# Session 86 — the brief

**Session 85 closed route C at per-slot granularity after this brief's first draft was written.**
§1 and §3.2 carry the verdict; read them before anything else in here.

Session 85's commit is on `merge-upstream`. **Source changed and the binary was rebuilt, but NO
default changed**: the installed `kyty_emulator.exe` is `24476c7b7a66a652…`, 23 595 520 bytes, and
all five gates session 85 added are **0**. Harness — **`C:/kyty/s85`**, port it to `C:/kyty/s86`.

## 0. Read first

0. **`docs/ROADMAP.md` §0 and §2 C.** Route A is closed by measurement (`S` = 20 838 µs against a
   16 667 µs frame budget; session 83). **Route C is closed at per-slot granularity by measurement
   (session 85):** the descriptor write costs ~1 ns, deciding to skip it costs more than skipping
   it saves, and the recoverable part was cashed by `texfast` in session 59 and is worth 1 527 µs a
   frame. What remains of route C is **one unmeasured idea** (§3.2) and **one unsplit block**
   (§3.1). Do not build any step of `docs/DESIGN_82_parallel.md`; it is a closed design.
1. `C:/kyty/s85/FACTS.md` — the single source of truth. **§12 FIRST (the price of the exploit and
   route C's verdict), then §2 (six corrections to the record, all found by reading before any
   number), §3 (the unit price, and §3.5 where the regression was declared uninformative by a rule
   fixed in advance — note §3.4 carries a retraction the same session issued against itself),
   §4 (the census with two biases measured and one found to be ZERO), §5 (`bda_scan_us` is a
   `memcpy`), §6 (the package that did not pay and the three items refused), §8 (two corrected
   designs), §10 (all forty-six predictions scored).**
2. `C:/kyty/s85/README.md` — the standing traps. The two that will bite first: **a mechanism the
   brief asks you to build may already be shipped** (twice in three sessions now), and **a
   measurement the record prescribes may be the wrong instrument** (six sessions of `dapin` went
   into one).
3. `docs/PLAN_82_bind.md` — route B. **Do not package from it without reading the source first.**
   Session 85 read four of its items and kept one; of the three it dropped, **two were wrong, not
   small** (item 6b is unsound as written; item 3 names three consumers where there are five).
   Every line number in that file is stale.

**Check the byte count of anything large you read.**

**Harness:** port `C:/kyty/s85` → `C:/kyty/s86` with a script modelled on
`C:/kyty/s84/s85_port.py`, which repairs the two things a literal rewrite breaks: the head of every
`--roots` chain (it becomes `s86` and **drops `s85`**) and `area_verdict.py`'s arithmetic
`range(85, 70, -1)`. `gates_base.txt` is **unchanged** — 1092 bytes, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `bindlap`, `bdasplit`,
`slotstat`, `slotstatcheck`, `bindpack2`, `bindpack2check`, `bindpack`, `bdalap`, `plkstat`,
`mutwide`, `bindkey` and `bdabits` are deliberately absent from it. **Run `gen_gates.py --check`
only.**

## 1. What session 85 settled

* **Route C's unit price.** `blp85a`, VALID on all six criteria: **`P_img` = 22.82 ns**,
  **`P_buf` = 77.07 ns**, `P_prep` = 428.64 ns **a stage**, all as ratios of sums (the estimator was
  named in the pre-registration; the ratio of medians agrees to 1.2 %). The instrument costs
  +357.1 ± 72.8 µs. **The 21-to-30-fold contradiction of `ROADMAP` §2 C is resolved and both
  earlier numbers were right about different things:** the premise's 52.6–73.7 ns band matches the
  **buffer** side almost exactly and overstates the image side by 2.3–3.2×, while session 84's
  2.48 ns was never the same quantity.
