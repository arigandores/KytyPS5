"""p428.py - S13a2 (HPP-498, ROADMAP item 428 (v)): patch sc_s13.py, go_s13.py, test_sc_s13.py, test_go_s13.py, mut_sc_s13.py
from C:/kyty/s288/s13 into <out dir>: Z3 (KYTY_S_PCW=1 named on every arm, the S-pcw: line against the env), V7 (entry,
KNOWN_SCENES_ENTERED), seal 09 -> 11.  Every replacement must match its count.  ASCII, LF.
    python p428.py <out dir>
"""
import os
import re
import sys

SRC = 'C:/kyty/s288/s13'
OUT = sys.argv[1]
NL = chr(10)
LOG = []


def load(name):
    b = open(os.path.join(SRC, name), 'rb').read()
    assert b'\r' not in b, name
    return b.decode('ascii')


def rep(name, t, old, new, n=1):
    c = t.count(old)
    if c != n:
        raise SystemExit('%s: %d matches (want %d) of %r' % (name, c, n, old[:120]))
    LOG.append('%s: replaced %d x %r' % (name, n, old[:70]))
    return t.replace(old, new)


def renum(name, t):
    """seal 09 -> 11: 09b_s -> 11b_s, 09_s -> 11_s, the words 09b / 09."""
    for a, b in (('09b_s', '11b_s'), ('09_s', '11_s')):
        k = t.count(a)
        t = t.replace(a, b)
        LOG.append('%s: %s -> %s %d' % (name, a, b, k))
    for rx, b in ((r'\b09b\b', '11b'), (r'\b09\b', '11')):
        hits = [t[max(0, m.start() - 30):m.end() + 10].replace(NL, ' ') for m in re.finditer(rx, t)]
        t = re.sub(rx, b, t)
        LOG.append('%s: %s -> %s %d: %s' % (name, rx, b, len(hits), ' | '.join(hits)))
    return t


def save(name, t):
    t.encode('ascii')
    with open(os.path.join(OUT, name), 'wb') as f:
        f.write(t.encode('ascii'))


# ======================================================================================================== sc_s13.py
N = 'sc_s13.py'
t = renum(N, load(N))
t = rep(N, t, "(d)(2)); the arms run in link S13b under the lock, files in C:/kyty/s288/s13.",
        "(d)(2), item 419 (v) Z3, item 428 (v), (g)); the arms run in link S13b under the lock, files in C:/kyty/s288/s13.")
t = rep(N, t, '<variant>" - no install; item 414 (b): the arm binary is read from the field binary_sha256 of <tag>.json):',
        '<variant>" - no install; item 414 (b): the arm binary is read from the field binary_sha256 of <tag>.json; item 419 (v) Z3,' + NL +
        'item 428 (v)(1): every arm names KYTY_S_PCW=1 in its environment, every S-pcw: line of its log = that value):')
t = rep(N, t, "  alone and of (e)(3) alone are printed beside.  Decisions are the lead's (S13c)." + NL,
        "  alone and of (e)(3) alone are printed beside.  ENTRY (item 428 (g), V7): a level of the 19 is \"not enterable by -lvl\" when" + NL +
        "  NEITHER its k arm NOR its u arm carries the line \"Level has started: <level>\" in an attempt without a death marker (nor" + NL +
        "  hold_exit / ENDED / exited) and without a window event (minimized / Recovering Vulkan swapchain) - entry_state 'no' on both;" + NL +
        "  the word KNOWN_SCENES_ENTERED over the U arms of the levels outside \"not enterable\": PASS - every one PASS and w13 PASS with" + NL +
        "  a denominator >= 1; FAIL - any FAIL; else UNDETERMINED; printed beside KNOWN_SCENES (unchanged) with the list \"not" + NL +
        "  enterable\".  Decisions are the lead's (S13c)." + NL)
t = rep(N, t, "SEAL_BASE = 'C:/kyty/s288/pred/11_s.md'       # the seal of S13a: the line \"installed: PENDING\"" + NL,
        "SEAL_BASE = 'C:/kyty/s288/pred/11_s.md'       # the seal of S13a2: \"installed: PENDING\" (item 428 (v)(4): 09 not in force)" + NL)
t = rep(N, t, "SPCW_LINE = 'S-pcw: KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=0'          # item 408 (l): the arms run with the knobs S = 1 (S12d)" + NL,
        "SPCW_ENV = '1'                   # item 419 (v) Z3, item 428 (v)(1): every arm names KYTY_S_PCW=1 (absent means 1 after S12)" + NL +
        "SPCW_FMT = 'S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=0'           # the form of sc_s9.py: the log line = the env of the arm" + NL)
t = rep(N, t, "             KYTY_GUEST_ARGS='-lvl %s' % spec['level'], KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')" + NL +
        "    if spec['cls'] == 'T':",
        "             KYTY_GUEST_ARGS='-lvl %s' % spec['level'], KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0'," + NL +
        "             KYTY_S_PCW=SPCW_ENV)" + NL +
        "    if spec['cls'] == 'T':")
