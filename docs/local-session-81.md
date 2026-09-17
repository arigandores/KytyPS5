# Session 81 — local report

**Single source of truth for session 81.** Every number here was computed this session from a named
file. Where a number is an interpretation it says so; where something was not measured it says NOT
MEASURED.

Tree: `merge-upstream`. **No source file was changed and nothing was rebuilt.** Every run sits on
session 77's installed binary
`39306a9f95db805aec21d7909bbadf9ec0d115316a013e84d2bc77f8326d9dbf` (23 563 776 bytes), whose
`.text` is `90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0`, byte-identical to
`79680f59` and therefore to every `pfhint`, `pfcap` and `dapin` run quoted below.
`C:/kyty/build/install/kyty_emulator.exe` hashes to the same value.

Harness `C:/kyty/s81`, ported from `C:/kyty/s80` and **verified before use** by two independent
re-derivations of published tables: `a80_block_analyse.py` reproduces FACTS s80 §4.2's twelve-run
block table cell for cell, and `arms.py` reproduces FACTS s79 §3's thirteen-run table to the printed
digit. All `area_<tag>.csv` were re-derived mechanically (`build_areas81.py --verify`): **68 identical to
the copy an earlier session wrote, 0 differing, 46 with no earlier copy — 23 of those this
session's own runs**, and all 33 primary-stratum CSVs are inside the 68. *(An earlier draft wrote
"91 identical" by counting CSVs this session had just written itself; corrected on audit.)*
`gates_base.txt` is **1092 bytes, 99 names, sha256 `4724bf81…f8c4f`**.

**Pre-registrations, all six sealed before the work they cover, written in place so `mtime ==
ctime`, hashed into `a81_prereg_manifest.json` before the first number and into every `<tag>.json`
of the block:**

    pred/01_rcv.md          29987 B  sha256 1353caf4d4eb31ba3914a43291f08e1e05caf1ce48bf73362c6daed115b59f9a
    pred/02_onevblank.md    10082 B  sha256 421909d74de3e9a3...
    pred/03_sampler10.md    13007 B  sha256 716ec1bdf0b791cb913f946082eca6d8ee0e1882224e6426cc61dca9f5fe5d73
    pred/04_pacer.md         7121 B  sha256 7be076bfe8ee1878...
    pred/05_hang.md          6526 B  sha256 600fc2facd2c399e...
    pred/06_dapin.md         5346 B  sha256 26f3537758ea65ce...
    pred/order.txt            678 B  sha256 edb810d034fd983692d50342ff8f35227dae80a699969f01be220b2ad8c4ec5c

`mtime − ctime` is 0.000–0.012 s on all seven. `rcv81.py` refuses to run unless `pred/01` still
hashes to the manifest value and prints that hash in the header of every table; its population is
parsed out of the sealed §5 text, so this session's twenty new runs cannot silently join it. What
was on screen before the seal is declared in `pred/01` §0 and listed command by command in
`pre_seal_note.md`; three predictions that compare against numbers already on screen are marked
**half-blind** and excluded from the calibration figure.

---

## 0. In one sentence

**The criterion the brief proposed cannot be built on this record, and the four things found on the
way are worth more than it would have been**: the validity gate judges a *mixture* statistic while
the two arms render at the same size in all 33 runs (low mode −0.002…+0.083 % apart); **its bias is
now established prospectively** on twenty fresh runs, where the void set reads **−499.6 µs
[−903.3, −95.9]** more than the quoted set; **conditioning on the vblank class is conditioning on a
collider**, so the endpoint the brief named as the next primary is biased in opposite directions in
its two forms; the ten-block sampler design returned **NOT RESOLVED at −146.5 µs, p = 0.55**, with
session 80's +600.90 not replicating; and the entry hang has an operation class at last —
**sixteen `EopWrite` records from one submission**, caught twice in thirty instrumented entries at
exactly the historical 6.67 %. Meanwhile the gates themselves hold up and get smaller: on matched
pairs, where the arms do the same work, `pfhint` buys **−876.8 µs of frame time (+0.76 FPS)**,
`pfcap` −456.5 (+0.40) and `dapin` −893.9 (+0.86), against an A/A control of −7.0 ± 91.6 — and 60
FPS needs 18 300.

**This report was rewritten after an independent audit** (five agents re-deriving every headline
with their own parsers, five attacking, one scoring the board) that returned four fatal findings
against it. Every retraction is in §2, and three of them are against claims this session made
itself.

---

## 1. The zero-run analysis

Everything in §1 is computed from `area_<tag>.csv` and `ft81/ft_<tag>.csv`, mechanical derivations
of logs already on disk, under `pred/01_rcv.md` and `pred/02_onevblank.md`, both sealed before the
first number.

### 1.1 RCV is refuted by its own pre-registered rule, and that is the finding

`pred/01` §6 rule 5(b) retires the criterion if **more than 7 of the 33** primary-stratum runs are
RCV-UNCLASSIFIABLE. **Eleven are.** Rule 5 is evaluated first by the sealed text, so no verdict
under rules 1–4 is reported as a result of this session.

    published VALID  x RCV VALID           14
    published VALID  x RCV VOID             3   nos79a pfh77a smp80c
    published VOID   x RCV UNCLASSIFIABLE  11   nos80a nos80f pfh77c pfh78a pfh78e smp79d smp80b
                                                smp80d smp80f wit78b wit78c
    published VOID   x RCV VOID             5   smp79a smp79c smp79e smp80a smp80e
    published VOID   x RCV VALID            0

**Every one of the eleven is unclassifiable for the same reason: the arms' low-mode retention
differs by 10.2 … 22.1 pp.** When DRS climbs in the gate-ON arm, that arm's low-mode flips are a
different and much smaller sample, so there is nothing left to compare at a fixed mode. **RCV
admits no published-void run in the 33-run primary stratum, so its bias contrast has an empty
treatment group and rule 1 is NOT COMPUTABLE.** The information the brief hoped to condition on is
not in the data.

Three qualifications the audit forced, all of which sharpen rather than soften the verdict:

* **The retention gap *is* ΔHR** (r = +0.999 over the 33 runs; the eleven unclassifiable runs are
  exactly the eleven with |gap| > 10 pp), so rule 5(b) is a statement about how DRS responds to the
  gate, not about RCV's construction. **The verdict does not turn on the 10 pp cap**: the
  unclassifiable count is 15 at 5 pp, 14 at 8, 11 at 10, 10 at 11–13, 8 at 15 and 6 at 16, so
  "> 7" holds for every cap up to 15.
* **Out of sample RCV does readmit one run.** On the twenty fresh runs of §4, `nos81j` is
  published-VOID (whole-arm split +1.700 %) and RCV-VALID (restricted split +0.012 %, restricted
  work +0.141 %, 108/112 pairs matched, retention gap −3.03 pp) — and it carries **the block's
  largest effect, R1 = −1605.9 µs**. That is the only observation the record contains of what rule
  1's treatment group would have looked like, and it points the same way as §5.
