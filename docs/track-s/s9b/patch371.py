"""patch371.py - track S link S9b (HPP-458; ROADMAP "SESSION 122" item 371 (b)-(g)): RC1-RC6 of S9r in s9/go_s9.sh, s9/sc_s9.py,
s9/test_sc_s9.py, s9/test_go_s9.py, s9/mut_sc_s9.py.  Every replacement matches exactly once (REPALL - every match, at least one).
Originals are copied to C:/kyty/s288/s9b/orig/ first.  LF, ASCII.  Refuses under the lock.
    python C:/kyty/s288/s9b/patch371.py
"""
import os
import shutil
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
D = 'C:/kyty/s288/s9/'
ORIG = 'C:/kyty/s288/s9b/orig/'
REPALL = object()

GO = [
    (r'''#   BINARIES: the seal lines "s binary: <sha> <path>" (f3b3aa3b) and "u binary: <sha> <path>" (4aa62e95) of pred/05b_s.md (item 362 (d)).
''',
     r'''#   BINARIES: the seal lines "s binary: <sha> <path>" (f3b3aa3b) and "u binary: <sha> <path>" (4aa62e95) of pred/06_s.md (item 371 (g)).
#   GUARD s10/IN_ARM (item 371 (g), RC1 of S9r): written before INSTALLED=1 / TOUCHED=1 (the tag, the installed sha, man_pre_app,
#     man_pre_glc), removed only by a successful do_return; while it exists go_s9.sh refuses rc 1 as with RETURN_FAILED (a hard kill
#     of an arm leaves it; the lead returns by hand).  ADMISSION: the installed binary before the arm = INST_WANT (4aa62e95, item
#     342), else no arm (rc 1) - a new installation stops S10 until a lead item names the new sha.
'''),
    ('PRED=pred/05b_s.md\n',
     'PRED=pred/06_s.md\nINST_WANT="4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac"\n'),
    (r'''for G in $ROOT/s4/RETURN_FAILED $ROOT/s6/RETURN_FAILED $ROOT/s10/RETURN_FAILED; do
  if [ -e $G ]; then
    GT=""
    read -r GT < $G 2>/dev/null
    log0 "go_s9.sh $T refused (rc 1): the guard $G exists ($GT) - the lead removes it after the return by hand"
    echo "return failed guard $G: $GT"; exit 1
  fi
done
''',
     r'''guardfiles() {
  for G in $ROOT/s4/RETURN_FAILED $ROOT/s6/RETURN_FAILED $ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM; do
    if [ -e $G ]; then
      GT=""
      read -r GT < $G 2>/dev/null
      log0 "go_s9.sh $T refused (rc 1): the guard $G exists ($GT) - the lead removes it after the return by hand"
      echo "return failed guard $G: $GT"; exit 1
    fi
  done
}
guardfiles
'''),
    (r'''if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi
''',
     r'''if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi
guardfiles
'''),
    ('(go_s9.sh seal 05b)', '(go_s9.sh seal 06)'),
    ('INSTALLED=0\nTOUCHED=0\nRETURNED=0\n', 'INSTALLED=0\nTOUCHED=0\nRETURNED=0\nINARM_MINE=0\n'),
    (r'''  [ "$rc" = "0" ] || return_failed $rc
  return $rc
}
''',
     r'''  [ "$rc" = "0" ] || return_failed $rc
  if [ "$rc" = "0" ] && [ "$INARM_MINE" = "1" ] && [ "$INSTALLED" = "0" ] && { [ "$TOUCHED" = "0" ] || [ "$RETURNED" = "1" ]; }; then
    rm -f $LD/IN_ARM && INARM_MINE=0 && tline "guard $LD/IN_ARM removed after the successful return"
  fi
  return $rc
}
'''),
    (r'''tline "installed binary before the arm: $INST_SHA copied to $BINPRE"
INSTALLED=1
''',
     r'''tline "installed binary before the arm: $INST_SHA copied to $BINPRE"
if [ "$INST_SHA" != "$INST_WANT" ]; then
  log "the installed binary before the arm $INST_SHA != the installed of item 342 $INST_WANT - no arm (item 371 (g))"
  tline "installed binary before the arm $INST_SHA != $INST_WANT (item 342) - no arm; S10 stands until a lead item names the new sha"
  INST_SHA=""; echo "installed binary not $INST_WANT"; exit 1
fi
X=$($CX man app 2>&1); log "$X"; MPA=$(shaof "$X"); $CX note $CJ man_pre_app sha=$MPA >> $L 2>&1
X=$($CX man glc 2>&1); log "$X"; MPG=$(shaof "$X"); $CX note $CJ man_pre_glc sha=$MPG >> $L 2>&1
if ! { echo "IN_ARM $T $(date -u +%Y-%m-%dT%H:%M:%SZ) pid $$ - an arm is inside the lock; a successful return removes this file"
       echo "installed: $INST_SHA (copy $BINPRE)"
       echo "man_pre_app: $MPA (copy $LD/installed_pre after this line)"
       echo "man_pre_glc: $MPG (copy $LD/glc_pre after this line)"; } > $LD/IN_ARM; then
  log "the guard $LD/IN_ARM not written - no arm"; echo "IN_ARM not written"; exit 1
fi
INARM_MINE=1
tline "guard $LD/IN_ARM written (installed $INST_SHA, man_pre_app $MPA, man_pre_glc $MPG) before the install"
INSTALLED=1
'''),
    (r'''X=$($CX man app 2>&1); log "$X"; $CX note $CJ man_pre_app sha=$(shaof "$X") >> $L 2>&1
X=$($CX man glc 2>&1); log "$X"; $CX note $CJ man_pre_glc sha=$(shaof "$X") >> $L 2>&1
X=$($CX copy app $LD/installed_pre --replace 2>&1)''',
     r'''X=$($CX copy app $LD/installed_pre --replace 2>&1)'''),
]

