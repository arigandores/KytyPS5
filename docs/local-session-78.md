# Session 78 — FACTS

**Single source of truth for session 78.** Every number here was produced by running the named tool
on the named log, and every one of them was then **re-derived independently** by an auditor who
wrote its own parser and imported none of this session's code (§9). Where a number is an estimate
it says so; where something was not measured it says NOT MEASURED and names what would measure it.

**This report was rewritten after an independent audit found two fatal errors and fifteen serious
ones in its first draft.** Every retraction is listed in §9, in the words the audit forced. The
first draft's headline — "the baseline explains 95 % of the between-run variance of the `pfcap`
effect" — is **withdrawn**, and so is its claim that the CPU sampler was eliminated.

Tree: `merge-upstream`, HEAD `599f309`. **No code was changed and nothing was rebuilt.** Every run
was taken on session 77's installed binary `39306a9f95db805a…`, whose `.text` hashes to
`90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0` — verified here with my own
PE-section hasher to be **byte-identical to `79680f59`'s `.text`** recorded in
`prev77/build_verification.md`.

---

## 0. In one sentence

On byte-identical machine code, at identical rendered area, with every work counter flat to
0.2–0.4 %, one shipped gate measured **−131.7 µs in one run and −1298.1 µs in another** — a factor
of ten — and the run-to-run variation sits **more than twice as heavily in the arm the gate is
turned off in** (sd 525.8 against 241.9 µs), which says that what the programme has been calling an
error bar is a real quantity that the gate partly removes.

---

## 1. The runs

Fifteen runs, all entered Sky Garden at the first attempt in 14.3–16.4 s, **no entry hang**. Every
valid run reads guards check 2 at **11/11** self-check counters zero — verified directly from the
logs, not only through `guards.py` — and check 10 confirms the binary and every `GateArm` block.

| tag | what | verdict | result |
|---|---|---|---|
| `bind78a` | `KYTY_FRAME_TRACE=1`, `mutsite=1 pxstat=1`, no schedule | 7 PASS, 0 FAIL, 0 WARN | the phase tree (§4) |
| `pfh78a` | `pfhint=0\|1` | **VOID** — split +10.229 %, 50/114, rung 29.8 % | nothing quoted |
| `pfh78b` | `pfhint=0\|1`, `imgskip=1` | VALID — +0.001 %, 113/113 | −1085.7 ± 94.3 µs |
| `pfh78c` | `pfhint=0\|1`, `imgskip=1` | VALID — +0.001 %, 112/112 | −1298.1 ± 83.1 µs |
| `pfh78d` | `pfhint=0\|1` | VALID — +0.001 %, 112/112 | −1162.7 ± 84.6 µs |
| `pfh78e` | `pfhint=0\|1`, `--no-cpuclk` | **VOID** — split +7.805 %, 68/113 | nothing quoted |
| `pfh78f` | `pfhint=0\|1`, `--no-cpuclk` | VALID — +0.001 %, 124/124 | −131.7 ± 91.3 µs |
| `cap78a` | `pfcap=192\|1024` | **VOID** — split +1.287 %, 99/113 | nothing quoted |
| `cap78b` | `pfcap=192\|1024` | VALID — −0.001 %, 114/114 | −502.5 ± 99.9 µs |
| `aa78a` | **A/A** `pfhint=1\|pfhint=1` | VALID — +0.000 %, 115/115 | **+24.8 ± 75.8 µs, t = +0.45** |
| `wit78a` | `pfhint=0\|1`, `dawitptr=0` | VALID — −0.003 %, 113/113 | −919.4 ± 105.9 µs |
| `wit78b` | same | **VOID** — split +8.468 %, 18/112 | nothing quoted |
| `wit78c` | same | **VOID** — split +7.968 %, 56/113 | nothing quoted |
| `wit78d` | same | VALID — +0.002 %, 113/113 | −1116.5 ± 89.2 µs |
| `acc78a` | acceptance, 300 s, video | **8 PASS, 0 FAIL, 0 WARN, 4 SKIP, PASS, 0 glitches** | the base |

Five of the twelve ABBAs were void and **nothing is quoted from any of them, anywhere in this
report** — the first draft broke that rule twice and §9 records both.

**Base (`acc78a`, 8772 settled flips):** draws/frame **5049.00**, `cpu/draw` **6.4653 µs**,
`cpu_gpu_us` **32 643**, `gpu_busy_us` **13 310**, `dt_us` **35 069**, **28.51 FPS**.

---

## 2. The result

### 2.1 Seven area-valid `pfhint` ABBAs — MEASURED, and not in dispute

All seven ran executable code that is byte-identical (`pfh76c` on `79680f59`, the rest on
`39306a9f`; the `.text` section hashes are equal), at matched-pair rendered area
**2007.56–2008.03 Kpx**.

