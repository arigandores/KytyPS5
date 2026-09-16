# Session 77 — FACTS

**Single source of truth for session 77.** Every number here was produced by running the named tool
on the named log. Where a number is an estimate it says so in those words. Where something was not
measured it says NOT MEASURED and names what would measure it. Predictions, results and every
retraction in order: **`C:/kyty/s77/PREDICTIONS.md`** (50 056 bytes — read it with a byte count,
see the trap in §8).

Tree: `merge-upstream`, base `aefbbc8`. Code changed this session: **comments only**, in four files,
**60 insertions / 60 deletions**, every replacement preserving its block's line count.

---

## 0. In one sentence

The session **localised a shipped CPU win for the first time in the programme's history**
(`cap77a`: the whole −397 µs sits inside the render mutex, −260 µs of it in the binding phase),
**re-took `pfcap` with both arms compile-time**, **took `pfhint` four times to get two more valid
runs** — and then found the thing that matters more than either gate: **across area-valid runs of
the same configuration the two gates disagree at I² = 66 % and 95 %, so every figure this
programme has ever shipped carries an error bar three to five times too small.**

---

## 1. The runs

| tag | what | validity | result |
|---|---|---|---|
| `pfh77a` | ABBA `pfhint=0\|1`, period 30 | **VALID** — rung 0.0 %, split +0.001 %, 118/118, work −0.028 % | `cpu/draw` −2.129 % ± 0.242, t = −17.59 |
| `pfh77b` | same, period 15 | **VOID** — split **+14.582 %**, 15/226 | nothing quoted |
| `pfh77c` | same, period 30, exact repeat of `pfh77a` | **VOID** — split +8.014 %, 18/114 | nothing quoted |
| **`cap77a`** | ABBA `pfcap=192\|1024`, both arms compile-time, `mutsite=1 pxstat=1` | **VALID** — rung 0.0 %, split −0.002 %, 124/124, work +0.092 % | `cpu/draw` −1.305 % ± 0.135, t = −19.28 **+ the localisation** |
| `pfh77d` | ABBA `pfhint=0\|1`, period 30 | **VALID** — split +0.531 %, 112/114, work +0.081 % | `cpu/draw` −2.319 % ± 0.239, t = −19.42 |
| `curve77a` | 8 arms, `pfcap` 192…4096, no ABBA | ratios only | the whole release curve |
| **`acc77a`** | acceptance, 300 s, video | **8 PASS, 0 FAIL, 1 WARN, 3 SKIP, VERDICT PASS, 0 one-frame glitches** | the base |

Seven runs. Six entered Sky Garden at the first attempt in 14.8–17.3 s. **One entry hang**
(`curve77a` attempt 1, §7). `guards.py` check 2 reads **11/11** on every run; check 10 confirms the
binary and every `GateArm` block on every scheduled run. `pfh77d` is the only run with a clean
guard verdict: **10 PASS, 0 FAIL, 0 WARN**.

**Base (`acc77a`, 9595 settled flips):** draws/frame **5041.66**, `cpu/draw` **6.2137 µs**,
`cpu_gpu_us` **31 327**, `gpu_busy_us` **14 507**, `dt_us` **32 025**, **31.23 FPS**.
**Do not compare these absolutes with `acc76a`'s.** No executable code changed this session
(§6), so any difference is run-to-run variance — which is exactly what §3 is about.

---

## 2. The localisation — the first in the programme, and its caveats

`cap77a`, 124 area-matched pairs, `mutsite=1` and `pxstat=1` in **both** arms, analysed with
`paired_counters.py` (paired adjacent blocks, 2·SE and t on every counter):

    a_hold_us      27 520.2 -> 27 123.5   -396.7 +- 69.3   t = -11.44    the whole render mutex
      mh_bind_us   10 546.7 -> 10 287.0   -259.7 +- 30.8   t = -16.87
      mh_prog_us    5 894.4 ->  5 714.5   -179.9 +- 21.2   t = -17.01
        da_take_us  2 476.3 ->  2 405.7    -70.5 +- 14.7   t =  -9.60    AheadTake, nested in prog
      px_on_bind_us 6 012.9 ->  5 930.7    -82.2 +- 16.9   t =  -9.73    nested in bind
      px_off_bind_us  331.6 ->   331.6     +0.0 +-  0.6    t =  +0.01
      mh_emit_us    7 343.4 ->  7 377.7    +34.3 +- 19.3   t =  +3.55    the only phase that COSTS
      mh_pro_us +0.8, mh_rt_us +2.5, mh_tail_us +0.7, mh_disp_us +4.3, mh_pres_wait_us +5.6

