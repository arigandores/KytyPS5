"""Track M, M8b (HPP-859, ROADMAP s122 items 778(g)(2)(ii), 781(v)): the reviewer's own run of the T125 mutants against the
stand, in the reviewer's worktree C:/kyty/m657/m8b/wt (= M8a worktree commit 6da84361). Copy of
docs/track-m/m8a/mut_m8a.py with the paths changed to m8b and the reviewer's extra mutants m6..m10 (m1..m5 are the
author's substitutions byte for byte). A mutant is CAUGHT when the driver run_stand_m8a.py prints FAIL. EXPECT_SURVIVE
mutants are a probe of what the stand does not cover: their SURVIVED is the expected answer and does not fail the run.
Usage: python mut_m8b.py [--only <name>]   Output: mut_m8b.out.txt beside; last line ALL OK or FAIL."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m8b'
WT = HERE + '/wt'
EXE = HERE + '/build/m_t125_stand.exe'
DRIVER = 'C:/kyty/KytyPS5/docs/track-m/m8a/run_stand_m8a.py'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
A2 = 'src/libs/libAudio2.cpp'
T = chr(9)
NL = chr(10)

MUTANTS = [
    # m1..m5: the author's (mut_m8a.py), unchanged.
    ('m1_no_gain', [(A2, T + 'left *= object.m125_gain;' + NL + T + 'right *= object.m125_gain;' + NL, '')], False),
    ('m2_no_format_check', [(A2, T + '       (state.audio_format == AudioInternal::Format::FloatMono ||' + NL + T +
                             '        state.audio_format == AudioInternal::Format::Signed16bitMono) &&' + NL, '')], False),
    ('m3_mix_at_0', [(A2, T + 'if (MT125On()) {' + NL + T + T + 'audioout2_m125_queue_context_audio(ctx, blocking);',
                      T + 'if (true) {' + NL + T + T + 'audioout2_m125_queue_context_audio(ctx, blocking);'),
                     (A2, T + 'if (MT125On() && params->max_object_ports > 0) {',
                      T + 'if (params->max_object_ports > 0) {')], False),
    ('m4_one_object_lost', [(A2, T * 5 + 'mixed = true;' + NL + T * 4 + '}' + NL,
                             T * 5 + 'mixed = true;' + NL + T * 5 + 'continue;' + NL + T * 4 + '}' + NL)], False),
    ('m5_y_sign', [(A2, T * 3 + '*right = -half_power;' + NL, T * 3 + '*right = half_power;' + NL)], False),
    # m6..m10: the reviewer's.
    ('m6_destroy_keeps_mix_device', [(A2, T + 'audioout2_close_audio_handle(object_audio_handle); // Track M, M8a (T125): '
                                      'nothing for 0' + NL, '')], False),
    ('m7_mix_across_contexts', [(A2, 'if (state.used && state.context == ctx && audioout2_m125_mixable(state)) {',
                                 'if (state.used && audioout2_m125_mixable(state)) {')], False),
    ('m8_mix_first_in_batch', [(A2, 'params.push_back(AudioInternal::OutputParam {mix_handle, mix.data()});',
                                'params.insert(params.begin(), AudioInternal::OutputParam {mix_handle, mix.data()});')],
     False),
    # m9: the finiteness check of GAIN dropped (NaN passes, -1 still rejected). A NaN mix is NaN in every sample.
    ('m9_gain_nan_accepted', [(A2, '[](float v) { return std::isfinite(v) && v >= 0.0f; });',
                               '[](float v) { return !(v < 0.0f); });')], False),
    # m10: the mix device does not make the context queueable (the pacing of an objects-only context, question 781(v)(2)).
    ('m10_queueable_ignores_mix', [(A2, T * 2 + 'if (mix_handle > 0 && audioout2_m125_mixable(state) && '
                                    'AudioInternal::AudioOutHasDevice(mix_handle)) {' + NL + T * 3 + 'return true;',
                                    T * 2 + 'if (false) {' + NL + T * 3 + 'return true;')], True),
]

out_lines = []


def say(s):
    print(s)
    out_lines.append(s)


def flush():
    open(HERE + '/mut_m8b.out.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(out_lines) + NL)


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        say('LOCK or STOP')
        flush()
        sys.exit(3)


def build(tag):
    guard()
    os.makedirs(HERE + '/mut', exist_ok=True)
    log = '%s/mut/build_%s.log' % (HERE, tag)
    rc = subprocess.call(['python', HERE + '/bld.py', log, 'target', 'm_t125_stand'])
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


def member_fails(tag):
    """First MEMBER FAIL lines of the stand outputs of a mutant run (the driver keeps stand_m<mode>.out.txt)."""
    r = []
    for mode in ('0', '1'):
        path = '%s/mut/run_%s/stand_m%s.out.txt' % (HERE, tag, mode)
        if os.path.exists(path):
            for ln in open(path, encoding='utf-8', errors='replace').read().splitlines():
                if ln.startswith('MEMBER ') and ' FAIL' in ln:
                    r.append('m%s:%s' % (mode, ln[7:100]))
    return r


only = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == '--only' else None
all_ok = True
for name, subs, expect_survive in MUTANTS:
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
            say('MUTANT %s %s%s first=%s members=%d %s' % (name, 'CAUGHT' if caught else 'SURVIVED',
                                                         ' (probe: survival expected)' if expect_survive else '',
                                                         fails[0] if fails else '-', len(mf), '; '.join(mf[:3])))
            all_ok &= (caught != expect_survive)
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
