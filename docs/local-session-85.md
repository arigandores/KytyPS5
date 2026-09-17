# Session 85 — route C's unit price, measured; `bda_scan_us` attributed; route B's next package, not paid for

*This is `C:/kyty/s85/FACTS.md` verbatim, carried into git as the session's report.*
*The harness, the logs and the two pre-registrations live in `C:/kyty/s85`.*

---

# Session 85 — FACTS

**The single source of truth for session 85.** Everything is marked **[M]** measured (a counter in
a run of this session, or a prior session's run named), **[I]** inferred (read from source and
reasoned), **[NM]** not measured, **[R]** retracted.

## 0. In one sentence

**Route C's unit price exists: a descriptor slot costs 22.82 ns on the image side and 77.07 ns on
the buffer side of the bind phase, against the 2.48 ns session 84 measured for touching one — so
the 21-to-30-fold contradiction is resolved, and route C's exploitable ceiling is ~2.1 ms a frame,
not the 5–7 ms the premise implied.** Beside it: the census keeps its numbers and loses two of its
three biases (the third is measured at zero); the ~1.88 ms fixed part of `bda_scan_us` is
**92.7 % staging `memcpy` at 11 GB/s**, closing the session-84 debt; route B's next package —
**one item, because the other three did not survive reading** — measured **−35.9 ± 81.2 µs** against
a −150 µs bar sealed before the run and is **NOT PAID FOR**; and `dapin`'s six-session GPU debt
gained its fifth replication (+1.961 % ± 0.165 %), lost one candidate to a controlled test, and
**retired the measurement the record had been prescribing for it.**

## 1. The runs

Binary **`24476c7b7a66a65251fc2e8b28e608d0769a52a09cf183a6e9c1ef9ab8b8f519`**, 23 595 520 bytes,
built once and never rebuilt afterwards. Sky Garden (`-lvl underwater_aerial_garden`), settled
window **n ≥ 2100**, `KYTY_FRAME_TRACE=lite`, `KYTY_GATE_SCHEDULE_ABBA=1`, period `30+1800`.

| tag | what | pre-registration | verdict |
|---|---|---|---|
| `spv85a` | `slotstat=1 slotstatcheck=1 bindpack2=1 bindpack2check=1`, warm-up + 120 s | `pred/01` §4.1, `pred/02` §7.1 | **`sl_bad` = 0, `bp2_bad` = 0** — §4.4, §6.3 |
| `blp85a` | ABBA `bindlap=0\|1`, `bdasplit=1 slotstat=1` in **both** arms, 300 s | `pred/02` | **VALID** — the unit price, §3 |
| `bn2d85a` | ABBA `bindpack2=0\|1`, 300 s | `pred/01` | **VALID, NULL** — §6 |
| `dgt85a` | ABBA `dapin=1\|3` + `KYTY_GPU_TIME=1`, 240 s | **none** | diagnostic — §7 |
| `dap85a` | ABBA `dapin=1\|3`, 300 s | **none** | **VALID** — §7 |
| `rcp85a` | ABBA `recpin=0\|1`, 300 s | **none** | **VALID** — §7 |

**Seven emulator launches** (`spv85a` carries an uncounted warm-up), **every one entered on the
first attempt in 13.3–15.4 s**; no entry hang, against the historical 6.67 %.

**Three of the six runs are covered by no pre-registration and were named in no plan** — `dgt85a`,
`dap85a` and `rcp85a`, the `dapin` debt of §7. That is said here rather than left to be noticed,
as session 84 had to say of `acc84a`. They are diagnostics: no threshold rides on them and no
default was changed by them.

## 2. CORRECTIONS TO THE RECORD, all found by reading BEFORE any number existed

1. **The commit-side split the brief asked to build already exists.** `next-session-85.md` §3.1
   asks for a `plkstat`-idiom split of `CommitBindings` into "build the writes" and "issue them".
   It is in the tree as `cb_pool_tr_us` / `cb_pool_wr_us` / `cb_pool_em_us`, and it is **not**
   `TimingsEnabled`-gated: `Common::DrawStat::On()` is `Gates::Enabled(DrawStat) &&
   FrameStats::Enabled()` (`renderDraw.cpp` `DrawStatBegin`), so those three read under `lite`
   whenever `drawstat=1`. They have read 0 in every session only because that gate is off.
   `bindlap` therefore takes **no second set of timestamps there**; it reuses the same `cb_lap`
   closures. This is session 83's lesson again — *a mechanism the brief proposes to build may
   already be shipped.*
2. **`Scope` is not uniformly dead under `lite`, and the record has been treating it as if it
   were.** Only the **time** half takes its timestamp under `TimingsEnabled()`; the destructor's
   **count** `Add` is outside that guard, so a `Scope`'s count counter reads normally in a lite
   run. `b_texn`, `bb_n` and `ob_n` are exactly that, which is why they could be used as the
   arming denominators of §3.2.
3. **Prediction C1 of session 84 (`sl_over` exactly 0) was STRUCTURALLY UNLOSABLE**, in the same
   class as C6, and session 84 scored it a plain HIT. `SlotStatImages` 64 / `SlotStatSamplers` 32 /
   `SlotStatBuffers` 32 are literally `ShaderInfo::MaxImages` / `MaxSamplers` / `MaxBuffers` — the
   translator's own hard caps — so `sl_over` counts a condition the translator forbids.
