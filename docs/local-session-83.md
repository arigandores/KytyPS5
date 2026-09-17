# Session 83 — the sequential floor, measured; route A closed

*This is `C:/kyty/s83/FACTS.md` verbatim, carried into git as the session's report.*
*The harness, the logs and the four pre-registrations live in `C:/kyty/s83`.*

---

# Session 83 — FACTS

**The single source of truth for session 83.** Everything is marked **[M]** measured (a counter in
a run of this session, or a prior session's run named), **[I]** inferred (read from source and
reasoned), **[NM]** not measured, **[R]** retracted.

## 0. In one sentence

**The one number that decided the programme's largest open question was measured, and it closed the
question against us: the sequential floor is 20.8 ms, which is larger than the entire 16.7 ms frame
budget of 60 FPS — so no amount of parallel command recording can reach 60 FPS, at any granularity,
ever**; kill criterion K2 of `DESIGN_82_parallel.md` fires, the goal is restated in `ROADMAP.md`,
and the rest of the session went to the binding path.

## 1. The runs

| tag | binary sha256 | what | verdict |
|---|---|---|---|
| `flr83a` | `05134ccd…` | ABBA `mutwide=0\|15`, 300 s | **VOID** (pair match 65.8 %) |
| `flr83b` | `05134ccd…` | ABBA `mutwide=0\|15`, 300 s | **VALID** — the floor |
| `bpv83a` | `fc92cd24…` | `bindpack=1 bindpackcheck=1`, self-check | **the check FIRED** — §4.2 |
| `bpv83b` | `4588d793…` | the same after the fix | **`bp_bad` = 0** |
| `bpk83a` | `4588d793…` | ABBA `bindpack=0\|1`, 300 s | **VALID, below the ship threshold** |
| `bpc83a` | `4588d793…` | `bindpack=1`, 180 s, recorded | the video pass, **0 glitches** |
| `bpk83b` | `4588d793…` | ABBA `bindpack=0\|1`, 300 s, the sealed pool | **VALID** — §4.7 |
| `plk83a` | `8efb990c…` | A/A `plkstat=1`, 240 s, census | **the `mh_prog` question** |

Sky Garden (`-lvl underwater_aerial_garden`) everywhere, settled window **n ≥ 2100**,
`KYTY_FRAME_TRACE=lite`. Both floor runs entered on the first attempt (15.4 s and 14.8 s); no entry
hang this session.

**`flr83a` is VOID and its arm contrast is quoted nowhere.** Pair match **65.8 % (79/120)** against
the pre-registered ≥ 90 %; area split −0.630 % and work +0.035 % both passed, so the arms rendered
the same size and did the same work — the DRS simply moved inside the run. The criterion was **not
substituted, reweighted or retired**; another run of the same contrast was taken, exactly as
session 82 did with `dap82a`. Its floor readouts agree with `flr83b`'s to **0.3 %**
(`S_raw` 21 037 against 20 973), which is reported as a consistency check and not as a measurement.

## 2. THE SEQUENTIAL FLOOR — measured, and it closes route A

### 2.1 What was built

Knob **`mutwide`** (`KYTY_MUT_WIDE`, default 0, bitmask, limit 15) puts a `FrameStats::MutScope` on
the four surfaces of the render-mutex hold that carried none, so that `a_mut_us` stops being built
from six sites:

| bit | surface | why it is serial | µs/frame (`flr83b` arm 0) |
|---:|---|---|---:|
| 1 | `PrepareDrawRenderState` | `FindRenderTarget`/`FindDepthTarget`, EXCLUSIVE on `TextureCache::m_lock` (`DESIGN` §4) | 805 |
| 2 | `RefreshShaders` | `ProgramCache`/`PipelineCache` maps stay exclusive while the memo holds iterators (`DESIGN` §5.3) | 5 819 |
| 4 | the `DispatchDirect` critical section | no scope of any kind existed | 2 276 |
| 8 | `PrepareBda` | spine-only in any slice-parallel scheme (`DESIGN` §5.4) | — |

`MutScope` gained an optional second argument — the counter that proves the scope armed — with
default `Counter::Count` = none, so the six existing sites are unchanged argument for argument.

### 2.2 Arming, proved inside the run

