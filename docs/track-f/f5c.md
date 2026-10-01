# F5c (`HPP-357`) — зеркало раздела `C:/kyty/f287/FACTS.md`

Этап 1 (харнесс и печать) — коммит `2e5fdf40`, файлы `docs/track-f/f5c/`.

## F5c (`HPP-357`, Harness Engineer), этап 2 — серия под замком, 2026-10-01T15:44:42Z–16:05:31Z по строкам `times.txt`: (а) PASS, (б) NO STOP по печати / STOP по букве (дефект ридера — вопрос лиду), (в) PASS, (г) DATA

- Пробуждение монитора 15:42Z: замка нет, STOP нет; `win_f5c` 15:44:42Z — открыто (HPP-350/337/342/367 `done`, HPP-352/364/370 `blocked`,
  `executionRunId` пусты); стороннее 3D-приложение пользователя (pid 72024, причина BUSY 15:34:42Z) закрыто. Вызов — строкой печати
  `next_f5c.sh` → `PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series`; шлюз прошёл, замок взят 15:44:42Z, снят 16:05:31Z (rc 0).
- Печать `pred/f5c.md` sha256 `afffae715b43d92e98cc9a043e3367b410c7f00e9281fa782e2febb7ed5c8251` (= копия `C:/kyty/f287/pred/f5c.md`), ридер
  `f5c_read.py` не менялся после печати.
- Бинарь `6f495a65388a90a0381c9170f224777e84cb07d657115ad2a8662fa0bae168dd` установлен 15:44:49Z; возврат `9235a7ac61f1affb…` 16:05:14Z
  (sha256 сверен); кэш шейдеров 1 301 файл, listsha `bd7aa754…` = до серии; GLCache 16 файлов, listsha `3cdb7b0d…` = до серии; манифест
  после серии `cache_series.after.json`; посторонний CPU в замке 3,8 % из 32 логических.

| Тег | Плечо | Стенд 60:10 | Исход ридера (печать) | Числа |
|---|---|---|---|---|
| `f5c_a` | W `=1`, валидация, `KYTY_PIPELINE_PRECACHE=0`, фильтр Ф6 | `armed` 5,87 с → `minimize` 65,79 → `restore` 75,77 (Σdt) | **(а) PASS** | `Window 1 minimized` 1; `SwapchainZeroExtent:` begin 1 / end 1 (end = restore, не позже +2 с; `frames_dropped` 71, 9 965 мс); 0 `[Vulkan][E]`, 0 маркеров смерти, K2 0; удержание Σdt 324,5 с (≥ 310); `FrameTrace` после `restore` 2 039 (≥ 1 000); последняя строка — сохранение кэша пайплайнов; `AsyncPipelines: skipped draw` 1 108 (данные W без precache) |
| `f5c_b` | W `=0`, та же форма | `armed` 2,97 → `minimize` 62,97; `restore` нет | **(б) NO STOP** (член `vuid_01689_after_minimize` = False); вариант исполнителя — **STOP VUID-01689** | `[Vulkan][E][2]: vkCreateSwapchainKHR(): pCreateInfo->imageExtent (width = 0, height = 0) is invalid.` (1 строка, через 3 911 байт после `TestMinimize: minimize`), следующей строкой слоя `… #VUID-VkSwapchainCreateInfoKHR-imageExtent-01689)`; `SwapchainZeroExtent` 0, `FixMinimize: on` 0; конец — `vulkanWindow.cpp:913`, `SIGABRT`, код выхода 3221226505 (0xC0000409); 2 маркера `--- Error ---` (K1, лог и stdout) на остановке валидации |
| `f5c_v` | V `=1`, без валидации, видео | `armed` 3,12 → `minimize` 63,10 → `restore` 73,10 | **(в) PASS** | begin 1 / end 1 (end = restore; `frames_dropped` 300, 9 997 мс); удержание Σdt 334,4 с (≥ 330); видео 9 152 кадра (`.idx` 9 152), `s51_vidglitch 4 6` 0 глитчей всего и 0 вне окна (якорь `.idx` 64,51–76,51 с; вариант «наибольший разрыв» 64,57–76,59 с — 0); **N1**: записей после `end` 7 388, нарушений порядка present 0 (во всём файле 0); K1/K2 0; показанных кадров без записи вне окна 6, длиннейшая серия 1 (данные, не гейт); лист `sheet_f5c_v.png` (9 152 кадра, шаг 190, 8×6) — лиду |
| `f5c_g` | V `=0`, без валидации | `armed` 3,30 → `minimize` 63,28 → `restore` 73,28 | **(г) DATA** | маркеров смерти 0, K2 0; `Recovering Vulkan swapchain` 2, `SwapchainZeroExtent` 0; удержание Σdt 334,2 с; `FrameTrace` после `restore` 7 701; последняя строка лога `Event: quit` (штатный выход по таймеру удержания), код выхода — нет (`hold_exit` None) |

