"""ROADMAP: session 117 item 5 (spine verify by member-wise equality, not a padding-cleared digest), before the code."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `obs116`. Ничего не отгружается.
"""
NEW = ANCHOR + """5. **Поправка п. 4 до сборки (записано до правки):** clang-cl 19.1.5 не знает `__builtin_clear_padding` (проверено
   компиляцией: `__has_builtin` = 0), а в регистровых структурах 127 `bool` — сырой дайджест дал бы ложные расхождения по
   паддингу (локальные структуры обработчиков несут мусор стека, у спайна и у настоящего процессора — разный). **Решение:**
   режим 2 хранит полный снимок (`HW::Context`, `HW::UserConfig`, `HW::Shader` и восемь регистров процессора) на каждый
   элемент в самом теневом процессоре, а настоящий сравнивает: `memcmp` частей, при различии байт — поштучное равенство
   `operator== = default`, добавленное всем 61 типу `graphics/guest_gpu/hardwareContext.h` (заголовок НЕ входит в
   подпись кэша трансляции: там только `graphics/shader/**`, `shaderTranslationCache.cpp`, `gpu_format.h`,
   `gpu_defs.h` — `src/generate_version.cmake`); различие только в паддинге — новый счётчик `spine_pad` (не
   расхождение), поштучное неравенство — `spine_bad`. Снимок принадлежит плану с номером; сверка с чужим планом (вторая
   подача того же процессора, начатая до конца первой) — `spine_misal`. `spine_dig_ns` → `spine_chk_ns` (снимки и
   сверки). Оговорка: `float`-поля с NaN дадут `spine_bad` при поштучном равенстве — строки `SpineMismatch:` называют
   часть. Правила вердикта и следствия п. 4 — без изменений.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
