# Session 140 — PM4 per-opcode census `pm4c140` on the reference (one measurement session of a new data class by the stop rule; no code, no build)

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item **210** (the s139 close: external search "none passes" accepted
(б); RC1–RC9 of the review applied — `pl_cmd` 600.5 is the `pathlap` mark price, the 2 261.6 residual is "with instruments", the
`KYTY_PM4_TRACE` price and the per-packet correction, VB/IB rebind is not cached, `bl_tr` phase not analysed, SMT exclusion of the
`recspin` mechanism, the `mh_prog` remainder 1 859.4, the inventory with conditions verbatim incl. K8 (в); §6 answers (г); **the stop rule
executed: no third selection, the fork repeated to First agent with recommendation (B) (д)**; **the census `pm4c140` and its constants
(е)(1)–(8)**; Process items and general rule 25 (ж); course row 139 (з)), items **207–209** (the s139 acceptances), **204** (б)(5) (the
table of arm-0 phases with status), (е)(6) (the stop rule), **199** (ж)(2) (selection criteria — the reading of `NAMED` feeds them in
s141), **66** (а) (one attempt per tag), **55** (б), **40** (е)(1) (BDA bands), **62** (а), (г) (K8 / A6), **65**, **69**, **72** (а) (`adm126`
— why not K9), §2, §3 "Что закрыто". `docs/session-139/levers139.md` (rev 2, `aa5bb086…`), `docs/session-139/review139.md` (`9bb52db9…`),
`docs/session-139/audit/AUDIT139.md` (`8be29638…`); `C:/kyty/s139/FACTS.md`; `ps5 em/CLAUDE.md`; `ps5 em/docs/agent-team.md` (general
rules 15–25, sections 19–22).

**Open the report with these numbers:** session 139 — no game, no code, no build: external search (Lever Researcher) — **none passes**
(B1 raw PM4 registers ✗(ii), (iii), (vii); B2 recorder spin ✗(i), (iii); no technique with a mechanism in our code on `pl_em_vtx`);
review SOUND_WITH_CHANGES, 9 RC, own recount matched every [c] to the tenth; audit 0 MAJOR / 4 MINOR. No answer on the fork `HPP-261`
— course A executed; the fork is repeated with the lead's recommendation (B). Arm-0 levels of `kp137` (µs/frame, [c] / [c-arith.]):
`pl_proc` 34 696.9, `cpu_gpu` 33 866.8, `a_hold` 31 488.4, `a_wait` 179.6; outside the render mutex by the wall 3 028.8 = named 767.3
(`pl_cmd` 600.5 — mark price) + **residual 2 261.6 (with instruments, composition [U])**; `pl_proc` − `cpu_gpu` 830.1 (two clocks);
PM4 loop iterations 26 208/frame. Nothing shipped; **sessions without shipping: 11 (129–139)**. Course row 139 repeats **47.98 %**
(34 740.2 µs, arm 0 of `kp137`, `05431dad` with instruments, NEW) — not the time of the installed `9235a7ac`. **The lead's prior:
P(`NAMED`) ≈ 0.4, P(a lever from s140 passing the s141 selection) ≈ 0.08 [I] — said aloud: s140 almost surely ships nothing; its value
is closing the largest not-analysed row with data for the fork answer.** None of these numbers is a gain or a ceiling. 60 FPS is not
promised.

## Rule of the session

