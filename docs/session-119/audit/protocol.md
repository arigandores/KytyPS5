# Audit 119: protocol and derivation

**Lens:** the timeline and the derivation. I checked five things:
- that every ROADMAP item (1–4) was recorded before the action it governs;
- that the smokes were honestly disclosed;
- that the item-3 fixes landed between their record and the seal;
- that the seal was complete before the first sealed run and that the sealed window stayed quiet;
- the diff `a104.py` → `g2_119.py`, the `go119a.sh` guard bytes, and item 4 against the sealed consequence.

**How:** read-only work. I did not run the game or the emulator, built nothing and edited no existing file. The only
scorer executions were a copy of `g2_119.py` in my own scratchpad, run in `--draft` mode on the sealed logs.

**Evidence sources:**
- git (`git log`, `git show`, `git diff` of `docs/ROADMAP.md`);
- NTFS birth and modify times of every file in `C:/kyty/s119`;
- the run JSONs and `go119a.log`;
- the executor's own session transcript (`~/.claude/projects/.../314bf4dc-….jsonl`), which gives exact tool-call times;
- the bytecode cache `C:/kyty/s119/__pycache__/g2_119.cpython-313.pyc`;
- sha256 of every sealed file.

## Verdict

**The protocol HOLDS. The derivation is CONFIRMED, with one MAJOR finding that does not change the verdict.**

- **Order.** Items 1–4 are append-only ROADMAP commits, each made before the action it governs.
- **Smokes.** They ran after item 1. The rule and predictions were fixed before them, which the bytecode proves.
- **Item-3 fixes.** Made after item 3 was recorded and before the seal.
- **Seal.** Complete before the chain started: PRED_SHA filled, fixtures run, SEALS119 written, `mutlib` 40/40 with controls 3/3, commit `3aaddb6`.
- **Sealed window.** No heavy work ran during it.
- **Item 4.** It applies exactly the sealed consequence.

**The MAJOR finding:** the derived scorer kept session 104's evaluator window (kept rows idx 60..88). It never applied
the standing rule for new or derived scorers (frames 10–88, or the full block, as the main estimator), and no ROADMAP
decision recorded the exception.

Re-scored under the standing window, route A is still closed:

| window | T₂ (µs) | G₂ (µs) |
|---|---:|---:|
| 60–88 (sealed) | +1 645.4 ± 157.4 | 2 216.5 |
| 10–88 (standing rule) | +1 571.5 ± 90.3 | 2 350.9 |
| full block | +1 577.6 ± 91.6 | 2 334.1 |

Ten MINOR findings follow: wording in item 4, the completeness of the smoke disclosure, and small ordering and hygiene
slips.

---

## 1. Timeline (local time, +02:00)