| run | arm0 (`pfhint=0`) | arm1 (`pfhint=1`) | effect | 2·SE | arm0 `da_take_us`/take |
|---|---:|---:|---:|---:|---:|
| `pfh78f` | 31 567.2 | 31 435.5 | **−131.7** | 91.3 | 289.0 ns |
| `pfh77a` | 31 941.9 | 31 251.7 | −690.2 | 87.8 | 311.7 |
| `pfh76c` | 32 205.4 | 31 948.1 | −257.3 | 133.5 | 311.7 |
| `pfh77d` | 32 586.5 | 31 852.2 | −734.3 | 103.8 | 326.4 |
| `pfh78b` | 32 675.1 | 31 589.4 | −1085.7 | 94.3 | 392.4 |
| `pfh78d` | 32 923.6 | 31 760.9 | −1162.7 | 84.6 | 387.8 |
| `pfh78c` | 32 977.5 | 31 679.4 | **−1298.1** | 83.1 | 372.3 |

    arm0 (hint OFF)  sd 525.8 us   range 1410.3   (1.62 % of mean)
    arm1 (hint ON )  sd 241.9 us   range  696.4   (0.76 % of mean)
    random effects  -766.8 us   95 % CI [-1098, -436]   Q = 539.3 / 6 df   I^2 = 98.9 %   tau = 445 us

**The runs did the same work.** Re-derived on the arm-0 matched-pair population of all seven:
`gbar` 0.036 %, `rec_n` 0.236, `pmemo_miss` 0.249, `smp_miss` 0.261, `draws` 0.262, `da_hit` 0.295,
`ob_n` 0.296, `da_move` 0.305, `bb_n` 0.312, `pmemo_hit` 0.323, `da_pf_b` 0.326, `da_words` 0.332,
`b_texn` 0.334, `da_runs` 0.336 % of spread. **Only the price moved**, and it is concentrated:
`da_take_us` spans **2489.8 … 3388.0 µs a frame, 30.5 %**, which is **63.7 % of the whole arm-0
spread**, over an identical 8614–8639 takes against an identical 12.50–12.54 MB offered per frame.

### 2.2 Where the variation sits — MEASURED, with the intervals the audit forced

The untreated arm is the more variable one, **sd 525.8 against 241.9 µs, ratio 2.17**. The arms are
correlated across runs (r = +0.524), so the correct test is Pitman–Morgan, and I ran it myself:
r(diff, sum) = **+0.709**, **t = +2.25 on 5 df, p = 0.074**. **Suggestive, not established.** And the treated arm still carries **46 %** of the
untreated arm's run-to-run sd: of arm1's 241.9 µs, only 126.7 µs tracks arm0 and **115 µs is
variation the baseline does not explain at all.**

Regressing arm1 on arm0:

    all 7 runs         slope 0.241   95 % CI [-0.210, 0.692]  (t on 5 df)   r +0.524   resid sd 225.8
    the 6 on 39306a9f  slope 0.293   95 % CI [-0.062, 0.649]  (t on 4 df)   r +0.753   resid sd 162.5

**This is not a coupling-free regression.** `arm1 ≡ arm0 + effect`, so regressing arm1 on arm0 is
the regression of the effect on arm0 with 1 added to the slope — the first draft claimed immunity
for a relabelling of the identical fit, and that claim is withdrawn. The coupling was instead
**quantified**: the within-run standard error of an arm mean, measured from each run's own blocks,
is 62–93 µs (not the 47 µs the first draft asserted), and the two arms' sampling errors are
correlated at r ≈ +0.77. Correcting for attenuation **and** for that shared error gives an
errors-in-variables slope of **0.231**, within 1 pp of the naive 0.241. The coupling is real and
small.

> **`pfhint` removes 76 % of the run-to-run baseline variation, 95 % CI [31, 121] pp.**
> The interval excludes slope = 1 (the gate irrelevant to the swing) and reaches past 100 %, which
> shows that 1 − slope is a regression coefficient and **not** a bounded variance share.
> **This is an INTERPRETATION** — a between-run OLS on seven runs, chosen after seeing the seven
> points, not a pre-registered test.

### 2.3 What is held within a run is the EFFECT, not the baseline

The first draft said the state is "set before flip 2100 and held for the whole run". That is **false
of the baseline and true of the effect**, and the distinction matters because the first draft's
operational prescription depended on the wrong half.

