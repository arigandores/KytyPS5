# Session 81 — prompt

Session 80's commit is on `merge-upstream`. **No source code changed in session 80** — every run
sat on session 77's installed binary `39306a9f95db805aec21d7909bbadf9ec0d115316a013e84d2bc77f8326d9dbf`,
whose `.text` is `90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0`. Harness —
**`C:/kyty/s80`**, port it to `C:/kyty/s81`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (acceptance base of
record, settled window n ≥ 2100: **28.61 FPS**, CPU 32 789 µs, GPU 13 497 µs).

Session 80 found the mechanism the last three sessions were missing and then had its own block
taken apart by its own audit. **Read §2, §5 and §9 of its FACTS before anything else.**

## 0. Read first

1. `C:/kyty/s80/FACTS.md` — the single source of truth. **§1 (the mechanism), then §2 (what it
   retracts from the record), then §5 (what the block's audit took back), then §10.**
2. `C:/kyty/s80/README.md` — the standing traps, which grew by twelve.
3. `C:/kyty/s80/pred/01_sampler_block.md`, `02_vblank.md`, `order.txt` — **do not edit them.**
4. `C:/kyty/s80/wf/` and `wf2/` — the audit reports and the 33 adversarial verdicts behind every
   retraction.

**Check the byte count of anything large you read.** Reading through the rtk-rewritten shell
truncates silently.

**Harness:** port `C:/kyty/s80` → `C:/kyty/s81` with `C:/kyty/s80_port.py` as the model, roots
rewritten, `.txt`/`.json` **byte-exact**. `gates_base.txt` pins the same **99 names, 1092 bytes**,
sha256 `4724bf812e8d095f21dc89b0e324fcf156e30d2614edcc35bb1623f9fe5f8c4f`. Verify the port by
re-deriving session 80's twelve-run table before you use it.

## 1. What session 80 settled

* **The emulator presents on a vblank grid.** `dt_us` is quantised to 1/2/3 × 16 666.7 µs;
  one present is one complete game frame (draws/flip constant to 0.346 %, six once-per-frame
  counters intact on a short flip and doubled over the pair); and
  `p1 + 2·p2 + 3·p3 = mean_dt / 16 666.667` with a gap of 0.0000.
* **So `cpu_gpu_us` per flip is frame time minus thread idle, not a CPU price** — r = 0.954–0.9986
  against `dt_us` in 36 of 36 arm-level fits.
* **90.6 % of the published `pfhint` effect is a vblank-class mix shift.** Class-fixed, the
  per-flip effect is **−52.9 µs (sd 40.6, range 103.7)** against the published sd 475.1 and range
  1273.6.
* **The swing is headroom**: corr(effect, arm-0 3-vblank share) = **−0.9759** over the ten-run
  record population, and it holds inside both halves (−0.9689, −0.9502, each at the permutation
  floor), with no gap wider than 3.21 pp. It is a genuine ten-point relation, not a two-cluster
  artefact — unlike the twelve-run version, which is (§5.6).
* **The conditioner the programme used since session 78 collapses** under a composition filter:
  corr(effect, arm-0 `cpu_gpu_us`) −0.878 → −0.234, while `dt_us` holds at −0.977 (Williams
  t = −5.31, p = 0.0011).
* **Both shipped figures survive work-normalisation** and `dapin`'s interval narrows:
  `pfcap` **−484 µs [−656, −311]**, `dapin` **−738 µs [−983, −494]**.
* **Acceptance criterion 1 is no longer vacuous**: `da_cl_bad` = 0 over 113 133 663 predicate
  evaluations in `vfy80a`.

## 2. What is settled — do not reopen

* **FACTS s79's `arm0 dt_us` column is a both-arms mean.** The arm-0 value is −0.9814, not −0.972.
* **`arm0 cpu_gpu_us` is not a price and must not be the primary endpoint again.** Its
  price component and its mixture component point in opposite directions (§5.4).
* **Draws per flip explains none of the swing** (D-term 4.48 %, work per frame identical to
  0.346 %). The composition that matters is the vblank class.
* **The entry hang is one signature, four instances, and sampler-independent** (2 of 30 with,
  2 of 30 without). "Both hangs on S" had probability 0.30. Do not re-litigate it statistically —
  instrument it (§3.4).
* **Nothing clears the multiplicity screen for what sets the state at process start.** Best
  family-wise p = 0.0736 and that candidate is the sampler itself; no candidate measured before
  flip ~300 reached |r| = 0.50. The state is established between flips ~150 and ~450.
* **The four-arm schedule for `imgskip` remains ruled out** (orientation artefact,
  `gates.cpp:380-381`).

## 3. The work, by prize

### 3.1 A rung-conditioned validity criterion — do this FIRST, it costs no run

Session 80's largest finding is one it was not looking for. **"Area-valid" is empirically "DRS
never left the low rung"** — 13 VALID / 0 void where the high-rung share is < 0.5 %, against
2 VALID / 19 void where DRS climbed, Fisher p = 1.1 × 10⁻⁷. Only two rungs are occupied (2009.9
and 3208.7 Kpx per attachment, gap +59.64 %), so breaching the 1.0 % gate needs a 1.68 pp
difference in high-rung attachments — which the vblank class cannot produce and `pfhint` can,
because the scene is CPU-bound and a cheaper frame lets DRS climb. **21 of 21** DRS-active
`pfhint` runs have the gate-ON arm on the higher rung, and corr(ΔHR, |effect|) = +0.6945.

So the gate voids a run over a rung-mix difference worth about **−60 µs** of the endpoint while
being **strongly proportional to the effect under test**. In session 80's block the quoted set
reads **+727.8 µs [+106.0, +1349.6]** smaller than the discarded one (p = 0.0152); across the
record the contrast is +238.2 [−93.6, +570.0] and **contains zero**.

*What to do:* build a criterion that restricts every run to low-rung flips **before** the split is
computed, apply it to all 38 `pfhint` runs, all `pfcap` runs and both `dapin` runs, and restate
every shipped figure under it beside the published one. Pre-register the criterion before applying
it. This is a zero-run analysis and it decides which runs the programme is allowed to quote.

**Caveat to write into the pre-registration:** VALID is *defined* by the split, so a correlation
between VALID and the split is definitional. The claim to test is the rung-versus-class separation,
not that one.

### 3.2 The sampler block, properly powered

NOT RESOLVED at **+600.90 µs, paired-t p = 0.0717**, with realised power **0.541** (known only to
lie in [0.14, 0.90]). The design needed **10 blocks (20 runs)** for 80 % power at δ = 675 and 23
blocks at its own 400 µs threshold.

*What to do:* the same randomised block design with forced orientation balance, **ten blocks**, and
the primary endpoint stated as the **class-fixed price**, not the per-flip mean — because the two
disagree in sign (B1 +600.90, V3 −493.26, corr −0.8139). Quote the paired t's p, not the
permutation's. And note that the exact sign-flip test at k = 6 was a 6-of-6 sign test with a 38 %
power ceiling; at k = 10 it has 1024 arrangements and is usable.

### 3.3 The guest-clock pacer — one run, no code

Still open, still a confound in every A/B by construction. Upper bound ~9 % with the point
estimate of the wrong sign, so it is an existence test, not a size test. **One area-valid ABBA
with `KYTY_AUDIO_SYNC=0`**: `GuestSpeedEnabled()` reads it once, `KernelSetGuestSpeed` returns
immediately, `ScaledTscLocked` becomes the identity, and the arm-wise clock contrast is exactly
zero by construction. If the effect still reads inside −767 [−1106, −428], the pacer is excluded.

### 3.4 The entry hang — instrument it, ~15 minutes

One signature, four instances, all 1–3 flips after the level-entry stall, all with the GPU lagging
by 91–93 submissions and `requested − known = 1`. `KYTY_GPU_CHECKPOINTS=1` with
`KYTY_GPU_HANG_ABORT_S=0` prints `GpuCheckpoint breadcrumb (last started, never completed)` — the
stalled operation by name. The window is flips 189–202, so an attempt can be abandoned at flip 250
and costs ~25 s instead of 320 s; at 6.67 % a 30-attempt block is ~15 minutes and should catch two.

### 3.5 The causal direction of the one-vblank frame

A short flip is one complete game frame missing ~40 depth-only passes and ~7.5 five-attachment
passes carrying ~2160 draws, and `gpu_busy_us` falls 3197 µs. **NOT MEASURED which way the
causation runs**, and the simple content→time story fails the arithmetic: removing ~13 ms from a
32.6 ms frame lands at two vblanks, yet no `rpa_a5 == 0` flip ever takes two, in 18 of 18 runs.
*Next:* `KYTY_GPU_TIME` or `KYTY_DUMP_FRAME` on a single such flip, to see whether the guest's PM4
stream for that frame actually lacks the five-MRT passes.

### 3.6 Free, already paid for

* **`dapin`** — still two runs, still not a pure placement contrast, still owes an explanation of
  its `gpu_busy_us` rise (+1.4…1.9 %, the only contrast in the record that moves it). Its
  work-normalised figure is −738 µs [−983, −494] and it is the only candidate on the list that
  buys frame time (+0.86 FPS) for no code.
* **`cond80.py` has two known defects** — `rung_hi_pct` conflates the DRS rung with cheap frames,
  and `ROOTS` stops at s75 so 16 two-arm runs are missing. Fix before reusing it.
* **P2's `imgskip` contrast** is still +29.2 µs inside its own ±250 µs band; two runs a side, two-arm
  ABBAs only.

## 4. Do NOT

**New, from session 80:**

* **Do not quote `cpu_gpu_us` per flip as a CPU price.** It is frame time minus thread idle on a
  vblank grid. Quote a price per draw at a fixed vblank class, or quote the class shift.
* **Do not report a statistic the pre-registration did not name.** Rule 1 said "the paired t";
  session 80's first draft reported the permutation p. That is session 78's `t = +0.45` defect
  repeated by the session that catalogued it.
* **An exact sign-flip test at k = 6 is a 6-of-6 sign test.** Name the rejection region before
  quoting the p.
* **Compute power from the interval on σ, not the point**, and design from the interval.
* **Print leverage, Spearman and a permutation p beside every r at small n.** A −0.995 over five
  points was one point, and removing it flipped the sign.
* **Run the within-state check rather than assuming it either way** — it destroyed the block's
  screen and left the record's standing.
* **A single-arm admission rule does not cover a two-arm readout.**
* **Beating your own priors on a scoreboard is a failure, not a success**: P(≥20 of 23) = 0.0150
  under the priors as written means the bands were too wide.
* **`<tag>.json["started"]` is the run's END.** Use `launched`.

**Carried, all in force:** never compare between runs; confirm arming by a counter or a log line;
start at 1800, analyse from 2100; do not substitute a criterion that fails; finish a pre-registered
block even when its rule fires early; never ship `dawitloop` or `dawitness=0`; do not add a Knob
enum entry anywhere but immediately before `Count`; `gen_gates.py --with` keeps the **first**
`--with`; a knob value in a gate file is decimal; do not run other work on the machine during a
measuring run; write the pre-registration before the session's own runs and have an independent
agent attack the result afterwards — that is what caught session 80 in ten places.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| frame time is vblank-quantised | 4.31 / 89.65 / 6.03 % on 1/2/3 vblanks; identity gap 0.0000 | **ESTABLISHED** |
| the published effect is class mix | **90.6 %**; class-fixed −52.9 µs | **MEASURED** |
| the swing is headroom | corr(effect, arm-0 3-vblank share) **−0.9759**, holds within halves | a screen, ten points |
| the baseline as conditioner | −0.878 → **−0.234** under a composition filter | **the published conditioner is wrong** |
| the sampler as a contributor | +600.90 µs, paired-t p = 0.0717; class-fixed price −493.26 µs | **NOT RESOLVED, sign-dependent** |
| the validity gate | a DRS-rung filter; selects on the effect | **MEASURED**; bias size only within the block |
| `pfcap` 192 → 1024 | **−484 µs [−656, −311]** | 3 runs, shipped |
| `dapin` 0xffff → 0x5555 | **−738 µs [−983, −494]**, +0.86 FPS | 2 runs, not pure |
| the entry hang | one signature, 4 in 60 attempts | **UNEXPLAINED** |

**The honest statement of the task.** Session 78 found a swing. Session 79 cleared the harness of
causing it. Session 80 found what it is: the emulator presents on a vblank grid, so the "CPU price
per frame" the programme watched for three sessions is frame time with the idle taken out, nine
tenths of every gate effect quoted in microseconds is frames moving out of the three-vblank class,
and the gate that decides which runs may be quoted selects against exactly the runs where the
effect is largest. **60 FPS still needs about 15 ms off the CPU path, and the cheapest item on the
list is still an analysis of data already on disk.**
