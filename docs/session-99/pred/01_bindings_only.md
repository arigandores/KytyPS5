# Session 99 pre-registration 01 Ă˘â‚¬â€ť bindings-only M3 diagnostic

SEALED on 2026-09-19 after offline scorer checks on bf98a, bf98c and rv98a and 18 synthetic
mode-2 tests. No session-99 game process has been authorised or run. Once sealed,
this text is immutable; any correction needs a separate amendment before new data.

## 0. Scope and prior information

Budget: <= ~3.0 us/draw (median), <= ~2.3 us (p99, 7284 draws). Reference current path:
6.4 us/draw, 31.6 ms/frame, GPU busy 12.8 ms. M3 remains GAP; M4 and M5 follow in that order.
60 FPS is not promised. The user's current instruction permits all preparation but forbids
launching the game until a further signal. This document is a protocol, not launch permission.

The previous global M3 result is F_a=14.274 ms and F_c=12.825 ms; the user's constant
2.2535 gives 15.078..16.527 ms, GAP. The historical +2.65 must remain visible in the old
readout. Neither old rule nor its sealed texts is changed here.

Mode 2 preserves normal resource acquisition (AheadTake, SRT memo, successful
MaterializeResources), while flooring PrepareBindings/Rebind*/per-slot synchronization.
It also preserves real compute-clear shortcuts. Mode 3/clear=1 freezes a snapshot and
removes those shortcuts. The net contrast B_i-F_i therefore is NOT a pure materialization
timer, and its positive sign means returned work made the measured path more expensive.
The reverse sign printed as an example in next-session-99.md is corrected here.

## 1. Instrument and provenance

Required new binary SHA256:
ee9cc8ab1f5d25384dedb02a6a6abfca2aa7692585fcaddc74950721afc7a160
(23739904 bytes, build_local.cmd). It allows the existing measured burn in bfmode=2 as
well as 3; mode 0/1 and budget zero remain inert. No gate/default is changed.

Three new positive witnesses, only armed && bfmode==2:
bf_live_ahead after a successful AheadTake; bf_live_mat after successful materialization;
bf_live_memo before a successful SRT memo return. They do not count frozen reuse or failure.
All three are printed including zero. They add an unmeasured positive cost to mode 2.
The old 857-edge proof is historical evidence for mode3/clear1, not a proof of this new binary
or mode2/clear0. Every new process must prove its own survival/frame controls.

Required environment: KYTY_BIND_FLOOR_LATCH=1, KYTY_BIND_FLOOR_CLEAR=0,
KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, KYTY_GPU_CHECKPOINTS=0,
KYTY_GATE_SCHEDULE_ABBA=1, KYTY_FRAME_TRACE=lite. The 1092-byte/99-name gates_base.txt
remains sha256 00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8.
Nothing else runs on the measurement machine. One executor owns game, GPU, cache and log.

## 2. Two distinct instruments, calibration and stopping

Instrument a: base bindfloor=0 drawahead=1 bfmode=2; armed bindfloor=1 drawahead=1 bfmode=2.
Instrument c: base bindfloor=0 drawahead=1 bfmode=2; armed bindfloor=1 drawahead=0 bfmode=2.
Both schedule arms contain the same bfburn, period 30, start 1800, ABBA. These are two actual
resource-acquisition implementations; c is not removal of dead workers as it was in mode3.
Both are mandatory. No B_c=B_a-W_a fallback is permitted.

After explicit game permission, order: cal99a -> bf99a -> cal99c -> bf99c. A failure of any
required stage stops the sequence. No automatic retries, no replacement run to obtain PASS.
--attempts 1 is explicit, overriding the harness default of three. An entry hang is recorded
as an entry failure, not counted as a floor hang; it still stops this sequence.

Each calibration is one process, hold 180 seconds, no warmup-first, bfburn=12000. This is a
new deliberately provisional budget, not an inherited calibration. It is based on old full-floor
burn 16400 minus roughly 4 ms of returning resource acquisition; it is only a prediction.
Calibrations are not measurements of B and have no architecture verdict. Their admission keeps
all applicable controls except C9 (the equality being calibrated); criterion 3 must still be
VALID. Require at least 10 matched block pairs and >=30 completed falling edges in the full
log, and the expected 180-second hold. If calibration cannot meet these requirements, STOP.

For each instrument independently:
  b = 12000 + round_100(dt_U - dt_A)
where dt_U/dt_A are arithmetic per-row dt_us means in that calibration outside T* in the
measurement window, and round_100 is nearest 100 us, ties away from zero. Require
0 < b <= 30000; do not clamp. Store the source tag, raw means and b in the calibration artifact.
No third process is used to retune it if the later measurement fails C9.

Each bf99 measurement: hold 300, --warmup-first, --attempts 1. Both processes must survive
their entire holds and have no GPU hang/slow-wait/abort/fatal markers. Its counted process
must pass every measurement control including C9 <=0.03. Take video on bf99a (>=3000 frames)
and assess by the existing video workflow; the intentionally broken floor image is allowed,
but its behaviour and any recovery defect must be reported. Do not infer normal rendering
correctness from a floor video or from a successful build.

## 3. Endpoint, controls and refusal

Window: n>=2100 and blk>=1. E is every GateArm block whose predecessor has the other arm,
including predecessor block 0. T* removes the last row of the old block and idx0/idx1 of
the new block at each such boundary. Preserve the session-98 pairing algorithm. Drop both
members of a pair if either has no retained rows.

