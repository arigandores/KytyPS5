# mutlib — fast, strict, shared mutation harness (v2)

`mutlib.py` replaces the per-session `mut_*.py` run loops. Those loops started a fresh `python test_X.py <mutant>`
subprocess per mutant and ran the whole fixture suite every time, which took 1.5 to 3 hours per N-family scorer.
mutlib reads the same mutant lists and runs the same fixture suites, but it never edits them: the mutant scorer
goes to a scratch directory, and the suite is transformed in memory.

**v2 is current.** v1 (sha256 `db8703bd…`) is kept as `mutlib_v1.py` (also archived as
`C:/kyty/KytyPS5/docs/session-113/mutlib/mutlib_v1.py`). v1 passed acceptance on six real suites (`ACCEPTANCE.md`),
but two adversarial reviews (`REVIEW_60857009.md` with `adversarial/`, `REVIEW_1e4c88d5.md` with `review2/`) showed
false-kill holes for general use. The section **v2: what changed and why, per hole** below maps every hole to its fix
and to the check that shows it closed. The decision behind v2 is ROADMAP §0.1, session 113, item 13.

```
python mutlib.py --scorer S --test T --mutants M [--workers N] [--no-memo] [--no-fast]
                 [--only a,b] [--changed-from PARENT_SCORER --sample 0.2 --seed N] [--control]
                 [--timeout SEC] [--out FILE]
```

The CLI and the report format are v1's, minus `--no-hoist` (there is no hoisting any more). Examples (run from
`C:/kyty/s106_stage/mutlib`):

```
python mutlib.py --scorer C:/kyty/s113/vbn113b.py --test ../test_vbn113b.py --mutants ../mut_vbn113b.py --control --out vbn113b.mut.txt
python mutlib.py --scorer ../net112.py --test ../test_net112.py --mutants ../mut_net112.py --control --out net112.mut.txt
python mutlib.py --scorer ../shn113.py --test ../test_shn113.py --mutants ../mut_shn113.py --changed-from ../net112.py --sample 0.2
```

* **Exit codes:**
  * 0: every selected mutant was killed and every control survived.
  * 1: at least one mutant survived.
  * 2: the run is not certified: a mutant is unresolved (timeout, harness error, environment failure, or a crash
    that a rerun did not reproduce) or a control did not survive.
  * 3: refused. Possible causes: `C:/kyty/SEALED_RUN.lock` exists, a bad anchor, a mutant script shape the strict
    extraction does not recognise, an unsupported suite shape, or the unmutated scorer fails its own suite.
* **Report:** the header gives the sha256 of the harness, scorer, test and mutant script, the format, the family, the
  memo decision and the selection, then the decisions taken after the baseline (fast mode confirmed or disabled,
  workers forced to 1, memo disabled). Then one line per mutant: `<name>  KILLED by <first failing case>  (s)`,
  `KILLED (crash: ...)`, `KILLED by exit N`, `KILLED (exit 0 before the end of the suite)`, `SURVIVED`,
  `TIMEOUT ...`, `UNRESOLVED (...)` or `HARNESS ERROR (...)`, with notes in brackets (rerun to confirm, rerun without
  the memo, rerun alone, console-encoding note). Totals follow, then the verdict line **with the mutant count**:
  `ALL KILLED (43 of 43 selected mutants killed; 43 defined in the mutant script)`, `SURVIVORS: [...] (...)` or
  `NOT CERTIFIED (...) (...)`. Progress lines go to stderr as they finish. `--out` writes the ordered report to a
  file.
* **Never run it during a sealed run.** It refuses while `C:/kyty/SEALED_RUN.lock` exists, and by default it
  uses cpu_count − 4 = 28 processes at a time.
* **`--dry-run`** prints the header and the selection, then exits without running anything.
* **Dispatch order:** the slowest mutants of the previous run go first, new ones before them, so the run does not
  end on a long tail. The timings come from `cache/<stem>/durations.json`. The report always keeps definition order.

## v2: what changed and why, per hole

