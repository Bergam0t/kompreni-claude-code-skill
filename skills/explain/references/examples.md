# Examples (illustrative)

These describe an invented small Python project. They show shape and tone, not real output. The file locations and snippets here don't exist, so `check_refs.py` would rightly reject them; in a real explanation every one must pass the checker.

## Brief

> Depth: brief. Level: intermediate. `parse_date` in [dates.py:14](src/dates.py#L14) crashed on an empty string because it indexed `s[0]` before checking length. It now returns `None` for empty or whitespace-only input *(code)*, and its one caller, `load_row`, already treats `None` as "skip this row" ([loader.py:31](src/loader.py#L31)), so blank cells are now skipped instead of aborting the import. A regression test was added in `tests/test_dates.py`; I ran the full suite (42 passed). Non-date garbage such as `"abc"` still raises, which wasn't touched.

## Standard

> Depth: standard. Level: intermediate.
>
> **In one paragraph.** Report exports were timing out for large accounts because the whole result was built in memory. The changes make the export stream rows in batches.
>
> **What changed, by purpose**
> - *Streaming export.* `build_report` used to return a list; it now yields batches of 500 rows ([report.py:40](src/report.py#L40)). `export_csv` writes each batch as it arrives ([export.py:22](src/export.py#L22)).
> - *Callers adapted.* The API endpoint wraps the generator in a streaming response ([api.py:88](src/api.py#L88)).
> - *Tests.* `test_report.py` now consumes the generator and checks batch sizes.
>
> The core of the change, as it now reads:
>
> ```python src/report.py:40-44
> def build_report(account):
>     for start in range(0, account.row_count, BATCH_SIZE):
>         yield account.fetch_rows(start, BATCH_SIZE)
> ```
>
> **Why this way.** Batch size 500 is a constant with no stated rationale *(inferred: a round number)*. Streaming rather than pagination was your request *(stated)*.
>
> **Limitations.** `build_report` is also called by `email_summary` ([mail.py:17](src/mail.py#L17)), which does `len(report)`. That breaks on a generator. I haven't changed it. *(code)*
>
> **Verification.** 6 tests in `test_report.py` pass. Nothing exercised the API endpoint or `email_summary`.
>
> **Worth remembering.** `build_report` is now a generator: anything that indexes it or takes its length needs updating.

## Deep (abridged)

> Depth: deep (an interface change touching three modules). Level: advanced, so no concepts section.
>
> **In one paragraph.** Plugins used to register handlers by editing the router's dict. They now register through a `Registry`, so the router no longer knows about plugins at all.
>
> **What changed, by purpose**
> - *New `Registry`* ([registry.py:8](src/registry.py#L8)) holds handlers by route and rejects duplicates.
> - *Router decoupled.* `Router.dispatch` asks the registry instead of reading `HANDLERS` ([router.py:55](src/router.py#L55)).
> - *Plugins migrated.* All four built-in plugins call `registry.add` at import time.
>
> **How the pieces fit together**
> ```text
> plugin import --add()--> Registry <--lookup()-- Router.dispatch
> ```
> Registration happens at import, so import order now decides which plugin wins a duplicate route. It used to be dict-literal order *(code)*.
>
> **Why this way.** The duplicate check was requested *(stated)*. Making `Registry` a module-level singleton rather than an instance on `Router` is *(inferred)* to keep plugin code to one line.
>
> **Limitations.** Third-party plugins that still mutate `HANDLERS` will silently stop working ([router.py:12](src/router.py#L12) keeps the name, now empty). No test covers that.
>
> **Verification.** 31 tests pass; the new duplicate-route test is in `test_registry.py`. Import-order behaviour is untested.
>
> A structured walkthrough could be worth writing for a change this size.

## History mode: `branch=retry-uploads` (abridged)

> Depth: standard. Level: intermediate. History mode: `main..retry-uploads`, 4 commits.
>
> **In one paragraph.** Uploads to object storage failed outright on any network error. The branch retries them with backoff, and stops retrying errors that can't succeed, such as a missing bucket.
>
> **What changed, by purpose**
> - *Retry wrapper.* `upload()` now calls `with_retry(send, attempts=4)` ([storage.py:61](src/storage.py#L61)); before, it called `send` once.
> - *Which errors retry.* `is_retryable` treats timeouts and 5xx as retryable, and 4xx as final ([retry.py:12](src/retry.py#L12)).
>
> **Why this way.** Retries were added after uploads failed on flaky Wi-Fi *(PR #41)*. The 4xx rule came from review: "retrying a 403 just delays the error" *(PR #41)*. Four attempts is not explained anywhere *(inferred: a conventional default)*.
>
> **How it got here**
> - The first version retried every exception (`3f1c2a0`). It was narrowed to `is_retryable` after review (`9be7d14`).
> - Jitter was added in a separate commit, "avoid thundering herd" (`c02e5f9`) *(commit `c02e5f9`)*.
>
> **Verification.** `test_retry.py` was added (6 tests). The CI checks on PR #41 passed. No test covers `upload()` itself with a failing network.
>
> **Scope.** Merge-base `e81d3b2`; changes merged in from `main` are excluded. Uncommitted work in the current checkout isn't included.

## Level `"fluent in R, new to Python"` (abridged)

> Depth: standard. Level: new-to-language, with comparisons to R (as you asked).
>
> **In one paragraph.** The dashboard re-read the same 200 MB CSV on every page refresh. It now reads each file once and reuses the result.
>
> **Concepts used here**
> - **Decorators** (`@lru_cache` at [data.py:8](src/data.py#L8)). A line starting with `@` above a function wraps that function in another one when it's defined. It's like writing `load_table <- memoise::memoise(load_table)` in R, but placed above the definition.
> - **`functools.lru_cache`**. Python's built-in equivalent of `memoise`: it remembers results by argument. Unlike `memoise`, the arguments must be *hashable* (strings, numbers, tuples; not lists or data frames). That's why `load_table` takes a file path, not a data frame.
> - **`with` blocks** ([data.py:11](src/data.py#L11)). They open a resource and guarantee it's closed afterwards, even on an error. It's the job `on.exit(close(con))` does in an R function.
>
> **What changed, by purpose**
> - *Cached loading.* `load_table(path)` is wrapped in `@lru_cache(maxsize=8)`, so the eight most recently used files stay in memory *(code)*.
> - ...
>
> **Worth remembering.** The cache holds the *same* data frame object for every caller. If any caller modifies it in place (as `df["x"] = ...` does, much like R's `data.table` `:=` and unlike ordinary R assignment, which copies), every later caller sees the modified version.
