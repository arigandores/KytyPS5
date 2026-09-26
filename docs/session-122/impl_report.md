# Session 122 - burn implementation workflow report

#### IMPL
The `burn` knob is in and the emulator builds (`BUILD OK`, only warnings that were already there). The offline spin check passes 3 of 3 runs (`ALL OK`). Nothing is committed and the game was not run. The first spin check failed, and I fixed it with three follow-up patches; details under "Spin check".

**Build and checks**
- sha256 of `C:/kyty/build/install/kyty_emulator.exe`: `8149147e36271ec7399daf04f23cc3e6bd9543b07b6da8e8010385ef221207b0`. An earlier build (`4a2f4215…`) was overwritten and does not include the three follow-up patches.
- Build tail:
  ```
  Building CXX object common\CMakeFiles\common.dir\frameStats.cpp.obj
  -- Installing: C:\kyty\build\install/kyty_emulator.exe
  -- Up-to-date: C:\kyty\build\install/libwinpthread-1.dll
  BUILD OK: C:\kyty\build\install\kyty_emulator.exe
  ```
- Logs: `C:/kyty/s122/patches/build_burn.log` (full build) and `build_burn2.log` (rebuild after the follow-ups).
- `check_gate_order.py --src C:/kyty/KytyPS5/src` exits 0 ("GATE ORDER: clean"; knobs 37 entries = 37 rows, `Burn` last).
- The build map has `Common::FrameStats::BurnSpinUntil` as its own function. Disassembly shows the loop is `rdtsc`, compare, `pause`, jump, so it was not optimised away.

**Files changed** (all under `C:/kyty/KytyPS5/src`)
- `common/gates.h`: `Burn` added after `TexMemo8`, "LAST row" comment moved.
- `common/gates.cpp`: row `{"KYTY_BURN", "burn", 0, 899999}` after texmemo8, "LAST row" comment moved.
- `common/frameStats.h`: counters, `BurnSite` enum, `BurnSpinUntil`, the inline hooks, `BurnPublishFrame`.
- `common/frameStats.cpp`: the cold paths (decode, block, spread, self-test, placebo, code 7).
- `graphics/presentation/videoOut.cpp`: key published right after `Gates::Poll` (after `poll_ns`, before `SetLean`); named rows added.
- `graphics/guest_gpu/graphicsRun.cpp`: code 1 after `EXIT_IF(!has_submission)`, before `Process`; code 7 in `Submit` before `m_submission_mutex`.
- `graphics/host_gpu/renderer/commandRecorder.cpp`: codes 2/5, end of the `if (m_gpu)` block, before `Execute`.
- `graphics/host_gpu/renderer/pipeline/pipelineCache.cpp`: code 6 at the top of the worker loop (`index == 0`); code 3 before `AheadRun`.
- `kernel/eventQueue.cpp`: code 4 before `return OK`, only when the wait was blocking.

Nothing under `src/graphics/shader/**` was touched, and there is no new source file.

**Patch scripts** (`C:/kyty/s122/patches/`, run in this order)
1. `patch_burn.py`: the main patch.
2. `patch_burn_carry.py`: counts each spread step's bookkeeping tail inside the dose.
3. `patch_burn_cpuw.py`: the CPU cross-check compares against the wall between the two CPU readings.
4. `patch_burn_gap.py`: adds a measured `rdtsc` gap to each spread step.

Also there: `burn_hooks.diff`, the diff of the call sites.

**Counters, in print order** (after `tm8_pb_n`, same order in `frameStats.h` and `videoOut.cpp`, all raw with `micros=false`)
`burn_g_ns burn_g_n burn_g_cpu_ns burn_g_cpu_w burn_g_seen burn_r_ns burn_r_n burn_r_q burn_r_cpu_ns burn_r_cpu_w burn_r_seen burn_m_ns burn_m_n burn_m_q burn_m_cpu_ns burn_m_cpu_w burn_m_seen burn_m0_seen burn_t_ns burn_t_n burn_t_cpu_ns burn_t_cpu_w burn_t_seen burn_s_seen burn_s_main burn_p_ns burn_p_n burn_p_cpu_ns burn_p_cpu_w burn_p_seen burn_late burn_cpu_bad`