Splitting every run's matched pairs into halves (the ABBA order makes a half-to-half move
common-mode, not a gate contrast) — re-derived here over ten runs, my own parser: the **baseline**
moves by up to **+501.0 µs** inside one process (`pfh78b`; `cap76a` +267.8 µs; median |shift|
**139.6 µs**) against a between-run sd of 526 µs — while the **effect** moves by a median of
**34.9 µs**, max 232.6 µs, against a between-run sd of 449 µs. In the A/A the two halves read
+23.4 and +26.1 µs.
And those within-run baseline moves pass through the gate **untouched**: pooled over 14 runs the
treated arm follows the untreated one at slope **1.26 [0.83, 1.68]**, against −0.759 between runs
(t = 5.13 for the difference). They also sit in a different component — within-run, `da_take_us`
carries only ~12–20 % of the move, against 63.7 % between runs.

**So a run's total `cpu_gpu_us` is a proxy for the gate-removable state, not the state itself, and
"quote a prefetch gate as a slope against the run's own baseline" is NOT licensed.**

### 2.4 The A/A — the estimator is sound; it says nothing about the mechanism

`aa78a`, two textually identical arms, ABBA, 115/115 pairs, area split +0.000 %:
**+24.8 ± 75.8 µs, t = +0.45**. The bracketing timer reads **340.32 ns per take in arm0 against
340.58 ns in arm1**, where every real `pfhint` ABBA moves it by 8–13 %.

So the estimator, the schedule and the pairing carry no bias larger than about ±75 µs in that
process. Three things the first draft got wrong here, all corrected:

* Of the three historical A/A runs, **two are area-void on this programme's own gate** (`aa68b`
  split −0.496 %, 56/79; `aa70a` split +1.091 %, 40/101). The first draft quoted their pool
  (+95.0 ± 81.2 µs) as the comparator, which is quoting void runs. The only valid historical A/A is
  `aa69a`, +88.1 ± 104.5 µs, and **`aa78a` − `aa69a` = −63.3 ± 129.1 µs (t = −0.98)**: the
  historical offset is **neither reproduced nor refuted**. Pooling the two valid A/As gives
  **+46.6 ± 61.3 µs**, so a systematic offset up to about +108 µs is not excluded.
* One A/A has zero degrees of freedom on between-run behaviour and cannot license any statement
  about a 1410 µs between-run spread.
* **Under the state hypothesis an A/A must read zero whether or not the state exists**, since both
  arms carry the same run state. It corroborates the instrument, not the mechanism.

### 2.5 What was tested — and what the pre-registered rules actually say about it

