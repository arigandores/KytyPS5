# AUDIT111 — adversarial audit of session 111 (`daslot`): RECOUNT · PROTOCOL · CODE

Own parsers only, all in `C:/kyty/s111/audit111/` (`parse.py`, `abba.py`, `recount_shp.py`, `robust.py`,
`clocks_arm.py`, `between.py`, `allfields.py`, `runsum.py`, `guardcost.py`, `recount_misc.py`, `transcript_scan.py`,
`transcript_dump.py`, `subagent_scan.py`, `mtime_scan.py`, `newmut.py`, `grep_src.py`; outputs `*.txt` beside them).
No session scorer imported (the fixture re-runs and mutants run the session's own copies under `audit111/rerun` and
`audit111/mut`). Nothing built, no game run, nothing written outside `audit111/` (checked with `find -newer`).

## Verdicts
- **RECOUNT — CONFIRMED.** Every claimed number of obs111, vds111b, shp111 (main, secondary, K1–K6), vss111 and
  vid111/check111 reproduces exactly. Unlike session 110 the estimator window does not matter here. **One MAJOR on the
  size (MAJOR-1): arm 0 is not "today"** — the unconditional slot protocol lengthens the walker's `m_mutex` hold in
  arm 0, so −230.7 µs is the gain over a *slowed* baseline; the gain over the session-110 build is unmeasured and
  plausibly smaller.
- **PROTOCOL — HOLDS.** Every ROADMAP record precedes its action, every seal is committed and hashed before its run,
  nothing but `ScheduleWakeup`/heartbeat happened in the three sealed windows (main transcript, 14 subagent
  transcripts, 338 719-file mtime scan), all three fixture suites reproduce their sealed outputs, the 02→02b
  replacement is a disclosed, pre-registered correction. Defects are MINOR: vds111b D1–D5 never scored; `check111.py`
  unsealed/uncommitted with a stale docstring and no fixtures; 5 of 12 new `shp111.py` mutants survive (threshold
  edges); see MINOR-2…5, 10.
- **CODE — NOT REFUTED.** No race found in the guard/Taking/publish-once protocol at `daslot=1` (walker, GuestGpu,
  workers, ring-full cancellation, generation bump, retirement, shutdown); memory orderings and the seqlock are the
  standard correct patterns. MINOR code notes (MINOR-6…9). The cause of MAJOR-1 is in the code (at `daslot=0` the
  protocol's work sits inside the walker's `m_mutex` hold), but it is a performance bias, not a correctness defect.

## RECOUNT

