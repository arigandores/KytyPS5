<!-- Mirror of C:/kyty/s122/FACTS.md (source of truth), personal identifiers and foreign application names removed by ps5 em audit122/mirror_facts122.py. -->
# Session 122 — the bottleneck map through the knob `burn`: sealed burn ABBAs on five scenes (map complete by scene, partial by thread — code 1 and the placebo); reference scene NOT_RESOLVED; audited (recount CONFIRMED, 3 MAJOR / 5 MINOR)

> **Header updated by the Session Auditor (HPP-8, 2026-09-27).** The previous title — "PAUSED by the user: … not yet smoke-tested; no sealed run; the vblank staircase found; the frame-skip plan recorded" — and the paragraph "Numbers" below describe the pause of 2026-09-26 and are kept as history; the session resumed (sections 4–8, Step 4, Audit). **The "vblank staircase" inference of §1.3 is refuted by `sky122` (Audit, MAJOR-2).**

**Single source of truth for session 122 (paused).** Mirrored into git as `docs/local-session-122.md`. Harness root
`C:/kyty/s122`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–5.

**Numbers:** installed build `d3a981a2…` (git `7c73f26`) — unchanged; the `burn` build is committed as WIP and not
installed. Sky Garden ≈ 51–52 % game speed. 60 FPS is not promised.

## 1. What was done

1. **Order (item 1):** the scene map through causal probes — a per-thread calibrated CPU burn, a two-dose ABBA per scene.
2. **Design (item 2):** designer + adversarial reviewer (ACCEPT WITH REQUIRED CHANGES, RC1–RC13) → `design122.md`. Knob
   `burn` = thread code × 100 000 + dose µs (1 GuestGpu before `Process`; 2/3 record thread / all M1 workers, spread;
   4 main guest thread at the return of `KernelWaitEqueue`; 5/6 controls; 7 fallback at `GuestGpu::Submit` before its
   mutex; 8 placebo). Scenes from `data/prein/product_levels.xml`: Sky Garden, `intro_next`, `penguin_atlantis`,
   `time_stopper_ghost_world`, `rotating_level_day_and_night` (+ fallbacks). Reading rule: slope of mean `dt` over the
   dose — critical / not critical / superlinear / unresolved / GPU-bound, with the vblank steps reported.
3. **The vblank staircase (the lead's finding, item 2):** in `shp121` 93.4 % of Sky Garden frames take exactly 2 vblanks
   (33.3 ms; median `dt` 33 300 µs); the game steps a fixed 1/60 s per frame, so savings below the distance to the next
   vblank step do not change `dt` — why small GuestGpu wins have not shown in FPS. **Plan:** session 123 — frame skipping
   (execute each frame's command stream for everything the guest reads back, skip the draw translation of every other
   frame; game speed toward ~100 % at ~30 shown FPS), if the map shows GuestGpu critical; a flip-pacing knob as the
   second lever; frame generation (Lossless Scaling, driver-level) as a user-side check afterwards.
4. **Code (items 3–4):** implementation agent, adversarial code reviewer (PASS_WITH_FIXES), fixer. 32 `burn_*`
   counters; the spin `BurnSpinUntil` (`rdtsc` + `pause`, calibrated on `NowNs`'s constant; offline against QPC: blocks
   +0.02…+0.08 %, spread dose counted exactly 2 000.0 µs). The implementation's own decisions were written as item 3 by
   the fixer agent in the lead's name and accepted explicitly in item 4. Build from the working tree `cc6f256b…`
   (not installed, not run).
5. **Paused (item 5)** at the user's instruction ("finish the current run, update all docs, push and stop").

## 2. Code

WIP commit (see git): `frameStats.h/.cpp` (spin, hooks, counters), `gates.h/.cpp` (`Knob::Burn`, LAST),
`graphicsRun.cpp` (codes 1, 7), `commandRecorder.cpp` (2, 5), `pipelineCache.cpp` (3, 6), `eventQueue.cpp` (4),
`videoOut.cpp` (key publication, counters). Default 0: behaviour unchanged. NOT smoke-tested.

## 3. Resume

`docs/next-session-122.md` §«Возобновление»: build from the WIP commit, pin, the burn smoke on Sky Garden (6 arms), the
entry smokes of the new levels, the scorer with fixtures and mutants, the seal, the sealed ABBAs per scene; chain
`C:/kyty/s122/go122a.sh` (build sha placeholders to fill).

## 4. Resumed: step 2 (the smokes) — harness ready, runs gated by the machine (Harness Engineer, 2026-09-26)

Build `2baf8742…` (git `25f3886`, `src/` identical to the WIP `41effbd`) is pinned in `go122a.sh` and accepted by the
lead for the smoke. Prepared for step 2:

* **`go122a.sh bsky122`** — the UNSEALED six-arm burn smoke of ROADMAP item 7: `KYTY_GATE_SCHEDULE=300+1800:burn=0|
  burn=102000|burn=402000|burn=802000|burn=202000|burn=302000`, no ABBA (the emulator ignores ABBA above two arms
  anyway), 200-s hold, video, `--stable-draws 300`. The schedule wraps back to `burn=0` by itself, which is the
  placebo-noise check the item asks for. Matched BEFORE the `e*)` branch, so it cannot fall into the sealed default.
* **`smoke122.py`** — the smoke reader: blocks built from the `GateArm:` lines only (never from `blk=`, trap of s. 120),
  the first 10 and last 5 frames of every block dropped (the arm switch lands on the last position of the outgoing
  block); prints arming (`burn_{g,r,m,t,p}_ns/_n/_q/_seen`), coverage (`burn_m0_seen`, `burn_s_seen`, `burn_s_main`),
  `cpu/wall` per group, `burn_late`, `burn_cpu_bad`, the scene columns, the vblank histogram of `dt` and the failure
  markers. Exercised offline on `C:/kyty/s121/log_shp121.txt` (89 blocks parsed, the old build reads all `burn_*` as
  absent, as it must).

**Environment traps found before the first run (both cost a refused chain, nothing measured):**

1. **`BASH_ENV` of the agent shell exports a Windows-style `PATH`** (`C:\…;C:\…`), which bash cannot split: inside any
   `bash <script>` every POSIX tool and `python` is "command not found", and `go122a.sh` then reports "a process stays
   busy" because `procload.py` never ran. Launch the chain as
   `export PATH="/usr/bin:/bin:…"; env -u BASH_ENV PATH="$PATH" bash /c/kyty/s122/go122a.sh <tag>`.
2. **~~NVML is down on this machine~~ — WRONG, WITHDRAWN 2026-09-26 20:31. `%ProgramFiles%` is missing from the agent
   shell's environment, and `nvml.dll` then fails to initialise.** Every `nvidia-smi` (System32 and all three
   driver-store copies) answered "Failed to initialize NVML: Unknown Error" here while Vulkan worked, and I read that as
   a driver that had not been rebooted into. The user's screenshot (20:30:09, the same machine) showed `nvidia-smi`
   answering normally in their own shell, which killed that reading. Bisected: same user `…/<user>`, session 1, window
   station `WinSta0\Default`, medium integrity, same binary; the sandbox is irrelevant (same failure with it off);
   `Start-Process -UseNewEnvironment` succeeds at once. The agent environment simply has no `ProgramFiles` (nor
   `ProgramData`, `LOCALAPPDATA`, `APPDATA`, `PROCESSOR_ARCHITECTURE`, `COMPUTERNAME`, …), and restoring **`ProgramFiles`
   alone** makes NVML initialise. Fix, in `go122a.sh` (`patch_go122a_pf.py`, LF, `bash -n` clean): the chain exports
   `ProgramFiles` (plus `ProgramData`, `LOCALAPPDATA`, `APPDATA`) before its first `nvidia-smi` and before every python
   child, so the clock logger inside `enter_scene.py` inherits it; the substitution of `patch_go122a_nvml.py` is
   **withdrawn**, and a missing numeric GPU utilisation refuses every tag again, sealed or not. Verified by the live
   chain: `eght122` logged `idle check cpu=3 gpu=6`, and the full harness query answers with the throttle mask
   `0x0000000000000400` (inside the allowed 0x405). **The sealed ABBAs of this session are NOT blocked.** The only
   smoke that ran under the wrong reading is `bsky122` (with `--no-smi`, hence no `gpuclk_bsky122.csv`); it is UNSEALED
   and none of its numbers enter a verdict, so nothing has to be repeated for that reason.
