# Session 122 — adversarial review of `design/burn.md` (knob `burn`, reading rule, scenes)

Reviewer scope: read-only on `C:/kyty/KytyPS5` (HEAD `2f1ca04`), the game data and `C:/kyty/s121/log_shp121.txt`. No source edit, no
build, no game run, no commit. Line numbers are of HEAD.

## Verdict

**ACCEPT WITH REQUIRED CHANGES.** The core idea holds: pure-CPU spins at lock-free sites on GuestGpu, the record thread and M1,
ABBA on the mean `dt`, measured dose. The anchor reading (Sky Garden, code 1, 0 | 2 000 µs, 40 pairs) is statistically sound.
Five defects must be fixed before the ROADMAP line and the seal:

- **RC1:** the fallback site (code 7) runs under a guest-submission mutex.
- **RC2:** three unmarked deviations from the recorded ROADMAP item.
- **RC3:** the "independent clock" fixture depends on the result it is meant to check.
- **RC4:** the class table has gaps, and its "contains 1" test fails the design's own prediction.
- **RC5:** vblank quantization is handled only for the 60 Hz cap, and the slack correction's denominator is unreliable.

RC6–RC13 are smaller.

---

## 1. File:line claims — checked

| claim | result |
|---|---|
| `gates.h:642-644` `TexMemo8` last before `Count`, "LAST row" comment at :642 | **OK** |
| `gates.cpp:420-423` texmemo8 last `KNOB_DEFINITIONS` row; clamp `wanted < limit ? wanted : limit` in `Initialize`/`ApplyText` | **OK** (:446-453, :598-600). A value ≥ 900 000 clamps to 899 999, which is code 8 with dose 99 999, so it is rejected. That is fine. |
| `graphicsRun.cpp:790-791` code 1 site: after `EXIT_IF(!has_submission)`, before the `process_scope` block; `Process` at :799 | **OK.** Outside `m_queue_mutex` (its scope closes at :765) and outside the render mutex. `m_processing` is already `true`, so a `WaitForIdle` waiter such as `GuestGpu::Done` (:323-327, which holds `m_submission_mutex` while it waits) also waits through the burn. A longer `Process` would have the same effect, so this is acceptable, but state it. Each slice ends with `BufferFlush` (:1021, :1056), so no lazily coalesced work sits unsubmitted during a burn at slice start. |
| `commandRecorder.cpp:1031-1035` code 2/5 site; `m_gpu` at :118; `Drain` at :520 | **OK.** No mutex is held there. `log_shp121` shows exactly one `gpu=1` recorder. Note that the GuestGpu thread drains the recorder from the direct-write path (`commandScheduler.cpp:749`, `rec_direct` ≈ 783 per frame, of which `rec_direct_busy` ≈ 23 find a backlog), not only at buffer ends. That supports the design's "spread, not block" argument. |
| `pipelineCache.cpp:3057-3058` code 3 site (before `AheadRun`), `3024-3025` code 6 | **OK.** Outside `ahead_mutex` (3028-3045). The slot is still `AheadQueued` (the CAS to `AheadRunning` happens inside `AheadRun`), so a burn delays the job exactly like slower M1 work. |
| `eventQueue.cpp:440` code 4 site | **OK.** Only the `KernelEqueueRef owner` pin is held, which is a reference and not a lock. |
| `graphicsRun.cpp:654-657` code 7 "before `m_queue_mutex`, no lock" | **WRONG — see RC1.** |
| `videoOut.cpp:1197` `Gates::Poll` in `FlipQueue::Flip` on the present thread (`PresentThread`, :805) | **OK.** The store goes after `Poll`, under `FlipQueue::m_mutex` (locked at :1187). That is harmless. |
| `runtimeLinker.cpp:1512` Main role | **OK** |
| `frameStats.h:2177` `Tm8ProbeN` last counter; `videoOut.cpp:2774` `tm8_pb_n` last named row | **OK** |
| `TscCyclesPerNs` `frameStats.cpp:142-155`, `NowNs` :198-212 | **OK** (a 20 ms QPC calibration, the same constant). `dt_us` comes from `NowNs` on the present thread, so the burn units match `dt` units. |
| "`rec_work_us` … all live in lite" (§2.5) | **WRONG.** `RecordWorkNs` is timed under `TimingsEnabled()` (`commandRecorder.cpp:1034`) and reads `rec_work_us=0` in `log_shp121` (lite). `semwait_us` is live (25 586 µs per frame). |
| "neither `underwater_aerial_garden` nor any other level name is a string of `eboot.bin`" | **Partly wrong.** `intro_next` occurs once in `eboot.bin`. `underwater_aerial_garden` and `penguin_atlantis` occur 0 times. The conclusion (resolve against `product_levels.xml`) still holds. |
| "the five call sites" (§1.6) | There are six hook sites (1, 2/5, 3, 6, 4, 7) plus the key store. Cosmetic. |

