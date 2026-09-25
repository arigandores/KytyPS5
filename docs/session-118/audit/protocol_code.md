# Audit 118: protocol and code (adversarial)

This audit only read files. It did not run the game or build anything, and it changed no existing file. Logs were read
in Python binary mode. Scope: ROADMAP §0.1 "СЕССИЯ 118" items 1–5 (`docs/ROADMAP.md:2304-2399`),
`docs/next-session-118.md`, `docs/session-118/designA4_part2.md`, `docs/session-118/check/PRESEAL.md`, and commits
f62d537..a8c856c. The harness is `C:/kyty/s118`. For the code, the census fix `7bc87cd` and the instruments `14f08b2`
and `970e8ce` were read in full, along with the code around them.

## Check 1: protocol

### Timeline (git dates, file mtimes, json and chain log; all times +0200)

| time | event | evidence |
|---|---|---|
| 21:47:33 / 21:51:21 | item 1; item 2 + design (K4 on `dep`, 300 ‰ bar, consequences incl. W2_CEILING "f = 0,5") | f62d537, bd0dc57 |
| 21:57:20 | instruments | 14f08b2 (build c41290d0, build118.log 21:56:45) |
| ~21:58–22:01:15 | smoke118 (carry defect) | old/smokes/smoke118.json |
| 22:02:19 → 22:02:47 | item 3 recorded, then shadow-reset fix + build 8bd4c930 | aad6f6b, 970e8ce, build118c.log |
| ~22:03–22:06:43 | smoke118b (W=4 317 ‰) | smoke118b.json |
| 22:47:47 | pre-seal report | check_spk118/PRESEAL.md |
| **22:49:26** | **item 4 recorded (census fix + disclosure)** | 968ff0a |
| 22:49:42 / **22:49:44** | fix script / the four sources patched (all mtimes 22:49:44.58–.59, none later) | patch_census_fix118.py, `ls` of src |
| 22:50:00 | build 321175ab; ninja recompiled graphicsRun, renderDraw and descriptors (build118d.log [8–10/14]), so the build started after the edit | build118d.log, build/install exe = 321175ab |
| 22:51:32 | commit of the fix | 7bc87cd |
| ~22:52:30–22:55:41 | smoke118c (build 321175ab) | smoke118c.json (hold 180.1 s, start 10.8 s) |
| 22:53:57–59 | scorer, test and mut patched (item-4 report lines), during the smoke but before its data | patch_spk118_item4.py, spk118.py mtimes |
| 22:54–23:02:52 | draft mutants (work_mut118 pyc 22:54…23:02; draft2 125/125) — **overlap with smoke118c 22:54–22:55:41** | work_mut118/__pycache__, mut_spk118.draft2.out.txt |
| 23:03:45 / 23:03:50 | pred final / chain final | pred mtime == ctime (spk118.json `mtime_ctime_delta_s 0.0`) |
| 23:04:18–23:05:02 | sealed mutlib v4.1 tally, 125/125, controls 3/3, wall 44.0 s | mut_spk118.out.txt |
| 23:05:10 | SEALS118.txt + commit of the seal copies | 201ca03 |
| 23:05:13 → 23:05:49 → 23:11:19 | chain requested → emulator start → verdict ADMITTED / W2_CEILING | go118a.log |
| 23:13:03 / 23:14:10 | item 5 / next-session-119.md | a8c856c, file mtime |

- **CONFIRMED: item 4 was recorded before the fix, the fix came before the seal, and the seal and tally came before
  the run.** Every sha in SEALS118.txt matches the file on disk now (pred `fe65225a…`, scorer `6fa60aad…`, test, mut,
  chain, gates, procload, enter_scene, launch_run, run_safety99, exe `321175ab…`, mutlib `db82ef4b…`, tally
  `6df4798e…`). The `docs/session-118/seal01/` copies in 201ca03 match byte for byte, and so does the chain log in
  a8c856c. `enter_scene` recorded the pred sha as `fe65225a…` before launch. **The pred did not change after the seal.**
