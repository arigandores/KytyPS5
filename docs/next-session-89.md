# Session 89 — the brief

**Session 88 measured the term each of session 87's two headline figures was missing, and both
figures halved.** Read `docs/ROADMAP.md` **§0.1** first — it still separates *"three routes with a
measured ceiling do not reach 60 FPS"* (proved) from *"60 FPS is unreachable"* (**not** proved).
**§0.1 now carries a session-88 addendum that changes what §2 C and §2 D say**, so read the
addendum and those two sections together or not at all.

Session 88's commit is on `merge-upstream`. **Source changed and the binary was rebuilt three
times, but NO default changed**: the installed `kyty_emulator.exe` is `25fd4f2e0010f799…`,
23 612 416 bytes, and the knob session 88 added (`bindwit`) is **0**. Harness — **`C:/kyty/s88`**,
port it to `C:/kyty/s89`.

## 0. Read first

0. **`docs/ROADMAP.md` §0.1 (including the session-88 addendum), §2 C (the whole of it — sessions
   85, 86, 87 and 88 are four different claims about the same thing, and the last one takes the
   re-opening back), §2 D and §5.** A is closed by measurement (session 83). B sums to 0.7–2.5 ms
   and has shipped −252 µs in four sessions. **C's image half is MARGINAL at 514 µs against its own
   1 000 µs floor — not near either threshold — and is not built.** D2 is divided to the bottom
   except for one block.
1. `C:/kyty/s88/FACTS.md` — the single source of truth. **§0, then §2 (the null control that
   caught the session's own instrument, and what it cost), §3.3–3.5 (the split, the verdict and the
   four reasons it is still an upper bound), §4.1 (the correction to session 87), §4.3 (what the
   residue is), §6 (a debt taken, run, and failed on admission) and §8 (all forty-seven
   predictions, including the three defects in predictions I wrote myself, and what the independent
   audit moved).**
2. `C:/kyty/s88/README.md` — the standing traps. The three that will bite first: **a null control
   you wrote before the run can catch your own instrument — write it so it can fail, and then
   believe it**; **where an `rdtsc` sits changes what it COSTS, not only what it reads**; and
   **an effect can be too big for the estimator** — `dap88a` moved cpu/draw by 9 %, moved the DRS
   rung with it, and was refused by the matched-pair estimator.