SC = [
    (r'''             member) printed beside.
  --read-c5''',
     r'''             member) printed beside.  Item 371 (b): an arm is read with its admission, its entry, no death marker and the video
             member = the video read by the detector (haze not None) with frames after frame 1 002 (0-based: >= 1 004 frames);
             the video frames, the present rows and the one-frame glitches are data per arm; the word of seal 05b (+ >= 3 000
             frames and 0 one-frame glitches as members) is printed beside as the executor variant ("DIFFERS (video rule)").
  --read-c5'''),
    (r'''             >= 2 of 5 arms fail or a screen > 180 s, else ALIVE_BY_PROBE_5 (UNDETERMINED while an arm is not evaluable).
''',
     r'''             >= 2 of 5 arms fail or a screen > 180 s, else ALIVE_BY_PROBE_5 (UNDETERMINED while an arm is not evaluable).
             Item 371 (v): a screen without both lines has the lower bound max(elapsed_ms of "ShaderPreparation: progress",
             --timeout when the attempt ended by timeout); a bound > 180 s is the kill member ("screen > N s (lower bound)"); an
             arm with neither both lines nor a bound > 180 s is not an S-cat member: with >= 1 such arm and < 2 failing members
             the word is UNDETERMINED; the letter of item 355 (e) ("else alive") is printed beside ("DIFFERS (screen
             undetermined)"), and the executor variant counting a failing arm without a screen measure ("DIFFERS (a failing arm
             without a screen measure)").  RC4: per U arm stdout Shaders:, rec_new_after, perm_after and the skip lines after the
             first scene frame (data, item 371 (g)).  The lead sheet of a series longer than 20 frames: 24 frames spread evenly
             over [start-2, end+2] (RC5).
'''),
    ("PRED_PATH = 'C:/kyty/s288/pred/05b_s.md'                       # item 362 (d)",
     "PRED_PATH = 'C:/kyty/s288/pred/06_s.md'                        # item 371 (g)"),
    ("HAZE_AFTER = 1002\nFFMPEG = 'ffmpeg'\n",
     "HAZE_AFTER = 1002\nSHEET_LONG = 20                  # item 371 (g), RC5: a series longer than 20 frames -> 24 frames spread evenly\n"
     "SHEET_N = 24\nFFMPEG = 'ffmpeg'\n"),
    (r'''def plan(spec):
    """One line for go_s9.sh: link level cls mode hold salt pcw src sdraws timeout pre0 cs0 u binkind form."""
    if spec['t2form'] and spec.get('form') not in ('c5', 'app'):
        return 'UNDETERMINED'
    sd, to = (300, 480) if spec['group'] == 'pi' else (100, 600 if spec['u'] else 480)
''',
     r'''def stable_timeout(spec):
    """(stable draws, --timeout s) of an arm: pi 300 / 480, u 100 / 600, the rest 100 / 480."""
    return (300, 480) if spec['group'] == 'pi' else (100, 600 if spec['u'] else 480)


def plan(spec):
    """One line for go_s9.sh: link level cls mode hold salt pcw src sdraws timeout pre0 cs0 u binkind form."""
    if spec['t2form'] and spec.get('form') not in ('c5', 'app'):
        return 'UNDETERMINED'
    sd, to = stable_timeout(spec)
'''),
    (r'''    len(scan_s rows)) and the line count (= scan_s lines) - identities of this scan."""
    r = dict(rows=0, lines=0, bvh=[], csp={}, gamepatch=0, create=[], create_nous=0, create_ln=[])
''',
     r'''    len(scan_s rows)) and the line count (= scan_s lines) - identities of this scan; the lines "ShaderPreparation: progress":
    their count and the maximum of their elapsed_ms (item 371 (v): the lower bound of the preparation screen)."""
    r = dict(rows=0, lines=0, bvh=[], csp={}, gamepatch=0, create=[], create_nous=0, create_ln=[], prog_ms=None, prog_n=0)
'''),
    (r'''            elif c0 == b'G':
                if line.startswith(b'GamePatch:'):
                    r['gamepatch'] += 1
''',
     r'''            elif c0 == b'G':
                if line.startswith(b'GamePatch:'):
                    r['gamepatch'] += 1
            elif c0 == b'S':
                if line.startswith(b'ShaderPreparation: progress '):
                    v = A.field(line.rstrip(), b'elapsed_ms')
                    r['prog_n'] += 1
                    if v is not None and (r['prog_ms'] is None or v > r['prog_ms']):
                        r['prog_ms'] = v
'''),
    (r'''        '%s / %s' % ((ia or '-')[:16], (ib or '-')[:16]))
''',
     r'''        '%s / %s' % ((ia or '-')[:16], (ib or '-')[:16]))
    add('installed binary before the arm = the installed %s of item 342 (item 371 (g), RC1)' % BIN_U[:8], ib == BIN_U,
        (ib or '-')[:16])
'''),
    ("    r['entered'] = eg is not None\n",
     "    r['entered'] = eg is not None\n    r['present_rows'] = len(s['rows'])\n"),
    ("seed_ignored=s['seed_ignored'], cache_test=sox['any'], prepare_cold=sox['prepare_cold'])",
     "seed_ignored=s['seed_ignored'], cache_test=sox['any'], prepare_cold=sox['prepare_cold'],\n"
     "                     prog_ms=sx['prog_ms'], prog_n=sx['prog_n'])"),
    (r'''def clean_arm(r):
    """Admitted, entered, video of >= 3 000 frames with 0 glitches and 0 death markers (the arm is readable)."""
    g = r.get('glitch') or {}
    return ok_arm(r) and r.get('entered') and r.get('video') and g.get('video_frames', 0) >= FRAMES_VIDEO and \
        g.get('glitches') == 0 and not r['marks'] and not r['ended'] and not r['exited']
''',
     r'''def clean_arm(r):
    """Item 371 (b): the arm is readable - admitted, entered, the video read by the detector (haze not None) with frames after
    frame 1 002 (0-based), no death marker; the video frames, the present rows and the one-frame glitches are data, not members."""
    h = r.get('haze')
    return ok_arm(r) and r.get('entered') and h is not None and h['frames'] - 1 > HAZE_AFTER and not r['marks'] and \
        not r['ended'] and not r['exited']


def clean_arm_x(r):
    """The executor variant of seal 05b (printed beside, item 371 (b)): admitted, entered, a video of >= 3 000 frames with 0
    one-frame glitches, read by the detector, no death marker."""
    g = r.get('glitch') or {}
    return ok_arm(r) and r.get('entered') and r.get('video') and g.get('video_frames', 0) >= FRAMES_VIDEO and \
        g.get('glitches') == 0 and not r['marks'] and not r['ended'] and not r['exited'] and r.get('haze') is not None


def video_rule_line(word, wordx):
    """Item 371 (b): the word of seal 05b printed beside."""
    return 'executor variant (seal 05b: + video >= %d frames and 0 one-frame glitches as members; not members by item 371 (b)): ' \
           '%s%s' % (FRAMES_VIDEO, wordx, '' if wordx == word else ' - DIFFERS (video rule)')
'''),
    (r'''    bad = [t for t in PI_ORDER if not clean_arm(rs[t]) or rs[t].get('haze') is None]
    hz = {}
    for t in PI_ORDER:
        h = rs[t].get('haze')
        hz[t] = None if h is None else bool(h['after'])
        out.append('%s: %s; video %s; haze frames %s median %s low %s series %s; after frame %d (letter: start > %d) %s; '
                   'variant (any frame > %d) %s' % (
                       t, 'clean' if clean_arm(rs[t]) else 'NOT clean (%s)' % (rs[t]['fail'] or 'video/markers'),
                       rs[t].get('glitch'), h and h['frames'], h and round(h['med'], 4), h and h['low'],
                       h and h['runs'], HAZE_AFTER, HAZE_AFTER, h and h['after'], HAZE_AFTER, h and h['after_var']))
    held = dict((t, rs[t]['derive142']['dt_after_first_us'] >= HOLD_W_US) for t in ('pi_w1', 'pi_w0'))
    out.append('W arms presented >= 300 s after the first scene frame: %s' % held)
    loaded = {}
    for rt, wt in PI_W.items():
        lb = rs[rt]['loaded']
        wb = rs[wt]['saves']['last_bytes']
        loaded[rt] = lb is not None and lb == wb and rs[rt]['prep']['disabled'] == 0
        out.append('%s loaded %s bytes = last write of %s %s, disabled %d -> %s' % (
            rt, lb, wt, wb, rs[rt]['prep']['disabled'], 'PASS' if loaded[rt] else 'FAIL'))
''',
     r'''    bad = [t for t in PI_ORDER if not clean_arm(rs[t])]
    bad_x = [t for t in PI_ORDER if not clean_arm_x(rs[t])]
    hz = {}
    for t in PI_ORDER:
        h = rs[t].get('haze')
        g = rs[t].get('glitch') or {}
        hz[t] = None if h is None else bool(h['after'])
        out.append('%s: %s (executor variant: %s); video frames %s, present rows %s, one-frame glitches %s; haze frames %s median %s '
                   'low %s series %s; after frame %d (letter: start > %d) %s; variant (any frame > %d) %s' % (
                       t, 'readable' if clean_arm(rs[t]) else 'NOT readable (%s)' % (rs[t]['fail'] or 'entry/video/markers'),
                       'readable' if clean_arm_x(rs[t]) else 'NOT readable', g.get('video_frames'), rs[t].get('present_rows'),
                       g.get('glitches'), h and h['frames'], h and round(h['med'], 4), h and h['low'], h and h['runs'],
                       HAZE_AFTER, HAZE_AFTER, h and h['after'], HAZE_AFTER, h and h['after_var']))
    held = dict((t, rs[t]['derive142']['dt_after_first_us'] >= HOLD_W_US) for t in ('pi_w1', 'pi_w0'))
    out.append('W arms presented >= 300 s after the first scene frame: %s' % held)
    loaded = {}
    for rt, wt in PI_W.items():
        lb = rs[rt].get('loaded')
        wb = (rs[wt].get('saves') or {}).get('last_bytes')
        dis = (rs[rt].get('prep') or {}).get('disabled')
        loaded[rt] = lb is not None and lb == wb and dis == 0
        out.append('%s loaded %s bytes = last write of %s %s, disabled %s -> %s' % (
            rt, lb, wt, wb, dis, 'PASS' if loaded[rt] else 'FAIL'))
'''),
    (r'''    var = dict((t, bool(rs[t]['haze']['after_var'])) if rs[t].get('haze') else (t, None) for t in PI_ORDER)
    if bad or not all(held.values()):
        out.append('arms not readable (admission, identity, entry, video, markers, haze, hold): %s' % (bad or 'hold'))
        return 'NOT_EVALUABLE', out
    word = pi_word(hz, loaded)
''',
     r'''    var = dict((t, bool(rs[t]['haze']['after_var'])) if rs[t].get('haze') else (t, None) for t in PI_ORDER)
    wordx = 'NOT_EVALUABLE' if bad_x or not all(held.values()) else pi_word(hz, loaded)
    if bad or not all(held.values()):
        out.append('arms not readable (admission, identity, entry, the video read by the detector with frames after %d, markers, '
                   'hold - item 371 (b)): %s' % (HAZE_AFTER, bad or 'hold'))
        out.append(video_rule_line('NOT_EVALUABLE', wordx))
        return 'NOT_EVALUABLE', out
    word = pi_word(hz, loaded)
'''),
    (r'''        wx, '' if wx == word else ' - DIFFERS (the loaded member)'))
''',
     r'''        wx, '' if wx == word else ' - DIFFERS (the loaded member)'))
    out.append(video_rule_line(word, wordx))
'''),
    (r'''def u_eval(r):
    """One U arm: (fails S-cat True / False / None undetermined, the gate word, the screen seconds or None, detail)."""
    if r is None:
        return None, 'not made', None, ''
    gates = r['prep']['seed_installed'] >= 1 and r['prep']['prepare_cold'] >= 1
    if not gates:
        return None, 'CATALOGUE NOT INSTALLED (ShaderSeed: installed %d, Cache test mode: prepare-cold %d) - not an S-cat ' \
                     'attempt, stop of the U series, a question to the lead' % (r['prep']['seed_installed'],
                                                                                 r['prep']['prepare_cold']), None, ''
    xs = [x for x in (r.get('prep_created_s'), r.get('prep_ready_s')) if x is not None]
    screen = max(xs) if len(xs) == 2 else None
    if not ok_arm(r) or not r.get('entered') or 'f1' not in r:
''',
     r'''def u_screen(r):
    """Item 355 (e), item 371 (v): (seconds, kind) of the preparation screen of a U arm.  'measured' - both lines seen: the later of
    prep_created_s and prep_ready_s (from the Popen); 'lower bound' - a line missing: the maximum of elapsed_ms of the lines
    "ShaderPreparation: progress" (the startup wait loop, 4414e235 window.cpp:1015) and, when the attempt ended by timeout, the
    --timeout of the arm; 'none' - neither."""
    if r is None:
        return None, 'none'
    xs = [x for x in (r.get('prep_created_s'), r.get('prep_ready_s')) if x is not None]
    if len(xs) == 2:
        return max(xs), 'measured'
    lb = []
    pm = (r.get('prep') or {}).get('prog_ms')
    if pm is not None:
        lb.append(pm / 1000.0)
    if r.get('attempt') == 'timeout':
        lb.append(float(stable_timeout(SPEC[r['tag']])[1]))
    return (max(lb), 'lower bound') if lb else (None, 'none')


def u_eval(r):
    """One U arm: (fails S-cat True / False / None undetermined, the gate word, (screen seconds, kind) of u_screen, detail)."""
    if r is None:
        return None, 'not made', (None, 'none'), ''
    p = r.get('prep') or {}
    gates = p.get('seed_installed', 0) >= 1 and p.get('prepare_cold', 0) >= 1
    if not gates:
        return None, 'CATALOGUE NOT INSTALLED (ShaderSeed: installed %d, Cache test mode: prepare-cold %d) - not an S-cat ' \
                     'attempt (a form interference, not counted among the S-cat arms, a repeat only by a lead item, item 371 ' \
                     '(g)), stop of the U series, a question to the lead' % (p.get('seed_installed', 0),
                                                                              p.get('prepare_cold', 0)), (None, 'none'), ''
    screen = u_screen(r)
    if not ok_arm(r) or not r.get('entered') or 'f1' not in r:
'''),
    (r'''def read_u(get):
    """Item 355 (e): KILLED / ALIVE_BY_PROBE_5 / UNDETERMINED."""
    out = []
    nf = 0
    und = 0
    over = False
    for j in range(U_N):
        tag = 'u_%d' % (j + 1)
        r = get(tag)
        f, gw, screen, det = u_eval(r)
        nf += f is True
        und += f is None
        if screen is not None and screen > PREP_LIMIT_S:
            over = True
        if screen is None:
            und += 0 if f is None else 1
        out.append('%s %s: %s; S-cat member %s; preparation screen %s s (PipelinePrecache: all pipelines created %s s, '
                   'ShaderPreparation: ready %s s; log created %s ms, startup wait %s ms); %s' % (
                       tag, U_LIST[j], gw, {True: 'FAILS', False: 'holds', None: 'undetermined'}[f], screen,
                       r and r.get('prep_created_s'), r and r.get('prep_ready_s'), r and r['prep']['created_ms'],
                       r and r['prep']['waited_ms'], det))
    if nf >= U_KILL or over:
        word = 'KILLED'
    elif und:
        word = 'UNDETERMINED'
    else:
        word = 'ALIVE_BY_PROBE_5'
    out.append('S-cat (item 229 (d)(2), item 355 (e)): arms failing %d of %d (kill at >= %d), a screen > %d s %s -> %s' % (
        nf, U_N, U_KILL, PREP_LIMIT_S, over, word))
    return word, out
''',
     r'''def screen_text(sec, kind):
    if kind == 'measured':
        return '%.1f s' % sec
    if kind == 'lower bound':
        return ('> %.1f s (lower bound)' % sec) if sec > PREP_LIMIT_S else \
            '>= %.1f s (lower bound, not above %d s - the screen undetermined, not an S-cat member)' % (sec, PREP_LIMIT_S)
    return 'undetermined (no line, no progress line, no timeout - not an S-cat member)'


def read_u(get):
    """Item 355 (e), item 371 (v): KILLED / ALIVE_BY_PROBE_5 / UNDETERMINED; the letter of item 355 (e) and the executor variant
    beside."""
    out = []
    nf = 0
    nf_m = 0
    und = 0
    und_scr = 0
    over = False
    for j in range(U_N):
        tag = 'u_%d' % (j + 1)
        r = get(tag)
        f, gw, (sec, kind), det = u_eval(r)
        if sec is not None and sec > PREP_LIMIT_S:
            over = True
        member = kind == 'measured' or (kind == 'lower bound' and sec > PREP_LIMIT_S)
        nf += f is True
        nf_m += f is True and member
        und += f is None
        if not member and f is not None:
            und_scr += 1
        p = (r or {}).get('prep') or {}
        g = (r or {}).get('gates') or {}
        out.append('%s %s: %s; S-cat member %s; stdout Shaders: %s, rec_new_after %s, perm_after %s, skip lines after the first '
                   'scene frame %s; preparation screen %s (PipelinePrecache: all pipelines created %s s, ShaderPreparation: ready '
                   '%s s; progress lines %s, max elapsed_ms %s; attempt %s; log created %s ms, startup wait %s ms); %s' % (
                       tag, U_LIST[j], gw, {True: 'FAILS', False: 'holds', None: 'undetermined'}[f],
                       g.get('stdout_shaders', '-'), g.get('rec_new_after', '-'), g.get('perm_after', '-'),
                       (r or {}).get('skips_after', '-'), screen_text(sec, kind), r and r.get('prep_created_s'),
                       r and r.get('prep_ready_s'), p.get('prog_n'), p.get('prog_ms'), r and r.get('attempt'),
                       p.get('created_ms'), p.get('waited_ms'), det))
    if nf_m >= U_KILL or over:
        word = 'KILLED'
    elif und or und_scr:
        word = 'UNDETERMINED'
    else:
        word = 'ALIVE_BY_PROBE_5'
    letter = 'KILLED' if nf >= U_KILL or over else ('UNDETERMINED' if und else 'ALIVE_BY_PROBE_5')
    varx = 'KILLED' if nf >= U_KILL or over else ('UNDETERMINED' if und or und_scr else 'ALIVE_BY_PROBE_5')
    out.append('S-cat (item 229 (d)(2), item 355 (e), item 371 (v)): failing members %d of %d (kill at >= %d), a screen > %d s %s, '
               'arms without a screen measure %d -> %s' % (nf_m, U_N, U_KILL, PREP_LIMIT_S, over, und_scr, word))
    out.append('by the letter of item 355 (e) ("else alive": an arm without a screen measure is alive, its failure counts): %s%s' % (
        letter, '' if letter == word else ' - DIFFERS (screen undetermined)'))
    out.append('executor variant (a failing arm without a screen measure counts among the failing, %d failing): %s%s' % (
        nf, varx, '' if varx == word else ' - DIFFERS (a failing arm without a screen measure)'))
    return word, out
'''),
    (r'''def haze_sheet(tag, root=LINK_DIR, ffmpeg=FFMPEG):
    """The lead sheet of every series after frame 1 002 of a pi arm: frames start-2 .. end+2 (at most 24) tiled 6 wide at
    480 px, into <root>/haze_<tag>_<start>-<end>.png; prints the files."""
''',
     r'''def sheet_frames(a, b, frames):
    """Item 371 (g), RC5: the frames of the lead sheet of the series a .. b - a-2 .. b+2 clipped to the video; a series longer than
    20 frames -> 24 frames spread evenly over [a-2, b+2] (both ends kept)."""
    lo, hi = max(0, a - 2), min(frames - 1, b + 2)
    if b - a + 1 <= SHEET_LONG:
        return list(range(lo, hi + 1))
    return sorted(set(lo + (hi - lo) * k // (SHEET_N - 1) for k in range(SHEET_N)))


def sheet_vf(idx):
    """The ffmpeg filter of the sheet: the frames idx tiled 6 wide at 480 px."""
    return "select='%s',scale=480:-1,tile=6x%d" % ('+'.join('eq(n\\,%d)' % i for i in idx), (len(idx) + 5) // 6)


def haze_sheet(tag, root=LINK_DIR, ffmpeg=FFMPEG):
    """The lead sheet of every series after frame 1 002 of a pi arm: the frames of sheet_frames() tiled 6 wide at 480 px, into
    <root>/haze_<tag>_<start>-<end>.png; prints the files and the frame numbers."""
'''),
    (r'''    for a, b in h['after_var']:
        lo, hi = max(0, a - 2), min(h['frames'] - 1, b + 2, a - 2 + 23)
        outp = os.path.join(root, 'haze_%s_%d-%d.png' % (tag, a, b))
        n = hi - lo + 1
        rows = (n + 5) // 6
        vf = "select='between(n\\,%d\\,%d)',scale=480:-1,tile=6x%d" % (lo, hi, rows)
        subprocess.run([ffmpeg, '-loglevel', 'error', '-y', '-i', vid, '-vf', vf, '-frames:v', '1', '-vsync', '0', outp])
        print('HAZE SHEET %s series %d-%d frames %d-%d -> %s sha256 %s' % (
            tag, a, b, lo, hi, outp, A.sha_file(outp) if os.path.isfile(outp) else 'MISSING'))
''',
     r'''    for a, b in h['after_var']:
        idx = sheet_frames(a, b, h['frames'])
        outp = os.path.join(root, 'haze_%s_%d-%d.png' % (tag, a, b))
        subprocess.run([ffmpeg, '-loglevel', 'error', '-y', '-i', vid, '-vf', sheet_vf(idx), '-frames:v', '1', '-vsync', '0',
                        outp])
        print('HAZE SHEET %s series %d-%d frames %s -> %s sha256 %s' % (
            tag, a, b, ','.join(str(i) for i in idx), outp, A.sha_file(outp) if os.path.isfile(outp) else 'MISSING'))
'''),
]