t = rep(N, t, "    add('no KYTY_S_PCW / KYTY_FIX_* in the env (the shipped defaults of the installed binary)'," + NL +
        "        not any(k.startswith(('KYTY_S_PCW', 'KYTY_FIX_')) for k in env), ','.join(k for k in env if" + NL +
        "                                                                              k.startswith(('KYTY_S_PCW', 'KYTY_FIX_'))))" + NL,
        "    add('KYTY_S_PCW=%s named in the env (item 419 (v) Z3, item 428 (v)(2))' % SPCW_ENV, env.get('KYTY_S_PCW') == SPCW_ENV," + NL +
        "        env.get('KYTY_S_PCW') or 'absent')" + NL +
        "    add('no KYTY_S_PCW_FORCE_MS / KYTY_FIX_* in the env (item 428 (v)(1))'," + NL +
        "        not any(k == 'KYTY_S_PCW_FORCE_MS' or k.startswith('KYTY_FIX_') for k in env)," + NL +
        "        ','.join(k for k in env if k == 'KYTY_S_PCW_FORCE_MS' or k.startswith('KYTY_FIX_')))" + NL)
t = rep(N, t, "    r['admit'].append(('the knob line \"%s\" (S12d: knobs S = 1), every S-pcw: line' % SPCW_LINE," + NL +
        "                       len(s['spcw']) >= 1 and all(x == SPCW_LINE for x in s['spcw']), ';'.join(s['spcw'][:2]) or 'none'))" + NL,
        "    pv = (js.get('env') or {}).get('KYTY_S_PCW')" + NL +
        "    r['admit'].append(('every S-pcw: line (>= 1) = \"%s\" with the KYTY_S_PCW of the env of the arm (item 419 (v) Z3)' % SPCW_FMT," + NL +
        "                       len(s['spcw']) >= 1 and all(x == SPCW_FMT % pv for x in s['spcw'])," + NL +
        "                       '%s / env %s' % (';'.join(s['spcw'][:2]) or 'none', pv)))" + NL)
t = rep(N, t, NL + NL + "def arm_word(ms):" + NL,
        NL + NL + "def death(r):" + NL +
        "    \"\"\"A death marker of sc142 or hold_exit / ENDED / exited (the predicate of E3-death).\"\"\"" + NL +
        "    return bool(r.get('marks')) or bool(r.get('ended')) or bool(r.get('exited'))" + NL + NL + NL +
        "def entry_state(r):" + NL +
        "    \"\"\"Item 428 (g), V7: the field \"entered\" of one arm - ('yes', why) the log carries \"Level has started: <level>\"; ('no', why)" + NL +
        "    an attempt with a log, without the line, without a death marker (nor hold_exit / ENDED / exited) and without a window event" + NL +
        "    (minimized / Recovering Vulkan swapchain); ('void', why) otherwise (not made, no log, a death marker or a window event" + NL +
        "    without the line) - not evidence that -lvl does not enter the level.\"\"\"" + NL +
        "    if r is None:" + NL +
        "        return 'void', 'not made'" + NL +
        "    if r.get('entered'):" + NL +
        "        return 'yes', 'Level has started'" + NL +
        "    if 'window' not in r:" + NL +
        "        return 'void', 'no log'" + NL +
        "    if death(r):" + NL +
        "        return 'void', 'a death marker without the entry line'" + NL +
        "    w = r.get('window') or {}" + NL +
        "    if w.get('minimized', 0) or w.get('recover', 0):" + NL +
        "        return 'void', 'a window event without the entry line'" + NL +
        "    return 'no', 'no entry line in a clean attempt'" + NL + NL + NL +
        "def not_enterable(get):" + NL +
        "    \"\"\"Item 428 (g): per level of the 19 (level, entry of k_NN, entry of u_NN, not enterable) - not enterable by -lvl when both" + NL +
        "    arms are 'no' [c of two logs].\"\"\"" + NL +
        "    rows = []" + NL +
        "    for lv, kt, ut in zip(LIST13, K_TAGS, U_TAGS):" + NL +
        "        ks, us = entry_state(get(kt)), entry_state(get(ut))" + NL +
        "        rows.append((lv, ks, us, ks[0] == 'no' and us[0] == 'no'))" + NL +
        "    return rows" + NL + NL + NL +
        "def entered_word(excl, wall, ww):" + NL +
        "    \"\"\"Item 428 (g): (word, words of the U arms in the denominator) - the U arms of the levels outside \"not enterable\": PASS" + NL +
        "    when every one and w13 PASS with a denominator >= 1; FAIL on any FAIL (w13 included); else UNDETERMINED.\"\"\"" + NL +
        "    den = [w for w, x in zip(wall, excl) if not x]" + NL +
        "    word = sub_word(den + [ww])" + NL +
        "    if word == 'PASS' and not den:" + NL +
        "        word = 'UNDETERMINED'" + NL +
        "    return word, den" + NL + NL + NL +
        "def arm_word(ms):" + NL)
t = rep(N, t, "                                                   N_KNOWN, ww))" + NL + "    return word, out" + NL,
        "                                                   N_KNOWN, ww))" + NL +
        "    ent = not_enterable(get)" + NL +
        "    for (lv, ks, us, x), t in zip(ent, U_TAGS):" + NL +
        "        out.append('entry %s %-30s k %s (%s), u %s (%s) -> %s' % (t, lv, ks[0], ks[1], us[0], us[1]," + NL +
        "                                                                 'NOT ENTERABLE by -lvl' if x else 'in the denominator'))" + NL +
        "    wE, den = entered_word([x for _, _, _, x in ent], wall, ww)" + NL +
        "    out.append('KNOWN_SCENES_ENTERED (item 428 (g), V7: the levels outside \"not enterable\"): %s - denominator %d of %d, arms '" + NL +
        "               'PASS %d / FAIL %d / UNDETERMINED %d, W %s; not enterable by -lvl: %s' % (" + NL +
        "                   wE, len(den), N_KNOWN, den.count('PASS'), den.count('FAIL'), den.count('UNDETERMINED'), ww," + NL +
        "                   ' '.join(lv for lv, _, _, x in ent if x) or 'none'))" + NL +
        "    return word, out" + NL)
