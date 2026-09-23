# Session 103, sealed addendum 04: the adversarial audit and what it changes

Written after the four-lens audit (reports archived in `C:/kyty/s103/audit103/`), before publication.
`pred/01`–`03` are not edited.

## Tally

* **Recount — NOT REFUTED.** Own code reproduces X′ = 1.2934 [0.2910, 0.2946], L = 1.0201, A/B =
  1.0027, every per-item median, the event mapping (3 355 events), the Williams order of all 20
  rounds, V-e (S1, S8 fail; share 0.221), the series verdict (A3 FAIL only; 2 875 168 trips in 7
  entries; `bl_near` 387 072 all in `ent103_42`; worst 0.347 s) and the video (3 842 frames, 0
  glitches). A numpy bootstrap moves the CI by ~0.001 — immaterial.
* **Code — REFUTED, narrowly, on a descriptive claim.** No code defect invalidates a verdict (the
  capped modules validate; 9/9 loops guarded; one budget; the trip path ran on the driver; default-off
  identity holds; the lean path is correct). **Withdrawn: "trips always cover whole dispatches"**
  (FACTS §1.1/§2.3, ROADMAP item 4): entries 22, 30, 49 have readbacks that are not multiples of a
  dispatch (e.g. `ent103_30` total 149 536 = 2 336.5 groups of 64), so some groups tripped one wave
  and finished the other. The inference built on it ("invalid acceleration-structure data during
  level load") loses that support. Minor findings recorded: the tail copy is not ordered against
  later atomics (per-readback attribution can split; totals exact), `bl_*` read 0 without FrameTrace,
  32-bit wrap stops reporting, trips uncounted in a program without a fault binding, `strtoul`
  parsing traps, the pre-existing non-atomic fault-bit store now hit by whole-dispatch flushes.
* **Fidelity — NOT REFUTED on the CLOSE; REFUTED on the size.** **X′ = 1.2934 is an UPPER bound, not
  the price of G's BDA path**: V2′ keeps the page-crossing slow path (named in the ROADMAP §7 row that
  decision (б) cited), the per-group dword fallback, the run-time alignment test applied to PER-LANE
  addresses (divergent: S7 worse under V2′ 2.08 than V2 1.79), and page lookups repeated per block.
  Removing the slow path and the fallback in the SPIR-V brings S4/S5/S8 from 128 to 96 registers.
  The auditor's estimate for G without those artefacts: **X_G ≈ 1.09–1.17 [I]**, still above 1.06;
  the CLOSE flips only if S7 under G ≤ ~1.15 and every other item ≈ L + 1 %, implausible with
  per-access page lookups in S7's loop. The CI describes the bench, not G. The CLOSE covers G with a
  page-table BDA path, not a flat device mirror of guest memory (a different design, not priced).
* **Protocol — NOT REFUTED, one MAJOR disclosure.** **The M5′ offline builds ran DURING the sealed
  series** (S4 probe 01:44–01:52, `m5p_recompile.py` with real driver compiles 02:03–02:38),
  overlapping up to 53 of 67 counted entries (six of the seven trip entries) and the video pass,
  against `pred/01` §2 "the GPU otherwise idle". NOT ACCEPTED stands (conservative); the "0 of 67"
  was collected under that disturbance. Also: the loop-cap/env code was written (not only drafted)
  before the ROADMAP record, but first built after it; the M5′ amendment changed "a constant null
  base" to "read once per invocation" and dropped "no reloads after stores" while calling the rest
  "as recorded" (both bias V2′ toward CLOSE); the keep-ON decision is not a breach (the seal gives no
  consequence for NOT ACCEPTED) but its rationale over-reaches — `pred/01` §4 licenses "rate below
  6.67 % at ~99 %" only for an ACCEPTED series, so that sentence is withdrawn from "Proved"; the
  M5′ scorer checks `pred/02` and the parents, not `pred/03`; the pre-fix identity sweep left no
  artefact (overwritten).

## What stands

* G CLOSED by the recorded rule, published as: X′ = 1.2934 is an upper bound; the CLOSE rests on the
  inference that removable artefacts cannot bring it to ≤ 1.06 (auditor's estimate 1.09–1.17 [I]).
* The loop cap: NOT ACCEPTED (A3); 0 hangs in 67 entries observed (not a licensed rate); ON by
  default by the recorded decision; whole-dispatch wording and the mechanism inference withdrawn.
* The video pass: PASS for the steady state only (no trip was on screen).
* ROADMAP §6: the session's one real-path change did not pass its sealed A/B-equivalent — by §6 the
  session did not ship an accepted change.
