Session 79's commit is on `merge-upstream`. **No source code changed in session 79** — every run
sat on session 77's installed binary `39306a9f95db805a…`, whose `.text` is byte-identical to
`79680f59`'s (`90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0`). Harness —
**`C:/kyty/s79`**, port it to `C:/kyty/s80`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (acceptance base of
record, restated on the settled window n ≥ 2100: **28.61 FPS**, CPU 32 789 µs, GPU 13 497 µs).

Session 79 answered the question session 78 left and then had its own answers taken apart by its
own audit. Read the audit's conclusions before you read anything else it says.

## 0. Read first

1. `C:/kyty/s79/FACTS.md` — the single source of truth. **§9 first** (what the audit forced, three
   fatal and fifteen serious), then §2 and §3, then §10 (not closed, with the next measurement
   named for each).
2. `C:/kyty/s79/README.md` — the standing traps, which grew by eleven.
3. `C:/kyty/s79/pred/01_sampler.md`, `02_smt.md`, `03_pfcap.md` — **do not edit them.** Their
   sha256 is inside every `<tag>.json` they cover, so an edit is now detectable.
4. `C:/kyty/s79_audit/` — the four auditors' own scripts and block sums, if you want the arithmetic
   behind a retraction.

**Check the byte count of anything large you read.** Reading through the rtk-rewritten shell
truncates silently.

**Harness:** port `C:/kyty/s79` → `C:/kyty/s80`, roots rewritten, `.txt`/`.json` **byte-exact**.
`gates_base.txt` pins the same **99 names — 83 gates and 16 knobs, 1092 bytes**, sha256
`4724bf812e8d095f21dc89b0e324fcf156e30d2614edcc35bb1623f9fe5f8c4f`. Verify the port by re-deriving
session 79 before you use it.

## 1. What session 79 settled

* **The CPU sampler is not the variable.** The pre-registered rule fired on run 1: `nos79a`,
  `--no-cpuclk`, read **−848.3 ± 76.6 µs**, and the three sampler-free runs in existence span
  **757 µs**. Session 78's thirteen sampler runs are rehabilitated.
* **The swing is at least as large as session 78 said**: range **2503 µs**, sd 749 over ten
  area-valid `pfhint` ABBAs on byte-identical `.text`. (The sd increase over session 78's 525.8 is
  F = 2.03 on (9,6) df, p ≈ 0.2 — not significant. Do not quote "1.8× larger".)
* **`pfcap` has three same-code runs at last: −453 µs [−628, −278]**, I² CI [0, 88 %]. And session
  78's two-run figure, restated with the t quantile, **included zero**.
* **At the best state the gate is worth −109 ± 30 µs**, p = 0.0004 — small, not nothing.

## 2. What is settled — do not reopen

* **Session 78's §3.2(3) heap-layout plan measures the wrong object.** The backing is imported in
  27 chunks of 512 MB, so 64 KiB granularity pins bits 0..15 of every `run.backing` identical in
  every run, and `RecordThread: recorder=0x…` is the record thread's arena, which `AheadTake` never
  touches.
* **The 326-counter hunt is not re-run.** It returned nothing over 11 byte-identical runs and
  auditor D asked that it be refused.
* **The four-arm schedule for P2's `imgskip` contrast is ruled out.** `gates.cpp:380-381` silently
  forces ABBA off for `arms != 2`, `:468-469` falls back to plain round robin so every arm has the
  same predecessor, and session 79 measured an **orientation artefact of up to 158 µs
  half-amplitude** (the block after an arm switch is cheaper, in every run including the A/A) which
  ABBA cancels to ≤ 0.9 µs and a round robin does not.
* **Intra-CCD placement cannot be tested against any log on disk.** Nothing records which logical
  CPU a thread ran on; `GetCurrentProcessorNumber` is called at one site and immediately reduced to
  an L3 index, and `da_ccd_x`/`rec_ccd_x` read identically 0 in both arms of all ten runs.

## 3. The work, by prize

### 3.1 Condition on frame time, not on the CPU baseline — do this FIRST, it costs no run to specify

Session 79's single most useful finding is one it did not go looking for:

    corr(effect, arm-0 cpu_gpu_us)  -0.878
    corr(effect, arm-0 da_take_us)  -0.909      (the first two are NOT distinguishable, Steiger p = 0.71)
    corr(effect, arm-0 dt_us)       -0.972
    corr(effect, mean GPU power)    +0.968 ... +0.998     from gpuclk_<tag>.csv, written since session 76

