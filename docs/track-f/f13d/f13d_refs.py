# F13d (HPP-485): reference map of the review - each <commit>:<path>:<line> checked by anchor (substring of the line) and +1
# (substring of the next line) against `git show <commit>:<path>` (general rule 24(1)).  Prints ALL OK or the failures.
import subprocess, sys

REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('c5bff245', 'docs/ROADMAP.md', 21235, '395. **Звено F13c трека F (`HPP-484`, лид): F13a (`HPP-479`) и F13b (`HPP-483`) ПРИНЯТЫ',
     'по картинке: чёрный кадр даёт константа полноэкранного затемнения игры'),
    ('c5bff245', 'docs/ROADMAP.md', 21264, '(б) **Звено F13d (Red Team, `todo`, стадия review лида)', '`C:/kyty/f287/f13b/`), F13a'),
    ('c5bff245', 'docs/ROADMAP.md', 21278, '(в) **Звено F13e (лид, `blocked` на F13d) — приёмка отзыва; правило решено сейчас:**',
     'Б41 `НЕ ДЕФЕКТ` (картинка: кадр гостя воспроизведён [c снимка и реплея]'),
    ('c5bff245', 'docs/ROADMAP.md', 21306, '(з) **Не заявляется:** что чёрный экран `ending_boss_after_credit` — не дефект до F13e',
     'почему игра не переходит дальше'),
    ('0ba742fb', 'docs/track-f/f13b.md', 14, '1. Чёрный кадр даёт **сама игра константой полноэкранного затемнения**',
     'сцену с цветом (0, 0, 0) с весом `1,0`'),
    ('0ba742fb', 'docs/track-f/f13b.md', 103, '2. **Полноэкранное затемнение** — **да, константой игры** (§3)',
     'осмысленная кривая тонмаппинга [c снимка]; что значение записала логика игры'),
    ('0ba742fb', 'docs/track-f/f13b.md', 108, '4. **Пропущенные draw** — 22 draw гостя на флип',
     'Vulkan (7 `vkCmdDraw*` + 2 меш-задачи). Тихие выходы'),
    ('0ba742fb', 'docs/track-f/f13b.md', 112, 'Какие из 13 «лишних» — снимок не показывает.',
     'выход финального прохода при весе 1 не зависит ни от сцены, ни от оверлея'),
    ('0ba742fb', 'docs/track-f/f13b.md', 133, 'значит, на Cross и Circle игра здесь не отвечает [c]', ''),
    ('0ba742fb', 'docs/track-f/f13b.md', 135, '**Чтение:** игра после карточки «THE END» сама гасит кадр затемнением',
     'последовательности при прямом входе `-lvl`, где игре некуда возвращаться [I]'),
    ('0ba742fb', 'docs/track-f/f13b.md', 137, 'Ждёт ли игра системного события (сохранение, трофей, диалог)',
     'HLE после карточки в логах нет [c] (журнал имён HLE в этой форме неполон'),
    ('84c1f78c', 'docs/track-f/f13a.md', 173, '**Данные к вопросу «ждёт ли игра ввода»:**',
     'Что нажатие дошло до игры как кнопка геймпада, лог не показывает'),
    ('ded0daf2', 'src/loader/runtimeLinker.cpp', 405, 'const auto log_index = g_unresolved_stub_call_log_count.fetch_add(1);',
     'if (log_index < 1024) {'),
    ('ded0daf2', 'src/libs/libSystemService.cpp', 146, 'static int KYTY_SYSV_ABI SystemServiceReceiveEvent(SystemServiceEvent* event) {',
     'PRINT_NAME();'),
    ('ded0daf2', 'src/libs/libSystemService.cpp', 156, 'return SYSTEM_SERVICE_ERROR_NO_EVENT;', '}'),
    ('ded0daf2', 'src/libs/libSaveData.cpp', 724, 'LOGF("\\t user_id  = %" PRId32 "\\n"', '"\\t data     = 0x%016" PRIx64 "\\n"'),
    ('ded0daf2', 'src/libs/libSaveData.cpp', 728, '"\\t data_num = %" PRIu32 "\\n"', '"\\t slot_id  = %" PRIu32 "\\n",'),
    ('ded0daf2', 'src/libs/libNet.cpp', 2392, 'LOGF("\\t event_name = %s\\n"', '"\\t prop       = 0x%016" PRIx64 "\\n"'),
    ('ded0daf2', 'src/libs/libNet.cpp', 2407, 'LOGF("\\t context = %d\\n"', '"\\t handle  = %d\\n"'),
    ('ded0daf2', 'src/libs/libs.h', 53, '#define PRINT_NAME()', 'static const bool print_name_forced = Common::EnvFlagOn("KYTY_PRINT_NAMES");'),
    ('ded0daf2', 'src/kernel/pthread.cpp', 3287, 'KYTY_PRINT_NAMES_THREADS=<name>[,<name>...]: PRINT_NAME on the listed guest threads only.', ''),
]
bad = 0
for c, p, n, a, b in REFS:
    lines = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True, check=True).stdout.decode('utf-8').split('\n')
    ok_a = a in lines[n - 1]
    ok_b = (b in lines[n]) if b else True
    print('%s %s:%s:%d anchor=%s +1=%s' % ('OK ' if ok_a and ok_b else 'BAD', c, p, n, ok_a, ok_b))
    bad += not (ok_a and ok_b)
print('ALL OK' if bad == 0 else 'FAIL %d' % bad)
