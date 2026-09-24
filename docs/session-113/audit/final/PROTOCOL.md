# Audit 113 (final): PROTOCOL lens

Scope: session 113, ROADMAP §0.1 "СЕССИЯ 113 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 14–21. That covers seals 01d
(`vbn113g..j`), 01e (`vbn113k`), 01f (`vbn113m`) and 02 (`shn113`), the video `vid113` with `check113`, mutlib v2, and
the code commits `56a4b4f`, `967d1aa` and `623009f`. The audit was read-only: no game runs, no builds, no git writes.
Every script it ran is in this folder.

## Verdict: the protocol HOLDS. No MAJOR findings. 5 MINOR findings (one is still open), plus INFO notes.

- Every decision in items 14–21 was committed to ROADMAP before the first action it authorises. At HEAD, each item's
  text is byte-identical to the text in its first commit, so nothing was edited afterwards.
- All 72 hash lines in `SEALS113.txt` match the files on disk. The two exceptions are lines 70–71, which lines 74–75
  supersede before the run (see MINOR-1).
- Every run used its sealed pre-registration, its sealed scorer and its sealed binary.
- Every mutant tally reads ALL KILLED, and each tally's "defined" count equals an independent count of the mutants in
  the script.
- No agent, build, mutlib run or commit falls inside any sealed-chain window.

---

## 1. Ordering: HOLDS

Sources for the times below:
- git commit times (author time equals commit time in all 30 commits checked, back to `f505e50`).
- Chain logs `go113d..h.log`.
- File birth/modification times.
- The build log `C:/kyty/build/.ninja_log`, calibrated on `kyty_emulator.exe`.
- The executor's own session transcript
  (<the session transcript>).

`roadmap_items.py` → `roadmap_items.out.txt` checks that the action commits' trees already contain each item.

| Item | ROADMAP commit | What it authorises, with times | Result |
|---|---|---|---|
| 14 | `38fe037` 16:47:57 | `patch_s113c.py` created 16:48:37. Build 16:48:43–16:49:06 (objects 16:48:55, exe linked 16:49:06). Code `56a4b4f` 16:49:13, its tree holds item 14. `make_vbn113d` 16:49:50. pred/01d created 16:51:01. Seal `6ccd896` 16:51:30. | HOLDS |
| 15 | `7f61398` 19:50:30 | Trigger scan of vbn113d 19:50:35. First use of v2 on a sealed scorer: `mut_vbn113d` 19:50:59–19:51:35. | HOLDS |
| 16 | `37aa33f` 19:52:01 | `go113d.sh` started 19:52:26. The vbn113d mutant run came before item 16, but item 15 had already ordered it ("мутанты запечатанного vbn113d → go113d.sh"). Item 16 records "01d runs as sealed" before the chain. | HOLDS |
| 17 | `d93e814` 20:16:29 | `patch_s113d.py` 20:16:41. Exe linked 20:19:09. Code `967d1aa` 20:19:23. `make_vbn113e` 20:21:39. pred/01e 20:22:17. Seal `04ccab5` 20:22:59. Mutants 20:23:04–20:23:41, archived in `9f5acea` 20:23:50. `go113e` 20:24:00. | HOLDS |
| 18 | `e344e34` 20:35:24 | `patch_s113e.py` 20:36:46. Exe linked 20:37:18. Code `623009f` 20:37:46. `make_vbn113f` 20:38:23. pred/01f 20:38:53. One command at 20:39:23 appended the seal lines, made commit `6ce3e0d`, then ran mutlib (done 20:40:09). Tally archived in `c8e0fda` 20:40:17. `go113f` 20:40:21. | HOLDS |
| 19 | `a2e8096` 20:49:47 | `make_shn113b.py` 20:50:20. pred/02 20:55:22. `go113g.sh` 20:55:36. Seal `43c1633` 21:00:37. | HOLDS |
| 20 | `d75fda3` 21:01:07 | The REFUSED attempt (21:00:39–21:00:48) is the finding that led to item 20, not an action taken under it. `mut_shn113_sealed.py` derived 21:01:12 (`assert` that exactly 2 lines were removed). Sealed-copy mutants 21:01:16–21:54:53; draft mutants until 22:00:12. Archived in `ade1cb6` 22:00:27. `go113g` 22:00:28. | HOLDS |
| 21 | `46989bb` 22:12:01 | `make_check113.py` first written 22:13:04 (transcript). Seal lines appended 22:13:24. Mutlib REFUSED. Re-anchored 22:13:33 and re-sealed 22:13:36. Mutants done 22:13:41. Commit `0dea739` 22:13:50, then `go113h` in the next tool call at 22:13:50. | HOLDS (see MINOR-1) |

