<!-- Mirror of C:/kyty/s141/FACTS.md (source of truth), personal identifiers and foreign application names removed by step3/mirror_facts141.py (local only). -->
# Session 141 — FACTS (source of truth; mirrored to `docs/local-session-141.md` by the lead at the close)

## Step 0 — inventory of correctness and scenes under goal (B) (Lever Researcher, `HPP-272`)

**Author:** Lever Researcher. Not accepted until the lead writes «Принято» in `HPP-272`.

- **Inputs read (HEAD):** KytyPS5 `main` `00c7264b` (last item `ROADMAP.md` п. 216; п. 215 read — form (А)–(Д), ranking rule, constants), ps5-em `75abe3b`,
  brief `docs/next-session-141.md` (`eb1076fc`), note `C:/kyty/s140/lead/inventory_B_notes.md`. After the work: no item after 216 in `ROADMAP.md`, 0 comments
  on `HPP-272` (checked before `done`).
- **No game, no emulator code, no build, no lock, no commit.** Logs read only by python in binary mode, streaming; `C:/kyty/SEALED_RUN.lock` absent at every
  scan (checked in the same command).
- **Document:** `C:/kyty/KytyPS5/docs/session-141/inventory141.md` (not committed; the lead commits at acceptance); sha256 — the reconciliation row of
  `step0/times.txt` (taken after the last edit).
- **Prior P (before reading, 18:48:57Z):** P(the list holds K1/K2 at ≤ 300 s of game per entry) = 0.65 [I] (lead 0.6). After: 0.9 [I] that such rows
  exist (Б1 BVH entry hang, Б2 stall at frames ≈ 951–954, Б3 unsubmitted-tick wait), 0.45 [I] that one of them is provably fixable within ≤ 2 sessions.
- **(А) scene map:** `product_levels.xml` sha256 `8f50b465ff0856aa4eef79236e933b442294e47f9a97bf691274b9017d8d4fa9`, 114 levels / 114 unique files [c]
  (`step0/levels141.out.txt` `4c7e8333`); entered 8, never entered 106 [c] (`step0/scenemap141.out.txt` `66fa9756`); the 8th beyond the brief's 7 —
  `title_controller_ship` (boot path; s113 census 4 clean runs). «Holds» for 5 scenes = one 300-s log without death markers [c] (`step0/logscan141.out.txt`
  `c37c9075`: 12 logs, 0 `GpuHangAbort:`/`ErrorDeviceLost`/`Unhandled exception:`/`[Vulkan][E]`/`GpuWaitSlow:`); `SCENE_OK` 0.
- **(Б) defect list:** 23 rows — K2 ×3 (Б1–Б3), K1 ×1 (Б4, exit), K3 ×2 (Б5, Б6), K4 ×8 (Б7–Б14), K5 ×9 (Б15–Б23); 9 closed defects confirmed; the speed-track
  rows of §7 (190 rows, last one s134) not itemised — outside goal (B).
- **New fact [c]:** the s122 document is wrong about `AsyncPipelines: skipped draw` on first entries — not «20 lines on one frame» (`docs/local-session-122.md:165-166`)
  but 1 320 / 762 / 185 lines over 14 / 69 / 11 frames in `eatl122` / `eght122` / `ednn122`, with 14 / ≥ 64 / 11 held incomplete flips; 0 in the warm sealed runs
  of the same levels (`step0/skipscan141.out.txt` `7cf6c23a`, `step0/heldscan141.out.txt` `209eda51`, `step0/logscan141.out.txt`). Row Б5.
- **Also [c]:** `PriorityStall:` (> 50 ms, `unsub=1`) in 5 of 12 logs — all with video recording or validation, 0 in the sealed 300-s runs; the log is capped at
  64 lines (`commandScheduler.cpp:654`) (`step0/prioscan141.out.txt` `9cad2795`). `[Vulkan][W]` 440 084 lines in `s6s137` (validation run), 0 elsewhere.
- **(В) ranking (proposal):** 1 Б2, 2 Б1, 3 Б3, 4 Б5, 5 Б6; with question В1 answered «sub-second stall is not K2»: Б1, Б3, Б5, Б2, Б6. Only Б1 (0.5) and Б5 (0.55) have
  P(≤ 2 sessions) ≥ 0.5 [I].
