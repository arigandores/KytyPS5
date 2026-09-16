# Session 79 — FACTS

**Single source of truth for session 79.** Every number here was produced by running the named tool
on the named log, and every headline was then **re-derived independently** by four auditors who
wrote their own parsers and imported none of this session's code (§9). Where a number is an
interpretation it says so; where something was not measured it says NOT MEASURED.

**This report was rewritten after that audit found three fatal errors and fifteen serious ones in
its first draft.** Every retraction is in §9, in the words the audit forced. The first draft's two
new claims — that the CPU sampler contributes about 1.2 ms to the baseline, and that `dapin` is a
0.72 ms effect "in the wrong place" to be the variable — are **both withdrawn**.

Tree: `merge-upstream`, HEAD `29ded80`. **No source file was changed and nothing was rebuilt.**
Every run sits on session 77's installed binary
`39306a9f95db805aec21d7909bbadf9ec0d115316a013e84d2bc77f8326d9dbf` (23 563 776 bytes), whose
`.text` was hashed here today with a PE-section walker and reads
`90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0` — byte-identical to the `.text`
of `79680f59` and therefore to every `pfhint` and `pfcap` run quoted below. Two auditors walked the
PE themselves and agree.

Harness `C:/kyty/s79`, ported from `C:/kyty/s78` and **verified before use, not after**:
`area_verdict.py` re-derives session 78 on six runs to the printed digit, `arms.py` the seven-run
table, `stats78b.py` the random-effects pool, and the normalised text of `gates_base.txt`
(1092 bytes, 99 names, sha256 `4724bf81…f8c4f`) is **byte-identical to the `gates` field of
`pfh78d.json`, `pfh78f.json` and `cap78b.json`**.

---

## 0. In one sentence

The CPU sampler is **not** the variable behind the run-to-run swing — the first run of the session
measured −848.3 µs without it and three sampler-free runs now span 757 µs — and while establishing
that, the session found a knob already in the tree that buys **0.72 ms of GuestGpu CPU and
+0.86 FPS, reproducibly**, and then found, in its own audit, that the knob is not the pure thread-
placement contrast it was designed to be and that the swing's best predictor was on disk all along:
**the run's own frame time, r = −0.972.**

---

## 1. The runs

Ten attempts, **six area-valid, four void**, all entered Sky Garden at the first attempt in
**14.4–16.8 s**, **no entry hang**.

| tag | what | sampler | verdict | result |
|---|---|---|---|---|
| `nos79a` | `pfhint=0\|1`, `--no-cpuclk` | no | VALID — +0.001 %, 116/116 | **−848.3 ± 76.6 µs** |
| `smp79a` | `pfhint=0\|1` | yes | **VOID** — split +4.541 %, 59/114, rung 46.7 % | not quoted |
| `smp79b` | `pfhint=0\|1` | yes | VALID — −0.002 %, 111/111 | **−1365.0 ± 99.7 µs** |
| `smp79c` | `pfhint=0\|1` | yes | **VOID** — split +3.174 %, 78/115, rung 26.7 % | not quoted |
| `smp79d` | `pfhint=0\|1` | yes | **VOID** — split +11.280 %, 48/113, rung 41.0 % | not quoted |
| `smp79e` | `pfhint=0\|1` | yes | **VOID** — split **+1.946 %** (limit 1.0) and 102/115 = 88.7 % | not quoted |
| `nos79b` | `pfhint=0\|1`, `--no-cpuclk` | no | VALID — +0.005 %, 126/126 | **−91.4 ± 80.7 µs** |
| `smt79a` | **`dapin=65535\|21845`** | yes | VALID — +0.001 %, 122/122 | **−705.7 ± 85.8 µs** |
| `smt79b` | **`dapin=65535\|21845`** | yes | VALID — −0.002 %, 121/121 | **−735.3 ± 97.9 µs** |
| `cap79a` | `pfcap=192\|1024` | yes | VALID — +0.001 %, 115/115 | **−488.9 ± 100.5 µs** |

**No effect, baseline, take price or direction from a void run is quoted anywhere in this report**
— the auditors searched the file and confirmed it. Their validity arithmetic (split, match rate,
rung share) is in the table above because it is what makes them void, and calling that "nothing is
quoted, not an aside", as the first draft did, was wrong. `smp79e` failed on **two** criteria, not
one: its split is +1.946 % against a 1.0 % limit as well as 88.7 % against 90 %. Neither was moved.

**Criterion 5 of `PLAN.md` §1 — the bracketing timer with every delta** (the first draft gave it
for three runs of six):

    nos79a  da_take_us  2855.2 -> 2544.9 = -310.3 +- 18.8   smp79b  3276.8 -> 2784.8 = -492.0 +- 18.2
    nos79b              2607.9 -> 2564.9 =  -43.0 +- 12.2   cap79a  2740.1 -> 2642.8 =  -97.3 +- 19.2
    smt79a              2420.3 -> 2389.5 =  -30.8 +- 12.7   smt79b  2623.3 -> 2580.4 =  -42.9 +- 14.3

**Criterion 4 — `summary4.py` whole-arm vs paired cross-check**, which the first draft never
mentioned: gaps **+0.005, +0.006, +0.009, +0.004, +0.022, +0.006 pp** against a 0.05 pp limit. All
six pass.