t = rep(N, t, "        out.append('%s %-30s arm %s; entered %s first %s; recipes saved lines %s last %s; created %s ms; death markers %s; '" + NL +
        "                   'window %s' % (t, r['level'], 'PASS' if ok_arm(r) else 'FAIL %s' % r['fail'][:3], r.get('entered'),",
        "        out.append('%s %-30s arm %s; entered %s first %s; recipes saved lines %s last %s; created %s ms; death markers %s; '" + NL +
        "                   'window %s; entry %s' % (t, r['level'], 'PASS' if ok_arm(r) else 'FAIL %s' % r['fail'][:3], r.get('entered'),")
t = rep(N, t, "                                  ';'.join(m['kind'] for m in r['marks']) or 'none', r.get('window')))" + NL,
        "                                  ';'.join(m['kind'] for m in r['marks']) or 'none', r.get('window'), entry_state(r)))" + NL)
t = rep(N, t, "    g = r['glitch']" + NL + "    o.append('  video:",
        "    o.append('  entered (item 428 (g)): %s (%s)' % entry_state(r))" + NL + "    g = r['glitch']" + NL + "    o.append('  video:")
assert 'SPCW_LINE' not in t
save(N, t)

# ======================================================================================================== go_s13.sh
N = 'go_s13.sh'
t = renum(N, load(N))
t = rep(N, t, "item 410 (g)(6)(iii), item 414):" + NL,
        "item 410 (g)(6)(iii), item 414, item 419 (v) Z3, item 428 (v)):" + NL)
t = rep(N, t, "#   GUARD s13/IN_ARM:",
        "#   KNOB (item 419 (v) Z3, item 428 (v)(1)): every arm names KYTY_S_PCW=1 positionally (SPCW, after S12 an absent knob means 1);" + NL +
        "#     the caller's KYTY_S_PCW, KYTY_S_PCW_FORCE_MS, KYTY_GAME_PATCH and every KYTY_FIX_* are unset before the arm." + NL +
        "#   GUARD s13/IN_ARM:")
t = rep(N, t, "# item 342 (e): no S13b arm names a patch file; the knobs of the installed binary stay at their shipped defaults" + NL +
        "unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA VK_LAYER_MESSAGE_ID_FILTER KYTY_GAME_PATCH KYTY_S_PCW KYTY_S_PCW_FORCE_MS" + NL,
        "# item 342 (e): no S13b arm names a patch file; item 428 (v)(1): the caller's S knobs and KYTY_FIX_* never reach an arm" + NL +
        "unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA VK_LAYER_MESSAGE_ID_FILTER KYTY_GAME_PATCH KYTY_S_PCW KYTY_S_PCW_FORCE_MS" + NL +
        "for V in $(compgen -e); do case \"$V\" in KYTY_FIX_*) unset \"$V\";; esac; done" + NL +
        "SPCW=1   # item 419 (v) Z3, item 428 (v)(1): every arm names KYTY_S_PCW=1 itself (after S12 an absent knob means 1, not 0)" + NL)
t = rep(N, t, "KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 $CLSX $UX $VALE\"",
        "KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_S_PCW=$SPCW $CLSX $UX $VALE\"")
save(N, t)

# ======================================================================================================== test_sc_s13.py
N = 'test_sc_s13.py'
t = renum(N, load(N))
t = rep(N, t, "(e), item 371 (v), item 410 (g)(6)(iii), item 414 (b), (g)(1), (g)(5)-(7))." + NL,
        "(e), item 371 (v), item 410 (g)(6)(iii), item 414 (b), (g)(1), (g)(5)-(7), item 419 (v) Z3, item 428 (v), (g))." + NL +
        "S13a2 (item 428): KYTY_S_PCW=1 named on every arm (absent / 0 / FORCE_MS / KYTY_FIX_* FAIL), every S-pcw: line against the env" + NL +
        "of the arm (a line other than the env FAILS, a line = an env of 0 passes that row), the field \"entered\" and the word" + NL +
        "KNOWN_SCENES_ENTERED at every edge (Q1-Q13)." + NL)
t = rep(N, t, "ok &= case('C1 environment k: the base + CLOCK_PIN + MARKERS, no trace, no seed path, no cache mode'," + NL +
        "           e == dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1'," + NL +
        "                     KYTY_GUEST_ARGS='-lvl title_controller_ship', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0'))" + NL,
        "ok &= case('C1 environment k: the base + CLOCK_PIN + MARKERS + KYTY_S_PCW=1 (item 428 (v)(1)), no trace, no seed path, no '" + NL +
        "           'cache mode', e == dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1'," + NL +
        "                                 KYTY_GUEST_ARGS='-lvl title_controller_ship', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0'," + NL +
        "                                 KYTY_S_PCW='1'))" + NL)
