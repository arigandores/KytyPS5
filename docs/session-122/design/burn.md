# Session 122 — knob `burn` (causal probe per thread) and the scene list

Status: DESIGN ONLY (read-only on `C:/kyty/KytyPS5`, HEAD `2f1ca04`; installed build `d3a981a2…`). Nothing here is
recorded in `ROADMAP.md`; every constant below that the lead adopts must be written there (session 122 item 1 and
later items) BEFORE the code / the seal, per the session rule. Line numbers are of the current tree.

Items marked **[AMEND]** go beyond the text of ROADMAP s122 item 1 and need their own ROADMAP line before use.

---

## 0. What the probe answers

d(mean dt) / d(burn) per thread per scene. A thread whose extra N µs of pure CPU per frame moves the mean frame time by
≈ N is on the critical path, and a saving on it converts 1:1; ≈ 0 means it has slack. This replaces the census-to-wall
guesswork that failed in session 121 (texmemo8: −84 % key misses, < 0.16 ms of wall).

---

## 1. The knob

### 1.1 Table rows (LAST rows, as the tree demands)

* `src/common/gates.h:642-644` — today `TexMemo8` is the last `Knob` before `Count` (the comment "LAST row, matching the
  LAST entry of KNOB_DEFINITIONS" sits at :642). Add after it, move the "LAST row" comment down:
  `Burn, // KYTY_BURN, file name "burn" (MEASUREMENT ONLY: code * 100000 + dose_us; 0 off)`.
* `src/common/gates.cpp:420-423` — today `{"KYTY_TEX_MEMO8", "texmemo8", 0, 3}` is the last `KNOB_DEFINITIONS` row. Add
  `{"KYTY_BURN", "burn", 0, 899999},` after it (fallback 0, limit 899 999; `Initialize` :444-453 and `ApplyText`
  :592-604 clamp to `limit`).
* Run `python C:/kyty/s96/check_gate_order.py` after the patch and before the build (enum/table order is not checked by
  the compiler). `burn` is one more name absent from `gates_base.txt` (it lives only in schedule arms), so any harness
  `ABSENT` count grows by 1.

### 1.2 Encoding: one decimal value = thread code × 100 000 + dose in µs

`code = v / 100000`, `dose_us = v % 100000`. Readable in a gate text: `burn=102000` = GuestGpu, 2 000 µs.
Rejected (treated as 0, one log line `Burn: value=<v> rejected` ≤ 8 lines): `code` ∉ 1..8, `dose_us` = 0,
`dose_us` > 20 000.

| code | thread | form | site (anchor) |
|---:|---|---|---|
| 1 | GuestGpu | block, once per frame | `graphicsRun.cpp:790-791` (ThreadRun, after `EXIT_IF(!has_submission)`, before the `process_scope` block that calls `gpu->Process(submission)` at :799) |
| 2 | record thread (the GuestGpu recorder, `m_gpu`) | **spread** over the frame's records | `commandRecorder.cpp:1031-1035` (Loop, after the `if (m_gpu)` block, before the timed `Execute(header, …)`) |
| 3 | M1 draw-ahead pool (all workers) | **spread** over the frame's jobs | `pipelineCache.cpp:3057-3058` (AheadWorker, inside `for (… i < count …)`, before `AheadRun(ahead_slots[taken[i]])`) |
| 4 | main guest thread | block, once per frame | `kernel/eventQueue.cpp:440` (KernelWaitEqueue, success path, just before `return OK`, only if the wait was blocking: `timo == nullptr` or `*timo != 0`) |
| 5 | record thread | block (control for 2) | same site as 2, first record after the key change |
| 6 | M1 worker index 0 | block (task-literal) | `pipelineCache.cpp:3024-3025` (top of `for (;;)`, BEFORE the `ahead_mutex` scope, `index == 0`) |
| 7 | main guest thread | block, fallback site | `graphicsRun.cpp:654-655` (`GuestGpu::Enqueue` entry, before `LookaheadSubmission` :656 and before `m_queue_mutex` :657) |
| 8 | placebo burner | block, own thread | a dedicated `std::thread` started on the first arming of code 8; not on any path |

Codes 4 and 7 fire only when `FrameStats::CurrentRole() == ThreadRole::Main` (the role is registered at
`loader/runtimeLinker.cpp:1512`, the host thread that runs the guest's `main`). Codes 2/5 fire only on the recorder with
`m_gpu == true` (`commandRecorder.cpp:118`).

Why code 3 (pool spread) and not only code 6 (one worker block), which the brief names: M1 jobs are pulled from one
queue by 4 workers (`dathreads` = 4, `pipelineCache.cpp:3029-3045`); a block on one worker is absorbed by the other
three, so code 6 answers "is one worker spare" (expected ≈ 0 always) and code 3 answers the useful question "does M1
throughput gate the frame" (a slower job arrives late, the draw falls back to inline work on GuestGpu — `da_late` /
`da_miss` rise). Both are cheap; code 3 is the one to seal, code 6 is an optional control.

Why spread for the record thread (code 2) and block only as a control (code 5): the recorder idle-spins ≈ 26 ms a frame
(`rec_spin_gpu_us` ≈ 25.8 ms in `log_shp121`), so its slack is huge, but the producer is coupled to it through
`CommandRecorder::Drain` (`commandRecorder.cpp:520`; the producer waits for the tail at every buffer end). A 2 ms block
lands on a drain with high probability and stalls GuestGpu for up to the rest of the block — that measures latency
coupling, not whether record work is expensive. A spread dose (more work per record) is the honest analogue of "record
work got N µs heavier" — the only saving the record thread can offer. Reading 2 vs 5 separates the two.

### 1.3 The frame, the key and the tear rule

**The key.** One global `std::atomic<uint32_t> g_burn_frame` (new, `frameStats.h`, next to `Detail::g_count_limit`),
stored with `memory_order_release` by the presentation thread in `FlipQueue::Flip` right AFTER `Common::Gates::Poll`
(`videoOut.cpp:1197`; add the store at :1198, before `SetLean`). Value = `flip_status.count`. Because the store follows
`Poll`, a thread that loads the new key with `acquire` also sees the knob value `Poll` published for that flip.

**"The frame" per thread** = the interval between two consecutive keys, i.e. one presentation-thread flip interval =
exactly one `FrameTrace` line (the line `n = F+1` reports the interval opened by key `F`). Per thread:

* GuestGpu: the first submission slice it starts after the flip (GuestGpu works one guest frame ahead of presentation, so
  in steady state it is the same rate: one dose per GuestGpu frame).
* record thread: the first record it executes after the flip (code 5), or every record of that interval (code 2).
* M1 pool: the jobs run in that interval (code 3); worker 0's first loop turn (code 6).
* main guest thread: its first blocking `KernelWaitEqueue` that returns events after the flip (code 4), or its first
  submission (code 7). The sampler of session 12 found this thread 64 % asleep "waiting for the flip", 23 % in condvars,
  ~6 % game code (HANDOFF §2.17), so the return from its per-frame wait is the start of its frame work.
* placebo: a thread that polls the key with `Sleep(1)` and spins at each change.

If a thread does not reach its site in some interval, that frame gets no dose (it is not carried over); the scorer uses
the MEASURED burn per frame, never the nominal one, and coverage is a fixture (§4).

**Tear rule.** The knob is read exactly once per thread per key change, in the cold path, and the whole frame's dose
(block length, or spread budget and quantum) is derived from that single read. A schedule switch therefore acts at the
next key on each thread. The only tear left is a thread that loaded key F and read the knob after the NEXT `Poll`
(one frame at a block edge); the estimator window (frames 10–88 of each 90-frame block) excludes it.

### 1.4 The hook (inline, `frameStats.h`) and the cold path (`frameStats.cpp`)

```
// frameStats.h (after Detail::g_count_limit):
inline constinit std::atomic<uint32_t> g_burn_frame {0};
inline constinit thread_local uint32_t t_burn_key  = 0;   // key this thread last acted on
inline constinit thread_local uint64_t t_burn_left = 0;   // spread budget left this frame, TSC cycles
inline constinit thread_local uint64_t t_burn_q    = 0;   // spread quantum, TSC cycles
void BurnNewFrame(uint32_t site, uint32_t key);           // cold, frameStats.cpp
void BurnSpreadStep();                                    // cold-ish, frameStats.cpp
inline void BurnHook(uint32_t site) {
    const auto key = Detail::g_burn_frame.load(std::memory_order_acquire);
    if (key != Detail::t_burn_key) [[unlikely]] { BurnNewFrame(site, key); return; }
    if (Detail::t_burn_left != 0) [[unlikely]] { BurnSpreadStep(); }
}
```

`BurnNewFrame` (once per frame per thread): sets `t_burn_key`, adds 1 to `burn_<t>_seen` for the thread class the site
belongs to, reads `Gates::Value(Knob::Burn)` ONCE, decodes, returns unless `code` matches this site (and the role /
`m_gpu` / `index` condition holds), then either spins the block or arms the spread budget.

**The spin — registers only, no lock, no memory:**

```
// frameStats.cpp, next to TscCyclesPerNs (:142-155), which NowNs (:198-212) also uses.
[[gnu::noinline]] static uint64_t SpinCycles(uint64_t cycles) {
    const uint64_t t0 = __rdtsc();
    uint64_t       t  = t0;
    while (t - t0 < cycles) { _mm_pause(); t = __rdtsc(); }
    return t - t0;                              // elapsed TSC cycles, overshoot <= one pause + rdtsc
}
```

`cycles = dose_ns * TscCyclesPerNs()` — the same constant `NowNs` divides by, so the burnt time is exact in the units
of every `*_ns` counter. `_mm_pause` (not an ALU loop) so that an SMT sibling running another emulator thread loses as
little issue bandwidth as possible (risk R3). If `TscCyclesPerNs() == 0` (no invariant TSC) the knob refuses: one line
`Burn: no calibrated TSC, disabled`, nothing spins.

The bookkeeping (`Add` of counters, the knob read) is OUTSIDE the spin. The counted time is the wall from hook entry
to hook exit on the armed path (`__rdtsc` at entry of `BurnNewFrame` / `BurnSpreadStep` to exit, converted once), so the
spread's per-call overhead is inside the dose instead of hidden beside it.

**Spread (codes 2, 3).** At the key change: budget `B = dose` (code 2) or `dose / dathreads` per worker (code 3,
`dathreads` read in the same cold call); quantum `q = 1.25 · B / max(1, prev)` where `prev` = the calls this thread saw
in its previous ARMED frame (counted only while armed; first armed frame uses `q = 250 ns`). Each hook call spins
`min(q, left)` and stops at `left = 0`, so the dose is front-loaded into the first ≈ 80 % of the frame and never exceeds
`B`; leftover budget at the next key is discarded (the counter shows what was burnt). ≈ 11 000 records a frame on Sky
Garden (`rec_pub` 11 067, `log_shp121`) gives q ≈ 230 ns at dose 2 000.

**Self-test (once, on the first arming of any code):** spin 1 000 µs, time it with `NowNs` and with QPC, log
`Burn: selftest target_us=1000 tsc_us=<x> qpc_us=<y> cycles_per_ns=<c>`. Fixture: both within ±2 %.

**Log lines (all bounded):** `Burn: arm code=<c> thread=<name> dose_us=<n> q_ns=<q>` on each change of armed value per
code (≤ 32 lines), the self-test line, `Burn: value=… rejected` (≤ 8), `BurnLate: code= us= target_us=` when one block
overshoots its target by > 50 µs (preemption witness, ≤ 64 lines).

### 1.5 Counters (`FrameTrace-x`, raw ns / counts, `micros = false`)

Append after `Tm8ProbeN` (`frameStats.h:2177`, before `Count` :2178) and after `{"tm8_pb_n", …}` in the named table
(`videoOut.cpp:2774`). All are at indices above `Counter::LogNs`, so they read 0 under `fslean=1` (gates_base pins
`fslean=0`); they are counted in `KYTY_FRAME_TRACE=lite` (Add is live whenever `FrameStats::Enabled()`).

| name | meaning |
|---|---|
| `burn_g_ns`, `burn_g_n`, `burn_g_seen` | GuestGpu (code 1): burnt ns, burnt frames, frames the hook saw a new key |
| `burn_r_ns`, `burn_r_n`, `burn_r_q`, `burn_r_seen` | record thread (codes 2, 5): ns, armed frames, spin calls, seen |
| `burn_m_ns`, `burn_m_n`, `burn_m_q`, `burn_m_seen` | M1 pool / worker 0 (codes 3, 6); `seen` counted per worker (≈ 4 / frame) |
| `burn_t_ns`, `burn_t_n`, `burn_t_seen` | main guest thread (codes 4, 7); `seen` only on the `Main` role |
| `burn_p_ns`, `burn_p_n` | placebo (code 8) |
| `burn_late` | blocks that overshot by > 50 µs |

Independent witnesses already on the lines: `cpu_gpu_us`, `cpu_main_us` (main `FrameTrace`, thread CPU via
`QueryThreadCycleTime`), `cpu_record_us` (`FrameTrace-draw`), `rec_spin_gpu_us`, `da_late` / `da_miss` / `da_hit`.

### 1.6 What must not change at `burn = 0`

* Nothing spins, nothing is logged, no thread is created, no lock or allocation is added; `burn_*_ns/_n/_q` read 0.
* Per hook call: one acquire load of `g_burn_frame` + one TLS compare (+ one TLS load on spread sites). Per frame per
  hooked thread: one relaxed knob load and one `Add` to `burn_*_seen`. Per flip: one release store.
* No change to PM4 processing order, record order, M1 queue policy, submission order, guest-visible values, the
  translation-cache signature (no file under `src/graphics/shader/**` is touched) or the pipeline cache.
* No new source files (avoids `build_local.cmd configure`): the code lives in `frameStats.h/.cpp`, the table rows, the
  five call sites and the named table.
* Proof at 0 (smoke, unsealed): an A/A schedule `burn=0|burn=0` must read the usual A/A floor; a build-identity check that
  `d3a981a2` and the new build at `burn=0` give the same `FrameTrace` field set plus the new `burn_*` names.

---

## 2. Reading rule (to be recorded in ROADMAP before the seals)

### 2.1 Run shape

`KYTY_GATE_SCHEDULE="90+<start>:burn=0|burn=<code*100000+N>"`, `KYTY_GATE_SCHEDULE_ABBA=1`, `KYTY_FRAME_TRACE=lite`,
`KYTY_GPU_CLOCK_PIN=1` (every sealed run and the video), `KYTY_GPU_WALL=1` (GuestGpu wall regions, live in lite),
40 ABBA pairs = 80 blocks × 90 frames = 7 200 frames (≈ 232 s at 31 FPS, ≈ 120 s at 60 FPS). Estimator window: frames
10–88 of each block (the switch lands at position 89 of the outgoing block), also in every derived scorer.

### 2.2 Estimator

* Per block: mean `dt_us` over the window. Per pair: `B − A`. `Δ` = mean over pairs, `2SE_Δ = 2·sd/√pairs`.
* `N̄` = mean over B-block window frames of `burn_<t>_ns / 1000` (the MEASURED dose, not the nominal one).
* Slope `s = Δ / N̄`, `2SE_s = 2SE_Δ / N̄`.
* Slack of the probed thread in arm A: `slack_A = mean_A(dt_us − cpu_X_us)` (X = `gpu` for code 1, `main` for 4/7);
  thread CPU counts spin-waits as work, so this is a LOWER bound of absorbable slack. Excess slope
  `s_x = Δ / max(N̄ − slack_A, 0.25·N̄)`, reported beside `s`.
* Draw-adjusted estimator (s121 item 9(3)): `Δ_adj = Δ − 5.7 µs · Δdraws`, admitted only if `|Δdraws| < 2SE(Δdraws)`.
* Placebo correction [AMEND]: on the anchor, `s_p` of code 8 at the same N; if `s_p − 2SE > 0`, every slope of that
  scene is reported also as `s − s_p`.

### 2.3 Numbers: noise, dose, signal

Session 121 (`shp121`, Sky Garden, pinned, 44 pairs): `2SE_Δ` = 154.3 µs ⇒ per-pair sd ≈ 512 µs ⇒ at 40 pairs
`2SE_Δ` ≈ 162 µs. Then

| N (µs) | 2SE of s | perturbation of a 31.8 ms frame |
|---:|---:|---:|
| 1 000 | ±0.16 | 3 % |
| 2 000 | ±0.08 | 6 % |
| 3 000 | ±0.054 | 9 % |

**Doses (proposal):** code 1 (GuestGpu) and code 4 (main) at **N = 2 000** on CPU-bound scenes — 1 and 0 are 12 SE apart,
and 0.5 is resolved to ±0.08, while the frame moves only 6 %. N = 1 000 is too close to the GuestGpu slack
(`dt − cpu_gpu` ≈ 31.83 − 31.15 = 0.67 ms on Sky Garden in `log_shp121`): if all of it were absorbed, a truly critical
GuestGpu would read s ≈ 0.33 at N = 1 000 but ≥ 0.67 at N = 2 000. Codes 2/3/8 on the anchor at N = 2 000.
**Vsync-capped scenes** (arm-A mean dt ≤ 17.2 ms and ≥ 90 % of frames in 15–18.5 ms, e.g. the desert at 59.7 FPS):
the cap hides everything below the slack, so the dose is set from that scene's smoke:
`N = roundup_500(max(2 000, slack_smoke + 2 000))`, ≤ 12 000; the reading there is `s_x` (and "headroom ≥ slack").

### 2.4 Quantization: why the MEAN dt is the right observable

`log_shp121` (9 546 flips with ≥ 2 000 draws): 10.8 % of frames at 16–20 ms, 86.0 % at 30–36 ms, 1.9 % at 46–52 ms;
mean 31.83 ms, median 33.27 ms. Flips land on vblanks, but GuestGpu produces frames without waiting for them
(cpu_gpu 31.15 ms), so the flip phase drifts and the one-vblank frames are the dither: the MEAN interval equals the
production period W. Adding N to W moves the mean by N (the one-vblank share falls; past 33.3 ms the three-vblank share
rises) — linear in N as long as the flip queue does not back up. The MEDIAN is quantized and must not be used. The
scorer prints the share of 1/2/3-vblank frames per arm as a diagnostic (the expected sign: at N = 2 000 on Sky Garden
the 16–20 ms share should drop from ≈ 11 % towards 0).

### 2.5 Classification per scene (lite counters of arm A + slopes)

| class | condition |
|---|---|
| **GuestGpu-critical** | code-1 `s`: 2SE interval contains 1 and not 0 (ROADMAP s122 rule). [AMEND] also when it excludes both but `s_x` contains 1 ("critical after slack") |
| **GPU-bound** | median `gpu_busy_us/dt_us` ≥ 0.9 AND code-1 `s` contains 0 (expected when `N < slack_A`: GuestGpu waits for the GPU inside `Process`, visible in `semwait_gpu_us` and in `slack_A`) |
| **vsync-capped** | arm-A mean dt ≤ 17.2 ms with ≥ 90 % of frames at one vblank; read `s_x` and the headroom |
| **main-critical** | code-4 (or 7) `s` contains 1 and not 0 |
| **other-thread** | code-1 `s` contains 0, `gpu_busy/dt` < 0.9, not capped ⇒ the critical thread is none of the probed ones (guest task threads, present thread) — a new probe, not a GuestGpu track |
| **partial** | `s` excludes both 0 and 1 and `s_x` excludes 1 ⇒ two limits alternate; report, no track opened on it alone |

Lite fields for the table (all live in lite): `dt_us`, `cpu_gpu_us`, `cpu_main_us`, `gpu_busy_us`, `semwait_us`,
`semwait_gpu_us`, `draws` (main line); `rec_spin_gpu_us` (x); `cpu_record_us`, `rec_work_us`, `bda_scan` (draw);
`gw_idle_ns`, `gw_blk_ns`, `gw_flip_ns`, `gw_proc_ns` (x, with `KYTY_GPU_WALL=1`); `rt_kpx/rt_att` (DRS step);
BDA regime by `bda_scan` (≈ 52 NEW / ≈ 1 066 OLD per frame).

Expected on Sky Garden (prediction, to be sealed): GuestGpu `s` ∈ [0.67, 1.0] at N = 2 000; main `s` ≈ 0
(`dt − cpu_main` ≈ 22.6 ms of slack); record spread ≈ 0 (recorder idles ≈ 26 ms); record block (code 5) > 0 through
`Drain`; M1 pool spread small unless `da_late` rises; placebo ≈ 0.

---

## 3. Scenes

Level names are the `<File>` values of `data/prein/product_levels.xml` (the `-lvl` argument resolves against these
lists: neither `underwater_aerial_garden` nor any other level name is a string of `eboot.bin`, and Sky Garden enters
with `-lvl underwater_aerial_garden`). All candidates are `PlayGoChunk 0` and have `levels/<name>/level.lvx` on disk.
The project's logs contain only six levels ever started (`Level has started:` over `C:/kyty/**/*.txt|log`:
`underwater_aerial_garden` 4 647, `ps_logo` 446, `title_controller_ship` 438, `intro_next` 425, `worldmap` 71,
`transition_next` 71); `-lvl` was only ever used with `underwater_aerial_garden` and `intro_next`. So every heavy
candidate is new to the emulator and needs the unsealed entry smoke.