3. **The machine is not idle:** a foreign game (its process, ~0.7 CPU s/s) has been running since before the first
   attempt, so the `procload` gate is waiting for it (retry every 60 s, up to 1800 s). Nothing was installed and the
   lock was never taken while it waits. **Cleared 20:14:52** — the user closed that game and the chain started itself.

## 5. Step 2a DONE: the burn smoke `bsky122` (UNSEALED, disclosed; not a verdict of the session)

Run `bsky122`, build `2baf8742…`, Sky Garden (`underwater_aerial_garden`), entered in 18.9 s at frame 430, held 200.1 s
clean (`hold_exit: null`), 6 166 `FrameTrace` flips, 15 `GateArm:` blocks (14 × 285 evaluated frames + a 153-frame
tail), `failure markers: none`, no `AsyncPipelines: skipped draw`. `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`,
`KYTY_GPU_CHECKPOINTS` not passed; BDA regime NEW (`bda_scan` 53–105 per frame). No GPU utilisation sample (NVML, §4.2).

**Calibration (printed once):** `Burn: selftest target_us=1000 tsc_us=1000.1 qpc_us=1000.1 spin_us=1000.0
cycles_per_ns=2.495240 rdtsc_gap_ns=8.0` — the spin is calibrated in the live process, not only offline.

| arm | code | thread | armed | dose per frame | `cpu/wall` | `burn_late` | `burn_cpu_bad` |
|---|---|---|---|---|---|---|---|
| `burn=0` (blocks 0, 6, 12) | 0 | — | all `burn_*_ns` = 0 | — | — | 0 | 0 |
| `burn=102000` (1, 7, 13) | 1 | GuestGpu | yes, `burn_g` only | 2 000.8–2 001.0 µs | 0.968–0.971 | 0 | 0 |
| `burn=402000` (2, 8, 14) | 4 | main guest thread | **NO — `burn_t_seen` = 0** | — | — | 0 | 0 |
| `burn=802000` (3, 9) | 8 | placebo | yes, `burn_p` only | 2 001.1–2 004.7 µs | 0.976–0.977 | **5 in the first block**, then 0 | 0 |
| `burn=202000` (4, 10) | 2 | record thread | yes, `burn_r` only | 1 991.8–1 993.4 µs | 1.419–1.427 | 0 | 0 |
| `burn=302000` (5, 11) | 3 | M1 workers | yes, `burn_m` only | 1 991.5–1 995.7 µs per frame in total over 4 workers (497.9–499.0 per worker) | 1.482–1.486 | 0 | 0 |

* **Selectivity holds:** in every armed block exactly one counter group grows and the others read 0; the two `burn=0`
  blocks that follow armed blocks read 0 everywhere, so the placebo thread contributes **no** counter noise after it is
  armed once (`burn_p_seen` keeps counting 285 per block with `burn_p_ns` = 0).
* **`cpu/wall`:** blocking codes 1 and 8 land at 0.968–0.977 (≈ 1.00 as designed); spread codes 2 and 3 at 1.42–1.49 —
  above the 1.33 predicted by construction, consistent with more `QueryThreadCycleTime` pairs per slice than the
  design's estimate. It is printed diagnostics, not a verdict.
* **`burn_cpu_bad` = 0 in every block** (the required invariant).
* **`burn_late` = 5** and six `BurnLate: code=8 us=2103.2…2546.1 target_us=2000` lines, all at the placebo's first
  arming (block 3) and none afterwards: the placebo thread's first slices overshoot by 5–27 % while its own thread warms
  up. Harmless for the placebo (it exists to be noise) but it is the one code whose dose is not tight on the first block.
* **Exit is clean:** no `--- Error ---` / `--- Fatal Error ---` / `--- std::terminate ---` / `--- abort() ---`, the log
  ends on ordinary lines, so the placebo thread's `Add` during static destructors produced no crash and no garbage.
* **The extra pin line is exactly one:** `DrawAheadPin: DrawAhead …` appears 6 times against 5 in the s. 121 baseline
  (`log_shp121.txt`) — the placebo thread, as ROADMAP item 3(e) predicted.