t = rep(N, t, "ok &= case('C9 a KYTY_FIX_* key in the env: the family row FAILS', not fo)" + NL,
        "ok &= case('C9 a KYTY_FIX_* key in the env: the family row FAILS', not fo)" + NL +
        "(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_S_PCW=None))" + NL +
        "ok &= case('C10 no KYTY_S_PCW in the env (item 428 (v)(1)) -> the family row FAILS naming it', not fo and 'KYTY_S_PCW' in fd)" + NL +
        "(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_S_PCW_FORCE_MS='0'))" + NL +
        "ok &= case('C11 KYTY_S_PCW_FORCE_MS in the env -> the family row FAILS naming it', not fo and 'KYTY_S_PCW_FORCE_MS' in fd)" + NL +
        "ok &= case('C12 every arm (k, u, w13) expects KYTY_S_PCW=1', all(S.expected_env(S.SPEC[t]).get('KYTY_S_PCW') == '1'" + NL +
        "                                                             for t in S.SEQ) and S.SPCW_ENV == '1')" + NL)
t = rep(N, t, "R_KNOB = 'no KYTY_S_PCW / KYTY_FIX_* in the env (the shipped defaults of the installed binary)'" + NL,
        "R_SPCW = 'KYTY_S_PCW=1 named in the env (item 419 (v) Z3, item 428 (v)(2))'" + NL +
        "R_FORCE = 'no KYTY_S_PCW_FORCE_MS / KYTY_FIX_* in the env (item 428 (v)(1))'" + NL)
t = rep(N, t, "ok &= case('J6 KYTY_S_PCW=1 / KYTY_FIX_B42=1 set in the env -> the knob row FAILS (shipped defaults)', R_KNOB in adm(" + NL +
        "    'u_01', js_for('u_01', env_over=dict(KYTY_S_PCW='1'))) and R_KNOB in adm('u_01', js_for('u_01', env_over=dict(KYTY_FIX_B42='1'))))" + NL,
        "ok &= case('J6 KYTY_S_PCW absent (u_01) / =0 (w13) / empty (k_01) in the env -> the row \"KYTY_S_PCW=1 named\" FAILS; =1 passes '" + NL +
        "           '(J1)', R_SPCW in adm('u_01', js_for('u_01', env_over=dict(KYTY_S_PCW=None))) and" + NL +
        "           R_SPCW in adm('w13', js_for('w13', env_over=dict(KYTY_S_PCW='0'))) and" + NL +
        "           R_SPCW in adm('k_01', js_for('k_01', env_over=dict(KYTY_S_PCW=''))) and R_SPCW not in adm('u_01', js_for('u_01')))" + NL +
        "ok &= case('J6b KYTY_S_PCW_FORCE_MS / KYTY_FIX_B42 in the env -> the force row FAILS; KYTY_FIXED (not the prefix KYTY_FIX_) -> not '" + NL +
        "           'that row', R_FORCE in adm('u_01', js_for('u_01', env_over=dict(KYTY_S_PCW_FORCE_MS='0'))) and" + NL +
        "           R_FORCE in adm('u_01', js_for('u_01', env_over=dict(KYTY_FIX_B42='1'))) and" + NL +
        "           R_FORCE not in adm('u_01', js_for('u_01', env_over=dict(KYTY_FIXED='1'))))" + NL)
t = rep(N, t, "ok &= case('K28 the knob line KYTY_S_PCW=0 -> admission FAILS (knobs S = 1); the E1 members undetermined, the arm UNDETERMINED',",
        "ok &= case('K28 the log line KYTY_S_PCW=0 against the env 1 -> the S-pcw: row FAILS (the log != the env); the E1 members '" + NL +
        "           'undetermined, the arm UNDETERMINED',")
t = rep(N, t, "ok &= case('K29 no knob line -> admission FAILS', any('S-pcw' in f for f in r['fail']))" + NL,
        "ok &= case('K29 no knob line -> admission FAILS', any('S-pcw' in f for f in r['fail']))" + NL +
        "r = make_arm('u_01', [x.replace('KYTY_S_PCW=1', 'KYTY_S_PCW=0') for x in scene(UL, post_rows(), header=HEADER_T)]," + NL +
        "             js=js_for('u_01', env_over=dict(KYTY_S_PCW='0')))" + NL +
        "ok &= case('K28b env KYTY_S_PCW=0 and the log line =0: the S-pcw: row PASSES (the log = the env), the env row FAILS (=0)'," + NL +
        "           ('admission: ' + R_SPCW) in r['fail'] and not any('S-pcw:' in f for f in r['fail']))" + NL +
        "r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), js=js_for('u_01', env_over=dict(KYTY_S_PCW=None)))" + NL +
        "ok &= case('K28c no KYTY_S_PCW in the env, the log line =1 -> the env row and the S-pcw: row FAIL'," + NL +
        "           ('admission: ' + R_SPCW) in r['fail'] and any('S-pcw:' in f for f in r['fail']))" + NL +
        "r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T + ['S-pcw: KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=0']))" + NL +
        "ok &= case('K28d two S-pcw: lines, the second =0 against the env 1 -> the S-pcw: row FAILS (every line)'," + NL +
        "           any('S-pcw:' in f for f in r['fail']) and not ('admission: ' + R_SPCW) in r['fail'])" + NL +
        "r = make_arm('u_01', [x.replace('KYTY_S_PCW_FORCE_MS=0', 'KYTY_S_PCW_FORCE_MS=15000') for x in" + NL +
        "                      scene(UL, post_rows(), header=HEADER_T)])" + NL +
        "ok &= case('K28e the log line with KYTY_S_PCW_FORCE_MS=15000 -> the S-pcw: row FAILS', any('S-pcw:' in f for f in r['fail']))" + NL)
