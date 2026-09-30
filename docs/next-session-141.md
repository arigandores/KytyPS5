# Session 141 — correctness and scene inventory under goal (B) (no game, no code, no build)

**Read first:** `ROADMAP.md` "СЕССИЯ 122" item **215** (the s140 close: the fork answer (B) read by its consumer (а); `pm4c140` not read —
stopped by item 214 (б); the reference course table closed by row 140 and **the course form under (B)** — what counts as shipping,
`SCENE_OK`, the distance to the goal (в); the goal in the documents (г); **the s141 constants — chain, inventory form (А)–(Д), ranking
rule, the lead's prior (д)**; audit and "Процесс" of s140 moved into this session's audit (е); the `CLAUDE.md` revision (ж)), item
**214** (the user's answer (B): the program goal becomes game correctness on as many scenes as possible; the census stopped; the s141
frame), items **128** (г) (death markers), **151** (6) (`s51_vidglitch.py`), §6 (video pass), §7 (debts), §3 "Что закрыто";
`ps5 em/CLAUDE.md`; `ps5 em/HANDOFF.md` §4 (tests) and the entries named by the inventory; `ps5 em/docs/env-vars.md` (entry recipes by
session); `ps5 em/docs/agent-team.md` (general rules 5, 15–25); the lead's note `C:/kyty/s140/lead/inventory_B_notes.md`
(`ec509375…`, [I-agent], NOT verified line by line — leads to check, not facts).

**Open the report with these facts:** the program goal changed at the s140 close by the user's answer (B) on `HPP-261`: **correctness
of the game on as many scenes as possible** (picture, crashes, hangs, level entry and hold); Sky Garden speed is no longer a goal nor a
gate; the installed build stays `9235a7ac…` (`rtskip=1`) with all shipped defaults. Session 140 shipped nothing: the PM4 census
`pm4c140` stopped at step 2 without a game run (drafts parked, `docs/session-140/step2/`). The reference speed course is closed by row
140 (47.98 % repeated; 12 sessions without speed shipping). Under (B): `SCENE_OK` count 0 of 114 (the criterion is new; 7 levels were
entered in the past with evidence of other forms), the defect list is not yet built. **The lead's prior [I]:** P(the list holds a
K1/K2 defect reproducible at ≤ 300 s of game per entry) ≈ 0.6; P(the first target chosen at the s141 close is a scene census) ≈ 0.5;
the first shipping under (B) not before s143. 60 FPS is not promised.

## Rule of the session

As in sessions 138–140: every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u` at writing;
times in step rows only from `date -u` at the event, written in the same command into `C:/kyty/s141/step<N>/times.txt`; a row about an
event noticed later carries both times with the source (general rule 23); reading an input not earlier than its commit and the
`ROADMAP.md` item named as read; extending a step's scope only by a `ROADMAP.md` item before the action. **No game, no emulator code, no
build, no lock in session 141.** Logs are read only by python in binary mode, never whole; every number from a log is [c] with the path
and sha256; every estimate is [I] with its basis. Every file:line reference is checked at HEAD `main` and collected in a map file with
sha256 (as general rule 24(1)). Commits only `git commit --only -- <paths>` with the real `C:/Program Files/Git/cmd/git.exe` and
`GIT_AUTHOR_*`/`GIT_COMMITTER_*` (platform trap 11). No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the
whole tree before commits (the list lives in `C:/kyty/scrub/`, never in git). A third "Доработать" is never given to one link.

## Chain (item 215 (д)(1)): every specialist step carries an `executionPolicy` review stage by the lead

Root `HPP-3` is `blocked` on step 3. Step 0 is created `blocked` on the s140 close link `HPP-271` (general rule 25).

## Steps

**0. Lever Researcher — inventory** `C:/kyty/KytyPS5/docs/session-141/inventory141.md` (the lead commits it at acceptance), maps in
`C:/kyty/s141/step0/` with sha256, section `## Step 0` of `C:/kyty/s141/FACTS.md`. Form of item 215 (д)(2): (А) **scene map** — all 114
levels of `games/PPSA21564-app/data/prein/product_levels.xml` (path and sha256), one row per level: entered in the emulator (yes/no),
evidence (session, tag, log with sha256 if it exists, else document file:line), outcome {holds / hang / crash / never entered /
unknown}, build of the last entry; (Б) **defect list** — one row per defect: class K1 crash, K2 hang or device lost, K3 visible picture,
K4 translator/decoder gap without a proven visible symptom, K5 tool/harness/test; status {open / partial / closed: item}; evidence
file:line at HEAD; scenes affected; reproduction cost (game seconds, entries, user needed, p per entry [c] or [I] with basis); proof
criterion of a fix by item 215 (в)(2)(i); P(fix provable within ≤ 2 sessions) [I] with basis; (В) **ranking by the rule of item 215
(д)(2)(В)** (K1/K2 on entry or hold > K3 > K4 > K5; then scenes affected; then reproduction cost; ties by P) — the top five rows are a
proposal, not a decision; (Г) **scene-census option** for s142 — up to 10 never-entered levels, one entry ≤ 120 s each with video, cost
in minutes of game; (Д) every line of `inventory_B_notes.md` confirmed by a reference or struck with the reason. Your P(K1/K2 at ≤ 300 s
per entry) before the reading, with `date -u`.
**1. Red Team — adversarial review** `C:/kyty/KytyPS5/docs/session-141/review141.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, numbered
RCs with a failure scenario each): every reference of the map files opened at HEAD; every level-status row against its evidence;
missed defects (§7 debts, HANDOFF §4 tests, crash/hang signatures of the s122 entries, `AsyncPipelines: skipped draw`, BVH); the
ranking rule applied as written; reproduction costs and p per entry; that no row claims a scene is correct or `SCENE_OK`.
**2. Session Auditor — audit** `C:/kyty/KytyPS5/docs/session-141/audit/AUDIT141.md`: the protocol of session 140 (items 212–214, the
stop of the census, step 2 handed in as WIP and its own "Процесс": item 214 read 20 min after its commit, file creation without
`times.txt` rows; item 214 (в)) and of steps 0–1 of s141 (time rows against commits and items, acceptances, privacy, `CLAUDE.md` =
`AGENTS.md` by sha256); MAJOR / MINOR; debts; the "Процесс" section (item 113 (б), ≤ 5 items, lines verbatim) — including any agent
instruction that contradicts goal (B) (item 215 (г)).
**3. Roadmap Lead — close of session 141**: acceptance of the inventory and the review as items; the choice of the first target under
(B) (a fix from the ranked list or the scene census) with its proof criterion named before any code or game run; course row 141 of the
(B) table; audit and "Процесс" lines, applied before the s142 chain (general rule 25); documents (`FACTS.md` → `docs/local-session-141.md`,
`HANDOFF.md`, `CLAUDE.md` = `AGENTS.md`, `docs/agent/`, `agent-team.md` entry point, `C:/kyty/LOOP_STATE.md`); brief
`docs/next-session-142.md`; commit of both repositories; the s142 chain before closing.

## Must not be claimed

60 FPS; that goal (B) makes the game faster or keeps its speed; that any scene is correct, playable to the end or `SCENE_OK` (no scene
has been checked by that criterion); that the inventory is complete; any past-session number as a gain or a ceiling; that the PM4 census
would have found a lever or that the outside-mutex residual is or is not removable; that the `bindlean` package or B2 is correct; OLD;
47.98 % as the time of `9235a7ac`.
