# FS7a (`HPP-565`, Emu Engineer): седьмой бинарь отгрузки трека F (FS7) — умолчания `KYTY_FIX_F8=1` и `KYTY_FIX_B24=1`

Решение лида — `be255cde:docs/ROADMAP.md:22584` п. 467 (якорь «467. **Звено F18f трека F (`HPP-542`, лид): F18c, F18d, F18e ПРИНЯТЫ»; +1 — «(а)
**Приёмка строкой по членам п. 441(д).**»), подпункт (г)(1) — FS7a; поправка — `76fe4284:docs/ROADMAP.md:22713` п. 487 (якорь «487. **Звено F19f трека F
(`HPP-550`, лид): F19c, F19d, F19e ПРИНЯТЫ»; +1 — «(а) **Приёмка строкой по членам п. 451(д).**»), подпункт (г)(1) — Б24 едет в FS7 (комментарий лида
`f73835ac` в звене). Правило базы — п. 410(г)(6)(i), чтение «содержит» — п. 380(б). Вход — код F18c `10a4800b`, F19c `9c726d74`, F19c2 `919c1a19` и база FS6a
`3904522d` (бинарь FS6 `9325446c`, установлен 2026-10-05 02:12:47Z, FS6d `HPP-558`, п. 510). Игра не запускалась; установленный бинарь `9325446c`,
`C:/kyty/build/install` и кэши не тронуты (sha256 `ps5 em/kyty_emulator.exe` после звена — `9325446cdd3c960b…`) [c]. Устройства звука и ввода хоста не
трогались: стенды работают на драйвере звука `disk` и виртуальных падах SDL. Время — UTC по `date -u`, события — `C:/kyty/f287/times.txt` (строки `FS7a`).
Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.
**WIP по дыму: бинарь собран, проверен стендами и тестами, игрой не проверялся** (теги `fs7_h`, `fs7_n` — FS7c после FS7b).

## Итог

- **База по п. 410(г)(6)(i) — FS6a `3904522d`**: FS6 установлен (п. 510); после него лидом не принят ни один другой бинарь отгрузки — п. 511–512 (S13c)
  каталог не устанавливают, F16o2 `365cc3c2` — код с умолчанием 0 (бинарь теста) [c].
- **Коммит кода: `main` `ec6c4c83`** (`--only`; 3 файла, +17/−7): `src/libs/audio.cpp` (чтение `KYTY_FIX_F8` и комментарий), `src/libs/audio_internal.h`
  (комментарий: старое умолчание), `src/libs/controller.cpp` (чтение `KYTY_FIX_B24` и комментарий над `g_fix_b24`).
- **Worktree `C:/kyty/f287/fs7a/wt` — `d6ee2dc8`** = `3904522d` + cherry-pick `10a4800b` (`e2a21d74`) + cherry-pick `9c726d74` (`915871f7`) + cherry-pick
  `919c1a19` (`b47033cb`) + cherry-pick `ec6c4c83` (`d6ee2dc8`); **конфликтов нет** — `CMakeLists.txt` в `9c726d74` слит автоматически («Auto-merging»), блоки
  целей `b24_pad_stand` и `f8_audio_stand` оба на месте дословно (дифф `CMakeLists.txt` против базы — два добавленных блока по 5 строк, `fs7a_vs_3904522d.diff`);
  patch-id каждого cherry-pick = оригиналу (`3add70bd`, `875b7df3`, `2a996c60`, `68d889d6`) [c]; `git status --short` — 0 строк; CR в `src/` — 0 из 456 файлов
  (`mk_wt.log`).
- **Бинарь: sha256 `8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7`**, копия `C:/kyty/f287/bin/kyty_emulator_8df61c00.exe` (sha256 тот же;
  `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`); строка версии `KytyPS5-2026-09-15-6a2987a-1883-gd6ee2dc8`. **Не установка.**
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `26ce5fc78ea3b20be537c7696be041f5e97d9e58` = базе** (FS6/S12/FS5) — `build/kytyGitVersion.h`, 1 вхождение
  в exe; `KYTY_GIT_REVISION` = `d6ee2dc886c9…`. Правка вне `src/graphics/shader/**` — каталог варианта `variant_fixb26_fixb1b_fixf10` не меняется, прогрева нет [c].
