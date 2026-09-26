# Session 121 — design of knob `texmemo8`: the texture memo as 512 sets × 8 ways of the same 4 096 entries

Author: designer agent of the session-121 workflow (read-only study; no source edited, nothing built, the game not run,
nothing committed). **Not accepted until the lead records it in ROADMAP s121 by an explicit line.**
Tree `C:/kyty/KytyPS5` at HEAD `6339dc8`; emulator code = commit `0310cbb` (build `15cdbfc6…` of s120; it contains
`r1cen`/`r2cen`/`spcen`). Every file:line below is from that tree and quotes WHOLE lines. Tags: **[M]** measured (run
named), **[I]** inferred from code/arithmetic, **[U]** unknown.

Sources read: ROADMAP s120 items 2, 4–8 and s121 item 1; `docs/next-session-121.md`; `docs/session-120/design/r1.md`,
`r1_review.md`; `docs/session-120/audit/closure.md`; `C:/kyty/s120/runs120/rpk120_cen120.{txt,json}`; source
`descriptors.cpp` (whole `ResolveTextureWith`, the r1cen census `:1364-1894`, R2 `:2781-3170`, `PrepareBindings` image
loop `:3225-3290`, `RebindImages` `:3520-3728`, `ShadowQueue` `:3809-3894`), `renderMemo.h`, `descriptors.h`,
`render.h`, `textureCache.{h,cpp}` (`ShadowProbe`), `renderCompute.cpp:170-240`, `gates.{h,cpp}`, `frameStats.h`,
`videoOut.cpp`; harness `C:/kyty/s121/gates_base.txt`, `C:/kyty/s120/go120a.sh`, `C:/kyty/s111/shp111.py` (pairing).

## 0. What is being built, and the numbers it stands on

The texture memo of `ResolveTextureWith` is direct-mapped: `memo_hash % 4096` (`descriptors.cpp:2004-2007`), 4 096
`Texture` entries (`renderMemo.h:114`, `:119`). Seal 01 `cen120` [M] (pinned, NEW BDA regime, 38 pairs, P arm, frames
10–88): lookups 46 399.5 a frame; an 8-way LRU of the SAME 4 096 entries would have hit **W = 1 258.7** key misses a
frame with the real hit's full proof and 0 disagreements (`r1_w8_bad` = 0 on all rows, `w1` null control 0);
`t_hit` 19.2 ns, `t_T` 516.6 ns, `t_miss` 539.3 ns; net ceiling `C_w8` = A 626.1 − L 33.1 + R 81.1 + E 28.4 − P 43.7 =
**658.8 ± 9.1 µs** a frame. Losses (hits the 8-way would lose that direct keeps) ≈ 33.1/(516.6 − 19.2) ≈ **66.6 a
frame** [I]. Audit 120 (closure §1.2–1.4): honest ceiling ≈ 0.33–0.62 ms, **realizable ≈ 0.25–0.50 ms, central
0.35–0.40** [I]; power of one sealed ABBA at 2SE 0.14–0.18 ms: 0.25 ms 79–95 %, 0.35 ms 94–99 %, 0.15 ms 38–54 %.

`texmemo8` is a **knob** (0..3) because it needs more than two values:

| value | meaning | may be timed? |
|---:|---|---|
| 0 | today's direct memo, byte-for-byte behaviour (§7) | yes (M arm) |
| 1 | 8-way memo (the candidate to ship) | yes (P arm) |
| 2 | 1 + **VERIFY** (every gained hit against a fresh full resolution, a 1/64 control of non-gained hits, the texfast contract check in `RebindImages`, the sampled probe timer) | **never** |
| 3 | 2 + **positive control**: every 1 024-th gained hit is compared against a deliberately corrupted COPY of the slot's image id (state untouched; the fresh answer is returned) — proves in the real game that `tm8_bad` can fire (s120 review F-G asked every `*_bad` for a failing control) | **never** |

Value 3 is an ADDITION to ROADMAP s121 item 1 (which names only the verify mode); it needs its own recorded decision
(the lead may drop it and keep the max at 2; §5.4 then loses only its positive control, which the offline unit test
§8.5 partly replaces).

## 1. Data layout

### 1.1 Where the entries live — unchanged

`std::vector<Texture> textures {TextureSlots};` (`renderMemo.h:119`), 4 096 entries; `Texture` = dwords 32 B +
`resource_key` 8 + `valid` + `ImageId` + `ImageDesc` (~584 B, r1.md §2.2) + `version` + `fast_stamp` + `fast_view` ≈
650 B each ≈ 2.7 MB [I]. **Under `texmemo8` ≥ 1 entry `set·8 + way` is way `way` of set `set`** (set = `memo_hash &
511`, the low 9 bits; the direct index uses the low 12 bits, `memo_hash % 4096` = `& 4095`, so every key of a direct
slot maps to one set). Hence `memo_index = set·8 + way < 4096 = TextureSlots`: every reader of
`memo_index`/`memo_version` (§3) keeps indexing a real entry, and the `Texture` fields keep their meaning (a valid
entry holds exactly one key; `version` moves on every store and invalidation; `fast_view`/`fast_stamp` belong to the
(image, desc) the entry holds).

### 1.2 The tag/LRU lines — new, one 64-B line per set

The layout the census priced (`R1::Set<8>`, `descriptors.cpp:1393-1397`, `alignas(N * 8)` = 64): 8 compact 32-bit tags
(the high 32 bits of `memo_hash`, `R1Tag` `:1455-1457`) + 8 32-bit LRU stamps. `use == 0` ⇔ empty way.

**Invariant I-T (kept by `ResolveTextureWith`, the only writer of `valid`, r1_review §1):**
`texture_sets8[s].use[w] != 0 ⇔ textures[s·8+w].valid`, and then `texture_sets8[s].tag[w] == high32(memo_hash of the
key textures[s·8+w] holds)`. Consequently a key is present in at most one way of its set (a store happens only after
the full-proof probe of every tag-matching way failed, §2.2).

`renderMemo.h` — after the `TextureWay` struct (`:76-80`), before the `// Gate "texmemo2": resource key by
ImageResource address.` comment (`:81`):

```cpp
+	// Session 121, knob "texmemo8" (C:/kyty/s121/design/texmemo8.md): the SAME `textures` entries as 512 sets x 8 ways,
+	// entry index = set * 8 + way (so memo_index < TextureSlots and every reader of memo_index / memo_version keeps
+	// indexing a real entry).  One 64-byte line per set: the compact tag (high 32 bits of memo_hash) and the LRU stamp
+	// of each way; use == 0 <=> the way is empty <=> textures[set * 8 + way].valid == false (ResolveTextureWith keeps
+	// the two in step).  The tag only filters: a hit still needs the full proof (resource_key, 32-byte T#, liveness).
+	struct alignas(64) TextureSet8 {
+		std::array<uint32_t, 8> tag {};
+		std::array<uint32_t, 8> use {};
+	};
+	static_assert(sizeof(TextureSet8) == 64);
+	// texmemo8 >= 2 (VERIFY, never timed): the key a DIRECT memo (index memo_hash % TextureSlots) would hold now, so a
+	// hit the direct memo would have missed ("gained") is recognised and checked against a fresh full resolution.
+	struct TextureDirectKey {
+		uint64_t                resource_key = 0;
+		std::array<uint32_t, 8> dwords {};
+		ImageId                 image_id;
+		bool                    valid = false;
+	};
```

`renderMemo.h:114-122` — constants and members (the `texture_mode` word right after `textures`, so it shares the line
the executor already loads to index `textures`):

```cpp
 	static constexpr size_t TextureSlots = 4096;
+	static constexpr size_t TextureWays8 = 8;                          // knob "texmemo8"
+	static constexpr size_t TextureSets8 = TextureSlots / TextureWays8; // 512
+	static_assert((TextureSets8 & (TextureSets8 - 1)) == 0);
 	static constexpr size_t ResourceKeySlots = 1024;
@@
 	std::vector<Texture>     textures {TextureSlots};
+	uint32_t                 texture_mode    = 0; // effective texmemo8 the entries are laid out for (0 direct, 1-3 8-way)
+	uint32_t                 texture8_clock  = 0; // LRU clock of texture_sets8 (renormalised before it wraps)
+	uint32_t                 texture8_sample = 0; // texmemo8 >= 2: the 1/64 sampler (control check, probe timer)
+	std::vector<TextureSet8> texture_sets8 {TextureSets8};    // 32 KiB, zero = every way empty
+	std::vector<TextureDirectKey> texture8_direct;            // texmemo8 >= 2 only (allocated by the switch), else empty
 	std::vector<TextureWay>  texture_ways {TextureSlots};
```

Pure helpers (header, so the offline unit test §8.5 can compile them without the executor), after the struct, before
`} // namespace Libs::Graphics` (`renderMemo.h:128`):

