# Session 120 — adversarial review of `spcen.md` (same-pass render-target memo census)

Reviewer: agent, read-only. Tree `C:/kyty/KytyPS5` at HEAD `8f8a5f1` (the design was read at `996d565`; the two commits
since touch only `docs/ROADMAP.md`, so every source line below is the design's tree). No build, no run, no source edit.

**Verdict: SOUND_WITH_CHANGES.** The per-image witness decision is sound (verified below), the gate-0 path is clean,
and almost every file:line claim holds. But four defects would make the sealed run give a wrong or unreadable answer:
(1) the "race" class hides the very failures the bad counters are supposed to catch; (2) the B check has side effects on
texture-cache LRU counters; (3) the B predicate misses a witness that can change without `MetaEpoch` moving; (4) the
ceiling formula is not an honest bound in the CLOSED direction, and it uses the stale 1 ms threshold. All of these can
be fixed without changing the design's structure.

---

## 1. File:line claims checked

| claim | status |
|---|---|
| `image.cpp:120-121` (own `backing.state`/`subresource_states` only), `:123-124` atomimg gate, `:137-139` resize, `:167-186` per-subresource write only with a barrier, `:190-192` clear, `:194-226` whole path, early return `:200-206`, `:226` unconditional `state =` | ✓ |
| GetBarriers callers `image.cpp:244-246`, `:302-304`, `:348-350`, `tiler.cpp:548-550` | ✓ (tree-wide grep: no other writer of `state`/`subresource_states` except `vma.cpp:399-400`, `:450-451`, `swapchain.cpp:274-275`) |
| `vma.cpp:399-400`, `:450-451`; `graphicContext.h:156-181`, NO_COPY `:167`; no `<atomic>` in `:9-14` | ✓ |
| `swapchain.cpp:237` create, `:67`/`:222` delete, `:274-275` W8, `:281` source.Transit, `:759` render lock (also `:800`, `:890`) | ✓. `Frame::Configure` (`:782`, `:809`) calls `CreateImage` under the render lock, so the S3 bump runs from the present thread too, but only between draws |
| `slotVector.h:84` generation bump on erase | ✓ |
| `descriptors.cpp:3815` `binding.layout = image.backing.state.layout`; the lemma "after any Transit, state.layout == destination" | ✓ (early return needs `state.layout == destination_layout`; otherwise `:226` writes it) |
| `ImageBinding` `image.h:42-52`; `ResetBindings` `descriptors.cpp:2025-2032`; `BindImage` `:1782-1801`; `BindRenderTarget` `:2019-2023`; re-find resets `colorRenderTarget.cpp:147`, `depthRenderTarget.cpp:311`, `renderDraw.cpp:896`, `descriptors.cpp:2514`, `:2699`; `textureCache.cpp:954`, `:1065-1066`, `:1085` | ✓ |
| §1.3: `m_surface_metas` `textureCache.h:302`, epoch comment `:303-307`, writers `:3042-3055`, `:3057-3094`, `:3105`, `:3200-3208`, `:3219-3233`, `:3240-3246`, `:457`, `:1839-1948`, `:2389-2396`; `MetaClearMask`/`IsMetaCleared` `:3017-3040` pure | ✓ |
| §1.3 "`:3206` … the only image-level writer of `kind`" | **✗** `image.info.metadata = desc.info.metadata` also at `textureCache.cpp:1833` (`PrepareDccClear`), `:1915` (`PrepareCmaskClear`), `:2383` (`FindDepthTarget`). Each bumps `MetaEpoch` only when an entry is inserted or changes type (`:1837-1851`, `:1919-1933`, `:2388-2397`) → finding **F3** |
| §1.3 "**`UnmapMemory` runs on a guest thread** (not under the render mutex), so `MetaEpoch` can move concurrently" | **✗** `RenderContext::UnmapMemory` sends it to the GuestGpu thread with `m_gpu->SendCommandSync(unmap)` (`renderContext.cpp:278-297`); only the shutdown path (`IsStopping`) runs it in place. Every `BumpMetaEpoch` site (mapped above) runs on GuestGpu or on the present/RenderDoc thread under the render mutex. Guest fault handlers (`InvalidateMemory`) never reach `FreeImage` or a meta writer → finding **F1** |
| `render.h:289-290`; `context.cpp:324-406`, early return `:325-327`, `EndRenderingImpl` `:447-…`; `image.cpp:253-266` | ✓. Also `CommandBuffer::End`/`EndRecorded` end the pass at submit (`context.cpp:191-229`), and the scheduler owns ONE `CommandBuffer m_command` (`commandScheduler.h:144`), so `buffer` == `Scheduler().Current()` on the direct path `:2837` |
| §1.5: `colorRenderTarget.h:14-31`, version `.cpp:150`, `:170`; `descriptors.cpp:2712-2724`; `depthRenderTarget.h:21-45`, key `.cpp:281-299`, `:314`, `:332`; `renderDraw.cpp:998`, `:1081`; `render.h:565-580`; `AcquireTargetView` record `renderDraw.cpp:853-865` | ✓ (with `rtfast` on, `r` is NOT re-copied on the same slot/version, `colorRenderTarget.cpp:137-140`, `depthRenderTarget.cpp:301-304`, so an in-place mutation persists: consistent with the census, which never records from a re-find draw) |
| S7 `renderDraw.cpp:835-838`, S8 `:893-895`, S9 `:2437-2452`, S10 `:2675`/`:2837`, S11 `descriptors.cpp:3509-3525`, S12 `:3686-3690`, S13 `:3734-3740`/`:3817`, S14 `:1866-1868`, S15 `frameStats.h:1943`/`:2355-2385`, S16 `videoOut.cpp:2582`, S17 `gates.h:413-414`, `gates.cpp:282-285` | ✓ |
| no return between `renderDraw.cpp:2308` and the check | ✓ (the `return`s at `:2316` and `:2395` are inside lambdas) |
| `FrameStats::Enabled()` out of line `frameStats.cpp:160-164`; `Add`/`NoteMax` `frameStats.h:2044-2064` | ✓ |
| translation-cache signature `generate_version.cmake:41-56`, `CMakeLists.txt:155-156` | ✓, no touched file is in it |
| render mutex held from the check to `BeginRendering` | ✓ (`renderDraw.cpp:2999` `LockGuard` for the whole draw; no unlock of the render mutex anywhere; the `pipelineCache.cpp:117`, `:6002` unlocks are `PipelineCache::m_mutex`) |

---

## 2. Findings (most severe first)

### F1 — CRITICAL: "race" hides self-inflicted failures, so the bad counters cannot catch what they claim to catch

`SpRtPost` (§3.7) sets `raced = meta1 != sp.meta0 || any bind_stamp moved`. `SpTrPost` (§3.9) sets race iff
`meta1 != st.meta0`. The design justifies this by claiming `MetaEpoch` moves concurrently from guest `UnmapMemory`. That
premise is false (§1). No cross-thread writer of `MetaEpoch` exists during the check→post window, so every move inside
the window comes from the draw itself. The self-inflicted moves are exactly the failure modes the bad counters are
meant to detect:

* **B, bit D**: whenever `MaterializeDeferredDccClear` finds `mask != 0` and decodes, it consumes the state through
  `cache.TouchMeta(...)` (`descriptors.cpp:1961-1965`), and `TouchMeta` bumps (`textureCache.cpp:3232`). So a D event
  that actually materializes **always** lands in `sp_tr_race`, never in `sp_tr_bad`. Bit D can only turn into bad when
  the decode fails. The same goes for the aliased `ClearImage` path (`:1953-1954`).
* **A**: if a hole in the predicate lets `IsMetaCleared` return true inside a would-hit, `TouchMeta` (`renderDraw.cpp:1000`)
  bumps the epoch, and X/R become race. A slow path (bit F) through `FindRenderTarget` → `PrepareDccClear`
  (`textureCache.cpp:1839-1851`) also bumps it and becomes race.
* **A, `bind_stamp`**: this one really is written by other threads (fault handlers, `image.h:213-217`). But the call's
  own slow path can also bump it: `FindRenderTarget` → refresh/untrack → `bind_stamp.fetch_add` (`textureCache.cpp:590`,
  `:607`, `:626`). Re-reading the stamps after the call therefore cannot tell a guest race from a hole.

The admission threshold `race ≤ 10⁻⁴·would` allows ≈ 1.3 races per frame (≈ 13 000 would-hits/frame), about 4 000 over
the run. A hole that fires about once a frame would pass as "race" with `sp_*_bad = 0` and could OPEN a track on an
unsound mechanism.

### F2 — MAJOR: the B check changes cache state and counters other scorers read (behaviour beyond timing at 1)

`SpTrCheck` and the record path of `SpTrPost` call `cache.GetImage(b.image_id)` "the same call the loop makes".
`TextureCache::GetImage` is not a lookup. It calls `TouchImage` (`textureCache.h:102-106` → `textureCache.cpp:493-514`),
which does three things:
* increments `m_lru_touch_calls` and `m_lru_touch_repeats`. These are published every frame as `TexLruTouches` and
  `TexLruRepeats` (`textureCache.cpp:3293-3296`), so P gains up to about 47 k touches a frame;
* stores `frame_accessed_last`;
* with `texlru=0`, calls `m_lru_cache.Touch` for every slot.

That is an LRU-state and counter side effect in the P arm, and it inflates the measured check cost.

### F3 — MAJOR: the B predicate misses a witness, so the census would FAIL on a missing input rather than on a real hole

`MaterializeDeferredDccClear` returns early on `image.info.metadata.kind != Dcc` (`descriptors.cpp:1847-1849`) and reads
`metadata.range.address` (`:1852`). `PrepareDccClear` rewrites `image.info.metadata` (`textureCache.cpp:1833`) with **no
`MetaEpoch` move** when the `m_surface_metas` entry already exists as `Dcc`. The same applies to `PrepareCmaskClear`
(`:1915`) and `FindDepthTarget` (`:2383`). Here is how it goes wrong:
1. A colour image is sampled with `kind = None`, and the B memo is recorded.
2. A slow-path `FindRenderTarget` sets `kind = Dcc` over an existing Dcc entry that still has a clear mask.
3. The next draw is a would-hit (flags and epoch are equal), but the loop materializes. That is bit D, so `sp_tr_bad`
   under F1's fix, or race as designed.

A real memo would have to witness `kind` and `range.address` per slot. `SpTrFlags` (8 bits) omits them.

### F4 — MAJOR: the verdict threshold is stale

`docs/ROADMAP.md` s120 item 2 (commit `6f691cb`, recorded before action) replaces the 1 ms track threshold with **0.5 ms
net measured ceiling**. Item (г) says: "порог 1 мс в правилах вердикта проектов с. 120 заменяется на 0,5 мс". Item (б)
says spcen A + B form one package. §8 of the design, fixture 11 and the §7 comments still use 1 000 µs. (The workflow
brief's "≥ 1 ms" is the pre-item-2 rule; the ROADMAP record is the one in force.)

### F5 — MAJOR: the ceiling is not an honest bound in the CLOSED direction

* **The record cost is not subtracted.** A real memo must record on every miss and pin at `BeginRendering`. The
  census's record sits inside `pl_em_sppost_ns`/`sp_tr_post_ns`, which N does not subtract. By the design's own §9
  prices that is ≈ 40 ns × 400–1 100 A misses plus ≈ 20–60 ns × 1 800–3 600 B miss stages, **≈ 0.05–0.25 ms a frame**,
  optimistic. Against a 0.5 ms threshold this matters.
* **"G is a strict upper bound" is false.** `pl_em_rt_hit_ns` and `bl_tr_hit_ns` are measured warm, right after the check
  touched the same `Image` lines. The design's own "(−) warm" bullet says so, and its §12.8 puts the B check at about half
  the loop's memory traffic. G(P) < the same work in M.
* So N leans low, which is safe for OPEN but **unsafe for CLOSED**. Yet CLOSED (`mean(N)+2SE < thr` or `mean(G) < thr`) is
  the verdict that records `mh_emit` micro-tracks as exhausted. `Δ_warm` is computed but "never used", which is the wrong
  way round for a closing rule.
* `Δ_warm` for B needs `bindlap=1` in **both** arms (`bl_tr_us` exists only under `cb_timed`). The design never pins it.

### F6 — MEDIUM: fixture 2 would make every run NOT EVALUABLE

"In M every `sp_*` … = 0 on **every** frame". The schedule flips at the present, while GuestGpu may already be running
draws on the other side of the edge (the s98 `bf_xover` crossover). The first M frame after a P block can therefore carry
P counts, and the design itself says the same about arm edges in fixture 16. The zero check must use frames 10–88 of M
blocks. The FAIL-on-any-frame rule for `*_bad` stays as designed.

### F7 — MEDIUM (recommended, prevents a false FAIL): the A check does not restate the full rtfast predicate

The check compares only part of the fast record: `valid`, `image_id`, `backing`, `view`, `stamp`. It does not compare
`fast.meta_epoch`, `fast.source_size`, `fast.source_first_level`, `fast.htile_clear_mask` or `fast.view_info` against
their live counterparts. Instead it reasons that the record is unchanged since N. That holds only if no unarmed
`AcquireRenderTargets` ran between N and N+1 (for example a `bindfloor` draw, or a gate edge inside an open pass). §5.1's
claim "the only ways the fast path can fail are these two moves" is therefore not strictly true. The cheap terms
(`fast.meta_epoch == meta0`, `fast.source_size == img->source_size`, `fast.source_first_level == img->source_first_level`,
depth `fast.htile_clear_mask == img->info.htile_clear_mask`) should be added to the Live reason. Alternatively, clear
`m_sp->rt.valid` and every `tr[k].valid` in `SpDrawScope` when `m_sp != nullptr` and the draw is not armed.

### F8 — MINOR (recommended)

* `SpRtPost` reads `sp.img[i]` (pointers cached at the check) after the call. On the F path, `FindImage` or
  `ResolveOverlap` can `FreeImage` (`textureCache.cpp:1017`, `:1069`, `:1073`, `:2079`), so the read can be use-after-destroy.
  Re-look up with `cache.m_slot_images.try_get(m.t[i].id)`; nullptr ⇒ bit I.
* `SpRtAfterBegin` validates `sp.rt.pending` even when it has just set `draw_bad = 0x40`. On P2 it should invalidate
  instead. P2 should also require `pass_before == sp.rt.pass_serial` to call it bad; any other restart is the `sp_rt_rst`
  diagnostic.
* B: include `binding.image_view` in the slot identity for `is_target && IsDepth()` slots, so the EXIT sanity check
  (`descriptors.cpp:3771-3789`) keeps the same population.
* §5.3 "must still do" should list `depth.depth_load_clear_enable = false` (an output, `renderDraw.cpp:998`) at ≈ 0 ns.
* `Δ_warm_A` also carries `DrawStatTail()` and the latch, because M books them in `pl_em_rt` and P books them in
  `pl_em_spchk`. They cost about 1–2 ns a draw; state it.
* `VulkanImage` grows 104 → 112 B and shifts every `Image` field after `backing` by 8 B. Both arms carry the shift, so
  this is not an ABBA issue, but say so.

---

## 3. What holds (checked, no change)

* **Per-image witness (the design's decision).** `GetBarriers` reads only `backing.state`/`subresource_states` of its own
  image, plus immutable `info.resources`/`IsVolume()`, the `atomimg` gate (compared) and `NarrowUploadBarriers` (barrier
  contents only). The stencil association read by `stencil_kept` is not layout state. Every writer of the serial runs
  under the render mutex: the GuestGpu draw, dispatch, GC and command paths, and the present thread at `swapchain.cpp:759`
  and `:800`. So both the per-image witness and the global S bit are sound.
* **Gate 0.** One relaxed gate load per draw. `FrameStats::Enabled()` runs only after the gate. `m_sp` stays null, so
  `sp_tr` is false and `cb_timed` and the laps are unchanged. The rt mark is unchanged. The rare-path TLS tests are fine.
  The always-on serial is one 4-field compare per partial-path call, plus a relaxed RMW per bump and per real pass begin.
* **A predicate vs the full work.** `feedback` is false whenever `!is_bound`: registered ⇒ `!info.data.Empty()`
  (`textureCache.cpp:373`) ⇒ `BindImage` sets `is_bound` for every pixel binding, including the `RebindImages` repair
  (`descriptors.cpp:2517`). Layouts, extents and clear values come from memo identity. `IsMetaCleared` is witnessed by
  `MetaEpoch` plus the record rule.
* **A timer placement.** `pl_em_rt_hit_ns` is exactly `AcquireRenderTargets` (plus an inert `lap.Mark` in lite), and the
  check and post are outside it. For B, `bl_tr_hit_ns` is the loop only: the extra `cb_lap` before the check and the
  `cb_t` re-base after the check and the post keep `bl_tr` = prologue + GDS + loop, as in M.
* **Replay.** Cost-faithful to about 1–2 ns per target (`NoteMax` is one relaxed load and a compare, the same as the
  sink max). `rt_att`/`rt_kpx` are untouched in P because the full work runs.
* **P2.** It stays sound because `ClearImage` begins its pass through raw `Handle().beginRendering` (`textureCache.cpp:2610`),
  never through `BeginRenderingImpl`.
* **Counter count.** 51, and the reason spans (9, 5) are right.

---

## 4. Required changes (exact)

**RC1 (F1).** Remove `MetaEpoch` from both race predicates and give it a bad bit.
```cpp
// SpRtPost: before the bad test
if (meta1 != sp.meta0) { bad |= 0x80; }                 // M: the call moved MetaEpoch (no cross-thread writer)
// race only when the fast path failed because a target's stamp moved BEFORE the slow-path Find:
bool raced = t_sp_rt_stamp_race;                        // set at S7, see below; never re-read stamps after the call
// S7, renderDraw.cpp:835 (stamp is loaded there BEFORE FindRenderTarget/FindDepthTarget):
if (t_sp_rt_armed) { t_sp_rt_slow = true; t_sp_rt_stamp_race |= (stamp != fast.stamp); }
// SpTrPost: no race class
if (meta1 != st.meta0) { bad |= 0x10; }                 // M
if (bad != 0) { FS::Add(FS::Counter::SpTrBad, 1); /* SpTrMismatch */ }
```
Fix §1.3 and §5.1–§5.2 text. Either drop `sp_tr_race`, or keep it as a counter that is always 0 and add a fixture for it.
Adjust the race-threshold rule to cover `sp_rt_race` only.

**RC2 (F2).** In `SpTrCheck` and in the `SpTrPost` record, replace `cache.GetImage(b.image_id)` with
`cache.m_slot_images[b.image_id]`. `RenderExecutor` already reads this private, see `renderDraw.cpp:811`, `:892`. Add the
§10 statement: "no census path calls `GetImage`/`TouchImage`; `TexLruTouches`/`TexLruRepeats` are equal in P and M per
draw".

**RC3 (F3).** Widen the slot flags and add metadata. In `SpTrSlot`: `uint16_t flags` (+`ImageMetadataKind meta_kind`,
`uint64_t meta_addr`). Compare `img.info.metadata.kind` and `img.info.metadata.range.address` under reason `Flags`, and
record them. Correct §1.3.

**RC4 (F4).** Everywhere in §7, §8 and §11, 1 000 µs → **500 µs**. Rewrite fixture 11:
* N = 499.9 ⇒ CLOSED; 500.0 ⇒ OPEN;
* mean 550 with 2SE 100 ⇒ UNDECIDED;
* G⁺ = 490 ⇒ CLOSED;
* N_A alone ≥ 500 ⇒ OPEN and names A.

The mutant "`>` for `≥`" moves to 500 µs. Cite ROADMAP s120 item 2 (а), (б), (г).

**RC5 (F5).**
(a) Time the record separately:
* `sp_rt_rec_ns` covers the record block of `SpRtPost` plus `SpRtAfterBegin`;
* `sp_tr_rec_ns` covers the record block of `SpTrPost`;
* both are raw ns, printed, with nesting fixtures `sp_rt_rec_ns ≤ pl_em_sppost_ns + rec-span share` and
  `sp_tr_rec_ns ≤ sp_tr_post_ns`.

(b) Redefine the net ceilings:
* `N_A = pl_em_rt_hit_ns − pl_em_spchk_ns − sp_rt_rep_ns − sp_rt_rec_ns`
* `N_B = bl_tr_hit_ns − sp_tr_chk_ns − sp_tr_rep_ns − sp_tr_rec_ns`

(c) Delete "G is a strict upper bound". Define the warm-corrected upper variants:
* `Δ_A = max(0, pl_em_rt_ns(M) − pl_em_rt_ns(P))`
* `Δ_B = max(0, 1000·(bl_tr_us(M) − bl_tr_us(P)))`
* `N⁺ = N + Δ_A·pl_em_rt_hit_ns/pl_em_rt_ns + Δ_B·bl_tr_hit_ns/sp_tr_loop_ns`
* `G⁺` is defined the same way.

(d) Verdict:
* OPEN iff `mean(N) − 2SE ≥ 500`;
* CLOSED iff `mean(N⁺) + 2SE < 500` or `mean(G⁺) < 500`;
* otherwise UNDECIDED.

(e) Pin `pathlap=1 mutsite=1 bindlap=1` in both arm texts. A fixture must return NOT EVALUABLE when `bl_tr_us` is
absent or 0 in M.

Add these mutants: record not subtracted; CLOSED on N instead of N⁺; G used as the upper bound without Δ.

**RC6 (F6).** Fixture 2: require M-arm zeros only in frames 10–88 of M blocks. Edge frames are reported and do not
decide. Keep "any `*_bad` on any frame ⇒ FAIL".

Recommended, not required: F7 (restate the full rtfast predicate, or invalidate the memos on unarmed draws) and the F8
items.
