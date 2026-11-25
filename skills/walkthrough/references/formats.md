# Formats

Two output formats share one structure. `qmd` is richer (tabsets, code annotations, collapsible callouts, numbered figures) and renders to a single HTML file. `md` is GitHub-flavoured Markdown that reads well on GitHub and in editors. The `qmd` syntax below was rendered with Quarto 1.11 with no warnings. A code tour (`code=all`, see `code-tour.md`) is `qmd` only, because it depends on code annotations.

## Code blocks

Every code block is exactly one of these. `check_refs.py` enforces it.

| Kind | `qmd` | `md` |
|---|---|---|
| Verbatim, current code | ```` ```{.python filename="src/api.py:40-46"} ```` | ```` ```python src/api.py:40-46 ```` |
| Verbatim, before the change | ```` ```{.python filename="src/api.py:40-46@abc1234"} ```` | ```` ```python src/api.py:40-46@abc1234 ```` |
| Illustrative (simplified, example usage, shell, output) | ```` ```{.python .illustrative filename="Simplified from src/api.py"} ```` | ```` ```python illustrative ```` with a line above saying what it is |
| Flow sketch | ```` ```{.text} ```` | ```` ```text ```` |
| Diagram | ```` ```{mermaid} ```` | ```` ```mermaid ```` |

