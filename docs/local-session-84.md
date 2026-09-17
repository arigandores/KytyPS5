# Session 84 — route C's ceiling, measured; the binding-path package, shipped

*This is `C:/kyty/s84/FACTS.md` verbatim, carried into git as the session's report.*
*The harness, the logs and the two pre-registrations live in `C:/kyty/s84`.*

---

# Session 84 — FACTS

**The single source of truth for session 84.** Everything is marked **[M]** measured (a counter in
a run of this session, or a prior session's run named), **[I]** inferred (read from source and
reasoned), **[NM]** not measured, **[R]** retracted.

**This file was rewritten after an independent audit** — four agents recomputed every headline
number from the raw logs with their own parsers and attacked the reasoning. **Every number
reproduced to the digit.** Nothing in §3, §4 or §5's counters moved. What the audit found was in
the *writing*: one false claim, three real limits of the census instrument that the first draft did
not state, a mis-scored prediction, a unit price derived the wrong way, and a run that was taken
and then never reported. All of it is in §2, and the numbers it corrects are corrected in place.

## 0. In one sentence

**Route C's ceiling was measured for the first time: 64.2 % of the 109 836 descriptor slots a frame
binds carry the same value they carried in the previous committed draw of the same stage — 87.4 %
of image slots, 95.9 % of sampler slots — while only 2.06 % of stages repeat everything; the unit
price of a slot is [NM], so this is a ceiling and not a saving.** And the binding-path package,
now four items, shipped at **−251.7 ± 82.8 µs** against the **−150 µs** threshold sealed before the
run — route B's first default change.

## 1. The runs

| tag | binary sha256 | what | verdict |
|---|---|---|---|
| `bpv84a` | `6e86a7f6…` | `bindpack=1 bindpackcheck=1`, warm-up + 120 s | **`bp_bad` = 0** — §4.2 |
| `slp84a` | `6e86a7f6…` | ABBA `slotstat=0 bdalap=1\|slotstat=1 bdalap=1`, 320 s | **VOID** (area split −1.055 %) |
| `slp84b` | `6e86a7f6…` | the same contrast again, 320 s | **VALID** — the census, §3 |
| `bpk84a` | `6e86a7f6…` | ABBA `bindpack=0\|bindpack=1`, 300 s | **VALID** — the package, §4 |
| `bpc84a` | `6e86a7f6…` | `bindpack=1`, 180 s, recorded | **5 986 presents, 0 glitches** |
| `acc84a` | `f0e2ddf4…` | **shipped defaults**, 200 s, **NOT pre-registered** | §6 |

Sky Garden (`-lvl underwater_aerial_garden`) everywhere, settled window **n ≥ 2100**,
`KYTY_FRAME_TRACE=lite`. **Seven emulator launches** (`bpv84a` carries an uncounted warm-up),
**every one entered on the first attempt in 14.3–15.4 s**; no entry hang this session, against the
historical 6.67 %.

**`slp84a` is VOID and its arm contrast is quoted nowhere.** Whole-arm area split **−1.055 %**
against the pre-registered < 1.0 % — 0.055 pp outside. Pair match 97.7 % and work −0.015 % both
passed, so the arms did the same work; the DRS simply moved inside the run. **The criterion was not
substituted, reweighted or retired** — another run of the same contrast was taken, as session 82
did with `dap82a` and session 83 with `flr83a`. `pred/02_slotstat.md` §5 fixed **in advance** what
happens to a void run's numbers (*"its census is reported as a consistency reading and its price
contrast is quoted nowhere"*); **it does not authorise the replacement run, and no pre-registered
text of this session does** — the practice is the record's, carried from sessions 82 and 83, and it
is named here rather than dressed up as a rule. `slp84b` was taken after `bpk84a` and nothing was
re-rolled. What the void run's census is worth is in §3.3.

## 2. RETRACTIONS AND CORRECTIONS TO THIS SESSION'S OWN FIRST DRAFT

1. **[R] "The void run agrees to the valid one to 0.05 pp on every ratio."** False, and contradicted
   by the six numbers printed beside it. **Two of six are inside 0.05 pp; the worst is 8× outside.**
   Gaps (`slp84a` − `slp84b`, pp): `R_smp` 0.013, `R_img` 0.046, `R_view` 0.051, `R_stage` 0.058,
   all-slots 0.179, **`R_buf` 0.403**. The honest statement is in §3.3, and it matters because the
   agreement was the only thing offered for reporting the void run's census at all.
2. **[R] "a miss costs 106.3 µs".** That is a total divided by a count, and it invites the marginal
   reading it does not license. `bda_scan_us` is nearly **fixed per frame**: OLS over 8 026 settled
   frames gives **`bda_scan_us` = 1 875.1 + 16.53 × misses** (r = +0.46). §5 is rewritten around
   the fixed cost, which is the stronger finding.
3. **[R] "Prediction P4 is a MISS."** The null-T# population differs by **+0.85 % on medians** and
   by **+0.037 % on means** — and the same section admits the run on the **mean** work statistic
   (+0.004 %). Reading the admission criterion on means and the arming criterion on medians, then
   blaming the non-additivity of medians for the failure that created, is an error against this
   session's own interest. **P4 is a HIT on every additive statistic.** §4.4.
4. **[R] "the first FPS-relevant source change since session 82."** −251.7 µs is an order of
   magnitude inside the vblank plateau (−1.6 ms … −15.8 ms reads a flat 30.0 FPS), and two other
   sections of this file say so. The package buys frame time; it moves no scoreboard number.