- **N2 (п. 285(в)):** во всех 4 тегах строка входа перед `TestMinimize: armed` несёт имя `underwater_aerial_garden` (одна пустая строка
  входа раньше — данные); сдвиг строки входа → `armed`: 54 / 226 / 54 / 107 байт, 0 строк `FrameTrace`, 0,000 с Σdt; `armed → minimize`
  59,92 / 60,00 / 59,98 / 59,98 с, `minimize → restore` 9,98 / — / 10,00 / 10,00 с.
- **Дефект ридера (б), найден после серии.** `f5c_read.py:181` ищет `VUID-VkSwapchainCreateInfoKHR-imageExtent-01689` только в строке
  `[Vulkan][E]`; слой печатает идентификатор следующей строкой «The Vulkan spec states … #VUID-…-01689)» — так же в `log_w144_09`
  (эталон Б37). Набор `test_f5c_read.py` (69/69) моделировал VUID в той же строке. Ридер запечатан и не правится; вердикт (б) по печати —
  **NO STOP**. Своя проверка `vuid_b_check.out.txt` (`facts_f5c_2.py`): `[Vulkan][E]` — байт 30 643 161, VUID — байт 30 643 415 (+254),
  после `TestMinimize: minimize` (30 639 250); процесс завершён (SIGABRT). По букве п. 273(е)(3)(б) «остановка с
  VUID-VkSwapchainCreateInfoKHR-imageExtent-01689» — **выполнено (вариант исполнителя)**. Вопрос лиду: засчитывать (б) по варианту или
  повторить (б) с исправленным ридером под новой печатью.
- Наблюдение листа (не вердикт): плитка 6 первой строки — заставка «LET'S GO» с чёрным прямоугольником справа от текста; смотреть лиду.
- Не заявляется: что без правки свёрнутое окно ведёт к крэшу или не ведёт (тег (г) — данные одного входа класса); что сцена корректна или
  проходима до конца; ни одно число — не выигрыш.
- Файлы: `C:/kyty/f287/f5c/` — `log_f5c_*.txt`, `stdout_f5c_*.txt`, `score_f5c_*.txt`, `runs/f5c_*.read.json`, `rec_f5c_v.mp4` (+`.idx`),
  `glitch_f5c_v.txt`, `sheet_f5c_v.png`, `vuid_b_check.out.txt`, `go_f5c.log`; в git — `docs/track-f/f5c/runs/` и `docs/track-f/f5c.md`.
- sha256: `score_f5c_a.txt` `c7d990ebe3583650a5f903b3f6b64da13359a900ccaf4615b6cce7ede92fd2e6`; `score_f5c_b.txt` `94d07d985d8f3db32d947d428142984d35060ba10247b79f5bf2c350b070239a`; `score_f5c_v.txt` `cb653254147b39151849e485823182c819d971416018df1e5b7f46e01cb88e9e`; `score_f5c_g.txt` `c5160e87f63a42b4059e630400cd5b77db6feb42d5eccb40e9ba03424cb85990`; `vuid_b_check.out.txt` `aa7136a5203df26d278edac0b94206dbf0c6b8cd0f11f06bcfce0a7a90449310`.