* **The vblank staircase is reproduced in every block:** 2 vblanks 82.1–95.1 % of frames, 3 vblanks 2.5–17.9 %,
  1 vblank 0–5.9 %; median `dt` 32 695–34 449 µs. A 2-ms burn does not move the staircase, which is exactly why the
  dose→`dt` slope has to be read in a sealed ABBA, not from these block means.

* **Picture:** `rec_bsky122.mp4` — 6 177 frames 960×540, index complete, **0 one-frame glitches**
  (`s51_vidglitch.py 4 6`). A 2-ms burn on any of the five armed threads does not corrupt the image.

**Defect found — code 4 never arms.** `burn_t_seen` = 0 in all 15 blocks, so the hook at `eventQueue.cpp:444` is never
reached *by the thread registered as `ThreadRole::Main`*: `BurnNewFrame` returns early for `BurnSite::Main` unless
`CurrentRole() == ThreadRole::Main` (`frameStats.cpp:939-944`), and the site itself only fires when a **blocking**
`sceKernelWaitEqueue` returned events (`timo == nullptr || *timo != 0` plus `*out != 0`). `burn_s_main` = 0 against
`burn_s_seen` = 285 per block says the same thing from the other side: the per-frame submission that advances the burn
key is never made by the Main-role thread either. `cpu_main_us` ≈ 9.7 ms per frame, so that thread is alive and busy —
what is missing is the *site*, not the thread. Consequence: **the main-guest-thread arm of the map must use code 7**
(the designed fallback at `GuestGpu::Submit` before its mutex, which burns whichever thread advances the submit key and
does not test the role), and codes 5, 6, 7 remain untested by this smoke because they are not in the six-arm schedule.

## 6. Step 2b: the level entry smokes (UNSEALED, disclosed; not a verdict of the session)

One entry per level, build `2baf8742…`, `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, 120-s hold, video, no schedule.
Read with `smoke122.py --levels` (whole run, first frame that reports a scene onwards).

| tag | level | entered | dt median | vblanks | cpu_gpu/dt | gpu_busy/dt | cpu_main/dt | draws | disp | submits | bda_scan | rec spin us |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `eatl122` | `penguin_atlantis` | 14.6 s, 7 443 frames | 16 737 us | **1vb 99.2 %**, 2vb 0.7 % | 0.832 | 0.637 | 0.252 | 2 600.1 | 152.0 | 27.9 | 69.0 (NEW) | 12 336.9 |
| `eght122` | `time_stopper_ghost_world` | 15.5 s, 4 872 frames | 30 508 us | **1vb 45.2 %, 2vb 54.5 %**, 3vb 0.2 % | 0.977 | 0.483 | 0.263 | 3 514.4 | 146.6 | 27.7 | 1 113.2 (**OLD**) | 20 336.2 |
| `ednn122` | `rotating_level_day_and_night` | 14.9 s, 7 395 frames | 16 706 us | **1vb 98.4 %**, 2vb 1.6 % | 0.972 | 0.646 | 0.466 | 2 570.4 | 258.7 | 29.7 | 60.2 (NEW) | 13 972.1 |
| `edes122` | `intro_next` | 32.5 s, 7 230 frames | 16 845 us | **1vb 99.3 %**, 2vb 0.6 %, +4 frames ≥ 3vb (max 23 796 476 us) | 0.253 | 0.636 | 0.149 | 574.2 | 113.5 | 21.8 | 64.7 (NEW) | 4 365.9 |

Three classes among the first three levels — and `intro_next` is a fourth one of its own (last paragraph of this section):

* **`penguin_atlantis` and `rotating_level_day_and_night` sit on the 60-Hz ceiling** (one vblank in 99.2 % / 98.4 % of
  frames) — the opposite of Sky Garden's two vblanks in 93.4 %. On these levels a saved microsecond buys headroom, not
  a step of FPS, so they cannot show a burn's effect as a change of frame rate; only `dt` below the cap can move.
* **`time_stopper_ghost_world` is the bimodal one** — 45.2 % of frames at one vblank and 54.5 % at two, `dt` median
  30 508 us. It is the only level of the three that actually straddles a step, and therefore the only one where a burn
  dose can flip frames across the staircase; it is also **the only one in the OLD BDA regime** (`bda_scan` 1 113 per
  frame against 60–69 for the other two), so its numbers must never be compared with the NEW-regime levels.
* **All three are CPU-bound on the GuestGpu thread** (`cpu_gpu/dt` 0.83–0.98 against `gpu_busy/dt` 0.48–0.65), and the
  record thread spins 12.3–20.3 ms per frame — the same shape the Sky Garden micro-tracks ran into.

Video: `rec_eatl122.mp4` 7 461 frames, `rec_eght122.mp4` 4 833, `rec_ednn122.mp4` 7 431 — index complete for all three,
**0 one-frame glitches** each (`s51_vidglitch.py 4 6`).

**Caveat for the coming seal (every level, not just the first):** each log carries 20 `AsyncPipelines: skipped draw`
lines, all at a single entry frame (193 / 255 / 221 for `eatl` / `eght` / `ednn`) — cold pipelines during entry, far
before the measured region, since a sealed schedule starts at frame 1800. That marker is fatal for the ABBA scorers,
so `pred/01_map122.md` must either bound the marker check to the measured window or demand a warm pipeline cache;
otherwise every level fails on entry noise. The decision is the lead's, BEFORE the seal.

**Correction (s141 close, `ROADMAP.md` "СЕССИЯ 122" items 217 (а), 221 (з)(2)):** not 20 lines at one frame — 1 320 / 762 / 185 `AsyncPipelines: skipped draw` lines on 14 / 69 / 11 frames (`eatl122` / `eght122` / `ednn122`) [c] (`docs/session-141/inventory141.md` row B5).

**`edes122` (`intro_next`) ran on the fifth attempt, at 21:28:50, and PASSED** (`intro_next` in 32.5 s, acceptance ≤ 90 s; its row and numbers are the last paragraph of this section). It is not a defect of the level: the `procload` gate (0.50 CPU s/s per
process) had refused four attempts in a row because the user's game (its process, 0.68–0.77 CPU s/s) and browser
(its process, 0.51–0.66) keep the machine busy. The gate is NOT weakened — `retry_edes.sh` only repeats the full
`go122a.sh edes122` invocation, each with its own procload checks and its own lock, up to 12 attempts.

Its configuration was checked without running the game and needs no change: `go122a.sh edes122` maps to
`LEVEL=intro_next`, unsealed, `HOLD=120`, `--stable-draws 300` (the desert settles at about 755 draws, so the
threshold is reached), `--rec`, `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, and `KYTY_GPU_CHECKPOINTS` is not
passed at all. **Step 2 is complete: all four level entry smokes are in.** The entry was parked on issue HPP-10 while the gate
stayed shut; the gate opened by itself at 21:28:36 (the user's game stopped burning CPU), the background
`retry_edes.sh` took the slot on its own attempt, and `after_edes.sh` produced the video check and the row
without a human in the loop. Nothing else in session 122 waits on it: the scorer, the fixtures, the mutants and
`pred/01_map122.md` wait on the lead's two decisions (the dead code 4 and the `AsyncPipelines: skipped draw`
window), not on this level.

