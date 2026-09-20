# Session 100 — route E, M3: the ADDEND is measured, the gap narrows, and M3 stays GAP

**Single source of truth for session 100.** Mirrored into git as `docs/local-session-100.md`.
Harness root `C:/kyty/s100`. Everything below is measured unless marked otherwise.

> **This report was rewritten after an adversarial audit.** Its first version, the first ROADMAP
> edit and commit `8a9de7b` claimed that M3 was CLOSE and that G and R1 were closed. **That claim
> is withdrawn.** The defects are recorded in the sealed addendum
> `pred/03_audit_addendum.md` (10 653 B, `f3c2104b7a27b448a6c46a9526531c22e3d809546be5c51d90cca4e333ecad75`);
> `pred/01` and `pred/02` are untouched, as seals must be. Read §11 before quoting anything here.

**The three numbers route E must open with (`ROADMAP.md` §5 item 5):** the 60 FPS budget is
≤ ~3.0 µs a draw on the median frame and ≤ ~2.3 µs on a p99 frame (7 284 draws); the CPU path
stands at **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms**, unchanged — this session measured
no new baseline; **M3 is still GAP and M4 and M5 are still not done.**
**60 FPS is not promised: the chance is ~15 % (8…25 %).**

---

## 1. Result

**M3 remains GAP. G and R1 are alive, open and unlicensed. The order M3 → M4 → M5 is untouched.**

What the session did establish is that **the sealed constant 2.2535 is wrong in a direction that
narrows the gap**, and by how much:

    the sealed constant                  2.2535    -> min VERDICT_INPUT 15.078   GAP by 0.422 ms (s98)
    with the sampler term restored       2.595188  -> min VERDICT_INPUT 15.420   GAP by 0.080 ms
    (cen100b: T1 1.664154 + T2 0.4905 + T3 0.337034 + T5 0.1035)

and that **the rule as sealed cannot decide M3 in the CLOSE direction at all**, because its term
test is one-directional: it adds work the floor removes and V2 keeps, and has no slot for work the
floor **keeps** and V2 **deletes** — which the session's own cited authority prices at
**0.773…1.935 ms**, three to eight times the margin, in the subtractive direction. With that
included the minimum verdict input is **≤ 14.97 ms**, and the gap widens rather than closes.

The withdrawn arithmetic is printed beside, permanently: ADDEND 2.918040 / 2.916948 ⇒
VERDICT_INPUT 15.743040…17.192040 and 15.741948…17.190948. Its numbers are right; its composition
was not. See §11.

---

## 2. Two seals, two instruments, two runs

Both are published; neither is re-scored into the other. **The `branch` row is what each seal's
rule returned; §11 says why the CLOSE one does not stand.**

| | `pred/01_addend_census.md` | `pred/02_moved_mark.md` |
|---|---|---|
| seal | 19 152 B, `4c90060f91c21052238e0395abe2229e316012849c6bd54623d858edc5cf8c65` | 11 043 B, `b1930f69f83a77d3bba359d4d18f0653f7fea6a331232dc9edaaf46c2a82e137` |
| instrument | existing gate `bindlap` (s85/86) | new gate `blmove` (s100), moved mark |
| binary | `34206e3f…` (session-99 final) | `6f7475b8…` (session-100 build A) |
| confirmation | `cen100b`, 900 s, 90 pairs | `mov100b_entry1`, 900 s, 90 pairs |
| controls | 19/19 technical, 6/6 strict | 23/23 technical, 6/6 strict |
| T1 images | 1.664154 ms (48 013.674 slots) | 1.659044 ms (47 866.5 slots) |
| T3 samplers | 0.337034 ms (`bl_smp_us`) | inside T34 |
| T4 shader data | 0.404808 ms (`bl_sd_us`) — **struck by `pred/03` §2** | inside T34 |
| T3 + T4 | 0.741842 ms | **0.664996 ms** |
| instrument cost | C = 0.436552 ms, subtracted by that rule | C = 0.140948 ms, not subtracted |
| bias bound | — | B = 0.001092 ms |
| ADDEND as that rule composed it | 2.999996 / 2.563444 | 2.918040 / 2.916948 |
| branch that rule returned | **GAP** (short by 0.111556 ms) | **CLOSE — WITHDRAWN, see §11** |
| **ADDEND with T4 struck** | **2.595188 ⇒ 15.420188…16.869188 ⇒ GAP by 0.079812** | **2.555165 ⇒ 15.380165…16.829165 ⇒ GAP by 0.119835** |

