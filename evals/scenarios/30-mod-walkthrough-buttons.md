# Scenario 30: Walkthrough and Code tour buttons

**Setup:** Load the skill and the mod: `claude --plugin-dir . --plugin-dir mods/kompreni-offer`.

**Task:** Make a change, then press **Walkthrough**. Send it. Make another change, set depth to `brief`, and press **Code tour**.

**Expect:** The first fills in `/kompreni:walkthrough` plus the level, with no scope. After it runs, the count resets. The second fills in `/kompreni:walkthrough code=all` with no depth. Neither overwrites a draft. Without the walkthrough skill installed, neither button shows.
