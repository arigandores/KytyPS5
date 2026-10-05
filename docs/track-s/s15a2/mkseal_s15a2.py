"""mkseal_s15a2.py - track S, link S15a2 (HPP-615; ROADMAP "SESSION 122" item 528 (b)(4)): writes the seal C:/kyty/s288/pred/15_s.md
from the seal C:/kyty/s288/pred/14_s.md (pinned by sha256) by exact replacements, every anchor exactly once: the title, the line
"Written by", the bullet THE U HOLD (item 528 (b)(1), (c)), the sha256 lines of s15/enter_scene_s15.py, s15/mk_enter_s15.py,
s15/test_enter_scene_s15.py, s15/hmut_s15.py (read now), and two bullets of section 6 (S15a2: the code, its fixtures and mutants;
the reading of item 528 (b)(5)).  Every other line of seal 14 is kept byte for byte.  Refuses (rc 5) when the lock exists, (rc 1)
when the seal 15 exists (a seal is never rewritten), when seal 14 is not the pinned one or when sc_s15.py / go_s15.sh are not the
sealed ones (item 528 (b)(3): sc_s15.py does not change).  LF, ASCII.
    python mkseal_s15a2.py <test_enter_scene_s15.out.txt> <hmut_enter.out.txt> <negctl.out.txt>
"""
import hashlib
import os
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
ROOT = 'C:/kyty/s288'
OLD = ROOT + '/pred/14_s.md'
OLD_SHA = '9a810237993b4700be86dc0bac38ad7bff05d27e68f1f8555cc7f9b17c241a83'
SEAL = ROOT + '/pred/15_s.md'
KEEP = {'s15/sc_s15.py': '6b3ad9c411f7053053278bf00579076d902d0c6796bcd650a6b5ddac896438b4',
        's15/go_s15.sh': 'f5c1b67ce6449c85a7af18a3df897c0e882ae8ddee2f02b3aa1e568ab6a8687a'}