**The instrument was checked before the numbers were read.** `mh_n + mh_disp_n == a_hold_n`
**exactly** in both arms (5303.6, 5308.8); `sum(mh_*)` covers `a_hold_us` to **99.650 %** and
**99.645 %**, matching session 69's 99.68–99.69 %; and **the sum of the seven phase deltas is
−396.8 µs against `a_hold_us`'s −396.7 µs, a gap of 0.1 µs.**

**What is MEASURED:** the whole gain is inside the render mutex, and it divides **−260 µs in the
binding phase, −180 µs in the program phase, of which −70 µs is inside `AheadTake`.**

**What is NOT ESTABLISHED, and was corrected by the audit:** the per-vector account
("five snapshot vectors → bind, two specialization → prog, four witness → `AheadTake`") is an
**interpretation**, not a measurement. Three phase numbers cannot identify eleven vectors,
`snapshot.buffers` is in fact read inside `mh_emit_us`, and no arm in the record has ever
prefetched a subset. *What would make it a measurement:* a knob taking a **bitmask of which of the
eleven vectors to prefetch** — a few lines, with `da_pf_b` splitting by mask as the arming proof.

**Three caveats, all found by the audit and none of them dismissed:**

* **`cap77a` carries ~0.4–0.6 ms/frame of its own timer instrumentation inside the path under
  test — more than the 0.386 ms effect.** "It cancels because it is in both arms" covers an
  additive main effect, not an interaction with prefetch **timeliness**, and such an interaction
  would point the same way as the result. `cap77a` is the only `pfcap` run carrying it and it is
  the largest of the three. **The localisation has zero replication.**
* **`cap77a`'s guards check 6 failure is NOT symmetric** — six of seven offending groups are in
  arm1, five of them high — so session 74's "symmetric host noise inflates variance without
  biasing" does not license calling it noise here.
* **`mh_emit_us` is below the programme's own significance bar** on the check-6-clean subset
  (+23.2 ± 21.7, t = +2.14). It is nevertheless the one phase where the mechanism predicts a cost —
  the L1 displacement the gate necessarily causes — so it belongs in the accounting:
  −431 µs in prog+bind against +23…+34 µs in emit, netting −397 µs.

**What it points at.** `mh_bind_us` is **10.5 ms a frame**, the largest phase inside the render
mutex, and the programme has never attacked it. But `px_on_bind_us` covers 6.0 ms of it and carries
only −82 of the −260 µs: **the 4.2 ms that `pxstat` does not cover carries 68 % of the delta.**
Whatever is worth attacking in the binding path is mostly *outside* `PrepareGraphicsBindings`.

---

## 3. The finding that outranks both gates: the error bars are 3–5× too small

