# Session 80 — local report

**Single source of truth for session 80.** Every number here was computed this session from a
named file, and every headline was re-derived independently by agents that imported none of this
session's code and then attacked by three adversaries each (§9). Where a number is an
interpretation it says so; where something was not measured it says NOT MEASURED.

Tree: `merge-upstream`. **No source file was changed and nothing was rebuilt.** Every run sits on
session 77's installed binary
`39306a9f95db805aec21d7909bbadf9ec0d115316a013e84d2bc77f8326d9dbf` (23 563 776 bytes), whose
`.text` is `90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0`, byte-identical to
`79680f59` and therefore to every `pfhint`, `pfcap` and `dapin` run quoted below.
`C:/kyty/build/install/kyty_emulator.exe` hashes to the same value, so `enter_scene.py` installing
it is a no-op.

Harness `C:/kyty/s80`, ported from `C:/kyty/s79` and **verified before use**: `arms.py` from
`C:/kyty/s80` re-derives session 79's whole §3 table to the printed digit. `gates_base.txt` is
**1092 bytes, 99 names, sha256 `4724bf812e8d095f21dc89b0e324fcf156e30d2614edcc35bb1623f9fe5f8c4f`**.

**Pre-registrations, both sealed before run 1 and never edited:**

    pred/01_sampler_block.md  13309 B  sha256 b5f919bcdf1616f9b1bb041c36e23d1fa3c408689e657f7d55048591bf4663c7
    pred/02_vblank.md          6833 B  sha256 f57c4c62de88956fd7be5d1693ae07b4723bcc8fe1fa68e20eaff8c89abb7b25
    pred/order.txt              868 B  sha256 018b5db873e9d860cfaf459c27071d83ad290e9c7f669951ebceb73add50652d

`01`'s sha256, size, mtime and ctime are recorded inside all twelve `<tag>.json` **before the
emulator started**; its mtime − ctime is 1.0 ms. `02`'s is not (`enter_scene.py --pred` takes one
path) — its anchors are mtime == ctime = 0.0 ms and `a80_prereg_manifest.json`, and that is a
weaker anchor, stated here rather than glossed. `order.txt`'s **mtime − ctime is 12.05 s**, because
it was rewritten once before run 1 when the design changed (§4.1); its real anchor is that the draw
reproduces from a fixed seed, which two auditors verified independently.

---

## 0. In one sentence

The variable behind three sessions of unexplained swing is **not a CPU price at all**: `dt_us` is
hard-quantised onto the 60 Hz vblank grid, `cpu_gpu_us` per flip is therefore a frame-time
statistic, **90.6 % of the published `pfhint` effect is a vblank-class mix shift**, and what varies
between runs is how many frames had already missed the two-vblank deadline — while the
twelve-run pre-registered block on the CPU sampler returned **NOT RESOLVED** and its own audit
showed that the endpoint the programme has been conditioning on measures composition, not price.

---

## 1. The zero-run finding — the mechanism

Seven agents and twenty-one adversarial audits, entirely on data already on disk.

### 1.1 Frame time is quantised and one present is one game frame

* **`dt_us` lies on the 60 Hz vblank grid.** Pooled over the ten-run `pfhint` population,
  **1 vblank 4.31 %, 2 vblanks 89.65 %, 3 vblanks 6.03 %**; on the twelve new runs
  **99.97–100.00 %** of settled flips are within rounding of 1, 2 or 3 × 16 666.7 µs.
  `flip_rate = 0` is confirmed twice — no `SetFlipRate` line in 1 274 270 log lines, and
  `sceVideoOutSetFlipRate`'s NID `CBiu4mCE1DA` is **absent from the game's import table** — so the
  pacer target is 16 666.667 µs (`videoOut.cpp:1193-1194`).
* **One present is one complete game frame.** Draws per flip is 5036.4–5048.8 across the ten,
  a spread of **0.346 %**. Six independent once-per-frame counters (`rpa_a3` 40.0055 vs 40.0044,
  `downloads`, `dmas`, `dg_img`, `da_mesh_vs`, `rpd_a1`) are **intact** on a one-vblank flip and
  **exactly doubled** over the pair with its neighbour. A wall-clock slice cannot do that.
* **The class mixture IS mean frame time and nothing else:**
  `p1 + 2·p2 + 3·p3 = mean_dt / 16 666.667` with a gap of **0.0000 in all thirteen runs checked**
  and **≤ 0.0011 in all twelve new ones**.
* Therefore **`cpu_gpu_us` per flip ≈ `dt_us` − thread idle**: regressing one on the other within
  an arm gives **r = 0.954–0.9986 in all 36 arm-level fits** (`nos79b` arm 1: r = 0.9986,
  intercept 36.2 µs).
* `dt_us` is present-to-present wall clock on the Present thread (`videoOut.cpp:1267`, spanning
  two `FS::NowNs()` at `:1236`), from **rdtsc** (`frameStats.cpp:197-211`); `cpu_gpu_us` is
  `QueryThreadCycleTime` on the GuestGpu thread (`frameStats.cpp:604-620`), so it excludes every
  descheduled wait and includes every spin.

