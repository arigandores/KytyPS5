# Session 113 pre-run audit: knob `bdanarrow` (commit 37e0de1) and sealed harness `vbn113`

**How the audit was run.** Four lenses looked at the change: safety, check validity, threads and harness. Two skeptics then tested each finding independently. A finding counts as surviving if at most one of its two skeptics refuted it. Where several lenses reported the same defect, their findings are merged below, and the original lens and ID is kept in brackets. Nothing was built or run, nothing under `C:/kyty/KytyPS5` or `C:/kyty/s113` was changed, and no background processes are left. The lenses and skeptics wrote their scratch helpers only under `C:/kyty/s113/audit113pre/` (for example `old_level.py`, `rowcheck.py`, `f1_maps2.py`, `f1_maps_sk2.py`, `f1_skeptic_hist.py`, `sk2_f1_diff.txt`, `sk2_f3_nonl.py`, `crlf_probe.sh`, `callers.py`, `fgrep.py`, `diff_src.txt`).

I re-read the following myself while writing this report:
- `bufferCache.cpp:2782-2897`
- `renderContext.cpp:312-392`
- `regionManager.h:183-213`
- `memoryTracker.h:28-30`
- `vbn113.py:100-158`
- every caller of `PrepareFrame` and `FlipQueue::Prepare`

---

## 1. Surviving findings (most severe first)

### S1 — MAJOR — Races inflate `bda_nmiss`, so the zero-tolerance BAD rule can close a safe mode 1 [check‑F1 = threads‑F1; none of the 4 skeptics refuted it; all 4 graded it MAJOR]

**Defect.** Knob 2 decides that knob 1 "would skip" a region using a stamp it reads without the region lock. It collects the dirty bits later, under that lock. A guest CPU write announced between those two points gets counted in `bda_nmiss`. Knob 1 would not lose such a write: the region stamp has already moved, so the next `PrepareBda` walks the region. This is the same one-pass delay the design already accepts for any write that lands just after the collect (`bufferCache.cpp:2814-2816`, `renderContext.cpp:388-391`).

**Evidence.**
- The scan runs on GuestGpu:
  - `:2874` reads `stamp = RegionWriteStamp(index)`, an acquire load with no lock (`memoryTracker.h:72-78`, `regionManager.h:141-142`).
  - `:2883-2884` fixes `narrow_would_skip` from that value.
  - `:2885` stores `seen`.
  - `:2889` `CollectCpuModifiedRanges` then takes `manager->lock` (`memoryTracker.cpp:186-187`).
  - `:2890-2894` increments `bda_nwould`, and also `bda_nmiss` when `DirtyRangesTouchBuffers` returns true.
- The writer runs on a guest thread:
  - Path: `HandleFault` (`renderContext.cpp:136-171`) → `InvalidateWriteFault` (`memoryTracker.h:179-188`), or → `InvalidateRegion` (`memoryTracker.h:138-142`).
  - Under the region lock it sets the bits (`regionManager.h:189`) and then bumps the epochs (`:209-210`).
- Nothing else keeps the two apart. `PrepareBda` holds `m_mapped_ranges_mutex` only as a shared lock (`renderContext.cpp:316`), and the fault path also takes it shared.
- Interleaving:
  1. GuestGpu reads stamp E.
  2. Thread T locks R, sets the bit of page P inside registered buffer B, bumps R to E+1 and unlocks.
  3. Collect sees P and counts `bda_nmiss++`.
- A variant: T already holds the lock when the stamp is read. Collect blocks and then sees the bits.
- What knob 1 does on the same interleaving:
  - It skips R, and `seen.stamp` stays E.
  - The cpu-epoch snapshot was taken before the write (`:321`, saved at `:390`), so the next call is not served from the cache (`:324`).
  - The stamp is now E+1 ≠ E, so R is walked.
