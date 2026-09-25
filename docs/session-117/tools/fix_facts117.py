"""Session 117 close: FACTS and next-session-118 follow the audit (ROADMAP item 15)."""
from pathlib import Path

f = Path('C:/kyty/s117/FACTS.md')
s = f.read_bytes().decode('utf-8')


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)


rep("""# Session 117 — lock-contention and GuestGpu micro-tracks closed by the record; back to route A (parallel command-stream processing), stage 4 first: the shadow spine is built and passes its sealed test (0 mismatches in 19.1 M compares, 0.61 ms a frame on GuestGpu); a full `mutlib` v4.1 seal run costs 42 min; no speed-up of the game shipped""",
    """# Session 117 — lock-contention tracks closed; route A (parallel command-stream processing), stage 4 part 1: the shadow spine is built and passes its sealed test (0 mismatches in 19.1 M compares; self-timed 0.61 ms a frame on GuestGpu, a lower bound); a full `mutlib` v4.1 seal run costs 42 min; the audit reopened the GuestGpu micro-track candidates; no speed-up of the game shipped""")
rep("""3. **Micro-tracks on the GuestGpu thread exhausted by the record (item 3):**""",
    """3. **Micro-tracks on the GuestGpu thread "exhausted by the record" (item 3) — RETRACTED by the audit (item 15):**""")
rep("""   (the shadow spine, the cheapest test able to close the route) before the rest of stage 3.**""",
    """   (the shadow spine, the cheapest test able to close the route) before the rest of stage 3.** The audit found the
   citation wrong: session 89 put the witness verify at 1.03–1.06 ms (≥ 1 ms), the `mh_emit` parts were never checked for
   a removable part, image resolution (~2.6 ms) is bounded only by its repeat-skip mechanism — these candidates are
   re-measured on the current build in session 118 together with stage 4 part 2.""")
rep("""   **spine 608.0 µs a frame on GuestGpu** (bar 1 200),""",
    """   **spine 608.0 µs a frame on GuestGpu by its own timer** (bar 1 200; median 555, p99 942, max 1 155),""")
rep("""**Proved:** a second pass over PM4 through the real register handlers reproduces the register state before every
draw/dispatch of Sky Garden within a submission, at 0.61 ms a frame on GuestGpu (1.8 % of the frame), and would fit on the
walker thread.""",
    """**Proved:** a second pass over PM4 through the real register handlers reproduces the register state before every
draw/dispatch of Sky Garden within a submission; its own timer reads 0.61 ms a frame on GuestGpu and it would fit on the
walker thread even at three times that. **Not proved:** the frame-level price (the in-run control arm 2 − arm 0 shows the
self-timers missing ~0.55 ms of what they add; there was no `spine=0` arm); """)
rep("""## 5. Audit

(filled after the audit agents report)""",
    """## 5. Audit (item 15)

Two agents, own parsers. **Recount: every number of item 14 and of the score CONFIRMED**, admission 18/18, seal 01r2 hashes
match the chain's. **Protocol:** re-seals only line endings and the suite's final line; smokes disclosed; item 11's fixes
stricter, not tuned to the smokes. **MAJOR:** (1) the 0.61 ms price is a self-timed lower bound, not proved (in-run
control +1 639 ± 281 µs `dt` against +1 087 ± 27 self-timed); (2) item 7's "machine idle" is false — design, commits, a
6-s clang probe and a source patch ran during the timing (the 42.1 min is practically unaffected; the heavy build came
after); (3) item 3 mis-cited the record — the micro-track stop rule did not fire; (4) the claim "never changes what
executes" is false at `spine` 1/2 (plan-time guest reads, spine-only `EXIT` paths; not triggered in `spn117`). MINOR: the
spine code predated its item 4 by seconds (order broken); item 9's order unprovable; the pred's "all rules predate the
smokes" is wrong for parts of item 11; admission leaned on item 11's `armed` relaxation (17 compares at the block's last
frame — the estimator window should be 10–88); BDA regime NEW in both arms; the installed exe was swapped back after
scoring. **Decisions:** PART2 stands; micro-track candidates re-measured in 118; a safe plan (GPU-clean reads only,
abort instead of `EXIT`) before part 2.""")
rep("""`docs/next-session-118.md`: stage 4 part 2 in ONE build and ONE sealed run (item 6): K3 — elements per host render pass
and the largest pass's share; K4 — image-set overlap of adjacent segments at W = 2 and W = 4; the carry — an unseeded spine
on the walker thread (state carried across submissions per queue) compared at submission starts.""",
    """`docs/next-session-118.md`: ONE build and ONE sealed run (item 6): a safe spine plan first; stage 4 part 2 — K3
(elements per host render pass), K4 (image-set overlap of adjacent segments at W = 2 and 4), the carry (an unseeded spine
on the walker thread compared at submission starts); and, in its own schedule arm, the re-measure of the micro-track
candidates on the current build (witness verify, image resolution, `mh_emit` parts) for a track by the ≥ 1 ms rule.""")
f.write_bytes(s.encode('utf-8'))

