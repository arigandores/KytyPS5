"""M1a (HPP-835): write docs/track-m/m1/upstream.md from themes.json + merged tables (out/)."""
import json, csv, collections, os, re, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
D = 'C:/kyty/m657/m1a/'
O = D + 'out/'
C = json.load(open(D + 'commits.json', encoding='utf-8'))
R = json.load(open(D + 'merged_raw.json', encoding='utf-8'))
T = json.load(open(D + 'themes.json', encoding='utf-8'))
order = list(C.keys())
LINE = re.compile(r'b3dc9c67:([^:\s]+):(\d+)')

def cell(s, n=None):
    s = (s or '').replace('|', '/').replace('\n', ' ').replace('\t', ' ').strip()
    if n and len(s) > n:
        s = s[:n - 1].rstrip() + '…'
    return s

def best_rel(t):
    rs = [R[h]['relevance'] for h in t['hs']]
    return max(rs, key=len)

def basis_ref(t):
    for h in t['hs']:
        m = LINE.search(R[h]['basis'])
        if m:
            return '`b3dc9c67:%s:%s`' % (m.group(1), m.group(2)), R[h]
    for h in t['hs']:
        b = R[h]['basis'].strip()
        if b not in ('-', ''):
            return cell(b, 160), None
    return '—', None

def commits(t):
    return ' '.join('`%s`' % h[:8] for h in t['hs'])

cnt_c = collections.Counter(R[h]['class'] for h in order)
cnt_t = collections.Counter(t['cls'] for t in T.values())
conf_t = collections.Counter((t['cls'], t['conf']) for t in T.values())
CL = ['А', 'Б', 'В', 'В′', 'Г', 'Д']
L = []
A = L.append
A('# M1a (трек M, `HPP-835`): опись отставания от upstream `6a2987a7..origin/main` `dad900c6`')
A('')
A('Исполнитель — Emu Engineer, 2026-10-12 (UTC). Правило класса — `ROADMAP.md` п. 752(в) (= п. 633(в) + (В′)); обязательные члены — п. 752(г)(1)–(7).')
A('Upstream: `origin` = `KytyPS5/KytyPS5`, `origin/main` `dad900c6`, база (merge-base) `6a2987a7`; 564 коммита без слияний, 376 файлов. Основания —')
A('на нашем `main` `b3dc9c67` (текущая вершина `068d7224` отличается от `b3dc9c67` только `docs/ROADMAP.md`, п. 752). Ни один из 564 коммитов')
A('не перенесён к нам раньше (`git cherry b3dc9c67 origin/main 6a2987a7` — 564 из 564 `+`; совпадений заголовков с нашими коммитами — 0).')
A('Игра не запускалась, замок не брался, код `main` не менялся, сборок не было. Пометки: [c] — проверено кодом или данными, [I] — вывод,')
A('[U] — неизвестно; утверждения upstream о проверке («fixes …», «tested») для нас [I].')
A('')
A('Файлы звена: `upstream.tsv` (машинная таблица `sha`, `тема`, `класс`, `файлы`), `upstream_detail.tsv` (все поля строки: суть, основание,')
A('якорь и +1, судьба нашей правки, довод по ASTRO BOT, уверенность, подпись трансляции, задетые наши ханки ручек), `check_m1a.py` (проверка')
A('покрытия, классов и якорей — печатает `564 of 564` и `ALL OK`), приложения `m883.md` (член (5)) и `tests.md` (член (6)), свидетельства')
A('`evidence/` (`ophist.tsv`, `overlap.tsv`, `knobs.md`), скрипты `tools/`.')
A('')
A('## 0. Итог')
A('')
A('| класс | смысл (п. 752(в)) | тем | коммитов | из них тем c / I / U |')
A('|---|---|---|---|---|')
mean = {'А': 'у нас нет, корректность ASTRO BOT — кандидат на перенос', 'Б': 'у нас сделано и проверено — не брать',
        'В': 'пересекается с нашим кодом иначе — решение по данным M1c', 'В′': 'upstream лучше — только со свидетельством у нас',
        'Г': 'вне цели — не брать', 'Д': 'только скорость — справка, перенос только по A/B M3'}
for c in CL:
    A('| %s | %s | %d | %d | %d / %d / %d |' % (c, mean[c], cnt_t.get(c, 0), cnt_c.get(c, 0), conf_t.get((c, 'c'), 0), conf_t.get((c, 'I'), 0), conf_t.get((c, 'U'), 0)))
