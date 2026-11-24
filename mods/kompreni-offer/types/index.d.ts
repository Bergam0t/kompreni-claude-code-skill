/** The offer shown after a turn that edited files. */
export type Offer = {
  /** Paths edited during the turn, by the main loop or its subagents. */
  files: string[]
}

declare module 'claude-code' {
  interface PluginState {
    'kompreni-offer': { pending: Offer | null }
  }
}