`pred/01` §3.1 pre-declared this exact branch before any session-100 data existed: *"Without T4 it
is 2.5988 ⇒ 15.424 … 16.873 ⇒ GAP by 0.076 ms."* **The session landed on its own pre-declared
branch.**

**The two instruments agree where they can be compared.** `T3 + T4` differs by
0.741842 − 0.664996 = **0.076846 ms** over 9 107.1 stages a flip = **8.44 ns a stage**, the size of
the two extra timestamps and five extra `Add`s `bindlap` takes inside that region and `blmove` does
not. Image populations agree to **0.31 %** (48 013.7 against 47 866.5) across different binaries
and runs. Neither figure is an identity; both are consistency checks of the expected size.

---

## 3. What the census is, and why the mark price cancels

The instrument is sound; the audit that attacked it hardest confirmed so. `pred/02` gate
**`blmove`** (`KYTY_BIND_LAP_MOVE`, default 0, MEASUREMENT ONLY) takes, inside
`RenderExecutor::PrepareBindings`, **exactly two timestamps and four `Add`s a stage in both
phases**. Phase 0 closes right after the image loop; phase 1 right after the `shader_data` copy.
The phase alternates per stage **type** (`blm_turn[stage % 16]++ & 1`), so each type contributes
equally to both spans.

    T34 = (s1 - s0) * stages_per_flip        s0, s1 = ns a stage, per block
    T1  = (blm_img0 + blm_img1) a flip * 34.66 ns   (sealed s88 unit cost, population measured)

Each close reads `NowNs()` **before** its four `Add`s and `blm_t0` is taken after `NowNs()`
returns, so neither span contains any mark cost at all — stronger than the seal's "cancels term by
term". The measured phase balance on `mov100b_entry1` is **5.250549 against 5.250713 image slots a
stage (0.0031 %)** and **1.221278 against 1.221185 sampler slots (0.0076 %)**; the base arm's eight
`blm_*` sums are **exactly 0**, not merely below the 0.001 darkness ratio; the residual bias bound
is **B = 0.001092 ms**. Per-block `T34` has sd 0.044951 ms over 90 blocks, so SE(median) ≈ 0.006 ms.

`blmove`'s own ABBA cost is reported and never used: **C = 0.140948 ms a flip**, or
**+0.387 % ± 0.112 % cpu/draw, t = +6.91**. `bindlap`'s was 0.436552 ms.

### 3.1 The terms, and which of them survives

| term | (i) the floor removes it | (ii) V2 keeps it (`s94/rewrite94/gpu-driven.md`) | status |
|---|---|---|---|
| T1 images | `BindFloorPrepareStage` replaces the image loop; `bf_img` = "stub image-view descriptors written" | §4 `mh_bind` basis: "V2 adds 47 885 × (19.66 + 15.00 ns) = 1.66 ms [M units s88]" | in the sealed constant already; population refreshed |
| T2 writable slots | same | §4 basis "written slots 490.5 [M s94]" | 0.4905 sealed, not re-measured |
| **T3 samplers** | same; `prepared.samplers` is left **empty** and `CommitBindings`' `floor_sources` supplies one cached handle per slot without calling `NativeSampler` | §4 basis "**+ samplers 345 [M s86]**" — the one item genuinely dropped from the constant | **stands: +0.337 ms** |
| **T4 shader data** | **FALSE**: `descriptors.cpp:673` does `shader_data.assign(ShaderDataDwords(), 0u)` — the floor writes every dword and removes only the gather | **FALSE**: the push §3 names is `descriptors.cpp:3887-3891`, **inside `CommitBindings`, which the floor keeps** | **STRUCK (`pred/03` §2)** |
| T5 synchronisation | — | user decision, session 98 (`bd96b`, +103.5 µs) | 0.1035 sealed |

