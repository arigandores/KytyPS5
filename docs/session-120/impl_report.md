# Session 120 - implementation workflow report (agents, build, code reviews, fix)

#### IMPL r1
The R1 census (knob `r1cen`, 0..2, default 0) is fully in the tree, and the build finished with `BUILD OK`. The gate-order check exits 0 and lists `R1Census <-> r1cen` as UNMATCHED; that is only the name heuristic, not a swap. I did not commit and did not run the game.

**Files changed** (tree was clean, so this is the first instrument in):
- `C:/kyty/KytyPS5/src/common/gates.h`: `Knob::R1Census` added after `Spine`; the "LAST row" note moved from `Spine` to it.
- `C:/kyty/KytyPS5/src/common/gates.cpp`: `{"KYTY_R1_CENSUS", "r1cen", 0, 2}` added after the `spine` row; the "LAST row" note moved.
- `C:/kyty/KytyPS5/src/common/frameStats.h`: 64 `Counter` entries after `ScNs`, with a comment block.
- `C:/kyty/KytyPS5/src/graphics/presentation/videoOut.cpp`: 64 rows after `sc_ns`, all `micros = false`.
- `C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/descriptors.cpp`: the census state and helpers after the `bindwit` statics, the `ResolveTextureWith` sites S2/S3/S4/S6, and the `RebindImages` sites S7–S10.

**Patch script:** `C:/kyty/s120/patches/patch_r1cen.py`, one script for all five files, anchored on whole lines with each anchor asserted to occur once, LF kept. It generates the enum entries and print rows from one list, so the two orders cannot differ. Build log: `C:/kyty/s120/patches/build_r1cen.log`.

**New counters, in print order (64):**
r1_hn r1_mn r1_sn r1_hit_ns r1_hit_t r1_miss_ns r1_nost r1_nost_ns r1_rb_ns r1_rb_n r1_rbf_ns r1_rbf_n r1_mp r1_mp_ns r1_w4_q r1_w4_qns r1_w4_p r1_w4_pns r1_w4_lose r1_w4_bad r1_w4_rb r1_w4_rbns r1_w4_pb_ns r1_w8_q r1_w8_qns r1_w8_p r1_w8_pns r1_w8_lose r1_w8_bad r1_w8_rb r1_w8_rbns r1_w8_pb_ns r1_d16_q r1_d16_qns r1_d16_p r1_d16_pns r1_d16_bad r1_d16_rb r1_d16_rbns r1_w1_q r1_w1_qns r1_w1_p r1_w1_pns r1_w1_lose r1_w1_bad r1_w1_rb r1_w1_rbns r1_pb0_ns r1_pb_n r1_am_n r1_ham_ns r1_ham_t r1_sstale r1_cold r1_reset r1_tagx r1_incl r1_xthr r1_self_h_ns r1_self_h_n r1_self_m_ns r1_self_m_n r1_self_s_ns r1_self_s_n

**What is implemented:** everything in `r1.md`, RC2–RC10 of the review, and the recommendations adopted in design120.md §2.
- `alignas(64)` on `Proof` (64 bytes).
- No census work on key-match lookups.
- The richer `R1CenMismatch:` line, capped at 40 lines per process.
- `r1_nost`/`r1_nost_ns`.
- The owner-thread check `r1_xthr`.
- The mandatory w1 null control.
- The probe counters, the per-table re-record time, and post-mode lookups after t1.
- The after-miss counters.
- The self bracket opened before `R1Arm` and split by hit, key miss and stale.
- The fast-branch sample is disabled under `texfastcheck`.

At `r1cen=0` the only added work is the knob load and branches that are never taken. There is no allocation, no thread-local access, no `NowNs` and no `FrameStats::Enabled()` call. Images are read only through `m_slot_images.try_get`.

**Deviations from the spec:**
1. **Census storage:** `t_r1` is a `constinit thread_local R1::Census*`, allocated once with `new` (about 1.9 MB) and never freed. The spec had `thread_local std::unique_ptr`; the pointer avoids a thread-local guard and matches the R2 decision.
2. **w1 counters:** w1 has the full per-table set (q, qns, p, pns, lose, bad, rb, rbns), not only the four RC7 names. All must read 0, as design120 says for any `r1_w1_*`.
3. **Probe timing (RC2):** the timed tag probes are this lookup's real probes, reused for the LRU update, rather than an extra pair of probes whose results are thrown away.
4. **Which desc group differs:** each proof stores a 10-bit fingerprint for each group (info / view / source). So the per-group flags in `R1CenMismatch:` can miss a real difference about once in 1 024. The bad check itself uses the full 64-bit digest, built by combining three XXH3 hashes.
5. **`RebindImages` under `texmemo2`:** the knob is also forced to 0 there, to match `ResolveTextureWith`.
6. **After-miss flag (RC6):** it lives in the census and is read and cleared on every armed level-2 lookup. This is equivalent to "the next R1Begin", since `R1Begin` no longer runs on key-match lookups.
7. **Self bracket:** the part before t0 closes with its own stamp before t0 is taken, so no census arithmetic sits inside [t0, t1].
8. **Not done:** the optional RC4 tightening (count only re-records that recorded a view) and the offline LRU unit test, which design120 did not adopt.
9. **Foreign thread:** if `R1Arm` refuses a thread (`r1_xthr`), that lookup still books the level-1 timers.

**Build:**
```
-- Installing: C:\kyty\build\install/kyty_emulator.exe
BUILD OK: C:\kyty\build\install\kyty_emulator.exe
```
The only warning in a file I touched is at `descriptors.cpp(99)` (`-Wreturn-type`), in code that was already there; my block starts at line 1364.

sha256 of `C:/kyty/build/install/kyty_emulator.exe`: `fb21ddf5f597e89f1a8ea29b1ed1de06dda8b925f5c695614e27e7cbbcfcc34c`

#### IMPL r2
The R2 census (knob `r2cen`) is in the tree and the incremental build finished cleanly with `BUILD OK`. It was only compiled, not run. Nothing was committed, the game was not started, and nothing under `src/graphics/shader/**` was touched. It sits on top of the R1 instrument without reordering it. `check_gate_order.py` exits 0 ("GATE ORDER: clean").

