# Session 127 — the K3 prototype: skip the render-target resolution and acquisition, with a self-check, a sealed ABBA and video

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 76 (the close of 126: verdict (а), audit
corrections and the lock-before-`procload` rule (б), the course (в), K2 answered item by item (г), `recon126` (д), AnyPS5 (е),
**the lever inventory (ж)**, **the constants of this session (з)(1)–(7)**, the chain (к)); items 63, 64, 67, 68, 70, 71 (the K3
census of 126: groups `G_mask`/`G_slot[n]`/`G_dact`/`G_depth` of item 64 (б), generations outside `HW::Context` (RC8), the
non-register sources, the one-latch-per-operation trap); item 66 (а) (one attempt per registered tag); items 19, 74 (one full
`mutlib`, add-only top-up); `docs/session-126/design126.md` rev. 2 (§3.3 invalidation sources, §4 sites, §12 RC table),
`docs/session-126/design/codereview126.md`, `docs/session-126/audit/AUDIT126.md`; `ps5 em/CLAUDE.md` environment entries of 126
(`rk3cen`), 120 (`spcen`, `VulkanImage::state_serial`), 60 (`progmemo`/`progmemocheck` — the self-check pattern), 59
(`rtfast`); `ps5 em/docs/agent-team.md`. Code: `src/graphics/host_gpu/renderer/renderDraw.cpp` (`PrepareDrawRenderState`,
`AcquireRenderTargets` call site, `Rk3*` hooks of commit `8c4baf90`), `colorRenderTarget.cpp`, `depthRenderTarget.cpp`,
`renderMemo.h`, `guest_gpu/pm4Handlers.cpp` (47 D_census setter calls, `n3prime_table.txt`), `src/common/gates.{h,cpp}`.

**Open the report with these numbers:** installed build `d3a981a2…` (`7c73f26`); course base **52.0 %** (16 667 / 32 067.2 µs —
`k3c126` arm B, session 126, measuring build `14bead6f`, BDA **NEW**, pin; NOT comparable with 50.9 % of session 125, which was
OLD on `e4bb66ca`); remainder 15 400.2 µs; **15 sessions in a row without shipped speed (112–126)**; K3 kill test:
**R_K3⁺ = 2 096.9 µs (NEW) ≥ 500 — K3 NOT CLOSED**, an upper bound that contains the instrument's own cost; 94.6 % of draws
write no relevant CB/DB group (`rk3_w`/`rk3_n`); T0 alone 1 370.2. Honest estimate before measuring: censuses of this program
overstated by 1.6–20×, and the skip still has to check the non-register witnesses — the prototype's gain is probably several
times below 2 096.9; the shipping bar is −100 µs. 60 FPS is not promised.

## Rule of the session

As since session 102 with the additions of 121–126: every decision in `ROADMAP.md` before the first action — also a rule
constant that differs from an accepted decision, BEFORE the agent brief, the lead as author; agent paragraphs tagged and
accepted explicitly; amendments as new items; a sealed consequence is not revoked. Seals with fixtures and ONE full `mutlib`
v4.1 run on the final text with filled seal constants (add-only top-up by item 74) — only fixtures and `--only` during
development; suites end with `ALL OK`; edit scripts write LF; backslashes only through files written by Write. **Blocks by
`GateArm:` lines, never by `blk`.** The seal names every window with its item number, every windowed scorer has an edge
fixture (item 55 (б)); the level statistic is named beside the window. **The harness checks `C:/kyty/SEALED_RUN.lock` BEFORE
`procload.py` in every call, smoke included (item 76 (б), MINOR-2 of 126).** **The knob is read ONCE per draw.** **Default 0 is
the old path byte for byte.** One attempt per registered tag (item 66 (а)); no restart to obtain a BDA regime (item 76 (г)(6)).
The installed build stays `d3a981a2`; the measuring build is a pinned copy built from a committed tree (item 70 (в)). **While
`C:/kyty/SEALED_RUN.lock` exists no run — lead included — edits, commits or starts processes (item 25 (ж)).** Long runs in the
foreground (timeout 600 000 ms), start verified; the `procload` wait ≤ 540 s per call. No agent creates user interactions
(item 16). Privacy grep before commits; the platform name is allowed, the company name and foreign applications are not
(item 76 (и)). **R_K3⁺ is never a gain; a Δ of the prototype is a gain only by the reading of item 76 (з)(5).**

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

The specialist sets `done` with a report; the platform moves the step to `in_review` and wakes the lead; the lead checks the
artifacts, writes the decisions the next step needs into `ROADMAP.md`, and sets `done` with "Принято: …" — only then the next
step unblocks. A return is "Доработать: …" in the same task, at most twice. Root `HPP-3` is `blocked` on the terminal step.

## Steps

