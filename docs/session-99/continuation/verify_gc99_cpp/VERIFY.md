# Independent C++ GC audit review

Verdict: **PASS within the requested observer scope. No concrete defect found.**

Reviewed 2026-09-19 against HEAD `b129fbbd0bd7b0e5081e2e0928cfbf7fefa26248`. Read actual current diff and surrounding callers; did not read author reports, FACTS, diagnostic outputs, or author gc_audit_tests. The unrelated CPU observer additions were excluded. No source edits, compilation, emulator, or game execution.

## Findings and evidence

All paths below are relative to `C:/kyty/KytyPS5`.

1. **Opt-in, no GC policy change.** `src/graphics/host_gpu/renderer/cache/textureCache.cpp:3265` accepts exactly environment value `1`; missing, `0`, empty or other strings disable. Added code reads state, logs mode once and writes FrameStats counters only. Existing `floor_hold` is still computed exactly once at :3272. Existing two tick mutations, trigger return, held return, collection predicates, and FreeImage call are unchanged. Audit-disabled overhead includes its one-time mode log/static initialization and cheap tests; this is not literally zero overhead.

2. **Independent sticky subset is current and read-only.** `src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:997` reads only `t_bf_slice != nullptr && t_bf_slice->sticky_armed_counted`; no CurrentOp, live gate, BfInitBase, BfLatch or adoption. Actual flag becomes true at :846–848 when a mode-1 submission first fixes an armed sticky value. `src/graphics/guest_gpu/graphicsRun.cpp:769` sets the current pointer around the whole Process call, clears it at :771 and only then calls SliceComplete at :774. All five renderer GC call sites (:975, :996, :1021, :1031, :1039) are within Process. Hence the inspected GC calls read a live current submission before its count is removed. Outside the slice the getter returns false even if CurrentOp remains armed. Existing pointer lifecycle is single-thread TLS; the added getter introduces no ownership or synchronization change.

3. **Expected hold and lost sticky detection.** `textureCache.cpp:3277` uses the required union of ordinary helper and current counted sticky. :3282 expressly marks sticky true/helper false as bad independently of clock delta, including critical pressure where a correct delta of 1 would otherwise mask the lost sticky. Helper uses a global sticky count at `descriptors.cpp:1013`; witness reads the current per-submission boolean directly, not that global aggregate. Both derive from the same original latch decision, so this is independent observation of an existing subset, not an independent proof that every latch decision is correct. Base, pending, and other submissions' sticky values are not independently witnessed.

4. **Per-call clock accounting exactly once on all current normal paths.** Before tick is saved at :3271. Below-trigger return checks at :3339; held/noncritical return checks at :3353; ordinary collection path checks at :3359. These paths are exclusive. Existing mutations :3291 and :3356 yield 0 for held noncritical, 1 otherwise. No m_gc_tick write exists in collection or FreeImage: the normal-path check before collect therefore sees the complete current call's clock delta. Expected delta is selected from hold and actual critical pressure, not from observed tick behavior. Backwards, unsigned wrap, skipped increments, advancing under hold and catch-up increments are detected. The clock is protected by the existing `m_lock` at :3257.

5. **Critical uses refreshed pressure and covers permitted override.** Device usage refresh is at :3314–3316, before :3338/:3351/:3359. Below-trigger/held early returns pass false because the actual critical override was not entered. Normal path uses `m_total_used_memory >= m_critical_gc_memory`, the exact threshold that controls existing held override and aggressive collection. The trigger cannot exceed critical under constructor formula (:246–255), and defaults are trigger 0, critical 3 GiB. Thus a critical held call cannot silently return below trigger. Audit occurs before collection changes accounting, preserving the override that actually happened even if memory later drops. The separate critical counter increments only when expected hold and critical are both true.

6. **Root evictions observed at the real call.** :3432–3437 counts only after candidate validity, association, keep, and download skip tests; immediately before the sole GC FreeImage root call. It covers both collection passes and critical collection. `DeleteImage` recursively frees depth associations at :430–438; those descendants are represented by their counted root and are not counted twice. This is root eviction calls, not the number of images including children or eventual physical Vulkan destruction. FreeImage performs the expected deletion on the valid candidate path (:473–489).

7. **Five fields retain zeros.** `src/common/frameStats.h:1642` onward declares the five counters. `src/graphics/presentation/videoOut.cpp:2370–2374` maps all five to unscaled integer fields. The shared loop at :2396–2400 unconditionally emits every named field; there is no zero filter. The ordinary FrameStats-enabled/previous-snapshot trace conditions still apply (:1223, :1245); “always printed” means every emitted FrameTrace-x record, not that tracing is forced on.

## Independent counterexamples

`independent_cases.py` and generated `independent_cases.json`: **38 cases PASS**, including ten caught mutants: held advancement, base stall, catch-up in both states, backwards movement, uint64 wrap, critical stall/double increment, and lost sticky with otherwise correct clock behavior both at noncritical and critical pressure. Boundary cases cover below/at trigger and below/at critical, memory refresh crossing pressure in both directions, and stale CurrentOp outside a slice. This is a specification model and source review, not execution of compiled C++ or evidence about a live game.

## Limits

This approves the instrument, not a calibrated run, GC correctness everywhere, floor reversibility, comparability, M3, or any performance conclusion. Evictions outside RunGarbageCollector are out of scope. Future tick mutations after the current normal-path check would require moving/reviewing the check; there are none now. Snapshots can split independent counters across adjacent flip rows; verdict logic must inspect the appropriate complete population and require checks>0 to avoid treating disabled/no-observation zeros as evidence.

## Reviewed source hashes (SHA-256)

- textureCache.cpp: `DD75732BAB8EA922399E67870A9382532E4D18B1EB00F683781EB8041EE6DC80`
- descriptors.cpp: `781A454CEE79E6AC9A75A96AD6FA002B0983FF696B6A70B798D19D7C51C4B6D7`
- descriptors.h: `B8982E4C45F7DBC80600C136B531E4604D62990FB8A38426BE32CCC83906C8CA`
- frameStats.h: `C2A654A93D79370F364D051F01D964AA49B82DE4426FFA532285F1FC1B023A21`
- videoOut.cpp: `A45E6CF01066FB3BFAD3452B73E0930EF85E68AC3038555D111263A866BF03C6`
