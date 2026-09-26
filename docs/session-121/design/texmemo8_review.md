# Session 121 — adversarial review of `texmemo8.md` (8-way texture memo, verify mode)

Reviewer agent of the session-121 workflow. Read-only: no source edited, nothing built, the game not run, nothing
committed. Tree `C:/kyty/KytyPS5` at HEAD `6339dc8` (emulator code = `0310cbb`). Every file:line below was re-read in
that tree. Sources: `C:/kyty/s121/design/texmemo8.md` (all 953 lines), ROADMAP s121 item 1, `docs/next-session-121.md`,
`docs/session-120/design/r1_review.md`, `docs/session-120/audit/closure.md` §1 and §5,
`docs/session-120/audit/recount.md` §2, `descriptors.cpp` (`ResolveTextureWith` `:1900-2273`, census `:1364-1894`,
R2 `:2845-2866`, `:2945-2965`, `:3050-3062`, `:3150-3170`, `PrepareBindings` image loop `:3225-3290`, `RebindImages`
`:3515-3728`, rtfast write-back `:3770-3800`, `ShadowQueue` `:3809-3894`), `renderMemo.h`, `descriptors.h`, `render.h`,
`renderCompute.cpp:163-240`, `:850-890`, `textureCache.{h,cpp}` (`FindImage` `:2029-2120`, `ResolveOverlap` `:985-1060`,
`ConstrainSampledSource` `:1189-1217`, `ConfigureImageSource*` `:1219-1252`), `slotVector.h`, `frameStats.{h,cpp}`
(`Add`, `Read`), `videoOut.cpp:1255-1270`, `:2743-2752`, `gates.{h,cpp}`, `assert.h`, `C:/kyty/s121/gates_base.txt`.

## Verdict: **SOUND_WITH_CHANGES**

The memo mechanism is sound. Every store, including a victim eviction, bumps `version` and drops `fast_view`. A layout
switch invalidates by a version bump, and every reader of `memo_index`/`memo_version` checks `version`. `memo_index`
stays below 4 096. The hit keeps the real full proof. `texmemo8=0` changes no behaviour (only codegen, see RC7). The
design also found every memo reader I could find (§1.2).

The problem is the protocol around it. As written, the verify smoke `vfy121` would **FAIL on its own identities**, and
the sealed scorer's fixture S13 would make `shp121` **NOT_ADMITTED**. Both use a ±8 tolerance on cross-family
identities, and session 120 measured the residual of exactly these shapes at 26–525 counts a block window (RC1).

Three further defects weaken the verify mode:
* the positive control can hide a real mismatch (RC2);
* the samplers are periodic, which the census deliberately avoided (RC3);
* the texfast contract check can never fire and costs milliseconds (RC4).

All the required changes are small. None of them adds a population or changes the timed arm (`texmemo8=1`), except
RC7, which touches only codegen.

---

## 1. Verification of the design's claims

### 1.1 File:line claims

| claim | source | result |
|---|---|---|
| direct index `memo_hash % 4096`, entries `:119`, `TextureSlots` `:114` | `descriptors.cpp:2004-2007`, `renderMemo.h:114`, `:119` | OK |
| anchors `:1992`, `:1996`, `:2002`, `:2011-2015`, `:2016`, `:2037`/`:2038`, `:2067`, `:2069`, `:2084`, `:2087-2092`, `:2094`, `:2190`, `:2222`, `:2226`, `:2251-2252`, `:2263`, `:2268`, `:2271` | read one by one | OK (whole-line anchors match) |
| `TextureWay` `:76-80`, texmemo2 comment `:81`, namespace end `:128` | `renderMemo.h` | OK |
| `R1::Set<8>` `alignas(N*8)`, `R1Tag` = high 32 bits, `R1Victim` (empty way first, else lowest `use`), `R1DescDigest :1468-1515` | `descriptors.cpp:1393-1397`, `:1455-1457`, `:1549-1560`, `:1468` | OK: the design's helpers reproduce the census's victim and tag exactly; census set index `h & (W8Sets-1)` (`:1586`, `:1658`, `:1733`) = the design's `h & 511` |
| `R1Hit` real index `h & 4095` | `:1729` | OK |
| `RebindImages` `:3575` memo, `:3581-3584` r1 gating, eligibility `:3597-3605`, fast view `:3610-3617`, texfastcheck reset `:3642`, record `:3657-3658` | read | OK |
| `ShadowQueue` `:3846-3852` | read | OK. It copies the predicate into the job **on GuestGpu**; the worker (`textureCache.cpp:2183`) sees only `has_view`/`fast_stamp`. The worker never reads the memo |
| `R2Reproduced :2850-2864`, replay `h % 4096 :3057`, `bad_key` `:2950-2957`, gate `:3161-3164` | read | OK. Note: under 8-way an eviction-plus-store moves a way by exactly **+1**, which `bad_key` reads as a defect. Forcing r2cen off is therefore mandatory, not just tidy |
| compute clear shortcut `renderCompute.cpp:195` | read | OK. Its T# resolves through the stencil association, so `store` is false and it is never memoized; under 8-way it stays a miss with an untouched victim |
| `gates.h:628-633`, `gates.cpp:419-420`, `FindAssignment :458-470`, `frameStats.h:2138-2139`, `videoOut.cpp:2743` | read | OK |
| **"`SlotVector::insert` can reallocate (`slotVector.h:66-68`)" (§2.4, risk 3; inherited from r1_review §2)** | `slotVector.h:113-116`: storage is `std::deque<Slot>` | **WRONG reason, right conclusion.** `deque::emplace_back` keeps element references valid. The real hazard is `FindImage` **erasing** an image: `FreeImage` at `textureCache.cpp:2079` (resources grew) and inside `ResolveOverlap` (`:1017`). An erase runs `value.reset()`, so `cached` can dangle. The re-read stays required (RC6) |

