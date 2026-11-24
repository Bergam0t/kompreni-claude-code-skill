# Examples (illustrative)

These describe an invented small Python project. They show shape and tone, not real output. The file locations and snippets here don't exist, so `check_refs.py` would rightly reject them; in a real explanation every one must pass the checker.

## Brief

> Depth: brief. `parse_date` in [dates.py:14](src/dates.py#L14) crashed on an empty string because it indexed `s[0]` before checking length. It now returns `None` for empty or whitespace-only input *(code)*, and its one caller, `load_row`, already treats `None` as "skip this row" ([loader.py:31](src/loader.py#L31)), so blank cells are now skipped instead of aborting the import. A regression test was added in `tests/test_dates.py`; I ran the full suite (42 passed). Non-date garbage such as `"abc"` still raises, which wasn't touched.

## Standard

> Depth: standard.
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

> Depth: deep (an interface change touching three modules).
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
