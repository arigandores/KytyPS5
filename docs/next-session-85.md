# Session 85 — the brief

Session 84's commit is on `merge-upstream`. **Source changed, a default changed and the binary was
rebuilt**; the installed `kyty_emulator.exe` is `f0e2ddf4c4c1bb40d301…`, 23 586 304 bytes. Harness —
**`C:/kyty/s84`**, port it to `C:/kyty/s85`.

## 0. Read first

0. **`docs/ROADMAP.md` §0 and §2 C.** Route A is closed by measurement (`S` = 20 838 µs against a
   16 667 µs frame budget; session 83). **Route C's ceiling is now measured too: 64.2 % of the
   109 836 descriptor slot-bindings a frame carry the value the same stage bound in the previous
   committed draw — 87.4 % of image bindings, 95.9 % of sampler slots, 51.3 % of buffer slots —
   while only 2.06 % of stages repeat everything. All of those are UPPER BOUNDS and the unit price
   is [NM].** Do not build any step of `docs/DESIGN_82_parallel.md`; it is a closed design.
1. `C:/kyty/s84/FACTS.md` — the single source of truth. **§2 (eleven retractions the audit forced
   on the first draft — read this before believing any earlier summary), §3 (the census, its three
   upward biases and the unit price that contradicts route C's premise), §4 (the package that
   shipped and the sub-edit that was refused), §5 (`PrepareBda` is a fixed cost), §9 (all nineteen
   predictions scored).**
2. `C:/kyty/s84/README.md` — the standing traps.
3. `docs/PLAN_82_bind.md` — route B, thirteen items. Items 1, 4, 9 and 11 have shipped; item 5's
   premise is bounded out; item 7 is not A/B-able inside one binary. **Every `descriptors.cpp` line
   number in that file is stale: +118 for item 0 and +298/+327 for item 11 against the tree session
   84 leaves. Anchor on verbatim text.**

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s84` → `C:/kyty/s85`. `gates_base.txt` is **unchanged** — 1092 bytes,
99 names, sha256 `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `slotstat`,
`bdalap`, `bindpack`, `bindpackcheck`, `mutwide`, `plkstat`, `bindkey` and `bdabits` are
deliberately absent from it. **Run `gen_gates.py --check` only.** The s84 port already repaired the
`--roots` chains a second time — verify they survived, and read the port's diagnostic.

## 1. What session 84 settled

* **Route C has a number.** `slp84b`, VALID on all six criteria (pair match 134/134, split
  −0.001 %, work −0.064 %, gap +0.004 pp): `R_img` **87.44 %**, `R_view` 87.45 %, `R_smp`
  **95.87 %**, `R_buf` **51.26 %** (33.35 % before the stream-ring slots that cannot repeat are
  removed), `R_stage` **2.06 %**, all slots **64.23 %**. Arming: `sl_img_n` against `b_texn`
  +0.02 %, `sl_buf_n` against `bb_n` −0.01 %, `sl_over` exactly 0, every `sl_*` 0 in arm 0. The
  instrument costs **+274.1 ± 75.2 µs**, about 2.5 ns a slot.
* **Read them as UPPER BOUNDS.** `FACTS` s84 §3.5 names three biases, all upward, that the census's
  missing self-check would have bounded: a null T# resolves to a **real** shared image and a null
  buffer to a **constant** descriptor, so degenerate bindings count as repeats (~2.9 % of image
  slots; buffers [NM]); a `DynamicStorage` binding is N descriptor elements but one count, compared
  on element 0; and the shadow row is keyed by **positional index with no shader identity**, so a
  slot is compared against another slot's history whenever the previous draw ran a different shader
  (upper bound 24.8 % of stage commits). **`PLAN.md` declared a `SlotStatVerify`/`sl_bad` gate and
  it was never built** — building it is the cheapest thing session 85 can do to the census.
* **`slp84a` was VOID** (area split −1.055 % against a 1.0 % limit) and its contrast is quoted
  nowhere. Two of its six census ratios sit within 0.05 pp of the valid run and the worst, `R_buf`,
  is 0.40 pp away; `pred/02_slotstat.md` §5 had fixed **in advance** that a void run's census is a
  consistency reading and nothing more.
