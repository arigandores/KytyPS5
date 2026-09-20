# Session 101 — route E, M3: a TWO-DIRECTIONAL addend

**Order M3 → M4 → M5 stays** (the user's decision of session 97, `ROADMAP.md` §5 item 5). Read
`ROADMAP.md` **first**: §0.1 (the session-100 addendum), §2 E (the M3 block with the session-100
addendum and its withdrawal), §4 (the vblank plateau and the endpoint rule), §5 item 5, §6, §7.
Then `C:/kyty/s100/FACTS.md` in full (in git `docs/local-session-100.md`) — **including its §11** —
then `C:/kyty/s100/README.md`, and the three sealed texts
`C:/kyty/s100/pred/01_addend_census.md` (19 152 B, `4c90060f…`),
`02_moved_mark.md` (11 043 B, `b1930f69…`) and
**`03_audit_addendum.md` (10 653 B, `f3c2104b…`)**. **Sealed texts are immutable:** a correction
goes into a new sealed addendum, never into the file — which is exactly what `pred/03` is.

**Open the report with the three numbers** (`ROADMAP.md` §5 item 5 demands it): budget ≤ ~3.0 µs a
draw (median) / ≤ ~2.3 µs (p99, 7 284 draws); the carried reference path is 6.4 µs a draw, 31.6 ms
a frame, GPU busy 12.8 ms — **session 100 measured no new baseline**; undone: **M3 (GAP), M4, M5**.
**Do not promise 60 FPS: the chance is ~15 % (8…25 %).**

## 0. Where M3 stands after session 100

* **M3 is GAP. G and R1 are alive, open and unlicensed.** Session 100's first report and commit
  `8a9de7b` claimed CLOSE; that claim was **withdrawn** after an adversarial audit and is recorded
  as withdrawn in `pred/03`, in `FACTS.md` §11, in `ROADMAP.md` §0.1, in the route-E table and in
  the M3 block. **Do not resurrect it.**
* **What survived and is the session's real result:** the sealed constant 2.2535 was assembled from
  a three-item line of `s94/rewrite94/gpu-driven.md` §4 and dropped one of those items — the
  samplers. Re-measured on the current binary in the same scene, `bl_smp_us` = **0.337034 ms**, so
  the addend becomes **2.595188** and the gap narrows from **0.422 ms (session 98) to 0.080 ms**.
* **Why it still cannot close:** the term test is **one-directional**. It admits "the floor removes
  it ∧ V2 keeps it" and adds it, and has **no slot** for "the floor **keeps** it ∧ V2 **deletes**
  it", which must be **subtracted**. `gpu-driven.md:63` names one with a number:
  `CommitBindings 2 035 (tr/wr/em 962/626/447 [M s94]) → 0.1–0.3`, and the floor keeps the write
  and emit halves (1 073 µs). That is **0.773…1.935 ms to subtract**, three to eight times the
  margin the withdrawn CLOSE rested on.
* A second defect of the same rule: the term T4 (`shader_data`) failed its own half (i) —
  `descriptors.cpp:673` is `prepared.shader_data.assign(ShaderDataDwords(), 0u)`, so the floor
  writes every dword and removes only the gather — and its half (ii) pointed at
  `descriptors.cpp:3887-3891`, **inside `CommitBindings`, which the floor keeps**, i.e. at work
  already inside `F`.
* A third: **the floor's own stub work is inside `F` and has never been timed.** Only counts exist
  (`bf_img`, `bf_smp`, `bf_reuse`). Every added term must be **net of it**.

## 1. The measurable question for session 101

> **What is the NET addend of the M3 rule: Σ(the floor removes it ∧ V2 keeps it) − Σ(the floor
> keeps it ∧ V2 deletes it), with both sums measured and every term net of the floor's own stub?**

This is the shape `pred/03` §8 prescribes. Seal it before a single number:

1. **Two-directional composition**, with the subtractive sum non-empty from the start. Its first
   member is `CommitBindings`' write and emit halves. The session-94 split
   (tr/wr/em 962/626/447 µs) exists; what does not exist is a measurement of **what the floor
   keeps of it** and **what V2 would keep of it**. The first is measurable today with a `bindlap`
   sibling on the three `cb_lap` marks that already exist (`bl_tr_us`, `bl_wr_us`, `bl_em_us`,
   `bl_cmt_n`); the second is a design reading and must be quoted, not invented.
2. **Price the floor's stub.** A timer on `floor_sources` and on `BindFloorPrepareStage` is the
   minimum. Without it no added term is net and the rule cannot decide in the CLOSE direction.
3. **One unit system.** T1 is priced in V2's modelled unit (34.66 ns a slot); T3 is priced at the
   current implementation's 30.3 ns memoised lookup. The current image cost in `mov100b_entry1` is
   70.18 ns a slot — twice the V2 unit. Mixing them silently is what let the withdrawn CLOSE look
   larger than it was. State the unit of every term.
4. **Put the constant to the user first.** `docs/next-session-100.md` §1 required the user's
   decision in `ROADMAP.md` **before** acting; session 100 acted under a delegation and recorded
   the change afterwards. Ask, record, then measure.
5. **Consider whether M3 can be decided at all this way.** If the subtractive half cannot be
   measured to better than ±0.3 ms, say so and take the honest GAP rather than a fourth screen.
   `ROADMAP.md:46` stands either way.

## 2. What is already built and needs no new code

* **`blmove`** (gate, session 100, default 0): the moved-mark census of the sampler loop plus the
  `shader_data` copy. The audit confirmed its spans contain no mark cost at all, its base arm is
  exactly dark, and its two phases draw from the same stage population (balance 0.0031 % on images,
  0.0076 % on samplers). **Reach for this idiom whenever the answer is the same order as the probe**
  — it is what separated `mov100b_entry1` from `cen100b`, where `bindlap` cost 0.4366 ms to measure
  0.74 ms.
* **`bindlap`** (gate, session 85/86) already carries `bl_tr_us`, `bl_wr_us`, `bl_em_us` and
  `bl_cmt_n` — the `CommitBindings` split the subtractive half needs. They were printed but not
  used in session 100.
* **`clr_taken_meta` / `clr_taken_img`** (session 100, always on): 9.00 a flip of 268.0 dispatches.
* The harness pattern that worked: port first, seal second, scorer plus offline tests third (one
  fixture that must be admitted and one mutation per control that must fail it), pilot 300 s,
  confirmation 900 s, independent recount, **then an adversarial audit before publishing**, then
  one ROADMAP edit. The audit is what caught session 100; do not skip it.

## 3. Side items, none of them route E

* **The entry hang cost session 100 a 900-second run.** `mov100b` died at entry with
  `GpuHangAbort: role=4 requested=2976 known=2975`, `nvlddmkm` 153 — the historical 6.67 % uncapped
  BVH traversal `cs=0x380bb9d636390bae`. **Five entries in session 100, one hang.** The design is
  ready and nothing is built: `C:/kyty/s100/design98/loops.md` — `KYTY_BVH_LOOP_CAP` (environment
  variable, default 0, plan 65536), in the translation-cache signature with a **separate cache
  directory**, trip counters in the fault-buffer tail. About eleven files including the SPIR-V
  backend; needs a HIST run first and an **offline register/SASS check on the 3.8 ms lighting CS
  `5323c4ef4f785055`** (one extra live register there has cost 45 % before); the first capped run
  is fully cold. `loops.md`'s host-side anchors are stale by ~18 lines, its shader-side ones exact.
  **A correctness bug for every user of the emulator.**
* **`PrefetchComputePipelines`, decomposed in session 100** on the current binary, both arms
  agreeing, with no new code: `da_walk_us` 1 836.9 µs a flip over 5.00 walks, of which
  `da_queue_us` 769.1 µs = **41.9 %** is inside `QueueDrawAhead` under `PipelineCache::m_mutex`;
  `da_q` 7 986 requests a flip ⇒ **125 mutex acquisitions a flip** at the shipped 64-request batch.
  A knob on that batch is a three-line change in `graphicsRun.cpp:1403` with its own controls
  (`da_hit`, `da_miss`, `da_late`). **Not built on purpose.** Outside M1–M5 ⇒ a user decision.
* **`da_take_us` = 2 345 µs a flip** (the `AheadTake` pickup) is still not split.
* **The cross-queue ACB tear** and **every gate except `bindfloor` being unaudited against being
  read twice inside one operation** are still open.
* **The DRS clock debt** (`ROADMAP.md` §7) is still open and still costed at "days".

## 4. Traps of session 100 that turned out to be real

1. **A one-directional census cannot close a two-directional question.** This is the session's own
   fatal defect and the most transferable lesson: when a rule can only add, its verdict in the
   adding direction is unsafe by construction. Write both sums or neither.
2. **"The floor removes it" must be read in the source, not from a comment.** The floor *zeroing*
   a vector is not the floor *removing* the work; and a design document's prose ("push user SGPRs
   as push data") can point at a site the floor **keeps**.
3. **An instrument can be more expensive than what it measures.** `bindlap` costs 0.4366 ms and
   measures 0.74 ms. The moved-mark idiom of session 88 is the fix; an estimate is not.
4. **A phase that alternates per stage would have been biased** — stages arrive as VS then PS, so a
   per-stage counter gives the two types opposite phases forever. `blm_turn[stage % 16]` alternates
   per stage **type**, and the balance is controlled, not assumed.
5. **A dropped report line does not fail a scorer that only checks fields it can see**: the block
   simply fails completeness and is rejected, silently shrinking the population.
   `STREAMS_COMPLETE` is the control that catches it. Found by a fixture, not by a run.
6. **`dispatches` is on the MAIN `FrameTrace` line, not on `FrameTrace-x`.**
7. **`guards.py` checks 3 and 6 failed on all three admitted runs** with nothing of the session
   running. They are reported, not deciding. Do not silence them and do not promote them.
8. **Publish only after an adversarial audit.** Five independent lenses, each told to refute and to
   default to refuted, overturned a verdict that had passed 23/23 technical controls, 6/6 strict
   controls, criterion 3, an independent recount and byte-identical re-scoring. Controls prove the
   run; they do not prove the rule.
9. Carried and still real: all `KYTY_*` go **positionally** to `enter_scene.py`; `--attempts 1`;
   `gen_gates.py` only with `--check`; **never rebuild between a measurement and its acceptance**;
   after a GPU hang the GPU runs ~60 s to the TDR and the dead process holds `_kyty.txt`; the vblank
   plateau quantises `dt_us`; `summary4.py`'s `cpu_net_us` under lite **is** `cpu_gpu_us`, and
   `spin_gpu_us` lives on the `FrameTrace-draw` line.
10. **The port's `const()` regex only matches a bare quoted literal.** Carry repair 7 forward and
    grow `ABSENT` 33 → **34** (`blmove`).

## 5. The port, first

Write `s101_port.py` **fresh in the source folder `C:/kyty/s100/`** (`SRC = C:/kyty/s100`,
`DST = C:/kyty/s101`), modelled on `C:/kyty/s99/s100_port.py`. **Never run a carried `*_port.py`.**
Advance: the COMMA chain 26 → 27 roots (`s101…s75`); `area_verdict.py` `range(101,70,-1)`;
`shift91.py` `range(101,66,-1)`; `s94lib.py` 10 roots, `bda93.py` 11, `stg92.py` 12; `regime94.py`
9 roots plus the `s101` fallback; the 18 sealed-path constants and repair 7's four expression paths
repointed to `prev100/pred/`; sealed texts grow **15 → 18** (the three session-100 seals).
`ABSENT` becomes **34 names**. Assert `gates_base.txt` is still 1 092 B / 99 names /
`00c116dc…0594d8`, and that `gates.cpp` now yields **133** `{"KYTY_*","name"}` entries (133 − 99 = 34).

## 6. Working procedure and the deliverable

PLAN with a measurable question, then CODE → TEST → a fresh VERIFY → **an adversarial audit**. One
executor owns the GPU, the log and the caches; no background build, scorer or review during a hold;
build only through `build_local.cmd`; `check_gate_order.py` after any gate/knob patch and **before**
the build. **ROADMAP §6 expects the session to end with a source change that passed A/B** — a
counter is a change and its ABBA is the A/B. At the end: one edit to ROADMAP, then FACTS
(`C:/kyty/s101/FACTS.md`, mirrored as `docs/local-session-101.md`), `docs/next-session-102.md`, both
game contexts **including their environment-variable and gate list**, and the mandatory commit
without push; do not capture the dirty `3rdparty/nlohmann_json`.

## 7. Must not be claimed

That M3 is closed, or that G or R1 are closed or licensed — session 100's CLOSE is **withdrawn** ·
that the withdrawal makes 60 FPS reachable or unreachable (`ROADMAP.md:46` stands either way) ·
that `F_a`/`F_c` were re-measured (session 98, binary `9aa93e73…`) · that `cen100b`'s GAP was
revised · that session 99's `B_a`/`B_c`, its HIGH or its zero addend enter the M3 arithmetic ·
that the `shader_data` term can be re-admitted without measuring, net of the floor's own fill, the
part of it a rewrite actually deletes · that the moved mark being free **in the difference** makes
`blmove` free (0.140948 ms a flip, printed) · that the L3 counter re-measures session 98's runs ·
that the DRS clock debt, the mode-2 residual pessimism, the cross-queue ACB tear or the entry-hang
BVH traversal are discharged · that M4 or M5 may be skipped or re-ordered without the user's
decision written into `ROADMAP.md` first. **And no frame-rate gain, no speedup, no 60 FPS.**
