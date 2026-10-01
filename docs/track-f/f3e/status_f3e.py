"""F3e (HPP-343): track F status line in ps5-em CLAUDE.md == AGENTS.md, FACTS.md section, times.txt lines. LF, write_bytes; aborts on lock."""
import os, pathlib, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
D = pathlib.Path('C:/kyty/KytyPS5/ps5 em')
old = ('`HPP-342` F3d (Harness Engineer, после `HPP-333`) → `HPP-343` F3e (лид); ')
new = ('`HPP-342` F3d (Harness Engineer, после `HPP-333`) → **F3e (`HPP-343`, п. 282, `cc9880e6`): Б1б и Ф9 `FIXED` — на 6 входах `KYTY_FIX_B1B=1` пар «X / X>>8» 0, '
       '`BvhLoopCapTrip:` 0, смертей 0, K2 0, видео 3 454 / 7 510 / 8 574 кадров 0 глитчей, W 0 `[Vulkan][E]`, контроль `=0` возвращает пары; листы лида — видимых дефектов нет; '
       'звенья отгрузки трека F `HPP-368` FSa (Emu Engineer: умолчание `KYTY_FIX_DUALSRC` 0 → 1, сборка из чистого worktree, таблица умолчаний) → `HPP-369` FSb (Red Team) → '
       '`HPP-370` FSc (Harness Engineer: W/V Sky Garden, W/V `mini_giants_garden`, справка V `KYTY_FIX_B1B=0`) → `HPP-371` FSd (лид; установка не раньше `HPP-354`); '
       'Б1а — серия без ограничителя не назначается; очередь F: F6 = Б9а (`HPP-372` F6a проект, Lever Researcher → `HPP-373` F6b, лид), затем Ф10 → Б11 (+Ф3) → Б4 → Ф5/Ф7**; ')
old2 = '`HPP-287` — `blocked` на `HPP-343` и `HPP-358`;'
new2 = '`HPP-287` — `blocked` на `HPP-371`, `HPP-373` и `HPP-358`;'
for name in ('CLAUDE.md', 'AGENTS.md'):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    crlf = '\r\n' in t
    t = t.replace('\r\n', '\n')
    assert t.count(old) == 1 and t.count(old2) == 1, name
    t = t.replace(old, new).replace(old2, new2)
    if crlf:
        t = t.replace('\n', '\r\n')
    p.write_bytes(t.encode('utf-8'))
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
F = pathlib.Path('C:/kyty/f287/FACTS.md')
sec = ('\n## F3e (`HPP-343`, лид), 2026-10-01 14:15–14:3xZ: приёмка F3 — Б1б и Ф9 `FIXED` (п. 282, KytyPS5 `cc9880e6`)\n\n'
       'Вход: пробуждение `issue_blockers_resolved` (`HPP-342` `done` 14:13Z). Прочитаны п. 259, 277, 281; отчёт F3d `5f716839:docs/track-f/f3d.md`. Замка и `STOP` не было\n'
       'при каждой команде (первая строка — проверка замка); `HPP-315` (S4) `in_progress` — процессов с ГП у лида нет; пересчёт — 6 с.\n\n'
       '- Пересчёт лида [c]: `f3e_chk.py` (sha256 `237d7600…`), вывод `f3e_chk.out.txt` (`922b115e…`, `F3E RECOUNT ALL OK`) — sha 8 логов; пары, низкие страницы,\n'
       '  `BvhLoopCapTrip:`, маркеры смерти, `[Vulkan][E]`, строки `Shader translation cache:` (8 из 8 — каталог по ручке), Σ`dt`, среднее `dt`, кадры ≥ 1 с — совпали\n'
       '  с `summary_f3d.txt`.\n'
       '- Листы `sheet_f3d_a2.png`, `sheet_f3d_a4.png`, `sheetpair_f3d_bv.png` просмотрены; против `C:/kyty/s142/sheet_c142_02.png`, `sheet_c142_09.png` и `v142` — те же\n'
       '  сцены, видимых дефектов нет.\n'
       '- Решение — `ROADMAP.md` п. 282 (14:19:37Z, коммит `cc9880e6` до создания звеньев): Б1б и Ф9 `FIXED`; `f3d_bv`/`f3d_bw` — регрессионный вход п. 228(г)(5)\n'
       '  для `2e6df8f0`; звенья отгрузки и F6; Б1а — серия без ограничителя не назначается; очередь F после F6 — Ф10 → Б11 (+Ф3) → Б4 → Ф5/Ф7.\n'
       '- Звенья (`mk_chain_fs.py`, вывод `chain_fs.json`; стадии review у звеньев специалистов проверены в ответе API): `HPP-368` FSa (`todo`), `HPP-369` FSb,\n'
       '  `HPP-370` FSc, `HPP-371` FSd (лид), `HPP-372` F6a (`todo`, Lever Researcher), `HPP-373` F6b (лид). `HPP-287` — `blocked` на `HPP-371`, `HPP-373`, `HPP-358`.\n'
       '- Реестр §16 — Б1б, Ф9 `FIXED`; Б1а, Ф10, Б9а. Строка трека F в `CLAUDE.md` = `AGENTS.md` — `ps5-em`.\n'
       '- Скрипты: `ins282.py`, `p282.md`, `reg282.md`, `mk_chain_fs.py`, `status_f3e.py` (копии — `docs/track-f/f3e/`).\n')
ft = F.read_bytes().decode('utf-8')
assert '## F3e (' not in ft
F.write_bytes((ft.rstrip('\n') + '\n' + sec).encode('utf-8'))
T = pathlib.Path('C:/kyty/f287/times.txt')
tt = T.read_bytes().decode('utf-8')
tt = tt.rstrip('\n') + '\n' + ''.join(x + '\n' for x in [
    '2026-10-01T14:15:19Z F3e start (lead, HPP-343), no lock, no STOP',
    '2026-10-01T14:16:51Z F3e lead recount f3e_chk.py start, no lock (6 s)',
    '2026-10-01T14:19:37Z F3e decision ROADMAP p.282 (commit cc9880e6)',
    '2026-10-01T14:22:44Z F3e chain created HPP-368..HPP-373, HPP-287 blocked on HPP-371, HPP-373, HPP-358',
])
T.write_bytes(tt.encode('utf-8'))
print('ok')
