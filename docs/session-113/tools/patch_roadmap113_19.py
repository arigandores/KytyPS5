"""ROADMAP 0.1 "СЕССИЯ 113" item 19 (the 01f verdict and the re-pin of seal 02), written before any action on it."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   3 с важнее выигрыша `bdanarrow` (корректность и зависания — первыми). Долг §7: «ожидание неподанного тика».
"""
NEW = ANCHOR + """19. **Итог печати 01f — GO (записано до печати 02):** `vbn113m` допущен, принудительный OLD (`bda_scan` 1 064,
   `BufferGc: … shift_mb=1024`), Σ`bda_nwould` 11 845 121, **`bda_nmiss` 0, `bda_nxthr` 0**, `bda_nrace` 0, все семь
   предсказаний HIT; рывок не повторился (`prio_stall` 0, `gw_idle_prio` 0; `prio_unsub` 5,67 на кадр — ожидания на
   неподанном тике обычны и коротки). Режим 1 в принудительном OLD этой сцены не пропустил бы ни одной синхронизации.
   **Печать 02 — ABBA `bdanarrow=0|1` по п. 3 (600 с, пин, кадры 10–89, правило Δ`dt` ≤ −100 мкс и 2·SE < 0, допуск
   плечо 0 OLD и плечо 1 `bda_scan` ≤ 200, видео при S1–S2) с перепривязкой черновика `shn113` генератором
   `make_shn113b.py` (якоря — целые строки):** сборка `1678d3f4`; в ожидаемом окружении обоих плеч и видео
   `KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024` (принудительный OLD; `ENV_EXPECTED` сверяется фикстурой `CONSTANTS`, видео —
   проверкой `shifted`); схема строки `-x` + `bda_nrace`, `prio_unsub`, `prio_stall`, `gw_idle_prio`; метка размера «build
   1678d3f4, forced OLD (GC trigger −1024 MiB), main estimator»; порог `NARROW_ARMED_ARM1` (уровень `bda_nskip` плеча 1 ≥ 1
   — медиана средних по блокам) НЕ меняется: в принудительном OLD `bda_ginv_reg` — медиана 1, среднее 1,16–1,40 на кадр;
   строка `BufferGc:` в скорер не вводится — принуждение проверяют окружение и `REGIME_OLD_ARM0`. Цепочка `go113g.sh`:
   сверка установленной сборки, `shn113` (600 с), скоринг; при SHIP_PENDING_VIDEO — видео `vsn113` (120 с, пин, сдвиг,
   `gates_narrow1.txt`, `KYTY_REC`) + `s51_vidglitch.py` + повторный скоринг; при недопуске из-за `REGIME_OLD_ARM0` — один
   повтор `shn113b`. Мутанты — `mutlib` v2 `--control --no-memo` на запечатанной копии (п. 15). Размер подписывается
   «принудительный OLD»; вклад в скорость игры = размер × доля естественного OLD (не измерена).
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
