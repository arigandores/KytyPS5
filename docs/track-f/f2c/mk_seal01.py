# F2c (HPP-310): writes pred/01_f2c.md - the seal of the F2c series (ROADMAP p.237(g)(5), p.254(e), p.256).  The text of p.256
# is copied verbatim from git (KytyPS5 b1703ae6:docs/ROADMAP.md, from the line "256. " to the line before the next blank-line
# paragraph), every sealed file gets one 'seal: <sha256> <name>' line.  UTF-8, LF.
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/f287/f2c'
sys.path.insert(0, HERE)
import f2c_read as R  # noqa: E402

GIT = 'C:/Program Files/Git/cmd/git.exe'
COMMIT = 'b1703ae6'
when = sys.argv[1]
road = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', '%s:docs/ROADMAP.md' % COMMIT], capture_output=True,
                      check=True).stdout.decode('utf-8').split('\n')
i0 = next(i for i, l in enumerate(road) if l.startswith('256. **'))
i1 = next(i for i in range(i0, len(road)) if road[i].strip() == '')
p256 = road[i0:i1]
assert any(l.lstrip().startswith('(ж)') for l in p256) and road[i1 + 1].startswith('**'), road[i1 + 1][:20]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def path(n):
    return n if n.startswith('C:/') else os.path.join(HERE, n)


L = []
A = L.append
A('# Печать 01 звена F2c трека F — доказательные прогоны Б26б (`pred/01_f2c.md`)')
A('')
A('Звено F2c (`HPP-310`, Harness Engineer). Записана %s (UTC по `date -u`) ДО первого прогона серии F2c. Основание — `ROADMAP.md`' % when)
A('«СЕССИЯ 122» п. 237(г)(4)–(6), п. 237(в)(2) (`57729aed`), п. 254(е) (`d3a8d951`), **п. 256** (`%s:docs/ROADMAP.md:%d`, якорь' % (COMMIT, i0 + 1))
A('«256. **Звено F2c трека F (`HPP-310`): ответы лида на В1–В5», контроль +1 — %d «пятого хэша по механизму и pc»); отзыв F2b' % (i0 + 2))
A('`docs/track-f/f2b/f2b-review.md` RC1–RC4, RC6. Пункты после п. 256 к моменту печати: нет (перечитано перед печатью). Без мутантов и без')
A('отзыва (п. 256(е)). После печати скорер `f2c_read.py`, `f2c_b26.py`, харнесс `go_f2c.sh`, `win332_f2c.py`, `shalist_f2c.py`, наборы')
A('фикстур и все файлы §5 не меняются: `go_f2c.sh` проверяет каждую строку `seal:` вызовом `f2c_read.py --check-seal` перед замком;')
A('`<tag>.json` каждого прогона несёт sha256 этой печати (`--pred`).')
A('')
A('## 1. Константы п. 256 — дословно (`%s:docs/ROADMAP.md:%d`–%d)' % (COMMIT, i0 + 1, i1))
A('')
for l in p256:
    A('> ' + l.strip())