Evidence of weight is the per-level data under `data/prein/levels/<name>/` (`gfx/*.jxm` = level geometry; `pfx/*.pfbhk`
= Havok physics data, a guest-CPU indicator, not particles). Textures are shared and not counted. Sky Garden for scale:
gfx 12.4 MB / 23 files, pfx 6.2 MB.

| order | `-lvl` name | product name | gfx (jxm) | pfx (physics) | lvx layers | why |
|---:|---|---|---:|---:|---:|---|
| anchor | `underwater_aerial_garden` | G1 Aerial Garden ("Sky Garden") | 12.4 MB / 23 | 6.2 MB / 13 | 17 | known CPU-bound anchor |
| anchor | `intro_next` | Intro (desert) | 1.1 MB / 4 | — | 3 | known; 755 draws, 59.7 FPS ⇒ vsync-capped, `--stable-draws 500` |
| **1** | `penguin_atlantis` | G4 Atlantis | **900 MB / 176** | 311 MB / 162 | 27 | 2nd-largest geometry of the game, 73× Sky Garden; underwater scene; moderate risk |
| **2** | `time_stopper_ghost_world` | G4 Horror Time | **3 830 MB / 114** | 1 137 MB / 107 | 25 | largest geometry by 4×; highest GPU-load candidate; risk: memory/import preload and load time |
| **3** | `rotating_level_day_and_night` | G5 Day and Night | 69 MB / 44 | **176 MB / 92** | 17 | lighting change + heavy physics ⇒ the best candidate for a non-GuestGpu (guest) critical thread |
| alt | `hub_crashsite` | Hub Crashsite | 182 MB / 63 | 100 MB / 46 | 49 | crowd of VIP bots, most layers; likely CPU/draw heavy (a second GuestGpu-bound point) |
| alt | `hoover_beach` | G5 Hoover Beach (secret) | 166 MB / 23 | 60 MB / 11 | 18 | geometry |
| alt | `mini_giants_garden` | G4 Giants Garden | 137 MB / 85 | 79 MB / 77 | 28 | geometry + physics |
| alt | `ice_iceberg` | G5 Iceberg | 100 MB / 16 | 36 MB / 7 | 12 | geometry |

