# mutlib — fast, strict, shared mutation harness (v4)

`mutlib.py` replaces the per-session `mut_*.py` run loops. Those loops started a fresh `python test_X.py <mutant>`
subprocess per mutant and ran the whole fixture suite every time, which took 1.5 to 3 hours per N-family scorer.
mutlib reads the same mutant lists and runs the same fixture suites, but it never edits them: the mutant scorer goes
to a scratch directory, and the suite is transformed in memory.

**v4 is current** (sha256 in *Validation of v4*). v3 (sha256 `5d2f2f90…`, accepted in `ACCEPTANCE_V3.md`) is kept
byte-identical as `mutlib_v3.py`, v2 (`877eb53a…`) as `mutlib_v2.py`, v1 (`db8703bd…`) as `mutlib_v1.py`. v4 closes
the holes of the fourth review (`review4/`, evidence in `review4/out/`) and adds the five speed items of ROADMAP
session 115 item 3. Every v3 guarantee is kept; where v4 is faster, the section *How fixture replay works* says why the
answer stays the one the old method gives. The v3, v2 and v1 sections further down are history.

```
python mutlib.py --scorer S --test T --mutants M [--workers N] [--no-memo] [--no-fast] [--no-replay]
                 [--only a,b] [--changed-from PARENT [--sample 0.2] [--seed N]] [--control]
                 [--python INTERPRETER] [--profile-fixtures] [--timeout SEC] [--out FILE]
```

**Which command (the default paths):**

* **A derived scorer** (it has a sealed parent, e.g. `ttl114b.py` from `ttl114.py`): the mutants whose anchor touches
  a line that differs from the parent, plus a reproducible 20 % sample of the rest:
  `python mutlib.py --scorer ttl114b.py --test test_ttl114b.py --mutants mut_ttl114b_sealed.py --changed-from ttl114.py --control`
* **A scorer without a sealed parent:** every mutant: `python mutlib.py --scorer S --test T --mutants M --control`.
* `--no-memo` is no longer needed: the reason for it (review4 MAJOR-2) is closed. The memo is on by default.
* Everything else (fixture replay, early exit, the pipelined baseline) is on by default and turns itself off where it
  cannot be exact; the header says so and why.

**Exit codes** (v3's): 0 every selected mutant killed and every control survived; 1 a survivor; 2 not certified (an
unresolved mutant, a control that did not survive, **v4: the shared fixture store changed during the run**); 3 refused
(also: v4's new refusals below).

**Report** (v3's format; additions only): header lines `selection:` (with `--changed-from`: the parent's sha256, the
changed lines, the touching and the sampled mutants, and the changed lines no mutant anchor overlaps), `fixtures:`
(replay on / off and why, the store, the jobs without replay), `interpreter:` (with `--python`), `memo: off for N
mutant(s) whose source compares object identity`; a `BASELINE#2` line (the second baseline that validates fixture
replay); mutant lines may carry `[rerun isolated in a fresh process without fixture replay: it touched the shared
fixtures (...)]` or `[the suite swallowed the early exit ...; the recorded kill stands]`; summary lines `early exit:`
(how much of the suite the kills skipped), `fixture replay:` (calls replayed per job), `STORE CHANGED` (then the
verdict is NOT CERTIFIED); the verdict line keeps `(N of M selected mutants killed; K defined in the mutant script`
and adds `; selected by --changed-from PARENT: T touching + S of R sampled` when a selection was made.

**Never run it during a sealed run:** it refuses while `C:/kyty/SEALED_RUN.lock` exists (unchanged). It uses
cpu_count − 4 processes by default.

## v4: the fourth review's holes, per hole

Hole ids are review4's triples (`review4/sc_t*`, `test_t*`, `mut_t*`). Checks (all in `v4check/`, outputs in
`v4check/out/`): `run_review4_v4.py` (every review3 and review4 triple against its reference, the reviewer's runner with
its outputs redirected), `filter_probe_v4.py` (review4's 12 filter variants plus 13 of v4's), `fast_rebind_v4.py`
(review4's 11 rebinding variants plus 15 of v4's and 7 that must keep fast mode), `scan_scripts.py` (every project
mutant script under v3 and v4), `static_v4.py`, `run_syn3_v4.py`, `run_syn2_v4.py`, `run_adv_v4.py` (v3's checks,
copies with outputs redirected and at most 2 workers).

