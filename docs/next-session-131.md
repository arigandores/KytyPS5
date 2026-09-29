# Session 131 — two levers: (L) the loss window of `armcopy` by address, P8 against a real loss (diagnostic, no ceiling); (K16) the dose calibration of the dispatch path with a phase census, sealed ABBA `dd131`

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 123 (the close of 130: verdict (а), shipping (б), audit
decisions (в) — the `date -u` rule and the lead-recount rule, privacy P-1; process items (г); the course (д); the re-assessment
(е); **the constants of track L (ж)(1)–(5)**; **the constants of track K16 (з)(1)–(6)**; debts (и); the chain (к)); items 116–122
(the attribution of `ac_cbad`: classes M/E, H = `ac_cbm_host` − `ac_cbm_host_d`, the P8 residual of item 119 (б), `CBAD_LOSS`),
105 (ж)(7), 93 (г) (the dose pattern `protceil=2` that K16 copies), 84–87, 83 (г), 77 (б), 78 (е), 66 (а), 55 (б).
`docs/session-130/audit/AUDIT130.md`; `docs/local-session-130.md` (§Step 6 — the H event: row n = 2516, block 7, p = 85, 9 adjacent
pages); `docs/session-130/cbad130.md` ред. 2 (§3.6 the lemma, §4.2 `dk`, the sites С1–С9); `docs/session-130/design/cbadreview130.md`;
`docs/session-130/design/codereview130.md`; `docs/session-129/design129.md` ред. 2; `ps5 em/CLAUDE.md` environment entries of 130
(`acinline`, `ac_cbm_*`), 129 (`armcopy`), 128 (`protceil`); `ps5 em/docs/agent-team.md` (rules 13–14, section 18).
Code: `src/graphics/host_gpu/memoryTracker.h` (`ForEachUploadRange`, `Handover`), `pageManager.cpp` (`UpdateRegionWatchers`,
`TakePendingRun`, `apply`, `AcChunk`, `AcClassify`), `renderer/cache/bufferCache.cpp`, `renderer/renderCompute.cpp` (the dispatch
span of `mh_disp_us`, `pl_cs_*`), `src/common/gates.{h,cpp}`, `src/common/frameStats.h`.

**Open the report with these numbers:** session 130 — **`ARMCOPY_INCORRECT`** by the sealed reading of items 116 (е) / 118 (б):
`s10s130` (build `3f4af2c3`, ABBA `armcopy=2|4`, reference) H₂ = 9, H₄ = 0 (one row, 9 adjacent pages of one chunk) ⇒ `CBAD_LOSS`;
desert 0/0; guards 0; audit recount CONFIRMED to the unit, 0 MAJOR / 2 MINOR. **No `ACINLINE_*` verdict** (`ai130` never ran).
Nothing shipped; **sessions without shipping: 2 (129, 130)**. **No speed number in session 130.** Course base unchanged: **53.36 %**
(31 237.1 µs, arm 0 of `ac129`, `edd17418` at `armcopy=0`, NEW) — not the time of the installed `9235a7ac`; remainder 14 570.1 µs.
The measured time of `armcopy` (`ac129` −334.9 ± 144.4 µs, NEW) is not on the scoreboard — the mechanism failed its correctness
reading. K16: level 2 359 µs of the dispatch path [M, `recon126`]; honest prior of the calibration 0.90 × 2 359 ≈ 2 120 µs [I] —
`K16_OPEN` is almost certain, and the decisive output is the **phase census** (what inside 8.8 µs per dispatch is removable).
60 FPS is not promised.

## Rule of the session