**Named and excluded, with the half each fails** (fixed in the seal before any data, and all of
these survived the audit): the permutation `find_if` and its `specialization ==` compare
(`pg_pms_us` 298.72 µs, s90) — **fails (i)**, verified: `pipelineCache.cpp:3269-3295` sits outside
every `bind_floor` guard, so it is already inside `F` and adding it would double count;
`AheadTake` 2 557, `pg_mat` 666.9, `pg_pm` 461.9, memo 72, stamps 196 — **fail (ii)**, §4's
`mh_prog` row lists them under *Disappears*; `pg_pre` 1 541 and key+find 255 — **fail (i)**, the
floor keeps the pipeline lookup; readable buffer slots (59.3 ns each) — **fail (ii)**, §3 has the
shader fetch V#s through BDA.

**And the class the test has no slot for at all:** work the floor **keeps** that V2 **deletes**,
starting with `CommitBindings`' write and emit halves. That is defect A of `pred/03` and it is
what makes the rule unable to decide CLOSE. See §11.

---

## 4. Runs, in order. Nothing is re-scored, nothing is retried into admission.

| tag | hold | binary | outcome |
|---|---|---|---|
| `cen100a` | 300.1 s | `34206e3f…` | ADMITTED_PILOT, 22 pairs, all controls clean |
| `cen100b` | 900.3 s | `34206e3f…` | **ADMITTED_ADDEND_CENSUS**, 90 pairs, 19/19 + 6/6, **GAP** |
| `mov100a` | 300.1 s | `6f7475b8…` | ADMITTED_PILOT, 22 pairs, all controls clean |
| `mov100b` | — | `6f7475b8…` | **ENTRY FAILURE, NOT_MEASUREMENT**: `GpuHangAbort: role=4 requested=2976 known=2975 current=3071`, never reached the scene, `nvlddmkm` 153 at 02:06:10 |
| `mov100b_entry1` | 900.3 s | `6f7475b8…` | **ADMITTED_MOVED_MARK**, 90 pairs, 23/23 + 6/6; its rule returned CLOSE, **withdrawn in §11** |

`mov100b` is the historical **entry** hang (6.67 % of entries, the uncapped BVH traversal
`cs=0x380bb9d636390bae` named in session 98), not a floor hang and not a defect of the instrument.
It is recorded as an entry failure and the retry used the distinct tag `mov100b_entry1` under the
same fixed protocol and budget, with no cache-policy change — the first of the at most two isolated
attempts `pred/02` §4 allows. **Five entries this session, one hang.** The floor was not used in
any session-100 run.

**Admission evidence for `mov100b_entry1`:** work **+0.041242 %**, area split **+0.005223 %**, area
match **100 % (90/90 pairs)**, C5 **0.000412**, C9 **0.001323**, orientations **[45, 45]**, 2 610
rows an arm, 187 GateArm blocks, criterion 3 **VALID**, and an independent recount written after
the scorer and sharing no code with it **agrees on every published figure**. An adversarial auditor
re-parsed the raw log with its own code and reproduced **every published digit**.

**Reported, never deciding:** `guards.py` returns **7 PASS, 2 FAIL, 1 WARN, 2 SKIP** on
`mov100b_entry1` — check 3 resolution and check 6 cores ("something else used the machine"). The
same two failed on `cen100a` and `cen100b`, including with nothing of this session running, so
check 6 is noisy here. They are not criteria of either sealed rule, and the arm-symmetry controls
that are (area, work, C5, C9) are clean.

---

## 5. The session-98 L3 debt is paid, and the bound tightens 22×

