# Audit 120: protocol

**Lens:** the protocol. I checked five things:

- that each ROADMAP item 1–7 was recorded before the action it governs;
- that the sealed window (11:48–11:54) stayed quiet;
- that the chain guards were right;
- that every deviation was disclosed;
- that the sealed hashes are consistent everywhere, and that no identity leaked into git.

**How:** read-only work. I built nothing, ran neither the game nor any scorer, and edited no existing file. My only
computations were small read-only parsers over `log_cen120.txt`, to size the row-skew residuals (§5.4).

**Evidence sources:**

- git: `log`, `show`, `diff` of `docs/ROADMAP.md` and `docs/session-120`;
- the modify times of every file in `C:/kyty/s120`;
- `go120a.log`, `cen120.json`, `smk120.json`, `gpuclk_cen120.csv`;
- the mutlib report headers;
- the lead's session transcript and the per-agent transcripts of each workflow
  (`~/.claude/projects/C--Users-<user>-OneDrive-Desktop-ps5-em/314bf4dc…/`), which give exact tool-call times and
  authorship;
- `~/.claude/sessions/*.json`, for the other live Claude session on the machine.

## Verdict

**The protocol HOLDS. I found no MAJOR finding, and nothing that could change the sealed verdict.** There are 10
MINOR deviations and 3 INFO notes. Most are already disclosed somewhere; §5 says where.

- **Order.** Items 1–4 and 6 were recorded before the actions they govern. Item 7 was recorded after the run and the
  scoring, and before the audit.
- **Item 5 came after its own actions.** Item 5 was committed with the code, 28 s before the smoke. But it records two
  things done 30–100 s before it was written:
  - the fixer agent's specification edits;
  - the lead's code patch `patch_spcen_c`.
- **Seal and run.** The seal was complete and committed (`13181a8`, 11:48:18) before the chain was requested
  (11:48:23) and before the game started (11:49:03).
- **Sealed window.** It was quiet for everything I can observe: this session's workflows, its agents, the lead, mutlib
  and builds. The machine-wide CPU load during the run cannot be known (§2).
- **Hashes.** All 14 sealed sha256 values in `SEALS120.txt` equal:
  - the files now;
  - the mutlib report headers (scorer, test and mutants of both sets);
  - the `files:` line of `go120a.log`;
  - the git copies (`docs/session-120/seal01/` and `docs/session-120/design120.md`; the 24 MB exe is not in git, by
    design).
- **Identity in git.** No user name or e-mail appears in any committed session-120 file. One user handle does: the
  launcher argument `--user-name <launcher user name>` in `seal01/enter_scene.py` (MINOR-10).

## 1. Were items 1–7 recorded before the actions they govern?

All times are local (+02:00). Each row gives the item's commit time, then the first action the item governs.

| item | commit and time | what it governs, and when that first happened | verdict |
|---|---|---|---|
| 1. Order and scope | `996d565` 01:00:32 | Design workflow `wf_2ff355e1` launched at 01:01:08 | before ✓ |
| 2. Threshold 1 ms → 0.5 ms | `6f691cb` 01:35:33 | The verdict rules. They were first written into `design120.md` at 04:22:14 (the design agents started at 01:01 still under 1 ms; the reviewers asked for 0.5 ms). | before ✓ |
| 3. Session 121 is a scene map | `8f8a5f1` 01:38:15 | Session 121; no action in 120 | ✓ |
| 4. Design, verdict rules, consequences | `5c6eea3` 04:22:40 | Code: implementation workflow `wf_f1e0752d`, first agent at 04:23:41. `design120.md` was written at 04:22:14; the design docs were committed in `4d4a113` at 04:22:48 (8 s after the item, but written before it). | before ✓ |
| 4, amended in place | `3086142` 10:20:09 | The sealed consequences (seal at 11:18:11, run at 11:48:59). The sentence was written by an agent (spc120 fixer) at 09:20:56 and accepted by the lead in item 6 at 10:20:09. | before the seal ✓; see MINOR-3 and MINOR-4 |
| 5. Build and code review | in `0310cbb` 05:11:49 | The smoke (requested 05:12:17) and the scorers (workflow from 05:19:12): before ✓. It also records actions that already existed: the fixer's `design120.md`/`spcen.md` edits (05:10:06), and `patch_spcen_c` applied and built at 05:11:03–05:11:17. The item's text was written at 05:11:35. | partly after its own actions — MINOR-1 |
| 6. Scorers before the seal: skew ±8, build name | `3086142` 10:20:09 | The ±8 apply workflow `wf_05b3e930` (first agent at 10:20:24; `patch_skew8_120.py` at 10:22:13), the pred fix (10:20:38) and the seal (11:18:11) | before ✓ |
| 7. Verdict of seal 01 | `096dcfc` 11:55:23 | Run ended at 11:54:25, scored at 11:54:33–11:54:44; audit workflow launched at 11:55:56 | after the run, before the audit ✓ |