**Files changed** (all under `C:/kyty/KytyPS5/src/`)
- `common/gates.h`: `Knob::R2Census` after `R1Census`; the "LAST row" comment moved to it.
- `common/gates.cpp`: `{"KYTY_R2_CENSUS", "r2cen", 0, 2}` after the `r1cen` row; the "LAST row" comment moved to it.
- `common/frameStats.h`: 44 `Counter` entries after `R1SelfStaleN`, before `Count`.
- `graphics/presentation/videoOut.cpp`: 44 rows after `r1_self_s_n`, all `micros = false`.
- `graphics/host_gpu/renderer/pipeline/descriptors.cpp`, in four places:
  - The census code, placed at the end of the anonymous namespace before `PrepareBindings`:
    - the table: `constinit thread_local R2Table* t_r2`, entries holding a contiguous `std::array<DescriptorValue,64>` of T# words plus per-slot metadata;
    - the full-desc key: `R2DescKey`, `R2KeyStore`, `R2DescDiff`;
    - the helpers `R2Log`, `R2Arm`, `R2Reproduced`, `R2PreLoop` and `R2Census`.
  - The knob read and the pre-loop sampled witness, before `bl_t`.
  - `r2_res_ns` taken from `bl_res`'s own interval, with r2cen's own stamps only when `bindlap` is off.
  - The census call, last in `PrepareBindings`.

**Patch script:** `C:/kyty/s120/patches/patch_r2cen.py`. Build log: `C:/kyty/s120/patches/build_r2cen.log`.

**New counters, in print order (44)**
r2_stg r2_noimg r2_big r2_odd r2_prog r2_rep r2_cl r2_mx r2_cl_ns r2_mx_ns r2_ot_ns r2_cl_sl r2_cl_nul r2_mx_sl r2_mx_eq r2_ot_sl r2_s_cl_ns r2_s_cl_sl r2_s_cl_nul r2_s_mx_ns r2_s_mx_sl r2_s_ot_ns r2_s_ot_sl r2_sl_eq r2_sl_hit r2_cl_lod r2_cl_dcc r2_cl_bc r2_cl_tick r2_cl_meta r2_bad r2_bad_key r2_div r2_nul_ns r2_nul_n r2_wr_ns r2_wr_n r2_wo_ns r2_wo_n r2_st_ns r2_st_n r2_rm_ns r2_rm_sl r2_rm_n

Log lines: `R2Mismatch:` (at most 40), `R2MismatchKey:` (at most 40, from the +1 detector) and `R2Diverge:` (at most 20, information only).

**Deviations from the spec, with reasons**
1. **Free functions instead of a `RenderExecutor` member.** The census is static functions in the anonymous namespace, so `render.h` is untouched. `PrepareBindings` passes in the texture cache's `m_slot_images`, `m_memo.get()`, `MetaEpoch` and `AgeTick`. Behaviour is the same.
2. **The whole census is off under `texmemo2`** (the knob value is forced to 0), as R1 does. The design only skipped the replay. The memo index is then a way index, which would make R and the +1 detector wrong. The base gate file pins `texmemo2=0` anyway.
3. **Sampled-stage counters are a subset, not a split.** `r2_cl_*`, `r2_mx_*` and `r2_ot_*` cover all stages, so the time and slot partitions still add up to `bl_res`. The seven `r2_s_*` counters are the 1/8 sampled subset. The unsampled values for T* are therefore all − sampled: `r2_cl_ns − r2_s_cl_ns`, S_u = `r2_cl_sl − r2_s_cl_sl`, Z_u = `r2_cl_nul − r2_s_cl_nul`.
4. **Dropped counters.** `r2_chk_ns`/`r2_chk_n` are gone, replaced by `r2_wr_*`/`r2_wo_*` and the null pair `r2_nul_*` (C3). `r2_cl_lru` is gone (C6). `r2_rm_n` counts replayed stages (C3).
5. **Three log budgets, not two** (one per tag), because C5 adds the third tag `R2MismatchKey`.
6. **Null flag stored per slot.** It is set from the T# decode at store time, and R uses it for null slots both before and after the loop, so both checks run identical code.
7. **Desc comparison scope.**
   - The group-128 bit also covers the metadata fields the review did not list (control, dcc_clear_word, cmask_clear_words, compression, stencil_compressed, dcc_clear_register_valid), because the review asks for the whole `ImageDesc`.
   - Only the first min(levels, 16) mip entries are stored and compared.
   - Bit 256 (memo index or version differs) is set only on R slots.
   - `R2MismatchKey` lines print `fields=0`.
8. **Reset and sampling.**
   - The table resets only on a gap in `GpuTimeProfiler::Frame()`, as in the design, not on a schedule-block change: with r2cen=1 in both arms nothing in the table depends on the arm.
   - Stages with no images or more than 64 are never sampled.
   - The unreachable `images.size() != n` case goes to `r2_odd`, and to `r2_s_ot_*` if its stage was sampled.

At r2cen=0 the only extra work is the knob load, a few zero-initialised locals, and the never-taken branches. The `r2_res_ns = bl_now − bl_t` subtraction also runs, a register operation the review accepted.

**Build result:** exit code 0; the last lines are:
```
-- Installing: C:\kyty\build\install/kyty_emulator.exe
BUILD OK: C:\kyty\build\install\kyty_emulator.exe
```
The only warning in `descriptors.cpp` is the pre-existing one at line 99, so the patch adds no new warnings.

sha256 of `C:/kyty/build/install/kyty_emulator.exe`: `c62fcea252bd71c5f7dbb112f9ab02bbeb216cba81f99962fc7e56a3c57896eb`

#### IMPL spcen
The spcen part is in the tree and builds cleanly on top of r1cen and r2cen. Nothing was committed and the game was not run. Nothing under `src/graphics/shader/**` was touched.

**Files changed** (all under `C:/kyty/KytyPS5/src`):
- `common/gates.h`, `common/gates.cpp`: `Gate::SamePassCensus` / `{"KYTY_SAME_PASS_CENSUS", "spcen", false}` go after SliceCensus. The "LAST row" comments moved to the new rows. `check_gate_order.py` reports "GATE ORDER: clean" and exits 0.
- `common/frameStats.h`: 52 counters appended after the R2 block, plus `PathLap::MarkSplit` and `PathLap::Running`.
- `graphics/presentation/videoOut.cpp`: 52 rows after `r2_rm_n`, all `micros = false`.
- `graphics/host_gpu/graphicContext.h`: `g_image_state_serial`, `ImageStateSerial()`, `VulkanImage::state_serial`, `NoteStateChange()`.
- `graphics/host_gpu/vma.cpp`: both `CreateImage` backing resets bump the serial.
- `graphics/host_gpu/renderer/image/image.cpp`: `GetBarriers` bumps the serial on a barrier, a resize or clear of `subresource_states`, or a W5 value change.
- `graphics/host_gpu/renderer/context.cpp`: the pass-begin serial moves at every real pass begin.
- `graphics/host_gpu/renderer/render.h`: the per-thread census flags, the census state structs, `CommandBuffer::PassBeginSerial()`, and `m_sp` plus the Sp* members and `friend class SpDrawScope`.
- `graphics/host_gpu/renderer/renderDraw.cpp`: the rare-path flags at S7 and S8, `SpDrawScope`, the A check / post / after-begin, the split marks, and both BeginRendering sites.
- `graphics/host_gpu/renderer/pipeline/descriptors.cpp`: the S14 DCC flag, the B check and post, and the `sp_tr` latch, which also turns on the commit timers. The stage index is only counted when armed.

