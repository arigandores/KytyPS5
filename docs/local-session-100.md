# Session 100 — route E, M3: the ADDEND is measured, and the sealed rule returns CLOSE

**Single source of truth for session 100.** Mirrored into git as `docs/local-session-100.md`.
Harness root `C:/kyty/s100`. Everything below is measured unless marked otherwise.

**The three numbers route E must open with (`ROADMAP.md:1322-1324`):** the 60 FPS budget is
≤ ~3.0 µs a draw on the median frame and ≤ ~2.3 µs on a p99 frame (7 284 draws); the CPU path
stands at **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms**, unchanged — this session measured
no new baseline; **M4 and M5 are still not done**, and M3's decision is the subject below.
**60 FPS is not promised: the chance is ~15 % (8…25 %).**

---

## 1. Result

**M3's addend stopped being a hand-assembled constant and became a measured census. Under the
sealed rule of `pred/02_moved_mark.md` the confirmation `mov100b_entry1` returns CLOSE: G and R1
are closed.**

    ADDEND_hi = 2.918040375446948 ms      ADDEND_lo = 2.916948087090759 ms
    VERDICT_INPUT hi = 15.743040 … 17.192040 ms      lo = 15.741948 … 17.190948 ms
    both minima >= 15.5  =>  CLOSE        (margin 0.243 ms on the deciding minimum)

The sealed inequality, the thresholds 15.5 / 11.0, the min/max two-instrument form and the
floor values `F_a` = 14.274 / `F_c` = 12.825 (session 98, `bf98a` / `bf98c`) are **unchanged and
were not re-measured**. Only the addend changed, and only because the constant 2.2535 was
assembled from one line of a design table while dropping two of that same line's own measured
items.

**What CLOSE does and does not mean.** It closes **G** (GPU-driven/bindless V2) and **R1**
(single-threaded rewrite) by the rule the user sealed. `ROADMAP.md:46` stands unchanged:
**НЕ ДОКАЗАНО, что 60 FPS недостижим, и что переписывать нечего.** No frame-rate gain was
measured, nothing was shipped that changes the picture, and M4 and M5 are untouched and keep
their order.

---

## 2. Two seals, two instruments, two published results

Both are published; neither is re-scored into the other.

| | `pred/01_addend_census.md` | `pred/02_moved_mark.md` |
|---|---|---|
| seal | 19 152 B, `4c90060f91c21052238e0395abe2229e316012849c6bd54623d858edc5cf8c65` | 11 043 B, `b1930f69f83a77d3bba359d4d18f0653f7fea6a331232dc9edaaf46c2a82e137` |
| instrument | existing gate `bindlap` (s85/86) | new gate `blmove` (s100), moved mark |
| binary | `34206e3f…` (session-99 final) | `6f7475b8…` (session-100 build A) |
| confirmation | `cen100b`, 900 s, 90 pairs | `mov100b_entry1`, 900 s, 90 pairs |
| controls | 19/19 technical, 6/6 strict | 23/23 technical, 6/6 strict |
| T1 images | 1.664154 ms (48 013.674 slots) | 1.659044 ms (47 866.5 slots) |
| T3+T4 | 0.741842 ms | **0.664996 ms** |
| instrument cost | C = 0.436552 ms, **subtracted** | C = 0.140948 ms, **not subtracted** |
| bias bound | — | B = 0.001092 ms |
| ADDEND hi / lo | 2.999996 / 2.563444 | 2.918040 / 2.916948 |
| VERDICT_INPUT | 15.824996…17.273996 / 15.388444…16.837444 | 15.743040…17.192040 / 15.741948…17.190948 |
| **branch** | **GAP** (short by 0.111556 ms on the conservative branch) | **CLOSE** |

`cen100b`'s GAP is not an error and is not revised: `pred/01` could not tell how much of
`bindlap`'s four timestamps and five `Add`s a stage fall inside the spans it measures, so it
subtracted the whole instrument. That is why `pred/02` exists.

**The two instruments agree where they can be compared.** `T3 + T4` differs by
0.741842 − 0.664996 = **0.076846 ms** over 9 107.1 stages a flip = **8.44 ns a stage**, which is
the size of the two extra timestamps and five extra `Add`s that `bindlap` takes inside that
region and `blmove` does not. Image populations agree to **0.31 %** (48 013.7 against 47 866.5)
across different binaries and runs. Neither figure is an identity; both are consistency checks of
the expected size and are reported as such.

