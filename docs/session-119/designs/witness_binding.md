# Session 119 — removability design: M1 witness verify and the binding resolution (`bl_res`, `bl_buf`, `bl_img`)

Read-only code study. No game run, no build, no source edit. Tags: **[M]** measured (run named), **[I]** inferred
(arithmetic on measured numbers, often cross-binary), **[U]** unknown. All code references are to the tree at
`fe8faf6` (`C:/kyty/KytyPS5`).

## 0. Data used and one caveat about the levels

Counts below are my own re-parse of `C:/kyty/s118/log_spk118.txt`, arm M (`takelap=1 bindlap=1 pathlap=1 mutsite=1`),
frames 10–88 of every block, `draws > 3000`, 2 997 frames, **means per frame** (script in my scratchpad, not a seal):

| counter | mean | counter | mean |
|---|---:|---|---:|
| `bl_prep_us` / `bl_prep_n` (= `bl_stage_n`) | 4 441 / 9 443 | `da_t_ver_us` | 1 274 |
| `bl_res_us` / `bl_res_n` | 3 384 / 50 400 | `da_t_pfb_us` / `da_t_pfa_us` / `da_t_cpy_us` | 315 / 683 / 482 |
| `bl_smp_us` / `bl_sd_us` | 377 / 416 | `da_hit` | 8 710 |
| `bl_img_us` / `bl_img_n` | 1 144 / 50 400 | `da_runs` / `da_runs_clean` / `da_singles` | 86 000 / 28 814 / 0 |
| `bl_buf_us` / `bl_buf_n` | 4 012 / 49 471 | `da_words` / `da_words_clean` | 463 097 / 53 216 |
| `b_texn` / `tex_hits` (memo hits) | 50 400 / 47 136 | `da_cl_look` / `da_cl_miss` / `p_creads` | 33 511 / 1 471 / 4 698 |
| `tnull_hit` / `texmemo_collide` / `texmemo_stale` | 1 482 / 1 773 / 7.4 | `ob_stream` / `ob_stream_kb` | 14 567 / 20 234 |
| `texfast_ok` / `texfast_no` / `texfast_rec` | 45 421 / 4 867 / 1 532 | `cb_copy` / `cb_copy_kb` | 8 156 / 800 |
| `sync_noop` / `bufepoch` / `ob_n` | 26 203 / 8 343 / 50 180 | `draws` / `dispatches` | 5 201 / 270 |

My means are ~5 % above the levels quoted in the brief (1 274 vs 1 211; 3 384 vs 3 213; 4 012 vs 3 868; 1 144 vs 1 095)
— a different window/estimator. I compute **unit prices on my rows** (level and count from the same frames) and quote
ceilings on my scale; multiply by ~0.95 for the brief's scale. Nothing below changes sides of 1 ms under that factor.

**Caveat that matters for every ceiling here:** all four levels are *traced* (`KYTY_FRAME_TRACE=lite`) levels.
`FrameStats::Enabled()` is an out-of-line call (`frameStats.cpp:160-164`) and every census block guarded by it runs in a
lite run and never in untraced play. Arm M also carried `takelap`/`bindlap`/`pathlap`/`mutsite` (`bindlap` alone
+357 µs, s85). One of these census blocks sits inside `da_t_ver` itself (§1.3).

## 1. What each counter times, and how they nest

### 1.1 `AheadTake` phases (gate `takelap`) — GuestGpu, inside `PipelineCache::m_mutex`, inside `mh_prog`

`AheadTake` is `pipelineCache.cpp:3165-3428`; the rolling chain is seeded from `da_take_us`'s timestamp (`:3175-3182`).

| counter | span | what is inside |
|---|---|---|
| `da_t_key_us` | seed → `:3192` | `ClassOf`/`Fingerprint`, `AheadHash`, `UserDataHash` |
| `da_t_prb_us` | `:3192` → `:3261` | probe loop, `TryGuardSlot`, `slot.Matches`, state → `AheadTaking` |
| `da_t_pfa_us` | `:3261` → `:3345` | eleven `PrefetchVectorData` (`:3265-3334`) **plus five census `FS::Add` (`:3335-3344`)** |
| `da_t_pfb_us` | `:3345` → `VerifyWitness:1048-1052` | `VerifyWitness` entry: `dawitloop` read (`:1009`), `FS::Enabled()` + `DrawAheadDirect` Add (`:1021-1027`), `direct` epoch test, live-run prefetch pass (`:1028-1044`) |
| **`da_t_ver_us`** | `:1052` → `:3360` | **live-run loop `:1053-1078`** (direct-pointer `SameRecordedWords`, `:978-991`), **clean-run loop `:1079-1143`** (one `CleanBackingPage` per clean run, `:652-767`), singles loop `:1144-1155` (0 in this scene), return |
| `da_t_cpy_us` | `:3360` → `:3421` | two `std::swap` or `CopyAheadResult`, slot retire |

