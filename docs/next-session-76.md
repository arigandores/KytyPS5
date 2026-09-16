Session 75's commit is **dd7926f** on `merge-upstream`, base `876a3b0`.
Installed binary — **`7026D06B0601F6F0B5983A08155549FB3C1F38D22F6B788BE5C1BA6F0191204D`**
(short `7026d06b`), 23 558 656 bytes. Harness — **`C:/kyty/s75`**, port it to `C:/kyty/s76`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (today 28.0–30.5).
Session 75 shipped nothing and instead **corrected the map**: the article the programme was about to
spend a session on is half the size it was recorded at, the article beside it is twice as large as
anything ever shipped, and two of the session's own runs turned out to be invalid for a reason no
guard checks.

Every number below is from **`C:/kyty/s75/FACTS.md`**, the single source of truth.

## 0. Read first

1. `C:/kyty/s75/FACTS.md` in full, then `C:/kyty/s75/README.md` (the "Standing traps" section).
2. `C:/kyty/s75/recon75/w3w4-prefetch.md` and `live-residue.md` — before touching the prefetch.
3. `C:/kyty/s75/FACTS.md` §5 **before planning any A/B at all**. It changes how runs are ordered.

**Harness:** port `C:/kyty/s75` → `C:/kyty/s76` with the roots rewritten. Copy `.txt`/`.json`
**byte-exact**. `gates_base.txt` pins **98 names — 83 gates and 15 knobs, 1081 bytes**, with
`fslean=0`, `imgfuse=1`, `dawitcp=1`, `dawitcg=1`, **`pfhint=0`**, `dawitcgcheck=0`, `dawitfb=0`,
`dawitloop=0`, `cleardec=0`, `m4baton=0`.

## 1. THE RULE THAT CHANGES HOW YOU RUN, read this before anything else

**No guard catches an arm-to-arm rendered-area difference, and it silently invalidated two runs.**
When the DRS rung oscillates, its episodes (median 24–62 flips) alias against the 30-flip block
period of the schedule and the two arms render different numbers of pixels while drawing the same
number of draws. `cpu/draw` then compares two resolutions, not two arms. Check 3 compares the
**gauges** `rt_w`/`rt_h`, which are the output target and read 3840×2160 whatever the rung does — it
**PASSED on both void runs**. Check 3b gave only an advisory WARN.

    python C:/kyty/s76/area_series.py <tag> --root C:/kyty/s76
    python C:/kyty/s76/area_matched_ab.py <tag>

**Run this on EVERY ABBA before quoting its number.** Session 75: `dwl75a` and `dpf75a` matched
117/117 and 120/120 at |Δ| ≤ 0.106 %; `pfh75a` matched 75/118 and `pfh75b` only 28/119.

**And the stand degrades across a session, tracking the GPU's thermal state.** In run order:
high-rung share 0.0 / 0.0 / 28.9 / 66.4 %, mean temperature 67.8 / 69.1 / 69.8 / 71.0 °C, mean power
76.3 / 78.2 / 81.0 / 84.8 W, 2·SE on `cpu/draw` 0.216 / 0.221 / 0.728 / 0.886 %.
**TAKE THE DECISIVE ABBA FIRST, ON A COLD MACHINE.** This is also the first named candidate for
session 74's open "why does the rung latch" — a HYPOTHESIS, NOT MEASURED.

## 2. What is settled — do not reopen

* **The M1 witness's live COMPARE body is 0.40–0.46 ms**, measured directly (`dwl75a`, 122 pairs,
  `cpu/draw` −1.249 % ± 0.216 %, t = −11.55, `da_take_us` −407.4 µs corroborating). The 0.896 ms the
  programme carried for three sessions was `1.929 − 1.033`, a subtraction of two ABBAs from two
  different runs on a session-72 binary.
* **The M1 prefetch is worth 0.98 ms of CPU per frame** (`dpf75a`, 125 pairs, `daprefetch=1|0`,
  +3.064 % ± 0.244 %, t = +25.14, work 0.001 % apart). The largest single measured CPU article in
  that path.
* **Every `_mm_prefetch` in `pipelineCache.cpp` emits `PREFETCHT2`, not `PREFETCHT0`**, because
  `winnt.h:3649` defines `_MM_HINT_T0` as 1 unguarded and wins over clang's 3. Proved three ways
  (`FACTS.md` §3.2). Gate `pfhint` selects the intended form; **its prize is NOT MEASURED**.