## 2. Required changes

### RC1 — code 7 is not lock-free (BLOCKER for code 7)

`GuestGpu::Enqueue` is called only from `Submit` (:196-206), `SubmitCompute` (:209-220) and `SubmitFlipPreparation` (:223-232). Each
of them takes `GpuMutexLock lock(m_submission_mutex)` **before** calling `Enqueue`. A burn at `Enqueue` entry therefore holds the
guest-submission mutex, and every other guest thread that submits (compute queues, `VideoOutSubmitFlip` → `SubmitFlipPreparation`,
`Done`) is serialised behind it. That is not "pure CPU on that thread".

In addition, the `Main` role check may never fire: nothing shows that the main guest thread is the one that submits.

**Fix:**
- Move the fallback to the entry of `GuestGpu::Submit`, before the `GpuMutexLock` (:196). Fire it for "the first graphics `Submit`
  after the key change", on any guest thread.
- Count the submitter's role in a new counter (or add `burn_t_role`).
- Take `burn_t_seen` from that site.
- Record the site in ROADMAP before use (the design already requires this for code 7).

### RC2 — unmarked deviations from ROADMAP s122 item 1

The recorded text is "GuestGpu **внутри `Process`**, … **воркер M1** …". The plan's run list is "ABBA двух доз на сцену (прожиг
GuestGpu 0 | N мкс; на опорной сцене — ещё главный поток гостя)". The design deviates in three places:

- **(a)** Code 1 sits **before** `Process`, not inside it. This is the better site: no render mutex, one burn per slice start. It
  still needs a ROADMAP line saying so, before code.
- **(b)** The M1 probe is the pool-wide spread (code 3), not one worker. The argument is sound. Mark it [AMEND].
- **(c)** Sealed runs of codes 2, 3, 5, 6 and 8 on the anchor go beyond the recorded run plan. Only code 8 is marked [AMEND].
  Either mark all of them [AMEND] with their own ROADMAP line, or keep them as unsealed smokes.

Also, the ROADMAP names the design file `docs/session-122/design122.md`. Copy the file there, or name this path in the ROADMAP line.

### RC3 — fixture 5 ("independent clock") depends on the result

On a thread that is busy nearly the whole frame, `cpu_X ≤ dt`. For GuestGpu on Sky Garden, `dt − cpu_gpu` is 665 µs (block
window means 381–1 254 µs in `log_shp121`). So `Δcpu_gpu ≲ Δdt + 0.67 ms`. At N = 2 000 with a true slope s ≤ 0.6,
`Δcpu_gpu` ≤ 1 870 µs, which is outside ±15 % of N̄, and the run is NOT_ADMITTED **exactly when the answer is "partial" or
"absorbed"**. The same happens when the burn replaces spin-waits.

**Fix:** verify the burn itself, not the frame:
- For block codes, read `QueryThreadCycleTime` just before and after each spin and publish it as `burn_{g,r,m,t,p}_cpu_ns`. This is
  the s99 `bf_burn_cpu_ns` idiom.
- Admission: `burn_*_cpu_ns ≥ 0.9 · burn_*_ns` over the B-block window (the spin was on-CPU and not preempted).
- For spread codes, sample one spin in 64.
- `Δcpu_X(B − A)` becomes a printed diagnostic, never a gate.

### RC4 — classification: missing classes, and "contains 1" is too strict

**(a) Missing classes.** Every outcome must map to exactly one class:
- **unresolved:** the 2SE interval contains both 0 and 1, or `2SE_s > 0.35`. Classify as NOT_EVALUABLE for that thread. No
  consequence follows; the dose is raised or the pairs extended only through a new ROADMAP line.
- **superlinear:** `s − 2SE_s > 1`. This happens when the dose crosses a vblank step in a locked regime (RC5) or through coupling
  such as `Drain`. It is never read as "critical 1:1".