**Image-upload traffic (P2's candidate).** The mechanism it predicted is **refuted in direction**:
at 11.1 MB/frame the effect was −1085.7 µs, *larger* than at 99–147 MB/frame, where an L3-pollution
story predicts smaller. But **P2's own discriminating contrast is NOT RESOLVED**. P2 fixed the rule
in advance: "if the contrast comes back inside ±250 µs, the honest report is 'not resolved by two
runs a side'". With `pfh78a` void, the contrast is
−1162.7 − ½(−1085.7 + −1298.1) = **+29.2 µs**, inside the band. The first draft announced
"the manipulation moved nothing" and never said its own rule called for "not resolved". By the rule
written before the runs, **the next step is two more runs a side.** What *is* established is that a
nine-fold manipulation of `img_up_kb` moved the effect by +29 ± ~250 µs against the +860 µs the
observational ordering across `pfh76c`/`pfh77a`/`pfh77d` had suggested — and that `img_up_kb` is not
even stable under its own control: two runs with a byte-identical gate file uploaded **11.1 and
48.9 MB a frame**.

**The CPU sampler — NOT ELIMINATED.** The first draft said it was, on the strength of `pfh78e`
reading −3.657 %. `pfh78e` is **void**, that number may not be quoted, and removing it reverses the
argument: only two runs were taken with `--no-cpuclk`, only one is valid, and that one (`pfh78f`)
read **−131.7 µs — the smallest effect of the session, smaller than every run that carried the
sampler.** On the admissible evidence the sampler I added to the harness remains a live candidate
with **n = 1 pointing toward it**, and the next measurement is two more `--no-cpuclk` ABBAs.
**NOT MEASURED.**

**A run-level multiplicative factor** (effective clock, thermal state, "the run was slower") is
disfavoured: normalising every matched-pair delta by its own run's baseline leaves τ/|µ| at 36.2 %
against 39.4 %. That is a **weakening, not an exclusion**, and the first draft's "is excluded"
is downgraded. The CPU telemetry added this session records CCD0 at 4542 MHz against CCD1's 4951,
~29 % occupancy, no throttle bit outside 0x400.

### 2.6 The variable — NOT IDENTIFIED

It is a state that changes the **price** of memory-bound work by up to 36 % while changing the
**amount** by 0.3 %, and 63.7 % of its between-run footprint is inside `da_take_us` — the witness
compare and the eleven-vector prefetch block. Whether it is "concentrated in `AheadTake`" is an
INTERPRETATION: 63.7 % is a share of a between-run spread, not a localisation.

Live candidates, in order: **the CPU sampler** (n = 1 against it, §2.5); **host background state**
(now recorded per run in `pre_run['host']`, never yet varied deliberately); **host-heap layout**
(the emulator prints one fingerprint per run, `RecordThread: started recorder=0x…`, and the sixteen
values on disk sit in sixteen different L1 sets — but ranking six runs by one of thirty-two
candidate bit-fields reproduces any ordering with probability ≈ 0.59, so this must be tested
prospectively, never fitted).

*What would measure the last one:* ~15 lines and 11 gauges (`FrameStats::Gauge` exists at
`frameStats.h:969-975`) recording the host addresses of the eleven prefetched vectors and the
witness backing, then three runs with the prediction written down first.

---

## 3. What this does to the programme's table

| article | axis | the record | state |
|---|---|---|---|
| **the baseline itself** | CPU | **1410 µs of run-to-run swing at identical work** | **the finding; variable NOT IDENTIFIED** |
| `pfhint` 0 → 1 | CPU | 7 valid runs, −132 … −1298 µs | RE **−767 µs [−1098, −436]**, I² = 98.9 % |
| `pfcap` 192 → 1024 | CPU | 4 valid runs, −238 … −503 µs, **two binaries** | see below |
| fraction of the swing the gate removes | — | `pfhint` 76 % [31, 121] pp | **INTERPRETATION**, n = 7, not pre-registered |
| A/A on this binary | — | +24.8 ± 75.8 µs | the estimator is unbiased at that level |
| where `pfhint`'s win lives | — | the eleven-vector block **suffices** | §5, 2 valid runs |
| `mh_bind_us` interior | CPU | first prices, with a stated bias | §4 |
| C2 / the GPU axis | GPU | ~8–10 µs of wall | still closed |

**`pfcap` must be split by binary, and this session's own PLAN said so before any run was taken.**
`cap76a` and `cap76b` ran on `240edc027c7b5a26`, whose `pfcap=1024` arm reached the prefetch through
the runtime overload clang unrolls by eight — **different machine code for the very block under
test** (their own `<tag>.json`; s76 FACTS §1; s77 FACTS §5; `pipelineCache.cpp:2725-2728`).
`cap76b` also ran at schedule period 15 and at 2012.9 Kpx. `PLAN.md` §0a, written before run 1,
says: "**τ(`pfcap`) = 61 µs is NOT established and `pfcap` must not be used as corroboration.**"
The first draft dropped that restriction and promoted the four-run series to the session's tightest
result. **That is the criterion substitution this programme condemns, committed by me, and it is
withdrawn.**

What survives: four area-valid `pfcap` runs read −238.2, −294.1, −381.8, −502.5 µs (random effects
−353 µs [−460, −246], I² = 82.8 %). **Same-code, they are two runs** — `cap77a` −381.8 ± 79.8 at
arm0 31 710.8 and `cap78b` −502.5 ± 99.9 at arm0 32 381.0, random effects **−438.4 [−556.5, −320.4]**
— i.e. a line through two points with zero degrees of freedom. The two `240edc02` baselines are
**3.0 ± 78.1 µs apart**, one point in x, so even the four-run fit is effectively three points with
the binary perfectly confounded against the ordering. **"Perfectly monotone" and "the baseline
explains 95 %" are withdrawn** (exact permutation p = 0.042 — the floor for n = 4; the 95 % interval
on the explained fraction is [4 %, 100 %]; the residual sd of 32 µs has a 95 % interval of
[17, 201] µs, spanning the raw effect sd of 115 µs).

**Censoring.** The valid sample is conditioned on the area gate: eight of fifteen `pfhint` ABBAs in
the record are void. They do **not** differ from the valid ones in arm-0 baseline (t = −0.34) or in
measured effect (t = −0.37), so the censoring is not shown to be informative — but fitting all
fifteen gives slope **−0.653 [−1.12, −0.19]** and r = −0.642 (r² 0.41) instead of −0.889 (r² 0.79).
**Every regression in §2.2 is conditional on the area-valid subsample.**

**The practical consequence for 60 FPS**, stated as the hypothesis it is: at the lowest `pfhint`-run
baseline in the record (`pfh78f`, arm0 31 567 µs) the gate measured only −131.7 ± 91.3 µs, which
suggests the programme's shipped total should be quoted at the **best** baseline rather than the
mean — a smaller number than the table carries. That rests on **one run**, and that run is also the
session's only valid `--no-cpuclk` run, so it cannot both acquit the sampler and set the bound. It
is also not the lowest baseline in the record (`cap76a`/`cap76b` read 31 301–31 304). **Two more
low-baseline runs are needed before it is anything but a hypothesis.**

---

## 4. `mh_bind_us` priced for the first time (`bind78a`)

