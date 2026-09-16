# Session 79 — the prompt

Session 78's commit is on `merge-upstream`. **No source code changed in session 78** — every run sat
on session 77's installed binary `39306a9f95db805a…`, whose `.text` is byte-identical to
`79680f59`'s (`90c5653d90a0f265c69c7b2d97b5e6e9cd7436ee0000d7963d0a217370d9aeb0`). Harness —
**`C:/kyty/s78`**, port it to `C:/kyty/s79`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (today 28.51; session
77's acceptance run read 31.23 on the same machine code — that difference is the subject below).

Session 78 did not find the variable behind τ. It did something more useful: it showed that τ is
**not an error bar at all**, and it refuted its own best candidate with its own manipulation.

## 0. Read first

1. `C:/kyty/s78/FACTS.md` — the single source of truth. **§9 first**: the report was rewritten after
   an independent audit found two fatal and fifteen serious errors in its first draft, and every
   retraction is listed there. Then §2 (the result) and §6 (the prediction scoreboard).
2. `C:/kyty/s78/README.md` — standing traps.
3. `C:/kyty/s78/pred/01…08` — the pre-registrations. **Do not edit them.** Their `mtime == ctime` is
   the only anchor the ordering has, and the `WRITTEN <time>` line inside files 03–08 is wrong.
4. `C:/kyty/s78_audit/audit_results.json` — the four audit reports in full, if you want the
   arithmetic behind a retraction.

**Check the byte count of anything large you read.** Reading through the rtk-rewritten shell
truncates silently.

**Harness:** port `C:/kyty/s78` → `C:/kyty/s79`, roots rewritten, `.txt`/`.json` **byte-exact**.
`gates_base.txt` pins the same **99 names — 83 gates and 16 knobs, 1092 bytes**, sha256
`4724bf812e8d095f21dc89b0e324fcf156e30d2614edcc35bb1623f9fe5f8c4f`.

## 1. What session 78 established

On byte-identical `.text`, at rendered area 2007.56–2008.03 Kpx, with every work counter flat to
0.2–0.4 % (`gbar` 0.036 %, `draws` 0.262, `da_hit` 0.295, `da_pf_b` 0.326, `b_texn` 0.334):

| run | arm0 (`pfhint=0`) | arm1 (`pfhint=1`) | effect | arm0 `da_take_us`/take |
|---|---:|---:|---:|---:|
| `pfh78f` | 31 567.2 | 31 435.5 | **−131.7 ± 91.3** | 289.0 ns |
| `pfh77a` | 31 941.9 | 31 251.7 | −690.2 ± 87.8 | 311.7 |
| `pfh76c` | 32 205.4 | 31 948.1 | −257.3 ± 133.5 | 311.7 |
| `pfh77d` | 32 586.5 | 31 852.2 | −734.3 ± 103.8 | 326.4 |
| `pfh78b` | 32 675.1 | 31 589.4 | −1085.7 ± 94.3 | 392.4 |
| `pfh78d` | 32 923.6 | 31 760.9 | −1162.7 ± 84.6 | 387.8 |
| `pfh78c` | 32 977.5 | 31 679.4 | **−1298.1 ± 83.1** | 372.3 |

* **arm0 sd 525.8 µs, arm1 sd 241.9 µs, ratio 2.17** — but Pitman–Morgan on correlated variances
  gives **t = +2.25 on 5 df, p = 0.074**. Suggestive, not established.
* **63.7 % of the arm-0 spread is inside `da_take_us`** (2489.8 → 3388.0 µs a frame, 30.5 %) at an
  identical 8614–8639 takes over an identical 12.50–12.54 MB offered.
* **Within a run the EFFECT is stable and the BASELINE is not** — median half-to-half shift 34.9 µs
  against 139.6 µs (max 501.0), and the within-run baseline moves pass through the gate untouched.
  **So the run's total `cpu_gpu_us` is a proxy, not the quantity.**
* **A/A on this binary: +24.8 ± 75.8 µs, t = +0.45**, bracketing timer 340.32 vs 340.58 ns. The
  estimator is unbiased at ±75 µs. (Two of the three historical A/A runs are area-void and must not
  be quoted; the only valid one is `aa69a`.)
* `pfhint` random effects over the seven: **−767 µs [−1098, −436]**, I² = 98.9 %, τ = 445 µs.
* "`pfhint` removes 76 % of the run-to-run baseline swing" is **95 % CI [31, 121] pp** and is an
  **interpretation** — a between-run OLS on seven runs, chosen after seeing them.

## 2. What is settled — do not reopen

* **`cap78b` answers session 77's audit item C4 the other way.** Without `mutsite`/`pxstat` it reads
  −1.586 % (−502.5 ± 99.9 µs), *larger* than `cap77a`'s −1.305 % with the instrumentation. The
  localisation was not inflated by its own timers.
* **The eleven-vector prefetch block alone suffices for `pfhint`'s win.** With the entire guest-line
  population (`dawitptr=0`, arming proved by `da_direct` present and exactly 0) deleted from both
  arms, it still buys −919.4 ± 105.9 and −1116.5 ± 89.2 µs.
* **The prefetch populations are the other way round from session 78's first draft:** the
  eleven-vector block issues `da_pf_cap_b`/64 = **184 734 a frame (21.4 per take)** against the
  guest-line loop's **54 906**. It is 3.36× the larger, not 192× the smaller.
* **`pfcap` must be split by binary.** `cap76a`/`cap76b` ran on `240edc02`, whose `pfcap=1024` arm
  took the runtime overload clang unrolls by eight. Same-code `pfcap` is **two runs**: `cap77a`
  −381.8 ± 79.8 and `cap78b` −502.5 ± 99.9, random effects −438 [−557, −320].
* **Image-upload traffic is not the mechanism P2 described** (the effect went the wrong way), **but
  P2's own contrast is NOT RESOLVED**: +29.2 µs inside its pre-registered ±250 µs band.
* **The GPU axis** — still ~8–10 µs of wall. Not until CPU is below ~18 ms.

## 3. The work, by prize

### 3.1 Clear or convict the CPU sampler — do this FIRST, it is the cheapest thing on the list

Session 78 added `C:/kyty/s78/cpuclk.py` to the harness and ran 13 of its 15 runs with it. The first
draft cleared it on the strength of a **void** run; corrected, **the single valid run without it
(`pfh78f`) carries the smallest effect of the session, −131.7 µs, smaller than every run that had
it.** n = 1 pointing at it.

**Two `--no-cpuclk` `pfhint=0|1` ABBAs, pre-registered, before anything else.** If they land at
−0.5…−1.3 ms like the sampler runs, it is cleared and 13 runs of session 78 are rehabilitated. If
they land near −132 µs, the harness itself has been the variable and every session-78 number needs
re-reading. Either answer is worth more than any gate on the list. Expect ~1/3 of `pfhint` runs to
go void.

### 3.2 The variable behind the 1410 µs baseline swing

Excluded or disfavoured: the DRS rung, thermal state, the `pfcap` state, biased pair-dropping,
per-pair covariates, pace, image-upload traffic (manipulated), an error-bar artefact, within-run
drift, an ABBA order effect, and any run-level *multiplicative* factor.

Remaining, in order:

1. **the CPU sampler** (§3.1);
2. **host background state** — now recorded in `pre_run['host']` on every run, **never yet varied
   deliberately**. Figma was resident in all three low-effect session-77 runs and absent from all
   three high-effect ones; Slack ×2 and Telegram were unique to `pfh76c`. Two runs, one dirty host
   and one clean, pre-registered on process *identity* not count;
3. **host-heap layout.** The state is re-rolled on every process start and changes the price of
   memory-bound work by 36 % while changing the amount by 0.3 %. Every log already prints one
   fingerprint (`RecordThread: started recorder=0x…`) and the sixteen on disk sit in sixteen
   different L1 sets — but ranking runs by one of thirty-two candidate bit-fields reproduces any
   ordering with p ≈ 0.59, so **this must be tested prospectively, never fitted.** *What would
   measure it:* ~15 lines and 11 gauges (`FrameStats::Gauge`, `frameStats.h:969-975`) recording the
   host addresses of the eleven prefetched vectors and the witness backing, then three runs with the
   prediction written down first.

### 3.3 `mh_bind_us` — the biggest untouched CPU item, now with prices

`bind78a` lit every fine-grained timer for the first time (they read exactly zero in every other run
on disk, because the harness runs `KYTY_FRAME_TRACE=lite`). On the settled window:

    d_bind 13 215.3 = b_buf 4640.3 (ob_us 4347.6, bb_sync 3206.2) + b_tex 3339.9 (b_view 464.8)
                    + bb_find 651.9 + b_smp 302.8 + bb_upload 268.0 + residual 4012.3

69.8 ns per texture resolution (47 884/frame), 89.8 ns per `ObtainBuffer` (48 427/frame), 92.6 ns
per `FindTexture` (5017/frame). **The ordering of `b_buf` against `b_tex` is NOT established**:
`Scope` overhead scales with the count of nested scopes, `b_buf` encloses ~96 900 a frame against
`b_tex`'s 5017, and the two cross at c = 14.1 ns inside a 7–15 ns bracket. **Resolving that costs
one count argument on each of `bb_sync`'s two `Scope` sites plus a `Scope`-cost calibration**, and
it decides which of two ~4 ms blocks to attack. Existing zero-code levers with arming counters:
`texmemo2=0|1` (`texmemo_key_miss`), `smpmemo=0|1` (`smp_miss` 6674/frame).

### 3.4 Free, already paid for

* **`pfcap` has only two same-code area-valid runs.** A third is worth more than a new gate, and
  `pfcap` runs are cheap — though `cap78a` became the first ever to fail the area gate.
* **P2's `imgskip` contrast needs two more runs a side** to be resolved rather than abandoned.
* **The share the guest-line prefetch population carries** is 4 %, 25 % or 11 % [−88, +109] %
  depending on the estimator.
* **Anchor the pre-registration.** Have `enter_scene.py` record the sha256 of the pre-registration
  file in `<tag>.json` at run start. Session 77's audit item C10 is still not discharged — only a
  filesystem mtime anchors the ordering.

## 4. Do NOT

**New, from session 78:**

* **Do not run a manipulation without a same-session control.** The `imgskip` finding survived
  exactly until the control was taken and landed between the two treated runs.
* **Do not quote a void run, once, anywhere.** It inverted a conclusion in the first draft.
* **Apply your pre-registered decision rule, do not merely publish it.**
* **Do not drop a pre-registered exclusion because the data later look good.** `PLAN.md` §0a
  excluded two runs before run 1; the draft built its tightest claim on them.
* **Relabelling a regression does not remove mathematical coupling** — `arm1 ≡ arm0 + effect`.
  Quantify the coupling instead.
* **2·SE is not a 95 % interval at small n** (t = 2.571 on 5 df, 4.303 on 2).
* **A perfect correlation over four points has an exact permutation p of 0.042 — the floor.**
* **"Shares, not absolutes" does not protect a nested timer**: `Scope` overhead scales with the
  count of nested scopes, not their duration.
* **A counter with no count counter has no unit price**, and a `Scope` at two call sites is not one
  function's time.
* **Compute on the settled window, n ≥ 2100.**
* **`gen_gates.py --with` keeps the FIRST `--with`, not the second.** Write `--with a=1 b=1`.
* **Take the prediction's timestamp from the clock, and never edit a pre-registration afterwards.**

**Carried, all in force:** never compare between runs; confirm arming by a counter; start at 1800,
analyse from 2100; do not substitute a criterion; never ship `dawitloop` or `dawitness=0`; do not add
a Knob enum entry anywhere but immediately before `Count`; do not run other work on the machine
during a measuring run; write the prediction down first and have an independent agent attack the
result afterwards — that is what caught session 78 seventeen times.

## 5. The arithmetic

**Today** (`acc78a`): CPU **32 643 µs**, GPU **13 310 µs**, wall **35 069 µs**, **28.51 FPS**.
`acc77a` read 31 327 / 14 507 / 32 025 / 31.23 **on the same machine code**.

| article | axis | measured | state |
|---|---|---:|---|
| **the baseline swing** | CPU | **1410 µs at identical work** | **the finding; variable NOT IDENTIFIED** |
| `pfhint` 0 → 1 | CPU | −132 … −1298 µs, RE −767 [−1098, −436] | 7 valid runs, I² = 98.9 % |
| `pfcap` 192 → 1024, same code | CPU | −438 µs [−557, −320] | **2 valid runs** |
| fraction of the swing `pfhint` removes | — | 76 % [31, 121] pp | INTERPRETATION, n = 7 |
| A/A on this binary | — | +24.8 ± 75.8 µs | the estimator is sound |
| where `pfhint`'s win lives | — | the eleven-vector block suffices | 2 valid runs |
| `mh_bind_us` interior | CPU | `b_buf` 4.64, `b_tex` 3.34 ms/frame | ordering undetermined |
| the CPU sampler | — | **not cleared, n = 1 against it** | **§3.1, do this first** |

**The honest statement of the task.** The programme has spent seven sessions shipping prefetch and
memo gates and quoting each as a number. Session 78 showed that the number does not exist: the same
gate is worth 0.13 ms when the machine is in one state and 1.30 ms when it is in another, the state
changes on every process start, and it is worth up to 1.4 ms a frame — as much as everything shipped
since session 72. **60 FPS still needs about 15 ms off the CPU path, and until the state is named,
the programme cannot tell how much of what it has already shipped it actually has.** The cheapest
next step is also the most uncomfortable one: find out whether the harness itself has been the
variable.