As in sessions 138–139: every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u` at writing
and not later than the item's commit; times in step rows only from `date -u` at the event, written in the same command into
`C:/kyty/s140/step<N>/times.txt`; a row about an event noticed later carries both times with the source (general rule 23); reading an
input not earlier than its commit and the `ROADMAP.md` item named as read; extending a step's scope only by a `ROADMAP.md` item before the
action. **No emulator code, no build in session 140.** The game runs only in steps 2–3 (Harness Engineer), under
`C:/kyty/SEALED_RUN.lock` and the `procload.py` gate, one attempt per tag (item 66 (а)); the installed `9235a7ac` is restored after every
call. `KYTY_PM4_TRACE` is a MEASUREMENT-ONLY instrument (class of item 65 (в)): its numbers are levels [c] of one run, not a gain, not a
ceiling, not a price; a per-opcode share is read only with the per-packet correction and the packet count printed beside it (RC2).
Every number from a log is [c] with the path and sha256; every estimate [I] with its basis; never "share × level" (items 150 (е),
175 (е)). Mutants — `mutlib` v4.1, one full scoring run ≤ 15 min on the final text with the seal constants filled (items 19, 84–87).
Commits only `git commit --only -- <paths>` with the real `C:/Program Files/Git/cmd/git.exe` (platform trap 11). No agent creates user
interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives in `C:/kyty/scrub/`, never in
git). A third "Доработать" is never given to one link.

## Chain (item 210 (е)(8)): every specialist step carries an `executionPolicy` review stage by the lead

Root `HPP-3` is `blocked` on step 5. Step 0 is created `blocked` on the s139 close link (general rule 25) and starts when it is `done`.
The fork to First agent stays in `HPP-261` (the question card is open there); its formal consumer is step 5 (item 73 (в)(1)); until
the answer the course is this census.

## Steps

**0. Probe Designer — census design** `C:/kyty/KytyPS5/docs/session-140/design140.md` (the lead commits it at acceptance), section
`## Step 0` of `C:/kyty/s140/FACTS.md`. Constants of item 210 (е)(3)–(6) are fixed; the design adds, before any data: (i) the map
opcode → "outside the mutex / under the mutex / mixed" at HEAD, file:line per handler, sha of the map file (general rule 24(1));
(ii) the ĉ_in calibration — a site whose handler is empty by the map (candidate `nopXX`), else the lower bound 22.9 ns [c] printed with
it; (iii) the coverage identity (Σ PM4 sites + named `pl_*` against `pl_proc`, with an explicit mark-price term) and its tolerance;
(iv) the row window per run with the item number; (v) the `INSTRUMENT_FAIL` / `DEBT` conditions; (vi) the scorer spec with a fixture
per outcome edge (`NAMED` at 400/325, `SPREAD`, `INSTRUMENT_FAIL`, `DEBT` at 4 000 NEW rows); (vii) the executor's P(`NAMED`) before
the data (`date -u`). No game, no build, no code.
**1. Red Team — adversarial review** `C:/kyty/KytyPS5/docs/session-140/review140.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, numbered RCs):
the opcode map against the code at HEAD; the ĉ_in site really empty; the identity closes on `kp137` arm-0 numbers where it can; a
scenario where the per-packet instrument price moves a group across 400 (RC2 of s139); the window and the NEW-row minimum; that no
outcome reads as a gain. No game, no build, no code.
**2. Harness Engineer — harness, scorer, smoke, seal**: `C:/kyty/s140/go140a.sh` (install `05431dad` from `C:/kyty/s136/`, the arm-0
`kp137` knob string, Sky Garden, pin, restore `9235a7ac`), scorer `pm4c140.py` + fixtures (`ALL OK`) + one full `mutlib` run; smoke
`pm4s140` 1 × 120 s with `KYTY_PM4_TRACE=1` (the `FrameTrace-pm4:` lines carry opcode sites and the ĉ_in site; NEW); seal
`pred/01_pm4c140.md` with the constants of item 210 (е) and the design, `SEALS140.txt`.
**3. Harness Engineer — registered census** `pm4c140a`…`d` (4 × 300 s, `KYTY_PM4_TRACE` = 0, 1, 1, 0), scoring by the sealed scorer,
`printed_delta=no` before reading where the seal requires it; section `## Step 3` of FACTS.
**4. Session Auditor — audit** `C:/kyty/KytyPS5/docs/session-140/audit/AUDIT140.md`: own parser recount of every printed number to the
tenth; protocol (time, decisions before actions, acceptances, lock intervals, privacy, `CLAUDE.md` = `AGENTS.md`); MAJOR / MINOR; the
"Процесс" section (item 113 (б)).
**5. Roadmap Lead — close of session 140**: the reading of the outcome as an item (`NAMED` ⇒ the s141 selection on that target by
item 199 (ж)(2), unless the fork answer changes the course; `SPREAD` ⇒ the residual row becomes "analysed: spread" and leaves the speed
selection; `INSTRUMENT_FAIL`/`DEBT` ⇒ not read); the First agent answer read and written as an item (consumer of `HPP-261`); without
an answer and without `NAMED` — no second measurement session and no speed selection without the answer (item 210 (д)(3)); course
row 140; audit and process lines; documents with the `CLAUDE.md` revision of item 113 (г); commit of both repositories; the chain of
session 141 before closing (Process applied first, general rule 25).

## Must not be claimed

60 FPS; that the census finds a lever; that `NAMED` is a candidate, a gain or a ceiling; that `SPREAD` proves no lever outside the
mutex; any per-opcode level without the per-packet correction and its packet count; the instrument price between runs as a precise
number; that the census meets the K8 re-open condition (it gives host time per packet, not the guest submit time A6, item 210 (в)(8));
any number of the table of item 204 (б)(5), any `kp137` row or κ = 0.54 as a gain, a ceiling or a forecast of a future ABBA; that the
`bindlean` package or B2 is correct; the origin of Δ`pl_em_vtx` / Δ`mh_disp` (D14); OLD; other scenes; 47.98 % as the time of
`9235a7ac` or as a gain / drop against other course rows.
