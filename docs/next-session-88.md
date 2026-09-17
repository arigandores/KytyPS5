# Session 88 — the brief

**Session 87 opened the two largest unsplit blocks in the record and both answers were the opposite
of their names.** Read `docs/ROADMAP.md` **§0.1** first — it separates *"three routes with a
measured ceiling do not reach 60 FPS"* (proved) from *"60 FPS is unreachable"* (**not** proved), and
those two get conflated every time. **§0.1 now carries a session-87 addendum that changes what §2 C
says**, so read the addendum and §2 C together or not at all.

Session 87's commit is on `merge-upstream`. **Source changed and the binary was rebuilt, but NO
default changed**: the installed `kyty_emulator.exe` is `84b3fe93304c7158…`, 23 610 368 bytes, the
gate session 87 added (`bindalt`) is **0** and the gate it extended (`proglap`) is **0**. Harness —
**`C:/kyty/s87`**, port it to `C:/kyty/s88`.

## 0. Read first

0. **`docs/ROADMAP.md` §0.1 (including the session-87 addendum), §2 C (the whole of it — the
   session-85 verdict, the session-86 correction and the session-87 re-opening are three different
   claims about the same thing), §2 D and §5.** A is closed by measurement (session 83). B sums to
   0.7–2.5 ms and has shipped −252 µs in four sessions. **C's image half is RE-OPENED at 1 107 µs
   against its own 1 000 µs floor, by a rule sealed before the run, with a 10.7 % margin and an
   unmeasured term inside it.** D2 and D3 are divided to the bottom.
1. `C:/kyty/s87/FACTS.md` — the single source of truth. **§0, then §2 (four things refused or found
   before a line was written, one of them the split the brief itself prescribed), §3.4 and §3.5 (the
   verdict, the three readings it is robust to, and the three things that stand between 1 107 µs and
   a saving), §4 and §4.4 (what the block actually is, and the prior measurement that is quoted
   rather than repeated), §7 (all twenty-nine predictions, including the one I wrote that could not
   fail).**
2. `C:/kyty/s87/README.md` — the standing traps. The three that will bite first: **a comment that is
   true can still not license what you want it to**; **an algebraic identity is not an
   over-identification check — substitute the definitions and see whether it can fail**; and **the
   number you need may already be printed in every log, not just last session's** — `da_take_us` is
   admission criterion 5 of every run this programme performs and it was 58 % of the block session
   86 called "never looked at".
