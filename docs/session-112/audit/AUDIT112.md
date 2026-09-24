# AUDIT112 — adversarial audit of session 112 (`daguard`, `vdg112`, `net112`, `vid112`): RECOUNT · PROTOCOL · CODE

Own parsers and scripts only, all in `C:/kyty/s112/audit112/` (`parse112.py` → `pkl/*.pkl` for 22 runs of sessions
108–112, `abba112.py`, `recount_net.py`, `recount_vdg.py`, `crossrun.py`, `regime.py`, `regime2.py`, `clocks_arm112.py`
(copied from audit111), `transcript_scan112.py`, `subagent_scan112.py`, `mtime_scan112.py`, `newmut112.py`; outputs
`*.txt` beside them). No session scorer imported; the fixture re-runs and the new mutants run the session's own copies
under `audit112/rerun` with their fixture directories repointed into `audit112/rerun`. Nothing built, no game run, no
state-changing git command, nothing written outside `audit112/`.

## Verdicts

- **RECOUNT — CONFIRMED (numbers), with one MAJOR on the label of the quoted size.** Every claimed number of `vdg112`,
  `net112` (main, secondary, full block, N1–N7) and `vid112`/`check112` reproduces exactly. The ABBA effect is robust
  (thirds, caps, trimmed mean, bootstrap, full block, clocks and DRS balanced). **MAJOR-1:** arm 1 (`daslot=0
  daguard=0`) is *not* the pre-session profile — its walker call costs 1.18–1.19 µs against 1.006–1.033 µs in all six
  pre-session ABBA arms (≤ 1.056 in any pre-session run), in both BDA regimes — so −243.1 ± 62.6 µs is the gain of `daslot=1` over `daslot=0 daguard=0` of
  build `b47b58a9`, not "session 111's gain against the pre-session profile" (pred/02 title and §4, scorer label). The
  question session 112 was opened for (audit-111 MAJOR-1) is still unanswered.
- **PROTOCOL — HOLDS.** Decision after 111 committed before the code; seals committed and hashed before the chain;
  `check112.py` hashed and committed before its run; only `ScheduleWakeup` / a heartbeat message inside the sealed
  window (main transcript, 17 subagent transcripts, 347 444-file mtime scan); all three fixture suites reproduce their
  sealed outputs; every sealed prediction printed and scored. MINOR defects: the arm-order refinement was handed to the
  scorer-deriving agent 18 s before it was written into ROADMAP (MINOR-2); `vdg112` and `check112` fixtures do not cover
  both sides of every threshold, contrary to decision-after-111 item 4 and FACTS (MINOR-3, MINOR-4); a factual slip in
  seal 01 (MINOR-5).
- **CODE — NOT REFUTED.** The `unguarded` safety argument holds on every path I could find (all `AheadTake` /
  `AheadNote` / `memo_generation++` sites are inside `ProgramCache::Get`, every caller of which holds `m_mutex`; every
  `QueueAhead` caller takes `ahead_queue_mutex` for the whole body; workers never write keys or take guards; no slot can be
  `Taking` while another thread holds `m_mutex`). `daguard` changes nothing at `daslot=1` except the (never triggered)
  `GuardSlot` yield. Knob enum and table orders match (30/30). Informational notes MINOR-6, MINOR-7.

## RECOUNT

### net112 (600 s, pinned, ABBA arm 0 `daslot=1 daguard=1`, arm 1 `daslot=0 daguard=0`)

`recount_net112.txt`. 197 `GateArm:` lines, arm texts exact, `abba=1 period=90 arms=2`; blocks 0–3 before frame 2100,
196 incomplete ⇒ 192 blocks, **96 pairs, orientations 48/48**; block assignment by frame arithmetic and by the rows'
own `arm=`/`blk=` fields agree (0 mismatches). Only marker: one `GpuClockPin: mode 1`. 49 × 4 `Gate:` toggle lines
(`daslot`/`daguard` switched together).

