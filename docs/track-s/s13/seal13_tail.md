## 6. Readings of the executor and the answers of the lead (item 428 (g), item 434 (b), item 436 (b), item 446, item 452; the code reads them as written here)

- V1 (the binary) - accepted: the seal says "installed: PENDING" and the edition pred/13b_s.md, made by a lead item after the
  verdict of S13r3 (item 452 (d)(2), (e)), names the sha, the signature, the variant and carries the line "edition: base
  pred/13_s.md sha256 <sha256 of this seal>" (RC6); the code does not change for the edition.  Every tag refuses rc 6 until
  then.
- V2 (the plan) - accepted: item 410 (g)(6)(iii) - S13b collects on the signature of FS5; on it 0 of the 19 are in the catalogue,
  so all 19 are collected from the empty set (PLAN_FS5); the letter "signature 56189185...:fixb26:fixb1b" of the task reads as
  "the signature of the binary of the arms".
- V3 (the hold of a collection arm) - accepted: 180 s = the U hold 120 s + 60 s (the game is not deterministic, item 408 (m)).
- V4, V5, V6, V8, V9 - accepted as written in seal 09: a collection arm runs class M without video and without its own members
  (V4); w13 runs in form U, class M, hold 330 s (V5); E1-skip and E1-held read the rows i > fi, the reading 1 printed beside, E1-skip
  needs both the rows and the lines at 0 (V6); the series stops at the first death marker and at a window event, a U arm with the
  catalogue not installed stops the later U arms and w13, a repeat only by a lead item (V8); the export takes the compatibility
  line from s13/log_k_19.txt, the U arms check their own line against the seal line (V9).
- V7 (the 19) - the rule of the lead before the data (item 428 (g)): section 1, ENTRY and WORDS: a level whose k arm and u arm are
  both "no" is "not enterable by -lvl" [c of two logs]; KNOWN_SCENES_ENTERED beside KNOWN_SCENES (unchanged).  The fields "void"
  (a death marker, hold_exit / ENDED / exited, a window event, no log, not made) are read as "not evidence" - the predicate of a
  death marker is the one of E3-death (sc142 markers, hold_exit / ENDED / exited) and the window event the one of item 273 (z)
  (minimized / Recovering Vulkan swapchain); NARROWED by item 434 (b) into the code (RC3, item 436 (b)(3)): an arm with any
  failing admission or identity row is "void"; and by item 436 (b)(4) (RC4): "no" needs both lines of the end of the
  preparation screen and a guest frame after the later one.
- Z3 (item 419 (v), item 428 (v)(1), (2)): every arm names KYTY_S_PCW=1 (section 1, THE KNOB S-pcw); the scorer checks every
  "S-pcw:" line against the env of the arm (sc_s9.py form).
- RC1-RC7 of S13r (item 436 (b)(1)-(7)) - as decided by the lead; section 1 names each in its bullet.  Fixtures:
  test_sc_s13.py R1-R13 (RC1), S1-S12 (RC2, RC7), T0-T11 (RC3, RC4), E6-E6g (RC6); test_go_s13.py G5, G5b, G22, GL15-GL17 (RC5).
- The answers of item 446 (b)-(g) to the questions of seal 12: Q-a (RC4) - the rule of the lead: only the arm k_01 is read
  "no" by item 446 (b) in S13c from the data lines of the scorer; the code and this seal do not apply it (the field "entered"
  of k_01 of the empty-set form stays "void" in the output); Q-b (RC2) - executor's variant accepted (item 446 (v)): a row by
  the log missing without a death marker -> every member UNDETERMINED, also on w13; Q-c (RC1) - executor's variant accepted
  (item 446 (g)): w13 carries no E1 member, its domain is data.
- RC1 and RC2 of S13r2 (item 452 (b), (c)) - as decided by the lead, variant (a) in the code; section 1 bullets "THE DATA OF
  ITEM 446 (b)" and "THE ADMISSION GATE".  Fixtures: test_sc_s13.py Y1-Y9 (RC1: the line and its text, 0 / 1 rows after the
  later line, "no ... yet" before and after the ready line, another variant directory and a slash path, the form with both
  lines of the end of the preparation screen "not counted" with the RC4 count unchanged, no ready / no "no ... yet" line, ASCII
  of a non-ASCII path, the lines of --read per k / U / w13 arm, no outcome changed), Z1-Z9 (RC2: a crash with a failing
  return_glc -> E3-death FAILS, the arm FAIL, "entered" void; no death with a failing man_post_app -> the members as without
  it, "entered" void; a failing cache-protocol row before the arm -> every member UNDETERMINED; each row after the arm alone;
  k_02 with app_post_copy missing -> "void", the gate ok; w13 with a failing return_app -> the W members as without it; every
  admission row of every arm kind in exactly one list; an UNCLASSED row read before the run; a name in two lists UNCLASSED;
  the words with a failing row after the arm), S9 (the three classes printed); hand mutants s13/hmut4.py (the class "after the
  arm" moved to "before the run"; the field (ii) counted while "all pipelines created" is present; the later line not the max;
  the text not printed; the rows after the arm gating W - outputs s13/hmut4/hmut_<id>.txt).
- Cost [I]: 19 collection arms of about 5 min (start, hold 180 s, returns), the export about 1 min, 19 U arms of about 4 min, w13
  about 7 min - about 3 h 10 min under the lock, one tag per lock, queue P > F > S (item 322 (g)).
- Not claimed: that a U arm and w13 reproduce the driver cache of a first run of the user (GLCache - as found, after fs5_i; RC7,
  item 436 (b)(7)); that the levels of the 19 change the scene during the hold (only [I]); that the catalogue of the 19 will pass
  (e)(1); that the collection holds every pipeline a U arm meets; that -lvl
  enters any of the seven levels without an observed entry; that ps_logo is not a scene (only [I] by its name); that an arm
  without KYTY_S_PCW would run otherwise on S12; the completeness of the corpus and the catalogue; that the record of a growing
  blob by =1 is sound (S12c (3)); that the cache writes cause the freezes of a cold entry; where the driver keeps its warmth; that
  the freezes of an entry come from the shaders; that the shaders get faster on the GPU; no number is a gain; 60 FPS is not
  promised; the goal (B) does not change.
