# Session 113: adversarial code audit (final)

Scope: `37e0de1`, `6eb7d14`, `56a4b4f`, `967d1aa`, `623009f`. The net `src/` diff is `7e892d5..HEAD`: 12 files, +263/-6. No
`src/` commit comes after `623009f`. Everything was read only: no build, no run, no git write. The one tool run was
`C:/kyty/s96/check_gate_order.py`, which read the files and printed `GATE ORDER: clean`. Entry 30 `BdaNarrowStamps` matches
row `KYTY_BDA_NARROW_STAMPS`. Line numbers refer to HEAD.

## Summary

| Claim | Verdict | Severity of what remains |
|---|---|---|
| C1 default = session 112 except counters and logs | NOT REFUTED | INFO |
| C2 knob 1 correct by construction | NOT REFUTED | MINOR (conditions, listed below) |
| C3 exact knob-2 check; no crossing piece | NOT REFUTED | INFO |
| C4 GC shift arithmetic | NOT REFUTED | INFO (2 nits) |
| C5 instrument behaviour-free and safe | NOT REFUTED | INFO (3 semantic caveats) |
| C6 new correctness bug | none found | none |

**No MAJOR finding.** One correction to an earlier audit: the pre-run audit's S2 "correction 1" says knob 1 is strictly worse
when an unregistration shrinks a window. That does not hold for any unregistration path in the tree (see C2, item 5).

---

## C1. Default (`bdanarrow=0`, shift 0) = the session-112 build: NOT REFUTED

Every path that differs from session 112 when the defaults are in force:

1. **`PrepareBda`** (`renderContext.cpp:346-359`). The old condition (`registration || mapping` → one `InvalidateBdaRegionStamps`)
   became: mapping → invalidate; else registration → invalidate unless `narrow == 1`. For 0 and 2 that is still one
   generation bump on exactly the same conditions. `NoteBdaMapInvalidation` and `SetBdaNarrowCheck(false)` only write members
   that knob 2 reads. The knob is read after the `bda_cached` return (`:334-338`), so cached calls are unchanged. Values
   above 2 are clamped to the limit (`gates.cpp:428`, `:576`).
2. **`MarkBdaRegions` on every registration** (`bufferCache.cpp:152`, `:2793-2806`) sets `generation = 0` on the new
   buffer's regions. At knob 0 this is redundant:
   - Every registration moves `m_registration_epoch` (`:112`). That defeats `bda_cached` (`renderContext.cpp:325`), so the
     next scanning `PrepareBda` bumps the generation before it visits any region.
   - 0 and the old generation are both non-current. The skip tests are `generation == current` (`:2869`, `:2894`), so
     they decide the same way.
   - `use_bits` is false for that pass in both builds (`:2854-2857`).
   - A mark placed after the bump but before a visit in the same pass would need a registration during
     `SynchronizeBuffersInRange`. Nothing on that path creates a buffer: `SynchronizeBuffer` → `UploadCopies` →
     `StreamBuffer::Map` → `CommandScheduler::Wait` (`commandScheduler.cpp:443-458`) submits but never runs
     `PopPendingOperations`, which is the only way the fault-manager `FindBuffer` (`faultManager.cpp:182-221`) could run.
     `PrepareBda` holds the render mutex, so the scan and the other registrars are serialized with it (pre-audit S4
     confirmed that the callers all run on GuestGpu).
3. **`SynchronizeBuffersByRegion`**: `m_bda_scan_thread =` (`:2848`) and `const auto prev = seen` (`:2900`) are dead stores
   at knob 0. The `else` branch (`:2932-2934`) is the original `CollectCpuModifiedRanges` call.
4. **Counters and logs**: `bgc_evict` (`:2003`, `:2036`), `bda_*` Adds, the one-line `BufferGc:` log (`:419`), and the new
   enum entries appended before `Counter::Count`. `named[]` in `videoOut.cpp:1465` is an unsized array.
5. **The instrument (`623009f`)** changes timing only: a `try_lock` in GuestGpu's idle and blocked paths, and the
   `site` field filled for priority operations. That field already existed in `PendingOperation`
   (`commandScheduler.h`, `PendingOperation::site`), and nothing reads it for behaviour.
6. **Shift 0** gives `shifted == expected` (`bufferCache.cpp:416-417`), so the trigger is unchanged.

## C2. Mode 1 correct by construction: NOT REFUTED

**Invariant that mode 1 needs.** After region R is walked at stamp s with window W, one of two things holds: every
registered-buffer page in W∩R is CPU-clean, or R's stamp has moved. Every event that could make R hold unsynced
registered data must then either move R's stamp or mark R.

- **Dirty bits and stamps.** Every setter of a CPU-dirty bit moves `RegionManager::m_epoch` under the region lock:
  - `ChangeState<Cpu,true>` (`regionManager.h:209-212`), called from `InvalidateRegion`, `InvalidateWriteFault`,
    `MarkRegionAsCpuModified` and `UntrackMemory`;
  - a provisional armdefer upload (`:372`);
  - region creation, where the stamp goes from `{}` to `{ptr,e}` (`memoryTracker.cpp:67-73`).