`da_t_ver` is disjoint from every `bl_*` counter (different phase of the draw: program refresh vs bindings).

### 1.2 `bindlap` — GuestGpu, inside the render mutex, inside `mh_bind`

Per graphics draw (`renderDraw.cpp:2216-2265`) and per dispatch (`renderCompute.cpp:863-888`) the order is:
`PrepareBindings` (per stage) → `FindBuffers` → `PrepareBda` → `RebindImages` (per stage) → colour-target re-find →
`RebindBuffers` (per stage) (`descriptors.cpp:2656-2733`).

| counter | span (file:line) | content |
|---|---|---|
| `bl_prep_us` | `LapScope`, whole `PrepareBindings` `descriptors.cpp:2136-2349` | = `bl_res` + `bl_smp` + `bl_sd` + derived remainder (prologue incl. `prepared.Reset()` = `TextureBinding` dtors, `bindpack` kind mask `:2144-2147`, `has_gds` `:2337-2348`) = 4 441 − 3 384 − 377 − 416 = **264 µs** |
| **`bl_res_us`** ⊂ `bl_prep` | mark chain `:2162` → `:2271-2277` | `images.reserve` + per slot: `ResolveTextureWith` (`:1367-1712`) **and** `BindImage` (`:1782-1801`) |
| `bl_smp_us` ⊂ `bl_prep` | `:2276` → `:2291-2297` | `NativeSampler` (`:1730-1743`, sampler cache) |
| `bl_sd_us` ⊂ `bl_prep` | `:2296` → `:2303-2306` | `shader_data` copy from user data |
| **`bl_img_us`** | `LapScope`, whole `RebindImages` `:2499-2654` | repair loop `:2509-2521` (re-resolve via `ResolveTexture` only for dead/`needs_rebind` images), `slicecen` census (off), **`texfast` loop `:2551-2646`** (memo view or `FindTexture`) |
| **`bl_buf_us`** | `LapScope`, whole `RebindBuffers` `:2384-2487` | per slot `NativeStorageBuffer` (`:151-373`: null / direct const-bank ring copy `:241-276` / `ObtainBuffer` `:278` → `bufferCache.cpp:1126-1360` / aligned const-bank ring copy `:287-330` / `InvalidateMemoryFromGPU` for written `:351-353`); per stage `NativeUpload` of `flattened_srt` and `shader_data` into the stream ring (`:2466-2483`, `:1769-1780`) |

**Nesting:** only `bl_res`, `bl_smp`, `bl_sd` nest (inside `bl_prep`). `bl_img` and `bl_buf` are separate functions,
disjoint from `bl_prep` and from each other. `bl_res` is **not** inside `bl_img` or `bl_buf`. `FindBuffers`
(`ClampRangeSize` + `FindBuffer` per buffer slot), `PrepareBda`, the colour-target re-find and `ShadowQueue` are in
**no** `bl_*` span. `SetVulkanObjectNameF` (`:360`) is a no-op unless the debug dump is on (`vulkanCommon.h:36-39`).

### 1.3 A census block inside `da_t_ver` that untraced play never pays