**Spin check** (`C:/kyty/s122/unit/burn_unit.cpp`, built by `build_burn_unit.cmd`, output in `run_burn_unit.out`)
It compiles the same `BurnSpinUntil` from `frameStats.h` with clang-cl `/O2`, and calibrates the timer the way the emulator does. Results against QPC over 200 repetitions per dose:

| Dose | Mean error | Max error | CPU/wall median |
|---|---|---|---|
| 200 µs | +0.16 µs (+0.08 %) | ≤ 3.8 µs | 1.000 |
| 1000 µs | +0.22 to +0.30 µs (+0.03 %) | ≤ 5.3 µs | 1.000 |
| 2000 µs | +0.28 to +0.35 µs (+0.02 %) | ≤ 12 µs | 1.000 |

The large maxima are single interrupts. A copy of the spread step (2000 µs, q = 227 ns, about 7 700 steps) lands within −0.01 % to +0.36 % of the budget, with sampled CPU/wall of 1.24 to 1.37.

The first two runs failed on the spread. Its counted dose was 3.3 % short of the real wall time, then 2.8 % after the carry fix. The remaining gap of about 7 ns per step equals the cost of one back-to-back `rdtsc` pair, which I measured at 6.8 to 7.5 ns (`unit/tmp/rd.cpp`). The sampled CPU/wall also read 0.60 because the two `QueryThreadCycleTime` calls cost more than a 230 ns chunk. `patch_burn_carry.py`, `patch_burn_cpuw.py` and `patch_burn_gap.py` fix these.

**Where the code differs from the spec, and why**
1. **Code 7 comes after the `draw_commands.empty()` early return**, still before the lock. An empty `Submit` submits nothing, so it should not count as the first graphics submit.
2. **The frame key is tracked per site on each thread.** One thread can reach two sites: the main thread reaches both `KernelWaitEqueue` and `Submit`, and M1 worker 0 reaches both its loop top and its job site. With one key per thread, the first site would take the frame and the other would never fire.
3. **Code 7 uses a global key taken by the first submitter**, so it fires on the first graphics `Submit` on any thread. It has its own coverage counters: `burn_s_seen`, and `burn_s_main`, which counts submitters with the Main role. `burn_t_seen` stays the code-4 coverage. Code 7's dose goes to `burn_t_*`.
4. **Extra counters beyond the spec:**
   - `burn_*_cpu_w`: RC3's CPU is sampled on only 1 spread step in 64, so it cannot be compared with `burn_*_ns`. Admission becomes `cpu_ns ≥ 0.9 · cpu_w`. It is the wall between the two CPU readings, and on sampled steps the spin starts after the first reading.
   - `burn_m0_seen`: coverage for code 6.
   - `burn_p_seen`: coverage for the placebo.
   - `burn_cpu_bad`: failed CPU-time readings.
5. **The spin is in `frameStats.h`**, using the same built-ins that `__rdtsc` and `_mm_pause` expand to. This lets the unit test compile the identical function without adding a file, which would trigger a CMake re-glob.
6. **What counts as the dose:**
   - Blocks: timed from after the decode, the one-time self-test and the arm log, to just before the counter updates. So the 1 ms self-test is not charged to the first frame; it runs at block position 0, outside window 10–88.
   - Spread steps: each step also counts the previous step's bookkeeping tail and the measured `rdtsc` gap (from the unit test). The last tail of each frame is dropped.
7. **The self-test log line has two extra fields**, `spin_us=` and `rdtsc_gap_ns=`.
8. **How the placebo is started and pinned:** the GuestGpu thread starts it the first time it reads code 8, so it needs GuestGpu submissions. It is detached. It re-applies `DrawAheadApplyPin(false)` before each spin, passed in as a function pointer from the code-1 site. It polls the key with `Sleep(1)`.
9. **`burn_r_n` / `burn_m_n` count armed frames for the spread codes**; for code 3 that is per worker.
10. **Code 6 checks the key at the top of worker 0's loop.** If worker 0 slept through the flip, it burns on its next loop turn after that batch.
11. **Code 1 runs while `m_processing` is true.** So a `WaitForIdle` waiter (`GuestGpu::Done`) waits through the burn. The review accepted this as the same as a slower `Process`.

