# Scenario 24: Markdown walkthrough without Quarto

**Setup:** As scenario 23, but with `quarto` not on PATH (or pass `format=md`).

**Task:** Run `/kompreni:walkthrough`.

**Expect:** Writes a `.md` file in GitHub-flavoured Markdown: `> [!NOTE]` alerts with no code inside them, ```` ```mermaid ```` blocks, answers in `<details>`, code blocks with location tags or marked illustrative. No Quarto-only syntax (`:::`, `{.python ...}`, `# <1>`). Reads correctly when pushed to GitHub. No `.gitignore` is created.
