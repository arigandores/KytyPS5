## 6. Readings of the executor (questions to the lead; the code reads them as written here until a lead item says otherwise)

- V1 (the binary): the binary of S13b is not installed at this seal (S12d, FS5d); the seal says "installed: PENDING" and the edition
  09b names it (section 1).  Every tag refuses rc 6 until then.  Alternative: a new seal of the code with a constant - rejected: it
  would need a new mutant run for a constant the edition rule pins as well.
- V2 (the plan): item 410 (g)(6)(iii) - S13b collects on the signature of FS5; on it 0 of the 19 are in the catalogue, so all 19
  are collected from the empty set (PLAN_FS5).  The letter of the task (the rule on 56189185...:fixb26:fixb1b) gives 5 of 19 in the
  catalogue and 14 to collect (PLAN_FS4, printed by lvl_s13.out.txt).  If a lead item lifts the block of S13b on FS5e (FS5 not
  installed), the same code collects all 19 from the empty set on FS4 too - the 5 in the installed catalogue are collected again
  (about + 5 arms); starting the collection from a copy of the installed catalogue would change the code (a new seal).
- V3 (the hold of a collection arm): 180 s = the U hold 120 s + 60 s (the catalogue must hold what the U arm meets; the game is not
  deterministic, item 408 (m)).  The constant HOLD_K is the executor's; the lead may name another before S13b (a new seal).
- V4: a collection arm runs class M (no trace) without video and without its own members; its data are printed.
- V5: w13 runs in form U (the empty app caches, the exported catalogue, prepare-cold) so the validation covers the first run of
  the user with the shipped catalogue; class M; hold 330 s.
- V6 (the letter "after the first scene frame"): E1-skip and E1-held read the rows i > fi (the first scene frame itself is not
  after it); the reading 1 of sc_s (a held first scene frame counted) is printed beside as data.  E1-skip needs both the rows and
  the lines at 0.
- V7 (the 19): ps_logo is "not a scene by its name [I]" and seven of the 19 have no -lvl entry seen on this binary family; an arm
  that does not enter its level (no line "Level has started: <level>" or no first scene frame) leaves its E1 members undetermined,
  so KNOWN_SCENES is UNDETERMINED - not PASS, not FAIL.  No level is dropped from the 19 here (item 217 (g): an exclusion only by a
  new lead item on [c] evidence of the -lvl entry); the question to the lead: whether "the 19 enterable levels" of item 229 (e)(1)
  keep a level that -lvl does not enter.
- V8 (stops): the series stops at the first death marker of any arm (as S10) and at a window event (item 273 (z)); a U arm with the
  catalogue not installed stops the later U arms and w13.  A repeat of a tag - only by a lead item.
- V9 (the export log): tools/shader_seed.py takes the compatibility line from s13/log_k_19.txt, the last collection arm on the
  installed binary; the U arms check their own log line against the signature of the seal line.
- Cost [I]: 19 collection arms of about 5 min (start, hold 180 s, returns), the export about 1 min, 19 U arms of about 4 min, w13
  about 7 min - about 3 h 10 min under the lock, one tag per lock, queue P > F > S (item 322 (g)).
- Not claimed: that the catalogue of the 19 will pass (e)(1); that the collection holds every pipeline a U arm meets; that -lvl
  enters every one of the 19; the completeness of the corpus and the catalogue; that the record of a growing blob by =1 is sound
  (S12c (3)); that the cache writes cause the freezes of a cold entry; where the driver keeps its warmth; that the freezes of an
  entry come from the shaders; that the shaders get faster on the GPU; no number is a gain; 60 FPS is not promised; the goal (B)
  does not change.
