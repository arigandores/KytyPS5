# F18a (HPP-535): assembles f18a.md from the parts of the run folder and the table of the 20 old logs built from
# sweep_old.jsonl; prints the numbers the text quotes, for a check against the text.
# Usage: python asm_f18a.py <parts dir> <data dir> <out.md>
import json, os, re, sys

parts, data, out = sys.argv[1], sys.argv[2], sys.argv[3]
old = [json.loads(l) for l in open(os.path.join(data, 'sweep_old.jsonl'), encoding='utf-8')]
new = [json.loads(l) for l in open(os.path.join(data, 'sweep_new.jsonl'), encoding='utf-8')]
DATE = {45: '09-12', 50: '09-13', 56: '09-13', 57: '09-13', 58: '09-13', 59: '09-14', 60: '09-14', 61: '09-15', 63: '09-15', 64: '09-15',
        99: '09-19', 100: '09-20', 101: '09-20', 105: '09-23'}


def fe(r, needle):
    for e in r['ev']:
        if needle in e[4]:
            return e


def num(x, nd=1):
    return ('%.*f' % (nd, x)).replace('.', ',')


def sp(n):
    return '{:,}'.format(n).replace(',', ' ')


def sess(p):
    m = re.search(r'/s(\d+)/', p) or re.search(r'log_s(\d+)_', p)
    return int(m.group(1))


rows = ['| Лог | Сессия (дата) | sha256 текста | Сцена в момент отказа | `T_vib`, с | `T_fail`, с | Δ, с | Строк Ф8 | До конца лога, с | Строк Ф8 в с |',
        '|---|---|---|---|---|---|---|---|---|---|']
lifes = []
for r in sorted(old, key=lambda x: (sess(x['path']), x['path'])):
    qf = r['qfirst']
    vib = fe(r, 'AudioOut: vibration port')
    scene = None
    for e in r['ev']:
        if 'Level has started: ' in e[4] and e[0] < qf[0]:
            scene = e[4].split('Level has started: ', 1)[1].strip()
    d = (qf[1] - vib[1]) / 1000.0
    tail = (r['ts_last'] - qf[1]) / 1000.0
    lifes.append((r['ts_last'] - vib[1]) / 1000.0)
    s = sess(r['path'])
    rows.append('| `%s` | %d (%s) | `%s…` | `%s` | %s | %s | %s | %s | %s | %s |' % (
        r['path'].replace('.xz', ''), s, DATE[s], r['sha256_text'][:16], scene, num(vib[1] / 1000.0), num(qf[1] / 1000.0), num(d, 2),
        sp(r['qfail']), num(tail), sp(int(round(r['qfail'] / tail)))))
text = ''
for name in ('head.md', 'part1.md', 'mid.md', 'part2.md', 'tail.md'):
    text += open(os.path.join(parts, name), encoding='utf-8').read().rstrip('\n') + '\n\n'
assert '<<TABLE20>>' in text
text = text.replace('<<TABLE20>>', '\n'.join(rows))
assert '<<' not in text, re.findall(r'<<[^>]*>>', text)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text.rstrip('\n') + '\n')
print('written', out, len(text), 'chars, lines', text.count('\n'))
print('old: life after vib min %.1f max %.1f; sum qfail %d' % (min(lifes), max(lifes), sum(r['qfail'] for r in old)))
nosnd = sum(1 for r in new if not r.get('snd'))
print('new: logs without any sound line', nosnd, 'of', len(new), '; with vib', sum(1 for r in new if fe(r, 'vibration port')),
      '; stored GiB %.1f' % (sum(r['size'] for r in new) / 2.0 ** 30))
print('old xz GiB %.2f' % (sum(r['size'] for r in old) / 2.0 ** 30))
