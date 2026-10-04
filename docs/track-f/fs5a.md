# FS5a (`HPP-509`, Emu Engineer): пятый бинарь отгрузки трека F (FS5) — умолчание `KYTY_FIX_F10=1`

Решение лида — `7de178f9:docs/ROADMAP.md:21732` п. 410 (якорь «410. **Звено F12h трека F (`HPP-482`, лид): F12d, F12e, F12f, F12g ПРИНЯТЫ — Ф10
`FIXED` по п. 391(г)»; +1 — «кода 1 из 3 прошла; умолчание `KYTY_FIX_F10=1` — пятым бинарём отгрузки трека F FS5»), подпункт (г)(1) —
`7de178f9:docs/ROADMAP.md:21767` (якорь «(1) **FS5a (Emu Engineer, без замка).**»; +1 — «иначе `EnvValueOn`), одно чтение (`static const bool`)
сохраняется»), правило базы (г)(6) — `7de178f9:docs/ROADMAP.md:21804` (якорь «(6) **Порядок отгрузок FS5 и S12 и сбор S13»; +1 — «`56189185` и варианте
`variant_fixb26_fixb1b`»). Вход — код F12d `1833ee28` и база FS4 `3d0e46da` (`7037b199`, `docs/track-f/fs4a.md`). Игра не запускалась; установленный
бинарь `31cbfee8` и кэши не тронуты (sha256 `ps5 em/kyty_emulator.exe` после сборки — `31cbfee8261f…`). Время — UTC по `date -u`, события —
`C:/kyty/f287/times.txt` (строки `FS5a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Замка `C:/kyty/SEALED_RUN.lock` и
`C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой); перед каждой командой дольше 60 с — проверка API (`hecheck.sh`): звена
Harness Engineer в `in_progress` не было ни разу (общее правило 30), комментариев в `HPP-509` — 0.
**WIP по дыму: бинарь собран и проверен тестами, игрой не проверялся** (теги — FS5c после FS5b).

## Итог

- **База по п. 410(г)(6)(i) — FS4 `3d0e46da`**: S12a (`HPP-494`) на начало сборки — `blocked`, лидом не принят (API 07:11:27Z) [c].
- **Коммит кода: `main` `c3eb8fe8`** (родитель `b64cc8be`; 3 файла, +11/−5, `--only`): `ShaderDecoder.cpp` (чтение), `ShaderDecoder.h` и
  `shaderTranslationCache.cpp` (только комментарии, называвшие умолчание 0).
- **Worktree `C:/kyty/f287/fs5/fs5a/wt` — `0e72bc19` = cherry-pick `c3eb8fe8` на `8a56dc2a` = cherry-pick `1833ee28` на `3d0e46da` (FS4)**; оба cherry-pick
  без конфликтов; patch-id `1833ee28` = `8a56dc2a` (`db491819…`), `c3eb8fe8` = `0e72bc19` (`187a3c1f…`) [c]; шесть файлов `1833ee28` в `0e72bc19` = `main`
  `c3eb8fe8` (`git diff --stat` пуст); `git status --short` — 0 строк; CR в `src/` — 0 из 456 файлов.
