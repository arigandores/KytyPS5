# -*- coding: utf-8 -*-
"""Append the audit section (step 9, HPP-32) to C:/kyty/s123/FACTS.md once; LF, write_bytes."""
from pathlib import Path

P = Path('C:/kyty/s123/FACTS.md')
MARK = '## Step 9 — audit'
SEC = '''
## Step 9 — audit (HPP-32; author: Session Auditor; not yet accepted by the lead)

`C:/kyty/s123/audit123/AUDIT123.md` (git `docs/session-123/audit/`). Game not started by the auditor; no lock during the audit.
* **Recount CONFIRMED** by an own parser (`recount123.py`, no code shared with `skc123.py`/`smk123.py`/`ref123.py`): `sky123`
  Δ`dt_us` 11 384,3 ± 132,7 мкс (51 пара), `ght123` 8 076,7 ± 77,0 (71) — до последней цифры, оба CEILING_MEASURED; все ряды
  G4/G7/G8/G9/G10/G11/K16/Т2/Т5 совпадают. Бутстрэп [11 254,7; 11 512,9] / [8 006,0; 8 155,8]; окно 10..88 — 11 364,4 / 8 088,0.
* **1 MAJOR / 6 MINOR, вердикты не меняются.** MAJOR-1: тик рутины «Сторож цикла» (ран лида `f942e011`, `chain_check.py
  --repair`, запись `HPP-54`) 06:40:06–06:40:29 внутри замка `ght123` (06:37:42–06:43:08) — нарушение п. 25(ж); текст рутины
  всё ещё разрешает «проверку во время запечатанного прогона». Без задетых пар Δ `ght123` 8 051,7 ± 69,8 (±0 с) … 8 053,0 ±
  72,3 (±15 с). MINOR: полосы G10 300/600 без строки ROADMAP; база G8(2) `ght122` в печати раньше п. 39(в) (не ослабление:
  с базой `sky122` 3,14 % < 5 %); черновой полный `mutlib` при разработке (п. 19(б)); `procload --wait-s 1800` > 600 с
  (первая попытка ушла в фон, п. 21); GPU 6–7 % перед `sky123`; `runs123/` пуст (нет `--out`).
* **НЕ доказано:** выигрыш; потолок в режиме NEW (опора шла в OLD); у `ght123` est B 16 672,7 ≈ вблэнк — Δ усечён, «60 кадров/с»
  не частота игры; критичность GuestGpu (Δdt/Δcpu_gpu 0,863 / 0,777 — наблюдение); картинка (видео нет); K16 (`img_up_kb` на
  переведённый кадр ×2,18); цена ручки при 0 против `d3a981a2`.
'''

text = P.read_bytes().decode('utf-8')
assert MARK not in text, 'already patched'
text = text.rstrip('\n') + '\n' + SEC
P.write_bytes(text.encode('utf-8'))
print('appended', len(SEC), 'chars')
