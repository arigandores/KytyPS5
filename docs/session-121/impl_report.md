# Session 121 - implementation workflow report

#### REVIEW 0 PASS
 NB Positive control is tautological by construction (descriptors.cpp:2018-2037, Tm8::Agree). Once real_ok holds, id == slot.image_id. `claim` is slot.image_id with generation^0x80000000, so `id != claim` is always true: TexMemo8Verdict::InjectMissed is unreachable and tm8_inject_miss=0 proves nothing. tm8_inject > 0 at mode 3 proves only that the counter/log path runs and that SlotId's defaulted == compares generation. It does not prove that the Tm8Bad/Tm8CtlBad Add path can fire. CheckRebind's inject (:2075-2086) is the same: when the real placement holds, (index^8)/8 != SetOf(h) by construction. This follows RC2/RC4 as the review wrote them, so it is not a defect against the spec. vfy121/pred text should say plainly that the evidence tm8_bad/tm8_rbbad can fire is the offline unit test (TexMemo8Judge / TexMemo8Placed driven directly), not the in-game control.
 NB Verify mode can EXIT instead of counting (descriptors.cpp:2461-2463). On a gained or sampled hit, resolve_full re-runs the fatal validations: ValidateSampledDepthBinding, the 'depth target cannot be bound as a storage image' EXIT, ValidateStorageColorView, and EXIT_NOT_IMPLEMENTED. A mode-1 hit never runs these. A real memo/fresh divergence of that kind would therefore end the smoke with '--- Error ---' rather than count tm8_bad. The fatal-marker rule in vfy121 should classify a fatal marker inside a mode-2/3 block as a verify FAIL (a divergence found), not NOT_EVALUABLE.
 NB Deviation 6 does not fully cover review recommendation 6 (descriptors.cpp:3511-3520). R2 is turned off only from the state at stage start: the knob value or texture_mode. Suppose the knob flips 0 -> nonzero after that check, and a later ResolveTextureWith in the same stage switches the layout. R2Census then books the stage against 8-way indices, and bad_key / replay are direct-layout constructs. This affects measurement only and changes nothing that executes. Record the rule in ROADMAP/vfy121: never schedule r1cen/r2cen != 0 together with a texmemo8 flip.
 NB tm8_cenoff in PrepareBindings (:3514-3518) also counts when the knob is already 0 but the memo is still laid out 8-way, i.e. before the first resolve after a flip. The must-read-0 rule therefore holds only for runs where r2cen is 0 everywhere (it is in every planned arm). The counter's comment should say so.
 NB The RC6 re-check (:2470-2474) re-tests registered/needs_rebind/depth_id but not info.data/extent. This is correct, because agreement already requires v_store (image->info.data == v_desc.info.data) and an equal R1DescDigest (which covers data and extent) for the same id. Handling a relive failure as a disagreement stores and returns the fresh answer, which is exactly what the miss path would do, so it stays consistent with a fresh resolution.
 NB Checked and correct (no action): (1) invariant use!=0 <=> valid is kept by every writer: the hit LRU (write skipped only when use == clock, which is then the unique global max and so the set MRU), stale drop, store, verify refill (valid=true explicit), verify drop, Invalidate, and renorm inside Tick before the assignment. Find also re-tests e.valid. (2) Every store, eviction, refill, drop and layout switch bumps version and nulls fast_view, so texfast eligibility (:3962-3967) and the ShadowQueue query (:4211-4217) cannot accept a binding from an evicted way or from the other layout. (3) memo_index = set*8+way < 4096. (4) A key cannot occupy two ways: a store happens only after a full-proof probe miss, and resolve_full never touches the memo. (5) texmemo2 precedence: memo2 forces tm8=0, which invalidates any 8-way layout on the first memo2 call. (6) The compute clear shortcut (renderCompute.cpp:195) and null textures/bindpack are unaffected. (7) The RC5 shadow drop at all three sites errs toward more verification. (8) Clock renormalisation keeps stamps unique per set and never 0.
 NB texmemo8=0 equivalence verified independently. A script diff of HEAD 530f6aa's miss-path block against the resolve_full body shows 158/158 lines identical after de-indenting and applying the two declared substitutions ('desc {}' removed, 'const bool store =' -> 'store ='). The only residue is the continuation-line whitespace of the store expression. Every added branch is guarded by tm8 != 0, tm8 >= 2, memo2, or texture_mode (0 at the default). EXIT uses only __FILE__/__LINE__, so failure text is unchanged apart from line numbers. The 64-byte-aligned inline set array under make_shared relies on C++17+ aligned new, which has precedent in this build: R1::Census containing alignas Set<8> via new, and the commandRecorder alignas(64) members.
 NOTES I found no blocking defect in the memo's correctness. Read-only review of `git diff HEAD` in C:/kyty/KytyPS5 (descriptors.cpp, renderMemo.h, the new renderMemo8.h, gates.h/.cpp, frameStats.h, videoOut.cpp) against design121.md, texmemo8_review.md RC1-RC8 and texmemo8.md.