At `burn=0`, each hook call costs one acquire load and one thread-local compare (one more load on spread sites, two loads on `Submit`). Once per new key per site there is one cold call: a `seen` count, one knob read, and for the main site a role check. For code 7 the cold call is one CAS on the global key. Per flip there is one release store. Nothing spins, logs, or starts a thread.

The four patch scripts are listed above. Other files are in `C:/kyty/s122/unit/`: `burn_unit.cpp`, `build_burn_unit.cmd`, `run_burn_unit.out`, `burn_unit.exe`, `tmp/rd.cpp`, `tmp/edit_unit_gap.py`.
#### REVIEW PASS_WITH_FIXES
 BLOCK {"file": "C:/kyty/KytyPS5/docs/ROADMAP.md (s122, after item 2 at :2824-2844)", "problem": "The implementation makes decisions that neither ROADMAP s122 item 1-2, design122.md nor the RC list contains. Under the program rule, a decision that is not written down is invalid, so these must be recorded before the smoke. (a) Code 7 fires after the `draw_commands.empty()` early return (graphicsRun.cpp:194-198). The lock order is still correct: the hook comes before `GpuMutexLock` at :199. (b) The frame key is kept per site on each thread (frameStats.h:2709, `t_burn_key[BurnSite::Count]`), not as the single `t_burn_key` of the design. (c) RC1 requires \"take `burn_t_seen` from that site\". Code-7 coverage is instead published as the new counters `burn_s_seen` and `burn_s_main` (frameStats.cpp:985-988), and `burn_t_seen` stays at the code-4 site. The burn wall of code 7 is still booked to `burn_t_ns`/`burn_t_n`/`burn_t_cpu_*`. (d) The counted spread dose `burn_{r,m}_ns` has two parts that are not the wall of the spin itself. `t_burn_carry` is the previous step's bookkeeping. `t_burn_gap` is a per-process estimate of one back-to-back rdtsc pair, added on every step (frameStats.cpp:897-898, :704-719). So `burn_{r,m}_ns` is partly estimated, while the design says \"MEASURED dose\". (e) New `burn_*_cpu_w` counters give the wall between the two cross-check readings, and `burn_cpu_bad` is new. (f) After its first arming the placebo thread runs for the rest of the process and wakes every 1 ms. It is therefore absent in the first A block and present in every later block.", "fix": "Add ROADMAP s122 item 3 with the lead as author, before the smoke. It records (a)-(f) as accepted or rejected. For (c) it states that the scorer reads `burn_s_seen` (and `burn_s_main` as the role count) for code-7 coverage, and `burn_t_*` for the code-7 dose. For (d) it states that the spread N-bar includes a per-step estimated term of about 7 ns, validated offline at -0.01 % to +0.36 % against QPC by `C:/kyty/s122/unit/run_burn_unit.out`. Alternatively, rename to match RC1 literally, but then the text and the code must agree. No code change is needed if these items are accepted."}
 NB The spread CPU cross-check is biased upward. `BurnSpreadStep` (frameStats.cpp:890-906) reads `QueryThreadCycleTime` outside `s0..s1`, so `burn_{r,m}_cpu_ns` includes most of the cost of the two QTCT calls, but `burn_{r,m}_cpu_w` does not. The unit test shows cpu/wall = 1.32-1.37 with no preemption. A 0.9 threshold therefore only fires when more than ~45 % of the sampled spin wall was preempted. design122 makes the cross-check a printed diagnostic, so it is not a gate. The scorer should print the spread ratio against the unit-test baseline of ~1.33, not against 1.0. The block codes are unaffected: cpu/wall is 1.000 at 2 ms.
 NB Converting each spread step separately (`BurnNs(elapsed)` truncated per step, frameStats.cpp:900) loses about 0.5 ns per step. Over ~7 700 record steps that is ~4 µs (0.2 %) low, which matches the unit test's counted 1995-1997 against QPC 2000-2007. To fix, accumulate cycles in TLS and convert once when the key changes. The frameStats.cpp header comment says "one TSC -> ns conversion", which is true only for blocks.
 NB RC13 is only partly met. `alignas(64)` on `g_burn_frame` and `g_burn_submit_key` (frameStats.h:2707-2708) aligns where each starts, but pads nothing after them. The linker may pack another small COMDAT global (for example `g_count_limit`) into the rest of the line. For a real private line, wrap each in `struct alignas(64) { std::atomic<uint32_t> v; }`. This is cosmetic: each is written once per flip or frame.
 NB The unit test's spread path is a copy of `BurnSpreadStep`, not the compiled function. Only `BurnSpinUntil` is shared through the header, so equivalence rests on inspection. Keep the copy byte-identical, or move the step body into an inline header helper that the unit also includes.
 NB The placebo applies `DrawAheadApplyPin(false)` (frameStats.cpp:862-864), which logs `DrawAheadPin: DrawAhead mode=...` once. Any scorer or log check that counts DrawAhead pin lines sees one extra. It is harmless, but should be disclosed.
 NB The detached placebo thread keeps calling `Add`, `Gates::Value` and, rarely, `LOGF` while static destructors run at exit. The risk is low: logging is bounded and Windows ends the process by terminating the thread. Watch the smoke for exit-time noise before trusting a code-8 seal.
 NB At `burn=0`, `BurnSubmitHook` costs an acquire load, a relaxed load and a compare per `Submit`, plus a CAS, an `Add` and a role check per key. That is slightly more than the per-site cost the frameStats.h:2688-2700 header comment documents. Adjust the comment.
 NB Code 1's burn lies outside every `gw_*` region and outside `GpuThreadProcessNs` (graphicsRun.cpp:795 comes before the scope at :798). It appears in `cpu_gpu_us` but not in `gw_proc_ns`. The RC5 locked test (`gw_idle+gw_blk+gw_flip`) is unaffected, but anything that reads `gw_proc` as GuestGpu work must add `burn_g_ns`. `m_processing` stays true during the burn, so `WaitForIdle`/`Done` waiters wait through it. The review accepted this; it is stated here for the record.
 NB Coverage for spread code 3 and for code 6 depends on the worker having work. `burn_m_seen` counts only frames in which a worker ran at least one job. Code 6 fires at the loop top after a batch, so a worker asleep in `ahead_cv` across a flip burns only after its next batch. The scorer must use the per-worker denominator from RC7.
 NOTES Verdict: the code can go to the smoke once the one blocking item is done. That item is recording the implementer's deviations in ROADMAP; it needs no code change. I reviewed read-only: I did not edit, build, run anything or commit. Only the git diff at HEAD 7f0951f was read.