Three area-valid runs now exist for each shipped gate. **Quoted on the matched-pair population**
(the one validity licenses — quoting the wall over all blocks while deciding validity on the
matched subset was one of the audit's corrections):

| gate | run | matched pairs | wall delta |
|---|---|---:|---:|
| `pfhint` | `pfh76c` (s76) | 109 | −257.3 ± 133.5 µs, t = −3.86 |
| | `pfh77a` | 118 | **−690.2 ± 87.8**, t = −15.72 |
| | `pfh77d` | 112 | **−734.3 ± 103.8**, t = −14.15 |
| `pfcap` | `cap76a` (s76) | 126 | −294.1 ± 93.1, t = −6.32 |
| | `cap76b` (s76) | 231 | −238.2 ± 91.2, t = −5.22 |
| | `cap77a` | 124 | **−381.8 ± 79.8**, t = −9.57 |

    pfhint  random-effects  -565 us   95 % CI [-824, -305]   I^2 = 94.6 %   tau = 223 us
    pfcap   random-effects  -307 us   95 % CI [-392, -222]   I^2 = 65.7 %   tau =  61 us

**The between-run standard deviation τ is 223 µs for `pfhint` and 61 µs for `pfcap`, against
within-run 2·SE of 88–134 µs and 80–93 µs.** Session 76 wrote that `cap76a` and `cap76b` "agree,
0.167 pp apart against a combined 2·SE of 0.225 pp"; pairwise that is true, and adding `cap77a`
gives Q = 16.8 on 2 df. **The pairwise agreement of two runs was luck.**

**Every shipped figure in the programme's table rests on one or two runs quoted with a within-run
2·SE** — s72's 0.33 ms, s73's 1.268 / 0.19–0.23 ms, s74's 0.31–0.32 ms, s76's two. **None of those
intervals is the uncertainty of the quantity; each is the uncertainty of that run.**

**The variable behind τ is NOT IDENTIFIED.** Tested and excluded this session: the DRS rung (every
matched pair of all three `pfhint` runs is a low-rung pair), thermal state (`gpuclk` medians 70.0
vs 71.0 °C, 81.3 vs 82.6 W, 2467 vs 2482 MHz), the `pfcap` state (94.4 % in all arms), biased pair
dropping (`pfh76c`'s 12 dropped pairs read −0.472 % ± 3.119 %), and per-pair covariates (pooled
585 matched pairs: corr with `gpu_busy_us` −0.104, with area −0.068, with baseline CPU −0.232).
**A pace hypothesis was raised and then withdrawn** — the audit showed it is division bias
(`dt_us` contains `cpu_gpu_us`) and that matching pace on an unbiased covariate makes the
disagreement *worse*. **The harness records no CPU-side telemetry at all** — every column is
nvidia-smi — which is the most likely place the variable is hiding.

---

## 4. The two shipped gates, restated

| article | axis | estimate | 95 % interval | evidence |
|---|---|---:|---|---|
| `pfcap` 192 → 1024 (at `pfhint=1`) | CPU | **0.31 ms** | [0.22, 0.39] | 3 area-valid runs, I² = 66 % |
| `pfhint` 0 → 1 (at `pfcap=1024`) | CPU | **0.56 ms** | [0.31, 0.82] | 3 area-valid runs, I² = 95 % |

**Their sum is NOT MEASURED and must not be formed by addition** — each is an increment measured
with the other gate on in both arms, and the one run that tried the total (`both76a`) is void.

Session 76's `pfcap` figure (0.29–0.31 ms) **turns out to have been right, for reasons that were
wrong** (§5). Its `pfhint` figure (0.25 ms) was **less than half** the pooled estimate and lies
outside its interval.

**`pfh76c` is not dropped.** The rule written before `pfh77d` said "two agree, revise up, record
the third as an outlier", and applied literally it gives `pfhint` = 0.69–0.73 ms. It is not
applied, because dropping the run that disagrees is the move session 76 was condemned for and
because I² = 95 % says the three runs are not estimating the same thing — a fact about the stand,
not about `pfh76c`. **Both readings are printed; the random-effects one is the one to quote.**
No validity criterion was weakened to get there; what changed is the estimator over the runs that
passed.

---

## 5. What session 76 got wrong about `pfcap`, and what session 77 then got wrong about that

Session 76 called −0.29…−0.31 ms a **lower bound** because "the winning arm reached the prefetch
through the runtime, **non-unrolled** overload". **That reason is false.** Disassembling the
installed binary and attributing through the map file, per vector per cache-level branch:

| instantiation | address range | shape | min against | prefetches |
|---|---|---|---|---:|
| `<192>` | 0x843429–0x84392d | peeled, 3 guarded prefetches at 0 / 0x40 / 0x80 | immediate `0xc0` | 3 |
| **`<1024>` (shipped)** | 0x842eb0–0x8433c9 | **ROLLED** loop, 4 instructions per line | immediate `$0x400` | 1 |
| runtime overload | 0x84395c–0x844852 | **runtime-unrolled by 8** + rolled remainder | **register** | 9 |

`11×3 + 11×1 + 11×9 = 143` = the measured 143 `prefetcht0` and 143 `prefetcht2` in `AheadTake`;
and session 76's own "+66 of each form" for its all-runtime build = `11×(9−3)`. **The winning arm
ran the unrolled loop, not a non-unrolled one.**

**Session 77 then claimed this made the figure an UPPER bound. That was wrong too, and was
corrected by an adversary before any run.** The runtime form also pays ~13 extra fixed instructions
per non-empty vector, repaid only above eight lines, and the mean vector is ~124.6 B ≈ 2 lines —
so the sign of the shape term is **undetermined** and its magnitude is bounded to roughly
−13…+70 µs against a stand that resolves 53 µs.

**`cap77a` settled it empirically instead:** with both arms compile-time the effect is −381.8 µs,
larger than the biased runs' −294 and −238. The shape term is not what separates them; §3's τ is.

---

## 6. The documentation debt — seven sites, and a stronger verification than the programme had

Session 76 deliberately left comments wrong rather than rebuild after acceptance. There were
**seven** sites, not the three recorded, and two of them stated **retracted** numbers as if they
were measurements: `gates.cpp:174-193` justified the shipped `pfhint` from `pfh76a` and `pfh76b`
alone — the two runs session 76 itself voided — and asserted "THE SHIPPED FIGURE IS 0.41-0.48 ms";
`pipelineCache.cpp:2711-2714` repeated it and said "pfcap still defaults to the 192", eleven lines
above `:2725-2729` which already said 1024 shipped. **The file contradicted itself inside one
function.**

All seven are fixed (`patch_docdebt.py`), and two statements session 77 itself wrote were then
corrected after adversarial attack (`patch_docdebt2.py`). **Every replacement preserves its block's
line count**, which makes the verification exact:

> `.text`, `.data`, `.pdata`, `.tls` and `.reloc` are **byte-identical** to `79680f59`.
> Only **23 bytes of `.rdata`** differ, and they are the embedded git-describe tag, the fork build
> title, the debug-directory timestamp and the `RSDS` PDB GUID. **No instruction changed.**

That is stronger than the prefetch-opcode histogram the programme has used, and it works only
because `__LINE__` is materialised as an immediate in `.text` at every `EXIT_IF` site
(`KYTY_FINAL` is never defined here), so a line-count change would move thousands of immediates.
41 compiler warnings, **all pre-existing**, none in a hunk of this diff. Re-verified after a forced
recompile of all four touched translation units. **The exe hash is NOT reproducible across links**
(the PDB GUID is regenerated), so it is recorded per run in each `<tag>.json`.

---

## 7. Free items and negative results

**The cap release curve, measured in one run with no code** (`curve77a`, eight arms; the `pf`
lambda computes `min(total, cap)` regardless of which overload ran, so the ratio is exact):

| `pfcap` | 192 | 256 | 384 | **512** | 640 | 768 | **1024** | 4096 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| released | 58.91 % | 67.00 % | 77.85 % | **83.95 %** | 87.48 % | 90.01 % | **94.40 %** | 99.99 % |
| lines/frame | 115 618 | 130 929 | 152 691 | 164 417 | 171 608 | 176 029 | 184 940 | 195 430 |

`da_hit` 8624–8645 and `da_pf_b` 12.51–12.56 MB in every arm: the eight arms were offered the same
work. **The pre-registered rule was "write a `<512>` branch only if 512 releases ≥ 88 %". It
releases 83.95 %, so the branch is not written and the idea is closed.** *(An arithmetic argument
that 512 would cost ~37 µs was withdrawn — it was a cross-run subtraction of a mislabelled rate.
The decision rests on the pre-registered release rule alone.)* **This curve is also an unused
measurement of the per-vector size distribution** — the truncation curve inverts to the size
histogram of the eleven vectors, which nothing else in the record gives.

**W4 is not a lever on the 0.98 ms.** `daprefetch` is read once (`pipelineCache.cpp:2706`) and its
block closes at `:2777`, before `VerifyWitness` at `:2795`, so `dpf75a`'s +976 µs belongs entirely
to the eleven-vector block. W4's guest-line prefetch lives inside the `dawitptr` bundle. The brief's
distance statement is also inverted: the tree prefetches all live runs then compares all live runs,
so run 0 has the **least** lead and the last run the most. Population 6.36 live runs per take.

**The GPU axis has no cheap step.** `gpu_busy_us` 14.5 ms against a 32.0 ms wall; the only shipped
GPU change passed through to the wall at under 4 %. C2 rescales post-C1 to ~0.20–0.25 ms of GPU
≈ 8–10 µs of wall, an order below the `dt_us` resolution. **Not worth a session until CPU is
below ~18 ms.**

**An entry hang, unexplained.** `curve77a` attempt 1:
`GpuHangAbort: role=4 requested=3196 known=3195 current=3289 after=8s`, with
`submit_backlog=0 record_backlog=0 acopy=2866/2866/2866 acopy_pending=0` — **not** session 58's
`acopyidle` failure mode and not a backlog; the GPU was ahead at 3289 while the known-completed
marker stuck at 3195. The harness retried on its own and attempt 2 entered in 15.3 s. Log kept as
`log_curve77a_a1.txt`. The audit's view, which is accepted: this should have been chased, because
the corrected reading makes it **configuration-independent and unexplained** rather than a known
nuisance, and `KYTY_GPU_CHECKPOINTS=1` would have named the failing operation.

**`aa77a`, the A/A control, was pre-registered and never taken** — dropped in favour of a fourth
`pfhint` attempt when three of the first five runs came back void. What partly replaces it:
`pfh77a` (+0.001 %) and `pfh77c` (+8.014 %) are the **same configuration on the same binary**,
which shows directly that the rung is a property of the run, not of the gate.

**A harness finding:** the rung state is decided in the first ~600 settled flips and holds
(`pfh77a` 0.0 % in every decile; `pfh77c` and `pfh77b` oscillating from the start). An early abort
is therefore possible and would save ~4.5 minutes of the ~6 a void run costs — but only ever to
ABORT on a bad start, never to ACCEPT on a good one (`pfh76c` started quiet and still drifted).

---

## 8. Tools, traps and checks

**New this session, both validated against known ground truth:**

* **`area_verdict.py`** — the validity gate. Prints the whole-arm `rt_kpx/rt_att` split **against a
  threshold that fails** (`guards.py` check 3b computes the same quantity but judges it against an
  **advisory 5 %** limit, which is why session 76's +2.191 % passed), the high-rung share, the pair
  match rate, and the population beside every ratio; refuses to print anything for a missing input;
  and **separates VALIDITY from SIGNIFICANCE** so that a valid null run is not reported as
  unquotable. Reproduces session 76 FACTS §2 exactly.
* **`paired_counters.py`** — paired adjacent-block differences with 2·SE and t for any counter.
  `xstat.py --arms` prints per-arm totals with no error bar, so no `mh_*` or `da_take_us` delta in
  the record before this session could be called significant or insignificant. It reproduces
  `cap76a` −0.869 %/126 pairs and `pfh76c` −0.882 %/109 pairs exactly, and flags a counter that is
  present-but-identically-zero instead of reporting it as a measurement. **It gave the bracketing
  timer an error bar for the first time:** `cap76a` −1.8 ± 10.8 (t = −0.34) against `pfh76c`
  −130.7 ± 21.2 (t = −12.35).

**Traps found this session:**

* **Reading a large file through this shell's rtk rewrite returns it TRUNCATED.**
  `PREDICTIONS.md` came back as 702 lines / 46 171 bytes against the real 764 / 50 056, and what it
  silently dropped was the **last** section — the one carrying the retractions. An auditor reading
  it that way took a retracted intermediate figure for the conclusion. **Read final documents with
  an explicit byte count and check it.**
* **`gen_gates.py --with` is `nargs='*'`, not `append`** — `--with a=1 --with b=1` silently applies
  only `b=1`, and the tool's own confirmation line lists only the survivor. Write `--with a=1 b=1`.
* **A count check can pass while the attribution is backwards.** `11×8+11×3+11×1+11×1` and
  `11×3+11×1+11×9` both sum to 143; only the `min()` operand distinguishes the instantiations.
  This session's first opcode note got it wrong and its own predictions file got it right — the
  same self-contradiction it was criticising session 76 for.
* **Instrumentation inside the path under test does not "cancel" just because it is in both arms.**
  It cancels as an additive main effect; it does not cancel as an interaction.
* **Quoting the wall over all blocks while deciding validity on matched pairs** is the metric/
  population mismatch of session 76's §5.5 in a new dress.
* **Two runs agreeing is not a tight estimate.** `cap76a` and `cap76b` agreed to 0.167 pp and the
  three-run I² is 66 %.

**Checks:** clean builds, 0 errors, no new warnings; `.text` byte-identical (§6). Test binaries were
**not** re-run and do not need to be: the executable code is provably unchanged, which is a stronger
statement than a passing test.

---

## 9. The arithmetic, restated

**Today** (`acc77a`): CPU **31 327 µs**, GPU **14 507 µs**, wall **32 025 µs**, **31.23 FPS**.

| article | axis | measured | state |
|---|---|---:|---|
| `dawitptr` + `daepceil` | CPU | 0.33 ms | shipped s72 — **one run, interval too narrow (§3)** |
| `imgfuse` (C1) | GPU / CPU | 1.268 / 0.182 ms | shipped s73 — same caveat |
| `dawitcp` (W7) | CPU | 0.19–0.23 ms | shipped s73 — same caveat |
| `dawitcg` (W8) | CPU | 0.31–0.32 ms | shipped s74 — same caveat |
| **`pfcap` 192 → 1024** | **CPU** | **0.31 ms [0.22, 0.39]** | **3 area-valid runs, I² = 66 %** |
| **`pfhint` 0 → 1** | **CPU** | **0.56 ms [0.31, 0.82]** | **3 area-valid runs, I² = 95 %** |
| both together | CPU | NOT MEASURED | do not add |
| cap below 1024 | CPU | closed | 512 releases 83.95 % < the pre-registered 88 % |
| cap above 1024 | CPU | closed | `cap76c` +0.200 %, inside its own predicted band |
| where the `pfcap` gain lands | — | **MEASURED** | bind −260, prog −180 (of which `AheadTake` −70) |
| which vector buys it | — | NOT ESTABLISHED | needs a prefetch bitmask knob |
| **the between-run variance τ** | — | **223 µs / 61 µs** | **the variable is NOT IDENTIFIED** |
| W4 (prefetch distance) | CPU | not a lever on the 0.98 ms | closed by reading |
| `mh_bind_us` | CPU | 10.5 ms/frame | **never attacked; 68 % of its delta is outside `pxstat`** |
| C2 / the GPU axis | GPU | ~8–10 µs of wall | not worth a session until CPU < 18 ms |

**The conclusion.** Two gates were re-measured and one was localised, but the session's real result
is the one it did not set out to find: **the programme's stand has a between-run variance it has
never measured and never controlled, and it is three to five times the error bar every shipped
figure is quoted with.** Finding that variable is now worth more than any single gate on the list —
and the first thing to try is instrumenting the CPU, which this harness does not measure at all.

Commit **45fd423** (branch `merge-upstream`, base `aefbbc8`, 6 files, +60 / -60 in source
plus two docs), not pushed. Report: `C:/kyty/s77/FACTS.md` (the single source of truth),
`C:/kyty/s77/README.md`, in git `docs/local-session-77.md`; the next prompt is
`docs/next-session-78.md`.
