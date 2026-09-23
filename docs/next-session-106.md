# Session 106 — "maximum FPS", track 1 item 2 first: where the +196 µs of GuestGpu time off-CPU under `dawalk=1` goes, then a candidate by the Δ`dt` bar; route A M3.2 written alongside without measured run time

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 105 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–4, the session-105 addition and
**the executor's decision after session 105** (items 1–4: track 1 item 2 first; M3.2 takes no measured run time
before it; the scorer-fixture rule; the clock pin on every sealed run incl. the video); the decision after
session 104 (two tracks, ship bar on Δ`dt`); §4, §6, §7 (session-105 rows); then `C:/kyty/s105/FACTS.md` in full
(in git `docs/local-session-105.md`) incl. §7, the design `docs/session-105/designA3_stage3.md`, and the sealed
texts `C:/kyty/s105/pred/01`–`04` (hashes in `SEALS105.txt`). Sealed texts are immutable.

**Open the report with these numbers:** Sky Garden steady mean `dt_us` ≈ 31.6 ms pinned (`dwk104` arm
`dawalk=1`; `reg105b` 30.80 ms over the middle third of a 180 s pinned screen); game speed = 16 667 / mean `dt_us`
≈ 0.53×; GuestGpu busy ≈ 97 %. 60 FPS stays the direction without a route with a live estimate. **Game speed is
measured by Δ`dt` directly.**

## 1. The port, first

Write `s106_port.py` **fresh in `C:/kyty/s105/`** (`SRC = C:/kyty/s105`, `DST = C:/kyty/s106`), modelled on
`C:/kyty/s104/s105_port.py`. Never run a carried `*_port.py`. Advance chains by one; sealed texts grow
**40 → 44** (`01_dawalklead.md`, `02_m31.md`, `03_scorer_fix.md`, `04_audit105.md` land in `prev105/pred/`; no
basename collision, checked in session 105); r6/r7 gain the session-105 seal constants (`lead105.py`, `ctx105.py`
`PRED`); `gates_base.txt` unchanged (1 092 B / 99 names / sha256 `303a7849…`, `dawalk=1`; `ctxtick` is NOT in
it and takes its compiled default 1); **`gates.cpp` 136 entries (111 gates + 25 knobs), `ABSENT` 37** unless a
gate is added. Carry `lead105.py`, `ctx105.py` (the FIXED one), `check105.py`, `make_ctx105.py`, `go105*.sh`,
`gates_ctx1.txt`, `gates_ctx2.txt` as archive (pinned to their seals; never re-run).

## 2. Track 1 item 2 — the +196 µs off-CPU (ROADMAP decision after session 105, item 1)

`dwk104`: Δ`cpu_net` −458.5 µs but Δ mean `dt` only −265.9 µs ⇒ ≈ +196 µs of frame time that is not GuestGpu CPU
appeared with `dawalk=1` (ratio 0.58, 95 % CI 0.43–0.70). Candidates [I]: GuestGpu waits on
`PipelineCache::m_mutex` held by the walker's `QueueDrawAhead`; the walker thread preempts GuestGpu or its M1
workers on the `dapin` CCD; GuestGpu waits for the walker (`dawalklead`, `da_wlag_us`); the record thread.

1. **Read (no runs):** where `DrawAheadWalk` runs (affinity under `dapin=1`, priority), every lock and wait it
   shares with GuestGpu, and which existing counters measure GuestGpu time off-CPU (wall busy vs `cpu_gpu_us`;
   `pl_prog_wait_us`/`plkstat`, `a_wait_us`, `mh_pres_wait_us`, `da_wlag_us`; what is dark in `lite`). Write the
   decomposition `Δdt − Δcpu_net = Σ named waits + rest` with every term's instrument, its cost, and whether it
   is live under `KYTY_FRAME_TRACE=lite`.
2. **Record in ROADMAP, then seal** one ABBA `dawalk=0|1`, 600 s, pinned, the separating instruments armed in
   BOTH arms (their own cost cancels in the contrast; say so), rule and thresholds in the seal: which term, if
   ≥ half of the 196 µs, names the mechanism. **Run the derived scorer on a synthetic fixture carrying every new
   field before sealing** (decision after 105, item 3).
3. **If the mechanism has a lever in the tree** (e.g. walker affinity/priority, `dabatch`, `dapin` for the walker
   alone): a candidate ABBA by the Δ`dt` bar (≤ −100 µs, 2·SE excluding 0, work/area controls, video pass with
   the pin). **If not:** the fix is designed and recorded in ROADMAP before any code.

## 3. Track 2 — route A M3.2 (written, not measured, until item 2 has had its run)

From `designA3_stage3.md` and the audit (`pred/04` items 1, 3, 4, 7): the binding-preparation phase takes the
buffer; `StreamBuffer::Commit(tick)`; delete the `ctxtick=0` branch (knob keeps 1 and 2/3 for checks) and fix the
test at `ShaderRecompilerComputeTests.cpp:1917`; assert `tick == m_command.m_tick` at the three `NextTick`
sites under `ctxtick ≥ 2`; extend `ctx_rec_block` to `WaitPriorityOperations`, `CommandRecorder::Drain`,
`WaitAsyncCopies`, `queue_mutex`; a positive control for `ctx_midsub` (force a mid-draw submit, e.g. a tiny
stream ring, at `ctxtick=2`, and see it count; the `ctx-mid:` row value is µs, the count follows `/`).
Acceptance recorded in ROADMAP before the code, sealed before its runs; its runs come after track 1's.

## 4. Traps that are live

1. No builds, driver compiles, scorer runs **or reading agents** while a sealed run is on the GPU.
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included (session-105 deviation).
3. Scorers' IDENTITY hashes the INSTALLED exe: never rebuild between a run and its scoring (debt §7).
4. `KYTY_BVH_LOOP_CAP` ON by default (65 536); the loop-cap re-series (episode-aware) is still owed.
5. At `ctxtick ≥ 2` mid-operation submits are renamed `ctx-mid:<site>` in `FrameTrace-submit` — exact-name
   scorers (`shift91.py` `host-read`) would miss them; the default 1 does not rename.
6. `AsyncPipelines: skipped draw` is a fatal marker in the ABBA scorers (one repeat allowed).

## 5. Deliverable

PLAN with a measurable question; every decision recorded in ROADMAP first; CODE (or a default flip) → TEST →
VERIFY → **adversarial audit before publishing**. At the end: one ROADMAP edit, FACTS
(`C:/kyty/s106/FACTS.md`, mirrored as `docs/local-session-106.md`), `docs/next-session-107.md`, both game
contexts (`CLAUDE.md` = `AGENTS.md`) incl. the environment-variable list, a short `HANDOFF.md` block, the
mandatory commit without push.

## 6. Must not be claimed

60 FPS · a game-speed gain from Δ`cpu_net` alone · that route A will reach G (a model ceiling) · that the loop
cap is accepted · that `ctx_midsub` = 0 means "no mid-draw submits anywhere" before its positive control.