`a_mut_us` cannot prove arming (it is the measurement) and `a_mut_n` cannot either (the new scopes
enclose some of the six and turn them from outer intervals into inner ones). **`mw_n`** does [M]:

* arm 0: **median 0.000**. 58 of 3600 arm-0 frames of `flr83a` (1.61 %) carry a non-zero value, at
  most **62** = 0.58 % of the armed value, recurring on the ABBA period — a schedule-boundary
  straddle, one flip's Poll against the frame it is attributed to, **not leakage of the knob**. The
  pre-registration said "exactly 0.000"; the median is, the tail is not, and that is recorded here
  rather than smoothed over.
* arm 1: **10 542** against `2 × mh_n + mh_disp_n + bda_n` = **10 568**, i.e. **−0.25 %**, inside
  the pre-registered ±2 %. On `flr83a`, per frame over 3624 frames: median −0.262 %, range
  −1.207 % … −0.038 % — one-sided towards fewer, which is the only licensed direction (a draw that
  returns before the render-state mark constructs no wide scope).

### 2.3 `flr83b` — VALID on every pre-registered criterion

| criterion (session 81 §1, carried unchanged) | reading | |
|---|---|---|
| 1. `guards.py --first-frame 2100` check 2 | 0 MISMATCH lines; 2/11 reachable self-check counters zero | PASS |
| 1. …check 10 | binary confirmed, 249 `GateArm` blocks, every arm text where meant | PASS |
| 2. arming by a counter inside the run | `mw_n` 0 → 10 542, identity to −0.25 % (§2.2) | PASS |
| 3. area split < 1.0 % | **+0.002 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (119/119)** | PASS |
| 3. work within 0.5 % | **+0.054 %** | PASS |
| 4. `summary4` whole-arm vs paired gap < 0.05 pp | +0.366 % vs +0.368 %, **+0.002 pp** | PASS |
| 5. bracketing timer `da_take_us` | **2431 → 2421 µs, −10 µs** | reported |
| 6. everything on matched pairs | yes | PASS |

`guards.py` reads **8 PASS, 1 WARN, 3 SKIP, 0 FAIL** — including check 6 (cores), which FAILs
routinely and did not here. Checks 8 and 9 are SKIP because the recorder was off; check 7 is SKIP
because no `nvidia-smi` sample caught the GPU above 50 %.

### 2.4 The floor [M]

Medians over the settled window, `flr83b`:

| | arm 0 (`mutwide=0`) | arm 1 (`mutwide=15`) | difference |
|---|---:|---:|---:|
| `a_mut_us` | **13 437** | **20 973** | **+7 536** |
| `a_mut_n` | 61 469 | 70 465 | +8 996 |
| `mw_n` | 0 | 10 542 | +10 542 |
| `a_hold_us` | 28 667 | 28 686 | +19 |
| `a_wait_us` | 155 | 156 | +1 |
| `cpu_gpu_us` | 32 421 | 32 443 | +22 |
| `spin_gpu_us` | 5 | 5 | 0 |
| `gpu_busy_us` | 12 519 | 12 494 | −25 |
| `draws` | 5 072 | 5 060 | −12 |

**The instrument's price**, on the 119 matched pairs, which is the population criterion 6 names:
`cpu/draw` **+0.368 % ± 0.134 % (2·SE), t = +5.48**; the pre-registered primary endpoint
`cpu_net_us` = `cpu_gpu_us − spin_gpu_us` **+0.336 % ± 0.262 %**; in microseconds
**P = +135.3 ± 87.7**.

| quantity, as `pred/01_floor.md` §5 defines it | µs/frame |
|---|---:|
| `S_lo` — the six sites of session 68, on this binary and scene | **13 437** |
| `S_raw` — + `mh_rt` + `mh_prog` + `mh_disp` + `PrepareBda` | **20 973** |
| `P` — the whole price of the addition, charged against the number it inflates | **+135.3** |
| **`S_hi` = `S_raw` − `P`** | **20 838** |
| `a_hold_us` — the standing upper bound | 28 686 |

`S_lo` reproduces `amut68a` 13 300 and `amut69a` 14 035.5 on a different binary, which is a sanity
check and is labelled as one.

### 2.5 K2 fires, and the arithmetic is worse than K2

`pred/01_floor.md` §6, fixed before the run: **`S_hi` ≥ 16 000 µs → K2 fires, step A is closed and
the programme's goal is restated.** `S_hi` = **20 838**.