### 1.2 What a one-vblank flip is

A flip with `draws < 4500` is **one complete game frame missing a specific block of guest render
work**: ~**40 full-resolution depth-only passes** each closed by a shader-write barrier plus
~**7.5 five-attachment passes carrying ~2160 draws** (`rpa_a0` −40.2, `rpa_a5` −7.5, `rpd_a5`
−2157.8, `rpa_e7` −40.0, `swloc_ok`/`swbar` −40). `gpu_busy_us` falls **−3197 µs**, so the GPU
really did less work. Ruled out with whole-log scans: AsyncPipelines skipping draws (**0 lines**),
a held incomplete present (**0 lines**), a double present, `KYTY_GE_DRAWS`, a DRS resolution change
(`rt_w×rt_h` = 3840×2160 on every flip).

**Which way the causation runs is NOT MEASURED**, and the arithmetic forbids the simple answer:
removing ~2160 draws at ~6.2 µs/draw ≈ 13 ms from a 32.6 ms frame lands at ~19.6 ms — two vblanks
— yet **no `rpa_a5 == 0` flip ever takes two or more vblanks and no 1-vblank flip ever carries
≥ 4500 draws, in 18 of 18 runs.**

### 1.3 The published effect is nine parts class mix

Per-arm vblank-class shares over the ten-run population, arm1 − arm0, paired t on 9 df with the
exact 2¹⁰ sign-flip permutation:

    1-vblank share  +0.8097 pp  [+0.4629, +1.1565]  t = +5.282  exact p = 0.0020
    2-vblank share  +3.2130 pp  [+1.2571, +5.1689]  t = +3.716  exact p = 0.0059
    3-vblank share  -4.0109 pp  [-6.0242, -1.9975]  t = -4.507  exact p = 0.0020

At the pooled band prices (1 vbl 16 637.4, 2 vbl 31 761.0, 3 vbl 46 018.1 µs/flip) those shifts
carry **−694.3 µs/flip of the published −766.5 µs mean = 90.6 %**. Measured directly, holding the
class fixed, the per-flip effect is **−52.9 µs, sd 40.6, range 103.7** against the published
sd 475.1 and range 1273.6.

**And the swing is headroom:** corr(published effect, arm-0 3-vblank share) = **−0.9759**
(Spearman −0.9515) over the ten, whose shares run **0.820 % … 14.835 %**. Split at the median, the
relation holds inside **both** halves — r = **−0.9689** (low five) and **−0.9502** (high five),
each at the exact permutation floor p = 0.0167 — and the ten shares have no gap wider than 3.21 pp.
**So the record population is a genuine ten-point monotone relation, not a two-cluster contrast.**
(The block's own version is a two-cluster contrast; see §5.3. This distinction is the session's
sharpest, and it was not in the first draft.)

### 1.4 The conditioner the programme has used since session 78 collapses

    corr(effect, arm-0 cpu_gpu_us)   -0.878   ->  -0.234 [-0.812, +0.575]  once cheap flips are dropped
    corr(effect, arm-0 dt_us)        -0.981   ->  -0.977 [-0.996, -0.872]
    Steiger (Williams t, df n-3)     TEN published -2.932 p = 0.0220 ; TEN filtered -5.314 p = 0.0011

**The baseline's apparent predictive power was the one-vblank flip share, not a CPU price.**
Leave-one-out: the Steiger p is LOO-robust only in the filtered variant ([0.0012, 0.0035]); on the
published estimator dropping `pfh76c` alone takes it above 0.05.

**`dt_us` is not the best predictor either.** Screening all 341 usable arm-0 counters common to the
ten runs, it ranks **4th**: `semwait_us` −0.9855, `rec_spin_gpu_us` −0.9854, `rec_spin_us` −0.9853,
`dt_us` −0.9814. None of the four is distinguishable (Steiger p = 0.55–0.58; mutual r ≥ 0.994). The
three that beat it are **waiting** counters. INTERPRETATION, not measurement.

### 1.5 The guest-clock pacer is not shown to be a confound

The chain is verified line by line (`videoOut.cpp:1187-1206`, α = 0.08, target 16 666.667 µs,
`KernelSetGuestSpeed` → `ScaledTscLocked` at `pthread.cpp:196-202`). Upper bound on its
contribution to the published effects **~9 %, with the point estimate of the wrong sign**, far
inside τ = 472 µs. It **is** a guaranteed correlate of every effect, so nothing derived from it —
`dt_us`, `resid0`, the class shares, mean frame time are all the same number — may be quoted as an
independent predictor. **The single measurement that settles it:** one area-valid ABBA with
`KYTY_AUDIO_SYNC=0`, which makes `ScaledTscLocked` the identity and the arm-wise clock contrast
exactly zero by construction. No code, no rebuild. NOT TAKEN this session.

---

## 2. What §1 retracts from the record

