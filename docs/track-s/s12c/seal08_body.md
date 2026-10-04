# Seal 08_s - track S link S12c (HPP-496): the shipping arms of S-pcw on the S12 copy adb0c82f - s12_w, s12_v, the blob growth pair s12_gw / s12_gr, the reference s12_v0 (ROADMAP "SESSION 122" item 408 (l) S12c; item 414 (b), (d)(1), (g)(2); item 419 (v) Z1-Z3)

@WRITTEN@  No S12c tag runs before the lead line "Seal 08 accepted" in HPP-496 (item 408 (l)).  After this seal the scorer, the fixtures, the mutants and the harness do not change (a change = a new seal).  The arms are scored by s12/sc_s12.py (new; it loads C:/kyty/s288/sc_s.py of seal 04, sha256 8b0e0aff..., unchanged, only for the class of item 241 (v)(3) in the data line of item 414 (g)(2)).  ASCII only.

## 1. The arms, the members, the words (constants of s12/sc_s12.py; harness s12/go_s12.sh)

- Link directory: C:/kyty/s288/s12 (item 408 (l)).  The harness s12/go_s12.sh is a port of s9/go_s9.sh (seal 07): stop file, lock
  first, the RETURN_FAILED / IN_ARM guards of s4 / s6 / s10 / s12, procload, the name guard, idle (cpu < 15 and idle142), one attempt,
  the seal call line, the S12 copy installed for the arm only and the installed binary returned by sha after it, the app caches
  (_ShaderCache/PPSA21564 with pipelines.bin, _PipelineCache) and GLCache copied before every arm and returned by manifest sha after it
  (cachex_s.py, unchanged), the lock rows in s12/runs_s/lock.log (UTC), the foreign-CPU row (fgcpu143.py, <app> mask), GamePatch ->
  rc 7.  The driver: s9/enter_scene_s9.py (seal 07, unchanged; --attempts 1 --no-install --require-idle, the seal path as --pred).
  Every KYTY_* and VK_LAYER_* variable of the calling shell is unset by go_s12.sh; the arm's environment is the positional pairs only.
- The binary of every arm: the S12 copy C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe (sha256 adb0c82f..., item 419 (a)); the scorer
  names the binary of an arm by the field binary_sha256 of <tag>.json (item 414 (b), (d)(1)); the row installed_before (the binary
  installed in the emulator folder before the arm, returned after) is a row of the return, never the arm's binary.
- Admission of every arm (NOT_ADMITTED if any fails): one attempt; binary_sha256 = adb0c82f; prereg = this seal (sha and path); guest
  args -lvl <level>; gates empty; every KYTY_* and VK_* key of the json env = the seal (values; path keys by suffix); --vulkan-validation
  true only on s12_w; --hold of the arm; no pipeline-cache retry; installed before in {FS4 31cbfee8, FS5 631ff987} (section 6, Q1) and
  after = before; return_prev ok; return_app / return_glc got = expected; the restores of the mode; s12_gw records its post copies;
  Z3 (item 419 (v), a standing rule of track S): the arm names KYTY_S_PCW explicitly (s12_v0 0, the others 1) and every log line
  "S-pcw: ..." equals "S-pcw: KYTY_S_PCW=<v> KYTY_S_PCW_FORCE_MS=0" (>= 1 line; the form of sc_s9.py; no arm sets the stand).
- Environment M = KYTY_FRAME_TRACE=lite KYTY_GPU_HANG_ABORT_S=8 KYTY_QUEUE_TRACE=1 KYTY_GUEST_ARGS=-lvl <level> KYTY_GPU_CLOCK_PIN=1
  KYTY_GPU_MARKERS=0 KYTY_S_PCW=<v> (+ the path keys KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_REC on video arms); T = M + KYTY_AV_TRACE=1
  KYTY_SHADER_REGISTER_TRACE=1 (the line "AvTrace: pcw recipes" is printed only with the AV trace, 4d9e8ab7 pipelineCache.cpp:6263).
  No arm names KYTY_GAME_PATCH, KYTY_S_PCW_FORCE_MS, KYTY_GPU_CHECKPOINTS, a salt or KYTY_PIPELINE_PRECACHE (precache by default).
