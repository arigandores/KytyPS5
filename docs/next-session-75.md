# Session 75 — prompt

Session 74's commit is **b8fd302** on `merge-upstream`, base `ca2a8ae`.
Installed binary — **`017FC03107D569CA047E24F802CCCE0D9187A21AFF747EE7A0F622D8E42631C3`**
(short `017fc031`), 23 555 584 bytes. Harness — **`C:/kyty/s74`**, port it to `C:/kyty/s75`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (today 30.5). Session 74
killed both patches session 73 left ready, answered M4's transport question negatively **by
measurement**, and shipped **0.31–0.32 ms of CPU** from the M1 witness's clean loop.

Every number below is from **`C:/kyty/s74/FACTS.md`**, the single source of truth.

## 0. Read first

1. `C:/kyty/s74/FACTS.md` in full, then `C:/kyty/s74/README.md` (the "Standing traps" section).
2. `C:/kyty/s73/recon73/witness-clean.md` — before touching the live loop, which is now the largest
   named CPU article that does not need M4.
3. `C:/kyty/s72/FACTS.md` §3 (the witness split by loop) and §8 (the three serialisers).

**Harness:** port `C:/kyty/s74` → `C:/kyty/s75` with the roots rewritten. Copy `.txt`/`.json`
**byte-exact**. `gates_base.txt` pins **97 names — 82 gates and 15 knobs, 1072 bytes**, with
`fslean=0` (without it 137 counters go silent), `imgfuse=1`, `dawitcp=1`, **`dawitcg=1`**,
`dawitcgcheck=0`, `dawitfb=0`, `dawitloop=0`, `cleardec=0`, `m4baton=0`.

## 1. What is settled — do not reopen

* **W8 shipped and accepted.** `dawitcg=1`: −0.31…−0.32 ms of CPU wall (`cg74b`, 116 pairs,
  t = −11.84, guards 10 PASS), `da_cl_miss` 15 140.6 → 1 406.3, `da_cl_bad` 0 over ~98 million
  self-checks, two acceptances with video and 0 one-frame glitches. **The clean loop is spent**:
  its residue is 1 402–1 408 misses a frame at 25–40 ns = 35–56 µs, below the stand.
* **M4's transport is answered NEGATIVELY.** 94.38 % of hand-offs at L=32 and 92.94 % at L=128 fall
  inside an open render pass, the ratio does not fall with L, and the boundaries collapse onto
  **~12.5 submission slices a frame that no L can move**. `cram_write` = 0, so the register fork is
  6 803 bytes. **The next M4 question is the submission structure, not the transport.**
