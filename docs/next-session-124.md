# Session 124 — the closure census of frame skipping (measurement only): how much of a skipped frame a correct version could really leave untranslated

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 40 (the close of 123: verdict, the lever of this
session and its constants (в)(1)–(5), harness constants (е), the routine pause (д)), item 38 (the smoke findings: LOD poll
is a 4-frame series every 16 frames; mode 2 marks the wrong set 10/16; the marking fix (д)), item 25 (г) (the correctness
contract of a shippable version), item 23 (the chain on the platform's own mechanisms); `docs/session-123/design123.md`
§2 (risk classes K1–K6), §3 (census, mode 2), §3.5 (the closure deferred to 124), §11 (the direction table — the model
for this session's); `docs/session-123/audit/AUDIT123.md` §4–§5; `C:/kyty/s123/FACTS.md` (git
`docs/local-session-123.md`) sections "Step 6" (smoke D2 census numbers), "Step 8", "Close".

**Open the report with these numbers:** installed build `d3a981a2…` (`7c73f26`; restored at the close of 123, the
`skipceil` build `e4bb66ca…` stays pinned in `C:/kyty/s123`); frame-skip ceiling of the crude knob on Sky Garden
11 384.3 ± 132.7 µs (`sky123`, BDA **OLD**, 51 pairs), `ght123` 8 076.7 ± 77.0 (OLD, est B at one vblank — truncated);
both CEILING_MEASURED — a ceiling, not a gain. The NEW-regime ceiling is not measured. Smoke D2 (unsealed, wrong set
10/16): zero guest-observable reads of skipped writes on CP/GDS/indirect-args paths, 8 `SkcCpuRead:` lines; share of
skipped draws whose writes the next frame reads `x1_wd/c_dd` = 0.32 — a LOWER bound (last step only). 60 FPS is not
promised.

## Rule of the session

As since session 102 with the additions of 121–123: every decision in `ROADMAP.md` before the first action — also a
rule constant that differs from an accepted decision, BEFORE the agent brief, the lead as author; agent paragraphs tagged
and accepted explicitly; amendments as new items; a sealed consequence is not revoked. Seals with fixtures and ONE full
`mutlib` v4.1 run on the final text with filled seal constants — no full draft runs, only fixtures and `--only`
(item 40 (е)(3)); suites end with `ALL OK`; edit scripts write LF; backslashes only through files written by Write.
Blocks by `GateArm:` lines where a schedule exists; host events in the run window invalidate the run (`hostdev`); the
`AsyncPipelines: skipped draw` marker is fatal inside the evaluated population. `KYTY_GPU_CLOCK_PIN=1` in every sealed
run; `KYTY_GPU_CHECKPOINTS` never passed. **The BDA regime is quoted with every number, by the bands of item 40 (е)(1)
(arm-0/run block mean `bda_scan` ≤ 300 NEW, ≥ 600 OLD, else mixed — not quoted as a regime).** The seal is checked
against the guard list of the ACCEPTED design; loosening a guard is a ROADMAP line before the seal (item 25 (е)).
**While `C:/kyty/SEALED_RUN.lock` exists no run — lead and watchdog tasks included — edits, commits or starts processes
(item 25 (ж)).** Long runs and their scoring in the foreground (timeout 600 000 ms), start verified; the `procload` wait
≤ 540 s per call (item 40 (е)(4)). No agent creates user interactions (item 16). Privacy grep before commits (user name,
e-mail, launcher user name); foreign applications are not named in committed text. **The census may CLOSE frame skipping
but can never ship it; U is never a gain, a speed-up or a forecast.**

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

The specialist sets `done` with a report; the platform moves the step to `in_review` and wakes the lead; the lead checks
the artifacts (not the report), writes the decisions the next step needs into `ROADMAP.md`, and sets `done` with
"Принято: …" — only then the next step unblocks. A return is "Доработать: …" in the same task, at most twice (item 23 (в)).
Root `HPP-3` is `blocked` on the terminal step; the issue watchdog on `HPP-3` is the only liveness guard (the routine is
paused, item 40 (д)).

## Steps

0. **Harness Engineer — port `C:/kyty/s124`** from `s123` (`go124a.sh`, `idle124.py`, `enter_scene.py`, `envchk124.py`,
   `hostdev124.py`; `procload` and the name guard before the lock and before installing a build). Apply item 40 (е):
   `procload --wait-s` ≤ 540 per call, refusal "busy" after it (MINOR-4); GPU utilisation median DURING the hold written
   beside the run (`<tag>.json`, a row, not a guard; MINOR-5); the chain calls the scorer with `--out
   C:/kyty/s124/runs124/<tag>.score.json` (MINOR-6); a census tag with a constant gate file (no schedule, no video).
   Fixtures `ALL OK`, full `mutlib` of the harness helpers. No game run.
1. **Probe Designer — design** `docs/session-124/design124.md` (+ `design/`) under item 40 (в): (1) mode 2 marking fix
   exactly as item 38 (д) (modes 0/1 byte-identical); (2) mode 3 — the CLOSURE: for every marked frame the set of its
   draws/dispatches whose output reaches the observable directly or transitively (images, buffers incl. BDA as far as
   visible, GDS, DMA; within the marked frame), where observable = guest CPU reads, CP reads, GDS, LOD reports (the whole
   poll series, item 38 (б)), and reads in the next unmarked frame before overwrite; output `f_free` (share of draws of
   marked frames outside the closure) and, if the design finds an honest way, a time-weighted share; (3) a DIRECTION TABLE
   for every term (model: §11 of design123) proving `f_free`⁺ is an UPPER side — or naming what keeps it from being one;
   (4) the positive control (a known chain "image written in frame N → read in N+1" must land in the closure) and the
   null control; (5) guards (arming, §4.4-type zeros, progress without hang, no `skipceil` timing use), smoke plan, what
   the seal must check; (6) the cost of the instrument (mode 3 is not for timing).
2. **Red Team — adversarial review of the design** (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT with numbered RCs),
   specifically: can `f_free`⁺ be understated (missed edges: BDA reads, DMA, CP reads of GPU-written memory, deferred
   clears, image→image copies, GC evictions, cross-frame compute)? The lead accepts the design and the RCs by a ROADMAP
   line BEFORE the code step starts.
2a. **Probe Designer — design rev 2** (added by ROADMAP item 43 (о)): `design124.md` rev 2 applying RC1–RC14 as
   decided in item 43 (а)–(н); the lead accepts rev 2 by a ROADMAP item before step 3 starts.
3. **Emu Engineer — code and build:** mode 2 fix and mode 3 as accepted; `check_gate_order.py` clean; test-failure delta
   0; build from a commit, pinned copy `C:/kyty/s124/kyty_emulator_<sha8>.exe`, `EXPECT`/`PINNED` in `go124a.sh`.
4. **Red Team — code review** of the commit (BLOCKING / non-blocking; unrecorded implementation decisions are BLOCKING —
   they go to ROADMAP by the lead before the smoke).
5. **Emu Engineer — fixes and final build** (or "no fixes", with the same pin re-confirmed); pin updated.
6. **Harness Engineer — smoke** (UNSEALED, disclosed): Sky Garden, mode 2 (fixed) — T7 plus marked-row alternation
   ≤ 2 %; mode 3 — closure counters, positive control lands, no hang; A/A `skipceil=0|0` of the new build (cost at 0
   stays a row). No smoke number enters a verdict.
7. **Harness Engineer — scorer, fixtures, the seal** `pred/01_<name>124.md` with the reading of item 40 (в)(3)
   (U = 11 517 µs × `f_free`⁺; U < 500 → FRAME SKIP CLOSED BY CENSUS; U ≥ 500 → prototype in 125; direction not upper →
   NOT_RESOLVED), the guard list of the accepted design, the BDA-regime bands; ONE full `mutlib` run on the final text;
   `SEALS124.txt`. No game run.
8. **Harness Engineer — the sealed census run** on Sky Garden (mode 3 by a constant gate file, pinned clock, no video);
   one attempt; `hostdev`, `envchk`. No other scene.
9. **Session Auditor — audit** (independent recount, MAJOR/MINOR, debts), `audit124/`, git `docs/session-124/audit/`.
10. **Roadmap Lead — close:** verdict in `ROADMAP.md`, documents (`FACTS.md` → `docs/local-session-124.md`, `HANDOFF.md`,
    `CLAUDE.md` = `AGENTS.md`, `docs/agent/`, `agent-team.md` entry point, `LOOP_STATE.md`), commit of both repositories,
    the chain of session 125 created before closing.

## Must not be claimed

60 FPS; U, `f_free`, or the ceiling Δ as a gain, a speed-up or a forecast of one (a census is not a saving — in this
program census prices were wrong by 2–20×); frame skipping as shipped, correct or designed-and-proven; that a correct
version "will save" any number; the OLD-regime ceiling as the NEW-regime ceiling; `ght123` est B as the game's frame rate;
that GuestGpu is proven critical (item 24 (б)); the vblank staircase as a reason for invisibility (item 25 (б)); numbers of
the old mode 2 (set 10/16) as the census of mode 1's set; any census number from a scene other than the reference; a speed
number beside another heavy job.
