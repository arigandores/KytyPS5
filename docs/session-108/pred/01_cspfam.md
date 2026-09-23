# Sealed pre-registration 01 — session 108, track 1 candidate: `cspfam=0|4` (skip the walker's steady-state compute prefetch per shader family)

**Immutable once written.** Recorded in `docs/ROADMAP.md` §0.1 (the executor's decision after session 107, item 1 —
commit `87f1c2b`; "СЕССИЯ 108 — ЗАПИСИ ДО ДЕЙСТВИЙ", items 1–2 — commit `3cc53a2`, and item 4 — the resumption after the pause, fixtures by option (a) — committed with this text) before the code and this text.

## 0. Why

`obs107` (session 107): the walker thread holds `PipelineCache::m_mutex` behind ~99 % of GuestGpu's contended wall at
the three instrumented sites (422 µs a flip; spin share ≥ 0.75, likely ≈ 1, so mostly GuestGpu's own CPU); its
compute prefetch holds the lock 342 µs a flip (266 calls × 1.29 µs) and in the steady scene finds a built pipeline
every time (`cspf_have` 266/266, `cspf_new` 0).

## 1. What is tested

Source `f9e19f7`, build `fd1d0bd7f68280e97680bc68dfe56fdf57a134429a49bc9223ece6254b7b1e72` (made from the working tree
7 s before that commit, label `…-g3cc53a2-dirty`, same code; verify its sha256 before the run): knob `cspfam` (default
0; K = the streak): a per-thread table keyed on the shader FAMILY (code hash and base + the stage static key, no user
SGPRs) counts consecutive locked prefetches that found a built pipeline; at a streak ≥ K the walker returns before
the lock. The table is updated only while `cspfam` ≠ 0 — frozen in arm-0 blocks — and is cleared when the
programs-epoch mirror or `ShaderRegistrations()` moved (the epoch moves on a new `programs` entry, not on a new
permutation); the streak therefore means "the last K locked prefetches observed while the knob was non-zero". Guard
counters in every run (no gate): `cs_sync_new` (no pipeline at the dispatch — compiled synchronously) and
`cs_sync_wait` (a pending entry — queued by the lookahead prefetch or by the startup pipeline precache — still
compiling, waited for). Arm 0 `dawalk=1 dawalklead=1 cspfam=0` (today), arm 1 `dawalk=1 dawalklead=1 cspfam=4`. No
`plkstat`, no `KYTY_GPU_WALL`: the shipping configuration.

## 2. Runs, in order, nothing else on the machine (no builds, compiles, scorers, agents; a heartbeat only
reschedules — `go108.sh` holds `C:/kyty/SEALED_RUN.lock` for the whole chain); one repeat on a fatal marker

1. `fam108`: `python C:/kyty/s108/enter_scene.py fam108 --hold 600 --attempts 1 --gates-file
   C:/kyty/s108/gates_base.txt --pred C:/kyty/s108/pred/01_cspfam.md
   "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 cspfam=0|dawalk=1 dawalklead=1 cspfam=4"
   KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (installs the build above); scored by
   `fam108.py` (derived from `dab107.py` by `make_fam108.py`).
2. Only if the score reads `SHIP_PENDING_VIDEO`: `vfm108` — `python C:/kyty/s108/enter_scene.py vfm108 --hold 120
   --attempts 1 --no-install --rec --gates-file C:/kyty/s108/gates_fam4.txt --pred C:/kyty/s108/pred/01_cspfam.md
   KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (`gates_fam4.txt` = `gates_base.txt` as ONE line with ` cspfam=4` before
   its trailing CRLF, 1 101 B, sha256 recorded in `SEALS108.txt`); then `python C:/kyty/scripts/s51_vidglitch.py
   C:/kyty/s108/rec_vfm108.mp4 4 6 C:/kyty/s108/vidframes_vfm108 > vfm108_glitch.txt`; the scorer re-reads with
   `--video-meta vfm108.json --video-report vfm108_glitch.txt`. Both runs are chained in `go108.sh` (modelled on
   `C:/kyty/s107/go107b.sh`, the main run without `--no-install`).

## 3. Admission