- Scorer: `vbn113.py:137` sets `BAD = Σbda_nmiss + Σbda_nxthr`, and `:145-148` gives NO_GO for any BAD > 0. `pred/01_vbn113.md` §4 has no allowance for races.
- Rate (estimate, not a measurement): about 52 first-write regions per frame, about 1.0–1.4 bump passes per frame, a window of about 20–300 ns and about 8 800 frames. That gives roughly 0.4–40 expected race counts in 300 s, so P(BAD ≥ 1 from races alone) is somewhere between about 0.3 and nearly 1.
- The error runs one way only. Races can add counts but never hide a real miss, so a **GO stays valid**. A **NO_GO cannot be interpreted**, and the build gives no way to tell a race from a real miss: there is no second stamp read and no per-event log line. One wording correction from the skeptics: `bda_nmiss` *is* an upper bound. The defect is that the sealed rule reads any count as a real miss.

**Addendum (raised by a skeptic, checked in the code by me).** `ChangeState<Cpu,true>` bumps `m_cpu_epoch` *before* `m_epoch`, both with release (`regionManager.h:209-210`). `BdaNoteRegionWrite` comes after both (`:212`). The comment at `:207-208` says the order "does not matter" to the BDA scan. That is wrong, because of the three-epoch cache.
- Failure path: a writer sits between the two `fetch_add`s. `PrepareBda`'s acquire load at `renderContext.cpp:321` sees the new global epoch, but the stamp load at `bufferCache.cpp:2874` still sees the old region epoch.
- Result: the region is skipped and the post-bump cpu epoch is saved (`:390`). The next call is then a cache hit (`:324-339`), and the sync waits until some other epoch moves.
- Scope: this already happens today in every non-bump pass at every knob value, with a window of nanoseconds. In a bump pass it is a real difference between knob 1 and knob 0. The re-read fix below would classify it as a race.
- Fix: swap the order to bits → `m_epoch` → bdabits note → `m_cpu_epoch` (release). Both loads are acquire (`memoryTracker.h:29`, `regionManager.h:142`). After the swap, a snapshot that sees the global bump also sees the region bump, and the re-read discriminator becomes exact. The swap keeps both epochs after the bits, so the `syncfree` ordering argument (`:203-206`) is unaffected.

**Fix.**
1. In `SynchronizeBuffersByRegion`, after `CollectCpuModifiedRanges`, read `RegionWriteStamp(index)` again. Count `bda_nmiss` only if it still equals `stamp`; otherwise count a new `bda_nrace`. Log the first ~40 misses (region, dirty range, buffer, seen/stamp generations).
2. Swap the epoch order as described in the addendum.
3. Rebuild, then reseal `pred/01`, `vbn113.py` (`BINARY_SHA`, `FIELDS_X`) and the fixtures and mutants.
4. If the sealed build is kept instead, record in `ROADMAP.md` **before** the run, as the decision rule requires, that a NO_GO with a small BAD cannot be interpreted. It must be settled by re-running on a build with the re-read, not by closing mode 1.

---

### S2 — MINOR — Existing `bdastamp` hole: a 4 MiB region shared by two mapped ranges is walked only for the lower range [safety‑F1 = check‑F3 = threads‑F2; none of the 6 skeptics refuted it; all graded it MINOR]

**Defect.** `PrepareBda` walks each mapped range separately, in ascending order (`renderContext.cpp:371-373`, `rangeSet.h:63-66`). Only ranges that touch are merged (`rangeSet.h:23,31`). Each walk is bounded to that range's registered buffers (`bufferCache.cpp:2933-2954`) and collects only `[cursor, cursor+bytes)` (`:2842-2843`, `:2889`). But it stores `seen` for the **whole** region (`:2885`).

