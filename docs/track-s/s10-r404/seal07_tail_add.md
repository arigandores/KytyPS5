## 6a. Item 404 - the decision, the executor realisation and the questions (ROADMAP "SESSION 122" item 404, KytyPS5 c1c89522)

- (v) DECIDED by the lead: T-1 and T-6 of an entered S10 arm on the domain from the first scene frame; the whole-log values a data
  row; a not entered arm on the whole log; the other identities unchanged.  The alternative "from the first FrameTrace row" was
  rejected (4 219 lines against 4 251, difference -32).
- (v) c5_0 is not repeated but rescored: by the letter of item 355 (d) 630 in-game creations, median 215 us -> NO -> the form of
  T2 = APP ("cold of the application": full return, precache by default, no salt; the driver cache is not neutralised [U]; the
  base reads the application side).  The cold gate of T2 in the form APP - by the letter of item 241 (v)(7) with item 362 (b) for
  the form APP (the recipe member kept; precache by default, the recipe writer works).
- Executor realisation (a question to the lead, printed here, not a new rule):
  (1) the admission row prereg of the five arms made under the seal 06b accepts that seal (path and sha256 605ebfa5); any other
      tag needs this seal; without it the five arms would fail admission on the seal path alone and could not be rescored;
  (2) a skipped-draw line without frame= (RX_SKIP of sc_s not matched) is not in the domain (the letter "with frame= >="), it
      is counted in the detail "(lines without frame= k)"; on the five arms k = 0;
  (3) the seal path of the harness and of its suite: s9/go_s9.sh PRED=pred/07_s.md (one line and one comment line) and five
      path literals of s9/test_go_s9.py - the lead named only s9/sc_s9.py, but go_s9.sh checks "sc_s9.py --check-seal --seal
      $PRED" before every lock, so with seal 06b it would refuse every arm after the scorer change; nothing else in go_s9.sh
      changed (diff against a4406484 in the git copy);
  (4) the threshold SKIP_LINES_MAX is compared with the whole-log line count (the emulator stops the lines per process).
- Fixtures of item 404 (g): (1) and (5) on the real logs - s10/r404/test_r404.py (c5_0 domain 4 183 / 4 183 and 150 / 150 PASS,
  the data row 4 251 / 4 271 and 171 / 170; pi_w1, pi_r1, pi_w0, pi_r0 and c5_0: every printed line of the original scorer
  b8f5e3fa (seal 06b) equal apart from the T-1 / T-6 rows, the data row and the prereg row name); (1)/(3), (2), (4) and the edges
  synthetic in s9/test_sc_s9.py X1 - X9 and G3b (prior seal).  Mutants --only of the changed functions (ident_domain, the call
  in score_arm, the prereg row, PRIOR_*, PRED_PATH): 28 of 28 killed, 3 of 3 controls survived (s10/r404/mut_r404.txt).

- Not claimed (item 404 (e)): that the salt without precache never neutralises the driver cache (one arm, one level; the word NO
  by the letter of the threshold); where the warmth of the driver lives; that the shift of frame= and n at the edges of the series
  is a defect of the emulator; that the first scene frame of c5_0 (4.34 s, K2 in the form PRECACHE=0 on f3b3aa3b) says anything
  about the installed binary; that the entry freezes are caused by the shaders; no number is a gain; 60 FPS is not promised.