- (1) s12_w - W Sky Garden (underwater_aerial_garden), M, caches as found (copied before, returned after; no restore), the W form of
  item 295 (b): --emu-arg=--vulkan-validation --emu-arg=true VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin
  VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, no VK_LAYER_MESSAGE_ID_FILTER, no video, --hold 310, stable 300, timeout 600 (the form of
  FS5c fs5_w).  Members: entered (the entry line and a first scene frame, draws >= 100); hold >= 300 s (sum dt_us after the first
  scene frame, before a scene change); 0 [Vulkan][E] in the log and in the stdout; [Vulkan][W] > 0 (positive control of the layer);
  0 layer limit lines ("this will be the last time reporting it", log and stdout); DualSrcBlend: supported=1 enabled=1 before the
  first line carrying GuestOut; 0 death markers.
- (2) s12_v - V Sky Garden, M, caches as found, video (KYTY_REC), --hold 330, stable 300, timeout 480.  Members: entered; hold >= 300
  s; video index records >= 3 000; 0 one-frame glitches (s51_vidglitch.py <rec> 4 6, line "one-frame glitches: N"; missing -> the
  member unread -> NOT_EVALUABLE); the sheet for the lead made (sheet142.py, line "sheet: "); 0 death markers; 0 frames >= 1 s after
  the first scene frame.  The lead views the sheet (item 408 (l) "list of the lead").
- (3) the blob growth pair.  s12_gw - hero_kratos, T, full return from snap0 (d8ca8c8e) + snap0_drv (1767ca0a) - the form APP (precache
  by default, no salt) - video, --hold 330, stable 100, timeout 480; after the arm the app caches and GLCache are copied to
  s12/app_post/s12_gw and s12/glc_post/s12_gw before the return (their MANIFEST.txt lines "<path> <size> <sha256>" are the Z2 manifest;
  the harness also writes the row "Z2 manifest after s12_gw" into s12/times.txt).  Members: PipelineCache/PPSA21564.bin present in
  the post manifest; its sha256 != snap0 cc5b747c5bece91e...; its size > 94 435 713 bytes (snap0); 0 death markers; entered.  Z2: the
  manifest names PPSA21564.bin (present, sha256, size) and PPSA21564.bin.tmp (present) - printed; ".bin absent, .tmp present" is the
  word INTERFERENCE (window (g) of the review, item 419 (g)); a repeat of the pair from snap0 only by a lead item, not counted as an
  attempt.  Z1 (s12_gw): the counts of "saved" (and of them "... forced"), "save failed", "failed to write", "failed to create cache
  directory" are printed (data).
  s12_gr - hero_kratos, T, integrity (the form pcw_int of seal 04): the app caches and GLCache restored from the post copies of s12_gw
  (no snapshot), video, --hold 120, stable 100, timeout 480.  Members (Z1, item 419 (v)): exactly one line "Vulkan pipeline cache:
  loading" and exactly one "loaded N bytes"; 0 lines of each of initializing, initialized empty, invalidating, driver rejected,
  disabled (one member row each); N = the last "saved N bytes" of s12_gw; N = the size of PPSA21564.bin in the post manifest of s12_gw
  - 76 (the driver signature + the 8 bytes of the XXH3 hash; 76 = 94 435 713 - 94 435 637, snap0 against the loaded N of pi_r1, S10);
  without a loaded line the member row fails and names its cause (the classes seen, or "no load line of any class") - never None;
  0 death markers; 0 one-frame glitches; the sheet for the lead made.  The state (e) of the review (a file newer than the last saved
  line) fails the row "N = the last saved" and passes "N = size - 76": both are printed; the word is FAIL by the letter.
- (4) s12_v0 - the reference: s12_v with KYTY_S_PCW=0; the members of s12_v printed; its word REFERENCE_PASS / REFERENCE_FAIL, not a
  member of the ship.
- The data line of item 414 (g)(2) (Debt D-2 of AUDIT_S3; not a member) on s12_gw and s12_gr: the "AvTrace: pcw recipes" lines (count,
  sum and maximum of hold_us, maximum of lock_us, sum of copied) and every held frame >= 100 ms after the first scene frame with its
  class of item 241 (v)(3) (sc_s.classify of seal 04: PCW / SHADER / PRIO / GPUTHR / WAIT; attribution with T-3 of sc_s and T-4 read
  "no queued line and 0 precache lines" as the identity - the cold variant directory has no recipes file), the hold_us of the pcw
  recipes lines in its groups i .. i+1 and the mark "+recipes-save" when a "PipelinePrecache: saved" line is there; NOT_EVALUABLE (never
  0) when there is no such line or frame.  The regression shows the line on S10 t2_1: one held frame n 282 of 280.4 ms, class PCW,
  +recipes-save, no pcw recipes line (KYTY_S_PCW=0 arm) -> NOT_EVALUABLE (AUDIT_S3 MINOR-2).
