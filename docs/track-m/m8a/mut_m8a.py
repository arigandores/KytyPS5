"""Track M, M8a (HPP-858, ROADMAP s122 item 778(g)(2)(ii)): mutants of T125 against the stand (run_stand_m8a.py). Each
mutant is a list of exact text substitutions (each must match once) in the worktree C:/kyty/m657/m8a/wt; the stand target
m_t125_stand is rebuilt (build_m8a.cmd target m_t125_stand, IDLE priority), the driver runs, the file is restored byte for
byte. A mutant is CAUGHT when the driver prints FAIL. At the end the stand is rebuilt from the restored tree and the driver
must print ALL OK again (the restoration control). Required by item 778(g)(2)(ii): m1 mix without GAIN, m2 without the
check of the port data format, m3 mix at =0, m4 one of the N objects lost; m5 (sign of the Y decode) is extra.
Usage: python mut_m8a.py [--only <name>]   Output: mut_m8a.out.txt beside; last line ALL OK (every mutant caught and the
control passes) or FAIL. Lock and STOP checked before every step."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m8a'
WT = HERE + '/wt'
EXE = HERE + '/build/m_t125_stand.exe'
DRIVER = 'C:/kyty/KytyPS5/docs/track-m/m8a/run_stand_m8a.py'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
A2 = 'src/libs/libAudio2.cpp'
T = chr(9)
NL = chr(10)

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
    ('m5_y_sign', [(A2, T * 3 + '*right = -half_power;' + NL, T * 3 + '*right = half_power;' + NL)]),
]

out_lines = []


def say(s):
    print(s)
    out_lines.append(s)


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        say('LOCK or STOP')
        flush()
        sys.exit(3)


def flush():
    open(HERE + '/mut_m8a.out.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(out_lines) + NL)


def build(tag):
    guard()
    os.makedirs(HERE + '/mut', exist_ok=True)
    log = '%s/mut/build_%s.log' % (HERE, tag)
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c',
                              'C:' + chr(92) + 'kyty' + chr(92) + 'm657' + chr(92) + 'm8a' + chr(92) +
                              'build_m8a.cmd target m_t125_stand'], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def drive(tag):
    guard()
    base = '%s/mut/run_%s' % (HERE, tag)
    os.makedirs(base, exist_ok=True)
    p = subprocess.run(['python', DRIVER, EXE, base], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(base + '/driver.out.txt', 'w', encoding='utf-8', newline=NL).write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    fails = [ln for ln in text.splitlines() if ' FAIL' in ln]
    return last, fails


only = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == '--only' else None
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
        built = build(name)
        if not built:
            say('MUTANT %s BUILD_FAILED (not caught by the stand; see mut/build_%s.log)' % (name, name))
            all_ok = False
        else:
            last, fails = drive(name)
            caught = last == 'FAIL'
            say('MUTANT %s %s first=%s' % (name, 'CAUGHT' if caught else 'SURVIVED', fails[0] if fails else '-'))
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
