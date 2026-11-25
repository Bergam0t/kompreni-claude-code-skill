# Scenario 25: walkthrough of a pushed commit

**Setup:** A repo with a GitHub remote and a pushed multi-file commit that isn't `HEAD`.

**Task:** Run `/kompreni:walkthrough commit=<sha>`.

**Expect:** The front matter has `source: commit`, `base` = the parent's full SHA, `tip` = the commit's full SHA, `dirty: false`. References carry GitHub permalinks at the full SHA, and `check_refs.py --ref <sha>` passes. Rationale comes from the commit message and PR, labelled. The checkout is unchanged.
