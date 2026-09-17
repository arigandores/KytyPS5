# Session 86 — FACTS

**The single source of truth for session 86.** Everything is marked **[M]** measured (a counter in
a run of this session, or a prior session's run named), **[I]** inferred (read from source and
reasoned), **[NM]** not measured, **[R]** retracted.

## 0. In one sentence

**Route D was opened and two of its four blocks were divided: `mh_prog` is NOT a lookup — the key
build and the map lookup are 28.74 ns a call and 4.3 % of it, while 93.65 % of `ProgramCache::Get`
is resource materialisation; and `PrepareBindings`' 3 991 µs turns out to be 76 % the image loop at
65.25 ns a slot, which is the second term session 85 recorded as missing and which makes route C's
image ceiling 3 454 µs rather than the 800 µs that was published.** Beside them: route D4 is
**MARGINAL at M = 0.1822** but **the bucket that makes it marginal is not the one a draw merge could
exploit** — a true instanced-merge candidate is **0.668 %** of draws; route C's last idea reads
**292.5 µs against its own 300 µs floor** and is closed by the rule sealed before the run, by a
2.5 % margin; and the shipped `progmemo` is worth **−699.0 ± 86.3 µs** with its key half priced
exactly at **73.79 ns a miss against 14.53 ns a hit**.

## 1. The runs

Binary **`813b8c9dd68a6f0a817f69483ce386ffa7fe5127499a836f95711538219fceb5`**, 23 607 296 bytes.
A **first** binary, `a6e33c0edc3bd5cb…` (23 607 808 B), was built and then superseded — §2.1 says
why and what of it is quoted (nothing). Sky Garden (`-lvl underwater_aerial_garden`), settled
window **n ≥ 2100**, `KYTY_FRAME_TRACE=lite`, `KYTY_GATE_SCHEDULE_ABBA=1`, period `30+1800`.

| tag | binary | what | pre-registration | verdict |
|---|---|---|---|---|
| `spv86a` | first | one arm, all six gates on | `pred/01` §6 | **SCOUTING — no number quoted**, §2.1 |
| `spv86b` | second | one arm, all six gates on, 120 s | `pred/01` §6 | **`sl_bad` = 0, `dm_bad` = 0, `dm_over` = 0** |
| `drm86a` | second | ABBA `drawmerge=0\|1`, five gates in **both** arms, 300 s | `pred/01`, `pred/02` | **VALID** — §3, §4, §5, §6 |
| `pgm86a` | second | ABBA `progmemo=1\|0`, three gates in both arms, 300 s | `pred/03` | **VALID** — §7 |

**Five emulator launches** (`spv86a` and `spv86b` each carry an uncounted warm-up), **every one
entered on the first attempt in 13.4–14.8 s**; no entry hang, against the historical 6.67 %.

## 2. CORRECTIONS TO THE RECORD, and one to this session's own instrument

### 2.1 The instrument was wrong, its own scouting run caught it, and it was fixed before the deciding run [M]

`spv86a` read **`dm_over` = 454 a frame** against `pred/01` §4's *"must read 0"*. The cause: the
push payload was stored as raw dwords in a fixed `4 × 32` array, and
`BindingLayout::ShaderDataDwords()` is `memory_offset_dword + (memory_offset_count + 3) / 4` — **not
bounded by any translator cap**, unlike images (`MaxImages` 64), samplers (32) and buffers (32),
whose bounds `sl_over` = 0 has proved every frame since session 84. Because an over-cap draw is
**excluded** from the classification by design — so that truncation can never become a false match —
the cap was silently deleting **8.7 %** of the population and invalidating the next draw's
comparison as well.

Fixed to **one FNV-1a hash a stage**, which has no cap. Cost: `d_sd` becomes *"the payload
differs"* instead of a dword count, which is all the classification ever asked of it, and a 64-bit
hash collision could read as *"push constants equal"* — negligible over ~5 000 draws a frame, and
said rather than hidden. A second, non-deciding change went in with it: the per-slot **difference**
counters now accumulate whenever the lengths match rather than only when the pipeline also does, so
that `dm_img_d` is usable as the consistency reading `pred/01` §7 asks for. **The classification and
the routing rule of `pred/01` §5 are untouched, and `spv86a`'s numbers are quoted nowhere.**

**`dm_over` then read 0 in `spv86b` and 0 in both arms of `drm86a`, over 7 192 settled frames.**
Prediction M2 is therefore scored a HIT **and discounted** — it was a live test that FAILED once and
is near-unlosable only after the fix.

