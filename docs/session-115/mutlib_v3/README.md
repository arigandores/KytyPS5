# mutlib — fast, strict, shared mutation harness (v3)

`mutlib.py` replaces the per-session `mut_*.py` run loops. Those loops started a fresh `python test_X.py <mutant>`
subprocess per mutant and ran the whole fixture suite every time, which took 1.5 to 3 hours per N-family scorer.
mutlib reads the same mutant lists and runs the same fixture suites, but it never edits them: the mutant scorer
goes to a scratch directory, and the suite is transformed in memory.

**v3 is current.** v2 (sha256 `877eb53a…`, accepted in `ACCEPTANCE_V2.md`) is kept byte-identical as
`mutlib_v2.py`; v1 (sha256 `db8703bd…`) as `mutlib_v1.py`. The third adversarial review (`review3/`: triples T1–T7,
evidence in `review3/out/`) found two MAJOR and six MINOR holes in v2, and session 113 asked for a draft-only marker
(item 20). The section **v3: what changed and why, per hole** maps each of them to its fix and to the check that
shows it closed; the v2 and v1 sections below are kept as history.

```
python mutlib.py --scorer S --test T --mutants M [--workers N] [--no-memo] [--no-fast]
                 [--only a,b] [--changed-from PARENT_SCORER --sample 0.2 --seed N] [--control]
                 [--timeout SEC] [--out FILE]
```

The CLI and the report format are v2's. Examples (run from `C:/kyty/s106_stage/mutlib`):

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
  * 3: refused. Possible causes: `C:/kyty/SEALED_RUN.lock` exists, a bad anchor (an absent anchor refuses unless the
    mutant is marked draft-only), a mutant script shape the strict extraction does not recognise (including, since
    v3, a second collection of (name, old, new) tuples, a text substitution in the harness part whose old / new text
    does not come from the recognised collection, a filter in front of it that mutlib cannot evaluate, a bad
    draft-only marker), an unsupported suite shape, or the unmutated scorer fails its own suite.
* **Report:** the header gives the sha256 of the harness, scorer, test and mutant script, the format, what the
  harness part of the mutant script does (v3), the draft-only marks (v3), the family, the memo decision (v3: how file
  arguments are keyed) and the selection, then the decisions taken after the baseline (fast mode confirmed or
  disabled, workers forced to 1, memo disabled). Then one line per mutant: `<name>  KILLED by <first failing case>
  (s)`, `KILLED (crash: ...)`, `KILLED by exit N`, `KILLED (exit 0 before the end of the suite)`, `SURVIVED`,
  `TIMEOUT ...`, `UNRESOLVED (...)`, `HARNESS ERROR (...)` or (v3) `SKIPPED (draft-only: ...)` / `SKIPPED (the
  mutant script's own filter skips it: ...)`, with notes in brackets (rerun to confirm, rerun without the memo, rerun
  alone, console-encoding note). Totals follow, then the verdict line **with the mutant count**: `ALL KILLED (43 of 43
  selected mutants killed; 43 defined in the mutant script)`, `SURVIVORS: [...] (...)` or `NOT CERTIFIED (...)
  (...)`; when mutants were skipped the count says so: `(315 of 315 selected mutants killed; 317 defined in the
  mutant script, 2 skipped as draft-only)`, `(..., 1 skipped by the mutant script's own filter)`. Progress lines go to
  stderr as they finish. `--out` writes the ordered report to a file.
* **Never run it during a sealed run.** It refuses while `C:/kyty/SEALED_RUN.lock` exists, and by default it
  uses cpu_count − 4 = 28 processes at a time.
* **`--dry-run`** prints the header and the selection (and the skipped mutants), then exits without running anything.
* **Dispatch order:** the slowest mutants of the previous run go first, new ones before them, so the run does not
  end on a long tail. The timings come from `cache/<stem>/durations.json`. The report always keeps definition order.

### Marking a draft-only mutant (session 113 item 20)

A mutant whose anchor exists only in an unfilled seal (for example `PRED_SHA = None`) makes the run on the SEALED
scorer refuse, because its anchor is absent. Mark it, in the mutant script, in either way:

```
mutant('CONST_pred_sha_prefilled', "PRED_SHA = None          #", "PRED_SHA = '0' * 64     #")  # mutlib: draft-only
    ('sha_prefilled', 'PRED_SHA = None', "PRED_SHA = '0' * 64"),  # mutlib: draft-only        (list format)
DRAFT_ONLY = ['CONST_pred_sha_prefilled', 'CONST_pred_bytes_prefilled']                      (a top-level literal)
```