5. **[R] "Route C's ceiling … is large"** as an unqualified adjective, in §0 and §8. A population
   whose unit price is [NM] cannot be known to be large. §3.6 now puts the one per-slot price this
   session *did* measure — **2.48 ns** — against the **52.6–73.7 ns/slot** that route C's own
   5–7 ms premise implies, which is the comparison the first draft avoided.
6. **`acc84a` was taken, was the only run of the shipped binary, and appeared in no section.** Its
   verdict cell pointed at §5, which never mentioned it. It now has §6, including the admission
   that **it is the only run of this session covered by no pre-registration and named in no plan**.
7. **[R] §6 item 6's "all of which have a compiled fallback of 0."** `bindpack`'s compiled fallback
   is now **`true`** — by this session's own ship. The conclusion (the stale `gates_base.txt` masks
   nothing) survives and is re-derived in §7.6 from the corrected premise.
8. **Line numbers this session's own edits invalidated.** `PrepareBda`'s dispatch-side call is
   `renderCompute.cpp:795`, not `:791` — it moved 4 lines when the item-9 arming pair went in at
   `:786-790`. And `PLAN_82_bind.md`'s item-11 anchors are now **+298** and **+327**, not +141,
   because `NoteSlotStat`/`VerifyDescSetCounts` added ~150 lines above them. The section whose
   lesson is *anchor on verbatim text* had republished numbers its own patch had moved.
9. **`PLAN.md` §1 item 3 declared a `SlotStatVerify` / `sl_bad` self-check that was never built.**
   There is no such symbol in the tree. The census therefore has **no value-level self-check** —
   only two population identities. §3.5 states that as the instrument's main weakness.
10. **Neither §3.2 nor §4.4 reported the arm-0 tail**, which both pre-registrations require. Both
    now do (§3.2, §4.4); both tails are benign.
11. Smaller, all verified and fixed in place: the video pass's "max difference 4.6–5.3 throughout"
    described only the settled window, not the load (§4.7); two rows of §4.5's matched-pair table
    came from `summary4`'s population, not the matched pairs; `arms.py` and `summary4` compute
    `cpu_gpu_us`, not `cpu_net_us`, and are relabelled; criterion 6 for `bpk84a` is marked
    **PARTIAL**, not PASS (§4.3); the entry range is 14.3–15.4 s over **seven** launches.

## 3. THE ROUTE-C CENSUS — the first measurement of its ceiling

### 3.1 `slp84b` — VALID on every pre-registered criterion

| criterion (session 81 §1, carried unchanged) | reading | |
|---|---|---|
| 1. `guards.py --first-frame 2100` check 2 | 0 MISMATCH lines in log and stdout | PASS |
| 1. …check 10 | binary confirmed, 278 `GateArm` blocks, arm0 ×139 arm1 ×139 | PASS |
| 2. arming by a counter inside the run | §3.2 | PASS |
| 3. area split < 1.0 % | **−0.001 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (134/134)** | PASS |
| 3. work within 0.5 % | **−0.064 %** | PASS |
| 4. `summary4` whole-arm vs paired gap < 0.05 pp | +1.010 % vs +1.013 %, **+0.004 pp** | PASS |
| 5. bracketing timer `da_take_us` | **312.3 → 312.8 ns, +0.15 %** | reported |
| 6. everything on matched pairs | yes (134 pairs, all matched) | PASS |

Check 6 (cores) FAILs, as it does routinely; it is not an admission criterion.

### 3.2 Arming, proved inside the run — with the tail

| quantity | arm `slotstat=0` | arm `slotstat=1` | |
|---|---:|---:|---|
| every `sl_*` | **0.000 median** | non-zero | PASS |
| `sl_img_n` against `b_texn` | 0 | 49 582.5 vs 49 571.5 = **+0.02 %** | limit 2 % |
| `sl_buf_n` against `bb_n` | 0 | 48 894.0 vs 48 901.0 = **−0.01 %** | limit 2 % |
| `sl_over` | 0 | **0 in every frame of the run**, max 0 | the bounds hold |

On sums the two identities are tighter still: `sl_img_n`/`b_texn` **−0.0067 %**, `sl_buf_n`/`bb_n`
**−0.0048 %**. Both denominators are counted in the binding phase by code this gate does not touch,
and run in **both** arms.

