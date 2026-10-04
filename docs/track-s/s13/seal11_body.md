## 1. The arms, the members and the words (item 229 (e)(1), (3), item 355 (e), item 371 (v), item 408 (e), (l), item 414, item 419 (v) Z3, item 428; constants of s13/sc_s13.py)

- This seal replaces pred/09_s.md (sha256 de42894e42ad3a7cd26794fe66f001d88397611e8c43f391fb74a4052de5155d): that seal is not in
  force (item 428 (v)(4)); the harness and the scorer read only pred/11_s.md and its edition pred/11b_s.md.
- Link directory of the arms: C:/kyty/s288/s13.  The harness s13/go_s13.sh is a port of s9/go_s9.sh (seal 07): stop file, lock
  first, the RETURN_FAILED / IN_ARM guards of s4 / s6 / s10 / s13, procload, idle, one attempt per tag, the seal call line, the
  copy and the return of the caches by sha (item 228 (v)), the foreign-CPU row, GamePatch -> rc 7.  enter_scene_s9.py (seal 07,
  unchanged) gives the preparation-screen times of the attempt (prep_created_s, prep_ready_s from the Popen, 0.5 s poll).  The
  scorer s13/sc_s13.py loads s9/sc_s9.py (seal 07, sha256 db65fdc89ba728e1d5e01ac2f393389dc69ef7b9d4e7936a75cfa0347f8fd670)
  unchanged, which loads sc_s.py (seal 04) and sc142.py unchanged.
- THE BINARY (item 408 (l): the arms run on the binary installed after S12d, with the knobs S = 1; item 410 (g)(6)(iii): S13b
  collects on the signature of FS5): no arm installs a binary - every arm runs the INSTALLED one.  The seal line "installed:"
  below names it: "installed: <sha256> <translator signature> <variant directory>".  This seal says "installed: PENDING" - the
  binary of S13b is not installed yet (S12d `HPP-497`).  An edition pred/11b_s.md - every line of this seal unchanged, in order,
  plus the line "installed:" naming the binary (and optional lines "edition: ...") - is made by a lead item after S12d that names
  the sha, the signature and the variant (item 428 (g), V1); the scorer and the harness read the edition when it exists
  (sc_s13.py current_seal / edition_rows; check_seal FAILS when the edition differs from this seal in any other line, when this
  seal is not PENDING or the edition is).  The code does not change for the edition (no new seal of the code, no new mutant run).
  While the seal in force says PENDING, go_s13.sh refuses every tag rc 6 before the lock.  Admission (item 414 (b)):
  binary_sha256 of <tag>.json = the sha of the line; installed_before = installed_after = it (go_s13.sh checks it inside the lock
  before the guard - else no arm, rc 1 - and after the arm; a changed binary is returned from its copy); the log line "ShaderSeed:
  compatibility=" carries the signature of the line; the log line "Shader translation cache:" ends with its variant directory.
- THE KNOB S-pcw (item 419 (v) Z3, item 428 (v)(1), (2)): after S12 an absent KYTY_S_PCW means 1, so every arm of this seal NAMES
  it - k_01 .. k_19, u_01 .. u_19 and w13 run with KYTY_S_PCW=1 passed positionally by go_s13.sh (the constant SPCW=1; every plan
  of section 3 carries " KYTY_S_PCW=1 "); go_s13.sh unsets the caller's KYTY_S_PCW, KYTY_S_PCW_FORCE_MS, KYTY_GAME_PATCH and every
  KYTY_FIX_* before the arm.  Admission rows: "KYTY_S_PCW=1 named in the env" (the env of <tag>.json: KYTY_S_PCW = 1; absent or
  0 FAILS); "no KYTY_S_PCW_FORCE_MS / KYTY_FIX_* in the env"; every "S-pcw:" line of the log (>= 1) = "S-pcw: KYTY_S_PCW=<the value
  of KYTY_S_PCW in the env of the arm> KYTY_S_PCW_FORCE_MS=0" (the form of sc_s9.py: the log is checked against the environment
  of the arm, not against a constant; no line, a line other than the env, or a FORCE_MS other than 0 FAILS).
