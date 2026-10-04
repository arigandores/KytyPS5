# F18a (HPP-535): summary of sweep_old.jsonl (the 20 logs of sessions 45-105 with the F8 line) and sweep_new.jsonl
# (sessions 106+, tracks, play).  Prints the tables of docs/track-f/f18a.md and writes old_logs.tsv, new_logs.tsv,
# snd_texts.tsv.  Usage: python agg_f18a.py <dir with the jsonl files>
import json, os, re, statistics, sys

d = sys.argv[1]
RETRY_S = 3.0          # controller.cpp:102 RETRY_US
WRAP = 256             # SDL.c:119 Uint8 SDL_SubsystemRefCount


def load(name):
    p = os.path.join(d, name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.startswith('{')]


def first_ev(r, needle, before_line=None):
    for e in r.get('ev', []):
        if needle in e[4] and (before_line is None or e[0] < before_line):
            return e
    return None


def count_ev(r, needle, lo=None, hi=None):
    return sum(1 for e in r.get('ev', []) if needle in e[4] and (lo is None or e[0] >= lo) and (hi is None or e[0] < hi))


def scene_at(r, line):
    s = None
    for e in r.get('ev', []):
        if 'Level has started: ' in e[4] and e[0] < line:
            s = e[4].split('Level has started: ', 1)[1].strip()
    return s


def sec(ms):
    return '-' if ms is None else '%.1f' % (ms / 1000.0)


old = load('sweep_old.jsonl')
rows = []
print('== old: the logs of sessions 45-105 with the F8 line: %d' % len(old))
print('path | sha256 | lines | qfail (inv) | opens before vib | vib_s | fail_s | delta_s | predicted_s | per retry s | scene | '
      'tail_s | qfail/s | opens after | pad lines | ev_over')
deltas = []
for r in sorted(old, key=lambda x: x['path']):
    if r.get('missing'):
        print(r['path'], 'MISSING')
        continue
    qf = r['qfirst']
    vib = first_ev(r, 'AudioOut: vibration port')
    opens_before = count_ev(r, 'AudioOut: opened SDL device', hi=(vib[0] if vib else None))
    opens_before_fail = count_ev(r, 'AudioOut: opened SDL device', hi=qf[0])
    opens_after = count_ev(r, 'AudioOut: opened SDL device', lo=qf[0])
    pad = sum(1 for e in r['ev'] if 'Haptics: pad audio device' in e[4])
    delta = (qf[1] - vib[1]) / 1000.0 if vib and qf[1] is not None and vib[1] is not None else None
    pred = (WRAP - opens_before_fail) * RETRY_S
    per = delta / (WRAP - opens_before_fail) if delta is not None else None
    tail = (r['ts_last'] - qf[1]) / 1000.0 if r['ts_last'] is not None and qf[1] is not None else None
    rate = r['qfail'] / tail if tail else None
    if delta is not None:
        deltas.append((delta, per))
    row = [r['path'], (r.get('sha256_text') or r['sha256'])[:16], r['lines'], '%d (%d)' % (r['qfail'], r['qfail_inv']), opens_before, sec(vib[1]) if vib else '-',
           sec(qf[1]), '-' if delta is None else '%.2f' % delta, '%.0f' % pred, '-' if per is None else '%.4f' % per,
           scene_at(r, qf[0]) or '-', '-' if tail is None else '%.1f' % tail, '-' if rate is None else '%.0f' % rate, opens_after, pad,
           r['ev_over']]
    rows.append(row)
    print(' | '.join(str(x) for x in row))
