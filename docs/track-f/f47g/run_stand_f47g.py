"""run_stand_f47g.py - the stand of KYTY_DIAG_F47DT without the game (track F, F47g HPP-824, ROADMAP s122 item 740(v)(1)).

    python run_stand_f47g.py <f47dt_stand.exe> <work dir>

Starts the stand twice (KYTY_DIAG_F47DT=1 and =0, every other KYTY_* removed), each in its own empty directory, and checks:
  =1  P cmp=ne (positive control: one byte changed after the upload), N cmp=eq (negative control), A pooled copy -> last
      line hashed eq (a srcres line if the first line was pending), L lost, I import ne / I0 eq, O owner unmeasured,
      U no_note, D und with the current source = (i) and the earlier one != (i), R1/R2 register words through
      push / clear / write / pop, C0 file new and C1/C2 capped with one "F47dt: capped" line, F47dtStat files=10
      bytes=26214400 capped=1, 10 files whose XXH3-64 is the hash in the name and in the line, N+- on the P file
      (one byte flipped at 10 positions -> a different hash, 10 of 10);
  =0  "on=0", DONE, 0 lines with "F47dt" in the log, no _f47dt directory.
Rule 27: the lock and STOP are checked before each process. Prints ALL OK / FAILED (exit 0 / 1); 3 - lock or STOP."""
import hashlib
import os
import random
import re
import shutil
import subprocess
import sys

import xxhash

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def run(exe, work, value):
    d = os.path.join(work, 'on' if value == '1' else 'off')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_DIAG_F47DT'] = value
    guard()
    p = subprocess.run([exe, d], capture_output=True, env=env, timeout=300, cwd=os.path.dirname(exe))
    out = p.stdout.decode('utf-8', 'replace')
    open(os.path.join(d, 'stdout.txt'), 'w', encoding='utf-8', newline='\n').write(out)
    log = open(os.path.join(d, 'stand.log'), 'rb').read().decode('utf-8', 'replace')
    return d, p.returncode, out, log


def kv(line):
    return dict(t.split('=', 1) for t in line.split() if '=' in t)


