# BDA regime OLD / NEW: the mechanism (read-only investigation, 2026-09-24)

Source tree: `C:/kyty/KytyPS5/src`. Logs: `C:/kyty/s82 … s112/log_*.txt` (190 logs, all the same
binary family and the same machine). Nothing was built or run, and no source file was changed. The
scripts and their outputs are in this directory (§6).

## 0. The answer in one paragraph

`bda_scan` ≈ 1 066 is **one full walk of the whole BDA span (~1 032 tracking regions) per frame**,
added to the ~50 regions that normally move. The walk happens because `PrepareBda` invalidates
**every** region stamp whenever `BufferCache::m_registration_epoch` has moved
(`renderContext.cpp:343-345`), and in OLD runs that epoch moves ~1.2 times a frame because the
**buffer-cache garbage collector is armed**. It evicts buffers that have been idle for 160 GC ticks
(~20 frames), which calls `Unregister`, and those buffers are re-created later, which calls
`Register` (`buf_new` 1.1–2.4 a frame). The GC is armed only when device-local memory usage (the
VMA **block** bytes plus driver memory) is at or above `m_trigger_gc_memory`. That threshold is
computed once, in the `BufferCache` constructor, from the heap budget: 9 747 352 781 B
(9 295.8 MiB) on this machine (`bufferCache.cpp:395-406`, `:1945-1950`). Across 190 archived logs
the regime matches the sign of *usage − trigger* at every steady MemStats sample, with two kinds of
exception. Runs within 75 MiB of the trigger are mixed. Bindfloor A/B runs are half OLD, because
the floor arm suspends the buffer GC (`bf_bgc_hold`). Usage differs between runs by **whole
256 MiB VMA blocks**: NEW runs hold 8 531–8 857 MiB of blocks, OLD runs 9 218+ MiB, and the
allocated bytes are the same (~6.7 GiB). The regime is therefore sticky for the whole run. The
buffer GC frees sub-allocations inside blocks that stay pinned, so it can never bring usage back
under the trigger, and below the trigger nothing is ever evicted. What remains to measure is why a
launch leaves 2 extra 256 MiB blocks after level load (§4, H2).

## 1. PrepareBda and what a "scan" is (Q1)

* `RenderContext::PrepareBda`, `graphics/host_gpu/renderer/renderContext.cpp:300-379`.
  * `:321-326` is the three-epoch cache. If the global CPU write epoch
    (`MemoryTracker::m_cpu_epoch`, moved by any CPU write announcement anywhere), the
    registration epoch (`BufferCache::m_registration_epoch`) and `m_mapping_epoch` are all
    unchanged, the call returns at once (`bda_hit`, counted at `:337`). This serves ~155–158 of the
    ~178–181 calls a frame in **both** regimes.
  * `:343-345`: **if the registration epoch or the mapping epoch moved, it calls
    `m_buffer_cache.InvalidateBdaRegionStamps()`** (`bufferCache.h:143`, `m_bda_stamp_generation++`).
    This is a global invalidation. Every region's saved stamp becomes stale, including regions the
    (un)registered buffer never touched.
  * `:357-359` runs `m_mapped_ranges.ForEach(... SynchronizeBuffersInRange ...)`.
* `BufferCache::SynchronizeBuffersInRange`, `bufferCache.cpp:2860-2933`. It counts `bda_rng`
  (`:2869`) and bounds each guest mapping to [first registered buffer that intersects it, end of the
  last one] (`:2877-2905`). A mapping with no buffer returns at once and counts `bda_rng_e`
  (`:2894`). With gate `bdastamp` on (default 1) it calls `SynchronizeBuffersByRegion`
  (`:2915-2917`).