* **The binding-path package SHIPPED.** Four items now (`PLAN_82_bind.md` 1, 4, 9 and 11), measured
  on `bpk84a`, VALID on all six criteria: **`cpu_net_us` −251.7 ± 82.8 µs, t = −6.08**,
  `cpu/draw` −0.817 % ± 0.140 %, t = −11.70 over 117 matched pairs, `gpu_busy_us` +0.069 % (noise),
  `da_take_us` unmoved. Against the **−150 µs** threshold sealed before the run → **SHIP**, and the
  bar was not moved. Self-check `bp_bad` = 0 over 1 952 frames; video `bpc84a` 5 986 presents,
  **0 one-frame glitches**; `acc84a` confirms the compiled default is live.
* **`PrepareBda` costs 2 234.5 µs a frame, essentially all of it scan, and the scan is a FIXED
  cost.** A probe costs **under 0.021 µs** (resolution-limited: 14.5 ns on the arm sums, and the
  printer truncates). OLS over 8 026 frames: **`bda_scan_us` = 1 875.1 + 16.53 × misses**, so a 4x
  change in the miss count buys 1.3x the time. **~1.88 ms is paid by whichever call scans first**,
  and what costs that much before the per-range work begins is [NM] — session 83 bounded the
  `std::map` descents at ≤ 0.35 ms. The 2 181 µs of `bind78a` stands, within 2.5 %.
* **A `Lap` would not have measured it.** `FrameStats::Lap` takes its timestamp under
  `TimingsEnabled()`, false under `lite` — the same predicate that makes `bda_us` read 0. Use the
  `plkstat` idiom.

## 2. What is settled — do not reopen

* **Route A in every form** (`S` = 20.8 ms > 16.7 ms, session 83).
* **A whole-stage binding memo**, for the third time and now at slot granularity: `R_stage` = 2.06 %.
* **Widening `bindkey`**: the key carries a per-object guest pointer and changes every draw by
  construction. Table width cannot move a hit rate of a key that never repeats.
* **The `std::map` of `SynchronizeBuffersInRange` as the carrier of `bda_us`** (≤ 0.35 ms of 2.23).
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

The rule is unchanged and not negotiable: **the session ends with a source change that was A/B'd on
this machine, or it failed.**

### 3.1 Route C's unit price — the number that decides whether 64 % is worth anything

The census is a **population**. `ROADMAP.md` §2 C says ~5–7 ms of the frame is the price of
checking memos that hit, and 64.2 % of the slots are unchanged — but **what one descriptor slot
costs is [NM]**, and session 82's trap (17 518 region visits that looked like 1 ms and measured
−50.8 ± 87.5) is exactly this shape. Two ways to price it, in order of cost:

1. **Measure inside the emulator, and reconcile the contradiction first.** The only per-slot price
   ever measured here is the census instrument's own **2.48 ns** (272.2 µs over 109 836 slots),
   against the **52.6–73.7 ns/slot** that route C's 5–7 ms premise implies over ~95 000 slots — a
   factor of 21–30. The census also sits in `mh_emit_us` while the 5–7 ms is spent in
   `mh_bind_us`. Until those are reconciled the 64 % is not attached to the cost it is supposed to
   bound. A `plkstat`-idiom split of `CommitBindings` into "build the writes" and "issue them"
   would say how much of `mh_emit_us` is the write-list build.
2. **Price the exploit directly.** The 87.4 % figure is about **images**, and the obvious shape is
   not a partial update but a **split set layout**: the static image and sampler descriptors in one
   set bound once, the volatile buffer descriptors in another. That is a large change and it must
   be costed on a microbenchmark before a line of it is written in the emulator.

**Do not build the exploit this session without a measured unit price.** The census licenses a
ceiling, not a saving, and the report says so in three places.

### 3.2 Route B's next package

`PLAN_82_bind.md` items **2** (texture-memo associativity, 250–550 µs, NOT RESOLVED), **3**
(`ImageDesc` by reference on a memo hit, 150–300 µs), **6** (buffer epoch + clean verdict,
150–400 µs combined) and **8** (const-bank copy batching, 40–120 µs) are the unshipped plausible
ones. Package them, pre-register a threshold **in µs, in the statistic `endpoint84.py` prints**,
and measure once. Items 10 and 12 need a counter before they need a patch.

### 3.3 The debts

* **`dapin`'s GPU cost** +1.238 %, replicated four times, unexplained for a **sixth** session. One
  `KYTY_GPU_TIME` pair on a `dapin` ABBA. It is the oldest open number in the record.