- **negative:** `s + 2SE_s < 0`. This is an artefact such as power or scheduling; see the placebo.

"≈ 0" must be defined as "contains 0 and excludes 1". The GPU-bound condition "code-1 s contains 0" is vacuous when the interval
is wide, so it must also exclude 1.

**(b) The "contains 1" test fails the design's own prediction.** With 2SE_s ≈ ±0.06–0.08 at the anchor, the ROADMAP test "contains 1
and not 0" becomes a test for s = 1 exactly. The design itself predicts GuestGpu s ∈ [0.67, 1.0]. A true s = 0.85 (15 % absorbed
into spin-waits or slack) reads [0.77, 0.93] and lands in "partial". The consequence rules would then open no GuestGpu track,
although GuestGpu is plainly the dominant thread.

**Fix:** pre-register, by a new ROADMAP line (the rule is already recorded, so this is an amendment, lead as author):
- **critical-dominant:** `s − 2SE ≥ 0.67` and not superlinear. Consequences as for "critical".
- The strict "contains 1" is kept and printed beside it.

**(c) Evaluability for new scenes.** The noise (per-pair sd 400–512 µs, from my recount and s121) is from Sky Garden with Astro
standing still. Unknown levels may drift more. The `2SE_s ≤ 0.35` evaluability limit above is required per scene and thread.

### RC5 — vblank quantization: correct the model, generalise the lock test, fix the slack correction

**What holds (quantified on `log_shp121`, 7 936 armed flips, 88 blocks):**
- The present thread flips only on vblanks (`PresentThread` :805-878), so single-frame `dt` sits on the 16.7 ms grid. The window
  mean still telescopes: `Σ dt` over frames 10–88 = (time of flip 88 − time of flip 9), so the quantization error of a block mean
  is only the phase of its two end flips. That is at most V/79 = 211 µs, with sd ≈ V/(79·√6) ≈ 86 µs per block and ≈ 122 µs per
  pair, already inside the measured 400–512 µs pair sd.
- `dt` has lag-1 autocorrelation −0.18: short frames compensate long ones. This is the "drift" regime the design describes, and
  the GuestGpu CPU fills 98 % of every interval (`dt < cpu_gpu` in only 0.44 % of flips).
- In this regime a burn is linear across the 2V = 33.3 ms step (W 31.8 → 33.8 ms). **The anchor reading at 0 | 2 000 is sound.**

**What does not hold:** the design treats a dead zone only as a 60 Hz cap ("mean dt ≤ 17.2 ms, ≥ 90 % at one vblank"). A dead
zone arises whenever the loop containing the probed thread waits on a vblank-aligned event: WAIT_FLIP_DONE, `FlipQueue::Wait`
(`gw_flip_ns`), a guest flip wait, or `flip_rate > 0`. Then `dt = k·V` for **any** k, and a critical thread reads s = 0 for
N < headroom h = k·V − L. Past h it jumps by V, smoothed by jitter, giving a local slope that can be ≫ 1.

The histogram test cannot tell the two regimes apart near a step. In drift with W = 32.5 ms, only (2V − W)/V ≈ 5 % of frames are
1V, so ≥ 90 % sit at 2V, and a "≥ 90 % at one vblank" rule for k = 2 would call it locked.

**Fix:**
1. **Regime test per scene from the smoke (and arm A of the seal), for any k.** Call a scene *locked* when the probed thread's
   blocking wall waits per frame ≥ 0.25·N. For GuestGpu that is `gw_idle_ns + gw_blk_ns + gw_flip_ns` (lite, `KYTY_GPU_WALL=1`).
   For the main thread there is no wall instrument, so use `dt − cpu_main` as an upper bound. Otherwise call it *drifting*.
   Also print the lag-1 autocorrelation of `dt` and the 1V/2V/3V shares (negative ACF with a mixed histogram means drift).
2. **Locked scenes: two non-zero doses.** Run ABBA `burn=N1 | burn=N2` with N1 ≥ h_upper + 1 000 µs and N2 = N1 + 2 000 µs. Read
   `s = Δ/(N̄2 − N̄1)`. This is literally "ABBA двух доз"; it cancels the headroom instead of estimating it, and it keeps both arms
   in the same (drift) regime. Keep N2 − N1 < V so that one arm cannot cross two steps. N2 ≤ 20 000 fits the knob.
