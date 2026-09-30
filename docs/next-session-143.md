# Session 143 — `SCENE_OK` series `sc143` on 10 never-entered main levels under goal (B) (no code)

**Read first:** `ROADMAP.md` "СЕССИЯ 122" item **231** (the s142 close: sheets (а); **Sky Garden `SCENE_OK` — YES, the first shipping under
(B) (б)**; scene map rows of the ten `sc142` levels (в); new rows B33 and observation B34, B1b/B3b/B26/B9 updates (г); forms B5a 0/10 → K4,
B5 7/10 and 6/10, N = 4 (д); **the first fix under (B) — B26 by track F iteration F1, cold entry by track S (е)**; course row 142 (ж);
audit and "Процесс" 1–5, general rule 27 extended to tracks P/F/S (з); **the s143 target and all constants (и)(1)–(6)**; the chain (к);
debts (л)), items **221** (в)–(г) (first scene frame, reading of the entry, `SCENE_OK` conditions), **223**–**225** (answers of the lead,
RC1–RC10 of the s142 review, seal `02`), **228** (в) (track F executes fixes under (B)), **229** (б)–(в) (track S owns B5/B5a, the lock queue
session > P > F > S), **230**; `C:/kyty/s142/FACTS.md` (steps 0–3) and `docs/local-session-142.md`; `C:/kyty/s142/sc142.py`,
`go142a.sh`, `test_sc142.py`, `pred/02_sc142.md` (the port base); `C:/kyty/s142/step4/summary142_viewed.txt` (the regression target);
`docs/session-141/inventory141.md` (map (А)); `ps5 em/CLAUDE.md`; `ps5 em/docs/env-vars.md`; `ps5 em/docs/agent-team.md` (general rules
5, 15–27).

**Open the report with these facts:** goal (B) since the s140 close — correctness of the game on as many scenes as possible; Sky Garden
speed is neither a goal nor a gate; installed build `9235a7ac…` (`rtskip=1`) with all shipped defaults. Session 142 shipped the first
`SCENE_OK` (Sky Garden: V 334.1 s after the first scene frame, 10 176 frames, 0 frames ≥ 1 s, video 10 567 frames 0 glitches, sheet viewed;
W validation 310.0 s, 0 `[Vulkan][E]`). Census `sc142`: 10 of 10 never-entered levels entered, held 120 s, K2 0, death markers 0; B5 form
7/10 (6/10 without `c142_10`), B5a 0/10. Distance (course row 142): `SCENE_OK` 1 of 114; open defects 33 — K1 2 / K2 1 / K3 6 / K4 17 /
K5 7; 19 of 114 levels ever entered. Fixes run in tracks F (B26 first) and S (cold entry). **The lead's prior [I]:** P(entered) ≈ 0.9 per
level; P(`SCENE_OK` | entered) ≈ 0.75 ⇒ ≈ 6–7 new `SCENE_OK` expected; P(≥ 1 K1/K2 in 10) ≈ 0.4. 60 FPS is not promised.

## Rule of the session

As in sessions 138–142: every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u` at writing;
times in step rows only from `date -u` at the event, written by the same command into `C:/kyty/s143/step<N>/times.txt`; a row about an
event noticed later carries both times with the source (general rule 23); reading an input not earlier than its commit and the
`ROADMAP.md` item named as read; extending a step's scope only by a `ROADMAP.md` item before the action. **No emulator code and no build
in session 143** (the installed `9235a7ac` is the build under measurement). Game runs only by the Harness Engineer, one at a time, under
the lock `C:/kyty/SEALED_RUN.lock` through `procload.py`, only after the seal `pred/01_sc143.md`; between tags the lock is free and the
queue is session > P > F > S. **No agent of any track runs a process or writes a file while the lock exists (general rule 27).** Logs are
read by python in binary mode, never whole; every number from a log is [c] with the path and sha256; every estimate is [I] with its basis.
References to changing documents are pinned `<commit>:<path>:<line>` (`ps5-em@<commit>:…`) with an anchor map and the +1 positive control
(general rule 24(1)). A stop of a running link comes as a comment AND the file `C:/kyty/s143/STOP` (general rule 26): every command longer
than 60 s starts with `[ -e C:/kyty/s143/STOP ] && exit 4`. Commits only `git commit --only -- <paths>` with the real
`C:/Program Files/Git/cmd/git.exe` and `GIT_AUTHOR_*`/`GIT_COMMITTER_*` (platform trap 11). No agent creates user interactions.
`PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives in `C:/kyty/scrub/`, never in git). A third
"Доработать" is never given to one link. Runs and scoring are synchronous in the heartbeat; a continuation is only a saved Paperclip wake
with a checked API answer (trap (5) as amended by item 231 (з)).

## Chain (item 231 (к)): every specialist step carries an `executionPolicy` review stage by the lead

