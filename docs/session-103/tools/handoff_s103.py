P = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/HANDOFF.md'
raw = open(P, 'rb').read()
crlf = b'\r\n' in raw
b = raw.decode('utf-8').replace('\r\n', '\n')
head = '# HANDOFF — ASTRO BOT на KytyPS5\n\n'
assert b.startswith(head)
block = '''Дата: 2026-09-23. **Сессия 103 (кратко; источник истины — `C:/kyty/s103/FACTS.md`, план — ROADMAP §0.1 и
`docs/next-session-104.md`).** Ограничитель циклов BVH `KYTY_BVH_LOOP_CAP` включён по умолчанию (65 536 шагов,
шейдер `380bb9d636390bae`): 0 зависонов входа в Sky Garden из 67, срабатывания в 7 входах, серия по печати НЕ
ПРИНЯТА (A3). M5′ (`KYTY_BDA_LEAN`): X′ = 1,2934 (верхняя граница) ⇒ G ЗАКРЫТ; маршрут E исчерпан, 60 FPS больше
не направление работ; следующий маршрут — V (плато вблэнка: флип выходит только на тике эмулируемого вблэнка).
15 проверок «наличия» в трансляторе читают значение. Бинарь `16ef56b6…`, хэш транслятора `699c1e4b…`, seed
шейдеров устарел. Ускорения нет.

'''
b = head + block + b[len(head):]
out = b.replace('\n', '\r\n') if crlf else b
open(P, 'wb').write(out.encode('utf-8'))
print('ok', crlf)
