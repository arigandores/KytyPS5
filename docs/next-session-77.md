# Session 77 — prompt

Session 76's commit is on `merge-upstream`, base `a86e4a9`.
Installed binary — **`79680F59BDA44AB8357B0E64643658AEE3C0C5C431115C7329F34E4A5F021384`**
(short `79680f59`), 23 563 776 bytes. Harness — **`C:/kyty/s76`**, port it to `C:/kyty/s77`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (today 30.75).

Session 76 shipped two gates. It also **voided three of its own runs, withdrew a headline that was
roughly twice the truth, and retracted a conclusion** — and what corrected it was not a new run but
an adversary applying a threshold the programme had already written down and the session had walked
past. **Read `C:/kyty/s76/FACTS.md` §2 and §5 before anything else.**

## 0. Read first

1. `C:/kyty/s76/FACTS.md` in full — especially **§2 (why three runs are void)** and **§5 (what the
   session got wrong)**.
2. `C:/kyty/s76/README.md` — "Standing traps".
3. `C:/kyty/s76/PREDICTIONS.md` — every prediction with its misses and the retraction, in order.
4. `C:/kyty/s75/recon75/w3w4-prefetch.md` and `live-residue.md` — the W4 reference.

**Harness:** port `C:/kyty/s76` → `C:/kyty/s77`, roots rewritten, `.txt`/`.json` **byte-exact**.
`gates_base.txt` pins **99 names — 83 gates and 16 knobs, 1092 bytes**, with `fslean=0`,
`imgfuse=1`, `dawitcp=1`, `dawitcg=1`, **`pfhint=1`**, **`pfcap=1024`**, `dawitcgcheck=0`,
`dawitfb=0`, `dawitloop=0`, `cleardec=0`, `m4baton=0`.

## 1. THE RULE SESSION 76 BROKE — read before planning any ABBA

**Before quoting any ABBA, compute whole-arm `rt_kpx/rt_att` per arm and compare it to the table in
`area_matched_ab.py`'s OWN HEADER:** +0.00 % quotable, **+1.74 % VOID**, +4.30 % VOID. Session 76
computed its own +2.191 % and never compared it to that table, and shipped against it for most of a
session.

**And ≥ 90 % pair matching IS reachable.** Session 76 pre-registered it, failed it twice, retired it
with a design table computed on the failing run's own area series, and an adversary falsified the
substitute by showing that `pfh75b` — the run session 75 voided — passes all six substituted
criteria. The gate was hit four times the same day, twice at the very period the table said tops out
at 57.6 % (`cap76a` 126/126 and `cap76c` 117/117 at period 30, `cap76b` 231/233, `pfh76c` 109/121).
**It is a rung-quietness detector and it works. If a criterion fails, take another run — do not
substitute the criterion.**

**Cold does not buy rung quietness.** Session 76's cold first run oscillated at 17.7 %; the later,
warmer `cap76a` (69.6 °C, 81.0 W) was dead quiet. Quietness is a property of the run; check it.

## 2. What is settled — do not reopen

* **`pfcap` 192 → 1024 shipped: 0.29–0.31 ms**, two area-clean ABBAs (126/126 and 231/233) agreeing
  0.167 pp apart against a combined 2·SE of 0.225. **A lower bound** — the winning arm carried a
  runtime, non-unrolled loop the shipped path does not.
* **`pfhint` 0 → 1 shipped: 0.25 ms**, ONE area-clean ABBA (`pfh76c`, 109/121, +0.446 %), the first
  `pfhint` ABBA in the programme to pass every stated criterion.
* **DO NOT ADD THE TWO.** Each is an increment measured with the other gate on in both arms, and the
  session's own numbers show they overlap (`pfhint` read −413/−482 µs at `pfcap=192` and −245 µs at
  `pfcap=1024`). The run that tried to measure the total, `both76a`, is **void**.
* **1024 is the cap's operating point**: `pfcap=1024|4096` costs +0.185 % ± 0.169 % with area
  117/117 and 99.9994 % of the offer released. **W3 is exhausted.**
