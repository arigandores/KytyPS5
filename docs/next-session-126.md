# Session 126 — the K3 kill test: an UPPER bound of what skipping the render-target check can remove

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 62 (the close of 125: verdict (а), audit
corrections (б), superseded text (в), A-walker parked (г), the course (д), the lever inventory (е), **the constants of this
session (ж)(1)–(6)**, the parallel K2 task (з), the chain (и)); item 61 (Lever Researcher retrospective: K3 is item (е));
item 56 (course section, base every 5 sessions — deadline chain of 128); "СЕССИЯ 120" (census `spcen`: part A — render
targets remembered inside an open pass, counters `pl_em_rt_hit(g)_ns`, 340.2 point / 686.9 upper; its close item);
session 59 (gate `rtfast`: witnesses `bind_stamp`, backing, view info, desc metadata, `TextureCache::MetaEpoch()`,
`AssociateStencil`); `ps5 em/CLAUDE.md` environment entries of 120 (`spcen`), 96 (`pathlap`: `pl_em_rt_ns` is the
`AcquireRenderTargets` span of the emit chain), 59 (`rtfast`); `ps5 em/docs/agent-team.md`; the retrospective document
`retro` on `HPP-82` (§3.1 K3, K7). Code: `src/graphics/host_gpu/renderer/renderDraw.cpp` (emit chain, `AcquireRenderTargets`
call site ~`:2921`), `colorRenderTarget.cpp`, `depthRenderTarget.cpp`, `renderMemo.h`, the PM4 context-register handlers
in `guest_gpu/graphicsRun.cpp`.

**Open the report with these numbers:** installed build `d3a981a2…` (`7c73f26`); reference speed **50.9 %** (16 667 /
32 757.6 µs — `sky123` arm 0, session 123, build `e4bb66ca` at `skipceil=0`, BDA **OLD**, pin); remainder 16 090.6 µs;
**14 sessions in a row without shipped speed (112–125)**; K3 best-case ceiling ≤ 1 550 µs [I] (all of `pl_em_rt_ns`, all
rows of `obs116`, NEW) = 9.6 % of the remainder (4.8 % halved); honest estimate before measuring: `spcen` A 340.2 / 686.9
[census], `rtfast` fast path already in 99.6 % of checks ⇒ the expected outcome is **K3 CLOSED**. A-walker parked (item 62
(г)). 60 FPS is not promised.

## Rule of the session

As since session 102 with the additions of 121–125: every decision in `ROADMAP.md` before the first action — also a rule
constant that differs from an accepted decision, BEFORE the agent brief, the lead as author; agent paragraphs tagged and
accepted explicitly; amendments as new items; a sealed consequence is not revoked. Seals with fixtures and ONE full
`mutlib` v4.1 run on the final text with filled seal constants — only fixtures and `--only` during development (item 40
(е)(3), 54 (а)); suites end with `ALL OK`; edit scripts write LF; backslashes only through files written by Write. **Blocks
by `GateArm:` lines, never by `blk` (audit 125 MAJOR-1).** **The seal names every window with its item number and every
windowed scorer has an edge fixture (item 55 (б)); the level statistic (row mean or median of block means) is named beside
the window (item 62 (б) MINOR-3).** **Every term of R_K3⁺ carries a proven UPPER direction; a term without one enters whole
(item 62 (ж)(1)).** **The one-attempt mechanism of the sealed run is a ROADMAP line with the step (MINOR-1 of 125).** The
measurement knob is default 0, MEASUREMENT ONLY, and does not change emulation at any value; the installed build stays
`d3a981a2`. **While `C:/kyty/SEALED_RUN.lock` exists no run — lead, watchdog tasks and the Lever Researcher included —
edits, commits or starts processes (item 25 (ж)).** Long runs in the foreground (timeout 600 000 ms), start verified;
the `procload` wait ≤ 540 s per call. No agent creates user interactions (item 16). Privacy grep before commits; foreign
applications are not named in committed text. **R_K3⁺ is never a gain, a cost of a built thing or a forecast.**

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

The specialist sets `done` with a report; the platform moves the step to `in_review` and wakes the lead; the lead checks the
artifacts (not the report), writes the decisions the next step needs into `ROADMAP.md`, and sets `done` with "Принято: …" —
only then the next step unblocks. A return is "Доработать: …" in the same task, at most twice (item 23 (в)). Root `HPP-3`
is `blocked` on the terminal step; the issue watchdog on `HPP-3` is the only liveness guard.

