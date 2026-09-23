# Sealed pre-registration 01 — session 105, "maximum FPS" track 1, candidate 1: knob `dawalklead` = 2 under `dawalk=1`

**Immutable once written.** A correction goes into a new sealed addendum. The decision this implements
(candidate 1, and the ship bar on Δ mean `dt`) was recorded in `docs/ROADMAP.md` §0.1 ("РЕШЕНИЕ
ИСПОЛНИТЕЛЯ ПОСЛЕ С. 104") before this text.

## 1. Question

`dawalk=1` (shipped in session 104) walks the guest's PM4 on its own thread at most `dawalklead`
submissions ahead of GuestGpu (default 1). The walk ahead cools the M1 results: in `dwk104` arm 1 vs arm
0, `da_take_us` +414.7, `da_miss` +219.1, `da_late` +8.1 a flip. Session 60 (phase means of `log_sky60`,
no ABBA, no pin): lead 2 gave `da_late` 0.00 and `da_miss` 202 against lead 1's 7.8–8.3 and 309–315.
**Does `dawalklead=2` shorten the mean frame in Sky Garden?**

## 2. Protocol

* Binary: the installed `61ae73476eac343fcca3554924496ec0c50da536826ecab6dea7a1e4548e4bd1` (session 104's
  ship build, `dawalk=1` compiled in). Harness `C:/kyty/s105`, `gates_base.txt` sha256
  `303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf` (pins `dawalk=1 dawalklead=1`).
* Run `lead105`: `python C:/kyty/s105/enter_scene.py lead105 --hold 600 --attempts 1 --no-install
  --gates-file C:/kyty/s105/gates_base.txt --pred C:/kyty/s105/pred/01_dawalklead.md
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1|dawalk=1 dawalklead=2" KYTY_GATE_SCHEDULE_ABBA=1
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`. No `KYTY_GPU_CHECKPOINTS`, no `KYTY_REC`. **No builds, driver
  compiles, scorer runs or agents of any kind while it runs** (sessions 103/104 MAJORs).
* Entry hang ⇒ one isolated `lead105_entry1`; INVALID ⇒ one repeat `lead105b` (decided before seeing any
  arm difference: a repeat is taken whenever the run is INVALID).
* Scorer `C:/kyty/s105/lead105.py` (derived from session 104's `dwk104.py`; pairs, blocks, controls,
  bands, work split, area verdict, pin, record thread, fatal markers incl. `AsyncPipelines: skipped draw`,
  as there), with: arms `dawalk=1 dawalklead=1` / `dawalk=1 dawalklead=2`; arming — both arms walk
  (`da_wjobs`, `da_wskip` ≥ 1 a flip), skip/posts identity within ±1 % and drops ≤ 5 % in each arm, walks
  per flip within ±5 %; instruments dark.

## 3. Ship rule (the ROADMAP decision after session 104)

SHIP `dawalklead=2` as the new default only if ALL: the run is ADMITTED; **S1** paired Δ mean `dt_us`
(arm 2 − arm 1) ≤ −100 µs; **S2** its 2·SE excludes 0 (mean + 2·SE < 0); **S3** the video pass `vld105`
(`enter_scene.py vld105 --hold 120 --attempts 1 --no-install --rec` with a gate text carrying `dawalk=1
dawalklead=2`, no schedule, `KYTY_GPU_MARKERS=0`; `s51_vidglitch.py`) reads ≥ 3 000 frames and 0 one-frame
glitches. S1–S2 without the video ⇒ SHIP_PENDING_VIDEO. Δ`cpu_net_us` is reported and never decides.
**Power:** at `dwk104`'s pair SD of Δ`dt` (549 µs), 600 s gives 2·SE ≈ 115 µs; an effect smaller than
~115 µs will not ship from this run.

## 4. Reported, never deciding

Δ`cpu_net_us`, Δ`da_take_us`, Δ`da_miss`, Δ`da_late`, Δ`da_hit`, Δ`da_walk_us`, `da_wdepth`, `da_wlag_us`,
Δ`gpu_busy_us`, Δ`draws`, the Δdt/Δcpu ratio.

## 5. Predictions (published whether hit or miss)

L1 Δ`da_late` in [−9, −3] a flip · L2 Δ`da_miss` in [−150, −30] · L3 Δ`da_take_us` in [−400, 0] µs ·
L4 Δ mean `dt` in [−350, +100] µs · L5 Δ mean `dt` ≤ −100 µs (the ship bar; low confidence).

## 6. Must not be claimed

60 FPS · a game-speed figure for the unpinned default setup (the pin holds the DRS step) · any gain from
Δ`cpu_net` alone · that route A is licensed by this run.