**Can the 8-way memo return an answer the direct memo or a fresh resolution would not?** Only through the same exposure the direct memo already has: a superseded overlap image, or desc drift from FindImage's view/source trim. The 8-way memo simply keeps entries longer, and verify modes 2 and 3 exist for exactly this. A hit still requires:
- a tag-filtered full key proof: valid, the 64-bit resource_key, and the 32-byte T# memcmp;
- the unchanged liveness and data/extent test.

**Checked and correct:**
- Every store, victim eviction, verify refill or drop, stale drop and layout switch bumps `version` and nulls `fast_view`. RebindImages eligibility (:3962-3967) and ShadowQueue (:4211-4217) therefore can never accept a binding from an evicted way or from the other layout.
- `memo_index` stays below 4096.
- `texmemo2` takes precedence: `tm8` is forced to 0, which invalidates.
- `r1cen` is forced off in both ResolveTextureWith and RebindImages; R2 is forced off at stage start.
- Null textures, bindpack and the compute clear shortcut are unaffected.
- The LRU skip-write is exact: `use == clock` implies the way is the global maximum stamp, so it is already the MRU of its set.
- Renormalisation inside Tick runs befor
#### REVIEW 1 PASS_WITH_FIXES
 BLOCK {"file": "C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/descriptors.cpp", "problem": "The timed arm P (texmemo8=1) makes two avoidable out-of-line calls on the lookup hot path. RC7 force-inlined the lambda, but `Tm8::Find` (:1914) and `Tm8::Tick` (:1949) are plain `static` functions, and clang did not inline them. I checked this on the installed build f5331c39 using the linker map and a scan of E8 call targets in both ResolveTextureWith instantiations (RVA 0x811740 and 0x81a3d0). Each one calls `Tm8::Find` at 0x8369d0 (784 bytes) on every lookup whenever tm8 != 0, and calls `Tm8::Tick` at 0x838350 (496 bytes, because TexMemo8Renorm's 512-set loop is inlined into it) from the hit LRU at :2542-2544 and the store at :2599. The call sites are 0x812898/0x81b5ec for Find and 0x81417a/0x8149d7 plus the matching pair in the second instantiation for Tick. The M arm pays neither call. The P arm pays about 46k Find calls and about 45k Tick calls a frame, plus spills of RTW's live registers around each call, so the bias against P is roughly 0.1-0.3 ms a frame. The predicted gain is −0.35 ms, and the power at 0.25 ms is 79–95 %, so this bias alone can turn a real SHIP into NO_SHIP. That would close R1 with a number that belongs to the build, not the mechanism. ROADMAP s121 item 1 allows ONE build, shared by smk121 and shp121, so this must be fixed before the smoke, not after. The census priced the probe inline (P = 0.94 ns a lookup).", "fix": "(1) At descriptors.cpp:1914, write `static inline __attribute__((always_inline)) Probe Find(...)`, and at :1949 write `static inline __attribute__((always_inline)) uint32_t Tick(...)`. (2) In renderMemo8.h, move the wrap branch out of TexMemo8Tick into a cold helper: `__attribute__((noinline, cold)) inline void TexMemo8RenormCold(uint32_t& clock, TexMemo8Set* s, size_t n) { TexMemo8Renorm(s, n); clock = TexMemo8Ways; }`. TexMemo8Tick then becomes `if (clock == UINT32_MAX) [[unlikely]] { TexMemo8RenormCold(clock, sets, count); renormed = true; } return ++clock;`. The unit test builds with clang-cl, so the GNU attribute compiles there too. Leave FindTimed out of line; it then times the inlined probe, which is the same code the P arm runs. (3) After the rebuild, repeat the check used here: scan both RTW instantiations for E8 calls whose target is Tm8::Find or Tm8::Tick; there must be none. Then rerun check_lambda_texmemo8.py, check_gate_order.py and the unit test/mutants, and record the new sha."}
 NB The DCC insurance counter tm8_dcc_chg (descriptors.cpp:2453-2479) can never fire. When `dcc_skip` holds (the image already has kind Dcc at this address), AdoptPendingDccForTexture returns at textureCache.cpp:3185-3186 without touching anything, so the verify arm cannot mask a hit-tail adoption gap in the first place. Report it as a vacuous zero, not as evidence. It also reads Gate::MetaLock a second time within the same operation (tear risk). MetaLock is pinned to 1, so this is harmless.
 NB The verify logic itself is sound for this lens. Every gained hit, plus a non-periodic 1/64 xorshift sample of the other hits (bits 0-5, :2217-2221), runs the full `resolve_full` right after the liveness test and before the hit tail (:2448-2464). `Agree` decides real_ok = store && id == slot.image_id && digest-equal first, and only then looks at the inject (TexMemo8Judge, renderMemo8.h:109-117), so an injected lookup can never hide a real mismatch or refill. Gained hits come from the direct shadow, and the shadow is updated exactly or conservatively at every site (DirectStore RC5 drop at :2001-2012, DirectDrop on stale and on no-store). The relive re-check (:2470-2475) routes a failure into the refill/drop branch and returns the fresh answer.
 NB Known limit, stated so no reader overclaims: mode 2 runs FindImage (TouchImage, ConfigureImageSource) before the hit tail, and it refills the memo on a mismatch. Its memo and texture-cache state therefore diverge from mode 1 (review recommendation 8). The only evidence for mode 1 itself is the texmemo8=1 blocks of smk121 under texfastcheck=1 (valid only together with texfast_bad = 0) and the zero-leak and arming checks of shp121.
 NB The counters are in the right places. Tm8Look/Hit/Miss/Stale are adjacent (frameStats.h:2155-2158), and look = hit + miss + stale holds exactly per call (the miss Add at :2241, look at :2248, hit at :2444, stale at :2572). Gain and Check are adjacent (:2159-2160). Check is booked inside Agree, after resolve_full, so a flip can split one gained hit across two rows. The window residual stays at 1-2, well within the NEAR ±8 tolerance. All 31 rows in videoOut.cpp:2744-2774 follow enum order with micros=false. check_gate_order.py (rerun here) reports GATE ORDER: clean, and TexMemo8 is the last enum entry and the last row.
 NB The timed arm has no per-lookup instrument. At mode 1 there is no RNG, no NowNs and no per-lookup Add: Tm8Alias counts only on a 32-bit tag alias inside Find, and Tm8Fill/Evict/EvictView only on stores. Look/Hit/Miss/Stale/Gain/Check/pb_* are all behind `tm8 >= 2`. The M arm (0) pays one relaxed knob load, one compare against `memo.texture_mode`, and a few never-taken `tm8 != 0` branches; RebindImages adds one `memo->texture_mode` load. resolve_full is inlined at both sites: each RTW instantiation has 5 FindImage calls (3 in the null-texture paths and 2 in the lambda copies), and the map shows no out-of-line lambda operator.
 NB Identities the scorers must use exactly as built. Identity 11 (FAR): tex_hits = tm8_hit − tm8_bad − tm8_vctl_bad − tm8_relive. Identity 1's upper bound gains + tm8_vctl_bad + tm8_relive, because the refill at :2489 counts a fill. The counter is named `tm8_ddiff`; design121 §1.3 calls it `tm8_directdiff`, so vfy121/shp121 should parse `tm8_ddiff` and record the naming difference.
 NB The RC4 positive control (CheckRebind :2059ff, inject = index ^ 8) is rejected by construction, because the wrong set index can never equal TexMemo8SetOf(h) for an entry that is placed. It proves that the counter and log path fire, not that a real misplacement is detected. The unit test's figure '374 of 200000 direct-layout entries also look placed' is the real power statement and belongs in the report.
 NB The switch into 2 or 3 (Tm8::Switch :1990ff) re-assigns the direct shadow on every edge, including 3→2 and 2→3. This is conservative (more hits count as gained right after the edge). Block positions 0-2 lie outside the 10-88 window, so gained/vchk bands are unaffected.
 NOTES This was a read-only review. I edited, built and ran nothing, and committed nothing. I did run two read-only checks: check_gate_order.py (clean) and a Python scan of the installed exe `C:/kyty/build/install/kyty_emulator.exe` (sha256 prefix f5331c39d7452302) against `C:/kyty/build/kyty_emulator_clang_lld_link.map`. The scan looked for E8 call targets inside both ResolveTextureWith instantiations, and it is what found the blocking issue. `Tm8::Find` and `Tm8::Tick` are called out of line on every P-arm lookup and hit. The lambda is correctly inlined.

