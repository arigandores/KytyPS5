"""mk05b.py - track S link S9 (HPP-431), rework 1 (item 362 (d)): makes s9/mkseal_s05b.py, s9/seal05b_body.md, s9/seal05b_tail.md
from the files of seal 05 (which do not change).  Every replacement matches once.  LF, ASCII.  Refuses under the lock.
"""
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
D = 'C:/kyty/s288/s9/'

BODY = [
    ("""  Reading (item 355 (g)) by the scorer word: READ_1 - a series in pi_r1 and none in pi_r0 (a defect of S-pcw: iteration 2, B33
  not FIXED); READ_2 - no series in the four, or a series in both R, AND both R "Vulkan pipeline cache: loaded N bytes" = the
  last "saved N bytes" of their own W and 0 "disabled" (B33 FIXED, the count of track S, not a ship under (B)); READ_3 - a series
  only in pi_r0 (among the R arms) or only in the W arms (an effect of the scene [I], as (2)); READ_OTHER - any other outcome
  (decision S11);""",
     """  Reading (item 355 (g), item 362 (v)) by the scorer word: READ_1 - a series in pi_r1 and none in pi_r0 (a defect of S-pcw:
  iteration 2, B33 not FIXED); READ_2 - no series in the four, or a series in both R, AND both R "Vulkan pipeline cache: loaded N
  bytes" = the last "saved N bytes" of their own W and 0 "disabled" (B33 FIXED, the count of track S, not a ship under (B));
  READ_3 - a series only in pi_r0 (among the R arms: a series in pi_r0 and in a W arm with none in pi_r1 is READ_3, printed with
  a note) or only in the W arms, AND the loaded member of READ_2 on both R (item 362 (v): "as (2)" is the consequence and the
  condition; an effect of the scene [I], as (2)); without the loaded member -> READ_OTHER; the executor's reading (READ_3 without
  the loaded member) is printed beside ("reading of the executor ...", "DIFFERS (the loaded member)" when it differs);
  READ_OTHER - any other outcome (decision S11);"""),
    ("""  A T2 arm counts with its admission, its entry and the cold gate of item 241 (v)(7) by the LETTER (T2_GATE_READING = letter: a
  new permutation, a new recipe and a skipped draw after the entry line); the variant without the recipe member under
  KYTY_PIPELINE_PRECACHE=0 is printed beside ("variant gate: n").  T-4 under""",
     """  A T2 arm counts with its admission, its entry and the cold gate of item 241 (v)(7) as decided by item 362 (b)
  (T2_GATE_READING = p362): in the form C5 (KYTY_PIPELINE_PRECACHE=0) a new permutation, >= 1 in-game creation after the entry
  line (a line "AvTrace: pipeline " without the word "precache" with a " us=" field whose log line number is above the line
  "GuestOut: Level has started: L"; the count create_after of the gates) and a skipped draw after the entry line - the recipe
  member is replaced because PRECACHE=0 stops the recipe writer (4fc501f4 pipelineCache.cpp:5858); in the form APP by the letter
  (a new permutation, a new recipe and a skipped draw).  Beside per T2 arm and in the counts: "by the letter (with the recipe)"
  and "executor variant" (the recipe member dropped with no replacement, rejected by item 362 (b)).  T-4 under"""),
    ("""the identity "scan_x rows = scan_s rows" (FAIL when broken).""",
     """the identities "scan_x rows = scan_s rows" and "scan_x lines = scan_s lines" (the line numbers of the creations, item 362 (b);
  FAIL when broken)."""),
]