### 1.2 Readers of the memo: is any missed?

Searches: `fast_view|memo_version|textures\[|TextureSlots|texture_ways|Memo\(\)|fast_stamp|memo_index` over `src/`,
plus `ResolveTexture(|ResolveTextureWith(` and `RebindImages(|PrepareBindings(`. Result: the design's table §3 is
complete. The readers it lists are `ResolveTextureWith`, `RebindImages` (repair loop plus texfast),
`ShadowQueue`, `R2Reproduced`/R2 replay, the r1 census, the compute clear shortcut, and `PrepareBindings`. Separately:
* The colour/depth memos (`colorRenderTarget.cpp:130-172`, `depthRenderTarget.cpp:296-334`, `renderDraw.cpp:995`) and
  the rtfast write-back (`descriptors.cpp:3786-3796`) use `colors`/`depths`, not `textures`.
* `drawstate`/`snapkeep` reuse storage and programs, not bindings: `PrepareBindings` still runs for every draw
  (`renderDraw.cpp:2604`, `:2624`), and `RebindImages` for every stage (`descriptors.cpp:3764`, `renderCompute.cpp:883`).
* `bindfloor` reuses materializations but is pinned off.
* One executor exists (`renderContext.h:85`), with one lazily created memo (`descriptors.cpp:2284-2289`).

### 1.3 Mechanism checks that PASS

* **Version/valid semantics under eviction.** A key miss chooses the victim as `memo_slot`. The unchanged store block
  `:2253-2262` then does `version++` and `fast_view = nullptr` on that way. The design's own additions do the same:
  the stale drop (`use = 0`), the verify refill (`version++`) and the verify drop (`valid = false`, `version++`,
  `use = 0`). `version` never resets, including across `Invalidate`, so a `(memo_index, memo_version)` pair has no ABA
  short of 2³² bumps of one entry.
* **Invariant I-T.** Its writers are the hit LRU, the stale drop, the store, the verify refill and drop, and
  `Invalidate`. `Find` requires `e.valid` as well as the tag, so a missed `use = 0` degrades to a miss, never to a
  wrong hit.
* **Layout switch inside a draw.** The knob is read once per `ResolveTextureWith` call, so the stages of one draw can
  straddle an edge, and so can the repair loop of `RebindImages`. Every binding from the old layout then fails
  eligibility by the version bump and re-records through `FindTexture`, which is correct. `tm8_check` is computed at
  `:3575`, after the repair loop (`:3535-3546`), so it reflects any switch the repair caused. I accept the per-call read.
* **texmemo2.** `memo2` forces `tm8 = 0`, so a texmemo2 period invalidates the 8-way layout, and returning to 8-way
  invalidates again. texmemo2's stale `texture_ways` tags then point at invalid entries, and its own key compare makes
  those misses. That is correct.
* **Liveness and generation.** `try_get` is generation-checked (`slotVector.h:58-61`) and the memo stores only exact
  backings (`:2251-2252`). The superseded-overlap exposure is unchanged in kind and longer in time, which is exactly
  what the gained-hit verify covers.
