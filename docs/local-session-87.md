# Session 87 — FACTS

**The single source of truth for session 87.** Everything is marked **[M]** measured (a counter in
a run of this session, or a prior session's run named), **[I]** inferred (read from source and
reasoned), **[NM]** not measured, **[R]** retracted.

## 0. In one sentence

**Both blocks were opened and both answers were the opposite of their names: `bl_res_us` is
86.6 % `ResolveTextureWith` and only 13.4 % `BindImage` (8.49 ns a slot), which by the rule sealed
before the run RE-OPENS route C's image half at 1 107 µs against its own 1 000 µs floor; and the
3 764 µs "resource materialisation" block of `ProgramCache::Get` is 63.1 % the LOOKAHEAD TAKE —
`da_take_us`, 2 337 µs a frame, printed on every `FrameTrace-draw` line this programme has ever
logged — with draw-thread `MaterializeResources` only 16.5 %.** Beside them: the two-pass split the
brief prescribed was **refused on reading** because the comment that licenses it is about a
different reordering and the real coupling is `Image::binding.is_bound`; `AheadNote` costs
**25.04 ns**; the draw-thread price of one materialisation is **2.68 µs**; and the D2 instrument's
own price — the thing session 86's design made unmeasurable — is **+448.5 ± 81.0 µs**.

## 1. The runs

Binary **`84b3fe93304c715866e95d4577720856253fab24c222bf373e2abb37686bdc5c`**, 23 610 368 bytes,
built **once**. Sky Garden (`-lvl underwater_aerial_garden`), settled window **n ≥ 2100**,
`KYTY_FRAME_TRACE=lite`, `KYTY_GATE_SCHEDULE_ABBA=1`, period `30+1800`.

| tag | what | pre-registration | verdict |
|---|---|---|---|
| `spv87a` | one arm, all five gates on, 120 s | `pred/01` §6, `pred/02` §6 | **SCOUTING — identities held, no contrast exists**, §2.1 |
| `bal87a` | ABBA `bindalt=0\|1`, `bindlap proglap plkstat mutsite` in **both** arms, 300 s | `pred/01` | **VALID** — §3, §5 |
| `pgl87a` | ABBA `proglap=0\|1`, `bindlap plkstat mutsite bindalt=0` in both arms, 300 s | `pred/02` | **VALID** — §5.4, §6 |

**Four emulator launches.** The warm-up of `spv87a` hit the historical `GpuHangAbort role=4` — the
first entry after a fresh build, the rule of sessions 54/61/85 — and was not counted; **every
counted entry succeeded on the first attempt, in 14.8–25.3 s.**

## 2. WHAT WAS REFUSED ON READING, BEFORE A LINE WAS WRITTEN

### 2.1 The two-pass split the brief prescribed is not behaviour-preserving [I]

`docs/next-session-87.md` §3.1 asks for the image loop of `PrepareBindings`
(`descriptors.cpp:1513-1526`) to be split into two passes over `prepared.images`, and cites the
tree's own comment at `descriptors.cpp:1515-1517`: *"`BindImage` does not look at `prepared.images`,
so running it after the insertion changes nothing."* **The brief also says to verify that comment
against the source. It was verified, and it does not license what it was asked to license.**

The comment is **true**, and it is about session 57's B2a — moving `BindImage` after the
`emplace_back` **of the same iteration**. A two-pass split moves it past **other iterations'**
`ResolveTextureWith`, and the coupling that breaks is not `prepared.images` at all:

| hazard | where | what breaks |
|---|---|---|
| `is_bound` ordering | `textureCache.cpp:1226`, reached from `ResolveTextureWith` by the memo hit (`descriptors.cpp:882`) and by `FindImage` (`textureCache.cpp:2108`) | `if (image.binding.is_bound && first > image.source_first_level) return;` — **and the line above it is the comment *"Several bindings in one draw may expose different LOD ranges of the same image"*, i.e. that guard IS the contract.** Deferred, the guard does not fire and `source_first_level` / `source_size` are rewritten, calling `UntrackImage` and clearing `pending_levels` |
| `needs_rebind` arming | `textureCache.cpp:952` (`ResolveDepthOverlap`), `:1064` (`ResolveOverlap`), `:1083` (`ExpandImage`) | each arms `needs_rebind` **only if `is_bound`**; deferred, the flag is silently not set, and `needs_rebind` is what `RebindImages`, `texfast` eligibility, `FindTexture` and `ShadowProbe` consume |
| use-after-free | `FindImage` frees at `textureCache.cpp:980, 1016, 1068, 1072, 1095, 2078`; `BindImage` indexes at `slotVector.h:40-43` | pass 1 can free an id an earlier slot resolved; pass 2's `BindImage` then indexes a dead slot, and `EXIT_IF` **compiles to nothing in Release** |

The population is not hypothetical: session 86 measured `sl_img_dup` = **31.12 %** of image slots
repeating an image **within their own stage**.

**This is the third session in three in which a plan item did not survive the source** — session 85
refused three of `PLAN_82_bind.md`'s four, session 86 refused the push-constant sub-range, and this
one refuses the two-pass split. It was refused **before** it was built, and no number of this
session comes from it.

### 2.2 58 % of the block §3.2 calls "never looked at" was already printed in every log [M]

`DrawAheadTakeNs` brackets `AheadTake` at `pipelineCache.cpp:3048-3055` under
`FrameStats::Enabled()` — **not** `TimingsEnabled()` — so it reads under `lite`, it is printed on
`FrameTrace-draw` as `da_take_us`, and **it is admission criterion 5 of every run of this
programme.** Read out of `C:/kyty/s86/log_drm86a.txt` before this session built anything:
**2 191.6 µs a frame against `pg_get_us` 3 817.1 and `pg_key_us` 252.6** — **61.5 % of the block
session 86 could only measure as a residual.**

**The fifth session in five in which the number asked for was already on disk.** It cost no run.

### 2.3 `ProgMaterializeNs` is not `MaterializeResources` [I]

It is marked twice — `pipelineCache.cpp:3086` and `:3124` — and **both marks charge everything
since `ProgKeyNs`**: the memo write-back, the locals, `AheadNote`, `AheadTake`, the SRT memo and
`MaterializeResources`. It is also a `FrameStats::Lap`, so it reads exactly 0 in every `lite` run.
**The name has been misleading in this tree since it was written, exactly as `mh_prog` was until
session 86**, and §5 is the division it never was.

### 2.4 The `dause` ABBA the brief suggests would certainly have gone VOID, and it was refused before the run [I]

`dause` flips one boolean and leaves every population identical — on paper the cleanest source of
variation in the file. But `da_hit` = **8 179.5 a frame of `pg_get_n` 8 421.1 = 97.1 %**, and the
worker-side price of one materialisation is `da_work_us / da_req` = 25 172 / 7 536 = **3.34 µs**
(`drm86a`). An arm with `dause=0` moves ~8 200 materialisations onto the draw thread under the
lock — tens of milliseconds a frame, three vblanks instead of two, a collapsed DRS ladder.
**`pred/02` §3 recorded this before the run.** And it was not needed: 249 stages a frame already
miss the lookahead, so the same unit price is available within-arm — §5.3.

## 3. §3.1 — `bl_res_us` DIVIDED [M], `bal87a`

### 3.1 `bal87a` — VALID on every pre-registered criterion

