"""F36b (HPP-759): append the F36b section to C:/kyty/f287/FACTS.md by general rule 34 - copy to FACTS.md.prev, append mode 'a',
size after = size before + section bytes; on mismatch the copy is returned and the script stops (exit 2). Refuses if the header
is already there (exit 1)."""
import os, shutil, sys

P = 'C:/kyty/f287/FACTS.md'
H = '## F36b (`HPP-759`, Red Team): враждебный отзыв реплея Б8-H F36a — `SOUND_WITH_CHANGES`, 2 RC (к чтению F36c)'
T = '\n' + H + '''

- **Задание:** п. 687(з) (`02531a91:docs/ROADMAP.md:24428`); вход — отчёт F36a `08214036:docs/track-f/f36a.md`. Отчёт — `docs/track-f/f36b-review.md`, файлы `C:/kyty/f287/f36b/` (в git `docs/track-f/f36b/`). Ссылки 9 из 9 (`refs_f36b.out.txt`, `ALL OK`).
- **Время (UTC, `f36b/times.txt`):** пробуждение 21:16:06; свой разбор SPIR-V 21:20:25, RC3(б) 21:20:49; мутанты комментарием до данных 21:21:01 (N = 5, seed — нет); реплей k03 21:22:33–21:24:05; входы k03 21:25:09–21:25:41; пересчёт F36a 21:26:34; реплей 11 годных 21:26:58–21:32:40.
- **Вид мест [c своего разбора]:** FS11 `%5011`, `%5013`, `%5037` = S12 `%5038`, `%5040`, `%5064` — `Fragment`, `DepthReplacing`, `OpImageSampleImplicitLod … Bias`, выходы Location 0–2 ⇒ вид эталона H.
- **RC3(б) [c кэша]:** ключ `a772ac521fadeb8a` один; модуль в каталогах до F19 = модулю снимка `ebff0fee…`, в `_fixf19` = `def` `71ebbdda…`.
- **Пересчёт F36a своим кодом:** 38 событий, годных 13 (по (α) 5), `N_diff` 0, `n_t` > 0 на 13, `n_f` 0, Г2 38/38 — = F36a.
- **Свой реплей 13 годных + 1 негодного [c]:** `N_null` 0, Г1 по выходам и по входам PS/VS (22–24 ресурса) 0 на 13 из 13; RC4(б) `mask_inv` = `mem_inv` = `sens`, ≠ `def` на 13 из 13; поля = F36a (14 событий × 10 полей, `cmp_f36b.py` `ALL OK`). На № 2 (k03 46854) вход `t27059` несёт выход № 1 (def 530, sens 746).
- **Мутанты:** m1 убит (№ 2: `Npre` 530/746); m1′ («до» на `eid − 1`) убит 14/14; m2 и m2′ убиты на № 2 (4 303 ≠ 130), на № 1/№ 3 эквивалентны (хранилище свежее — игра перезаписывает слоты); m3 (ошибка select на `%5011`) убит 13/13 (`N(m3, mask)` 228–914).
- **RC:** RC1 — член RC4(б) F23g (обязателен по п. 503(в)) в наборе F36a не исполнялся; читать по F36b (13/13). RC2 — Г1 F36a только по выходам; прошлое исполнение доходит до события через входы (показано на № 2); читать «выходы [c F36a] + входы PS/VS [c F36b] 13/13», следующий реплей Б8 — Г1 с входами. По прочтению F36b — не «RC к методу» п. 687(ж)(5); решает лид (F36c).
- **Наблюдения:** Г2 различает только на чётных исполнениях; слоты счётчиков — слова данных игры (1, 1000); поправка §0.8 подтверждена (`eid − 1` = после события на 14/14); форма A — 3 места из 18 выборок неявного LOD с битом дорожки; сэмплеры снимка `Never` у 27 `Dref` — [U].
- **Не заявляется:** что Б8-H — дефект или не дефект (решает F36c); что входы вне PS/VS равны; что офлайн-трансляция повторена; форма при ложном условии; что класс H не встречается на других программах, кадрах, драйверах; 60 FPS не обещаются.
'''
b = T.encode('utf-8')
before = os.path.getsize(P)
if H in open(P, encoding='utf-8').read():
    print('already there'); sys.exit(1)
shutil.copyfile(P, P + '.prev')
with open(P, 'ab') as f:
    f.write(b)
after = os.path.getsize(P)
if after != before + len(b):
    shutil.copyfile(P + '.prev', P)
    print('SIZE MISMATCH', before, len(b), after, '- copy returned'); sys.exit(2)
print('appended', before, '+', len(b), '=', after)
