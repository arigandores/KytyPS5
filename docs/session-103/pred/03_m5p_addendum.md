# Session 103, sealed addendum 03 to pred/02 (M5′), written BEFORE any timing

`pred/02_m5p_bench.md` (6 183 B, `4035a9b0…`) is not edited. Nothing here moves the rule, the
threshold, the arms, the design or the verdict. Written after the offline build of every module of
arms A, V1, V2′ (`m5p/recompile.json`) and before `find`, `equal` or `bench` ran.

1. **Correction of a reported number (my misreading of a truncated listing).** pred/02 §1 says
   "STL 30 → 0 (S4 V2 → V2′)". The module bytes (md5 `ba653eb4…`) give: in the `s16_sass.py` window
   STL 30 → 9 (7 `STL` + 2 `STL.64`); over the full code 98 → 48 (A: 32); local memory 256 → 144 B.
   V2′ registers are 128 on S4, S5 and S8 (A: 96, 80, 96/107) with spills on S4/S8 — reported, part of
   the price, never deciding.
2. **P4′ "on the common items"** means: the items that are in session 102's X set (S2–S7, S9, S10)
   AND pass V-e for V2′ here; X of session 102 is recomputed on exactly that set from
   `C:/kyty/s102/m5/real/` when the set is smaller than those eight.
3. **V-a capture log** is `C:/kyty/s102/log_m5cap102b.txt` (the successful
   capture run; `log_m5cap102.txt` is the crashed first attempt and carries no `GpuClockPin` line).
4. **Float edge:** the comparison `CI_lo(X′ − 1) > 0.06` is evaluated as in the session-102 scorer
   (IEEE doubles); an exact 1.06 is not expected and would be reported with that caveat.
