# mutlib — fast, strict, shared mutation harness

`mutlib.py` replaces the per-session `mut_*.py` run loops. Those loops started a fresh `python test_X.py <mutant>`
subprocess per mutant and ran the whole fixture suite every time, which took 1.5 to 3 hours per N-family scorer.
mutlib reads the same mutant lists and runs the same fixture suites, but it never edits them: the mutant scorer
goes to a scratch directory, and the suite is transformed in memory.

```
python mutlib.py --scorer S --test T --mutants M [--workers N] [--no-memo] [--no-hoist] [--no-fast]
                 [--only a,b] [--changed-from PARENT_SCORER --sample 0.2 --seed N] [--control]
                 [--timeout SEC] [--out FILE]
```

Examples (run from `C:/kyty/s106_stage/mutlib`):

```
python mutlib.py --scorer C:/kyty/s113/vbn113b.py --test ../test_vbn113b.py --mutants ../mut_vbn113b.py --control --out vbn113b.mut.txt
python mutlib.py --scorer ../net112.py --test ../test_net112.py --mutants ../mut_net112.py --control --out net112.mut.txt
python mutlib.py --scorer ../shn113.py --test ../test_shn113.py --mutants ../mut_shn113.py --changed-from ../net112.py --sample 0.2
```

* **Exit codes:**
  * 0: every selected mutant was killed and every control survived.
  * 1: at least one mutant survived.
  * 2: the run is not certified. A mutant timed out or hit a harness error, a control was killed, or hoisting
    diverged on a survivor.
  * 3: refused. Possible causes: `C:/kyty/SEALED_RUN.lock` exists, a bad anchor, an unsupported suite shape, or
    the unmutated scorer fails its own suite.
* **Report:** the header gives the sha256 of the harness, scorer, test and mutant script, the format, the family
  and the selection. Then comes one line per mutant: `<name>  KILLED by <first failing case>  (s)`,
  `<name>  KILLED (crash: ...)`, `<name>  SURVIVED`, or `<name>  TIMEOUT ...`. Totals follow, then `ALL KILLED`,
  `SURVIVORS: [...]` or `NOT CERTIFIED`. Progress lines go to stderr as they finish. `--out` writes the ordered
  report to a file.
* **Never run it during a sealed run.** It refuses while `C:/kyty/SEALED_RUN.lock` exists, and by default it
  uses cpu_count − 4 = 28 processes.
* **`--dry-run`** prints the header (hashes, format, family, fast / hoist / memo decisions) and the selection, then
  exits without running anything. Use it to check a `--changed-from` selection first.
* **Dispatch order:** the slowest mutants of the previous run go first, new ones before them, so the run does not
  end on a long tail. The timings come from `cache/<stem>/durations.json`. The report always keeps definition
  order.

## How it works

1. **Mutant extraction (the mutant script is never run).** The script is parsed with `ast`. Only the statements
   before the harness part are candidates: that part starts at the first `def run`, the first loop over
   `MUTANTS` / `M`, or a `try` / `while` / `with` / `__main__` block. Of the candidates, mutlib evaluates only:
   * the statements that define mutants: `MUTANTS = [...]` and re-filters of it, or `mutant(...)` calls,
     including the ones inside `for` loops;
   * the assignments and helper definitions those statements read, found as a transitive closure;
   * imports.

   Prints, `mkdir` and `SRC = ...read` statements are skipped unless something needs them. `mutant()` is
   replaced by a stub that fills an ordered dict and refuses duplicates. The original helper must be plain
   "assert + `M[name] = (old, new)`", otherwise extraction is refused. Every anchor must occur exactly once
   in `--scorer` and must differ from its replacement, otherwise the run aborts (like the N-family harness).
   Note that the list-family scripts only printed `ANCHOR xN` and skipped the mutant.
