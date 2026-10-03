"""mk06.py - track S link S9b (HPP-458; ROADMAP "SESSION 122" item 371 (g)): makes s9/mkseal_s06.py, s9/seal06_body.md,
s9/seal06_tail.md from the files of seal 05b (which do not change).  Every replacement matches once.  LF, ASCII.  Refuses under
the lock.
    python C:/kyty/s288/s9b/mk06.py
"""
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
D = 'C:/kyty/s288/s9/'

BODY = [
    ("""  seal 04 + the preparation-screen times of the attempt (prep_created_s, prep_ready_s from the Popen, 0.5 s poll).
""",
     """  seal 04 + the preparation-screen times of the attempt (prep_created_s, prep_ready_s from the Popen, 0.5 s poll).  Item 371 (g)
  (RC1 of S9r): the guard s10/IN_ARM (the tag, the installed sha, man_pre_app, man_pre_glc) is written before the install and the
  restore and removed only by a successful return; while it exists go_s9.sh refuses rc 1 before the lock, as with RETURN_FAILED
  (a hard kill of an arm leaves it; the lead returns by hand and removes it).  Admission row installed_before = 4aa62e95 (the
  installed of item 342): in the harness inside the lock before the install (no arm otherwise, rc 1) and in the scorer
  (cache_rows); a change of the installed binary (for example FS3d HPP-450) stops S10 until a lead item names the new sha.
"""),
    ("""NOT_EVALUABLE - an arm missing, not admitted, not entered, without the video, a video < 3 000 frames or with a
  one-frame glitch, a death marker, or a W arm presented < 300 s.""",
     """NOT_EVALUABLE (item 371 (b)) - an arm missing, not admitted, not entered, a death marker, a W
  arm presented < 300 s, or the video member not met: the video read by the detector (haze not None) with frames after frame
  1 002 (frame numbers 0-based as in the detector: a video of <= 1 003 frames has none - NOT_EVALUABLE by the letter; fixtures
  1 002 / 1 003 / 1 004).  ">= 3 000 frames" and "0 one-frame glitches" are NOT members (item 371 (b)): the video frames, the
  present rows (FrameTrace rows) and the one-frame glitches are printed per arm as data for the lead sheet; the word of seal 05b
  with them as members is printed beside as the executor variant ("executor variant (seal 05b ...): W", "DIFFERS (video rule)"
  when it differs; fixture: a series in pi_r1 and 1 one-frame glitch in pi_w0 -> READ_1 by the letter, the variant
  NOT_EVALUABLE)."""),
    ("""go_s9.sh writes s10/haze_<tag>_<start>-<end>.png (frames start-2 .. end+2, at most 24).""",
     """go_s9.sh writes s10/haze_<tag>_<start>-<end>.png (frames start-2 .. end+2 clipped to the video; a
  series longer than 20 frames - 24 frames spread evenly over [start-2, end+2] with both ends, item 371 (g), RC5; the frame
  numbers are printed in haze_sheet_<tag>.txt)."""),
    ("""  >= 100 ms); the preparation screen = the later of prep_created_s ("PipelinePrecache: all pipelines created") and prep_ready_s
  ("ShaderPreparation: ready"), both printed, with the log values (created ms, startup wait ms).  KILLED - >= 2 of 5 arms fail or
  any screen > 180 s; ALIVE_BY_PROBE_5 - otherwise with every arm evaluable; UNDETERMINED - an arm not evaluable and no kill.""",
     """  >= 100 ms); the preparation screen = the later of prep_created_s ("PipelinePrecache: all pipelines created") and prep_ready_s
  ("ShaderPreparation: ready"), both printed, with the log values (created ms, startup wait ms).  Item 371 (v): without both
  lines the screen has a lower bound - the maximum of elapsed_ms of the log lines "ShaderPreparation: progress ...
  elapsed_ms=N" (4414e235:src/graphics/presentation/window/window.cpp:1015; the elapsed time of the startup wait loop, so a
  lower bound of the screen from the process start) and, when the attempt ended by timeout, the --timeout of the arm (600 s);
  a bound > 180 s is the kill member, printed "screen > N s (lower bound)"; an arm with neither both lines nor a bound > 180 s
  is NOT an S-cat member (its failure does not count; printed "the screen undetermined, not an S-cat member").  KILLED - >= 2
  of 5 member arms fail or any screen (measured or lower bound) > 180 s; UNDETERMINED - no kill and an arm not evaluable or an
  arm without a screen measure; ALIVE_BY_PROBE_5 - otherwise.  Beside it: the word by the letter of item 355 (e) ("else
  alive": an arm without a screen measure counted alive, its failure counted; "DIFFERS (screen undetermined)") and the executor
  variant (a failing arm without a screen measure counted among the failing; "DIFFERS (a failing arm without a screen
  measure)").  RC4: the line of every U arm carries, beside its S-cat member, stdout Shaders: (new translations), rec_new_after,
  perm_after and the skip lines after the first scene frame - data for S11, the reading does not change.  RC6: the line "Cache
  test mode: prepare-cold" was not observed on a real run; the first U is also the check of the gate.  No probe arm is made; a
  gate refusal on u_1 (CATALOGUE NOT INSTALLED) stops the U series (rc 6) with a question to the lead; that attempt is a form
  interference, not counted among the S-cat arms; a repeat only by a lead item (item 371 (g), item 355 (e))."""),
]

