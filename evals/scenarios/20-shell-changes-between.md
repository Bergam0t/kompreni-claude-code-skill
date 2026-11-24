# Scenario 20: shell-made changes between explanations

**Setup:** Any git project.

**Task:** After one explanation, ask Claude to change a file using only sed or a script, and to create a new file the same way. Explain again.

**Expect:** Both shell-made changes appear: the snapshot diff catches them, including the untracked file.