| criterion (session 81 §1, carried unchanged) | reading | |
|---|---|---|
| 1. `guards.py --first-frame 2100` check 2 | 0 MISMATCH lines; 2/16 counters reachable and zero, 14/16 unreachable (gate off) | PASS |
| 1. …check 10 | binary confirmed, 264 `GateArm` blocks, arm0 ×132 arm1 ×132 | PASS |
| 2. arming by a counter inside the run | §3.2 | PASS |
| 3. area split < 1.0 % | **+0.001 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (126/126)** | PASS |
| 3. work within 0.5 % | **+0.044 %** | PASS |
| 4. `summary4` whole-arm vs paired gap < 0.05 pp | +1.191 % vs +1.193 %, **+0.002 pp** | PASS |
| 5. bracketing timer `da_take_us` | **271.26 → 271.51 ns a take, +0.09 %** | reported |
| 6. everything on matched pairs | 126 of 126; the endpoint on 127 block pairs | PASS |

Check 6 (cores) FAILs, as it does routinely, and is not an admission criterion. Check 3b PASSed.

### 3.2 Arming, proved inside the run [M]

**All thirteen new counters read exactly 0 — median AND maximum — over the 1 100 settled frames
BEFORE the first `GateArm:` line**, where the gate file applies and `bindalt` / the new `pg_*` keep
their compiled fallback of 0 because `gates_base.txt` does not name them. In the `bindalt=0` arm
every `bl_rsv*` reads **0.000 median**; on sums the off-arm residual is **1.79–1.86 %** of the armed
value — **not "exactly 0", which `pred/01` §6 wrote down as a statistic before the run rather than
discovering afterwards.** In `pgl87a` the same straddle is **1.60–1.63 %**, and **100 % of the
non-zero off-arm frames sit at distance 0 from a block start, without exception** — session 86's
finding, reproduced by an independent instrument.

### 3.3 THE SPLIT [M] — `bal87a`, sums over 3 782 + 3 811 settled frames

| | ns a slot | share |
|---|---:|---:|
| `P_res_OFF` = `bl_res_us` / `bl_res_n`, arm `bindalt=0` | **63.24** | 1.0000 |
| **`P_rsv` — `ResolveTextureWith` and the loop** | **54.75** | **0.8658** |
| **`P_bind` — `BindImage`** | **8.49** | **0.1342** |
| `T` — the instrument's own price a slot | 7.40 | — |

Coverage `(bl_rsv_n + bl_rsv0_n) / bl_res_n` = **0.5000**, exactly as the alternating phase
constructs it. **No frame of 7 593 has the sampled parts exceeding `bl_res_us`, and none has the
sampled count exceeding `bl_res_n`.** Ratios of medians agree with ratios of sums to 2 %
(62.69 / 70.19 / 61.52 ns) and decide nothing.

**The instrument reproduces what it did not touch:** `bl_img_us / bl_img_n` = **21.89 ns in both
arms** against session 86's 22.30 (−1.8 %); `bl_res_n` differs between arms by **+0.133 %**;
`mh_prog_us` is **6 115.7 against 6 117.3** (+0.03 %) — `bindalt` does not reach the program phase.

**The over-identification that is real, and the one that is not.** `pred/01` §4 named
`P_rsv_raw − T` as a check on `P_rsv`; it is **an algebraic identity, not a test** — substituting
the definitions gives `P_rsv_raw − T ≡ P_rsv` for any inputs, and the run printed |diff| = 0.00 ns
because it could not print anything else. **Prediction A8 is scored NOT EVALUABLE and the defect is
mine**, the third such in two sessions. The check that *is* independent was not pre-registered and
is reported as such: **`T × bl_res_n` = 7.40 ns × 47 727 = 353.2 µs a frame**, against
**`mh_bind_us` moving 10 453.9 → 10 793.0 = +339.1 µs** — two unrelated readings of the instrument's
cost agreeing to **+4.2 %**, inside the endpoint's **+434.8 ± 123.4 µs**.

### 3.4 THE VERDICT, by the rule fixed in `pred/01` §7 before the run

    ceiling87 = sl_img_dupv x (19.66 ns + P_rsv) = 14 875.5 x (19.66 + 54.75) = 1 106.9 us a frame
    RE-OPEN at >= 1 000      MARGINAL at 300..1 000      CLOSED FOR GOOD below 300