with open(os.path.join(d, 'old_logs.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('path\tsha256_16\tlines\tqfail (inv)\topens_before_vib\tvib_s\tfail_s\tdelta_s\tpredicted_s\tper_retry_s\tscene\ttail_s\t'
            'qfail_per_s\topens_after\tpad_lines\tev_over\n')
    for row in rows:
        f.write('\t'.join(str(x) for x in row) + '\n')
print('last window / event line before the first qfail line (gap in s of process time), and sound lines in the 60 context lines:')
KW = ('AudioIn', 'Haptics', 'AudioOut', 'Window ', 'Event:', 'SDL', 'device', 'Controller', 'controller')
for r in sorted(old, key=lambda x: x['path']):
    if r.get('missing'):
        continue
    qf = r['qfirst']
    w = [e for e in r['ev'] if e[0] < qf[0] and (e[4].startswith('Window ') or e[4].startswith('Event:') or 'Recovering' in e[4])]
    gap = '-' if not w or w[-1][1] is None or qf[1] is None else '%.1f' % ((qf[1] - w[-1][1]) / 1000.0)
    hits = sum(1 for l in r['ctx'] if any(k in l for k in KW))
    print('  %s | %s | gap_s %s | context lines %d, with sound/window/device words %d' % (
        r['path'], w[-1][4][:40] if w else '-', gap, len(r['ctx']), hits))
if deltas:
    ds = [x[0] for x in deltas]
    ps = [x[1] for x in deltas]
    print('delta_s: n %d min %.2f median %.2f max %.2f; per retry s: min %.4f median %.4f max %.4f' %
          (len(ds), min(ds), statistics.median(ds), max(ds), min(ps), statistics.median(ps), max(ps)))
print('identities old: qfail == sum(qtexts)+over: %s; qfail_inv == qfail: %s' % (
    all(r['qfail'] == sum(r['qtexts'].values()) + r['qtexts_over'] for r in old if not r.get('missing')),
    all(r['qfail'] == r['qfail_inv'] for r in old if not r.get('missing'))))
print('qtexts old:', sorted({k for r in old if not r.get('missing') for k in r['qtexts']}))

mid = load('sweep_mid.jsonl')
print()
print('== mid: the other logs of sessions <= 105 (C:/kyty root files and C:/kyty/s<NN>, NN <= 105; the 20 above excluded): %d' % len(mid))
mafts = []
for r in mid:
    if r.get('missing'):
        continue
    vib = first_ev(r, 'AudioOut: vibration port')
    if vib and vib[1] is not None and r['ts_last'] is not None:
        mafts.append(((r['ts_last'] - vib[1]) / 1000.0, r['path'], r['qfail']))
mafts.sort()
print('qfail lines %d in %d logs; logs with the vibration port line %d; with it and timestamps %d' % (
    sum(r.get('qfail', 0) for r in mid), sum(1 for r in mid if r.get('qfail')),
    sum(1 for r in mid if first_ev(r, 'AudioOut: vibration port')), len(mafts)))
if mafts:
    print('life after the vibration port line, s: median %.1f, max %.1f (%s); >= 600 s: %d; >= 700 s: %d; >= 759 s: %d' % (
        statistics.median([a for a, _, _ in mafts]), mafts[-1][0], mafts[-1][1], sum(1 for a, _, _ in mafts if a >= 600),
        sum(1 for a, _, _ in mafts if a >= 700), sum(1 for a, _, _ in mafts if a >= 759)))
    for a, p, q in mafts[-6:]:
        print('  %.1f s  qfail %d  %s' % (a, q, p))
print('logs with "Haptics: pad audio device ... opened": %d; sound line texts with "failed": %s' % (
    sum(1 for r in mid if any('Haptics: pad audio device' in e[4] and 'opened' in e[4] for e in r.get('ev', []))),
    sorted({t for r in mid for t in r.get('snd', {}) if 'failed' in t})))
print('xz rc != 0: %d; missing: %d; ev_over logs: %d' % (sum(1 for r in mid if r.get('xz') and r.get('xz_rc') != 0),
                                                         sum(1 for r in mid if r.get('missing')), sum(1 for r in mid if r.get('ev_over'))))
print('separation: min delta of the 20 = %.2f s; max life without the line (mid + new) = see the two max values' % (min(x[0] for x in deltas) if deltas else -1))

new = load('sweep_new.jsonl')
print()
print('== new: logs of sessions 106+, tracks f287 / p283 / s288, play: %d' % len(new))
by = {}
snd = {}
longs = []
nrows = []
seen = {}
for r in new:
    if r.get('missing'):
        continue
    m = re.match(r'C:/kyty/([^/]+)/', r['path'])
    root = m.group(1) if m else '?'
    sha = r.get('sha256_text') or r['sha256']
    dup = sha in seen
    seen.setdefault(sha, r['path'])
    b = by.setdefault(root, {'logs': 0, 'distinct': 0, 'lines': 0, 'bytes': 0, 'qfail': 0, 'qlogs': 0, 'vib': 0, 'no_ts': 0, 'long': 0})
    b['logs'] += 1
    b['distinct'] += 0 if dup else 1
    b['lines'] += r['lines']
    b['bytes'] += r['size']
    b['qfail'] += r['qfail']
    b['qlogs'] += 1 if r['qfail'] else 0
    vib = first_ev(r, 'AudioOut: vibration port')
    b['vib'] += 1 if vib else 0
    after = None
    if vib and vib[1] is not None and r['ts_last'] is not None:
        after = (r['ts_last'] - vib[1]) / 1000.0
    elif r['ts_last'] is None:
        b['no_ts'] += 1
    pad = sum(1 for e in r['ev'] if 'Haptics: pad audio device' in e[4] and 'opened' in e[4])
    hoff = sum(1 for e in r['ev'] if 'Haptics: disabled' in e[4])
    opens = count_ev(r, 'AudioOut: opened SDL device')
    if after is not None and after >= (WRAP - opens) * RETRY_S:
        b['long'] += 1
        longs.append((r['path'], after, opens, r['qfail'], pad, hoff, dup))
    if not dup:
        for t, n in r['snd'].items():
            e = snd.setdefault(t, [0, 0, r['path']])
            e[0] += n
            e[1] += 1
    nrows.append((r['path'], sha[:16], r['size'], r['lines'], r['qfail'], opens, '-' if after is None else '%.1f' % after,
                  sec(r['ts_last']), pad, hoff, ';'.join(r['lvl'])[:120]))
tot = {'logs': 0, 'distinct': 0, 'lines': 0, 'bytes': 0, 'qfail': 0, 'qlogs': 0, 'vib': 0, 'no_ts': 0, 'long': 0}
print('root | logs | distinct sha256 | GiB stored | lines | qfail lines | logs with qfail | logs with vibration port | '
      'logs >= wrap time after the vibration port | logs without timestamps')


def rk(k):
    m = re.fullmatch(r's(\d+)', k)
    return (0, int(m.group(1))) if m else (1, k)


for k in sorted(by, key=rk):
    b = by[k]
    for x in tot:
        tot[x] += b[x]
    print('%s | %d | %d | %.2f | %d | %d | %d | %d | %d | %d' % (k, b['logs'], b['distinct'], b['bytes'] / 2.0 ** 30, b['lines'], b['qfail'],
                                                              b['qlogs'], b['vib'], b['long'], b['no_ts']))
print('TOTAL | %d | %d | %.2f | %d | %d | %d | %d | %d | %d' % (tot['logs'], tot['distinct'], tot['bytes'] / 2.0 ** 30, tot['lines'],
                                                                tot['qfail'], tot['qlogs'], tot['vib'], tot['long'], tot['no_ts']))
afts = sorted((float(x[6]), x[0]) for x in nrows if x[6] != '-')
if afts:
    print('life after the vibration port line, s: logs %d, median %.1f, max %.1f (%s); >= 400 s: %d; >= 600 s: %d; >= 759 s: %d' % (
        len(afts), statistics.median([a for a, _ in afts]), afts[-1][0], afts[-1][1], sum(1 for a, _ in afts if a >= 400),
        sum(1 for a, _ in afts if a >= 600), sum(1 for a, _ in afts if a >= 759)))
print('logs by the number of "opened SDL device" lines:', dict(sorted(
    {k: sum(1 for x in nrows if x[5] == k) for k in {x[5] for x in nrows}}.items())))
print('logs with "Haptics: pad audio device ... opened":', sum(1 for x in nrows if x[8]), '; with "Haptics: disabled":', sum(1 for x in nrows if x[9]))
print('logs with "AudioOut: SDL_OpenAudioDevice failed":')
for r in sorted(new, key=lambda x: x.get('path', '')):
    if r.get('missing'):
        continue
    f = [e for e in r['ev'] if 'SDL_OpenAudioDevice failed' in e[4]]
    if f:
        print('  %s | lines %d | first at %s s | opened lines %d | qfail %d | %s | %s' % (
            r['path'], len(f), sec(f[0][1]), count_ev(r, 'AudioOut: opened SDL device'), r['qfail'], ';'.join(r['lvl'][:2]), f[0][4]))
print('logs that ran past the wrap time (after_s >= (256 - opens) * 3 s after the vibration port line):')
for p, a, o, q, pad, hoff, dup in sorted(longs):
    print('  %s after_s %.1f opens %d qfail %d pad_opened %d haptics_off %d%s' % (p, a, o, q, pad, hoff, ' (dup)' if dup else ''))
with open(os.path.join(d, 'new_logs.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('path\tsha256_16\tsize\tlines\tqfail\topens\tafter_vib_s\tts_last_s\tpad_opened\thaptics_off\tlevels\n')
    for row in sorted(nrows):
        f.write('\t'.join(str(x) for x in row) + '\n')
with open(os.path.join(d, 'snd_texts.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('lines\tlogs\tfirst_log\ttext\n')
    for t, e in sorted(snd.items(), key=lambda x: -x[1][0]):
        f.write('%d\t%d\t%s\t%s\n' % (e[0], e[1], e[2], t))
print('distinct sound line texts (distinct logs): %d' % len(snd))
for t, e in sorted(snd.items(), key=lambda x: -x[1][0])[:40]:
    print('  %9d lines %4d logs  %s' % (e[0], e[1], t[:150]))
print('snd_over logs:', sum(1 for r in new if r.get('snd_over')), 'ev_over logs:', sum(1 for r in new if r.get('ev_over')),
      'xz rc != 0:', sum(1 for r in new + old if r.get('xz') and r.get('xz_rc') != 0), 'missing:', sum(1 for r in new + old if r.get('missing')))