### 2.2 `ROADMAP` §2 D2's premise — *"1.13 µs a draw just to FIND a program"* — is wrong [M]

`mh_prog_us` really is ~6.0 ms a frame over ~5 020 draws. But **finding the program costs 28.74 ns
a lookup, 255 µs a frame, 4.3 % of the phase** (§5). What the phase actually is: 70 % lock hold, and
inside that hold **93.65 % of `ProgramCache::Get` is resource materialisation, not lookup.** The
name has been wrong in this record since session 69.

### 2.3 Route C's image-slot ceiling was published on an incomplete price [M] [R]

`FACTS` s85 §9 said plainly: *"`PrepareBindings`' 3 991 µs a frame is not split by resource kind, so
the image-slot ceiling of §3.4 has an unmeasured second term."* **That term is now measured at
65.25 ns a slot**, against the 19.66 ns the ceiling was computed from. §6.3 carries the arithmetic
and what does and does not follow from it.

### 2.4 Three of D2's four splits were already shipped, and one more mechanism was already on disk [M]

Before a line was written: the lock is `plkstat` (session 83, lite-readable), the memo compare is
`pmemo_chk_us` (lite-readable, and it already read 396.8 µs a frame in `blp85a`), and the key build,
map lookup and materialisation are `ProgKeyNs` / `ProgPrepareNs` / `ProgMaterializeNs` /
`ProgPermNs` — which are `FrameStats::Lap` and therefore read exactly 0 in every
`KYTY_FRAME_TRACE=lite` run this programme performs. **D2's work was re-emission on the
lite-readable idiom, not invention**, and `pred/02` §2 said so before the run. And D4's necessary
condition was **already on disk** — §3.1.

## 3. ROUTE D4 — THE CENSUS THAT HAD NO CEILING

### 3.1 The free number: it was in session 85's log all along [M]

`PipelineCache::GetGraphicsPipeline` (one caller) counts `pmemo_pipe` when a draw's whole
`GraphicsPipelineKey` equals the previous draw's. Gate `progmemo`, **default 1 since session 60**;
printed on `FrameTrace-x`; `gates_base.txt` pins `fslean=0`. Over the settled window of
`C:/kyty/s85/log_blp85a.txt`: **3 893.3 a frame against `draws` 5 041.3 = 77.2 %, both arms agreeing
to 0.01 %.** `draws` over-counts the denominator, so that is a **lower** bound.

**Three quarters of consecutive draws in Sky Garden already share a pipeline, and the record has
carried that number, unread, since session 85.** It cost no run.

### 3.2 `drm86a` — VALID on every pre-registered criterion

| criterion (session 81 §1, carried unchanged) | reading | |
|---|---|---|
| 1. `guards.py --first-frame 2100` check 2 | 0 MISMATCH lines; `dm_bad`, `sl_bad` reachable in `spv86b` and zero | PASS |
| 1. …check 10 | binary confirmed, 250 `GateArm` blocks | PASS |
| 2. arming by a counter inside the run | §3.3 | PASS |
| 3. area split < 1.0 % | **−0.001 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (120/120)** | PASS |
| 3. work within 0.5 % | **+0.025 %** | PASS |
| 4. `summary4` whole-arm vs paired gap < 0.05 pp | +1.943 % vs +1.948 %, **+0.005 pp** | PASS |
| 5. bracketing timer `da_take_us` | **268.6 → 269.3 ns a take, +0.26 %** | reported |
| 6. everything on matched pairs | 120 of 120; the endpoint runs on 120 block pairs | PASS |

Check 6 (cores) PASSes here and FAILs in `pgm86a`, as it does routinely; it is not an admission
criterion. Check 3b raised one advisory pass-area difference; the render size itself held.

### 3.3 Arming, proved inside the run [M]

**Every one of the fourteen new counters reads exactly 0 — median AND maximum — over the 1 400
settled frames BEFORE the first `GateArm` line**, where the gate file applies and the new names keep
their compiled fallback of 0 because `gates_base.txt` does not mention them. That is a stronger
proof than a median claim and it covers `bl_res_*`, `bl_smp_*`, `bl_sd_us`, every `pg_*`, every
`sl_img_dup*` and `dm_n`, none of which has an off arm in this run.

