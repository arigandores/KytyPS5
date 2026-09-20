# Session 102 — route E: the LAST measurement (M5), then code

**The user's three decisions after session 101 are recorded in `ROADMAP.md` §0.1 and §5 item 5
BEFORE this session acts on them** — the clause that failed in sessions 100 and 101. Read them
first, then `ROADMAP.md` §0.1, §2 E, §4, §6, §7. Then `C:/kyty/s101/FACTS.md` in full (in git
`docs/local-session-101.md`) — **including its §11** — then `C:/kyty/s101/README.md`, and the three
sealed texts `pred/01_two_directional.md` (29 915 B, `091ecf76…`), `02_regime_addendum.md`
(9 735 B, `b4ef078b…`) and **`03_audit_addendum.md` (20 259 B, `688b7be4…`)**. **Sealed texts are
immutable:** a correction goes into a new sealed addendum, never into the file.

**Open the report with the three numbers** (`ROADMAP.md` §5 item 5): budget ≤ ~3.0 µs a draw
(median) / ≤ ~2.3 µs (p99, 7 284 draws); the carried reference path is 6.4 µs a draw, 31.6 ms a
frame, GPU busy 12.8 ms; undone: **M5 only**. **Do not promise 60 FPS: the chance is ~15 %
(8…25 %).**

## 0. What the user decided, and what it changes

1. **M3 is closed as a FINAL GAP.** No further M3 measurement. The branch is
   constant-independent — it is GAP at 2.65, at 2.2535, at 2.595188 and at 2.455173.
   **G and R1 stay alive and UNLICENSED**; no CLOSE is claimed and `ROADMAP.md:46` stands.
2. **M4 is removed.** Its rule closes only P, and M1 closed P in session 95. The order is now
   **M1 → M2 → M3 (GAP) → M5**.
3. **A5 stays 0.1035 ms** (submission granularity, `bd96b`). The user was shown before deciding
   that the CLOSE threshold on this term is **A5 ≥ 1.42 ms**, that the measured label granularity
   `bd96a` gives **2.8936 ⇒ CLOSE ⇒ G and R1 closed**, and that `gpu-driven.md:67` prices the same
   row at **2–10 ms [U]**. The number of sync points stays [U] and stays in §7.

**So the measuring phase ends with M5, and this session is the hinge: one bench measurement, then
code.**

## 1. M5 — the last measurement, and it needs no game run

The sealed rule (`ROADMAP.md` §2 E): *«M5 — цена BDA/LDG на GPU (стенд, без прогона игры).
`KYTY_RECOMPILE` + `rd_cs_time.py` на топовых шейдерах. **Правило: > +6 % на топ-позициях GPU ⇒ G
закрыт.**»*

* **Seal it before a number**, with the shader set, the variant set, the estimator and the
  acceptance fixed in advance: which top-GPU shaders (name them by hash from the recorded
  `GpuTime-kind` / `GpuTime-top` populations), how many repetitions, which statistic, and what
  counts as a valid bench run. Sessions 15–19 built this stand; the recipe is in `HANDOFF.md` §5
  and in the environment list of the game context (`KYTY_RECOMPILE`, `s16_sass.py`,
  `rd_cs_time.py`, `pipestat.exe`).
* **Watch the register-pressure trap**: one extra live register on the 3.8 ms lighting CS
  `5323c4ef4f785055` has cost 45 % before (sessions 18–20). Report registers and SASS, not only
  time.
* **Either outcome ends the phase.** `> +6 %` ⇒ **G closed**, and with P, P+G and F already closed
  the rewrite has nothing left; the programme's honest target becomes "maximum FPS with unshakeable
  correctness". `≤ +6 %` ⇒ G survives, still **unlicensed**, and a prototype is the user's call at
  ~15 % and 15–30 sessions.
* **No game run is required.** If one is taken anyway, it is subject to every rule below.

## 2. Then code. Three candidates, none of which depends on any remaining measurement

1. **`KYTY_GPU_CHECKPOINTS` reads by presence, not by value** (`vulkanWindow.cpp:1195`). `=0` turns
   checkpoints ON, refuses the record thread (`commandRecorder.cpp:1078`) and arms a per-draw
   `EndRendering` pair, a per-draw `eAllCommands` barrier and a per-operation mutex; measured cost
   `gpu_busy` **48.6 → 12.8 ms**, frame **48.9 → 32.4 ms**. One line to fix, plus a **sweep of the
   whole tree** — `KYTY_FRAME_TRACE` is presence-tested too, so this is a class. **Its A/B already
   exists** (`cm101a` against `cm101c`/`cm101d`), which makes it the cheapest honest way to satisfy
   `ROADMAP.md` §6 with a change to a real path rather than a counter.
2. **The entry hang: `KYTY_BVH_LOOP_CAP`.** The uncapped BVH traversal `cs=0x380bb9d6…` hangs
   **6.67 % of entries** and has cost this programme whole runs. Design is ready
   (`C:/kyty/s101/design98/loops.md`); about eleven files including the SPIR-V backend, the cap in
   the translation-cache signature with a **separate cache directory**, trip counters in the
   fault-buffer tail. Needs a HIST run first and an **offline register/SASS check on
   `5323c4ef4f785055`**; the first capped run is fully cold. **A correctness bug for every user of
   the emulator.**
