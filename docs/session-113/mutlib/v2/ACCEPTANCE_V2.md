# mutlib v2 acceptance (2026-09-24, ROADMAP §0.1 session 113 item 13)

**Harness:** `C:/kyty/s106_stage/mutlib/mutlib.py`, sha256 **`877eb53a9d939293308fd4bcbce2764606f42a9c1f0d6df4282923db529a6108`**.
Every check below passed on the first try, so mutlib.py was **not changed**. Every report carries this sha in its header,
and `accept2/check_accept_v2.py` verifies it. `mutlib_v1.py` is unchanged (sha256 `db8703bd…`).

**Verdict: PASS.**
* **Item 1 (reviewer counter-examples):** v2 gives the old method's verdict on every mutant, with three kinds of exception.
  All three are required by the item 13 decision itself:
  * E and E2 are refused, as strict extraction requires.
  * K is stricter than the old V rule. The decision requires exit 0 plus an ALL OK line plus the end of the suite.
  * I is noted, not emulated, as the decision requires for the console encoding.
* **Item 2 (six real suites):** every mutant gets its v1 verdict.
  * All controls survive.
  * net112 and shn113 name the earliest old failing case for 277 / 277 and 310 / 310 mutants.
  * vbn113c keeps the known survivor `bad_race`.
* **Item 3 (wall times):** recorded below. v2 is correct but slower than v1 on the N suites, because hoisting was removed
  (see §3).

**How the runs were done:**
* **One suite at a time,** with nothing else running on the machine (CPU idle before the start).
* **Sealed-run lock:** `C:/kyty/SEALED_RUN.lock` was absent throughout. The chain `accept2/chain.sh` checks for it before
  every step.
* **Workers and flags:** 28 workers on 32 threads, mutlib's default, unless a row says otherwise. Every real-suite run used
  `--control`.
* **Where the output is:** reports, stdout, stderr and the externally measured wall time are in `accept2/<suite>.*`. The
  per-report checks are in `accept2/<suite>.check.txt`.
* **Environment:** Python 3.13.13, `PYTHONIOENCODING` and `PYTHONUTF8` unset (old console encoding cp1250).

## Summary table

