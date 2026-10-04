"""S13a4 (HPP-553): s13/seal13_body.md and s13/seal13_tail.md from the texts of seal 12 (item 452 (b)-(d)).  Each replacement
occurs exactly once.  LF, ASCII.
    python mk_seal13_text.py
"""
S13 = 'C:/kyty/s288/s13'
NL = chr(10)


def apply(text, repl, name):
    for a, b in repl:
        n = text.count(a)
        if n != 1:
            raise SystemExit('%s: the target occurs %d times: %r' % (name, n, a[:100]))
        text = text.replace(a, b)
    text.encode('ascii')
    return text


body = open(S13 + '/seal12_body.md', encoding='ascii').read()
B = [
    ('item 419 (v) Z3, item 428, item 434 (b), item 436; constants of s13/sc_s13.py)',
     'item 419 (v) Z3, item 428, item 434 (b), item 436, item 446, item 452; constants of s13/sc_s13.py)'),
    ('''- This seal replaces pred/11_s.md (sha256 5657da3b5846144684e0de3e9fe4ae5f0087b4c93492d661650e3aae55400592): that seal is not in
  force (item 436 (v)(2)), nor is pred/09_s.md (item 428 (v)(4)); the harness and the scorer read only pred/12_s.md and its
  edition pred/12b_s.md.  The changes against seal 11 are the seven required changes of the review S13r
  (c4d4a7e9:docs/track-s/s13r-review.md) as decided by item 436 (b)(1)-(7): RC1 the E1 domain, RC2 the admission gate, RC3 and
  RC4 the field "entered", RC5 the guards, RC6 the edition line, RC7 the driver cache line - each below in its bullet.''',
     '''- This seal replaces pred/12_s.md (sha256 300ee9558d32d9af4ed3373c8ec0df5783f08f69a622362d6a2b98919ef7da5a): that seal is not in
  force (item 452 (d)(2)), nor are pred/11_s.md (item 436 (v)(2)) and pred/09_s.md (item 428 (v)(4)); the harness and the scorer
  read only pred/13_s.md and its edition pred/13b_s.md.  The changes against seal 12 are the two required changes of the review
  S13r2 (ffae6160:docs/track-s/s13r2-review.md section 2) as decided by item 452 (b), (c): RC1 the data of the reading of item 446
  (b) (bullet "THE DATA OF ITEM 446 (b)"), RC2 the third class of the admission rows "after the arm" (bullet "THE ADMISSION
  GATE").  Seal 12 itself carried the seven changes of the review S13r (c4d4a7e9:docs/track-s/s13r-review.md) as decided by item
  436 (b)(1)-(7): RC1 the E1 domain, RC2 the admission gate, RC3 and RC4 the field "entered", RC5 the guards, RC6 the edition
  line, RC7 the driver cache line - each below in its bullet, unchanged.'''),
    ('''binary of S13b is not installed yet (S12d `HPP-497`).  An edition pred/12b_s.md - every line of this seal unchanged, in order,
  plus the line "installed:" naming the binary and EXACTLY ONE line "edition: base pred/12_s.md sha256 <the 64 hex sha256 of''',
     '''binary of S13b is not named yet (the edition is a lead item after the verdict of S13r3).  An edition pred/13b_s.md - every
  line of this seal unchanged, in order, plus the line "installed:" naming the binary and EXACTLY ONE line "edition: base
  pred/13_s.md sha256 <the 64 hex sha256 of'''),
    ('''  this seal file>" (RC6, item 436 (b)(6)) - is made by a lead item after S12d that names the sha, the signature, the variant and''',
     '''  this seal file>" (RC6, item 436 (b)(6), item 452 (d)(2)) - is made by a lead item that names the sha, the signature, the
  variant and'''),
    ('''  first collection arm k_01 (the empty set) is that form; by the letter its "no" is "void" (a question to the lead in section 6).  A level of the 19 whose k''',
     '''  first collection arm k_01 (the empty set) is that form; by the letter its "no" is "void" - the lead reads k_01 by item 446 (b)
  in S13c from the data lines of bullet "THE DATA OF ITEM 446 (b)" (the code does not apply that reading).  A level of the 19 whose k'''),
    ('''- THE ADMISSION GATE (RC2, item 436 (b)(2)): the admission rows of an arm are "before the run" (the json, the environment, the
  binary, prereg, the cache protocol before the arm) or "by the log" (the S-pcw: line, the GamePatch: line, the compatibility
  line, the variant directory of the translation cache line, the window event) - fmt_arm names each.  A failing row before the
  run -> EVERY member of the arm UNDETERMINED (the computed value printed beside as "data: ...").''',
     '''- THE ADMISSION GATE (RC2, item 436 (b)(2); item 452 (c) - RC2 of S13r2): the admission rows of an arm fall into three classes
  by an EXPLICIT LIST OF NAMES in sc_s13.py (ADMIT_PRE, ADMIT_LOG, ADMIT_POST; row_class; not by position): "before the run" (the
  json, the environment, the binary, prereg, the cache protocol before the arm - restore of the app caches, GLCache not restored,
  man_launch_glc = man_pre_glc, the catalogue before the arm, the installed binary before the arm = the seal line, return_prev_ok,
  the manifests man_pre_app, man_pre_glc, glc_pre_copy, the cache json present), "by the log" (the S-pcw: line, the GamePatch:
  line, the compatibility line, the variant directory of the translation cache line, the window event) or "after the arm"
  (return_app, return_glc, the installed binary after the arm = before it, the manifests man_post_app and man_post_glc, and on a
  k_NN arm app_post_copy) - fmt_arm names the class of each row.  A row in no list or in two is UNCLASSED: printed so and read
  as "before the run"; the fixture Z7 fails on any UNCLASSED row of any arm kind (a new admission row without a class does not
  pass ALL OK).  A failing row AFTER THE ARM is printed beside the arm (the line "rows after the arm (item 452 (c)): FAIL ...")
  and makes the field "entered" "void" (item 436 (b)(3) unchanged) but does NOT gate the members of the arm: they count as
  without it (PASS, FAIL or UNDETERMINED by the other rules); the series stops anyway at the guard RETURN_FAILED (RC5) before
  the next arm.  A failing row before the run (or UNCLASSED) -> EVERY member of the arm UNDETERMINED (the computed value printed
  beside as "data: ...").'''),
    ('''  member UNDETERMINED (executor's variant, section 6).  The same on w13 (its members).''',
     '''  member UNDETERMINED (item 446 (v), Q-b).  The same on w13 (its members; the row "W admitted and entered" reads the failing
  rows but those after the arm).
- THE DATA OF ITEM 446 (b) (RC1 of S13r2, item 452 (b) - data, no outcome reads them): per arm (U, w13, k_NN; fmt_arm, and the
  lines "<tag> data of item 446 (b)" of --read for every made k arm, U arm and w13): (i) the log line number and the text of the
  first line "PipelinePrecache: no <path> yet" (ASCII, the path whole; bytes above 127 as backslash escapes) or "none"; (ii) the
  FrameTrace rows (the rows the scorer counts frames by - those of RC4) after max(the line of "ShaderPreparation: ready", the line
  of "no ... yet") when the line "PipelinePrecache: all pipelines created" is absent and both lines are present; else "not
  counted" with the reason (the line "all pipelines created" present - the form of both lines of the end of the preparation
  screen, whose RC4 count is unchanged; no ready line; no "no ... yet" line).  Beside them, executor's addition (data): whether
  the parent directory of the path is the variant of the seal line "installed:" (yes / NO / n/a while PENDING).  The field
  "entered", the members and the words do not read these lines; the reading of item 446 (b) for k_01 is the lead's in S13c.'''),
]
body13 = apply(body, B, 'body')