Hole ids: `adv N` = `REVIEW_60857009.md` (triples in `adversarial/`), `r2 X` = `REVIEW_1e4c88d5.md` (files in
`review2/`). Checks: `v2check/run_adv.py` (every reviewer triple, reference = `v2check/oldref.py`, a fresh
subprocess per mutant sharing no code with mutlib), `v2check/static_checks.py`, `v2check/runtime_memo_checks.py`,
`v2check/run_syn2.py` (synthetic triples in `v2check/syn2/`), `v2check/compare_v1.py`, `v2check/memo_mutants_v2.py`.
Their outputs are in `v2check/out/`.

| hole | what went wrong in v1 | v2 fix | verified by |
|---|---|---|---|
| adv 1 (A, A2), r2 MAJOR-2 | hoisted checks ran before fixture code changed the scorer module (`setattr`, a helper) | **hoisting removed**: every check runs where the original runs it (V: module-level guards in suite order; N: the original final loop) | run_adv A, A2, S_setattr: `lax`, `THRESH_2` SURVIVE as in the old harness |
| adv 2 (B) | a mutant read a file that later fixture code wrote | hoisting removed | run_adv B: `min10` SURVIVES |
| adv 3 (H) | hidden state (`lru_cache`) made the final-loop re-check differ | hoisting removed (one pass, as the original) | run_adv H: `nocopy` SURVIVES |
| r2 MAJOR-1 | a name bound after its `case()` raised `NameError` when hoisted | hoisting removed | run_adv S_late: `MODE_b` SURVIVES |
| r2 MINOR-1 | hoisting stayed on with fast mode off | moot (no hoisting) | run_adv S_okfalse: fast OFF, `MODE_b` SURVIVES |
| adv 6 (J, G) | jobs shared a worker process: a logging file handle blocked the next job's `rmtree` (crash counted as a kill), a helper module's cache leaked between jobs | **one fresh spawned process per job** (baseline, controls, mutants), never reused; each job gets its own new directory `work/<run>/jNNNNN/{fx,m}`, removed by the parent after the process has exited | run_adv J: `ge_equiv`, `log_text` SURVIVE; G: both KILLED, as the old harness |
| adv 6 (confirmation) | an environment crash counted as a kill | a crash raised **outside the scorer file**, or a job process that died, is **rerun once in a fresh process**; it counts only if the rerun kills too, otherwise UNRESOLVED; a failure to prepare the job directory or start the process is UNRESOLVED (environment), never KILLED; an exception raised in mutlib's own code is a HARNESS ERROR, not a kill | run_syn2 S1 (`nokey` KeyError in the test, `die` os._exit: both KILLED after a confirming rerun), S2 (`flaky`: first run crashes in the test, the rerun survives → UNRESOLVED, exit 2) |
| adv 7 (L) | parallel jobs shared every path outside BASE | the whole baseline runs under an audit hook (writes, creates, removes, renames/replaces, copies, links, process spawns); any path outside the job directory (BASE and the mutant's own directory, both private to the job; tempfile paths are private too) → **`--workers` forced to 1, said in the header**. The baseline runs alone, before anything else. Beyond the decision: any control / mutant that writes outside its directory while other jobs run makes every job that overlapped it in time be **rerun alone** | run_adv L4 ×3: `workers: FORCED TO 1`, `tag2`, `tag3` SURVIVE in every repetition; run_syn2 S4 (`rerun alone: 4 jobs`) |
| adv 4 (C), r2 MINOR-2 (P2a, P3a, P3b) | the memo's deny-list purity check let `read_run` change its parameters, aliases, module objects (also through a module-level lambda); a hit then skipped the change | **allow-list purity** of the whole closure (`read_run`, the module functions and **lambdas** it reaches): only locals, statically bound module names and allowed builtins may be read; only allowed builtins, closure functions, local nested functions and functions of an allow-list of pure stdlib modules may be called; a value is either owned by the call or foreign (module data, `read_run`'s parameters, anything reached from them), and only owned values may be changed; a helper may change its parameter only if every call site passes an owned value; mutable default arguments, function attributes, dunder / private attributes, classes, generators, `global`, imports and IO other than reading a file parameter are refused | static_checks P2a, P2b, P3a, P3b, P3c (`list.append(SEEN, 1)`), P3d (mutable default), P3e (own parameter) all OFF; P3f / P10 (a helper filling an owned dict, the net112 pattern) ON; sc_c OFF → run_adv C1, C4 ×3: `ge_equiv` SURVIVES |
| adv 4 (runtime guard) | — | **runtime guard on every cache miss**: the canonical form of every argument and every data dependency before and after the call must be equal, and the result must not share a mutable object with them; otherwise the job ends with a memo violation, **the memo is off for the rest of the run and the job is rerun without it** (said in the header) | runtime_memo_checks R1 (module data changed through an owned list), R2 (argument changed through an alias), R3 (result shares module data); run_syn2 S3 (`grow`: `memo: DISABLED at run time after grow`, rerun without the memo, KILLED as in the old harness) |
| r2 MINOR-2 (P4a, P4b) | `zipfile` / `configparser` reads of other files passed the deny-list | allow-list of modules (`re`, `math`, `statistics`, `struct`, `json`, `collections`, `itertools`, `functools`, `operator`, `bisect`, `heapq`, `string`, `hashlib`, `binascii`, `zlib`, `base64`, `unicodedata`, `copy`, `fractions`) and builtins | static_checks P4a, P4b OFF |
| r2 MINOR-3 (P5) | a top-level statement that binds nothing (`limit.k = 3`) was outside the dependency hash | function attributes are refused; **every top-level statement that stores into, mutates or passes a dependency is hashed** with the closure | static_checks P5 OFF; P5b (`SEEN[0] = 3 → 4`): hash moves |
| r2 MINOR-3 (P6), adv 8 (D) | names reached by reflection (`getattr(THIS, 'K')`, `globals()`-generated regexes) were outside the closure | the memo is refused **module-wide** for `globals` / `vars` / `locals` / `exec` / `eval` / `__import__` / `import *` / `sys.modules` / `.__dict__`; the closure may only read names that a statement binds or allowed builtins; at install the memo is refused when the module dict holds names no statement binds | static_checks P1, P6, P9 OFF; sc_d OFF → run_adv D: `row_re` KILLED as in the old harness; runtime_memo_checks R5 (a name created by a walrus in a module-level comprehension: memo off at install) |
| r2 MINOR-3 (builtins) | `mod.open = ...` by a test was invisible to the key | at install and **on every call**: a builtin the closure reads that is shadowed in the module, or replaced in the builtins namespace, bypasses the memo | runtime_memo_checks R4 |
| r2 MINOR-3 (P8) | a directory and a missing file had the same key | a file parameter is keyed by type: absent / directory / file (sha256 of its bytes) / other (mode) | static_checks P8: three different keys |
| adv 5 (E, E2) | extraction silently dropped `MUTANTS.append` in loops, `MUTANTS[0] = ...`, `M['x'] = ...`, `M.update(...)` | **strict extraction**: every mention of the mutant collection anywhere in the script must be a recognised definition (exactly one `MUTANTS = [(name, old, new), ...]` literal, optional re-filters `MUTANTS = [m for m in MUTANTS if ...]`; or exactly one `M = {}` plus `mutant(...)` calls at top level, in plain `for` / `if` blocks) or a read-only use (iteration, `len`, `list`, `.items()`, subscripts, `in`, ...); anything else refuses the run; `mutant()` may not be called inside a function or after the harness part; the definitions may not read `sys.argv` / the environment; a statement that is not evaluated may not use a mutable value the definitions read; **the verdict line carries the mutant count** | run_adv E, E2: REFUSED (exit 3) instead of ALL KILLED; static_checks: the six real scripts give v1's lists exactly (277, 310, 41, 43, 36, 24) |
| adv 9 (F) | exit 0 in mid-suite counted as SURVIVED unless the success line was exactly `ALL OK` | **success = exit 0 AND an ALL OK line (a line starting with the words `ALL OK`) AND the end of the suite reached** (a marker wraps the final `sys.exit(...)` argument, or follows the last statement); N family: the old substring rule too; the baseline must satisfy it or the run is refused | run_adv F: `version_always` KILLED as in the old N harness; K: see differences |
| adv INFO 11 (I) | old child processes printed through a cp1250 pipe and crashed on U+2265 | **noted, not emulated**: a line the old console encoding cannot encode gets a note on the mutant line and a `NOTE:` summary line; `sys.stdout.buffer` now exists (v1 had none: `AttributeError` would have been a false kill) | run_adv I: `detail_sym` SURVIVED with the note (the one documented difference); run_syn2 S1 `buffer` SURVIVES |
| r2 MINOR-4 | the V-family kill label could come from any line printed since the previous guard | each guard's orientation is decided statically (its case line printed **before** it or by the **next** statement); the label comes only from the most recent line or the next line | compare_v1: every verdict and kill label on check112 / vdg112 / vbn113b / vbn113c equals v1's (156 rows: 144 mutants, 12 controls) |
| adv INFO 12 | `Pool.close` waited 20 s for a starting worker | no idle workers exist (a process per job) | run_adv I: wall 0.3 s |
| (found while building v2) | the early exit and the `failures` rule trusted the static analysis that the final exit follows `ok` | the baseline evaluates the final exit expression with `ok=False` (only plain expressions qualify); if that is not a non-zero exit, **fast mode is switched off** and recorded guard failures are no longer a verdict | run_syn2 S5 (`sys.exit(0 if ok or True else 1)`: fast DISABLED, both mutants SURVIVE as in the old harness) |
| (found while building v2) | the report itself crashed when a label or note held a character the console cannot encode | stdout / stderr of the harness use `backslashreplace`; notes are ASCII | run_adv I |