1. **FACTS s79 §3's column headed `arm0 dt_us` is not arm-0.** It is the settled-window mean over
   **both arms** — every arm-0 candidate estimator deviates from the printed column by +55.7 to
   +722.6 µs and gives r = −0.980…−0.981, while every both-arms candidate lands within 2.6–23.3 µs
   and gives −0.9717…−0.9720. So **−0.972 was computed against a covariate that contains its own
   outcome**, which is the failure mode the same report polices elsewhere. The correct arm-0 value
   is **−0.9814**. The contamination weakens rather than inflates, so nothing downstream is
   overstated.
2. **"range 2503 µs, sd 749 over ten runs at identical work"** stands only if "identical work"
   means rendered area per attachment, which is what it was argued from and which does not see the
   class mixture. Excluding fragment flips moves arm-0 sd **749.0 → 489.3** and range
   **2503.4 → 1794.5**.
3. **FACTS s79 §3.5's "at the best state the gate is worth −109.1 ± 30.2 µs, t = −3.61,
   p = 0.0004"** does not survive the filter: fragment-free those two runs read **−3.5 ± 60.0** and
   **−88.1 ± 55.6**, pooled **−49.1 ± 40.8, t = −1.20**. And the same two-run pool with the t
   quantile that §5 of that report applied to `pfcap` gives **[−493, +275]**, containing zero. §3.5
   and §5 of FACTS s79 used different rules on two-run pools.
