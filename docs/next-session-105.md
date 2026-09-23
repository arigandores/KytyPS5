# Session 105 — "maximum FPS", track 1: cheap zero-code candidates by sealed ABBA with the bar on Δ`dt`; track 2: route A stage 3 as a design with one measurable milestone

**Read first:** `ROADMAP.md` §0.1 — the session-104 decisions (items 1–8), the audit's corrections to items
1–2, the session-104 addition and **the executor's decision after session 104** (two tracks; ship bar on
Δ`dt`); §4 (plateau, corrected), §6, §7 (session-104 rows); then `C:/kyty/s104/FACTS.md` in full (in git
`docs/local-session-104.md`) including §8, the design review `docs/session-104/designA_review.md`, and the
sealed texts `C:/kyty/s104/pred/01`–`05` (hashes in `SEALS104.txt`). Sealed texts are immutable.

**Open the report with these numbers:** Sky Garden steady mean `dt_us` ≈ 31.6 ms in the pinned `dwk104` arm
`dawalk=1` (31 618 µs; `cpu_net_us` 30 744; the unpinned default setup is not measured); game speed = 16 667 / mean `dt_us` ≈ 0.53×;
GuestGpu busy ≈ 97 %. 60 FPS stays the direction without a route with a live estimate. **Game speed is
measured by Δ`dt` directly** (the Δdt/Δcpu ratio was 0.58 for `dawalk`, 1.02 for `shadowresolve`).

## 1. The port, first

Write `s105_port.py` **fresh in `C:/kyty/s104/`** (`SRC = C:/kyty/s104`, `DST = C:/kyty/s105`), modelled on
`C:/kyty/s103/s104_port.py`. Never run a carried `*_port.py`. Advance chains by one; sealed texts grow
**35 → 40** (`pred/01_reg104.md`, `02_a_stage1.md`, `03_dawalk.md`, `04_audit_addendum.md`,
`05_claims104_addendum.md` land in `prev104/pred/`; **`04_audit_addendum.md` collides by basename with session
103's `04_audit_addendum.md` in `prev103/pred`** — handle like the s100/s101 `03_audit_addendum.md` case); r6/r7 gain the session-104
seal constants (`a104.py`, `dwk104.py` `PRED`); **`gates_base.txt` is now 1 092 B / 99 names / sha256
`303a784911cf…cbbf` with `dawalk=1`** (was `00c116dc…`); `gates.cpp` 135 entries, `ABSENT` 36 unless a
gate is added. Carry `a104.py`, `dwk104.py`, their tests, `go104*.sh`, `gates_dawalk1.txt`,
`gates_nodawalk.txt`, `gates_base.pre104ship.*` as archive (pinned to their seals; never re-run).

## 2. Track 1 — zero-code candidates (each: ROADMAP record → seal → ABBA with pin → video if shipping)

* **Ship bar (recorded after session 104):** Δ mean `dt` ≤ −100 µs with 2·SE excluding 0 (at the `dwk104`
  pair SD of 549 µs a 600 s run gives 2·SE ≈ 115 µs, so the effective bar is ≈ −115 µs); work and area in
  the controls; `cpu_net` reported; video pass (≥ 3 000 frames, 0 one-frame glitches) before the default
  moves; a new build's video pass after it.
* **Candidate 1: `dawalklead=1|2` with `dawalk=1`.** Session 60 (phase means of `log_sky60`, no ABBA, no pin):
  lead 2 gave `da_late` 0.00 and `da_miss` 202 against lead 1's 7.8–8.3 and 309–315. Under `dawalk=1` the M1 cooling cost is `da_take_us`
  +415, `da_miss` +219, `da_late` +8 a flip (`dwk104`). One run, 600 s, schedule
  `90+1800:dawalklead=1|dawalklead=2` (both arms `dawalk=1`), scorer derived from `dwk104.py` with the bar on Δ`dt`.
* **Candidate 2: the +196 µs of GuestGpu off-CPU time under `dawalk=1`** (Δdt/Δcpu 0.58). First read:
  where the walker thread runs (`dapin`, `DrawAheadWalk` thread affinity) and whether GuestGpu waits on
  `PipelineCache::m_mutex` (`plkstat` counters) — a sealed ABBA only if a lever exists in the tree.
* **Candidate list:** compile from ROADMAP §3/§7 and the environment-variable list every gate/knob that
  was measured without ABBA or clock pin, or closed "below threshold" when the threshold was set against
  60 FPS (e.g. `copywake=1` −33.4 µs `stg_pool_ns`); rank by expected Δ`dt` [I]; run at most two per session.

## 3. Track 2 — route A stage 3 (design only, one measurable milestone)

`designA_review.md` §3: stage 3 is the recording-context enabler at N = 1 (`RecordCtx`, explicit tick and
context through the ~43 `CurrentTick()` uses, `EXIT` on blocking calls from recorder threads), saving 0,
3–5 sessions. Write the design with the FIRST milestone small enough for one session and measurable by an
A/A-style ABBA (|Δ`cpu_net`| inside ±90 µs, video clean, entry-hang rate not worse over ≥ 60 entries).
Record the milestone in ROADMAP first. It must not displace track 1.

## 4. Traps that are live

1. No builds, driver compiles, scorer runs **or reading agents** while a sealed run is on the GPU
   (sessions 103 and 104 MAJORs). Check result files between chained runs (session 104 minor).
2. `gates_base.txt` now pins `dawalk=1`; any run on an older copy tests `dawalk=0`.
3. Scorers' IDENTITY hashes the INSTALLED exe: never rebuild between a run and its scoring (debt §7).
4. `KYTY_BVH_LOOP_CAP` ON by default (65 536); the loop-cap re-series (episode-aware) is still owed.
5. The first-character env class (`value[0] != '0'`) reads `false`/`off` as ON.
6. `AsyncPipelines: skipped draw` is a fatal marker in the ABBA scorers (a new permutation compiling inside
   the window invalidates the run; one repeat allowed).

## 5. Deliverable

PLAN with a measurable question; every decision recorded in ROADMAP first; CODE (or a default flip) → TEST →
VERIFY → **adversarial audit before publishing**. At the end: one ROADMAP edit, FACTS
(`C:/kyty/s105/FACTS.md`, mirrored as `docs/local-session-105.md`), `docs/next-session-106.md`, both game
contexts (`CLAUDE.md` = `AGENTS.md`) including the environment-variable list, a short `HANDOFF.md` block, the
mandatory commit without push.

## 6. Must not be claimed

60 FPS · a game-speed gain from Δ`cpu_net` alone · that route A will reach G (a model ceiling) · that the
loop cap is accepted · that the plateau statement holds below ~20 ms of per-frame work.
