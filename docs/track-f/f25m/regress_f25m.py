"""F25m (HPP-680): regression of f25m_read.py on the F25f logs (binary B, the cold and warm tags with frames in count and a reference
set) - the cold path of f25m_read (f25_read.read_log with the cached parsers, then INSTR_POLL) gives the F25f K / K_I / in count of each
tag except the frames it moves to INSTR_POLL (printed with their poll_us); S and the LongFrame / LogAsync rows are 0 there (binary B has
no such lines).  Reads C:/kyty/f287/f25f/log_<tag>.txt and runs/<tag>/read.json; writes nothing.  ASCII only; ends with REGRESS PASS.
usage: python regress_f25m.py [tag ...]"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f25m_read as M  # noqa: E402

R = M.R
F = M.F
SRC = 'C:/kyty/f287/f25f'
TAGS = ['f25_k01', 'f25_k02', 'f25_k03', 'f25_k04', 'f25_k05', 'f25_s15', 'f25_s01', 'f25_s14']
print('suite regress_f25m.py sha256 %s target f25m_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), M.sha_file(os.path.join(HERE, 'f25m_read.py'))))
ok = True
tags = sys.argv[1:] or TAGS
for t in tags:
    t0 = time.time()
    old = json.load(open(os.path.join(SRC, 'runs', t, 'read.json'), encoding='utf-8'))
    lv = old['level']
    log = os.path.join(SRC, 'log_%s.txt' % t)
    theta = R.read_theta(os.path.join(SRC, 'pred', 'f25f_seal.md'))
    m6 = R.read_m6(os.path.join(SRC, 'runs', t, 'm6.txt'))
    cal = R.read_cal(os.path.join(SRC, 'runs', t, 'cal.txt'))
    x = M.scan_extra(log, lv)
    M.with_cache(log)
    try:
        r = R.read_log(log, theta, lv, os.path.join(HERE, 'runs'), m6, cal)
    finally:
        M.without_cache()
    k0, ki0, c0 = r['K'], r['K_I'], r['in_count']
    M.instr_poll(r, x)
    o = old['log']
    same = (k0, ki0, c0) == (o['K'], o['K_I'], o['in_count'])
    moved = [(z['n'], z['dt_us'], z['poll_us']) for z in r['frames'] if z.get('instr_poll')]
    unk = [z['n'] for z in r['frames'] if z.get('poll_unknown') and z['in_count']]
    ok &= same
    ok &= x['lf'] == [] and x['stall'] == [] and x['sleep'] == [] and x['summary'] == []
    print('%s %s: F25f K %d K_I %d in count %d | before INSTR_POLL %d %d %d %s | after K %d K_I %d in count %d; INSTR_POLL %s; POLL_UNKNOWN in '
          'count %s; FlipHold lines %d (cap flip %s); new lines LongFrame %d stall %d sleep %d summary %d | %.0f s' % (
              t, lv[:5], o['K'], o['K_I'], o['in_count'], k0, ki0, c0, 'SAME' if same else 'DIFFERENT', r['K'], r['K_I'], r['in_count'], moved,
              unk[:6], len(x['fh']), r['fliphold_cap_flip'], len(x['lf']), len(x['stall']), len(x['sleep']), len(x['summary']), time.time() - t0))
    sys.stdout.flush()
print('REGRESS PASS' if ok else 'REGRESS FAIL')
sys.exit(0 if ok else 1)