| time | event | evidence |
|---|---|---|
| 23:28:54 | s118 item 6 (f₂ = 0.555, spine = max(proxy, 959), the rule for s119) committed | `f11dda7` |
| 23:29:05–23:29:31 | executor reads s104 `pred/02`, greps `da_walk_us`/`da_queue_us` (reading only) | transcript |
| **23:30:00** | **item 1** committed; the harness port (cp/sed into `C:/kyty/s119`) runs in the same command AFTER the commit | `fe8faf6`; file births 23:30:00.29–.36 |
| 23:30:18 / 23:30:28 | two design agents launched (read-only) | transcript, subagent meta 23:30:18/28 |
| 23:31:03 | `probe_fields119.py` (band levels vs `obs116`/`spk118`, item 1) | birth 23:31:04 |
| 23:32:31–23:32:33 | `make_g2_119.py` written; `g2_119.py` generated (sha `8b3e5853…`) | births 23:32:31/33 |
| 23:35:02–23:38:04 | `test_g2_119.py` 71 → 76 fixtures, ALL OK | transcript |
| 23:38:28–23:38:30 | `mut_g2_119.py` (34), draft mutant loop started (pid 15644 per PRESEAL) | birth 23:38:28 |
| **23:38:45–23:42:08** | **smoke `smk119s`** (launched 23:38:45) | `smk119s.json` |
| 23:39:11 | pred draft written (with FILL placeholders) | pred birth 23:39:11; transcript Write |
| 23:39:34 | `go119a.sh` written | birth 23:39:34 |
| **23:42:26–23:45:49** | **smoke `smk119m`** | `smk119m.json` |
| 23:44:17 / 23:44:41 | design reports written; agents finished 23:44:31 / 23:44:56 | births, subagent jsonl |
| 23:46:23 | pred: FILL → smoke disclosure, mutants "(33)" | transcript heredoc |
| 23:46:44 | pre-seal check agent launched | transcript |
| **23:47:05** | **item 2** committed (designs copied to git, byte-equal after LF) | `f1a47b8` |
| 23:58:29 | draft mutant loop done, 34/34 | task notification |
| 23:58:36 | pred "(33)" → "(34)" | transcript (see m6) |
| 23:58:39 | PRESEAL.md delivered (file 23:58:26) | notification |
| **23:59:04** | **item 3** committed | `b110592` |
| 23:59:42–00:00:19 | make/test edited (both mtime 23:59:43.0078), `g2_119.py` regenerated (`5d4d907f…`) | transcript, mtimes |
| 00:00:31 | heredoc edits of `mut_g2_119.py` + `go119a.sh` (backslashes mangled, raw CR) | transcript |
| 00:00:58–00:01:01 | `fix_go119a_guard.py` rewrites the guard lines and the `tag_sh` escape | births/mtimes |
| 00:01:29–00:01:30 | `fix_pred119_item3.py` → pred final (84 + 5 fixtures, 40 mutants, bands, known limits) | pred mtime 00:01:30.899 |
| 00:01:30–00:25:22 | draft mutant rerun, 40/40 | `mut_g2_119.draft2.out.txt` |
| **00:25:39–00:25:40** | **seal**: `seal119.py` fills PRED_SHA/PRED_BYTES (`e22c96a7…`, 7 596 B) | `g2_119.py` mtime 00:25:40 |
| 00:25:40–00:26:25 | fixtures with real logs: 89 fixtures, 0 failed, ALL OK | `test_g2_119.seal.out.txt` |
| 00:26:25 | SEALS119.txt written (16 hashes) | birth 00:26:25 |
| 00:26:29–00:29:18 | `mutlib` v4.1 (frozen `db82ef4b`), `--control --no-memo`, work/cache under s119: 40/40, controls 3/3, 168 s | `mut_g2_119.out.txt` |
| 00:29:23–00:29:24 | tally appended; seal commit | `3aaddb6` (committed copies byte-equal to disk) |
| **00:29:29** | chain `go119a.sh sh119` requested | `go119a.log` |
| 00:29:29–00:30:05 | procload clean ×2, name guard 0, pred sha = PRED_SHA, idle cpu = 3 / gpu = 0 | `go119a.log` |
| **00:30:09–00:35:29** | **`sh119`** | `sh119.json` |
| 00:35:29–00:36:06 | chain checks for `mut119` (clean, cpu = 1 / gpu = 0) | `go119a.log` |
| **00:36:10–00:41:29** | **`mut119`** | `mut119.json` |
| 00:41:29–00:41:40 | scoring (`runs119/g2_119_score.*`) | births |
| **00:42:11** | **item 4** committed (before any action on it) | `e0be82b` |
| 00:42:43 / 00:43:06 / 00:43:30 | audit workflow; `next-session-120.md`; FACTS draft | transcript |

## 2. CONFIRMED

**C1 — items 1–4 were recorded before the actions they govern, and append-only.**
- Each of `fe8faf6`, `f1a47b8`, `b110592` and `e0be82b` adds lines (22, 20, 15, 15) and deletes none, so no earlier item
  was reworded after the fact.