* **The desc is a pure function of the key.** `ConstrainSampledSource` (`textureCache.cpp:1189-1217`) depends on the
  desc and static flags only, and `FindImage` writes only `view_info.base_level/base_layer` (overlap) and the source
  trim. The fresh digest is therefore comparable with the stored one, as it was in the census.
* **The verify does not compare against the same memo.** `resolve_full` never touches `Memo()`: it runs
  `FindImage` on `m_slot_images`.
* **`texmemo8=0`.** No `Switch`, identical Adds in identical order, `r1_level = r1_req`, and in `RebindImages` one
  field load. OK apart from RC7.
* **Clock/renorm.** Stamps are unique within a set, the ranks keep the LRU order, `Tick` at `UINT32_MAX` renormalises
  before it wraps, and `Invalidate` resets the clock with every way empty. OK.

---

## 2. Findings and REQUIRED changes

### RC1 — MAJOR (blocks the protocol): cross-family identities cannot hold at ±8

The flip snapshots the counters **one at a time, in enum-index order, each read under the registry mutex**
(`videoOut.cpp:1257-1259`, `frameStats.cpp:214-222`). Two counters far apart in the enum are read tens to hundreds of
µs apart, while GuestGpu resolves about 1.5 textures a µs. Summing over a window does not cancel this: the two edge
rows leave a residual. Session 120 measured it on exactly these shapes: **`r1_hn − tex_hits` 520, `r1_mn −
(collide+empty)` 26, `b_texn − (hn+mn+sn+tnull)` 525** as the largest per-block window residuals
(`docs/session-120/audit/recount.md:81-88`, "FAR"). ROADMAP s120 item 6's ±8 was only ever exercised on NEAR
identities (residual 1–2, `recount.md:244-246`).

The design's identities 10 (`tm8_look` vs `tex_hits + texmemo_* + …`), 11 (`tm8_hit` vs `tex_hits + …`), 13
(`tm8_miss` vs `collide + empty`) and 19 (`tm8_rbchk` vs `texfast_*`) join counters from far-apart enum ranges:
`tex_hits`/`b_texn` sit in the old draw block and `texmemo_*`/`texfast_*` in the mid `-x` block, while `tm8_*` would be
appended at the end. The sealed fixture S13 (`tex_hits + collide + empty + stale` vs `b_texn − tnull_*`, 8 pass / 9
fail) is the shape that measured **525**. Consequences:
* `vfy121` FAILs on its own §8.2 PASS rule;
* if S13 is an admission check, `shp121` is NOT_ADMITTED;
* either way the track stops falsely.

**Required:**

```diff
 §6 counters (enum order = identity order; all mode >= 2 counters CONTIGUOUS at the end, in this order)
-| 10 | Tm8Look | = tex_hits + texmemo_collide + texmemo_empty + texmemo_stale + tm8_bad + tm8_vctl_bad + tm8_inject |
+| 10 | Tm8Look | NEAR: = tm8_hit + tm8_miss + tm8_stale                     (all tm8_*, adjacent: +-8 per window)
+| 10a| Tm8Stale (new, mode >= 2, Add in the stale path next to TexMemoStale) | info
-| 11 | Tm8Hit  | = tex_hits + tm8_bad + tm8_vctl_bad + tm8_inject |
+| 11 | Tm8Hit  | FAR:  tex_hits = tm8_hit - tm8_bad - tm8_vctl_bad   (see RC2: inject no longer returns early)
-| 13 | Tm8Miss | = texmemo_collide + texmemo_empty |
+| 13 | Tm8Miss | FAR:  = texmemo_collide + texmemo_empty
 | 15 | Tm8Check = tm8_gain            | NEAR (place Tm8Gain and Tm8Check adjacent)
-| 19 | Tm8RbCheck <= texfast_ok + texfast_no | 
+| 19 | Tm8RbCheck <= texfast_ok + texfast_no | FAR
+ Tolerances: NEAR = +-8 counts on a block's window sum (s120 item 6).  FAR = |residual| <= max(64, 1 per mille of the
+ larger window sum) - s120 measured 520/525 on ~3.5 M (0.15 per mille) and 26 on ~140 k.  A constant offset of one a row
+ (>= 79 a window) must still fail every NEAR identity; FAR identities additionally must hold on run MEANS to 0.1 per mille.
 §8.4 fixture
-| S13 | identity skew: tex_hits + collide + empty + stale vs b_texn - tnull_* off by 8 (pass) and 9 (fail) |
+| S13 | FAR identity b_texn - tnull_* = tex_hits + collide + empty + stale: residual 525 on a 3.6 M window (pass),
+|     |   0.0011 x window (fail), a constant +1 a row on a NEAR identity (fail) |
```

