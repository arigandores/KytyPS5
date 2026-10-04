# F20a (HPP-551): self-check of the sweep records.
#   (1) identities of every swept record: per scene frames_h <= frames, sum_h <= sum_us, k100 >= k1s, max >= 100 000
#       exactly when k100 > 0; every slow row has dt_us >= 100 000; with slow_over == 0 the number of slow rows of a scene
#       with q == 0 that start inside / after the window equals k100_w / k100_h; ft_n >= frames of all scenes; lines > 0.
#   (2) every path of the list has exactly one record, no record is 'missing', xz_rc == 0.
#   (3) independent reading: for the sample logs and the six control logs the frames >= 100 ms after the first scene
#       frame of the first Sky Garden scene are re-read line by line (no blocks, no regex on the buffer) and compared
#       with the slow rows (n, dt_us) of the sweep - only the part of the log up to LIMIT_N frames is re-read.
#   (4) known frames of the register (F0, an independent sweep): ack129 n 954 183 252; lw3s131 n 1060 155 753;
#       rs135 n 7445 235 598; s3s130 (intro_next) n 2980 100 276; v142 n 382 180 521 and 10 176 frames after the first
#       scene frame.
# Prints 'ALL OK' and exits 0 when every member holds.  Usage: python selfcheck_f20a.py [dir]
import glob, json, lzma, re, sys

