> *An example of `/kompreni:explain` output, written in another repository: its file references and paths point there. See [the examples README](README.md).*

# Explanation: a faster simulation without pandas in the hot loops

Depth: deep. Level: intermediate. History mode with `since=4188308`, covering commits `364702f`, `f86edd2` and `8a5fc92`.

**In one paragraph.** The simulation spent most of its time in pandas rather than in SimPy. For every new caller, every step of a journey and every result row, it built or filtered a small DataFrame to look up a value that never changes during a run. These three commits move that work to the two ends of a run. Lookups are built once, as lists, dicts and a `Counter`, when the model starts. DataFrames are assembled once, when results are written. Seeded output is byte-identical, and a 3-day run went from about 31s to 0.2s when the versions were timed back to back *(observed)*.

## Concepts used here

- **Why `random.choices` gives identical draws:** `random.choices(items, weights=w)` builds cumulative weights and picks with one random number. The same items, in the same order, with the same weights, give the same pick. So replacing a pandas Series with a plain list of the same values changes nothing. That's why the new lookups keep CSV row order (`transitions.py:36-41`).
- **The fixed cost of each pandas call:** a filter, `.query()` or `concat` builds new objects every time. Inside a loop that runs thousands of times, that fixed cost dominates. A dict lookup costs almost nothing.

## What changed, by purpose

*Storing results (`364702f`).* `store_patient_results` used to rebuild the whole table for every row:

```python hsm.py:386@4188308
        self.results_df = pd.concat([self.results_df, df_dictionary], ignore_index=True)
```

Each call copied every earlier row, so the cost grew with the square of the run's length. Rows are now appended to `self.results_rows` (`hsm.py:406`) and joined once, in `write_all_results`:

```python hsm.py:418
self.results_df = pd.concat(
    [self.results_df, pd.DataFrame(self.results_rows)], ignore_index=True
)
```

*Arrival rates (`f86edd2`).* `generate_111_calls` ran three identical `.query()` calls for each caller. Now:
- `HSM.__init__` indexes `inter_arrival_times.csv` once, by (hour, weekday flag, quarter) (`hsm.py:112-119`).
- The generator does one lookup per caller (`hsm.py:214`).
- The start date is parsed once (`hsm.py:122`).

*Per-step and per-caller lookups (`8a5fc92`).*
- **Next destination:** `next_destination` filtered the transition table on every step. It now reads lists grouped once in `Transitions.__init__` (`transitions.py:78-79`).
- **Network graph:** every step ran a row-wise `apply` over the 42-row table. Now each step increments a `Counter` (`hsm.py:318`), and the table is filled once when results are written (`hsm.py:429-432`).
- **The rest:** `avoidable_ed_admission`, the caller's disposition draws and the GP surgery draw now use dicts and lists built once (`caller.py:29-36`, `hsm.py:193`).

## Why it was done this way

- **Byte-identical output was the requirement** *(stated)*, so the seeded regression test could prove each step. Every choice follows from it: lists keep CSV order, the draws stay the same, and the single concat keeps the CSV format.
- **Concatenating onto the empty `results_df`,** rather than writing `pd.DataFrame(rows)` directly, keeps the old column order. It also keeps the float formatting (`1.0`) that `utilities.py:208` relies on *(code, comment at `hsm.py:415-417`)*.
- **Batched scipy sampling was dropped.** A profile showed sampling took about 1% of the run, and batching would have changed the order of random draws *(observed, stated)*.
- **Three commits:** each tackled the largest remaining hotspot, and was tested and benchmarked before the next *(stated)*.

## How the pieces fit together

```text
start-up     CallDispositions / HSM.__init__ / Transitions.__init__  -> lists, dicts, Counter
per caller   Caller + generate_111_calls        -> dict and list reads only
per step     next_destination + transition count -> dict read, Counter += 1
per row      store_patient_results              -> list append
end of run   write_all_results                  -> one concat, one weight fill, CSVs
```

Nothing outside the model changed. `runSim` still builds an `HSM` and calls `run()`, and the CSVs the Dash app reads are identical.

## Limitations and knock-on effects

- **The lookups are snapshots taken at start-up.** Code that later edited one of the source DataFrames during a run would no longer affect the simulation *(code)*. Nothing does this today.
- **Results are only filled in at the end.** `results_df` and the network weights are only filled in `write_all_results`. During a run, the data lives in `results_rows` and `transition_counts`.
- **A missing key now raises `KeyError`,** instead of failing on an empty selection *(inferred)*.
- **The arrival cut-off bug is still there,** and still pinned by the regression test (`hsm.py:185-186`).

## Verification

No tests were added in this range. These commits were made in the same working session, and the regression test (`tests/test_regression.py`) passed after each one, ending at 4 passed in 1.83s *(observed)*. Three settings the test doesn't cover gave identical output before and after `8a5fc92` *(observed)*: the `max` and `mean` arrival options, and the `tree` transitions. There's no PR, so there are no CI results.

Gaps: nothing was run through the Dash app's process pool, or on Linux.

## How it got here

- `364702f`'s commit message says 34.5s → 14.7s. That was measured while the machine was busier. Timed back to back, the same two versions took 10.9s and 5.6s *(observed)*.

## Worth remembering

- In this model, don't filter, query, `apply` or concatenate a DataFrame per caller, step or row. Build a lookup in an `__init__` instead.
- To keep seeded output identical, a lookup must give the same values, in the same order, as the code it replaces.
- Run `pytest` after any change to the model. It takes under 2 seconds now.

## Useful elsewhere

- **Gotcha: `pd.concat` in a loop is quadratic (pandas 1.4.4).** Collect dicts in a list and build the frame once. Here that alone halved a 3-day run *(observed)*.
- **Gotcha: an empty DataFrame decides the dtypes of rows concatenated onto it (pandas 1.4.4).** Integers become floats, written as `1.0`. A faster rewrite must keep that step if the exact output matters *(observed in the saved CSVs)*.
- **Technique: profile before optimising.** The suspected hotspot, scipy sampling, took about 1% of the run, so the riskiest planned change was dropped *(observed)*.

## Scope

`4188308..8a5fc92`, 3 commits, made in one working session. Uncommitted files at the time (walkthroughs, and `output/MOOOD-study/_publish.yml`) aren't included. `gh` found no PR for these commits.

The same range has a full walkthrough: `kompreni/walkthroughs/2026-11-26-faster-simulation-without-pandas-hot-loops.qmd`.