- **Verbatim** means contiguous lines copied exactly: no edits, no `...`, no added comments. Only removing a common indent and adding annotation markers (`qmd`) are allowed. At most about 15 lines, or what `levels.md` sets.
- **"Before" code** uses `@<base>`: the base SHA in history mode, `HEAD` for uncommitted session changes, or the commit before the session's first commit.
- **In `qmd`, never write ```` ```{python} ````** (no dot): Quarto would execute it. Always use the dotted class form.
- In `qmd`, give every illustrative block a visible `filename="..."` caption saying what it is: `Simplified from <path>`, `Example usage`, `Example output`, `Shell`.
- When in doubt, mark it illustrative.

## References and links

- In prose, write references as inline code: `` `src/api.py:42` `` or `` `src/api.py:40-46` ``. They are checked by `check_refs.py`, and they stay meaningful wherever the document is moved.
- **Permalinks**: add a link only when all three hold: the tip is a commit (not `dirty`), `git remote get-url origin` is a GitHub URL, and the commit is on the remote (`git branch -r --contains <tip>` prints something). Then link with the full SHA: `[src/api.py:40-46](https://github.com/<owner>/<repo>/blob/<full sha>/src/api.py#L40-L46)`. The checker verifies the path and lines at that SHA.
- **No relative links** to source files (`../../src/api.py`). They break when the document is moved or rendered elsewhere.
- Name commits by short SHA in prose. A PR is `#<n>`, linked if you have its URL.

## Callouts

| Purpose | `qmd` | `md` |
|---|---|---|
| At a glance | `::: {.callout-note title="At a glance"}` ... `:::` | `> [!NOTE]` then `> **At a glance**` and `> ` lines |
| Gotcha, limitation | `::: {.callout-warning title="..."}` | `> [!WARNING]` |
| Analogy, tip | `::: {.callout-tip title="..."}` | `> [!TIP]` |
| Optional depth | `::: {.callout-note collapse="true" title="Deep dive: ..."}` | `<details><summary>Deep dive: ...</summary>` (blank line, content, blank line) `</details>` |

In `md`, never put a code block inside a `> [!NOTE]` alert; put it after the alert. Code blocks inside `<details>` are fine if blank lines surround them.

### The drift note (when `dirty: true`)

Put this at the top of the Overview, inside the At a glance callout or straight after it:

- `qmd`: `::: {.callout-warning title="References point at uncommitted code"}`
- `md`: `> [!WARNING]`

Text: "This walkthrough was written on <date> before the changes were committed. Line references point at the working tree as it was then (on top of commit `<head short sha>`) and may have drifted."

## Before and after

`qmd`: a tabset. Use `group="before-after"` and the tab names exactly `Before` and `After`, so all such tabsets in the document switch together. The tab headings are one level below the section they're in.

````markdown
::: {.panel-tabset group="before-after"}
### Before
```{.python filename="src/api.py:40-44@abc1234"}
...exact old lines...
```

### After
```{.python filename="src/api.py:40-46"}
...exact new lines...
```
:::
````

`md`: two consecutive blocks, each preceded by a bold label: `**Before** (at `abc1234`)` and `**After**`.

## Code annotations (`qmd` only)

Append a marker as a comment, in the block's language, at the end of a line, and follow the block immediately with a numbered list. The front matter sets `code-annotations: hover` (a code tour uses `below`, see `code-tour.md`). Markers are allowed on verbatim blocks: the checker ignores them when comparing.

Tested with Quarto 1.11:
- Lines that share an explanation repeat the same marker.
- Blank lines between the block and its list are fine, but any prose between them silently unlinks the annotations.
- Each item must be a single paragraph: a second paragraph is silently dropped.
- An item must not start with a list, heading or quote marker (`- `, `a. `, `#`, `>`); that makes the whole render fail.
- Annotations work inside tabsets and collapsed callouts.

The checker reports each of these mistakes as an error.

````markdown
```{.python filename="src/api.py:40-42"}
def fetch(url, retries=3):        # <1>
    for attempt in range(retries):  # <2>
```
1. The default of three comes from the config change in @sec-what-changed.
2. Each attempt...
````

Comment syntax: `#` (Python, R, shell, YAML), `//` (JS, TS, C-family, Rust, Go), `--` (SQL, Lua, Haskell), `;` (Lisp, assembly), `<!-- <n> -->` (Markdown, HTML), `/* <n> */` (CSS). In `md`, follow the block with a short numbered list that refers to the lines by content instead.

## Diagrams

- `qmd`: a `{mermaid}` cell with a label and caption, referred to as `@fig-<name>` in the prose:
  ````markdown
  ```{mermaid}
  %%| label: fig-upload-flow
  %%| fig-cap: "What happens to an upload now"
  flowchart LR
    A[Client] --> B[Queue]
  ```
  ````
- `md`: a plain ```` ```mermaid ```` block (GitHub renders it) with an italic caption line after it.
- Keep labels short. Alias participants with spaces in sequence diagrams (`participant Q as Upload queue`). Avoid unescaped double quotes and semicolons in labels.

## Questions and answers

`qmd`: the question in bold with a number, then its answer in a collapsed callout straight after it.

````markdown
**1. What does `fetch()` do now when the server returns 503 twice, then 200?**

::: {.callout-note collapse="true" title="Answer"}
It retries twice and returns the third response. See @sec-how-it-works-now.
:::
````

`md`: the same question, then:

````markdown
<details><summary>Answer</summary>

It retries twice and returns the third response. See [How it works now](#how-it-works-now).

</details>
````

## Cross-references within the document

- `qmd`: give each `##` section an id (`## How it works now {#sec-how-it-works-now}`) and refer to it as `@sec-how-it-works-now`. Figures are `@fig-...`.
- `md`: link to GitHub's heading anchors: lowercase, spaces become hyphens, punctuation removed (`[How it works now](#how-it-works-now)`).

## Rendering inside an existing Quarto project

If the repo (or a parent folder) has a `_quarto.yml`, a `.qmd` in `kompreni/walkthroughs/` belongs to that project:
- `quarto render <file>` writes the HTML into the project's output folder (e.g. `_site/kompreni/walkthroughs/`), not next to the file;
- a website project's next full render includes the walkthroughs as pages.

That's why `render=auto` skips rendering there. Mention the second point in the reply the first time you write into such a repo, so the user can exclude the folder in `_quarto.yml` (`project: render:`) if they don't want walkthroughs on their site.
