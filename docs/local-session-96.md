# Session 96 — route E, measurement M3 — FACTS

**This file is the only source of truth for session 96.** Anything not in it is not a result of
this session. Numbers from a run that failed admission appear here only as replaced runs, and are
never quoted as measurements.

## 0. The three numbers route E opens with (`ROADMAP.md:1210-1212`)

* budget **≤ ~3.0 µs a draw** on a median frame, **≤ ~2.3 µs** on a p99 frame (7 284 draws);
* today **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms** (pinned p50 12.83 / p90 13.94 /
  p99 15.77);
* of M1–M5 still undone: **M3, M4, M5**.

**60 FPS is not promised.** ~15 % (8–25 %); session 96 did not raise it and did not lower it.

## 0.1 What this session did and did not settle

**Settled.** The two decompositions `ROADMAP.md:1051-1052` names as part of M3 — *"цепочки отметок,
делящие время ВНЕ мьютекса (4,05 мс, никогда не разделено) и `mh_emit` за вычетом CommitBindings
(~5 мс, не разделено)"* — **are now split** (§2, run `pl96a`, admitted). Neither had ever been
split in ~96 sessions.

**Settled, and it is a trap turning into a measurement.** The dynamic-resolution trap of
`ROADMAP.md:1062-1065` **fired, and was measured**: a translation path made twice as fast pushed
the game from 2 002 Kpx to **8 037 Kpx — 4.014×, native 4K** — within 30 frames (§3).

**Settled, and it is a property of the instrument, not of the emulator.** The ceiling stub
`bindfloor` **cannot be an ABBA arm as built**: it is not reversible, and the run freezes at the
schedule's return to the base arm (§4).

**Settled.** The M3 rule's third term, `+0,5 мс (синхронизация)`, was an assumption and is now
measured at one of its two candidate granularities: an extra `PrepareBda` at every end-of-pipe
label costs **+2 893.6 ± 93.2 µs a flip — 5.8× the assumed 0.5 ms** (§5). The submission
granularity is still unmeasured.

**NOT settled: `F_st`.** No admitted run produced it. **M3 is therefore NOT closed, and G and R1
are neither closed nor licensed.** The sealed rule of `ROADMAP.md:1052-1053` was not applied to
any number, and no verdict on G or R1 follows from this session.

## 1. The runs

| tag | binary | what | admission | status |
|---|---|---|---|---|
| `pl96a` | `65fca20dd4bc8528…` | gate `pathlap`, both splits | criterion 3 **VALID**, controls **7/7** | **ADMITTED** |
| `bf96a` | `65fca20dd4bc8528…` | gate `bindfloor`, `bfmode=1` | criterion 3 **INVALID** (0 rows at n ≥ 2100) | **REPLACED** |
| `bd96a` | `65fca20dd4bc8528…` | knob `bdaevery=2` | criterion 3 **VALID**, controls **6/6** after `pred/05` | **ADMITTED** |
| `bf96b` | `993be4a85af569c4…` | `bindfloor`, `bfmode=3 bfburn=16400` | criterion 3 **INVALID** (0 rows at n ≥ 2100) | **REPLACED** |

`guards.py` check 6 (cores) FAILed on `pl96a` and `bd96a`. **It is not a criterion** — stated in
`ROADMAP.md`, in `accept96.sh` and in the pre-registrations before the runs.

`pl96a` and `bd96a` were accepted against binary `65fca20d…`; `bf96b` ran on `993be4a8…`, built
after them to carry the download-ring repair. Their acceptances cannot be re-run against the
binary installed now, and that is stated rather than hidden.

## 2. `pl96a` — ADMITTED. The two splits of M3

Gate `pathlap` (`KYTY_PATH_LAP`, default 0, measurement only), ABBA `pathlap=0 mutsite=1` |
`pathlap=1 mutsite=1`, `KYTY_GPU_CLOCK_PIN=1`, window n ≥ 2100, 129 matched pairs.
Criterion 3: split **+0.002 %**, pairs **129/129**, work **+0.134 %** → VALID.
Controls **7/7**. Predictions **10 HIT / 2 MISS / 0 NOT EVALUABLE**.
Instrument price **+362.9 ± 80.8 µs (2·SE), t = +8.98** on 129 pairs = 0.072 µs a draw.