**Differences from the old harnesses that remain on purpose (both are the better verdict):**

* **Stricter than the old V rule** (adv INFO 10, run_adv K): an exit 0 without an ALL OK line, or before the end of
  the suite, is KILLED; the old V harness looked only at the exit code.
* **Console encoding** (adv INFO 11, run_adv I): a mutant that only prints a character cp1250 cannot encode survives in
  mutlib and carries a note; the old harness crashed and called it killed.

## How it works (v2)

1. **Mutant extraction (the mutant script is never run).** The script is parsed with `ast`. The statements before the
   harness part are candidates: that part starts at the first `def run` / `lane` / `main` / `worker`, the first loop
   over the collection, or a `try` / `while` / `with` / `__main__` block. mutlib evaluates only the statements that
   define mutants, the assignments and helper definitions they read (a transitive closure), and imports. `mutant()`
   is replaced by a stub that fills an ordered dict and refuses duplicates; the original helper must be plain
   "assert + `M[name] = (old, new)`". Before evaluating anything, the strict check above walks every node of the
   script. Every anchor must occur exactly once in `--scorer` and differ from its replacement, otherwise the run is
   refused.
2. **Execution: one fresh process per job.** The baseline runs first and alone; then controls and mutants run with
   `--workers` processes at a time. Each job is a new `spawn`-ed process that:
   * creates its own directory `work/<run>/jNNNNN/` (never reused) and writes the mutant scorer to `m/<scorer name>`
     (`sys.dont_write_bytecode` is set, so no `.pyc` can be picked up);
   * `exec`s the transformed suite in a fresh globals dict with `__name__ == '__main__'` and
     `sys.argv = [test, mutant(, fx dir when the suite reads argv[2])]`, capturing stdout and stderr;
   * sends its result to the parent and exits with `os._exit` (no interpreter state survives a job).

   The parent removes the job directory after the process has exited. A job over `--timeout` is killed and reported
   **TIMEOUT (unresolved, never killed)**. The default timeout is max(120 s, 3 × the baseline, 3 × the baseline's
   estimated time without memo hits).
