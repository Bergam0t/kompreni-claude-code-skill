import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import { buildPrompt, parseArgs } from '../hooks/register'

const turn = (agentId?: string) => ({
  reason: 'answer' as const,
  answer: 'Done.',
  durationMs: 1000,
  isAborted: false,
  turnId: 't1',
  ...(agentId === undefined ? {} : { agentId }),
})

// An in-memory $.store, standing for the engine's.
const memoryStore = (on: On) => {
  const store = new Map<string, unknown>()
  on('store.get', (_, e) => ({ value: store.get(e.key) }))
  on('store.set', (_, e) => {
    store.set(e.key, e.value)
    return { value: undefined }
  })
  return store
}

const typed = (text: string) => ({ text, wait: false, origin: { kind: 'composer' as const } })

const command = (name: string) => ({ name, description: '', source: 'plugin' as const })

const BAND = {
  plugin: 'kompreni-offer',
  component: 'AbovePrompt',
  props: {
    hasSurvey: false,
    isCollapsed: false,
    isWorking: false,
    maxRows: 3,
    bodyColumns: 100,
    scroll: { offset: 0, bodyRows: 3 },
    view: {},
  },
} as const

test('builds the prompt from settings', async () => {
  expect(buildPrompt('kompreni:explain', 'auto', 'auto')).toBe('/kompreni:explain')
  expect(buildPrompt('kompreni-explain', 'deep', 'new-to-language')).toBe(
    '/kompreni-explain depth=deep level=new-to-language',
  )
  expect(buildPrompt('kompreni:explain', 'auto', 'fluent in R, new to Python')).toBe(
    '/kompreni:explain level="fluent in R, new to Python"',
  )
})

test('parses settings arguments', async () => {
  expect(parseArgs('off depth=brief level="knows R, new to Python" command=/kompreni-explain')).toEqual({
    enabled: 'off',
    depth: 'brief',
    level: 'knows R, new to Python',
    command: '/kompreni-explain',
  })
})

test('no band before any edit, a band after a turn that edited a file', async ($, on) => {
  memoryStore(on)
  on('tool.call', () => ({ result: {} }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('prompt.submit', (_, e) => ({ text: e.text }))

  const before = await $.ui.mount({ ...BAND, surface: 'vscode' })
  expect(await before.find({ key: 'explain' })).toBeUndefined()
  await before.unmount()

  await $.prompt.submit(typed('fix the bug'))
  await $.tool.call({ tool: 'Edit', file_path: '/repo/a.py', old_string: 'a', new_string: 'b' })
  await $.turn.complete(turn())

  for (const surface of ['terminal', 'vscode', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    expect((await ui.find({ type: 'Text', text: /Kompreni/ }))?.text).toBe('Kompreni: 1 file changed.')
    expect(await ui.find({ key: 'explain' })).toBeDefined()
    await ui.unmount()
  }
})

test('a turn with no edits, or a subagent turn, offers nothing', async ($, on) => {
  memoryStore(on)
  on('tool.call', () => ({ result: {} }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit(typed('what does this do?'))
  await $.tool.call({ tool: 'Read', file_path: '/repo/a.py' })
  await $.turn.complete(turn())
  await $.tool.call({ tool: 'Write', file_path: '/repo/b.py', content: 'x' })
  await $.turn.complete(turn('sub-1'))

  const ui = await $.ui.mount({ ...BAND, surface: 'vscode' })
  expect(await ui.find({ key: 'explain' })).toBeUndefined()
  await ui.unmount()
})

test('Explain fills the prompt with the installed command and the chosen settings', async ($, on) => {
  const filled: string[] = []
  memoryStore(on)
  on('tool.call', () => ({ result: {} }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('prompt.submit', (_, e) => ({ text: e.text }))
  on('command.list', () => ({
    value: [command('compact'), command('kompreni-explain')],
  }))
  on('prompt.read', () => ({ value: { text: '', cursor: 0 } }))
  on('prompt.fill', (_, e) => {
    filled.push(e.text)
    return { isFilled: true, text: e.text, cursor: e.text.length }
  })

  await $.prompt.submit(typed('add a feature'))
  await $.tool.call({ tool: 'Write', file_path: '/repo/new.py', content: 'x' })
  await $.turn.complete(turn())

  const ui = await $.ui.mount({ ...BAND, surface: 'vscode' })
  await ui.select({ key: 'level', value: 'new-to-language' })
  await ui.select({ key: 'depth', value: 'deep' })
  await ui.press({ key: 'explain' })
  expect(filled).toEqual(['/kompreni-explain depth=deep level=new-to-language'])
  expect(await ui.find({ key: 'explain' })).toBeUndefined()
  await ui.unmount()
})

test('a draft in the prompt box is never overwritten', async ($, on) => {
  const filled: string[] = []
  memoryStore(on)
  on('tool.call', () => ({ result: {} }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('prompt.submit', (_, e) => ({ text: e.text }))
  on('command.list', () => ({ value: [command('kompreni:explain')] }))
  on('prompt.read', () => ({ value: { text: 'half-typed question', cursor: 5 } }))
  on('prompt.fill', (_, e) => {
    filled.push(e.text)
    return { isFilled: true, text: e.text, cursor: 0 }
  })

  await $.prompt.submit(typed('change it'))
  await $.tool.call({ tool: 'Edit', file_path: '/repo/a.py', old_string: 'a', new_string: 'b' })
  await $.turn.complete(turn())

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  await ui.press({ key: 'explain' })
  expect(filled).toEqual([])
  expect(await ui.find({ key: 'explain' })).toBeDefined()
  await ui.unmount()
})