---

## 3. What the census is, and why the mark price cancels

`pred/02` gate **`blmove`** (`KYTY_BIND_LAP_MOVE`, default 0, MEASUREMENT ONLY) takes, inside
`RenderExecutor::PrepareBindings`, **exactly two timestamps and four `Add`s a stage in both
phases**. Phase 0 closes right after the image loop; phase 1 closes right after the
`shader_data` copy. The phase alternates per stage **type** (`blm_turn[stage % 16]++ & 1`, the
`previous_key` idiom already in the file), so each type contributes equally to both spans.

    T34 = (s1 - s0) * stages_per_flip        s0, s1 = ns a stage, per block
    T1  = (blm_img0 + blm_img1) a flip * 34.66 ns   (sealed s88 unit cost, population measured)

The price of the opening mark, the closing mark and the four `Add`s cancels term by term in
`s1 − s0`. Nothing is estimated and nothing is subtracted. The measured phase balance on
`mov100b_entry1` is **5.250549 against 5.250713 image slots a stage (0.0031 %)** and
**1.221278 against 1.221185 sampler slots a stage (0.0076 %)**, and the residual bias bound is
**B = 0.001092 ms** — three orders of magnitude below the 0.243 ms margin.

`blmove`'s own ABBA cost is reported and never used: **C = 0.140948 ms a flip**, or
**+0.387 % ± 0.112 % cpu/draw, t = +6.91** by `summary4.py`. `bindlap`'s was 0.436552 ms.

### 3.1 The five terms and the two the sealed constant dropped

| term | (i) the floor removes it | (ii) V2 keeps it (`s94/rewrite94/gpu-driven.md`, written before M3 had a number) | value |
|---|---|---|---|
| T1 images | `BindFloorPrepareStage` replaces the image loop; `bf_img` = "stub image-view descriptors written" | §4 `mh_bind` basis: "V2 adds 47 885 × (19.66 + 15.00 ns) = 1.66 ms [M units s88]" | **1.659044** |
| T2 writable slots | same | §4 basis "written slots 490.5 [M s94]" | 0.4905 sealed |
| T3 samplers | same; `bf_smp` = "stub sampler descriptors written" | §4 basis "**+ samplers 345 [M s86]**" — **dropped from the sealed constant** | measured inside T34 |
| T4 shader data | `BindFloorPrepareStage` **zeroes** `shader_data` instead of copying it (descriptors.cpp:669) | §3 "**push user SGPRs** plus texture heap indices as push data" — **never in the constant** | measured inside T34 |
| T5 synchronisation | — | user decision, session 98 (`bd96b`, +103.5 µs) | 0.1035 sealed |

**Named and excluded, with the half each fails** (fixed in the seal before any data):

* the permutation `find_if` and its `candidate.specialization == specialization` compare
  (`pg_pms_us` = 298.72 µs, `pgl90a`, s90) — **fails (i)**: `pipelineCache.cpp` guards only the
  materialisation reuse with `bind_floor`; the `find_if` block runs in every mode, so that time
  is already inside `F_a`/`F_c`. Adding it would be double counting.
* `AheadTake` 2 557, `pg_mat` 666.9, `pg_pm` 461.9, memo 72, stamps 196 — **fail (ii)**: §4's
  `mh_prog` row lists all of them under *Disappears*.
* `pg_pre` 1 541 and key+find 255 — **fail (i)**: the floor keeps the pipeline lookup.
* readable buffer slots (59.3 ns each, `Ceiling_bind_ro` 1 001.3 µs) — **fail (ii)**: §3 has the
  shader fetch V#s through BDA.
* `CommitBindings` 2 035 µs — **fails (ii)** as a `mh_bind` survivor; §4 puts its survivor at
  0.1–0.3 ms inside the `mh_emit` row, which the floor keeps.

**The anticipated arithmetic was declared inside both seals before the runs** (`pred/01` §3.1,
`pred/02` §3.1), including that stale values would give CLOSE and that the branch flips to GAP
if the re-measured sum falls 12.9 %, or if the correction exceeds 0.325 ms. `pred/01`'s
correction did exceed it and `pred/01` returned GAP.

---

