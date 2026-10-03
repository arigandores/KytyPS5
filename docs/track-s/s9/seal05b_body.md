- Link directory of the arms: C:/kyty/s288/s10 (item 355 (k)); the harness s9/go_s9.sh (a port of go_s.sh of seal 04: stop file,
  lock first, RETURN_FAILED guards of s4 / s6 / s10, procload, idle, one attempt, the seal call line, the copy and the return of
  the installed binary and of the caches by sha, the foreign-CPU row, GamePatch -> rc 7); enter_scene_s9.py = enter_scene.py of
  seal 04 + the preparation-screen times of the attempt (prep_created_s, prep_ready_s from the Popen, 0.5 s poll).
- Environment: M = KYTY_FRAME_TRACE=lite KYTY_GPU_HANG_ABORT_S=8 KYTY_QUEUE_TRACE=1 KYTY_GUEST_ARGS=-lvl <level>
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 (+ the path keys KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_REC); T = M + KYTY_AV_TRACE=1
  KYTY_SHADER_REGISTER_TRACE=1.  The KYTY_* families of item 241 (v)(6) (ASYNC_, PIPELINE_, SHADER_, S_, DUMP_, FIX_,
  KYTY_CACHE_MODE, KYTY_CS_PRETRANSLATE) = this seal, else FAIL; the strict row (every KYTY_* key) is printed and is an admission
  row too.  No arm runs validation; no arm names KYTY_GAME_PATCH (item 342 (e)).
- (g) the repeat of integrity, binary s (f3b3aa3b, S5c), underwater_aerial_garden, video:
  pi_w1 M, full return (snap0 d8ca8c8e + snap0_drv 1767ca0a), KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=15000, hold 330 (>= 300 s presented
  after the first scene frame - a readability row); after the arm the app caches and GLCache are copied to s10/app_post/pi_w1 and
  s10/glc_post/pi_w1.  pi_r1 T, integrity: the app caches and GLCache restored from those copies (no snapshot - the form pcw_int
  of seal 04), =1 + 15000, hold 120.  pi_w0 / pi_r0 the same with KYTY_S_PCW=0.
  The detector of the lead (C:/kyty/s288/lead/haze_s8.py, ported by the letter into sc_s9.py): ffmpeg crop 300x60 at (660, 60) of
  the 960x540 frame, scale 60x12, rgb24; per frame the mean of (max - min) / (max + 1); the median of the frames >= 300 (0 when
  the video has <= 300 frames); a frame is low below 0.75 x the median; low frames merge with a gap <= 3; a series is kept when
  end - start >= 5 (the code of the lead); "after frame 1 002" = start > 1 002 (letter), the variant "any frame > 1 002" printed
  beside (a difference is printed "DIFFERS (edge 1 002)").  Positive fixture: the cached saturations of s6/rec_pcw_int.mp4
  (sha256 705cb5fd...) give the series 1 928 - 1 946 as the only one after frame 1 002; negative: s6/rec_pcw_1.mp4 (518df1a0...)
  none after it (s9/fx/haze_pcw_int.json, s9/fx/haze_pcw_1.json, made by sc_s9.haze_of; --regress runs the detector on the six
  videos of item 355 (g) and matches the lead).
  Reading (item 355 (g), item 362 (v)) by the scorer word: READ_1 - a series in pi_r1 and none in pi_r0 (a defect of S-pcw:
  iteration 2, B33 not FIXED); READ_2 - no series in the four, or a series in both R, AND both R "Vulkan pipeline cache: loaded N
  bytes" = the last "saved N bytes" of their own W and 0 "disabled" (B33 FIXED, the count of track S, not a ship under (B));
  READ_3 - a series only in pi_r0 (among the R arms: a series in pi_r0 and in a W arm with none in pi_r1 is READ_3, printed with
  a note) or only in the W arms, AND the loaded member of READ_2 on both R (item 362 (v): "as (2)" is the consequence and the
  condition; an effect of the scene [I], as (2)); without the loaded member -> READ_OTHER; the executor's reading (READ_3 without
  the loaded member) is printed beside ("reading of the executor ...", "DIFFERS (the loaded member)" when it differs);
  READ_OTHER - any other outcome (decision S11); NOT_EVALUABLE - an arm missing, not admitted, not entered, without the video, a video < 3 000 frames or with a
  one-frame glitch, a death marker, or a W arm presented < 300 s.  Beside it: (z)(1) on pi_r1 - "AvTrace: pcw overlap wait"
  lines; 0 -> "undetermined (RC1 S5d)", printed beside FIXED and not a member of it (item 355 (g)).  The lead sheet of every
  series after frame 1 002: go_s9.sh writes s10/haze_<tag>_<start>-<end>.png (frames start-2 .. end+2, at most 24).
