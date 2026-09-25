# Session 116 — `mutlib` v4.1 (the ≤ 10-min seal made safe), then the next speed track from a clean phase breakdown

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 115 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–11 (item 10: v4 and its review; item 11: the
audit and the measures); `C:/kyty/s115/FACTS.md` (git `docs/local-session-115.md`); `docs/session-115/mutlib_v4/`
(README, ACCEPTANCE_V4.md, WORKFLOW_RESULT.txt with the review).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1 bdanarrow=0 titleasync=1`, installed build `d3a981a2…` (`7c73f26`: the presentation-ring fix
+ `titleasync=1`, seal 01 `chk115` PASS). Session 115: the startup crash on long shader preparation fixed and verified;
`mutlib` v4 cuts a full ABBA-size seal from ~70 to ~20 min; the ≤ 10-min selective path is barred until v4.1. 60 FPS stays
the direction without a route with a live estimate.

## Rule of the session

As since session 102: decisions in `ROADMAP.md` before the first action (also every change to a running workflow); a
sealed consequence is never set aside after its outcome; seals with fixtures and mutants (`mutlib` v4 frozen copy, FULL
runs, `--control --no-memo --work-dir C:/kyty/s116/work*`); **a sealed chain refuses while any process with `mutlib.py`
in its command line lives, and agents with heavy tasks are stopped before it**; never two heavy jobs at once; audit
before closing.

## Steps

0. **Harness root `C:/kyty/s116`**: port `enter_scene.py`, `gates_base.txt`, `run_safety99.py`, `procload.py` (add the
   `mutlib.py` process refusal), the pinned exe `kyty_emulator_d3a981a2.exe`.
1. **`mutlib` v4.1** (one workflow, ≤ 4 agents, small): (a) test-aware `--changed-from`: always select a mutant whose kill
   case in the PARENT's sealed report was changed or removed in the derived suite, every mutant absent from the parent's
   report, and fall back to a full run when the suites' shared fixture machinery (the writers, `make`) differs; plus the
   20 % sample; (b) static refusal of fixture replay when the suite uses `shutil.copy2`/`copytree`; (c) the other review
   MINORs where cheap; (d) timings with `--no-memo` on `ttl114b` (full and selected). Acceptance: the review's triples J
   and A plus one big suite; the target ≤ 10 min per ABBA seal.
2. **Clean phase breakdown** on `d3a981a2`: a sealed measuring run (pinned, `mutsite=1`/`pathlap`, no recording, nothing
   else on the machine) to split the GuestGpu CPU time per operation (~6.2 µs at ~5 300 draws + ~270 dispatches a frame).
3. **The next speed track** chosen by the rule (§2/§5) from step 2, recorded before code.
4. F2 (the flip mutex held ~2.4 ms per flip) stays a correctness debt unless its counters show waiting.

## Must not be claimed

60 FPS; that `--changed-from` is safe before v4.1 passes; that long cold preparations are verified; any speed number
measured beside another heavy job.
