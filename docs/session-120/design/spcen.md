# Session 120 — design of gate `spcen`: same-pass render-target memo census

Read-only code study on `C:/kyty/KytyPS5` at `996d565` (installed build `d3a981a2…`). No build, no run, no source
edited. Every file:line below was read in this tree. Reference designs: `C:/kyty/s119/designs/emit_parts.md`
(§3.1, §3.2, §3.3, §6 — this document is the exact form of its §6) and `witness_binding.md` (idioms only).

**What the gate does.** Per graphics draw, WITHOUT acting, it evaluates two memo conditions and books the measured
time of the work each memo would have skipped into separate would-hit counters, while the full work runs exactly as
today beside every would-hit:

* **A (rt)** — a memo of `AcquireRenderTargets` (`renderDraw.cpp:870-1133`) recorded by the previous draw of the
  open render pass: would it have returned the same `RenderState` with no side effect but the replayable stores?
* **B (tr)** — a per-stage memo of the image-transit loop of `CommitBindings` (`descriptors.cpp:3740-3816`): would
  every `MaterializeDeferredDccClear` + `Image::Transit` of that stage have been a no-op again?

`sp_rt_bad` / `sp_tr_bad` count every would-hit whose full work produced something the memo would not have reused.
The ceiling is the would-hit time minus the census's own check and a timed dry replay. Nothing the emulator decides
reads any census state.

**One decision this design takes (to be written into ROADMAP before code): the between-draws witness is a PER-IMAGE
state serial (`VulkanImage::state_serial`), and the s119 GLOBAL serial is kept as a nested, stricter variant.**
Reason: `AcquireRenderTargets` reads only the targets' state records and the transit loop only its own images'
(`GetBarriers` reads `backing.state`/`backing.subresource_states` of its own image only, `image.cpp:120-121`), so a
per-image serial is exactly as sound and does not lose a hit to an unrelated barrier (a storage image of the previous
draw, a commit-side transit of a non-target). The global serial still decides "the full work changed nothing" inside
the draw (all its writers hold the render mutex this draw holds, §1.1), and its would-hit population is reported
nested (`sp_rt_wg`, `pl_em_rt_hitg_ns`, `sp_tr_wg`, `bl_tr_hitg_ns`), so the s119 witness is measured too.

Tags: **[M]** measured (run named), **[I]** inferred from code + arithmetic. Populations quoted are `spk118` arm M
per frame as re-parsed in `emit_parts.md` §1.1.

---

## 1. Writer audit (what the witnesses must cover)

### 1.1 Image layout/access state — every writer (tree-wide search of `src/` for `subresource_states`,
`backing.state`, `.state =`, `state.layout`, `GetBarriers(`)

| # | writer | file:line | thread / lock | covered by |
|---|---|---|---|---|
| W1 | `Image::GetBarriers`, whole-image path: barrier + `state =` | `image.cpp:194-226` (early return with NO write at `:200-206`) | GuestGpu, or the present thread (below); render mutex | bump at `:226` (a barrier always exists on this path past `:206`) |
| W2 | `GetBarriers`, partial path: `subresource_states.resize` | `image.cpp:137-139` | same | bump (representation change) |
| W3 | `GetBarriers`, partial path: per-subresource write, only with a barrier | `image.cpp:167-186` | same | bump (`!barriers.empty()`) |
| W4 | `GetBarriers`, partial path: `subresource_states.clear()` when `!partial` | `image.cpp:190-192` | same | bump (representation change) |
| W5 | `GetBarriers`, partial path: **whole `state =` even with NO barrier** (s119 caveat) | `image.cpp:226` | same | bump iff the 4-field value changes (`pl_stage`, `access_mask`, `layout`, `atomic_write`) |
| W6 | `GraphicContext::CreateImage`, recycled backing: `state = {Undefined}`, `subresource_states.clear()` | `vma.cpp:399-400` | caller's (texture cache under render mutex; present thread under it at `swapchain.cpp:759`) | bump |
| W7 | `CreateImage`, new backing: `state = {initialLayout}`, `clear()` | `vma.cpp:450-451` | same | bump |
| W8 | `Presenter::Frame::Transit`: `image.state =`, `clear()` | `swapchain.cpp:274-275` | present thread | **not bumped**: `Frame::image` is the presenter's own `VulkanImage` (created `swapchain.cpp:237`, freed `:67`/`:222`); a guest `Image` reaches presentation only through `source.Transit(...)` at `swapchain.cpp:281` = W1–W5 |

Callers of `GetBarriers` (all reach W1–W5): `Image::Transit` `image.cpp:244-246`, `Image::Upload` `:302-304`,
`Image::Download` `:348-350`, the tiler `tiler.cpp:548-550`. The present thread transits a guest image
(`swapchain.cpp:281`) while holding the render mutex (`swapchain.cpp:759`, `LockGuard render_lock`), so it can only run
between two draws; the census draw holds the same mutex from before its check to after its `BeginRendering`
(`mh_emit` is one hold). No `std::swap`/move of a `backing` exists (`VulkanImage` is `KYTY_CLASS_NO_COPY`,
`graphicContext.h:166-168`); a freed `Image` bumps its `SlotVector` generation (`slotVector.h:84`), so an `ImageId`
(index + generation) never names a second image.

**Reader that makes W5 matter:** `descriptors.cpp:3815` `binding.layout = image.backing.state.layout` reads the
whole-image record right after the slot's transit — so it is observable. Proven below (§5.2) that after any
`Transit` `backing.state.layout == destination_layout`, which is what makes `binding.layout` a pure function of the
slot's inputs.

### 1.2 Per-draw image flags (`ImageBinding`, `image.h:42-52`) — every writer

`ResetBindings` clears them each draw (`descriptors.cpp:2025-2032`); rebuilt by `BindImage` (`:1782-1801`: `is_bound`,
`force_general`, `shader_write`, `shader_write_plain`), `BindRenderTarget` (`:2019-2023`: `is_target`),
`AcquireRenderTargets` (`renderDraw.cpp:945-946`, `:1056-1057`: `attachment_layout/access`). Re-find paths reset the
whole struct (`colorRenderTarget.cpp:147`, `depthRenderTarget.cpp:311`, `renderDraw.cpp:896`, `descriptors.cpp:2514`,
`:2699`); the texture cache sets `needs_rebind`/`is_target` on merges (`textureCache.cpp:954`, `:1065-1066`, `:1085`).
The census compares the live values of this draw, so no writer can slip past it.

### 1.3 Metadata (DCC / CMASK / HTile) state

`TextureCache::m_surface_metas` (`textureCache.h:302`) is documented to bump `m_meta_epoch` on every change
(`textureCache.h:303-307`); verified at every writer: `ClearMeta` `textureCache.cpp:3042-3055`, `TrackDccFill`
`:3063-3094`, `StampPendingDccFill` `:3105`, the pending-DCC adoption `:3200-3208` (it also writes
`image->info.metadata.kind` at `:3206`, the only image-level writer of `kind`), `TouchMeta` `:3219-3233`, `UnmapMemory`
`:3240-3246`, plus `:457`, `:1839-1948`, `:2389-2396`. `MetaClearMask`/`IsMetaCleared` (`:3017-3040`) are pure
functions of `m_surface_metas`. **`UnmapMemory` runs on a guest thread** (not under the render mutex), so
`MetaEpoch` can move concurrently — the census classifies such a case as a race, not as bad (§5).

### 1.4 Render-pass state

`CommandBuffer::m_rendering`/`m_render_state` (`render.h:289-290`) are written only by `BeginRenderingImpl`
(`context.cpp:324-406`, early return `:325-327` when open with an equal state) and `EndRenderingImpl` (`:447-499`).
Every barrier `Transit` records is preceded by `EndRendering(why)` (`image.cpp:253-266`), so inside one open pass no
barrier has been recorded since that pass began.

### 1.5 The render-target inputs `AcquireRenderTargets` reads

Per colour target: `RenderColorInfo` (`colorRenderTarget.h:14-31`), whose `memo_slot`/`memo_version` identify the
resolver memo entry the info came from; the version moves on every store (`colorRenderTarget.cpp:150`, `:170`) and on
the `PrepareGraphicsBindings` re-find (`descriptors.cpp:2712-2724`). **The only rewrite of a target without a version
move is the dead fallback re-find inside `AcquireRenderTargets` itself (`renderDraw.cpp:892-906`)** — the census
never records a memo from a draw where it ran (§3.4). Depth: `RenderDepthInfo` (`depthRenderTarget.h:21-45`), memo
keyed by every register read (`depthRenderTarget.cpp:281-299`), same version protocol (`:314`, `:332`); the only
post-resolution writer is `AcquireRenderTargets` itself (`renderDraw.cpp:998`, `:1081`: `depth_load_clear_enable`,
an output). The view comes from the rtfast record `m_color_view_fast[slot]` / `m_depth_view_fast`
(`render.h:565-580`), written only by `AcquireTargetView` (`renderDraw.cpp:853-865`).

---

## 2. Sites (file:line)

