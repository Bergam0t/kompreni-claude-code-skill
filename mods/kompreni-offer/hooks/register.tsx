import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Offer } from '../types'

// The offer for the turn that just ended; null when there is nothing to offer.
const pending = atom({ plugin: 'kompreni-offer', key: 'pending' } as const, null)

// Settings kept across sessions in $.store.
const LEVEL = 'level'
const DEPTH = 'depth'
const COMMAND = 'command'
const ENABLED = 'enabled'

const DEPTHS = ['auto', 'brief', 'standard', 'deep']
const LEVELS = ['auto', 'new-to-programming', 'new-to-language', 'intermediate', 'advanced']
// The explain skill's names: as a plugin, then as a plain skill (e.g. a junction).
const KNOWN_COMMANDS = ['kompreni:explain', 'kompreni-explain']

const EDIT_TOOLS = new Set(['Edit', 'Write', 'NotebookEdit'])

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

/** The prompt to fill: the command plus any non-auto settings. */
export const buildPrompt = (command: string, depth: string, level: string) => {
  const parts = [`/${command}`]
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

export const register: Register = on => {
  // Module variable: the files edited since the last prompt. A reload resets it,
  // which at worst skips one offer.
  let edited = new Set<string>()

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'kompreni-offer',
      description: 'Kompreni offer settings: on, off, depth=, level=, command=',
      argumentHint: '[on|off] [depth=auto|brief|standard|deep] [level=<preset or "free text">] [command=<skill command>]',
    })
    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    edited = new Set()
    await update($, pending, () => null)
    return next(e)
  }).catch(($, e, next) => next(e)) // never block a prompt over a failed offer

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (EDIT_TOOLS.has(e.tool) && ran.deny === undefined && ran.isError !== true) {
      const input = e as unknown as { file_path?: string; notebook_path?: string }
      const path = input.file_path ?? input.notebook_path
      if (path !== undefined) edited.add(path)
    }
    return ran
  }).catch(($, e, next) => next(e)) // never block or change a tool call

  on('turn.complete', async ($, e, next) => {
    const done = await next(e)
    const isMainAnswer = e.agentId === undefined && e.reason === 'answer'
    const isEnabled = text(await $.store.get(ENABLED), 'on') === 'on'
    if (isMainAnswer && isEnabled && edited.size > 0) {
      const offer: Offer = { files: [...edited] }
      await update($, pending, () => offer)
    }
    return done
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'kompreni-offer' }, async ($, e) => {
    const args = parseArgs(e.args)
    const errors: string[] = []
    if (args.enabled !== undefined) await $.store.set(ENABLED, args.enabled)
    if (args.depth !== undefined) {
      if (DEPTHS.includes(args.depth)) await $.store.set(DEPTH, args.depth)
      else errors.push(`depth must be one of ${DEPTHS.join(', ')}`)
    }
    if (args.level !== undefined) await $.store.set(LEVEL, args.level === '' ? 'auto' : args.level)
    if (args.command !== undefined) await $.store.set(COMMAND, args.command.replace(/^\//, ''))

    const command = (await resolveCommand($)) ?? 'not found (set command=)'
    const lines = [
      `Kompreni offer: ${text(await $.store.get(ENABLED), 'on')}`,
      `depth: ${text(await $.store.get(DEPTH), 'auto')}`,
      `level: ${text(await $.store.get(LEVEL), 'auto')}`,
      `command: /${command}`,
      ...errors,
    ]
    return { text: lines.join('\n') }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const offer = await read($, pending)
    if (e.props.hasSurvey || offer === null) return next(e)

    const depth = text(await $.store.get(DEPTH), 'auto')
    const level = text(await $.store.get(LEVEL), 'auto')
    const levels = LEVELS.includes(level) ? LEVELS : [...LEVELS, level]
    const { Box, Button, Select, Text } = $.ui.resolve(e)
    const n = offer.files.length

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
      const filled = await $.prompt.fill({ text: buildPrompt(command, chosenDepth, chosenLevel) })
      if (filled.isFilled) await update($, pending, () => null)
    }

    return (
      <Box flexDirection="row" gap={1}>
        <Text dimColor>
          Kompreni: {n} file{n === 1 ? '' : 's'} changed.
        </Text>
        <Select
          key="depth"
          label="Depth"
          value={depth}
          options={DEPTHS.map(value => ({ value }))}
          onSelect={value => void $.store.set(DEPTH, value)}
        />
        <Select
          key="level"
          label="Level"
          value={level}
          options={levels.map(value => ({ value }))}
          onSelect={value => void $.store.set(LEVEL, value)}
        />
        <Button key="explain" label="Explain" onPress={() => void explain()} />
        <Button key="dismiss" label="Dismiss" onPress={() => void update($, pending, () => null)} />
      </Box>
    )
  })
}
