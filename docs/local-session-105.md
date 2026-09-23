# Session 105 — candidate `dawalklead=2` KEPT at 1; route A milestone M3.1 (the command buffer names its owner and tick) ACCEPTED and `ctxtick=1` made the default

**Single source of truth for session 105.** Mirrored into git as `docs/local-session-105.md`.
Harness root `C:/kyty/s105`. Everything below is measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned: mean `dt_us` ≈ 31.6 ms (`dwk104` arm `dawalk=1`), game speed ≈ 0.53×;
screens this session (pinned, 180 s, middle third of rows): `reg105a` 30.82 ms on
`61ae7347…`, `reg105b` 30.80 ms on `8de4a93b…`. 60 FPS stays the direction without a route with a live
estimate. **No speedup this session** (M3.1 saves nothing by design; candidate 1 did not ship).

---

## 1. Result

1. **Candidate 1 — `dawalklead=2` under `dawalk=1` (sealed `pred/01_dawalklead.md`): KEEP 1.** `lead105` (600 s,
   pinned, ABBA, 94 pairs, ADMITTED): Δ mean `dt` **−61.0 µs** (2·SE 115.5, t −1.06) — the ship bar −100 µs
   not met; Δ`cpu_net` −79.6; Δ`da_late` −7.9 and Δ`da_miss` −137.8 a flip (predicted), Δ`da_take_us` +69.4
   (missed prediction): the cooler M1 results do not reach the frame.
2. **Route A, Stage 3, milestone M3.1 (design `docs/session-105/designA3_stage3.md`, decision recorded in
   ROADMAP before the code, sealed acceptance `pred/02_m31.md`): ACCEPTED on P1–P4; `ctxtick=1` is the default.**
   `CommandBuffer` keeps its owner scheduler and tick (set in `BeginCommand`); the draw/dispatch path uses
   `buffer.Scheduler()`; the ownership tick of `DescriptorHeap::Commit/CommitRing` and `MergeCostCensus` is
   explicit, chosen by knob `ctxtick` (0 old expression, 1 `buffer.Tick()`, 2 +checks, 3 +EXIT);
   `RenderContext::AgeTick()` names the age clock. Executor uses of the global scheduler/tick: 30 → 2.
   Nothing under `src/graphics/shader/**` (translation cache warm).
   * **P1** `ctx105` (300 s, `ctxtick=2`): Σ`ctx_chk_bad` 0, Σ`ctx_rec_block` 0, no `CtxCheck:` line; median
     `ctx_chk_n` 8 509 per flip vs draws + dispatches 5 627 (no flip below; min ratio 1.19). **`ctx_midsub` = 0**
     — credible (the counter is reachable, and no `stream-wrap`/`sanitizer-slot`/`download*` submit row exists
     in any session-105 log), but **never tested against a known positive** (§7 item 1).
   * **P2** `abb105` (900 s, pinned, ABBA `ctxtick=0|1`, 146 pairs): **ADMITTED after a scorer fix** (sealed
     `pred/03_scorer_fix.md`: the derived scorer did not parse `ctx_chk_*`, so its "instruments dark" control
     failed mechanically; in the raw log both fields are 0 on all 28 791 lines); |Δ`cpu_net`| point **62.6 µs**
     ≤ 90 (2·SE 91.2), Δ`dt` −66.3 µs (t −1.36). Not a proof of equivalence.
   * **P3** video `vct105` (`ctxtick=1`): 3 925 frames, 0 one-frame glitches — **ran WITHOUT
     `KYTY_GPU_CLOCK_PIN=1`, a deviation from seal 02 §1 found by the audit** (the video decides no timing).
     **P4** 10/10 entries at `ctxtick=2`, `ctx_chk_bad` 0, no hang. **Screen** `reg105b` vs `reg105a`: CPU per
     draw −0.09 %.
   * **Predictions (seal 02 §3):** Q1 P1–P4 pass — HIT · Q2 `ctx_midsub` in [0.5, 20] — **MISS** (0) · Q3 |Δcpu_net|
     ≤ 60 µs — **MISS** (62.6) · Q4 screen within ±2 % — HIT.
   * Ship build `810bb54b…` (`de9c754`), video `vid105` with the compiled default: 3 977 frames, 0 glitches.

## 2. Harness

`C:/kyty/s105`, ported by a fresh `C:/kyty/s104/s105_port.py`: `PRECONDITIONS PASS: 5 root constructs; 40
sealed texts (38 land in prev104/pred, 2 stay in carried prev103/pred and prev100/pred); 29 live paths (18
files) + 9 expression paths (7 files); gates 1092 B / 99 names (sha 303a7849..., dawalk=1); gates.cpp 135
entries (111 gates + 24 knobs); ABSENT 36` → `PORT DIAGNOSTIC: clean; carried=6235 ledger=57 skipped=33`.
New: `lead105.py` (from `dwk104.py`), `ctx105.py` (from `lead105.py`), `check105.py`, `go105.sh`,
`go105b.sh`, `gates_ctx1.txt`, `gates_ctx2.txt`. `gates.cpp` now yields 136 entries (111 + 25 knobs: `ctxtick`
added), `ABSENT` becomes 37 in the next port.

