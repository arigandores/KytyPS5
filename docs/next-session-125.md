# Session 125 — the A-walker kill test, step 1: an offline LOWER bound of what GuestGpu pays to accept a spine plan

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 55 (the close of 124: verdict, the flip-hold
contract clause (г), the lever of this session and its constants (д)(1)–(4), the chain (ж)); "СЕССИЯ 120" item on the close
(the A-walker debt decision "(5)": parked, reopened when no GuestGpu candidate ≥ 0.5 ms remains, first step — an offline
lower bound of plan acceptance; the ≈ 97 ns/op [I] figure); "СЕССИЯ 119" items 4–5 (model `g2_119`, G₂ = 2 216.5 with the
spine on GuestGpu, 3 484.7 with the spine off the critical path; kill test: residual acceptance cost ≤ 484.7 µs AND writing
second-context tax ≤ 1 645 µs); §2 A; §7 row "вариант маршрута A-walker"; sessions 117–118 (knob `spine`: shadow plan,
snapshots, carry, safe plan — `CLAUDE.md` environment entries); `C:/kyty/s119/` (`g2_119.py`, `designs/`, `FACTS.md`, git
`docs/local-session-119.md`), `C:/kyty/s117`, `C:/kyty/s118`; `docs/session-124/audit/AUDIT124.md` §4.

**Open the report with these numbers:** installed build `d3a981a2…` (`7c73f26`; restored at the close of 124, the census
build `b185f002…` stays pinned in `C:/kyty/s124`); frame skipping CLOSED entirely on the reference — translation by census
(`cen124` U = 177.1 µs < 500, BDA OLD), flip hold by the contract clause of item 55 (г) (≤ 109 µs removable); route A with
the spine on GuestGpu closed in 119 (G₂ 2 216.5 < 3 000, NEW); A-walker G₂ 3 484.7 [I] if the residual acceptance cost on
GuestGpu < 484.7 µs. Sky Garden reference: mean `dt_us` ≈ 32.8 ms and `cpu_gpu_us` ≈ 31.4 ms (`sky123` arm-0 rows, OLD —
rows, not a measurement of anything in this session). 60 FPS is not promised.

## Rule of the session

As since session 102 with the additions of 121–124: every decision in `ROADMAP.md` before the first action — also a rule
constant that differs from an accepted decision, BEFORE the agent brief, the lead as author; agent paragraphs tagged and
accepted explicitly; amendments as new items; a sealed consequence is not revoked. Seals with fixtures and ONE full
`mutlib` v4.1 run on the final text with filled seal constants — only fixtures and `--only` during development (item 40
(е)(3); a repeat is allowed only when the mutant list alone changes, item 54 (а)); suites end with `ALL OK`; edit scripts
write LF; backslashes only through files written by Write. **The seal names every window with its item number and every
windowed scorer has an edge fixture (item 55 (б)).** **Every term of LB_acc carries a proven LOWER direction; a term without
one is left out (item 55 (д)(1)).** **No emulator code and no game run in this session (item 55 (д)(3)):** a design that
needs new data from the game stops and asks the lead in its report — a ROADMAP line comes before any code. The bench is a
timing measurement: sealed, exclusive (`C:/kyty/SEALED_RUN.lock`), `procload` and idle checks before the lock, one attempt.
**While the lock exists no run — lead and watchdog tasks included — edits, commits or starts processes (item 25 (ж)).**
Long runs in the foreground (timeout 600 000 ms), start verified; the `procload` wait ≤ 540 s per call. No agent creates
user interactions (item 16). Privacy grep before commits (user name, e-mail, launcher user name); foreign applications are
not named in committed text. **LB_acc is never a cost of a built thing, a gain or a forecast.**

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

The specialist sets `done` with a report; the platform moves the step to `in_review` and wakes the lead; the lead checks the
artifacts (not the report), writes the decisions the next step needs into `ROADMAP.md`, and sets `done` with "Принято: …" —
only then the next step unblocks. A return is "Доработать: …" in the same task, at most twice (item 23 (в)). Root `HPP-3`
is `blocked` on the terminal step; the issue watchdog on `HPP-3` is the only liveness guard (the routine is paused, item
40 (д)).