The `dab107` integrity, controls and walk arming, with the batch arming replaced by `FAMILY_DARK_ARM0`
(Σ`cspfam_look` = 0 over arm-0 kept rows) and `FAMILY_ARMED_ARM1` (arm-1 level of `cspfam_skip` ≥ 1), plus
**`SYNC_COMPILE`**: over ALL rows from frame 2100, by each row's arm, Σ`cs_sync_new` of arm 1 ≤ that of arm 0 + 2
(both sums and `cs_sync_wait` are printed).
Fixtures (NON-draft, `test_fam108.py`, 103 cases, all as planted; each asserts the exact failing set and
the exact failing ship rules, video checks, arming sub-checks by name and protocol errors): every verdict branch
(SHIP, SHIP_PENDING_VIDEO, KEEP by the bar, KEEP by a failed video, KEEP not admitted, DRAFT) and the refusals of
`main()`; alone, S1, S2, all nine video checks (and a missing video file reading ABSENT), every integrity term
(`PREREG_PINNED`, `BINARY_SEALED`, `SCHEMA`, `FIELD_ORIGIN`, `RAW_CONTIGUITY`, `DURATION`, `GATEARM`, `NO_FLOOR`,
`MARKERS_OFF`, `NO_RECORDING`, `STREAMS_COMPLETE`, `ROW_ARMS`, `IDENTITY` through `main()`), every control
(`PIN_ONCE`, `RECORD_THREAD_TWO`, `NO_CHECKPOINT_LINE`, `NO_GPUHANGABORT`, `NO_FATAL_MARKER` for each of its eight
markers, `PAIRS`, `BANDS`, `WORK_SPLIT`, `AREA_VERDICT`, `AREA_SELECTED`, `SYNC_COMPILE` with its +2 edge), every
arming sub-check by name under `control:ARMING` (`WALK_ARMED_ARM0/1`, `WALK_IDENTITY_ARM0/1`, `WALK_DROPS_ARM0/1`,
`WALKS_SAME`, `INSTRUMENTS_DARK`, `FAMILY_DARK_ARM0`, `FAMILY_ARMED_ARM1`) and every protocol error (each sealed
env value, the schedule in env and meta, each absent variable, an extra variable, the gates sha and text, the
attempt label, count, outcome, hold exit and hold, the meta hold). Coupled by construction and asserted as exact
sets: `INPUTS` with the protocol (a missing input is a protocol error), `ENV_NO_CHECKPOINTS` with the protocol (an
extra `KYTY_*` variable), `AB_BA_BALANCED` with `GATEARM` or `PAIRS` (the pinned ABBA pattern pairs whole
quartets, one pair of each orientation), `BINARY_SEALED` with `IDENTITY` in `main()`, and the no-pair early
return (`PAIRS` with `AB_BA_BALANCED`, `BANDS`, `WORK_SPLIT`, both area controls, `ARMING`).

## 4. Ship rule

SHIP `cspfam=4` only if ADMITTED and **S1** mean Δ`dt` ≤ −100 µs and **S2** mean Δ`dt` + 2 SE < 0, and the video
pass reads PASS (the scorer's nine video checks: installed binary, `dawalk=1` and `cspfam=4` in the gate text,
pinned, recorded, no schedule, no checkpoints, one ok attempt, ≥ 3 000 frames, 0 one-frame glitches). Δ`cpu_net`
reported, never deciding. On SHIP: ROADMAP first, the `gates.cpp` default, a new build and its own pinned video pass,
checked by a script pinned to that build's sha256 (as `check105.py` was).

## 5. Predictions (published whether hit or miss)

F1 arm-1 `cspfam_skip` level in [150, 270] a flip · F2 arm-1 `cspf_have` level ≤ 60 · F3 Δ`cpu_net` in [−400, −50]
· F4 Δ`dt` in [−300, 0] · F5 Δ`dt` ≤ −100 (the ship bar; medium-low confidence) · F6 Δ`da_miss` in [−30, +30].

## 6. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; that the family skip is
safe in scenes other than Sky Garden (scene loads bring new permutations; `cs_sync_new` is the guard, not a proof);
additivity with other gains (frame time is vblank-quantised).