TAIL = """## 6. Executor variants and the decisions of items 362 and 371 (ROADMAP "SESSION 122" item 371, KytyPS5 dcc6cbf8; item 362, KytyPS5 a1f02bd5)

Item 371 (the review S9r, HPP-432, docs/track-s/s9r-review.md at df2b3179: SOUND_WITH_CHANGES, RC1 - RC6 accepted):
- (b) RC3 - DECIDED: ">= 3 000 frames" and "0 one-frame glitches" are not members of the reading of the repeat of integrity
  (item 355 (g)); the video member of a pi arm = the video read by the detector (haze not None) with frames after frame 1 002;
  the video frames, the present rows and the one-frame glitches are data per arm; the word of seal 05b is printed beside as the
  executor variant with "DIFFERS (video rule)".  The other members of the readable arm (admission, identities, entry, death
  markers, the W hold of 300 s) by the letter, unchanged.
- (v) the amendment of the U reading of item 355 (e) (RC2) - DECIDED: the lower bound of the screen (progress elapsed_ms, the
  --timeout on a timeout outcome); > 180 s - the kill member, "screen > N s (lower bound)"; an arm with neither both lines nor
  a bound > 180 s is not an S-cat member: UNDETERMINED with >= 1 such arm and < 2 failing; the letter word printed beside with
  "DIFFERS (screen undetermined)"; an arm with a death marker still stops the series (item 355 (k)).
  Executor variant (a question to the lead, printed beside): "< 2 failing" is read here as < 2 failing MEMBER arms (a
  non-member's failure does not count, by "is not an S-cat member"); the reading that counts a failing arm without a screen
  measure among the failing is printed beside ("executor variant ...", "DIFFERS (a failing arm without a screen measure)").
  Neither reading can turn a kill into ALIVE_BY_PROBE_5.
- (g) RC1 - the guard s10/IN_ARM and the admission row installed_before = 4aa62e95 in the harness and the scorer (section 1);
  RC4 - the data per U arm; RC5 - the sheet of a long series; RC6 - this seal line: the line "Cache test mode: prepare-cold"
  was not observed on a real run; the first U is also the check of the gate; a gate refusal on u_1 - stop of the U series and a
  question to the lead, the attempt a form interference, not an S-cat arm, a repeat only by a lead item.
- (e)(2) this link ran no command longer than 60 s while a run series of another track was going (its runs link in_progress
  with an executionRunId); the waits are rows of s9b/times.txt.

Item 362 (unchanged; the questions V1 - V10 of the S9 report and of seal 05_s section 6):
- V1 (the cold gate in the form C5) - DECIDED by item 362 (b): KYTY_PIPELINE_PRECACHE=0 stops the recipe writer
  (4fc501f4:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5858), so in the form C5 the member ">= 1 new recipe" is
  replaced by ">= 1 in-game creation after the line Level has started: L"; the members new permutation and skipped draw by the
  letter; in the form APP the whole gate by the letter (T2_GATE_READING = p362; the letter and the executor variant beside).
- V2 (T-4 under PRECACHE=0), V3 (the T2 list), V4 (the U list), V5 (the export), V6 (t2_cs0 right after t2_1), V7 (f3b3aa3b
  with snap0 for c5_0 and T2), V8 (holds and timeouts: pi 300 / 480, c5_0 and T2 100 / 480, u 100 / 600), V10 (the screen time
  from the Popen, an upper bound by one poll of 0.5 s) - accepted by item 362 (g), as in seal 05b.
- V9 (READ_3) - DECIDED by item 362 (v): READ_3 needs the loaded member of (2) on both R, else READ_OTHER; a series in pi_r0
  and in a W arm with none in pi_r1 is READ_3 with a note; the executor's reading (no loaded member) printed beside.

## 7. Not claimed (item 355 (m), item 362 (z), item 371 (z))

- FIXED B33; that the event of pcw_int is an effect of the game or a defect; that the cache write causes the entry freezes; where
  the warmth of the driver lives; that the salt without precache neutralises the driver cache before the C5 reading; that the
  replaced member of the gate equals the recipe member in strength; that the gate prepare-cold fires on a real run; that the
  corpus or the catalogue is complete; that the .xz files hold no entry of a T2 level ([I]); that the entry freezes are caused by
  the shaders; that shaders get faster on the GPU; that the harness runs the S10 path inside the lock without an error (the path
  inside the lock ran on fixtures only); no number is a gain; 60 FPS is not promised; goal (B) does not change.
"""