3. **Drop `s_x` as a classifier.** Keep it only as a diagnostic. Its denominator `N − slack_A` uses `dt − cpu_X`, which is **not** a
   lower bound of absorbable slack as §2.2 claims: it contains involuntary preemption and ready-queue time (not absorbable) and
   misses spin-waits (absorbable). At N − slack ≈ 2 000 µs, a ±0.5 ms error in slack moves `s_x` by ±25 %. If kept at all, use the
   GuestGpu wall waits (item 1) and propagate their 2SE.
4. The vsync-capped class becomes "locked at k" for any k, read through item 2.

### RC6 — "savings convert 1:1" is a one-sided derivative

A burn measures d(dt)/d(+work). A saving of S converts 1:1 only while no other constraint takes over. The table must print a
**saving headroom** per scene: the minimum over the other constraints of their measured slack. That means the GPU (`dt − gpu_busy`),
the main thread (`dt − cpu_main`), the record thread (`rec_spin_gpu_us`) and M1 idle (from `da_work_us` / 4 threads). In drift the
next vblank floor also applies: dt ≥ V. The consequence text should read "a saving on X converts ≈ 1:1 up to that headroom."

### RC7 — fixture 4 and coverage: define the frames and the per-worker count

- "A blocks: every `burn_*_ns` exactly 0" must apply to **window frames 10–88**. The tear frame at position 0 or 89 can legally
  carry a burn, and would otherwise make a valid run NOT_ADMITTED.
- `burn_m_seen` for code 3 is counted per worker. Define admission as `burn_m_seen / (frame · dathreads) ≥ 0.95`, or as
  "≥ 0.95 frames with at least one worker seeing the key". State which.
- A burn in interval F shows in `dt` 1–3 flips later: GuestGpu works a frame ahead, and the main thread may be two ahead.
  Window 10–88 covers this; say so in §1.3.

### RC8 — new-scene protocol: schedule start, run length, cold translation

- **Run length:** 40 pairs × 180 frames = 7 200 frames is not "short" at the FPS of a heavy level (≈ 8–12 min at 10–15 FPS). Set
  `--hold` and the pair count from the smoke FPS, capped by a pre-registered wall budget.
- **Schedule start:** `90+<start>` is a fixed frame number, but time-to-stable varies per level. Set `<start>` from the smoke's
  stable frame plus ≥ 600 frames. The scorer drops blocks that begin before the `stable` frame recorded in `<tag>.json`.
- **Fatal markers:** in new levels, content streamed later compiles new shaders or pipelines mid-run. Add to the fatal or
  NOT_ADMITTED markers any `CsStall:` or new-translation line inside the measured range, next to `AsyncPipelines: skipped draw`.
  Run the seal only after a warm smoke on the same build; the translation-cache signature is unchanged, since no `shader/**` file
  is touched.

### RC9 — placebo thread (code 8)

- Create it `detach()`ed, or leaked and never joinable. A joinable `std::thread` destroyed at exit calls `std::terminate`, which
  prints `--- std::terminate ---`, one of this scorer's own fatal markers.
- Pin it to the same CCD mask as GuestGpu and M1 (`dapin`). Unpinned, the result depends on where Windows puts it, so it does not
  measure the SMT/power effect it is meant to.
- It stays [AMEND].

### RC10 — lite field list and text corrections

- Remove `rec_work_us` from the live-in-lite list (§2.5): it reads 0.
- Correct the `eboot.bin` sentence about `intro_next` (§3).

### RC11 — `cpu_record_us` may be the wrong recorder

Both recorders call `RegisterCurrentThread(ThreadRole::Record)` (`commandRecorder.cpp:955`), and the handle is replaced by the
last caller (`frameStats.cpp:236-240`). The GPU recorder is created lazily, so it is probably the last, but this is not guaranteed.
Either check the startup order from the log in the smoke, or do not use `cpu_record_us` for code 2/5 at all (RC3 makes that
possible).

### RC12 — the pacer and speed clamp at block edges (diagnostic)

- `pace_ema_us` settles with α = 0.08 (`videoOut.cpp:1216`), a time constant of ≈ 12 frames. At window frame 10 about 45 % of the
  speed step is still settling. Print the 30–88 mean beside the 10–88 estimator as a diagnostic only; the window rule is not
  changed.
