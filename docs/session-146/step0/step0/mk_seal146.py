"""mk_seal146.py - session 146 step 0 (HPP-386): writes C:/kyty/s146/pred/01_sc146.md, the seal of the series sc146, BEFORE the
first run of the series.  Every sha256 line is computed now from its file; the outputs quoted are named with their sha256.
After the seal sc146.py, go146a.sh, gate146.py, the wrappers and the suites do not change (a change is a new seal).  UTF-8, LF."""
import hashlib
import importlib.util
import os
import subprocess
import sys

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


utc = subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()
OUTS = ('step0/test_sc146.out.txt', 'step0/test_gate146.out.txt', 'step0/test_go146a.out.txt', 'step0/test_tools146.out.txt',
        'step0/test_fgcpu146.out.txt', 'step0/regress145.out.txt', 'step0/calib146.out.txt', 'step0/check1b146.out.txt',
        'step0/jsonsrc145.out.txt', 'step0/tilereg146_1.out.txt', 'step0/tilereg146_2.out.txt', 'step0/lvl146.out.txt',
        'mut_sc146.txt', 'step0/run1/mut_sc146.run1.txt', 'step0/mut_screen1.txt', 'step0/mut_screen2.txt',
        'step0/mut_screen3.txt', 'step0/test_i146.out.txt', 'step0/setup146.out.txt')
L = []
L.append('# Печать 01 серии `sc146` — шаг 0 с. 146 (`pred/01_sc146.md`)')
L.append('')
L.append('Шаг 0 с. 146 (`HPP-386`, Harness Engineer). Записана %s (UTC по `date -u`) ДО первого прогона серии `sc146`. Основание — `ROADMAP.md`' % utc)
L.append('«СЕССИЯ 122» **п. 309(к), (л)(1)–(7)** (цель с. 146 и константы), **п. 300(б)(2)–(4)** (установка, форма W на бинаре отгрузки), п. 281(г),')
L.append('п. 295, 273(к)(4), 221(г)(3), **п. 313** (приёмка установки, прогрева и списка 15 уровней), **п. 314** (зачётный прогон мутантов `--workers 16`);')
L.append('прочитаны пункты после выдачи звена: 310, 311 (P17 принят, новых прогонов нет), 312 (P18: звенья P19–P22 трека P — очередь замка сессия > P),')
L.append('313, 314. Печать установки и прогрева — `pred/00_i146.md` (`%s`).' % sha('pred/00_i146.md')[:16])
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
L.append('**W пары при `NOT_ENTERED` V не вызывается** (п. 309(к)(1)): `go146a.sh` спрашивает `sc146.py --skip-w <w>` (по `runs146/<v>.score.json`,')
L.append('иначе по логу V) до замка; ответ `SKIPPED_V_NOT_ENTERED` — файл `skipped_<w>.txt`, строка `times.txt`, rc 0, не попытка, порядок идёт дальше.')
L.append('')
L.append('## 2. Чтение (`sc146.py`, профиль 146) — правила `sc145.py` без изменения констант (п. 309(л)(4))')
L.append('')
L.append('- `SCENE_OK` уровня — по паре одной сессии на `dac02fb9` (`v146_NN`/`w146_NN`); пар с W `9235a7ac` нет; строки V/W, лист, sha листа и видео —')
L.append('  как `sc145` (п. 221(г)(3), 224(а)); слово `YES` — только с отметкой листа лидом.')
L.append('- Форма W на бинаре отгрузки: строка допуска «W form on the shipment binary: no KYTY_PIPELINE_PRECACHE in the env»; строки')
L.append('  `PipelinePrecache: N recipes ->` у W — строка данных. Форма п. 295(б)(1)–(4) — без изменений.')
L.append('- **`DualSrcBlend: supported=1 enabled=1` до первой `GuestOut`:** у контрольного `w146_00` — член буквы его остановки (п. 300(б)(4)); у каждого W —')
L.append('  строка данных (п. 309(л)(4)); рядом печатается вариант исполнителя по п. 281(г) («нет — тег FAIL») с пометкой [I], в вердикт не входит.')
L.append('- Строки данных (не гейт, п. 309(л)(4)): `stubs` (Ф13, строки `Unresolved import stub called`, лог и stdout), `asserts` (Ф14, `ASSERT:` и')
L.append('  `user_msg_param`; ≠ 0 — строка закрытия в реестр F), события по плиткам у каждого V (Д-4: правило аудитора AUDIT145 §1.4, плитки 4×4, порог 4,')
L.append('  `tiles146.py` → `tiles_<V>.txt` и тройки кадров `tiles_<V>.png` для листа лида).')
L.append('- `r146_01`…`r146_03`: строка «RECHECK <уровень>: PASSES / REMOVES SCENE_OK / PENDING_SHEET» по строкам V п. 221(г)(3), строке')
L.append('  «guest args / json level / sha лога = times.txt» и отметке листа; `r146_04`: строка «B40 SECOND HOLD» с кадрами K2 (данные для p Б40).')
L.append('- Sky Garden на `dac02fb9` (п. 300(д)): строка-справка — `WARMUP VERDICT` из `score_i146_v.txt` и исход контрольного W; слово `SCENE_OK` Sky')
L.append('  Garden этим скорером не печатается (решение — закрытие).')
L.append('- Остановки (п. 273(к)(4), 309(л)(5)): контрольный W остановлен (буква: маркер смерти, `[Vulkan][E]`, строки лимита слоя, нет строки')
L.append('  DualSrcBlend; чтение исполнителя [I] для шлюза — любая строка W); два W подряд остановлены до первой `GuestOut` одним ключом; **три V подряд**')
L.append('  `NOT_ENTERED` одним маркером — по всем сделанным V серии в порядке (`r146_*` и `v146_*`; вариант исполнителя: в с. 145 V были только')
L.append('  переписью); событие окна на сделанном теге прямо перед. `--stop-check` читает `runs146/<тег>.score.json`, если его sha лога = строке')
L.append('  `enter_scene end` `step2/times.txt`, иначе лог; источник — строкой `STOP CHECK SOURCES`.')
L.append('- Шлюз шага 2 `step2/gate146.py`: `--start` — эталон `runs146/cache_i146_v.after.json` (конец прогрева) по печати; кэш трансляции')
L.append('  (`PPSA21564` с каталогом `variant_fixb26_fixb1b`) отличается — STOP, кэши драйвера — данные; ≥ 60 GiB на C:; `--before <тег>` — члены (w), (b) (форма')
L.append('  W по env), (f), (v), (e), (l), (c)(2), (g) на сделанном теге прямо перед (пропущенный W проходится до V перед ним).')
L.append('')
L.append('## 3. Доказательства шага 0 (выводы — с sha256)')
L.append('')
for o in OUTS:
    p = os.path.join(ROOT, o)
    if os.path.isfile(p):
        L.append('- `%s` `%s`: %s' % (o, sha(o)[:16], tail(o)[0][:200].replace('|', '/')))
    else:
        L.append('- `%s`: ОТСУТСТВУЕТ' % o)
