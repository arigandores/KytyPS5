# cal99a: offline mechanism analysis for a new session-100 protocol

Only existing raw inputs were read. New analysis code/output is confined to this directory.
This is exploratory diagnosis, NOT a re-admission, burn calibration, B estimate, or new M3 verdict.
The sealed cal99a refusal remains: work -4.0974201604%, C5 FAIL, criterion 3 INVALID,
17 completed falls <30. See ../verify_cal99a/VERIFY.md:8 and ../pred/01_bindings_only.md:53.

## 1. What the entire raw record confirms

Independent parser merges all 3812 FrameTrace/main/draw/x records (n=2..3813), attaches raw
main-line references, reconstructs the actual GateArm block transitions, and applies T* exactly.
Code: analyze.py; complete per-record extract: rows.csv; all aggregates: analysis.json.
The decision window n>=2100 begins log_cal99a.txt:468323 and ends :633783.

| Population | U draws/row | A draws/row | A/U - 1 |
|---|---:|---:|---:|
| Required untrimmed window (843/871 rows) | 5052.851720 | 4845.815155 | -4.097420% |
| T*-retained (799/828 rows) | 5020.246558 | 4836.275362 | -3.664585% |
| T*-removed (44/43 rows) | 5644.931818 | 5029.511628 | -10.902172% |

T* removes 87/1714 rows in the window (5.076%). Removing those rows does NOT remove
the workload discrepancy. Nor is it explained by the two endpoint fragments: 28 complete
opposite-arm pairs, blocks10/11 through64/65, ALL have negative draw differences,
-1.765241%..-8.589142%, median -3.832399%. Thirteen complete UAAU cycles, blocks12..63,
ALL are negative, -3.124359%..-6.386578%, median -4.025082%.
The four consecutive record-count quarters give -4.028651%, -4.343420%, -3.977491%,
-4.383676%. This is a repeating arm-related effect, not merely global elapsed-time drift.

## 2. Most of the deficit is located AFTER the existing T* exclusion

There are 14 complete rising transitions in the decision window. At each rise, every one
of idx2/3/4/5 has draws<4000: 56/56 rows. Means by idx2..5 are 2864.6, 3081.1, 3139.8,
3611.4 draws, with dt 26.167, 27.279, 30.034, 32.193 ms. All four positions are RETAINED
by the old last-old/idx0/idx1 T* rule. On falling transitions, idx1 averages 7335.3 draws
and 68.239 ms (15 occurrences including the last partial block); these are removed by T*.

Concrete first complete rise: block13, n2191/idx0, log_cal99a.txt:477140.
n2193/idx2 (:477250) has1786 draws/16.808ms; n2194 (:477330)3760/33.498ms;
n2195 (:477435)3470/33.464ms; n2196 (:477525)3567/33.262ms.
The next fall, block15 n2251 (:482841), is followed by n2252 (:482932):7198/66.415ms.

For the same thirteen complete cycles (equal U/A sample counts at each phase), arm age is
idx0..29 on the switching block, idx30..59 on the next same-arm block:

| Arm age | Rows per arm | U draws/row | A draws/row | Difference |
|---|---:|---:|---:|---:|
| 0..1 |26|5865.35|5045.96|-13.9699%|
| 2..5 |52|5450.94|3220.98|-40.9097%|
| 6..14 |117|5249.90|4943.46|-5.8370%|
| 15..29 |195|4927.88|4936.53|+0.1755%|
| 30..59 |390|4938.18|4947.27|+0.1841%|

This locates a transient lasting beyond idx1 and makes a globally persistent 4% loss an
incomplete description. It does NOT license selecting age>=15 after seeing these data.
Even age6..59 still differs -0.874619% in the same complete cycles, beyond the old 0.5% limit.
The late-phase observation is diagnostic support for a future settling experiment only.

## 3. The row mixture changes strongly; raw alone cannot label every row a guest-frame fragment

In retained rows, draws<4000 occur in U94/799=11.765% versus A281/828=33.937%.
draws>6000 occur in U50/799=6.258% versus A3/828=0.362%. Yet the retained MEDIAN
increases: U5226, A5461. Thus the negative mean is not a uniform scaling of draw counts.
Untrimmed vblank-like duration classes show the same change:

| dt class | U count | A count | U mean draws | A mean draws |
|---|---:|---:|---:|---:|
| <25ms |0|16|n/a|1815.8|
| 25..42ms |15|351|2980.7|3892.5|
| 42..58ms |778|500|4955.7|5594.7|
| >=58ms |50|4|7185.6|7006.0|

Short rows (<42ms) therefore comprise U15/843=1.779%, A367/871=42.135%.
These are explicitly duration classes, NOT proven incomplete guest frames. Raw counters lack
an independent guest-frame-completeness witness in this analysis. Source-level counter/reset
semantics must establish whether presentation cuts a guest frame; otherwise report short rows.
Pearson corr(draws,dt) U0.609786/A0.967812; corr(draws,cpu_gpu_us) U0.962565/A0.986776.
Area-per-attachment equality does not imply equal quantities of work: attachment count is
U12336.27/A11776.36 and dispatches U272.954/A263.263 in the untrimmed window.

## 4. Duration and host samples

Stable n278 is at cumulative raw8.815422s (log_cal99a.txt:248817); schedule starts with
block0 n1801 at94.998171s (:439608). Thus about86.18s of the hold precede the schedule.
First completed-fall row n1891 is99.148697s (:448179), last n3811 is188.897471s (:633588).
Sixteen fall-to-fall intervals take89.748774s, mean5.609298s. Under this SAME observed
cadence, thirteen extra falls need~72.92s: approximately253s hold rather than180s.
This is planning arithmetic, not a guarantee: new period/burn/cadence changes that estimate.
Requiring and recording the actual count is necessary; simply waiting longer does not fix work.

cpuclk_cal99a.csv has two-second samples, not individual-arm observations. For t110..150s
(20 samples), perf_ccd0/ccd1 means179.82/196.095; t150..196s (23 samples)180.00/195.757.
busy_all falls18.614%->17.283% and mean sampled process CPU seconds10.266->9.447.
GPU/CPU sample timestamps cannot alone assign the cause of a repeatable idx2..5 draw transient.
No new claim of GPU saturation, throttling, or a named competing process follows here.
The pre-existing CPU-group guard failure remains a separate unresolved issue.

## 5. Minimal future evidence

Do not reuse cal99a's dt means as an admitted burn budget. First establish a prospective
settling/work-comparability procedure: the current measurement unit and T* horizon are
demonstrably insufficient to hide the arm-induced transient. Verify counter/guest-frame
semantics, then use a newly sealed rule to measure settling with sufficient same-arm dwell,
equal complete blocks/cycles, unchanged strict work tolerance, and independent area control.
If settling exclusions are chosen from this exploratory record, test them on NEW data and
report excluded data/durations alongside the retained population; never rescue cal99a.
Both phase comparability and global/raw work still need explicit interpretation; a late-phase
pass cannot prove missing work was harmless or that the stub is a valid architectural bound.
Only after comparable work is demonstrated should the new protocol admit a dt calibration,
then test the actual calibrated a and c instruments with >=30 observed falls. One fixed longer
hold solves only the count deficiency. No B, calibrated budget, or branch is calculated here.
