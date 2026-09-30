# Session 135 — the census `rs135`: measurement-only knob `rbslow` (the `slow` class of `RebindBuffers` split into parts, plus a would-hit census of `buffast` without action) in arms `b2reuse=0|1`

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" items **165** (the s134 close: `kp134` read `NOT_RESOLVED` (а);
**B2 parked as a speed lever — the phase `bl_buf` moved −11.8 ± 36.1, the L reduction returns as an equal per-iteration surcharge on
`epoch` (+11.0 ns) and `slow` (+8.3 ns) iterations, reopen condition** (б); audit and process (в); 6 sessions without shipping, course
row 134 = 48.91 % not comparable to 51.38 % (г); **the fork to First agent and the census stop rule from the s135 close** (д); debts
(ж)) and **166** (the census `rs135`: why a census and not a prototype (а); **the knob `rbslow` and its counters (б)(1)–(3)**; the run
(в); smokes (г); **the reading for the s136 selection — R3, U3 ≥ 400 with diff ≤ 0.01, the surcharge attribution rows** (д); holds (е);
chain (ж)); items 55 (б), 76 (б), 83 (б), 84–87, 89 (г), 105 (в), 113, 132 (г), 141 (в) (the census template), 146 (в), 147 (а), 150 (е),
162 (а). `docs/session-134/levers134.md` §3.2 (`buffast` on `slow`) and §5 (the fallback census `rbslow`); `docs/session-133/design133.md`
§3.3 (the 1/8 sampling idiom of `rbcen`); `docs/session-134/audit/AUDIT134.md` §4–§6; `ps5 em/CLAUDE.md` environment entries of 134 and
133; `ps5 em/docs/agent-team.md` (general rules 15–19, sections 19–22).
Code (at `cf5fd876`): `src/graphics/host_gpu/cache/bufferCache.cpp` (`ObtainBuffer` slow path — lines 1561–1582 at `0f539e02` per
`levers134.md` §5; `buffast`/`buffastcheck` 1369–1443), `pipeline/descriptors.cpp` (`RebindBuffers`, the `rbcen` class timers and the
`b2reuse` probe), `src/common/gates.{h,cpp}`, `src/common/frameStats.h`.

**Open the report with these numbers:** session 134 — the prototype `b2reuse` (build `33f5a15a`, tree `cf5fd876`, not installed): kill
smoke `s1s134` NOT_KILLED (L reduction 268.4, SE 9.1, 23 NEW pairs); the sealed `kp134` (ABBA `b2reuse=0|1`, 300 s, 39 NEW pairs):
Δ `dt_us` **+135.5 ± 272.7**, corrected +108.9 ± 219.3 ⇒ **`NOT_RESOLVED`**; OLD 0 pairs — `DEBT`; audit recount CONFIRMED to the tenth,
0 MAJOR / 3 MINOR. Rows (census, not a gain): L reduction 243.3 ± 14.5 returns as `rb_epoch` +56.9 and `rb_slow` +210.4 at unchanged
iteration counts (+11.0 / +8.3 ns per iteration); `bl_buf` −11.8 ± 36.1 ⇒ **B2 parked as a speed lever** (not closed). Correctness
(в), (г), (д) of item 151 (д)(3) not checked. Nothing shipped; **sessions without shipping: 6 (129–134)**; s135 is a census ⇒ **7 after
it**. Course row 134: **48.91 %** (34 074.8 µs, arm 0 of `kp134`, `33f5a15a` with the instruments `rbcen=1 bindlap=1 pathlap=1 mutsite=1
plkstat=1`, NEW, pin) — not comparable to 51.38 %, not the time of the installed `9235a7ac`. The `slow` class of arm 0: **2 203.4 µs/frame
at 24 180.7 iterations (91.2 ns)** — a level, not a removable amount. The lead's priors (item 166 (а)): P(U3 ≥ 400) ≈ 0.3; the surcharge —
"moved work" 0.35, "surcharge" 0.45, "not resolved" 0.2. None of these numbers is a gain or a ceiling. 60 FPS is not promised.

## Rule of the session

