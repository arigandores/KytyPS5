# Final independent VERIFY 99: PASS

Verdict applies to the exact frozen sources below and the unchanged 10848-byte sealed
pre-registration. No outstanding reproducible blocker was found in the reviewed scope.
This is preparation/code verification, not admission of a game measurement or permission
to launch it. The original `REVIEW.md` and `HARNESS_REVIEW.md` remain unchanged and retain
the earlier CODE findings and counterexamples.

## Evidence

- **23/23 supplied scorer tests PASS**, actual unittest count in `final_scorer_tests.txt`.
- **20/20 independent final assertions PASS**, in `final_recheck.txt` and
  `final_recheck/assertions.json`. Both positive synthetic instruments pass protocol,
  every new core control, all four inherited kept controls, freshly computed criterion 3,
  and all ten selected reversibility controls. Their fixture endpoint is 19 ms over 165
  pairs. These are component fixtures, never real ADMITTED measurements.
- Negative independent assertions cover five individually missing early fields, early
  mid-block live leakage, contradictory metadata arms, six stdout-only forbidden markers,
  short whole-log duration, stale area CSV, changed calibration stdout hash, and invalid
  raw calibration area. The calibration replay assertion uses actual scorer dependencies,
  without mocked protocol/area/reversibility functions.
- **8/8 supplied harness AST tests PASS**. The five independent fatal-marker
  counterexamples that defeated v1 all stop before the counted process on v2.
  Both saved output streams are required and scanned using the shared helper.
- Additional production-root test: `--root C:/kyty/s98 --calibration` refuses with exit 2
  before opening run inputs or creating calibration artifacts. Output is in
  `production_root_refusal.txt`.
- Earlier independent raw recount reproduced historical F_a=14.274068801724138 ms
  (128 pairs), F_c=12.825411375615763 ms (122 pairs), and rv98a 432 + warmup 425 = 857
  falling edges. Old estimators were not changed by the fixes, so that heavy recount was
  not repeated. See `old_raw_recount.txt`.

## Review assertions

1. Previously missed live DARK structure and required field presence now cover the whole
   parsed log. Removing bf_mixed, bf_trig_fire, bf_dlskip, bf_live_mat or img_new from
   n1900 rejects the fixture; live leakage at unarmed block3 idx10 fails DARK_B.
2. Criterion 3 is regenerated from the exact current raw file into a temporary CSV;
   existing area CSVs are ignored. Calibration replay takes the same path. Doubling armed
   raw area produces INVALID despite a stale valid CSV.
3. Requested schedule, env, actual GateArm entries and metadata arms agree or refuse.
   New binary, baseline gates and sealed rule hashes remain pinned. Calibrations require
   hold180, one attempt, initial burn12000; measurements require hold300, warmup then
   attempt1. Core endpoint requires >=10 pairs; selected rv controls require >=30 falls.
4. Calibration replay verifies metadata/log/stdout source hashes, reruns controls and
   criterion 3, recomputes raw dt means and half-away-from-zero round_100, and requires the
   exact resulting budget in both measurement arms. Out-of-range values are not clamped.
5. Both streams use the same case-insensitive fatal/slow-wait matcher. Warmup failure,
   death, short hold, missing stream or forbidden marker stops before counted launch.
6. Endpoint still subtracts bf_burn_ns/1000 in mode2 and uses inherited T* trimming and
   paired-block estimator. Both instruments remain mandatory; no subtraction fallback,
   global CLOSE, development licence, or automatic M4/M5 advancement was introduced.
7. Mechanics-only cannot produce a real ADMITTED result. Canonical raw logs are read;
   new scorer paths do not use legacy --log override/copy-delete behavior. Calibration
   artifacts use exclusive creation; production artifacts are restricted to s99.
8. Original failure readouts remain reported. Calibration output is labelled calibration
   only and has no new B/architecture verdict; historical full output is separately archived.

## Limits

No game, launch harness main or build was run. The launch-loop tests execute only its AST
with attempt() mocked. No mode2 performance, calibration, video behavior or hazard-rate
claim follows from this PASS. The old 857-edge result remains evidence for its old binary
and mode, not a new mode2 proof. Video assessment remains a real-run task.

Raw-duration checking is deliberately a **necessary consistency check**: whole-log dt sum
must cover the metadata hold; duplicate main frame numbers, missing dt fields and negative
dt values are refused.
It does not independently prove an uninterrupted hold, since the whole log includes entry;
after-stable duration is printed only. Survival also relies on recorded hold_exit/hold_s,
absence of forbidden markers and the process's frame/reversibility controls. This report
does not upgrade that check into stronger evidence or invent an extra timing tolerance.

## Frozen SHA256

| File | SHA256 |
|---|---|
| bf99.py | 92cb8148415992e23b033af81b5104a1f23d33928a2f66ffb14aa94b2ea958fb |
| m3_99.py | 8a80e4cf90e04d56685dc5f3e794bf6354cf9377a61896f4fc3b27c400fe85b3 |
| test99_scorers.py | 18ae159c0680632e2babcb40abb8c69289416c1a5c290a64541bd7749e285a7c |
| accept99.sh | 589128026f3cf99568e09412c929fab295f650fe3877224c120f7b89fa4f8d77 |
| enter_scene.py | f4a142b8042ee7a13c59aa5fad4ef72ee80a1b7bf34fe7855a368c27e50ee7fd |
| run_safety99.py | 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 |
| test99_harness_stop.py | ac36b63c7d8c1f66a7a436deb5ea729466da5cbf0eaa963ceb46dac5a9b707b5 |
| pred/01_bindings_only.md | 8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d |

All verification-generated files were confined to `C:/kyty/s99/verify_scorer99`.