TSC = [
    (r'''reading printed beside.  Synthetic logs only, no process is started.
''',
     r'''reading printed beside.  S9b (item 371): the video member of the repeat (the detector read with frames after 1 002; a series in
pi_r1 with a glitch in pi_w0 -> READ_1, the executor variant NOT_EVALUABLE; <= 1 003 frames -> NOT_EVALUABLE), the row
installed_before = 4aa62e95, the lower bound of the U screen (progress 181 000 / 179 000 / 180 000 ms, the maximum not the last,
timeout without lines, no line at all), the letter word and the executor variant beside, the RC4 data, the sheet frames of
RC5.  Synthetic logs only, no process is started.
'''),
    (r'''ok &= case('A6 paths: link C:/kyty/s288/s10, seal pred/05b_s.md (item 362 (d)), Sky Garden, L0 shuriken_ninja_castle',
           S.LINK_DIR == 'C:/kyty/s288/s10' and S.PRED_PATH == 'C:/kyty/s288/pred/05b_s.md' and S.SKY == 'underwater_aerial_garden'
''',
     r'''ok &= case('A6 paths: link C:/kyty/s288/s10, seal pred/06_s.md (item 371 (g)), Sky Garden, L0 shuriken_ninja_castle',
           S.LINK_DIR == 'C:/kyty/s288/s10' and S.PRED_PATH == 'C:/kyty/s288/pred/06_s.md' and S.SKY == 'underwater_aerial_garden'
'''),
    (r'''ok &= case('F6 no cache json -> one failing row', S.cache_rows(S.SPEC['u_1'], None, lambda t: None) ==
           [('cache protocol json present', False, 'missing')])
''',
     r'''ok &= case('F6 no cache json -> one failing row', S.cache_rows(S.SPEC['u_1'], None, lambda t: None) ==
           [('cache protocol json present', False, 'missing')])
ok &= case('F7 item 371 (g), RC1: installed_before must be the installed 4aa62e95 of item 342 - before = after = f3b3aa3b fails that '
           'row only', [r[0] for r in crow('pi_w1', installed_before=dict(sha=BIN_S), installed_after=dict(sha=BIN_S))] ==
           ['installed binary before the arm = the installed 4aa62e95 of item 342 (item 371 (g), RC1)'] and
           [r[0] for r in crow('u_2', installed_before=dict(sha=BIN_S), installed_after=dict(sha=BIN_S))] ==
           ['installed binary before the arm = the installed 4aa62e95 of item 342 (item 371 (g), RC1)'])
'''),
    (r'''ok &= case('I10 a W arm presented < 300 s -> NOT_EVALUABLE', w7 == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(2999, 0))
ok &= case('I11 a pi arm with a video < 3 000 frames -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(3000, 0))
ok &= case('I11b a pi arm with exactly 3 000 video frames is readable', S.read_pi(getter())[0] == 'READ_2')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(3200, 1))
ok &= case('I12 a pi arm with a one-frame glitch -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
''',
     r'''ok &= case('I10 a W arm presented < 300 s -> NOT_EVALUABLE; the executor variant NOT_EVALUABLE too (no DIFFERS)',
           w7 == 'NOT_EVALUABLE' and any(x.startswith('executor variant (seal 05b') and x.endswith('): NOT_EVALUABLE')
                                         for x in rd7))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(2999, 0))
w11, rd11 = S.read_pi(getter())
ok &= case('I11 item 371 (b): a pi arm with a video < 3 000 frames is readable by the letter (READ_2); the executor variant '
           'NOT_EVALUABLE - DIFFERS (video rule)', w11 == 'READ_2' and any(
               x.startswith('executor variant (seal 05b') and x.endswith(': NOT_EVALUABLE - DIFFERS (video rule)') for x in rd11))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(3000, 0))
w11b, rd11b = S.read_pi(getter())
ok &= case('I11b a pi arm with exactly 3 000 video frames: READ_2 in both readings, no DIFFERS (video rule)', w11b == 'READ_2' and
           any(x.startswith('executor variant (seal 05b') and x.endswith(': READ_2') for x in rd11b))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(3200, 1))
w12, rd12 = S.read_pi(getter())
ok &= case('I12 item 371 (b): a pi arm with a one-frame glitch is readable by the letter (READ_2); the executor variant '
           'NOT_EVALUABLE - DIFFERS (video rule)', w12 == 'READ_2' and any(
               x.startswith('executor variant (seal 05b') and x.endswith(': NOT_EVALUABLE - DIFFERS (video rule)') for x in rd12))
'''),
    (r'''# ---- c5_0 and the C5 reading
''',
     r'''# ---- item 371 (b) (RC3 of S9r): the video member of the repeat = the video read by the detector with frames after 1 002
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(94435637)]), sat=sat_for([(1928, 1946)]))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(3200, 1))
w18, rd18 = S.read_pi(getter())
ok &= case('I18 item 371 (b): a series in pi_r1 and 1 one-frame glitch in pi_w0 -> by the letter READ_1, the executor variant '
           'NOT_EVALUABLE - DIFFERS (video rule); the video frames, present rows and glitches printed per arm', w18 == 'READ_1'
           and any(x.startswith('executor variant (seal 05b') and x.endswith(': NOT_EVALUABLE - DIFFERS (video rule)')
                   for x in rd18) and
           any(x.startswith('pi_w0: readable (executor variant: NOT readable); video frames 3200, present rows ') and
               'one-frame glitches 1;' in x for x in rd18) and
           any(x.startswith('pi_r1: readable (executor variant: readable); video frames 3200, present rows ') and
               'one-frame glitches 0;' in x for x in rd18))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), sat=sat_for(n=1002))
w19, rd19 = S.read_pi(getter())
ok &= case('I19 a pi video of 1 002 frames (none after frame 1 002) -> NOT_EVALUABLE by the letter', w19 == 'NOT_EVALUABLE' and
           any(x.startswith('arms not readable (admission, identity, entry, the video read by the detector') and "['pi_w0']" in x
               for x in rd19))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), sat=sat_for(n=1003))
ok &= case('I19b 1 003 frames (0-based: the last is frame 1 002) -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), sat=sat_for(n=1004))
ok &= case('I19c 1 004 frames (frame 1 003 after the edge) -> readable, READ_1', S.read_pi(getter())[0] == 'READ_1')
rm_arm('pi_w0')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), video=False)
ok &= case('I20 a pi arm without a video (no detector reading) -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M))
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(94435637)]))
ok &= case('I21 restored: READ_2', S.read_pi(getter())[0] == 'READ_2')
ok &= case('I22 RC5 sheet frames: a 19-frame series a-2 .. b+2 contiguous; 20 frames contiguous (24); 21 frames -> 24 spread '
           'evenly with both ends; a long series 1 930 - 2 010 -> 24 frames 1 928 .. 2 012; clipped at the end of the video',
           S.sheet_frames(1928, 1946, 3749) == list(range(1926, 1949)) and
           S.sheet_frames(1000, 1019, 3749) == list(range(998, 1022)) and
           S.sheet_frames(1000, 1020, 3749) == [998 + 24 * k // 23 for k in range(24)] and
           S.sheet_frames(1930, 2010, 3749) == [1928 + 84 * k // 23 for k in range(24)] and
           len(S.sheet_frames(1930, 2010, 3749)) == 24 and S.sheet_frames(3700, 3760, 3749)[-1] == 3748 and
           S.sheet_frames(3700, 3760, 3749)[0] == 3698 and len(S.sheet_frames(3700, 3760, 3749)) == 24 and
           S.sheet_frames(1, 5, 100)[0] == 0)
ok &= case('I23 RC5 sheet filter: the frames by eq(n), 6 wide, rows = ceil(n / 6)', S.sheet_vf([1, 2]) ==
           "select='eq(n\\,1)+eq(n\\,2)',scale=480:-1,tile=6x1" and S.sheet_vf(list(range(6))).endswith('tile=6x1') and
           S.sheet_vf(list(range(7))).endswith('tile=6x2'))

# ---- c5_0 and the C5 reading
'''),
    (r'''def u_arm(tag, skip=False, att=False, gates=True, std=True, created=30.0, ready=31.0, lv=None):
    hdr = U_HDR if gates else HEADER_T
''',
     r'''def u_arm(tag, skip=False, att=False, gates=True, std=True, created=30.0, ready=31.0, lv=None, prog=(), outcome='ok'):
    hdr = (U_HDR if gates else HEADER_T) + ['ShaderPreparation: progress %d/100 skipped=0 elapsed_ms=%d' % (i + 1, ms)
                                            for i, ms in enumerate(prog)]
'''),
    (r'''          extra_stdout=U_STD if std else (), js=js_for(tag, attempt=dict(prep_created_s=created, prep_ready_s=ready)))
''',
     r'''          extra_stdout=U_STD if std else (), js=js_for(tag, attempt=dict(prep_created_s=created, prep_ready_s=ready,
                                                                         outcome=outcome)))
'''),
    (r'''ok &= case('M6 one screen line not seen -> the screen undetermined -> UNDETERMINED', S.read_u(getter())[0] == 'UNDETERMINED')
''',
     r'''w6u, l6u = S.read_u(getter())
ok &= case('M6 one screen line not seen, no progress line, no timeout -> the screen undetermined, not an S-cat member -> '
           'UNDETERMINED; the letter of item 355 (e) ALIVE_BY_PROBE_5 - DIFFERS (screen undetermined)', w6u == 'UNDETERMINED' and
           any(x.startswith('by the letter of item 355 (e)') and x.endswith(': ALIVE_BY_PROBE_5 - DIFFERS (screen undetermined)')
               for x in l6u) and any(x.startswith('u_5 fragile_battle_1:') and 'preparation screen undetermined (no line' in x
                                     for x in l6u))
'''),
    (r'''ok &= case('M11 u_eval of a not made arm -> undetermined', S.u_eval(None)[0] is None and S.u_eval(None)[1] == 'not made')
''',
     r'''ok &= case('M11 u_eval of a not made arm -> undetermined', S.u_eval(None)[0] is None and S.u_eval(None)[1] == 'not made')
u_arm('u_5', ready=None, prog=(1000, 181000))
wq1, lq1 = S.read_u(getter())
ok &= case('MU1 item 371 (v): no ready line, the last progress 181 000 ms -> the lower bound 181 s > 180 -> KILLED, printed '
           '"screen > 181.0 s (lower bound)"', wq1 == 'KILLED' and any(
               x.startswith('u_5 fragile_battle_1:') and 'preparation screen > 181.0 s (lower bound)' in x and
               'progress lines 2, max elapsed_ms 181000' in x for x in lq1))
u_arm('u_5', ready=None, prog=(181000, 1000))
ok &= case('MU2 the bound is the maximum of elapsed_ms, not the last line -> KILLED', S.read_u(getter())[0] == 'KILLED')
u_arm('u_5', ready=None, prog=(1000, 179000))
wq3, lq3 = S.read_u(getter())
ok &= case('MU3 the last progress 179 000 ms -> the bound 179 s not above 180 -> not a member -> UNDETERMINED; the letter '
           'ALIVE_BY_PROBE_5 - DIFFERS (screen undetermined)', wq3 == 'UNDETERMINED' and any(
               x.startswith('by the letter of item 355 (e)') and x.endswith(': ALIVE_BY_PROBE_5 - DIFFERS (screen undetermined)')
               for x in lq3) and any('>= 179.0 s (lower bound, not above 180 s' in x for x in lq3))
u_arm('u_5', ready=None, prog=(180000,))
wq3b, lq3b = S.read_u(getter())
ok &= case('MU3b the bound exactly 180 s -> not above -> UNDETERMINED, printed as not above', wq3b == 'UNDETERMINED' and
           any('>= 180.0 s (lower bound, not above 180 s' in x for x in lq3b))
u_arm('u_5', created=None, ready=None, outcome='timeout')
wq4, lq4 = S.read_u(getter())
ok &= case('MU4 the attempt ended by timeout without both lines and without progress -> the bound = --timeout 600 s -> KILLED, '
           '"screen > 600.0 s (lower bound)"', wq4 == 'KILLED' and any(
               x.startswith('u_5 fragile_battle_1:') and 'preparation screen > 600.0 s (lower bound)' in x for x in lq4))
u_arm('u_5', created=None, ready=None, outcome='timeout', prog=(700000,))
ok &= case('MU4b timeout with a progress line of 700 s -> the bound is the maximum 700 s (not the timeout term appended last)',
           any('preparation screen > 700.0 s (lower bound)' in x for x in S.read_u(getter())[1]))
u_arm('u_5', created=None, ready=None)
ok &= case('MU5 no line, no progress, outcome ok -> UNDETERMINED', S.read_u(getter())[0] == 'UNDETERMINED')
u_arm('u_2', skip=True)
u_arm('u_5', skip=True, created=None, ready=None)
wq7, lq7 = S.read_u(getter())
ok &= case('MU7 a failing arm with a screen (u_2) and a failing arm without a screen measure (u_5): 1 failing member -> '
           'UNDETERMINED; the letter of item 355 (e) KILLED - DIFFERS (screen undetermined); the executor variant KILLED - '
           'DIFFERS (a failing arm without a screen measure)', wq7 == 'UNDETERMINED' and any(
               x.startswith('by the letter of item 355 (e)') and x.endswith(': KILLED - DIFFERS (screen undetermined)')
               for x in lq7) and any(x.startswith('executor variant (a failing arm without a screen measure counts')
                                     and x.endswith(': KILLED - DIFFERS (a failing arm without a screen measure)') for x in lq7))
u_arm('u_5')
u_arm('u_4', att=True)
wq8, lq8 = S.read_u(getter())
ok &= case('MU8 RC4: the line of every U arm carries stdout Shaders:, rec_new_after, perm_after and the skip lines after the '
           'first scene frame (u_2 0 / 0 / 0 / 1, u_4 1 / 0 / 1 / 0); KILLED with two failing members', wq8 == 'KILLED' and any(
               x.startswith('u_2 hoover_beach:') and 'stdout Shaders: 0, rec_new_after 0, perm_after 0, skip lines after the '
               'first scene frame 1;' in x for x in lq8) and any(
               x.startswith('u_4 interactive_credit_00:') and 'stdout Shaders: 1, rec_new_after 0, perm_after 1, skip lines '
               'after the first scene frame 0;' in x for x in lq8))
u_arm('u_2')
u_arm('u_4')
'''),
]