## 4. Runs, in order. Nothing is re-scored, nothing is retried into admission.

| tag | hold | binary | outcome |
|---|---|---|---|
| `cen100a` | 300.1 s | `34206e3f…` | ADMITTED_PILOT, 22 pairs, all controls clean, branch preview GAP |
| `cen100b` | 900.3 s | `34206e3f…` | **ADMITTED_ADDEND_CENSUS**, 90 pairs, 19/19 + 6/6, **GAP** |
| `mov100a` | 300.1 s | `6f7475b8…` | ADMITTED_PILOT, 22 pairs, all controls clean, branch preview CLOSE |
| `mov100b` | — | `6f7475b8…` | **ENTRY FAILURE, NOT_MEASUREMENT**: `GpuHangAbort: role=4 requested=2976 known=2975 current=3071`, never reached the scene, `nvlddmkm` 153 at 02:06:10 |
| `mov100b_entry1` | 900.3 s | `6f7475b8…` | **ADMITTED_MOVED_MARK**, 90 pairs, 23/23 + 6/6, **CLOSE** |

`mov100b` is the historical **entry** hang (6.67 % of entries, the uncapped BVH traversal
`cs=0x380bb9d636390bae` named in session 98), not a floor hang and not a defect of this
instrument. It is recorded as an entry failure and the retry used the distinct tag
`mov100b_entry1` under the same fixed protocol and budget, with no cache-policy change — the
first of the at most two isolated attempts `pred/02` §4 allows. **Five entries this session, one
hang.** The floor was not used in any session-100 run.

**Admission evidence for `mov100b_entry1`:** work **+0.041242 %**, area split **+0.005223 %**,
area match **100 % (90/90 pairs)**, C5 **0.000412**, C9 **0.001323**, orientations **[45, 45]**,
2 610 rows an arm, 187 GateArm blocks, criterion 3 **VALID**, and an independent recount written
after the scorer and sharing no code with it **agrees on every published figure**
(`mov100b_entry1_parent_recount.json`).

**Reported, never deciding** (they are reported because they failed and must stay visible):
`guards.py` returns **7 PASS, 2 FAIL, 1 WARN, 2 SKIP** on `mov100b_entry1` — check 3 resolution
("the render target or the viewport moved during the run", 3 fragment flips skipped) and check 6
cores ("26 of 92 groups more than 10 % off their arm median — something else used the machine").
The same two failed on `cen100a` and `cen100b`. Check 6 also failed with nothing of this session
running on the machine, so it is noisy here; it is not a criterion of either sealed rule, and the
arm-symmetry controls that are (area, work, C5, C9) are clean.

---

## 5. The session-98 L3 debt is paid, and the bound tightens 22×

`ROADMAP.md:1406` owed "a counter of the short clear paths actually taken in the base arm". Two
always-on counters were added behind no gate: **`clr_taken_meta`** and **`clr_taken_img`**, at the
two sites where `TryConsumeComputeMetaClear` / `TryConsumeComputeImageClear` consume a dispatch
(`renderCompute.cpp:406`, `:410`).

    mov100b_entry1, both arms, settled window (they are not gated, so the arms agree):
      clr_taken_meta  2.0005 / 1.9994 a flip
      clr_taken_img   6.9992 / 6.9975 a flip
      total           9.000  / 8.997  a flip   of 268.02 / 267.98 dispatches = 3.358 % / 3.357 %

Session 98's `bf_clr_skip` is a **shape** census and read **198.01 a flip = 73.8 %** of
dispatches. The real population is **9.00 a flip = 3.36 %**, a factor of **22.0** smaller.
Applying the sealed `bf98.py` form `|dF_L3| ≤ count × 7.967 µs` with the real count:

    |dF_L3| <= 9.00 * 7.967 / 1000 = 0.0717 ms   (was 1.578 ms)
    F_a +- L3 = [14.202, 14.346]    F_c +- L3 = [12.753, 12.897]

Neither interval straddles 13.2465 ms any more; session 98's printed straddle
`[12.697, 15.852]` is superseded **as a bound**, not as a published number. **Caveat carried:**
this is measured in an **unfloored** run on a different binary; under the floor the frozen
snapshot changes which shortcuts fire, and `bf_clr_skip` is structurally unreachable at
`bfmode=2`. It is the counter session 98 asked for, not a re-measurement of session 98's runs.

