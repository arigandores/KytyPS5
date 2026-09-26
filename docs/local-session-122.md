# Session 122 — PAUSED by the user: the bottleneck-map instrument (knob `burn`) is designed, implemented and code-reviewed but not yet smoke-tested; no sealed run; the vblank staircase found; the frame-skip plan recorded

**Single source of truth for session 122 (paused).** Mirrored into git as `docs/local-session-122.md`. Harness root
`C:/kyty/s122`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–5.

**Numbers:** installed build `d3a981a2…` (git `7c73f26`) — unchanged; the `burn` build is committed as WIP and not
installed. Sky Garden ≈ 51–52 % game speed. 60 FPS is not promised.

## 1. What was done

1. **Order (item 1):** the scene map through causal probes — a per-thread calibrated CPU burn, a two-dose ABBA per scene.
2. **Design (item 2):** designer + adversarial reviewer (ACCEPT WITH REQUIRED CHANGES, RC1–RC13) → `design122.md`. Knob
   `burn` = thread code × 100 000 + dose µs (1 GuestGpu before `Process`; 2/3 record thread / all M1 workers, spread;
   4 main guest thread at the return of `KernelWaitEqueue`; 5/6 controls; 7 fallback at `GuestGpu::Submit` before its
   mutex; 8 placebo). Scenes from `data/prein/product_levels.xml`: Sky Garden, `intro_next`, `penguin_atlantis`,
   `time_stopper_ghost_world`, `rotating_level_day_and_night` (+ fallbacks). Reading rule: slope of mean `dt` over the
   dose — critical / not critical / superlinear / unresolved / GPU-bound, with the vblank steps reported.
3. **The vblank staircase (the lead's finding, item 2):** in `shp121` 93.4 % of Sky Garden frames take exactly 2 vblanks
   (33.3 ms; median `dt` 33 300 µs); the game steps a fixed 1/60 s per frame, so savings below the distance to the next
   vblank step do not change `dt` — why small GuestGpu wins have not shown in FPS. **Plan:** session 123 — frame skipping
   (execute each frame's command stream for everything the guest reads back, skip the draw translation of every other
   frame; game speed toward ~100 % at ~30 shown FPS), if the map shows GuestGpu critical; a flip-pacing knob as the
   second lever; frame generation (Lossless Scaling, driver-level) as a user-side check afterwards.
4. **Code (items 3–4):** implementation agent, adversarial code reviewer (PASS_WITH_FIXES), fixer. 32 `burn_*`
   counters; the spin `BurnSpinUntil` (`rdtsc` + `pause`, calibrated on `NowNs`'s constant; offline against QPC: blocks
   +0.02…+0.08 %, spread dose counted exactly 2 000.0 µs). The implementation's own decisions were written as item 3 by
   the fixer agent in the lead's name and accepted explicitly in item 4. Build from the working tree `cc6f256b…`
   (not installed, not run).
5. **Paused (item 5)** at the user's instruction ("finish the current run, update all docs, push and stop").

## 2. Code

WIP commit (see git): `frameStats.h/.cpp` (spin, hooks, counters), `gates.h/.cpp` (`Knob::Burn`, LAST),
`graphicsRun.cpp` (codes 1, 7), `commandRecorder.cpp` (2, 5), `pipelineCache.cpp` (3, 6), `eventQueue.cpp` (4),
`videoOut.cpp` (key publication, counters). Default 0: behaviour unchanged. NOT smoke-tested.

## 3. Resume

`docs/next-session-122.md` §«Возобновление»: build from the WIP commit, pin, the burn smoke on Sky Garden (6 arms), the
entry smokes of the new levels, the scorer with fixtures and mutants, the seal, the sealed ABBAs per scene; chain
`C:/kyty/s122/go122a.sh` (build sha placeholders to fill).
