# Session 91 — the brief

**Session 90 built D1, found it reaches 100 % of its bytes, and then found that the work it was
built to remove has been on the copy pool since session 27.** Read `docs/ROADMAP.md` **§0.1**
first — it still separates *"three routes with a measured ceiling do not reach 60 FPS"* (proved)
from *"60 FPS is unreachable"* (**not** proved). **§0.1 carries a session-90 addendum and §2 D's
D1 paragraph was rewritten end to end**; read them together or not at all.

Session 90's commit is on `merge-upstream`. **Source changed and the binary was rebuilt twice, but
NO default changed**: the installed `kyty_emulator.exe` is `12b0940a00e951bb…`, 23 619 584 bytes,
and both names session 90 added (`bufimp`, `bufimpcheck`) are **0**. Harness — **`C:/kyty/s90`**,
port it to `C:/kyty/s91`.

## 0. Read first

0. **`docs/ROADMAP.md` §0.1 (including the session-90 addendum), §2 D (D1 rewritten), §5 item 4
   and §7.** A is closed by measurement. B sums to 0.7–2.5 ms and has shipped −252 µs in four
   sessions. C is MARGINAL at 514 µs and is not built. **D2 is divided to the bottom. D1 is now
   built and measured, and it is not shipped.**
1. `C:/kyty/s90/FACTS.md` — the single source of truth. **§0.1 FIRST (three defects of my own
   sealed text, one of them inside the file written to repair the first), then §2 (the census),
   §2.1 (the result that needs no contrast), §3 (the A/B that failed admission and its diagnosis),
   §4 and §4.1 (the valid run), §5 (six corrections to this programme's own record) and §7 (all 27
   predictions).**
2. `C:/kyty/s90/README.md` — the standing traps. The three that will bite first: **a byte counter
   printed through the "micros column" is kB, not KiB, and this record misread one for five
   sessions**; **an exact-zero band is legitimate only where the counter is never `Add`ed — an
   arm-labelled window needs a share**; and **`gen_gates.py --out X` without `--with` ignores
   `--out` and rewrites `gates_base.txt`**.
3. `C:/kyty/s90/PLAN.md` **§0 A** — the D1 blocker list, and §0 B, the corrections. It exists; do
   not redo it.

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s90` → `C:/kyty/s91` with a script modelled on
`C:/kyty/s89/s90_port.py` — **written fresh in the SOURCE directory**. It repairs the head of every
`--roots` chain and `area_verdict.py`'s arithmetic `range(90, 70, -1)`. `gates_base.txt` is
**unchanged** — 1092 bytes, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`; `bufimp`, `bufimpcheck` and
`proglap` are deliberately absent from it, which is what gives every new counter a free, **exact**
arming proof in the pre-schedule window. **Run `gen_gates.py --check` only** — and note that
`--out` is honoured only together with `--with`.

## 1. What session 90 settled

* **D1's bytes were overstated by 4.6 % by a unit.** `sync_up_kb` rides the micros column, so it
  is kB = 1000 bytes (`videoOut.cpp:1550`). 22 803.8 is **22.80 MB = 21.75 MiB**, not 22.8 MiB.
* **`bda_up_us` = 2 118.3 µs is not the memcpy.** It times `SynchronizeBuffersOfDirtyRanges`
  whole. Session 85's "92.7 % at 11 GB/s" is arithmetic from an assumed bandwidth that returns
  100 % of the timer by construction.
* **The memcpy is already parallel, and that needs no contrast to establish.**
  `CopyGuestToStaging` queues a region to the copy pool when it is ≥ 64 KiB and
  `TryGetBackingPointer` succeeds — **the same admission test the import uses** — and the census
  says it succeeds for **100.00 %** of regions at a mean of **306 KB over 1.003 regions an
  upload**. `acopy_wait_us` = 0.5 µs a frame.
* **The import itself is reachable and correct.** `bi_ok/bi_try` = 1.0000, `bi_b` = 100 % of the
  upload bytes, `bi_noback` = `bi_nochunk` = `bi_split` = 0, **`bi_bad` = 0** with `bufimpcheck`
  on in both arms, resolution ~10 µs a frame, `bi_cp` = `bi_ok`.
* **Its A/B is INVALID and the contrast is quoted nowhere.** Area split −21.877 %, pair match
  42.9 %. The import arm holds the low DRS rung on 94.7 % of frames against 47.0 %, and the vblank
  histogram goes 14.1 % → 1.0 % at one vblank and 0 % → 11.8 % at three. **Second knob with
  `dapin`'s failure mode.**
* **`pg_pm_us` is closed.** `pgl90a`, VALID: the `specialization ==` compare is **0.7648 of the
  search at 31.77 ns a candidate**; `PushData::StartFor` plus the loop iteration is 0.2352 at
  9.77 ns. **It is a proof, not work** — at 1.0590 candidates a call almost every compare succeeds,
  so a digest cannot replace it without trusting a hash.
