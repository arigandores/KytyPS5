# Session 119 — route A at W = 2: re-measure G₂ on the current build (two sealed ABBA runs, zero emulator code) and removability designs for the GuestGpu micro-track candidates ≥ 1 ms

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 118 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–6 (item 5: the `spk118` outcome; item 6:
the audit and the G₂ rule for this session, fixed to the measured f₂ = 0.555); `C:/kyty/s118/FACTS.md` (git `docs/local-session-118.md`);
`docs/session-104/designA_review.md` §1–3 (stage 1 and the G rule); `C:/kyty/s104/pred/02_a_stage1.md` and the scorer
`C:/kyty/s104/a104.py` (the stage-1 parent for whole-line derivation).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1 bdanarrow=0 titleasync=1 spine=0 slicecen=0`, installed build `d3a981a2…` (`7c73f26`).
Session 118: the shadow spine passes K5 and the carry (0 of 25 904 plans), K3 largest run 0.16, **K4 W = 2 47 ‰ PASS,
W = 4 325 ‰ FAIL ⇒ W = 2 is route A's ceiling**; the two halves of the cut are 555 ‰ / 445 ‰ of the elements, so
from the session-104 members G₂ = 4 827 − T₂ µs [I], [2 295; 4 827] for T₂ ∈ [0; 2 532] — the break-even tax is
1.83 ms, where T₂ is expected, so it is re-measured before stage 3. Arm M levels a frame: witness verify 1.21 ms,
`bl_res` 3.21, `bl_buf` 3.87, `bl_img` 1.09, `mh_emit` com 2.38 / rt 1.57 / vtx 1.36 / rec 1.23. 60 FPS stays the
direction without a route with a live estimate.

## Rule of the session

As since session 102: every decision in `ROADMAP.md` before the first action; a sealed consequence is never set aside
after its outcome; seals with fixtures and mutants (`mutlib` v4.1 frozen `docs/session-116/mutlib_v41/`, FULL runs
`--control --no-memo --work-dir/--cache-dir C:/kyty/s119/...`); edit scripts write LF (`write_bytes`), fixture suites
end with `ALL OK`; mutation runs and code reading may overlap each other, never a sealed run; audit before closing.

## Steps

0. **Harness root `C:/kyty/s119`**: port `enter_scene.py` (ROOT s119), `gates_base.txt`, `run_safety99.py`,
   `procload.py`, `launch_run.py`, the pinned `kyty_emulator_d3a981a2.exe`.
1. **G₂ re-measure (ROADMAP 118 item 5 (1)), zero emulator code, on the installed `d3a981a2`:** derive the scorer from
   `a104.py` by whole lines (W = 2: f₂ = 0.555, the tax from `shadowresolve=0|1`); two sealed pinned 300-s ABBA runs:
   (1a) `mutwide=0|15` with `mutsite=1 amut=1 plkstat=1 pathlap=1` in both arms ⇒ `S`, `S_ctx`, spine (`da_walk_us` −
   `da_queue_us`); (1b) `shadowresolve=0|1` ⇒ T₂. **Rule (recorded in items 5–6):** G₂ = `cpu_net` − [`S_ctx` +
   f₂·(`cpu_net` − `S_ctx`)] − spine − T₂ with **f₂ = 0.555** (the sealed `spk118` median `k4_w2_fmax`) and **spine =
   max(`da_walk_us` − `da_queue_us` of (1a), 959 µs)**; **G₂ < 3 000 µs ⇒ route A closed for maximum FPS; ≥ 3 000 ⇒
   stage 3 resumes** (M3.2 …; first gain at stage 5, W = 2); one repeat per NOT_ADMITTED run. Check before the seal that the
   stage-1 knobs still mean what `a104.py` assumes (`mutwide` bits, `shadowresolve` readers, `amut`, `plkstat`), that
   `pathlap`'s own price is subtracted as in s104, and that the s104 scorer's printed "RULE (G^ …)" leftover is removed.
2. **Removability designs (item 5 (2)), by code reading, not during a sealed run:** for each arm-M candidate ≥ 1 ms —
   the witness verify (`AheadTake` phase, 1.21 ms), image resolution `bl_res` (3.21), buffer part `bl_buf` (3.87), the
   image loop `bl_img` (1.09), the `mh_emit` parts com / rt / vtx / rec — what exactly repeats per draw, what a memo or a hoist would need to be correct
   (the witness), and a CEILING of the removable part with the arithmetic; recorded in ROADMAP before any code. A speed
   track opens only on a measured ceiling ≥ 1 ms; a ceiling that needs a new counter goes into one measurement build.
3. **Consequences:** route A closed ⇒ the next sessions go to the micro-track designs with a ceiling ≥ 1 ms; route A
   continues ⇒ stage 3 (M3.2) is planned in `next-session-120.md` beside the best micro-track.
4. Audit, close (FACTS, local-session-119, next-session-120, CLAUDE.md = AGENTS.md, HANDOFF, LOOP_STATE, commit; no push).

## Must not be claimed

60 FPS; any gain of route A before stage 5 measures one; that the spine carries state on another thread (the carry was
tested on GuestGpu between consecutive plans); any speed number beside another heavy job; a ceiling from the arm-M levels
alone (a level is not a removable part).