Behaviour at 0: nothing spins, logs or starts a thread; the only per-flip cost is the release store in videoOut.cpp:1200.
- Per hook call the cost is one acquire load and one thread-local compare. Spread sites add one thread-local bool load.
- Per new key, each site makes one cold `BurnNewFrame`: a seen-counter `Add` plus one relaxed `Gates::Value` in `BurnDecode`, which returns at value 0 before any other work (frameStats.cpp:735-738).
- `BurnSubmitHook` adds a CAS per key.
- The placebo starts only from the GuestGpu site after code 8 decodes (frameStats.cpp:913-947 into :870-876), and only once.

Each site is on the stated thread and outside the stated locks:
- **Code 1** (graphicsRun.cpp:795): after the `m_queue_mutex` scope closes at :766, before the `Process` scope at :798. No render mutex is held.
- **Code 7** (graphicsRun.cpp:197-198): before `GpuMutexLock(m_submission_mutex)` at :199. The only caller, agc.cpp:4211 `submit_dcb`, holds no lock. `SubmitCompute` and `SubmitFlipPreparation` are not hooked.
- **Codes 2/5** (commandRecorder.cpp:1032): inside `if (m_gpu)`, with no mutex held, before `Execute`.
- **Code 6** (pipelineCache.cpp:3025-3028): `index == 0`, before the `ahead_mutex` scope.
- **Code 3** (pipelineCache.cpp:3064): after the mutex scope, before `AheadRun`, so the slot is still `AheadQueued`.
- **Code 4** (eventQueue.cpp:443-445): success path only, blocking waits only; only the owner pin is held. The role is checked in `BurnNewFrame`.