* **The ceiling, in microseconds for the first time.** 40 664 repeating image slots × 22.82 ns =
  **928 µs** and 15 275 repeating buffer slots × 77.07 ns = **1 177 µs**, total **≈ 2 105 µs a
  frame** — with the buffer half an **upper attribution**, because `P_buf` is an average over hit
  and miss slots that this run could not decompose (`buffast` is 0). **`ROADMAP` §2 C's "5–7 ms of
  memo-check price" is the right order for the whole reuse path (4 824 µs) but at most 2.1 ms of it
  stands on slots that repeat.**
* **The marginal price is NOT separable in this scene, and that was a pre-registered outcome.**
  R² = 0.80 but max VIF **60.9** against a limit of 20 fixed before the run, regressor correlations
  +0.966…+0.990. The coefficients decide nothing and prediction U7 is scored NOT EVALUATED.
* **The census kept every number and lost two of its three biases.** `R_img` reproduces at
  **87.432 %**. Bias 3 **eliminated** by keying on `shader_hash`: `R_img` → **84.933 %**, all slots
  64.67 → **61.78 %**, so the bias was worth **−2.89 pp** and the shader-change rate is **9.35 %**
  against session 84's 24.8 % upper bound. Bias 1 measured on both halves (2.956 % of image slots,
  **2.370 %** of buffer slots — the half that was [NM]). **Bias 2 is ZERO**: no `DynamicStorage`
  multi-mip binding exists in Sky Garden. `sl_bad` = 0, and it is an **element-count** check, not a
  value check, which `pred/02` §6 said before it was built.
* **`bda_scan_us` is a `memcpy`.** `bda_up_us` **2 121 µs** of `bda_walk_us` **2 287** = **92.7 %**,
  and that is the staging copy of **22 761 KiB a frame at 10.99 GB/s**. The frame's first scanning
  `PrepareBda` costs **977 µs in one call** against 55.7 µs for each of 24 later ones — **17.5×**,
  but the 24 still carry 58 % of the total. **Session 83's `std::map` bound was 20× too loose**
  (0.018 ms, not 0.18…0.35), and a region visit costs **4.8 ns**, which is why `bdabits` could
  never have paid.
* **Route B's package was one item and it did not pay.** `bindpack2` = `PLAN_82_bind.md` item 6a:
  **−35.9 ± 81.2 µs, t = −0.88** against the −150 µs bar sealed before the run. All four falsifiers
  unmoved, `bp2_bad` = 0, and `be_race` — the race window the change widens — **measured at
  0.0111 % of short circuits**. The run still bought a per-call price: **≤ 21.7 ns**.
* **`dapin`'s GPU cost: fifth replication, one candidate eliminated, the prescribed instrument
  retired.** `dap85a` reads **+1.961 % ± 0.165 %, t = +23.74** — the tightest ever. `dgt85a`, the
  `KYTY_GPU_TIME` pair the brief asked for, reads **+0.095 % ± 0.186 %** at 6.7× the resolution
  needed: **that instrument cannot see the effect.** `rcp85a` killed the obvious candidate:
  moving the record thread (`rec_ccd_x` 34 → 0) costs **+0.098 % ± 0.186 %** of GPU — nothing.
* **AND THEN ROUTE C WAS CLOSED, in the same session, by the measurement this brief's §3.2 was
  written to commission.** A microbenchmark outside the game (`C:/kyty/tools/dsbench`) priced the
  exploit: **a sampled-image descriptor — the kind that repeats 84.9 % of the time — costs 0.95 ns
  to write**; removing **every** descriptor write in the frame saves **312 µs**; the split layout
  saves **+137 µs** while merely **deciding** which slots repeat costs **272 µs**. Then `tfs85a`
  contrasted the shipped gate **`texfast`** — the source of variation §3.4 below asks for — and
  found the repeat **already cashed**: a slot resolved through `FindTexture` costs **55.02 ns**, a
  slot served by the memo view **19.66 ns**, and the shipped fast path is worth **1 527 µs a
  frame, since session 59.** The remaining 19.66 ns is the **validity witness** a sound skip would
  have to reproduce. **Route C at per-slot granularity is a ceiling with nothing behind it**, and
  `FACTS.md` §3.4's image figure was corrected by its own session from 928 to 799 µs.
  **Everything in §3.2 below is therefore already done, and its answer is no.**

