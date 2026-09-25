# spk118 — pre-seal review (independent, adversarial)

Session 118, route A stage 4 part 2. Reviewed: `spk118.py` (sha at review c7f04d2f…), `test_spk118.py`, `mut_spk118.py`,
`go118a.sh`, `enter_scene.py`, `pred/01_spk118.md`, ROADMAP «СЕССИЯ 118» items 1–3, `designA4_part2.md`, and
`git diff bd0dc57..HEAD -- src/` (HEAD `970e8ce`, src tree clean). The installed exe, the pinned copy and
`build/install` all hash to `8bd4c930…`. Nothing outside `C:/kyty/s118/check_spk118/` was written, except the fixture
directory `fx_spk118` that `test_spk118.py` rewrites on every run. The game was not run and mutlib was not run.

**Verdict: SEAL AFTER FIXES.** Nothing blocks the seal. Two MAJOR findings are about what the pre-registration
discloses; the fixes add disclosure and report-only lines and change no rule. Seven MINOR findings are fixture holes,
record keeping and wording.

## Evidence: the real smoke rewritten into the sealed shape is ADMITTED

`rewrite_smoke.py` builds `root/` from `smoke118b`. It shifts the frame numbers of `FrameTrace*`, `Gate:` and `GateArm:`
lines by +900 (so the schedule starts at 1800), inserts one `GpuClockPin: mode 1` line (the smoke ran unpinned), and
sets the sealed env, `hold_s` 300 and the prereg record. The draft scorer then passes **all 18 admission checks**
(`score_rewritten.json`).
- `Gate:` lines appear only at arm changes. At block 0 only the two non-default names are printed (`slicecen=1`,
  `spine=2`); at every later change all six names are printed. **No `Gate:` line appears at startup.** `gate_lines_ok`
  accepts this pattern.
- 5414 of 5414 rows carry every field of `MAIN_FIELDS`, `DRAW_FIELDS` and `X_FIELDS`, and none repeats a key. There are
  25 complete blocks per arm.
- Leakage between arms, by block index: P blocks carry `carry_skip` at indices 0–1 and M counters (`da_t_n`,
  `bl_stage_n`, `pl_em_n`, `mh_draws`) at index 89. M blocks carry `spine_cmp` (latched plans still finishing) and one
  `k4_w4_n` at index 0. **Kept frames 10–88 are clean in both directions.**
- `el_ops` 99.95 %. K5 PASS; C PASS (15 829 compares, 0 bad); safe (0 uncertain, 0 aborted). K3 median 0.1635 ⇒ W_MAX 8.
  K4 W=2 PASS at 46 ‰ (1973 frames); W=4 FAIL at 317 ‰ (1797 frames). **Consequence W2_CEILING**, as the pred expects.
- None of these results comes from a scorer defect.

## BLOCKER
None.

## MAJOR

**M1. The W=4 verdict depends on how much of the run one scene state takes up, and that is not disclosed.**
- In the smoke, the qualifying W=4 `dep` values fall into two modes: **1287 of 1797 frames (71.6 %) sit at exactly
  317 ‰**, and the rest sit at 88–140 ‰ (89 ‰ in 403 frames).
- Per-block medians switch between the two modes: blocks 0, 7, 8 and 32–40 read ≈ 89 ‰; blocks 3–4, 11–31 and 43–48 read
  317 ‰.
- The modes do not follow the DRS rung (`rt_kpx/rt_att` 2006 against 2009). High-mode frames have about 190 fewer
  elements (5269 against 5460).
- So the median, and with it W2_CEILING or STAGE3, depends on whether the 317-mode takes more than 50 % of the pinned
  300-s hold. The unpinned 180-s smoke cannot predict that share, and the margin is 17 ‰.
- `pred/01_spk118.md:53-55` reports only "~317 ‰ — above the bar" and "expected W2_CEILING".
- W=2 is safe: every value lies in 31–47 ‰.

*Fix (no rule change):*
- State the bimodality and the 72/28 split in the pred.
- Add report-only lines to the scorer: the share of qualifying frames above the bar at W=2 and W=4, and the per-block
  medians (or the per-block count above the bar).
- Name the two modes in the audit's reading of the result.

**M2. The pred says `dep` can only be under-counted; code reading finds ways it can be over-counted, with a 17 ‰ margin.**
`pred:58-65` names only a downward bias (images written through buffers are invisible). There are also ways it can go
up [I]:
- (a) `renderDraw.cpp:1126-1128` records the depth target as *written* on every draw, even though
  `depth.depth_write_enable` exists (`:1019`). A depth buffer bound read-only as an attachment in two adjacent segments
  is counted as a write-crossing, although it needs no transition and no ordering.