- `check_gate_order.py` (`C:/kyty/s113/`) на `main` после патча и на `wt/src` — `GATE ORDER: clean`, вывод байт в байт = FS6a (`gate_order_wt.out.txt` FS6a) —
  гейтов и ручек правка не добавляет [c].
- **Стенд `f8_audio_stand` из того же worktree** (sha256 `c0cf1ea3…`; драйвер `run_stand_fs7a_f8.py` — порт `docs/track-f/f18c/run_stand_f18c.py`, чтение
  п. 448(б): `disk` × 3 устройства), `ALL OK`:

| прогон | `KYTY_FIX_F8` | итог | ожидание п. 467(г)(1) |
|---|---|---|---|
| (i) `i_disk3_fix0` | `0` | `first_fail_call=254`, `fail_devices_at_first=3` (3 из 3), `Invalid audio device ID`, `init_calls=303`, строк `FixF8:` 0 | отказ на вызове 254 у 3 из 3 ✓ |
| (ii) `ii_disk3_unset` | не задана | `queue_failed=0`, `init_calls=1`, `acq=10003`, `FixF8: mode=1` 1 строка | 0 отказов, `init_calls` 1 ✓ |
| (iii) `iii_disk3_unset` | не задана | 2 × 5 000: `init_calls_after_threads=1`, `acquire_failed=0`, `FixF8:` 1 | `init_calls` 1 ✓ |
| (i) в форме `=1` `i_disk3_unset` | не задана | 0 отказов, `init_calls=1` | (справка) |
| `refuse`, `refuse_host` | `0` | стенд отказывается без драйвера и с драйвером хоста, rc 3 | (контроль драйвера) |

- **Стенд `b24_pad_stand` из того же worktree** (sha256 `068b8eb1…`), `ALL OK` у всех трёх драйверов:
  - `run_stand_fs7a_b24.py` (порт `docs/track-f/f19c/run_stand_f19c.py`): (i) `i_fix0` (`KYTY_FIX_B24=0`) — `wall_vib_us` 2 800 035, `pad_wait_max_us`
    2 799 934, `guest_sdl` 2, строк `FixB24:` 0 — контроль ✓; (ii) `ii_unset` (не задана) — `fix_b24=1`, `wall_vib_us` 44, `pad_wait_max_us` 4,
    `po_wait_max_us` 2 799 933, `guest_sdl` 0, `y_done_before_unlock=1`, `FixB24: mode=1` ✓; (iii) `iii_unset`, `iii_unset_b` — 20 000 записей при 278/280
    циклах подключения, `pad_wait_max_us` 25/12, `guest_sdl` 0, `rumble_bad` 0, `final_connected=1` ✓; справка: `i_unset` (форма `=1` для (i)), `ii_fix0`.
  - `run_stand_fs7a_b24dd.py dd` × 100 без переменной (порт `docs/track-f/f19c2/run_stand_f19c2.py`; циклы 0…99 пачками по 25 под сторожем): **падений 0 из 100**,
    не чистых 0, сценарий выполнен 100 из 100 (`po_wait_max_us` 300 067…301 370 ≥ 200 000), `ddsum … member` — `ALL OK`.
  - `trig`: пад `054C:0CE6` (`pad_type_ps5=1`); без переменной — `wall_trig_a_us` 37, отправки после разблокировки 2, `last_eq_b=1`, `a_ne_b=1`; `=0` —
    `wall_trig_a_us` 2 799 570 ≥ 2 700 000; `ALL OK` (член не запаркован).
- **Тесты при умолчаниях** (в окружении нет ни одной `KYTY_*`, кроме `KYTY_TESTS_CONTINUE`/`KYTY_TESTS_VERBOSE`); база — бинари сборки FS6a
  `C:/kyty/f287/fs6a/build` (`shader_cfg_tests` FS6a; `audio_propagation_tests` собран в той же сборке FS6a в этом звене как доп. цель):
  - `shader_cfg_tests`: 127 тестов у обоих, строк `failed:` 4 и 4, равны (Б11 `IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ` и 2 строки `shader resource evaluation
    failed`); логи с заменой `elapsed_ms=\d+` байт в байт; rc 0 [c].
  - `audio_propagation_tests`: база и FS7 — rc 0, последняя строка `ALL OK`, строк `failed:` 0 и 0; логи байт в байт [c].