- **CONFIRMED: no heavy work during the sealed run.** Between 23:05:30 and 23:11:20, the only files written under
  `C:/kyty` were the run's own artefacts (`gates.req`, `sample.req`, log, stdout, gpuclk, json, score, go118a.log). The
  other writes in that window were the emulator's own outputs in the game folder (`_kyty.txt`, `_run_stdout.txt`,
  `_PipelineCache`). No git object or index was written until 23:13:03. One write falls just before the run:
  `C:/kyty/LOOP_STATE.md` at 23:05:23.9, a text line written during the chain's first `procload` window, before the
  23:05:49 launch. It is trivial.
- **CONFIRMED: the pre-registration discloses honestly that the fix followed the smoke.** It states in bold "The census
  fix was made AFTER this smoke showed W = 4 at the bar; it could move the outcome either way" (`pred/01_spk118.md:63-64`),
  and ROADMAP 118 item 4 says the same (`ROADMAP.md:2359-2361`). The fix follows the recorded design ("written =
  storage / targets", `designA4_part2.md` §3). It also moved the result away from the favourable verdict: W=4 went from
  317 to 325 ‰. I recounted from the logs (sc_frames = 1, k4_w4_n = 1):
  - smoke118b: W=4 317 ‰, 70.9 % of frames above the bar;
  - smoke118c: W=4 325 ‰, 72.8 % above; W=2 47 ‰; census image records −2.2 %;
  - spk118: W=4 325 ‰, W=2 47 ‰.

  The smoke118c numbers match the pred.
- **CONFIRMED (disclosed): smoke118c ran while the draft mutants were running.** The pred says so (`:65`). The overlap
  is about 1.5 min at the end of the smoke. Its numbers are counts, not timings, and decide nothing.
- **CONFIRMED: the consequence was applied as sealed.** The pred table row (`:45`) gives K4 W=2 PASS (47 ‰, 0.0 % of
  frames above the bar) and W=4 FAIL (median 325 ‰), which is **W2_CEILING**. W=4 was evaluable on 3 008 of 3 239 kept
  frames (≥ 50 %). Every level quoted in item 5 matches `runs118/spk118.score.txt`:
  - K5 / C / safe: 0 bad, 25 904 plans;
  - spine: `spine_cmp` 5 308.8 of 5 308.9; `spine_ns` 958.8 µs;
  - blocks: 33 blocks at 325 ‰ and 8 at 90 ‰;
  - arm M: 1 211 / 653 / 462 / 4 235 / 3 868 / 3 213 / 1 095 / 10 969 / 6 662 / 7 426 (2 376 / 1 565 / 1 363 / 1 226 /
    745); `bda_scan` 57.6.
- **CONFIRMED: item 5 does not set aside the sealed consequence.** The sealed row fixes two things: W = 2 is the
  ceiling, and the best case is recomputed with f = 0,5 before stage 3 resumes. Both were done: G₂ ∈ [3 026; 5 558] µs,
  and the arithmetic checks (X = 9 300/0.7 = 13 286; 0.5·X − 1 085 = 5 558; minus T4 2 532 = 3 026). The seal names no
  rule to apply to the recomputed number. Adding one sealed re-measure before stage 3 is a new decision, not a reversal.
  It was recorded before any action (23:13:03, before next-session-119.md at 23:14:10). It delays stage 3; it does not
  cancel it, and no CLOSE_A is claimed.

### Findings

- **MAJOR P1: the recompute in item 5 and the G₂ rule for session 119 use f = 0.5, although the same sealed run measured
  the realized 2-way split at 0.555.**
  - Item 5 derives f = max(f_max, 1/W) = 0.5 "because K3's largest run 0.16 < 0.5" (`ROADMAP.md:2383-2384`).
  - The census defines `fmax` as the largest segment's share when the frame is cut at pass starts
    (`designA4_part2.md` §3; `graphicsRun.cpp:1481-1491`). The sealed score prints **`fmax median 555`** at W = 2
    (`runs118/spk118.score.txt`, K4 W=2 line).
  - At W = 4 the same census gives `fmax` 300. That is exactly the 0.30 the session-104 stage-1 rule used instead of 1/W
    (`ROADMAP.md:617-618`). So the precedent charged the realized largest piece, not the ideal share.
  - With f = 0.555: G₂ = 0.445·13 286 − 1 085 − T₂ = 4 827 − T₂. The conservative end (T₂ = T4) is **≈ 2 295 µs, below
    the 3 000 bar**.
  - The claim that the conservative end "clears the bar by 26 µs" (item 5; `next-session-119.md` intro) holds only for
    the ideal f. The session-119 rule hard-codes 0.5 (`ROADMAP.md:2393`; `next-session-119.md` step 1), which builds in
    an optimistic bias of about 730 µs. That is about 28 times the margin the decision is about.
  - This does not break the seal: the best case at 0.5 stays correct as a best case. But the next decision inherits the
    bias.
  - *Fix, in ROADMAP before session 119's seal:* state which f the G₂ < 3 000 rule uses. Propose the measured
    `k4_w2_fmax`, with the f = 0.5 best case also reported. Alternatively, record why 0.5.
- **MINOR P2: choosing to re-measure rather than apply the standing stage-1 rule (G ≥ 3 000 ⇒ continue) at the
  conservative end is discretion exercised after the outcome.** It was recorded before acting and it is the cautious
  direction. The record does not say whether a 26 µs miss would also have been re-measured rather than closed. Given P1,
  this question is moot.
- **MINOR P3: a C PASS of "8 of 8 plans a frame" is thinner evidence than it reads.**
  - After a `reset_processor` submission, both sides are compared after the reset (`graphicsRun.cpp:949-951`,
    `:1613-1644`). smoke118's "one mismatch a frame" implies about 1 of the 8 compares a frame is trivially equal.
  - On the graphics queue, the CE→DE compare only tests that CE leaves the registers alone (PRESEAL m1).
  - The carry was tested on GuestGpu between consecutive plans, not on the walker thread the plan asked for
    (`next-session-118.md` step 1). Item 2 changed this before the code, and pred Limits discloses it.
  - Item 5 does not quantify the non-trivial compares.
- **MINOR P4: the build count and a departure from the pre-seal recommendation.** Item 1 says "ONE build", but there
  were three (c41290d0, 8bd4c930, 321175ab). The pre-seal agent recommended only disclosing M2 ("cannot be fixed
  without a rebuild"). Items 3 and 4 recorded each rebuild before it happened, and only one build ran sealed. Protocol
  holds.
- **MINOR P5: the installed exe is now `321175ab`** (game folder, 23:05:26), while CLAUDE.md says `d3a981a2`. Item 5(3)
  schedules the reinstall. After it, re-scoring `spk118` will fail `installed_now`, as in session 117. The score is
  archived in a8c856c.

## Check 2: code (7bc87cd, 14f08b2, 970e8ce)

- **CONFIRMED: the RebindImages hook indexes correctly.** The hook is in `RebindImages`, not `PrepareBindings`
  (`descriptors.cpp:2522-2532`); the pre-seal review noted this as wording only.
  - `snapshot` is `prepared.runtime->resources` (`:2493`). `PrepareBindings` sets `prepared.runtime = &runtime`
    (`:2143`) in the same draw/dispatch, so it is the snapshot `PrepareBindings` used.
  - `PrepareBindings` emplaces exactly one `prepared.images` entry per slot, in slot order (`:2211-2228`, via the `emit`
    of `ResolveTextureWith`). `EXIT_IF(images.size() != program.info.images.size())` (`:2507`) guards the size.
  - `snapshot.images[i]` is already read for every i in `PrepareBindings` (`:2224`) and in the repair loop (`:2516`).
  - The `snapswap` swap happens inside `AheadTake`, before `PrepareBindings` (`pipelineCache.cpp:3397-3405`), so nothing
    moves the snapshot between the two calls.
  - The null test decodes the same descriptor with the same `IsNull()` that `ResolveTextureWith` uses to bind the shared
    null image (`descriptors.cpp:1373, 1385`), so exactly the null-image population is skipped.
  - The compute path reaches the same hook (`renderCompute.cpp:863, 883`).
- **CONFIRMED: `AttachmentWriteAspects()` reflects both depth and stencil writes** (`depthRenderTarget.cpp:488-535`).
  - Depth counts when `depth_write_enable || depth_load_clear_enable`.
  - Stencil counts when `stencil_clear_enable`, or when the stencil test is on and some face op can change the value
    (fail/pass/depth-fail against the write mask and compare mask).
  - An undefined format returns {}.
  - The hook runs after the explicit HTile clear path has folded its clear into `depth_load_clear_enable`
    (`renderDraw.cpp:1059-1081, 1121-1131`).
  - Colour targets with a zero write mask never reach the list (`renderDraw.cpp:1631-1638`,
    `colorRenderTarget.cpp:106-118`), so "colour = write" is sound.
- **CONFIRMED: the 64-bit record packing cannot overflow into the element field.** The key is a `uint32_t` shifted by 1
  (bits 1..32), the element starts at bit 33, and the mask `0x1ffffffff` (`graphicsRun.cpp:1437, 1555`) keeps key and
  write. The element is below 2³¹.
  - `ImageKey = index ^ generation·0x9e3779b1` (`sliceCensus.h:20-22`, `SlotId` of `common/slotVector.h:18-30,84-85`) is
    a bijection for a fixed generation. A collision needs two generations whose products agree in the high bits, which
    is negligible in one frame's image set. A collision could only merge two images, which biases `dep` upward.
  - **MINOR C1:** the key is not collision-free in principle; this has no material effect.
- **CONFIRMED: the K4 definition matches the design.** `dep` counts images present in both adjacent segments and
  written in either (`graphicsRun.cpp:1454-1479`), which is |(Wr_A∩B)∪(A∩Wr_B)|. The denominator is min(|A|,|B|), the
  result is the maximum over pairs, and cuts are strictly increasing (`upper_bound` puts the pass-start element in the
  new segment). The census is thread-local on GuestGpu (`:1376-1381`). A frame whose number jumps discards its partial
  state (`:1517-1527`).
- **MINOR C2: K4 cannot see several kinds of write.** Besides buffers, which the Limits mention, image writes that
  bypass bindings and targets are invisible: consumed compute clear shortcuts return before `RebindImages`
  (`renderCompute.cpp:411-424`), and meta/DCC clears, copies and uploads are also missed. All of these bias `dep`
  downward. This does not matter at W = 2 (47 against 300 ‰). But K4 W = 2 PASS is necessary, not sufficient:
  cross-cut buffer read-after-write was not measured.
- **CONFIRMED: at the default of 0, behaviour does not change.**
  - `slicecen` is appended last with default false (`gates.h:413`, `gates.cpp:284`).
  - Every call site is gated (`descriptors.cpp:2524`, `renderDraw.cpp:1123`, `graphicsRun.cpp:2873`). `PassBegin`
    (`context.cpp:333`) returns at `Armed()`.
  - With `spine` 0, `SpinePlan` returns after one boolean store (`graphicsRun.cpp:1588-1593`).
  - `SpineNoteReset` (`:950`, `:1562-1566`) resets only a shadow that already exists, and `Reset` is pure state
    (`:366-379`).
  - All other 14f08b2 hunks are new static helpers, `SpinePlan` bodies, or the gated element hook.
- **CONFIRMED: nothing under `src/graphics/shader/**` changed.** `git diff --stat 7c73f26..HEAD -- src/graphics/shader`
  and `1b31ae2..HEAD` are both empty. The translation-cache signature files (`generate_version.cmake:41-57` plus
  `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `CMakeLists.txt:155-156`) are untouched. build118c
  recompiled `shader.cpp` only because it includes headers that changed; its source did not change.

**Verdict:** the protocol held: decisions were recorded before actions, the seal came before the run, the pred is
unchanged, the smokes were disclosed, the fix-after-smoke was disclosed, there was no heavy work during the run, and
W2_CEILING was applied as sealed. The code is correct and inert at 0. One MAJOR finding stands: item 5's G₂ uses
f = 0.5 while the same run measured the W = 2 split at 0.555, which puts the conservative end at ≈ 2.3 ms, below the bar.
Session 119's rule must fix its f before the seal.
