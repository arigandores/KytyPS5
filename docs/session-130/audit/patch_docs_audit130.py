# -*- coding: utf-8 -*-
"""s130 audit (HPP-153): Step 9 appended to C:/kyty/s130/FACTS.md; status paragraph into ps5 em CLAUDE.md and AGENTS.md
(byte-identical after) above the s129 closure paragraph; platform traps 8 and 9 (full text in docs/platform-traps.md, one
line in CLAUDE.md/AGENTS.md); HANDOFF entry after the s129 closure entry. Whole-line anchors, each counted exactly once;
LF; write_bytes. Port of audit129/patch_docs_audit129.py."""
from pathlib import Path

A = Path('C:/kyty/s130/audit130')
F = Path('C:/kyty/s130/FACTS.md')
D = Path('C:/kyty/KytyPS5/ps5 em')

STATUS = ('Дата: 2026-09-29. **Сессия 130 — АУДИТ (шаг 9, `HPP-153`, объём п. 122(е)): ЧТЕНИЕ п. 116(е)/118(б) ПЕРЕСЧИТАНО '
          'СВОИМ ПАРСЕРОМ — CONFIRMED ДО ЕДИНИЦЫ; 0 MAJOR / 2 MINOR; `CBAD_LOSS` ⇒ `ARMCOPY_INCORRECT` СТОИТ.** Опора '
          '`s10s130` (сборка `3f4af2c3`, ABBA `armcopy=2|4`): H₂ = 9, H₄ = 0 (все строки блоков плеча и окно 10–88 п. 55(б); '
          'все 9 — одна строка n = 2516, блок 7, p = 85, 9 смежных страниц); пустыня `s11s130` 0/0; стражи при 2 — 0; И1–И3, '
          'И8 построчно и И4 по блоку — 0 нарушений; пересчёт п. 119(в) — тот же исход; контроль `s12s130` жив. Шаг 0в '
          'пересчитан до цифры (3,183 / 3,068; 0,981), установленная `9235a7ac` (sha аудита), умолчания в дереве `armcopy` 0, '
          '`acinline` 0. Протокол п. 116–122: решение до действия по порядку коммитов, поправки до данных, одна попытка, замок '
          'до `procload`, бюджет мутантов ≈ 4 621 из 4 800 с — чисто. MINOR: время решения в тексте п. 116/116(л)/118/120 позже '
          'коммита пункта (1–13 мин); пересчёт лида п. 122 относит строку n = F к новому блоку (±396 страниц, исход тот же). '
          '«Процесс» — 5 пунктов (шаг 1: 77 мин мутантов; эскалация на третьем «Доработать»; cp1250; работа рычага до '
          'доказательств отгрузки; время решений). **НЕ доказано:** что `armcopy` теряет записи (H ≠ потеря, Р8 [U]) или не '
          'теряет; OLD; `acinline`. Числа скорости в с. 130 нет. Аудит — `C:/kyty/s130/audit130/AUDIT130.md` (git '
          '`docs/session-130/audit/`). Закрытие — `HPP-154`.\n')
ANCHOR = 'Дата: 2026-09-28. **Сессия 129 ЗАКРЫТА: `ARMCOPY_GAIN`'

TRAP_LINE_OLD = '  (п. 16); перед `git commit` агента выставить `GIT_AUTHOR_*`/`GIT_COMMITTER_*` в том же вызове шелла.'
TRAP_LINE_NEW = ('  (п. 16); перед `git commit` агента выставить `GIT_AUTHOR_*`/`GIT_COMMITTER_*` в том же вызове шелла;\n'
                 '  (8) третье «Доработать» одного звена эскалирует review на доску — доработка сверх второй новым звеном '
                 '(п. 115);\n'
                 '  (9) Python с кириллицей в выводе — `export PYTHONIOENCODING=utf-8` (консоль cp1250, с. 130 p7).')