| id | file:line | role |
|---|---|---|
| S1 | `src/graphics/host_gpu/graphicContext.h:156-181` | `VulkanImageState`, `VulkanImage`: add the global serial, `VulkanImage::state_serial`, `NoteStateChange()` |
| S2 | `src/graphics/host_gpu/renderer/image/image.cpp:135-139, 190-192, 226` | bumps W2, W4, W1/W3/W5 |
| S3 | `src/graphics/host_gpu/vma.cpp:399-400, 450-451` | bumps W6, W7 |
| S4 | `src/graphics/host_gpu/renderer/context.cpp:331-332` | pass-begin serial (after the early return and `EndRenderingImpl`) |
| S5 | `src/graphics/host_gpu/renderer/render.h:135, 289-295` | `CommandBuffer::PassBeginSerial()`, `s_pass_begin_serial` |
| S6 | `src/graphics/host_gpu/renderer/render.h:311-590` | `SpCensusState` (before the class), `m_sp` member + five private methods + `friend class SpDrawScope` (before `:590`) |
| S7 | `src/graphics/host_gpu/renderer/renderDraw.cpp:835-838` | `AcquireTargetView` slow path: `t_sp_rt_slow` |
| S8 | `src/graphics/host_gpu/renderer/renderDraw.cpp:893-895` | `AcquireRenderTargets` dead re-find: `t_sp_rt_refind` |
| S9 | `src/graphics/host_gpu/renderer/renderDraw.cpp:2437-2452` | latch + A check before, A post after `AcquireRenderTargets` |
| S10 | `src/graphics/host_gpu/renderer/renderDraw.cpp:2675` (packet) and `:2837` (direct) | A: pass-restart check + memo validation around `BeginRendering` |
| S11 | `src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3509-3525` | B: read the latch, arm `cb_timed` |
| S12 | `descriptors.cpp:3686-3690` | B: stage index |
| S13 | `descriptors.cpp:3734-3740` and `:3817` | B: check before the loop, post after its `cb_lap` |
| S14 | `descriptors.cpp:1866-1868` | `MaterializeDeferredDccClear` past `mask == 0`: `t_sp_dcc_pending` |
| S15 | `src/common/frameStats.h:1943` (append before `Count`) and `:2355-2385` (`PathLap`) | 51 counters; `PathLap::MarkSplit`, `PathLap::Running` |
| S16 | `src/graphics/presentation/videoOut.cpp:2582-2583` (after `{"sc_ns", …}`) | 51 print rows, all `micros = false` |
| S17 | `src/common/gates.h:413-414`, `src/common/gates.cpp:282-285` | gate `SamePassCensus` / `"spcen"`, LAST rows |

None of these files is in the translation-cache signature (`src/generate_version.cmake:41-56`: `src/graphics/shader/**`
+ `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h` per `CMakeLists.txt:155-156`). No new `.cpp` file (no
CMake configure needed).

---

## 3. Exact code plan (pseudo-diffs)

### 3.1 S1 — the serials (always counted)

```cpp
+#include <atomic>                                                   // graphicContext.h:9-14 has no <atomic>
 struct VulkanImageState { ... };                                   // graphicContext.h:156-163
+// Session 120, gate "spcen" (MEASUREMENT ONLY, ALWAYS counted - C:/kyty/s120/design/spcen.md s.1): the image
+// layout/access state machine moved. Global serial and per-backing serial; both move together, in
+// Image::GetBarriers when it changes a state record (a barrier, a value change of `state`, a resize or clear of
+// `subresource_states`) and in GraphicContext::CreateImage. Write-only on every path but the census.
+inline std::atomic<uint64_t> g_image_state_serial {0};
+[[nodiscard]] inline uint64_t ImageStateSerial() noexcept {
+	return g_image_state_serial.load(std::memory_order_relaxed);
+}
 struct VulkanImage {
 	...
 	VulkanImageState              state;
 	std::vector<VulkanImageState> subresource_states;
+	uint64_t                      state_serial = 0; // session 120: see g_image_state_serial
 	VmaAllocation                allocation = nullptr;
+	void NoteStateChange() noexcept {
+		state_serial++; // written under the render mutex like `state` itself
+		g_image_state_serial.fetch_add(1, std::memory_order_relaxed);
+	}
 };
```

### 3.2 S2 — `Image::GetBarriers` (`image.cpp:116-228`)

```cpp
 	Barriers barriers;
+	bool     representation_moved = false; // session 120, gate "spcen" (always)
 	if (partial || has_subresource_states) {
 		if (!has_subresource_states) {
 			subresource_states.resize(info.resources.levels * info.resources.layers, state);
+			representation_moved = true;
 		}
 		... loop unchanged (a subresource record is written only with a barrier, :167-186) ...
 		if (!partial) {
 			subresource_states.clear();
+			representation_moved = true;
 		}
 	} else {
 		... unchanged, including the early `return {};` at :205 (no write, no bump) ...
 		barriers.push_back(barrier);
 	}
-	state = {destination_stage, destination_access, destination_layout, atomic_write};
+	const VulkanImageState next {destination_stage, destination_access, destination_layout, atomic_write};
+	const bool value_moved = state.pl_stage != next.pl_stage || state.access_mask != next.access_mask ||
+	                         state.layout != next.layout || state.atomic_write != next.atomic_write;
+	if (!barriers.empty() || representation_moved || value_moved) {
+		backing.NoteStateChange();
+		Common::FrameStats::Add(Common::FrameStats::Counter::ImageStateSerialBumps, 1);
+		if (barriers.empty() && !representation_moved) {
+			Common::FrameStats::Add(Common::FrameStats::Counter::ImageStateSerialValue, 1); // W5 alone
+		}
+	}
+	state = next;
 	return barriers;
```

### 3.3 S3, S4, S5 — backing creation and the pass-begin serial

```cpp
 // vma.cpp:399-400 and again at :450-451
 	image.state      = {.layout = vk::ImageLayout::eUndefined};   // (:450: initialLayout)
 	image.subresource_states.clear();
+	image.NoteStateChange(); // session 120, gate "spcen" (always): the backing starts over
+	Common::FrameStats::Add(Common::FrameStats::Counter::ImageStateSerialBumps, 1);

 // context.cpp:331-332
 	EndRenderingImpl(RenderPassEnd::State, packet);
+	s_pass_begin_serial.fetch_add(1, std::memory_order_relaxed); // session 120, gate "spcen" (always)
 	Common::FrameStats::Add(Common::FrameStats::Counter::RenderPassBegins, 1);

 // render.h, class CommandBuffer
 	[[nodiscard]] bool IsRendering() const noexcept { return m_rendering; }
+	// Session 120, gate "spcen": moves at every REAL pass begin (BeginRenderingImpl past its early return) of any
+	// command buffer. Always counted; read only by the census.
+	[[nodiscard]] static uint64_t PassBeginSerial() noexcept {
+		return s_pass_begin_serial.load(std::memory_order_relaxed);
+	}
 ...
+	static inline std::atomic<uint64_t> s_pass_begin_serial {0};
```

### 3.4 S6 — census state (render.h, before `class RenderExecutor`)

```cpp
+// Session 120, gate "spcen" (MEASUREMENT ONLY, spcen.md). Nothing outside the census reads any of this.
+inline constinit thread_local bool t_sp_rt_armed    = false; // AcquireRenderTargets of an armed draw is running
+inline constinit thread_local bool t_sp_rt_slow     = false; // ... it took AcquireTargetView's slow path
+inline constinit thread_local bool t_sp_rt_refind   = false; // ... it took its dead-image re-find
+inline constinit thread_local bool t_sp_dcc_armed   = false; // an armed stage's transit loop is running
+inline constinit thread_local bool t_sp_dcc_pending = false; // ... it met a non-zero DCC clear mask
+struct SpRtTarget {
+	ImageId          id;
+	uint32_t         slot = 0, memo_slot = UINT32_MAX, memo_version = 0; // slot: target_slot, UINT32_MAX = depth
+	vk::Image        backing = nullptr;
+	vk::ImageView    view    = nullptr;         // == the rtfast record's view (the value Acquire returned)
+	uint32_t         stamp = 0;                 // bind_stamp == the rtfast record's stamp
+	uint32_t         source_first_level = 0;
+	uint64_t         source_size  = 0;
+	uint64_t         state_serial = 0;          // backing.state_serial after the recording Acquire
+	uint32_t         htile_mask = 0;            // depth only
+	bool             is_bound = false;          // binding.is_bound seen by the recording Acquire (colour)
+	vk::ImageLayout  att_layout = vk::ImageLayout::eUndefined; // binding.attachment_layout it stored
+	vk::AccessFlags2 att_access;                                // binding.attachment_access it stored
+	uint32_t         w = 0, h = 0; uint64_t kpx = 0;            // colour Extent(), for the counter replay
+};
+struct SpRtMemo {
+	bool pending = false, valid = false, has_depth = false;
+	uint32_t color_count = 0;
+	std::array<SpRtTarget, RENDER_COLOR_ATTACHMENTS_MAX + 1> t {}; // colours in order, depth last
+	uint64_t serial_end = 0, meta_end = 0, pass_serial = 0;
+	RenderState state;  PassExtentWitness extents;
+};
+struct SpTrSlot {
+	ImageId id; uint32_t base_level = 0, level_count = 0, base_layer = 0, layer_count = 0;
+	uint8_t storage = 0, flags = 0;                   // flags: SpTrFlags() below
+	vk::ImageLayout att_layout = vk::ImageLayout::eUndefined, result = vk::ImageLayout::eUndefined;
+	vk::AccessFlags2 att_access; uint64_t state_serial = 0;
+};
+inline constexpr uint32_t kSpTrSlots = 32;
+struct SpTrMemo {
+	bool valid = false, atomimg = false; uint32_t n = 0; uint64_t serial_end = 0, meta_end = 0;
+	std::array<SpTrSlot, kSpTrSlots> s {};
+};
+struct SpTrStage { bool would = false, would_g = false, atomimg = false, open0 = false; uint64_t serial0 = 0, meta0 = 0; };
+struct SpCensusState {
+	bool armed = false, would_rt = false, would_rt_g = false, open0 = false;
+	uint32_t draw_bad = 0, rt_logged = 0, tr_logged = 0;
+	uint64_t serial0 = 0, meta0 = 0;
+	std::array<Image*, RENDER_COLOR_ATTACHMENTS_MAX + 1> img {};
+	std::array<uint32_t, RENDER_COLOR_ATTACHMENTS_MAX + 1> stamp0 {};
+	SpRtMemo rt;  std::array<SpTrMemo, 4> tr {};  // 4 = max stages of a draw (descriptor_stages, renderDraw.cpp:2214)
+	struct Sink { RenderState state; PassExtentWitness extents; std::array<uint32_t, 9> layout {}; std::array<uint64_t, 9> access {};
+	              uint32_t usage = 0, gpu_mod = 0, w = 0, h = 0; std::array<uint32_t, kSpTrSlots> tr_layout {}; } sink;
+};
 class RenderExecutor {
 ...
+	// Session 120, gate "spcen": allocated at the first armed draw (about 7 KiB), never at gate 0.
+	std::unique_ptr<SpCensusState> m_sp;
+	void      SpRtCheck(CommandBuffer&, const RenderColorInfo*, uint32_t, const RenderDepthInfo&);
+	void      SpRtPost(CommandBuffer&, const RenderColorInfo*, uint32_t, const RenderDepthInfo&, const RenderState&);
+	void      SpRtAfterBegin(bool open_before, uint64_t pass_before);
+	SpTrStage SpTrCheck(uint32_t k, const PreparedBindings&, uint32_t n, const CommandBuffer&);
+	void      SpTrPost(uint32_t k, const PreparedBindings&, uint32_t n, const SpTrStage&, uint64_t loop_ns,
+	                   const CommandBuffer&);
+	// Read TextureCache privates (m_slot_images, m_readback_linear_images) exactly as AcquireTargetView does:
+	// SpRtConfigOk = rtfast && !graphics_debug_dump_enabled() && !cache.m_readback_linear_images && !slicecen;
+	// SpStencilKept = the stencil_kept lambda of renderDraw.cpp:807-814 on the recorded fast.stencil_record.
+	[[nodiscard]] static bool SpRtConfigOk(const TextureCache& cache);
+	[[nodiscard]] static bool SpStencilKept(const TextureCache& cache, const RenderDepthInfo& depth,
+	                                        const TargetViewFast& fast, ImageId id);
+	friend class SpDrawScope;
 };
```

