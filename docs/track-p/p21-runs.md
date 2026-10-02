# Трек P, звено P21 (`HPP-393`, Harness Engineer): повтор G1 итерации P-var 1 — четыре тега под замком и скоринг

Печать `C:/kyty/p283/pred/05_p15.md` (принята `ROADMAP.md` п. 331, KytyPS5 `4636e5fd`); пункты п. 312(д), 326. Источник истины — `C:/kyty/p283/FACTS.md`, раздел P21; время — `C:/kyty/p283/p21/times.txt`.


- Время — `C:/kyty/p283/p21/times.txt` (`date -u`): старт 18:47:38Z; `qa_A2` 18:47:51–18:57:16Z, `qv_3` 18:57:25–19:05:30Z, `qv_4` 19:05:43Z (BUSY до замка
  19:06:25Z — не попытка, повтор вызова 19:07:05Z) – 19:15:39Z, `qw_V2` 19:15:55–19:23:37Z; конец серии 19:24:35Z. Замок — `p19/runs/lock.log`.
- Вызовы дословно из печати `05_p15.md` (`a2dd7c74…`, принята п. 331), `--check-seal` PASS (22) перед серией; по одной попытке, на бинаре P-var
  `56ee1914…`; установленная `dac02fb9…` снята перед каждым тегом и возвращена по sha после каждого (4 из 4 строк «returned … = before the tag»); кэши
  трансляции — `unchanged by the run` 4 из 4, GLCache после = до 4 из 4; строк `minimized` / `Recovering Vulkan swapchain` 0 у всех тегов,
  `lost keyboard focus` 1 у `qa_A2` (ввод — `KYTY_KEYS` силами эмулятора; членом допуска п. 273(з) не является); `vk_layer_settings.txt` нет.
- **`STOPCHECK qa_A2 PASS`** (доля 5,29 % в [3,98; 7,24]; потерянных строк 0 из 10 165; нулевой контроль ok; сверка D к `qa_A` P17 — 69 имён, медиана
  1,0000; GLCache 16 → 16) — повтор `qh_A3`/`qa_A3` не понадобился.
- **`VERDICT_P19 g1'=TWO_OF_TWO ratchet=NONE r2=OK w=W_CLEAN x=qa_A2`** (`verdict_p19.txt` `6f4a3a89…`):
  - `qv_3`: `SPEED_OK` 0,9979 (29 имён скорости, 32 целые пары, 20 событий; «минус одно событие» 0,9961…1,0035, сторона та же; доля наибольшего
    события 0,1834; T6 0,9991; `HIDDEN OVERRUN` нет); поимённый фильтр 0,02 (печать): 50 из 69, `SPEED_OK` 1,0033.
  - `qv_4`: `SPEED_OK` 0,9978 (28 имён, 31 пара, 20 событий; 0,9965…1,0024; доля 0,1846; T6 0,9992; `HIDDEN OVERRUN` нет); фильтр 0,02: `SPEED_OK` 1,0017.
  - ХРАПОВИК `NONE` (`qa_A2` 5,29 % в полосе; `qv_3` 2,79 %, `qv_4` 2,40 %). R2: видео `qa_A2` / `qv_3` / `qv_4` — 10 542 / 10 935 / 12 824 кадров,
    0 глитчей, K1/K2 0. Гейт целостности ручки 2: покрытие 0,999907 / 0,999921 / 0,999609 (`qw_V2`).
  - `qw_V2` `W_CLEAN`: 0 `[Vulkan][E]` на 324,0 с; 295(б)(1) строк лимита 0; (2) строк слоя 866 165; (3) последняя строка слоя 0 мкс до конца
    удержания; форма `limit=100000000 filter=none`, `KYTY_PIPELINE_PRECACHE=0`. Печать (W по `dt` не судится): 7,90 FPS, k = 3 у 100 % записей,
    411 строк `skipped draw`.
  - Строка прежнего правила с окном признака (печать `W03`): `qv_3` `SPEED_OK`, `qv_4` `CLOCK_UNDETERMINED`.