So in a layout M1 < M2 inside region R:
- M1's walk consumes every stamp move, global bump and `MarkBdaRegions` mark (`:2789-2793`).
- M2's walk then skips R (`:2876`, or `:2851` with bdabits).
- CPU-dirty pages of a registered buffer in M2∩R are never collected by the BDA scan. This covers both its pre-existing dirty pages and later writes. The code has been like this since session 53, and it is identical in `37e0de1^`.

**Corrections from the skeptics.**
1. The arms are not always identical. Suppose the only M1 buffer reaching into R is unregistered.
   - Knob 0/2 bumps the global generation (`renderContext.cpp:352-357`), M1 no longer reaches R, and M2 walks R.
   - Knob 1 marks nothing on erase (a mark happens only on insert, `bufferCache.cpp:152`), so R stays skipped.
   - So in this layout the premise that unregistration "makes nothing relevant" (`bufferCache.cpp:149-151`, `ROADMAP.md:1305-1307`) is **false**. This variant is visible to knob 2, though: the M2 visit is walked with `narrow_would_skip` true, and `DirtyRangesTouchBuffers` finds B, so `bda_nmiss` counts it.
2. The hole shared by all knob values is invisible to the check, because the skip at `:2876` comes before `:2883`.

**Is the layout plausible here?** No instance has been found.
- `log_vid112` has 7–8 logged GPU mappings, which merge into 5–6 ranges, and no two share a 4 MiB region.
- Not excluded: unlogged runtime or program memory (`memory.cpp:4044`, 16 KiB granularity) and partial unmaps that split a range.
- `bda_rng_e`/`bda_rng` = 3 non-empty ranges out of 12.

**Fix (separate `bdastamp` debt, not a condition for shipping knob 1).** Choose one:
- Add a per-pass counter to `BdaRegionStamp`: a second visit in the same pass walks its part but does not overwrite `seen`.
- Walk once over the union of mapped-range pieces.
- Store `seen` only when the walked piece covers every mapped byte of the region.

Also do a one-off dump of the mapped ranges to decide whether the hole is live, and fix the safety comment and the ROADMAP premise.

---

### S3 — MINOR — `armdefer`: a provisional upload moves the region stamp but not the global epoch, so the three-epoch cache delays the settling scan [safety‑F2; 0 of 2 skeptics refuted it]

**Defect and path.**
- A provisional upload bumps only `RegionManager::m_epoch` and the bdabits bit (`regionManager.h:365-375`, "Not the global CPU epoch").
- The unbatched BDA sync reaches it (`bufferCache.cpp:2775` → `:815`, `pass_batch=false`, `memoryTracker.h:297-299`).
- `PrepareBda` returns from its cache on `cpu_epoch`/registration/mapping (`renderContext.cpp:321-339`) before any region walk.
- So the settling scan waits for an unrelated epoch move, and GPU reads through BDA can see bytes written in the protection-lag window.
- It requires `armdefer=1` and `protbatch2=0`. It exists since session 60 and does not depend on the knob. The gate is off by default (`gates.cpp:96`) and pinned `armdefer=0` in `gates_narrow1/2.txt`.

**Fix (only if `armdefer` is revived).** Bump the global CPU epoch on a provisional upload, or invalidate the BDA cache while a provisional upload is pending.

---

### S4 — MINOR, effectively informational — `bda_nxthr` is part of BAD [check‑F2 survives formally, 1 of 2 skeptics refuted it; the same claim as harness‑F2 is refuted 2 of 2]

The rule keeps check‑F2 formally alive. Its only concrete path, however, is refuted by 3 of the 4 skeptics across both lenses, and I confirmed the callers by grep:
- `Presenter::PrepareFrame` (`swapchain.cpp:745`) has exactly one caller, `videoOut.cpp:1030`, inside `FlipQueue::Prepare`.
- `FlipQueue::Prepare` has two callers, `videoOut.cpp:2877` and `:2887`.
- Those are reached from the PM4 flip handlers and from `graphicsRun.cpp:1050` `PrepareCpuFlip`, both inside `GuestGpu::Process` on the single GuestGpu thread.