| quantity | arm `drawmerge=0` | arm `drawmerge=1` |
|---|---:|---:|
| every `dm_*` | **0.000 median**, 60 of 3 600 frames non-zero | non-zero |
| `dm_over` | 0 | **0** |
| `dm_n` against `draws` | — | 4 936.9 vs 5 041.7 = **0.9792** |
| `dm_pipe` against `pmemo_pipe` | `pmemo_pipe` live in both arms | **−1.644 %**, limit 2 % |
| `dm_ring / dm_bufn` against `sl_buf_ring / sl_buf_n` | 0.3411 vs 0.3473 | **0.3506 vs 0.3479**, 0.27 pp |

**The arm-0 tail is 1.71 % of the armed value and `pred/01` §7 named 1 % — so it is above the figure
that text wrote down, and it is reported rather than smoothed.** What the text also asked for is
whether it is concentrated at block boundaries: **all 60 non-zero frames are at distance 0 from a
block start, without exception.** It is the schedule straddle and nothing else.

### 3.4 THE CENSUS [M] — `drm86a` arm 1, sums over 3 592 settled frames

| per frame | value | share of `dm_n` |
|---|---:|---:|
| `dm_n` — draws classified | **4 936.9** | 1.0000 |
| `dm_pipe` — same `VkPipeline` as the previous draw | **3 827.4** | **0.7753** |
| `dm_same` — everything identical | 1.0 | 0.0002 |
| `dm_push` — only push constants differ | 0.0 | 0.0000 |
| `dm_buf1` — exactly one buffer slot differs | 419.5 | 0.0850 |
| `dm_no` | 4 516.4 | 0.9148 |
| **with stream-ring slots excluded** | | |
| `dm_same_nr` | 1.0 | 0.0002 |
| `dm_push_nr` | 32.0 | 0.0065 |
| `dm_buf1_nr` | **866.4** | **0.1755** |
| `dm_mesh` | 172.3 | 0.0349 |
| `dm_ring / dm_bufn` | 16 133 / 46 014 | **0.3506** |

    M = (dm_same_nr + dm_push_nr + dm_buf1_nr) / dm_n  =  0.1822   =>  MARGINAL

by the rule fixed in `pred/01` §5 (LICENSED ≥ 0.30, MARGINAL 0.10–0.30, CLOSED < 0.10).

### 3.5 AND THE BUCKET THAT MAKES IT MARGINAL IS NOT THE ONE A DRAW MERGE COULD EXPLOIT [M]

**This is the finding, and it matters more than the verdict.**

| what it would take | share of draws |
|---|---:|
| `dm_same_nr + dm_push_nr` — a **true instanced-merge / multi-draw** candidate | **0.668 %** |
| `dm_buf1_nr` — one buffer binding differs: needs **descriptor indexing or bindless**, not a merge | **17.550 %** |

`vkCmdDrawMultiIndexedEXT` and instancing require the descriptor set to be **identical**; they
cannot vary a buffer binding between the merged draws. So **merging draws in the ordinary sense is
dead at 0.668 %** — 33 draws a frame out of 4 937 — and everything that makes D4 marginal sits in a
bucket that would need the game's per-object buffers moved behind an index. That is a different,
much larger change than "merge two draws", and it is the honest statement of what M = 0.18 buys.

**The crudest possible upper bound, and it will not be written as a saving:** the per-draw fixed
cost is `cpu_gpu_us / draws` = 32 019 / 5 040 = **6.35 µs**, so `M × dm_n × 6.35 µs` = **5 706 µs a
frame** — a figure that assumes a merged draw costs nothing and that the bindless rewrite is free.
In this programme upper bounds have been wrong by 2.6×, 20× and 2.3×. **What M licenses is a
session, not a number**, and §3.5's split says which session.

### 3.6 The consistency reading that missed, and why [M]

`dm_img_d` = 3 385.8 a frame against `sl_img_n − sl_img_view` = 6 008.3 — **−43.6 %**, against a
±15 % band. **Prediction M12 MISS.** The cause is structural and was half-stated in `pred/01` §7:
`slotstat` keys its shadow row by `(ShaderType % 16, positional index)` and compares **every**
commit, while `dm_*` is a flat per-draw signature that accumulates differences only when the draw's
vector **lengths** match the previous draw's. A draw whose stage set or slot counts change
contributes to slotstat's difference and not to `dm_img_d`. The band was written against an
identity the two instruments never had.

## 4. D3 — `PrepareBindings` DIVIDED, AND ROUTE C'S MISSING TERM [M]

Both arms of `drm86a` carried `bindlap=1` and agree to 0.1 % on every figure below; arm 1 is quoted.