| term (main estimator, rows 10–89), d = arm 1 − arm 0 | claim | own recount |
|---|---|---|
| d mean `dt_us` | +243.1, 2SE 62.6, t 7.77 | **+243.097, 2SE 62.591, t 7.77**; sign-flip p < 1e-4; bootstrap 95 % [181, 305]; median of pair d 206.7 |
| d `cpu_net_us` | +240.7 (2SE 56.8) | +240.676, 2SE 56.807, t 8.47 |
| d `da_walk_us` | +49.1 | +49.080, 2SE 8.174 |
| d `gpu_busy_us` | −22.5 | −22.502, 2SE 22.426 (t −2.01) |
| d `da_late` | −5.3 (11.2 → 5.8) | −5.342; levels 11.25 → 5.77 |
| secondary 60–88 | +278.3 (2SE 111.5) | +278.344, 2SE 111.525 |
| N1 arm-1 `da_queue_us`/`da_qcall` (levels) | 1.189 MISS | 1.1895 (median of block means); 1.1812 (means) — MISS |
| N2 arm 0 | 1.142 HIT | 1.1423 / 1.1325 |
| N3, N4 | 243.097 HIT | 243.097 |
| N5 arm-1 `da_q_noguard` level | 1 074.6 | 1 074.625; arm-0 kept sum 0 |
| N6 arm-0 `da_q_free` level | 1 073.0 | 1 072.975; arm-1 kept sum 0 |
| N7 d `da_miss` | −3.0 | −3.015 (2SE 5.3) |