So the `ResolveSurface` → `ObtainBuffer` → `Register` → `MarkBdaRegions` chain runs on the scanning thread, and `:2786` does not count it. The real present thread (`swapchain.cpp:838-879`) never touches the buffer or texture cache. The comments at `swapchain.cpp:748` and `bufferCache.cpp:850` that suggest otherwise are stale. With `m4baton=0` pinned, `bda_nxthr` is 0 by construction.

**Residual action.** Record before the run that a NO_GO with `Σbda_nmiss = 0` and `Σbda_nxthr > 0` means "an unknown off-thread registrar". It is to be investigated, not read as a miss. The scorer prints the two totals separately (`vbn113.py:167-169`).

---

### S5 — MINOR — B3–B5 are means over all rows, but the band was set from a median; B4 is about a coin flip at its upper edge [harness‑F1; 0 of 2 skeptics refuted it]

**Defect.**
- B2 is the median of `FrameTrace-draw` rows from the stable frame on (`vbn113.py:116-120,131`).
- B3–B5 are `tot/rows` over **all** `FrameTrace-x` rows, load rows included (`:108-114,138`). The prediction texts still call them a "level" (`:45,47`), and the seal says only "a frame".
- `bda_nwould` ≈ `bda_scan` − ~52 − marked regions (`bufferCache.cpp:2883-2891`).
- In OLD runs the rescan count k is skewed: k=1 in 62 %, k=2 in 27.5 %, k≥3 in 7.7 %, mean ≈ 1.41 (`log_vds111b`). So the steady-state mean `bda_nwould` is ≈ 1 420–1 434, on or above the 1 400 edge. The band looks derived from the median (1068 − 52).

**Correction from the skeptics.** The all-row B4 is between about 1 350 and 1 427, depending on how much of the load-phase excess counts as would-skip. Map-invalidated and first scans do not count. So P(MISS) is about 35–80 %, not a firm MISS.

**Impact.** None on the verdict. Predictions only print HIT/MISS (`vbn113.py:149-157`), and GO/NO_GO uses only errors, regime and BAD (`:141-148`).

**Fix.** Record before scoring that a B4 MISS near 1 400 comes from the choice of statistic and says nothing about the mechanism. Future seals should name the statistic.

---

### S6 — MINOR — BAD is summed only over rows that parse, and nothing checks row continuity [harness‑F3; 0 of 2 skeptics refuted it]

**Defect.**
- `X_ROW` is anchored at the start of the line (`vbn113.py:38,108`). The captured `n` is never used, and nothing compares the row count with the main `FrameTrace` rows.
- A row glued onto another thread's line that lacks a newline silently drops its `bda_nmiss`/`bda_nxthr`. That is the unsafe direction: it could turn a NO_GO into a GO.
- Writers exist that can leave a line without a newline: 20 of 1 774 `LOGF` calls, plus guest `printf` via `guestPrintf.cpp:774`. Counts after the last flip are never printed (`videoOut.cpp:1246`, and the run ends with a hard kill).
- Measured risk is currently 0: 0 glued rows and 0 gaps in 14 711 rows of `log_vds111b` and `log_vdg112`.

**Fix.** Before accepting a GO, run `C:/kyty/s113/audit113pre/rowcheck.py` on `log_vbn113.txt`. It must show contiguous `n`, 0 mid-line rows, and an x-row count equal to the main row count (±1). Future scorers should add a STREAMS_COMPLETE-style term.

---

### S7 — MINOR — `go113.sh` installs whatever build is present, with no identity check before the run [harness‑F4; 0 of 2 skeptics refuted it]

