# Session 144 — `SCENE_OK` series `sc144`: control W, W of eight `sc143` levels in the no-precache form, V/W pairs of twelve levels (no code)

**Read first:** `ROADMAP.md` "СЕССИЯ 122" item **254** (the s143 close: sheets of the ten V viewed (а); `SCENE_OK` NO 10 of 10 — every W
stopped by validation at start (б); map rows (А) of the ten `sc143` levels (в); new rows **B35** (dual-source blend without `dualSrcBlend`)
and **B36** (K2 on the hold of `pot_treasure_cave`), **B5a K4 → K2** (г); answers to the step 2 questions (д); **the W form until the B35
fix — `KYTY_PIPELINE_PRECACHE=0`, and the cross-session V/W pair (е)**; track F iteration F4 = B35 with its criterion before code (ж);
course row 143 (з); audit and "Процесс" 1–5 (и); **the s144 target and all constants (к)(1)–(7)**; the chain (л)), items **253** (the audit
acceptance: recipe 1592 is the cause of the W stop), **249**, **246**, **242** (the reading rules of `sc143`), 231 (и), 221 (в)–(г), 224;
`C:/kyty/s143/FACTS.md` (steps 0–3) and `docs/local-session-143.md`; `docs/session-143/audit/AUDIT143.md` §2; `C:/kyty/s143/sc143.py`,
`go143a.sh`, `test_sc143.py`, `pred/02_sc143.md` (the port base); `C:/kyty/s143/step4/summary143_viewed.txt` and
`C:/kyty/s142/step4/summary142_viewed.txt` (the regression targets); `docs/track-f/register.md` §10; `ps5 em/CLAUDE.md`;
`ps5 em/docs/env-vars.md`; `ps5 em/docs/agent-team.md` (general rules 5, 15–28).

**Open the report with these facts:** goal (B) since the s140 close — correctness of the game on as many scenes as possible; Sky Garden
speed is neither a goal nor a gate; installed build `9235a7ac…` (`rtskip=1`) with all shipped defaults. Session 143: V entered 10 of 10
never-entered levels; on 120 s `HOLDS_120` 9 / K2 1, on the whole V `HOLDS_120` 8 / K2 2 (`rocket_hourglass` 1.78 s at entry,
`pot_treasure_cave` 6.61 s on the hold); 0 one-frame glitches on 10 videos; sheets viewed, no visible defect; **all 10 W stopped by
validation before the first `GuestOut` line** — the startup precache recreates recipe № 1592 (dual-source blend) and the emulator never
enables `dualSrcBlend` (B35). Distance (course row 143): `SCENE_OK` 1 of 114 (Sky Garden); open defects 35 — K1 2 / K2 3 / K3 6 / K4 17 /
K5 7; 29 of 114 levels ever entered; sessions without a shipping under (B): 1. **The lead's prior [I]:** P(control W passes) ≈ 0.8;
P(W passes | control) ≈ 0.8 per level; P(V without K2 over 330 s, repeated entry) ≈ 0.85 ⇒ ≈ 8–11 new `SCENE_OK`. 60 FPS is not promised.

## Rule of the session

