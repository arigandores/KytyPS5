# Session 121 audit — lens PROTOCOL

Read-only audit. Nothing was edited, built, run or committed. The only file written is this report.
Evidence used:
- git timestamps of `docs/ROADMAP.md` and `docs/session-121/**` (commits `6339dc8` … `a14a2c6`);
- file creation and modification times under `C:/kyty/s121`;
- `go121a.log` and `C:/kyty/LOOP_STATE.md`;
- **the lead's own session transcript** and the transcripts of the three workflows (design `wf_2dfe4828`,
  implementation `wf_9efc6b82`, scorers `wf_4564dc3e`). These give the exact second of every tool call, which settles
  ordering questions that file timestamps alone cannot.
- every sealed file, re-hashed with sha256.

All times are local (+02:00).

## Verdict

**PROTOCOL HOLDS, with one MAJOR finding (outcome-neutral), four MINOR findings and several notes.**

These hold:
- Both seals preceded their runs.
- Every sealed sha matches everywhere it appears (disk, git copies, mutlib headers, `go121a.log`).
- No game was launched outside the two sealed runs.
- Nothing heavy ran during either sealed run.
- No user name, e-mail address or launcher user name appears in the committed session-121 files or commit messages.

The MAJOR finding is the arming floor. The lead set it at +300 in a workflow brief at 13:38:31, which departs from
the +800 floor of RC8 that item 2 accepted. It reached ROADMAP only at 16:13:41 (item 5), and item 5 presents it as
the fixer agent's paragraph. It changes no verdict: the measured arming was +1 388 in vfy121 and +1 434 in shp121,
far above either floor.

## 1. Items 1–8: recorded before the actions they govern?

| item | ROADMAP commit | governed action (first act) | order |
|---|---|---|---|
| 1 order/scope | `6339dc8` 12:13:29 | harness port `cp … C:/kyty/s121` 12:13:34; `Player` substitution 12:13:41; design workflow 12:14:04 | OK |
| 2 design accepted | `530f6aa` 12:45:45 | impl workflow launched 12:46:05; first code artefact `patches/renderMemo8.h.in` 12:52:10, `patch_texmemo8.py` 12:54:19 | OK (design files 12:29–12:45 were authorised by item 1(1)) |
| 3 build + code review | inside code commit `5e8e1d2` 13:14:44 (patch applied 13:14:42 in the same command as `git add`) | smoke chain 13:15:13; scorer workflow 13:38:31 | OK for "before the commit, smoke and scorers". The code itself (12:54–13:11) was authorised by item 2. The agent's deviations from the design (31 counters, R2 off by layout, the direct-shadow reset at three sites) and the review fix (`always_inline`, 13:11:22) came **before** item 3 accepted them. That is disclosed ("Принимаю отклонения агента"). NOTE. |
| 4 two seals | `8c42ff9` 13:37:00 | chain rewritten for vfy121/shp121 13:37:22; scorer workflow 13:38:31 | OK. The smoke chain was stopped (TaskStop 13:36:30, taskkill 13:36:36) **before** item 4, so the change of plan followed a stop, not a run. |
| 5 arming floor, RC8 ceiling, chain gate | `ea7c698` 16:13:41 | floor ≥ 300 set in the lead's scorer brief at **13:38:31**; chain gate written by the fixer agent at **15:33:04** (`go121a.sh`), `chk_vfy121.py` at 15:32:12; agent drafted the paragraph at 15:33:37 | **FAIL (floor): see MAJOR-1.** The chain gate is implemented under item 4 ("запускается только после ПРОХОДА печати 01", 13:37:00). Only its mechanics (vfytag, `chk_vfy121.py` conditions) were recorded after the fact. MINOR-3. |
| 6 seal 01 PASS | `5389e16` 16:54:22 | seal 02: `seal121_02.py` run after the commit in the same command (16:54:22+); mutlib on sealed shp121 at 16:54:46 | OK. However, `pred/02_shp121.md` was **written at 16:54:13, 9 s before** item 6 was applied, and it already cites item 6. NOTE. |
| 7 suite repair | `60a60bf` 17:06:47 (patch file written 17:06:45) | **Edit of `test_shp121.py` 17:06:25**; suite run 17:06:26–34 | **After, by 22 s.** The item says "записано до правки". MINOR-2. The lead's admission of "minutes" overstates the gap, which was 22 s. The edit's own comment already cites "ROADMAP s121 item 7". The second full mutlib started at 17:06:53, after the record. |
| 8 seal 02 verdict | `a14a2c6` 17:25:07 | score 17:24:34–40; audit workflow 17:25:35; reinstall of d3a981a2 17:25:11 | OK ("записано до аудита" holds). |