**Defect.**
- `go113.sh:15-16` runs `enter_scene.py vbn113` without `--no-install`. `enter_scene.py:566-570` copies `C:/kyty/build/install/kyty_emulator.exe` without comparing its hash.
- IDENTITY and BINARY pin `94362eae` only at scoring time (`vbn113.py:25,71-82`).
- A rebuild before launch (another agent is active) therefore gives NOT_ADMITTED. That is fail-safe, but the run is wasted, and the chain repeats only on NOT_EVALUABLE (`go113.sh:21`). The seal allows the second tag only for the NEW regime, so recovery would need a recorded deviation.
- Current state: the build output is `94362eae…` (matches), the installed exe is `b47b58a9…` (the old build), and a pinned copy exists at `C:/kyty/s113/kyty_emulator_94362eae.exe`.

**Fix.** Check `sha256(C:/kyty/build/install/kyty_emulator.exe) == 94362eae…` by hand immediately before launch and record it. Alternatively, install from the pinned copy, which means changing and resealing `go113.sh`, since it is sealed in `SEALS113.txt`.

---

### S8 — MINOR — Seal §2 "nothing else on the machine" is not enforced by any admission term [harness‑F5; 0 of 2 skeptics refuted it]

**Defect.**
- `enter_scene.py:564,669` records `pre_run` (GPU state and the host process census), and on a busy GPU it only prints a WARNING (`:262-264`).
- `vbn113.py` never reads `pre_run`. `guards.py` is not in the chain, and even its check 0 (`guards.py:580-625`) looks only at the GPU.
- `go113.sh:8` writes `SEALED_RUN.lock` without checking whether it is already held.
- This matters now: the user says a heavy agent job is running. Load cannot turn a real miss into zero, but it changes which interleavings are sampled, which feeds S1.

**Fix.** Do not launch `go113.sh` until the other job has finished. Before scoring, check by hand that `vbn113.json` `pre_run` has GPU util median ≤ 10 and no foreign heavy process in `host.top`, and record the result.

---

### S9 — MINOR — No archived output backs "31 mutants killed", and the mutants target the draft scorer [harness‑F6; 0 of 2 skeptics refuted it]

**Defect.**
- `mut_vbn113.py:6-7` reads `C:/kyty/s106_stage/vbn113.py`, the draft (`fa35ad73`). It differs from the sealed copy (`9e89d715`) only at lines 23-24 (`PRED_SHA`/`PRED_BYTES`), and `test_vbn113.py:23-25` overrides both.
- All 31 anchors appear exactly once in both copies, and an inspection finds that each mutant is killed by at least one fixture.
- Commit `942fd2f` contains no mutant output, which matches earlier sessions' practice.

**Fix (bookkeeping only).** Outside any sealed run, point the mutant script at the sealed copy, or record the draft's sha, then archive the `killed 31 of 31` output next to `SEALS113.txt`. Note that the test `rmtree`s `s106_stage/fx_vbn113`.

---

## 2. Refuted findings

- **harness‑F2** (`bda_nxthr` fires on a present-thread registration made under the render mutex): refuted by 2 of 2 skeptics. `PrepareFrame`/`ResolveSurface` run on the GuestGpu thread (see S4), which is the thread that sets `m_bda_scan_thread` (`bufferCache.cpp:2830`). The present thread's `Present` never reaches the caches. The same claim survives only formally as check‑F2 (S4).
- **Partial refutations inside surviving findings** (the finding survives, a sub-claim does not):
  - S2: "knob 0 behaves identically" is false after an unregistration; that variant is counted by `bda_nmiss`.
  - S5: "B4 ≈ 1 420, MISS" becomes "about a coin flip at the 1 400 edge".
  - S1: "`bda_nmiss` is not an upper bound" is wrong wording; it is an upper bound that the sealed rule reads as an exact count.

---

## 3. Checked OK

