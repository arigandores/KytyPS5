"""ROADMAP: session 116 item 4 (drop the id_emit_med check before sealing), written before the change."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `semwait_gpu_us`, `prio_us`. Правит агент-автор черновика; затем фикстуры, мутанты черновика, печать.
"""
NEW = ANCHOR + """4. **Поправка п. 3 до печати (записано до правки):** проверка «медиана разности `pl_em_n − mh_draws` по строкам = 0»
   (`id_emit_med`) убирается: на `pl96a` разность < 0 в 42,3 % строк, = 0 в 8,8 %, > 0 в 48,9 % — ресэмплинг даёт 3,9 % (6 000
   строк) и 1,7 % (8 500) случайного отказа исправного прогона, а при чуть более скошенном перекосе на этой сборке — отказ
   всегда; при этом она **избыточна**: допуск суммы 256 на ≥ 6 000 строк уже ловит систематический сдвиг от 0,043 на
   строку. Остаётся только тождество по сумме (256) и удержаний (16). Правит агент-автор; фикстуры, мутанты, печать.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