- **Consumers.** The only code that clears CPU-dirty bits is `ForEachUploadRange` (`memoryTracker.h:289-364`). Its only
  callers are `SynchronizeBuffer` (`bufferCache.cpp:826`) and `CollectBufferUpload` (`:2661`). Both upload into the
  registered buffer they were given.
- **Skips that leave bits set.** `HasCurrentUpload` holds only if nothing was announced since an upload that consumed the
  bits of that interval. `SyncFreeSkip` holds only if the bits are clear. So neither leaves registered dirty data with
  an unmoved stamp.

Sequences tested against mode 1:

1. **New buffer over pages left dirty (the stated case).** `MarkBdaRegions(CpuAddress, Size)` runs after
   `m_buffers.emplace` (`:125`, `:152`) and covers the whole created range, including the `ResolveOverlaps` expansion and
   the stream leap, because it uses `buffer.CpuAddress()`/`Size()`. The index is `vaddr / TRACKER_REGION_SIZE`, the same
   as the scan index (`:2859`). `last` is clamped to `size()-1`; `first` beyond it makes the loop empty, and such regions
   are not scannable anyway.
2. **Buffers spanning several regions.** The loop runs `first..last` (`:2802`). Holds.
3. **Window growth** (`SynchronizeBuffersInRange` `:2972-2993`). The window only grows when a buffer is registered in the
   mapping.
   - Regions strictly between the old edge and the new buffer contain no registered buffer.
   - A boundary region that the new buffer touches is marked.
   - Holds.
4. **Registration during a pass** (stale window). Not reachable, as shown in C1 item 2.
5. **Unregistration and re-creation.** Every non-join unregistration first runs `UntrackMemory` over the buffer's full
   range:
   - GC at `:2002` and `:2035`;
   - `DeleteBuffersOverlapping` at `:2532` and `:2542`.

   That calls `ChangeState<Cpu,true>` on every existing region of the buffer, which moves their stamps. `JoinOverlap`'s
   unregistration (`:639-648`) always comes with the registration of a superset buffer (`:650-679`), which is marked.
   Re-creating a buffer is a registration, so its regions are marked. Holds.
   - **Correction to AUDIT113PRE S2 "correction 1".** That note said that when the only M1 buffer reaching a shared
     region R is unregistered, knob 1 leaves R skipped. In fact the eviction's `UntrackMemory` moves R's stamp. M1's window
     no longer reaches R, so the M2 visit sees a moved stamp and walks R. The shared-region hole is **the same in all knob
     values**, and the new code does not make it worse. After a mark, the M1 visit consumes it, exactly as it consumes a
     global bump.
6. **Guest map changes.** `m_mapping_epoch` makes all three knob values bump globally (`renderContext.cpp:348-351`).
   `MapMemory` and `UnmapMemory` change it under the exclusive lock, and `PrepareBda` holds the shared lock throughout
   (`:316`).
7. **Knob switches** (schedule arms). Marks are unconditional, so 0→1 is sound at any `PrepareBda`, and 0 and 2 are
   supersets of 1.
8. **bdabits interplay.** A marked region fails the `generation == current` half of the bit skip (`:2869`) and falls to
   the stamp path. In mode 1, `use_bits` simply stays true more often. Holds.
9. **Registrations on other threads (`bda_nxthr`).** Every registrar found runs on GuestGpu under the render mutex, or on
   the main thread after `m_gpu.reset()` (`ShutdownGpu` → `Finish` → `PopPendingOperations`). None of them run at the same
   time as a scan.

**Remaining conditions (MINOR, not refutations):**

- **(a) Serialization.** Mode 1 depends on registration being serialized with the scan. A registrar that ran at the same
  time could lose a mark: `seen = {...}` (`:2901`) can overwrite `generation = 0`. That would be a data race in knob 0
  too, but knob 0 would recover at the next bump. `bda_nxthr` records the thread, not concurrency.
  - A pre-existing teardown window exists. While `GuestGpu::Shutdown` joins a thread that is still draining work,
    `UnmapMemory` runs `unmap()` inline on the guest thread (`renderContext.cpp:293-296`). Its `Finish` →
    `PopPendingOperations` can reach the fault-manager `FindBuffer`. This is the same in all modes.
- **(b) Loss of the safety net.** In the OLD regime, knob 0's frequent global re-walks hid any violation of the invariant
  above. Knob 1 removes that. No violating path was found, and the forced-OLD knob-2 runs report 0 `bda_nmiss` in
  11.8 M would-skip regions. That evidence was collected on knob-2 histories, whose witnesses are at most one frame old.
  Knob-1 histories keep witnesses much longer, and that difference was not exercised.

## C3. Exact knob-2 check: NOT REFUTED

- **No crossing piece.** The only caller is `bufferCache.cpp:2910`, found by repository-wide grep. It passes
  `(cursor, bytes)` with `bytes = min(scan_end-cursor, RS - cursor%RS)` (`:2860-2861`). Because `cursor < scan_end`,
  `bytes >= 1`, and `cursor%RS + bytes - 1 <= RS-1`. So `(cursor+bytes-1)/RS == cursor/RS`, and the `EXIT_IF`
  (`memoryTracker.cpp:199`) cannot fire. `ValidateRange` is the same call the old path made.