| | µs a frame | population | **ns a unit** | share of `bl_prep_us` |
|---|---:|---:|---:|---:|
| `bl_prep_us` — `PrepareBindings`, whole | **4 101.5** | 9 122.7 stages | 449.60 | 1.0000 |
| **`bl_res_us` — the image loop** | **3 124.6** | 47 885 image slots | **65.25** | **0.7618** |
| `bl_smp_us` — the sampler loop | 345.1 | 11 125 sampler slots | 31.02 | 0.0841 |
| `bl_sd_us` — the `shader_data` copy | 385.0 | — | — | 0.0939 |
| remainder, **derived** | 246.8 | — | — | 0.0602 |

Ratios of medians agree with ratios of sums to **0.4 %** (65.11 vs 65.25; 30.49 vs 31.02), so the
estimator choice moves nothing — it is still named, because *an estimator nobody chose is still a
choice.* `bl_res_n` matches `bl_img_n` to **+0.0001 %**, and **no frame of either arm has the parts
exceeding the whole.**

**The instrument reproduces session 85 on the counters it did not touch:** `bl_img_us / bl_img_n` =
**22.30 ns** against 22.82 (2.3 % apart) and `bl_buf_us / bl_buf_n` = **76.01 ns** against 77.07
(1.4 % apart), on a different binary carrying three more marks a stage. `bl_prep_us` is 4 101.5 µs
against 3 991 µs — larger, because the instrument grew, exactly as `pred/02` §3 said it would; the
two are **not** comparable and the split is a ratio claim.

**`bl_res_us` contains `BindImage` as well as `ResolveTextureWith`** — they share the loop body and
separating them needs the per-slot pair this session refused. That is the next measurement of route
C and §6.3 says why it is now the important one.

## 5. D2 — WHAT `mh_prog` ACTUALLY IS [M]

`drm86a` arm 1 (`mutsite=1 plkstat=1 proglap=1` in both arms), confirmed by `pgm86a` arm 0 to 0.2 %.

| | µs a frame | share of `mh_prog_us` |
|---|---:|---:|
| **`mh_prog_us`** | **5 991.8** | 1.0000 |
| `pg_pre_us` — everything before the lock | 1 541.3 | 0.2572 |
|   … of which `pmemo_chk_us` — the memo compare | 404.5 | 0.0675 |
| `pl_prog_wait_us` — waiting for `PipelineCache::m_mutex` | 42.6 | 0.0071 |
| **`pl_prog_hold_us` — holding it** | **4 177.7** | **0.6972** |
|   … of which `pg_get_us` — `ProgramCache::Get`, both draw stages | **4 019.5** | 0.6708 |
|     … of which **`pg_key_us` — the key build and `programs.find`** | **255.1** | **0.0426** |
|     … of which **materialisation** | **3 764.4** | **0.6283** |
| the `RefreshShaders` prologue and the phase's remainder | 230.2 | 0.0384 |

* **`pg_key_us / pg_key_n` = 28.74 ns a lookup.** Prediction G3 (< 200 ns) HIT, and it is the answer
  to D2: *finding* the program is 4.3 % of the phase.
* **Materialisation is 93.65 % of `ProgramCache::Get`.** Prediction G6 (> 0.50) HIT, by a wide
  margin. What runs there is `AheadTake`, the SRT memo, `MaterializeResources` and the permutation
  scan — **resource materialisation, not a lookup.**
* `pg_perm / pg_get_n` = **1.059**: the permutation `find_if` examines essentially one candidate, so
  the `std::deque` scan is not a cost. G7 HIT.
* `pg_cold_n` = `pg_compile_n` = **0.00 a frame in every arm of both runs** — the translation-cache
  load and `Compile` contamination `pred/02` §4 insisted on counting is **measured at zero**, so
  none of the figures above is contaminated. G2 HIT.
* **`pg_n` equals `pl_prog_n` exactly** (+0.0000 %), the identity `pred/02` §7 fixed. G1 HIT.
* `pl_prog_hold_us / mh_prog_us` = **69.72 %** reproduces session 83's 68.9 % on a different binary.

**So the lever session 83 named and the lever the brief named are both wrong.** It is not
parallelism (closed, s83) and it is not a cheaper key or a faster map (28.74 ns, 255 µs). It is
**resource materialisation under the pipeline-cache lock, 3 764 µs a frame = 11.9 % of the frame**,
and nothing in this record has ever looked at it.

## 6. ROUTE C — its last idea, and its ceiling corrected

### 6.1 Duplicates within a stage [M] — `drm86a`, both arms agree to 0.1 %