- Копии — `C:/kyty/p283/p21/runs/` (73 файла), `SHA256SUMS_p21.txt` `44be58d1…`; листы `sheet_qa_A2.png`, `sheet_qv_3.png`, `sheet_qv_4.png` — лиду (не смотрены).
- Обёртки `p21/`: `next_one.sh` (только запуск), `wait_one.sh` (≤ 530 с), `call_one.sh`, `apichk21.py`; маска `<app>` — `mask21.py` (`2573210f…`,
  `test_mask21.py` 7 `ALL OK`, вывод `5dfa3dad…`) по `times.txt`, `gop19.log`, `<тег>.stdout.txt` после каждого вызова.
- Вопрос лиду: запечатанные `fgcpu_p15.py`/`procload.py`/`enter_scene.py` печатают имена процессов (правило «Процесс» 4 с. 146); текстовые выводы
  маскированы после вызова, json (`<тег>.json`, `runs/fgcpu_<тег>.a.json`) — без маски (их читает скорер; копии в `p21/runs` байт в байт).
- Не заявляется: что патч исправляет игру; что P-var или G1′ корректны; что переменный шаг не ломает физику; что шаг один; ни одно число — не выигрыш.

## Файлы

`SHA256SUMS_p21.txt` (73 файла) sha256 `44be58d169a6a621afe350f42f48d1ae5746083f326febb1f5b094e0a1bffc93`.

| файл (`C:/kyty/p283/p21/runs/`) | sha256 |
|---|---|
| `05_p15.md` | `a2dd7c74d8346c32067576e3c15060d195d8bcb954ef1ad22f22228ae4d5b2bb` |
| `verdict_p19.txt` | `6f4a3a893b4d8d6b53c852092d974e6ef5b63b73b432f0ce87833b151bfd09fa` |
| `g12_p19.txt` | `6df4984ab59d98a154c3b7d0ba4800d8f8f9cb0c6fcc84bf2f1cb571106342fb` |
| `stopcheck_qa_A2.txt` | `b086d4a67ac5e2b903a605334754e637c48ece800319cdb783849c13ae6aa8fe` |
| `log_qa_A2.txt` | `3030dd07d161149dbbd534d1332bf9d63c31a2b8bc1f5864ebc8a91021b5f224` |
| `log_qv_3.txt` | `b530b3b58372159413ab7e09c9aba2f2decedd211d09dc77fe2c8dd4d43ca8b7` |
| `log_qv_4.txt` | `a3bccd598a2ef19b23952b878e7481a34c2120f1d37a38e1c3feda61f023d14d` |
| `log_qw_V2.txt` | `47723998fe9f7abb0800459f486e597bdab4ce24a43b0b02e05cfa06f13ceb41` |
| `rec_qa_A2.mp4` | `331b7c25126913107ac2fcaffa736bffa1ae42839d46e886919ce169a2a078b0` |
| `rec_qv_3.mp4` | `c023efb1a827ea476817d06eb4faa66b600e7740fe1383a683b506850533e282` |
| `rec_qv_4.mp4` | `af484cc8abf33bf5868d3d40b6ba4f8c7d89cab6be2e4e9228e1113d79075cb3` |
| `sheet_qa_A2.png` | `164b10f3fd519574517b865e4ed0617cc1ee569b4d2b8e0035ed41483eed97cd` |
| `sheet_qv_3.png` | `34075b0509c9f3d73e8b8f8f201abf1105ab85350c128a60f86aec0144590ea0` |
| `sheet_qv_4.png` | `755da843ff9b1ecf3052294933ed84e17b007487e8a25214e13612880b9dfe0d` |
| `score_qa_A2.txt` | `33fd38682922502904cacc3ebf89d06b347b1e819dd6bdebef39754002616733` |
| `score_qv_3.txt` | `1185e556e498c67137220dfcf0ee6e37565b7056211c0f02948a740b6b0f0407` |
| `score_qv_4.txt` | `28e04c9f58cfb9b5ed1438ea10ccd87354bc1250c3a3a55517f60881d4ec852c` |
| `score_qw_V2.txt` | `9bdeaf57c14d86b82d11af90c00af7c493b57a9262ce7207c7bccf7d30487853` |
| `lock.log` | `cbce164c267b74d299257a079764194c5b6db40b7bb061b93d25981198a9e9d2` |
