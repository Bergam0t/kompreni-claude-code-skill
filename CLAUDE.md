# Personality

- No sycophancy. Value honest, objective feedback over agreeableness — push back on weak ideas, biases, or poorly-thought-out requests, and explain better alternatives, while staying friendly.
- I'm always open to ideas on better ways to do things. Please don't hesitate to suggest a better way, or one that has long lasting impact over a tactical change.

# Git commit workflow

- Never run `git commit` unless explicitly asked that turn. Drafting/staging is fine anytime.
- Every commit needs a `Co-Authored-By: Claude <model-name> <noreply@anthropic.com>` trailer (via HEREDOC), one per contributing model.

# General workflow

- As you work, maintain a file called HANDOVER-working.md, which references the HANDOVER-original.md document to help track what has and hasn't yet been actioned.

# HISTORY.md

- Every user-facing change needs an entry — check as part of the task, don't wait to be asked.
- Add to the top section if it's unreleased; only start a new version header (bumping `version` in `.claude-plugin/plugin.json` to match) for the first change since the last release.
- Version headers are a single `#` with a bare number — `# 2.0.0`, not `## v2.0.0`.
- One top-level bullet per feature/fix, nested (4-space) sub-bullets for specifics.
- Docs/example-only changes to already-documented features usually don't need a new bullet — refine existing wording instead.
