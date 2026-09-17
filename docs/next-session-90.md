# Session 90 — the brief

**Session 89 opened the 1 607 µs nobody had looked at, and it is not a proof and not a lookup: it
is prefetching.** Read `docs/ROADMAP.md` **§0.1** first — it still separates *"three routes with a
measured ceiling do not reach 60 FPS"* (proved) from *"60 FPS is unreachable"* (**not** proved).
**§0.1 now carries a session-89 addendum, and §2 D was rewritten end to end** (its stale
session-72 quotation is finally gone), so read the addendum and §2 D together or not at all.

Session 89's commit is on `merge-upstream`. **Source changed and the binary was rebuilt once, but
NO default changed**: the installed `kyty_emulator.exe` is `4bffdbc7563ef624…`, 23 612 928 bytes,
and the gate session 89 added (`takelap`) is **0**. Harness — **`C:/kyty/s89`**, port it to
`C:/kyty/s90`.

## 0. Read first

0. **`docs/ROADMAP.md` §0.1 (including the session-89 addendum), §2 D (rewritten), §5 item 4 and
   §7.** A is closed by measurement. B sums to 0.7–2.5 ms and has shipped −252 µs in four
   sessions. C is MARGINAL at 514 µs and is not built. **D2 is now divided to the bottom: the
   4 049 µs block is 63 % `AheadTake`, `AheadTake` is 34.7 % witness loops and 57 % prefetch, and
   every one of those parts is either a proof or a shipped default.**
1. `C:/kyty/s89/FACTS.md` — the single source of truth. **§2 FIRST (a null control failed, and the
   section argues against its own decision), then §3.2 (the split), §3.3 (the verdict and what the
   rule said it would mean), §3.4 (what the brief's three components really measured), §3.5 (what
   is still an upper bound), §4 (the §3.2 reading and the hoist verdict), §5 (`pg_pm_us`) and §7
   (all 24 predictions, four of them my own being wrong).**
2. `C:/kyty/s89/README.md` — the standing traps. The three that will bite first: **a null control
   written as an exact per-frame identity cannot survive the flip straddle, and a control no run
   can pass is not a control**; **a mark's price does not carry between chains** (7.5 ns in session
   87, **3.45 ns** here); and **a phase can be dominated by something other than the thing you
   named it after** (`da_t_cpy_us` was predicted ≤ 120 µs from the copy and read 459 µs of swaps).
3. `C:/kyty/s89/PLAN.md` **§0 B** — the lock list. It is the precondition for §3.2 below and it
   already exists; do not redo it, extend it.

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s89` → `C:/kyty/s90` with a script modelled on
`C:/kyty/s88/s89_port.py` — **written fresh in the SOURCE directory**, because the copies inside a
harness are self-copy no-ops. It repairs the head of every `--roots` chain and `area_verdict.py`'s
arithmetic `range(89, 70, -1)`. `gates_base.txt` is **unchanged** — 1092 bytes, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`; `takelap` is deliberately
absent from it, which is what gives every new counter a free, **exact** arming proof in the
pre-schedule window. **Run `gen_gates.py --check` only.**

## 1. What session 89 settled

* **The residue of `AheadTake` is 57 % prefetch.** `da_t_pfa_us` **678.5** (eleven
  `PrefetchVectorData`, gate `daprefetch`) + `da_t_pfb_us` **265.7** (one `__builtin_prefetch` per
  live run, 54 887 a frame) = **944.2 µs a frame, 33.8 % of `AheadTake`**, against 134.7 µs for the
  probe loop and 116.6 µs for the key build. **A prefetched line costs 3.51 ns and a take
  prefetches 21.42 of them.**
* **It is a debt against three shipped defaults, and the rule said so before the number.**
  `daprefetch`=1 (`dpf75a`: removing it costs **+0.98 ms**), `pfhint`=1 (−0.25 ms), `pfcap`=1024
  (−0.29…−0.31 ms). **The 944 µs is the wall time of the instructions, not the net effect of
  having them, and nothing exists to collect it.**
* **The take is 459.4 µs and it is not the copy.** 92.2 % of hits retire the slot through two
  `std::swap`s; the 670.6 that copy move 235 B each ≈ 16 µs. **Prediction T6 predicted ≤ 120 µs and
  missed by 3.8×.**