Robustness: full block 0–89 +243.2 (2SE 60.4); thirds +240.7 / +229.9 / +258.7; capped at 41 667 / 50 000 / 60 000 µs:
+240.1 / +247.3 / +246.0; 10 % trimmed mean +236.9; 20 of 96 pairs negative. **Session 110's failure mode is absent**
(main = full block; the secondary window only widens the SE). Long flips: arm 0 7 680 rows, p99 34 178, max 82 665,
≥ 41 667 µs 0.26 %; arm 1 7 680 rows, p99 34 205, max 50 376, ≥ 41 667 µs 0.35 %. **Mechanism = vblank share:** the
one-vblank share falls from 0.149 to 0.135 in arm 1 (d −0.0137, t −7.9), which alone is ≈ 229 µs of mean `dt`; the
difference of block *medians* is only +17.9 µs. Clocks per arm (`clocks_net112.txt`): GPU SM 2 332 / 2 325 MHz
median, power 75.8 / 75.8 W, 67 °C both, event reason `0x400` in all 408 / 413 samples; CPU 4 624 / 4 621 MHz (CCD0),
5 015 / 5 012 (CCD1); DRS `rt_kpx/rt_att` 2 000.0 / 2 000.3. `bda_scan` 53 / 53 (NEW regime, both arms). Game speed:
+0.69 % on the block-median levels, +0.79 % on the arm means (the ROADMAP's "≈ +0,79 %").

### vdg112 (300 s, pinned, ABBA arm 0 `daslot=0 daguard=0` | arm 1 `daslot=1 daguard=1`, `smemocheck=1`)

`recount_vdg112.txt`, `recount_vdg112_arms.txt`. 7 472 `FrameTrace-x` rows, none missing any of the 13 fields; 64
`GateArm:` lines, exact texts; one `Gate: smemocheck=1 frame=1`. Totals: `da_chk_ok` **61 535 031**, `da_chk_bad` 0,
`da_slot_bad` 0, `da_guard_yield` 0, `da_guard_busy` 0, `da_hint_torn` 0, `da_q_taking` 2, `da_hint_defer` 283,
`da_q_noguard` 3 011 966, `da_q_free` 4 904 831; 0 `DaSlotVerify`/`DrawAheadVerify` lines. Per arm (rows 10–89):
2 480 / 2 560 rows, `da_q_noguard` level 1 070 / 0 and sum 0 in arm 1, `da_q_free` level 0 / 1 074 and sum 0 in arm 0,
checks/hits 0.99998 / 1.000001 (the scorer's 0.999981 vs my 0.999983 in arm 0 is a one-row offset in block 0 only: the
scorer counts row n = 1800, logged after the first `GateArm:` line, as position 0 — immaterial). Transition rows
(positions 0–9): 633 rows, 0 bad. D1–D5 HIT as claimed. **GO confirmed.**

### vid112 / check112

`log_vid112.txt`: 3 695 scene rows from stable frame 276; `da_q_free` 4 149 989 (1 123.1 a row), `da_q_noguard` 0,
`da_slot_bad` 0, `cspfree_hit` 982 085, `cspfree_bad` 0, `cs_sync_new` 0, `da_guard_yield` 0; one `GpuClockPin: mode
1`; no marker. Re-running `s51_vidglitch.py` on `rec_vid112.mp4` into `audit112/vidframes`: **3 980 frames, 0
one-frame glitches**. PASS confirmed. (vid112 happened to launch in the OLD BDA regime, `bda_scan` median 1 069 —
irrelevant for a video check.)

### What N1's miss means (MAJOR-1)

Walker time per `QueueDrawAhead` call (`da_queue_us`/`da_qcall`, all rows from frame 2100; `regime.txt`,
`crossrun.txt`). `da_queue_us` starts **before** the `m_mutex` lock in both the session-110 and the current code, so
it includes the wait for `m_mutex` (arm 1, all pre-session runs) or for `ahead_queue_mutex` (arm 0) — same instrument
in every row below:

| run | code / setting | regime | µs per call |
|---|---|---|---:|
| fam108 arm 0 / 1 | s108, `cspfam` 0 / 4 | NEW | 1.006 / 1.033 |
| frm109 arm 0 / 1 | s109, `cspfree` 0 / 1 | **OLD** | 1.007 / 1.019 |
| shp110 arm 0 / 1 | s110, `cspfree` 0 / 1 | NEW | 1.007 / 1.018 |
| sf108c, sf108d, vfy109, obs111, vsh110, vid110 | pre-session | mixed | 1.006–1.056 |
| shp111 arm 0 | `daslot=0` WITH guards | OLD | 1.238 |
| shp111 arm 1 / net112 arm 0 | `daslot=1` | OLD / NEW | 1.103 / 1.133 |
| **net112 arm 1** | **`daslot=0 daguard=0`** | NEW | **1.181** |
| vdg112 arm 0 / 1 (smemocheck: GuestGpu holds `m_mutex` far longer) | no-guard / `daslot=1` | NEW | 1.434 / 1.253 |

1. **The BDA regime does not explain it**: the same pre-session code reads 1.007/1.019 in OLD (frm109) and 1.007/1.018
   in NEW (shp110).
2. **The guards explained only a quarter of audit-111's excess**: 1.238 → 1.181 µs, against ≈ 1.01 before session 111.
   The residual ≈ 0.16–0.18 µs a call × 1 083 calls ≈ **165–190 µs a flip of walker time** (arm-1 `da_walk_us` 2 503
   vs 2 344–2 386 in the session-110 arms).
3. What remains in arm 1 against session 110: `ahead_queue_mutex` lock/unlock *inside* the `m_mutex` hold; every hint
   copied into an `AheadHintView` (`ReadHintLocked`) instead of read in place; the `PairGuard`/`Taking` branches in
   `QueueAheadSource`; on GuestGpu (both arms) the `TryGuardSlot`/`UnguardSlot` exchanges and the `Taking` store in
   every `AheadTake` probe, the seqlock and `Fingerprint`/`ClassOf` calls in every `AheadNote`, publish-once deferral.
   The wait/hold split is unknown (`plkstat` off). vdg112 shows the no-guard per-call time is highly sensitive to how
   long GuestGpu holds `m_mutex` (1.434 µs with `smemocheck`), so part of the residual may be wait. Session 110's
   instrumented `obs111` had hold 0.894 + ≈ 0.14 wait per call.
4. Every residual adds work relative to session 110 except one — the walker now reads `source->plan_class` instead of
   calling the out-of-line `ClassOf` per source (a few ns each), which makes arm 1 *cheaper* there and the observed
   excess more, not less, notable — so **the gain of today's code over session-110 code is plausibly smaller than 243 µs
   in magnitude.** Cross-run INDICATION only (not a measurement; cross-run spreads of 100–450 µs are normal here):
   today's arm (net112 arm 0, NEW) 30 894 µs vs session 110's shipped arm (shp110 arm 1, NEW) 30 980 µs, −85 µs; the
   no-guard arm 31 144 µs, +164 µs over that session-110 arm.

**Fair quote:** −243.1 ± 62.6 µs a flip (≈ +0.7–0.8 % game speed) for `daslot=1` against `daslot=0 daguard=0` of build
`b47b58a9`, pinned, Sky Garden, NEW BDA regime. The ROADMAP item 5 and FACTS wording ("против профиля без стражей",
"no-guard profile"; FACTS §6 "not proved that arm 1 equals the session-110 code") is acceptable; the pred/02 title,
its §4 and `net112.py`'s `GAIN_LABEL` ("session 111's gain against the pre-session profile") are not. Against
session-110 code: **not measured**.

### BDA regime indication (`regime.txt`, `regime2.txt`)

No run switches regime (OLD fraction 0.2–1.4 % in NEW runs, 95–97 % in OLD runs), so no within-run estimate exists
and every ABBA difference is regime-clean. Across runs: 600 s ABBA arms, OLD (4 arms) − NEW (6 arms): `dt` +207 µs,
`cpu_net` +83 µs — but half of it is shp111 (both arms high). Matched pairs (same code at the compared setting):
`cspfree=0` s109 OLD − s110 NEW +27 µs; `cspfree=1` +88 µs; `daslot=1` shp111 arm 1 (OLD) − net112 arm 0 (NEW)
**+442 µs** (`cpu_net` +379); videos +144 and +297 µs. 300 s single-config runs: OLD − NEW +19 µs (`cpu_net` −125).
All five matched pairs have OLD slower in `dt` (27–442 µs, median ≈ 144), but the size is inconsistent and `cpu_net`
changes sign; builds, days and thermal states differ. Indication only: the OLD regime goes with frames ~0–450 µs longer,
of the same order as the effects this program ships, so between-run levels must never be compared across regimes and
the s111 (OLD) and s112 (NEW) ABBA sizes (−230.7 vs −243.1) are not a test of the guards' effect.

## PROTOCOL

- **Order of records** (`transcript_calls112.txt`): decision after 111 committed `5609d47` 05:49:10; patch written
  05:51:23, built 05:51:50 (exe 05:52:13), committed `7e892d5` 05:52:24; working tree clean, no source newer than the
  exe; installed exe = build = `b47b58a9…` = `kyty_emulator_b47b58a9.exe`. vdg112 scorer (05:53:44) is covered by
  decision-after-111 item 2. ROADMAP "СЕССИЯ 112" records written 06:10:50, committed `b12d6b5` 06:11:14; seal 01
  committed `391f8d7` 06:12:04; pred/02 drafted 06:14:35, finalized 07:46:19, SEALS 07:49:54, committed `8acab29`
  07:50:04; chain 07:50:11–08:08:55. **MINOR-2** below.
- **Seals** (`SEALS112.txt`): all 16 hashes match the files and the committed copies in `docs/session-112`; the port
  line names `s111/s112_port.py` (`fd469ad6`, matches; the copy in `s112` differs only by its self-rewritten roots, as
  in earlier ports). Scorer outputs carry the sealed hashes (vdg112 `8845f970`, net112 `745b1575`, check112
  `829cb59f`); run metas carry the sealed prereg hashes.
- **Sealed window:** main transcript — one `ScheduleWakeup` (07:50:17), one heartbeat message (08:00:13) with no tool
  call, the task notification at 08:08:55. 17 subagent transcripts (sessions 108–112, this audit included) — 0 calls in
  the window (the net112-deriving agent ended 07:46:10, this audit started 08:10:25). mtime scan of 347 444 files under `C:/kyty` and the emulator folder: only chain products
  (logs, stdout, csv, json, runs112, mp4, `gates.req`/`sample.req`, `_kyty*.txt`, `_PipelineCache`). A stray
  `tail -f` (since 06:35) was killed at 07:46:04, before the window.
- **Fixture suites reproduce:** `test_vdg112.py` 63 fixtures ALL OK, identical to `test_vdg112_sealed.out.txt`;
  `test_check112.py` 38 ALL OK, identical; `test_net112.py` 205 cases ALL OK (3 min 20 s), identical except the two
  REFUSE lines that print the fixture path.
- **Predictions:** D1–D5 and N1–N7 all printed with HIT/MISS; N1 MISS reported in ROADMAP item 5 and FACTS.
- **Arm order:** the change from the decision text ("`daslot=0 daguard=0` | `daslot=1`") to arm 0 = today was recorded
  as item 3 (`b12d6b5`) before seal 02 and before any run; the rule is equivalent (REVERT iff d(A − daslot1) + 2SE < 0
  ⟺ daslot=1 worse with 2SE excluding 0).
- **New mutants** (`newmut112.py`, `newmut_fast.txt`, `newmut_net.txt`): vdg112 — V7 (block position +1) and V8
  (IDENTITY) killed; **V1 (CHECKED `min`→`max`), V2 (D2 band 800→801), V3 (D3 1400→1399), V4 (D5 `min`→`max`), V5
  (levels median→max), V6 (D4 100→99), V9 (ARM_ROWS `or`→`and`) survive**; V10 (numerator without `da_chk_bad`)
  survives but is near-equivalent (it only matters when BAD > 0). check112 — C1 (binary), C4 (hang marker), C5
  (stable `>`), C7 (missing glitch line) killed; **C2 (`gpuwaitslow` marker dropped), C3 (`errordevicelost` dropped),
  C6 (frames = first number in the report) survive**. net112 — all four killed (revert bar `SHIP_US` 0 → 0.5 by
  `S1_edge_out`; N1 band 1.12 → 1.125 and N7 band +40 → +41 by the prediction-edge fixtures; `SYNC_SLACK` 2 → 3 by
  `SYNC`/`SYNC_unkept`): the net112 suite does cover its edges, as its seal says.

## CODE

`git show 7e892d5`, current `pipelineCache.cpp`, and `git diff 6d8f690 HEAD` (session-110 close → now;
`diff_s110_head_pipelineCache.txt`).

- **`unguarded` safety.** Guard takers: `QueueAheadSource` (only from `QueueAhead`, whose `lock_guard` on
  `ahead_queue_mutex` covers the whole body, at every `daslot`) and `AheadTake` (only from `ProgramCache::Get`, line
  3611). Callers of `Get`: `GetGraphicsPrograms` (`PipeLockMeasured lock(m_mutex)`, 4977), `GetComputeProgram` (5061),
  `PrefetchComputePipeline` (5507) — all hold `m_mutex`; the `cspfree` unlocked path (`PrefetchFree`,
  `MaterializeUnlocked`) touches neither slots nor hints. `AheadTake` publishes every `Taking` slot (Ready or Empty)
  before returning (3378, 3392, 3418), so while a thread holds `m_mutex` no slot is `Taking` and no guard is held by a
  draw. Workers only CAS `Queued→Running` and publish `Ready/Failed` (they never read key fields the producer writes
  on a non-Empty/Failed/Ready slot, nor the guard). Ring-full cancellation is the producer itself under `ahead_mutex`.
  A `daslot=1` producer and an unguarded `daslot=0` producer cannot overlap (`ahead_queue_mutex`); the lock order is
  always `m_mutex` → `ahead_queue_mutex` → `ahead_mutex`, never reversed (nothing under `ahead_queue_mutex` takes
  `m_mutex`). The knobs are read before the lock, but the safety needs only that `m_mutex` is held, which it is.
- **`ReadHintLocked`.** The only hint writer is `AheadNote` (single call site 3601, inside `Get`, under `m_mutex`);
  `ahead_variants` are written only there too; `memo_generation++` only at 3711 (inside `Get`). Correct.
- **`GuardSlot` yield.** Correct; never triggered in any run (`da_guard_yield` 0 in vdg112, net112, vid112) — MINOR-6.
- **`ahead_thread_count`.** The worker-side read is now an atomic; the only other readers of `ahead_threads.size()`
  (`QueueAhead` 2991, `AheadStartThreads`) run under `ahead_queue_mutex`, where the vector is resized. A relaxed count
  can lag the vector only during growth, when it cannot exceed the knob — no wake is lost. `AheadStopThreads` clears the
  vector without `ahead_queue_mutex` (destructor only) — MINOR-7, pre-existing.
- **`daguard` at `daslot=1`.** `QueueAhead(requests, walk, false)`: `ReadHint` with the seqlock, `PairGuard` on — the
  session-111 path; only difference is the yield. Knob enum and `KNOB_DEFINITIONS` in the same order (30/30, `daguard`
  last, default 1, max 1); counters appended last and printed by name.

## Findings

**MAJOR-1 (RECOUNT, interpretation) — the quoted size is not "against the pre-session profile".** Evidence above: N1
MISS (1.189 µs against the band [0.90, 1.12] and against 1.006–1.033 in all six pre-session ABBA arms, ≤ 1.056 in any
pre-session run, regime-independent);
removing the guards removed 0.057 of ≈ 0.23 µs a call; ≈ 165–190 µs a flip of walker time remains in arm 1. The pred/02
title, §4 and `GAIN_LABEL` name −243.1 "session 111's gain against the pre-session profile"; the goal of decision after
111 item 1 ("Сессия 112 меряет выигрыш против кода до сессии") is not met and audit-111 MAJOR-1 stays open. The number
itself is confirmed. **What to do:** quote −243.1 ± 62.6 µs only as "`daslot=1` vs `daslot=0 daguard=0` of `b47b58a9`";
write "gain against session-110 code: not measured, plausibly smaller"; do not add it to the session-110 baseline. If the
figure matters, one `plkstat` observation of the no-guard arm (hold vs wait per call, same instrument as `obs111`'s 0.894
µs hold) would locate the residual before any further build; otherwise close the question — the shipped default is not
at stake (KEEP either way).

**MINOR-2 (PROTOCOL) — the arm order was acted on 18 s before it was recorded.** The net112-deriving agent was launched
at 06:10:32 with "arm 0 = today" and the text "Decision rule (already recorded in ROADMAP)"; the ROADMAP item 3 that
introduces the arm order was written at 06:10:50 and committed at 06:11:14. Recorded before seal 02 and any run; the rule
is equivalent. **What to do:** write the record before launching the agent, even for a relabeling.

**MINOR-3 (PROTOCOL/fixtures) — `vdg112` fixtures do not cover both sides of every threshold.** Seven of ten new mutants
survive (V1–V6, V9; V10 near-equivalent): no fixture where only one arm fails CHECKED or ARM_ROWS, no band edges for D2,
D3, D5, no fixture at D4 = 100. This contradicts decision-after-111 item 4 ("по фикстуре на край каждого порога") and
the claim in seal 01 §2 and FACTS ("63 fixtures incl. both sides of every threshold"). No effect on GO (0.99998 / 1.000001 against 0.99; D2 1 074,
D3 1 070 far from 800/1 400). **What to do:** add one-arm CHECKED/ARM_ROWS fixtures and in/out fixtures at every
prediction edge; state fixture coverage as tested by mutants.

**MINOR-4 (PROTOCOL/fixtures) — `check112` misses two markers and the real report format.** Mutants dropping
`gpuwaitslow` or `errordevicelost` from MARKERS, and one reading the frame count as the first number of the glitch
report, survive; the real report begins `C:/kyty/s112/rec_vid112.mp4: 3980 frames …`, whose first number is 112. No effect
on PASS (re-run: 3 980 frames, 0 glitches). **What to do:** one fixture per marker, and fixture reports in the real
format (path with digits).

**MINOR-5 — seal 01 §1 says "every switch between them is exercised ~70 times".** The run had 64 blocks and 32 arm
switches (16 each way): ABBA switches every second block and `smemocheck` stretches flips to ≈ 47 ms. Nothing scored
depends on it. **What to do:** compute such counts from the schedule and the verify-run frame time before sealing.

**MINOR-6 (CODE) — the `GuardSlot` yield ships untested in practice.** `da_guard_yield` = 0 in every run of the session,
so the only change the shipped binary gained at `daslot=1` is validated by construction and by the video only.
`SwitchToThread` yields only to a ready thread on the same processor, so against a draw preempted on another core it
degenerates into a spin with a system call every 256 iterations — harmless; the comment "gives its quantum away" is
optimistic. **What to do:** nothing unless `da_guard_yield` ever reads non-zero.

**MINOR-7 (CODE, pre-existing, informational) — `ahead_threads` at shutdown.** The new comment says "`ahead_queue_mutex`
(AheadStartThreads) / shutdown"; `AheadStopThreads` (destructor) clears the vector without that lock. A concurrent
`QueueAhead` there would already be a use-after-free of the whole cache, so this adds no new risk. **What to do:** none.

## Size to quote

**−243.1 ± 62.6 µs a flip (2·SE, 96 pairs, frames 10–89; ≈ +0.7–0.8 % game speed) for `daslot=1` against `daslot=0
daguard=0` of build `b47b58a9`, pinned, Sky Garden, NEW BDA regime.** Against session-110 code: not measured —
plausibly smaller in magnitude (arm 1 still carries ≈ 0.17 µs a call of walker cost that no pre-session build had;
cross-run indication ≈ −85 µs, not a measurement).
