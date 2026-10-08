"""F26c (HPP-692): section 9 of docs/track-f/f26c.md - the series report from runs/b25_*/read.json, the json of the tags and the run
folders (no verdict; ROADMAP s122 item 630 (d)(4)).  Prints markdown to stdout.  ASCII-safe except the Russian headings."""
import glob
import json
import os
import re
import sys

G = 'C:/kyty/f287/f26c'
TB = 'abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'


def rd(p):
    try:
        return open(p, encoding='utf-8', errors='replace').read().strip()
    except OSError:
        return ''


rows = []
for p in sorted(glob.glob(G + '/runs/b25_*/read.json')):
    d = os.path.basename(os.path.dirname(p))
    if '.' in d:
        continue
    r = json.load(open(p, encoding='ascii'))
    j = json.load(open('%s/%s.json' % (G, r['tag']), encoding='utf-8'))
    run = '%s/runs/%s' % (G, r['tag'])
    r['launched'] = j.get('launched')
    r['installed_before'] = rd(run + '/installed_before.txt')[:8]
    r['installed_after'] = rd(run + '/installed_after.txt')[:8]
    r['mcmp'] = rd(run + '/manifest_cmp.txt').split('\n')[0]
    r['state'] = rd(run + '/state_cmp.txt').split('\n')[0]
    r['tempo'] = rd(run + '/tempo.txt').split('\n')[0]
    m = re.search(r'fps ([0-9.]+)', r['tempo'])
    r['fps'] = m.group(1) if m else '-'
    r['host_load'] = j.get('host_load', {})
    rows.append(r)

out = []
w = out.append
w('| Тег | Запуск (местн.) | Бинарь json / до / после | Вход, с | Удержание, с | Кадров | Σ `dt`, с | max `dt`, мкс | Детектор | Класс | Слой | Темп, к/с | Кэши до = после |')
w('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in rows:
    w('| `%s` | %s | `%s` / `%s` / `%s` | %s | %s | %d | %.1f | %d | %d/%d/%d | %s | %s | %s | %s |' % (
        r['tag'], (r['launched'] or '-')[11:], (r['binary'] or '-')[:8], r['installed_before'], r['installed_after'], r['entry_s'], r['hold_s'],
        r['frames'], r['sum_dt_s'], r['max_dt_us'], r['detector'][0], r['detector'][1], r['detector'][2], r['cls'], r.get('layer') or '-',
        r['fps'], 'EQUAL' if 'EQUAL' in r['mcmp'] and 'EQUAL' in r['state'] else 'DIFFER'))
c = {}
for r in rows:
    c[r['cls']] = c.get(r['cls'], 0) + 1
lay = {}
for r in rows:
    if r['cls'] == 'COUNTED':
        lay[r.get('layer')] = lay.get(r.get('layer'), 0) + 1
w('')
w('Итог строк: тегов %d; классы %s; слои засчитанных %s; N = 5 описи + %d = %d из 60.' % (
    len(rows), ', '.join('%s %d' % kv for kv in sorted(c.items())), ', '.join('%s %d' % kv for kv in sorted(lay.items())), c.get('COUNTED', 0),
    5 + c.get('COUNTED', 0)))
bins = sorted(set((r['binary'] or '-')[:8] for r in rows) | set(r['installed_before'] for r in rows) | set(r['installed_after'] for r in rows))
w('Бинари: %s (FS10 `%s`).' % (', '.join('`%s`' % b[:8] for b in bins), TB[:8]))
w('Кадров ≥ 1 с после входа: %d; до входа (строка): %d; max `dt` после входа — %d мкс (`%s`); маркеров смерти: %d; `--- Error ---`: %d; `Unhandled host exception`: %d.' % (
    sum(r['long_frames'] for r in rows), sum(r.get('pre_entry_long_frames', 0) for r in rows), max(r['max_dt_us'] for r in rows),
    max(rows, key=lambda r: r['max_dt_us'])['tag'], sum(sum(r['death'].values()) for r in rows), sum(r['error_lines'] for r in rows),
    sum(r['host_exc'] for r in rows)))
w('Вход (`entry_s`): %.1f–%.1f с; Σ `dt`: %.1f–%.1f с; удержание `hold_s`: %.1f–%.1f с; темп %s–%s к/с.' % (
    min(r['entry_s'] for r in rows), max(r['entry_s'] for r in rows), min(r['sum_dt_s'] for r in rows), max(r['sum_dt_s'] for r in rows),
    min(r['hold_s'] for r in rows), max(r['hold_s'] for r in rows), min(r['fps'] for r in rows), max(r['fps'] for r in rows)))
w('')
w('Вызовы без попытки (эмулятор не стартовал; не теги, не помехи; папки `runs/<тег>.<причина>_<время>`):')
for d in sorted(glob.glob(G + '/runs/b25_*.*')):
    b = os.path.basename(d)
    why = b.split('.', 1)[1]
    det = ''
    if why.startswith('busy'):
        det = rd(d + '/procload.txt').split('\n')[-1][:110]
    elif why.startswith('nostart'):
        t = rd(d + '/run.txt')
        m = re.search(r'pre_run: REFUSED \(([^)]*)\)', t)
        det = 'require-idle: ' + m.group(1) if m else 'no launching line'
    elif why.startswith('noimport'):
        det = 'enter_scene.py import (run_safety99.py missing, seal 2)'
    w('- `%s` — %s' % (b, det.replace('|', '/')))
print('\n'.join(out))