### 3.5 S7, S8, S14 — flags on rare paths (TLS test only; nothing at gate 0 on the common path)

```cpp
 // renderDraw.cpp:835-838 (AcquireTargetView, after the rtfast fast path failed)
 	FS::Add(FS::Counter::RtFastNo, 1);
+	if (t_sp_rt_armed) { t_sp_rt_slow = true; }
 // renderDraw.cpp:893-895 (AcquireRenderTargets dead fallback)
 	    old_image->binding.needs_rebind) {
+		if (t_sp_rt_armed) { t_sp_rt_refind = true; }
 // descriptors.cpp:1866-1868 (MaterializeDeferredDccClear)
 	if (mask == 0) {
 		return;
 	}
+	if (t_sp_dcc_armed) { t_sp_dcc_pending = true; }
```

### 3.6 S15 — `PathLap` additions (`frameStats.h:2355-2385`)

```cpp
+	// Session 120, gate "spcen": Mark(total) that also charges the SAME interval to up to two nested
+	// would-hit subsets, so `total` keeps its meaning in both arms of a schedule.
+	static void MarkSplit(Counter total, Counter hit, bool in_hit, Counter hit_g, bool in_hit_g) {
+		if (Detail::t_path_t0 != 0) {
+			const auto now = NowNs();
+			const auto spent = now - Detail::t_path_t0;
+			Add(total, spent);
+			if (in_hit)   { Add(hit, spent); }
+			if (in_hit_g) { Add(hit_g, spent); }
+			Detail::t_path_t0 = now;
+		}
+	}
+	[[nodiscard]] static bool Running() noexcept { return Detail::t_path_t0 != 0; }
```

### 3.7 S9 — A around `AcquireRenderTargets` (`renderDraw.cpp:2437-2452`)

```cpp
+// renderDraw.cpp, namespace Libs::Graphics - NOT an anonymous namespace: it is the friend render.h names.
+class SpDrawScope {
+public:
+	SpDrawScope(RenderExecutor& ex, bool on): m_ex(ex), m_on(on) {
+		if (!on) { return; }
+		if (!ex.m_sp) {
+			ex.m_sp = std::make_unique<SpCensusState>();
+			LOGF("SpCensus: mode 1 rt_targets=%u tr_slots=%u\n", RENDER_COLOR_ATTACHMENTS_MAX + 1, kSpTrSlots);
+		}
+		ex.m_sp->armed = true;
+	}
+	~SpDrawScope() {
+		if (m_on) { m_ex.m_sp->armed = m_ex.m_sp->would_rt = m_ex.m_sp->would_rt_g = false; t_sp_rt_armed = false; }
+	}
+	[[nodiscard]] bool Armed() const noexcept { return m_on; }
+private:
+	RenderExecutor& m_ex; bool m_on;
+};

 	lap.Mark(Common::FrameStats::Counter::DrawVertexNs);
 	Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmVtxNs);
 	DrawStatTail();
+	// Session 120, gate "spcen" (MEASUREMENT ONLY): latch the gate ONCE for this draw - CommitBindings and the
+	// BeginRendering sites read the latch, never the gate (the s97 lesson) - and evaluate WITHOUT ACTING whether a
+	// same-pass render-target memo could skip the AcquireRenderTargets below. Gate first: FrameStats::Enabled() is
+	// out of line (frameStats.cpp:160-164) and must not run at gate 0.
+	SpDrawScope sp_scope(*this, !bind_floor &&
+	                                Common::Gates::Enabled(Common::Gates::Gate::SamePassCensus) &&
+	                                Common::FrameStats::Enabled());
+	if (sp_scope.Armed()) {
+		SpRtCheck(buffer, state.color_info, state.color_count, state.depth_info);
+		Common::FrameStats::PathLap::MarkSplit(Common::FrameStats::Counter::PathEmSpChkNs,
+		                                       Common::FrameStats::Counter::SpRtChkHitNs, m_sp->would_rt,
+		                                       Common::FrameStats::Counter::SpRtChkHitNs, false);
+	}
 	const auto rendering = ... unchanged (both bind_floor arms) ...;
 	lap.Mark(Common::FrameStats::Counter::DrawAcquireRtNs);
-	Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmRtNs);
+	if (sp_scope.Armed()) {
+		Common::FrameStats::PathLap::MarkSplit(Common::FrameStats::Counter::PathEmRtNs,
+		                                       Common::FrameStats::Counter::PathEmRtHitNs, m_sp->would_rt,
+		                                       Common::FrameStats::Counter::PathEmRtHitGNs, m_sp->would_rt_g);
+		SpRtPost(buffer, state.color_info, state.color_count, state.depth_info, rendering);
+		Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmSpPostNs);
+	} else {
+		Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmRtNs); // gate 0: byte-for-byte today
+	}
```

`SpRtCheck` (renderDraw.cpp, reads only; first failing reason wins, order fixed = counter order):

```cpp
void RenderExecutor::SpRtCheck(CommandBuffer& buffer, const RenderColorInfo* colors, uint32_t color_count,
                               const RenderDepthInfo& depth) {
	namespace FS = Common::FrameStats;
	auto& sp = *m_sp;  auto& m = sp.rt;  auto& cache = m_context.GetTextureCache();
	if (m.pending) { m.pending = false; m.valid = false; }  // the recorder never reached BeginRendering
	sp.serial0  = ImageStateSerial();
	sp.meta0    = cache.MetaEpoch();
	sp.open0    = buffer.IsRendering();
	sp.draw_bad = 0;
	const bool     has_depth = static_cast<bool>(depth.image_id);
	const uint32_t n         = color_count + (has_depth ? 1u : 0u);
	enum : uint32_t { None, Memo, Cfg, DepthClear, Meta, Ids, Live, Serial, Bound, DepthSampled, Pass };
	uint32_t why = None;
	if (!m.valid)                                        why = Memo;
	else if (!SpRtConfigOk(cache))                       why = Cfg;   // rtfast on, no debug dump, no linear
	                                                                  // readback, slicecen off
	else if (has_depth && depth.depth_clear_enable)      why = DepthClear;
	else if (sp.meta0 != m.meta_end)                     why = Meta;
	else if (color_count != m.color_count || has_depth != m.has_depth) why = Ids;
	else {
		for (uint32_t i = 0; i < n && why == None; i++) {
			const bool      d    = i == color_count;
			const auto&     t    = m.t[i];
			const ImageId   id   = d ? depth.image_id : colors[i].image_id;
			const uint32_t  slot = d ? UINT32_MAX : colors[i].target_slot;
			const uint32_t  ms   = d ? depth.memo_slot : colors[i].memo_slot;
			const uint32_t  mv   = d ? depth.memo_version : colors[i].memo_version;
			if (id != t.id || slot != t.slot || ms == UINT32_MAX || ms != t.memo_slot || mv != t.memo_version) {
				why = Ids; break;
			}
			auto*       img   = cache.m_slot_images.try_get(id);
			const auto& fast  = d ? m_depth_view_fast : m_color_view_fast[slot];
			const auto  stamp = img != nullptr ? img->bind_stamp.load(std::memory_order_acquire) : 0u;
			// AcquireTargetView's fast predicate (renderDraw.cpp:815-823) restated against the memo: desc,
			// view_info and metadata are equal by the memo identity above, so only the live parts are read.
			if (img == nullptr || !img->registered || img->depth_id || img->binding.needs_rebind ||
			    img->pending_levels != 0 || img->backing.image != t.backing || stamp != t.stamp ||
			    img->source_size != t.source_size || img->source_first_level != t.source_first_level ||
			    !fast.valid || fast.image_id != id || fast.backing != t.backing || fast.view != t.view ||
			    fast.stamp != t.stamp ||
			    (d && (img->info.htile_clear_mask != t.htile_mask || !SpStencilKept(cache, depth, fast, id)))) {
				why = Live; break;                 // SpStencilKept = renderDraw.cpp:807-814, reads only
			}
			if (img->backing.state_serial != t.state_serial) { why = Serial; break; }
			if (!d && img->binding.is_bound != t.is_bound) { why = Bound; break; }
			sp.img[i] = img;  sp.stamp0[i] = stamp;
		}
		if (why == None && has_depth && sp.img[color_count]->binding.is_bound) why = DepthSampled;
		if (why == None && !(sp.open0 && CommandBuffer::PassBeginSerial() == m.pass_serial)) why = Pass;
	}
	sp.would_rt   = why == None;
	sp.would_rt_g = sp.would_rt && sp.serial0 == m.serial_end;       // the s119 global witness, nested
	FS::Add(FS::Counter::SpRtDraws, 1);
	if (!FS::PathLap::Running()) { FS::Add(FS::Counter::SpRtUntimed, 1); }
	if (sp.would_rt) {
		FS::Add(FS::Counter::SpRtWould, 1);
		FS::Add(FS::Counter::SpRtTargets, n);
		if (sp.would_rt_g) { FS::Add(FS::Counter::SpRtWouldGlobal, 1); }
	} else {
		FS::Add(static_cast<FS::Counter>(static_cast<uint32_t>(FS::Counter::SpRtMissMemo) + why - 1), 1);
	}
	t_sp_rt_slow = t_sp_rt_refind = false;
	t_sp_rt_armed = true;
}
```