* **The fragment exclusion is itself differential post-treatment selection**, of exactly the class
  `pred/01` §3.4 refuses to make inside an estimator: the arm-1 fragment share exceeds arm-0 in
  **31 of 33 runs, mean +0.438 pp**, so dropping fragments drops arm-1 flips preferentially. That,
  not an implementation discrepancy, is why rule 5(c)'s self-test fires: the three runs it names
  have **zero** HIGH flips, so the fragment rule is the only thing that can move them
  (`nos79a` work +0.253 → +0.550 %, `pfh77a` −0.028 → +0.583 %, `smp80c` +0.033 → +0.860 %, against
  a 0.5 % limit). It strengthens 5(b): the criterion fails on its own rationale. *(Noted against
  myself: 5(c) is written both as a refutation trigger and as "reported not fatal" in the same
  sentence of the sealed file. It is reported as fired; 5(b) is the unambiguous one. An earlier
  draft wrote the work move as "+0.12 % to +1.48 %" — neither endpoint is on disk; the three real
  moves are above.)*

RCV is also *stricter* than the published gate, not more permissive: three published-valid runs
become RCV-VOID and, in the primary stratum, none of the void ones are readmitted.

**Out of sample, on the twenty fresh runs of §4: 9 RCV-VALID, 7 RCV-VOID, 4 UNCLASSIFIABLE.**
`pred/03` P3.9 predicted ≥ 16 RCV-VALID: **MISS**, in the same direction as rule 5(b).

### 1.2 The two modes are a DRS resolution step, and the arms render at the same resolution

`pred/01` §2's discriminators over the 33-run primary stratum (fragments excluded before labelling):

    D1 attachment count, HIGH vs LOW   -5.4 % … +2.4 %   (mostly within +-2 %)
    D2 draws per flip,   HIGH vs LOW   -3.4 % … +1.1 %
    D6 HIGH episode length             median 11-40 flips, max 274

A resolution step multiplies area per attachment and leaves the attachment count and the work
alone; a flip-boundary artefact moves the denominator and cannot persist for tens of flips. **The
sealed reading returns *a DRS resolution step* (P1.14 HIT)**, and the twenty fresh runs of §4
reproduce it (D1 mean +0.58 %, max 3.65 %; D2 +0.25 %, max 1.89 %; median episode 20, minimum 10 —
P3.14 HIT). The same measurement on `ab67a` and `aa67a` — the two runs `guards.py check_area`'s
docstring cites for the opposite reading — gives D1 +2.25 % / +2.21 %, D2 +1.10 % / +1.16 %, median
episode 33 / 42 flips. **So the docstring's stated reason ("depending on whether the flip boundary
fell before or after the frame's big passes") is not supported by the data it names.**