**`edes122` (`intro_next`, the desert) ran as the fourth level entry smoke, UNSEALED.** Entry: 32.5 s to a stable scene, 7 230 frames read. Reader: `smoke122.py --levels` (the same one as the three rows above, trims 10/5). `dt` median 16 845 us; vblank shares 1vb 99.34 %, 2vb 0.61 %, 3vb 0.01 %, 4vb 0.03 %, 1428vb 0.01 %. Ratios (medians): `cpu_gpu/dt` 0.253, `gpu_busy/dt` 0.636, `cpu_main/dt` 0.149. Per frame: 574.2 draws, 113.5 dispatches, 21.8 submits, `bda_scan` 64.7 (NEW regime), record-thread spin 4 365.9 us. Video: rec_edes122.mp4: 7262 frames 960x540, index entries 7262; one-frame glitches: 0. `AsyncPipelines: skipped draw`: 0 line(s) on frame(s) none. Frames above 2.5 vblanks: frame 4945: 23 796 476 us, frame 5065: 67 687 us, frame 4967: 66 844 us, frame 3301: 45 000 us; `MainTaskLate:` (age of a main-thread task, knob of s. 114) after the entry: frame 4944: 23 812 688 us, frame 5064: 90 186 us, frame 4966: 85 334 us. **This is a fourth class, not one of the three above:** `cpu_gpu/dt` 0.253 against 0.83–0.98 on the other three levels, and a record-thread spin of 4 365.9 us against 12 337–20 336 — the GuestGpu thread is NOT the busy one here, so a burn on it has slack to hide in and a map built only on Sky Garden would miss this shape. The run is unsealed, so these numbers are disclosed and do not enter the verdict of the session.

**The 23.8 s stall of `edes122` is attributed, by three witnesses, to a Bluetooth gamepad that went
out of range during the run (the user disconnected it), and NOT to the build, the level or the emulator.**
The user named the cause; the log agrees and two independent witnesses confirm it.
(1) `log_edes122.txt` holds exactly ONE wall-clock gap in the whole run - 23.809 s, from t=90.075 to
t=113.884 - and `MainTaskLate: us=23 812 688` right at its end: the SDL main thread did not service its queue
for 23.8 s. (2) `gpuclk_edes122.csv`: GPU utilisation 50-97 % until 21:30:24.733, then 6-9 % until
21:30:48.568 and 77-98 % immediately after - the GPU was IDLE through the stall, so this is a host stall, not
a GPU hang and not a TDR (no `nvlddmkm` 153, no `GpuHangAbort`, the process never died). (3) The Windows
System log carries one event inside the whole run window: provider `HidBth`, id 2, Warning, 21:30:24 -
"Bluetooth HID device either went out of range or became unresponsive" - the same second the GPU went idle.
The mechanism is plausible but NOT proven (no stack was captured): the removal is handled on the main thread,
which calls `SDL_GameControllerClose` right there (`window.cpp:378`, and `ReleaseHostPads` sends effect/LED
writes at shutdown), and a dying Bluetooth HID link can block those calls for tens of seconds; a main thread
that stops pumping messages stalls presentation behind WSI. What is measured is the attribution, not the site.

Tool: `hostdev122.py <tag>` (fixtures `test_hostdev122.py`, 87 checks, `ALL OK`, fully offline) reads the run
window from `<tag>.json` (`launched`..`finished`, padded), queries the Windows System log for it, finds `dt_us`
outliers at or after the stable frame and GPU-idle windows inside the busy span, and correlates them:
verdict `RUN_INVALID` (a host device event fell inside the window) / `STALL_UNATTRIBUTED` / `RUN_CLEAN` /
`NOT EVALUABLE` (the System log could not be read). Applied to the four level smokes: `edes122` RUN_INVALID
(`hidbth/2` correlated with a 22.8 s GPU-idle window and frame 4945); **`eatl122` RUN_INVALID as well** -
a second `hidbth/2` at 20:34:49 sits inside its window, but its log has NO gap above 1 s and its worst frame
after the entry is 118 ms, so that event landed at the shutdown edge and left the measured region alone;
`eght122` and `ednn122` STALL_UNATTRIBUTED on 118-264 ms hitches with no host event. All four are unsealed,
so nothing here changes a verdict. For a SEALED run the consequence is the lead's to record in `ROADMAP.md`:
proposal - a sealed run whose window is not clean of `HidBth`/`BTH*`/`nvlddmkm` is invalid and is repeated,
and no Bluetooth device is switched on or off while a sealed run holds the lock.

## 7. Step 3: the scorer `map122.py`, its fixtures and a FULL mutant run — seal NOT written (Harness Engineer, 2026-09-26)

Resumed after the account-limit pause of 20:20 from the files on disk (not restarted). ROADMAP s122 items 13, 14 and 17
(commit `c8b8e7f`) are now in the scorer; the seal waits on the codes-5/6/7 smoke `csky122` (item 13 (c)), which this
step was told not to run (no game in step 3).