TAIL = """## 6. Executor variants and the decisions of item 362 (ROADMAP "SESSION 122" item 362, KytyPS5 a1f02bd5; the questions V1 - V10 of the S9 report and of seal 05_s section 6)

- V1 (the cold gate in the form C5) - DECIDED by item 362 (b): KYTY_PIPELINE_PRECACHE=0 stops the recipe writer
  (4fc501f4:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5858, anchor "if (!PipelinePrecacheEnabled() ||
  !m_program_cache->translation_cache.Enabled()) {", control +1 "return;"), so in the form C5 the member ">= 1 new recipe" is
  replaced by ">= 1 in-game creation after the line Level has started: L" (a line "AvTrace: pipeline " without the word
  "precache" with a " us=" field; the order by the log line number); the members new permutation and skipped draw by the letter;
  in the form APP the whole gate by the letter.  This seal counts by it (T2_GATE_READING = p362); the rows "by the letter (with
  the recipe)" and "executor variant" (the two members without a replacement - rejected) are printed beside per T2 arm and in
  the counts.
- V2 (T-4 under PRECACHE=0) - accepted by item 362 (g): 0 precache lines and no queued line is the identity.
- V3 (the T2 list) - accepted by item 362 (g): the pool (A) of C:/kyty/s146/step0/lvl146.py in map order; t2_1 hero_kratos,
  t2_2 hero_drake, t2_3 voxel_challenge_3, t2_4 armadillo_challenge_2, t2_5 fragile_battle_4, reserves t2_6 .. t2_10
  voxel_challenge_4, fragile_battle_5, voxel_challenge_5, miniboss_challenge_genie, symbol_triangle; the .xz files of HPP-401
  are not read.
- V4 (the U list) - accepted by item 362 (g): "an arm with a return" = a log under C:/kyty/s288, f287, p283, play or the
  emulator folder; u_1 underwater_aerial_garden, u_2 hoover_beach, u_3 robot_builder_next, u_4 interactive_credit_00, u_5
  fragile_battle_1; mini_giants_garden is not in the catalogue (by the letter of item 355 (e)).
- V5 (the export) - accepted by item 362 (g): the export from the byte-equal staging copy s9/stage/PPSA21564 is not a code
  change and was made in S9; the step "export" of S10 is the catalogue check by the manifest before every U arm.
- V6 (t2_cs0 order) - accepted by item 362 (g): right after t2_1.
- V7 (binary of c5_0 and T2) - accepted by item 362 (g): f3b3aa3b with the snapshot snap0 (translation signature 699c1e4b); the
  BvhLoopCapTrip column is for this binary.
- V8 (holds and timeouts) - accepted by item 362 (g): W hold 330, stable / timeout as in section 3; stable draws / timeouts pi
  300 / 480, c5_0 and T2 100 / 480, u 100 / 600.
- V9 (READ_3) - DECIDED by item 362 (v): a series in pi_r0 and in a W arm with none in pi_r1 is READ_3 (the executor's reading
  accepted; printed with a note); "as (2)" of item 355 (g)(3) is the consequence AND the condition: READ_3 needs the loaded
  member of (2) on both R ("Vulkan pipeline cache: loaded N bytes" = the last "saved N bytes" of their own W and 0 "disabled"),
  without it READ_OTHER (decision S11).  The executor's reading (no loaded member) is printed beside.
- V10 (the screen time) - accepted by item 362 (g): from the Popen of the emulator, an upper bound by at most one poll of 0.5 s.

## 7. Not claimed (item 355 (m), item 362 (z))

- FIXED B33; that the event of pcw_int is an effect of the game or a defect; that the cache write causes the entry freezes; where
  the warmth of the driver lives; that the salt or the return neutralises the driver cache before the C5 reading; that the
  replaced member of the gate equals the recipe member in strength; that the runs of test_go_s9.py distorted hv_2; that the
  entry freezes are caused by the shaders; that the corpus or the catalogue is complete; that shaders get faster on the GPU;
  that the harness runs the S10 path inside the lock without an error (the path inside the lock ran on fixtures only); no number
  is a gain; 60 FPS is not promised; goal (B) does not change.
"""

