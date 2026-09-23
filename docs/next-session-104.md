# Session 104 — route V: the vblank plateau. Read how the guest paces its flips, measure the ceiling, then (only if it pays) a late-flip release behind a gate with a sealed ABBA

**Read first:** `ROADMAP.md` §0.1 — the session-103 addition and **the executor's decision after session 103
(G with a page table CLOSED on an upper bound; no route with a live estimate for 60 FPS; route V next, as a
hypothesis)**, §4 (the vblank plateau), §6, §7 (the session-103 rows); then
`C:/kyty/s103/FACTS.md` in full (in git `docs/local-session-103.md`), including §8 (the audit), and the sealed
texts `C:/kyty/s103/pred/01`–`05` (hashes in `SEALS103.txt`). Sealed texts are immutable.

**Open the report with these numbers** (session 103's series, binary `16ef56b6…`, Sky Garden, scene window of
all 67 entries, 37 119 frames): `dt_us` median 33.5 ms, `cpu_gpu_us` 32.9 ms, `gpu_busy_us` 12.6 ms; frames on
2/3/1 vblanks = 79.3/20.1/0.5 %; `cpu_gpu_us/dt_us` ≈ 0.98 on both 2- and 3-vblank frames; **game speed =
16 667 / mean `dt_us`** (the game steps 1/60 s per flip). 60 FPS stays the direction but has no route with a
live estimate (ROADMAP §0.1); the work is on "maximum FPS with unshakable correctness". Do not promise a
speedup before the A/B.

## 0. Why route V — a hypothesis, with the evidence against it

The emulator releases a flip only on a tick of its emulated 60 Hz vblank (`src/graphics/presentation/
videoOut.cpp`, the vblank thread: `VblankBegin(); m_flip_queue.Flip(0);`, and `IsFlipDueLocked` with
`flip_rate`); frame intervals are quantised (79.3 % two vblanks, 20.1 % three). **But the data do not show
the GuestGpu thread idling on the grid:** `cpu_gpu_us/dt_us` is 0.98 on two- AND three-vblank frames
(48.7 ms of CPU on 50 ms frames). Two readings: (i) the frame's work really fills the interval — then a flip
release gains nothing and the lever is the 20 % tail of heavy frames (with the median at 33.5 ms, right at
the 33.3 ms boundary, a 1–3 ms CPU saving would move part of that tail to two vblanks); (ii) the CPU counter
includes busy time that grows with the interval — then the release has a real ceiling. Steps (a)/(b) decide
between them, and step (b′) below measures the tail. The host display was read as 240 Hz
(Win32_VideoController, at session 103).

## 1. The port, first

Write `s104_port.py` **fresh in `C:/kyty/s103/`** (`SRC = C:/kyty/s103`, `DST = C:/kyty/s104`), modelled on
`C:/kyty/s102/s103_port.py`. **Never run a carried `*_port.py`.** Advance the COMMA chain 29 → 30 roots, the
`range(…)` constants by one, the root lists of `s94lib.py`/`bda93.py`/`stg92.py`/`regime94.py` (+ the `s104`
fallback); sealed texts grow **30 → 35** (the five session-103 texts land in `prev103/pred/`; check no name
collides — `04_audit_addendum.md` and `05_claims_addendum.md` are new); r6 gains the session-103 constants (`bvh103.PRED`, the three seal
paths of `m5p_103.py`, and every other `pred/…` constant of the new tools); `NEW_SESSION` names session-104
files. `ABSENT` stays **36**; `gates_base.txt` 1 092 B / 99 names; `gates.cpp` **135** entries — unless this
session adds a gate (then +1 and `ABSENT` 37 in the NEXT port). Carry `M5P_RUNBOOK.md`, `m5p_*`, `bvh103.py`,
`series103.py`, `identity_sweep.py` (archive: pinned to their own seals — never re-run).

## 2. Step (a) — how does the guest pace its flips? (reading + one diagnostic run, no code on the real path)

* Read `videoOut.cpp` end to end for the flip path: `VideoOutSubmitFlip` / `SubmitFlipFromGpu`
  (`sync.cpp:228…`), `ReserveFlipRequest`, the flip queue, `IsFlipDueLocked`, the flip/vblank events the guest
  can wait on (`KERNEL_EVFILT_VIDEO_OUT`), `VideoOutWaitVblank`, `VideoOutGetFlipStatus`, `SetFlipRate`, the
  pace/speed EMA (`KernelSetGuestSpeed`).
