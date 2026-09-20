# Session 101 — route E: M4, with M3 decided

**Order M4 → M5 stays** (the user's decision of session 97, `ROADMAP.md` §5 item 5). Read
`ROADMAP.md` **first**: §0.1 (the session-100 addendum), §2 E (the M3 block with the session-100
addendum, then **M4** and **M5**), §4 (the vblank plateau and the endpoint rule), §5 item 5,
§6, §7. Then `C:/kyty/s100/FACTS.md` in full (in git `docs/local-session-100.md`), then
`C:/kyty/s100/README.md`, and the two sealed rules `C:/kyty/s100/pred/01_addend_census.md`
(19 152 B, `4c90060f…`) and `02_moved_mark.md` (11 043 B, `b1930f69…`). **Sealed texts are
immutable:** a correction goes into a new sealed addendum, never into the file.

**Open the report with the three numbers** (`ROADMAP.md` §5 item 5 demands it): budget ≤ ~3.0 µs
a draw (median) / ≤ ~2.3 µs (p99, 7 284 draws); the carried reference path is 6.4 µs a draw,
31.6 ms a frame, GPU busy 12.8 ms — **session 100 measured no new baseline**; undone: **M4, M5**.
**Do not promise 60 FPS: the chance is ~15 % (8…25 %).**

## 0. Where route E stands

* **M1 closed P and P+G** (session 95). **M2 closed F** (session 95).
* **M3 is decided: CLOSE. G and R1 are closed** by the sealed rule, with the addend measured
  rather than assembled: `mov100b_entry1`, ADDEND 2.918040 / 2.916948 ms, VERDICT_INPUT
  15.743040…17.192040 and 15.741948…17.190948, both minima ≥ 15.5. Thresholds, `F_a` = 14.274,
  `F_c` = 12.825 and the min/max form were not touched and not re-measured.
* **`cen100b` returned GAP on the same question with the other instrument** (ADDEND_hi 2.999996
  would have closed it; its instrument cost 0.436552 ms exceeded the margin). Both results are
  published. **Do not re-score one into the other and do not quote only the one you prefer.**
* **CLOSE is a rule verdict, not a proof about 60 FPS.** `ROADMAP.md:46` stands: *НЕ ДОКАЗАНО,
  что 60 FPS недостижим, и что переписывать нечего.* No speedup was measured in session 100.
* **M4 and M5 are not started.** M4's own rule closes only **P**, and P was already closed by M1;
  the user was asked exactly this in session 97 and kept the order. **Ask again at the start of
  session 101 whether M4 is still worth a session now that M3 has closed G and R1**, and record
  the answer in `ROADMAP.md` before acting. If the answer is "skip M4", M5 becomes the next item
  and `ROADMAP.md:1333-1334` (M5 not before M3 **and** M4 close) is the line that must be
  renegotiated in writing first.

## 1. M4, as sealed

`ROADMAP.md` §2 E: mark the mutations inside the six `MutScope` sites, `mh_rt`, `mh_prog` and
`mh_disp` as **semantic** (order mandatory: draw N+1 samples what N drew) or **bookkeeping**;
count the shares and the 32/64-draw chunks that contain a semantic one.
**Rule: semantic time > 8 ms or > 20 % of chunks need sequence ⇒ P closed.** One session.

Before any number: **write and seal the classification of every site as semantic or bookkeeping,
from the sources, and the estimator and controls.** That is what made sessions 96–100 work. The
classification is the whole measurement; a site classified after the numbers exist is not a
measurement.

## 2. Practical starting points that already exist

* **`mutsite`** (gate, session 69) already splits the render-mutex hold into `mh_pro`, `mh_rt`,
  `mh_prog`, `mh_bind`, `mh_emit`, `mh_tail`, `mh_disp`, `mh_pres` and costs 0.10 ms a frame with
  99.68 % coverage of `a_hold_us`. `gates_base.txt` pins `mutsite=0`, so it is a schedule arm.
* **`m4baton`** (knob, session 68) already runs the real draw path for a PM4 range on a second
  thread while GuestGpu is parked, with `bat_*` counters; `ROADMAP.md` warns that `cpu/draw` in
  the baton arm is **not** a verdict.
* The harness pattern that worked in session 100: port first, seal second, scorer plus offline
  tests third (one fixture that must be admitted and one mutation per control that must fail it),
  pilot 300 s, confirmation 900 s, independent recount, then one ROADMAP edit.

## 3. Side items now on the board, none of them route E

* **The entry hang cost session 100 a 900-second run.** `mov100b` died at entry with
  `GpuHangAbort: role=4 requested=2976 known=2975`, `nvlddmkm` 153 — the historical 6.67 %
  uncapped BVH traversal `cs=0x380bb9d636390bae`. **Five entries in session 100, one hang.**
  The design is ready and nothing is built: `C:/kyty/s100/design98/loops.md` —
  `KYTY_BVH_LOOP_CAP` (environment variable, default 0, plan 65536), in the translation-cache
  signature with a **separate cache directory**, trip counters in the fault-buffer tail.
  It touches about eleven files including the SPIR-V backend, needs a HIST run first and an
  **offline register/SASS check on the 3.8 ms lighting CS `5323c4ef4f785055`** (one of the 13
  BVH programs; one extra live register there has cost 45 % before), and the first capped run is
  fully cold. **A correctness bug for every user of the emulator, not route E.**
  Note: `loops.md`'s host-side line anchors are stale by ~18 lines; the shader-side ones are exact.
* **`PrefetchComputePipelines`, now decomposed** (session 100, current binary, both arms agreeing,
  no new code): `da_walk_us` 1 836.9 µs a flip over 5.00 walks, of which `da_queue_us` 769.1 µs =
  **41.9 %** is inside `QueueDrawAhead` under `PipelineCache::m_mutex`; `da_q` 7 986 requests a
  flip ⇒ **125 mutex acquisitions a flip** at the shipped 64-request batch. A knob on that batch
  is a three-line change in `graphicsRun.cpp:1403` with its own controls (`da_hit`, `da_miss`,
  `da_late`). **Not built in session 100 on purpose** — the deciding measurement was not going to
  ride on a hot-path change. Outside the sealed M1–M5 order ⇒ a user decision.
* **`da_take_us` = 2 345 µs a flip** (the `AheadTake` pickup) is still not split.
* **The cross-queue ACB tear** and **every gate except `bindfloor` being unaudited against being
  read twice inside one operation** are both still open.
* **The DRS clock debt** (`ROADMAP.md:1094`, `:1402`) is still open and still costed at "days".
  Session 100 set `KYTY_GPU_CLOCK_PIN=1` as `ROADMAP.md:1307` requires and its arms stayed matched
  (C9 0.13 %); that is not the same as solving the debt.

## 4. Traps of session 100 that turned out to be real

1. **An instrument can be more expensive than what it measures.** `bindlap` costs 0.4366 ms a
   flip and the quantity it measures is 0.74 ms, so `pred/01` had to subtract the whole
   instrument and lost the branch. The fix was not a tighter estimate but the **moved-mark**
   idiom of session 88, where both phases pay identical marks at different program points and the
   price cancels term by term. Reach for it whenever the answer is the same order as the probe.
2. **A phase that alternates per stage would have been biased**: stages arrive as VS then PS, so
   a per-stage counter gives the two stage types opposite phases forever. `blm_turn[stage % 16]`
   alternates **per stage type**. The measured balance is 0.003 % on images and 0.008 % on
   samplers — do not assume it, control it.
3. **A dropped report line does not fail a scorer that only checks fields it can see**: losing
   one `FrameTrace-x` line silently shrinks the population instead of failing, because the block
   then fails completeness and is simply rejected. `STREAMS_COMPLETE` (every main-line flip in
   the measured region carries all three streams, excluding the final flip) is the control that
   catches it. This was found by a fixture, not by a run.
4. **`dispatches` is on the MAIN `FrameTrace` line, not on `FrameTrace-x`.** A scorer that looks
   for it among the `-x` fields drops every row and reports an empty population.
5. **`guards.py` checks 3 and 6 failed on all three admitted runs** with nothing of the session
   running on the machine. They are reported, not deciding, and the arm-symmetry controls that
   decide (area, work, C5, C9) were clean. Do not silence them and do not promote them.
6. Carried and still real: all `KYTY_*` go **positionally** to `enter_scene.py`; `--attempts 1`
   (the default is 3); `gen_gates.py` only with `--check`; **never rebuild between a measurement
   and its acceptance** (`guards.py` check 10 hashes the exe installed *now*); after a GPU hang
   the GPU runs ~60 s to the TDR and the dead process holds `_kyty.txt`; the vblank plateau
   quantises `dt_us`, so 16.7…33.3 ms all read 30.0 FPS; `summary4.py`'s `cpu_net_us` under lite
   **is** `cpu_gpu_us`, and `spin_gpu_us` lives on the `FrameTrace-draw` line.
7. **The port's `const()` regex only matches a bare quoted literal.** Four session-99 scorers
   write `PRED = ROOT / '…'` or `Path('…')`; `s100_port.py` repair 7 inserts `prev99/` into the
   relative part only. The next port must carry repair 7 forward and grow `ABSENT` 33 → **34**
   (`blmove`).

## 5. The port, first

Write `s101_port.py` **fresh in the source folder `C:/kyty/s100/`** (`SRC = C:/kyty/s100`,
`DST = C:/kyty/s101`), modelled on `C:/kyty/s99/s100_port.py`. **Never run a carried
`*_port.py`.** Advance: the COMMA chain 26 → 27 roots (`s101…s75`); `area_verdict.py`
`range(101,70,-1)`; `shift91.py` `range(101,66,-1)`; `s94lib.py` 10 roots, `bda93.py` 11,
`stg92.py` 12; `regime94.py` 9 roots plus the `s101` fallback; the 18 sealed-path constants and
repair 7's four expression paths repointed to `prev100/pred/`; sealed texts grow **15 → 17**
(the two session-100 seals). `ABSENT` becomes **34 names**. Assert `gates_base.txt` is still
1 092 B / 99 names / `00c116dc…0594d8`, and that `gates.cpp` now yields **133** `{"KYTY_*","name"}`
entries (133 − 99 = 34).

## 6. Working procedure and the deliverable

PLAN with a measurable question, then CODE → TEST → a fresh VERIFY. One executor owns the GPU,
the log and the caches; no background build, scorer or review during a hold; build only through
`build_local.cmd`; `check_gate_order.py` after any gate/knob patch and **before** the build.
**ROADMAP §6 expects the session to end with a source change that passed A/B** — a counter is a
change and its ABBA is the A/B (`ROADMAP.md:1317-1318`). At the end: one edit to ROADMAP, then
FACTS (`C:/kyty/s101/FACTS.md`, mirrored as `docs/local-session-101.md`),
`docs/next-session-102.md`, both game contexts **including their environment-variable and gate
list**, and the mandatory commit without push; do not capture the dirty `3rdparty/nlohmann_json`.

## 7. Must not be claimed

That session 100 proved 60 FPS unreachable, or that CLOSE licenses anything beyond G and R1 ·
that `F_a`/`F_c` were re-measured (they were not; session 98, binary `9aa93e73…`) · that
`cen100b`'s GAP was revised or is an error · that session 99's `B_a`/`B_c`, its HIGH or its zero
addend enter the M3 arithmetic · that the moved mark being free **in the difference** makes the
instrument free (its cost is 0.140948 ms a flip and is printed) · that the L3 counter re-measures
session 98's runs (it is an unfloored run on another binary) · that the DRS clock debt, the
mode-2 residual pessimism, the cross-queue ACB tear or the entry-hang BVH traversal are
discharged · that M4 or M5 may be skipped, re-ordered or advanced without the user's decision
written into `ROADMAP.md` first. **And no frame-rate gain, no speedup, no 60 FPS.**
