"""ROADMAP: session 115 item 9 (F2 measured offline; the input for the next speed track), written before acting."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   подготовка с удержанием 10 с). Дальше: вердикт v4 (воркфлоу идёт), долги F2, трек скорости, аудит сессии.
"""
NEW = ANCHOR + """9. **Долги F2 — замер офлайн по `vid115` (3 584 кадра сцены; записано до решения):** поток презентации держит
   `VideoOutConfig::mutex` **2,43 мс на флип** (медиана; p90 4,21, p99 5,76, максимум 12,94 мс), GuestGpu в
   `ReserveFlipRequest` **ни разу не ждал** (`flip_rsv_wait_n` 0 на всех строках), строк `FlipHold` (> 50 мс) нет; стена
   `UpdateTitle` 31 мкс на вызов, возраст задач главного потока 88 мкс. **Решение:** F2 не трек скорости — цены в этой
   сцене нет; остаётся долгом корректности §7 (долгий `Present` под мьютексом задержал бы гостя; фиксы (b)/(c) — только
   если счётчики покажут ожидание). **Вход для следующего трека скорости** (тот же лог, запись видео включена, поэтому
   уровни только внутри прогона): `cpu_gpu_us` 34,3 мс при `dt` 35,4 мс — кадр упирается в CPU потока GuestGpu; 5 266 draw
   + 268 dispatch на кадр ⇒ ≈ 6,3 мкс CPU на операцию; `fault_us` 15,3 мс на кадр суммарно по потокам гостя при 1 240
   фолтах (на GuestGpu 21 и 0,13 мс — не на критическом пути). Выбор трека — по правилу §2/§5 в сессии 116 с разбивкой
   фаз (`mutsite`/`pathlap`) на свежей сборке; в этой сессии не начинается.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
