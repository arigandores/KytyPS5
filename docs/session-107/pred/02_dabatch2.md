# Sealed pre-registration 02 — session 107, track 1 candidate: `dabatch=8|2` under `dawalk=1`

**Immutable once written.** Recorded in `docs/ROADMAP.md` §0.1 ("СЕССИЯ 107 — ЗАПИСИ ДО ДЕЙСТВИЙ", items 4–5,
commit `ba0d59c`) before this text.

## 0. Why

`obs107` (pred/01): the walker thread holds `PipelineCache::m_mutex` behind 98.6 % of GuestGpu's contended wall;
its `QueueDrawAhead` holds are 57.7 % of it (1 080 holds a flip of 0.95 µs each at `dabatch=8`). Shorter holds
should shorten GuestGpu's waits [I]; the walker pays ×4 calls and worker notifications on the same CCD, which may
eat the gain — the prediction has low confidence.

## 1. What is tested

Build `dd567a0feb49d8f182345434920649b485b677b69569c5e06d9b9d73b20789a3` (installed; `plkstat` off, `cspmemo=0` —
behaviour of `2b30f836…` plus dark counters). Arm 0 `dawalk=1 dawalklead=1 dabatch=8` (today's default), arm 1
`dawalk=1 dawalklead=1 dabatch=2`. No `plkstat`, no `KYTY_GPU_WALL`: the shipping configuration.

## 2. Runs, in order, nothing else on the machine (no builds, compiles, scorers, agents; a heartbeat only
reschedules); one repeat on a fatal marker

1. `dab107`: `python C:/kyty/s107/enter_scene.py dab107 --hold 600 --attempts 1 --no-install --gates-file
   C:/kyty/s107/gates_base.txt --pred C:/kyty/s107/pred/02_dabatch2.md
   "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 dabatch=8|dawalk=1 dawalklead=1 dabatch=2"
   KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`; scored by `dab107.py` (derived from
   `dab106.py` by `make_dab107.py`; before this seal it ran on five fixtures in NON-draft mode with full protocol
   metadata — SHIP, SHIP_PENDING_VIDEO, KEEP by the bar, KEEP by a failed video, KEEP by the batch arming — each
   gave its planted verdict, `test_dab107.py`).
2. Only if the score reads `SHIP_PENDING_VIDEO`: `vdb107` — `--hold 120 --no-install --rec`, gate file
   `gates_dab2.txt` (= `gates_base.txt` + ` dabatch=2`), `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`; the scorer
   re-reads with `--video-meta vdb107.json --video-report vdb107_glitch.txt`.

## 3. Admission

The `dab106` integrity, controls and walk arming unchanged, with `BATCH_ARMED`: arm-1 / arm-0 `da_qcall` ≥ 3.

## 4. Ship rule

SHIP `dabatch=2` only if ADMITTED and **S1** mean Δ`dt` ≤ −100 µs and **S2** mean Δ`dt` + 2 SE < 0, and the video
pass reads PASS. Δ`cpu_net` reported, never deciding. On SHIP: ROADMAP first, then the `gates.cpp` default, a new
build and its own pinned video pass.

## 5. Predictions (published whether hit or miss)

B1 `da_qcall` ratio in [3.5, 4.5] · B2 Δ`da_queue_us` in [0, +600] · B3 Δ`cpu_net` in [−300, 0] · B4 Δ`dt` in [−250,
+50] · B5 Δ`dt` ≤ −100 (the ship bar; LOW confidence) · B6 Δ`da_miss` in [−30, +30].

## 6. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; that the mechanism is
shorter holds (no `plkstat` in this run); additivity with the `dabatch=8` gain (frame time is vblank-quantised).