* One diagnostic run (`enter_scene.py … KYTY_AV_TRACE=1` positionally, plus `KYTY_PRINT_NAMES_THREADS` for
  the guest's render/main threads if needed, short hold): which calls does ASTRO BOT make per frame, what
  flip rate/mode does it set, and does its next frame wait on the flip event, on a vblank event, or on
  nothing (GPU-side flip via PM4 only)?
* **Decide in writing (ROADMAP first) whether a release can pay at all.** If the guest's next frame waits
  on vblank ticks rather than on the flip, releasing the flip changes nothing — then route V needs a
  different lever (e.g. the vblank grid itself), recorded as such.

## 3. Step (b) — the ceiling, measured before any behaviour change

A counter (always on under `FrameStats`, no behaviour change): per flip, the time from "flip request ready
to go" (GPU-side flip packet processed / request reserved) to "flip released at a vblank tick" = the
quantisation wait. One baseline run in Sky Garden (≥ 300 s hold, `KYTY_GPU_CLOCK_PIN=1`) gives the mean wait
per frame and its share of `dt_us` — **the ceiling of route V**. Seal the go/no-go rule BEFORE the run (e.g.
build the release only if the mean wait is ≥ 1.0 ms a frame, or ≥ 3 % of `dt_us`).

## 3′. Step (b′) — the three-vblank tail, whatever (b) says

Split the scene's frames into two populations (two vs three vblanks) and compare every `FrameTrace` /
`FrameTrace-draw` / `FrameTrace-x` counter between them on the same run (draws, dispatches, uploads,
`img_up_kb`, `da_*`, GC, faults, `hostread_*`): what makes a frame heavy? If it is CPU work, name the largest
term; that term — not a flip release — is then the first lever of "maximum FPS".

## 4. Step (c) — only if (b) passes: the release, behind a gate, with a sealed ABBA

* Gate `vrrflip` (default 0; `gates.h`/`gates.cpp` last row; `check_gate_order.py` before the build): a flip
  that is due and ready is released immediately when at least one vblank period has passed since the
  previous release, instead of waiting for the next tick; never faster than the vblank frequency. The guest-
  visible vblank events and counters keep their 60 Hz meaning.
* Seal `pred/01` before the run: ABBA within one run (`KYTY_GATE_SCHEDULE` + `_ABBA=1`), primary endpoint
  **mean `dt_us`** of the scene (equivalently game speed), controls: work per frame (draws), DRS step
  (`rt_kpx`), `cpu_gpu_us` (must NOT move — the release is not a CPU saving), audio sync (`KYTY_AV_TRACE`
  audio lines: no drift growth), no hang; decision rule and threshold written first; `KYTY_GPU_CLOCK_PIN=1`.
* **Video pass is owed** (the release changes presentation): `--rec`, `s51_vidglitch.py`, ≥ 3 000 frames,
  plus a look at frame pacing (judder) in the video.
* Shipping the default ON only by the sealed A/B plus the video pass, recorded in ROADMAP first.

## 5. Also owed (only with an idle machine, never overlapping a sealed run — the session-103 MAJOR)

* The loop-cap re-series with an episode-aware rule (histogram of spent budget inside/outside trip
  episodes) and a video pass that actually shows a trip — ROADMAP §7.
* The shader seed `_ShaderSeeds/PPSA21564` (stale since translator hash `699c1e4b…`): rebuild with
  `tools/shader_seed.py` from a verified run covering the intro, the desert and Sky Garden.

## 6. Traps that are live

1. **No offline builds, driver compiles or scorer runs while a sealed run is on the GPU** (session 103's
   audit MAJOR: pipestat compiles overlapped 53 of 67 entries).
2. `KYTY_BVH_LOOP_CAP` is ON by default; `=0` turns it off (and moves the cache to its own directory).
   `KYTY_LOOP_LIMIT` is replaced by the cap for capped programs.
3. Translator hash `699c1e4b…`: the translation cache is warm after session 103's runs; the seed is stale.
4. `gates_base.txt` pins `recordthread=1`; `enter_scene.py` takes emulator flags as `--emu-arg=--rd`; all
   `KYTY_*` positionally; `--attempts 1`; never rebuild between a measurement and its acceptance.
5. The first-character env class (`value[0] != '0'`) still reads `false`/`off` as ON.
6. `bl_trip`/`bl_near` read 0 without `KYTY_FRAME_TRACE`; the always-on witness is the `BvhLoopCapTrip:` line.

## 7. Deliverable

PLAN with a measurable question; any rule, threshold or decision recorded in `ROADMAP.md` first; CODE → TEST →
a fresh VERIFY → **an adversarial audit before publishing**. At the end: one edit to ROADMAP, FACTS
(`C:/kyty/s104/FACTS.md`, mirrored as `docs/local-session-104.md`), `docs/next-session-105.md`, both game
contexts (`CLAUDE.md` = `AGENTS.md` in the emulator folder) including the environment-variable list, a short
block in `HANDOFF.md`, and the mandatory commit without push; do not capture the dirty `3rdparty/nlohmann_json`.

## 8. Must not be claimed

60 FPS · that the goal changed (60 FPS stays the direction, without a route) · that the grid quantisation
costs anything before (b) measures it · that G is open (M5′ closed it on an upper bound; a flat-mirror design is a different, unpriced design)
· that the loop cap is accepted · that a flip release is a CPU saving · any game-speed gain before its sealed
A/B and video pass.