MK = [
    ('"""mkseal_s05.py - track S, link S9 (HPP-431): writes the seal C:/kyty/s288/pred/05_s.md of link S10',
     '"""mkseal_s05b.py - track S, link S9 (HPP-431), rework 1 (item 362 (d)): writes the seal C:/kyty/s288/pred/05b_s.md of link S10'),
    ('    python C:/kyty/s288/s9/mkseal_s05.py\n', '    python C:/kyty/s288/s9/mkseal_s05b.py\n'),
    ("OUT = R + '/pred/05_s.md'", "OUT = R + '/pred/05b_s.md'"),
    ("""    w('# Seal 05_s - track S link S9 (HPP-431) for link S10: the repeat of integrity, C5, the T2 base with t2_cs0, the S-cat probe '
      '(ROADMAP "SESSION 122" item 355 (g)-(zh), (k))')""",
     """    w('# Seal 05b_s - track S link S9 (HPP-431), rework 1, for link S10: the repeat of integrity, C5, the T2 base with t2_cs0, the '
      'S-cat probe (ROADMAP "SESSION 122" item 355 (g)-(zh), (k); item 362)')"""),
    ("""    w('Written by C:/kyty/s288/s9/mkseal_s05.py (sha256 %s) at %s UTC, before any S10 arm.""",
     """    w('Written by C:/kyty/s288/s9/mkseal_s05b.py (sha256 %s) at %s UTC, before any S10 arm.  It replaces the seal pred/05_s.md '
      '(sha256 d56e2e645ca7f0be60266c25bfa87869e94c4f3e0e9146796625fda000605784, not changed): S10 goes by this seal (item 362 (d)).'
      '"""),
    ("sha(R + '/s9/mkseal_s05.py')", "sha(R + '/s9/mkseal_s05b.py')"),
    ("open(R + '/s9/seal05_body.md'", "open(R + '/s9/seal05b_body.md'"),
    ("open(R + '/s9/seal05_tail.md'", "open(R + '/s9/seal05b_tail.md'"),
    ("('mutants (counted full run)', R + '/s9/mut_sc_s9.txt', None)",
     "('mutants (counted full run of rework 1)', R + '/s9/mut_sc_s9b.txt', None)"),
    ("""    w('- mutant runs of the link (wall, s9/times.txt): screening full 181 s (mut_screen1.txt: 208 of 211, survivors cr_glc, ad_gp, '
      'tc_fail - fixtures F2, G3, K2 added), a refused --only run (the suite failed F2 before any mutant, ~10 s), screening --only '
      'of the three 41 s (mut_screen3.txt: 3 of 3), the counted full run 179 s (mut_sc_s9.txt) - in all about 411 s')""",
     """    w('- mutant runs of the link (wall, s9/times.txt): before rework 1 - screening full 181 s (mut_screen1.txt: 208 of 211), a '
      'refused --only run ~10 s, screening --only 41 s (mut_screen3.txt: 3 of 3), the counted full run of seal 05 179 s '
      '(mut_sc_s9.txt: 211 of 211); rework 1 (item 362) - screening --only of the 19 new and 12 changed mutants 56 s '
      '(rework1/mut_screen4.txt: 31 of 31), the counted full run 222 s (mut_sc_s9b.txt) - in all about 689 s of the 30 min budget')"""),
]


def rep(t, reps, name):
    for a, b in reps:
        n = t.count(a)
        if n != 1:
            raise SystemExit('NO MATCH (%d) in %s: %r' % (n, name, a[:100]))
        t = t.replace(a, b)
    t.encode('ascii')
    return t


def main():
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    body = rep(open(D + 'seal05_body.md', 'rb').read().decode('ascii'), BODY, 'body')
    mk = rep(open(D + 'mkseal_s05.py', 'rb').read().decode('ascii'), MK, 'mkseal')
    TAIL.encode('ascii')
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    open(D + 'seal05b_body.md', 'wb').write(body.encode('ascii'))
    open(D + 'seal05b_tail.md', 'wb').write(TAIL.encode('ascii'))
    open(D + 'mkseal_s05b.py', 'wb').write(mk.encode('ascii'))
    print('written seal05b_body.md seal05b_tail.md mkseal_s05b.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