Add the mutant "FAR tolerance applied as NEAR" (it must fail S13's 525 case). In the `vfy121` checker, every
identity carries its NEAR/FAR class explicitly, with one fixture per class edge.

### RC2 — MAJOR: the positive control hides a real mismatch

`Tm8::Agree` corrupts `claim` first and then counts `inject ? Tm8Inject : (gained ? Tm8Bad : Tm8CtlBad)`. On an
injected lookup where the fresh answer really disagrees with the memo, the event is booked as `tm8_inject`, and
`tm8_bad` stays 0. At mode 3 that happens on about 1/1 024 of gained hits. The design also leaves open (§2.4 note)
whether an inject refills. The refill variant changes state, counts `Tm8Fill` and breaks identity 1. Fix both:

```diff
 static bool Agree(bool gained, bool inject, const RenderExecutorMemo::Texture& slot, uint32_t index, ImageId id,
                   const TextureCache::ImageDesc& desc, bool store) {
-	ImageId    claim = slot.image_id;
-	if (inject) {
-		claim.generation ^= 0x80000000u;
-	}
 	const auto a = R1DescDigest(slot.desc);
 	const auto b = R1DescDigest(desc);
 	FS::Add(gained ? Ctr::Tm8Check : Ctr::Tm8CtlCheck, 1);
-	if (store && id == claim && a.all == b.all) {
-		return true;
-	}
-	FS::Add(inject ? Ctr::Tm8Inject : (gained ? Ctr::Tm8Bad : Ctr::Tm8CtlBad), 1);
+	const bool real_ok = store && id == slot.image_id && a.all == b.all;    // the REAL verdict, always first
+	if (real_ok && inject) {
+		ImageId claim = slot.image_id;
+		claim.generation ^= 0x80000000u;                                      // a COPY; never written back
+		if (id != claim) {                                                    // the comparison must reject it
+			FS::Add(Ctr::Tm8Inject, 1);                                        // positive control fired
+			/* log Tm8VerifyInjected (own budget 4) */
+		} else {
+			FS::Add(Ctr::Tm8InjectMiss, 1);                                    // new: must read 0 (control broken)
+		}
+		return true;                                                          // state untouched, hit proceeds
+	}
+	if (real_ok) {
+		return true;
+	}
+	FS::Add(gained ? Ctr::Tm8Bad : Ctr::Tm8CtlBad, 1);                         // a real mismatch, even on an inject lookup
 	...log Tm8VerifyMismatch (budget 40)...
 	return false;
 }
```

With this, an inject never takes the refill branch. Identity 11 becomes `tex_hits = tm8_hit − tm8_bad − tm8_vctl_bad`
(FAR, RC1), and identity 1 (`tm8_fill ≤ collide + empty + stale + bad + vctl_bad`) holds at every mode. Add fixtures:
"`tm8_inject_miss` = 1 ⇒ FAIL"; "an injected lookup with a real mismatch counts `tm8_bad`" (the offline unit test
of §8.5 can drive `Agree` directly).

### RC3 — MAJOR: periodic samplers alias with per-stage slot structure

`tm8_smp = (++texture8_sample & 63) == 0` and `inject = (texture8_sample & 1023) == 0` are strides over the lookup
sequence. Lookups arrive in fixed per-stage slot order (`PrepareBindings` iterates `i = 0..images.size()`,
`:3227-3243`), so a stride that shares a factor with the typical image count samples the same slot positions draw
after draw. The "1/64 control of the other hits" would then cover only a fixed subset of slot positions, and the probe
timer would be biased. The census avoided this on purpose: `R1Next`, `descriptors.cpp:1448`, "xorshift32 … (not
periodic: no slot aliasing)".

