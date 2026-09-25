# Session 115 — the presentation record ring fixed (no main-thread present during shader preparation) and verified by a sealed boot check; `titleasync=1` shipped; `mutlib` v3 accepted and v4 built (full runs ×3.5 faster; the selective path barred until v4.1); no speed-up of the game shipped

**Single source of truth for session 115.** Mirrored into git as `docs/local-session-115.md`. Harness root
`C:/kyty/s115`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 115 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–11 (session 114 items 16
closes the previous session).

**Opening numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1 daguard=1
bdanarrow=0 titleasync=0`, installed build `916f6489…` (session 114). **Closing:** the same defaults with
**`titleasync=1`**; installed build **`d3a981a2…`** (git `7c73f26`; pinned copy `C:/kyty/s115/kyty_emulator_d3a981a2.exe`).
60 FPS is not promised.

---

## 1. Result

1. **The ring fix** (item 1, `503a8bf`): `WindowPrepareShaders` no longer presents from the main thread — the VideoOut
   present thread already presents the preparation overlay while it is active; before the SDL main loop `UpdateTitle`
   always posts (the present thread is not parked any more); atomic overlay progress counters; `KYTY_PREPARE_MAIN_PRESENT=1`
   (measurement only) restores the old present as a positive control; the wait line reports `presents_other=` /
   `presents_main=`. `titleasync` default 1 in the same build (`7c73f26`).
2. **Seal 01 `chk115`: PASS** (after a pre-seal check with one BLOCKER fixed — the control never prints `GpuClockPin:` —
   and amendment 1 of the load gate): `boot115a` held the preparation screen 10 111 ms with 607 overlay presents by the
   present thread and 0 by the main thread; `boot115c` (`KYTY_TITLE_ASYNC=1`) 10 115 ms, 606 / 0; the control `boot115b`
   still dies at `commandRecorder.cpp:326`; video `vid115` 3 894 frames, 0 glitches, BDA NEW. ⇒ build `d3a981a2` stays,
   `titleasync=1` shipped, C1 closed by construction (reviewed by reading; no run-time guard).
3. **F2 measured offline** (item 9): the flip mutex is held 2.43 ms per flip (median), GuestGpu never waited in the scene
   window ⇒ a correctness debt, not a speed track.
4. **`mutlib` v3 accepted** (item 4): 11 suites, 1 225 / 1 225 rows equal to v2; the acceptance took 3 h 54 min (three full
   passes of the big suites) and blocked the session — my planning error (user: «я ебал ждать каждую сессию по 3-6
   часов»).
5. **`mutlib` v4** (items 3, 10; user: «делай все 5 пунктов после приемки»): review4 fixes plus selection, shared
   read-only fixtures, early exit (a killed mutant skips a median 98–99 % of the suite), `--python`, fixture profiling.
   Accepted (trimmed): all verdicts equal; **full `ttl114b` 20.3 min against ~70**, `net112` 14 min; PyPy equal but not
   faster. Review: **`--changed-from` unsafe** when the derived test suite changed (MAJOR-1) ⇒ **barred until v4.1**;
   `copy2`/`copytree` bypass the fixture guard (MAJOR-2, not used by our suites). v4 is the tool for FULL runs.
6. **Session audit** (item 11): recount CONFIRMED; code clean; **MAJOR P1** — a v4 mutlib run (2 workers) overlapped the
   whole sealed chain; the verdict stands (functional checks), but Q3 and the item-9 levels are not clean measurements.

## 2. Code

`503a8bf` (ring fix), `7c73f26` (titleasync default 1). Builds: **`d3a981a2`** (installed). Seals: `docs/session-115/`
(pred 01 + amendment 1, check115, go115a/go115r, procload). mutlib: frozen v3 `docs/session-115/mutlib_v3/` (5d2f2f90),
frozen v4 `docs/session-115/mutlib_v4/` (b666df35). No push.

## 3. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `go115a` ×2 | 01 | refused before any run (foreign `game-X` 30 min; then a mutlib run of mine) | no run |
| `vid115` | 01 | video, build `d3a981a2`, defaults | PASS (3 894 frames, 0 glitches, NEW) |
| `boot115a`, `boot115c` | 01 | `KYTY_PREPARE_HOLD_MS=10000`, knob default / 1 | PASS (10.1 s hold, 607 / 606 presents, 0 main) |
| `boot115b` | 01 | + `KYTY_PREPARE_MAIN_PRESENT=1` (control) | fatal `:326` as expected |

## 4. Proved, and not proved

**Proved:** the old main-thread preparation present trips the ring owner check; without it a 10-s preparation hold
completes with the overlay drawn by the present thread at ~60 Hz, at both knob values; the build records a clean video.
**Not proved:** a long COLD preparation (only a warm one held for 10 s); C1 at run time; any game speed effect; the
item-9 levels (measured beside a mutlib run).

## 5. Next

`docs/next-session-116.md`: (1) `mutlib` v4.1 — test-aware selection (the parent report's kill cases), static refusal of
replay on `copy2`/`copytree`, a `--no-memo` timing on a big suite; chains refuse while any `mutlib.py` process lives;
(2) the next speed track by the rule, from a clean phase breakdown (`mutsite`/`pathlap`) on `d3a981a2`; (3) F2 stays a
debt.