## 2. What is settled — do not reopen

* **Route A in every form** (`S` = 20.8 ms > 16.7 ms, session 83).
* **A whole-stage binding memo**, three times now, most recently at slot granularity with the
  shader-identity correction: `R_stage_sh` = **2.21 %**.
* **The `std::map` of `SynchronizeBuffersInRange`** — 0.018 ms a frame, 60 ns a call.
* **The BDA region walk as a carrier** — 4.8 ns a visit.
* **The record thread as the carrier of `dapin`'s GPU cost** — refuted by `rcp85a`.
* **`KYTY_GPU_TIME` as the instrument for that question** — it cannot see the effect.
* **`PLAN_82_bind.md` item 6b** — unsound as written.
* **Route C at PER-SLOT granularity** — priced and closed (session 85, §1). Do not re-open it with
  a partial-update scheme, a split set layout, or push descriptors: 0.95 ns a descriptor, 312 µs
  for all of them, 272 µs to decide, and the split additionally needs a **translator** change
  because both `spv::DecorationDescriptorSet` emissions are hard-coded to set 0.
* **The buffer half of route C** — a repeating `{VkBuffer, offset, range}` carries no information
  about whether the guest wrote the bytes under it, and 34.9 % of buffer slots are stream-ring
  views that cannot repeat by construction.
* Everything in `ROADMAP.md` §3.

## 3. The work — THIS IS A CODING SESSION

The rule is unchanged and not negotiable: **the session ends with a source change that was A/B'd on
this machine, or it failed.** A measurement gate's own ABBA satisfies it — sessions 83 and 85 both
ended that way — but a session that ships nothing twice running should say so in `ROADMAP` §1.

### 3.1 Split `bl_prep_us` — route C's next number, and the cheapest thing in this brief

`PrepareBindings` costs **3 991 µs a frame**, the single largest block of the bind phase, and it is
**not split by resource kind**. It contains, per stage, one `ResolveTextureWith` per image
(~48 800 a frame), one `NativeSampler` per sampler (~11 100), and the `shader_data` copy. **Until it
is split, the image-slot ceiling of §1 has an unmeasured second term that could double or triple
it.**

The instrument is three more `bindlap` counters on the same idiom — `bl_res_us` / `bl_res_n` around
the image loop, `bl_smp_us` around the sampler loop, the remainder being `shader_data`. Two
timestamps per stage more, so the instrument grows by about a quarter. **It rides in the same ABBA
as anything else you build.** Pre-register `P_res` as a ratio of sums, in ns per image slot, and
pre-register the combined image price `P_res + P_img` and the ceiling it implies.

### 3.2 DONE IN SESSION 85 — and the one idea it leaves standing

The measurement this section commissioned was taken in session 85 and **retired route C at per-slot
granularity**. `C:/kyty/tools/dsbench` is in the tree, with its build script, and `FACTS.md` §12
carries the numbers and the verdict against the rule `pred/03` §4 fixed beforehand.
**Do not re-run it and do not re-argue it.**

**What survives is one mechanism, and it is not a per-slot skip: amortise the WITNESS across the
slots of a stage.** The 19.66 ns a repeating image slot costs is the liveness re-check, the memo
eligibility test, the `bind_stamp` acquire load, `pending_levels` and `TextureSourceSettled`. When
several slots of one stage name the **same image**, that witness is evaluated once per slot and
could be evaluated once per image. `R_stage_sh` = 2.21 % does **not** rule this out, because it does
not require the whole stage to repeat.

**Measure first, as always.** One counter: the number of image slots a stage binds that share an
`image_id` with an earlier slot of the same stage — call it `sl_img_dup`. It costs one small
per-stage set or a linear scan over ≤ 8 entries, it rides in any ABBA, and it is the entire
question. If `sl_img_dup` is near zero the idea is dead and route C is closed outright; if it is
30–50 % the ceiling is `sl_img_dup × ~15 ns`, which is the part of the witness that is a load rather
than a compare.