As in session 130 (items 105 (в), 123 (в)): every decision in `ROADMAP.md` before the first action — also a rule constant that
differs from an accepted decision, BEFORE the agent brief; **the time in a decision header is `date -u` at writing and not later
than the item's commit**; a lead recount puts row n = F into the LEAVING block (position 89) and cites its output file and sha;
agent paragraphs tagged and accepted explicitly; amendments as new items; a sealed consequence is not revoked. Every specialist
step writes `## Step N — …` in `C:/kyty/s131/FACTS.md` BEFORE `done`, time in UTC, the scale named in every table. Mutants: the
chain once at step 0 **with a wall forecast before the start** (mutants × suite wall under N workers / N + control per part;
forecast over the remaining budget — question to the lead BEFORE the start), ≤ 8 workers, cheap refusals before full paths, the
outer `timeout` of a part above its inner cap; constants and same-form tags — fixtures and `ALL OK` only; a stage-logic edit without
budget left — stop and ask; scorer suites in the `mutlib` early-exit form; ONE full scorer `mutlib` v4.1, cap 15 min; session budget
30 min by item 87 (б)(3). A regime with 0 pairs prints `DEBT`. **Blocks by `GateArm:` lines, never by `blk`.** Window 10–88 of
item 55 (б) named with its item number. The harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call (item
76 (б)); the chain call of a sealed tag is verbatim from the seal, `PLWAIT` in the log (item 105 (в)). One attempt per registered
tag. **The installed build is `9235a7ac…`; every chain with the game restores it.** While `C:/kyty/SEALED_RUN.lock` exists nobody
edits, commits or starts processes (item 25 (ж)). Long runs in the foreground (timeout 600 000 ms); start time and expected end in
the step comment. No agent creates user interactions (item 16). Python printing Cyrillic runs with `export PYTHONIOENCODING=utf-8`.
Privacy grep over the whole tree before commits (the check list lives in `C:/kyty/scrub/`, never in git). A third "Доработать" is
never given to one link — rework beyond the second is a new link (item 115).

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

0, 0п, 1 and 2 start in parallel. The specialist sets `done` with a report and its `FACTS.md` section; the platform moves the step to
`in_review`; the lead writes the decisions the next step needs into `ROADMAP.md` and sets `done` with "Принято: …". The code step 5
waits for BOTH design reviews (3 and 4) accepted. Root `HPP-3` is `blocked` on step 11.

## Steps