## Steps

0. **Harness Engineer — port `C:/kyty/s126`** from `s124`/`s125`: `procload.py`, the name guard, `idle126.py`,
   `envchk126.py`, `hostdev126.py`, `enter_scene.py`, `gates_base.txt`, the chain `go126a.sh` with the game (smoke tags
   and one sealed tag; install of a pinned build copy and restore of `d3a981a2` afterwards; `--out
   C:/kyty/s126/runs126/<tag>.score.json`). Fixtures `ALL OK`, full `mutlib` of the changed helpers only. No game run.
1. **Probe Designer — design** `docs/session-126/design126.md` (+ `design/`) under item 62 (ж): (1) FIRST the cheap path
   (ж)(3): can an existing sealed log (`cen120` `sp_*` / `pl_em_rt_hit(g)_ns`, `obs116`, `g2_119`, others) bound R_K3⁺
   from ABOVE without a new counter — with proof, or why not; (2) the complete list of invalidation sources of the
   render-target acquisition, derived from code (every path that writes CB/DB/DB_* context registers, epochs, clears,
   witnesses), with a completeness argument; (3) the model R_K3⁺ = Σ terms, µs per reference frame, with a DIRECTION TABLE
   (model: §11 design123 / §7 design124 / §3.5 design125) proving each term is an upper side — or entering it whole; (4)
   the measurement knob if needed: counters, sites, cost, why it cannot change behaviour; the split of `pl_em_rt_ns`
   (witness checks vs acquisition vs pass begin); (5) the population, window and level statistic by item number, the BDA
   regime beside it, the base arm (ж)(5); (6) the reading exactly as item 62 (ж)(2), including the K7 condition; (7)
   guards and what the seal must check. Questions to the lead in the report, not guesses.
2. **Red Team — adversarial review** (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT with numbered RCs), specifically: can
   R_K3⁺ be UNDERstated so that K3 closes falsely — a missed invalidation source, a term that is not an upper bound, a
   population or regime that is not the reference, a span narrower than what a skip would remove, cost of the new check
   hidden in another phase? The lead accepts by a ROADMAP line BEFORE step 3 (or cancels steps 3–7 by (ж)(3)).
3. **Emu Engineer — the knob** (MEASUREMENT ONLY, default 0, last line of knobs; `check_gate_order.py` before build), a
   pinned build copy in `C:/kyty/s126`, the installed build unchanged.
4. **Red Team — code review** of step 3 (PASS / PASS_WITH_FIXES / FAIL; BLOCKING items), including "no behaviour change at
   any value".
5. **Harness Engineer — smoke** on the pinned build (counters alive, identities, cost of the knob, BDA regime), a report
   with rows only.
6. **Harness Engineer — scorer, fixtures (every term and every window edge), the seal** `pred/01_k3c126.md` with the
   reading of item 62 (ж)(2) and the one-attempt mechanism; ONE full `mutlib` on the final text; `SEALS126.txt`.
7. **Harness Engineer — the sealed run** on the reference (lock, `procload --wait-s 540`, idle, one attempt, pin, base arm
   with the knob 0) and its scoring; restore `d3a981a2`.
8. **Session Auditor — audit** (independent recount of R_K3⁺ from the logs, own parser, blocks by `GateArm:`; protocol;
   MAJOR/MINOR; debts), `audit126/`, git `docs/session-126/audit/`.
9. **Roadmap Lead — close:** verdict, the course section and the §1 row (with the new base), the K2 document of the Lever
   Researcher (item 62 (з)) answered item by item, documents, commit of both repositories, the chain of session 127
   (K5 bench, unless K3 opens a prototype) created before closing.

**Parallel, outside the chain (item 62 (з)): Lever Researcher — K2 first step**, read-only over existing sealed logs; no
chain step waits for it.

## Must not be claimed

60 FPS; R_K3⁺, `pl_em_rt_ns` or any census number as a gain, a speed-up or a forecast (census prices here were wrong by
1.6–20×); K3 as open, designed or shippable because R_K3⁺ ≥ 500 (a census does not open a track, rule 4); K7 closed
without the containment proof of item 62 (ж)(2); a term of R_K3⁺ without a proven upper direction left out; numbers from
the OLD regime compared with NEW, or rows built by `blk`; the base arm of a measurement build as a measurement of
`d3a981a2`; A-walker as alive or dead; the vblank staircase as a reason for invisibility (item 25 (б)); a timing number
beside another heavy job.