**Patch scripts:**
- `C:/kyty/s120/patches/patch_spcen.py`: the main patch. It checks every anchor in every file before writing anything.
- `C:/kyty/s120/patches/patch_spcen_b.py`: a follow-up that adds the `depth_load_clear_enable = false` store to the dry replay (review F8).

**New counters, in print order (52):** sp_ser_n, sp_ser_val, sp_rt_n, sp_rt_would, sp_rt_wg, sp_rt_tgt, pl_em_spchk_ns, sp_rt_chkh_ns, pl_em_rt_hit_ns, pl_em_rt_hitg_ns, pl_em_sppost_ns, sp_rt_rep_ns, sp_rt_rep_att, sp_rt_rep_kpx, sp_rt_rec, sp_rt_rec_ns, sp_rt_bad, sp_rt_race, sp_rt_rst, sp_rt_nt, sp_rt_x_memo, sp_rt_x_cfg, sp_rt_x_dclr, sp_rt_x_meta, sp_rt_x_ids, sp_rt_x_live, sp_rt_x_ser, sp_rt_x_bound, sp_rt_x_dsmp, sp_rt_x_pass, sp_tr_n, sp_tr_slots, sp_tr_would, sp_tr_wg, sp_tr_wslots, sp_tr_loop_ns, bl_tr_hit_ns, bl_tr_hitg_ns, sp_tr_chk_ns, sp_tr_chkh_ns, sp_tr_post_ns, sp_tr_rep_ns, sp_tr_rec, sp_tr_rec_ns, sp_tr_bad, sp_tr_dcc, sp_tr_x_big, sp_tr_x_memo, sp_tr_x_meta, sp_tr_x_shape, sp_tr_x_ser, sp_tr_x_flags.

That is the design's 51, minus `sp_tr_race` (removed per RC1), plus the two RC5 record timers. Log lines: `SpCensus: mode 1 …` once, and at most 40 each of `SpRtMismatch:` and `SpTrMismatch:`.

**Deviations from the spec, with reasons:**
1. **Record timer placement.** `sp_rt_rec_ns` and `sp_tr_rec_ns` sit right after their record counts; design120 gives no position for them. `sp_rt_rec_ns` covers the record block of `SpRtPost` (including the should-record decision) plus only the pin block of `SpRtAfterBegin`. The restart/P2 diagnostic is left out because a real memo would not pay it.
2. **P2 when a stamp race was seen.** If the draw's slow path saw a bind_stamp race, a P2 restart is counted as `sp_rt_race`, not `sp_rt_bad`. This is consistent with RC1. Also, nothing is recorded from a raced draw.
3. **One more flag bit in the B slot flags.** Bit 0x100 is set when the backing image is null (an early-return input of `MaterializeDeferredDccClear`). The flags are also `uint16_t` per RC3, and the slot identity carries `meta_kind`, `meta_addr` and the depth-target `image_view`.
4. **B miss reasons for odd cases.** A `try_get` that returns nullptr in the B check counts under `sp_tr_x_ser`. A stage position k ≥ 4 counts under `sp_tr_x_big`. The design gives no reason for either, and this keeps the reason partition exact.
5. **Stricter recording.** The A record is also refused when any target lookup returns nullptr or a colour `target_slot` is out of range; the B record is refused when any slot lookup returns nullptr. The A record uses `try_get` for the sampled-depth test instead of `operator[]`, per RC2.
6. **Fuller A Live check.** Per F7, the Live reason also compares `fast.view_info` and the full rtfast `SameTargetMetadata` against the draw's desc, in addition to the listed terms. The unarmed-draw memo invalidation is also in place.

**One assumption to check in the smoke run.** Bad bit S (and the global-serial variants) relies on the review's claim that every serial writer, including `CreateImage` callers, runs under the render mutex. If some thread creates images outside it, the A and B bad counters would pick up false S bits.

**Build:** `cmd //c "C:\kyty\build_local.cmd"` ends `-- Installing: C:\kyty\build\install/kyty_emulator.exe` / `BUILD OK: C:\kyty\build\install\kyty_emulator.exe`. The build shows no errors. The touched files show the same warnings as the previous build, only on shifted line numbers. The log is at `C:/kyty/s120/patches/build_spcen.log`.

**sha256** of `C:/kyty/build/install/kyty_emulator.exe`: `700eecc5d5c493d194c8f5d3809ef778f4efd469d4c529fa70c0afc9b104b943`

#### BUILD
All four checks passed. `build_local.cmd` didn't need to recompile anything: the binary had already been built from the current sources. I made no fixes and changed no files.

**1. Gate order check** (`python C:/kyty/s96/check_gate_order.py --src C:/kyty/KytyPS5/src`): exit 0, ends with `GATE ORDER: clean`.
- Gate: 113 enum entries and 113 table rows. Knob: 35 enum entries and 35 table rows.
- It also printed many `UNMATCHED (not a swap, check by hand)` lines, for example `entry 111 SliceCensus <-> row KYTY_SLICE_CENSUS / slicecen`, `entry 112 SamePassCensus <-> row KYTY_SAME_PASS_CENSUS / spcen`, `entry 33 R1Census <-> row KYTY_R1_CENSUS / r1cen` and `entry 34 R2Census <-> row KYTY_R2_CENSUS / r2cen`.
- In every one I looked at, the enum name and the table row are the same gate. The script reports no swaps, and the pairing (position 111 is slicecen, 112 is spcen) is consistent.

**2. Build** (`cmd //c "C:\kyty\build_local.cmd"`): exit 0, tail `-- Up-to-date: C:\kyty\build\install/kyty_emulator.exe` then `BUILD OK: C:\kyty\build\install\kyty_emulator.exe`.
- The log has no errors or warnings. Ninja only regenerated `kytyGitVersion.h` and compiled nothing.
- The binary (04:54:23) is newer than the newest changed source files, `render.h` and `renderDraw.cpp` (04:54:03), so it matches the current working tree.
- The full log is in `C:/kyty/s120_build.log`.

