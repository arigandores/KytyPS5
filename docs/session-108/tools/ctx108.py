"""Session 108 close: the game contexts (CLAUDE.md = AGENTS.md in the emulator folder). One-shot."""
from pathlib import Path
root = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')
p = root / 'CLAUDE.md'
lines = p.read_text(encoding='utf-8').split('\n')


def block(start_prefix):
    """index range [i, j) of the paragraph starting with start_prefix (ends at the next blank line)"""
    i = next(k for k, l in enumerate(lines) if l.startswith(start_prefix))
    j = i
    while j < len(lines) and lines[j].strip():
        j += 1
    return i, j


state = """**СОСТОЯНИЕ (2026-09-23): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд до «стоп», вопросов не задавать,
после исчерпания лимитов продолжать; push — нет). Хартбит — cron в беседе (:17 и :47); во время запечатанного
прогона он не делает ни одного вызова инструментов; все цепочки прогонов держат замок `C:/kyty/SEALED_RUN.lock`;
состояние для хартбита — `C:/kyty/LOOP_STATE.md`. **Сессия 108 закрыта**, следующая — `docs/next-session-109.md`
(`cspfam` v2 со стражем в силе, затем `QueueDrawAhead` вне `m_mutex`). Решения после с. 106–108 (`ROADMAP.md` §0.1)
действуют: фикстуры — на каждый член и ветку; перед предложением ручки — её ТЕКУЩЕЕ умолчание в `gates.cpp`; страж
обязан иметь экспозицию (precache compute выкл). **Скорость игры = 16 667 / mean `dt_us`. 60 FPS не обещать.**"""
i, j = block('**СОСТОЯНИЕ НА ПАУЗЕ')
lines[i:j] = state.split('\n')

s108 = """Дата: 2026-09-23. **Сессия108: `cspfam=4` ДАЛ Δ СРЕДНЕГО КАДРА −141,8 МКС ПРИ ПИНЕ И БЫЛ ОТГРУЖЕН, НО СТРАЖ В СИЛЕ
(PRECACHE COMPUTE ВЫКЛ) ПРОПУСТИЛ 6 СИНХРОННЫХ КОМПИЛЯЦИЙ ПРОТИВ 3 ⇒ УМОЛЧАНИЕ ОТКАТАНО К 0; УСКОРЕНИЯ НЕ ОСТАЛОСЬ.**
Возобновлена после паузы: порт `s108` (`s108_port.py` `cb104f40`, 50 печатей), 103 фикстуры `fam108.py` (все члены
поодиночке), печать `pred/01_cspfam.md` (`a40cf056`). `fam108` (ABBA `cspfam=0|4`, 600 с, пин, 96 пар): SHIP, Δ`dt`
−141,8 (2·SE 107,0, t −2,65; CI [−246; −38]; выигрыш — больше одновблэнковых кадров 13,25 → 13,97 %), видео чистое;
умолчание 4 (`eed387b`, сборка `fc78c564`, видео `vid108` чистое). Аудит (печать `pred/02_audit108.md` `401a76cc`):
пересчёт CONFIRMED, протокол HOLDS, код NOT REFUTED; **MAJOR — страж `cs_sync_new` и пустыня без силы** (стартовый
precache строит все 121 compute-пайплайна). Проверка в силе (`KYTY_PIPELINE_PRECACHE=gfx`): `sf108c` (0) — `cs_sync_new`
3 (первый положительный контроль), `sf108d` (4) — 6 > 3 + 2 ⇒ **откат `cspfam` к 0** (`01f0c79`, сборка
**`379777bb…`** установлена, видео `vid108r` 3 933 кадра, 0 глитчей). Убиты осиротевшие `tail -F`/`grep` сессий
102–105; хартбит больше не выполняет команд во время прогона. Источник истины — `C:/kyty/s108/FACTS.md`, в git
`docs/local-session-108.md`."""
i, j = block('Дата: 2026-09-23. **Сессия108 (WIP')
lines[i:j] = s108.split('\n')

env = """- Сто восьмая сессия (**ручка построена, отгружена и откатана; умолчания поведения = с. 107**): ручка **`cspfam`**
  (`KYTY_CS_PREFETCH_FAMILY`, 0..1024, **умолчание 0** — было 4 между `eed387b` и `01f0c79`; ПОСЛЕДНЯЯ строка ручек;
  значение = K): префетч compute на потоке обхода возвращается до `PipelineCache::m_mutex`, если у семейства шейдера
  (хэш/база кода + статический ключ стадии) последние K захваченных префетчей, увиденных ПРИ `cspfam` ≠ 0, нашли
  готовый пайплайн, а зеркало `programs_epoch` и `ShaderRegistrations()` не сдвинулись (при `cspfam` = 0 таблица
  заморожена); счётчики `FrameTrace-x` `cspfam_look`, `cspfam_skip`. **Страж (только при `KYTY_FRAME_TRACE`):**
  `cs_sync_new` (в `GetComputePipeline` пайплайна нет — синхронная компиляция на диспатче), `cs_sync_wait`
  (недостроенная запись — ожидание). **Страж без экспозиции слеп:** стартовый precache строит все известные
  compute-пайплайны, поэтому первую встречу проверять с `KYTY_PIPELINE_PRECACHE=gfx`. `cspfam` — 39-е имя вне
  `gates_base.txt`; `gates.cpp` даёт 138 записей (111 + 27). Харнесс `C:/kyty/s108`: `fam108.py`/`make_fam108.py`/
  `test_fam108.py` (103 фикстуры), `check108.py`/`check108r.py` (видео сборки, привязаны к sha), `go108*.sh` (все
  держат замок `C:/kyty/SEALED_RUN.lock`), `gates_fam0.txt`/`gates_fam4.txt`, `audit108/`, копии оцененных сборок
  `kyty_emulator_fd1d0bd7.exe`/`kyty_emulator_fc78c564.exe`."""
i = next(k for k, l in enumerate(lines) if l.startswith('- Сто восьмая сессия ('))
j = i + 1
while j < len(lines) and lines[j].startswith('  '):
    j += 1
lines[i:j] = env.split('\n')

text = '\n'.join(lines)
p.write_text(text, encoding='utf-8')
(root / 'AGENTS.md').write_text(text, encoding='utf-8')
print('ok', len(text))