4. **`nos79b`, "the lowest baseline in the record" at 31 139.2, has essentially the most expensive
   2-vblank flips of the ten** (32 924.0 µs, second of ten behind `pfh78f`'s 32 927.0). Its low
   published baseline is 11.7 % one-vblank flips, not a cheap machine.
5. **Draws per flip explains none of it.** The exact symmetric range split of the 2503.4 µs swing
   is **D-term 112.2 µs (4.48 %), P-term 2391.2 µs (95.52 %)**; work per game frame is identical to
   0.346 %. The composition that matters is the **vblank class**, not the draw count.
6. **`<tag>.json["started"]` is the run's END**, stamped in `enter_scene.py`'s `finally:` block:
   confirmed on 10 of 10 session-79 runs, where it equals the last `gpuclk` sample to within 0.6 s
   while the first sample is ~1 s after `pre_run.sampled_at`, 321 s earlier. FACTS s79 §7 quotes
   three of those stamps as "the actual starts"; all three shift equally so its 34 % survives, but
   §1's "written 20:09:39, run 1 at 20:16:54" describes a 7 m 15 s gap that was **1 m 50 s**.
7. **Acceptance criterion 1 was vacuous and is now not.** Nine of the eleven self-check counters
   are incremented only inside verify gates that `gates_base.txt` pins off, so "11/11" has been
   2/11 since session 74. `guards.py` now prints the reachable and unreachable sets separately, and
   `vfy80a` (§6) armed one.

---

## 3. What the statistics should be

The A/A control `aa78a` calibrates all four candidate statistics and is clean on every one
(+24.8 µs/flip, +12.4 fragment-free, +0.036 % per draw, **+10.1 ± 25.4 µs** on a nominal
5040-draw frame).

| article | published µs/flip | per-draw × 5040 draws/frame |
|---|---:|---:|
| `pfcap` 192 → 1024, same code, 3 runs | −452.8 [−628.0, −277.5] | **−483.6 [−656.3, −310.9]** |
| `dapin` 0xffff → 0x5555, 2 runs | −718.6 [−1128.4, −308.7] | **−738.2 [−982.7, −493.6]** (46 % narrower) |
| `pfhint` 0 → 1, 10 runs | −766.9 [−1106.1, −427.8] | −799.6 [−1159.4, −439.9] |

**Both shipped figures survive the work-normalised restatement and `dapin`'s interval narrows.**
And the most stable restatement of a gate is as a class shift: on the record `pfhint` removes
**45.7 % [37.6 %, 52.8 %]** of 3-vblank flips at CV 20.0 % against 62.0 % for µs/flip.

---

## 4. The block — twelve runs, pre-registered

### 4.1 The design and the one declared change

Six blocks of two, one S (CPU sampler on) and one N (`--no-cpuclk`) each, **with forced
orientation balance** — three blocks lead with S and three with N — so a linear drift cancels out
of the S−N contrast by construction. Which three lead with S was drawn by
`random.Random(0x4724bf81)` (the first 8 hex of `sha256(gates_base.txt)`, a value fixed by the
harness and unchooseable) shuffling `["S"]*3+["N"]*3`; two auditors reproduced the draw.

**Declared, because hiding it would be worse:** an earlier draw under a design that shuffled each
block independently put N first in 5 of the 6 blocks (p = 6/64 = 0.094), leaving a within-block
drift confounded with the contrast. The **design** was changed to force orientation balance —
before any run, for that stated reason, and not because of any result. The discarded draw is kept
at `pred/order_discarded_unbalanced.txt`.

Every run is an exact replication of `pfh78d` / `pfh78f` / `nos79a` / `nos79b`:
`KYTY_GATE_SCHEDULE=30+1800:pfhint=0|pfhint=1`, ABBA, `--hold 300`, `gates_base.txt` unmodified
(all twelve carry 99 identical assignments, verified), guest args `-lvl underwater_aerial_garden`.
**No re-takes, no optional stopping**, twelve runs whatever they read.

### 4.2 The twelve

| tag | S/N | valid | B1 | B2 ×5040 | V1 arm0 | V1 arm1 | V5 | E | ±2SE | V4 | frag % |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `nos80a` | N | void | 32 473.2 | 32 565.7 | 11.326 | 4.482 | 0.396 | −1292.2 | 114.9 | −163.0 | 0.617 |
| `smp80a` | S | void | 32 809.9 | 32 613.9 | 12.036 | 7.025 | 0.584 | −811.9 | 117.8 | −83.7 | 0.181 |
| `smp80b` | S | void | 33 419.9 | 33 153.7 | 14.788 | 7.750 | 0.524 | −1129.1 | 132.6 | −73.4 | 0.151 |
| `nos80b` | N | **VALID** | 32 654.8 | 32 645.1 | 10.497 | 3.121 | 0.297 | −1343.5 | 75.3 | −146.4 | 0.219 |
| `smp80c` | S | **VALID** | 31 643.4 | 31 769.9 | 1.022 | 0.727 | 0.712 | −220.2 | 92.0 | +4.4 | 7.278 |
| `nos80c` | N | **VALID** | 31 798.1 | 31 879.6 | 1.103 | 0.732 | 0.663 | −240.9 | 86.9 | −10.6 | 6.817 |
| `smp80d` | S | void | 33 326.7 | 33 232.6 | 12.619 | 6.405 | 0.508 | −1080.3 | 198.8 | +16.3 | 1.186 |
| `nos80d` | N | **VALID** | 31 596.1 | 31 729.8 | 1.237 | 0.644 | 0.520 | −148.9 | 87.3 | −2.0 | 7.478 |
| `nos80e` | N | **VALID** | 31 435.9 | 31 566.6 | 1.089 | 0.560 | 0.514 | −134.2 | 87.7 | −22.3 | 8.556 |
| `smp80e` | S | void | 32 128.6 | 32 252.5 | 7.526 | 2.463 | 0.327 | −880.2 | 105.6 | −127.7 | 0.451 |
| `nos80f` | N | void | 32 902.0 | 33 003.3 | 13.423 | 4.348 | 0.324 | −1629.3 | 115.4 | −196.6 | 0.267 |
| `smp80f` | S | void | 33 137.0 | 33 347.9 | 13.423 | 7.004 | 0.522 | −1194.3 | 159.3 | −91.4 | 1.147 |

All 120 cells were re-derived independently by two auditors with their own parsers: **0
mismatches**. Acceptance: **guards check 2 PASS and check 10 PASS in all twelve**; arming proved in
all twelve (arm 0 `pf_l1` 0.30–0.40 per frame on the settled window against `da_hit`
8621.0–8637.1; arm 1 `pf_l1` = `da_hit` to **0.0047 %**); criterion 4 cross-check gaps
**+0.0013 … +0.0109 pp** against a 0.05 pp limit on the five valid runs; the bracketing timer
`da_take_us` moved in all twelve. **guards check 6 FAILS in `smp80c`, `nos80c`, `smp80d`,
`nos80d`, `nos80e`** — four of the five area-valid runs; `nos80b` passes it and passes guards
overall.

### 4.3 The pre-registered tests and the verdict

Six within-block S − N differences, paired t on 5 df, with the exact 2⁶ = 64 sign-flip permutation
beside it:

    B1  primary     +600.90 us   95 % CI [ -77.09, +1278.88]   t = +2.279   paired-t p = 0.0717   exact p = 0.0625
    B2  co-primary  +496.76 us   95 % CI [-104.37, +1097.89]   t = +2.125   paired-t p = 0.0870   exact p = 0.0938
    V1  arm-0 3-vbl   +3.79 pp   95 % CI [  -0.99,    +8.57]   t = +2.038   paired-t p = 0.0970   exact p = 0.1250
    Welch 6 v 6 on B1: +600.90, t = +1.567 on 9.8 df

`pred/01` rule 1 requires the same sign, **both** |S − N| > 400 µs **and** the paired t two-sided
p < 0.05. The first three hold; the fourth does not. Rule 2 (both < 200 µs) does not hold.

> **VERDICT: NOT RESOLVED**, in the pre-registered word. `pred/01` rule 3.

**A one-sided test would have fired rule 1 (p = 0.0358) and is NOT licensed**: `pred/01` writes
"two-sided" twice, states rule 2 on |S − N|, and holds P1.2 at p = 0.55 — a declaration of near
ignorance about the direction. The headline turned on exactly this pre-registered choice, which is
why it could not be revisited afterwards.

**The convergence, reported as a separate statement and not as a result.** FACTS s79 §2.3's
rung-matched 14-run screen gave **+674.9 µs**; this independent randomised block gives
**+600.90 µs**. Two estimates from disjoint designs agreeing at ~+600–675 µs, neither reaching
p < 0.05.

---

## 5. What the block's audit took back

Four auditors re-derived it and twelve adversaries attacked. The load-bearing corrections:

1. **The p I first reported was the wrong statistic.** `pred/01` §5 rule 1 names **the paired t**
   two-sided p; the first draft reported the **permutation** p (0.0625). The paired-t p is
   **0.0717** (B1) and **0.0870** (B2). The verdict is unchanged; the number is corrected. This is
   the same class of defect as session 78's `t = +0.45` substitution, committed in the session that
   catalogued it.
2. **The exact test at k = 6 is a 6-of-6 sign test.** Its two-sided p can only take the values
   2/64, 4/64, 6/64…, so at α = 0.05 the rejection region is the single most extreme arrangement:
   rejection requires all six block differences to share a sign, and all magnitude information is
   discarded. Block 3's difference (−154.71 µs, 11× smaller than block 4's +1730.60) makes
   rejection impossible regardless of the other five. Its maximum power against a true 675 µs
   effect is **38 %**.