**3. Diff stat** (`git -C C:/kyty/KytyPS5 diff --stat`, HEAD `4d4a113`, uncommitted work): 12 files, 2286 insertions, 8 deletions.
```
 3rdparty/nlohmann_json                              |    0   (old submodule state, not this session's work)
 src/common/frameStats.h                             |  214
 src/common/gates.cpp                                |   13
 src/common/gates.h                                  |   31
 src/graphics/host_gpu/graphicContext.h              |   17
 src/graphics/host_gpu/renderer/context.cpp          |    1
 src/graphics/host_gpu/renderer/image/image.cpp      |   19
 src/graphics/host_gpu/renderer/pipeline/descriptors.cpp | 1303
 src/graphics/host_gpu/renderer/render.h             |  113
 src/graphics/host_gpu/renderer/renderDraw.cpp       |  416
 src/graphics/host_gpu/vma.cpp                       |    6
 src/graphics/presentation/videoOut.cpp              |  161
```
Nothing under `src/graphics/shader/**` changed, so the shader translation cache signature is unaffected.

**4. Binary:** `C:/kyty/build/install/kyty_emulator.exe` (24,021,504 bytes, 2026-09-26 04:54:23).
- sha256: `700eecc5d5c493d194c8f5d3809ef778f4efd469d4c529fa70c0afc9b104b943`
- `C:/kyty/build/kyty_emulator.exe` has the same hash.
- It is not yet copied into the emulator folder, and nothing was committed or run.

#### REVIEW r1 PASS
 NB Self bracket carries the RC2 probe instrument (descriptors.cpp:1737-1755 inside the bracket that closes at :1804). On a self-sampled hit, the bracket r1_self_h_ns also contains the six extra NowNs calls and four Adds of the probe timing. Non-self hits never pay these. So r1_self_h_ns / r1_self_h_n over-states the census's per-hit cost, likely by a large factor (the hit census is about 10-15 ns). No design120 formula uses r1_self_* any more: R2 takes T* from the M arm under C2(b). The number feeds only 'R1's share' and the consistency flag. Fix either way: the scorer subtracts (r1_pb0_ns + r1_w4_pb_ns + r1_w8_pb_ns) plus 4 stamp prices from Σ r1_self_h_ns, or it reports that share as an upper bound.
 NB The RC6 after-effect term includes census pollution. Between a stored key miss and the next hit, R1Miss runs: in post mode R1Lookup plus R1Live after t1 (:1839-1848), then R1DescDigest and four table fills (:1849-1888). These touch up to 4 proof lines, 3 tag sets and the candidate image lines. t_ham therefore carries census cache effects that t_hit mostly lacks, and E_T = max(0, t_ham - t_hit)·... is biased upward. That raises C_pt, the side that can produce a false OPEN. The scorer must report E_T separately, as the design already asks. Recommended: state this bias in the prediction, or also report C_T without E_T beside the verdict.
 NB The self count is split three ways (r1_self_h_n / r1_self_m_n / r1_self_s_n, :1804, :1892). The F3 sampler check must therefore use their sum over (r1_hn + r1_mn + r1_sn), expected 1/64. The scorer can also assert the exact identity r1_pb_n == r1_self_h_n on every row: both are Added once per self-sampled hit with c != nullptr.
 NB LRU clock wrap: c.clock is a uint32_t (:1574). Each hit bumps it up to 3 times, about 150 k times a frame, and it is reset only by R1ResetCensus (block change, frame gap, first arm). Under the sealed schedule (period 90) it cannot wrap. In a long run with no schedule it wraps after about 28 k frames. After a wrap, use = 0 marks a live way empty, which shows up as false losses and a nonzero r1_w1_lose. That is a safe NOT_EVALUABLE, not a wrong number. Note it for smokes run without a schedule.
 NB R1CenMismatch group bits (:1512-1514, :1866-1872) are 10-bit fingerprints of the per-group hashes. A group that really differs is reported as equal with probability about 1/1024. This is log-only (the bad decision uses the full 64-bit digest), so it is informational.
 NB RebindImages at r1cen = 0 (:3587-3589) zero-initialises two std::array<uint64_t,4> on the stack at every call (about 9.4 k calls a frame, 64 B each). This is not strictly 'only the knob load and never-taken branches', but it is negligible and paid identically in both arms. Moving the arrays inside an if (r1_time) scope would be cleaner, but it is not needed for the seal.
 NB Cross-instrument: in the P arm the R1 census (about 1-1.6 ms, 1.9 MB of tables) runs in the bindings phase: bl_res via the PrepareBindings loop, bl_img via the RebindImages LapScope, and mh_bind. It is in no span of spcen (pl_em_rt, bl_tr) or of R2 (R2 takes T* from M, and the replay r2_rm has its own stamps and never calls ResolveTextureWith). Two effects remain. (1) R1's cache pollution can inflate P-arm pl_em_rt_ns and bl_tr_us. spcen's Δ_A and Δ_B (M − P) are clamped at 0, so the clamp can hide the inflation and bias N⁺ low. The spc120 scorer should report the unclamped Δ values. (2) R2's P-arm r2_res_ns / r2_cl_* include R1's in-loop work: never mix P-arm R2 class times into T*. C2(b) already forbids this, and the rpk120 fixtures should include a mutant that does it.
 NB The census reads images through try_get without m_lock, before and after the miss path (R1Live :1516-1523). This is the same hazard class as the existing memo-hit path (:2035-2037), not a new one. It is noted only because pre mode reads up to 4 candidate images per key miss where the real path reads one.
 NB Checked and correct, for the record. At r1cen = 0 the only additions are the knob load (:1996, :3581) and never-taken branches, with no TLS, NowNs, Enabled() or allocation. The table order is clean (check_gate_order.py: GATE ORDER clean; Knob R1Census/R2Census and Gate SamePassCensus are last in the same order as their rows). All 64 r1_* enum entries have exactly one FrameTrace-x row, in the same order, micros=false, printed including zeros, and every one is Added somewhere. RC2, RC4, RC5, RC6, RC7 (w1 null control, zero by construction; I traced the stale/!store/cold/reset paths), RC9 and RC10 are all present. So are alignas(64) Proof, no R1Begin work on key-match lookups, the richer R1CenMismatch line, r1_nost/_ns and the r1_xthr owner CAS. The miss path has a single return (:2271), so r1_mn and r1_sn close their identities. memo_index = memo_hash % 4096 = h & 4095, as R1Hit derives it. No Image* or const Image* is kept across calls. No census path calls GetImage/TouchImage/FindImage or writes the memo, the cache or an image.
 NOTES I found no blocking defect in the r1cen implementation. This was a read-only review: I edited, built and ran nothing, apart from the read-only C:/kyty/s96/check_gate_order.py, which reports GATE ORDER clean. The R1 code is in C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/descriptors.cpp, with its counters in src/common/frameStats.h, src/graphics/presentation/videoOut.cpp and src/common/gates.h/.cpp. Current-file line numbers: helpers :1364-1895; ResolveTextureWith :1996, :2019-2033, :2080-2083, :2265-2269; RebindImages :3577-3589, :3606-3608, :3664-3683, :3716-3727.

