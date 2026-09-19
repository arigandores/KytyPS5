# Session 99 — M3 bindings-only: first calibration NOT ADMITTED, sequence STOPPED

This is the session's source of truth. After preparation commit a3558a2 the user explicitly
said "можешь запускать". One executor launched exactly one cal99a process, without warmup
or retry. The process survived, but the calibration failed its sealed admission. No bf99a,
cal99c or bf99c followed. No accepted burn, B_a/B_c or new M3 verdict exists.

## 0. Three opening numbers and route state

Budget <=~3.0 us/draw, <=~2.3 us at p99 (7284 draws). The OLD admitted reference remains
6.4 us/draw, 31.6 ms/frame, GPU busy 12.8 ms. This failed calibration is not a replacement
performance baseline. Prior global M3 remains GAP; M4 and M5 are undone in that order.
No speedup, global G/R1 closure or 60 FPS has been proved or promised.

## 1. What actually ran

cal99a: period30, start1800, ABBA; base bindfloor0/drawahead1/bfmode2/bfburn12000;
armed bindfloor1/drawahead1/bfmode2/bfburn12000. Latch1, clear0, clock pin1, GPU markers0,
GPU checkpoints0; original gates_base, --hold180 --attempts1, no --warmup-first or video.
All KYTY_* were positional arguments. No other agent ran a scorer/build during the hold.
Pre-existing user/system services were not stopped; pre-run GPU utilization was 1%.

The new binary ee9cc8ab1f5d25384dedb02a6a6abfca2aa7692585fcaddc74950721afc7a160
(23739904 bytes) was installed and is still installed. The former 9aa93e73... exe is saved
as C:/kyty/s99/kyty_emulator_before_run99.exe; orig-74a78f3 was not touched. No rebuild
followed the successful preparation build. Frozen scorer/harness hashes matched the prior
independent review, and source/defaults were not changed for this run.

Stable scene: frame278, 15.9s from launch. Hold180.1s for requested180; outcome ok,
hold_exit=null, harness exit0. Raw dt sum189.030605s, after stable180.215183s. No forbidden
hang/abort/fatal marker in raw log or stdout. Emulator process count after exit: zero.
The calibration scorer was called once, after process closure, and returned exit1.

## 2. The deciding failure — three controls, two distinct deficiencies

| Control | Measured diagnostic | Required | Result |
|---|---:|---:|---|
| Criterion3 work | -4.0974201604% draws/frame | abs <0.5% | FAIL / overall INVALID |
| Inherited C5 | abs difference0.0409742016042 | <=0.02 | FAIL |
| R2 completed falling edges | 17 | >=30 | FAIL |

C5 and criterion3 work are the same draw-population difference, not independent evidence.
Untrimmed window means: U5052.85172004745, A4845.8151549942595 draws/frame on843/871 rows.
Criterion3 area split was only -0.0105082881%, and complete area pairs28/28 matched: both
PASS. The criterion failed because WORK changed; not because its between-arm area test failed.

There were34 arm changes, all34 bf_edge at idx0, no stray/duplicate edge. The raw record
ends at n3813. T* contains102 rows across the whole log and87 inside n>=2100; the scorer's
printed102 is the full set, not the window count. Retained rows U799/A828; endpoint pairs29
(minimum10 passed). The area scorer uses28 pairs because it requires >=8 rows per block.

T*-trimmed diagnostic dt means: U50501.82478097622us, A42516.67149758454us. C9 is exempt
ONLY for calibration. These means are not a B endpoint, a performance claim or permission
to use a derived burn. No admitted calibration artifact was created. The original180-second
duration delivered only17 completed falls at this run's pace; extending it alone would
not remove the independent failure of the work-population tests.

Under sealed pred/01_bindings_only.md §2, ANY required failure stops the sequence. Therefore
bf99a/cal99c/bf99c were not launched, the rule was not amended, and there was no retry.

## 3. What this one process did establish (limited scope)