3. `docs/PLAN_82_bind.md` — route B. **Do not package from it without reading the source first.**
   Every line number in it is stale, session 85 refused three of its four proposed items on
   reading, and its item-3 design is superseded by `FACTS` s85 §8.1.

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s88` → `C:/kyty/s89` with a script modelled on
`C:/kyty/s87/s88_port.py` — **written fresh in the SOURCE directory**, because the copies of
earlier port scripts inside the harness have had their own `SRC` and `DST` rewritten to the same
path and are self-copy no-ops. It repairs the two things a literal rewrite breaks: the head of
every `--roots` chain (it becomes `s89` and **drops `s88`**) and `area_verdict.py`'s arithmetic
`range(88, 70, -1)`. `gates_base.txt` is **unchanged** — 1092 bytes, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `bindwit`, `bindalt`,
`proglap`, `drawmerge`, `bindlap`, `bdasplit`, `slotstat`, `slotstatcheck`, `bindpack2`,
`bindpack`, `bdalap`, `plkstat`, `mutwide`, `bindkey` and `bdabits` are deliberately absent from
it — which is also what gives every new counter a free arming proof in the pre-schedule window.
**Run `gen_gates.py --check` only.**

**Two traps that cost session 88 runs:**

* **A name already present in `gates_base.txt` cannot be overridden by appending it** —
  `FindAssignment` takes the **first** whole-word `name=`. `dawitloop`, `dapin`, `mutsite` and
  `recordthread` are in the file; assign such names **in the arm text**, which the gate-file pass
  then skips.
* **"exactly 0" on a schedule arm is unreachable on sums.** Session 86 recorded it, `pred/01` of
  session 88 named the statistic and passed, `pred/02` of the same session did not and both of its
  arming predictions are misses. **Write the statistic into the prediction.**

## 1. What session 88 settled

* **The memo-hit tail of `ResolveTextureWith` is 15.00 ns a slot; the proof is the other 50 %.**
  `W1` = 37.49, `W2` = 22.48 ns; the mark's price cancels because both arms take one timestamp a
  slot in the same kind of place — **to the precision null control C8 certifies, which is ±32 %**,
  so `skip88` is 10…20 ns and `ceiling88` is 440…590 µs. MARGINAL throughout.
* **`ceiling88` = `sl_img_dupv` × (19.66 + 15.00) = 514 µs a frame ⇒ MARGINAL**, against session
  87's 1 107 µs. **Route C's image half does not stay re-opened.** Margin +71 % above 300 and −49 %
  below 1 000 — **not near either edge**, unlike session 86's 2.5 % and session 87's 10.7 %.
  `sl_img_dupv` = 14 831.7 a frame, measured in that session's own run: the borrowed number was
  right to 0.3 %; the term nobody had measured was the one that moved.
* **A slot whose resolve does NOT take the memo-hit path costs 284 ns — 7.6× a hit — on 6.4 % of
  slots**, and **48.1 % of that population is the cheap null-descriptor path**, so the memo miss
  alone is **284…548 ns and is [NM]**. Splitting it is one counter, and `tnull_hit` already
  separates the population on the `FrameTrace-x` line.
* **The M1 witness loops inside the pipeline-cache lock cost 567.4 µs (clean) + 285.1 µs (live) =
  852.5 µs a frame = 34.7 % of `AheadTake` and 21.1 % of the 4 049 µs block** — against the ~82 % /
  ~48 % session 87 quoted from session 72 on a different binary and **honestly labelled a
  quotation**. A factor of **2.4** on the `AheadTake` share, which is within-run and [M], and
  **2.3** on the block share, whose 4 049 µs denominator is session 87's and is therefore [I].
* **816 µs of the 4.5 ms `PipelineCache::m_mutex` hold is the witness loops**, measured on
  `pl_prog_hold_us` moving with the knob in both runs.
* **A pre-registered null control caught the session's own instrument** — the first time in this
  record. `bl_res_us/bl_res_n` read −3.78 % between two arms that each take one timestamp a slot,
  because an `rdtsc` followed by dependent work costs a whole mark more than one followed by
  independent work. The defective instrument returned 24.05 ns where the repaired one returns
  15.00 — the repair moved the answer by 38 %, and the defective reading was **60 % too high**, in
  the direction that re-opens a route.

## 2. What is settled — do not reopen

* **Route A in every form** (`S` = 20.8 ms > 16.7 ms).
* **Route C at per-slot granularity** (session 85) **and route C's image half at per-stage
  granularity** (session 88: 514 µs, MARGINAL, `skip88` known to ±32 %, with four unmeasured
  reductions still inside it). **The verdict is not robust to the sealed rule's own allocation**:
  reading `FACTS` s85 §12.6c strictly — the 19.66 ns **is** the proof — gives **222 µs, CLOSED FOR
  GOOD**; the loosest reading gives 738 µs, still MARGINAL. **Every reading says do not build it.**
  **Do not re-open it without a NEW measured term**; the only one left — the witness share of the
  19.66 ns — **can only make it smaller**.
* **The two-pass split of the image loop** — refused on reading, `FACTS` s87 §2.1.
* **"Make the program lookup cheaper"** — 28.74 ns a call, 255 µs a frame.
* **Merging consecutive draws** — 0.668 % share an identical descriptor set.
* **A whole-stage binding memo**, four times now.
* **A `dause=0|1` ABBA** — it would go VOID; `FACTS` s87 §2.4.
* **The `std::map` of `SynchronizeBuffersInRange`**, **the BDA region walk**, **the record thread
  as `dapin`'s GPU carrier**, **`KYTY_GPU_TIME` as the instrument for that question**,
  **`PLAN_82_bind.md` item 6b**, **and `recordthread=0|1` as the `dapin` experiment** — it is a
  two-variable contrast (`FACTS` s88 §6).
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

### 3.1 FIRST: the residue of `AheadTake` — 1 607 µs a frame, 65 %, and now the largest unsplit block in the record

`da_take_us` is 2 459.5 µs a frame; the witness loops are 852.5 of it (§1) and **the other 1 607 µs
has never been looked at.** It is three things, all inside `PipelineCache::m_mutex`:

* the **two-probe open-addressed slot lookup**, `pipelineCache.cpp:2731-2905`;
* the **`dawitptr` prefetch pass** over `witness.live_runs`, `:786-805` — which **neither** value
  of `dawitloop` skips, so session 88's numbers do not contain it;
* **`CopyAheadResult`** and the singles loop (`:898-909`, `da_singles` = 0.000 a frame in this
  scene, so the singles are empty and the copy is not).

**Split it with the `proglap` idiom one level down**: a rolling mark chain inside `AheadTake`,
seeded from the timestamp `da_take_us` already takes at `pipelineCache.cpp:3069`, so the chain's
first mark is free. Three or four marks, never a per-probe pair.

**Pre-register the routing rule before the run.** Suggested shape, to be fixed in `pred/01` §7 of
that session with its own bands: if the copy dominates, the lever is the snapshot layout
(`snapdiff`/`snapswap` already ship and session 58 measured them); if the probe dominates, the
lever is the hash table; if the prefetch pass dominates, **it is the `dawitptr` gate's own cost and
that gate is already shipped by default 1**, so the number is a debt against a shipped default and
must be reported as one.

**And read `da_runs` = 82 543 a frame before you build anything** — it is already printed on every
`FrameTrace-draw` line, and 82 543 runs against 8 687 calls is 9.5 runs a call. **Sixth session in
six: look for the number on disk first.**

### 3.2 THEN: can `AheadTake` leave the lock?

`FACTS` s88 §4.2 measured that **816 µs of the 4.5 ms `PipelineCache::m_mutex` hold is the witness
loops**, and §4 measured that the whole of `AheadTake` — 2 459 µs — runs under it. The lock is
taken at `pipelineCache.cpp:4307` and released at `:4325`; `AheadTake` is called at `:3070`,
inside `Cache::Get`.

**This is a reading task before it is a coding task.** What the witness reads (`ShaderReadCache`,
the guest words, `MayHaveImages`, the page tables) and what `AheadTake` writes (the slot's
`taken` state, `CopyAheadResult`'s destination) decide whether the verification can be hoisted out
of the critical section or run speculatively before it. **Do not write a line until that list
exists**, and write the list into the session's `PLAN.md` §0 the way sessions 85–88 did — three of
the last four plan items that did not survive the source were caught exactly there.

### 3.3 The debts, ranked by what is now known

* **D1 — `BufferCache::UploadCopies`, 22.8 MiB a frame at 11 GB/s, ceiling ~2.1 ms.** **It is now
  the largest measured ceiling in the record that has never been started**, because route C's image
  half is 514 µs and D2's witness is 852 µs. A rewrite. Re-read session 28's caveats first.
* **`pg_pm_us` = 462 µs a frame at 52.1 ns a call.** Not the deque scan (1.06 candidates). It is
  `PushData::StartFor` plus the `specialization ==` compare, and which of the two is [NM].
* **`dapin`'s GPU cost, NINTH session.** Session 88 took it, ran the corrected single-variable
  contrast, and it **failed admission**: with the record path off the arms differ by ~9 % of CPU,
  which moves the DRS rung, which the matched-pair estimator refuses (area split +12.93 %, pair
  match 33.0 %). **The next step is an estimator that survives a DRS shift, or a contrast that does
  not cause one** — e.g. `dapin=1|3` (both pinned, different CCD) with the record path live.
  **Either take it with that design or strike it from §7.**
* **The witness share of the 19.66 ns of `RebindImages`** — the last unmeasured term inside
  `ceiling88`. **It can only lower 514 µs**, so it is worth a counter only if something else in
  that file is being touched anyway.
* **Route B items 2, 8, 10, 12 and the corrected item 3** (`FACTS` s85 §8).
* **`PipelineCache::m_mutex` splitting** — and §3.2 above is the precondition for it.

**Say the odds out loud before starting.** 16.7 ms needs ~15 ms removed. §3.1's block is 1.6 ms and
is **work**, not a proof, so unlike sessions 87–88 it is not bounded below by a correctness
argument — but nothing says it is removable either. **Expect hundreds of microseconds, not
milliseconds, and do not promise 60 FPS on the strength of it.** In this programme upper bounds
have now been wrong by 2.0×, 2.3×, 2.4×, 2.6×, 20× and — in the other direction — 4.3×.

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or
it failed.** A measurement gate's own ABBA satisfies it.

## 4. Do NOT

**New, from session 88:**

* **Do not write a null control you cannot imagine failing — and do not explain one away when it
  does.** C8 failed at −3.78 %, `wit88a`'s §3.1 numbers were not published, the instrument was
  repaired under a new sealed pre-registration, and the repaired run moved the answer by 38 %. The
  post-hoc explanation is in `FACTS` s88 §2 **and is labelled post-hoc**.
* **Do not assume two marks of equal count cost the same.** An `rdtsc` followed by work that
  depends on it costs a whole mark more than one followed by independent work — 6.9 ns a sampled
  slot, measured. **Put the two arms' marks in the same kind of place.**
* **Do not arm an instrument for a loop when it is sampled per slot.** The first version of
  `bindwit` stamped on memo hits the alternating phase never samples — ~165 µs a frame in one arm
  only. Found by reading the patched source before any number.
* **Do not run a contrast large enough to move the DRS rung.** `dap88a` was refused by its own
  admission criteria at +12.93 % area split. The matched-pair estimator is the admission gate, and
  a 9 % arm difference is outside what it will accept.
* **Do not write "exactly 0" about a counter on a schedule arm.** Straddle. Write the statistic.
* **Do not argue with a run that fails admission — replace it.** `dwl88a` (pair match 70.4 %) was
  replaced by `dwl88c` and is quoted nowhere in `FACTS.md`, including where it would have agreed.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming
proved by a counter inside the run — and the **pre-schedule window is free and stronger than a
median**; `guards.py` check 10 hashes the exe installed *now*, so compare check **lines**, not
verdicts, and do not rebuild between acceptance and the final answer; check 6 (cores) FAILs
routinely and is not an admission criterion; a gate enum entry goes immediately before `Count`
**and** its `DEFINITIONS` row goes last, in the same order — a knob's row goes in
`KNOB_DEFINITIONS` with its limit, and the clamp is strict `<`, so the limit itself is reachable;
**there is no `static_assert`**; every verify line needs a cap (32–64); never put a printf's format
string and its argument list in one patch call; a counter absent from `guards.py`'s `SELF_CHECKS`
is **never parsed**, so add the row before the first run; **no value-initialiser on a per-call
scratch array**; `dt_us` is not an endpoint inside the vblank plateau; the `_us` counters on
`FrameTrace-x` are ALREADY microseconds; **the first entry after a fresh build hangs** — three of
ten entries in session 88, every one absorbed by `--warmup-first` or a second attempt.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b` | **MEASURED — closes route A** |
| **the memo-hit tail of `ResolveTextureWith`** | **15.00 ns a slot; the proof is the other 50 %** | **MEASURED (s88)** |
| **route C's image half, by the sealed rule** | **514 µs, MARGINAL** (±32 %; 222 µs under a stricter allocation, 738 under a looser one) | **NOT RE-OPENED; s87's 1 107 µs did not survive its missing term** |
| a slot that does NOT take the memo-hit path | **284 ns, 7.6× a hit, on 6.4 % of slots** | **MEASURED (s88); 48.1 % of it is the null path, so the memo miss alone is 284…548 ns, [NM]** |
| **D2: the M1 witness loops inside the lock** | **567.4 + 285.1 = 852.5 µs = 34.7 % of `AheadTake`** | **MEASURED (s88); s72's quotation was 2.4× high** |
| **D2: the residue of `AheadTake`** | **1 607 µs a frame, 65 %** | **NOT SPLIT — §3.1, and now the largest unsplit block** |
| of the 4.5 ms `PipelineCache::m_mutex` hold, the witness | **816 µs** | **MEASURED (s88) — §3.2** |
| D2: draw-thread `MaterializeResources` | 667 µs = 16.5 %, 2.68 µs a call | MEASURED (s87) |
| D2: the permutation phase | 462 µs = 11.4 %, 52.1 ns a call | **MEASURED — unattributed, §3.3** |
| D4: identical descriptor set (a real merge) | 0.668 % | MEASURED — merging is dead |
| **D1, staging `memcpy`** | **~2 100 µs** | **NOT STARTED — now the largest untouched ceiling** |
| `dapin`'s GPU cost | +1.961 % ± 0.165 %, ×5; the corrected contrast FAILED admission | **UNEXPLAINED, ninth session** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured since session 82 |

**The honest statement of the task.** Sessions 83–86 measured and closed the bookkeeping. Session
87 divided the two largest unopened blocks and found both to be *the price of proving a cached
answer is still good* — and published two figures for it, each with one term it had not measured.
**Session 88 measured both terms and both figures halved: the proof is half of a memo-hit resolve,
not all of it, and the witness loops are a fifth of the block under the lock, not a half.** What is
left in those blocks is **work** — a two-probe lookup, a prefetch pass and a copy on one side, a
`ConfigureImageSource` / `TouchImage` / DCC-adoption tail on the other. **Session 89 is for opening
the 1 607 µs nobody has looked at, and for finding out whether any of it has to be under the
lock.**
