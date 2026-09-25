# Session 119 — removability design for the `mh_emit` parts com / rt / vtx / rec (read-only code study)

Author: agent (read-only; no build, no run, no source edited). Source tree `C:/kyty/KytyPS5` at the working tree of
session 119 (installed build `d3a981a2…`, measurement build of `spk118` = `321175ab…`). Numbers: `spk118` arm M
(`takelap=1 bindlap=1 pathlap=1 mutsite=1`, pinned, Sky Garden, BDA NEW), re-parsed from `C:/kyty/s118/log_spk118.txt`
by this agent: frames of arm 1 in block positions 10–88, **3 210 frames**, means per frame. The parse reproduces the
task's numbers to the microsecond (com 2 377.2, rt 1 566.2, vtx 1 364.3, rec 1 226.3, pipe 745.6, rest 45.3,
`mh_emit` 7 430.5, `pl_em_n` 5 024.9, `draws` 5 044.9).

Tags: **[M]** measured (source run named), **[I]** inferred from code reading + arithmetic, never measured.
Per-draw divisor: `pl_em_n` = **5 025** draws that ran the emit chain (5 040 gives the same to 0.3 %).

**Bottom line first.** No single part of `mh_emit` has a removable share that code reading can put at ≥ 1 ms.
One mechanism is borderline and is the only one worth a measurement: a **same-pass render-target memo** (skip
`AcquireRenderTargets` when nothing it depends on moved since the previous draw), ceiling **0.9–1.1 ms [I]**, and
**1.3–1.5 ms [I]** if the commit-side image transitions are skipped under the *same* witness. Everything else
(vertex/index memo, write-list offload, record-side hoists) is **< 1 ms [I] by construction** and should not open a
track. What turns the borderline into [M] is one census gate (§6), not code.

---

## 1. What each span times (the marks)

`PathLap` (`src/common/frameStats.h:2355-2385`): the constructor sets the thread-local cursor, each `Mark(c)` charges
`now − cursor` to `c` and moves the cursor, the destructor charges the remainder to `pl_em_rest`. Arm with
`Enabled()` (lite-safe). The chain opens at `renderDraw.cpp:2305-2308`, exactly where `HoldPhase(HoldEmitNs)` opens
(`:2300`), so Σ`pl_em_*` = `mh_emit` on the same draws (7 425.7 of 7 430.5 µs here; the 0.06 % is flip read skew).

| span | opened at (previous mark) | closed at | what runs inside |
|---|---|---|---|
| **vtx** | `renderDraw.cpp:2305` (chain start) | `:2438` | `KYTY_IMAGE_WATCH` static (`:2314-2340`), debug-dump checks `DebugDumpFrame/Address/Addresses` (`:2341-2429`, static guards, `renderCompute.cpp:1016-1075`), `MutScope` ctor (`:2312`), **`AcquireVertexBuffers`** (`:1361-1460`: collect ranges, `std::sort`, merge, `ClampRangeSize`, **`ObtainBuffer` per merged range** `:1408`), **`PrepareIndexBuffer`** (`:1702-1726`: stream copy for host data or **`ObtainBuffer`** `:1717`) |
| **rt** | `:2438` | `:2452` | `DrawStatTail` (no-op when off), **`AcquireRenderTargets`** (`:870-1133`) |
| pipe | `:2452` | `:2500` | indirect sanitizer (rare), `GetGraphicsPipeline` — not in scope |
| **com** | `:2500` | `:2669` (packet) / `:2811` (direct) | skip-draw check, `PassDraw` Add (`:2526`), `drawmerge`/`mergecost` scaffolding (`:2541-2619`), `framerep` gate read (`:2624`), `SetDrawDebugPhase` (`:2666`), **`CommitBindings`** (`descriptors.cpp:3386-4050`) |
| **rec** | `:2669` | `:2790` (packet) / `:2935`, `:2970` (direct) | `BeginRenderingPacket` (`context.cpp:274,324-406`), `RecordCommandWriter` open (`commandRecorder.cpp:317-334`), vertex/index binds (`renderDraw.cpp:2680-2681`), **`SetGraphicsDynamicParams`** (`:386-543`), stencil (`:354-381`), feedback-loop state, pipeline bind, GPU markers (no-op), `EmitDrawPrimitives` (`:1772`), **`HasShaderBufferWrites`** ×stages (`shaderResourceBarrier.cpp:92-115`), shader-write barrier decision, **`tail.Commit`** → `EndRecord` → `Publish` (`commandRecorder.cpp:499-518, 336-375, 253-280`), debug phases |