3. **The block was underpowered as designed.** Observed within-block difference sd
   **σ_d = 645.94 µs**, 95 % CI [403.2, 1584.3]. Realised power at δ = 675 is **0.541**, and only
   known to lie in **[0.14, 0.90]** given the CI on σ_d. 80 % power needs **10 blocks (20 runs)** at
   δ = 675 and **23 blocks (46 runs)** at δ = 400 — the rule's own decision threshold. `pred/01`
   P1.4's "roughly 60–70 % power" was optimistic. Blocking did work: it removed **53 %** of the
   difference variance.
4. **The primary endpoint measures composition, and the price component has the opposite sign.**
   Shift-share on B1 across the twelve: **mixture +1054.10 µs (175 %), price −453.20 µs (−75 %)**.
   The pre-registered class-fixed readout V3 gives S − N = **−493.26 µs** — opposite in sign to B1
   — with corr(B1, V3) = **−0.8139**. Restricting to same-state blocks gives **+295.5 µs**, below
   rule 1's own threshold. **So the sampler contrast's sign depends on the statistic**, and that,
   not the p value, is the substantive result of the block.
5. **P2.4 is a HIT as sealed and worth almost nothing as evidence.** `pred/02` P2.4 names the
   Pearson correlation over the area-valid runs; realised **−0.9952**, so it is scored a hit. But
   `nos80b` carries leverage **h = 0.9996**, removing it flips the sign to **+0.4973**, the
   Spearman is **−0.5000**, and the exact permutation p over 120 relabellings is **0.1417**. The
   out-of-sample test of §1.3's −0.9759 **did not succeed on its own pre-registered population**.
6. **The twelve-run version is a two-cluster contrast.** corr(effect, arm-0 3-vblank share) over
   all twelve is −0.9145, but within the eight HIGH-state runs it is **−0.3569, exact p = 0.3824**,
   and within the four LOW-state runs +0.4973. Effective degrees of freedom **1**, not 10.
   **This does NOT carry over to the record population**, where the same split gives −0.9689 and
   −0.9502 inside the halves, both at the permutation floor, with no gap wider than 3.21 pp (§1.3).
7. **P1.9 survives only as a rank test.** corr(fragment share, effect) = +0.9920 over the five
   valid runs, but the honest statement is that the five rank-order perfectly: Spearman **+1.0000**,
   exact two-sided rank p = **2/120 = 0.0167**, which is that test's floor.
8. **V5 was quoted over void runs, which `PLAN.md` §1 forbids.** `pred/01`'s admission rule exempts
   B1 and B2 *because they are single-arm*; V5 is an arm contrast. **Restated on the five
   area-valid runs: geometric mean 0.5185, 95 % CI [0.3385, 0.7941] — the gate removes 48.2 %
   [20.6 %, 66.1 %] of 3-vblank flips**, an interval 3.3× wider than the twelve-run one.
   P2.7 and P2.8 hit on both populations, so their scoring stands.
9. **Two further protocol deviations, neither material.** B2's fragment median is
   `statistics.median` over all CSV rows rather than `guards.py`'s nearest-rank p50 over its scoped
   window — it moves B2 by 0.19 µs and two flips in one run. And `pred/01`'s "at least 20
   rung-matched arm-0 blocks" admission is **printed, not enforced**; non-binding here (the minimum
   over the twelve is 43) but a run with 1–19 blocks would have been admitted silently.
10. Minor: my arming band "`da_hit` 8620–8635" is **8619.31–8637.12** depending on window;
    `cond80.csv`'s `rung_hi_pct` column conflates the true DRS rung (`rt_kpx/rt_att > 2600`) with
    cheap frames and reads 0.5–11.8 % where the programme's own gate reads **0.00 %** in 15 of 21
    runs; `cond80.py` omits 16 two-arm runs whose roots predate s75; "reorders the runs completely"
    is Spearman **+0.5394**; `draws < 4500` is a mixture of two populations and `dt < 20 ms` is the
    clean discriminator.