| claim | own recount |
|---|---|
| obs111: contended wall 236.1 µs/flip, tag 1 232.6 (98.5 %), tag 2 0, walker hold 965.6 µs/flip = 1 080 × 0.894 µs, spin share ≥ 0.70 | identical (7 983 rows n ≥ 2100): 236.11 / 232.59 / 0.00 / 3.52 (tags 0+3); 239.7 acquisitions; hold 965.57 / 1 080.0 / 0.894; spin 0.703; 1 `GpuClockPin: mode 1`, no marker in log or stdout |
| vds111 NOT_ADMITTED (smemocheck never armed) | `da_chk_ok` 0 over 9 858 rows; log has only `Gate: daslot=2 frame=1` |
| vds111b GO: chk_ok 60.77 M, chk_bad 0, slot_bad 0, q_free 7.82 M, guard_busy 1, q_taking 2, hint_torn 0, hint_defer 278 | identical (7 239 rows); `da_chk_ok` / `da_hit` = 1.0000004 (every take checked); 0 `DaSlotVerify`/`DrawAheadVerify` lines; both `Gate: smemocheck=1` and `Gate: daslot=2` at frame 1. **D1–D5 (sealed in 02b) all HIT**: BAD 0; q_free 1 080.3/flip ∈ [800, 1400]; guard_busy 0.0001; q_taking 0.0003; torn 0 |
| shp111 ADMITTED, 94 pairs (47/47), blocks 188, excluded [192] | 194 GateArm blocks, 0 rows whose `arm=` disagrees with its block, same 94 pairs / exclusion |
| main (10–89) Δ mean dt −230.7 (2SE 81.8, t −5.64) | −230.65 (81.75, t −5.64); median −213.1; sign-flip p < 1e-4; bootstrap95 [−304, −145] |
| Δcpu_net −234.5 (t −6.08); da_walk −162.1; gpu_busy +22.4 (t 1.97) | −234.48 (77.19); −162.12 (11.06); +22.37 (22.66, t 1.97) |
| secondary (60–88) −231.5 (2SE 102.7), excluded [3, 192] | −231.53 (102.69), same exclusion |
| K1 1 077.1, K2 0, K3/K4 −230.7, K5 +1.41, K6 0 | identical (arm levels = median of block means) |
| vss111 3 944 frames, 0 glitches | identical; log has 3 `BvhLoopCapTrip` lines at frame ≈195 — the known startup BVH loop (same shape in stl110b_5, ent109_1, ent109b_2/3/7 without daslot), not a daslot effect |
| vid111 / check111 PASS: 4 023 frames, 0 glitches, 3 723 scene rows, cspfree_hit 265.79, q_free 1 122.0, slot_bad 0, sync 0 | identical |

**Estimator sensitivity (`robust_shp111.txt`) — the size does not depend on the window:** full block (96 pairs)
−233.3 (81.3); rows 0–29 −193, 30–59 −218, 60–89 −275, 10–49 −233, 50–89 −228; capping flips at 45 / 34.5 ms −224 /
−216; 5 %-trimmed pair mean −252; halves −262 / −200; orientation AB −284 vs BA −177 (z ≈ 1.3, cancels by ABBA).
Arm-independent long flips land symmetrically (≥ 41.7 ms: 57 vs 51 in the main window, by in-window third [20, 21,
16] vs [16, 21, 14]) — the session-110 failure mode is absent. **Mechanism of the gain:** the one-vblank share rises
11.33 → 12.62 % (+1.29 pp, t 5.4); that shift alone implies −222 µs of the −231; within-class means move −8.6 µs.

