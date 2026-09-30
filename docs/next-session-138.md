# Session 138 — selection: the inventory of parked levers and the measured phases of the frame thread, with the threshold tightened by the data of sessions 136–137 (no game, no code)

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item **199** (the s137 close: `kp137` `NOT_RESOLVED` stands (а); the
`bindlean` package parked by the stop rule of item 190 (е)(6) and its re-open condition (б); the correctness summary (в); **the `kp137` rows
and the lead's answer to the question of item 198 (в) — the transfer κ = 0.54 ± 0.38 [I] against the dose slope 0.902, the readability
threshold ≈ 325 µs/frame (г)**; course row 137 = 47.98 %, D10 (д); First agent — information (е); **the s138 selection and its constants
(ж)(1)–(7)**; audit and process (з); debts (и)), items **198** (the `kp137` reading and rows), **190** (е)(4)–(6) (the sealed ABBA template
for a prototype), **194** (д) (the pooled scorer rules), **175** (е) and **176** (the previous selection and its acceptance — the template),
**165** (б), (д) (B2 parked, the census stop rule), §2 (the routes and every parked lever's re-open condition), §3 "Что закрыто".
`docs/session-137/audit/AUDIT137.md` (§1.1 the pooled recount and rows, §1.3 sensitivity, §4 not proven, §5 debts);
`docs/session-136/levers136.md` (the previous selection document — the form); `C:/kyty/s137/FACTS.md` `## Step 4`, `## Step 5`;
`ps5 em/CLAUDE.md`; `ps5 em/docs/agent-team.md` (general rules 15–23, sections 19–22 incl. the new p. 8 and p. 9).

**Open the report with these numbers:** session 137 — one build `05431dad` for all tags, no code: correctness (б) MET (`s4cs137`, outcome
(1)), (в) MET in OLD (`kk137`; 2.84 % of checks on NEW rows), (д) NOT READ (`s6s137`, 195 < 500 NEW rows); sealed `kp137` (8 calls ×
300 s, ABBA `bindlean=0|1`, 301 NEW pairs): Δ `dt_us` −75.1 ± 75.3, corrected −108.5 ± 74.1 ⇒ **`NOT_RESOLVED`**; OLD 0 pairs — `DEBT`;
rows (not readings): `bl_buf_us` reduction 182.1 ± 12.8, Δ`mh_bind_us` −200.8 ± 29.2, Δ`gpu_busy_us` −60.2 ± 14.5, Δĉ −1.327 ± 0.132 ns;
audit recount CONFIRMED to the tenth, 0 MAJOR / 3 MINOR. **The `bindlean` package is PARKED** (item 199 (б)). Nothing shipped;
**sessions without shipping: 9 (129–137)**. Course row 137 = **47.98 %** (34 740.2 µs, 28.8 FPS; arm 0 of the pooled `kp137`,
`05431dad` with instruments, NEW, pin) — not the time of the installed `9235a7ac`, not comparable with row 136 (−937.7 µs drift [I], D10).
**The lead's prior: P(no candidate passes) ≈ 0.6 [I].** None of these numbers is a gain or a ceiling. 60 FPS is not promised.

## Rule of the session

As in session 137 (items 190, 199): every decision in `ROADMAP.md` before the first action; the time in a decision header is `date -u`
at writing and not later than the item's commit; **times in step rows only from `date -u` at the event, written at the event into
`C:/kyty/s138/step<N>/times.txt`; a row about an event noticed later carries both the write time and the event time with its source
(general rule 23)**; reading an input not earlier than its commit and the `ROADMAP.md` item named as read; extending a step's scope only by
a `ROADMAP.md` item before the action. **No game run, no build, no emulator code, no lock, no mutants in session 138** (item 199 (ж)(6));
every number a document cites from a log is marked [c] with the log path and sha256, every estimate [I] with its basis; an estimate is
never "share × level" (items 150 (е), 175 (е)); a row "arm 1 − arm 0" with ĉ subtracted only beside Δĉ ± 2SE and the raw row (section 22
p. 6); blocks by `GateArm:` lines, window 10–88 of item 55 (б) named with its item number. Commits in the shared folder (the Lever Researcher does
not commit) only `git commit --only -- <paths>` with the real `C:/Program Files/Git/cmd/git.exe` (platform trap 11). No agent creates
user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives in `C:/kyty/scrub/`, never in
git). A third "Доработать" is never given to one link.

## Chain (item 199 (ж)(6)): every specialist step carries an `executionPolicy` review stage by the lead