- **Таблица умолчаний** (`knobs_fs7a.py d6ee2dc8` — копия `knobs_fs6a.py`, ожидание + `KYTY_FIX_F8`, `KYTY_FIX_B24`): умолчание 1 (не задана = ВКЛ) — ровно
  `KYTY_FIX_B1B`, `KYTY_FIX_B24`, `KYTY_FIX_B26`, `KYTY_FIX_B4`, `KYTY_FIX_B42`, `KYTY_FIX_B9A`, `KYTY_FIX_DUALSRC`, `KYTY_FIX_F10`, `KYTY_FIX_F8`,
  `KYTY_FIX_MINIMIZE`, `KYTY_FIX_SVAL`, `KYTY_S_PCW` (11 имён п. 467(г)(1) и `KYTY_FIX_B24` п. 487(г)(1)); `DEFAULT-ON == expected: True`, `ALL OK`. Против вывода
  FS6a — новые имена `KYTY_FIX_F8` (`src/libs/audio.cpp:295`), `KYTY_FIX_B24` (`src/libs/controller.cpp:839`), `KYTY_TEST_AUDIOLOSS`, `KYTY_TEST_HIDLOSS`
  (`default-off`), сдвиг строки `KYTY_TEST_MINIMIZE` в `window.cpp` (1055 → 1312, вставка F19c) и списки [c].
- **Дифф источника FS7 против `3904522d` — 12 файлов, ровно объединение файлов `10a4800b`, `9c726d74`, `919c1a19` и `ec6c4c83`** (+3185/−10): `CMakeLists.txt`,
  `docs/track-f/f18c/patch_f18c_src.py`, `run_stand_f18c.py`, `docs/track-f/f19c/patch_f19c_src.py`, `run_stand_f19c.py`,
  `src/graphics/presentation/window/window.cpp`, `src/libs/audio.cpp`, `audio_internal.h`, `controller.cpp`, `controller.h`, `tests/B24PadStand.cpp`,
  `tests/F8AudioStand.cpp`; вне них — пусто [c] (`files_expected.txt` = `files_actual.txt`, `diffstat_vs_3904522d.txt`, `fs7a_vs_3904522d.diff`,
  `fs7a_vs_b47033cb.diff`).
- **Член «бинарь содержит» в чтении п. 380(б)** (`git cherry -v d6ee2dc8 <c> <c>^`, `cherry.out.txt`): `-` у `10a4800b`, `9c726d74`, `919c1a19`, `ec6c4c83`,
  `a86a5ad0`, `17eb924e` — 6 из 6 ✓; также `-` у `4e72289e`, `68602c4f`, `17adaf80`, `1833ee28`, `c3eb8fe8`, `c1732d1a`; `+` (не входят) у `082d1612` (F14e),
  `f98e842c` (F14e2), `fcaf141b` (F14c), `741e3312` (P35), `c9b4268e` (P40), `365cc3c2` (F16o2) [c]. Предки `d6ee2dc8` (`--is-ancestor`): `3904522d`,
  `4d9e8ab7`, `0e72bc19`, `3d0e46da`, `4414e235` — да.
- В exe: `FixF8: mode=` — 1, `FixB24: mode=` — 1, `FixB4: mode=` — 1; `KYTY_FIX_F8` — 1, `KYTY_FIX_B24` — 1; `KYTY_FIX_F19`, `KYTY_PVAR_HOLD`, `KYTY_DIAG_F5`,
  `KYTY_FIX_F26`, `KYTY_FIX_F5CMU` — 0 [c].

## Код (`ec6c4c83`; в `d6ee2dc8` — те же строки)

**`KYTY_FIX_F8`** — `FixF8Enabled` (`src/libs/audio.cpp:291–303`):

```cpp
static bool FixF8Enabled() {
	// Track F, FS7a (HPP-565, ROADMAP s122 item 467(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FS4a 17adaf80).
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_FIX_F8");
		const bool  on    = value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
		if (on) {
			LOGF("FixF8: mode=1\n");
		}
		...
```