* `BufferCache::SynchronizeBuffersByRegion`, `bufferCache.cpp:2779-2857`. It walks the bounded span
  in 4 MiB steps (`TRACKER_REGION_SIZE`, `regionDefinitions.h:13`). For each region:
  * stamp = `MemoryTracker::RegionWriteStamp(index)` = {RegionManager*, `RegionManager::Epoch()`},
    or {nullptr, 0} for a region that does not exist yet (`memoryTracker.h:72-78`);
  * if the saved `{stamp, generation}` equals {current stamp, current generation}, the region is
    skipped and counts `bda_skip` (`:2837-2840`);
  * otherwise it saves the new stamp (`:2842`) and **counts `bda_scan` (`:2843`,
    `Counter::BdaRegionsScanned`, printed as `bda_scan=` in `FrameTrace-draw`, `videoOut.cpp:1305`)**.
    It then:
    * runs `MemoryTracker::CollectCpuModifiedRanges(cursor, bytes)` (`:2846`;
      `memoryTracker.cpp:163-191`). This takes the region spin lock and walks the CPU-dirty bitmap.
      **A missing region is appended whole as one dirty range** (`:184`), and a new RegionManager
      starts all-dirty (`regionManager.h:129`);
    * runs `SynchronizeBuffersOfDirtyRanges()` (`:2848`, `bufferCache.cpp:2741-2777`). This does
      one `m_buffers.upper_bound` per dirty range (`bda_drng`, `:2747`) and a `SynchronizeBuffer`
      for each registered buffer the range intersects (`pb2_sync`, `:2767`). It counts
      `pb2_pass` once per non-empty dirty list (`:2773`).
* So `bda_scan` counts **region visits (4 MiB, clipped to the span) whose stamp or stamp
  generation changed since that region's last visit**. The same region can count more than once
  in a frame: once per scanning call after it moved.

## 2. What moves a region's stamp, and what moves the generation (Q2)

| What moves | Where | Callers (reachable in the steady scene) |
|---|---|---|
| `RegionManager::m_epoch` (+ global `m_cpu_epoch`) | `ChangeState<Cpu, true>`, `regionManager.h:209-212`. **Unconditional**, even for pages that are already CPU-dirty | (a) `MemoryTracker::InvalidateRegion` (`memoryTracker.h:124-148`) ← `BufferCache::InvalidateMemory` (`bufferCache.cpp:423-430`) ← `HandleFault` 1-page write window (`renderContext.cpp:162`), `RenderContext::InvalidateMemory` (`:212-220`, from `kernel/memory.cpp:1232-1236` ← file reads `kernel/fileSystem.cpp:167/788/798/940/948`), `ReleaseGuestStack` (`:235`), `UnmapMemory` (`:285`); (b) `InvalidateWriteFault` (`memoryTracker.h:164-196`) ← `HandleFault` with knob `faultkb` 64 KiB (`renderContext.cpp:171`); (c) `MarkRegionAsCpuModified` (`memoryTracker.cpp:193-199`) ← `ReadMemoryOnGpu(is_write)` (`bufferCache.cpp:553-555`); (d) **`UntrackMemory`** (`memoryTracker.cpp:225-247`) ← **buffer GC** (`bufferCache.cpp:1987`, `:2019`) and `DeleteBuffersOverlapping` (`:2515`, `:2525`) |
| `RegionManager::m_epoch` only | `ForEachUploadRangeArmDeferred`, provisional upload, `regionManager.h:372` | gate `armdefer` only (default 0) |
| stamp {nullptr,0} → {ptr,1} | `MemoryTracker::GetOrCreateRegion`, `memoryTracker.cpp:59-75` | lazily, from any `Iterate<true>` (uploads, `IsRegionCpuModified`, `MarkRegion*`) |
| **stamp generation (all regions at once)** | `InvalidateBdaRegionStamps`, `bufferCache.h:143`, called from `PrepareBda` `renderContext.cpp:343-345` | **registration epoch** `++m_registration_epoch` in `ChangeRegister` (`bufferCache.cpp:112`) ← `Register` (`CreateBuffer` `:663`) / `Unregister` (`DeleteBuffer` `:195-205` ← `JoinOverlap` `:632`, **GC clean eviction `:1988`**, `DeleteBuffersOverlapping` `:2516/:2526`; **GC dirty eviction `:2020`**); **mapping epoch** (`MapMemory` `renderContext.cpp:269`, `UnmapMemory` `:289`) |

Several things do **not** move a stamp: GPU writes (`ChangeState<Gpu,…>`), downloads, uploads (they
clear bits and re-protect, `ForEachModifiedRange<Cpu,true>`), protection changes, LRU touches and
texture-cache work.

**Could ~1 000 regions move every frame in a steady scene?** The per-region paths cannot. There are
~1 270 CPU write faults a frame, the same in both regimes, and they land in a handful of regions.
They produce the ~50 base scans that both regimes show. Only the generation bump rescans the
whole span, and it rescans all of it: ~1 032 regions per bump.

## 3. What the archived logs show (Q3)

Scripts: `scan_logs.py`, `joint.py`, `memstats.py`, `sweep.py`, `loadphase.py` (§6). The steady
window is frames ≥ 2100 (≥ 300 or ≥ 1200 where noted).

