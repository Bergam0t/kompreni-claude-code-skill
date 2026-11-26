# Code tour (`code=all`)

A code tour shows **all the substantive changed code**, with a little context, and explains it line by line with Quarto code annotations. It's for a reader who wants to understand the change from the code itself, not only from a summary. Everything in `structure.md` and `formats.md` still applies unless this file says otherwise.

`code=all` is `qmd` only: GitHub-flavoured Markdown has no code annotations. The Quarto behaviour below was tested by rendering with Quarto 1.11.

## Shape

Keep these sections from `structure.md`:
- Overview
- The problem
- **Before**, kept short: the old behaviour in prose, plus the running example
- Concepts used here
- How the pieces fit together
- Decisions and alternatives
- Verification
- Limitations
- Check your understanding
- Worth remembering
- Useful elsewhere: link each item to its tour stop (`@sec-tour-…`). An annotation on the lines where a gotcha bites can point to it in a few words ("a Git for Windows quirk: see @sec-useful-elsewhere")
- Scope and provenance

Replace "What changed" and "How it works now" with a **Code tour** section (`## Code tour {#sec-tour}`).

Front matter: as in `front-matter.md` (including the `grid`, the light/dark theme and the mermaid `<style>`), but with `code-annotations: below` instead of `hover`, and `kompreni.code: all`. With `below`, the explanations sit under each block, and clicking an item highlights its lines. That suits a tour, where the explanations are the point.

```yaml illustrative
format:
  html:
    embed-resources: true
    toc: true
    grid:
      sidebar-width: 0px
      body-width: 1050px
    code-annotations: below
    theme:
      light: flatly
      dark: darkly
    respect-user-color-scheme: true
    include-in-header:
      text: |
        ...the <style> block from front-matter.md, unchanged...
```

## The tour

- **One stop per purpose group**, as a `###` heading with an id: `### Taking the snapshot {#sec-tour-snapshot}`. Name the stop after what the code does, not the file.
- **Stops go in reading order**: follow the call or data flow, starting at the entry point (the command, the handler, the public function), not file order. Within a stop, the blocks from one file go in file order.
- **Each stop opens with one or two sentences**: what this part does, and how it connects to the previous stop. Then come the blocks, each followed straight away by its annotation list.
- **Carry the running example through the annotations** ("with the example's two edits, `files` is now `['a.py']`"), so the reader traces one concrete case through the new code.
- **Tests** come last, as `### Tests {#sec-tour-tests}`. See below.
- **Housekeeping** (renames, formatting, lockfiles, generated files, version bumps) gets one closing line in the Code tour, not blocks.

## What goes in a block