**Clocks and DRS per arm (`clocks_shp111.txt`, samples mapped to blocks by the log's own timestamps):** GPU SM
2 325 / 2 325 MHz, throttle mask 0x400 in 425/425 and 416/416 samples, power 75.0 / 75.1 W; CPU CCD0 4 620 / 4 624
MHz, CCD1 5 010 / 5 010. Process CPU per 2-s sample 15.34 → 16.07 s (+4.8 %, busy_all 26.4 → 27.7 %): arm 1 burns more
CPU (more threads run concurrently instead of waiting). DRS: rt_kpx/rt_att 2 001.7 / 2 001.3 (Δ −0.36, t −1.6),
rt_att Δ −7.8 (t −0.5) — no area split. Side effects in arm 1 (all within-run, t from paired blocks): `da_late`
5.4 → 10.7 a flip (t 34), `sync_up_kb` +161 (t 9.5), `fault_us` +156 (t 1.96), `semwait_us` −161, `da_wlag_us` −388.

**The size to quote:** −231 ± 82 µs a flip at the pin (≈ +0.73 % game speed) **against `daslot=0` of the same
build** — see MAJOR-1 for why this is an upper bound on the magnitude of the gain over the session-110 build.
Pooling with session 110 is not meaningful (a different knob; wins are not additive).

## Findings

**MAJOR-1 (recount × code) — arm 0 of `shp111` is not "today": the unconditional protocol slows arm 0 in a way that
does not cancel, so Δ = −230.7 µs overstates the gain over the session-110 build.** ROADMAP item 5 calls the guards a
constant cost present in both arms ("их постоянная цена этим ABBA не измерена"). It is not constant across arms: at
`daslot=0` the whole `QueueAhead` — now with two guard exchanges and two releases per `QueueAheadSource`, the
`ahead_queue_mutex`, `ReadHint` seqlock reads and atomic loads — runs *inside* the walker's `m_mutex` hold
(`pipelineCache.cpp:4979-4983`, `:2765`, `:2656-2667`), so the hold that GuestGpu contends with gets longer only in
arm 0; in arm 1 that cost moves off the lock. Indication across the ten runs of the same scene (`guardcost.txt`,
`da_queue_us`/`da_qcall`, walker time per `QueueDrawAhead` call including any lock wait): pre-session builds 1.007,
1.018 (shp110), 1.031 (vid110), 1.032 (obs111, whose measured hold is 0.894 µs/call); post-session builds 1.237
(shp111 arm 0), 1.103 (shp111 arm 1, no `m_mutex` at all), 1.112 (vds111), 1.208/1.239 (vid111/vss111, recording).
The session's own code thus costs the walker ≈ 0.1–0.2 µs a call (≈ 100–230 µs a flip), and at `daslot=0` that sits
in a hold that was ≈ 0.89 µs (+11…25 %). The contended wall GuestGpu pays grows at least proportionally with the hold
(≈ quadratically for random arrivals), so arm 0 carries tens of µs a flip (model: ≈ 30–120) of contention the
session-110 build did not have, and Δ removes it. Separately, the GuestGpu-side guard cost (`TryGuardSlot` +
extra state stores in `AheadTake`, the per-draw `ClassOf` call in `AheadNote`) is in both arms and unmeasured; the
take cost per hit is unchanged in the 600-s runs (0.3412/0.3416 pre vs 0.3404/0.3421 post µs, ≤ ~40 µs a flip) but
+4…8 % in the 120-s recorded runs (vid110 0.355 vs vid111/vss111 0.371/0.382). Between-run dt/cpu comparisons cannot
settle it: shp110 ran in the NEW BDA regime (`bda_scan` 55 a flip) and shp111 in OLD (1 466), and shp110's GPU SM
clock was 2 415 MHz vs 2 325 (`allfields_shp110a1_shp111a0.txt`: shp111 arm 1 is +367 µs dt vs shp110 arm 1 — not
attributable). **The SHIP decision stands** (arm 1 is better than any `daslot=0` of this build, and the
contention it removes is real); **the size is "−231 ± 82 against the slowed arm 0; against the session-110 build
likely ≈ −100…−200 (model, unmeasured)".**
*Do:* quote the size with that qualifier; measure the constant: a `plkstat=1` run of `0c8a13f2` at `daslot=0`
(walker hold per call and contended wall vs obs111's 0.894 µs / 236 µs) or, better, a build-level knob that turns the
guards/publish-once off at `daslot=0` and an ABBA of it against `daslot=1`.

**MINOR-2 (protocol) — vds111b's sealed predictions D1–D5 were never scored** (`vds111b.py` prints totals and the
verdict only; ROADMAP item 5 lists values, not HIT/MISS). All five HIT on this recount. Same defect as session 110's
MINOR (seal 02 predictions unscored). *Do:* every scorer prints every sealed prediction.

**MINOR-3 (protocol) — `check111.py` was published after its run and is outside git.** Generated 05:07:56 (after the
context compaction at 05:07:20), run 05:10:40; its sha `1f740594…` appears first in ROADMAP item 6 (`c314429`,
05:11:09). `check111.py`, `make_check111.py` and `go111v.sh` are not in `docs/session-111/tools` and not in
`SEALS111.txt`. Its docstring is stale (says "vid108.json", "`cspfam` absent", "cspfam_skip > 0"; the code checks
cspfree/daslot). It has no fixtures or mutants, so every mutant survives by construction. Gaps: `slot_default_armed`
(`da_q_free > 0`) cannot tell `daslot=1` from `daslot=2`; `pinned` accepts ≥ 1 pin line; `cs_sync_wait` is printed
but not checked; `rows > 0` is the only row minimum. None of these changes the vid111 outcome (env carries no
`KYTY_DRAW_AHEAD_SLOT`/`KYTY_CS_PREFETCH_FREE`; 1 pin line; 0 waits). *Do:* commit the three files and add their
hashes to SEALS111 marked "post-run"; fix the docstring; give check scripts a small fixture set.

**MINOR-4 (protocol) — the verify evidence is thinner than "60.8 M checks" suggests.** (a) vds111b ran at 42.2 ms a
flip (smemocheck re-materializes every take) vs 31.3 ms shipped, so the walker/GuestGpu interleavings it sampled are
not the shipped ones; the shipped mode `daslot=1` was never run with `smemocheck`. (b) `da_slot_bad` (daslot=2) is
nearly tautological: the single producer writes `source` and `fingerprint` together under the guard, so it can only
fail on memory corruption; the end-to-end evidence is `da_chk_*`. (c) `vds111b.py` ARMED needs only 10 000 checks
(≈ 1 flip) and does not tie checks to hits; it does not read the log's `Gate: daslot=` line. *Do:* next verify run
at the shipped mode with `smemocheck`, ARMED as checks/hits ≥ 0.99.

**MINOR-5 (protocol) — the sealed scorer fails its own fixture suite by design.** `test_shp111.py` on the sealed
`shp111.py` reports `CONSTANTS` FAIL (the draft constants are expected); the 180 fixtures / 209 mutants certify the
draft. Re-run here: identical to `test_shp111_sealed.out.txt` (179 OK + CONSTANTS), so nothing hides behind it, but a
suite that is red on the sealed bytes cannot flag a second difference. *Do:* make CONSTANTS accept the sealed values.

**MINOR-6 (code) — the walker's `GuardSlot` is an unbounded pure spin** (`:2407-2411`, `YieldProcessor` only, no OS
yield). The draw side is bounded (64 spins, then a miss). If GuestGpu is preempted inside its few-instruction guard
window (or inside `ClassOf` in the `daslot=2` check), the walker burns its quantum while holding
`ahead_queue_mutex` (and, at `daslot=0`, `m_mutex`). Liveness is not at risk (the guard holder never waits for the
walker); CPU is. *Do:* spin N, then `SwitchToThread`.