- **(Г) scene census for s142:** 10 never-entered levels (5 main G1–G5, 3 SPH-fluid, voxel, boss G1), one `-lvl` entry each, hold 120 s, `--rec`; ≈ 25–30 min of game
  [I] (s122 smokes: 141–162 s wall per entry [c]); does not produce `SCENE_OK` (that needs 300 s + validation ≈ 57 min for 10 [I]).
- **(Д) note:** every line judged; struck — «≈ 20 skipped-draw lines» (wrong) and «NGG is skipped» (stale vs `renderDraw.cpp:2383-2384`); corrected — Sky Garden
  since s45 (not s47), two entries per level in s122 (not one), `enter_scene.py:533` (it is `:568`), last validation log `s6s137`; not verified — byte identity
  of the s130–136 test logs.
- **Reference map:** `step0/refs141_map.txt` `d45b5e9b` — 155 references, 0 bad, 27 files, `ALL OK` (last output).
- **Questions to the lead (constants unchanged):** В1 sub-second stall — K2 or K3; В2 K1 at exit — key 1 or not; В3 12 non-scene entries (`ui_*` ×7, `*_data` ×3,
  `ps_logo`, `team_logo`) in the «of 114» denominator; В4 Б5 — K3 or K4.
- **Privacy:** the first-line sample of `[Vulkan][W]` in `s6s137` names a foreign application — cut from `heldscan141.out.txt` (sha before/after in `times.txt`);
  the document names no user, mail, launcher or foreign application.
- **Not claimed:** 60 FPS; that (B) speeds up or keeps speed; that any scene is correct, playable to the end or `SCENE_OK`; that the inventory is complete;
  any past number as a gain or ceiling; correctness of `bindlean` and B2; 47.98 % as the time of `9235a7ac`.

### Time table (only from `C:/kyty/s141/step0/times.txt`)

| UTC | event |
|---|---|
| 18:48:57 | start, prior P = 0.65 |
| 18:49:36 | `levels141.out.txt` `4c7e8333`, `levels141.json` `3f6609a2` |
| 18:49:52 | `scanscripts141.out.txt` `e3b0c442` — empty: the first script failed on a heredoc backslash (SyntaxError), rewritten through Write |
| 18:57:47 | `scanscripts141.out.txt` `bc92ed87` |
| 18:59:10 | `logscan141.out.txt` `c37c9075` |
| 18:59:33 | `skipscan141.out.txt` `7cf6c23a` |
| 19:00:08 | `codemap141.out.txt` `1de6a0bd` (HEAD `00c7264b`) |
| 19:00:32 | `heldscan141.out.txt` `3cff80e3` |
| 19:01:12 | `heldscan141.out.txt` redacted → `209eda51` |
| 19:03:10 | `prioscan141.out.txt` `9cad2795` |
| 19:04:59 | `scenemap141.md` `07958e4b`, `scenemap141.out.txt` `66fa9756` |
| 19:07:30 | `inventory141.md` assembled `26d79789` |
| 19:07:45 | `refs141_map.txt` `90f2a319` |
| 19:07:59 | `inventory141.md` edit → `7df9efb8`; `refs141_map.txt` `d45b5e9b` |
| (reconciliation row) | `times.txt` last row: checks (а)–(д) and the final document sha |

## Step 1 — adversarial review of `inventory141.md` (Red Team, `HPP-273`)

**Verdict: SOUND_WITH_CHANGES, 12 RC** — `C:/kyty/KytyPS5/docs/session-141/review141.md` sha256 `56e0eafd628f70130ade5b57dfa183121b83dc4958b1bd82760ff48e20318cb9`.
Input: `inventory141.md` `7df9efb8…` at commit `8c29c88d` (ROADMAP p. 217 read; p. 214–217 are the last items at hand-in; reading started 19:12:30Z,
after the commit 19:11:54Z). No game, no code, no build, no lock; logs read by python in binary mode, lock checked before each scan.