**Criterion 1 is weaker than it reads, and this is a finding about the programme, not the session.**
Every valid run reads guards check 2 at "11/11 self-check counters zero", but auditor D traced all
eleven: **nine of them are incremented only inside a verify gate** (`da_cl_bad` behind
`dawitcgcheck`, `texfast_bad` behind `texfastcheck`, `bfast_bad` behind `buffastcheck`, and likewise
`pb_bad`, `pb_bad_rw`, `arm_bad`, `sf_bad`, `tf_bad`, `pmemo_bad`), and every one of those gates is
pinned **off** in `gates_base.txt`. Only `pb_stuck` and `pb_inflight_bad` carry information. **"11/11"
is 2/11**, and it has been since session 74. Check 10 confirms the binary and every `GateArm` block
in all ten runs.

**Pre-registrations** — `pred/01_sampler.md` (8827 B, sha256 `7f30cced…`, written **20:09:39**,
run 1 at 20:16:54), `pred/02_smt.md` (**20:53:08**, `smt79a` at 20:58:34), `pred/03_pfcap.md`
(**21:05:04**, `cap79a` at 21:10:33). **Session 77's audit item C10 is discharged**: `enter_scene.py
--pred` reads the pre-registration's sha256, byte count, mtime and ctime **before the emulator
starts** and writes them into `<tag>.json`; all three still hash to what their runs recorded and
`mtime − ctime ≤ 3 ms`. **But see §6: two of the three were written mid-session with six and eight
runs of this session already read, and their absolute-magnitude bands were drawn around values
already observed.** The machinery proves they were not edited afterwards; it does not make them
blind.

---

## 2. The CPU sampler — REFUTED as the variable; the contributor question is NOT RESOLVED

### 2.1 The pre-registered rule fired on the first run

`pred/01_sampler.md` fixed, before any run: *"H REFUTED as soon as one area-valid `--no-cpuclk` run
reads E ≤ −600 µs. One counterexample refutes a necessity claim."* **`nos79a`, the first run of the
session, read −848.3 ± 76.6 µs.** H is refuted.

Session 78's suspicion rested on `pfh78f` being the smallest effect, the lowest baseline and the
lowest take price of seven — three extremes in the one run without the instrument. It was one draw.

### 2.2 And the swing survives the sampler's removal, which is the stronger statement

Every `--no-cpuclk` run in existence, on byte-identical `.text`:

    pfh78f  arm0 31 567.2   effect   -131.7 +- 91.3
    nos79b  arm0 31 139.2   effect    -91.4 +- 80.7
    nos79a  arm0 31 872.2   effect   -848.3 +- 76.6      spread 756.9 us over three runs

`pfh78e`, the fourth `--no-cpuclk` attempt ever taken, is **void** and is not quoted in any form.

### 2.3 What the first draft claimed here, and why it is withdrawn

The first draft reported that the four sampler runs carry the four highest baselines of the ten,
with no overlap, a difference of means of +1169.3 µs and an exact permutation p of 1/210 = 0.0048;
it hedged on session and time-of-day confounding and then ranked the sampler-as-contributor as the
best-evidenced open candidate. **All three of the auditors who looked at it refuted it, on three
independent grounds, and it is withdrawn:**

* **The separation is not specific.** Auditor D screened every arm-0 quantity in the logs:
  **21 of 722 separate the same four/six groups perfectly at the same p = 0.0048**, and
  `cpu_gpu_us` ranks **15th of the 21** by gap-to-range. One of the 21 is **the effect itself** —
  the quantity §2.1 has just declared sampler-independent on the strength of `nos79a`.
* **The labels are not exchangeable and the correct test says so.** Stratified within session, the
  exact permutation p is **0.083**, not 0.0048.
* **The session's own four voided sampler runs destroy it.** The area gate tests an *arm contrast*;
  §2.3's endpoint is a *single-arm* baseline, which that gate does not test. Restricting every run
  to arm-0 blocks on the low rung (area within 0.5 % of 2007.7 Kpx, so area and work match), all
  fourteen `pfhint` runs give sampler +674.9 µs, **exact p = 0.035, ranges overlapping** —
  `smp79e` (sampler) reads **31 383.8**, below four of the six sampler-free runs. The single
  retained sampler run of session 79 is the **maximum of the five attempted**.

**So the sampler's contribution to the baseline is NOT RESOLVED**, as `pred/01`'s own rule 1 said it
would be (refutation is of *necessity*), and it is **not** ranked first in §10. What would settle
it is unchanged: arm-0 `cpu_gpu_us` as the pre-registered primary endpoint, randomised and
interleaved, six runs a side, **and every attempt admitted on a rung-matched arm-0 baseline
regardless of its arm-contrast validity.**

A mechanism exists to be tested and session 78's own recon measured it: loading CCD1 while CCD0 is
saturated costs CCD0 **4.4–4.6 % of clock**, ~1.4 ms of a 31 ms frame
(`s78_recon/r3_results.txt:172-184`, whose own next line labels it INTERPRETATION, NOT MEASURED ON
THE GAME). The sampler is pinned to CCD1 at a 0.38 % duty cycle.

---

## 3. What twelve runs say about the swing

**The population, stated as a rule and not as a list:** every area-valid ABBA on this `.text` whose
two arms differ in `pfhint` and nothing else. That is **twelve** runs, not the ten the first draft
tabulated: `wit78a` and `wit78d` qualify and were omitted. Two of the twelve (`pfh78b`, `pfh78c`)
carry `imgskip=1` in both arms and two (`wit78a`, `wit78d`) carry `dawitptr=0` in both arms, i.e.
four differ from the other eight at run level. Fits are given for both populations.

| run | arm0 | arm1 | effect | 2·SE | arm0 take ns | arm0 `dt_us` |
|---|---:|---:|---:|---:|---:|---:|
| `nos79b` | 31 139.2 | 31 047.8 | **−91.4** | 80.7 | 303.0 | 31 468 |
| `pfh78f` | 31 567.2 | 31 435.5 | −131.7 | 91.3 | 289.0 | 31 868 |
| `nos79a` | 31 872.2 | 31 023.8 | −848.3 | 76.6 | 331.3 | 33 882 |
| `pfh77a` | 31 941.9 | 31 251.7 | −690.2 | 87.8 | 311.7 | 33 504 |
| `pfh76c` | 32 205.4 | 31 948.1 | −257.3 | 133.5 | 311.7 | 32 571 |
| `pfh77d` | 32 586.5 | 31 852.2 | −734.3 | 103.8 | 326.4 | 34 179 |
| `pfh78b` | 32 675.1 | 31 589.4 | −1085.7 | 94.3 | 392.4 | 34 572 |
| `pfh78d` | 32 923.6 | 31 760.9 | −1162.7 | 84.6 | 387.8 | 34 840 |
| `pfh78c` | 32 977.5 | 31 679.4 | −1298.1 | 83.1 | 372.3 | 34 765 |
| `smp79b` | 33 642.6 | 32 277.6 | **−1365.0** | 99.7 | 379.2 | 34 947 |
| *(`wit78d`)* | 32 630.6 | 31 514.1 | −1116.5 | 89.2 | — | — |
| *(`wit78a`)* | 32 971.7 | 32 052.3 | −919.4 | 105.9 | — | — |

    ten runs   arm0 sd 749.0  range 2503.4 (7.74 % of the mean)   arm1 sd 402.7  range 1253.8
               random effects -766.9  95 % CI [-1106.1, -427.7] (t on 9 df)  I2 = 99.1 %  tau = 472
    twelve     slope 0.4552 [0.233, 0.677]   RE -808.8 [-1091.3, -526.3]   tau = 442

### 3.1 The swing is wider, but "1.8× larger than session 78" is a statistic of n

The observed range is **2503.4 µs**, against session 78's 1410.3 on seven runs. Expected range grows
with n at fixed σ (2.70 σ at n = 7, 3.08 σ at n = 10), and the estimated **sd went 525.8 → 749.0, a
ratio of 1.43 whose variance-ratio test is F = 2.03 on (9,6) df, p ≈ 0.2 — not significant.** Both
new extremes are this session's: the lowest baseline in the record (`nos79b`, 31 139.2 — below
`cap76b`'s 31 300.9, though that ran on a different binary) and the highest (`smp79b`, 33 642.6).
**The honest statement is that the swing is at least as large as session 78 said and the ten-run
range is 2503 µs, not that it grew 1.8-fold.**

### 3.2 The untreated arm is the more variable one — strengthened, not established

Pitman–Morgan on the correlated arms, with **diff = arm1 − arm0, the report's own convention**:
**r(diff, sum) = −0.760, t = −3.31 on 8 df, p = 0.011**. (The first draft printed +0.760; the
covariance is var(arm1) − var(arm0) and is negative by construction whenever the untreated arm is
the more variable one, so the sign contradicted the sentence.) sd ratio **1.86, 95 % CI [1.19,
2.91]**.

**It is not established, and the first draft's "established" is withdrawn.** The test appears in no
pre-registration of this session; seven of the ten runs are the runs on which session 78 generated
and first tested the same hypothesis at p = 0.074; **on the three new runs alone it gives p = 0.29**;
dropping either new extreme gives p = 0.039–0.049 and dropping both gives 0.153; the exact
sign-flip permutation gives 0.039; and eight inferential statistics were read off these ten points
(Šidák α = 0.0064). **Suggestive and strengthened.**

### 3.3 Where the swing is — the first draft's 63.7 % is stale and the majority has moved

Session 78's "63.7 % of the arm-0 spread is inside `da_take_us`" is a ratio of ranges against a
**1410.3 µs** swing. The arm-0 `da_take_us` range over the ten runs is **897.7 µs — unchanged**
(min `pfh78f` 2487.4, max `pfh78b` 3385.1; all three new runs are interior). So:

    da_take_us   range  897.7 =  35.9 % of the swing   var share 19.9 %   cov share 37.3 %
    remainder    range 1834.5 =  73.3 %                var share 45.3 %   cov share 62.7 %

(only the covariance shares sum to 100 %). **Every microsecond of swing this session added is
outside `da_take_us`**, and the majority of the swing now sits in the `cpu_gpu_us − da_take_us`
remainder. Auditor D's "the remainder varies by only 709.5 µs = 2.40 %", quoted by the first draft
and by `pred/02_smt.md`, is **1834.5 µs on ten runs**.

### 3.4 The best predictor of the effect was on disk since session 76 and nobody used it

    corr(effect, arm-0 cpu_gpu_us)  -0.878
    corr(effect, arm-0 da_take_us)  -0.909
    corr(effect, arm-0 dt_us)       -0.972

The first draft claimed the take price "predicts the effect better than the baseline does". It does
not, distinguishably: **Steiger's z = −0.37, p = 0.71** for dependent correlations at n = 10. But
**frame time beats both**, and auditor D measured **corr(effect, mean GPU power over the settled
window) = +0.968 … +0.998** across five subsets, from `gpuclk_<tag>.csv` files the harness has
written since session 76. **The state is best read as how fast the whole frame is running**, not as
a CPU price; and that reading was available for free in every run the programme has ever taken.
**This is a screen over correlated, mutually downstream quantities, not a cause.**

### 3.5 What this does to the shipped figure

    arm0 31 139 (lowest seen)  fitted effect  -91 us   measured -91.4
    arm0 32 353 (the mean)     fitted effect -767 us
    arm0 33 643 (highest seen) fitted effect -1484 us

The first draft concluded "at the best state the gate is worth **nothing measurable**". **That is
withdrawn.** `nos79b` reads −91.4 ± 80.7, **t = −2.27, p = 0.025**; `pfh78f` reads −131.7 ± 91.3,
**t = −2.88, p = 0.005**; pooled they give **−109.1 ± 30.2 µs (SE), t = −3.61, p = 0.0004**, and
they agree (Q = 0.44 on 1 df). **At the best state the gate is worth about 0.11 ms — one seventh of
the pooled figure. Small, not nothing.**

And the fit licenses nothing of that precision there. `arm0 = 31 139` is the minimum of the ten, its
leverage is **h = 0.392**, and the **95 % prediction interval is [−748.0, +566.4]** — it contains
zero and contains `pfh77d`'s −734.3. The point prediction agreeing with the point measurement to
0.6 µs is a coincidence inside a ±657 µs band around a point that is itself in the fit. No
pre-registration of this session contained a baseline-conditioned prediction of E — `pred/01`
explicitly forbade adjusting E by B — so the first draft's "one of them was taken with the
prediction of the fit written down before it" is **false and withdrawn**.

### 3.6 "Removes 56 % of the swing" is a slope and nothing else

    1 - slope(arm1 ~ arm0)       = 56 %  [31, 80] pp      <- what is quoted
    1 - var(arm1)/var(arm0)      = 71 %                   <- the actual variance share
    1 - range(arm1)/range(arm0)  = 50 %                   <- "the swing" is defined as the range
    1 - sd(arm1)/sd(arm0)        = 46 %

The four disagree by 25 pp on the same ten points. Session 78's error was an interval that ran past
100 %; the first draft narrowed the interval and kept the error. **Quote it as a slope, and name
what it leaves: 241.6 µs of arm-1 sd is residual scatter the gate does not remove and the fit does
not predict.** Errors-in-variables was checked and is negligible: within-run SE of an arm mean is
57.0–93.2 µs and the two arms' sampling errors correlate at +0.65…+0.84, which moves the slope from
0.4434 to 0.4411 — **0.24 pp**.

---

## 4. `dapin` — 0.72 ms of CPU and +0.86 FPS, and it is not the contrast it was designed to be

### 4.1 The manipulation

`dapin=1` pins GuestGpu, the four DrawAhead workers and the record thread to `0x…ffff` — **sixteen
logical CPUs on eight physical cores** of CCD0. Verified today and again by two auditors with
`GetLogicalProcessorInformationEx`: 16 physical cores, SMT on every one, siblings (0,1) (2,3) …
(30,31). `pipelineCache.cpp:1451-1458` documents the knob as "0 off, 1/2 L3 group, **other = raw
affinity mask**" and states "the GuestGpu thread applies it to itself once per submission, a
DrawAhead worker at every task it claims"; `:1523` returns early only when the mode is unchanged.
**`dapin=21845` = `0x5555` = CPUs 0,2,…,14, one logical CPU per physical core.** Both arms were
given a raw mask so both take the same branch.

Arming is in the log and needs no counter. `smt79a`: `GuestGpu mode=65535` ×64 and `mode=21845` ×64,
`DrawAhead` ×256 and ×256, `Record` ×63 and ×64. `smt79b`: GuestGpu 64 and **63**, DrawAhead 256 and
**252**, Record 63 and 63 (the first draft said "the same"). **Zero `failed` suffixes in either.**
Auditor D's source census confirms `Knob::DrawAheadPin` is read at exactly two places, both only to
build an affinity mask, with no behavioural branch anywhere in the tree, and that exactly six
threads apply it and no others. The block-boundary re-pin is balanced by the ABBA order.

### 4.2 The measurement

    smt79a   arm0 31 752.9   effect  -705.7 +- 85.8    dt_us -2.696 %   30.581 -> 31.420 FPS
    smt79b   arm0 32 001.4   effect  -735.3 +- 97.9    dt_us -2.822 %   30.338 -> 31.216 FPS
    random effects  -718.6 us   95 % CI [-1128.5, -308.6] (t on 1 df)   Q = 0.21 / 1 df

The two runs differ by 29.6 µs against an SE of the difference of 65.1. **`I² = 0` and `τ = 0` are
estimator floors at k = 2** (Q = 0.21 < df = 1), not measurements; the Q-profile 95 % upper bound on
τ is ≈ 666 µs, larger than `pfhint`'s 472, though τ ≥ 400 is disfavoured at p ≈ 0.04. The first
draft printed "I² = 0, τ = 0" with no interval — the only article in the report without one — and
called it "the first thing this programme has measured in three sessions that reproduces". **Two
runs agreeing is consistent with reproducibility and with τ up to ~300 µs, and the programme's own
three-run rule is not met.**

**In frame time, which is what 60 FPS is denominated in, `dapin` is +0.839 and +0.878 FPS** —
larger than `pfcap` (+0.38…+0.46) and than seven of the ten `pfhint` runs. The A/A control reads
+16.1 ± 96.5 µs of `dt_us` (t = +0.33), so the CPU→frame-time conversion is not an instrument
artefact. The first draft printed no frame-time figure for anything.

### 4.3 It is NOT a pure placement contrast — the first draft's headline is withdrawn

The first draft wrote "Work is unchanged" on the strength of `da_hit`, draws and rendered area.
Auditor D checked the rest. **Nine counters move reproducibly in both runs, with t between 10 and
33 — five to twenty times larger than in any other contrast in the record:**

| per frame, arm1 − arm0 | `smt79a` (t) | `smt79b` (t) | largest in any other run |
|---|---|---|---|
| `rp_begin` (render-pass begins) | +6.55 (20.6) | +7.59 (20.6) | +0.97 (3.1) |
| `rpa_slot` / `rpa_att` | +12.98 (33.1) | +14.37 (29.8) | +1.19 (2.9) |
| `rpa_re_kpx` (pass-restart area) | +2674.6 Kpx (9.5) | +2075.5 (7.5) | +626 (2.2) |
| `rec_direct` | +19.23 (24.5) | +22.97 (24.4) | +2.58 (3.0) |
| `faults` | +28.31 (18.3) | +31.30 (20.2) | +5.09 (3.1) |
| `pb_flush` | +14.6 (22.3) | +15.6 (24.3) | +2.32 (3.7) |
| `prot_pages` | +236.2 (15.8) | +225.8 (15.8) | +42.6 (2.8) |
| `submits` | −0.66 (−13.0) | −0.59 (−10.0) | +0.15 (3.2) |
| **`gpu_busy_us`** | **+169.0 (14.7)** | **+238.2 (20.2)** | +46.6 (4.4) |

I verified the last row myself with `summary4.py`: `gpu_busy_us` rises **+1.319 %** and **+1.948 %**
in the `0x5555` arm, against +0.346 % in `nos79a` and +0.159 % in `cap79a`. **`dapin` is the only
contrast in the record that moves GPU busy time significantly.** D ruled out the guest-clock pacer
as the cause: three `pfhint` runs carry *larger* per-arm guest-clock differences and move none of
these counters.

**Corrected statement.** `dapin=65535|21845` buys −705.7 ± 85.8 and −735.3 ± 97.9 µs of GuestGpu
CPU and about +0.86 FPS, **while simultaneously and reproducibly increasing render-pass begins by
3.6–4.2 %, pass-restart area by 2–2.7 Mpx a frame, page faults by 2.3–2.5 %, protect-batch flushes
by 3.5 % and GPU busy time by 1.4–1.9 %, and reducing submissions by 1.7 %.** It is a net CPU
saving against a GPU cost, produced by a changed interleaving of the GuestGpu and record threads —
**not the pure thread-placement contrast `pred/02_smt.md` designed.** §0's first-draft phrase "in
nothing but which logical CPUs the scheduler happened to give six threads" is withdrawn.

### 4.4 Where the win went, and why the "wrong place" argument is withdrawn

Auditor D decomposed it, matched pairs, both runs consistent to ~10 %:

    da_walk_us  (M1 shadow walk)  -277.4 / -271.6   39.3 % / 36.9 % of the win
    da_queue_us (M1 enqueue)      -123.8 / -122.2   17.5 % / 16.6 %
    da_take_us                     -30.8 /  -42.9    4.4 % /  5.8 %
    pb_wait_gpu_us                 +58.1 / +61.6    -8.2 % / -8.4 %
    unattributed on GuestGpu      -382.4 / -423.0   54.2 % / 57.5 %   (every run is KYTY_FRAME_TRACE=lite)

Off the GuestGpu thread: `da_work_us` (four M1 workers) **−1643.5 / −1551.5**, `cpu_record_us`
−501.7 / −614.6 of which `rec_spin_us` (polling an empty queue) **−603.4 / −700.1**, `cpu_main_us`
+110.9 / +134.9 — **total thread CPU −2.73 / −2.76 ms a frame**, 3.8× the headline.

The first draft argued that `dapin` is "a large effect in the wrong place" because it puts 4–6 % of
itself into `da_take_us` while "63.7 % of the swing lives there". **§3.3 shows that 63.7 % is 35.9 %
on the ten-run table and that the majority of the swing has moved into the remainder — which is
where `dapin` acts.** The argument is inverted by the session's own data. **"Whatever the state is,
this is not it" is withdrawn, and so is §9's "cheap falsification" built on it.** What can be said:
`dapin`'s win is ~57 % in the M1 walk and enqueue, which between them carry ~17 % of the swing, and
~54–58 % of it is untimed because the harness runs at `lite`. **Intra-CCD placement is neither
established nor excluded as the variable.**

### 4.5 Not shippable as written

`21845` is a raw mask for this machine's topology. Shipping needs a **mode** — "one logical
processor per physical core of the largest-L3 group", computed the way the existing `l3_masks`
already are — which is a source change and was not made. And the GPU cost in §4.3 must be
understood first: a 1.4–1.9 % rise in `gpu_busy_us` is affordable at 12.5 ms of GPU against 32 ms of
CPU and would not be on a GPU-bound scene.

---

## 5. `pfcap` — a third same-code run

    cap77a   arm0 31 710.8   effect  -381.8 +- 79.8
    cap78b   arm0 32 381.0   effect  -502.5 +- 99.9
    cap79a   arm0 32 225.7   effect  -488.9 +- 100.5
    random effects  -452.8 us   95 % CI [-628.0, -277.7] (t on 2 df)   Q = 4.60/2   I2 = 56.5 %   tau = 53

Arming, measured: `da_pf_cap_b / da_pf_b` = **58.94 % in the 192 arm, 94.41 % in the 1024 arm**
(session 76 read 58.8 / 94.4 — close, not "exactly"). The bracketing timer moved **−97.3 ± 19.2 µs**.

Three corrections to the first draft, all from the audit:

* **"the interval is 2.0× wider" is 1.48×**, and the attribution was inverted. The third run
  **narrowed** the standard error 32 % (60.2 → 40.7); the widening is entirely the z→t switch
  (2.20×).
* **Applied consistently, the same switch puts zero inside session 78's own two-run figure**:
  `cap77a` + `cap78b` with t on 1 df give **[−1203.7, +326.9]**. That is the finding, and this
  session's third run is what removes it.
* **I² = 56.5 % has a 95 % CI of [0 %, 88 %] and Q gives p = 0.100**: the three runs are **not**
  shown to disagree. P3.6 was scored a hit on a point estimate whose interval starts at zero.

`cap76a` and `cap76b` remain excluded: they ran on `240edc02`, different machine code for the block
under test, and session 78's `PLAN.md` §0a pre-registered the exclusion.

---

## 6. The prediction scoreboard, honestly

**Twenty-five predictions were pre-registered** (P1.1–P1.11, P2.1–P2.7, P3.1–P3.7), not the
twenty-one the first draft counted; 22 were scorable. **21 hit, 1 missed.**

**Miss (1): P1.5** — the arm-0 baseline of the `--no-cpuclk` runs predicted in 31 300 … 33 300 µs;
`nos79b` read **31 139.2**. **Same direction as every one of session 78's fifteen misses: a band
drawn for an absolute magnitude was too narrow.**

**And 21 of 22 is worth nothing as calibration, for four reasons the audit named:**

1. **Two of the three pre-registrations were not blind.** `pred/01` was written before run 1.
   `pred/02` was written at 20:53 after six runs, and its own text says "four of this session's
   seven attempts so far have been void"; its bands P2.5 (275–360 ns) and P2.7 (30 800–33 800 µs)
   were drawn around values already observed. `pred/03` was written at 21:05 after eight runs and
   opens by quoting `nos79b`'s −91.4. **Fourteen of the twenty-one hits were written with the
   session's own results in hand.**
2. **The bands were drawn deliberately wide**, precisely because session 78 scored 9 hits to 15
   misses with every miss in one direction. A wide band is easy to hit.
3. **Several are nested or logically forced.** P1.1 entails P1.2; rule 1 firing forces P1.3 and P1.4
   false; P1.7 is inside P1.6; P3.3 is inside P3.2.
4. **The scoring rule was asymmetric.** P2.4 and P3.3, rated p = 0.45, are counted as hits for
   occurring, while P1.3 (0.25) and P1.4 (0.30) are counted as correct for not occurring — a rule
   under which a sub-coin-flip prediction wins either way.

**P1.8 was scored on one run, not two.** It reads "the same-session sampler **controls**", plural;
four of five sampler attempts went void.

**The only two predictions with real discriminating power were P1.1 and P1.10, and both came out
against the hypothesis they were written to test.**

---

## 7. The block that was not finished, and the deviations

`pred/01_sampler.md` fixed **four valid ABBAs, order N S S N, budget ten attempts, no optional
stopping**. What happened:

* The block consumed **7 attempts** and produced **three valid runs — N S N — two `--no-cpuclk` and
  ONE sampler control**, against a design of two a side. **Three attempts of the ten-attempt budget
  were left and were spent on `pred/02` and `pred/03` instead.**
* `pred/01` rule 3's "fewer than two valid runs a side → NOT RESOLVED" condition was therefore met,
  and the first draft did not say so. It is said here, and §2.3 rests on a single sampler
  observation.
* The order deviation (N S N for N S S N) was declared in the session log at the time it was taken,
  with the argument that N S N is also drift-balanced. That argument is **approximately** right, not
  exactly: the actual starts are 20:16:54, 20:28:54 and **20:51:42**, so the S run sits at 34 % of
  the span, not 50 %, and the first draft's "20:47" for `nos79b` was **typed from memory and is five
  minutes wrong** — in the paragraph arguing temporal balance, in a session whose banner claim is
  that timestamps are read from the clock.
* `PLAN.md` §2 and `pred/01` define **B** as the *whole-arm* arm-0 `cpu_gpu_us`; §3's table reports
  the *matched-pair* mean (they differ by 0.0–53.4 µs). No conclusion changes; the estimator is
  declared here.

---

## 8. Corrections to the record

Items 1–6 were raised by **session 78's own four auditors** and reached neither its `FACTS.md` §9
nor the session-79 brief. That audit file contains **5 FATAL and 20 SERIOUS findings**, not the "two
fatal and fifteen serious" §9 reports, and its claim that every one was incorporated is false — the
t = +0.45 substitution and the 8772-flip window are two that demonstrably were not.

1. **The brief's §3.2(3) heap-layout plan is the wrong measurement on the wrong object.** Because
   the backing is imported in 27 chunks of 512 MB (`HostImport:`), `run.backing` is chunk base plus
   a fixed guest offset, and Windows' 64 KiB allocation granularity then pins **bits 0..15 identical
   in every run** — the whole L1 line offset and the virtually-indexed set index (48 KB, 12-way →
   64 sets → index bits 6..11). Only L2-TLB index bits and physical page colour are free. And
   `RecordThread: started recorder=0x…` is the **record thread's own arena**, which `AheadTake`
   never touches. *(The chunking premise is load-bearing and the first draft dropped it.)*
2. **`FACTS.md` s78 §2.4's "t = +0.45" for the A/A is a statistic substitution.** +0.45 is the t of
   `area_verdict.py`'s per-cent `cpu/draw` statistic; **the t of the +24.8 ± 75.8 µs effect is
   +0.654**. Raised by three of four s78 auditors, never fixed, propagated into the brief.
3. **"8772 settled flips" for `acc78a` is the whole run.** 285 of those flips have draws < 3000. On
   n ≥ 2100 the base reads **32 789 / 13 497 / 34 956 / 28.61 FPS**, not 32 643 / 13 310 / 35 069 /
   28.51; `acc77a` reads **31 360 / 14 681 / 31 765 / 31.48**. Both propagated into the brief.
4. **s78 §2.1's "(1.62 % of mean)" is printed after the range but is sd/mean.** Range/mean is
   **4.351 %**, 2.68× larger.
5. **A confound in every A/B the programme runs.** `videoOut.cpp:1188-1206` paces the guest clock
   from an EMA (α = 0.08, ~12-flip time constant, so it settles **inside** a 30-flip block):
   `speed = clamp(target_us / pace_ema_us, 0.2, 1.0)` → `KernelSetGuestSpeed`. Auditor D established
   `flip_rate = 0` (no `SetFlipRate` call in 1 274 270 lines), so `target_us = 16 667` and the
   measured speed is 0.467–0.530 — **never clamped**. Per-arm guest-clock differences run 0.3–4.2 %
   across the record and **0.0 % in the A/A**. That the pacer *causes* the area splits is **NOT
   MEASURED**. Its untested corollary: with a ~12-flip time constant inside a 30-flip block, the
   first ~40 % of every block carries a guest-speed transient inherited from the previous arm.
6. **The 326-counter hunt over 11 byte-identical runs returned nothing** and auditor D asked that it
   not be re-run. It was not. Host co-tenancy is **not discriminated by** the s78 record (the
   `pre_run` census is identical across all fifteen runs) — "excluded" overstates it, since an
   identical process-name census is not an identical load. `pre_run['host']` cannot see the sampler
   at all: `sample_host()` runs 28 lines before `start_cpu()`.
7. **Session 78's "the validity gate does not discard the runs where the gate works best" does not
   hold in session 79.** In **4 of 4** void runs the effect over *all* adjacent pairs is more
   negative than over matched pairs (−958.0 vs −796.2; −885.9 vs −866.3; −1451.4 vs −1418.6;
   −424.9 vs −334.0), i.e. the gate drops the pairs where the gate looks best, by 20–162 µs. And the
   void runs' effects are slightly **larger** than the valid ones (−853.8 vs −768.3), the opposite
   of what s78 recorded. The DRS feedback itself replicates: **16 of 16** void ABBAs on disk have the
   gate-ON arm rendering more area.
8. **A position-in-the-ABBA-period artefact nobody has measured.** Splitting matched pairs by
   orientation, the block immediately following an arm switch is systematically cheaper, in **every**
   run including the A/A control; half-amplitude up to **158.5 µs** (`cap78b`), −38.3 µs in `aa78a`.
   Because ABBA balances orientation 61/61, the induced bias on every published estimate is
   **≤ 0.9 µs** — no number in the record is wrong because of it. **But it does not cancel in a
   round-robin schedule of more than two arms**, which is exactly the four-arm design §10 was going
   to propose.

---

## 9. What the audit forced

Four agents that had not seen the analysis were given the raw logs and the draft: one re-derived
every headline with its own parser, three attacked. **The re-deriver returned CONFIRMED — all 20
run-level numbers and all ten-run statistics reproduce to the printed digit, and the
pre-registration hashes and `.text` hash verify independently** — and the three adversaries returned
PARTLY_REFUTED. The load-bearing retractions:

* **"The four sampler runs carry the four highest baselines, no overlap, p = 0.0048" — WITHDRAWN.**
  21 of 722 arm-0 quantities separate the same groups at the same p, including the effect itself;
  stratified within session p = 0.083; and the session's own four voided sampler runs, admitted on
  the single-arm endpoint the gate does not test, break the separation entirely.
* **"At the best state the gate is worth nothing measurable" — WITHDRAWN.** −109.1 ± 30.2 µs,
  t = −3.61, p = 0.0004. Small, not nothing; and the fit's prediction interval there is [−748, +566].
* **"0.72 ms of CPU in nothing but which logical CPUs the scheduler gave six threads" — WITHDRAWN.**
  Nine work counters move at t = 10–33, `gpu_busy_us` among them.
* **"It is a large effect in the wrong place / whatever the state is, this is not it" — WITHDRAWN
  AND INVERTED.** 63.7 % is 35.9 % on this session's own table and the majority of the swing has
  moved to the remainder, where `dapin` acts.
* **"Work is unchanged" — FALSE.**
* **"The sd ratio is now established" — SOFTENED** to suggestive and strengthened: not
  pre-registered, a second look at data that generated the hypothesis, p = 0.29 on the new runs
  alone, 0.039 by exact sign-flip permutation.
* **"The swing is 1.8× larger" — SOFTENED**: the sd ratio is 1.43 at F = 2.03, p ≈ 0.2.
* **"The take price predicts the effect better than the baseline" — WITHDRAWN** (Steiger p = 0.71),
  and replaced by the one that does: `dt_us`, r = −0.972.
* **"The interval is 2.0× wider" — 1.48×, and the causation was inverted.**
* **"τ = 0, I² = 0, it reproduces" — the floors named, the interval restored, the three-run rule
  declared unmet.**
* **"Nothing is quoted from any void run, not an aside" — the sentence was false as written.**
* **"11/11 self-check counters zero" — 2 of the 11 carry information; nine are unreachable.**
* **"All entered in 15.3–16.1 s" — 14.4–16.8 s, typed from memory.**
* **Pitman–Morgan sign, `cap79a`'s timer (−97.3, not −95.8), `cap76b` not `cap76a` as the lowest
  prior baseline, "sevenfold" (9.3×), "exactly" (58.94 vs 58.8), the scoreboard's count.**

---

## 10. Not closed, and what would settle each

1. **The variable behind the swing.** The best description found this session is not a CPU quantity
   at all: **corr(effect, arm-0 `dt_us`) = −0.972** and corr(effect, GPU power) ≈ +0.97, both from
   files the harness has written since session 76. *Next:* stop treating the baseline as the
   conditioning variable and pre-register **frame time** as it, then find what sets frame time at
   process start. This costs no run to specify and supersedes the candidate list the brief carried.
2. **The CPU sampler as a contributor** — NOT RESOLVED (§2.3). *Next:* arm-0 `cpu_gpu_us`
   pre-registered as the primary endpoint, randomised and interleaved, six a side, **every attempt
   admitted on a rung-matched arm-0 baseline** regardless of arm-contrast validity.
3. **`dapin`.** Two runs, −719 µs [−1129, −309], +0.86 FPS, and **not a pure placement contrast**.
   *Next:* a third run; a `lite`-off run to attribute the 54–58 % that is untimed; and an
   explanation of the `gpu_busy_us` rise before any shipping decision. A shippable version needs a
   topology-derived mode, not a raw mask.
4. **Intra-CCD placement as a varying state** — **untestable from any log on disk.** Nothing records
   which logical CPU a thread ran on; `GetCurrentProcessorNumber` is called at one site and
   immediately reduced to an L3 index, and `da_ccd_x`/`rec_ccd_x` read identically 0 in both arms of
   all ten runs. *Next:* a two-line `GetCurrentProcessorNumber()` gauge per flip — but that is a
   rebuild.
5. **A named, testable mechanism nobody has looked at**: on the eight sampler runs' `cpuclk` CSVs,
   the slow state is the **idler** state — corr(c3_ccd0, arm-0 baseline) = **+0.914** (+0.936 on the
   five `pfhint` runs), corr(busy_ccd0) = −0.781 (−0.990), corr(intr_ccd0) = −0.894 — while
   `mhz_ccd0` spans only 0.9 % against the baseline's 7.7 %. **C-state residency and wake-up latency,
   not frequency and not contention.** n = 5–8 and all mutually downstream: a screen, not a finding.
6. **P2's `imgskip` contrast** is still not resolved (+29.2 µs inside its own ±250 µs band). **The
   four-arm schedule that would answer it in one process is now ruled out**: `gates.cpp:380-381`
   silently forces ABBA off for `arms != 2`, `:468-469` falls back to plain round robin so every arm
   has the same predecessor, and §8.8's orientation artefact — up to 158 µs, present in the A/A —
   does not cancel in that design.
7. **The guest-clock pacer** (§8.5) — one ABBA with it pinned, or with the rung forced low in both
   arms. It bears on every measurement the programme takes.
8. **Acceptance criterion 1 is vacuous** and should be rewritten to name the two counters that are
   reachable, or to turn one verify gate on in one run per session.
9. Session 78's untouched items: the guest-line prefetch population's share; `b_buf` vs `b_tex` and
   the `Scope`-cost calibration; the prefetch bitmask knob; the sum of the shipped gates; M4's
   serialiser (44.6 FPS ceiling); the dead gate `dawitfb`.
10. **No acceptance run was taken.** No source file changed, so it would have been one more draw of
    the state. The base of record is `acc78a`, restated on the settled window as
    **32 789 / 13 497 / 34 956 / 28.61 FPS**.

---

## 11. The arithmetic

| article | axis | measured | state |
|---|---|---:|---|
| **the baseline swing** | CPU | **range 2503 µs, sd 749 over ten runs at identical work** | **variable NOT IDENTIFIED** |
| its best predictor | — | **corr(effect, arm-0 `dt_us`) = −0.972** | a screen over downstream quantities |
| the swing is heavier in the untreated arm | — | sd ratio 1.86 [1.19, 2.91], PM p = 0.011 | **suggestive, not established** |
| where the swing is | — | `da_take_us` 35.9 % of range; remainder 73.3 % | s78's 63.7 % was against a 1410 µs swing |
| `pfhint` 0 → 1 | CPU | RE −767 [−1106, −428], I² = 99.1 %, τ = 472 | 10 runs (12 by the stated rule) |
| `pfhint` at the best state seen | CPU | **−109 ± 30 µs, p = 0.0004** | small, not nothing; PI there is [−748, +566] |
| `pfcap` 192 → 1024, same code | CPU | **−453 µs [−628, −278]**, I² CI [0, 88] % | **3 runs**; s78's two on t(1 df) included zero |
| **`dapin` 0xffff → 0x5555** | CPU+GPU | **−719 µs [−1129, −309], +0.86 FPS**, GPU +1.4…1.9 % | **2 runs, not a pure placement contrast** |
| the CPU sampler as *the* variable | — | refuted on run 1; 757 µs of swing without it | **REFUTED** |
| the CPU sampler as a *contributor* | — | separation is shared by 21 quantities; stratified p = 0.083 | **NOT RESOLVED** |
| fraction of the swing `pfhint` removes | — | slope-based 56 % [31, 80] pp; 46–71 % by other metrics | INTERPRETATION |

**The honest statement.** Session 78 asked whether the harness had been the variable. It had not —
the same gate moved by 757 µs across three runs that never saw the sampler, and the largest of them
was the first run of this session. Beyond that the session's own audit took back both of its new
claims, and what is left in their place is more useful than either: the swing's majority is **not**
in the timer the programme has been watching, its best predictor is the run's own **frame time**,
and a knob that was already in the tree buys **0.86 FPS** for no code while doing something to the
GPU that nobody has explained. **60 FPS still needs about 15 ms off the CPU path, and the programme
still cannot say what state it is measuring in — but it now knows which number to condition on.**

Commit **270ae1f** (branch `merge-upstream`, base `29ded80`, 2 files, +805) — `docs/local-session-79.md` and `docs/next-session-80.md` only. **No source file changed and nothing was rebuilt this session.** Not pushed.
