# M8a (HPP-858) — записка имён до кода: T125, порт `c86c8b4d9` в своей форме под `KYTY_M_T125`

Время записи (UTC, `date -u`): 2026-10-13T06:03Z — до первой правки кода. Основание: `ROADMAP.md` п. 778(г)(2), (ж)
(KytyPS5 `1ffda330`). Исполнитель — Emu Engineer. Код: worktree `C:/kyty/m657/m8a/wt` от MS1 `ed94b13d` и тем же
патчем в `main` (patch-id равны). Номера строк ниже — по дереву MS1 `ed94b13d`.

## 1. Ручка и строки

- `KYTY_M_T125`, умолчание 0 (не задана, пустая или `0/false/off/no` — ВЫКЛ; иное — как `Common::EnvValueOn`),
  читается один раз на процесс функцией `MT125On()` в `src/libs/libAudio2.cpp`; первая же проверка печатает
  `MT125: mode=<0|1>` (раз на процесс; первый вызов — `AudioOut2ContextCreate`).
- `MT125Stat: when=exit mixed=<n> mixed_nz=<n>` — только при `=1`; `mixed` — число вызовов вывода контекста
  (`ContextPush`), в которых смесь объектов отдана на устройство; `mixed_nz` — из них с ≥ 1 ненулевым отсчётом смеси.
  Печать — обработчиком `std::at_quick_exit`, который `MT125On()` ставит при `=1` (позже `EmergencyShutdownActive`,
  `src/emulator.cpp:550`, поэтому исполняется раньше него и строка уходит в журнал до сброса). `src/emulator.cpp` не
  правится (его места выхода в `main` и в MS1 различаются строками диагностики — patch-id не сошёлся бы). Выход не
  через `std::quick_exit` (фатал, `_Exit`) строку не печатает — как `FixF20Stat`.
- Ручки измерения нет; вне набора подписи трансляции (тема HLE, `src/libs/**` в подпись не входит).

## 2. Места правки (все — `src/libs/libAudio2.cpp`; `audio.cpp`, `audio_internal.h`, `dualSenseHaptics`, `emulator.cpp` не правятся)

1. `#include <cmath>` — после `#include <atomic>` (:14) (`std::isfinite`).
2. `AudioOut2ContextState` (:173–180) — поле `int object_audio_handle = 0;` (устройство смеси контекста; при `=0`
   всегда 0).
3. `AudioOut2PortStateEntry` (:182–193) — поля `float m125_gain = 1.0f;` и `uint32_t m125_ambisonics = UINT32_MAX;`
   (при `=0` не пишутся и не читаются).
4. Новые функции T125 перед `audioout2_context_has_queueable_device` (:345): `MT125On()`, счётчики и
   `MT125PrintExitStat()`, `audioout2_m125_mixable(state)` (отбор объекта в смесь — проверка формата данных порта),
   `audioout2_m125_coefficients(ambisonics, &l, &r)`, `audioout2_m125_mix_object(mix, state, grains)`,
   `audioout2_m125_has_queueable_device(ctx)`, `audioout2_m125_queue_context_audio(ctx, blocking)`,
   `audioout2_m125_set_object_attributes(port, attributes, num)`, `audioout2_m125_unfreeze` — нет (см. §4, D5).
5. `audioout2_context_has_queueable_device` (:345) — первой строкой тела: при `MT125On()` — ответ
   `audioout2_m125_has_queueable_device(ctx)` (старое условие ИЛИ «у контекста устройство смеси и ≥ 1 объект в смеси
   с PCM»).
6. `audioout2_queue_context_audio` (:356) — первой строкой тела: при `MT125On()` — `audioout2_m125_queue_context_audio`
   и возврат. Тело при `=0` не меняется (в `main` в нём строки M6a `KYTY_DIAG_M5W2`; при `=1` они не исполняются —
   счётчики M6a при `KYTY_M_T125=1` не считают, справка для чтения тегов с обеими ручками).
7. `AudioOut2ContextCreate` (:420) — после `g_audioout2_context_mutex.Unlock();` (:447): при `MT125On()` и
   `params->max_object_ports > 0` — `AudioInternal::AudioOutOpen(AUDIO_OUT_PORT_TYPE_MAIN, num_grains, 48000,
   Format::FloatStereo)` вне замка, затем под замком запись в `object_audio_handle`, если контекст ещё тот же
   (иначе — закрыть). Ошибка открытия — ручка 0, игре код не меняется (`OK`), смеси нет.
