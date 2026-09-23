# Session 103, sealed addendum 05: the claims lens (fifth audit lens, on the texts)

Written after the claims lens and before publication. `pred/01`–`04` are not edited. No verdict changes:
the series stays NOT ACCEPTED (A3), G (with a page table) stays CLOSED on an upper bound, the video pass
stays PASS (steady state).

**Verdict: REFUTED on the basis of the next route; corrected before publication.**

1. MAJOR — the vblank distribution first written into ROADMAP §0.1/§7, FACTS and the plan (86/13/1 %,
   from the last 300 frames of five logs) does not reproduce over the scene window of all 67 entries
   (37 119 frames): **79.3 / 20.1 / 0.5 %**, medians `dt_us` 33.5 ms, `cpu_gpu_us` 32.9 ms, `gpu_busy_us`
   12.6 ms. Replaced everywhere.
2. MAJOR — "the vblank grid quantises the CPU frame / a late frame waits almost a period" was stated as a
   basis; the data do not show it: `cpu_gpu_us/dt_us` = 0.981 on two-vblank and 0.980 on three-vblank
   frames (48.7 ms on 50 ms frames). Recast as a hypothesis [I] with both readings; a step (b′) measuring
   the three-vblank tail was added to the plan.
3. MINOR — the goal was stated as changed ("60 FPS no longer a direction"); the executor may not change
   the goal. Recast: 60 FPS has no route with a live estimate; the work continues on "maximum FPS".
4. MINOR — "G CLOSED" unqualified in places, "route E exhausted" beyond `pred/04` (R1 ≤ 3 % [I] not
   closed; a flat mirror unpriced): qualified everywhere.
5. MINOR — whole-dispatch leftovers (entries 32, 36 also unequal; "three whole dispatches" in
   `ent103_42` unverifiable): removed.
6. MINOR — disclosure gaps (six of seven trip entries inside the overlap; "drafted" vs "applied"; the two
   amendment changes biased to CLOSE missing from ROADMAP): added to ROADMAP and FACTS.
7. MINOR — §9 undercounted the real-path changes and did not book the seed incompatibility as a
   regression: corrected.
8. MINOR — small inaccuracies (553 files incl. 12 without GCN; M4 withdrawn, not done; S2 registers 72/70;
   the ROADMAP §7 "машинерия BDA" row stale; the numpy CI shift): corrected.
