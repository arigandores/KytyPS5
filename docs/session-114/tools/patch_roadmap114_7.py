"""ROADMAP: session 114 item 7 (the seal-01 verdict and the seal-02 plan), written before seal 02."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   запечатанной копии) → `go114b.sh` (ABBA 600 с + видео) → возобновление приёмки `mutlib` v3 → закрытие сессии 114.
"""
NEW = ANCHOR + """7. **Итог печати 01 `ctl114` — PASS (записано до печати 02):** машина перед цепочкой: CPU 4–5 %, GPU 0 %.
   `ctl114a` (`titleasync=0`): окно рывка `dt` 3 034 886 мкс, `MainThreadWait: us=3001826 frame=3000`, один `GpuWaitSlow:
   role=4 requested=96303 known=96302 current=96303 … submit_backlog=0 record_backlog=0` — **та же подпись, что у события
   `vbn113k` с. 113**, `PriorityStall: tick=96303 unsub=1 us=2975859` (у `vbn113k` ожидание 2,975 с), место — `sync.cpp`
   (прерывание EOP, по карте компоновщика), `FlipHold: us=3003371 present_us=3002829` (весь рывок — внутри `Present`).
   `ctl114b` (`titleasync=1`): окно `dt` 33,4 / 33,2 / 33,2 мс, `GpuWaitSlow` нет, `MainTaskLate: us=3000429` (главный поток
   спал те же 3 с). Вывод: ручка разрывает цепочку «занятый главный поток → заморозка эмуляции»; подпись события с. 113
   воспроизведена цепочкой через заголовок окна — но что заняло главный поток в `vbn113k`, не наблюдалось (не
   утверждать). **Печать 02 `ttl114`:** черновик (`C:/kyty/s114/ttl114_draft/`, генератор `make_ttl114.py`, 249 фикстур,
   мутанты черновика 344/344, проверка скептика PASS; MINOR-1 — скорер не читает условие «контроль 01 PASS» ⇒ оно
   закрепляется текстом печати: SHIP засчитывается только при PASS `ctl114`, который уже получен); мутанты на
   запечатанной копии — без двух черновых (производный файл, как п. 20 с. 113). Затем `go114b.sh`: `ttl114` (600 с) → при
   SHIP_PENDING_VIDEO видео `vtt114` (`gates_title1.txt`, 120 с) и повторный скоринг.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
