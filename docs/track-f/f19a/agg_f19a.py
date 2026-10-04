# F19a (HPP-543): aggregates sweep_new.jsonl.p* of sweep_f19a.py.  Usage: python agg_f19a.py <dir> <out.txt>
# Definitions (of this link, not of the register):
#   pad log        a log with at least one connect line  'Controller <id>: "<name>" type=...'
#   slow frame     'FrameTrace: n=' line with dt_us >= 1 000 000
#   phase of a slow frame, by the last 'Level has started: <non-empty name>' line before it:
#       boot  - no such line;  entry - less than 10 s of frame time (sum of dt_us) after it;  hold - 10 s or more
#   near a controller line: the frame interval [ts_end - dt, ts_end] widened by 5 s on both sides holds the timestamp
#       of a controller line (ts_end - the first log timestamp after the frame line; a controller line without a
#       timestamp before it - printed before the first timestamped line - counts as ts_first of the log)
import glob, json, re, sys

d, out = sys.argv[1], sys.argv[2]
recs = []
for p in sorted(glob.glob(d + '/sweep_new.jsonl.p*')):
    for l in open(p, encoding='utf-8'):
        if l.startswith('{'):
            recs.append(json.loads(l))
recs.sort(key=lambda r: r['path'])
n_list = len(recs)
seen, uniq = set(), []
for r in recs:            # the list walks C:/kyty/s288 twice (it is both 's<NNN>' >= 106 and a named root)
    if r['path'] not in seen:
        seen.add(r['path'])
        uniq.append(r)
n_path = len(uniq)
seen, recs, copies = {}, [], []
for r in uniq:            # byte-identical copies ('_a1' attempt copies): the first path in sort order is kept
    k = r.get('sha256')
    if k in seen:
        copies.append((r['path'], seen[k]))
    else:
        seen[k] = r['path']
        recs.append(r)
o = open(out, 'w', encoding='utf-8', newline='\n')


def p(*a):
    o.write(' '.join(str(x) for x in a) + '\n')


def root(path):
    return path.split('/')[2]


def tag(path):
    return path.replace('C:/kyty/', '').replace('.xz', '').replace('.txt', '').replace('log_', '')


CONN = re.compile(r'^Controller (\d+): "([^"]*)" type=(\d+) .*path=(<\w+>)')
miss = [r for r in recs if r.get('missing')]
recs = [r for r in recs if not r.get('missing')]
p('list entries', n_list, 'distinct paths', n_path, 'distinct contents (sha256)', len(recs) + len(miss), 'byte-identical copies dropped', len(copies))
p('logs', len(recs), 'missing', len(miss), 'GiB stored %.1f' % (sum(r['size'] for r in recs) / 2.0 ** 30),
  'lines', sum(r['lines'] for r in recs), 'frames', sum(r['ft_n'] for r in recs),
  'frame time h %.1f' % (sum(r['ft_us'] for r in recs) / 3.6e9))
p('caps: ctl_over', sum(r['ctl_over'] for r in recs), 'mt_over', sum(r['mt_over'] for r in recs), 'slow_over',
  sum(r['slow_over'] for r in recs), 'lvl_over', sum(r['lvl_over'] for r in recs), 'win_over', sum(r['win_over'] for r in recs))
p('xz rc != 0:', sum(1 for r in recs if r.get('xz_rc', 0) != 0))

p()
p('== A. controller lines')
texts = {}
for r in recs:
    for c in r['ctl']:
        t = re.sub(r'\d+', '#', c[4])
        texts.setdefault(t, [0, set()])
        texts[t][0] += 1
        texts[t][1].add(r['path'])
for t, (n, s) in sorted(texts.items(), key=lambda x: -x[1][0]):
    p('  %6d lines %4d logs | %s' % (n, len(s), t))
pad = []
for r in recs:
    conns = [(c, CONN.match(c[4])) for c in r['ctl']]
    conns = [(c, m) for c, m in conns if m]
    if conns:
        pad.append((r, conns))
p('pad logs (>= 1 connect line):', len(pad), 'of', len(recs))
for r, conns in pad:
    unk = [c for c in r['ctl'] if 'disconnect of unknown id' in c[4]]
    mot = [c for c in r['ctl'] if c[4].startswith('ControllerMotion')]
    hap = [c for c in r['ctl'] if 'Haptics: pad audio device' in c[4]]
    held = (r['ft_us'] - conns[0][0][3]) / 1e6
    p('  %-34s connects %d %s frame time after first connect %.1f s; unknown-id %d motion %d haptics-device %d; slow %d; MainTaskLate max %d us'
      % (tag(r['path']), len(conns), ['%s id %s type %s line %d ts %s' % (m.group(4), m.group(1), m.group(3), c[0], c[1]) for c, m in conns],
         held, len(unk), len(mot), len(hap), r['slow_n'], r['mt_late_max']))
p('logs with "disconnect of unknown id":', [(tag(r['path']), [(c[0], c[1], c[2]) for c in r['ctl'] if 'unknown id' in c[4]])
                                             for r in recs if any('unknown id' in c[4] for c in r['ctl'])])
