# Front matter

Every walkthrough starts with a YAML front matter block. The `kompreni:` part is the seed of Kompreni's persistent knowledge format (handover §9 Phase 3): later tools and agents will search walkthroughs by these fields, so fill them accurately and keep the shape stable. Quarto passes the `kompreni:` key through as metadata without a warning; GitHub shows the block as a table at the top of an `.md` file.

## qmd

```yaml illustrative
---
title: "Retry failed uploads"
date: 2026-11-24
format:
  html:
    embed-resources: true
    toc: true
    grid:
      sidebar-width: 0px
      body-width: 1050px
    code-annotations: hover
    theme:
      light: flatly
      dark: darkly
    respect-user-color-scheme: true
    include-in-header:
      text: |
        <style>
        body { --mermaid-fg-color--lightest: rgba(128,128,128,.08); --mermaid-fg-color--lighter: #adb5bd; }
        body.quarto-dark { --mermaid-label-fg-color: #fff; --mermaid-edge-color: #adb5bd; }
        body.quarto-dark :is(.edgeLabel, .edgeLabel p, .labelBkg) { background-color: var(--mermaid-label-bg-color) !important; }
        </style>
        <style>
        div.sourceCode code > span:is(.kompreni-added, .kompreni-removed, .kompreni-changed) { display: inline-block; min-width: 100%; }
        div.sourceCode code > span.kompreni-added { background: rgba(46,160,67,.18); }
        div.sourceCode code > span.kompreni-removed { background: rgba(248,81,73,.18); }
        div.sourceCode code > span.kompreni-changed { background: rgba(214,162,28,.24); }
        div.sourceCode code > span:is(.kompreni-added, .kompreni-removed, .kompreni-changed)::after { position: absolute; left: 3em; top: 0; width: 1em; text-align: center; font-weight: bold; }
        div.sourceCode code > span.kompreni-added::after { content: "+"; color: #2ea043; }
        div.sourceCode code > span.kompreni-removed::after { content: "−"; color: #e5534b; }
        div.sourceCode code > span.kompreni-changed::after { content: "~"; color: #c69026; }
        </style>
        <script>
        document.addEventListener("DOMContentLoaded", () => {
          for (const div of document.querySelectorAll("div.sourceCode:is([data-added], [data-removed], [data-changed])")) {
            const kinds = {};
            for (const kind of ["added", "removed", "changed"]) {
              for (const part of (div.dataset[kind] || "").split(",").filter(p => p.trim())) {
                const [a, b] = part.split("-").map(Number);
                for (let n = a; n <= (b || a); n++) kinds[n] = kind;
              }
            }
            for (const span of div.querySelectorAll("code > span[id]")) {
              const kind = kinds[Number(span.id.split("-").pop())];
              if (kind) span.classList.add("kompreni-" + kind);
            }
          }
        });
        </script>
kompreni:
  schema: 1
  kind: walkthrough
  summary: "Uploads that fail with a 5xx are now retried up to three times with backoff, instead of failing the whole batch."
  source: session
  base: 3f2a91c4e0b1...
  tip: 51d0a3b7c9de...
  dirty: true
  commits: []
  files: [src/upload.py, src/config.py, tests/test_upload.py]
  level: intermediate
  depth: deep
  code: key
  tests: "pytest tests/test_upload.py: 14 passed"
  lessons:
    - {kind: pattern, topic: "retries", summary: "Classify errors as retryable before retrying: retrying a 4xx only delays the failure."}
  snapshot: {tree: 8c1e..., head: 51d0a3b7c9de...}
---
```

## md

The same, without the `format:` key.

## Fields

| Field | Required | Value |
|---|---|---|
| `title` | yes | Names the purpose, not the files. Double-quoted; escape `"` inside as `\"` |
| `date` | yes | Today, `YYYY-MM-DD` |
| `format` | `qmd` only | Exactly as above. `embed-resources` makes the HTML one self-contained file. `grid` gives the body the room Quarto keeps on the left for a sidebar, which a standalone page never has, so code and diagrams get wider; the TOC on the right is unchanged. `theme` with `light` and `dark` adds Quarto's light/dark toggle (top right), and `respect-user-color-scheme` starts in the reader's system setting until they use the toggle. The first `<style>` fixes mermaid colours that Quarto gets wrong: in dark mode, labels in the theme's dark blue and near-invisible arrows; in both modes, near-black subgraph boxes. The second `<style>` and the `<script>` tint the lines listed in a code block's `changed=`, `added=` and `removed=` (yellow, green and red, with a `~`, `+` or `−` beside the line number; see `formats.md`, "Before and after"): the script reads the real line number from each line's id, which `.numberLines startFrom` sets, and the translucent tints read in both light and dark mode. Copy all of it unchanged. **Inside an existing Quarto project** (see `formats.md`), leave out `grid`, `theme`, `respect-user-color-scheme` and the mermaid `<style>`, so the site's own layout and theme apply; keep `include-in-header` with only the line-mark `<style>` and `<script>` |
| `kompreni.schema` | yes | `1` |
| `kompreni.kind` | yes | `walkthrough` |
| `kompreni.summary` | yes | One sentence: what changed and why, in behaviour terms. Written for someone scanning a list of walkthroughs |
| `kompreni.source` | yes | `session`, `branch`, `commit` or `since` |
| `kompreni.base` | yes | Full SHA the changes are measured from: the merge-base, `<commit>^`, the `since` ref resolved, or in session mode the commit before the session's first commit (or, if it made none, `HEAD` as it was before any commit made in step 4 of SKILL.md) |
| `kompreni.tip` | yes | Full SHA of the end of the range. In session mode, `HEAD` at the time of writing |
| `kompreni.dirty` | yes | `true` if the walkthrough covers uncommitted changes, so references point at the working tree. Otherwise `false` |
| `kompreni.branch` | if any | The branch name in `branch=` mode, or the current branch in session mode |
| `kompreni.pr` | if found | The PR number |
| `kompreni.commits` | yes | Full SHAs in the range, oldest first, excluding merges. `[]` if none |
| `kompreni.files` | yes | Repo-relative paths of the files whose changes are explained, in a flow list. Leave out lockfiles and generated files |
| `kompreni.level` | yes | The level used: a preset name, or the free text |
| `kompreni.depth` | yes | `standard` or `deep` |
| `kompreni.code` | yes | `key` (key excerpts) or `all` (a code tour; see `code-tour.md`, which also switches `code-annotations` to `below`) |
| `kompreni.tests` | yes | What was run and the result, in one line, or `"none run"`. In history mode, the CI summary or `"no results available"` |
| `kompreni.lessons` | if any | One entry per item in "Useful elsewhere", in the same order: `kind` (`gotcha`, `pattern` or `technique`), `topic` (the library, tool or area, such as `"pandas"` or `"git on Windows"`, plus a version when the item depends on it), and `summary` (one sentence that makes sense alone). Leave the key out when the section is left out. These let later tools find a gotcha across all walkthroughs |
| `kompreni.snapshot` | session mode | `{tree: <sha>, head: <sha>}` from `snapshot.py` |
| `kompreni.focus` | if given | The `focus=` value |

Get every SHA from git (`git rev-parse <ref>`), never from memory. Don't add fields that aren't listed here; propose them as a change to this file instead.