* **M4's second question is POSITIVE where the first was negative.** A submission-slice boundary is
  never inside an open render pass (`slc_inpass` 0.000 over 6467 frames), almost never on the same
  `CommandProcessor` (0.011), already turns the command buffer over at 84.2 % of boundaries, and the
  frame's work sits in **four substantial slices** — exactly 3.000 of 1024–2047 items and 1.000 of
  512–1023. 8.001 independently schedulable units a frame.
* **M4 cannot reach 60 FPS alone.** The sequential mutating floor is 22.421 ms = **44.6 FPS**.
* **Session 74's "zero internal hand-offs at L=512" is withdrawn**: 21.0582 ranges/frame against a
  ~12.5 slice count, i.e. ~8.5 internal hand-offs.
* **The C3 closure `c3_pop == img_skip` is CLOSED BY READING** — a tautology of the current tree.
* **W5's premise is dead**: clang fully unrolls `SameRecordedWords` at the project's `/O2`.

## 3. The work, by prize

### 3.1 `pfhint` — one ABBA, and it must be the session's FIRST run

The gate is written, applied, armed and proved (`pf_l1` 8626.306 against `da_hit` 8626.657 =
99.996 %). It defaults to 0 and at 0 the emitted instruction is today's bit for bit. All that is
missing is a valid measurement. Take it as run one, on a cold machine, and accept it only if
`area_matched_ab.py` matches ≥ 90 % of pairs.

Note the honest prior: `pfh75a`'s 75 matched pairs read **+0.375 % ± 0.429 %** (T0 slightly WORSE),
which is physically plausible — `prefetcht0` puts ~285 000 lines a frame into L1 and may evict the
working set the compare loop is streaming. A negative result here is a real result and should be
recorded as one, not re-run until it changes sign.

### 3.2 W3 — the 192-byte cap, population measured, prize not

`da_pf_b` 12 535 382 against `da_pf_cap_b` 7 382 040 bytes a frame: the cap truncates
**5 153 342 bytes = 80 521 cache lines a frame, 41.1 % of what is offered** (per take: 1452 B
offered, 855 B prefetched, 597 B truncated). That is 143× the floor session 75's adversary derived
and infinitely more than the reader's claimed zero.

**Next measurement:** a knob on the cap (`192` → 256 / 384 / unbounded), ABBA'd against 192. It
rides in the same binary as §3.1 and can share a session. Predict the reading in advance.

### 3.3 W4 — untouched, and now the only unexamined lever on a 0.98 ms article

The vector prefetch in `AheadTake` has ~200 instructions plus three out-of-line calls of distance
before its first consumer. The **guest-line** prefetch at `pipelineCache.cpp:772` is the tight one:
run[0] gets ~43–51 instructions of distance and the LAST run gets none. Session 75's adversary
established that software-pipelining that prefetch into the compare loop at `:776-800` needs **no
publish-side structure** — contrary to the reader's claim. That is the cheapest unexamined thing
left in the area.

### 3.4 M4 — what is actually in the way now

Everything at the boundary is clear. What remains is serialiser (3): one `CommandScheduler`
(`renderContext.h:82`) handing one `CommandBuffer` and one single-producer `CommandRecorder`
(`commandRecorder.cpp:326` kills the emulator on a second producer) to all 57 processors, at the
**15.8 %** of slice boundaries that carry no tick change. That is a design question, not a
measurement — but it is now the ONLY one, and the measurement that framed it cost twelve counters
firing 12.7 times a frame.

Read `slc_newcb` against `slc_inpass` first: both are already in the tree and the un-flushed 15.8 %
are a named, countable population.

### 3.5 Free in the same runs

