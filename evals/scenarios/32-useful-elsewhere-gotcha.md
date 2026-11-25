# Scenario 32: a library gotcha worth carrying away

**Setup:** A small Node project with a test runner.

**Task:** Ask for a function that groups a list of events (each with an ISO date string) by calendar month, labelled like "2026-03", with tests that include events on the first and last day of a month and in December. Then run `/kompreni:explain depth=standard`, and afterwards `/kompreni:walkthrough`.

**Expect:**
- Both include "Useful elsewhere" with a gotcha about JavaScript's `Date`: `getMonth()` counts from 0, and/or parsing a date-only ISO string gives UTC midnight, so local-time getters can shift it into the previous day or month. Each item is tied to the line that handles it, and labelled *(code)*, or *(observed)* if a test failed on it during the session.
- No generic advice ("write tests for edge cases"). At most 2 items in the explanation.
- The walkthrough's `kompreni.lessons` lists the same items, with `kind: gotcha` and `topic: "JavaScript Date"`.
- Every claim about `Date` is accurate.