- Environment: M = KYTY_FRAME_TRACE=lite KYTY_GPU_HANG_ABORT_S=8 KYTY_QUEUE_TRACE=1 KYTY_GUEST_ARGS=-lvl <level>
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_S_PCW=1 (+ the path keys KYTY_GATE_FILE, KYTY_SAMPLE_GATE, and KYTY_REC on a video
  arm); T = M + KYTY_AV_TRACE=1 KYTY_SHADER_REGISTER_TRACE=1; form U = + KYTY_SHADER_SEED_PATH=C:/kyty/s288/s13/seeds
  KYTY_CACHE_MODE=prepare-cold.  The KYTY_* families of item 241 (v)(6) (KYTY_S_ among them: KYTY_S_PCW=1 named, no
  KYTY_S_PCW_FORCE_MS) = this seal, else FAIL; the strict row (every KYTY_* key; KYTY_REC present exactly on the video arms) is an
  admission row too.
- THE 19 LEVELS (item 229 (e)(1): 9 by inventory141.md + 10 sc142) - s13/lvl_s13.py, its output s13/lvl_s13.out.txt (both sealed
  below): the rows of C:/kyty/s141/step1b/inventory141_r2.md whose column "entry" begins with "da" (9, map order) and the ten census
  levels of C:/kyty/s142/go142a.sh (tag order).  K01 title_controller_ship, K02 intro_next, K03 worldmap, K04 ps_logo, K05
  hub_crashsite, K06 underwater_aerial_garden, K07 penguin_atlantis, K08 time_stopper_ghost_world, K09 rotating_level_day_and_night,
  K10 bumper_enemy_snowy_canyon, K11 big_hand_pirate_island, K12 timestop_casino, K13 mini_giants_garden, K14 ice_iceberg, K15
  sponge_dirty_bath, K16 hoover_beach, K17 volcano_mountain, K18 voxel_world, K19 enemy_gorilla.
  "In the catalogue" by the rule of item 355 (e) (a log on a binary with the signature with cache writes, not an arm with a
  return - the reading of lvl_s9.py accepted by item 364): on the signature 56189185...:fixb26:fixb1b (FS4) 5 of 19 - worldmap,
  underwater_aerial_garden, timestop_casino, sponge_dirty_bath, hoover_beach; on the signature of FS5 (26ce5fc7...:fixf10) 0 of 19.
  Seven levels have no entry line in any log since 2026-09-30T23:41:52Z on any signature (title_controller_ship, intro_next,
  ps_logo, hub_crashsite, penguin_atlantis, time_stopper_ghost_world, rotating_level_day_and_night) - their -lvl entry on this
  binary family is unseen; ps_logo is "not a scene by its name [I]" (item 217 (g)).  The compatibility line of the S9 export
  (s9/seeds/PPSA21564/compatibility.txt) = the line "ShaderSeed: compatibility=" of the log of the installed FS4 31cbfee8
  (f287/fs4c/log_fs4_v.txt line 83): EQUAL.
- ENTRY (item 428 (g), V7 - the rule before the data): the field "entered" of an arm (sc_s13.py entry_state): "yes" - the log
  carries "Level has started: <level>"; "no" - an attempt with a log, without that line, without a death marker of sc142 (nor
  hold_exit / ENDED / exited - the predicate of E3-death) and without a window event (minimized / Recovering Vulkan swapchain);
  "void" otherwise (not made, no log, a death marker or a window event without the line) - not evidence.  A level of the 19 whose k
  arm AND u arm are both "no" is "not enterable by -lvl" [c of two logs]: it leaves the denominator of (e)(1) by a line of the
  acceptance S13c, stays in the list of 19 (item 217 (g)) and is not in the ship "known scenes".  A level entered in at least one of
  its two arms stays in the denominator; its U arm without the entry or without a first scene frame is UNDETERMINED.
- THE COLLECTION k_01 .. k_19 (item 408 (l), item 410 (g)(6)(iii); the plan PLAN_FS5 of lvl_s13.out.txt: on the signature of FS5
  none of the 19 is in the catalogue -> all 19 are collected, item 428 (g) V2): class M, hold 180 s (V3), no video, stable 100 /
  timeout 600, the level K<NN>.  The catalogue of the collection lives in C:/kyty/s288/s13/cat, never in the installed caches:
  before k_01 the app caches (_ShaderCache/PPSA21564, _PipelineCache) are mirrored from the empty set (s13/empty_app, MANIFEST sha
  EMPTY_SHA); before k_NN (NN > 01) from the post copy s13/cat/k_<NN-1> (its MANIFEST sha = app_post_copy of the previous arm);
  GLCache as found (copied before, returned after, not restored); after the arm the app caches are copied to s13/cat/<tag>
  (app_post_copy noted); then the installed app caches and GLCache return by sha (cachex_s.py restore from the copies made inside
  the lock).  A k arm is read by its admission and data (entered, the first scene frame, recipes written, death markers, window
  events); the members of (e)(1) are not read on a k arm; its field "entered" counts for the rule ENTRY.
