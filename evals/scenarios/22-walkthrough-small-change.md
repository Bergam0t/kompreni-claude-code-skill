# Scenario 22: walkthrough of a small change

**Setup:** Any git project.

**Task:** Ask for a one-line bug fix, then run `/kompreni:walkthrough`.

**Expect:** Says a walkthrough isn't worth it for a change this size, gives the `/kompreni:explain` command instead, and asks before writing. No file is written unless the user says yes; if they do, it is a short walkthrough.