The default path is the packet path (`recpack`, `packet && buffer.Recorder()`, `:2665`): `rec_pack` 5 005 of 5 025
draws record through the ring [M spk118]. The direct path (`:2797-2970`) carries ~20 draws a frame.

### 1.1 Main work per span, with the population [M spk118 arm M, per frame]

* **com — 2 377 µs = 473 ns/draw.** `bindlap` splits it (`descriptors.cpp:3524-3556`, same stamps): **transit
  `bl_tr` 967.2** (the per-image-slot loop `:3740-3816`: `GetImage`, `MaterializeDeferredDccClear` `:1845-…`,
  layout decision, `Image::Transit`), **write-list `bl_wr` 659.5** (`:3835-3929`: one `WriteDescriptorSet` per program
  binding, infos pushed into `m_descriptor_buffers/images`, `MakeImageInfo`, push-data copy), **emit `bl_em` 479.9**
  (`:3971-4007`: `DescriptorHeap::Commit` for pooled layouts, `PushBindingsPacket` → `CommandRecorder::PushBindings`
  `commandRecorder.cpp:440-497`, a ~1 KiB record memcpy + publish). Remainder **269.6** = span head before the call +
  function prologue + `bindlap`'s own stamps. Populations: `bl_cmt_n` 5 024.9 commits, **`bl_img_n` 47 873 image
  slots** (tr = **20.2 ns/slot**), `bl_buf_n` 47 712 buffer slots, `bl_smp_n` 11 151 samplers; `ds_ring_n` 2 646
  pooled sets (the other half push descriptors).
* **rt — 1 566 µs = 311.7 ns/draw.** Per colour target (`:881-973`): liveness re-check, `AcquireTargetView` fast path
  (`:795-868`, gate `rtfast`: ~15 compares incl. `view_info ==` and `SameTargetMetadata`, `bind_stamp` and
  `MetaEpoch` loads, `MarkGpuModified`), two `SetVulkanObjectNameF` (early-out, `vulkanCommon.h:34-50`), layout from
  `is_bound`, `attachment_layout/access` stores, **`Image::Transit`** (`image.cpp:230-282` → `GetBarriers`
  `:116-228`, a no-op compare in the steady state), extent, 3 counters + 2 gauges. Depth (`:974-1106`): the same view
  path, **`IsMetaCleared` = `TrackingSpinLock` + `std::map::find`** (`textureCache.cpp:3029-3040`,
  `textureCache.h:286,302`), `ClearMeta` when the guest clears depth, `TouchMeta` when an HTile clear is pending,
  feedback-loop scan over the pixel images, `Transit`. Populations: `rt_att` 12 507 colour attachments (**2.49/draw**),
  `rt_fast_ok` 17 391 + `rt_fast_no` 63 acquisitions ⇒ depth ≈ 4 947 (**0.98/draw**), **≈ 89.7 ns per target**.
* **vtx — 1 364 µs = 271.5 ns/draw.** Dominated by `BufferCache::ObtainBuffer` (`bufferCache.cpp:1126-1360`). **Both
  call sites pass `memoizable = false` and no `BufferId`** (`renderDraw.cpp:1408`, `:1717-1718`; defaults in
  `bufferCache.h:79-85`): they never take the `buffast` memo (`:1157-1227`) nor the upload-epoch fast path
  (`:1255-1301`, needs a valid `id`), so every call runs the combined tracker query (`:1307-1310`) and then
  `FindBuffer` + `TouchBuffer` + `SynchronizeBuffer` (`:1336-1341`, `DrawStat::BufSlow`). The non-`ObtainBuffer` part
  (static guards, range collect/sort/merge, `ClampRangeSize` memo) is ~60 ns/draw [I].
