# Session 87 — the brief

**Session 86 opened route D and divided two of its four blocks, and both divisions point at the same
thing: the money is in WORK, not in bookkeeping.** Read `docs/ROADMAP.md` **§0.1** first — it
separates *"three routes with a measured ceiling do not reach 60 FPS"* (proved) from *"60 FPS is
unreachable"* (**not** proved), and those two get conflated every time.

Session 86's commit is on `merge-upstream`. **Source changed and the binary was rebuilt, but NO
default changed**: the installed `kyty_emulator.exe` is `813b8c9dd68a6f0a…`, 23 607 296 bytes, and
all three gates session 86 added are **0**, as are the two it extended. Harness — **`C:/kyty/s86`**,
port it to `C:/kyty/s87`.

## 0. Read first

0. **`docs/ROADMAP.md` §0.1, §2 C, §2 D and §5.** A is closed by measurement (`S` = 20 838 µs
   against a 16 667 µs budget, session 83). C is closed at per-slot granularity (session 85) and its
   last idea is closed by its own pre-registered floor (session 86, 292.5 µs against 300) — **but
   §2 C also carries a correction session 86 made against its own record, and it is the reason the
   first item of §3 exists.** B sums to 0.7–2.5 ms and has shipped −252 µs in four sessions. D is
   the only route with anything open, and §5 now orders it by measurement rather than by guess.
1. `C:/kyty/s86/FACTS.md` — the single source of truth. **§0, then §2 (four corrections to the
   record, one of them to session 86's own instrument), §5 (what `mh_prog` actually is — read this
   before anything else in §3), §6.3 (route C's ceiling corrected 4.3× and why the verdict
   survives), §3.5 (why D4's headline is not the bucket a merge would use), §7.3 (the two-arm unit
   price and why the memo's miss population is 24 % dearer than an average call), §9 (all
   forty-three predictions, including the two I wrote badly).**
2. `C:/kyty/s86/README.md` — the standing traps. The three that will bite first: **a cap you assume
   must be a cap something enforces**; **a counter that rides both arms cannot have its own price
   measured, so do not predict it**; and **the number you need may already be in last session's
   log** — `pmemo_pipe` answered D4's necessary condition at zero cost, the fourth time in four
   sessions.
