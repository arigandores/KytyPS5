# Session 112 — `daslot=1` KEPT: against `daslot=0 daguard=0` of the same build it shortens the mean frame by 243.1 ± 62.6 µs at the pin (≈ +0.79 % game speed); against the session-110 code still unmeasured (audit); the guard-free mode verified with transitions (61.5 M checks, 0 bad)

**Single source of truth for session 112.** Mirrored into git as `docs/local-session-112.md`. Harness root
`C:/kyty/s112`. Everything below is measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1`
and the new `daguard=1`. `net112` block levels: arm 0 (today) mean `dt_us` 30 829.7 (≈ 0.541× game speed), arm 1
(no guards, `daslot=0`) 31 042.9. That run was in the NEW BDA regime (`bda_scan` ≈ 52 a frame); session 111's `shp111`
was in OLD (≈ 1 068) — between-run levels are not comparable. 60 FPS is not promised.

---

## 1. Result

1. **Port** `C:/kyty/s111/s112_port.py` (`fd469ad6…`, 3 147 lines): `PORT DIAGNOSTIC: clean; carried=7455 ledger=84
   skipped=31`; 67 sealed texts (65 in `prev111/pred`); `gates.cpp` 141 entries (111 + 30), ABSENT 42.
2. **Code** (`7e892d5`; ROADMAP decision after session 111, items 1 and 3, recorded first): knob **`daguard`**
   (`KYTY_DRAW_AHEAD_GUARD`, 0..1, default 1, LAST knob row) — at `daslot=0` and `daguard=0` the M1 queue, holding
   `m_mutex` and `ahead_queue_mutex`, skips the slot guards and reads hints directly (`ReadHintLocked`); counter
   `da_q_noguard`. `GuardSlot` yields to the OS after 256 spins (`da_guard_yield`). Workers read the thread count from
   an atomic (`ahead_thread_count`) — the old `ahead_threads` size race. Comments on `plan_fingerprint`/`plan_class`/
   `taken`/`pixel` and `daslot=0` corrected. Build **`b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7`**.
3. **Records** (`b12d6b5`): `vdg112`, `net112` (arm 0 = today, arm 1 = the candidate — the arm order refines item 1 of
   the decision after session 111 to the "arm 0 = today" convention, recorded before the seal), the build's video.
4. **`vdg112`** (sealed `pred/01_vdg112.md` `e4029a49…`, 300 s, pinned, ABBA `daslot=0 daguard=0 | daslot=1 daguard=1`,
   `smemocheck=1` in place, 64 blocks, ADMITTED): **GO** — `da_chk_ok` 61 535 031, `da_chk_bad` 0, `da_slot_bad` 0,
   mismatch lines 0; checks/hits 0.99998 (arm 0) / 1.000001 (arm 1); `da_q_noguard` 1 070 a flip only in arm 0,
   `da_q_free` 1 074 only in arm 1; `da_guard_yield` 0, `da_guard_busy` 0, `da_hint_torn` 0; D1–D5 HIT.
5. **`net112`** (sealed `pred/02_net112.md` `f5269a7b…`, ABBA arm 0 `daslot=1 daguard=1`, arm 1 `daslot=0 daguard=0`,
   600 s, pinned, 96 pairs, ADMITTED): **KEEP `daslot=1`** — Δ(arm 1 − arm 0) mean `dt` **+243.1 µs (2·SE 62.6, t 7.77)**
   on frames 10–89; secondary 60–88 +278.3 (2·SE 111.5); Δ`cpu_net` +240.7; `da_walk_us` +49.1; `gpu_busy_us` −22.5;
   `da_late` −5.3 (11.2 → 5.8). **Session 111's gain against the no-guard profile: −243.1 ± 62.6 µs.** N2–N7 HIT;
   **N1 MISS** — arm-1 walker time per `QueueDrawAhead` call 1.189 µs against the band [0.90, 1.12]: without the guards
   it did not return to the ~1.0 µs of pre-session builds (arm 0: 1.142).
6. **`vid112`** (build `b47b58a9`, pinned, defaults): 3 980 frames, 0 glitches, `da_q_free` 1 123 a flip,
   `da_q_noguard` 0 — `check112.py` (38 fixtures, 24 mutants, hashed in SEALS112 before its run) PASS.

## 2. Harness

`C:/kyty/s112`: `vdg112.py` (new; 63 fixtures, 36 mutants killed — but not every threshold edge: 7 of 10 audit mutants survive), `net112.py`
(from `shp111.py` by `make_net112.py`; 205 fixtures; 277 mutants killed; `CONSTANTS` now accepts sealed seal values —
audit-111 MINOR-5), `check112.py` (38 fixtures, 24 mutants), `go112.sh` (holds the sealed-run lock), `gates_chk.txt`
(`smemocheck=1` in place), `gates_guard0.txt`; build copy `kyty_emulator_b47b58a9.exe`.

## 3. Source, builds, provenance

Commits: `5609d47` (session 111 close), `7e892d5` (code), `b12d6b5` (records), `391f8d7` (seal 01 + port), `8acab29`
(seal 02 + scorers + chain), `460a61a` (results), the session commit. Build `b47b58a9…` (installed; vdg112, net112,
vid112). Not bit-reproducible. No push.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `vdg112` | verify, ABBA no-guard / shipped, `smemocheck=1`, 300 s | GO: 61.5 M checks, 0 bad |
| `net112` | ABBA today / no-guard, 600 s | KEEP: Δ +243.1 (2·SE 62.6) for the no-guard arm |
| `vid112` | video of build `b47b58a9`, defaults | 3 980 frames, 0 glitches; `check112` PASS |

## 5. Next

The size question of `daslot` is closed as a size question (the default does not depend on it; decision after session
112, item 1). Session 113: the BDA regime — OLD (~1 066 scans a frame) is the usual start state and goes with longer
frames across runs (audit indication, +27…+442 µs in 5 of 5 pairs). An offline census of every archived log with
`bda_scan`, code reading of `PrepareBda` and the region stamps, an instrument if needed, then a knob only if the
mechanism is found. Plan: `docs/next-session-113.md`.

## 6. Proved, and not proved

**Measured.** At the pin in Sky Garden, the shipped `daslot=1` is 243.1 ± 62.6 µs a frame faster than the same build's
`daslot=0` without slot guards — the profile closest to the session-110 code that one run can measure; the guard-free
mode and the transitions between modes produced 0 mismatches over 61.5 M checked takes.
**Not proved.** The gain against the session-110 code (arm 1 is not it: the walker's per-call time stayed at 1.19 µs
against ~1.0 — audit MAJOR); anything off the pin, in other scenes, or across BDA regimes; additivity; 60 FPS.

## 7. Audit

One agent, three lenses; sealed addendum `pred/03_audit112.md` (`32d27a4a…`); report and scripts
`C:/kyty/s112/audit112/` (`AUDIT112.md`).

* **Recount — CONFIRMED** (robust: full block +243.2, thirds +241 / +230 / +259; clocks and DRS area equal; the gap is
  the one-vblank share 0.149 → 0.135).
* **Protocol — HOLDS.** **Code — NOT REFUTED** (the unguarded argument holds: every `AheadTake`/`AheadNote`/generation
  bump is inside `ProgramCache::Get` under `m_mutex`; every `QueueAhead` under `ahead_queue_mutex`).

Findings: **MAJOR** — arm 1 is not the pre-session profile: its walker call costs 1.18–1.19 µs against 1.006–1.033 in all
six pre-session ABBA arms; the guards were only a quarter of session 111's excess; seal 02's title and §4 and the
scorer label ("against the pre-session profile") are wrong. Quote −243.1 ± 62.6 µs against `daslot=0 daguard=0` of
`b47b58a9` (NEW regime); against session 110 unmeasured (cross-run indication ≈ −85 µs). **MINOR** — the arm order
reached the scorer agent 18 s before ROADMAP recorded it (still before the seal); `vdg112` fixtures miss threshold edges
(7 of 10 new mutants survive, none near the real values); `check112` lacks fixtures for two markers and the real report
format; seal 01 promised ~70 switches (32 happened); the `GuardSlot` yield never fired; `AheadStopThreads` clears
`ahead_threads` without `ahead_queue_mutex` (destructor only). **BDA regime (indication):** no run switched regime
mid-run; across runs OLD was slower in 5 of 5 matched pairs (+27…+442 µs; pooled 600-s arms +207).
