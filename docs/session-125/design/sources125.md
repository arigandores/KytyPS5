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