D = (sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f20a').rstrip('/') + '/'
TAB = chr(9)
rows = [l.rstrip(chr(10)).split(TAB) for l in open(D + 'list_f20a.tsv', encoding='utf-8') if l.strip()]
recs = {}
dup = 0
for fn in [D + 'sweep_all.jsonl']:
    for l in open(fn, encoding='utf-8'):
        if l.startswith('{'):
            r = json.loads(l)
            dup += r['path'] in recs
            recs[r['path']] = r
bad = []


def chk(name, cond, info=''):
    if not cond:
        bad.append('%s %s' % (name, info))


chk('(2) one record per path', dup == 0 and set(recs) == set(r[0] for r in rows), 'dup %d recs %d rows %d' % (dup, len(recs), len(rows)))
nsc = nsl = 0
for p, r in recs.items():
    chk('(2) missing', not r.get('missing'), p)
    chk('(2) xz_rc', r.get('xz_rc', 0) == 0, p)
    chk('(2) size', r['size'] == int([x for x in rows if x[0] == p][0][1]), p)
    chk('(1) lines', r['lines'] > 0 or r['size'] == 0, p)
    tot = 0
    for i, s in enumerate(r['scenes']):
        nsc += 1
        tot += s['frames'] + s['after_quit'] + (1 if s['first_n'] is not None else 0)
        chk('(1) hold part', s['frames_h'] <= s['frames'] and s['sum_h'] <= s['sum_us'], p)
        chk('(1) k1s <= k100', s['k1s_w'] <= s['k100_w'] and s['k1s_h'] <= s['k100_h'], p)
        chk('(1) max vs k100 w', (s['max_w'] >= 100000) == (s['k100_w'] > 0), p)
        chk('(1) max vs k100 h', (s['max_h'] >= 100000) == (s['k100_h'] > 0), p)
        chk('(1) window is 10 s', s['sum_us'] - s['sum_h'] >= 10000000 or s['frames_h'] == 0, p)
        if r['slow_over'] == 0 and r['scenes_over'] == 0:
            w = sum(1 for x in r['slow'] if x['scene'] == i and x['q'] == 0 and x['t_before_us'] < 10000000)
            h = sum(1 for x in r['slow'] if x['scene'] == i and x['q'] == 0 and x['t_before_us'] >= 10000000)
            chk('(1) slow rows = k100', (w, h) == (s['k100_w'], s['k100_h']), '%s scene %d rows %s k %s' % (p, i, (w, h), (s['k100_w'], s['k100_h'])))
    chk('(1) ft_n >= scene frames', r['ft_n'] >= tot or r['scenes_over'], p)
    chk('(1) slow count', len(r['slow']) + r['slow_over'] == r['slow_n'], p)
    for x in r['slow']:
        nsl += 1
        chk('(1) slow dt', x['dt_us'] >= 100000, p)
        chk('(1) interval parts', x['il'] >= x['io'] + x['fta'] + x['ir'] + x['gcn'] and x['io'] >= 0, '%s n %d' % (p, x['n']))

FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
DRAWS = re.compile(rb' draws=(\d+)')
LIMIT_N = 3000


def reread(path):
    f = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    in_sg = False
    first_n = None
    got = []
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            m = FT.match(line)
            if not m or not in_sg:
                continue
            n, dt = int(m.group(1)), int(m.group(2))
            if first_n is None:
                d = DRAWS.search(line)
                if d and int(d.group(1)) >= 100:
                    first_n = n
            else:
                if dt >= 100000:
                    got.append((n, dt))
                if n >= LIMIT_N:
                    break
        elif b'Level has started:' in line:
            name = line.split(b'Level has started:', 1)[1].strip()
            if name:
                if in_sg:
                    break
                in_sg = name == b'underwater_aerial_garden'
    f.close()
    return first_n, got


K = 'C:/kyty/'
LOGS = ['s128/log_shp128.txt.xz', 's142/log_v142.txt', 'f287/fsc/log_fs_b.txt', 's146/log_i146_v.txt', 'f287/fs3/fs3c/log_fs3_v.txt',
        'f287/fs4c/log_fs4_r1.txt', 'f287/fs4c/log_fs4_v.txt', 'f287/fs5/fs5c/log_fs5_r1.txt', 'f287/fs5/fs5c/log_fs5_v.txt',
        'f287/fs5/fs5e/log_fs5_i.txt', 's288/s12/log_s12_v.txt', 's288/s10/log_u_1.txt', 's129/log_ack129.txt.xz', 's130/log_ack130.txt.xz',
        's130/log_s12s130.txt.xz', 's131/log_lw4s131.txt.xz', 's131/log_lw5s131.txt.xz', 's131/log_lw6s131.txt.xz']
nrr = 0
for t in LOGS:
    r = recs[K + t]
    first_n, got = reread(K + t)
    si = [i for i, s in enumerate(r['scenes']) if s['level'] == 'underwater_aerial_garden'][0]
    mine = [(x['n'], x['dt_us']) for x in r['slow'] if x['scene'] == si and x['q'] == 0 and x['n'] <= LIMIT_N]
    chk('(3) first_n', first_n == r['scenes'][si]['first_n'], t)
    chk('(3) frames >= 100 ms up to n %d' % LIMIT_N, got == mine, '%s reread %s sweep %s' % (t, got[:6], mine[:6]))
    nrr += len(got)


def has(t, level, n, dt):
    r = recs[K + t]
    return any(x['n'] == n and x['dt_us'] == dt and r['scenes'][x['scene']]['level'] == level for x in r['slow'])


SGN, INN = 'underwater_aerial_garden', 'intro_next'
chk('(4) ack129 n 954', has('s129/log_ack129.txt.xz', SGN, 954, 183252))
chk('(4) lw3s131 n 1060', has('s131/log_lw3s131.txt.xz', SGN, 1060, 155753))
chk('(4) rs135 n 7445', has('s135/log_rs135.txt.xz', SGN, 7445, 235598))
chk('(4) s3s130 n 2980', has('s130/log_s3s130.txt.xz', INN, 2980, 100276))
chk('(4) v142 n 382', has('s142/log_v142.txt', SGN, 382, 180521))
chk('(4) v142 frames', recs[K + 's142/log_v142.txt']['scenes'][0]['frames'] == 10176)
for b in bad[:40]:
    print('FAIL', b)
print('records', len(recs), 'scenes', nsc, 'slow rows', nsl, 'slow_over logs', sum(1 for r in recs.values() if r['slow_over']),
      'scenes_over logs', sum(1 for r in recs.values() if r['scenes_over']), 'reread logs', len(LOGS), 'reread frames', nrr, 'failed', len(bad))
if not bad:
    print('ALL OK')
sys.exit(1 if bad else 0)