- **Item 1** (23:30:00) came before the port, the agents, the scorer, the fixtures, the mutants and both smokes.
- **Item 2** (23:47:05) came after both design reports were delivered and before any action on them. No code was written.
- **Item 3** (23:59:04) came before every fix it lists. The one exception is the mutant count (see m6).
- **Item 4** (00:42:11) came 31 s after the score was written and before `next-session-120.md` and FACTS.
- The design agents finished at 23:44:56, well before the first sealed run, as item 1 (4) required.

**C2 — the smokes ran after item 1, and the rule and predictions were fixed before them.**
- `smk119s` launched at 23:38:45 and `smk119m` at 23:42:26. Both came after s118 item 6 (23:28:54) and s119 item 1
  (23:30:00).
- **Proof that the scorer was not tuned after the smokes:**
  - The file `__pycache__/g2_119.cpython-313.pyc` was compiled at 23:55:41. Its header records a source mtime of
    23:32:33 and a size of 54 471 B, so `g2_119.py` was not written between 23:32:33 and 23:55:41.
  - I compared that pyc against the sealed `g2_119.py`. It has identical bytecode and constants for `predictions`,
    `compute_g`, `g_of`, `verdict`, `select`, `arming_mut`, `arming_sh`, `evaluate_run`, `evaluate` and `main`.
  - Its module constants (F_SERIAL 0.555, F_SENS 0.564, SPINE_DIRECT_US 959, BAR, bands, window) are identical too.
    Only the docstring, `summary()` (the item-3 labels) and the two seal lines differ.
- **Proof that the pre-registration was not tuned after the smokes.** Its first version was written at 23:39:11, 26 s
  after `smk119s` launched and before any smoke number existed. Diffed against the sealed text, four hunks changed and
  nothing else:
  - the FILL counts;
  - the band sentence;
  - the smoke section;
  - the "Known limits" paragraph (item 3 (4)).

  The rule, the decision table, the predictions and "must not be claimed" are byte-identical to that first version.
- **The disclosed smoke numbers reproduce exactly.** I re-scored both smokes as a draft (`--start 900 --first 1200`):
  - T₂ +1 983.1 ± 414.7, and +2 116.6 ± 470.8 on `dt`;
  - `cpu_net` 31 695.0;
  - `S_lo` 13 619.4, `S_raw` 22 504.2 (A4 misses);
  - `P_mw` +17.9 ± 452.5;
  - spine 1 369.4 (sh arm 0: 1 288.9);
  - `pl_em_rec` 1 267.4, `pl_em_com` 2 350.5;
  - G₂ 2 028.8, ceiling 3 989.0, break-even tax 1 011.9;
  - `sh_jobs` 5 034.8, which is 0.996 a draw;
  - `mw_n` identity −0.3 %.
- The disclosure's statement that the draft mutants ran during both smokes is true: the loop ran 23:38:30–23:58:29.
  Its gaps are listed under m5.

**C3 — the item-3 fixes were made after item 3 and before the seal, and all are present.**
- Every fix is dated between 23:59:42 and 00:01:30 (§1). The seal came at 00:25:39.
- **Item 3 (1).** `go119a.sh` gained a name guard over `mut_g2_119|test_g2_119|mutlib`, and a check that sha256 of
  pred = PRED_SHA (lines 31–37).
- **Item 3 (2).** Every fixture it asks for exists in `test_g2_119.py`:
  - `mw_n` / `a_mut_us` darkness of `sh` (:463, :465);
  - `worker 0` twice (:467);
  - area −3.1 % / −2.9 % (:333, :335);
  - the A11b direction (:337);
  - the session-104 `sh` tag (:587).

  Six matching mutants were added (`sh_dark_mw`, `sh_dark_amut`, `worker_set`, `area_abs`, `a11b_ge`, `tag_sh`), giving
  34 → 40.
- **Item 3 (3).** The labels are in place: the `pl_pref` spine is marked "meaningless at dawalk=1", the `sh` arm-0 proxy
  is printed, and the docstring lines naming `sh104`/`mut104` and "ROADMAP s0.1 item 6" are fixed.
