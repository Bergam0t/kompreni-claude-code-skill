import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderChildren } from 'claude-code'

// Session state: files edited since the last explanation, and whether to show the row.
const sinceExplain = atom({ plugin: 'kompreni-offer', key: 'sinceExplain' } as const, [])
const isVisible = atom({ plugin: 'kompreni-offer', key: 'isVisible' } as const, false)
const hasExplained = atom({ plugin: 'kompreni-offer', key: 'hasExplained' } as const, false)
const allEdited = atom({ plugin: 'kompreni-offer', key: 'allEdited' } as const, [])
// Session only: "whole conversation" is a one-off choice, unlike depth and level.
const scope = atom({ plugin: 'kompreni-offer', key: 'scope' } as const, 'new')
// With show=always: hidden by Dismiss (or by filling the prompt) until the next turn finishes.
const isDismissed = atom({ plugin: 'kompreni-offer', key: 'isDismissed' } as const, false)

// Settings kept across sessions in $.store.
const LEVEL = 'level'
const DEPTH = 'depth'
const COMMAND = 'command'
const ENABLED = 'enabled'
const SHOW = 'show'

// When the row shows: always (the default), or only after a turn that edited files.
const SHOWS = ['always', 'changes']

const DEPTHS = ['auto', 'brief', 'standard', 'deep']
const LEVELS = ['auto', 'new-to-programming', 'new-to-language', 'intermediate', 'advanced']
// What 'auto' means, shown in the pickers. The value filled in stays 'auto' (i.e. no argument).
const AUTO_LABELS: Record<string, string> = {
  depth: 'auto (picked from the size of the change)',
  level: 'auto (intermediate, unless this chat, CLAUDE.md or memory says otherwise)',
}

/** Picker options: each value as its own label, except 'auto', which says what it means. */
export const optionsFor = (kind: 'depth' | 'level', values: string[]) =>
  values.map(value => (value === 'auto' ? { value, label: AUTO_LABELS[kind] } : { value }))

const SCOPES = [
  { value: 'new', label: 'since last explanation' },
  { value: 'all', label: 'whole conversation' },
]
// The explain skill's names: as a plugin, then as a plain skill (e.g. a junction).
const KNOWN_COMMANDS = ['kompreni:explain', 'kompreni-explain']

const EDIT_TOOLS = new Set(['Edit', 'Write', 'NotebookEdit'])
// History-mode runs explain a branch or commits, not this session's edits.
const HISTORY_ARGS = /\b(branch|since|commit)=/

const text = (value: unknown, fallback: string) =>
  typeof value === 'string' && value !== '' ? value : fallback

/** `key=value` and bare `on`/`off`; values may be "double quoted". */
export const parseArgs = (args: string) => {
  const out: Record<string, string> = {}
  for (const m of args.matchAll(/(\w+)=(?:"([^"]*)"|(\S+))|\b(on|off)\b/g)) {
    if (m[4] !== undefined) out.enabled = m[4]
    else if (m[1] !== undefined) out[m[1]] = m[2] ?? m[3] ?? ''
  }
  return out
}

/** The prompt to fill: the command plus any non-default settings. */
export const buildPrompt = (command: string, depth: string, level: string, scope = 'new') => {
  const parts = [`/${command}`]
  if (scope === 'all') parts.push('scope=all')
  if (depth !== 'auto') parts.push(`depth=${depth}`)
  if (level !== 'auto') parts.push(/\s/.test(level) ? `level="${level}"` : `level=${level}`)
  return parts.join(' ')
}

/** The explain command to fill: the one set with command=, else the first installed. */
async function resolveCommand($: EngineInterface): Promise<string | undefined> {
  const chosen = await $.store.get(COMMAND)
  if (typeof chosen === 'string' && chosen !== '') return chosen
  const names = new Set((await $.command.list()).map(c => c.name))
  return KNOWN_COMMANDS.find(name => names.has(name))
}

