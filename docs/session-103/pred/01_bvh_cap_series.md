# Session 103, sealed before any run: acceptance of the BVH loop cap (`KYTY_BVH_LOOP_CAP`)

Decision recorded first in `docs/ROADMAP.md` §0.1 (commit `27b492d`, "РЕШЕНИЯ ИСПОЛНИТЕЛЯ НА СЕССИЮ 103",
items 1–2). This text fixes the protocol and the verdict before the first launch of the new binary.
It is immutable; a correction goes into a new sealed addendum.

## 1. What is tested

The default binary of session 103: `KYTY_BVH_LOOP_CAP` ON, budget 65 536 loop-header executions per
invocation, one shared budget per invocation, set `{380bb9d636390bae}`. A trip counts `bl_trip` in the
fault-buffer tail and returns through the normal return path; a normal return that spent more than
1/16 of the budget counts `bl_near`. Offline facts, known before this seal: the three permutations of
`380bb9d6` validate (`spirv-val --target-env vulkan1.3 --uniform-buffer-standard-layout`), registers
128 → 128, local memory 80 → 64 B; with `KYTY_BVH_LOOP_CAP=0` the recompiler reproduces the stored
modules byte for byte; every other recompilable cached module (106 CS, 173 PS) is byte-identical to
the session-102 cache (VS are not recompilable offline and are not covered).

## 2. Protocol

* Binary: the build installed by the warm-up; its sha256 is recorded by every run (`binary_sha256`).
  No rebuild from the warm-up to the end of the series.
* **Warm-up (not counted):** `ent103_warm` — the first run after the build is cold (every shader is
  translated again, `pipelines.bin` is rebuilt). If it fails, one more warm-up `ent103_warm2`; still
  not counted.
* **Counted entries:** `ent103_01` … `ent103_67`, each
  `python C:/kyty/s103/enter_scene.py <tag> --attempts 1 --hold 20` (Sky Garden,
  `-lvl underwater_aerial_garden`, stable = the default 90 frames with draws ≥ 3000, timeout 240 s),
  no extra `KYTY_*` variable, the GPU otherwise idle. One entry at a time, in order.
* **Technical failures:** a counted entry that ends without any hang/device-loss/abort marker and
  without reaching the scene (e.g. the start-up crash `commandRecorder.cpp:326`, a launcher error)
  is a technical failure: it is reported, and replaced by one more entry appended at the end
  (`ent103_68`, …), at most 3 replacements. A hang, device loss, `Unhandled exception`, `std::terminate`
  or `abort()` is never technical.
* **Stopping:** the series stops at the second entry with a hang/device loss (the verdict is then
  already NOT ACCEPTED); after the first it continues.

## 3. Per entry (scorer `bvh103.py`, from `log_<tag>.txt` and `<tag>.json`)

* `armed`: the log has `BvhLoopCap: cap=65536 token=''`.
* `outcome`: `<tag>.json` attempt outcome, `hold_exit`.
* `hang`: any line matching `run_safety99.failure_marker` (GpuHangAbort, GpuWaitSlow, GpuMarkerHung,
  ErrorDeviceLost, std::terminate, abort(), fatal, Unhandled exception). `GpuWaitSlow` alone is
  reported as `slow` and is a hang only together with `GpuHangAbort`/device loss.
* `bl_trip`, `bl_near`: sums of the `FrameTrace-x` counters over the whole log, cross-checked against
  the last `BvhLoopCapTrip:` line (`total=`, `near_total=`); the larger of the two is used.
* `max_dt_us`: the largest `FrameTrace: dt_us` of the run.

## 4. Verdict — ACCEPTED only if every item holds

* **A1 armed** — every counted entry is armed.
* **A2 no hang** — 0 counted entries with a hang or device loss; every counted entry reached the
  scene (`outcome == ok`) and survived the 20 s hold (`hold_exit` null), after replacements.
* **A3 margin** — `bl_near == 0` in every counted entry (the largest legitimate walk × 16 ≤ the cap).
* **A4 not systematic** — at most 15 of the 67 counted entries have `bl_trip > 0` (the historical
  entry-hang rate is 6.67 %; systematic trips would mean the cap cuts legitimate work).
* **A5 worst frame** — the largest `max_dt_us` of the counted entries is below 30 000 000 µs
  (half the 60 s TDR).

Otherwise NOT ACCEPTED, with the failing items named. P(0 hangs in 67 | p = 6.67 %) = 0.0098: an
ACCEPTED series says the entry-hang rate with the cap is below 6.67 % at ~99 % confidence; it does
NOT prove the rate is 0, and it does not name the mechanism of the historical hang (trips prove only
that the budget ran out).

## 5. Video pass (ROADMAP §6 debt, owed because the cap reaches the renderer)

`vid103`: `enter_scene.py vid103 --attempts 1 --hold 120 --rec`, then
`python C:/kyty/scripts/s51_vidglitch.py <rec.mp4> 4 6 <dir>`. PASS: ≥ 3 000 frames, the file decodes
without errors, and 0 single-frame glitches flagged; flagged frames are inspected by eye and reported.

## 6. Predictions (published whether they hit or miss)

* Q1: the series is ACCEPTED.
* Q2: between 0 and 10 counted entries show `bl_trip > 0`.
* Q3: no counted entry shows `bl_near > 0`.

## 7. Must not be claimed

A speedup or a frame-rate change; that the entry hang is proved gone (only bounded); that the
trips are the historical hang (the counter shows a budget ran out, not why); anything about the
other 12 BVH programs (uncapped).