```diff
-	const bool  tm8_smp   = tm8 >= 2 && (++memo.texture8_sample & 63u) == 0;
+	// xorshift32 in the memo (state never 0), as R1Next: not periodic, so no slot-position aliasing.
+	uint32_t    tm8_rnd   = 0;
+	if (tm8 >= 2) [[unlikely]] {
+		auto x = memo.texture8_sample; x ^= x << 13u; x ^= x >> 17u; x ^= x << 5u; memo.texture8_sample = tm8_rnd = x;
+	}
+	const bool  tm8_smp   = tm8 >= 2 && (tm8_rnd & 63u) == 0;
 ...
-	const bool inject = tm8 == 3 && gained && (memo.texture8_sample & 1023u) == 0;
+	const bool inject = tm8 == 3 && gained && ((tm8_rnd >> 6u) & 1023u) == 0;   // independent bits of the same draw
 renderMemo.h:
-	uint32_t                 texture8_sample = 0;
+	uint32_t                 texture8_sample = 0x9E3779B9u; // xorshift state (never 0)
```

Do not reuse `t_r1_rng`: r1cen is forced off, but a shared stream would couple the two instruments in any future run.

### RC4 — MAJOR: `CheckRebind` cannot fire, is expensive, and is not the control the audit asked for

Eligibility (`:3599-3605`) already requires `slot->valid ∧ slot->version == binding.memo_version ∧ slot->image_id ==
binding.image_id`. Every writer of `image_id`/`desc` also bumps `version`, so equal versions imply the same desc.
`CheckRebind`'s id-and-digest comparison is therefore tautological, and it can fire only if a future writer forgets
the bump. It also computes **two `R1DescDigest`s per eligible binding**: about 45 k a frame (`texfast_ok + no` ≈ 50 k,
r1_review §1) × 2 × ~100 ns ≈ 9 ms a frame of verify-arm time for nothing.

Closure §5.3 asked for something else: a counter for "eligible under a stale layout". Replace the check with a
**placement check**. It is cheap (one XXH3 of 32 B), cannot be satisfied by construction, and would fire on a missed
invalidation. A direct-layout entry `i` holds a key with `h & 4095 == i`, which lies in set `i & 511`, and that differs
from `i >> 3` for all but a handful of `i`.

```diff
-static void CheckRebind(const RenderExecutorMemo::Texture& slot, const TextureBinding& binding) {
-	FS::Add(Ctr::Tm8RbCheck, 1);
-	if (slot.image_id == binding.image_id && R1DescDigest(slot.desc).all == R1DescDigest(binding.desc).all) {
-		return;
-	}
+// texmemo8 >= 2: an ELIGIBLE binding's slot must hold a key that BELONGS at that index under the CURRENT layout, and
+// (8-way) its way must be non-empty with the key's tag - i.e. no entry laid out by the other layout is ever eligible.
+static void CheckRebind(const RenderExecutorMemo& m, const TextureBinding& binding, bool inject) {
+	FS::Add(Ctr::Tm8RbCheck, 1);
+	const auto&    slot  = m.textures[binding.memo_index];
+	const uint64_t h     = MemoHashBytes(slot.dwords.data(), sizeof(slot.dwords), slot.resource_key);
+	uint32_t       index = binding.memo_index;
+	if (inject) index ^= 8u;                                   // mode 3, 1/1024: a wrong set must be rejected
+	const auto&    s     = m.texture_sets8[index / 8u];
+	const bool placed = m.texture_mode == 0
+	    ? (h & 4095u) == index
+	    : (h & 511u) == index / 8u && s.use[index % 8u] != 0 && s.tag[index % 8u] == static_cast<uint32_t>(h >> 32u);
+	if (inject) { FS::Add(placed ? Ctr::Tm8RbInjectMiss : Ctr::Tm8RbInject, 1); return; }
+	if (placed) return;
 	FS::Add(Ctr::Tm8RbBad, 1);
 	...log Tm8RebindMismatch (budget 40)...
 }
```

`tm8_rbbad` must read 0. At mode 3, `tm8_rbinject` > 0 and `tm8_rbinject_miss` = 0; draw the inject bit from the
RC3 xorshift. Counters: +2 (`Tm8RbInject`, `Tm8RbInjectMiss`), plus `Tm8Stale` (RC1) and `Tm8InjectMiss` (RC2) ⇒
**28** `tm8_*`. The optional "slot holds binding's id/desc" check can stay as a 1/64 sample if the lead wants a
silent-writer guard. It must not be described as the stale-layout control.

### RC5 — MINOR (required, small): the direct shadow's "exact" claim is false in one case