8. `AudioOut2ContextDestroy` (:459) — чтение `object_audio_handle` под замком контекста до сброса состояния и
   `audioout2_close_audio_handle` после цикла портов (при `=0` ручка 0 — закрытие ничего не делает).
9. `AudioOut2PortSetAttributes` (:678) — после `EXIT_NOT_IMPLEMENTED(...)`: при `MT125On()` и объектном порте
   разбор id 1 `GAIN` и id 8 `AMBISONICS` (`audioout2_m125_set_object_attributes`); затем общий путь (указатель PCM —
   как в MS1, для всех портов).
10. CMake: цель стенда `m_t125_stand` (`tests/MT125Stand.cpp` + `libAudio2.cpp` + `loader/timer.cpp`, как
    `audio_out2_port_tests`, `EXCLUDE_FROM_ALL`), запуск скриптом `docs/track-m/m8a/run_stand_m8a.py`, не ctest.

Порт шин (`port_type` не `0x1xx`) при `=1` идёт ровно путём MS1: тот же отбор `audio_handle > 0 && pcm_data != nullptr`,
тот же указатель, порядок и тот же вызов `AudioOutOutputs`; `GAIN` портам шин не применяется (член (г)(2)(i) «байт в
байт как при `=0`»; у upstream `c86c8b4d9` `GAIN` шин применяется — расхождение с upstream названо, [I] о консоли).

## 3. Смесь (форма upstream `audioout2_mix_object`, эталон — `TestObjectGainAndAmbisonics`)

- Объект в смеси (`audioout2_m125_mixable`): `port_type == 0x100`, `sampling_freq == 48000`, `audio_format` ∈
  {`FloatMono`, `Signed16bitMono`}, `pcm_data != nullptr` — те же условия, при которых upstream вообще создаёт
  объектный порт; прочие объектные порты (`0x1xx` ≠ `0x100`, иная частота, иной формат) в смесь не идут.
- Коэффициенты (лево, право) по `AMBISONICS`: `UINT32_MAX` и 64 — (½√2, ½√2); 0 — (1, 1); 2 и 65 — (½√2, −½√2);
  прочие — объект не смешивается (0, 0); каждый × `GAIN`. Отсчёт: float как есть, s16 — /32 768.
- Буфер смеси — `num_grains` × 2 float, заводится заново на каждый вывод (нет накопления между Push); выдаётся
  последним параметром `AudioOutOutputs` с ручкой `object_audio_handle`, если ≥ 1 объект попал в смесь и мест < 32.
- Чтение PCM объекта — по указателю в момент Push (тот же класс сырого чтения, что у портов шин: их PCM `AudioOutOutputs`
  тоже читает по указателю гостя); довод безопасности — M6c: `ao_obj_unread` 0 при `ao_obj_push` 2 014 739 (все гранулы
  объектов читаемы); если указатель недействителен — падение при `=1` [I] (тот же риск, что у шин).

## 4. Решения исполнителя

- **D1 `313b60e92` (копия PCM в `SetAttributes`) — не берётся.** Смесь её не требует: PCM объекта читается по
  указателю в момент Push, как PCM портов шин; игра задаёт PCM в цикле голосов вместе с позицией (id 3) на каждой
  гранулe [I по разбору M5a `0xeb2720`], общий буфер у ≥ 2 портов не показан (условие парковки `313b60e92` п. M5a не
  изменилось). Следствие: проверка «владения PCM» теста upstream (запись в буфер после `SetPcm` до Push) стендом не
  воспроизводится — смесь берёт байты на момент Push; это названо расхождением с эталоном, не членом.
- **D2 Ошибочные коды upstream не берутся.** Upstream при `=1` отказывает объектному порту в создании
  (`INVALID_PARAM`) и контексту без устройства (`OUT_OF_RESOURCE`), а `SetAttributes` — при повторе id, `nullptr`,
  неверном размере; у нас коды игре при `=1` те же, что при `=0` (`OK`), неверный атрибут молча не применяется
  (усиление и амбисоника порта остаются прежними), PCM того же вызова применяется. Довод: смесь не требует менять
  ответы игре; новый код отказа меняет путь игры, а не вывод.
