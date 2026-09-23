# Sealed pre-registration 02 — session 104, route A Stage 1 ("kill or go"): runs `mut104` and `sh104`


**Immutable once written.** A correction goes into a new sealed addendum.

---

## 0. What this decides, and where it was decided

`ROADMAP.md` §0.1, "РЕШЕНИЯ ИСПОЛНИТЕЛЯ В СЕССИИ 104", items 3 and 6 (recorded before this text):
route A is reopened for evaluation under "maximum FPS", and its Stage 1 is two ABBA runs with the
GPU clock pinned, zero code, which produce **G** — the saving route A could at best deliver — and
apply the rule written there: **G < 3 ms ⇒ A closed for maximum FPS; G ≥ 3 ms ⇒ A proceeds by
stages** (`C:/kyty/s104_designA/review.md` §3). This document fixes the exact formulas, constants,
controls and predictions.

Nothing in Stage 1 ships. Binary under test: the installed
`16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352` (session 103), gate base
`gates_base.txt` sha256 `00c116dc…0594d8`.

## 1. The instruments, and why the combination is legal

| gate / knob | kind, default | what it arms | live in `KYTY_FRAME_TRACE=lite`? |
|---|---|---|---|
| `mutwide` (`KYTY_MUT_WIDE`) | knob 0..15, 0 | `MutScope` on bit 1 `PrepareDrawRenderState`, 2 `RefreshShaders`, 4 the `DispatchDirect` critical section, 8 `PrepareBda`; arming counter `mw_n` | yes (`MutScope` reads `Enabled()`) |
| `amut` (`KYTY_A_MUTATE`) | gate, 0 | the six `MutScope` sites of session 68 (`a_mut_us`, `a_mut_n`) and `MutexMark` (`a_hold_us`, `a_hold_n`, `a_wait_us`) | yes |
| `mutsite` (`KYTY_MUT_SITE`) | gate, 0 | `HoldLap` chain `mh_*`; also arms `MutexMark` | yes (`HoldLap` reads `Enabled()`) |
| `plkstat` (`KYTY_PIPE_LOCK_STAT`) | gate, 0 | `LockSplit` at the three `PipelineCache::m_mutex` sites: `pl_prog_*`, `pl_pipe_*`, `pl_cs_*` | yes |
| `pathlap` (`KYTY_PATH_LAP`) | gate, 0 | `PathLap` emit chain `pl_em_*` (raw ns) and `PathSpan`s outside the mutex `pl_proc/pref/eop/bar/sub/gc/cmd/look_*` (raw ns) | yes (`Enabled()`) |
| `shadowresolve` (`KYTY_SHADOW_RESOLVE`) | knob 0..16, 0 | K worker threads re-run the read-only half of binding resolution per draw and throw it away: `sh_jobs`, `sh_us`, `sh_push_us`, `sh_lock_us`, `sh_trk_us`, `sh_drop`, `sh_over`, `sh_wake`, `sh_img`, `sh_buf` | yes |
| `shadowmask` (`KYTY_SHADOW_MASK`) | knob 0..3, 3 | 1 image probes, 2 buffer probes, 3 both (session 64's main contrast) | — |

Also read, and live in lite: `cpu_gpu_us`, `dt_us`, `draws`, `dispatches`, `gpu_busy_us` (main line);
`spin_gpu_us`, `rec_n`, `bda_n` (count only; `bda_us` is a `Scope` and reads 0 in lite),
`da_walk_us`, `da_queue_us`, `da_take_us`, `da_hit`, `da_miss`, `da_late`, `da_walks`
(`FrameTrace-draw`); `rt_att`, `rt_kpx` and everything else on `FrameTrace-x`. **`spin_gpu_us`
lives on `FrameTrace-draw`, not on the main line** (session 83 trap); `cpu_net_us` is computed by
the scorer, never by `summary4.py`. Every field was verified to be printed, on this line, by the
installed binary (`log_reg104.txt`, `test_a104.py`).

**Legality.** `pathlap` **requires `mutsite=1` in the same arm** (`frameStats.h:2071-2085`: a
`PathSpan` refuses to arm while `Detail::t_hold_t0 != 0`, and only `HoldLap` sets it); both arms
carry both. `mutwide`'s four scopes arm on the knob bit alone (they do not need `amut`); `amut` is in
both arms so that `a_mut_us` of arm 0 is session 68's six sites (`S_lo`) and arm 1 adds the four
surfaces (`S_raw`), exactly as `flr83b`. `mutwide`, `plkstat` and `pathlap` are absent from
`gates_base.txt`, so the schedule owns them; `amut` and `mutsite` are pinned 0 there and the
schedule overrides them (as in session 83). Gates that time `CommitBindings` themselves
(`bindlap`, `drawstat`, `mergecost`, `cbmove`, `blmove`) stay 0. `amut+mutsite+plkstat+mutwide=15`
ran together as `plk83a`; `pathlap+mutsite` as `pl96a`; **the five together have never run** — the
arming controls of §4.2 are what admits the combination.

`shadowresolve` is **measurement only**: its probes read texture/buffer-cache slots without
protection against the GuestGpu thread's insert/delete (session 64 review: use-after-free risk
admitted). It ran clean on 2 200 worker frames (desert) and 30 900 frames (`sky64a`). The four
workers start on the first arm-1 block and stay; while the knob reads 0 they sleep in 5 ms steps
(`shadowResolve.cpp:124`), so arm 0 is "workers parked", not "no threads".