**Facts [c] found by the review** (paths and sha in the output files):
- 35 of 155 `ROADMAP.md` references of the inventory point to other lines at HEAD `8c29c88d` (p. 217 inserted 44 lines above §7); `refs141.py` checks only line existence (tautological `ALL OK`).
- B2: `dt` >= 100 ms at n 951–954 in 3 of 15 Sky Garden logs (`ack129` 183 252, `ack130` 194 034, `s12s130` 194 568 us); 0 of 4 s122 logs, 0 of 8 `kp137a…h`; `dnn122` has no hold stall (only n 224, 119 744 us at entry).
- `edes122` (`42830f04…`): flip n 4945 `dt_us` 23 796 476, `MainTaskLate: us=23812688` — not in the inventory defect list (attributed by `local-session-122.md:188-201` to a Bluetooth pad disconnect, mechanism unproven).
- B5 windows: `eatl122` n 191 1 391 088 us (held flip), `eght122` n 253 856 069 / 389 263 946 / 816 133 208, `ednn122` n 219 499 355; warm entries also have one 120–182 ms frame at entry (`ght122`, `ght123`, `dnn122`, `kp137h`).
- `census.csv` s113 (`1c385932…`, 579 runs): game marker `GuestOut: Level has started:` — `ps_logo` 105 runs, `worldmap` 29, `title_controller_ship` 105; scene `transition_next` (not in `product_levels.xml`) in 7 runs s54–s61; column `fatal`: 37 runs (6 `--- Fatal Error ---`, 4 `--- Error ---`, 27 `GpuHangAbort:`).
- 12 logs: `--- Fatal Error ---` / `--- Error ---` 0 each; `opcode is not implemented` 101 lines in each (96 SOP1 0x21, 1 SOP1 0x0c, 4 VOPC 0xe3), process continues.
- `vbn113k` (`6a54e332…`): flip n 9672 `dt_us` 3 032 310 (last n 9 770); `PriorityStall:` 0 lines in that log.
- `s6s137` `[Vulkan][W]` 440 084: two vkCmd forms (310 821 / 129 262, fragment output without attachment) + 1 masked line.
- §7 correctness debts of shipped defaults not inventoried: `daslot` (default 1) race `ahead_threads`; `rtskip` (default 1) in OLD seen only by validation; invalidation completeness.

**RC:** RC1 references pinned to a commit + anchor check; RC2 B2 p 3/15, 1 scene, N 14; RC3 new K2 row (23.8 s host stall); RC4 B5 K3 [c] / Atlantis K2, entry boundary, criterion vs warm base; RC5 map by the game marker (`ps_logo` entered; `transition_next`); RC6 census `fatal` column and EXIT form in death markers; RC7 unimplemented opcodes met (new K4, 5 scenes), B7 class [U], census baseline; RC8 §7 correctness debts of shipped defaults; RC9 ranking not literal (key 2 [c], key 3 scalar, B3 split); RC10 B1 p and criterion from another build, cap makes the series non-discriminating; RC11 B3 K2 [c] from `vbn113k`; RC12 form (B9/B21/B23 without criterion, B19 53 in `src`, B18 cost, B6 cost). Questions to the lead: key 2 [c] only; cost scalar; entry boundary for p. 217(b); HID-event window for `SCENE_OK`.

**Files and sha256** (`C:/kyty/s141/step1/`):

| file | sha256 |
|---|---|
| `refs141_rt.out.txt` | `5fe19e4aa489d9ec` |
| `logscan141_rt.out.txt` | `87ded2049ba6d955` |
| `ctx141_rt.out.txt` | `ee77a2ef7ea031b8` |
| `ctx2_141_rt.out.txt` | `91bde5f6fd45a5b1` |
| `misc141_rt.out.txt` | `80ae45ccc23f99c4` |
| `lvlstart141_rt.out.txt` | `5bd2ae4f2dbbb441` |
| `sky951_141_rt.out.txt` | `e1353e43ac336d89` |
| `vbn141_rt.out.txt` | `abccab4fd5bbc1e9` |
| `trans141_rt.out.txt` | `6610d4e565b45513` |
| `fatal141_rt.out.txt` | `9d0101e841a531c5` |
| `fatal2_141_rt.out.txt` | `ed31465ab219653b` |
| `vkw141_rt.out.txt` | `bf178d99a6276960` |
| `revrefs141.out.txt` | `6d6587f1f802d760` |

**Time (from `C:/kyty/s141/step1/times.txt`, UTC):**