The reading is in fact sharper than the criterion. `DESIGN_82_parallel.md` §1 models
`T_cpu(W) = S + max(f_max, 1/W)·(cpu_total − S)`, so with **any** number of record contexts and
**perfect** balance, `T_cpu → S`. Here

> **S = 20.8 ms against a 60-FPS frame budget of 16.7 ms.**

**The serial part alone does not fit in a 60-FPS frame.** No `W`, no granularity, no lock
decomposition in the design changes that: parallel command recording cannot reach 60 FPS in this
scene, and its best conceivable outcome is `T_cpu` ≈ 20.8 ms, which on the vblank grid is two
vblanks — **30.0 FPS on the scoreboard**, the same number `DESIGN` §0.4 already predicted for every
plausible `S`.

### 2.6 What this number does NOT say — three caveats, all load-bearing

1. **It is the floor at the granularity of four named surfaces** [I]. **MEASURED AND CLOSED in
   §2.7 of this same session: 68.9 % of `mh_prog` runs under `PipelineCache::m_mutex`, held out to
   everyone.** The caveat is kept below as it was written, because it was written before the
   measurement and the measurement went against the session's own prediction. `mh_prog_us`
   (5 850 µs) is
   wrapped **whole**, and `progmemo` reports that **74.8 %** of draws repeat the previous draw's
   register inputs and take the memo, which is a *read*. If `ProgramCache` lookup could be made
   genuinely shared — `DESIGN` §5.3 says it cannot while the memo holds **iterators**, and names
   `SourceEntry*` + a validating key as the precondition — up to ~5.8 ms would leave S and it would
   land near **15 ms**. **That is the only lever in the record that could revive route A**, it is a
   question about locking rather than a measurement, and nothing in `DESIGN` proposes it as a step.
   Even then the design's own condition needs `S ≤ 14 ms` **and** `f_eff ≤ 0.125` simultaneously.
2. **`a_mut_us` is not purely the GuestGpu thread's** [M, source]. `Detail::t_mut_depth` is
   thread-local and `Read()` sums every shard, and `swapchain.cpp:767` → `Impl::ResolveSurface` →
   `TextureCache::FindImage` constructs MutScope site 3/6 **on the present thread**. That is about
   one interval per present against `a_mut_n` 70 465, so it cannot move the conclusion, but
   `a_mut_us` is a process quantity and `a_hold_us` is not.
3. **The instrument is inside the thing it measures.** `P` = +135.3 µs of the +7 536 µs addition is
   the instrument, i.e. **1.8 %**; `S_hi` subtracts all of it, which makes `S_hi` conservative only
   if every microsecond of `P` falls inside a wide interval. Any that does not makes `S_hi` an
   under-estimate, so the true floor is at least this.

### 2.7 THE CAVEAT, MEASURED — and it closes against the session's own prediction

`pred/04_plkstat.md` was sealed before the instrument existed, with the decision rule fixed:
`H` = `pl_prog_hold_us`, `M` = `mh_prog_us`, and **`H/M` ≥ 0.60 → the floor stands as published;
`H/M` ≤ 0.25 → the floor is an over-estimate by up to `M − H`.**

Gate **`plkstat`** (`KYTY_PIPE_LOCK_STAT`, default 0) puts a `FrameStats::LockSplit` — session 68's
`MutexMark` shape, timestamp taken right before the `LockGuard` — on each of the **three**
`PipelineCache::m_mutex` acquisitions of the per-draw and per-dispatch path. **Wait and hold are
never summed**, and the three sites sit in three different containers and are never added together.

`plk83a`, A/A (`plkstat=1 amut=1 mutsite=1 mutwide=15` in both arms), 5 407 settled frames, guards
check 2 and check 10 PASS. Medians [M]:

| site | container | `n` | wait µs | **hold µs** | hold / container |
|---|---|---:|---:|---:|---:|
| `GetGraphicsPrograms` | `mh_prog_us` 5 959 | 5 057 | 42 | **4 108** | **68.9 %** |
| `GetGraphicsPipeline` | `mh_emit_us` 7 598 | 5 057 | 48 | 653 | 8.6 % |
| `GetComputeProgram` | `mh_disp_us` 2 190 | 268 | 2 | 237 | 10.8 % |
| **all three** | `a_hold_us` 28 632 | | 92 | **4 998** | **17.5 %** |