`SpRtPost` (after the full `AcquireRenderTargets`; the bad check, the timed dry replay, the record):

```cpp
void RenderExecutor::SpRtPost(CommandBuffer& buffer, const RenderColorInfo* colors, uint32_t color_count,
                              const RenderDepthInfo& depth, const RenderState& rendering) {
	namespace FS = Common::FrameStats;
	auto& sp = *m_sp;  auto& m = sp.rt;  auto& cache = m_context.GetTextureCache();
	t_sp_rt_armed = false;
	const uint64_t serial1 = ImageStateSerial();
	const uint64_t meta1   = cache.MetaEpoch();
	const bool     open1   = buffer.IsRendering();
	const bool     fallback = t_sp_rt_slow || t_sp_rt_refind;
	const bool     has_depth = static_cast<bool>(depth.image_id);
	const uint32_t n = color_count + (has_depth ? 1u : 0u);
	if (sp.would_rt) {
		uint32_t bad = 0;                                             // bits: section 5.1
		if (!(rendering == m.state))  { bad |= 0x01; }               // R: the RenderState it returned
		if (serial1 != sp.serial0)    { bad |= 0x02; }               // S: any image state written / barrier
		if (fallback)                 { bad |= 0x04; }               // F: FindRenderTarget/FindDepthTarget/re-find
		for (uint32_t i = 0; i < n; i++) {
			const ImageId id = i == color_count ? depth.image_id : colors[i].image_id;
			if (id != m.t[i].id) { bad |= 0x08; }                    // I: target identity after the call
			if (sp.img[i]->binding.attachment_layout != m.t[i].att_layout ||
			    sp.img[i]->binding.attachment_access != m.t[i].att_access) { bad |= 0x10; } // X: side stores
		}
		if (has_depth && depth.depth_load_clear_enable) { bad |= 0x10; }
		if (g_pass_extents.max_width != m.extents.max_width || g_pass_extents.max_height != m.extents.max_height ||
		    g_pass_extents.true_kpx != m.extents.true_kpx) { bad |= 0x10; }
		if (sp.open0 && !open1)       { bad |= 0x20; }               // P: the call closed the open pass
		if (bad != 0) {
			bool raced = meta1 != sp.meta0;                          // guest UnmapMemory (section 1.3)
			for (uint32_t i = 0; i < n; i++) {
				raced |= sp.img[i]->bind_stamp.load(std::memory_order_acquire) != sp.stamp0[i]; // guest fault
			}
			sp.draw_bad = bad;
			if (raced) { FS::Add(FS::Counter::SpRtRace, 1); }
			else {
				FS::Add(FS::Counter::SpRtBad, 1);
				if (sp.rt_logged++ < 40) {
					LOGF("SpRtMismatch: frame=%d why=0x%02x colors=%u depth=%u serial=%" PRIu64 "->%" PRIu64
					     " meta=%" PRIu64 "->%" PRIu64 " fallback=%u\n", m_context.GetGpu().GetFrameNum(), bad,
					     color_count, has_depth ? 1u : 0u, sp.serial0, serial1, sp.meta0, meta1, fallback ? 1u : 0u);
				}
			}
		}
		// Dry replay: the loads and stores a real hit must still make (section 5.3), into sp.sink, timed.
		const auto r0 = FS::NowNs();
		sp.sink.state = m.state;  sp.sink.extents = m.extents;
		for (uint32_t i = 0; i < n; i++) {
			const auto& t = m.t[i];
			sp.sink.layout[i] = static_cast<uint32_t>(t.att_layout);
			sp.sink.access[i] = static_cast<uint64_t>(t.att_access);
			sp.sink.gpu_mod  += sp.img[i]->IsGpuModified() ? 1u : 0u;   // MarkGpuModified's load + branch
			sp.sink.usage    |= 1u << i;                                 // usage.render_target / depth_target
			if (i < color_count) {
				FS::Add(FS::Counter::SpRtRepAtt, 1);                     // = RtAttachments
				FS::Add(FS::Counter::SpRtRepKpx, t.kpx);                 // = RtPixelsK
				sp.sink.w = std::max(sp.sink.w, t.w);  sp.sink.h = std::max(sp.sink.h, t.h); // = NoteMax x2
			}
		}
		FS::Add(FS::Counter::SpRtRepNs, FS::NowNs() - r0);
	}
	// Record - strict: the call changed nothing and took no fallback (s119: "only if it emitted no barrier").
	const bool depth_sampled = has_depth && cache.m_slot_images[depth.image_id].binding.is_bound;
	bool rec_ok = sp.draw_bad == 0 && SpRtConfigOk(cache) && serial1 == sp.serial0 && meta1 == sp.meta0 &&
	              !fallback && !depth_sampled && !(has_depth && (depth.depth_clear_enable ||
	                                                             depth.depth_load_clear_enable));
	for (uint32_t i = 0; i < n && rec_ok; i++) {
		rec_ok = (i == color_count ? depth.memo_slot : colors[i].memo_slot) != UINT32_MAX;
	}
	m.valid = false;  m.pending = false;
	if (!rec_ok) { return; }
	if (!sp.would_rt) {
		// full record from THIS draw: ids, slots, memo identity, and per target the live post-call values
		// (backing.image, the rendering view, bind_stamp, source_*, backing.state_serial, htile mask,
		// binding.is_bound / attachment_layout / attachment_access, Extent() and its kpx); plus
		// color_count, has_depth, state = rendering, extents = g_pass_extents.
		...
	}                                                  // a clean would-hit keeps the content (it is equal by 5.1)
	m.serial_end = serial1;  m.meta_end = meta1;
	m.pending = true;                                  // valid only once BeginRendering pins the pass (S10)
}
```

### 3.8 S10 — around `BeginRendering` (packet `renderDraw.cpp:2675`, direct `:2837`)

```cpp
+	const bool     sp_open = sp_scope.Armed() && buffer.IsRendering();
+	const uint64_t sp_pass = sp_scope.Armed() ? CommandBuffer::PassBeginSerial() : 0;
 	buffer.BeginRenderingPacket(rendering);             // direct path: buffer.Scheduler().BeginRendering(rendering)
+	if (sp_scope.Armed()) {
+		SpRtAfterBegin(sp_open, sp_pass);
+	}

void RenderExecutor::SpRtAfterBegin(bool open_before, uint64_t pass_before) {
	namespace FS = Common::FrameStats;
	auto& sp = *m_sp;
	const uint64_t pass_after = CommandBuffer::PassBeginSerial();
	if (sp.would_rt && pass_after != pass_before) {
		FS::Add(FS::Counter::SpRtRestart, 1);        // diagnostic: something closed the pass after the check
		if (open_before && sp.draw_bad == 0) {       // an OPEN pass equal to the memo cannot restart (section 5.1 P2)
			sp.draw_bad = 0x40;
			FS::Add(FS::Counter::SpRtBad, 1);
			// SpRtMismatch: line with why=0x40, as above
		}
	}
	if (sp.rt.pending) {
		sp.rt.pass_serial = pass_after;  sp.rt.valid = true;  sp.rt.pending = false;
		FS::Add(FS::Counter::SpRtRecords, 1);
	}
}
```

### 3.9 S11–S13 — B in `CommitBindings`

```cpp
 	const bool bind_lap     = Common::Gates::Enabled(Common::Gates::Gate::BindLap);          // :3509
+	// Session 120, gate "spcen" (MEASUREMENT ONLY): the DRAW's latch (renderDraw.cpp SpDrawScope), never a second
+	// gate read. Graphics commits of armed draws only; the floor has nothing to transit.
+	const bool sp_tr = m_sp != nullptr && m_sp->armed && !bind_floor &&
+	                   pipeline_bind_point == vk::PipelineBindPoint::eGraphics;
 ...
-	const bool cb_timed     = (Common::DrawStat::On() || bind_lap || merge_cost) &&
+	const bool cb_timed     = (Common::DrawStat::On() || bind_lap || merge_cost || sp_tr) &&   // :3522
 	                      pipeline_bind_point == vk::PipelineBindPoint::eGraphics;
 ...
+	uint32_t sp_next_stage = 0;
 	for (auto* prepared: prepared_bindings) {                                                    // :3686
+		const uint32_t sp_k = sp_next_stage++;
 		... GDS block unchanged ...
 		const uint32_t floor_transit_count = ...;                                                // :3734
 		EXIT_IF(descriptors.images.size() < floor_transit_count);
+		SpTrStage sp_st {};
+		if (sp_tr) {
+			cb_lap(cb_transit);        // prologue / GDS block stay in bl_tr exactly as before (laps are additive)
+			sp_st = SpTrCheck(sp_k, descriptors, floor_transit_count, buffer);   // reads only; arms t_sp_dcc_*
+			const auto now = FS::NowNs();
+			FS::Add(FS::Counter::SpTrChkNs, now - cb_t);
+			if (sp_st.would) { FS::Add(FS::Counter::SpTrChkHitNs, now - cb_t); }
+			cb_t = now;                // the check is not transit time
+		}
 		for (uint32_t i = 0; i < floor_transit_count; i++) { ... unchanged ... }                // :3740-3816
+		const uint64_t sp_tr_before = cb_transit;
 		cb_lap(cb_transit);                                                                      // :3817
+		if (sp_tr) {
+			SpTrPost(sp_k, descriptors, floor_transit_count, sp_st, cb_transit - sp_tr_before, buffer);
+			const auto now = FS::NowNs();
+			FS::Add(FS::Counter::SpTrPostNs, now - cb_t);
+			cb_t = now;                // the post is not write-list time
+		}
```

`SpTrCheck` / `SpTrPost` (descriptors.cpp):