As in session 134 (items 150 (в), 165 (в)): every decision in `ROADMAP.md` before the first action; the time in a decision header is
`date -u` at writing and not later than the item's commit; **times in step rows only from `date -u` at the event, written at the event
into `C:/kyty/s135/step<N>/times.txt`; the FACTS time table is taken only from that file; a platform break is a row `обрыв`** (process 4
of s134); reading an input not earlier than its commit and the `ROADMAP.md` item named as read (general rule 19); extending a step's scope
only by a `ROADMAP.md` item before the action; commits in the shared folder only `git commit --only -- <paths>`. Before any expensive
irreversible action (full mutant run, game run) re-read the `ROADMAP.md` items written after the link was issued and the link's comments.
Counts and sha in a report come from the last output of the suite, with its path and sha256; the first line of a suite's output is
`suite <name> sha256 <suite sha> target <name> sha256 <target sha>`. **Equalities of `FrameTrace`/`FrameTrace-x` counters written by
different `FS::Add` are never a per-row condition — only a running sum with K or a sum per tag** (section 22). **A code change that
introduces a flag or state lists every set/clear site and every exit where the clear does not run** (section 22; Emu Engineer
instructions). **The full scorer `mutlib` wall forecast = measured time of one suite run × mutants / workers × 1.3; > 900 s — a question
to the lead before the start.** An acceptance item that creates or cancels a link is executed in the same heartbeat before "Принято". A
link with a platform `terminal access failure` comment is re-issued by the lead at the next heartbeat. Every specialist step writes
`## Step N — …` in `C:/kyty/s135/FACTS.md` BEFORE `done`, the scale named in every table. Mutants: the chain once at step 0 with a wall
forecast before the start; ≤ 8 workers; ONE full parser `mutlib` v4.1, cap 15 min; session budget 30 min (item 87 (б)(3)). Blocks by
`GateArm:` lines, never by `blk`; row n = F goes to the LEAVING block; window 10–88 of item 55 (б) named with its item number. The harness
checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call; the chain call of a registered tag is verbatim from the registration,
`PLWAIT` in the log; one attempt per registered tag. **The installed build is `9235a7ac…`; every chain with the game restores it.** While
the lock exists nobody edits, commits or starts processes. Long runs in the foreground; start time and expected end in the step comment.
No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives in
`C:/kyty/scrub/`, never in git). A third "Доработать" is never given to one link.

## Chain (item 166 (ж)): every specialist step carries an `executionPolicy` review stage by the lead

Steps 0 and 1 start in parallel. Root `HPP-3` is `blocked` on step 9. The fork "≥ 6 sessions without shipping" is with First agent
(item 165 (д)); an answer that changes the course arrives as a new `ROADMAP.md` item and is executed even if a link's description is not
edited.

## Steps