**Item-7 numbers against the scorer outputs.** Every number item 7 quotes matches the scorers:

- R1: 658.8 ± 9.1; w4 540.7; d16 621.7; without E 630.4; t_hit 19.2; miss 539 ns; W 1 258.7.
- R2: C_pt 435.2, C_up 1 067.6, C_lo −36.8.
- Package R: 1 093.9 ± 15.0.
- spcen: A 340.2 / 686.9; B −8.1 / 177.9; SP 332.1 / 864.9.
- Price P−M: 2 766 ± 138 (rpk120 prints 2 765.9 ± 137.7; spc120 prints 2 768.0).
- 38 pairs; `w1` = 0.

In the "correctness" line of `rpk120`, `r1_reset` = 56 is not a correctness counter. It is the census-reset count
(`r1.md` F7; about one per P block) and correctly drops no block.

The sealed consequence (в), "path B recorded exhausted", rests on the member rule. That rule was already in the
pre-code `design120.md` §6 ("each member reported alone with the same rule", "CLOSED — that path is recorded
exhausted"). So the 10:20 amendment clarified it; it did not create it.

## 2. Did anything heavy run during the sealed run (11:48:59–11:54:25)?

**What can be known, and was quiet:**

- **The lead.** Its transcript shows these entries:
  - 11:48:22: chain launched in the background;
  - 11:48:26: a wake-up scheduled;
  - 11:48:30: one text message;
  - then nothing until the task notification at 11:54:25.

  The heartbeat cron fires at :17 and :47, so no heartbeat fell inside the window.
- **This session's workflows.** The last agent entry before the run was at 11:17:51 (the skew-apply workflow
  `wf_05b3e930`). The next was at 11:55:57 (the audit). No workflow agent has a timestamp inside the window:

  | workflow | active |
  |---|---|
  | design | 01:01–04:16 |
  | deep research | 01:46–04:03 |
  | implementation | 04:23–05:10 |
  | scorers | 05:19–05:52, then 08:51–10:19 |
  | skew apply | 10:20–11:17 |
  | audit | from 11:55:57 |
- **mutlib.** The sealed-copy run (background task `bjesgh4pi`) ended at 11:48:01: its `rpk120` report reads
  wall 1 506.8 s with 28 workers, starting at about 11:22:54. That is 22 s before the chain, 58 s before the idle check
  and 62 s before the game launch. `procload.py` reported clean twice (at about 11:48:37 and 11:48:5x) and the name
  guard found no process.
- **Builds.** `C:/kyty/build/install/kyty_emulator.exe` has not changed since 05:12:04 (sha `15cdbfc6`, the pinned
  build). No file under `C:/kyty` or the emulator folder changed in the window except the run's own outputs (`cen120.*`,
  `log_cen120.txt`, `gpuclk_cen120.csv`, `gates.req`, `sample.req`, `_kyty.txt`, `_run_stdout.txt`,
  `_PipelineCache`).
- **GPU.** `gpuclk_cen120.csv` covers 11:49:03–11:54:25:
  - utilization: median 37 %, maximum 50 %, which is consistent with the emulator alone (GPU busy about 12.8 of
    31.6 ms);
  - temperature: 46 → 66 °C;
  - clock-event mask `0x400` (as before).

  No other GPU-heavy application is visible.