## 2. The runs

Both: Sky Garden, `--hold 300`, `--attempts 1`, `--no-install`, `gates_base.txt`,
`KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` positional,
**`KYTY_GPU_CHECKPOINTS` and `KYTY_REC` absent** (on this binary `KYTY_GPU_CHECKPOINTS=0` is harmless but
prints `GPU checkpoints off`, which the control of §4.1 refuses — absence is the rule of session
101), nothing else running on the machine.

* **`mut104`** — `KYTY_GATE_SCHEDULE="90+1800:mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1|mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1"`
* **`sh104`** — `KYTY_GATE_SCHEDULE="90+1800:shadowresolve=0 shadowmask=3|shadowresolve=4 shadowmask=3"`

Exact commands: `pred_drafts/RUNS104.md`. Order: `sh104` first (it carries the uninstrumented
`cpu_net` and the tax; if its probes crash, the session learns it before spending `mut104`), then
`mut104`. An entry hang is an ENTRY failure (`<tag>_entry1`, one further isolated attempt), never a
re-score. A run INVALID by §4 may be repeated **once** (`mut104b` / `sh104b`); a second INVALID run
of either makes Stage 1 **NOT EVALUABLE**, and the executor records a decision in `ROADMAP.md`
before any further action.

## 3. Population (session 101 `pred/01` §4, as carried by `dab102.py`)

Blocks of 90 flips from frame 1800; kept rows idx 60..88 (29) of each block; blocks with a kept
frame below 2100 rejected; pairs (2k, 2k+1) inside complete ABBA quartets only. Per block: the
arithmetic mean over its kept rows. Per pair: (arm 1) − (arm 0). **An arm's level** = the median over
its selected blocks of the block means. "d X" = mean over pairs of the per-pair difference, SE the
sample SD over √n. Expected ≈ 42 pairs from 300 s (`dab102a`: 42).

## 4. Admission — each run separately

### 4.1 Common (carried unchanged from `dab102.py` / session-102 `pred/03` §4 with `pred/05` §1)

