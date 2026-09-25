# Session 115 — correctness first: the presentation record ring (the startup crash at `commandRecorder.cpp:326`), then the boot check and the re-ship of `titleasync=1`, then `mutlib` v3 and the next speed track

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 114 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 9–16 (item 13: the crash; item 15: the
session audit, the rollback to `titleasync=0` and the fix design; item 16: `mutlib` v3) and §7; `C:/kyty/s114/FACTS.md`
(git `docs/local-session-114.md`); `C:/kyty/s114/audit114/` (git `docs/session-114/audit114/journal_results.json`,
findings DESIGN-115, C-1, C-3).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1 bdanarrow=0 titleasync=0`, installed build `916f6489…` (`74e2ad7`). Session 114: the 3-s
stall of `vbn113k` reproduced by a busy SDL main thread (the window title waited for it under the flip mutex, the same
`GpuWaitSlow`/`PriorityStall` signature); the knob `titleasync=1` breaks the chain at no measurable cost (Δ`dt` −43.5 ±
73.2 µs, NEW) but stays 0 by the sealed boot-check rule; the boot check found a knob-independent startup crash. 60 FPS
stays the direction without a route with a live estimate.

## Rule of the session

As every session since 102: decisions recorded in `ROADMAP.md` before the first action; **a sealed consequence is never
set aside after its outcome** (item 15, P1) — a rule may change only for a run not yet seen; a seal per run with
fixtures and mutants (`mutlib` — v2 frozen copy until v3 is accepted, always `--work-dir C:/kyty/s115/work*`); nothing
else heavy on the machine during a sealed chain, **and never two heavy jobs (mutlib, workflows) at once**; before each
chain CPU < 15 %, GPU < 10 % and **no single foreign process above ~0.5 CPU·s/s** (item 15 (д)); audit before closing.

## Steps

0. **Harness root `C:/kyty/s115`**: copy `enter_scene.py`, `gates_base.txt`, `run_safety99.py`, the pinned exe
   `kyty_emulator_916f6489.exe`; check `C:/kyty/SEALED_RUN.lock` is absent; add the per-process load gate to the chain
   preamble (two `cpu_s` samples ~10 s apart from the process list).
1. **The ring (correctness first).** Who records into the presentation scheduler: the VideoOut present thread
   (`videoOut.cpp:831/843/854/872/1182` → `Presenter::Present`, `PrepareBlankFrame(nullptr)`) and the main thread only in
   `WindowPrepareShaders` (`window.cpp:996-998`); `CommandRecorder::BeginRecord` gives the ring to the first recorder and
   `EXIT`s on another thread (`commandRecorder.cpp:320-326`). **Preferred fix (audit DESIGN-115):** no main-thread present
   in `WindowPrepareShaders` (keep the overlay flag and SDL event pumping — the present thread already presents the
   preparation overlay, `videoOut.cpp:840-857`); before the main loop runs `UpdateTitle` must not park the present
   thread (post or skip), else the overlay never refreshes; the progress counters atomic (C-10); a measurement-only
   switch restoring the old main-thread present as the positive control (expected: the `:326` fatal). Fallback (C-1):
   producer handover inside the render-lock scopes with an atomic `m_producer`, plus a present mutex taken after
   `FramePool::Acquire`, released before `UpdateTitle`, order `cfg->mutex` → present → render. Record the choice first.
2. **The boot seal (new):** controls BEFORE the fix on `916f6489`/the pre-fix build — a boot with
   `KYTY_RECORD_THREAD=0` (expected to finish a ≥ 10-s hold: validates the admission path; session-102 log
   `log_m5cap102b.txt` did so in 19.8 s) and a boot at defaults (expected `:326`: the stress engages); AFTER the fix — the
   boot at defaults must finish the hold with no fatal, no `PresentOverlap`, and the overlay presents counted from the
   present thread during the hold. State in the seal that it tests the ring fix, not `titleasync`.
3. **Re-ship `titleasync=1`** only on PASS of step 2 (seal 02b's size stands): the default flip in the same build as
   the fix, a video with a check script (report the BDA regime of every level), FAIL/NOT_ADMITTED ⇒ 0 without discussion.
4. **`mutlib` v3** — per item 16 (acceptance outcome and review).
5. **Review F2 debts** (other blocking calls under `VideoOutConfig::mutex`: `Present` itself, `Gates::Poll`, logging)
   — measure `flip_hold_*` phases first; fixes (b) "don't hold the mutex through `Present`" and (c) "submit before
   `PrepareVideoOutFlip` when priority operations wait" only with their own seals.
6. **The next speed track** by the rule (candidates: the queue-to-run latency of priority operations; the remaining
   `PipelineCache::m_mutex` contention; ROADMAP §1 phases).

## Must not be claimed

60 FPS; that C1 is verified before step 2 passes; that `titleasync=1` is shipped before step 3; that the startup crash
is limited to measurement runs (any long preparation hits it until step 1).
