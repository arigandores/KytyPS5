# Independent C++ VERIFY, 2026-09-19

Scope: current uncommitted diff of frameStats.h, descriptors.cpp, videoOut.cpp against HEAD. Read source and ROADMAP opening only; no author FACTS/explanations/analysis or gameplay outputs. No build/game run, no source edits.

Verdict: PASS static review of requested additive instrumentation, subject to measurement limitations below. No concrete new implementation defect found. Compilation/runtime validity is not established by static review. git diff --check passed.

## Assertions

1. SAME CPU CLOCK: descriptors.cpp:3307 and :3318 call FrameStats::ThreadCpuNs(ThreadRole::Gpu), identical reader/role to cpu_gpu_us (videoOut.cpp:1241-1253, :1276). The actual API is QueryThreadCycleTime divided by the cached TSC calibration (frameStats.cpp:604-619). GuestGpu registers this role at graphicsRun.cpp:663.
2. OLD BUDGET UNCHANGED: mode/budget checks, cumulative slice target/clamp, original begin/while, floor.burned_ns and BindFloorBurnNs updates are unchanged (descriptors.cpp:3262-3294, :3310-3314, :3332-3333). Probe work is outside the wall burn interval and never enters the budget.
3. INERT CASES: modes outside 2/3 return at :3263; budget zero at :3267; exhausted/zero slices at :3282/:3288. All precede static env initialization. Env unset/0 never executes either added ThreadCpuNs call (:3297-3308, :3315-3318). This means no ADDED CPU query: ordinary existing FrameTrace queries remain.
4. ONE CLASSIFICATION PER SAMPLED SLICE: cpu_begin != 0 and cpu_end > cpu_begin adds delta + success at :3321-3324; all remaining cases increment bad at :3326. Zero API result, unknown role, end zero, backwards clock, and equal pair are explicitly bad. No wall-time substitution. No exception/early exit exists inside the new sample span. Valid here means successful strictly positive pair, not independent clock accuracy proof.
5. NO NEW LATCH READ: only original BindFloorCurrentOp().mode at :3262; new code reads no gate/latch and does not mutate bindings, floor mode, frame, or target.
6. OUTPUT: four enum values at frameStats.h:1613-1616 map one-to-one to named fields at videoOut.cpp:2362-2365. false is micros=false, NOT omission of zeros (NamedCounter :1459-1462). Loop :2391-2397 serializes all entries unconditionally, including zero.
7. PROBE BOUNDS: :3306-3308 bracket the entire first ThreadCpuNs call; :3316-3319 bracket the second. Both costs are summed for successes AND bad pairs at :3330. CPU span includes the tail of first query, the intervening clock/control work and the head of second query. Probe bounds include both query tails outside that CPU span too.
8. COMPILE/SCOPE: cstdlib and required declarations already included; uint64_t/enum additions fit existing patterns. Counter-sized arrays and snapshots derive their extent from Counter::Count. No additional default/gate change seen in the diff. The unrelated dirty submodule remains outside review.

## Limitations, not new blocking defects

A. These are trace counters: trace must be enabled and fslean off. RegisterCurrentThread skips its handle without Enabled (frameStats.cpp:232-234); Add can discard high-index counters in lean mode (frameStats.cpp:189-194, frameStats.h:1781-1785). Therefore env=1 alone is not a universal observability guarantee. Under trace/lite + fslean=0 the requested counters are active.
B. probe_ns is query wall bounds, NOT total instrumentation overhead. Static initialization/logging, env branches, intermediate timestamps/control, and Add operations are not all included. These remain in cpu_gpu_us. The initial mode log also exists with env0 at first actual burn; inert modes/budget0 do not reach it.
C. NowNs is the existing un-serialized RDTSC clock with its existing positive-calibration/monotonicity assumptions (frameStats.cpp:197-210). Probe subtraction adds no wall-clock-invalid handling; neither does existing wall burn. This review cannot independently certify ns accuracy/frequency assumptions of QueryThreadCycleTime normalization. Sharing the cpu_gpu_us clock is proved by code, hardware accuracy is not.
D. Role Gpu is a registered thread, not necessarily the caller. The baton path explicitly avoids registering as Gpu (graphicsRun.cpp:1602-1606). Protocol must keep actual burn on GuestGpu; if other execution routes run it, a zero/stalled Gpu pair will go bad, but a positive unrelated Gpu delta cannot be detected by this patch alone.
E. Counter snapshots read separate atomics (frameStats.cpp:213-221; videoOut.cpp:1239). Sampling boundaries may split delta/N/probe/wall updates across adjacent output rows. Exact per-row equality is not guaranteed; aggregate/steady-window checks should account for boundaries.
F. New query overhead can change frame pacing and number of actual sampled slices indirectly even though wall budget arithmetic is unchanged. Work/area/pacing admission is a runtime protocol responsibility.

Evidence not claimed: build success, runtime sample positivity, probe size, no hangs, unchanged FPS/work, calibration validity, or final M3 verdict.