A('| всего | | %d | %d | |' % (len(T), len(order)))
A('')
A('Уверенность темы — худшая из её строк (U > I > c). Тем В′ — 0: проверяемого у нас свидетельства, что upstream-вариант лучше нашего, нет ни')
A('для одной темы (по правилу — тогда Б или В).')
A('')
A('**Главное для M1c (прочтение исполнителя, не решение):**')
A('')
A('1. Сильнейшие кандидаты А с [c] по коду и данным игры: `T233` legacy MAD (`d8be245c2`: у нас `V_MAD_F32`/`V_MAC_F32`/`V_MADMK`/`V_MADAK` —')
A('   слитный `Fma`; игра исполняет `V_MAD_F32` 642 242 раза в 5 540 программах и `V_MAC_F32` 730 734 раза в 5 532 из 5 698), `T234`')
A('   `DS_MIN/MAX_F32` (`e85279ea7`: в коде игры поле data1 = регистр адреса — компилятор игры считает инструкцию двухоперандной, у нас')
A('   сравнение идёт с data1), `T265` ID файлов AMPR (`e43aadf75`: 31-битный FNV-1a, 5 пар путей пакета ASTRO BOT с равным хэшем), `T272`')
A('   состояние курков (`3c62359e0`: игра ставит эффекты курков, у нас `scePadGetTriggerEffectState` всегда 0). Видимое следствие ни одной')
A('   из них у нас не показано — критерий «ИСПРАВЛЕНО» до кода (п. 633(г)) требует воспроизведения.')
A('2. Темы транслятора А (`T032`, `T113`, `T200`, `T203`, `T233`, `T234`, `T257`, `T306`) меняют подпись трансляции — цена холодный вход и прогрев')
A('   (п. 418(в)); `T257` (ветвление всей волной) стоит на `ConditionRef` из #883 и меняет все шейдеры.')
A('3. Переход upstream на SDL3 (`T093`, `f68c77d78`) — основа почти всех поздних правок звука, ввода и окна upstream; он переписывает места')
A('   трёх отгруженных правок (Ф8 `KYTY_FIX_F8`, Б24 `KYTY_FIX_B24`, Ф24 `KYTY_FIX_F24`). Перенос любой правки звука/ввода upstream после')
A('   2026-09-23 — ручной.')
A('4. #883 (`T138`) — класс В по частям; маска привязки цвета (р1) у нас — Б (условия «формат слота ≠ 0» у нас нет — механизма потери травы')
A('   нет); подробно — §8 и `m883.md`.')
A('5. Наш код в областях кэша текстур, рендера и материализации переписан сильно (наш `textureCache.cpp` — 6 620 строк против 2 016 у')
A('   upstream): почти любой перенос оттуда — ручная интеграция, не cherry-pick.')
A('')
A('## 1. Метод')
A('')
A('1. Опись коммитов (`tools/m1a_prep.py`): заголовки, файлы, признаки «трогает файл с нашей ручкой», «трогает набор подписи трансляции»')
A('   (набор — `src/graphics/shader/**/*.{cpp,h,inc}` + `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`:')
A('   `b3dc9c67:CMakeLists.txt:156`), путь, которого у нас нет.')
A('2. Корзины по путям (`tools/bucket_m1a.py`, 12 корзин) — разбор девятью помощниками-разборщиками по одним правилам (`tools/agent_rules.md`):')
A('   каждая строка — тема, класс, суть, основание с якорем и +1, судьба нашей правки, довод по ASTRO BOT, уверенность. Сводка и проверки —')
A('   исполнитель: покрытие 564 из 564, один класс на тему, все 224 якоря `b3dc9c67:<путь>:<строка>` сверены с текстом строки и строки +1')
A('   (`check_m1a.py`), выборочная сверка сильнейших А по коду.')
A('3. Свидетельства отношения к ASTRO BOT: (а) `evidence/ophist.tsv` — гистограмма опкодов всех 5 698 уникальных шейдерных программ')
A('   `eboot.bin` (обход F23a `gcn_f23a.walk`; `tools/ophist_m1a.py`; опкода нет в таблице — игра его не исполняет [c]; оговорка: поле op MUBUF')
A('   взято 7 битами, проверка помощника с битом 25 — опкодов 0x80–0xff в игре нет, выводы не меняются; программы вне `eboot.bin` — 96 SWAPPC')
A('   и пр. — гистограмма не видит); (б) импорты NID `eboot.bin` и `sce_module/*.prx` (таблицы `LIB_FUNC` нашего кода); (в) логи установленного')
A('   FS15 (`log_fs15_v`, `log_fs15_z`), фильтр по строкам; (г) реестр трека F `docs/track-f/register.md`; (д) `evidence/overlap.tsv` — место')
A('   правки upstream против наших ханков (координаты базы `6a2987a7`, допуск 3 строки, `tools/overlap_m1a.py`).')
A('4. Прочтение класса Г исполнителем: кроме лаунчера, CI, доков и сборок Linux/macOS, в Г — правки путей, которых ASTRO BOT не исполняет,')
A('   только со свидетельством (опкод 0 в `ophist`, NID не импортируется, платформа не Windows); без свидетельства — Г с уверенностью U (список')
A('   для M1b — §5). Чистые рефакторинги без изменения ответа — Г или Д (если заявлена скорость).')
A('')

