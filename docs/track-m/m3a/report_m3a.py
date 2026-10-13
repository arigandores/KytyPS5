"""Track M link M3a (HPP-842): build report.md from the outputs of the series (read.json of every tag, g5/g6/g7 outputs, pairs, K0/K1
manifests, times.txt).  Rows only; no verdict on a theme (M3b).  Refuses under the lock (exit 3).  ASCII + the Russian text of the
report (UTF-8 file).  usage: python report_m3a.py"""
import glob
import hashlib
import json
import os
import re
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - exit 3')
    sys.exit(3)
G = 'C:/kyty/m657/m3a'
sys.path.insert(0, G)
import m3a_read as M  # noqa: E402

ORDER = ['m3_i'] + ['m3_%s_%s' % (L, k) for L in ('sg', 'hb', 'mg', 'ac', 'f1', 'f2') for k in ('w', 'v', 'f')] + \
    ['m3_sg_t2310', 'm3_g5_a1', 'm3_g5_b1', 'm3_g5_b2', 'm3_g5_a2', 'm3_g6']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def rd(t):
    p = os.path.join(G, 'runs', t, 'read.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def admitted(name):
    pick = None
    for t in (name, name + '_r1', name + '_r2'):
        r = rd(t)
        if r and r.get('admitted'):
            pick = t
    return pick


def text(p):
    return open(p, encoding='utf-8', errors='replace').read() if os.path.exists(p) else ''


def main():
    out = []
    o = out.append
    o('# M3a (трек M, `HPP-842`): серия M3 на MS1 — таблица тегов и пересчёт')
    o('')
    o('Печать `pred.md` sha256 `%s`. Ридер `m3a_read.py` sha256 `%s`. Вердикта по темам нет — чтение M3b (лид). Время — `times.txt` (UTC).' % (
        sha(G + '/pred.md'), sha(G + '/m3a_read.py')))
    o('')
    o('## 1. Теги (последний допущенный из `<тег>`, `_r1`, `_r2`)')
    o('')
    o('| тег | допущен | бинарь | уровень | форма | члены | форма FS15 | кадров ≥ 1 с | глитчей | видео | удержание, с | mean dt (+30 с, конец A), мкс | MWave1 | [Vulkan][E] / [W] |')
    o('|' + '---|' * 14)
    for name in ORDER:
        t = admitted(name) or name
        r = rd(t)
        if not r:
            o('| `%s` | не сделан | | | | | | | | | | | | |' % name)
            continue
        inf = r.get('info') or {}
        g5 = (r.get('g5') or {}).get('end_a') or {}
        yn = (lambda v: '-' if v is None else ('ALL YES' if v else 'NOT ALL YES'))
        o('| `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |' % (
            t, 'да' if r.get('admitted') else 'НЕТ: %s' % r.get('interference'), r.get('bin'), r.get('level'), r.get('kind'),
            yn(r.get('ok')), yn(r.get('form_ok')), inf.get('frames_ge1s'), inf.get('glitches'), inf.get('video_index'),
            inf.get('hold_s'), g5.get('mean'), ','.join(inf.get('mwave1') or []) or '-', inf.get('vke'), inf.get('vkw')))
    o('')
    o('Не попытки и помехи (папки `runs/<тег>.<причина>_<время>`): %s.' % (
        ', '.join('`%s`' % os.path.basename(p) for p in sorted(glob.glob(G + '/runs/m3_*.*_*'))) or 'нет'))
    o('')
    o('## 2. Члены, которые не YES')
    o('')
    any_no = False
    for name in ORDER:
        t = admitted(name)
        r = rd(t) if t else None
        if not r:
            continue
        for a, b in (r.get('members') or []) + (r.get('form') or []):
            if not b:
                any_no = True
                o('- `%s`: NO — %s' % (t, a))
    if not any_no:
        o('- нет (у всех допущенных тегов члены и форма FS15 — ALL YES)')
    o('')
    for title, f in (('G5', 'g5.out.txt'), ('G6', 'g6.out.txt'), ('G7 agg', 'g7_agg.out.txt'), ('G7 grep', 'g7_grep.out.txt'),
                     ('G7 wit', 'g7_wit.out.txt'), ('Пары листов', 'pairs.out.txt')):
        p = os.path.join(G, f)
        o('## %s (`%s`, sha256 `%s`)' % (title, f, sha(p)))
        o('')
        o('```')
        lines = [l for l in text(p).splitlines() if not l.startswith(("G1' ", 'W03 ', "G1'b ", 'STOPCHECK ', 'PAIR ', '  ', 'RUN ', 'EXCLUDED', 'R2 ',
                                                                       'DELTA', 'INTEGRITY', 'WINDOW', 'ENV ', 'G1 ', 'VERDICT_PAIR'))]
        o('\n'.join(lines[-40:]) if lines else '(нет вывода)')
        o('```')
        o('')
    o('## Кэши')
    o('')
    o('- K0 `k0/k0.tsv` sha256 `%s` (%s).' % (sha(G + '/k0/k0.tsv'), text(G + '/k0/k0.txt').strip()[:160]))
    o('- K1 `k1/k1.tsv` sha256 `%s` (%s).' % (sha(G + '/k1/k1.tsv'), text(G + '/k1/k1.txt').strip()[:160]))
    o('')
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
