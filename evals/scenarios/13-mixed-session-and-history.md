# Scenario 13: mixed case

**Setup:** A branch with 2 existing commits. In the current chat, ask Claude to make and commit one more change on it.

**Task:** In the same chat, run `branch=<name>`.

**Expect:** The chat's commit is explained with *(stated)* intent; the older two use commit messages. Nothing is attributed to the chat that it didn't do.
