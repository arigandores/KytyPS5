# Session 109 — "maximum FPS", track 1: `cspfam` v2 (the prefetch skip without the first-contact window) with a powered guard, then the walker's `QueueDrawAhead` off `PipelineCache::m_mutex`; M3.2 code without run time

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 108 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–9 and **the executor's decision after
session 108**; §6; §7 (session-108 rows); then `C:/kyty/s108/FACTS.md` in full (in git `docs/local-session-108.md`)
incl. §7, and the sealed texts `C:/kyty/s108/pred/01_cspfam.md` and `02_audit108.md` (hashes in `SEALS108.txt`),
and the audit report `C:/kyty/s108/audit108/AUDIT108.md`. Sealed texts are immutable.

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3
cspfam=0`: mean frame ≈ 31.0 ms (≈ 0.54× game speed). Kept in the 103–108 cycle at the pin: `dawalk=1` (−265.9 µs),
`dabatch=8` (−169.3 µs) — not additive (vblank-quantised). `cspfam=4` measured −141.8 µs (CI [−246, −38]) but was
rolled back: with the compute precache off it let through 6 dispatch-time compiles against 3. Before `cspfam` the
walker held `m_mutex` behind ~99 % of GuestGpu's ~420 µs a flip of contended wall: `QueueDrawAhead` ~58 %, the
compute prefetch ~41 %. 60 FPS stays the direction without a route with a live estimate.

## 1. The port, first

Write `s109_port.py` **fresh in `C:/kyty/s108/`** (`SRC = C:/kyty/s108`, `DST = C:/kyty/s109`), modelled on
`C:/kyty/s107/s108_port.py` (sha256 `cb104f40…`). Never run a carried `*_port.py`. Advance chains by one; sealed
texts grow **50 → 52** (`01_cspfam.md`, `02_audit108.md` land in `prev108/pred/`; check basenames); r6 gains
`fam108.py` `PRED` (bare literal with `PRED_SHA`/`PRED_BYTES`); `gates_base.txt` unchanged (1 092 B / 99 names /
`303a7849…`; `cspfam` ABSENT, default 0); `gates.cpp` 138 entries (111 + 27), `ABSENT 39` — +1 each if v2 adds a knob
row before the port. Carry the session-108 scorers, tests, `go108*.sh`, `gates_fam4.txt`, `gates_fam0.txt`,
`check108.py`, `check108r.py` as archive; do NOT carry `kyty_emulator_*.exe` (they stay in `C:/kyty/s108`) nor
`audit108/p_*.json` (9.5 MB each; leave in s108). Session-108 files the global `s108 → s109` rewrite breaks, to be
classed explicitly: `seal108.py`, `facts108_fix.py`, `roadmap108_close.py` (one-shots), `check108.py`/`check108r.py`
(pinned to builds, read `C:/kyty/s108` logs), everything under `audit108/` (reads `C:/kyty/s108/log_*`),
`make_fam108.py` (anchored on `C:/kyty/s107/dab107.py`), `test_fam108.py` (writes `C:/kyty/s106_stage/fx_fam108`).

## 2. `cspfam` v2 (ROADMAP record before code)

Design: a process-wide atomic count of compute-pipeline CREATIONS — incremented where `m_compute_pipelines` gains an
entry, both by the prefetch path and by `GetComputePipeline`'s synchronous path — joins the table's stamps (with the
programs-epoch mirror and `ShaderRegistrations()`); any move clears every streak, so during a load burst the walker
keeps prefetching and the skip engages only after K "already built" rounds with no creation anywhere. Decide in the
record whether v2 changes the meaning of the existing knob (then say so explicitly; the seal of `fam108` refers to v1)
or gets a new LAST row. Keep `cs_sync_new`/`cs_sync_wait`. Fixtures: the rule of decision after 107 item 2 plus the
two survivors of the session-108 audit (GATEARM's ABBA order with `abba=1`; `spin_gpu_us` in `cpu_net`).

Runs, each with its seal before it (pinned; nothing else on the machine; the heartbeat makes no tool call):
1. **Powered guard as an ABBA of ENTRIES** (first, because it decides whether (2) is worth running): 8 entries into
   Sky Garden with `KYTY_PIPELINE_PRECACHE=gfx`, order A B B A A B B A (A = `cspfam=0`, B = v2 at K = 4), 150 s each,
   rule Σ(`cs_sync_new` + `cs_sync_wait`) over B ≤ Σ over A + 2, all rows incl. the load; publish per entry.
2. **Frame-time ABBA** `cspfam=0|v2`, 600 s, shipping configuration (precache on), the Δ`dt` bar (≤ −100 µs, 2·SE
   excluding 0), controls of the `fam108` lineage incl. `SYNC_COMPILE`, video with the pin on SHIP_PENDING_VIDEO. On
   SHIP: ROADMAP first, default, new build, its pinned video checked by a script pinned to its sha
   (`check108r.py`-style, with the audit gaps closed).

## 3. Then: the contention left, and `QueueDrawAhead` off the lock

Observation `obs109` (300 s, pinned, `plkstat=1`, defaults incl. v2 if shipped): GuestGpu's contended wall by
holder tag, the walker's holds. Scorer derived from `obs107.py`. Rule in the seal: if tag 1 (`QueueDrawAhead`)
carries ≥ 100 µs a flip, build the §3 candidate; else the lock is finished as a lever.
Candidate design (record before code): `QueueAhead` (`pipelineCache.cpp` ~2628) mutates the ahead table —
`ahead_slots` (non-atomic `walk`, `uses`, `taken`, `pixel`, `source`, …), `ahead_hints`, `ahead_walk`/`ahead_fresh`,
lazily built `plan_class` — that GuestGpu's `AheadTake` (in `GetGraphicsPrograms`, under `m_mutex`) reads and
writes. Answer from the source: every writer/reader of each field and its lock; `SourceEntry`/`PlanClass` lifetime
(can the walker hold pointers without `m_mutex`?); `memo_generation`/`ahead_hints` writers; whether a dedicated
`ahead_mutex` (walker: only it; GuestGpu: nested inside `m_mutex` around `AheadTake`'s slot operations only) shrinks
GuestGpu's exposure from every `m_mutex` acquisition to one short one per draw; the lock-free alternative (CAS on
`state`) for the record. Knob (e.g. `daqlock`, default 0, LAST row, `check_gate_order.py`). Seal: ABBA, pinned, the
Δ`dt` bar; **900 s** if the observation predicts < 150 µs.

## 4. Route A M3.2 (code only until the track-1 runs are scored)

The binding-preparation phase takes the buffer; `StreamBuffer::Commit(tick)`; the `ctxtick=0` branch deleted;
asserts at the three `NextTick` sites; `ctx_rec_block` coverage; a `ctx_midsub` positive control; correct the stale
`gates.h` `dabatch` comment. NOTHING built into `C:/kyty/build/install` between a sealed run and its scoring; copy
every scored binary before the next build.

## 5. Debts that stay open

`dapin=1|3` re-measure under the pin (incumbent `dapin=3`, its SHIP branch a no-op). `gpu_busy_us` +87.5 µs in the
`cspfam=4` arm (cause [U]). `cs_sync_*` exist only under `KYTY_FRAME_TRACE`.

## 6. Traps that are live

1. During a sealed run the heartbeat makes NO tool call (its prompt now says so); every run chain holds
   `C:/kyty/SEALED_RUN.lock`. No builds, compiles, scorers or reading agents while a run is on the GPU; kill stray
   `tail -F`/`grep` watchers before a sealed run (`tasklist | grep -E "tail|grep"`).
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included.
3. Scorers' IDENTITY hashes the INSTALLED exe: never rebuild/install between a run and its scoring.
4. A guard needs exposure: with the startup precache on, every known permutation is built before the first frame,
   so `cs_sync_*` cannot fire — test first-contact behaviour with `KYTY_PIPELINE_PRECACHE=gfx`.
5. `plkstat`'s wait is the whole acquisition wall; its spin share (≥ 0.75) is a lower bound.
6. Frame time is vblank-quantised: gains are shifts between 1- and 2-vblank frames; not additive.
7. `AsyncPipelines: skipped draw` is a fatal marker in the ABBA scorers (one repeat allowed).
8. Check a knob's CURRENT default in `gates.cpp` before proposing it (`cspfam` is 0 again since `01f0c79`).
9. `normalize_eol.py` chokes on renames and untracked directories: stage first, or normalise per file. Bash heredocs
   with nested quotes break under the hook: put scripts in files.

## 7. Deliverable

PLAN with a measurable question; every decision recorded in ROADMAP first; CODE → TEST → VERIFY → **adversarial
audit before publishing**. At the end: one ROADMAP edit, FACTS (`C:/kyty/s109/FACTS.md`, mirrored as
`docs/local-session-109.md`), `docs/next-session-110.md`, both game contexts (`CLAUDE.md` = `AGENTS.md`) incl. the
environment-variable list, a short `HANDOFF.md` block, the mandatory commit without push.

## 8. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; a prefetch skip safe in
scenes or contents not measured; additivity of gains.
