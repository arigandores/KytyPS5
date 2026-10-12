"""run_stand_f47g2.py - the stand of KYTY_DIAG_F47DT without the game (track F, F47g2 HPP-828, ROADMAP s122 item 742(v);
port of run_stand_f47g.py of F47g HPP-824 with the arms of RC1-RC4 of the review F47h).

    python run_stand_f47g2.py <f47dt_stand.exe> <work dir>

Starts the stand twice (KYTY_DIAG_F47DT=1 and =0, every other KYTY_* removed), each in its own empty directory, and checks:
  =1  P cmp=ne (positive control: one byte changed after the upload), N cmp=eq (negative control), A pooled copy -> last
      line hashed eq (a srcres line if the first line was pending), L lost, I import ne / I0 eq, O owner unmeasured,
      U no_note, D und with the current source = (i), the earlier one != (i) and the record of image 9 (sid=9:1),
      R1/R2 register words through push / clear / write / pop;
      T (RC2) two images of one range: image 20 ne sid=20:1, image 21 eq sid=21:1, image 22 sk=other_image sid=21:1 und;
      S (RC4) one byte of the inline staging copy changed before the note: ne, sh = the stand's hash of the staging
      bytes; A2 (RC4) one byte of the pooled staging copy changed before the resolution: hashed, ne, sh = the stand's
      hash; G (RC3) ring: a noted GPU-copy range (whole / inside / overlapping) unmeasured:gpu_copy, a range not noted
      and the noted range after the generation moved -> the stand's hash, 5 lookups while a pooled copy may be in
      flight -> the stand's hash every time and inflight=1 at least once; Q (RC1) two draws with n 710 / 711 have the q
      of the flip line (path=0 rid=9001), the draw after the flip q + 1, a shown line n=1 rid=9001;
      C0 file new and C1/C2 capped with one "F47dt: capped" line, F47dtStat files=14 bytes=27459584 capped=1 flips=1
      ring_gpu_notes=1, 14 files whose XXH3-64 is the hash in the name and in a line, N+- on the P file (one byte
      flipped at 10 positions -> a different hash, 10 of 10);
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


def lines_of(log, marker):
    return [kv(l[l.index(marker):]) for l in log.split('\n') if marker in l]


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
    arm_kv = {}
    for m in re.finditer(r'^ARM (\w+) (.*)$', out1, re.M):
        t = kv(m.group(2))
        arm_kv.setdefault(m.group(1), []).append(t)
        if 'addr' in t:
            arms.setdefault(m.group(1), (int(t['addr'], 16), int(t['size'], 16)))
    imgs = lines_of(log1, 'F47dt: kind=img')
    by_addr = {}
    for t in imgs:
        a = int(t['img'].split('+')[0], 16)
        by_addr.setdefault(a, []).append(t)
    srcres = lines_of(log1, 'F47dt: kind=srcres')
    regs = lines_of(log1, 'F47dt: kind=reg')
    rings = lines_of(log1, 'F47dt: kind=ringstand')
    flips = lines_of(log1, 'F47dt: kind=flip')
    shown = lines_of(log1, 'F47dt: kind=shown')
    capped = [l for l in log1.split('\n') if 'F47dt: capped' in l]
    stat = lines_of(log1, 'F47dtStat:')

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
    check('D deferred completion: current source = (i), earlier != (i) -> und; record of image 9',
          dd['cmp'] == 'und' and dd['sh'] == dd['ih'] and dd['ph'] != dd['ih'] and dd['scomp'] == '1'
          and dd['sid'] == '9:1')
    check('R1 after clear + write', len(regs) == 2 and regs[0]['CB_BLEND0_CONTROL'] == '12345678'
          and regs[0]['CB_TARGET_MASK'] == 'R')
    check('R2 after pop', len(regs) == 2 and regs[1]['CB_BLEND0_CONTROL'] == '40010501'
          and regs[1]['CB_TARGET_MASK'] == '0000000f')
    # T (RC2)
    ta, tb, tc = one('TA', 0), one('TA', 1), one('TA', 2)
    check('T (RC2) image 20: its own record (old bytes) -> ne, sid=20:1',
          ta['cmp'] == 'ne' and ta['sid'] == '20:1' and ta['sh'] != ta['ih'], 'cmp=%s sid=%s' % (ta['cmp'], ta['sid']))
    check('T (RC2) image 21 of the same range -> eq, sid=21:1', tb['cmp'] == 'eq' and tb['sid'] == '21:1')
    check('T (RC2) image 22 never uploaded -> sk=other_image sid=21:1 und',
          tc['sk'] == 'other_image' and tc['sid'] == '21:1' and tc['cmp'] == 'und', 'sk=%s' % tc.get('sk'))
    # S, A2 (RC4)
    s = one('S')
    s_st = arm_kv['S'][0]['staging']
    check('S (RC4) inline: staging byte changed before the note -> ne, sh = hash of the staging bytes',
          s['cmp'] == 'ne' and s['sh'] == s_st and s['sh'] != s['ih'], 'sh=%s staging=%s' % (s['sh'], s_st))
    a2 = one('A2')
    a2_st = arm_kv['A2'][0]['staging']
    check('A2 (RC4) pooled: staging byte changed before the resolution -> hashed ne, sh = hash of the staging',
          a2['sst'] == 'hashed' and a2['cmp'] == 'ne' and a2['sh'] == a2_st and a2['sexact'] == '1',
          'sst=%s sh=%s staging=%s' % (a2['sst'], a2['sh'], a2_st))
    # G (RC3)
    g_names = [k for k in ('G1', 'G1b', 'G1c', 'G2', 'G3') for _ in arm_kv.get(k, [])] + ['G4'] * len(arm_kv.get('G4', []))
    check('G ring lines: one per lookup (10)', len(rings) == 10 and len(g_names) == 10, '%d lines' % len(rings))
    if len(rings) == 10:
        check('G1/G1b/G1c (RC3) noted GPU-copy range whole / inside / overlapping -> unmeasured:gpu_copy',
              all(rings[k]['gvh'] == 'unmeasured:gpu_copy' for k in range(3)), str([rings[k]['gvh'] for k in range(3)]))
        check('G2 range not noted -> the hash of the bytes', rings[3]['gvh'] == arm_kv['G2'][0]['expect'])
        check('G3 noted range after the generation moved -> the hash of the bytes',
              rings[4]['gvh'] == arm_kv['G3'][0]['expect'])
        g4 = rings[5:10]
        check('G4 (RC3) lookups while a pooled copy may be in flight -> the hash every time, inflight=1 at least once',
              all(r['gvh'] == arm_kv['G4'][0]['expect'] for r in g4) and any(r['inflight'] == '1' for r in g4),
              'inflight=%s' % ','.join(r['inflight'] for r in g4))
    # Q (RC1)
    q0, q1, q2 = one('Q0', 0), one('Q0', 1), one('Q0', 2)
    fl = flips[0] if len(flips) == 1 else {}
    check('Q (RC1) one flip line path=0 rid=9001', len(flips) == 1 and fl['path'] == '0' and fl['rid'] == '9001',
          str(flips))
    check('Q (RC1) the two draws before the flip: the q of the flip, n 710 / 711',
          q0['q'] == q1['q'] == fl.get('q') and q0['n'] == '710' and q1['n'] == '711',
          'q0=%s q1=%s flip=%s n0=%s n1=%s' % (q0['q'], q1['q'], fl.get('q'), q0['n'], q1['n']))
    check('Q (RC1) the draw after the flip: q + 1', fl and int(q2['q']) == int(fl['q']) + 1, 'q2=%s' % q2['q'])
    check('Q (RC1) shown line n=1 rid=9001', len(shown) == 1 and shown[0]['n'] == '1' and shown[0]['rid'] == '9001')
    # C and stat
    c = [one('C0'), one('C1'), one('C2')]
    check('C file cap: C0 new, C1/C2 capped, one capped line',
          [x['ifile'] for x in c] == ['new', 'capped', 'capped'] and len(capped) == 1)
    check('F47dtStat files=14 bytes=27459584 capped=1 flips=1 ring_gpu_notes=1', len(stat) == 1 and
          stat[0]['files'] == '14' and stat[0]['bytes'] == '27459584' and stat[0]['capped'] == '1'
          and stat[0]['flips'] == '1' and stat[0]['ring_gpu_notes'] == '1', str(stat))
    fdir = os.path.join(d1, '_f47dt')
    names = sorted(os.listdir(fdir)) if os.path.isdir(fdir) else []
    good = len(names) == 14
    for nm in names:
        h = nm.split('_')[1].split('.')[0]
        good &= '%016x' % xxhash.xxh3_64_intdigest(open(os.path.join(fdir, nm), 'rb').read()) == h
        good &= any(t['ih'] == h for t in imgs)
    check('14 files, XXH3-64 of each = its name = an ih of a line', good, '%d files' % len(names))
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