- (b) Null descriptors resolve to one shared null image per `NullTextureKey` (`descriptors.cpp:1385-1428`), and a null
  *storage* binding is recorded as written (`descriptors.cpp:2522-2527`). Every pair of segments that both bind a null
  storage slot of the same key therefore counts a spurious dependency.
- (c) `image_id.index` carries no generation, so an image slot freed and reused within a frame merges two images.

Each image moves `dep` by 1000/min(|A|,|B|) ‰, and near 317 ‰ against a 300 ‰ bar one or two images decide the
verdict. This cannot be fixed without a rebuild. *Fix:* disclose it in the pred's Limits, stating that the bias has
both directions and giving the margin.

## MINOR

**m1. The 90 % coverage clause of C can never fire.**
- `SpinePlan` adds exactly one of `CarryCmp`/`CarrySkip` per plan (`graphicsRun.cpp:1613-1643`) and `SpineN` once
  (`:1917`). So `carry_cmp == spine_n − carry_skip` holds identically (the smoke reads 8.0 = 8.0 − 0).
- `spk118.py:318` can reach NOT_EVALUABLE only through `with_pred == 0` or `!safe`.
- This matches ROADMAP item 2's wording, so it is not a scorer defect. Report `carry_skip/spine_n` (the share of broken
  chains) so the audit can see coverage.
- Also: on the graphics queue, the CE→DE compare only tests that CE leaves the registers alone. At `reset_processor`
  submissions, both sides are compared after the reset (`:949-952`, by design per item 3). The number of non-trivial
  cross-submission compares is therefore below `carry_cmp`.

**m2. Four mutants survive the fixtures** (`extra_mutants.py`, run against `test_spk118.py`).
- `k4_n_ge`: `v['k4_w%d_n' % w] == 1` changed to `>= 1` (`spk118.py:328`). This is the real case: the smoke has 90 rows
  with `sc_frames=1, k4_w4_n=2` and summed `dep` (634 ‰ × 61).
- `c_with_pred_ge0`: `with_pred > 0` changed to `>= 0` (equivalent once admitted).
- `cons_close_before_ne` and `cons_close_before_stop`: the consequence order (`:336-345`). No fixture combines K5/C
  NOT_EVALUABLE or FAIL with K4 W=2 FAIL.
- Near-equivalent survivors: `safe_both_arms` and `k5_cmp_both_arms`.

*Add fixtures:*
- 60 % of arm-P rows with `k4_w4_n=2, dep=999`; expect `k4w4_verdict` NOT_EVALUABLE.
- K5 NOT_EVALUABLE together with `k4_w2_dep=301`; expect NOT_EVALUABLE.
- K5 FAIL (or C FAIL) together with `k4_w2_dep=301`; expect STOP_STAGE4.

**m3. Two mutants are killed only by a crash.** `draw_fields` (and very likely `rec_full`) are killed by a `KeyError` in
the report (`spk118.py:348`), not by `block_draw_field_missing` or `block_field_missing`. mutlib will list them as killed
by no named case.

**m4. The pred's fixture count is wrong.** The pred says the suite has 111 fixtures (`pred:18`); the suite prints "112
fixtures" (`report` and `prereg_real` included).

**m5. ROADMAP does not record several rules that exist only in the pred and the scorer.** ROADMAP item 2 lacks:
- K4's 50 % qualification;
- K4 NOT_EVALUABLE (W=2 ⇒ repeat; W=4 ⇒ W2_CEILING);
- the precedence of K5/C FAIL over the safe condition;
- the `smoke118b` disclosure (item 3 records only `smoke118`).

The program's rule is that an unrecorded decision is invalid, so add them as item 4 before the seal.

**m6. The "safe plan" claim is broader than the code.**
- (a) `IsGpuClean` at plan time does not cover a word that a GPU write *earlier in the same submission* dirties before
  execution. The spine then reads the stale value and mispredicts; K5/C would show it, and on a divergent path the
  value-level EXITs become reachable.
- (b) `SpineRegisterPacketSafety` (`graphicsRun.cpp:1331-1339`) pre-checks the header-exact EXITs of CLEAR_STATE,
  NUM_INSTANCES, SET_BASE and DISPATCH_RESET. It does not pre-check those of INDEX_TYPE, INDEX_BUFFER_SIZE and
  INDEX_BASE (`pm4Handlers.cpp:1919-1949`), although the spine calls those handlers (`graphicsRun.cpp:1716-1718`).

The knob is measurement-only and off by default. Record both as residual risk; do not rebuild before this seal.

**m7. The K4 counters split across rows, which the design does not describe.**
- `FinishFrame`'s adds straddle the flip snapshot in about 4.5 % of rows. The smoke has 88 rows with
  `sc_frames=1, k4_w4_n=0`, and 84 of them are followed by `k4_w4_n=2`. `sc_ns` is 0 in the split rows.
- About 9 % of frames lose their W=4 value. The `== 1` filter handles this, and the loss is neutral between the two
  modes (8.4 % against 9.3 %).
