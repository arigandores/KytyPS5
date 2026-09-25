# mutlib v3 acceptance (2026-09-25)

**Harness:** `C:/kyty/s106_stage/mutlib/mutlib.py`, sha256 **`5d2f2f90a28e9f405158d2771898f54850692279c3056f4acf0b6aac3b97537d`**.
Every check below passed on the first try, so mutlib.py was **not changed**. Every v3 report carries this sha in its
header, and `accept3/check_accept_v3.py` verifies it (env `MUTLIB_SHA`).
`mutlib_v2.py` is still byte-identical to the accepted v2 (sha256 `877eb53a…`), and `mutlib_v1.py` is unchanged (`db8703bd…`).

**Verdict: PASS.**

* **Item 1, real suites: PASS.**
  * All eleven suites, run with `--control`, give their v2 verdict and their v2 kill label on every mutant: 1 225 of
    1 225 mutant rows, 1 502 of 1 502 with the net112 `--no-memo` run. The extra runs (the warm net112 rerun and the
    second timing pass) agree as well.
  * Every control survived: 3 of 3 in all 13 runs of `accept3/chain.sh` (12 acceptance runs plus the warm net112
    rerun) and in the 8 v3 runs of the second timing pass.
  * net112 and shn113 (draft) name the old harness's earliest failing case for 277 of 277 and 310 of 310 mutants.
  * The sealed shn113 with the ORIGINAL `mut_shn113.py` (a copy with the two v3 markers) gives exactly the expected
    result: **315 killed, 2 skipped as draft-only, controls 3 of 3**. Its 315 rows are identical to session 113's report.
  * vbn113c keeps the known survivor `bad_race`.