```cpp
static uint8_t SpTrFlags(const Image& img) noexcept {   // every per-image input of the transit decision
	return (img.info.data.Empty() ? 0x01 : 0) | (img.binding.is_target ? 0x02 : 0) |
	       (img.binding.force_general ? 0x04 : 0) | (img.binding.shader_write ? 0x08 : 0) |
	       (img.binding.shader_write_plain ? 0x10 : 0) | (img.info.IsDepth() ? 0x20 : 0) |
	       (img.registered ? 0x40 : 0) | (img.depth_id ? 0x80 : 0);   // the last two: DCC early return, :1847-1850
}

SpTrStage RenderExecutor::SpTrCheck(uint32_t k, const PreparedBindings& d, uint32_t n, const CommandBuffer& buffer) {
	namespace FS = Common::FrameStats;
	auto& memo = m_sp->tr[k];  auto& cache = m_context.GetTextureCache();
	SpTrStage st {};
	st.serial0 = ImageStateSerial();  st.meta0 = cache.MetaEpoch();  st.open0 = buffer.IsRendering();
	st.atomimg = Common::Gates::Enabled(Common::Gates::Gate::AtomicImageBarrier);  // GetBarriers reads it per call
	enum : uint32_t { None, Big, Memo, Meta, Shape, Serial, Flags };
	uint32_t why = None;
	if (n > kSpTrSlots)                                  why = Big;
	else if (!memo.valid || memo.atomimg != st.atomimg)  why = Memo;
	else if (st.meta0 != memo.meta_end)                  why = Meta;
	else if (n != memo.n)                                why = Shape;
	else {
		for (uint32_t i = 0; i < n; i++) {
			const auto& b = d.images[i];  const auto& s = memo.s[i];  const auto& v = b.desc.view_info;
			if (b.image_id != s.id || v.base_level != s.base_level || v.level_count != s.level_count ||
			    v.base_layer != s.base_layer || v.layer_count != s.layer_count ||
			    (b.desc.type == TextureCache::BindingType::Storage ? 1 : 0) != s.storage) { why = Shape; break; }
			const auto& img = cache.GetImage(b.image_id);   // this draw's id: the same call the loop makes
			if (img.backing.state_serial != s.state_serial) { why = Serial; break; }
			if (SpTrFlags(img) != s.flags || img.binding.attachment_layout != s.att_layout ||
			    img.binding.attachment_access != s.att_access) { why = Flags; break; }
		}
	}
	st.would   = why == None;
	st.would_g = st.would && st.serial0 == memo.serial_end;
	FS::Add(FS::Counter::SpTrStages, 1);  FS::Add(FS::Counter::SpTrSlots, n);
	if (st.would) {
		FS::Add(FS::Counter::SpTrWould, 1);  FS::Add(FS::Counter::SpTrWouldSlots, n);
		if (st.would_g) { FS::Add(FS::Counter::SpTrWouldGlobal, 1); }
	} else {
		FS::Add(static_cast<FS::Counter>(static_cast<uint32_t>(FS::Counter::SpTrMissBig) + why - 1), 1);
	}
	t_sp_dcc_pending = false;  t_sp_dcc_armed = true;
	return st;
}

void RenderExecutor::SpTrPost(uint32_t k, const PreparedBindings& d, uint32_t n, const SpTrStage& st,
                              uint64_t loop_ns, const CommandBuffer& buffer) {
	namespace FS = Common::FrameStats;
	auto& memo = m_sp->tr[k];  auto& cache = m_context.GetTextureCache();
	t_sp_dcc_armed = false;
	const bool     dcc     = t_sp_dcc_pending;
	const uint64_t serial1 = ImageStateSerial(), meta1 = cache.MetaEpoch();
	const bool     open1   = buffer.IsRendering();
	FS::Add(FS::Counter::SpTrLoopNs, loop_ns);
	if (dcc) { FS::Add(FS::Counter::SpTrDcc, 1); }
	uint32_t bad = 0;
	if (st.would) {
		FS::Add(FS::Counter::BindLapTrHitNs, loop_ns);
		if (st.would_g) { FS::Add(FS::Counter::BindLapTrHitGNs, loop_ns); }
		uint32_t slot = UINT32_MAX;
		if (serial1 != st.serial0) { bad |= 0x01; }                       // S: a barrier / state write in the loop
		if (dcc)                   { bad |= 0x02; }                       // D: a DCC clear was pending
		if (st.open0 && !open1)    { bad |= 0x08; }                       // P: the loop closed the pass
		for (uint32_t i = 0; i < n; i++) {
			if (d.images[i].layout != memo.s[i].result) { bad |= 0x04; slot = i; break; }  // L: binding.layout
		}
		if (bad != 0) {
			if (meta1 != st.meta0) { FS::Add(FS::Counter::SpTrRace, 1); }
			else {
				FS::Add(FS::Counter::SpTrBad, 1);
				// SpTrMismatch: frame=%d stage=%u n=%u why=0x%02x slot=%u  (<= 40 lines, m_sp->tr_logged)
			}
		}
		const auto r0 = FS::NowNs();                                       // dry replay: the per-slot store
		for (uint32_t i = 0; i < n; i++) { m_sp->sink.tr_layout[i] = static_cast<uint32_t>(memo.s[i].result); }
		FS::Add(FS::Counter::SpTrRepNs, FS::NowNs() - r0);
	}
	const bool rec_ok = bad == 0 && n <= kSpTrSlots && serial1 == st.serial0 && meta1 == st.meta0 && !dcc;
	if (!rec_ok) { memo.valid = false; return; }
	if (!st.would) {
		memo.n = n;  memo.atomimg = st.atomimg;
		for (uint32_t i = 0; i < n; i++) {
			const auto& b = d.images[i];  const auto& v = b.desc.view_info;  const auto& img = cache.GetImage(b.image_id);
			memo.s[i] = {b.image_id, v.base_level, v.level_count, v.base_layer, v.layer_count,
			             uint8_t(b.desc.type == TextureCache::BindingType::Storage), SpTrFlags(img),
			             img.binding.attachment_layout, b.layout, img.binding.attachment_access,
			             img.backing.state_serial};
		}
		memo.valid = true;
		FS::Add(FS::Counter::SpTrRecords, 1);
	}
	memo.serial_end = serial1;  memo.meta_end = meta1;
}
```

### 3.10 S16, S17 — printing and the gate

`videoOut.cpp` after `{"sc_ns", FS::Counter::ScNs, false},` (`:2582`): the 51 rows of §6 in table order, every one
`micros = false` (raw ns / raw counts, the convention since s91). `gates.h`/`gates.cpp`: §7.

---

## 4. The would-hit predicates (what "a memo could skip" means)

### 4.1 A — `AcquireRenderTargets`, inside the open pass (first failing reason is counted)

| order | reason counter | condition for a would-hit |
|---:|---|---|
| 1 | `sp_rt_x_memo` | a memo exists: recorded by the latest armed draw under the strict rule (§3.7) AND pinned to its pass at `BeginRendering` (§3.8) |
| 2 | `sp_rt_x_cfg` | `rtfast` on, no debug dump, no linear readback, `slicecen` off (the configuration in which `AcquireTargetView` can take its fast path and `AcquireRenderTargets` has no census side effect) |
| 3 | `sp_rt_x_dclr` | **not a depth clear**: `!depth.depth_clear_enable` (`ClearMeta` mutates, `renderDraw.cpp:991-994`) |
| 4 | `sp_rt_x_meta` | `MetaEpoch()` equal to the memo's (HTile/DCC/CMASK state unchanged; `IsMetaCleared` then answers as at the memo, `renderDraw.cpp:995-997`) |
| 5 | `sp_rt_x_ids` | same target set: `color_count`, depth presence, per target `image_id` (index+generation), `target_slot`, resolver `memo_slot` (≠ `UINT32_MAX`) and `memo_version` (the desc, view_info, metadata, extent, depth register flags and clear values are those of the memo, §1.5) |
| 6 | `sp_rt_x_live` | per target the live half of the rtfast fast predicate: `registered`, `!depth_id`, `!needs_rebind`, `pending_levels == 0`, same `backing.image`, `bind_stamp` equal, `source_size`/`source_first_level` equal, the rtfast record still valid for this id with the memo's view and stamp; depth: `htile_clear_mask` equal and the stencil association alive (`renderDraw.cpp:807-814`) |
| 7 | `sp_rt_x_ser` | **the new image-state counter unmoved**: per target `backing.state_serial` equal to the memo's (the global serial is the nested `sp_rt_wg`) |
| 8 | `sp_rt_x_bound` | per colour target `binding.is_bound` equal (it selects `eGeneral` vs `eColorAttachmentOptimal`, `:943-944`) |
| 9 | `sp_rt_x_dsmp` | **not a sampled depth target**: `!depth_image.binding.is_bound` (then the feedback scan `:1019-1035` is false and `sampled_readonly` `:1049-1052` false) |
| 10 | `sp_rt_x_pass` | **same open pass**: `IsRendering()` and `PassBeginSerial()` equal to the value pinned after the memo draw's `BeginRendering`. Last on purpose: `sp_rt_x_pass` = the draws that pass everything but the open-pass requirement |

Identity: `sp_rt_n = sp_rt_would + Σ sp_rt_x_*` (10 reasons, exact per frame). Nested: `sp_rt_wg` = would-hits
whose global serial also equals the memo's `serial_end`.

### 4.2 B — the transit loop of one stage (stage position k of the draw's commit)

| order | reason | condition |
|---:|---|---|
| 1 | `sp_tr_x_big` | `n = program.info.images.size() ≤ 32` |
| 2 | `sp_tr_x_memo` | a memo for position k recorded under the strict rule, and the same `atomimg` gate value (`GetBarriers` reads it, `image.cpp:123-124`) |
| 3 | `sp_tr_x_meta` | `MetaEpoch()` equal (then every `MaterializeDeferredDccClear` again finds mask 0, `descriptors.cpp:1856-1868`) |
| 4 | `sp_tr_x_shape` | same `n`; per slot same `image_id`, same view range (`base_level`, `level_count`, `base_layer`, `layer_count` — the `range` of `:3751-3752`), same storage-ness |
| 5 | `sp_tr_x_ser` | per slot image `backing.state_serial` equal |
| 6 | `sp_tr_x_flags` | per slot `SpTrFlags` (`data.Empty`, `is_target`, `force_general`, `shader_write`, `shader_write_plain`, `IsDepth`, `registered`, `depth_id`) and `attachment_layout`/`attachment_access` equal — every per-image input of the branch at `:3760-3814` and of `atomic_write` `:3757-3759` |