TGO = [
    ('05b_s.md', REPALL, '06_s.md'),
    (r'''the GamePatch interference.  The first output line names this suite and the harness by sha256; the output ends with ALL OK.
''',
     r'''the GamePatch interference.  S9b (item 371 (g), RC1 of S9r): the guard s10/IN_ARM written before the install (the game sees
it with the tag, the installed sha and the pre manifests) and removed by the successful return; a hanging IN_ARM (a hard kill)
refuses the next arm rc 1 before the lock; an installed binary other than INST_WANT -> rc 1 inside the lock, nothing installed,
no IN_ARM, no attempt.  The first output line names this suite and the harness by sha256; the output ends with ALL OK.
'''),
    (r'''           'echo "go_s.sh $T pid $$ started' in src_t)
''',
     r'''           'echo "go_s.sh $T pid $$ started' in src_t)
ok &= case('G23 item 371 (g): the shipped harness guards s10/IN_ARM with the RETURN_FAILED guards and pins INST_WANT = 4aa62e95 '
           '(item 342); the seal is pred/06_s.md', '$ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM; do' in src_t and
           'INST_WANT="4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac"\n' in src_t and
           'PRED=pred/06_s.md\n' in src_t and src_t.count('guardfiles\n') == 2)
'''),
    (r'''    "json.dump({'tag': tag, 'gp': os.environ.get('KYTY_GAME_PATCH'), 'seen': seen, "
''',
     r'''    "ia = open(os.path.join(root, 'IN_ARM')).read() if os.path.exists(os.path.join(root, 'IN_ARM')) else None\n"
    "json.dump({'tag': tag, 'gp': os.environ.get('KYTY_GAME_PATCH'), 'seen': seen, 'in_arm': ia, "
'''),
    (r'''             ('RSLEEP=5\n', 'RSLEEP=0\n')):
''',
     r'''             ('RSLEEP=5\n', 'RSLEEP=0\n'),
             ('INST_WANT="4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac"\n', 'INST_WANT="%s"\n' % sha2(PINU))):
'''),
    ("TAGS2 = ('pi_w1', 'pi_r1', 'u_1', 'c5_0')", "TAGS2 = ('pi_w1', 'pi_r1', 'u_1', 'c5_0', 'pi_w0')"),
    (r'''print('checks: %d' % N[0])
''',
     r'''ia1 = js2('pi_w1').get('in_arm') or ''
t4 = (B2 / 's10' / 'times.txt').read_text()
ok &= case('GL10 IN_ARM (item 371 (g)): the game saw it - the tag, the installed sha, man_pre_app / man_pre_glc of the arm - and '
           'the successful return removed it', ia1.startswith('IN_ARM pi_w1 ') and ('installed: %s (copy' % sha2(PINU)) in ia1
           and ('man_pre_app: %s ' % cj2('pi_w1').get('man_pre_app', {}).get('sha', 'x')) in ia1 and
           ('man_pre_glc: %s ' % cj2('pi_w1').get('man_pre_glc', {}).get('sha', 'x')) in ia1 and
           len(cj2('pi_w1').get('man_pre_app', {}).get('sha', '')) == 64 and
           not (B2 / 's10' / 'IN_ARM').exists() and t4.count('guard ') >= 2 and 'removed after the successful return' in t4)
(B2 / 's10' / 'IN_ARM').write_text('IN_ARM pi_w0 2026-10-03T00:00:00Z pid 1 - a hard kill left it\n')
n_lock = len(lockrows())
rc, o = go2('pi_w0')
ok &= case('GL11 a hanging IN_ARM (a hard kill of an earlier arm) -> rc 1 "return failed guard" before the lock: no lock row, '
           'no attempt, the installed binary untouched, the guard kept', rc == 1 and 'return failed guard' in o and 'IN_ARM' in o
           and len(lockrows()) == n_lock and not (B2 / 's10' / 'attempt_pi_w0.txt').exists() and
           GAME2.read_bytes() == b'installed build X' and (B2 / 's10' / 'IN_ARM').exists())
(B2 / 's10' / 'IN_ARM').unlink()
put2(GAME2, b'another installed build')
n_lock = len(lockrows())
rc, o = go2('pi_w0')
t5 = (B2 / 's10' / 'times.txt').read_text()
ok &= case('GL12 an installed binary other than INST_WANT -> rc 1 inside the lock: nothing installed, no IN_ARM, no attempt, the '
           'lock taken and released, the row in times.txt', rc == 1 and 'installed binary not' in o and
           GAME2.read_bytes() == b'another installed build' and not (B2 / 's10' / 'IN_ARM').exists() and
           not (B2 / 's10' / 'attempt_pi_w0.txt').exists() and len(lockrows()) == n_lock + 2 and not Path(LOCK2).exists() and
           ('!= %s (item 342) - no arm' % sha2(PINU)) in t5)
put2(GAME2, b'installed build X')
print('checks: %d' % N[0])
'''),
]