* **`clr_none` is closed.** `clrwide` is unsound (the fill's remainder is written by nobody) and its
  reachable population is ≤ 0.849 fills/frame, not 3.776 — `clr_over` is an image count summed over
  declined fills, and 100 % of it comes from one fill.
* **The between-run GPU spread is the upload COUNT** at 517–564 µs per upload, with identical
  rendered content. **The DRS rung does not always latch** — whether a run latches is the variable.

## 2. The work, by prize

### 2.1 The live loop, 0.896 ms — the largest article left that does not need M4

Three candidates named by session 72 and still unwritten, all in `VerifyWitness`
(`pipelineCache.cpp:582-667`) and its readers:

* **W3** — `PrefetchVectorData`'s 192-byte cap.
* **W4** — prefetch with a real distance rather than a fixed one.
* **W5** — `SameRecordedWords`' 4-byte compare.

`dawitptr` took 17 % of this half in session 72 (0.152 ms). The live loop runs **54 912.6 runs /
392 386.6 words (88.4 % of all compared words)** against the clean loop's 27 737.4 / 51 269.3.

**Do what sessions 73 and 74 both did: price it before writing it.** A counter that says how many
words a candidate would actually skip costs one base run and can kill the candidate outright — it
killed W6 (`da_cl_fb` read exactly 0) and it sized W8 to within 0.03 % before a line of the table
existed. Do NOT write a gate first.

### 2.2 M4, second question: the submission structure

The fork is dead at the transport, but the reason is now a **number**, not a wall: hand-offs land in
an open pass because a range boundary is chosen by a draw budget while a pass boundary is chosen by
the guest's PM4. The open question is whether the **submission slices** — 12.42 at L=32 and 12.55 at
L=128, invariant in L — are themselves state boundaries. If a slice boundary is always outside an
open pass, a fork at slice granularity has 12.5 hand-offs a frame and zero pass breaks, and the
splice tax is 12.5 × 11.3-11.8 µs ≈ 0.14 ms.

**Next measurement, one base run, no gate:** count slice boundaries and how many are taken with a
render pass open — the same pair of counters as `rng_total`/`rng_inpass`, moved from
`ProcessPm4Baton` to `CommandProcessor::Process` (`graphicsRun.cpp:979`, `ProcessPm4(execution, 0)`),
so it works at `m4baton=0` and costs nothing. `C:/kyty/s74/patch_m4_range_fixed.py` is the model.

### 2.3 Free in the same runs

* **The wall cost of the 137 counters.** Session 73's named method is **void** — the binary is gone
  and between-run comparison is forbidden. Use one ABBA on **`fslean=0|1`** instead: it silences
  every counter past `Counter::LogNs` in-run. It measures the ACCUMULATE half only (`Scope`'s
  `NowNs()` is gated by `TimingsEnabled()`), so report it as a lower bound.
* **The external C3 closure** `c3_pop == img_skip` — one 120 s run with `imgskip=1` pinned, then
  `check_s71_counters.py`. **Not run for four sessions.**
* **Is W8's `gpu_busy_us` rise really frame packing?** One `KYTY_GPU_TIME` run per arm, comparing
  `GpuTime-kind` shares rather than per-interval absolutes. NOT VERIFIED today.
* **Why the upload count gyrates 14.9–20.0 per frame** — `imgwhy.py` on two runs at opposite ends.
* **Why the DRS rung latches** — one 300 s base run with `KYTY_POKE="27e46c:909090909090"`.
* **`0x53be70000`'s registration lifetime**: an image with exactly that base and size exists on
  ~23 % of frames and is absent on the rest, toggling almost every frame. A READING question.
* **Gate `dawitfb` is dead code with an empty population** and can be deleted.

## 3. Do NOT

**New, from session 74:**

* **`PATCH_DRY=1` checks anchors, not compilation.** It passed on a patch that then failed to build,
  after the files were already edited. Block-scope `namespace FS = ...` does not reach a function
  above it; class members need qualifying from a free function.
* **Do not rebuild between the acceptance run and the final answer, for any reason.** A
  comment-only rebuild changed the installed hash and would have failed guards check 10 on the very
  run that accepted the ship.
* **Do not quote a counter's name as its attribution.** Read the increment site. `clr_over` cost
  session 73 an entire design because it is an image count summed over declined fills.
* **Do not tag-invalidate nothing and clear everything.** A persistent table whose witness moves
  tens of times a frame must bump a key, not memset 4096 entries inside the render mutex.
* **Do not bind anything in `ShaderReadCache`'s constructor that only GuestGpu uses** — the four M1
  workers construct one too.
* **Do not write a self-check without a line cap.**
* **Do not quote session 74's stand.** `aa74a` was contaminated (Slack restarted itself:
  +0.334 % bias, t = +2.57, check 6 FAIL). Both decisions came from the measuring run's own 2·SE.

**Carried, all in force:**

* **Never compare between runs** — this session's own spread on identical configurations is 7.3 %
  on `cpu/draw` and 27.75–31.42 FPS.
* **Confirm a gate fired by a counter in the run, never by the launcher.**
* **Start an ABBA schedule at 1800, analyse from 2100.**
* **Do not set `fslean=1`** in a measuring run other than the one that measures it.
* **Never ship `dawitloop`. Never ship `dawitness=0`. Never write an epoch witness for M1's word
  comparison. Never build a shared head for the record ring.**
* **Do not run any other work on the machine during a measuring run** — and note that the agent
  tooling itself is resident on this host and is the likeliest cause of session 74's check-6
  failures.
* **Do not give an estimate as a measurement.** No number → write "NOT MEASURED" and name what
  would give it.

## 4. The arithmetic

**Today** (`acc74a`): CPU **32 385 µs**, GPU **14 832 µs**, wall **32 813 µs**, **30.48 FPS**.
CPU is the wall in 97–100 % of game frames, at about twice the 16.667 ms budget.

| article | axis | measured | state |
|---|---|---:|---|
| `dawitptr` + `daepceil` | CPU | 0.33 ms | shipped, session 72 |
| `imgfuse` (C1) | GPU / CPU | 1.268 / 0.182 ms | shipped, session 73 |
| `dawitcp` (W7) | CPU | 0.19–0.23 ms | shipped, session 73 |
| **`dawitcg` (W8)** | **CPU** | **0.31–0.32 ms** | **shipped, session 74** |
| M1 witness, live loop | CPU | **0.896 ms** | **W3/W4/W5 unwritten — §2.1** |
| C2 (dirty sub-range) | GPU | 0.252 ms | unexamined |
| `imgskip` | GPU | 1.142 ms | a ceiling, not a patch |

**Shipped on CPU across sessions 72–74: 1.01–1.07 ms against a deficit of 15.7 ms — 6.4–6.8 %.**

**The honest statement of the task.** The live loop is 0.896 ms and is the last large article
reachable without M4; everything after it is M4, and M4's transport is now closed by measurement.
What is NOT closed is whether the **submission slice** is a state boundary (§2.2) — that is one base
run and two counters, and it is the cheapest thing in the programme that could still change the
answer about 60 FPS.
