# Session 98 — route E, measurement M3 (third attempt) — FACTS

**This file is the only source of truth for session 98** (in git `docs/local-session-98.md`).
Anything not in it is not a result of this session. A run that failed admission appears only as a
replaced or failed run, and none of its contrasts is quoted.

## 0. The three numbers route E opens with

* budget **≤ ~3.0 µs a draw** (median frame), **≤ ~2.3 µs** (p99 frame, 7 284 draws);
* today **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms**;
* of M1–M5 undone: **M3 (its verdict is GAP — it continues), M4, M5** (order M3 → M4 → M5 kept).

**60 FPS is not promised** (~15 %, 8–25 %). Nothing in this session moves it.

**The user's decisions this session (asked before any number).** (1) The synchronisation term of
the M3 rule: **submission granularity** (`bd96b`, +103.5 µs) ⇒ `VERDICT_INPUT = F_st + 1.66 + 0.49 +
0.1035 = F_st + 2.2535` ms; the sealed `+2.65` is printed beside it for ever. (2) The trigger test
that hangs the GPU on purpose: **yes, two processes**.

## 1. What this session settled

1. **M3 has a number, and its verdict is GAP.** On the frame-latched floor, both instruments
   admitted: **`F_a` = `F_st''`(`bf98a`) = 14.274 ms, `F_c` = `F_st''`(`bf98c`, no M1 workers) =
   12.825 ms** ⇒ `VERDICT_INPUT` low **15.078**, high **16.527** ms. CLOSE needs low ≥ 15.5 (short by
   0.42 ms), PROCEED needs high ≤ 11.0. **Nothing closes, nothing proceeds; G and R1 stay alive and
   unlicensed; by session 96's sealed §3 a bindings-only arm (`bfmode=2`, `KYTY_BIND_FLOOR_CLEAR=0`)
   is scheduled and M3 continues.** With the sealed 2.65 the low value would be 15.475 — GAP too,
   0.025 ms under the threshold.
2. **The runaway ops are NAMED, by a new instrument, without device loss** (`KYTY_GPU_MARKERS`,
   §3): in `trig98a` the **floor-edge hang is the OIT resolve `cs=0x657ad04626bf9d55`** (a per-pixel
   linked-list walk until `next == 0`, no cap) and the **ENTRY hang is a BVH traversal
   `cs=0x380bb9d636390bae`** (one of the 13 programs whose leaf/stack walk has no step bound). Both
   `prior_done=1 culprit=op` (everything before them had finished), no progress in 1 s. **The
   historical entry hang (6.67 % of entries) and the floor-edge hang are two different shaders.**
3. **The frame-latched floor is reversible.** `rv98a`: 11/11 on the counted attempt, 10/10 on the
   warmup, **857 falling edges and 0 GPU hangs** in 2 × 600 s (session 97's rate, 3 in 489, gives
   that with P ≈ 0.005). Every arm change adopted at index 0 of the new block (865/865, 851/851).
4. **A floor defect outside its charter was found and closed**: the floor reuses ONE snapshot per
   program taken at the FIRST floored materialisation of the process (not the last, as the sealed
   texts of sessions 96–97 said), and the compute clear shortcuts ran BEFORE the floor branch on
   it — real clears, `ClearMeta` and `TrackDccFill` at stale addresses in every floored frame.
   `KYTY_BIND_FLOOR_CLEAR=1` routes those dispatches down the floor branch.
5. **The session-97 "GDS marker" was weaker than recorded**: `gds_bar` is 0 in the last armed flip
   before 76/76 (`rv97b`) and 116/116 (`rv97a`) falling edges; the direct-write table that showed the
   site resets a row's delta whenever row order changes. The trigger was therefore tested causally.

## 2. The mechanism

Read-only lenses (workflow `wf_34b720f2-a88`; texts `C:/kyty/s98/design98/{latch,naming,gds,loops}.md`)
and `trig98a`:

* **All 57 guest queues run on the one GuestGpu thread**, round-robin at submission granularity,
  into one CommandScheduler and one VkQueue; the guest frame boundary on GuestGpu is the flip PM4
  packet; GuestGpu reaches flip packet N+1 after the presentation thread's `Poll(N)` on 100 % of
  7 720 scheduled flips of session 97. Under the per-op latch of session 97 every edge therefore
  switched the floor MID-FRAME.
* **OIT:** 14 pixel shaders append nodes (GDS counter, reset by PM4 `DMA_DATA`, never floored) and
  exchange a per-pixel head image; the resolve `657ad046…` walks the list until `next == 0` and
  the whole wave loops while any lane walks. If the head clear is floored and the producers run
  real, new nodes link to heads left by the last real frame 10–30 flips earlier — a cycle, and the
  wave never returns. `trig98a` forced exactly that tear (the falling edge held floored until the
  first GDS consumer — 947 floored ops, then an OIT-producer draw) and the resolve hung **in that
  frame**.
* **BVH:** 13 compute programs traverse a BVH with no step counter (leaf loop exits only on a
  sentinel read from memory; the game's invalid-TLAS `S_TRAP` is translated as a no-op). One of them
  hung on ENTRY at flip ~190 in `trig98a`'s counted attempt, before any schedule.
* **Also uncapped:** the GPU hash-table probes `81f39ef20546ebae` / `e4c97c75ce70efc3` (exit only on
  the key or `0xFFFFFFFF`). Not implicated by any run.
* **The frame latch removes the tear inside a queue but not across queues.** At EVERY flip packet
  one ACB submission enqueued right after the flip-bearing DCB (`queue=39`, 14 ops,
  `seq = s_flip + 1`) had already run entirely under the old value (`bf_xover_acb` 866 at 865 arm
  changes in `rv98a`). It hung nothing in 857 falling edges. Whether it belongs to frame N or N+1
  cannot be told from sequence numbers.

## 3. The instrument changes — commit `d7828b1`, binary `9aa93e73673e8c53…`

All switches are ENVIRONMENT variables read once per process (never gates: they cannot tear and do
not touch the gate-order tables); without them the binary behaves as HEAD except for new counters
printed as 0. Patches `C:/kyty/s98/patch_s98a.py … patch_s98e.py`; b, c, d reviewed by independent
agents before any run (workflows `wf_58b5c6a4-a8d`, `wf_8557653e-895`).

| env | what | counters / lines |
|---|---|---|
| `KYTY_BIND_FLOOR_LATCH=1` | **frame latch**: the scheduled value is adopted at a guest flip packet by submission sequence number (older submissions keep the old value, later ones take the new), sticky per submission (the flip-bearing DCB has one value before and one after its flip), the base changes when every older submission completed; GC keep-alive also while any running submission holds an armed sticky value | `bf_xover`, `bf_xover_acb`, `bf_defer`, `bf_defer_force`, `bf_mixed`; `BindFloorXover:`, `BindFloorMixed:` |
| `KYTY_BIND_FLOOR_LATCH=2` | **trigger test**: a falling edge is held floored until the first draw/dispatch whose shader key the base arm saw issue a real GDS barrier | `bf_trig_fire`, `bf_trig_wait`, `bf_trig_fb`; `BindFloorTrigger:` |
| `KYTY_BIND_FLOOR_CLEAR=1` | an armed op with `bfmode != 2` skips the compute clear shortcuts on the frozen snapshot (takes the floor branch) and drops an armed `bf_skip` op instead of running the real binding path over the snapshot | `bf_clr_skip` (by shape — an UPPER bound), `bf_skip_drop` |
| `KYTY_GPU_MARKERS=1\|2` | `VK_AMD_buffer_marker` TOP/BOTTOM (+ `pre` BOTTOM_OF_PIPE before each op at 2) around every draw and game dispatch; CPU op ring; readout at `GpuWaitSlow`/`GpuHangAbort` with the device NOT lost; the NV checkpoint query only after device loss (`ReportGpuCheckpoints` split) | `gm_ops`, `gm_ok`, `gm_bad`, `gm_unsup`, `gm_live`, `gm_live_top`; `GpuMarkerHung:`, `GpuMarkerInFlight:`, `GpuMarkerTick:`, `GpuMarkerGap:`, `GpuMarkerVisibility:`, `GpuMarkerProgress:` |
| `KYTY_QUEUE_TRACE=2` | `=1` plus the op ranges and cs/vs/ps hashes of every submitted tick | `GpuSubmitOps:` |

Harness: `enter_scene.py` `rotate_log()` waits up to 180 s for a log a hung process still holds
(the dead process keeps its handles until the TDR); scorers `trig98.py`, `rv98.py`, `bf98.py` (v3),
`m3_98.py`; `accept98.sh`.

## 4. Runs (binary `9aa93e73…` for every run)

| tag | what | result |
|---|---|---|
| `smk98a` | smoke, no schedule, latch 1, clear 1, markers 2, 90 s | alive; `gm_ok` every flip, `gm_bad` 0, `gm_live` > 0; `dt` median 33.4 ms |
| `trig98a` | trigger test, latch 2, clear 0, markers 2, period 10 | warmup hung at its 9th falling edge — **OIT resolve**; counted attempt hung on ENTRY — **BVH traversal**; the harness then died on the locked log (fixed). **H1: INCONCLUSIVE by the sealed rule** |
| `rv98a` | proof, latch 1, clear 1, period 10, 2 × 600 s, video | **11/11 (warmup 10/10), 857 falling edges, 0 hangs** |
| `bf98a` | M3, period 30, `bfburn=16400` | **ADMITTED**: `F_st''` 14.274 ms |
| `bf98c` | M3 without the M1 workers, `bfburn=18800` (`B_c`) | **ADMITTED**: `F_st''` 12.825 ms |

### 4.1 `trig98a` — the sealed verdict and why

Warmup: 9 falling edges, the trigger fired at each (9 `BindFloorTrigger: fire` lines; 8 in reported
counter rows), hung in the flip of the 9th, 129 s into the hold: `GpuMarkerHung … cs=0x657ad04626bf9d55
args=4096,1,1 floor=0 started=1 prior_done=1 culprit=op`, identical at `slow` and `abort`,
`progress=0`. Counted attempt 1: `GpuHangAbort` at flip ~190 (no `GateArm` yet):
`cs=0x380bb9d636390bae args=1,2048,1 floor=0 prior_done=1 culprit=op`. H1 is INCONCLUSIVE by the
sealed rule: the counted attempt's hang was on entry, and — a defect of `trig98.py` — the fatal
edge's `bf_trig_fire` is booked in the flip the process dies in, which is never reported, so T3 read
8/9 = 0.889 < 0.90 and the warmup hang read "not countable". The sealed rule was not re-scored and
the stopping rule held (no repeat). Controls: T1, T1b, T2, T4 PASS on the warmup.

### 4.2 `rv98a` — the proof

| criterion | counted | warmup |
|---|---|---|
| R1 survival | 600.2 s | 600.2 s |
| R2 falling edges | 432 | 425 |
| R3′ | 1 730 boundaries, 0 wrong, 0 stray; Σ `bf_edge` 865 = 865, all at idx 0 | 851 = 851, all at idx 0 |
| R4′ (DARK98) | 0 disallowed, 0 last-index | same |
| R5 | 0 | 0 |
| R6 / R6′ | 20 / 26 | 15 / 21 |
| R7 / R7′ | 1 / 3 | 1 / 2 |
| R8 | `bf_mixed` 0, `bf_defer_force` 0 | same |
| R9 | both survive, 857 falling edges | — |

Reported: R8x `bf_xover_acb` > 0 at 432/432 falling edges (425/425); `bf_defer` at every adoption;
`bf_clr_skip` 196.08 a floored flip; D1 `f_fall` 0.895, `f_rise` 0.744, `1 − lat/dt` 0.642 (outside
D1's reported band). Criterion 3 VALID (split +0.004 %, 850/850 pairs). Guards (not criteria):
check 3 FAIL (DRS moved the targets; 9.55 % fragment flips), check 6 FAIL (this session's review
agents ran dry runs during `rv98a`), check 9: 85 one-frame detections of amplitude ~4 in 19 116
frames — inside floor blocks the presented image alternates between two stale frames; no
black-material frame as in `rv97a`. The video pass of the new instrument is taken.

### 4.3 `bf98a` and `bf98c` — M3 (`pred/02_m3_frame.md`)

|  | `bf98a` | `bf98c` |
|---|---|---|
| schedule | `bindfloor=0\|1`, `bfmode=3 bfburn=16400`, P 30 | + `drawahead=1\|0`, `bfburn=18800` |
| criterion 3 | VALID, −0.002 %, 128/128 | VALID, +0.002 %, 122/122 |
| C1‴ C2′ C3′ C4 C5 C6′ C7 C8″ C9″ C10‴ | all PASS | all PASS |
| C9″ | 0.0148 (armed 30 833.8 / unarmed 31 298.2 µs) | 0.0032 (32 346.1 / 32 242.6) |
| C11–C20 (R1, R2, R3′, R4′, R5, R6, R6′, R7, R7′, R8) | 10/10; 66 falling edges | 10/10; 63 falling edges |
| bf_edge position | idx0 133/133 | idx0 127/127 |
| **`F_st''`** (T*-trimmed, deciding) | **14.274 ms** | **12.825 ms** |
| `F_st` narrow T / untrimmed (printed only) | 14.139 / 14.404 | 12.817 / 13.167 |
| C8″ net armed / unarmed | 14 266.6 / 30 900.7 µs | 12 867.5 / 31 329.2 µs |
| `E''` (burn check) | −269.4 ± 90.5 µs, t −5.95 | +281.8 ± 106.0, t +5.31 |
| `E_net''` | −16 635.0 ± 81.4 µs | −18 461.8 ± 98.3 µs |
| `W''` `da_walk_us` armed / unarmed | 1 868.8 / 1 817.5 | 723.9 / 1 893.6 |
| `da_work_us` armed | 26 852.9 | 0.0 |
| L3 bound | 1.578 ms (198.01 `bf_clr_skip` × 7.967 µs) | 1.577 ms |

`B_c = 16400 + round_100(1868.8) + round_100(31298.2 − 30833.8) = 16400 + 1900 + 500 = 18800`.
`F_a − F_c` = 1.449 ms (walk 1 145 µs less, the rest the four M1 workers). **VERDICT (m3_98.py):
low 15.078, high 16.527 ⇒ GAP**; sealed 2.65: 15.475 / 16.924 ⇒ GAP. Both runs' `F_st'' ± L3`
straddle 13.2465 ms, which by `pred/02` §4 also takes the gap branch (the script prints the straddle
as "reported, not deciding" — a wording difference from the sealed text with the same outcome).
Guards: check 6 FAIL on both (2/52 and 1/48 groups; no background work of mine ran; `ds4windows.exe`
and `tabtip.exe` were on the GPU) — not a criterion.

Predictions of `pred/02` §6: Q1 HIT, Q2 HIT, Q3 HIT (14.274 in [12.5, 16.0]), Q4 HIT (1.449 in
[1.0, 4.0]), Q5 HIT (GAP), Q6 HIT (1.578 ≤ 1.6). `pred/01` §6: P1 SUPPORTED → INCONCLUSIVE; P2 the
modal class named; P3 HIT; P4 MISS (the scorer defect); P5 HIT; P6 HIT (100 % idx0); P7 MISS (xover
at 100 % of edges, predicted ≤ 50 %); P8 HIT; P9 HIT; P10 MISS.

## 5. Sealed pre-registrations of this session — not to be edited

| file | bytes | sha256 |
|---|---:|---|
| `pred/01_hang_trigger.md` | 19 391 | `aca036c1a094c18176ad5ac04f69f9ed8a926bf81ac1d6f63760f8493c071cd3` |
| `pred/01b_entry_hang.md` | 4 202 | `3884109387e44f520b63fe5684340fc1828111dda30a7b99bdb9098ac41d49b6` |
| `pred/02_m3_frame.md` | 11 825 | `83144a3dfeff531eccd1da0bef91cdf882e4fcf4d6a70d8545f1ed9a53354389` |

## 6. Defects of this session's own work

1. `trig98.py` could not count the fatal edge as fired (its counter row is never written) — T3 and
   "countable" fail by construction for a hang in the fire flip (§4.1).
2. `rv98.py` R3′ as first written ignored the arm change block 0 → 1 (its window started at blk 1)
   and would have FAILed `rv98a` on its first edge — found by review before `rv98a` was scored,
   fixed to implement the sealed text (Σ `bf_edge` = number of arm changes, 0 → 1 included).
3. `bf98.py`: 12 defects in v1 and 3 more in v2 (a `--log` dry run could overwrite and DELETE a real
   log; orphan blocks; the per-block leak count) — all before `pred/02` was sealed.
4. The patches: the positive control first proved visibility only after a signal (added
   `gm_live`), a TOP marker alone could not separate "op k hung" from "work before k hung" (added
   `pre`), the sticky value let the GC run under floored ops (patch e).
5. `enter_scene.py` died launching the next attempt while a hung process still held `_kyty.txt`.
6. Review agents ran scorer dry runs during `rv98a` (guards check 6). Nothing ran during `bf98a/c`.
7. **Disclosure:** a mechanics check of `bf98.py` on `rv98a` AFTER `pred/02` was sealed printed
   `F_st''` ≈ 14.6 ms for that period-10 proof run; it is not a measurement and is quoted nowhere.
8. `m3_98.py` labels the L3 straddle "not deciding" while `pred/02` §4 makes it take the gap branch;
   the verdict is GAP either way.

## 7. Not closed

* **M3: the gap branch.** A bindings-only arm (`bfmode=2`, `KYTY_BIND_FLOOR_CLEAR=0`) needs its own
  sealed pre-registration: what it measures and what rule it feeds were never written (session 96's
  §3 only schedules it). The M3 constant `2.2535` stands.
* **The L3 bound is crude** (1.58 ms; `bf_clr_skip` counts by shape): a counter of the shortcuts
  actually taken in the base arm would tighten it; it cannot enter a proven binary retroactively.
* **The cross-queue tear** (`bf_xover_acb` at every edge) is not removed; it would need the flip to
  be known at ENQUEUE (a PM4 scan of the DCB for the flip packet) to assign frames by sequence.
* **The entry hang** (BVH traversal `380bb9d6…`, historically 6.67 % of entries) — a real
  correctness bug of the emulator, not route E. The capped-loop design is ready
  (`design98/loops.md`: `KYTY_BVH_LOOP_CAP`, in the cache signature, trip counter in the fault-buffer
  tail); the OIT resolve and the hash probes can be capped the same way.
* M4, M5; the general hazard "any gate read twice inside one op can tear" (only `bindfloor` fixed);
  `PrefetchComputePipelines` 245 µs a call; the 1 921.6 µs residue outside the mutex; the BDA
  regime; the written `bc_ok` slots; `C_bda` in NEW; the GPU side of `bdaall`; the single-chunk
  notify; the `ObtainBuffer` ring timer; `pfhint`/`pfcap`/`dapin` with the pin; route B.