**What cannot be known:**

- **Another Claude Code session is alive on the machine:** pid 47932, project `<foreign app>-mcp`, started 2026-09-25 09:48.
  - Its transcript was appended at 11:51:24, inside the window, but only with a `bridge-session` metadata record (the
    Remote Control bookkeeping line).
  - Its last conversational turn was 2026-09-25 11:50 local (`pendingWorkflowCount: 1` at that time).
  - No subagent file of that project changed on 2026-09-26, and it made no model turns during the run.
  - Its CPU use in the window is unknown. `procload` saw nothing above 0.5 CPU s/s at the start.
- **Machine-wide CPU load during the run.** The guards run only at the start. `cen120.json` has `cpuclk_requested:
  true` but `cpuclk: null`: no CPU clock or load trace was captured. Other processes (voicemeeter is the top CPU
  consumer at the start, plus Edge, Razer, LG HUB and others) and any user activity are unobservable in the window.
- **Thermal state after the 25-minute, 28-worker mutlib run.** The run started 62 s after it with no cool-down (INFO-1).
  The ABBA pairs cancel slow drift for the P−M quantities; the absolute `dt_us` values carry it.

## 3. Were the chain guards right?

`go120a.sh`, sealed sha `afbb71ab…`, unchanged since 05:18:15. Its checks, in order:

1. **Lock** (`C:/kyty/SEALED_RUN.lock`): checked for existence, then taken atomically with `noclobber` after the
   pre-checks; removed by `trap … EXIT`. The lock is absent now. ✓
2. **`procload.py --wait-s 1800`** (sealed sha `d9e7a777…`): refuses while any process uses more than 0.5 CPU s/s, or
   while any process command line contains `mutlib.py`. The log reads "clean", twice. The limitation is known: no
   total-load cap (`total cap None`), so many small processes are not seen.
3. **Name guard:** `mut_rpk120|mut_spc120|test_rpk120|test_spc120|mutlib` in any command line, excluding its own
   PowerShell. It logged no refusal, so the count was 0. ✓
4. **Pred sha against both scorers (sealed tag only):** `sha256sum pred/01_cen120.md` compared with the `PRED_SHA`
   parsed out of `rpk120.py` and `spc120.py`. The pred is `d20cd3de…` and both scorers carry it (line 70 of `rpk120.py`,
   line 126 of `spc120.py`). ✓
   - The chain does not check `PRED_BYTES`, but both scorers do (8 483), and the scorer check `prereg_sha ok` also
     compares `cen120.json`.`prereg` (`read_at` 11:48:59, sha `d20cd3de…`, 8 483 bytes).
5. **Pinned sha, before and after installing:** `EXPECT=15cdbfc6…` against the pinned copy and against the installed
   exe. ✓ The scorers re-hash the installed exe (`installed_now ok`); a re-score after the close reinstalls `d3a981a2`
   will need `--installed-sha` (the known trap from s118).
6. **`files:` line** (10 files, 16-hex prefixes): every prefix equals `SEALS120.txt`. The line does not cover
   `go120a.sh` itself, `design120.md` or `smoke120.py`, and the exe is covered by `EXPECT`. ✓
7. **Idle check** after taking the lock: CPU 1 % (limit 15), GPU 0 % (limit 10). ✓ The scorer's `idle` check reads
   `pre_run.gpu_util_median` = 0.0. ✓

Two general gaps: every guard runs only at the start, and no in-run process monitor exists (INFO-2).

## 4. Hash consistency

