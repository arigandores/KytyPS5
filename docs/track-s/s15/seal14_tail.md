## 6. Readings of the executor and the answers of the lead (item 511 (z); item 428 (g), item 434 (b), item 436 (b), item 446, item 452, item 464 (d); the code reads them as written here)

- V1 (the binary) - item 511 (z)(1): the seal says "installed: PENDING"; the edition pred/14b_s.md, made by a lead item after FS8d
  (and after the warm-up FS8e) and before the first tag, names the sha, the TRANSLATOR SIGNATURE (field 2, item 490 (e): the part
  of the compatibility line before "::", checked by an offline export check) and the variant, and carries the line "edition: base
  pred/14_s.md sha256 <sha256 of this seal>" (RC6); the code does not change for the edition.  Every tag refuses rc 6 until then.
- V2 (the plan) - item 511 (z)(2): the same 19 levels; FS8 is a new signature and variant directory (item 471 (0)), so all 19 are
  collected from the empty set.
- V3 (the hold of a collection arm) - item 511 (z)(3): 300 s (was 180 s by the reading V3 of seal 09).
- V4, V5, V6, V8, V9 - as in seal 13: a collection arm runs class M without video and without its own members (V4); w13 runs in
  form U, class M, hold 330 s, no hold rule (V5); E1-skip and E1-held read the rows after the anchor, the reading 1 printed beside,
  E1-skip needs both the rows and the lines at 0 (V6); the series stops at the first death marker and at a window event, a U arm
  with the catalogue not installed stops the later U arms and w13, a repeat only by a lead item (V8); the export takes the
  compatibility line from s15/log_k_19.txt, the U arms check their own line against the seal line (V9).
- V7 (the 19) - as in seal 13 (item 428 (g); RC3, RC4 of item 436 (b)(3)-(4)); the acceptance is S15c.
- Z3 (item 419 (v), item 428 (v)(1), (2)): every arm names KYTY_S_PCW=1 (section 1, THE KNOB S-pcw); the scorer checks every
  "S-pcw:" line against the env of the arm (sc_s9.py form).
- RC1-RC7 of S13r (item 436 (b)(1)-(7)), the answers of item 446 (b)-(g), RC1 and RC2 of S13r2 (item 452 (b), (c)) - unchanged
  (item 511 (z)(6)); their fixtures are kept (test_sc_s15.py R1-R13, S1-S12, T0-T11, E6-E6g, Y1-Y9, Z1-Z9, S9; test_go_s15.py G5,
  G5b, G22, GL15-GL17); the hand mutants of seal 13 (s13/hmut4.py, outputs s13/hmut4/) are not rerun (the code they mutate is
  unchanged by the port).
- S15a, item 511 (z)(3)-(5) - the rules of the lead, in the code as written in section 1: (3) HOLD_K 300 (fixtures B4, B6, D1,
  G14, G18c); (4) the U hold: sc_s15.py U_RULE "120:3000:300", HOLD_RULE_U, the admission row "hold rule ... in the json" (B6b,
  B6c, D2, H1-H6, J11, Z7b), enter_scene_s15.py UHold / --hold-u (test_enter_scene_s15.py E1, E2, U1-U15, H1-H6, R1 - the replay
  of 4 real S13b logs: UHold = sc_s.locate and the domain; under the rule u_06 would have been held past 125.5 s, its video 2 942
  < 3 000), go_s15.sh the 11th field of the plan (G16, G18c, G18d); (5) the domain from the entry line (X1-X9, X5b).  Executor's
  variants (a question to the lead in the report of S15a; the code applies them): (a) the wall cap of a U hold = 300 + 60 s from
  the start of the hold (a game that stops presenting); (b) the hold of item 511 (z)(4) starts at "stable" of enter_scene (as the
  S13 hold did) - the presented time is counted from the first scene frame, so the arm is held at least the rule after it;
  (c) on the domain of item 511 (z)(5) the reading 2 of sc_s (the anchor row is before the entry line, a held flip there is not
  in the domain - X5, X5b); (d) the identities of item 511 (z)(i) by the row that counts a line, the rows of item 404 printed as
  data (a scorer fix of S15a; MINOR-6 / MINOR-7 of seal 13 now read PASS where the line is counted on both sides).
- S15a, hand mutants: s15/hmut_s15.py - 18 of enter_scene_s15.py (the comparisons of the cap, the minimum and the video, and / or,
  the closed search, the start line, the exact name and its strip, the first-scene-frame row in the time, the anchor entry, the
  scene threshold, the video count, the break of the loop, the wall cap, the json rule, the index path, the entry time, the order
  of the parse) and 6 of go_s15.sh (the "-" branch, the anchored regex, rc 2, $HUX in the call, the enter_scene path, the field
  number); outputs s15/hmut/hmut_<id>.txt, the summary lines in s15/hmut_enter.out.txt and s15/hmut_go.out.txt.
- N2 of item 464 (d): the fixture Z7b - the admission names of the 39 arms of the plan (P10 form), every name in exactly one list.
- Cost [I]: 19 collection arms of about 6.5 min (start, hold 300 s, returns), the export about 1 min, 19 U arms of about 4-7 min
  (the hold rule: 120 s after the first scene frame, longer while the video is below 3 000 frames, at most 300 s), w13 about 7 min
  - about 4.5-5 h under the lock (item 511 (z): 4.5-5 h), one tag per lock, queue P > F > S (item 322 (g)).
- Not claimed: that the catalogue is right for the first entry of the user; that a U arm and w13 reproduce the driver cache of a
  first run of the user (GLCache - as found; RC7, item 436 (b)(7)); that 300 s of collection meet the rare specializations; that
  the catalogue of the 19 will pass (e)(1) in S15; that the frames >= 100 ms of u_06 come from the shaders; that form U slows a
  scene or does not slow it on FS8 (the data of item 511 (z)(ii) are of adb0c82f and 4aa62e95); that the cache writes cause the
  freezes of a cold entry; where the driver keeps its warmth; a neutralization of the driver cache; that the freezes of an entry
  come from the shaders; that S-replay is feasible; that -lvl enters a level without an observed entry on FS8; the completeness of
  the corpus and the catalogue; that the shaders get faster on the GPU; no number is a gain; 60 FPS is not promised; the goal (B)
  does not change.