Firing once per frame, and the tear rule:
- The key is `flip_status.count`, incremented at videoOut.cpp:1194 and published with release after `Gates::Poll` at :1197. It is read with acquire, and the knob is read relaxed afterwards, so the Poll value is visible.
- Each site on each thread decodes the knob exactly once per new key. Spread frames derive budget and quantum from that single read, including the `dathreads` read.
- Code 7 takes the frame through a monotone CAS on `g_burn_submit_key`, so exactly one submitter per key.
- M1 worker 0 has two sites with separate keys and separate codes, so they cannot interfere. The spread thread-local state is reset only by spread sites.

Deadlock, reordering and guest-visible semantics: I found no lock held around any burn and no change to PM4, record, M1 queue or submission order. At code 4 the burn runs after events are dequeued; at code 7 it runs before the submission is built.

The spin, `BurnSpinUntil` (frameStats.h:2718-2726):
- It is `[[gnu::noinline]]` and uses `__builtin_ia32_rdtsc` and `__builtin_ia32_pause`. Both have side effects, so the loop cannot be folded; it touches registers only.
- The target is `dose * TscCyclesPerNs()`, the same static constant `NowNs` uses (frameStats.cpp:143-156, :203).
- A block counts the wall from before the first QTCT to after the second, so it includes both QTCT calls and the dose is not undercounted.
- The unit output shows blocks within +0.03 % mean against QPC.

Counters:
- 32 new enum entries after `Tm8ProbeN` (frameStats.h:2178-2210), in the same order as the named rows after `tm8_pb_n` (videoOut.cpp:2777-2808), all with `micros=false`.
- They sit above `LogNs`, so `fslean` zeros them as designed.
- The CPU cross-check follows RC3 in design122's weakened form (diagnostic, not a gate): block codes read QTCT around every spin, spread codes 1 in 64.

Table order:
- `Knob::Burn` comes after `TexMemo8`, with the LAST comment moved (gates.h:643-652).
- The row `{"KYTY_BURN","burn",0,899999}` comes after `texmemo8` (gates.cpp:423-427). I checked this by reading; I did not rerun `check_gate_order`.

Decoding and rejection:
- The environment value and `ApplyText` both parse with `strtoul` and clamp to 899 999. That clamped value is code 8 with dose 99 999, which is rejected.
- Code 0 (for example `burn=2000`), dose 0 (for example 100000) and doses above 20 000 are all rejected, with at most 8 log lines.
- If the TSC is not calibrated, the knob refuses once with a log line.

RC1, RC7, RC9 and RC13 are present in the code. RC4-RC6, RC8, RC11 and RC12 are scorer or protocol items and were not reviewed here.

Relevant paths: C:/kyty/KytyPS5/src/common/frameStats.h, C:/kyty/KytyPS5/src/common/frameStats.cpp, C:/kyty/KytyPS5/src/common/gates.h, C:/kyty/KytyPS5/src/common/gates.cpp, C:/kyty/KytyPS5/src/graphics/guest_gpu/graphicsRun.cpp, C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/commandRecorder.cpp, C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp, C:/kyty/KytyPS5/src/graphics/presentation/videoOut.cpp, C:/kyty/KytyPS5/src/kernel/eventQueue.cpp, C:/kyty/s122/unit/run_burn_unit.out.
#### FIX
1 blocking finding FIXED, 5 cheap non-blocking ones applied, the other 4 recorded in ROADMAP item 3. `check_gate_order.py` exits 0 and the build is clean. Nothing committed; the game was not run; no background processes left.

