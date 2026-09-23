# Sealed pre-registration 02 — session 106, track 1 item 2 candidate: `dabatch=64|8` under `dawalk=1`

**Immutable once written.** Recorded in `docs/ROADMAP.md` §0.1 ("СЕССИЯ 106 — ЗАПИСИ ДО ДЕЙСТВИЙ", items 4–5,
commit `8ab9b5d`) before this text.

## 0. Why

`gw106` (pred/01, ADMITTED, NAMED `lock_wait_us`): under `dawalk=1` the GuestGpu thread waits +616.5 µs a flip on
`PipelineCache::m_mutex` (t 210), mostly spinning (`CRITICAL_SECTION` with spin count). The holder is the walker
thread: `QueueAhead` under the lock (`da_queue_us` 851 µs a flip, 134 calls of 64 requests ⇒ ~6.3 µs a hold, about
GuestGpu's own gap between acquisitions) and `PrefetchComputePipeline`. Knob `dabatch` (session 102, read once per
walk) sets the requests per `QueueDrawAhead` call, i.e. the length of each walker hold.

## 1. What is tested

Build `d23094dfe42478f8a40907741120837c4cf952ff16b830c1e6e55697dc177db3` (installed; `KYTY_GPU_WALL` absent ⇒
identical behaviour to `810bb54b…` plus dark counters). Arm 0 `dawalk=1 dawalklead=1 dabatch=64` (today's
default), arm 1 `dawalk=1 dawalklead=1 dabatch=8`. No `plkstat`, no `KYTY_GPU_WALL`: the shipping configuration.

## 2. Runs, in order, nothing else on the machine (no builds, compiles, scorers, agents); one repeat on a fatal marker

1. `dab106`: `python C:/kyty/s106/enter_scene.py dab106 --hold 600 --attempts 1 --no-install --gates-file
   C:/kyty/s106/gates_base.txt --pred C:/kyty/s106/pred/02_dabatch.md
   "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 dabatch=64|dawalk=1 dawalklead=1 dabatch=8"
   KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`; scored by `dab106.py` (derived from
   `lead105.py` by `make_dab106.py`; run on a synthetic fixture before this seal).
2. Only if the score reads `SHIP_PENDING_VIDEO`: `vdb106` — `--hold 120 --no-install --rec`, gate file
   `gates_dab8.txt` (= `gates_base.txt` + ` dabatch=8`), `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`; the scorer
   re-reads with `--video-meta vdb106.json --video-report vdb106_glitch.txt` (`s51_vidglitch.py`).

## 3. Admission

The `lead105` integrity, controls and walk arming unchanged (pairs ≥ 60, bands, work split, area verdict and
selection, pin once, two record threads, no checkpoint line, no GpuHangAbort, no fatal marker incl.
`AsyncPipelines: skipped draw`, identity of the installed exe, instruments dark, walks ±5 %), plus
`BATCH_ARMED`: arm-1 / arm-0 `da_qcall` level ≥ 4.

## 4. Ship rule (ROADMAP, decision after session 104)

SHIP `dabatch=8` as the default only if ADMITTED and **S1** mean Δ`dt` ≤ −100 µs and **S2** mean Δ`dt` + 2 SE < 0,
and the video pass reads PASS (installed binary, `dabatch=8` in the gate text, pinned, recorded, one ok attempt,
≥ 3 000 frames, 0 one-frame glitches). Δ`cpu_net` reported, never deciding. On SHIP: ROADMAP first, then the
`gates.cpp` default, a new build and its own video pass.

## 5. Predictions (published whether hit or miss)

B1 `da_qcall` ratio in [6, 9] · B2 Δ`da_queue_us` in [0, +250] · B3 Δ`cpu_net` in [−500, −100] · B4 Δ`dt` in
[−350, 0] · B5 Δ`dt` ≤ −100 (the ship bar; medium confidence) · B6 Δ`da_miss` in [−30, +30].

## 6. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; that the compute-
prefetch half of the contention (+268 µs at `GetComputeProgram`) is touched by this knob.
