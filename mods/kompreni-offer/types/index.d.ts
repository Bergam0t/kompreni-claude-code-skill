/** Marks this file as a module so the declaration below augments 'claude-code'. */
export type KompreniOfferFiles = string[]

declare module 'claude-code' {
  interface PluginState {
    'kompreni-offer': {
      /** Paths edited since the last Kompreni explanation in this session. */
      sinceExplain: KompreniOfferFiles
      /** Paths edited at any point in this session. */
      allEdited: KompreniOfferFiles
      /** What Explain covers: since the last explanation, or the whole conversation. */
      scope: 'new' | 'all'
      /** Whether the offer row is showing. */
      isVisible: boolean
      /** With show=always: whether Dismiss (or filling the prompt) has hidden the row until the next turn ends. */
      isDismissed: boolean
      /** Whether an explanation has run in this session (changes the row's wording). */
      hasExplained: boolean
    }
  }
}
