# FS2d (`HPP-384`) — приёмка FS2c и установка FS2 (зеркало раздела `C:/kyty/f287/FACTS.md`)

Статус: FS2 `bbad499c` установлен; решение — `ROADMAP.md` п. 338; файлы — `docs/track-f/fs2d/`.

## FS2d (`HPP-384`, лид), 2026-10-02T20:54Z–21:09:29Z: FS2c принят, FS2 `bbad499c` установлен — Б37 и Б9а отгружены под (B) (`ROADMAP.md` п. 338)

Время — UTC по `date -u`; строки событий — `C:/kyty/f287/times.txt`.
- **Вход:** FS2c `HPP-383` `done` (20:53:03Z; KytyPS5 `f96c15a1`, отчёт `docs/track-f/fs2c.md`); сводка `summary_fs2.txt` `ebe132f2…` — PASS; FSd `HPP-371`, с. 145
  `HPP-354`, с. 146 `HPP-390` — `done`; комментарии звена `f56cc4fe` (п. 309(л)(5)) и `fed2947f` (откат п. 329(б)).
- **Пересчёт лида (20:56:28–20:57:06Z, без замка):** `C:/kyty/f287/lead/fs2d_chk.py` (`e334378f…`) → `fs2d_chk.out.txt` (`ce03a84d…`) — `FS2D RECOUNT ALL OK`;
  sha логов = отчёту FS2c; `fs2_w`/`fs2_v`/`fs2_t`: `[Vulkan][E]` 0, смерти 0, `FixMinimize: on` 1, `FixB9a: on` 1, `DualSrcBlend` 1, `ASSERT:` 0,
  `user_msg_param` 0, `[AudioPropagation_v1]` 0, лимит слоя 0; `fs2_w0`: `FixMinimize: on` 0, `imageExtent (width = 0, height = 0)` после `TestMinimize:
  minimize`, VUID-01689 смещение 1 — STOP.
- **Листы:** `sheet_fs2_v.png` (`4bcef41d…`), `sheet_fs2_t.png` (`95b1dd3d…`) против `f6e/sheet_f6e_a2.png` — видимых дефектов и отличий нет.
- **Решение** `ROADMAP.md` п. 338 — 2026-10-02 21:00:28Z (запись ждала снятия замка P26 только проверками замка).
- **Установка (21:00:41Z, одной командой с проверкой замка):** `ps5 em/kyty_emulator.exe` `dac02fb9…` → `bbad499c56b744dfcef85b7556735c025ebb3db185b6bb9b02e7a0b3a228eb55`
  (копия `C:/kyty/f287/bin/kyty_emulator_bbad499c.exe`); процессов эмулятора не было; кэши не тронуты; откат — `C:/kyty/s146/kyty_emulator_dac02fb9.exe` или
  `KYTY_FIX_MINIMIZE=0` и `KYTY_FIX_B9A=0` вместе (п. 329(б)).
- **Реестр** §24 — Б37, Б9а `FIXED`, отгружены под (B); дельта курса [I] 44 → 42 на установленной, скрипт — следующим закрытием.
- **Документы:** `CLAUDE.md` = `AGENTS.md` — строка установленной сборки и строка трека F; зеркало — `docs/track-f/fs2d.md`, `docs/track-f/fs2d/lead/`.
- **Не заявляется:** что без правки свёрнутое окно никогда не ведёт к крэшу; что звук верен; что 40 `SCENE_OK` держатся на FS2; корректность любой сцены и
  проходимость до конца; ни одно число — не выигрыш; 60 FPS не обещается.