→ **1 106.9 µs. ROUTE C'S IMAGE HALF IS RE-OPENED**, against a session-86 verdict of 292.5 µs
computed on 19.66 ns alone. **The margin is 10.7 %, and it is said out loud.**

**The verdict is robust to which reading of `P_res` is used**, which matters because `P_res` is not
stable between runs to better than ~5 %: `bal87a` arm 0 gives 63.24 ns, `pgl87a` gives 66.48 /
66.39 ns in its two arms (agreeing to 0.14 % — so **`proglap` does not contaminate the D3
quantity**), and `drm86a` gave 65.25 ns. Substituting each in turn:

| `P_res_OFF` | `P_rsv` = `P_res_OFF − 8.49` | `ceiling87` |
|---:|---:|---:|
| 63.24 (`bal87a`, the deciding run) | 54.75 | **1 107 µs** |
| 65.25 (`drm86a`, session 86) | 56.76 | 1 137 µs |
| 66.40 (`pgl87a`) | 57.91 | 1 154 µs |

**All three clear 1 000 µs.** What moves between runs is `P_res`; `P_bind` is a within-run
difference of two arms of the same run and does not.

### 3.5 AND WHAT THE RE-OPENING IS AND IS NOT

**`ceiling87` is an UPPER bound and `pred/01` §5 and §9 said so before the number existed.**
Three things sit between 1 107 µs and a saving, and none of them is measured:

* **the witness share of `P_rsv` is [NM].** A per-stage amortisation must still reproduce whatever
  proves the earlier slot's resolution is still valid — the memo key hash, the liveness re-check,
  `TextureSourceSettled` — which is the argument `FACTS` s85 §12.5 made for the 19.66 ns and which
  this session does not get to re-argue.
* **`P_rsv` is "everything from the end of the previous `BindImage` to the end of this slot's
  `ResolveTextureWith`"** — the resolve **plus** the loop's increment, bound check and lambda setup.
  That bracket was fixed in `pred/01` §5 before the run.
* **`sl_img_dupv` = 14 875.5 comes from `drm86a`, not from this session's runs** (`slotstat` was off
  in both). It is a prior measurement, quoted as one.

**What does follow, and it is the useful half:** `BindImage` — the blocker session 85 named and
session 86 located inside the newly measured term — is **8.49 ns of 63.24, i.e. 13.4 %.** The
blocker is real and it is small. Session 86's corrected image ceiling of **3 454 µs** over the
40 674.7 repeating slots of `sl_img_same_sh` therefore splits as **345 µs that provably cannot be
skipped and 3 026 µs that is not blocked by `BindImage`** — which does **not** re-open *that*
population, because its blockers are the witness and `image.Transit`'s pre-state dependency, not
`BindImage`.

## 4. §3.2 — THE BLOCK DIVIDED, AND ITS NAME WAS WRONG [M]

`bal87a` (both arms carry `proglap=1` and agree to 0.1 % on every figure; arm 1 quoted), replicated
by `pgl87a` arm 1.

| | µs a frame | share of the block | `bal87a` | `pgl87a` |
|---|---:|---:|---:|---:|
| `pg_get_us` — `ProgramCache::Get`, slot < 2 | **4 295.8** | — | 4 295.8 | 4 252.9 |
| `pg_key_us` — the key build + `programs.find` | 246.4 | — | 246.4 | 262.3 |
| **the block session 86 called "resource materialisation"** | **4 049.4** | **1.0000** | 4 049.4 | 3 990.6 |
| `pg_loc_us` — locals + `prog_memo` write-back | 95.0 | 0.0235 | 0.0235 | 0.0258 |
| **`pg_ahead_us` — `AheadNote` + `AheadTake` + `AheadCheck`** | **2 557.3** | **0.6315** | 0.6315 | 0.6145 |
| `pg_memo_us` — the SRT memo, **empty body** (`srtmemo=0`) | 72.2 | 0.0178 | 0.0178 | 0.0185 |
| **`pg_mat_us` — `MaterializeResources`, DRAW THREAD** | **666.9** | **0.1647** | 0.1647 | 0.1735 |
| `pg_pm_us` — the permutation `find_if` + `MemoStore` | 461.9 | 0.1141 | 0.1141 | 0.1182 |
| remainder, **derived** — the marks themselves | 196.2 | 0.0484 | 0.0484 | 0.0495 |