n = Path('C:/kyty/KytyPS5/docs/next-session-118.md')
t = n.read_bytes().decode('utf-8')


def rep2(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep2("""# Session 118 — route A, stage 4 part 2 in one build and one sealed run: the pass histogram (K3), the image overlap of adjacent segments (K4) and the carry of the spine across submissions""",
     """# Session 118 — one build, one sealed run: a safe spine plan; route A stage 4 part 2 (the pass histogram K3, the image overlap K4, the carry across submissions); and the re-measure of the GuestGpu micro-track candidates the session-117 audit reopened""")
rep2("""shadow spine reproduces the register state before every draw/dispatch (0 mismatches in 19.1 M compares) at 0.61 ms a frame
on GuestGpu; route A's best case −3…−6 ms (10–20 % game speed) [I]; one big ABBA seal costs 42 min of mutants.""",
     """shadow spine reproduces the register state before every draw/dispatch (0 mismatches in 19.1 M compares); its own timer
reads 0.61 ms a frame on GuestGpu (a lower bound — the frame-level price is unmeasured); route A's best case −3…−6 ms
(10–20 % game speed) [I]; one big ABBA seal costs 42 min of mutants; the audit reopened three micro-track candidates
(witness verify ~1.03 ms in session 89, image resolution ~2.6 ms, the `mh_emit` parts).""")
rep2("""1. **Design, recorded in ROADMAP before code (one build, three measurement-only terms, one knob or three):**""",
     """1. **Design, recorded in ROADMAP before code (one build, measurement-only terms):**
   - **Safe plan (ROADMAP 117 item 15 (в)):** the spine reads predication / `COND_EXEC` / branch words and indirect
     register tables only from GPU-clean pages (else the plan is marked uncertain: `spine_uncertain`), and the shadow
     processor aborts the plan instead of reaching an `EXIT`; the knob comment is corrected.""")
rep2("""2. **Code, smoke (unsealed, disclosed), pre-seal check agent, seal, mutants, one sealed pinned run** (300 s; ABBA only if a
   term needs an off arm).""",
     """   - **Micro-track re-measure (item 15 (б)), its own schedule arm:** `takelap` (the six `AheadTake` phases, witness
     verify), `bindlap` (resolution vs bind, per slot), `pathlap`+`mutsite` (the `mh_emit` parts) on the current build;
     each candidate's REMOVABLE part estimated by a rule recorded first; a track only at ≥ 1 ms.
2. **Code, smoke (unsealed, disclosed), pre-seal check agent (its report written to a file), seal, mutants, one sealed
   pinned run** (300 s; a schedule with one arm for part 2 and one for the re-measure, so the instruments do not measure
   each other; estimator window frames 10–88).""")
n.write_bytes(t.encode('utf-8'))
print('ok')