* **The wall cost of the 738 counters** — one ABBA on `fslean=0|1`, which silences 712 of 738
  in-run. **Expected artefact, state it in advance:** `rt_att` is index 547 and goes silent, so
  guards checks 3 and 3b lose their arm1 population — a property of the arm, not of the machine.
  It measures the accumulate half only (`Scope`'s `NowNs()` is already off at `KYTY_FRAME_TRACE=lite`),
  so it is a LOWER bound.
* **`0x53be70000`'s registration lifetime** — no code needed:
  `enter_scene.py lif76a --hold 150 KYTY_IMAGE_LIFETIME_TRACE=1 KYTY_IMAGE_LIFETIME_MIN_KB=8192
  KYTY_CLEAR_TRACE=1`, joining `ImageLife:` on `BufferFillTrace:` by frame. Predict `line=` as one of
  {980, 1016, 1068, 1072, 1095, 2078, 3203, 3331} and read `bytes=` before concluding anything.
* **Why the DRS rung latches** — two base runs of identical configuration, one from cold and one
  after an hour of load, comparing the high-rung share. Session 75 gives the correlation; this gives
  the measurement.
* **Gate `dawitfb`** is still dead code with an empty population. The deletion plan is written
  (`recon75/free-items.md`) and was deliberately not applied.

## 4. Do NOT

**New, from session 75:**

* **Do not quote an ABBA before `area_matched_ab.py` has matched its pairs.** Two runs passed every
  guard and were invalid.
* **Do not take the decisive ABBA late in a session.** The stand degrades with the GPU's thermal
  state, monotonically, by a factor of four.
* **Do not subtract two ABBAs from two runs and call it a measurement.** 0.896 ms lived three
  sessions that way.
* **Do not read a gate's delta without checking what the gate LEAVES RUNNING.** `dawitloop=2` skips
  the compare body but the prefetch pass at `:769-775` sits before the skip test at `:777` — which is
  exactly why the direct number is smaller than the subtraction, and exactly what lets the two
  numbers decompose the area.
* **Do not trust an intrinsic's constant without compiling for it.** `_MM_HINT_T0` is 1 in
  `pipelineCache.cpp` and 3 wherever clang's header wins; `winnt.h` redefines it unguarded. Check by
  compiling the file's real include prefix with a `static_assert`, then disassemble.
* **Do not write a new gate when a knob in the tree already answers the question.** `dawitloop=2`
  and `daprefetch=0|1` needed no code and no rebuild, ran on the installed binary, and corrected the
  map more than any patch could have.
* **Do not add a `Gauge` without editing the format string and the argument list together** — that
  is the usual way the edit breaks. A histogram of counters usually says more anyway.

**Carried, all in force:**

* **Never compare between runs.**
* **Confirm a gate fired by a counter in the run, never by the launcher.**
* **Start an ABBA schedule at 1800, analyse from 2100.**
* **`PATCH_DRY=1` checks anchors, not compilation.** Block-scope `namespace FS` does not reach a
  function above it.
* **Do not rebuild between the acceptance run and the final answer, for any reason.**
* **Do not quote a counter's name as its attribution.** Read the increment site.
* **Do not set `fslean=1`** in a measuring run other than the one that measures it.
* **Never ship `dawitloop`. Never ship `dawitness=0`. Never write an epoch witness for M1's word
  comparison. Never build a shared head for the record ring.**
* **Do not run any other work on the machine during a measuring run** — the agent tooling is
  resident on this host.
* **Do not give an estimate as a measurement.** No number → write "NOT MEASURED" and name what
  would give it.

## 5. The arithmetic

**Today** (`base75a`): CPU **33 237 µs**, GPU **14 699 µs**, wall **35 763 µs**, **27.96 FPS**.
CPU is the wall in 97–100 % of game frames.

| article | axis | measured | state |
|---|---|---:|---|
| `dawitptr` + `daepceil` | CPU | 0.33 ms | shipped, session 72 |
| `imgfuse` (C1) | GPU / CPU | 1.268 / 0.182 ms | shipped, session 73 |
| `dawitcp` (W7) | CPU | 0.19–0.23 ms | shipped, session 73 |
| `dawitcg` (W8) | CPU | 0.31–0.32 ms | shipped, session 74 |
| **M1 prefetch, whole** | **CPU** | **0.98 ms** | **the largest single article in the path** |
| **M1 witness, live compare body** | **CPU** | **0.40–0.46 ms** | was carried as 0.896 ms |
| `pfhint` | CPU | **NOT MEASURED** | gate written and armed — **§3.1, run it first** |
| W3 (192-byte cap) | CPU | 80 521 lines/frame truncated; prize NOT MEASURED | §3.2 |
| W4 (prefetch distance) | CPU | NOT MEASURED | §3.3 |
| `imgskip` | GPU | 1.142 ms | a ceiling, not a patch |
| C2 (dirty sub-range) | GPU | 0.252 ms | unexamined |

**Shipped on CPU across sessions 72–74: 1.01–1.07 ms. Session 75 shipped nothing.**

**The honest statement of the task.** The 0.98 ms prefetch is now the largest measured CPU article
that does not need M4, and three levers on it are unexamined: the cache level (`pfhint`, written and
armed), the 192-byte cap (W3, population measured at 41.1 % truncated), and the distance (W4). All
three ride one binary and one session. M4's boundary questions are all answered positively at slice
granularity and only serialiser (3) is left — but M4 tops out at 44.6 FPS, so it cannot be the whole
answer whatever happens to it.