**And the arms render at the same resolution in every run.** The attachment-weighted low mode
(`guards.py`'s own `wpct` at p5, the statistic its hard criterion is taken on) differs between arms
by **−0.002 % … +0.083 %** across all 33 runs — including the run whose published split is
**+11.28 %**. *(An earlier draft wrote the range as strictly positive; one run is −0.002 %, and
which run that is depends on p5 tie-handling. The claim — same size to under 0.1 % — is
unaffected.)* The published gate judges the whole-arm **mean**, which is a *mixture* statistic: it
measures how often each arm sat on the high rung, not what size it rendered.

`area_verdict.py`'s own docstring says the defect it fixed was "the THRESHOLD, not the
computation". It tightened `guards.py` check 3b's **advisory** 5 % limit on the draw-weighted mean
to a hard 1.0 % — and `guards.py` treats that statistic as advisory precisely because it is a
mixture. **The gate the programme has used since session 77 is a hard threshold on the harness's
own advisory statistic.**

### 1.3 What the gate is protecting, and what it is not

Declared exploratory under `pred/01` §7's discipline, and **restated after audit, which refuted the
first reading of it.**

**The price of a high-mode flip is NOT IDENTIFIED.** Inside one run and one arm, HIGH minus LOW
over the 17 runs carrying both modes:

    at k == 2, non-fragment      -43.1 us per flip (sd 61.4; per-run 2*SE 70 ... 140)
    unconditional                +123.9 us         (sd 305.2)
    at k >= 3                    +205.5 us         (sd 200.8)
    gpu_busy_us                  +12.68 % at k == 2 and +13.18 % unconditional - stable throughout

Only the CPU figure reverses, and it reverses with the conditioning: §1.4 establishes that k is a
threshold on the outcome, so the k = 2 price is itself conditioned on a descendant of the
treatment, and a per-flip endpoint is contaminated *unconditionally*, not at fixed k. The price is
also **positive in 6 of the 17 runs**. **So the sign of any mixture contamination is not
established**, and the first draft's "the high mode is cheaper on the CPU" is withdrawn.

**And the contamination in the quoted effect is zero, because the pair matching already removes
it.** The published estimator only ever reads adjacent blocks matched within 0.5 % on
`rt_kpx/rt_att`. Inside that matched-pair population the arms' high-mode share differs by
**+0.003 pp on average (−0.185 … +0.443 pp over the 16 void runs)**, i.e. **+0.00 µs** of mixture;
mechanically the high mode is +60.4 % of the low mode (3219.7 against 2007.7 Kpx per attachment),
so a 0.5 % area tolerance admits at most **0.83 pp** of intra-pair high-share difference and
**≤ 0.36 µs** of mixture, for any run, by construction. **The first draft's "the gate discards 16 of
33 runs to protect against five microseconds" is withdrawn**: the −5 µs was priced with the
whole-arm ΔHR (mean +13.48 pp over the void runs), which the estimator never sees.

**What the gate does protect against is the divergence between the pairs it keeps and the pairs it
drops**, and that is 10–100× larger than the mixture: over the 16 void runs, matched-pair R1 minus
dropped-pair R1 is **mean +72.0 µs, mean |Δ| 152.2 µs, maximum +804.6 µs** (`smp79e`, 102 matched
against 13 dropped). That is the honest quantity to weigh against the ≈ 500 µs the gate costs in
§5 — a real protection, an order of magnitude smaller than the cost, and measured on the same
population the gate acts on.

Session 80's §6 measured the high rung's cost as −0.19 % of `cpu_gpu_us`; this session finds that
number is conditioning-dependent and that its consequence for the quoted effect is nil. **What
survives is the gpu side**: a high-mode flip costs **+12.7 … +13.2 % of `gpu_busy_us`**, stable
across conditionings and replicating FACTS s80 §6's +12.97 %.

**The size of what the gate discards**, in this session's three statistics over the 33-run stratum
— in-sample, with the groups defined by a two-arm quantity downstream of the effect, so this
**sizes** the bias and does not establish it:

    published-VOID minus published-VALID   R1  -317.9 us  95 % CI [-605.0, -30.9]  Welch t -2.27
                                           R2  -310.0     [-597.8, -22.3]
                                           R3  -242.1     [-456.4, -27.7]
    mean high-mode share: VALID 0.36 %, VOID 35.07 %

FACTS s80 §6 gave the same contrast as **+238.2 [−93.6, +570.0]** over 34 runs and called it NOT
ESTABLISHED; on the machine-code-clean stratum of 33 it is **+317.9 [+30.9, +605.0]**. **§5 settles
it prospectively on twenty runs that did not exist when the hypothesis was formed.**

### 1.4 Conditioning on the vblank class is conditioning on a collider

**Declared exploratory: no sealed file covers this section** - neither `pred/01` nor `pred/02`
names a within-class work contrast - and it was computed before run 1 of the block (`PLAN.md` S2),
so nothing downstream of it is contaminated. It is reported because it changes what two
pre-registered endpoints can mean.

The class `k` is a threshold on frame time; frame time is the outcome. **Within k = 2 the gate-ON
arm carries more draws in 33 of 33 runs: +1.94 % on average, +0.20 ... +3.58 %**, while over all
flips the same arms differ by **+0.29 %** - a Simpson signature. The within-class difference tracks
how many frames moved out of k >= 3 (mean spill +4.58 pp):

    corr(k>=3 spill pp, within-k2 draws difference %) = +0.9634
        Spearman +0.9502, permutation p < 0.0001, max leverage 0.122, jackknife [+0.9599, +0.9690]
    within-state: low half +0.9377, high half +0.8592; the 15 DRS-inactive runs +0.9705, 15 of 15
        positive - so it is not a DRS-mixture artefact
    partial r given the run's own effect: +0.3093

**The raw +0.9634 is a consistency check and not evidence**, because nearly every run-level
quantity in this record correlates about 0.96 with every other (r(spill, R1) = -0.981,
r(within-k2, R1) = -0.9663). The quantitative statement that does carry information is the
no-free-parameter reconstruction: **the spill accounts for about 78 % of the within-k2 draws
difference** (predicted +1.51 % against an observed +1.94 %), and the residual of about +0.42 pp is
not closed.

Both class-fixed readouts inherit the selection, and the **mechanism is arithmetic**: within k = 2
the marginal cost of a draw is **3.087 us** against an average of **6.375 us**, and the treated
arm's k = 2 flips carry **+94.6 draws**. The per-flip form charges those draws at the marginal cost
(+292 us *towards* zero) and the per-draw form at the average (-311 us *away* from it), which
reproduces the two published-looking numbers from one underlying work-matched price of about
-360 us:

    class-fixed PER FLIP         mean  -65.5 us (sd 48.2)
    class-fixed PER DRAW x 5040  mean -676.0 us (sd 326.4)
    corr(within-k2 draws difference, per-draw form) = -0.9938  -- but this is ~92 % ALGEBRA: the
        draws difference sits in the statistic's denominator, and the empirical slope
        (-350.5 us per 1 %) is within 9 % of the arithmetic identity's -321.3.  The informative
        per-flip correlation is -0.68 ... -0.75 depending on class weighting.

**This is the mechanism behind FACTS s80 S5.4's unexplained sign disagreement** between B1
(+600.90) and V3 (-493.26) at corr = -0.8139. **Neither named class-fixed form is unbiased.** A
within-class estimator that also fixes the work - an ANCOVA of `cpu` on `draws` with an arm dummy,
within k = 2, per run - reads **-396.3 us (sd 228.0)**, converging with S1.5's independently
derived draw-count-matched -408/-419; **whether that is unbiased is NOT MEASURED.** The brief's
S3.2 instruction was nevertheless carried out - the block's primary endpoint C1 is the class-fixed
price and S4 reports it - and this section says what that number can and cannot mean.

### 1.5 Where the effect goes, and what a draw-count-matched figure is worth

**This section replaces two claims this session made and then refuted itself** (S2.8, S2.9).

**What the gates buy, on the estimator the programme actually uses.** On matched pairs the two arms
do the same work - draws per flip differ by **+2.8 per flip (+0.06 %)** over the 33-run stratum -
and:

    matched pairs, 33-run stratum   d_dt -876.8 us (sd 446.1)   d_cpu -847.6   d_gpu +25.2
                                    d_draws +2.8 per flip       -> 29.148 FPS to 29.912 (+0.76)
    the twenty fresh runs of section 4   d_dt -808.9 (sd 519.9) d_cpu -789.7   -> +0.72 FPS
    pfcap, 4 runs                   d_dt -456.5 (sd 67.3)       d_cpu -452.9   -> +0.40 FPS
    dapin, 3 runs                   d_dt -893.9 (sd 29.1)       d_cpu -713.4   d_gpu +206.8
                                                                               -> +0.86 FPS
    A/A, 6 runs                     d_dt   -7.0 (sd 91.6)       d_cpu   -2.8   -- the calibration

**In the pure CPU contrasts the saving converts into frame time nearly one for one** - `pfhint`
-876.8 against -847.6 (3 %) and `pfcap` -456.5 against -452.9 (1 %) - **and not in `dapin`**, which
pays +206.8 us of GPU and shows -893.9 against -713.4 (25 %). The A/A control reads zero on both.
That is the number the programme's goal is stated in, and it is the figure to quote.

**The draw-count-matched estimator, declared exploratory, and what it actually is.** Binning
non-fragment low-mode flips by `draws` (100-draw bins, both arms >= 20 flips, weighted by
min(n0, n1)) gives **-407.8 us (sd 234.0)** for `pfhint` against a plain per-flip difference of
**-788.8** over the same flips. **Five things the audit established about it, all of which limit
what it may be read as:**

* **It bins on the class.** Median bin k-purity is **1.000** over the 343 bins with >= 40 flips,
  and restricted to k = 2 flips alone it reads **-396.7** of the -407.8 - so it performs exactly
  the conditioning S1.4 has just shown inadmissible, and the whole figure is the within-class draw
  adjustment. It is one point inside the bracket S1.4 identifies at [-65.5 per flip, -676.0 per
  draw]; the ANCOVA at -396.3 lands in the same place.
* **It is draw-count-matched, not work-matched.** At the same draw count the treated arm is doing
  measurably more of every other render counter: `swbar` +4.8 %, `rpa_a0` +3.6 %, `rpa_re_kpx`
  +1.85 %, `rp_begin` +1.1 %, `submits` +1.8 %, `rpa_a5` +2.5 %.
* **It buys almost no frame time.** Binned `dt_us` is **-51.8 us (sd 34.6)** against binned
  `cpu_gpu_us` -407.8 - 6.3 % of the frame-time effect retained against 52 % of the CPU effect. A
  k-class shift-share on the same flips puts **-783.8 of -821.4 us of dt (95.4 %)** and **-712.4 of
  -788.6 us of cpu (90.3 %)** in the between-class term. **So "both halves are real" is withdrawn:
  about 95 % of the frame time and 90 % of the CPU the gate buys is the vblank-class mixture
  moving, and the within-class residue is about -76 us of CPU and about -38 us of frame time per
  flip.**
* **It has no limit in the bin width**: 25 -> -422.3, 50 -> -412.6, 100 -> -407.8, 200 -> -395.4,
  400 -> -363.4, 800 -> -319.0, 1600 -> -648.1 (the break). About -420 is a choice of constant.
* **Its coverage is differential**: 87.3 % of arm-0 flips against 93.3 % of arm-1 flips, and the
  6.0 pp preferentially dropped are arm 0's heavy k >= 3 flips.

Beside it, on the same bins: `da_take_us` **-200.1 us** - half the binned CPU figure sits inside
the timer wrapped around the block `pfhint` actually changes - `cpu_main_us` **+105.3**,
`gpu_busy_us` **+123.3**. **-408 is not a net saving of machine work.**

    other populations, same estimator:  pfcap -209.5 (sd 90.2, 4 runs)
                                        dapin -128.6 (sd 15.1, THREE runs incl. smt81a)
    A/A calibration: legacy pool -2.3 us, SE 7.6 (10 runs).  The tier-1 pair is aa78a +4.7 and
        vfy80a -20.2; their "+-17.6" is the sd of two points and its 1-df interval is +-157.6, so
        the legacy pool is the calibration that carries weight.

**RETRACTED in full: the spin decomposition.** An earlier draft subtracted `rec_spin_gpu_us` from
`cpu_gpu_us` and reported -254.5 us as "the figure without spin". `rec_spin_gpu_us` is accrued in
`CommandRecorder::SpinFor` on the thread that registers as `ThreadRole::Record`, while
`cpu_gpu_us` is `QueryThreadCycleTime` on the `ThreadRole::Gpu` handle - **it cannot be inside the
GuestGpu thread's cycle counter** - and empirically it is 0.81 x `dt_us` at r = +0.9915, so the
subtraction deflates the endpoint by about 0.86 of frame time. Applied to the plain per-flip
difference it flips the sign, **-788.8 -> +58.7**. How much of `cpu_gpu_us` is spin is **NOT
MEASURED**; the only GuestGpu-thread spin counter this record carries is `prot_spin_gpu_us`, every
run is `KYTY_FRAME_TRACE=lite`, and the decomposition needs a non-lite run (S10).

### 1.6 The one-vblank flip: a strong sequence signature, and a family split that does NOT hold

`pred/02`'s tests, **run on 39 runs and 265 048 non-fragment on-grid flips**. *(Declared deviation:
`pred/02` S2 seals the population as every run on disk carrying the counters, in three strata; 68
of the 74 extracted runs carry a populated `rpa_a5`, holding 489 202 non-fragment scoped flips, and
`a81_onevblank.py` hard-codes 33 primary runs plus six named tags. The three strata are never
printed and this session's own twenty block runs are excluded from its own one-vblank analysis. The
deviation is declared here rather than glossed; T1-T7 should be re-run over all 68 in three strata,
and that is S10.)*

