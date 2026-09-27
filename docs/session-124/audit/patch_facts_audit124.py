# -*- coding: utf-8 -*-
"""Append the audit section (step 9, HPP-64) to C:/kyty/s124/FACTS.md once; LF, write_bytes."""
from pathlib import Path

P = Path('C:/kyty/s124/FACTS.md')
MARK = '## Step 9 — audit'
SEC = '''
## Step 9 — audit (HPP-64; author: Session Auditor; not yet accepted by the lead)

`C:/kyty/s124/audit124/AUDIT124.md` (git `docs/session-124/audit/`). Игру аудитор не запускал; замка во время аудита не было.
* **Пересчёт CONFIRMED** своим парсером (`recount124.py`, общего кода с `cen124.py`/`smk124.py`/`ref124.py`/`skc123.py` нет):
  окно 290..6910 (6 621 строка, 73 блока), τ_ctx 18,612 / τ⁺ 18,716 нс, `f_n^L` 0,00386, `f_x^{L+}` = `f_t^L(3τ⁺)` 0,01086,
  W₀⁺ 32 609,202045 (из лога `sky123`), q⁺ 0,5000, **U = 177,06 мкс < 500 → FRAME_SKIP_CLOSED_BY_CENSUS**, режим BDA OLD
  (73/73 блоков). Все стражи, которые аудит повторил (T1, И7′, G5, P1/P2/P4, G8, G10, G2), совпадают.
* **Чувствительность (ряды):** U = 500 потребовал бы τ_true ≥ 104,2 нс (5,6 τ_ctx; E ≤ ≈ 85 нс при E [I] 2–6); U только по
  числу draw ≈ 63; половины окна `f_t^L(3τ⁺)` 0,01104 / 0,01067; самый тяжёлый блок из 73 → U ≈ 261.
* **1 MAJOR / 2 MINOR, вердикт не меняется.** MAJOR-1: окно множителя W₀⁺ в печати и `ref124.py` — 10..87, а п. 50(в)
  требует «позиции 10–88» (п. 54 подписал число 10..87 как «10–88»); на 10..88 W₀⁺ 32 600,7, U 177,01. MINOR-1: второй полный
  `mutlib` разрешён п. 54(а) после обоих прогонов. MINOR-2: «Step 8» цитирует p50 τ̂ у стража G10, а страж — max τ̂ = 460,49 нс
  (46 % предела; в дыме 6а было 205).
* **Замок (п. 25(ж)):** в 17:33:08Z–17:39:24Z нет ни одного события платформы; живой ран один — Harness Engineer `fc78945a`;
  ран лида кончился в 17:31:15Z.
* **НЕ доказано:** выигрыш/ускорение/прогноз; удержание флипа (U_p⁺ 790,7 > 500 — не закрыто); A3 (E), A4, A5; отсутствие
  лишних рёбер (RC6); независимая часть P2 лишь 0,24 %; режим NEW; другие сцены; картинка.
'''

text = P.read_bytes().decode('utf-8')
assert MARK not in text, 'already patched'
text = text.rstrip('\n') + '\n' + SEC
P.write_bytes(text.encode('utf-8'))
print('appended', len(SEC), 'chars')