| suite | scorer (sha256 prefix) | mutants | v2 result | controls | first failing case vs old harness | v2 wall | v1 wall | old harness wall |
|---|---|---|---|---|---|---|---|---|
| net112 | `s106_stage/net112.py` draft (`566c8bf1`) | 277 | **277 killed** | 3 / 3 survived | **277 / 277** equal the earliest old case | **1267.7 s** (21.1 min), warm v2 cache | 778 s | ≈ 6300 s (1 h 45 min) |
| net112 `--no-memo` | same | 277 | **277 killed** | 3 / 3 survived | **277 / 277** | **2006.6 s** (33.4 min) | not run in full | — |
| shn113 | `s106_stage/shn113.py` (`026fae4f`) | 310 | **310 killed** | 3 / 3 survived | **310 / 310** equal the earliest old case | **2062.6 s** (34.4 min), cold v2 cache | 1186 s (cold) | ≈ 3 h |
| vbn113b | `s113/vbn113b.py` sealed (`688db5fc`) | 41 | **41 killed** | 3 / 3 | (not required; labels = v1's on 44 / 44 rows) | 27.0 s | 19.2 s | ≈ 7.0 min |
| vdg112 | `s106_stage/vdg112.py` (`7d44c5b6`) | 36 | **36 killed** | 3 / 3 | (labels = v1's on 39 / 39 rows) | 18.7 s | 13.5 s | ≈ 4.3 min |
| check112 | `s106_stage/check112.py` (`829cb59f`) | 24 | **24 killed** | 3 / 3 | (labels = v1's on 27 / 27 rows) | 3.2 s | 3.0 s | ≈ 19 s |
| vbn113c | `s113/vbn113c.py` sealed (`834044de`) | 43 | **42 killed + `bad_race` SURVIVED** (known) | 3 / 3 | (labels = v1's on 46 / 46 rows) | 29.4 s | 21.1 s | never run (≈ 8 min) |

**Totals over all seven runs:**
* 0 unresolved (timeout, harness error, environment, not reproduced).
* 0 kills by a crash of the suite, 0 confirmation reruns, 0 memo reruns and 0 "rerun alone".
* No run forced to one worker, no memo disabled at run time, no job directory left behind.
* Fast mode was confirmed by the baseline in every run.

The verdict line of every report carries the counts, for example `ALL KILLED (277 of 277 selected mutants killed; 277 defined in
the mutant script)`. The test and mutant scripts are byte-identical to those of the v1 acceptance (sha256 in each report
header).

## 1. Counter-examples from both reviews: PASS

**Runner:** `accept2/run_adv_v2.py`.
* **Where it comes from:** an adaptation of `adversarial/run_all.py`, the reviewer's runner. That file and everything else
  in `adversarial/` and `review2/` are left unedited.
* **Configurations and arguments:** the same 15 configurations, with the same mutlib arguments, repetitions and fresh
  caches, plus the four `review2/syn` suites.
* **Reference:** the reviewer's own `adversarial/oldstyle.py`, unchanged (sha256 `213d8168…`). It runs a fresh `python -B`
  subprocess per mutant on the original test text and applies the old V and N criteria. It shares no code with mutlib.
* **What it compares, per mutant:**
  * the verdict under the configuration's old criterion;
  * for mutants both sides kill, the old first line with a FAIL token against v2's `KILLED by <case>`.

Output: `accept2/out/adv_compare_v2.txt`; the individual reports are in `accept2/out/adv/`.

**Result over 19 configurations and 23 runs (C4 and L4 three times each):**
* **Verdicts:** 21 runs are not refused, holding 46 mutant verdicts. 44 equal the old method; 2 differ as the decision
  requires (K, I).
* **Refusals:** 2 runs are REFUSED (E, E2), as required.
* **Kill labels:** all 22 kills that name a case name the same case as the old first FAIL line.
* **Controls:** every control survived, 3 / 3, in all 20 runs that had controls.
* **No drift between repetitions:** the repetitions of C4 and L4 are identical. v1's outcomes varied between repetitions
  (C4: SURVIVORS / NOT CERTIFIED / ALL KILLED; L4: SURVIVORS twice, ALL KILLED once).

| config | old criterion | mutlib args | per mutant: old → v2 | result |
|---|---|---|---|---|
| A (setattr after 1st case) | N | `-w 2 --control` | `lax` SURVIVED → SURVIVED; `strict` KILLED (large) → KILLED by large | agree (v1: false kill of `lax`) |
| A2 (helper sets `mod.STRICT`) | N | `-w 2 --control` | `lax` S → S; `strict` K (large) → K by large | agree (v1: false kill) |
| B (file written after the case) | N | `-w 2 --control` | `min10` S → S; `nocont` K (joined) → K by joined | agree (v1: false kill) |
| C1 (read_run mutates a parameter) | V | `-w 1`, fresh cache | `ge_equiv` S → S; `limit4` K (good) → K by good | agree; memo OFF (`.append on notes`) |
| C4 ×3 | V | `-w 4 --control`, fresh cache | each rep: `ge_equiv` S → S; `limit4` K (good) → K by good | agree ×3 (v1: ALL KILLED / SURVIVORS / NOT CERTIFIED) |
| D (globals()-generated regexes) | V | `-w 1 --control`, fresh cache | `row_re` K (good) → K by good; `two` K (good) → K by good | agree; memo OFF (`globals()`) (v1: `row_re` survived) |
| E (MUTANTS.append in loops, `MUTANTS[0]=`) | V | `-w 2 --control` | old: `limit5` K, `text_NOTE` S, `text_MODE` S, `mode_lax` S; v2: **REFUSED** (exit 3; item store and .append named) | refused by decision (v1: ran 1 of 4, ALL KILLED) |
| E2 (`M['x']=`, `M.update`) | V | `-w 2 --control` | old: `limit4` K, `text_NOTE` S, `mode_lax` S; v2: **REFUSED** (exit 3) | refused by decision (v1: ran 1 of 3) |
| F (exit 0 mid-suite, "ALL OK (3 cases)") | N | `-w 2 --control` | `version_always` K (rc 0, no ALL OK) → K (exit 0 before the end of the suite); `neg_go` K (neg) → K by neg | agree (v1: `version_always` survived) |
| K (the same, V family) | V | `-w 2 --control` | `version_always` **S (rc 0) → K** (exit 0 before the end of the suite); `neg_go` K (neg) → K by neg | **differs by decision:** v2 requires ALL OK + end of suite; the old N criterion also calls it KILLED |
| G (helper-module cache) | V | `-w 1 --control` | `limit4` K (three) → K by three; `limit2` K (two) → K by two | agree (v1: both survived) |
| H (lru_cache state) | N | `-w 2 --control` | `nocopy` S → S; `budget2` K (one) → K by one | agree (v1: false kill of `nocopy`) |
| I (U+2265 in output) | V | `-w 2 --control` | `detail_sym` **K (UnicodeEncodeError, cp1250) → S** with the note "printed '\u2265' … cp1250 cannot encode"; `limit4` K (three) → K by three | **differs by decision:** encoding noted, not emulated; summary `NOTE:` line present |
| J (logging handle blocks rmtree) | V | `-w 4 --control` | `ge_equiv` S → S; `log_text` S → S; `limit4` K (three) → K by three | agree (v1: false crash kills) |
| L4 ×3 (seal outside BASE) | V | `-w 4 --control` | each rep: `tag2` S → S; `tag3` S → S; `limit4` K (three) → K by three; header `workers: FORCED TO 1 - the baseline wrote outside its job directory: [...fx_l_aux, ...seal.md]` | agree ×3 (v1: false kills in every rep) |
| S_late (name bound after its case) | N | `-w 2 --control` | `MODE_b` S → S; `verdict_no` K (A) → K by A | agree (v1: false kill of `MODE_b`) |
| S_setattr | N | `-w 2 --control` | `THRESH_2` S → S; `ge_gt` K (B_edge) → K by B_edge | agree, including the label (v1: false kill, wrong label A) |
| S_okfalse (`if not passed: ok = False`) | N | `-w 2 --control` | `MODE_b` S → S; `verdict_no` K (A) → K by exit 1 | agree; fast OFF (no `ok &=`), so the label is the exit code, not a case: not a wrong label |
| S_pop (`cases.pop()`) | N | `-w 2 --control` | `MODE_b` S → S; `verdict_no` K (A) → K by A | agree |

(`-w` = `--workers`. For every config the mutant scripts, scorers and tests are the reviewers' files.)

**Supplement: review 2's static memo probes P0–P8.**
* **Script:** `accept2/memo_probes_v2.py`, output `accept2/out/memo_probes_v2.txt`. P0–P7 use the reviewer's sources verbatim.
  v1's `Memo.key` no longer exists, so P8 is keyed through v2's `Memo.state`.
* **Result: 0 failures.**
  * P0 (the plain read_run) is ON.
  * P1, P2a, P2b, P3a, P3b, P4a, P4b, P5 and P6 are OFF, each with a reason naming the construct.
  * P5b (a store into a dependency) stays ON and its dependency hash moves.
  * P7 (control) stays ON and its hash moves.
  * P8: the keys for a missing path, a directory and an empty file are all different.

## 2. Real suites: PASS

**Commands** (from `C:/kyty/s106_stage/mutlib`, via `accept2/chain.sh`, one step at a time):
```
mutlib.py --scorer ../check112.py --test ../test_check112.py --mutants ../mut_check112.py --control
mutlib.py --scorer ../vdg112.py --test ../test_vdg112.py --mutants ../mut_vdg112.py --control
mutlib.py --scorer C:/kyty/s113/vbn113b.py --test ../test_vbn113b.py --mutants ../mut_vbn113b.py --control
mutlib.py --scorer C:/kyty/s113/vbn113c.py --test ../test_vbn113c.py --mutants ../mut_vbn113c.py --control
mutlib.py --scorer ../net112.py --test ../test_net112.py --mutants ../mut_net112.py --control
mutlib.py --scorer ../shn113.py --test ../test_shn113.py --mutants ../mut_shn113.py --control
mutlib.py --scorer ../net112.py --test ../test_net112.py --mutants ../mut_net112.py --control --no-memo
```

**Checker:** `accept2/check_accept_v2.py`, adapted from v1's `accept/check_accept.py`. It adds `UNRESOLVED` and v2's
verdict and tally formats. It checks:
* the header names mutlib 2 with the expected sha;
* every mutant is KILLED except the expected survivors;
* the three controls are SURVIVED;
* the tally agrees with the per-mutant lines;
* the verdict line carries the expected counts (selected = defined = the script's count);
* N mode also:
  * the name sets equal the old harness's;
  * each `KILLED by <case>` equals the earliest, in suite order, of the cases the old harness listed.

  The old lists come from `net112/mut_net112.out.txt` and `shn113/mut_shn113.out.txt`. The suite order comes from
  `C:/kyty/s112/test_net112_sealed.out.txt` and `shn113/test_shn113.out.txt`.

**Results (all `PASS … (0 problems)`):**
* **net112:** 277 / 277 killed; first failing case 277 agree, 0 mismatch, 0 unknown.
  * Kill position: median 22 % / mean 31 % of the suite.
  * Controls: `CONTROL_comment_after_docstring` 197 s, `CONTROL_pass_end_of_read_run` 410 s (misses the memo on every
    parse), `CONTROL_module_pass_at_end` 194 s.
  * Baseline: 85.1 s on the warm v2 cache (hit_mem 48, hit_disk 134), no violation.
  * Mutant timeout: 762 s.
* **net112 `--no-memo`:** 277 / 277 killed, 277 / 277 first failing case.
  * All 277 verdict and label pairs are identical to the memo run.
  * Controls: `CONTROL_pass_end_of_evaluate` replaces the read_run control; all 3 survived (≈ 400 s each).
  * Baseline: 197.1 s. Timeout: 591 s.
* **shn113:** 310 / 310 killed; first failing case 310 agree, 0 mismatch, 0 unknown.
  * Kill position: median 21 % / mean 31 %.
  * Controls: all 3 survived (`CONTROL_pass_end_of_read_run` 578 s).
  * Baseline: 263.5 s with the v2 cache cold (miss 161, hit_disk 2, hit_mem 48), no violation.
  * Timeout: 896 s.
* **Same verdicts and labels as v1:** net112 280 / 280 and shn113 313 / 313 rows (mutants and controls) carry the same
  verdict and the same kill label as v1's accepted reports (`accept/*.report.txt`). The same holds for the V suites (27 /
  39 / 44 / 46 rows).
* **vbn113c:** 42 killed, `bad_race` SURVIVED, exit 1, `SURVIVORS: ['bad_race'] (42 of 43 selected mutants killed; 43
  defined in the mutant script)`.
  * The report is saved as **`mutlib/mut_vbn113c_v2.out.txt`** (a copy of `accept2/vbn113c.report.txt`).
  * The gap is the one v1's acceptance established with an independent runner: no B1 fixture with races only.
  * vbn113c stays not certified until the suite gets that fixture.

## 3. Wall times

| suite | old harness | v1 | **v2** | v2 / v1 | old / v2 | v2 mutant time (sum, median) | v1 mutant time (sum, median) |
|---|---|---|---|---|---|---|---|
| check112 | ≈ 19 s | 3.0 s | **3.2 s** | 1.07 | ≈ 6× | — | — |
| vdg112 | ≈ 4.3 min | 13.5 s | **18.7 s** | 1.39 | ≈ 14× | — | — |
| vbn113b | ≈ 7.0 min | 19.2 s | **27.0 s** | 1.41 | ≈ 16× | — | — |
| vbn113c | never run (≈ 8 min) | 21.1 s | **29.4 s** | 1.39 | ≈ 16× | — | — |
| net112 | ≈ 6300 s | 778 s | **1267.7 s** (21.1 min) | **1.63** | ≈ 5.0× | 31 559 s, 93.9 s | 18 306 s, 42.2 s |
| net112 `--no-memo` | — | — | **2006.6 s** (33.4 min) | — | ≈ 3.1× | 48 879 s, 143.9 s | — |
| shn113 (cold cache) | ≈ 10 800 s | 1186 s (cold) | **2062.6 s** (34.4 min) | **1.74** | ≈ 5.2× | 48 265 s, 137.2 s | 27 925 s, 82.5 s |

The wall is measured outside the harness (`accept2/<suite>.wall.txt`). Old-harness figures are the ones in `ACCEPTANCE.md`.

**Findings for the executor (none is a correctness problem):**
1. **Removing hoisting costs about 1.7× on the N suites.**
   * The item 13 premise "no gain: 147 s without against 170 s with" came from the wall time of a 20-mutant subset. On that
     subset the wall is bounded by the baseline, which hoisting evaluated twice.
   * On the full runs, the mutant time grows 1.72× (net112) and 1.73× (shn113), because every job writes all fixtures
     before the final loop.
   * v1's `ACCEPTANCE.md` §5 had already shown this on the same subset (807 s against 1507 s of mutant time).
   * As a result, net112 takes 21 min and shn113 34 min. ROADMAP item 7's target (≤ 10 min) is not met by v2, and v1 did not
     meet it either (13 / 20 min).
   * v2 is still about 5× faster than the old harness on the N suites and 6–16× faster on the V suites.
   * Getting the speed back without the false-kill risk would need a new decision, for example early exit inside the
     original final loop only plus cheaper fixture writing. That is outside this acceptance.
2. **The parse memo is worth 1.58× wall on net112** (1268 s against 2007 s) and 1.55× mutant time. It raised no runtime
   guard violation in 280 + 313 jobs.
3. **Timeout margins are sufficient but not wide.**
   * The per-job timeout comes from a baseline that runs alone, while jobs run 28 at a time and slow down about 2×.
   * Slowest job against its timeout:
     * net112: 410 s of 762 s;
     * `--no-memo`: 406 s of 591 s;
     * shn113: 578 s of 896 s.
   * A timeout is reported as UNRESOLVED and never as a kill. So a tighter margin could only turn a certified run into
     NOT CERTIFIED (exit 2), never produce a false kill.
4. **The V-suite walls grow by about one baseline**, because the baseline now runs alone. The worker time stays the same
   or lower (for example vbn113c 414.6 s against v1's 438.1 s).
5. **Disk:** the shn113 parse cache is now warm under v2. `cache/shn113` is 2.2 GB, including v1's 1.1 GB of entries, which
   are never read again and can be deleted. `cache/net112` is 1.6 GB.

## Housekeeping

* **Files written, all under `C:/kyty/s106_stage/mutlib/`:**
  * `ACCEPTANCE_V2.md` and `mut_vbn113c_v2.out.txt`;
  * the new folder `accept2/`: the scripts `run_adv_v2.py`, `memo_probes_v2.py`, `check_accept_v2.py` and `chain.sh`,
    plus the reports, logs and checks;
  * v2 cache entries in `cache/shn113` and the updated `cache/*/durations.json`;
  * a changelog entry in `README.md`.
* **Scratch removed:** `adversarial/old_work`, `adversarial/fx_*` and `review2/syn/fx` (created by `oldstyle.py` and by the
  fixed-BASE suites), `accept2/work` and `accept2/cache_*`. mutlib removed its own work directories; no `WARNING could not
  remove` line appears in any report.
* **Nothing else touched:** no scorer, test, mutant script, review file or `mutlib.py` was edited; their sha256 values are
  in the report headers. No build, no game or emulator run, no git command that changes state.
* **No background processes remain.**