The programme has spent two sessions conditioning gate effects on the run's CPU baseline. **The
run's own frame time predicts them better, and GPU power — a quantity that is not in the CPU path at
all — predicts them about as well.** That is either a much better handle on the state or evidence
that all four are downstream of one thing. Either way the conditioning variable is wrong.

*What to do:* re-derive the table for every `pfhint`, `pfcap` and `dapin` run in the record against
`dt_us` and against `gpuclk` power/clock/temperature, **pre-register frame time as the conditioning
variable**, and then ask what sets frame time at process start. This is a zero-run analysis of data
already on disk, and it should precede every new run of the session.

**Caveat to write into the pre-registration:** these are mutually downstream quantities and n = 10.
Nothing fitted to them is a result; the output is a pre-registered prediction for the runs that
follow.

### 3.2 `dapin` — 0.86 FPS for no code, and an unexplained GPU cost

`dapin=21845` (= `0x5555`, one logical CPU per physical core of CCD0; **decimal in the gate file**)
against the default mask, as a two-arm ABBA with `pfhint=1` in both arms:

    smt79a  -705.7 +- 85.8    dt -2.696 %   30.581 -> 31.420 FPS
    smt79b  -735.3 +- 97.9    dt -2.822 %   30.338 -> 31.216 FPS
    random effects -719 us [-1129, -309] (t on 1 df)

Larger in frame time than `pfcap` and than seven of the ten `pfhint` runs. **But it is not the pure
placement contrast it was designed to be:** nine work counters move reproducibly at t = 10–33,
including **`gpu_busy_us` +1.32 % and +1.95 %** — the only contrast in the record that moves GPU
busy time significantly — plus `rp_begin` +3.6–4.2 %, `rpa_re_kpx` +2–2.7 Mpx/frame, `faults`
+2.3–2.5 %, `prot_pages`, `submits` −1.7 %. Inside `cpu_gpu_us` the win is 39/37 % `da_walk_us`,
18/17 % `da_queue_us`, 4/6 % `da_take_us` and **54–58 % untimed because the harness runs at `lite`**.

*Three things, in order:* **(a)** a third run, because two is below the programme's own rule;
**(b)** one run at `KYTY_FRAME_TRACE=1` to attribute the untimed half — session 79 showed that costs
a run and nothing else; **(c)** an explanation of the GPU rise before any shipping decision.
Shipping needs a **mode** ("one logical processor per physical core of the largest-L3 group",
computed the way `l3_masks` already is), not a raw mask — that is a source change and ends the
byte-identical-`.text` property, so decide the order deliberately.

### 3.3 The CPU sampler as a contributor — NOT RESOLVED, and the design is now known

Session 79's first draft claimed the four sampler runs carry the four highest baselines with no
overlap, p = 0.0048. **Withdrawn.** 21 of 722 arm-0 quantities separate the same groups at the same
p — one of them is the effect itself; stratified within session p = 0.083; and admitting the four
voided sampler runs on a **rung-matched arm-0 baseline** gives +674.9 µs, p = 0.035, ranges
overlapping.

*The design that would settle it:* arm-0 `cpu_gpu_us` pre-registered as the primary endpoint,
randomised sampler assignment, interleaved, **six runs a side**, and **every attempt admitted on a
rung-matched arm-0 baseline regardless of its arm-contrast validity** — because the area gate tests
an arm contrast and the endpoint is single-arm. That last clause is the whole lesson.

### 3.4 A named mechanism nobody has looked at: C-state residency

On the eight `cpuclk` CSVs the harness has written since session 78, against each run's own
rung-matched arm-0 baseline:

    corr(c3_ccd0,       baseline) = +0.914   (+0.936 on the five pfhint runs)
    corr(busy_ccd0,     baseline) = -0.781   (-0.990)
    corr(intr_ccd0,     baseline) = -0.894   (-0.915)
    corr(mhz_ccd0,      baseline) = -0.604   (-0.732), dynamic range 0.9 % against the baseline's 7.7 %

**The slow state is the idler state**: CCD0 spends more time in C3, is less busy, takes fewer
interrupts. That is the opposite of a contention story and it is not a frequency story. n = 5–8 and
all mutually downstream — a screen, not a finding — but it is the first mechanism named for the
swing that is neither refuted nor untestable. A power-plan manipulation (processor idle disable) is
a one-line host change and a pre-registered two-arm contrast.