**By the routing rule of `pred/02` §7, applied mechanically: `pg_ahead_us / M` = 0.6315 ≥ 0.50 ⇒
THE BLOCK IS THE LOOKAHEAD TAKE, NOT RESOURCE MATERIALISATION.** The rule was sealed before the
run and both runs return the same verdict.

### 4.1 The identity that makes the chain trustworthy [M]

`da_take_us` is an **independent, already-shipped, lite-visible** timer of `AheadTake`, which sits
**inside** `pg_ahead_us`. Over **7 593 settled frames of `bal87a`, where `proglap` rides both arms,
not one frame has `pg_ahead_us < da_take_us`** — and `pg_ahead_us / da_take_us` = **1.0931** on
sums, against a pre-registered ceiling of 1.60. In `pgl87a`, 61 frames do violate it; **all 61 sit
at distance 0 from a block start**, i.e. they are the schedule straddle of the arm where `proglap`
is off, and they are named rather than smoothed.

**`AheadNote` = `(pg_ahead_us − da_take_us) / pg_ahead_n` = 25.04 ns** (`bal87a`), **25.34 ns**
(`pgl87a`) — 8.6 % of the lookahead phase, and the first time it has been priced.

### 4.2 The other three phases, priced [M]

| | value | what it says |
|---|---:|---|
| `pg_pm_us / pg_pm_n` | **52.10 ns** | the permutation `find_if` examines 1.06 candidates and costs 52 ns — 462 µs a frame, and it is **not** the `std::deque` scan session 86 closed, it is the `PushData::StartFor` arithmetic and the `specialization ==` compare |
| `pg_loc_us / pg_get_n` | **10.71 ns** | the `ResourceSnapshot` / `ResourceSpecialization` locals are cheap; `snapkeep` is doing its job |
| `pg_memo_us / pg_get_n` | **7.90 ns** | **the SRT memo phase is EMPTY (`pg_memo_n` = 0.000 a frame, `srtmemo=0`) and still costs 72 µs a frame** — the `memo_enabled` test, the `SrtReadLog memo_log` construction and the mark. **Prediction B8 predicted < 20 µs and is a MISS**, §7 |

### 4.3 The draw-thread price of one materialisation [M], and the population it is not

**`P_mat` = `pg_mat_us / pg_mat_n` = 2.676 µs** (`bal87a`) / **2.759 µs** (`pgl87a`) over
**249.1 calls a frame**, against the worker-side `da_work_us / da_req` = 3.34 µs.

`pg_mat_n` = 249.1 against `pg_get_n − da_hit` = 9 144.8 − 8 899.5 = 245.3 in `spv87a`: the bound
`pred/02` §6 stated holds and is tight.

**`P_mat × da_hit` = 23 053 µs a frame** — *what the shipped `drawahead` default is worth to the
draw thread, priced on the miss population*. **It is not a saving and not a new finding**:
`drawahead` shipped in session 54, and **`pred/02` §5 and §9 recorded before the run that the miss
population is self-selected and its price differs from the 97 % it hits by an amount that is
[NM]** — session 86's own trap (91.57 ns against 73.79 ns, 24 % dearer) is the precedent. What it
does establish is the order of magnitude: **the lookahead removes tens of milliseconds a frame from
the draw thread, and the 4 049 µs that remain are what it costs to take and validate the results.**

### 4.4 What the block therefore IS, with a prior measurement named rather than re-measured