* **Item 2, counter-examples: PASS.**
  * **review3:** all 17 configurations agree with their reference (`adversarial/oldstyle.py` unedited, or for T4 the
    mutant script's own loop).
    * T4a and T4b are REFUSED with exit 3.
    * T5 and T5b agree with the memo ON.
    * T4c reproduces the script's own filter as SKIPPED.
  * **The v2 counter-examples** (the same 19 configurations / 23 runs as ACCEPTANCE_V2): the comparison is identical to
    the v2 acceptance's, line for line, apart from timings and hashes.
    * K is stricter and I is noted, not emulated: the two differences decided in v2.
    * E and E2 are refused.
    * The labels agree.
  * **Review 2's memo probes P0–P8:** 0 failures.
  * **Supplement: new probes written for this acceptance.** They exercise the two MAJOR fixes with shapes the builder did
    not test: 11 path-analysis variants and 6 harness-part variants. Result: 0 unsafe, all 6 harness variants refused.
* **Item 3, timings: recorded below. v3 costs the same as v2.**
  * **V suites:** all eight, with both orders of v2 / v3, took 385.8 s under v3 against 381.0 s under v2 (1.013).
  * **N suites:**
    * net112 with a warm cache, same day: 0.951 of v2's wall.
    * net112 `--no-memo`: 1.005 of v2's wall.
    * shn113 draft, cold cache: 0.989 of v2's wall.
  * The one run that was slower, the first v3 net112 run (cold cache), is discussed in §3.

**How the runs were done:**
* **Chains:** `accept3/chain.sh` ran the acceptance and `accept3/chain2.sh` the second timing pass. Both run strictly one
  step at a time, and no two heavy runs ever overlapped.
* **Sealed-run lock:** `C:/kyty/SEALED_RUN.lock` was absent throughout. The chains check for it before every step.
* **Machine load:** the CPU load was sampled right before each of the 41 steps and was 0–18 % (median about 3 %). No
  game ran and no build ran.
  * A concurrent read-only reviewer agent may have been active. It never showed in the load samples.
* **Workers:** 28 workers on 32 threads, mutlib's default. Every real-suite run used `--control`.
* **Where the output is:**
  * reports, stdout and stderr are in `accept3/<run>.*`;
  * the externally measured wall time (with the load sample) is in `accept3/<run>.wall.txt`;
  * the per-report checks are in `accept3/<run>.check.txt`;
  * the v2 timing runs are in `accept3/v2t/`;
  * the second timing pass is in `accept3/timing2/`.
* **Environment:** Python 3.13.13; `PYTHONIOENCODING` and `PYTHONUTF8` unset, so the old console encoding is cp1250.
* **Inputs:** every scorer, test and mutant script has the same sha256 as in the header of its v2 reference report (checked
  before the runs). The only file that differs from a project file is the marked copy `accept3/mut_shn113_marked.py`:
  * sha256 `68b63ac5…`;
  * it equals `C:/kyty/s113/mut_shn113.py` (`bc0b66a8…`) except for a trailing comment `# mutlib: draft-only` on the
    two lines `CONST_pred_sha_prefilled` and `CONST_pred_bytes_prefilled` (a 2-line diff, verified with difflib).

## Summary table (item 1)

| suite | scorer (sha256 prefix) | mutants | v3 result | controls | rows equal to the v2 report (verdict + label) | first failing case vs old harness | v3 wall | v2 wall (reference) |
|---|---|---|---|---|---|---|---|---|
| check112 | `s106_stage/check112.py` (`829cb59f`) | 24 | **24 killed** | 3 / 3 | 24 / 24 (`accept2`) | — | 3.4 s | 3.2 s |
| vdg112 | `s106_stage/vdg112.py` (`7d44c5b6`) | 36 | **36 killed** | 3 / 3 | 36 / 36 | — | 18.8 s | 18.7 s |
| vbn113b | `s113/vbn113b.py` sealed (`688db5fc`) | 41 | **41 killed** | 3 / 3 | 41 / 41 | — | 28.4 s | 27.0 s |
| vbn113c | `s113/vbn113c.py` sealed (`834044de`) | 43 | **42 killed + `bad_race` SURVIVED** (known) | 3 / 3 | 43 / 43 | — | 31.9 s | 29.4 s |
| vbn113d | `s113/vbn113d.py` sealed (`7952a9c8`) | 43 | **43 killed** | 3 / 3 | 43 / 43 (`s113/mut_vbn113d.out.txt`) | — | 30.9 s | 36.0 s (s113) |
| vbn113e | `s113/vbn113e.py` sealed (`4977228d`) | 51 | **51 killed** | 3 / 3 | 51 / 51 | — | 35.8 s | 36.4 s (s113) |
| vbn113f | `s113/vbn113f.py` sealed (`7595b199`) | 54 | **54 killed** | 3 / 3 | 54 / 54 | — | 40.4 s | 45.9 s (s113) |
| check113 | `s113/check113.py` sealed (`2120ed5a`) | 31 | **31 killed** (1 by a crash in the scorer, as in v2) | 3 / 3 | 31 / 31 | — | 4.5 s | 4.7 s (s113) |
| net112 | `s106_stage/net112.py` (`566c8bf1`) | 277 | **277 killed** | 3 / 3 | 277 / 277 | **277 / 277** | 1526.3 s (cold v3 cache) | 1267.7 s (warm) |
| net112 `--no-memo` | same | 277 | **277 killed** | 3 / 3 | 277 / 277 | **277 / 277** | 2016.7 s | 2006.6 s |
| shn113 (draft) | `s106_stage/shn113.py` (`026fae4f`) | 310 | **310 killed** | 3 / 3 | 310 / 310 | **310 / 310** | 2040.4 s (cold) | 2062.6 s (cold) |
| shn113 (SEALED) | `s113/shn113.py` (`c5a582be`), mutants = marked copy of `s113/mut_shn113.py` | 317 defined | **315 killed, 2 skipped as draft-only** | 3 / 3 | 315 / 315 (`s113/mut_shn113.out.txt`) | (no old-harness run exists) | 2206.3 s | 3217.5 s (s113, `--no-memo`) |
| *extra:* net112 warm | same as net112 | 277 | 277 killed | 3 / 3 | 277 / 277 | 277 / 277 | 1298.0 s | 1365.4 s (v2 same day) |

**Totals over the 13 v3 runs of `accept3/chain.sh`:**
* 0 unresolved (timeout, harness error, environment, not reproduced).
* 0 confirmation reruns, 0 memo reruns, 0 "rerun alone".
* No run forced to one worker, no memo disabled at run time, no `WARNING could not remove` line.
* Fast mode was confirmed by the baseline in every run.

**Verdict lines:** every one carries the counts, for example
`ALL KILLED (315 of 315 selected mutants killed; 317 defined in the mutant script, 2 skipped as draft-only)`.

## 1. Real suites: PASS

**Commands** (from `C:/kyty/s106_stage/mutlib`, via `accept3/chain.sh`; `$S` = `..`, `$X` = `C:/kyty/s113`, `$A` = `accept3`):
```
mutlib.py --scorer $S/check112.py --test $S/test_check112.py --mutants $S/mut_check112.py --control
mutlib.py --scorer $S/vdg112.py --test $S/test_vdg112.py --mutants $S/mut_vdg112.py --control
mutlib.py --scorer $X/vbn113b.py --test $S/test_vbn113b.py --mutants $S/mut_vbn113b.py --control
mutlib.py --scorer $X/vbn113c.py --test $S/test_vbn113c.py --mutants $S/mut_vbn113c.py --control
mutlib.py --scorer $X/vbn113d.py --test $S/test_vbn113d.py --mutants $S/mut_vbn113d.py --control
mutlib.py --scorer $X/vbn113e.py --test $X/test_vbn113e.py --mutants $X/mut_vbn113e.py --control
mutlib.py --scorer $X/vbn113f.py --test $X/test_vbn113f.py --mutants $X/mut_vbn113f.py --control
mutlib.py --scorer $X/check113.py --test $X/test_check113.py --mutants $X/mut_check113.py --control
mutlib.py --scorer $X/shn113.py --test $X/test_shn113.py --mutants $A/mut_shn113_marked.py --control
mutlib.py --scorer $S/net112.py --test $S/test_net112.py --mutants $S/mut_net112.py --control
mutlib.py --scorer $S/net112.py --test $S/test_net112.py --mutants $S/mut_net112.py --control --no-memo
mutlib.py --scorer $S/shn113.py --test $S/test_shn113.py --mutants $S/mut_shn113.py --control
mutlib.py --scorer $S/net112.py --test $S/test_net112.py --mutants $S/mut_net112.py --control      (net112_warm, timing)
```
* **Byte-identical inputs:**
  * `$X/test_vbn113e.py`, `$X/mut_vbn113e.py`, `$X/test_vbn113f.py` and `$X/mut_vbn113f.py` are byte-identical to the
    `s106_stage` copies that session 113's reports name.
  * vbn113d's test and mutant scripts live only in `s106_stage`.
* **The memo:**
  * All eight V suites report `memo: off for this scorer (read_run is not one top-level def)`. For them the memo flag
    changes nothing but the control set.
  * The N runs used the memo, except `net112_nomemo`.

**Checker:** `accept3/check_accept_v3.py`, adapted from v2's `accept2/check_accept_v2.py`.
* **What it checks (unchanged from v2):**
  * the header names mutlib 3 with the expected sha;
  * every mutant is KILLED except the expected survivors, with nothing unresolved;
  * exactly three controls, all SURVIVED;
  * the tally agrees with the per-mutant lines;
  * the verdict line carries the counts.
* **New in v3:**
  * the set of SKIPPED mutants must equal the expected set, and every skip must be draft-only (the SKIPPED lines and the
    header's `draft-only:` line must agree);
  * the verdict line must read `N defined …, M skipped as draft-only`;
  * **row by row against the v2 reference report,** the same mutant names, and for every mutant the same verdict **and
    the same kill label** (the whole text between the verdict and the time). Controls are compared by verdict where the
    names agree. The control set depends on the memo decision, not on the harness version.
* **N mode (as in v1 and v2):** each `KILLED by <case>` must equal the EARLIEST, in suite order, of the cases the old
  harness listed.
  * The old lists come from `s106_stage/net112/mut_net112.out.txt` and `s106_stage/shn113/mut_shn113.out.txt`.
  * The suite order comes from `C:/kyty/s112/test_net112_sealed.out.txt` and `s106_stage/shn113/test_shn113.out.txt`.
* **The checker detects failures:** it was first run on the builder's v3 reports, and a deliberately wrong expectation
  (`--skipped x`) gave FAIL with 3 problems.

**Results (all `PASS … (0 problems)`, files `accept3/<run>.check.txt`):**
* **The eight V suites:** every row equals its v2 reference.
  * References: `accept2/*.report.txt` for check112, vdg112, vbn113b and vbn113c; `C:/kyty/s113/mut_*.out.txt` for
    vbn113d/e/f and check113.
  * check113's `gc_count` keeps its label `KILLED (crash: IndexError: list index out of range [check113.py:116])`.
  * vbn113c: `SURVIVORS: ['bad_race'] (42 of 43 selected mutants killed; 43 defined in the mutant script)`, exit 1. This
    is the known gap: the suite has no B1 fixture with races only.
* **net112:** 277 / 277 killed; 277 / 277 name the old earliest failing case.
  * Kill position: median 22 % / mean 31 % of the suite.
  * Controls: 189 s, `CONTROL_pass_end_of_read_run` 400 s (a memo miss on every parse), 189 s.
  * Baseline: 198.0 s on the cold v3 cache (hit_mem 48, hit_disk 2, miss 132).
  * Mutant timeout: 689 s. The slowest job took 400 s.
* **net112 `--no-memo`:** 277 / 277 killed and 277 / 277 earliest cases.
  * Its 277 verdict and label pairs are identical to the memo run's.
  * Controls: 395 / 386 / 397 s.
  * Baseline 194.1 s, timeout 582 s, slowest job 410 s.
* **net112 warm** (a timing rerun): 277 / 277 and 277 / 277 again.
  * Baseline 86.3 s (hit_mem 48, hit_disk 134, no miss).
  * Timeout 788 s.
* **shn113 (draft):** 310 / 310 killed; 310 / 310 name the old earliest failing case.
  * Kill position: median 21 % / mean 31 %.
  * Controls: 249 / 555 / 250 s.
  * Baseline: 265.5 s on the cold cache (miss 161). Timeout 903 s.
* **shn113 (SEALED), the new item:**
  * Header: `draft-only: 2 mutant(s) marked ['CONST_pred_bytes_prefilled', 'CONST_pred_sha_prefilled']; 2 skipped because
    the anchor is absent from this scorer (an unfilled seal)`.
  * The two lines `CONST_pred_sha_prefilled  SKIPPED (draft-only: its anchor is absent from this scorer)` and
    `CONST_pred_bytes_prefilled  SKIPPED (…)`.
  * 315 killed, exit 0: `ALL KILLED (315 of 315 selected mutants killed; 317 defined in the mutant script, 2 skipped as
    draft-only)`.
  * Controls 3 / 3: 273 s, `CONTROL_pass_end_of_read_run` 588 s, 274 s.
  * Baseline 119.6 s (warm: hit_mem 51, hit_disk 167). Timeout 1078 s.
  * **All 315 rows equal session 113's `C:/kyty/s113/mut_shn113.out.txt`**, verdict and label.
    * That run used v2, `--no-memo` and the derived `mut_shn113_sealed.py`.
    * So the marker reproduces the derived script exactly, and the memo changes no verdict or label here either.

## 2. Counter-examples: PASS

### 2a. review3 triples

**Runner:** `accept3/run_review3_a3.py`, adapted from the reviewer's `review3/run_review3.py` (not edited).
* **Same configurations, arguments and caches.** T5 `noctl_warm` reuses the cache of T5 `ctl_cold`.
* **Reference:** `adversarial/oldstyle.py`, unedited (sha256 `213d8168…`). For T4 the reference is `python mut_t4X.py`,
  the mutant script's own loop.
* **Stricter than the reviewer's runner.** A configuration PASSes only if all of these hold:
  * every verdict equals the old verdict, and no extra mutant runs;
  * with `--control`, all three controls survive;
  * the exit code matches (0 / 1);
  * T5 / T5b with the memo: the header shows `memo: read_run …` and nothing disables it (0 memo reruns);
  * every kill names the same case as the old output's first FAIL line. For `KILLED by exit 1 (first failing guard: X)`,
    that is X;
  * T4a / T4b: REFUSED with exit 3;
  * T4c: `skipped` becomes `SKIPPED`, exit 0, and the verdict line counts the filtered mutant.

Output: `accept3/out/review3_compare_v3.txt` (per-run reports in `accept3/out/r3/`).

| triple | hole (review3) | old method | v2 (review3 evidence) | **v3** | result |
|---|---|---|---|---|---|
| T1v `ctl` | MINOR 3 | `no_trailing_nl` S, `limit4` K (three) | `no_trailing_nl` K (false kill) | `no_trailing_nl` **S**, `limit4` K by three; exit 1; controls 3/3 | PASS |
| T1n `ctl` | MINOR 3 | same | same false kill | same as the old method | PASS |
| T2 `ctl` | MINOR 1 | `unsealed` S, `limit4` K (three) | `unsealed` K (false kill) | `unsealed` **S**; `limit4` K by exit 1 (first failing guard: three); no `fast:` line (fast off: the exit reads DRAFT) | PASS |
| T2 `nofast` | MINOR 1 | same | agreed | same | PASS |
| T3 `ctl` | MINOR 2 | `no_return` S, `limit4` K (three) | `no_return` K (false kill) | `no_return` **S**, `limit4` K by three | PASS |
| T3 `nofast` | MINOR 2 | same | agreed | same | PASS |
| T5 `ctl_cold` | **MAJOR-1** | `ge_equiv` S, `limit4` K (three) | NOT CERTIFIED; `ge_equiv` K by missing; 2 controls killed | `ge_equiv` **S**, `limit4` K by three; controls 3/3; **memo ON**, path-sensitive (`exc` used, line 14), memory only | PASS |
| T5 `noctl_warm` | **MAJOR-1** | same | REFUSED (the baseline failed from the cache) | same as the old method, memo ON | PASS |
| T5 `noctl_cold` | **MAJOR-1** | same | `ge_equiv` K (false kill) | same as the old method, memo ON | PASS |
| T5 `nomemo` | control | same | agreed | same | PASS |
| T5b `ctl_cold` | **MAJOR-1** | `report_fallback` K (missing), `legacy_on` S, `limit4` K | `report_fallback` S (false survivor), `legacy_on` K (false kill) | `report_fallback` K by missing, `legacy_on` **S**, `limit4` K by three; **memo ON**, path-sensitive (line 17) | PASS |
| T5b `nomemo` | control | same | agreed | same | PASS |
| T6 `ctl` | MINOR 5 | `lambda_wrap` S, `nest_bad` K (deep) | `lambda_wrap` K (RecursionError, false kill) | `lambda_wrap` **S**, `nest_bad` K by deep | PASS |
| T7 `ctl` | MINOR 4 | `trace_on` S, `limit4` K (three) | `trace_on` K (crash: `fileno`) | `trace_on` **S**, `limit4` K by three | PASS |
| T4a | **MAJOR-2** | `limit4` K, `limit2` K, `ge_equiv` **S** (second list EXTRA) | ALL KILLED (ran 2 of 3) | **REFUSED, exit 3**: `line 18: a (name, old, new)-shaped value outside the recognised MUTANTS definition (a second mutant collection?)` | PASS |
| T4b | **MAJOR-2** | same (list LATE merged into the jobs) | ALL KILLED (ran 2 of 3) | **REFUSED, exit 3** (line 24, the same message for M) | PASS |
| T4c | MINOR 6 | `limit4` K, `ge_equiv` skipped (own filter), `limit2` K: ALL KILLED | `ge_equiv` S (false survivor) | `ge_equiv` **SKIPPED**, others K; exit 0; `ALL KILLED (2 of 2 …; 3 defined in the mutant script, 1 skipped by the mutant script's own filter)`; controls 3/3 | PASS |

**SUMMARY: 17 configurations, 17 PASS, 0 FAIL.** All 16 kills that can be compared (every T1–T7 kill) name the old
first FAIL case. T4's reference prints no case names.

### 2b. The v2 counter-examples (both v1 reviews): the same 19 configurations / 23 runs as ACCEPTANCE_V2

**Runner:** `accept3/run_adv_a3.py`, which is `accept2/run_adv_v2.py` with its outputs redirected to `accept3/out/` and
`SKIPPED` added to its line pattern. It keeps the same 15 configurations of review 1, the four `review2/syn` suites, the
same arguments, repetitions and fresh caches, and the same reference (`adversarial/oldstyle.py`).

Output: `accept3/out/adv_compare_v3.txt`, with the reports in `accept3/out/adv/`.

**Result:** after normalising timings, the harness name (v2 / v3), dependency hashes and cache paths, the 94 comparison
lines are **identical** to `accept2/out/adv_compare_v2.txt` (0 differing lines, checked with difflib). In detail:

| config (criterion) | per mutant: old → v3 | as in the v2 acceptance |
|---|---|---|
| A, A2, B (N) | `lax` / `lax` / `min10` S → S; `strict` / `strict` / `nocont` K → K by large / large / joined | yes |
| C1 (V), C4 ×3 (V) | `ge_equiv` S → S; `limit4` K → K by good; memo OFF (`.append on notes`) | yes; no drift across the three C4 reps |
| D (V) | `row_re`, `two` K → K by good; memo OFF (`globals()`) | yes |
| E, E2 (V) | **REFUSED, exit 3** (item store / `.append`) | yes: refused by decision |
| F (N) | `version_always` K → K (exit 0 before the end of the suite); `neg_go` K → K by neg | yes |
| **K (V)** | `version_always` **S → K** (exit 0 before the end of the suite) | yes: **differs by decision** (v3 needs ALL OK + end of suite) |
| G (V) | `limit4` K → K by three; `limit2` K → K by two | yes |
| H (N) | `nocopy` S → S; `budget2` K → K by one | yes |
| **I (V)** | `detail_sym` **K (UnicodeEncodeError, cp1250) → S** with the summary `NOTE:` line; `limit4` K → K by three | yes: **differs by decision** (noted, not emulated) |
| J (V) | `ge_equiv`, `log_text` S → S; `limit4` K → K by three | yes |
| L4 ×3 (V) | `tag2`, `tag3` S → S; `limit4` K → K by three; `workers: FORCED TO 1` (the baseline wrote outside) | yes; no drift |
| S_late, S_setattr, S_pop (N) | `MODE_b` / `THRESH_2` / `MODE_b` S → S; kills by A / B_edge / A | yes |
| S_okfalse (N) | `MODE_b` S → S; `verdict_no` K → K by exit 1 (fast off: no `ok &=`) | yes: the same label as v2, not a wrong label |

**Totals:**
* **Runs:** 21 runs are not refused, holding 46 mutant verdicts. 44 equal the old method, and 2 differ as decided in v2
  (K, I). E and E2 are refused.
* **Labels:** every kill that names a case names the old first FAIL case. The one exit-code label (S_okfalse) is the
  same as in v2.
* **Controls:** 3 / 3 in all 20 runs that had controls.

### 2c. Memo probes (supplement)

**`accept3/memo_probes_a3.py`:** a copy of `accept2/memo_probes_v2.py` (review 2's P0–P8 sources verbatim) run against v3.
Output `accept3/out/probes.stdout.txt`.
* **0 failures:**
  * P0 and P7 are ON, and P7's dependency hash moves.
  * P1, P2a, P2b, P3a, P3b, P4a, P4b, P5 and P6 are OFF, each with a reason naming the construct.
  * P5b stays ON and its hash moves.
  * P8: the keys for missing, directory and empty file all differ.

### 2d. New probes written for this acceptance (supplement, not in the task list)

These shapes are not the builder's (`v3check/`) and not the reviewer's. They aim at the two MAJOR fixes.

* **MAJOR-1 path analysis:** `accept3/probe_path_a3.py`, output `accept3/out/probe_path.txt`.
  * **Method:** 11 variants of a T5-like `read_run` are planned with v3's `plan_memo`. A plan is unsafe only if the memo
    is ON, `log_path` is keyed by type and bytes only, and the plan is path-insensitive while the result depends on the
    path in a form the runtime backstop cannot see.
  * **Result: 0 unsafe, 0 relying on the backstop.**
    * The controls (Q0: a constant message; Q3: `exc.errno`) stay ON and path-insensitive, as intended.
    * These are ON and **path-sensitive**: `str(exc)` (Q1), `exc.filename` (Q2), `fh.name` (Q5), the exception rebound
      to another name and then `len(str(e2))` (Q9), and `len(repr(exc.args))` (Q10).
    * The parameter formatted into the message (Q4) is OFF: `open()` other than reading a file parameter.
    * The exception caught in a module-level helper that calls a lambda or a nested def which opens the file (Q6–Q8,
      including a `len(str(e))` result no backstop could see) is OFF: `guard: calls the local value f`.
* **MAJOR-2 harness part:** `accept3/probe_m4/mut_r*.py` on `review3/sc_t4.py` / `test_t4.py`, output
  `accept3/out/probe_m4.txt`.
  * **Method:** each script's own loop is the reference, and every script runs a mutant mutlib's recognised list does
    not show.
  * **Result: all six are REFUSED with exit 3.**
    * r1: a second list built by `str.split`, looped with `itertools.chain(MUTANTS, EXTRA)`. Refused as "MUTANTS is used
      in a way that may change it (Call)".
    * r2: a second collection from `json.loads`, with its own loop. Refused as "does not take its old / new text from
      one element".
    * r3: a helper `job()` called from the loop and also with `*'…'.split('|')`. Refused, same reason.
    * r4: `MUTANTS.extend(...)` after a helper def. Refused (`.extend`).
    * r5: a loop over `MUTANTS + [...]` with the loop variables rebound. Refused (BinOp).
    * r6: the loop rebinds `new` for one mutant, so the old method's `limit2` survives. Refused.
  * Where the old method differs (a survivor mutlib would not have seen), v3 refuses and does not guess.

## 3. Timings

Walls are measured outside the harness by the chain scripts. Worker time and per-job times come from the reports. The
table below is `accept3/out/timing_tables.md`, generated by `accept3/timing_tables.py` from those files.

### V suites (28 workers, `--control`; two passes, v3 first in pass 1, v2 first in pass 2)

| suite | v3 wall pass 1 / 2 | v2 wall pass 1 / 2 | v3 / v2 wall (sum of both passes) | v3 / v2 worker time (sum) | v3 / v2 median job | v3 baseline | earlier v2 wall (acceptance / session 113) |
|---|---|---|---|---|---|---|---|
| check112 | 3.4 / 3.4 s | 3.1 / 7.4 s | 0.648 | 0.841 | 0.900 | 0.7 s | 3.2 s (acc.) |
| vdg112 | 18.8 / 18.9 s | 18.9 / 20.3 s | 0.962 | 0.959 | 0.944 | 7.2 s | 18.7 s (acc.) |
| vbn113b | 28.4 / 27.3 s | 27.2 / 27.3 s | 1.022 | 1.006 | 0.995 | 10.2 s | 27.0 s (acc.) |
| vbn113c | 31.9 / 31.3 s | 30.2 / 29.7 s | 1.055 | 1.013 | 0.993 | 13.0 s | 29.4 s (acc.) |
| vbn113d | 30.9 / 30.8 s | 29.5 / 29.4 s | 1.048 | 1.002 | 0.992 | 11.0 s | 36.0 s (s113, internal) |
| vbn113e | 35.8 / 34.4 s | 33.6 / 36.0 s | 1.009 | 0.973 | 0.956 | 12.3 s | 36.4 s (s113, internal) |
| vbn113f | 40.4 / 41.1 s | 39.2 / 40.6 s | 1.021 | 0.999 | 0.986 | 13.8 s | 45.9 s (s113, internal) |
| check113 | 4.5 / 4.5 s | 4.3 / 4.3 s | 1.047 | 0.921 | 0.929 | 1.1 s | 4.7 s (s113, internal) |
| **all eight** | 385.8 s | 381.0 s | **1.013** | | | | |

(check112's v2 7.4 s in pass 2 was the first step after the 23-minute v2 net112 run; its other three walls are 3.1–3.4 s.)

### N suites (28 workers, `--control`)

| run | memo cache | v3 wall | v3 worker time | v3 baseline | v3 median mutant | v2 reference | v2 wall | v2 worker | v2 baseline | v3 / v2 wall | v3 / v2 median job |
|---|---|---|---|---|---|---|---|---|---|---|---|
| net112 | cold (first v3 run) | 1526.3 s | 36655 s | 198.0 s | 109.9 s | accept2/net112 (warm, 2026-09-24) | 1267.7 s | 32446 s | 85.1 s | 1.204 | 1.147 |
| net112_warm | warm | 1298.0 s | 33333 s | 86.3 s | 91.4 s | accept2/net112 (warm, 2026-09-24) | 1267.7 s | 32446 s | 85.1 s | 1.024 | 0.979 |
| net112_warm | warm | 1298.0 s | 33333 s | 86.3 s | 91.4 s | **accept3/v2t/net112_v2 (warm, same day)** | 1365.4 s | 35169 s | 87.1 s | **0.951** | 0.917 |
| net112_nomemo | `--no-memo` | 2016.7 s | 50634 s | 194.1 s | 147.2 s | accept2/net112_nomemo | 2006.6 s | 50274 s | 197.1 s | 1.005 | 1.001 |
| shn113 (draft) | cold | 2040.4 s | 49226 s | 265.5 s | 130.7 s | accept2/shn113 (cold) | 2062.6 s | 49618 s | 263.5 s | 0.989 | 0.978 |
| shn113s (sealed) | warm (the builder's smoke run) | 2206.3 s | 57126 s | 119.6 s | 160.1 s | s113 `mut_shn113.out.txt` (`--no-memo`, derived script) | 3217.5 s | 81938 s | 272.0 s | 0.686 | 0.797 |

(Worker time is the report's `worker time` line, which includes the baseline and the controls. ACCEPTANCE_V2 quoted the
mutants alone, for example 31 559 s for net112.)

**Findings (none is a correctness problem):**
1. **v3 costs the same as v2.**
   * V suites: 1.013× wall and 0.96–1.01× worker time over both orders.
   * N suites: the same-day A/B on net112 with a warm cache, the cleanest comparison, gives v3 0.951× v2's wall and
     0.917× its median job. `--no-memo` gives 1.005 / 1.001, and shn113 cold gives 0.989 / 0.978.
   * v3's compile-once and real-file capture neither gain nor lose measurably on these suites. Their jobs are dominated
     by the scorer and by fixture I/O.
2. **The first v3 net112 run was 20 % slower than v2's acceptance run.**
   * The v3 cache was cold, because the harness version is part of the dependency hash, so v2's warm entries are never
     read. That added a 198 s baseline instead of 85 s.
   * Its jobs were also 15 % slower (median job 1.147×), and the cause was not isolated. The effect was not reproduced:
     * the warm rerun one hour later was 0.979× v2's acceptance per job;
     * shn113 on an equally cold cache was 0.978×;
     * and v2 itself, run the same day, was slower than v3.

     So it is run-to-run variation of the machine (disk and file cache), not v3.
   * The Memo class differs from v2's only by the path key for path-sensitive plans, the stat-error key and the
     backstop on misses. On a hit of a path-insensitive plan it does what v2 did. `CONTROL_pass_end_of_read_run`, which misses
     on every parse, took 400 s in both v3 runs against 410 s in v2's acceptance.
3. **The sealed shn113 now runs with the memo** (session 113 had to use `--no-memo` with a derived script): 2206 s against
   3217.5 s, 0.686×.
   * That v2 figure is session 113's own internal wall, taken under that session's machine state.
   * The ratio is the memo's gain, not v3's. Compare the draft shn113's 2040 s, which has 310 mutants and a cold cache.
4. **Timeout margins, slowest job against its timeout:**
   * net112: 400 of 689 s;
   * `--no-memo`: 410 of 582 s;
   * shn113: 555 of 903 s;
   * sealed shn113: 588 of 1078 s.

   As in v2, a timeout is UNRESOLVED, never a kill.
5. **Against the old harness,** the speed-ups are as in v2: about 5× on the N suites and 6–16× on the V suites. ROADMAP
   item 7's target of ≤ 10 min per N suite is still not met (net112 21.6 min warm, shn113 34 min). v3 was not meant to
   change that.

## Housekeeping

* **Files written, all under `C:/kyty/s106_stage/mutlib/`:**
  * `ACCEPTANCE_V3.md`;
  * a changelog entry in `README.md`;
  * the folder `accept3/`:
    * the scripts `chain.sh`, `chain2.sh`, `check_accept_v3.py`, `run_review3_a3.py`, `run_adv_a3.py`,
      `memo_probes_a3.py`, `probe_path_a3.py`, `timing_tables.py`, `probe_m4/mut_r*.py`;
    * the marked copy `mut_shn113_marked.py`;
    * the reports, logs, checks and walls, including `v2t/` and `timing2/`;
  * v3 cache entries (132 in `cache/net112`; 161 in `cache/shn113` for the draft, beside the builder's 165 for the
    sealed scorer) and the updated `cache/*/durations.json`.
* **Where the scripts come from:**
  * `accept3/mut_shn113_marked.py` and `accept3/run_adv_a3.py` were found already in `accept3/` from an earlier,
    interrupted start of this acceptance (01:07).
  * The marked copy was verified to differ from the project file only by the two markers.
  * The runner was verified to differ from `accept2/run_adv_v2.py` only by paths, names and the SKIPPED pattern. Only its
    docstring was corrected.
  * The dry-run output `accept3/out/shn113_sealed_marked.dryrun.stdout.txt` is from that start.
* **Disk:**
  * `cache/net112` holds 2.4 GiB: 0.79 GiB of v3 entries (written 2026-09-25) and 1.58 GiB of older ones.
  * `cache/shn113` holds 4.4 GiB: 2.22 GiB of v3 entries and 2.15 GiB of older ones.
  * The older v1 / v2 entries are never read by v3 (the harness version is in the key) and can be deleted.
* **Scratch removed:**
  * `adversarial/old_work`, `adversarial/fx_*` and `review2/syn/fx`;
  * `review3/fx_*` and `review3/mut_t4?_work` (created by the references);
  * the runners' `accept3/cache_*` and `accept3/work`;
  * the probe work directories.

  mutlib removed its own job directories: no `WARNING could not remove` line appears in any report. `work/probe` and
  `work/verify` were there before this acceptance and were left alone.
* **Nothing else touched:**
  * No scorer, test, mutant script, review file, `mutlib.py`, `mutlib_v2.py` or `mutlib_v1.py` was edited. Their sha256
    values are in the report headers.
  * `C:/kyty/s113` was only read, and `C:/kyty/s114` was not touched.
  * No build, no game or emulator run, no git command.
* **No background processes remain.**