Findings, point by point:
(1) r1cen=0 leaves behaviour unchanged. memo2 ? 0 : Value(...) is read once. r1_on short-circuits before Enabled(). The RebindImages load happens only when fast. Before t0 the only census reads are the knob, the owner atomic and TLS.
(2) No emulator state changes at any level. Image reads use only m_slot_images.try_get (R1Live). There is no GetImage, TouchImage, FindImage, lock, or write to the memo, the texture cache, an image or LodStats. The only new EXIT-free work is the allocation on the first armed lookup.
(3) Every REQUIRED RC of r1_review.md that belongs in code is present and matches design120 section 2:
 - RC2 probe: r1_w4_pb_ns / r1_w8_pb_ns / r1_pb0_ns / r1_pb_n, on self-sampled hits.
 - RC4: r1_T_rbns for w4/w8/d16/w1.
 - RC5: the post-mode lookup and liveness run after t1.
 - RC6: r1_am_n / r1_ham_ns / r1_ham_t.
 - RC7: the w1 table through the same helpers, all r1_w1_* counters.
 - RC9: the self bracket opens before R1Arm and is split into h/m/s.
 - RC10: !fast_check in r1_fs.
 Every counter the section-2 formulas need exists, is named as specified and is printed raw.
(4) Timer placement is correct:
 - The hit interval runs from the branch to just before emit.
 - The miss interval runs from the branch to just before emit, after the store.
 - The re-record and fast-branch intervals are the same span.
 - Census work sits outside every interval; the one exception is pre-mode warming, which by design is priced from the post half.
(5) Every thread-local is single-owner, the owner check catches any other thread, and the sampling RNG shows no harmful correlation between the self, post and hit draws (checked in GF(2)). r1_T_rb is bounded by Σ(q+p), and the identities F2, F3 and F5 hold by construction.

The nonblocking items are scorer-side guards. The two that matter most for reading the numbers:
 - The probe stamps inflate r1_self_h_ns.
 - E_T carries census cache effects and so leans upward, the direction that can produce a false OPEN.
Interactions with the other two instruments are in the nonblocking list. The main one: R1's cache footprint in the P arm can shift spcen's M−P deltas, and the zero clamp hides this.
#### REVIEW r2 PASS
 NB r2_s_* are SUBSETS of r2_cl_*/r2_mx_*/r2_ot_*, not disjoint classes. For example, descriptors.cpp:2995 adds res_ns to r2_cl_ns unconditionally and :2999 adds it again to r2_s_cl_ns when the stage is sampled. That keeps the partition identity (cl+mx+ot == 1000*bl_res_us) exact. The catch is that design120's T* 'over unsampled clean stages' must be computed as (r2_cl_ns - r2_s_cl_ns) * (S+Z) / ((r2_cl_sl - r2_s_cl_sl) + (r2_cl_nul - r2_s_cl_nul)). The frameStats.h comment ('s_* the same over the 1/8 SAMPLED stages only') is ambiguous. Pre-register the subset semantics in pred/ and add a scorer mutant that treats s_* as disjoint and must FAIL. The review's information line (C3) should divide r2_s_cl_ns by (r2_s_cl_sl + r2_s_cl_nul), not by r2_s_cl_sl alone.
 NB The post-loop cache residual is larger than the r2.md estimate. C5(i) (whole-desc diff incl. 16 mips) makes R2DescDiff read about 600 B of s.key plus the ~584 B fresh desc on every equal-T# slot of every same-program stage. R2KeyStore (:3113) writes about 600 B a slot on every non-clean stage. So the census moves roughly 1.2 KB a slot, about 50 MB a frame, in BOTH arms. It also re-touches the memo lines and image lines that the next repeating call of the same stage type will need. Under C2(b) that warming lowers M's T* (toward a false CLOSE); the pollution raises it. Net sign [U]. The pred should state that the residual C2(b) accepts is now this size, not 'small'. The in-run gauge is the information line r2_cl_ns_u/(S_u+Z_u) - r2_s_cl_ns/(r2_s_cl_sl+r2_s_cl_nul). It prices the same kind of pre-warming, so report it next to the verdict.
 NB Cross-instrument interaction (P arm only): the r2cen=2 replay touches memo lines on sampled clean stages, and the census re-reads memo and image lines after every loop. Both run in P, where R1 measures t_hit / t_T. Warmer memo lines can lower R1's t_hit relative to production and inflate A_T = W_T*(t_T - t_hit), a lean toward OPEN of unknown size. spcen's spans (pl_em_*, bl_tr) sit in emit/CommitBindings, not in PrepareBindings, so no census time lands in them. Mention the R1 interaction in the rpk120 pred as a stated residual; no code change needed.
 NB The R2 census has no owner-thread check. R1 counts r1_xthr; t_r2 (:2812) is silently per-thread. It is correct only with m4baton=0, and only GuestGpu calls PrepareBindings (renderDraw.cpp:2601/2621, renderCompute.cpp:863; shadowresolve does not call it). The scorer must keep asserting m4baton=0 and bindspare=0 per C7. Optional: reuse the R1 owner idiom and add an r2_xthr counter.
 NB R2Arm (:2837) invalidates the whole table when GpuTimeProfiler::Frame() (the presented-flip count) moved by more than 1 since the last armed call. A GuestGpu stall spanning two flips therefore also resets it. The effect is conservative: a few extra non-repeating stages in that frame. Negligible, but it means r2_prog can dip on stall frames. It is not an 'unarmed stretch' in the C2(b) run, where both arms are armed.
 NB r2_cl_dcc (information) evaluates 'settled' on image state AFTER the loop. A slot whose adoption ran inside this very loop therefore reads settled and is not counted, which undercounts first-time adoptions. In steady-state clean repeats the previous call already adopted, so the error is small. It is not a formula term, so it stays information only.
 NB flags[] / meta_addr[] are deliberately uninitialised (C9). They are read only on clean stages, where every slot passed the equal-T# test and was written (:2940-2950 region). That is correct, but clang may emit -Wmaybe-uninitialized / -Wsometimes-uninitialized. If the build uses warnings-as-errors, silence it locally rather than adding {} (a {} value-initialiser would reintroduce the memset C9 removed).
 NB The +1 detector (r2_bad_key, :2954) was re-verified against every texture-memo version write in the tree. Only descriptors.cpp:2090 (stale) and :2260 (store) write it; depthRenderTarget.cpp:314/:332 and descriptors.cpp:3790 are the colour/depth memos. Every legitimate path moves the version by 0 or by at least 2 on the same index, or emits UINT32_MAX. This needs no fix: the detector is sound as implemented under texmemo2=0, which is forced off at :3162.
 NOTES I read the code and did not build, run or edit anything. Scope: knob r2cen in C:/kyty/KytyPS5 (working tree against HEAD), checked against design120.md §3, r2.md and r2_review.md C1–C10. No blocking defects found.

