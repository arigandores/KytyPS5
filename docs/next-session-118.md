# Session 118 — one build, one sealed run: a safe spine plan; route A stage 4 part 2 (the pass histogram K3, the image overlap K4, the carry across submissions); and the re-measure of the GuestGpu micro-track candidates the session-117 audit reopened

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 117 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–15 (item 3: why route A, stage 4 first; item 6:
batching; item 14: the `spn117` result; item 15: the audit); `C:/kyty/s117/FACTS.md` (git `docs/local-session-117.md`);
`docs/session-117/designA4_spine.md`; `docs/DESIGN_82_parallel.md` §1 (Amdahl, f_eff) and §7 (K1–K8);
`docs/session-104/designA_review.md` §3–4.

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1 bdanarrow=0 titleasync=1 spine=0`, installed build `d3a981a2…` (`7c73f26`). Session 117: the
shadow spine reproduces the register state before every draw/dispatch (0 mismatches in 19.1 M compares); its own timer
reads 0.61 ms a frame on GuestGpu (a lower bound — the frame-level price is unmeasured); route A's best case −3…−6 ms
(10–20 % game speed) [I]; one big ABBA seal costs 42 min of mutants; the audit reopened three micro-track candidates
(witness verify ~1.03 ms in session 89, image resolution ~2.6 ms, the `mh_emit` parts). 60 FPS stays
the direction without a route with a live estimate.

## Rule of the session

As since session 102: every decision in `ROADMAP.md` before the first action (also every change to a running workflow
and every stage a workflow drops); a sealed consequence is never set aside after its outcome; seals with fixtures and
mutants (`mutlib` v4.1 frozen `docs/session-116/mutlib_v41/`, FULL runs `--control --no-memo --work-dir/--cache-dir
C:/kyty/s118/...`); edit scripts write LF (`write_bytes`), fixture suites end with `ALL OK`; mutation runs may overlap
coding and builds, never a sealed run; audit before closing.

## Steps

0. **Harness root `C:/kyty/s118`**: port `enter_scene.py` (ROOT s118), `gates_base.txt`, `run_safety99.py`,
   `procload.py`, `launch_run.py`, the pinned `kyty_emulator_d3a981a2.exe`; the `spn117` scorer is the parent for
   whole-line derivation.
1. **Design, recorded in ROADMAP before code (one build, measurement-only terms):**
   - **Safe plan (ROADMAP 117 item 15 (в)):** the spine reads predication / `COND_EXEC` / branch words and indirect
     register tables only from GPU-clean pages (else the plan is marked uncertain: `spine_uncertain`), and the shadow
     processor aborts the plan instead of reaching an `EXIT`; the knob comment is corrected.
   - **K3 — the pass histogram:** on the real path, the draws + dispatches between consecutive host render-pass begins
     (`BeginRenderingImpl`), dispatches outside a pass counted into the current run; per frame the largest run and the
     total (a gauge + counters), and a histogram by size. Rule of `DESIGN_82` §7 K3 (largest pass ≥ 25 % of elements and
     f_max ≥ 0.30 ⇒ W > 4 buys nothing) — for maximum FPS it bounds W, it does not close the route; record the reading
     before the run.
   - **K4 — image overlap of adjacent segments:** per frame, the images each element touches (bound textures from the
     image loop of `PrepareBindings`, colour/depth targets from `AcquireRenderTargets`), the frame cut at pass boundaries
     into W = 2 and W = 4 segments balanced by element count, and the shared share of adjacent segments; the measure
     (|A ∩ B| / min(|A|, |B|) or Jaccard) fixed in the design. K4 (> 30 % ⇒ the transition authority becomes a new
     serialiser) as the sealed rule.
   - **Carry:** an UNSEEDED spine on the `dawalk` walker thread (per-queue `CommandProcessor` state carried across
     submissions, as route A would need), its state at each submission start handed to GuestGpu and compared
     member-wise with the real state there (counters like `spine_*`); this is the one thing `spn117` could not prove.
   - **Micro-track re-measure (item 15 (б)), its own schedule arm:** `takelap` (the six `AheadTake` phases, witness
     verify), `bindlap` (resolution vs bind, per slot), `pathlap`+`mutsite` (the `mh_emit` parts) on the current build;
     each candidate's REMOVABLE part estimated by a rule recorded first; a track only at ≥ 1 ms.
2. **Code, smoke (unsealed, disclosed), pre-seal check agent (its report written to a file), seal, mutants, one sealed
   pinned run** (300 s; a schedule with one arm for part 2 and one for the re-measure, so the instruments do not measure
   each other; estimator window frames 10–88).
3. **Consequences fixed before the run:** a carry mismatch ⇒ stage 4 stops until the hazard has a design; K4 over its
   bar ⇒ route A's granularity coarsens or the route closes for maximum FPS (decided by the arithmetic recorded first);
   all pass ⇒ stage 3 resumes (M3.2) with stage 5 (W = 2) as the first milestone with a gain.
4. If time remains: nothing else heavy; the session closes with its audit.

## Must not be claimed

60 FPS; any gain of route A before stage 5 measures one; that the spine carries state across submissions before the
carry term passes; any speed number beside another heavy job.
