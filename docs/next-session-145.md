# Session 145 — `SCENE_OK` series `sc145`: control W, W repeat of `rocket_hourglass`, V/W pairs of sixteen never-entered levels (no code)

**Read first:** `ROADMAP.md` "СЕССИЯ 122" item **273** (the s144 close: sheets of the twelve V viewed (а); `SCENE_OK` YES 18 / NO 2 of 20 (б); map
rows (в); new rows **B37** (swapchain recreated at zero window size) and **B38** (video recording loses shown frames right after the first scene
frame of a cold entry), B36 p = 1 of 2 (г); the course row recount by script (д); track F iteration F5 = B37 with its criterion before code (е);
course row 144 (ж); audit and "Процесс" 1–5 (з); **the s145 target and all constants (к)(1)–(7)**; the chain (л)), item **274** (execution of 273),
items **272** (audit acceptance; D-5 answer — the validation layer duplicate limit counts per message id), **270**, **266**, **264**, 254 (е);
`C:/kyty/s144/FACTS.md` (steps 0–4) and `docs/local-session-144.md`; `docs/session-144/audit/AUDIT144.md` §1.3, §2, §4, §7; `C:/kyty/s144/sc144.py`,
`go144a.sh`, `test_sc144.py`, `step2/gate144.py`, `pred/01_sc144.md` (the port base); `C:/kyty/s144/step4/summary144_viewed.txt` (the regression
target); `docs/track-f/register.md` §12; `ps5 em/CLAUDE.md`; `ps5 em/docs/env-vars.md`; `ps5 em/docs/agent-team.md` (general rules 5, 15–28).

**Open the report with these facts:** goal (B) since the s140 close — correctness of the game on as many scenes as possible; Sky Garden speed is
neither a goal nor a gate; installed build `9235a7ac…` (`rtskip=1`) with all shipped defaults. Session 144: control W on Sky Garden passed; 19 of
21 W held 310 s with 0 `[Vulkan][E]` (form without precache); 12 of 12 repeated-entry V held 330 s with K2 0 and 0 glitches; sheets viewed, no visible
defect; **`SCENE_OK` YES 18 / NO 2 of 20** — `rocket_hourglass` (its W was stopped at 89 s by a window minimize: the swapchain is recreated with a
0×0 extent, B37) and `mini_giants_garden` (its W stops on B35 in game). Distance (course row 144): `SCENE_OK` **19 of 114**; open defects 39 —
K1 2 / K2 3 / K3 7 / K4 19 / K5 8, of them defects by item 228(б) 15; 29 of 114 levels ever entered; sessions without a shipping under (B): 0.
**The lead's prior [I]:** P(control W) ≈ 0.9; P(`-lvl` entry of a new level) ≈ 0.85; P(cold V without K2 over 330 s) ≈ 0.8; P(W passes | V) ≈ 0.9 ⇒
≈ 8–11 new `SCENE_OK`. 60 FPS is not promised.

## Rule of the session