As in sessions 138–143: every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u` at writing;
times in step rows only from `date -u` at the event, written by the same command into `C:/kyty/s144/step<N>/times.txt`; a row about an
event noticed later carries both times with the source (general rule 23); reading an input not earlier than its commit and the
`ROADMAP.md` item named as read; extending a step's scope only by a `ROADMAP.md` item before the action. **No emulator code and no build
in session 144** (the installed `9235a7ac` is the build under measurement; the B35 fix lives in track F, iteration F4). Game runs only by
the Harness Engineer, one at a time, under the lock `C:/kyty/SEALED_RUN.lock` through `procload.py`, only after the seal
`pred/01_sc144.md`; between tags the lock is free and the queue is session > P > F > S; **track links with the lock that are not `done`
at the start of step 2 get the s144 audit link as a blocker** (general rule 27, "Процесс" 1 of s143). **No agent of any track runs a
process or writes a file while the lock exists.** File-system searches only inside `C:/kyty` with a `timeout`, never `find /`; no process
outlives its heartbeat (general rule 28). Logs are read by python in binary mode, never whole; every number from a log is [c] with the
path and sha256; every estimate is [I] with its basis. References to changing documents are pinned `<commit>:<path>:<line>`
(`ps5-em@<commit>:…`) with an anchor map and the +1 positive control (general rule 24(1)). A stop of a running link comes as a comment AND
the file `C:/kyty/s144/STOP` (general rule 26): every command longer than 60 s starts with `[ -e C:/kyty/s144/STOP ] && exit 4`. Commits
only `git commit --only -- <paths>` with the real `C:/Program Files/Git/cmd/git.exe` and `GIT_AUTHOR_*`/`GIT_COMMITTER_*` (platform trap
11). No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives in
`C:/kyty/scrub/`, never in git). A third "Доработать" is never given to one link. Runs and scoring are synchronous in the heartbeat; a
continuation is only a saved Paperclip wake with a checked API answer.

## Chain (item 254 (л)): every specialist step carries an `executionPolicy` review stage by the lead, checked in the API answer

Root `HPP-3` is `blocked` on step 4. Step 0 is created `blocked` on the s143 close link `HPP-301` (general rule 25).

## Steps

**0. Harness Engineer — harness, scorer, regression, calibration, mutants, seal** in `C:/kyty/s144/` (port of `C:/kyty/s143/go143a.sh`,
`sc143.py`, `test_sc143.py`, `fgcpu143.py`): `go144a.sh` — 33 tags in the order of item 254 (к)(1): `w144_00` control W on Sky Garden
(`underwater_aerial_garden`); `w144_01`…`w144_08` — W only for `spring_punch_sky_aztec`, `booster_construction`, `mini_astro_clock_tower`,
`path_maker_mana_tree`, `spring_punch_monster_cave`, `gulliver_island`, `booster_magic_lamp`, `rocket_space_station` (paired with V
`v143_NN` of s143, log sha256 checked against `C:/kyty/s143/step2/times.txt`); then pairs `v144_NN`/`w144_NN`, NN = 09…20:
`rocket_hourglass`, `pot_treasure_cave`, `bumper_enemy_snowy_canyon`, `big_hand_pirate_island`, `timestop_casino`, `ice_iceberg`,
`sponge_dirty_bath`, `hoover_beach`, `volcano_mountain`, `voxel_world`, `enemy_gorilla`, `mini_giants_garden` (last). V — `-lvl`, shipped
defaults, video `KYTY_REC`, hold ≥ 330 s wall, `--attempts 1`, map row marked "repeated entry", forms B5/B5a/B33 kept apart from cold
entries. **W — `--vulkan-validation true` + `KYTY_PIPELINE_PRECACHE=0`**, hold ≥ 310 s, no video; the scorer checks the form by a
positive control (no `PipelinePrecache: N recipes ->` line in a W log, present in V logs of the series; a violation is a tag FAIL).
Scorer `sc144.py` — the rules of `sc143.py` after items 242, 246 with **no change of constants**; `SCENE_OK` per level over its V/W pair
(item 254 (е)); for the eight `sc143` V the sheet row is "viewed" by item 254 (а); "frame with a skipped draw" is read by distinct
`frame=` ids (debt D-7). Stop rules: control W stopped (any death marker or `[Vulkan][E]`) — stop before the first tag, question to the
lead; two W in a row with one stop marker before the first `GuestOut` line — stop; three V in a row "not entered" with one marker — stop.
**Regression without game:** the new scorer reproduces `C:/kyty/s143/step4/summary143_viewed.txt` on the 20 logs of s143 (map, outcomes,
forms, `SCENE_OK` NO 10/10) and `C:/kyty/s142/step4/summary142_viewed.txt` on the 12 logs of s142 — diff printed; calibration 5 of 5;
fixtures `ALL OK` (new edges: a W tag paired with a V of another session; the W form and its violation; W stopped in game after
`GuestOut`; a repeated-entry V); one counted full mutant run ≤ 15 min (`mutlib` v4.1, forecast before the run); seal `pred/01_sc144.md`
with sha256 of the harness, scorer, fixtures, `enter_scene.py`, `s51_vidglitch.py`, `sheet142.py` and the 33 call lines. No game run in
this step.
**1. Red Team — adversarial review** (`C:/kyty/KytyPS5/docs/session-144/review144.md`): the cross-session pair cannot pair the wrong log or
level; the W form control cannot pass a W with precache on; the stop rules count W; the regression is byte-exact where claimed; the seal.
**2. Harness Engineer — 33 runs and scoring** under the lock, one at a time, in the sealed order; an API check row in `times.txt` before
every call; contact sheet of every video for the lead; no re-run of a failed entry; stop rules as sealed.
**3. Session Auditor — audit** `docs/session-144/audit/AUDIT144.md`: the protocol of the s143 close (items 254–255, general rule 25 order,
sha256 table of all `instructions/AGENTS.md`) and of steps 0–2 of s144 (general rules 27–28); own recount of the scorer outputs **including
the video frame count and coverage by own code** (debt D-4); privacy; `CLAUDE.md` = `AGENTS.md`; MAJOR / MINOR; debts; "Процесс".
**4. Roadmap Lead — close of session 144**: sheets of every V viewed (a row per tag); `SCENE_OK` yes/no per level; map rows; register F
rows; course row 144; "Процесс" applied before the s145 chain; documents; the s145 chain.

## Must not be claimed

60 FPS; that goal (B) makes the game faster or keeps its speed; that any scene is correct or playable to the end (`SCENE_OK` is a hold
window without input at the `-lvl` point); that a level "works" from an entry; that a run proves a defect absent where it did not show
it; that the W stop of s143 is a property of a level; that recipe 1592 is the only obstacle for W; that the B35 pipeline draws right or
wrong; that W without precache equals W with precache in the pipelines a level creates; that the B36 K2 and `PriorityStall:` share one
cause; that the inventory is complete; that B5/B33 frames come from shader preparation; that the B34 blocks are or are not a defect; any
past-session number as a gain or a ceiling; that `bindlean` or B2 is correct; OLD; 47.98 % as the time of `9235a7ac`.