`ROADMAP.md` owed "a counter of the short clear paths actually taken in the base arm". Two
always-on counters were added behind no gate: **`clr_taken_meta`** and **`clr_taken_img`**, where
`TryConsumeComputeMetaClear` / `TryConsumeComputeImageClear` consume a dispatch
(`renderCompute.cpp:406`, `:410`).

    mov100b_entry1, both arms (they are not gated, so the arms agree):
      clr_taken_meta  2.0005 / 1.9994 a flip
      clr_taken_img   6.9992 / 6.9975 a flip
      total           9.000  / 8.997  a flip   of 268.02 / 267.98 dispatches = 3.358 % / 3.357 %

Session 98's `bf_clr_skip` is a **shape** census and read **198.01 a flip = 73.8 %**. Applying the
sealed `bf98.py` form `|dF_L3| ≤ count × 7.967 µs` with the real count:

    |dF_L3| <= 9.00 * 7.967 / 1000 = 0.0717 ms   (was 1.578 ms)
    F_a +- L3 = [14.202, 14.346]    F_c +- L3 = [12.753, 12.897]

**Caveats carried:** this is measured in an **unfloored** run on a different binary; under the
floor the frozen snapshot changes which shortcuts fire, and `bf_clr_skip` is structurally
unreachable at `bfmode=2`. The two counters are not the same population as `bf_clr_skip`: the new
one bounds how many shortcuts a **normal** frame takes, which is the quantity session 98 asked for,
not a re-measurement of session 98's runs.

---

## 6. `PrefetchComputePipelines`, measured on the current binary and not attacked

Session 96 measured `pl_pref_ns` = 1 961.1 µs a flip over 8 calls (6.2 % of the frame) and nobody
has touched it since. This session measured its decomposition from its own logs, with **no new code
and no extra run** (`mov100b_entry1`, settled window, both arms):

    da_walk_us   1 836.9 / 1 837.5 us a flip over 5.00 walks
    da_queue_us    769.1 /   769.4 us a flip  =  41.9 % of the walk, inside QueueDrawAhead
                                                 under PipelineCache::m_mutex
    da_q         7 986   /  7 987   requests a flip  =>  125 mutex acquisitions a flip at the
                                                 shipped 64-request batch
    da_take_us   2 345.2 / 2 348.6 us a flip (the AheadTake pickup, a separate debt)
    da_hit/miss  8 652 / 74

A knob on that batch is a three-line change with a ready A/B (`da_hit`/`da_miss`/`da_late`).
**It was NOT built and NOT measured**: the session kept its build small so that the deciding
measurement did not ride on a hot-path change.

---

## 7. Source changes, and how ROADMAP §6 is satisfied

One build, **`6f7475b8a6b9636aa31938d97f26c1bd4b7dbfd97213dd01b99b8cd3109268c0`**, from
`patch_s100a.py` (8 anchors, all unique, dry-run first). `check_gate_order.py` ran after the patch
and before the build: **Gate 110/110, Knob 23/23, GATE ORDER: clean**. Build exit 0, 0 errors.

* **gate `blmove`** (`KYTY_BIND_LAP_MOVE`, default 0) — `gates.h` and `gates.cpp` LAST row.
* **eight counters** `blm_s0_ns blm_s0_n blm_s1_ns blm_s1_n blm_img0 blm_img1 blm_smp0 blm_smp1`.
* **two counters** `clr_taken_meta` / `clr_taken_img`, always on, behind no gate — they
  deliberately break the "every `bf_*` reads 0 at `bindfloor=0`" invariant of `frameStats.h:1597`,
  following the precedent of `bf_igc_*`.

**No default moved, no shipped path changed, no knob default moved.**