Every fine-grained draw-phase timer in the tree reads **exactly zero in every run on disk**, because
they sit behind `KYTY_FRAME_TRACE=1` and the harness has always run `lite`. One run lit them.

Instrument check first, on the settled window: `mh_n + mh_disp_n = 5046.546 + 268.021 = 5314.567
= a_hold_n` **exactly**, and `sum(mh_*)` covers `a_hold_us` to **99.691 %** (session 69 read
99.68–99.69 %).

**The window matters and the first draft got it wrong:** its tree was computed from n = 2, i.e.
including the ~2100-flip entry ramp. Restated on the programme's standard settled window
**n ≥ 2100** (6171 flips):

    d_bind    13 215.3 us/frame        (mh_bind_us 13 355.5)
      b_buf    4 640.3   35.1 %   NativeStorageBuffer      descriptors.cpp:149
        ob_us  4 347.6            ObtainBuffer             bufferCache.cpp:892
          bb_sync 3 206.2         BindBufSyncNs - TWO functions, see below
      b_tex    3 339.9   25.3 %   ResolveTextureWith       descriptors.cpp:747
        b_view   464.8            FindTexture              textureCache.cpp:2202
      bb_find    651.9    4.9 %   the buffer-descriptor decode loop   descriptors.cpp:1372
      b_smp      302.8    2.3 %   NativeSampler            descriptors.cpp:1039
      bb_upload  268.0    2.0 %                            descriptors.cpp:1440
      residual  4 012.3   30.4 %

Unit prices: **69.8 ns per texture resolution** (47 884/frame), **89.8 ns per `ObtainBuffer`**
(48 427/frame), **92.6 ns per `FindTexture`** (5017/frame).

**Three caveats, all from the audit and all load-bearing:**

* **No unit price can be quoted for `bb_sync`.** Its `Scope` is constructed **without a count
  counter** at *two different functions* — `BufferCache::SynchronizeBuffer` (`bufferCache.cpp:735`)
  and `BufferCache::CollectBufferUpload` (`:2340`). The first draft's "65.5 ns per
  `SynchronizeBuffer`" divided it by `ob_n` on an untested one-per-`ObtainBuffer` assumption.
  **Withdrawn.** Measuring it costs one count argument on each Scope.
* **"The buffer path is the largest block" is NOT established.** `FrameStats::Scope` timestamps
  inside its own constructor and destructor, so each nested scope charges roughly half its overhead
  to itself and **all** of it to its parent — the inflation scales with the **count** of nested
  scopes, not with their duration. `b_buf` encloses ~96 900 nested scopes a frame (`ob_us` 48 427
  plus `bb_sync`); `b_tex` encloses 5017. Writing *c* for the per-scope cost, `b_buf` and `b_tex`
  are equal at **c = 14.1 ns**, and the plausible bracket for *c* on this machine is **7–15 ns**
  (lower anchor: session 69's measured 0.10 ms `mutsite` cost over ~31 000 timestamps; upper anchor:
  `bind78a`'s `mh_bind_us` against `cap77a`'s over ~190–250 k scopes). The crossover is inside the
  bracket. **"Shares, not absolutes" is not a defence when the bias scales with count.**
* **`FindTexture`'s population does not replicate**: 4593 (`cap77a`), 4636 (`pfh76c`),
  4715 (`pfh77a`), 4803 (`pfh78d`), 4810 (`pfh77d`) against `bind78a`'s 5017 — a 4–9 % excess, and
  it is the population carrying the `FindTexture` price.

What survives cleanly: **the render-mutex binding phase is a per-binding cost, not a per-draw one**
— ~47 900 texture resolutions and ~48 400 `ObtainBuffer` calls a frame, 9.5 of each per draw — and
the two candidate blocks are of the same order, ~3.3–4.6 ms a frame each, with their ordering
undetermined by this run.

---

## 5. Where `pfhint`'s win lives (`wit78a`, `wit78d`)

`pfhint` selects the cache level of every `__builtin_prefetch` in the tree. There are exactly four
emission sites, all in `pipelineCache.cpp` (`:735`, `:737` inside `PrefetchLine`; `:796`, `:802`
inside `VerifyWitness`), reached by three call populations on the take path: the guest-line loop at
`:790-806`, entirely inside `if (direct)` and therefore alive only when `dawitptr=1`; the
eleven-vector block at `:2730-2766` under `daprefetch` (pinned 1); and `PrefetchLine` at
`:2366-2367`, which is **dead** because `daqpre=0` is pinned in all six gate files of this session.
`dawitptr` is read at exactly two places, `:781` and `:784`, both inside `VerifyWitness`. **So
`dawitptr=0` removes the whole guest-line population and nothing else in the prefetch path.**

**The populations, corrected — the first draft had them inverted.** Measured from the counters, not
from a static opcode census:

| population | per frame | how |
|---|---:|---|
| eleven-vector block | **184 734** | `da_pf_cap_b` 11 822 994 B / 64 B, = 21.4 per take |
| guest-line loop | **54 906** | live runs = `da_runs` − `da_runs_clean` − `da_singles`, `da_singles` present and exactly 0 |

**The eleven-vector block is the larger population by 3.36×, not the smaller one by 192×.** The
first draft's "192 times as many" divided a per-frame count by a per-take count, and its "286 per
take" was session 77's static disassembly census (143 `prefetcht0` + 143 `prefetcht2`, two mutually
exclusive hint forms across three template instantiations). **P8's prediction 1 was given
probability 0.6 *because of* that inverted ratio.** Corrected, the outcome is the expected one, not
a surprise.

Two area-valid ABBAs with `dawitptr=0` pinned in both arms, arming proved by counter — `da_direct`
and `da_direct_no` are both **present and read exactly 0.000** in both arms against 8626.6 per frame
in `pfh78d`:

    wit78a   arm0 32 971.7   effect  -919.4 +- 105.9
    wit78d   arm0 32 630.6   effect -1116.5 +-  89.2

**P8 prediction 1 (|effect| < 350 µs) is REFUTED; prediction 2 (−900 … −1300 µs) is a hit on both
runs.** What is MEASURED: **with the entire guest-line population deleted from both arms, `pfhint`
still buys −0.92 to −1.12 ms — the eleven-vector block alone suffices to produce a win of the same
order as the full gate.**

