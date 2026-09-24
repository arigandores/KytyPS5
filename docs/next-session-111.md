# Session 111 — "maximum FPS", track 1: the contention left after `cspfree=1`, then `daslot` (the M1 queue off `PipelineCache::m_mutex`)

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 110 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–7 and **the executor's decision after
session 110**; §6; §7 (session-110 rows); `C:/kyty/s110/FACTS.md` (git `docs/local-session-110.md`) incl. §7;
`C:/kyty/s109/design109.md` §A (the `daslot` design); the sealed texts `C:/kyty/s110/pred/*` (`SEALS110.txt`).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1`. Shipped in session 110: `cspfree=1` — Δ mean frame ≈ −200 µs at the pin (pooled full-block estimate of
the ship run and session 109's measurement, −202 ± 45; the sealed 60–88 window read −418.7 — inflated, audit). Before it, GuestGpu's contended wall at `m_mutex` was ~420 µs a flip, the walker
the holder in ~99 % (`QueueDrawAhead` ~58 %, the compute prefetch ~41 % — now gone). 60 FPS stays the direction
without a route with a live estimate.

## 1. The port, first

`s111_port.py` fresh in `C:/kyty/s110/` (SRC `C:/kyty/s110`, DST `C:/kyty/s111`), modelled on
`C:/kyty/s109/s110_port.py` (`544b231d…`). Sealed texts 58 → 62 (`01_stl110.md`, `02_stl110b.md`, `03_shp110.md` + the
audit addendum `04_audit110.md` → `prev110/pred/`). r6 gains `stl110.py`, `stl110b.py`, `shp110.py` `PRED`.
`gates_base.txt` unchanged; `gates.cpp` 139 entries (`cspfree` default 1), ABSENT 40 (+1 per new knob before the port).
Do not carry `kyty_emulator_*.exe` or `fx_*` fixture dirs. Class the generators (`make_stl110*.py`,
`make_test_stl110.py`, `make_shp110.py`), the one-shots (`seal110.py`) and `audit110/`.

## 2. Observation `obs111` (sealed, 300 s, pinned)

`plkstat=1`, defaults otherwise: GuestGpu's contended wall at the three instrumented sites by holder tag, the walker's
holds (`pl_wq_hold_*`; `pl_wp_hold_*` should be ~0 now), the spin-share lower bound. Scorer derived from `obs107.py`
by a `make_*.py` with the rule of fixtures (each term alone + each branch, mutants killed). Predictions to seal: tag 2
≈ 0; tag 1 ≥ 90 % of the contended wall; contended wall 150–300 µs a flip. **Rule in the seal:** if tag 1 carries
≥ 100 µs a flip, build `daslot` (§3); else the lock is finished as a lever (record, then §4).

## 3. `daslot` (ROADMAP record before code)

Per `design109.md` §A: publish-once hints (a source enters a hint only with a published compiled SRT; fingerprint and
class computed before), atomic hint/variant fields and `memo_generation`, `ahead_slots` behind an atomic pointer under a
new `ahead_queue_mutex`, a per-slot guard byte and a new state `AheadTaking` (move `slot.taken = 1` before the state
store), `QueueDrawAhead` takes `ahead_queue_mutex` instead of `m_mutex`. Knob `daslot` (0..2; 2 = verify: recompute the
slot key under the guard, `da_slot_bad`), counters `da_guard_n`, `da_guard_busy`, `da_q_taking_wait`, `da_hint_defer`,
`da_slot_bad`. Make the guard protocol and publish-once rules unconditional so the knob only switches the lock (safe
to flip mid-run). Runs: verify (`daslot=2`, 300 s; `da_slot_bad` = 0, `smemocheck` agreement as at `daslot=0`), then the
ship ABBA `daslot=0|1` (600 s, pinned, Δ`dt` bar) and video. Scorers derived by `make_*.py`, fixtures and mutants.

## 4. Other levers and debts

The mid-pass buffer uploads (session-109 audit: +1.7…3 render-pass splits a flip and `gpu_busy_us` +30…90 µs when the
prefetch hold goes) — a census of which buffers, whose CPU writes, why synchronous. `cspfree` code debts (re-check the
epoch mirror after the unlocked materialization; count "null source" apart from "moved"; one `PipelineCache` per
process). `dapin=1|3` under the pin. M3.2.

## 5. Traps that are live

1. During a sealed run the heartbeat makes NO tool call; every chain holds `C:/kyty/SEALED_RUN.lock`; kill stray
   `tail`/`grep` watchers (agents leave them) before a sealed run.
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included.
3. IDENTITY hashes the INSTALLED exe; copy each scored build before the next build.
4. A scorer's cross-check must match what the emulator reports: counters of the interval before the first
   `FrameTrace` row are never reported (session 110 `stl110`).
5. The main estimator of every new ABBA seal is the FULL block (or frames 10–89); the 60–88 window is printed as
   secondary (it caught arm-independent ~48 ms hitches in session 110). Do not add gains.
6. Python `Path.write_text` on Windows writes CRLF; bash heredocs with nested quotes break under the hook.

## 6. Deliverable

PLAN; records before actions; CODE → TEST → VERIFY → **adversarial audit before publishing**; one ROADMAP edit, FACTS
(`C:/kyty/s111/FACTS.md` → `docs/local-session-111.md`), `docs/next-session-112.md`, both game contexts, a short
`HANDOFF.md` block, the commit without push.

## 7. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; safety in scenes not
measured; additivity of gains.