t = rep(N, t, "# ================================================================================ order" + NL,
        "# ================================================================================ entry (item 428 (g), V7)" + NL +
        "def rec(**over):" + NL +
        "    d = dict(entered=False, window={}, marks=[], ended=False, exited=False)" + NL +
        "    d.update(over)" + NL +
        "    return d" + NL + NL + NL +
        "ok &= case('Q1 entry_state: not made -> void; the entry line -> yes; no log (no window field) -> void; a clean attempt without '" + NL +
        "           'the line -> no', S.entry_state(None)[0] == 'void' and S.entry_state(rec(entered=True))[0] == 'yes' and" + NL +
        "           S.entry_state(dict(entered=False, marks=[], ended=False, exited=False))[0] == 'void' and" + NL +
        "           S.entry_state(rec()) == ('no', 'no entry line in a clean attempt'))" + NL +
        "ok &= case('Q2 entry_state without the line: a death marker / hold_exit (ended) / exited / minimized / Recovering -> void; '" + NL +
        "           'restored only -> no; the entry line with a death marker -> yes'," + NL +
        "           S.entry_state(rec(marks=[dict(kind='crash')]))[0] == 'void' and S.entry_state(rec(ended=True))[0] == 'void' and" + NL +
        "           S.entry_state(rec(exited=True))[0] == 'void' and S.entry_state(rec(window={'minimized': 1}))[0] == 'void' and" + NL +
        "           S.entry_state(rec(window={'recover': 1}))[0] == 'void' and S.entry_state(rec(window={'restored': 2}))[0] == 'no' and" + NL +
        "           S.entry_state(rec(entered=True, marks=[dict(kind='crash')]))[0] == 'yes')" + NL +
        "rk = make_arm('k_04', scene('other_level', post_rows(), header=HEADER_M), video=False, sheet=False," + NL +
        "              stdout=['Cache test mode: none'])" + NL +
        "ru = make_arm('u_04', scene('other_level', post_rows(), header=HEADER_T))" + NL +
        "ok &= case('Q3 whole arms not entering ps_logo (k_04 class M, u_04 class T, clean) -> entry no on both; fmt_arm prints the field'," + NL +
        "           S.entry_state(rk)[0] == 'no' and S.entry_state(ru)[0] == 'no' and not rk['entered'] and" + NL +
        "           any(x.startswith('  entered (item 428 (g)): no (') for x in S.fmt_arm(ru)) and" + NL +
        "           any(x.startswith('  entered (item 428 (g)): yes (') for x in S.fmt_arm(clean)))" + NL +
        "UNO = copy.deepcopy(UCLEAN)" + NL +
        "UNO['entered'] = False" + NL +
        "ne = S.not_enterable(get_of({'k_04': rec(), 'u_04': UNO}))" + NL +
        "ok &= case('Q4 not_enterable: ps_logo with k_04 and u_04 both no -> True; the other 18 (k not made) -> False'," + NL +
        "           len(ne) == 19 and ne[3][0] == 'ps_logo' and ne[3][3] is True and ne[3][1][0] == 'no' and ne[3][2][0] == 'no' and" + NL +
        "           [x[3] for x in ne].count(True) == 1 and ne[0][1][0] == 'void' and ne[0][2][0] == 'yes')" + NL + NL + NL +
        "def ent_line(out):" + NL +
        "    return [x for x in out if x.startswith('KNOWN_SCENES_ENTERED')]" + NL + NL + NL +
        "word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UNO}))" + NL +
        "el = ent_line(out)" + NL +
        "ok &= case('Q5 ps_logo not entered in k_04 and u_04 (both clean) -> not enterable: KNOWN_SCENES UNDETERMINED (unchanged), '" + NL +
        "           'KNOWN_SCENES_ENTERED PASS on 18 of 19, the list names ps_logo, the entry line of u_04 NOT ENTERABLE'," + NL +
        "           word == 'UNDETERMINED' and len(el) == 1 and ': PASS - denominator 18 of 19' in el[0] and" + NL +
        "           el[0].endswith('not enterable by -lvl: ps_logo') and" + NL +
        "           any(x.startswith('entry u_04 ps_logo') and x.endswith('NOT ENTERABLE by -lvl') for x in out) and" + NL +
        "           any(x.startswith('entry u_01 ') and x.endswith('in the denominator') for x in out))" + NL +
        "word, out = S.read_known(get_of({'k_04': rec(entered=True), 'u_04': UNO}))" + NL +
        "ok &= case('Q6 entered in k_04 only -> in the denominator: u_04 UNDETERMINED -> KNOWN_SCENES_ENTERED UNDETERMINED on 19'," + NL +
        "           ': UNDETERMINED - denominator 19 of 19' in ent_line(out)[0] and ent_line(out)[0].endswith('lvl: none'))" + NL +
        "word, out = S.read_known(get_of({'k_04': rec(), 'u_04': copy.deepcopy(UCLEAN)}))" + NL +
        "ok &= case('Q7 k_04 no but u_04 entered -> in the denominator: PASS on 19', ': PASS - denominator 19 of 19' in ent_line(out)[0])" + NL +
        "word, out = S.read_known(get_of({'u_04': UNO}))" + NL +
        "ok &= case('Q8 k_04 not made (void) and u_04 no -> in the denominator: UNDETERMINED on 19'," + NL +
        "           ': UNDETERMINED - denominator 19 of 19' in ent_line(out)[0])" + NL +
        "UDEAD = copy.deepcopy(UNO)" + NL +
        "UDEAD['marks'] = [dict(kind='crash')]" + NL +
        "word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UDEAD}))" + NL +
        "ok &= case('Q9 u_04 without the line but with a death marker (void) -> in the denominator; its E3-death FAILS -> FAIL on 19'," + NL +
        "           ': FAIL - denominator 19 of 19' in ent_line(out)[0])" + NL +
        "UWIN = copy.deepcopy(UNO)" + NL +
        "UWIN['window'] = {'minimized': 1}" + NL +
        "word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UWIN}))" + NL +
        "ok &= case('Q10 u_04 without the line but with a window event (void) -> in the denominator: UNDETERMINED on 19'," + NL +
        "           ': UNDETERMINED - denominator 19 of 19' in ent_line(out)[0])" + NL +
        "bad = copy.deepcopy(w_ok)" + NL +
        "bad['vke'] = 1" + NL +
        "word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UNO}, bad))" + NL +
        "ok &= case('Q11 ps_logo not enterable and a [Vulkan][E] on w13 -> KNOWN_SCENES_ENTERED FAIL on 18'," + NL +
        "           ': FAIL - denominator 18 of 19' in ent_line(out)[0])" + NL +
        "ok &= case('Q12 entered_word: a denominator 0 with w13 PASS -> UNDETERMINED; an excluded FAIL arm is not counted -> PASS; a FAIL '" + NL +
        "           'in the denominator -> FAIL; w13 FAIL / UNDETERMINED -> FAIL / UNDETERMINED'," + NL +
        "           S.entered_word([True] * 19, ['UNDETERMINED'] * 19, 'PASS') == ('UNDETERMINED', []) and" + NL +
        "           S.entered_word([True] + [False] * 18, ['FAIL'] + ['PASS'] * 18, 'PASS') == ('PASS', ['PASS'] * 18) and" + NL +
        "           S.entered_word([False] * 19, ['PASS'] * 18 + ['FAIL'], 'PASS')[0] == 'FAIL' and" + NL +
        "           S.entered_word([True] * 19, ['PASS'] * 19, 'FAIL')[0] == 'FAIL' and" + NL +
        "           S.entered_word([False] * 19, ['PASS'] * 19, 'UNDETERMINED')[0] == 'UNDETERMINED' and" + NL +
        "           S.entered_word([False] * 19, ['PASS'] * 19, 'PASS') == ('PASS', ['PASS'] * 19))" + NL +
        "word, out = S.read_known(get_of())" + NL +
        "ok &= case('Q13 19 clean U arms and a clean W -> KNOWN_SCENES PASS and KNOWN_SCENES_ENTERED PASS on 19, list none'," + NL +
        "           word == 'PASS' and ': PASS - denominator 19 of 19' in ent_line(out)[0] and ent_line(out)[0].endswith('lvl: none'))" + NL +
        "# ================================================================================ order" + NL)