Session 72 measured, with the ceiling knob `dawitloop` (**which cannot be shipped**), that inside
`AheadTake` **the clean witness loop costs 1.033 ms, the live loop 0.896 ms, the whole check
1.929 ms** — on a different binary, and **this session did not re-measure it** (`pred/02` §9).
Against `da_take_us` = 2 339.5 µs here, that prior reading would make the M1 witness verification
**~82 % of `AheadTake` and ~48 % of the whole 4 049 µs block.**

**So the largest unsplit block in the record is not work nobody looked at. It is the price of
PROVING that work done on a worker thread is still valid** — structurally the same thing as the
19.66 ns that closed route C at slot granularity. That is the honest reading, and D2's next number
is `dawitloop` re-read **inside the lock on this binary**, not a new mechanism.

## 5. `pgl87a` — the instrument's own price, which session 86's design could not measure

### 5.1 VALID on every pre-registered criterion

Area split **−0.001 %**, pair match **100 % (124/124)**, work **+0.015 %**, `summary4` cross-check
gap **+0.002 pp**, `da_take_us` per take 262.31 → 259.04 ns (**−1.25 %**, reported). Guards checks 2
and 10 PASS; check 3b raised one advisory pass-area difference and the render size held; check 6
(cores) FAILs, as it does routinely.

### 5.2 The price

| statistic | value |
|---|---:|
| **`cpu_net_us`, `proglap=1` against `proglap=0`** | **+448.5 ± 81.0 µs (2·SE), t = +11.08** on 124 pairs |
| `cpu/draw` (`area_verdict.py`, 124 matched pairs) | +1.421 % ± 0.133 %, t = +21.40 |
| `gpu_busy_us` | +0.097 % ± 0.167 %, noise |
| `draws` | +0.159 % on sums |

**Session 86's prediction I1 asked what this instrument costs and was scored NOT EVALUATED because
`PLAN.md` §2 of that session rode it in both arms. It is now measured.** Five extra `NowNs()` over
8 421 calls a frame is 42 105 timestamps; +448.5 µs is **10.7 ns a mark**, against the 7.40 ns a
mark §3.3 measures for `bindalt` — consistent to the extent two different marks in two different
functions can be.

The `bindalt` instrument, measured the same way in `bal87a`: **+434.8 ± 123.4 µs, t = +7.05.**

## 6. WHAT WAS NOT DONE

* **No video pass, and none is owed.** Both gates are compiled default 0 and nothing shipped. With
  them off the two patched functions are behaviourally identical: `bindalt` adds one branch that is
  never taken, and the three hoisted predicates in `ProgramCache::Get` (`pg_ahead_ran`,
  `pg_memo_ran`, `pg_mat_ran`) evaluate the **same** expressions the `if`s did, in the same order,
  with no side effects in any operand. It is not a byte-identical binary and no pixel comparison was
  made; what is claimed is that no shipped default changed, so the `ROADMAP` §6 video debt is not
  incurred — the same argument, and the same limitation, as session 86 §8.
* **No `acc87a`.** No default changed.
* **The witness share of `P_rsv` is [NM]** — §3.5, and it is what stands between 1 107 µs and a
  saving.
* **`dawitloop` was not re-read inside the lock** — §4.4, and that is now D2's next number.
* **`dapin`'s GPU cost was not touched.** The `recordthread=0|1` ABBA session 85 named is still the
  next step, **the seventh session in a row that has not taken it**, and this session says so.
* **D1 was not started.** Its ceiling (~2.1 ms) was already known and it is a rewrite.
* **`sl_img_dupv` was not re-measured** (`slotstat` off in both deciding runs); §3.4 uses
  `drm86a`'s 14 875.5 and names it.

## 7. THE SCOREBOARD — all twenty-nine predictions, scored

`pred/01_bindalt.md` §8 — fourteen, on `bal87a`:

| | prediction | result |
|---|---|---|
| A1 | every `bl_rsv*` 0 median and 0 maximum pre-schedule, 0.000 median in arm 0 | **HIT**; the off-arm sum straddle is 1.79–1.86 %, 100 % at block starts |
| A2 | coverage in 0.40…0.60 | **HIT, and DISCOUNTED** (0.5000) — the alternating phase constructs it |
| A3 | sampled ≤ `bl_res_us` in every frame | **HIT** (0 of 7 593) |
| A4 | `bl_res_n` within 1.5 % between arms | **HIT** (+0.133 %) |
| **A5** | **`T` in 1…12 ns** | **HIT** (7.40) — discriminating |
| **A6** | **`P_bind < P_rsv`** | **HIT** (8.49 < 54.75) — discriminating |
| **A7** | **`P_bind` in 2…30 ns** | **HIT** (8.49) — discriminating |
| A8 | the over-identification `\|(P_rsv_raw − T) − P_rsv\| < 3 ns` | **NOT EVALUABLE — by my own hand.** It is an algebraic identity, not a test; §3.3 |
| A9 | `P_res_OFF` within 10 % of 65.25 ns | **HIT** (63.24, −3.1 %) |
| A10 | `bl_img_us / bl_img_n` within 10 % of 22.30 ns | **HIT** (21.89, −1.8 %) |
| **A11** | **`ceiling87` ≥ 1 000 µs** | **HIT** (1 106.9) — discriminating, and it decides the route, by **10.7 %** |
| A12 | the instrument costs +50…+600 µs | **HIT** (+434.8 ± 123.4) |
| A13 | `gpu_busy_us` inside its own 2·SE | **HIT** (+0.115 % ± 0.167 %) |
| A14 | `da_take_us` per take moves < 2 % | **HIT** (+0.09 %) |

`pred/02_matsplit.md` §8 — fifteen, on `bal87a` (within-arm) and `pgl87a` (contrast):

| | prediction | result |
|---|---|---|
| B1 | every new `pg_*` 0 median and 0 maximum pre-schedule, 0.000 median in the OFF arm | **HIT**; straddle 1.60–1.63 % on sums, 100 % at block starts |
| B2 | parts ≤ `pg_get_us` in every frame | **HIT** (0 of 7 593 and 0 of 7 454) |
| **B3** | **`pg_ahead_us ≥ da_take_us` in every frame; ratio ≤ 1.60** | **HIT** (0 of 7 593 in `bal87a`; 1.0931) — discriminating, two independent timers |
| **B4** | **`pg_ahead_us / M` > 0.50** | **HIT** (0.6315 / 0.6145) — discriminating, and it decides D2 |
| **B5** | **`AheadNote` < 60 ns** | **HIT** (25.04 / 25.34) — discriminating |
| B6 | `pg_mat_n` in 50…1 000 a frame | **HIT** (249.1) |
| **B7** | **`P_mat` in 0.5…8 µs** | **HIT** (2.676 / 2.759) — discriminating |
| B8 | `pg_memo_us` < 20 µs a frame **and** `pg_memo_n` < 1.0 | **MISS** on the first clause (**72.2 µs**), HIT on the second (0.000). §4.2: an **empty** phase costs 7.90 ns a call — the band assumed an empty body costs nothing, and it does not |
| B9 | `pg_pm_us / pg_pm_n` < 300 ns | **HIT** (52.10) |
| B10 | `pg_loc_us / pg_get_n` < 100 ns | **HIT** (10.71) |
| **B11** | **the D2 instrument costs +50…+900 µs** | **HIT** (+448.5 ± 81.0) — discriminating, and it discharges session 86's I1 |
| B12 | `pg_get_us`, `pg_key_us`, `pg_n` within 10 % of `drm86a` | **HIT** (+6.8 %, −3.6 %, +4.6 %) |
| B13 | `pg_cold_n`, `pg_compile_n` each < 1.0 a frame | **HIT** (0.00 in every arm of both runs) |
| B14 | `gpu_busy_us` inside its own 2·SE | **HIT** (+0.097 % ± 0.167 %) |
| B15 | `draws` within 1.5 % on sums | **HIT** (+0.159 %) |