**ROADMAP §6** is satisfied through `ROADMAP.md` §5 item 4 ("счётчик — это правка, и его ABBA — это
A/B"): `blmove` ran a full ABBA in `mov100a` and `mov100b_entry1`, its cost is significant and
measured (+0.387 % ± 0.112 % cpu/draw, t = +6.91), and its arms are symmetric on every strict
control. **The video-pass debt does not arise**: neither addition can reach the renderer — `blmove`
only reads a clock and increments counters, and `clr_taken_*` are pure counters at sites that
already returned. That is an argument from the diff, confirmed by the audit, not a measurement.

---

## 8. Harness

`C:/kyty/s100`, ported from `C:/kyty/s99` by a freshly written `C:/kyty/s99/s100_port.py`.
`PRECONDITIONS PASS: 5 root constructs; 15 sealed texts; 18 live paths + 4 expression paths;
gates 1092 B / 99 names` → `PORT DIAGNOSTIC: clean; carried=1792 ledger=41 skipped=59`.

New port work: **repair 7**, for the four session-99 scorers whose `PRED` is `ROOT / '…'` or
`Path('…')` and escapes the port's `const()` regex; it inserts `prev99/` into the relative part
only. Also an explicit `R1_ARCHIVE` entry for `verify_port99/verify.py`; the port failed loudly on
it rather than silencing it. Sealed texts grew **10 → 15** into `s100/prev99/pred/`, byte-exact.
`accept99.sh` arrives carrying `R=C:/kyty/s99` — **do not run it**.

**Scorers, all proved offline before the first run:** `cen100.py` with `test_cen100.py` — **30
checks**, including one mutation per control that must fail that control; `mov100.py` with
`test_mov100.py` — **28 checks**. `cen100.py` was dry-run on session-99's `log_eng99a4.txt` and
**reproduced session 99's own published metrics exactly** (work −0.02365018145291 %, 22 pairs,
orientations [11, 11]). Two later edits added optional `x_fields`/`main_fields` parameters to
`cen100.read_log`; `cen100b`'s score was re-derived after each and is **byte-identical**.
Independent recounts share no code with the scorers and agree to `abs_tol 1e-10`.

---

## 9. Proved, and not proved

**Proved.** That the sealed constant 2.2535 dropped one measured item of its own source line — the
samplers, `bl_smp_us` = 345.1 µs (`drm86a`, s86), measured again here at 0.337034 ms on the current
binary in the same scene — and that restoring it narrows the session-98 gap from **0.422 ms to
0.080 ms** without closing it. That the moved-mark instrument measures a quantity of its own order
without its probe entering the answer (phase balance 0.003 %/0.008 %, bias bound 0.001092 ms, base
arm exactly dark). That the session-98 L3 bound tightens from 1.578 ms to **0.0717 ms**. That
`PrefetchComputePipelines`' walk is **41.9 % mutex-held queueing** at **125 acquisitions a flip**.

**Not proved, and withdrawn.** That G and R1 are closed. That M3 is decided. The rule both seals
use is **one-directional** and cannot decide CLOSE; the missing subtractive direction is worth
**0.773…1.935 ms** against a 0.243 ms margin (`pred/03` §1). Term T4 fails its own inclusion test
(`pred/03` §2). The floor's own stub work has never been timed and is inside `F` (`pred/03` §4).

**Also not proved**, unchanged from before: that 60 FPS is unreachable — `ROADMAP.md:46` stands.
That `F_a`/`F_c` are right: carried from session 98 on binary `9aa93e73…`, not re-measured. That
the mode-2 residual pessimism of session 99 is bounded. That the DRS clock debt is discharged —
`KYTY_GPU_CLOCK_PIN=1` was set as `ROADMAP.md` requires and the arms stayed matched (C9 0.13 %),
which is not the same thing. That the cross-queue ACB tear or the entry-hang BVH traversal are
fixed — neither is, and the second cost this session a 900-second run. **No frame-rate gain, no
speedup, no 60 FPS.**

---

## 10. Provenance

* Binaries: session-99 final `34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f`
  (`cen100a`, `cen100b`); session-100 build A
  `6f7475b8a6b9636aa31938d97f26c1bd4b7dbfd97213dd01b99b8cd3109268c0` (`mov100a`, `mov100b`,
  `mov100b_entry1`), installed now. **No rebuild between the last measurement and this report.**
