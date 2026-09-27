# Session 123 — the ceiling of frame skipping (measurement only) and why the GuestGpu slope stops below 1

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 25 (the close: map verdict, the staircase
correction, the lever of this session and its constants (в)–(и)), item 24 (the sealed map), item 23 (the chain on the
platform's own mechanisms), item 2 (the frame-skip idea as first recorded — its staircase rationale is REFUTED by item
25 (б)); `docs/session-122/audit/AUDIT122.md` §3–§5; `C:/kyty/s122/FACTS.md` (git `docs/local-session-122.md`) sections
"Step 4", "Audit", "Close"; `docs/session-122/design/` (the `burn` design — its guard list is the model for the guard
list this session's seal must carry, item 25 (е)).

**Open the report with these numbers:** installed build `d3a981a2…` (`7c73f26`; restored at the close of 122, the
`burn` build `2baf8742…` stays pinned in `C:/kyty/s122`); Sky Garden game speed 0.527 in the base arm of `sky122`
(pinned GPU clock, BDA NEW; 91.2 % of frames at two vblanks); 2 ms burnt on GuestGpu move mean `dt` by 1.80 ms
(s 0.902 ± 0.065, NOT_RESOLVED), `ght122` 0.939 ± 0.039 (OLD, judges only itself); three of five scenes already at
game speed ≈ 1 (HEADROOM); no scene GPU-bound. 60 FPS is not promised.

## Rule of the session

As since session 102 with the additions of 121–122: every decision in `ROADMAP.md` before the first action — also a
rule constant that differs from an accepted decision, BEFORE the agent brief, the lead as author; agent paragraphs tagged
and accepted explicitly; amendments as new items; a sealed consequence is not revoked. Seals with fixtures and ONE full
`mutlib` v4.1 run on the final text with filled seal constants (item 19); suites end with `ALL OK`; edit scripts write
LF; backslashes only through files written by Write. Estimator window frames 10–88 (the arm switch lands at position 89
of the outgoing block); blocks by `GateArm:` lines; outlier frame ≥ 0.5 s drops its ABBA pair, > 2 dropped pairs = run
invalid (item 17 (в)); pair floor 24 after drops; host events in the run window invalidate the run (`hostdev`, item
17 (а)); the `AsyncPipelines: skipped draw` marker is fatal only inside the evaluated population (item 14).
`KYTY_GPU_CLOCK_PIN=1` in every sealed run and video; `KYTY_GPU_CHECKPOINTS` never passed; `KYTY_GPU_WALL=1` in both
arms of the sealed run (item 25 (д)). The BDA regime is quoted with every number. **The seal is checked against the
guard list of the ACCEPTED design; loosening a guard is a ROADMAP line before the seal (item 25 (е)).** **While
`C:/kyty/SEALED_RUN.lock` exists no run — lead, routine ticks, watchdog tasks included — edits, commits or starts
processes (item 25 (ж)).** Long runs and their scoring in the foreground (timeout 600 000 ms), start verified (lock /
process / log). No agent creates user interactions (item 16). Privacy grep before commits (user name, e-mail, launcher
user name); foreign applications are not named in committed text.

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

The specialist sets `done` with a report; the platform moves the step to `in_review` and wakes the lead; the lead
checks the artifacts (not the report), writes the decisions the next step needs into `ROADMAP.md` "СЕССИЯ 123", and sets
`done` with "Принято: …" — only then the next step unblocks. A return is "Доработать: …" in the same task, at most twice
(item 23 (в)). No acceptance-link tasks. Root `HPP-3` is `blocked` on the terminal step; the issue watchdog on `HPP-3`
wakes the lead if the subtree stops.

## Steps

0. **Harness Engineer — port `C:/kyty/s123`** from `s122` (`go123a.sh`; `procload` and the name guard repeated before
   the lock and before installing a build; video; `KYTY_GPU_WALL=1` wired for sealed runs). **Unify the idle criterion**
   (item 25 (ж), MINOR-2): the chain's pre-run idle check uses the same measurement and threshold as the scorer
   (`pre_run.gpu_util_median` ≤ 10). No game run in this step.
1. **Probe Designer — design** `docs/session-123/design123.md` (+ `design/`): ONE measurement-only knob (name proposed by
   the designer; default 0; LAST knob row; read once per flip, may be a schedule arm) under the constants of item 25 (г):
   on every second flip the host translation of draws is skipped, everything the guest can observe executes (labels,
   EOP/RELEASE_MEM, fences, WAIT_REG_MEM, DMA, compute dispatches, queries), the skipped flip shows the previous frame
   (`KYTY_ASYNC_HOLD_FRAME` machinery); picture may degrade, hang / device loss / death = FAIL. Plus the CORRECTNESS
   CENSUS: (1) guest CPU reads of pages written by skipped draws; (2) images written by draws of frame N and read in frame
   N+1 before being overwritten (history targets), by draws and passes. Counters, guards (dose/arming analogues, DRS guard
   `rt_kpx/rt_att`, coverage in both arms), smoke plan, what the seal must check. Names the risk of each skipped class.
2. **Red Team — adversarial review of the design** (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT with numbered RCs).
   The lead accepts the design and the RCs by a ROADMAP line BEFORE the code step starts.
3. **Emu Engineer — code and build:** the knob and census as accepted; `check_gate_order.py` clean; test-failure delta
   0; build from a commit, pinned copy `C:/kyty/s123/kyty_emulator_<sha8>.exe`, `EXPECT`/`PINNED` in `go123a.sh`.
4. **Red Team — code review** of the commit (BLOCKING / non-blocking findings; unrecorded implementation decisions are
   BLOCKING — they go to ROADMAP by the lead before the smoke).
5. **Emu Engineer — fixes and final build** (or "no fixes", with the same pin re-confirmed); pin updated.
6. **Harness Engineer — smoke** (UNSEALED, disclosed): one run on Sky Garden, schedule `knob=0|1` (and the census mode
   if the design has one), video; arming, coverage, census counters, no hang, `vidglitch`. No smoke number enters a
   verdict.
7. **Harness Engineer — scorer, fixtures, the seal** `pred/01_<name>123.md` with the reading of item 25 (г)
   (Δ + 2SE < 500 µs → CLOSED; Δ − 2SE ≥ 500 µs → ceiling measured, design of the correct version in 124; otherwise
   NOT_RESOLVED), the guard list of the accepted design, the `gw_*` report rows; ONE full `mutlib` run on the final text;
   `SEALS123.txt`. No game run.
8. **Harness Engineer — sealed ABBA** on Sky Garden (`KYTY_GPU_WALL=1`, pinned, video); `ght122`'s level as a second run
   only on outcome (ii) and only judged in its own BDA regime.
9. **Session Auditor — audit** (independent recount, MAJOR/MINOR, debts), `audit123/`, git `docs/session-123/audit/`.
10. **Roadmap Lead — close:** verdict in `ROADMAP.md`, documents (`FACTS.md` → `docs/local-session-123.md`, `HANDOFF.md`,
    `CLAUDE.md` = `AGENTS.md`, `docs/agent/`, `agent-team.md` entry point, `LOOP_STATE.md`), commit of both repositories,
    the chain of session 124 created before closing; pause the routine "Сторож цикла KytyPS5" and delete I12/`--repair`
    once the watchdog has fired once and was verified (item 25 (и)).

## Must not be claimed

60 FPS; the ceiling Δ as a gain, a speed-up or a forecast of one (the crude knob breaks the picture; the correct version
pays an unknown share for cross-frame dependencies — upper estimates in this program were wrong by 2–20×); "game speed"
under the knob as the game's speed; frame skipping as shipped, correct or designed; that GuestGpu is proven critical
(item 24 (б): NOT_RESOLVED); the vblank staircase as the reason small wins were invisible (item 25 (б): it was noise);
any number of the `burn` map as a saving (the map is a derivative in added work at one dose); the `gw_flip_ns` census as
a flip-pacing ceiling (a census does not open a track); `ght122` numbers against numbers of the other BDA regime; a speed
number beside another heavy job.