The marker is a comment that STARTS with `mutlib: draft-only`, on a line of that mutant's definition (a comment that
only mentions the marker is not one). On a scorer where the anchor is absent the mutant is reported `SKIPPED
(draft-only: its anchor is absent from this scorer)`, the header says `draft-only: N mutant(s) marked [...]; M skipped
...` and the verdict line `N defined in the mutant script, M skipped as draft-only`. On the draft (anchor present
once) it runs as usual. What still refuses (exit 3): an unmarked absent anchor (the message suggests the marker), a
marked anchor that occurs more than once, a marker that sits on no mutant definition or on one whose name is not a
string literal, a `DRAFT_ONLY` that is not one top-level literal of defined names. Demonstrated on
`v3check/mut_shn113_marked.py` (a copy of `C:/kyty/s113/mut_shn113.py` with the two markers; the project's scripts
are not edited): on the sealed `C:/kyty/s113/shn113.py` it gives 317 defined, 2 skipped, and the 315 that remain are
exactly the list of `mut_shn113_sealed.py`.

## v3: what changed and why, per hole

Hole ids: `T…` = the review3 triples (`review3/sc_t*`, `test_t*`, `mut_t*`; the reviewer's report and evidence in
`review3/out/`). Checks (all in `v3check/`, outputs in `v3check/out/`): `run_review3_v3.py` (every review3 triple
against its reference: `adversarial/oldstyle.py` unedited, or for T4 the mutant script's own loop),
`run_adv_v3.py` (both v1 reviews' 19 configurations, the runner of the v2 acceptance with outputs redirected),
`run_syn2_v3.py` (v2's mechanism checks S1–S6), `run_syn3.py` (23 new synthetic checks in `v3check/syn3/`, each
against oldstyle.py or the script's own loop), `static_v3.py` (extraction, memo keys and path analysis, the guard,
suite plans, the marker grammar), `rerun_v_suites_v3.py` (the eight small real V suites, row by row against their
accepted v2 reports); v2's own `v2check/static_checks.py` and `runtime_memo_checks.py` unchanged against v3.

| hole | what went wrong in v2 | v3 fix | verified by |
|---|---|---|---|
| **MAJOR-1** (T5, T5b) | the read_run memo keyed a file argument by its type and bytes, not its path, but a result could carry the path (`str(exc)`, `exc.filename`, `fh.name`, `repr(fh)`): a result produced for one path (the baseline's fixture, run.log) was served for another (log.txt, a later job) - false kills and a false survivor | **(1) static path analysis of read_run**: an exception object used other than `.errno` / `.strerror` / `.winerror`, or a file object used other than to read it (`read`, `readline`, `readlines`, `close`, iteration, `iter` / `next` / `list` / `tuple` / `enumerate`), makes the plan **path-sensitive**: its file arguments are keyed by their path (and the argument's type) as well as the file's type and bytes, and its values stay in the job's memory LRU (no shared disk cache). **(2)** a failed `stat` is keyed by the exception type, errno and winerror (v2: one key `absent` for every failure). **(3) runtime backstop** for path-insensitive plans: a value whose pickle contains the file argument's path (as given, absolute, `/` and `\`, repr-escaped, case-insensitive) or its name (3+ characters) is never stored (`path_in_result` in the job's memo stats), so no cached value can carry one path into a call on another | run_review3_v3 T5 (ctl_cold, noctl_warm, noctl_cold, nomemo) and T5b (ctl_cold, nomemo): all agree with oldstyle.py, memo ON, controls 3/3; run_syn3 FH (`fh.name`: keyed by path) and CONST (a constant file name in the result: never stored); static_v3 §2: 12 read_run variants classified as intended, sc_t5 / sc_t5b path-sensitive, net112 / shn113 path-insensitive (their disk cache stays shared), keys: two paths with the same bytes share a key only when insensitive, file / absent / directory / invalid name all differ |
| **MAJOR-2** (T4a, T4b) | strict extraction checked only the one collection name: a second list of (name, old, new) tuples with its own loop (T4a), or a loop over `list(M.items()) + LATE` (T4b), ran mutants mutlib never saw - `ge_equiv` survived in the old method, mutlib said ALL KILLED | **harness-part check** (`_HarnessCheck`): **(1)** a (name, old, new)-shaped tuple, a (name, (old, new)) pair or a dict name -> (old, new) anywhere outside the recognised definitions refuses (a tuple of mutant NAMES is allowed); **(2)** every `.replace(A, B)` / `str.replace(S, A, B)` outside the definitions must take (A, B) = (old, new) of ONE element of the recognised collection - a loop over the collection or a read-only view of it (`list`, `tuple`, `sorted`, `reversed`, `iter`, `enumerate`, `.items()` / `.values()` / `.keys()`), `M[k]`, `M.get(k)`, unpacking, an element's `[1]` / `[1:]`, or a helper parameter whose every call site passes such values; a name that holds a view counts only if every later use of it is read-only; a slice of the collection does not count; a replacement of constants refuses when its old text occurs in the scorer; `.sub` / `.subn` with non-constant arguments refuse. The verdict line keeps `N defined` | run_review3_v3 T4a, T4b: REFUSED (exit 3); run_syn3 M4_zip and M4_concat (the second list built without a literal and appended to a copy of MUTANTS: v2 silently extracted 2 of 3 there), M4_slice, M4_hardcoded, M4_helper_extra: REFUSED; M4_helper_ok, M4_items_ok, M4_filter_count: accepted, same verdicts as the scripts' own loops; static_v3 §1 and the scan of every project mutant script: the accepted ones give v2's lists exactly |
| MINOR 1 (T2) | the exit probe evaluated the final exit with ok=False only once, on the baseline; `sys.exit(0 if ok or DRAFT else 1)` with a mutant that makes DRAFT true exits 0 on failures, yet the early exit killed it | fast mode (early exit) only when the final exit expression reads **no name but the pass flag**; otherwise every suite runs to its end | run_review3_v3 T2 (ctl and nofast): `unsealed` SURVIVED as in the old method; static_v3 §4 |
| MINOR 2 (T3) | the guard looked only at the truth of the value; `ok &= None` raises TypeError in the suite (swallowed by its handler, the suite goes on and passes), but the guard had already recorded a failure and exited early | the guard gets the current ok (loaded first, as the statement loads it) and computes `ok & value` (or `value` for `ok = ok and value`) itself; a failure is recorded only when the value and that result are falsy AND computing them did not raise; it is EXACT (may end the job early, may name a kill) only when ok and the value are plain bool / int; a recorded failure names a kill only when the suite's exit code is non-zero (v2: any recorded failure was a kill) | run_review3_v3 T3 (ctl and nofast): `no_return` SURVIVED as in the old method; static_v3 §3 (None, False, 0, 2, [], a value whose bool() raises, a guard in a function) |
| MINOR 3 (T1v, T1n) | success needed a line STARTING with `ALL OK`; a scorer report written without its final newline glued the success line to it | success = exit 0 AND `ALL OK` anywhere in stdout + stderr (the old N rule) AND the end of the suite reached AND no `FIXTURE FAILURES` line | run_review3_v3 T1v, T1n: `no_trailing_nl` SURVIVED as in the old method |
| MINOR 4 (T7) | the capture stream had no `fileno()` (also no `writelines`, `closed`, `name`); `faulthandler.enable(file=sys.stderr)` crashed and counted as a kill | **the job's stdout / stderr are real files** in the job directory (`cap/stdout.txt`, `cap/stderr.txt`, utf-8, surrogatepass), and **fds 1 / 2 point at them** during the job, as the old harness's pipes were the child's fds 1 / 2: every file attribute exists, `os.write(1, ...)`, `faulthandler` with or without a file, `sys.__stdout__` and a wrapper around `sys.stdout.buffer` land in the captured output. The runtime reads the files back as lines at its hooks: every guard, the end marker, the end of the job, and `_mutlib_after()`, inserted after every printing / writing statement of the suite (it resolves a failed guard whose case line is printed after it, exactly where v2's Python stream did) | run_review3_v3 T7: `trace_on` SURVIVED; run_syn3 CAP (nine stream APIs, all SURVIVE as in the old method) and CAPFD (the success line written with `os.write(1, ...)`) |
| MINOR 5 (T6) | the suite ran 7 frames deeper than under `python test.py`, so a recursion that fitted the old limit hit RecursionError (a false kill) | the recursion limit is raised by the frames below the suite's module frame plus a margin for harness frames that can sit above a scorer frame (16: the audit hook; 64 with the memo: its wrapper and key); `sys.getrecursionlimit()` / `sys.setrecursionlimit()` show and take the values the suite would see; printing no longer runs Python code at all (real files) | run_review3_v3 T6: `lambda_wrap` SURVIVED; run_syn3 DEEP: +1 frame survives, 40 levels past the old limit killed as in the old method; 10 levels past it is the documented residual (below) |
| MINOR 6 (T4c) | a filter in the mutant script's own loop (`if name in KNOWN_EQUIVALENT: continue`) was ignored: the mutant ran and survived (a false survivor) | every condition in front of an accepted substitution (an enclosing `if`, an earlier `if ...: continue / return`) is **evaluated per mutant**: comparisons of the mutant's name / old / new with literals and with top-level literal collections (only read elsewhere), `startswith` / `endswith`, `len`, and anchor checks `X.count(old)` on the scorer text. A mutant it skips is reported `SKIPPED (the mutant script's own filter skips it: line N: ...)` and counted in the verdict line; a condition mutlib cannot evaluate, a `break` that is taken (it would skip every later mutant) or a `raise` that fires refuses (the message says to use a re-filter or DRAFT_ONLY) | run_review3_v3 T4c: `ge_equiv` SKIPPED, ALL KILLED as the old method; run_syn3 M4_filter_list (SKIPPED), M4_filter_count (the usual anchor check: nothing skipped), M4_filter_env and M4_filter_break (REFUSED) |
| **NEW** (session 113 item 20) | a mutant anchored on the unfilled seal (`PRED_SHA = None`) refused the whole run on the sealed scorer, so session 113 ran a derived `mut_shn113_sealed.py` | the draft-only marker (above): a marked mutant whose anchor is absent is SKIPPED, counted in the header and the verdict line; an unmarked absent anchor still refuses | run_syn3 DRAFT_* (7 runs: list / calls / DRAFT_ONLY on the sealed scorer, the draft scorer against the old method, unmarked, stray and ambiguous markers); the real case: `v3check/mut_shn113_marked.py` on the sealed shn113 (dry run and N smoke run, below) |
| (found while building v3) | - | a `break` filter skips every later mutant, so it is accepted only if never taken; a name holding a view of the collection that is changed later (`ALL = list(MUTANTS); ALL.extend(EXTRA)`) passed v2 and the first v3 draft, now it does not count as the collection; old and new taken from two different elements (a cross product of two loops) passed the first v3 draft, now every accepted substitution must take both from the same element (the same unpacking statement, the same element variable, or helper parameters whose every call site passes one element); `os.replace(src, dst)` is a file move, not a substitution; fds 1 / 2 redirected (not only `sys.stdout`); the marker must START the comment (a comment that mentioned it was taken for a stray marker) | run_syn3 M4_filter_break, M4_zip, M4_concat, CAPFD; static_v3 §1 shapes (cross product, `os.replace`); the marked shn113 copy's header comment |