| file | `SEALS120.txt` | file now | mutlib header | `go120a.log` `files:` | git copy |
|---|---|---|---|---|---|
| `pred/01_cen120.md` | `d20cd3de…` | = | — | `d20cd3de41cb8e58` = | `seal01/pred/` = |
| `design/design120.md` | `e56b7fe0…` | = | — | — | `docs/session-120/design120.md` = |
| `rpk120.py` | `70362d41…` | = | = (`mut_rpk120.sealed.txt`) | = | = |
| `test_rpk120.py` | `55e3b6ae…` | = | = | = | = |
| `mut_rpk120.py` | `b9240e71…` | = | = | = | = |
| `spc120.py` | `815083e6…` | = | = (`mut_spc120.sealed.txt`) | = | = |
| `test_spc120.py` | `d4ee970d…` | = | = | = | = |
| `mut_spc120.py` | `9cc163c4…` | = | = | = | = |
| `gates_base.txt` | `303a7849…` | = | — | = | = |
| `go120a.sh` | `afbb71ab…` | = | — | — | = |
| `enter_scene.py` | `36cb148f…` (after the 11:19 edit) | = | — | = | = |
| `procload.py` | `d9e7a777…` | = | — | = | = |
| `kyty_emulator_15cdbfc6.exe` | `15cdbfc6…` | = (and the installed exe =) | — | via `EXPECT` = | not in git (by design) |
| `smoke120.py` | `de6d3b71…` | = | — | — | = |

**Also checked:**

- `SEALS120.txt`, `mut_*.sealed.txt` and `seal120.py` in git are byte-identical to the local copies.
- The mutlib harness sha in both reports is `db82ef4b…`, the frozen v4.1.
- The sealed runs used `--control --no-memo --work-dir C:/kyty/s120/mutwork_* --cache-dir C:/kyty/s120/mutcache_*`
  (transcript at 11:19:05), with no `--changed-from`.
- The pre-seal full mutlib runs were on scorers with sha `71770a94…` (rpk) and `170c843c…` (spc). I reverted the two
  `PRED_SHA`/`PRED_BYTES` lines of the sealed scorers to `None` and rebuilt each file: they reproduce those two shas
  exactly. So the sealed scorers differ from the scorers that passed pre-seal only by the seal fill.
- The design reviews and designs in git equal the local copies, except `r2_review.md` line 8, where
  `copy_design120.py` redacted the user name. Expected.
- The removed mutant `sum_open_pkg_ignored` is a true equivalent: in `summary_of`, with no OPEN member and the package
  OPEN, the fall-through `summary = pk_v` gives `'OPEN'` too, and `carrying` is computed outside the branch. Between
  `mutlib_rpk120_run1.log` and `_run.log`, one mutant was removed and two were added (`sum_open_before_na`,
  `sum_open_pkg_closed`). The mutant file carries the reason. `SEALS120.txt` (lead-written, 11:48:17) records it;
  ROADMAP does not (INFO-3).

## 5. Deviations: were they disclosed?

### MINOR-1 — `patch_spcen_c` applied and built before item 5 recorded it, and never adversarially reviewed

**Timeline (transcript):**

| time | event |
|---|---|
| 05:10:58 | `patch_spcen_c.py` written |
| 05:11:03 | applied and rebuilt, giving `e637cabe…` at 05:11:17 |
| 05:11:35 | the item-5 text that adopts it ("Принято мной сверх ревью…") written |
| 05:11:49 | committed together |

- The decision was recorded 32 s after the action. It went into the same commit and came before the smoke and the
  seal.
- **Why it is not reviewed.** The three code reviewers reviewed the tree before this patch (the build agent at
  04:54–04:55; `build_review.log` at 05:10 reports "Up-to-date"). The patch changes how `sp_rt_race` is decided (only
  the first slow-path entry of a draw decides). That counter drives an A NOT_EVALUABLE gate (> 10⁻⁴·`sp_rt_would`).
- **Effect.** It read 0 in the run, so the patch could not have flipped an admitted verdict. Whether the pre-patch
  rule would also have read 0 is unknown.
- **Disclosure:** partial. The adoption is disclosed; that it came after the action and without review is not.

### MINOR-2 — The fixer agent changed the specification before the lead recorded it

- **What changed.** At 05:10:06 the implementation workflow's fixer agent (`patches/patch_review_docs.py`) edited
  `design120.md` §4 (the timer-read add-back in `N⁺`, the row-skew ±2 rule) and `spcen.md` §11, in both the local and
  the git copies. Its report says: "I did not add this decision to `ROADMAP.md`".