* **The ~1.88 ms FIXED part of `bda_scan_us`** — a `plkstat`-idiom split inside
  `SynchronizeBuffersInRange`, separating what is paid once a frame from what is paid per range.
  One run.
* **The census's missing self-check.** `sl_bad` + a `SlotStatVerify` gate that re-derives a slot's
  identity a second way and compares, plus counters for the two unmeasured populations (null buffer
  slots, `DynamicStorage` mip bindings). One build, no run of its own — it rides in any ABBA.

## 4. Do NOT

**New, from session 84:**

* **Do not put a `Lap` anywhere in a measurement run and expect a number.** `Lap` and `Scope` both
  take their timestamp under `TimingsEnabled()`, which is **false** under `KYTY_FRAME_TRACE=lite`.
  Only the `plkstat` idiom — a timestamp under `Enabled()`, differenced by hand — reads.
* **Do not read a cost off a population, and do not read a marginal price off an average.** 88 % of
  `PrepareBda` calls are probes and 99.9 % of its time is scan — the session-82 trap pointed the
  other way. And "2 232.5 µs ÷ 21 misses = 106.3 µs a miss" was wrong twice over: the denominator
  was a difference of medians, and the true marginal cost is **16.5 µs** against a **1 875 µs**
  fixed part.
* **Name the estimator in the pre-registration.** `pred/02` defined the census ratios as ratios of
  counters and fixed no statistic; ratio-of-medians and ratio-of-sums differ by **1.96 pp** on
  `R_buf`, which is 5x the void-vs-valid gap the first draft was calling agreement.
* **Score every prediction, not the ones you remember.** Session 84's first draft scored 6 of 19
  and both of its misses were among the 13 it skipped.
* **Do not trust `guards.py` check 2 to cover a self-check you just wrote.** It only sees labels
  listed in its own `SELF_CHECKS` table; a new `…Verify: MISMATCH` line is silently discarded until
  you add the row. Session 83 ran two self-check runs believing otherwise.
* **Do not anchor a patch on a line number from `PLAN_82_bind.md` or from any FACTS older than one
  session.** The drift is +118 to +141 lines and two of those anchors now point at live, unrelated
  code.
* **Do not raise a shipping threshold because the package grew.** −150 µs answers "is a default
  change worth making"; it does not depend on item count. Session 84 kept it and shipped at −251.7.
* **Do not ship a change whose correctness cannot be checked.** Item 11's sub-range push-constant
  write was refused for that reason alone, and its 20–60 µs forgone.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming proved
by a counter inside the run, with the **median and the tail**; `guards.py` check 10 hashes the exe
installed *now*, so compare check **lines**, not verdicts, and do not rebuild between acceptance and
the final answer; check 6 (cores) FAILs routinely and is not an admission criterion; a gate enum
entry goes immediately before `Count` **and** its `DEFINITIONS` row goes last, in the same order;
every verify line needs a cap (32–64); never put a printf's format string and its argument list in
one patch call; `dt_us` is not an endpoint inside the vblank plateau.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b` | **MEASURED — closes route A** |
| route C's ceiling | **64.23 % of 109 836 slot-bindings**, `slp84b` | **MEASURED, upper bound — the lever is per-slot** |
| …of which image slots | **87.44 %** (`R_view` 87.45 %) | **MEASURED** |
| …of which sampler slots | **95.87 %** | **MEASURED** |
| …stages repeating everything | **2.06 %** | **MEASURED — a whole-stage memo is dead** |
| **route C's UNIT PRICE** | — | **NOT MEASURED — the only thing between the census and a saving** |
| the four-item `bindpack` package | **−251.7 ± 82.8 µs**, `bpk84a` | **SHIPPED, default 1** |
| `PrepareBda` | **2 234.5 µs/frame, 99.9 % scan** | **MEASURED** |
| …of which not `std::map` descents | ~1.9 ms | **NOT ATTRIBUTED** |
| `dapin`'s GPU cost | +1.238 %, ×4 | **UNEXPLAINED, sixth session** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured in session 84 |

**The honest statement of the task.** Session 83 closed the direction that would have made the
frame parallel. Session 84 measured the one that would make it smaller, and found that two thirds
of the work a frame does at the descriptor level is work it already did last draw — but also that
the repetition is spread so that only one stage in fifty repeats completely, which is why every
instrument built on hashing a stage or a set as a unit has read near zero for three sessions. The
next number that matters is not another population. **It is the price of one descriptor slot, and
until that exists the 64 % is a ceiling and nothing else.**