* **The "two-probe lookup" is 1.0433 probes a call.** `da_probe` has been take-side **plus**
  queue-side since session 71 and the queue half is 64 % of it.
* **The witness loops' ITERATION is 175.4 µs = 2.12 ns a run** — a term session 88's subtraction could not see,
  because both `dawitloop` skip paths still run `ordinal++; continue;`.
* **`pg_pm_us` is 65.4 % the `find_if`**, i.e. `PushData::StartFor` + the `specialization ==`
  compare, exactly as session 89's own brief said and contrary to prediction P5.
* **A mark of this shape costs 3.45 ns**, not the 7.5 ns `pgl87a` implies.
* **A pre-registered null control failed, and it is the first thing in the report.** C1 demanded
  parts ≤ whole in **every frame** and 3 of 3 741 straddled the flip. **No run could pass it.** The
  report publishes the numbers anyway, names the sealed control that carries them instead (C2,
  which reproduced session 88's 852.5 µs from a different method on a different binary), and
  states the case against its own decision. **A reader who holds session 89 to the letter of its
  own seal should treat §3 as unpublished.**

## 2. What is settled — do not reopen

* **Route A in every form** (`S` = 20.8 ms > 16.7 ms).
* **Route C at per-slot granularity** (s85) **and its image half at per-stage granularity**
  (s88: 514 µs, MARGINAL). The only unmeasured term left **can only make it smaller**.
* **The two-pass split of the image loop** — refused on reading, `FACTS` s87 §2.1.
* **"Make the program lookup cheaper"** — 28.74 ns a call; and now **"make the slot lookup
  cheaper"** — 134.7 µs a frame at 1.0433 probes a call.
* **"`CopyAheadResult` is the residue"** — the copy is ≈ 16 µs a frame.
* **Merging consecutive draws** — 0.668 %.
* **A whole-stage binding memo**, four times.
* **`dause=0|1`**, **`recordthread=0|1` as the `dapin` experiment**, **the `std::map` of
  `SynchronizeBuffersInRange`**, **the BDA region walk**, **the record thread as `dapin`'s GPU
  carrier**, **`KYTY_GPU_TIME` as that instrument**, **`PLAN_82_bind.md` item 6b**.
* **Removing the prefetch.** Three ABBAs say it pays for itself. Do not propose `daprefetch=0`.
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

### 3.1 FIRST: D1 — `BufferCache::UploadCopies`, ~2 100 µs, and it is now the largest untouched ceiling in the record

Every block this programme has opened since session 85 has turned out to be a proof or a shipped
default. **D1 is neither, it is measured, and nobody has started it.** 22.8 MiB a frame through
`CopyGuestToStaging` → staging → `vkCmdCopyBuffer` at 11 GB/s.

**Read session 28 first** (`VK_EXT_external_memory_host`, the import path, `KYTY_HOST_IMPORT*`,
the reupload-tick heuristic) — images already avoid the staging copy this way and **buffers do
not**. The question this session answers is **why not**: which of the buffer path's requirements
(alignment, the write-fault window, the epoch witness, the stream ring) the image path does not
have. **That is a reading task before it is a coding task, and the list goes into `PLAN.md` §0 the
way sessions 85–89 did.**

**Do not propose a rewrite before the list exists.** Four of the last five plan items that did not
survive the source were caught exactly there.

### 3.2 THEN: the `pg_pm_us` search, one mark — and NOT the hoist

**The hoist is closed and it was closed for free.** `FACTS` s89 §4.1 read `pl_prog_wait_us` =
**42.0 µs a frame against a 4 756.6 µs hold — a ratio of 113** — from the same run, because
`plkstat` was 1 in both arms and nobody had looked at the wait since session 87. `AheadTake` **is**
hoistable in-thread under the three conditions in `PLAN.md` s89 §0 B, and hoisting it is worth
**tens of microseconds**. The GuestGpu thread's total loss to that lock across all three of its
sites is **92.4 µs a frame = 0.30 % of the frame**, and the only other holders are background
compile workers with **zero** `AsyncPipelines: skipped draw` in the run. **Do not build it. Do not
re-open it without a scene that compiles during play.**

What is left in that neighbourhood is one mark: **`pg_pm_us`'s 337 µs search half is
`PushData::StartFor` + `ShaderDataDwords` + the `specialization ==` compare, and which of them it
is, is [NM].** One mark inside the `find_if` predicate, riding in the existing `proglap` chain, in
both arms of whatever ABBA §3.1 needs. It is cheap and it closes a debt that has been open since
session 87.

**And the same trick that closed the hoist should be tried first on D1**: `bda_up_us`,
`bda_walk_us`, `sync_up_kb` and `ob_stream_kb` are all already printed. **Seventh session in
seven: look for the number on disk before building an instrument.**

### 3.3 The debts, ranked by what is now known

* **What fraction of the 21.42 prefetched lines a take is ever read.** It decides whether the
  648 µs of pass A is reducible at all. A counter on first touch, or an A/B with a truncated vector
  set. **Do not confuse it with `daprefetch=0`, which is already measured and is a loss.**
* **The 459.4 µs take, unsplit** between the two `std::swap`s, `slot.uses = 0`, the release store
  and the two `Gates::Enabled` reads per retire. One mark.
* **`pg_pm_us`: `PushData::StartFor` or the `specialization ==` compare.** One mark inside the
  predicate. 337 µs a frame is at stake and it is now known to be the search.
* **`PipelineCache::m_mutex` splitting: CLOSED by §4.1, not built.** 42.0 µs of wait against
  4 756.6 µs of hold. Do not re-open without a scene that compiles during play.
* **`dapin`'s GPU cost, TENTH session.** Session 88 ran the corrected contrast and it failed
  admission at +12.93 % area split. **Either take it as `dapin=1|3` with the record path live, or
  strike it from §7.** It has cost nine sessions and produced one number nobody can explain.
* **The witness share of the 19.66 ns of `RebindImages`** — worth a counter only if something else
  in that file is being touched.
* **Route B items 2, 8, 10, 12 and the corrected item 3** (`FACTS` s85 §8).

**Say the odds out loud before starting.** 16.7 ms needs ~15 ms removed. D1's ceiling is 2.1 ms and
it is the biggest single thing left; everything else named above is hundreds of microseconds.
**Expect hundreds of microseconds, not milliseconds, and do not promise 60 FPS on the strength of
it.** In this programme upper bounds have been wrong by 2.0×, 2.3×, 2.4×, 2.6×, 3.8×, 20× and — in
the other direction — 4.3×.

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or
it failed.** A measurement gate's own ABBA satisfies it.

## 4. Do NOT

**New, from session 89:**

* **A parts-vs-whole identity against `FrameTrace` counters CANNOT be exact, and the reason is not
  the flip.** `videoOut.cpp:1238-1240` snapshots counters **one at a time**, in enum-index order,
  each under the registry mutex — so the whole (`DrawAheadTakeNs`, index 176) and the parts
  (indices 872-877) are sampled hundreds of calls apart. Session 89's first edition blamed the
  flip straddle and was wrong by 50-250×. **Write the statistic as a ratio of sums.**
* **When a control fails, the seal's remedy is to REPAIR THE CONTROL under a new sealed
  pre-registration — not only to replace the run.** Session 89 rebutted the "replace the run" half,
  which was true and irrelevant, and did not take the cheap remedy that was available. **Read
  `FACTS` s89 §2(d) before you write your first control.**
* **An "arithmetic check" built from two DEFINED quantities is an identity and cannot fail.**
  `tail ≡ whole − Σ` and `Δ ≡ whole_on − whole_off` give `Σ − Δ + tail ≡ whole_off` for any Σ.
  Session 87 recorded this as A8; session 89 did it again and an audit caught it.
* **Do not write a null control as an exact per-frame identity.** `da_take_us` is Added after
  `AheadTake` returns and the phases are Added inside it; a flip between them puts the parts in
  frame N and the whole in N+1. **Write the statistic — a share of frames, a ratio of sums — and
  make it one a correct run can pass.**
* **Do not carry a mark's price between chains.** 7.5 ns in session 87's `proglap`, **3.45 ns** in
  session 89's `takelap`, on the same machine and the same kind of mark, because what follows the
  `rdtsc` differs. **Measure the instrument in its own ABBA every time.**
* **Do not size a phase by the thing you named it after.** `da_t_cpy_us` is the swaps, not the
  copy, and the prediction missed by 3.8×.
* **Do not trust a counter that is "already on disk" without asking what populations it sums.**
  `da_probe` is take-side plus queue-side and the queue half is 64 %.
* **Do not attribute code to the gate a brief names — and do not harden the correction into a new
  error.** The eleven-vector pass belongs to `daprefetch`; the live-run pass is guarded by
  `dawitptr`'s `direct` predicate and **does not exist without it**. Session 89's sealed file said
  this correctly and its report then claimed `dawitptr` "gates neither of them into existence",
  which is false.
* **A counter that sums bytes is not a count of instructions.** `da_pf_cap_b`/64 is a **lower**
  bound on prefetches issued, because each vector issues `ceil(size/64)`; so the derived "ns a
  line" is an **upper** bound.
* **A unit price divided by a population that does not own the whole numerator is a bound, not a
  price.** Session 89 published three and the audit relabelled all three.
* **Do not read a default out of a comment in `pipelineCache.cpp`** — `:694` still says `daepceil`
  "(default 1)" and it is 0.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming
proved by a counter inside the run, and **the pre-schedule window is free and exact** while a
schedule arm needs a statistic; `guards.py` check 10 hashes the exe installed *now*, so compare
check **lines**, not verdicts, and do not rebuild between acceptance and the final answer; check 6
(cores) FAILs routinely and is not an admission criterion; a gate enum entry goes immediately
before `Count` **and** its `DEFINITIONS` row goes last, in the same order; **there is no
`static_assert`**; a counter absent from `guards.py`'s `SELF_CHECKS` is **never parsed**;
`PATCH_DRY=1` checks anchors, **not compilation**; patch anchors must be **text**, because every
line number in every brief has been stale; the `_us` counters on `FrameTrace-x` are ALREADY
microseconds; **the first entry after a fresh build hangs** — `--warmup-first` absorbed it again.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b` | **MEASURED — closes route A** |
| route C's image half | 514 µs, MARGINAL (±32 %) | **NOT RE-OPENED** |
| D2: the M1 witness loop **bodies** | 567.4 + 285.1 = **852.5 µs** | MEASURED (s88) |
| **D2: the witness loop ITERATION** | **175.4 µs, 2.12 ns a run** | **MEASURED (s89) — s88's subtraction could not see it** |
| **D2: the two prefetch passes** | **944.2 µs (884.2 un-instrumented)** | **MEASURED (s89) — a debt against three shipped defaults** |
| **D2: the take (swaps + retire)** | **459.4 µs** | **MEASURED (s89) — NOT SPLIT** |
| **D2: the probe loop** | **134.7 µs**, 1.0433 probes a call | **MEASURED (s89) — the lever is dead** |
| **D2: the key build** | **116.6 µs** | **MEASURED (s89)** |
| **`pg_pm_us`: the search half** | **337.0 of 515.4 µs** | **MEASURED (s89) — NOT SPLIT further** |
| D2: draw-thread `MaterializeResources` | 667 µs, 2.68 µs a call | MEASURED (s87) |
| **D1, staging `memcpy`** | **~2 100 µs** | **NOT STARTED — the largest untouched ceiling, §3.1** |
| **`pl_prog_wait_us` against `pl_prog_hold_us`** | **42.0 µs against 4 756.6 µs, a ratio of 113** | **MEASURED (s89) — the lock is not contended, so the hoist is worth tens of microseconds. CLOSED** |
| `dapin`'s GPU cost | +1.961 % ± 0.165 %, ×5; the corrected contrast FAILED admission | **UNEXPLAINED, tenth session** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured since session 82 |

**The honest statement of the task.** Sessions 83–86 measured and closed the bookkeeping. Sessions
87 and 88 found the two largest unopened blocks to be the price of proving a cached answer is still
good, and session 88 halved both by measuring the term each was missing. **Session 89 opened the
last unsplit block and found it is not a proof either: it is 944 µs of prefetching lines for a
later phase, 459 µs of moving a result out of a slot, 175 µs of walking a list and 251 µs of
hashing and comparing a key — all of it work, none of it removable by anything that exists, and
the largest piece is three defaults that were each shipped because removing them cost more.**
**Session 89 also closed the lock question for free, from a counter its own run already printed:
the hold is 4 756 µs and the wait is 42.** **Session 90 is for D1 — the one measured ceiling in
this record that nobody has started — and it should begin by reading the counters D1 already
prints, because six sessions in a row the number was on disk.**
