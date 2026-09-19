# Session 99 — route E, M3 continues: the gap branch (`bfmode=2`)

**EXECUTED AFTER PERMISSION; STOPPED AT cal99a (NOT ADMITTED).**
The single180.1s calibration failed work comparability (-4.0974%) and falling-edge count
(17<30). Fresh raw VERIFY confirmed it. No accepted burn or B exists; no later run followed.
Installed binary: ee9cc8ab..., unchanged seal8b816528.... Do not repeat this sequence.
Current facts: docs/local-session-99.md. Next PLAN: docs/next-session-100.md.

The remainder is the original pre-preparation brief; its old burn/proof/scorer assumptions
are superseded only as explicitly recorded in the new sealed rule.

**Order M3 → M4 → M5 stays** (the user's decision, session 97). Read `C:/kyty/s98/FACTS.md` in full
first (in git `docs/local-session-98.md`), then `ROADMAP.md` §0.1 (the session-98 addendum) and §2 E
(M3, the session-98 addendum), `C:/kyty/s98/README.md`, and the sealed `C:/kyty/s98/pred/01_hang_trigger.md`,
`01b_entry_hang.md`, `02_m3_frame.md`, plus session 96's `prev97/pred/02_bindfloor.md` §3.

**Open the report with the three numbers:** budget ≤ ~3.0 µs a draw (median) / ≤ ~2.3 µs (p99,
7 284 draws); today 6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms; undone M3 (GAP, continuing),
M4, M5. **Do not promise 60 FPS** (~15 %).

## 0. Where M3 stands

* **`F_a` = 14.274 ms, `F_c` = 12.825 ms** (both admitted, frame-latched floor, `KYTY_BIND_FLOOR_CLEAR=1`),
  constant **2.2535** (the user's submission choice) ⇒ **15.078…16.527 ⇒ GAP**. CLOSE missed by 0.42 ms.
* The floor is **proven reversible** (`rv98a`, 857 falling edges, 0 hangs); the instrument is binary
  `9aa93e73…`, commit `d7828b1`; env `KYTY_BIND_FLOOR_LATCH=1 KYTY_BIND_FLOOR_CLEAR=1`.
* **Session 96's §3 only SCHEDULES the bindings-only arm (`bfmode=2`); it never says what that arm
  decides.** That is this session's first job, sealed BEFORE any `bfmode=2` run.

## 1. First: write and seal the rule of the `bfmode=2` arm

Read what `bfmode=2` does in the code (`descriptors.cpp`, `pipelineCache.cpp:3126` —
`bind_floor = armed && mode != 2`: resources ARE materialised, only `PrepareBindings`/`Rebind*`/the
per-slot syncs are floored; `C:/kyty/s95/rewrite94/gpu-driven.md:141` "in between ⇒ split with a B =
bindings-only run"). Then decide, in a new sealed pre-registration, BEFORE any number:

* what quantity the arm yields (e.g. `F_B''` = the floor with materialisation kept; `F_B'' − F_a` =
  descriptive net returned-work contrast (not a pure materialisation timer)), with the same T*-trim, controls and burn rules as
  `pred/02_m3_frame.md` (the burn is calibrated anew — `bfmode=2` moves the floor's work);
* **which branch of G/R1 each outcome closes or keeps open** — write it as a table, like session 96's §3;
* `KYTY_BIND_FLOOR_CLEAR=0` in the `bfmode=2` arm (pred/01 §4: at `bfmode=2` the snapshot is not
  frozen, so its clears are real work); `bf98.py` already refuses clear=1 with bfmode=2;
* whether the verdict must still hold on BOTH instruments (walk and workers in / out).

Dry-run the scorer on `bf98a`/`bf98c`/`rv98a` BEFORE sealing (session 97 trap: a sealed control can be
unsatisfiable for the instrument it scores).

## 2. Then the run(s)

`bf99a` with `bfmode=2` in the floor arm (period 30, ABBA, pin, `--warmup-first`, hold 300, markers
OFF, latch 1). Nothing else may run on the machine during a measurement (session 98: review agents'
dry runs failed guards check 6 of `rv98a`).

## 3. Side items, not route E (ask the user whether to take any)

* **The ENTRY hang is now named: a BVH traversal (`cs=0x380bb9d636390bae`)** — 13 programs with no
  step bound, the game's invalid-TLAS `S_TRAP` translated as a no-op; historically 6.67 % of entries.
  A correctness fix for every user of the emulator: `C:/kyty/s98/design98/loops.md` has the design
  (`KYTY_BVH_LOOP_CAP`, in the translation-cache signature, separate cache directory, a trip counter in
  the fault-buffer tail read every flip). The OIT resolve `657ad04626bf9d55` and the hash probes
  `81f39ef20546ebae` / `e4c97c75ce70efc3` can be capped the same way.
* **A counter of the compute clear shortcuts actually taken** in the base arm — tightens the L3 bound
  (1.58 ms today). Needs a new binary, so it cannot serve the session-98 numbers retroactively.
* **The cross-queue tear**: one ACB submission (`queue=39`, 14 ops, `seq = s_flip + 1`) runs under the
  old value at every edge; knowing the flip-bearing DCB at ENQUEUE (a PM4 scan) would remove it.

## 4. Traps of session 98 that turned out to be real

1. **After a GPU execution hang the GPU keeps executing ~60 s until the TDR whatever
   `KYTY_GPU_HANG_ABORT_S` says**; the desktop freezes and the dead process keeps its handles
   (`_kyty.txt`). `enter_scene.py` now waits up to 180 s before rotating the log.
2. **`KYTY_GPU_MARKERS=2` names a hung op without device loss** (`GpuMarkerHung … culprit=op|gap`); it
   is the first tool for any hang, not `KYTY_GPU_CHECKPOINTS=1` (which changes the run).
3. **The frame latch moves the edge into index 0 of the new block** (~0.7–0.9 of a frame of the other
   arm): every endpoint must trim T* = {last row of the old block, idx0, idx1 of the new}.
4. **The floor snapshot is the FIRST materialisation of the process**, not the last.
5. **A scorer's counter row for the flip a process dies in is never written** (`trig98.py` T3).
6. **Review agents must not run scorers on large logs while a measurement runs.**
7. Carried: `KYTY_*` go POSITIONALLY to `enter_scene.py`; check `nvidia-smi` before a run; never
   rebuild between acceptance and the final answer (the installed exe is `9aa93e73…`).

## 5. The port

`C:/kyty/s98/s99_port.py`, written fresh in the SOURCE folder, modelled on `C:/kyty/s97/s98_port.py`
(five root constructs, the ledger, diagnostics); `gates_base.txt` byte-identical (1 092 B, 99 names,
`00c116dc…0594d8`); the ten sealed preds of sessions 96–98 into `prev98/pred/` byte-exact; `pred/`
empty; `accept99.sh` written new; the scorers pinned by path (`trig98.py`, `rv98.py`, `bf98.py`,
`m3_98.py`, and the carried ones) pointed at `prev98/pred/`.