**Do not build the amortisation before that counter reads.** Session 85's own lesson is that a
measured population turned out to be a photograph of an optimisation shipped six sessions earlier.

### 3.3 Route B, from the corrected designs and not from the plan

`FACTS` s85 §8 writes both down:

* **Item 3, the safe shape** — a desc arena addressed by index, with the memo holding a slot number
  instead of a 584-byte desc; `TextureBinding` goes 640 → 60 bytes and the copy disappears for the
  miss, `!store` and null-T# paths too. **Measure first:** one counter for how often a binding's
  memo slot is overwritten within the draw that holds it. If that counter is not ~0, the arena is
  the only safe shape and the naive reference is dead for good.
* **Item 8, the corrected batching** — one `Map`/`Commit` per draw for site 1's const-bank copies,
  with the third `m_stream_buffer` consumer (`ObtainBuffer`'s own stream path) accounted for, the
  arming counter `dp_stream_maps` (not `d_stream_maps`), and a verify that re-reads the mapped
  sub-range and `memcmp`s it against a fresh `TryReadBacking`.

Items 10 and 12 still need a counter before they need a patch. **Item 2 still has no decisive
measurement** — the number of distinct live texture-memo keys a frame — and a capacity change made
without it is a guess.

### 3.4 The debts

* **`dapin`'s GPU cost, now in its sixth session and narrower than ever.** It is real (+1.961 % ±
  0.165 %, five replications), it is visible only with the record thread live, and it is **not**
  caused by that thread's placement. What remains: the record thread's *existence* rather than its
  affinity, the submission pattern it produces, or something about how `gpu_busy_us` is harvested.
  **Do not spend another run on `KYTY_GPU_TIME`.** A `recordthread=0|1` ABBA with `dapin` pinned at
  3 would separate existence from affinity in one run.
* **`PipelineCache::m_mutex`, 5.0 ms a frame of hold, whether it can be split** — [NM] since
  session 83. It no longer revives route A, but it is 5 ms.
* ~~**The marginal per-slot price**~~ — **closed in session 85 by the route this line named**: the
  shipped gate `texfast` is exactly a knob that moves the hit rate without moving the stage count,
  and `tfs85a` used it to identify X = 55.02 ns and F = 19.66 ns. The same trick is available for
  the buffer half (`buffast`, default 0) and **has not been used**; it would split the 77.07 ns a
  buffer slot costs the way `texfast` split the image side. One run.

## 4. Do NOT

**New, from session 85:**

* **Do not build what the tree already has.** Twice in three sessions the brief has asked for a
  mechanism that was already shipped (session 83: the BDA epoch cache; session 85: the commit-side
  `cb_lap` split, which reads under `lite` whenever `drawstat=1`). **Grep for it first.**
* **Do not assume `Scope` is dead under `lite`.** Its **time** half is; its **count** half is not,
  which is the only reason `b_texn`, `bb_n` and `ob_n` exist as arming denominators.
* **Do not spend a run on a prescribed measurement without asking what the instrument changes.**
  `KYTY_GPU_TIME` turns `PacketsWanted()` false and changes what `gpu_busy_us` is derived from; six
  sessions prescribed it for a question it cannot answer.
* **Do not let a degenerate regression publish a coefficient.** Fix the VIF limit and the
  "declare it uninformative" clause **before** the run, as `pred/02` §4.3 did. R² = 0.80 with
  VIF 60.9 produces numbers that look publishable and mean nothing.
* **Do not read an identity off medians.** `bda_first_n + bda_late_n` reads +8.7 % against
  `bda_n − bda_hit` on medians and is **exact** on sums. `draws` in `rcp85a` differ +4.3 % on
  medians and −0.125 % on sums. **Every population identity is checked on sums.**
* **Do not arithmetic with a bound.** Session 83's `std::map` bound was 20× loose; session 84's
  shader-change bound was 2.6× loose. A bound is not a number.