Checks on the code commits:
- Each patch script's birth time is after its ROADMAP commit: `patch_s113c` 16:48:37, `patch_s113d` 20:16:41,
  `patch_s113e` 20:36:46.
- No emulator link happened between those three builds: the day's links were 16:49:06, 20:19:09 and 20:37:18. So no
  code was built before its item was recorded.

## 2. Seals: HOLDS

`SEALS113.txt` (76 lines) is byte-equal to the git copy `docs/session-113/SEALS113.txt` at HEAD. The copies committed
at each seal commit grow as expected: 29 → 32 → 40 → 42 → 50 → 52 → 62 → 66 → 76 lines.

Recomputed sha256 of every listed file (paths relative to `C:/kyty/s113`; `s112/s113_port.py` resolves to
`C:/kyty/s112`): all OK, except:

- **Lines 70–71** (`mut_check113.py` 13a99c51, `make_check113.py` fa7703a0): the files now hash 7cccc6fb and 89db22e3.
  Lines 73–75 ("re-derived … supersedes …") record the new hashes before the mutant run and before `go113h`. Neither
  file is an input of the vid113 run. See MINOR-1.

Pre-registration pins (scorer constant = file on disk = run meta `prereg`):

| Scorer | PRED_SHA / PRED_BYTES | pred on disk | meta prereg (runs) |
|---|---|---|---|
| vbn113d | 58d0f38b… / 4392 | same | g, h, i, j: same, read_at = chain times |
| vbn113e | c082d54a… / 5062 | same | k: same |
| vbn113f | 8ef6b554… / 2828 | same | m: same |
| shn113 | 75f34c69… / 5452 | same | shn113: same (`PREREG_PINNED` PASS) |

- vid113 has no pre-registration (`prereg` null, by design). `check113.json` records `check_sha256` 2120ed5a, which is
  the sealed value.
- Each score JSON's `scorer_sha256` equals the sealed scorer: 7952a9c8 ×4, 4977228d, 7595b199, c5a582be.
- All score files are dated at their chain times. None was re-scored later, and there were no other tags (no
  vbn113l/n, shn113b or vsn113).
- The pred files, scorers, fixtures, mutant scripts and chains archived in git (`docs/session-113/{pred,tools}`) are
  hash-equal to the sealed local copies.

## 3. Binaries: HOLDS

| Runs | meta `binary_sha256` | Pinned copy (rehashed) |
|---|---|---|
| vbn113g, h, i, j | 5ba0e188… | `kyty_emulator_5ba0e188.exe` OK |
| vbn113k | cf22e223… | `kyty_emulator_cf22e223.exe` OK |
| vbn113m, shn113, vid113 | 1678d3f4… | `kyty_emulator_1678d3f4.exe` OK |

- The chains check the pinned copy's sha, install it, and check the installed sha before every tag. `go113g` and
  `go113h` only check the installed exe.
- The installed exe is 1678d3f4 now (copied 20:40:21 by `go113f`).
- `shn113` integrity `IDENTITY` and `BINARY_SEALED` PASS. `check113` `binary` and `installed_now` PASS.

## 4. Mutants: HOLDS (see MINOR-2 and MINOR-4)