- **Lead's acceptance.** The lead accepted it in writing in item 5 (05:11:35 / 05:11:49): "исправлены в `design120.md`
  до печати". That was before the smoke, the scorers and the seal.
- **Disclosure:** yes, in item 5 and `impl_report.md`. The order (agent edit first, record second) is inherent to a
  fixer step, but it is not "decision before action".

### MINOR-3 — Agents wrote into ROADMAP item 4 and into the pred

| time | agent | wrote |
|---|---|---|
| 09:21:00 | spc120 fixer (`patch_member_consequence120.py`) | Inserted the "Каждый член несёт своё следствие…" sentence into ROADMAP item 4 in the working tree, and added the pred section "Member verdicts and scorer specifics (recorded after the pre-seal check, before the seal)". |
| 10:18:50 | rpk120 fixer | Rewrote that pred section's consequence bullet: the rpk120 per-name lines, `Open members:`, "superseded", "the summary line is the last line". |

- **ROADMAP sentence.** The lead accepted it explicitly in item 6 (10:20:09): "строка п. 4, дописанная исправителем,
  принимается мной". The commit message also names it ("items 4 (member consequences) and 6").
- **Pred sections.** Accepted only implicitly: the lead read the pred at 10:20:29, edited that same section at
  10:20:38 (`fix_pred120_a.py`, ±2 → ±8) and sealed it.
- **Authorship in the sealed pred.** It never says that two agents wrote those paragraphs.
- **Order against the code.** The member-consequence code in both scorers (spc fixer 09:18–09:34, rpk fixer
  10:12–10:19) came before the lead's written acceptance, though after the spc agent's own ROADMAP working-tree record.
- **All of it precedes the seal**, and the rule is already in `design120.md` §6 (pre-code). So it did not create an
  outcome.

### MINOR-4 — Item 4 amended in place instead of appended

- **The problem.** The member-consequence sentence sits inside item 4, which was committed at 04:22. A reader of the
  ROADMAP alone could take it for part of the pre-code record.
- **Mitigation.** It is self-labelled "(записано после проверки скорера до печати…)" and named in the commit subject of
  `3086142`.
- **Disclosure:** yes.

### MINOR-5 — The skew tolerance rose from ±2 to ±8 after the smoke

- **What happened.** Item 5's ±2 (itself the fixer's rule, MINOR-2) was raised to ±8 in item 6. The decision followed
  the smoke and the draft scores (the `sp_tr` partition reached ±2 on the smoke). It was recorded at 10:20:09 before
  any code change: `patch_skew8_120.py` at 10:22:13, applied by the workflow agents from 10:20:24.
- **Disclosure:** yes, in item 6 and in the sealed pred.
- **Not outcome-bearing.** I recomputed the window-sum residuals on `log_cen120.txt` myself (frames 10–88 by frame
  number, 77 complete blocks):

  | residual | maximum |
  |---|---|
  | `sp_rt` partition | 1 |
  | `sp_tr` partition | **2** |
  | `r1_pb_n` − `r1_self_h_n` | 1 |
  | `r2_rep` − (`r2_cl` + `r2_mx`) | 1 |
  | `r2_wr_n` + `r2_wo_n` − `r2_nul_n` | 1 |

  Under the old ±2 rule every block still passes (`tr_part_edge_2` was an ADMITTED fixture), so the change did not
  alter admission. The sealed run hit the old edge exactly, which supports the lead's no-headroom reasoning.
- **Other tolerances.** `rpk120`'s FAR tolerance (max(256, 0.1 %)) comes from `design120.md` §2 / `r1.md` F2
  (pre-code). The sealed pred does not name `rpk120`'s tolerances, only `spc120`'s.

### MINOR-6 — The `enter_scene.py` edit after `seal120.py` rewrote every sealed sha line

