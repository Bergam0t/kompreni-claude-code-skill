# Scenario 18: second explanation in one conversation

**Setup:** Any git project.

**Task:** Ask for a change, run `/kompreni:explain`, ask for a follow-up change to a related file, run it again.

**Expect:** The second covers only the follow-up, says it's since the last explanation, explains how it interacts with the first change, and ends with a new snapshot line. The working tree, index and stash are unchanged throughout.
