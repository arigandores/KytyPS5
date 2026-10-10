"""F31c (HPP-731): section 9 of docs/track-f/f31c.md - the series report from runs/b25m_*/read.json, the json of the tags, the run folders
and runs/lock.log (no verdict; ROADMAP s122 item 667 (e)(6)).  Port of F26c report_f26c.py.  Prints markdown to stdout (UTF-8)."""
import calendar
import glob
import json
import os
import re
import sys
import time

G = 'C:/kyty/f287/f31c'
TB = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'
RX_LOCK = re.compile(r'^lock (taken|released) (\S+) (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s*$')


def rd(p):
    try:
        return open(p, encoding='utf-8', errors='replace').read().strip()
    except OSError:
        return ''


locks = {}
cur = {}
for l in open(G + '/runs/lock.log', encoding='ascii'):
    m = RX_LOCK.match(l.strip())
    if not m:
        continue
    t = calendar.timegm(time.strptime(m.group(3), '%Y-%m-%dT%H:%M:%SZ'))
    if m.group(1) == 'taken':
        cur[m.group(2)] = (m.group(3), t)
    else:
        a = cur.pop(m.group(2))
        locks.setdefault(m.group(2), []).append((a[0], m.group(3), t - a[1]))

rows = []
for p in sorted(glob.glob(G + '/runs/b25m_*/read.json')):
    d = os.path.basename(os.path.dirname(p))
    if '.' in d:
        continue
    r = json.load(open(p, encoding='ascii'))
    j = json.load(open('%s/%s.json' % (G, r['tag']), encoding='utf-8'))
    run = '%s/runs/%s' % (G, r['tag'])
    r['installed_before'] = rd(run + '/installed_before.txt')[:8]
    r['installed_after'] = rd(run + '/installed_after.txt')[:8]
    r['mcmp'] = rd(run + '/manifest_cmp.txt').split('\n')[0]
    r['state'] = rd(run + '/state_cmp.txt').split('\n')[0]
    m = re.search(r'fps ([0-9.]+)', rd(run + '/tempo.txt').split('\n')[0])
    r['fps'] = m.group(1) if m else '-'
    lk = locks.get(r['tag'], [])
    r['lock'] = lk[-1] if lk else ('-', '-', 0)
    rows.append(r)

out = []
w = out.append
w('| Тег | Замок (UTC) | Замок, с | Бинарь json / до / после | Вход, с | Удержание, с | Кадров | Σ `dt`, с | max `dt`, мкс | Кадров ≥ 1 с | Детектор | Помеха | Класс | Слой | Темп, к/с | Кэши |')
w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in rows:
    w('| `%s` | %s–%s | %d | `%s` / `%s` / `%s` | %s | %s | %d | %.1f | %d | %d | %d/%d/%d | %s | %s | %s | %s | %s |' % (
        r['tag'], r['lock'][0][11:19], r['lock'][1][11:19], r['lock'][2], (r['binary'] or '-')[:8], r['installed_before'], r['installed_after'],
        r['entry_s'], r['hold_s'], r['frames'], r['sum_dt_s'], r['max_dt_us'], r.get('long_frames', 0), r['detector'][0], r['detector'][1],
        r['detector'][2], '; '.join(r['reasons']) or '0', r['cls'], r.get('layer') or '-', r['fps'],
        'EQUAL' if 'EQUAL' in r['mcmp'] and 'EQUAL' in r['state'] else 'DIFFER'))
c = {}
for r in rows:
    c[r['cls']] = c.get(r['cls'], 0) + 1
lay = {}
for r in rows:
    if r['cls'] == 'COUNTED':
        lay[r.get('layer')] = lay.get(r.get('layer'), 0) + 1
tot = sum(x[2] for v in locks.values() for x in v)
w('')
w('Итог строк: тегов %d; классы %s; слои засчитанных %s; N = 5 описи + %d = %d из 41.' % (
    len(rows), ', '.join('%s %d' % kv for kv in sorted(c.items())), ', '.join('%s %d' % kv for kv in sorted(lay.items())), c.get('COUNTED', 0),
    5 + c.get('COUNTED', 0)))
w('Замок: %d вызовов, сумма %d с (бюджет 23 400 с, п. 669); база %d с, возврат %d с.' % (
    sum(len(v) for v in locks.values()), tot, sum(x[2] for x in locks.get('base', [])), sum(x[2] for x in locks.get('return', []))))
bins = sorted(set((r['binary'] or '-')[:8] for r in rows) | set(r['installed_before'] for r in rows) | set(r['installed_after'] for r in rows))
w('Бинари: %s (FS11 `%s`).' % (', '.join('`%s`' % b for b in bins), TB[:8]))
w('Кадров ≥ 1 с после входа: %d; до входа: %d; max `dt` после входа — %d мкс (`%s`); маркеров смерти: %d; `--- Error ---`: %d; `Unhandled host exception`: %d; строк детектора: %d.' % (
    sum(r.get('long_frames', 0) for r in rows), sum(r.get('pre_entry_long_frames', 0) for r in rows), max(r['max_dt_us'] for r in rows),
    max(rows, key=lambda r: r['max_dt_us'])['tag'], sum(sum(r['death'].values()) for r in rows), sum(r['error_lines'] for r in rows),
    sum(r['host_exc'] for r in rows), sum(sum(r['detector']) for r in rows)))
w('Вход (`entry_s`): %.1f–%.1f с; Σ `dt`: %.1f–%.1f с; кадров: %d–%d; удержание `hold_s`: %.1f–%.1f с; темп %s–%s к/с.' % (
    min(r['entry_s'] for r in rows), max(r['entry_s'] for r in rows), min(r['sum_dt_s'] for r in rows), max(r['sum_dt_s'] for r in rows),
    min(r['frames'] for r in rows), max(r['frames'] for r in rows), min(r['hold_s'] for r in rows), max(r['hold_s'] for r in rows),
    min(r['fps'] for r in rows), max(r['fps'] for r in rows)))
w('')
w('Вызовы без попытки (эмулятор не стартовал; не теги, не помехи; папки `runs/<тег>.<причина>_<время>`):')
for d in sorted(glob.glob(G + '/runs/b25m_*.*')):
    b = os.path.basename(d)
    why = b.split('.', 1)[1]
    det = ''
    if why.startswith('busy'):
        det = 'шлюз procload до замка: ' + rd(d + '/procload.txt').split('\n')[-1][:110]
    elif why.startswith('nostart'):
        t = rd(d + '/run.txt')
        m = re.search(r'pre_run: REFUSED \(([^)]*)\)', t)
        det = 'под замком, require-idle: ' + (m.group(1) if m else 'no launching line')
    w('- `%s` — %s' % (b, det.replace('|', '/')))
sys.stdout.reconfigure(encoding='utf-8')
print('\n'.join(out))