4. **`PLAN_82_bind.md` item 3 names three consumers of `TextureBinding::desc`; there are five**,
   and the revalidation it cites does not make a reference safe. §8.1.
5. **`PLAN_82_bind.md` item 6b is unsound as written**, not merely small. §6.2.
6. **A counter absent from `guards.py`'s `SELF_CHECKS` is not merely unjudged — it is never
   PARSED.** `ZERO_COUNTERS` is derived from `SELF_CHECKS` and `COUNTER_RE` is built from
   `ZERO_COUNTERS`, so check 2's own "counters absent from this log" list cannot flag it either,
   because that list iterates the same derived names. Session 84 found two of the three silent
   drops; this is the third. Both of this session's rows were added **before** the first run.

## 3. THE UNIT PRICE — route C's missing number

### 3.1 `blp85a` — VALID on every pre-registered criterion

| criterion (session 81 §1, carried unchanged) | reading | |
|---|---|---|
| 1. `guards.py --first-frame 2100` check 2 | 0 MISMATCH lines; `sl_bad`, `bp2_bad` REACHABLE and zero | PASS |
| 1. …check 10 | binary confirmed, 254 `GateArm` blocks, arm0 ×127 arm1 ×127 | PASS |
| 2. arming by a counter inside the run | §3.2 | PASS |
| 3. area split < 1.0 % | **+0.002 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (122/122)** | PASS |
| 3. work within 0.5 % | **+0.047 %** | PASS |
| 4. `summary4` whole-arm vs paired gap < 0.05 pp | +1.110 % vs +1.113 %, **+0.003 pp** | PASS |
| 5. bracketing timer `da_take_us` | **319.2 → 319.2 ns, +0.00 %** | reported |
| 6. everything on matched pairs | 122 of 122; the deciding estimator runs on **122 block pairs** — the two populations coincide here | PASS |

Check 6 (cores) PASSes here and FAILs in three other runs of this session, as it does routinely; it
is not an admission criterion.

### 3.2 Arming, proved inside the run [M]

| quantity | arm `bindlap=0` | arm `bindlap=1` | |
|---|---:|---:|---|
| every `bl_*` | **0.000 median** | non-zero | PASS |
| `bl_img_n` against `b_texn` | 0 | 48 801 vs 48 781 = **+0.041 %** | limit 2 % |
| `bl_buf_n` against `bb_n` | 0 | 48 416 vs 48 410 = **+0.012 %** | limit 2 % |
| `bl_stage_n` against `sl_stage_n` | 0 | 9 265 vs 9 265 = **+0.000 %** | limit 2 % |
| `bda_bound_n` against `bda_rng` | 300 vs 300 | 300 vs 300 | exact, both arms |
| `bda_up_n` against `bda_scan` | 1 070 vs 1 070 | 1 070 vs 1 070 | exact, both arms |

On sums the three `bindlap` identities read **−0.0063 %**, **−0.0046 %** and **−0.0050 %**.

**`bda_first_n + bda_late_n` against `bda_n − bda_hit` reads +8.696 % ON MEDIANS AND IS EXACT ON
SUMS** — 3 656 + 76 218 = **79 874** against 656 034 − 576 160 = **79 874**. Medians are not
additive; this is the trap that made session 84 mis-score its own P4, met again and reported in the
additive statistic. The sums are quoted; the median form is named and discarded.

### 3.3 THE PRICE [M] — `blp85a` arm 1, ratios of sums, as `pred/02` §4.1 fixed before the run

| | per frame (median) | population | **ns per unit** |
|---|---:|---:|---:|
| `bl_prep_us` — `PrepareBindings`, the full resolution | **3 991 µs** | 9 265 **stages** | **428.64 ns a stage** |
| `bl_img_us` — `RebindImages` | **1 101 µs** | 48 801 image slots | **22.82 ns a slot** |
| `bl_buf_us` — `RebindBuffers` | **3 723 µs** | 48 416 buffer slots | **77.07 ns a slot** |
| `bl_tr_us` — commit, the image transitions | 1 002 µs | 5 090 commits | 195.96 ns a commit |
| `bl_wr_us` — commit, the write-list build | 1 166 µs | 5 090 commits | 228.84 ns a commit |
| `bl_em_us` — commit, the emit | 479 µs | 5 090 commits | 95.19 ns a commit |

Ratios of medians agree with ratios of sums to **1.2 %** (22.56 vs 22.82; 76.90 vs 77.07; 430.76 vs
428.64), so the estimator choice moves nothing here — unlike session 84's `R_buf`, where it moved
1.96 pp. It is still named, because *an estimator nobody chose is still a choice.*

**THE CONTRADICTION OF `ROADMAP` §2 C IS RESOLVED, and both of its numbers were right about
different things:**

| | ns per slot |
|---|---:|
| session 84's census instrument — a compare, a store and a conditional `Add` on values already computed | **2.48** |
| `ROADMAP` §2 C's premise: 5–7 ms of memo-check price over ~95 000 slots | **52.6 – 73.7** |
| **measured here: an image slot in `RebindImages`** | **22.82** |
| **measured here: a buffer slot in `RebindBuffers`** | **77.07** |

The premise's band is **matched almost exactly by the buffer side** and **overstates the image side
by 2.3–3.2×**. The census instrument's 2.48 ns was never the same quantity: it prices reading two
already-final handles, not producing them.