**Smoke order:** `penguin_atlantis` first; then `time_stopper_ghost_world` (if it fails to enter, hangs or exceeds the
memory budget, replace by `mini_giants_garden`); then `rotating_level_day_and_night` (if it fails, `hub_crashsite`).

**Smoke protocol (unsealed, disclosed):** `enter_scene.py <tag> --level <name> --stable-draws 300 --timeout 480
--attempts 3 --hold 60 --rec` (the first entry after a new build hangs by the rule of sessions 54/61, and each new level
translates new shaders — first attempts are warm-ups). Record from the smoke: entered or not, time to stable, draws
distribution (set the sealed `--stable-draws` to ≈ 0.6 × median), `dt`, `cpu_gpu_us`, `gpu_busy_us`, BDA regime, the
vblank shares, and from the video whether the stable frames are gameplay or the level's intro fly-over (only video is
admissible as picture evidence). A level whose first stable frames are a cinematic needs a longer `--hold` before the
schedule start.

---

## 4. Fixtures the scorer needs (plus mutants, `mutlib` v4.1 full runs, suite ends with `ALL OK`)

Parsing / protocol
1. Join `FrameTrace` main + `-x` + `-draw` lines by `n`; `arm=`/`blk=` from the main line (already shifted); drop frames
   before the first `GateArm:`; window 10–88; `STREAMS_COMPLETE` (every main-line flip in the measured range carries all
   three lines, except the last).