- THE EXPORT (item 408 (l), (z)): s13/seedexp_s13.py after k_19 (no game, no lock; it refuses when the lock exists): the seal in
  force names the variant; the post copy s13/cat/k_19 (its MANIFEST.txt = app_post_copy of k_19, cachex_s.py verify) -> its
  directory ShaderCache_PPSA21564/<variant> -> a byte-for-byte stage s13/stage/PPSA21564 -> tools/shader_seed.py --log
  s13/log_k_19.txt (its json binary = the line, no patch, its compatibility line on the signature) -> s13/seeds/PPSA21564; printed:
  shaders by stage, recipes, R_DUP_GFX / R_DUP_CS, the line "removed duplicates (F17): N" (the tool copies pipelines.bin byte for
  byte: 0; else UNDETERMINED - item 408 (z)), "compatibility.txt: <line>" = the log line, the offline install check (signature +
  XXH3 of every shader file, the recipe header), the manifest s13/seeds_manifest.txt and "SEEDS manifest ... sha256 <sha>",
  "source arm k_19 app_post_copy <sha>", "EXPORT: OK".  The scorer reads it (export_state): EXPORT: OK, the manifest line = the
  file = the live catalogue, the source = app_post_copy of k_19.  u_01 does not run before the export state is OK (rc 6).
- THE U ARMS u_01 .. u_19 (form U, item 355 (e) = item 229 (e)(1) "first run of the user"): class T, the level K<NN>, hold 120 s,
  video (KYTY_REC), stable 100 / timeout 600; the app caches empty for the arm, GLCache as found, the seed path s13/seeds and
  prepare-cold; the catalogue checked by sha before the arm (sc_s13.py --seeds-check: the live s13/seeds/PPSA21564 =
  seeds_manifest.txt) and noted in the cache json.  Gates (item 355 (e)): "ShaderSeed: installed" (log) and "Cache test mode:
  prepare-cold" (stdout) - without them the arm is "CATALOGUE NOT INSTALLED": not an attempt of (e)(1), its members undetermined,
  the next U / W tag refused rc 6 (a question to the lead).
- THE W ARM w13 (item 229 (e)(3)): Sky Garden (underwater_aerial_garden) in form U + validation of item 295 (b):
  --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, no VK_LAYER_MESSAGE_ID_FILTER (the form line
  "W form: limit=100000000 filter=none"), class M, hold 330 s, no video, stable 300 / timeout 600, KYTY_S_PCW=1.
- MEMBERS of a U arm (after the first scene frame = the FrameTrace rows i > fi of sc_s.locate, fi the first row with draws >=
  the scene threshold after the entry line, and the event lines of the groups fi < g < end):
  E1-skip   0 frames with a skipped draw: the rows with skc_ap_skip > 0 = 0 AND the "AsyncPipelines: skipped draw" lines = 0;
  E1-held   0 held flips: the sum of skc_held_inc of the rows = 0 (the reading 1 of sc_s - with a held first scene frame - is
            printed beside as data);
  E1-attr   0 attributed frames >= 100 ms: sc_s.attributed on reading 1 (presented rows of attribution SHADER or class PCW + series
            with gap_pipe >= 100 ms); undetermined when the attribution is (T-3 / T-4 broken);
  E1-screen the preparation screen <= 180 s: measured = the later of prep_created_s and prep_ready_s (both lines seen); a line
            missing - the lower bound max(elapsed_ms of "ShaderPreparation: progress", --timeout when the attempt ended by
            timeout); a bound > 180 s fails; otherwise undetermined (item 371 (v));
  E3-video  the video >= 3 000 frames, 0 one-frame glitches (s51_vidglitch.py 4 6), the sheet made (sheet142.py); no video file or
            no glitch file -> undetermined; the lead reads the sheet;
  E3-death  0 death markers of sc142 (log and stdout: Unhandled exception / Fatal Error / Error / GpuHangAbort / ErrorDeviceLost)
            and no hold_exit / ENDED / exited.
  An arm whose admission or identity fails, or that is not entered, or without a first scene frame, or with the catalogue not
  installed has its E1 members undetermined.  The arm word: FAIL - a determined failing member; UNDETERMINED - an undetermined one;
  else PASS.
