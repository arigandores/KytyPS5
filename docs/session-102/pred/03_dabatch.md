# Sealed pre-registration 03 — session 102, candidate code 3: knob `dabatch` (draw-lookahead requests per `QueueDrawAhead` call)

**Immutable once written.** Written after the build and **before** any run of the binary that
carries the knob. A correction goes into a new sealed addendum.

---

## 0. The candidate, and what reading already changed about it

`docs/next-session-102.md` §2 item 3 names it: *"`PrefetchComputePipelines` batch knob. 41.9 % of the
1 836.9 µs walk is queueing under `PipelineCache::m_mutex`, 125 mutex acquisitions a flip at the
shipped 64-request batch. Three lines in `graphicsRun.cpp:1403` with its own controls (`da_hit`,
`da_miss`, `da_late`)."*

Reading (session 102, `graphicsRun.cpp:1201-1427`, `pipelineCache.cpp:2386-2591`, `:4478-4490`)
corrects the premise before any number:

* The batch is the **M1 draw-lookahead request batch** of `WalkComputeDispatches`, not a
  compute-prefetch batch; `PrefetchComputePipelines` is only its GuestGpu entry.
* **`m_mutex` is effectively uncontended during the walk** — every other taker is on the same
  thread or rare. `da_queue_us` (807.9 µs a flip in `cm101d`, corrected regime) is **work done under
  the lock** — ≈ 95 ns a request over ≈ 8 479 requests — **not waiting**. The session-100 figures
  (769.1 of 1 836.9) come from `mov100b_entry1`, which ran in the defective checkpoint regime.
* A bigger batch removes only a **per-call fixed cost `b`** (lock, `DrawAheadCurrentL3`, ring push,
  notify, ~17 `FrameStats::Add`) times the number of calls saved. **`b` has never been measured.**
  The reading estimate [I] is 0.1–1 µs, i.e. **12–124 µs a flip** at batch 1024 — at or below the
  2·SE of the endpoint (≈ 82 µs in `cm101d`).

So the first question is `b`, and it is cheap to measure precisely: a SMALLER batch multiplies the
calls by ≈ 8 and makes `b` visible in `da_queue_us` at a 2·SE of ≈ 4 µs.

## 1. The patch (built before this seal)

Knob `dabatch` (`KYTY_DRAW_AHEAD_BATCH`, **default 64 = the literal it replaces**, limit 65536,
0 = one call per walk), read **once per walk**; `requests` became a `thread_local` vector cleared per
walk (identical semantics at every value; it removes the per-walk regrowth that would otherwise
confound a large batch). Counter **`da_qcall`** (FrameTrace-draw) counts `QueueDrawAhead` calls — the
arming proof. **At the default the shipped behaviour is unchanged.**

## 2. Run 1 — the pilot `dab102a` (measures `b`)

* `python C:/kyty/s102/enter_scene.py dab102a --hold 300 --attempts 1 --no-install --gates-file
  C:/kyty/s102/gates_base.txt --pred C:/kyty/s102/pred/03_dabatch.md
  KYTY_GATE_SCHEDULE="90+1800:dabatch=64|dabatch=8" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1
  KYTY_GPU_MARKERS=0` — `KYTY_GPU_CHECKPOINTS` and `KYTY_REC` absent entirely.
* Population, unchanged from session 101 `pred/01` §4: blocks of 90 from frame 1800, rows 60..88 of
  each block (29), blocks with a kept frame below 2100 rejected, pairs (2k, 2k+1) inside complete
  ABBA quartets only, a pilot needs **≥ 10 pairs**. Per block: arithmetic means over its kept rows;
  per pair: the difference (arm `dabatch=8`) − (arm `dabatch=64`).
* **`b̂` = mean over pairs of Δ`da_queue_us` ÷ mean over pairs of Δ`da_qcall`**, with a 90 %
  percentile bootstrap over pairs (20 000 resamples, seed 102).
* **Predicted saving at 1024:** `Ŝ = b̂ × (Q64 − Q1024)`, where `Q64` is the median `da_qcall` of the
  64 arm and `Q1024 = W + R/1024` with `W` the median `da_walks` and `R` = median(`da_req` +
  `da_nohint`) of the 64 arm (each walk makes at least one call).
