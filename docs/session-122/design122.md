# Session 122 — the bottleneck map across scenes: knob `burn` (per-thread calibrated CPU burn), scenes, reading rule

Lead's synthesis of `burn.md` (design) and `burn_review.md` (adversarial review: ACCEPT WITH REQUIRED CHANGES), written
before any code; both in `C:/kyty/s122/design/` (git `docs/session-122/design/`). **The instrument = the design with every
REQUIRED change RC1–RC5 and the smaller RC6–RC13 of the review; where this file differs, it wins.**

## 1. The knob

- `Knob::Burn` LAST (after `TexMemo8`), row `{"KYTY_BURN", "burn", 0, 899999}` after `texmemo8`; `check_gate_order.py`
  before the build. Value = thread code × 100 000 + dose µs (dose ≤ 20 000, else rejected and logged). MEASUREMENT ONLY;
  at 0 nothing spins, logs or starts a thread.
- Codes (accepted, including the design's [AMEND] items, recorded here as the lead's decisions): 1 GuestGpu once per frame
  just before `Process` in `ThreadRun` (outside every lock — "before `Process`" replaces item 1's "inside"); 2 the record
  thread, spread over the frame's records; 3 all M1 workers, spread (replaces item 1's "one worker"); 4 the main guest
  thread once per frame at the return of a blocking `KernelWaitEqueue`; 5 record thread once per frame (control);
  6 M1 worker 0 once per frame (control); 7 fallback for 4 — **RC1: at the entry of `GuestGpu::Submit` BEFORE
  `m_submission_mutex`, on the first graphics submit after the frame key changes, the submitter's role counted**;
  8 a placebo thread (the side effect of a spinning core).
- Frame key: the flip counter published after `Gates::Poll`; each thread reads the knob once per new key. The spin: a
  register-only `rdtsc` + `_mm_pause` loop against `NowNs`'s constant, no lock, no memory. **RC3:** each spin also timed
  by `QueryThreadCycleTime` (`burn_*_cpu_ns`) — the thread-CPU cross-check is a printed diagnostic, not a gate.
  Counters `burn_{g,r,m,t,p}_ns/_n/_cpu_ns`, `burn_r_q`/`burn_m_q`, `burn_*_seen`, `burn_late`, the role counter —
  raw, `micros=false`, after `tm8_pb_n`.

## 2. Scenes (from `data/prein/product_levels.xml`, entry `KYTY_GUEST_ARGS -lvl <name>`)

Anchor `underwater_aerial_garden` (Sky Garden); `intro_next` (desert); heavy candidates in smoke order:
`penguin_atlantis` (Atlantis), `time_stopper_ghost_world` (Horror Time; memory risk → `mini_giants_garden`),
`rotating_level_day_and_night` (Day and Night; guest-CPU candidate → `hub_crashsite`); alternates `hoover_beach`,
`ice_iceberg`. Every new level gets an unsealed entry smoke first (disclosed; stable-draws 300, timeout 480, the first
attempt a warm-up, video to tell gameplay from the fly-over).

## 3. Runs and the reading rule

- Per scene ONE sealed ABBA `burn=0 | burn=102000` (GuestGpu, 2 000 µs), 300 s, pinned; on the anchor also main guest
  thread `burn=0 | burn=402000` and the placebo `burn=0 | burn=802000` (the control runs of codes 2/3/5/6 only if time
  allows — each is its own recorded decision).
- Slope s = Δ(mean `dt_us`) / measured dose (mean, not median: frames drift across the 16.7/33.3 ms grid), 2SE by pairs.
- **RC4 classes:** critical (s − 2SE > 0.5 and the interval reaches 1); not critical (s + 2SE < 0.3); **superlinear**
  (s − 2SE > 1: the dose pushed frames across a vblank step); **unresolved** (the interval spans 0.3–0.5 or both 0 and 1 —
  recorded, a rerun only by a new decision); GPU-bound (median `gpu_busy/dt` ≥ 0.9 and the GuestGpu class "not critical").
- **RC5 vblank:** a scene is "locked" when ≥ 80 % of frames sit at one vblank multiple; in a locked scene the reading
  uses the fraction of frames per vblank step beside the mean, and the dose is chosen to exceed the slack to the next step
  (measured in the smoke); the slack correction uses the thread's own idle measure, reported only.
- Consequences fixed before the runs: as ROADMAP s122 item 1.

## 4. The vblank staircase (the lead's finding, recorded as the reason for the session order)

In `shp121` (s121, Sky Garden, 8 868 frames): 93.4 % of frames take ≈ 2 vblanks (33.3 ms), 4.4 % one, 2.1 % three; median
`dt` exactly 33 300 µs; `cpu_gpu_us` clusters at 30.7–33.6 ms. The game advances a fixed 1/60 s per frame (session 10),
so game speed = 16 667 / `dt`. A saving below the distance to the next vblank step does not change `dt` — the reason
small GuestGpu savings have not shown in FPS. **Plan (lead's decision):** session 123 — frame skipping (process each
frame's command stream for everything the guest reads back — labels, fences, EOP, compute read by the CPU — but skip the
draw translation of every other frame; game speed toward ~100 % at ~30 shown FPS) — designed only if this session's map
shows GuestGpu critical in the anchor; a vblank-pacing knob (complete a flip when ready instead of at the next 60 Hz
boundary) is analysed in the same design as the second lever. Frame generation (Lossless Scaling, driver-level) is a
user-side check after frame skipping works.