| time | event |
|---|---|
| 19:12:30 | начало чтения входа: коммит 8c29c88d (приёмка шага 0, ROADMAP п. 217), inventory141.md 7df9efb8 |
| 19:13:20 | refs141_rt.py -> refs141_rt.out.txt 5fe19e4a (HEAD KytyPS5 8c29c88d) |
| 19:16:40 | logscan141_rt.py -> logscan141_rt.out.txt 87ded204 |
| 19:17:22 | ctx141_rt.py -> ctx141_rt.out.txt ee77a2ef |
| 19:17:49 | ctx2_141_rt.py -> ctx2_141_rt.out.txt 91bde5f6 |
| 19:18:20 | misc141_rt.py -> misc141_rt.out.txt 80ae45cc |
| 19:19:00 | lvlstart141_rt.py -> lvlstart141_rt.out.txt 5bd2ae4f |
| 19:20:41 | sky951_141_rt.py -> sky951_141_rt.out.txt e1353e43 |
| 19:20:56 | vbn141_rt.py -> vbn141_rt.out.txt abccab4f |
| 19:21:24 | trans141_rt.py -> trans141_rt.out.txt 6610d4e5 |
| 19:21:32 | fatal141_rt (inline python) -> fatal141_rt.out.txt 9d0101e8 |
| 19:25:40 | revrefs141.py -> revrefs141.out.txt 8bff2129 (review a0c54aa5) |
| 19:26:08 | fatal2 (inline python) -> fatal2_141_rt.out.txt ed31465a |
| 19:26:22 | revrefs141.py -> revrefs141.out.txt 1d43fe96 (review 019880fb) |
| 19:26:55 | privacy: review141.md 0 hits (scrub checks+exprs); tree case-sensitive: expr 7 (2 files) and 9 (19 files) as p.216(v), others 0 |
| 19:27:14 | vkw141_rt.py -> vkw141_rt.out.txt bf178d99 (rerun into step1 of an earlier scratch-dir run ~19:22Z between rows 19:21:32 and date -u 19:23:29 - that run had no row) |
| 19:27:23 | review141.md final 56e0eafd (first written by the Write tool between date -u 19:23:29 and row 19:25:40 [a0c54aa5]; edits 19:26-19:28; scripts *_rt.py written by Write right before their run rows) |
| 19:27:24 | revrefs141.py -> revrefs141.out.txt 6d6587f1 (review 56e0eafd) MISSING 0 |

Late rows (general rule 23): the `[Vulkan][W]` scan first ran into the run scratch dir without a row (between 19:21:32 and 19:23:29, order of commands) — rerun into `vkw141_rt.out.txt` with a row; `review141.md` was first written by the Write tool between 19:23:29 (`date -u`) and 19:25:40 (row with its sha), edits until before 19:27:23; the `*_rt.py` scripts were written by Write right before their run rows. Privacy: `review141.md` 0 hits of the `C:/kyty/scrub/` lists; tree case-sensitive — expressions 7 and 9 only, as p. 216(в).


## Step 1b — inventory141 rev. 2 by RC1–RC12 and the lead answers p.218 (Lever Researcher, `HPP-276`)

Input: `ROADMAP.md` «СЕССИЯ 122» p.218 (commit `b896fd48`), review `docs/session-141/review141.md` (`56e0eafd…`, `a243746e`), rev. 1
`inventory141.md` (`7df9efb8…`, `8c29c88d`). Reading started 19:32:57Z, after `b896fd48`. No game, no code, no build, no lock; logs read only by
python in binary mode, streamed; `SEALED_RUN.lock` absent at every scan. Deliverable (file, the lead commits it at acceptance as
`docs/session-141/inventory141.md`): `C:/kyty/s141/step1b/inventory141_r2.md` sha256 `4e13daa41f94607929af4a2b6899c017c7ad44de94e246649781ac1a7817728c`.