### 3.1 OLD is exactly one full-span walk per churn event

Visits per scanning call, `(bda_scan + bda_skip) / (bda_n − bda_hit)`, are **1 032–1 039 in both
regimes** (bl93a NEW 1 039, mc94a OLD 1 032). The span is the same, and so is its ~4.1 GiB of guest
address space. The OLD excess, 1 068 − 52 = 1 016, equals **one span**. The frame-by-frame
k = round((bda_scan − 52)/span) against `buf_new` (the `joint.py` output):

| log (regime) | k=0 & buf_new=0 | k≥1 & buf_new≥1 | k≥1 & buf_new=0 | k=0 & buf_new≥1 |
|---|---|---|---|---|
| mc94a (OLD, 6 931 frames) | 257 | 5 682 (k=1: 4 404, k=2: 1 217, k=3: 61) | 986 | 6 |
| bl93a (NEW, 9 082 frames ≥300) | 8 743 | 287 | 20 | 32 |
| wak92a (NEW, 9 256 frames ≥300) | 8 942 | 251 | 27 | 36 |

In OLD runs 986 frames rescan with no creation. Those are Unregister-only frames (a GC eviction
whose re-creation lands in a later frame). `bda_drng` is ~1 175–1 220 in OLD-level frames against
72–83 in NEW-level ones, and `pb2_pass` ~825–1 001 against ~51. `pb2_sync` is **the same**
(67 against 66–75): the rescanned regions are CPU-dirty but hold no registered buffer, so the
~2 ms of OLD work is locks, bitmap walks and `m_buffers` lookups that find nothing.

### 3.2 Everything else is equal between the regimes (steady, frames ≥ 2100)

`faults` 1 264–1 279, `fw_n`, `tex_inval`, `pb_inval_flush`, `pb_refault`, `prot_calls`,
`prot_pages`, `sync_ups`, `dmas` 16, `dispatches` 268, `downloads` 1, `img_new`/`img_free`
6.3–7.7 (no regime pattern: OLD stg92a 6.63, NEW bl93a 6.76) and `unmap` (only frames
~457–485, once, in both regimes). There are **no** `Accessed non-GPU cached memory` lines after
frame 300 in either regime, so no buffer is re-created through the BDA fault buffer
(`faultManager.cpp:208-221`).

### 3.3 Device-local usage against the buffer-GC trigger

The trigger follows `bufferCache.cpp:397-406` with `GetTotalMemoryBudget` (discrete branch,
`vma.cpp:263-290`): heap-0 budget 15 975 055 360 → total = budget − 1 GiB = 14 901 313 536 →
threshold = min(total, 8 GiB) → **trigger = min(total − 0.6·8 GiB, total − 1 GiB) =
9 747 352 781 B = 9 295.8 MiB**. `m_total_used_memory = GetDeviceMemoryUsage()`
(`bufferCache.cpp:1945-1946`; `vma.cpp:243-259`) is the VMA-reported **device-local heap usage**,
which includes empty space in VMA blocks. Heap 1 (host import, ~15.7 GB) is not counted and is
equal in both regimes.

| log | regime | usage − trigger (steady MemStats) | blocks MiB | allocation MiB |
|---|---|---|---|---|
| bl93a | NEW | −282…−386 MiB | 8 790–8 817 | ~6 740 |
| wak92a | NEW | −288…−388 | 8 796 | ~6 750 |
| mc94a | OLD | +223…+319 | 9 308 | ~6 800 |
| bda94a | OLD | +180…+303 | 9 279 | ~6 730 |
| wak92a_warmup | OLD | +224…+320 | 9 309 | ~6 830 |
| stg92a | OLD | +200…+322 | 9 284 | ~6 790 |

The regime is already decided at the **first MemStats after level load (frame 299)**: OLD runs are
+132…+175 MiB above the trigger, NEW runs −454…−455 MiB below. `sweep.py` over **190 logs of
s82–s112** (every log uses the same budget), per MemStats sample at frame ≥ 1200:

* above the trigger and OLD-level: 2 570 samples; below and NEW: 1 378;
* above and NEW-level: 415. **All** of these are in bindfloor ABBA runs (`rv97*`, `bf98*`, `rv98*`,
  `bf99*`, `eng99*`, `life99a`, `cal99a`), plus 1 in the edge log `mut104` and 1 in
  `bl93a_warmup`;
* below and OLD: 1 (`bl93a_warmup`, a scene still loading).

