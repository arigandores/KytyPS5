# Session 120 — adversarial review of `r2.md` (knob `r2cen`, the stage image-block repeat census)

Read-only review. Nothing was built, run or edited under `src/`. Tree: `C:/kyty/KytyPS5` at HEAD `8f8a5f1`. That is
`996d565` plus two commits that touch only `docs/ROADMAP.md` (`git diff 996d565 HEAD -- src` is empty), so every
file:line of the design still applies. Tags follow the design: [M] measured, [I] inferred, [U] unknown.

An earlier version of this file (01:50) is superseded. Its copy is at
`C:/Users/<user>/AppData/Local/Temp/claude/C--Users-<user>-OneDrive-Desktop-ps5-em/314bf4dc-f9bb-42ec-a084-04f00b8e50d0/scratchpad/r2_review.prior_0150.md`.
Every claim below was re-derived from the source. Points kept from that version were checked again. One of its claims
(the keying comparison with s85) is wrong and is corrected in §3.

**Verdict: SOUND_WITH_CHANGES.**

What holds up:
* The census changes no emulator state at any value.
* Its reuse predicate R is exactly the memo-hit condition on clean stages. It is not optimistic.
* Booking the time by counter selection on `bindlap`'s own stamps is correct.

What does not hold up:
* Its **verdict rules are stale**. ROADMAP s120 item 2 (`6f691cb`, 01:35, eight minutes after `r2.md`) cut the
  track threshold to 0.5 ms and allowed packages.
* At 0.5 ms the design's own expectation (C_pt ≈ 0.5–0.8 ms) sits **on** the threshold. Each of the eight biases in
  §5 (0.05–0.5 ms each, in both directions) then decides the verdict.
* The bracket `C_lo ≤ true ≤ C_up` is **not established**.
* The bad check catches less than §8 claims.

Ten required changes are listed in §8. None of them touches the image loop.

---

## 0. The decisive change after the design was written: ROADMAP s120 item 2

`docs/ROADMAP.md:2538-2550` (`6f691cb`) says:
* (a) A track opens on a **measured net ceiling ≥ 0.5 ms a frame**, net of the check price a real memo also pays,
  with every `*_bad` = 0.
* (b) Candidates on one path are summed as a package, "R1 + R2 — one image-resolve package if their populations do not
  overlap", and the package is judged by the same threshold.
* (d) "The 1 ms threshold in the verdict rules of the s120 designs is replaced by 0.5 ms".

`r2.md` §6 rules 2–4, fixture 8 (the 999.9/1 000.0 boundaries), the §0 conclusion ("R2 alone is expected to close")
and §6 "Expected" all use 1 000 µs. Rule 4 sends R2 to "the package sum with R1" with no formula, no bracket member and
no SE. Change C1 fixes this.