---

## 6. `PrefetchComputePipelines`, measured on the current binary and not attacked

Session 96 measured `pl_pref_ns` = 1 961.1 µs a flip over 8 calls (42.44 % of the time outside
the render mutex, 6.2 % of the 31.6 ms frame) and nobody has touched it since. This session
measured its decomposition from its own logs, with **no new code and no extra run**
(`mov100b_entry1`, settled window, both arms):

    da_walk_us   1 836.9 / 1 837.5 us a flip over 5.00 walks
    da_queue_us    769.1 /   769.4 us a flip  =  41.9 % of the walk, inside QueueDrawAhead
                                                 under PipelineCache::m_mutex
    da_q         7 986   /  7 987   requests a flip  =>  125 mutex acquisitions a flip
                                                 at the shipped 64-request batch
    da_take_us   2 345.2 / 2 348.6 us a flip (the AheadTake pickup, a separate debt)
    da_hit/miss  8 652 / 74

So **41.9 % of the walk is mutex-held queueing**, and the shipped batch of 64 costs **125
acquisitions a flip**. A knob on that batch is a three-line change with a ready A/B
(`da_hit`/`da_miss`/`da_late` are its own controls). **It was NOT built and NOT measured**: the
session kept its build to the two additions above so that the deciding measurement did not ride
on a hot-path change. The lever is named, costed and left for session 101.

---

## 7. Source changes, and how ROADMAP §6 is satisfied

One build, **`6f7475b8a6b9636aa31938d97f26c1bd4b7dbfd97213dd01b99b8cd3109268c0`**, from
`patch_s100a.py` (8 anchors, all unique, dry-run first). `check_gate_order.py` ran after the
patch and before the build: **Gate 110 enum entries / 110 table rows, Knob 23 / 23, GATE ORDER:
clean**. Build exit 0, 0 errors.

* **gate `blmove`** (`KYTY_BIND_LAP_MOVE`, default 0) — `gates.h` LAST row, `gates.cpp` LAST row.
* **eight counters** `blm_s0_ns blm_s0_n blm_s1_ns blm_s1_n blm_img0 blm_img1 blm_smp0 blm_smp1`
  (raw ns / raw counts, printed including zeros).
* **two counters** `clr_taken_meta` / `clr_taken_img`, always on, behind no gate — they
  deliberately break the "every bf_* reads 0 at bindfloor=0" invariant of `frameStats.h:1597`,
  following the precedent of `bf_igc_*`.

**No default moved, no shipped path changed, no knob default moved.** At every default the
binary behaves as `34206e3f…` did.

**ROADMAP §6** ("сессия заканчивается изменением исходников, прошедшим A/B, либо она провалена")
is satisfied through `ROADMAP.md:1317-1318` ("счётчик — это правка, и его ABBA — это A/B"): the
`blmove` gate ran a full ABBA in `mov100a` and `mov100b_entry1`, its cost is significant and
measured (+0.387 % ± 0.112 % cpu/draw, t = +6.91), and its arms are symmetric on every strict
control. **The video-pass debt of §6 does not arise**: neither addition can reach the renderer —
`blmove` only reads a clock and increments counters and binds nothing, and `clr_taken_*` are
pure counters at sites that already returned. That is an argument from the diff, not a measurement.

---

## 8. Harness

`C:/kyty/s100`, ported from `C:/kyty/s99` by a freshly written `C:/kyty/s99/s100_port.py`
(never run a carried `*_port.py`). `PRECONDITIONS PASS: 5 root constructs; 15 sealed texts;
18 live paths + 4 expression paths; gates 1092 B / 99 names` →
`PORT DIAGNOSTIC: clean; carried=1792 ledger=41 skipped=59`.

New port work the old one did not cover: **repair 7**, for the four session-99 scorers whose
`PRED` is `ROOT / '…'` or `Path('…')` and therefore escapes the port's `const()` regex
(`bf99.py`, `settled99.py`, `settled99_gc.py`, `settled99_norec.py`). Repair 7 inserts `prev99/`
into the relative part only, so the line shape and the neighbouring `*_SHA` are untouched and the
four seals resolve into `s100/prev99/pred/`. Also new: an explicit `R1_ARCHIVE` entry for
`verify_port99/verify.py`, which carries a literal copy of the comma chain and legitimately fires
repair 1; the port failed loudly on it rather than silencing it.

