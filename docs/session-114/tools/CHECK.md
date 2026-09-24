# CHECK - adversarial check of the ttl114 draft (session 114, ROADMAP item 5)

Checked on 2026-09-25, read only (no game run, no build, no git write, no mutation harness run).

Files checked (sha256 as on disk; they match the drafting report):

| file | sha256 | bytes |
|---|---|---|
| `ttl114.py` | `e1113087f3f68bf10f1d2db87e6797b842b28d8b858c9385e11d3ff07b06f57f` | 50157 |
| `test_ttl114.py` | `0edede85ddb2b2cc0bc2d4681449af2c3a016f70a688918045ca3e68bb14731e` | 91867 |
| `mut_ttl114.py` | `951783ba3025a990562e20afc7f56d999f5ef1e804a39b8247d8799c362454e8` | 43546 |
| `make_ttl114.py` | `5b5794fac385cd635b237087af43ae664eb59235b4498f5b26996790358651ed` | 122637 |
| sealed inputs `C:/kyty/s113/{shn113,test_shn113,mut_shn113}.py` | `c5a582be…` / `f7c9ca53…` / `bc0b66a8…` (full hashes pinned in the generator, verified) | |

**Verdict: PASS. No MAJOR defect.** There is one MINOR finding: item 5's "control 01 PASS" condition appears only in text. Seven INFO notes follow it.

## 1. The scorer against item 5, line by line (`ttl114.py`, `diff` against sealed `shn113.py`: 284 diff lines, all accounted for)

| item-5 term | where | result |
|---|---|---|
| PRODUCTION_ROOT `C:/kyty/s114`, PRED `pred/02_ttl114.md`, PRED_SHA/PRED_BYTES None | :54-57 | OK |
| BINARY_SHA `916f6489…c3b2c` (= `SEALS114.txt` build) | :58 | OK |
| GATES_FILE `C:/kyty/s114/gates_base.txt`, GATES_SHA `303a7849…` (both copies have the same sha, checked) | :60-61 | OK |
| ARMS `dawalk=1 dawalklead=1 titleasync=0|1`, SCHEDULE derived | :68-69 | OK |
| TAG_RE `ttl114b?(?:_entry1)?`, HOLD_S 600 | :67, :70 | OK |
| S1: d mean dt_us (1 − 0, main rows 10..89) ≤ +50 (`<=`) | :72, :584 | OK |
| S2: d mean + 2·SE ≤ +200 (`<=`, sample SE) | :73, :585-586 | OK |
| SIZE_LABEL exact text | :74 | OK |
| Schema: pres_title_ns/_n, flip_rsv_wait_ns/_n, flip_hold_ns/_n, mt_age_ns, mt_n on the `x` row after gw_idle_prio | :109-110 | OK. In the build, `videoOut.cpp:2532-2540` prints these eight names in the FrameTrace-x table: raw values (`micros=false`), zeros included (loop :2543-2548), each name exactly once among all 958 table names. No main or draw row prints them, so FIELD_ORIGIN cannot collide. `pres_title_*` is timed with `NowNs()` and `Add` (`window.cpp:1150-1180`), not with `Scope`, so it is live in `KYTY_FRAME_TRACE=lite`. |
| ENV_EXPECTED = shn113's without `KYTY_BUFFER_GC_TRIGGER_SHIFT_MB` | :122-127 | OK (7 keys). The shift, `KYTY_TITLE_ASYNC` and `KYTY_MAIN_STALL_TEST` now fall under "outside the sealed launch". |
| Arming removed: REGIME_OLD_ARM0, NARROW_ARMED_ARM1, NARROW_DARK_ARM0, NARROW_SCAN_ARM1, NO_CHECK, NO_XTHR (and REGIME_OLD_SCAN, NARROW_SCAN_MAX) | :507-514 | OK (no leftover; the generator also forbids the words) |
| TITLE_COUNTED: level(pres_title_n) ≥ 1 in both arms, missing counts as 0 and fails | :511 | OK |
| TITLE_ARMED: arm-1 wall per call = level(pres_title_ns)/level(pres_title_n) ≤ 20000 ns AND < arm 0's wall; a missing level or a call level ≤ 0 gives None, and None fails | :475-482, :513-514 | OK |
| DEFAULTS_ON, INSTRUMENTS_DARK, WALK_* unchanged | :478-501, :515-525 | OK (byte-identical to shn113) |
| read_video: `' dawalk=1 '` and `' titleasync=1 '` in the gate text; `shifted` removed; binary, pinned, recorded, no_schedule, no_checkpoints, one_ok_attempt, frames ≥ 3000, no_glitch kept | :548-563 | OK |
| P1 arm-0 wall/call in [20, 5000] µs; P2 arm-1 ≤ 20 µs; P3 d dt [−500, +100]; P4 d dt ≤ 0; P5 d gpu_busy [−150, +150]; P6 d flip_rsv_wait_ns ≤ 0 (per-row counter, "raw ns a flip"); P7 d da_miss [−40, +40] | :773-787 | OK. P6 comes from the ABBA pair deltas of the per-row counter, which was added to PAIR_KEYS (:131). |
| Verdicts: `KEEP titleasync=0 (run not admitted / ship rule S1-S2 on mean dt not met / video pass failed)`, `SHIP titleasync=1 as the new default (…; ctl114 must read PASS)`, `SHIP_PENDING_VIDEO (titleasync=1: … vtt114 …)` | :809-817 | OK (but see MINOR-1) |
| must_not_be_claimed: the five items, word for word as specified | :820-822 | OK |