**0. Harness Engineer — port `C:/kyty/s131`** from `s130`: `gates_base.txt` with explicit `armcopy=0`, `acinline=0`, `lwin=0`,
`dispceil=0`, `protceil=0`, `rtskip=1` (sha in FACTS); the chain `go131a.sh` with the track-L tags of item 123 (ж)(4) (`lw1s131`…
`lw5s131`; the X control of `lw4s131` is a constant filled by fixture after the lead accepts step 3), the survival smoke `dds131`
(item 123 (з)(2)), the sealed `dd131` (item 123 (з)(3)); a smoke parser for the L reading (item 123 (ж)(5)) with a fixture on every
member (liveness, identity `lw_p8 + lw_x = H`, controls, guards, `LW_LOSS`, `LW_P8`, `NOT_RESOLVED` incl. ΣH = 0) ending in `ALL OK`;
lock before `procload`; `PLWAIT` fixture; one attempt; restore of the installed build; refusal on `protceil` ≠ 0; ONE full chain
mutant run with the forecast. No game run.
**0п. Session Auditor — privacy of the current tree** (item 123 (в)(3)): replace the name of the foreign application in the 27
pushed files (`docs/session-99/**`, `docs/session-120/audit/protocol.md`) by a neutral word; `git grep` over the whole tree with the
check list from `C:/kyty/scrub/`; one commit; no history rewrite, no push. Consumer — audit step 10.
**1. Probe Designer — design L** `docs/session-131/lw131.md` under item 123 (ж)(1)–(5): the stamps (clear generation, pending-mark
generation, operation id — written only by operations latched at 2/3/4); the exact time windows of class `lw_p8` (O3 cleared the
page's CPU-dirty bit after chunk K's take and before the S_k hold, its `pending` mark seen after S_k release); **the proof that any
write lost by chunk K lands in `lw_x`** (per window of §2 D129, О12/О14, X1–X4 — the windows where it does not are [U] aloud);
the deferred resolution and `lw_open`; the P8 control (`lwin=2`: where the spin widens the race and why `lw_p8` > 0 must follow);
**the X control** (which setting gives `lw_x` > 0 and why — or "none" aloud, then `LW_P8` is unreachable and the lead decides before
code); the `ArmCopyLoss` lines; path 0/1 untouched; no new lock or wait under `apply` / `RegionManager::lock` on path 1; cost at 1/2.
Questions to the lead. No game run, no emulator code.
**2. Probe Designer — design K16** `docs/session-131/dd131.md` under item 123 (з)(1)–(5): the exact span that feeds `mh_disp_us`
and the dose spot inside it (same clock, same thread, inside the hold); the phase census of the span (existing `pl_cs_*` plus new
counters only for the undivided rest; identity Σ phases ≤ span with a named tolerance); "0 is the old path byte for byte"; the
dose delivery guard; what the census can and cannot say about a mechanism. Questions to the lead. No game run, no emulator code.
**3. Red Team — adversarial review of L** `docs/session-131/design/lwreview131.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, numbered
RCs): build a write lost by chunk K that the classifier puts into `lw_p8` (found ⇒ MAJOR, the design changes before code); build a
dead X control; check the stamps against the code (`UpdateRegionWatchers`, `Handover`, `TakePendingRun`), not the text.
**4. Red Team — review of K16** `docs/session-131/design/ddreview131.md`: the dose spot and clocks against `renderCompute.cpp`; bias
of the ABBA by the dose outside the span; the census identity.
**5. Emu Engineer — code** (after the lead accepted 3 and 4): commit (1) the stale comment `ARMCOPY_HOLD` → `ARMCOPY_INCORRECT` in
`src/common/gates.{h,cpp}`; commit (2) `lwin`; commit (3) `dispceil` + census; `check_gate_order.py` before the build; `git status
--short -- src` empty → ONE measuring build → pinned copy `C:/kyty/s131/kyty_emulator_<sha8>.exe`; `shader_cfg_tests` delta 0; NOT
installed. No game run.
**6. Red Team — code review** `docs/session-131/design/codereview131.md` (PASS / PASS_WITH_FIXES / FAIL): path 0/1 untouched by any
read, stamps only at 2/3/4, the classifier as accepted, the dose as accepted, knob order.
**7. Harness Engineer — smokes** (after 6 and 0): `lw1s131`…`lw5s131` with the L reading of item 123 (ж)(5) as a separate report line
(all rows of the arm blocks; window 10–88 of item 55 (б) second); all `ArmCopyLoss` lines listed; `dds131` — survival, dose delivery,
BDA regime, Δ as rows. A death or hang is a finding, no repeat. Questions to the lead.
**8. Harness Engineer — scorer, fixtures, the seal** `pred/01_dd131.md` (both estimators, every window edge, every outcome of
item 123 (з)(4) incl. `DEBT` for 0 pairs, delivery guard, BDA and DRS; census rows); ONE full `mutlib`; `SEALS131.txt`.
**9. Harness Engineer — the sealed `dd131`** and its scoring; restore the installed build.
**10. Session Auditor — audit**: own recount of the L reading (classes, identity, controls, guards) and of `dd131` (both estimators,
the base, dose delivery); protocol (decision before action by commit order and `date -u`, one attempt, lock before `procload`, FACTS
per step, mutant budget and forecast); MAJOR/MINOR; not proven; debts; section «Процесс» (≤ 5 items); `audit131/`, git
`docs/session-131/audit/`.
**11. Roadmap Lead — close**: the L verdict and its consequence for `armcopy` (amendment of the H reading only at `LW_P8`); the K16
verdict; the course row (base — arm 0 of `dd131`); the re-assessment (by census: a K16 mechanism, or K5); process items; documents;
commit of both repositories; the chain of session 132 before closing.

**Outside the chain:** nothing; any off-chain task gets a formal consumer (item 73 (в)).

## Must not be claimed

60 FPS; that `armcopy=1` loses guest writes, or that it does not (before the L reading, and beyond what it says); that the 9 pages
of `s10s130` were one event ([I]); any speed number of session 130; the `ac129` gain on the installed build or on the scoreboard;
time or correctness of `acinline`; OLD; other scenes; the calibration Δ of `dd131`, the prior 2 120 or any census number as a gain or
as the ceiling of a mechanism; 53.36 % as the time of `9235a7ac`; rows built by `blk`; a timing number beside another heavy job.
