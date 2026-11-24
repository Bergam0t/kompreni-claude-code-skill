# History mode

Used when `branch`, `since` or `commit` is given. You are explaining committed history, so the conversation usually can't tell you why something was done. Commit messages, the PR and the code itself have to. This file replaces SKILL.md step 2 and adjusts step 6. Everything else in SKILL.md and `output-guide.md` still applies.

**Never change the repository state.** Don't check out, stash, reset or pull. Read files at the tip with `git show <tip>:<path>`.

## 1. Resolve the range

| Argument | Base | Tip | Diff | Commits |
|---|---|---|---|---|
| `branch=<name>` | `git merge-base <onto> <name>` | `<name>` | `git diff <base> <name> --` | `git log --no-merges <onto>..<name> --` |
| `since=<ref>` | `<ref>` | `HEAD` | `git diff <ref> HEAD --` | `git log --no-merges <ref>..HEAD --` |
| `commit=<ref>` | `<ref>^` (first parent) | `<ref>` | `git diff <ref>^ <ref> --` | just `<ref>` |

**Always end range commands with `--`** (and put any paths after it). A branch name can also be a file or folder name in the repo, and without `--` git fails with "ambiguous argument".

- **`onto`** (the default branch), if not given, is the first of these that works:
  1. `git symbolic-ref --short refs/remotes/origin/HEAD`
  2. `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`
  3. a local `main`, then `master`
  4. ask the user.

  Say which one you used.
- **Unknown ref**: `git rev-parse --verify <ref>^{commit}` fails. Say so and stop.
- **Branch already merged**: the merge-base equals the branch tip, so the range is empty. Say the branch appears to be merged already, and suggest `commit=<merge or squash commit>` with the actual SHA. Find it through the PR first (`gh pr list --head <name> --state merged --json number`, then `gh pr view <n> --json mergeCommit --jq .mergeCommit.oid`), which also works for squash merges. Otherwise use `git log --merges --ancestry-path <tip>..<onto> --oneline -- | tail -1`.
- **Branch with no commits beyond `onto`** (not merged, just nothing committed yet): say so, and mention any uncommitted work, which session mode can explain.
- **Merge commit given to `commit=`**: diff against the first parent, and say that this shows everything the merge brought in.
- **Root commit** (no parent): diff against the empty tree with `git show --stat <ref>`, then `git show <ref>`.

## 2. Collect

In one Bash call, run the following over the range:
- `git rev-list --count --no-merges <range> --`
- `git log --no-merges --format='--- %h %an %ad%n%s%n%b' --date=short <range> --`
- `git diff --stat <base> <tip> --` and `git diff --shortstat <base> <tip> --`

Then read the diffs group by group, as in session mode: summarise lockfiles, generated code and formatting in one line.

**Large ranges.** Above about 30 commits or about 1500 changed lines:
- use `deep` depth unless the user gave a depth;
- prioritise by behavioural impact, not by line count;
- say plainly what you explained in depth and what you only summarised;
- suggest `focus=<path or topic>` for a closer look.

## 3. Scope note (instead of the attribution check)

Write one or two lines at the end, under **Scope**, giving:
- the range you resolved, such as `main..review-fixes`, 7 commits, merge-base `abc1234`;
- that changes merged in from the default branch are excluded, because the diff starts at the merge-base;
- for `since=`, or a `branch=` that is checked out: if `git status --porcelain` shows uncommitted work, that it is not included;
- whether a PR was found, or why it wasn't looked for.

**Mixed case.** If this conversation made some of the commits in the range, use the conversation as the source of intent for those (*(stated)*), and the sources below for the rest.

## 4. Sources of "why"

Use them in this order. Label every piece of rationale, as in `output-guide.md`.

1. **Commit messages**, cited as *(commit `abc1234`)*. A message is the author's claim, not verified fact. Messages written by agents are often summaries of what changed, not why, so don't present them as reasons when they aren't.
2. **The pull request**, if `gh` works and the remote is on GitHub.
   - For `branch=`: `gh pr list --head <name> --state all --json number,title,url`.
   - For `commit=` or `since=`: `gh pr list --search <sha> --state merged --json number,title,url`.
   - Then `gh pr view <n> --json title,body,reviews,comments,statusCheckRollup`.
   - Cite as *(PR #n)*. Review comments that led to changes are especially useful.
   - If `gh` is missing, unauthenticated or the remote isn't GitHub, skip this and say so in the scope note. Don't ask the user to install anything.
3. **The changes themselves**: code comments, tests, and changelog or docs edits inside the range. Cite these as *(code)*.
4. ***(inferred)*** as a last resort, worded as such. If no source gives a reason, say the reason isn't recorded.

## 5. How it got here (optional)

Add a short **How it got here** section (at most about five bullets, each citing SHAs) only when the commit sequence teaches something the final diff hides:
- an approach that was tried and reverted or replaced (evidence of an alternative considered);
- fix-ups after review comments;
- a change of direction partway through.

Skip it when the commits are linear or uninformative ("wip", "fix typo").

## 6. Verification

- Report tests added or changed in the range.
- If a PR was found, report its CI checks from `statusCheckRollup`: which passed, failed or are pending.
- Otherwise say "No test results are available for this range."
- Don't run the tests yourself unless the tip is the current checkout and the tree is clean. Even then, offer and wait for a yes; never check out to run them.

## 7. Checking references

Line numbers refer to the **tip**, so pass `--ref <tip>` to `check_refs.py` (a branch name, a SHA, or `HEAD`). "Before" snippets use `@<base>` in their fence, as in `python src/a.py:10-14@abc1234`.

For `since=` the tip is `HEAD`. If the tree is dirty, still pass `--ref HEAD`, so that references point at committed code, not your uncommitted edits.
