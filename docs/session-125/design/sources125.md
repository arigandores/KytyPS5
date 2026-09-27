# Источники проекта `design125.md` (Probe Designer, `HPP-73`, ред. 1)

Все числа ниже — чтение существующих файлов; ни одна игра и ни один бенч не запускались.

## Код и документы (sha256 на момент чтения; HEAD репозитория `eb51a30a`)

| файл | sha256 | что взято |
|---|---|---|
| `src/graphics/guest_gpu/graphicsRun.cpp` | `e3f945196bb972d041ce8996fc6739d9b9a647bdccc410e5b9e5f1061910fe1a` | `SpineRegs` :1586–1595, `SpinePlan` :1597–1944 (засев :1662–1674, классы пакетов :1722–1900, побочный эффект элемента :1893–1895), срезы подач :1143–1166 |
| `src/graphics/guest_gpu/command_processor/commandProcessor.h` | — | `m_ctx` :227, `m_saved_ctx` :228, `m_const_ram[0x3000]` :245, `m_spine` :259 |
| `src/graphics/guest_gpu/graphicsRun.h` | — | `ComputeQueueCount` = 7 × 8 = 56, `QueueCount` = 57 (:49–53) |
| `docs/DESIGN_82_parallel.md` | `7a53a958c9291d997b2593162f1070804e15da660a3712d0f0e711862238929b` | §1 A′ (снимок 6 803 Б на точку форка), §2 (схема, классы (a)/(b)/(c)), шаг 2 (`cram_write`) |
| `docs/session-117/designA4_spine.md` | — | §0 «Each slice needs the full register state at its start» |
| `docs/session-118/designA4_part2.md` | `168e8276528192d3f5cecb7e1e4a3447aacbf6f0f3e0d141098308307c82159f` | §1 перенос («the walker … will not be seeded»), §2 безопасный план, §3 K4: кадр режется на W = 2 сегмента у начала прохода |
| `docs/session-120/audit/closure.md` §6 | — | происхождение «≈ 97 нс на операцию» = 485 мкс / ≈ 5 000 операций (бюджет, не измерение) |

## Запечатанные логи

| лог | sha256 | роль |
|---|---|---|
| `C:/kyty/s119/log_sh119.txt` (211 079 139 Б) | `fe8b0e2373a9f6daa1dc072b46212309d8a74558a97affdeb639f9ef11b8f0ba` | популяция `g2_119`, плечо 0 `shadowresolve=0` |
| `C:/kyty/s119/log_mut119.txt` (203 467 994 Б) | `2b0adcb807055d736e89338aced5f39b4bd682c50d98e142799c847622eec8c8` | популяция `g2_119`, плечо 0 `mutwide=0` |
| `C:/kyty/s118/log_spk118.txt` (209 913 488 Б) | `2248dbc66604974fe78196f73232d42e5b9d5ac2a7c7daa6b782fa0a1b7b3a68` | строка `Spine: mode=2 snap=4096 ctx=2672 ucfg=148 sh=1208` (другой источник — В2) |

## Проверки чтением (все строки лога, без окна и без плеча — справочно; скорер шага 3 считает по окну 10–88 плеча 0)

| лог | `cram_write` сумма | строк с `slc_total` | среднее `slc_total` | максимум `slc_total` |
|---|---:|---:|---:|---:|
| `log_sh119.txt` | 0 | 9 570 | 12,64 | 23 |
| `log_mut119.txt` | 0 | 9 508 | 12,64 | 24 |

Одна строка (`FrameTrace-draw` № 3000 `sh119`): `bda_n=171 bda_scan=50` — режим NEW (полоса ≤ 300, п. 40(е)(1)).
Печать `g2_119` (`C:/kyty/s119/runs119/g2_119_score.txt`, окно 60–88): плечо 0 `sh119` `draws` 5 013,0, `dispatches`
268,0; `da_wjobs` = 8 в строке `FrameTrace-x` № 3000.

Машина: `AMD Ryzen 9 9955HX3D`, 16 ядер / 32 логических CPU (`Win32_Processor`), два CCD.

## Редакция 2 (`HPP-79`, шаг 2а п. 57(з); HEAD репозитория `b6bf8c41`)