| Tally | Header scorer sha | defined / mutants in script (independent AST count) | Result | Controls |
|---|---|---|---|---|
| mut_vbn113d.out.txt | 7952a9c8 (sealed) | 43 / 43 | ALL KILLED 43/43 | 3/3 survive |
| mut_vbn113e.out.txt | 4977228d (sealed) | 51 / 51 | ALL KILLED 51/51 | 3/3 |
| mut_vbn113f.out.txt | 7595b199 (sealed) | 54 / 54 | ALL KILLED 54/54 | 3/3 |
| mut_shn113.out.txt | c5a582be (sealed) | 315 / 315 (293 literal + 22 from the schema loop) | ALL KILLED 315/315 | 3/3 |
| mut_shn113_draft2.out.txt | 830bcbb8 (draft `s106_stage/shn113b/shn113.py`) | 317 defined, `--only` 2 | ALL KILLED 2/2 | none (no `--control`, MINOR-2) |
| mut_check113.out.txt | 2120ed5a (sealed) | 31 / 31 | ALL KILLED 31/31 | 3/3 |

- All tallies name mutlib v2, sha 877eb53a. That equals the current `s106_stage/mutlib/mutlib.py` (last modified
  17:31:32) and the git archive `docs/session-113/mutlib/v2/mutlib.py`.
- The d/e/f tallies name the fixture and mutant files under `C:/kyty/s106_stage/` rather than the sealed `s113` copies.
  Their recorded hashes (42bb5ee6, 9c4fd32c, 9c5d713c, d8ecaa1a, d66b379e, 0ea43059) equal the sealed ones, so the
  content was the sealed content (INFO).
- **`mut_shn113_sealed.py`**: `diff` against `mut_shn113.py` shows exactly two deleted lines (341–342):
  `CONST_pred_sha_prefilled` and `CONST_pred_bytes_prefilled`. Those are the two mutants item 20 names. The derivation
  asserted that exactly 2 lines were removed.
- The draft scorer used for the 2 draft-only mutants differs from the sealed `shn113.py` only in lines 55–56
  (`PRED_SHA` and `PRED_BYTES` = None).
- Order in every case: seal lines, then seal commit, then mutlib run, then tally hashed into SEALS and archived. The
  tallies are dated after their seal commits: 19:51:35 > 16:51:30, 20:23:41 > 20:22:59, 20:40:09 > 20:39:23,
  21:54:53 > 21:00:37, 22:13:41 > 22:13:36 (re-seal).

## 5. Concurrency: HOLDS (INFO notes only)

Chain windows (from the chain logs): go113d 19:52:26–20:14:28, go113e 20:24:00–20:29:30, go113f 20:40:21–20:45:54,
go113g 22:00:28–22:11:05, go113h 22:13:50–22:16:27. Evidence is in `concurrency_scan.py` → `concurrency_scan.out.txt`.

- **Files under `C:/kyty` last written inside a window:** only each run's own outputs (log, stdout, meta, gpuclk/cpuclk,
  score, video). The one other write is the `0dea739` commit and `LOOP_STATE.md` at 22:13:50. The transcript shows that
  command returned before the chain was launched.
- **No mutlib writes** (`mutlib/work` and `cache`) and no generator or patch writes inside any window.
- **No emulator build inside any window.** The day's links were 16:49:06, 20:19:09 and 20:37:18.
- **Transcripts:** no subagent or workflow transcript has an entry inside any window.
  - The mutlib-v2 workflow's last agent entry was 19:49:35. The audit agents start at 22:17 or later, after the video.
  - In the main session, the only tool calls inside windows are the chain launches and `ScheduleWakeup`. The heartbeats
    at 19:57:31 and 20:27:30 were answered without tool calls.
- **Mutlib runs vs chains:** each mutlib run ended before its chain started.
  - vbn113d 19:51:35 < 19:52:26
  - vbn113e 20:23:41 < 20:24:00
  - vbn113f 20:40:09 < 20:40:21
  - shn113 sealed 21:54:53 and draft 22:00:12 < 22:00:28
  - check113 22:13:41 < 22:13:50