| hole | what went wrong in v3 | v4 fix | verified by |
|---|---|---|---|
| **MAJOR-1** (T8a, T8b, T8c) | the evaluation of the mutant script's own filters fell back to a guess: a module-level set later changed by `.discard` was read as its literal, `name = name.upper()` was ignored, `EQUIV.count(name)` on a file's text was evaluated on the scorer's text - mutants the old loop RAN were reported SKIPPED (a false ALL KILLED) | a filter is evaluated only where its value needs no fallback, otherwise the run refuses (exit 3, the message suggests a re-filter or `DRAFT_ONLY`): the element's name / old / new only when the loop binds them once in their scope; a name bound in front of the filter only when bound once, and a container only if it is never changed or handed out; a module-level name only when bound once by a literal BEFORE the substitution, and a container only if every use of it is read-only (no `.discard` / `.add` / `[:] =` / `del x[i]` / alias / helper / `*x`); a function-local name never; `X.count(old)` on a text mutlib cannot evaluate only when X is the very text the substitution edits (the anchor check), anything else refuses | run_review4_v4 T8a, T8b, T8c: REFUSED; filter_probe_v4: 25 variants, 0 false skips (19 refused, 6 agree with the loop, among them the anchor-check shapes `SRC.count(old) != 1` and `n = SRC.count(old); if n != 1`); scan_scripts: all 85 project mutant scripts give v3's outcome and list |
| **MAJOR-2** (T16) | the memo returns a fresh copy of read_run's value, so `v is not MISSING` (a sentinel) and `r['kind'] is 'empty'` (an interned literal) changed their answer: two false kills, only `--no-memo` was right | the memo plan is off for a source that compares identity: an `is` / `is not` whose operands are not None / True / False / Ellipsis / NotImplemented / a builtin type / `type(x)` / `x.__class__`, a call of `id()`, `operator.is_` / `is_not`. The scorer's plan and each mutant's own plan (that job runs without the memo; the header lists them); the SUITE's identity use turns the memo off for the run. Runtime backstop: a value holding a NaN (equal to itself only by identity: `v in rows`, `[v] == [v]`; found in the pickle's bytes, every float is pickled as BINFLOAT) is never stored and the uncached object is returned | run_review4_v4 T16 ctl_cold, ctl_warm (memo on): `is_sentinel`, `is_literal` SURVIVE as in the old method; the eleven accepted suites use only singleton comparisons (`type(size) is int` counts as one), so the memo stays on for them |
| **MINOR-1** (T14, `review4/static/fast_rebind.py`) | fast mode saw only some rebindings of `ok`: `ok, note = recheck(...)`, list / starred targets, a walrus, a match capture, a nested `global ok` with a tuple target left fast mode on, and an early exit killed a mutant the old method let survive | every binding of the module's `ok` is found (module scope and every function at any depth that declares it global, a walrus in a comprehension there, match captures, except / import / def / class / del / with / for targets) and fast mode is on only if all of them are the one `ok = True` and `ok &= ...` / `ok = ok and ...` | run_review4_v4 T14 ctl: `limit2` SURVIVES as in the old method; fast_rebind_v4: 26 rebinding variants turn fast mode off, 7 harmless shapes (a function's own `ok`, a lambda parameter, a class attribute, a comprehension variable) keep it; the 262 project suites keep their v3 decision |
| **MINOR-2** (T10) | the early exit is an exception; a suite that runs each case in `try: ... except BaseException:` swallowed it, went on and exited 0: a false survivor | the kill is recorded BEFORE the exception is raised; every later hook (guard, print hook, end marker) raises it again, and at the end of the job the recorded kill is the verdict whatever the suite did with the exception (the report notes `the suite swallowed the early exit`) | run_review4_v4 T10 ctl: `no_refusal` KILLED by `negative` as in the old method; `static_v4` §3 |
| T11, T12, T13 (review4, outside the list above) | the harness part ran the suite with an extra argument (`--quick`), ran a second script with runpy, or extended MUTANTS through `globals()`: a false kill or mutants mutlib never saw | refused: a `subprocess` call of `sys.executable` in the harness part may pass the suite only the mutant scorer and a fixture directory (no flag after the script, no `env=`); a mutant script that uses `globals` / `vars` / `locals` / `exec` / `eval` / `__import__`, `.__dict__`, `sys.modules`, or imports `runpy` / `importlib` is refused | run_review4_v4 T11, T12, T13: REFUSED; scan_scripts: no project script newly refused |
| T9a, T9b | a filter AFTER the substitution (`write; if name in SKIP: continue; run`) or a filter of the survivor tally: mutlib runs the mutant and may report a survivor the old loop hid | **not changed** (a possible false SURVIVOR, more work for the reviewer, never a false kill) | run_review4_v4 T9a, T9b: DIFFERS as before |

