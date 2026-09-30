# Session 142 — scene census `sc142` and a `SCENE_OK` attempt on Sky Garden under goal (B) (no code)

**Read first:** `ROADMAP.md` "СЕССИЯ 122" item **221** (the s141 close: acceptance with the sums by script (а); the rev. 2 amendments
(б); **the first scene frame is out of the entry window, the B5 and B5a criteria (в)**; **the first target under (B) — census `sc142`
and the `SCENE_OK` attempt with all reading constants (г)(1)–(5)**; the s142 chain (д); course row 141 (е); "Процесс" 1–5 (ж); debts
executed (з); the lead's prior (и)), items **215** (в)(2) (`SCENE_OK`, shipping under (B)), **217** (б)–(в) (K2/K3 classes, key-1
order), **218** (г)–(д) (first scene frame, entry window, death markers `--- Fatal Error ---` / `--- Error ---` / `hold_exit`), **219**
(в)–(ж) (row B32, B1a to K4, ranking), **220**; `docs/session-141/inventory141.md` (rev. 2: scene map (А), defect list (Б), census option
(Г) — the reading form of `sc142`); items **128** (г) (death markers), **151** (6) (`s51_vidglitch.py`), §6 (video pass); `ps5 em/CLAUDE.md`;
`ps5 em/docs/env-vars.md` (entry recipes — `KYTY_GUEST_ARGS="-lvl <level>"`, session 67); `ps5 em/docs/agent-team.md` (general rules 5,
15–26); `C:/kyty/s140/enter_scene.py` and `C:/kyty/s122/go122a.sh` (entry harness of s122 — the port base).

**Open the report with these facts:** goal (B) since the s140 close — correctness of the game on as many scenes as possible; Sky Garden
speed is neither a goal nor a gate; installed build `9235a7ac…` (`rtskip=1`) with all shipped defaults. Session 141 (inventory, no game,
no code) shipped nothing. Distance to the goal (course row 141): `SCENE_OK` 0 of 114; open defects 32 — K1 2 / K2 2 / K3 5 / K4 16 / K5 7;
9 of 114 levels ever entered (8 by the game's own marker + `hub_crashsite` by document). The top of the ranking (item 219 (ж)): B5a (cold
Atlantis entry, no presented frame for 1.39 s — one cold entry of one build `2baf8742`), B25, B24, B5 (cold-entry frames above the warm
base — 2 scenes [c] after item 221 (в)), B32. **The lead's prior [I]:** P(≥ 1 of 10 levels not entered or a death marker within 120 s) ≈
0.4; P(≥ 1 of 10 cold entries with a frame ≥ 1 s after the first scene frame) ≈ 0.6; P(Sky Garden `SCENE_OK`) ≈ 0.5; the first shipping
under (B) in s142 with P ≈ 0.4 (only via `SCENE_OK`), otherwise not before s143. 60 FPS is not promised.

## Rule of the session

As in sessions 138–141: every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u` at writing;
times in step rows only from `date -u` at the event, written by the same command into `C:/kyty/s142/step<N>/times.txt`; a row about an
event noticed later carries both times with the source (general rule 23); reading an input not earlier than its commit and the
`ROADMAP.md` item named as read; extending a step's scope only by a `ROADMAP.md` item before the action. **No emulator code and no build
in session 142** (the installed `9235a7ac` is the build under measurement). Game runs only by the Harness Engineer, one at a time, under
the lock `C:/kyty/SEALED_RUN.lock` through `procload.py`, only after the seal `pred/01_sc142.md`. Logs are read by python in binary mode,
never whole; every number from a log is [c] with the path and sha256; every estimate is [I] with its basis. References to changing
documents are pinned `<commit>:<path>:<line>` (`ps5-em@<commit>:…` for the emulator folder) with an anchor map and the +1 positive control
(general rule 24(1) as amended by item 221 (ж)). A stop of a running link comes as a comment AND the file `C:/kyty/s142/STOP` (general rule
26): every command longer than 60 s starts with `[ -e C:/kyty/s142/STOP ] && exit 4`. Commits only `git commit --only -- <paths>` with
the real `C:/Program Files/Git/cmd/git.exe` and `GIT_AUTHOR_*`/`GIT_COMMITTER_*` (platform trap 11). No agent creates user interactions.
`PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives in `C:/kyty/scrub/`, never in git). A third
"Доработать" is never given to one link.

## Chain (item 221 (д)): every specialist step carries an `executionPolicy` review stage by the lead

