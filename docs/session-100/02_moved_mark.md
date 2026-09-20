# Sealed pre-registration 02 — session 100, route E, M3: the moved-mark census

**Immutable once written.** A correction goes into a new sealed addendum, never into this file.
Written before any `blmove` measurement exists. It does not edit, weaken or re-score
`pred/01_addend_census.md`; `cen100b` and its GAP stand exactly as published.

---

## 0. Why a second instrument, stated from the first one's own result

`cen100b` was admitted under `pred/01` with 19/19 technical and 6/6 strict controls,
90 pairs, 2 610 rows an arm, and returned **GAP**. Its numbers:

    T1 images  1.664154   (48 013.674 image slots a flip x 34.66 ns)
    T2 writable 0.4905    (sealed s94)
    T3 samplers 0.337034  (bl_smp_us)
    T4 shader data 0.404808 (bl_sd_us)
    T5 sync    0.1035     (sealed s98)
    ADDEND_hi  2.999996   -> VERDICT_INPUT 15.824996 … 17.273996   (would be CLOSE)
    C          0.436552   -> ADDEND_lo 2.563444 -> 15.388444 … 16.837444 (below 15.5)
    => the two branches disagree => GAP, short by 0.111556 ms on the conservative branch

The whole remaining gap is the **price of the instrument that measures T3 and T4**, not the
quantity itself: `bindlap` pays four timestamps and five `Add`s a stage, and `pred/01`
deliberately subtracts that whole cost from T3+T4 because it could not tell how much of it
falls inside their spans.

