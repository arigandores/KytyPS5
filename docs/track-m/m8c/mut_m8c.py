"""Track M, M8c (HPP-860), step 0 (RC3 of M8b, ROADMAP s122 item 783(g)): the required stand mutants m1..m4 and m9 against
the T125 stand with the MaxDiff fix, on one tree (main worktree m8c/wtmain or MS2 worktree m8c/wt). Copy of
docs/track-m/m8b/mut_m8b.py (substitutions m1..m4, m9 byte for byte; m5..m8, m10 not run - item 783(g) names m1-m4, m9).
A mutant is CAUGHT when the driver run_stand_m8a.py prints FAIL; every mutant here must be CAUGHT; the control (restored
tree) must give ALL OK.
Usage: python mut_m8c.py <main|wt> [--only <name>]   Output: mut_m8c_<tree>.out.txt beside; last line ALL OK or FAIL."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m8c'
TREE = sys.argv[1]
assert TREE in ('main', 'wt')
WT = HERE + ('/wtmain' if TREE == 'main' else '/wt')
EXE = HERE + ('/buildmain' if TREE == 'main' else '/build') + '/m_t125_stand.exe'
CMD = 'build_m8c_main.cmd' if TREE == 'main' else 'build_m8c.cmd'
DRIVER = 'C:/kyty/KytyPS5/docs/track-m/m8a/run_stand_m8a.py'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
A2 = 'src/libs/libAudio2.cpp'
T = chr(9)
NL = chr(10)
BS = chr(92)

MUTANTS = [
    ('m1_no_gain', [(A2, T + 'left *= object.m125_gain;' + NL + T + 'right *= object.m125_gain;' + NL, '')]),
    ('m2_no_format_check', [(A2, T + '       (state.audio_format == AudioInternal::Format::FloatMono ||' + NL + T +
                             '        state.audio_format == AudioInternal::Format::Signed16bitMono) &&' + NL, '')]),
    ('m3_mix_at_0', [(A2, T + 'if (MT125On()) {' + NL + T + T + 'audioout2_m125_queue_context_audio(ctx, blocking);',
                      T + 'if (true) {' + NL + T + T + 'audioout2_m125_queue_context_audio(ctx, blocking);'),
                     (A2, T + 'if (MT125On() && params->max_object_ports > 0) {',
                      T + 'if (params->max_object_ports > 0) {')]),
    ('m4_one_object_lost', [(A2, T * 5 + 'mixed = true;' + NL + T * 4 + '}' + NL,
                             T * 5 + 'mixed = true;' + NL + T * 5 + 'continue;' + NL + T * 4 + '}' + NL)]),
    ('m9_gain_nan_accepted', [(A2, '[](float v) { return std::isfinite(v) && v >= 0.0f; });',
                               '[](float v) { return !(v < 0.0f); });')]),
]

out_lines = []
OUT = '%s/mut_m8c_%s.out.txt' % (HERE, TREE)


def say(s):
    print(s)
    out_lines.append(s)


def flush():
    open(OUT, 'w', encoding='utf-8', newline=NL).write(NL.join(out_lines) + NL)


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        say('LOCK or STOP')
        flush()
        sys.exit(3)


def build(tag):
    guard()
    os.makedirs('%s/mut_%s' % (HERE, TREE), exist_ok=True)
    log = '%s/mut_%s/build_%s.log' % (HERE, TREE, tag)
    cmd = 'C:' + BS + 'kyty' + BS + 'm657' + BS + 'm8c' + BS + CMD + ' target m_t125_stand'
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c', cmd], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def drive(tag):
    guard()
    base = '%s/mut_%s/run_%s' % (HERE, TREE, tag)
    os.makedirs(base, exist_ok=True)
    p = subprocess.run(['python', DRIVER, EXE, base], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(base + '/driver.out.txt', 'w', encoding='utf-8', newline=NL).write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    fails = [ln for ln in text.splitlines() if ' FAIL' in ln]
    return last, fails


def member_fails(tag):
    r = []
    for mode in ('0', '1'):
        path = '%s/mut_%s/run_%s/stand_m%s.out.txt' % (HERE, TREE, tag, mode)
        if os.path.exists(path):
            for ln in open(path, encoding='utf-8', errors='replace').read().splitlines():
                if ln.startswith('MEMBER ') and ' FAIL' in ln:
                    r.append('m%s:%s' % (mode, ln[7:100]))
    return r


only = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--only' else None
say('tree %s %s exe %s' % (TREE, WT, EXE))
all_ok = True
for name, subs in MUTANTS:
    if only and name != only:
        continue
    guard()
    saved = {}
    applied = True
    for path, old, new in subs:
        full = WT + '/' + path
        if full not in saved:
            saved[full] = open(full, 'rb').read()
        text = open(full, 'rb').read().decode('utf-8')
        if text.count(old) != 1:
            say('MUTANT %s ANCHOR count=%d %r' % (name, text.count(old), old[:60]))
            applied = False
            break
        open(full, 'wb').write(text.replace(old, new).encode('utf-8'))
    if applied:
        if not build(name):
            say('MUTANT %s BUILD_FAILED' % name)
            all_ok = False
        else:
            last, fails = drive(name)
            caught = last == 'FAIL'
            mf = member_fails(name)
            say('MUTANT %s %s first=%s members=%d %s' % (name, 'CAUGHT' if caught else 'SURVIVED',
                                                       fails[0] if fails else '-', len(mf), '; '.join(mf[:3])))
            all_ok &= caught
    else:
        all_ok = False
    for full, data in saved.items():
        open(full, 'wb').write(data)
        assert hashlib.sha256(open(full, 'rb').read()).hexdigest() == hashlib.sha256(data).hexdigest()
    flush()

if not only:
    if build('control'):
        last, fails = drive('control')
        say('CONTROL %s' % last)
        all_ok &= last == 'ALL OK'
    else:
        say('CONTROL BUILD_FAILED')
        all_ok = False
say('ALL OK' if all_ok else 'FAIL')
flush()
sys.exit(0 if all_ok else 1)