### Safety lens
- Every setter of a CPU-dirty bit moves the region stamp, through `ChangeState<Cpu,true>` (`regionManager.h:202-212`). That covers `InvalidateRegion` (`memoryTracker.h:142`), `InvalidateWriteFault` (`:188`), `MarkRegionAsCpuModified` (`memoryTracker.cpp:193-199`) and `UntrackMemory` (`:244-246`).
- Creating a region moves its stamp from `{nullptr,0}` to `{ptr,1}`. Managers are never destroyed, so there is no ABA.
- A walked portion leaves no CPU-dirty page of a registered buffer:
  - `SynchronizeBuffersOfDirtyRanges` visits every intersecting buffer (`bufferCache.cpp:2765-2777`).
  - The `HasCurrentUpload` early return cannot fire while a bit is set (`:802-806,836`).
  - `SyncFreeSkip` is sound under acquire/release.
  - The `protbatch2` path consumes bits the same way, and the gate is pinned 0.
- A registration bumps `m_registration_epoch` and marks its regions on the same thread in the same call (`:112,125,152`). So `bda_cached` can never return over a fresh mark. A mark placed during a scan forces another scan, because the pre-scan epoch is the one saved (`renderContext.cpp:322,391`).
- `MarkBdaRegions` index math is right and clamped (`:2789-2793`), and size 0 cannot occur (16 KiB alignment, `:642-644`; the null buffer is not registered, `:395-397`).
- Stamps still empty at registration are safe: `m_bda_stamp_generation` starts at 1 and only increases (`bufferCache.h:286,290,144`). Generation 0 never equals the current generation (`:2851,2876`).
- Joins and unregistration: `JoinOverlap` unregisters the old buffers, then `Register(new)` marks the union (`:628-667`). The GC and delete paths untrack before unregistering (`:1991-1993, :2024-2027, :2521-2532`).
- Guest-map changes still invalidate globally at every knob value, and `NoteBdaMapInvalidation` runs after the bump (`renderContext.cpp:348-351`).
- Nothing other than `PrepareBda` and the bdabits lines depends on the global bump.
- Knob 2 is a valid proxy for knob 1. Stamps are monotone, so the would-skip set (`:2883-2884`) is a superset of knob 1's skip set. `DirtyRangesTouchBuffers` walks buffers the same way as the sync, and it runs before the sync.
- Every `Register` path runs on GuestGpu (callers enumerated; `SendCommandSync` at `:469`). `m4baton=0` is pinned.
- Downloads, readback prefetch and stale reads never set CPU-dirty bits.
- Switching the knob at any moment is safe, because marks are unconditional (`:152`).

### Check lens
- `bdabits` cannot hide a region knob 1 would skip: the gate is off (`gates.cpp:199`), and in a bump pass a would-skip region has generation < current.
- The three-epoch early return happens before the knob is read and does not depend on it. The same passes scan at every knob value.
- `DirtyRangesTouchBuffers` (`:2797-2812`) matches the non-batched and batched sync walks. `CollectCpuModifiedRanges` clears its output first (`memoryTracker.cpp:167`).
- A mark cannot be lost on the scanning thread: `seen` is read before it is overwritten, and a mark made during this region's sync persists after `:2885`.
- Run sequentially, the would-skip predicate equals knob 1's skip decision on the same trajectory.
- Scans that happen only at knob 0 occur only in bump passes, and the check runs in every bump pass (`renderContext.cpp:347`).
- ARMED `Σbda_nskip == 0` is right for knob 2 (`:353-354`), and the map-bump branch takes precedence (`:348`).
- All 8 new counters print even when zero (`videoOut.cpp:2512-2518`). The built exe matches `BINARY_SHA` `94362eae`.
- Archive evidence supports 0 real misses: `pb2_sync` is 67 in OLD against 66–75 in NEW per frame (`MECHANISM.md:105-106`).