```cpp
+// Knob "texmemo8": the non-empty ways of `s` whose tag equals `tag`, as a bit mask.  Branch-free on purpose (clang
+// turns it into two 128-bit compares + a movemask): the set probe runs on every lookup.
+inline uint32_t TexMemo8TagMask(const RenderExecutorMemo::TextureSet8& s, uint32_t tag) noexcept {
+	uint32_t mask = 0;
+	for (uint32_t w = 0; w < 8; w++) {
+		mask |= static_cast<uint32_t>(s.tag[w] == tag && s.use[w] != 0) << w;
+	}
+	return mask;
+}
+// The way a store takes on a key miss: an empty way, else the least recently used (lowest stamp) - the census's
+// R1Victim (descriptors.cpp) on the same line.
+inline uint32_t TexMemo8Victim(const RenderExecutorMemo::TextureSet8& s) noexcept {
+	uint32_t best = 0;
+	for (uint32_t w = 0; w < 8; w++) {
+		if (s.use[w] == 0) {
+			return w;
+		}
+		if (s.use[w] < s.use[best]) {
+			best = w;
+		}
+	}
+	return best;
+}
+// Before the clock wraps: every non-empty way gets its rank (1..8) among the non-empty ways of its set - the LRU
+// order is kept exactly (stamps are unique), empty ways stay 0.  The caller sets the clock to 8.
+inline void TexMemo8Renorm(std::vector<RenderExecutorMemo::TextureSet8>& sets) noexcept {
+	for (auto& s: sets) {
+		std::array<uint32_t, 8> rank {};
+		for (uint32_t w = 0; w < 8; w++) {
+			if (s.use[w] == 0) continue;
+			rank[w] = 1;
+			for (uint32_t v = 0; v < 8; v++) rank[w] += (s.use[v] != 0 && s.use[v] < s.use[w]) ? 1u : 0u;
+		}
+		s.use = rank;
+	}
+}
```

### 1.3 Footprint

| part | size | when |
|---|---:|---|
| `textures` (unchanged) | 4 096 × ~650 B ≈ 2.7 MB | always |
| `texture_sets8` | 512 × 64 B = **32 KiB** | always allocated (zeroed in the constructor; never read at `texmemo8=0`) |
| 3 words `texture_mode`/`texture8_clock`/`texture8_sample` | 12 B | always |
| `texture8_direct` (verify shadow) | 4 096 × ~56 B ≈ **224 KiB** | only while the mode is 2 or 3 |

The hot set of a lookup at `texmemo8=1`: one tag line (32 KiB total, L1/L2-resident) + the entry of the matching way
(the same one entry the direct memo reads today) + on a hit one store to the tag line (`use`) and one to
`texture8_clock`.

### 1.4 The LRU clock

32-bit, `++` on every hit and every store (≈ 46 400 a frame [M]) ⇒ it would wrap after ≈ 92 000 frames ≈ 50 min at
31 FPS [I]. A 300-s run (≈ 9 300 frames) never reaches it, a shipped default does. `Tm8::Tick` (§2.1) renormalises
at `UINT32_MAX` (`TexMemo8Renorm`, 512 × 64 compares ≈ a few µs, counted `tm8_renorm`) and sets the clock to 8. No
invalidation, no change of any answer.

## 2. Code plan (pseudo-diffs, `descriptors.cpp`, whole-line anchors)

### 2.1 Helper block — new, after the end of `R1Miss` (`:1894` `}`), before `// Session 57, B2a: every result goes out through `emit`; ...` (`:1896`)

Placed after the census so `R1DescDigest` (`:1468-1515`) is in scope for the verify check (reused, as ROADMAP asks).

```cpp
+// Session 121, knob "texmemo8" (C:/kyty/s121/design/texmemo8.md): the texture memo as 512 sets x 8 ways of the SAME
+// 4 096 entries.  Read ONCE per ResolveTextureWith call.  1: the 8-way memo (the shipping candidate).  2: VERIFY,
+// MEASUREMENT ONLY, never a timed arm - every gained hit (the direct index would not have held the key) and a 1/64
+// sample of the other hits run the full resolution too and are compared (store, id, R1DescDigest), RebindImages checks
+// the texfast contract, the probe is timed on a 1/64 sample.  3: 2 + a positive control (every 1 024-th gained hit is
+// compared against a corrupted COPY of the slot id; nothing in the memo changes).  Off under texmemo2 (texmemo2 wins).
+namespace Tm8 {
+using Ctr                      = Common::FrameStats::Counter;
+constexpr uint32_t Ways        = RenderExecutorMemo::TextureWays8;
+constexpr uint32_t SetMask     = RenderExecutorMemo::TextureSets8 - 1;
+constexpr uint32_t DirectMask  = RenderExecutorMemo::TextureSlots - 1;
+static uint32_t Tag(uint64_t h) {
+	return static_cast<uint32_t>(h >> 32u); // = R1Tag: the set index uses the low bits, the tag the high ones
+}
+struct Probe {
+	uint32_t index = 0;     // set * 8 + way: the hit way, else the victim way
+	bool     found = false; // the full key proof passed on a non-empty way
+};
+// THE REAL HIT'S KEY TEST on every tag-matching way (valid, resource_key, 32-byte T#) - never the tag alone.
+static Probe Find(const RenderExecutorMemo& m, uint64_t h, uint64_t rk, const uint32_t* dwords) {
+	const uint32_t set = static_cast<uint32_t>(h) & SetMask;
+	const auto&    s   = m.texture_sets8[set];
+	for (uint32_t mask = TexMemo8TagMask(s, Tag(h)); mask != 0; mask &= mask - 1u) {
+		const uint32_t w = static_cast<uint32_t>(std::countr_zero(mask));
+		const auto&    e = m.textures[set * Ways + w];
+		if (e.valid && e.resource_key == rk && std::memcmp(e.dwords.data(), dwords, sizeof(e.dwords)) == 0) {
+			return {set * Ways + w, true};
+		}
+		Common::FrameStats::Add(Ctr::Tm8Alias, 1); // a 32-bit tag alias: the exact proof failed (expected ~0)
+	}
+	return {set * Ways + TexMemo8Victim(s), false};
+}
+// texmemo8 >= 2, the 1/64 sample: the probe price against a null stamp pair (the timed probe IS this lookup's probe).
+static Probe FindTimed(const RenderExecutorMemo& m, uint64_t h, uint64_t rk, const uint32_t* dwords) {
+	namespace FS      = Common::FrameStats;
+	const uint64_t a0 = FS::NowNs();
+	const uint64_t a1 = FS::NowNs();
+	const uint64_t b0 = FS::NowNs();
+	const Probe    p  = Find(m, h, rk, dwords);
+	const uint64_t b1 = FS::NowNs();
+	FS::Add(Ctr::Tm8Probe0Ns, a1 - a0);
+	FS::Add(Ctr::Tm8ProbeNs, b1 - b0);
+	FS::Add(Ctr::Tm8ProbeN, 1);
+	return p;
+}
+static uint32_t Tick(RenderExecutorMemo& m) {
+	if (m.texture8_clock == UINT32_MAX) [[unlikely]] {
+		TexMemo8Renorm(m.texture_sets8);
+		m.texture8_clock = 8;
+		Common::FrameStats::Add(Ctr::Tm8Renorm, 1);
+	}
+	return ++m.texture8_clock;
+}
+// A layout change (direct <-> 8-way): every entry invalid, every version moved, every recorded view dropped, every way
+// empty.  A binding resolved under the other layout (memo_index, memo_version) can never pass texfast eligibility or the
+// shadowresolve query again, because both require slot.version == binding.memo_version.
+static void Invalidate(RenderExecutorMemo& m) {
+	for (auto& t: m.textures) {
+		t.valid = false;
+		t.version++;
+		t.fast_view = nullptr;
+	}
+	std::fill(m.texture_sets8.begin(), m.texture_sets8.end(), RenderExecutorMemo::TextureSet8 {});
+	m.texture8_clock = 0;
+	Common::FrameStats::Add(Ctr::Tm8Inval, 1);
+}
+// The first call that sees another effective value.  0 <-> nonzero changes the layout: full invalidation.  Entering
+// 2/3: the direct shadow starts EMPTY (it models a direct memo that restarted at this layout edge; if the 8-way is
+// already full - 1 -> 2 - every hit counts as gained until the shadow fills: more verification, never less).
+static void Switch(RenderExecutorMemo& m, uint32_t mode) {
+	if ((m.texture_mode == 0) != (mode == 0)) {
+		Invalidate(m);
+	}
+	if (mode >= 2) {
+		m.texture8_direct.assign(RenderExecutorMemo::TextureSlots, {});
+	} else if (!m.texture8_direct.empty()) {
+		m.texture8_direct.clear();
+		m.texture8_direct.shrink_to_fit();
+	}
+	m.texture_mode = mode;
+	Common::FrameStats::Add(Ctr::Tm8Mode, 1);
+}
+// The direct shadow (texmemo8 >= 2): does the direct memo's slot memo_hash % 4096 hold K (and, when given, with id)?
+static bool DirectHolds(const RenderExecutorMemo& m, uint64_t h, uint64_t rk, const uint32_t* dwords,
+                        const ImageId* id) {
+	const auto& d = m.texture8_direct[h & DirectMask];
+	return d.valid && d.resource_key == rk && std::memcmp(d.dwords.data(), dwords, sizeof(d.dwords)) == 0 &&
+	       (id == nullptr || d.image_id == *id);
+}
+static void DirectPut(RenderExecutorMemo& m, uint64_t h, uint64_t rk, const uint32_t* dwords, ImageId id) {
+	auto& d        = m.texture8_direct[h & DirectMask];
+	d.resource_key = rk;
+	std::memcpy(d.dwords.data(), dwords, sizeof(d.dwords));
+	d.image_id = id;
+	d.valid    = true;
+}
+static void DirectDrop(RenderExecutorMemo& m, uint64_t h, uint64_t rk, const uint32_t* dwords) {
+	if (DirectHolds(m, h, rk, dwords, nullptr)) {
+		m.texture8_direct[h & DirectMask].valid = false;
+	}
+}
+// THE VERIFY CHECK (the census's bad check, r1.md section 7, on the real table): the hit claims (slot id, slot desc);
+// the fresh full resolution computed (id, desc, store) at the same moment.  The claim holds only if store and the id
+// (index AND generation) and the full desc digest agree.  `inject` (texmemo8 = 3): compare against a corrupted COPY.
+static bool Agree(bool gained, bool inject, const RenderExecutorMemo::Texture& slot, uint32_t index, ImageId id,
+                  const TextureCache::ImageDesc& desc, bool store) {
+	namespace FS     = Common::FrameStats;
+	ImageId    claim = slot.image_id;
+	if (inject) {
+		claim.generation ^= 0x80000000u; // the positive control: never written back
+	}
+	const auto a = R1DescDigest(slot.desc);
+	const auto b = R1DescDigest(desc);
+	FS::Add(gained ? Ctr::Tm8Check : Ctr::Tm8CtlCheck, 1);
+	if (store && id == claim && a.all == b.all) {
+		return true;
+	}
+	FS::Add(inject ? Ctr::Tm8Inject : (gained ? Ctr::Tm8Bad : Ctr::Tm8CtlBad), 1);
+	static std::atomic<uint32_t> logged {0};
+	static std::atomic<uint32_t> logged_inject {0};
+	if ((inject ? logged_inject : logged).fetch_add(1, std::memory_order_relaxed) < (inject ? 4u : 40u)) {
+		const uint32_t diff = a.groups ^ b.groups;
+		LOGF("%s: kind=%s set=%u way=%u store=%d id_same=%d slot_id=%u/%u fresh_id=%u/%u desc_same=%d"
+		     " info_differs=%d view_differs=%d source_differs=%d addr=0x%010" PRIx64 "\n",
+		     inject ? "Tm8VerifyInjected" : "Tm8VerifyMismatch", gained ? "gain" : "ctl", index / Ways, index % Ways,
+		     store ? 1 : 0, id == claim ? 1 : 0, slot.image_id.index, slot.image_id.generation, id.index,
+		     id.generation, a.all == b.all ? 1 : 0, (diff & 0x3ffu) != 0 ? 1 : 0, ((diff >> 10u) & 0x3ffu) != 0 ? 1 : 0,
+		     ((diff >> 20u) & 0x3ffu) != 0 ? 1 : 0, desc.info.data.address);
+	}
+	return false;
+}
+// texmemo8 >= 2, RebindImages: an ELIGIBLE binding must name a slot that holds exactly its (image, desc) - the version
+// contract that makes texfast safe under victim eviction and layout switches.
+static void CheckRebind(const RenderExecutorMemo::Texture& slot, const TextureBinding& binding) {
+	namespace FS = Common::FrameStats;
+	FS::Add(Ctr::Tm8RbCheck, 1);
+	if (slot.image_id == binding.image_id && R1DescDigest(slot.desc).all == R1DescDigest(binding.desc).all) {
+		return;
+	}
+	FS::Add(Ctr::Tm8RbBad, 1);
+	static std::atomic<uint32_t> logged {0};
+	if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
+		LOGF("Tm8RebindMismatch: index=%u version=%u slot_id=%u/%u binding_id=%u/%u addr=0x%010" PRIx64 "\n",
+		     binding.memo_index, binding.memo_version, slot.image_id.index, slot.image_id.generation,
+		     binding.image_id.index, binding.image_id.generation, binding.desc.info.data.address);
+	}
+}
+} // namespace Tm8
```

