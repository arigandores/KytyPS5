"""S18a2 (HPP-650): appends the section '## S18a2' to C:/kyty/s288/FACTS.md (LF, once)."""
import sys

P = 'C:/kyty/s288/FACTS.md'
NL = chr(10)
SECTION = NL.join([
    '',
    '## S18a2 — правка RC1 S18b: закрытие окна на экране подготовки без перестройки = FS8 (Emu Engineer, `HPP-650`, п. 576(б)–(г))',
    '',
    '- Время по `date -u`, файл `C:/kyty/s288/s18a2/times.txt`: старт 06:54:16Z; коммит в `main` 06:55:17Z; cherry-pick 06:55:28Z;',
    '  сборки 06:55:54Z–06:57:41Z; `chk576.py` 06:58:26Z; набор тестов 06:59:02Z. Замка не было; звеньев Harness Engineer `in_progress` 0.',
    '- **Код:** коммит `main` `7c31481b`, cherry-pick в worktree `C:/kyty/s288/s18a/wt` — HEAD `0005e11fee90bc42b51960573bfbb14f55694b4c`',
    '  (родитель `62ff7b5b`). `ReplayCloseStop`: при `!RebuildOn() || !m_replay_rebuild` — возврат сразу, без `m_precache_stop`, без `join`,',
    '  без строк `close stop` (путь FS8); при перестройке — `m_precache_stop` и опрос раз в 1 мс флага `m_replay_rebuild_done`, который поток',
    '  прекэша ставит сразу после возврата `ReplayRebuild`; фазу `PrecachePipelines` закрытие не ждёт, `join` нет; тексты строк прежние;',
    '  перестройка уже кончилась — те же строки, `wait_ms=0`. Стенд `stop` не менялся. Комментарии — `pipelineCache.cpp/.h`, `window.cpp`, `shaderReplay.cpp`.',
    '- **Бинарь:** `C:/kyty/s288/bin/kyty_emulator_b3cee576.exe`, sha256 `b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a`,',
    '  строка версии `KytyPS5-2026-09-15-6a2987a-1897-g0005e11f` (2 вхождения, одинаковые, после повторного configure); бинарь тестов',
    '  `shader_cfg_tests_27f69093.exe`. Игрой не проверялся (S18c). Установленный FS8 `2c9b69b9…` не тронут.',
    '- **Члены п. 576(г)(4)** (`chk576.py` `ALL OK`): `patch-id --stable` `7c31481b` = `0005e11f` (`643af5ff…`); `git diff 7c31481b 0005e11f`',
    '  по 6 путям кода — 24 строки `-` чужих коммитов (`381aa80a` 9, `9bd96f44` 6, `1d8d9aa6` 9), прочих 0; коммитов кода в `main` между',
    '  `fe4b227a` и `7c31481b` 0; К1(7) `302347b4..0005e11f` пуст; `9177b426…` — 1 вхождение в exe (и в S18a, и в FS8); `check_gate_order.py`',
    '  clean, вывод worktree = `main`; `shader_cfg_tests` rc 0, 133 теста, 0 строк `failed:`, SPIR-V 180/180 = S18a. Модельный тест не делался —',
    '  член решения закрытия — код S18b2.',
    '- Отчёт `docs/track-s/s18a2/report.md` (KytyPS5), скрипты и выводы — `C:/kyty/s288/s18a2/`, копии — `docs/track-s/s18a2/`.',
    '',
])


def main():
    raw = open(P, 'rb').read()
    text = raw.decode('utf-8')
    if '## S18a2 ' in text:
        print('already present')
        sys.exit(1)
    if not text.endswith(NL):
        text += NL
    open(P, 'wb').write((text + SECTION).encode('utf-8'))
    print('appended')


if __name__ == '__main__':
    main()