**MINOR-7 (code, perf) — a matching `Taking` slot makes the producer return `busy` without advancing `walk`/`uses`**
(`:2672-2678`): the next walk's draws of that key can then miss or find the slot evicted as "old" (rank 1). Rare here
(`da_q_taking` 0–2 per run). Also: `da_late` doubles at `daslot=1` (5.4 → 10.7 a flip, t 34) — the walker now
refreshes/re-queues concurrently with draws; each late take is a self-materialization. Perf only.

**MINOR-8 (code, comments) — invariants now rest on publish-once, but comments still say `m_mutex`.**
`SourceEntry::plan_fingerprint`/`plan_class` ("only the holder of PipelineCache::m_mutex computes and reads it",
`:1964-1968`) are read by the walker without `m_mutex`; correct only because `AheadNote` computes both before the
seqlock release that publishes the source, and `Fingerprint`/`ClassOf` never write a non-zero/non-null field.
`AheadSlot::taken/pixel` "holder of m_mutex only" (`:2321`) are now guard/Taking-protected; `gates.h` still calls
`daslot=0` "today". A future edit that lets an unpublished source reach the walker (e.g. a hint written before
`Fingerprint`) would be a silent data race. *Do:* update the comments; assert `plan_fingerprint != 0` in the walker
path in debug builds.

**MINOR-9 (code, pre-existing) — `ahead_threads` is mutated by `AheadStartThreads` under `ahead_queue_mutex`
(formerly `m_mutex`) while workers read `ahead_threads.size()` under `ahead_mutex`** (`:2596-2611`, `:2995-2996`) — a
data race whenever the thread knob grows; unchanged in kind by this session.

