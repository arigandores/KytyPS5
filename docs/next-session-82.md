# Session 82 — prompt

Session 81's commit is on `merge-upstream`. **No source code changed in session 81** — every run
sat on session 77's installed binary
`39306a9f95db805aec21d7909bbadf9ec0d115316a013e84d2bc77f8326d9dbf`, whose `.text` is
`90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0`. Harness — **`C:/kyty/s81`**,
port it to `C:/kyty/s82`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (acceptance base of
record, settled window n ≥ 2100: **28.61 FPS**, CPU 32 789 µs, GPU 13 497 µs).

Session 81 built the criterion session 80 asked for, watched it fail its own admission rule, and
found four larger things on the way. **Read §1, §2, §5 and §11 of its FACTS before anything else.**

## 0. Read first

1. `C:/kyty/s81/FACTS.md` — the single source of truth. **§1.1 (why the criterion failed), §1.2
   (what the gate's split really measures), §1.4 (the collider), §5 (the bias, established), §11.**
2. `C:/kyty/s81/README.md` — the standing traps, which grew by eight.
3. `C:/kyty/s81/pred/01_rcv.md` … `06_dapin.md`, `order.txt`, `pre_seal_note.md` — **do not edit
   them.** `pred/01` §0 says exactly what was on screen before it was sealed.
4. `C:/kyty/s81/PLAN.md` §3.0 — why the first attempt at the block was aborted, and the machine
   state that caused it.

**Check the byte count of anything large you read.** Reading through the rtk-rewritten shell
truncates silently.

**Harness:** port `C:/kyty/s81` → `C:/kyty/s82` with `C:/kyty/s81_port.py` as the model, roots
rewritten, `.txt`/`.json` **byte-exact**; session 81's one-off scripts stay unrewritten in
`prev81/scripts/`. `gates_base.txt` pins the same **99 names, 1092 bytes**, sha256
`4724bf812e8d095f21dc89b0e324fcf156e30d2614edcc35bb1623f9fe5f8c4f`. **Verify the port by
re-deriving session 81's twenty-run block table and session 80's twelve-run table before you use
it.**

## 1. What session 81 settled

* **The gate's split statistic is a mixture, not a resolution reading.** The attachment-weighted low
  mode — the statistic `guards.py` takes its own hard verdict on — differs between the arms by
  **−0.002 … +0.083 %** in **33 of 33** runs, while the mean-based split the gate judges reaches
  **+11.28 %**. `area_verdict.py` (session 77) tightened `guards.py`'s **advisory** 5 % limit on the
  mean into a hard 1.0 % gate; `guards.py` called it advisory because it is a mixture.
* **The high mode is a DRS resolution step**, not a flip-boundary artefact: attachment count and
  draws are unchanged across the modes (±2 %, ±1 %) and episodes last 11–40 flips, on the record
  and on twenty fresh runs. The explanation in `guards.py check_area`'s docstring is not supported
  by the two runs it cites.
* **The mixture the gate voids a run for is already removed by the pair matching.** Inside the
  matched-pair population the estimator actually reads, the arms' high-mode share differs by
  **+0.003 pp**, so the contamination in a quoted effect is **+0.00 µs**, bounded at 0.36 µs by the
  0.5 % pair tolerance. What the gate does protect against is the divergence between the pairs it
  keeps and the pairs it drops: **mean +72.0 µs, mean |Δ| 152.2, max +804.6** — an order of
  magnitude below what it costs. *(The CPU price of a high-mode flip is NOT IDENTIFIED: −43.1 µs at
  k = 2, +123.9 unconditional, +205.5 at k ≥ 3. Only the GPU side is stable, +12.7…+13.2 %.)*
* **The gate's bias is ESTABLISHED, prospectively.** On twenty fresh runs the void set reads
  **−499.6 µs [−903.3, −95.9]** more negative than the quoted set (R2 −525.0, R3 −381.8; means
  −1064.5 against −564.9). Session 80's in-sample +238.2 [−93.6, +570.0] was real and understated.
* **The vblank class is a collider.** Within k = 2 the treated arm carries **+1.94 % more draws in
  33 of 33 runs** (r = +0.9634 with the class spill), so the class-fixed endpoint is biased towards
  zero per flip and away from zero per draw — which is exactly session 80's unexplained
  B1-versus-V3 sign disagreement.
* **The sampler block at ten blocks: NOT RESOLVED.** C1 = −146.53 µs, paired-t p = 0.55; C2 (session
  80's own endpoint) = −96.04, p = 0.79. **+600.90 does not replicate.**
* **The gates convert CPU time into frame time nearly one for one in the pure CPU contrasts**, on
  matched pairs where the arms do the same work (+0.06 %): `pfhint` **Δdt −876.8 µs (+0.76 FPS)**
  against Δcpu −847.6, `pfcap` **−456.5 (+0.40)** against −452.9, A/A **−7.0 ± 91.6**. `dapin` is
  the exception at −893.9 against −713.4, because it also pays +207 µs of GPU.
* **`dapin` replicates at n = 3**: R2 −732.5 [−798.5, −666.4], and its GPU cost replicates a third
  time (+1.679 %, t = +19.17) and stays unexplained.
* **The guest-clock pacer is excluded** (armed: guest-on-host clock slope 1.000017) and its
  DRS hypothesis is refuted — with the pacer off, the resolution, the work and the frame rate are
  the record's to three digits.
* **The entry hang has an operation class**: 2 of 30 instrumented entries hung at exactly the
  historical 6.67 %, both with `requested − known = 1`, and the last sixteen CPU-recorded operations
  of both are **`EopWrite` from one submission**, ending at the same `ps` address.

## 2. What is settled — do not reopen

* **RCV is dead.** Restricting to the low rung cannot judge a third of the record (10–22 pp
  retention gaps) and readmits nothing. Do not rebuild it.
* **Do not quote a "class-fixed" number as a price.** k is a threshold on the outcome.
* **Do not call a per-draw figure work-normalised.** One present is one game frame; the arms' draws
  per flip agree to 0.06 %, so per-draw is per-flip rescaled.
* **The sampler is not a detectable contributor.** Two pre-registered blocks, 32 runs, now read
  +600.90 [−77, +1279] and −96.04 [−999, +807].
* **The pacer is not the source of the published effects**, and it does not drive the DRS ladder.
* **A sleeping display makes every measurement worthless** and no acceptance check sees it. Hold
  `ES_DISPLAY_REQUIRED` and send an input event before every run.

## 3. The work, by prize

### 3.1 The low-mode criterion — do this FIRST, it costs no run

The gate the programme uses judges the wrong statistic (§1). The harness already contains the right
one: `guards.py`'s attachment-weighted **p5 low mode** per arm, which is what the two arms actually
rendered.

*What to do:* pre-register it — **one line of `area_verdict.py`: replace the whole-arm mean ratio
with `wpct(area, att)` at p5, keep every threshold** — apply it to all 33 + 20 runs beside the
published gate, and state what it admits, what it still voids and on which criterion. Then decide,
in the pre-registration and not afterwards, **what the programme does with the +500 µs bias**: does
it restate the shipped figures over the larger admitted population, and what does it do about
τ ≈ 500 µs, which dominates either way? This is a zero-run analysis and it decides which runs the
programme may quote.

**Caveat to seal with it:** the low mode is also a *post-treatment* quantity — `pfhint` moves the
rung — so a criterion built on it is an admission rule, not an unbiased estimator. Say what it is.

### 3.2 How much of `cpu_gpu_us` is spin — NOT MEASURED, one run, no code

`cpu_gpu_us` is `QueryThreadCycleTime` on the GuestGpu thread: it excludes descheduled waits and
**includes spin**. Session 81 tried to price that by subtracting `rec_spin_gpu_us` and **retracted
it**: that counter is accrued on the **Record** thread (`CommandRecorder::SpinFor`), it is
0.81 × `dt_us` at r = +0.9915, and subtracting it flips the plain per-flip effect from −788.8 to
+58.7. The only GuestGpu-thread spin counter the record carries is `prot_spin_gpu_us`, and every
run is `KYTY_FRAME_TRACE=lite`. *Next:* one ABBA with **`KYTY_FRAME_TRACE=1`** so the per-thread
timers are populated, and a pre-registered decomposition; declare that the regime is not comparable
with the record's `lite` runs.

### 3.3 The one-vblank frame — one instrumented run, and a re-run of the sealed tests

Session 81 proposed a split into an "attribution shift" family and a "genuinely lighter" family and
**its own audit killed it**: the neighbouring interval carries one game frame's boundary markers in
1160 of 1160 triples, the within-class transfer is about a tenth of the claimed size with nothing
on the GPU, and the dt half of the conservation is an arithmetic identity of the family definition.
What survives is the sequence structure: a SHORT flip **never** follows a SHORT flip (0/6176),
follows a LONG one at MH RR 6.5 — **and precedes one at RR 28.3**, with n±5 placebos at 0.9, so the
association leans forward. *Next:* `KYTY_DUMP_FRAME` or `KYTY_GPU_TIME` over a window containing a
SHORT flip, with that forward asymmetry as the thing to explain; **and re-run `pred/02`'s T1–T7
over all 68 counter-carrying runs in the three sealed strata** — session 81 ran 39 runs in one
stratum and declared the deviation.

### 3.4 The entry hang's GPU side — ~15 minutes plus a decision

Thirty instrumented entries cost ~15 minutes and caught two hangs at 6.67 %. The CPU-recorded
history names the operation class (`EopWrite` × 16 from one submit, same `ps` address in both).
*Next:* either `KYTY_GPU_CHECKPOINTS=nv` (NV checkpoints, reported on the same path) or a source
change that calls `ReportGpuCheckpoints` on the hang path — **that is a rebuild, and it ends the
five-session run on one binary, so decide it deliberately**. And read what submit 1311/1325
contains at level entry: `KYTY_QUEUE_TRACE=1` is already on in every run.

### 3.5 `dapin` — the only candidate that buys FPS for no code

Three runs, **−732.5 µs [−798.5, −666.4]**, **+0.86 FPS**, and a **+1.679 % GPU cost replicated
three times and still unexplained**. It is not a pure placement contrast: `rp_begin` +3.43 %,
`rpa_re_kpx` +3.37 %, `prot_pages` +1.75 %, `submits` −1.51 %, all at t = 9…19. *Next:*
`KYTY_GPU_TIME` on one `dapin` pair to see which pass kind grows; and the design of a **mode**
(a topology query) to replace the raw mask 21845, which is a code change.

### 3.6 Free, already paid for

* **`cond81.py`** now covers **113 two-arm runs** across every root with the high-mode column
  computed after fragments are removed — session 80's two defects are fixed. Use it instead of
  `cond80.py`.
* **`guards.py` check 0 cannot see a sleeping display.** Add `GetLastInputInfo` and the monitor
  power state to `pre_run` and refuse such a run. Harness change, no measurement.
* **The `imgskip` contrast** is still +29.2 µs inside its own ±250 µs band; two runs a side.

## 4. Do NOT

**New, from session 81:**

* **Do not condition an estimator on anything the treatment moves** — the DRS rung and the vblank
  class both are. Conditioning the *criterion* is a different act from conditioning the *estimate*;
  say which you are doing.
* **Binning by draws is binning by the vblank class** (median bin k-purity 1.000), so a
  "work-matched" estimator is conditioning on the same collider. It is draw-count-matched, not
  work-matched — at equal draws the treated arm still does +4.8 % of `swbar` and +3.6 % of
  `rpa_a0` — and it buys −51.8 µs of frame time against −407.8 µs of CPU. Report the bracket
  (−65.5 per flip … −676.0 per draw), not a point.
* **A counter's name is not its thread.** `rec_spin_gpu_us` is the Record thread's; `cpu_gpu_us` is
  the GuestGpu thread's. Check the charge before differencing.
* **Price a contamination on the population the estimator reads**, not whole-arm.
* **A conservation ratio whose denominator is a multiple of the median frame time is an identity.**
* **Do not trust a pre-registered containment test that ignores state** — `pred/04`'s pacer rule
  compared a run against a record interval without conditioning on the 3-vblank share, and returned
  an outcome its own rules did not cover.
* **A prediction can be vacuous by construction** — `pred/01` P1.8 asked whether a readout moves
  between two criteria that compute it identically. Check every prediction against the design that
  will score it.
* **Write a zero-run pre-registration in place, hash it into a manifest before the first number, and
  make the analysis tool refuse to run against a changed hash.** There is no `<tag>.json` to anchor
  it otherwise.

**On the scoreboard:** session 81 scored **40 of 58 with a two-sided Poisson-binomial of 0.366 —
the first calibrated board in the record** (78: 9/24 all one way; 79: 21/22 worth nothing; 80:
20/23 at 0.0150, a failure in the "too many hits" direction). Three of its hits were vacuous by
construction and are named as such. Keep that standard: bands that can fail, and a scorer who ran
none of the analysis.

**Carried, all in force:** never compare between runs; confirm arming by a counter or a log line;
start at 1800, analyse from 2100; do not substitute a criterion that fails; finish a pre-registered
block even when its rule fires early; never ship `dawitloop` or `dawitness=0`; do not add a Knob
enum entry anywhere but immediately before `Count`; `gen_gates.py --with` keeps the **first**
`--with`; a knob value in a gate file is decimal; do not run other work on the machine during a
measuring run; quote the statistic the pre-registration names; compute power from the interval on
σ; print leverage, Spearman and a permutation p beside every r; run the within-state check; write
the pre-registration before the session's own runs and have an independent agent attack the result
afterwards.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the gate judges a mixture statistic | low mode +0.003…+0.083 % apart in 33/33; split up to +11.28 % | **ESTABLISHED** |
| the high mode is a DRS step | D1 ±2 %, D2 ±1 %, episodes 11–40 flips, on 33 + 20 runs | **ESTABLISHED** |
| what the gate protects | +0.00 µs of mixture inside matched pairs (bound 0.36); matched-minus-dropped +72.0 µs, max +804.6 | **MEASURED** |
| the gate's bias | **−499.6 µs [−903.3, −95.9]** on twenty fresh runs | **ESTABLISHED, prospectively** |
| the vblank class is a collider | +1.94 % draws within k = 2 in 33/33, r = +0.9634 | **ESTABLISHED** |
| the CPU sampler | C1 −146.53 p = 0.55; C2 −96.04 p = 0.79; +600.90 did not replicate | **NOT RESOLVED** |
| the guest-clock pacer | armed at slope 1.000017; effect larger, not smaller; DRS unchanged | **EXCLUDED** |
| `pfhint` in frame time | Δdt −876.8 µs → **+0.76 FPS** | 33 runs, matched pairs |
| `pfcap` in frame time | Δdt −456.5 µs → **+0.40 FPS** | 4 runs |
| `dapin` in frame time | Δdt −893.9 µs → **+0.86 FPS**, +207 µs GPU | 3 runs, not pure |
| the entry hang | 2/30 at 6.67 %; sixteen `EopWrite` from one submit | **operation class known** |
| the headroom screen | r = −0.9211 over 20 fresh runs, −0.8868 / −0.7473 within state | **replicated** |

**The honest statement of the task.** Session 80 found that the programme's endpoint is a frame-time
statistic. Session 81 found that both repairs proposed for it condition on consequences of the
treatment, that the gate deciding what may be quoted rejects a third of the record to avoid five
microseconds of contamination while costing a factor of 1.9 in the size of what it reports, and
that the gates do convert CPU time into frame time nearly one for one. **Three shipped gates are
worth about 2.2 ms of frame time together. The gap to 60 FPS is 18.3 ms, and nothing in the record
suggests it is hiding in the endpoint definitions any more.**
