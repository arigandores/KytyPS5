"""F6f (HPP-378): track F status line in ps5-em CLAUDE.md == AGENTS.md, FACTS.md section, times.txt lines. LF, write_bytes; aborts on lock."""
import os, pathlib, re, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
D = pathlib.Path('C:/kyty/KytyPS5/ps5 em')
rx = re.compile(r'очередь F: F6 = Б9а — F6b .*?Ф5/Ф7\*\*; ')
new = ('очередь F: F6 = Б9а — **F6f (`HPP-378`, п. 327, `cc3ceb27`): Б9а `FIXED`** (счёт трека F: `timestop_casino` ×2 и `mini_astro_clock_tower` при '
       '`KYTY_FIX_B9A=1` — 0 строк заглушки, `SourceCreate` 0,0067 на кадр (было 1,53), 0 смертей, 0 `ASSERT:`, листы без отличий; звук [U]); умолчание '
       '`KYTY_FIX_B9A=1` — бинарём FS2 с членами Б9а печати FS2c и тегами `fs2_tw`/`fs2_t` (`timestop_casino` при умолчаниях); Б9б — `ТУПИК`; '
       '**F7 = Б39** (пол арены `enemy_final` без материала — диагностика): звенья `HPP-397` F7a (Harness Engineer, снимок RenderDoc под замком) → `HPP-398` F7b '
       '(Emu Engineer, разбор draw пола) → `HPP-399` F7c (лид), затем Ф10 → Б11 (+Ф3) → Б4 → Ф5/Ф7; Б41 — после Б39**; ')
old2 = '`HPP-287` — `blocked` на `HPP-378` и `HPP-384`'
new2 = '`HPP-287` — `blocked` на `HPP-399` и `HPP-384`'
old3 = 'F — FS2 (Б37, Б9а) после закрытия с. 146 (п. 309(л)(5)), F6 (Б9а), F7 (Б39), затем Б41;'
new3 = 'F — FS2 (Б37, Б9а) после закрытия с. 146 (п. 309(л)(5)), F7 (Б39), затем Б41;'
for name in ('CLAUDE.md', 'AGENTS.md'):
    p = D / name
    t = p.read_bytes().decode('utf-8')
    crlf = '\r\n' in t
    t = t.replace('\r\n', '\n')
    assert len(rx.findall(t)) == 1 and t.count(old2) == 1 and t.count(old3) == 1, name
    t = rx.sub(lambda m: new, t).replace(old2, new2).replace(old3, new3)
    if crlf:
        t = t.replace('\n', '\r\n')
    p.write_bytes(t.encode('utf-8'))
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()
F = pathlib.Path('C:/kyty/f287/FACTS.md')
sec = ('\n## F6f (`HPP-378`, лид), 2026-10-02 17:02–17:1xZ: приёмка F6 — Б9а `FIXED` (п. 327, KytyPS5 `cc3ceb27`)\n\n'
       'Вход: пробуждение `issue_blockers_resolved` (`HPP-377` `done`, приёмка F6e — стадией review лида, комментарий `6bb3d200`). Прочитаны п. 287, 290, 294, 298(в)–(е),\n'
       '309(е)(1), 322; отчёт и сводка серии 2 F6e. `HPP-352` — `done` (серия с. 145 закрыта).\n\n'
       '- Пересчёт лида [c]: `f6f_chk.py` (sha256 `4594e014…`, кода F6e не импортирует), вывод `f6f_chk.out.txt` (`ac719639…`, `F6F RECOUNT ALL OK`), 17:03:5xZ, без замка.\n'
       '- Листы: `pair_f6e_a2_vs_c142_03.png`, `pair_f6e_b1_vs_v143_03.png` — видимых отличий от эталонов нет.\n'
       '- Решение — `ROADMAP.md` п. 327 (17:08:33Z, коммит `cc3ceb27` до создания звеньев): Б9а `FIXED`; умолчание 1 — FS2 с членами Б9а FS2c (`fs2_tw`/`fs2_t`);\n'
       '  реестр §23; F7 = диагностика Б39.\n'
       '- Звенья (`mk_chain_f7.py`, вывод `chain_f7.json`; стадии review у звеньев специалистов проверены в ответе API): `HPP-397` F7a (Harness Engineer), `HPP-398` F7b\n'
       '  (Emu Engineer), `HPP-399` F7c (лид), все `blocked` по цепочке; `HPP-287` — `blocked` на `HPP-399`, `HPP-384` (`HPP-371` — `done`).\n'
       '- **Процесс (отступление, названо):** замок трека S (`go_s.sh c2_0`) взят 17:04:34Z во время работы звена; под ним — одна команда чтения `wc -l` ROADMAP\n'
       '  (процесс, ≈ 17:05Z) и ожидание циклом `sleep 30` без записей до 17:08:17Z; черновики — только в папке прогона платформы.\n'
       '- Скрипты: `f6f_chk.py`, `p327.md`, `reg327.md`, `ins327.py`, `mk_chain_f7.py`, `status_f6f.py` (копии — `docs/track-f/f6f/`).\n')
ft = F.read_bytes().decode('utf-8')
assert '## F6f (' not in ft
F.write_bytes((ft.rstrip('\n') + '\n' + sec).encode('utf-8'))
T = pathlib.Path('C:/kyty/f287/times.txt')
tt = T.read_bytes().decode('utf-8')
tt = tt.rstrip('\n') + '\n' + ''.join(x + '\n' for x in [
    '2026-10-02T17:02:18Z F6f start (lead, HPP-378), no lock, no STOP',
    '2026-10-02T17:03:55Z F6f lead recount f6f_chk.py done (F6F RECOUNT ALL OK, out ac719639), no lock',
    '2026-10-02T17:04:34Z F6f foreign lock (track S go_s.sh c2_0) seen ~17:05Z; one read-only wc -l under it; wait loop without writes until 17:08:17Z',
    '2026-10-02T17:08:33Z F6f decision ROADMAP p.327 (commit cc3ceb27)',
    '2026-10-02T17:08:44Z F6f chain created HPP-397..HPP-399, HPP-287 blocked on HPP-399, HPP-384',
])
T.write_bytes(tt.encode('utf-8'))
print('ok')