### 3.4 THE CEILING, IN MICROSECONDS — the first time route C has had one

| | repeating slots a frame (same shader, §4) | × unit price | **µs a frame** |
|---|---:|---:|---:|
| image slots | 40 664 | 22.82 ns | **928** |
| buffer slots | 15 275 | 77.07 ns | **1 177** |
| **total, the reuse path** | | | **2 105** |
| `PrepareBindings`, **not split by resource kind** | — | — | **[NM], 3 991 µs a frame in total** |

**The buffer figure is an UPPER attribution and says so.** `P_buf` is an average over all 48 416
buffer slots, and `RebindBuffers` contains `ObtainBuffer`, the stream copies and the
synchronisations — a repeating slot is very probably cheaper than the average. The image figure is
not similarly inflated: **90.7 % of image slots take the memo fast path** (`texfast_ok` 44 153
against `texfast_no` 4 503), so the average is close to the fast-path price.

**Against `ROADMAP` §2 C, which says "порядка 5–7 мс — цена ПРОВЕРКИ мемо, которые попадают":** the
whole reuse path measures **4 824 µs a frame** (`bl_img_us` + `bl_buf_us`), so the 5–7 ms is the
right order for the checking as a whole — **but at most 2 105 µs of it stands on slots that
repeat**, and that is the part a per-slot skip could reach. **Route C's exploitable ceiling is ~2.1
ms a frame, not 5–7 ms**, with an unsplit 3 991 µs in `PrepareBindings` still to be divided.

**How much of the bind phase this accounts for.** 3 991 + 1 101 + 3 723 = **8 815 µs a frame** of
instrumented bind-side work, less the instrument's own **357 µs** = **8 458 µs**, against
`mh_bind` **11 429 µs** (`flr83b`, session 83) = **74 %**. The commit side, 2 647 µs, is **35 %** of
`mh_emit` 7 586 µs. Prediction U8 — the commit side is smaller than the bind side — **HIT**
(2 647 < 4 824).

### 3.5 THE MARGIN — declared uninformative by a rule fixed before the run

`pred/02` §4.2 asked for
`bl_img_us = a + c·bl_stage_n + b_hit·texfast_ok + b_miss·texfast_no`. It ran over 3 657 frames at
R² = 0.8039 and produced `b_hit` = 8.21 ns, `b_miss` = 216.85 ns — **and a maximum VIF of 60.9**
against the limit of 20 that `pred/02` §4.3 wrote down before the run. The three regressors
correlate at **+0.966 to +0.990**: in this scene the stage count, the hit count and the miss count
move together and the design cannot separate them.

**So the margin is NOT separable in this design, §4.3's clause fires, and the level of §3.3 stands
alone.** The coefficients above are printed for the record and **decide nothing**; prediction U7 is
**NOT EVALUATED** for that reason and not scored a hit. The buffer-side regression could not run at
all: `bfast_hit` / `bfast_miss` read 0 because gate `buffast` is 0, which the tool printed as
"the normal equations are singular — NOT RUN" rather than substituting anything.

### 3.6 The instrument's own price [M]

`cpu_net_us` **+357.1 ± 72.8 µs (2·SE), t = +9.81** on 122 block pairs (`endpoint84.py`);
`cpu_gpu_us` +356.3 ± 72.8 on 122 matched pairs (`arms.py`); `cpu/draw` **+1.082 % ± 0.109 %,
t = +19.92**; `summary4` +1.113 % ± 0.112 %, cross-check gap +0.003 pp. Prediction U6 — between
+300 and +1 500 µs — **HIT**. `gpu_busy_us` +0.005 % ± 0.170 %, noise.

That is **357 µs for 4 × 9 265 + 4 × 5 090 ≈ 57 400 `NowNs()` calls a frame = 6.2 ns a call**, and
it is the reason the instrument was built at stage granularity rather than slot granularity: at
~48 800 image slots a frame a per-slot pair would have added ~12 ns to a 22.82 ns quantity.

## 4. THE CENSUS — two biases MEASURED, one ELIMINATED, one found to be ZERO

`slotstat` rode **both arms** of `blp85a`, so this is a within-arm reading with no contrast claimed.
Every pre-existing `sl_*` counter kept its logic byte-for-byte.

### 4.1 Session 84 reproduced [M]

| ratio (sums, `blp85a` arm 1) | session 85 | `slp84b` (sums) |
|---|---:|---:|
| `R_img` | **87.432 %** | 87.43 % |
| `R_view` | 87.438 % | — |
| `R_smp` | **95.825 %** | — |
| `R_buf` | 52.880 % | 53.22 % |
| `R_stage` | 2.220 % | 2.29 % |
| all slots | **64.668 %** | 64.88 % |

**`R_img` reproduces to 0.00 pp on the estimator session 84 used for it.** Prediction U12 — within
1.0 pp — **HIT**.

### 4.2 BIAS 3 ELIMINATED, and it was worth −2.89 pp on the headline [M]

A repeat now counts only when the row's previous commit ran the **same** `shader_hash`.

| | uncorrected | corrected | **bias 3, measured** |
|---|---:|---:|---:|
| `R_img` | 87.432 % | **84.933 %** | **−2.499 pp** |
| `R_smp` | 95.825 % | **89.483 %** | **−6.342 pp** |
| `R_buf` | 52.880 % | **49.086 %** | **−3.794 pp** |
| `R_stage` | 2.220 % | 2.209 % | −0.011 pp |
| **all slots** | **64.668 %** | **61.777 %** | **−2.890 pp** |