def theme_table(cls, title, n_ess=220):
    ts = [t for t in T.values() if t['cls'] == cls]
    A(title)
    A('')
    A('| № | ключ | коммиты | суть | довод по ASTRO BOT | основание | подп. | ув. |')
    A('|---|---|---|---|---|---|---|---|')
    for t in ts:
        ref, _ = basis_ref(t)
        ess = t['title'] + ': ' + ' / '.join(cell(e, 160) for e in t['ess'][:3]) + (' …' if len(t['ess']) > 3 else '')
        A('| %s | `%s` | %s | %s | %s | %s | %s | %s |' % (t['id'], t['key'], commits(t), cell(ess, n_ess * 2), cell(best_rel(t), 420), ref,
                                                    'да' if t['sig'] else 'нет', t['conf']))
    A('')

theme_table('А', '## 2. Класс А — кандидаты на перенос (%d тем)' % cnt_t.get('А', 0))
A('Кандидат А — не решение о переносе: по п. 633(г) перенос идёт итерацией формы трека F с критерием «ИСПРАВЛЕНО» до кода (дефект')
A('воспроизводится у нас), иначе перенос — справка. Темы `T159` (AMPR-очередь) и `T309` (размер записи `WriteAddress`) связаны: `41beda436`')
A('стоит на исполнителе APR из `c045f0890`.')
A('')
theme_table('В', '## 3. Класс В — пересекается с нашим кодом иначе (%d тем)' % cnt_t.get('В', 0))
theme_table('Б', '## 4. Класс Б — у нас сделано (%d тем)' % cnt_t.get('Б', 0))
A('## 5. Класс Д (%d тем) и Г (%d тем)' % (cnt_t.get('Д', 0), cnt_t.get('Г', 0)))
A('')
A('Полные строки — §10 и `upstream_detail.tsv`. Темы Г с уверенностью U (Г без свидетельства [c] — первыми на отзыв M1b «не выброшено ли нужное»):')
A('')
A('| № | ключ | коммиты | название | почему Г / чего не хватает |')
A('|---|---|---|---|---|')
for t in T.values():
    if t['cls'] == 'Г' and t['conf'] == 'U':
        A('| %s | `%s` | %s | %s | %s |' % (t['id'], t['key'], commits(t), cell(t['title'], 120), cell(best_rel(t), 360)))
A('')
# ---- member (3)
A('## 6. Член (3): пересечение с отгруженным')
A('')
A('Ручки — `evidence/knobs.md` (23 строки `FIXED` реестра §129, все отгружены под (B), + трек S + трек P). Тем, трогающих файл с нашей ручкой')
A('(без `tests/`), — %d; из них место правки upstream задевает наш ханк с ручкой (по `overlap.tsv`) — %d.' % (
    sum(1 for t in T.values() if t['kf']), sum(1 for t in T.values() if t['kh'])))
A('')
A('### 6.1 По ручке: какие темы задевают её место')
A('')
byk = collections.defaultdict(set)
for t in T.values():
    for x in t['kh']:
        for k in re.findall(r'KYTY_\w+', x):
            byk[k].add(t['id'])
        if 'call-site' in x:
            byk['(место вызова гейта: ' + x.split(':')[0] + ')'].add(t['id'])
A('| ручка / место | строка реестра | темы, задевающие наш ханк |')
A('|---|---|---|')
reg = {}
for l in open(D + 'knobs.md', encoding='utf-8'):
    m = re.match(r'\| `(KYTY_\w+)` \| ([^|]+) \|', l)
    if m:
        reg[m.group(1)] = m.group(2).strip()