/** Whether a run of `name` with `args` is a session-mode Kompreni explanation. */
async function isSessionExplain($: EngineInterface, name: string, args: string): Promise<boolean> {
  const chosen = await $.store.get(COMMAND)
  const isExplain = KNOWN_COMMANDS.includes(name) || name === chosen
  return isExplain && !HISTORY_ARGS.test(args)
}

/** An explanation ran: what it covered no longer counts as unexplained. */
async function markExplained($: EngineInterface): Promise<void> {
  await update($, sinceExplain, () => [])
  await update($, isVisible, () => false)
  await update($, hasExplained, () => true)
}

export const register: Register = on => {
  // Edits in the current turn, so an offer appears only after a turn that changed something.
  // A reload resets it, which at worst skips one offer.
  let turnEdits = 0

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'kompreni-offer',
      description: 'Kompreni offer settings: on, off, show=, depth=, level=, command=',
      argumentHint:
        '[on|off] [show=always|changes] [depth=auto|brief|standard|deep] [level=<preset or "free text">] [command=<skill command>]',
    })
    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    turnEdits = 0
    await update($, isVisible, () => false)
    if (e.command !== undefined && (await isSessionExplain($, e.command.name, e.command.args))) {
      await markExplained($)
    }
    return next(e)
  }).catch(($, e, next) => next(e)) // never block a prompt over a failed offer

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (ran.deny !== undefined || ran.isError === true) return ran
    const input = e as unknown as { file_path?: string; notebook_path?: string; skill?: string; args?: string }
    if (EDIT_TOOLS.has(e.tool)) {
      const path = input.file_path ?? input.notebook_path
      if (path !== undefined) {
        turnEdits += 1
        const add = (files: string[]) => (files.includes(path) ? files : [...files, path])
        await update($, sinceExplain, add)
        await update($, allEdited, add)
      }
    } else if (e.tool === 'Skill' && input.skill !== undefined) {
      if (await isSessionExplain($, input.skill, input.args ?? '')) await markExplained($)
    }
    return ran
  }).catch(($, e, next) => next(e)) // never block or change a tool call

  on('turn.complete', async ($, e, next) => {
    const done = await next(e)
    const isMainAnswer = e.agentId === undefined && e.reason === 'answer'
    const isEnabled = text(await $.store.get(ENABLED), 'on') === 'on'
    if (isMainAnswer && isEnabled) {
      await update($, isDismissed, () => false)
      if (turnEdits > 0) await update($, isVisible, () => true)
    }
    return done
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'kompreni-offer' }, async ($, e) => {
    const args = parseArgs(e.args)
    const errors: string[] = []
    if (args.enabled !== undefined) await $.store.set(ENABLED, args.enabled)
    if (args.show !== undefined) {
      if (SHOWS.includes(args.show)) await $.store.set(SHOW, args.show)
      else errors.push(`show must be one of ${SHOWS.join(', ')}`)
    }
    if (args.depth !== undefined) {
      if (DEPTHS.includes(args.depth)) await $.store.set(DEPTH, args.depth)
      else errors.push(`depth must be one of ${DEPTHS.join(', ')}`)
    }
    if (args.level !== undefined) await $.store.set(LEVEL, args.level === '' ? 'auto' : args.level)
    if (args.command !== undefined) await $.store.set(COMMAND, args.command.replace(/^\//, ''))

    const command = (await resolveCommand($)) ?? 'not found (set command=)'
    const pending = (await read($, sinceExplain)).length
    const lines = [
      `Kompreni offer: ${text(await $.store.get(ENABLED), 'on')}`,
      `show: ${text(await $.store.get(SHOW), 'always')}`,
      `depth: ${text(await $.store.get(DEPTH), 'auto')}`,
      `level: ${text(await $.store.get(LEVEL), 'auto')}`,
      `command: /${command}`,
      `files changed since the last explanation: ${pending}`,
      ...errors,
    ]
    return { text: lines.join('\n') }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || text(await $.store.get(ENABLED), 'on') !== 'on') return next(e)
    const pending = await read($, sinceExplain)
    const isAlways = text(await $.store.get(SHOW), 'always') === 'always'
    const shows = isAlways
      ? !e.props.isWorking && !(await read($, isDismissed))
      : (await read($, isVisible)) && pending.length > 0
    if (!shows) return next(e)

    const depth = text(await $.store.get(DEPTH), 'auto')
    const level = text(await $.store.get(LEVEL), 'auto')
    const levels = LEVELS.includes(level) ? LEVELS : [...LEVELS, level]
    const explained = await read($, hasExplained)
    const chosenScope = explained ? await read($, scope) : 'new'
    const isAll = chosenScope === 'all'
    const files = isAll ? await read($, allEdited) : pending
    const since = explained && !isAll ? 'since the last explanation' : 'in this conversation'
    const { Box, Button, Select, Text } = $.ui.resolve(e)
    const n = files.length
    // Edits made only through shell commands aren't seen here, but the skill still finds them in git.
    const summary = n === 0 ? `no file edits seen ${since}` : `${n} file${n === 1 ? '' : 's'} changed ${since}`
    const hide = async () => {
      await update($, isVisible, () => false)
      await update($, isDismissed, () => true)
    }

    const explain = async () => {
      const command = await resolveCommand($)
      if (command === undefined) {
        $.ui.toast('Kompreni: no explain skill found here. Set one with /kompreni-offer command=<name>.')
        return
      }
      const box = await $.prompt.read()
      if (box.text.trim() !== '') {
        $.ui.toast('Kompreni: the prompt box has a draft, so nothing was filled in.')
        return
      }
      // Read the settings now, not the values captured when the band was drawn.
      const chosenDepth = text(await $.store.get(DEPTH), 'auto')
      const chosenLevel = text(await $.store.get(LEVEL), 'auto')
      const nowScope = (await read($, hasExplained)) ? await read($, scope) : 'new'
      const filled = await $.prompt.fill({ text: buildPrompt(command, chosenDepth, chosenLevel, nowScope) })
      // The count resets when the explanation actually runs, not here.
      if (filled.isFilled) await hide()
    }

    const buttons = (
      <Box flexDirection="row" gap={1}>
        <Button key="explain" label="Explain" onPress={() => void explain()} />
        <Button key="dismiss" label="Dismiss" onPress={() => void hide()} />
      </Box>
    )

    // Nothing new to explain: one line, using the remembered depth and level. After an explanation,
    // "Whole conversation" switches to the full row with that scope chosen.
    if (n === 0) {
      const canWiden = explained && (await read($, allEdited)).length > 0
      return (
        <Box flexDirection="row" alignItems="center" gap={1}>
          <Text dimColor>Kompreni: {summary}.</Text>
          {buttons}
          {canWiden && (
            <Button key="scope-all" label="Whole conversation" onPress={() => void update($, scope, () => 'all')} />
          )}
        </Box>
      )
    }

    // One picker per line: a fixed-width label on the left, the picker stretching to fill the rest.
    const row = (label: string, picker: RenderChildren) => (
      <Box flexDirection="row" alignItems="center" gap={1}>
        <Box width={6} flexShrink={0}>
          <Text>{label}</Text>
        </Box>
        <Box flexGrow={1}>{picker}</Box>
      </Box>
    )

    return (
      <Box flexDirection="column" rowGap={0}>
        <Text dimColor>Kompreni: {summary}.</Text>
        {explained &&
          row(
            'Scope',
            <Select
              key="scope"
              value={chosenScope}
              options={SCOPES}
              onSelect={value => void update($, scope, () => (value === 'all' ? 'all' : 'new'))}
            />,
          )}
        {row(
          'Depth',
          <Select
            key="depth"
            value={depth}
            options={optionsFor('depth', DEPTHS)}
            onSelect={value => void $.store.set(DEPTH, value)}
          />,
        )}
        {row(
          'Level',
          <Select
            key="level"
            value={level}
            options={optionsFor('level', levels)}
            onSelect={value => void $.store.set(LEVEL, value)}
          />,
        )}
        {buttons}
      </Box>
    )
  })
}