MUT = [
    (r'''Not mutated (equivalent - no input can tell the mutant): the identity "scan_x rows = scan_s rows" (both scans count the same
lines; a line one counts and the other does not crashes sc_s.scan_s first) and the video member of clean_arm() (a pi arm
without a video has no haze reading, so it is NOT_EVALUABLE either way).''',
     r'''Not mutated (equivalent - no input can tell the mutant): the identity "scan_x rows = scan_s rows" (both scans count the same
lines; a line one counts and the other does not crashes sc_s.scan_s first) and the video / haze members of clean_arm_x() (a pi
arm without a video has no haze reading, so it is NOT_EVALUABLE in both readings).  S9b (item 371): mutants of the video member
of the repeat, the executor variant of seal 05b, the row installed_before, the progress scan, the lower bound of the U screen,
the member rule and the three words of U, the RC4 data and the RC5 sheet frames.'''),
    ("('pred', \"PRED_PATH = 'C:/kyty/s288/pred/05b_s.md'\", \"PRED_PATH = 'C:/kyty/s288/pred/05_s.md'\"),",
     "('pred', \"PRED_PATH = 'C:/kyty/s288/pred/06_s.md'\", \"PRED_PATH = 'C:/kyty/s288/pred/05b_s.md'\"),\n"
     "    ('sheet_long', 'SHEET_LONG = 20 ', 'SHEET_LONG = 21 '),\n"
     "    ('sheet_n', 'SHEET_N = 24\\n', 'SHEET_N = 25\\n'),"),
    ('''    ('plan_sd_pi', "sd, to = (300, 480) if spec['group'] == 'pi'", "sd, to = (100, 480) if spec['group'] == 'pi'"),''',
     '''    ('plan_sd_pi', "return (300, 480) if spec['group'] == 'pi'", "return (100, 480) if spec['group'] == 'pi'"),
    ('plan_st', "    sd, to = stable_timeout(spec)\\n", "    sd, to = 300, 480\\n"),'''),
    ('''    ('so_pc', "if line.startswith(b'Cache test mode: prepare-cold'):", "if line.startswith(b'Cache test mode:'):"),''',
     '''    ('so_pc', "if line.startswith(b'Cache test mode: prepare-cold'):", "if line.startswith(b'Cache test mode:'):"),
    ('sx_prog_pfx', "if line.startswith(b'ShaderPreparation: progress '):", "if line.startswith(b'ShaderPreparation: ready'):"),
    ('sx_prog_max', "if v is not None and (r['prog_ms'] is None or v > r['prog_ms']):", "if v is not None:"),
    ('sx_prog_n', "                    r['prog_n'] += 1\\n", "                    pass\\n"),
    ('sx_prog_key', "v = A.field(line.rstrip(), b'elapsed_ms')", "v = A.field(line.rstrip(), b'skipped')"),'''),
    ('''    ('cr_inst', "ib is not None and len(ib) == 64 and ia == ib,", "ia == ib,"),''',
     '''    ('cr_inst', "ib is not None and len(ib) == 64 and ia == ib,", "ia == ib,"),
    ('cr_ib', "ib == BIN_U,\\n        (ib or '-')[:16])", "True,\\n        (ib or '-')[:16])"),
    ('cr_ib_s', "ib == BIN_U,\\n        (ib or '-')[:16])", "ib in (BIN_U, BIN_S),\\n        (ib or '-')[:16])"),'''),
    ('''    ('cl_frames', "g.get('video_frames', 0) >= FRAMES_VIDEO", "g.get('video_frames', 0) > FRAMES_VIDEO"),
    ('cl_glitch', "and \\\\\\n        g.get('glitches') == 0", "and \\\\\\n        True"),
    ('cl_marks', "g.get('glitches') == 0 and not r['marks'] and", "g.get('glitches') == 0 and"),''',
     '''    ('cl_frames', "g.get('video_frames', 0) >= FRAMES_VIDEO", "g.get('video_frames', 0) > FRAMES_VIDEO"),
    ('cl_glitch', "and \\\\\\n        g.get('glitches') == 0", "and \\\\\\n        True"),
    ('cl_marks', "h['frames'] - 1 > HAZE_AFTER and not r['marks'] and", "h['frames'] - 1 > HAZE_AFTER and"),
    ('cl_haze', "h is not None and h['frames'] - 1 > HAZE_AFTER", "(h is None or h['frames'] - 1 > HAZE_AFTER)"),
    ('cl_after', "h is not None and h['frames'] - 1 > HAZE_AFTER", "h is not None and h['frames'] - 1 >= HAZE_AFTER"),
    ('cl_after_off', "h is not None and h['frames'] - 1 > HAZE_AFTER", "h is not None and h['frames'] > 0"),
    ('cl_after_one', "h is not None and h['frames'] - 1 > HAZE_AFTER", "h is not None and h['frames'] > HAZE_AFTER"),'''),
    ('''    ('rp_bad', "bad = [t for t in PI_ORDER if not clean_arm(rs[t]) or rs[t].get('haze') is None]", "bad = []"),''',
     '''    ('rp_bad', "bad = [t for t in PI_ORDER if not clean_arm(rs[t])]", "bad = []"),
    ('rp_bad_l', "bad = [t for t in PI_ORDER if not clean_arm(rs[t])]", "bad = [t for t in PI_ORDER if not clean_arm_x(rs[t])]"),
    ('rp_bad_x', "bad_x = [t for t in PI_ORDER if not clean_arm_x(rs[t])]", "bad_x = [t for t in PI_ORDER if not clean_arm(rs[t])]"),
    ('rp_wordx_held', "wordx = 'NOT_EVALUABLE' if bad_x or not all(held.values()) else", "wordx = 'NOT_EVALUABLE' if bad_x else"),
    ('rp_vdiff', "'' if wordx == word else ' - DIFFERS (video rule)')", "'')"),
    ('rp_vline', "    out.append(video_rule_line(word, wordx))\\n", "    pass\\n"),'''),
    ('''    ('rp_loaded', "loaded[rt] = lb is not None and lb == wb and rs[rt]['prep']['disabled'] == 0", "loaded[rt] = lb is not None and lb == wb"),
    ('rp_loaded2', "loaded[rt] = lb is not None and lb == wb and rs[rt]['prep']['disabled'] == 0", "loaded[rt] = rs[rt]['prep']['disabled'] == 0"),''',
     '''    ('rp_loaded', "loaded[rt] = lb is not None and lb == wb and dis == 0", "loaded[rt] = lb is not None and lb == wb"),
    ('rp_loaded2', "loaded[rt] = lb is not None and lb == wb and dis == 0", "loaded[rt] = dis == 0"),'''),
    ('''    ('ue_gates', "gates = r['prep']['seed_installed'] >= 1 and r['prep']['prepare_cold'] >= 1", "gates = r['prep']['seed_installed'] >= 1"),
    ('ue_gates2', "gates = r['prep']['seed_installed'] >= 1 and r['prep']['prepare_cold'] >= 1", "gates = r['prep']['prepare_cold'] >= 1"),
    ('ue_screen', "screen = max(xs) if len(xs) == 2 else None", "screen = max(xs) if xs else None"),
    ('ue_max', "screen = max(xs) if len(xs) == 2 else None", "screen = min(xs) if len(xs) == 2 else None"),''',
     '''    ('ue_gates', "gates = p.get('seed_installed', 0) >= 1 and p.get('prepare_cold', 0) >= 1", "gates = p.get('seed_installed', 0) >= 1"),
    ('ue_gates2', "gates = p.get('seed_installed', 0) >= 1 and p.get('prepare_cold', 0) >= 1", "gates = p.get('prepare_cold', 0) >= 1"),
    ('ue_screen', "    if len(xs) == 2:\\n        return max(xs), 'measured'", "    if xs:\\n        return max(xs), 'measured'"),
    ('ue_max', "        return max(xs), 'measured'", "        return min(xs), 'measured'"),
    ('us_prog', "        lb.append(pm / 1000.0)\\n", "        pass\\n"),
    ('us_prog_unit', "        lb.append(pm / 1000.0)\\n", "        lb.append(pm / 1001.0)\\n"),
    ('us_tout', "    if r.get('attempt') == 'timeout':", "    if False:"),
    ('us_tout_val', "lb.append(float(stable_timeout(SPEC[r['tag']])[1]))", "lb.append(180.0)"),
    ('us_lb_none', "return (max(lb), 'lower bound') if lb else (None, 'none')", "return (max(lb), 'measured') if lb else (None, 'none')"),
    ('us_lb_max', "return (max(lb), 'lower bound') if lb else (None, 'none')", "return (lb[-1], 'lower bound') if lb else (None, 'none')"),'''),
    ('''    ('ue_notmade', "    if r is None:\\n        return None, 'not made', None, ''", "    if r is None:\\n        return False, 'not made', None, ''"),
    ('ru_kill', "    if nf >= U_KILL or over:", "    if nf > U_KILL or over:"),
    ('ru_over', "if screen is not None and screen > PREP_LIMIT_S:", "if screen is not None and screen >= PREP_LIMIT_S:"),
    ('ru_over_off', "    if nf >= U_KILL or over:", "    if nf >= U_KILL:"),
    ('ru_und', "    elif und:\\n        word = 'UNDETERMINED'", "    elif False:\\n        word = 'UNDETERMINED'"),
    ('ru_und_screen', "            und += 0 if f is None else 1", "            und += 0"),''',
     '''    ('ue_notmade', "    if r is None:\\n        return None, 'not made', (None, 'none'), ''", "    if r is None:\\n        return False, 'not made', (None, 'none'), ''"),
    ('ru_kill', "    if nf_m >= U_KILL or over:", "    if nf_m > U_KILL or over:"),
    ('ru_over', "if sec is not None and sec > PREP_LIMIT_S:", "if sec is not None and sec >= PREP_LIMIT_S:"),
    ('ru_over_off', "    if nf_m >= U_KILL or over:", "    if nf_m >= U_KILL:"),
    ('ru_und', "    elif und or und_scr:\\n        word = 'UNDETERMINED'", "    elif False:\\n        word = 'UNDETERMINED'"),
    ('ru_und_scr', "    elif und or und_scr:\\n        word = 'UNDETERMINED'", "    elif und:\\n        word = 'UNDETERMINED'"),
    ('ru_und_screen', "            und_scr += 1\\n", "            pass\\n"),
    ('ru_member', "member = kind == 'measured' or (kind == 'lower bound' and sec > PREP_LIMIT_S)", "member = kind != 'none'"),
    ('ru_nfm', "        nf_m += f is True and member\\n", "        nf_m += f is True\\n"),
    ('ru_letter', "letter = 'KILLED' if nf >= U_KILL or over else ('UNDETERMINED' if und else 'ALIVE_BY_PROBE_5')", "letter = word"),
    ('ru_letter_d', "'' if letter == word else ' - DIFFERS (screen undetermined)'", "''"),
    ('ru_varx', "varx = 'KILLED' if nf >= U_KILL or over else", "varx = 'KILLED' if nf_m >= U_KILL or over else"),
    ('ru_rc4', "g.get('stdout_shaders', '-'), g.get('rec_new_after', '-'), g.get('perm_after', '-'),", "g.get('stdout_shaders', '-'), g.get('perm_after', '-'), g.get('rec_new_after', '-'),"),
    ('ru_rc4_sh', "g.get('stdout_shaders', '-'), g.get('rec_new_after', '-')", "g.get('rec_new_after', '-'), g.get('rec_new_after', '-')"),
    ('ru_rc4_skip', "(r or {}).get('skips_after', '-'), screen_text(sec, kind)", "(r or {}).get('dt100', '-'), screen_text(sec, kind)"),
    ('st_lower', "        return ('> %.1f s (lower bound)' % sec) if sec > PREP_LIMIT_S else", "        return ('> %.1f s (lower bound)' % sec) if sec >= PREP_LIMIT_S else"),
    ('hs_long', "    if b - a + 1 <= SHEET_LONG:", "    if b - a + 1 < SHEET_LONG:"),
    ('hs_even', "lo + (hi - lo) * k // (SHEET_N - 1) for k in range(SHEET_N)", "lo + k for k in range(SHEET_N)"),
    ('hs_lo', "    lo, hi = max(0, a - 2), min(frames - 1, b + 2)", "    lo, hi = max(0, a - 1), min(frames - 1, b + 2)"),
    ('hs_hi', "    lo, hi = max(0, a - 2), min(frames - 1, b + 2)", "    lo, hi = max(0, a - 2), min(frames, b + 2)"),
    ('hs_rows', "(len(idx) + 5) // 6)", "(len(idx) + 6) // 6)"),'''),
]


def rep(t, reps, name):
    for item in reps:
        if len(item) == 3:
            a, _, b = item
            n = t.count(a)
            if n < 1:
                raise SystemExit('NO MATCH (all) in %s: %r' % (name, a[:100]))
            t = t.replace(a, b)
            continue
        a, b = item
        n = t.count(a)
        if n != 1:
            raise SystemExit('NO MATCH (%d) in %s: %r' % (n, name, a[:120]))
        t = t.replace(a, b)
    t.encode('ascii')
    return t


def main():
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    files = (('go_s9.sh', GO), ('sc_s9.py', SC), ('test_sc_s9.py', TSC), ('test_go_s9.py', TGO), ('mut_sc_s9.py', MUT))
    out = {}
    for name, reps in files:
        src = open(D + name, 'rb').read().decode('ascii')
        if '\r' in src:
            raise SystemExit('CRLF in %s' % name)
        out[name] = rep(src, reps, name)
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    os.makedirs(ORIG, exist_ok=True)
    for name, _ in files:
        if not os.path.exists(ORIG + name):
            shutil.copy2(D + name, ORIG + name)
    for name, _ in files:
        open(D + name, 'wb').write(out[name].encode('ascii'))
        print('patched %s' % name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