Sealed texts grew **10 → 15** into `s100/prev99/pred/`, byte-exact. `s100/pred/` was created
empty and now holds the two session-100 seals. `accept99.sh` arrives in `s100` still carrying
`R=C:/kyty/s99` — **do not run it**; the port prints that and `accept100.sh` was written by hand.
Three frozen copies under `verify_gc99_scorer/frozen/` keep a dangling `PRED` by design and the
port says so.

**Scorers and their proof of fitness, all offline, all before the first run:**
`cen100.py` (sealed to `pred/01`) with `test_cen100.py` — **30 checks, all pass**, including one
mutation per control that must fail that control; `mov100.py` (sealed to `pred/02`, reusing
`cen100`'s reader, selector, population and estimator unchanged) with `test_mov100.py` —
**28 checks, all pass**. `cen100.py` was dry-run on session-99's `log_eng99a4.txt` and
**reproduced session 99's own published metrics exactly** (work −0.02365018145291 %, 22 pairs,
orientations [11, 11]) — a cross-check of the selector and estimators against the sealed
session-99 scorer. Two later edits added optional `x_fields` / `main_fields` parameters to
`cen100.read_log`; `cen100b`'s score was re-derived after each and is **byte-identical**.

Independent recounts (`parent_recount100.py`, `parent_recount100_mov.py`) share no code with the
scorers and agree to `abs_tol 1e-10` on `cen100a`, `cen100b` and `mov100b_entry1`.

---

## 9. Proved, and not proved

**Proved this session.** The sealed M3 addend is incomplete against its own source: two measured
items of the very table that produced 1.66 and 0.49 were dropped. A census on the current binary
in the same scene (Sky Garden, `-lvl underwater_aerial_garden` — the scene of `drm86a`, `bf98a`,
`bf98c` and `bf99g`) puts the addend at **2.918 ms**, and the sealed rule then returns
**CLOSE**. The moved-mark instrument's price cancels by construction and its residual phase bias
is bounded at **0.001092 ms**. The session-98 L3 bound tightens from 1.578 ms to **0.0717 ms**.
`PrefetchComputePipelines`' walk is **41.9 % mutex-held queueing** at **125 acquisitions a flip**.

**Not proved.** That 60 FPS is unreachable — `ROADMAP.md:46` stands. That `F_a`/`F_c` are right:
they are carried from session 98 on binary `9aa93e73…` and were not re-measured; the rule has
always combined terms from different sessions and this one does too. That the mode-2 residual
pessimism of session 99 is bounded — it is not, and `B_a`/`B_c` enter nothing here. That the DRS
clock debt (`ROADMAP.md:1094`, `:1402`) is discharged — it is not; `KYTY_GPU_CLOCK_PIN=1` was set
as `ROADMAP.md:1307` requires and the arms stayed matched (C9 0.13 %), which is not the same
thing. That the cross-queue ACB tear or the entry-hang BVH traversal are fixed — neither is, and
the second one cost this session a 900-second run. That any gate other than `bindfloor` is safe
against being read twice inside one operation — still unaudited. **No frame-rate gain, no
speedup, no 60 FPS.**

---

## 10. Provenance

* Binaries: session-99 final `34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f`
  (`cen100a`, `cen100b`); session-100 build A
  `6f7475b8a6b9636aa31938d97f26c1bd4b7dbfd97213dd01b99b8cd3109268c0` (`mov100a`, `mov100b`,
  `mov100b_entry1`), installed now. **No rebuild happened between the last measurement and this
  report.**
* `gates_base.txt` unchanged: 1 092 B / 99 names /
  `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `blmove` is the **34th**
  name absent from it and lives only in schedule arms; `ABSENT` grows 33 → 34 for the next port.
* Seals: `pred/01_addend_census.md` 19 152 B `4c90060f…`, `pred/02_moved_mark.md` 11 043 B
  `b1930f69…`. **Not editable.**
* Every raw log, stdout, `<tag>.json`, score and recount is hashed in
  `runs100/manifest100.json`.
* Git HEAD at the start: `013b81aee6c668f96836abfa2375b435437fe3f9`, branch `merge-upstream`,
  only `3rdparty/nlohmann_json` dirty and deliberately excluded.
