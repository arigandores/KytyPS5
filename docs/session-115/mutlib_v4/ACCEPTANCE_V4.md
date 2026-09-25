# mutlib v4 acceptance (2026-09-25, trimmed)

**Harness:** `C:/kyty/s106_stage/mutlib/mutlib.py`, sha256 **`b666df3594ec245f488585b93ec7282fee5bfdff16d45e34cad60b01dd9f922b`**.
It was not changed during the acceptance; the hash was checked before and after every run. `mutlib_v3.py` is
byte-identical to the accepted v3 (`5d2f2f90a28e9f405158d2771898f54850692279c3056f4acf0b6aac3b97537d`).

**Scope.** The executor trimmed this acceptance so the user waits less. Everything the builder had already verified,
where its output files show PASS, is taken as done and was **not** run again (item 0). New runs cover only what was
missing: net112 under v4, PyPy, and the review3/review4 cases the builder's compare outputs did not cover. There were
no new v3-versus-v4 timing runs. Every heavy run went through the gate: `C:/kyty/s115/V4_GO` present, no
`C:/kyty/SEALED_RUN.lock`, a clean `procload.py`, one run at a time. The runs waited until a parallel chain
(`accept4/chain4.sh`, not started by this acceptance) had finished. No game, emulator, build or git operation was run.

**Verdict: PASS.** There is one reservation about timing: the 10-minute target is met only by the default path for a
derived scorer (see *Target*).

| item | result |
|---|---|
| 0. Builder outputs (small checks, ttl114b selection warm and cold, full ttl114b, syn2 / syn3 / syn4 / adversarial / review3 / review4 comparisons, probes) | **PASS** (files read and re-checked, nothing re-run) |
| 1. net112, full, `--control`, under v4 | **PASS**: 277 / 277 rows equal to accept3 (and to accept2), and 277 / 277 name the old harness's earliest failing case; controls 3 / 3; 844 s |
| 2. PyPy verdict equality: vbn113f, check115, then net112 | **PASS**: vbn113f 54 / 54, check115 104 / 104, net112 277 / 277 (and check112 24 / 24 from item 0), controls 3 / 3 each; but **no speed gain** on net112 (1 016 s against 844 s) |
| 3. review3 / review4 cases not covered by the builder | **PASS**: review3's T6 frame probe (v4 adds no frames: 9 = v3's 9); review3's V-suite rerun list (vdg112 36 / 36, vbn113b 41 / 41, vbn113c 43 / 43 with the known `bad_race` survivor) |
| Target: one ABBA-size seal in 10 min or less | **met by the default derived-scorer path** `--changed-from PARENT --control`: 7.6 min with a warm parse cache, 10.2 min with a cold one (2 % over). **Not met by full runs**: 345 ttl114b mutants take 20.3 min, 277 net112 mutants 14.1 min. |

## 0. Builder outputs taken as done (not re-run)

The files were read and every report was re-checked with `accept4/check_accept_v4.py`. That checker was generated
from accept3's `check_accept_v3.py` by `accept4/make_checker.py`: it expects the "mutlib 4" header and adds the
`--selected` and multi-`--ref` options. Before use it was checked against accept3's net112 report (`--major 3`), where
it reproduced accept3's PASS: 277 / 277 rows and 277 / 277 earliest cases.