On the measurement: the verify really does compare every gained hit, and the non-periodic 1/64 sample, against a fresh full resolution taken at lookup time. The real verdict is decided before the injection, an injected lookup never changes state, and a mismatch returns and memoizes the fresh answer. The remaining way for the verify to pass while mode 1 is wrong is the known one: verify-mode side effects (FindImage) make its state diverge from mode 1. The texmemo8=1 smoke blocks under texfastcheck=1, together with texfast_bad = 0, remain the only mode-1 evidence.

Spec files read: `C:/kyty/s121/design/design121.md`, `texmemo8_review.md`, `texmemo8.md`, ROADMAP s121 items 1-2. Diff under review: `git diff HEAD` in `C:/kyty/KytyPS5` (descriptors.cpp, renderMemo.h, the new `renderMemo8.h`, gates.h/.cpp, frameStats.h, videoOut.cpp). Unit output: `C:/kyty/s121/unit/run_tm8_unit.out` (ALL OK, 14/14 mutants killed).
#### blocking 1
#### FIX
**Result: the one blocking finding is FIXED.** Gate order, the lambda identity check, the unit test with all mutants, and the build all come out clean.

**Finding: `Tm8::Find` and `Tm8::Tick` were out-of-line calls on the P arm's hot path — FIXED**