Protocol/provenance and survival pass. C1'''/live darkness, C2', C3', C4_B, C6', C7,
C8''_B, C10'''_B and frame-integrity controls pass. Retained armed frozen counters bf_mat
and bf_reuse are zero; live_ahead=6835498, live_mat=631308, live_memo=0. Thus live acquisition
was observed in mode2, without asserting one materialization per draw. Real-clear skips,
skip drops, skipped readbacks, bf_mixed, bf_defer_force and trigger counters are zero.
Recovery medians over first2/first3 flips: images12/17, buffers2/3, all within50.

ACB crossover remains: bf_xover=bf_xover_acb=35, positive at all17 falling edges. No hang
occurred in this process. That does not meet the >=30-edge rule or provide a hazard-rate
proof; the old857-edge mode3 proof was not transferred to this new mode/binary.

## 4. Independent VERIFY and parent's check

A NEW verifier (verify_cal99a, no conversation fork, not a code author) received only the
sealed rule and raw inputs. It did not read runner/parent conclusions, call the full
calibration CLI, launch a game or build. Its verdict: NOT ADMITTED, STOP. Evidence and
raw hashes: verify_cal99a/VERIFY.md and VERIFY.json; its fresh area CSV did not use a cache.

The parent's separate recount_cal99a.py imports no scorer and does not compute B/F or a
burn candidate. It independently reproduces both draw means, -4.0974201604%,17 falls,
34 edges,87 window T* rows and both diagnostic dt means. The key numbers agree.

Primary raw log: log_cal99a.txt,84293208 bytes,
sha25621564a0826abb63a6d91a81358b01975cc5137a08e2469b3cd49a2b2ef7eb9c5.
Metadata: cal99a.json; stdout: stdout_cal99a.txt. No raw file or sealed rule was rewritten.

## 5. Descriptive guards (not additional deciding criteria)

Post-run guards exit1:4 PASS,3 FAIL,3 WARN,2 SKIP. Fail3: RT/viewport varied, with9 fragment
flips excluded; the attachment-weighted between-arm area comparison above still passed.
Fail4: work spread4.272% using the reverse ratio (same population as -4.097% in C5).
Fail6: one of12 CPU groups was -11.3% from its arm median,4.257 versus4.799 cores. It does
not identify a foreign process as the cause. GPU clock guard passed, temperatures60..69C;
no throttle reason outside the guard's allowed mask. ds4windows.exe/tabtip.exe were listed
on the GPU while pre-run utilization was1%; they were not killed and causality is unknown.

Video was not requested on calibration. Guards8/9 skipped; the required bf99a video was
never reached because the sequence stopped. No rendering/recovery visual acceptance exists.

## 6. Preparation retained, not redone

Commit a3558a2 contains the mode2 burn repair, live witnesses, sealed diagnostic rule and
reviewable harness snapshots. One build passed; offline verification passed23 scorer tests,
20 independent assertions and8 harness tests. Initial VERIFY failures and fixes (early missing
fields/live leaks, stale area CSV, inconsistent metadata/short raw logs, warmup continuation
and stdout/fatal markers) remain in docs/session-99 and FACTS_before_cal99a.md.
The failed real calibration was not turned into a code repair or a changed threshold.

Rule unchanged: pred/01_bindings_only.md,10848 bytes, sha256
8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d.
gates_base unchanged:1092 bytes/99 names, sha256
00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8.

## 7. Remaining work and continuation

No accepted calibration, B_a/B_c, bindings-only diagnostic branch, video acceptance or
completed M3. Prior global GAP and live/unlicensed G/R1 remain; M4/M5 do not start.
Why draws/frame changed and why this process's base timing differs from the old reference
are not established by this run. Do not label the difference a regression or foreign load.

A new PLAN must investigate work-count comparability and whether calibration can require
same work before its burn is matched, plus the inadequate transition count in a fixed180s
hold. Any revised experiment needs a NEW preregistration and new tag before new numbers;
do not edit this seal or simply repeat cal99a. Continuation prompt: docs/next-session-100.md.
The stop applies to this sequence; no further launch is queued. Session results are committed
without push, excluding the unrelated nlohmann_json submodule changes.
