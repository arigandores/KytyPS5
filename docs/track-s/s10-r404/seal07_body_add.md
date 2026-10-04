- Item 404 (ROADMAP "SESSION 122" item 404, KytyPS5 c1c89522; the lead comment a86fb7f8 in HPP-433): on an ENTERED arm (a
  first scene frame exists) the admission identities T-1 and T-6 are read on the domain of the arm - from the first scene frame
  n (the same frame as sc142.derive): T-1 = the lines "AsyncPipelines: skipped draw" with frame= >= n against the sum of
  skc_ap_skip of the FrameTrace rows with n' >= n; T-6 = the distinct frame= >= n against the sum of skc_held_inc of the same
  rows (s9/sc_s9.py ident_domain; the inherited sc_s.py of seal 04 unchanged).  The threshold SKIP_LINES_MAX (200 000) of sc_s
  counts the lines of the whole log, as before (the domain rows n/a at or above it).  The whole-log values of sc_s are printed
  beside as one data row "T-1 / T-6 whole log (data, item 404)" (n/a, not a member).  A skipped-draw line without frame= is not
  in the domain (by the letter "with frame= >= the first scene frame"; executor reading, section 6) and is counted in the detail
  "(lines without frame= k)".  A not entered arm keeps the whole-log T-1 / T-6 rows (its outcome NOT_EVALUABLE, item 371 (b)).
  T-2, sum skc_held = 0, rows without FrameTrace-x, torn rows, gaps of n, T-3, T-4 (the form C5 by s9/sc_s9.py), scan_x =
  scan_s, the first scene frame against sc142.derive - unchanged, on the whole log.
- Item 404 (g), the five arms made under the seal 06b (pi_w1, pi_r1, pi_w0, pi_r0, c5_0): rescored by this scorer without a new
  run; their admission row prereg accepts the seal 06b they ran under (path C:/kyty/s288/pred/06b_s.md, sha256 605ebfa5...,
  constants PRIOR_PATH / PRIOR_SHA / PRIOR_TAGS of s9/sc_s9.py); every later arm needs this seal 07 (executor realisation of
  "rescore the five arms", section 6).