**The bindfloor runs are a within-run A/B.** In `bf98a`, `eng99a2` and `rv97b`, the arm with
`bindfloor=0` is OLD in 95–97 % of frames, and the arm with `bindfloor=1` is OLD in 0–1.6 % of
frames with `bf_bgc_hold` ≈ 7.9–8.0 a frame. `bf_bgc_hold` counts buffer-GC calls that were
**above the trigger** and suspended (`bufferCache.cpp:1948-1956`). So ~8 GC calls a frame want to
collect, and 160 ticks ≈ 20 frames. (The floor also removes the binding path, so this A/B supports
H1 but does not isolate the GC alone.)

### 3.4 Usage comes in 256 MiB steps (VMA blocks)

Clustering the 190 logs by median block bytes (`blocks − 8 790` in 256 MiB steps):

| step | logs | blocks MiB | usage − trigger | mean OLD fraction |
|---|---|---|---|---|
| −9/−8 (other entry) | 2 | 6 393–6 647 | −2 700…−2 442 | 0.01 |
| −1 | 9 | 8 531–8 571 | −567…−442 | 0.03 |
| 0 | 43 | 8 682–8 857 | −406…−225 | 0.01 |
| **+1 (edge)** | 5 | 9 024–9 062 | **−75…+9** | 0.26 (0.01–0.59) |
| +2 | 98 | 9 218–9 404 | +133…+319 | 0.92 (0.50 = bindfloor runs) |
| +3 | 28 | 9 441–9 653 | +356…+573 | 0.81 |
| +4/+5 | 5 | 9 692–10 161 | +646…+1 085 | 0.48–0.97 |

Non-VMA device memory (usage − blocks) is 192–307 MiB everywhere. Allocation bytes are
~6.6–6.9 GiB everywhere. **So the whole difference is the number of VMA blocks held, in 256 MiB
quanta.** VMA's default large-heap block size is 256 MiB; nothing in `vma.cpp:48-59` overrides it.
131 of 190 logs are OLD (69 %), 54 NEW and 5 at the edge. That fits "OLD is the common state".

### 3.5 The candidates listed in the brief

| Candidate | Verdict | Why |
|---|---|---|
| VMA block count after level load (fragmentation, retained empty blocks, allocation/free ordering) | **the sticky input** (H2) | §3.4 |
| Heap budget at start (trigger computed once) | mechanism real, **not what varied here** | budget identical in all 190 logs; trigger moves 1:1 with budget above 8 GiB, so another VRAM consumer at launch would move it (H3) |
| LRU thrash of buffers | **yes, but gated by usage ≥ trigger, not by buffer size** | GC `:1960-1991`: age 160 ticks, ≤32 per call, only above the trigger |
| BufferJoin / region granularity / span | no | span 1 032–1 039 visits per call in both regimes |
| Mapping epoch (Map/Unmap) | no | unmap only at frames ~457–485, in both regimes |
| CPU write faults / region-epoch flood | no | equal counts in both regimes; they are the ~50 base scans |
| BDA fault-buffer re-creation | no | zero `Accessed non-GPU cached memory` lines in the steady scene |
| Host import pieces | no | heap 1, not counted by `GetDeviceMemoryUsage` on a discrete GPU |
| Dedicated vs sub-allocated (`KYTY_BUFFER_DEDICATED_KB`) | not the variable (same env), possibly a lever | dedicated allocations add equally to blocks and allocation, so the gap sits in shared blocks |
| Stream/ring buffers, `Primary()`, async protect worker | no evidence | none of them moves the registration epoch or the block count |
| Texture GC (`m_pressure_gc_memory` = the same 9 747 352 781) | co-switches, no visible effect | `textureCache.cpp:252`, `:3362-3365`; `img_*` show no regime pattern |
| Load-phase counters (frames 150–400: `buf_new`, `img_*`, `img_rec_*`, `img_defer*`) | nothing that separates the regimes | `loadphase_out.txt` |

## 4. Hypotheses, ranked (Q4)

### H1 (supported by the archived logs; highest confidence). The buffer-GC churn arms full-span BDA rescans