for k in sorted(byk):
    A('| %s | %s | %s |' % (k if k.startswith('(') else '`%s`' % k, ('место вызова гейта, имя ручки в ханке не названо' if k.startswith('(') else reg.get(k, '— (не отгружена: диагностика, умолчание 0)')), ', '.join(sorted(byk[k]))))
A('')
A('Ручки без единой задетой темы: %s.' % ', '.join('`%s`' % k for k in reg if k not in byk))
A('')
A('### 6.2 Что будет с нашей правкой — по темам')
A('')
A('Для каждой темы, трогающей файл с ручкой: файлы, задетые наши ханки (`overlap.tsv`), строка «что будет с нашей правкой».')
A('')
for t in T.values():
    if not t['kf']:
        continue
    A('- **%s** `%s` (%s): файлы — %s; задеты ханки ручек — %s.' % (t['id'], t['key'], t['cls'],
                                                                 ', '.join('`%s`' % f.rsplit('/', 1)[-1] for f in t['kf']),
                                                                 '; '.join(t['kh']) if t['kh'] else 'нет'))
    for n in t['notes']:
        A('  - %s' % cell(n))
A('')
# ---- member (4)
A('## 7. Член (4): подпись трансляции')
A('')
sig = [t for t in T.values() if t['sig']]
A('Тем, меняющих набор подписи трансляции (`src/graphics/shader/**` и три заголовка + `shaderTranslationCache.cpp`), — %d (коммитов — %d).' % (
    len(sig), sum(1 for h in order if any((p.startswith('src/graphics/shader/') and p.rsplit('.', 1)[-1] in ('cpp', 'h', 'inc')) or p in (
        'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 'src/graphics/guest_gpu/gpu_format.h',
        'src/graphics/guest_gpu/gpu_defs.h', 'src/graphics/host_gpu/renderer/image/imageInfo.h') for p in C[h]['files']))))
A('Перенос любой из них меняет подпись `KYTY_SHADER_SOURCE_HASH` — холодный каталог трансляции у пользователя, прогрев (п. 418(в)); каталоги')
A('`_ShaderSeeds` и повтора S-replay собраны на подписи `9177b426…` — тоже холодные до пересборки. По классам:')
A('')
for c in CL:
    ids = [t['id'] for t in sig if t['cls'] == c]
    if ids:
        A('- **%s** (%d): %s' % (c, len(ids), ', '.join(ids)))
