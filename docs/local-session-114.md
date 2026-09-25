# Session 114 — the 3-s stall explained (the window title waited for a busy SDL main thread under the flip mutex); the fix, knob `titleasync`, measured (SHIP by its ABBA) but kept at default 0 by the sealed boot-check rule; a hidden startup crash found (`commandRecorder.cpp:326`, the presentation record ring owned by one thread); no speed-up shipped

**Single source of truth for session 114.** Mirrored into git as `docs/local-session-114.md`. Harness root
`C:/kyty/s114`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 114 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–16.

**Opening numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1 daguard=1
bdanarrow=0`; installed build at the start `1678d3f4…` (session 113). **Closing:** the same defaults plus
`titleasync=0` (the knob exists, default 0); installed build **`916f6489…`** (`74e2ad7`; pinned copy
`C:/kyty/s114/kyty_emulator_916f6489.exe`); HEAD source `1713c6d` has default 0 too but also the measurement-only
boot tools (not built as installed). 60 FPS is not promised.

---

## 1. Result

1. **The mechanism of the 3-s stall of `vbn113k`** (offline, `stall/STALL_PATHS.md`, read-only agent + my checks): the
   presentation thread holds `VideoOutConfig::mutex` for the whole present and calls `WindowContext::UpdateTitle` inside
   it, which queued `SDL_SetWindowTitle` to the SDL main thread and **waited for it without a bound on every present**.
   While the main thread is busy, GuestGpu waits in `ReserveFlipRequest` on the same mutex before it submits the flip, the
   lazy EOP interrupt stays on the unsubmitted tick and the guest waits for it. Every other candidate path was impossible by
   the code or excluded by the log. What kept the main thread busy in `vbn113k` was not observed.
2. **Knob `titleasync`** (`KYTY_TITLE_ASYNC`, 0..1, read on every `UpdateTitle`): 1 puts the title into a slot and posts
   one task to the main thread without waiting (the main thread applies the latest text); **only once the SDL main loop
   runs** (review C1: before `WindowRun` the waiting path parks the present thread while `WindowPrepareShaders` presents).
   Instruments without behavior change: `pres_title_ns/_n`, `flip_rsv_wait_ns/_n`, `flip_hold_ns/_n` (`FlipHold:` lines),
   `mt_age_ns`/`mt_n` (`MainTaskLate:` lines), `MainThreadWait:` lines; positive control `KYTY_MAIN_STALL_TEST=<frame>:<ms>`.
3. **Control (seal 01 `ctl114`): PASS.** At `titleasync=0` a 3-s sleep of the main thread froze the emulation for
   3 034 886 µs with **the signature of `vbn113k`** (`GpuWaitSlow role=4`, `PriorityStall: … us=2975859`, the whole stall
   inside `Present`); at 1 the frames stayed 33 ms while the main thread slept the same 3 s.
4. **ABBA (seal 02 `ttl114`): NOT_ADMITTED** only by my unmeasured arming cap (arm-1 wall 21.4 µs > 20 µs) ⇒ KEEP; size
   −51.6 ± 75.4 µs reported. **Seal 02b `ttl114b` (cap 60 µs, chosen after seeing 02 — recorded as such): SHIP** — 96
   pairs, BDA NEW, walls 172.6 / 22.2 µs per call, **Δ`dt` −43.5 ± 73.2 µs** (not distinguishable from 0; a correctness
   fix, bar "not slower"), video `vtt114b` PASS; 6 of 7 sealed predictions HIT (P2's band was moved after 02).
5. **Default `titleasync=1`** (`175b873`), with two measurement-only tools for a boot check: `KYTY_PREPARE_HOLD_MS`
   (the preparation screen held by the main thread) and the `PresentOverlap` detector (its zone fixed before any run to
   end before `UpdateTitle`, where the startup park happens — item 11, `a74205e`). Pre-seal audit of the check (item 12):
   admission checks `adm_idle_*`, `adm_boot_parked`; NOT_ADMITTED with one repeat.
6. **Seal 03 (`go114d`): `vid114` PASS** (4 010 frames, 0 glitches, 3 726 scene rows, UpdateTitle 29.9 µs per call,
   `present_overlap` 0, no markers); **`boot114` died at `commandRecorder.cpp:326`** right after `PrepareHold` ⇒
   NOT_ADMITTED. Cause by the code: the presentation scheduler's record ring is single-producer and belongs to the first
   thread that records (the VideoOut present thread's startup blank present); the main thread's first preparation frame
   (`PrepareBlankFrame` → `BeginRecord`) trips the owner check. Hidden in warm runs (preparation ends before its first present); any long start (cold
   preparation, RenderDoc — the session-102 crash on the same line) hits it.
7. **Seal 03b (`bootctl114`): KEEP_1** — `boot114b` (default 1) and `boot114c` (`KYTY_TITLE_ASYNC=0`) died identically ⇒
   the crash does not depend on the knob. **C1 itself stays unverified** (the stress never reached its hold).
8. **Session audit (item 15): every number CONFIRMED; MAJOR P1** — item 13 set aside the sealed consequence of
   `pred/03` §3 after seeing `boot114` and did not say so; `boot114b` was in effect the sealed repeat and was not admitted
   again, so by the sealed rule the default is 0. **Honestly: the sealed consequence is kept — `titleasync` default 0,
   build `916f6489` installed**; 03b's KEEP_1 stays as evidence of knob independence, not as the decision. Re-ship in
   session 115 after the ring fix and a PASS of a new boot check (FAIL/NOT_ADMITTED ⇒ 0 without discussion).

## 2. Code

`36522d2` (knob, instruments, control), `9d7712c` (LF), `74e2ad7` (review fixes: gating, `FlipHold`, `MainTaskLate`),
`175b873` (default 1, `KYTY_PREPARE_HOLD_MS`, detector), `a74205e` (detector zone), `1713c6d` (default back to 0).
Builds: `78f290d4`, **`916f6489`** (seals 01–02b; installed at the close), `c6892df1` (never run, detector defect),
`8d7ba8f4` (seals 03–03b). Records and seals: `docs/ROADMAP.md` items 1–16, `docs/session-114/`. No push.

## 3. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `ctl114a`, `ctl114b` | 01 | `KYTY_MAIN_STALL_TEST=3000:3000`, knob 0 / 1 | **PASS** (freeze 3.03 s / none) |
| `ttl114` | 02 | ABBA `titleasync=0\|1`, 600 s | NOT_ADMITTED (cap 20 µs); −51.6 ± 75.4 |
| `ttl114b`, `vtt114b` | 02b | the same, cap 60 µs; video | **SHIP** (−43.5 ± 73.2); video PASS |
| `vid114` | 03 | video, build `8d7ba8f4`, defaults | **PASS** (4 010 frames, 0 glitches) |
| `boot114` | 03 | `KYTY_PREPARE_HOLD_MS=10000` | FATAL `commandRecorder.cpp:326` ⇒ NOT_ADMITTED |
| `boot114b`, `boot114c` | 03b | the same at knob 1 / 0 | both the same FATAL ⇒ **KEEP_1** |

## 4. Proved, and not proved

**Proved:** a busy SDL main thread freezes the emulation through the title wait under the flip mutex with the exact
signature of the session-113 stall, and `titleasync=1` breaks that chain; the knob costs nothing measurable (−43.5 ±
73.2 µs, NEW regime); the build `8d7ba8f4` with the default 1 recorded a clean video (OLD regime); the startup crash under
a long preparation exists and does not depend on the knob (and the session-102 logs had already shown it: fatal at
`KYTY_RECORD_THREAD=1`, a 19.8-s preparation completing at `=0`).
**Not proved:** what kept the main thread busy in `vbn113k`; C1 (no two threads in `Presenter::Present` at startup) —
reviewed by reading only; other blocking calls under `VideoOutConfig::mutex` (review F2); anything about 60 FPS.

## 5. Audits

Review of the knob (workflow, 15 agents, `review_titleasync.{txt,json}`): C1 MAJOR ⇒ gating. Pre-seal audit of
`check114` (1 agent): no BLOCKER; M1 (the counter is blind before the first flip), M2 (no evidence the stress engaged)
⇒ admission checks. **Session audit** (workflow, 4 auditors + 3 skeptics, `audit114/`, git
`docs/session-114/audit114/`): recounts CONFIRMED; protocol ordering and seal hashes hold; code of the knob clean; MAJOR
P1 (post-hoc override) ⇒ item 15 above; errata: `vid114` BDA regime OLD (not NEW); 6 of 7 sealed predictions (P2's band
moved after 02); the crash site is the main thread's `PrepareBlankFrame`; processes died ~7 s after launch; a one-core
`find` process ran through seals 01–02b (ABBA pairing cancels it to first order); parallel heavy work twice (before 01:10
and v3 acceptance beside the audit); a mutlib cache left in the repo (removed); seal 03b built in ~2 min without an
independent check.

## 6. Next

`docs/next-session-115.md`: (1) the presentation record ring ownership (preferred: no main-thread present in
`WindowPrepareShaders`), a new boot seal with controls before the fix (`KYTY_RECORD_THREAD=0` PASS path, defaults ⇒
`:326`), then re-ship `titleasync=1` with a video; (2) `mutlib` v3 (item 16); (3) review F2 debts; (4) the next speed
track by the rule.