* **The `proglap` chain costs +504.4 µs a frame = 5.61 ns a mark** (eight marks a call plus two a
  candidate). Third value on one machine: 7.5 / 3.45 / 5.61 ns.

## 2. What is settled — do not reopen

* **Route A in every form** (`S` = 20.8 ms > 16.7 ms).
* **Route C at per-slot granularity** (s85) and its image half at per-stage granularity (s88:
  514 µs, MARGINAL).
* **"Make the program lookup cheaper"**, **"make the slot lookup cheaper"**,
  **"`CopyAheadResult` is the residue"**, **merging consecutive draws**, **a whole-stage binding
  memo**, **removing the prefetch**, **hoisting `AheadTake` out of `PipelineCache::m_mutex`**.
* **Making imported guest memory the DESTINATION of a buffer.** `PLAN.md` s90 §0 A: 7 of 9 usages
  absent, no device address, and no representation for a page the CPU and GPU both own.
* **Re-running `bufimp=1|2` at a shorter period.** The area split is −21.9 %, not marginal.
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

### 3.1 FIRST: the estimator that survives a DRS shift — TEN sessions old and now shared by two knobs

`dapin` has carried this for nine sessions and `bufimp` joined it in session 90. **Two knobs whose
real effect moves the game's own resolution step cannot be measured by the paired area estimator,
and that is now a property of the programme, not of either knob.**

What exists: `area_verdict.py` pairs blocks and requires the two arms to render the same area;
`summary4.py` gives the paired statistic; `ROADMAP.md` §4 says that inside the vblank plateau the
primary endpoint must be `cpu_gpu_us − spin_gpu_us`, decided before the run. **What does not exist
is a way to compare two arms that legitimately render different areas.**

Read before you build: `area_verdict.py`, `area_series.py`, `summary4.py`, the `rt_*`/`vp_*`
gauges of session 67, and `FACTS` s88 §on `dap88a`. **Candidates, and the reading has to rank them
before a line is written:** a covariate-adjusted endpoint (cpu per unit area, with the adjustment
itself validated on a null A/A); a rung-stratified pairing that compares only blocks on the same
rung and reports the population it dropped; or a scene with no DRS at all. **The list goes into
`PLAN.md` §0 the way sessions 85–90 did, and "do not propose a rewrite before the list exists"
applies here too.**

### 3.2 THEN, and it is one line: the 64 KiB split of `bi_b`

Session 90's headline is a statement about a MEAN: 306 KB a region against a 64 KiB threshold. **It
cannot rule out a bimodal split.** Split `bi_b` at `ASYNC_COPY_MIN_BYTES` — bytes in regions ≥ 64
KiB versus below — and the statement becomes one about the distribution. **It rides free in the
census arm (`bufimp=1`) of any run and needs no contrast.** If the tail below the threshold turns
out to be large, D1 has an inline half nobody has measured and the route is alive; if it is small,
D1 is closed by arithmetic.

### 3.3 The debts, ranked by what is now known

* **The estimator (§3.1).** It gates D1's shipping contrast, `dapin`'s tenth attempt, and anything
  else whose effect is large.
* **Where `bim90a`'s 4.1 ms a frame went.** It is on no counted thread: `cpu_proc_us` −1 026 µs,
  `gpu_busy_us` −1 124 µs, `dt_us` +4 111 µs. Two named candidates, neither measured — the forced
  submit inside `WaitPendingHostReads` (`hostread_waits` 19.468 a frame at `hostread_wait_us` = 0)
  and the GPU reading host-cached guest pages. **A `SiteScope` on the `host-read` submits is the
  cheap half.**
* **The `ObtainBuffer` stream ring: 19.23 MB a frame in 13 325 memcpys of 1 443 B.** A second copy
  population, larger in call count than D1 and never examined. `ob_stream_us` needs
  `KYTY_FRAME_TRACE=1`, not `lite`.
* **The per-element price of `ResourceSpecialization::operator==`** — 31.77 ns a candidate is
  measured, the vector lengths are not.
* **What fraction of the 21.42 prefetched lines a take ever reads** (s89), **the 459.4 µs take,
  unsplit** (s89), **the witness share of the 19.66 ns of `RebindImages`** (s88), **route B items
  2, 8, 10, 12 and the corrected item 3**.

**Say the odds out loud before starting.** 16.7 ms needs ~15 ms removed. **D1 was the biggest
single thing left and it is now measured at zero on the thread that matters.** Everything named
above is hundreds of microseconds or an instrument. **Expect hundreds of microseconds, not
milliseconds, and do not promise 60 FPS on the strength of it.** In this programme upper bounds
have been wrong by 2.0×, 2.3×, 2.4×, 2.6×, 3.8×, 20× and — in the other direction — 4.3×, and
session 90 added a headline that was wrong in KIND rather than in size.

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or
it failed.** A measurement gate's own ABBA satisfies it.

## 4. Do NOT

**New, from session 90:**