* **rec — 1 226 µs = 244.0 ns/draw.** `BeginRenderingImpl` early-returns on `m_render_state == state` (a defaulted
  `operator==` over ~9 `RenderAttachment`s, `renderTarget.h:49-58`, `context.cpp:325`) — true for ~96 % of draws
  (`rp_begin` 189/frame); `SetGraphicsDynamicParams` rebuilds viewport/scissor from registers (`calc_final_scissor`,
  the `ViewportIndex` scan over VS outputs `:419-423`) and runs ~10 `GraphicsStateChanged` memcmps (`render.h:181-199`);
  `HasShaderBufferWrites` walks `program.info.buffers` of every stage per draw; `tail.Commit` publishes with a
  seq_cst store (`commandRecorder.cpp:273`). Ring traffic: `rec_pub` 10 923 publishes, **`rec_pack_kb` 6 105 KiB a
  frame = ~1 244 B/draw** (bindings record ~1 KiB, commands record ~0.2 KiB) [M].

**Instrument share inside every span (adversarial note).** Each span contains one `PathLap::Mark` (≈ 4–5 ns: `cbmove`
measured a mark pair at 8.35 ns, ROADMAP §0.1 s.101) ⇒ ~25 µs/frame per span, and the lite-mode `FrameStats::Add`s on
the path (`frameStats.h:2044-2055`, "about 250 counts per draw"; inside rt alone ~10 per draw). An uninstrumented
build pays neither (`g_count_limit` = 0 ⇒ early return). The program measures speed in the instrumented mode, so the
spans are the right yardstick, but part of every per-draw ns below is counting, not work.

---

## 2. Already tried / closed on this path — checked so nothing below re-proposes it

| closed item | where recorded | what it removed | does it cover a candidate below? |
|---|---|---|---|
| `rtfast` = 1 (s59) | `docs/local-session-59.md` §4, `cpu-hot-path-map.md:392-397` | `FindRenderTarget/FindDepthTarget` + lock per target | **No** — A skips the per-draw loop that remains *after* `rtfast` |
| route C closure (s85/s86) | `ROADMAP.md:2675-2681`, `:2737-2745` | skipping repeated slots in `PrepareBindings`: `BindImage` arms `is_bound`, `ResetBindings` clears it every draw, `AcquireRenderTargets` reads it; `Transit` decides by a pre-state the oracle does not know | **No** — A/B read `is_bound` *after* this draw's `BindImage` and witness the pre-state with a serial (§3.1); they skip nothing in `PrepareBindings` |
| B9 set reuse (s58/59) | `cpu-hot-path-map.md:388-391, 441-449, 464-465` | reuse a whole descriptor set (dynamic offsets) — ceiling 0.3–0.45 ms | **No** — no candidate reuses a set |
| D4 draw merging (s86) | `ROADMAP.md:2873-2898` | `dm_same_nr + dm_push_nr` = 0.668 % | **No** — not proposed |
| `recbatch/recrelax/recpin` (s57/58/63), `recpubn` (s61–63), `recimg/recup/recgen` (s62/63) | `local-session-57.md:45`, `parallel-draw-path.md:660-720` | publish frequency / direct-record drains — cost moves to drains | **Yes for any "publish less" idea** — not re-proposed |
| `buffast` (s58) | `local-session-58.md:73`, `cpu-hot-path-map.md:426-430` | memo of `ObtainBuffer` for **binding** requests, "in the noise" | **No for C**: vertex/index sites pass `memoizable=false` (`renderDraw.cpp:1408,1718`) — they never took part in that measurement |
| `drawstate`, `snapkeep`, `bindpack` (items 1,4,9,11), `bindpack2` | s57, s84, s85 | state zeroing, snapshot copies, per-pipeline descriptor counts, duplicate upload epoch | not re-proposed |
| `KYTY_READONLY_DEPTH_ACCESS` (s40) | `renderDraw.cpp:1041-1055` | flip-flop of read-only depth access between Acquire and Commit | kept as is |