The GDS block (`:3697-3727`) is outside the timed loop and outside the predicate (a real memo keeps it).
Identity: `sp_tr_n = sp_tr_would + Σ sp_tr_x_*` (6 reasons). Nested: `sp_tr_wg`.

### 4.3 Why a would-hit implies the full work is a repeat (the argument the bad check tests)

* B: `GetBarriers` is a deterministic function of (the image's `state`, `subresource_states`, the destination layout /
  access / stage, `range`, `atomic_write`, the `atomimg` gate, `info.IsVolume()`/`resources`). The destination and
  `range` are functions of the §4.2 inputs; the records are witnessed by `state_serial`; the memo is recorded only
  when the loop changed no record (global serial unmoved across it) and met no pending DCC mask. Same inputs + same
  records ⇒ the same zero-barrier, zero-write outcome, and `binding.layout` = the destination layout (§5.2).
* A: the fast path of `AcquireTargetView` holds (its predicate is §4.1 rows 2, 4, 5, 6 against an unchanged
  record), so the view is the record's; layouts are functions of `is_bound` (row 8) and of the depth flags (identity);
  `depth_load_clear_enable = depth_clear_enable ∨ IsMetaCleared` is false (rows 3, 4 and the record rule); the
  `Transit`s repeat a zero-write outcome (row 7 + the record rule); extents are functions of the descs. Hence the
  same `RenderState`, the same stores, and no barrier.

---

## 5. The bad check (what is compared, exactly)

Run beside every would-hit, after the full work, with the full work's result. One count per would-hit draw (A) or
would-hit stage (B); the first 40 are logged.

### 5.1 `sp_rt_bad` — A (bits of `SpRtMismatch: … why=`)

| bit | compared | "differs" means |
|---|---|---|
| 0x01 R | the returned `RenderState` vs the memo's (`operator==`, `renderTarget.h:49-58`): every attachment's view and layout, depth clear flags and clear values, width, height, layers, attachment count — **target image views and layouts** | not equal |
| 0x02 S | `ImageStateSerial()` before the call vs after — **barriers emitted = 0** and no state record written (all writers of the serial run under the render mutex this draw holds, §1.1, so any move is this call's) | moved |
| 0x04 F | fallback taken: `AcquireTargetView` slow path (`FindRenderTarget`/`FindDepthTarget`) or the dead re-find | taken |
| 0x08 I | **target image ids** after the call vs the memo's | not equal |
| 0x10 X | the stores a hit must replay: per target `binding.attachment_layout`/`attachment_access`; `depth.depth_load_clear_enable` (must be false); `g_pass_extents` (all three fields) | not equal |
| 0x20 P | the call closed the pass: `IsRendering()` true at the check, false after | closed |
| 0x40 P2 | **pass not restarted**: at `BeginRendering`, the pass was open right before it and `PassBeginSerial()` moved (an open pass whose state equals the memo cannot restart, since open ∧ same pass serial ⇒ `m_render_state == memo.state`) | restarted |

**Race, not bad (`sp_rt_race`)**: a difference while a witness that another thread writes moved between the check and
the post — a target's `bind_stamp` (guest fault handlers under `TextureCache::m_lock`, `image.h:212-217`) or
`MetaEpoch` (guest `UnmapMemory`, §1.3). Given the check passed, the only ways the fast path can fail inside the call
are exactly these two moves, so a hole in the predicate shows as F with no witness moved ⇒ bad.

### 5.2 `sp_tr_bad` — B (bits of `SpTrMismatch: … why=`)

| bit | compared | "differs" means |
|---|---|---|
| 0x01 S | global serial across the loop — **barriers emitted = 0**, no record written | moved |
| 0x02 D | `MaterializeDeferredDccClear` found a non-zero clear mask during the loop | found |
| 0x04 L | per slot the resulting `TextureBinding::layout` (`:3815`) vs the memo's | not equal |
| 0x08 P | the loop closed the pass | closed |

L is also a check of this lemma: after any `Transit`, `backing.state.layout == destination_layout` — the whole-image
path either early-returns only when `state.layout == destination_layout` (`image.cpp:200-206`) or writes it (`:226`);
the partial path always writes it (`:226`). **Race, not bad (`sp_tr_race`)**: a difference while `MetaEpoch` moved
during the loop.

### 5.3 What a real hit must still do (replayed dry and timed, so the ceiling is net of it)

A: return the memo's `RenderState`; restore `g_pass_extents` (read by the pass census, `context.cpp:358-363`); per
target store `attachment_layout`/`attachment_access` (`ResetBindings` cleared them; `CommitBindings` EXITs on
`eUndefined` for a sampled target, `descriptors.cpp:3768-3769`); `MarkGpuModified()` (a download may have cleared the
flag, `renderDraw.cpp:824`) and the `usage` flag; replay `RtAttachments`, `RtPixelsK` and the two `NoteMax` — **`rt_att`
/ `rt_kpx` are the DRS watchdog of every scorer**. B: the per-slot `binding.layout` store. The dry replay makes the
same number of loads, stores and `FS::Add`s into `m_sp->sink` and two new counters, so its time is cost-faithful.
Not replayed and not needed: `SetVulkanObjectNameF` (no-op without the debug dump, excluded by cfg), `RtFastOk`
(a counter), `SliceCensus::Image` (excluded by cfg).

---

## 6. Counters (51, appended in this order before `Counter::Count`, `frameStats.h:1943`; all raw ns / raw counts, `micros = false`)

| enum | print name | unit | meaning | M arm (`spcen=0`) |
|---|---|---|---|---|
| `ImageStateSerialBumps` | `sp_ser_n` | count | image-state serial moves (W1–W7) | **live (always)** |
| `ImageStateSerialValue` | `sp_ser_val` | count | … of which only a W5 value change (no barrier, no resize/clear) | **live (always)** |
| `SpRtDraws` | `sp_rt_n` | count | armed draws (A check evaluated) | 0 |
| `SpRtWould` | `sp_rt_would` | count | A would-hits (per-image witness) | 0 |
| `SpRtWouldGlobal` | `sp_rt_wg` | count | … also under the global serial (s119 witness) | 0 |
| `SpRtTargets` | `sp_rt_tgt` | count | targets (colour + depth) of A would-hits | 0 |
| `PathEmSpChkNs` | `pl_em_spchk_ns` | ns | emit-chain part: latch + A check, all armed draws | 0 |
| `SpRtChkHitNs` | `sp_rt_chkh_ns` | ns | … of which on would-hit draws | 0 |
| `PathEmRtHitNs` | `pl_em_rt_hit_ns` | ns | **`AcquireRenderTargets` on A would-hits** (subset of `pl_em_rt_ns`) | 0 |
| `PathEmRtHitGNs` | `pl_em_rt_hitg_ns` | ns | … on global-witness would-hits | 0 |
| `PathEmSpPostNs` | `pl_em_sppost_ns` | ns | emit-chain part: A bad check + dry replay + record | 0 |
| `SpRtRepNs` | `sp_rt_rep_ns` | ns | A dry replay (inside `pl_em_sppost_ns`) | 0 |
| `SpRtRepAtt` | `sp_rt_rep_att` | count | colour targets replayed (= their `rt_att`) | 0 |
| `SpRtRepKpx` | `sp_rt_rep_kpx` | Kpx | their `rt_kpx` | 0 |
| `SpRtRecords` | `sp_rt_rec` | count | A memos validated at `BeginRendering` | 0 |
| `SpRtBad` | `sp_rt_bad` | count | **must be 0** | 0 |
| `SpRtRace` | `sp_rt_race` | count | differences explained by a cross-thread witness move | 0 |
| `SpRtRestart` | `sp_rt_rst` | count | would-hits whose own `BeginRendering` began a new pass (something closed it after the check) | 0 |
| `SpRtUntimed` | `sp_rt_nt` | count | armed draws without a running `PathLap` (pathlap off ⇒ A times read 0) | 0 |
| `SpRtMissMemo` … `SpRtMissPass` | `sp_rt_x_memo`, `sp_rt_x_cfg`, `sp_rt_x_dclr`, `sp_rt_x_meta`, `sp_rt_x_ids`, `sp_rt_x_live`, `sp_rt_x_ser`, `sp_rt_x_bound`, `sp_rt_x_dsmp`, `sp_rt_x_pass` | count | first failing A reason, §4.1 order (contiguous; `static_assert` the span = 9) | 0 |
| `SpTrStages` | `sp_tr_n` | count | armed stages (graphics commits of armed draws) | 0 |
| `SpTrSlots` | `sp_tr_slots` | count | their image slots | 0 |
| `SpTrWould` | `sp_tr_would` | count | B would-hit stages | 0 |
| `SpTrWouldGlobal` | `sp_tr_wg` | count | … also under the global serial | 0 |
| `SpTrWouldSlots` | `sp_tr_wslots` | count | slots of B would-hit stages | 0 |
| `SpTrLoopNs` | `sp_tr_loop_ns` | ns | the transit loop (`:3740-3816` + its lap stamp), all armed stages — the total | 0 |
| `BindLapTrHitNs` | `bl_tr_hit_ns` | ns | **the transit loop on B would-hit stages** | 0 |
| `BindLapTrHitGNs` | `bl_tr_hitg_ns` | ns | … on global-witness would-hits | 0 |
| `SpTrChkNs` | `sp_tr_chk_ns` | ns | B check, all armed stages | 0 |
| `SpTrChkHitNs` | `sp_tr_chkh_ns` | ns | … on would-hit stages | 0 |
| `SpTrPostNs` | `sp_tr_post_ns` | ns | B bad check + dry replay + record | 0 |
| `SpTrRepNs` | `sp_tr_rep_ns` | ns | B dry replay (inside `sp_tr_post_ns`) | 0 |
| `SpTrRecords` | `sp_tr_rec` | count | B memos (re)recorded | 0 |
| `SpTrBad` | `sp_tr_bad` | count | **must be 0** | 0 |
| `SpTrRace` | `sp_tr_race` | count | differences while `MetaEpoch` moved | 0 |
| `SpTrDcc` | `sp_tr_dcc` | count | armed stages whose loop met a pending DCC mask (never recorded) | 0 |
| `SpTrMissBig` … `SpTrMissFlags` | `sp_tr_x_big`, `sp_tr_x_memo`, `sp_tr_x_meta`, `sp_tr_x_shape`, `sp_tr_x_ser`, `sp_tr_x_flags` | count | first failing B reason, §4.2 order (contiguous; `static_assert` span = 5) | 0 |

Log lines: `SpCensus: mode 1 rt_targets=9 tr_slots=32` (once, first armed draw); `SpRtMismatch:` and
`SpTrMismatch:` (≤ 40 each). No existing name starts with `sp_` or equals `pl_em_rt_hit_ns`/`bl_tr_hit_ns`
(`videoOut.cpp` searched); R1 uses `r1_*` (`C:/kyty/s120/design/r1.md`).

---

## 7. Gate / knob entries

One gate, no knob.

```cpp
 // gates.h, after SliceCensus (:413), before Count (:414)
+	// Session 120, MEASUREMENT ONLY (C:/kyty/s120/design/spcen.md): the same-pass render-target memo census. Per
+	// draw it evaluates, WITHOUT acting, whether a memo could skip AcquireRenderTargets inside the open pass and
+	// the transit loop of CommitBindings; the full work runs beside every would-hit and sp_rt_bad / sp_tr_bad count
+	// any difference. Read ONCE a draw and latched (CommitBindings and BeginRendering read the latch), so it CAN be
+	// a schedule arm. Changes nothing that executes. The rt times need "pathlap" in the same arm (else sp_rt_nt).
+	// Use with "cbmove" OFF (its stage spans would contain the census check).
+	// LAST row, matching the LAST enum entry before Gate::Count.
+	SamePassCensus,     // KYTY_SAME_PASS_CENSUS,   file name "spcen"

 // gates.cpp DEFINITIONS, after {"KYTY_SLICE_CENSUS", "slicecen", false}, (:284)
+    // Session 120, measurement only: the same-pass render-target memo census (spcen.md). Read once a draw and
+    // latched, so it CAN be a schedule arm.
+    // LAST row, matching the LAST enum entry before Gate::Count.
+    {"KYTY_SAME_PASS_CENSUS", "spcen", false},
```

Merge rule: R1 is a knob (`r1cen`, `KNOB_DEFINITIONS`); if R2 adds a gate, the merged patch fixes one order of the new
gates identical in `enum class Gate` and `DEFINITIONS`; run `check_gate_order.py` (s96) before the build. `spcen` is
a name absent from `gates_base.txt` (default 0): both schedule arm texts must name it (`spcen=1` in P, `spcen=0` in M);
the arm is identified by the `GateArm:` text, never by "a counter > 0" (s93 lesson).

Why no knob: a split A-only / B-only mode would need a second ABBA the session does not have; both halves share the
latch and the serials, and each half's own cost is measured in-arm (§9).

---

## 8. Ceiling formula and bound direction

Per P-arm frame (frames 10–88 of every P block; block means; mean of block means; 2·SE over blocks; per frame = per
`FrameTrace-x` interval, divisor 1 — s71):

```
G_A = pl_em_rt_hit_ns                                           gross: the work A would skip
N_A = pl_em_rt_hit_ns − pl_em_spchk_ns − sp_rt_rep_ns             net: minus the check on EVERY armed draw
                                                                        and the replay on every would-hit
G_B = bl_tr_hit_ns
N_B = bl_tr_hit_ns − sp_tr_chk_ns − sp_tr_rep_ns
N   = N_A + N_B            (disjoint: the rt span and the transit loop inside the com span)
Global-witness variants (s119 rule, diagnostic): G_A^g = pl_em_rt_hitg_ns, G_B^g = bl_tr_hitg_ns,
N_A^g = G_A^g − pl_em_spchk_ns − sp_rt_rep_ns·(sp_rt_wg/sp_rt_would), N_B^g likewise with sp_tr_*.
µs a frame = value / 1000.
```

The check is subtracted on all armed draws/stages because a real memo pays it on misses too. The measured removable
ceiling of the program's rule is **N** (and N_A, N_B separately).

**Bound direction.** G is a strict **upper** bound of what either memo can remove in the measured arm (it is the whole
skipped work). N is the measured net; it leans **low** (conservative):
* (−) the check touches the same `Image` objects, rtfast records and resolver entries right before the full work, so
  `pl_em_rt_hit_ns`/`bl_tr_hit_ns` are measured warm — smaller than the same work in M. Measurable from the ABBA:
  `Δ_warm = mean pl_em_rt_ns(M) − mean pl_em_rt_ns(P)` (identical work in both arms); an upper variant
  `N_A⁺ = N_A + Δ_warm·(pl_em_rt_hit_ns/pl_em_rt_ns)` is reported, never used for the verdict;
* (−) the census check is at least the real memo's check: it evaluates the pass condition last (so the per-target
  loop also runs on `sp_rt_x_pass` draws) and pays 2–3 reason/population `Add`s per draw a real memo would not;