- **Meta `pre_run` gpu_util median:** g 2, h 2, i 2, j 0, k 1, m 1, shn113 1, vid113 1 (the limit is 10).
- **INFO:** the 28-worker shn113 mutant pass (3 217 s wall, 81 938 worker-s) ended 16 s before `go113g`.
  - Its workers had exited: none appears in the `pre_run` top-20 at 22:00:31, although each would carry about
    2 900 CPU-s.
  - The machine's thermal state after an hour of full CPU load was not controlled. ABBA ordering absorbs drift, and
    this is not a protocol breach.
- **INFO:** during go113d–f two other `claude` processes (pids 46284 and 2072) were alive, using about 0.8 CPU-s/min
  each. The daemon log identifies them as idle background workers of another project (<another project>; jobs
  `80b102d3` and `b1ad55a1`). The daemon retired `b1ad55a1` at 22:14:47, during `vid113`. They are not programme
  agents and did no work.
- **INFO:** a hung background `rtk grep` (task `bxzwsc3eg`, started 20:16:43) was stopped with TaskStop at 20:23:56,
  3–4 s before `go113e`. Its output file never grew after that. From file evidence I cannot rule out an idle orphaned
  child process.

## 6. Generators and fixtures: HOLDS (the item-16 loss is the only one)

**Generators.** `make_vbn113e.py`, `make_vbn113f.py`, `make_shn113b.py` and `make_check113.py` (the s113 copies are
hash-equal to the `s106_stage` copies) each assert all three conditions:
- `a.endswith('\n') and b.endswith('\n')`
- `s.startswith(a) or ('\n' + a) in s`
- `s.count(a) == 1`

Together these force a single occurrence that starts at a line start and ends at a newline, i.e. whole lines.
`make_vbn113d.py` asserts only `s.count(a) == 1`: this is the prefix-anchor defect.

**The defect is documented** in ROADMAP item 16 (line 1468, "якорь … был ПРЕФИКСОМ строки `test_vbn113c.py:185`").
It is visible in `test_vbn113d.py:186`: `(dict(race=1), 'B1', True),  # B1 reads BAD, which races never enter
(bad_race) (dict(nmiss=1), 'B1', False),`.

**Case-list comparison** (`cmp_fixtures.py` → `cmp_fixtures.out.txt`; static AST, nothing run):

| Step | Cases | EDGES | Lost | Added / changed |
|---|---|---|---|---|
| c → d | 63 → 63 | 19 → 19 | EDGE `(dict(nmiss=1),'B1',False)` (the documented loss). `INVESTIGATE_race` became `GO_race`, as item 14 intends. `GO_tag_d/e/f` renamed to `GO_tag_h/i/j` (the tags). | EDGE `(dict(race=1),'B1',True)` |
| d → e | 63 → 70 | 19 → 20 | `GO_tag_h/i/j` (tags) | `ENV_SHIFT_*` ×2, `GC_LINE_*` ×7, `GO_tag_l`; the nmiss B1 EDGE restored |
| e → f | 70 → 72 | 20 → 22 | `GO_tag_l` (tag) | `GO_stall`, `GO_tag_n`, `ROWS_field_prio`, B7 edges ×2 |

- The other named fixtures (`make(...)` and `armed_edge(...)`, 7 in each version) are unchanged.
- No other fixture was lost. The `diff` of draft `shn113_draft/test_shn113.py` against sealed `test_shn113.py` shows
  only additions: `ENV_EXPECTED`, the four new schema fields, the `shift` parameter and `V_shift`/`V_shift_wrong`.
- The `diff` of `test_check112.py` against `test_check113.py` also shows only additions (8 cases, plus the new
  fields and constants).

---

## Findings