B_i = median over matched armed blocks of the block mean of
  (cpu_gpu_us - spin_gpu_us - bf_burn_ns/1000)/1000 ms.
Burn MUST be subtracted in mode2. F without trimming is reported only. No missing counter
may be silently interpreted as zero. Report matched pair count and edge-position histogram.

Keep session-98 C1''' (darkness/structure), C2' (population/skip/drop), C3' (emit), C5
(draw population), C6' (base BDA control), C7 (other instruments dark), C8'' (net floor cheaper),
C9'' (dt mismatch <=3%), C10''' (burn present/darkness/structure). Keep their numeric limits
and original FAIL lines. C4 of the frozen floor is printed only and replaced by C4_B:
  bf_mat=bf_reuse=0 on armed retained rows;
  all bf_live_ahead/mat/memo fields present, sum of live outcomes >0;
  c additionally bf_live_ahead=0 and bf_live_mat+bf_live_memo>0.
For both instruments the three live counters must satisfy the same unarmed transition
structure/darkness tolerance <=0.001 as bf_n. This is a positive path witness, not a claim
that there is one materialization per draw or a proof of counter timing overhead.

Require clear=0 and bf_clr_skip=bf_skip_drop=0. Keep C11-C20 from rv98: survival,
>=30 falling edges, single bf_edge in each allowed transition window and none elsewhere,
DARK98 structure, no skipped downloads, R6/R6'/R7/R7' recovery medians <=50, frame integrity
(bf_mixed=bf_defer_force=bf_trig_*=0). Apply the DARK structure also to the three live fields.
For counted/warmup hold survival require metadata as well as log evidence. Do not compare
clear=0 to the old clear=1 proof as an identity requirement. Lack of a mode2 hazard-rate proof
remains explicit; 30 edges cannot reproduce the power of 857 edges.

Refuse missing/inconsistent metadata, wrong binary/gates/pre-registration hash, wrong
protocol/schedule/environment, missing fields, missing internal schedule blocks/orphan blocks, missing or duplicate
edges, forbidden markers, any required control failure or non-VALID criterion 3. An unpaired endpoint block at the start/end of an ABBA record is allowed, reported and excluded
from the endpoint; it is not a missing internal block. Guesses about missing data do not produce a number. --mechanics-only on old logs/fixtures can never
produce ADMITTED. Calibrations expose controls and dt means but suppress floor/branch values.

## 4. Decision table Ă˘â‚¬â€ť intentionally limited before seeing B

Use B_a and B_c WITHOUT adding 2.2535. This does not assert that preserved materialization
already contains all the old 1.66+0.49; restoring missing real work needs a new operation-level
accounting. The zero addition is an explicitly optimistic CPU screen, not a rewrite budget.

| Prerequisite / value | New result | G | R1 |
|---|---|---|---|
| Either required measurement not admitted | NO VERDICT | alive/unlicensed | alive/unlicensed |
| Both admitted, min(B_a,B_c)>=15.5 ms | HIGH DIAGNOSTIC | unchanged GAP | unchanged GAP |
| Both admitted, max(B_a,B_c)<=11.0 ms | LOW DIAGNOSTIC: this optimistic CPU screen survives | unchanged GAP, no licence | unchanged GAP, no licence |
| Both admitted, otherwise | DIAGNOSTIC GAP | unchanged GAP | unchanged GAP |

HIGH identifies the measured residual as expensive even after removing bindings. It does not
close all designs preserving some materialization: no finite bound P on pessimistic work
added/retained by this instrument has been proved, including its new counter cost. The
required condition min(B_i-P_i)>=15.5 for a lower-bound exclusion is therefore NOT available.
The wider G removes materialization; R1 is not constrained to preserve its current algorithm.
No available outcome here produces global CLOSE, PROCEED-to-M5, or 60 FPS. M3 stays open.
After this diagnostic, another pre-registered decision is needed for the missing bound or
operation accounting. M4/M5 are not silently advanced.

Report B_a-F_a and B_c-F_c against the admitted session-98 numbers as descriptive contrasts
across binaries/clear modes only, with that provenance. They do not select any branch.

## 5. Predictions (not admission controls)

Q1: both mode2 measurements pass C4_B (code reachability); live_memo=0 with srtmemo=0.
Q2: B_a in [15,25] ms, B_c in [15,28] ms (old floor plus returned acquisition, deliberately broad).
Q3: HIGH DIAGNOSTIC is the modal outcome, but GAP remains plausible; LOW is unlikely.
Q4: calibrated measurements pass C9 <=0.03 (risk: real clear work, CPU competition and DRS).
Q5: all reported floor-clear skips are zero; positive xover remains possible and is reported.
Q6: no hangs; this is a prediction, not inherited reversibility evidence.

## 6. Offline validation and sealing record

Before sealing: offline99/synthetic_tests.txt records 18 tests PASS; offline99/legacy_bf98a.txt
reproduces 14.274 ms, 10/10, criterion3 VALID; legacy_bf98c.txt reproduces 12.825 ms,
10/10, VALID; legacy_rv98a.txt reproduces 11/11 and 857 completed falling edges. Legacy
original FAIL lines remain in those readouts. They are historical dry runs, not new mode2
admission. The parent independently recounted raw logs in recount99.py/recount99.json.
Fresh C++ and port reviews passed. Fresh scorer VERIFY receives this SEALED text and raw
inputs next; it must pass before any launch. A code defect returns to CODE. A defect in this
rule requires a separate sealed amendment, never editing this file.
