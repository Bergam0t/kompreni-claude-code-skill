/** Marks this file as a module so the declaration below augments 'claude-code'. */
export type KompreniOfferFiles = string[]

declare module 'claude-code' {
  interface PluginState {
    'kompreni-offer': {
      /** Paths edited since the last Kompreni explanation in this session. */
      sinceExplain: KompreniOfferFiles
      /** Whether the offer row is showing. */
      isVisible: boolean
      /** Whether an explanation has run in this session (changes the row's wording). */
      hasExplained: boolean
    }
  }
}
