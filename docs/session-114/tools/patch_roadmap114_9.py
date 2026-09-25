"""ROADMAP: session 114 item 9 (the seal-02b verdict: SHIP; the default flip and its video/boot checks), written first."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   планку и P2, `--only` на них), мутанты на запечатанной копии — мной; тег `ttl114b` (уже принимается `TAG_RE`).
"""
NEW = ANCHOR + """9. **Итог печати 02b `ttl114b` — SHIP `titleasync=1` (записано до правки умолчания):** мутанты запечатанной копии 345/345;
   машина CPU ≈ 5 %, GPU 0 %. Прогон допущен (96 пар, режим BDA NEW, `bda_scan` 50,5 / 50,6); стена `UpdateTitle` на вызов
   172 556 / 22 234 нс (плечо 1 ниже планки 60 000); **Δ`dt` = −43,5 ± 73,2 мкс** (2·SE, t −1,19; вторичное окно −35,0 ±
   139,1), Δ`cpu_net` −33,4 ± 61,7, Δ`gpu_busy` +9,5 ± 21,1; S1 (≤ +50) и S2 (−43,5 + 73,2 = +29,7 ≤ +200) выполнены;
   контроль 01 PASS; видео `vtt114b` PASS (3 921 кадр, 0 глитчей); все семь предсказаний HIT. Размер не отличим от нуля
   (правка корректности, не скорости). **Решение:** (1) умолчание `titleasync` = **1** (`KYTY_TITLE_ASYNC`, таблица ручек),
   новая сборка; (2) её видео `vid114` (120 с, пин, `gates_base.txt`) и проверочный скрипт `check114.py` из `check113.py`
   генератором (новое: `titleasync` нет в тексте гейтов; стена `UpdateTitle` на вызов по сцене ≤ 60 мкс — умолчание
   действует; счётчики `pres_title_*`); (3) **загрузка с холодным кешем пайплайнов драйвера** — вход `boot114`
   (`KYTY_PIPELINE_CACHE=0`, 120 с, пин): длинная фаза `WindowPrepareShaders` (главный поток презентует сам) при
   умолчании 1 — проверка фикса C1 (п. 4): прогон допущен (без маркеров смерти/зависания/потери устройства), в логе есть
   `ShaderPreparation: startup wait finished in <N> ms` с N ≥ 2 000 и прогресс подготовки; (4) при FAIL любого из двух —
   умолчание откатывается к 0, сборка `916f6489` остаётся. Всё в SEALS до прогона; цепочка `go114d.sh`.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