---

## 3. What repeats draw after draw, and what a skip must witness

### 3.1 The one witness that makes a skip of `Transit` provable: an image-state serial

`VulkanImageState` (`backing.state`, `backing.subresource_states`) is written in **three places only** (tree-wide grep
of `src/` for `.state =`, `state.layout =`, `subresource_states`): (1) `Image::GetBarriers` (`image.cpp:116-228`) —
every transition, including the tiler's direct call (`tiler.cpp:545-551`); (2) backing creation / recycling, which
resets the state to `eUndefined` / `initialLayout` without a barrier (`host_gpu/vma.cpp:399-400`, `:450-451`);
(3) swapchain image setup (`presentation/window/swapchain.cpp:275`, presentation images only, never a guest target).
Every barrier `Transit` produces is preceded by `EndRendering(why)` (`image.cpp:253-266`). So a global (relaxed)
**`image_state_serial`, incremented in `GetBarriers` whenever it emits a barrier or changes a state value, and at
sites (2)**, gives: *serial unchanged since point X ⇒ no guest image's layout/access changed since X*. (A new backing
also changes `backing.image`, which the per-target identity check of §3.2 compares anyway — the bump at (2) is
belt-and-braces.) Cost: one relaxed add per image barrier (`ibar` 420.9/frame [M]) — nothing on the hot path. This
answers the s85 objection ("`Transit` decides by a pre-state the oracle does not know"): the oracle does not need the
pre-state, only that it did not move.

Caveat found while reading (pre-existing, not introduced): in the partial / per-subresource path `GetBarriers`
overwrites the whole-image `state` at `:226` even when it emits no barrier. The serial must count a *value change*
of `state` there, not only barriers, or the witness has a hole.

### 3.2 rt — `AcquireRenderTargets` (candidate A: same-pass render-target memo)

**What repeats.** `rp_begin` 189 passes/frame against 5 025 draws [M] ⇒ **≥ 96 % of draws produce a `RenderState`
equal to the open pass** (that is exactly the `BeginRenderingImpl` early-return condition, `context.cpp:325`). For
those draws the whole loop recomputes the same views, layouts, extents and the same no-op `Transit`s.