What is **NOT MEASURED** is the share the guest-line population carries. Three estimators disagree:
+4 % against the cpu-baseline line, **+25 %** against the better-fitting take-timer line
(r = −0.907 against −0.889), and **+11 % with 95 % CI [−88, +109] %** from this session's own
`stats78.py`. The first draft's "±30 %" used the seven-run fit's residual sd as the error bar for
two runs that were not in the fit; their own dispersion gives **+44 ± 456 µs**. And the transfer is
itself suspect: `dawitptr=0` re-routes the live compare through `LiveBackingPage`
(`:812-825`), adding ~54 900 page-table lookups a frame, and at equal `cpu_gpu_us` (32 971.7 vs
`pfh78c`'s 32 977.5) it puts **+293 µs more** inside `da_take_us`. P8 pre-registered exactly this
caveat — "the two populations' shares are not additive across runs" — and the first draft dropped it.

---

## 6. The prediction scoreboard

The audit's sharpest procedural finding: the `pred/` chain scored itself honestly and **none of it
reached the report**. It does now.

**Hits:** P1.3 (`b_tex` 2300–4200, point 3300 → 3339.9), P1.5 (`b_smp` 200–900 → 302.8),
P1.6 (the instrumentation inflates the totals), P1.7 (`mh_n + mh_disp_n == a_hold_n` exactly,
coverage 99.691 %), P3.1 (`img_up_kb` 8–12 MB → 11.1), P3.5 (high rung below 29.8 %, area-valid →
0.0 %), P4.3 (area-valid, rung ~0), P8.2 (−900…−1300 on both `wit` runs), P7.5 (`da_pf_b` flat,
`pf_l1 ≈ da_hit` in both arms of `cap78b`).

**Misses, every one of them:**

| prediction | predicted | measured |
|---|---|---|
| P1.4 | `b_view` 500–2100 µs | **464.8** — below the band. §4's "96 ns, not 455 ns" is a *missed pre-registered band*, not an unheralded discovery |
| P2 / P5.1 | control −550…−850 µs | `pfh78d` **−1162.7** |
| P2 | skip runs \|effect\| < 350 µs | **−1085.7, −1298.1** — wrong in sign of the mechanism |
| P3.3 | `gpu_busy_us` falls 1.0–1.3 ms | **0.35–0.56 ms** against the same-session control |
| P4.1 | −900…−1250 µs | **−1298.1** — 48 µs outside |
| P4.4 | baseline `da_take_us` 3250–3500 | **3211** |
| P5.3 | control's high-rung share > 0 % | **0.0 %** |
| P5.4 | `pfh78d` `gpu_busy` 13.1–14.0 ms, take 2650–2850 ns | **12.85 ms, 3345 ns** — both outside |
| P6.1 / P6.2 | sampler guilty −1.9…−2.6 % (p 0.15) or innocent −3.2…−4.2 % (p 0.75) | `pfh78f` **−0.552 %** — outside **both** |
| P6.3 | take/take 370–400 or 310–330 ns | **289.0 ns** — outside both |
| P7.1 | −250…−450 µs | `cap78b` **−502.5** |
| P7.2 | both arms in a 31.0–32.0 ms "stable band" | arm0 **32 381** |
| P7.3 | baseline take 280–300 ns | **328.8 ns** |
| P7.4 | `pfcap` area-valid (5 for 5) | `cap78a` **VOID** — the first `pfcap` run ever to fail the gate |
| P8.1 | \|effect\| < 350 µs (p 0.6) | **−919.4, −1116.5** |

**Fifteen misses against nine hits, and the misses are nearly all in one direction: every band I
drew for an absolute magnitude was too small, and every prediction that a state would return to a
session-77 value failed.** That is the same systematic error session 77 recorded about this
prefetch, now extended to the baseline itself.

**Pre-registration, honestly.** Eight files cover fifteen runs (six are re-takes of a pre-registered
configuration, plus `acc78a`, covered by `PLAN.md` §2). The ordering is real: for all eight,
`mtime == ctime` to the millisecond (written once, never edited) and each precedes its run's
`pre_run.sampled_at` by **5–12 s** (18:08:02/18:08:11, 18:15:39/18:15:45, 18:21:32/18:21:38,
18:28:34/18:28:40, 18:35:01/18:35:06, 18:40:57/18:41:03, 18:53:23/18:53:28, 19:08:55/19:09:02).
**But the "WRITTEN <time>, BEFORE THE RUN" line inside files 03–08 is wrong** — I typed times from
memory rather than stamping them, and they read 4.5 to 43 minutes *after* the run they precede. The
files are **deliberately left unedited**, because editing them would destroy the `mtime == ctime`
evidence that is the only real anchor. **Session 77's C10 is therefore not discharged**: nothing but
a filesystem timestamp anchors the ordering. *The cheap fix for session 79:* have `enter_scene.py`
record the sha256 of the pre-registration file in `<tag>.json` at run start.

---

## 7. Corrections to the record

Each was found by an independent agent and then verified here directly.

1. **The session-76 logs are NOT gone.** `C:/kyty/s76` holds 18 logs; `pfh76c`, `cap76a` and
   `cap76b` were re-derived from their raw logs here. FACTS s77 §3's caveat is false.
2. **"The harness records no CPU-side telemetry at all" is too strong.** `cpu_main_us`,
   `cpu_gpu_us`, `cpu_present_us` and `cpu_proc_us` are on every `FrameTrace` main line
   (`frameStats.h:1085-1086`). `cpu_proc_us` is quantised to exactly 15 625 µs, so only per-arm
   means are usable. What is absent is *environment* telemetry.
3. **The `gen_gates.py --with` trap is recorded backwards.** `take_overrides` uses
   `argv.index('--with')` — the **first** occurrence. Verified empirically:
   `--with mutsite=1 --with pxstat=1` applies **`mutsite=1` only**. FACTS s77 §8,
   `prev77/README.md` and the project `CLAUDE.md` all say the second survives.
4. **FACTS s77 §7's entry-hang reading is backwards.** `current=3289` is
   `MasterSemaphore::m_current_tick`, the host's next-tick allocator, not GPU progress: the GPU was
   93 submissions *behind*, wedged for 59 s at 100 % utilisation and 166–175 W with the SwPowerCap
   bit (0x4) set on 116 samples of `gpuclk_curve77a.csv`. It is also **not the first since session
   61** — `fsl76a` attempt 1 is the same event. Rate 2 of 117 attempts; **0 of 15 this session**.
5. **FACTS s77 §7's "the truncation curve inverts to the size histogram of the eleven vectors" is
   false.** It inverts to byte mass by *offset band* plus bracketed counts above a threshold.
6. **FACTS s77 §7's "the rung is decided in the first ~600 settled flips and holds" has
   counter-examples** (`img69c`, `pfh75a`, `dec70a`, `aa68b`, `fsl76a`). No early abort was armed.
7. **`reusebindings` is not a gate.** `renderDraw.cpp:1892` calls it one; it is
   `RenderExecutor::ReuseBindingsEnabled()`, a read of `KYTY_REUSE_BINDINGS`. A gate-file A/B on
   that name would silently do nothing.
8. **The audit's C4 is not supported.** `cap77a` was suspected of being the largest `pfcap` reading
   because it alone carried `mutsite=1 pxstat=1` inside the path under test. `cap78b` carries none
   of it and reads **−1.586 %**, larger still, on the same binary. The instrumentation was not
   inflating the effect.
9. **The DRS feedback is real; the selection bias the first draft inferred from it is not.**
   MEASURED: in **12 of 12** void ABBAs on disk the gate-ON arm rendered *more* area, and among the
   nine rung-mobile `pfhint` runs the split tracks the effect (corr = **+0.841**). REFUTED as
   stated: the gate does **not** preferentially discard large effects — dropped-vs-matched pairs
   inside void runs differ by −20.7 ± 67 µs (12 runs); pooled, void runs carry *smaller* effects
   than valid ones (−680.8 vs −765.7, t = +0.37); baseline-adjusted they sit +145 ± 296 µs *above*
   the valid line. Rung mobility is orthogonal to effect size (r = −0.016), and 8 of the 9
   rung-mobile runs went void against 0 of the 6 rung-still ones.

---

## 8. Traps found this session

* **A manipulation without a same-session control is not a contrast.** Two `imgskip=1` runs read
  −1086 and −1298 µs against session 77's −690 and −734, and the reading "the gate modulates the
  effect" survived exactly until the control was taken and landed at −1163.
* **Quoting a void run's effect, even once, can invert a conclusion.** The first draft's "the CPU
  sampler is not the variable" rested entirely on `pfh78e`, which is void.
* **A pre-registered decision rule must be applied, not just written.** P2's ±250 µs band said "not
  resolved"; the first draft reported "refuted".
* **A pre-registered exclusion cannot be dropped because the data later look good.** `PLAN.md` §0a
  excluded `cap76a`/`cap76b` as corroboration before run 1; the first draft built the session's
  tightest claim on them.
* **Relabelling a regression does not remove mathematical coupling.** `arm1 ≡ arm0 + effect`.
* **2·SE is not a 95 % interval at small n.** On 5 df the t quantile is 2.571 and on 2 df 4.303.
* **A perfect correlation over four points has an exact permutation p of 0.042 — the floor.**
* **A `Scope`'s overhead scales with the COUNT of nested scopes, not their duration**, so "shares,
  not absolutes" does not protect a comparison between a deeply-nested block and a shallow one.
* **A counter with no count counter has no unit price** (`bb_sync`), and a `Scope` at two call sites
  is not one function's time.
* **Compute on the settled window.** The first draft's phase tree silently included the 2100-flip
  entry ramp.
* **Type the prediction's timestamp from the clock, not from memory** — and never edit a
  pre-registration afterwards, because its mtime is the only anchor it has.

---

## 9. What the audit forced

Four agents that had not seen the analysis were given the raw logs and the draft: one re-derived
every headline number with its own parser, three attacked. **The re-deriver returned CONFIRMED —
every number in the draft reproduced, most to the printed digit** — and the three adversaries
returned PARTLY_REFUTED with **2 fatal and 15 serious** findings, every one of which is accepted and
incorporated above. The load-bearing retractions:

* **"The baseline explains 95 % of the between-run variance of the `pfcap` effect" — WITHDRAWN.**
  n = 4, permutation p at the floor, explained-fraction interval [4 %, 100 %], and the series spans
  two binaries in violation of this session's own pre-registration.
* **"Perfectly monotone" — WITHDRAWN.** The two lowest baselines differ by 3.0 ± 78.1 µs.
* **"The CPU sampler is not the variable" — WITHDRAWN.** It rested on a void run.
* **"Image-upload traffic is NOT the variable / the manipulation moved nothing" — SOFTENED** to
  "the mechanism's direction is refuted; the pre-registered contrast is not resolved".
* **"192 times as many" — INVERTED.** The eleven-vector block is 3.36× the larger population.
* **"No shared term, so no mathematical coupling" — WITHDRAWN**, and the coupling quantified instead.
* **"Set before flip 2100 and held for the whole run" — CORRECTED**: the *effect* is held, the
  baseline is not.
* **"The validity gate discards the runs where the gate works best" — REFUTED as stated.**
* **"65.5 ns per `SynchronizeBuffer`" and "the buffer path is the largest block" — WITHDRAWN.**
* **The A/A comparator built from two void A/A runs — WITHDRAWN.**

---

## 10. The arithmetic, restated

**Today** (`acc78a`): CPU **32 643 µs**, GPU **13 310 µs**, wall **35 069 µs**, **28.51 FPS**.
`acc77a` read 31 327 / 14 507 / 32 025 / 31.23 on **the same machine code**. A single acceptance run
against a single acceptance run is a between-run comparison and is not a measurement; it is recorded
because the difference is the subject of this report, not a regression.

**The conclusion.** Session 77 found that the programme's error bars were three to five times too
small and called finding the variable behind τ the most valuable thing on the list. This session did
not find the variable — and its own best candidate was refuted by its own manipulation, while the
suspect it introduced itself is still not cleared. What it established instead is where to look:
**the between-run variation is more than twice as large in the arm the gate is switched off in, it
is 64 % inside the timer that brackets the path the gate prefetches into, it is stable within a run
while the total frame cost is not, and it is worth up to 1.4 ms a frame — as much as everything the
programme has shipped since session 72.** Quoting any prefetch gate as a single number remains
wrong, and this session can now say that the right conditioning variable is not the run's total CPU
either.

Commit **56fc550** (branch `merge-upstream`, base `599f309`, 2 files, +714) — documents
only; **no source file changed and nothing was rebuilt this session**. Not pushed.