TRAPS = (
    '- **Ловушка платформы 8 (2026-09-29, `HPP-142`, `ROADMAP.md` «СЕССИЯ 122» п. 115): третье «Доработать» одного звена\n'
    '  эскалирует стадию review на доску.** После третьего запроса изменений (`changesRequestedCount` 3) платформа ставит\n'
    '  `currentParticipant` = пользователь и снимает исполнителя; лид больше не может вернуть звено исполнителю — отказ\n'
    '  «Only the escalated reviewer can advance the current execution stage». Пользователя не просить (п. 16). Выход —\n'
    '  новое дочернее звено с тем же заданием и перевод блокеров на него (шаг 1б с. 130); правило лида — третьего\n'
    '  «Доработать» не выдавать, доработка сверх второй — новым звеном с явными блокерами (п. 115(г)).\n'
    '- **Ловушка окружения агентов 9 (2026-09-29, с. 130 шаг 1б, аудит `HPP-153`): Python печатает в консоль cp1250.**\n'
    '  `print` строки с кириллицей (в консоль или через перенаправление в файл) падает `UnicodeEncodeError: \'charmap\'\n'
    '  codec can\'t encode character`. В с. 130 так упал драйвер мутантов цепочки (часть p7): состояние не записалось,\n'
    '  вердикты части потеряны, 338 с стены. Запускать Python с `export PYTHONIOENCODING=utf-8` (или писать файлы\n'
    '  с `encoding=\'utf-8\'`). Та же кодировка портит кириллицу в аргументах командной строки (`curl -d`) — тело JSON\n'
    '  собирать в Python и передавать через stdin.\n')

HAND = ('Дата: 2026-09-29. **Сессия 130 — аудит (шаг 9, `HPP-153`; объём `ROADMAP.md` «СЕССИЯ 122» п. 122(е); источник истины — '
        '`docs/local-session-130.md`, раздел Step 9).** Шаги 7–8 (`ai130` и др.) отменены п. 122 после `CBAD_LOSS`. '
        'Пересчёт своим парсером — CONFIRMED до единицы: `s10s130` H₂ = 9 / H₄ = 0 (одна строка, 9 смежных страниц), '
        '`s11s130` 0/0, стражи при 2 — 0, тождества — 0 нарушений, п. 119(в) и окно 10–88 — тот же исход, контроль '
        '`s12s130` жив; шаг 0в — до цифры (3,183 / 3,068; 0,981); установленная `9235a7ac`. 0 MAJOR, 2 MINOR (время '
        'решения в тексте п. 116/116(л)/118/120 позже коммита; отнесение строки n = F в пересчёте лида), вердикт '
        '`ARMCOPY_INCORRECT` не меняется. «Процесс» — 5 пунктов; ловушки платформы 8 и 9. Не доказаны: потеря/не-потеря '
        'записей (Р8 [U]), OLD, `acinline`. Закрытие — `HPP-154` (лид).\n\n')
H_ANCHOR = 'Дата: 2026-09-28. **Сессия 129 ЗАКРЫТА (`HPP-139`, лид;'


def patch_claude(name):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    assert chr(13) not in t, name
    assert 'Сессия 130 — АУДИТ' not in t, name
    assert t.count(TRAP_LINE_OLD + '\n') == 1, name
    t = t.replace(TRAP_LINE_OLD + '\n', TRAP_LINE_NEW + '\n')
    lines = t.split(chr(10))
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, (name, idx)
    lines.insert(idx[0], STATUS.rstrip(chr(10)))
    lines.insert(idx[0] + 1, '')
    p.write_bytes(chr(10).join(lines).encode('utf-8'))


# FACTS: append Step 9
ft = F.read_bytes().decode('utf-8')
assert chr(13) not in ft and ft.endswith(chr(10))
assert '## Step 9' not in ft
sec = (A / 'facts_step9.md').read_bytes().decode('utf-8')
assert chr(13) not in sec
F.write_bytes((ft + sec).encode('utf-8'))

assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
for n in ('CLAUDE.md', 'AGENTS.md'):
    patch_claude(n)
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'docs/platform-traps.md'
t = p.read_bytes().decode('utf-8')
assert chr(13) not in t and t.endswith(chr(10))
assert 'Ловушка платформы 8' not in t
p.write_bytes((t + TRAPS).encode('utf-8'))

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
assert chr(13) not in t
assert 'Сессия 130 — аудит' not in t
lines = t.split(chr(10))
idx = [i for i, l in enumerate(lines) if l.startswith(H_ANCHOR)]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + 1] == '', repr(lines[i + 1])
lines.insert(i + 2, HAND.rstrip(chr(10)))
lines.insert(i + 3, '')
p.write_bytes(chr(10).join(lines).encode('utf-8'))
print('ok')
