"""Track M, M6a3 (HPP-856, ROADMAP s122 item 772(v), (g)): copy of m6a2/run_stand_m6a2.py with the M6a3 expectations:
pure 132 of 132 (new cases ao_obj_vq_nz, ao_obj_vq_zero - private commit; ao_obj_noaccess, ao_obj_guard, ao_obj_span; clr_r8_hi_div8
0x34121212; ao_obj_vq 0 on the storage and 0x1000 cases), M5W2Stat with ao_obj_vq last, audio 5 of 5 (push 5 - private commit).
Was: Track M, M6a2 (HPP-854, ROADMAP s122 item 770(b)-(e)): copy of m6a/run_stand_m6a.py with the M6a2 expectations.
Was: Track M, M6a (HPP-848, ROADMAP s122 item 767(i), (v), (z)): driver and reader of m_wave2_diag_stand.

Usage: run_stand_m6a.py <stand exe> <out dir>
One process per arm (audio at KYTY_DIAG_M5W2=0 and =1), stdout to <out>/<arm>[_k<k>].out.txt, LOGF to <out>/<arm>[_k<k>].log.
Members (each field has an input where it grows by 1 and one where it stays - item 767(i)):
  pure    103 of 103 checks match (M6a2; was 60 of 60) (15 fields of M5W2Stat + pushes, each with a >= 1 and a 0 case); the log holds one
          "M5W2Stat: when=stand" line with the same totals as the stand read, and "M5W2Clr: when=stand" lines for the formats
          R16_SFLOAT 76 (2 / 1), R16_UNORM 70 (1 / 1), RGBA16F 97 (2 / 1), RGBA16_UNORM 91 (1 / 1), RG32F 103 (1 / 1), RGBA8 37 (1 / 0).
  audio   =1: 4 of 4 pushes (M6a2 push 4: object port at an unreadable address - d_obj_unread 1, d_obj_nz 0, alive) with the wanted deltas (push 1 obj_push 1 obj_nz 1 bus_push 1 bus_nz 1; push 2 nz 0; push 3
          obj_nopcm 1) and "M5W2: mode=1"; =0: every delta 0 (the site is gated) and "M5W2: mode=0".
  printf  exactly one "GuestPrintf: negative precision prec=-1"; the output unchanged: A [] B [] C [ab].
  ampr    calls 1-2 rc 0, calls 3-25 rc EBUSY (0x80020010); "AmprRecordSpace: refused why=space ... write_offset=0x40 size=0x40"
          20 lines n=1..20; "AmprWriteAddress: refused why=ensure" 20 lines n=1..20.
  agc     27 of 27 calls ok=1 (the answer unchanged); "AgcReserveDW: cursor state" 20 lines n=1..20, the first five classes
          up0, down0, both0, down_lt_up, down0 (call 5 is the normal state: no line).
Last line ALL OK, or FAIL with every failed member. Lock and STOP checked before every process.
"""
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
EBUSY = -2147352560  # 0x80020010


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def run(exe, arm, knob, out_dir):
    guard()
    name = arm if knob is None else '%s_k%d' % (arm, knob)
    log = '%s/%s.log' % (out_dir, name)
    if os.path.exists(log):
        os.remove(log)
    env = dict(os.environ)
    env.pop('KYTY_DIAG_M5W2', None)
    if knob is not None:
        env['KYTY_DIAG_M5W2'] = str(knob)
    p = subprocess.run([exe, arm, log], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    text = p.stdout.decode('utf-8', 'replace')
    with open('%s/%s.out.txt' % (out_dir, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    logtext = open(log, 'rb').read().decode('utf-8', 'replace') if os.path.exists(log) else ''
    return p.returncode, text, logtext


def kv(line):
    return dict(re.findall(r'(\w+)=("[^"]*"|\S+)', line))


def end_line(arm, rc, text, fails):
    end = [l for l in text.splitlines() if l.startswith('MStand: m6 arm=%s ' % arm) and l.endswith(' END')]
    if rc != 0 or len(end) != 1:
        fails.append('%s: rc=%d END lines=%d' % (arm, rc, len(end)))
        return None
    return kv(end[0])


def main():
    exe, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    fails = []
    report = []

    # pure
    rc, text, log = run(exe, 'pure', 0, out_dir)
    e = end_line('pure', rc, text, fails)
    if e is not None:
        report.append('pure total=%s match=%s' % (e['total'], e['match']))
        if not (e['total'] == '132' and e['match'] == '132'):
            fails.append('pure: match %s of %s (want 132 of 132)' % (e['match'], e['total']))
        for l in text.splitlines():
            if ' match=0' in l and 'case=' in l:
                fails.append('pure: ' + l)
    stat = [l for l in log.splitlines() if l.startswith('M5W2Stat: when=stand ')]
    want_stat = dict(pushes='1', ao_obj_push='10', ao_obj_nz='3', ao_obj_nopcm='1', ao_bus_push='2', ao_bus_nz='1',
                     clr_dw='13', clr_dw_div='5', minlod_views='4', minlod_div='2', inv_calls='1', inv_part='3',
                     inv_gpu='4', inv_off='1', raw_rd='2', raw_rd_gpu='1',
                     minlod_div_x='1', clr_dw_div8='3', ao_obj_unread='4', inv_part_src='2', ao_obj_vq='2')
    if len(stat) != 1:
        fails.append('pure: M5W2Stat when=stand lines %d != 1' % len(stat))
    else:
        s = kv(stat[0])
        if not stat[0].rstrip().endswith(' inv_part_src=%s ao_obj_vq=%s' % (want_stat['inv_part_src'], want_stat['ao_obj_vq'])):
            fails.append('pure: M5W2Stat does not end with inv_part_src= ao_obj_vq=')
        for k, v in want_stat.items():
            if s.get(k) != v:
                fails.append('pure: M5W2Stat %s=%s want %s' % (k, s.get(k), v))
    clr = {kv(l)['fmt']: (kv(l)['clr_dw'], kv(l)['clr_dw_div'], kv(l).get('clr_dw_div8')) for l in log.splitlines()
           if l.startswith('M5W2Clr: when=stand ')}
    want_clr = {'76': ('2', '1', '0'), '70': ('1', '1', '0'), '97': ('2', '1', '0'), '91': ('1', '1', '0'),
                '103': ('1', '1', '0'), '37': ('1', '0', '0'), '9': ('3', '0', '2'), '16': ('2', '0', '1')}
    if clr != want_clr:
        fails.append('pure: M5W2Clr %s want %s' % (clr, want_clr))
    report.append('pure M5W2Clr %s' % sorted(clr.items()))

    # audio
    for knob in (1, 0):
        rc, text, log = run(exe, 'audio', knob, out_dir)
        e = end_line('audio', rc, text, fails)
        if e is not None:
            report.append('audio k%d total=%s match=%s on=%s' % (knob, e['total'], e['match'], e['on']))
            if not (e['total'] == '5' and e['match'] == '5' and e['on'] == str(knob) and e['knob'] == str(knob)):
                fails.append('audio k%d: %s' % (knob, e))
        if log.count('M5W2: mode=%d' % knob) != 1:
            fails.append('audio k%d: "M5W2: mode=%d" lines %d' % (knob, knob, log.count('M5W2: mode=%d' % knob)))

    # printf
    rc, text, log = run(exe, 'printf', None, out_dir)
    end_line('printf', rc, text, fails)
    n = log.count('GuestPrintf: negative precision prec=-1')
    report.append('printf negative precision lines %d' % n)
    if n != 1 or log.count('GuestPrintf: negative precision') != 1:
        fails.append('printf: negative precision lines %d (want 1)' % n)
    for want in ('MStandPrintf A []', 'MStandPrintf B []', 'MStandPrintf C [ab]'):
        if want not in log and want not in text:
            fails.append('printf: output "%s" missing' % want)

    # ampr
    rc, text, log = run(exe, 'ampr', None, out_dir)
    end_line('ampr', rc, text, fails)
    calls = {int(kv(l)['call']): int(kv(l)['rc']) for l in text.splitlines() if l.startswith('MStand: m6 arm=ampr call=')}
    want_calls = {i: (0 if i <= 2 else EBUSY) for i in range(1, 26)}
    if calls != want_calls:
        fails.append('ampr: rc per call %s' % calls)
    rs = [kv(l) for l in log.splitlines() if l.startswith('AmprRecordSpace: refused ')]
    wa = [kv(l) for l in log.splitlines() if l.startswith('AmprWriteAddress: refused ')]
    report.append('ampr AmprRecordSpace %d AmprWriteAddress %d' % (len(rs), len(wa)))
    if [r.get('n') for r in rs] != [str(i) for i in range(1, 21)] or \
            any(r.get('why') != 'space' or r.get('write_offset') != '0x40' or r.get('size') != '0x40' for r in rs):
        fails.append('ampr: AmprRecordSpace lines %s' % [(r.get('why'), r.get('n')) for r in rs][:3])
    if [r.get('n') for r in wa] != [str(i) for i in range(1, 21)] or any(r.get('why') != 'ensure' for r in wa):
        fails.append('ampr: AmprWriteAddress lines %s' % [(r.get('why'), r.get('n')) for r in wa][:3])

    # agc
    rc, text, log = run(exe, 'agc', None, out_dir)
    end_line('agc', rc, text, fails)
    oks = [kv(l)['ok'] for l in text.splitlines() if l.startswith('MStand: m6 arm=agc call=')]
    if oks != ['1'] * 27:
        fails.append('agc: ok per call %s' % oks)
    ag = [kv(l) for l in log.splitlines() if l.startswith('AgcReserveDW: cursor state ')]
    report.append('agc AgcReserveDW lines %d first %s' % (len(ag), [a.get('class') for a in ag[:5]]))
    if [a.get('n') for a in ag] != [str(i) for i in range(1, 21)]:
        fails.append('agc: AgcReserveDW n %s' % [a.get('n') for a in ag])
    if [a.get('class') for a in ag[:5]] != ['up0', 'down0', 'both0', 'down_lt_up', 'down0']:
        fails.append('agc: classes %s' % [a.get('class') for a in ag[:5]])

    for r in report:
        print(r)
    for f in fails:
        print('FAILED ' + f)
    print('ALL OK' if not fails else 'FAIL')
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