§2.7, first bullet, says an 8-way store of K is always mirrored exactly: "had K live → hit → DirectPut(K, id)". Take
the loss case where the shadow holds (K, id_old), id_old is live, and the fresh `id ≠ id_old`. The direct memo would
have **hit and returned id_old without storing**. `DirectPut(K, id)` instead records a direct memo holding (K, id).
Later 8-way hits of (K, id) are then classified "not gained" although the direct memo would have answered id_old, and
they get only the 1/64 control. The case needs an existing-memo defect (a live entry that disagrees with a fresh
resolution), but the classification must stay conservative:

```diff
 §2.6 store, tm8 >= 2
-			if (tm8 >= 2) {
-				Tm8::DirectPut(memo, memo_hash, resource_key, descriptor.fields, id);
-			}
+			if (tm8 >= 2) {
+				if (Tm8::DirectHolds(memo, memo_hash, resource_key, descriptor.fields, nullptr) &&
+				    !Tm8::DirectHolds(memo, memo_hash, resource_key, descriptor.fields, &id)) {
+					// loss case with another id: the direct memo may have hit with that id.  Drop K - later hits count
+					// as gained (verified) - and book it: a LIVE differing direct entry is an existing-memo mismatch.
+					Common::FrameStats::Add(Common::FrameStats::Counter::Tm8DirectDiff, 1);   // info; see text
+					Tm8::DirectDrop(memo, memo_hash, resource_key, descriptor.fields);
+				} else {
+					Tm8::DirectPut(memo, memo_hash, resource_key, descriptor.fields, id);
+				}
+			}
```

Amend §2.7's text: "exact, except the loss case with a differing id, which is dropped (conservative)". `tm8_ddiff` is
information only, because the shadow does not know whether id_old was still live. Report it.

### RC6 — MINOR (required): fix the `cached` justification and re-check liveness after `resolve_full`

Replace the reallocation argument, in §2.4's comment and risk 3, with the erase paths
(`textureCache.cpp:2079`, `:1017`). After a passing `Agree`, the id equals the slot's, the fresh image passed `store`
(data and extent equal, no stencil association), and the digest is equal. `registered`/`needs_rebind` are still only
known from before the fresh resolution's side effects, so re-test them cheaply:

```diff
-					cached = texture_cache.m_slot_images.try_get(memo_slot.image_id);
-					EXIT_IF(cached == nullptr);
+					// FindImage may ERASE images (FreeImage: textureCache.cpp:2079 resources grew, :1017 overlap), and
+					// SlotVector::erase resets the optional - `cached` is re-read; the deque itself never moves elements.
+					cached = texture_cache.m_slot_images.try_get(memo_slot.image_id);
+					if (cached == nullptr || !cached->registered || cached->binding.needs_rebind || cached->depth_id) {
+						Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Relive, 1);   // must read 0
+						/* treat as a disagreement: the v_store refill / drop branch above, return the fresh answer */
+					}
```

### RC7 — MINOR (required): the lambda refactor must not move the miss price, or the bias must be declared

`resolve_full` has two call sites and a large body (about 160 lines), so clang is unlikely to inline it at the miss
site. Captured locals then go through a closure pointer. Both arms pay that, but not equally: a miss-path slowdown δ
per miss is paid on ≈ 1 772 misses a frame in M and ≈ 580 in P. **Δ`dt_us` therefore reads the gain against
`texmemo8=0` of this build, which is slower than the installed `d3a981a2` by ≈ 1 772·δ.** Either:

```diff
-	const auto resolve_full = [&](TextureCache::ImageDesc& desc, bool& store) -> ImageId {
+	const auto resolve_full = [&](TextureCache::ImageDesc& desc, bool& store) __attribute__((always_inline)) -> ImageId {
```

(clang-cl accepts the GNU attribute on a lambda; a KYTY force-inline macro, if one exists, is equivalent.) Or the
pre-registration states in advance that the SHIP claim is "against `texmemo8=0` of the same build". Do both.

### RC8 — MINOR: identity/band corrections

* §8.2 lists identities "10–13, 15, 17, 19, 23 … within ±8". 17 and 23 are sampler ratio bands, not ±8. With RC3 the
  ratios become binomial: keep [1/80, 1/50] per block window, since the expected count is ≈ 700·79 and ±25 % is many
  sigma.