0. **Harness Engineer — port `C:/kyty/s127`** from `s126`: `procload.py`, the name guard, `idle127.py`, `envchk127.py`,
   `hostdev127.py`, `enter_scene.py`, `gates_base.txt`, the chain `go127a.sh` with the game: smoke tags (reference verify,
   desert verify `--level intro_next --stable-draws 500`, positive control, validation), the sealed tag `k3p127` and the
   registered tags `k3k127` (verify), `k3v127`/`k3w127` (video `KYTY_REC`, knob 1 / 0); lock check before `procload` with a
   fixture (item 76 (б)); install of a pinned build copy and restore of `d3a981a2`; `--out C:/kyty/s127/runs127/<tag>.score.json`;
   the one-attempt mechanism of item 66 (а) for every registered tag. Fixtures `ALL OK`, full `mutlib` of the changed helpers
   only. No game run.
1. **Probe Designer — design** `docs/session-127/design127.md` under item 76 (з): (1) the skip set — groups of item 64 (б) and
   every non-register source (the list of design126 rev. 2 §3.3 may grow, never shrink; image state between draws, pass
   closure by a non-draw operation, command-buffer/submit boundary), with a completeness argument and code citations;
   (2) what exactly is skipped (resolution in `PrepareDrawRenderState` + `AcquireRenderTargets`) and what stays on the path
   (pass begin, `Image::Transit`, memo writes) — each with a citation and a reason; (3) the self-check `rtskip=2`: which
   outputs are compared (all that downstream reads: targets, depth, pass info, memo slots/versions, layout side effects),
   fresh result on mismatch; (4) the positive control `rtskip=3`: which source it ignores and why the control is not
   tautological; (5) counters, sites, cost, refusals, the once-per-draw latch, proof that 0 is the old path byte for byte;
   (6) population, window, estimators and the reading exactly as item 76 (з)(4)–(5); (7) guards the seal must check.
   Questions to the lead in the report, not guesses. No game run, no emulator code.
2. **Red Team — adversarial review** (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT, numbered RCs): can the skip produce a
   wrong render target that the self-check does not see (a missed source, an incomplete comparison, a tautological positive
   control, a latch torn between resolution and acquisition)? can the ABBA be biased (Δ draws, a verify cost left in the timed
   arm, a regime split)? is 0 really the old path? Checked against code and logs, not against the design's text. The lead
   accepts by a ROADMAP line BEFORE step 3.
3. **Emu Engineer — the knob `rtskip`** (0..3, default 0, last knob row; `check_gate_order.py` before build), commit →
   `git status --short -- src` empty → build → pinned copy `C:/kyty/s127/kyty_emulator_<sha8>.exe`; the installed build
   unchanged. No game run.
4. **Red Team — code review** (PASS / PASS_WITH_FIXES / FAIL; BLOCKING items) against the accepted design and item 76 (з),
   including "0 is the old path byte for byte" and the once-per-draw latch.
5. **Harness Engineer — smoke** on the pinned build: `rtskip=2` on the reference and in the desert (`rts_bad` = 0, `rts_chk`
   > 0), `rtskip=3` (`rts_bad` > 0), `rtskip=1` under `--vulkan-validation true` on the reference (0 errors), cost and BDA
   regime; rows only, questions to the lead.
6. **Harness Engineer — scorer, fixtures (every estimator, every window edge, every outcome of item 76 (з)(5)), the seal**
   `pred/01_k3p127.md` (reading, one-attempt mechanism, base arm, BDA regime rule); ONE full `mutlib`; `SEALS127.txt`.
7. **Harness Engineer — the sealed `k3p127`** (lock, `procload --wait-s 540`, idle, one attempt, pin, ABBA
   `rtskip=0|rtskip=1`) and its scoring; then `k3k127` (verify, 300 s), `k3v127` and `k3w127` (videos, `s51_vidglitch.py`,
   a frame sheet of both videos side by side); restore `d3a981a2` after every run.
8. **Session Auditor — audit** (independent recount of Δ and of the base from the logs with an own parser, blocks by
   `GateArm:`; the verify run; protocol; MAJOR/MINOR; debts), `audit127/`, git `docs/session-127/audit/`.
9. **Roadmap Lead — close:** verdict by item 76 (з)(5) (`RTSKIP_GAIN` / `RTSKIP_NO_GAIN` / `NOT_RESOLVED` /
   `RTSKIP_INCORRECT`), the course row, the re-assessment K14 vs K5 (+ K16) for session 128, documents, commit of both
   repositories, the chain of session 128 (its step 0 ships `rtskip=1` if the verdict allows) created before closing.

**Outside the chain:** nothing (item 76 (к)); any off-chain task gets a formal consumer (item 73 (в)).

## Must not be claimed

60 FPS; R_K3⁺, T0, `pl_em_rt_ns` or any census number as a gain; a Δ of `k3p127` as a gain outside the reading of item 76
(з)(5), in another scene, or in another BDA regime than the one it was measured in; `rtskip=1` as correct without every
condition of item 76 (з)(3); the self-check or the positive control as proof of completeness of the source list (they are
evidence on the tested scenes); 52.0 % as growth over 50.9 %; the base arm of a measurement build as a measurement of
`d3a981a2`; rows built by `blk`; a timing number beside another heavy job.
