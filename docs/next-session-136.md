# Session 136 — the prototype `bindlean`: the package B2′ (light probe miss) + sync-carry, a kill smoke by the full timer `bl_buf_us` and the sealed ABBA `kp136`

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" items **175** (the s135 close: `rs135` read — `B3_PARKED`,
`B2M_NOT_RESOLVED` (а); close questions — R2, R3 by letter, U3, **MAJOR-1: rows with ĉ only beside raw rows and Δĉ; the raw rows
L −259.1, `rb_epoch` +50.0, `rb_slow` +195.0 — the B2 surcharge is real and sits in the head/tail of `slow` and in `epoch`
iterations** (б); audit and process (в); 7 sessions without shipping, course row 135 repeats 48.91 % (г); the fork `HPP-227` (д);
the selection at the close and its two outcomes (е)) and **176** (acceptance of the selection: the package accepted as one candidate
(б); hold 300 s (в); **the kill row — point estimate of the `bl_buf_us` reduction < 200 µs/frame** (г); **sync-carry (б) admitted
under a code proof and the race share ≤ 0.0002** (д); **the constants of `bindlean` (е)(1), the correctness conditions (е)(3), the
sealed `kp136` (е)(4) and its reading (е)(5)**; the killed outcome (ж); holds (з); chain (и)); items 55 (б), 76 (б), 83 (б), 84–87,
89 (г), 105 (в), 113, 132 (г), 150 (е), 151 (the prototype template), 152, 162 (а), 165. `docs/session-136/levers136.md` (the selection:
§1 debt D1 — ĉ by arm and raw rows of `kp134`, §2.1 B2′, §2.2 sync-carry, §4 the executor's proposal); `docs/session-134/design134.md`
(the `b2reuse` prototype: s.5.1 generation before the guest bytes, reset sites); `docs/session-135/audit/AUDIT135.md` §1а, §5–§7;
`ps5 em/CLAUDE.md` environment entries of 135 and 134; `ps5 em/docs/agent-team.md` (general rules 15–19, sections 19–22).
Code (HEAD; last `src/` change `32cd9fb3`): `src/graphics/host_gpu/pipeline/descriptors.cpp` (`B2Reuse::Probe` 129–199, `End()` 261–271,
the probe before `ObtainBuffer` 566–592, the insert on the ring return 584–592), `src/common/frameStats.h` (`CallScope` 4104–4108),
`src/graphics/host_gpu/cache/bufferCache.cpp` (`SyncFreeSkip` 884–913, `SynchronizeBuffer` 974–1068 with the repeat at 1007–1009,
`ObtainBuffer` 1501–1505 and the combined query 1554–1557, `BufEpochFast` 1513–1541), `memoryTracker.h:35–53`, `streamBuffer.h:89–93`,
`regionManager.h:180–397`, `src/common/gates.{h,cpp}`.

**Open the report with these numbers:** session 135 — the census `rs135` (build `74032561` copy of 3b, tree `32cd9fb3`, not installed;
ABBA `b2reuse=0|1`, 300 s, 38 NEW pairs): (д)(2) **`B3_PARKED`** (U3 −53.5, SE 21.0 < 400; raw 721.7 [I]); (д)(3) **`B2M_NOT_RESOLVED`**;
OLD 0 pairs — `DEBT`; audit recount CONFIRMED to the tenth, 1 MAJOR / 3 MINOR. The debt D1 (`levers136.md` §1): Δĉ between arms
−3.658 ± 0.144 ns in `kp134` and −3.786 ± 0.860 in `rs135` — ĉ depends on the arm; raw net row Δ(L + `epoch` + `slow`) −145.1 ± 54.3
(`kp134`) against −14.1 ± 47.0 (`rs135`), full timer `bl_buf_us` −11.8 ± 36.1 / −41.2 ± 35.1 — class rows alone do not decide, the kill
row is `bl_buf_us`. Nothing shipped; **sessions without shipping: 7 (129–135); 8 after s136 at any outcome** (shipping would be step 0
of s137). Course row 135 repeats **48.91 %** (34 074.8 µs, arm 0 of `kp134`, `33f5a15a` with instruments, NEW, pin) — not the time of
the installed `9235a7ac`. The package estimate by `bl_buf_us` −179…−515 [I], middle ≈ −330, halved ≈ −165 — **not a ceiling**. The
lead's priors (item 176 (б)): **P(killed on the smoke) ≈ 0.55, P(`GAIN` in `kp136`) ≈ 0.2** (executor 0.35–0.5). None of these numbers
is a gain or a ceiling. 60 FPS is not promised.

## Rule of the session

As in session 135 (items 165 (в), 175 (в)): every decision in `ROADMAP.md` before the first action; the time in a decision header is
`date -u` at writing and not later than the item's commit; **times in step rows only from `date -u` at the event, written at the event
into `C:/kyty/s136/step<N>/times.txt`; the FACTS time table is taken only from that file; a platform break is a row `обрыв`**; reading an
input not earlier than its commit and the `ROADMAP.md` item named as read; extending a step's scope only by a `ROADMAP.md` item before
the action; commits in the shared folder only `git commit --only -- <paths>`. Before any expensive irreversible action (full mutant run,
game run) re-read the `ROADMAP.md` items written after the link was issued and the link's comments. Counts and sha in a report come from
the last output of the suite, with its path and sha256; the first line of a suite's output is `suite <name> sha256 <suite sha> target
<name> sha256 <target sha>`. **Equalities of `FrameTrace`/`FrameTrace-x` counters written by different `FS::Add` are never a per-row
condition — only a running sum with K or a sum per tag** (section 22). **A code change that introduces a flag or state lists every
set/clear site and every exit where the clear does not run** (section 22). **A row "arm 1 − arm 0" of a level with ĉ subtracted is read
only beside Δĉ by pairs ± 2SE and the same row without ĉ** (section 22 p. 6). **A measurement-only side effect is looked for at the
design review, not first at the code review** (Red Team instructions). **The full scorer `mutlib` wall forecast = measured time of one
suite run × mutants / workers × 1.3; > 900 s — a question to the lead before the start.** An acceptance item that creates or cancels a
link is executed in the same heartbeat before "Принято". A link with a platform `terminal access failure` comment is re-issued by the lead
at the next heartbeat. Every specialist step writes `## Step N — …` in `C:/kyty/s136/FACTS.md` BEFORE `done`, the scale named in every
table. Mutants: the chain once at step 0 with a wall forecast before the start; ≤ 8 workers; ONE full parser `mutlib` v4.1, cap 15 min;
session budget 30 min (item 87 (б)(3)). Blocks by `GateArm:` lines, never by `blk`; row n = F goes to the LEAVING block; window 10–88 of
item 55 (б) named with its item number. The harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call; the chain call of
a registered tag is verbatim from the registration, `PLWAIT` in the log; one attempt per registered tag. **The installed build is
`9235a7ac…`; every chain with the game restores it.** While the lock exists nobody edits, commits or starts processes. Long runs in the
foreground; start time and expected end in the step comment. No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep
over the whole tree before commits (the list lives in `C:/kyty/scrub/`, never in git). A third "Доработать" is never given to one link.

## Chain (item 176 (и)): every specialist step carries an `executionPolicy` review stage by the lead

Steps 0 and 1 start in parallel. Root `HPP-3` is `blocked` on step 9. The fork "≥ 6 sessions without shipping" is with First agent
(`HPP-227`, item 165 (д)); an answer that changes the course arrives as a new `ROADMAP.md` item and is executed even if a link's
description is not edited.

## Steps

**0. Harness Engineer — port `C:/kyty/s136`** from `s135`/`s134`: `gates_base.txt` with explicit `armcopy=0`, `acinline=0`, `lwin=0`,
`dispceil=0`, `protceil=0`, `rtskip=1`, `mutsite=1`, `plkstat=1`, `bindlap=1`, `pathlap=1`, `rbcen=1`, `rbslow=0`, `b2reuse=0`, `bindlean=0`;
the chain `go136a.sh` with the smokes of item 176 (з): `s1s136` (ABBA `bindlean=0|1`, reference, pin, 200 s — the kill row (г)),
`s2s136` (2, reference, 150 s), `s3s136` (2, desert, `enter_scene.py --level intro_next --stable-draws 500`, 150 s), `s4s136` (3,
reference, 150 s), `s5s136` (2, forced OLD by the s113 method, 150 s), `s6s136` (1, Vulkan validation, duplicate limit lifted, NEW,
150 s), `s7s136` (spare, only by a lead item); the sealed `kp136` (item 176 (е)(4)), the registered `kk136` (2, reference, 300 s), video
`kv136` (1) / `kw136` (0), 120 s, `KYTY_REC`. A smoke parser: the kill row of item 176 (г) (point estimate of the `bl_buf_us` reduction
by pairs, ±2SE beside, `DEBT` < 10 pairs; beside-rows: raw net row, raw ns/iteration `epoch`/`slow`, Δĉ ± 2SE, `bln_skip`, Δ `dt_us`),
the conditions (е)(3)(а)–(е), (ж) (all `*_bad` = 0, `bln_path` = 0, `bln_chk` > 0, `bln_skip` > 0, the race share ≤ 0.0002, controls alive
at 3, refusal lines, death markers of item 89 (г) with the exception of item 132 (г)), each with a fixture, ending in `ALL OK`; the
fixture of every reset site (the 43 of `b2reuse` plus the new ones the accepted design names — added after steps 1–2); the counter names
of item 176 (е)(1) as constants. Lock before `procload`; `PLWAIT` fixture; one attempt; restore of the installed build; refusal on
`protceil` ≠ 0. ONE full chain mutant run with the forecast. No game run.
**1. Probe Designer — design** `docs/session-136/design136.md` of `bindlean` under item 176 (е)(1) (constants are not changed; a
deviation only as a question): B2′ — the inline light probe P/D/A with no write to `t_b2r` and no `pend` on a miss, the recomputed
insert at the ring copy with the generation read BEFORE the guest bytes (s.5.1 of `design134.md`), every line of `descriptors.cpp`,
`bufferCache.cpp`, `frameStats.h` it touches at HEAD; sync-carry — (а) the snapshot `(epoch, kind)` of `:1502` and the fact
"`HasCurrentUpload` is false" passed to `SynchronizeBuffer` only at `find = false`, `!is_written`; (б) the "CPU-clean" bit from the
combined query `:1554` — **the code proof that the safety argument of `SyncFreeSkip` (`:884–892`) holds with it, and the window** (item
176 (д)(1)); "0 is the old path byte for byte"; values 2 and 3 of (е)(1) with the counters `bln_*`; refusal at `rbcen=2` / `b2reuse` ≠ 0;
the list of set/clear sites of every new state and every exit without the clear; the reset sites (43 + new); the cost at 1 [I]; P(0) of
every rare event; the expected 2SE of the kill row and of `kp136` (section 22 p. 5). Questions to the lead. No game run, no emulator code.
**2. Red Team — adversarial review** `docs/session-136/design/review136.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, RCs): attack the (б)
proof of item 176 (д)(1) — an order of events where the bit from `:1554` skips an upload the old path would do outside the window; find a
path where the light miss changes a decision of the full probe; find a consumer of the ring copy keyed `(handle, offset)` or a writer of
tracker bits / epochs / `upload_epoch` without a reset; look for any side effect of value 1 beyond the intended one; check sites against
the code, not the text. UNSOUND on (б) ⇒ value 1 = B2′ + sync-carry (а) (item 176 (д)(1)).
**3. Emu Engineer — code** (after the lead accepted 2): the knob as accepted, LAST knob line, `check_gate_order.py` before the build;
on top of HEAD (`b2reuse`, `rbcen`, `rbslow` of the same build stay); `git status --short -- src` empty → ONE measuring build → pinned
copy `C:/kyty/s136/kyty_emulator_<sha8>.exe`; `shader_cfg_tests` delta 0 against HANDOFF §4; NOT installed; the list of set/clear sites
and exits. No game run.
**4. Red Team — code review** `docs/session-136/design/codereview136.md` (PASS / PASS_WITH_FIXES / FAIL): path 0 untouched; value 1 does
only what the accepted design says; values 2/3 self-check and control as (е)(1); item 176 (е)(3)(з) — a line per writer of tracker
bits, `m_gpu_modified_ranges`, epochs and `upload_epoch` and per consumer keyed `(handle, offset)`; a path without a reset is MAJOR
before the smokes; refusal; knob order.
**5. Harness Engineer — smokes** `s1s136`…`s6s136` (after 4 and 0): **the kill row of `s1s136` as a separate report line (mean, SE,
pairs, beside-rows) and STOP** — steps 6–7 only after the lead's acceptance item (item 176 (е)(2)); every condition of item 176 (е)(3)
(а), (б), (д), (е), (ж) as a line. A death or hang is a finding, no repeat. Questions to the lead.
**6. Harness Engineer — scorer `kp136.py`, fixtures, print `pred/01_kp136.md`** (the reading of item 176 (е)(5) with every edge — −100,
10 pairs, `DEBT`, the corrected estimator of item 77 (б), BDA by `bda_scan`; the expected 2SE as a print row; beside-rows Δ`bl_buf_us`,
raw class rows, Δĉ); window 10–88 with an edge fixture; ONE full `mutlib` with the forecast rule. After the lead's acceptance of step 5.
**7. Harness Engineer — the sealed `kp136`, the registered `kk136`, video `kv136`/`kw136`**; calls verbatim from the print/registration;
restore the installed build.
**8. Session Auditor — audit**: own recount of `kp136` and of the kill row by own parser; the correctness conditions (е)(3) by own logs;
protocol of items 175–176 and later; MAJOR/MINOR; not proven; debts; section «Процесс» (≤ 5 items); `audit136/`, git
`docs/session-136/audit/`; privacy of both trees.
**9. Roadmap Lead — close**: the reading of item 176 (е)(5) and the shipping decision; the course row 136 (arm 0 of `kp136` if run);
the answer of First agent, if any; process items; documents; commit of both repositories; the chain of session 137 before closing
(shipping ⇒ step 0 of s137; killed or not shipped ⇒ the selection by the inventory of parked levers, item 176 (ж)).

**Outside the chain:** the fork link to First agent `HPP-227` — not a chain step, no blocker on the chain.

## Must not be claimed

60 FPS; that the package, B2′ or sync-carry speeds up the game before `BLN_GAIN` is read; the selection estimates (−179…−515, −330,
47–233, 93–233) or any census number (U3, the raw rows, Δĉ, the net row, the per-iteration surcharge) as a gain, a ceiling or a speed;
that the package or B2 is correct before all conditions of item 176 (е)(3); that Δĉ is explained; that raw rows are more accurate than the
full timer; OLD; other scenes; 48.91 % as the time of `9235a7ac` or as a drop against 51.38 %; rows built by `blk`; a timing number beside
another heavy job.
