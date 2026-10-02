# Session 146 — install the track F shipment binary `dac02fb9`, then the `SCENE_OK` series `sc146` on it: control W, re-check of three scenes, second hold of `bonus_path_maker_mix`, V/W pairs of fifteen never-entered levels (no code)

**Read first:** `ROADMAP.md` "СЕССИЯ 122" item **309** (the s145 close: sheets of the sixteen V viewed — no visible defect on 14, a flat floor without
material on the `enemy_final` arena — new row **B39**, a candidate picture defect (а); the `final_stage` HUD inset events are game animation (б);
**`SCENE_OK` YES 14 / NO 3 of 17** (в); step 2 accepted (г); map rows — 44 of 114 levels ever entered, cold-form pools of 13 V (д); new rows B39 and
**B40** (K2 on the hold of `bonus_path_maker_mix`), B38 text (е); the course count rule and the course row by script (ж), (з); audit and "Процесс" 1–5
(и); the answer on faster series (к); **the s146 target and all constants (л)(1)–(7)**; the chain (м)), item **310** (execution of 309), item **300**
(the shipment binary acceptance: (б) the install as step 0 of s146, (в) `mini_giants_garden`, (г) the 33 `SCENE_OK` as evidence of `9235a7ac`), items
**308**, **306** (platform trap 12), **303–305**, 281 (г), 295; `C:/kyty/s145/FACTS.md` (steps 0–4) and `docs/local-session-145.md`;
`docs/session-145/audit/AUDIT145.md` §1.3–§1.6, §3, §4, §6, §7; `C:/kyty/s145/sc145.py`, `go145a.sh`, `test_sc145.py`, `step2/gate145.py`, the step 2
wrappers, `pred/03_sc145.md` (the port base); `C:/kyty/s145/step4/summary145_viewed.txt` (the regression target); `docs/track-f/register.md` §20–§21;
`docs/track-f/fsc.md`; `ps5 em/CLAUDE.md`; `ps5 em/docs/env-vars.md`; `ps5 em/docs/agent-team.md` (general rules 5, 15–28).

**Open the report with these facts:** goal (B) since the s140 close — correctness of the game on as many scenes as possible; Sky Garden speed is
neither a goal nor a gate. Installed build at the start: `9235a7ac…` (`rtskip=1`); step 0 installs the track F shipment binary `dac02fb9…` (commit
`95eec776`, translation signature `56189185`; `KYTY_FIX_DUALSRC=1`, `KYTY_FIX_B1B=1`, B26b; `KYTY_FIX_MINIMIZE=0`), accepted by item 300 after the FSc
regression. Session 145: control W passed; 33 of 34 tags made (`w145_06` cut by an executor timeout); 15 of 16 cold V entered and held 120 s; **`SCENE_OK`
YES 14 / NO 3 of 17** (`final_shooting` — `-lvl` opens the root `final_stage`, NOT_ENTERED by the letter; `bonus_path_maker_mix` — a 4.6 s frame on the
hold, B40; `enemy_final` — the lead's sheet shows an arena floor without material, B39). Distance (course row 145): `SCENE_OK` **33 of 114**; open rows 41 —
K1 2 / K2 4 / K3 6 / K4 18 / K5 11, of them defects by item 228(б) 15 (on the installed `9235a7ac` before the install: 45); 44 of 114 levels ever entered;
sessions without a shipping under (B): 0. **The lead's prior [I]:** P(control W) ≈ 0.85; P(`-lvl` entry of a new level) ≈ 0.9; P(cold V without K2 over
330 s) ≈ 0.8; P(W passes | V) ≈ 0.95; P(sheet) ≈ 0.9 ⇒ ≈ 9–11 new `SCENE_OK`; P(a re-check holds) ≈ 0.85 per scene. 60 FPS is not promised.

## Rule of the session

