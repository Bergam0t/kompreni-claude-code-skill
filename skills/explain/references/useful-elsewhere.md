# "Useful elsewhere": lessons that transfer

A short section of things the reader can take to other code, learned from this change: a library that behaved unexpectedly, a design worth reusing, a technique that solved a problem. Explanations, walkthroughs and code tours all use it.

## What goes in it

Three kinds of item:

- **Gotcha**: a library, tool, language or platform that behaves in a surprising way, which this change ran into or works around. Name the library, and its version from the lockfile or manifest when the behaviour depends on it.
- **Pattern**: a design or architectural approach used here that could be adapted elsewhere. Say when it fits and what it costs, not only that it exists.
- **Technique**: a way of debugging, testing or working with tools that worked here, such as making a timing-dependent test deterministic.

## How it differs from the neighbouring sections

| Section | Answers | Example |
|---|---|---|
| **Concepts used here** | What do I need to know to *read* this change? Depends on the level | "A decorator wraps a function when it's defined" |
| **Worth remembering** | What must I keep in mind about *this codebase*? | "Callers must not modify what `load_table` returns" |
| **Useful elsewhere** | What does this change teach that holds *outside* it? | "A cache that returns shared objects lets one caller corrupt another's data" |

Don't repeat an item across sections. If a gotcha is needed to follow the change, explain it in Concepts. Here, give only the lesson to carry away, in one line.

## What qualifies

An item must pass all four:

1. **Grounded.** It is tied to this change: a `file:line`, an error or test failure seen in this session, a commit message or PR discussion. No generic advice ("write tests", "name things clearly", "handle errors").
2. **Transferable.** It would help someone working on different code, in this repo or another.
3. **Not obvious at the reader's level.** At `advanced`, skip textbook patterns, but keep gotchas and non-obvious trade-offs. At `new-to-programming`, a well-known pattern can qualify if you say plainly why it helps.
4. **Accurate.** Back claims about a library's behaviour with the code, the docs or source you checked, or what was observed. If it rests on memory alone, label it *(inferred)* and say "probably", or leave it out. A wrong gotcha does more harm than none.

**Leave the section out when nothing qualifies.** Most small changes teach nothing beyond themselves, and that is fine. Never pad it.

## Form

Each item is one bullet: a bold lead-in naming the kind and topic, then one to three sentences giving the lesson, where it showed up here, and when it applies or doesn't. Label the evidence as elsewhere (see `output-guide.md`).

```markdown illustrative
- **Gotcha: Git for Windows compares file times to the second.** A same-size edit made within the second git last recorded can look unchanged, and git re-reads such files only when they are no older than the index. Copying the index with a fresh timestamp switched that off and hid an edit (`skills/explain/scripts/snapshot.py:54`) *(observed: the test missed it 8 times in 60)*. When copying git's index, keep its timestamp.
- **Technique: make a timing flake deterministic.** Instead of rerunning a flaky test, set the timestamps it depends on explicitly (`os.utime`), so the race happens every time. The test then fails reliably before the fix and passes after *(code)*.
```

## How many

| Output | Items |
|---|---|
| Explain, brief | No section. If a gotcha would bite the reader again, one sentence at the end, before the snapshot line |
| Explain, standard | Up to 2 |
| Explain, deep | Up to 3 |
| Walkthrough, short | Up to 3 |
| Walkthrough, full, and code tours | Up to 5 |

Its words count towards the length limit.