* **The 738 counters cost ≥ 0.22 ms a frame** — lower bound, lowest-confidence number in the record.
* **`0x53be70000` is the DRS low-rung colour target** (1920×1080, fmt 37, bpp 4, 8 847 360 B), with
  one create path (`InsertImage`, line 368), one free path (**`ResolveOverlap`, line 1072**) and a
  **median registration lifetime of 0 frames** — which is why the clear dispatch reads `none` on some
  frames and `ok` on others at the same address and size.
* **M4 tops out at 44.6 FPS** and only serialiser (3) is left. `slc_total` reproduced at 12.804.

## 3. The work, by prize

### 3.1 Confirm `pfhint` — it rests on one run

Four earlier ABBAs of this gate are mutually inconsistent at I² ≈ 97 %, but all four are area-void,
which explains the inconsistency rather than impugning `pfh76c`. **One more `pfhint=0|1` ABBA on the
installed binary, accepted on the same six criteria**, settles whether 0.25 ms stands. If it fails
the area gate, take another run — do not substitute the criterion.

### 3.2 Re-take `pfcap=192|1024` where both arms are compile-time

The shipped `<1024>` path was never itself an arm: `cap76a`/`cap76b` ran on a binary whose 1024 arm
used the runtime overload. On the installed binary both 192 and 1024 are compile-time branches, so
one re-take removes the bias and turns a lower bound into a measurement.

### 3.3 W4 — the prefetch DISTANCE, the last unexamined lever on the 0.98 ms

Session 75's adversary established that the guest-line prefetch at `pipelineCache.cpp:772` gives run
0 about **43–51 instructions** of distance and the **last run none**, and that software-pipelining it
into the compare loop at `:776-800` needs **no publish-side structure**. **Price it before writing
it**, and ask first whether a knob already in the tree decomposes it — that habit produced every win
since session 73.

### 3.4 Where the benefit actually lands — NOT MEASURED, and now conspicuous

`da_take_us` brackets `AheadTake`, which fully contains the prefetch block. It moves for `pfhint`
(−162, −236, −133 µs) and **does not move at all for `pfcap`** (−2.2, +5.4 µs) despite −306 and
−292 µs of wall. The knob is still the only difference between the arms, so causation is not in
doubt — **but nothing localises the gain.** One run at `mutsite=1`, reading `mh_prog_us`/`mh_bind_us`
across the arms, would say whether it lands in `PrepareGraphicsBindings`. That would also tell the
programme whether the next CPU win lives in the binding path rather than the witness path.

### 3.5 Documentation debt left deliberately unfixed

Fixing a comment would change the installed exe's hash after the acceptance run (session 74's trap),
so these were left: `frameStats.h:936-943` still calls `da_pf_cap_b` "the sum of min(bytes, 192)",
and the `pfcap` comments in `gates.h` and `gates.cpp` still say "Default 192 = today" beside a
definition that reads 1024. **Fix them first, before any rebuild-bearing work.**

### 3.6 Free in the same runs

* **An A/A on `pfhint`** (two textually identical arms). Runs that toggle `pfhint` split the DRS rung
  and runs that toggle `pfcap` do not, at comparable CPU deltas. If an A/A still splits the rung, the
  cause is not the gate. This is the cheapest open question in the record.
* **Why the rung moves.** The thermal correlation reproduced (r = +0.894 on temperature, +0.820 on
  power over six runs; ten runs over two sessions now) but is **not monotone within a run**:
  `pfh76a` ran 29.3 / 28.3 / 0.0 / 0.0 / 0.0 / 1.2 / 35.9 / 14.4 / 34.5 / 33.2 by decile from a
  53 °C start. *What would measure it:* two base runs of identical configuration, one cold, one after
  an hour of load.
* **A smaller cap** (384, 512) may buy most of §2's 0.30 ms more cheaply. Needs a compile-time branch
  for the candidate, or the test is unfair the way `cap76c` was.
* **Gate `dawitfb`** is still dead code with an empty population; deletion plan written, not applied.
* **C2 (dirty sub-range), 0.252 ms GPU** — unexamined, and the GPU axis has had nothing since s73.

## 4. Do NOT

**New, from session 76:**

* **Do not quote an ABBA without checking the whole-arm area split against the table in
  `area_matched_ab.py`'s own header.**