* **T1 - the predecessor.** A SHORT (one-vblank) flip is far likelier right after a LONG one:
  MH-pooled **RR = 6.483 [5.860, 7.173]** over the 32 contributing runs, per-run **2.5 (`nos80e`)
  ... 15.2 (`nos80a`)**. *(An earlier draft wrote "2.6 ... 51"; neither endpoint is a value of this
  statistic at any admission cut.)*
* **T1's mirror, which the seal did not ask for and which is four times stronger.** The same MH
  estimator on the **successor** gives **RR = 28.3** against the predecessor's 6.6 on the same data
  and admission rule, with n+-5 placebos at 0.91 and 0.71. The joint table reads
  `P(SHORT | prev = 2, next >= 3) = 5.1 %` against `P(SHORT | prev >= 3, next = 2) = 1.0 %`,
  `P(SHORT | both >= 3) = 69.7 %`, on a 0.62 % baseline. **The sequence leans forward, not back** -
  a phase-repayment signature rather than a late-frame-triggered drop. Part of that is forced by
  the arithmetic of a fixed vblank grid, which is itself the finding.
* **T3 - burstiness.** `P(SHORT | previous SHORT) = 0/6176` in every run: two one-vblank flips never
  occur in a row. That is a refractory structure, and it **refutes the burst mechanism this file's
  own P2.3 predicted**.
* **T2 - periodicity.** **No run carries a dominant cadence** (no gap value +-1 holds >= 20 % of the
  gaps, over the 29 runs with >= 20 SHORT-to-SHORT gaps).
* **T5 - the missing block.** Against the run's NORMAL median: `draws` -1914 ... -2275, `rpa_a0`
  -27 ... -38, `rpa_a5` -6 ... -8, `rpd_a5` -1535 ... -1953, `swbar` -27 ... -38. **P2.4 is a MISS**:
  pooled over 6182 SHORT flips the `rpa_a5` deficit takes its modal value on only **42.8 %** of
  them, not the >= 90 % predicted.
* **T6 - the arithmetic.** Over 265 048 flips: **exactly one** flip with `rpa_a5 == 0` and k >= 2
  (`nos80b`, n = 3087) and **0** one-vblank flips carrying >= 4500 draws. Session 80's 18-of-18
  claim replicates at scale with one exception, so P2.5's "zero exceptions" is a MISS by the letter.
* **T7 - the arm.** The arm-1 SHORT share exceeds arm-0 by **+0.2285 pp [+0.1139, +0.3430],
  t = +4.06, sign-flip p = 0.0003**, positive in 28 of 33.

**The family decomposition, and why its headline is WITHDRAWN.** Splitting SHORT flips by whether a
neighbour is a three-vblank flip gives

    family A, a 3-vblank neighbour   1159 flips   triple/3x median: draws 1.0219, dt 1.0024
    family B, both neighbours 2-vbl  1136 flips   triple/3x median: draws 0.8827, dt 0.8361

and an earlier draft read family A as an attribution shift - "the present fired early and the
block was attributed to the neighbouring interval; nothing was removed, it was moved" - and issued
a retraction against FACTS s80 S1.2 on that basis. **Both the reading and the retraction are
withdrawn.** The audit established three things:

* **The dt column is an identity, not a measurement.** Family B is a 1-vblank flip with two
  2-vblank neighbours, so its triple spans exactly 5 vblanks against a denominator of 3 x the
  2-vblank median = 6, forcing 0.8333 (measured 0.8351); family A's triple spans 6 or 7 with a
  median of 6, forcing 1.0000 (measured 1.0021). The residual against the forced value is +0.21 %
  in **both** families - which is the point. **Any conservation statistic whose denominator is a
  fixed multiple of the median frame time must be reported against the window's own vblank count.**
* **No block crossed a present boundary.** An attribution shift requires the neighbouring interval
  to carry two game frames' boundary markers; it carries one in **1160 of 1160 triples** (`dmas` at
  1x in 1160/1160 and 2x in 0/1160; `rpa_a3` the same).
