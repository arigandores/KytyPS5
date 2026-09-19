# bf99e work failure: independent raw causal readout

Offline diagnostic only. bf99e remains NOT_MEASUREMENT; no B is computed or published.
Source sealed pred02 and pred04 unchanged. New artifacts confined to work99_raw.

## 1. Reproduction and balanced time trend

Own parser merges only FrameTrace/main, draw and x numeric fields by n; retains raw main line
numbers and cumulative dt. Reads deciding row_ranges from frozen score for block membership.
Recomputed draws U5078.87421630094/A5042.781739811912, work -0.7106393061%, exactly frozen score.
The same 176 complete blocks, 88 U/88 A, 29 rows/block, 2552 rows/arm are used below unless
an explicitly exploratory window is named. Existing score bf99e_score.json:69 retains FAIL; metrics are at lines78-80.

Four disjoint BALANCED groups of 11 original quartets (44 blocks each) give work:
blocks4..47 -1.419856%;48..91 -0.533407%;92..135 -0.600790%;136..179 -0.285248%.
The first11 quartet differences are all negative. All44 quartet A-U differences have mean
-36.092476 draws, SD68.070852, 30 negative; these are descriptive, not admission statistics.
First300 seconds AFTER GateArm0, restricted to sealed rows: -1.3541583% (899 rows/arm).
After300 seconds: -0.3579091% (1653 rows/arm). Wall-quarter cuts in diagnostic JSON have unequal
arms at cut boundaries; use balanced quartet groups above for trend evidence.
Pilot eng99a4 same selector: -0.0236502%,638 rows/arm; all11 quartet mean difference -1.191223.

## 2. Monotonic washout and fixed n-modulo resonance do not explain it

First block after arm CHANGE (b%4=1,3): -0.5311096%; second SAME-arm block (b%4=0,2):
-0.8891048%,1276 rows/arm in each. A simple remaining decaying transient is not established.
Sealed U/A n residue frequencies are EXACTLY equal for mod2,3,4,5,6. For mod3 both have
[9,10,10]/29. Thus a COMMON signal depending only on n modk cannot produce contrast through
unequal phase counts. Arm-dependent phase shifts remain possible; no proof of them exists.
Lag3 draw autocorrelation in sealed U/A is +0.043186/+0.000969; strongest short lag is
U lag2 -0.306542, A lag1 -0.315113. This does not support a stable 3-row repetition.
Nearby fixed-length exploratory windows do not remove deficit:60..89(30) -0.7024663%;
60..86(27) -0.6289979%;61..87(27) -0.5485099%;59..88(30) -0.8169324%.
Other phase windows vary:30..59 +0.6361462%;30..88 -0.0300824%;15..88 +0.0435583%.
Whole0..89 -1.4954417% includes known transition imbalance (pilot whole -1.5401113%).
These are mechanism probes, never replacement deciding populations or a washout recommendation.

## 3. Work counts track GC invocation count, requiring real guest accounting

bf_igc_checks counts TextureCache GC invocations per pred04:39 and48; it is NOT guest frames.
Sealed U8.0489811912/A7.9913793103 calls/row, difference -0.7156418870%, while draw difference
is -0.7106393061%. Draws per GC call U630.9959106/A631.0277042 differ only +0.0050386395%.
On ALL0..89 rows of the same blocks, checks U8.05997475/A7.94002525; draws/call
U630.8908592/A630.8445575 (approximately -0.00734%). On30..88 checks means are IDENTICAL
7.99807395994 in both arms; draws/call U630.9619515/A630.7721428.
Thus the raw whole-block work mismatch persists but almost vanishes per this PROCESS-CALL
proxy on whole and sealed populations. This is evidence for changed sampled accounting mix,
not proof of equal work per guest frame. GC calls cannot become an admission denominator.
fbp_n is ProcessFaultBuffer calls; NEVER guest-frame count; armed values zero by floor design.

## 4. Confirmation has burst/catch-up rows absent in pilot

For n>=2100, bf99e has52 U rows draws<10 and0 A; pilot has0 in either arm.
First300 seconds after GateArm0 already contains19 such U rows in bf99e versus0 pilot.
Sealed draw SD U1207.092/A433.973; pilot U718.249/A414.576. U variability grew substantially.
Example raw log_bf99e.txt:619099 n3681 draws7830 dt137529;:619107 n3682 draws1 dt2076;
:619196 n3683 draws740 dt14351;:619317 n3684 draws8571 dt79253; all U block20.
This is direct asynchronous burst/catch-up evidence, not identification of the responsible clock.
Recording differs between processes, but duration/process/thermal state also differ. rec_n,
cpu_record_us,rec_work_us all sum to0 even in bf99e, so these counters cannot measure its cost.
Recording causation is not proven by this comparison.

## 5. Next independent test, bounded proposal

Seal A/A runs with recording OFF and ON, otherwise identical schedule labels, binary and
300-second duration, with exact order/tags fixed before data, no arm effect/B interpretation.
Apply existing sealed selector for presentation-count diagnosis, not admission, and retain all
results. This tests whether pseudo-label asymmetry and burst/catch-up occur without floor,
and whether recording changes them. Process order remains a limitation with one pair.
Before NEW confirmation, add counters at an actual guest flip/submission identity boundary
and accumulate draws on that same identity, retaining existing presentation counters. Check
both cumulative conservation and boundary tail/head contributions. Direct guest identity is
needed because GC/fault calls cannot prove guest-frame equivalence. Source analysis should
locate this boundary; do not choose longer/shifted washout merely because current data pass it.

## Reproduction artifacts

parse.py extracts inputs; analyze.py generates bf99e_diagnostic.json/eng99a4_diagnostic.json.
more.py/more_output.txt: balanced temporal groups, modulo outcomes, tails, recording fields.
phase.py/phase_output.txt: exact phase populations, quartet distribution, raw examples.
proxy.py/proxy_output.txt: GC-call means, draws/call, correlations. No endpoint fields parsed.