- `designA4_part2.md:53` ("a row may carry 0 or 2 frames — the scorer uses `sc_frames`") is incomplete. Disclose.

**Wording only.** The image hook is in `RebindImages` (`descriptors.cpp:2522-2527`), not "PrepareBindings". It sits in
the right place: after the rebind loop `image_id` is final, and the texfast loop below never changes it.

## Answers by question

**1. Scorer against ROADMAP 118 item 2 and the pred**
- K5, C, safe, K3, K4 (median at W=2 and W=4, 50 % qualification) and the order STOP_STAGE4 > NOT_EVALUABLE > CLOSE_A >
  W2_CEILING > STAGE3 all match the pred table and the docstring.
- C's coverage clause cannot fire (m1).
- The `plans > 0` and `el_p > 0` guards and `frame < START` in `gate_lines_ok` are redundant; they are harmless.

**2. Would a real, correct run be ADMITTED?** Yes, as the evidence section shows. There are no failing checks, no scorer
defects, no `Gate:` lines at startup and no leakage into kept frames.

**3. Semantics of the new counters**
- The frame boundary is exact: `AgcSuspendPoint` → `Done()` → `WaitForIdle()` → `m_done_num++`
  (`agc.cpp:1570`, `graphicsRun.cpp:323-336`, `:671-676`). The GuestGpu thread is idle when the number moves, and the
  mutex orders the read.
- `PassBegin` is reached only from the one `BeginRendering` call, inside a draw (`renderDraw.cpp:2835`). Therefore
  `el-1` is the current element, and a restart inside one element is handled correctly (duplicate starts are harmless).
- The last run is closed in `FinishFrame`. Images from other threads are excluded (`IsGpuThread`). At every flip of the
  gate the partial state is discarded (the jump rule).
- Carry: the chain across arm switches is broken correctly (`spine=0` clears `m_spine_carry_valid`; the first P plan
  counts as a skip). Each processor keeps its own chain. The `reset_processor` compare is post-reset on both sides (m1).
  No false-FAIL path was found; the smoke shows 0 bad in 15 829 compares.
- Weak points: image slot reuse (M2c), null or depth over-counts (M2a, M2b), and the K4 row split (m7). In the smoke,
  every kept arm-P row has `sc_frames == 1`, so rows with `sc_frames != 1` are not biasing the medians.

**4. Does the new code change what executes?**
- At knob or gate 0: no. What remains is a gate read, a boolean store, and a `Reset` of the shadow processor at
  `reset_processor` submissions once the shadow exists (shadow only).
- At `spine=2`, `IsGpuClean` takes `TextureCache::m_lock` and advances query epochs. It inflates `tgm_call`/`tgm_hint`,
  so do not compare those counters across arms. Otherwise it only reads.
- At `slicecen=1`: about 2.6 ms a frame (`sc_ns`) on GuestGpu, which lengthens arm-P frames by about 3.8 ms.
- No EXIT is reachable from the safety checks themselves. All indices are bounded; an unmapped indirect table would
  fault, but execution reads the same table.
- No new data race: `m_gpu_modified_ranges` is written only on GuestGpu, and the census state is `thread_local`.

**5. Fixture and mutant coverage, and the chain**
- Coverage holes: m2 and m3. All 116 anchors are unique, and every multi-line anchor matches the LF files.
- `go118a.sh` is identical in structure to the audited `go117a.sh`, with the paths and schedule changed. The schedule
  string equals the scorer's `SCHEDULE`. The lock, `procload`, the idle check, the pinned install with sha checks, the
  stale-artefact move, and the scoring all check out. `enter_scene.py`, `procload.py` and `gates_base.txt` equal the
  s117 copies apart from the paths (`GATES_SHA` verified).

## SEAL AFTER FIXES
1. Pred: disclose the W=4 bimodality (72 %/28 %, block medians 317 ‰/89 ‰, not DRS-driven) and the two-way `dep` biases
   with the 17 ‰ margin (M1, M2); correct the fixture count (m4).
2. Scorer: add report-only lines for the share of frames above the bar at W=2 and W=4, the per-block W=4 medians, and
   `carry_skip/spine_n` (M1, m1). Re-run the suite and the anchor check afterwards.
3. Fixtures: `k4_w4_n=2` rows, K5 NOT_EVALUABLE + K4 W=2 FAIL, K5/C FAIL + K4 W=2 FAIL (m2); regenerate the mutant tally.
4. ROADMAP item 4 before the seal: K4 50 % qualification, K4 NOT_EVALUABLE outcomes, FAIL precedence, `smoke118b`
   disclosure, and the residual safe-plan risks (m5, m6).

Scratch: `rewrite_smoke.py`, `root/` (rewritten log, json, stdout), `score_rewritten.json`, `extra_mutants.py`, `mut/`.