**MINOR-10 (protocol) — five new `shp111.py` mutants survive its 180 fixtures** (list above): all are threshold
edges with no fixture between the sealed value and the mutated one (arm-0 `da_q_free` 1–5, hold 550–594 s, area
pairs < 8 flips, walk identity 1–10 %, exactly 3 000 video frames). None matters for this run (arm-0 Σ`da_q_free` 0,
hold 600 s, identity 0.0001, 3 944 frames), so the SHIP verdict is unaffected; the "209 mutants killed" figure
overstates edge coverage. *Do:* one edge fixture per threshold.

## CODE — what was checked and found sound at `daslot=1`
- **Slot table:** producer (walker or GuestGpu's own walk, serialized by `ahead_queue_mutex`) holds both probe guards
  (address order) for the whole decision; the draw holds at most one guard at a time with a bounded spin; workers never
  guard → no deadlock, no lock-order inversion (`m_mutex` → `ahead_queue_mutex` everywhere; nothing inside
  `QueueAhead` takes `m_mutex`).
- **State machine:** Empty/Failed/Ready(old)/Queued(old, CAS-cancelled) are the only victims; Running and Taking never
  are. Key fields are written under the guard before `state.store(Queued, release)`; a worker's CAS
  `Queued→Running` (acq_rel) sees them; stale ring entries only ever run the slot's current key (harmless, as before).
  The draw moves Ready→Taking under the guard, and every exit after it publishes Ready (uses > 1) or Empty (last use,
  stale witness) with release; `taken`/`uses` are written before those releases → no `Taking` leak (except on an
  exception, where the process dies anyway). The ring-full `Queued→Empty` CAS runs without the guard but only on
  Queued and is idempotent with the draw's own cancellation. No ABA: every re-key happens under the guard.
- **Hints/variants:** Boehm seqlock (writer `seq+1` relaxed, release fence, relaxed body, `seq+2` release; reader
  acquire, relaxed body, acquire fence, relaxed recheck) — correct; all writers hold `m_mutex`. Variant key/source
  pairs can tear across two writes, but the reader only accepts a source already in the hint → a wrong guess, not a
  wrong result. `hint_torn` 0 in every run.
- **Lifetimes:** source entries are never freed while the cache lives (`retired_sources` keeps extracted nodes,
  `:3657-3663`; `programs` is a node-based `unordered_map`); `srt_compiled` is set once and never reset
  (`SrtWalker.cpp:1813-1821`); `PlanClass` never freed; `ahead_slots` allocated once, never reset; the walker thread is
  joined in `GuestGpu::Shutdown` (`graphicsRun.cpp:131-135`) — shutdown ordering is unchanged by this session (at
  `daslot=1` the walker no longer serializes with `m_mutex`, but nothing in shutdown relied on that). A `memo_generation` bump mid-queue
  only yields unmatched slots.
- **`daslot=0` vs the pre-session code:** same lock and same decisions, plus guards, `ahead_queue_mutex`, seqlock
  reads, the extra Ready store on multi-use takes, eager `Fingerprint`/`ClassOf` in `AheadNote` and deferral of
  hints until `srt_compiled` exists (`da_hint_defer` ≈ 1 a flip in both arms — sources the old code queued as
  `no_plan` anyway). Behaviourally equivalent; performance-wise slower (MAJOR-1).

## PROTOCOL — timeline (local time)
| when | what |
|---|---|
| 03:03:21 edit, 03:03:27 `1f488f7` | ROADMAP items 1–3 (obs rule, protocol, runs) |
| 03:06:43–03:09:21 | code `690c40e`, `dc1136b`, `6b340d7` (after the records); binary `c8235c90` copied 03:09:43 |
| 03:27:18 `d6c1264` | seals 01, 02 + scorers (SEALS111 lines 1–10) |
| 04:33:16 `be8d862` | seal 03 + `shp111.py` + `go111.sh` |
| **04:33:23–04:44:26** | go111: obs111 → BUILD_DASLOT, vds111 → NOT_ADMITTED; only `ScheduleWakeup` + heartbeat |
| 04:45:19 edit, 04:46:48 `27aa877` | ROADMAP item 4 (the 02b replacement, with vds111's numbers disclosed) + seal 02b |
| **04:46:51–05:05:40** | go111b: vds111b GO → shp111 SHIP_PENDING_VIDEO → vss111 → SHIP; only `ScheduleWakeup` + heartbeat |
| 05:05:55 edit, 05:06:03 patch, 05:06:04 `38d8f86` | ROADMAP item 5 edited before `gates.cpp`; build after the chain ended (log 05:06:19) |
| 05:07:50–05:07:56 | `make_check111.py`, `check111.py` generated (unsealed) |
| **05:08:04–05:10:40** | go111v: vid111 + glitch scan + check111 PASS; nothing else |
| 05:11:06 edit, 05:11:09 `c314429` | ROADMAP item 6 (vid111 result, audit decision) before this audit (05:11:47) |

All 22 SEALS111 hashes match the files; every run JSON's `prereg` carries the sealed sha/bytes; subagent transcripts
(14) have 0 tool calls inside any window; `mtime_scan.txt` lists only the runs' own outputs (plus `gates.req`,
`sample.req`, `_kyty*.txt`, `_PipelineCache` written by the launcher/emulator). Fixture suites re-run in
`audit111/rerun`: `test_shp111` 180 cases, `test_vds111b` 47, `test_obs111` 78 — outcomes identical to the sealed
`*_sealed.out.txt` (paths aside).

**New mutants (`newmut.py`, `newmut.txt`; none in `mut_shp111.py`'s 220 names):** 20 written, **15 killed, 5
survived**. `vds111b.py` (no mutation record existed for it): 8/8 killed (checks floor 10 000 → 1, BAD without the
lines, pin ≥ 1, rows 4 000, smemocheck count, hold 0.5×, precache env, stdout markers). `shp111.py`: 7/12 killed
(S2 `< 0` → `<= 0`, three FATAL markers dropped, gpu_busy band widened, `da_q_taking` dropped from the schema, drop
fraction loosened to 1.0); **survivors (MINOR-10):** `SLOT_DARK_tol5` (arm-0 Σ`da_q_free` = 0 → ≤ 5),
`HOLD_tol_50` (hold_s tolerance 5 → 50 s), `AREA_min_flips_0` (area-mirror min flips 8 → 0), `ID_TOL_10x` (walk
identity 1 % → 10 %), `VIDEO_frames_strict` (≥ 3 000 → > 3 000). `check111.py` has no fixtures, so every mutant
of it survives by construction (MINOR-3).

## What should be done
1. Quote `daslot`'s gain as −231 ± 82 µs **against `daslot=0` of the same build** (≈ +0.73 % game speed at the pin)
   and state that the gain over the session-110 build is unmeasured and likely smaller (MAJOR-1); measure it
   (a `plkstat` run at `daslot=0` of the new build, or a guard-off knob in an ABBA).
2. Score vds111b D1–D5 formally (all HIT) and make every future scorer print every sealed prediction.
3. Commit `check111.py`, `make_check111.py`, `go111v.sh`; record their hashes (post-run); fix the docstring.
4. Next verify run of this kind: the shipped mode with `smemocheck`, ARMED tied to checks ≈ hits.
5. Code hygiene: bounded-then-yield `GuardSlot`; comments on `plan_fingerprint`/`plan_class`/`taken` ownership;
   `gates.h` "today".
6. One edge fixture per threshold in `test_shp111.py`'s successor (the five surviving mutants).