До FS7a — `Common::EnvValueOn(std::getenv("KYTY_FIX_F8"))` (не задана / `""` → 0). Строка `FixF8: mode=1`, обёртки `SdlAudioAcquire` /
`SdlAudioSubsystemInit` / `SdlAudioSubsystemQuit`, стенд `KYTY_TEST_AUDIOLOSS` и `AudioStat` не меняются (`fs7a_vs_b47033cb.diff`: в `audio.cpp` 1 hunk —
комментарий и выражение чтения; в `audio_internal.h` — только комментарий) [c].

**`KYTY_FIX_B24`** — `Controller::Initialize` (`src/libs/controller.cpp:835–846`):

```cpp
	// Track F, F19c (ROADMAP s122 item 451(d)): KYTY_FIX_B24, read once here - before the guest threads exist.
	// FS7a (HPP-565, ROADMAP s122 item 487(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other value
	// as EnvValueOn (the form of FS4a 17adaf80).
	g_fix_b24 = [] {
		const char* value = std::getenv("KYTY_FIX_B24");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	if (g_fix_b24) {
		LOGF("FixB24: mode=1\n");
		g_pad_output = new PadOutput;
```

До FS7a — `Common::EnvFlagOn("KYTY_FIX_B24")` (не задана / `""` → 0). Строка `FixB24: mode=1`, создание `PadOutput`, стенд `KYTY_TEST_HIDLOSS`, счётчики
вывода пада и строка `Controller <id>: removed` не меняются (`controller.cpp` — 2 hunk: комментарий над `g_fix_b24` и выражение чтения) [c].

Форма обоих чтений = `KYTY_FIX_SVAL` FS4a (`17adaf80`), `KYTY_FIX_F10` FS5a, `KYTY_FIX_B4` FS6a [c]. Пути по коду [c]: без переменной и при `=1` — пути F18c
и F19c2 при `=1`; при `=0` — прежние пути F18c/F19c2 при `=0`. Подпись трансляции и каталог одни для всех значений (ручки вне подписи).

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `enabled` (static local, `audio.cpp:294`) | один раз — первый вызов `FixF8Enabled` (C++11 magic static, потокобезопасно) | нет — на время процесса | как до FS7a (была static local); значение — функция окружения процесса |
| `g_fix_b24` (static, `controller.cpp:179`) | одна запись — `Controller::Initialize` (`:838`), до потоков гостя (`EXIT_IF(g_controller != nullptr)` выше — второй вызов невозможен) | нет — на время процесса | как до FS7a (та же единственная запись F19c); дальше только чтения |

Нового состояния правка не вводит: меняются только выражения инициализации тех же переменных. Выходов с пропуском снятия нет — снятия нет и до правки.

## Сборка и порядок

FS6d `done` (п. 510) — старт 02:22:29Z; патч `patch_fs7a.py` (якоря — строки целиком, LF) на `main` и коммит `ec6c4c83` 02:23:07Z; `check_gate_order.py`
на `main` — clean; worktree `mk_wt_fs7a.sh ec6c4c83` (копия `mk_wt_fs6a.sh`: `3904522d` + cherry-pick `10a4800b`, `9c726d74`, `919c1a19` + FS7a; подмодули как
FS6a) 02:24:02Z. Configure: строка `rc=0` в 02:24:07Z без вывода сборки (повтор); две попытки 02:30:38Z и 02:38:39Z сняты сторожем по процессу `procload.py`
серии F20c (`KILLED: procload` 02:31:45Z, 02:39:38Z; rc 7); обрыв хартбита `fe8b4f83` 02:54:18Z (сбой терминала платформы); продолжено хартбитом
`8c99da91` без повтора выполненного: configure 02:55:50–02:57:09Z; эмулятор 02:57:15–02:58:28Z; `f8_audio_stand` 02:58:56–02:59:24Z; `b24_pad_stand`
02:59:27–02:59:54Z; `shader_cfg_tests` 03:00:03–03:00:33Z; `audio_propagation_tests` 03:00:34–03:01:02Z; база `audio_propagation_tests` (сборка FS6a)
03:01:02–03:01:31Z; тесты 03:01:36–03:01:38Z; стенд F8 03:01:49–03:01:52Z; стенд B24 03:01:58–03:02:15Z; `trig` 03:02:19–03:02:27Z; `dd` × 100
03:02:32–03:03:25Z; проверки `verify_fs7a.py` 03:04:19Z, `check_gate_order` на `wt/src` и таблица умолчаний 03:04:34Z.
Шаги — под `watch_fs7a.py` (предел 540 с, остановка при замке, `STOP` или процессе `procload.py`), перед каждым — строка API `api_chk.sh` в `times.txt`: в
`in_progress` у Harness Engineer — `HPP-561` (серия F20c; в продолжении `run=n`, очередь занята) и `HPP-601` (печать без игры); замка и `STOP` не было;
процесс `procload.py` — в двух снятых попытках configure. Флаги сборки = FS6a (`build_fs7a.cmd` — копия `build_fs6a.cmd` с путями `fs7a`), `Release`.