* **Path.** `GuestGpu::Process` completion and flip preparation call `RunGarbageCollector`
  (`graphicsRun.cpp:985/1006/1031/1041/1049`), then `BufferCache::RunGarbageCollector`
  (`bufferCache.cpp:1935`). There `m_gc_tick++` (`:1944`), `usage = GetDeviceMemoryUsage()`
  (`:1946`), and if `usage < trigger` it returns (`:1948`). Otherwise
  `m_lru_cache.ForEachItemBelow(tick − 160)` (`:1960-1966`) evicts ≤32 idle clean buffers:
  `UntrackMemory` + `DeleteBuffer` (`:1987-1988`) → `Unregister` → `++m_registration_epoch`
  (`:112`). The buffer is re-requested later → `FindBuffer` → `CreateBuffer` → `Register`
  (`:663`) → `++m_registration_epoch`. The next non-cached `PrepareBda` sees the registration
  epoch move → `InvalidateBdaRegionStamps` (`renderContext.cpp:343-345`) → every region of the
  ~1 032-region span is "scanned" (`bufferCache.cpp:2843`), with `CollectCpuModifiedRanges` and
  `SynchronizeBuffersOfDirtyRanges` over ~1 100 dirty ranges that intersect nothing.
* **Why it is sticky.** The trigger is a constant set in the constructor (`:395-406`).
  Usage is dominated by VMA block bytes, and evicting a sub-allocated buffer does not free a block
  that other allocations still share. So above the trigger the GC runs forever at ~1.5 evictions
  a frame (idle buffers are always found and re-requested), and below it nothing is ever evicted.
  Only a whole-block change can cross the line: a scene cut, or a run within one block of the
  trigger (edge logs `abb105`, `dab102a`, `mut104`, `vwk104`, `vdb106`).
* **Existing counters that differ OLD / NEW** (confirmed): `bda_scan` (≈1 068 / ≈51), `buf_new`
  (1.1–2.4 / 0.01), `bda_drng` (≈1 200 / ≈75), `pb2_pass` (≈825–1 000 / ≈51). The derived
  k = (`bda_scan` − 52)/span is ≈1.2 / ≈0.03, from `bda_scan`, `bda_skip`, `bda_n` and `bda_hit`.
  The `MemStats: heap=0 … usage=` line against the trigger computed from its `budget=` separates
  them (§3.3). `bf_bgc_hold` > 0 in any bindfloor run proves usage ≥ trigger. **Equal in both**
  (the controls): `faults`, `fw_n`, `pb2_sync`, `bda_rng`, `bda_hit`, span, `prot_*`.
* **Minimal new counters that would prove it directly:**
  1. `bgc_live`: `BufferCache::RunGarbageCollector` calls that pass the trigger test, `Add` right
     after `bufferCache.cpp:1948-1950` (before the floor branch). Also one log line at the
     constructor, `BufferGc: budget=%llu trigger=%llu critical=%llu`, at `:405-406`, so the
     threshold is logged instead of recomputed. Prediction: ≈8 a frame OLD, 0 NEW.
  2. `bgc_evict` / `bgc_evict_kb`: evictions at `:1987-1988` (clean) and `:2019-2021` (dirty).
     Prediction: ≈1.2–1.6 a frame OLD (≈ `buf_new`), 0 NEW.
  3. `bda_gen`: the `InvalidateBdaRegionStamps` calls at `renderContext.cpp:343-345`, split
     `bda_gen_reg` / `bda_gen_map` by which epoch moved. Prediction: `bda_scan` ≈ 52 +
     `bda_gen`·span, `bda_gen` ≈ 1.2 OLD, ≈ 0.03 NEW, `bda_gen_map` ≈ 0 in the steady scene.
  4. (identifies the churning buffers) `buf_new_re`: `CreateBuffer` (`:635-663`) calls whose range
     intersects one of the last 64 GC evictions (a ring filled at `:1988`). Add a capped log
     `BufferGcEvict: addr= size= idle_ticks= created_frame=`. Prediction: `buf_new_re` ≈ `buf_new`
     in OLD, which shows the creations are re-creations, not new ranges.

### H2 (the sticky input; likely, not yet measured). Level load leaves 2 extra 256 MiB VMA blocks

* **Path.** Scene load makes ~1 200–1 800 buffers in one frame (`buf_new` peak at frames 181–333),
  thousands of images, joins (the new buffer is allocated before the joined ones are deleted,
  `bufferCache.cpp:656`/`:632`), erasure deferred through `DeferOperation` (`:201-202`) and
  `VulkanDeferredDestroy`, and the `imgrecycle` pool (≤256 MiB kept for ≤2 s). How many 256 MiB
  blocks the peak forces, and how many stay pinned by long-lived allocations or kept as VMA's one
  empty block per memory type, depends on thread timing.
