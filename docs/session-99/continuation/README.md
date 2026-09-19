# Session 99 — bindings-only pair measured; limited HIGH diagnostic

Current source of truth: FACTS.md (mirrored in repo docs/local-session-99.md).
Both new no-record confirmations passed: bf99g(a)30.049869ms and bf99h(c)37.367904ms,
each900.3s,88 pairs and45 falling edges. Global M3 remains GAP, G/R1 unlicensed;
M4/M5 follow the user's existing order. No FPS improvement or60FPS is claimed.

The user's bf99e glitch report was checked separately: normal recorded vis99base900.3s,
17802 decoded frames,0 detector events; bf99e18037/185. The user saw no glitches in control.
Exact cause of the experimental-floor effects remains open; see VISUAL99.md.

Installed binary34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f,
23743488 bytes. Final entry point settled99_norec.py under immutable pred05. Pred01..05
and all old failures remain unchanged. No more game runs are queued for this session.

Run provenance and independently verified results: settled_runs/, verify99_confirm_raw/,
verify99_c_raw/, verify99_visual_raw/; root raw checks: parent_recount99.py.
All instructions below are HISTORICAL, superseded by current FACTS and the sealed addenda.
Next broader-M3 plan: C:/kyty/KytyPS5/docs/next-session-100.md.

## Archived preparation instructions (superseded)

# Session 99 — STOPPED at cal99a (NOT ADMITTED)

The user authorised execution; exactly one cal99a process survived180.1s but failed
work-population admission (-4.0974%) and transition count (17<30). No accepted burn exists.
bf99a/cal99c/bf99c must not follow under this seal. No retries or new game launches are queued.
Installed binary is now ee9cc8ab...; the old9aa93e73... exe is backed up in this directory.

Current result: FACTS.md and verify_cal99a/VERIFY.md. Next PLAN: docs/next-session-100.md
in C:/kyty/KytyPS5. The commands below are the ARCHIVED pre-run plan, not instructions
to restart the stopped sequence or overwrite cal99a. The immutable seal remains unchanged.

## Archived preparation instructions (before the user's launch permission)

# Session 99 — preparation, game launches forbidden pending user's signal

Budget <=3.0 us/draw (p99 <=2.3); reference path 6.4 us/draw, 31.6 ms/frame,
GPU busy 12.8 ms. M3 remains GAP, M4/M5 follow. No 60 FPS promise.

This session is unfinished until authorised calibration/measurement/video runs. The newly
built binary is `kyty_emulator_s99.exe`, SHA256
`ee9cc8ab1f5d25384dedb02a6a6abfca2aa7692585fcaddc74950721afc7a160`, 23739904 bytes.
The executable installed in the game directory is still the session-98 `9aa93e73...`.
Copying the prepared binary into the game directory is a remaining preflight step after
the user's signal and before the first authorised run; do not rebuild just for a commit label.

The new rule is sealed at `pred/01_bindings_only.md` (10848 bytes), SHA256
`8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d`.
The root draft is archival and is not the protocol. No command here
has been run. The definitive state is `FACTS.md`; port reports and parent
raw recount are already available as `port99_diagnostics.txt`, `port99_ledger.json`,
`recount99.py`, `recount99.json`.

After approval, one executor alone owns every emulator launch and the shared GPU/log/cache.
No background scorer/review/build runs during measurement. All KYTY_* settings go as
positional arguments to enter_scene.py. Use `--attempts 1`, not its default of three.
Any failure stops the sequence. A calibration is a distinct preregistered step, not a retry.

Proposed first command, ONLY after the rule is sealed, verification is complete, correct
binary installed, nvidia-smi preflight checked and the user permits game launch:

```powershell
python C:/kyty/s99/enter_scene.py cal99a --gates-file C:/kyty/s99/gates_base.txt --hold 180 --attempts 1 --pred C:/kyty/s99/pred/01_bindings_only.md "KYTY_GATE_SCHEDULE=30+1800:bindfloor=0 drawahead=1 bfmode=2 bfburn=12000|bindfloor=1 drawahead=1 bfmode=2 bfburn=12000" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_BIND_FLOOR_LATCH=1 KYTY_BIND_FLOOR_CLEAR=0 KYTY_GPU_MARKERS=0 KYTY_GPU_CHECKPOINTS=0
```

Then `python C:/kyty/s99/bf99.py cal99a --instrument a --calibration` computes a candidate burn from that
calibration, without a B endpoint/route decision. The next measurement command must use
that exact candidate. Sequence: cal99a -> bf99a -> cal99c -> bf99c; the second instrument
uses drawahead=0 only in its armed arm. Each bf99 run has hold 300, --warmup-first and
--attempts 1; bf99a also records >=3000 video frames. No repetitions after FAIL.

`m3_99.py` requires both admitted B measurements. It prints HIGH/LOW/GAP diagnostics;
no outcome closes G/R1 globally or licenses a rewrite. The old +2.2535 rule stays intact
for the old full floor; it is not automatically added to this different screen.

Scoring commands (after the corresponding authorised run exists):

```powershell
python C:/kyty/s99/bf99.py cal99a --instrument a --calibration
python C:/kyty/s99/bf99.py bf99a --instrument a
python C:/kyty/s99/bf99.py cal99c --instrument c --calibration
python C:/kyty/s99/bf99.py bf99c --instrument c
python C:/kyty/s99/m3_99.py --a bf99a --c bf99c
```