* **Do not substitute an acceptance criterion after it fails.** Take another run.
* **Do not add two gates' increments.** Each is measured with the other on in both arms.
* **Do not claim a default path is unchanged without scanning the emitted opcodes.** A knob whose
  default is "today's behaviour" can still change the code generated for that default — a runtime
  bound cost +66 prefetch instructions and compiled cleanly.
* **Do not print a ratio without its population.** A derived per-run file that was never generated
  reads as a zero, not an error; session 76 published a retracted conclusion that way.
* **Report the timer that brackets the changed code with every gate delta.**
* **Do not treat an `fslean` A/B as a normal measurement** — it silences `rt_att`, its own gate.
* **Do not add a Knob enum entry anywhere but immediately before `Count`.**
* **Do not assume a cold machine gives a quiet rung.**

**Carried, all in force:**

* **Never compare between runs.**
* **Confirm a gate fired by a counter in the run, never by the launcher.**
* **Start an ABBA schedule at 1800, analyse from 2100.**
* **A subtraction of two ABBAs from two runs is not a measurement.**
* **Check what a gate LEAVES RUNNING before reading its delta.**
* **Do not trust an intrinsic's constant without compiling for it.**
* **`PATCH_DRY=1` checks anchors, not compilation.**
* **Do not rebuild between the acceptance run and the final answer, for any reason.**
* **Do not quote a counter's name as its attribution.**
* **Never ship `dawitloop`. Never ship `dawitness=0`. Never write an epoch witness for M1's word
  comparison. Never build a shared head for the record ring.**
* **Do not run any other work on the machine during a measuring run.**
* **Do not give an estimate as a measurement.**
* **Write the prediction down before the run**, and **have an independent agent re-derive and attack
  the result afterwards** — that is what caught session 76, and the arithmetic was never the problem
  (every headline re-derived to within 0.0003 pp). Validity was.

## 5. The arithmetic

**Today** (`acc76a`): CPU **32 124 µs**, GPU **14 825 µs**, wall **32 523 µs**, **30.75 FPS**.

| article | axis | measured | state |
|---|---|---:|---|
| `dawitptr` + `daepceil` | CPU | 0.33 ms | shipped, s72 |
| `imgfuse` (C1) | GPU / CPU | 1.268 / 0.182 ms | shipped, s73 |
| `dawitcp` (W7) | CPU | 0.19–0.23 ms | shipped, s73 |
| `dawitcg` (W8) | CPU | 0.31–0.32 ms | shipped, s74 |
| **`pfcap` 192 → 1024 (W3)** | **CPU** | **0.29–0.31 ms** | **shipped, s76; two clean ABBAs; lower bound** |
| **`pfhint`** | **CPU** | **0.25 ms** | **shipped, s76; ONE clean ABBA — §3.1** |
| both together | CPU | **NOT MEASURED** | the run that tried is void; **do not add** |
| cap beyond 1024 | CPU | +0.185 % — costs | measured, closed |
| the 738 counters | CPU | ≥ 0.22 ms | lower bound, lowest confidence |
| M1 prefetch, whole | CPU | 0.98 ms | measured, s75 |
| **W4 (prefetch distance)** | **CPU** | **NOT MEASURED** | **§3.3 — the last lever on the 0.98 ms** |
| where the gain lands | — | NOT MEASURED | §3.4 |
| `imgskip` | GPU | 1.142 ms | a ceiling, not a patch |
| C2 (dirty sub-range) | GPU | 0.252 ms | unexamined |

**The honest statement of the task.** Two of the three levers on the 0.98 ms M1 prefetch are shipped
and the cap is exhausted at 1024, but one of the two rests on a single run and neither has been
localised by the timer that contains it. W4 (distance) is untouched. M4's boundary questions are all
positive and only the single shared `CommandScheduler` remains — but M4 tops out at 44.6 FPS, so
**60 FPS needs the CPU path to keep giving**, and the GPU axis has had nothing since session 73.

**And the lesson session 76 paid for: the programme had a working validity instrument and a recorded
threshold, and still shipped against it for most of a session. Check the instrument first.**
