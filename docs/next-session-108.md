# Session 108 — "maximum FPS", track 1: skip the walker's steady-state compute prefetch per shader family (code candidate behind a knob, sealed ABBA under the pin); then route A M3.2

> **RESUME POINT (session 108 was paused by the user on 2026-09-23, see `docs/local-session-108.md`).** Done: the
> ROADMAP records (`3cc53a2`), the code of §2 (`f9e19f7`, knob `cspfam`, guard counters `cs_sync_new/wait`), build
> `fd1d0bd7…` (not installed), the scorer `fam108.py` + `make_fam108.py` + 24 fixtures (ALL OK) and the seal DRAFT —
> all in `docs/session-108/`. Not done: §1 port (counts now: sealed texts 50, `gates.cpp` 138 entries = 111 + 27,
> `ABSENT 39`), the fixture debt, the seal, the run, the audit. Installed game binary: `dd567a0f…` (session 107). The
> session loop and the heartbeat cron are stopped. **Resume with `docs/local-session-108.md` §2, in its order: protect
> the build (check `C:/kyty/build/install` = `fd1d0bd7…`, build nothing there until `fam108` is scored), the fixture
> debt, the port (§1 below), place and seal from the draft, run.**

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 107 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–7, the session-107 addition and **the
executor's decision after session 107**; §6; §7 (session-107 rows); then `C:/kyty/s107/FACTS.md` in full (in git
`docs/local-session-107.md`) incl. §7, and the sealed texts `C:/kyty/s107/pred/01`–`03` (hashes in `SEALS107.txt`).
Sealed texts are immutable.

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3`: mean
frame ≈ 31.6 ms (0.53× game speed). GuestGpu's contended wall at `PipelineCache::m_mutex` ≈ 420 µs a flip (`obs107`,
three instrumented sites), holder the walker thread (~99 %), spin share ≥ 0.75 (likely ≈ 1) — so mostly GuestGpu's
own CPU. The walker's compute prefetch finds a built pipeline every time in the steady scene (`cspf_have` 266/266,
`cspf_new` 0) and holds the lock 342 µs a flip for it. 60 FPS stays the direction without a route with a live estimate.

## 1. The port, first

Write `s108_port.py` **fresh in `C:/kyty/s107/`** (`SRC = C:/kyty/s107`, `DST = C:/kyty/s108`), modelled on
`C:/kyty/s106/s107_port.py` (sha256 `03a05591…`). Never run a carried `*_port.py`. Advance chains by one; sealed
texts grow **47 → 50** (`01_obs107.md`, `02_dabatch2.md`, `03_audit107.md` land in `prev107/pred/`; check basenames);
r6 gains `obs107.py` and `dab107.py` `PRED` (bare literals with `PRED_SHA`/`PRED_BYTES`); `gates_base.txt` unchanged
(1 092 B / 99 names / `303a7849…`); **`gates.cpp` now 138 entries (111 + 27; `cspfam` is the last knob row), `ABSENT
39`.** Carry the session-107 scorers, tests, `go107*.sh`, `gates_obs.txt`, `gates_dab2.txt` as archive. Session-107
files the global `s107 → s108` rewrite breaks, to be classed explicitly as the s107 port did for its equivalents:
`audit107/dab107_mutS2.py` and `audit107/obs107_mutPIN.py` (bare `C:/kyty/s107/pred` literals, frozen/dangling),
`audit107/recount_dab.py`, `recount_obs.py`, `dab_mech.py` (read `C:/kyty/s107/log_*.txt`), `make_dab107.py` (anchored
generator), `roadmap107_close.py` (one-shot). New session-108 names the port must allow: `fam108.py`, `make_fam108.py`,
`test_fam108.py`, `gates_fam4.txt`, `SEALS108.txt`, `go108.sh`.

## 2. Track 1 — the family skip (code, knob, sealed ABBA)

Knob (e.g. `cspfam`, default 0, LAST knob row): in `PipelineCache::PrefetchComputePipeline`, a per-thread table
keyed on the shader FAMILY (code hash + base + the stage static key from `BuildStageStaticKey`, NO user SGPRs) counts
consecutive locked prefetches of that family that found a built pipeline; once a family has K (e.g. 4) such results
and the programs-epoch mirror and `ShaderRegistrations()` have not moved, the walker returns before the lock.
Safety readout, in every run: a counter of dispatch-time SYNCHRONOUS compute compiles (`GetComputePipeline`'s
"not found" branch, `KernelTimeFreezeScope`) — a skipped prefetch of a new permutation shows up there as a compile on
the dispatch; the ABBA admits the run only if that counter does not rise in the skip arm. The memo is only a hint:
the dispatch always runs its own `Get`/`GetComputePipeline`. ROADMAP record before code; `check_gate_order.py`; a
verify mode is not needed (no id is reused; the only failure is a missed prefetch, which the counter sees).
Seal: ABBA `cspfam=0|4` (the implemented knob's value IS K; the draft in `docs/session-108/` uses 4), 600 s, pinned, the Δ`dt` bar (≤ −100 µs, 2·SE excluding 0), the lead105-lineage controls,
the sync-compile control, video pass with the pin; scorer derived by a `make_*.py`; fixtures: each decision term
and each admission term gets a fixture where ONLY it fails, plus every verdict branch (decision after 107, item 2).

## 3. Route A M3.2

Design and code allowed, but NOTHING built into `C:/kyty/build/install` before `fam108` (and `vfm108`) are scored — the
unreproducible build `fd1d0bd7` must survive until then (use a separate build dir if a build is needed); measured run
time only after section 2's run: the binding-preparation phase takes the
buffer; `StreamBuffer::Commit(tick)`; the `ctxtick=0` branch deleted; asserts at the three `NextTick` sites;
`ctx_rec_block` coverage; a `ctx_midsub` positive control. Correct the stale `gates.h:534-535` `dabatch` comment in the
same code change.

## 4. Debts that stay open

`dapin=1|3` re-measure under the pin (the §7 "re-measure `dapin` with the record path" debt; `dapin=3` is the default
since session 82 — any such run re-measures the incumbent, its SHIP branch is a no-op). The M1 queue's own
synchronisation (tag 1) — a design task.

## 5. Traps that are live

1. During a sealed run a heartbeat does nothing but reschedule. No builds, compiles, scorers or reading agents
   while a run is on the GPU.
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included.
3. Scorers' IDENTITY hashes the INSTALLED exe: never rebuild between a run and its scoring.
4. plkstat's wait is the whole acquisition wall; the session-107 contended-path instrument pulls its spin share toward
   0.5 (0.75 is a lower bound).
5. Frame time is vblank-quantised: do not add candidates' gains linearly.
6. `AsyncPipelines: skipped draw` is a fatal marker in the ABBA scorers (one repeat allowed).
7. Check a knob's CURRENT default in `gates.cpp` before proposing it as a candidate (`dapin` was proposed as
   "never shipped" in session 107's first draft; it ships since session 82).

## 6. Deliverable

PLAN with a measurable question; every decision recorded in ROADMAP first; CODE → TEST → VERIFY → **adversarial
audit before publishing**. At the end: one ROADMAP edit, FACTS (`C:/kyty/s108/FACTS.md`, which must carry over §1 and
§3 of the current WIP `docs/local-session-108.md` before the git mirror replaces it), `docs/next-session-109.md`, both game contexts (`CLAUDE.md` = `AGENTS.md`) incl. the
environment-variable list, a short `HANDOFF.md` block, the mandatory commit without push.

## 7. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; that the family skip is
safe in scenes other than the one measured (scene loads create new permutations — the sync-compile counter is the
guard, not a proof).