### 2.1 `mh_emit` beyond `CommitBindings` = **4 893.3 µs a flip** — split

| phase | µs a flip | of EMIT |
|---|---:|---:|
| `CommitBindings` | 2 245.1 | 31.45 % |
| `AcquireRenderTargets` | 1 546.8 | 21.67 % |
| vertex + index buffers | 1 336.7 | 18.72 % |
| BeginRendering + dynamic state + `EmitDrawPrimitives` + record | 1 215.8 | 17.03 % |
| `GetGraphicsPipeline` | 748.7 | 10.49 % |
| remainder (debug dump, async-pipeline early return) | 45.4 | 0.64 % |
| **EMIT** | **7 138.5** | 100 % |

`EMIT / mh_emit_us` = 0.9860 (7 138.5 against 7 239.7) — the chain closes.

### 2.2 Outside the render mutex = **4 620.7 µs a flip** — split

`pl_proc_ns` 31 037.1 − `hold_gpu` 26 416.4 = OUTSIDE 4 620.7 (ROADMAP's 4.05 ms; in band).

| region | µs a flip | of OUTSIDE | calls a flip |
|---|---:|---:|---:|
| **`PrefetchComputePipelines`** | **1 961.1** | **42.44 %** | 8.0 |
| `ProcessCommands` | 563.5 | 12.20 % | 26 207.3 |
| `RunGarbageCollector` | 67.2 | 1.45 % | 8.0 |
| `BufferFlush` + `BufferFlushLazy` | 53.5 | 1.16 % | 539.9 |
| `WriteAtEndOfPipe` (the EOP labels) | 43.1 | 0.93 % | 369.1 |
| `EmitGlobalBarrier` | 10.8 | 0.23 % | 1 123.2 |
| **named** | **2 699.1** | 58.41 % | |
| **RESIDUE — attributed by no session** | **1 921.6** | **41.59 %** | |

`pl_look_ns` = **1.2 µs** (8.0 calls) is reported and NOT summed: `LookaheadSubmission` runs on
the guest submit thread (`GuestGpu::Enqueue`, `graphicsRun.cpp:630`), outside `GuestGpu::Process`.

### 2.3 The two misses, both informative

* **P8 MISS — the EOP labels are cheap.** `pl_eop_ns` **43.1 µs** a flip against the band
  [150, 1600], i.e. **0.117 µs per label** at 369 labels a flip. The label writes the CPU makes at
  PM4 parse time — the design constraint that killed zero-copy in session 66 and the D1 import in
  session 91 — cost 0.9 % of the outside-mutex time. **Whatever makes a guest-memory snapshot
  expensive, it is not the writing of the labels.**
* **P5 MISS — vertex/index plus render-target acquisition is dearer than predicted**: 2 883.4 µs
  against [1000, 2800].

### 2.4 The single largest named item outside the mutex

`PrefetchComputePipelines` at **1 961.1 µs a flip over 8 calls = 245 µs a call**, 42 % of the
outside-mutex time and **6.2 % of the whole 31.6 ms frame**. It has never been measured before.
It is the PM4 look-ahead walk that feeds `drawahead` and the compute prefetch, both shipped at 1.
**This is a lead for a later session; nothing in this session tests whether it can be reduced.**

## 3. `bf96a` — REPLACED. The DRS trap, measured

`bindfloor=1 bfmode=1`. The stub armed at frame 1830 and the process died at frame 1868 with

    TextureCache: failed to map reusable download buffer   textureCache.cpp:2842

**Cause, established by code and by the log, not by argument.** The stub halved the frame, the
game answered by climbing the DRS ladder, and a linear colour target outgrew the 32 MiB Download
ring (`bufferCache.cpp:377`):

| frames | `rt_kpx/rt_att` | `dt_us` |
|---|---:|---:|
| 1700–1830 (arm 0) | 2 002 Kpx (1920×1080) | 33 218 |
| 1841 | 2 567 | |
| 1842–1852 | 3 203–3 234 | |
| 1853–1858 | 6 016–6 041 | |
| 1860–1867 (arm 1) | **8 009–8 051 Kpx (3840×2160)** | 16 785 |

**4.014× the area.** At 2 002 Kpx a linear target is 16.0 MiB and fits; at 8 037 Kpx it is
**62.8 MiB against a 32 MiB ring**. `StreamBuffer::Map` returns null only on
`mapped_size > Size()` here — a full ring WAITS (`allow_wait` defaults true,
`streamBuffer.h:121`), so the failure is by size, not by pressure.

**This is prediction P10 of `pred/02_bindfloor.md`, and it HIT.** The trap of
`ROADMAP.md:1062-1065` had only ever been argued. It is now measured, on this machine, with
numbers: **a translation path that gets fast makes the game render four times the area within 30
frames.** Any future work on route E has to solve the DRS clock before it can measure anything.

**Nothing from this run is a measurement of the floor.** Its arms drew 1× and 4.014× the area.

## 4. `bf96b` — REPLACED. The stub is not reversible

`bindfloor=1 bfmode=3 bfburn=16400`, on binary `993be4a8…` which turns the download-ring `EXIT`
into a counted skip under the gate (`bf_dlskip`).

**The burn worked.** Floor-arm `dt_us` 33 126 / 33 502 against the base arm's ~33 000;
`bf_burn_ns` 17.53 ms a frame; `bf_dlskip` **0** — the ring never overflowed, the DRS never
climbed, `draws` 5 275–5 424 against the base 5 436. No crash.

**And the run still froze — at the schedule's return to the base arm.** The last three schedule
blocks:

    GateArm: arm=1 block=1 frame=1830  bindfloor=1 bfmode=3 bfburn=16400
    GateArm: arm=1 block=2 frame=1860  bindfloor=1 bfmode=3 bfburn=16400
    GateArm: arm=0 block=3 frame=1890  bindfloor=0 bfmode=3 bfburn=16400   <- last line of the log

1 889 flips, nothing after. The stub reuses the last materialisation of every program
(`bf_mat` 0, `bf_reuse` 10 168) and restores nothing when the gate goes off.

**Conclusion, and it is the design finding of this session: `bindfloor` as built cannot be an ABBA
arm, and `ROADMAP.md:1048` requires ABBA.** A future version must either make the floor reversible
(drop every reused snapshot and every cached null set when the gate turns off) or M3 needs a
different shape. **Until then `F_st` cannot be measured at all**, and no reading of the M3 rule
follows.

## 5. `bd96a` — ADMITTED after the controls were repaired. The synchronisation term is measured

**Result: at label granularity an extra `PrepareBda` costs +2 893.6 ± 93.2 µs (2·SE), t = +62.08
on 119 pairs — 5.8× the "+0,5 мс (синхронизация)" the M3 rule assumes.**

`bdaevery=0 | bdaevery=2`, 611.84 extra calls a flip, `be_ns` 4 853.4 µs a flip = **7.93 µs a
call including the render-mutex wait** (the hook takes it, and the timestamp sits above the lock,
by design — a real synchronisation point would wait too). `prot_gpu_us` +1 050.5, `fw_win_recent`
+229.3: the re-protect/refault cycle of session 94 §3.2 is present at 1/13 of `bdaall`'s call
count. Both arms are in the NEW BDA regime, and the unarmed arm held 50/50/50 across every window.

Predictions **5 HIT / 0 MISS / 3 NOT EVALUABLE** (P4, P5, P8 belong to `bd96b`, which was not
run). **P7 HIT: the term does NOT survive measurement at the granularity `gpu-driven.md:136`
specifies.** The submission granularity (`judge.md:116`, ~8 calls a flip) is **NOT MEASURED** —
which of the two M3 is entitled to use remains the user's choice, and this run supplies only one
of the two numbers.

### 5.1 The two controls that had to be repaired first

Criterion 3 was VALID from the start (split −0.002 %, pairs 119/119, work −0.168 %), but 2 of 6
controls failed, and both were defects of the sealed text, not of the instrument. Repaired under
`pred/05_bdaevery_controls.md` (9 087 B, sha256 `352448acaacd9b40…`); the sealed FAIL lines stay
in the scorer's output for ever.

* **C3 was confounded by construction.** It judged "same BDA regime" by `bda_scan`
  (`Counter::BdaRegionsScanned`, incremented per region visit in
  `BufferCache::SynchronizeBuffersInRange`, `bufferCache.cpp:2825`), but the knob adds 611.8
  `PrepareBda` calls a flip and each walks every mapped range: region visits went
  **21 456 → 199 063, ×9.28**. No run of this knob could pass it — it tested nothing.
  **C3′** judges the regime by `buf_new` (`Counter::BufCreates`, `streamBuffer.cpp:87`; the hook
  creates no buffer) **by LEVEL, not ratio** — the two regimes are ~0.01 against ~1.3–2, two
  orders apart, separator 0.1 — plus the new clause that the *unarmed* arm must hold one regime
  across every window. A ratio rule on `buf_new` would have rebuilt the same defect: at these
  counts the per-window ratio reaches 16× and is pure noise.
* **C5 compared unlike quantities**: `be_ns ≤ endpoint + 2·SE` (4 853.4 against 2 986.8), but
  `be_ns` is WALL time including the mutex wait *by design* while the endpoint is the thread's
  CPU time. It failed hardest exactly when the knob did most of its job. **C5′** keeps C5's first
  clause, **corrects the direction** (`be_ns ≥ endpoint − 2·SE`: wall is at least CPU) and adds an
  impossibility bound (`be_ns ≤ dt_us`).
  The repair is strictly stronger, and that is demonstrated, not asserted: a new fixture
  `bd96fake_lowtimer`, whose timer books 200 µs against a ~1 980 µs effect, **passes the sealed
  C5 and fails C5′** — the sealed control had no lower bound at all. The same rescoring found that
  the *good* `bd96` fixtures had wall time below CPU time, which is impossible for one piece of
  work; the sealed C5 had passed that too.

## 6. Defects of this session's own work, all found before or by the harness

1. **Gate table swap.** `KYTY_PATH_LAP` landed in `DEFINITIONS` before session 95's
   `KYTY_FRAME_REP` while the enum had `PathLap` after `FrameRep` — two gates silently swapped.
   Caught by an order check, not by the build. `C:/kyty/s96/check_gate_order.py` written so it
   cannot recur; it is now part of the build procedure.
2. **`BdaEveryHook` called `PrepareBda()` without the render mutex** from the PM4 parse path, while
   it mutates the buffer cache (`renderContext.cpp:302-304`, `:343`, `:356-358`). Fixed;
   re-entrancy checked rather than assumed.
3. **`pl_sub` double-counted** (`BufferFlushLazy` calls `BufferFlush`, both spans on one counter,
   ~0.6 ms of 4.05 ms) — found by independent review, fixed with a depth guard.
4. **`pl_gc` covered 1 of 5 `RunGarbageCollector()` sites** — found by the same review, fixed.
5. **`pl_look` summed although it is taken on another thread** — found by the same review, fixed in
   `pred/01` before any run existed.
6. **Sealed identity I1 was unsatisfiable.** `pred/01` §5 C1 admits a block-boundary leak; §8 I1
   demanded an exact zero of the same counters. Repaired under `pred/04_pathlap_identity.md`, and
   the repair corrected the repair: the leak is **FIRST 64 / LAST 62 / MID 0**, not "last frame"
   only — a span that opens under one arm and closes under the next (`pl_proc_ns` brackets a whole
   `GuestGpu::Process`). The new I1″ is strictly stronger than C1, proved with a fixture that
   passes C1 and fails only I1″.
7. **Sealed controls C3 and C5 of `pred/03`** — §5 above.
8. **`KYTY_REC` was exported instead of passed positionally**, so `bf96a` recorded no video.
   `enter_scene.py` drops exported environment variables — the trap written into this session's own
   README, then stepped in.

The sealed I1, C3 and C5 FAIL lines stay in the scorers' output for ever.

## 7. Not closed

* **`F_st`, and therefore M3, and therefore G and R1.** No admitted run produced a floor.
* The stub's reversibility (§4) — the blocker for M3.
* The DRS clock: `ROADMAP.md:1062-1065` now has a measurement behind it and must be solved before
  any faster path can be measured at all.
* `bd96b` (the submission granularity, `bdaevery=1`) was not run.
* The video pass for `bindfloor` — not taken; `bf96a`'s recorder was off by the mistake in §6.8.
* Carried from session 95: M4, M5; the BDA regime; the written `bc_ok` slots; `C_bda` in NEW; the
  GPU side of `bdaall`; the single-chunk notify; the `ObtainBuffer` ring timer;
  `pfhint`/`pfcap`/`dapin` with the pin; route B.
* New, from §2.4: **`PrefetchComputePipelines` at 245 µs a call, 6.2 % of the frame** — never
  measured before, never attacked.