Root `HPP-3` is `blocked` on step 4. Step 0 is created `blocked` on the s141 close link `HPP-275` (general rule 25).

## Steps

**0. Harness Engineer — harness, scorer, calibration, mutants, seal** in `C:/kyty/s142/` (port of `C:/kyty/s122/go122a.sh` and
`C:/kyty/s140/enter_scene.py`): `go142a.sh` (tags `v142` — Sky Garden `underwater_aerial_garden` video run; `w142` — the same entry with
`--vulkan-validation true`; `c142_01`…`c142_10` — the ten levels of item 221 (г)(1) in that order; `--attempts 1`; hold ≥ 120 s after the
entry line for the census, the sum of `dt_us` after the first scene frame ≥ 300 s for `v142`, a hold ≥ 300 s for `w142`; `KYTY_REC` video
for `v142` and the census; the lock and `procload.py`; the stop rule of item 221 (г)(4) — three levels in a row "not entered" with one
marker); scorer `sc142.py` by item 221 (г)(2)–(3) (entry, first scene frame, outcome, K2, K3 with "no warm base", the per-entry prints,
`SCENE_OK` yes/no with every condition printed; `AsyncPipelines: skipped draw` counted, not fatal); fixtures `test_sc142.py` ending with
`ALL OK` (every condition and every edge — first frame, frame 600 of the window, `dt` = 1 s, 100 ms, 2 999/3 000 frames, 0/1 `[Vulkan][E]`,
each death marker); **calibration on the s122 logs without game — 5 of 5** (item 221 (г)(4)); scorer mutants — `mutlib` v4.1, one counted
full run ≤ 15 min (`--control --no-memo --work-dir/--cache-dir C:/kyty/s142/...`); seal `pred/01_sc142.md` with sha256 of the harness,
scorer, fixtures, `enter_scene.py` and `s51_vidglitch.py`. No game run in this step. Questions on windows or constants not in item 221 —
in the report (general rule 5 of the instructions: "вариант исполнителя" printed next to the letter of the item).
**1. Red Team — adversarial review** of the harness, scorer, fixtures and seal (`C:/kyty/KytyPS5/docs/session-142/review142.md`,
SOUND / SOUND_WITH_CHANGES / UNSOUND, numbered RCs with a failure scenario each): every condition of item 221 (г)(2)–(3) implemented by the
letter; the first-frame rule of (в); hold measured by presented-frame time, not wall time; death markers of item 218 (д)(2); that the
census cannot retry a failed entry; that `SCENE_OK` cannot be printed with a missing run, a missing sheet row or a validation run that
stopped early; calibration and mutant survivors; the seal covers `enter_scene.py` and `s51_vidglitch.py`.
**2. Harness Engineer — runs and scoring** under the lock, one at a time, order `v142`, `w142`, `c142_01`…`c142_10`, each with its row in
`times.txt` and the log copied with sha256 immediately; scorer output per tag and a summary; contact sheets of every video (`ffmpeg`
frames → one sheet per tag) for the lead; no re-run of a failed entry.
**3. Session Auditor — audit** `C:/kyty/KytyPS5/docs/session-142/audit/AUDIT142.md`: the protocol of the s141 close (items 221–222,
general rule 25 order, instruction sha before/after) and of steps 0–2 of s142; own recount of the scorer outputs from the logs by own
parser (entry, first frame, K2/K3, death markers, `[Vulkan][E]`, frame counts); privacy; `CLAUDE.md` = `AGENTS.md` by sha256; MAJOR /
MINOR; debts; "Процесс" (≤ 5 items, lines verbatim).
**4. Roadmap Lead — close of session 142**: the sheet of every video viewed (a row per tag); `SCENE_OK` of Sky Garden yes/no by item 221
(г)(3); the scene map rows of the ten levels; new defect rows by class; p of the B5a and B5 forms on the installed build (k/10); the
choice of the first fix with its criterion named before any code (item 221 (в) or a new item); course row 142; "Процесс" applied before
the s143 chain; documents; brief `docs/next-session-143.md`; the s143 chain before closing.

## Must not be claimed

60 FPS; that goal (B) makes the game faster or keeps its speed; that any scene is correct or playable to the end (`SCENE_OK` is a
hold window without input at the `-lvl` point, nothing more); that a level "works" from a 120-s census entry; that the inventory is
complete; that the census proves a defect absent on a level it did not show; any past-session number as a gain or a ceiling; that the
`bindlean` package or B2 is correct; OLD; 47.98 % as the time of `9235a7ac`.