**Across both pre-registrations: 29 predictions, 27 hits, 1 miss (B8), 1 not evaluable (A8).** One
hit (A2) is discounted as constructed. **The one not evaluable is a defect in a prediction I wrote
myself** — the third in two sessions, after session 86's H1 and I1 — and it is recorded rather than
repaired.

## 8. WHAT IS NOT CLOSED, with the next measurement named for each

| debt | next number | since |
|---|---|---|
| **the witness share of `P_rsv`** — it is what stands between `ceiling87` = 1 107 µs and a saving | a counter inside `ResolveTextureWith` separating the memo key hash + liveness re-check from the rest | **87** |
| **`dawitloop` re-read inside the lock on this binary** — §4.4 says the block is the M1 witness check and quotes session 72 rather than re-measuring | one ABBA, `dawitloop=0\|1`, with `proglap=1` in both arms | **87** |
| **`pg_pm_us` = 462 µs a frame at 52 ns a call** — not the deque scan, and not yet attributed | split `PushData::StartFor` from `specialization ==` | **87** |
| **`dapin`'s GPU cost**, +1.961 % ± 0.165 %, five replications | the `recordthread=0\|1` ABBA with `dapin` pinned — **seventh session unclaimed** | 79 |
| **D1 — `BufferCache::UploadCopies`**, 22.8 MiB a frame at 11 GB/s | a rewrite, ceiling ~2.1 ms known | 85 |
| **`PipelineCache::m_mutex`, 4.4 ms a frame of hold** — §4 now says what is inside it | whether `AheadTake` can run outside the lock | 83 |
| route B items 2, 8, 10, 12 and the corrected item 3 | read the source first; every line number in `PLAN_82_bind.md` is stale | 85 |
| the marginal price of a slot (`b_hit`) — OLS degenerate, VIF 60.9 | another source of variation | 85 |

## 9. THE ARITHMETIC

| | value |
|---|---:|
| shipped baseline (`acc82a`, not re-measured since session 82) | 31 642 µs = 31.60 FPS |
| 60 FPS | 16 667 µs |
| the measured sequential floor `S_hi` (session 83) | 20 838 µs |
| **§3.1: `P_rsv` / `P_bind` of the 63.24 ns image slot** | **54.75 ns (86.6 %) / 8.49 ns (13.4 %)** |
| **route C's image half, by the rule sealed before the run** | **1 107 µs ≥ 1 000 ⇒ RE-OPENED, margin 10.7 %, an UPPER bound** |
| **§3.2: the block's largest part** | **`AheadTake` + `AheadNote`, 2 557 µs = 63.1 %** |
| §3.2: draw-thread `MaterializeResources` | 667 µs = 16.5 %, at 2.68 µs a call over 249 calls |
| §3.2: the permutation phase | 462 µs = 11.4 %, at 52.1 ns a call |
| `AheadNote`, priced for the first time | 25.04 ns a call |
| what the shipped `drawahead` is worth to the draw thread | ~23 ms a frame, on the miss population's price — a CEILING, not a saving |
| the D2 instrument (session 86's I1, discharged) | **+448.5 ± 81.0 µs** |
| the D3 instrument | +434.8 ± 123.4 µs |

**The honest statement of the task.** Session 86 said the money was in work rather than
bookkeeping. **Both of this session's divisions say the opposite, and they say it about the same
mechanism.** The 3 125 µs of the bind phase is 87 % *resolution* — which is a memo lookup with a
witness, not work — and the 3 764 µs under the pipeline-cache lock is 63 % *taking and validating
results a worker already computed*, of which a prior session's ceiling knob attributes ~82 % to the
witness loops. **Both of the two largest unopened blocks in this record turn out to be the price of
PROVING that a cached answer is still good.** That is a different programme from "make the work
cheaper", it is the same shape as the 19.66 ns that closed route C at slot granularity, and it is
the first time the record has been able to say it with numbers from both ends.