Arming, by identity: `pl_prog_n` **5 057** against `mh_n` **5 077** = **−0.39 %**; `pl_cs_n` **268**
against `dispatches` **268**, exactly. Both inside the pre-registered 2 %.

**`H/M` = 0.689 ≥ 0.60. The floor stands as published, and caveat 1 of §2.6 is closed against
reopening route A.** More than two thirds of `RefreshShaders` is spent holding a single mutex out to
every other thread, so wrapping the phase whole was not an over-estimate of consequence.

**Prediction S3 — `H/M` < 0.50 — is a MISS, and it was the discriminating one.** The reasoning
behind it was wrong in a way worth recording: `progmemo` short-circuits `PrepareProgram`, which is
the work *before* the lock, but **every draw still takes the lock and calls `ProgramCache::Get` once
per stage regardless of the memo**. A memo that saves the expensive preparation does not save the
lock. S1, S2, S4 and S5 hit.

**What this adds beyond the caveat.** One mutex holds out **5.0 ms of a 28.6 ms frame** — 17.5 % —
at a wait of **92 µs**, i.e. essentially uncontended **because exactly one thread takes it today**.
Under N record contexts that 5.0 ms is not parallel work; it is a serialiser, and
`DESIGN_82_parallel.md` §5.3 says it cannot be split while the memo holds **iterators**. Route A is
therefore closed twice over: by `S` = 20.8 ms, and by the largest single component of the part
`mutwide` newly revealed being exclusive lock hold rather than instrument artefact.

**A third independent reading of the floor, for free:** `plk83a` reads `a_mut_us` **20 998** on a
different binary with a different instrument armed, against `flr83b`'s **20 973** — **0.12 %** apart.

**What this run cannot show, as stated before it ran:** that the 31 % of `mh_prog` outside the lock
is *parallelisable*. It shows only that it is not protected by *that* lock. No revision of the K2
verdict follows from it, and none is made.

**The most generous hypothetical the record allows, and it still does not reach the condition.**
Grant, against `DESIGN` §5.3, that the **entire** 4 998 µs of `PipelineCache::m_mutex` hold becomes
parallel. Then `S` = 20 838 − 4 998 = **15 840 µs**. The design's own 60-FPS condition is
**`S ≤ 14 100 µs` AND `f_eff ≤ 0.125` simultaneously** (`DESIGN` §1). 15 840 > 14 100. **Route A is
closed with margin, not by a hair**, and the single largest lever anyone has named does not move it
far enough even when granted in full and for free.

## 3. WHERE `bda_us` GOES — the `std::map` candidate is bounded and small

Session 82 left this open: `bda_us` 2 181 µs a frame across 181 `PrepareBda` calls, **not** the
18 582 region visits (`bdabits` armed to 99.95 % and read −50.8 ± 87.5 µs), with "the `m_buffers`
`std::map` lookups of `SynchronizeBuffersInRange`" named as the next candidate. Four `Add`-style
counters were added — they read under `lite`, unlike `bda_us`, which is a `Scope`. Medians,
`flr83b`, identical in both arms [M]:

| counter | per frame | what it is |
|---|---:|---|
| `bda_n` | **179–180** | `PrepareBda` calls |
| **`bda_hit`** | **158** | …served by the three-epoch cache, **never scanning at all — 87.8 %** |
| `bda_rng` | 288 | `SynchronizeBuffersInRange` calls (≈ 13 mapped ranges per scanning call) |
| `bda_rng_e` | 216 | …of those, **75 % return on two map lookups** with no registered buffer in the mapping |
| `bda_drng` | 1 178 | dirty ranges fed to the upload pass, one `upper_bound` each |
| `bda_scan` | 1 066 | tracking regions actually scanned |
| `bda_skip` | 23 703 | …and skipped |

**The map-lookup population is `288 × 2 + 1 178` ≈ 1 754 red-black descents a frame.** At 100–200 ns
for a scattered descent that is **0.18–0.35 ms**; the unit price is **[NM]** and the population is
not a saving — session 82's own trap — so what this settles is the **ceiling**: the `std::map`
cannot be carrying 2.2 ms unless a descent costs over 1.2 µs, which it does not. **`PLAN_82_bind.md`
item 5's premise is bounded out**, the same way `bdabits` was.