| time (UTC, `date -u`, `step1b/times.txt`) | event |
|---|---|
| 19:32:57 | start, reading the input |
| 19:34:14 | `loglist141b.py` → `loglist141b.out.txt` `b2f71a52` (6 347 logs > 1 MB in s100–s140, 90.7 GB) |
| 19:36:41 | `scan141b.py` → `scan141b.json` `929b0224`, `scan141b.out.txt` `43cab52c` (2 809 logs s113–s140) |
| 19:39:11 | `ana141b.py` → `ana141b.out.txt` `b5efa1f2` |
| 19:43:03 | `ana2_141b.py` → `ana2_141b.out.txt` `c1e912ce` |
| 19:47:56 | `ana3_141b.py` → `ana3_141b.out.txt` `381408f0` |
| 19:56:23 | `mk_inv2.py` → `inventory141_r2.md` `4e13daa4`; `refs141b.py` → `refs141b_map.txt` `fb8cd365` (183 refs, 183 OK, control +1 NOT OK 183, `ALL OK`) |
| 19:56:42 | check row (a)–(e) |

Late rows (general rule 23): scripts `*.py`, `inv2_parts.md`, `anchors141b.json` were written by the Write tool right before their run rows;
intermediate assemblies of the document (`5382fa9f…`, `080c365f…`) and their map runs (FAIL 73 → 49 → 0 not-OK) ran between 19:47:56 and 19:56:23
without rows — only the last assembly and map are cited.

Full sha256: `loglist141b.out.txt` `b2f71a52e6d05d6f…`, `scan141b.json` `929b02240aea06b3…`, `scan141b.out.txt` `43cab52ca6571f0c…`, `ana141b.out.txt`
`b5efa1f28fafd934…`, `ana2_141b.out.txt` `c1e912ce9d5fbd49…`, `ana3_141b.out.txt` `381408f00e2ae738…`, `refs141b_map.txt` `fb8cd365227f8ec4…`,
`anchors141b.json` `497b1d55ec2b9a7a…`.

**Numbers [c] (path → sha above):**
- RC1: rev. 1 had 38 `ROADMAP.md` references in all forms (21 distinct lines); 35 occurrences (19 distinct) read other text at `b896fd48` than at
  `00c7264b` (review: 35). Rev. 2 pins every reference to a commit (`00c7264b` for ROADMAP lines of rev. 1, `b896fd48` for code and other KytyPS5
  documents, `ps5-em@75abe3b`), local files by sha256; map checks an anchor in the first target line, control +1 gives NOT OK for all 183.