- **D3 `GAIN` (id 1) — только объектным портам при `=1`:** `value != nullptr`, `value_size == 4` (моно), значение
  конечное и ≥ 0 — иначе не применяется; хранится в порте (держится до следующей записи), умолчание 1.
- **D4 `AMBISONICS` (id 8) — только объектным портам при `=1`:** `value_size == 4`, допустимы `UINT32_MAX`, 0…15,
  64…99 (как upstream), иначе не применяется; умолчание `UINT32_MAX`.
- **D5 «Заморозка» атрибутов upstream (`attributes_locked` до `ContextAdvance`) — не берётся.** Она не часть смеси, а
  правило времени атрибутов; если игра зовёт `ContextAdvance` не на каждой грануле (частота вызова в журнале не видна —
  [U]), заморозка держала бы усиление голоса на первом значении до конца его жизни. Без неё последний `GAIN` до Push
  действует. Блок теста upstream с заморозкой стендом не воспроизводится (названо).
- **D6 Устройство смеси** — одно на контекст при `max_object_ports > 0`, тип MAIN, стерео float 48 кГц, `num_grains`
  кадров; открывается тем же `AudioInternal::AudioOutOpen` → `Audio::OpenSdlDevice` → `SdlAudioSubsystemInit` →
  владелец подсистемы Ф8 `SdlAudioAcquire` (`init_calls` не растёт). Задаёт ли игра `max_object_ports > 0` — [I]
  (`ContextResetParam` даёт 256, правку игры перед `ContextCreate` не разбирал; при 0 смеси нет и член (г)(2)(v)
  `mixed_nz` ≥ 1 провалится — это и будет ответом).
- **D7 Замки.** Смесь считается под `g_audioout2_port_mutex` (как отбор портов шин), ручка устройства читается под
  `g_audioout2_context_mutex` отдельно и раньше (порядок «контекст, затем порт» — как в `PortCreate`; одновременно оба не
  держатся в новом коде). `AudioOutOutputs` — вне замков, как в MS1. Буфер смеси — локальный вектор вызова (SDL копирует
  данные в `SDL_QueueAudio`).

## 5. Путь пада

`dualSenseHaptics` в нашем дереве нет; вибрация идёт `Audio::AudioOutOutputs` → `Controller::PushHapticsPcm` для портов
`AUDIO_OUT_PORT_TYPE_VIBRATION`. Поле усилений смеси паду не нужно (смесь объектов идёт на порт MAIN, `GAIN` шин не
применяется) ⇒ путь пада не меняется ни при `=0`, ни при `=1`; `audio.cpp` и `audio_internal.h` правкой не тронуты.

## 6. Стенд и мутанты (члены (г)(2)(i)–(ii))

Стенд `tests/MT125Stand.cpp` без игры: подмена `AudioInternal::AudioOutOpen/Close/HasDevice/AudioOutOutputs`
(ловит параметры вывода), настоящий `libAudio2.cpp`. Плечи: `=0` и `=1` (два процесса, ручка — окружение).
Сцена: контекст `max_object_ports` = 8, 4 порта шин (стерео float, разный синус) и N = 3 объектных (моно float 48 кГц,
синусы 220/330/440 Гц, `GAIN` 0,25 / 0,5 / 1,0), Push × 4. Члены: при `=0` — число выводов на Push = 4, объектного PCM в
выводе 0; при `=1` — 5 выводов, 4 первых байт в байт как при `=0` (sha256 по Push), 5-й — смесь, равная эталону
(Σ gain·hp·x, допуск 1e-6); кейсы `TestObjectGainAndAmbisonics` (таблица амбисоники × `GAIN` 0,5, нулевой `GAIN` глушит,
`GAIN` держится, s16 и float, без накопления между Push); формат: порт 0x100 с 44 100 Гц / стерео / 0x101 — правило D3;
счётчики `mixed`/`mixed_nz`. Мутанты (сборкой с `-DKYTY_M125_MUT=<k>`): m1 «смесь без `GAIN`», m2 «без проверки формата
данных порта», m3 «смесь при `=0`», m4 «один из N объектов потерян» — каждый обязан провалить ≥ 1 член стенда.
