# mutlib acceptance (2026-09-24)

**Harness:** `C:/kyty/s106_stage/mutlib/mutlib.py`, sha256 `db8703bdf0820c9023e9f1a9d69ddfae6fddc00b8035d0294704b85115de00fb`.
Every check passed on the first try, so mutlib.py was not changed. Each report below carries this sha in its header.

**How the runs were done:**
* One suite at a time, with nothing else running.
* `C:/kyty/SEALED_RUN.lock` was absent throughout.
* 28 workers on 32 threads (mutlib's default), unless a row says otherwise.
* Every acceptance run used `--control`.
* Reports, stdout and stderr are in `accept/<suite>.*`.
* The per-report checker is `accept/check_accept.py`, and its output is in `accept/<suite>.check.txt`.

## Results

| suite | scorer (sha256 prefix) | mutants | killed | survived | controls survived | first failing case vs old harness | mutlib wall | old harness wall |
|---|---|---|---|---|---|---|---|---|
| net112 | `s106_stage/net112.py` draft (`566c8bf1`) | 277 | 277 | 0 | 3 / 3 | **277 / 277** equal the earliest old case, 0 mismatches | **778 s** (13.0 min) | about 1 h 45 min |
| shn113 | `s106_stage/shn113.py` (`026fae4f`) | 310 | 310 | 0 | 3 / 3 | **310 / 310** equal the earliest old case, 0 mismatches | **1186 s** (19.8 min), cold parse cache | about 3 h |
| vbn113b | `s113/vbn113b.py` sealed (`688db5fc`) | 41 | 41 | 0 | 3 / 3 | (not required) | 19.2 s | about 7.0 min |
| vdg112 | `s106_stage/vdg112.py` (`7d44c5b6`) | 36 | 36 | 0 | 3 / 3 | (not required) | 13.5 s | about 4.3 min |
| check112 | `s106_stage/check112.py` (`829cb59f`) | 24 | 24 | 0 | 3 / 3 | (not required) | 3.0 s | about 19 s |
| vbn113c | `s113/vbn113c.py` sealed (`834044de`) | 43 | 42 | **1: `bad_race`** | 3 / 3 | (not required) | 21.1 s | never run (about 8 min) |

In every run, 0 mutants were unresolved (timeout or harness error), 0 needed a faithful rerun and 0 were killed by a crash of the
suite. For net112 and shn113, no kill was found only in the final loop.

Mutlib wall is measured outside the harness (`accept/<suite>.wall.txt`). Where the old-harness figures come from:
* **net112:** 205 s baseline plus 97 620 s of mutant time over 16 lanes, from `net112/mut_net112.out.txt`.
* **shn113:** `s113/FACTS.md` gives about 3 h: a 267 s baseline plus 154 764 s of mutant time.
* **V suites:** serial old-style reruns by the builder, recorded in `README.md`. My 3 reference reruns of vbn113c took 10.9 s per
  mutant, which matches.

## 1. net112: PASS

* **Command:**
  ```
  mutlib.py --scorer ../net112.py --test ../test_net112.py --mutants ../mut_net112.py --control --out accept/net112.report.txt
  ```
* **Test and mutant script:** test `956397b4`, mutant script `08d91193`. Both are identical to their `C:/kyty/s112` copies.
* **Why the draft scorer:** it is the one the old run used. On the sealed copy two anchors do not exist
  (`CONST_pred_sha_prefilled`, `CONST_pred_bytes_prefilled`), so that copy cannot carry all 277 mutants.
* **Kills:** all 277 mutants killed.
* **Controls:** all 3 survived: `CONTROL_comment_after_docstring` 322 s, `CONTROL_pass_end_of_read_run` 693 s (it misses the
  parse memo by construction), `CONTROL_module_pass_at_end` 321 s.
* **Baseline:** passed in hoisted mode in 317 s. All 205 hoisted checks ran, and the lines they printed equal the final-loop lines.
* **First failing case:**
  * The suite order is the order of the 205 case lines in `C:/kyty/s112/test_net112_sealed.out.txt`.
  * For every mutant, the old harness lists the failing cases (`'  PROBLEMS '` lines) in `net112/mut_net112.out.txt`. The
    earliest of them in suite order must equal mutlib's `KILLED by <case>`.
  * Result: **277 agree, 0 mismatch, 0 names missing from the suite order.** The mutant name sets are identical.
  * Every old list was already in suite order.
* **Kill position:** the killing case sits at a median 22 % / mean 31 % of the suite.

## 2. shn113: PASS

* **Command:** the same, with `../shn113.py`, `../test_shn113.py` (`0dc13f98`) and `../mut_shn113.py` (`01599013`). These files
  have not changed since the old run: they were written at 09:34, and the old output at 12:12.
* **Kills:** all 310 mutants killed.
* **Controls:** all 3 survived (`CONTROL_pass_end_of_read_run` took 931 s).
* **Baseline:** passed in hoisted mode in 665 s, with all 235 hoisted checks. The parse cache started empty. The baseline and the
  first mutants filled it; the baseline's memo tally was hit_disk 167, miss 158.
* **First failing case:** the suite order is the 235 case lines of `shn113/test_shn113.out.txt`. Result: **310 agree, 0 mismatch,
  0 unknown.** The name sets are identical.
* **Kill position:** median 20 % / mean 30 % of the suite.

## 3. vbn113b, vdg112, check112: PASS

All mutants were killed (41 / 36 / 24) and all 3 controls survived in each suite. vbn113b ran on the sealed copy. vdg112 ran on
the `s106_stage` draft, as specified; its sealed copy `s112/vdg112.py` differs only in `PRED_SHA` / `PRED_BYTES`, and all 36
anchors are unique on that copy too.

## 4. vbn113c (sealed, first mutation pass): 42 of 43 killed, `bad_race` SURVIVES

* **Report:** saved as `mutlib/mut_vbn113c.out.txt`, a copy of `accept/vbn113c.report.txt`.
* **Mutant count:** `mut_vbn113c.py` defines **43** mutants, not 44. Its `MUTANTS` list literal has 43 entries (counted with
  `ast`), with no duplicates, and all 43 anchors are unique on the sealed scorer.
* **The survivor is real, not a harness artefact.** `accept/ref_one.py` shares no code with mutlib: it runs the original suite text
  in a fresh `python -B` subprocess, with only BASE redirected (`accept/ref_vbn113c.txt`).
  * `bad_race`: rc 0, ALL OK, no FAIL line.
  * Positive controls: `b6` is killed by `PRED_edge_15` and `bad_xthr` by `INVESTIGATE_xthr`, the same cases mutlib names.
* **What the gap is:**
  * `bad_race` adds `tot['bda_nrace']` to `bad`.
  * The verdict cannot change, because the GO branch already requires `bda_nrace == 0`.
  * But `out['bad']` and prediction B1 (`BAD == 0`) are never checked on a fixture that has races and nothing else.
  * A fixture case of the kind `(dict(race=1), 'B1', True)` in `test_vbn113c.py` would kill it.
* **Consequence:** vbn113c is **not certified** under the rule "every mutant killed" until the suite gets that fixture. Changing
  the suite is outside this task.

## 5. Timing: where the gain comes from (net112)

* **Subset:** 20 mutants, one about every 14th in definition order, listed in `accept/subset20.txt`.
* **Conditions:** no controls, warm parse cache, runs in sequence.
* **Consistency:** all 4 configurations killed all 20, and each named **the same first failing case as the full run** (20 / 20).

| configuration | workers | baseline | wall | mutant time, sum of 20 | median per mutant | mean per mutant |
|---|---|---|---|---|---|---|
| default (memo + hoist + early exit) | 21 | 167.6 s | **170.2 s** | 807 s | 13.9 s | 40.4 s |
| `--no-memo` | 21 | 403.1 s | 405.5 s | 1598 s | 31.2 s | 79.9 s |
| `--no-hoist` (early exit only in the final loop) | 21 | 121.4 s | 146.6 s | 1507 s | 55.7 s | 75.4 s |
| `--workers 1` | 1 | 140.6 s | 750.4 s | 609 s | 9.2 s | 30.4 s |
| old harness (archived, 16 lanes) | 16 | 205 s | not run | 7093 s | 357 s | 355 s |

How to read the table:
1. **Stopping at the first failing case, checked when each case is registered.**
   * The old harness always ran all 205 cases: about 205 s per mutant when running alone, and 355 s with 16 lanes running at
     once.
   * mutlib stops at the killing case, which sits at a median 22 % of the suite.
   * Without hoisting, a mutant still exits early in the final loop, but it must first write every fixture (about 2 GB). That
     costs 1507 s instead of 807 s, so **hoisting roughly halves the mutant cost.**
2. **The parse memo.** `--no-memo` doubles both the mutant cost (1598 s against 807 s) and the baseline (403 s against 168 s).
3. **Per-mutant cost without parallelism.** `--workers 1` gives the cost with no competing processes: 609 s for 20 mutants,
   against about 4100 s for the old harness (20 × 205 s). That is **about 6.7× cheaper per mutant** from memo, hoisting and early
   exit alone.
4. **Parallelism.** Running 21 to 28 workers at once costs about 1.3× per mutant (807 s against 609 s). It supplies the rest of
   the gain: the full net112 run did 18 306 s of mutant work in 778 s of wall time.
5. **What bounds the wall time.**
   * For small selections, the baseline bounds the wall time, because in hoisted mode it evaluates every case twice (hoisted and
     final loop). That is why `--no-hoist` has the lower wall on 20 mutants but nearly twice the mutant time.
   * For full runs with `--control`, the `pass`-in-`read_run` control, which misses the memo on every parse, bounds the wall
     (693 s for net112, 931 s for shn113).
   * Estimate only, not measured: without that control, net112 would take about 18 306 s / 28 ≈ 650 s.

**Full-run factor for net112:** the old harness needed about 6300 s of wall time, mutlib 778 s: **8.1×**. This comes from 5.3×
less mutant time under load (97 620 s against 18 306 s) and 28 workers instead of 16 lanes. **For shn113:** about 3 h against
19.8 min, with a cold cache.

## Housekeeping

* **Files written:** only under `C:/kyty/s106_stage/mutlib/`: `ACCEPTANCE.md`, `mut_vbn113c.out.txt`, `accept/`, the new parse
  cache `cache/shn113/` (1.1 GB, safe to delete), updated `cache/*/durations.json`, and a changelog entry in `README.md`.
* **Nothing else touched:** no scorer, test or mutant script was edited; their sha256 values are the ones in the report headers.
* **Clean up:** no work directories or background processes remain.
