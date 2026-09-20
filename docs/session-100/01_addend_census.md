# Sealed pre-registration 01 — session 100, route E, M3: the ADDEND census

**Immutable once written.** A correction goes into a new sealed addendum, never into this file.
Written before any session-100 measurement exists. Author: session-100 executor, under the user's
standing delegation of 2026-09-20 ("делай как будет лучше, не жди ответов от меня").

---

## 0. What this rule is, and what it is not

The sealed M3 rule is `ROADMAP.md:1081-1082`:

> **Правило: пол + 1,66 мс (образы) + 0,49 мс (записываемые слоты) + 0,5 мс (синхронизация) ≥ 15,5 мс
> ⇒ G и R1 закрыты; ≤ 11 мс ⇒ G идёт дальше.**

amended by the user's session-98 decision (`ROADMAP.md:1137-1138`, `:1325-1326`) to replace the 0.5 ms
synchronisation term with the submission-granularity +103.5 µs of `bd96b`, giving the constant
**2.2535**. Session 98 measured `F_a` = 14.274 ms (`bf98a`) and `F_c` = 12.825 ms (`bf98c`) and the
two-instrument form of `ROADMAP.md:1126-1127` returned **GAP**, short of CLOSE by 0.422 ms on the
minimum.

Session 99's `bfmode=2` arm is a **different screen** with addend 0 and it is finished
(`pred/02_settled_bindings.md` §6; `combined99_score.json`: DIAGNOSTIC_ONLY / HIGH). Nothing here
re-opens, re-scores or re-calibrates it. `B_a`/`B_c` are not inputs to this rule.

`docs/next-session-100.md` §1 offers three branches for the wide M3 rule. **This rule takes branch 2,
"an operation-level accounting that restores the missing real work", with branch 3 (an honest global
GAP) as its own default outcome.** Branch 1 (a finite bound **P** on the mode-2 instrument's residual
pessimism) is NOT taken: no such bound is proved here and none is asserted.

**This rule changes exactly one thing in the sealed M3 rule: the addend.** The inequality, the
thresholds 15.5 and 11.0, the min/max two-instrument form, and the values `F_a`/`F_c` are unchanged and
are NOT re-measured. The addend stops being a constant assembled by hand from a design table and
becomes a census measured on the current binary in the same scene.