- **What happened.** `fix_enter_scene120.py` (11:19:21–23) replaced the literal user path with `Path.home()`. It then
  recomputed all 64-hex lines of `SEALS120.txt`, not just the one for `enter_scene.py`. A blanket rewrite like that
  would silently re-seal any file changed after `seal120.py` (11:18:11).
- **Verified harmless here.** Every other sealed file's modify time is ≤ 11:18:11. The scorer, test and mutant shas
  equal the mutlib headers written from 11:19:05. The edit is behaviour-neutral: same folder, and the run's
  `cmdline` and entry (15.8 s) worked. `enter_scene.py` is not used by the scorers or fixtures.
- **Disclosure:** in `SEALS120.txt` (committed). Not in the pred (already sealed, correctly untouched) and not in the
  ROADMAP.

### MINOR-7 — The e637cabe build is not "the reviewed build"; the 15cdbfc6 build is disclosed

- **Where e637cabe comes from.** `e637cabe…` is the lead's 05:11:17 build after `patch_spcen_c`. The reviewed tree is
  the one before that patch. The sealed pred calls `e637cabe` "(the reviewed build)", which is inaccurate. Item 5's
  own text is not wrong: it lists `e637cabe` and the adopted patch separately.
- **Where 15cdbfc6 comes from.** `15cdbfc6…` is the rebuild after the commit (`0310cbb`, `build_commit.log`, 05:12:04).
  Between the two builds, `normalize_eol.py` rewrote line endings and the git version string changed.
- **Equality cannot be verified.** "Same source" is plausible, but the `e637cabe` binary was overwritten, so the
  equality cannot be checked byte for byte.
- **The runs used 15cdbfc6 only.** `smk120.json` and `cen120.json` both carry `binary_sha256` `15cdbfc6…`, so the claim
  "`e637cabe` в прогонах не участвует" is verified.
- **Disclosure:** yes, in item 6 and the pred, apart from the wording error above.

### MINOR-8 — `go120a.sh` was edited after the smoke and before the seal, undisclosed

At 05:18:14 the `GAME=` line changed from the literal `/c/Users/<user>/…` path to `$HOME/…` (same path). The smoke
ran on the earlier chain text. The change is harmless, and the edited text is what was sealed. Neither the pred's
smoke disclosure nor `SEALS120.txt` mentions it.

### MINOR-9 — The usage-limit gap appears only in `LOOP_STATE.md`

- **What happened.** From about 05:50 to 08:50 the session hit its usage limit (the transcript repeats "You've hit your
  session limit" from 05:50:08 to 08:47:13). The scorer workflow's writer agents stopped (rpk at 05:52:33, spc at
  05:50:14) and restarted at 08:51 on top of partial files (the rpk test file was partial).
- **What is not affected.** No action governed by the protocol fell into the gap. The restarted work went through the
  full pre-seal check and full mutlib.
- **Disclosure.** Only in `LOOP_STATE.md`, at 08:52. The ROADMAP, pred and `SEALS120.txt` do not mention it. It
  belongs in FACTS.

### MINOR-10 — User handle `<launcher user name>` in a committed session-120 file

- **Where.** `docs/session-120/seal01/enter_scene.py:579` carries `'--user-name', '<launcher user name>'`, the emulator launcher
  constant. The same stem also appears in the machine's pid domain `<launcher user name>legion`.
- **History.** The handle is already in git from session 99 (15 files). But the close of session 119 grepped for
  `<launcher user name>` among its privacy terms, and session 120's checks grep only the user name and the e-mail. So this is a regression in the
  check, not a new kind of leak.
- **Not found.** No real name or e-mail. The commit identity is the GitHub handle's noreply address, the established
  repository identity, and no push was made.

### Items 2/3: attributed to user questions, kept "on own merits" without a ROADMAP record (MINOR, under MINOR-1's rule)

- **What happened.** Items 2 and 3 were recorded "(вопрос пользователя …)". At 01:40 the user said questions are not
  decisions. The lead kept both items "on their own merits", but recorded that only in `LOOP_STATE.md` and
  `CLAUDE.md`/`AGENTS.md`.
