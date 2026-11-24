# Scenario 9: branch with main merged in

**Setup:** Create a feature branch with 2-3 commits. Add an unrelated commit to main, merge main into the branch, then add one more branch commit.

**Task:** Run `/kompreni:explain branch=<feature>` from main.

**Expect:** Only the feature's changes are explained, not main's unrelated commit. The scope note names the merge-base. No checkout happened.