tail = open(S13 + '/seal12_tail.md', encoding='ascii').read()
T = [
    ('## 6. Readings of the executor and the answers of the lead (item 428 (g), item 434 (b), item 436 (b); the code reads them as written here)',
     '## 6. Readings of the executor and the answers of the lead (item 428 (g), item 434 (b), item 436 (b), item 446, item 452; the code reads them as written here)'),
    ('''- V1 (the binary) - accepted: the binary of S13b is not installed at this seal (S12d); the seal says "installed: PENDING" and the
  edition pred/12b_s.md, made by a lead item after S12d (HPP-497), names the sha, the signature, the variant and carries the
  line "edition: base pred/12_s.md sha256 <sha256 of this seal>" (RC6); the code does not change for the edition.  Every tag
  refuses rc 6 until then.''',
     '''- V1 (the binary) - accepted: the seal says "installed: PENDING" and the edition pred/13b_s.md, made by a lead item after the
  verdict of S13r3 (item 452 (d)(2), (e)), names the sha, the signature, the variant and carries the line "edition: base
  pred/13_s.md sha256 <sha256 of this seal>" (RC6); the code does not change for the edition.  Every tag refuses rc 6 until
  then.'''),
    ('''- RC1-RC7 (item 436 (b)(1)-(7)) - as decided by the lead; section 1 names each in its bullet.  Fixtures: test_sc_s13.py R1-R13
  (RC1), S1-S12 (RC2, RC7), T0-T11 (RC3, RC4), E6-E6g (RC6); test_go_s13.py G5, G5b, G22, GL15-GL17 (RC5).
- QUESTIONS to the lead (the code follows the letter; each one with the executor's variant beside, no decision in the code):
  Q-a (RC4): the first collection arm k_01 starts from the empty set; S12c's s12_gw of that form printed "PipelinePrecache: no
  ... pipelines.bin yet" instead of "PipelinePrecache: all pipelines created" (s13/rc4_s12.out.txt).  By the letter a k_01
  without the entry line is "void" even after its preparation screen; it can only keep title_controller_ship in the denominator
  (the safe direction).  Executor's variant: for the empty-set form read the line "no ... pipelines.bin yet" in place of "all
  pipelines created" (the scorer prints its line number on every arm as data, so S13c can apply either reading by its line).
  Q-b (RC2): a row by the log whose line is missing WITHOUT a death marker is not named by item 436 (b)(2); the code makes every
  member UNDETERMINED (executor's variant: the form of the arm is unknown and no crash is there to keep).
  Q-c (RC1): item 436 (b)(1) names the domain "of the U arm and of w13"; seal 11 gives w13 no E1 member (w13 is the W of (e)(3),
  class M, no attribution) - the code keeps that and prints the w13 domain as data (executor's variant); E1 members on w13 would
  be a new rule of the lead.''',
     '''- RC1-RC7 of S13r (item 436 (b)(1)-(7)) - as decided by the lead; section 1 names each in its bullet.  Fixtures:
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
  the text not printed; the rows after the arm gating W - outputs s13/hmut4/hmut_<id>.txt).'''),
]
tail13 = apply(tail, T, 'tail')
for name, text in (('seal13_body.md', body13), ('seal13_tail.md', tail13)):
    with open(S13 + '/' + name, 'w', encoding='ascii', newline=NL) as f:
        f.write(text)
    print('%s lines %d' % (name, text.count(NL)))