### 3.5 Free, already paid for

* **Acceptance criterion 1 is vacuous** and has been since session 74: nine of the eleven
  "self-check counters zero" are incremented only inside verify gates that `gates_base.txt` pins
  off. Rewrite it, or turn one verify gate on in one run per session.
* **The guest-clock pacer** (`videoOut.cpp:1188-1206`, EMA α = 0.08, `flip_rate = 0` so the clamp is
  never active, per-arm guest-speed differences 0.3–4.2 % and 0.0 % in the A/A). It is a confound in
  every A/B the programme runs and it has never been tested. One ABBA with the rung forced low in
  both arms, or with the pacer pinned.
* **P2's `imgskip` contrast** is still +29.2 µs inside its own ±250 µs band. Two runs a side, in
  two-arm ABBAs only.
* **The validity gate does drop the pairs where the gate looks best** — 4 of 4 void runs in session
  79, by 20–162 µs. Session 78 declared this refuted; it is not. Quantify the bias before the next
  figure is shipped.

## 4. Do NOT

**New, from session 79:**

* **Do not stop a pre-registered block when its rule fires.** Session 79's fired on run 1, and the
  block still ended one valid run short of its 2+2 design **with three attempts of budget left**.
  Say so in the report if it happens; do not reframe the session's attempt count as the block's.
* **Do not select on an arm-contrast gate and then test a single-arm endpoint.** That is how the
  sampler separation was manufactured.
* **Screen a perfect separation against every other column before believing it.** 21 of 722 did the
  same thing at the same p.
* **A share is a share of something.** When the denominator moves, the share is stale — "63.7 % of
  the swing is in `da_take_us`" became 35.9 %, and the conclusion built on it inverted.
* **"Work is unchanged" needs more than three counters.**
* **A range grows with n.** Compare sds with an F test.
* **τ = 0 and I² = 0 at k = 2 are estimator floors.** Print the interval.
* **A second look at the data that generated the hypothesis is not a confirmation.**
* **Type nothing from memory** — not a timestamp, not an entry time, not a range.
* **Write the pre-registration before the session's own runs, not between them.** Two of session
  79's three were written mid-session and 14 of its 21 scored hits are worth nothing as calibration.

**Carried, all in force:** never compare between runs; confirm arming by a counter or a log line;
start at 1800, analyse from 2100; do not substitute a criterion; never ship `dawitloop` or
`dawitness=0`; do not add a Knob enum entry anywhere but immediately before `Count`; do not run
other work on the machine during a measuring run; `gen_gates.py --with` keeps the **first** `--with`;
a knob value in a gate file is **decimal**; write the prediction down first and have an independent
agent attack the result afterwards — that is what caught session 79 eighteen times.

## 5. The arithmetic

| article | axis | measured | state |
|---|---|---:|---|
| **the baseline swing** | CPU | **range 2503 µs, sd 749, ten runs at identical work** | **variable NOT IDENTIFIED** |
| its best predictor | — | **corr(effect, arm-0 `dt_us`) = −0.972** | §3.1, a screen |
| `pfhint` 0 → 1 | CPU | RE −767 [−1106, −428], I² = 99.1 %, τ = 472 | 10 runs |
| `pfhint` at the best state | CPU | −109 ± 30 µs, p = 0.0004 | 2 runs |
| `pfcap` 192 → 1024, same code | CPU | −453 µs [−628, −278] | 3 runs |
| **`dapin` 0xffff → 0x5555** | CPU+GPU | **−719 µs, +0.86 FPS**, GPU +1.4…1.9 % | **2 runs, not pure** |
| the CPU sampler | — | refuted as the variable; contributor not resolved | §3.3 |
| C-state residency | — | corr(c3_ccd0, baseline) = +0.914 | §3.4, a screen |

**The honest statement of the task.** Session 78 found the swing. Session 79 cleared the harness of
causing it, widened it to 2503 µs, and then discovered — in its own audit — that the majority of it
is **not** in the timer the programme has been watching, and that its best predictor is the run's own
frame time. The programme has been conditioning on the wrong number. **60 FPS still needs about
15 ms off the CPU path**, and the cheapest thing on the list is still an analysis of data already on
disk.