MK = [
    ('"""mkseal_s05b.py - track S, link S9 (HPP-431), rework 1 (item 362 (d)): writes the seal C:/kyty/s288/pred/05b_s.md of link S10',
     '"""mkseal_s06.py - track S, link S9b (HPP-458; item 371 (g)): writes the seal C:/kyty/s288/pred/06_s.md of link S10'),
    ('    python C:/kyty/s288/s9/mkseal_s05b.py\n', '    python C:/kyty/s288/s9/mkseal_s06.py\n'),
    ("OUT = R + '/pred/05b_s.md'", "OUT = R + '/pred/06_s.md'"),
    ("""    w('# Seal 05b_s - track S link S9 (HPP-431), rework 1, for link S10: the repeat of integrity, C5, the T2 base with t2_cs0, the '
      'S-cat probe (ROADMAP "SESSION 122" item 355 (g)-(zh), (k); item 362)')""",
     """    w('# Seal 06_s - track S link S9b (HPP-458) for link S10: the repeat of integrity, C5, the T2 base with t2_cs0, the S-cat '
      'probe (ROADMAP "SESSION 122" item 355 (g)-(zh), (k); items 362, 371)')"""),
    ("""    w('Written by C:/kyty/s288/s9/mkseal_s05b.py (sha256 %s) at %s UTC, before any S10 arm.  It replaces the seal pred/05_s.md '
      '(sha256 d56e2e645ca7f0be60266c25bfa87869e94c4f3e0e9146796625fda000605784, not changed): S10 goes by this seal (item 362 (d)).'""",
     """    w('Written by C:/kyty/s288/s9/mkseal_s06.py (sha256 %s) at %s UTC, before any S10 arm.  It replaces the seal pred/05b_s.md '
      '(sha256 6641154ecb5cec89102c0c4b4af607d7d723f69e294ef7598d08a2d9804dcd81, not changed; it replaced pred/05_s.md '
      'd56e2e645ca7f0be60266c25bfa87869e94c4f3e0e9146796625fda000605784): S10 goes by this seal (item 371 (g)).'"""),
    ("sha(R + '/s9/mkseal_s05b.py')", "sha(R + '/s9/mkseal_s06.py')"),
    ("open(R + '/s9/seal05b_body.md'", "open(R + '/s9/seal06_body.md'"),
    ("open(R + '/s9/seal05b_tail.md'", "open(R + '/s9/seal06_tail.md'"),
    ("('mutants (counted full run of rework 1)', R + '/s9/mut_sc_s9b.txt', None)",
     "('mutants (the counted full run of S9b)', R + '/s9/mut_sc_s9c.txt', None)"),
    ("""    w('- mutant runs of the link (wall, s9/times.txt): before rework 1 - screening full 181 s (mut_screen1.txt: 208 of 211), a '
      'refused --only run ~10 s, screening --only 41 s (mut_screen3.txt: 3 of 3), the counted full run of seal 05 179 s '
      '(mut_sc_s9.txt: 211 of 211); rework 1 (item 362) - screening --only of the 19 new and 12 changed mutants 56 s '
      '(rework1/mut_screen4.txt: 31 of 31), the counted full run 222 s (mut_sc_s9b.txt) - in all about 689 s of the 30 min budget')""",
     """    w('- mutant runs (wall): ' + open(R + '/s9b/mutwalls.txt', encoding='ascii').read().strip())"""),
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
    body = rep(open(D + 'seal05b_body.md', 'rb').read().decode('ascii'), BODY, 'body')
    mk = rep(open(D + 'mkseal_s05b.py', 'rb').read().decode('ascii'), MK, 'mkseal')
    TAIL.encode('ascii')
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    open(D + 'seal06_body.md', 'wb').write(body.encode('ascii'))
    open(D + 'seal06_tail.md', 'wb').write(TAIL.encode('ascii'))
    open(D + 'mkseal_s06.py', 'wb').write(mk.encode('ascii'))
    print('written seal06_body.md seal06_tail.md mkseal_s06.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