2. **In-process execution.** Workers are a pool of `spawn`-ed processes, one pipe each. For every job, a worker:
   * writes the mutant scorer to `work/<run>/w<k>/m/<scorer basename>`. The directory is fresh for every
     mutant and `sys.dont_write_bytecode` is set, so no stale `.pyc` can be picked up.
   * `exec`s the compiled transformed suite in a fresh globals dict, with `__name__ == '__main__'` and
     `sys.argv = [test, mutant(, fx dir when the suite reads argv[2])]`.
   * captures stdout and stderr.
   * catches `SystemExit`, `MutantKilled`, `HoistUnsafe` and any other exception. Any other exception is
     reported as `KILLED (crash: ...)`.
   * restores argv, streams, environment, cwd and `sys.path` afterwards.

   Each job's fixture directory is removed first, so every mutant starts from a clean slate like a first run.
   A job that exceeds `--timeout` has its worker killed and restarted. The default timeout is max(120 s,
   3 × the baseline). A timeout is reported as **unresolved, never as killed**, because a slow mutant whose
   suite would still pass must not count as killed.
3. **Suite transformation (AST, in memory).**
   * **Fixture directory:** the single top-level `BASE = Path(...)` points at the worker's own fixture directory.
   * **Guards:** every `ok &= X` and `ok = ok and X` on the module's `ok` becomes `ok &= _mutlib_guard(X, ...)`.
     This covers the module level, loops, and functions that declare `global ok`. A function's local `ok` is
     not touched. The guard returns X unchanged, and in fast mode a falsy X raises `MutantKilled`.
   * **Failing case name:** in the V family the name is recovered from the output. Either the line printed since
     the previous guard has a `FAIL` token (print-then-guard), or the next printed line does (guard-then-print).
     The first token of that line is the case name.
   * **Fast mode:** the early exit is used only when it is provably exact:
     * `ok` is initialised once to `True`;
     * `ok` is only ever updated by `&=` / `ok and`;
     * the suite ends with `sys.exit(<depends on ok>)`;
     * there is no other exit in the suite.

     Otherwise fast mode is off, and every suite runs to its end with the verdict taken from the exit.
4. **Hoisting (N family: `def case(...)` appending to a list, checked by a final `for c in cases:` loop).**
   * **Why it is needed:** in these suites `case()` only *registers* a case. Its `run` is a lambda that is called
     in the final loop, after all ~100 fixture logs (about 2 GB) have been written. So early exit in the final
     loop alone would still pay for all of the fixture generation.
   * **What mutlib builds:**
     * the final loop body is copied into `def _mutlib_check(c)`, with `continue` changed to `return`, and a bare
       guard labelled `c['name']` instead of the `ok` update;
     * the helpers the body needs are copied in front of it (`failing`);
     * `case()` calls the check on the case it has just appended.

     Each case is therefore evaluated as soon as it is registered, in the original order. The original final loop
     stays, and it re-checks every case of a mutant that survives the hoisted phase.
   * **Soundness gates:** the original ran every check *after* the last fixture statement, so each gate below
     checks that moving the checks earlier cannot change a result.
     * **Static:**
       * No module name that is bound more than once is read lazily by a lambda, function or the loop body.
         This rules out late-binding loop variables.
       * No module-level store into objects, and no container mutation, after the first `case()` call.
       * The loop body neither breaks, nor mutates its case, nor reads `ok`.
       * `case()` has no return.
     * **Per hoisted check, at run time, for every mutant:**
       * The interpreter state is fingerprinted before and after each check. This covers the scorer module's
         globals (functions by identity; data by a hash of its repr), the identities of the test's globals,
         the environment and the cwd.
       * An audit hook records every file write, remove, rename, mkdir, etc.
       * Any change, any write, or any exception raised by the check itself (as opposed to by the run it
         wraps) raises `HoistUnsafe`. The mutant is then **rerun faithfully without hoisting**, and the report
         says so: `[faithful rerun: ...]`.
       * A `SystemExit` raised by a check is a kill, exactly as it would be in the final loop.
     * **Baseline, before any result is trusted:**
       * The unmutated scorer runs in record mode, where guards never raise.
       * It must pass, and the lines printed by the 205 hoisted checks must equal, byte for byte, the lines
         printed by the original final loop.
       * Every file read and every directory listed by a hoisted check is recorded with its stat when read,
         and must be unchanged when the final loop starts. Stat probes (`os.stat`, `os.path.*`) are covered too.

     If any baseline condition fails, every job is restarted with hoisting off (`hoist: DISABLED at run time`).
     Mutants are scheduled optimistically while the baseline is still running.