CHANGED = ('s15/enter_scene_s15.py', 's15/mk_enter_s15.py', 's15/test_enter_scene_s15.py', 's15/hmut_s15.py')
NL = chr(10)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    if os.path.exists(LOCK):
        print('LOCKED - nothing written')
        return 5
    if os.path.exists(SEAL):
        print('STOP: %s exists - a seal is never rewritten' % SEAL)
        return 1
    if sha(OLD) != OLD_SHA:
        print('STOP: %s sha256 %s != %s' % (OLD, sha(OLD), OLD_SHA))
        return 1
    for n, want in KEEP.items():
        if sha(ROOT + '/' + n) != want:
            print('STOP: %s changed (%s != %s)' % (n, sha(ROOT + '/' + n), want))
            return 1
    test_out, hmut_out, neg_out = sys.argv[1:4]
    t = open(OLD, 'rb').read().decode('ascii')
    lines = t.split(NL)
    now = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    written_old = [x for x in lines if x.startswith('Written by C:/kyty/s288/s15/mkseal_s15.py ')]
    if len(written_old) != 1:
        print('STOP: the line "Written by" of seal 14 occurs %d times' % len(written_old))
        return 1
    written_new = (
        'Written by C:/kyty/s288/s15a2/mkseal_s15a2.py (sha256 %s) at %s by link S15a2 (HPP-615), before any arm of S15b.  Seal 14 '
        '(pred/14_s.md sha256 %s, link S15a, HPP-601) with the changes of ROADMAP "SESSION 122" item 528 (b)(1)-(5), (c) only: the '
        'title and this line; the bullet THE U HOLD (the cause "error <type name>" of item 528 (b)(1), the anchor "entry" of item 528 '
        '(c)); the sha256 lines of s15/enter_scene_s15.py, its generator s15/mk_enter_s15.py, its fixtures s15/test_enter_scene_s15.py '
        'and its hand mutants s15/hmut_s15.py; two bullets of section 6 (S15a2; the reading of item 528 (b)(5)).  Every other line of '
        'seal 14 is kept byte for byte - also the names pred/14_s.md and pred/14b_s.md, which the unchanged code reads (sc_s15.py '
        'SEAL_BASE / SEAL_B / SEAL_BASE_REL, the seal-path case of go_s15.sh; item 528 (b)(3): sc_s15.py does not change): the edition '
        'named by item 528 (d) is pred/15b_s.md, and until a lead item says how the code reaches this seal, go_s15.sh checks seal 14, '
        'which FAILS on the new sha256 of enter_scene_s15.py, and refuses every tag ("seal check failed", rc 1) - a question of S15a2 '
        'to the lead.  After this seal the scorer, the fixtures, the mutants, the harness, enter_scene_s15.py, the export and the list '
        'do not change (a change = a new seal).  S15b runs only after the narrow review S15r2 and the lead line accepting this seal, '
        'after FS8e (HPP-575) and the edition.  ASCII only.' % (sha(os.path.abspath(__file__)), now, OLD_SHA))
    hold_old_start = '- THE U HOLD (item 511 (z)(4)): '
    hold_next = '- THE W ARM w13 (item 229 (e)(3)): '
    i = [k for k, x in enumerate(lines) if x.startswith(hold_old_start)]
    j = [k for k, x in enumerate(lines) if x.startswith(hold_next)]
    if len(i) != 1 or len(j) != 1 or j[0] <= i[0]:
        print('STOP: the bullet THE U HOLD: %d starts, %d next bullets' % (len(i), len(j)))
        return 1
    hold_new = [
        '- THE U HOLD (item 511 (z)(4); item 528 (b)(1), (c)): after "stable" (enter_scene: 90 rows with draws >= 100 after the entry',
        '  line, unchanged) a U arm is held while the presented time after the first scene frame (the sum of dt_us of the FrameTrace rows',
        '  after it - the rows the scorer counts; the first scene frame as sc_s.locate finds it) is < 120 s OR the video holds < 3 000',
        '  frames, but not longer than 300 s of presented time after the first scene frame.  An arm with the entry line of its level and',
        '  without a first scene frame (ps_logo, item 511 (z)(5)) is held by the presented time of the FrameTrace rows from the entry line',
        '  (the anchor "entry" of UHold) - A DECISION OF THE LEAD, item 528 (c) (variant (d) of the lead), not an executor\'s variant:',
        '  "met" - presented from the entry line >= 120 s and the video >= 3 000 frames; "cap" - presented from the entry line >= 300 s;',
        '  the wall 300 + 60 s (item 526 (b)(1)); the anchor "fi" of an arm with a first scene frame does not change; S15b, the audit and',
        '  S15c read the hold of such an arm by item 528 (c).  The video frames are the complete lines of rec_<tag>.mp4.idx (the emulator',
        '  writes and flushes one line per recorded frame: screenshot.cpp; S13b: index lines = the frames of the video, 19 of 19).  The',
        '  hold ends "met" (both conditions), "cap" (300 s presented), "game ended" (the process exits - E3-death reads hold_exit),',
        '  "wall cap" (300 + 60 s of wall time from the start of the hold - a game that stops presenting) or "error <type name>" (item 528',
        '  (b)(1): a call of UHold.poll() in the hold loop or after it raised - both calls are in try/except Exception; UHold is not',
        '  polled again, the hold ends at once and the usual path follows: hold_end, ft_*, hold_exit, close_game; the line "U hold:',
        '  UHold.poll() raised <type>: <text>" in the output of the arm).  A video below 3 000 frames at the end of the hold is E3-video',
        '  FAIL by the letter (unchanged member).  <tag>.json carries hold_rule = {min_shown_s 120, video_frames 3000, cap_s 300,',
        '  wall_extra_s 60, scene_draws 100} (an admission row "before the run": the U arm carries exactly this rule, a k arm and w13',
        '  carry none); the attempt carries hold_end {cause, anchor fi / entry, shown_us, video_frames, rows, entry_rows, first_row,',
        '  closed} - a data line per U arm ("hold end (item 511 (z)(4), data)"), no member reads it; a cause beginning with "error" is',
        '  read by item 528 (b)(5) (section 6, READING OF ITEM 528 (b)(5)).',
    ]
    lines = lines[:i[0]] + hold_new + lines[j[0]:]
    lines = [written_new if x == written_old[0] else x for x in lines]
    title_old = '# Seal 14_s - track S link S15b (HPP-603): '
    k = [n for n, x in enumerate(lines) if x.startswith(title_old)]
    if len(k) != 1 or k[0] != 0:
        print('STOP: the title of seal 14: %s' % k)
        return 1
    lines[0] = '# Seal 15_s - track S link S15b (HPP-603): ' + lines[0][len(title_old):]
    for n in CHANGED:
        s = [m for m, x in enumerate(lines) if x.startswith('seal: ') and x.endswith(' ' + n)]
        if len(s) != 1:
            print('STOP: the seal line of %s occurs %d times' % (n, len(s)))
            return 1
        lines[s[0]] = 'seal: %s %s' % (sha(ROOT + '/' + n), n)
    anchor6 = '  number); outputs s15/hmut/hmut_<id>.txt, the summary lines in s15/hmut_enter.out.txt and s15/hmut_go.out.txt.'
    a6 = [m for m, x in enumerate(lines) if x == anchor6]
    if len(a6) != 1:
        print('STOP: the anchor of section 6 occurs %d times' % len(a6))
        return 1
    tx = open(test_out, 'rb').read().decode('ascii', 'replace')
    hx = open(hmut_out, 'rb').read().decode('ascii', 'replace')
    nx = open(neg_out, 'rb').read().decode('ascii', 'replace')
    if not tx.rstrip().endswith('ALL OK') or 'HMUT enter: 21 of 21 killed' not in hx:
        print('STOP: the suite is not ALL OK or the hand mutants are not 21 of 21 killed')
        return 1
    nfail = sorted(x.split(' ')[1] for x in nx.splitlines() if x.startswith('FAIL '))
    if nfail != ['H7', 'H8', 'M1', 'U15']:
        print('STOP: the negative control fails %s, not H7, H8, M1, U15' % nfail)
        return 1
    checks = [x for x in tx.splitlines() if x.startswith('checks: ')]
    sec6 = [
        '- S15a2, item 528 (b)(1)-(3) (HPP-615): both calls of UHold.poll() of the hold in try/except Exception (enter_scene_s15.py',
        '  u_error, written by the patched mk_enter_s15.py - U15 byte for byte); fixtures of test_enter_scene_s15.py: H7 - the torn row of',
        '  the probe P1 of S15r ("FrameTrace: n=6GuestOut: x dt_us=30000 draws=3000") written by a stand-in emulator, the hold loop ->',
        '  the cause "error ValueError", no poll after the exception, close_game called once and the game closed, hold_exit recorded;',
        '  H8 - the same row met by the poll after the loop; M1 - main() with that stand-in -> no exception out of main, <tag>.json full',
        '  (the attempt with hold_end, hold_exit, ft_total, hold_s; ft_total and hold_rule of the json).  The suite: %s, ALL OK' % (
            checks[-1] if checks else '?'),
        '  (s15/test_enter_scene_s15.out.txt sha256 %s); the negative control - the suite on enter_scene_s15.py of seal 14' % sha(
            test_out),
        '  (sha256 14fe343ee44c30b9a1351245189befd1b39998af8f4c933f1cc6e252a4e3f9ec) fails H7, H8, M1 and U15 (s15a2/negctl.out.txt',
        '  sha256 %s); the hand mutants s15/hmut_s15.py enter: 21 of 21 killed - e01-e18 of S15a and e19 the except of' % sha(neg_out),
        '  the loop, e20 the except after the loop, e21 the name of the cause (s15/hmut_enter.out.txt sha256 %s);' % sha(hmut_out),
        '  sc_s15.py unchanged (sha256 6b3ad9c411f7053053278bf00579076d902d0c6796bcd650a6b5ddac896438b4) - no full mutant run of the',
        '  scorer (item 528 (b)(3)); go_s15.sh unchanged - its hand mutants not rerun.',
        '- READING OF ITEM 528 (b)(5) (a rule of the lead): an arm whose hold_end.cause begins with "error" or whose <tag>.stdout.txt',
        '  ends with an exception trace is a run interference: a repeat of the tag is set by a lead item and does not count in the',
        '  attempts of the level (Process p. 1 of the audit of session 144); the series goes on only after a line of times.txt that no',
        '  process kyty_emulator.exe is there and the caches, GLCache and the binary are returned by sha and manifest.',
    ]
    lines = lines[:a6[0] + 1] + sec6 + lines[a6[0] + 1:]
    text = NL.join(lines)
    text.encode('ascii')
    if os.path.exists(LOCK):
        print('LOCKED before the write - nothing written')
        return 5
    with open(SEAL, 'w', encoding='ascii', newline=NL) as f:
        f.write(text)
    print('SEAL %s sha256 %s lines %d (from %s %s)' % (SEAL, sha(SEAL), text.count(NL), OLD, OLD_SHA[:16]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