* **Scorer** `map122.py` (sha `a92e1bd0…`, unsealed: `PRED_SHA = None`): new admission checks `outlier_pairs` (item
  17 (c): a frame of a schedule block with `dt_us` >= `OUTLIER_US = 500000` drops the pair (2k, 2k+1) whole, printed as
  `OUTLIER frame n= dt_us=`; more than `MAX_OUTLIER_PAIRS = 2` pairs => INVALID; `MIN_PAIRS = 24` counted after the
  drops), `host_clean` (item 17 (a): `hostdev_<tag>.txt` must name the tag, carry exactly `launched .. finished` of
  `<tag>.json` and a verdict `RUN_CLEAN` / `STALL_UNATTRIBUTED`; missing / foreign window / `NOT EVALUABLE` = NOT CHECKED
  = not admitted) and `host_tool` (`hostdev122.py` sha `8404ff8c…`). `no_skip_window` now follows item 14 literally:
  fatal from the population's first frame (1 811) on — the earlier draft only failed frames INSIDE windows, i.e. it let
  a marker between two windows pass; before 1 811 printed (count, largest frame); no block 0 => fatal everywhere.
  `skym122` = `burn=702000` (code 7, item 13); `coverage` for code 7 also needs `burn_s_main` > 0 (the arm measures the
  MAIN guest thread). `reading=HEADROOM` on `intro_next` (game-speed line withheld, item 17 (d)); every VERDICT line
  carries `pairs=` and the BDA regime, OLD adds the no-comparison note (item 17 (e)). Beside the raw slope, report only:
  the draw-adjusted estimator (per pair B dt − A dt × B draws / A draws) with its zone and a `DRAW-ADJUSTED ZONE
  DIFFERS` flag. `--plan-check` moved into `plan_check(tag, plan)`.
* **Fixtures** `test_map122.py` (sha `071f65a7…`): **180, ALL OK**; with `--real` (smoke `log_bsky122.txt`, s121
  `log_shp121.txt`) ALL OK. Edges: 500 000 / 499 999, 2 and 3 dropped pairs, the floor 23/24 after drops, an outlier
  outside the window and on an A block, a dt outlier on an incomplete row, every host verdict and a padded / foreign
  window, the skipped-draw marker at 1 810 / 1 811 / between windows / after the last block / with no GateArm, the
  headroom scene, the draw-adjusted arithmetic, the code-7 role split.
* **The 46 survivors of the unsealed run of 20:13** (228 mutants, 182 killed): 41 killed by new fixtures (the pair
  floor on the scorer's own `MIN_PAIRS`, `PLAN_DEFAULT` pinned against the seal's table, `DRAWS_MIN` at exactly 300,
  idle at exactly 10, the regime edges 300 / 600, exact zone edges by direct calls, two-pair 2SE, label mismatches,
  duplicate rows, the gates sha on byte-only difference, the repeat tag admitted, report lines…); 5 removed as
  equivalent or replaced (`rx_gate_arm_loose`, `arm_asserts_names_ignored` — the dead clause removed from the scorer,
  `estimate_pooled` — a no-op, replaced by a real pooled-means mutant, and the three mutants of the replaced skip-window
  code); reasons in the header of `mut_map122.py`.
* **Mutants** `mut_map122.py` (sha `32873dcf…`): **mutlib v4.1 FULL** (`--control --no-memo --work-dir
  C:/kyty/s122/mutwork --cache-dir C:/kyty/s122/mutcache`, no `--changed-from`): **281 mutants, 281 killed (14 by a
  crash of the suite), 0 survived, 0 unresolved; controls 3 of 3 survived**; 1 worker (the suite spawns `--plan-check`),
  wall 1 478.7 s; report `mut_map122.unsealed2.txt` (sha `7d7526e7…`), log `mut_run_unsealed2.log`.
* **Evidence / gate:** `mk_checks122.py` (new; refuses unless the fixtures are ALL OK now and the report names the
  current harness/scorer/suite/mutants by sha and reads ALL KILLED) wrote `checks/map122_checks.json` (pred None —
  rewritten at the seal). `chk_map122.py --tag skym122` REFUSES correctly: `PRED_SHA / PRED_BYTES not filled`.
  Dry scoring of the smoke `bsky122` (`--draft`): clean NOT_ADMITTED with 11 named reasons, no crash.
* **Chain** `go122a.sh` (sha `bb8c7862…`, `bash -n` clean): `skym122` schedule `burn=0|burn=702000`; after every run
  `hostdev122.py <tag> --pad 0 > hostdev_<tag>.txt` (logged rc and verdict), `hostdev_<tag>.txt` joins the stale-file
  sweep and `hostdev122.py` the sealed `files:` line; the step-4 order in the header.
* **Seal:** draft `pred/01_map122.draft.md` (sha `01003a13…`). Not `pred/01_map122.md`, no `SEALS122.txt` entry:
  item 13 (c) composes the seal only after `csky122`. What remains is mechanical: run `csky122` (unsealed, one run,
  Sky Garden), read it by item 13 (a) (`burn_s_seen` > 0, `burn_s_main` > 0, `burn_cpu_bad` = 0, `burn_t_*` dose
  within ±2 %); rename the draft (drop its DRAFT paragraph, or remove the `skym122` row by item 13 (b)); fill
  `PRED_SHA`/`PRED_BYTES`; fixtures + FULL mutants again on the sealed copy; `mk_checks122.py`; `SEALS122.txt`.
  **No sealed run happened; no smoke number enters a verdict.**

## 8. Step 3b: the codes-5/6/7 smoke `csky122`, the HEADROOM rule of item 18 (c), and the seal `pred/01_map122.md` (Harness Engineer, 2026-09-27)

