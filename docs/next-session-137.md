# Session 137 — `bindlean` continues: correctness repeats on the new `IF5` "snapshot tear" form and a powered sealed `kp137` (8 × 300 s, pooled pairs)

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item **190** (the s136 close: `kp136` `NOT_RESOLVED` stands (а);
conditions of item 176 (е)(3) — (г) met by the lead's frame sheets, (б) and (в) not read (б); `kp136` rows and the lead's reading —
≈ 200 µs/frame off `bl_buf` measured, the transfer to `dt_us` below the power of 300 s (в); course row 136 = 46.72 %, base drift
+1 603.1 µs [U] — debt D10 (г); First agent's answer A on `HPP-227` (д); **the s137 lever and its constants (е)(1)–(8): one build
`05431dad`; the `IF5` "snapshot tear" form and its calibration before data; the correctness repeats `s4cs137`, `kk137`, `s6s137`; the
sealed `kp137` of 8 calls × 300 s with pooled pairs and no peeking; the reading; the stop rule before data**; holds (ж); chain (з);
audit and process (и); debts (к)), and items **176** (the `bindlean` constants (е)(1), conditions (е)(3), `kp136` (е)(4), reading (е)(5)),
**183–189** (the value-3 controls: 186 (в)–(д) the "no resets" control, 188 (в) the generation witness and outcomes (1)/(2)/(2′)/(3), 189
the `INSTRUMENT_FAIL` of `s4cs136` and the debts), **184 (б)** (validation read by rows), **187** (the answers on `IF*`, death markers,
liveness), items 55 (б), 76 (б), 77 (б), 78 (е), 83 (б), (г), 84–87, 89 (г), 105 (в), 132 (г), 162 (а). `docs/session-136/audit/AUDIT136.md`
(§1 the recount, §1.3 the conditions, §5 debts, §6 process); `C:/kyty/s136/FACTS.md` `## Step 7`, `## Step 5c3`, `## Step 0`;
`C:/kyty/s136/pred/01_kp136.md` (the print template); `ps5 em/CLAUDE.md` environment entry of 136; `ps5 em/docs/agent-team.md` (general
rules 15–20, sections 19–22 incl. the new 22 p. 1 addition and p. 7).

**Open the report with these numbers:** session 136 — the prototype `bindlean` (tree `5b972f56`, measuring build `03ce7a92`; value-3
control builds `a4794944`/`ee2287ed`/`05431dad`; none installed): kill smoke `s1s136` `NOT_KILLED` (`bl_buf_us` reduction 212.6, SE 34.7,
23 NEW pairs); sealed `kp136` (ABBA `bindlean=0|1`, 300 s, 37 NEW pairs): Δ `dt_us` −68.4 ± 254.8, corrected −100.1 ± 224.4 ⇒
**`NOT_RESOLVED`**; OLD 0 pairs — `DEBT`; rows (not readings): Δ`bl_buf_us` −199.3 ± 39.5, Δ`mh_bind_us` −195.9 ± 100.2, raw net −343.7 ±
51.0, Δĉ −1.276 ± 0.176 ns; conditions (б) and (в) of item 176 (е)(3) **not read** (`INSTRUMENT_FAIL` on single-row snapshot tears,
K = 32); audit recount CONFIRMED to the tenth, 0 MAJOR / 5 MINOR. Nothing shipped; **sessions without shipping: 8 (129–136)**. Course
row 136 = **46.72 %** (35 677.9 µs, arm 0 of `kp136`, `03ce7a92` with instruments, NEW, pin) — not the time of the installed `9235a7ac`,
not comparable with rows 131–135. Pair SD of the corrected estimator 682 (`kp136`) … 1 086 (`s1s136`), pooled 858 ⇒ expected 2SE of
`kp137` at ≈ 300 pairs 79 … 99 … 125. **The lead's priors (item 190 (е)): P(`BLN_GAIN`) ≈ 0.3 [I], P(shipping in s138) ≈ 0.2 [I].**
None of these numbers is a gain or a ceiling. 60 FPS is not promised.

## Rule of the session