* (−) each dry replay carries one timer read (~7 ns) in `sp_*_rep_ns`;
* (+) the dry replay stores into `m_sp->sink` instead of `Image::binding` (same line the check already loaded, so
  within ≈ 1–2 ns per target) and the cross-span cache effect of the skipped work on com/rec is not measured —
  bounded by ≈ 2 ns × `sp_rt_tgt` + 1 ns × `sp_tr_wslots` ≈ ≤ 0.06 ms/frame [I].

**Proposed verdict rule (to be sealed in ROADMAP before code, program rule s119 item 2):**
FAIL (mechanism unsound as designed) if `sp_rt_bad + sp_tr_bad > 0` on ANY frame of the run (not only the window) or
any `SpRtMismatch:`/`SpTrMismatch:` line exists; NOT EVALUABLE if `sp_rt_nt > 0` in P, if `sp_rt_n ≠ pl_em_n` beyond
the row skew, or if `(sp_rt_race + sp_tr_race) > 10⁻⁴·(sp_rt_would + sp_tr_would)`; OPEN a track iff
`mean(N) − 2·SE ≥ 1 000 µs` (report which of N_A, N_B carries it); CLOSED iff `mean(N) + 2·SE < 1 000 µs` or
`mean(G_A + G_B) < 1 000 µs` (then `mh_emit` micro-tracks are recorded exhausted on Sky Garden, per `emit_parts.md`
§5); otherwise UNDECIDED (no track). Quote every number with the BDA regime (`bda_scan`).

**Prior expectation, not a seal [I]** (from `spk118` and `emit_parts.md` §4): `sp_rt_n` ≈ 5 025, `sp_rt_would` ≈
3 900–4 600, G_A ≈ 0.9–1.3 ms, check ≈ 5 025 × 55–70 ns ≈ 0.3 ms, replay ≈ 0.15 ms ⇒ N_A ≈ 0.5–0.9 ms;
`sp_tr_n` ≈ 9 000–9 200 (graphics stages; `bl_stage_n` 9 443 includes 270 dispatches), `sp_tr_slots` ≈ 45–47 k,
G_B ≈ 0.5–0.75 ms, check ≈ 8 ns/slot + 5 ns/stage ≈ 0.4 ms ⇒ N_B ≈ 0.1–0.35 ms. So N ≈ 0.6–1.25 ms: the census is
needed precisely because this straddles 1 ms.

---

## 9. Own cost of the instrument

**Always on (both arms, also at gate 0):** the two serials. `NoteStateChange` + one `Add` on the non-early-return
paths of `GetBarriers` (≈ `ibar` 421 barrier calls/frame [M spk118] plus the partial-path calls) and in `CreateImage`
(`img_new`); a 4-field compare on every partial-path call; one relaxed add per real pass begin (`rp_begin` 189/frame).
≤ 0.05 ms/frame [I]. Not priced by P|M (both arms carry it); versus `d3a981a2` it is bounded by
`sp_ser_n × ~25 ns` + the partial-path compares.

**P arm only [I]:**
* A per armed draw: latch (gate read + out-of-line `FrameStats::Enabled()`) ~4 ns; check ~45–60 ns (3.46 targets ×
  ~12 loads/compares + `try_get` + rtfast record); two extra `PathLap` marks ~16–20 ns; post: `RenderState` compare
  (~376 B) ~15–30 ns, side-store compares ~8 ns, dry replay on would-hits ~35 ns incl. two timer reads, record ~40 ns
  on misses / ~5 ns on hits; `BeginRendering` bookkeeping ~5 ns ⇒ ≈ 130–160 ns/draw × 5 025 ≈ **0.65–0.8 ms/frame**.
* B per armed stage: three extra timer reads (split lap, check end, post end) ~21–25 ns; check ~5 ns + ~8 ns/slot ×
  5.1 slots; post ~10 ns + ~1 ns/slot, +~20 ns record on misses, +~15 ns dry replay on would-hits; ~6 `Add`s ⇒
  ≈ 80–100 ns/stage × ~9 170 ≈ **0.75–0.95 ms/frame**.
* Total P − M ≈ **1.4–1.8 ms/frame [I]** (plus the R1/R2 census in the same arm).