(`ImageId` field names `index`/`generation` as used by `R1CenMismatch` `:1869-1870`. The `^ 0x80000000u` only needs to
make the copy differ; the build agent picks whatever `ImageId` allows.)

### 2.2 `ResolveTextureWith` — the lookup (`:1992-2015`)

```cpp
@@ :1992-1996
 	auto&          memo         = Memo();
 	const bool     memo2        = Common::Gates::Enabled(Common::Gates::Gate::TexMemo2);
+	// Session 121, knob "texmemo8" (C:/kyty/s121/design/texmemo8.md): read ONCE per call - a knob read twice in one
+	// operation can tear (session 97).  texmemo2 wins (both write the textures entries through their own index);
+	// asking for both is counted (tm8_x2 must read 0).  The memo remembers the value it is laid out for; the first
+	// call that sees another one switches it (a layout change invalidates every entry).
+	const uint32_t tm8          = memo2 ? 0u : Common::Gates::Value(Common::Gates::Knob::TexMemo8);
+	if (memo2 && Common::Gates::Value(Common::Gates::Knob::TexMemo8) != 0) [[unlikely]] {
+		Common::FrameStats::Add(Common::FrameStats::Counter::Tm8WithMemo2, 1);
+	}
+	if (memo.texture_mode != tm8) [[unlikely]] {
+		Tm8::Switch(memo, tm8);
+	}
 	// Session 120, knob "r1cen" (MEASUREMENT ONLY, C:/kyty/s120/design/r1.md): read ONCE per call - a knob read twice
 	// in one operation can tear (session 97).  The census models the direct table only: off under texmemo2.
-	const uint32_t r1_level     = memo2 ? 0u : Common::Gates::Value(Common::Gates::Knob::R1Census);
+	// Session 121: and off under texmemo8 (its real-index bookkeeping, R1Hit's h & 4095, is the direct layout).
+	const uint32_t r1_req       = memo2 ? 0u : Common::Gates::Value(Common::Gates::Knob::R1Census);
+	const uint32_t r1_level     = tm8 != 0 ? 0u : r1_req;
+	if (tm8 != 0 && r1_req != 0) [[unlikely]] {
+		Common::FrameStats::Add(Common::FrameStats::Counter::Tm8CensusOff, 1);
+	}
@@ :2002-2010
 	const uint64_t memo_hash =
 	    MemoHashBytes(descriptor.fields, sizeof(descriptor.fields), resource_key);
+	// Session 121, knob "texmemo8": the set probe.  At >= 2 the 1/64 sample times it (never at 1: the P arm carries no
+	// per-lookup instrument, section 6).
+	const bool  tm8_smp   = tm8 >= 2 && (++memo.texture8_sample & 63u) == 0;
+	Tm8::Probe  tm8_probe {};
+	if (tm8 != 0) {
+		tm8_probe = tm8_smp ? Tm8::FindTimed(memo, memo_hash, resource_key, descriptor.fields)
+		                    : Tm8::Find(memo, memo_hash, resource_key, descriptor.fields);
+	}
 	const uint32_t memo_index =
 	    memo2 ? MemoTextureWay(memo, memo_hash)
-	          : static_cast<uint32_t>(memo_hash % RenderExecutorMemo::TextureSlots);
+	    : tm8 != 0 ? tm8_probe.index
+	               : static_cast<uint32_t>(memo_hash % RenderExecutorMemo::TextureSlots);
 	auto& memo_slot = memo.textures[memo_index];
 	const bool memo_key_match =
-	    memo_slot.valid && memo_slot.resource_key == resource_key &&
-	    std::memcmp(memo_slot.dwords.data(), descriptor.fields, sizeof(descriptor.fields)) == 0;
+	    tm8 != 0 ? tm8_probe.found // the probe ran the same three-term test on this entry
+	             : memo_slot.valid && memo_slot.resource_key == resource_key &&
+	                   std::memcmp(memo_slot.dwords.data(), descriptor.fields, sizeof(descriptor.fields)) == 0;
@@ :2011-2015
 	if (!memo_key_match) {
 		Common::FrameStats::Add(memo_slot.valid ? Common::FrameStats::Counter::TexMemoCollide
 		                                        : Common::FrameStats::Counter::TexMemoEmpty,
 		                        1);
+		if (tm8 >= 2) [[unlikely]] {
+			Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Miss, 1);
+			if (Tm8::DirectHolds(memo, memo_hash, resource_key, descriptor.fields, nullptr)) {
+				Common::FrameStats::Add(Common::FrameStats::Counter::Tm8DirectLose, 1); // a loss (census ~66.6/frame)
+			}
+		}
 	}
+	if (tm8 >= 2) [[unlikely]] {
+		Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Look, 1);
+	}
```

**Meaning of the existing counters under `texmemo8` ≥ 1** (unchanged names, the arming identities rest on them):
`texmemo_collide` = key miss whose victim way held another key (the store, if any, is an eviction); `texmemo_empty` =
key miss with an empty victim way; `texmemo_stale` = key found by the full proof, image failed liveness; `tex_hits`
(`BindTexMemoHits`, `:2067`) = hits. So `texmemo_collide + texmemo_empty` stays "key misses".

### 2.3 The full resolution as a local lambda (needed by VERIFY; behaviour-neutral)

The verify path must run exactly the miss path's resolution on a hit. It is moved, verbatim and in the same order,
into a lambda defined before the hit branch — after `:2015` (the closing `}` of the collide/empty `if`), before the
`// Session 120, knob "r1cen": nothing above the stamp r1_t0 is timed.` comment (`:2016`):

```cpp
+	// Session 121: the full resolution (formerly inline below the hit path), unchanged and in the same order, as a
+	// lambda so that texmemo8 >= 2 can run it on a hit.  It reads only descriptor / resource / storage and calls what
+	// the inline code called; `desc` arrives value-initialised (it was `TextureCache::ImageDesc desc {};`).
+	const auto resolve_full = [&](TextureCache::ImageDesc& desc, bool& store) -> ImageId {
+		<lines :2094-:2189 verbatim>
+		<line :2190 `TextureCache::ImageDesc desc {};` REMOVED - the parameter>
+		<lines :2191-:2250 verbatim>
+		store = !stencil_association && image->info.data == desc.info.data &&
+		        image->info.extent == desc.info.extent;
+		return id;
+	};
```