`sl_shader_chg / sl_stage_n` = **9.353 %** against the **24.8 %** upper bound session 84 derived
from `pmemo_miss`. Predictions U13 (corrected < uncorrected) and U14 (the gap below 24.8 pp) —
**both HIT**. **The upper bound was loose by a factor of 2.6, and the quantity it bounded is now a
number.**

### 4.3 BIAS 1 MEASURED, including the half that was [NM] [M]

| | share of its slots |
|---|---:|
| `sl_img_null / sl_img_n` — image slots resolved from a null T# | **2.956 %** |
| `sl_buf_null / sl_buf_n` — the constant `{NULL_BUFFER_ID, 0, 16}` descriptor | **2.370 %** |

The image figure confirms session 84's ~2.9 % estimate to 0.06 pp (U17 **HIT**); the buffer figure
was **[NM]** in session 84 and is now measured (U15 **HIT**). Both are structural repeats: they are
real and a partial update really could skip them, but they are not the game rebinding anything.

### 4.4 BIAS 2 MEASURED, AND IT IS ZERO IN THIS SCENE [M] — a predicted MISS

`sl_img_elem / sl_img_n` = **1.0000** (175 090 380 against 175 090 210 on sums, 1.0 × 10⁻⁶ apart);
`sl_smp_elem / sl_smp_n` = **1.0000**. **There is no `DynamicStorage` multi-mip binding in Sky
Garden**, so the bias session 84 could only bound is **zero here**. Prediction U16 —
`sl_img_elem > sl_img_n` — is a **MISS**, and it is the more useful outcome: the bias is measured
rather than assumed.

### 4.5 The self-check, and what it honestly is not [M]

**`sl_bad` = 0** — sum 0, max 0 over 1 915 settled frames of `spv85a` and over 3 657 frames of
`blp85a`; zero `SlotStatVerify` lines anywhere. Prediction U1 **HIT**.

**It is an ELEMENT-COUNT check and not a value check, and `pred/02` §6 said so before it was
built.** The quantity the census reports is *"did this slot equal what the same row held last
time"*, and the shadow table is the only record of last time; everything recomputable at that site
re-derives **this** draw's value. What is checked is that the elements the write list will emit,
derived from the compiled `BindingLayout`, agree with what the census counted — which is precisely
what would have caught bias 2 before publication, had there been any to catch. The **sampler**
identity is measured and never accused: nothing in the tree guarantees every entry of
`prepared.samplers` is referenced by a binding, while the image one is guaranteed by session 84's
own D2 assertion.

### 4.6 The routing verdict, on the corrected ratios

`R_stage_sh` **2.209 %** < 30 % and `R_img_sh` **84.933 %** ≥ 60 % ⇒ **route C's lever is
PER-SLOT**, unchanged from session 84. Prediction U18 **HIT**. **And now it has a price and a
ceiling** (§3.3, §3.4), which is what separates this session's statement from last session's.

## 5. WHAT `bda_scan_us` IS — the session-84 debt, closed [M]

`bdasplit` rode **both arms** of `blp85a`; the two arms agree to 0.1 % on every counter below, so
the reading is quoted once.

| counter | per frame | per unit |
|---|---:|---|
| `bda_bound_us` — the two `m_buffers` descents | **18 µs** | 300 calls → **60 ns a call** |
| `bda_walk_us` — `SynchronizeBuffersByRegion`, whole | **2 287 µs** | 75 calls |
| `bda_collect_us` — `CollectCpuModifiedRanges` | **65 µs** | |
| `bda_up_us` — `SynchronizeBuffersOfDirtyRanges` | **2 121 µs** | 1 070 scanned regions → **1.98 µs a region** |
| per-region visit = walk − collect − up | **101 µs** | ~21 000 visits → **≈ 4.8 ns a visit** |
| `bda_first_us` — the frame's FIRST scanning `PrepareBda` | **977 µs** | **1 call → 977 µs a call** |
| `bda_late_us` — every later one | **1 337 µs** | 24 calls → **55.7 µs a call** |

**92.7 % of the walk is `bda_up_us`, and `bda_up_us` is a `memcpy`.** `sync_up_kb` is
**22 761 KiB a frame**; 22 761 KiB ÷ 2 121 µs = **10.99 GB/s**, inside the 10–20 GB/s band
hypothesis H of `pred/02` §5 named **before the run**. Prediction U9 (`bda_up_us` > 1 000 µs)
**HIT**; U10 (first/late per call ≥ 5×) **HIT at 17.5×**.

**Hypothesis H is confirmed on its substance and only partly on its shape, and the difference is
recorded rather than rounded away.** H said the fixed part is the first full-span pass. Per call the
first is **17.5× dearer**; but there are 24 later calls, so they still carry **58 %** of the total
(1 337 µs against 977 µs). The correct statement is not *"the first call pays it all"* — it is
**"the first call pays 17.5× what a later one pays, because it consumes the dirty bits, and what it
is paying for is the staging copy of 22 MiB a frame."**

**Session 83's bound on the `std::map` descents was 20× too loose.** It read *"1 754 tree descents
a frame ⇒ 0.18…0.35 ms"*; measured, `bda_bound_us` is **0.018 ms** — 60 ns a call across all 300
calls including the ~216 that find no registered buffer and return. Prediction U11 (< 400 µs)
**HIT**, and by an order of magnitude.

