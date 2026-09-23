# Session 104, sealed addendum 04: the adversarial audit and what it changes

Written after three audit lenses (reports in `C:/kyty/s104/audit104/`), before publication. `pred/01`–`03`
are not edited. No sealed verdict changes: `dawalk` SHIP stands, route A Stage 1 "A proceeds" stands,
the `reg104` screen reading stands.

## Tally

* **Recount — NOT REFUTED** on all six claims (own parser and statistics): `dwk104` Δcpu_net −458.4618
  (t −8.0003), Δdt −265.9487 (t −4.6458), 92 pairs, arming exact; `sh104` T4 +2 532.4918 (t 32.53);
  `mut104` INVALID on exactly 11 skipped draws (frame 2 330, with a 165.7 ms frame); `mut104b` G 5 683.1019,
  G^ 7 628.9515; `reg104` 31.1495 / 30.3760 / 6.1132; videos 3 886 / 3 917 frames, 0 glitches; seed 512 /
  638 verified by hashes. Notes: `dt` is vblank-quantised per row (medians 33.27 vs 33.26 ms) — the mean
  gain comes from the one-vblank share and fewer > 40 ms frames; carry-over −576 vs −341 by order
  (cancelled by ABBA to first order); G is likely conservative (≈ 600 µs of instrument time left in
  S_raw); `reg104` ran with the seed incompatible and one 212.9 ms hitch (conditions not matched).
* **Protocol — REFUTED narrowly.** **MAJOR: `reg104` ran while the design-review agent was reading and
  scanning files** (03:39–03:50 against 03:42–03:46), against `pred/01`'s "no other work on the
  machine" — a between-run screen whose reading (−2.1 %) could only have been pushed slower; it stands.
  Minors: `<fill>` fields left in `pred/02`/`pred/03` (the scorer→seal link is one-way; the reverse is
  commit `dbd6538`); the scorer prints a stale "RULE (G^ < 3000 …)" label (the code decides on the
  central G); verdict terms (P_mw, dI, C_TS, W_E, the 3 % area clause) set in the seal as ROADMAP item 6
  delegated; the `mut104` repeat was chosen after the invalid run's G (5 812.7, same direction) was
  printed; `pred/03` §5 said `gen_gates.py` regenerates `gates_base.txt` — **done instead by a one-pin
  byte edit (`dawalk=0` → `1`, 1 092 B, 99 names, sha256 `303a7849…`)** because today's `gen_gates.py`
  writes all 135 names and would change the harness's 99-name composition; IDENTITY in both scorers hashes
  the installed exe, so after the ship build (`61ae7347…`) the sealed scorers no longer admit the
  session's runs (acceptance is recorded in `runs104/`); `go104.sh` did not check results between runs.
* **The plateau claim — PARTLY REFUTED.** NOT REFUTED for Sky Garden (the mean is not quantised and
  follows GuestGpu work; stronger evidence: draws per interval grow with the interval, 2 884 / 5 252 /
  7 376 for 1 / 2 / 3 vblanks; across 351 ABBA blocks dt − GuestGpu CPU stays 0.70–0.84 ms while CPU
  goes 30.1 → 35.2 ms, crossing 33.3 ms with no plateau). **REFUTED: the mechanism** — GuestGpu DOES
  wait on flips: `R_WAIT_FLIP_DONE` (`pm4Handlers.cpp:2570` → `CommandProcessor::WaitFlipDone`,
  `graphicsRun.cpp:2468` → `FlipQueue::Wait`, `videoOut.cpp:1102`) once per frame, with two display
  buffers, so GuestGpu runs at most ~2 flips ahead; the depth-16 queue is irrelevant. The mean is free
  because this wait has slack while per-frame work exceeds ~20 ms (peak `lat_us` 19.7–20.3 ms). **REFUTED:
  the desert evidence** (`sky61d`, `sky60`, `sky63a` middle thirds mix a light 60 FPS phase with Sky
  Garden). **PARTLY REFUTED: "savings convert ~1:1"** — the ratio Δdt/Δcpu_net is 0.58 in `dwk104`
  (bootstrap 95 % CI 0.43–0.70; +196 µs of GuestGpu off-CPU time, t 7.6, cause not isolated) and 1.02 in
  `sh104`; speed-up estimates must use Δdt directly. **Route V closure stands for now, with the reason
  corrected:** closed while per-frame work > ~20 ms; it reopens below that (the double-buffer
  `WAIT_FLIP_DONE` then binds). **Also:** "20.1 % three-vblank frames" comes from unsettled early frames
  of short entries; steady windows have ≤ 1.3 % three-vblank and 9–14 % one-vblank frames.

## What the texts must say

The corrected mechanism, the removal of the desert evidence, Δdt as the measure of game speed (dawalk:
+0.8 % game speed from Δdt −265.9 µs, not from Δcpu), the regime bound on route V, the `reg104`
disclosure, and the `gates_base.txt` handling.