* **Decision after the pilot** (the programme's usefulness threshold of session 92 is 60 µs a flip):
  * upper 90 % bound of `Ŝ` below **60 µs** ⇒ **candidate CLOSED — not shipped, no second run**;
  * otherwise ⇒ run 2.
* Mechanism check (reported): Δ`da_walk_us` ≈ Δ`da_queue_us` (the extra calls cost the walk what they
  cost the queue); if Δ`da_walk_us` > 2 × Δ`da_queue_us`, the call cost is partly outside the timed
  region and `b̂` is a LOWER bound — stated, not repaired.

## 3. Run 2 — the decision `dab102b` (only if §2 says so)

* Same launch, `--hold 900`, schedule `"90+1800:dabatch=64|dabatch=1024"`, tag `dab102b`, a
  measurement needs **≥ 30 pairs**.
* **Ship `dabatch` = 1024 as the new default** only if ALL hold:
  1. endpoint `cpu_net_us` = `cpu_gpu_us − spin_gpu_us` (per-pair Δ, arm 1024 − arm 64): mean < 0
     with **t ≤ −2.0**;
  2. `da_walk_us`: mean Δ < 0 with t ≤ −2.0;
  3. safety, each within its own pre-registered band: |Δ`da_late`| ≤ 0.10 a flip; Δ`da_hit` ≥ −1 % of
     the 64 arm's `da_hit`; Δ`da_miss` ≤ +1 % of `da_hit` of the 64 arm; `da_busy` does not rise by
     more than 5 a flip;
  4. every control of §4.
  Otherwise the default stays 64 and the knob stays as a measurement knob.
* **A shipped default is a new build**: the video pass (≥ 3 000 frames, `s20_vidglitch.py`) of the
  shipped build is then owed (ROADMAP §6) and is taken before the session's final commit if time
  allows, else recorded as the next session's first debt.

## 4. Controls — both runs, every limit fixed here

The brief's lesson (two sessions admitted a run that was 50 % off): each arm's median must lie in
* `dt_us` **[28 000, 40 000]**, `rec_n` **[9 000, 13 000]**, `gpu_busy_us` **[10 000, 16 000]**;
and the run must show:
* **work split** |median `draws` 8/1024 arm ÷ 64 arm − 1| ≤ 0.5 %; area split (`area_verdict.py`)
  valid as in session 101;
* **arming**: median `da_qcall` of the non-default arm ÷ that of the 64 arm within ±25 % of
  `(W + R/B)/Q64` for B = 8 or 1024;
* exactly one `GpuClockPin: mode 1`, two `RecordThread: started`, no `GPU checkpoints` line, no
  `GpuHangAbort`, no fatal marker;
* `KYTY_GPU_CHECKPOINTS` absent from the run's `env`.
Any control failing ⇒ the run is INVALID and nothing is shipped from it. An entry hang is an ENTRY
failure (`<tag>_entry1`), one further isolated attempt, never a re-score.

## 5. Predictions (no decision weight)

* **Q1.** `b̂` in **[0.05, 1.5] µs**.
* **Q2.** Ŝ upper bound < 60 µs ⇒ the candidate closes after the pilot.
* **Q3.** Δ`da_late` (8 − 64) within ±0.05 a flip.

## 6. Must not be claimed

A speedup from the pilot (its non-default arm is slower by design) · that `m_mutex` contention was
measured (it was read to be negligible, not measured) · a frame-rate gain · 60 FPS.

---

## Provenance at sealing time

* Emulator binary built this session, NOT yet installed or run: `346ba4f6448c35cba8677101a1599c6ddd0b907d3ea76015ada692cd3b3dc776` (source HEAD `0d35faa` + uncommitted session-102 changes; translator hash `2db9065aef8b54a24a7d29b3584df9647f61dd95` unchanged).
* `shader_cfg_tests.exe` `cfe15c6cf5ce14ed2988d4da4d7e6590c65f2b319b751d1937ccd71b825a73a5`.
* Sealed at 2026-09-22T22:12:14.