- **Item 3 (4).** The pre-registration now states:
  - 84 + 5 fixtures and 40 mutants;
  - `obs116` bands (`dt` 31 650, `rec_n` ≈ 10 900, `gpu_busy` ≈ 12 900);
  - 36–38 expected pairs;
  - the double-count sentence, replaced;
  - the disclosure of the instrumented spine proxy.
- The rule, F₂, the spine term, the bar and the consequences are unchanged (C2).

**C4 — the seal was complete before the first sealed run.**
- **Order:**
  1. PRED_SHA/PRED_BYTES filled at 00:25:39.
  2. Fixtures with real logs, 89 of 89, at 00:26:25.
  3. SEALS119 written at 00:26:25.
  4. The full frozen `mutlib` v4.1 run: `--control --no-memo`, `--work-dir`/`--cache-dir` under `C:/kyty/s119`, no
     `--changed-from`. Result 40/40 killed, controls 3/3, finished 00:29:18.
  5. Tally line and commit `3aaddb6` at 00:29:24.

  All of that came before the chain (00:29:29) and the emulator launch (00:30:09).
- **Hashes:** all 16 hashes in SEALS119 match the current files. These are the pred, scorer, fixtures, mutants, generator,
  chain, `gates_base`, `procload`, `enter_scene`, `launch_run`, `run_safety99`, the pinned exe, `a104.py`, `mutlib.py`,
  the seal fixture output and the `mutlib` output.
- **Committed copies:** every file in `docs/session-119/seal01/` is byte-equal to its disk copy. The later additions in
  `e0be82b` (score and chain log) are byte-equal too.
- **Pinning:** both run JSONs carry `prereg.sha256 = e22c96a7…`, bytes 7 596, `read_at` 00:30:05 / 00:36:06.
  `PREREG_PINNED` passes.

**C5 — no heavy work during 00:29:30–00:41:30.**
- **Transcript.** After the chain started (00:29:28) the executor made one light call at 00:29:34 (m8), a
  `ScheduleWakeup` at 00:29:57, and a heartbeat answered without any tool call (00:29:59 → 00:30:02). The next event is
  the chain's completion notice at 00:41:40.
- **Agents.** No subagent was alive: the last (pre-seal) one finished at 23:58:39, and the audit workflow started at
  00:42:43.
- **Background tasks.** All had finished: the draft rerun at 00:25:22, and `mutlib` (foreground) at 00:29:18.
- **Filesystem.** A scan of `C:/kyty` (depth 4) and the emulator folder for files modified between 00:29:25 and 00:41:45
  finds only the runs' own artefacts:
  - logs, stdout, gpuclk csv, JSON;
  - `gates.req`/`sample.req`, written by `enter_scene`;
  - `runs119/`;
  - the lock directory entry;
  - `_kyty*.txt`, `_run_stdout.txt`, `_PipelineCache`;
  - `kyty_emulator.exe`, copied by the chain at 00:35:43.

  No commit, no `LOOP_STATE.md` write (last 00:43:09), and no write elsewhere in `C:/kyty/s119`.
- **Chain checks.** The chain's own checks passed before each run: procload clean ×2, name guard 0, pred sha equal,
  idle cpu 3 / 1 % and gpu 0 %.

**C6 — the derivation is mechanical and each change is licensed.**
- `make_g2_119.py`, re-run into my scratchpad, reproduces the sealed `g2_119.py` byte for byte except the two seal lines
  (PRED_SHA/PRED_BYTES).
- The CRLF-normalised diff `a104.py` → `g2_119.py` is whole-line only. Each change maps to a record:

| change | licensed by |
|---|---|
| F_SERIAL 0.30 → 0.555 | s118 item 6 (1), s119 item 1 |
| F_SENS 0.39 → 0.564 (p90) | s118 item 6 (p10–p90 543–564) |
| SPINE_DIRECT_US 959; `t['spine'] = max(lvl(mut,0,'spine_us'), 959)` (was `lvl(sh,0,…)`) | s118 item 6, s119 item 1 ("прогона `mut119`") |
| `spine_us = da_walk_us − da_queue_us` (unchanged, :369-370) | item 1 |
| SH_ARMS `shadowresolve=4` → `1`; `SH_FOUR_WORKERS` → `SH_ONE_WORKER == [0]` | item 1 |
| `da_wjobs` dropped from both darkness checks | item 1 |
| BINARY_SHA `d3a981a2…`, GATES_SHA `303a7849…`, paths, tags | item 1 |
| prediction bands A3/A4/A8/A9/A10a/A11a/A11b | item 1 ("предсказания обновляются") |
| summary labels, `must_not_be_claimed`, docstring s5/s6 | item 3 (3) |