**MINOR-1: the check113 mutant script and its generator changed after their seal line, with no ROADMAP record.**
- At 22:13:24 the executor appended SEALS lines 67–72, which pin `mut_check113.py` 13a99c51 and `make_check113.py`
  fa7703a0.
- mutlib then REFUSED: "mutant def_cspfree: anchor found 0 times".
- At 22:13:33 the generator was edited so that `def_cspfree` anchors on the check113 form of the line. At 22:13:36
  both files were regenerated and re-sealed (lines 73–75, "supersedes").
- This supersession is visible in SEALS and git, but no ROADMAP item records it. Item 20's rule covers only mutants
  that anchor on an unfilled seal.
- The first versions are recoverable only as hashes: git holds only the final files.
- No run input changed: `check113.py` 2120ed5a and `test_check113.py` f8415d98 are the same before and after. The new
  mutant removes the same `cspfree` clause as before.

**MINOR-2: the draft-only shn113 mutants ran without `--control`, and their draft scorer was not pre-hashed.**
- Item 15(b) and pred/02 §2 require `--control --no-memo`. The draft run used `--only … --no-memo`, so it had no
  control mutants. Its BASELINE did survive.
- The draft scorer `s106_stage/shn113b/shn113.py` (830bcbb8) has no SEALS line. It appears only in the tally header.
- The effect is small: 2 mutants, and the scorer differs from the sealed one only in the two unfilled `PRED_*` lines
  (verified).

**MINOR-3 (OPEN at audit time, due in the close of item 21(3)): promised records are missing.**
- Item 16 says "дефект — в FACTS и в долг §7". Item 15(г) makes mutlib v3 a "долг §7". Item 18 names the debt
  "ожидание неподанного тика".
- ROADMAP §7 (line 2803 on) has no row for any of the three. Its session-113 rows are lines 2873–2877.
- `C:/kyty/s113/FACTS.md` was last written at 13:17:38, so it holds nothing from items 11–21.

**MINOR-4: the item 15(b) trigger scan is on record only for vbn113d.**
- The transcript shows the scan at 19:50:35 for vbn113d only. It shows no scan of vbn113e/f, the sealed shn113 or
  check113 before their mutant runs.
- The auditor re-ran the review3 scan logic read-only (`scan_derived.py` → `scan_derived.out.txt`). All six suites
  pass: exit expression `0 if ok else 1`; `ok &=` operands `passed` / `not differ`, none inside `try`; one mutant
  collection; no raw stdout writes.
- So the missing scan has no effect on any verdict.

**MINOR-5 (pre-existing convention): run inputs that are not hash-listed.**
- `enter_scene.py` launches the game and writes each run's meta (env, pre_run, prereg). Its sha is a69fa919, and its
  mtime 09:04:12 equals the port time, before every seal. The port script is sealed (04cfa646).
- `C:/kyty/scripts/s51_vidglitch.py` feeds `check113`'s glitch count. Its mtime is 2026-09-13.
- No SEALS file from sessions 102–113 lists `enter_scene.py`. There is no evidence either file changed.

**INFO**
- The heavy mutant pass ended 16 s before the ABBA run (section 5).
- The idle foreign Claude daemon workers; one was retired during vid113 (section 5).
- The stopped hung grep task (section 5).
- `ScheduleWakeup` calls were made inside the windows. They only register a wake-up and start no process.
- In every s113 meta, `started` equals `finished` (both are written at the end). The start time is in `launched`.

## Evidence files (this folder)

- `roadmap_items.py` / `.out.txt`: the first commit that holds each item, the HEAD-vs-first text identity, and whether
  the action trees contain the item.
- `cmp_fixtures.py` / `.out.txt`: the case lists of `test_vbn113c`, `d`, `e` and `f`.
- `scan_derived.py` / `.out.txt`: the item 15(b) trigger scan on the derived suites (read-only, `-B`).
- `concurrency_scan.py` / `.out.txt`: last writes in the windows, transcript entries in the windows, and the day's
  builds.
- `tx_window.py`: prints the executor transcript for a time window (used for the tables above).
