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

(Sections 4-7 of C:/kyty/s122/FACTS.md are not yet mirrored here; the lead mirrors them scrubbed at the session close.)

## 8. Step 3b: the codes-5/6/7 smoke `csky122`, the HEADROOM rule of item 18 (c), and the seal `pred/01_map122.md` (Harness Engineer, 2026-09-27)

* **Item 18 (c) in the scorer BEFORE the seal:** `HEADROOM_LEVELS = ('intro_next',)` is gone. `reading_of` /
  `headroom_of`: over the window rows (positions 10–88) of the base-arm (`burn=0`) blocks of the POPULATION PAIRS
  (after the outlier drops — the harness's reading of "окно 10–88 базового плеча", flagged to the lead), the share of
  `dt_us` < `HEADROOM_DT_US` = 25 000; ≥ `HEADROOM_SHARE` = 0.95 ⇒ `reading=HEADROOM` (game-speed line withheld); no
  base-arm row ⇒ `reading=NOT_EVALUABLE` (never HEADROOM; game-speed line withheld too); else `SPEED`. Every report
  prints `reading <R>: base-arm window share of dt_us < 25000 = <share> over <n> frames`. Fixtures: 0.949 / 0.950 by
  direct calls, 24 999 / 25 000 end-to-end (15 vs 16 slow base frames of 316 = 0.9525 / 0.9494), B-arm and outside-window
  frames ignored, a dropped pair ignored, `intro_next` with a two-vblank base reads SPEED, Sky Garden with a one-vblank
  base reads HEADROOM, no base arm = NOT_EVALUABLE. Direct-call fixtures of `pred_checks` for the unfilled and the
  filled constants (trap of s121) and `pred_constants_sealed` (the real file against `PRED_SHA`/`PRED_BYTES`).
* **Smoke `csky122`** (UNSEALED, disclosed; build `2baf8742…`; Sky Garden entered in 19.4 s, stable at frame 389; 200-s
  hold; 6 321 flips; 16 `GateArm:` blocks of `300+1800:burn=0|502000|602000|702000`; `KYTY_GPU_CLOCK_PIN=1`,
  `KYTY_GPU_MARKERS=0`, `KYTY_GPU_CHECKPOINTS` not passed; procload clean, idle cpu 3 gpu 6; `hostdev_csky122.txt`
  RUN_CLEAN (0 events); failure markers none; `AsyncPipelines: skipped draw` 0; BDA NEW, `bda_scan` 54–82):

  | arm | blocks | own group dose a frame | `cpu/wall` | other groups | `burn_s_seen` | `burn_s_main` | `burn_late` | `burn_cpu_bad` |
  |---|---|---|---|---|---|---|---|---|
  | `burn=0` | 0, 4, 8, 12 | — (all 0) | — | 0 | 285 | 0 | 0 | 0 |
  | 502000 (code 5, record thread block) | 1, 5, 9, 13 | `burn_r` 2 000.6–2 000.9 µs | 0.991–0.993 | 0 | 285 | 0 | 0–1 | 0 |
  | 602000 (code 6, M1 worker 0 block) | 2, 6, 10, 14 | `burn_m` 2 000.3–2 001.1 µs | 0.997–0.999 | 0 | 285 | 0 | 0–2 | 0 |
  | 702000 (code 7, `GuestGpu::Submit`) | 3, 7, 11, (15: 8 frames) | `burn_t` 2 000.3–2 000.5 µs | 0.998–0.999 | 0 | 285 | **0** | 0 | 0 |

  Seven `BurnLate:` lines (codes 5/6, 2 050–2 149 µs against 2 000) — the same small warm-up overshoot as the placebo
  in `bsky122`. The vblank staircase again: 2 vblanks 84–97 % of frames in every block.
* **Item 13 (a) FAILS for code 7:** it arms with the exact dose and burns only its own group, but `burn_s_main` = 0 in
  every block — the thread that advances the submit key is not the thread registered as `ThreadRole::Main`. So by item
  13 (b) **the arm "main guest thread" left the map**: `skym122` is removed from `PLAN_DEFAULT` (the tag has no PLAN
  entry; `map122.py --plan-check skym122` exits 2), and `go122a.sh skym122` refuses with the reason. The coverage split
  `burn_s_seen`/`burn_s_main` for code 7 stays in the scorer (fixture tag `sub122`). Mutants `plan_skym_code4` /
  `plan_skym_none` replaced by `plan_skym_back`; `headroom_levels_empty` replaced by 14 reading mutants.
* **Video of the smoke is missing** — my launcher `run_csky122.sh` gave the chain a PATH without `ffmpeg`, so
  `KYTY_REC` wrote only `rec_csky122.mp4.idx` (6 354 entries) and no `.mp4` (`stdout_csky122.txt:17`). The smoke is not
  repeated for it (no verdict uses its picture; the user watches the screen); the launcher PATH now includes WinGet
  Links and chocolatey.
* **Seal:** `pred/01_map122.md` sha256 `3430b26fb77ae7284e23ec7351860b9d4f6b37f7085627de5b39028260d00677`, 11 126 B —
  written into `map122.py` `PRED_SHA`/`PRED_BYTES`; the draft moved to `old/01_map122.draft.superseded_by_seal.md`.
  Fixtures on the sealed copy: `test_map122.py --real` **196 fixtures, 0 failed, ALL OK**.
* **Mutants on the sealed copy:** `mutlib` v4.1 FULL (`--control --no-memo --work-dir C:/kyty/s122/mutwork --cache-dir C:/kyty/s122/mutcache`, no `--changed-from`): **294 mutants, 294 killed (14 by a crash of the suite), 0 survived, 0 unresolved; controls 3 of 3 survived**; wall 1 605.6 s; report `mut_map122.sealed.txt` (sha `2ae1b9c1…`), log `mut_run_sealed.log`.
* **Evidence and seal record:** `mk_checks122.py` wrote `checks/map122_checks.json` (fixtures 194 ALL OK without `--real`, mutants 294/294, pred `3430b26f…`); `chk_map122.py` PASS for `sky122`, `skyp122`, `des122`, REFUSED for `skym122` (no PLAN entry); `SEALS122.txt` seal 01 lists 19 files (scorer `ce35585a…`, suite `49aa53a5…`, mutants `849a4303…`, chain `c4b2b213…`). **No sealed run happened; no smoke number enters a verdict.** Next: the lead's acceptance link of step 3b, which gates the sealed runs of HPP-7 (order `sky122`, `skyp122`, `des122`).
