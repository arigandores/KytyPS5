"""ROADMAP: session 117 item 9 (smoke result; the one spine fix), written before the fix."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   или менять следствия. Если дым чист — печать и запечатанный прогон на этой сборке.
"""
NEW = ANCHOR + """9. **Дым `smoke117` (сборка `af50e1b4`, `e8404d9`; числа не цитируются): инструмент работает** — 3 680 кадров со
   спайном, ни одного маркера сбоя, строка `Spine: mode=2 snap=4096 ctx=2672 ucfg=148 sh=1208`, счётчики живы,
   `spine_abort` 0, `spine_misal` 0; но ~24 `spine_bad` на кадр, все в части `sh` на `DISPATCH_DIRECT` (0x15), по 7 на
   подачу. **Причина — дефект спайна против настоящего процессора:** `CommandProcessor::DispatchDirect` (и через него
   `DispatchIndirect`) пишет в состояние `m_sh_ctx.SetCsWaveSize(ComputeWaveSize(mode))` при исполнении элемента, а
   спайн побочные эффекты элементов не повторял (draw-пакеты меняют только `m_num_instances`, он исключён по проекту).
   **Исправление (до правки):** после снимка dispatch-элемента спайн делает то же `SetCsWaveSize(ComputeWaveSize(mode))`,
   `mode` = последнее слово пакета (`DISPATCH_DIRECT` len 5, `DISPATCH_INDIRECT` len 3/4 — как в обработчиках). Новая
   сборка, повтор дыма; печать — на ней.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