| per frame | value |
|---|---:|
| `sl_img_n` | 47 885.4 |
| `sl_stage_n` | 9 122.6 |
| **`sl_img_dup`** — a slot whose `image_id` repeats an earlier slot of the same stage | **14 902.5** = **31.12 %** |
| **`sl_img_dupv`** — … and whose `VkImageView` repeats too | **14 875.5** = **31.06 %** |
| `sl_img_dstage` — stages holding at least one duplicate | 2 210.5 = **24.22 %** of stages |
| `sl_img_sq` — `Σ n(n−1)/2` | 481 560 = **52.79** a stage |

**Duplication is real and it is concentrated:** 31 % of image slots are duplicates but only 24 % of
stages hold one, and `sl_img_dup` is 99.8 % `sl_img_dupv` — a duplicate by id is almost always a
duplicate by view, so the whole descriptor element repeats, not merely the image.

`sl_img_sq / sl_stage_n` = **52.79** against a predicted band of 5–40: **prediction S3 MISS**, and
the miss is informative. A uniform 5.25 images a stage would give 11.2; 52.79 means the per-stage
image count is heavily skewed, a second moment nothing in this tree had measured. It is also the
exact worst case of the duplicate scan — 481 560 comparisons a frame, ~190 µs at ~0.4 ns — so **the
instrument reports its own bound**, which is what it was built to do.

### 6.2 THE VERDICT, by the rule fixed in `pred/02` §6 before the run

    ceiling_hi = sl_img_dupv x 19.66 ns = 14 875.5 x 19.66 ns = 292.5 us a frame
    BUILD at >= 1 000      MARGINAL at 300..1 000      ROUTE C CLOSED OUTRIGHT below 300

→ **292.5 µs. ROUTE C'S LAST IDEA IS CLOSED OUTRIGHT** — and by a margin of **2.5 %**.

`pred/02` §5 sealed the threshold in the other units too: *"clearing 300 µs needs roughly
`sl_img_dupv` ≥ 15 300."* Measured: **14 875.5**, short by **2.8 %**. **This is as close to its own
pre-registered floor as any verdict in this record**, and the margin is said out loud rather than
rounded away. Two things push it further down and none pushes it up: the per-image fraction `f` of
the 19.66 ns is **[NM]** and is certainly below 1 (the per-slot half — `memo_index`,
`memo_version`, `slot->image_id`, `fast_view`, the `fast_stamp` compare, `desc.info.metadata.kind`,
the `mip_mode` gate, `TextureSourceSettled`'s desc-dependent tail and the two stores — cannot be
amortised), and 9.3 % of image slots never take the fast path at all. Prediction **S4 HIT**, written
to lose in the direction this session would have preferred.

### 6.3 [R] AND ROUTE C'S IMAGE CEILING IS 3 454 µs, NOT 800 — the term session 85 named as missing [M]

`FACTS` s85 §9 recorded the debt precisely: *"`PrepareBindings`' 3 991 µs a frame is not split by
resource kind, so the image-slot ceiling of §3.4 has an unmeasured second term."* §4 measures it.

| | ns a repeating image slot |
|---|---:|
| `RebindImages`, memo fast path (session 85, `tfs85a`) | 19.66 |
| **`PrepareBindings`, the image loop (this session, `drm86a`)** | **65.25** |
| **total** | **84.91** |

40 674.7 repeating image slots a frame (`sl_img_same_sh`, reproducing session 85's 40 664 to
0.03 %):

| | µs a frame |
|---|---:|
| what `FACTS` s85 §12.6 published | **800** |
| what the complete price gives | **3 454** |

**Applying `pred/03` of session 85's own rule to the corrected number reads LICENSED, not "nothing
behind it".** That is stated plainly because the arithmetic is the arithmetic.

**And the verdict does not change, because the verdict was never the arithmetic.** Session 85 closed
route C on three soundness blockers, and the newly measured term is **where the worst of them
lives**: `BindImage` — which arms `is_bound` / `force_general` / `shader_write` on the image, which
`ResetBindings` clears **every draw**, and which `AcquireRenderTargets` reads to choose `eGeneral`
over `eColorAttachmentOptimal` — is **inside the image loop of `PrepareBindings`, i.e. inside the
65.25 ns**. Session 85 wrote that *"a slot skipped in `PrepareBindings` would silently change an
unrelated render target's layout."* It was right, and it now turns out to have been talking about
the larger half.