**0. Harness Engineer — port `C:/kyty/s135`** from `s134`: `gates_base.txt` with explicit `armcopy=0`, `acinline=0`, `lwin=0`, `dispceil=0`,
`protceil=0`, `rtskip=1`, `mutsite=1`, `plkstat=1`, `bindlap=1`, `pathlap=1`, `rbcen=1`, `b2reuse=0`, `rbslow=0`; the chain `go135a.sh` with
the smokes `s1s135` (`rbslow=1`, `b2reuse=0`, reference, 150 s: counters alive, R3 per row, `rs_bf_n` > 0), `s2s135` (`rbslow=1` with
`rbcen=0`, reference, 150 s: refusal line, `rs_*` = 0), `s3s135` (`rbslow=1`, Vulkan validation, duplicate limit lifted, 150 s; V5 by
cross-reference with `s3s133`, item 147 (а)) and the registered `rs135` (ABBA `90+1800` `b2reuse=0|1`, both arms `rbcen=1 rbslow=1
bindlap=1 pathlap=1 mutsite=1 plkstat=1 rtskip=1 armcopy=0 acinline=0 lwin=0 dispceil=0 protceil=0`, 300 s, no video, `KYTY_GPU_MARKERS=0`);
a smoke parser for the counters of item 166 (б)(1)–(3), R1/R2/R3 with percent, refusal and death markers, each with a fixture, ending in
`ALL OK`; lock before `procload`; `PLWAIT` fixture; one attempt; restore of the installed build; refusal on `protceil` ≠ 0. ONE full
chain mutant run with the forecast. No game run.
**1. Probe Designer — design** `docs/session-135/design135.md` of `rbslow` under item 166 (б) (constants are not changed; a deviation
only as a question): the mark sites of every part (1) with their code lines at HEAD `cf5fd876` and the proof that marks lie on the same
sampled iteration as `rb_slow_ns` and outside the intervals they split; the counters (2) on every `slow` iteration; the would-hit
conditions of (3) read from the `buffast` code (key, `RangeWriteEpoch`, registration epoch) and **which parts of (1) a `buffast` hit
would skip, by the code** (this defines U3); the check `rs_bf_diff`; where the probe/insert/check live (outside the `rs_*` timers); "0 is
the old path byte for byte" and "1 changes no value, decision or side effect (LRU, epochs, tracker bits)"; the refusal at `rbcen` ≠ 1;
the cost at 1 [I]; P(0) of every rare event of the reading; the expected 2SE of the B2 rows (section 22, point 3). Questions to the
lead. No game run, no emulator code.
**2. Red Team — adversarial review** `docs/session-135/design/review135.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, RCs): find a way the
census changes the path (LRU touch, epoch read with a side effect, allocation inside `ObtainBuffer`); find a would-hit condition that
differs from the real `buffast` (U3 then measures the wrong thing); check that the parts of (1) partition the sampled iteration (R3);
check sites against the code, not the text.
**3. Emu Engineer — code** (after the lead accepted 2): the knob as accepted, LAST knob line, `check_gate_order.py` before the build;
on top of `cf5fd876`; `git status --short -- src` empty → ONE measuring build → pinned copy `C:/kyty/s135/kyty_emulator_<sha8>.exe`;
`shader_cfg_tests` delta 0 against HANDOFF §4; NOT installed. No game run.
**4. Red Team — code review** `docs/session-135/design/codereview135.md` (PASS / PASS_WITH_FIXES / FAIL): path 0 untouched; value 1
changes nothing but counters (a line per touched call — LRU, epochs, tracker); marks on the sampled iteration; refusal; knob order.
**5. Harness Engineer — smokes** `s1s135`…`s3s135` (after 4 and 0), each condition of item 166 (г) as a line; R1/R2/R3 with percent. A
death or hang is a finding, no repeat. Questions to the lead.
**6. Harness Engineer — parser `rs135.py`, fixtures, registration `pred/01_rs135.md`** (levels (1)–(3) from arm 0 by blocks; B2 rows
arm 1 − arm 0 by pairs with the expected 2SE; the reading of item 166 (д) with every edge — R3 ±5 %, U3 400, diff 0.01 / 0.05, the
attribution rules; window edges; `DEBT` for < 10 pairs); ONE full `mutlib` with the forecast rule. After the lead's acceptance of step 5.
**7. Harness Engineer — the registered `rs135`**; the call verbatim from the registration; restore the installed build.
**8. Session Auditor — audit**: own recount of `rs135` by own parser (levels, R1/R2/R3, U3, diff share, B2 rows); protocol of items
165–166 and later; MAJOR/MINOR; not proven; debts; section «Процесс» (≤ 5 items); `audit135/`, git `docs/session-135/audit/`; privacy of
both trees.
**9. Roadmap Lead — close**: the reading of item 166 (д); the selection for s136 by Lever Researcher at the close before the brief
(criteria (1′)/(3′)/(5′) of item 150 (е) and the stop rule of item 165 (д)); the course row (135 repeats 48.91 %); the answer of First
agent, if any; process items; documents (with the revision of item 113 (г) at this close); commit of both repositories; the chain of
session 136 before closing.

**Outside the chain:** the fork link to First agent (item 165 (д)) — not a chain step, no blocker on the chain.

## Must not be claimed

60 FPS; that B2 speeds up or slows down the game; that B2 is closed (`NO_GAIN` was not read) or correct; the L reduction 243.3 / 268.4,
the net row, the per-iteration surcharge or ≤ 47.9 as a gain, a ceiling or a speed; U3, the would-hit share or any census number as a
gain or a ceiling; the B2 rows of `rs135` as a speed; that `buffast` is removable or correct; OLD; other scenes; 48.91 % as the time of
`9235a7ac` or as a drop against 51.38 % / 53.36 %; rows built by `blk`; a timing number beside another heavy job.