2. `GateArm: text=` of arm 0 is exactly `burn=0`, of arm 1 exactly `burn=<pre-registered value>`; decode → (code, N)
   equals the pre-registration; a text with a second assignment of `burn=` → NOT_ADMITTED (first assignment wins).
3. IDENTITY: sha256 of the installed exe and of the pred file; fatal markers (`AsyncPipelines: skipped draw`,
   `--- std::terminate ---`, `--- Error ---`, `GpuHangAbort:`) → NOT_ADMITTED.

Armed proofs
4. B blocks: `burn_<t>_n / frame` ≥ 0.95 (block codes) and `burn_<t>_ns / frame` within [0.97·N, 1.03·N + 20 µs];
   spread codes: ≥ 0.90·N. A blocks: every `burn_*_ns` exactly 0.
5. Independent clock: `cpu_gpu_us(B) − cpu_gpu_us(A)` (code 1) or `cpu_main_us` (4/7) within ±15 % of N̄.
6. Coverage in BOTH arms: `burn_<t>_seen / frame` ≥ 0.95 (main: if < 0.95 the main dose is NOT_EVALUABLE — switch to code 7
   through a new ROADMAP line, never silently).
7. `burn_late` ≤ 1 % of armed frames; self-test line present and within ±2 %.

Guards
8. DRS step: `rt_kpx/rt_att` per arm within 2 %; `Δdraws` significance printed; draw-adjusted estimator admitted only when
   `|Δdraws| < 2SE`.