A('')
A('## 2. Что прогоняется (п. 237(г)(5), п. 256(б), (д), (е))')
A('')
A('Бинарь правки — `C:/kyty/f287/bin/kyty_emulator_5821482a.exe`, sha256 `5821482a13a38bb9e42719b75fbd7b6e308a08c8e98caab02afb5398aac368dd`')
A('(п. 256(б)); ставится ОДИН раз внутри замка на всю серию; в ловушке выхода — возврат `C:/kyty/s128/kyty_emulator_9235a7ac.exe`')
A('(sha256 `9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7`, проверка sha). Уровень `underwater_aerial_garden`, `-lvl`')
A('(`KYTY_GUEST_ARGS`), файл гейтов пустой, позиционно `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`, `KYTY_GPU_CHECKPOINTS` не передаётся;')
A('`--attempts 1` (неудача — данные, повтора нет), `--stable-draws 300`, `--require-idle`. Порядок — ровно этот:')
A('')
A('| тег | плечо | окружение | удержание стены (п. 256(д)) | мера удержания |')
A('|---|---|---|---|---|')
A('| `f2c_a` | (а) V | `KYTY_FIX_B26=1`, видео `KYTY_REC`, без валидации | 330 с, `--timeout 480` | сумма `dt_us` после первого кадра сцены ≥ 300 с |')
A('| `f2c_b` | (б) W | `KYTY_FIX_B26=1`, `--vulkan-validation true`, `KYTY_PIPELINE_PRECACHE=0` (форма п. 254(е)), `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin`, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000`, без видео | 310 с, `--timeout 600` | сумма `dt_us` после первого кадра сцены ≥ 300 с (буква `hold_s` json — рядом) |')
A('| `f2c_c` | (в) контроль | `KYTY_FIX_B26=0`, без валидации, без видео | 120 с, `--timeout 480` | `hold_s` json ≥ 120 и сумма `dt_us` после строки входа ≥ 120 (буква); после первого кадра сцены ≥ 120 (вариант) |')
A('')
A('Остановка серии: маркер смерти или rc `enter_scene.py` ≠ 0 — следующие теги не запускаются, вопрос лиду. Стоп-файл `C:/kyty/f287/STOP`')
A('— до всего, перед замком и перед каждым тегом. Окно замка (п. 256(е)) — в той же команде, что замок, сразу перед ним: файла замка нет,')
A('стоп-файла нет, `HPP-332` не `in_progress` и не `done` по ответу API (`win332_f2c.py`, строка `times.txt` с ответом); иначе BUSY rc 4.')
A('Начатая серия не прерывается.')
A('')
A('**Кэши (п. 228(в), п. 256(в)).** Внутри замка до установки: список содержимого `_ShaderCache/PPSA21564` (корень, `variant_fixb26`,')
A('`pipelines.bin`) и его копия — списки равны (строка `times.txt`); манифест `cachemf143.py`; список и копия `GLCache`')
A('(`%LOCALAPPDATA%/NVIDIA/GLCache`). После серии в ловушке выхода: кэш прогона ПЕРЕНОСИТСЯ в `cache_run/<UTC>/` (сохраняется), копия')
A('возвращается, список обязан совпасть со списком до серии; `GLRESTORE=1` — `GLCache` прогона переносится в `glcache_run/<UTC>/`, копия')
A('возвращается, список обязан совпасть. Несовпадение любого возврата — rc 1 и стоп-файл `C:/kyty/f287/STOP` (стоп треку F), затем')
A('комментарий в `HPP-330` до старта `HPP-332` (п. 256(в)).')
A('')
A('## 3. Правило чтения (п. 237(г)(4)–(5), п. 256(а), (б), (г), (д))')
A('')
A('Чтение — `f2c_read.py --tag <tag>` (импорт `C:/kyty/s142/sc142.py` после проверки sha256 `%s` без правки —' % R.SC142_SHA)
A('п. 256(г); профиль Б26 — `f2c_b26.py`, sha256 проверяется так же). **Вердикт записи — строка `F2C VERDICT <tag> RC1/executor variant')
A('(rule of p.256(a),(d) - verdict of record)`; строка `F2C VERDICT <tag> letter` печатается рядом (п. 256(а)).**')
A('')
A('- Допуск (иначе `NOT ADMITTED`): одна попытка; `-lvl underwater_aerial_garden`; `KYTY_FIX_B26` ровно `1`/`1`/`0` (RC6);')
A('  `KYTY_GPU_CLOCK_PIN=1`; нет `KYTY_GPU_CHECKPOINTS`; `KYTY_PIPELINE_PRECACHE=0` только у `f2c_b`, у остальных не задана; видео только у')
A('  `f2c_a`; `--vulkan-validation true` только у `f2c_b`, активность валидации по трём признакам п. 224 (0 «нет слоя», ≥ 1')
A('  `validation_features`, ≥ 1 `[Vulkan][`).')
A('- Ручка (RC3(4)): строка `Shader translation cache:` — `variant_fixb26` при `=1`, корень при `=0`, иначе `INVALID RUN`. Форма')
A('  п. 254(е): в W 0 строк `PipelinePrecache: N recipes -> `, в V ≥ 1, иначе `FAIL (form p.254(e))`.')
A('- (а) `f2c_a`: 0 строк `opcode is not implemented` с SOP1 `0x0c` и VOPC `0xe3`; SOP1 `0x21` — ровно 96; **положительный счёт по')
A('  п. 256(а): хэш засчитан, если у него ровно одна строка `CsPretranslate: ready|skipped` и это `ready`, либо `skipped` с причиной не')
A('  SOP1 `0x0c` / не VOPC `0xe3` и pc отказа больше первого места правки (`57c4…` — `0x168`; четыре VOPC — первое `0xe3` по')
A('  `C:/kyty/f287/f1a/b26_shaders.tsv`); 5 из 5**; 0 маркеров смерти (`sc142.markers`); вход, нет смены сцены; видео ≥ 3 000 кадров,')
A('  `s51_vidglitch.py 4 6` 0 глитчей, лист `sheet_f2c_a.png` (смотрит лид); переоткрытия Б26а 0. Окно входа (600 кадров после первого')
A('  кадра сцены) не считается. Каждый кадр ≥ 100 мс на удержании — интервал (байты лога от предыдущей строки `FrameTrace` до строки')
A('  кадра) и число строк с одним из 5 хэшей в нём; правке приписывается кадр только с такой строкой, остальные — информация против `v142`')
A('  (п. 256(б)(1)), не вердикт.')
A('- (б) `f2c_b`: 0 `[Vulkan][E]` (лог и stdout) при активной валидации; ручка; форма п. 254(е); 0 маркеров смерти; переоткрытия 0.')
A('  Профиль и число строк `CsPretranslate` в W — данные (без стартового precache проверка `known` срабатывает реже).')
A('- (в) `f2c_c`: профиль `CONTROL RETURNS` — SOP1 `0x21` 96, SOP1 `0x0c` 1, VOPC `0xe3` 4, VOPC `0xf3` 0, иных опкодов нет; ручка')
A('  (корень); 0 маркеров смерти; переоткрытия 0.')
A('- (г) в каждом логе — проверка переоткрытия Б26а (п. 237(в)(2)): `CsPretranslate: miss|hit` с хэшем из 96, `shader CFG build failed`')
A('  вне `CsPretranslate:`, смерть из транслятора — число строк; любое ≠ 0 — `FAIL` плеча и строка FACTS.')
A('- **Удержание (п. 256(д)):** у (а) и (б) сумма `dt_us` показанных кадров после первого кадра сцены < 300 с при прочих выполненных —')
A('  `NOT EVALUABLE` (повтор — только строкой лида); при невыполненном ином критерии — `FAIL`.')
A('- Строки печати 22 ручек (п. 256(б)(3); 19 префиксов `f2c_read.py`: %s) — счёт в каждом логе, ожидание 0;' % ', '.join('`%s:`' % k for k in R.KNOB_NAMES))
A('  ненулевой счёт — строка FACTS, критерий не меняет, K3 удержания этого лога — «не разобрано».')
A('- Регрессионный вход п. 228(г)(5) серия F2c НЕ закрывает (п. 256(б)(2)).')
A('')
A('## 4. Строка вызова (п. 105(в))')
A('')
A('go_f2c call: PLWAIT=540 bash C:/kyty/f287/f2c/go_f2c.sh series')
A('')
A('Вызов — отсоединённо обёрткой (стена серии ≈ 25–35 мин больше 600 с команды инструмента), ожидание — передним планом по ≤ 560 с в том же')
A('хартбите; второй вызов при идущей серии запрещён (`attempt_<tag>.txt`).')
A('')
A('## 5. Печать файлов')
A('')
for n in R.SEALED:
    A('seal: %s %s' % (sha(path(n)), n))
A('')
A('Наборы (последний вывод): `test_f2c_read.py` — `test_f2c_read.out.txt` sha256 %s; `test_go_f2c.py` — `test_go_f2c.out.txt` sha256 %s;' % (
    sha(path('test_f2c_read.out.txt')), sha(path('test_go_f2c.out.txt'))))
A('`test_f2c_b26.py` — `test_f2c_b26.out.txt` sha256 %s; бинарь правки sha256 %s.' % (
    sha(path('test_f2c_b26.out.txt')), sha('C:/kyty/f287/bin/kyty_emulator_5821482a.exe')))
os.makedirs(os.path.join(HERE, 'pred'), exist_ok=True)
out = os.path.join(HERE, 'pred', '01_f2c.md')
assert not os.path.exists(out), 'seal exists'
with open(out, 'wb') as f:
    f.write(('\n'.join(L) + '\n').encode('utf-8'))
print('seal written', out, sha(out), 'p256 lines', len(p256))
