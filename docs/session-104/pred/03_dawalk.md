# Sealed pre-registration 03 — session 104, route A Stage 2: gate `dawalk` (the PM4 look-ahead walk off the GuestGpu thread)


**Immutable once written.** A correction goes into a new sealed addendum.

---

## 0. The candidate

`ROADMAP.md` §0.1, session-104 decisions, item 7 (recorded before this text): gate `dawalk=0|1` at
`dawalklead=1`, a candidate to ship **without code**; default 1 only by a sealed ABBA with the pin.
Gate `dawalk` (`KYTY_DRAW_AHEAD_WALK`, default 0, since session 59): at `GuestGpu::Enqueue`
(`LookaheadSubmission`, `graphicsRun.cpp:1771-1796`, on the guest's submit thread) each submission
is posted to one `DrawAheadWalk` thread which runs the same `WalkComputeDispatches` (compute prefetch
+ the M1 draw look-ahead, shadow state carried per queue) and the GuestGpu thread then skips its own
walk in `PrefetchComputePipelines` (`graphicsRun.cpp:1798-1826`, counter `da_wskip`). Knob
`dawalklead` (default 1): a graphics job waits until GuestGpu is at most that many submissions
behind (`graphicsRun.cpp:1503-1522`); jobs more than 24 enqueues behind, or already started by
GuestGpu, are dropped unwalked (`da_wdrop`). M1 results stay witness-checked; the compute prefetch
only compiles. `gates_base.txt` pins `dawalk=0 dawalklead=1`; both are named in both arms, so the
schedule owns them.

**What is known.** The GuestGpu-side walk costs `da_walk_us` ≈ 1 833–1 870 µs a flip inside
`PrefetchComputePipelines` ≈ 1 961 µs (`pl96a`, `dab102a`, `reg104`) — the ceiling of the saving.
Session 60 (no ABBA, no pin, `log_sky60.txt`) moved it and paid for it: at lead 1 `da_take_us`
+≈ 500, `da_miss` 150 → 300, `da_late` 0 → 8, the walker's own walk +33 %; net −0.3…−1.4 % CPU a draw
at a ±1.4 % resolution. **Never measured under ABBA and pin.**

## 1. Why one 600-s run and not a pilot plus a decision run

Session 102 needed two runs because the pilot measured a different contrast (`dabatch=8`, to expose
the per-call cost) from the one that would ship (`1024`). Here the contrast that would ship is the
only one of interest, so a "pilot" would be an early look at the same data — optional stopping. One
run of 600 s gives ≈ 95 pairs (`dab102a`: 42 from 300 s), and with `dab102a`'s per-pair SD of
`cpu_net_us`, 530 µs, a 2·SE ≈ 109 µs — enough to resolve the −150 µs bar, whose own clause
dominates the 2·SE clause at that width. One entry instead of two also halves the exposure to the
6.67 % entry-hang rate.

## 2. The run

`dwk104`: Sky Garden, `--hold 600`, `--attempts 1`, `--no-install`, `gates_base.txt`,
`KYTY_GATE_SCHEDULE="90+1800:dawalk=0 dawalklead=1|dawalk=1 dawalklead=1"`,
`KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` positional; **`KYTY_GPU_CHECKPOINTS`
and `KYTY_REC` absent**; no measurement instrument (`amut`, `mutsite`, `pathlap`, `plkstat`,
`mutwide`, `shadowresolve` all at their base values) — the ship decision is taken on the
configuration that would ship. Exact command: `pred_drafts/RUNS104.md`.

Population as session 101 `pred/01` §4 (`dab102.py`): blocks of 90 from frame 1800, kept rows idx
60..88, blocks with a kept frame below 2100 rejected, pairs (2k, 2k+1) inside complete ABBA quartets,
per block the mean over kept rows, per pair (arm `dawalk=1`) − (arm `dawalk=0`), an arm's level the
median of its block means. A measurement needs **≥ 60 pairs**. An entry hang is an ENTRY failure
(`dwk104_entry1`, one further isolated attempt). A run INVALID by §3/§4 may be repeated once
(`dwk104b`); a second INVALID run keeps the default 0 and is recorded.

## 3. Admission (carried from `dab102.py` / session-102 `pred/03` §4 with `pred/05` §1)

Integrity: `PREREG_PINNED`, `BINARY_SEALED` (`16ef56b6…`), `IDENTITY`, `SCHEMA`, `FIELD_ORIGIN`,
`RAW_CONTIGUITY`, `DURATION`, `GATEARM` (exact arm texts), `ROW_ARMS`, `AB_BA_BALANCED`,
`STREAMS_COMPLETE`, `NO_FLOOR`, `MARKERS_OFF`, `NO_RECORDING`; protocol (env, schedule, gates text,
one attempt, hold ≥ 595 s, no exit inside the hold).
Controls: arm levels of `dt_us` ∈ [28 000, 40 000], `rec_n` ∈ [9 000, 13 000], `gpu_busy_us` ∈
[10 000, 16 000]; work split strict |work| < 0.5 % (mean `draws` over all retained rows); area mirror
(split < 1.0 %, pair match ≥ 90 %, work < 0.5 %) and selected-row split < 1 % / match ≥ 90 %; one
`GpuClockPin: mode 1`; two `RecordThread: started`; no `GPU checkpoints` line of any kind; no
`GpuHangAbort`; no fatal marker in log or stdout; `KYTY_GPU_CHECKPOINTS` absent; ≥ 60 pairs.

## 4. Arming — by counters inside the run (all live in lite: `FS::Enabled()` or unconditional `Add`)

* `WALK_DARK_ARM0`: `da_wjobs`, `da_wskip`, `da_wdrop` sum to exactly 0 over arm-0 kept rows.
* `WALK_ARMED_ARM1`: arm-1 levels of `da_wjobs` ≥ 1 and `da_wskip` ≥ 1.
* `WALK_IDENTITY_ARM1`: over arm-1 kept rows, |Σ`da_wskip` / Σ(`da_wjobs` + `da_wdrop`) − 1| ≤ 1 % —
  every posted submission is either walked or dropped by the walker, and skipped by GuestGpu.
  **Verified on a real dawalk=1 log before sealing:** `log_sky60.txt` phase `lead1` 3 524 skips
  against 3 521 posts (+0.09 %), phase `both` 3 516 against 3 520 (−0.11 %); the `dawalk=0` phases
  read exactly 0.
* `WALK_DROPS`: Σ`da_wdrop` ≤ 5 % of posts (a dropped job is a submission nobody walked: no M1
  requests and no compute prefetch for it — above 5 % arm 1 is "walk partly removed", not "walk
  moved").
* `WALKS_SAME`: arm-1 level of `da_walks` within ±5 % of arm 0's (the same submissions walked).
* `INSTRUMENTS_DARK`: `mw_n`, `a_hold_us`, `a_mut_us`, `pl_em_n`, `pl_proc_n`, `sh_jobs` sum to 0.

`pl_pref_ns` → ~0 in arm 1 (`review.md` §3) would need `pathlap=1 mutsite=1` in both arms, i.e. an
instrument on the ship run; the identity above proves the same thing (every GuestGpu walk was
skipped) without one, and is used instead.

## 5. THE SHIP RULE

Endpoint `cpu_net_us` = `cpu_gpu_us` − `spin_gpu_us` (**`spin_gpu_us` from `FrameTrace-draw`**),
paired over ABBA blocks. **Ship `dawalk=1` as the new default only if ALL hold:**

* **S1** mean d`cpu_net_us` ≤ **−150 µs**;
* **S2** mean d`cpu_net_us` + 2·SE < 0 (2·SE excludes 0);
* **S3** mean d`dt_us` < 0 (the same sign — the mean frame follows GuestGpu work, §0.1 item 1);
* **S4** the run is ADMITTED (§3, §4);
* **S5** a video pass `vwk104` on the installed binary with `dawalk=1` in its gate text (not a
  schedule), `KYTY_REC` set, one ok attempt, **≥ 3 000 frames and 0 one-frame glitches** in
  `s51_vidglitch.py`'s report.

S1–S4 true and no video report yet ⇒ **SHIP_PENDING_VIDEO**: nothing ships until S5 is read.
Otherwise the default stays 0. **A shipped default is a new build** (`gates.cpp` default 0 → 1,
`gen_gates.py` regenerates `gates_base.txt`): the ROADMAP §6 video pass of that build is then owed
and taken before the session's final commit, or recorded as the next session's first debt.

**Reported, deciding nothing:** d`da_take_us`, d`da_miss`, d`da_late`, d`da_hit`, d`da_stale`,
d`da_queue_us`, d`gpu_busy_us`, d`draws`; d`da_walk_us` (in arm 1 this is the WALKER's walk — off
GuestGpu — and says nothing about the saving); `da_wlag_us` and `da_wdepth` of arm 1.

## 6. Predictions (scored by `dwk104.py`, no decision weight)

| # | prediction | band |
|---|---|---|
| D1 | arm-1 `da_wskip` level (≈ submissions a flip; `pl_pref_n` = 8.0) | [7, 9] |
| D2 | skip/posts identity | ±1 % |
| D3 | d`cpu_net_us` | [−700, +100] µs (point −250: s60 −0.3…−1.4 % of ≈ 30.5 ms, against a 1.96 ms walk minus cooling) |
| D4 | d`da_take_us` | [0, +800] |
| D5 | d`da_miss` | [+20, +250] |
| D6 | d`da_late` | [0, +12] |
| D7 | d`da_walk_us` (the walker slower than GuestGpu's own walk) | [+200, +1 000] |
| D8 | **d`cpu_net_us` ≤ −150 (the bar is met) — discriminating, low confidence (≈ 50 %)** | one-sided |

## 7. Must not be claimed

A frame-rate figure · 60 FPS · that the walk is gone from the machine (it moved to another thread on
the same CCD — `dapin`) · any saving read from the arm-1 `da_walk_us` · that route A is licensed or
advanced by this run beyond its Stage 2 · anything from an inter-run comparison.

---

## Provenance at sealing time (fill when sealing)

* Binary `16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352`; `gates_base.txt`
  `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`.
* Scorer `dwk104.py` `<fill>`; tests `test_dwk104.py` `<fill>` (32 synthetic + 8 real checks pass).
* Sealed at `<fill>`.