- RC5: real logs s113–s140 (outside fixture/mutant dirs) 158, unique 155; marker `GuestOut: Level has started:` there — Sky Garden 133, `intro_next` 12,
  Horror Time 3, Atlantis 2, Day and Night 2, no other names; census `levels`: Sky Garden 468, `ps_logo` 105, `title_controller_ship` 105, `intro_next` 104,
  `worldmap` 29; `scene` column: `transition_next` 7. Entered 9 of 114 (8 by the game's marker + `hub_crashsite` by document), not entered 105.
- RC4 / p.218(g): first scene frames of the 12 logs — eatl122 189, atl122 149, eght122 253, ght122 239, ght123 224, ednn122 219, dnn122 222,
  edes122 232, des122 201, s6s136 313, s6s137 184, kp137h 182. B5 K3 on 3 scenes against warm bases (Atlantis 116 791/100 150 vs 95 006; Horror
  856 069/263 946 vs 164 302; Day and Night 499 355 vs 119 744); Atlantis n 191 1 391 088 µs — K2 on entry (new row B5a).
- RC2: B2 form (n 945–960, dt ≥ 100 ms) — 6 of 121 Sky Garden logs s113–137 without validation, all in s129–131 (1/8, 2/5, 3/7), 0 elsewhere.
- RC10: `BvhLoopCapTrip:` in 5 of 133 Sky Garden entries s113–137 (sessions 113, 114, 118, 126), 0 of 72 since s127; entry hangs without the cap
  19/224 (census s76–102), with the cap 0/151 (census s103–113) and 0/133 (logs).
- RC11: vbn113k n 9672 dt 3 032 310; 1 of 11 entries in s113; mechanism reproduced by `ctl114a` (s114), `titleasync=1` shipped s115 (default 1 at
  `gates.cpp:409`), 0 hold frames ≥ 1 s in 136 entries s115–137 except edes122 — B3a proposed as closed.
- RC6: 37 census `fatal` rows attributed (table in the document); unattributed `sig1` → new row B25 (1/46 intro runs s59–113, 0/12 logs s122–136).
  Death markers in real logs s113–140: `s1s128`, `s2s128` (`protceil=1`), `dds131` (exit race B4).
- RC7: profile SOP1 0x21 ×96, SOP1 0x0c ×1, VOPC 0xe3 ×4 in 151 of 155 real logs; 12 lines before the level start and 89 after in each of 3 logs.
- RC12(b): class `[0] != '0'` at `b896fd48` — 57 = 53 src + 4 tests; `gates.cpp:630` not in class.

**Rev. 2 content:** (A) 114 rows re-sourced by the game's marker + `transition_next` line outside 114; (B) rows B1a/B1b, B3a/B3b, B5/B5a split,
new B24 (HID stop), B25 (sig1), B26 (opcodes), B27–B29 (`daslot`, `rtskip` invalidation completeness, `rtskip` in OLD), B30 (dnn122 GPU idle), B31
(ednn122 hold frame 118.6 ms); B21, B23 moved to remarks; table «p по всем логам», table «Столбец `fatal`», §7 sift; (C) ranking re-done by
p.217(v), 218(b), (v): top five (proposal) — B5a, B1a, B25, B24, B5; (D) census reading list amended; RC table (8). Questions to the lead: V5 (B3a
closed?), V6 (B1a place), V7 (RC8 wording: `intro_next` was entered on `rtskip=1` builds).

**Not claimed:** any scene correct, completable or `SCENE_OK`; the inventory complete; the `edes122` pause caused by the gamepad; B3a closed by
decision; any past number a gain or a ceiling; `bindlean` / B2 correct; 60 FPS; 47.98 % as `9235a7ac` time. Constants of p.215(v), (d), p.217(b)–(d),
p.218 unchanged.

## Step 2 — audit of the s140 protocol and s141 steps 0, 1, 1b (Session Auditor, `HPP-274`)

**Author:** Session Auditor. Input: `ROADMAP.md` p. 212–219 (commit `a8ac9773`, p. 219 20:00:57Z); reading started 20:02:49Z (row of `step2/times.txt`),
after `a8ac9773` (20:02:08Z) and the lead's «Принято» on `HPP-276` (20:02:28Z). No game, no code, no build, no lock; logs read only by python in binary mode.
Document: `C:/kyty/KytyPS5/docs/session-141/audit/AUDIT141.md` sha256 `de5529ff7d416e0e5c3d5df9b348a6aeb37adc14c2938284f2ad9fab6f726900`.

- **Verdict: 0 MAJOR / 5 MINOR; recount `CONFIRMED` with three form divergences; top five of p. 219(ж) unchanged.** Decisions p. 212–219 each
  recorded before the link line and the action; the `pm4c140` stop ran without a game, seal or lock; s140 close kept general rule 25; FACTS unchanged
  after acceptances (prefix sha `92ddae35`, `2c988e10`, `98b807a5`, `36c3504e`, `83a954b9`, `feee43fd` found).
- **Own recount** (`rc_audit141.py`, `rc_ana141.py`; outputs in git LF copies `rc_ana141.out.txt` `6916b3fb…`, `rc_ana141b.out.txt` `5b4c8eab…`): 158 files /
  155 unique logs; census 579 rows, levels 468/105/105/104/29, `transition_next` 7, `fatal` 6/4/27; 12 first scene frames and window maxima equal; B5a
  n 191 1 391 088; skipped draw 1 320/762/185 on 14/69/11 frames; `edes122` n 4945 23 796 476; B2 6/121; B32 numbers equal; B26 151/155; B3b 25/141;
  B1a 19/224, 0/284 (no census s113 SG rows — no overlap); B1b 5/133. **Divergences:** `fatal` table sum 38 not 37 (`trig98a` twice); B4 «only
  `--- Fatal Error ---`» — 3 logs (`s1s128`, `s2s128`, `dds131`); B3a denominator 135 not 136.
- **Reference map rev. 2** (`refchk141.py` → `refchk141.out.txt` `b8da7245…`): 183 refs resolve, 49 explicit anchors found, 49 absent at +1.
- **MINOR:** (1) p. 214 read by step 2 of s140 19 min 39 s after its commit; mutant pre-screen started ≈ 40 s after the stop comment; PRED/SC set and
  rolled back (rule 17 repeat); (2) time rows with gaps / reconstructed (rule 19 repeat); (3) rev. 2 numbers and K5 order (B17 first by key 2) not
  caught by acceptance; (4) B5 on Day and Night rests on the first scene frame's own `dt` (499 355 at n 219; without it 67 381 < base 119 744) — rule
  p. 218(г) silent; (5) two executor constants without a question (last-5-frames rule; B2 windows 945–960 / 900–1 000 / 949–954).
- **Checks:** privacy — KytyPS5 `6d0bfe8b..a8ac9773` 16 commits and ps5-em `516ca16..75abe3b` 2 commits clean; tree — checks #7 2 files (named), #9 19 files,
  blocking 0 (`privacy141.out.txt` `bfc2b703…`); `CLAUDE.md` = `AGENTS.md` = `342011e4…`; `doc_split_check 3611f8d` ALL OK lost 0; installed binary
  `9235a7ac…`, last `_kyty.txt` 14:40:23Z, `runs140/` absent, `src` diff empty.
- **Process:** 5 items (stop file + comment re-read, rule 26; pinned references in rule 24(1); instructions diverging from goal (B) — lead line 16,
  Lever Researcher role/output form, speed lenses of Harness Engineer / Probe Designer / Red Team; sums and ranking checked by script; executor constants
  as questions). Lines verbatim in AUDIT141.md §10.
- **Debts:** B5 first-frame rule before its criterion; rev. 2 corrections at the s141 close; `inventory141.md` in git lacks B32 and p. 219 ranking;
  `privacy139.py` in git against rule 14.
- **Not claimed:** any scene correct, completable or `SCENE_OK`; the inventory complete; builds of logs; 60 FPS; speed under (B).
- Time — only `C:/kyty/s141/step2/times.txt`.

## Close — закрытие сессии 141 (лид, `HPP-275`; `ROADMAP.md` «СЕССИЯ 122» п. 221)

**Итог:** первая сессия под целью (B) — инвентарь корректности и сцен без игры, кода и сборок. Инвентарь `docs/session-141/inventory141.md`
(ред. 1 `7df9efb8`, ред. 2 `4e13daa4` по RC1–RC12 отзыва) с поправками лида п. 219(в)–(ж) и п. 221(б)–(в) принят; отзыв `review141.md`
SOUND_WITH_CHANGES (12 RC) принят целиком; аудит `AUDIT141.md` — 0 MAJOR / 5 MINOR. **Первая цель под (B) — перепись сцен `sc142` (10
невходивших уровней, по одному холодному входу на установленной `9235a7ac`, удержание 120 с, видео) и попытка `SCENE_OK` Sky Garden
(прогон с видео и прогон с валидацией, по 300 с)** — без кода, правила чтения — п. 221(г) до прогона, печать `pred/01_sc142.md`. Отгружено
ничего.

- **Проверка лидом [c]:** `C:/kyty/s141/lead/p221chk.py` → `p221chk.out.txt` (`6907388e…`): окно входа девяти логов с. 122–123 с первым кадром
  сцены и без него (`eatl122` 1 391 088 / 1 391 088; `eght122` 856 069 / 263 946; `ght123` 164 302 / 66 389; `ednn122` 499 355 / 67 381; прочие
  без изменений); `p221sum.py` → `p221sum.out.txt` (`4539dc27…`): 32 открытых строки — K1 2, K2 2, K3 5, K4 16, K5 7; Б3а закрыт статусом;
  таблица `fatal` — 38 слагаемыми, без повтора `trig98a` — 37; ключ 1 мест 1–14 п. 219(ж) монотонен.
- **Решения п. 221:** (б) поправки ред. 2 (сумма `fatal`, Б4, знаменатель Б3а 135, Б17 первой в K5, одно окно Б2 n 945–960); (в) первый кадр
  сцены вне окна входа ⇒ Б5 — 2 сцены [c] (Atlantis, Horror Time), Day and Night — [I]; критерий Б5 (`dt` < max(100 мс, тёплая база), N 3
  холодных входа) и Б5а (N от p `sc142`; при 0/10 — ключ K4 по п. 219(д)) — до кода; (г) первая цель и константы `sc142` (уровни, чтение,
  `SCENE_OK`, калибровка 5 из 5 на логах с. 122, мутанты, печать с `enter_scene.py` и `s51_vidglitch.py`, замок, остановка, цена ≈ 40–45 мин
  игры [I]); (д) цепочка; (е) строка курса 141; (ж) «Процесс» 1–5 приняты; (з) долги аудита; (и) априор.
- **Курс под (B), строка 141:** `SCENE_OK` 0 из 114; открытых дефектов 32 (K1 2 / K2 2 / K3 5 / K4 16 / K5 7); отгружено ничего; сессий без
  отгрузки под (B) подряд — 1.
- **«Процесс» аудита — применён ДО цепочки с. 142** (общее правило 25; `C:/kyty/s141/step3/proc221.py`, вывод `proc221.out.txt` `91a1bfea`):
  (1) общее правило 26 «стоп-файл» — `agent-team.md`, инструкции Harness Engineer и лида; (2) правило 24(1) — закреплённые ссылки с якорем и
  контролем +1; (3) строка цели лида, раздел (B) Lever Researcher, строка линз скорости Harness Engineer, Probe Designer, Red Team (+ строка
  лида о `AsyncPipelines: skipped draw`); (4) самосверка сумм скриптом — Lever Researcher, строка приёмки — лид; (5) константы исполнителя —
  вопросом — Lever Researcher, Red Team (+ Harness Engineer добавкой лида). sha256: `agent-team.md` `f982fa3d` → `d4bba36e`; Roadmap Lead
  `7d792865` → `6a1da2c8`; Lever Researcher `50a8b760` → `8662daf0`; Red Team `6958d656` → `03563b3f`; Harness Engineer `b4a31d53` → `5654b2e5`;
  Probe Designer `e3ea18bf` → `57d2e9ec`.
- **Цепочка с. 142** (`C:/kyty/s141/step3/mk_chain142.py`, `chain142.json` `3997ab7f`, создана 20:34:12Z по времени платформы): `HPP-277` 0
  харнесс/скорер/калибровка/мутанты/печать (Harness Engineer; `blocked` на `HPP-275`) → `HPP-278` 1 отзыв (Red Team) → `HPP-279` 2 прогоны под
  замком (Harness Engineer) → `HPP-280` 3 аудит (Session Auditor) → `HPP-281` 4 закрытие (лид); у 0–3 — стадия review с лидом; `HPP-3` —
  `blocked` на `HPP-281`; `chain_check.py HPP-3` — `ALL OK` (`chain_check.out.txt` `dff6c944`).
- **Долги аудита, исполненные этим закрытием (п. 221(з)):** шапка `inventory141.md` — строка лида о поправках после ред. 2; строка исправления
  в `docs/local-session-122.md` («≈ 20 строк» → 1 320 / 762 / 185 на 14 / 69 / 11 кадрах); строка §7 «рывок 3 с» помечена закрытой статусом
  инвентаря; `docs/session-139/audit/privacy139.py` убран из дерева.
- **Коммиты:** KytyPS5 `ba15ee6a` (п. 221), `4633907a` (бриф с. 142), далее — документы и п. 222; ps5-em — документы закрытия.
- **Не доказаны:** корректность любой сцены и `SCENE_OK`; полнота инвентаря; что перепись найдёт или не найдёт дефект; что пауза `edes122` —
  геймпад; скорость под (B); корректность `bindlean` и B2; OLD; время `9235a7ac`. 60 FPS не обещаются.

**Время (из `C:/kyty/s141/step3/times.txt`, `date -u` в момент события):**

| UTC | событие |
|---|---|
| 20:24:59 | начало чтения входа (после п. 220 `e16edb5c` и «Принято» шага 2) |
| 20:27:21 | `p221chk.out.txt` `6907388e` |
| 20:30:23 | `p221sum.out.txt` `4539dc27` |
| 20:31:45 | п. 221 вставлен (заголовок 20:31:44), коммит `ba15ee6a` |
| 20:32:28 | «Процесс» 1–5 применён (`proc221.out.txt` `91a1bfea`) — до цепочки |
| 20:33:08 | бриф `next-session-142.md` — `4633907a` |
| 20:34:28 | цепочка с. 142 создана, `chain_check` `ALL OK` (`dff6c944`) |

Дальнейшие строки (документы, коммиты, п. 222, итог в `HPP-3`, `done`) — только в `times.txt`.