**What this changes is the next measurement, not the verdict.** `bl_res_us` must be split into
`ResolveTextureWith` and `BindImage`, which needs the image loop broken into two passes over
`prepared.images` — legal, because the tree's own comment says *"`BindImage` does not look at
`prepared.images`, so running it after the insertion changes nothing"* — and that is one patch and
one run. **Until it is taken, "route C is a ceiling with nothing behind it" stands on a price that
is 4.3× smaller than the real one, and this file says so rather than leaving it to be found.**

## 7. `progmemo` — a shipped gate used as the source of variation

### 7.1 `pgm86a` — VALID on every pre-registered criterion

Area split **+0.001 %**, pair match **100 % (125/125)**, work **−0.135 %**, `summary4` cross-check
gap **−0.001 pp**, `da_take_us` per take 273.7 → 269.6 ns (**−1.50 %**, reported). Guards checks 2
and 10 PASS; check 6 (cores) FAILs, 5 of 50 groups, as it does routinely and is not an admission
criterion.

### 7.2 Arming, and a prediction of mine that was badly posed [M]

`pmemo_hit`, `pmemo_pipe` and `pg_key_hit_n` all read **0.000 median** in the `progmemo=0` arm — and
**415 247 on sums**, 110.7 a frame, **1.68 % of the armed value**. All 62 non-zero frames are at
distance 0 from a block start: the same schedule straddle §3.3 measures at 1.71 %.

**Prediction H1 said "exactly 0" and is scored a MISS**, because `pred/03` §4 omitted the median
qualifier that `pred/01` §7 carries for exactly this reason. **It is my own badly-posed prediction
and it is recorded, not repaired.** Every figure of §7.3 is computed with the block-start frame of
**every** block dropped from **both** arms, after which the off-arm residual is **exactly 0**.

### 7.3 THE UNIT PRICE OF A PROGRAM KEY [M] — two equations on sums, `pred/03` §2

    arm ON  :  pg_key_us = K_hit x pg_key_hit_n + K_miss x (pg_key_n - pg_key_hit_n)
    arm OFF :  pg_key_us = K_miss x pg_key_n

| | ns a call |
|---|---:|
| **`K_miss`** — build the static key + `unordered_map::find`, over the **whole** population | **73.79** |
| **`K_hit`** — the memo iterator instead | **14.53** |
| **what the shipped memo saves per hit** | **59.26** |

**The model reproduces the raw arm difference to +0.30 %** (394 647 against 393 471 ns a frame).
Predictions H3, H4 and H5 all HIT.

**And the two populations are not the same price, which is a finding in itself.** Read *within* the
ON arm, the memo's own misses cost **91.57 ns** against `K_miss` = 73.79 ns over the whole
population — **the self-selected miss population is 24 % dearer than an average call**, because the
memo misses on the stages with more static state and larger keys. Both numbers are real, they answer
different questions, and quoting either as "the" price would be wrong.

### 7.4 What the shipped default is worth [M]

| statistic | value |
|---|---:|
| `cpu_net_us`, `progmemo=1` against `progmemo=0` | **−699.0 ± 86.3 µs (2·SE), t = −16.21** on 125 pairs |
| `cpu/draw` (`area_verdict.py`, 125 matched pairs) | **−2.406 % ± 0.127 %, t = −37.77** |
| `mh_prog_us` | 5 994.8 → 6 588.6 = **−593.8 µs** |
| … of which the key half, from §7.3 | **−394.6 µs** |
| `pl_prog_hold_us` | 4 220.7 → 4 620.7 = **−400.0 µs** |
| `pmemo_chk_us` — what the memo's own check costs | **+371 µs** (377.2 → 6.4) |
| `gpu_busy_us` | −0.004 % ± 0.162 %, noise |

**The accounting closes:** the memo pays 371 µs to ask the question, saves 394.6 µs on the key half
plus the pipeline-key memo, and nets −699 µs of frame time. H6 HIT. **This is a confirmation of a
default shipped in session 60, not a new saving**, and it is the second-largest within-run effect in
this record after `recpin`'s −1 687 µs.

## 8. WHAT WAS NOT DONE

* **No video pass.** Nothing shipped: all three gates this session adds are 0 and the two it extends
  are 0, so with them off the rendering path is behaviourally identical to the one session 84
  shipped. It is not a byte-identical binary and no pixel comparison was made; what is claimed is
  that no shipped default changed, so the `ROADMAP` §6 video debt is not incurred.
* **No `acc86a`.** No default changed.
* **`bl_res_us` is not split into `ResolveTextureWith` and `BindImage`** — §6.3, and it is now the
  most valuable single measurement left in route C.