**The arm-0 tail [M].** 62 of 4 020 arm-0 frames (**1.54 %**) carry a non-zero `sl_*`, **every one
of them at offset 0 inside its block** — the schedule-boundary straddle `pred/01` §4 describes, one
flip's Poll against the frame it is attributed to, not leakage. The worst single frame reads
`sl_img_n` 782 = **1.577 %** of the armed median (above `pred/02`'s 1 % line on that one frame);
in aggregate the leak is **0.0069 %** of the armed sum. `sl_stage_all` and `sl_over` are 0 in every
arm-0 frame. **Dropping every straddle frame moves the ratios of §3.3 by at most 0.030 pp.**

**One arming check of `pred/02` §4 could not be run and its absence was not declared in the first
draft.** The third row — `sl_stage_n` within 2 % of `bp_mask`'s population — is not evaluable in
`slp84b`, because `bp_mask` sits behind `bindpack`, which is 0 in that run: it reads 0.000 in both
arms. **`sl_stage_n` is therefore the one census counter with no pre-registered arming identity in
this run**, and it is the denominator of `R_stage` and of every per-stage figure. A substitute
identity exists in the same run and is reported as the substitute it is: `pmemo_hit + pmemo_miss` =
**9 090** graphics stage commits against `sl_stage_n − dispatches` = **9 082**, i.e. **−0.09 %**.

### 3.3 The census [M] — medians over the settled window, `slp84b` arm 1

| counter | per frame | |
|---|---:|---|
| `sl_stage_n` | **9 350** | prepared stages (1.72 per draw or dispatch) |
| `sl_stage_all` | **193** | stages where every slot repeated |
| `sl_img_n` | **49 582.5** | image **bindings** (5.30 per stage) — see §3.5 |
| `sl_img_same` | **43 354.5** | …same `VkImageView` **and** same layout |
| `sl_img_view` | **43 358** | …same view, layout ignored |
| `sl_smp_n` | **11 360** | sampler slots (1.21 per stage) |
| `sl_smp_same` | **10 891** | …same `VkSampler` |
| `sl_buf_n` | **48 894** | buffer slots (5.23 per stage) |
| `sl_buf_same` | **16 307** | …same `{VkBuffer, offset, range}` |
| `sl_buf_ring` | **17 083.5** | stream-ring views, counted **independently** of `sl_buf_same` |
| `sl_over` | **0** | nothing past the translation-time bounds, in any frame |

| ratio, as `pred/02` §6 defines it | ratio of medians | ratio of sums |
|---|---:|---:|
| **`R_img`** | **87.44 %** | 87.43 % |
| `R_view` | 87.45 % | — |
| **`R_smp`** | **95.87 %** | — |
| **`R_buf`** = `sl_buf_same / (sl_buf_n − sl_buf_ring)` | **51.26 %** | **53.22 %** |
| ring share of the buffer slots | 34.94 % | — |
| **`R_stage`** | **2.06 %** | **2.29 %** |
| **all slots** | **64.23 %** | **64.88 %** |

**`pred/02` §6 defines these ratios as ratios of counters and fixes no estimator.** Every figure
above is a **ratio of medians** unless the third column says otherwise, and the estimator choice is
not free: `R_buf` moves **1.96 pp** and the all-slots headline **0.65 pp** between the two forms.
The routing verdict survives all of them (`R_stage` ≤ 2.29 % ≪ 30 %, `R_img` ≥ 87.4 % ≥ 60 %). For
the same reason "109 836 slots a frame" is a **sum of three medians**; the median of the per-frame
total is **109 994**, and both sit **~16 % above the ~95 000** that `ROADMAP` §2 C's premise is
written in.

**The void run, honestly.** `slp84a` reads `R_img` 87.48, `R_view` 87.50, `R_smp` 95.86, `R_buf`
51.67, `R_stage` 2.12, all-slots 64.41. **Two of the six ratios are within 0.05 pp of the valid run
and the worst — `R_buf` — is 0.40 pp away.** That is a consistency reading of a void run and it is
reported as nothing else; no conclusion rests on it.

### 3.4 What this says

**`pred/02` §6's routing rule, applied mechanically: `R_stage` < 0.30 and `R_img` ≥ 0.60 → the
slots repeat but the stages do not. Route C's lever is PER-SLOT.** It needs partial descriptor
updates or a set layout that separates the static slots from the volatile ones — the hardest of the
three outcomes the rule allowed for, and the one this programme has never priced.

**And the shape is not the one the first draft claimed.** It is tempting to write "87 % of slots
repeat and yet only 2 % of stages do — one changed slot spoils the stage." The arithmetic says the
opposite is the finding. Take the measured per-slot rates and the measured 11.75 slots a stage and
assume independence: `0.8744^5.303 × 0.9587^1.215 × 0.3335^5.229` = **0.15 %**. Measured `R_stage`
is **2.06 %**, i.e. **13.8× MORE stage-level repeat than independence predicts.** The information
in these three numbers is **clustering**: when a stage's slots change they change together, and
when they do not, a whole stage is often clean. The low absolute `R_stage` is forced by the slot
count; the excess over independence is not, and it is the part that bears on whether any
group-level skip is exploitable.

`R_stage` also carries an uncorrected artefact that `R_buf` does not: **1.83 stream-ring slots per
stage cannot repeat by construction**, so a stage that binds one can never enter `sl_stage_all`.
`pred/02` corrects `R_buf`'s denominator for exactly that and leaves `R_stage` uncorrected.
Prediction **C6 — `R_stage` < 0.30 — was therefore close to unloseable before the run**, and
`pred/02` §7 named it half of "the discriminating pair". It is scored a HIT in §9 and that HIT is
worth very little.

### 3.5 THREE LIMITS OF THE INSTRUMENT, all found by the audit, none of them in the first draft

The census has **no value-level self-check** — `PLAN.md` declared a `SlotStatVerify`/`sl_bad` gate
and it was never built (§2.9). Its only corroboration is two *population* identities. Three
consequences, each read out of the source and each pushing `R_img` and `R_buf` **upward**:

1. **The `key != 0` / `handle != 0` guard cannot fire, so degenerate bindings count as repeats.**
   A null T# does not arrive as a null view: `ResolveTextureWith` resolves it through
   `FindImage(NullTextureDesc(...))` to a real shared image, and `MakeImageInfo` `EXIT_IF`s on a
   null view, so **no committed image slot is ever null**. A null buffer is worse:
   `NativeStorageBuffer` returns `{GetBuffer(NULL_BUFFER_ID).Handle(), 0, 16}` — a **constant**
   descriptor — for every `address == 0 || size == 0`. These are *real* repeats that a partial
   update really could skip, so they are not spurious; but they are structural, not the game
   rebinding the same texture. Size of the image half, measured in this run: `tnull_miss` ≈
   **1 440 of 49 582 image slots a frame, 2.9 %**, all of them guaranteed repeats. The buffer half
   has **no counter** and is **[NM]**.
2. **`sl_img_n` counts image BINDINGS, not descriptor elements.** A `DynamicStorage` mip binding
   holds `mip_views[0..N−1]` and the descriptor write emits N elements from it
   (`MakeImageInfo(..., element)` selects `mip_views[element]`), but the census contributes 1 and
   compares only `mip_views.front()`. So the headline "109 836 descriptor slots" is a count of
   bindings, and `R_img` can score a binding *same* while elements 1…N−1 changed. Population of
   mip bindings: **[NM]**.
3. **The shadow row is keyed `(ShaderType, positional index)` with no shader identity.** When the
   previous committed draw on that stage ran a **different shader**, index `i` denotes a different
   logical binding in a different layout. A positional match there is not skippable by any partial
   update, and it still counts. Upper bound from this run: `pmemo_miss / (pmemo_hit + pmemo_miss)`
   = **2 252 / 9 090 = 24.8 %** of graphics stage commits had register inputs differing from the
   previous draw's — an over-estimate of the shader-change rate, but the right order.

**All three bias the ratios up, and none of them is quantified.** `R_img` = 87.4 % should be read
as **an upper bound on the fraction of image bindings a per-slot skip could exploit**, with at
least 2.9 pp of it structural null bindings and an unmeasured share of it positional aliasing
across shader changes. That is still a large number, and it is the first one of its kind in this
programme; it is not a number to design against without the self-check the plan promised.

### 3.6 The instrument's own price, and the comparison the first draft avoided

On the 134 matched pairs: `cpu_gpu_us` **+274.1 ± 75.2 µs** (`arms.py`), `cpu_net_us` **+272.2 ±
74.8 µs, t = +7.27** (`endpoint84.py`), `cpu/draw` **+0.949 % ± 0.124 %, t = +15.26**. `summary4`
reads +1.013 % ± 0.138 %, cross-check gap +0.004 pp. Prediction C7 HIT.

That is **272.2 µs / 109 836 slots = 2.48 ns per slot** for a compare, a store and a conditional
`Add` — **the only per-slot price this programme has ever measured.** Set against it:

| | ns per slot |
|---|---:|
| `ROADMAP` §2 C's premise: 5–7 ms of memo-check price over ~95 000 slots | **52.6 – 73.7** |
| measured here, for touching a slot and comparing it | **2.48** |

**Nothing in this session says the expensive 53–74 ns is spent on the slots that repeat**, and the
census is deliberately sited in `mh_emit_us` while the 5–7 ms is spent in `mh_bind_us`. A repeated
*output* at the end of the bind phase is not a demonstration that the bind phase's *checking* was
skippable. That gap is the honest statement of what still stands between 64.2 % and a saving, and
it is why §8 calls the unit price the next number rather than the exploit the next build.

## 4. THE BINDING-PATH PACKAGE — four items, and it SHIPS

### 4.1 The fourth item, and the sub-edit that was refused

| item | `PLAN_82_bind.md` | state |
|---|---|---|
| A — null T# descriptor memo | item 1 | in the tree since session 83 |
| B — one binding-kind scan a stage | item 4 | in the tree since session 83 |
| C — the unread `GraphicsBindings` | item 9 | in the tree since session 83 |
| **D — the descset bundle, two of three edits** | **item 11** | **new this session** |

* **D1** — `descriptor_count`, `write_count` and `push_stages` are cached on
  `PipelineCache::Pipeline`, where `CreateDescriptorLayout` already computes exactly them and
  throws them away, and `CommitBindings` stops rebuilding them per draw. Staleness is impossible
  [I, call graph]: every write is inside `CreatePipelineInternal` before `ready.store(release)`,
  every read after `ready.load(acquire)`, and the pipeline key pins the permutation ids that pin
  the binding layout. **Both `EXIT_IF`s of the pre-pass loop are kept** — only the inner descriptor
  walk is skipped [verified by the audit at `descriptors.cpp:2299` and `:2311-2314`, outside the
  `if (!bind_pack)` guards].
* **D2** — the `m_image_occurrences` invariant loop moves behind `DrawStat::On()`. It is a pure
  assertion with no consumer; the vector's load-bearing uses are untouched. `KYTY_FINAL` is
  `#undef` in this build, so its `EXIT_IF` is a live branch.

**D3 — writing only the used sub-range of the 128-byte push block — was REFUSED**, and the reason
was fixed in `pred/01_bindpack4.md` §2 before any number existed. A sub-range `vkCmdPushConstants`
leaves the remainder **undefined, not zero**; the layouts here are **not** push-constant-compatible
with each other; and **no self-check can detect the failure**, because the shader would read
garbage where it reads a defined zero today, surfacing as a corrupt `V#` base address hundreds of
draws downstream. Its claimed 20–60 µs is forgone and said so. **The programme does not ship a
change whose correctness it cannot check** — which is also the standard §3.5 now holds the census
to, and the census falls short of it.

### 4.2 The self-check, and the gap in the tool that was supposed to run it

`bpv84a`, `bindpack=1 bindpackcheck=1`: **`bp_bad` = 0, sum 0 over 1 952 settled frames, zero
`BindPackVerify` lines anywhere in the log or stdout.** The new D1 check recomputes all three
numbers beside the cached ones, compares **field by field** with a 40-line cap, and names the
disagreeing field; it never fired. Its arming is the emulator's own `Gate: bindpackcheck=1 frame=1`
line plus `guards.py`'s REACHABLE classification — **there is no counter proving the verify path
executed**, which is one rung weaker than a counter and is stated rather than glossed.

**And a defect in `guards.py` that made session 83's self-check runs weaker than they read.**
`classify_alert` only records a line whose label is in `SELF_CHECKS`, and `SELF_CHECKS` had **no
`BindPackVerify` row** and `COUNTER_GATE` **no `bp_bad`**. A `BindPackVerify: MISMATCH` line passed
the generic `MISMATCH` regex and was then **discarded from both the fatal and the self-check
tables**. Session 83 ran `bpv83a`/`bpv83b` believing check 2 covered them; it did not.
`bda_bit_bad` was missing the same way. Both rows are added, and check 2 now reports `bp_bad` as
REACHABLE and zero. Beside it, `verifiers_enabled` scanned the env and the arm texts but **not the
gate file**, so a single-arm self-check run printed *"no `*_VERIFY` / `*check` gate was enabled"*
one line under its own correct classification. Both repaired.

### 4.3 `bpk84a` — VALID on every pre-registered criterion

| criterion | reading | |
|---|---|---|
| 1. check 2 / check 10 | 0 MISMATCH lines; binary confirmed, 260 `GateArm` blocks, arm0 ×130 arm1 ×130 | PASS |
| 2. arming inside the run | §4.4 | PASS |
| 3. area split < 1.0 % | **−0.583 %** | PASS |
| 3. pair match ≥ 90 % | **93.6 % (117/125)** | PASS |
| 3. work within 0.5 % | **+0.004 %** | PASS |
| 4. whole-arm vs paired gap < 0.05 pp | −0.828 % vs −0.825 %, **+0.003 pp** | PASS |
| 5. `da_take_us` | **313.9 → 313.9 ns, +0.010 %** | reported |
| 6. everything on the matched-pair population | **PARTIAL** — see below | reported |

**Criterion 6 is PARTIAL and saying PASS was wrong.** `pred/01` §6 names `endpoint84.py`'s
estimator as primary, and that estimator runs on **125 adjacent opposite-arm block pairs**, which
are not the **117** area-matched ones. The pre-registration is itself inconsistent here (§5 asks
for matched pairs, §6 names the unmatched estimator), and the verdict is identical either way —
−251.7 on 125 block pairs, −245.1 on the 117 matched pairs — but the criterion as written is not
met by the number that decided, and that is recorded rather than rounded away.

Check 6 (cores) FAILs — 6 of 50 groups off by more than 10 % — and is not an admission criterion;
it FAILed in 13 of session 81's 20 block runs.

### 4.4 Arming [M] — all four items, which session 83 could not do

| counter | item | arm `bindpack=0` | arm `bindpack=1` |
|---|---|---:|---:|
| `tnull_hit` | A | **0.000** | 1 481 |
| `tnull_miss` | A | 1 468.5 | **0.000** |
| `bp_mask` | B | **0.000** | 9 542 |
| `bp_local_make` | C | 5 447 | **0.000** |
| `bp_local_skip` | C | **0.000** | 5 478 |
| `bp_dsc` | D | **0.000** | 5 478 |
| `bp_bad` | B, D | 0 | 0 |

**Item C had no arming counter in session 83.** `bp_local_make`/`bp_local_skip` repair it as **one
`Add` in each arm** — deliberately symmetric, so proving the arming costs the same on both sides
and cannot bias the contrast in either direction.

**The tail**, which `pred/01` §4 requires and the first draft omitted: the off-arm counters are
non-zero on **0.64–1.60 %** of frames, all at block boundaries, with the worst single frame at
**1.82 %** of the armed median (`tnull_hit`, one frame) and **0.005–0.02 %** of the armed value in
aggregate. `bp_bad` has no tail: it is 0 in every frame of every run.

`bp_dsc` **5 478** against `draws + dispatches` **5 520** = **−0.76 %**, inside the pre-registered
2 % (P2 HIT). The shortfall is **not** between `PrepareBindings` and `CommitBindings`, as the first
draft said: `bp_local_skip`, counted at the top of the draw path, already reads the same 5 478
(window sums 19 757 460 against 19 757 469, 0.00005 % apart). The draws are lost earlier.

**The null-T# population identity, corrected [M].** `tnull_hit + tnull_miss` reads **+0.85 % on
medians** and **+0.037 % on means** between the arms; per-draw on sums, +0.032 %. `draws`
themselves differ by +0.61 % on medians and **+0.004 % on means** — and criterion 3 admits the run
on the mean. **On every additive statistic the identity is an order of magnitude inside
`pred/01`'s 0.5 % band, so P4 is a HIT**; the first draft scored it a MISS by reading the arming
criterion on medians and the admission criterion on means in the same section.

### 4.5 The effect, and the decision

| statistic | population | value |
|---|---|---:|
| **`cpu_net_us`, the pre-registered primary endpoint, in µs** (`endpoint84.py`) | 125 adjacent block pairs | **−251.7 ± 82.8 (2·SE), t = −6.08** |
| `cpu_gpu_us` (`arms.py`; the label `cpu_net_us` was wrong — it does not fetch `spin_gpu_us`) | 117 area-matched pairs | **−245.1 ± 85.5** |
| …true `cpu_net_us` on the same 117 pairs | 117 matched pairs | −245.2 ± 85.4 |
| `cpu/draw` (`area_verdict.py`) | 117 matched pairs | **−0.817 % ± 0.140 %, t = −11.70** |
| `cpu/draw` (`summary4.py`) | 130 cycles, n ≥ 1800 | −0.825 % ± 0.132 %, t = −12.50 |
| `cpu_gpu_us` as a percentage (`summary4`, printed as `cpu_net_us` — see §7.7) | 130 cycles | −0.764 % ± 0.246 % |
| `gpu_busy_us` | 117 matched pairs | +0.138 % ± 0.177 %, t = +1.55, **inside its own noise** |
| `gpu_busy_us` | 130 cycles (`summary4`) | +0.069 % ± 0.212 % |
| `dt_us` | 117 matched pairs | −0.721 % — **inside the vblank plateau, and not an endpoint** |

`pred/01_bindpack4.md` §6, fixed before the number existed:

> `cpu_net_us` effect **≤ −150 µs** with a 2·SE that excludes zero → **SHIP**.

**Measured −251.7 ± 82.8 µs**, interval [−334.5, −168.9]. The interval excludes zero and the effect
clears the bar by 100 µs. The two µs estimators agree to **6.6 µs**; the percentage form (−0.764 %
of arm 0's 31 130.8 µs = −237.8 µs) sits **5.5 %** from the deciding estimator and 3.0 % from the
matched-pair one — against session 83, where the same two forms disagreed by **26 %**. **The bar
was not moved**: −150 µs is the number session 83 wrote for the three-item package, kept unchanged
because it answers *"is a default change worth making"*, which does not depend on how many items
the package contains.

→ **`bindpack` default 0 → 1. SHIPPED.**

**Prediction P6 — "`E` between −600 and −150 µs, i.e. the package SHIPS" — HIT, and it was the
discriminating one**, written to be able to lose. Session 83's discriminating prediction was its
mirror image and also held.

### 4.6 What this session does NOT claim about the package

* **Not that item D is worth −251.7 − (−137.9) = −114 µs.** Different binaries; sessions 72 and 80
  ruled out inter-run comparison of `cpu_gpu_us`. `bpk84a` measures the **four-item package against
  nothing**, on this binary, in this run. One gate, one number, no attribution.
* Nothing about `mh_bind_us` or `mh_emit_us`: `mutsite` is 0 in `gates_base.txt`, so every `mh_*`
  reads 0 in every run of this session. **Prediction P7 is NOT EVALUATED**, as the pre-registration
  said it would be if `mutsite` was off.
* Any FPS number inside the vblank plateau — including this effect, which is an order of magnitude
  inside it.

### 4.7 The video pass

`bpc84a`, `bindpack=1`, 180 s held, recorder on: **5 986 recorded presents at 960x540, index
entries 5 986, and `s20_vidglitch.py` reports ONE-FRAME GLITCHES: 0** over 100 one-second buckets.
`bp_bad` reads **0** across 3 876 settled frames here too.

**Correcting the first draft's description of the metric:** the per-second maximum inter-frame
difference is 4.6–5.3 only from about second 22 onward; over the whole recording it runs **0.00 to
60.62, with 15 buckets above 6.0**, all of them in the first 22 seconds, which is the level load
and the camera settling. Restricted to the settled window the range is 4.64–5.33 with 64 of 65
buckets inside [4.6, 5.3]. The load-bearing number — **0 one-frame glitches** — is unaffected.
**This is not a pixel-for-pixel comparison**; none has ever been made in this programme.

## 5. WHAT `PrepareBda` COSTS — the session-82 debt, closed, and the answer is a FIXED cost

Gate `bdalap` rode in **both** arms of `slp84b`, so this is a within-arm reading with no contrast
claimed. Medians, identical in both arms [M]:

| counter | per frame | |
|---|---:|---|
| `bda_lap_n` | **179** | and `bda_n` **179** |
| `bda_probe_us` | **2** | entry through the three-epoch comparison, paid by **every** call |
| `bda_scan_us` | **2 232.5** | the `ForEach` walk, reached only by a miss |
| `bda_hit` | 158 | the three-epoch cache, 88.3 % of calls |

**Arming, on sums rather than medians, which is the stronger form:** over the settled window
`bda_lap_n` totals **1 442 819** against `bda_n` **1 442 819** — **exactly equal**. Per frame they
differ on 73 of 8 026 frames by −19…+19, because `BdaLaps` is added mid-function while
`BdaPrepares` is added by the `Scope` destructor, so a flip between the two splits one call.

**The probe is resolution-limited and is reported as a bound, not a point.** The printer truncates
(`dus()` divides by 1000), so a printed 2 means [2 000, 3 000) ns for the whole frame. On the arm
totals: **20 888 µs printed over 1 442 819 calls = 14.5 ns**, and with the truncation the true
value is **< 20.1 ns a call**. `PrepareBda`'s early return — `shared_lock`, two epoch loads, a
compare — costs under **0.021 µs**.

**And the scan is a FIXED cost, not a per-miss one.** This is the finding, and the first draft got
it wrong by dividing a total by a count:

| | |
|---|---:|
| misses per frame, **median** | **24.0** |
| misses per frame, **mean** | 21.22 |
| `median(bda_n) − median(bda_hit)`, which the first draft used | 21 |
| `bda_scan_us` / misses, ratio of **sums** | **104.89 µs** |
| median `bda_scan_us` / median misses | 93.02 µs |
| **OLS over 8 026 frames: `bda_scan_us` = 1 875.1 + 16.53 × misses**, r = +0.46 | |

A 4× change in the miss count buys about a 1.3× change in the time. **~1.88 ms a frame is paid by
whichever call scans first, regardless of how many follow, and a marginal miss costs ~16.5 µs.**
`PrepareBda` costs **2 234.5 µs a frame** and essentially all of it is the scan — but the lever is
not "make fewer calls miss", it is "make the first scan of the frame cheaper".

Three corrections to the record follow [M]:

1. **`FACTS` s83 §6 named "a `Lap` inside `PrepareBda`" as the next step. That would not have
   worked.** `FrameStats::Lap` takes its timestamp under `TimingsEnabled()`, **false** under
   `KYTY_FRAME_TRACE=lite`, exactly like the `Scope` it would have replaced. The instrument used is
   the `plkstat` idiom — a timestamp under `Enabled()`, differenced by hand — **the only shape in
   this tree that reads in a measurement run**. The tree already documents the trap in the
   `HoldLap` comment and it was still about to be walked into.
2. **The 2 181 µs of `bind78a` was not materially inflated by its own nested instrumentation.**
   `FACTS` s83 §3 raised that as the reason the number could not be trusted; the lite measurement
   reads **2 234.5 µs**, within 2.5 %. The figure stands.
3. **The unattributed residual is now bounded from both sides, and it is the fixed part.** Session
   83 bounded the `std::map` descents at ≤ 0.35 ms; the OLS intercept alone is **1.88 ms**. What
   costs that much before the per-range work begins is **[NM]**, and it is the named next
   measurement. `bda_scan_us` also contains `InvalidateBdaRegionStamps()`.

**Prediction C9 — "`bda_probe_us` > `bda_scan_us`" — is a MISS.** The reasoning behind it was wrong
in a way worth recording: 88 % of the calls take the early return, so the *population* is
overwhelmingly probes, and it was tempting to read that as the cost being overwhelmingly probes.
**A population that is 88 % cheap can still be 99.9 % expensive by time.** That is session 82's "a
population is not a saving", pointed the other way. It is **not** a discriminating prediction —
`pred/02` §7 gives that designation to C3 and C6 — and calling it decisive in the first draft was
an overclaim.

## 6. `acc84a` — the shipped binary, and what it is not

After the default flip and the rebuild, one 200 s run on shipped defaults, **no gate file entry for
`bindpack` at all**. Medians over 4 411 settled frames, binary `f0e2ddf4…` confirmed by check 10
[M]:

    bp_dsc 5 483   bp_local_skip 5 483   bp_local_make 0   bp_mask 9 552
    tnull_hit 1 475   tnull_miss 0   bp_bad 0 (max 0, sum 0)
    sl_img_n 0   bda_lap_n 0        (slotstat and bdalap correctly still 0 by default)

**That is the arm-1 signature produced by the compiled default alone**, and it is the only evidence
in the session that the *ship itself* took effect — `bpk84a` only proves the gate works when a
schedule assigns it.

**Three things `acc84a` is not**, all of which the first draft should have said instead of omitting
the run entirely: it is **covered by no pre-registration** and named in no plan, it is **not
area-validated** (no `area_acc84a.csv` was built), and **its frame time is not comparable to
`acc82a`'s** — different binary, and sessions 72 and 80 closed inter-run comparison of
`cpu_gpu_us`. No number of it is used for anything but the arming above.

## 7. CORRECTIONS TO THE RECORD

1. **`PLAN_82_bind.md`'s line numbers are stale**, and two of its anchors point at live, unrelated
   code. Against the tree as this session found it the drift was +118 (item 0) and +141 (item 11);
   **against the tree as this session leaves it, item 11's anchors are +298 and +327**, because
   `NoteSlotStat` and `VerifyDescSetCounts` added ~150 lines above them. Anchor on verbatim text.
2. **`PrepareBda`'s two call sites are `descriptors.cpp:1791` and `renderCompute.cpp:795`**, not
   `:1650` and `:780` as `FACTS` s83 §5.6 says. `:795` is this session's own value — the call moved
   4 lines when the item-9 arming pair went in.
3. **`guards.py` could not see `BindPackVerify: MISMATCH` at all**, and `verifiers_enabled` ignored
   the gate file (§4.2). Both repaired.
4. **The one-argument `RenderExecutor::PrepareBindings` overload is dead** — declared at
   `render.h:315`, defined at `descriptors.cpp:1392`, no caller in the tree.
5. **The s84 port's diagnostic fired and was read.** Rewriting `C:/kyty/s83` → `C:/kyty/s84` inside
   the `--roots` defaults of `arms.py`, `baseline.py` and `effect.py` turned the head of the chain
   into `s84` and **dropped `s83`** — the identical failure the s81→s82 port made, unread for a
   whole session. The port asserts the chain and exits 1. `area_verdict.py` also carried a
   five-root gap (s83…s78) since session 77.
6. **`gates_base.txt` is deliberately stale and stays so**, but not for the reason the first draft
   gave. `gen_gates.py --check` regenerates 1 192 bytes / 108 names against the pinned 1 092 / 99;
   the nine absent names are `bindkey`, `bdabits`, `bdabitscheck`, `bindpack`, `bindpackcheck`,
   `plkstat`, `slotstat`, `bdalap` and the knob `mutwide`. **Eight of the nine have a compiled
   fallback of 0; `bindpack`'s is now `true`**, by this session's ship. Nothing is masked either
   way — the file *pins* nothing it omits, so an omitted name inherits its compiled default, which
   is exactly what a shipped default wants. Session 82 faced the mirror image (the file **pinning**
   `dapin=1` over a newly shipped 3) and had to change and re-hash it; this is the benign case, and
   it is benign by the structure of the file rather than by luck.
7. **`summary4.py`'s `cpu_net_us` was identically `cpu_gpu_us`** in every lite run: it parses only
   lines starting `FrameTrace:`, `spin_gpu_us` lives on `FrameTrace-draw`, and `or 0` substituted
   zero — **the exact trap session 83 catalogued, still live in the tool a session later**.
   Numerically immaterial (`spin_gpu_us` ~5–40 µs a frame, moving ~0.04 µs between arms), but the
   defect is the silence. The tool now counts the absences and **prints them**. `arms.py` computes
   `cpu_gpu_us` and never fetched `spin_gpu_us` either; both are relabelled in §4.5.
8. **`endpoint84.py`'s pairing loop is safe only because of ABBA.** It appends a pair at every
   adjacent opposite-arm index without skipping, which under a plain alternating A/B schedule would
   put every interior block in two pairs and understate the SE. Under `KYTY_GATE_SCHEDULE_ABBA=1`
   the opposite-arm adjacencies are disjoint by construction, and this was verified on `bpk84a`:
   the 125 pairs use each block at most once. `effect.py` and `area_verdict.py` document the ABBA
   reason; `endpoint84.py` did not, and now says so in its docstring.

## 8. WHAT WAS NOT DONE

* **No `KYTY_GPU_TIME` pair on `dapin`**: its +1.238 % GPU cost, replicated four times, is
  unexplained for a **sixth** session. It is the oldest open number in the record.
* **The census has no value-level self-check.** `PLAN.md` declared one and it was not built. That
  is the single largest hole this session leaves, because §3.5's three limits are exactly what such
  a check would have bounded.
* **Route C's unit price is [NM]**, and §3.6 shows the only per-slot number measured here is 21–30×
  below what route C's own premise assumes. Until that is reconciled, 64.2 % is a ceiling.
* **The ~1.88 ms fixed part of `bda_scan_us` is unattributed** (§5).
* **No `mutsite=1` run**, so no `mh_*` phase moved in any measurement of this session.
* **Whether `PipelineCache::m_mutex` can be split** is [NM]; 5.0 ms a frame of hold (session 83).

## 9. THE SCOREBOARD — all nineteen predictions, scored

`pred/01_bindpack4.md` §7 — ten:

| | prediction | result |
|---|---|---|
| P1 | `bp_bad` = 0 in `bpv84a` | **HIT** (0 over 1 952 frames, 0 log lines) |
| P2 | `bp_dsc` 0 in arm 0, within 2 % of `draws + dispatches` in arm 1 | **HIT** (−0.76 %) |
| P3 | `bp_local_make`/`bp_local_skip` each 0 in the other arm | **HIT** |
| P4 | `tnull_hit + tnull_miss` equal between the arms, ±0.5 % | **HIT** on means (+0.037 %); MISS on medians (+0.85 %) — §4.4 |
| P5 | the effect is negative | **HIT** |
| P6 | `E` between −600 and −150 µs, i.e. the package ships | **HIT** — the discriminating one |
| P7 | `mh_emit_us` falls | **NOT EVALUATED** (`mutsite` = 0, as the pre-registration allowed) |
| P8 | `draws` differ by < 0.5 % | **HIT** on means (+0.004 %); MISS on medians (+0.61 %). The pre-registration does not name the statistic — a defect in it, recorded |
| P9 | `gpu_busy_us` does not move beyond its own 2·SE | **HIT** under both populations |
| P10 | `da_take_us` moves by less than 1 % | **HIT** (+0.010 %) |

`pred/02_slotstat.md` §7 — nine:

| | prediction | result |
|---|---|---|
| C1 | `sl_over` exactly 0 | **HIT** (max 0 over all 10 124 frames) |
| C2 | `sl_img_n` vs `b_texn` and `sl_buf_n` vs `bb_n` within 2 % | **HIT** (+0.02 %, −0.01 %) |
| C3 | `R_img` > 0.60 | **HIT** (87.44 %) — named discriminating, and it discriminated |
| C4 | `sl_img_view` − `sl_img_same` < 5 pp of `sl_img_n` | **HIT** (0.007 pp) |
| C5 | `R_buf` < `R_img` | **HIT** (51.26 < 87.44) |
| C6 | `R_stage` < 0.30 | **HIT** (2.06 %) — but close to unloseable, §3.4 |
| C7 | the instrument's price positive and below +1 500 µs | **HIT** (+272.2) |
| C8 | `sl_buf_ring` between 1 % and 25 % of `sl_buf_n` | **MISS** (34.94 %, and 34.42 % in the void run) |
| C9 | `bda_probe_us` > `bda_scan_us` | **MISS**, and instructively — §5 |

**16 hits, 2 misses, 1 not evaluated, 2 statistic-dependent.** The first draft scored six of the
nineteen and called the wrong one decisive; both misses (C8, C9) were among the thirteen it never
mentioned, and C8 is a miss in the very quantity `R_buf`'s correction rests on.

## 10. THE ARITHMETIC

| | value |
|---|---:|
| shipped baseline before this session (`acc82a`) | 31 642 µs = 31.60 FPS |
| the package this session shipped, within-run | **−251.7 ± 82.8 µs** — no scoreboard movement (vblank plateau) |
| the measured sequential floor `S_hi` (session 83) | 20 838 µs |
| 60 FPS | 16 667 µs |
| **route C's ceiling** | **64.2 % of 109 836 slot-bindings a frame** |
| **route C's unit price** | **[NM] — 2.48 ns measured for touching one, 52.6–73.7 ns assumed by the premise** |

**The floor is still 4.2 ms larger than the whole 60-FPS budget** and nothing here changes that.
What changed is that route C — the last route whose ceiling was unmeasured — has a number, and the
number says two thirds of the descriptor work a frame does is work it did last draw. **What it does
not say is that any of it is recoverable**: the repetition is measured at the end of the bind
phase, the price of the checking is spent inside it, and the only per-slot price anyone has
measured is 21–30× too small to be the one the premise is built on. **The next number is the unit
price, not another population.**
