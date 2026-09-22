# C:/kyty/s102 — session-102 harness

**Read `FACTS.md` first** (and its §9). It is the single source of truth; this file is only a map.

## Result in four lines

**M5 was measured:** today's emitter's BDA path costs **+42 %** (X) and **+33 %** at equal load
granularity (Y) on **eight** of the ten top Sky Garden shaders (S1, S8 fail V-e), and the const-bank →
global-load step alone **+2.1 %** (L, all ten). **It does NOT close G** (`pred/08`, tally corrected by
`pred/09`): the tiered rule of `pred/02` was not recorded in ROADMAP first, and V2 carries unpriced
machinery (a pixel-shader fault store that likely disables early depth testing, doubled page-table
reads). G stays alive and unlicensed; the decision is the user's.
**`KYTY_GPU_CHECKPOINTS=0` no longer turns checkpoints on** (accepted 6/6 on the entry retry
`ckpt102_entry1`, under `pred/06` written after the hang). **`dabatch` is CLOSED** (b̂ = 0.078 µs a call;
the saving at 1024 is PREDICTED at 9.5 µs a flip against 60 — extrapolated, not measured).

## Disclosures (see FACTS §9)

P2 MISS (X − 1 = 0.420 outside [0.02, 0.20]); Q3 MISS (Δ`da_late` −0.24 a flip, t −4.3); two technical
retries (an entry hang; a start-up crash under `--rd`), the entry clause `pred/06` written after the hang;
the code was built and both candidate runs taken BEFORE the M5 capture; 15 shader-tree presence sites
deferred, so the class is not fully fixed; per-event GPU durations are not additive (whole-frame
X ≈ 1.387, L ≈ 1.010, V2s/A ≈ 1.028); V2 reads wrong bytes on S1 (4 153 261 B, null-page fault bit) and
S8 (746 B), and V-e checks only each item's last event; the capture retry ran with the record thread ON;
the `thread_local` change to the default M1 walk was never compared with the old code.

## Sealed, immutable (`SEALS102.txt`)

`pred/01_m5_bench.md` · `02_m5_addendum.md` · `03_dabatch.md` · `04_checkpoints_fix.md` ·
`05_dabatch_addendum.md` · `06_ckpt_entry_addendum.md` · `07_m5_capture_retry.md` ·
`08_audit_addendum.md` · `09_audit_tally_addendum.md`. `prev101/pred/` holds 20 texts of sessions 96–101;
session 100's `03_audit_addendum.md` stays in `prev100/pred/` (basename collision). **Do not edit any.**

## Tools

* M5: `M5_RUNBOOK.md`; `m5_recompile.py` (arms A/V1/V2/V2s → `m5/recompile.json`, `m5/spv/`),
  `m5_sass_full.py` (`m5/regs.json`), `m5_layout_check.py`, `rd_m5_find.py`, `m5_plan.py`,
  `rd_m5_equal.py`, `rd_m5_bench.py`, `m5_run.py`, scorer `m5_102.py` + `test_m5_102.py` (132).
  Real run in `m5/real/`; old-capture mechanics in `m5/mechanics*/` (MECHANICS ONLY).
* Candidates: `ckpt102.py` + `test_ckpt102.py` (55), `dab102.py` + `test_dab102.py` (164),
  `accept102.sh ckpt TAG | dab TAG pilot|decision` (carries `R=C:/kyty/s102`).
* Audit: `audit102/` (seven lens reports, the code-review record, the parent's `l8_check.py`).
* `enter_scene.py` gained `--emu-arg=<arg>` (write `--emu-arg=--rd`).
* `check_gate_order.py` knows `('DrawAheadBatch', 'dabatch')`. **Mandatory after any gate/knob patch.**
* The port that built this root is `C:/kyty/s101/s102_port.py`; write `s103_port.py` fresh in **this**
  folder (see `docs/next-session-103.md` §2). `gates.cpp` now yields **135** entries (111 + 24);
  `ABSENT` grows 35 → **36** (`dabatch`).
* `accept101.sh`, `accept100.sh`, `accept99.sh` carry their own roots — do not run them.

## Runs

| tag | outcome |
|---|---|
| `ckpt102` | ENTRY hang with the signature of the historical BVH entry hang (markers off, op not named) |
| `ckpt102_entry1` | checkpoint fix ACCEPTED, 6/6 (retry under `pred/06`) |
| `dab102a` | pilot ADMITTED, candidate CLOSED |
| `m5cap102` | start-up crash `commandRecorder.cpp:326` under `--rd` |
| `m5cap102b` | M5 capture, `_RenderDoc/kyty_1790110985179586_capture.rdc` |

## Do not

* Do not quote "M5 = CLOSE" or "G closed": the scorer's `CLOSE-machinery` is withdrawn as a licence.
* Do not read X as G's intrinsic price, or as a ten-item figure (it is eight).
* Do not say the capture retry ran without the record thread: `gates_base.txt` pins `recordthread=1`.
* Do not treat the checkpoint fix as a speedup or as an ABBA A/B: it is a categorical inter-run witness.
* Do not rebuild before re-running any acceptance: IDENTITY hashes the installed exe.