and the miss path becomes (replacing `:2094-:2252`):

```cpp
-	const auto address      = descriptor.Base40();
-	... (:2094-:2250) ...
-	const bool store = !stencil_association && image->info.data == desc.info.data &&
-	                   image->info.extent == desc.info.extent;
+	TextureCache::ImageDesc desc {};
+	bool                    store = false;
+	const ImageId           id    = resolve_full(desc, store);
```

`id` was `auto id` (reassigned inside for the stencil association, `:2226`) — that stays inside the lambda. The later
readers (`:2253-2272`: store, `R1Miss`, `emit`) see the same `id`, `desc`, `store`. The EXITs keep their text. **The
refactor must be proven neutral before any run:** compile, then the unsealed smoke's `texmemo8=0` arm must reproduce the
M-arm counters of cen120 in kind (`tex_hits`, `texmemo_*`, `texfast_*` per frame within noise), and `rtk git diff`
must show the moved block byte-identical except the two lines named above (a script can compare the old block with
the lambda body).

### 2.4 Hit path (`:2033-:2086`)

Insert the verify block at the top of the liveness-passed block — after `:2037`
(`    cached->info.extent == memo_slot.desc.info.extent) {`), before the `// Session 88, knob "bindwit": THE MEMO-HIT
DECISION IS COMPLETE HERE.` comment (`:2038`):

```cpp
+			// Session 121, knob "texmemo8" >= 2 (VERIFY, never a timed arm): a GAINED hit (the direct shadow does not
+			// hold this key with this id) and a 1/64 control sample of the other hits run the full resolution NOW -
+			// liveness has just been read at lookup time, as the census's pre mode - and are compared.  A disagreement
+			// returns and memoizes the FRESH answer (rendering stays correct), and counts tm8_bad / tm8_vctl_bad.
+			if (tm8 >= 2) [[unlikely]] {
+				const bool gained =
+				    !Tm8::DirectHolds(memo, memo_hash, resource_key, descriptor.fields, &memo_slot.image_id);
+				Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Hit, 1);
+				if (gained) {
+					Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Gain, 1);
+				}
+				if (gained || tm8_smp) {
+					const bool inject = tm8 == 3 && gained && (memo.texture8_sample & 1023u) == 0;
+					TextureCache::ImageDesc v_desc {};
+					bool                    v_store = false;
+					const ImageId           v_id    = resolve_full(v_desc, v_store); // FindImage: side effects, untimed arm
+					if (!Tm8::Agree(gained, inject, memo_slot, memo_index, v_id, v_desc, v_store)) {
+						if (v_store) {                        // a refill of THIS way with the fresh answer
+							memo_slot.image_id = v_id;
+							memo_slot.desc     = v_desc;
+							memo_slot.version++;
+							memo_slot.fast_view = nullptr;
+							memo.texture_sets8[memo_index / Tm8::Ways].use[memo_index % Tm8::Ways] = Tm8::Tick(memo);
+							Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Fill, 1);
+							Tm8::DirectPut(memo, memo_hash, resource_key, descriptor.fields, v_id);
+						} else {                              // unmemoizable: the way is emptied
+							memo_slot.valid = false;
+							memo_slot.version++;
+							memo_slot.fast_view = nullptr;
+							memo.texture_sets8[memo_index / Tm8::Ways].use[memo_index % Tm8::Ways] = 0;
+							Tm8::DirectDrop(memo, memo_hash, resource_key, descriptor.fields);
+						}
+						Common::DrawStat::Mark(Common::DrawStat::Memo);
+						return emit(v_id, v_desc, v_store ? memo_index : UINT32_MAX, v_store ? memo_slot.version : 0u);
+					}
+					// FindImage may have inserted images: SlotVector::insert can reallocate (slotVector.h:66-68), so
+					// `cached` is re-read.  v_id == slot id here, so the image exists.
+					cached = texture_cache.m_slot_images.try_get(memo_slot.image_id);
+					EXIT_IF(cached == nullptr);
+				}
+				if (gained) {
+					Tm8::DirectPut(memo, memo_hash, resource_key, descriptor.fields, memo_slot.image_id);
+				}
+			}
```

(At mode 3 `inject` is a COPY-level corruption: `Agree` returns false for an agreeing answer, the fresh answer — equal
to the memo's — is stored and returned; state stays correct. The build agent may prefer: on `inject`, count
`tm8_inject` and fall through to the hit tail without the refill — either is correct; pick one and fixture it.)

LRU touch — `:2068-2070`:

```cpp
 				if (memo2) {
 					memo.texture_ways[memo_index].use = ++memo.texture_clock;
+				} else if (tm8 != 0) {
+					memo.texture_sets8[memo_index / Tm8::Ways].use[memo_index % Tm8::Ways] = Tm8::Tick(memo);
 				}
```

