
## F47g2 (`HPP-828`, Emu Engineer) — правки RC1–RC5 кода `KYTY_DIAG_F47DT` и ридера по Ф1–Ф3 (п. 742(в), (г); запись __NOW__, UTC)

- Без замка и без игры; установленный FS15 `bfac84be`, `C:/kyty/build*` и кэши не трогались. **WIP**: код игрой не проверялся.
- Код: worktree `C:/kyty/f287/f47g/wt` `1f9b5b77` + `8bdc069a`; `main` `bfe0be75` (`--only`, `+`/`-` строки = `8bdc069a`, 434/118).
- RC1: поле `q` (флипы, поставленные разбором GuestGpu, + 1; `NoteFlip` в `Flip()`, `Flip(addr)`, `FlipWithInterrupt`, `PrepareCpuFlip`),
  строки `F47dt: kind=flip q= path= rid=` и (решение исполнителя) `F47dt: kind=shown n= rid=` на потоке показа; окно и `d` — по `q`;
  `n` — отдельным полем. RC2: запись (ii) по `ImageId` с поколением слота, `sid`, `rlast`, `sk=other_image`. RC3: без глобального сторожа
  пула у кольца Stream; нота GPU-копии const-bank ⇒ `gvh=unmeasured:gpu_copy`; `ggpu` у буфера. RC4: плечи S, A2. RC5 и Ф1–Ф3 — ридер
  `dt_f47g2.py`.
- Бинарь теста `C:/kyty/f287/bin/kyty_emulator_86e42e36.exe` (sha256 `86e42e36440ac5b7ac7a420c12d7a6aaadc4ffc483145ae9c6d18be046075e82`,
  версия `…-1932-g8bdc069a`), подпись `9177b426…` = базе; стенд `942c4791…`.
- Стенд `run_stand_f47g2.py` `ALL OK` (32 члена, `=1`/`=0`); свои мутанты m2, m2p, m6, m7 — `FAILED` на стенде; ридер `selftest` `ALL OK`
  (54); `shader_cfg_tests` = F47g (дельта 0); `check_gate_order.py` clean (worktree и `main`).
- Отчёт `docs/track-f/f47g2.md`, файлы `docs/track-f/f47g2/`. Следующее звено — F47h2 (Red Team, ревью).