**Speed (secondary):** the suite is transformed and compiled ONCE in the parent (`BASE` now reads the job's fixture
directory from the job's globals, so one code object serves every job) and sent to every job as a marshalled code
object: a job no longer parses, transforms and compiles the suite twice (about 0.24 s per job on the N suites, 0.02
s on check112). Nothing else changed: still one fresh spawned process per job; a pre-forked pool was not added
(process start is about 0.05 s against 0.8–100 s per job, not worth its risk). Measured timings: *Validation of v3*.

**Differences from the old harnesses that remain on purpose:**

* **Stricter than the old V rule** (adv INFO 10, run_adv K, unchanged from v2): an exit 0 without `ALL OK`, or before
  the end of the suite, is KILLED; the old V harness looked only at the exit code.
* **Console encoding** (adv INFO 11, run_adv I, unchanged from v2): a mutant that only prints a character cp1250
  cannot encode survives in mutlib and carries a note; the old harness crashed and called it killed.
* **Refused mutant scripts** (E, E2 from v2; T4a, T4b and the M4 variants above from v3): where the old method ran
  mutants that mutlib cannot see from the recognised collection, mutlib refuses instead of guessing.
* **Recursion window** (run_syn3 DEEP `deeper10`): a scorer whose recursion ends between the old harness's limit and
  that limit plus the margin (16 frames, 64 with the memo) survives in mutlib where the old harness crashed it. This is
  a possible false SURVIVOR (more work for the reviewer), never a false kill: any RecursionError mutlib sees would have
  happened in the old harness too.

## How it works (v3)

1. **Mutant extraction (the mutant script is never run).** The script is parsed with `ast`. The statements before the
   harness part are candidates: that part starts at the first `def run` / `lane` / `main` / `worker`, the first loop
   over the collection, or a `try` / `while` / `with` / `__main__` block. mutlib evaluates only the statements that
   define mutants, the assignments and helper definitions they read (a transitive closure), and imports. `mutant()`
   is replaced by a stub that fills an ordered dict and refuses duplicates; the original helper must be plain
   "assert + `M[name] = (old, new)`". Before evaluating anything, the strict check (v2) walks every node of the
   script. After evaluating, the **harness-part check** (v3) reads the rest of the script statically: no second
   collection of mutant-shaped values; every text substitution draws (old, new) from one element of the recognised
   collection (a role analysis over names, loops, unpacking, subscripts and helper parameters, with Python's scoping);
   every filter in front of a substitution is evaluated per mutant (skipped mutants are reported SKIPPED) or the run
   refuses. Draft-only markers are read from the comments (`tokenize`) and from a `DRAFT_ONLY` literal. Every anchor
   must occur exactly once in `--scorer` and differ from its replacement (a marked draft-only mutant whose anchor is
   absent is skipped), otherwise the run is refused.
2. **Execution: one fresh process per job.** The baseline runs first and alone; then controls and mutants run with
   `--workers` processes at a time. Each job is a new `spawn`-ed process that:
   * creates its own directory `work/<run>/jNNNNN/` (never reused) and writes the mutant scorer to `m/<scorer name>`
     (`sys.dont_write_bytecode` is set, so no `.pyc` can be picked up);
   * opens `cap/stdout.txt` and `cap/stderr.txt` there as its `sys.stdout` / `sys.stderr` and points fds 1 / 2 at them
     for the duration of the suite;
   * raises its recursion limit by the frames below the suite plus the margin (the suite sees its own values);
   * `exec`s the suite's code object (transformed and compiled once by the parent) in a fresh globals dict with
     `__name__ == '__main__'` and `sys.argv = [test, mutant(, fx dir when the suite reads argv[2])]`;
   * reads the output back, sends its result to the parent and exits with `os._exit` (no interpreter state survives a
     job).

   The parent removes the job directory after the process has exited. A job over `--timeout` is killed and reported
   **TIMEOUT (unresolved, never killed)**. The default timeout is max(120 s, 3 × the baseline, 3 × the baseline's
   estimated time without memo hits).
3. **Suite transformation (AST, in memory, once).**
   * **Fixture directory:** the single top-level `BASE = Path(...)` becomes `Path(<the job's fx directory>)`, read
     from the job's globals.
   * **Guards:** every `ok &= X` and `ok = ok and X` on the module's `ok` becomes `ok &= _mutlib_guard(ok, X, ...)`
     (module level, loops, and functions that declare `global ok`; a function's local `ok` is not touched). The guard
     returns X unchanged; it records a failure when X and `ok & X` (or X) are falsy and computing that did not raise,
     EXACT when ok and X are plain bool / int.
   * **Output hooks:** `_mutlib_after()` after every printing / writing expression statement; with a failed guard
     waiting for its case line it reads the new output, names the case and, in fast mode, ends the job there.
   * **End marker:** the argument of the final `sys.exit(...)` / `raise SystemExit(...)` is wrapped in
     `_mutlib_end(...)` (descending into a final `if __name__ == '__main__':`); otherwise the marker follows the last
     statement. A suite exit before it is "before the end of the suite".
   * **Fast mode (early exit)**, only where it is exact: `ok` is initialised once to `True` and only ever updated by
     `&=` / `ok and`; the suite ends with `sys.exit(<plain expression that reads no name but ok>)`; there is no other
     exit and no reflection in the suite; **and** the baseline confirms that the exit expression with `ok=False` is
     non-zero. Then an EXACT failing guard **at module level** ends the job at once (V family: in suite order; N
     family: in the original final loop, labelled `c['name']`); a guard inside a function only records. Otherwise
     every suite runs to its end and recorded failures only name the case.
   * **Case names (V family):** a guard whose case line is printed before it takes the name from the most recent
     stdout line (first token of a line with a `FAIL` token); a guard followed by its print takes it from the next
     line.
4. **Parse memo (`read_run`).**
   * **When it is on:** for scorers with a top-level `read_run` whose closure passes the allow-list purity check and
     whose module uses no reflection (v2). The test's `importlib.util.spec_from_file_location` is wrapped, so
     `exec_module` of the mutant path installs the memo wrapper on `module.read_run` (refused at install when the
     module holds names no statement binds, a closure builtin is shadowed, or a dependency is a module / callable
     outside the allow-list).
   * **Memo key:** the dependency hash (sha256 of the source and AST of `read_run`, of every top-level binding it
     reads, transitively, and of every top-level statement that stores into, mutates or passes one of them, in this
     mutant's source, plus the harness version), the canonical values of the data dependencies, for every file
     parameter its type (a failed stat by its exception type, errno and winerror; a directory; a file by the sha256 of
     its bytes; other by its mode) **and, when the plan is path-sensitive, its path**, and the canonical form of the
     other arguments. A rebound or modified function / module dependency, a shadowed or replaced builtin, or a value
     without a canonical form bypasses the memo for that call.
   * **Runtime guard on misses:** the arguments and data dependencies are unchanged and the result shares nothing
     with them (v2); a path-insensitive value that carries its file argument's path or name is not stored (v3).
   * **Storage:** pickled values in a per-job LRU (`--memo-mem-mb`, 256 MB) and, for the unmutated dependency hash of
     a path-insensitive plan only, on disk in `cache/<scorer stem>/<key>.pkl` (magic `MUTLIBM2`, payload sha256,
     atomic replace), shared by all jobs and later runs; every disk entry was produced by a guarded miss. Entries of
     earlier versions are never read (the harness version is part of the hash).
   * **Fresh copies:** every call, hit or miss, returns a fresh `pickle.loads` copy.
5. **Verdict.** A mutant survives only if its suite exits 0, reaches its end, has `ALL OK` in its output (stdout or
   stderr) and does not print a `FIXTURE FAILURES` line. An early exit at an exact failing guard (fast mode) is a
   kill; otherwise the exit code decides and a recorded exact failure only names the kill (v2 also counted a recorded
   failure as a kill when the suite exited 0). A crash in the scorer file kills; a crash elsewhere or a dead process
   kills only if a rerun in a fresh process kills too.
6. **Controls (`--control`):** a comment line after the docstring, `pass` at the end of `read_run` (a different
   dependency hash, so the uncached path runs; `evaluate` when there is no memo), and `pass` at module level at the
   end of the file. A control that does not survive means the harness or the suite is nondeterministic, and the exit
   code is 2.
7. **`--changed-from PARENT`** runs every mutant whose anchor overlaps a line that `difflib` finds changed between
   PARENT and `--scorer`, plus a reproducible sample of the rest (`--sample`, 0.2 by default, seeded by the first 16
   hex digits of the scorer sha256 unless `--seed` is given). Skipped mutants are never selected.

## Residual assumptions (stated, not hidden)

* The suite runs as `__main__` in its own globals dict; `sys.modules['__main__']` is the job process's main module,
  not the suite. A suite that reaches its own `__main__` module object through `sys.modules` would see a difference.
* Writes are audited through Python's audit events (`open` for writing, `os.remove` / `rename` / `mkdir` / `rmdir`,
  `shutil.*`, links, `chmod` / `utime`, process spawns). A write by native code that raises no audit event is not
  seen. Process spawns force `--workers 1` because their writes cannot be audited.
* The memo's static purity check is conservative but not complete: aliasing into module data or arguments through an
  owned container is allowed statically and caught only by the runtime guard on a miss. Every value served from the
  cache was produced by a miss that passed the guard, and a miss that fails it is never stored.
* **Path (v3):** read_run's result can depend on the text of a file argument only through an exception object or a
  file object (the file parameter itself may only be opened for reading, compared with None or probed with
  `Path(p).is_file()` / `.exists()`); the static analysis follows both (by name, conservatively). The runtime backstop
  finds the path or name only as text; a value that encodes the path otherwise (its length, a hash) is excluded by
  the static analysis alone.
* **Harness part (v3):** mutlib assumes the harness part produces each mutant scorer with `.replace(old, new)`. Text
  edits of another kind (slicing and concatenating the source, writing a hand-edited file) are not recognised as
  substitutions. Which names the harness part passes to a function that applies `M[name]` (for example a job list
  `[n for n in M if ...]`, or a filter in a caller) is not traced: mutlib runs every defined mutant there, so the
  most it can do is report a survivor the old method never ran, never drop a mutant. `X.count(old)` in a filter is
  evaluated on the `--scorer` text.
* **Recursion (v3):** see the recursion window above. Threads started by the suite get the same raised limit.
* **Output (v3):** fds 1 / 2 are redirected with `os.dup2`; a child process started by the suite writes wherever the
  C runtime's standard handles point (spawns force `--workers 1` anyway).
* When the memo goes off at run time, jobs that finished before keep their results (each of their hits was produced
  by a guarded miss with the same key); every later job and the violating job run without the memo.
* Set iteration order in memoised values follows pickle reconstruction. Across processes this was already not stable
  in the old harness (string hash randomisation).
* Early exit ends the job at the first exact failing module-level guard. A suite that would have crashed or hung
  later is killed at that guard; the old harness would have killed it later or hung. Once ok is 0 / False the suite
  keeps it falsy unless a later operand defines `__rand__` returning a true value (not seen in any suite).
* Disk: without hoisting every N-family job writes all its fixtures before the final loop (about 2 GB for net112), so
  28 concurrent jobs need about 56 GB of scratch space at peak.

## Validation of v3 (2026-09-25, before acceptance on the N suites)

All on mutlib.py sha256 `5d2f2f90a28e9f405158d2771898f54850692279c3056f4acf0b6aac3b97537d`, run by
`v3check/chain_v3.sh`, one step at a time (log `v3check/out/chain_v3.log`; `out/` below is `v3check/out/`);
`C:/kyty/SEALED_RUN.lock` absent throughout; no game, emulator or build.

* **review3 triples** (`out/review3_compare.txt`): 17 configurations; 15 agree with the reference (T1v, T1n, T2 ×2,
  T3 ×2, T5 ×4, T5b ×2, T6, T7, T4c), T4a and T4b are REFUSED as decided; every control survived; T5 / T5b with the
  memo ON.
* **Both v1 reviews** (`out/adv_compare_v3.txt`): 19 configurations, 23 runs: identical to the accepted v2 comparison
  apart from timings and hashes (K and I differ from the old method by decision, E / E2 refused, every control
  survived, no drift between repetitions).
* **v2 mechanisms S1–S6** (`out/syn2_compare.txt`): all as v2.
* **v3 mechanisms** (`out/syn3_compare.txt`): 23 checks, 0 BAD (see the table above; the one listed difference from
  the old method, DEEP `deeper10`, is the documented recursion window).
* **Static** (`out/static_v3.txt`): 0 failures, including the harness shapes (element subscripts, starred slices,
  `enumerate` + `os.replace` accepted; reversed old / new, a cross product of two loops, `re.sub` on the source
  refused; a `==` name filter skips its mutant). v2's `static_checks.py` and `runtime_memo_checks.py`, unchanged: 0
  failures each (`out/chain_v2static.txt`, `out/chain_v2runtime.txt`).
* **Every project mutant script** (`C:/kyty/s1*`, `s8*`, `s9*`, 71 files): 44 give exactly v2's list, 27 are refused
  by both versions, none is newly refused or changed.
* **The eight small real V suites** (`out/vsuites/`, `--control`, 28 workers, one suite at a time), compared row by
  row (verdict and kill label, controls included) with their accepted v2 reports (`accept2/`,
  `C:/kyty/s113/mut_*.out.txt`):

  | suite | v3 result | rows identical to the v2 report |
  |---|---|---|
  | check112 | 24 / 24 killed, controls 3 / 3 | 28 / 28 |
  | vdg112 | 36 / 36 killed, controls 3 / 3 | 40 / 40 |
  | vbn113b (sealed) | 41 / 41 killed, controls 3 / 3 | 45 / 45 |
  | vbn113c (sealed) | 42 killed, `bad_race` SURVIVED (the known gap), controls 3 / 3 | 47 / 47 |
  | vbn113d (sealed, `--no-memo`) | 43 / 43 killed, controls 3 / 3 | 47 / 47 |
  | vbn113e (sealed, `--no-memo`) | 51 / 51 killed, controls 3 / 3 | 55 / 55 |
  | vbn113f (sealed, `--no-memo`) | 54 / 54 killed, controls 3 / 3 | 58 / 58 |
  | check113 (sealed, `--no-memo`) | 31 / 31 killed, controls 3 / 3 | 35 / 35 |

* **N smoke test** (sealed `C:/kyty/s113/shn113.py`, `test_shn113.py`, the marked copy
  `v3check/mut_shn113_marked.py`, `--only S1_off,FATAL_stdout_unscanned --control --workers 5`, memo ON):
  exit 0, `ALL KILLED (2 of 2 selected mutants killed; 317 defined in the mutant script, 2 skipped as
  draft-only)`: the header lists the two draft-only mutants as skipped, `S1_off` KILLED by `S1_S2_positive` and
  `FATAL_stdout_unscanned` KILLED by `FATAL_so0` (the labels of the session-113 report), controls 3 / 3 including
  `CONTROL_pass_end_of_read_run` (a memo miss on every parse, 713 s). Baseline 357.7 s on the warm v3 cache (hit_mem
  51, hit_disk 167, no miss); wall 1072.8 s (`out/shn113_sealed_smoke_final.report.txt`). A first run on the
  cold v3 cache (sha `7047b671`, which differs from the final file only in the static harness-part check) gave
  the same verdicts: baseline 511.5 s with 165 guarded misses, none of them a memo violation or a value carrying
  its path (`out/shn113_sealed_smoke_7047b671.*`). The dry run on the final sha (`out/chain_dryrun.txt`) selects
  the 315 mutants of `mut_shn113_sealed.py`.
* **Timings.** During this session the machine was loaded by other programs (a game and a disk-wide `find` started by
  another process), so walls are only comparable when measured side by side. Side by side, same moment, same flags:
  the vbn113f baseline job took 18.3 / 18.5 s under v2 and 18.7 / 18.8 s under v3 (+2 %); the whole vbn113f run
  (`--no-memo --control`, 28 workers) 66.2 s wall / 848 s worker under v2 and 57.0 s / 909 s under v3 (within the
  noise of the loaded machine); check112 (`--control`, alternating v2 / v3 / v2 / v3, `out/ab_check112_*.txt`): 9.2 /
  7.1 s wall under v2, 7.8 / 7.4 s under v3 (worker time 35.4 / 42.6 s against 34.8 / 34.4 s). The runtime path
  backstop costs 32 ms per memo miss on a 7.6 MB shn113 parse value (about 5 s of a 165-miss baseline). The V-suite
  walls of the final chain (10.7 s to 157.6 s) were taken under the heaviest load and are 2–5× the v2 acceptance walls
  for that reason, not a v3 regression; the N suites' 1.7× cost of v2 (no hoisting: every job writes all fixtures) is
  unchanged by v3.

## v2: what changed and why, per hole (history)

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

**Differences from the old harnesses that remained on purpose in v2 (still so in v3):**

* **Stricter than the old V rule** (adv INFO 10, run_adv K): an exit 0 without an ALL OK line, or before the end of
  the suite, is KILLED; the old V harness looked only at the exit code.
* **Console encoding** (adv INFO 11, run_adv I): a mutant that only prints a character cp1250 cannot encode survives in
  mutlib and carries a note; the old harness crashed and called it killed.

## Validation of v2 (history: 2026-09-24, before acceptance on the N suites)

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

* `mutlib.py`: the harness (v3). `mutlib_v2.py`: v2, byte-identical to the accepted file (sha256 `877eb53a…`).
  `mutlib_v1.py`: v1, unchanged (sha256 `db8703bd…`).
* `cache/<scorer stem>/`: the shared parse memo and `durations.json`. It can be deleted at any time. v1, v2 and v3
  entries live side by side (different hashes, never read across versions); v3 stores only entries of
  path-insensitive plans there.
* `work/`: per-run scratch (`<stem>_<pid>_<time>/jNNNNN/{fx,m,cap}`), removed at the end unless `--keep-work` is given.
* `v3check/`: the v3 self-checks and their outputs (`out/`): `chain_v3.sh` (runs them all, one at a time; log
  `out/chain_v3.log`), `run_review3_v3.py`, `run_adv_v3.py`, `run_syn2_v3.py`, `run_syn3.py` with `syn3/`,
  `static_v3.py`, `rerun_v_suites_v3.py`, `mut_shn113_marked.py` (the draft-only demonstration copy),
  `scan_replace.py` / `scan_tup.py` (the scans of every project mutant script behind the harness-part check).
* `v2check/`, `accept2/`, `ACCEPTANCE_V2.md`: v2's self-checks and acceptance (not edited).
* `review3/`: the third review (not edited). `adversarial/`, `review2/`, `REVIEW_*.md`: the reviews of v1 (not
  edited).

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
* 2026-09-25, **v3** (review3 MAJOR-1, MAJOR-2, MINOR 1–6; session 113 item 20): the read_run memo keys a file
  argument by its path when read_run can carry it (an exception or file object used beyond reading), keys a failed
  stat by its kind, and never stores a value that carries its file argument's path or name; strict extraction also
  reads the harness part of the mutant script (no second collection, every text substitution drawn from one element
  of the recognised collection, filters in front of it evaluated and honoured as SKIPPED, otherwise refused); fast
  mode only when the final exit reads nothing but the pass flag; the guard computes `ok & value` and fails only
  without raising; success needs `ALL OK` anywhere in the output; the job's stdout / stderr are real files with fds
  1 / 2 on them; the recursion limit is raised by the harness's own frames; draft-only markers; the suite is
  transformed and compiled once. mutlib.py v3 sha256
  `5d2f2f90a28e9f405158d2771898f54850692279c3056f4acf0b6aac3b97537d`. v2 kept as `mutlib_v2.py`. Full acceptance on
  the N suites is the next stage.
* 2026-09-25, v3 acceptance (`ACCEPTANCE_V3.md`, `accept3/`): all checks passed on the first try, mutlib.py unchanged
  (sha256 `5d2f2f90…`). Eleven real suites with `--control`: every mutant row equal to its v2 report (verdict and
  kill label), all controls survived; net112 277/277 (also `--no-memo`) and shn113 draft 310/310 name the earliest old
  failing case; the SEALED shn113 with the original `mut_shn113.py` plus two draft-only markers gives 315 killed + 2
  skipped as draft-only; vbn113c keeps `bad_race`. review3: 17/17 configurations agree with the reference (T4a / T4b
  refused, T5 / T5b with the memo on); the v2 counter-examples give the v2 acceptance's comparison line for line (K, I
  by decision; E, E2 refused); P0-P8 0 failures. Timings: v3 = v2 (V suites 1.013x wall over both orders; net112 warm,
  same day, 0.951x; `--no-memo` 1.005x; shn113 cold 0.989x).