3. **Suite transformation (AST, in memory).**
   * **Fixture directory:** the single top-level `BASE = Path(...)` points at the job's `fx` directory.
   * **Guards:** every `ok &= X` and `ok = ok and X` on the module's `ok` becomes `ok &= _mutlib_guard(X, ...)`
     (module level, loops, and functions that declare `global ok`; a function's local `ok` is not touched). The guard
     returns X unchanged and records a falsy X with the failing case's name.
   * **End marker:** the argument of the final `sys.exit(...)` / `raise SystemExit(...)` is wrapped in
     `_mutlib_end(...)` (descending into a final `if __name__ == '__main__':`); otherwise the marker follows the last
     statement. A suite exit before it is "before the end of the suite".
   * **Fast mode (early exit)**, only where it is exact: `ok` is initialised once to `True` and only ever updated by
     `&=` / `ok and`; the suite ends with `sys.exit(<plain expression of ok>)`; there is no other exit and no
     reflection in the suite; **and** the baseline confirms that the exit expression with `ok=False` is non-zero. Then
     a falsy guard **at module level** ends the job at once (V family: in suite order; N family: in the original
     final loop, labelled `c['name']`); a guard inside a function only records. Otherwise every suite runs to its end
     and recorded failures only name the case.
   * **Case names (V family):** a guard whose case line is printed before it takes the name from the most recent line
     (first token of a line with a `FAIL` token); a guard followed by its print takes it from the next line.
4. **Parse memo (`read_run`).**
   * **When it is on:** for scorers with a top-level `read_run` whose closure passes the allow-list purity check and
     whose module uses no reflection. The test's `importlib.util.spec_from_file_location` is wrapped, so `exec_module`
     of the mutant path installs the memo wrapper on `module.read_run` (refused at install when the module holds names
     no statement binds, a closure builtin is shadowed, or a dependency is a module / callable outside the
     allow-list).
   * **Memo key:** the dependency hash (sha256 of the source and AST of `read_run`, of every top-level binding it
     reads, transitively, and of every top-level statement that stores into, mutates or passes one of them, in this
     mutant's source, plus the harness version), the canonical values of the data dependencies, the type and bytes of
     every file parameter, and the canonical form of the other arguments. A rebound or modified function / module
     dependency, a shadowed or replaced builtin, or a value without a canonical form bypasses the memo for that call.
   * **Runtime guard on misses:** see the table (arguments and data dependencies unchanged, result shares nothing).
   * **Storage:** pickled values in a per-job LRU (`--memo-mem-mb`, 256 MB) and on disk in
     `cache/<scorer stem>/<key>.pkl` (magic `MUTLIBM2`, payload sha256, atomic replace). Only entries of the
     unmutated dependency hash go to disk, shared by all jobs and later runs; every disk entry was produced by a
     guarded miss. v1's entries are never read (the harness version is part of the hash).
   * **Fresh copies:** every call, hit or miss, returns a fresh `pickle.loads` copy.
5. **Verdict.** A mutant survives only if its suite exits 0, reaches its end, prints an ALL OK line (N family: `ALL
   OK` in the output as well), does not print `FIXTURE FAILURES`, and — when fast mode is sound — no guard failed. A
   crash in the scorer file kills; a crash elsewhere or a dead process kills only if a rerun in a fresh process kills
   too.
6. **Controls (`--control`):** a comment line after the docstring, `pass` at the end of `read_run` (a different
   dependency hash, so the uncached path runs; `evaluate` when there is no memo), and `pass` at module level at the
   end of the file. A control that does not survive means the harness or the suite is nondeterministic, and the exit
   code is 2.
7. **`--changed-from PARENT`** runs every mutant whose anchor overlaps a line that `difflib` finds changed between
   PARENT and `--scorer`, plus a reproducible sample of the rest (`--sample`, 0.2 by default, seeded by the first 16
   hex digits of the scorer sha256 unless `--seed` is given).

## Residual assumptions (stated, not hidden)

* The suite runs as `__main__` in its own globals dict; `sys.modules['__main__']` is the job process's main module,
  not the suite. A suite that reaches its own `__main__` module object through `sys.modules` would see a difference.
* Writes are audited through Python's audit events (`open` for writing, `os.remove` / `rename` / `mkdir` / `rmdir`,
  `shutil.*`, links, `chmod` / `utime`, process spawns). A write by native code that raises no audit event is not
  seen. Process spawns force `--workers 1` because their writes cannot be audited.
* The memo's static purity check is conservative but not complete: aliasing into module data or arguments through an
  owned container is allowed statically and caught only by the runtime guard on a miss. Every value served from the
  cache was produced by a miss that passed the guard, and a miss that fails it is never stored.
* When the memo goes off at run time, jobs that finished before keep their results (each of their hits was produced
  by a guarded miss with the same key); every later job and the violating job run without the memo.
* Set iteration order in memoised values follows pickle reconstruction. Across processes this was already not stable
  in the old harness (string hash randomisation).
* Early exit ends the job at the first failing module-level guard. A suite that would have crashed or hung later is
  killed at that guard; the old harness would have killed it later or hung.
* Disk: without hoisting every N-family job writes all its fixtures before the final loop (about 2 GB for net112), so
  28 concurrent jobs need about 56 GB of scratch space at peak.

## Validation of v2 (2026-09-24, before acceptance on the N suites)

* **Small V suites** (`v2check/out/<suite>.report.txt`, all with `--control`, 27–28 processes, one suite at a time):

  | suite | mutants | v2 verdicts | same verdict and kill label as v1 (rows incl. controls) | v2 wall | v1 wall |
  |---|---|---|---|---|---|
  | check112 | 24 | 24 killed, controls 3/3 | 27 / 27 rows | 3.0 s | 2.9 s |
  | vdg112 | 36 | 36 killed, controls 3/3 | 39 / 39 | 18.5 s | 13.3 s |
  | vbn113b (sealed) | 41 | 41 killed, controls 3/3 | 44 / 44 | 26.3 s | 19.1 s |
  | vbn113c (sealed) | 43 | 42 killed, `bad_race` survives, controls 3/3 | 46 / 46 | 29.8 s | 20.9 s |

  The wall time grows by about one baseline (0.8 / 7.1 / 10.1 / 11.0 s), because the baseline now runs alone before
  anything else; the worker time is the same or lower (13.7 / 229.1 / 345.3 / 415.3 s against 19.0 / 238.2 / 365.0 /
  438.1 s). No baseline wrote outside its directory, so no run was forced to one worker.
* **Reviewer counter-examples** (`v2check/out/adv_compare.txt`): 19 configurations, 23 runs including the
  repetitions: all agree with the old method except the two differences above; E and E2 are refused.
* **Mechanisms** (`v2check/out/syn2_compare.txt`): S1–S6 as in the table.
* **Static and runtime memo checks:** `static_checks.py` 0 failures (includes the six real mutant scripts, the six
  real suite plans with fast mode on, and the net112 / shn113 memo plans ON with v1's dependency set);
  `runtime_memo_checks.py` 0 failures; `memo_mutants_v2.py`: 25 / 277 (net112) and 36 / 310 (shn113) mutants touch
  the closure and every one moves the hash; none turns the memo off.
* **net112 smoke run** (`v2check/out/net112_smoke.*`, final sha, `--only S1_off,FATAL_stdout_unscanned --workers 2
  --control`): baseline 89.6 s on a warm v2 cache (215.7 s on the first, cold run: 132 guarded misses, no violation);
  the three controls SURVIVE, including `CONTROL_pass_end_of_read_run` (every parse a guarded miss, 203.5 s);
  `S1_off` KILLED by `S1_S2_positive`, `FATAL_stdout_unscanned` KILLED by `FATAL_so0`, the same cases as v1; no
  forced workers; wall 6 min 23 s. Without hoisting `S1_off` takes 31 s instead of v1's 4 s (all fixtures are written
  before the final loop).
* **Acceptance of ROADMAP item 13: done, PASS** (`ACCEPTANCE_V2.md`, `accept2/`, same sha): every reviewer
  counter-example gives the old verdict except E / E2 (refused), K (stricter) and I (encoding noted), as decided;
  net112 277 / 277 and shn113 310 / 310 killed, each naming the earliest old failing case; the V suites as above;
  all controls survived. Walls: net112 1268 s (2007 s with `--no-memo`), shn113 2063 s (cold cache).

## v1 history

v1 validation (reference comparison on the V suites, net112 277 / 277 and shn113 310 / 310 first failing cases, the
timings with hoisting) is in `ACCEPTANCE.md`. v1 hoisted each N-family check to the moment its `case()` registered
it; the acceptance measured that this gave no wall-time gain worth its risk (net112, 20 mutants: 170 s with, 147 s
without), and the reviews showed five ways it could give a false kill, so v2 removed it. (Correction from
`ACCEPTANCE_V2.md` §3: that subset's wall was bounded by the baseline; on the full runs removing hoisting costs about
1.7× in mutant time and wall — net112 1268 s against 778 s, shn113 2063 s against 1186 s.)

| suite | mutants (+3 controls) | old harness | v1 wall |
|---|---|---|---|
| check112 | 24 | serial, 24 × 0.8 s ≈ 19 s | 2.9 s |
| vdg112 | 36 | serial, 36 × 7.2 s ≈ 4.3 min | 15.6 s |
| vbn113b | 41 | serial, 41 × 10.3 s ≈ 7.0 min | 20.9 s |
| vbn113c | 43 | never run (≈ 8.0 min) | 23.5 s |
| net112 | 277 | ≈ 1 h 45 min | 795 s (13.3 min) |
| shn113 | 310 | ≈ 3 h | 1186 s (19.8 min), cold cache |

## Files

* `mutlib.py`: the harness (v2). `mutlib_v1.py`: v1, unchanged (sha256 `db8703bd…`).
* `cache/<scorer stem>/`: the shared parse memo and `durations.json`. It can be deleted at any time. v1 and v2
  entries live side by side (different hashes and magic).
* `work/`: per-run scratch (`<stem>_<pid>_<time>/jNNNNN/{fx,m}`), removed at the end unless `--keep-work` is given.
* `v2check/`: the v2 self-checks listed above and their outputs (`out/`).
* `adversarial/`, `review2/`, `REVIEW_*.md`: the two reviews of v1 (not edited).

## Changelog

* 2026-09-24, v1 acceptance (`ACCEPTANCE.md`, `accept/`): net112 277/277 and shn113 310/310 killed, each naming the
  earliest old failing case; vbn113b 41/41, vdg112 36/36, check112 24/24 killed; all controls survived; vbn113c 42/43
  (`bad_race`, a real gap in the suite). mutlib.py v1 sha256
  `db8703bdf0820c9023e9f1a9d69ddfae6fddc00b8035d0294704b85115de00fb`.
* 2026-09-24, **v2** (ROADMAP §0.1 session 113 item 13): hoisting removed; one fresh process per job; crash / death
  confirmation; environment failures unresolved; baseline write audit forcing one worker; strict extraction with the
  count in the verdict line; success = exit 0 + ALL OK line + end of suite; allow-list memo purity with a runtime
  guard; exit probe for fast mode; kill labels from the most recent / next line only; console encoding noted.
  mutlib.py v2 sha256 `877eb53a9d939293308fd4bcbce2764606f42a9c1f0d6df4282923db529a6108` (the file every check in
  `v2check/out/` ran against).
* 2026-09-24, v2 acceptance (`ACCEPTANCE_V2.md`, `accept2/`): all checks passed on the first try, mutlib.py unchanged
  (sha256 `877eb53a…`). Reviewer triples via the reviewer's `oldstyle.py`: 44 / 46 verdicts equal, K and I differ as
  decided, E / E2 refused; net112 277/277 (also with `--no-memo`) and shn113 310/310 killed with 277/277 and 310/310
  earliest old failing cases; vbn113b 41/41, vdg112 36/36, check112 24/24; vbn113c 42/43 (`bad_race`, report
  `mut_vbn113c_v2.out.txt`); all controls survived.