**Hit condition (all must hold; evaluated before the call, after this draw's `PrepareBindings`):**
1. `image_state_serial` equal to the value captured at the **end of the previous draw's `AcquireRenderTargets`**
   (captured there, not at `BeginRendering`: the previous draw's `CommitBindings` may transit a sampled target after
   its Acquire — `descriptors.cpp:3767-3796` — and that must invalidate).
2. `TextureCache::MetaEpoch()` equal (HTile/DCC clear state; `textureCache.h:75-77`, 18 `BumpMetaEpoch` sites).
3. Same target set: per slot `image_id` (index + generation), `target_slot`, view desc — cheapest via an identity the
   resolver already has (the `ResolveRender*Target` memo hit, `rt_hits` 17 506/frame [M]) rather than a 2.7 KiB compare.
4. Per target image: `registered && !binding.needs_rebind`, `bind_stamp` unchanged (CPU write / buffer-modified ⇒
   `RefreshImage` work), `pending_levels == 0`, `binding.is_bound` equal to the memo (it selects `eGeneral` vs
   `eColorAttachmentOptimal`, `:943-944`; depth read-only combine `:1049-1052`), `IsGpuModified()` true.
5. Depth: `depth_clear_enable == false` (`ClearMeta` mutates, `:991-994`), `meta_clear == false` in the memo (so no
   `TouchMeta`, `:995-1002`), `depth_write_enable`/stencil flags equal, and the depth image **not** `is_bound`
   (otherwise the feedback scan `:1019-1035` must run — run it, it is cheap, and miss if its answer differs).
6. Not when the stencil plane path applies (`rtfast` already sends it slow, `:807-814`) or debug-dump config.

**What a hit must still do (side effects that are not idempotent across draws):**
* write `binding.attachment_layout/attachment_access` per target: `ResetBindings` clears the whole `binding` every draw
  (`descriptors.cpp:2025-2031`) and `CommitBindings` EXITs on `eUndefined` for a sampled target (`:3768-3769`);
* replay `RtAttachments`, `RtPixelsK`, `NoteMax(RtWidth/RtHeight)` and `SliceCensus::Image` — **`rt_att/rt_kpx` are
  the DRS watchdog of every scorer** (CLAUDE.md s67); dropping them would break admission, not rendering;
* restore `g_pass_extents` (`renderTarget.h:66-72`): a hit can still begin a pass (a pass can end without any image
  state change — `end_buf_upload` 18.8, `end_dispatch` 10.8 per frame [M]);
* return the memo'd `RenderState` (and, optionally, a flag that lets `BeginRenderingPacket` skip its compare when the
  pass-begin count is unchanged — this is where part of rec's `BeginRendering` cost goes).

**Why the closure of route C does not apply:** `is_bound` is read after this draw's `BindImage` (condition 4); the
pre-state is covered by condition 1. Nothing in `PrepareBindings` is skipped.

### 3.3 com — `CommitBindings`

* **Transit loop (967 µs, 20.2 ns/slot) — candidate B.** Per stage, the image list (ids, binding type, view format,
  `atomic_write`) and the per-image flags (`is_target`, `attachment_layout/access`, `force_general`, `shader_write`,
  `shader_write_plain`) decide the desired state. With the serial of §3.1 captured at the **end of the previous
  draw's transit loop, and recorded only if that loop emitted zero barriers**, an identical list ⇒ every `Transit` is
  again a no-op (repeated storage writes without an atomic pair always emit a barrier, `image.cpp:194-206`, so they
  never get recorded). Must still: store `binding.layout` per slot (feeds `MakeImageInfo`, `:3815`); keep the GDS
  branch (`:3697-3727`) outside the skip; skip `MaterializeDeferredDccClear` only if `MetaEpoch` is unchanged and its
  mask was 0 last time (it takes `m_lock` + `std::map::find` per DCC image, `:1856-1858`). The flags must be compared
  per slot (they are rebuilt per draw), so the Image object is still touched: the skip saves the call chain, not the
  memory traffic — roughly half of 20.2 ns.
* **Write-list (659.5 µs) — offload candidate D.** Its *shape* is a constant of the program (`bindpack` already
  caches counts on the pipeline, `:3485-3493`); only the infos change. It cannot be skipped (stream-ring offsets differ
  every draw — B9 / D4 findings), but it could be built on the record thread from compact inputs: the ring already
  carries every info by value (`commandRecorder.cpp:488-494`), so the producer would save the write-struct build and the
  per-write conversion in `PushBindings` (`:467-487`), not the bytes. Needs the program object alive until the record
  thread consumes the record (lifetime not established by this study) — a real risk.
* **Emit (479.9 µs).** `DescriptorHeap::Commit` + ~1 KiB memcpy + publish. Publish frequency is closed (§2). Nothing
  removable without changing the record format.

### 3.4 vtx — `AcquireVertexBuffers` / `PrepareIndexBuffer` (candidate C)

The same guest ranges are asked every time a mesh is drawn (depth pre-pass, G-buffer, shadow cascades). The existing
`buffast` memo (`bufferCache.cpp:1157-1227`, witness `RangeWriteEpoch` + `m_registration_epoch` + instance, verify
gate `buffastcheck`) is sound for read-only requests and would apply as is: vertex and index reads are read-only;
the stream-copy branch for small CPU-dirty ranges is never remembered (`:1326-1331`). Making the two call sites
memoizable is a two-argument change. What must be witnessed is exactly `buffast`'s witness; `ClampRangeSize` keeps its
own memo. Transient index data (`host_data`) stays on the stream path.

### 3.5 rec — the draw record (candidate E, hoists)

* `HasShaderBufferWrites` (`shaderResourceBarrier.cpp:92-115`) loops `program.info.buffers` of every stage on every
  draw; "has any written buffer" (and "all written are atomic") is a constant of the program ⇒ hoist to a flag on
  `CompiledShaderInfo`, keep the per-draw V# test only for programs that have written buffers. Zero correctness risk.
* `SetDrawDebugPhase` ×2–6, `LogDrawPhase` ×3–4 per draw (`renderDraw.cpp:1485-1497`, `debug.cpp:618`,
  `gpuCheckpoints.cpp:178-185`): each is a non-inline call whose body early-returns; one per-draw bool would do.
* `SetGraphicsDynamicParams`: recomputed from registers every draw; a memo needs a register-write generation that the
  command processor does not keep (none found); comparing the inputs costs about what computing them costs.
* `BeginRenderingPacket` compare: removable only together with A.

---

## 4. Ceilings (explicit arithmetic)

Per-draw costs = span / 5 025. "Hit cost" = work a skip must still do (§3), estimated from the loads/stores it keeps.

**A — same-pass render-target memo (rt).**
* Population: draws with no image-state change and no target change since the previous Acquire ≥ 5 025 − `ibar`
  420.9 − `end_target` 89.7 = **≈ 4 514 (89.8 %) [I]** (lower bound: several barriers can land on one draw).
* Hit cost: 3.46 targets × ~18 ns (id/generation, 5 field loads, 2 stores, counter replay) + ~15 ns fixed ≈ **77 ns [I]**.
* If hit draws cost the average: 4 514 × (311.7 − 77) ns = **1.06 ms**. Adversarial: the ~511 miss draws include the
  63 `rt_fast_no` finds, HTile clears and ~400 target barriers; if they cost 2× the average (≈ 600 ns), hit draws
  average (1 566 − 511 × 0.6) / 4 514 = 279 ns ⇒ 4 514 × (279 − 77) = **0.91 ms**.
* **Ceiling A = 0.9–1.1 ms [I]** — borderline against the 1 ms rule. Sub-item already inside it: `IsMetaCleared`
  lock + map find on 4 947 depth acquisitions × ~30–50 ns = 0.15–0.25 ms [I] (alone < 1 ms).

**B — commit-side transit skip under the same serial (com, tr).**
* Eligible slots: repeating slots 84.9 % [M s85: 40 664 / 47 885] × serial unchanged ~90 % [I] ≈ 76 %.
* Saving per eligible slot ≈ 20.2 − ~10 (flag compare + `binding.layout` store) ≈ 10 ns [I].
* 0.76 × 47 873 × 10.2 ns = **0.37 ms [I]** — **< 1 ms alone.**

**A + B + `BeginRendering` compare** (one mechanism, one witness): 0.9–1.1 + 0.37 + 4 836 × ~15 ns (0.07) ≈
**1.3–1.5 ms [I]**.

**C — vertex/index memo (vtx).** ObtainBuffer share ≤ 271.5 − ~60 = ~211 ns/draw (≤ 1.06 ms); hit cost ~25 ns ×
~1.5–2.5 calls ≈ 50 ns/draw [I]. At 100 % hits: 5 025 × (211 − 50) = **0.81 ms**; at the 47 % hit rate `buffast`
had on bindings [M s58]: **0.38 ms**. **Ceiling C ≤ 0.81 ms [I] — < 1 ms, plainly.** (Even the whole span, 1.36 ms,
cannot reach 1 ms of removal once the irreducible part is counted.)

**D — write-list offload to the record thread (com, wr + part of em).** 659.5 + ~10 writes × ~4 ns × 5 025 (0.20) −
residual producer cost of packing raw inputs (≈ 0.2–0.4) ≈ **0.5–0.8 ms [I]** — < 1 ms, and it is a structural change
(record format, program lifetime), not a removal.

**E — rec hoists.** `HasShaderBufferWrites` flag 20–40 ns/draw ⇒ 0.10–0.20 ms; debug-phase calls ~24 ns/draw ⇒ 0.12
ms; dynamic-state memo without a register generation ≤ 0.2–0.3 ms; together **0.4–0.6 ms [I]**, each item < 0.3 ms.
Individually below the noise of any ABBA the program has run (±75–92 µs A/A, ROADMAP §2 B).

---

## 5. Ranking — ceiling × probability of a correctness-safe removal

| rank | candidate | ceiling [tag] | P(safe) | score | comment |
|---|---|---|---|---|---|
| 1 | **A** same-pass RT memo | 0.9–1.1 ms [I] | 0.7 | ~0.7 | single-writer serial makes the `Transit` skip provable; side effects enumerable (§3.2) |
| 2 | A+B one mechanism | 1.3–1.5 ms [I] | 0.45 | ~0.63 | B adds DCC materialisation, `atomic_write`, partial-path subtleties |
| 3 | C vertex/index memo | ≤ 0.81 ms [I] | 0.85 | ~0.55 | the machinery and its verify gate exist; cannot reach 1 ms |
| 4 | E hoists | 0.4–0.6 ms [I] | 0.95 | ~0.5 | zero-risk, but only as a package, unmeasurable one by one |
| 5 | D write-list offload | 0.5–0.8 ms [I] | 0.5 | ~0.3 | structural; lifetime risk |

**Pursue first: A — but as a MEASUREMENT, not code.** Its correctness witness is **the image-state serial of §3.1**
(bumped in `Image::GetBarriers` and at the two backing-creation sites in `vma.cpp`) together with `MetaEpoch`, per-target `bind_stamp`/`registered`/`needs_rebind`/
`pending_levels`/`is_bound`/`IsGpuModified`, and the depth register flags; the verification criterion is that the full
`AcquireRenderTargets`, run beside every would-hit draw, returns a `RenderState` identical to the memo and moves neither
the serial nor `MetaEpoch` (§6, `sp_rt_bad = 0`). A track opens only if the [M] ceiling of A (or A+B, measured in the
same run) is ≥ 1 ms.

Plain statement: **com, vtx and rec each have no candidate whose removable part reaches 1 ms by reading; rt is the only
span with a borderline candidate.** If the census puts A+B below 1 ms, `mh_emit` is exhausted as a micro-track on this
scene (only structural moves — the record-thread offload D, or fewer operations — remain), and that should be recorded.

---

## 6. The single measurement that turns A (and B) into [M]

Smallest new instrument; everything else reuses arm M's gates (`pathlap mutsite bindlap`).

1. **`image_state_serial`** — relaxed counter in `Image::GetBarriers`, bumped when a barrier is produced or `state`
   changes value, and at the backing (re)creation sites `vma.cpp:399-400`/`:450-451` (§3.1). Always on (≈ 421
   adds/frame).
2. **Gate `spcen` (measurement only, default 0, last line of the gate table; run `check_gate_order.py`).** In
   `ExecutePreparedDraw`, after the vtx mark and before `AcquireRenderTargets`, evaluate the §3.2 hit condition against
   a memo recorded by the previous draw (never acting on it). Time the evaluation with its own pair of stamps into
   **`sp_chk_ns`/`sp_chk_n`** and keep it out of the rt span (restart the `PathLap` cursor after it, or book it to its
   own counter via `Mark`).
3. Close the rt span with `Mark(would ? PathEmRtHitNs : PathEmRtNs)` — counter selection only, **no extra timestamp**
   (new counters **`pl_em_rt_hit_ns`, `sp_rt_would`**).
4. After the real call: `sp_rt_bad` += would ∧ (returned `RenderState` ≠ memo'd one ∨ serial moved during the call ∨
   `MetaEpoch` moved); log `SpRtMismatch:` (≤ 40 lines). Then record the new memo (only if the pass is open and the call
   emitted no barrier).
5. Same idiom for B inside `CommitBindings`: per stage, would-hit ⇒ book that stage's transit lap to
   **`bl_tr_hit_ns`** (bindlap's existing stamp, counter selection only); `sp_tr_bad` += loop emitted a barrier or any
   slot's `binding.layout` differs from the memo.
6. **Pre-registered rule (to be written into ROADMAP before any code):**
   ceiling_A[M] = Σ`pl_em_rt_hit` − `sp_rt_would` × (`sp_chk_ns`/`sp_chk_n` + 10 ns × targets/draw);
   ceiling_B[M] = Σ`bl_tr_hit` − hits × 10 ns/slot; FAIL on any `sp_*_bad` > 0 (the mechanism is then unsound as
   designed); **track opens iff ceiling_A ≥ 1 ms, or ceiling_A + ceiling_B ≥ 1 ms with B's bad = 0**; otherwise record
   `mh_emit` micro-tracks as exhausted on Sky Garden.
7. One build, one sealed run: ABBA `spcen=0|1` with `pathlap=1 mutsite=1 bindlap=1` in both arms (the census prices
   itself), pinned, BDA regime stated, window 10–88.

For C, if ever wanted despite the < 1 ms ceiling: pass `memoizable=true` at `renderDraw.cpp:1408` and `:1718` under a
new gate and run `buffast=1 buffastcheck=1`; Δ`pl_em_vtx` in an ABBA is the [M] number (no new counter needed).

---

## 7. Summary table

| candidate | what repeats | ceiling µs [tag] | measurement to confirm | risk |
|---|---|---|---|---|
| **A** same-pass RT memo (rt) | ≥ 89.8 % of draws re-acquire the same targets of the open pass; every `Transit` a no-op | **900–1 100 [I]** | gate `spcen`: `pl_em_rt_hit_ns`, `sp_rt_would`, `sp_chk_ns`, `sp_rt_bad` (§6) | medium: serial must cover partial-path `state` writes and the `vma.cpp` backing resets; must replay `attachment_layout` stores (ResetBindings), DRS counters, `g_pass_extents`; no hit on depth clear / sampled depth |
| A: `IsMetaCleared` memo only | lock + `std::map` find per depth acquisition, answer stable under `MetaEpoch` | 150–250 [I] | subsumed by A | low |
| **B** commit transit skip (com tr) | 84.9 % of image slots repeat [M s85], transits no-op under the serial | **~370 [I]** (< 1 ms) | same gate: `bl_tr_hit_ns`, `sp_tr_bad` | medium-high: DCC materialisation, `atomic_write`, per-draw flags still loaded |
| A + B + `BeginRendering` compare | same witness | **1 300–1 500 [I]** | same run | as A and B |
| **C** vertex/index memo (vtx) | same guest VB/IB ranges every pass; sites bypass `buffast` (`memoizable=false`) | **≤ 810 [I]** (< 1 ms; 380 at 47 % hits) | `memoizable=true` at `renderDraw.cpp:1408,1718` + ABBA `buffast`, Δ`pl_em_vtx` | low (existing verified witness) |
| **D** write-list offload (com wr/em) | write shape constant per program; infos change | **500–800 [I]** (< 1 ms) | ABBA of an offload knob; `bl_wr` Δ | medium-high: record format, program lifetime |
| **E** rec hoists (`HasShaderBufferWrites` flag, debug phases, dyn-state) | program constants and debug flags re-evaluated per draw | **400–600 [I]** total, each < 300 (< 1 ms) | package ABBA only | low |
