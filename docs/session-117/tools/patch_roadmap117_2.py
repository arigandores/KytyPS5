"""ROADMAP: session 117 item 2 (lock-contention tracks closed; the user's question), written before acting."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   на кадр (п. 7 с. 116), арифметика потолка — в ROADMAP до кода.
"""
NEW = ANCHOR + """2. **Треки замков закрыты (вопрос пользователя «мб хватит mutex фиксить?»; записано до действий):** с. 106–112 сняли
   ожидание замков (`dabatch`, `cspfree`, `daslot`, `daguard`) по ≈ 0,2 мс (≈ +0,7 % скорости) каждый; `obs116` показал,
   что GuestGpu занят весь кадр (`gw_idle` 28 мкс), а 92,3 % «под render mutex» — это сама работа операций (bind/emit/
   prog), а не ожидание. **Новых треков вокруг захвата/ожидания замков (`m_mutex`, render mutex, мьютекс флипа) не
   открывать**, пока замер не покажет ожидание ≥ 1 мс на кадр; F2 остаётся долгом корректности. Для 60 FPS нужно
   −15 мс кадра (31,65 → 16,67), правками по 0,2 мс не достижимо. **Правило остановки:** если `fin117` не найдёт в
   `AheadTake`/`mh_bind`/`mh_emit` снимаемой части ≥ 1 мс, это записывается как исчерпание мелких правок потока GuestGpu
   на этой сцене, и с. 118 оценивает структурный шаг (второй исполнитель операций с упорядоченной записью — маршрут M4
   закрыт в с. 95 по своему правилу; или сокращение числа операций) по потолку, а не продолжает микроправки.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