* **Item 18 (c) in the scorer BEFORE the seal:** `HEADROOM_LEVELS = ('intro_next',)` is gone. `reading_of` /
  `headroom_of`: over the window rows (positions 10–88) of the base-arm (`burn=0`) blocks of the POPULATION PAIRS
  (after the outlier drops — the harness's reading of "окно 10–88 базового плеча", flagged to the lead), the share of
  `dt_us` < `HEADROOM_DT_US` = 25 000; ≥ `HEADROOM_SHARE` = 0.95 ⇒ `reading=HEADROOM` (game-speed line withheld); no
  base-arm row ⇒ `reading=NOT_EVALUABLE` (never HEADROOM; game-speed line withheld too); else `SPEED`. Every report
  prints `reading <R>: base-arm window share of dt_us < 25000 = <share> over <n> frames`. Fixtures: 0.949 / 0.950 by
  direct calls, 24 999 / 25 000 end-to-end (15 vs 16 slow base frames of 316 = 0.9525 / 0.9494), B-arm and outside-window
  frames ignored, a dropped pair ignored, `intro_next` with a two-vblank base reads SPEED, Sky Garden with a one-vblank
  base reads HEADROOM, no base arm = NOT_EVALUABLE. Direct-call fixtures of `pred_checks` for the unfilled and the
  filled constants (trap of s121) and `pred_constants_sealed` (the real file against `PRED_SHA`/`PRED_BYTES`).
* **Smoke `csky122`** (UNSEALED, disclosed; build `2baf8742…`; Sky Garden entered in 19.4 s, stable at frame 389; 200-s
  hold; 6 321 flips; 16 `GateArm:` blocks of `300+1800:burn=0|502000|602000|702000`; `KYTY_GPU_CLOCK_PIN=1`,
  `KYTY_GPU_MARKERS=0`, `KYTY_GPU_CHECKPOINTS` not passed; procload clean, idle cpu 3 gpu 6; `hostdev_csky122.txt`
  RUN_CLEAN (0 events); failure markers none; `AsyncPipelines: skipped draw` 0; BDA NEW, `bda_scan` 54–82):

  | arm | blocks | own group dose a frame | `cpu/wall` | other groups | `burn_s_seen` | `burn_s_main` | `burn_late` | `burn_cpu_bad` |
  |---|---|---|---|---|---|---|---|---|
  | `burn=0` | 0, 4, 8, 12 | — (all 0) | — | 0 | 285 | 0 | 0 | 0 |
  | 502000 (code 5, record thread block) | 1, 5, 9, 13 | `burn_r` 2 000.6–2 000.9 µs | 0.991–0.993 | 0 | 285 | 0 | 0–1 | 0 |
  | 602000 (code 6, M1 worker 0 block) | 2, 6, 10, 14 | `burn_m` 2 000.3–2 001.1 µs | 0.997–0.999 | 0 | 285 | 0 | 0–2 | 0 |
  | 702000 (code 7, `GuestGpu::Submit`) | 3, 7, 11, (15: 8 frames) | `burn_t` 2 000.3–2 000.5 µs | 0.998–0.999 | 0 | 285 | **0** | 0 | 0 |

  Seven `BurnLate:` lines (codes 5/6, 2 050–2 149 µs against 2 000) — the same small warm-up overshoot as the placebo
  in `bsky122`. The vblank staircase again: 2 vblanks 84–97 % of frames in every block.
* **Item 13 (a) FAILS for code 7:** it arms with the exact dose and burns only its own group, but `burn_s_main` = 0 in
  every block — the thread that advances the submit key is not the thread registered as `ThreadRole::Main`. So by item
  13 (b) **the arm "main guest thread" left the map**: `skym122` is removed from `PLAN_DEFAULT` (the tag has no PLAN
  entry; `map122.py --plan-check skym122` exits 2), and `go122a.sh skym122` refuses with the reason. The coverage split
  `burn_s_seen`/`burn_s_main` for code 7 stays in the scorer (fixture tag `sub122`). Mutants `plan_skym_code4` /
  `plan_skym_none` replaced by `plan_skym_back`; `headroom_levels_empty` replaced by 14 reading mutants.
* **Video of the smoke is missing** — my launcher `run_csky122.sh` gave the chain a PATH without `ffmpeg`, so
  `KYTY_REC` wrote only `rec_csky122.mp4.idx` (6 354 entries) and no `.mp4` (`stdout_csky122.txt:17`). The smoke is not
  repeated for it (no verdict uses its picture; the user watches the screen); the launcher PATH now includes WinGet
  Links and chocolatey.
* **Seal:** `pred/01_map122.md` sha256 `3430b26fb77ae7284e23ec7351860b9d4f6b37f7085627de5b39028260d00677`, 11 126 B —
  written into `map122.py` `PRED_SHA`/`PRED_BYTES`; the draft moved to `old/01_map122.draft.superseded_by_seal.md`.
  Fixtures on the sealed copy: `test_map122.py --real` **196 fixtures, 0 failed, ALL OK**.
* **Mutants on the sealed copy:** `mutlib` v4.1 FULL (`--control --no-memo --work-dir C:/kyty/s122/mutwork --cache-dir C:/kyty/s122/mutcache`, no `--changed-from`): **294 mutants, 294 killed (14 by a crash of the suite), 0 survived, 0 unresolved; controls 3 of 3 survived**; wall 1 605.6 s; report `mut_map122.sealed.txt` (sha `2ae1b9c1…`), log `mut_run_sealed.log`.
* **Evidence and seal record:** `mk_checks122.py` wrote `checks/map122_checks.json` (fixtures 194 ALL OK without `--real`, mutants 294/294, pred `3430b26f…`); `chk_map122.py` PASS for `sky122`, `skyp122`, `des122`, REFUSED for `skym122` (no PLAN entry); `SEALS122.txt` seal 01 lists 19 files (scorer `ce35585a…`, suite `49aa53a5…`, mutants `849a4303…`, chain `c4b2b213…`). **No sealed run happened; no smoke number enters a verdict.** Next: the lead's acceptance link of step 3b, which gates the sealed runs of HPP-7 (order `sky122`, `skyp122`, `des122`).

## Step 4 (HPP-7): sealed burn ABBAs by scene — 2026-09-27 00:39–01:41

All runs: build `2baf8742…` installed (IDENTITY `installed_now` ok in every run, nothing rebuilt), seal 01
`pred/01_map122.md` `3430b26f…`, scorer `map122.py` `ce35585a…`, chain `go122a.sh` via `run_step4.sh <tag>`
(lock + `procload` repeated before the lock, `hostdev122.py` after every run), `KYTY_GPU_CLOCK_PIN=1`, no
`KYTY_GPU_CHECKPOINTS`, `KYTY_GATE_SCHEDULE=90+1800:burn=0|burn=V`, `KYTY_GATE_SCHEDULE_ABBA=1`, hold 300 s, estimator
window frames 10–88, no video by the seal (line 28). `skym122` NOT run (item 13 (b), item 20 (c)). No fallback level
needed: every planned level entered.

| tag | level | arm B | BDA | pairs | Δ`dt_us` ± 2SE | s ± 2SE (interval) | reading | vblank | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `sky122` | Sky Garden | 102000 GuestGpu | NEW 53.6/54.4 | 42 | +1 804.7 ± 129.3 | 0.902 ± 0.065 (0.838..0.967) | SPEED | 2vb 91.2 % PINCHED | **NOT_RESOLVED** |
| `skyp122` | Sky Garden | 802000 placebo | NEW | 42 | — | — | — | — | **NOT_ADMITTED** (`idle`: pre-run GPU util median 11 > 10) — not quoted |
| `skyp122r` | Sky Garden | 802000 placebo | **OLD** 1 013/1 015 | 42 | −22.9 ± 188.3 | −0.011 ± 0.094 (−0.106..0.083) | SPEED | 2vb 90.5 % PINCHED | **NOT_CRITICAL** |
| `des122` | intro_next | 102000 GuestGpu | NEW 25.7/31.5 | 98 | −3.3 ± 14.5 | −0.002 ± 0.007 (−0.009..0.006) | HEADROOM | 1vb 100.0 % | **NOT_CRITICAL** |
| `atl122` | penguin_atlantis | 102000 GuestGpu | NEW 31.3/30.6 | 91 | +1.6 ± 12.5 | 0.001 ± 0.006 (−0.005..0.007) | HEADROOM | 1vb 100.0 % | **NOT_CRITICAL** |
| `ght122` | time_stopper_ghost_world | 102000 GuestGpu | **OLD** 1 088/1 085 | 57 | +1 878.2 ± 77.8 | 0.939 ± 0.039 (0.900..0.978) | SPEED | 1vb 47.9 % / 2vb 52.1 %, not pinched | **NOT_RESOLVED** |
| `dnn122` | rotating_level_day_and_night | 102000 GuestGpu | NEW 26.6/26.6 | 90 | +454.0 ± 70.3 | 0.227 ± 0.035 (0.192..0.262) | HEADROOM | 1vb 98.6 % PINCHED | **NOT_CRITICAL** |

All admitted runs: every admission check ok, 0 outlier pairs dropped, 0 skipped draws, `burn_cpu_bad` 0, dose
2 000.4–2 001.3 µs a frame, cpu/wall 0.973–0.996 (block codes, ~1.00 by construction). Host: `RUN_CLEAN` everywhere
except `dnn122` = `STALL_UNATTRIBUTED` (one GPU-idle window 01:35:38–01:35:41, 3.0 s, 9 s after launch — inside the
13.4-s level entry, before the population; admitted by seal line 66).

Report-only lines (not verdicts):
* Draw-adjusted: `sky122` s 0.913 ± 0.047, `ght122` 0.937 ± 0.034 (both NOT_RESOLVED as the raw); `dnn122` 0.322 ±
  0.039 → zone NOT_RESOLVED, **DIFFERS from the raw NOT_CRITICAL** (Δdraws −30.7 ± 10.8 under the dose); `des122` −0.117
  ± 0.157, `atl122` 0.023 ± 0.053, `skyp122r` −0.002 ± 0.085 (all NOT_CRITICAL).
* Δ`cpu_gpu_us` under the GuestGpu dose: +1 826.8 (`sky122`), +1 980.2 (`des122`), +1 901.1 (`atl122`), +1 919.5
  (`ght122`), +1 745.0 (`dnn122`) — the dose lands on GuestGpu in every scene. Δ`gpu_busy_us` within ±2SE of 0 except
  `dnn122` −90.4 ± 52.8.
* Game speed under the dose (SPEED scenes only): `sky122` 0.5270 → 0.4985 (−5.40 %), `ght122` 0.6825 → 0.6338 (−7.14 %).
  GPU-bound: no in every GuestGpu scene.

What this does and does not show:
* On both SPEED scenes (Sky Garden NEW, ghost world OLD) 2 ms burnt on GuestGpu moves the frame by 0.90–0.94 of the
  dose, the 2SE interval does NOT reach 1 → by the reading rule (item 2) **NOT_RESOLVED**: GuestGpu is not proven
  critical (and not proven non-critical) on either. Why the slope stops short of 1 is not measured by this step.
* On the three HEADROOM scenes the slope measures what the frame absorbs before the next vblank step, never speed:
  desert and Atlantis absorb 2 ms fully (s ≈ 0), day-and-night absorbs about ¾ (s 0.227).
* Placebo (`skyp122r`, BDA OLD): a detached 2-ms spinner does not reach the frame (s −0.011 ± 0.094) — noise on the
  process exit and the placebo thread is not visible at this resolution. It is compared with nothing of the NEW
  regime; `sky122` (NEW) has no same-regime placebo.
* Not measured by step 4: record thread, M1 workers, main guest thread (left the map, item 13 (b)), GPU-bound scenes
  (none found). The map is by one thread (GuestGpu) and one dose (2 ms). Picture: the sealed runs carry no video by the
  seal; the picture evidence is the smoke `rec_bsky122.mp4` (0 one-frame glitches with a 2-ms burn on each of the five
  armed threads) and the level-smoke videos (0 glitches each).
* Scores: `score_<tag>.txt/.json`, chain log `go122a.log`, run outputs `step4_<tag>.out`, host `hostdev_<tag>.txt`.

## Audit (step 5, HPP-8, Session Auditor, 2026-09-27)

Document `C:/kyty/s122/audit122/AUDIT122.md` (git `docs/session-122/audit/`), own parsers `recount122.py`, `obs122.py`,
`guards122.py` (no code shared with `map122.py`), checksums `SHA256SUMS.txt`.

* **Recount: CONFIRMED.** All six admitted runs equal the scorer to the last printed digit (Δ, 2SE, slope, interval,
  zone, draw-adjusted row, reading and its share, BDA regime, dose, game speed); a pair bootstrap (20 000) gives the same
  intervals. The block offset (row n of block k at position n − F_k − 1) was derived from the data: the first burnt row
  after an A→B switch is F + 1, and the main line's `arm=` agrees with the `GateArm:` arm on every row of all seven logs.
  A first pass shifted by one row moved Δ by ≤ 42 µs with the same zones — the verdicts are robust to the window edge.
* **Protocol: holds for the verdicts; 3 MAJOR, 5 MINOR, none changes a sealed verdict.**
  * MAJOR-1: agent work inside the sealed windows of `skyp122` and `skyp122r` (lead heartbeats on `HPP-3` committing
    ROADMAP items 22/23 and docs at 00:59, 01:09, 01:10; First agent on `HPP-19` 01:00–01:08), against item 6. The
    placebo verdict stands (unsynchronised load cannot bias an ABBA; top of the interval 0.083 ≪ 0.3), but its 2SE is not
    a clean-run noise figure.
  * MAJOR-2: "a saving below the distance to the next vblank step does not change `dt`" (item 2, `design122.md` §4, §1.3
    above, the scorer's PINCHED text) is refuted by `sky122`: on a scene with 91.2 % of frames at two vblanks a 2-ms dose
    moved MEAN `dt` by 1.80 ms (s 0.90; one-vblank share 11.15 → 2.47 %, three-vblank 0.93 → 3.07 %, which reproduces
    Δ). The design (`burn.md` §2.4) and the review (RC5) said so before the runs. Verdicts unchanged; the invisibility of
    past small wins is a noise limit (2SE ≈ 130–190 µs at ~42 pairs), and the session-123 frame-skip rationale cannot
    cite the staircase. The correction is a new ROADMAP item (HPP-9).
  * MAJOR-3: the seal loosened or dropped guards of the accepted design without a ROADMAP line — dose [0.97N; 1.03N+20]
    → ±5 %, `burn_late` ≤ 1 % → printed, coverage ≥ 0.95 in both arms → B > 0, the DRS guard (`rt_kpx/rt_att` within
    2 %) and `KYTY_GPU_WALL=1` dropped. On the runs the strict dose/late/GuestGpu-coverage guards pass; placebo coverage
    0.899/0.916; `dnn122` pooled DRS +2.33 % but paired +54 ± 57.5 (n.s.). Without `KYTY_GPU_WALL` the sealed runs
    cannot answer why s < 1.
  * MINOR-1 watchdog heartbeats `HPP-18`/`HPP-21` inside sealed windows; MINOR-2 chain and scorer measure idle
    differently (cost `skyp122`, repeat landed in BDA OLD); MINOR-3 this file's stale header and unmarked sections §5,
    §6, Step 4 (header fixed above); MINOR-4 item 21 mixes UTC with local time; MINOR-5 item 2 (N = 2 000 everywhere)
    vs RC5 (dose above the slack on locked scenes) unresolved — HEADROOM verdicts say only "≥ 2 ms of slack at 60 Hz".
* **Not proven:** GuestGpu critical on the reference (item 2's frame-skip condition is literally NOT met); record thread,
  M1 workers, main guest thread; any saving (the map is a derivative in added work at one dose; RC6); why s < 1 — an
  auditor's report-only observation: per pair Δ(`dt` − `cpu_gpu`) −22 ± 55 (`sky122`), −41 ± 31 (`ght122`), while
  `cpu_gpu` grew by only 0.91 / 0.96 of the dose (≈ 165 / 75 µs of GuestGpu's own work vanished under the dose,
  consistent with absorbed spin-waits; whose — [U]); a NEW-regime placebo; the picture of the sealed runs. 60 FPS is not
  promised; the three HEADROOM scenes ran at 0.9994–0.9998 game speed in their windows (pinned) — a measurement of those
  windows, not a claim about the game.
* **Debts** (to be parked at the close): code 4; code 7 off the main thread; codes 2/3/5/6 unsealed; NEW placebo;
  saving-side linearity; GuestGpu idle/spin under `KYTY_GPU_WALL=1`; the staircase correction; one idle criterion and the
  watchdog vs item 6; the missing `csky122` video; double/zero dose per flip on HEADROOM scenes.

## Close (step 6, HPP-9, Roadmap Lead, 2026-09-27)

*Author: the lead.* Decisions: `docs/ROADMAP.md` "СЕССИЯ 122" item 25 (written and committed `3d167e0` before any
action on it).

* **Audit accepted** (recount CONFIRMED, 3 MAJOR / 5 MINOR, no sealed verdict changes).
* **Map verdict (as item 24, not rewritten):** reference Sky Garden (NEW) GuestGpu slope 0.902 ± 0.065 NOT_RESOLVED;
  `ght122` (OLD, judges only itself) 0.939 ± 0.039 NOT_RESOLVED; `des122`/`atl122` HEADROOM (2 ms absorbed fully);
  `dnn122` HEADROOM (≈ ¾ absorbed); placebo `skyp122r` (OLD) NOT_CRITICAL. Map COMPLETE by scene, PARTIAL by thread
  (code 1 and the placebo). Game speed in the base-arm windows (pinned): reference 0.527, `ght122` 0.683, HEADROOM scenes
  0.9994–0.9998; no scene GPU-bound.
* **Staircase correction (MAJOR-2), item 25 (б):** "a saving below the distance to the next vblank step does not move
  `dt`" is refuted by `sky122`; frames are quantized, the mean is not; the invisibility of small past wins is the noise
  limit (2SE ≈ 130–190 µs at ~42 pairs).
* **Lever of session 123, item 25 (в)–(д):** the CEILING of frame skipping, measurement only — a knob (default 0) that
  skips host translation of draws on every second flip while everything the guest can observe still executes, the
  skipped flip shows the previous frame; picture may degrade, hang/death = FAIL; plus a correctness census (guest CPU reads
  of pages written by skipped draws; images written in frame N and read in N+1). Reading: Δ mean `dt` on the reference,
  ABBA, window 10–88; Δ + 2SE < 500 µs closes frame skipping; Δ − 2SE ≥ 500 µs opens a design of the correct version in
  session 124 (sized by the census, not by Δ); otherwise NOT_RESOLVED. Δ is a ceiling, never a gain. `KYTY_GPU_WALL=1` in
  both arms of the sealed run (the "why s < 1" debt; `gw_flip_ns` is the flip-pacing census).
* **Rules added (item 25 (е)–(ж)):** the seal is checked against the accepted design's guard list (MAJOR-3); while
  `SEALED_RUN.lock` exists no run — lead, routine ticks, watchdog tasks included — edits, commits or starts processes
  (MAJOR-1, MINOR-1); the chain uses the scorer's idle criterion (MINOR-2).
* **Installed build restored to `d3a981a2…`** (item 25 (з)); `2baf8742…` (knob `burn`, default 0) stays pinned at
  `C:/kyty/s122/kyty_emulator_2baf8742.exe`.
* **Chain of session 123** on the platform's own mechanisms (item 23): specialist steps with an `executionPolicy` review
  stage by the lead, no acceptance-link tasks, root `HPP-3` blocked on the terminal link, issue watchdog on `HPP-3`;
  `chain_check.py` reduced to a lint (item 25 (и)).
* **Debts parked in §7:** code 4 site dead; code 7 off the main-thread role; codes 2/3/5/6 not in the sealed map; NEW
  placebo; saving-side linearity (RC6); double/zero dose per flip on HEADROOM scenes. 60 FPS is not promised.