| builder output | content | result |
|---|---|---|
| `v4check/out/small_v4.log` (final file b666df35) | filter_probe (25 variants, 0 false skips), fast_rebind (0 BAD), scan_scripts (85 project mutant scripts: 57 ok→ok, 28 refused→refused), static_v4 / static_fx_v4 / static_v2 / runtime_memo (0 failures), syn4 (13 configurations, 0 BAD), review4 (56 configurations agree or are refused as decided; T9a / T9b differ as in v3), syn3 (23, 0 BAD), syn2 (6 / 6), adv (23 runs), check112 24 / 24, check112 under PyPy 24 / 24, check115 104 / 104, ttl114b `--only` subset 9 / 9 | PASS |
| `v4check/out/heavy/sel_warm.*` | ttl114b, `--changed-from ttl114.py --control`, 12 touching + 67 of 333 sampled = 79; warm parse cache | PASS 79 / 79 against session 114's report, controls 3 / 3; **458 s** |
| `v4check/out/heavy/sel_cold.*` | the same with a fresh `--cache-dir` | PASS 79 / 79, 3 / 3; **614 s** |
| `v4check/out/heavy/b1_6118aef5/full_warm.*` | ttl114b, all 345 mutants, `--control`, warm | PASS 345 / 345 (re-checked with `MUTLIB_SHA=6118aef5…`), 3 / 3; **1 220 s**. Run on the **earlier build 6118aef5**, not the final file (per the README, 6118aef5 came before the NaN backstop switched to scanning the pickle's bytes). The report exists, so it was not run again. |
| `v4check/out/adv_compare_v4.txt` | 23 adversarial runs | K (stricter: `version_always` killed by the early `exit 0`) and I (cp1250 encoding crash, noted and not emulated) differ as decided since v2; E / E2 refused; S_okfalse gives the `exit 1` label form (fast mode off); controls 3 / 3 in every run. Same outcome as the v2 and v3 acceptances. |
| `v4check/out/syn2_compare.txt`, `syn3_compare.txt` | v2's and v3's synthetic checks | 6 / 6 ok; 23 checks, 0 BAD (DEEP: `deeper10` a survivor as in v3, never a false kill) |
| `v4check/out/review4/review4_compare.txt` | every review3 triple (T1v, T1n, T2, T3, T4a–c, T5, T5b, T6, T7) and every review4 triple (T8a–c, T9a, T9b, T10–T14, T16) against its reference | T8a / T8b / T8c (MAJOR-1) and T11 / T12 / T13 refused; T16 (MAJOR-2) agrees cold and warm with the memo on; T14 (MINOR-1) and T10 (MINOR-2) agree; T9a / T9b differ as before (a survivor the old loop hid, never a kill) |

## 1. net112 under v4: PASS

Command (`accept4t/run4t.sh net112`, from `C:/kyty/s106_stage/mutlib`, 28 workers, default cache):
```
python mutlib.py --scorer C:/kyty/s106_stage/net112.py --test C:/kyty/s106_stage/test_net112.py --mutants C:/kyty/s106_stage/mut_net112.py --control
```
* **The scorer is the `s106_stage` copy (`566c8bf1`), the one accept2 and accept3 used.** `C:/kyty/s112/net112.py`
  (`745b1575`) differs from it only in the two sealed lines `PRED_SHA` / `PRED_BYTES`. On it, the mutants
  `CONST_pred_sha_prefilled` and `CONST_pred_bytes_prefilled`, which are not marked draft-only, find no anchor and the
  run refuses. The test and mutant scripts are byte-identical in both places (`956397b4`, `08d91193`).
* **Result:** ALL KILLED (277 of 277); controls 3 / 3 survived. 0 unresolved, 0 reruns of any kind, 0 isolated reruns,
  no store change. Fixture replay was on: 178 of 178 generator calls were validated by the two baselines, 2.37 GB were
  shared read-only, and 48 416 calls were replayed (890 ran for real, the mutants of the constants the generators
  read). Early exit: the kills skipped a median 78 % / mean 69 % of the suite's 205 checks.
* **Checks** (`accept4t/runs/net112.check.txt`, `check_accept_v4.py N … --ref accept3 --ref accept2 --old
  ../net112/mut_net112.out.txt --order C:/kyty/s112/test_net112_sealed.out.txt`): PASS, 0 problems.
  * 277 / 277 rows are identical (verdict and kill label) to **accept3/net112.report.txt** and to
    accept2/net112.report.txt.
  * 277 / 277 kills name the old harness's earliest failing case; the kill position is a median 22 % / mean 31 % of
    the suite.
  * `v4check/compare_rows.py` against accept3 agrees: 277 equal.
* **Time:** wall **843.8 s (14.1 min)**, worker time 20 925 s; v3's run took 36 655 s of worker time. This was the
  first v4 run of net112, so its parse-memo entries were cold (read_run dependency hash `d9d1406b…`; the builder never
  ran net112). Both baselines took 416 s each while the pipelined mutants were already running.

## 2. PyPy: PASS for verdicts, no speed gain

PyPy 3.12 v8.0.0 (`C:/kyty/tools/pypy/pypy3.12-v8.0.0-win64/pypy3.exe`), `--python PYPY`, every other option default.
Verdicts and kill labels were compared row by row with the CPython v4 run of the same suite and with the accepted
reference.

| suite | source of the PyPy run | rows equal (verdict + label) | controls | PyPy wall | CPython v4 wall |
|---|---|---|---|---|---|
| check112 | builder (`small_v4.log`, 2 workers) and `accept4/runs/check112_pypy` | 24 / 24 vs accept3 and vs CPython v4 | 3 / 3 | 3.1 s | 4.2 s |
| vbn113f | `accept4/runs/vbn113f_pypy` (parallel chain, re-checked here) | **54 / 54** vs accept3 and vs CPython v4 | 3 / 3 | 33.9 s | 43.3 s |
| check115 | `accept4/runs/check115_pypy` (parallel chain, re-checked here) | **104 / 104** vs session 115's report and vs CPython v4 | 3 / 3 | 37.6 s | 35.6 s |
| net112 | `accept4t/runs/net112_pypy` (this acceptance) | **277 / 277** vs the CPython v4 run and vs accept3; 277 / 277 earliest old cases | 3 / 3 | **1 015.6 s** (worker time 27 111 s) | 843.8 s (20 925 s) |

* The vbn113f and check115 PyPy runs came from `accept4/chain4.sh`, which ran on this machine at 14:56–15:17. Their
  headers carry the final sha (`b666df35`) and the `interpreter: … pypy 3.12.14` line, and both pass
  `check_accept_v4.py` with 0 problems. They were not repeated.
* net112 was run because the two small suites agreed and the expected time was under 30 min; it took 17 min.
* `accept4/runs/vbn113f_pypyonly` also ran under PyPy with `--no-fast`. It shows the same 54 kills of the same cases
  in the `KILLED by exit 1 (first failing guard: X)` label form that `--no-fast` gives. That is a label format, not a
  difference.
* **Conclusion:** PyPy gives identical verdicts and labels on all four suites compared. It is slower on the large
  suite, so CPython remains the default.

## 3. review3 / review4 cases not covered by the builder: PASS

The builder's `review4_compare.txt` runs the same 22 triples as review4's own `review4/out/review4_compare.txt`. That
covers every `sc_t*` / `test_t*` / `mut_t*` triple of review3 and review4 (`mut_t12_extra.py` and `extra_t13.json` are
inputs of T12 / T13). Two things in review3 were not covered, and both were run here:

* **T6 probe** (`review3/test_t6probe.py`, `mut_t6probe.py`, `sc_t6.py`) counts how many Python frames sit below a
  scorer function called from the suite. It decides how close a recursive scorer gets to the recursion limit (the
  DEEP residual).
  * Under v4 the count is **9 frames (limit 1000)**. v3 gives the same 9 (same run, `accept4t/t6/`), v2 gave 9 and the
    old harness 2 (`review3/out/t6_*.txt`).
  * So v4's early-exit and replay hooks add no frames, and the DEEP residual (`deeper10`, a survivor, never a false
    kill) is unchanged, as syn3 shows.
  * As intended, the probe forced one worker (it writes outside its job directory).