- Data of every arm (not members): log and stdout sha256, the entry / scene change lines, frames >= 1 s and >= 100 ms after the
  first scene frame, death markers, window lines, Recovering Vulkan swapchain, GamePatch lines, skipped-draw lines, the counts of
  every "Vulkan pipeline cache:" class and the unknown ones, the saves, the translation cache directories and the first
  PipelinePrecache line (warm or cold variant directory, section 6 Q2), [Vulkan][E] / [W] / limit, DualSrcBlend.
- Death markers (log and stdout): "Unhandled exception:", "--- Fatal Error ---", "--- Error ---", "GpuHangAbort:", "ErrorDeviceLost".
- Words, in this order: NOT_EVALUABLE (json, log or stdout missing); NOT_ADMITTED (an admission row fails); INTERFERENCE (a line
  "Window <n> minimized", "Recovering Vulkan swapchain", a line beginning "GamePatch:" (item 342 (e)); s12_gw ".bin absent, .tmp
  present"); NOT_EVALUABLE (not entered, or a member unread); PASS / FAIL (s12_v0: REFERENCE_PASS / REFERENCE_FAIL).  The summary
  (sc_s12.py --summary): S12C (1) s12_w, (2) s12_v, (3) the pair PASS only when s12_gw and s12_gr are both PASS, (4) s12_v0.
- Order and stops (sc_s12.py --allowed; go_s12.sh rc 6 = no run, a question to the lead): s12_w s12_v s12_gw s12_gr s12_v0; every
  earlier arm made and scored (runs_s/<tag>.score.json); after a made arm with a death marker or the word INTERFERENCE the series
  stops; s12_gr only after s12_gw PASS or FAIL with s12/app_post/s12_gw and s12/glc_post/s12_gw present.
- Not claimed (item 408 (n), 414 (z), 419 (e)): that the event pcw_int is an effect of the game or a defect; that the write of a
  growing blob by =1 is whole before the pair is read; that the driver returns a consistent snapshot under parallel inserts (class
  (d) of the review is seen only by the members "0 death markers" and "video 0 glitches, the sheet of the lead" of s12_gr); that the
  cache write causes the freezes of a cold entry; that the write of the recipes file causes held frames; where the warmth of the
  driver is kept; that S12 works in the game before these arms; no number is a gain; 60 FPS is not promised.

## 6. The executor's readings and the questions to the lead (printed here; not new rules)

- Q1 (installed binary): the task says "the installed FS4 does not change"; FS5d (HPP-512, done) installed FS5 631ff987 before this
  seal (sha of C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe 631ff987... at 08:43:57Z).  Executor variant: the admission row and the
  harness accept the installed binary before the arm in {FS4 31cbfee8, FS5 631ff987} (INST_OK; anything else -> rc 1 inside the lock,
  nothing installed); the installed one is returned by sha after every arm either way.  A single value would refuse every arm after
  the next installation.
- Q2 (warm or cold entry of s12_w / s12_v / s12_v0): S12 = FS5 + the default of KYTY_S_PCW (item 419 (b)), so its translation
  signature and its variant directory variant_fixb26_fixb1b_fixf10 are those of FS5; FS5e (HPP-513, prewarm fs5_i without the return
  of the caches) was in progress at the seal and warms that directory.  The arms (1), (2), (4) run on the caches as found - warm after
  FS5e, cold before it; the data row prints the translation cache directory and the first PipelinePrecache line.  FS5c showed the cold
  entry of FS5 passing (fs5_v 0 frames >= 1 s, 0 glitches).
- Q3 (s12_gw from snap0): snap0 holds the translation caches of the signature 699c1e4b (no directory of the FS5 signature), so the
  translation and the recipes of s12_gw are cold (no startup precache); the driver blob prefix carries only the driver signature
  (review section 4 (b)), so snap0's blob loads (94 435 637 bytes, a data row) and the cold creations of the level grow it - the
  members (3) read that growth.  "300 s" of the task is read as the duration of the arm (--hold 330 as pi_w of S10), not a member.
- Q4 (members beyond the letter of item 408 (l)): s12_w also has [Vulkan][W] > 0 (positive control) and 0 limit lines (the form of
  item 295 (b) and FS5c fs5_w; a W without layer lines proves nothing); every arm has "entered" (no entry -> NOT_EVALUABLE); s12_gw has
  "0 death markers" (the series stops on it); the video of s12_gw and the frame count of s12_gr are data, not members.
- Q5: hold and timeout of s12_w = FS5c fs5_w (310 / 600); s12_v / s12_v0 = fs5_v (330 / 480); stable 300 on Sky Garden, 100 on
  hero_kratos (T2 of S10).
