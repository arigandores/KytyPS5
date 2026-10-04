"""F23f (HPP-592): markdown tables of the report from sum_f23f.json, arms_f23f.json, map_f23f.json, sites_f23f.json,
layout_f23f.json (no new data). Output: tables_f23f.md."""
import json

D = 'C:/kyty/f287/f23f/'
NL = chr(10)
s = json.load(open(D + 'sum_f23f.json'))
arms = json.load(open(D + 'arms_f23f.json'))
mp = json.load(open(D + 'map_f23f.json'))
sites = json.load(open(D + 'sites_f23f.json'))
lay = json.load(open(D + 'layout_f23f.json'))
out = []
out.append('### Таблица событий (`sum_f23f.out.txt`)')
out.append('')
out.append('| Снимок | EID | Программа | (а) | (б) | (в) | (г) | `n_entry` | `N_null` def/def2 | `N_null` orig/def | опоры равны | `N_diff` | `sens` | `n_t` / `n_f` по местам | Годно |')
out.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in s['rows']:
    g = 'нет (%s)' % r['g_why'] if not r['g'] else '✓'
    ent = str(r['n_entry']) if r['n_entry'] >= 0 else '—'
    cnt = '%s / %s' % (r['n_t'], r['n_f']) if r['n_t'] else '—'
    if r['n_t'] and r['diag_selfcheck'] != 0:
        cnt += ' (самопроверка ≠ 0: %d)' % r['diag_selfcheck']
    out.append('| %s | %d | `%s` %s | %s | %s | %s | %s | %s | %d | %d | %s | %d | %d | %s | %s |' % (
        r['cap'], r['eid'], r['prog'], r['stage'].upper(), '✓' if r['a'] else 'нет', '✓' if r['b'] else 'нет', '✓' if r['v'] else 'нет', g,
        ent, r['N_null'], r['N_null2'], 'да' if r['refs_equal'] else 'нет', r['N_diff'], r['N_sens'], cnt,
        '**да**' if r['valid'] else 'нет'))
out.append('')
out.append('### Программы')
out.append('')
out.append('| Программа | Стадия | Мест формы A | Модуль снимка = S12 | Раскладка | Событий | Годных | Годных с `N_diff` > 0 | Чтение п. 498(д)(iii) |')
out.append('|---|---|---|---|---|---|---|---|---|')
RD = {'not found for form H': '**не найдено для формы H**', 'not found for both forms': 'не найдено для обеих форм',
      'not determined': 'не определено', 'N_diff > 0 on a valid event': '**N_diff > 0**'}
for h, p in sorted(s['programs'].items(), key=lambda x: (x[1]['stage'], x[0])):
    caps = [e for l in mp[h]['captures'].values() for e in l]
    out.append('| `%s` | %s | %d | %s | %s | %d | %d | %d | %s |' % (
        h, p['stage'].upper(), len(sites[h]['sites']), 'да' if caps[0]['equal_s12'] else 'нет (F10)',
        'равна' if lay[h].startswith('EQUAL') else lay[h], p['events'], p['valid'], p['valid_ndiff_pos'], RD[p['reading']]))
out.append('')
out.append('### sha256 SPIR-V (первые 16 знаков; полные — `arms_f23f.json`, `map_f23f.json`)')
out.append('')
out.append('| Программа | снимок | `def` (= S12) | `mask` (а) | `mem` (б) | `blend` (F23c) | `sens` |')
out.append('|---|---|---|---|---|---|---|')
for h, a in sorted(arms.items(), key=lambda x: (x[1]['stage'], x[0])):
    caps = [e for l in mp[h]['captures'].values() for e in l]
    f = a['files']
    out.append('| `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%s` |' % (h, caps[0]['sha'][:16], f['def']['sha'][:16], f['mask']['sha'][:16],
                                                               f['mem']['sha'][:16], f['blend']['sha'][:16], f['sens']['sha'][:16]))
open(D + 'tables_f23f.md', 'w', encoding='utf-8', newline=NL).write(NL.join(out) + NL)
print(len(out))