**So the lever named by three sessions of the record is the wrong one.** It is not "make fewer
calls miss" (session 84), not "make the map faster" (session 82's candidate, session 83's bound),
and not the region walk (session 82's `bdabits`, −50.8 ± 87.5 µs, and now explained: **4.8 ns a
visit**, so 20 601 skipped visits could never have been worth a millisecond). It is **move 22 MiB a
frame less, or move it faster.**

`bda_walk_us` + `bda_bound_us` = **2 305 µs** against session 84's `bda_scan_us` **2 232.5 µs** —
different runs and different binaries, so this is a **cross-session consistency reading and nothing
more**; it agrees to 3.2 %.

## 6. ROUTE B's NEXT PACKAGE — one item, and it does NOT pay

### 6.1 What survived reading, and what did not

`next-session-85.md` §3.2 offered items **2, 3, 6 and 8**. One was built.

| item | claimed | verdict, fixed in `pred/01` §1 before any number |
|---|---:|---|
| **6a** — the duplicated upload-epoch evaluation | part of 150–400 µs | **BUILT** |
| 6b — the clean verdict reused in `SyncFreeSkip` | the rest | **REFUSED: unsound as written** |
| 3 — `ImageDesc` by reference on a memo hit | 150–300 µs | **REFUSED: correctness not checkable in this shape** |
| 2 — texture-memo associativity | 250–550 µs | **NOT BUILT: its own decisive measurement does not exist** |
| 8 — const-bank copy batching | 40–120 µs | **DEFERRED: design corrected and recorded, §8.2** |

### 6.2 Why 6b and 3 were refused [I]

**6b.** `SyncFreeSkip`'s own safety comment requires the clean read to **follow** the epoch
snapshot. `ObtainBuffer`'s read **precedes** it, so a guest write landing between them would be
missed **and then sealed** by the `buffer.upload_epoch = cpu_epoch` store. Making it sound needs the
epoch pair carried down as well — a second change to the same lines, and a different item.