Integrity: `PREREG_PINNED`, `BINARY_SEALED`, `IDENTITY` (installed exe = run binary = the sealed
one), `SCHEMA` (every field on every line), `FIELD_ORIGIN` (each field only on its line),
`RAW_CONTIGUITY`, `DURATION`, `GATEARM` (period 90, ABBA, frame = 1800 + 90·block, text exactly the
arm text), `ROW_ARMS`, `AB_BA_BALANCED`, `STREAMS_COMPLETE`, `NO_FLOOR` (`bf_*` = 0), `MARKERS_OFF`
(`gm_ops` = 0), `NO_RECORDING`. Protocol: env exactly as §2, schedule, gates text, one attempt,
hold ≥ 295 s, no exit inside the hold.
Controls: both arms' levels of `dt_us` ∈ [28 000, 40 000], `rec_n` ∈ [9 000, 13 000],
`gpu_busy_us` ∈ [10 000, 16 000]; work = mean `draws` of arm 1 over all retained rows ÷ that of arm
0 − 1, strict |work| < 0.5 %; `area_verdict` mirror (whole-arm split < 1.0 %, pair match ≥ 90 % at
0.5 %, work < 0.5 %) and the selected-row area split < 1 % / match ≥ 90 %; exactly one
`GpuClockPin: mode 1`; exactly two `RecordThread: started`; no `GPU checkpoints` line of any kind; no
`GpuHangAbort`; no fatal marker (`--- Error ---`, `--- Fatal Error ---`, `--- std::terminate ---`,
`--- abort() ---`, `ErrorDeviceLost`, `Unhandled exception:`, `GpuWaitSlow:`,
`AsyncPipelines: skipped draw`) in log or stdout; `KYTY_GPU_CHECKPOINTS` absent; **≥ 30 pairs**.

### 4.2 `mut104` arming

* `MW_DARK_ARM0`: arm-0 level of `mw_n` = 0 and its total over arm-0 kept rows ≤ 0.1 % of arm 1's;
* `MW_IDENTITY_ARM1`: arm-1 `mw_n` within ±2 % of `2·mh_n + mh_disp_n + bda_n` (session 83;
  `flr83b` reads −0.26 % with this scorer);
* `AMUT_ARMED`: `a_mut_us` > 0 and `a_mut_n` > 0 in both arms;
* `MUTSITE_HOLD_IDENTITY`: `mh_n` > 0 and `a_hold_n` within ±2 % of `mh_n + mh_disp_n`, both arms;
* `PLKSTAT_IDENTITIES`: `pl_prog_n` within ±2 % of `mh_n`, `pl_cs_n` within ±2 % of `dispatches`,
  `pl_prog_hold_us` > 0, both arms (session 83 §2.7);
* `PATHLAP_ARMED`: `pl_em_n` within ±2 % of `mh_draws`, `pl_pref_n` ≥ 1, and the emit chain closes:
  Σ`pl_em_*`/1000 ÷ `mh_emit_us` ∈ [0.95, 1.01], both arms (`pl96a`: 0.985);
* `OTHER_INSTRUMENTS_DARK`: `sh_jobs` and `da_wjobs` sum to 0 over all kept rows.

### 4.3 `sh104` arming

* `SH_DARK_ARM0`: arm-0 level of `sh_jobs` = 0 and its kept-row total ≤ 0.1 % of arm 1's;
* `SH_JOBS_PER_DRAW`: arm-1 `sh_jobs / draws` ∈ [0.90, 1.02];
* `SH_NO_DROP`: arm-1 `sh_drop / sh_jobs` ≤ 1 % (a full ring would under-measure the tax);
* `SH_FOUR_WORKERS`: log lines `ShadowResolve: worker 0..3 started`, exactly those four;
* `INSTRUMENTS_DARK`: `a_hold_us`, `a_mut_us`, `mw_n`, `pl_em_n`, `pl_proc_n`, `pl_prog_n`,
  `da_wjobs` sum to 0 over all kept rows of both arms — **the tax and `cpu_net` are measured with no
  instrument on**.

## 5. The readouts, and G

### 5.1 Terms (all µs a flip; `*_ns` counters ÷ 1000)

| term | definition | source |
|---|---|---|
| `cpu_net` | arm-0 level of `cpu_gpu_us − spin_gpu_us` | `sh104` (uninstrumented) |
| `S_lo` | arm-0 level of `a_mut_us` (reported) | `mut104` |
| `S_raw` | arm-1 level of `a_mut_us` | `mut104` |
| `P_mw`, 2SE | d `cpu_net_us` (arm 1 − arm 0) — the price of the four wide scopes | `mut104` |
| `T_in` | arm-1 level of `5·pl_em_n + 3·(pl_prog_n + pl_pipe_n + pl_cs_n) + a_mut_n` — instrument timestamps that land INSIDE `a_mut_us` (5 emit marks per draw inside the emit `MutScope`; 3 per `LockSplit`, all inside a wide scope in arm 1; one per outer `MutScope` interval) | `mut104` |
| `dI` | `C_TS · T_in / 1000` | |
| `E_rec`, `E_com` | arm-1 levels of `pl_em_rec_ns`, `pl_em_com_ns` ÷ 1000 | `mut104` |
| `spine` | arm-0 level of `da_walk_us − da_queue_us` (the PM4 walk minus M1 queueing; `dawalk=0`, so on GuestGpu) | `sh104` |
| `T4`, 2SE | d `cpu_net_us` (arm `shadowresolve=4` − arm 0) | `sh104` |
| `sh_push` | arm-1 level of `sh_push_us` (per-draw job hand-off, a probe artefact) | `sh104` |