## 3. Source, builds, provenance

Commits: `bfff4c3` (seal 01 + scorer), `38bfda2` (candidate-1 result + M3.1 decision), `4763c49` (M3.1
source), `f4c2f54` (seal 02 + scorers), `418e491` (addendum 03), `e3a764b` (acceptance + default decision),
`de9c754` (`ctxtick` default 1), the session commit. Builds: `8de4a93b…` (M3.1 at default 0; all acceptance
runs), `810bb54b…` (default 1; `vid105`). `check_gate_order.py` clean (Knob 25/25). `shader_cfg_tests`: the
same single failure as HEAD (1 of 127). No push.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `lead105` | `dawalklead=1|2` ABBA 600 s | ADMITTED, Δdt −61.0 ⇒ KEEP |
| `reg105a` / `reg105b` | screen, old / new binary | CPU/draw −0.09 % |
| `ctx105` | P1 checks, `ctxtick=2` | PASS, `ctx_midsub` 0 |
| `abb105` | P2 A/A `ctxtick=0|1` 900 s | ADMITTED (after the scorer fix), 62.6 µs ≤ 90 |
| `vct105` | P3 video `ctxtick=1` | 3 925 frames, 0 glitches |
| `ect105_01…10` | P4 entries `ctxtick=2` | 10/10, no hang |
| `vid105` | ship-build video | 3 977 frames, 0 glitches |

## 5. Next

Track (1) item 2 first (the +196 µs of GuestGpu time off-CPU under `dawalk=1`: where it goes, then a
candidate); M3.2 (binding-preparation phase takes the buffer; `StreamBuffer::Commit(tick)`; the audit's
asserts and the `ctx_midsub` positive control) is written alongside but takes no measured run time before
track (1) has had its run. Plan: `docs/next-session-106.md`.

## 6. Proved, and not proved

**Measured.** `dawalklead=2` does not shorten the mean frame by the bar. M3.1's checks are clean, its A/A
point is within 90 µs, video and entries clean. **Not proved.** Equivalence of `ctxtick=1` (P2 is a point
bound); that `ctx_midsub` can fire; any speedup; 60 FPS.

## 7. Adversarial audit

Two lenses (recount + protocol; code review of `4763c49` and `de9c754`), sealed as `pred/04_audit105.md`
(5 412 B, `2853aa9c…`). **Recount CONFIRMED** (every number above reproduced by independent code, blocks
from `blk=` cross-checked with `GateArm`). **Protocol HOLDS** (ROADMAP-first for all three decisions, seals
before runs, nothing else ran during sealed runs). **Code NOT REFUTED** (`buffer.Tick()` equals the render
`CurrentTick()` at every ownership site; `buffer.Scheduler()` is always the render scheduler; `ctxtick=0`
equals the old code). No FATAL or MAJOR finding. MINOR findings and their handling:

1. `ctx_midsub` = 0 without a positive control; the part before the render mutex is not counted → positive
   control owed before Stage 5 publishes mid-operation submits.
2. `check105.py` summed the µs group of `ctx-mid:` rows (moot: 0 rows in every log).
3. Checks prove tick equality only; "stamp = tick this buffer signals" is not checked independently → assert
   at the three `NextTick` sites in M3.2.
4. `ctx_rec_block` covers seven APIs, not `WaitPriorityOperations`/`Drain`/`WaitAsyncCopies`/`queue_mutex`.
5. The cost of `ctxtick=1` is bounded only by the A/A point (62.6 µs), not measured on its own.
6. Row renaming at `ctxtick ≥ 2` would drop renamed `host-read` rows from exact-name scorers.
7. The one-line test edit never compiled (target not built by `build_tests.cmd`).
8. The P2 re-score is asymmetric (could only turn a favourable estimate into PASS); the dry run on `lead105`
   had already printed `[FAIL] INSTRUMENTS_DARK` → rule: a derived scorer runs on a fixture carrying every
   new field before sealing.
9. Fixed scorer and `runs105/ctx105_*` not in git → in the session commit.
10. `vct105` without the clock pin (above).
11. Predictions unpublished → published above (Q2, Q3 MISS).
12. Stale scorer labels (`dwk104.py`); outputs do not hash their scorer.
13. Judgement: M3.1 (zero saving) took the run time while track (1) item 2 was not started → ROADMAP decision:
    session 106 runs track (1) item 2 first; M3.2 takes no measured run time before it.