**Н1 п. 454(в) для этой сборки — читать так:** sha256 `8df61c00…` относится к сборке в каталоге `C:/kyty/f287/fs7a/build`; сборка того же источника в другом
каталоге (FS7b) может дать другой sha256 — равенство машинного кода тогда читается классификатором с отрицательным контролем; бинарь тегов FS7c
опознаётся по sha256 `8df61c00…` и строке версии `…-1883-gd6ee2dc8`.

## Файлы

`C:/kyty/f287/fs7a/`, копии в `docs/track-f/fs7a/` (текстовые — LF): `patch_fs7a.py`, `patch_main.out.txt`, `commit_msg_code.txt`, `gate_order_main.out.txt`,
`gate_order_wt.out.txt`, `mk_wt_fs7a.sh`, `mk_wt.log`, `port_fs6a.py`, `build_fs7a.cmd`, `bstep.sh`, `api_chk.sh`, `watch_fs7a.py`, `sstep.sh`, `port_drivers.py`,
`run_stand_fs7a_f8.py`, `run_stand_fs7a_b24.py`, `run_stand_fs7a_b24dd.py`, `dd_loop_fs7a.sh`, `next_cycle.py`, `gate_free.py`, `dd_fs7_loop.log`,
`tests_fs7a.py`, `port_knobs.py`, `knobs_fs7a.py`, `knobs_fs7a.out.txt`, `verify_fs7a.py`, `verify_fs7a.out.txt`, `diffstat_vs_3904522d.txt`,
`files_expected.txt`, `files_actual.txt`, `fs7a_vs_3904522d.diff`, `fs7a_vs_b47033cb.diff`, `cherry.out.txt`, `kytyGitVersion_fs7.h`,
`runs/log_{tests,f8,b24,trig}.txt`, `runs/f8/` (`stand_fs7a_f8.txt`, `out_*.txt`), `runs/b24/` (`stand_fs7a_b24.txt`, `out_*.txt` до 200 КиБ),
`runs/trig/` (`trig_fs7a.txt`, `out_*.txt`), `runs/dd/` (`dd_fs7_cycles.txt`, `dd_fs7_summary.txt`, `dd_fs7_all.txt`), `runs/tests/{base,fs7}_{scfg,aprop}.txt`,
`SHA256SUMS_fs7a.txt` (sha256 локальных оригиналов и бинарей). В копии `mk_wt_fs7a.sh` адрес агента в `user.email` заменён на `<agent-email>` (общее правило
28), поэтому её sha256 отличается от строки `SHA256SUMS_fs7a.txt`.

## Вопросы лиду

Нет. Конфликтов cherry-pick нет. Отклонения от буквы, названные явно: драйверы стендов — порты `run_stand_f18c.py`, `run_stand_f19c.py`,
`run_stand_f19c2.py` (изменены только значение ручки прогонов «без переменной» и ожидание `=1` для «не задана», планы прогонов — члены п. 467(г)(1) и
п. 487(г)(1), имена файлов вывода; диффы — первые строки скриптов и `port_drivers.py`); база `audio_propagation_tests` собрана в сборке FS6a (в FS6a эта
цель не собиралась).

## Не заявляется

Что FS7 работает в игре (дыма не было, до FS7c) и что FS7 установлен (до FS7d); что настоящая потеря устройства хоста даёт ту же форму; что звук верен или
слышим; что поток звука без темпа меняет часы игры; что Б24 воспроизводим без оборудования; что сборка детерминирована при другом каталоге; что Ф6 — дефект или
не дефект; что Ф19 `FIXED`; что реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются.