* **The 3 764 µs of materialisation inside `ProgramCache::Get` is not divided** — §5.
* **The combined price of the D3 + D2 + §3.2 instruments is [NM]**, because `PLAN.md` §2 chose to
  ride them in both arms. That was a deliberate design decision and it made prediction **I1
  unevaluable by my own hand** — §9.
* **`dapin`'s GPU cost was not touched.** The `recordthread=0\|1` ABBA session 85 named is still the
  next step and this session did not take it.
* **D1 was not started.** Its ceiling (~2.1 ms) was already known and it is a rewrite, not a
  measurement.

## 9. THE SCOREBOARD — all forty-three predictions, scored

`pred/01_drawmerge.md` §8 — fourteen:

| | prediction | result |
|---|---|---|
| M1 | every `dm_*` 0.000 median in arm 0 | **HIT**; tail 1.71 % of the armed value, **above the 1 % the text named**, 100 % at block starts |
| M2 | `dm_over` = 0 | **HIT, and DISCOUNTED** — it FAILED in `spv86a` and is near-unlosable only after §2.1's fix |
| M3 | `dm_bad` = 0 | **HIT, and DISCOUNTED** — a cross-implementation check, not a value check |
| M4 | `dm_n / draws` in [0.90, 1.00] | **HIT** (0.9792) |
| **M5** | **`dm_pipe` within 2 % of `pmemo_pipe`** | **HIT** (−1.644 %) — discriminating; two independent implementations |
| **M6** | **`dm_same_nr / dm_n` < 0.05** | **HIT** (0.0002) — discriminating |
| **M7** | **M ≥ 0.15** | **HIT** (0.1822) — discriminating, and it decided the route |
| M8 | `dm_same ≤ dm_same_nr`; `dm_buf1 ≤ dm_buf1_nr + dm_same_nr + dm_push_nr` | **HIT** (0.0002 ≤ 0.0002; 0.0850 ≤ 0.1822) |
| M9 | `dm_ring / dm_bufn` within 10 pp of 34.94 % | **HIT** (35.06 %, 0.12 pp) |
| M10 | `dm_mesh / dm_n` < 0.05 | **HIT** (0.0349) |
| M11 | the instrument costs +150…+900 µs | **HIT** (+626.2 ± 80.5) |
| M12 | `dm_img_d` within 15 % of `sl_img_n − sl_img_view` | **MISS** (−43.6 %) — §3.6, the band was written against an identity the two instruments never had |
| M13 | `gpu_busy_us` inside its own 2·SE | **HIT** (+0.086 % ± 0.179 %) |
| M14 | `da_take_us` per take moves < 1 % | **HIT** (+0.26 %) |

`pred/02_splits.md` §8 — twenty:

| | prediction | result |
|---|---|---|
| P1 | every new `bl_*` and `pg_*` 0.000 median in its off arm | **HIT, and stronger than asked**: median **and maximum** 0 over 1 400 pre-schedule frames |
| P2 | `bl_res_n` within 0.1 % of `bl_img_n` | **HIT** (+0.0001 %) |
| P3 | parts ≤ whole in every frame | **HIT** (0 frames of 7 192) |
| **P4** | **`bl_res_us / bl_prep_us` > 0.60** | **HIT** (0.7618) — discriminating |
| P5 | `P_res` in 20…200 ns | **HIT** (65.25) |
| **P6** | **`P_res + P_img` in 40…120 ns** | **HIT** (87.55) — discriminating |
| P7 | `bl_smp_us / bl_smp_n` < `P_res` | **HIT** (31.02 < 65.25) |
| G1 | `pg_n` == `pl_prog_n` exactly | **HIT** (+0.0000 %) |
| G2 | `pg_cold_n`, `pg_compile_n` each < 1.0 a frame | **HIT** (0.00 and 0.00, both runs, both arms) |
| **G3** | **`pg_key_us / pg_key_n` < 200 ns** | **HIT** (28.74) — discriminating, and it renamed the phase |
| G4 | `pmemo_chk_us` < `pg_pre_us` < `pl_prog_hold_us` | **HIT** (404.5 < 1 541.3 < 4 177.7) |
| G5 | `Σ pg_get_us ≤ pl_prog_hold_us` every frame | **HIT** (0 frames over) |
| **G6** | **materialisation > 50 % of `pg_get_us`** | **HIT** (93.65 %) — discriminating |
| G7 | `pg_perm / pg_get_n` < 3 | **HIT** (1.059) |
| **S1** | **`sl_img_dup / sl_img_n` ≥ 0.10** | **HIT** (0.3112) — discriminating |
| S2 | `sl_img_dupv ≤ sl_img_dup`, `sl_bad` = 0 | **HIT** |
| S3 | `sl_img_sq / sl_stage_n` in 5…40 | **MISS** (52.79) — §6.1, and the miss is the finding |
| **S4** | **`sl_img_dupv × 19.66 ns` < 300 µs** | **HIT** (292.5) — discriminating, by a **2.5 %** margin |
| S5 | `sl_img_dstage / sl_stage_n` < `sl_img_dup / sl_img_n` | **HIT** (0.2422 < 0.3112) |
| I1 | the D3+D2+§3.2 instrument costs +200…+1 200 µs | **NOT EVALUATED — by my own design.** `PLAN.md` §2 rode them in both arms, which makes their combined price unmeasurable in this contrast. The prediction should not have been written against a design that could not test it |