The patch is `C:/kyty/s121/patches/patch_texmemo8_inline.py`. It runs once, after `patch_texmemo8.py`, and follows the house rules: whole-line anchors, each asserted to occur once, line endings kept, `write_bytes`.

1. **descriptors.cpp:** `Tm8::Find` is now `static inline __attribute__((always_inline)) Probe Find(...)`. `Tm8::Tick` is now `static inline __attribute__((always_inline)) uint32_t Tick(...)`. `FindTimed` stays out of line, so it times the inlined probe.
2. **renderMemo8.h:** the wrap branch moved into a cold helper:
   ```cpp
   __attribute__((noinline, cold)) inline void TexMemo8RenormCold(uint32_t& clock, TexMemo8Set* sets, size_t count) noexcept { TexMemo8Renorm(sets, count); clock = TexMemo8Ways; }
   ```
   `TexMemo8Tick` is now `if (clock == UINT32_MAX) [[unlikely]] { TexMemo8RenormCold(...); renormed = true; } return ++clock;`.
3. **Machine-code check:** a new script, `C:/kyty/s121/patches/scan_rtw_calls.py`, reads the map file and the exe and scans both ResolveTextureWith instantiations for direct calls (E8). Result: **PASS**.
   - `Tm8::Find` and `Tm8::Tick` no longer have out-of-line copies anywhere in the map.
   - Neither instantiation (0x811740 and 0x81a820) calls Find, Tick, TexMemo8Tick, TexMemo8Renorm, TexMemo8TagMask or TexMemo8Victim.
   - The Tm8 calls that remain are all on mode ≥ 2, verify or rare paths: FindTimed (1/64 sample), Agree, DirectHolds, DirectStore, DirectDrop, Switch, and the cold `TexMemo8RenormCold` (3 sites per instantiation, wrap only).