* **The transfer is about a tenth of the claimed size and none of it is on the GPU.** The correct
  within-class contrast - a k >= 3 flip adjacent to a SHORT minus a k >= 3 flip that is not, paired
  over 33 runs - recovers **+199 draws** of the SHORT flip's -2000, **+0.63 `rpa_a5`** of -7,
  **+61 `rpd_a5`** of -1700, and **+88 us of `gpu_busy_us` (t = +1.35, n.s.)** against -3100.
  *(An earlier draft quoted "`rpd_a5` +1250" and "`rpa_a5` 12-14 against a median of 7-8" - those
  compare a 3-vblank neighbour against the 2-vblank median, where +1600 and 13 are simply what any
  3-vblank flip reads. Against its own class the excess is +61 and +0.63.)*

**So it is NOT ESTABLISHED that family A differs in kind from family B**, and FACTS s80 S1.2 stands
as written. What this session adds to it is the sequence structure above, and the once-per-frame
counters' true intact rates over the 1160 family-A triples, which do not support a blanket claim:
**`dmas` 1160/1160, `rpa_a3` 1116/1160, `downloads` 1149/1160, `dg_img` 720/1160, `rpd_a1` 4/1160,
`da_mesh_vs` 8/1160.** The "intact on every flip" claim rests on `dmas` and `rpa_a3` alone.

**The sealed verdict on the causal direction is NOT MEASURED** (`pred/02` rule 3): rule 1 needs T1
**and** T3 pointing the same way and T3 points the other; rule 2 needs T2's cadence, and there is
none. The next measurement stays named: `KYTY_DUMP_FRAME` or `KYTY_GPU_TIME` over a window
containing a SHORT flip, now with the successor asymmetry as the thing to explain.

## 2. What this session retracts

**From the record:**

1. **FACTS s80 S6's "area-valid is empirically DRS never left the low rung"** stands as an
   association and is wrong as a reading of the statistic: the gate judges the whole-arm mean - a
   mixture - while the arms' rendered size is identical to under 0.1 % in 33 of 33 runs.
2. **FACTS s80 S10.1 and the session 81 brief S3.2 name an endpoint that cannot be unbiased**
   (S1.4). Neither class-fixed form is unbiased and the two are biased in opposite directions.
3. **`guards.py check_area`'s docstring explanation of the bimodality is not supported by the runs
   it cites** (`ab67a`, `aa67a`): attachment count and work are unchanged across the modes and the
   episodes last 33-42 flips.
4. **FACTS s80 S6's record-level bias contrast, +238.2 [-93.6, +570.0], "NOT ESTABLISHED", is
   +317.9 [+30.9, +605.0] on the machine-code-clean stratum and +499.6 [+95.9, +903.3]
   prospectively on twenty fresh runs** (S5).
5. **The `pfhint` population must be split by machine code.** `pfh75a`, `pfh75b`, `pfh76a`,
   `pfh76b` ran on binary `7026d06b`, whose `.text` is nowhere shown identical to `90c5653d...aeb0`.
   The primary stratum is **33**, not 38.
6. **FACTS s80 S7 and the brief S3.4 are wrong about the breadcrumb.** On an entry hang the abort
   path calls `ReportGpuCheckpointHistory()` - the last 16 CPU-recorded operations - and
   `ReportGpuSubmissionHistory()`; `GpuCheckpoint breadcrumb (last started, never completed)` comes
   only from `eErrorDeviceLost` (`masterSemaphore.cpp:56-62`). S8 shows what the correct instrument
   returns.

**From this session, against itself.** An independent audit - five agents re-deriving every
headline with their own parsers, five attacking the result and one scoring the board - returned
four fatal findings and twenty-odd smaller ones. The load-bearing ones:

7. **"Half of every shipped figure is the extra work the cheaper frame buys" is RETRACTED** (S1.5).
   On matched pairs the arms do the same work to +0.06 %, and `d_dt` tracks `d_cpu`: the saving
   converts to frame time.
8. **The spin decomposition is RETRACTED in full** (S1.5). `rec_spin_gpu_us` is accrued on the
   Record thread and cannot be inside the GuestGpu thread's cycle counter; it is 0.81 x `dt_us` at
   r = +0.9915, and subtracting it flips the plain per-flip figure from -788.8 to +58.7.
9. **"The gate discards 16 of 33 runs to protect against five microseconds" is RETRACTED** (S1.3).
   The -5 us was priced with the whole-arm mixture difference, which the matched-pair estimator
   never sees; inside the population it does see, the mixture difference is +0.003 pp and the
   contamination is +0.00 us, bounded at 0.36 us. What the gate protects against is the
   matched-versus-dropped divergence: mean +72.0 us, mean |delta| 152.2, max +804.6.
10. **"The high mode is cheaper on the CPU" is RETRACTED**; the price is NOT IDENTIFIED (-43.1 at
    k = 2, +123.9 unconditional, +205.5 at k >= 3, positive in 6 of 17 runs).
11. **The family-A reading of the one-vblank flip - "nothing was removed, it was moved" - is
    RETRACTED, and with it this session's retraction against FACTS s80 S1.2** (S1.6). The
    neighbouring interval carries one game frame's boundary markers in 1160 of 1160 triples, the
    within-class transfer is about a tenth of the claimed size, and the dt half of the conservation
    is an arithmetic identity of the family definition.
12. **Three numbers were not on disk and are corrected**: "91 identical" area CSVs (it is 68, with
    46 having no earlier copy); the fragment exclusion moving the work criterion "from +0.12 % to
    +1.48 %" (the statistic's maximum anywhere is +0.860 %, and the three real moves are in S1.1);
    and T1's per-run range "2.6 ... 51" (it is 2.5 ... 15.2 over the admitted runs).
13. **The draw-count-matched estimator is restated, not retracted** (S1.5): it bins on the class at
    median purity 1.000, it is matched on one work counter only, it buys -51.8 us of frame time
    against -407.8 us of CPU, and it has no limit in the bin width. It is one point inside the
    bracket S1.4 identifies, not "the price at a fixed per-flip work".

## 3. The statistics, and which to quote

| article | published | this session |
|---|---:|---:|
| `pfhint` 0 → 1, µs/flip | −766.9 [−1106.1, −427.8] | **−693.7 [−948.5, −438.8]** (17 area-valid of the 33) |
| `pfhint`, per nominal frame | −799.6 [−1159.4, −439.9] | −713.9 [−983.0, −444.7] |
| `pfhint`, **frame time** (matched pairs, 33 runs) | — | **Δdt −876.8 µs → +0.76 FPS** |
| `pfhint`, draw-count-matched (exploratory, §1.5) | — | −407.8 µs of CPU **and −51.8 µs of frame time**; bins on the class at purity 1.000 |
| `pfcap` 192 → 1024, per frame | −483.6 [−656.3, −310.9] | −483.6 [−656.3, −310.9] (unchanged) |
| `pfcap`, frame time | — | **Δdt −456.5 µs → +0.40 FPS** |
| `dapin` 0xffff → 0x5555, per frame, **3 runs** | −738.2 [−982.7, −493.6] (2 runs) | **−732.5 [−798.5, −666.4]** |
| `dapin`, frame time | +0.84 / +0.88 FPS | **Δdt −893.9 µs → +0.86 FPS** |
| `pfhint` as a class shift | removes 45.7 % [37.6, 52.8] | **47.1 % [40.2, 53.2]**, CV 22.5 % against 70.0 % |
| A/A calibration, frame time | +24.8 ± 75.8 µs/flip | **Δdt −7.0 ± 91.6 µs over six A/A runs** |

