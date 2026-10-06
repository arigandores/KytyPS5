"""F20l2: seal body additions before the seal (2026-10-06 ~19:55Z): run check of item 587 (g) in section 1, the four fixtures added
after the first sens run in section 6, the parked rule of item 587 (v) in section 3.  UTF-8, LF kept."""
import sys

P = 'C:/kyty/f287/f20l2/f20l2_seal_body.md'
s = open(P, 'rb').read().decode('utf-8')
assert '\r\n' not in s


def rep(old, new):
    global s
    if s.count(old) != 1:
        print('anchor count %d: %r' % (s.count(old), old[:60]))
        sys.exit(1)
    s = s.replace(old, new)


rep("- Порядок: `b32_z0b`, `b32_ppb`, `b32_pcb`.",
    "- **Проверка живости прогона (долг п. 587(г), выбор исполнителя):** после `procload.py` и до взятия замка `go_f20l2.sh` зовёт\n"
    "  `runchk_f20l2.py` — у `HPP-648` идёт прогон (`executionRunId`), равный `F20L2_RUN_ID`, который `launch_f20l2.sh` передал из\n"
    "  `PAPERCLIP_RUN_ID`, и статус `in_progress`; иначе (`RUN GONE`, `API ERROR`) — тег не стартует, каталог `<тег>.gone_*`, попыткой не\n"
    "  считается (отменённый прогон агента не останавливает отсоединённый вызов тега — п. 587(г)).\n"
    "- Порядок: `b32_z0b`, `b32_ppb`, `b32_pcb`.")
rep("Бюджет замка — п. 574(е): контрольных тегов 5 + 3.",
    "Бюджет замка — п. 574(е): контрольных тегов 5 + 3. Выбор, записанный в этой печати, исполнитель не меняет без пункта лида; при\n"
    "сомнении — вопрос лиду до действия (п. 587(в)).")
rep("регрессия ридера на логах F20e. Счёт проверок и sha256 выводов — строки `seal:` ниже.",
    "регрессия ридера на логах F20e. Первый прогон `sens_b32.py` (19:47Z) пропустил 4 правки из 111 (`theta not an admission member`,\n"
    "`gpu member S off`, `ring_hold_w sum off`, `admission loader mode not checked`) — ридер не менялся, в `test_b32_read.py` добавлены\n"
    "фикстуры: строка допуска «`θ_load` из печати» сама — FAIL без строки; шаг на GuestGpu с `S` = 40 из 40 (не `Sw`) — член «да»;\n"
    "накопленный `ring_hold` строки `-x` отличен от `ring_hold_w` и в сумму не идёт; справка `b32_pd` с нагрузчиком `half` — FAIL; второй\n"
    "прогон — 0 пропусков. `test_tools_f20l2.py` — и фикстуры `runchk_f20l2.py` (живой прогон, нет прогона, чужой прогон, статус не\n"
    "`in_progress`, пустой `F20L2_RUN_ID`, нечитаемый ответ). Счёт проверок и sha256 выводов — строки `seal:` ниже.")
open(P, 'wb').write(s.encode('utf-8'))
print('body patched')