4. **Checks rerun:**
   - `check_gate_order.py --src C:/kyty/KytyPS5/src`: "GATE ORDER: clean", exit 0. It also prints the same UNMATCHED heuristic lines as before, which do not affect the result.
   - `check_lambda_texmemo8.py`: PASS (157-line old block, 156-line lambda body).
   - `C:/kyty/s121/unit/run_tm8_unit.py`: baseline PASS and all 14 mutants KILLED, plus the stream-only kills; output ends "ALL OK". The push=1 stream did 999 renormalisations, so the cold path was exercised. I changed mutant 5's anchor to `if (clock == UINT32_MAX) [[unlikely]] {` to match the new header; its mutation is unchanged.

**Non-blocking notes (comments only, no code change)**
- **Tautological positive controls:**
  - In descriptors.cpp, `Agree` and `CheckRebind` now carry comments saying `tm8_inject_miss` and `tm8_rbinject_miss` are zero by construction.
  - The same comments say the evidence that `tm8_bad` / `tm8_rbbad` can fire is the offline unit test, not the in-game control.
- **`tm8_dcc_chg`:** the comment now calls it a vacuous zero. I confirmed that `AdoptPendingDccForTexture` returns at textureCache.cpp:3185-3186 without touching the image when the kind is already Dcc at that address.
- **`tm8_cenoff` / R2 stage-start rule:**
  - The comment now says `tm8_cenoff` reads 0 only when r2cen is 0 everywhere.
  - It also records the rule "never schedule r1cen/r2cen != 0 together with a texmemo8 flip".
  - The frameStats.h block comment now marks these as structural zeros.
- **Not done here, because they are outside source:**
  - Classifying a fatal marker in a mode-2/3 block as a verify FAIL in vfy121.
  - The matching wording in vfy121/pred and the ROADMAP rule.

**Build:** `cmd //c "C:\kyty\build_local.cmd"` exit 0; log in `C:/kyty/s121/patches/build_texmemo8_inline.log`. The patch adds no warnings: the only descriptors.cpp warning is the older `descriptors.cpp(99,1) -Wreturn-type`, which was already in the previous build log. The unit test build gives one getenv deprecation warning from `tm8_unit.cpp`, not from the header. Tail of the log:
```
-- Installing: C:\kyty\build\install/kyty_emulator.exe
-- Up-to-date: C:\kyty\build\install/libwinpthread-1.dll
BUILD OK: C:\kyty\build\install\kyty_emulator.exe
```

**sha256 of `C:/kyty/build/install/kyty_emulator.exe`:** `53bd8820ab7fa2375529fbe045dc9b44d223d94b8355146d7c4d0e77166fa7dd`

Nothing was committed and the game was not run. No emulator or build processes of mine are running, and the temporary unit build was deleted.

Files are in `C:/kyty/s121/patches/`:
- `patch_texmemo8_inline.py`
- `scan_rtw_calls.py`

Files changed by the patch:
- `src/graphics/host_gpu/renderer/renderMemo8.h`
- `src/graphics/host_gpu/renderer/pipeline/descriptors.cpp`
- `src/common/frameStats.h`

Test harness changed: `C:/kyty/s121/unit/run_tm8_unit.py`.