`CleanBackingPage` (`pipelineCache.cpp:652-767`) runs, whenever `FrameStats::Enabled()`, the session-74 W8 "would a
persistent table have held this page" probe (`:664-696`): an out-of-line `Enabled()` call, `BackingMapEpoch()`,
`GpuDirtyGen::Read()`, a random slot of a **64 KiB `thread_local` table** (larger than L1d) and 1–3 `FS::Add`. Its only
output is `da_cl_pmiss`/`da_cl_pdrop`; its question was answered and `dawitcg` shipped in s74. The clean loop calls
`CleanBackingPage` once per clean run: 28 814 calls a frame inside `da_t_ver` (the other 4 698 are the specialization
reader, `p_creads`). At 8–15 ns a call [I] that is **0.23–0.43 ms of the 1.27 ms**. So the untraced verify is
≈ **0.84–1.04 ms [I]** on my scale (≈ 0.80–0.99 on the brief's). Precedent for counting such a removal as a program
gain: `daepceil` (s72, −0.17…−0.19 ms) removed a statistics vector built only under `FrameStats::Enabled()`.

## 2. Candidates

Prices on my rows: `bl_res` 67.1 ns/slot, `bl_img` 22.7 ns/slot, `bl_buf` 81.1 ns/slot, `da_t_ver` 146 ns/hit =
14.8 ns/run = 2.75 ns/word. Split of `bl_res` using s88's non-hit price 284 ns (`wit88b`, cross-binary [I]): non-hit
resolves 50 400 − 47 136 = 3 264 (= `tnull_hit` 1 482 + `texmemo_collide` 1 773 + stale 7) × 284 = 927 µs, so a
**memo-hit slot costs (3 384 − 927)/47 136 = 52.1 ns** = BindImage 8.49 (s87 [M]) + proof 15.08 (s88 [M]) + tail 15.00
(s88 [M]) + emit/loop remainder ≈ 13.5 [I].

### 2.1 Witness verify (`da_t_ver`)

**What repeats.** Each hit re-reads ~53 recorded words in ~9.9 runs (6.6 live, 3.3 clean) and compares them with guest
memory. The same tables (per-frame V#/T# tables) are verified by many takes a frame, and frame after frame; s69–s70
compared 3·10⁹ words without one stale verdict (`da_stale` = 0 again in `spk118`). The work is re-proving an unchanged
answer. What a skip would have to witness: that no writer changed any recorded word between the worker read and the
take (guest CPU, GPU writes for clean runs, host-side writes into guest memory — file reads, DMA_DATA, WRITE_DATA, EOP
labels written at PM4 parse time).

| # | candidate | ceiling (arithmetic) | tag | verdict |
|---|---|---|---|---|
| W0 | delete/gate the W8 census probe in `CleanBackingPage` (`:664-696`) | 28 814 × 8–15 ns = **0.23–0.43 ms**, in traced runs only; **0 in untraced play** | [I] | instrument tax, not work; safe by construction (nothing decides on it) |
| W1 | page-protection witness: skip the compare for runs whose page is tracked, write-protected (CPU-clean) at the worker read and at the take, with the region epoch unchanged | f_prot × (untraced verify 0.84–1.04 ms) − epoch checks; f_prot [U], and the per-frame tables that dominate are rewritten each frame, i.e. CPU-dirty ⇒ f_prot likely small | [I] ≤ ~0.3 | s70's closure (`regionManager.h:202-210`: the epoch does not move on a second write to a dirty page) forbids it for dirty pages; for protected pages it is sound only if **every** host-side writer announces through the tracker — unaudited |
| W2 | dedupe a run already verified OK in the current **sync-free interval** (same address, count, words; `GpuDirtyGen` unchanged) | live runs compare ~7 words through a prefetched direct pointer at ~5 ns (s88: 285 µs / ~55 k runs) — a table probe costs the same, gain ≈ 0; clean runs ~8–12 ns untraced: ≤ 28 814 × 10 ns = **≤ 0.29 ms** × repeat share [U] | [I] | < 1 ms |
| — | `dawitness=0`, `dawitloop=1/2` | 1.27 ms | [M] ceiling knobs | **unsound**, measurement only |
| — | move `AheadTake` out of `m_mutex` | tens of µs (s89: wait 42 µs/frame) | [M] | closed s89 |
| — | shrink prefetch A/B, take | not the verify; prefetch is a debt against three shipped defaults (s89) | [M] | not this design |

**Plainly: no witness candidate reaches 1 ms.** The untraced verify level itself is ≈ 0.8–1.0 ms [I]; the per-run
compare already costs about what any substitute witness lookup would.

### 2.2 Image resolution `bl_res` (3 384 µs; 50 400 slots)

**What repeats.** 93.5 % of slots hit the texture memo (`tex_hits`/`b_texn`); 84.9 % of image slots equal the same
slot of the previous draw of the same shader (s85 `R_img_sh` [M]); 31 % repeat an image inside their own stage (s86).
On a hit the loop re-derives from the same 32-byte T# the same `ImageId` and re-proves it: `DecodeNativeDescriptor`,
XXH3 of the `ImageResource` prefix (`:1464-1466`, a constant of the program), XXH3 of the 32 T# bytes, `% 4096`,
32-byte `memcmp`, `try_get` + five liveness fields (`:1473-1485`); then the tail (`ConfigureImageSource`
`textureCache.cpp:1243-1251`, `tick_accessed_last`, `TouchImage` `:493-514`, DCC-adoption check), the emit (a
`TextureBinding` with a ~584-byte `ImageDesc` copy, PLAN_82 item 3) and `BindImage`.

What any skip must keep (the correctness witness): the liveness proof per image (generation, `registered`,
`!needs_rebind`, `!depth_id`, `info.data`/`extent`); `BindImage` every draw (`is_bound`/`force_general`/
`shader_write`, cleared by `ResetBindings`, read by `AcquireRenderTargets` — s85/s87); `tick_accessed_last ==
AgeTick()` (GC safety); the DCC adoption when `MetaCompress` (pending fills, s9); `ConfigureImageSource`'s effect
(witnessed by `Image::bind_stamp`, the `texfast` idiom); and the memo `version` semantics that `texfast` relies on
(`descriptors.cpp:2558-2566`).

| # | candidate | ceiling (arithmetic) | tag | probability of safe removal |
|---|---|---|---|---|
| **R1** | **texture-memo conflict misses.** The memo is direct-mapped, 4 096 slots (`renderMemo.h:114`, index `memo_hash % TextureSlots`, `descriptors.cpp:1469-1471`); `texmemo2` (2-way, **same capacity**, plus an 80 KB key cache) is 0 in `gates_base.txt`. 1 773 collisions a frame, and `texfast_rec` 1 532 stores a frame show ping-pong eviction (every store also kills the slot's `fast_view`, `:1705`). Each collision runs the full resolve (tile layout, `FindImage`, validation, memo store). | miss price c from 927 = 1 482·n + 1 780·c with null path n ∈ [0; 60] ns ⇒ **c ∈ [471; 521] ns**. Fixable = stores 1 532 … all collisions 1 780: 1 532 × (471 − 52.1) + 1 532 × 35.4 (RebindImages `FindTexture` 55.02 − fast 19.66, s85) = **0.70 ms** … 1 780 × (521 − 52.1) + 1 780 × 35.4 = **0.90 ms** | [I] | **~0.95** — capacity/associativity of an already re-validated memo; the hit proof is unchanged; no new witness |
| R2 | **per-stage image-block memo**: when a stage slot (`m_graphics_bindings` reuses the object) sees the same program and byte-identical `snapshot.images` block as its previous draw, keep `prepared.images` and skip decode + hashes + memcmp + memo-line touch + emit + the idempotent part of the tail; keep liveness, `tick_accessed_last`, DCC check, `BindImage` | skippable ≈ 8 (proof minus liveness) + 12 (tail minus required stores) + 13.5 (emit) ≈ 33.5 ns [I] per repeated hit slot; population ≤ 0.849 × 47 136 = 40 033 (assumes every repeating slot sits in a fully repeating image block) ⇒ ≤ 1.34 ms − stage memcmp 9 443 × ~8 ns ⇒ **≤ 1.27 ms upper**; at an images-only stage repeat share of 0.5 ⇒ ~0.7 ms | [I], share [U] | ~0.3 — skips `ConfigureImageSource`/`TouchImage` side effects on a `bind_stamp` witness; `prepared.images` lifetime must be restructured (`Reset()` clears it, `descriptors.h:117-135`); s87's blockers for across-draw skipping were "the witness and `image.Transit` PRE-state" — the latter lives in `CommitBindings`, not here, so it does not apply; the former is exactly the per-image liveness R2 keeps |
| R3 | `ImageDesc` by reference on a memo hit (PLAN_82 item 3, never built) | desc copy ≤ half the 13.5 ns emit: 47 136 × ~6.5 ns ≈ **0.31 ms** | [I] | ~0.6 — five consumers; same-draw slot rewrite hole (PLAN_82:160) |
| R5 | hoist the `ImageResource` key hash (constant per program resource) into a per-program array | XXH3 over ~64 B ≈ 4–6 ns × 50 400 = **0.20–0.30 ms** | [I] | ~0.95 (immutable input; do NOT use the `texmemo2` pointer cache — 80 KB > L1, PLAN_82:376) |
| — | skip `BindImage` | 8.49 × 50 400 = 0.43 ms | [I] | 0 — required per draw (s85/s87) |
| — | amortise duplicates inside a stage | 514 µs MARGINAL | [M] s88 | closed |

### 2.3 Image rebinding `bl_img` (1 144 µs; 22.7 ns/slot)

96 % of it is the `texfast` fast path, 45 421 × 19.66 ns ≈ 0.89 ms, which **is** the proof (bind_stamp, pending
levels, `TextureSourceSettled`, slot version — s85 §4). The rest: null T# bindings are never `texfast`-eligible
(the null memo emits `memo_index = UINT32_MAX`, `:1425`, ⇒ `slot == nullptr` at `:2558`): 1 482 × 35.4 ns =
**0.05 ms** [I]; collision re-records are already inside R1. **No candidate in `bl_img` above 0.1 ms.**

### 2.4 Buffer rebinding `bl_buf` (4 012 µs; 49 471 slots; 81.1 ns/slot)

**What repeats.** Per slot the same guest range resolves to the same buffer with the same no-op sync (`sync_noop`
26 203 + `bufepoch` 8 343 a frame); CPU-dirty small ranges are copied into the stream ring every bind (`ob_stream`
14 567 copies, 20.2 MB a frame, 1 389 B each) and const-bank aligned copies (`cb_copy` 8 156, 0.8 MB); per stage the
`flattened_srt`/`shader_data` payload is uploaded (s95: 9 397 uploads, 218 B each). s62: 84 % of ring copies are
byte-equal to the previous copy of the range, 98 % with the previous ring slot intact.

| # | candidate | ceiling (arithmetic) | tag | probability |
|---|---|---|---|---|
| — | memo the ring copy by guest memory | copy ≈ 20.2 MB / 21.5 GB/s (s78 `ob_stream_us` 897 µs on 19 MB) = 0.94 ms, of which only the WC write + `Map`/`Commit` is saveable | [I] | **closed s62**: page is CPU-dirty, i.e. writable without a fault, so no epoch witness; the content witness costs the read |
| B2 | **dedupe ring copies within a sync-free interval** (same queue, same submission, no WAIT_REG_MEM / RELEASE_MEM / EVENT_WRITE_EOP / EOS / WRITE_DATA / DMA_DATA / COND_EXEC / SET_PREDICATION since the earlier copy): reuse the earlier ring offset **without comparing bytes** | d × (0.94 + 8 156 × ~21 ns = 0.17) − probe 22.7 k × ~5 ns (0.11) ⇒ at d = 0.84 (s62 `cb_same` share as an upper proxy) **≤ 0.82 ms**; d [U] | [I] | ~0.4 — **new witness, ordering-based, not memory-based**: a CPU write not ordered by any GPU-visible sync against two draws of one interval may legally land after both, so both may see the earlier copy. It needs: interval id bumped at every packet above and at every submission start; GPU-write sequence unchanged (`NoteGpuWrite`, image→buffer and DMA copies); `StreamBuffer::Generation()` unchanged (ring not wrapped); same (vaddr, size, alignment). s62's closure does not cover it (it demanded a memory witness), but "unshakeable correctness" must accept a weak-ordering argument, and every emulator-internal write into guest memory must be a sync point — to be audited adversarially |
| B3 | `buffast` (existing gate, default 0): memo the `ObtainBuffer` answer with `RangeWriteEpoch` + `m_registration_epoch` (`bufferCache.cpp:1155-1242`) | eligible read-only answers ≤ ~30 k; saved `FindBuffer`/`TouchBuffer`/`UploadEpoch`/`HasCurrentUpload`/no-op `SynchronizeBuffer` minus its own epoch read and TLS probe ≈ ≤ 15 ns ⇒ **≤ 0.45 ms** | [I] | ~0.9 (self-check `buffastcheck`, `bfast_bad` 0 in s58/s59); s58 "in noise" was an inter-phase ±1.4 % method, never ABBA |
| — | payload memo (`NativeUpload`) | 9 397 × ~25 ns ≈ 0.24 ms; payload repeats N−1 on 8 draws a frame | [I]/[M] s95 | closed (M2, s95) |
| — | sticky CPU-dirty pages | 28 candidate pages a frame | [M] s57 | closed |
| — | BDA for ring-backed cb slots | +10.8 ms sync in OLD regime | [M] s94 | closed |

**Plainly: no single `bl_buf` candidate reaches 1 ms [I].** The largest identifiable piece of `bl_buf` is the
ob_stream memcpy (~0.94 ms [I]) and it is data movement of CPU-rewritten bytes.

## 3. Ranking (ceiling × probability of a correctness-safe removal)

| rank | candidate | ceiling (my scale) | p | product |
|---:|---|---:|---:|---:|
| 1 | R1 texture-memo conflicts | 0.70–0.90 ms [I] | 0.95 | **0.67–0.86** |
| 2 | B2 ring-copy interval dedupe | ≤ 0.82 ms [I] | 0.4 | ≤ 0.33 |
| 3 | R2 stage image-block memo | ≤ 1.27 ms upper, ~0.7 typical [I] | 0.3 | 0.21–0.38 |
| 4 | W0 witness census probe (traced metric only) | 0.23–0.43 ms [I] | 1.0 (untraced gain 0) | 0.23–0.43 traced / 0 play |
| 5 | B3 `buffast` | ≤ 0.45 ms [I] | 0.9 | ≤ 0.40 |
| 6 | R5 resource-key hoist | 0.20–0.30 ms [I] | 0.95 | 0.19–0.29 |
| 7 | R3 `ImageDesc` by reference | ≤ 0.31 ms [I] | 0.6 | ≤ 0.19 |
| 8 | W1 / W2 witness shortcuts | ≤ 0.3 ms each [I] | 0.3 / 0.5 | ≤ 0.15 |

**By reading, not one candidate has a removable part ≥ 1 ms**, and this program's upper estimates have run 2–20×
high. The only group whose [I] sum crosses 1 ms is the **image-resolve package on the `bl_res` loop** (R1 + R5 +
R2 or R3; populations of R1 (misses) and R2 (hits) are disjoint; R5/R3 overlap R2): ≈ 0.7–0.9 + 0.2–0.3 + 0.3–0.7 ≈
**1.2–1.9 ms upper [I]**. Under the program's rule this opens **no track** now; it justifies one measurement build.

**Pursue first: R1**, as the head of that package. Correctness witness it needs: *none new* — the hit path keeps its
whole proof (resource key + 32-byte T# `memcmp` + liveness of the cached image), and the design constraints are:
an entry's `version` moves whenever it is replaced or invalidated; `memo_index` stays a stable address of one entry
(set × ways + way) so `RebindImages`' `texfast` eligibility test (`:2558-2566`) keeps meaning "same entry, same
fill"; an N-way tag array must stay compact (a 16 K-entry table of ~650-byte `Texture` entries is 10 MB and would
slow the 47 k hits). Whether associativity or capacity is needed is decided by the measurement below.

## 4. One measurement build (all measurement-only, default 0, nothing under `src/graphics/shader/**`)

| candidate | smallest measurement that makes the ceiling [M] |
|---|---|
| R1 | (a) `tm_full_ns`/`tm_full_n` split collide/stale/null — the `Enabled()` two-timestamp idiom from the memo decision (`:1476`) to the return, so the miss price is [M] in lite; (b) a **shadow tag census** in the `da_cl_pmiss` idiom (tags only, never read back): predicted collisions for 4-way and 8-way at 4 096 entries and for 16 K direct (`tm_p4`, `tm_p8`, `tm_p16k`); ceiling [M] = (`texmemo_collide` − predicted residual) × `tm_full` price + re-records × s85 price |
| R2 | in `slotstat`: `sl_img_blk_sh` / `sl_img_blk_slots` — stages (and their image slots) whose whole image block equals the previous same-shader draw of that stage slot; price via a `bindwit`-style moved mark if the share is large |
| R5 | a moved mark around the key hash on alternating stages (`bindwit` idiom), or fold into R1's package ABBA |
| R3 | none cheaper than building it; ride on the package ABBA |
| B2 | `rc_dup`/`rc_dup_b` — ring copies whose (vaddr, size) is already in a per-interval table with ring generation and GPU-write sequence unchanged (interval bumped at the packets listed in B2); and move `ob_stream_us`/`cb_copy_us` from `TimingsEnabled` to the `Enabled()` idiom so the copy price is [M] in lite |
| B3 | **zero code**: one sealed pinned ABBA `buffast=0|1` on `d3a981a2` (verify arm `buffastcheck=1`, `bfast_bad` must read 0) |
| W0 | a knob that skips `pipelineCache.cpp:664-696`; ABBA → Δ`da_t_ver_us` [M]. Report it as an instrument tax (0 for untraced play) |
| W1 | at the take: `da_run_prot`/`da_word_prot` — runs/words whose page is tracked and CPU-clean (`IsRegionCpuCleanFast`) with the region epoch unchanged since the worker read |

## 5. Adversarial notes on my own numbers

* The 284 ns non-hit price and the 15.08/15.00/8.49 ns parts are from s87/s88 binaries (`bal87a`, `wit88b`); the
  52.1 ns hit price is derived by subtraction on today's rows. If the non-hit price has grown, R1 grows and the hit
  budget (hence R2/R3/R5) shrinks — R1 + R2 is roughly conserved.
* R1's "fixable" assumes the conflicts are associativity/capacity misses. Non-storable keys (overlap views,
  stencil association, `store == false`, `:1695-1696`) are re-resolved every time whatever the table; `texfast_rec`
  (1 532) vs `texmemo_collide` (1 773) suggests ~240 a frame of those; they are excluded from the low bound.
* s56 measured `texmemo2` "0 % in both scenes" — inter-run, a withdrawn method, and a package with the key cache;
  it neither confirms nor kills R1.
* B2's legality argument is mine and unaudited; it must survive a hostile review before any code (EOP labels are
  written at PM4 parse time, so RELEASE_MEM must end an interval; VideoOut flips, `SET_BASE`/indirect args, and any
  host write into guest memory need the same treatment).
* W0 improves every traced measurement of this program by 0.2–0.4 ms and the player's frame by nothing; calling it
  a speed gain would repeat the `daepceil` bookkeeping, so say which metric moved.

## 6. Summary table

| candidate | what repeats | ceiling µs [tag] | measurement to confirm | risk |
|---|---|---:|---|---|
| R1 texture-memo conflicts (`bl_res`, +`bl_img` re-record) | same T# keys evicting each other every frame (1 773 collisions, 1 532 stores) | 700–900 [I] | `tm_full` miss timer + shadow tag census (4/8-way, 16 K) | low: memo re-validated on every hit, no new witness |
| R2 stage image-block memo (`bl_res`) | whole image block of a stage slot equal to the previous same-shader draw | ≤ 1 270 upper, ~700 typical [I] | `sl_img_blk_sh` census in `slotstat` | high: skips tail side effects on a `bind_stamp` witness; `prepared.images` lifetime |
| R5 resource-key hoist (`bl_res`) | XXH3 of a per-program constant, every slot | 200–300 [I] | moved mark / package ABBA | very low |
| R3 `ImageDesc` by reference (`bl_res`) | 584-byte desc copy per hit slot | ≤ 310 [I] | package ABBA | medium: five consumers, same-draw rewrite |
| B2 ring-copy interval dedupe (`bl_buf`) | same (vaddr,size) copied again in one sync-free interval | ≤ 820 [I] | `rc_dup`/`rc_dup_b` + lite `ob_stream_us` | medium-high: new ordering witness, audit first |
| B3 `buffast` (`bl_buf`) | same range → same buffer, no-op sync | ≤ 450 [I] | zero-code ABBA `buffast=0\|1` | low: self-check exists |
| W0 W8 census probe (`da_t_ver`) | a closed question re-asked 28 814 times a frame | 230–430 [I], traced only; 0 in play | skip-knob ABBA | none (instrument) |
| W1 protected-page witness (`da_t_ver`) | unchanged words on write-protected pages | ≤ ~300 [I] | `da_run_prot`/`da_word_prot` | high: every host writer must announce |
| W2 interval run dedupe (`da_t_ver`) | same run verified again in one interval | ≤ 290 [I] | reuse B2's interval id + a run table census | medium |
| — BindImage, texfast fast path, stage duplicates, payload memo, sticky pages, ring memo by content, BDA cb | — | closed s85–s95 | — | — |
