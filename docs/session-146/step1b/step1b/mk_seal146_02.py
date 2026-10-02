"""mk_seal146_02.py - session 146 link 1b (HPP-395; ROADMAP s122 item 316): writes C:/kyty/s146/pred/02_sc146.md, the seal of the
series sc146 that REPLACES pred/01_sc146.md (01 is not edited), BEFORE the first run of the series.  The port of
step0/mk_seal146.py: the same sections 1-4, the skip of a W as item 316 (b)-(d) reads it (new section 5), the sha256 lines
(section 6) computed now from their files, the outputs of link 1b and of step 0 named with their sha256.  UTF-8, LF."""
import hashlib
import importlib.util
import os
import subprocess

ROOT = 'C:/kyty/s146'
spec = importlib.util.spec_from_file_location('sc146', ROOT + '/sc146.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def sha(p):
    p = p if p.startswith('C:/') else os.path.join(ROOT, p)
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def tail(p, n=1):
    with open(os.path.join(ROOT, p), 'rb') as f:
        return [x.decode('ascii', 'replace').rstrip() for x in f.read().split(b'\n') if x.strip()][-n:]


def outs(lst):
    r = []
    for o in lst:
        p = os.path.join(ROOT, o)
        if os.path.isfile(p):
            r.append('- `%s` `%s`: %s' % (o, sha(o)[:16], tail(o)[0][:200].replace('|', '/')))
        else:
            r.append('- `%s`: ОТСУТСТВУЕТ' % o)
    return r


utc = subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()
OUT1B = ('step1b/test_sc146.out.txt', 'step1b/test_gate146.out.txt', 'step1b/test_go146a.out.txt', 'step1b/test_tools146.out.txt',
         'step1b/test_fgcpu146.out.txt', 'step1b/regress145.out.txt', 'step1b/calib146.out.txt', 'step1b/check1b146.out.txt',
         'step1b/mut_only1b.txt', 'step1b/skipfx1b.out.txt')
OUT0 = ('step0/jsonsrc145.out.txt', 'step0/tilereg146_1.out.txt', 'step0/tilereg146_2.out.txt', 'step0/lvl146.out.txt',
        'mut_sc146.txt', 'step0/run1/mut_sc146.run1.txt', 'step0/mut_screen1.txt', 'step0/mut_screen2.txt',
        'step0/mut_screen3.txt', 'step0/test_i146.out.txt', 'step0/setup146.out.txt')
L = []
L.append('# Печать 02 серии `sc146` — звено 1б с. 146 (`pred/02_sc146.md`, взамен `pred/01_sc146.md`)')
L.append('')
L.append('Звено 1б с. 146 (`HPP-395`, Harness Engineer). Записана %s (UTC по `date -u`) ДО первого прогона серии `sc146`. Основание — `ROADMAP.md`' % utc)
L.append('«СЕССИЯ 122» **п. 316(б)–(д)** (KytyPS5 `3feacb81`; отзыв шага 1 `788e264f:docs/session-146/review146.md`, RC1 — вариант (а), RC2 — вариант')
L.append('исполнителя) и все основания печати 01: п. 309(к), (л)(1)–(7), 300(б)(2)–(4), 281(г), 295, 273(к)(4), 221(г)(3), 313, 314, 315. Перечитаны пункты')
L.append('после выдачи звена: последний пункт `ROADMAP.md` на момент печати — 316; комментариев в `HPP-395` нет.')
L.append('**Печать 01 (`pred/01_sc146.md` `%s`) не правится и заменена этой; серия по ней не шла (п. 316(в)).** Константы печати 01 не' % sha('pred/01_sc146.md')[:16])
L.append('меняются; меняются только правило пропуска W пары (§5) и путь печати в `sc146.py`, `go146a.sh`, `step2/gate146.py`, `step2/call_one.sh` и их наборах.')
L.append('Печать установки и прогрева — `pred/00_i146.md` (`%s`).' % sha('pred/00_i146.md')[:16])
L.append('')
L.append('## 1. Серия: 35 тегов, порядок, по одному вызову (п. 309(л)(2), п. 313(б))')
L.append('')
L.append('| тег | форма | уровень |')
L.append('|---|---|---|')
for t in S.SEQ:
    form = 'W контрольный' if t == S.CONTROL[0] else ('V повторной проверки' if t in ('r146_01', 'r146_02', 'r146_03') else (
        'V второе удержание (p Б40)' if t == 'r146_04' else ('V холодный первый вход' if t.startswith('v146_') else 'W пары')))
    L.append('| `%s` | %s | `%s` |' % (t, form, S.level_of(t)))
L.append('')
L.append('**V** — отгруженные умолчания установленного `dac02fb9` (precache по умолчанию, пустой файл ворот), видео `KYTY_REC`, удержание 330 с стены,')
L.append('`--stable-draws 300 --timeout 480`, `--attempts 1`. **W** — `--vulkan-validation true`, `VK_LAYER_PATH`, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000`,')
L.append('без `VK_LAYER_MESSAGE_ID_FILTER`, без `KYTY_PIPELINE_PRECACHE` (precache по умолчанию, п. 300(б)(4)), удержание 310 с, без видео,')
L.append('`--stable-draws 300 --timeout 600`. Каждый прогон: `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`; `KYTY_GPU_CHECKPOINTS` не передаётся.')
L.append('**W пары не вызывается только по правилу §5** (п. 309(к)(1) в редакции п. 316): `go146a.sh` спрашивает `sc146.py --skip-w <w>` до замка; ответ')
L.append('`SKIPPED_V_NOT_ENTERED` — файл `skipped_<w>.txt` и строка `times.txt` с полной строкой ответа (ключ V в ней), rc 0, не попытка, порядок идёт дальше;')
L.append('ответ `RUN` — W запускается.')
L.append('')
L.append('## 2. Чтение (`sc146.py`, профиль 146) — правила `sc145.py` без изменения констант (п. 309(л)(4))')
L.append('')
L.append('- `SCENE_OK` уровня — по паре одной сессии на `dac02fb9` (`v146_NN`/`w146_NN`); пар с W `9235a7ac` нет; строки V/W, лист, sha листа и видео —')
L.append('  как `sc145` (п. 221(г)(3), 224(а)); слово `YES` — только с отметкой листа лидом.')
L.append('- Форма W на бинаре отгрузки: строка допуска «W form on the shipment binary: no KYTY_PIPELINE_PRECACHE in the env»; строки')
L.append('  `PipelinePrecache: N recipes ->` у W — строка данных. Форма п. 295(б)(1)–(4) — без изменений.')
L.append('- **`DualSrcBlend: supported=1 enabled=1` до первой `GuestOut`:** у контрольного `w146_00` — член буквы его остановки (п. 300(б)(4)); у каждого W —')
L.append('  строка данных (п. 309(л)(4), п. 315); рядом печатается вариант исполнителя по п. 281(г) («нет — тег FAIL») с пометкой [I], в вердикт не входит.')
L.append('- Строки данных (не гейт, п. 309(л)(4)): `stubs` (Ф13, строки `Unresolved import stub called`, лог и stdout), `asserts` (Ф14, `ASSERT:` и')
L.append('  `user_msg_param`; ≠ 0 — строка закрытия в реестр F), события по плиткам у каждого V (Д-4: правило аудитора AUDIT145 §1.4, плитки 4×4, порог 4,')
L.append('  `tiles146.py` → `tiles_<V>.txt` и тройки кадров `tiles_<V>.png` для листа лида).')
L.append('- `r146_01`…`r146_03`: строка «RECHECK <уровень>: PASSES / REMOVES SCENE_OK / PENDING_SHEET» по строкам V п. 221(г)(3), строке')
L.append('  «guest args / json level / sha лога = times.txt» и отметке листа; `r146_04`: строка «B40 SECOND HOLD» с кадрами K2 (данные для p Б40).')
L.append('- Sky Garden на `dac02fb9` (п. 300(д)): строка-справка — `WARMUP VERDICT` из `score_i146_v.txt` и исход контрольного W; слово `SCENE_OK` Sky')
L.append('  Garden этим скорером не печатается (решение — закрытие).')
L.append('- Остановки (п. 273(к)(4), 309(л)(5)): контрольный W остановлен (буква: маркер смерти, `[Vulkan][E]`, строки лимита слоя, нет строки')
L.append('  DualSrcBlend; чтение исполнителя [I] для шлюза — любая строка W, принято п. 315); два W подряд остановлены до первой `GuestOut` одним ключом;')
L.append('  **три V подряд** `NOT_ENTERED` одним маркером — по всем сделанным V серии в порядке (`r146_*` и `v146_*`; принято п. 315); событие окна на')
L.append('  сделанном теге прямо перед. `--stop-check` читает `runs146/<тег>.score.json`, если его sha лога = строке `enter_scene end` `step2/times.txt`,')
L.append('  иначе лог; источник — строкой `STOP CHECK SOURCES`. Пропущенный W (§5) — не сделанный тег правил остановки.')
L.append('- Шлюз шага 2 `step2/gate146.py`: `--start` — эталон `runs146/cache_i146_v.after.json` (конец прогрева) по строке этой печати; кэш трансляции')
L.append('  (`PPSA21564` с каталогом `variant_fixb26_fixb1b`) отличается — STOP, кэши драйвера — данные; ≥ 60 GiB на C:; `--before <тег>` — члены (w), (b) (форма')
L.append('  W по env), (f), (v), (e), (l), (c)(2), (g) на сделанном теге прямо перед (пропущенный W проходится до V перед ним).')
L.append('')
L.append('## 3. Доказательства (выводы — с sha256)')
L.append('')
L.append('Звено 1б (наборы на файлах этой печати; `regress145`, `calib`, `check1b` — байт в байт = шагу 0):')
L.append('')
L.extend(outs(OUT1B))
L.append('')
L.append('Шаг 0 (без изменений; выводы, которые звено 1б не повторяло, — входы не менялись: `jsonsrc145`, плитки, список уровней, полный прогон мутантов):')
L.append('')
L.extend(outs(OUT0))
L.append('')
L.append('## 4. Вызовы (ровно одна строка на тег; другой `PLWAIT` — отказ rc 1)')
L.append('')
for t in S.SEQ:
    L.append('go146a call: PLWAIT=540 bash C:/kyty/s146/go146a.sh %s' % t)
L.append('')
L.append('## 5. Пропуск W пары (п. 309(к)(1) в редакции п. 316(б)–(г); заменяет букву печати 01)')
L.append('')
L.append('`sc146.py --skip-w <w>` (функция `skip_w`) отвечает `SKIPPED_V_NOT_ENTERED` (rc 0) **только** при положительном свидетельстве, что V пары')
L.append('не вошёл, — все члены сразу:')
L.append('1. у V есть чтение (`runs146/<v>.score.json`, если его sha лога = строке `enter_scene end` `step2/times.txt`, иначе лог) и исход `NOT_ENTERED`')
L.append('   (строки `Level has started: <уровень>` нет);')
L.append('2. файл `log_<v>.txt` есть; 3. его размер > 0 байт; 4. его sha256 **сейчас** = последней строке `<chain> <v> enter_scene end … sha256` в')
L.append('   `step2/times.txt` (п. 316(б); в чтении по json — файл на диске, а не sha из json);')
L.append('5. ключ V — `attempt:<исход>` (V ушёл без маркера смерти и без строки входа). Ключ-маркер — K1 (`--- Error ---`, `--- Fatal Error ---`,')
L.append('   `Unhandled exception:`), K2 (`GpuHangAbort:`, `ErrorDeviceLost` в логе или stdout эмулятора), `VALIDATION_STOP` — до строки входа: **W запускается**')
L.append('   (п. 316(в), вариант исполнителя RC2 принят лидом).')
L.append('')
L.append('Иначе — `RUN` (rc 1), W идёт по порядку: лога нет; лог 0 байт; sha лога ≠ строке `times.txt` (или строки нет); ключ-маркер; V вошёл; V не сделан.')
L.append('Каждая строка ответа при `NOT_ENTERED` V называет ключ V (`… outcome NOT_ENTERED key <ключ> (<источник>); …`), и строка `SKIPPED` несёт размер и')
L.append('sha лога; `go146a.sh` пишет строку ответа целиком в `skipped_<w>.txt` и в строку `times.txt` (п. 316(г)). Фикстуры: `test_sc146.py` F13 (ключ и')
L.append('свидетельство в строке), F13b (лога нет, чтение по логу — случай A опыта `rt146_skipfx`), F13c (лога нет, чтение по json), F13d (0 байт — случай B),')
L.append('F13e (0 байт и строка `times.txt` с sha пустого файла — член размера сам по себе), F13f (другой sha, по логу), F13g (лог изменён после')
L.append('`score.json`, по json), F13h (нет `times.txt`), F13i (ключ `attempt:no_stable` → `SKIPPED`), F13j (семь ключей-маркеров K1 / K2 / `VALIDATION_STOP`')
L.append('по логу и по json → `RUN`), F13k (опыт `rt146_skipfx` на синтетическом корне с копией `C:/kyty/s145/v145_02.json`: A и B → `RUN`); мутанты')
L.append('`--only` 22 из 22 убиты (`step1b/mut_only1b.txt`); повтор опыта A/B и случаи C/D — `step1b/skipfx1b.out.txt`.')
L.append('')
L.append('## 6. sha256 (`sc146.py --check-seal` перед каждым замком; шлюз `--start` читает строку эталона)')
L.append('')
for n in S.SEALED_NAMES:
    L.append('seal: %s %s' % (sha(n), n))
L.append('')
L.append('## 7. Не заявляется')
L.append('')
L.append('Что какая-либо сцена корректна или проходима до конца (`SCENE_OK` — окно удержания без ввода в точке `-lvl`); что Meta-уровни — сцены удержания;')
L.append('что 33 `SCENE_OK` `9235a7ac` держатся на `dac02fb9` до повторной проверки; что W без precache равен W с precache; что слой валидации сообщил бы')
L.append('любую ошибку; что детектор глитчей или правило плиток верны; что мутанты доказывают верность скорера, а не различающую силу фикстур; что')
L.append('положительное свидетельство ловит каждый отказ копии лога (только перечисленные в §5); что W, запущенный при маркере V, даст строку реестра (он может')
L.append('не дойти до той же точки); что инвентарь полон; 60 FPS; что (B) ускоряет игру.')
L.append('')
txt = '\n'.join(L)
dst = ROOT + '/pred/02_sc146.md'
assert not os.path.exists(dst), 'pred/02_sc146.md exists - a seal is not rewritten'
open(dst, 'wb').write(txt.encode('utf-8'))
print('pred/02_sc146.md written %s sha256 %s; %d call lines, %d seal lines' % (
    utc, sha('pred/02_sc146.md'), sum(1 for x in L if x.startswith('go146a call: ')), sum(1 for x in L if x.startswith('seal: '))))