**3.** The plan names three consumers of `TextureBinding::desc`; there are **five**
(`RebindImages`, `ShadowQueue`, `CommitBindings`, `renderDraw.cpp`'s depth feedback-loop scan inside
`AcquireRenderTargets`, and `renderCompute.cpp`). The revalidation the plan cites — *"`slot->valid
&& slot->version == binding.memo_version && slot->image_id == binding.image_id`"* — **guards the
cached VIEW, not the desc**: its fallback arm calls `FindTexture(binding.image_id, binding.desc)`,
which under a reference scheme would receive the **new occupant's** desc, and `FindTexture`
mutates. The memo slot is overwritten **in place** mid-draw, both by a same-draw slot collision and
by `RebindImages`' own re-resolve. **The programme does not ship a change whose correctness it
cannot check** — the standard that refused item 11's third edit in session 84. A safe shape exists
and is written down in §8.1 so the next session starts from it rather than from the plan.

### 6.3 The self-check, and a race window measured rather than argued [M]

`spv85a`, `bindpack2=1 bindpack2check=1`: **`bp2_bad` = 0, sum 0, max 0 over 1 915 settled
frames**, zero `BindPack2Verify` lines. Prediction B1 **HIT**.

**`be_race` = 1 055 over 9 546 500 short circuits = 0.0111 %**, non-zero on 811 of 1 915 frames,
worst frame 4. That is the window this change widens — a guest write landing between
`ObtainBuffer`'s epoch read and the one inside `SynchronizeBuffer` — **entered about 0.55 times a
frame, 1 call in 9 000**. Prediction B8 **HIT**. It is small, it is **measured**, and it is the
number that would have had to be argued had the package shipped.

### 6.4 `bn2d85a` — VALID on every pre-registered criterion

| criterion | reading | |
|---|---|---|
| 1. check 2 / check 10 | 0 MISMATCH lines; binary confirmed, 260 `GateArm` blocks, arm0 ×130 arm1 ×130 | PASS |
| 2. arming inside the run | §6.5 | PASS |
| 3. area split < 1.0 % | **−0.003 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (124/124)** | PASS |
| 3. work within 0.5 % | **−0.133 %** | PASS |
| 4. whole-arm vs paired gap < 0.05 pp | +0.007 % vs +0.009 %, **+0.001 pp** | PASS |
| 5. `da_take_us` | **304.2 → 304.8 ns, +0.20 %** | reported |
| 6. everything on matched pairs | the deciding estimator runs on **125 block pairs** against 124 area-matched ones; both are reported and they agree | reported |

Check 6 (cores) FAILs — 6 of 50 groups — and is not an admission criterion.

### 6.5 Arming, and the falsifiers [M]

| counter | arm `bindpack2=0` | arm `bindpack2=1` | |
|---|---:|---:|---|
| `be_fast` | **0.000** | **5 396** | B2 HIT |
| `bufepoch` | 8 553 | 8 549 | **−0.05 %**, unchanged by construction |
| `bp2_bad` | 0 | 0 | |
| `sf_skip` | 26 607 | 26 607 | **0.000 %** |
| `sync_noop` | 26 606 | 26 607 | **+0.004 %** |
| `sync_ups` | 74 | 74 | **0.000 %** |
| `sync_up_kb` | 22 974 | 22 953 | **−0.091 %** |

**All four falsifiers are unmoved**, so the short circuit removed exactly the redundant evaluation
and no real work. Prediction B4 **HIT**.

**`be_fast` 5 396 against `bufepoch` 8 553 in arm 0 = −36.9 %.** Prediction B3 — within 5 % —
is a **MISS**, and the cause is in `PLAN_82_bind.md`'s own text: `bufepoch` is an upper bound
because the same counter is incremented from the slow path at `bufferCache.cpp:1126` and from
`CollectBufferUpload`. **The population item 6a actually addresses is 5 396 a frame, not 8 486** —
63 % of what the plan claimed, and that is the number the effect must be divided by.

### 6.6 The effect, and the decision [M]

| statistic | population | value |
|---|---|---:|
| **`cpu_net_us`, the pre-registered primary endpoint, in µs** (`endpoint84.py`) | 125 block pairs | **−35.9 ± 81.2 (2·SE), t = −0.88** |
| `cpu_gpu_us` (`arms.py`) | 124 matched pairs | −52.5 ± 74.4 |
| `cpu/draw` (`area_verdict.py`) | 124 matched pairs | **−0.030 % ± 0.125 %, t = −0.47** |
| `cpu/draw` (`summary4.py`) | 129 cycles | +0.009 % ± 0.132 %, t = +0.13 |
| `gpu_busy_us` | 129 cycles | +0.124 % ± 0.188 %, noise |
| `dt_us` | 129 cycles | inside the vblank plateau, not an endpoint |

`pred/01_bindpack2.md` §6, fixed before the number existed: **ship at `E ≤ −150 µs` with a 2·SE
excluding zero.** Measured **−35.9 ± 81.2 µs**, interval **[−117.1, +45.3]** — the interval
includes zero and |E| < 150 µs.

→ **NOT PAID FOR. `bindpack2` stays at 0.** The code stays in the tree: it is correct, self-checked
(`bp2_bad` = 0) and its race window is measured. **The bar was not moved**, in either direction.

**Predictions B5 (negative) and B6 (in [−200, 0], i.e. does NOT clear the bar) — both HIT, and B6
was the discriminating one.** It was written to be able to lose in the direction this session would
have preferred, and the arithmetic behind it was published in `pred/01` §2 before the run:
`regionepoch` is 0 by shipped default, so `UploadEpoch` is one acquire load of `m_cpu_epoch` and
`HasCurrentUpload` is a handful of inline comparisons — 10–20 ns of removed work over ~8 500 calls.
The population turned out to be 5 396, not 8 500, and the effect landed below the band's own floor.

### 6.7 The per-call unit price this run bought anyway [M]

`pred/01` §3 fixed before the run that this contrast supplies a **per-call unit price under every
outcome**, because the removed work is enumerable and its population is counted inside the run.

**`E / be_fast` = −35.9 µs / 5 396 = −6.65 ns a call**, and on the 2·SE interval
**[−21.7, +8.4] ns a call**. Prediction B7 (5–30 ns) **HIT by magnitude**, but it is reported as a
**bound, not a point**: the effect does not clear its own noise, so what this run establishes is
that *the removed work costs less than about 22 ns a call*. That is consistent with §2's 10–20 ns
arithmetic and it is the second unit price of the session.

## 7. `dapin` — the sixth-session GPU debt: a fifth replication, one candidate eliminated, and the prescribed measurement RETIRED

**None of these three runs was pre-registered.** `next-session-85.md` §3.3 asked for *"one
`KYTY_GPU_TIME` pair on a `dapin` ABBA"*; that run was taken first, its answer was ambiguous, and
two further runs were taken to make it interpretable. No threshold rides on any of them.

| run | record thread | `cpu/draw` | **`gpu_busy_us`** |
|---|---|---:|---:|
| `dgt85a` — `dapin=1\|3` **with `KYTY_GPU_TIME=1`** | **OFF** (`PacketsWanted()` false) | −1.513 % ± 0.190 % | **+0.095 % ± 0.186 %, t = +1.02 — NOISE** |
| `dap85a` — `dapin=1\|3`, same binary, same scene | **LIVE** | **−2.233 % ± 0.145 %, t = −30.71** | **+1.961 % ± 0.165 %, t = +23.74** |
| `rcp85a` — `recpin=0\|1`, `dapin` at its default 3 | moved by the gate | **−5.082 % ± 0.142 %, t = −71.39** | **+0.098 % ± 0.186 %, t = +1.06 — NOISE** |

All three are VALID on the three area criteria (splits −0.002 %, +0.000 %, −0.003 %; pair match
100 % in each; work +0.048 %, +0.045 %, −0.125 %), with checks 2 and 10 PASS and check 6 FAILing as
it routinely does.

**1. The GPU cost replicated a FIFTH time, and this is the tightest reading it has ever had.**
`dap85a`: **+1.961 % ± 0.165 %, t = +23.74** over 128 cycles, against +1.238 / +1.350 / +1.931 /
+1.679 % in sessions 79–82. It is not an artefact of an old binary or an old harness.

**2. The measurement the record has been prescribing for it CANNOT SEE IT, and that is why six
sessions produced nothing.** `dgt85a` — the exact run the brief asked for — reads **+0.095 % ±
0.186 %**. Its own resolution is 6.7× finer than the effect it was looking for, so it did not miss
the effect for lack of power: **under `KYTY_GPU_TIME` the effect is absent.** Turning the profiler
on changes what `gpu_busy_us` is derived from, and `PacketsWanted()` goes false with it.
**`KYTY_GPU_TIME` is the wrong instrument for this question and is retired from it.**

**3. The record thread is NOT the carrier.** The obvious reading of (2) was that
`KYTY_GPU_TIME` removes the record thread and `recpin` (default 1 since session 63) pins that
thread to the `dapin` mask — so the record thread would be carrying the GPU cost. `rcp85a` tests
exactly that, without the profiler: moving the record thread from the process mask to the `dapin`
CCD costs **+0.098 % ± 0.186 % of `gpu_busy_us` — nothing**. The arming is clean: `rec_ccd_x`
**34 → 0**, the cross-CCD wakeups the pin exists to remove. **The candidate raised in this session
was killed by this session, in the run that was built to kill it.**

**4. A number worth keeping on its own.** `recpin=1` is worth **`cpu_net_us` −1 687.3 ± 80.6 µs,
t = −41.87** and **`cpu/draw` −5.082 %** — by a wide margin the largest within-run effect in this
record, and it has been the shipped default since session 63. It is a confirmation of a shipped
default, not a new saving; `draws` differ by +4.3 % on medians and **−0.125 % on sums**, so
`cpu/draw` is the statistic that means anything here (the median trap again).

**What is left of the debt:** the +1.96 % is real, replicated five times, visible only with the
record thread live, and **not** caused by the record thread's placement. That is narrower than
"unexplained" and it is where session 86 should start.

## 8. DESIGNS RECORDED SO THE NEXT SESSION DOES NOT START FROM THE STALE PLAN

### 8.1 Item 3, the safe shape [I]

A raw pointer or a memo index in `TextureBinding` is unsafe (§6.2). What is safe is a **desc arena
addressed by index**: `RenderExecutor` gains `std::vector<TextureCache::ImageDesc> m_desc_arena
{4096}` plus a per-draw serial; `RenderExecutorMemo::Texture` keeps a `uint32_t desc_slot` instead
of a 584-byte `desc` (the memo shrinks by 2.3 MiB and the arena gains it back, net zero); a memo
**store** takes the next arena slot rather than overwriting the one an in-flight binding
references, and counts a `dr_wrap` when the arena turns over inside one draw — structurally 0 at
≤ 64 bindings a draw against 4 096 entries, and **measured instead of asserted**.
`TextureBinding` then carries 4 bytes where it carried 584 (the binding goes 640 → 60 bytes) and the
copy disappears for the miss, `!store` and null-T# paths too. **Before any of it is written, one
counter: how often a binding's memo slot is overwritten within the draw that holds it.**

### 8.2 Item 8, the corrected design [I]

Site 1's const-bank copies can be coalesced into one `Map` / `Commit` per draw — every input is
already materialised by `FindBuffers` — but the reader's first design is **wrong in one load-bearing
place**: there is a **third** consumer of the same `m_stream_buffer` inside the very loop being
batched (`ObtainBuffer`'s own stream path), so "commit before any site-2 `Map`" is not sufficient.
`StreamBuffer` holds a single `m_offset` / `m_mapped_size`, and `Commit` does not reset
`m_mapped_size`. The arming proof is **`dp_stream_maps`** (not `d_stream_maps`), and the self-check
is to re-read the mapped sub-range through `Mapped().data() + sub_offset` and `memcmp` it against a
fresh `TryReadBacking` — `cbstat` alone cannot catch a wrong offset, because its shadow hashes guest
bytes rather than the ring.

## 9. WHAT WAS NOT DONE

* **No video pass.** Nothing shipped: every gate this session added is at 0, and with them at 0 the
  rendering path is behaviourally identical to the one session 84 shipped - the new code is
  reachable only through those gates. It is NOT a byte-identical binary and no pixel comparison
  was made; what is claimed is that no shipped default changed, so the `ROADMAP` §6 video debt is
  not incurred.
* **No `acc85a`.** No default changed, so there is nothing to confirm; the installed binary carries
  the session-84 defaults plus four gates that are all off.
* **`PrepareBindings`' 3 991 µs a frame is not split by resource kind**, so the image-slot ceiling
  of §3.4 has an unmeasured second term. That is the next measurement of route C.
* **The marginal per-slot price is [NM]**: the OLS was collinear and §4.3's clause fired (§3.5).
* **The buffer-side unit price is an average that cannot be decomposed** in this run, because
  `buffast` is 0 and `bfast_hit` / `bfast_miss` read 0.
* **No `mutsite=1` run**, so every `mh_*` reads 0 in every run of this session, as in session 84.
* **`dapin`'s GPU cost is still unexplained**, but it is narrower by one eliminated candidate and
  one retired instrument (§7).

## 10. THE SCOREBOARD — all twenty-nine predictions, scored

`pred/01_bindpack2.md` §7 — ten:

| | prediction | result |
|---|---|---|
| B1 | `bp2_bad` = 0 in `spv85a` | **HIT** (0 over 1 915 frames, 0 log lines) |
| B2 | `be_fast` 0.000 median in arm 0, non-zero in arm 1 | **HIT** (0 → 5 396) |
| B3 | `be_fast` within 5 % of `bufepoch` in arm 0 | **MISS** (−36.9 %) — §6.5, and the cause is in the plan's own text |
| B4 | `sf_skip`, `sync_noop`, `sync_ups`, `sync_up_kb` each move < 0.5 % | **HIT** (0.000, +0.004, 0.000, −0.091 %) |
| B5 | the effect is negative | **HIT** (−35.9 µs) |
| B6 | `E` in [−200, 0] µs — the package does NOT clear the bar | **HIT** — the discriminating one |
| B7 | `E / be_fast` between 5 and 30 ns a call | **HIT by magnitude** (−6.65 ns), reported as the bound ≤ 21.7 ns |
| B8 | `be_race` > 0 | **HIT** (1 055 = 0.0111 % of short circuits) |
| B9 | `gpu_busy_us` inside its own 2·SE | **HIT** (+0.124 % ± 0.188 %) |
| B10 | `da_take_us` moves < 1 % | **HIT** (+0.20 % per take) |

`pred/02_price.md` §9 — nineteen:

| | prediction | result |
|---|---|---|
| U1 | `sl_bad` = 0 | **HIT** |
| U2 | every `bl_*` 0.000 median in arm 0 | **HIT** |
| U3 | `bl_img_n` vs `b_texn`, `bl_buf_n` vs `bb_n` within 2 % | **HIT** (+0.041 %, +0.012 %) |
| **U4** | **`P_img` > 20 ns** | **HIT** (22.82) — discriminating; see the note below |
| U5 | `P_img` < 200 ns | **HIT** |
| U6 | the instrument costs +300…+1 500 µs | **HIT** (+357.1) |
| U7 | `b_hit` positive and below `P_img` | **NOT EVALUATED** — §4.3's collinearity clause fired (max VIF 60.9) |
| U8 | the commit side is smaller than the bind side | **HIT** (2 647 < 4 824 µs) |
| **U9** | **`bda_up_us` > 1 000 µs** | **HIT** (2 121) — discriminating |
| U10 | first/late per call ≥ 5× | **HIT** (17.5×) |
| U11 | `bda_bound_us` < 400 µs | **HIT** (18 µs — by an order of magnitude) |
| U12 | `R_img` reproduces 87.44 % within 1.0 pp | **HIT** (87.432 %) |
| U13 | `R_img_sh` < `R_img` | **HIT** (84.933 < 87.432) |
| U14 | `R_img − R_img_sh` < 24.8 pp | **HIT** (2.499 pp) |
| U15 | `sl_buf_null` > 0 | **HIT** (2.370 % of buffer slots) |
| U16 | `sl_img_elem > sl_img_n` | **MISS** — exactly equal; bias 2 is **zero** in this scene |
| U17 | `sl_img_null / sl_img_n` within 1.0 pp of 2.9 % | **HIT** (2.956 %) |
| U18 | the corrected routing verdict is unchanged | **HIT** |
| U19 | `sl_over` = 0, scored as structurally unlosable | **HIT, and discounted** — §2.3 |

**26 hits, 2 misses (B3, U16), 1 not evaluated (U7).** Both misses are informative and neither was
skipped: session 84's first draft scored 6 of 19 and both of its misses were among the 13 it never
mentioned.

**The note U4 needs.** U4 asked whether the bind phase's per-slot price is *"an order of magnitude
above the census instrument's 2.48 ns and inside reach of the 52.6–73.7 ns the premise assumes"*.
It is **9.2× the census instrument** — so the first half holds — but at 22.82 ns it is **0.31–0.43×
the premise band**, and it is the **buffer** side at 77.07 ns that lands in the premise's range.
The prediction is a HIT on the number it named and a partial answer to the sentence it was written
in; both halves are said.

## 11. THE ARITHMETIC

| | value |
|---|---:|
| shipped baseline (`acc82a`, not re-measured since) | 31 642 µs = 31.60 FPS |
| 60 FPS | 16 667 µs |
| the measured sequential floor `S_hi` (session 83) | 20 838 µs — **4.2 ms more than the whole 60-FPS budget** |
| **route C's unit price — image slot / buffer slot** | **22.82 ns / 77.07 ns** |
| **route C's ceiling, measured, in the reuse path** | **~2 105 µs a frame** (upper attribution on the buffer half) |
| …plus `PrepareBindings`, not split by resource kind | 3 991 µs a frame, **[NM]** |
| `bda_scan_us`, attributed | **92.7 % staging `memcpy` at 11 GB/s**, 22 761 KiB a frame |
| route B's next package (`bindpack2`, item 6a) | **−35.9 ± 81.2 µs — NOT PAID FOR**, gate stays 0 |
| `dapin`'s GPU cost | **+1.961 % ± 0.165 %**, fifth replication, still unexplained |
| `recpin=1`'s CPU value (shipped since session 63) | **−1 687 ± 81 µs**, confirmed |

**The honest statement of the task.** Session 84 measured that two thirds of a frame's descriptor
slots repeat and could not say what that was worth. Session 85 says what it is worth: **about
2.1 ms a frame in the reuse path, with a second term in `PrepareBindings` still unsplit** — against
a 15 ms gap to 60 FPS and a sequential floor that is already 4.2 ms larger than the whole 60-FPS
budget. **Route C is now the largest measured lever in the record and it is still not enough by
itself**, and the next number is not another population or another ceiling: it is the split of
`PrepareBindings` by resource kind, and then the cost of a partial descriptor update on this
driver — the price of the exploit, not of the work it would replace.