**`cap78a`, the only `pfcap` run ever to fail the gate, is RCV-VALID and reads −460.5 µs per
frame** — inside the shipped interval. Adding it moves the pool from −483.6 to −477.4: **the run
the gate discarded was not an outlier**, and that is the only place in the record where RCV changes
a shipped number at all.

---

## 4. The block — twenty runs, ten blocks, pre-registered

**A first attempt at this block was aborted before any run completed, for a machine-state reason,
and it is declared in `PLAN.md` §3.0**: the display had turned off after 23 minutes without user
input and the emulator ran at **4 FPS** with every thread idle and the GPU at 1–2 %. One input
event restored 14.3 s entries and a 33 538 µs median. Nothing from the aborted attempt is used.
`keepawake81.py` held the display awake for the rest of the session and `a81_block.py` sends one
key event before every run.

**Twenty runs, ten blocks of two, forced orientation balance (five lead S, five N), drawn from
`random.Random(0x2e8d095f)` — the second eight hex digits of `sha256(gates_base.txt)`.** No
re-takes, no optional stopping. All twenty ran; **two attempts hung at entry and were retried by
the harness** (`smp81f`, `smp81g`), which is P3.1's "at most two" — HIT. Entries: 14.3–15.8 s.

**Acceptance.** `guards.py` check 2 PASS and check 10 PASS in all twenty; **check 6 ("something
else used the machine") FAILS in 13 of 20**, as it did in session 80. Arming proved inside every
run: arm 0 `pf_l1` 1.6–3.7 per frame against `da_hit` 8609–8632; arm 1 `pf_l1` = `da_hit` to
**0.005 %**. Published area gate: **11 VALID, 9 VOID**; RCV: 9 VALID, 7 VOID, 4 UNCLASSIFIABLE.

### The pre-registered tests (`pred/03` §3), ten within-block S − N differences

    C1  PRIMARY   class-fixed, rung-fixed price   -146.53 us   95 % CI [-680.23, +387.17]
                                                  paired t = -0.621 on 9 df   p = 0.55
                                                  exact sign-flip p = 0.5645 (floor 0.00195)
    C2  CO-PRIM   B1, session 80's endpoint        -96.04 us   95 % CI [-999.21, +807.12]
                                                  paired t = -0.245 on 8 df   p = 0.79
    C4            B2, session 80's per-draw       -110.88 us   [-931.29, +709.53]
    C3            arm-0 3-vblank share              -1.18 pp   [-5.82, +3.47]
    Welch 10 v 10 on C1: -146.53 (t = -0.626 on 17.2 df)

> **VERDICT: NOT RESOLVED**, in the pre-registered word (`pred/03` §4 rule 3). |C1| is under
> 400 µs and its p is 0.55, so rule 1 does not fire; |C1| is under 200 µs but its 95 % interval does
> not exclude ±400 µs, so rule 2 does not fire either.

**C1 and C2 agree in sign** (both negative) — P3.5 HIT, and session 80's sign disagreement between
the per-flip and the class-fixed endpoint does **not** reappear at ten blocks.

**Session 80's +600.90 µs does not replicate.** Its own endpoint, C2, reads **−96.04 [−999, +807]**
here. Two independent blocks on the same design now read **+600.90 [−77, +1279]** and
**−96.04 [−999, +807]**; the honest statement is that **the sampler contribution is not detectable
and the earlier point estimate was not a signal**.

**Power, from the interval on σ and not the point** (`pred/03` §3):

    C1  sigma_d  746.1 us  95 % CI [513.2, 1362.2]   realised power at delta=675: 0.725
                                                     across the sigma interval: 0.244 .. 0.971
                                                     at delta=400: 0.286
    C2  sigma_d 1175.0 us  95 % CI [830.8, 1661.7]   power at delta=675: 0.280 (0.139 .. 0.552)

So C1's design met its 80 % target only at the optimistic end of σ, and **C2's σ_d is nearly twice
session 80's 645.94 µs** — P3.7 (σ_d in [450, 900]) is a **MISS** for C2 and a hit for C1's 746.1.
A design at δ = 400 would need about 40 blocks.

---

## 5. The gate's bias, established prospectively

The twenty runs of §4 are a population that did not exist when the hypothesis was formed. Splitting
them by the **published** gate's verdict:

    published-VOID minus published-VALID   R1  -499.6 us  95 % CI [-903.3, -95.9]  Welch t -2.60
                                           R2  -525.0     [-917.6, -132.4]         t -2.81
                                           R3  -381.8     [-683.6,  -80.1]         t -2.66
    group means (R1): VOID -1064.5 (9 runs)   VALID -564.9 (11 runs)
    mean high-mode share: VALID 0.00 %   VOID 27.42 %

**The set the programme is allowed to quote understates the effect by about 500 µs — a factor of
1.9 — and the interval excludes zero on all three statistics, out of sample.** Session 80 measured
+238.2 [−93.6, +570.0] in-sample and called it NOT ESTABLISHED; it is established now.

**And the headroom screen replicates at n = 20 with the within-state check passing:**

    corr(arm-0 3-vblank share, per-flip effect)   r = -0.9211   Spearman -0.8346   perm p < 0.0001
                                                  max leverage 0.184  jackknife [-0.934, -0.909]
    within-state, low half (10 runs)   r = -0.8868  Spearman -0.8424  perm p 0.0008
    within-state, high half (10 runs)  r = -0.7473  Spearman -0.5515  perm p 0.0127

P3.10 — which required both halves below −0.50 — is a **HIT**, and FACTS s80 §1.3's −0.9759 is now
confirmed prospectively rather than screened in-sample.

The block's own published-valid pool: **R1 −564.6 [−904.2, −224.9], τ = 503.5, I² = 99.2 %** over
11 runs — the same heterogeneity the record carries.

---

## 6. The guest-clock pacer — excluded, and its DRS hypothesis refuted

Two runs, `pac81a` and `pac81b`, `KYTY_AUDIO_SYNC=0`, both entered on attempt 1, both **VALID**
under the published gate (P4.1 HIT).

**Arming, proved inside the run** (`pred/04` §2): regressing the guest process time on the host QPC
over the settled window gives a slope of **1.000017** in both runs, identical in both halves — the
guest clock runs at the host rate and `ScaledTscLocked` is the identity. P4.2 HIT. *(The `speed=`
field of `AvTrace: flip` still reads 0.44–0.53, because `videoOut.cpp:1198-1203` computes
`cfg.pace_speed` whether or not the pacer is armed. `pred/04` §2 named that in advance: `speed=` is
not an arming proof, the slope is.)*

**The readout:** R1 = **−1331.8 ± 100.4** and **−1189.8 ± 89.4** µs per flip — **outside** the
record's random-effects interval [−1106.1, −428], and **on the far side, not the zero side**.

`pred/04` §3's rules do not cover that outcome: rule 1 wants containment, rule 2 wants the zero
side, rule 3 wants an invalid or a disagreeing pair. **Reported as the gap it is.** What it settles
is the direction: with the pacer provably disabled the `pfhint` effect is **larger**, not smaller,
so **the pacer is not manufacturing the published effect**. Both runs sit at a high arm-0 3-vblank
share (12.6 % and 8.5 %), and §5's headroom relation predicts large effects exactly there, so the
two runs are not anomalous once the state is conditioned on — **the containment test was the wrong
shape because it ignored state, and that is a defect of my pre-registration, not of the runs**.

**The DRS hypothesis is refuted.** It was reasonable to think the pacer tells the game it is running
at 60 FPS and that the game's dynamic resolution climbs because of it. It does not:

    tag       lowmode  hi-mode%   frag%  draws/flip   gpu/flip   dt median      FPS
    pac81a     2003.5      0.00    0.25      5050.4    12983.6       33392    29.95   AUDIO_SYNC=0
    pac81b     2004.3      0.00    1.00      5065.1    13500.7       33367    29.97   AUDIO_SYNC=0
    nos80b     2004.3      0.00    0.22      5047.9    13093.5       33374    29.96   record
    pfh78d     2003.7      0.00    0.16      5047.2    12863.3       33404    29.94   record
    aa78a      2004.3      0.00    0.36      5053.5    12482.4       33361    29.98   record

**With the guest clock unscaled the resolution, the work and the frame rate are the record's, to
three digits.** Declared exploratory; it decides nothing and it closes a hypothesis.

---

## 7. `dapin`'s third run

`smt81a`, an exact replication of `smt79a`/`smt79b`, entered on attempt 1, **VALID** under the
published gate (P6.1 HIT).

    tag      PUB    RCV     R1(us/flip)   2SE      R2        R3       k3_arm0  k3_arm1
    smt79a   VALID  VOID        -705.7   85.8   -743.1    -658.7       3.798    0.932
    smt79b   VALID  VOID        -735.3   97.9   -731.3    -610.2       4.652    1.184
    smt81a   VALID  VOID        -699.1   87.9   -722.5    -653.9       3.115    0.951

    three-run pools   R1 -711.7 [-823.6, -599.8]   R2 -732.5 [-798.5, -666.4]   R3 -643.4
                      tau 0.0 at k = 3 - an ESTIMATOR FLOOR, not a measurement

R2 lands inside the two-run interval [−982.7, −493.6]: **`dapin` REPLICATES** (`pred/06` rule 1,
P6.2 HIT), and the three-run interval is 2.7× narrower than the two-run one.

**The GPU cost replicates for the third time** (P6.3 HIT): `gpu_busy_us` **+1.679 %, t = +19.17**,
against +1.350 % and +1.931 % on the first two. And the work counters move as session 79 recorded
(P6.4 HIT): `rp_begin` **+3.434 % (t = +18.97)**, `rpa_re_kpx` **+3.367 % (t = +9.33)**,
`prot_pages` **+1.754 % (t = +16.49)**, `submits` **−1.514 % (t = −11.42)**, `da_take_us` −1.504 %,
`draws` +0.074 % (n.s.), `downloads` −0.027 % (n.s.), `dmas` 0.000 %.

**So `dapin` is confirmed, and it is confirmed as an impure contrast**: it buys −893.9 µs of frame
time (**+0.86 FPS**) and costs **+207 µs of GPU per flip**, and it changes five work counters at
t = 9…19. The GPU cost remains **UNEXPLAINED** (`pred/06` rule 3): no counter here attributes it.

---

## 8. The entry hang, named

Thirty instrumented entries (`KYTY_GPU_CHECKPOINTS=1`, abandoned at flip 250), every attempt
counted. **Two hung — 2 of 30 = 6.67 %, identical to the historical 4 of 60** (P5.1 HIT). Median
time to flip 250 over the 28 that passed: **15.3 s** (14.8–16.8), so the block cost ~15 minutes
(P5.5 HIT). No `ErrorDeviceLost` (P5.6 HIT).

**Two more hangs happened inside the twenty-run block** (`smp81f` and `smp81g`, attempt 1, retried
successfully), so session 81 adds **four** events to the record and the rate over everything since
session 76 is **8 in 110 attempts = 7.3 %**. All four of this session's abort lines carry the same
field set, `requested − known = 1`, `role=4`, `submit_backlog = record_backlog = 0`, an equal
`acopy` triple, **0 `GateArm:` lines**, and a `master` pointer whose low 16 bits are `0x2a10` — as
all four in the record did. The block's two died at flips **189 and 187**, the instrumented two at
**183 and 185**.

**The signature matches field for field** (P5.2 HIT):

    attempt 14  flip 183  GpuHangAbort: role=4 requested=2920 known=2919 current=3016
                          after=8s submit_backlog=0 record_backlog=0 acopy=2743/2743/2743
                          acopy_pending=0
    attempt 17  flip 185  GpuHangAbort: role=4 requested=3038 known=3037 current=3142
                          after=8s submit_backlog=0 record_backlog=0 acopy=2900/2900/2900
                          acopy_pending=0

`requested − known = 1` in both; `role=4`; the GPU 97 and 105 submissions behind the host's tick
allocator; flips 183 and 185 against the record's 188–202 (P5.3 HIT, band 180–210).

**And the new information — what the emulator was doing.** The checkpoint history is non-empty in
both (P5.4 HIT), and **every one of the last sixteen CPU-recorded operations is
`op=EopWrite(3)` from a single submission** — submit 1311 in one hang and 1325 in the other:

    GpuCheckpoint cpu-recorded (not GPU completion): seq=243279 op=EopWrite(3) submit=1311
        args=8,0,0,0x00000000 ps=0x00000004036b8900 vs=0x0000000000000000
    GpuCheckpoint cpu-recorded (not GPU completion): seq=244205 op=EopWrite(3) submit=1325
        args=8,0,0,0x00000000 ps=0x00000004036b8900 vs=0x0000000000000000

The last record of both hangs carries **the same `ps` address, `0x4036b8900`**. So the stall sits in
a run of end-of-pipe writes from one submission during level entry, and the tick it waits for is
the next one. **That is the first time the programme has had the operation class**; it is not proof
of the cause, and the GPU-side breadcrumb still needs a rebuild (§2.7).

---

## 9. The prediction scoreboard

Scored by an agent that wrote none of the pre-registrations and ran none of the analysis, from the
sealed files' hashes, with its own parser: **58 predictions, 40 HIT, 18 MISS** (two of those NOT
SCORABLE, which `pred/01` S8 counts as misses).

    blind pool 55 (P1.3, P1.4, P1.13 excluded as half-blind: 1 hit, 2 misses)
    expected hits under the stated priors 35.40, realised 39
    exact Poisson-binomial  P(>= 39) = 0.183   P(<= 39) = 0.886   two-sided 0.366
    -> NO CALIBRATION FAILURE in either direction, robust to the scorer's two contested calls

