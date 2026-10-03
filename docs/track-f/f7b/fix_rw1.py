"""fix_rw1.py - F7b rework (HPP-398, lead review 2026-10-03T01:48:59Z): sha list, git copies, report sec.7, FACTS section.
Writes LF.  Run only after the lock check in the same command."""
import hashlib
import shutil
import time

D = 'C:/kyty/f287/f7b'
G = 'C:/kyty/KytyPS5/docs/track-f/f7b'
REP = 'C:/kyty/KytyPS5/docs/track-f/f7b-b39.md'
FACTS = 'C:/kyty/f287/FACTS.md'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# 1. sha list: update changed, append new
NEW = ['rd_f7b.py', 'win_f7b.py', 'probe_f7b.py', 'probe_f7b.txt', 'patch_report_rw1.py', 'fix_rw1.py',
       'rd/probe_pts.json', 'rd/probe_pick.png']
rows = [l for l in open(D + '/sha_f7b.txt', encoding='utf-8').read().splitlines() if l.strip()]
names = [l.split(' *', 1)[1] for l in rows]
for n in NEW:
    line = '%s *%s' % (sha(D + '/' + n), n)
    if n in names:
        rows[names.index(n)] = line
    else:
        rows.append(line)
        names.append(n)
open(D + '/sha_f7b.txt', 'wb').write(('\n'.join(rows) + '\n').encode())

# 2. git copies
for n in ['rd_f7b.py', 'win_f7b.py', 'probe_f7b.py', 'probe_f7b.txt', 'patch_report_rw1.py', 'fix_rw1.py', 'sha_f7b.txt']:
    shutil.copyfile(D + '/' + n, G + '/' + n.split('/')[-1])
for n in ['rd/probe_pts.json', 'rd/probe_pick.png']:
    shutil.copyfile(D + '/' + n, G + '/' + n.split('/')[-1])

# 3. report sec.7
s = open(REP, 'rb').read().decode('utf-8').replace('\r\n', '\n')
a = "`rd_f7b_hist.txt`, `rd_f7b_debug.txt`, `rd_f7b_vsout.txt`, `uv_floor_on_12274.png`, `sha_f7b.txt` (полные sha256 22 файлов)."
b = ("`rd_f7b_hist.txt`, `rd_f7b_debug.txt`, `rd_f7b_vsout.txt`, `uv_floor_on_12274.png`, `sha_f7b.txt` (полные sha256 22 файлов).\n"
     "Доработка (ревью лида 01:48:59Z): `rd_f7b.py` — добавлена фаза `probe` (sha256 `%s…`), `win_f7b.py` — список окна дополнен\n"
     "`HPP-410`, `HPP-418`, `HPP-421`, `HPP-424`, `HPP-433` (`%s…`), `probe_f7b.py` (`%s…`, печатает `ALL OK`), `probe_f7b.txt`\n"
     "(`%s…`), `probe_pts.json` (`%s…`), `probe_pick.png`, `patch_report_rw1.py`, `fix_rw1.py`; `sha_f7b.txt` — %d строк." % (
         sha(D + '/rd_f7b.py')[:8], sha(D + '/win_f7b.py')[:8], sha(D + '/probe_f7b.py')[:8], sha(D + '/probe_f7b.txt')[:8],
         sha(D + '/rd/probe_pts.json')[:8], len(rows)))
assert s.count(a) == 1
s = s.replace(a, b)
open(REP, 'wb').write(s.encode('utf-8'))

# 4. FACTS section (append)
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
f = open(FACTS, 'rb').read().decode('utf-8').replace('\r\n', '\n')
f = f.rstrip('\n') + '\n\n' + (
    "## F7b (`HPP-398`, Emu Engineer) — доработка по ревью лида 2026-10-03T01:48:59Z: различающая проба подготовлена, реплей ждёт окна п. 277(г) (%s)\n\n"
    "- Ревью: тексель (0,0) атласа `12274` = плоский цвет пола ⇒ 6 точек F не различают (а) верные UV и (б) UV, схлопнутые в 0; связка VS 588 → PS 508 соседями не проверена.\n"
    "- `probe_f7b.py` (офлайн) `ALL OK`: калибровка проекции 12 из 12 (экран y = (−y/w·0,5+0,5)·H, глубина z/w = глубине истории); UV в точках F не (0,0), тексели — плоская область.\n"
    "- Лицевых треугольников 950 на тёмных текселях атласа (36,40,46) — 119, 944 пикселя, полоса x 2942…3105, y 1100…1112; у 960 — 1 (6 пикселей). Все 1 003 пикселя-кандидата перекрыты другими треугольниками 950 на плоских текселях ⇒ проба читает фрагмент перекрытого примитива в истории пикселей; точки Q950_1…Q950_8 и критерий чтения записаны в §2а отчёта до реплея.\n"
    "- §4: `%%376`/`%%380` = `OpSelect %%343 in_param_1 0`, `%%343` — бит дорожки в маске WQM от `Ballot(!gl_HelperInvocation)` (строки 700–769); для записанного пикселя [I] истинно. §5 поправлен: VS 588 → PS 508 соседями не проверена. §6: альтернатива (б) не различена.\n"
    "- Реплей `probe` не запущен: окно закрыто `HPP-418` (P33, `in_progress`, run `503ecb68…`); замок `gop31.sh` ~02:04–02:05Z — под замком ничего не писалось. Вывод звена не окончателен.\n"
    "- Отчёт `docs/track-f/f7b-b39.md` (§Вывод, §2а, §4–§7), файлы `docs/track-f/f7b/`. Снимок `enemy_final_600.rdc` не удалять.\n" % now)
open(FACTS, 'wb').write(f.encode('utf-8'))
print('ok rows', len(rows), now)