t = rep(N, t, "           'READ collection arms' in o2 and 'READ export:' in o2 and 'KNOWN_SCENES (item 229 (e)(1) with (3)): UNDETERMINED' in o2)" + NL,
        "           'READ collection arms' in o2 and 'READ export:' in o2 and 'KNOWN_SCENES (item 229 (e)(1) with (3)): UNDETERMINED' in o2" + NL +
        "           and 'KNOWN_SCENES_ENTERED (item 428 (g)' in o2 and 'entry u_04 ps_logo' in o2)" + NL)
save(N, t)

# ======================================================================================================== test_go_s13.py
N = 'test_go_s13.py'
t = renum(N, load(N))
t = rep(N, t, "interference, IN_ARM written and removed, a hanging IN_ARM -> rc 1, an installed binary other than the seal line -> rc 1 inside" + NL,
        "interference, IN_ARM written and removed, a hanging IN_ARM -> rc 1, an installed binary other than the seal line -> rc 1 inside" + NL)
t = rep(N, t, "the lock; S9r2 observation 1 - a failed return leaves IN_ARM and RETURN_FAILED; observation 2 - the lock line names the seal." + NL,
        "the lock; S9r2 observation 1 - a failed return leaves IN_ARM and RETURN_FAILED; observation 2 - the lock line names the seal." + NL +
        "S13a2 (item 419 (v) Z3, item 428 (v)(1)): every plan of the 39 arms names KYTY_S_PCW=1 once; the caller's KYTY_S_PCW," + NL +
        "KYTY_S_PCW_FORCE_MS and KYTY_FIX_* never reach the game, KYTY_S_PCW=1 goes positionally to enter_scene_s9.py." + NL)
t = rep(N, t, "ok &= case('G18 no arm names KYTY_GAME_PATCH, KYTY_S_PCW or KYTY_FIX_', all('GAME_PATCH' not in v[1] and 'KYTY_S_PCW' not in v[1]" + NL +
        "                                                                          and 'KYTY_FIX_' not in v[1] for v in out.values()))" + NL,
        "ok &= case('G18 every arm kind names KYTY_S_PCW=1 once (item 419 (v) Z3, item 428 (v)(1)); none names KYTY_S_PCW_FORCE_MS, '" + NL +
        "           'KYTY_GAME_PATCH or KYTY_FIX_', all(v[1].count(' KYTY_S_PCW=1 ') == 1 and v[1].count('KYTY_S_PCW') == 1 and" + NL +
        "                                              'GAME_PATCH' not in v[1] and 'KYTY_FIX_' not in v[1] for v in out.values()))" + NL +
        "plans2 = dict((tg, go(tg, dry='2')) for tg in TAGS)" + NL +
        "ok &= case('G18b DRY=2 of all 39 arms: rc 0, each plan names KYTY_S_PCW=1 once and no other S knob', len(plans2) == 39 and all(" + NL +
        "    v[0] == 0 and v[1].count(' KYTY_S_PCW=1 ') == 1 and v[1].count('KYTY_S_PCW') == 1 for v in plans2.values()))" + NL)