- **Every changed or added line of substantive code**, as it is at the tip.
- **Context**: enough unchanged lines to read the change. That means the enclosing signature when the function is short, otherwise up to about 3 lines either side. Don't pad with unchanged code nobody needs.
- **Split at natural boundaries** (a function, a class, a logical step) so that no block is much over about 40 lines.
- **No overlap** between blocks from the same file.
- **Real line numbers**: add `.numberLines startFrom="<first line>"`, so the numbers in the margin match the file. `startFrom` must equal the first line in the caption; the checker enforces this.

  ````markdown
  ```{.python .numberLines startFrom="51" filename="src/snapshot.py:51-57"}
  ````

  Without `startFrom`, Quarto numbers from 1.
- **Removed code that matters**: use the Before/After tabset from `formats.md`. Before is the old lines, verbatim at `@<base>`, with one or two annotations on what they did. After is the new lines, fully annotated.
- **Pure deletions** (code removed and not replaced): a short `@<base>` block with one annotation saying why it went, or that the reason isn't recorded.
- **Doc and config changes** that are the substance of the change (for example a skill's instructions, a schema, a CI workflow) are toured like code: in a `.markdown`, `.yaml` or similar block. Other docs (README, changelog) are housekeeping.

## Annotations

The syntax is in `formats.md`, "Code annotations". Rules for a tour:

- **Every changed line of code carries a marker.** Consecutive lines that do one thing share a number: repeat the same `# <n>` on each of them, which highlights them together. Unchanged context lines carry a marker only when the explanation needs them. Changed comments and docstrings that speak for themselves can go unmarked, or share one marker on their first line. Blank lines never carry one.
- **Marker syntax by language**: `# <n>` (Python, R, shell, YAML, TOML), `// <n>` (JS, TS, JSON, C-family, Rust, Go), `-- <n>` (SQL, Lua), `<!-- <n> -->` (Markdown, HTML), `/* <n> */` (CSS). All of these were tested.
- **Numbering restarts at 1 in each block.** So refer to other stops by section (`@sec-tour-snapshot`), never by annotation number.
- **Each item says what the lines do and why.** Give the reason with its evidence label where it's a decision: *(code)*, *(stated)*, *(commit `sha`)*, *(PR #n)*, *(observed)*, *(inferred)*. Don't restate the code in words ("assigns x to y"); say what it achieves, what it guards against, and what would break without it.
- **One paragraph per item, about one to four sentences.** Quarto silently drops a second paragraph (tested), and the checker reports it as an error. Inline code, emphasis and links are fine.
- **Start each item with a word**, not something Pandoc reads as a block: a bullet (`- `), a number or letter with a dot (`2. `, `a. `, a bare `A.`), a heading `#` or a quote `>`. Quarto's render then **fails outright** (tested: "Inline expected, got Blocks"). Starting with inline code is fine. The checker flags these. For more detail, add a collapsed callout after the list:
  `::: {.callout-note collapse="true" title="More on annotation 2: why a temporary index"}`.
- **The list comes straight after the block.** Blank lines between are fine. Any prose between unlinks every annotation silently (tested). Put the stop's closing remark after the list.
- **Detail by level** (`levels.md`):

  | Level | Annotations |
  |---|---|
  | `new-to-programming` | Roughly one per line or two. Plain readings, every construct named the first time |
  | `new-to-language` | Per logical step. Idioms and gotchas named where they occur |
  | `intermediate` | Per logical step. Only non-obvious behaviour explained |
  | `advanced` | Per decision. Invariants, risks and interactions only. Leave simple lines unmarked unless they changed |

  Changed lines always get a marker, whatever the level. At `advanced`, several changed lines can share one number.
- **Length**: as long as the code needs, but keep the annotation text well under about three times the number of lines shown. If one item keeps growing, the idea belongs in a prose section ("How the pieces fit together", "Decisions") that the item points to.

## Tests

One collapsed callout per test file, inside `### Tests`:

````markdown
::: {.callout-note collapse="true" title="Tests: tests/test_snapshot.py (7 new tests)"}
```{.python .numberLines startFrom="42" filename="tests/test_snapshot.py:42-53"}
...
```
1. One short item per test: the behaviour it pins down, and which stop it covers.
:::
````

Annotate each test briefly: what it sets up, what it asserts, and why that matters. Keep shared fixtures and helpers to one annotation each.

## Large changes

Above about 600 changed lines of source (excluding tests, lockfiles and generated files):
- say so at the top of the Code tour;
- tour the most behaviour-relevant groups in full;
- list the rest under **Not toured** in Scope and provenance, by file and range;
- suggest `focus=<path or topic>` for a closer tour.

Don't stop to ask: the user asked for all the code.

## Checking coverage

Run the checker with `--coverage` (see SKILL.md step 7). It lists every changed range that no verbatim block shows. Every note must be one of these:
- shown, by adding or widening a block;
- listed under **Not toured** in Scope and provenance, with a reason (housekeeping, generated, or over the size limit). Whole files can be listed by name.

"Removed lines not shown" notes are fine for deletions whose disappearance is explained in prose or in an annotation. Otherwise, add a Before block.