**Value 0** (descriptors.cpp:3157-3177, :3286-3296, :3370): the census adds only what follows. Nothing is allocated, there is no TLS access and no NowNs/Enabled() call, and the image loop is unchanged:
- one Gates::Value load;
- the never-taken `[[unlikely]]` branches;
- the r2_t0 compare;
- `r2_res_ns = 0`;
- one subtraction and store at the head of bl_smp (after bl_now, so outside bl_res).

**No emulator state changes at 1 or 2:**
- All image reads use m_slot_images.try_get (:2850-2863, R2Census).
- The memo is read through m_memo.get() and never through Memo(), so it is never created.
- No GetImage, TouchImage, FindImage, lock or LodStats call.
- The only writes are to t_r2, FrameStats counters and three bounded log budgets.
- No new reachable EXIT. R2PreLoop decodes nothing. DecodeNativeDescriptor runs only on values the loop already decoded. The replay's NullTextureKey takes the same (resource, written ? Storage : Texture) inputs the real null path uses (descriptors.cpp:1918-1924).
- No dangling pointer: only ImageIds are stored, and the program pointer is only compared.

**R is exactly the memo-hit condition** (:2850-2863 against :2008-2037):
- W1 and W2 imply the same resource_key, hash and index.
- `ms.version == s.memo_version && ms.valid && ms.image_id == s.id` (C5 iv).
- The five-field liveness test uses s.key.data/extent, which equal memo_slot.desc on an unchanged version.
- For a null T#, `try_get(s.id)` is equivalent to the bindpack hit test (:1925). The null slot is rewritten only after its image died, and ids carry a generation.
- r2_bad is therefore 0 by construction, and a nonzero value really means the invariant broke.

**The C5 desc diff covers every field:**
- R2DescDiff (:2752) covers every ImageDesc field: info incl. stencil, all of ImageMetadataInfo, htile, pitch, bpb, samples, bgra16, mip_layout up to min(levels,16); view_info; type; source_first_level; source_size.
- It is checked against imageInfo.h and textureCache.h:37-43. All comparison operators exist: GuestRange, ImageMipInfo and ImageSubresources have defaulted `<=>`, cmask_clear_words is a std::array, and ImageViewInfo has its own `==`.
- Bit 256 on memo index/version is present on R slots.
- The +1 detector is present and sound.

**Every required change and adopted recommendation is present:**
- C2(b): mode 1 runs everything except the replay; the replay is gated `mode == 2`.
- C3: the pre-loop sample before bl_t — null pair z0,z1 back to back, then W1+W2(+R) timed [z1,w1] into r2_wr_*/r2_wo_*, plus sampled-stage s_* counters.
- C9: no 2 KiB value-initialised array.
- r2_odd.
- constinit thread_local pointer.
- Contiguous `std::array<DescriptorValue,64>` of T# words.
- Separate log budgets.
- r2_cl_lru dropped; r2_cl_meta kept as information.
- r2_cl_dcc as the information DCC share.
- texmemo2 disarms the census once, before the loop.
- r2_rm_n added.

**Counters:**
- All 44 R2 enum entries match the videoOut rows by name and order, all `micros=false`. Verified by script.
- Every counter the design120 formulas need exists with the specified name: z̄, W, ST, T*, S/Z/L, C_rp, C_ext, and the sanity and correctness terms.
- Timer placement is right:
  - class times are bindlap's own bl_res interval, chosen by counter selection;
  - the witness and null pair sit before bl_t (inside bl_prep, outside bl_res);
  - store and replay are after the loop, with every Add outside its span;
  - each sampled span carries exactly one NowNs-call overhead, which z̄ cancels.
- Identities the scorer can test hold per call:
  - `cl_ns + mx_ns + ot_ns == 1000*bl_res_us`;
  - `cl_sl + cl_nul + mx_sl + ot_sl == bl_res_n`;
  - `rep == cl + mx`;
  - `wr_n + wo_n == nul_n`;
  - in P, `rm_sl == s_cl_sl + s_cl_nul`.

**Tables:**
- Knob enum: Spine, R1Census, R2Census, matching KNOB_DEFINITIONS spine, r1cen, r2cen.
- Gate enum: SliceCensus, SamePassCensus, matching slicecen, spcen.
- The LAST comments were moved.
- Read-once is respected: r2 and TexMemo2 are read once each, and MetaLock is read for information only.

**Threading:** GuestGpu under the render mutex only; per-thread RNG never zero.

**Interactions with the other two instruments:** spcen's always-on image state serials and pass serial are in both arms and negligible here. R1 and spcen spans contain no R2 time. The cache interactions are listed under nonblocking.