**This is the first board in the programme's record that neither over- nor under-shoots its own
bands.** Session 78 scored 9/24 with every miss in one direction; session 79 scored 21/22 and its
audit priced that at nothing; session 80 scored 20/23 at a two-sided 0.0150, a calibration failure
in the "too many hits" direction.

**What the board is nevertheless worth, honestly.** The scorer names **three hits as vacuous or
near-vacuous by construction** - P1.7 and P1.8 (both ask whether a readout moves between two
criteria that, as sealed, compute it identically) and P1.11 (whose premise the seal itself concedes
is "the premise of the criterion, not evidence for it") - and one MISS, P5.7, as vacuous by
non-occurrence. It also notes that **P3.2, P3.3 and P3.4 are three board entries decided by one
number** (C1 = -146.53). The discriminating lines are P1.14, P2.3, P2.9, P3.5, P3.7, P3.9, P3.10
and P4.3, and four of those eight came out against the session's own expectation.

**The most valuable misses:**

* **P2.3** predicted bursts; `P(SHORT | prev SHORT)` is **0/6176** - the opposite structure, and
  the reason `pred/02`'s rule 1 could not fire despite T1's RR of 6.5.
* **P3.9** predicted >= 16 of 20 RCV-VALID; **9** are - the out-of-sample half of `pred/01`'s own
  criterion, failing in the same direction as rule 5(b).