Shn113 guarantees kept byte-identical: the seal check and refusals, PREREG_PINNED, BINARY_SEALED, IDENTITY (main), SCHEMA, FIELD_ORIGIN, RAW_CONTIGUITY, DURATION, GATEARM (every clause), NO_FLOOR, MARKERS_OFF, NO_RECORDING, STREAMS_COMPLETE, ROW_ARMS and AB_BA_BALANCED. The controls PIN_ONCE, RECORD_THREAD_TWO, NO_CHECKPOINT_LINE, NO_GPUHANGABORT, NO_FATAL_MARKER (FATAL still lists `GpuWaitSlow:` and `AsyncPipelines: skipped draw`), ENV_NO_CHECKPOINTS, PAIRS ≥ 60, BANDS (unchanged since s111, used for both BDA regimes), WORK_SPLIT, AREA_VERDICT, AREA_SELECTED, ARMING and SYNC_COMPILE (≤ arm-0 + 2 over all rows from 2100) are kept too. So are the protocol checks, the main (10..89) and secondary (60..88, never deciding) windows, whole-quartet pairing, median block levels, sample SE, and `cpu_net_us` staying report-only. The removed shn113 logic is exactly the BDA arming, the shift env/video check and BDA-only report lines. `bda_scan` and `bgc_evict` levels are still reported, so the regime can still be quoted.

## 2. The generator

* Every change goes through `derive()` (AST outline: 3 `derive` calls with 32, 42 and 19 pairs, and no other write or replace path). Each anchor is asserted to end with `\n`, to start at a line start and to occur exactly once, and each replacement to end with `\n`. The inputs are pinned by full sha256 after the CRLF→LF normalisation; the sealed files are already LF, and their on-disk sha256 equals the pins. Each output is compiled, and each has a forbidden-leftover list. This is the same helper as `make_shn113b.py` plus those two extra checks.
* **Byte-reproducible:** a copy that differs only in `OUT` (pointed at `check/regen`) regenerated all three files byte-identical to the drafted ones (`cmp` and sha256). The outputs are LF-only, UTF-8 and end with a newline.

## 3. Fixtures

* `python test_ttl114.py ttl114.py` (default fx dir): **249 cases, ALL OK**, exit 0, 5 min 18 s (`check/test_run.out.txt`, sha256 `045cc6af…`).
* Isolation, read case by case:
  * **TITLE_COUNTED:** it fails alone in `_out0/1` (level 0.9875 while TITLE_ARMED holds) and in `_lag0/1` (main window only). A missing level (`_none0/1`) or a zero level (`_zero1`) also fails TITLE_ARMED, which is correct by construction.
  * **TITLE_ARMED:** it fails alone at the cap (20000 passes, 20001 fails), with equal walls, when arm 0 is faster, and per call (`_percall` passes, `_percall_out` fails). The main window only is covered in `_lag0/1`, and a missing ns level in `_none0/1` (with SCHEMA, by construction).
  * **S1 and S2:** S1 alone in `S1_only` (+50.5), with its edges `S1_edge` (+50) and `S1_edge_in` (+49.5). S2 alone in `S2_only` and `SE_exact` (which straddles +200 between the sample and population SE). `S2_edge` (+200 with SE 0) makes S2 hold while S1 fails, and `S2_edge_out` (+200.5) fails both.
  * **Schema:** each of the eight new fields alone (`SCHEMA_<name>`, with its exact missing list), plus `FIELD_ORIGIN_title`.
  * **Video gate:** `V_gate`, `_mode2`, `_none` and `_dawalk`, each alone. The exact list of video-check names in the SHIP case kills a re-added `shifted`.
  * **Environment:** `ENV_EXTRA_title_async`, `_main_stall_test` and `_buffer_gc_trigger_shift_mb`, plus CONSTANTS against a written-out ENV_WANT.
  * **Predictions:** every P1-P7 edge, both at the edge and one step outside it.
  * **Text:** the claims (exact text), every verdict string (full text) and the tag acceptance and refusal cases.