* **Do not write an exact-zero band on an ARM-LABELLED window.** It is legitimate only where the
  counter is never `Add`ed — the pre-schedule window. A frame whose flip straddles an arm boundary
  carries a count across the label, and `pred/01` A2 read 0.0003 instead of 0 for exactly that
  reason. **Write a share.**
* **Before banding a counter, check which gate owns its `Add`.** `pred/02` G4 compared `pg_perm`
  across a `proglap=0|1` contrast, and `ProgLapPerms` is `Add`ed only when `prog_lap` is true.
  **The repair file repeated the class of mistake it was written to repair.**
* **A byte counter printed through the micros column is kB (1000 bytes).** `videoOut.cpp:1550`
  says so. Check the units of every `*_kb` before quoting it in MiB.
* **A timer around a function is an upper bound on the one line inside it you care about**, and an
  "X % at Y GB/s" attribution of that timer is arithmetic, not measurement, and returns whatever
  the assumed bandwidth makes it return.
* **Check whether the work you are removing is already on another thread.** `AsyncMemcpy` moves
  every ≥ 64 KiB region off the GuestGpu thread, and its admission test may be the same test your
  new path uses — in which case your path captures exactly the work that was already parallel.
* **`gen_gates.py --out <file>` is ignored without `--with`, and rewrites `gates_base.txt`.** Read
  the tool's own output line.
* **Never pipe a writing script through `head`** — SIGPIPE kills it before it writes, and the
  lines it did print look like success.
* **Do not let an INVALID run's contrast leak into a diagnosis.** Session 90 quotes `bim90a`'s
  within-arm census and its per-arm distributions and never its difference; `dt_us` +4.1 ms is
  written as a diagnosis with both arms' numbers, not as a measured effect.
* **A design a reading refutes may not be the design you were going to build.** Nine independent
  "BLOCKS" findings against making imported memory the buffer DESTINATION are all correct and all
  irrelevant to changing only the copy SOURCE.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming
proved by a counter inside the run; `guards.py` check 10 hashes the exe installed *now*, so compare
check **lines**, not verdicts, and do not rebuild between acceptance and the final answer; check 6
(cores) FAILs routinely and is not an admission criterion; a gate enum entry goes immediately
before `Count` **and** its `DEFINITIONS` row goes last, in the same order; **there is no
`static_assert`**; a counter absent from `guards.py`'s `SELF_CHECKS` is **never parsed**;
`PATCH_DRY=1` checks anchors, **not compilation**; patch anchors must be **text**; the `_us`
counters on `FrameTrace-x` are ALREADY microseconds; **the first entry after a fresh build hangs**
— `--warmup-first` absorbs it; **`daepceil`'s comment still says "(default 1)" and it is 0**.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b` | **MEASURED — closes route A** |
| route C's image half | 514 µs, MARGINAL (±32 %) | **NOT RE-OPENED** |
| **D1's bytes** | **22.80 MB a frame, not 22.8 MiB** | **CORRECTED (s90) — a five-session unit error** |
| **D1's reachable share** | **100.00 % of uploads and of bytes** | **MEASURED (s90), within-arm** |
| **D1's memcpy on the GuestGpu thread** | **already pooled at the mean** — 306 KB a region against a 64 KiB threshold | **DERIVED (s90) from source + census, no contrast** |
| **`bda_up_us` = 2 118.3 µs** | **NOT the memcpy** | **CORRECTED (s90)** |
| **D1's A/B** | **INVALID — area split −21.9 %, pair match 42.9 %** | **NOT MEASURED; the effect moves the DRS step** |
| **`pg_pm_us`'s search half, divided** | **`specialization ==` 298.72 µs (76.5 %), the push-data half 91.85 µs (23.5 %)** | **MEASURED (s90, `pgl90a` VALID) — a proof, not work** |
| **the `proglap` chain's own price** | **+504.4 µs a frame = 5.61 ns a mark** | **MEASURED (s90) — a debt open since session 86** |
| D2: the two prefetch passes | 944.2 µs | MEASURED (s89) |
| D2: the take (swaps + retire) | 459.4 µs | MEASURED (s89) — NOT SPLIT |
| `dapin`'s GPU cost | the corrected contrast FAILED admission | **UNEXPLAINED, tenth session, and now shared with `bufimp`** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured since session 82 |

**The honest statement of the task.** Sessions 87–89 found the three largest unopened blocks to be
the price of proving a cached answer is still good. **Session 90 took the one block that was
neither a proof nor a shipped default, built it, and found that its headline number was the wrong
kind of number twice: the bytes were overstated by a unit, and the timer they were attributed to
does not contain the work they were attributed to, because that work has been on the copy pool
since session 27.** The import reaches every byte it aims at, costs 10 µs a frame to resolve, and
its one A/B could not be read because the change is large enough to move the game's own resolution
step. **Session 91 is for the estimator that failure names — it is ten sessions old, it now blocks
two knobs, and until it exists no large effect in this programme can be measured at all.**