### MAJOR-1 — the arming floor changed before it was recorded, and item 5 misattributes it

- Item 2 (12:45:45) accepted **all** required changes RC1–RC8 of `texmemo8_review.md`. RC8/S4 (review lines 332–335)
  says to keep NOT_EVALUABLE "only below +800 or above that ceiling".
- The lead's scorer-workflow brief at 13:38:31 instructed "tex_hits above mode 0 by at least 300 a frame, and key misses
  … below by at least 300 a frame" for vfy121, and the same for shp121. No ROADMAP line covered this.
- Item 4 (13:37:00) gives no number ("tex_hits выше, промахи ключа ниже").
- The shp121 pre-seal checker caught the gap as a blocking finding ("The arming rule departs from a recorded decision
  without its own …; fix: add a line to ROADMAP s121, e.g. item 4a"). The fixer drafted `patch_roadmap121_5.py` at
  15:33:37 and wrote there that the floor "stays as the spec says".
- The lead committed that draft at 16:13:41 as item 5, "абзац агента-исправителя … ПРИНЯТ мной этой строкой без
  изменений". So the decision is recorded **2 h 35 min after** it was acted on. The record also presents it as the
  agent's, although the lead's brief originated it.
- It was recorded before seal 01 (16:14:43), so both sealed rules contain it legitimately. It has no effect on any
  verdict: +1 388 and +1 434 clear +800 as well.
- Rule violated: "decisions in ROADMAP before actions". The programme's pre-seal check did its job here.

### MINOR-2 — item 7's text says it came before the edit; it came 22 s after

The Edit call is at 17:06:25. `patch_roadmap121_7.py` was written at 17:06:45 and committed at 17:06:47. Only fixtures
were added (the Edit's old and new strings were checked: three `check(...)` calls plus a probe JSON). The scorer and
pred are unchanged (`46f8cadc…`, `3b951163…`). No run happened in between.

## 2. Agent edits: tagged and accepted?

- **Item-5 paragraph.** The agent's draft (fixer `agent-aa428a45…`, Write at 15:33:37) and the committed patch differ
  only in the heading: "4a." became "5.", and the tag "абзац агента-исправителя после проверки до печати; принимается
  явно" became "… `shp121` … ПРИНЯТ мной этой строкой без изменений". So "без изменений" is true of the body. The
  paragraph is tagged and accepted explicitly. The origin of the +300 floor is misstated (MAJOR-1).
- **Chain gate in `go121a.sh`.** Written by the fixer at 15:33:04, re-read by the lead, and accepted through item 5(3).
  The script's header cites item 4, which does authorise "shp121 only after a PASS of seal 01". The file carries no
  agent tag of its own, but its acceptance is recorded. MINOR-3 is only that the mechanics came 40 min before their
  ROADMAP line.
- **Pred sections.** Both preds were written by the lead: `pred/01_vfy121.md` at 16:14:19, then `fix_pred01_121.py` at
  16:14:43; `pred/02_shp121.md` at 16:54:13. Pred 01's marker paragraph was adopted from the fixer: FATAL marker list,
  GpuWaitSlow not fatal (NOT_ADMITTED anywhere), stdout twins, markers after `Event: quit`, and identity 19 reported
  only. The fix script's docstring labels this as "the fixer's marker rules". The pred text only says "the scorers were
  written by agents". The fixer's reading is consistent with item 3(б) and item 4 (a *fatal* marker in a mode-2/3 arm
  counts as FAIL) and with design §8.2. Identity 19 was never gated by the writer, so reporting it adds a check and
  relaxes nothing. NOTE: these rules were not attributed to the fixer inside the pred.
- **Code deviations of the implementation agent.** Accepted explicitly in item 3 ("Принимаю отклонения агента …").
  NOTE: accepted after implementation, as in earlier sessions.

## 3. Failed chain starts before vfy121: really no run?

`go121a.log` shows four requests before the vfy121 start. None reached the `<tag> start` line, which is the only line
followed by `enter_scene.py`.

| request | outcome | how far it got |
|---|---|---|
| 13:15:13 `smk121` | procload waited on `a foreign application` (pid 2936, 2.5–4.6 CPU s/s); the lead killed the chain at 13:36:30–36; log line "stays busy" 13:36:37 | stopped in the first `procload`, before the lock, before install |
| 16:31:56 `vfy121` | procload waited on the fixer's leftover Monitor `tail -n 0 -F …mutlib_shp121_run.log` (started by `agent-aa428a45…` at 15:35:54, killed by the lead at 16:46:07); then the second procload saw `msedge` at 0.62 CPU s/s → refused 16:46:36 | **took the lock, verified and INSTALLED the pinned `0bd21ec2` into the game folder** (the `files:` line at 16:46:23 comes after `cp`), then refused; the lock was released by the trap |
| 16:47:32 `vfy121` | name guard counted 2. These were the lead's own background command, whose command line contained `mutlib` inside the LOOP_STATE text. The item-6 claim is confirmed. | stopped before the lock and install |
| 16:47:59 `vfy121` | started at 16:48:36 | — |

No game launch:
- No `log_smk121*`, `rec_smk121*`, `smk121.json` and no `old/` directory exist.
- A search of the lead transcript and all three workflow transcripts finds no `enter_scene.py`, `run*.sh` or
  `launch_run.py` invocation. The only game starts are the three `bash go121a.sh …` calls. The only copies into the
  game folder are the reinstalls of `d3a981a2` at 12:10:31 and 17:25:11, plus the chain's own install.
- `_kyty.prev.txt` is byte-identical in size to `log_vfy121.txt`, so no launch happened between vfy121 and shp121.
- `pred/01` states "No emulator run of the build `0bd21ec2` has happened yet" (16:14). This is consistent with all of
  the above.

NOTE: the install during the 16:31:56 attempt was not disclosed. Item 6 says "до старта ничего не запускалось", which
is true of the game. Item 6's "дважды останавливал шлюз … стартовал с четвёртой попытки" counts the smk121 request as
an attempt. The tail made procload wait but did not itself cause a refusal. LOOP_STATE at 16:47 already says "refused
twice", although only one refusal (16:46:36) had happened by then. These are wording issues only.

## 4. Anything heavy during the sealed runs (vfy121 16:48:36–16:53:04, shp121 17:19:05–17:24:30)?

**No.**
- **Lead.** The only tool call inside either window was ScheduleWakeup (16:48:41, 17:19:10). The two Monitors
  (16:48:12, 17:18:31) were `until grep …; sleep 5` loops that ended on the start line. They overlapped only the
  chain's idle check, which read cpu=2/gpu=0 and cpu=5/gpu=0.
- **Workflows.** The scorer workflow ended at 16:14:10 and the audit started at 17:25:35. No agent transcript was
  written during either window.
- **Mutation runs.**
  - Sealed vfy121: 16:15:03–16:31:39.
  - Sealed shp121 #1: 16:54:46–17:05:39, after vfy121 ended.
  - Sealed shp121 #2: 17:06:53–17:18:08, which ends 20 s before the shp121 chain request. `mutlib` reports its wall
    time at 674.5 s.
- **Files modified inside the windows** (whole `C:/kyty`, the game folder and `~/.claude/projects`):
  - the runs' own artefacts;
  - `__pycache__/launch_run.pyc`;
  - `_PipelineCache/PPSA21564.bin`;
  - and one line of the other Claude session's transcript (the a foreign application project). That line is a `bridge-session`
    metadata update at 16:51:24. That session has had no tool activity since 2026-09-25 09:50Z.
- **Foreign load.** `a foreign application` is absent from the `pre_run.host.top` of both run JSONs; it had over 30 000 CPU-s when
  alive and would top that list. Pre-run GPU utilisation median was 0 in both runs.
- **Limit.** Nothing samples processes during the hold itself. The claim rests on the start-of-run checks and the
  absence of any other activity.

## 5. Sealed shas

Every sealed file was re-hashed. Each hash equals:
- (a) its line in `SEALS121.txt`;
- (b) the git copy in `docs/session-121/seal01` (and `docs/session-121/design121.md`, `docs/session-121/runs/`);
- (c) the `mutlib` headers (`mut_*.sealed.txt`, `mutlib_*_sealed.log`: scorer, test and mutants shas; harness
  `db82ef4b…`, which equals `docs/session-116/mutlib_v41/mutlib.py`);
- (d) the `files:` / `sealed verify PASS` lines of `go121a.log` (16-hex prefixes).

| file | sha256 (prefix) | a | b | c | d |
|---|---|---|---|---|---|
| pred/01_vfy121.md | f681d4db | ✓ | ✓ | – | ✓ |
| design/design121.md | ce1462bb | ✓ | ✓ | – | – |
| vfy121.py | 43359b14 | ✓ (both seals) | ✓ | ✓ | ✓ |
| test_vfy121.py | 61edc64b | ✓ | ✓ | ✓ | ✓ |
| mut_vfy121.py | 48557f67 | ✓ | ✓ | ✓ | ✓ |
| gates_base.txt | 303a7849 | ✓ | ✓ | – | ✓ (both) |
| go121a.sh | b12a9716 | ✓ (both) | ✓ | – | not logged; mtime 15:33:04 unchanged since the seal |
| enter_scene.py | 30b4d915 | ✓ | ✓ | – | ✓ (both) |
| procload.py | d9e7a777 | ✓ | ✓ | – | ✓ (both) |
| kyty_emulator_0bd21ec2.exe | 0bd21ec2 | ✓ | not in git (binary) | – | EXPECT check in chain; both score JSONs carry build 0bd21ec2 |
| chk_vfy121.py | c5743505 | ✓ (both) | ✓ | – | ✓ |
| pred/02_shp121.md | 3b951163 | ✓ | ✓ | – | ✓ |
| shp121.py | 46f8cadc | ✓ | ✓ | ✓ | ✓ |
| test_shp121.py | ae5a63de (repaired) | ✓ | ✓ | ✓ | ✓ |
| mut_shp121.py | d7e6620c | ✓ | ✓ | ✓ | ✓ |
| runs121/vfy121.score.json | bcc00a82 | ✓ | ✓ | – | ✓ |

Other checks:
- `SEALS121.txt` (078cdc06) is identical on disk and in git.
- Its first 19 lines equal the seal-01 commit `0a106f2`, so seal 01 was only appended to.
- The `mut_*.sealed.txt` reports, the seal scripts and both score files are identical on disk and in git.
- The build `0bd21ec2` was built from the committed tree: `build_local` ran after `git commit` at 13:14:44 and printed
  the sha.

### MINOR-4 — seal 02 was re-issued in place and the superseded state is not recorded

`seal121_02.py` sealed shp121 at 16:54:22 with `test_shp121.py` sha **`60df04d6…`**, and the first full mutlib ran on
that state (342/344). `seal121_02_tally.py` then replaced only that line with `ae5a63de…`, asserting that every other
line was unchanged, and appended a note. The old sha appears only in the lead transcript and the scorers report. It is
not in `SEALS121.txt` or git, and the first run's report was overwritten. The session-117 precedent labelled a
superseded seal (01r, "superseded, never run"). Nothing was run on the superseded state, and the scorer and pred are
unchanged, so this is traceability only. Also a NOTE: the seal-02 files sit in `docs/session-121/seal01/`.

## 6. Personal data in committed session-121 files

- A `git grep` of HEAD over `docs/session-121/**` and every session-121 commit (diffs and messages) finds:
  - no Windows user name;
  - no e-mail address;
  - no launcher user name. `enter_scene.py` carries the neutral `Player`.
- Paths are `$HOME` / `os.path.expanduser('~')`.
- Commit author and trailer are the pre-existing repository identity and the Claude trailer, not introduced here.
- NOTE: ROADMAP item 4 and the committed `pred/01_vfy121.md` name `a foreign application` ("the user's other session"). That is not
  an identity, but it discloses another application the user runs. A neutral wording ("a foreign busy process") would
  have served.

## Findings list

- **MAJOR-1** (protocol, outcome-neutral): the arming floor +300 replaced RC8's accepted +800 in the lead's brief at
  13:38:31. It was recorded at 16:13:41 as the "agent paragraph" item 5, so the record came after the action and names
  the wrong origin.
- **MINOR-2**: item 7 was recorded 22 s after the fixture edit, although it says "до правки".
- **MINOR-3**: the chain-gate mechanics (`chk_vfy121.py`, the vfytag file) were written by the fixer at 15:32–15:33,
  40 min before item 5. The gate itself is authorised by item 4.
- **MINOR-4**: seal 02 was re-issued in place. The superseded `test_shp121.py` sha 60df04d6 and the 342/344 report are
  not preserved in `SEALS121.txt` or git.
- **NOTE**:
  - pred 02 was written 9 s before item 6 was applied, and it cites item 6;
  - the item-3 deviations and the review fix were accepted after implementation (disclosed);
  - the 16:31:56 attempt installed `0bd21ec2` before refusing (not disclosed);
  - item 6 and LOOP_STATE miscount the refusals;
  - pred 01 does not attribute the fixer's marker rules to the fixer;
  - `a foreign application` is named in committed text;
  - the fixer's leftover Monitor process (`tail -F`) blocked the chain. It was found and killed, and this is disclosed.
