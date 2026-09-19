# Session 98 — route E, measurement M3 (third attempt): the edge hang

**Order M3 → M4 → M5 stays** (the user's decision, session 97). Read `C:/kyty/s97/FACTS.md` in
full first (in git `docs/local-session-97.md`), then `ROADMAP.md` §0.1 and §2 E, `C:/kyty/s97/README.md`,
and the sealed `C:/kyty/s97/pred/01_floor_reversible.md` and `pred/02_floor_walk.md`.

**Open the report with the three numbers:** budget ≤ ~3.0 µs a draw (median) / ≤ ~2.3 µs (p99,
7 284 draws); today 6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms; undone M3, M4, M5. **Do not
promise 60 FPS** (~15 %).

## 0. Where M3 stands

* `F_st` does not exist. **M3 is not closed; G and R1 are neither closed nor licensed.**
* The session-96 death (a gate torn inside one draw) is **fixed and proven**: 0 tears, 0 silent
  deaths in 486 survived falling edges. The texture and buffer storms after an edge are gone
  (R6 1 051 → 14–27, R7 1 056 → 3).
* **Blocker: a GPU execution hang at ~0.6 % of falling edges** (3 in 489; plus 1 at a rising edge
  in the checkpoint-mode diagnostic `hg97a`, whose warmup hung on ENTRY with no floor at all).
  Every one: first base flip after the edge, ~20 submissions into it (~88–90 KB of log after the
  `GateArm` line), `role=4 requested=known+1`, the CPU 87 ticks ahead, zero backlogs, the hung
  submission waits on nothing, the GPU at **100 % / ~174 W** until the abort, an `nvlddmkm` event
  153 at the same second (TdrDelay is 60 s here). **The signature equals the historical ENTRY hang
  (6.67 % of entries).** A 300 s hold at period 10 survives only ~1 time in 3.
* The sealed stopping rule of `pred/02_floor_walk.md` §1.6 fired on `rv97b`: nothing further was
  run on the floor in session 97.
* **Built, not run:** `patch_s97d.py` (binary `e80b1603…` in `C:/kyty/build/install`) — with
  `nullDescriptor` the floor binds TRUE null descriptors instead of the shared 16-byte NULL buffer
  and the nine null images (floor stores polluted the buffer the real path reads for degenerate
  V#s; `Vulkan nullDescriptor:` is logged; counter `bf_ndesc`). It removes ONE candidate.

## 0.1 The prime suspect (read-only finding of `wf_724e89d5-00b`, lens "loops" — not yet proven)

The only unbounded, memory-driven loops in this scene are the BVH traversals of FOUR indirect
async-compute ray-tracing kernels issued every frame through `AgcAcbDispatchIndirect`:
**`0x503d7f066a496c3c`, `0x1f16e50eea0c89e3`, `0xff8ee744ffa4dcdc`, `0xf88d0f630ac5b35d`**. The
leaf loop exits only on a sign-bit sentinel read from memory (variant-V# `S_BUFFER_LOAD` through
the base address, no bound), the node loop only when every child is `0xFFFFFFFF` and the stack is
empty (the stack pointer is clamped with `S_MIN_U32 s46,60`, so an overflow never exits), there is
no step counter, and the game's own invalid-TLAS guard (`S_BITCMP1` bit 18 → `S_TRAP`) is translated
as a no-op (`Scalar.cpp:229-231`). During 20 floored flips the BVH / instance / light-list
producers wrote only into the null buffer while the guest kept streaming and reusing memory; a
stale pointer into still-registered memory reads real bytes that are not a BVH, no fault is
recorded, and the wave never returns. The historical ENTRY hang: in 8 of 8 logs it came one frame
after the fault path registered a wild BDA page. **Also a one-line defect: the `GpuHangAbort`
branch of `masterSemaphore.cpp:113` calls `ReportGpuCheckpointHistory` (the CPU ring), not
`ReportGpuCheckpoints` (the GPU-written breadcrumb) — that is why no run ever named the op.**

Suggested repair to pre-register (measurement only): a translator knob that caps the iterations of
every loop in programs containing `BvhIntersectRay` (e.g. 1<<16 steps an invocation), part of the
shader-translation-cache signature (unlike `KYTY_LOOP_LIMIT`), active in BOTH arms, with a
host-visible trip counter in `FrameTrace-x` — it turns a process-killing hang into a counted
picture glitch, which the floor's charter allows. Alternative: skip (not floor) those four
dispatches while the latch is armed and in the first base flip after a falling edge, and exclude
that flip from scoring.

**The trigger's marker (synthesis of `wf_724e89d5-00b`, post hoc on two hangs, replicated by the
third on another binary, chance ≈ 0.02):** the direct-write site `+0x80d33b` is the GDS barrier
(`MakeGdsDependency` inlined in `CommitBindings`; confirmed by disassembling `c6fe36da`). A real
GDS barrier ran inside the edge flip's own interval at **14 of 489 falling edges — all three hangs
are among them (3/14 ≈ 20 % against 0/475)**. The per-op latch flips the floor MID-FRAME: floored
producers early in the GPU frame, real consumers after them. **Ranked fix: a frame-latched floor**
— GuestGpu adopts the scheduled value only when it processes the flip EOP (`sync.cpp` EopFlip /
EopWriteBackFlip / EopOnlyFlip), `BindFloorLatchOp` and the GC freezes read that value, a new
counter `bf_mixed` (frames holding both armed and unarmed ops) must read 0 — count it per queue:
the four ray-tracing kernels arrive through `AgcAcbDispatchIndirect` and the async-compute queues
may not share the graphics flip boundary (then adopt only when no submission is in flight on any
queue). Keep patch D. Do NOT keep written slots real (floored producers would write garbage into
what real consumers walk, and ~490 µs of binding cost would return to the ceiling).
`GetFrameNum()` is NOT a frame clock (it is `m_done_num`, advanced by `AgcSuspendPoint`).
A quick trigger test: apply a pending change at the first real GDS-barrier op after `Poll` — the
hazard should rise to ~20 % an edge.

## 1. First, name the op that runs away (no guessing past this point)

The checkpoint breadcrumb of session 97 printed only CPU-recorded EOP writes. Two ways, pick one
and pre-register it:

* **(a) run** `KYTY_GPU_CHECKPOINTS=1 KYTY_GPU_HANG_ABORT_S=0`, ABBA period 2–4, so the 60 s TDR
  returns `eErrorDeviceLost` and `ReportGpuCheckpoints` names the never-completed op with its
  ps/vs/cs hash. The checkpoint mode hung on ENTRY in `hg97a` — count that, do not hide it.
  **Each hang then freezes the desktop for ~60 s** (TdrDelay 60). Trust the NV top/bottom-of-pipe
  markers over the breadcrumb: dispatches are not wrapped in an extra barrier (only draws are,
  `renderDraw.cpp:1468-1480`).
* **(b) patch** the `GpuHangAbort` branch (`masterSemaphore.cpp:104-118`) to read and print the
  GPU-written breadcrumbs and the NV checkpoint data before EXIT, and widen the `KYTY_QUEUE_TRACE`
  record so every tick carries the CS/VS/PS hashes recorded into it.

Then the lever **`KYTY_LOOP_LIMIT`** (with `KYTY_SHADER_CACHE=0`) in BOTH arms: 0 hangs in
≥ 300–400 falling edges ⇒ a shader loop; the same rate ⇒ a draw or an indirect count.
Read-only, before any run: find the OIT resolve shader (per-pixel linked lists built by ~16
shaders, a head image and a node buffer) in the translation cache / a `KYTY_DUMP_GCN` dump and
check whether its loop is capped and what clears the head image.

## 2. Then the fix — candidates, ranked by the session-97 workflow `wf_724e89d5-00b`

1. **A game shader runs away on data a transition frame left inconsistent** (0.35–0.55): GPU-built
   pointer structures (OIT lists; possibly BVH, light lists) torn or stale across the floor. Fixes:
   (i) adopt the scheduled `bindfloor` value on GuestGpu only at a guest-frame boundary (the flip
   packet), so no guest frame runs half floor, half real; (ii) keep REAL bindings for written and
   atomic resources (storage images, written buffers, GDS; ~5.6 % of slots) and null only the
   read-only ones — producers stay structurally consistent; its cost goes into `F_st` and must be
   stated (conservative for CLOSE).
2. **Shared-null pollution** (0.12–0.20) — patch D; can be confirmed by downloading the 16 bytes of
   `NULL_BUFFER_ID` at each latched falling edge.
3. Floor draws rasterising garbage into real targets and history (0.12).

**Every change above is a change to the instrument**: a new sealed pre-registration, a new
reversibility proof (`rv98a`: the R1–R7 of `rv97.py`, ≥ 100 falling edges on the counted
attempt), and only then `bf97a`/`bf97c` exactly as `pred/01` §5 and `pred/02` §2–§3 of session 97
wrote them (both-instruments verdict: CLOSE only if `min(F_a, F_c) + 2.65 ≥ 15.5`, PROCEED only if
`max(F_a, F_c) + 2.65 ≤ 11.0`). `bf97c`'s burn is fixed from `bf97a`'s own numbers.

## 3. The user's decision that is owed

The synchronisation term now has both numbers: **label +2 893.6 ± 93.2 µs (`bd96a`, NEW regime)**,
**submission +103.5 ± 112.0 µs, t = +1.85 (`bd96b`, OLD regime)**. Which one M3 uses is the
user's choice — and the two came from different BDA regimes.

## 4. Traps of session 97 that turned out to be real

1. **Gates flip on the presentation thread.** Any gate read more than once inside one op can
   tear. `bindfloor` now latches per op; no other gate was audited.
2. **UCRT `std::set_terminate` is PER THREAD**; the process-global report is the `SIGABRT`
   handler (patch B).
3. **A sealed control can be unsatisfiable for the instrument it scores** — C6 (the floor zeroes
   `bda_scan`), C8 (the burn equalises `cpu_gpu_us`), C10 (every rising edge books burn into the
   last unarmed flip). Dry-run every scorer on the previous session's fixtures BEFORE sealing.
4. **"No WER event" means nothing here**: WER is disabled for the user. The System log's
   `nvlddmkm` 153 is the GPU-side witness; `gpuclk_<tag>.csv` shows execution (100 %) vs wait (0 %).
5. **`KYTY_GPU_CHECKPOINTS=1` changes the run**: its warmup hung on entry.
6. **A stopping rule binds even when a new idea arrives**: `pred/02` §1.6 said "nothing further on
   the floor this session", patch D was ready, and the rule was kept — D waits for its own
   pre-registration.
7. Carried: `KYTY_*` go POSITIONALLY to `enter_scene.py` (`--rec` sets `KYTY_REC` itself);
   check `nvidia-smi` before a run; never rebuild between acceptance and the final answer (the
   installed exe is `c6fe36da…`; `C:/kyty/build/install` holds `e80b1603…`).

## 5. The port

`C:/kyty/s97/s98_port.py`, written fresh in the SOURCE folder, modelled on
`C:/kyty/s96/s97_port.py` (five root constructs, the ledger, diagnostic (i)); `gates_base.txt`
byte-identical (1 092 B, 99 names, `00c116dc…0594d8`); the seven sealed preds of sessions 96–97
into `prev97/` byte-exact; `pred/` empty; `accept98.sh` written new; the carried scorers pinned by
path must be pointed at `prev97/pred/` (session 97's `s97_harness.py` did this for `prev96`).
