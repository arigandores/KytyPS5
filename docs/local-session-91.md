# Session 91 — FACTS

**The single source of truth for this session's numbers.** `README.md` is the harness and the
traps, `PLAN.md` §0 is the reading that fixed the plan, `pred/01_shift.md`, `pred/02_pin.md` and
`pred/03_repair.md` are sealed and were not edited. `read91/report_*.md` are the five readers'
reports; `review91/review_*.md` the three adversarial reviews.

Every number is a **ratio of sums over its window**, a paired mean over the programme's cycles
(`summary4.build_cycles`, warm-up 3, min block 5), or an exact zero where the counter is never
`Add`ed. Labels: **[M]** measured in this session; **[I]** inference, model-dependent or
between-run; **[K]** known before the sealing that scores it (not a blind test).

---

## 0. In one sentence

**The game's dynamic resolution reads GPU timestamps, and on this emulator a GPU timestamp is the
pacer-scaled CPU clock written by the GuestGpu thread at PM4 parse — so a CPU-side knob moves the
DRS rung; that is why two knobs were unmeasurable, and it gives the estimator the brief asked for a
concrete form: a one-site, per-process pin of that clock (`KYTY_GPU_CLOCK_PIN`), built, with a
positive control, sealed and NOT YET RUN because the game was not opened in this session.**
Meanwhile the fallback estimator (TB, the total effect with a bracket) was sealed, validated on 20
archived runs and applied to both blocked contrasts without a run: **D1 (`bufimp`) is CLOSED as a
frame-time regression** — +13.4 % `dt` at matched area in the window where the game latched both
arms LOW (`area_verdict` VALID there: split −0.001 %, 51/51, work −0.075 %), carried by **4.6 ms a
flip of GuestGpu blocked in forced host-read drains** that the census arm does not have (1.6 µs) —
and **`dapin=3` with the record path off cuts GuestGpu CPU per draw by 9.19 % (t −133)**, while its
GPU cost stays UNDETERMINED: the rung-mediated share is the whole answer there, and only the pin
can read it.

### 0.1 Defects of my own text, listed first

1. **`pred/01` §5 anchored its host-read rule on the whole-arm `dt` contrast of the INVALID
   `bim90a`** (+4 110.8 µs, FACTS s90 §3) — exactly the leak session 90's trap forbids — and its H5
   is itself a between-arm contrast of that run. Re-anchored here on TB's admitted T `dt`
   (+13.493 % of 31 017 µs ≈ 4 185 µs, half 2 093): **the verdict does not change** (4 820 µs). And
   **H1 and H5 read the same nanoseconds** (`masterSemaphore.cpp:138-143` adds one wait to both
   `SemWaitGpuNs` and the `host-read` site): counted once below.
2. **`pred/01` §5 asked for `gpu_blocked`, `gpu_idle`, `gpu_proc`** — main-line fields that read 0
   in every lite run (`TimingsEnabled`), the same vacuity `PLAN` §0 B item 2 found in
   `hostread_wait_us`. Printed; 0.000 in both arms.
3. **`pred/01` §7 "the largest chance dh in an A/A is 6.7 pp" is false under the tool's own
   definition**: `aa67b` reads **+8.80 pp** draw-weighted. Still far below +28.4 / −53.6.
4. **`pred/02` R4 was a defective band, found BEFORE any pinned run** by running the sealed readout
   on the record: fragments (1-vblank half-frames) are never in [1990, 2030), and modern runs carry
   2–14 % of them, so eight unpinned LOW runs read 83.7–98.9 %. Repaired under `pred/03` (R4'), and
   R4 is still printed.
5. **`PLAN` §0 A said "real Vulkan GPU time never reaches the guest" — overstated.** EOP interrupts
   and flip completions arrive at REAL GPU completion (`commandScheduler.cpp:569-586`), stamped with
   the pacer-scaled clock; only the timestamp VALUES are parse-time. The pin does not cover those
   channels, and only a pinned run can say whether they matter.
6. **`PLAN` §0 A's "the guest then sees the wall span ≈ 31 ms" is a prediction**, not a reading:
   what holds by construction is that the pinned G is today's G divided by the speed (≈ ×2).
7. **W's pair set is the refused matched subset of `bim90a`, to the digit**: the full run's 51
   matched pairs all start at n ≥ 6 181 and read −0.989 % ± 0.207 %, t −9.57 — as W does. W is
   justified ONLY by the scene-locked latch (last HIGH flip 6 146; 18 runs of the record drop at
   6 144–6 147), a window fixed by flip number from rung labels before any outcome was read; on it
   W1 could fail only on work.
8. **T3 MISSED, and the reason is the bracket's premise, not the direct effect.** `bim90a`'s in-run
   CPU price is +1.159 % ± 0.387 %, ≈ 4.3 SE from the A/A pool (+0.048 ± 0.337): its HIGH flips sit
   early in arm-1 blocks (mean position 8.5 against 14.0) — arm-switch carryover, not a rung price.
   The run's own windows imply ≈ +0.28 % (early n < 6 150: T −1.170 % at dh −91.1 pp; late: −0.917 %
   at dh 0). **CPU D on a rung-shifted run is therefore [I]**, like GPU D, and "UNDETERMINED" is not
   evidence of a null.
