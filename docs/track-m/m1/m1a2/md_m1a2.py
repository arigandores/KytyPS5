"""M1a2 (HPP-837): edit docs/track-m/m1/upstream.md of M1a (read from git eee39691, so the script is idempotent):
banner after the header, class cells of §10 corrected in place with the mark '(M1a2; было X)', rows T313/T314 after T240/T185
in §10, new section §14 generated from the data of m1a2/ (signatures.tsv, witness.tsv, upstream_parts.tsv,
upstream_merges.tsv, upstream.tsv). Read-only for git; exit 3 lock / 4 STOP. Usage: python md_m1a2.py"""
import collections, csv, os, re, subprocess, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP present - exit 4'); sys.exit(4)
HERE = os.path.dirname(os.path.abspath(__file__))
M1 = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(M1, '..', '..', '..'))
GIT = 'C:/Program Files/Git/cmd/git.exe' if os.path.exists('C:/Program Files/Git/cmd/git.exe') else 'git'


def git(*a):
    return subprocess.run([GIT, '-C', REPO] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')


def tsv(path):
    return list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


md = git('show', 'eee39691:docs/track-m/m1/upstream.md')
up = tsv(os.path.join(M1, 'upstream.tsv'))
old_up = list(csv.DictReader(git('show', 'eee39691:docs/track-m/m1/upstream.tsv').splitlines(), delimiter='\t',
                             quoting=csv.QUOTE_NONE))
sig = tsv(os.path.join(HERE, 'signatures.tsv'))
wit = tsv(os.path.join(HERE, 'witness.tsv'))
parts = tsv(os.path.join(M1, 'upstream_parts.tsv'))
merge = tsv(os.path.join(M1, 'upstream_merges.tsv'))[0]
det = tsv(os.path.join(M1, 'upstream_detail.tsv'))
rc1 = {r['тема']: r['вид'] for r in tsv(os.path.join(M1, 'm1b', 'rc1_themes.tsv'))}
new_cls = {r['тема']: r['класс'] for r in up}
old_cls = {r['тема']: r['класс'] for r in old_up}
line_of = {}
for d in det:
    line_of.setdefault(d['тема'], d['строка_M1a2'])

# ---- banner
anchor = '\n## 0. Итог\n'
banner = ('\n> **M1a2 (`HPP-837`, п. 756(б)) поправила эту опись.** Действующие классы — `upstream.tsv` и §14 (А-резерв у 74 тем RC1, '
          'T256 → А, T021 → В, деление T240/T313 и T185/T314, слияние `8cecaf4e` — `upstream_merges.tsv`). Таблица §10 поправлена на '
          'месте с пометкой «(M1a2; было X)»; §0–§9 — текст издания M1a без правки (классы там — до M1a2).\n')
assert anchor in md
md = md.replace(anchor, banner + anchor, 1)
# ---- §10 class cells and part rows
out, in10 = [], False
for line in md.split('\n'):
    if line.startswith('## 10. '):
        in10 = True
    elif line.startswith('## 11. '):
        in10 = False
    m = re.match(r'^\| (T\d{3}) \| ([^|]*)\| ([^|]+) \|', line)
    if in10 and m:
        t = m.group(1)
        cells = line.split(' | ')
        if new_cls[t] != old_cls[t]:
            assert cells[2] == old_cls[t], (t, cells[2])
            cells[2] = '%s (M1a2; было %s)' % (new_cls[t], old_cls[t])
            line = ' | '.join(cells)
        out.append(line)
        if t in ('T240', 'T185'):
            p = [x for x in parts if x['родитель'] == t and x['тема'] != t][0]
            out.append('| %s | `%s` | %s (M1a2; часть %s) | %s | `%s` | %s | `%s` | %s | %s |' % (
                p['тема'], {'T313': 'img-clear16-guard', 'T314': 'prs-lds-clamp'}[p['тема']], p['класс'], t,
                'I', p['sha'][:8], p['суть'][:90] + ('…' if len(p['суть']) > 90 else ''), p['основание'],
                'нет' if p['тема'] == 'T313' else 'нет', '—'))
        continue
    out.append(line)
md = '\n'.join(out)

# ---- §14
cc_new = collections.Counter(r['класс'] for r in up)
cc_old = collections.Counter(r['класс'] for r in old_up)
th_new = collections.Counter(new_cls.values())
th_old = collections.Counter(old_cls.values())
order = ['А', 'А-резерв', 'Б', 'В', 'В′', 'Г', 'Д']
S = []
S.append('## 14. M1a2 (`HPP-837`): правки по исходам отзыва M1b (п. 756(б)(1)–(6))')
S.append('')
S.append('Исполнитель — Probe Designer, 2026-10-12 (UTC). Вход — опись M1a (KytyPS5 `eee39691`), отзыв M1b `review.md` (`9430bb10`), '
         'решения — `ROADMAP.md` п. 756 (`f7208cda`), правило класса — п. 752(в). Игра не запускалась, замок не брался, сборок нет, код '
         '`main` не менялся. Свой код и выводы — `m1a2/` (`apply_m1a2.py` пишет `upstream.tsv`, `upstream_detail.tsv`, '
         '`upstream_parts.tsv`, `upstream_merges.tsv` из издания `eee39691`; `md_m1a2.py` — этот раздел; `check_m1a2.py` — члены '
         '(1)–(6)). Пометки [c]/[I]/[U] — как в отзыве.')
S.append('')
S.append('### 14.0 Итог классов (счёт скриптом)')
S.append('')
S.append('| класс | коммитов M1a | коммитов M1a2 | тем M1a | тем M1a2 (+ части) |')
S.append('|---|---|---|---|---|')
for c in order:
    extra = {'А': ' + T313', 'А-резерв': ' + T314'}.get(c, '')
    S.append('| %s | %d | %d | %d | %d%s |' % (c, cc_old[c], cc_new[c], th_old[c], th_new[c], extra))
S.append('| всего | %d | %d | %d | %d + 2 |' % (sum(cc_old.values()), sum(cc_new.values()), sum(th_old.values()),
                                                 sum(th_new.values())))
S.append('')
S.append('Расчёт по коммитам: Г = 375 − 110 (RC1) = **265**, поправки (2) Г не трогают; А = 40 + 1 (T256) = 41; А-резерв = 110 − 1 = 109; '
         'Б = 10 − 1 (T021) = 9; В = 58 + 1 = 59; Д = 81. Коммиты T240 (`57c97ebd`) и T185 (`e6cb880a`) несут по две темы: класс строки '
         '`upstream.tsv` — Б (декодирование / пад), вторая тема — колонка `доп_тема` (`T313:А`, `T314:А-резерв`) и строка '
         '`upstream_parts.tsv`; по долям коммит идёт в оба класса.')
S.append('')
S.append('### 14.1 RC1: А-резерв и сигнатуры отказа')
S.append('')
S.append('75 тем `m1b/rc1_themes.tsv`: 74 — **А-резерв** (перенос только при сигнатуре у нас или офлайн-свидетельстве по всей игре), '
         '**T256 — А** (волна 1, п. 756(в)(1)). Строка `строка_M1a2` каждой темы это называет.')
S.append('')
nprint = len({r['тема'] for r in sig if r['сигнатура'] != '-'})
streams = collections.Counter(r['поток'] for r in sig)
S.append('**Сигнатуры (`m1a2/signatures.tsv`, `mk_sig_m1a2.py` — `ALL OK`).** %d мест на 48 тем (30 FATAL, 18 RT): у %d тем печатаемый '
         'текст, у T202 и T305 печати нет (путь молча берёт устаревший V# / отбрасывает предикат — место названо). Места найдены '
         'тремя помощниками звена только чтением и перепроверены скриптом: строка N и N+1 на `b3dc9c67` — %d из %d; сигнатура — '
         'подстрока литерала у места. Поток: лог %d, stderr %d, stdout %d, нет %d. Сигнатура T001 сужена до '
         '`Exception: code=0xc00000fd` (переполнение стека): общий вид «Exception: code=» есть в чистом прогоне (16 строк C++-исключений '
         '`0xe06d7363` в `stdout_fs15_v`) [c].' % (len(sig), nprint, len(sig), len(sig), streams['лог'], streams['stderr'],
                                                   streams['stdout'], streams['нет']))
S.append('')
nokey = sorted({r['тема'] for r in sig} - {r['тема'] for r in sig if (r['поток'] == 'лог' and r['ключ_свипа'] == 'да') or
                                           (r['поток'] == 'stderr' and r['в_логе'] != '-' and r['ключ_свипа'] == 'да')})
S.append('**Находка [c]: свип трека F этих сигнатур не видит.** У %d из 48 тем строка журнала с сигнатурой не совпадает с `KEY` сканера '
         '`docs/track-f/f0/sweep_f0.py` (его без изменений импортирует `sweep_f48a.py`): «Not implemented (…)» (в `KEY` только '
         '«not implemented»), «… is not a valid runtime value», «sampling a writable depth…» и т. п. — свип видит только общий '
         'заголовок «--- Error ---» / «--- Fatal Error ---»; строки stderr/stdout (`_run_stdout.txt`) свип не читает вовсе. Темы: %s. '
         'Поэтому поиск — свой: **`m1a2/grep_sig_m1a2.py`** (все сигнатуры и строки-спутники в логе; строка «CsPretranslate: '
         'skipped» считается отдельно). Положительный контроль `selftest` — 46 из 46 тем с печатью найдены по строке формы нашей '
         'печати, отрицательные строки — 0; отрицательный контроль на чистом V FS15 (`log_fs15_v.txt` + `stdout_fs15_v.txt`) — 0 '
         'фатальных совпадений, 33 строки предтрансляции «… is not a valid runtime value» (`CsPretranslate: skipped`) у 15 тем (14 RT и T072) — '
         'отказ CS-программ при предтрансляции, не фатал прогона [c]; к какой теме относится каждая — по `hash`/`pc` строки [U]. '
         'Правило переоткрытия п. 749 читает эти сигнатуры этим поиском; `sweep_f48a.py` не меняется (вне звена).' % (
             len(nokey), ', '.join(nokey)))
S.append('')
S.append('| тема | вид | мест | поток | первая сигнатура | место (`b3dc9c67`) | ключ свипа |')
S.append('|---|---|---|---|---|---|---|')
by = collections.defaultdict(list)
for r in sig:
    by[r['тема']].append(r)
for t in sorted(by):
    rs = by[t]
    first = next((r for r in rs if r['сигнатура'] != '-'), rs[0])
    S.append('| %s | %s | %d | %s | `%s` | `%s` | %s |' % (
        t, rc1[t], len(rs), '/'.join(sorted({r['поток'] for r in rs})), first['сигнатура'].replace('|', '\\|'),
        first['место'].replace('b3dc9c67:', ''), '/'.join(sorted({r['ключ_свипа'] for r in rs}))))
S.append('')
pic = sorted(t for t, k in rc1.items() if k in ('PIC', 'HLE'))
S.append('Темы PIC/HLE без печатающего отказа (%d): %s — А-резерв, кроме T256 (А); переоткрытие — видимый дефект на листе, строка '
         'реестра или офлайн-свидетельство по всей игре.' % (len(pic), ', '.join(pic)))
S.append('')
S.append('**Офлайн по всей игре (T226 и T314) [c].** `m1a2/lds_m1a2.py`: в 6 087 AMDGPU ELF `eboot.bin` (5 698 уникальных программ) '
         'раздел `.shader_header` — заголовок AGC `Shader` с парами SH-регистров (указатель `sh_registers` — от своего поля); у 190 '
         'программ типа CS есть `COMPUTE_PGM_RSRC2` (0x213), LDS = биты [23:15] × 512 Б. Гистограмма: 0 Б — 107, ≤ 9 728 Б — 59, '
         '49 152 Б — 24; наибольший 49 152 Б = `maxComputeSharedMemorySize` устройства пользователя (RTX 5080 Laptop, драйвер 616.56, '
         '`vulkaninfoSDK`) — сверх предела 0 из 190. Свидетельство обо всей игре, а не о пройденных сценах; что игра передаёт значение '
         'заголовка без правки — [I]. Триггер переноса T226/T314 — устройство с пределом < 49 152 Б (тогда 24 программы сверх) или '
         'новая программа.')
S.append('')
S.append('### 14.2 RC2: T021 → В, деление T240 и T185')
S.append('')
S.append('| тема | часть коммита | класс | ханки | основание |')
S.append('|---|---|---|---|---|')
for p in parts:
    S.append('| %s | %s `%s` | %s | %s | `%s` |' % (p['тема'], 'основная' if p['тема'] == p['родитель'] else 'часть ' + p['родитель'],
                                                 p['sha'][:8], p['класс'], p['ханки'], p['основание'].replace('b3dc9c67:', '')))
S.append('')
S.append('T021 (`f38d738e`) — **В**: наш `minLod` не прибавляет `base_level` (RC2(а) отзыва); проверка — §14.6. T313 — защита '
         'заливки DWORD R16 с неравными половинами: у нас путь `ClearImageFromBuffer` (`textureCache.cpp:2971`) берёт младшую '
         'половину слова — волна 2 вместе с частью заливки T179 (п. 756(в)(3)). T314 — предел LDS вычислений (`GetComputeProgram`, '
         '`pipelineCache.cpp:5424`; у нас `lds_size_dwords = lds_size × 128` без зажима, `shader.cpp:850`) — А-резерв со свидетельством '
         '§14.1.')
S.append('')
S.append('### 14.3 RC3: слияние `8cecaf4e` и переименования')
S.append('')
S.append('`upstream_merges.tsv`: `%s` → тема **%s**, класс **%s** (как у T053), файлы — комбинированный дифф (%d): %s. Основание '
         '`%s` — «%s». %s' % (merge['sha'], merge['тема'], merge['класс'], len(merge['файлы'].split(';')),
                              ', '.join('`%s`' % f for f in merge['файлы'].split(';')), merge['основание'].replace('b3dc9c67:', ''),
                              merge['якорь'], merge['строка_M1a2']))
S.append('')
S.append('Колонка `файлы` `upstream.tsv` — обе стороны переименований `git diff-tree -r -M`: дописаны исходные пути у `b11aea80` '
         '(`src/loader/redZonePatcher.cpp`) и `5940e623` (`src/graphics/host_gpu/shaders/gpu_tiler_swap_bgra16.comp`); расхождений с '
         '`-M` — 0 из 564 (`check_m1a2.py`). `m1b/cov_m1b.py` поправлен в одном месте (ветка слияния): слияние с содержимым '
         'считается покрытым только строкой `upstream_merges.tsv` с его sha, темой и классом этой темы и ровно его файлами '
         'комбинированного диффа; остальные проверки отзыва не тронуты. `cov_m1b.py` и `check_m1a.py` (новая колонка `доп_тема`, '
         'класс А-резерв) печатают `ALL OK`.')
S.append('')
S.append('### 14.4 RC4: свидетели строк журнала')
S.append('')
nw = len({r['тема'] for r in wit})
S.append('`m1a2/wit_m1a2.py` (`ALL OK`): литералы удалённых строк вызовов печати/журнала каждого коммита (и слияния) против %d '
         'наших скриптов `docs/` на `b3dc9c67` (`*.py`, `*.sh`, `*.ps1`, `*.cmd`); судьба ключа — есть ли он текстом в `src/` '
         'upstream `dad900c6`. %d строк, %d тем (`m1a2/witness.tsv`; ключи вида «size = 0x» — общие, отсеивает читатель). Колонка '
         '`свидетели` `upstream_detail.tsv` — по теме. Правило M2 (п. 756(б)(4)): перенос темы со свидетелем сохраняет строку '
         'текстом.' % (4160, len(wit), nw))
S.append('')
S.append('| тема | ключ | в upstream | наши читатели |')
S.append('|---|---|---|---|')
for r in wit:
    if len(r['ключ']) < 14 and r['тема'] not in ('T116',):
        continue
    s = r['скрипты'].split(';')
    S.append('| %s | `%s` | %s | %s |' % (r['тема'], r['ключ'].replace('|', '\\|'),
                                        {'kept_text_upstream': 'текст есть', 'removed_upstream': '**удалена**'}[r['судьба_в_upstream']],
                                        ', '.join('`%s`' % x.replace('docs/', '') for x in s[:3]) + (
                                            '' if len(s) <= 3 else ' (+%d)' % (len(s) - 3))))
S.append('')
S.append('Особо: T116 — строка `flipPendingNum` в upstream печатается только при `--graphics-debug-dump` (`a20fb7f9`): '
         '`f34a/flipmap.py`, `f9a/scan_log.py` ослепнут без флага; T124 — строки «Relocate: unresolved PLT import patched to stub», '
         '«Late-resolved import:», «=== Stubbed function, returning OK ===» удалены; T151 — «RenderColorTarget: slot=» удалена; T017 — '
         'строка нулевого dispatch сохранена, проверка перенесена до подготовки программы.')
S.append('')
S.append('### 14.5 RC5: темы Д против кадра ≥ 1 с')
S.append('')
S.append('T163, T239, T155, T178 — класс Д, строка: «%s».' % line_of['T163'].split(' ‖ ')[-1])
S.append('')
S.append('### 14.6 RC6: что превратит В в В′ или Б')
S.append('')
for t in ('T021', 'T240', 'T069', 'T255', 'T007'):
    txt = [x for x in line_of[t].split(' ‖ ') if 'RC6' in x][0]
    S.append('- **%s** — %s' % (t, txt))
S.append('')
S.append('### 14.7 Проверки')
S.append('')
S.append('`check_m1a.py` — `564 of 564`, якорей 224, `ALL OK`; `m1b/cov_m1b.py` — `ALL OK`; `m1a2/check_m1a2.py` — члены (1)–(6) и счёт '
         'классов, `ALL OK`; `mk_sig_m1a2.py`, `grep_sig_m1a2.py selftest`, `lds_m1a2.py`, `wit_m1a2.py` — `ALL OK`. Выводы — '
         '`m1a2/*.out.txt`; sha256 — в отчёте звена.')
S.append('')
S.append('### 14.8 Не заявляется (M1a2)')
S.append('')
S.append('Что какая-либо тема А-резерв игра на невиданных уровнях исполняет или не исполняет; что сигнатуры покрывают все пути отказа '
         'темы (найдены места, которые снимают коммиты upstream; путь без печати — [U]); что 33 строки предтрансляции относятся к '
         'конкретной теме RT; что предел LDS другого устройства ниже 49 152 Б; что проверки §14.6 дадут В′; ни одно число — не '
         'выигрыш; 60 FPS не обещаются; цель (B) не меняется.')
S.append('')
md = md.rstrip('\n') + '\n\n' + '\n'.join(S)
open(os.path.join(M1, 'upstream.md'), 'w', encoding='utf-8', newline='\n').write(md)
print('upstream.md written; §10 class cells changed:', sum(1 for t in new_cls if new_cls[t] != old_cls[t]),
      'nokey themes', len(nokey))