## v4: speed, the five items (ROADMAP session 115 item 3)

### (1) Selection for derived scorers: `--changed-from PARENT [--sample F] [--seed N]`

Every selected mutant whose anchor overlaps a line of `--scorer` that `difflib` finds changed against PARENT (a deletion
marks the lines around it), plus a reproducible sample of the rest: `random.Random(seed).sample(rest, round(F * len))`
over the rest in definition order, F = 0.2 by default, the seed = the first 16 hex digits of the scorer's sha256 unless
`--seed` is given (the same list as v3 for the same inputs). Draft-only and filter-skipped mutants are never selected.
v4 makes it robust and reportable: `--sample` / `--seed` without `--changed-from` refuse (exit 3), so do a sample
outside 0..1 and a missing parent; the header names the parent and its sha256, the number of changed lines, the
touching mutants, the sampled mutants and the changed lines **no** mutant anchor overlaps (lines this run does not
mutate - look at them); the verdict line says `selected by --changed-from <parent>: T touching + S of R sampled`.
Example (ttl114b from ttl114): 22 changed lines, 12 touching + 67 of 333 sampled = 79 of 345 mutants.

### (2) Shared read-only fixtures: fixture replay

Every job used to run the suite's fixture generators itself (ttl114b: 221 calls of make / variant / video, 53 s of
Python and 4-5 GB of files per job, 1.7 TB written for one run). v4 generates them ONCE per run and lets every job
reuse them read-only, keeping a fresh interpreter per job and the suite's own order of execution: see *How fixture
replay works* below. Measured on ttl114b (5 mutants and 3 controls, 2 workers, `v4check/out/real/`): a mutant killed
by an early case took 1.3-2.3 s instead of 108-122 s (v2's report); a mutant of a constant make() reads (ARMS) ran its
generators for real (87 s); the three controls, which run the whole suite, 134-139 s (467 s for the one that mutates
read_run and so misses the memo on every parse).

### (3) Early exit

v3 ended a job at the first exact failing guard at module level. v4 also ends it at an exact failing guard inside a
function that declares the pass flag global (the kill is recorded before the raise, review4 MINOR-2), and measures what
it saves: the summary line `early exit: K kill(s) ended at their first failing case; they skipped a median X % / mean
Y % of the suite's N checks, about Z s of the baseline's suite time per job`. Exactness is v3's: the guard's `ok` and
value are plain bool / int, fast mode's conditions hold (the only bindings of `ok` are `ok = True` and `&=` / `ok and`
updates, the final exit reads only `ok`, no other exit), so `ok` stays 0 / False and the original suite exits non-zero.
For the N family the kill happens in the final loop; with fixture replay the fixture phase before it no longer costs
the job anything.

### Also: the memo for a mutated read_run

