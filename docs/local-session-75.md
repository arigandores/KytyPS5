# Session 75 — FACTS

**Single source of truth for session 75.** Every number here was produced by running the named tool
on the named log. Where a number is an estimate it says so in those words. Where something was not
measured it says NOT MEASURED and names what would measure it.

Tree: `merge-upstream`, base `876a3b0` (session 74's `b8fd302` plus its doc commit); this session is
commit **dd7926f**, 6 files, +197 / −21, not pushed.
Installed binary: **`7026D06B0601F6F0B5983A08155549FB3C1F38D22F6B788BE5C1BA6F0191204D`**
(short `7026d06b`), 23 558 656 bytes.

Two binaries carried runs; each run's `<tag>.json` records which, and guards check 10 verifies it:

| binary | what it is | runs |
|---|---|---|
| `017fc031` | session 74's installed binary, UNCHANGED | `dwl75a`, `dpf75a` |
| **`7026d06b`** | **+ gate `pfhint`, + 13 counters — INSTALLED** | `smk75a`, `pfh75a`, `pfh75b`, `base75a` |

---

## 0. In one sentence

The session **re-measured the programme's largest named non-M4 article directly instead of by
subtraction and found it half the size** (0.40–0.46 ms, not 0.896 ms), **priced the thing next to it
at 0.98 ms** — the largest single measured CPU article in the M1 path — **proved from source to
binary that every prefetch in that path asks for the wrong cache level**, **answered M4's second
question with six counters** (a submission-slice boundary is never inside an open render pass, almost
never on the same processor, and the frame's work sits in four substantial slices), and **built the
validity instrument that caught two of its own runs** rendering different numbers of pixels in the
two arms while every guard passed.

**Nothing shipped.** The one candidate this session wrote is NOT MEASURED, and the reason is named,
reproduced and now instrumented.

---

## 1. The runs

| tag | what | hold | entry | `pre_run` | binary | verdict |
|---|---|---:|---:|---|---|---|
| `dwl75a` | ABBA `dawitloop=0\|2` | 300 s | 19.3 s | 2.0 % / 27.5 W | `017fc031` | **9 PASS, 0 FAIL, 1 WARN**, PASS |
| `dpf75a` | ABBA `daprefetch=1\|0` | 300 s | — | 2.0 % / 28.4 W | `017fc031` | **8 PASS, 0 FAIL, 2 WARN**, PASS |
| `smk75a` | smoke on the new binary | 90 s | 14.8 s | 2.0 % / 28.8 W | `7026d06b` | 0 errors |
| `pfh75a` | ABBA `pfhint=0\|1` | 300 s | — | 2.0 % / 28.8 W | `7026d06b` | **FAIL check 6** — §5 |
| `pfh75b` | ABBA `pfhint=0\|1`, re-take | 300 s | — | 2.0 % / 29.1 W | `7026d06b` | **FAIL check 6** — §5 |
| **`base75a`** | **base + video** | 300 s | — | 2.0 % / 27.0 W | `7026d06b` | **9 PASS, 0 FAIL, 0 WARN, 3 SKIP, 0 glitches** |

**Six runs, every one entered Sky Garden at the first attempt.** 0 `GpuWaitSlow` / `GpuHangAbort` /
`ErrorDeviceLost` / `Unhandled exception` / `MISMATCH` / `VUID` in all six logs. `guards.py` check 2
reads **11/11** self-check counters present and zero on every run.

**Base (`base75a`, 6467 settled frames, n ≥ 2100):** draws/frame **5043.3**, dispatches 268.0,
`cpu/draw` **6.5903 µs**, `cpu_gpu_us` **33 237**, `gpu_busy_us` **14 699**, `dt_us` **35 763**,
**27.96 FPS** — 9 PASS, 0 FAIL, 0 WARN, 3 SKIP, VERDICT PASS, **0 one-frame glitches**, check 8
presents step 1 everywhere.

---

## 2. The live loop — measured directly, and it is half what the programme carried

### 2.1 What the 0.896 ms actually was

Session 72 reported the M1 witness's live loop at **0.896 ms of wall per frame**. That number is
**1.929 ms − 1.033 ms**: the whole of `VerifyWitness` (from `wit72a`, ABBA on `dawitness`) minus the
clean loop (from `wlp72a`, ABBA on `dawitloop=0|1`) — two ABBAs from **two different runs on a
session-72 binary**, which inherits both errors and which the programme's own rule against
cross-run arithmetic should have flagged. It has never been re-measured.

### 2.2 `dwl75a` — the direct measurement, and it needed no code

Knob `dawitloop` has a value 2 that skips the live-run compare body while leaving the loop, the
ordinal and — crucially — **the prefetch pass at `pipelineCache.cpp:769-775`, which sits BEFORE the
skip test at :777** — running. So an ABBA on `dawitloop=0|2` measures the **compare body alone**,
where the subtraction measured compare body + prefetch pass + prologue + call.

`dwl75a`, 122 pairs, on the INSTALLED session-74 binary with no rebuild:

    cpu/draw        -1.249 % +- 0.216 % (2*SE),  t = -11.55   SIGNIFICANT
    whole-arm cpu/fr  32 319 -> 31 863 us  =  -456 us
    paired            -1.249 % of 32 319   =  -404 us
    gpu_busy_us     +0.035 % +- 0.230 %  - noise
    work check      draws -0.160 %  -> OK
    cross-check     whole-arm -1.253 % against paired -1.249 %, gap 0.004 pp

**The live compare body of `VerifyWitness` costs 0.40–0.46 ms of CPU wall per frame.**

**Armed, and proved by a counter in the run:** arm1 `da_loop_skip` = **54 910.902**/frame against
live runs = `da_runs − da_runs_clean − da_singles` = 82 671.530 − 27 757.739 − 0 = **54 913.791** —
**0.0053 % apart**. arm0 reads 2.839 (schedule-boundary frames). Behaviour bit-identical:
`da_hit` = `da_direct` in both arms (8641.265/8641.259 and 8632.752/8632.758), every `da_stale*`
zero, guards check 2 11/11.

**The timer corroborates the wall to 1 %:** `da_take_us` **2703.891 → 2296.486 = −407.4 µs** against
the paired wall estimate of −404 µs.

### 2.3 What follows for W3, W4 and W5

W5 attacks the compare body. Its target is therefore **0.43 ms, not 0.896 ms**, and session 75's
recon established two further things about it, both verified against the shipped binary by an
independent adversary:

* **W5's premise as stated is dead.** At the project's own `/O2` clang **fully unrolls**
  `SameRecordedWords` into a straight-line 8-deep chain — there are no iterations to halve. The
  function has zero symbols in the link map and four copies of the chain sit inside `VerifyWitness`.
* **The loop is not instruction-bound.** 0.896 ms / 54 912.6 runs = 16.32 ns per run against roughly
  52.7 retired instructions is IPC 0.8–1.1 against a 3–4 floor for that instruction mix. Removing a
  third of the instructions from a loop stalled three- to four-fold on memory returns a third of a
  quarter. **The host core clock appears in no log in this programme, so the IPC figure is an
  ESTIMATE, NOT MEASURED.**

---

## 3. The prefetch — 0.98 ms, and it has been asking for the wrong cache level

### 3.1 `dpf75a` — the population, measured before anything was written

`daprefetch` is a shipped gate, on by default since session 56, and **it had never been measured
alone**. One ABBA settles what the whole prefetch idea is worth and bounds W3 and W4 together.

`dpf75a`, 125 pairs, on the INSTALLED session-74 binary:

    cpu/draw        +3.064 % +- 0.244 % (2*SE),  t = +25.14   SIGNIFICANT
    whole-arm cpu/fr  31 950 -> 32 926 us  =  +976 us
    gpu_busy_us     +0.078 % +- 0.223 %  - noise
    work check      draws -0.001 %  -> OK
    cross-check     whole-arm +3.055 % against paired +3.064 %, gap 0.010 pp

**The M1 prefetch is already worth 0.98 ms of CPU per frame** — more than the live compare loop it
feeds (0.43 ms) and more than sessions 72–74 shipped in total (1.01–1.07 ms).

### 3.2 The defect, proved from source to binary

`pipelineCache.cpp` includes `<xmmintrin.h>` at **line 57**, below fifty-six project headers. One of
those has already pulled in `<windows.h>`, and `winnt.h:3649` defines, **unguarded**:

    #define _MM_HINT_T0     1
    #define _MM_HINT_T1     2
    #define _MM_HINT_T2     3
    #define _MM_HINT_NTA    0

By line 57 the xmmintrin include guard is set, so clang's own `_MM_HINT_T0` (3, `xmmintrin.h:2185`)
is never defined and winnt.h's 1 stands. clang lowers `_mm_prefetch(p, sel)` as
`__builtin_prefetch(p, 0, sel)` with **GCC locality**, where 3 = T0, 2 = T1, **1 = T2**, 0 = NTA.

**Proof 1 — the compiler names it.** Lines 1..57 of the real file, compiled with the project's own
flags and includes plus `static_assert(_MM_HINT_T0 == 3)`:

    real.cpp(59,15): error: static assertion failed due to requirement '1 == 3'
    winnt.h(3649,25): note: expanded from macro '_MM_HINT_T0'

**Proof 2 — the same prefix, two forms, two opcodes.**

| source | emitted |
|---|---|
| `_mm_prefetch(p, _MM_HINT_T0)` — today | **`prefetcht2`** |
| `__builtin_prefetch(p, 0, 3)` — the fix | `prefetcht0` |

**Proof 3 — the shipped binary.** `llvm-objdump` of `017fc031`: **50 `prefetcht2`, 13 `prefetcht0`,
72 `prefetchnta`**, and the three-deep 0 / 0x40 / 0x80 chain at `0x140842a05` — which is
`PrefetchVectorData`'s 192-byte cap and nothing else in the binary has that shape — is `prefetcht2`.
After this session's build, `prefetcht0` reads **63** (13 + 50): both forms are compiled and the gate
picks at run time.

**All four `_mm_prefetch` call sites in the whole tree are in this one file** (`:772`, `:1247`,
`:2306`, `:2307`), so the defect is exactly co-extensive with the M1 witness path — which is the path
that was just measured at 0.98 ms.

### 3.3 The gate is armed and the prize is NOT MEASURED

Gate **`pfhint`** (`KYTY_PREFETCH_HINT_L1`, default **0** = today, bit for bit). The arming proof is
a counter, not the launcher: `pfh75a` arm1 `pf_l1` = **8626.306** against `da_hit` = **8626.657** —
**99.996 %** — and arm0 = 0.371 (boundary frames). The gate fired exactly where it was meant to.

**Its prize is NOT MEASURED.** See §5.

---

## 4. M4's second question — answered by six counters, at `m4baton=0`

Session 74 answered the transport negatively: 93–94 % of baton range hand-offs fall inside an open
render pass at every L where hand-offs exist, and the boundaries collapse onto ~12.5 submission
slices a frame. This session put counters on the slice itself.

A **submission slice** is one call of `CommandProcessor::Process` that reaches `ProcessPm4` with a
non-empty buffer stack (`graphicsRun.cpp:957-987`). Six counters at that one site, all behind
`FrameStats::Enabled()`, all working at `m4baton=0`, firing ~12.7 times a frame.

`base75a`, 6467 settled frames:

| counter | per frame | reading |
|---|---:|---|
| `slc_total` | **12.702** | inside the band 11.0–14.0 **predicted before the run**; the smoke run read 12.821 and the baton runs 12.42 / 12.55 — **the slice count is not a baton artefact** |
| `slc_inpass` | **0.000** | **a slice boundary is NEVER inside an open render pass** — the obstacle that killed the range fork does not exist here |
| `slc_cp_same` | **0.011** | consecutive slices almost always run on different `CommandProcessor`s, so serialiser (2), the per-processor register context and cursor, is not touched at the boundary |
| `slc_newcb` | 10.691 (**84.2 %**) | exactly the floor 0.838 predicted from the flush count; the missing 15.8 % are the CE/DE boundaries that carry no flush |
| `slc_resume` | 4.701 | **8.001 independently schedulable units per frame** |
| `slc_d0 / d1 / d2 / d3 / d4` | **8.702 / 0 / 1.000 / 3.000 / 0** | sums to 12.702 = `slc_total` **to the digit** |

**The concentration histogram is the most useful number, and it is not a distribution — it is a
structure.** Exactly 3.000 slices a frame execute 1024–2047 draws+dispatches, exactly 1.000 executes
512–1023, none reaches 2048, and 8.702 are trivial (< 128). Against 5311 items a frame, the 8.702
trivial slices carry at most 8.702 × 127 = 1105, so **the four substantial slices carry ≥ 79.2 % of
the frame** and the largest is **f ≈ 0.23–0.39** of it — not the 0.80+ that would have killed the
route, and not the even ~0.10 spread either.

**Verdict: none of the three obstacles that closed the fork at range granularity holds at slice
granularity.** The pass never has to be broken (0.000), the register context is not shared across the
boundary (0.011), the command buffer already turns over at 84.2 % of boundaries, and the work divides
into four balanceable units. What remains is serialiser (3) — the single shared `CommandScheduler`
and its single-producer `CommandRecorder` — at the 15.8 % of boundaries that do not turn over.

**The ceiling this does NOT move.** `cpu_gpu_us` is 33 237 µs a frame and the sequential mutating
floor was measured at 22.421 ms (`mut69a`) and 23.601 ms (`mut69b`) — and session 72 recorded that
figure as UNDERSTATED. 22.421 ms is **44.6 FPS**. **M4 at any granularity cannot deliver 60 FPS on
its own**; at best it delivers about 10.8 ms of the 16.6 ms deficit, minus a splice tax of
8.001 × 11.33–11.76 µs = **91–94 µs** a frame.

### 4.1 A session-74 statement withdrawn, by measurement

`s74/FACTS.md` §3 says "At L=512 session 68 measured ranges/frame equal to the slice count, i.e.
**zero internal hand-offs**." That is wrong. `C:/kyty/s68/log_bat68_512.txt`, arm 1 (`m4baton=512`),
2285 steady frames at n ≥ 2100, extracted by this session:

    bat_ranges 10.5287 + bat_self_ranges 10.5295 = 21.0582 ranges/frame,  bat_drop 0.0000
    arm 0 (m4baton=0), the control:                 0.0386

Against a slice count of 12.4–12.7 that is about **8.5 internal hand-offs at L=512, not zero**.

---

## 5. Why nothing shipped — and the instrument that says so

### 5.1 The two `pfhint` runs disagree by 2.4 pp

| run | pairs | `cpu/draw` | 2·SE | t | guards |
|---|---:|---:|---:|---:|---|
| `pfh75a` | 123 | +0.197 % | 0.729 % | +0.54 | **FAIL check 6** (3 of 48 groups) |
| `pfh75b` | 124 | −2.080 % | 0.913 % | −4.56 | **FAIL check 6** (4 of 48 groups) |

Both 2·SE are three to four times worse than the session's two clean runs (0.216 %, 0.221 %), and the
two point estimates straddle zero by 2.3 pp. **Neither is quoted.**

### 5.2 The cause: the arms rendered different numbers of pixels

`rt_kpx / rt_att`, arm1 against arm0, n ≥ 2100:

| run | arm0 | arm1 | difference | high-rung share |
|---|---:|---:|---:|---:|
| `dwl75a` | 2007.8 | 2007.8 | **+0.00 %** | **0.0 %** |
| `dpf75a` | 2007.7 | 2007.7 | **+0.00 %** | **0.0 %** |
| `pfh75a` | 2338.6 | 2379.4 | +1.74 % | 28.9 % |
| `pfh75b` | 2754.3 | 2872.7 | **+4.30 %** | **66.4 %** |

When the DRS rung oscillates, its episodes (median 24–62 flips, session 74 §5.2) **alias against the
30-flip block period of the schedule**, and the two arms end up rendering different numbers of pixels
while drawing the same number of draws. `cpu/draw` is then not a comparison of the arms.

**No guard catches this.** Check 3 compares the resolution GAUGES `rt_w`/`rt_h`, which are the output
target and read 3840×2160 in both arms whatever the rung does — it PASSED on both runs. Check 3b is
advisory on the pass area and only raised a WARN. **Two runs were invalidated by something every
guard passed.**

### 5.3 The instrument — `area_matched_ab.py`

New tool: it rebuilds summary4's own estimator (block value = ratio of sums, paired between adjacent
blocks of the two arms) and keeps only the pairs whose two blocks agree in rendered area to within a
tolerance. **It validates on the controls**: `dwl75a` and `dpf75a` match every pair (max |Δarea|
0.106 %) and the matched result equals the all-pairs result exactly.

| run | matched | `cpu/draw` on matched | `gpu_busy` all → matched |
|---|---|---|---|
| `dwl75a` | 117 / 117 | −1.280 % ± 0.216 %, t = −11.85 | +0.099 % → +0.099 % |
| `dpf75a` | 120 / 120 | +2.988 % ± 0.221 %, t = +27.01 | +0.094 % → +0.094 % |
| `pfh75a` | 75 / 118 | **+0.375 % ± 0.429 %, t = +1.75 — noise** | +0.550 % → **+0.062 %** |
| `pfh75b` | **28** / 119 | −2.031 % ± 1.023 % — 28 pairs is a sliver | +1.406 % → **−0.237 %** |

The filter removes the GPU artefact exactly as designed. It does **not** reconcile the two CPU
numbers: in `pfh75b` matched (−2.031 %) and dropped (−2.063 %) agree, so that run's CPU effect is not
an area artefact but something else the run does not isolate.

**`pfhint` is NOT MEASURED.** *Next measurement:* one ABBA taken as the **first run of a session, on
a cold machine**, accepted only if `area_matched_ab.py` matches ≥ 90 % of pairs.

### 5.4 Why the machine got worse — a named mechanism for session 74 §9.6

The high-rung share rose monotonically across the session, and so did the GPU's thermal state:

| run (in order) | high-rung share | mean temp | mean power | 2·SE on `cpu/draw` |
|---|---:|---:|---:|---:|
| `dwl75a` | **0.0 %** | 67.8 °C | 76.3 W | **0.216 %** |
| `dpf75a` | **0.0 %** | 69.1 °C | 78.2 W | **0.221 %** |
| `pfh75a` | 28.9 % | 69.8 °C | 81.0 W | 0.728 % |
| `pfh75b` | **66.4 %** | 71.0 °C | 84.8 W | **0.886 %** |

Session 74 left "why the DRS rung latches" NOT ESTABLISHED. **This is the first named candidate: it
tracks the machine's thermal state across a session, and the stand degrades with it.** It is a
correlation over four runs, so it is a HYPOTHESIS, NOT MEASURED. *What would measure it:* two base
runs of identical configuration, one from cold and one after an hour of load, comparing the high-rung
share; or one run with `KYTY_POKE="27e46c:909090909090"` reading `GuestOut:` around each crossing.

**The operational consequence is immediate and should be adopted: take the decisive ABBA FIRST.**
This session's first two runs resolve 0.22 %; its last two resolve 0.9 %.

---

## 6. W3 — the population is not empty, it is large

`da_pf_b` (bytes the eleven vectors of one take OFFER to `PrefetchVectorData`) against `da_pf_cap_b`
(what the 192-byte cap lets through), `base75a`, 6467 frames:

    da_pf_b      12 535 382 bytes/frame
    da_pf_cap_b   7 382 040 bytes/frame
    truncated     5 153 342 bytes/frame  =  80 521 cache lines/frame  =  41.1 % of what is offered
    per take      1452 B offered, 855 B prefetched, 597 B truncated

Session 75's recon reader called this population empty from the per-frame mean; its adversary refuted
that from `log_base74a.txt` with a Jensen floor of ≥ 561 lines/frame. **The measured answer is
80 521 lines/frame — 143× the adversary's floor and infinitely more than the reader's zero.** Neither
had the per-take distribution, which is what decides it.

**W3's prize is still NOT MEASURED** — a truncated line is only worth something if the loop would
have stalled on it. *Next measurement:* a knob that raises the cap, ABBA'd against 192.

---

## 7. What this session did NOT close, with the next measurement named

1. **`pfhint` — NOT MEASURED** (§5). *Next:* one ABBA as the FIRST run of a session, on a cold
   machine, accepted only if `area_matched_ab.py` matches ≥ 90 % of pairs.
2. **W3's prize — NOT MEASURED** (§6). Population measured at 80 521 truncated cache lines a frame.
   *Next:* a knob on the 192-byte cap, ABBA'd.
3. **W5** — target corrected from 0.896 ms to 0.43 ms, premise (fewer iterations) refuted by the
   disassembly, loop shown to be memory-stalled. *Next, if it is ever wanted:* the run-length
   histogram, and a `dawitloop=3` that walks the live runs without comparing, which is the only thing
   that splits the 0.43 ms into its per-run and per-word halves.
4. **W4** — untouched. The vector prefetch has ~200 instructions of distance; the guest-line prefetch
   at `:772` has ~43–51 for run 0 and none for the last run. *Next:* software-pipeline the backing
   prefetch into the compare loop, which needs no publish-side structure.
5. **The wall cost of the 738 counters — NOT MEASURED.** Designed and not run: one ABBA on
   `fslean=0|1`, which silences 699 of 725 counters in-run (indices 25..724; `LogNs` is 25).
   **Expected artefact, stated in advance:** `rt_att` is index 547 and goes silent, so guards checks
   3 and 3b lose their arm1 population — that is a property of the arm, not of the machine. It
   measures the accumulate half only, so it is a LOWER bound.
6. **The C3 closure `c3_pop == img_skip` — CLOSED BY READING, no run needed.** The two counters are
   incremented 53 lines apart in one function from one `population` boolean with only
   `&& Gates::Enabled(ImageSkipGpuStale)` between them; the identity is a tautology of the current
   tree. Four sessions of "not run" resolved without a run.
7. **Why the DRS rung latches** — first named candidate (§5.4), NOT MEASURED.
8. **`0x53be70000`'s registration lifetime** — reading done: one create path
   (`FindImage → InsertImage → RegisterImage`), nine `FreeImage` call sites of which only two are
   gated by `safe_to_delete`. *Next, no code needed:*
   `enter_scene.py lif75a --hold 150 KYTY_IMAGE_LIFETIME_TRACE=1 KYTY_IMAGE_LIFETIME_MIN_KB=8192
   KYTY_CLEAR_TRACE=1`, joining `ImageLife:` on `BufferFillTrace:` by frame.
9. **Gate `dawitfb` is still dead code with an empty population.** Deletion plan written and
   deliberately NOT applied — it would have moved `gates_base.txt` mid-session and split the run
   record in two for zero prize.
10. **Whether W8's `gpu_busy_us` rise is frame packing** — carried from session 74, untouched.
11. **The sequential mutating floor is above 13.9–14.9 ms by an unmeasured amount.**

---

## 8. Code and tools

### 8.1 Source, 6 files, +197 / −21

**One gate, default 0:** `pfhint` (`KYTY_PREFETCH_HINT_L1`). At 0 the emitted instruction is today's
bit for bit; at 1 the four prefetch sites issue `prefetcht0`. The gate is read **once per take**,
never per line, and the hot loop over 54 911 runs a frame is duplicated under one branch so neither
arm pays a per-iteration test. A prefetch changes no value and no decision, so **the arms are
behaviourally identical by construction and no self-check is needed.**

**Thirteen counters**, all past `Counter::LogNs` so `fslean=1` silences them:

* `pf_l1` — the arming proof of `pfhint` (`da_hit` in the armed arm, 0 in the other).
* `da_pf_b`, `da_pf_cap_b` — W3's population.
* `slc_total`, `slc_inpass`, `slc_resume`, `slc_cp_same`, `slc_newcb`, `slc_d0`..`slc_d4` — the
  submission slice.

**The session-74 trap was answered, not tripped:** every Add at `CommandProcessor::Process` is
written `Common::FrameStats::Add(Common::FrameStats::Counter::X, 1)` in full, because all five
`namespace FS = Common::FrameStats;` in `graphicsRun.cpp` are block-scoped and all five sit **below**
that function. `slice_resume` is captured before the push that would make the stack non-empty;
`slice_draws0` is declared in the function body, outside the `Enabled()` guard, because the histogram
reads it after `ProcessPm4` returns; the two file statics go above the function, not with the baton
statics 554 lines below it.

**A `Gauge` was deliberately not used** for the concentration: a Gauge would need the main
`FrameTrace` format string and its argument list edited together, which is the usual way that edit
breaks, and a five-bucket histogram says more than a max.

**Checks:** two clean builds, 0 errors and no new warnings; five test binaries pass (plus
`memory_tracker_tests` with `KYTY_ARM_DEFER=1`) and the four `shader_recompiler_compute_tests` groups
that touch the tiler and the image-view cache; `resource_tracking_tests` fails as always with a
**byte-identical 1478-byte log, sha256 `06aef666…`**, matching s60/s63/s64/s67–s74.

### 8.2 Harness `C:/kyty/s75`

Port of `C:/kyty/s74` with the roots rewritten; session 74's applied one-shot patches are parked in
`prev74/`, 73's in `prev73/`, 72's in `prev72/`, 71's in `prev71/`. `.txt`/`.json` copied byte-exact
(`gates_base.txt` verified sha256-identical at 1072 bytes before regeneration).
`gates_base.txt` now pins **98 names — 83 gates and 15 knobs, 1081 bytes**, adding `pfhint=0`;
`gen_gates.py --check` exits 0 and `--selftest` passes 27 assertions.

New: **`area_matched_ab.py`** (§5.3) and the recon corpus `recon75/` (five areas, each read by one
agent and refuted by an independent adversary, every claim carrying `file:line`).
Applied patches: `patch_pfhint.py`, `patch_m4_slices.py`.

---

## 9. The arithmetic, restated

**Today** (`base75a`): CPU **33 237 µs**, GPU **14 699 µs**, wall **35 763 µs**, **27.96 FPS**.
CPU is still the wall.

| article | axis | measured | state |
|---|---|---:|---|
| `dawitptr` + `daepceil` | CPU | 0.33 ms | shipped, session 72 |
| `imgfuse` (C1) | GPU / CPU | 1.268 / 0.182 ms | shipped, session 73 |
| `dawitcp` (W7) | CPU | 0.19–0.23 ms | shipped, session 73 |
| `dawitcg` (W8) | CPU | 0.31–0.32 ms | shipped, session 74 |
| **M1 prefetch, whole** | **CPU** | **0.98 ms** | **measured this session — the largest single article in the M1 path** |
| **M1 witness, live COMPARE body** | **CPU** | **0.40–0.46 ms** | **measured directly this session; was carried as 0.896 ms by subtraction** |
| `pfhint` (the correct cache level) | CPU | **NOT MEASURED** | gate written and armed; §5 |
| W3 (the 192-byte cap) | CPU | population **80 521 lines/frame**; prize NOT MEASURED | §6 |
| `imgskip` | GPU | 1.142 ms | a ceiling, not a patch |
| C2 (dirty sub-range) | GPU | 0.252 ms | unexamined |

**Shipped on the CPU axis across sessions 72–74: 1.01–1.07 ms. This session shipped nothing** and
instead corrected the map: the article the programme was about to spend a session on is half the size
it was recorded at, and the article beside it — which nobody had ever measured alone — is twice as
large as any of them.

**The conclusion, sharpened.** 60 FPS by the median needs the GuestGpu thread at its sequential
mutating floor, and that floor is 22.4 ms = **44.6 FPS**, so **M4 cannot reach 60 FPS alone** — but
M4's second question came back POSITIVE where the first came back negative: at slice granularity the
boundary never breaks a render pass, never shares a register context, and divides the frame into four
balanceable units. The single shared `CommandScheduler` and its single-producer `CommandRecorder` are
now the whole of what stands in the way, and they are named at exactly 15.8 % of boundaries.