t = rep(N, t, "           'PRED=$(python $SC --seal-path' in src_t and src_t.count('guardfiles' + NL) == 2 and 'seal 06' not in src_t)" + NL,
        "           'PRED=$(python $SC --seal-path' in src_t and src_t.count('guardfiles' + NL) == 2 and 'seal 06' not in src_t and" + NL +
        "           'for V in $(compgen -e); do case \"$V\" in KYTY_FIX_*) unset \"$V\";; esac; done' + NL in src_t and" + NL +
        "           ('SPCW=1 ' in src_t) and 'KYTY_GPU_MARKERS=0 KYTY_S_PCW=$SPCW $CLSX' in src_t)" + NL)
t = rep(N, t, "\"json.dump({'tag': tag, 'gp': os.environ.get('KYTY_GAME_PATCH'), 'spcw': os.environ.get('KYTY_S_PCW'), 'seen': seen, \"",
        "\"json.dump({'tag': tag, 'gp': os.environ.get('KYTY_GAME_PATCH'), 'spcw': os.environ.get('KYTY_S_PCW'), 'seen': seen, \"" + NL +
        "    \"'fix': sorted(k for k in os.environ if k.startswith('KYTY_FIX_') or k == 'KYTY_S_PCW_FORCE_MS'), \"")
t = rep(N, t, "rc, o = go2('k_01', KYTY_S_PCW='0')" + NL,
        "rc, o = go2('k_01', KYTY_S_PCW='0', KYTY_S_PCW_FORCE_MS='15000', KYTY_FIX_B42='1')" + NL)
t = rep(N, t, "ok &= case('GL2 k_01: the game saw NO app cache file (the empty set), GLCache as found (no restore), KYTY_S_PCW of the caller '" + NL +
        "           'not seen; the installed caches and GLCache back after', j.get('seen') == [] and 'y.bin' in j.get('glc', []) and" + NL +
        "           j.get('spcw') is None and",
        "ok &= case('GL2 k_01: the game saw NO app cache file (the empty set), GLCache as found (no restore), KYTY_S_PCW / '" + NL +
        "           'KYTY_S_PCW_FORCE_MS / KYTY_FIX_B42 of the caller not seen, KYTY_S_PCW=1 passed positionally; the installed caches and '" + NL +
        "           'GLCache back after', j.get('seen') == [] and 'y.bin' in j.get('glc', []) and" + NL +
        "           j.get('spcw') is None and j.get('fix') == [] and 'KYTY_S_PCW=1' in j.get('argv', []) and")
t = rep(N, t, "           '--emu-arg=--vulkan-validation' in j.get('argv', []) and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000' in j.get('argv', []))" + NL,
        "           '--emu-arg=--vulkan-validation' in j.get('argv', []) and 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000' in j.get('argv', [])" + NL +
        "           and 'KYTY_S_PCW=1' in j.get('argv', []) and 'KYTY_S_PCW=1' in js2('u_01').get('argv', []))" + NL)
save(N, t)

# ======================================================================================================== mut_sc_s13.py
N = 'mut_sc_s13.py'
t = renum(N, load(N))
t = rep(N, t, "Track S link S13a (HPP-498; ROADMAP \"SESSION 122\" item 408 (l), item 229 (e)(1), (3), item 414): mutants of s13/sc_s13.py -",
        "Track S link S13a2 (HPP-498; ROADMAP \"SESSION 122\" item 408 (l), item 229 (e)(1), (3), item 414, item 428): mutants of s13/sc_s13.py -")
t = rep(N, t, "    ('spcw', \"SPCW_LINE = 'S-pcw: KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=0'\", \"SPCW_LINE = 'S-pcw: KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=0'\")," + NL,
        "    ('spcw_env', \"SPCW_ENV = '1' \", \"SPCW_ENV = '0' \")," + NL +
        "    ('spcw_fmt', \"SPCW_FMT = 'S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=0'\", \"SPCW_FMT = 'S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=1'\")," + NL)
t = rep(N, t, "    ('env_pin', \"KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')\", \"KYTY_GPU_CLOCK_PIN='1')\")," + NL,
        "    ('env_pin', \"KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0',\\n\", \"KYTY_GPU_CLOCK_PIN='1',\\n\")," + NL +
        "    ('env_spcw', \"KYTY_GPU_MARKERS='0',\\n             KYTY_S_PCW=SPCW_ENV)\", \"KYTY_GPU_MARKERS='0')\")," + NL)
t = rep(N, t, "    ('ad_knobs', \"        not any(k.startswith(('KYTY_S_PCW', 'KYTY_FIX_')) for k in env),\", \"        not any(k.startswith(('KYTY_FIX_',)) for k in env),\")," + NL,
        "    ('ad_spcw_env', \"env.get('KYTY_S_PCW') == SPCW_ENV,\\n\", \"True,\\n\")," + NL +
        "    ('ad_force', \"not any(k == 'KYTY_S_PCW_FORCE_MS' or k.startswith('KYTY_FIX_') for k in env),\", \"not any(k.startswith('KYTY_FIX_') for k in env),\")," + NL +
        "    ('ad_fix', \"not any(k == 'KYTY_S_PCW_FORCE_MS' or k.startswith('KYTY_FIX_') for k in env),\", \"not any(k == 'KYTY_S_PCW_FORCE_MS' for k in env),\")," + NL +
        "    ('ad_fix_prefix', \"or k.startswith('KYTY_FIX_') for k in env),\", \"or k.startswith('KYTY_FIX') for k in env),\")," + NL)