Root `HPP-3` is `blocked` on step 4. Step 0 is created `blocked` on the s142 close link `HPP-281` (general rule 25).

## Steps

**0. Harness Engineer — harness, scorer, regression, calibration, mutants, seal** in `C:/kyty/s143/` (port of `C:/kyty/s142/go142a.sh`,
`sc142.py`, `test_sc142.py`): `go143a.sh` — tags in pairs `v143_NN`, `w143_NN` for NN = 01…10 in the order of item 231 (и)(1)
(`spring_punch_sky_aztec`, `booster_construction`, `mini_astro_clock_tower`, `path_maker_mana_tree`, `spring_punch_monster_cave`,
`gulliver_island`, `rocket_hourglass`, `pot_treasure_cave`, `booster_magic_lamp`, `rocket_space_station`); V — `-lvl`, video `KYTY_REC`,
hold ≥ 330 s wall, `--attempts 1`; W — the same entry with `--vulkan-validation true`, hold ≥ 310 s, no video; the lock and `procload.py`;
at the end of every run inside the lock a `times.txt` row with CPU of foreign processes (debt D-4); the stop rule — three V in a row "not
entered" with one marker. Scorer `sc143.py` — the rules of `sc142.py` after item 224 with **no change of constants**: from each V the map
row (А) and the forms B5 / B5a / B33 (window 599 frames after the first scene frame, "no warm base", hold); `SCENE_OK` per level over its
V/W pair with every condition of item 221 (г)(3) and item 224 printed, the row "sheet of V viewed by the lead" filled by the close.
**Regression without game:** the new scorer on the 12 logs of s142 reproduces `C:/kyty/s142/step4/summary142_viewed.txt` (map rows,
outcomes, B5/B5a k/10, Sky Garden `SCENE_OK` YES) — diff printed; **calibration 5 of 5** on the s122 logs (item 221 (г)(4)); fixtures
`ALL OK` (every new edge: a level with V but no W, W without V, a pair with W stopped early, two levels in one summary); one counted full
mutant run ≤ 15 min (`mutlib` v4.1, `--control --no-memo --work-dir/--cache-dir C:/kyty/s143/...`, forecast before the run); seal
`pred/01_sc143.md` with sha256 of the harness, scorer, fixtures, `enter_scene.py`, `s51_vidglitch.py`, `sheet142.py` and the 20 call lines.
No game run in this step. Questions on windows or constants not in item 231 — in the report ("вариант исполнителя" next to the letter).
**1. Red Team — adversarial review** (`C:/kyty/KytyPS5/docs/session-143/review143.md`, SOUND / SOUND_WITH_CHANGES / UNSOUND, numbered RCs
with a failure scenario each): the generalisation of `SCENE_OK` to a level pair cannot mix levels or accept a pair with a missing or
early-stopped member; the census reading of a cold V is the reading of `sc142`; the regression is byte-exact where it claims so; the
foreign-CPU row; calibration and mutant survivors; the seal.
**2. Harness Engineer — 20 runs and scoring** under the lock, one at a time, order `v143_01`, `w143_01`, …, `v143_10`, `w143_10`, each with
its `times.txt` row and the log copied with sha256 immediately; scorer output per tag and a summary; contact sheet of every video for the
lead; no re-run of a failed entry; stop rule as sealed.
**3. Session Auditor — audit** `C:/kyty/KytyPS5/docs/session-143/audit/AUDIT143.md`: the protocol of the s142 close (items 231–232, general
rule 25 order, instruction sha before/after — table of all `instructions/AGENTS.md`) and of steps 0–2 of s143 (general rule 27: no track
work under the lock — mtime of files of `C:/kyty/p283`, `C:/kyty/f287`, `C:/kyty/s288` against `lock.log`); own recount of the scorer
outputs by own parser; privacy; `CLAUDE.md` = `AGENTS.md` by sha256; MAJOR / MINOR; debts; "Процесс" (≤ 5 items, lines verbatim).
**4. Roadmap Lead — close of session 143**: the sheet of every video viewed (a row per tag); `SCENE_OK` yes/no per level; map rows (А) of
the ten levels; new defect rows by class into the track F register; course row 143; "Процесс" applied before the s144 chain; documents;
brief `docs/next-session-144.md` (candidate: `SCENE_OK` of the ten `sc142` levels, the three remaining main levels); the s144 chain.

## Must not be claimed

60 FPS; that goal (B) makes the game faster or keeps its speed; that any scene is correct or playable to the end (`SCENE_OK` is a
hold window without input at the `-lvl` point, nothing more); that a level "works" from a census entry; that the census proves a defect
absent on a level it did not show; that the inventory is complete; that the B34 title-card blocks are or are not a defect; that B5/B33
frames come from shader preparation (before S0 and S-warm); any past-session number as a gain or a ceiling; that the `bindlean` package
or B2 is correct; OLD; 47.98 % as the time of `9235a7ac`.