The change of the rule is recorded in `ROADMAP.md` in the same session, with this file named, as
`docs/next-session-100.md` §1 requires ("A change to that rule, to its branches or to its constant goes
into `ROADMAP.md` first").

---

## 1. Why the addend is suspect, established from texts only

The addend 1.66 + 0.49 was assembled from one line of `C:/kyty/s94/rewrite94/gpu-driven.md` §4, the
design document written in session 94 **before** M3 was measured. That line reads, verbatim:

> | `mh_bind` | 11 174 | V1 93–97 %; V2 71–82 % | V1 0.4–0.8; **V2 2.0–3.3** | written slots 490.5 [M s94];
> V2 adds 47 885 × (19.66 + 15.00 ns) = 1.66 ms [M units s88] **+ samplers 345 [M s86]** |

The sealed rule took two of that basis's three items and dropped the third. The dropped item is not an
estimate: `bl_smp_us` = **345.1 µs a frame over 11 125 sampler slots at 31.02 ns a slot** was measured
in run `drm86a` (`docs/local-session-86.md:197`), in the **same scene** (`-lvl underwater_aerial_garden`)
as `bf98a`, `bf98c` and `bf99g`, and from the **same table** whose 47 885 image slots produced the 1.66.

The floor removes the sampler work: `BindFloorPrepareStage` (descriptors.cpp:669) replaces the whole of
`PrepareBindings`, and `bf_smp` is documented at frameStats.h:1606 as "stub sampler descriptors written".
So the sampler term satisfies both halves of the test below, and its absence from the constant is an
assembly gap, not a distinction.

The same §3 of `gpu-driven.md` describes V2's per-draw CPU work as: *"parse registers, look up the
pipeline from register state only, **push user SGPRs plus texture heap indices as push data**, bind the
index buffer, record the draw."* The user-SGPR copy is `prepared.shader_data`, measured by
`bl_sd_us`, and `BindFloorPrepareStage` **zeroes** `shader_data` instead of copying it
(descriptors.cpp:669). It too satisfies both halves and is absent from the constant.

---

## 2. The term test, fixed here

A term enters **ADDEND** if and only if **both** hold:

* **(i) the full floor removes it** — established from the source tree, not from data; and
* **(ii) `C:/kyty/s94/rewrite94/gpu-driven.md` §3–§4 describes V2 as still performing it on the CPU** —
  established from a document written in session 94, before M3 had a number.

No term may be added that fails either half, and no term named by (ii) that passes (i) may be dropped.
The set is closed here.

| term | (i) removed by the floor | (ii) kept by V2 | value in this session |
|---|---|---|---|
| **T1 images** | `BindFloorPrepareStage` replaces the image loop of `PrepareBindings`; `bf_img` = "stub image-view descriptors written" | §4 basis: "V2 adds 47 885 × (19.66 + 15.00 ns) = 1.66 ms [M units s88]" | `mean(bl_res_n) × 34.66 ns`, **population re-measured, unit cost sealed from s88** |
| **T2 writable slots** | same replacement | §4 basis "written slots 490.5 [M s94]"; §3 "Only for those draws does the CPU walk the SRT path" | **0.4905 ms, sealed s94 value, NOT re-measured** |
| **T3 samplers** | same replacement; `bf_smp` = "stub sampler descriptors written" | §4 basis "+ samplers 345 [M s86]" | `mean(bl_smp_us)/1000`, **re-measured** |
| **T4 shader data** | `BindFloorPrepareStage` zeroes `shader_data` instead of copying it (descriptors.cpp:669) | §3 "push user SGPRs … as push data" | `mean(bl_sd_us)/1000`, **re-measured** |
| **T5 synchronisation** | not a binding term | user decision, session 98 | **0.1035 ms, sealed, NOT re-measured** |

**Terms named and EXCLUDED, with the half they fail** (written here so the set cannot grow after data):

* the permutation `find_if` and its `candidate.specialization == specialization` compare
  (`pg_pms_us` = 298.72 µs, `pgl90a`, s90) — **fails (i)**: `pipelineCache.cpp` guards only the
  materialisation reuse with `bind_floor`; the `find_if` block runs in every mode, so this time is
  already inside `F_a`/`F_c`. Adding it would be double counting.
* `AheadTake` (2 557 µs), `pg_mat` (666.9 µs), `pg_pm` (461.9 µs), memo (72 µs), stamps (196 µs) —
  **fail (ii)**: §4's `mh_prog` row lists all of them in its *Disappears* column.
* `pg_pre` (1 541 µs), key+find (255 µs) — **fail (i)**: the floor keeps the pipeline lookup
  (`ROADMAP.md:1079` "оставить … пайплайн"), so they are inside `F`.
* readable buffer slots (59.3 ns each, `Ceiling_bind_ro` 1 001.3 µs) — **fail (ii)**: §3 has the shader
  fetch V#s through BDA at run time.
* `CommitBindings` (2 035 µs) — **fails (ii)** as a survivor of `mh_bind`: §4 puts its survivor at
  0.1–0.3 ms inside the `mh_emit` row, which the floor keeps.
* anything not named in `gpu-driven.md` §3–§4.

---

## 3. The rule

For i in {a, c}:

    VERDICT_INPUT_i(X) = F_i + X,   F_a = 14.274 ms, F_c = 12.825 ms   (session 98, unchanged)

    ADDEND_hi = T1 + T2 + T3 + T4 + T5
    ADDEND_lo = T1 + T2 + max(0, T3 + T4 - C) + T5

where **C** is the measured ABBA cost of the `bindlap` instrument itself in ms a flip (§5). `C` is a
deliberately **over**-conservative correction: it is the whole instrument's cost, while only T3 and T4
carry in-span instrument overhead (T1 is a count times a sealed unit cost and carries none).

**Branches:**

* **CLOSE** — G and R1 closed — if and only if
  `min(VERDICT_INPUT_a(ADDEND_hi), VERDICT_INPUT_c(ADDEND_hi)) ≥ 15.5`
  **and** `min(VERDICT_INPUT_a(ADDEND_lo), VERDICT_INPUT_c(ADDEND_lo)) ≥ 15.5`.
  A CLOSE that the instrument's own cost can overturn is not a CLOSE.
* **PROCEED** — if `max(VERDICT_INPUT_i(ADDEND_hi)) ≤ 11.0`. **Unreachable**: it needs
  ADDEND ≤ −3.274 ms. It is written so the rule is complete, not because it can fire.
* **GAP** — in every other case, including the case where the two ADDEND branches disagree. Global M3
  stays open, G and R1 stay alive and unlicensed, the order M3 → M4 → M5 is untouched, and the session
  reports the gap in ms.

**No other outcome exists. HIGH/LOW of session 99 are a different instrument and do not appear here.**

### 3.1 What the arithmetic would be on stale values, declared before the run

With the session-86/94/98 values (47 885 image slots, `bl_smp_us` 345.1, `bl_sd_us` 385.0, 490.5,
0.1035): ADDEND_hi = 1.6597 + 0.4905 + 0.3451 + 0.3850 + 0.1035 = **2.9838 ms**, VERDICT_INPUT
**15.809 … 17.258 ⇒ CLOSE**. Without T4 it is 2.5988 ⇒ 15.424 … 16.873 ⇒ **GAP** by 0.076 ms. With the
sealed constant 2.2535 it is 15.078 … 16.527 ⇒ **GAP** by 0.422 ms.

**All three numbers were visible to the author before this file was sealed, and are written here so
that the seal is not read as a blind test.** What the run decides is whether the **current**
populations, on the **current** binary, in the same scene, still support them, and whether the
instrument's own cost leaves the branch standing:

* CLOSE needs ADDEND ≥ 2.675 ms, i.e. **T1 + T3 + T4 ≥ 2.0810 ms**.
* The stale sum is 2.3898 ms. The margin is **0.3088 ms = 12.9 %**: a fall of more than 12.9 % in the
  re-measured sum, or an instrument cost C above 0.3088 ms, flips the verdict to GAP.

---

## 4. Population and selector — adopted unchanged, not tuned

Identical to `pred/02_settled_bindings.md` §2, taken over verbatim so that nothing is chosen on new data:

* schedule `KYTY_GATE_SCHEDULE="90+1800:<base>|<armed>"`, `KYTY_GATE_SCHEDULE_ABBA=1`;
* a block is the 90 frames `GateArm.frame+1 … +90`; **keep exactly `scheduled[60:89]` = 29 rows**,
  indices 60..88, of every eligible block;
* a block whose lowest kept frame is below **2100** is rejected;
* pair original blocks (2k, 2k+1) and retain only **complete ABBA quartets 4k..4k+3**; an incomplete
  quartet is dropped whole. No re-pairing, no block reuse, no posthoc window.
* A measurement needs **≥ 30 complete pairs** and **≥ 30 arm changes**; a pilot needs ≥ 10 and ≥ 8.

**T\* does not trim the endpoint population** (as in `pred/02`); there is no floor and no latch in this
run, so the latch-leakage structure does not apply and is not invoked.

All per-flip means are **arithmetic means over the retained rows of the arm**, and every block-level
figure is the **median over blocks of the block mean**, the estimator of `pred/02` §3. Both are named
here so that no estimator is chosen later.

---

## 5. Instrument, protocol and arms

**Instrument: the existing gate `bindlap`** (`KYTY_BIND_LAP`, gates.cpp:212, default 0, MEASUREMENT
ONLY, session 85/86). No new gate, knob or environment variable is required for this rule. `bindlap` is
one of the 33 names absent from `gates_base.txt`, so it is driven from the schedule arms and nothing
else in the pinned baseline moves.

    base arm  : bindlap=0
    armed arm : bindlap=1

Fixed environment, positional to `enter_scene.py` (exported `KYTY_*` are dropped by the launcher):

    KYTY_GATE_SCHEDULE="90+1800:bindlap=0|bindlap=1"  KYTY_GATE_SCHEDULE_ABBA=1
    KYTY_GPU_CLOCK_PIN=1  KYTY_GPU_MARKERS=0  KYTY_GPU_CHECKPOINTS=0
    KYTY_BIND_FLOOR_LATCH=0  KYTY_BIND_FLOOR_CLEAR=0
    KYTY_REC absent entirely (pred/05 §2 carried: empty or 0 is not a valid way to disable it)

`--gates-file C:/kyty/s100/gates_base.txt` (1 092 B, 99 names, sha `00c116dc…0594d8`), `--attempts 1`,
`--no-install` once the binary is installed, `--pred` pointing at this file.

**No burn and no DRS calibration.** The floor halved the frame and moved the DRS step; `bindlap` adds
of order 0.1 % of a 31.6 ms frame, so no `bfburn` is used and no calibration chain is run. The DRS step
is verified to have stayed matched by the C9 and area controls below, exactly as in session 99, and the
session-91 pin is set as `ROADMAP.md:1307` requires. **This is not a claim that the DRS clock debt
(`ROADMAP.md:1094`, `:1402`) is discharged** — it is not, and it is restated as open in the report.

**Sequence:** pilot `cen100a` `--hold 300`; then, only if the pilot is admitted, a **fresh**
confirmation `cen100b` `--hold 900`. The verdict is taken from the confirmation alone. A pilot is not a
retry and a run is never re-scored into admission. If the entry hangs it is an ENTRY failure, recorded
separately under the tags `cen100a_entry1` / `cen100a_entry2`, at most two further isolated attempts,
same protocol and budget, no cache-policy change to obtain success (`pred/02` §5, carried).

---

## 6. Controls. Every limit is carried unchanged; not one is widened.

**Strict (a failure stops admission):**

| name | limit |
|---|---|
| `AREA_SPLIT` | \|area_split_pct\| < 1 % |
| `AREA_MATCH` | ≥ 90 % of pairs inside the 0.5 % per-pair area band |
| `WORK` | \|work_pct\| < 0.5 % |
| `C5` | \|draws_a/draws_u − 1\| ≤ 0.02 |
| `C9` | \|dt_a − dt_u\|/dt_u ≤ 0.03 |
| `RETAINED_DATA` | the selector returned data on both arms |
| `COMPLETE_PAIRS` | ≥ 30 (measurement) / ≥ 10 (pilot) |
| `AB_BA_BALANCED` | equal, non-zero counts of AB-first and BA-first pairs |

**Technical (a failure stops admission):**

| name | what it asserts |
|---|---|
| `SCHEMA` | every retained row carries all of `bl_stage_n bl_prep_us bl_prep_n bl_res_us bl_res_n bl_smp_us bl_smp_n bl_sd_us bf_n bf_disp cpu_gpu_us spin_gpu_us dt_us draws rt_kpx rt_att`; an absent field is a FAIL, never a zero |
| `RAW_CONTIGUITY` | main `FrameTrace` n strictly consecutive over the whole raw log; `dt_us` non-negative |
| `GATEARM` | blocks contiguous from 0, `(arms,period,abba) == (2,90,1)`, `arm == (0,1,1,0)[block%4]`, `frame == 1800 + 90*block` |
| `NO_FLOOR` | `bf_n == bf_disp == bf_skip == bf_clr_skip == bf_skip_drop == 0` on **every** row of the raw log |
| `MARKERS_OFF` | `gm_ops == 0` everywhere |
| `PIN_ON` | exactly one `GpuClockPin: mode 1` line and no other mode |
| `BINDLAP_DARK` | for each of `bl_stage_n bl_prep_us bl_prep_n bl_res_us bl_res_n bl_smp_us bl_smp_n bl_sd_us`, the **unarmed** sum ≤ 0.001 × the armed sum |
| `BINDLAP_ARMED_POSITIVE` | every one of those eight is > 0 on the armed arm, and > 0 on **every** retained armed block |
| `PARTS_LE_WHOLE` | on every retained armed row, `bl_res_us + bl_smp_us + bl_sd_us ≤ bl_prep_us` |
| `RES_N_IDENTITY` | \|mean(`bl_res_n`)/mean(`bl_img_n`) − 1\| ≤ 0.001 (the session-86 identity, +0.0001 % there) |
| `STAGE_POP` | `bl_prep_n > 0` and \|mean(`bl_res_n`)/mean(`bl_prep_n`) − 1\| is **reported**, not limited |
| `CRASHES` | no `GpuWaitSlow:`, `GpuHangAbort:`, `ErrorDeviceLost`, `Unhandled exception:`, `--- Error ---`, `--- Fatal Error ---`, `--- std::terminate ---`, `--- abort() ---`, `AsyncPipelines: skipped draw` in log or stdout |
| `SURVIVAL` | the counted attempt has `hold_exit is None` and `hold_s ≥ hold − 5` |
| `NO_RECORDING` | `KYTY_REC` absent from the env block and no `Recording:` line in log or stdout |
| `IDENTITY` | the exe installed at scoring time hashes to the run's `binary_sha256` |
| `DURATION` | `sum(dt_us)/1e6 ≥ hold_s` |

**Reported, never deciding:** `guards.py <tag> --first-frame 2100`, `area_series.py` + `area_verdict.py`
(criterion 3), `summary4.py --blocks`, `endpoint84.py`, the whole-window (unfixed-population) work, and
`bl_img_us`/`bl_buf_us`/`bl_tr_us`/`bl_wr_us`/`bl_em_us`/`bl_cmt_n`.

An admitted run publishes its numbers even when a reported check fails, and the failing reported lines
stay visible in the write-up forever.

---

## 7. The instrument cost C

`C` = the ABBA difference of the endpoint of `ROADMAP.md:1243-1247`, in ms a flip:

    C = median over armed blocks of mean(cpu_gpu_us - spin_gpu_us)
      - median over base  blocks of mean(cpu_gpu_us - spin_gpu_us)
      all divided by 1000

taken from the raw log, not from `summary4.py` (whose `cpu_net_us` under lite **is** `cpu_gpu_us`) and
not from `endpoint84.py` (reported only). `spin_gpu_us` is read from the `FrameTrace-draw` line, never
from the main line (session-83 trap, `ROADMAP.md:1248-1249`).

If `C ≤ 0` it is clamped to 0 for `ADDEND_lo` and the raw value is printed beside. `C` is **never**
deducted from T1 and is **never** used to correct `F_a`/`F_c`.

---

## 8. Independent recount

The endpoint, the four measured quantities, `C`, `work_pct`, `area_split_pct`, `dt_relative` and the
pair count are re-derived by a **separate script written after the scorer**, in the shape of
`parent_recount99.py`: it re-reads `log_<tag>.txt` directly, rebuilds the 90-frame blocks from 1801,
applies idx 60..88 over complete quartets, and asserts every figure against the scorer's JSON with
`math.isclose(abs_tol=1e-10)`. A mismatch stops publication.

The scorer is dry-run against existing session-96…99 logs and against synthetic fixtures **before** the
first session-100 run, and a fixture that should fail each control is shown to fail it (session-97 trap:
a sealed control can be unsatisfiable for the instrument it scores).

---

## 9. What no outcome of this rule may be used to claim

* That `F_a`/`F_c` were re-measured. They were not; they are carried from session 98 on binary
  `9aa93e73…`, and the ADDEND is measured on a different binary. The rule has always combined terms
  from different sessions (1.66 from s88, 0.49 from s94, 0.1035 from s96/98) and this is stated, not
  hidden.
* That a CLOSE proves 60 FPS unreachable. CLOSE closes **G and R1** by the sealed rule. `ROADMAP.md:46`
  stands: "**НЕ ДОКАЗАНО:** что 60 FPS недостижим, и что переписывать нечего."
* That M4 or M5 may be skipped, re-ordered or advanced. The order M3 → M4 → M5 is the user's decision of
  session 97 and is not the agent's to revisit.
* That session 99's `B_a`/`B_c`, its HIGH, or its zero addend enter this arithmetic. They do not.
* That the DRS clock debt is discharged, that the mode-2 residual pessimism is bounded, that the
  cross-queue ACB tear is fixed, or that the entry-hang BVH traversal is capped.
* That `bl_res_us`, `bl_smp_us` or `bl_sd_us` are free of their own instrument overhead. They are not;
  that is exactly what `C` and the two-branch rule exist to bound.
* Any frame-rate gain, any speedup, and 60 FPS. **Не обещать 60 FPS: шанс ~15 % (8…25 %).**

---

## 10. Provenance at sealing time

* Harness root `C:/kyty/s100`, ported from `C:/kyty/s99` by `C:/kyty/s99/s100_port.py`
  (PRECONDITIONS PASS: 5 root constructs; 15 sealed texts; 18 live paths + 4 expression paths;
  gates 1092 B / 99 names — PORT DIAGNOSTIC: clean; carried=1792 ledger=41 skipped=59).
* Installed binary at sealing time:
  `34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f`, 23 743 488 B — the session-99
  final build. If a session-100 build replaces it before the run, the run records the new hash and this
  file's arithmetic is unchanged; the binary is **not** re-pinned inside this text.
* `gates_base.txt` 1 092 B / 99 names / `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`.
* Git HEAD `013b81aee6c668f96836abfa2375b435437fe3f9`, branch `merge-upstream`, no push.
* Scene `-lvl underwater_aerial_garden` (Sky Garden) — the scene of `drm86a`, `bf98a`, `bf98c`, `bf99g`.