* **review3's V-suite rerun list** (`review3/rerun_v_suites.py`: check112, vdg112, vbn113b, vbn113c). check112 is in
  item 0; the other three were run under v4 (`accept4t/runs/`, 28 workers) and checked against accept3 and accept2:

| suite | result | rows equal accept3 / accept2 | controls | v4 wall | v3 wall (accept3) |
|---|---|---|---|---|---|
| vdg112 | 36 killed | 36 / 36, 36 / 36 | 3 / 3 | 19.9 s | 18.8 s |
| vbn113b | 41 killed | 41 / 41, 41 / 41 | 3 / 3 | 28.7 s | 28.4 s |
| vbn113c | 42 killed, `bad_race` SURVIVED (known) | 43 / 43, 43 / 43 | 3 / 3 | 34.7 s | 31.9 s |

## Timings (v3 / v2 numbers are the known ones; no new side-by-side runs)

| run | old harness | v1 | v2 | v3 | **v4** |
|---|---|---|---|---|---|
| **ttl114b seal, derived scorer** (345 defined) | — | — | 4 086 s ≈ 68 min, all 345 (session 114, "about 70 min") | — | **`--changed-from ttl114.py`: 79 mutants, 458 s (7.6 min) warm / 614 s (10.2 min) cold** |
| ttl114b, all 345 | — | — | 4 086 s | — | 1 220 s (20.3 min, build 6118aef5, warm) |
| **net112**, all 277 | ≈ 1 h 45 min | 13 min | 1 267.7 s (21.1 min, warm) | 1 298–1 526 s (21.6–25.4 min); `--no-memo` 2 016.7 s (33.6 min, the mode ROADMAP 115 item 4 required for v3) | **843.8 s (14.1 min)**, cold memo; under PyPy 1 015.6 s |
| shn113, all 310 / 317 | ≈ 3 h | 20 min | 34–37 min | 2 040–2 206 s (34–37 min) | not run |
| small V suites (check112, vdg112, vbn113b / c / f, check115) | — | — | seconds | 3–41 s | 4–43 s (no gain: fixture replay is off for them, because they have no generator or their generators return a dict, and they already run in seconds) |