- The G rule (`g_of`), `verdict()` (central G₂ vs 3 000, area 3 %, both ADMITTED), the ceiling, controls, bands,
  tolerances and population are carried unchanged.
- Nothing outside item 1 / item 6 / item 3 changed. The one thing that should have changed and did not is M1.

**C7 — the `go119a.sh` guard lines are byte-correct and work as intended.**
- **Bytes.** The file is 4 770 B, LF-terminated, **0 CR bytes**, ASCII only. The sha `3a268e15…` equals SEALS119 and
  the commit.
- **Name guard (line 32).** In bash double quotes, `\$_` and `\$PID` reach PowerShell as `$_` and `$PID`.
  - The PowerShell process excludes itself by `$PID`; its own command line contains the pattern.
  - `-match … -and …` binds correctly.
  - `tr -d '\r'` is backslash-r.
  - An empty result (PowerShell failing) or a non-zero count refuses: it fails closed.
- **Pred-hash check (lines 35–37).**
  - `grep -o "^PRED_SHA = '[0-9a-f]*'" | cut -d"'" -f2` extracts the hash.
  - PRED_SHA = None produces no match, so the value is empty and the chain refuses.
  - `sha256sum … | cut -c1-64` gives the file hash.
- **The pre-existing CPU and GPU idle lines** have correct escapes (`\$a`, `tr -d '\r'`, `tr -d ' \r'`).
- **Live evidence.** The log shows the guard passing (no refusal line, `files:` logged at 00:29:43 / 00:35:43) and the
  idle check reporting integers.