The nonblocking items are about writing things down (s_* subset semantics, the residual's size, the R1 interaction) and optional hardening (owner-thread check). The lead should run check_gate_order.py before the build, as design120 requires; I verified the order by hand.
#### REVIEW spcen PASS_WITH_FIXES
 BLOCK {"file": "C:/kyty/s120/design/design120.md", "line": 0, "problem": "The spcen code is correct, but section 4's upper bound N+ counts the census's own timer reads as memo cost, so N+ comes out low. Each rdtsc NowNs read costs one latency z (about 5-9 ns) that a real memo never pays, and the subtracted spans carry extra reads: pl_em_spchk_ns has one extra PathLap mark per armed draw (renderDraw.cpp:2828; in M that read sits in pl_em_rt). sp_rt_rec_ns has one pair per armed draw (renderDraw.cpp:1148/1204) plus one per pin (renderDraw.cpp:1242). sp_rt_rep_ns has one pair per would-hit. sp_tr_chk_ns has one per stage (descriptors.cpp:5024 lap to the check-end NowNs), and sp_tr_rec_ns and sp_tr_rep_ns one each (descriptors.cpp:4656, 4609). The gross terms pl_em_rt_hit_ns and bl_tr_hit_ns include only one latency per would-hit. Net bias is about -z*(2*sp_rt_n + sp_rt_rec + 2*sp_tr_n): at about 5 000 draws and 9 200 stages a frame that is roughly 0.15-0.3 ms. The pre-check cb_lap(cb_transit) at descriptors.cpp:5024 also adds one extra latency per stage to bl_tr_us(P), which pulls Delta_B toward 0. N+ drives CLOSED (the permanent 'exhausted' record) against a 0.5 ms threshold, so a biased N+ can give a wrong CLOSED.", "fix": "Before the scorer is sealed, record in ROADMAP/design120 that an in-run null pair zbar = sum r2_nul_ns / sum r2_nul_n (P arm; r2cen>=1 in both arms, and R2PreLoop takes two back-to-back NowNs on the same GuestGpu thread) is added back. N+ = N + zbar*(2*sp_rt_n + sp_rt_rec + 2*sp_tr_n) + Delta_A*pl_em_rt_hit_ns/pl_em_rt_ns + Delta_B'*bl_tr_hit_ns/sp_tr_loop_ns, where Delta_B' = max(0, 1000*(bl_tr_us(M) - bl_tr_us(P)) + zbar*sp_tr_n(P)). Keep N as the lean-low point. Report zbar, and add a mutant that drops the add-back. Code alternative: add an spcen-owned null pair counter (sp_nul_ns/sp_nul_n, one NowNs pair per armed draw) and use it instead of r2_nul."}
 BLOCK {"file": "C:/kyty/s120/design/spcen.md", "line": 0, "problem": "Fixture 4 in section 11 ('sp_rt_n = sp_rt_would + sum of 10 x' and 'sp_tr_n = sp_tr_would + sum of 6 x', exact per frame, a one-off skew must FAIL) and the per-frame nesting fixtures in fixture 5 cannot hold on real rows. FrameTrace-x reads each counter separately (FS::Read, frameStats.cpp:214, one registry-locked sum per counter, in print order videoOut.cpp:2692-2743) while GuestGpu keeps adding. A draw whose SpRtDraws Add lands between the read of sp_rt_n and the read of its reason counter moves one count between adjacent lines. The same applies to sp_rt_wg vs sp_rt_would, bl_tr_hit_ns vs sp_tr_loop_ns (sp_tr_loop_ns is printed first), and sp_tr_wslots vs sp_tr_slots. With about 170 new reads in the line and draws about 6 us apart this happens on a large share of frames (the s116 precedent is row skew up to +-60). An exact per-frame test would make the sealed run NOT_EVALUABLE or FAIL for no reason.", "fix": "The scorer tests the partitions and nestings on window sums (frames 10-88 of each block) with a tolerance of +-1 count per block boundary (+-2 per block window), or per line with +-1 on counts and +-one stage's or draw's span on ns. Change fixture 4 so that a +-1 skew between adjacent lines that cancels over the window is ADMITTED, and a persistent off-by-one (the mutant 'reason index shifted') still FAILs. The 'M-arm zeros on window frames only' rule stays as RC6."}
 NB Race decided per slow-path entry: renderDraw.cpp:839-842 ORs stamp != fast.stamp on EVERY slow-path entry of the draw. If target 0 takes the slow path through a predicate hole (stamp unmoved), its FindRenderTarget can Untrack or refresh an aliasing target j and bump j's bind_stamp (textureCache.cpp:590/607/626). Target j's later slow-path entry then sets race, so the hole books as sp_rt_race instead of sp_rt_bad. The 1e-4 rule usually turns that into NOT_EVALUABLE rather than a false pass. Recommended: `if (!t_sp_rt_slow) t_sp_rt_stamp_race = stamp != fast.stamp; t_sp_rt_slow = true;` so only the first slow entry decides, before any Find of this draw has run.
 NB sp_rt_rec_ns also includes the pin time from SpRtAfterBegin (renderDraw.cpp:1233-1243), which sits in the pl_em_com/rec span, not in pl_em_sppost_ns. The RC5 nesting fixture must read sp_rt_rec_ns <= pl_em_sppost_ns + (pin share). There is no separate pin count or ns, so check the inequality on window sums; it holds by a wide margin. Optional: a separate sp_rt_pin_ns counter.
 NB The value-0 path is not byte-identical to d3a981a2, by design (always counted, both arms): GetBarriers adds a 4-field compare, NoteStateChange and an Add (image.cpp:230-243); CreateImage bumps the serial (vma.cpp:401-403, 455-457); every real pass begin does a relaxed fetch_add (context.cpp:332); VulkanImage grows 104->112 B and RenderExecutor gains a unique_ptr. At spcen=0 the per-draw extras are: SpDrawScope's null test of m_sp (renderDraw.cpp:881-900), two Armed() tests around each BeginRendering, the sp_tr null test, and a zero-initialised SpTrStage plus one uint64 copy per stage in CommitBindings. There is no allocation, no NowNs and no FrameStats::Enabled() at 0: the gate is read first and short-circuits. The TLS flags are read only on the rtfast slow path, the dead re-find and a non-zero DCC mask. Report the prices against d3a981a2 as disclosed.
 NB Once m_sp exists, every unarmed (M-arm) draw does six stores to invalidate the memos (F7, renderDraw.cpp:884-893). This is correct and required, and it is a tiny M-only cost inside the P-M price.
 NB The B memo is keyed by stage position k (sp_next_stage, descriptors.cpp:4965-4966) and not by program.stage. The transit loop's depth-feedback EXIT reads program.stage == Pixel. The census never skips the loop, so this does not affect soundness here, but a real B memo would need stage type in its key (position 1 is HS in tessellated draws and PS otherwise).
 NB SpRtConfigOk reads the rtfast and slicecen gates twice per armed draw (check at renderDraw.cpp:~977 and rec_ok at ~1149). These are not the census gate and both are pinned by gates_base.txt, so there is no tear risk in the sealed run.
 NB Checked and holding: RC1 (bit M 0x80 for A and 0x10 for B; race only from t_sp_rt_stamp_race; sp_tr_race removed and absent from enum and print rows). RC2 (every census image read goes through m_slot_images.try_get; SlotVector::try_get is pure, deque-backed and address-stable; the R1/R2 diff adds no GetImage/TouchImage/FindImage either). RC3 (uint16 flags plus meta_kind/meta_addr, and backing.image==nullptr in the flags). RC5(a) timers present. F7 (full rtfast predicate restated at renderDraw.cpp:~1004-1015 including meta_epoch, source_*, view_info, SameTargetMetadata, htile and stencil, plus invalidation on unarmed draws). F8 (re-lookup in SpRtPost with nullptr => bit I; P2 invalidates the pending memo and is bad only when pass_before == m.pass_serial; image_view in the slot identity for depth targets; sink.depth_load_clear; the 104->112 B comment). Reason enums span 9 and 5 with static_asserts; the reason index is SpRtMissMemo + why - kSpRtMemo, so there is no off-by-one. Array bounds are guarded (slot < MAX before m_color_view_fast[slot]; k < tr.size(); n <= 32). No new EXIT. No stale Image* is dereferenced across AcquireRenderTargets. All 52 spcen rows print with micros=false in enum order after the R1/R2 blocks. The gate row comes after slicecen in both enum and DEFINITIONS (check_gate_order.py: GATE ORDER clean, 113/113). spcen is read once per draw and latched; CommitBindings and both BeginRendering sites read only the latch; the bl_tr split (lap before the check, cb_t re-based after the check and after the post) keeps bl_tr = prologue + GDS + loop.
 NOTES Read-only review of the working tree C:/kyty/KytyPS5 against design120.md section 4, spcen.md and spcen_review.md RC1-RC6. Nothing was edited, built, run or committed; the only thing run was the read-only C:/kyty/s96/check_gate_order.py.

The spcen code in the tree (renderDraw.cpp:835-1244, 2819-2854, 3076-3083, 3244-3251; descriptors.cpp:4460-4657, 4795-4800, 4964-4966, 5021-5117; render.h; frameStats.h:2085-2140, 2576-2591; videoOut.cpp:2691-2743; image.cpp:136-243; vma.cpp; context.cpp:332; gates.h/gates.cpp) implements every REQUIRED change and every adopted recommendation. Every counter the section 4 formulas need exists (pl_em_rt_hit_ns, pl_em_spchk_ns, sp_rt_rep_ns, sp_rt_rec_ns, bl_tr_hit_ns, sp_tr_chk_ns, sp_tr_rep_ns, sp_tr_rec_ns, sp_tr_loop_ns, sp_rt_bad, sp_tr_bad, sp_rt_race, sp_rt_would). Each is in the right span and prints raw.

Value 0 matches the design. The only additions are the always-on serials the design declares, the latch tests and never-taken rare-path TLS tests; there is no allocation, NowNs or Enabled() at 0.

No census path changes emulator state. Reads go through try_get only, Image* pointers are re-looked up after AcquireRenderTargets, there is no new EXIT, and no call touches the LRU.

Neither blocking item is a code defect. Both are scorer/spec problems that would make the sealed verdict wrong or unreadable, and both must be settled before the scorer (spc120.py) is sealed:
(1) N+ is not an honest upper bound. The census's own timer reads are subtracted as if they were memo costs, biasing it about 0.15-0.3 ms low, and the extra pre-check lap also pulls Delta_B down. Fix: add back zbar from the in-run null pair r2_nul_ns/r2_nul_n, or add an spcen null pair.
(2) The reason-partition and nesting identities cannot be exact per frame, because the flip reads counters one at a time while GuestGpu adds. Fix: test on window sums or with a +-1 tolerance.

No interaction with r1cen/r2cen breaks spcen. R1/R2 work sits in the bindings half before the check, and their diff adds no GetImage/TouchImage/FindImage/state writes. cbmove and slicecen must stay off (both absent from the arms), as the gate comment says.
#### blocking_count 2
#### FIX
Both findings are FIXED. They were spec defects, not code defects, so I corrected the spec and left the emulator source alone. The gate-order check and the build are clean.

**Finding 1 (spcen, N⁺ counts the census's own timer reads): FIXED in `design120.md` §4.**
- **Claim checked in the source first.** Each of these is paid on every armed draw or stage, with no early return before it:
  - the extra mark after the check (`MarkSplit(PathEmSpChkNs…)`);
  - the `rec0` pair in `SpRtPost` (`renderDraw.cpp:1148/1204`) and the one per pin in `SpRtAfterBegin` (`:1242`);
  - the pre-check `cb_lap(cb_transit)` into the `sp_tr_chk_ns` read (`descriptors.cpp:5024-5027`);
  - the `sp_tr_rec_ns` pair (`:4612/4656`).
  
  The replay pairs and the gross hit spans each carry one read per would-hit, so they cancel. The net bias is −z·(2·sp_rt_n + sp_rt_rec + 2·sp_tr_n), as the review said. The pre-check lap also adds one read per stage to `bl_tr_us(P)`.
- **New rule block (it replaces the old N⁺ line):**
  - z̄ = Σ r2_nul_ns / Σ r2_nul_n, from the P arm's window frames. P runs `r2cen=2`, and `R2PreLoop` takes two back-to-back `NowNs` on the GuestGpu thread (`descriptors.cpp:2881-2898`). If Σ r2_nul_n = 0 or z̄ ≤ 0 ⇒ NOT_EVALUABLE.
  - Z = z̄·(2·sp_rt_n + sp_rt_rec + 2·sp_tr_n)
  - Δ_B′ = max(0, 1000·(bl_tr_us(M) − bl_tr_us(P)) + z̄·sp_tr_n(P))
  - N⁺ = N + Z + Δ_A·pl_em_rt_hit_ns/pl_em_rt_ns + Δ_B′·bl_tr_hit_ns/sp_tr_loop_ns
- **Unchanged:** N stays the lean-low point that OPEN uses.
- **New reporting and mutants:** the scorer reports z̄, Z and Δ_B′. Two new mutants: one drops Z, one uses Δ_B where Δ_B′ is due.
- **Code alternative not taken** (`sp_nul_ns`/`sp_nul_n`): `r2cen` is armed in both arms, so `r2_nul` is already an in-run null pair on the same thread.

**Finding 2 (spcen fixtures 4/5 cannot hold exactly per frame): FIXED in `spcen.md` §11, with a "Row skew" rule in `design120.md` §4.**
- Partitions and nestings are now tested on window sums, frames 10–88 of each block.
- Counts must match within ±2 per block window (±1 per edge).
- ns nestings must match within the subset counter's own values on the window's two edge lines.
- A ±1 skew between adjacent lines that cancels over the window is ADMITTED. A persistent off-by-one on every line still FAILs.
- New mutant: "partitions/nestings tested exact per frame".
- RC6 (M-arm zeros on window frames only) is unchanged.

**Files changed** (docs only; both copies are byte-identical, LF kept):
- `C:/kyty/s120/design/design120.md` and `C:/kyty/KytyPS5/docs/session-120/design120.md`
- `C:/kyty/s120/design/spcen.md` and `C:/kyty/KytyPS5/docs/session-120/design/spcen.md`

I did not add this decision to `ROADMAP.md`; it is recorded only in `design120.md`, which ROADMAP s120 item 4 points to.

**Patch script:** `C:/kyty/s120/patches/patch_review_docs.py` (whole-line anchors, each count asserted to be 1, original line endings restored, `write_bytes`).

**New counters:** none. The print order is unchanged: the r1 block, then the r2 block, then the sp block ending with `sp_tr_x_flags`.

**Deviations from the spec:** none. Of the options the review offered, I took the spec-record fix rather than the code alternative.

**Gate-order check:** `check_gate_order.py` printed `GATE ORDER: clean`, exit 0. It also listed many "UNMATCHED … check by hand" lines; they are informational name-match lines, and most are for gates that predate session 120.

**Build:** `build_local.cmd` exit 0, ending with `BUILD OK: C:\kyty\build\install\kyty_emulator.exe` and 0 warnings or errors in `C:/kyty/s120/patches/build_review.log`. Nothing recompiled because no source changed.

sha256 of `C:/kyty/build/install/kyty_emulator.exe`: `700eecc5d5c493d194c8f5d3809ef778f4efd469d4c529fa70c0afc9b104b943`