p('logs with "Haptics: pad audio device":', [tag(r['path']) for r in recs if any('Haptics: pad audio device' in c[4] for c in r['ctl'])])

p()
p('== B. MainTaskLate')
late1 = [r for r in recs if r['mt_late_max'] >= 1000000]
p('logs with MainTaskLate >= 1 s:', len(late1))
for r in late1:
    r['_startup'] = all(c[2] == 0 for c in r['mt'] if c[4].startswith('MainTaskLate') and int(c[4].split('=')[1]) >= 1000000)
    p('  %-34s max %d us; before the first frame: %s; main-thread lines: %s' % (tag(r['path']), r['mt_late_max'], 'yes' if r['_startup'] else 'NO',
                                                    [(c[0], c[1], c[2], c[4]) for c in r['mt'] if 'MainTaskLate' not in c[4] or int(c[4].split('=')[1]) >= 1000000]))
p('logs with any MainTaskLate line:', sum(1 for r in recs if r['mt_late_max'] > 0), '; with MainStallTest:',
  sum(1 for r in recs if any(c[4].startswith('MainStallTest') for c in r['mt'])), '; with PrepareHold:',
  sum(1 for r in recs if any(c[4].startswith('PrepareHold') for c in r['mt'])), '; with TestMinimize:',
  sum(1 for r in recs if any(c[4].startswith('TestMinimize') for c in r['mt'])))

p()
p('== C. slow frames (dt_us >= 1 s)')
rows = []
for r in recs:
    ispad = any(CONN.match(c[4]) for c in r['ctl'])
    for s in r['slow']:
        line, tsb, ftn, ftus, n, dt, tsa = s
        lv = [l for l in r['lvl'] if l[4] and l[0] < line]
        if not lv:
            ph = 'boot'
        elif ftus - lv[-1][3] < 10000000:
            ph = 'entry'
        else:
            ph = 'hold'
        te = tsa if tsa is not None else tsb
        near = []
        if te is not None:
            for c in r['ctl']:
                tc = c[1] if c[1] is not None else r['ts_first']
                if tc is not None and te - dt / 1000.0 - 5000 <= tc <= te + 5000:
                    near.append(c[4][:40])
        lateh = [c for c in r['mt'] if c[4].startswith('MainTaskLate') and abs(c[0] - line) < 2000 and int(c[4].split('=')[1]) >= 1000000]
        rows.append((r, ispad, ph, near, lateh, s, lv[-1][4] if lv else ''))
p('slow frames:', len(rows), 'in logs:', len(set(x[0]['path'] for x in rows)))
for ph in ('boot', 'entry', 'hold'):
    sel = [x for x in rows if x[2] == ph]
    p('  phase %-5s frames %4d logs %4d ; in pad logs %d ; near a controller line %d ; with MainTaskLate >= 1 s within 2000 lines %d'
      % (ph, len(sel), len(set(x[0]['path'] for x in sel)), sum(1 for x in sel if x[1]), sum(1 for x in sel if x[3]),
         sum(1 for x in sel if x[4])))
p('slow frames near a controller line (any phase):')
for x in rows:
    if x[3]:
        p('  %-34s phase %s lvl %s n %d dt_us %d line %d ts_end %s near %s' % (tag(x[0]['path']), x[2], x[6], x[5][4], x[5][5], x[5][0], x[5][6], x[3]))
p('slow frames on hold:')
for x in rows:
    if x[2] == 'hold':
        p('  %-34s lvl %-28s n %6d dt_us %9d line %8d pad_log %d near_ctl %d main_late>=1s %d' % (
            tag(x[0]['path']), x[6], x[5][4], x[5][5], x[5][0], x[1], len(x[3]), len(x[4])))
p('slow frames in pad logs (any phase):')
for x in rows:
    if x[1]:
        p('  %-34s phase %s lvl %s n %d dt_us %d line %d near_ctl %s' % (tag(x[0]['path']), x[2], x[6], x[5][4], x[5][5], x[5][0], x[3]))

p()
p('== D. exposure')
p('pad logs: frame time after the first connect line, s: %.1f' % sum((r['ft_us'] - c[0][0][3]) / 1e6 for r, c in pad))
p('logs without a pad: %d, frame time h %.1f' % (len(recs) - len(pad), sum(r['ft_us'] for r in recs if not any(CONN.match(c[4]) for c in r['ctl'])) / 3.6e9))
by = {}
for r in recs:
    k = root(r['path'])
    by.setdefault(k, [0, 0, 0, 0])
    by[k][0] += 1
    by[k][1] += 1 if any(CONN.match(c[4]) for c in r['ctl']) else 0
    by[k][2] += r['slow_n']
    by[k][3] += 1 if r['mt_late_max'] >= 1000000 else 0
p('by root (logs / pad logs / slow frames / logs with MainTaskLate >= 1 s):')
p('  ' + ' '.join('%s:%d/%d/%d/%d' % (k, v[0], v[1], v[2], v[3]) for k, v in sorted(by.items())))
o.close()
print(open(out, encoding='utf-8').read())
