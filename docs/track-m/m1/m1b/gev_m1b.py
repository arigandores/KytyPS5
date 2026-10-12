# M1b: type of evidence behind each class-G theme (row-level regex on the M1a "довод" field), then per theme the WEAKEST row.
# Evidence kinds (strongest first):
#   OOS   - out of scope by rule p.752(v): launcher/CI/build/docs/non-Windows/tests-only/log-only/pure refactor/net-revert pair
#   OPC   - opcode absent in all 5 698 eboot programs (ophist) or only in programs the game never requests
#   NID   - function NID not imported / no dynamic load / not registered (static imports [c])
#   DEF   - default-off option or config the game/env does not hit, answer same [c]
#   SEEN  - only "not seen on visited scenes": 59 entered levels / 40 SCENE_OK / 281 entries / F48a sweep / W 40 scenes / T1 corpus
#   UNK   - applicability not shown: "не доказан", "не измерено", "[U]"
# Usage: python gev_m1b.py [themes]   -> per-theme table to stdout
import csv, re, sys, collections
D = 'docs/track-m/m1/'
with open(D + 'upstream_detail.tsv', encoding='utf-8', newline='') as f:
    rows = [r for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE) if r['класс'] == 'Г']
P = [
    ('UNK', r'не доказан|не измерено|\[U\]|влияние \[U\]|применимость к игре \[U\]'),
    ('SEEN', r'59 входивших|40 SCENE_OK|40 сцен|281 вход|свипе F48a|корпус T1|линии курса|на пройденных|V FS15|log_fs15|112 логов|4 357 stdout|560 из 562|pipelines\.bin|40 последних логах|в реестре трека F строки нет|в реестре нет|K1 с этой сигнатурой'),
    ('NID', r'не импортир|NID .* нет|нет динамической|не грузит модули|не регистрирует|не создаёт|колбэк задан|не вызывает|AIO игра'),
    ('OPC', r'игра не исполняет|опкода нет|в игре 0|= ?0 \[c|0 инструкций|SWAPPC в eboot нет|SWAPPC нет|игрой не исполняется|FP64-опкодов в eboot 0|опкоды в eboot 0|row_share 0|dmask 1|FLAT игры|режим 6 игра не задаёт|не используется \[c\]|PQ-формат не используется|metadata 0, dcc 0'),
    ('DEF', r'при умолчании|умолчание off|не включается в нашей конфигурации|только при Config|не-ASCII|ответ на нашем пути не меняется|совпадает с нашей|ответ для ASTRO тот же|Zen 5'),
    ('OOS', r'лаунчер|Лаунчер|не меняет эмулятор|Linux|macOS|платформа|только тест|только журнал|только печать|только сборк|сборочная|компиляц|рефакторинг|Рефакторинг|поведение не меняется|0 изменений|ничего не меняет|профайлер|Бренд|GUI|хоста|удобство|Удобство|тест инфраструктуры|харнесс тестов|мёртвый код|ожидание кода|следует за|исправление сборки|покрытие|применим|не нужен|ответы эмулятора не меняются|ответ эмулятора тот же|Диагностика'),
]
ORDER = {k: i for i, (k, _) in enumerate(P)}  # lower index = weaker
def kind(text):
    for k, rx in P:
        if re.search(rx, text):
            return k
    return 'NONE'
th = collections.OrderedDict()
for r in rows:
    k = kind(r['довод_ASTRO'] + ' ' + r['суть'])
    th.setdefault(r['тема'], []).append((k, r))
summ = collections.Counter()
out = []
for t, lst in th.items():
    weakest = min((k for k, _ in lst), key=lambda k: ORDER.get(k, -1))
    summ[weakest] += 1
    out.append((weakest, t, lst[0][1]['ключ'], len(lst), lst[0][1]['увер'], lst[0][1]['подпись']))
for w, t, key, n, u, s in sorted(out):
    print(f'{w}\t{t}\t{key}\tn={n}\tув={u}\tподп={s}')
print('themes', len(th), dict(summ), file=sys.stderr)