The return `:2084-2085` (`return emit(memo_slot.image_id, memo_slot.desc, memo_index,` / `memo_slot.version);`) is
unchanged: under `texmemo8` it hands out `set·8+way` and that entry's version — texfast then keeps the way's recorded
view (the census's `R` term).

### 2.5 Stale path (`:2087-:2092`)

```cpp
 		Common::FrameStats::Add(Common::FrameStats::Counter::TexMemoStale, 1);
 		Common::DrawStat::Mark(Common::DrawStat::Memo);
 		memo_slot.valid = false;
 		memo_slot.version++;
 		memo_slot.fast_view = nullptr;
+		if (tm8 != 0) {
+			// Invariant I-T: the way is empty again.  memo_index still names it, so a store below refills THIS way -
+			// what the direct memo does with its slot and what the census's R1Fill(found = true) modelled.
+			memo.texture_sets8[memo_index / Tm8::Ways].use[memo_index % Tm8::Ways] = 0;
+			if (tm8 >= 2) {
+				Tm8::DirectDrop(memo, memo_hash, resource_key, descriptor.fields);
+			}
+		}
 	}
```

### 2.6 Miss path store (`:2253-:2265`) — insert + evict

```cpp
+	// Session 121, knob "texmemo8": a key miss whose victim way holds another key is an EVICTION; the store below moves
+	// the way's version and drops its view like any store.  Read before the store overwrites them.
+	const bool tm8_evict = tm8 != 0 && !memo_key_match && memo_slot.valid;
+	const bool tm8_view  = tm8_evict && memo_slot.fast_view != nullptr;
 	if (store) {
 		std::memcpy(memo_slot.dwords.data(), descriptor.fields, sizeof(descriptor.fields));
 		Common::DrawStat::Mark(Common::DrawStat::Memo);
 		memo_slot.resource_key = resource_key;
 		memo_slot.image_id     = id;
 		memo_slot.desc         = desc;
 		memo_slot.valid        = true;
 		memo_slot.version++;
 		memo_slot.fast_view = nullptr;
 		if (memo2) {
 			memo.texture_ways[memo_index] = {memo_hash, ++memo.texture_clock};
+		} else if (tm8 != 0) {
+			auto& set                        = memo.texture_sets8[memo_index / Tm8::Ways];
+			set.tag[memo_index % Tm8::Ways]  = Tm8::Tag(memo_hash);
+			set.use[memo_index % Tm8::Ways]  = Tm8::Tick(memo);
+			Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Fill, 1);
+			if (tm8_evict) {
+				Common::FrameStats::Add(Common::FrameStats::Counter::Tm8Evict, 1);
+			}
+			if (tm8_view) {
+				Common::FrameStats::Add(Common::FrameStats::Counter::Tm8EvictView, 1);
+			}
+			if (tm8 >= 2) {
+				Tm8::DirectPut(memo, memo_hash, resource_key, descriptor.fields, id);
+			}
 		}
-	}
+	} else if (tm8 >= 2) {
+		// No store: the direct memo would keep its slot, which holds K only in the loss case (and then only while K is
+		// live).  Dropping K errs toward MORE gained hits (more verification), never fewer.
+		Tm8::DirectDrop(memo, memo_hash, resource_key, descriptor.fields);
+	}
```

A key miss with no store leaves the victim way untouched (its key J stays), exactly like today's direct slot. The
r1cen block (`:2266-2270`) and the final `emit` (`:2271-2272`) are unchanged (`r1_on` is false under `texmemo8`).

### 2.7 Why the direct shadow classifies "gained" exactly or conservatively

`texture8_direct[h & 4095]` models the direct memo's slot content = the last key stored there and not invalidated
since. Mirror, event by event (both memos see the same lookup stream from the same layout edge, where both are empty):
* **8-way store of K** (miss or stale with `store`): the direct memo would afterwards hold K too (it had K live → hit;
  had K dead → stale → the same store; lacked K → miss → the same store) ⇒ `DirectPut(K, id)`. Exact.
* **8-way hit on K, shadow holds (K, same id)**: not gained; nothing changes. Exact.
* **8-way hit on K, shadow does not**: gained ⇒ the direct memo would miss and store (the verify computes `store`; a
  `store == false` is itself a bad) ⇒ `DirectPut`. Exact.
* **8-way stale on K**: the direct memo, if it held K, held the same id (every store updates both) ⇒ it is stale too
  ⇒ `DirectDrop`. Exact.
* **8-way key miss, no store**: the direct memo keeps K only in the loss case while K is live; the shadow drops K ⇒
  later hits of K count as gained ⇒ conservative.
* **1 → 2 without invalidation**: the shadow starts empty ⇒ conservative.
So a hit is classified "not gained" only if the direct memo would really have hit it with the same id; the verify
never skips a hit the direct index could not have produced.

### 2.8 `RebindImages` (`:3572-:3605`)

```cpp
@@ :3575
 	auto*      memo       = fast ? &Memo() : nullptr;
+	// Session 121, knob "texmemo8" >= 2 (VERIFY): every ELIGIBLE binding is checked against the slot it names
+	// (Tm8::CheckRebind).  The mode latched in the memo by ResolveTextureWith: no knob load on this path.
+	const bool tm8_check  = memo != nullptr && memo->texture_mode >= 2;
@@ :3581-3584
 	uint32_t r1_level = fast ? Common::Gates::Value(Common::Gates::Knob::R1Census) : 0u;
-	if (r1_level != 0 && Common::Gates::Enabled(Common::Gates::Gate::TexMemo2)) {
+	if (r1_level != 0 && (Common::Gates::Enabled(Common::Gates::Gate::TexMemo2) || memo->texture_mode != 0)) {
 		r1_level = 0;
 	}
@@ after :3605 (`			                      !image.binding.needs_rebind;`)
+			if (tm8_check && eligible) [[unlikely]] {
+				Tm8::CheckRebind(*slot, binding);
+			}
```

(`memo` is non-null whenever `r1_level != 0`, because `r1_level` is read only when `fast`.)

### 2.9 `PrepareBindings` R2 (`:3161-:3164`)

```cpp
 	if (r2 != 0) [[unlikely]] {
-		if (!Common::FrameStats::Enabled() || Common::Gates::Enabled(Common::Gates::Gate::TexMemo2)) {
+		if (!Common::FrameStats::Enabled() || Common::Gates::Enabled(Common::Gates::Gate::TexMemo2) ||
+		    Common::Gates::Value(Common::Gates::Knob::TexMemo8) != 0) {
+			if (Common::Gates::Value(Common::Gates::Knob::TexMemo8) != 0) {
+				Common::FrameStats::Add(Common::FrameStats::Counter::Tm8CensusOff, 1);
+			}
 			r2 = 0;
```

(Loads only when `r2cen != 0`. R2's replay indexes `h % 4096` (`:3057`) and its `bad_key` detector assumes "+1 =
direct slot mismatch" (`:2950-2957`): both are direct-layout constructs.)

### 2.10 `gates.h` / `gates.cpp` / `frameStats.h` / `videoOut.cpp`

`gates.h` after `:632` (`R2Census, ...`), before `Count,` (`:633`); move the "LAST row" note from `R2Census`'s comment
(`:628-631`):

```cpp
+	// Session 121 (C:/kyty/s121/design/texmemo8.md, docs/session-121/design121.md): the texture memo as 512 sets x 8
+	// ways of the same 4 096 entries (entry = set * 8 + way).  0 = direct (default), 1 = 8-way, 2 = 8-way + VERIFY
+	// (MEASUREMENT ONLY, never timed: gained hits and a 1/64 control against a fresh full resolution, the texfast
+	// contract in RebindImages, a sampled probe timer; tm8_bad / tm8_vctl_bad / tm8_rbbad must read 0), 3 = 2 + a
+	// positive control (tm8_inject > 0, state untouched).  Read once per ResolveTextureWith call, so it CAN be a
+	// schedule arm: a change between 0 and nonzero invalidates the whole memo.  Off under texmemo2 (tm8_x2 counts);
+	// forces r1cen / r2cen off (tm8_cenoff counts).
+	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
+	TexMemo8,         // KYTY_TEX_MEMO8,          file name "texmemo8" (0 direct, 1 8-way, 2 verify, 3 verify + control)
```

`gates.cpp` `KNOB_DEFINITIONS` after `:420` (`{"KYTY_R2_CENSUS", "r2cen", 0, 2},`); move the "LAST row" note (`:419`):

```cpp
+    // Session 121: the 8-way texture memo (1), with VERIFY (2, MEASUREMENT ONLY) and a positive control (3). Read once
+    // per ResolveTextureWith call, so it CAN be a schedule arm (a layout change invalidates the memo).
+    // LAST row, matching the LAST enum entry before Knob::Count.
+    {"KYTY_TEX_MEMO8", "texmemo8", 0, 3},
```

Then `python C:/kyty/s96/check_gate_order.py` BEFORE the build (the order is not compiler-checked). Name check:
`FindAssignment` is token-bounded (`gates.cpp:458-470`, r1_review §1); `texmemo8` ≠ `texmemo2`; no `FrameTrace-x`
name starts with `tm8_`. `texmemo8` is not in `gates_base.txt` — the schedule owns it; **every arm text names it once**
(first assignment wins — s111 trap).

`frameStats.h` after `:2138` (`SpTrMissFlags,           // sp_tr_x_flags`), before `Count` (`:2139`): the 24 enumerators of
§6 with one comment block ("Session 121 (knob "texmemo8", C:/kyty/s121/design/texmemo8.md): raw counts / raw ns.
tm8_bad, tm8_vctl_bad, tm8_rbbad, tm8_x2, tm8_cenoff must read 0; tm8_inject > 0 only at texmemo8 = 3.").
`videoOut.cpp` after `:2743` (`{"sp_tr_x_flags", FS::Counter::SpTrMissFlags, false},`): the 24 rows
`{"tm8_…", FS::Counter::Tm8…, false}` — all `micros = false`.

## 3. Every reader of `memo_index` / `version` / `fast_view` and what each needs

| # | reader (file:line) | what it reads/writes | what it needs | under `texmemo8` |
|---|---|---|---|---|
| 1 | `ResolveTextureWith` hit/stale/store (`descriptors.cpp:2004-2272`) | all fields | index names the entry holding the key; version moves on every store/invalidation | §2.2–2.6; a victim eviction IS a store (`version++`, `fast_view = nullptr`, `:2260-2261`) |
| 2 | `RebindImages` texfast (`:3594-3662`): eligibility `:3597-3605`, fast view `:3610-3617`, record `:3657-3658`, texfastcheck reset `:3642` | `textures[binding.memo_index]`: `valid`, `version`, `image_id`, `fast_view`, `fast_stamp` | `memo_index < 4096`; `version == memo_version` ⇒ the entry still holds exactly the (id, desc) the binding came from (desc: nobody writes `binding.desc` after emit — grep of `(binding\|images[i]\|b).desc… =` in `renderer/` finds none) | holds: every store/eviction/invalidation moves `version`; a binding resolved under the other layout fails by the invalidation bump. **Checked in the verify arm** (`tm8_rbchk`/`tm8_rbbad`, §2.8). A binding whose way is evicted later in the same draw re-records via `FindTexture` (correct, a few extra calls) |
| 3 | `ShadowQueue` (`:3846-3852`) → worker `TextureCache::ShadowProbe` (`textureCache.cpp:2162-2200`) | the same predicate as #2, read-only, copied into the job | same as #2 | holds; `shadowresolve=0` pinned in every run (`gates_base.txt`) |
| 4 | `R2Reproduced` (`:2850-2864`) | `textures[s.memo_index]`: `version`, `valid`, `image_id` | same as #2 | generic, but R2's replay (`:3054-3063`, `h % 4096`) and `bad_key` (`:2950-2957`) are direct-layout ⇒ **r2cen forced off** (§2.9) |
| 5 | r1cen census (`R1Hit` real index `h & 4095` `:1729`, `R1Miss` marks `:1885-1888`, `RebindImages` marks `:3669-3678`) | index/marks | the direct layout | **forced off** (§2.2, §2.8) |
| 6 | compute clear shortcut (`renderCompute.cpp:195`, `const auto  binding     = ResolveTexture(resource, resources.images[0]);`) | only `image_id`/`desc` of the result | a correct answer | goes through the 8-way like any lookup; `memo_index` unused; nothing to change |
| 7 | `RebindImages` repair loop (`:3536-3546`, `images[i] = ResolveTexture(...)`) | the fresh binding's index/version, consumed by #2 in the same call | as #1 | nothing to change |
| 8 | `PrepareBindings` image loop (`:3238-3243`) | emits the binding (`emplace_back(id, desc, index, version)`) | as #1 | nothing to change; `bindwit` marks (`:2048-2050`, `:2077-2079`) untouched — the verify block sits before them and `bindwit` is 0 in every run |
| 9 | `texmemo2` (`MemoTextureWay` `:1318-1335`, `texture_ways` `:2069`, `:2263`) | its own way index into the same entries | exclusive use of the entries | **mutually exclusive**: `texmemo2` wins, `tm8_x2` counts, `gates_base.txt` pins `texmemo2=0` and the scorer asserts it |
| 10 | null-texture memo (`:1923-1966`), colour/depth memos (`colorRenderTarget.cpp:131-172`, `depthRenderTarget.cpp:296-334`, `renderDraw.cpp:995`) | separate arrays | — | unaffected |

## 4. Knob semantics

1. **Read once per call.** `tm8` is a local read by one relaxed `Gates::Value` at the top of the memo part
   (`gates.h` `Value`: one relaxed atomic load once `g_ready`). Every decision of the call — probe, hit, verify, stale,
   store, LRU — uses the local (s97 tear rule). `RebindImages` does not read the knob; it reads the mode the memo is
   laid out for (`memo->texture_mode`), latched by the resolves of the same draw.
2. **Flip mid-frame / ABBA block edge.** `Gates::Poll` runs once per flip on the presentation thread; the schedule
   writes `g_block` then applies the arm (`gates.cpp:638-649`, r1_review §1). GuestGpu sees the new value at its next
   resolve, possibly mid-frame or between two stages of one draw. **Detection is by value, not by block:** the memo
   stores the effective value it is laid out for (`texture_mode`); the first call whose `tm8` differs runs
   `Tm8::Switch`. A change 0 ↔ nonzero runs `Tm8::Invalidate`: `valid = false`, `version++`, `fast_view = nullptr` on
   all 4 096 entries, all ways empty, clock 0 (≈ 8 192 line writes ≈ 0.1–0.3 ms [I], once per flip edge). Any
   `TextureBinding` still carrying a `(memo_index, memo_version)` of the other layout — the earlier stages of a draw
   straddling the edge, `drawstate`/`snapkeep`-kept `PreparedBindings` — fails eligibility (#2/#3) by the version bump
   and re-records through `FindTexture`: correct, a few µs at the edge. A change 1 ↔ 2/3 keeps the entries (same
   layout) and only (re)starts or drops the direct shadow.
   ABBA symmetry: in `A B B A` the edges A→B and B→A invalidate and the continuation blocks do not — each arm gets
   one cold and one warm block start per quartet; the refill (≈ 3 000 misses × 0.5 µs ≈ 1.5 ms [I]) lands in block
   positions 0–2, outside the window 10–88.
3. **Mutual exclusion with `texmemo2`.** `tm8 = memo2 ? 0 : Value(TexMemo8)`: texmemo2's path is byte-for-byte
   unchanged; asking for both counts `tm8_x2` (the extra knob load only when `texmemo2=1`). `gates_base.txt` pins
   `texmemo2=0`; the scorer asserts it in the base and in both arm texts (it must not appear there at all, or = 0).
4. **Censuses off under it.** `r1cen` forced 0 in `ResolveTextureWith` and `RebindImages`, `r2cen` forced 0 in
   `PrepareBindings`; a request counts `tm8_cenoff`. `spcen` (render-target / transition census) does not read the
   texture memo, but the timed arms name `spcen=0` anyway (s120 price of the three censuses: +2.77 ms, closure §5.6).
5. **Threads.** Only GuestGpu resolves textures (census `r1_xthr` = 0 on all cen120 rows [M]); every `texmemo8` state
   lives in the executor's memo and is touched only under the render mutex on that thread. No lock, no atomic beyond
   the knob load and the two static log budgets.

## 5. VERIFY (`texmemo8 = 2`, positive control `= 3`)

### 5.1 What is checked

* **Gained hits — every one.** A hit is gained when the direct shadow (§2.7) does not hold its key with its id — the
  population the direct index h % 4096 would not have produced, i.e. exactly what `texmemo8` adds. Comparing with the
  direct memo there would be vacuous (it has no answer — closure §5.1): each gained hit instead runs `resolve_full`
  (the miss path: layout, validations, `FindImage`, view validation, DCC adoption) right after the hit's liveness test
  passed (lookup time, as the census's exact pre mode) and requires
  `store ∧ fresh_id == slot.image_id ∧ R1DescDigest(fresh_desc).all == R1DescDigest(slot.desc).all`
  (`R1DescDigest` `:1468-1515`: every consumer-read field, member-wise, never a memcmp of the padded `ImageDesc`).
  Fail ⇒ `tm8_bad` + `Tm8VerifyMismatch: kind=gain …` (≤ 40 lines a process; the line names both ids and which desc
  group differs), and the fresh answer is memoized and returned (§2.4).
* **Control — 1/64 of the other hits** (`tm8_vctl`, `tm8_vctl_bad`, `kind=ctl`, same budget). These are hits the
  direct memo would have made: a failure there says the EXISTING memo can return a stale answer (r1.md §7 rule — the
  session records it before anything else).
* **The texfast contract** in `RebindImages`: every eligible binding's slot must hold exactly the binding's id and desc
  digest (`tm8_rbchk`, `tm8_rbbad`, `Tm8RebindMismatch:` ≤ 40). This is the audit's "eligible under a stale layout"
  control (closure §5.3) and covers victim eviction too.
* **Recommended in the same smoke arm:** `texfastcheck=1` (existing gate, `:3621-3645`): every fast view is compared
  with `FindTexture` (`texfast_bad` must read 0) — a view-level check of texfast under the 8-way.
* **Positive control (`= 3`):** every 1 024-th gained hit is compared against a copy of the slot id with a flipped
  generation bit ⇒ `tm8_inject` ≈ `tm8_gain`/1 024 and `Tm8VerifyInjected:` (own budget of 4 lines, so it can never
  hide a real mismatch line). Proves in the running game that the comparison, the counter and the log path fire.

### 5.2 What the verify arm is not

It runs `FindImage` (TouchImage, `ConfigureImageSourceUnlocked`, unconditional DCC adoption) on ≈ 1 260 + 720 hits a
frame [I] and so is slower and has more side effects than `texmemo8=1`: **never a timed arm, never a video of record
for SHIP** (the video of record is of `texmemo8=1` blocks, §8.2). Its answer is the fresh one wherever they disagree,
so its rendering is correct even when it finds a defect.

### 5.3 Coverage

≈ 1 190–1 260 gained hits a frame [I from W and losses] × ≈ 5 000 frames of a 180-s smoke ⇒ ≈ 6 M exact checks; any
disagreement mechanism above ≈ 10⁻⁶ per gained hit shows. Limits (stated): the check covers the answer, not the side
effects (argued equal, r1_review §3); a defect that only appears after the image dies between the check and a later
use is the existing memo's liveness question, not the table's.

## 6. Counters (`FrameTrace-x`, raw counts / raw ns, `micros = false`)

**Cost rule:** at `texmemo8=1` (the timed P arm) only rare-path counters exist (fills ≈ 500–600 a frame [I], the
others rarer) ≈ ≤ 3 µs a frame; **no per-lookup Add, no RNG, no stamp** in the P arm — a per-hit Add (≈ 1–1.5 ns ×
46 k ≈ 50–70 µs [I]) would bias the ABBA against P by ≈ 15–20 % of the predicted gain. Per-lookup counters exist only
at ≥ 2 (never timed). Lookups/hits/misses of the timed arms come from the EXISTING counters both arms pay
(`b_texn`, `tex_hits` on `FrameTrace-draw:`; `texmemo_*`, `texfast_*` on `FrameTrace-x:`).

| # | enum | name | mode | meaning | identity / bound |
|---:|---|---|:-:|---|---|
| 1 | `Tm8Fill` | `tm8_fill` | ≥1 | stores into a way (key miss or stale with `store`, verify refills) | ≤ collide + empty + stale (+ bad at ≥2); **> 0 in every P block = arming proof**; 0 in M windows |
| 2 | `Tm8Evict` | `tm8_evict` | ≥1 | fills whose victim way held another key | ≤ min(`tm8_fill`, `texmemo_collide`) |
| 3 | `Tm8EvictView` | `tm8_evict_view` | ≥1 | of those, the victim held a recorded texfast view | ≤ `tm8_evict` |
| 4 | `Tm8Alias` | `tm8_alias` | ≥1 | tag matches whose full proof failed | ~0 (census `r1_tagx`) |
| 5 | `Tm8Inval` | `tm8_inval` | any | full invalidations (0 ↔ nonzero) | ≈ 1 per flip edge, block position 0 only |
| 6 | `Tm8Mode` | `tm8_mode` | any | mode switches | ≥ `tm8_inval`; position 0 only |
| 7 | `Tm8Renorm` | `tm8_renorm` | ≥1 | clock renormalisations | 0 in a 300-s run |
| 8 | `Tm8WithMemo2` | `tm8_x2` | any | calls with texmemo2 on and texmemo8 requested | **must be 0** (all rows) |
| 9 | `Tm8CensusOff` | `tm8_cenoff` | ≥1 | r1cen/r2cen requested under texmemo8 (calls) | **must be 0** (all rows) |
| 10 | `Tm8Look` | `tm8_look` | ≥2 | memo lookups | = `tex_hits + texmemo_collide + texmemo_empty + texmemo_stale + tm8_bad + tm8_vctl_bad + tm8_inject` |
| 11 | `Tm8Hit` | `tm8_hit` | ≥2 | hits before verification | = `tex_hits + tm8_bad + tm8_vctl_bad + tm8_inject` |
| 12 | `Tm8Gain` | `tm8_gain` | ≥2 | gained hits (§2.7) | ≤ `tm8_hit`; predicted ≈ 1 190–1 260 a frame |
| 13 | `Tm8Miss` | `tm8_miss` | ≥2 | key misses | = `texmemo_collide + texmemo_empty` |
| 14 | `Tm8DirectLose` | `tm8_dlose` | ≥2 | key misses the direct shadow held (losses, upper) | info; census ≈ 66.6 |
| 15 | `Tm8Check` | `tm8_vchk` | ≥2 | gained hits verified | = `tm8_gain` |
| 16 | `Tm8Bad` | `tm8_bad` | ≥2 | gained hits that disagreed | **must be 0** (all rows) |
| 17 | `Tm8CtlCheck` | `tm8_vctl` | ≥2 | control-sample hits verified | / (`tm8_hit − tm8_gain`) ∈ [1/80, 1/50] |
| 18 | `Tm8CtlBad` | `tm8_vctl_bad` | ≥2 | control hits that disagreed | **must be 0** |
| 19 | `Tm8RbCheck` | `tm8_rbchk` | ≥2 | eligible `RebindImages` bindings checked | > 0; ≤ `texfast_ok + texfast_no` |
| 20 | `Tm8RbBad` | `tm8_rbbad` | ≥2 | eligible bindings whose slot holds another (id, desc) | **must be 0** |
| 21 | `Tm8Probe0Ns` | `tm8_pb0_ns` | ≥2 | null stamp pairs of the probe sample | |
| 22 | `Tm8ProbeNs` | `tm8_pb_ns` | ≥2 | timed probes (`Find`) | t_pb = max(0, (Σ pb − Σ pb0)/Σ n) — reported, informational |
| 23 | `Tm8ProbeN` | `tm8_pb_n` | ≥2 | probe samples | / `tm8_look` ∈ [1/80, 1/50] |
| 24 | `Tm8Inject` | `tm8_inject` | 3 | positive-control mismatches | ≈ `tm8_gain`/1 024 at 3; **0 at 1 and 2** |

Tolerance of every counted identity: the s120 decision, ±8 counts on the sum of a block's window (the flip reads
counters one by one, s116; ROADMAP s120 item 6); a constant offset of one a row fails.

**Arming identities between the arms of the timed ABBA** (window means, P − M; predictions from cen120 [M]/[I]):
* `tex_hits` **+≈ 1 190** (W 1 258.7 minus ≈ 66.6 losses), admitted band [+800, +1 500];
* `texmemo_collide + texmemo_empty` **−≈ 1 190**, band [−1 500, −800] (collide carries almost all of it: empty ≈ 0.2);
* `texmemo_stale` per arm reported (M ≈ 7.4 [M, s118]; P may rise — longer residency); no band;
* `texfast_rec` and `texfast_no` **down** (direction only; the census's `R` term 81.1 µs is its price, not a count);
  `texfast_ok` up;
* `b_texn` equal within noise (same lookups);
* `tm8_fill` > 0 in every P window block and 0 in every M window row; mode-≥2 counters 0 everywhere; `r1_*`, `r2_*`,
  `sp_*` (except the always-counted `sp_ser_*`) 0 in both arms.

## 7. What must not change at `texmemo8 = 0`

* **Behaviour, byte for byte, in a run that never arms it:** control flow, memo contents, `version`, `fast_view`,
  every existing Add and its order (`texmemo_*`, `tex_hits`, `tnull_*`, `b_texn`), `bindwit` marks, emit arguments;
  `texmemo2` path; r1cen/r2cen at 0 and nonzero (`r1_level = r1_req` when `tm8 == 0`).
* **Added cost at 0 (both arms pay it):** one relaxed knob load and one compare of `memo.texture_mode` (same line as
  `textures`' header) per call that reaches the memo; three never-taken `tm8 != 0`/`tm8 >= 2` branches; the miss path
  as a lambda (same statements; codegen may differ — irrelevant to the ABBA, both arms run one binary); in
  `RebindImages` one field load (`memo->texture_mode`) per call when `fast` and one never-taken branch per eligible
  binding. ≈ ≤ 30 µs a frame [I], symmetric.
* **Layout:** `RenderExecutorMemo` gains 12 B + two vectors (32 KiB zeroed once; the direct shadow empty). `Texture`,
  `TextureBinding`, `RenderExecutor`, `render.h` untouched.
* **After a nonzero period** (ABBA M blocks): the first call at 0 invalidates ⇒ the direct memo restarts cold, as in a
  fresh process — correct, and it is the M arm's half of the symmetric edge cost (§4.2).
* Nothing under `src/graphics/shader/**` (translation-cache signature unchanged).
* `FrameTrace-x` gains 24 names at its end (scorers read by name).

## 8. Protocol

### 8.1 Order (ROADMAP s121 item 1, with this design's details)

1. Record this design (after the adversarial review) in ROADMAP and `docs/session-121/design121.md` BEFORE any code
   line (s120 item 8(7)), including: the knob range 0..3 (value 3 is new), the verify smoke's rule (§8.2), the sealed
   rule (§8.3), the rerun rule.
2. Code (§2), `check_gate_order.py`, one build; offline unit test (§8.5); the refactor neutrality check (§2.3).
3. **Unsealed verify smoke `vfy121` (disclosed), 180 s, Sky Garden, pinned**, rule written before it runs (§8.2).
4. Scorer `shp121.py` + fixtures + mutants (`mutlib` v4.1 FULL, `--control --no-memo --work-dir/--cache-dir
   C:/kyty/s121/...`), a pre-seal check agent, the seal (pred `pred/01_shp121.md` with its sha in the scorer).
5. Pause after `mutlib`; one sealed ABBA `shp121` (§8.3); `shp121r` only on NOT_ADMITTED.
6. Audit, close.

### 8.2 Verify smoke `vfy121` (unsealed, disclosed; never timed)

Schedule without ABBA, 4 arms so that every edge kind occurs: `KYTY_GATE_SCHEDULE=90+1800:<a2>|<a1>|<a0>|<a3>`,
sequence 2, 1, 0, 3, 2, 1, 0, 3 … (edges 2→1 keep-layout, 1→0 invalidate, 0→3 invalidate + shadow, 3→2 keep):
`aN = texmemo8=N texfastcheck=1 r1cen=0 r2cen=0 spcen=0` (every arm names every scheduled name). `KYTY_REC` on (the
video: glitch scan of the whole recording, `s51_vidglitch.py`; one-frame glitches = 0 required in the `texmemo8=1`
blocks, reported for all). Pin, `KYTY_GPU_MARKERS=0`, `gates_base.txt`.
**PASS** iff over ALL rows of the run: `tm8_bad = tm8_vctl_bad = tm8_rbbad = texfast_bad = tm8_x2 = tm8_cenoff = 0`,
no `Tm8VerifyMismatch:`/`Tm8RebindMismatch:`/`TexFastVerify: MISMATCH` line; `tm8_inject > 0` in every mode-3 window
block and 0 elsewhere, `Tm8VerifyInjected:` lines present; identities 10–13, 15, 17, 19, 23 of §6 within ±8 per block
window; mode-2/3 window means `tm8_gain` ∈ [600, 2 000]; no fatal marker (`--- Error ---`, `--- Fatal Error ---`,
`--- std::terminate ---`, `AsyncPipelines: skipped draw` in the window); the `texmemo8=0` arm's `tex_hits`,
`texmemo_*`, `texfast_*` per frame in kind with cen120's M arm (refactor neutrality). FAIL ⇒ no seal; the track stops
and records the mismatch (and, if `kind=ctl`, that the existing memo is suspect).

### 8.3 Sealed ABBA `shp121`

* Build: the one build of step 2 (pinned copy `C:/kyty/s121/kyty_emulator_<sha8>.exe`, sha in the chain and the
  scorer). Sky Garden via `enter_scene.py` (neutral launcher name), 300-s hold, one attempt, `KYTY_FRAME_TRACE=lite`
  (set by `enter_scene.py`), `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, no `KYTY_REC`, no `KYTY_GPU_TIME`, no
  `KYTY_GPU_CHECKPOINTS` (s101 trap), `gates_base.txt` (pins `texmemo2=0 texfastcheck=0 fslean=0 mutsite=0 m4baton=0
  shadowresolve=0`; `bindlap`, `pathlap`, `bindwit`, `bindalt`, `slicecen`, `spine` absent = 0).
* `KYTY_GATE_SCHEDULE=90+1800:texmemo8=1 r1cen=0 r2cen=0 spcen=0|texmemo8=0 r1cen=0 r2cen=0 spcen=0`,
  `KYTY_GATE_SCHEDULE_ABBA=1`. P = arm 0 (`texmemo8=1`), M = arm 1.
* Chain `go121a.sh` = `go120a.sh` ported: lock `C:/kyty/SEALED_RUN.lock`, `procload.py` (refuses while `mutlib` or a
  mutant/fixture process of `shp121` lives), pred sha = scorer `PRED_SHA`, installed sha, idle CPU/GPU, per-process CPU
  sampling during the run (s120 item 8(7)), no agent work during the run.
* **Estimator (the program's):** per block, mean of main-line `dt_us` over block positions 10..88 (s119/s120 window
  rule); ABBA pairs (b, b+1), (b+2, b+3) of each quartet (as `C:/kyty/s111/shp111.py` `select`), only blocks that reached
  position 88; Δ = mean over pairs of (P − M); 2SE = 2·sd/√n_pairs. The same for `cpu_gpu_us` (reported).
* **Pre-registered prediction** [I]: Δ`dt_us` ≈ **−350 µs** (range −250 … −500); power of the ship rule at 2SE
  0.14–0.18 ms: true −0.25 ms ⇒ 79–95 %, −0.35 ⇒ 94–99 %, −0.15 ⇒ 38–54 %. Secondary: Δ`tex_hits` ≈ +1 190, Δ key misses
  ≈ −1 190, `texfast_rec` down, `b_texn` equal. A null or small result means the census ceiling was loose (closure
  §1.2 lists where: hot `t_hit`, cold-slot emit, E/t_T census pollution, under-priced probe and LRU writes, R as an
  upper), not that the mechanism is wrong.
* **Rule (ROADMAP s120 item 2(в), s121 item 1), fixed before the run:** **SHIP** (default `texmemo8` → 1 in
  `KNOB_DEFINITIONS`; later harnesses pin `texmemo8=1` in `gates_base.txt` in place) iff (a) `shp121` ADMITTED,
  (b) Δ + 2SE < 0 (the whole 2SE interval of Δ`dt_us` below 0, strictly), (c) `vfy121` PASS (0 mismatches of any
  kind), (d) its video clean. Otherwise **NO_SHIP**: the R1 track is closed with its measured Δ ± 2SE (on Sky Garden,
  this build, pinned). NOT_ADMITTED ⇒ one rerun `shp121r`, then NOT_EVALUABLE.

### 8.4 Scorer `shp121.py`: admission checks, fixtures, mutants

Admission (as `rpk120`): binary sha, installed_now, pinned copy, env exact (the variables above and nothing else of the
`KYTY_*` family that changes behaviour), hold, one ok attempt, prereg + prereg sha, gates exact (base file sha),
gate lines, arm texts exactly the two above, no fatal marker, no skipped-draw marker in the window, streams complete
(`FrameTrace:`, `-draw:`, `-x:` for every flip of the measured area except the last line), pairs ≥ 30, idle, BDA regime
(`bda_scan`) the same in both arms and reported (NEW ≈ 50–60, OLD ≈ 1 060 a frame).

Fixtures (synthetic rows; one per member and per edge; the suite ends with `ALL OK`):

| id | fixture | expected |
|---|---|---|
| S1 | arm by `GateArm:` text: a P row whose text lacks `texmemo8=1`, or an M row with `texmemo8=1`; the texts naming `texmemo2`, `texfastcheck=1`, `r1cen=2`, or missing `spcen=0` | NOT_ADMITTED each |
| S2 | arming: a P window block with Σ`tm8_fill` = 0; an M window row with `tm8_fill` = 1 (leak); a row anywhere with `tm8_look`/`tm8_hit`/`tm8_vchk`/`tm8_pb_n` > 0 (a verify leak into a timed arm) | NOT_ADMITTED each |
| S3 | zeros on ALL rows: `tm8_x2` = 1, `tm8_cenoff` = 1, `tm8_bad` = 1, `tm8_rbbad` = 1, `tm8_inject` = 1 — each at block positions 3, 50 and 95 | NOT_ADMITTED (x2/cenoff) / NO_SHIP-FAIL (bad/rbbad/inject) at every position |
| S4 | arming bands: Δ`tex_hits` = +799.9 / +800.0 / +1 500.0 / +1 500.1; Δkey misses −799.9 / −800 / −1 500 / −1 500.1 | outside ⇒ NOT_EVALUABLE ("not armed as predicted"), inside ⇒ passes |
| S5 | window: rows at positions 9 and 89 with `dt_us` = 10⁶ | Δ unchanged to 1e-9 |
| S6 | pairs: a quartet whose last block stops at position 87; an arm order B A A B at the start | the short block and its pair dropped; pairing by arm label, P − M sign kept |
| S7 | estimator arithmetic: 4 pairs Δ = −300, −400, −350, −350 ⇒ mean −350.0, sd 40.82, 2SE 40.82 | exact to 1e-6 |
| S8 | ship edge: Δ = −350, 2SE = 350 (upper exactly 0) ⇒ NO_SHIP; 2SE = 349.999 ⇒ SHIP; Δ = +10 ⇒ NO_SHIP | as stated (strict) |
| S9 | verify evidence: `vfy121` summary with PASS / FAIL / missing / sha mismatch; video flag clean / glitch / missing | SHIP only with PASS + clean + matching sha |
| S10 | BDA regime: P NEW, M OLD | NOT_EVALUABLE |
| S11 | units: `dt_us` µs, `tm8_pb*_ns` ns converted once | a double conversion fails S7-style arithmetic |
| S12 | fatal marker `--- std::terminate ---` inside the hold | NOT_ADMITTED |
| S13 | identity skew: `tex_hits + collide + empty + stale` vs `b_texn − tnull_*` off by 8 on a block window (pass) and 9 (fail) | as stated |
| S14 | pin: no `GpuClockPin: mode 1` line | NOT_ADMITTED |
| S15 | installed sha ≠ pinned sha | NOT_ADMITTED |

Mutants (`mutlib` v4.1 FULL): window 0–88 / 10–89 / 60–88; arm by `tm8_fill > 0` instead of the `GateArm` text; sign
Δ = M − P; SE instead of 2SE; ship on `upper <= 0`; ignore the vfy121 verdict; ignore the video; ignore `tm8_bad`
windowed only (bad checked in the window, not on all rows); drop the verify-leak check (S2 third case); drop the
arming bands; pairs across non-adjacent blocks; mean of frames instead of mean of block means; keep blocks that did
not reach 88; drop the BDA check; accept `texmemo2=1`; ns treated as µs in the probe report; tolerance ±8 removed /
widened to ±80; median instead of mean.

`vfy121` checker (`vfy121.py`, unsealed but pre-written, with its own fixtures ending `ALL OK`): one fixture per zero
rule (each at positions 3/50/95), per identity (±8 edge), per band edge (`tm8_gain` 599.9/600/2 000/2 000.1, sampler
ratios 1/80, 1/50), `tm8_inject` 0 in a mode-3 block (FAIL: the positive control did not fire) and 1 in a mode-2 block
(FAIL), a `Tm8VerifyMismatch:` line anywhere (FAIL), a missing mode (the 4-arm schedule not realised) ⇒ NOT_EVALUABLE.

### 8.5 Offline unit test (recommended, before the smoke)

A test (e.g. in `resource_tracking_tests`) of the three pure helpers of `renderMemo.h` against a brute-force 8-way LRU on
a random key stream (10⁶ operations, stores and hits, with and without forced renormalisation every 1 000 ticks):
same hit/miss sequence, same victims, no duplicate key in a set, I-T kept, renorm preserves order. Its own mutants
(victim = highest stamp; empty ways not preferred; renorm reversing ranks; mask ignoring `use`) must fail it.

## 9. Risks

1. **The gain may be small or zero** (closure §1.2): `t_hit` of a gained hit is colder than the measured 19.2 ns (its
   entry and image lines were evicted by the direct table, lower bound ≈ 32 ns more [M warm_ns]); emit copies ~584 B
   from a colder entry; the probe (one tag line + mask) and the LRU store on EVERY lookup were under-priced by the
   census (P 43.7 µs = 0.94 ns a lookup [M]; realistic 1–3 ns ⇒ 45–140 µs [I]). Power at −0.15 ms is a coin flip.
2. **Longer residency** raises the exposure named at `:1989-1991` (an answer superseded by a later exact image) and
   may raise `texmemo_stale`. The full-proof hit plus liveness is the same as today's; the verify smoke is exactly the
   check for this; `texmemo_stale` is reported per arm.
3. **`cached` dangling in the verify path:** `FindImage` can reallocate `SlotVector` storage (`slotVector.h:66-68`,
   r1_review §2) — the pointer is re-read (§2.4). Any other pointer kept across `resolve_full` would be a bug.
4. **The refactor into a lambda** must be verbatim; a slip there changes BOTH arms and the texmemo8=0 behaviour. Guard:
   §2.3 neutrality check and the `texmemo8=0` arm of the smoke.
5. **Invariant I-T** has four writers (hit LRU, stale drop, store, verify refill/drop) plus `Invalidate`; a missed
   `use = 0` would leave a valid-looking way over an invalid entry — the probe's `e.valid` term (§2.1) makes that a
   miss, not a wrong hit; the unit test and `tm8_alias` watch it.
6. **Victim eviction resets the victim's `fast_view`** (`tm8_evict_view`): a view recorded for a key evicted by LRU
   is lost exactly as the direct memo loses it on overwrite; fewer conflict misses ⇒ net fewer re-records (predicted
   `texfast_rec` down). If `tm8_evict_view` is large the R term is smaller than 81.1 µs.
7. **Mid-draw layout switch:** stages resolved before the switch re-record via `FindTexture` (version bump) — correct;
   a few µs at block position 0.
8. **Invalidation spike** ≈ 0.1–0.3 ms + ≈ 1.5 ms of refill misses at each flip edge [I] — outside the window, equal in
   both arms; a scorer that forgets the window would charge it to both arms equally in ABBA but inflate the SE.
9. **Clock wrap in long sessions** (≈ 50 min): renormalisation path exercised only by the unit test and a forced wrap
   (optional debug: start the clock at `UINT32_MAX − 10⁶` in the smoke's mode-3 arm — a one-line recorded option).
10. **texmemo2 left stale:** `texture_ways` are never touched under `texmemo8`; texmemo2 is pinned 0 and not a shipping
    path. A future texmemo2 run after texmemo8 sees invalidated entries (valid = false) and refills — correct.
11. **Census numbers are not comparable:** r1cen/r2cen read 0 under `texmemo8`; the s120 scorers must never be run on
    this session's logs.
12. **Scorer traps:** `b_texn`/`tex_hits` live on `FrameTrace-draw:`, `texmemo_*`/`texfast_*`/`tm8_*` on
    `FrameTrace-x:`, `dt_us`/`cpu_gpu_us` on `FrameTrace:` — join by `n=` (r1_review §1); `GateArm` arms and blocks are
    already shifted by the emulator; derived scorers must be checked on a synthetic row with every new field (s105).
13. **Verify-arm side effects** (extra `FindImage` + unconditional DCC adoption on ≈ 2 k hits a frame) make the verify
    arm behave differently from the shipping arm; that is why its numbers are never timings and the video of record
    is the `texmemo8=1` blocks.
14. **Hot-path codegen at 0:** the extra branches and the lambda are paid in both arms, but they also shift the M arm
    against the installed `d3a981a2` build; no claim compares them.
15. **Not claimed, whatever happens:** 60 FPS; the census's 658.8 µs as a speed-up; any R2/A gain; d16 (not in scope
    without a recorded decision and a measured footprint, audit 120 item 1).