**And a correction to the record:** `bda_us` **reads 0 under `KYTY_FRAME_TRACE=lite`**, so nothing
in this session times the BDA path. The 2 181 µs of `bind78a` was taken with full tracing, where
every nested `Scope` inside `PrepareBda` also charges. **What `PrepareBda` costs in a measurement
run is [NM]**, and the honest next step is a `Lap` inside it, not another estimate from a count.

Two further facts the census gives for free: the three-epoch early return of `PrepareBda`
(`KYTY_BDA_EPOCH_CACHE`) is **alive and carries 87.8 % of the calls** — `DESIGN` step 1a proposed
building exactly that mechanism, and it is already shipped; and `SynchronizeBuffersInRange` spends
**three quarters of its calls** proving a mapping holds no registered buffer at all.

## 4. THE BINDING-PATH PACKAGE — gate `bindpack`: correct, armed, and worth 138 µs against a 150 µs bar

### 4.1 What is in it

`ROADMAP.md` §5 and `PLAN_82_bind.md` §3 both fix in advance that route B ships in packages,
because its items are individually inside the A/A noise floor of ±75…92 µs. Three items, one gate:

| item | `PLAN_82_bind.md` | claimed | what changed |
|---|---|---:|---|
| A — null T# descriptor memo | item 1 | 100–400 µs | ~1 480 resolutions a frame stop building a ~584-byte `ImageDesc` and calling `FindImage` (scheduler, validate, constrain, spin lock, map) for an answer that is a pure function of three fields with at most **nine** values. Both `emit` lambdas take `const ImageDesc&`, so a hit copies nothing. Every hit is re-validated against the live slot — strictly more than `GetNullImage` does. |
| B — one binding-kind scan a stage | item 4 | 80–220 µs | `IR::FindBinding` is an out-of-line linear scan asked **three** questions about the same `BindingLayout` at ~9 500 stages a frame. One pass answers all three. No cache, no pointer key, no invalidation. |
| C — the unread `GraphicsBindings` | item 9 | 20–75 µs | fifteen empty-vector constructors and destructors on the stack of every draw, never read while `ReuseBindingsEnabled()` is on. Same in the dispatch path. |

Item 7 (`IsGpuThread` as a cross-TU call) was **excluded**: inlining cannot be switched inside one
binary, so it is only A/B-able between binaries — the comparison sessions 72 and 80 ruled out.

### 4.2 THE SELF-CHECK FIRED, AND THE DEFECT WAS IN THE CHECKER

`bpv83a` read **`bp_bad` = 177 a frame** and printed its full cap of 40 `BindPackVerify: MISMATCH`
lines, **every one of them `null texture key=0`** — item B was clean, item A disagreed with a fresh
resolution on every hit of that key.

The check was `std::memcmp(&check_desc, &slot.desc, sizeof(check_desc))`, and
`TextureCache::ImageDesc` is an **aggregate with padding**: `ImageInfo` ends in `bool bgra16` before
`std::array<ImageMipInfo,16>`, and the outer struct puts `BindingType` (one byte), a `uint32_t` and
a `uint64_t` in a row. `slot.desc = desc` is the implicitly-defined copy assignment — **member-wise,
carrying no padding** — while `ImageDesc desc {}` is aggregate initialisation, which leaves padding
**indeterminate**. The check was comparing bytes that no consumer of the desc ever loads.

Replaced by a field-wise comparison of every field `NullTextureDesc` writes plus the `ImageId`, with
the failing half named in the log. `bpv83b`: **`bp_bad` = 0, sum 0 over 1831 settled frames, zero
MISMATCH lines anywhere in the log.** The memo is correct.

**Neither cut was weakened to get there**, and the second had to read 0 before anything was
measured, exactly as `pred/02_bindpack.md` §2 required.

### 4.3 `bpk83a` — VALID on every pre-registered criterion

| criterion | reading | |
|---|---|---|
| 1. check 2 / check 10 | 0 MISMATCH lines; binary confirmed, 261 `GateArm` blocks | PASS |
| 2. arming inside the run | §4.4 | PASS |
| 3. area split < 1.0 % | **+0.000 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (125/125)** | PASS |
| 3. work within 0.5 % | **+0.109 %** | PASS |
| 4. whole-arm vs paired gap < 0.05 pp | −0.534 % vs −0.529 %, **+0.006 pp** | PASS |
| 5. `da_take_us` | **295.8 → 295.8 ns, unmoved** | reported |
| 6. matched-pair population | yes | PASS |

