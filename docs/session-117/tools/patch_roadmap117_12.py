"""ROADMAP: session 117 item 12 (seal 01 re-issued before any run: line endings), written before the re-seal."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `graphicsRun.cpp`) и что `m_num_instances` и const RAM вне сверки.
"""
NEW = ANCHOR + """12. **Печать 01 `spn117` перевыпущена до любого прогона (записано до перевыпуска):** первая печать (`17baed5`) — 101
   фикстура, 104/104 черновых мутанта; `mutlib` v4.1 на запечатанной копии ОТКАЗАЛ до запуска («anchor found 0 times» у
   многострочного якоря `arms_none`): мои скрипты правок п. 11 писали `spn117.py`, `test_spn117.py`, `mut_spn117.py` и
   `pred/01_spn117.md` через `Path.write_text`, то есть с окончаниями CRLF на Windows, а `mutlib` сверяет якоря с сырыми
   байтами (черновой цикл читал через `read_text` и не видел разницы). **Решение:** эти четыре файла приводятся к LF
   (содержимое по строкам то же), фикстуры и черновые мутанты перегоняются, печать 01 выпускается заново с новыми
   хэшами в `SEALS117.txt` (строки первой печати остаются в файле с пометкой «superseded, never run»), мутанты — снова
   `mutlib` v4.1. Урок в правила харнесса: скрипты правок пишут `write_bytes` / `newline='\\n'`.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