Ни игра, ни бенч не запускались; ниже — чтение кода и существующих файлов.

| файл | sha256 | что взято |
|---|---|---|
| `src/graphics/guest_gpu/graphicsRun.cpp` | `e3f945196bb972d041ce8996fc6739d9b9a647bdccc410e5b9e5f1061910fe1a` (не менялся с ред. 1) | `GuestGpu::Enqueue` :661–676 (`enqueue_ns` :669, `LookaheadSubmission` :663), `Process` :940–958 (`first_slice`, `KYTY_LAG_TRACE`), срезы :1143–1175, обходчик :2330–2420 (удержание `dawalklead` :2382–2395, `da_wlag_us` :2408, `da_wdepth` :2409), `DrawAheadWalkerPost` :2438–2466 (`enqueue_ns` :2458), `LookaheadSubmission` :2649–2661 |
| `src/graphics/presentation/videoOut.cpp` | `5a389d7ed18a7fcf2c909dc9a759d14223a9cdc16ec7e6daec90ed22fa9a6763` | `FlipQueue::Reserve` :888–915 (`reserve_host_ns` :900), `lat_us` :1311–1313, `VideoOutSubmitFlip` :3385, `SubmitFlipFromGpu` :3401, `WaitFlipDone` :3439 |
| `src/graphics/host_gpu/renderer/sync.cpp` | `1d4539d1032e10870d1d43a542eb265943276f787a615dddca086f122269a166` | `PrepareVideoOutFlip` :228–234 — флип пакетом DCB резервируется потоком GuestGpu (источник `GpuEop`) |
| `src/libs/agc.cpp` | `0b1474d766bf347425ad31521285f06ff6f3ef57ef588f8eec06cbe7d7411cec` | `AgcDcbWaitUntilSafeForRendering` :2167, `AgcDriverSubmitAcb` :4337 — `LOGF` без метки времени |
| `src/common/frameStats.h` | `5a783b8fb699626465214acef39b2bfbcc6350570e6e24d2da3ee333ccd47a4f` | `DrawAheadWalk*` :523–527, `GpuWallIdleNs` :1758 |
| `C:/kyty/s119/runs119/g2_119_score.json` | `85f3364359b31fb24b5868ed5ab1b884b552482a3d38c286e461a28c4374b8ae` | запечатанная печать `g2_119`: `terms.cpu_net` 30 252,517, `central.S_ctx` 18 724,194, `central.G` 2 216,540, `terms.spine` 1 268,172, `central.T4` 1 645,391, `F` 0,555 |
| `C:/kyty/s119/log_sh119.txt`, `log_mut119.txt` | как выше | ряды §3.4/§3.7 |
| `docs/session-125/design/rows125.py` | `f890142dcf6e48330e4e75a3250f7775f66c56796a3a5352aa31dd6dd5bfceaf` | пересчёт рядов §3.4/§3.7: плечо 0, окно idx 10..88 (п. 55(б)), исключённые блоки как `g2_119`; номер блока — поле `blk` основной строки `FrameTrace` (черновая арифметика [I], ничего не решает) |

Ряды (`rows125.py`, 3 239 строк × 41 блок в каждом прогоне):

| поле | `sh119` | `mut119` |
|---|---:|---:|
| `cpu_gpu_us / dt_us` среднее / медиана | 0,950 / 1,0 | 0,953 / 1,0 |
| `dt_us − cpu_net` среднее, мкс | 1 261 | 1 209 |
| `lat_us` среднее, мкс | 11 271 | 11 592 |
| `da_wjobs` / `da_wdrop` / `da_wskip` на кадр | 7,94 / 0,04 / 7,97 | 7,94 / 0,04 / 7,97 |
| `da_wlag_us` / `da_wjobs`, мкс | 9 061 | 9 326 |
| `da_wdepth` / `da_wjobs` | 2,23 | 2,23 |
| `slc_total` среднее | 12,58 | 12,57 |
| `bda_scan` среднее | 56,9 | 55,8 |
| `gw_idle_ns` | 0 | 0 |

`gw_idle` 28 мкс/кадр — `obs116` (`ROADMAP.md` «СЕССИЯ 116» п. 6, режим NEW), иной прогон: только ряд §3.7, в печать не идёт.