`guards.py` reads 9 PASS, 2 SKIP, 1 FAIL — the FAIL is check 6 (cores), which is not an admission
criterion and FAILed in 13 of session 81's 20 block runs.

### 4.4 Arming [M], medians over the settled window

| counter | arm `bindpack=0` | arm `bindpack=1` |
|---|---:|---:|
| `tnull_hit` | **0** | **1 486** |
| `tnull_miss` | **1 476** | **0** |
| `bp_mask` | **0** | **9 576** |
| `bp_bad` | 0 | 0 |

The null-T# population is `tnull_hit + tnull_miss`: **1 476 against 1 486, +0.68 %**. The
pre-registration asked for equality within 0.5 % and this is **0.18 pp outside it** — medians of
different frame sets are not additive, `draws` themselves differ by +0.46 % between the arms
(5 244 / 5 268), and the population tracks the draws. It is recorded as the near-miss it is rather
than rounded into compliance.

### 4.5 The effect, and why the gate stays at 0

On the 125 matched pairs [M]:

| statistic | value |
|---|---:|
| `cpu/draw` | **−0.548 % ± 0.146 % (2·SE), t = −7.49** |
| **`cpu_net_us`, the pre-registered primary endpoint, in µs** | **−139.8 ± 81.2 (2·SE), t = −3.44** |
| `cpu_gpu_us` matched-pair effect (`arms.py`) | −140.4 ± 81.2 |
| `cpu_net_us` as a percentage (`summary4`, 130 blocks) | −0.548 % ± 0.248 %, SIGNIFICANT |
| `gpu_busy_us` | +11 µs, inside its own noise |
| `dt_us` | −13 µs — **inside the vblank plateau, and not an endpoint** |

`pred/02_bindpack.md` §6, fixed before the number existed:

> `cpu_net_us` effect **≤ −150 µs** with a 2·SE that excludes zero → **SHIP**.
> effect's 2·SE includes zero, **or** |effect| < 150 µs → **NOT PAID FOR**, the gate stays at 0.

**Measured: −139.8 µs.** The interval excludes zero and the effect is real — t = −3.44 on the
primary endpoint and −7.49 on `cpu/draw` — but it is **10.2 µs, 7 %, short of the threshold this
session wrote for itself before seeing it**. The threshold is not moved. **`bindpack` stays at 0.**

The code stays in the tree: it is correct, it is self-checked clean, and its counters bound the
question — the same disposition `bdabits` got in session 82. A second run pooled with this one
would halve the interval and could cross the threshold; **that is a pre-registration for the next
session, not a decision for this one**, because taking it now is optional stopping.

**A lesson worth more than the decision: write the threshold in the statistic the tool reports.**
`summary4` reports `cpu_net_us` as a *percentage* (−0.548 %), which converts to **−177 µs** against
arm 0's 32 366 µs/frame; the µs estimator on the same pairs reads **−140**. The two disagree by
**26 %** because one averages percentages of block values and the other averages absolute
differences. The threshold was written in µs, so the µs estimator decides — but had it been written
in percent, the same run would have shipped.

### 4.7 THE TWO-RUN POOL — pre-registered before the second run, and it returns the same verdict

`bpk83a` missed the ship threshold by 10.2 µs, which is exactly the shape of result that tempts a
programme to move a threshold. Instead `pred/03_pool.md` was sealed — **after** `bpk83a` and
**before** `bpk83b` existed — fixing the estimator, the weights, `E_a` = −139.8 and `SE_a` = 40.6,
**exactly two runs with no third under any outcome**, and the unchanged −150 µs rule. §1 of it
states the bias it carries in its own words: *the decision to take a second run is data-dependent,
and that is a selection effect*; it is bounded and declared, not removed.