3. **`PrefetchComputePipelines` batch knob.** 41.9 % of the 1 836.9 µs walk is queueing under
   `PipelineCache::m_mutex`, **125 mutex acquisitions a flip** at the shipped 64-request batch.
   Three lines in `graphicsRun.cpp:1403` with its own controls (`da_hit`, `da_miss`, `da_late`).

**Order them yourself, but keep the build small:** session 100's own lesson is that the deciding
measurement must not ride on a hot-path change. If M5 is measured in the same session as a code
change, measure first and patch after.

## 3. Traps that are still live

1. **`KYTY_GPU_CHECKPOINTS` must not be passed at all** in any measuring run, not even as `=0`.
2. **Never rebuild between a measurement and its acceptance** — `guards.py` check 10 and the
   scorer's IDENTITY control hash the exe installed *now*.
3. All `KYTY_*` go **positionally** to `enter_scene.py`; `--attempts 1`; no warmup, no retry, no
   re-scoring; `--out` must never overwrite.
4. **An instrument's own cost is not a point value** — pair the estimator and publish a range
   (session 101: 0.071 / 0.109 / 0.355 ms for one instrument on one binary).
5. **A prediction re-registered after it missed is not a prediction**, and one entailed by another
   carries no information.
6. **Give any new control suite a frame-time band, a `rec_n` limb and a `gpu_busy_us` limb.** Two
   consecutive sessions had a full suite admit a run that was 50 % off.
7. `guards.py` checks 3b and 6 fail with nothing else running: reported, never deciding. Do not
   silence them and do not promote them.
8. The vblank plateau quantises `dt_us`; `summary4.py`'s `cpu_net_us` under lite **is**
   `cpu_gpu_us`; `spin_gpu_us` lives on the `FrameTrace-draw` line.

## 4. The port, first

Write `s102_port.py` **fresh in the source folder `C:/kyty/s101/`** (`SRC = C:/kyty/s101`,
`DST = C:/kyty/s102`), modelled on `C:/kyty/s100/s101_port.py`. **Never run a carried `*_port.py`.**
Advance: the COMMA chain 27 → 28 roots (`s102…s75`); `area_verdict.py` `range(102,70,-1)`;
`shift91.py` `range(102,66,-1)`; `s94lib.py` 11 roots, `bda93.py` 12, `stg92.py` 13; `regime94.py`
10 roots plus the `s102` fallback; the r6 paths (**12 files / 20 constants**, plus `cm101.py`'s own
`PRED` and `PRED2`) and r7's four expression paths repointed to `prev101/pred/`; sealed texts grow
**18 → 21**. `ABSENT` becomes **35 names** (add `cbmove`). Assert `gates_base.txt` is still
1 092 B / 99 names / `00c116dc…0594d8`, and that `gates.cpp` yields **134** `{"KYTY_*","name"}`
entries (111 gates + 23 knobs; 134 − 99 = 35).

## 5. Working procedure and the deliverable

PLAN with a measurable question, **record any rule or constant change in `ROADMAP.md` first**, then
CODE → TEST → a fresh VERIFY → **an adversarial audit before publishing**. One executor owns the
GPU, the log and the caches; no background build, scorer or review during a hold; build only through
`build_local.cmd`; `check_gate_order.py` after any gate/knob patch and **before** the build.
**`ROADMAP.md` §6 expects a source change that passed A/B** — and this is the first session in six
whose candidates move a real path, so claim it on its warrant, not on the gloss. **The video-pass
debt is real for candidates 2 and 3** (`--video`, `s20_vidglitch.py`, ≥ 3 000 frames): both can
reach the renderer. At the end: one edit to ROADMAP, then FACTS (`C:/kyty/s102/FACTS.md`, mirrored
as `docs/local-session-102.md`), `docs/next-session-103.md`, both game contexts **including their
environment-variable and gate list**, and the mandatory commit without push; do not capture the
dirty `3rdparty/nlohmann_json`.

## 6. Must not be claimed

That M3's final GAP closes, licenses or refutes anything — it closes **the measurement**, by the
user's decision; G and R1 stay alive and unlicensed · that M4 was performed (it was removed) · that
A5 is measured to be right (0.1035 ms is the user's decision; the design document's own band for
that row is 2–10 ms [U], and at A5 ≥ 1.42 the rule would have returned CLOSE) · that session 101
measured the subtractive half (one of four terms, unfloored) · that the regime finding is a speedup
— nothing was made faster, a diagnostic that had been on by accident was turned off · that the
split of the regime's cost between the lost record thread, the per-draw barrier and the
per-operation mutex is known · that `F_a`/`F_c` were re-measured · that the DRS clock debt, the
mode-2 residual pessimism or the cross-queue ACB tear are discharged · that M5 may be skipped, or
its rule changed, without the user's decision written into `ROADMAP.md` first. **And no frame-rate
gain, no speedup, no 60 FPS.**