A('')
A('Отдельно (не подпись трансляции, но ключ пайплайна — рецепты precache и каталог S-replay холодные после переноса, по строкам помощников):')
keyc = [t for t in T.values() if any(('ключ пайплайна' in n or 'ключ программ' in n or 'рецепт' in n) for n in t['notes'] + [best_rel(t)])]
A(', '.join('%s `%s`' % (t['id'], t['key']) for t in keyc) + '.')
A('')
# ---- member (5)
A('## 8. Член (5): upstream #883 и трава Sky Garden (п. 633(д))')
A('')
A('Полный разбор — `m883.md` (якоря проверены). Кратко [c кода, I вывода]:')
A('')
A('1. #883 = `0791f921f` «UFC 5 in-game» (34 файла, +3 226 / −2 265). Маска цвета — только в `renderDraw.cpp`: `DrawHasActivePixelShader` →')
A('   `DrawColorOutputMask` (бит слота — только при `SPI_SHADER_COL_FORMAT[slot] != 0` и слоте в `CB_TARGET_MASK & CB_SHADER_MASK`), от неё')
A('   `ps_active`, отображение экспорта и `mrt_mask &= color_output_mask` — вложение привязывается только при ненулевом формате (эта строка')
A('   теряет траву в форке `BryanKAdams/BryKytyPS5` после их слияния `585fc13f`). Остальное в #883: граница сэмплера int/float (р2), сброс')
A('   денормалей во входах `V_CMP_*_F32` (р3), границы `DS_APPEND/CONSUME` (р4), выравнивание скалярных чтений (р5), переписанный CFG и')
A('   `ConditionRef` (р6, основная масса), отладочный дамп (р7), косметика эмиттера (р8).')
A('2. У нас (`b3dc9c67`): вложения привязываются по маске целей и базе (`renderDraw.cpp:3014`), активность PS — по `CB_TARGET_MASK &')
A('   CB_SHADER_MASK` (`:2649`), условия «формат слота ≠ 0» нет ⇒ механизма потери травы у нас нет; правило привязки проверено данными (Ф6')
A('   `НЕ ДЕФЕКТ`, реестр §59: `bound_missing` = `bound_extra` = 0 на Sky Garden). Оговорка: счётчик Ф6 читает `CB_COLORn_INFO.FORMAT`, не')
A('   `SPI_SHADER_COL_FORMAT`.')
A('3. Правка форка `26d62f80` возвращает привязку по маске записи (`DrawColorWriteMask`) — по сути наше нынешнее поведение; форматная маска')
A('   upstream остаётся только для `ps_active` и отображения экспорта. Если логику #883 переносить, `26d62f80` обязательна; ханки #883 стоят на')
A('   upstream `b594f8c83`(б), на наш код не ложатся; менять согласованно все три вызова `DrawHasActivePixelShader` (`:3034`, `:3634`, `:3676`).')
A('   С Б35 совместима; конфликт с Б35 — только при переносе `649367472`, `21a1346e2` или `73615c31f`.')
A('4. Класс #883 — **В** (неоднороден): р1 Б, р2–р4 кандидаты А без довода исполнения (р2) или с исполнением опкода (р3 `VOPC:1` 24 607')
A('   инструкций, р4 `DS:3e` в 239 программах) — U, р5–р6 В, р7 Г, р8 Д. **Член M1c/M3 при переносе #883 или его р1:** V Sky Garden')
A('   (`underwater_aerial_garden`) в форме `fs15_v` и пара листов с `fs15_v` — средняя трава у тропы на тех же кадрах; положительный контроль —')
A('   сборка без `26d62f80` обязана потерять траву (иначе лист не детектор); W Sky Garden и W `mini_giants_garden` с 0 `[Vulkan][E]`; для')
A('   `21a1346e2` — сначала замер на Sky Garden (draw, где номер слота по `CB_SHADER_MASK` ≠ номеру экспорта; экспорты в слот с нулевым')
A('   `COL_FORMAT`).')
A('5. Связанные upstream-коммиты маски цвета: `b594f8c83` (`T020`, В: (а) сохранение слотов — Б, наш `d844f4cb2`; (б) привязка по экспорту')
A('   PS — В), `649367472` (`T046`, Б — наш Б35, вместе брать нельзя), `73615c31f`/`0bef3fc0d` (`T156`, В, U), `21a1346e2` (`T255`, В, U),')
A('   `b96871e2b` (SNORM16-экспорт, Г [c]: в 5 866 PS-рецептах четырёх `pipelines.bin` режимы целей только 1 и 4).')
A('')
# ---- member (6)
A('## 9. Член (6): тесты upstream, применимые без кода')
A('')
A('Полный разбор — `tests.md` (статически, [I]: пробной сборки не было). Общие преграды: upstream на SDL3 (у нас SDL2), сигнатура')
A('`SrtMemoryReader` (`std::span` против `uint32_t*`), свой харнесс `Check`/`KYTY_TESTS_CONTINUE` — изменённые файлы целиком не переносятся,')
A('переносятся отдельные функции.')
A('')
A('- Новые файлы (15): без кода и годен — только `LruCacheTests.cpp`; компилируются, но вне игры или с ожидаемым провалом — `CesTests.cpp`,')
A('  `HttpUriParseTests.cpp`, `SaveDataDialogTests.cpp`; остальные 11 не переносятся (нет `common/archive.h`, `trophies.h`, `ngs2.cpp`,')
A('  `libPngEnc.cpp`, `dualSense*`, `guestInstructionPatcher.h`; SDL3).')
A('- **Кандидаты в гейт `shader_cfg_tests`** (перенос функции в `tests/shaderCfgTests.cpp`, код не меняется; каждому нужен прогон):')
A('  `TestDsFloatMinMaxDecoder` (DS_MIN/MAX_F32 — путь игры, см. `T234`), `TestShaderStageBarriers` (S_BARRIER — 66 программ),')
A('  `TestVertexBufferGrouping`, `TestSpirvRepeatedEmission`, `TestU64RegisterPairRoundTrip`, `TestShaderFeatureCollection`,')
A('  `TestRayTracingInstructions` (после правки члена теста: у нас BVH64 — отдельный опкод `IMAGE_BVH64_INTERSECT_RAY`). Условно — 6')
A('  CFG-тестов `…Cfg…Structured` и `TestNggVertexEntryState`. Из 47 новых функций `shaderCfgTests.cpp` без кода переносятся 22.')
A('- GPU-кандидаты (`shader_recompiler_compute_tests`, ≈ 30 `TestCase` на опкодах, которые игра исполняет) и прочие цели — `tests.md` §5.2.')
A('- Пробы (провал на `b3dc9c67` ожидаем — сигнал для M1c, не гейт): `VectorMadF32RoundsProduct`/`VectorMadF32FlushesDenorms` (`T233`),')
A('  `BvhIntersections` (расхождения решать по GPURT, не по upstream; тройки типов 2–3 фикстуры совпадают с нашим Ф10), CPU-пробы выбора')
A('  дескриптора по ветви, AudioOut2 (`T125`).')
A('')
# ---- full table
A('## 10. Все темы')
A('')
A('| № | ключ | класс | ув. | коммиты | название | основание | подп. | файлы ручек |')
A('|---|---|---|---|---|---|---|---|---|')
for t in T.values():
    ref, _ = basis_ref(t)
    A('| %s | `%s` | %s | %s | %s | %s | %s | %s | %s |' % (t['id'], t['key'], t['cls'], t['conf'], commits(t), cell(t['title'], 140), ref,
                                                      'да' if t['sig'] else 'нет',
                                                      ', '.join('`%s`' % f.rsplit('/', 1)[-1] for f in t['kf']) or '—'))