---

## 6. The validity gate is a DRS-rung filter, and it selects on the effect

This is the most consequential thing the block produced and it was not what it was looking for.

**Only two DRS rungs are occupied**, attachment-weighted over all 344 816 settled flips of the 50
two-arm runs on disk: **low 2009.9 Kpx/attachment, high 3208.7 Kpx/attachment, gap +59.64 %**. So
the whole-arm split the gate judges is ≈ Δ(high-rung attachment share) × 0.5964, and **to breach
the 1.0 % gate the arms must differ by ≥ 1.68 pp of high-rung attachments**.

**The vblank class cannot do it.** A 3-vblank flip carries `rt_kpx/rt_att` only **+0.315 %**
[+0.303, +0.327] different from a 2-vblank one (24 runs with zero high-rung flips in arm 0). The
largest class-composition term anywhere in 50 runs is 0.52 pp, and isolating the k ≥ 3 class on the
13 DRS-inactive `pfhint` runs gives **−0.0331 … −0.0012 pp** against class shifts up to −11.2 pp —
**30× below the gate**. `nos80b` settles it alone: the second-largest 3-vblank class shift in the
record and a machine-zero split (+0.001 %), VALID.

**"Area-valid" is empirically "DRS never left the low rung."** On the `pfhint` population:
13 VALID / 0 void where the high-rung share is < 0.5 %, against 2 VALID / 19 void where DRS
climbed — **Fisher exact p = 1.13 × 10⁻⁷**; on this block's twelve, 5/0 against 0/7, p = 0.0013.
(Caveat raised on audit and accepted: VALID is *defined* by the split in 50 of 50 runs, so the
VALID↔split correlation is partly definitional; the rung↔class separation is not.)

**The mechanism — MEASURED in part, INTERPRETATION as a chain.** In **21 of 21** `pfhint` runs
where DRS was active, the `pfhint=1` arm carries the **higher** high-rung share, and
corr(ΔHR, |effect|) over those 21 = **+0.6945 [+0.375, +0.866]**. The high rung costs
**+12.97 % [+12.33, +13.60]** of `gpu_busy_us` and **−0.19 % [−0.36, −0.02]** of `cpu_gpu_us`
(arm-0, fragments excluded, k = 2 only, 25 runs). The chain: the scene is CPU-bound → `pfhint=1`
cheapens the CPU frame → the frame finishes sooner → DRS sees GPU headroom and climbs → arm 1 draws
more area → the split opens → the run is voided.

**The sharp consequence: the gate voids a run for a rung-mix difference worth about −60 µs on a
31 000 µs frame — nearly orthogonal to the endpoint it protects — while being strongly
proportional to the effect under test.**

**What it does to the published record:**

    this block   VALID (5) mean -417.6  sd 519.6   void (7) mean -1145.3  sd 272.1
                 VALID - void = +727.8 us  95 % CI [+106.0, +1349.6]  Welch t = +2.86 on 5.6 df
                                                              exact permutation p = 0.0152
                 survives inside each arm: +798.9 us in S, +993.9 us in N (so not a sampler artefact)
    whole record VALID (15) -650.2   void (19) -888.4
                 VALID - void = +238.2 us  95 % CI [-93.6, +570.0]  -- CONTAINS ZERO, NOT ESTABLISHED
    pooled pfhint, area-valid only, 15 runs : -650.4 [-933.1, -367.8]  tau 508  I2 99.2 %
    pooled pfhint, every run, matched pairs : -781.6 [-951.4, -611.8]  tau 481  I2 98.8 %

**The direction is towards SMALL effects: the published population understates by about 20 %.**
Within this block by +727.8 µs, i.e. the quoted set reads **2.7× smaller** than the discarded one.
Across the record the contrast contains zero and is **NOT ESTABLISHED**. Session 78 declared this
refuted; session 79 said it holds; session 80 gives it a mechanism and a size, and the size is
established only within this block.

---

## 7. The entry hangs

Two attempts hung: `smp80c` attempt 1 and `smp80f` attempt 1, both `GpuHangAbort: role=4`, both
retried successfully at the next attempt. The failed attempts are preserved
(`log_smp80c_a1.txt`, `log_smp80f_a1.txt`, 16 MB each) and are used as measurements nowhere.

**There are exactly four hang events in the whole on-disk record and they are one signature.** All
four abort lines are 159 bytes with the same field set and order; all four have `role=4`,
`after=8s`, `submit_backlog=0`, `record_backlog=0`, `acopy_pending=0`, an equal `acopy` triple and
**`requested − known = 1`**; all four end at
`masterSemaphore.cpp:118 "GPU stopped completing submissions"`; all four died at flip **188–202**,
**1–3 flips after the level-entry stall frame**, with **0 `GateArm:` lines** — no schedule arm had
ever been applied. `master` differs only in bits 16–23, sharing the low 16 bits `0x2a10` every
time.