* **Why it is sticky.** VMA never frees a block that holds any allocation. In the settled scene the
  allocation total (~6.7 GiB) does not change, so the block count left by the load holds for the
  whole run. It is already visible at frame 299 (§3.3).
* **Existing counters.** `MemStats: … blocks=` against `allocation=` (a gap of 1.8–2.1 GiB in NEW
  runs, 2.3–2.6 GiB in OLD runs, the same allocation). Load-phase `buf_new`, `img_new`,
  `img_rec_put` and `img_defer_kb` do **not** separate the regimes (`loadphase_out.txt`).
* **Minimal new counters.** Set `VmaAllocatorCreateInfo::pDeviceMemoryCallbacks` at `vma.cpp:48-59`
  (pfnAllocate/pfnFree: memory type, size), giving counters `vma_blk_alloc` / `vma_blk_free` and a
  capped log `VmaBlock: alloc|free type= size= frame=`. Also extend `MemStats:` (`vma.cpp:118`)
  with per-memory-type `blockCount` / `allocationCount` / empty-block count from
  `vmaCalculateStatistics`. Prediction: OLD runs allocate two more ~256 MiB device blocks between
  frames ~180 and ~300 and never free them. If they are VMA's retained empty blocks, the per-type
  empty-block count reads 1+1 in OLD and 0 in NEW.

### H3 (possible on other launches; not the variation observed here). The trigger follows the budget at start

* **Path.** `BufferCache` constructor → `GetTotalMemoryBudget()` (`vma.cpp:263-290`, the VMA heap
  budget at that moment minus 1 GiB) → trigger (`bufferCache.cpp:397-406`). The texture cache takes
  the same number as `m_pressure_gc_memory` (`textureCache.cpp:247-257`). Above 8 GiB of budget the
  trigger moves 1:1 with the budget, so ~300 MiB of VRAM taken by another process at launch
  (browser video, recorder, a lingering previous emulator) would turn a NEW launch into OLD.
* **Why it is sticky.** It is read once.
* **Existing counters.** The `budget=` field of the first `MemStats:` line. It is identical
  (15 975 055 360) in all 190 logs, so H3 did **not** produce the OLD/NEW split seen so far.
* **New counter.** The `BufferGc:` constructor line of H1 item 1.

### H4 (explains the "transient OLD" inside NEW runs). First-time creations while the scene settles

* **Path.** The same `Register` → `InvalidateBdaRegionStamps` chain, but through ranges that are
  requested for the first time, below the trigger.
* **Why it is sticky (it isn't).** The creations die out once every range has a buffer. This is
  bl93a's OLD stretch at frames 214–289 and its 19–38 % OLD-level frames in 300–1 199, with
  `buf_new` 0.19–0.69 a frame and usage 282–455 MiB **below** the trigger. It is also
  `bl93a_warmup`, and "left the level at frame 277".
* **Existing counters.** `buf_new` > 0 together with usage < trigger. New counter: `bgc_evict` = 0
  in those frames, with `buf_new_re` = 0.

## 5. Implications (not implemented)

* The OLD cost is two design choices multiplying. The generation bump is global, although only the
  (un)registered buffer's own regions become relevant, and nothing at all for an `Unregister`
  (`renderContext.cpp:340-345`). And device-wide VMA block usage arms an LRU that evicts live
  buffers. Invalidating only `[buffer.CpuAddress(), +Size())` of a newly registered buffer
  (clearing those regions' `generation`) would remove the ~1 016 extra scans in either regime. A
  buffer-GC trigger based on the cache's own bytes, or one with hysteresis, would remove the churn
  and its re-uploads (`UntrackMemory` marks the evicted pages CPU-dirty).
* Before any such change, an A/B needs no new code. Classify every archived and future run by the
  first steady `MemStats` usage against 9 295.8 MiB (or by the 256 MiB step of `blocks=`), and
  quote each PrepareBda number with its regime.

## 6. Files in this directory

* `scan_logs.py` → `scan_out1.txt`: per-regime means and medians and the transition frames
  (bl93a, mc94a).
* `joint.py`: the k × `buf_new` table (§3.1).
* `memstats.py` → `memstats_out1.txt`, `memstats_out2.txt`: usage against trigger per MemStats
  sample, with the regime of the next 300 frames.
* `sweep.py` + `sweep_list.txt` → `sweep_all.tsv`: 190 logs, s82–s112.
* `loadphase.py` → `loadphase_out.txt`: load-phase counters, OLD against NEW.