The package is disjoint in the ROADMAP's sense. Within one call a slot is either a memo hit (R2's clean population) or
a miss (R1's population). One interaction is not additive: a miss that R1 fixes becomes a hit and can turn a mixed stage
into a clean one. The sum of the two separately measured ceilings therefore **under-states** the package. That is
conservative for opening and must be written down. R3 (desc by reference) and R5 (resource-key hoist) are **inside**
R2's removable part (§1.1: the emit copy and the resource-key XXH3), so they must never be added to R2.

## 1. File:line claims — verified

| claim (design) | source | verdict |
|---|---|---|
| `PrepareBindings` `descriptors.cpp:2129-2349`; `bindlap` LapScope `:2136-2141`; `Reset()` `:2142`; `bindkey` `:2148-2158` (`previous_key` `:2150-2154`); comment `:2159`; `bl_t` `:2162`; loop `:2211-2267` (resolve/emit `:2223-2228`, `BindImage` `:2259-2260`); `bl_res` close `:2270-2277`; `bl_sd` `:2303-2306`; `blmove` `:2307-2316`; `bindalt`/`bindwit` `:2317-2336`; GDS/end `:2337-2349`; anon namespace `:2048-2127`, anchor `:2124-2127` | as stated | OK |
| resolve `:1368-1712`: `Scope` `:1371-1372`, decode `:1373`, null path `:1385-1439` (bindpack hit test `:1393`), `LodStats::Touch` `:1442-1444`, lod trace `:1445-1455`, resource key `:1462-1466`, hash/index/slot/memcmp `:1467-1475`, liveness `:1482-1485`, tail `:1499-1518`, emit `:1528-1529`, stale `:1531-1535`, store `:1695-1711` | as stated | OK |
| `NullTextureKey` `:589-604`; `Memo()` `:1723-1728`; `BindImage` `:1782-1801`; `ResetBindings` `:2025-2032`; `RebindImages` `:2489-2654` (repair `:2509-2521`, texfast `:2546-2646`, eligibility `:2558-2566`, `fast_view`/`fast_stamp` `:2600`, `:2615-2616`) | as stated | OK |
| slotstat idiom `:3015-3087` | tables `:3015-3048`, census `NoteSlotStat` `:3089-…` | minor: the census body starts at `:3089` |
| §1.2 "DCC clears … `descriptors.cpp:1841-1845` callers" | `:1841-1845` are the two **definitions**; the per-slot caller is `:3747` (CommitBindings transit), the other `:2015` | cosmetic |
| `descriptors.h:21-37`, `:71-136`, `Reset()` `:117-135`, `images.clear()` `:123` | as stated | OK |
| `render.h` `BindImage` `:387`, `m_bound_images` `:402`, `m_memo` `:559` | as stated | OK |
| `renderMemo.h` `MemoHashBytes` `:30`, `Texture` `:62-75`, `version` `:70`, `TextureSlots` `:114` | as stated | OK (and see §5: `version` sits **after** the ~584-B `desc`, `:67-70`) |
| `textureCache.h` `MetaEpoch` `:75-77`, `GetImage`→`TouchImage` `:102-106`, `m_meta_epoch` `:306`, `m_gc_tick` `:312`, `friend class RenderExecutor` `:324` | as stated | OK |
| `textureCache.cpp` `TouchImage` `:493-514`, `ConfigureImageSource(Unlocked)` `:1219-1251` (`is_bound` test `:1227`), `AdoptPendingDccForTexture` `:3178-3217` | as stated | OK |
| `renderContext.h:53` `AgeTick`; `gpuTimeProfiler.h:52` / `gpuTimeProfiler.cpp:53-55` (path `src/graphics/host_gpu/renderer/`); `videoOut.cpp:1195` `SetFrame`; `lodStats.h:31-37` | as stated | OK |
| `frameStats.h` `ScNs`/`Count` `:1942-1943`, `Enabled` `:1996`, `NowNs` `:2041`, `Add` `:2044-2055`; `videoOut.cpp` `sc_ns` `:2582`, `bl_res_us/_n` `:2080-2081`; `gates.h` `Spine`/`Count` `:607-608`; `gates.cpp` `spine` `:411`, `}};` `:412` | as stated | OK |
| call sites `renderDraw.cpp:2222`, `:2242`, `bindspare` `:2229-2249`; `renderCompute.cpp:863` | as stated | OK |

The pseudo-code compiles in substance:
* `ImageInfo::type` is `Prospero::ImageType` (`imageInfo.h:66`).
* `ImageSubresources` has a defaulted `<=>` (`imageInfo.h:39`).
* `ImageViewInfo::operator==` compares integers only (`imageInfo.h:175-182`), so no NaN trap.
* `SlotId` has a defaulted `<=>` (`slotVector.h:27`) and `try_get` checks the generation (`slotVector.h:50-61`).
* `DescriptorValue::operator==` exists (`ResourceSnapshot.h:14-16`).
* `GpuTimeProfiler::Frame()` is already used in `descriptors.cpp` (`:2426`).
* `NullTextureKey` is file-`static` and declared above the census.

Two small defects:
* `R2Log` as "one helper with one `static` budget per tag" needs two statics, one per call site, or the budget passed
  in.
* No existing gate/knob/counter name collides with `r2cen` / `r2_*`. `FindAssignment` requires a separator before the
  name and `=` after it (`gates.cpp:458-470`). An arm text must stay under 512 B (`gates.cpp:482`).

## 2. Does it change behaviour?

**At `r2cen=0`: no.**
* The only additions are one `Gates::Value`, which is two relaxed loads inline (`gates.h:642-647`), a few register
  selects, and the `if (r2 != 0)` at the end.
* With `bindlap=1`, `r2_res_ns = bl_now − bl_t` runs at the head of `bl_smp` in both arms. The `r2 != 0 && bl_t == 0`
  test and `uint64_t r2_res_ns = 0` sit **inside** `bl_res`'s span (after `:2162`, before `:2272`). These are one or
  two register operations, identical in P and M. §3.7(b) and §9's "0 instructions inside `bl_res`" are therefore
  slightly overstated, and it is harmless.
* No allocation, no stamp, no `Enabled()` call.
* `r2`, `r2_meta0` and `r2_t0` are live across the loop, so its register allocation can change against `d3a981a2`
  (not against M). "Byte-for-byte" holds at source level only.

**At `r2cen=1/2`: only timing, log lines and one allocation.**
* **State.** The census never calls `GetImage`, `TouchImage`, `Memo()` (it reads `m_memo.get()`), `FindImage`, or
  `m_slot_images[]`, which `EXIT_IF`s. It uses `try_get`. It takes no lock and writes no `Image`, memo slot, LodStats
  bank or `m_bound_images`. `texlru_n/_rep`, `tex_hits`, `b_texn` and `tnull_*` are untouched.
* **Allocation.** `R2Table` is about 196 KB (`R2Slot` ≈ 192 B × 64 × 16), value-initialised. `scratch.reserve(64)` adds
  about 41 KB. Both are allocated once, at the first armed call, under the render mutex, outside the window. After that
  nothing allocates: `scratch` elements have empty `mip_views`.
* **EXIT.** No new reachable `EXIT`:
  * `DecodeNativeDescriptor`'s `EXIT_IF(dword_count < 8)` (`descriptors.h:247`) runs only on values the loop already
    decoded.
  * `NullTextureKey`'s `EXIT` (`:596`) has the same condition as `NullTextureDesc`'s (`:619`), which the real null path
    runs at either `bindpack` value.
* **Ordering.** Nothing is reordered. The census reads `prepared.images` before `RebindImages` touches it.
* **Other scorers' counters.** The census cost lands in P's `bl_prep_us` remainder, `mh_bind`, `a_hold`, `cpu_gpu_us`
  and `dt`. It does not land in `bl_res`, `bl_img`, `mh_emit` or `pl_em_*`, which `spcen` and R1 read. Scorers parse
  `FrameTrace-x` by token name (`g2_119.py:155`, `spk118.py:122`), and the log line is built with `fmt::sprintf` into a
  `std::string` (`log.h:57-62`). Adding 31–40 fields therefore truncates or shifts nothing.
* **Thread safety.** The census runs on GuestGpu under the render mutex, at the only three call sites. It reads the same
  unlocked image fields the real hit path reads. `m_gc_tick` is written by `RunGarbageCollector` on the same thread
  (`textureCache.cpp:3292`, `:3357`). `t_r2` is `thread_local`, which is valid only with `m4baton=0`. There is one
  `RenderExecutor` and one memo per `RenderContext`.

## 3. Is R ("would hit") as strict as a real reuse? Yes on clean stages — with pins that must be asserted

For a non-null slot, R means: the T# is equal (W2), the program is equal (W1), the memo slot's `version` is unchanged
since the stored element, and the image passes the five-field liveness test. This is **equivalent** to "the full path
takes the memo hit and returns this element", for these reasons:

* **Same program ⇒ same `ImageResource` bytes ⇒ same `resource_key`, hash and index** (`:1462-1471`), with
  `texmemo2=0`. Program objects are never freed: `Permutation`s live in a `std::deque` (`pipelineCache.cpp:1973`) and
  dropped sources go to `retired_sources` (`:3708`). Note 11.5 (pointer reuse) is therefore over-cautious and harmless.
* **Every write** to `valid`/`dwords`/`resource_key`/`image_id`/`desc` bumps `version` (`:1531-1535`, `:1698-1708`). A
  tree-wide grep shows the only other writes are `fast_view`/`fast_stamp` (`:2600`, `:2615-2616`). The memo is never
  reset (`:1723-1728`).
* **Post-loop evaluation is exact for clean stages.** If R holds after the loop, the version did not move, so that slot
  took the hit at slot time. Hits change no liveness field: `ConfigureImageSourceUnlocked` may `UntrackImage` or
  `MarkBufferModified`, but touches neither `registered` nor `needs_rebind` (`textureCache.cpp:583-597`, `:1219-1241`).
  Adoption changes only `metadata` (`:3205-3207`). `BindImage` changes only `is_bound`/`force_general`/`shader_write*`.
  `needs_rebind` is set only in `FindImage` paths (`textureCache.cpp:954`, `:1085`), which a clean stage never runs. On
  mixed stages the evaluation is conservative, as stated.
* **The held element a real R2 keeps is harmless beyond (id, desc, index, version).** `RebindImages` rewrites
  `image_view` and clears `mip_views` on every slot (`:2553`, `:2604`, `:2608`, `:2634`, `:2640`). `CommitBindings`
  writes `binding.layout` on every slot with no `continue` before it (`:3815`). The previous draw's values never reach
  a consumer.
* **Keying.** R2's per-stage-TYPE "previous" plus same-program test is **the same keying s85 used**.
  `NoteSlotStat(program.stage, program.shader_hash, …)` (`:3831`) keys `s = stage % 16` (`:3094`) with
  `same_shader = shader == g_slot_prev.shader[s]` (`:3098`, `img_same_sh` `:3131`). The prior review's claim that s85
  is "per same shader" and not comparable is wrong. Rule 5's comparison is legitimate, noting that s85 compares
  view + layout after `RebindImages` while R2 compares T# + memo version. A per-program-keyed variant (A,B,A,B) remains
  unmeasured. That is a scope note, not a defect.

Witnesses a **real** R2 needs that the census only has through pins. The census must **assert** them (C7):
* `bindpack=1`. The null R is the bindpack null-memo hit test (`:1392-1393`). `bindpack` is **absent** from
  `C:/kyty/s120/gates_base.txt` and defaults to true (`gates.cpp:204`).
* `texmemo2=0` (index function).
* `m4baton=0` (thread-local table).
* A gate epoch for `texmemo2`/`bindpack`/`metalock` flips. This is needed by a prototype only.

Missing belt-and-braces: R does not include `slot.valid && slot.image_id == s.id`, the texfast eligibility terms
(`:2561-2563`). Today they are implied by `version`, but a witness should state them (C5).

## 4. The bad counter: what it can and cannot catch

`r2_bad` counts R slots whose fresh id or desc-key differs from the stored element.
* Under the invariant it is 0 by construction, and no write today can break it (§3).
* The claim "0 **iff** the invariant holds" (§8) is false. Four gaps:

1. **Silent key change is invisible.** Suppose `dwords`/`resource_key`/`valid` change without `version++`. The fresh
   path then misses (Collide/Empty), runs the full resolve and **stores**. That bumps the version, so the post-loop R
   reads false and nothing is counted. A real R2 evaluating R at slot time would have reused.

   **Exact detector (verified case by case, `texmemo2=0`).** Take an equal-T# slot whose fresh `memo_index` equals the
   stored one, with the stored index valid.
   * A hit shows a version delta of 0.
   * Every legitimate path shows a delta ≥ 2:
     * stale then store: +2;
     * eviction by another key (+1) then re-store (+1);
     * a stale without a store, by this or another stage, leaves `valid=false`, so the next resolve stores (+1 more) or
       emits `UINT32_MAX` (excluded);
     * the previous `RebindImages` repair (stale +1, then store +1 or Empty-store later).
   * A delta of **exactly +1** means the resolve found the unchanged slot not matching its own key.
2. **The fresh `memo_index`/`memo_version` are never compared.** These are exactly what texfast consumes
   (`:2558-2562`), and what a reuse hands on. An index-function instability that lands on another slot with equal
   content passes unseen.
3. **`R2DescKey` is a subset.** It omits `pitch`, `bytes_per_block`, `samples`, `bgra16`, `stencil`,
   `htile_clear_mask`, `metadata.range.size`, `metadata.dcc_alpha_msb` and `mip_layout`. The miss path writes all of
   them (`:1635-1660`) and a reuse hands on the whole `ImageDesc`.
4. It is not an oracle of image correctness. The design says so, correctly.

With C5 applied, `r2_bad + r2_bad_key` directly guard the invariant that R2 and texfast both rest on. That is all a
census can do. The real verify belongs to the prototype's own gate (rule 3).

## 5. The ceiling: every term's direction

S, Z are the clean non-null and null slots. Numbers are [I] unless tagged.

| # | term / defect | bias on C | size | risk |
|---|---|---|---|---|
| a | **`CHK`, `ST`, `r2_rm_ns` include one stamp pair each.** `NowNs` is out of line: function-static, `__rdtsc`, a double divide (`frameStats.cpp:198-205`). A pair costs 8.35 ns [M s101 `cbmove`], about the size of W1+W2 itself | C_up/C_pt/C_lo **low**; C_rp high | ≈ 8.35 ns × (≈9.4 k + storing stages ≈ 3–5 k) ≈ **0.10–0.12 ms** | **false CLOSE** |
| b | **W2 is priced hot, post-loop, but a real R2 pays it pre-loop, cold.** M1-hit snapshots reach GuestGpu by `std::swap(resources, slot.snapshot)` (`pipelineCache.cpp:3413`), written by a worker core. The first GuestGpu touch of `snapshot.images` (3–4 lines a stage) is the loop's decode, so T* books that cross-core transfer as removable. A real R2's W2 would pay it | C_pt/C_lo/C_rp **high** | [U], 0.1–0.5 ms plausible | **false OPEN** |
| c | **`V = 4.0 ns` ignores where `version` lives.** `version` is after the ~584-byte `desc` (`renderMemo.h:67-70`), about 600 B from `dwords`, on its own line. The full path touches that line only at the emit (`:1528-1529`). R2's per-slot check must still fetch it, and a 2.6 MB memo is not L1-resident | C_pt **high** | +3–10 ns × S ≈ 0.1–0.4 ms | **false OPEN** (rule 4). C_lo is covered by P = 15.08 |
| d | **R1's in-loop census in the same P arm.** r1.md §6 puts `R1Hit` (8–15 ns) plus `Enabled()`/RNG (~3 ns) on **every hit**, and 120–300 ns on misses, inside `ResolveTextureWith`, inside `bl_res`. Clean stages are all hits. `f` removes only the uniform part. r1.md §11 itself says "the R2 scorer must subtract R1's self share … or R2 must run in an arm without `r1cen`" | ± | about −8 % … +2 % of T* ≈ **±0.05–0.2 ms** | both |
| e | **`B = 8.49` [M s87] in C_up is a cross-binary constant.** Rule 2's "closed independently of the kept-price constants" is false: B·(S+Z) ≈ 0.2–0.4 ms of C_up | C_up low if BindImage is cheaper today | 25–48 µs per ns of B error | **false CLOSE** |
| f | **`Reset()` destructors** (`descriptors.h:123`) are a removal a swap-held R2 gets, excluded from C_up | C_up low | ≤ 2 ns × (S+Z) ≈ ≤ 0.1 ms | **false CLOSE** |
| g | **The tail `TouchImage` (`:1501`) is always redundant.** `BindImage` → `GetImage` → `TouchImage` (`textureCache.h:102-106`) touches the same image in the same slot iteration. With `texlru=1` the second touch returns early. The end state (`frame_accessed_last`, `lru_touch_tick`, LRU order) is identical; only the `texlru_n/_rep` counts differ. §1.2's condition ("only if `m_gc_tick` and `Frame()` equal") is wrong, and `r2_cl_lru` asks a question with no bearing on the decision | C_pt, C_lo **low** | 2–4 ns × S ≈ 0.05–0.19 ms | false CLOSE |
| h | **Traced-only work inside T\*.** `Scope resolve_scope` counts in lite (`frameStats.h:2079-2090`, `:1371`) and `Add(BindTexMemoHits)` runs per hit (`:1515`), `Add(NullTexHits)` per null slot. They cost ≈1.2 ns each in lite and ≈0 in play (`Add` returns on `g_count_limit = 0`, `frameStats.h:2046-2048`). This is the s119 W0 / `daepceil` lesson | C high for play | ≈ 1.2 ns × (2S + Z) ≈ 0.06–0.12 ms | false OPEN for play |
| i | `LS = 3.0` ns: `LodStats::Touch` is a function-static guard plus a locked `fetch_add` plus a load and CAS loop (`lodStats.h:25-37`) ≈ 5 ns | C_pt/C_lo high | ≤ 0.09 ms | minor |
| j | `ST` is measured on the census table's 192-byte stride. A real R2 stores T# words contiguously | C low | small | minor |
| k | Per-stage fixed work inside the span (`reserve`, the gate locals `:2174-2211`, `blm_t0` `:2210`) that a real R2 still pays | C high | tens of µs | minor |
| l | Clean stages whose DCC check reaches the lock + `std::map::find` (`textureCache.cpp:3179`, `:3191`) cost more than the all-hit average behind T = 15.00. `r2_cl_dcc` is counted but **unused** | C_pt/C_lo high | small | minor |

**Conclusion.** At 1 ms these errors were mostly second order. At 0.5 ms they are not:
* (a), (e), (f) and (g) push toward a false CLOSE by up to about 0.5 ms together.
* (b), (c) and (h) push toward a false OPEN by up to about 1 ms together.

`C_up` is not an upper bound (because of a, e, f and d), and `C_lo` is not a lower bound (because of b and d). The
design's replay proxy C_rp shares (b) and (c)'s optimism, so rule 4's two conditions are not independent.

**Timer placement.** The class times are placed correctly. With `bindlap=1` they are bindlap's own interval selected by
class, with no new stamp and none of the census's own work. The partition identity holds per call. The **sampled**
spans (`r2_chk_ns`, `r2_st_ns`, `r2_rm_ns`) contain the instrument's own stamp latency. §7's "P−M prices it exactly:
Δbl_prep − Δbl_res − Δbl_smp − Δbl_sd" holds.

## 6. Hot-path cost (armed)

* **`std::array<ShaderTextureResource, 64> decoded;` value-initialises 2 KiB on every census call.** `fields[8] = {0}`
  (`shaderBindings.h:78`) means ≈ 9 443 × 10–20 ns ≈ **0.1–0.2 ms a frame**, missing from §7. The house rule (s86)
  already forbids exactly this: see `descriptors.cpp:3103-3106`, "NO value initialiser … `{}` would memset".
* The rest of §7 (≈ 0.6–1.2 ms a frame, all outside `bl_res`) is plausible.
* The per-call footprint is one entry: about 1 KB at 5.3 slots, 12 KB at 64. `thread_local std::unique_ptr` puts a TLS
  guard on every access. `constinit thread_local R2Table* t_r2 = nullptr` (the `t_shard` idiom, `frameStats.h`) avoids
  it.

## 7. Minor

* §1.2's `r2_cl_meta` claim, that adoption is a no-op under an unchanged `MetaEpoch`, is unproven. Adoption also reads
  image state that `MetaEpoch` does not cover: `registered`, `data`, `IsDepth`, `depth_id`, `metadata.kind`
  (`textureCache.cpp:3180-3189`). Keep the counter as information only.
* An early return with `prepared.images.size() != n` and `1 ≤ n ≤ 64` is booked as `R2Big`. It is unreachable, but it
  deserves its own label.
* `r2_meta0` exists only for `r2_cl_meta`. Dropping it removes one pre-loop load and one live range.
* The 2SE must come from per-ABBA-pair values of C, with `f` from each pair's own M blocks, not "over P blocks".

---

## 8. REQUIRED changes (write them into the design, then ROADMAP, before the patch)

**C1 — Rules at 0.5 ms and the package (ROADMAP `:2538-2550`).**
* Replace 1 000 by **500 µs** in §6 rules 2–4 and in fixture 8 (boundaries 499.9 / 500.0 for every branch).
* Rewrite the §0/§6 expectations.
* Pre-register the package formula as `C_pkg,x = C_R1,x + C_R2,x` for x ∈ {up, pt, lo}, with the 2SE of the
  **per-pair sum**:
  * package CLOSED if `C_pkg,up + 2SE < 500`;
  * OPEN if `C_pkg,lo − 2SE ≥ 500`;
  * else the point rule.
* An R2 value enters the package only when `r2_bad + r2_bad_key = 0`.
* Write down the disjointness argument (hit vs miss per call), the conservative interaction (R1-fixed misses enlarge
  R2's clean set), and "never add R3/R5 to R2".

**C2 — Remove R1's contamination of T\* by a pre-registered rule, not a note.** Preferred **(b)**:
* Run `r2cen=1` in **both** arms and `r2cen=2` (the replay) in P only.
* Take T* from **M's** own `r2_cl_ns`. M has `r1cen=0`, so there is no R1 work in the loop, and no `f` is needed.
* Record in ROADMAP before action that M now carries the R2 census. Its cost is then common to both arms and outside
  every P−M line.
* Fixture 1 becomes: M `r2_stg == bl_prep_n > 0`, `r2_rm_* == 0`; P `r2_rm_* > 0`.
* State the residual: the census's post-loop cache effect on the next loop, sign [U], small.

Alternative **(a)**:
* `T* = f_net × (r2_cl_ns(P) − ŝ_hit × S)`, with `f_net = bl_res(M) / (bl_res(P) − R1_inloop(P))`.
* This needs R1 to report its in-loop self price **split by hit and miss**, a change to r1.md.
* Sanity: `|f_net − 1| ≤ 0.03`, else NOT EVALUABLE.

**C3 — Price the witness where and how a real R2 pays it (pre-loop, cold), and correct every sampled span for the stamp
pair.** This fixes 5(a), 5(b) and 5(c).
* Draw the 1-in-8 sample **before** `bl_t` (`:2162`).
* On sampled stages, before `bl_t`: take a null pair `z0, z1` back to back. Then W1 + W2, plus, on repeating stages,
  the per-slot R check (memo `version` load, `try_get`, five-field liveness, `valid`/`image_id`).
* Book the time into `r2_wr_ns`/`r2_wr_n` (repeating) or `r2_wo_ns`/`r2_wo_n` (other), and the null pair into
  `r2_nul_ns`/`r2_nul_n`.
* Book sampled stages' `res_ns` and slots into separate counters (`r2_s_ns`, `r2_s_sl`, by class). Build T* only from
  unsampled clean stages, scaled by slots: `T*_u × (S+Z)/(S_u+Z_u)`.
* Replace `CHK` and the `V·S` term by `W = (w̄_rep − z̄)·r2_rep + (w̄_oth − z̄)·(r2_stg − r2_noimg − r2_big − r2_rep)`.
  The kept work per clean non-null slot is then `B + T'` (no V).
* `ST` and `C_rp` subtract `z̄` per sampled span. Add `r2_rm_n` (replayed stages).
* Information line: `r2_cl_ns_u/(S_u+Z_u) − r2_s_cl_ns/r2_s_cl_sl` = the first-touch cost moved into W.

```cpp
// PrepareBindings, after the knob read and BEFORE `bl_t` (:2162).  Armed only; r2 read once above.
R2Pre r2pre {};
if (r2 != 0) {
	r2pre = R2PreLoop(program, snapshot); // member: rng draw; on sampled stages z0,z1 null pair, then W1+W2(+R)
}                                         // timed [z1, w1]; Adds R2NullNs/R2Nulls and R2WitRep*/R2WitOth*
...
if (r2 != 0) {
	R2Census(program, snapshot, prepared, r2, r2pre, r2_res_ns); // sampled stages book res_ns into R2Sampled*
}
```

**C4 — Make C_up an upper bound in fact, and scope the CLOSE.**
* `C_up = T* − B_lo·(S+Z) + R_reset − W − ST`, with `B_lo` pre-registered below 8.49 (e.g. 5.0 ns [I]: slot lookup,
  `TouchImage` repeat path, three flag stores, one `push_back`) and `R_reset = 2.0 ns × (S+Z)` [I].
* Report the sensitivity row at B = 8.49.
* Delete "closed independently of the kept-price constants".
* A CLOSE names its scope: the whole-block, per-stage-type R2. The per-slot variant is reported as `C_ext` [I]. If
  `C_ext ≥ 500` it is recorded as "not closed, unmeasured", never as closed.

**C5 — Make the bad check cover what §8 claims.**
* (i) Compare the **whole** `ImageDesc` field-wise: add `pitch`, `bytes_per_block`, `samples`, `bgra16`, `stencil`,
  `htile_clear_mask`, `metadata.range.size`, `metadata.dcc_alpha_msb` and `mip_layout` (16 × 4 fields). Put them in
  diff group 128. This is measurement only, so the cost is acceptable.
* (ii) On an R slot, OR 256 into `dm` when `b.memo_index != s.memo_index || b.memo_version != s.memo_version`.
* (iii) Add the +1 detector:
  ```cpp
  if (s.memo_index < RenderExecutorMemo::TextureSlots && b.memo_index == s.memo_index &&
      b.memo_version == s.memo_version + 1u) {   // equal T#, same program
  	bad_key++;                                  // R2BadKey "r2_bad_key"; log R2MismatchKey (<= 40)
  }
  ```
* (iv) R additionally requires `memo->textures[s.memo_index].valid && .image_id == s.id` (texfast `:2561-2563`).
* Rule 1 becomes `Σ(r2_bad + r2_bad_key) > 0` or any `R2Mismatch*:` line ⇒ FAIL.
* Rewrite §8 as "if" (not "iff"), and state what the census cannot see.

**C6 — Correct the kept list.**
* In C_pt/C_lo use `T' = T − τ_touch` (τ = 3.0 ns [I], the redundant tail `TouchImage`, 5g) and `LS = 5.0` ns.
* Rewrite the `TouchImage` rows of §1.1/§1.2 ("always redundant with `BindImage`'s `GetImage`, same slot iteration").
* Drop `r2_cl_lru`.
* Relabel `r2_cl_meta` "information, not a witness" (§7).

**C7 — Arm assertions (fixture 1, else NOT EVALUABLE).**
* In both arms: `bindpack` = 1 (absent or 1), `texmemo2=0`, `m4baton=0`, `bindlap=1`, `fslean=0`.
* `bindalt`, `bindwit`, `blmove`, `bindfloor` absent or 0. They put stamps or stubs inside `bl_res` or bypass
  `PrepareBindings`.

**C8 — Traced vs play.** Report every C twice: traced, and play = traced − `A·(2S + Z)` with A = 1.2 ns [I] (5h). The
OPEN branches (rules 3, 4 and the package) read the play value.

**C9 — No 2 KiB memset per call.** Replace `decoded[64]` with per-slot bits written only for equal-T# slots and left
uninitialised (one flag byte: null / `MipStatsCntEn` / `MetaCompress`, plus a `uint64_t` meta address), or decode again
in the clean pass. Under C2(b) this cost is in both arms, which is one more reason to remove it.

**C10 — Statistics and fixtures.**
* SE from per-ABBA-pair C, not "over P blocks".
* New fixtures: the 500 boundaries; the package sum with a mutant that adds SEs instead of pairing; a mutant that forgets
  `z̄` must FAIL; `r2_bad_key=1` ⇒ FAIL; a `bindpack=0` arm ⇒ NOT EVALUABLE; C2(b)'s M-arm arming; C3's sampled-stage
  exclusion (a mutant building T* from all clean stages must FAIL); every new counter on a synthetic line; the suite ends
  with `ALL OK`.

## 9. Recommended (not blocking)

* Read the knob after the loop for the post-loop census, keeping only C3's pre-loop read, so that nothing new is live
  across the loop at gate 0.
* Store T# words in a contiguous per-entry array (`std::array<DescriptorValue, 64>`) apart from the per-slot metadata,
  so `ST` resembles a real R2's store (5j).
* Add a DCC-lock term `DL·r2_cl_dcc` to C_pt/C_lo (DL ≈ 30–50 ns [I], with T reduced to its non-lock part), or report
  the lock share of all armed hits beside the clean one (5l).
* Use `constinit thread_local R2Table*` instead of `thread_local std::unique_ptr` (§6).
* Two `R2Log` budgets (one per call site); fix the `:1841-1845` → `:3747` reference; give the unreachable
  `images.size() != n` exit its own label.