5. **Parse memo (`read_run`).**
   * **When it is on:** by default, for scorers with a top-level `read_run`. The test's
     `importlib.util.spec_from_file_location` is wrapped, so `exec_module` of the mutant path also installs a
     memo wrapper on `module.read_run`. The scorer's other functions reach the wrapper through the global.
   * **Memo key:** it combines four parts.
     * The dependency hash: sha256 of the source segments and AST dumps of `read_run` and of every top-level
       binding it reads, transitively, *in this mutant's source*. A mutant touching any of them therefore
       misses by construction.
     * The current values of the data dependencies in a canonical form (sets sorted). A test that reassigns
       `mod.X` changes the key. A rebound or modified function dependency bypasses the memo.
     * sha256 of the bytes of every file parameter, or "none" / "absent".
     * The other arguments, in canonical form.
   * **When the memo is refused for a source:** the static purity check must pass, and the refusal applies to
     that source only, so its calls go straight through. The check fails on any of these:
     * `read_run` or its dependencies open anything other than a file parameter read-only;
     * they use `Path` other than `Path(param).is_file()` / `.exists()`;
     * they use `os` / `sys` / `time` / `random` / `print` / ...;
     * they write into module-level objects;
     * they declare `global`;
     * they are generators.

     A file parameter is one used only in `open(p, read mode)`, `p is (not) None`, or `Path(p).is_file()` /
     `.exists()`.
   * **Storage:** values are stored pickled, in a per-worker LRU (`--memo-mem-mb`, 256 MB by default) and on
     disk in `cache/<scorer stem>/<key>.pkl`. Each file has a magic header and a payload sha256 and is written
     with an atomic replace. Only entries of the *unmutated* dependency hash go to disk, so they are shared by
     all workers and all later runs; a mutant that changes `read_run`'s closure keeps its entries in memory.
   * **Fresh copies:** every call, hit or miss, returns a fresh `pickle.loads` copy, so a hit behaves exactly
     like a recomputation.
6. **Verdict.** A mutant survives only if its suite exits 0 and all of these hold:
   * no guard failed;
   * no line was left pending;
   * `FIXTURE FAILURES` was not printed;
   * `ALL OK` was printed, when the baseline prints it.

   This is the old N-family criterion. It is at least as strict as the old V-family one, which looked only at
   the exit code.
7. **Controls (`--control`).** These are three equivalent mutants that must survive:
   * a comment line added after the docstring;
   * `pass` at the end of `read_run`, which changes the memo dependency hash so the uncached path runs;
     `evaluate` is used when there is no memo;
   * `pass` at module level at the end of the file.

   A killed control means the harness or the suite is nondeterministic, and the exit code is 2.
8. **`--changed-from PARENT`** runs every mutant whose anchor overlaps a line that `difflib` finds changed
   between PARENT and `--scorer`. It adds a reproducible sample of the rest: `--sample` (0.2 by default),
   seeded by the first 16 hex digits of the scorer sha256 unless `--seed` is given. The report lists both sets.

## Residual assumptions (stated, not hidden)

* A hoisted kill assumes that the fixture code run *after* the killing case does not change the files that case
  read. This is verified on the baseline (read audit plus the line-for-line comparison), but not per mutant: a
  mutant can only influence fixture code through the scorer module's values, and the per-check fingerprint
  catches any lasting change to those. `--no-hoist` removes this assumption at roughly twice the cost for N
  suites.
* The fingerprint covers scorer module globals, test global bindings, the environment and the cwd. It does not
  see mutations of objects that are reachable only through the test's own containers (the tests do not share
  them with the scorer).
* Set iteration order in memoised values follows pickle reconstruction. Across processes this was already not
  stable in the old harness (string hash randomisation).

## Validation done (2026-09-24)

* **Reference comparison:** `work/verify/ref_run.py` runs the ORIGINAL suite text, with only its BASE line
  redirected under `work/`, in a fresh subprocess per mutant, as the old harness did. It compares the verdict
  and the first failing case with the mutlib report.
  * check112: 24/24 agree.
  * vbn113b (sealed `C:/kyty/s113/vbn113b.py`): 41/41 agree.
  * vdg112: 36/36 agree.
  * vbn113c (sealed): 43/43 agree, including its one survivor, `bad_race`.