**Blocking finding (ROADMAP s122 decisions (a)-(f)): FIXED.** ROADMAP s122 now has item 3 (lead as author, recorded before the smoke), inserted after item 2. All of (a)-(f) are marked accepted:
- (a) Code 7 fires after the `draw_commands.empty()` early return, and the hook still sits before `m_submission_mutex`.
- (b) The frame key is kept per site on each thread (`t_burn_key[BurnSite::Count]`).
- (c) The scorer reads code-7 coverage from `burn_s_seen`, with `burn_s_main` as the role count, and the code-7 dose from `burn_t_*`. This replaces RC1's literal "`burn_t_seen` from that site".
- (d) The spread dose includes a per-step estimated rdtsc-gap term of about 7 ns. Offline check against QPC:
  - before the rounding fix: −0.01 … +0.36 % of the 2000 µs budget;
  - after it: counted exactly 2000.0 µs, QPC wall −0.16 … +0.59 % (other load was running on the machine).
- (e) New `burn_*_cpu_w` and `burn_cpu_bad` counters. The scorer compares the spread cpu/wall ratio with a baseline of about 1.33, not 1.0.
- (f) The placebo thread lives for the rest of the process: absent in the first A block, present in every later block. It adds one extra `DrawAheadPin` log line, and it keeps running during process exit.

Script: `C:/kyty/s122/patches/patch_burn_review2.py` (`PART=roadmap`), text in `C:/kyty/s122/patches/roadmap_item3.md`.

**Non-blocking findings:**
1. **Spread cpu/wall biased high: recorded, no code change.** A code fix would push the ratio below 0.9 instead. The ~1.33 baseline is in ROADMAP (e) and in the `frameStats.cpp` comment. The new unit runs gave 1.32–1.39, plus one outlier of 16.8 (an interrupt charged to the thread during a `QueryThreadCycleTime` call).
2. **Per-step truncation: FIXED.** Each spread step now carries the sub-nanosecond remainder to the next step (`t_burn_frac`, reset when a spread frame is armed). The same change is in the unit test's copy of the step. The unit test was rebuilt and run twice (ALL OK), and the output was appended to `run_burn_unit.out`. That file also holds one run I started by mistake on the old exe; it is labelled as such.
3. **RC13 cache lines: FIXED.** `g_burn_frame` and `g_burn_submit_key` are now `struct alignas(64) BurnLine { std::atomic<uint32_t> v; }` with a `static_assert(sizeof == 64)`. All 10 uses were changed to `.v`.
4. **Unit test uses a copy of the step: kept identical.** The copy was updated with the same statements as the real function. Documented in item 3.
5. **Placebo `DrawAheadPin` log line: disclosed** in (f).
6. **Placebo thread at exit: disclosed** in (f). Check the smoke for exit-time log noise before trusting a code-8 result.
7. **`burn=0` cost comment: FIXED.** The `frameStats.h` header comment now lists the Submit hook's cost.
8. **Code 1 outside `gw_proc`, `m_processing` held during the burn: recorded** in item 3.
9. **Code 3 and code 6 coverage depends on worker work: recorded** in item 3 (the scorer uses the per-worker denominator, RC7).

Patch scripts: `C:/kyty/s122/patches/patch_burn_review2.py` (`PART=code`) and `patch_burn_review2b.py` (comment reflow only).

**Build tail** (`C:/kyty/s122/patches/build_burn3.log`):
```
-- Installing: C:\kyty\build\install/kyty_emulator.exe
-- Up-to-date: C:\kyty\build\install/libwinpthread-1.dll
BUILD OK: C:\kyty\build\install\kyty_emulator.exe
```
No warnings come from burn code. The ones left are old `getenv` deprecation warnings and old `-Wreturn-type` warnings (`pipelineCache.cpp:373`, `imageView.cpp`, `shaderResourceBarrier.cpp`).

**sha256 of `C:/kyty/build/install/kyty_emulator.exe`:** `cc6f256be6b780c71827004f8fc1ad5ecb851670ecda4ebea70627c984442a40`. It has not been copied into the emulator folder.

Files changed:
- `C:/kyty/KytyPS5/src/common/frameStats.h`
- `C:/kyty/KytyPS5/src/common/frameStats.cpp`
- `C:/kyty/KytyPS5/docs/ROADMAP.md`
- `C:/kyty/s122/unit/burn_unit.cpp`
- `C:/kyty/s122/unit/run_burn_unit.out`