9. Same BDA regime in both arms (per-arm mean `bda_scan`).
10. Vblank share table per arm (diagnostic, not a gate).

Estimator / classification (synthetic logs)
11. Δ = N exactly → s = 1, contains 1; Δ = 0 → s = 0; Δ = N − slack → s < 1, `s_x` = 1; Δ with a 1-frame tear at every
    block edge → unchanged (window); an A block carrying burn → NOT_ADMITTED; a B block with `burn_n` = 0 → NOT_ADMITTED;
    nominal N ≠ measured N̄ → slope uses N̄.
12. One synthetic per class of §2.5 (GuestGpu-critical, GPU-bound with `gpu_busy/dt` 0.95, vsync-capped, main-critical,
    other-thread, partial), each on the boundary (contains-1 edge, 0.9 edge, 17.2 ms edge).
13. Each new field on a synthetic line (the session-105 rule: a derived scorer must be checked on a line with every new
    field before the seal).

---

## 5. Risks

* **R1 lock inside the burn.** Every site is outside emulator locks: code 1 after `m_queue_mutex` scope closes
  (`graphicsRun.cpp:765`) and before the render mutex is taken inside `Process`; code 2/5 before `Execute` with no mutex;
  code 3/6 outside `ahead_mutex` (`pipelineCache.cpp:3028-3045`); code 4 after `WaitForEvents` returned; code 7 before `m_queue_mutex`.
  The reviewer must re-verify each at patch time. The main-thread burn may run while the GUEST holds its own locks —
  accepted: that is exactly what longer guest code would do.