3. `docs/PLAN_82_bind.md` — route B. **Do not package from it without reading the source first.**
   Every line number in it is stale, session 85 refused three of its four proposed items on reading,
   and its item-3 design is superseded by `FACTS` s85 §8.1.

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s86` → `C:/kyty/s87` with a script modelled on `C:/kyty/s85/s86_port.py`,
which repairs the two things a literal rewrite breaks: the head of every `--roots` chain (it becomes
`s87` and **drops `s86`**) and `area_verdict.py`'s arithmetic `range(86, 70, -1)`. `gates_base.txt`
is **unchanged** — 1092 bytes, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `bindlap`, `bdasplit`,
`slotstat`, `slotstatcheck`, `bindpack2`, `bindpack2check`, `bindpack`, `bdalap`, `plkstat`,
`mutwide`, `bindkey`, `bdabits`, `proglap`, `drawmerge` and `drawmergecheck` are deliberately absent
from it — which is also what gives every new counter a free arming proof in the pre-schedule window.
**Run `gen_gates.py --check` only.**

## 1. What session 86 settled

* **`mh_prog` is not a lookup.** `pl_prog_hold_us` is **69.72 %** of the phase (reproducing session
  83's 68.9 %), `pg_get_us` is 96 % of the hold — and inside it the key build plus
  `unordered_map::find` is **255 µs a frame, 28.74 ns a call, 4.3 % of the phase**, while
  **materialisation is 93.65 % = 3 764 µs a frame = 11.9 % of the whole frame.** `pg_cold_n` and
  `pg_compile_n` read 0.00, so nothing is contaminated by translation. `pg_n == pl_prog_n` exactly.
* **`PrepareBindings` is 76.2 % its image loop**, at **65.25 ns a slot** over 47 885 slots a frame,
  against 8.4 % for samplers (31.02 ns) and 9.4 % for the `shader_data` copy. `bl_res_n` matches
  `bl_img_n` to +0.0001 % and no frame has the parts exceeding the whole.
* **Route C's image ceiling was published on an incomplete price and is 4.3× larger.** A repeating
  image slot costs **19.66 ns in `RebindImages` plus 65.25 ns in `PrepareBindings` = 84.91 ns**, so
  40 675 repeating slots are **3 454 µs a frame, not the 800 µs `FACTS` s85 §12.6 published.** The
  verdict survives — `BindImage`, the blocker session 85 named, lives **inside** the newly measured
  term — but the number did not.
* **Route D4 is MARGINAL and its headline misleads.** M = 0.1822 by the rule sealed before the run,
  and **77.53 % of consecutive draws already share a pipeline**. But a true instanced-merge
  candidate — identical descriptor set, which is what `vkCmdDrawMultiIndexedEXT` and instancing
  require — is **0.668 %, 33 draws a frame out of 4 937.** All the mass is `dm_buf1_nr` (17.55 %),
  which needs the game's per-object buffers behind an index.
* **Route C's last idea is closed by 2.5 %.** `sl_img_dupv` × 19.66 ns = **292.5 µs** against the
  300 µs floor `pred/02` §6 sealed; the slot threshold sealed beside it was 15 300 and the
  measurement is 14 875. Two things push it further down and none pushes it up.
* **The program key's unit price, by a shipped gate rather than a regression.** `progmemo=0` makes
  every call a miss: **`K_miss` = 73.79 ns, `K_hit` = 14.53 ns**, and the model reproduces the raw
  arm difference to **+0.30 %**. Inside the `progmemo=1` arm the memo's own misses cost **91.57 ns**
  — the self-selected miss population is **24 % dearer** than an average call. `progmemo=1` is worth
  **−699.0 ± 86.3 µs**, confirming a default shipped in session 60.

## 2. What is settled — do not reopen

* **Route A in every form** (`S` = 20.8 ms > 16.7 ms).
* **Route C at per-slot granularity** (session 85) **and its witness-amortisation idea** (session 86,
  292.5 µs against its own 300 µs floor). What is NOT closed is §3.1 below.
* **Merging consecutive draws** — 0.668 % share an identical descriptor set.
* **"Make the program lookup cheaper"** — 28.74 ns a call, 255 µs a frame.
* **The permutation `std::deque` scan** — 1.059 candidates examined a call.
* **A whole-stage binding memo**, four times now.
* **The `std::map` of `SynchronizeBuffersInRange`** (0.018 ms), **the BDA region walk** (4.8 ns a
  visit), **the record thread as `dapin`'s GPU carrier**, **`KYTY_GPU_TIME` as the instrument for
  that question**, **`PLAN_82_bind.md` item 6b**.
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

### 3.1 FIRST: split `bl_res_us` into `ResolveTextureWith` and `BindImage`

**This is the cheapest decisive measurement left in the record and it settles a number this
programme has already published twice.** `bl_res_us` is 3 124.6 µs a frame at 65.25 ns a slot, and
it contains both the resolution (which a memo could in principle serve) and `BindImage` (which
session 85 named as a hard blocker: it arms `is_bound` / `force_general` / `shader_write`, which
`ResetBindings` clears every draw and `AcquireRenderTargets` reads to choose `eGeneral` over
`eColorAttachmentOptimal`).

Do it **without a per-slot timestamp pair** — the rule sessions 85 and 86 both kept, because a pair
costs ~9 ns against the quantity being measured. The image loop can be split into two passes over
`prepared.images`, and the tree's own comment licenses it: *"`BindImage` does not look at
`prepared.images`, so running it after the insertion changes nothing."* Verify that comment against
the source before relying on it — it is a comment, not a measurement. Then two rolling marks give
`bl_rsv_us` and `bl_bind_us` at stage granularity.

**Pre-register the routing rule before the run**: what value of `bl_rsv_us / bl_res_us` would make
route C's image half worth re-opening, and what value closes it for good. Note that the answer is
bounded below by the witness argument of `FACTS` s85 §12.5, which this session does not get to
re-argue.

### 3.2 THEN: divide the 3 764 µs of materialisation under the pipeline-cache lock

**This is the largest unsplit block in the entire record — larger than route B's whole ceiling, and
11.9 % of the frame — and nothing in this programme has ever looked at it.** It is inside
`ProgramCache::Get`, between `lap.Mark(ProgKeyNs)` and the four returns, and its parts are named in
the source: `AheadNote` / `AheadTake` (gate `drawahead`, default 1), the SRT memo (`MemoFind` /
`MemoVerify`, gate `srtmemo`), `MaterializeResources`, the permutation `find_if`, and `Compile` on
the cold path (`pg_compile_n` = 0, so it is not in the settled window).

Add `proglap` counters for each, on the same `LapScope` idiom, still **`slot < 2` only**. Three or
four marks a call. **Before writing them, read what is already there**: `DrawAheadTakeNs`
(`da_take_us`) already times `AheadTake` and reads under lite — it is the bracketing timer every run
of this programme already reports, at ~270 ns a take. `SrtMemoHits` / `SrtMemoMisses` /
`SrtMemoStale` already count the SRT memo's outcomes. **Grep before building, the fifth time.**

**And the shipped gates are the source of variation:** `drawahead`, `srtmemo` and `dause` are all
knobs that move the hit rate without moving the populations — the `texfast` / `progmemo` trick,
twice validated. An ABBA on one of them prices its half exactly, without a regression.

### 3.3 The debts, unchanged and unstarted

* **`dapin`'s GPU cost, seventh session.** +1.961 % ± 0.165 %, five replications, visible only with
  the record thread live and **not** caused by that thread's placement. A **`recordthread=0|1` ABBA
  with `dapin` pinned at 3** separates existence from affinity in one run. Session 86 did not take
  it and says so.
* **D1 — `BufferCache::UploadCopies`**, 22.8 MiB a frame at 11 GB/s, ceiling ~2.1 ms. A rewrite, not
  a measurement. Re-read session 28's caveats (`KYTY_HOST_IMPORT_REUPLOAD_TICKS`, the first-piece
  stalls) before touching it.
* **`PipelineCache::m_mutex`, 4.2 ms a frame of hold** — and §3.2 now says what is inside it, which
  is the precondition for asking whether it can be split.
* **Route B items 2, 8, 10, 12 and the corrected item 3** (`FACTS` s85 §8).
* **The per-image fraction `f` of the 19.66 ns witness** — [NM], and it is the term that decides how
  much of an upper bound 292.5 µs really is.

**Say the odds out loud before starting.** 16.7 ms needs ~15 ms removed. The two blocks §3.1 and
§3.2 divide total 6.9 ms, and dividing a block is not removing it. In this programme upper bounds
have been wrong by 2.6×, 20× and 2.3×, and one published ceiling has now been wrong by 4.3× in the
**other** direction. **Expect single-digit milliseconds from route D and do not promise 60 FPS on
the strength of it.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.** A measurement gate's own ABBA satisfies it.

## 4. Do NOT

**New, from session 86:**

* **Do not cap a census by analogy.** `drawmerge` capped the push payload at 32 dwords because
  images cap at 64 and buffers at 32 — but `ShaderDataDwords()` is bounded by nothing, and because
  an over-cap draw is excluded by design the cap silently deleted 8.7 % of the population.
  **Check that every bound you assume is a bound something enforces.**
* **Do not predict the price of an instrument you are riding in both arms.** `PLAN.md` §2 made that
  choice so the readings would be within-arm, and thereby made prediction I1 unevaluable.
* **Do not write "exactly 0" about a counter on a scheduled arm.** The block-boundary straddle is
  1.68–1.71 % of the armed value in both ABBA runs and 100 % of it sits at distance 0 from a block
  start. Write the statistic — median or sum — into the prediction.
* **Do not quote a memo's within-arm miss price as the price of the work.** 91.57 ns against
  73.79 ns; the miss population is self-selected and 24 % dearer.
* **Do not treat a debt named in a §9 as discharged.** `FACTS` s85 §9 recorded that route C's
  ceiling had an unmeasured second term. It did, and it was 3.3× larger than the measured one.
* **Do not report a census headline without naming which sub-bucket carries it.** D4's M = 0.18 and
  the merge it appears to license is worth 0.668 %.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming proved
by a counter inside the run — and the **pre-schedule window is free and stronger than a median**;
`guards.py` check 10 hashes the exe installed *now*, so compare check **lines**, not verdicts, and
do not rebuild between acceptance and the final answer; check 6 (cores) FAILs routinely and is not
an admission criterion; a gate enum entry goes immediately before `Count` **and** its `DEFINITIONS`
row goes last, in the same order — **and there is no `static_assert`**; every verify line needs a cap
(32–64); never put a printf's format string and its argument list in one patch call; a counter absent
from `guards.py`'s `SELF_CHECKS` is **never parsed**, so add the row before the first run; **no
value-initialiser on a per-call scratch array**; `dt_us` is not an endpoint inside the vblank
plateau; the `_us` counters on `FrameTrace-x` are ALREADY microseconds.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b` | **MEASURED — closes route A** |
| **D2: `mh_prog`, the lookup half** | **255 µs a frame, 28.74 ns a call, 4.3 %** | **MEASURED — the phase was misnamed** |
| **D2: resource materialisation under the lock** | **3 764 µs a frame = 11.9 % of the frame** | **NOT DIVIDED — §3.2, the largest unsplit block left** |
| **D3: `PrepareBindings`, the image loop** | **3 124.6 µs, 65.25 ns a slot, 76.2 %** | **MEASURED** |
| …split into resolve and `BindImage` | — | **NOT MEASURED — §3.1** |
| **route C's image ceiling, corrected** | **3 454 µs, not 800** | **MEASURED — verdict unchanged, number was not** |
| **D4: consecutive draws sharing a pipeline** | **77.53 %** | **MEASURED** |
| **D4: identical descriptor set (a real merge)** | **0.668 %** | **MEASURED — merging is dead** |
| **D4: one buffer binding apart** | **17.55 %**, M = 0.1822 | **MARGINAL — needs bindless** |
| route C's last idea | **292.5 µs against a 300 µs floor** | **CLOSED, margin 2.5 %** |
| the program key | **73.79 ns a miss / 14.53 ns a hit** | **MEASURED by a shipped gate** |
| `progmemo=1`, shipped session 60 | **−699.0 ± 86.3 µs** | **CONFIRMED** |
| D1, staging `memcpy` | ~2 100 µs | **NOT STARTED** |
| `dapin`'s GPU cost | +1.961 % ± 0.165 %, ×5 | **UNEXPLAINED, seventh session** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured since session 82 |

**The honest statement of the task.** Sessions 83–85 measured, priced and closed the bookkeeping:
parallel recording, the descriptor slot, the memo check. Session 86 asked what the two largest
remaining blocks actually contain, and the answer in both cases was **not bookkeeping**: 3 764 µs of
resource materialisation under the pipeline-cache lock and 3 125 µs of texture resolution in the
bind phase, neither of which has ever been divided. **That is 6.9 ms of a 31.6 ms frame in two
blocks nobody has opened, and opening them is what session 87 is for.**