A('')
# ---- anchors
A('## 11. Якоря оснований (строка и контроль +1)')
A('')
A('Для каждой темы с основанием-строкой: `b3dc9c67:<путь>:<строка>` — «якорь» / +1 «следующая строка». Все строки всех 564 коммитов с такими')
A('основаниями (224) проверяет `check_m1a.py` по `upstream_detail.tsv`.')
A('')
for t in T.values():
    ref, row = basis_ref(t)
    if row is None:
        continue
    A('- %s %s — «%s» / +1 «%s»' % (t['id'], ref, cell(row['anchor']).replace('`', "'"), cell(row['anchor_plus1']).replace('`', "'")))
A('')
A('## 12. Сомнения и долги исполнителя')
A('')
A('1. Отношение к ASTRO BOT для HLE-тем (`sys-*`, `av-*`) — импорт NID [c] плюс вывод [I]: логи игры не печатают вызовы HLE, факт вызова виден')
A('   только по строкам `LOG` разрешённых функций. Сильнейшие Г с U (§5) — путь, возможно, исполняется (например темы `img-*` о трафарете и')
A('   BC-алиасах, `rnd-*` о RectList/PM4 CHAIN, `ir-tdesc-valid`).')
A('2. Отсутствие фатала по логам покрывает только пройденные уровни (59 входивших из 114) — такие Г помечены I, не c.')
A('3. Класс ставится на коммит целиком; в смешанных коммитах (`0791f921f`, `89792a3bc`, `bec67b786`, `e6cb880ad`) части расписаны в `relevance`')
A('   (`upstream_detail.tsv`) и в `m883.md`.')
A('4. Направление ISA для `DS_MAX_F32` (наш порядок сравнения против документа) — [I]; довод `T234` опирается на код игры (data1 = регистр адреса).')
A('5. Пары «коммит + revert» (`cd9fc6ff2`/`266c12cec`, `5b68a26cc`/`1c301c9aa`, `165234b15`/`c2b7b0b58`) — Г с [c] (итог 0 изменений).')
A('6. Пересечение мест (`overlap.tsv`) — механика по координатам базы с допуском 3 строки; файлы `tests/` шумят (регистрация фикстур в конце файла),')
A('   в §6 не учитываются.')
A('7. Пробной сборки не было (п. 752(г)(7) — по желанию исполнителя); выводы о компиляции тестов — [I].')
A('')
A('## 13. Не заявляется')
A('')
A('Что upstream лучше или хуже нашего; что перенос любой темы что-то исправит у нас; что кандидаты А дают видимый дефект ASTRO BOT; что темы Г')
A('с уверенностью U игрой не исполняются; что опись полна по смыслу внутри больших коммитов; что CI или тесты upstream проходят у нас; ни одно')
A('число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.')
A('')
open(O + 'upstream.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
print('lines', len(L), 'bytes', os.path.getsize(O + 'upstream.md'))