def main():
    exe, work = sys.argv[1], sys.argv[2]
    os.makedirs(work, exist_ok=True)
    ok = True

    def check(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        print('%s %s %s' % ('OK  ' if cond else 'FAIL', name, detail))

    print('stand %s sha256 %s' % (exe, hashlib.sha256(open(exe, 'rb').read()).hexdigest()))
    d1, rc1, out1, log1 = run(exe, work, '1')
    check('=1 rc 0, on=1, DONE', rc1 == 0 and 'on=1' in out1 and 'DONE' in out1, 'rc=%d' % rc1)
    arms = {}
    for m in re.finditer(r'^ARM (\w+) addr=0x([0-9a-f]+) size=0x([0-9a-f]+)', out1, re.M):
        arms.setdefault(m.group(1), (int(m.group(2), 16), int(m.group(3), 16)))
    imgs = [kv(l[l.index('F47dt: '):]) for l in log1.split('\n') if 'F47dt: kind=img' in l]
    by_addr = {}
    for t in imgs:
        a = int(t['img'].split('+')[0], 16)
        by_addr.setdefault(a, []).append(t)
    srcres = [kv(l[l.index('F47dt: '):]) for l in log1.split('\n') if 'F47dt: kind=srcres' in l]
    regs = [kv(l[l.index('F47dt: '):]) for l in log1.split('\n') if 'F47dt: kind=reg' in l]
    capped = [l for l in log1.split('\n') if 'F47dt: capped' in l]
    stat = [kv(l[l.index('F47dtStat:'):]) for l in log1.split('\n') if 'F47dtStat:' in l]

    def one(arm, k=0):
        a = arms[arm][0]
        return by_addr[a][k]

    p = one('P')
    check('P positive control: one byte changed after the upload -> ne', p['cmp'] == 'ne' and p['sh'] != p['ih'],
          'ih=%s sh=%s' % (p['ih'], p['sh']))
    n = one('N')
    check('N negative control: unchanged -> eq', n['cmp'] == 'eq' and n['sh'] == n['ih'])
    a0, a1 = by_addr[arms['A0'][0]][0], by_addr[arms['A0'][0]][1]
    res_ok = a0['sst'] == 'hashed' or any(r['useq'] == a0['sseq'] and r['sst'] == 'hashed' for r in srcres)
    check('A pooled copy: last line hashed eq (srcres if the first was pending)',
          a1['sst'] == 'hashed' and a1['cmp'] == 'eq' and a1['sexact'] == '1' and res_ok,
          'first sst=%s' % a0['sst'])
    l = one('L')
    check('L ring generation moved -> lost, und', l['sst'] == 'lost' and l['cmp'] == 'und')
    i, i0 = one('I'), one('I0')
    check('I import, one byte changed -> ne; I0 -> eq',
          i['sk'] == 'import' and i['cmp'] == 'ne' and i0['cmp'] == 'eq' and i0['sexact'] == '0')
    o = one('O')
    check('O owner -> unmeasured und', o['sk'] == 'owner' and o['sst'] == 'unmeasured' and o['cmp'] == 'und')
    u = one('U')
    check('U no note -> und', u['swhy'] == 'no_note' and u['cmp'] == 'und')
    dd = one('D')
    check('D deferred completion: current source = (i), earlier != (i) -> und',
          dd['cmp'] == 'und' and dd['sh'] == dd['ih'] and dd['ph'] != dd['ih'] and dd['scomp'] == '1')
    check('R1 after clear + write', len(regs) == 2 and regs[0]['CB_BLEND0_CONTROL'] == '12345678'
          and regs[0]['CB_TARGET_MASK'] == 'R')
    check('R2 after pop', len(regs) == 2 and regs[1]['CB_BLEND0_CONTROL'] == '40010501'
          and regs[1]['CB_TARGET_MASK'] == '0000000f')
    c = [one('C0'), one('C1'), one('C2')]
    check('C file cap: C0 new, C1/C2 capped, one capped line',
          [x['ifile'] for x in c] == ['new', 'capped', 'capped'] and len(capped) == 1)
    check('F47dtStat files=10 bytes=26214400 capped=1', len(stat) == 1 and stat[0]['files'] == '10'
          and stat[0]['bytes'] == '26214400' and stat[0]['capped'] == '1', str(stat))
    fdir = os.path.join(d1, '_f47dt')
    names = sorted(os.listdir(fdir)) if os.path.isdir(fdir) else []
    good = len(names) == 10
    for nm in names:
        h = nm.split('_')[1].split('.')[0]
        good &= '%016x' % xxhash.xxh3_64_intdigest(open(os.path.join(fdir, nm), 'rb').read()) == h
        good &= any(t['ih'] == h for t in imgs)
    check('10 files, XXH3-64 of each = its name = an ih of a line', good, '%d files' % len(names))
    pf = os.path.join(fdir, '%016x_%s.bin' % (arms['P'][0], p['ih']))
    data = open(pf, 'rb').read() if os.path.exists(pf) else b''
    rnd = random.Random(740)
    hit = 0
    for k in range(10):
        b = bytearray(data)
        if not b:
            break
        b[rnd.randrange(len(b))] ^= 1 << rnd.randrange(8)
        hit += '%016x' % xxhash.xxh3_64_intdigest(bytes(b)) != p['ih']
    check('N+- one byte of a copy of the P file flipped at 10 positions -> a different hash', hit == 10, '%d of 10' % hit)

    d0, rc0, out0, log0 = run(exe, work, '0')
    check('=0 rc 0, on=0, DONE', rc0 == 0 and 'on=0' in out0 and 'DONE' in out0, 'rc=%d' % rc0)
    check('=0 no line with F47dt in the log', log0.count('F47dt') == 0, '%d' % log0.count('F47dt'))
    check('=0 no _f47dt directory', not os.path.exists(os.path.join(d0, '_f47dt')))
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