* **Independent check** (`check/indep_check.py`, not derived from the suite): its own fixture writer builds noisy, realistic runs. It independently recounts d mean, SE and the per-call walls and compares them with the scorer (1e-9 relative). It covers these cases:
  * d +20 in the OLD regime gives PENDING; with a vtt114 video on the `gates_title1.txt` text it gives SHIP.
  * The session-113 video (bdanarrow=1, shifted) gives a video FAIL.
  * d +60 fails S1 alone.
  * d +21.8 with 2SE 191.5 fails S2 alone.
  * An arm-1 wall of 25 µs fails TITLE_ARMED alone.
  * Arm 0 with no calls fails both TITLE checks.
  * The shift in the launch is a protocol error.
  * `GpuWaitSlow` in stdout fails NO_FATAL_MARKER.
  * The `MainThreadWait`, `MainTaskLate` and `FlipHold` lines are not markers.
  * The P6 value is −40000 raw ns a flip.

  All 11 cases are OK (`check/indep_check.out.txt`).
* A `--draft` smoke run on the real session-113 log (`C:/kyty/s113/log_shn113.txt`, 372 MB) runs without a crash. It shows SCHEMA and TITLE_* failing on the old build's missing counters and the protocol flagging the old schedule and the shift, as expected.
* The mutation report was read, not rerun: 344/344 killed and 3/3 controls survived, under frozen mutlib v2 `877eb53a` with the memo off (baseline "memo off"). The new-term mutants and their killers match the isolation above.

## 4. Findings

**MINOR-1: the scorer does not read the "control 01 PASS" condition of item 5.** Item 5 reads: SHIP `titleasync=1` if the run is admitted, **control 01 PASS**, S1, S2 and the video PASS; otherwise KEEP 0. The scorer never reads ctl114. The condition appears only in the docstring (:29-30) and in the SHIP verdict text ("…; ctl114 must read PASS", :813); `SHIP_PENDING_VIDEO` (:815) does not mention it. So the verdict field can read SHIP when ctl114 read FAIL.

This is not rated MAJOR, for three reasons:
* The task's TARGET defines the scorer's SHIP without this condition.
* The SHIP string states the condition rather than claiming it was met, as shn113's "video pass is owed" did.
* Item 6 runs `go114a.sh` (ctl114) before pred/02 is sealed.

Remedy: the pred/02 seal text must pin "the SHIP verdict counts only if ctl114 (pred/01 `ac16a32a`) read PASS; otherwise KEEP titleasync=0". Alternatively, a `--control-out <ctl114 json>` input could check its sha and verdict. That would be a scorer change and would need its own fixtures and mutants.

INFO (no action required):
1. **Regime.** No BDA-regime term remains, as item 5 intends. The `bda_scan` levels are reported, so a quoted size must name its regime, because levels from different regimes are not compared.
2. **TITLE_COUNTED sits at the nominal value of 1 call a flip.** This is safe by code:
   * `UpdateTitle` is on the only success path of `Presenter::Present` (`swapchain.cpp:903`).
   * That present runs inside `FlipQueue::Flip` before the FrameTrace snapshot, on the same thread (`videoOut.cpp:1182`).
   * Only held or dropped presents, or an active shader-preparation overlay, give rows with 0. A held present also prints the fatal `AsyncPipelines: skipped draw`.
3. **Video gate check.** A gate text holding both `titleasync=0` and `titleasync=1` would pass this check, while the loader takes the first value (inherited from shn113). `gates_title1.txt` normalises to `gates_base.txt + " titleasync=1"`. Its stray `\r` before ` titleasync=1` is harmless: `FindAssignment` accepts `\r`, and `enter_scene.py:527` normalises whitespace.
4. **Hard-coded draft paths.** `test_ttl114.py` defaults its fixture dir to `C:/kyty/s114/ttl114_draft/fx` (4 GB), and `mut_ttl114.py` sets `HERE` to the draft folder. shn113 did the same with `s106_stage`. For the sealed copy, pass a fixture dir or accept this.
5. **The two draft-only seal mutants.** `CONST_pred_sha_prefilled` and `CONST_pred_bytes_prefilled` will not anchor on the sealed copy, whose PRED_SHA is filled; exclude them there, as in s113.
6. **mutlib cache in the repo.** `git status` in `C:/kyty/KytyPS5` shows an untracked `docs/session-113/mutlib/v2/cache/` (mutlib v2 writes its cache inside the repo; the ctl114 entry belongs to the other workflow). Keep it out of commits.
7. **Temporary files.** The checker's temporary fixtures (`check/ifx`, `check/regen`) were removed; only the scripts and outputs under `check/` remain.
