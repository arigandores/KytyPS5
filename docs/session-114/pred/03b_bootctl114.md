# Sealed pre-registration 03b — session 114: two control boots of the fatal `commandRecorder.cpp:326`

**Immutable once written.** Recorded in `docs/ROADMAP.md` §0.1 "СЕССИЯ 114 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 13 (`94dfa24`)
before this text. Seen before this text: seal 03 chain `go114d` — `vid114` passed every video check; `boot114`
(`KYTY_PREPARE_HOLD_MS=10000`, default `titleasync=1`) died with `--- Fatal Error ---` at `commandRecorder.cpp:326`
(`m_producer != self`) right after `PrepareHold`, before the first `ShaderPreparation: progress` line ⇒ `check114`
NOT_ADMITTED. The reading of the code: the presentation scheduler's record ring is single-producer and belongs to the
first thread that records into it (the VideoOut present thread, whose blank present runs at startup and then parks in
`UpdateTitle`); the main thread's first present in `WindowPrepareShaders` trips the owner check. Before the SDL main loop
`titleasync` 0 and 1 take the same waiting path (item 4), so the knob cannot change this.

## 1. Runs (chain `go114e.sh`; lock; machine idle CPU < 15 %, GPU < 10 %; build 8d7ba8f4 installed after its sha check)

- **`boot114b`** — `enter_scene.py boot114b --hold 60 --attempts 1 --no-install --gates-file gates_base.txt`,
  `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000` (= `boot114` again, default 1).
- **`boot114c`** — the same with `--gates-file gates_title0.txt` and `KYTY_TITLE_ASYNC=0` in the environment (the gate
  file is applied only from the guest's first flip, the environment sets the value from process start).

## 2. Rule (`bootctl114.py`, fixtures `test_bootctl114.py` 42, mutants `mut_bootctl114.py` 25 through mutlib v2 frozen copy)

Per tag the setup must hold (build, hold env, pin, no schedule, no checkpoints, the knob as above), else
**NOT_EVALUABLE** (fix the setup, run again under this seal). Outcome per tag **SAME_FATAL** iff exactly one
`PrepareHold: ms=10000` line, a line containing `commandRecorder.cpp:326` after it, and no `startup wait finished` line.
**Both SAME_FATAL ⇒ KEEP_1:** the fatal does not depend on the knob, `titleasync=1` stays (video `vid114` PASS), the boot
check of C1 is re-run after the fix of the ring ownership (session 115, first item). **Otherwise DEFAULT_0:** the default
goes back to 0 (build 916f6489 stays installed).

## 3. Predictions

P1 `boot114b` SAME_FATAL · P2 `boot114c` SAME_FATAL · P3 each dies within 60 s of process start.

## 4. Must not be claimed

That C1 (two threads presenting at once) is verified — it is not: the boot stress never reached its hold. That long
starts work — they crash at both knob values until the ring ownership is fixed.