**C8 — item 4 applies the sealed consequence exactly and adds no argument that sets it aside.**
- **The sealed row** (pred: "G₂ < 3 000 → Route A is CLOSED for maximum FPS … the next sessions go to the micro-track
  designs with a ceiling ≥ 1 ms", "decision, taken without further argument") **is applied verbatim:** "Запечатанное
  следствие применяется без дальнейших доводов".
- **What item 4 adds:**
  - that stages 3–6 do not start (implied);
  - that `spine`/`slicecen` stay default-0 tools (the status quo);
  - that the next sessions go to item 2's measurement build under item 2's rule. Item 2 was recorded before the seal
    and found no candidate proved ≥ 1 ms, so this is the sealed row's route, not a new one.
- **Every number** in item 4 equals `runs119/g2_119_score.txt`, and the printed arithmetic evaluates to 2 216.49.
- The sensitivities (f = 0.564: 2 112.8; wall: 2 094.9) are reported and are all below the bar.

**C9 — both sealed runs are in the same BDA regime, NEW,** so combining the two runs is legal. `bda_scan` medians are
52 (`sh119`) and 51 (`mut119`). Among frames ≥ 1 200, 58 of 8 372 and 76 of 8 310 are above 500. Item 4 does not state
this (m4).

**C10 — the arming seen in the raw logs matches the scorer:**
- `sh119` has exactly one `ShadowResolve: worker 0 started`; `mut119` has none.
- Each run has one `GpuClockPin: mode 1` and two `RecordThread: started`.
- There are no checkpoint, `GpuHangAbort` or fatal-marker lines.

## 3. MAJOR

**M1 — the derived scorer silently kept session 104's evaluator window (kept rows idx 60..88) as the main estimator,
against the standing rule for new/derived ABBA scorers. The verdict does not change.**

**Where the rule is recorded:**
- ROADMAP line 1124, decision after s110 item 1: "Главный оценщик будущих ABBA — ПОЛНЫЙ блок (или кадры 10–89) вместо
  окна 60–88; окно 60–88 печатается как второстепенное".
- Debt table line 3804: "главный оценщик — полный блок … в следующих производных скорерах".
- s117 decision (г), lines 2300–2301: "окно оценщика новых скореров — кадры 10–88".
- s118 item 1, line 2317: "Окно оценщика — кадры 10–88".
- CLAUDE.md standing rules: "окно оценщика ABBA — кадры 10–88".

**What s119 did:**
- `g2_119.py:91` keeps `KEEP_LO, KEEP_HI = 60, 89`, carried from `a104.py`, which was written before s110.
- Item 1 carried "популяция … pred/02 §3–§5" without recording that this overrides the standing window.
- Pred line 38 repeats "kept rows idx 60..88 … is session 104's".
- Neither the pre-seal check nor item 3 noticed.

The rule "решение до действия; незаписанное решение недействительно" makes this a MAJOR protocol finding.

**Materiality, measured.** I ran a scratch copy of the sealed scorer in `--draft` mode on the sealed logs:

| window | T₂ (µs, 2SE) | G₂ central | break-even T₂ | G₂^ | controls |
|---|---:|---:|---:|---:|---|
| 60–88 (sealed) | 1 645.4 ± 157.4 | **2 216.5** | 861.9 | 3 724.2 | all pass |
| 10–88 (standing) | 1 571.5 ± 90.3 | **2 350.9** | 922.5 | 3 756.8 | all pass, 40 pairs each |
| full block 0–89 | 1 577.6 ± 91.6 | **2 334.1** | 911.7 | 3 734.8 | all pass |

Route A is closed under every window, with a margin of about 650 µs and a measured tax about 1.7× the break-even. Two
side effects:
- The 60–88 window inflates T₂ by about 74 µs and its 2SE by about 75 %.
- The sole prediction miss, A4 (`S_raw` 21 642 > 21 500), is a window effect: at 10–88 it is 21 425.6, a HIT.

**Required action:**
- Record in item 5 that the sealed G₂ used the 60–88 window, and that the standing-window G₂ is 2 351 µs (closed).
- Change no verdict.
- Put the window change into the whole-line derivation checklist of every future scorer derived from a pre-s110 parent.

## 4. MINOR

**m1 — item 4 overstates the ceiling.** It says "потолок G₂^ 3 724,2 (все неопределённые члены в пользу A)". In s119 that
parenthetical is not true.
- The ceiling keeps spine = max(proxy, 959) = 1 268.2, but the A-favourable end of the spine is the direct 959.
- It keeps f₂ = 0.555, but the A-favourable end is the `spk118` p10 of 0.543.
- With both at their A-favourable ends, G₂^ ≈ 4 030–4 190 µs.

The ceiling decides nothing, so this is wording only. Session 104's definition ("every uncertain term at the end that
favours route A") no longer holds once the spine became a max of two values.

**m2 — "налог W = 2 T₂" describes more than was measured.** The measured quantity is the tax on GuestGpu thread CPU of
ONE read-only shadow resolver (`shadowresolve=1`), which the rule uses as a proxy for the second context.
- The pre-registration itself forbids claiming "that one read-only shadow reader reproduces the contention of a second
  context that WRITES the caches".
- Item 4 uses the rule's label without the qualifier.
- The FACTS headline says "the measured tax of a second context (+1.65 ms)", and the executor's final message says
  "второй контекст добавляет потоку GuestGpu +1 645 ± 157 мкс". Both should read "one read-only shadow reader
  (the rule's T₂)".

**m3 — "измерен вдвое больше" is rounded up.** 1 645.4 / 861.9 = 1.91 (FACTS: "about twice"). Trivial.

**m4 — item 4 does not state the BDA regime.** The standing rule is "режим BDA — по `bda_scan`, указывать при каждом
уровне". Measured here: NEW in both runs (C9).

**m5 — the pre-registration's smoke disclosure is incomplete. The smokes decide nothing, hence MINOR.** Three gaps:
- **(a) Mixed BDA regimes.** `smk119s` ran in regime **OLD** (`bda_scan` median 1 068; 4 213 of 4 372 frames ≥ 1 200
  above 500). `smk119m` was **mixed**: 1 495 of 4 242 above 500, the rest NEW. The draft G₂ 2 029 and the sentence "so
  the smokes point to CLOSED" therefore combine `cpu_net`/T₂ from one regime with S from another, which the standing
  rule forbids comparing.
- **(b) A comparison that did not reproduce.** The added known-limit "(in the smokes 1 369 µs against 1 289
  uninstrumented — against route A)" compares across regimes. It vanished in the sealed runs: 1 268.2 against 1 266.8.
- **(c) Undisclosed load.** Only the draft mutants are named as load during the smokes. The two design agents also ran
  throughout both smokes (23:30:18–23:44:56).

**m6 — one item-3 correction preceded item 3.** Pred "mutants (33)" → "(34)" was written at 23:58:36. That is 28 s
before item 3 was recorded (23:59:04) and 3 s before the pre-seal report arrived (23:58:39). It was triggered by the
executor's own draft tally (34/34 at 23:58:29), and item 3 (4) then listed it as a decision. It is a factual count, and
00:01:29 superseded it with 40. Trivial ordering slip.

**m7 — the known heredoc trap recurred.** At 00:00:31 a bash heredoc through the command hook mangled backslashes: a
raw CR in `go119a.sh`, and a broken `\d` escape in the `tag_sh` mutant. This is the trap CLAUDE.md warns about. It was
caught at 00:00:51, rewritten from a Write-tool script (`fix_go119a_guard.py`, which asserts no CR) and verified before
the seal. FACTS discloses it. No effect on the seal.

**m8 — one tool call inside the chain's exclusivity checks.** At 00:29:34, 5 s after `go119a.sh` started, the executor
ran `sleep 20; cat go119a.log; ls SEALED_RUN.lock` (to 00:29:54).
- It fell inside the chain's own pre-launch checks: procload 00:29:29–00:29:43 and a second procload after install.
- It is negligible CPU, it ended before the idle sample (≈ 00:29:59–00:30:05) and the launch (00:30:09), and every
  check passed.
- It is not heavy work, but after the chain has started the heartbeat rule expects no tool calls.

**m9 — pre-seal residuals that item 3 did not list** (none affects this seal):
- The `tag_re` accepts `_entry1`, but the chain cannot launch such a tag and the pre-registration does not say how an
  entry hang is handled. s104 §2 did. No entry failure occurred.
- The A8 lower bound (959) is vacuous by construction.
- The `kill_t4` code comment says "ceiling" but the code computes the central value; the printed label is right.
- The comment `EXPECTED_LINE … verified on log_reg104` is stale.
- The name guard sees `mutlib`'s `multiprocessing` spawn workers only through their parent's command line. Orphans would
  be invisible by name; procload's rate check still covers busy ones.
- Pred line 18 describes the chain's refusals without the two new guards.
- `patch_roadmap119_1.py` sits in `C:/kyty/s118`, not `s119`.

**m10 — a stale ROADMAP heading.** The §2 A heading (ROADMAP line 2552) still reads "для «максимума FPS» переоткрыт в с.
104 и идёт этапами" after item 4 closed route A for maximum FPS. Update it at close (item 5), along with the §0.1 summary.

## 5. Checks with nothing to report

These were checked and are fine:
- The pinned exe equals the installed exe, `d3a981a2…`, now as well. Re-scoring `IDENTITY` would pass.
- `KYTY_GPU_CHECKPOINTS` is absent from the run environments.
- The schedules are byte-equal to the scorer's `RUNS`.
- The cross-run arm-0 area is 0.002 %.
- Run order: `sh119` before `mut119`, as item 1 (3) requires. No repeat was needed.
- `SEALS119.txt` header time 00:26 is consistent with the file's birth time.
- ROADMAP was not touched between 00:01 and 00:42, apart from item 4.