- **Exactness of the predicate.** The dirty bits and `manager->Epoch()` are read under one `manager->lock`
  (`memoryTracker.cpp:216-218`). Every epoch move after a bit is set happens under that same lock (see C2). So
  `prev.stamp == locked` proves nothing was announced since the previous walk's unlocked stamp read (`:2892`, stored at
  `:2901`).
  - Bits present at that read were visible to that walk's locked collect.
  - A null manager returns `{}` with the whole piece counted as dirty. That equals the unlocked `{}`, and it is a real miss
    if knob 1 skipped it.
  - `prev.generation != 0 && >= m_bda_map_generation` reproduces knob 1's `generation == current`. Marks write 0, and
    `m_bda_map_generation` is the generation right after the last map bump (`bufferCache.h:147`).
- **Scope of "exact" (INFO).**
  - `bda_nmiss` counts dirty ranges that overlap a registered buffer. That is an upper bound on missed uploads, because
    `HasCurrentUpload` could make the overlap harmless.
  - It is evaluated on the knob-2 history. Because stamps only increase, knob 1's skip set is a subset of the would-skip
    set. The check is therefore conservative, which is the safe direction.
  - Knob 2's synchronization behaviour equals knob 0's: one region, same collect, plus read-only
    `DirtyRangesTouchBuffers`.

## C4. GC shift: NOT REFUTED

- `shift_mb` is clamped to `2^30` and multiplied by `GiB/1024`, which is 1 MiB in bytes. The largest shift is 2^50 bytes.
  `expected` is at least about −1 GiB, so there is no int64 overflow.
- The result is floored with `max(shifted, 1 GiB)` (`bufferCache.cpp:412-417`).
- The critical threshold is untouched (`:418`) and stays above `expected`.
- At 0, `shifted == expected`.

Nits (INFO, measurement only):
- `strtoull("-N")` wraps to the maximum, so the trigger becomes 1 GiB.
- If `CanReportMemoryUsage()` is false, the early return at `:399-401` ignores the variable and prints no `BufferGc:` line.

## C5. Priority-stall instrument: NOT REFUTED

- **Lock order.** GuestGpu holds `m_queue_mutex` (`graphicsRun.cpp:693`) and then `try_lock`s `m_operation_mutex`
  (`commandScheduler.cpp:606`). A try-lock never blocks, so this new lock order cannot deadlock.
  - No code holding `m_operation_mutex` blocks on `m_queue_mutex`. Every critical section on it only pushes, pops, reads
    state, or waits on a condition variable, which releases the mutex.
  - Nothing is logged or counted under `m_operation_mutex`. `Add` and at most 32 `LOGF` calls run under
    `m_queue_mutex`, which is bounded and already the pattern there.
  - The GuestGpu thread never owns `m_operation_mutex` at `ThreadRun` top level, so there is no recursive `try_lock` on a
    `std::mutex`.
- **Site lifetime.** It is a code return address, stored and read only under the lock (`:589`, `:639`, `:667`).
  `DeferredSiteName` interns names in a static map protected by its own leaf mutex and never erases them, so `c_str()`
  stays valid.
- **Reset.** `m_priority_active_site` is set and cleared together with `m_priority_active` under the lock (`:637-639`,
  `:665-667`).
- **Other threads.** `Add` from the priority thread attaches a shard lazily (`frameStats.cpp:178-188`).
- **Lifetime.** The scheduler outlives the GuestGpu thread. `m_gpu` is joined and reset first (`renderContext.cpp:100-123`).
- **Tick semantics.** `CurrentTick()` is an atomic load of the next tick to hand out, and `NextTick()` returns the old value
  (`masterSemaphore.h:19-27`). A tick captured at deferral is therefore at most `CurrentTick()`, and `>=` means `==`: Submit
  has not reserved it. That is the correct test.

Caveats (INFO):
- With `recordthread` and `asyncsubmit`, "submitted" means that Submit reserved the tick. That buffer may still sit in the
  record or submit FIFO, so such stalls log `unsub=0`.
- A failed `try_lock` undercounts `gw_idle_prio`.
- The idle probe runs once per loop entry or wake. A priority operation queued after GuestGpu went idle is visible only
  through `prio_unsub` and `prio_stall`.

## C6. New correctness bugs: none found

- **Initialization.** All new members are initialized (`bufferCache.h:293-295`, `commandScheduler.h:152`).
- **Overflow.** The generation is uint64, and 0 is never current because the generation starts at 1. `MarkBdaRegions`
  arithmetic is sound for valid guest ranges.
- **Tables.** Knob and gate tables are in order. The counter enum is appended.
- **Threads.** `m_bda_*` members are touched only on the scanning or registering thread under the render mutex. The only
  cross-thread reads are `m_bda_scan_thread` and `m_bda_region_stamps` in `MarkBdaRegions`. They would race only in the
  concurrent-registrar case of C2(a), which would already be a race on `m_buffers` in the session-112 code.
