"""ROADMAP: session 117 item 10 (second smoke; the R_DISPATCH_RESET fix), written before the fix."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   сборка, повтор дыма; печать — на ней.
"""
NEW = ANCHOR + """10. **Дым `smoke117b` (сборка `175936c8`, `fbcfd49`; числа не цитируются):** ~20 `spine_bad` на кадр остались, та же
   подпись (`sh`, `DISPATCH_DIRECT`, по 7 на подачу) — но с элемента 0, то есть состояние расходилось ДО первого
   dispatch. **Причина — второй дефект спайна:** пользовательский пакет `R_DISPATCH_RESET` (`IT_NOP`, `CpOpDispatchReset`)
   вызывает `cp.Reset()` — сброс `m_sh_ctx`, `m_ucfg`, `m_ctx`, `m_saved_ctx`, индексных регистров, маркера и const RAM;
   спайн из пользовательских пакетов применял только `R_CONTEXT_STATE`. Остальные пользовательские пакети
   (`R_ACQUIRE_MEM`, `R_RELEASE_MEM`, `R_FLIP`, `R_WAIT_FLIP_DONE`, `R_PUSH_MARKER`, `R_POP_MARKER`) регистров не трогают
   (прочитано). **Исправление (до правки):** спайн применяет и `R_DISPATCH_RESET` настоящим обработчиком на теневом
   процессоре. Новая сборка, третий дым; если он чист — печать.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