### 5.2 Constants, fixed now

* **F = 0.30** — the ROADMAP rule's f at DCB granularity.
* **BAR = 3 000 µs.**
* **C_TS = 3.96 ns** per timestamp (`NowNs` + one `Add`): `pl96a`'s pathlap price 362.9 µs a flip
  ÷ its 91 663 GuestGpu timestamps a flip (7 × `pl_em_n` 5 018.0 + 2 × 28 268.3 spans:
  `pl_proc_n` 12.8, `pl_pref_n` 8.0, `pl_eop_n` 369.1, `pl_bar_n` 1 123.2, `pl_sub_n` 539.9,
  `pl_gc_n` 8.0, `pl_cmd_n` 26 207.3; `pl_look` is on the guest thread and excluded). [I],
  cross-binary.
* **W_E = 1 115.575 µs** — `CommitBindings` write-list 675.455 + emit 440.120 a flip, session 101
  `cm101d` (gate `cbmove`, corrected regime). [M], **cross-run and cross-binary, flagged.**

### 5.3 G, central and ceiling

    S_now   = S_raw − max(P_mw, 0) − dI                       S_now^  = S_raw − max(P_mw + 2SE, 0) − 2·dI
    E_move  = E_rec + W_E                                     E_move^ = E_rec + E_com
    S_ctx   = S_now − E_move                                  S_ctx^  = S_now^ − E_move^
    T4c     = T4                                              T4^     = max(0, T4 − 2SE − sh_push)
    G       = cpu_net − [S_ctx + F·(cpu_net − S_ctx)] − spine − T4c
    G^      = cpu_net − [S_ctx^ + F·(cpu_net − S_ctx^)] − spine − T4^

`S_now` is session 83's `S_hi` (`S_raw − P`) further cleared of this run's own timestamps inside
the scopes. **G^ is the ceiling: every uncertain term at the end that favours route A** (the
instrument price at its upper end and doubled, the whole of `CommitBindings` moved into the
contexts, the tax less its SE and less the per-draw hand-off no DCB-granularity design would pay).

### 5.4 Reported beside G, deciding nothing

`G` with F = 0.39 (the upper end of `f_max`); `G_wall` = G − max(0, d`dt_us` − d`cpu_net_us`) of
`sh104` (a tax that makes GuestGpu wait rather than spin shows on the wall, not on thread CPU);
`G` with the spine read as `pl_pref_ns/1000 − da_queue_us` of `mut104` arm 0 (the whole
`PrefetchComputePipelines`); `H/M` = `pl_prog_hold_us / mh_prog_us` (session 83: 0.689); the
cross-run instrument price = `mut104` arm-0 `cpu_net` − `sh104` arm-0 `cpu_net`; the T4 at which
the central G would reach the bar; `S_raw` beside session 83's 20 973 (inter-run, a sanity check).

## 6. THE RULE

**Applied to G (central), as `ROADMAP.md` §0.1 item 6 records the rule; G^ (the ceiling) is reported
beside it and decides nothing:**

| reading | decision, taken without further argument |
|---|---|
| **G < 3 000 µs** | **Route A is CLOSED for maximum FPS** (in addition to its s83 closure for 60 FPS). Only Stage 2 (`dawalk`, `pred/03`) survives. Recorded in `ROADMAP.md`. |
| **G ≥ 3 000 µs** | **Route A proceeds by stages** (`review.md` §3), each stage with its own seal; Stage 3 starts only after Stage 2 is scored. |