- **What the ROADMAP still shows.** The attribution, and no re-affirmation.
- **Effect:** none on this run. The 0.5 ms rule is used by the verdict and was recorded before the design.

### Smoke numbers — disclosed correctly

The smoke numbers agree across all four places they appear:

| source | numbers |
|---|---|
| `runs120/smk120_smoke.txt` (lead's `smoke120.py`) | R1 w8 620.2, R2 C_pt 444.1, R point 1 064.3, spcen N 305.2, N⁺ 830.0, P−M 2 783.8 |
| draft scorer JSONs | rpk: R1 615.9, R 1 060.0 / 1 703.9. spc: A 315.5 / 653.7, B −9.8 / 176.9, SP 305.7 / 830.7, P−M 2 816.9 ± 191.7 |
| the pred's disclosure | all of the above, plus that the scorer agents saw them |
| item 6 and `LOOP_STATE.md` | the same |

- **Smoke conditions** (idle check CPU 2 %, GPU 0 %; "no agent between 05:12 and 05:16"): verified. The
  implementation workflow's last agent entry is at 05:10:33 and the scorer workflow's first at 05:19:12. The lead only
  wrote text between 05:12:30 and 05:16:21.
- **Rules before the smoke.** Items 4 and 5 were committed before it (05:11:49 < 05:12:17), as the pred states.
- **What the smoke revealed.** It showed R1 already OPEN (about 616–620) before the seal. The thresholds (items 2 and
  4) were fixed before the smoke, so this is disclosure, not a breach.

## INFO

- **INFO-1 — No cool-down.** The 28-worker mutlib run (40 142 worker-seconds) ended 58 s before the idle check and 62 s
  before the launch. The guards passed. P−M and the ceilings are within-run ABBA quantities; absolute `dt_us` may carry
  thermal state.
- **INFO-2 — Start-only guards, no in-run CPU evidence.** `cpuclk` is null although it was requested. In-run quiet is
  established only for this session's own actors and for GPU utilization (≤ 50 %).
- **INFO-3 — Unlogged actions.**
  - The lead killed pid 28716 at 10:19:46. It was a leftover `tail -f` of an agent's mutlib log, harmless and outside
    any sealed window; no record mentions it.
  - The removed equivalent mutant is recorded in `SEALS120.txt` and `mut_rpk120.py`, not in the ROADMAP.

## Recommendations

1. **Record before acting, even for a one-line patch.** Write the ROADMAP line before applying a code change such as
   `patch_spcen_c`. Get an adversarial look at any code changed after the code review, or state in the record that
   the change is unreviewed.
2. **Tag agent-written text.** When an agent writes into the ROADMAP or a pred, tag the paragraph with its author. Add
   an explicit acceptance line in the lead's next item that names each accepted paragraph, the pred sections included.
   Append amendments as new items instead of inserting them into sealed-era items.
3. **Make seal-refresh scripts narrow.** They should rewrite only the named file's line and assert that every other
   line is unchanged. A blanket recompute hides drift.
4. **Correct the FACTS wording.** State that `e637cabe` = reviewed tree + `patch_spcen_c` (unreviewed), and that
   `15cdbfc6` = the commit rebuild. Record there too the `go120a.sh` `$HOME` edit after the smoke, the usage-limit gap
   (05:50–08:51, writers restarted on partial files), and the kill of pid 28716.
5. **Widen the privacy grep.** Restore `<launcher user name>` (and the other s119 terms) in the pre-commit grep. Decide once whether
   the launcher `--user-name` constant may stay in git copies; if not, redact it in `seal01/enter_scene.py` in a later
   commit (the sealed local copy stays as is).
6. **Watch the machine during sealed runs.** Add a cool-down or wait (for example, idle CPU for 5 minutes after a mutlib
   run). Add an in-run monitor that samples top processes' CPU every 10–30 s (and fix `cpuclk`). Then "nothing ran"
   becomes measured instead of inferred.
7. **Re-score with the sealed build hash.** At the close (reinstalling `d3a981a2`), any re-score of `cen120` must pass
   `--installed-sha 15cdbfc6…`.