L.append('')
L.append('## 4. Вызовы (ровно одна строка на тег; другой `PLWAIT` — отказ rc 1)')
L.append('')
for t in S.SEQ:
    L.append('go146a call: PLWAIT=540 bash C:/kyty/s146/go146a.sh %s' % t)
L.append('')
L.append('## 5. sha256 (`sc146.py --check-seal` перед каждым замком; шлюз `--start` читает строку эталона)')
L.append('')
for n in S.SEALED_NAMES:
    L.append('seal: %s %s' % (sha(n), n))
L.append('')
L.append('## 6. Не заявляется')
L.append('')
L.append('Что какая-либо сцена корректна или проходима до конца (`SCENE_OK` — окно удержания без ввода в точке `-lvl`); что Meta-уровни — сцены удержания;')
L.append('что 33 `SCENE_OK` `9235a7ac` держатся на `dac02fb9` до повторной проверки; что W без precache равен W с precache; что слой валидации сообщил бы')
L.append('любую ошибку; что детектор глитчей или правило плиток верны; что мутанты доказывают верность скорера, а не различающую силу фикстур; что')
L.append('инвентарь полон; 60 FPS; что (B) ускоряет игру.')
L.append('')
txt = '\n'.join(L)
os.makedirs(ROOT + '/pred', exist_ok=True)
open(ROOT + '/pred/01_sc146.md', 'wb').write(txt.encode('utf-8'))
print('pred/01_sc146.md written %s sha256 %s; %d call lines, %d seal lines' % (
    utc, sha('pred/01_sc146.md'), sum(1 for x in L if x.startswith('go146a call: ')), sum(1 for x in L if x.startswith('seal: '))))
