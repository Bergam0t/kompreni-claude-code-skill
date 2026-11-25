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
    code-annotations: hover
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
| `format` | `qmd` only | Exactly as above. `embed-resources` makes the HTML one self-contained file |
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