* **P4.3** predicted the pacer effect would land inside the record's interval; it landed outside on
  the far side, an outcome `pred/04`'s rules do not cover (S6).
* **P1.1, P1.2 and P1.12** are the criterion failing on its own terms.

## 10. Not closed, and what would settle each

1. **The validity criterion.** RCV is refuted by its own rule 5(b). What the evidence points at is
   already in the harness: **judge the split on `guards.py`'s attachment-weighted low mode**, which
   is what the two arms actually rendered, and handle the mixture separately. *Next:* pre-register
   the low-mode criterion, apply it to the 33 + 20 runs beside the published gate, and state what it
   admits — one line of `area_verdict.py`, no threshold change.
2. **The bias is established; the correction is not.** §5 says the quoted population understates by
   ~500 µs. *Next:* decide, in advance, whether the programme restates its shipped figures over the
   admitted-plus-void population under the low-mode criterion, and what it does about the
   heterogeneity (τ ≈ 500 µs) that dominates either way.
3. **How much of `cpu_gpu_us` is spin is NOT MEASURED.** `rec_spin_gpu_us` is the Record thread's
   poll of an empty queue and cannot appear in the GuestGpu thread's cycle counter, so
   "cpu − rec_spin" is not a decomposition of anything (applied to the plain per-flip difference it
   flips the sign, −788.8 → +58.7). The only GuestGpu-thread spin counter this record carries is
   `prot_spin_gpu_us`. *Next:* one ABBA with **`KYTY_FRAME_TRACE=1`** (not `lite`) so the
   per-thread timers are populated, and a pre-registered split; the regime is not comparable with
   the record's `lite` runs and that must be declared.
4. **The direction of causation of the one-vblank frame** — NOT MEASURED, and the family split
   this session proposed does not survive audit (§1.6). What does survive is a **forward**
   asymmetry: the successor association (MH RR 28.3) is four times the predecessor's (6.6), with
   placebos at 0.9. *Next:* `KYTY_DUMP_FRAME` or `KYTY_GPU_TIME` over a window containing a SHORT
   flip, with that asymmetry as the thing to explain; and re-run `pred/02`'s T1–T7 over all **68**
   counter-carrying runs in the three sealed strata, which this session did not do (39 runs, one
   stratum, declared in §1.6).
5. **The entry hang.** The operation class is now known (a run of `EopWrite` from one submit, the
   same `ps` address in both). *Next:* `KYTY_GPU_CHECKPOINTS=nv` for NV checkpoints, or a source
   change that calls `ReportGpuCheckpoints` on the hang path, to get the GPU-side breadcrumb; and a
   look at what submit 1311/1325 contains at level entry.
6. **`dapin`'s GPU cost** — three runs, +1.35/+1.93/+1.68 %, still UNEXPLAINED, and still not a
   pure placement contrast. *Next:* `KYTY_GPU_TIME` on one `dapin` pair to see which pass kind
   grows.
7. **A sleeping display makes every measurement worthless and nothing detects it.** *Next:* add
   `GetLastInputInfo` and the monitor power state to `guards.py` check 0 and refuse such a run.
8. **What sets the state at process start** — unchanged: nothing clears the multiplicity screen,
   and no candidate measured before flip ~300 reaches |r| = 0.50. §5's headroom relation now has
   n = 20 of prospective support, so **the state is real and its cause is still unknown**.
9. Session 78's untouched items: the guest-line prefetch population's share; `b_buf` vs `b_tex`;
   the prefetch bitmask knob; the sum of the shipped gates; M4's serialiser; the dead gate
   `dawitfb`.
10. **No acceptance run was taken.** No source file changed, so it would have been one more draw of
    the state. The base of record remains `acc78a`: **32 789 / 13 497 / 34 956 / 28.61 FPS**.

---

## 11. The arithmetic of the goal

The target is 60 FPS: **16 667 µs per presented frame**. The base of record is **34 956 µs**
(28.61 FPS), of which the GuestGpu thread is busy **32 789 µs** — it is that thread, not the GPU
(13 497 µs), that fills the frame.

Measured this session on matched pairs, with an A/A control of **−7.0 ± 91.6 µs**:

    pfhint   -876.8 us of frame time   +0.76 FPS
    pfcap    -456.5 us                 +0.40 FPS
    dapin    -893.9 us                 +0.86 FPS   (and +207 us of GPU, unexplained)

**The three together are about 2.2 ms of frame time. The gap to 60 FPS is 18.3 ms.**

**The honest statement.** Session 80 established that the programme's µs-per-flip endpoint is a
frame-time statistic. Session 81 finds that both proposed repairs — conditioning on the DRS rung and
conditioning on the vblank class — condition on consequences of the treatment, and that the gate
deciding what may be quoted rejects a third of the record to avoid a divergence of about +72 µs
while costing the record a factor of 1.9 in the size of what it reports. What is solid is smaller
and firmer than what was shipped: **the gates do convert CPU time into frame time nearly one for
one, they are worth about 2.2 ms together, and 60 FPS needs eighteen.**

*(Corrected on audit: the gate's protective quantity is not a five-microsecond mixture — the pair
matching removes that entirely — but the divergence between the pairs it keeps and the pairs it
drops, mean +72.0 µs and at most +804.6. That is still an order of magnitude below the ≈ 500 µs it
costs the record, and the cost is the part that is established prospectively.)*

Commit *(filled at the end of the session)*.