A job whose read_run closure is mutated (its dependency hash differs from the scorer's) runs **without** the memo: its
values could only be reused inside that job, and a guarded miss costs more than such a repeat saves (ttl114b: about
+0.38 s a miss on a 0.9 s parse, about 200 parses against 51 repeats; `v4check/probe_miss_cost.py`). Without the memo the job computes exactly what the old
harness computed. (v2check's S3 no longer trips the runtime guard for its `grow` mutant for this reason; the guard is
still exercised on the scorer's own closure by `runtime_memo_checks.py`, 0 failures against v4.)

### (4) Another interpreter: `--python PATH`

Every job (the baselines too) runs under PATH: `PATH mutlib.py --_job SPEC RESULT`, with the job described and answered
by pickle files (protocol 4) and the suite transformed again in each job (another interpreter cannot load CPython's
marshalled code). On an interpreter whose `os` functions raise no audit events (PyPy), mutlib raises them itself
(`os.remove` / `rename` / `replace` / `link` / `symlink` / `mkdir` / `rmdir` / `chmod` / `utime` / `truncate` / `listdir` /
`scandir`), so the write audit and the shared-fixture guard see what they see under CPython; and a replaying job
identifies the shared files by `os.stat` in its own interpreter (PyPy reports another `st_dev` than CPython). PyPy 3.12 v8.0.0
(`pypy3.12-v8.0.0-win64.zip`, sha256 `0ccfe530cf22330bd225c561bb41b6200a759d96a15847c541d4b98859adaf3f`, equal to the
checksum pypy.org publishes) is installed in `C:/kyty/tools/pypy/pypy3.12-v8.0.0-win64/pypy3.exe`.
**Not recommended (yet):** the verdicts and labels are identical to CPython where compared (check112: 24 / 24 rows,
controls 3 / 3; the ten syn4 configurations), but the gain is small - ttl114b's whole suite in one process takes 290 s
under PyPy against 364 s under CPython (fixture generation 1.7x faster, parsing 1.4x, the scorer's evaluation slower),
check112's run 10.9 s against 10.6 s - and PyPy differs where a suite could notice: files are closed by the garbage
collector, not when the last reference goes (a suite that opens without `with` and then removes or renames the file
fails on Windows), `is` compares ints / floats / strings by value, the recursion limit counts differently. The
acceptance must compare a suite's verdicts and labels under both interpreters before PyPy is used for it.

### (5) Fixture sizing: `--profile-fixtures` and rules for new generators

`--profile-fixtures` runs the baseline only (generators recorded, nothing replayed, no mutant) and prints, per case,
the time its fixture generation took, the bytes and rows (newlines) of the files written for it, the number of files,
the time its check took, and the generators that made them; then the ten largest and the ten slowest cases. N family:
a case owns the generator calls made after the previous `case(...)` registration and before its own, and its check is
its guard in the final loop; V family: a case is the segment before each guard. Exit 0 after the report (3 when the
baseline fails). ttl114b (`v4check/out/real/ttl114b_profile.txt`): 249 cases, 451 files, 5.15 GB, 12.2 million rows;
every make() writes 25.7 MB / 61 013 rows (224 blocks of 90 frames, three lines each) in 0.32 s, and every check costs
about 0.4 s (0.1 s of it the memo hit on the 25.7 MB log). Once fixtures are replayed, the checks dominate a job, and
their cost follows the length of the log: a base four times shorter makes every check about four times cheaper.

**Rules for new fixture generators** (existing tests are not edited; these are for the next ones):

1. **The minimum rows that keep every threshold edge.** A log needs the rows its case tests and no more: the scorer's
   admission minimum (pairs, blocks, flips) plus ONE margin unit, not the production length. Put the edge cases (at the
   edge, one step beyond) on the same minimum-length base; derive the size from the suite's own hard-coded window
   constants (never from the scorer, so a mutant cannot move its own fixture), and assert in the suite that the base
   still clears every admission minimum.
2. **Generate once, derive by reference.** One base log (`make('good')`); the variants hard-link or append to it
   (`variant()`), they do not regenerate identical text. `--profile-fixtures` shows the bytes per case: a case above a
   few MB wants a reason.
3. **Keep generators replayable** (fixture replay works only on them; a violating call simply runs in every job):
   a top-level `def`, not decorated, no `global`, no update of the pass flag; its result a function of its arguments,
   the suite's globals and the scorer's constants only; no printing; no global random state (`random.Random(seed)` is
   fine); no time, process id, hash of an object, directory listing outside the fixture directory, reading of the
   scorer file, writing outside the fixture directory; return an immutable value (a Path, a string, a tuple); embed
   the fixture path only whole (the job directory's NAME alone is not substituted), and do not change a generated file
   after the generator returns (write its final content inside the generator; otherwise every job gets a private copy
   of that file, which costs its write).
4. **No reliance on file times, inode numbers, link counts or write permission** in the scorer or the suite (they
   differ for shared files; mutlib turns replay off for such a suite).

## How fixture replay works (and why the answer does not change)

1. **Candidates** (static): the suite's top-level functions whose code can write a file, directly or by calling
   another such function (`write_text`, `open`, `mkdir`, `link`, `copyfile`, `dump`, ...), except `case`, decorated
   functions, generators, and functions with a `global` statement or an update of the pass flag. The suite is
   transformed with `F = _mutlib_fx(F, 'F')` right after each candidate's def (the wrapper keeps `__name__`,
   `__wrapped__`); only its outermost calls (depth 0) are recorded or replayed. Replay is off for the run when the scorer
   or the suite reads file times, inode numbers, link counts, modes (`st_mtime`, `st_ino`, `st_nlink`, `st_mode`,
   `samefile`, `lstat`, `os.access`, ...), with `--no-replay`, or when the suite has no candidate.
2. **Recording, twice.** The baseline R1 and a second baseline R2 run side by side, in two job directories of the same
   path length (`jNNNNN`), in two processes (different pids, times, random seeds). For every depth-0 generator call each
   records: a fingerprint of its **arguments** (structural; functions and lambdas by code and closure contents), of the
   **suite globals its code can look up** (the global names in the bytecode of the generator and of every suite function
   / lambda reachable through its arguments, closures and the suite's globals; reflection - `globals`, `vars`,
   `eval`, `__dict__`, frames, `sys.modules` - makes the call unreplayable), the **scorer-module attributes it read**
   (the scorer module's class is switched to a subclass whose `__getattribute__` notes reads during a recorded call; a
   scorer function read that way makes the call unreplayable), the **files outside the fixture directory it opened**
   (their content hash; the scorer file itself makes it unreplayable), the environment / cwd / argv / sys.path / where
   printing goes / the locale / the decimal context, and the
   **whole fixture directory** before and after (every name, size and content hash); its **effects** (directories and
   files created, changed, removed; a file that carries the job directory's path in any spelling - as given, with `/`,
   backslash-escaped as in JSON or repr, lower-cased - is kept as bytes with the path as a placeholder; any other file
   by its content hash) and its **return value** (an immutable value, paths as placeholders). A call is recordable only
   if it changed nothing else: arguments, the suite globals it can reach, scorer values it read, the environment, the
   global random state, the threads, the job's output (no printing); no process, no directory listing outside the
   fixture directory, no write outside it. R1 copies every recorded file into the run's store (`fxstore/<sha256>`).
3. **Validation.** A call is replayable only if R1 and R2 recorded it identically once each one's job directory is a
   placeholder: the same inputs, the same effects (the same file hashes; the same bytes of the path-carrying files) and
   the same return value. So a generator that embeds anything but the full job path, or depends on time, the process
   or global random state, is never replayed (the hash seed is the same for every job: item 6). If the two baselines made different sequences of calls,
   replay is off. The store files are checked against their hashes and made **read-only** (the Windows attribute).
4. **Replay** (every other job, when the mutated text cannot act at import beyond binding its own names: a comment, a
   def's body, an assignment of data; otherwise that job runs its generators for real). Call #i is replayed only if
   **every input R1 recorded is equal now**: the arguments, the suite globals, the scorer attributes R1 saw read (with
   this mutant's values: a mutant of a constant make() reads runs make() for real), the outside files, the environment,
   and the whole fixture directory. If one differs the call runs for real (from then on the directory differs and the
   later calls usually run for real too). Replaying applies the recorded effects to the job's OWN fixture directory:
   directories made, files hard-linked to the store (NTFS; a private copy above 900 names per file, and for a file the
   suite changes later), path-carrying files written with this job's own path, removals done; the recorded return value
   is returned with this job's path. Given the same inputs a deterministic call has the same effects, and the recorded
   call was validated as deterministic, so the job's fixture directory and the values it holds are exactly those the
   original run would have produced; the order of execution is the suite's own.
5. **Protection.** The store files are read-only; a job that tries to write, truncate, remove, re-mode, overwrite, copy
   the mode of, or map a shared file (or link it past the link limit) is stopped by the audit hook before the
   operation happens (`FxTouched`), its result is discarded, and it is **rerun in a fully isolated fresh process without
   replay** (`[rerun isolated ...]`). At its end every job re-hashes the shared files it read; after every job the
   parent checks every store file's size, time and read-only mode (a restored mode is reported); at the end it
   re-hashes the whole store. A changed store file cannot be traced to
   one job, so the run is **NOT CERTIFIED** (exit 2), never a kill.
6. **One hash seed.** With replay on, every job of the run (the two baselines too) runs with `PYTHONHASHSEED=0`:
   a generator that writes the iteration order of a set of strings writes what every job would write (two baselines
   with random seeds could agree on such an order by chance and so validate it).
7. **The pipelined baseline** (N family): both baselines dump their recording when they reach the final loop; the
   parent validates it, finalises the store and starts the controls and mutants while the baselines still run their
   checks (the control that mutates read_run, the longest job of a run because it parses everything, starts together
   with the baselines). The mutant timeout is provisional (4 h) until the baseline passes; the fast-mode exit probe is evaluated in the
   parent (a plain expression of `ok`) and must match the baseline's. If a baseline fails, writes outside its directory,
   starts a process, or evaluates the exit differently, every result so far is dropped and the run starts again the v3
   way (the baseline alone, then the mutants, no replay) - said in the header. V family: the two baselines run first,
   then the mutants.

## Residual assumptions added by v4 (v3's still hold, below)

* **Fixture replay compares the inputs it can see.** A generator's arguments, the suite globals its bytecode can look up,
  the scorer attributes it read, the files outside the fixture directory it opened, the whole fixture directory, the
  environment / cwd / argv / sys.path / where printing goes / the locale / the decimal context. It does not see the
  state of other modules (the `json` encoder's switches, a `warnings` filter, ...) that scorer code could change at run
  time; a mutation that could change such state at import time runs without replay (only comments, function bodies
  and data assignments are replayed), and a generator that reads such state is assumed not to.
* **Determinism is established by two runs.** A generator whose output depends on something that happened to be equal
  in both baselines but differs in a later job (a coin that landed the same twice, the date changing) is not caught.
* **Existence checks outside the fixture directory raise no audit event**: a generator whose behaviour depends on a
  path outside the fixture directory that a job creates or deletes is not caught (such a job is an outside writer: the
  jobs that ran next to it are rerun alone, v3's rule).
* **Shared files are not fresh files.** Their times, inode, link count and read-only mode differ; replay is off when the
  scorer or the suite names them (`st_mtime`, `st_ino`, `st_nlink`, `st_mode`, `samefile`, `lstat`, `os.access`, ...),
  and a mutant whose text names them runs without replay. Reading `os.stat(p)[8]` by index is not seen.
* **The recording baselines switch the scorer module's class** (to follow attribute reads). A suite that tests
  `type(mod) is types.ModuleType` would behave differently in them (its baseline would fail, the run would say so).
  Replaying jobs do not switch it.
* **Writes by native code that raise no audit event** (v3's assumption) now also cover the shared store: such a write to
  a shared file fails on the read-only attribute and is not reported as touching the store.
* **The pipelined baseline** starts the mutants before the baseline's verdict; a failing, outside-writing or
  differently-exiting baseline drops every result and restarts the run the v3 way.
* **Early exit inside a function** relies on the same exactness as v3's module-level exit; the recorded kill is honoured
  even when the suite swallows the exception and later exits 0 (the report notes it).
* **Selection** follows the scorer text: a mutant whose anchor lies on an unchanged line is only sampled, even if the
  changed lines change its meaning (the sample is the guard against that; the uncovered changed lines are listed).

## Files (v4)

* `mutlib.py`: the harness (v4). `mutlib_v3.py`: v3, byte-identical to the accepted file (sha256 `5d2f2f90…`).
  `mutlib_v2.py`, `mutlib_v1.py`: unchanged.
* `cache/_shared_v4/`: v4's parse memo, shared by every scorer (the key holds the hash of read_run's closure, so a
  derived scorer with the parent's read_run hits the parent's entries); `cache/<scorer stem>/durations.json`. Older
  directories (`cache/net112`, ...) hold v1-v3 entries, never read by v4, and can be deleted.
* `work/<run>/`: per-run scratch: `jNNNNN/{fx,m,cap}` per job, `fxstore/` (the read-only shared fixtures),
  `fxrec_r1.pkl` / `fxrec_r2.pkl` (+ `.g`) the recordings, `fxplan.pkl`; removed at the end unless `--keep-work`.
* `v4check/`: v4's checks and their outputs (`out/`), listed in the sections above; `syn4/` the fixture-replay triples;
  `prof_suite.py`, `probe_memo_cost.py`, `probe_pypy_features.py` the design measurements behind v4
  (`out/prof_ttl114b*.txt`); `compare_rows.py` compares a report row by row with a reference report.
* `C:/kyty/tools/pypy/`: the PyPy used by `--python` (outside this folder; the zip kept with its checksum).

## Validation of v4

Final file: mutlib.py sha256 **`b666df3594ec245f488585b93ec7282fee5bfdff16d45e34cad60b01dd9f922b`**. The small checks
ran on it through `v4check/small_v4.sh` (one step at a time, at most 2 workers, log `v4check/out/small_v4.log`), the
heavy ones through `v4check/heavy_v4.sh` (28 workers, one run at a time, each step behind the full gate: `V4_GO`, no
`SEALED_RUN.lock`, a clean `procload.py`; outputs `v4check/out/heavy/`, the earlier file's in `out/heavy/b1_6118aef5/`).
No game, emulator or build was run by this work.

**The target: one ABBA-size seal (ttl114b, 345 mutants, about 70 min in session 114).**

| run (28 workers, `--control`) | mutlib file | wall | rows equal session 114's report (verdict + kill label) | controls |
|---|---|---|---|---|
| `--changed-from ttl114.py` (the default path for this derived scorer: 12 touching + 67 sampled = 79), warm parse cache | final `b666df35` | **458 s (7.6 min)** | 79 / 79 | 3 / 3 |
| the same, cold parse cache (a fresh `--cache-dir`) | final `b666df35` | **614 s (10.2 min)** | 79 / 79 | 3 / 3 |
| the same, warm / cold | `6118aef5` (before the NaN backstop read the pickle's bytes) | 446 s / 679 s | 79 / 79 each | 3 / 3 |
| all 345 mutants (no selection), warm | `6118aef5` | **1 220 s (20.3 min)**; v2: 4 086 s | **345 / 345** | 3 / 3 |

In the selection runs the two baselines validated all 221 generator calls and every job replayed them (17 459 replayed,
0 ran for real); in the full run 1 549 calls ran for real (the mutants of the constants the generators read) and
74 698 were replayed. All runs: 0 isolated reruns, 0 store changes, 0 reruns of any kind. The kills skipped a median
99 % (mean 77 %) of the suite's 249 checks in the selection, 86 % / 72 % over all 345. The wall of the selection is set
by its longest job, the control that mutates read_run (454 s warm, 563 s cold: every parse uncached, no memo), which
starts with the baselines (285 s warm, 605 s cold); worker time 6 181 s warm, 12 525 s cold. The full run needs
30 258 s of worker time, so its wall is set by the total, not by one job.

**Correctness checks** (all on the final file):

* **review4's holes** (`out/review4/review4_compare.txt`): 56 configurations agree with their reference or are refused
  as decided: T8a, T8b, T8c (MAJOR-1) refused; T16 cold / warm (MAJOR-2) agree with the memo on; T14 (MINOR-1) and T10
  (MINOR-2) agree with fast mode on; T11, T12, T13 refused; review3's 17 as in the v3 acceptance (T4a / T4b refused,
  T5 / T5b with the memo on). T9a / T9b differ as before (a survivor the old loop hid, never a kill).
* **Probes:** `filter_probe_v4.py` 25 variants, 0 false skips; `fast_rebind_v4.py` 0 BAD (26 rebindings off, 7 harmless
  shapes on); `static_fx_v4.py` 0 failures (identity uses, the deny list, generator candidates, import inertness, the
  job-path forms, the validation of two recordings, the read-only store: finalise, per-job check, full verification,
  deleting read-only links); `probe_nan_blob.py` (the pickle-level NaN test agrees with a walk of the value).
* **v3's checks against v4** (copies with outputs redirected, at most 2 workers): `static_v4.py` 0 failures (its guard
  checks use a fresh runtime per check: an early exit now re-raises at every later hook of the same job);
  `static_checks_v2_on_v4.py` and `runtime_memo_v4.py` 0 failures; `run_syn3_v4.py` 23 checks, 0 BAD;
  `run_syn2_v4.py` 6 / 6 (S3's `grow` mutates read_run and so runs without the memo: KILLED as in the old method,
  without the memo-rerun note it had in v2 / v3); `run_adv_v4.py`: the same comparison as the v2 and v3 acceptances line
  for line apart from hashes (K stricter and I noted by decision, E / E2 refused, controls 3 / 3).
* **Every project mutant script** (`scan_scripts.py`, 85 files under `C:/kyty/s1*`, `s8*`, `s9*`): 57 accepted with v3's
  exact list, skips and marks, 28 refused by both; none newly refused.
* **Fixture replay** (`run_syn4.py`, 13 configurations against `adversarial/oldstyle.py`): every verdict and first
  failing case equals the old method's, controls 3 / 3 each: replay on with the job path carried in a JSON-escaped
  meta (RP), a job that touches a shared file rerun isolated (RPT), a file the suite changes later replayed as a private
  copy (RPM), a set order written into a fixture (RPH), replay refused for time (RPN), global random (RPG), printing
  (RPP), the job directory's name (RPD), a scorer function (RPS), `--no-replay` (RP_nr), and RP / RPT / RPM under PyPy.
* **Real suites, row by row at 2 workers** (`compare_rows.py`): check112 24 / 24 against `accept3/` (also under PyPy:
  24 / 24); check115 104 / 104 against session 115's v3 report; ttl114b 9 / 9 (`--only`: kills at the first cases and
  late ones, the two constants make() reads - their 442 generator calls ran for real - and the one read_run mutant;
  795 s), controls 3 / 3 each.
* **The fixture profile** (`--profile-fixtures`): ttl114b and check112 (`v4check/out/real/ttl114b_profile.txt`).
* **Not done here** (left to the acceptance): net112 at 28 workers (`heavy_v4.sh net112`) and the PyPy comparison on
  a large suite (`heavy_v4.sh sel_pypy`). Until that comparison shows identical verdicts, PyPy is not recommended.

## Changelog (v4; the earlier entries are in the v3 README below)

* 2026-09-25, **v4** (review4 MAJOR-1, MAJOR-2, MINOR-1, MINOR-2 and T11 / T12 / T13; ROADMAP session 115 item 3, the
  five speed items): strict evaluation of the mutant script's own filters (refuse instead of a fallback); the memo off
  for a source that compares object identity, NaN values never cached, and no memo for a mutated read_run; every
  rebinding of `ok` turns fast mode off; an early-exit kill is recorded before its raise and honoured when swallowed;
  early exit also inside global-`ok` functions, with the skipped share reported; the harness part may not pass the suite
  extra arguments / environment, reflection and runpy / importlib refused; `--changed-from` refuses a stray `--sample` /
  `--seed` and reports parent, touching, sampled and uncovered lines, also in the verdict line; fixture replay (two
  recording baselines, a read-only store of hard-linked fixtures, per-call input checks, touched jobs rerun isolated,
  the store checked after every job and re-hashed at the end, `PYTHONHASHSEED=0` for a replaying run), a pipelined start
  for the N family, `--no-replay`; `--python` (PyPy 3.12 v8.0.0 installed, checksum verified; not recommended yet);
  `--profile-fixtures`; the memo cache shared by all scorers (`cache/_shared_v4`). mutlib.py v4 sha256
  `b666df3594ec245f488585b93ec7282fee5bfdff16d45e34cad60b01dd9f922b`; v3 kept as `mutlib_v3.py`. The acceptance
  (ROADMAP: quick - net112 and two small suites, the counter-examples, the timing) is the next stage.

## The v3 README (history; unchanged below, its headings demoted)


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

### v3: what changed and why, per hole

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

### How it works (v3)

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

### Residual assumptions (stated, not hidden)

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

### Validation of v3 (2026-09-25, before acceptance on the N suites)

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

### v2: what changed and why, per hole (history)

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

### Validation of v2 (history: 2026-09-24, before acceptance on the N suites)

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

### v1 history

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

### Files

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

### Changelog

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