As in sessions 138–144: every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u` at writing; times in
step rows only from `date -u` at the event, written by the same command into `C:/kyty/s145/step<N>/times.txt`; a row about an event noticed later
carries both times with the source (general rule 23); reading an input not earlier than its commit and the `ROADMAP.md` item named as read;
extending a step's scope only by a `ROADMAP.md` item before the action. **No emulator code and no build in session 145** (fixes live in tracks F and
S). Game runs only by the Harness Engineer, one at a time, under the lock `C:/kyty/SEALED_RUN.lock` through `procload.py`, only after the seal
`pred/01_sc145.md`; between tags the lock is free and the queue is session > P > F > S; **while the series runs (first `lock taken` to last `lock
released`), links without the lock — tracks and the lead — start no builds, mutant sets or recounts longer than 30 s; the runner comments the start
and the end of the series in the cycle task** (general rule 27, "Процесс" 2 of s144); **a file write and a comment go in one Bash command with the
lock check in it** (general rule 27, "Процесс" 3). Track links with the lock that are not `done` at the start of step 2 get the s145 audit link as a
blocker. File-system searches only inside `C:/kyty` with a `timeout`, never `find /`; no process outlives its heartbeat (general rule 28). Logs are
read by python in binary mode, never whole; every number from a log is [c] with the path and sha256; every estimate is [I] with its basis.
References to changing documents are pinned `<commit>:<path>:<line>` (`ps5-em@<commit>:…`) with an anchor map and the +1 positive control
(general rule 24(1)). A stop of a running link comes as a comment AND the file `C:/kyty/s145/STOP` (general rule 26): every command longer than 60 s
starts with `[ -e C:/kyty/s145/STOP ] && exit 4`. Commits only `git commit --only -- <paths>` with the real `C:/Program Files/Git/cmd/git.exe` and
`GIT_AUTHOR_*`/`GIT_COMMITTER_*` (platform trap 11). No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the whole
tree before commits (the list lives in `C:/kyty/scrub/`, never in git). A third "Доработать" is never given to one link. Runs and scoring are
synchronous in the heartbeat; a continuation is only a saved Paperclip wake with a checked API answer.

## Chain (item 273 (л)): every executor step carries an `executionPolicy` review stage by the lead, checked in the API answer

Root `HPP-3` is `blocked` on step 4. Step 0 is created `blocked` on the s144 close link `HPP-334` (general rule 25).

## Steps

**0. Harness Engineer — harness, scorer, regression, calibration, mutants, seal** in `C:/kyty/s145/` (port of `C:/kyty/s144/go144a.sh`, `sc144.py`,
`test_sc144.py`, `step2/gate144.py`, `fgcpu144.py`, `cachemf144.py`): `go145a.sh` — 34 tags in the order of item 273 (к)(1): `w145_00` control W on
Sky Garden (`underwater_aerial_garden`); `w145_01` — W repeat of `rocket_hourglass` (paired with V `v144_09` of s144, log sha256 checked against
`C:/kyty/s144/step2/times.txt`); then pairs `v145_NN`/`w145_NN`, NN = 02…17, cold first entry: `small_pot_lava`, `spin_drill_natural_cave`,
`enemy_taco`, `jack_in_the_box`, `final_shooting`, `picup_light`, `enemy_snake`, `light_gadget_graveyard`, `shuriken_ninja_castle`, `final_stage`,
`mini_rocket_chain`, `enemy_chameleon`, `bonus_path_maker_mix`, `enemy_bird`, `cymbal_party_land`, `enemy_final`. V — `-lvl`, shipped defaults,
video `KYTY_REC`, hold ≥ 330 s wall, `--attempts 1`; cold-entry forms B5/B5a/B33 go into the cold pools. **W — `--vulkan-validation true` +
`KYTY_PIPELINE_PRECACHE=0` + `VK_LAYER_MESSAGE_ID_FILTER=<the id of the F6 warning>`** (the id named from the s144 W logs [c] — the one message
that exhausted the duplicate limit in 13 W; no other id is filtered), hold ≥ 310 s, no video. Scorer `sc145.py` — the rules of `sc144.py` with **no
change of constants**, plus three rows (item 273 (к)(2)–(3)): **window event** (counts of `Window <id> minimized`, `restored`, `resized`,
`size changed`, `lost keyboard focus`, `Recovering Vulkan swapchain`; a tag with `minimized` or `Recovering Vulkan swapchain` is not read as a level
outcome — admission row "window event", the gate stops the series and asks the lead); **video continuity** (B38: `FrameTrace` lines after the first
scene frame ending inside a `.idx` recording gap > 60 ms, and the longest run — data next to `SCENE_OK`, not a gate); **layer limit** (count of the
layer's "last time reporting it" lines per W: 0 required in the control W; elsewhere ≠ 0 marks "layer truncated", outcome by the letter).
`SCENE_OK` per level over its V/W pair (item 254 (е)); for `rocket_hourglass` the sheet row of `v144_09` is "viewed" by item 273 (а). Stop rules:
control W stopped — stop before the next tag, question to the lead; two W in a row with one stop marker before the first `GuestOut` line — stop;
three V in a row "not entered" with one marker — stop; a window event — stop and question. **Regression without game:** the new scorer reproduces
`C:/kyty/s144/step4/summary144_viewed.txt` on the 33 logs of s144 and 8 V of s143 (new rows apart — diff printed); calibration 5 of 5; fixtures
`ALL OK` (new edges: a window event, `Recovering Vulkan swapchain` without `minimized`, the layer limit line in the control W, a recording gap, a
pair with a V of s144, a cold entry); one counted full mutant run ≤ 15 min (`mutlib` v4.1, forecast before the run); seal `pred/01_sc145.md` with
sha256 of the harness, scorer, gate, fixtures, `enter_scene.py`, `s51_vidglitch.py`, `sheet142.py` and the 34 call lines. No game run in this step.
**1. Red Team — adversarial review** (`C:/kyty/KytyPS5/docs/session-145/review145.md`): the message filter cannot hide an error message; the
window-event row cannot pass a minimized run; the cross-session pair cannot pair the wrong log or level; the continuity row; the regression is
byte-exact where claimed; the seal.
**2. Harness Engineer — 34 runs and scoring** under the lock, one at a time, in the sealed order; an API check row in `times.txt` before every
call; comments on the series start and end in the cycle task; contact sheet of every video for the lead; no re-run of a failed entry; stop rules as
sealed.
**3. Session Auditor — audit** `docs/session-145/audit/AUDIT145.md`: the protocol of the s144 close (items 273–274, general rule 25 order, sha256 table
of all `instructions/AGENTS.md`) and of steps 0–2 of s145 (general rules 27–28 with the s144 additions); own recount of the scorer outputs including
the video frame count, coverage and continuity, and **the one-frame glitch detector by own code on ≥ 3 videos** (debt D-4); privacy;
`CLAUDE.md` = `AGENTS.md`; MAJOR / MINOR; debts; "Процесс".
**4. Roadmap Lead — close of session 145**: sheets of every V viewed (a row per tag); `SCENE_OK` yes/no per level; map rows; register F rows;
course row 145 by script; "Процесс" applied before the s146 chain; documents; the s146 chain.

## Must not be claimed

60 FPS; that goal (B) makes the game faster or keeps its speed; that any scene is correct or playable to the end (`SCENE_OK` is a hold window
without input at the `-lvl` point); that a level "works" from an entry; that a run proves a defect absent where it did not show it; that the video
of a cold V shows the first seconds of the scene; that the W stop of `w144_09` is a property of a level; who minimized the window; that a minimized
window without validation crashes or does not; that W without precache equals W with precache in the pipelines a level creates; that the B35
pipeline draws right or wrong; that the validation layer would have reported an error after its limit; that a repeated entry equals a cold one;
that the B36 K2 and `PriorityStall:` share one cause; that the inventory is complete; that the glitch detector is right; that B5/B33 frames come
from shader preparation; that the B34 blocks are or are not a defect; any past-session number as a gain or a ceiling; that `bindlean` or B2 is
correct; OLD; 47.98 % as the time of `9235a7ac`.