- On locked 60 Hz scenes, `speed > 0.97 → 1.0` (`videoOut.cpp:1218`) is a nonlinearity. Arm A runs unscaled guest time and arm B
  runs scaled. Guard with Δdraws and the DRS step (already present) and report it.

### RC13 — minor

- Give `g_burn_frame` its own cache line (`alignas(64)`) rather than sitting "next to `g_count_limit`", which every `Add` reads.
  It is written once per flip, so this is cosmetic.
- The self-test (1 ms spin) runs on the first-arming thread at block position 0. That is outside the window; say so.

## 3. Items that hold as designed

- **The spin.** `[[gnu::noinline]]` plus `__rdtsc` (a volatile intrinsic) with `_mm_pause` cannot be removed or folded by the
  compiler. It is register-only, lock-free, and calibrated by the same constant as `NowNs`. Overshoot is at most one pause plus one
  `rdtsc`. Preemption is counted (`BurnLate`) and made visible by RC3.
- **Deadlock.** None found at sites 1, 2/5, 3, 6 and 4. No site holds an emulator lock that the present thread, GuestGpu or the
  submitters need, except code 7 (RC1). The record-thread block (code 5) delays GuestGpu through `Drain`, and possibly through
  present-side `DrainAsyncSubmits` (`commandScheduler.cpp:195-200`, rare). That is a delay, not a deadlock, and the design reads
  code 5 only as a control.
- **Order.** No site reorders PM4, records, M1 queue policy, submissions or guest-visible values. The burn only adds wall time.
- **Main-thread hook (code 4), guest-visible timing.** The burn runs after `WaitForEvents` has returned and dequeued the events.
  Event contents, including flip `processTime` counters, are unchanged, and no emulator state is touched. The guest sees a longer
  syscall, the same as longer guest code. The pacer and audio-sync effects are those of any slowdown (RC12). What remains open is
  coverage and position (R7): the "64 % asleep waiting for the flip" figure comes from the session-12 **cutscene** sampler, not
  from Sky Garden, and does not name `sceKernelWaitEqueue`. The smoke's `burn_t_seen` settles coverage. The slope is valid
  wherever in the frame the burn lands.
- **Tear rule.** The acquire/release pairing on the key after `Poll`, with the knob read once per key, leaves one possible tear
  frame at each block edge. Window 10–88 excludes it.
- **Statistics at the anchor.** In s121 `2SE_Δ` = 154.3 µs at 44 pairs, so ≈ 162 µs at 40 pairs. My independent recount of
  `log_shp121` with adjacent block pairs gives a per-pair sd of 399 µs, or 2SE ≈ 126 µs at 40 pairs. At N = 2 000,
  `2SE_s` ≈ 0.06–0.08, so 0 and 1 are 12–16 SE apart. The dose is ≈ 6 % of the frame and gives
  W = 31.8 → 33.8 ms, which is linear in the drift regime (RC5).
- **Level names are real.** All nine are `<File>` entries of `data/prein/product_levels.xml`, each with
  `data/prein/levels/<name>/level.lvx` present:

  | level | gfx (decimal MB, files) | pfx (decimal MB, files) |
  |---|---:|---:|
  | `underwater_aerial_garden` ("G1 - Aerial Garden") | 13.0 / 23 | 6.5 / 13 |
  | `intro_next` ("Intro") | 1.2 / 4 | — |
  | `penguin_atlantis` ("G4 - Atlantis") | 943.9 / 176 | 326.4 / 162 |
  | `time_stopper_ghost_world` ("G4 - Horror Time") | 4 015.8 / 114 | 1 192.5 / 107 |
  | `rotating_level_day_and_night` ("G5 - Day and Night") | 72.2 / 44 | 184.0 / 92 |
  | `hub_crashsite` | 191.2 / 63 | 104.4 / 46 |
  | `hoover_beach` | 174.5 / 23 | 62.9 / 11 |
  | `mini_giants_garden` | 143.9 / 85 | 83.0 / 77 |
  | `ice_iceberg` | 104.5 / 16 | 37.9 / 7 |

  The design's figures are MiB; they agree. `enter_scene.py` supports `--level`, `--stable-draws`, `--timeout`, `--attempts`,
  `--hold` and `--rec` as used.
- **Not proven: that the new levels can be entered.** No new level has been entered in this emulator, so that part rests on the
  smoke, as the design says. On-disk geometry size is weak evidence of per-frame GPU or CPU load; only the smoke counters classify
  a scene.