* **R2 slack absorption.** A block at submission start can fall into a wait that follows (flip done, WaitRegMem);
  hence `s_x` and N = 2 000 ≫ 0.67 ms on Sky Garden.
* **R3 shared core / power.** A spinning thread shares its physical core with an SMT sibling and raises package power
  (lower boost elsewhere). `_mm_pause` minimises the first; the placebo (code 8) measures both on the anchor.
* **R4 preemption.** The dose is wall time on a TSC target, so a descheduled burner still delays its thread by the dose;
  overshoot is counted (`burn_ns` is measured) and flagged (`burn_late`).
* **R5 game adaptation.** Longer frames lower the pacer speed (`KernelSetGuestSpeed`) and stretch audio; the game steps
  1/60 s per frame, so work per frame should not change — guarded by `Δdraws`, the DRS step and `KYTY_GPU_CLOCK_PIN=1`.
* **R6 record coupling.** Code 5 reads `Drain` coupling, not record cost; never classify the record thread from code 5.
* **R7 main-thread site coverage.** Unknown whether the main guest thread blocks in `KernelWaitEqueue` every frame; the
  smoke must show `burn_t_seen` ≈ 1 per frame, else code 7 (new ROADMAP line first).
* **R8 new levels.** None of the heavy candidates was ever run: shader translation stalls, possible unimplemented
  features, memory (`time_stopper_ghost_world` has 3.8 GB of geometry against the 13.5 GB backing and the import
  preload), a fly-over intro that looks "stable" by draws. Smoke with video first; replace per §3.
* **R9 interaction with other measurement knobs.** Never combine with `bindfloor`/`bfburn`, `spine`, censuses or
  `mutsite`; the arms differ only by `burn=`.
* **R10 malformed value.** `burn=2000` (no code digit) decodes to code 0 → off (logged); the scorer's fixture 2 catches
  a wrong arm text before any number is read.
* **R11 heavy neighbour.** No speed number beside another heavy job: `procload` and the name guard before the lock, as in
  the session rule.