3. `docs/PLAN_82_bind.md` — route B. **Do not package from it without reading the source first.**
   Every line number in it is stale, session 85 refused three of its four proposed items on reading,
   and its item-3 design is superseded by `FACTS` s85 §8.1.

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s87` → `C:/kyty/s88` with a script modelled on `C:/kyty/s86/s87_port.py`
— **written fresh in the SOURCE directory**, because the copies of earlier port scripts inside the
harness have had their own `SRC` and `DST` rewritten to the same path and are self-copy no-ops.
It repairs the two things a literal rewrite breaks: the head of every `--roots` chain (it becomes
`s88` and **drops `s87`**) and `area_verdict.py`'s arithmetic `range(87, 70, -1)`. `gates_base.txt`
is **unchanged** — 1092 bytes, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `bindalt`, `proglap`,
`drawmerge`, `drawmergecheck`, `bindlap`, `bdasplit`, `slotstat`, `slotstatcheck`, `bindpack2`,
`bindpack2check`, `bindpack`, `bdalap`, `plkstat`, `mutwide`, `bindkey` and `bdabits` are
deliberately absent from it — which is also what gives every new counter a free arming proof in the
pre-schedule window. **Run `gen_gates.py --check` only** (it now reports 100 gates / 1307 bytes,
which is the file being *out of date on purpose*).

**And a trap that cost session 87 a counter:** a name **already present** in `gates_base.txt` cannot
be overridden by appending it — `--gates "$(cat gates_base.txt) mutsite=1"` leaves `mutsite` at 0,
because `FindAssignment` takes the **first** whole-word `name=`. Assign such names **in the arm
text**, which the gate-file pass then skips.

## 1. What session 87 settled

* **`bl_res_us` is 86.6 % `ResolveTextureWith` and 13.4 % `BindImage`.** `P_res` = 63.24 ns a slot,
  `P_rsv` = **54.75 ns**, `P_bind` = **8.49 ns**, the instrument's own price `T` = 7.40 ns. Coverage
  0.5000 by construction; no frame of 7 593 has the parts exceeding the whole; `bl_img_us/bl_img_n`
  reproduces session 86's 22.30 ns to −1.8 % on a counter the instrument did not touch.
* **Route C's image half is RE-OPENED at `ceiling87` = `sl_img_dupv` × (19.66 + `P_rsv`) =
  1 106.9 µs**, by the rule sealed in `pred/01` §7 before the run (re-open ≥ 1 000, marginal
  300…1 000, closed below 300). **Margin 10.7 %.** Robust to all three available readings of `P_res`
  (63.24 / 65.25 / 66.40 ns give 1 107 / 1 137 / 1 154 µs), because what varies between runs is
  `P_res` and `P_bind` is a within-run difference of two arms.
* **The two-pass split the previous brief prescribed was refused on reading.** The comment at
  `descriptors.cpp:1515-1517` is true and is about session 57's B2a — the **same iteration**. The
  coupling a two-pass split breaks is `Image::binding.is_bound`, read by
  `ConfigureImageSourceUnlocked` (`textureCache.cpp:1226`, whose own comment one line above **is**
  the ordering contract), by `ResolveOverlap` / `ResolveDepthOverlap` / `ExpandImage`, and by nothing
  at all after `FindImage` has freed the id the deferred `BindImage` would index.
* **The 3 764 µs "resource materialisation" block is 63.1 % the LOOKAHEAD TAKE.** `pg_ahead_us`
  (`AheadNote` + `AheadTake` + `AheadCheck`) 2 557 µs; draw-thread `MaterializeResources` 667 µs
  (16.5 %) at **2.68 µs a call** over 249 calls; the permutation phase 462 µs at **52.1 ns**;
  the locals 95 µs at 10.7 ns. `AheadNote` priced for the first time at **25.04 ns**.
* **`da_take_us` = 2 337 µs a frame is 58 % of that block and has been printed on every
  `FrameTrace-draw` line since session 54** — it is admission criterion 5 of every run this
  programme performs. **The fifth session in five in which the number asked for was already on
  disk.** `pg_ahead_us ≥ da_take_us` in every one of 7 593 frames, ratio 1.0931.
* **The D2 instrument costs +448.5 ± 81.0 µs and the D3 instrument +434.8 ± 123.4 µs.** Session 86's
  prediction I1, which its own design made unevaluable, is discharged by one extra run.

## 2. What is settled — do not reopen

* **Route A in every form** (`S` = 20.8 ms > 16.7 ms).
* **Route C at per-slot granularity** — the descriptor-write side (session 85: 0.95 ns a descriptor,
  split +137 µs against −272 µs to decide). **What is re-opened is the per-STAGE amortisation of
  duplicate image slots, and only that.**
* **The two-pass split of the image loop** — refused on reading, `FACTS` s87 §2.1.
* **"Make the program lookup cheaper"** — 28.74 ns a call, 255 µs a frame.
* **Merging consecutive draws** — 0.668 % share an identical descriptor set.
* **The permutation `std::deque` scan as a POPULATION** — 1.059 candidates a call. Its 52 ns a call
  is a different question and is open (§3.3).
* **A whole-stage binding memo**, four times now.
* **A `dause=0|1` ABBA** — `FACTS` s87 §2.4: `da_hit` is 97.1 %, a worker materialisation is 3.34 µs,
  and the arm would move ~8 200 of them onto the draw thread. It would go VOID.
* **The `std::map` of `SynchronizeBuffersInRange`**, **the BDA region walk**, **the record thread as
  `dapin`'s GPU carrier**, **`KYTY_GPU_TIME` as the instrument for that question**,
  **`PLAN_82_bind.md` item 6b**.
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

### 3.1 FIRST: the witness share of `P_rsv` — the term that decides whether 1 107 µs exists

**This is the cheapest decisive measurement left and it is the only thing standing between a
re-opened route and a session spent building the wrong thing.** `P_rsv` = 54.75 ns is
`ResolveTextureWith` plus the loop's own overhead. A per-stage amortisation of a duplicate image
slot can skip only the part that is *not* the proof that the earlier slot's resolution is still
valid. In `ResolveTextureWith` (`descriptors.cpp:764-1086`) that proof is: `DecodeNativeDescriptor`,
the resource key, `MemoHashBytes` over the eight T# dwords, the memo index, the 32-byte `memcmp`,
`m_slot_images.try_get`, the five-field liveness check, and `TextureSourceSettled`'s desc-dependent
tail. Everything after it — `ConfigureImageSource`, `TouchImage`, `tick_accessed_last`, the DCC
adoption, the memo way clock, `emit` — is not.

**Split it with the same idiom, one mark a call, not a pair**: the function already has exactly one
`FrameStats::Scope` at `:767-768` (`BindResolveTexNs` / `BindResolveTex`) which **reads 0 under
`lite`** — so the re-emission is the `LapScope` idiom, as `proglap` was. Two counters, `bl_wit_us` /
`bl_wit_n`, bracketing entry to the memo-hit decision.

**Pre-register the routing rule before the run**: `ceiling88 = sl_img_dupv × (19.66 + P_rsv −
P_wit)`, with the same three bands `pred/01` §7 used (≥ 1 000 build, 300…1 000 marginal, < 300
closed). And **measure `sl_img_dupv` in this session's own run** (`slotstat=1`) rather than quoting
`drm86a`'s 14 875.5 — `FACTS` s87 §3.5 names that as a borrowed number.

**Note the trap `FACTS` s87 §3.3 records**: before writing an over-identification check, substitute
the definitions and see whether it can fail. A8 could not.

### 3.2 THEN: `dawitloop` read INSIDE the lock, on this binary

`FACTS` s87 §4.4 attributes ~48 % of the 4 049 µs block to the M1 witness verification **on the
strength of session 72's measurement on a different binary, outside the lock, and says so rather
than pretending to have measured it.** The knob still exists: `dawitloop` (`KYTY_DA_WITNESS_LOOP`,
0/1/2, default 0, **A CEILING THAT CANNOT BE SHIPPED** — at 1 it skips the clean-run loop of
`VerifyWitness`, at 2 the live one, so some recorded guest words are not compared; `da_loop_skip`
confirms it fired). **One ABBA `dawitloop=0|1` with `proglap=1` in both arms prices the clean loop
inside the lock exactly**, and a second `0|2` prices the live one. Two runs, no new code beyond the
schedule — and the arms must assign `dawitloop` **in the arm text**, because it IS in
`gates_base.txt`.

**What it decides:** if the witness loops are most of `pg_ahead_us`, then D2's lever is the same
shape as route C's — amortise or cheapen a *proof*, not the work — and the two blocks become one
question. If they are not, the remaining `AheadTake` cost is slot probing and `CopyAheadResult`, and
that is a different lever.

### 3.3 The debts, unchanged and unstarted

* **`dapin`'s GPU cost, EIGHTH session.** +1.961 % ± 0.165 %, five replications, visible only with
  the record thread live and **not** caused by that thread's placement. A **`recordthread=0|1` ABBA
  with `dapin` pinned at 3** separates existence from affinity in one run. Sessions 86 and 87 both
  declined it and both said so. **Either take it or strike it from §7.**
* **`pg_pm_us` = 462 µs a frame at 52.1 ns a call.** Not the deque scan (1.06 candidates). It is
  `PushData::StartFor` plus the `specialization ==` compare, and which of the two is [NM].
* **D1 — `BufferCache::UploadCopies`**, 22.8 MiB a frame at 11 GB/s, ceiling ~2.1 ms. A rewrite.
  Re-read session 28's caveats before touching it.
* **`PipelineCache::m_mutex`, 4.4 ms a frame of hold** — and §3.2 above is the precondition for
  asking whether `AheadTake` can run outside it.
* **Route B items 2, 8, 10, 12 and the corrected item 3** (`FACTS` s85 §8).

**Say the odds out loud before starting.** 16.7 ms needs ~15 ms removed. §3.1's ceiling is at most
1.1 ms and is an upper bound with a term inside it that is being measured precisely because it is
expected to reduce it. In this programme upper bounds have been wrong by 2.6×, 20×, 2.3× and — in
the other direction — 4.3×. **Expect hundreds of microseconds, not milliseconds, and do not promise
60 FPS on the strength of it.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.** A measurement gate's own ABBA satisfies it.

## 4. Do NOT

**New, from session 87:**

* **Do not let a comment license a reordering it was not written about.** `descriptors.cpp:1515`
  says `BindImage` does not read `prepared.images`; that is true and irrelevant, because the
  coupling is `Image::binding.is_bound` and the guard that depends on it carries its own comment one
  line above. **Read the code the comment is about, not the comment.**
* **Do not write an over-identification check without substituting the definitions.** A8 was
  `P_rsv_raw − T` against `P_rsv`; the two are identically equal, the run printed |diff| = 0.00 ns
  because it could not print anything else, and the prediction is NOT EVALUABLE. **The third defect
  in a prediction of my own in two sessions.**
* **Do not assume a phase with an empty body is free.** `pg_memo_us` reads 72 µs a frame with
  `pg_memo_n` = 0.000; the boolean test, the `SrtReadLog` construction and the mark are 7.9 ns a
  call. **Prediction B8 is a MISS for that reason.**
* **Do not run an ABBA that is certain to go VOID.** `dause=0` would have moved ~8 200
  materialisations onto the draw thread — tens of milliseconds, three vblanks, a collapsed DRS
  ladder. Refuse it **before** the run and take the number within-arm if it is available.
* **Do not quote a unit price across runs.** `P_res` reads 63.24 / 65.25 / 66.40 ns in three runs.
  A within-run difference of two arms does not move; a level does.
* **Do not append a name that `gates_base.txt` already contains.** The first assignment wins.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming proved
by a counter inside the run — and the **pre-schedule window is free and stronger than a median**;
the schedule straddle is **1.6–1.9 % on sums and 100 % of it sits at distance 0 from a block
start**, so write the statistic into the prediction; `guards.py` check 10 hashes the exe installed
*now*, so compare check **lines**, not verdicts, and do not rebuild between acceptance and the final
answer; check 6 (cores) FAILs routinely and is not an admission criterion; a gate enum entry goes
immediately before `Count` **and** its `DEFINITIONS` row goes last, in the same order — **and there
is no `static_assert`**; every verify line needs a cap (32–64); never put a printf's format string
and its argument list in one patch call; a counter absent from `guards.py`'s `SELF_CHECKS` is
**never parsed**, so add the row before the first run; **no value-initialiser on a per-call scratch
array**; `dt_us` is not an endpoint inside the vblank plateau; the `_us` counters on `FrameTrace-x`
are ALREADY microseconds.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b` | **MEASURED — closes route A** |
| **D3: `bl_res_us`, the resolve half** | **54.75 ns a slot = 86.6 %** | **MEASURED (s87)** |
| **D3: `bl_res_us`, `BindImage`** | **8.49 ns a slot = 13.4 %** | **MEASURED (s87) — the blocker is small** |
| **route C's image half, by the sealed rule** | **1 107 µs ≥ 1 000** | **RE-OPENED, margin 10.7 %, an UPPER bound** |
| …the witness share of `P_rsv` inside it | — | **NOT MEASURED — §3.1, and it decides the above** |
| **D2: the block's largest part** | **`AheadTake` + `AheadNote`, 2 557 µs = 63.1 %** | **MEASURED (s87)** |
| D2: draw-thread `MaterializeResources` | 667 µs = 16.5 %, 2.68 µs a call | **MEASURED (s87)** |
| D2: the permutation phase | 462 µs = 11.4 %, 52.1 ns a call | **MEASURED — unattributed, §3.3** |
| `AheadNote` | 25.04 ns a call | **MEASURED (s87)** |
| …the witness loops inside `AheadTake` | 1.929 ms (s72, other binary, outside the lock) | **NOT RE-MEASURED — §3.2** |
| D4: identical descriptor set (a real merge) | **0.668 %** | **MEASURED — merging is dead** |
| D1, staging `memcpy` | ~2 100 µs | **NOT STARTED** |
| `dapin`'s GPU cost | +1.961 % ± 0.165 %, ×5 | **UNEXPLAINED, eighth session** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured since session 82 |

**The honest statement of the task.** Sessions 83–86 measured, priced and closed the bookkeeping,
and session 86 concluded that the money was in work rather than bookkeeping. **Session 87 divided
both of the blocks that conclusion rested on, and both turned out to be neither: 87 % of the bind
phase's image loop is a memo lookup with a witness, and 63 % of the block under the pipeline-cache
lock is taking and validating results a worker already computed.** Both of the two largest unopened
blocks in this record are the price of **proving that a cached answer is still good** — the same
shape as the 19.66 ns that closed route C at slot granularity. **Session 88 is for finding out how
much of that proof is actually necessary**, and §3.1 is the one number that decides whether the
answer is worth anything.