**The GPU lagged; it was not ahead.** `current` is `MasterSemaphore::m_current_tick`, the host's
next-tick allocator, so the GPU was behind by **92 / 91 / 93 / 91** submissions. This confirms
session 78's correction and means FACTS s77 §7's reading is inverted.

**Both hangs fell on sampler runs, and that is evidence of nothing.** Under the randomisation
actually used (20 equiprobable assignments) "both hung slots carry S" has probability **6/20 =
0.30** — tied with "both carry N" as the most likely outcome. Historically: **60 entry attempts
since session 76, 4 hung = 6.67 %**; with the sampler 2 of 30, without it 2 of 30 — **identical to
three decimals**, and two of the four happened before `cpuclk.py` existed. Fisher two-sided 1.0000.

`pred/01` P1.1 ("all twelve enter, no entry hang", p = 0.80) is a **MISS**.

**Correction to the record found on the way:** session 76's report states all eleven runs entered
at the first attempt; its own `fsl76a.json` records attempt 1 as `GpuHangAbort`.

**Next measurement:** `KYTY_GPU_CHECKPOINTS=1` with `KYTY_GPU_HANG_ABORT_S=0`, which prints
`GpuCheckpoint breadcrumb (last started, never completed)` — the stalled operation by name. The
window is flips 189–202, so an instrumented attempt can be abandoned at flip 250 and costs ~25 s
rather than 320 s; at 6.67 % a 30-attempt block is ~15 minutes and would be expected to catch two.

---

## 8. The prediction scoreboard, honestly

**Twenty-three predictions were sealed** (P1.1–P1.13, P2.1–P2.10). **20 hit, 3 missed.**

**The three misses:** P1.1 (two entry hangs), P1.4 (the primary p, 0.0717 against < 0.05), and
**P2.10** — the class-fixed arm-0 price was predicted to span less than 1500 µs and spans
**1965.4 µs (31 042.9 … 33 008.3)**. P2.10's miss is the informative one: **the state is not only
class mix**, since the price at a fixed class still varies 6.3 % run to run. Audit adds that the
class-fixed price is itself **two-valued, 1758 µs apart, with 31 µs of scatter inside the low
state** — 96.6 % of its variance is between two regimes.

**And 20 of 23 is worth nothing as calibration**, for reasons the audit computed rather than
asserted: the exact Poisson-binomial probability of ≥ 20 hits under the author's own stated priors
is **0.0150**, i.e. the scoreboard beat its own priors, which means the bands were drawn too wide,
not that the predictions were good. About six lines carry information and three of those are the
misses. Named as carrying nothing: **P2.1, P2.2, P1.2, P1.3, P1.5, P1.11, P1.12, P1.13, P2.6**;
P1.8 and P2.3 are one measurement in two forms, as are P2.9 and P1.3.

**The predictions that discriminated were P1.4, P2.4 and P2.10.** P1.4 came out against the
hypothesis. P2.4 was scored a hit by its own words and is worth nothing on inspection (§5.5).
P2.10 came out against the session's own model and is the most useful line on the board.

---

## 9. What the audit forced

Twenty-eight agents on the zero-run analysis and sixteen on the block; every headline re-derived by
an independent parser and attacked through an arithmetic, an inference and a protocol lens. The
re-derivations returned **0 mismatches on all 120 block cells, all three paired tests, the Welch,
V5, the validity verdicts, the arming, `vfy80a` and all twelve `<tag>.json`**. The retractions are
§2 (against the record) and §5 (against this session). The ones that cost this session most:

* **The permutation p was reported where the pre-registration named the paired t** — 0.0625 for
  0.0717.
* **P2.4's out-of-sample confirmation is one leverage point**, and the first draft presented
  −0.9952 as a replication.
* **V5 was pooled over void runs** in breach of a standing rule, and is 3.3× wider when it is not.
* **"The validity gate filters on the vblank class"** — my own framing — is **REFUTED**; it filters
  on the DRS rung, and the class association is a sibling through shared headroom.
* **"Work is unchanged" across the arms is false for a third time**, now in the class mixture:
  the arms differ by +0.81 / +3.21 / −4.01 pp of 1/2/3-vblank flips at t = +5.28 / +3.72 / −4.51.
* Auditors were themselves refuted on: "all five area-valid runs carry guards FAIL" (**four**;
  `nos80b` passes), the sign of the criterion-4 gaps (**positive**), the scoreboard count (**23**,
  not 22), the `masterSemaphore` abort branch (it calls `ReportGpuSubmissionHistory` too), the
  `pfhint` population size (**38** runs carry that schedule, not 34), and several fragment
  statistics in §6's first draft.

---

## 10. Not closed, and what would settle each

1. **The sampler as a contributor — NOT RESOLVED**, and now with a size and a power curve.
   *Next:* the same design at **10 blocks (20 runs)** for 80 % power at δ = 675, and the primary
   endpoint stated as the **class-fixed price**, not the per-flip mean, because §5.4 shows the two
   disagree in sign. The p to quote is the paired t's.