**Not evaluable** (no decision; recorded as such) if either run is not ADMITTED, or if the two runs'
arm-0 render areas (Σ`rt_kpx`/Σ`rt_att` over kept rows) differ by more than **3 %** — `cpu_net` and
`S` would then come from different DRS rungs.

## 7. Predictions (scored by `a104.py`, no decision weight)

| # | prediction | band |
|---|---|---|
| A1 | `mw_n` arm-0 level exactly 0 | exact |
| A2 | `mw_n` arm 1 vs `2·mh_n + mh_disp_n + bda_n` | ±2 % |
| A3 | `S_lo` | [11 500, 14 500] |
| A4 | `S_raw` | [18 500, 21 500] (`flr83b` 20 968 with this scorer) |
| A5 | `P_mw` | [0, +400] (`flr83b` +244.5 ± 176 on this population) |
| A6 | `H/M` | ≥ 0.60 |
| A7 | `E_rec` / `E_com` | [1 000, 1 500] / [1 800, 2 700] (`pl96a` 1 221 / 2 265) |
| A8 | `spine` | [900, 1 300] (`dab102a` 1 086, `reg104` ≈ 1 088) |
| A9 | `cpu_net` | [29 800, 31 600] (`dab102a` 30 668) |
| A10 | `T4` / `sh_push` / `sh_us` | [+700, +2 600] / [250, 700] / [2 500, 6 500] (s64 Sky Garden: +4.2…+6.5 % CPU/draw, 470–500, 4 030–4 180) |
| A11 | G central in [4 000, 8 000] / **G ≥ 3 000 (A proceeds) — the discriminating prediction** | [4 000, 8 000] / one-sided |
| A12 | cross-run instrument price | [+500, +2 500] |

**What the record already implies (inter-run, [I]):** with `S_raw` 20 968 and `P_mw` 244.5 (`flr83b`),
`T_in` ≈ 126 900, `E_rec`/`E_com` 1 221/2 265 (`pl96a`), `cpu_net` 30 668 and `spine` 1 086
(`dab102a`) and T4 = 1 300…2 000 (s64): **G ≈ 5 900…6 600 µs, G^ ≈ 7 800…8 500 µs.** The central G
reaches the bar only if **T4 ≳ 4 900 µs (≈ 16 % of `cpu_net`, three times session 64's tax)**; the
ceiling only if T4 ≳ 6 800 µs. **This rule is therefore unlikely to close route A; its realistic
kill path is a tax far above session 64's.**

## 8. Must not be claimed

A speedup (Stage 1 changes nothing that ships) · that route A will reach G (G is a ceiling of a
model, not a measurement of a design) · that f = 0.30 was measured (it is the rule's constant; no
Stage-1 counter measures f) · that the read-only probes reproduce the contention of contexts that
WRITE the caches (they do not; the direction is unfavourable to A and unmeasured) · that `S_ctx` is
the floor A would meet (it removes only record and `CommitBindings`; `Transit`, `AcquireRenderTargets`,
VB/IB uploads, pipeline creation stay serial by assumption) · a frame-rate figure · 60 FPS.

## 9. Known limits, stated before the runs

* `W_E` and `C_TS` are borrowed from sessions 101 and 96 (other binaries). The ceiling does not use
  `W_E`; `C_TS` enters both ends (doubled at the ceiling).
* The formula charges the spine in full AND leaves the walk inside `cpu_net − S_ctx`, whose F-share
  is kept: ≈ 0.3 × `spine` ≈ 0.33 ms of double count, **against** route A, in both G and G^. The rule
  is applied as recorded in `ROADMAP.md`; the amount is printed.
* `cpu_net` (from `sh104`) and `S` (from `mut104`) are levels from two runs; the area control of
  §6 is the only guard against a DRS difference.
* `T4` is measured on GuestGpu thread CPU; a wait component appears only in `G_wall` (§5.4).

---

## Provenance at sealing time (fill when sealing)

* Binary `16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352` (installed; built session 103).
* `gates_base.txt` `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`.
* Scorer `a104.py` sha256 `<fill>`; tests `test_a104.py` `<fill>` (51 synthetic + 14 real checks pass).
* Sealed at `<fill>`.