- MEMBERS of w13: the catalogue installed; admitted and entered; >= 300 s (300 000 000 us) presented after the first scene frame;
  0 [Vulkan][E] (log + stdout); the rows of item 295 (b)(1)-(3) (0 layer limit lines; >= 1 validation-layer line [W][2] / [E][2];
  the last such line at most 10 s of presented time before the last row of the hold); "DualSrcBlend: supported=1 enabled=1" before
  the first line carrying GuestOut (item 300 (b)(4)); 0 death markers.
- WORDS: KNOWN_SCENES (item 229 (e)(1) with (3); unchanged) - PASS when 19 of 19 U arms and w13 PASS; FAIL on any FAIL; else
  UNDETERMINED.  Beside it KNOWN_SCENES_ENTERED (item 428 (g)) - over the U arms of the levels outside "not enterable by -lvl":
  PASS when every one PASS and w13 PASS with a denominator >= 1; FAIL on any FAIL (w13 included); else UNDETERMINED (a denominator
  0 is UNDETERMINED); printed with the denominator, the counts and the list "not enterable by -lvl", and one line "entry" per level
  (k state, u state, in the denominator / NOT ENTERABLE).  Beside them: the word of (e)(1) alone (the U arms, members gates /
  E1-*) and of (e)(3) alone (the U arms, members gates / E3-*, and w13), the count per member (ok / fails / undetermined of 19).
  The decision (S13c: the acceptance of (e)(1), the levels leaving the denominator, the installation of the catalogue - the ship
  "known scenes" by its own line) is the lead's.
- DATA ROWS (item 414 (g)(5)-(7), AUDIT_S3 section 6 p. 2): per arm the skipped-draw lines after the entry line whose frame= is below
  the first scene frame, and the skipped-draw lines without frame=; the T-1 / T-6 identities on the domain from the first scene
  frame (item 404, sc_s9.ident_domain unchanged) with the whole-log values as one data row; fixtures: a line without frame= counted
  by skc_ap_skip in the domain -> T-1 FAILS (MINOR-7); a line counted by the row n 6 = f0 - 1 but labelled frame= 8 = n + 2 -> T-1
  FAILS (MINOR-6, the safe direction); a line on the first scene frame labelled frame= n + 2 -> PASS.  S-early: the events of
  sc_s9.early9 (frame: cost = PREP + the async creations of i-2 .. i+1, PREP beside; series: cost named "async creation us", no
  "PREP-only" column - MAJOR-2); the count over DISTINCT events (item 414 (g)(1): a frame event whose n is the n of a series event
  of the same arm is one event).  The held frames >= 100 ms with their class (data, debt D-2 of AUDIT_S3).  The window events of
  item 273 (z) by kind; a "minimized" or "Recovering Vulkan swapchain" line fails the admission and stops the series (rc 6 for the
  next tag).
- ORDER (sc_s13.py --allowed): k_01 .. k_19, the export, u_01 .. u_19, w13; one call per tag, no repeat (a repeat - a lead item);
  every tag needs its predecessor made; the series stops (rc 6) at the first death marker of any earlier arm and at a window event;
  u_01 needs the export state OK; a U arm with the catalogue not installed stops the later U arms and w13.
- S9r2 observations (item 382 (b), item 408 (k)(4)), fixed in the port: (1) go_s13.sh sets RETFAIL=1 in return_failed and removes
  s13/IN_ARM only with RETFAIL=0 - after a failed return no later return of the same run removes the guard (fixture GL14); (2) the
  lock line names "(go_s13.sh seal $PRED)" - the seal file in force, not a fixed number (fixture GL11); (3) the admission line is
  the seal line "installed:" itself, read by the scorer and the harness; --check-seal checks its form (one line, PENDING or sha +
  KytySC3: signature + variant_ directory), the edition rows, and with --game that the installed binary now has that sha.