Root `HPP-3` is `blocked` on step 2. No separate audit link: the recount of the selection's numbers by own code is step 1; the protocol
of s138 is checked by the s139 audit as a row.

## Steps

**0. Lever Researcher — the selection** `C:/kyty/KytyPS5/docs/session-138/levers138.md` (the lead commits it at acceptance), section
`## Step 0` of `C:/kyty/s138/FACTS.md`, time in `C:/kyty/s138/step0/times.txt`. At the top — the executor's P("none passes") before the
analysis (`date -u`). Criteria of item 199 (ж)(2), all at once: (i) target level [c] ≥ 400 µs/frame on the frame-holding thread (GuestGpu of
the reference) — from arm 0 of `kp137` (`C:/kyty/s137/log_kp137a…h.txt`, arm-0 blocks of the read pairs, window 10–88 of item 55 (б),
blocks by `GateArm:`) or a named log of s131–137 with the same instrument; (ii) the mechanism named BY CODE (file:line at HEAD of `main`) —
what exactly is not executed and why the result is the same; (iii) **the middle of the removable estimate [I] ≥ 325 µs/frame** (item 199
(г)) by the full timer of the phase, with a splitting basis (not "share × level") and the lower bound of the range printed beside it;
(iv) a state self-check at 2 and a positive control at 3 in a form that already gave `*_bad` > 0 on data (section 22 p. 7), or the argument
why such a form exists; (v) every correctness risk with a closing plan, including the minimum of NEW rows for EACH correctness tag
(section 22 p. 9); (vi) novelty against §3 and against the re-open conditions of the parked levers — a line with the item; (vii) the [I]
number of sessions to shipping ≤ 2 (prototype with a sealed 8 × 300 s ABBA in s139, shipping at step 0 of s140). A package of several
mechanisms in one knob is allowed if each part passes (ii), (iv), (v) and the package passes (iii); `bindlean` as a part only by item 199
(б). **Candidates (≤ 5):** (А) the parked inventory — K5, K14/`armcopy`, K16, B2, B3, `acinline`, L, `bindlean` (by (б)) and any other
parked lever with a written re-open condition (§2, items 122–198): per lever a line "is the re-open condition met, and by what"; (Б) ≤ 3
new mechanisms on the measured phases of the frame thread in arm 0 of `kp137` (`mh_bind` and its parts `rb_*`/`bl_*`, `mh_emit`,
`mh_prog`, `mh_disp`, `mh_rt` — whatever the log carries), each by (2); external sources (other console emulators, Vulkan practice) —
read-only. A recommendation, or "none passes" aloud. No game, no build, no code, no commits.
**1. Red Team — adversarial review of the selection** `C:/kyty/KytyPS5/docs/session-138/review138.md` (SOUND / SOUND_WITH_CHANGES /
UNSOUND, numbered RCs): every [c] number recounted by OWN code from the same logs (path, sha256, window, blocks); every mechanism
checked against the code at HEAD, not the text; every (iii) estimate — is it "share × level" in disguise, and what did the same kind of
estimate give on data before (`levers136.md` middle −330 → measured 182); novelty against §3 and the parked levers' conditions; for every
passing candidate — an input where value 1 gives a different result from 0 and value 2 does not catch it. No game, no build, no code.
**2. Roadmap Lead — close of session 138**: the acceptance item of the selection (outcome (4): mechanism, knob 0..3, target phase, kill
condition by the full timer < 200 µs/frame, correctness with a NEW-row minimum on every tag, the sealed 8 × 300 s ABBA template of items
190 (е)(4)–(6) and 194 (д), the s139 prototype chain; or outcome (5): no new census, the fork to First agent with a formal consumer —
(A) external search in s139, (B) a goal change, (C) a pause; until the answer — (A)); course row 138 (repeats 47.98 %, no new point);
process items of the review; documents; commit of both repositories; the chain of session 139 before closing.

## Must not be claimed

60 FPS; that the `bindlean` package speeds up or slows down the game; κ = 0.54 as a measured transfer (a ratio of two rows [I]); that the
time removed on the binding thread is "lost"; any `kp137` row (182.1, 200.8, −60.2, −318.2, −257.0, Δĉ) or any selection estimate as a
gain, a ceiling or a forecast of a future ABBA; that a candidate passes before the lead's acceptance item; that the package or B2 is
correct; that the byte detector works in general; OLD; other scenes; 47.98 % as the time of `9235a7ac`, as a gain against 46.72 % or as a
drop against 48.91 / 51.38 %; the −937.7 µs base drift as a speed-up.