t = rep(N, t, "    ('sa_spcw', \"len(s['spcw']) >= 1 and all(x == SPCW_LINE for x in s['spcw']),\", \"all(x == SPCW_LINE for x in s['spcw']),\")," + NL +
        "    ('sa_spcw_all', \"len(s['spcw']) >= 1 and all(x == SPCW_LINE for x in s['spcw']),\", \"len(s['spcw']) >= 1,\")," + NL,
        "    ('sa_spcw', \"len(s['spcw']) >= 1 and all(x == SPCW_FMT % pv for x in s['spcw']),\", \"all(x == SPCW_FMT % pv for x in s['spcw']),\")," + NL +
        "    ('sa_spcw_all', \"len(s['spcw']) >= 1 and all(x == SPCW_FMT % pv for x in s['spcw']),\", \"len(s['spcw']) >= 1,\")," + NL +
        "    ('sa_spcw_env', \"all(x == SPCW_FMT % pv for x in s['spcw']),\", \"all(x == SPCW_FMT % SPCW_ENV for x in s['spcw']),\")," + NL +
        "    ('sa_pv_key', \"pv = (js.get('env') or {}).get('KYTY_S_PCW')\", \"pv = (js.get('env') or {}).get('KYTY_S_PCW_FORCE_MS')\")," + NL)
t = rep(N, t, "    # order" + NL,
        "    # entry (item 428 (g), V7)" + NL +
        "    ('de_marks', \"return bool(r.get('marks')) or bool(r.get('ended')) or bool(r.get('exited'))\", \"return bool(r.get('ended')) or bool(r.get('exited'))\")," + NL +
        "    ('de_ended', \"return bool(r.get('marks')) or bool(r.get('ended')) or bool(r.get('exited'))\", \"return bool(r.get('marks')) or bool(r.get('exited'))\")," + NL +
        "    ('de_exited', \"return bool(r.get('marks')) or bool(r.get('ended')) or bool(r.get('exited'))\", \"return bool(r.get('marks')) or bool(r.get('ended'))\")," + NL +
        "    ('es_none', \"        return 'void', 'not made'\", \"        return 'no', 'not made'\")," + NL +
        "    ('es_yes', \"    if r.get('entered'):\\n        return 'yes'\", \"    if False:\\n        return 'yes'\")," + NL +
        "    ('es_nolog_key', \"    if 'window' not in r:\\n        return 'void', 'no log'\", \"    if False:\\n        return 'void', 'no log'\")," + NL +
        "    ('es_nolog', \"        return 'void', 'no log'\", \"        return 'no', 'no log'\")," + NL +
        "    ('es_death', \"    if death(r):\\n        return 'void'\", \"    if False:\\n        return 'void'\")," + NL +
        "    ('es_min', \"    if w.get('minimized', 0) or w.get('recover', 0):\", \"    if w.get('recover', 0):\")," + NL +
        "    ('es_rec', \"    if w.get('minimized', 0) or w.get('recover', 0):\", \"    if w.get('minimized', 0):\")," + NL +
        "    ('es_no', \"    return 'no', 'no entry line in a clean attempt'\", \"    return 'void', 'no entry line in a clean attempt'\")," + NL +
        "    ('ne_and', \"rows.append((lv, ks, us, ks[0] == 'no' and us[0] == 'no'))\", \"rows.append((lv, ks, us, ks[0] == 'no' or us[0] == 'no'))\")," + NL +
        "    ('ne_k', \"rows.append((lv, ks, us, ks[0] == 'no' and us[0] == 'no'))\", \"rows.append((lv, ks, us, us[0] == 'no'))\")," + NL +
        "    ('ne_u', \"rows.append((lv, ks, us, ks[0] == 'no' and us[0] == 'no'))\", \"rows.append((lv, ks, us, ks[0] == 'no'))\")," + NL +
        "    ('ne_tags', \"ks, us = entry_state(get(kt)), entry_state(get(ut))\", \"ks, us = entry_state(get(ut)), entry_state(get(ut))\")," + NL +
        "    ('ew_excl', \"    den = [w for w, x in zip(wall, excl) if not x]\", \"    den = list(wall)\")," + NL +
        "    ('ew_ww', \"    word = sub_word(den + [ww])\", \"    word = sub_word(den)\")," + NL +
        "    ('ew_zero', \"    if word == 'PASS' and not den:\\n        word = 'UNDETERMINED'\", \"    if False:\\n        word = 'UNDETERMINED'\")," + NL +
        "    ('rk_ent_list', \"' '.join(lv for lv, _, _, x in ent if x) or 'none'))\", \"' '.join(lv for lv, _, _, x in ent) or 'none'))\")," + NL +
        "    ('rk_ent_flag', \"wE, den = entered_word([x for _, _, _, x in ent], wall, ww)\", \"wE, den = entered_word([False for _ in ent], wall, ww)\")," + NL +
        "    # order" + NL)
save(N, t)
print(NL.join(LOG))
print('P428: OK')