**How it is measured:** (a) the sealed ABBA P|M prices it as Δ mean `dt_us`, `cpu_gpu_us`, `mh_emit`; (b) in-arm, the
directly timed part is `pl_em_spchk_ns + pl_em_sppost_ns + sp_tr_chk_ns + sp_tr_post_ns` (a lower bound: the
lap-split and re-base timer reads of B and the `BeginRendering` bookkeeping are outside these counters; also
`pl_em_com_ns(P) − pl_em_com_ns(M)` ≈ B's share). With `KYTY_GPU_CLOCK_PIN=1` the DRS rung does not follow the slower
P frames (s91), so the scene's work per frame is the same in both arms.

---

## 10. What must NOT change at gate 0

1. No census work on any path: `SpDrawScope` reads one gate (a relaxed load) and stops — `FrameStats::Enabled()` is
   evaluated only after it; `m_sp` is never allocated; the rt mark stays `PathLap::Mark(PathEmRtNs)` exactly; no
   `PathEmSpChkNs`/`PathEmSpPostNs` mark; `CommitBindings` computes `sp_tr = false` (one null-pointer test per
   commit), so `cb_timed`, every `cb_lap`, the loop and `cb_t` are exactly today's; the `BeginRendering` sites do
   nothing more than test `sp_scope.Armed()`.
2. The three TLS flags are tested only on rare paths (the rtfast slow path ~63/frame, the dead re-find, a non-zero
   DCC mask) and written only when armed.
3. No decision anywhere reads a census field, a serial or the pass serial: no Vulkan call, record, barrier, pass
   begin/end, EXIT condition, memo (texture / colour / depth / rtfast), GC or gate/knob changes.
4. The always-on parts (§9) only write two new atomics, one new `VulkanImage` field and two new counters.
   `VulkanImage` grows by 8 B; `RenderExecutor` by one `unique_ptr`; `CommandBuffer` by one static.
5. The translation-cache signature is unchanged (§2): nothing under `src/graphics/shader/**`,
   `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`.
6. `FrameTrace-x` gains 51 fields at its end (scorers read by name; `sp_ser_n`/`sp_ser_val` are non-zero in M);
   the main `FrameTrace` line is unchanged.
7. Non-lite caveat: the old `FrameStats::Lap` (`TimingsEnabled`, 0 in lite) is not re-based, so in a
   `KYTY_FRAME_TRACE=1` run with `spcen=1` `DrawAcquireRtNs` contains the check and `DrawPipelineNs` the post; the
   measurement mode is lite.

---

## 11. Fixtures a scorer needs

Each on a synthetic `FrameTrace-x` line carrying EVERY one of the 51 new fields plus the fields read (s105 lesson),
the suite ending with `ALL OK`, LF line endings.

1. **Arming by arm text.** P/M decided from `GateArm: … text=` containing `spcen=1`/`spcen=0`; a line where all
   `sp_rt_*` are 0 inside a P block must not flip the arm.
2. **M arm zeros.** In M every `sp_rt_*`, `sp_tr_*`, `pl_em_spchk_ns`, `pl_em_sppost_ns`, `pl_em_rt_hit(g)_ns`,
   `bl_tr_hit(g)_ns` = 0 on every frame (else NOT EVALUABLE); `sp_ser_n > 0` in BOTH arms (serial alive);
   `sp_ser_val ≤ sp_ser_n`.
3. **Draw identity.** P: `sp_rt_n = pl_em_n` per frame within the row skew (no return between `renderDraw.cpp:2308`
   and the check; `bindfloor=0`); exact on window sums ± rows×2.
4. **Reason partition.** `sp_rt_n = sp_rt_would + Σ10 sp_rt_x_*`; `sp_tr_n = sp_tr_would + Σ6 sp_tr_x_*`, tested on
   WINDOW sums (frames 10–88 of each block) within ±2 per block window (±1 per window edge), never exact per frame:
   `FrameTrace-x` reads each counter separately (`FS::Read`, print order) while GuestGpu keeps adding, so a draw's or
   stage's `SpRtDraws`/`SpTrStages` Add and its reason Add can land on adjacent lines (review of the code, BLOCKING;
   design120.md §4 "Row skew"). A fixture with a +1/−1 skew between two adjacent lines that cancels over the window
   is ADMITTED; a persistent +1 on every line (the mutant "reason index shifted" or an extra Add) must FAIL.
5. **Nesting.** `sp_rt_wg ≤ sp_rt_would`, `pl_em_rt_hitg_ns ≤ pl_em_rt_hit_ns ≤ pl_em_rt_ns`,
   `sp_rt_chkh_ns ≤ pl_em_spchk_ns`, `sp_rt_rep_ns ≤ pl_em_sppost_ns`, `sp_tr_wg ≤ sp_tr_would`,
   `bl_tr_hitg_ns ≤ bl_tr_hit_ns ≤ sp_tr_loop_ns ≤ 1000·bl_tr_us + rounding` (**`bl_tr_us` is µs, every new field is
   ns** — a unit fixture), `sp_tr_chkh_ns ≤ sp_tr_chk_ns`, `sp_tr_rep_ns ≤ sp_tr_post_ns`,
   `sp_tr_wslots ≤ sp_tr_slots`. All on WINDOW sums as fixture 4 (the same row skew applies to every pair here,
   e.g. `sp_rt_wg`/`sp_rt_would`, `bl_tr_hit_ns`/`sp_tr_loop_ns`, `sp_tr_wslots`/`sp_tr_slots`): counts within ±2 per
   block window; ns within the subset counter's values on the window's two edge lines. A fixture with a one-line
   skew that cancels over the window is ADMITTED; a fixture where the subset exceeds the superset on every line FAILs.
6. **Target bounds.** `sp_rt_tgt ≤ rt_fast_ok + rt_fast_no`; `sp_rt_rep_att ≤ rt_att`; `sp_rt_rep_kpx ≤ rt_kpx`;
   `sp_rt_rep_att ≤ sp_rt_tgt`.
7. **Emit chain.** P: `pl_em_vtx + pl_em_spchk + pl_em_rt + pl_em_sppost + pl_em_pipe + pl_em_com + pl_em_rec +
   pl_em_rest ≈ 1000·mh_emit_us` on window means (tolerance as s116: 256 on the sum; row skew ±60); M: the s116
   identity without the two new parts. A fixture that forgets the two parts must FAIL.
8. **Bad.** One frame with `sp_rt_bad = 1` (anywhere, also outside 10–88) ⇒ FAIL; same for `sp_tr_bad`; a log line
   `SpRtMismatch:` or `SpTrMismatch:` with all counters 0 ⇒ FAIL.
9. **Race threshold.** `race = 10⁻⁴·would` exactly ⇒ evaluable; one above ⇒ NOT EVALUABLE.
10. **Timing present.** `sp_rt_nt > 0` in a P frame ⇒ NOT EVALUABLE (pathlap missing).
11. **Ceiling arithmetic.** Known synthetic block values: N = 999.9 µs with 2·SE 0 ⇒ CLOSED; 1 000.0 ⇒ OPEN;
    mean 1 050, 2·SE 100 ⇒ UNDECIDED; G_A + G_B = 990 with N computed negative ⇒ CLOSED; N_A alone ≥ 1 000 ⇒ OPEN and
    names A. Check subtraction uses `pl_em_spchk_ns` (all draws), NOT `sp_rt_chkh_ns` (a mutant using chkh must
    change the verdict of a fixture built for it).
12. **Window.** Frames 10–88 of each block; a fixture with a huge value in frame 9 and frame 89 must not move the
    ceiling; the first P block's frame carrying the one-time `SpCensus:` allocation is outside the window.
13. **Divisor.** Per frame, not per draw: a fixture where `pl_em_rt_hit_ns/sp_rt_would` is used instead must fail.
14. **Global variant.** Report N^g with the replay scaled by `sp_rt_wg/sp_rt_would`; the verdict uses N, never N^g.
15. **Warm-cache variant.** `Δ_warm` from M − P `pl_em_rt_ns`; reported only; a fixture with Δ_warm pushing N⁺ over
    1 000 while N < 1 000 must stay CLOSED/UNDECIDED.
16. **Straddle.** A frame at the arm edge whose line carries partial counts is excluded by the window; a fixture
    where the first frame after an M→P edge has `sp_rt_x_memo = sp_rt_n` (no memo yet) is normal.
17. **Stream completeness.** Every main-line frame in the window carries a `FrameTrace-x` line with all 51 names
    (s100 `STREAMS_COMPLETE`); a missing field ⇒ NOT EVALUABLE, never a silent drop.
18. **BDA regime.** `bda_scan` classifies the run (NEW ≈ 52/frame); a mixed run is reported per regime.

Mutants the suite must kill (for `mutlib` v4.1 full runs): gross instead of net; check subtracted on hits only;
`bl_tr_us` treated as ns; per-draw divisor; bad ignored; mismatch lines ignored; race counted as bad or ignored;
arm by counter > 0; window 0–99; the two new chain parts dropped from the identity; N^g used for the verdict;
the timer-read add-back Z dropped from N⁺ (design120.md §4); Δ_B used where Δ_B′ is due; partitions/nestings tested
exact per frame (killed by the cancelling-skew fixtures of 4 and 5, which must stay ADMITTED);
`sp_rt_nt` ignored; reason partition off by one reason; `>` for `≥` at 1 000 µs.

---

## 12. Risks for the hostile review

1. **Own cost ≈ 1.4–1.8 ms/frame in P** (heavier than `spine`); the ABBA prices it, but P runs slower.
2. **Per-image witness is this design's decision** (s119 said a global serial). Soundness rests on `GetBarriers`
   reading only its own image's records (`image.cpp:120-121`); the global variant is measured nested, so a reviewer
   who rejects the per-image witness still gets the s119 number from the same run.
3. **Resolver-memo identity** stands in for comparing ~600-byte descs. Its one known hole (the dead re-find in
   `AcquireRenderTargets`, no version move) is excluded at record; a `drawstate` flip between two draws is a
   theoretical second hole. Either would show as bad (F/R), not as a silent wrong hit.
4. **Cross-thread witnesses** (`bind_stamp`, `MetaEpoch`) make "race" a separate class; if races are frequent the
   rule says NOT EVALUABLE rather than guessing.
5. **Warm-cache bias** makes N conservative; `Δ_warm` is reported, not used.
6. **B memo keyed by stage position**: interleaved materials miss (lower hit rate, conservative); a per-program
   memo is a different mechanism, not measured here.
7. **Strict record rule** (no barrier/fallback in the recording call) loses ≤ one hit per pass start with
   transitions (≤ 189 draws/frame) — conservative, ≤ ~0.06 ms [I].
8. **The B check touches every slot's `Image`** (≈ half of the loop's memory traffic), so N_B is likely small; a
   cheaper draw-level witness (identical image lists of all stages ⇒ identical flags) is a possible later refinement,
   not this census.
9. **Gate-table merge** with R1 (knob) / R2: order fixed once, `check_gate_order.py` before the build.
