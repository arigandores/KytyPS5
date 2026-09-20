# Session 102 — route E, M3: the FLOORED halves, and the regime split

**Order M3 → M4 → M5 stays** (the user's decision of session 97, `ROADMAP.md` §5 item 5). Read
`ROADMAP.md` **first**: §0.1 (the session-101 addendum), §2 E (the M3 block and its session-101
correction), §4 (the vblank plateau and the endpoint rule), §5 item 5, §6, §7. Then
`C:/kyty/s101/FACTS.md` in full (in git `docs/local-session-101.md`) — **including its §11** —
then `C:/kyty/s101/README.md`, and the three sealed texts
`C:/kyty/s101/pred/01_two_directional.md` (29 915 B, `091ecf76…`),
`02_regime_addendum.md` (9 735 B, `b4ef078b…`) and
**`03_audit_addendum.md` (20 259 B, `688b7be4…`)**. **Sealed texts are immutable:** a correction
goes into a new sealed addendum, never into the file — which is exactly what `pred/03` is.

**Open the report with the three numbers** (`ROADMAP.md` §5 item 5 demands it): budget ≤ ~3.0 µs a
draw (median) / ≤ ~2.3 µs (p99, 7 284 draws); the carried reference path is 6.4 µs a draw, 31.6 ms
a frame, GPU busy 12.8 ms — **session 101 measured no new baseline**; undone: **M3 (GAP), M4, M5**.
**Do not promise 60 FPS: the chance is ~15 % (8…25 %).**

## 0. Where M3 stands after session 101

* **M3 is GAP, and the branch does not depend on the constant** — it holds at 2.65, at the user's
  2.2535, at session 100's 2.595188 and at session 101's 2.455173. **G and R1 are alive, open and
  unlicensed.** Do not resurrect any CLOSE.
* **What was measured and stands:** `CommitBindings`' write build **0.675455 ms** and emit
  **0.440120 ms** a flip, unfloored, on binary `b70d0096…`, by gate `cbmove` — a moved mark whose
  price cancels in each difference and whose null span priced that mark at **8.35 ns a commit**.
  Per-commit total **211.7 ns against session 94's 213.4 ns: 0.8 %**, two binaries, two
  instruments, seven sessions apart.
* **What was withdrawn** (`pred/03`, four FATALs): the margin "GAP by 0.219827 ms" as *the* result;
  the claim that the subtractive half is measured; the "15 ms of GuestGpu CPU" reading of the
  regime; `C_cbmove` as a point value; "all 15 predictions HIT".
* **The procedural failure that must not recur.** The constant was put to the user before any
  measurement, the user delegated, and the executor **measured without recording the change in
  `ROADMAP.md` first**. That is session 100's Defect E repeated in breach of session 101's own
  plan. **Ask, RECORD, then measure — the record goes in before the first run, not after it.**
* **The regime finding, corrected.** `vulkanWindow.cpp:1195` tests `KYTY_GPU_CHECKPOINTS` by
  **presence**, so `=0` turns checkpoints ON, refuses the record thread and arms a per-draw
  `EndRendering` pair, a per-draw `eAllCommands` barrier and a per-operation mutex. Removing it
  takes `gpu_busy` **48.6 → 12.8 ms** and the frame **48.9 → 32.4 ms**. Sessions 99–100 — including
  `cen100b`, the source of A1 and A3 — ran in that regime; `bf98a`/`bf98c`, the source of
  `F_a`/`F_c`, did not.

## 1. The measurable question for session 102

> **What do `CommitBindings`' write build and emit cost UNDER THE FLOOR, what does the floor's own
> stub cost over the same slots, and which of the three regime causes is worth the 6×?**

The first two are one run. `bindlap` is in the pinned binary and `cb_timed` is armed by it, so a
**floor-armed ABBA with `bindlap=1` in BOTH arms** gives `bl_wr_us` and `bl_em_us` as the floor
pays them — the subtractive half's measured part, in the regime `F_a`/`F_c` were measured in — and
its **arm difference prices the floor's own stub inside `CommitBindings`**, which is `pred/03` §8.2
of session 100 and S2 of session 101, unmeasured for three sessions. The third is one more ABBA at
a 32 ms frame: `recordthread=1|0`.

Seal it before a single number, and this time:

1. **Record the constant and the rule in `ROADMAP.md` BEFORE the first run**, with the user's
   answer quoted. If the user delegates again, record the delegation *and* the executor's choice
   there, before measuring. This clause has now failed twice.
2. **Be conservative toward the branch that can fire.** CLOSE is arithmetically impossible while
   ADD is frozen; PROCEED is not. Publish **both** bounds — the one that favours CLOSE and the one
   that favours PROCEED — or the verdict is a restatement of the composition.
3. **Price the floored write build.** The floor does **not** remove it (`descriptors.cpp:3833`:
   `floor_sources` sits inside the write-building loop and still builds ≈ 144 000 descriptor
   entries a flip). Session 101 dropped it from both directions; it belongs in SUB.
4. **Re-measure A3 in the corrected regime**, or label it a dead-regime time. It is the only ADD
   term that is a time, and it is 1.5× the withdrawn margin.
5. **Pair the estimator of an instrument's own cost** and publish a range. `C_cbmove` read
   0.071/0.109/0.355 ms across three runs of one binary; the paired estimate is 0.17–0.18 ms.
6. **Give the control suite a frame-time band, a `rec_n` limb and a `gpu_busy_us` limb.** Two
   consecutive sessions have had a full suite admit a run that was 50 % off.

## 2. What is already built and needs no new code

* **`cbmove`** (gate, session 101, default 0): the moved-mark census of `CommitBindings`. Both
  phases pay exactly two timestamps and four `Add`s at different program points; the null phase
  prices the mark pair directly. The audit attacked it hardest and confirmed it in every detail.
  Reach for this idiom whenever the answer is the same order as the probe.
* **`bindlap`** (gate, session 85/86) already carries `bl_tr_us`, `bl_wr_us`, `bl_em_us`,
  `bl_cmt_n`, and `cb_timed` does not care whether the floor is armed — which is why one floored
  ABBA answers two questions at once.
* **The floor machinery** is proven reversible (session 98: latch by frame, 857 falls, 0 hangs) and
  its burn chain exists (`settled99_norec.recommendation()`, LOCK/TUNE/CAUSAL_TEST). **A new binary
  invalidates session 99's burn LOCKs (17800 / 10200): budget three calibration pilots.**
* The harness pattern that worked: port first, seal second, scorer plus offline tests third (one
  fixture that must be admitted, one mutation per control that must fail it — session 101 left
  **nine controls with no mutation**, fix that), pilot 300 s, confirmation 900 s, independent
  recount, **then an adversarial audit before publishing**, then one ROADMAP edit.

## 3. Side items, none of them route E

* **`KYTY_GPU_CHECKPOINTS` is a correctness bug for every user** — one line
  (`vulkanWindow.cpp:1195`: compare the value, as `KYTY_GPU_MARKERS` already does). It was not
  fixed in session 101 because the binary was pinned by the IDENTITY control. `KYTY_FRAME_TRACE`
  is presence-tested too, so a sweep of the whole tree is the honest fix. **A one-line fix plus a
  sweep is a source change; its A/B is the `recordthread`/regime contrast already measured.**
* **The entry hang** (uncapped BVH traversal `cs=0x380bb9d6…`, 6.67 % of entries) is still
  unbuilt: `C:/kyty/s101/design98/loops.md`, `KYTY_BVH_LOOP_CAP`, about eleven files including the
  SPIR-V backend, a separate translation-cache directory, a fully cold first run, and an offline
  register/SASS check on the 3.8 ms lighting CS. **Session 101 had three entries and no hang.**
* **`PrefetchComputePipelines`**: 41.9 % of the walk is queueing under `PipelineCache::m_mutex`,
  125 acquisitions a flip at the shipped 64-request batch. A knob is three lines with its own A/B.
  Outside M1–M5 ⇒ a user decision.
* **`da_take_us` = 2 345 µs a flip** is still not split. **The cross-queue ACB tear** and **every
  gate except `bindfloor` being unaudited against being read twice inside one operation** are open.
  **The DRS clock debt** (`ROADMAP.md` §7) is open and still costed at "days".

## 4. Traps of session 101 that turned out to be real

1. **A composition whose every zero points at an impossible branch decides nothing.** Session 101's
   "conservative toward CLOSE" was conservative in the only direction that could not matter.
2. **A sealed environment can select a regime.** One variable carried from session 99 moved the
   frame 50 % and nobody noticed for three sessions, because no control watched the frame time.
3. **An instrument's own cost is not a point value.** Same binary, same scene: 0.071 / 0.109 /
   0.355 ms. Pair it or publish a range.
4. **Agreement can be a cancellation artefact.** The emit agreed with session 94 "to 1.4 %" only
   because a −6.1 % per-commit difference met a +4.9 % population difference.
5. **A prediction re-registered after it missed is not a prediction**, and a prediction entailed by
   another carries no information. Session 101 published 15 and had at most 9.
6. **Editing the scorer after the first run makes "published exactly as scored" unverifiable**
   when `--out` refuses to overwrite and no earlier score was saved.
7. **`guards.py` checks 3b and 6 failed on all three runs** with nothing else of the session
   running. Reported, not deciding. Do not silence them and do not promote them.
8. Carried and still real: all `KYTY_*` go **positionally** to `enter_scene.py`; `--attempts 1`;
   **never rebuild between a measurement and its acceptance**; after a GPU hang the GPU runs ~60 s
   to the TDR and the dead process holds `_kyty.txt`; the vblank plateau quantises `dt_us`;
   `summary4.py`'s `cpu_net_us` under lite **is** `cpu_gpu_us`; `spin_gpu_us` lives on the
   `FrameTrace-draw` line.

## 5. The port, first

Write `s102_port.py` **fresh in the source folder `C:/kyty/s101/`** (`SRC = C:/kyty/s101`,
`DST = C:/kyty/s102`), modelled on `C:/kyty/s100/s101_port.py`. **Never run a carried `*_port.py`.**
Advance: the COMMA chain 27 → 28 roots (`s102…s75`); `area_verdict.py` `range(102,70,-1)`;
`shift91.py` `range(102,66,-1)`; `s94lib.py` 11 roots, `bda93.py` 12, `stg92.py` 13; `regime94.py`
10 roots plus the `s102` fallback; the r6 paths (now **12 files / 20 constants**, plus `cm101.py`'s
own `PRED`/`PRED2`) and r7's four expression paths repointed to `prev101/pred/`; sealed texts grow
**18 → 21** (the three session-101 seals). `ABSENT` becomes **35 names** (add `cbmove`). Assert
`gates_base.txt` is still 1 092 B / 99 names / `00c116dc…0594d8`, and that `gates.cpp` now yields
**134** `{"KYTY_*","name"}` entries (111 gates + 23 knobs; 134 − 99 = 35).

## 6. Working procedure and the deliverable

PLAN with a measurable question, **record the constant in ROADMAP**, then CODE → TEST → a fresh
VERIFY → **an adversarial audit**. One executor owns the GPU, the log and the caches; no background
build, scorer or review during a hold; build only through `build_local.cmd`; `check_gate_order.py`
after any gate/knob patch and **before** the build. **ROADMAP §6 expects the session to end with a
source change that passed A/B** — and note that five consecutive sessions have satisfied it with a
counter while moving no default and no shipped path; the `KYTY_GPU_CHECKPOINTS` fix is the first
candidate in a long time that moves a real one. At the end: one edit to ROADMAP, then FACTS
(`C:/kyty/s102/FACTS.md`, mirrored as `docs/local-session-102.md`), `docs/next-session-103.md`,
both game contexts **including their environment-variable and gate list**, and the mandatory commit
without push; do not capture the dirty `3rdparty/nlohmann_json`.

## 7. Must not be claimed

That M3 is closed, or that G or R1 are closed or licensed — session 100's CLOSE is withdrawn and
session 101's margin is withdrawn · that session 101 measured the subtractive half (it measured one
of four terms, unfloored) · that the regime finding is a speedup — nothing was made faster, a
diagnostic that had been on by accident was turned off · that any number of sessions 94–100 is
revised · that the split of the regime's cost between the lost record thread, the per-draw barrier
and the per-operation mutex is known · that `F_a`/`F_c` were re-measured (session 98, binary
`9aa93e73…`) · that the DRS clock debt, the mode-2 residual pessimism, the cross-queue ACB tear or
the entry-hang BVH traversal are discharged · that A5 (0.1035 ms) may be changed without the
**user's** decision recorded in `ROADMAP.md` first — the design document's own band for that row is
2–10 ms [U] and at its low end the composition would read CLOSE · that M4 or M5 may be skipped or
re-ordered without the user's decision written into `ROADMAP.md` first. **And no frame-rate gain,
no speedup, no 60 FPS.**