`pred/03_progmemo.md` §5 — nine:

| | prediction | result |
|---|---|---|
| H1 | `pmemo_hit`, `pmemo_pipe`, `pg_key_hit_n` each **exactly 0** in the OFF arm | **MISS** on sums (1.68 %, all at block starts), HIT on medians — **badly posed by me**, §7.2 |
| H2 | `pg_key_n` within 2 % between arms on sums | **HIT** (−0.918 %) |
| **H3** | **`K_miss > K_hit`** | **HIT** (73.79 > 14.53) — discriminating |
| **H4** | **`K_miss − K_hit` in 10…300 ns** | **HIT** (59.26) — discriminating |
| H5 | the model reproduces the raw arm difference within 5 % | **HIT** (+0.30 %) |
| **H6** | **`progmemo=1` worth `cpu_net_us` in [−2 500, 0] µs** | **HIT** (−699.0 ± 86.3) — discriminating, and it could have embarrassed a shipped default |
| H7 | `draws` within 1.5 % on sums | **HIT** (−0.135 %) |
| H8 | `gpu_busy_us` inside its own 2·SE | **HIT** (−0.004 % ± 0.162 %) |
| H9 | `pg_cold_n` < 1.0 a frame in both arms | **HIT** (0.00) |

**Across all three pre-registrations: 43 predictions, 39 hits, 3 misses (M12, S3, H1), 1 not
evaluated (I1).** Two hits (M2, M3) are discounted as near-unlosable and said so. **Two of the four
non-hits are defects in predictions I wrote myself** — H1 omitted the median qualifier my own
`pred/01` carried, and I1 was written against a design that could not test it.

## 10. THE ARITHMETIC

| | value |
|---|---:|
| shipped baseline (`acc82a`, not re-measured since session 82) | 31 642 µs = 31.60 FPS |
| 60 FPS | 16 667 µs |
| the measured sequential floor `S_hi` (session 83) | 20 838 µs |
| **D4: consecutive draws sharing a pipeline** | **77.53 %** |
| **D4: a true instanced-merge candidate** | **0.668 % of draws — merging is dead** |
| **D4: one buffer binding apart (needs bindless, not a merge)** | **17.55 %**, M = 0.1822, **MARGINAL** |
| **D3: `PrepareBindings`, the image loop** | **3 124.6 µs a frame, 65.25 ns a slot, 76.2 % of the block** |
| **D2: `mh_prog`, the lookup half** | **255 µs a frame, 28.74 ns a call — 4.3 % of the phase** |
| **D2: `mh_prog`, resource materialisation under the lock** | **3 764 µs a frame = 11.9 % of the frame, [NM] inside** |
| **route C's last idea** | **292.5 µs against a 300 µs floor — CLOSED, margin 2.5 %** |
| **route C's image ceiling, corrected** | **3 454 µs, not the 800 published — and `BindImage` is inside it** |
| the program-key unit price | **73.79 ns a miss / 14.53 ns a hit** |
| `progmemo=1`, shipped since session 60 | **−699.0 ± 86.3 µs**, confirmed |

**The honest statement of the task.** Route D had no measured ceiling anywhere in it when this
session started. Two of its four blocks are now divided, and both divisions point the same way:
**the money is not in the bookkeeping this programme has been measuring for four sessions, it is in
work — 3 764 µs of resource materialisation under the pipeline-cache lock, and 3 125 µs of texture
resolution in the bind phase.** Route D4 is marginal and the part that is marginal needs a bindless
rewrite rather than a draw merge. And route C's own ceiling turns out to have been published on a
price 4.3× too small — which does not re-open it, because the blocker session 85 identified lives in
the very term that was missing, but which does mean the next route-C number is a two-way split of
`bl_res_us` and not another population.