## Steps

0. **Harness Engineer — port `C:/kyty/s125`** from `s124`: `procload.py`, the name guard, `idle124.py` → `idle125.py`,
   `hostdev`, the lock handling of `go124a.sh` reduced to a bench chain `go125a.sh` (no game: no `enter_scene`, no build
   install; a sealed bench tag `lb125` with one attempt and `--out C:/kyty/s125/runs125/<tag>.score.json`). Fixtures
   `ALL OK`, full `mutlib` of the changed helpers only. No game run, no bench run.
1. **Probe Designer — design** `docs/session-125/design125.md` (+ `design/`) under item 55 (д): (1) what the GuestGpu must
   minimally do per operation to ACCEPT a plan computed on the walker thread (hand-off, register-state application, order),
   read from the spine code of 117–118 and the models of 119 — named per term; (2) the LOWER-bound model LB_acc = Σ terms,
   µs per reference frame, with a DIRECTION TABLE (model: §11 of design123 / §7 of design124) proving each term is a lower
   side — or naming why it is not and leaving it out; (3) data from existing sealed logs only — the `g2_119` population
   (session 119, NEW) for operation counts and state volume per operation (which counters, which window — named with its
   item number); if a needed number is not in any sealed log — a question to the lead, not a guess; (4) the offline floor
   microbenchmark: what it times, why its reading is a floor on this machine (cache state, copy width, no contention), the
   estimator and its 2SE, the idle and load guards; (5) the reading exactly as item 55 (д)(2) (LB_acc ≥ 484.7 → A-walker
   CLOSED; < 484.7 → condition 2 next; direction not lower → NOT_RESOLVED); (6) guards and what the seal must check.
2. **Red Team — adversarial review of the design** (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT with numbered RCs),
   specifically: can LB_acc be OVERstated (a term that is not a lower bound, an operation count from the wrong population or
   regime, a bench that times more than the floor, double counting with G₂'s own members)? A close by LB_acc is only sound
   if it is truly a lower bound. The lead accepts the design and the RCs by a ROADMAP line BEFORE step 3; a design revision
   (2a) is added by a ROADMAP item if needed.
3. **Harness Engineer — bench, scorer, fixtures, the seal** `pred/01_lb125.md` with the reading of item 55 (д)(2), the guard
   list of the accepted design, windows named with item numbers, edge fixtures; ONE full `mutlib` run on the final text;
   `SEALS125.txt`. No game run.
4. **Harness Engineer — the sealed bench run** `lb125` (lock, `procload --wait-s 540`, idle, one attempt) and its scoring.
5. **Session Auditor — audit** (independent recount of LB_acc from the logs and the bench output, protocol, MAJOR/MINOR,
   debts), `audit125/`, git `docs/session-125/audit/`.
6. **Roadmap Lead — close:** verdict in `ROADMAP.md`, documents (`FACTS.md` → `docs/local-session-125.md`, `HANDOFF.md`,
   `CLAUDE.md` = `AGENTS.md`, `docs/agent/`, `agent-team.md` entry point, `LOOP_STATE.md`), commit of both repositories,
   the chain of session 126 created before closing.

## Must not be claimed

60 FPS; LB_acc, G₂ or any A-walker number as a gain, a speed-up or a forecast of one; that A-walker "would save" anything
(G₂ is a model with [I] members; census prices in this program were wrong by 2–20×); A-walker as alive, designed or proven
before kill condition 2 is measured; an LB_acc term without a proven lower direction; numbers from the OLD regime as members
of the NEW model (or the reverse) without a ROADMAP line; frame skipping as shipped, correct, or anything but closed; U,
`f_free` or the 11.4 ms ceiling as a gain; that GuestGpu is proven critical (item 24 (б)); the vblank staircase as a reason
for invisibility (item 25 (б)); a timing number beside another heavy job.