`bpk83b` is **VALID** on every criterion — pair match **100.0 % (126/126)**, split **+0.002 %**,
work **+0.007 %**, guards check 2 and check 10 PASS, `da_take_us` 277.7 → 277.9 ns — and its arming
is exact: `tnull_hit` 0 → 1 496, `tnull_miss` 1 490 → 0, `bp_mask` 0 → 9 620, `bp_bad` 0 in both,
null population **+0.40 %** apart (inside `pred/02`'s 0.5 %, where `bpk83a` read +0.68 %).

| run | `cpu_net_us`, matched pairs | `cpu/draw` |
|---|---:|---:|
| `bpk83a` | −139.8 ± 81.2 (SE 40.6), 125 pairs | −0.548 % ± 0.146 %, t = −7.49 |
| `bpk83b` | −135.8 ± 84.0 (SE 42.0), 126 pairs | −0.457 % ± 0.123 %, t = −7.42 |
| **pool** | **−137.9 ± 58.4 (2·SE), t = −4.72** | |

**Q on 1 d.f. = 0.005 (p = 0.945)**: the two runs agree to **4.0 µs**. That is the finding that
matters more than the verdict — **the package is not "10 µs short of 150", it is worth about 138 µs
and the threshold was not unlucky.** The pooled interval is [−196.2, −79.5].

`pred/03_pool.md` §5: SHIP iff `E_pool` ≤ −150 **and** the upper bound is below zero. The upper
bound is below zero; **−137.9 is not ≤ −150**. → **NOT PAID FOR, finally. `bindpack` stays at 0, and
there is no third run.** Predictions R1–R6 all HIT, including **R4**, the discriminating one, which
was written as "the pool does **not** clear −150" and would have cost something had the package
shipped.

**The effect is real and small.** It is 0.43 % of the CPU frame, it is correct (`bp_bad` 0 over
1831 frames), and it is video-clean (5 732 presents, 0 one-frame glitches). What the rule rejects is
not its existence but its size. The disposition is the one `bdabits` got: the code stays in the
tree, the gate stays at 0, and the package ships when a fourth item pushes the pool past the line.

### 4.6 The video pass — session 82's standing debt, discharged

`bpc83a`: `bindpack=1` in both arms, 180 s held, recorder on. **5 732 recorded presents, 960x540,
index entries 5 732, and `s20_vidglitch.py` reports ONE-FRAME GLITCHES: 0** over 95 one-second
buckets (max inter-frame difference 5.0–5.8 throughout, no outlier). `bp_bad` reads **0** across
3 623 settled frames here too.

This discharges the video debt session 82 carried, and it pre-clears the package: the item that can
reach the renderer — a memoised null-T# `ImageId` and `ImageDesc` — was live for the whole
recording. **This is not a pixel-for-pixel comparison**; no such comparison has ever been made in
this programme and none is claimed.

## 5. CORRECTIONS TO THE RECORD

1. **`KYTY_FRAME_TRACE=lite` prints a SHORT main `FrameTrace` line.** `spin_gpu_us`, `bda_n`,
   `bda_scan` and `bda_skip` live on **`FrameTrace-draw`**, not on it. A tool that reads them off
   the main line finds nothing and, in the case of `cpu_net_us` = `cpu_gpu_us − spin_gpu_us`,
   silently degenerates to `cpu_gpu_us` **without saying so**. `floor83.py` hit this on its first
   run; it now parses `FrameTrace-draw`. `spin_gpu_us` is **5 µs a frame**, so the endpoint is
   numerically the same either way — the defect is that nothing announced the substitution.
2. **Route B's tools had lost two roots.** `arms.py`, `baseline.py` and `effect.py` carried
   `--roots C:/kyty/s83,C:/kyty/s80,…`: **s82 and s81 had silently fallen out** during the s81→s82
   port, because `rewrite()` matched a six-root literal against a seven-root one. Session 82's own
   port printed the diagnostic (`root .py still naming s80: arms.py, baseline.py, effect.py`) and
   it was not read. Repaired in the s83 port and asserted.
3. **`area_series.py` carried `--root C:/kyty/s70` as its default since session 70** and
   regenerated nothing unless `--root` was passed by hand. Fixed to `C:/kyty/s83`.
4. **`CommitPoolTransitNs`/`WriteNs`/`EmitNs` are not unread because they are unprinted.**
   `DESIGN` §6 item 3 says they "exist since session 59 and have never been read"; they **are**
   emitted on `FrameTrace-x` as `cb_pool_tr_us`/`_wr_us`/`_em_us` (and the `cb_push_*` twins), and
   they read **0** because they accumulate only under `DrawStat::On()`, i.e. gate `drawstat`, which
   `gates_base.txt` pins off. Reading them is not free: `drawstat` also arms every `DrawStat::Mark`
   and costs 3–4 % of CPU per draw.
5. **`bb_obtain` (`BindBufObtainNs`) is declared and printed and never incremented anywhere in the
   tree**, so `ObtainBuffer`'s share of the binding cost has never been separated from `b_buf`.
   Same failure class, already named in `PLAN_82_bind.md` §5.
6. **`bda_us` straddles `mh_bind_us` and `mh_disp_us`.** Only the draw-side call
   (`descriptors.cpp:1650`) is inside the binding phase; the dispatch-side call
   (`renderCompute.cpp:780`) is charged wholesale to `mh_disp_us`. Subtracting `bda_us` from
   `mh_bind_us` to decompose the binding phase — which session 82's §4.4 does — **over-subtracts by
   the dispatch share**, and no counter splits the two.
7. **No path from `PrepareGraphicsBindings` reaches `Memory::IsGpuCleanRange`** [I, verified by
   walking the call graph]. `DESIGN` §5.4 ends with "the preparatory work nobody has done: list
   which parts of `mh_bind_us` and `mh_prog_us` reach it". For `mh_bind_us` the answer is **none** —
   every call site of `IsGpuClean*` is in `pipelineCache.cpp` (the SRT/shader-read phase and the M1
   workers). `BufferCache::HasGpuDirtyBytes`, one of its three ingredients, **is** reached, by four
   paths named in the harness notes.

## 6. WHAT WAS NOT DONE

* **No `KYTY_GPU_TIME` pair on `dapin`**, so its +1.238 % GPU cost stays unexplained for a fifth
  session.
* **`bda_us` is not timed by anything in this session** (§3) — a `Lap` inside `PrepareBda` is the
  named next step.
* **No second valid floor run beyond `flr83b`**; `flr83a` agrees to 0.3 % but is void.
* ~~The `mh_prog` question of §2.6~~ — **measured in §2.7 after the first draft of this file was
  written: 68.9 % of it is `PipelineCache::m_mutex` hold, the floor stands, and the session's own
  prediction S3 was wrong.**
* **Whether the 31 % of `mh_prog` outside that lock is parallelisable is [NM]** — it is only known
  not to be protected by *that* lock. Naming the other reasons it might be serial is a
  source-reading task nobody has done.
* **Whether `PipelineCache::m_mutex` can be split** is [NM] and is now the load-bearing question
  behind 5.0 ms a frame. `DESIGN` §5.3 names the precondition: `programs` + `programs_epoch` must
  stop being reachable through **iterators** held by the memo (`SourceEntry*` + a validating key).
* ~~No second `bindpack` run.~~ **Taken under `pred/03_pool.md`, sealed between the two runs; the
  pool reads −137.9 ± 58.4 and the verdict is unchanged (§4.7).** There is no third run.
* **Route C is not started.** `ROADMAP.md` §2 C is now the only route with an unmeasured ceiling and
  nothing in this session measured it.

## 7. THE ARITHMETIC

| | µs/frame | FPS |
|---|---:|---:|
| shipped baseline (`acc82a`, session 82) | 31 642 | 31.60 |
| 60 FPS | 16 667 | 60.00 |
| **the measured sequential floor `S_hi`** | **20 838** | **48.0 at W = ∞, 30.0 on the vblank grid** |
| remaining gap to 60 | ≈ 15 000 | |

**The floor is 4.2 ms larger than the whole 60-FPS budget.** Everything that could still close the
gap has to make the serial work itself smaller — route C of `ROADMAP.md` — because there is no
longer a route that makes it run in parallel.

**What this session shipped, plainly.** No default changed, and the scoreboard did not move: the
binding-path package pooled over two valid runs measured **−137.9 ± 58.4 µs** against the
**−150 µs** threshold this session wrote for itself before the first run, and the threshold was not
moved — the second run showed the package is worth about 138 µs rather than being unluckily short of
150. What did change is the direction:
**route A is closed by a measurement instead of by an argument**, and the three source changes
(`mutwide`, `bindpack`, the corrected self-check) are in the tree, armed by counters, self-checked
clean and A/B'd on this machine.