- (d) c5_0: binary s, L0 shuriken_ninja_castle, T, full return, KYTY_PIPELINE_SALT=c5_0 KYTY_PIPELINE_PRECACHE=0, hold 120.
  "Salt without precache neutralises" = >= 10 in-game creations (lines "AvTrace: pipeline " without the word "precache" that carry
  a " us=" field; lines without it - "waited_us" - are counted apart, not in the median) AND their median us >= 20 000 -> YES;
  else NO.  The form of T2 by code: YES -> C5 (full return, KYTY_PIPELINE_SALT=<tag>, KYTY_PIPELINE_PRECACHE=0); NO -> APP "cold of
  the application" (full return, precache by default, no salt; the line "the driver cache is not neutralised [U]").  c5_0 not
  admitted or not entered -> UNDETERMINED: no T2 tag runs (go_s9.sh rc 6), a question to the lead.
- (d) T2: binary s, T, full return, hold 120, the form of C5; levels of s9/lvl_s9.py (T2LIST): t2_1 hero_kratos, t2_2 hero_drake,
  t2_3 voxel_challenge_3, t2_4 armadillo_challenge_2, t2_5 fragile_battle_4; reserves t2_6 voxel_challenge_4, t2_7
  fragile_battle_5, t2_8 voxel_challenge_5, t2_9 miniboss_challenge_genie, t2_10 symbol_triangle (a reserve only while fewer than
  five T2 arms count).  t2_cs0 = the level of t2_1, its form + KYTY_CS_PRETRANSLATE=0, right after t2_1 (item 355 (d)); its rows
  against t2_1 are data (skip rows, held flips, presented frames >= 100 ms, the CsPretranslate lines by kind), decision S11.
  A T2 arm counts with its admission, its entry and the cold gate of item 241 (v)(7) as decided by item 362 (b)
  (T2_GATE_READING = p362): in the form C5 (KYTY_PIPELINE_PRECACHE=0) a new permutation, >= 1 in-game creation after the entry
  line (a line "AvTrace: pipeline " without the word "precache" with a " us=" field whose log line number is above the line
  "GuestOut: Level has started: L"; the count create_after of the gates) and a skipped draw after the entry line - the recipe
  member is replaced because PRECACHE=0 stops the recipe writer (4fc501f4 pipelineCache.cpp:5858); in the form APP by the letter
  (a new permutation, a new recipe and a skipped draw).  Beside per T2 arm and in the counts: "by the letter (with the recipe)"
  and "executor variant" (the recipe member dropped with no replacement, rejected by item 362 (b)).  T-4 under KYTY_PIPELINE_PRECACHE=0 (c5_0, form C5): 0 precache
  lines and no queued line is the identity (the letter row of sc_s - "no queued line" -> broken - would fail every such arm).
  S-early (item 241 (b)(4)): per attributed frame >= 100 ms of the counted T2 arms the cost = PREP + the us of the async creations
  in groups i-2 .. i+1, per series with gap_pipe >= 100 ms the async us ending in it; lead = FirstUse - Register (sc_s.early);
  "lead < cost in n of m" (denominator 0 -> undetermined); the PREP-only reading of sc_s printed beside.  Column (zh): the
  number of BvhLoopCapTrip: lines in the groups i-1 .. i of every frame >= 100 ms (data, not a class).
- (e) the S-cat probe, binary u (the installed 4aa62e95), form U: the app caches _ShaderCache/PPSA21564 and _PipelineCache
  mirrored from s10/empty_app (MANIFEST.txt empty, sha e3b0c442...) for the arm, GLCache as found (copy before, return after),
  the installed caches returned after by sha; KYTY_SHADER_SEED_PATH=C:/kyty/s288/s9/seeds KYTY_CACHE_MODE=prepare-cold; T, hold
  120, stable 100, timeout 600.  The catalogue s9/seeds/PPSA21564 is checked against seeds_manifest.txt (sha 72605a65...) before
  every U arm (sc_s9.py --seeds-check; a difference -> rc 1, no run).  Gates of the arm: >= 1 log line "ShaderSeed: installed"
  and >= 1 stdout line "Cache test mode: prepare-cold"; without them the arm is "CATALOGUE NOT INSTALLED", not an S-cat
  attempt; the U series stops (rc 6) and the lead is asked.  Levels (lvl_s9.py ULIST): u_1 underwater_aerial_garden, u_2
  hoover_beach, u_3 robot_builder_next, u_4 interactive_credit_00, u_5 fragile_battle_1 (mini_giants_garden is not in the
  catalogue: no log with cache writes on the signature carries its entry line).  An arm FAILS S-cat with a skipped-draw line
  after the first scene frame or an attributed frame >= 100 ms (sc_s attributed(): SHADER or PCW rows and series with gap_pipe
  >= 100 ms); the preparation screen = the later of prep_created_s ("PipelinePrecache: all pipelines created") and prep_ready_s
  ("ShaderPreparation: ready"), both printed, with the log values (created ms, startup wait ms).  KILLED - >= 2 of 5 arms fail or
  any screen > 180 s; ALIVE_BY_PROBE_5 - otherwise with every arm evaluable; UNDETERMINED - an arm not evaluable and no kill.
- Every arm: video (s51_vidglitch.py, sheet142.py), the sc142 outcome and death markers, the BvhLoopCapTrip column, the in-game
  creations, the preparation lines, the driver cache writes and loads; the identities "scan_x rows = scan_s rows" and "scan_x lines = scan_s lines" (the line numbers of the creations, item 362 (b);
  FAIL when broken).