- **Бинарь: sha256 `631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17`**, копия `C:/kyty/f287/bin/kyty_emulator_631ff987.exe` (sha256 тот же;
  `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). **Не установка.**
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `26ce5fc78ea3b20be537c7696be041f5e97d9e58` — новая** (≠ FS4 `56189185…`; ≠ F12d `e248e4a8…`, т. к.
  FS5a правит `src/graphics/shader/**`) (`build/kytyGitVersion.h:9`, 1 вхождение в exe); `KYTY_GIT_REVISION` = `0e72bc19c9ec…` (`:7`). Каталог по
  умолчанию — `variant_fixb26_fixb1b_fixf10` [c гейта]. Первый запуск FS5 — холодная трансляция во всех вариантах.
- `check_gate_order.py` (`C:/kyty/s113/`, `--src wt/src`) — `GATE ORDER: clean`, вывод байт в байт = FS4a (гейтов и ручек правка не добавляет).
- **`shader_cfg_tests` при умолчаниях (в окружении нет ни одной `KYTY_*`, кроме `KYTY_TESTS_CONTINUE`/`KYTY_TESTS_VERBOSE`) — 127 тестов, падение 1 — Б11**
  (`IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`, 2 строки), rc 0; лог с заменой `elapsed_ms=\d+` = FS4a [c]; без замены — одна строка 64 (`elapsed_ms` 17 у FS5).
- **GPU-гейт F12d `shader_recompiler_compute_tests --fix-f10-only` — 6 из 6 `ALL OK`** (15 кейсов: 11 F10 + 4 B1b, по 16 строк `ok` с проверкой ключа кэша):

| `KYTY_FIX_F10` | `KYTY_BVH_NATIVE` | effective | ожидания | подпись / каталог | итог |
|---|---|---|---|---|---|
| нет | 0 | 1 | `=1` | `…:fixb26:fixb1b:fixf10` / `variant_fixb26_fixb1b_fixf10` | `ALL OK` |
| нет | 1 | 1 | `=1` | `…:fixb26:fixb1b:fixf10` / `variant_fixb26_fixb1b_fixf10` | `ALL OK` |
| `0` | 0 | 0 | `=0` | `…:fixb26:fixb1b` / `variant_fixb26_fixb1b` | `ALL OK` |
| `0` | 1 | 0 | `=0` | `…:fixb26:fixb1b` / `variant_fixb26_fixb1b` | `ALL OK` |
| `1` | 0 | 1 | `=1` | `…:fixb26:fixb1b:fixf10` / `variant_fixb26_fixb1b_fixf10` | `ALL OK` |
| `1` | 1 | 1 | `=1` | `…:fixb26:fixb1b:fixf10` / `variant_fixb26_fixb1b_fixf10` | `ALL OK` |

  Ожидания гейт выбирает по `FixF10Enabled()` процесса (`F10Cases(fix_on)`, `tests/ShaderRecompilerComputeTests.cpp:31950`), ключ кэша — `Require("F10Cache")`
  (токен `:fixf10` в подписи и `_fixf10` в каталоге — последние и только при effective 1) [c]. Подпись во всех шести — `KytySC3:26ce5fc7…`.
- В exe строки `KYTY_FIX_F10`, `:fixf10`, `FixSval: mode=`, `FixB42Ext: mode=` — по 1 [c]. Предупреждений в правленых файлах нет (`build_wt1.log`, полная
  сборка 782 шага) [c].
- **Таблица умолчаний** (`knobs_fs5a.py 0e72bc19`): умолчание 1 — ровно `KYTY_FIX_B1B`, `KYTY_FIX_B26`, `KYTY_FIX_B42`, `KYTY_FIX_B9A`, `KYTY_FIX_DUALSRC`,
  `KYTY_FIX_F10`, `KYTY_FIX_MINIMIZE`, `KYTY_FIX_SVAL` (восемь ручек п. 410(г)(1); база не S12 — `KYTY_S_PCW` не входит, его чтение — `default-off`);
  `DEFAULT-ON == expected: True`, `ALL OK`; против вывода FS4a — только строка `KYTY_FIX_F10` и списки [c].
- **Дифф источника FS5 против `3d0e46da` — 6 файлов, ровно файлы `1833ee28`** (+352/−11); файлы FS5a — подмножество этих шести; вне шести — пусто [c]
  (`diffstat_vs_3d0e46da.txt`, `fs5a_vs_3d0e46da.diff`, `fs5a_vs_8a56dc2a.diff`).
- **Член «бинарь содержит» в чтении п. 380(б)** (`git cherry -v 0e72bc19 <c> <c>^`, `cherry.out.txt`): `-` (равное изменение есть в истории) у `4e72289e`,
  `68602c4f`, `17adaf80`, `1833ee28`, `c3eb8fe8` — 5 из 5 ✓; `+` (нет) у `741e3312` (P35), `c9b4268e` (P40), `fcaf141b` (F14c, тест) [c]. Предки
  `0e72bc19` (`--is-ancestor`): `d515b901`, `92d11340`, `3d0e46da`, `8a56dc2a`, `4414e235` — да.

## Код (`c3eb8fe8:src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp`, в `0e72bc19` — те же строки)

**Умолчание** — `FixF10Enabled` (`:352–360`):

```cpp
bool FixF10Enabled() {
	// Track F, FS5a (HPP-509, ROADMAP s122 item 410(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FS4a 17adaf80).
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_FIX_F10");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return enabled;
}
```

Форма = `KYTY_FIX_SVAL` FS4a (`3d0e46da:pipelineCache.cpp:1343–1351`) и `KYTY_FIX_B1B` (`ShaderDecoder.cpp:344–350`): не задана или `""` → 1;
`0/false/off/no` → 0; прочее — `EnvValueOn` [c]. До FS5a — `Common::EnvValueOn(std::getenv("KYTY_FIX_F10"))` (не задана / `""` → 0). Комментарии:
`ShaderDecoder.h:759–761` («default ON since FS5a … unset or empty = on»), `shaderTranslationCache.cpp:578–579` («the default since FS5a»). Ветки `=1` / `else`
в `spirvEmitterMemory.cpp:2234…` и `Memory.cpp:891…`, токен `:fixf10` (`shaderTranslationCache.cpp:584`, последний в варианте) не меняются [c]
(`fs5a_vs_8a56dc2a.diff` — 3 hunk, только комментарии и чтение).

Пути по коду [c]: без переменной и при `=1` — путь F12d при `=1`; при `KYTY_FIX_F10=0` — ветка `else` (прежние строки, дословно `1833ee28`) — путь FS4 по
SPIR-V, отличие — подпись трансляции (новая), каталог `variant_fixb26_fixb1b` тот же, что у FS4 (п. 410(г)(4): `=0` на FS5 — только на холодном каталоге).

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `enabled` (static local, `ShaderDecoder.cpp:355`) | один раз — первый вызов `FixF10Enabled` (C++11 magic static, потокобезопасно; первый вызов — конструктор `ShaderTranslationCache` до первой трансляции, или трансляция) | нет — на время процесса | как до FS5a (была static local); значение — функция окружения процесса |

Нового состояния правка не вводит: меняется только выражение инициализации той же static local. Выход функции один (`return enabled`).

## Сборка

`mk_wt_fs5a.sh` (копия `mk_wt_fs4a.sh` на `3d0e46da` + cherry-pick `1833ee28`; подмодули как FS4) 07:12:26Z; патч worktree `patch_fs5a.py` (3 якоря —
блоки строк целиком, LF) и `check_gate_order.py` 07:12:50Z; configure 07:13:05–07:13:46Z; сборка-проверка 07:13:52–07:14:47Z; патч `main` тем же скриптом
(`cmp` трёх файлов с worktree ✓; до патча файлы `main` = `1833ee28`) и коммит `c3eb8fe8` 07:15:11Z; `git checkout -- src` в worktree и cherry-pick → `0e72bc19`
07:15:17Z; версия и пересборка 07:15:22–07:15:52Z; бинарь и копия 07:16:02Z; тесты (сборка 07:16:03–07:17:13Z, прогон 07:17:31–07:17:34Z, `run_tests_fs5a.sh`).
Шаги сборки — под `lockrun.sh` (копия FS4a: убивает шаг при замке или `STOP`, предел шага 540 с), флаги = FS4a (`build_fs5a.cmd` — копия `build_fs4a.cmd` с путями
`fs5\fs5a` и аргументом `target <имя>` из `build_f12d.cmd`). `CMakeCache.txt`: `Kyty_SOURCE_DIR=C:/kyty/f287/fs5/fs5a/wt`, `Release`.

## Файлы

`C:/kyty/f287/fs5/fs5a/`, копии в `docs/track-f/fs5a/` (текстовые — LF): `mk_wt_fs5a.sh`, `mk_wt.log`, `build_fs5a.cmd`, `lockrun.sh`, `hecheck.sh`,
`patch_fs5a.py`, `patch_wt.out.txt`, `patch_main.out.txt`, `gate_order.out.txt`, `run_tests_fs5a.sh`, `run_tests.out.txt`, `cfgtests_defaults.log`,
`gate_f10{unset,0,1}_nat{0,1}.txt`, `knobs_fs5a.py`, `knobs_fs5a.out.txt`, `diffstat_vs_3d0e46da.txt`, `fs5a_vs_3d0e46da.diff`, `fs5a_vs_8a56dc2a.diff`,
`cherry.out.txt`, `kytyGitVersion_fs5.h`, `commit_msg_code.txt`, `SHA256SUMS_fs5a.txt` (sha256 локальных оригиналов и бинаря). В копиях `mk_wt_fs5a.sh` адрес
агента в `user.email` заменён на `<agent-email>` (общее правило 28), поэтому его sha256 отличается от строки `SHA256SUMS_fs5a.txt`.

## Вопросы лиду

Нет. Чтение члена «содержит» — п. 380(б) (`git cherry` `-`), как в FS4a.

## Не заявляется

Что кремний PS5 отвечает на типы 2–3 ровно как программный путь GPURT; семантика слов 2–3 на PS5; что правка видна на листе; что дельты счётчиков или времени —
доказательство; что Ф20 влияет на игру; что SPIR-V корректен для устройства и картинка верна; что FS5 работает в игре (дыма не было, до FS5c); ни одно число —
не выигрыш; 60 FPS не обещаются.