* **Do not take a population from the plan.** `PLAN_82_bind.md` cites `bufepoch` ≈ 8 486 for item
  6a; the change fires 5 396 times, and the plan's own text calls its figure an upper bound.
* **Do not count consumers from a document.** The plan named three readers of
  `TextureBinding::desc`; there are five, and the safety argument it offers guards the wrong thing.
* **Do not call a ceiling a saving, even in microseconds.** §3.2 is why.

**Carried:** no optional stopping; pre-registrations sealed in place and never edited; arming proved
by a counter inside the run, with the **median and the tail**; `guards.py` check 10 hashes the exe
installed *now*, so compare check **lines**, not verdicts, and do not rebuild between acceptance and
the final answer; check 6 (cores) FAILs routinely and is not an admission criterion; a gate enum
entry goes immediately before `Count` **and** its `DEFINITIONS` row goes last, in the same order —
**and there is no `static_assert`, so a missing row compiles and then dereferences `nullptr` on the
first flip**; every verify line needs a cap (32–64); never put a printf's format string and its
argument list in one patch call; a counter absent from `guards.py`'s `SELF_CHECKS` is **never
parsed**, so add the row before the first run; `dt_us` is not an endpoint inside the vblank plateau.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| the sequential floor `S` | **20 838 µs**, `flr83b` | **MEASURED — closes route A** |
| route C's ceiling, as a population | 64.2 % of 109 836 slot-bindings, `slp84b` | **MEASURED** |
| …corrected for the shader-identity bias | **61.78 % of slots; `R_img` 84.93 %** | **MEASURED, session 85** |
| **route C's UNIT PRICE** | **22.82 ns image / 77.07 ns buffer** | **MEASURED, session 85** |
| **route C's ceiling, in µs** | **≈ 2 105 µs a frame**, reuse path | **MEASURED — buffer half an upper attribution** |
| …plus `PrepareBindings`, unsplit | 3 991 µs a frame | **NOT SPLIT — §3.1** |
| **the price of the EXPLOIT** | **0.95 ns an image descriptor; 312 µs for all of them; 272 µs to decide** | **MEASURED, session 85 — route C CLOSED at per-slot granularity** |
| the shipped `texfast` fast path | **1 527 µs a frame**, since session 59 | **MEASURED — the repeat was already cashed** |
| a repeating image slot, corrected | **19.66 ns**, and it is the validity witness | **MEASURED** |
| amortising the witness across a stage's slots | — | **NOT MEASURED — §3.2, one counter** |
| `bda_scan_us` | **92.7 % staging `memcpy`, 22 761 KiB at 11 GB/s** | **MEASURED, session 85** |
| route B, `bindpack2` (item 6a) | −35.9 ± 81.2 µs | **NOT PAID FOR, gate 0** |
| `dapin`'s GPU cost | +1.961 % ± 0.165 %, ×5 | **UNEXPLAINED, seventh session; one candidate eliminated** |
| shipped frame time | 31 642 µs = 31.60 FPS (`acc82a`) | not re-measured since session 82 |

**The honest statement of the task.** Session 83 closed the direction that would have made the frame
parallel. Session 84 measured how much of the frame's descriptor work repeats. Session 85 priced
both sides of that repetition and **closed route C at per-slot granularity**: the descriptor write
costs ~1 ns, deciding to skip it costs more than skipping it saves, and the part that was genuinely
recoverable was cashed by `texfast` in session 59 and is worth 1 527 µs a frame today.

**All three routes now have a measured ceiling and none of them reaches 60 FPS.** A is closed by
`S` = 20.8 ms against a 16.7 ms budget; C is closed at slot granularity; B sums to 0.7–2.5 ms and
has shipped −252 µs in four sessions. **The honest goal is the one `ROADMAP` §0 has carried since
session 83 — maximum FPS under unshakeable correctness — and session 86 should either find a route
nobody has named, or stop looking for one and spend itself on the two largest unattributed blocks
left: `PrepareBindings` at 3 991 µs and `mh_prog` at 5 850 µs.** Those are 9.8 ms of a 31.6 ms
frame and neither has ever been divided.