* `gates_base.txt` unchanged: 1 092 B / 99 names /
  `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`. `blmove` is the **34th** name
  absent from it and lives only in schedule arms; `ABSENT` grows 33 → 34 for the next port.
* Seals: `pred/01_addend_census.md` 19 152 B `4c90060f…`, `pred/02_moved_mark.md` 11 043 B
  `b1930f69…`, `pred/03_audit_addendum.md` 10 653 B `f3c2104b…`. **Not editable.**
* Every raw log, stdout, `<tag>.json`, score and recount is hashed in `runs100/manifest100.json`.
* Git HEAD at the start: `013b81aee6c668f96836abfa2375b435437fe3f9`, branch `merge-upstream`, only
  `3rdparty/nlohmann_json` dirty and deliberately excluded.
* Session-100 commits: **`8a9de7b`** (the work, with the withdrawn CLOSE claim in its message),
  **`64a0762`** (hash stamp) and **`af5572e04681e81ff07883d83ea6029e65212b21`** (this rewrite, the withdrawal and
  `pred/03`; no source file touched). **No push.**

---

## 11. The adversarial audit, and what it overturned

After the verdict was published, five independent auditors were run against it, each on a distinct
lens and each instructed to refute and to default to refuted when uncertain. **All five refuted**,
and their three decisive source claims were then verified by hand against the tree. The defects are
sealed in `pred/03_audit_addendum.md`; in summary:

1. **The term test is one-directional (fatal).** It admits only "the floor removes it ∧ V2 keeps
   it". The symmetric class — "the floor **keeps** it ∧ V2 **deletes** it", which must be
   **subtracted** — has no slot. `gpu-driven.md:63` names one with a number:
   `CommitBindings 2 035 (tr/wr/em 962/626/447 [M s94]) → 0.1–0.3`, and the floor keeps the write
   and emit halves (its own comment: "the SHAPE of the descriptor writes, which the floor does not
   change"). **0.773…1.935 ms to subtract, 3.2× to 8.0× the margin.**
2. **T4 fails half (i) and its half (ii) is inside `F` (fatal).** `descriptors.cpp:673` is
   `prepared.shader_data.assign(ShaderDataDwords(), 0u)` — the floor writes every dword and removes
   only the gather; and the push §3 credits to V2 is `descriptors.cpp:3887-3891`, inside
   `CommitBindings`, which the floor keeps. **Strike T4 ⇒ GAP by 0.080…0.120 ms.**
3. **The headline "two dropped measured items" was half wrong (fatal to the framing).** That table
   line has three items and the constant dropped **one** — the samplers. `shader_data` has no
   measured value anywhere in the design document.
4. **The floor's own stub work is inside `F` and was never timed (fatal).** CLOSE would need it to
   cost under 4.1 ns a slot-touch over 47 866.5 image and 11 165 sampler touches. Unmeasured.
5. **The constant was changed on the executor's authority under the user's delegation, not the
   user's own decision**, and the ROADMAP entry was written after the runs.
   `docs/next-session-100.md` §1 required the user's decision in ROADMAP **first**. The work was
   authorised; a global M3 verdict on that constant is **not licensed**.

**What the audit confirmed as sound:** every number and both recounts; the selector and estimators;
that the moved-mark spans contain no mark cost at all; that the base arm is exactly dark; that the
two phases draw from the same stage population; that the `find_if` exclusion is right and avoided a
real double count; that the floor genuinely stubs samplers; that session 85's "the sampler half
≈ 0" is a marginal-gain statement and does not contradict T3; that no control was widened; that no
run was dropped from the ledger; and that neither source addition can reach the renderer.

**What the next rule must do** is in `pred/03` §8: be two-directional with the subtractive half
**measured**; price the floor's own stub so every term is net of it; price terms in V2's units
rather than mixing them with the current implementation's; and put the constant to the user before
acting on it.