As in sessions 138–145: every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u` at writing; times in
step rows only from `date -u` at the event, written by the same command into `C:/kyty/s146/step<N>/times.txt`; a row about an event noticed later
carries both times with the source (general rule 23); reading an input not earlier than its commit and the `ROADMAP.md` item named as read;
extending a step's scope only by a `ROADMAP.md` item before the action. **No emulator code and no build in session 146** (fixes live in tracks F and S).
The binary changes once — step 0, item 300 (б); FS2 (`HPP-384`) is not installed before the s146 close. Game runs only by the Harness Engineer, one at a
time, under the lock `C:/kyty/SEALED_RUN.lock` through `procload.py`; the series only after the seal `pred/01_sc146.md`; between tags the lock is free
and the queue is session > P > F > S; while the series runs, links without the lock start no builds, mutant sets or recounts longer than 30 s and use
**no Edit / Write tools** (a change is a script from a file run by one Bash command with the lock check in it; general rule 27, "Процесс" 1 of s145);
a track link assigned to the series executor is `blocked` on the runs link. **A question that needs the lead — a comment in the own link mentioning
the lead AND one line in `HPP-3`; a waiting monitor is set only by an `executionPolicy` write carrying the current `stages`, the API answer checked
for non-empty `stages` in the same command** (platform trap 12, "Процесс" 2). **No external `timeout`, `kill` or repeated call around a detached tag
call before its `rc=` line** ("Процесс" 4). **No foreign process or application name in `times.txt`, FACTS, comments or commits — `<app>` and the pid;
`git grep -P -f C:/kyty/scrub/checks.txt -- <added paths>` in the same command as every `git commit --only`** (general rule 28, "Процесс" 5).
File-system searches only inside `C:/kyty` with a `timeout`, never `find /`; no process outlives its heartbeat. Logs are read by python in binary mode,
never whole; every number from a log is [c] with the path and sha256; every estimate is [I] with its basis. References to changing documents are pinned
`<commit>:<path>:<line>` (`ps5-em@<commit>:…`) with an anchor map and the +1 positive control (general rule 24(1)). A stop of a running link comes as a
comment AND the file `C:/kyty/s146/STOP` (general rule 26). Commits only `git commit --only -- <paths>` with the real `C:/Program Files/Git/cmd/git.exe`
and `GIT_AUTHOR_*`/`GIT_COMMITTER_*` (platform trap 11). No agent creates user interactions. `PYTHONIOENCODING=utf-8`. A third "Доработать" is never
given to one link. Runs and scoring are synchronous in the heartbeat; a continuation is only a saved Paperclip wake with a checked API answer.

## Chain (item 309 (м)): every executor step carries an `executionPolicy` review stage by the lead, checked in the API answer

Root `HPP-3` is `blocked` on step 4. Step 0 is created `blocked` on the s145 close link `HPP-354` (general rule 25).

## Steps

**0. Harness Engineer — install and warm-up (under the lock), then harness, scorer, level list, regression, calibration, mutants, seal** in
`C:/kyty/s146/`. (a) Install by item 300 (б)(1)–(3): copy `C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe` → `kyty_emulator.exe` of the emulator folder,
sha256 before and after, pinned copy `C:/kyty/s146/kyty_emulator_dac02fb9.exe`; caches untouched (manifests and `GLCache` before/after as `times.txt`
rows); warm-up tag `i146_v` — V Sky Garden on the installed binary in the item 221 (г)(3) form (video, Σ`dt` after the first scene frame ≥ 300 s, 0 glitches,
0 death markers, 0 frames ≥ 1 s, sheet for the lead against `fs_b`); a failed warm-up — roll back with `C:/kyty/s128/kyty_emulator_9235a7ac.exe` and ask
the lead. (b) Port of `go145a.sh`, `sc145.py`, `test_sc145.py`, `step2/gate145.py` and the wrappers: `go146a.sh` — 35 tags (item 309 (л)(2)): `w146_00`
control W on Sky Garden in the item 300 (б)(4) form (`--vulkan-validation true`, precache by default, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000`, no
`VK_LAYER_MESSAGE_ID_FILTER`, the line `DualSrcBlend: supported=1 enabled=1` before the first `GuestOut`); `r146_01`…`r146_03` — re-check V of
`hoover_beach`, `sponge_dirty_bath`, `timestop_casino`; `r146_04` — second V hold of `bonus_path_maker_mix`; pairs `v146_NN`/`w146_NN`, NN = 05…19 — the
first 15 never-entered scene levels in the order of the level map of `C:/kyty/s141/step1b/inventory141_r2.md`, checked against the `Level has started:`
lines of every log under `C:/kyty` since 2026-09-30 including the track roots, without the "non-scenes" of item 217 (г) and without `final_shooting`
(the list and the check — a script and its output with sha256; the lead accepts the list with step 0, before the seal). V — shipped defaults of the
installed `dac02fb9`, video, hold ≥ 330 s wall, `--attempts 1`; W — the control-W form, no video, hold ≥ 310 s; the W of a pair is not called when its V is
`NOT_ENTERED` (row `SKIPPED_V_NOT_ENTERED`, not an attempt). Scorer `sc146.py` — the rules of `sc145.py` with **no change of constants**, plus data rows
(not gates): `stubs` (F13: count of `Unresolved import stub called`), `asserts` (F14: `ASSERT:` and `user_msg_param`), tile events of every V (D-4: the
auditor's tile rule, threshold 4), the `DualSrcBlend` control of every W; BUSY and CPU rows print `<app>` and the pid; `--stop-check` reads
`runs146/<tag>.score.json`; `SCENE_OK` by a pair of one session on `dac02fb9`. The call wrapper moves the previous output of a tag away before a new
call (D-9). **Regression without game:** `sc146.py` reproduces `C:/kyty/s145/step4/summary145_viewed.txt` on the 33 logs of s145 (new rows apart — diff
printed); calibration 5 of 5; fixtures `ALL OK` (new edges: `SKIPPED_V_NOT_ENTERED`, `stubs`/`asserts`, the `DualSrcBlend` control, an `r146_` tag,
`<app>`); one counted full mutant run ≤ 15 min (`mutlib` v4.1, forecast before the run); seal `pred/01_sc146.md` with sha256 of the harness, scorer,
gate, fixtures, `enter_scene.py`, `s51_vidglitch.py`, `sheet142.py`, wrappers and the 35 call lines.
**1. Red Team — adversarial review** (`C:/kyty/KytyPS5/docs/session-146/review146.md`): the install rows (sha before/after, caches untouched, warm-up
sheet); the control-W form on `dac02fb9` (precache by default cannot hide a stop; the `DualSrcBlend` control); the level list against all logs (own
recount); `SKIPPED_V_NOT_ENTERED` cannot skip a W of an entered V; `--stop-check` from json gives the same decisions as from the log on the 33 s145 tags;
the new data rows; the regression is byte-exact where claimed; the seal.
**2. Harness Engineer — 35 runs and scoring** under the lock, one at a time, in the sealed order; an API check row in `times.txt` before every call;
comments on the series start and end in the cycle task; contact sheet of every video for the lead (frames with tile events as triples); no re-run of a
failed entry; stop rules as sealed; no external `timeout` around a call.
**3. Session Auditor — audit** `docs/session-146/audit/AUDIT146.md`: the protocol of the s145 close (items 309–310, general rule 25 order, sha256 table of
all `instructions/AGENTS.md`) and of steps 0–2 of s146 (the install against item 300 (б); general rules 27–28 with the s145 additions); own recount of the
scorer outputs including video and the glitch detector; privacy (`<app>`); `CLAUDE.md` = `AGENTS.md`; MAJOR / MINOR; debts; "Процесс".
**4. Roadmap Lead — close of session 146**: sheets of every V (a row per tag); `SCENE_OK` yes/no per level (re-check scenes: a breach of item 221 (г)(3)
removes the scene's `SCENE_OK`); B40 p; map rows; register F rows; course row 146 by script (`mini_giants_garden` +1 with the install); "Процесс" applied
before the s147 chain; documents; the s147 chain.

## Must not be claimed

60 FPS; that goal (B) makes the game faster or keeps its speed; that any scene is correct or playable to the end (`SCENE_OK` is a hold window
without input at the `-lvl` point); that a level "works" from an entry; that a run proves a defect absent where it did not show it; that the 33
`SCENE_OK` of `9235a7ac` hold on `dac02fb9` before their re-check; that the `enemy_final` floor is wrong or right; the cause of the B40 K2 or its link to
B36 or `PriorityStall:`; that the video of a cold V shows frames without records; that `final_shooting` cannot be entered otherwise; that a repeated entry
equals a cold one; that W without precache equals W with precache; that the B35 pipeline draws right or wrong; that the validation layer would report
any error; that the glitch detector is right; that the inventory is complete; any past-session number as a gain or a ceiling; that `bindlean` or B2 is
correct; OLD; 47.98 % as the time of `9235a7ac`.