Speed-ups:
* **ttl114b seal**, default path against session 114's full v2 run: ×8.9 warm, ×6.7 cold.
* **ttl114b, full run:** ×3.35.
* **net112:** ×1.5 against v3 warm, ×1.8 against v3 cold, and ×2.4 against the v3 `--no-memo` mode that item 4
  prescribed. Worker time fell from 36 655 s to 20 925 s.

**Target** (one ABBA-size seal in 10 min or less):
* **Met** for a derived scorer with a sealed parent on the default path (`--changed-from PARENT --control`, default 20 %
  sample): 7.6 min with a warm parse cache. With a cold cache (the first run of a new read_run closure) it takes
  10.2 min, 0.2 min over.
* **Not met** for full runs: the 345 ttl114b mutants take 20.3 min, because their wall is set by about 30 000 s of
  total work. The 277 net112 mutants take 14.1 min.

## Recommended flags

1. **Derived scorer with a sealed parent** (the usual ABBA seal):
   `python mutlib.py --scorer S --test T --mutants M --changed-from PARENT --control`
   (sample 0.2 and the seed from the scorer's sha256 are the defaults).
   * Keep the default `--cache-dir` so the parse memo is warm.
   * Read the header's list of changed lines that no mutant anchor overlaps before sealing.
2. **New scorer without a sealed parent:** a full run, `python mutlib.py --scorer S --test T --mutants M --control`.
   Expect about 14 min for a net112-size suite and 20 min for a ttl114b-size one.
3. **`--no-memo`** (ROADMAP session 115 item 4):
   * **Why item 4 required it:** review4 MAJOR-2, where memo copies broke `is` comparisons with non-singletons. v4
     closes that and it is verified:
     * T16 agrees cold and warm with the memo on;
     * net112 under v4 with the memo gives rows identical to v3's `--no-memo` run (`accept3/net112_nomemo`, 277 / 277);
     * check112, vbn113f and check115 give identical rows with and without the memo under v4 (`accept4/runs/*_v4nm`).

     So v4 does not need `--no-memo` by default.
   * **Keep `--no-memo`** in three cases:
     * whenever `mutlib_v3.py` is used as a fallback (item 4 unchanged);
     * under v4, when the scorer or suite compares read_run results by object identity in a way v4's detector does not
       cover. The detector covers `is` / `is not` against a non-singleton, `id()`, `operator.is_` / `is_not`; an
       identity test through a helper imported from another module is not covered;
     * when the report shows `skipped by the mutant script's own filter` lines that are not explained, the T9a / T9b
       shape: a possible false survivor, never a false kill.
   * **The other item-4 conditions** (`ok` changed only by `&=` / `ok and`, a plain `python TEST mutant [fx]` call, a
     filter mutlib can evaluate) are now enforced by v4 itself, by refusal or by fast mode switching off.
   * `--work-dir C:/kyty/s1NN/work*` stays good practice.
4. **PyPy (`--python …pypy3.exe`):** item 2 passed on check112, vbn113f, check115 and net112, so it is **allowed** for
   those suites. It is **not recommended**, because it is slower on the large suite (net112 +20 % wall, +30 % worker
   time) and gains at most seconds on the small ones. It was **not** compared on ttl114b (`heavy_v4.sh sel_pypy` was
   not run), so do not use it for ttl114b-family seals.

## Not done / residuals

* The full 345-mutant ttl114b run exists only on build 6118aef5. It was not repeated on the final file (the selection
  runs on the final file agree 79 / 79).
* shn113 was not run under v4.
* There is no warm-cache net112 timing under v4; the 843.8 s above is a cold-memo run.
* T9a / T9b are unchanged: a filter after the substitution can yield a survivor the old loop hid, never a false kill.

## Files

* `accept4t/run4t.sh`: the gated runner for this acceptance. Its log is `accept4t/run4t.log`.
* `accept4t/runs/`: net112, net112_pypy, vdg112, vbn113b and vbn113c. Each has `.report`, `.stdout`, `.stderr` and
  `.wall` files, and a `.check` file from `check_accept_v4.py`; net112 also has a `compare_rows` output.
* `accept4t/t6/`: the T6 probe under v4 and v3 (`*.frames.txt`, reports).
* Used read-only: `accept4/check_accept_v4.py`, `accept4/runs/*` (the parallel chain's check112, vbn113f and check115
  runs) and `v4check/out/**`.