* **net112, all 277 mutants:** for 277/277, mutlib's `KILLED by <case>` equals the FIRST entry of the old
  harness's failing-case list in `net112/mut_net112.out.txt`. The 3 controls survived. The baseline passed in
  hoisted mode, and its 205 hoisted-check lines were identical to the final-loop lines.
* **Safety nets:**
  * Synthetic mutants in `work/verify/mut_syn_net112.py`:
    * `SYN_state` adds a module global: detected, faithful rerun, SURVIVED.
    * `SYN_write` makes `read_run` write a file: the memo is refused as impure, the write is detected, faithful
      rerun, SURVIVED.
    * `SYN_hang`: TIMEOUT, the worker is restarted.
  * `work/verify/test_syn_hoist.py`: a suite whose final loop prints `len(cases)`, so the hoisted lines differ.
    The baseline's check caught it, hoisting was disabled at run time, and every job was restarted faithfully.
    The verdicts were correct.
* **Finding:** vbn113c has a real survivor. `bad_race` adds `bda_nrace` to `bad`. The verdict is unchanged by
  construction (the GO branch already requires `bda_nrace == 0`), but prediction B1 (`BAD == 0`, read from
  `r['bad']`) and `out['bad']` are never checked on a fixture that has races only. A missing fixture of the
  kind `(dict(race=1), 'B1', True)` would kill it. The mutant script defines 43 mutants, not 44.

## Measured timings (32 threads, 28 workers)

| suite | mutants (+3 controls) | old harness | mutlib wall |
|---|---|---|---|
| check112 | 24 | serial, 24 × 0.8 s ≈ 19 s | 2.9 s |
| vdg112 | 36 | serial, 36 × 7.2 s ≈ 4.3 min | 15.6 s |
| vbn113b | 41 | serial, 41 × 10.3 s ≈ 7.0 min | 20.9 s |
| vbn113c | 43 | never run (would be 43 × 11.1 s ≈ 8.0 min) | 23.5 s |

The old per-suite times were measured with `ref_run.py` on one worker. For the V suites the mutlib wall time is
bounded by the baseline and control runs, which each run the whole suite (10–18 s under full load).
| net112 | 277 | baseline 205 s + 277 × median 356 s over 16 lanes ≈ 1 h 45 min | 795 s (13.3 min) |

Details for net112:

* Per mutant, mutlib took a median of 43 s and a mean of 67 s (p90 168 s), against the old median of 356 s. That
  is 18 677 s of worker time against 97 620 s.
* The baseline took 320 s: it runs record mode with a warm memo, evaluating hoisted and then final.
* The `pass`-in-`read_run` control took 714 s, because every parse misses by construction.
* **Where the time goes now:** with a warm memo, `read_run` costs about 0.06 s per case (hash plus unpickle)
  instead of 0.7 s. What remains is the scorer's own `evaluate()`, mostly `block_means` → `statistics.fmean`,
  and the suite's `make()` fixture writing, about 2 GB per full suite. Both are inherent to the scorer and the
  suite.
* **First run of a new scorer:** the cache starts cold. The baseline and the first mutants fill it at the same
  time, and the later mutants read from it.

## Files

* `mutlib.py`: the harness.
* `cache/<scorer stem>/`: the shared parse memo. It can be deleted at any time and is rebuilt by the next
  baseline. It is about 6.5 MB per distinct fixture log, about 0.8 GB for net112.
* `work/`: per-run scratch (`<stem>_<pid>_<time>/w<k>/{fx,m}`), removed at the end unless `--keep-work` is given.
  `work/verify/` and `work/probe/` hold the development checks above.

## Changelog

* 2026-09-24, acceptance (`ACCEPTANCE.md`, `accept/`): net112 277/277 and shn113 310/310 killed, each naming the earliest old
  failing case; vbn113b 41/41, vdg112 36/36, check112 24/24 killed; all controls survived; vbn113c 42/43 (`bad_race`, a real
  gap in the suite, confirmed without mutlib). No defect found, **no code change**: mutlib.py stays sha256
  `db8703bdf0820c9023e9f1a9d69ddfae6fddc00b8035d0294704b85115de00fb`.
