# Session 104, sealed addendum 05: the claims lens on the final texts

Written after the fourth lens (claims) and before publication. `pred/01`–`04` are not edited. No verdict
changes: every headline number reproduced (dwk104, sh104, mut104b terms, reg104, videos, seed, hashes,
the plan's port numbers).

**Verdict: REFUTED narrowly (presentation); corrected before publication.**

1. MAJOR — ROADMAP §0.1 items 1–2 kept the withdrawn claims unstruck (the 16-deep queue as the mechanism,
   the desert evidence, "≈ 1:1 (0.97–0.98)", "GuestGpu does not wait for flips") and the uncorrected
   "30,7…31,9 мс при 10–16 %": struck inline with "(отозвано …)", numbers corrected to 31,15…31,83 / 9,7–13,5 %
   (also in the §4 note).
2. MINOR — "below ~20 ms the double buffer binds" stated as fact in ROADMAP §0.1/§4/§7 and FACTS §9:
   tagged [I] (peak `lat_us` 19.6–20.3 ms steady, outliers 21.6–25.4 ms).
3. MINOR — FACTS's "≤ 1.3 % three-vblank" contradicted `vid103` 7.2 % / `sh104` 5.1 %: qualified to runs
   without recording or instruments.
4. MINOR — "+0.8 %" without the pin qualifier (ROADMAP addition, HANDOFF, plan's "shipped default"):
   qualified (ABBA with the GPU clock pinned; the unpinned default setup, where DRS moves, not tested).
5. MINOR — HANDOFF block lacked the `reg104` MAJOR, the `gates_base.txt` handling, the Sky Garden scope and
   the "slack" wording: added.
6. MINOR — ROADMAP item 8(a) said `gates_base.txt` still pins `dawalk=0`; the hand edit (05:07) came first:
   annotated; `gates_base.json` rewritten too; the archived scorers pin `GATES_SHA` `00c116dc…` as well as the
   installed exe.
7. MINOR — session-60 numbers: "−0.3…−1.4 % CPU a draw" belongs to `dawalklead=2` (lead 1: +2.4 / −0.4 /
   −1.6 %); `da_miss` 202 vs 309–315, `da_late` 0.00 vs 7.8–8.3 (phase means of `log_sky60`): corrected.
8. MINOR — `reg104` had 21 `AsyncPipelines: skipped draw` and one held flip: disclosed.
9. MINOR — stale route-A statements (§0.1 table "20,8 мс = 30 FPS", §2 A "ЗАКРЫТ"): annotated with the
   session-104 status.
10. MINOR — the ship bar's power: at the `dwk104` pair SD (549 µs) a 600 s run gives 2·SE ≈ 115 µs, so the
    effective bar is ≈ −115 µs: stated.