2. **Which way the causation runs between the missing render-pass block and the one-vblank
   present** — NOT MEASURED, and the simple content→time story is refuted by the arithmetic
   (§1.2). *Next:* `KYTY_GPU_TIME` or `KYTY_DUMP_FRAME` on a single `rpa_a5 == 0` flip, to see
   whether the guest's PM4 stream for that frame actually lacks the five-MRT passes.
3. **The validity gate selects on the effect** (§6). *Next:* a rung-conditioned criterion —
   restrict every run to low-rung flips before the split is computed — applied to the whole record,
   and the shipped figures restated under it. This is a proposal for session 81, not a substitution
   made here.
4. **The guest-clock pacer** — one ABBA with `KYTY_AUDIO_SYNC=0`, no code, no rebuild (§1.5).
5. **`dapin`** — still two runs, still not a pure placement contrast, still owes an explanation of
   its `gpu_busy_us` rise. Its work-normalised figure is **−738 µs [−983, −494]**.
6. **The entry hang** — one signature, four instances, `KYTY_GPU_CHECKPOINTS=1` names the stalled
   operation at ~25 s per attempt (§7).
7. **What sets the state at process start** — **nothing clears the multiplicity screen.** Best raw
   p = 0.0062 (`gpuclk` power over entry seconds 40–60), best family-wise p = **0.0736**, and that
   candidate is the sampler itself. **No candidate measured before flip ~300 reached |r| = 0.50.**
   The state is established between flip ~150 and ~450, i.e. wall-clock ~11–22 s from launch,
   straddling level entry. Nothing on disk resolves it finer.
8. **The C-state screen cannot be run where it matters**: `cpuclk_*.csv` exists only for sampler
   runs, so it is structurally unable to see the two lowest-baseline runs in the record.
9. Session 78's untouched items: the guest-line prefetch population's share; `b_buf` vs `b_tex`;
   the prefetch bitmask knob; the sum of the shipped gates; M4's serialiser; the dead gate
   `dawitfb`.
10. **No acceptance run was taken.** No source file changed, so it would have been one more draw of
    the state. The base of record remains `acc78a` on the settled window: **32 789 / 13 497 /
    34 956 / 28.61 FPS**.

---

## 11. The arithmetic

| article | measured | state |
|---|---|---|
| frame time is vblank-quantised | 1/2/3 vblanks carry 4.31 / 89.65 / 6.03 %; `p1+2p2+3p3 = mean_dt/VB` to 0.0000 | **ESTABLISHED** |
| `cpu_gpu_us`/flip is a frame-time statistic | r = 0.954–0.9986 on `dt_us` in 36 of 36 arm fits | **ESTABLISHED** |
| share of the published `pfhint` effect that is class mix | **90.6 %**; class-fixed effect −52.9 µs, sd 40.6 | **MEASURED** |
| the swing is headroom | corr(effect, arm-0 3-vblank share) = **−0.9759**, holding inside both halves | **a screen, ten points, monotone** |
| the baseline as conditioner | **−0.878 → −0.234** under a composition filter; `dt_us` holds at −0.977 | **the published conditioner is wrong** |
| the sampler as a contributor | B1 **+600.90 µs**, paired-t p = 0.0717; class-fixed price **−493.26 µs** | **NOT RESOLVED, and sign-dependent** |
| the validity gate | is a DRS-rung filter; voids on ~−60 µs of endpoint, selects on the effect | **MEASURED**; the bias size only within this block |
| bias of the published population | block **+727.8 µs [+106.0, +1349.6]**; record **+238.2 [−93.6, +570.0]** | block MEASURED, record NOT ESTABLISHED |
| `pfcap` 192 → 1024, work-normalised | **−484 µs [−656, −311]** | 3 runs, shipped, survives |
| `dapin` 0xffff → 0x5555, work-normalised | **−738 µs [−983, −494]** | 2 runs, not a pure contrast |
| `pfhint` as a class shift, area-valid runs of the block | removes **48.2 % [20.6 %, 66.1 %]** of 3-vblank flips | 5 runs |
| the entry hang | one signature, 4 in 60 attempts; sampler-independent | **UNEXPLAINED** |
| acceptance criterion 1 | `da_cl_bad` = 0 over **113 133 663** predicate evaluations | **no longer vacuous** |

**The honest statement.** Sessions 78 and 79 measured a swing they could not explain and
conditioned it on a number that turns out to be mostly a mixture: the emulator presents on a
vblank grid, so the "CPU price per frame" the programme has watched for three sessions is
frame time with the idle removed, and nine tenths of the gate effect it has been quoting is frames
moving out of the three-vblank class. The twelve-run block on the sampler returned NOT RESOLVED at
p = 0.0717 with about half the power it needed, and its own audit found the endpoint's price
component pointing the other way. What is new and solid is the mechanism, the arithmetic that ties
the swing to headroom, and the discovery that the gate deciding which runs may be quoted selects
against exactly the runs where the effect is largest. **60 FPS still needs about 15 ms off the CPU
path — and the programme now knows that the number it has been calling CPU time is not it.**