### Threads lens
- Every `ChangeRegister<insert>` caller runs on GuestGpu, flip-surface resolve included (`videoOut.cpp:2877/2887`, `graphicsRun.cpp:1050/3111`).
- The M1 workers, the draw-ahead walker, `cspfree` and the compute lookahead never reach `FindBuffer`, `CreateBuffer` or the BDA scan.
- `m_bda_region_stamps` is resized once, on the marking thread (`:2827-2829`), so the `seen` reference stays valid.
- `m_bda_scan_thread` is written and read on the same thread, so there is no data race. It is a "same thread as the last scan" test, not a race detector.
- The knob is read once per non-cached `PrepareBda` (`renderContext.cpp:346-347`), and `m_bda_narrow_check` is set before every scan.
- Knob 0 is exactly the pre-patch behaviour; the mark is redundant after a global bump.
- The new per-region work runs only on walked regions and short-circuits at knob 0/1. `FrameStats::Add` costs one load plus a compare when disabled (`frameStats.h:1959-1963`).
- Harness names match the build (`videoOut.cpp:2503-2519`). `fslean=0` and `m4baton=0` are pinned, and the enum and table rows are last (`gates.h:585`, `gates.cpp:399`).

### Harness lens
- The seal hashes of `pred/01_vbn113.md` (`e6b7b397`, 3 443 B), `vbn113.py`, `test_vbn113.py`, `mut_vbn113.py`, `gates_narrow1/2.txt` and `go113.sh` all match `SEALS113.txt`.
- All 11 `FIELDS_X` names print on every x row, each exactly once. `bda_scan` exists only on `FrameTrace-draw`. The draw row `n` and the main row `n` are both `flip_status.count` (`videoOut.cpp:1259/1267`), so the stable filter is consistent.
- In the archive logs, x rows = main rows = draw rows, there is exactly one `GpuClockPin: mode 1` line, and there are 0 markers.
- The REGIME threshold of 500 separates OLD (median 1 069) from NEW (median 56).
- ARMED is reachable at knob 2 (`bda_ginv_reg` ≈ 1.39/frame OLD). `MIN_WOULD=1000` is far below the expected sums: about 10^7 in OLD and about 5·10^5 in NEW. So a NEW run reads NOT_EVALUABLE and the repeat can fire.
- The chain's repeat grep survives CRLF (`crlf_probe.sh`). The `vbn113b --no-install` run reuses the build that `vbn113` installed.
- `gates_narrow2` = base + ` bdanarrow=2`, and the knob's limit is 2. The defaults `daslot=1`, `daguard=1` and `cspfree=1` are unpinned and match the seal.
- `enter_scene.py:535` strips every inherited `KYTY_*`, so `KYTY_GPU_CHECKPOINTS`, `KYTY_REC` and `KYTY_PIPELINE_PRECACHE` cannot leak in.
- The seal text matches the scorer: the admission terms, the rule, the B1–B5 bands, 74 fixture checks and 31 listed mutants.
- Artifacts line up (`enter_scene.py:490-495`). The ported launcher differs from s112 only in ROOT and docstrings.

---

## 4. Verdict

Knob 1 is not less safe than knob 0 on any path found in the game's observed mapping. The one layout where it is worse (S2, after an unregistration) has not been shown to exist, and when it occurs it is counted by `bda_nmiss`. A GO from the check can be trusted. A NO_GO cannot be interpreted until the race discriminator in S1 exists.

KNOB1_SAFETY: NOT REFUTED; CHECK_VALIDITY: WEAK; HARNESS: NEEDS FIXES (1. S1: add the stamp re-read with `bda_nrace` and a miss log, swap the epoch order at `regionManager.h:209-212`, rebuild and reseal; or record the small-BAD NO_GO interpretation rule in ROADMAP before the run. 2. S7: check the build sha 94362eae immediately before launch. 3. S8: do not launch while the other heavy job runs, and check `pre_run` by hand. 4. S6: run `rowcheck.py` for continuity before accepting a GO. 5. S4/S5: record the `bda_nxthr`-only NO_GO rule and the B4 edge expectation before scoring. 6. S9: archive the mutant output against the sealed scorer.)