# Session 107 — "maximum FPS", track 1: the other half of the `PipelineCache::m_mutex` contention (compute prefetch on the walker); first measure the holder and the spin share, then a code candidate behind a gate

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 106 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–7, the session-106 addition and **the
executor's decision after session 106** (items 1–4); §6; §7 (session-106 rows); then `C:/kyty/s106/FACTS.md` in
full (in git `docs/local-session-106.md`) incl. §7, and the sealed texts `C:/kyty/s106/pred/01`–`03` (hashes in
`SEALS106.txt`). The code-lens sketch of the fix is in `pred/03_audit106.md` and FACTS §5. Sealed texts are immutable.

**Open the report with these numbers:** Sky Garden, pinned, `dabatch=8` shipped: Δ mean `dt` −169.3 µs (`dab106`,
≈ +0.55 % game speed, vblank-quantised: +26 short frames of 2 726); the mean frame before it ≈ 31.8 ms (0.525×).
Under `dawalk=1` GuestGpu's wall at `PipelineCache::m_mutex` acquisitions was +616 µs a flip (`gw106`, at
`dabatch=64`): `GetGraphicsPrograms` +161, `GetGraphicsPipeline` +187, `GetComputeProgram` +268 (268 acquisitions).
60 FPS stays the direction without a route with a live estimate.

## 1. The port, first

Write `s107_port.py` **fresh in `C:/kyty/s106/`** (`SRC = C:/kyty/s106`, `DST = C:/kyty/s107`), modelled on
`C:/kyty/s105/s106_port.py` (sha256 `70157bbf…`). Never run a carried `*_port.py`. Advance chains by one; sealed
texts grow **44 → 47** (`01_gwall.md`, `02_dabatch.md`, `03_audit106.md` land in `prev106/pred/`; check basenames);
r6 gains the session-106 seal constants (`gw106.py` and `dab106.py` `PRED`, bare literals with `PRED_SHA`/
`PRED_BYTES`); `gates_base.txt` unchanged (1 092 B / 99 names / `303a7849…`; `dabatch` and `ctxtick` are NOT in it
and take their compiled defaults 8 and 1); `gates.cpp` 136 entries, `ABSENT 37` unless a gate is added (a new gate
makes 137 / 38). Carry `gw106.py`, `dab106.py`, their `make_*`/`fixture_*`, `go106*.sh`, `gates_dab8.txt` as
archive. The session-105 `m31_notes.md` stays where the 106 port put it.

## 2. Measure first (decision after 106, item 1)

One instrument patch, measurement only, no default moved: (a) HOLD counters on the walker's
`PipelineCache::PrefetchComputePipeline` and `QueueDrawAhead` — time under the lock, timestamped AFTER the
`LockGuard` (the existing `da_queue_us` includes the walker's own wait); (b) the spin share of GuestGpu's three
plkstat waits: `TryLock` first, and only on failure read `ThreadCpuNs(Gpu)` around the blocking `Lock`, giving
`pl_*_spin_ns` next to `pl_*_wait`. Record in ROADMAP → seal an observation run (ABBA `plkstat=0|1` is NOT needed;
one pinned run with `plkstat=1` and the new counters, `dabatch=8`, 300 s) with its predictions → run → read.
Scorer fixtures plant an effect in every decision term and walk every verdict branch (decision after 106, item 3).

## 3. The code candidate

A per-thread "already present" memo on the walker that skips `PrefetchComputePipeline` entirely (no lock, no
`m_program_cache->Get`, whose `MaterializeResources` includes the SRT walk): key = the `PrepareProgram` result
(computed outside the lock) plus a hash of the user SGPRs; an entry is recorded only when `Get` returned an id that
`m_compute_pipelines` already holds, stamped with atomic mirrors of `programs_epoch`, `memo_generation` and
`ShaderRegistrations()`; the memo is only a hint (the real dispatch always does its own `Get`/`GetComputePipeline`;
`m_compute_pipelines` is never erased; program ids are never reused), so a stale entry costs a missed prefetch,
never a wrong result. Behind a new gate (default 0) with counters (memo hits, skipped holds); ROADMAP record before
code; `check_gate_order.py`; sealed ABBA 600 s, pinned, the Δ`dt` bar (≤ −100 µs, 2·SE excluding 0), the video pass
with the pin; on SHIP the default moves, a new build, its video pass. Correct the stale `gates.h:534-535` comment
in the same code change.

## 4. Then

M3.2 (route A) — design and code allowed, measured run time only after section 3's run.

## 5. Traps that are live

1. **During a sealed run a heartbeat does nothing but reschedule** (session-106 audit: `cat`+`tasklist` ran inside
   `dab106`). No builds, compiles, scorers or reading agents while a run is on the GPU.
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included.
3. Scorers' IDENTITY hashes the INSTALLED exe: never rebuild between a run and its scoring.
4. plkstat's wait is the whole acquisition wall (spin + block); it is not a sub-part of `dt − cpu_net`.
5. Frame time is vblank-quantised: a Δ mean `dt` is a change in the share of short frames; do not add candidates'
   gains linearly.
6. `AsyncPipelines: skipped draw` is a fatal marker in the ABBA scorers (one repeat allowed).

## 6. Deliverable

PLAN with a measurable question; every decision recorded in ROADMAP first; CODE → TEST → VERIFY → **adversarial
audit before publishing**. At the end: one ROADMAP edit, FACTS (`C:/kyty/s107/FACTS.md`, mirrored as
`docs/local-session-107.md`), `docs/next-session-108.md`, both game contexts (`CLAUDE.md` = `AGENTS.md`) incl. the
environment-variable list, a short `HANDOFF.md` block, the mandatory commit without push.

## 7. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; a split of `dt − cpu_net`
into lock spin and other waits without the spin counters; that the memo removes the whole `cs` wait before its run.