* Identity 1's upper bound gains `+ tm8_vctl_bad` (the control refill also fills).
* Arming band S4: the upper edge of +1 500 can reject a genuine result. The census table was reset every block
  (`R1ResetCensus` `:1606`, via `R1Arm` `:1623`), while P→P continuation blocks of the real memo are not.
  The physical ceiling is the M arm's own key misses (≈ 1 772). Use **[+800, M-arm Σ(collide + empty) of the same
  quartet]**, and keep NOT_EVALUABLE only below +800 or above that ceiling (the ceiling is a hard impossibility).

---

## 3. Recommendations (not required)

1. **DCC adoption insurance** (closure §5.5 asked for it). The verify arm runs the miss path's unconditional
   `AdoptPendingDccForTexture` **before** the hit tail, which masks any hit-tail adoption gap in mode 2/3. Cheap
   counter: before `resolve_full`, record `settled` (the hit tail's skip condition, `:2059-2062`) and the image's
   `(metadata.kind, metadata.range)`. After it, if `settled` held and the metadata changed ⇒ `tm8_dcc_chg` (must read 0).
2. **LRU write on a hit that is already MRU.** `if (use[w] != texture8_clock) use[w] = Tick(m);` keeps the exact LRU
   order and saves two stores on repeated keys, which are common (R2's repeating blocks). Worth it in the P arm.
3. **Inline the set array.** `alignas(64) std::array<TextureSet8, 512> texture_sets8 {};` inside
   `RenderExecutorMemo` (heap-allocated via `make_shared`, and over-aligned allocation is fine in C++17). This removes
   the vector-data-pointer load in front of the set line. Minor.
4. **The probe is a dependent load chain.** Hash → set line → compare → entry, where the direct memo has hash → entry.
   On a cold entry that serialises two misses. The census `P` (0.94 ns a lookup, closure §1.2 f) did not include
   this. Risk 1 should say it can reach 2–4 ns a lookup (90–185 µs), not only "1–3 ns".
5. **Video of record.** `vfy121`'s `texmemo8=1` blocks run with `texfastcheck=1`, which replaces a wrong view before
   display. That is acceptable only jointly with `texfast_bad = 0` (then nothing was replaced). State this in §8.2, or
   add a fifth arm `texmemo8=1 texfastcheck=0` whose blocks are the video of record.
6. **Never schedule `r1cen`/`r2cen` ≠ 0 together with a `texmemo8` flip.** R2 reads `TexMemo8` at stage start
   separately from the per-resolve read (§2.9), so a flip mid-stage would contaminate one stage. The arms name them 0
   anyway; record it as a rule.
7. **Value 3.** Accept it, conditional on RC2 and RC4, as a separate recorded decision. It is the only in-game proof
   that `tm8_bad` and `tm8_rbbad` can fire.
8. **Verify-arm limits to state in §5.3.** The verify arm touches about 2 k extra images a frame through `FindImage`
   (`TouchImage`, `tick_accessed_last`). Its texture-cache GC order, and hence the memo contents it sees, differ from
   mode 1, so a defect that exists only under mode 1's exact eviction order is not covered. The mode-1 video and the
   sealed arm's zero-leak checks are the only evidence for mode 1 itself.

## 4. Summary for the lead

| # | severity | change | touches timed arm? |
|---|---|---|---|
| RC1 | MAJOR (protocol-blocking) | NEAR/FAR identity classes; contiguous `tm8_*`; `Tm8Stale`; S13 rewritten | no (scorer/checker only) |
| RC2 | MAJOR | `Agree`: real verdict first, inject never refills, `Tm8InjectMiss` | no (mode 3) |
| RC3 | MAJOR | xorshift samplers | no (modes 2–3) |
| RC4 | MAJOR | `CheckRebind` → placement check with inject | no (modes 2–3) |
| RC5 | MINOR | shadow: drop instead of put in the differing-id loss case; `Tm8DirectDiff` | no |
| RC6 | MINOR | erase-based justification; re-check liveness after `resolve_full`; `Tm8Relive` | no |
| RC7 | MINOR | force-inline `resolve_full` and declare the same-build comparison | **codegen of both arms** |
| RC8 | MINOR | band/identity text; S4 upper edge = M-arm key misses | no |

Counter total after RC1–RC6: 24 + `Tm8Stale`, `Tm8InjectMiss`, `Tm8RbInject`, `Tm8RbInjectMiss`, `Tm8DirectDiff`,
`Tm8Relive` = **30** (all `micros = false`, contiguous, identity members adjacent). With these changes the design is
sound to record in ROADMAP s121 and to build.
