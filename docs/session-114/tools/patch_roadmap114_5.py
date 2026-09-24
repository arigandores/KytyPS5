"""ROADMAP: session 114 item 5 (the design of seals 01 and 02), written before they are drafted."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   умолчанием 1 покрывает загрузку). Новая сборка; печати 01/02 готовятся на ней.
"""
NEW = ANCHOR + """5. **Сборка правок разбора — `916f6489…` (`74e2ad7`); устройство печатей (записано до черновиков; обе готовятся и
   запечатываются, НЕ запускаются до разрешения, п. 3):** **01 `ctl114`** (контроль): два входа Sky Garden по 180 с, пин,
   `KYTY_MAIN_STALL_TEST=3000:3000`, ручка файлом гейтов (`gates_title0.txt` / `gates_title1.txt` = `gates_base.txt` +
   ` titleasync=0|1`), теги `ctl114a` (0) и `ctl114b` (1); строка рывка — первая `FrameTrace: n=` после `MainStallTest:
   queued`, окно — эта строка и две следующие. PASS, если оба входа допущены, в `ctl114a` max `dt_us` окна ≥ 2 500 000
   (заморозка) и есть `MainThreadWait: us=` ≥ 2 500 000, а в `ctl114b` max `dt_us` окна ≤ 500 000, `GpuWaitSlow` нет и
   есть `MainTaskLate: us=` ≥ 2 500 000 (главный поток действительно спал); иначе FAIL; `GpuWaitSlow` в `ctl114a`
   допустим (ожидаем), прочие маркеры — недопуск. **02 `ttl114`** (ABBA): плечи `dawalk=1 dawalklead=1 titleasync=0|1`,
   600 с, пин, главный оценщик — кадры 10–89; скорер — из запечатанного `shn113` генератором (якоря — целые строки)
   руками агентов по этому тексту: окружение без сдвига порога GC; схема + `pres_title_*`, `flip_rsv_wait_*`,
   `flip_hold_*`, `mt_age_ns`/`mt_n`; вооружение BDA (`REGIME_OLD_ARM0`, `NARROW_*`, `NO_CHECK`, `NO_XTHR`) заменяется на
   `TITLE_COUNTED` (уровень `pres_title_n` ≥ 1 в обоих плечах) и `TITLE_ARMED` (стена на вызов у плеча 1 ≤ 20 000 нс и
   меньше, чем у плеча 0); `DEFAULTS_ON`, `INSTRUMENTS_DARK`, проверки обхода — как были. **Правило:** SHIP
   `titleasync=1` (умолчание 1 в следующей сборке), если допущен, контроль 01 PASS, **S1** Δ`dt` (1 − 0) ≤ **+50** мкс,
   **S2** Δ`dt` + 2·SE ≤ **+200** мкс (страж от шумного прогона, скрывающего замедление; дополнение к п. 2, записано здесь
   до печати) и видео `vtt114` (`gates_title1.txt`, пин, ≥ 3 000 кадров, 0 глитчей) PASS; иначе KEEP 0. Предсказания
   (не решают): P1 стена на вызов у плеча 0 в [20, 5 000] мкс; P2 у плеча 1 ≤ 20 мкс; P3 Δ`dt` в [−500, +100]; P4 Δ`dt` ≤ 0;
   P5 Δ`gpu_busy` в [−150, +150]; P6 Δ`flip_rsv_wait_ns` ≤ 0; P7 Δ`da_miss` в [−40, +40]. Мутанты — `mutlib` v2 (замороженная
   копия `docs/session-113/mutlib/v2/mutlib.py`, пока v3 не принят), `--control --no-memo`.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