9. **The scoreboard below is inflated in substance**: T1, T2, T4, T6, T7 bracketed magnitudes that
   were on disk or published before sealing [K].

---

## 1. What was done, and what was NOT

| step | state |
|---|---|
| harness `C:/kyty/s91`, ported by `C:/kyty/s90/s91_port.py` (written fresh in the SOURCE dir) | **clean**; `gates_base.txt` 1092 B, 99 names, sha256 `00c116dc…0594d8`, unchanged; `gen_gates.py --check` only |
| the reading (`PLAN.md` §0), five readers | done — mechanism, prior art, empirics, anchors, plumbing |
| `pred/01_shift.md` sealed **before `shift91.py` ran on any log** | 10 161 B, sha256 `82877f4a23e1f15a…`, mtime − ctime +0.003 s |
| TB validation (V1–V4) and targets (§5, §6, W) | done, §3–§5 |
| `patch_s91.py` + `patch_s91b.py` (the pin, its positive control, the counters) | built: **`887ede9f8323297f…`, 23 623 680 B**; NOT installed in the game folder (`enter_scene` installs it); the installed exe is still `12b0940a…` |
| `pred/02_pin.md` (three pinned runs) and `pred/03_repair.md` (R4') | sealed: 8 360 B `ebf4b9f041c9a308…` +0.000 s; 2 747 B `7c9fae4cc4bc58b4…` +0.000 s |
| **the pinned runs `pin91a/b/c`** | **NOT RUN — the user asked that the game not be opened until they say so** |
| tests | `memory_tracker_tests` all cases passed; `resource_materialization_tests` all cases passed; `resource_tracking_tests` output **byte-identical to session 90's** (the known "SRT runtime" failure, then the process ends the same way) |

---

## 2. The reading, in five lines (details `PLAN.md` §0 A)

1. **Mechanism [read in source].** `RELEASE_MEM data_sel=3` → `Sync::ReadReferenceClock()` →
   `KernelReadTsc()` = freeze-excluded TSC × pacer speed, memcpy'd into guest memory at PM4 parse
   (`graphicsRun.cpp:2562-2564`, `sync.cpp:45-54`, `pthread.cpp:187-216`, `videoOut.cpp:1187-1206`).
2. **The rung follows the scaled clock, not real GPU time [M, record]**: 65 DRS-active runs — before
   an UP transition S = speed × dt is lower in 59/65 (t −9.69), `gpu_busy_us` t −1.46.
3. **CPU pays nothing for the high rung within a block, GPU pays ≈ 11–13 % [M, old binaries]**:
   cpu/draw +0.048 % ± 0.337 %, gpu/draw +11.23 % ± 0.47 % (296 cells, four rung-varying A/As).
4. **The A/A slope of cpu on area is reverse causation [M]**: switches to LOW follow expensive frames;
   with d_k3 and fragment share in the regression the rung term is ≈ 0.
5. **Prior art [read]:** every admission rule on disk voids all six rung-varying A/As; RCV (s81) was
   refuted by its own rule; within-rung OLS was wrong 17–22×; no configuration without DRS was ever
   tried. **The pin is the first.**

---

## 3. TB, validated on 20 archived runs [M; not blind, K]

`shift91.py --validate` (`_validate91b.txt`, identical to `_validate91.txt` after the review's
latent fixes):

| set | result |
|---|---|
| **V1** 12 A/A runs, T `cpu_net/draw` \|t\| < 3 | **PASS** — largest \|t\| 2.58 (`aa74a`, contaminated in its own session) |
| **V2** D interval contains 0 in ≥ 10 of 12 | **PASS at the edge, 10/12** (`aa74a` t +2.58, `vfy80a` t −2.06 on 30 cycles); for the six single-rung A/As it is V1 restated at 2 SE |
| **V3** 8 valid runs: \|dh\| ≤ 0.5 pp, sign, \|t\| ≥ 3, within max(0.15 pp, 1 SE) of F2 | **PASS 8/8** — e.g. `pgl90a` +1.596 % (F2 +1.586), `tfs85a` −4.531 % (−4.591) |
| **V4** in-run price, 4 mixed A/As | **PASS** — cpu +0.801 / −0.148 / −0.002 / +0.439 %; gpu +13.20 / +8.52 / +9.04 / +14.22 % |

---

## 4. D1 (`bufimp`) — CLOSED as a frame-time regression

### 4.1 The host-read census of `bim90a` (`pred/01` §5) [M, within-arm]

| per flip, n ≥ 2100 | census arm (`bufimp=1`) | import arm (`bufimp=2`) |
|---|---:|---:|
| `FrameTrace-wait` host-read µs | **1.55** | **4 609.58** |
| host-read wait events | 0.001 | 8.365 |
| `FrameTrace-submit` host-read µs | 0.00 | 210.64 |
| host-read submit events | 0.000 | 7.418 |
| `hostread_waits` (hazard hits) | 0.009 | 19.468 |
| `semwait_gpu_us` | 2.09 | 4 609.05 (the same ns as the wait row) |
| `submits` | 38.55 | 46.32 |

**Rule (re-anchored, §0.1 item 1): (wait + submit) host-read = 4 820 µs a flip ≥ 2 093 ⇒ the
forced host-read drain carries the lost frame time.** GuestGpu blocks in `m_master.Wait` after a
submit forced mid-recording (`CommandScheduler::Wait`, tick == CurrentTick), 8.4 times a flip, ≈
550 µs each. It is BLOCKED time, so it is invisible to `cpu_gpu_us` (thread CPU time) — which is
why the frame got longer while every counted thread did less. **And it is why the import arm drops
to the LOW rung: the blocked span lengthens the GuestGpu wall span inside the frame, i.e. G.**

### 4.2 TB on `bim90a` [M; CPU D and GPU D are I]

| | reading |
|---|---|
| dh | **−53.61 pp**, SE 4.13 |
| T `cpu_net/draw` | **−1.071 %**, SE 0.069, t −15.44 |
| T `dt` | **+13.493 %**, SE 0.152, t +88.51 |
| T `gpu/draw` | −8.539 %, SE 0.486 (mostly the rung) |
| p (in-run, C = 26) | cpu +1.159 % ± 0.387; gpu +13.37 % ± 1.45 |
| D `cpu_net/draw` | [−0.859, +0.024] % — UNDETERMINED **[I]** (§0.1 item 8) |
| D `gpu/draw` | [−4.106, +1.608] % — UNDETERMINED [I] |

### 4.3 W — the latch window, n ≥ 6150 [M, with §0.1 item 7]

`area_verdict.py bim90a --first-frame 6150`: HIGH 0.0 %, split **−0.001 %**, match **51/51**, work
**−0.075 %** ⇒ **VALID**. Matched: `cpu_net/draw` **−0.974 %** (t −9.47), `dt` **+13.382 %**
(t +52.68), `gpu/draw` −2.149 % (t −18.63). On summary4's cycles over the same window
(`review91/wcheck.py`): −0.917 % and +13.775 %.

**Verdict by the rule sealed in `pred/01` §6: W1 and W3 hold ⇒ D1 is CLOSED as a regression at the
LOW rung for late-scene content.** The frame-time loss does not depend on the rung: early (dh −91
pp) +13.35 %, late (dh 0) +13.4–13.8 %. **`bufimp` stays 0, and there is nothing to tune: the import
makes the GPU read guest pages AFTER the CPU may write them, so a write must wait for the read, and
in this scene the CPU rewrites these pages 19.5 times a flip.**

---

## 5. `dapin` with the record path off (`dap88a`) — TB [M; D is I]

| | reading |
|---|---|
| dh | **+28.38 pp**, SE 3.14 |
| T `cpu_net/draw` | **−9.193 %**, SE 0.069, t **−132.9** |
| T `dt` | −7.542 %, t −69.7 |
| T `gpu/draw` | +4.375 %, SE 0.335, t +13.05 |
| p (in-run, C = 76) | cpu **−0.173 % ± 0.329**; gpu **+10.71 % ± 0.43** |
| D `cpu_net/draw` | **[−9.386, −8.881] %** — negative [I] (the premise holds here: p_cpu ≈ 0) |
| D `gpu/draw` | **[−0.156, +2.774] %** — UNDETERMINED [I] |

**`dapin=3` makes GuestGpu ~9 % cheaper per draw when every draw takes the direct path** (with the
record thread on, the record says −738 µs ≈ −2.3 %). **Its GPU cost — the tenth-session debt — is
not settled by TB**: the rung carries +2.3…+3.9 % of T `gpu/draw`, and the remainder straddles 0.
`pred/02` run A reads it with the rung held.

---

## 6. Corrections to this programme's record

1. **`summary4.py`'s `cpu_net_us` is `cpu_gpu_us` in every lite run** — it parses only `FrameTrace:`
   and says so itself in a NOTE. FACTS s90 §4.1's "+1.5760 %, t +14.38" is `cpu_gpu_us`; true
   `cpu_net_us` **+1.5851 %, t +14.46** [M]. `ROADMAP` §4 and s90 `pred/01` named the wrong tool.
2. **`hostread_wait_us` is structurally 0 in lite** (`Scope` stamps under `TimingsEnabled` only);
   s90's "the waits are under ~50 ns each" is withdrawn and **s90 E3 was VACUOUS**. The waits are
   ≈ 550 µs each (§4.1).
3. **The host-read `SiteScope` FACTS s90 §8 proposed has existed since before session 90**
   (`bufferCache.cpp:1610`) — the number that answered "where did 4.1 ms go" was on disk. **Eighth
   session in eight.**
4. **`accept90.sh` inside s91 pointed at s90** (the port rewrites only `.py`); `accept91.sh` is new.
5. **Session 81's "pacer→DRS refuted" (`pac81a/b`) does not follow**: 0 HIGH in 2/2 pacer-off runs
   is what the pacer model predicts (null probability ≈ 0.30).
6. **`ob_stream_us` is also 0 in lite** (same `TimingsEnabled` gate) — the `ObtainBuffer` stream
   ring, 19.66 MB a flip in 13 380 copies in `pgl90a`, has never been timed in a measurement run.
7. `daepceil`'s comment still says "(default 1)" and it is 0 — carried.

---

## 7. What was built (no default moved)

* **`KYTY_GPU_CLOCK_PIN`** (environment, read once per process; `sync.cpp`): 1 = the guest GPU clock
  drops the pacer speed (`KernelReadTscBase`, freezes still excluded, rdtsc inside the lock); 2 =
  POSITIVE CONTROL, the scaled clock at half rate. One `GpuClockPin: mode N` line. Counters:
  `gclk_n` (every read), `gclk_pin` (pinned reads — never Added without the pin), **`gclk_adv` /
  `gclk_sadv` — arming by VALUE** (the guest clock's advance over the scaled clock's; 1/speed at 1,
  0.5 at 2), `gclk_back` (backward steps).
* **The upload memcpy split, live in every run**: `CopyGuestToStaging` returns whether it pooled;
  `stg_pool_n/_b/_ns`, `stg_in_n/_b/_ns`, `stg_inbig_n`, `stg_in_gpu_b`, `up_tmp_n/_b`,
  `stg_img_pool_b`, `stg_img_in_b`; census `bi_b_small`, `bi_reg_small`. Bytes raw, times raw ns.
* **Host-read waits timed in lite**: `hr_free`, `hr_gpuw(_us)`, `hr_forced(_us)`, `hr_sync(_us)`,
  `hr_call_us`.
* Tools: `shift91.py` (TB/W/census), `pin91.py` (scores `pred/02`+`pred/03`), `accept91.sh`.

---

## 8. The pinned runs — PENDING

`pred/02_pin.md` §1 carries the three commands; `accept91.sh <tag>` reads each. Not run: the user
asked that the game not be opened until they say so.

---

## 9. The scoreboard — `pred/01_shift.md`, 22 entries

| # | reading | verdict |
|---|---|---|
| V1 | 12/12 \|t\| < 3 | HIT [K] |
| V2 | 10/12 contain 0 | HIT [K], at the edge |
| V3 | 8/8 | HIT [K] |
| V4 | 4/4 | HIT [K] |
| H1 | 4 609.6 µs ≥ 2 000 | HIT |
| H2 | 1.55 ≤ 100 | HIT |
| H3 | 210.6 ∈ [30, 800] | HIT |
| H4 | 8.37 wait events (19.47 hazard hits) ∈ [3, 25] | HIT (either counter) |
| H5 | +4 607 ≥ 1 500 | HIT — **the same ns as H1, and a contrast of the INVALID run: not counted separately** |
| T1 | dh −53.61 ∈ [−55, −35] | HIT [K] |
| T2 | −1.071 %, t −15.4 | HIT [K] |
| **T3** | D [−0.859, +0.024] | **MISS** — the bracket's premise failed in-run (§0.1 item 8) |
| T4 | +13.49 %, t +88.5 | HIT [K] |
| T5 | p_gpu +13.37, C 26 | HIT |
| T6 | +28.38 | HIT [K] |
| T7 | −9.193 %, t −132.9 | HIT [K] |
| T8 | D [−9.386, −8.881] | HIT |
| T9 | p_gpu +10.71, C 76 | HIT |
| T10 | D_gpu [−0.156, +2.774], midpoint +1.31 | HIT by wording — **its gloss "dapin=3 costs GPU time" is NOT established** |
| W1 | VALID | HIT — informative only on work (§0.1 item 7) |
| W2 | −0.974 % ∈ [−2.0, +0.5] | HIT |
| W3 | +13.38 %, t +52.7 | HIT |

**22 entries, 21 hits by wording, 1 miss; counting H1/H5 once and setting the [K] items aside, the
blind part is 12 entries, 11 hits, 1 miss.** The miss is a premise I wrote (item 4 of `PLAN` §0 A
applied to a run whose in-run price contradicts it). **Four defects of my own text are listed in
§0.1 before a single pinned run exists — the fifth consecutive session in which my own defects
outnumber the world proving me wrong.**

---

## 10. What is NOT closed

| debt | next number | since |
|---|---|---|
| **The pin works or not** | `pin91a` (R1–R4' against the unpinned dh +28.4 pp) and `pin91b` (the positive control) | **91** |
| **`dapin`'s GPU cost, ELEVENTH session** | `pin91a` E3 at a fixed rung; TB left it in [−0.16, +2.77] % [I] | 79 → 91 |
| **the 64 KiB split of the upload bytes** | `stg_in_b / (stg_in_b + stg_pool_b)`, live in every run now — first reading in `pin91a` | 90 → 91 |
| the `ObtainBuffer` stream ring (19.66 MB/flip, 13 380 copies) | its timer is 0 in lite: a lite-live timer, the `hr_*` idiom | 90 |
| the per-element price of `ResourceSpecialization::operator==` | a counter on the vector lengths | 90 |
| prefetch lines read (s89), the take unsplit (s89), the witness share of `RebindImages` (s88), route B items 2, 8, 10, 12, 3 | unchanged | 83–89 |
| ~~D1: import guest memory for buffers~~ | **CLOSED in session 91: +13.4 % frame time at matched area, 4.6 ms/flip of forced host-read drains** | 85 → **91** |
| ~~where `bim90a`'s 4.1 ms went~~ | **CLOSED: GuestGpu blocked in forced host-read drains, 4 609.6 µs/flip wait + 210.6 submit** | 90 → **91** |
| ~~an estimator that survives a DRS shift~~ | **BUILT, NOT YET TESTED ON A RUN**: the pin (primary) and TB (fallback, validated on the record) | 79 → 91 |

## 11. The arithmetic

60 FPS = 16 667 µs; shipped 31 642 µs (`acc82a`, not re-measured); floor `S` 20 838 µs. **Nothing
here removes work.** D1 is closed with a loss, not a gain. The pin turns two knobs from unmeasurable
into measurable; what they then measure is hundreds of microseconds at most.