This rule removes the estimate instead of tightening it. The session-88 idiom (`bindwit`,
"the mark MOVED rather than added … so the price of the mark cancels EXACTLY in the arm
difference and never has to be estimated") is applied to the same two spans.

---

## 1. The instrument, and why its price cancels

Gate **`blmove`** (`KYTY_BIND_LAP_MOVE`, default 0, MEASUREMENT ONLY, added in session 100,
`gates.cpp` LAST row, `check_gate_order.py` clean before the build). Inside
`RenderExecutor::PrepareBindings`:

* one timestamp `blm_t0` is taken immediately before the image loop, in **both** phases;
* **phase 0** closes right after the image loop: span0 = the image loop;
* **phase 1** closes right after the `shader_data` copy: span1 = image loop + sampler loop +
  `shader_data` copy;
* each phase then writes **exactly four** counters. Two timestamps and four `Add`s a stage in
  both phases, at different program points.

Therefore `span1 − span0` is the sampler loop plus the `shader_data` copy **with the price of
the opening mark, the closing mark and the four `Add`s cancelling term by term**. Nothing is
estimated and nothing is subtracted.

The phase alternates **per stage type** (`blm_turn[stage % 16]++ & 1`), the `previous_key`
idiom already in the file, so every stage type contributes equally to both spans and the
difference is not a comparison of unlike stages.

**`blmove` must run with `bindlap` OFF.** `bindlap`'s own mark after the image loop sits
inside span 1 and outside span 0, which would put its price back into the difference. A run
in which any `bl_*` counter is non-zero is refused.

---

## 2. The quantities

Per retained armed **block** (never per row — ratios of small counts are not an estimator):

    s0  = sum(blm_s0_ns) / sum(blm_s0_n)            ns a stage, phase 0
    s1  = sum(blm_s1_ns) / sum(blm_s1_n)            ns a stage, phase 1
    stages_per_flip = (sum(blm_s0_n) + sum(blm_s1_n)) / rows_in_block
    img0ps = sum(blm_img0) / sum(blm_s0_n)          image slots a stage, phase 0
    img1ps = sum(blm_img1) / sum(blm_s1_n)
    smp0ps = sum(blm_smp0) / sum(blm_s0_n)          sampler slots a stage, phase 0
    smp1ps = sum(blm_smp1) / sum(blm_s1_n)
    smpALL = (sum(blm_smp0) + sum(blm_smp1)) / (sum(blm_s0_n) + sum(blm_s1_n))

    T34_block = (s1 - s0) * stages_per_flip / 1e6                       ms a flip
    T1_block  = (sum(blm_img0) + sum(blm_img1)) / rows * 34.66e-6       ms a flip

and the published value of each is the **median over the retained armed blocks**, the
estimator of `pred/01` §4 and `pred/02` §3 of session 99.

`T1` uses the **sealed session-88 unit cost 34.66 ns** exactly as `pred/01` did; only the
population is measured. `T2 = 0.4905` and `T5 = 0.1035` stay sealed and are not measured.

### 2.1 The residual-bias bound B

The two phases are balanced by construction but not identical. The leftovers are bounded, not
assumed away:

    B_img = |img1ps - img0ps| * (s0 / img0ps) * stages_per_flip / 1e6     ms a flip
    B_smp = |smp1ps / smpALL - 1| * T34_block                             ms a flip
    B     = B_img + B_smp        (median over the retained armed blocks)

`B_img` prices the image-slot imbalance at the phase-0 image time per slot — the only price
for an image slot this instrument measures. `B_smp` prices the sampler-population imbalance
against the whole measured difference, which is an over-estimate because the `shader_data`
half of `T34` carries no sampler dependence at all.

---

## 3. The rule

    ADDEND_hi = T1 + 0.4905 + T34 + 0.1035
    ADDEND_lo = T1 + 0.4905 + max(0, T34 - B) + 0.1035
    VERDICT_INPUT_i(X) = F_i + X,   F_a = 14.274, F_c = 12.825   (session 98, NOT re-measured)

* **CLOSE** — G and R1 closed — iff `min_i VERDICT_INPUT_i(ADDEND_hi) >= 15.5` **and**
  `min_i VERDICT_INPUT_i(ADDEND_lo) >= 15.5`.
* **PROCEED** — iff `max_i VERDICT_INPUT_i(ADDEND_hi) <= 11.0`. **Unreachable**, written for
  completeness only.
* **GAP** — every other case, including the two branches disagreeing. Global M3 stays open,
  G and R1 stay alive and unlicensed, the order M3 → M4 → M5 is untouched.

Thresholds, `F_a`, `F_c`, the min/max form, `T2` and `T5` are **identical to `pred/01`**, which
is itself the sealed rule of `ROADMAP.md:1081-1082` as amended by the user in session 98. The
only change from `pred/01` is that `T3 + T4` is measured by an instrument whose price cancels,
so the conservative branch subtracts a **bounded imbalance** instead of a whole instrument.

### 3.1 What the arithmetic would be on `cen100b`'s values, declared before the run

`cen100b` measured `T1 = 1.664154` and `T3 + T4 = 0.741842`. If `blmove` reproduces them and
`B` is small, `ADDEND_hi = 3.000` and `ADDEND_lo = 3.000 − B`, so the branch is **CLOSE for
any B below 0.325 ms** and GAP above it. **This is visible to the author before sealing and is
written here so the seal is not read as a blind test.** What the run decides is (i) whether the
moved-mark difference reproduces 0.7418 ms at all — it is a different estimator on a different
binary and may not — and (ii) whether the phase imbalance `B` really is small. Both can fail.

A reproduction of `T1` within 1 % of `cen100b`'s 48 013.674 image slots a flip is also a
cross-instrument check that costs nothing and is reported either way.

---

## 4. Population, protocol and arms

Population, selector and estimator: **exactly `pred/01` §4**, carried unchanged (period 90,
start 1800, `scheduled[60:89]`, first frame 2100, complete ABBA quartets, ≥ 30 pairs for a
measurement and ≥ 10 for a pilot, median over blocks of the block value).

    base arm  : blmove=0
    armed arm : blmove=1

    KYTY_GATE_SCHEDULE="90+1800:blmove=0|blmove=1"   KYTY_GATE_SCHEDULE_ABBA=1
    KYTY_GPU_CLOCK_PIN=1  KYTY_GPU_MARKERS=0  KYTY_GPU_CHECKPOINTS=0
    KYTY_BIND_FLOOR_LATCH=0  KYTY_BIND_FLOOR_CLEAR=0
    KYTY_REC absent entirely

`--gates-file C:/kyty/s100/gates_base.txt` (1 092 B, 99 names — `blmove` is the 34th name
absent from it and lives only in the schedule arms), `--attempts 1`, `--pred` this file.

**Sequence:** pilot `mov100a --hold 300`, then, only if it is admitted, a fresh confirmation
`mov100b --hold 900`. The verdict comes from the confirmation alone. A pilot is not a retry.
Entry hangs are recorded as `mov100a_entry1` / `_entry2`, at most two, same protocol, no
cache-policy change to obtain success.

**Binary.** This rule is measured on the session-100 build
`6f7475b8a6b9636aa31938d97f26c1bd4b7dbfd97213dd01b99b8cd3109268c0`, which adds `blmove`, the
two `clr_taken_*` counters and nothing else. At every default it is byte-equivalent in
behaviour to `34206e3f…`: no gate default moved, no knob default moved, no shipped path
changed. `cen100a`/`cen100b` were measured on `34206e3f…` and are **not** re-scored here.

---

## 5. Controls. Every `pred/01` control is carried unchanged; these are added.

| name | limit |
|---|---|
| `BINDLAP_OFF` | every `bl_*` counter is 0 on **every** row of the raw log |
| `BLMOVE_DARK` | each of `blm_s0_ns blm_s0_n blm_s1_ns blm_s1_n blm_img0 blm_img1 blm_smp0 blm_smp1` sums to ≤ 0.001 x its armed sum on the unarmed arm |
| `BLMOVE_ARMED_POSITIVE` | all eight are > 0 on the armed arm and on **every** retained armed block |
| `PHASE_BALANCE` | \|blm_s0_n / blm_s1_n − 1\| ≤ 0.01 on every retained armed block |
| `IMAGE_BALANCE` | \|img1ps / img0ps − 1\| ≤ 0.01 on every retained armed block |
| `SAMPLER_BALANCE` | \|smp1ps / smp0ps − 1\| ≤ 0.01 on every retained armed block |
| `SPAN_ORDER` | `s1 > s0` on every retained armed block (span 1 strictly contains span 0) |
| `T34_POSITIVE` | the published `T34` > 0 |

plus, from `pred/01` §6 verbatim: `SCHEMA`, `STREAMS_COMPLETE`, `RAW_CONTIGUITY`, `GATEARM`,
`NO_FLOOR`, `MARKERS_OFF`, `PIN_ON`, `CRASHES`, `SURVIVAL`, `NO_RECORDING`, `IDENTITY`,
`DURATION`, `PREREG_PINNED`, `COMPLETE_PAIRS`, `AB_BA_BALANCED`, `RETAINED_ROWS`, and the six
strict controls `AREA_SPLIT` < 1 %, `AREA_MATCH` ≥ 90 %, `WORK` < 0.5 %, `C5` ≤ 0.02,
`C9` ≤ 0.03, `RETAINED_DATA`. **Not one limit is widened.**

Reported, never deciding: `guards.py --first-frame 2100` (check 6 is not a criterion),
`area_series.py` + `area_verdict.py`, `summary4.py --blocks`, `endpoint84.py`, the instrument's
own ABBA cost `C_blmove` (reported for comparison with `bindlap`'s 0.4366 ms, **never
subtracted** — that is the whole point of the moved mark), and `clr_taken_meta` /
`clr_taken_img` with their per-flip dispatch denominator.

The scorer is dry-run on existing logs and on synthetic fixtures, and a fixture that should
fail each control is shown to fail it, **before** the first `blmove` run. The published numbers
are re-derived by a separate recount script that shares no code with the scorer.

---

## 6. What no outcome of this rule may be used to claim

* That `F_a`/`F_c` were re-measured, or that `cen100b`'s GAP was revised. It was not: this is a
  different instrument under a different seal, and both results are published side by side.
* That a CLOSE proves 60 FPS unreachable. It closes **G and R1** by the sealed rule;
  `ROADMAP.md:46` stands.
* That the mark price cancelling is a proof that `blmove` is free. It is a proof that its price
  cancels **in the difference**; its total cost is still reported as `C_blmove`.
* That M4 or M5 may be skipped or re-ordered, or that session 99's `B_a`/`B_c` enter here.
* That the DRS clock debt, the residual pessimism of the mode-2 floor, the cross-queue ACB tear
  or the entry-hang BVH traversal are discharged.
* Any frame-rate gain, any speedup, and 60 FPS. **Не обещать 60 FPS: шанс ~15 % (8…25 %).**
