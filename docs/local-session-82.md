# Session 82 — FACTS

**The single source of truth for session 82.** Everything is marked **[M]** measured (a counter in a
run, or a prior session's run named), **[I]** inferred (read from source and reasoned), **[NM]** not
measured, **[R]** retracted.

## 0. In one sentence

**The FPS moved for the first time since session 74: 28.61 → 31.60**, because the thread placement
sessions 79 and 81 measured three times as a raw mask became a portable *mode* and shipped; and the
one optimisation this session invented — a write map for the BDA region walk — was **armed
perfectly, measured, and bought nothing**, its first cut having been killed by its own self-check.

## 1. The runs

Six attempts, five completed runs, one entry hang. `-lvl underwater_aerial_garden` (Sky Garden),
settled window **n ≥ 2100** everywhere.

| tag | binary sha256 | what | verdict |
|---|---|---|---|
| `bdv82a` | `6d171d01…` | `bdabits=1 bdabitscheck=1`, 180 s | **DEFECTIVE CODE — nothing quotable** |
| `bdv82b` | `3607aa9e…` | same, after fix 1 | self-check clean |
| `bdb82a` | `515d4ce4…` | ABBA `bdabits=0\|1`, 300 s | **VALID, null** |
| `dap82a` | `515d4ce4…` | ABBA `dapin=65535\|3`, 300 s | **VOID** (area gate) |
| `dap82b` | `515d4ce4…` | ABBA `dapin=65535\|3`, 300 s | **VALID** |
| `acc82a` | `df7a2a50…` | plain run on shipped defaults, 240 s | confirmation, **not a measurement** |

The three ABBA runs share one binary, so they are directly comparable to each other. `acc82a` and
the final installed binary (`143dbc43…`, 23 568 896 B) differ from them — the first by the shipped
default, the second by a comment. **`guards.py` check 10 hashes the exe installed *now*, so re-running
it against `dap82b` today fails check 10 on identity alone.** Compare check *lines*, not verdicts.

`bdv82b` attempt 1 hit the historical entry hang: `role=4`, `requested − known = 1`, `after=8s`,
`submit_backlog=0`, `record_backlog=0`, `acopy=2717/2717/2717`, `acopy_pending=0`. Byte for byte the
signature of session 81 §10. Attempt 2 entered in 27.9 s. **One hang in six attempts is inside the
recorded 6.67 %**; nothing in this session's code touches that path.

## 2. SHIPPED: knob `dapin`, default 1 → 3

### 2.1 What mode 3 is

One logical processor per physical core of the L3 cache group with the most bytes, derived from
`GetLogicalProcessorInformationEx(RelationProcessorCore)` — the SMT-primary of each core of the
X3D CCD. Sites: `pipelineCache.cpp` `DrawAheadLargestL3Mask` / `DrawAheadSmtPrimaryMask`, applied in
`DrawAheadApplyPin` and `DrawAheadApplyRecordPin`. Behaviour at `dapin=0/1/2` and at every raw mask
other than 3 is **byte for byte what it was**; the value 3 has stopped being a raw mask and that is
recorded in `gates.h`.

### 2.2 Why this is not a new contrast

Sessions 79 and 81 measured the arm `dapin=21845` three times and pooled it at **−732.5 µs
[−798.5, −666.4]**, and could not ship it because 21845 is a constant of this machine's topology.
**Mode 3 computes exactly that mask here, and the proof is an identity in the log, not a
statistic** [M]:

```
DrawAheadPin: GuestGpu  mode=3      mask=0x0000000000005555
DrawAheadPin: Record    mode=3      mask=0x0000000000005555
DrawAheadPin: DrawAhead mode=3      mask=0x0000000000005555
DrawAheadPin: GuestGpu  mode=65535  mask=0x000000000000ffff
```

All three thread classes applied it, 64/64/256 times across the 128 blocks.

### 2.3 `dap82b` — VALID, and every pre-registered criterion

| criterion (session 81 §1, carried unchanged) | reading | |
|---|---|---|
| 1. `guards.py --first-frame 2100` check 2 | 0 MISMATCH lines; 2/11 reachable self-check counters zero | PASS |
| 1. …check 10 | binary confirmed, 256 `GateArm` blocks, every arm text where meant | PASS |
| 2. arming by a counter inside the run | `DrawAheadPin: mode=3 mask=0x5555` (§2.2) | PASS |
| 3. area split < 1.0 % | **+0.003 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (123/123)** | PASS |
| 3. work within 0.5 % | **+0.088 %** | PASS |
| 4. `summary4` whole-arm vs paired gap < 0.05 pp | whole-arm −2.182 % vs paired −2.175 %, **+0.007 pp** | PASS |
| 5. bracketing timer `da_take_us` reported | **−41.7 µs** | reported |
| 6. everything on matched pairs | yes | PASS |

**The effect** [M], 123 matched pairs:

| statistic | value |
|---|---:|
| `cpu/draw` | **−2.185 % ± 0.140 % (2·SE), t = −31.12** |
| matched-pair effect | **−660.8 µs ± 83.2** |
| `dt_us` | **−820.7 µs** (32 476.6 → 31 656.0) |
| **FPS** | **30.791 → 31.590 (+0.799)** |
| `cpu_gpu_us` | −639.4 µs |
| `gpu_busy_us` | **+1.238 % (+147.1 µs)** |
| `draws` | +4.1 (+0.088 %) — the arms do the same work |

`guards.py` reads **8 PASS, 1 FAIL, 1 WARN, 2 SKIP**. The FAIL is check 6 (cores: 6 of 49 groups
more than 10 % off their arm median). **Check 6 is not one of the six admission criteria** and
session 81 recorded it FAILing in 13 of its 20 block runs. Checks 8 and 9 are SKIP because the
recorder was off; see §6 for why no video pass was taken.

### 2.4 `dap82a` was VOID and was not quoted

The first attempt at this contrast read **−813.2 µs ± 119.5** and is **not quotable**: area split
**+3.937 %** against the 1.0 % limit and pair match **54.5 % (66/121)**. High-rung share 34.2 % —
DRS climbed a rung in the cheaper arm. This is exactly the bias session 81 established
prospectively (voided runs read −499.6 µs [−903.3, −95.9] *more* than quoted ones).
**The criterion was not substituted, reweighted or retired. Another run was taken.** That the
second run then read a smaller effect (−660.8 against −813.2) is the direction session 81 predicted.

### 2.5 Confirmation, and what it is not

`acc82a`, no schedule, shipped defaults, 5658 settled frames: mean `dt_us` **31 642.1 = 31.603 FPS**,
`cpu_gpu_us` 30 759.2, `gpu_busy_us` 13 235.7, `draws` 5041.1, pin line `mode=3 mask=0x5555`.
**This is a confirmation that the default is live end to end, NOT a measurement**: an inter-run
comparison against the 28.61 FPS baseline of `acc78a` is exactly the comparison sessions 72 and 80
ruled out. The measurement is `dap82b` and only `dap82b`.

### 2.6 The open item, carried forward unchanged

**The GPU side costs +1.238 % (+147.1 µs) and is replicated a FOURTH time** (after +1.350, +1.931,
+1.679 in sessions 79 and 81) and is **still UNEXPLAINED** [NM]. It does not bind — `gpu_busy_us`
12.56 ms inside a 32.5 ms frame — and that is why shipping is defensible, not because the question
was answered. Session 81's brief asked for one `KYTY_GPU_TIME` pair to see which pass kind grows;
that run was not taken.

### 2.7 `gates_base.txt` changed, and it had to

The base pinned `dapin=1`, which would have **silently overridden the new default in every harness
run**. Updated in place: still **1092 bytes, 99 names**, sha256
`4724bf81…f8c4f` → **`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`**.
This breaks an invariant that had held since session 67, deliberately. `dap82a`/`dap82b`/`bdb82a`
ran on the OLD base (their `dapin` came from the schedule, which owns the names it assigns);
`acc82a` ran on the new one.

## 3. NOT PAID FOR: gate `bdabits`, left at 0

### 3.1 What it does

The BDA region walk consults a bit per tracking region before reading that region's write stamp.
The map is a **conservative superset** of "the stamp moved": a clear bit *proves* the stamp is
unchanged, a set bit proves nothing and falls through to today's code. Bits are set at every event
that can move a stamp — both `m_epoch.fetch_add` publishers (`regionManager.h:209`, `:370`) and
region creation (`memoryTracker.cpp:70`) — and cleared **before** the region is read, so a write
racing with the scan is seen by the next preparation instead of lost.

### 3.2 Why it was expected to pay, and why that was wrong

`bind78a` [M]: `bda_n` **181** `PrepareBda` calls a frame at `bda_us` **2181 µs** = **12.05 µs a
call**, and inside them **18 582 region visits** (`bda_skip` 17 518 + `bda_scan` 1064) to find 1064
moved stamps. Every visit is an acquire load of `m_regions[index]` and a dependent load of
`manager->Epoch()`. **My estimate that 17 518 of those cost ~0.6–1.0 ms a frame was wrong** [R]:
the ~103 managers are re-read by all 180 calls of the frame and stay hot, so the loads saved were
already cheap. **What the 2181 µs is actually spent on is [NM]**; the `m_buffers` `std::map`
lookups of `SynchronizeBuffersInRange` (`bufferCache.cpp:2519`, `:2526`, `:2461`) are the next
candidate and were never timed.

### 3.3 `bdb82a` — VALID, armed, null

Arming, per arm, medians [M]: `bda_bskip` **0 → 20 601** a frame (99.95 % of the 20 611 skips),
`bda_scan` **1066 in BOTH arms** (identical work), `bda_bit_bad` **0**, **0 MISMATCH lines**.
Validity: area split −0.004 %, pair match **100.0 % (117/117)**, work −0.146 %.

**Effect: −50.8 µs ± 87.5 (2·SE); `cpu/draw` −0.003 % ± 0.178 %, t = −0.03.**
The A/A noise floor of this instrument is ±75…92 µs (`aa78a` +24.8 ± 75.8; session 81 A/A
−7.0 ± 91.6). **The result is null and the gate stays at 0.** It is kept in the tree because it is
correct and its counters bound the question.

### 3.4 THREE DEFECTS IN THE FIRST CUT, ALL FOUND BY ITS OWN SELF-CHECK

`bdv82a` printed **40 361 555** `BdaBitsVerify: MISMATCH` lines over 3355 settled frames.

1. **THE LOGIC — a correctness defect, not a false alarm.** A clear bit proves "no announcement
   since this scan last cleared it". It does **not** prove today's code would have skipped, because
   today's skip *also* requires a stamp stored under the **current generation**. A region never
   scanned under this generation has `generation` 0 against `m_bda_stamp_generation`'s initial 1, so
   today's code SCANS it and the first cut SKIPPED it — **unscanned bytes stayed unscanned**. Fixed
   by requiring both halves, and by clearing the bit unconditionally (a region that falls through
   without clearing would never become skippable again).
2. **THE LOG.** The MISMATCH line had no cap, unlike every other verify in the tree
   (`SyncFreeVerify` 64, `BufFastVerify` 32, `TrackFreeVerify` 64). 40 M lines is a 22 MB/s log and
   would have distorted the run even had the logic been right. Capped at 40.
3. **THE PRINTF.** The format string and the argument list went into one `patch()` call; the
   argument anchor failed, so the file was never written and the arguments were applied separately
   afterwards. Result: **four `%llu` against six arguments** — in `log_bdv82a.txt` `bpage_hit` and
   `bpage_miss` carry `bda_bskip` and `bda_bit_bad`, and **every counter after `bda_skip` in that
   one printf is shifted by two and is not quotable from that run.**

`bdv82b`, after the fix: `bda_bskip` 22 778 of 22 783 skips (99.98 %), `bda_bit_bad` **0** over
n ≥ 2100, and **4** MISMATCH lines, all in warm-up. Those four are the documented
announce-between-two-queries race — a write landing after the clear sets the bit again, so the skip
was sound. The check was then hardened the way `SyncFreeVerify` is (`BdaRegionWritePending`), and
`bdb82a` reads **0 MISMATCH lines**.

## 4. CORRECTIONS TO THE RECORD

Four numbers in `docs/next-session-82.md` and in session 75's FACTS are wrong. Each was re-derived
from the logs this session.

1. **22.421 ms is NOT the sequential mutating floor.** Gate `amut` arms `FrameStats::MutScope`,
   whose construction sites are exactly six in the whole tree (`bufferCache.cpp:738`, `:895`,
   `textureCache.cpp:2030`, `:2206`, `descriptors.cpp:1054`, `renderDraw.cpp:1971`), and it measured
   `a_mut_us` **13 300** (`amut68a`) and **14 035.5** (`amut69a`). 22 421 is
   `a_hold_us(mut69a) 29 906 − mh_prog_us(mut69a) 7 485`; `mut69b` reproduces the identity
   (31 650 − 8 049 = 23 601). The mislabel entered through s75/FACTS §4 and reached the brief.
   **The true floor is [NM], bracketed by [13.3, 29.0] ms.**
2. **`mh_bind_us` is 13 355.5, not 13 215.3**; 13 215.3 is `d_bind` (`DrawBindingsNs`).
3. **`b_view` is a sibling of `b_tex`, not a child**: `BindFindTexNs` brackets
   `TextureCache::FindTexture`, which is reached only from `RebindImages`, while `ResolveTextureWith`
   calls `FindImage`.
4. **The `mh_bind` residual is 3547.6 (against `d_bind`) / 3687.8 (against `mh_bind_us`), not
   4012.3**, and about **2003 µs of it is `bda_us`** — a timer session 78 simply did not subtract.

And one of this session's own: **run `bk82a`, taken before the numbers above, is INVALID in its
entirety** — last flip n = 669, the n ≥ 2100 window never reached, `dt_us` 54 501 (18.3 FPS) against
a 33 537 baseline, `cpu_gpu_us` 49–51 k against 31.7 k. Its `rt_kpx/rt_att` is 2014 Kpx, so this is
**not** a DRS rung — it is a machine state that appears in no run of the record. **No `bk_*` number
is quoted anywhere.** Its one-slot comparison (`previous_key[stage]`, `descriptors.cpp:1374`) also
answers "does this stage repeat the *immediately preceding* draw", not "does it repeat any recent
draw", so it would not have settled the binding-memo question even had the run been valid.

## 5. THE FULL CPU FRAME, DECOMPOSED — first time in the record

`bind78a`, medians over 6171 settled frames, verified by two independent parsers [M]:

| phase | µs/frame | share of `a_hold_us` |
|---|---:|---:|
| `mh_pro_us` prologue | 302 | 1.0 % |
| `mh_rt_us` render state | 806 | 2.8 % |
| `mh_prog_us` programs | 5 831 | 20.1 % |
| **`mh_bind_us` bindings** | **12 027** | **41.5 %** |
| `mh_emit_us` apply + record | 7 403 | 25.5 % |
| `mh_tail_us` | 241 | 0.8 % |
| `mh_disp_us` dispatch | 2 419 | 8.3 % |
| `mh_pres_us` present | 123 | 0.4 % |
| sum | 29 152 | |
| `a_hold_us` (render mutex held) | **29 004** | **89 % of `cpu_gpu_us` 32 501** |
| `gpu_busy_us` | 12 509 | the GPU could sustain ~80 FPS |

`spin_gpu_us` 4 µs, `spin_us` 119 µs — lock contention is negligible today, which is the baseline
any parallel scheme must be held against.

## 6. WHAT WAS NOT DONE

* **No video pass.** `guards.py` checks 8 and 9 are SKIP. The shipped change is thread affinity and
  cannot reach the renderer; `bdabits` is off. **A video pass is still owed before the next
  behavioural change ships**, and `bdabits` must get one if it is ever turned on.
* **No `KYTY_GPU_TIME` pair on `dapin`**, so the +1.238 % GPU cost stays unexplained (§2.6).
* **No second valid `dapin` run on this binary.** The shipped figure rests on one valid run here
  plus three in the record.
* **No measurement of the true mutating floor**, which is the single number deciding whether the
  parallel rewrite is worth starting (§4.1, and `DESIGN_82_parallel.md` §5).
* **`bda_us` reads 0 in `KYTY_FRAME_TRACE=lite`** (it is a `Scope`, which needs `TimingsEnabled()`),
  so nothing in §3 is attributed to the BDA path by a timer — only by the ABBA on `cpu_gpu_us`.

## 7. DESIGN WORK PRODUCED, NOT YET BUILT

* **`C:/kyty/s82/DESIGN_82_parallel.md`** — slice-parallel command recording (a sequential spine plus
  N record contexts), the lock decomposition, the race inventory, the build order in nine steps, and
  the kill criteria K1–K8. Its headline: **60 FPS requires `S ≤ 14 ms` AND `f_eff ≤ 0.125`
  simultaneously**, i.e. eight-way parallelism finer than DCB granularity together with a
  sequential floor sitting on its measured lower bound. At DCB granularity (4 units, f = 0.30) the
  ceiling is 30 FPS whatever else is done.
* **`C:/kyty/s82/PLAN_82_bind.md`** — the binding path, thirteen ranked items summing to
  **0.7…2.5 ms** after container deflation, i.e. 4–14 % of the gap.
* **The vblank plateau, and it governs everything that follows** [I from session 80's identity, [M]]:
  `dt_us` is quantised to 1/2/3 × 16 666.7 µs. Between roughly −1.6 ms and −15.8 ms of saving the
  scoreboard reads **30.0 FPS and does not move**. 44.6 FPS = 22.4 ms = two vblanks = 30.0; that
  number will never appear on screen. **The primary endpoint of every run in that band must be
  `cpu_gpu_us − spin_gpu_us`, decided before the run, not `dt_us`.**

## 8. THE ARITHMETIC

| | µs/frame | FPS |
|---|---:|---:|
| baseline of record (`acc78a`) | 34 956 | 28.61 |
| shipped this session (`acc82a`, confirmation) | 31 642 | **31.60** |
| 60 FPS | 16 667 | 60.00 |
| **remaining gap** | **≈ 15 000** | |

Three shipped gates plus `dapin` are worth about 3.0 ms together. The binding path offers at most
another 2.5 ms. Everything else lives behind the parallel rewrite, and that rewrite is bounded by
a sequential floor nobody has measured.