As in session 136 (items 176, 187, 190): every decision in `ROADMAP.md` before the first action; the time in a decision header is
`date -u` at writing and not later than the item's commit; **times in step rows only from `date -u` at the event, written at the event
into `C:/kyty/s137/step<N>/times.txt`; the FACTS time table is taken only from that file; a platform break is a row `обрыв`**; reading an
input not earlier than its commit and the `ROADMAP.md` item named as read; extending a step's scope only by a `ROADMAP.md` item before
the action; commits in the shared folder only `git commit --only -- <paths>` **with the real `C:/Program Files/Git/cmd/git.exe`** (platform
trap 11). Before any expensive irreversible action (full mutant run, game run) re-read the `ROADMAP.md` items written after the link was
issued and the link's comments. Counts and sha in a report come from the last output of the suite, with its path and sha256; the first
line of a suite's output is `suite <name> sha256 <suite sha> target <name> sha256 <target sha>`. **Equalities of `FrameTrace`/`FrameTrace-x`
counters written by different `FS::Add` are never a per-row condition — only a running sum (item 190 (е)(2) form) or a sum per tag**
(section 22). **A row "arm 1 − arm 0" of a level with ĉ subtracted is read only beside Δĉ by pairs ± 2SE and the same row without ĉ**
(section 22 p. 6). **The lock `C:/kyty/SEALED_RUN.lock` is taken by EVERY `go137a.sh` call (smokes too); before writing, committing,
building or testing — `ls C:/kyty/SEALED_RUN.lock` in the same command; lock present — wait, write nothing.** **Every step with mutants
prints the remaining session mutant budget (30 min, item 87 (б)(3)); a permission beyond it only by a lead item naming the extension.**
The full scorer `mutlib` wall forecast = measured time of one suite run × mutants / workers × 1.3; > 900 s — a question to the lead before
the start. Mutants: the chain once at step 0 with a wall forecast before the start; ≤ 8 workers; ONE full parser `mutlib` v4.1, cap 15 min.
Blocks by `GateArm:` lines, never by `blk`; row n = F goes to the LEAVING block; window 10–88 of item 55 (б) named with its item number;
pairs only inside one call. The harness checks the lock BEFORE `procload.py` in every call; the chain call of a registered/sealed tag is
verbatim from the registration/print, `PLWAIT` in the log; one attempt per tag and per `kp137` call. **The installed build is
`9235a7ac…`; every chain with the game restores it.** Long runs in the foreground (≤ 600 s per call); start time and expected end in the
step comment; a step that does not fit a heartbeat stays `todo` with the next action. No agent creates user interactions.
`PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives in `C:/kyty/scrub/`, never in git). A third
"Доработать" is never given to one link.

## Chain (item 190 (з)): every specialist step carries an `executionPolicy` review stage by the lead

Root `HPP-3` is `blocked` on step 6. Steps 2 and 3 run in parallel after the lead accepted 0 and 1; step 4 waits for both.

## Steps

**0. Harness Engineer — port `C:/kyty/s137`** from `s136`: ONE build for every tag — `05431dad…` (`C:/kyty/s136/kyty_emulator_05431dad.exe`,
item 190 (е)(1)); `gates_base.txt` as `s136` (`armcopy=0`, `acinline=0`, `lwin=0`, `dispceil=0`, `protceil=0`, `rtskip=1`, `mutsite=1`,
`plkstat=1`, `bindlap=1`, `pathlap=1`, `rbcen=1`, `rbslow=0`, `b2reuse=0`, `bindlean=0`); **the `IF5` "snapshot tear" form of item 190 (е)(2)**
in the smoke parser (FAIL ⇔ |S_n| > 32 on two consecutive rows, or |S_last| > 32, or > 3 single rows > 32 per tag; a single row is a
row `IF5_TEAR` (n, d, S_n, S_{n+1})) with a fixture on every edge (one row 32/33, two consecutive rows 33, S_last 32/33, 3/4 tears per tag);
**the calibration print** of the new form on all 12 logs of s136 (per tag and identity: largest single |d|, number of tears, largest
min(|S_n|, |S_{n+1}|), row volume `bln_skip`, `bln_n`) — any of the 12 failing by (i)–(iii) is a stop and a question before any run; the
validation rule of item 184 (б) by rows (V1–V5 PASS ∧ `[Vulkan][E]` = 0 on the whole log ∧ ≥ 500 full rows with `bda_scan` ≤ 300) with the
499/500 fixture; the chain `go137a.sh` with `s4cs137` (3, reference, 150 s, `--census --no-rec --m4baton0`), `kk137` (2, reference, 300 s),
`s6s137` (1, validation, reference, 150 s), `kp137a`…`kp137h` (8 × 300 s, item 190 (е)(4)); ONE full chain mutant run with the forecast
and the remaining budget. No game run.
**1. Red Team — adversarial review** `docs/session-137/review137.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, RCs) of the step-0 form and of
the pooling of item 190 (е)(4): can a real accounting defect of `bln_*` (a hit not checked, a check not counted, a skip counted twice)
pass as single-row tears under (i)–(iii); does pooling pairs across calls bias Δ or SE (call effects, β by pooled pairs, BDA per pair, DRS);
is there any peeking path (an interim Δ printed, a call skipped or added by result); does the calibration on the 12 logs of s136 use any
data beyond the form. No game run.
**2. Harness Engineer — correctness repeats** (after the lead accepted 0 and 1), order `s4cs137` → `kk137` → `s6s137`, one attempt each,
readings verbatim from item 190 (е)(3): (б) by item 186 (д) with item 188 (в); (в) all `*_bad` and `bln_path` = 0 per tag, race share ≤
0.0002, `IF*` PASS by the new form; (д) by item 184 (б). A death or hang at 1/2 fails (е). One report with a line per condition, then
`done` — the lead's acceptance item decides on `kp137` by item 190 (е)(6).
**3. Harness Engineer — scorer `kp137.py`, fixtures, print `pred/01_kp137.md`** (after the lead accepted 0 and 1; parallel to 2): the
reading of item 176 (е)(5) on pooled pairs with every edge (−100, 10 pairs, `DEBT`, the corrected estimator of item 77 (б) with β by
pooled pairs, BDA by `bda_scan` per pair, DRS of item 78 (е) on pooled pairs); per-call rows (pairs, mode, admission; Δ per call only
after the eighth call); **no peeking** — the scorer refuses to print any Δ before all 8 call logs exist; an excluded call (`FAIL`,
`NOT_ADMITTED`, `INSTRUMENT_FAIL`) — its pairs out, a report row; death marker at 1 or in an unassigned frame ⇒ `BLN_INCORRECT`; the expected
2SE as a print row (79 … 99 … 125 at ≈ 300 pairs; `GAIN` reachable at true Δ ≤ ≈ −180…−225); beside-rows Δ`bl_buf_us`, raw class rows,
Δĉ ± 2SE with the row with and without ĉ; the eight call lines verbatim; window 10–88 with an edge fixture; ONE full `mutlib` with the
forecast rule and the remaining budget.
**4. Harness Engineer — the sealed `kp137`** (after the lead accepted 2 and 3 and did not cancel it by item 190 (е)(6)): 8 calls
`kp137a`…`kp137h`, each in the foreground, `procload --wait-s 540` before each, verbatim from the print, one attempt each; all 8 run at any
interim outcome except a death marker in arm 1; then the pooled reading by the printed scorer; restore the installed build.
**5. Session Auditor — audit**: own recount of the pooled `kp137` and of the three correctness tags by own parser (incl. the new `IF5` form
and the calibration print); protocol of items 190 and later; MAJOR/MINOR; not proven; debts; section «Процесс» (≤ 5 items); `audit137/`,
git `docs/session-137/audit/`; privacy of both trees.
**6. Roadmap Lead — close**: the reading of `kp137` and the shipping decision by item 190 (е)(5)–(6) (shipping ⇒ step 0 of s138 — a new
commit with default `bindlean=1` + debt D6, Red Team code review, build, install, video `shp138`; `NOT_RESOLVED`/`NO_GAIN` ⇒ `bindlean`
parked, s138 = the Lever Researcher selection by the inventory of parked levers); the course row 137; process items; documents; commit of
both repositories; the chain of session 138 before closing.

## Must not be claimed

60 FPS; that the package speeds up the game before `BLN_GAIN` is read on pooled pairs; any per-call Δ as a reading; the `kp136` rows
(199.3, 212.6, −343.7, −285.1, Δĉ), the lead's weighted estimate −121.9 or any census/selection number as a gain, a ceiling or a forecast
of `kp137`; that the package or B2 is correct before (б), (в), (д) are read in s137; that the byte detector works before (б) is read; that the
`IF5` tear form is right before the step-1 review; that s4cs136/kk136 are re-read by the new form (they are not — calibration only); OLD;
other scenes; 46.72 % as the time of `9235a7ac` or as a drop against 48.91 / 51.38 %; the base drift +1 603.1 µs as a measured cost of
path 0; rows built by `blk`; a timing number beside another heavy job.
