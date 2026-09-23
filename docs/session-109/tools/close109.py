"""Session 109 close: SEALS109 (+ audit addendum), FACTS §7 and corrections, ROADMAP (item 8 fix, item 9, addition,
decision after 109, cycle line, §7 rows).  One-shot; LF writes."""
import hashlib
from pathlib import Path

S109 = Path('C:/kyty/s109')
RM = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(path, pairs):
    s = Path(path).read_bytes().decode('utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (str(path), a[:80])
        s = s.replace(a, b)
    Path(path).write_bytes(s.encode('utf-8'))


audit = S109 / 'pred' / '05_audit109.md'
with open(S109 / 'SEALS109.txt', 'ab') as f:
    f.write(('%s *pred/05_audit109.md\n' % sha(audit)).encode('ascii'))
a_sha = sha(audit)[:8]

edit(S109 / 'FACTS.md', [
    ("""   events at load (frames 136–193) and in the first hundreds of frames after, in both arms. **Not shipped by the
   seal; `frf109` (`pred/03`) not run.** Hypothesis [I]: without the contention GuestGpu reaches dispatches whose
   async compiles are still running sooner; the count does not measure stall duration.""",
     """   events at load and after it, in both arms (the excess splits evenly: B 6 at load / 6 after, A 2 / 1 — audit).
   **Not shipped by the seal; `frf109` (`pred/03`) not run.** Weakly significant (one-sided p 0.032 binomial, 0.043 by
   permutation over entries). Hypothesis [I], supported by the audit: without the contention GuestGpu reaches
   dispatches whose async compiles are still running sooner — after load, a flip where the walker queued a new
   pipeline has a wait in 6/14 cases in B against 1/17 in A (p 0.021); new-pipeline flips cost about the same in both
   arms (13.2 vs 15.3 ms extra), so the count does not show a duration penalty. Predictions: pred/01 E1 HIT, **E2
   MISS**, E3 E4 HIT; pred/01b V1–V5 HIT; pred/02 E1 HIT, **E2 MISS**, E3 E4 HIT."""),
    ("""   prefetch never takes the lock); `da_walk_us` −36.1; **`gpu_busy_us` +70.6 µs (t 4.63), reproducing `fam108`'s +87.5
   — cause [U]**. Removing tag 2's hold is worth ≈ −150 µs by two different mechanisms.""",
     """   prefetch never takes the lock); `da_walk_us` −36.1; **`gpu_busy_us` +70.6 µs (t 4.63), reproducing `fam108`'s +87.5
   — identified by the audit [I]: ~2 more buffer uploads a flip land inside render passes and split them (the only
   moving close reason; `sync_up_kb` +252 KiB; `nvidia-smi` +0.5 pp utilisation, +0.2 W)**. Robustness: sign-flip p
   0.012, bootstrap 95 % [−270, −36], paired median −16, dropping the 5 most negative pairs −94; the gain is
   one-vblank flips 13.11 → 14.26 %. Predictions of pred/04 (scored by the audit — `frm109.py` printed pred/03's
   G1–G6): M1 M2 M3 HIT, **M4 MISS** (Δ`da_walk_us` −36.1 against ≤ −100). Removing tag 2's hold is worth ≈ −150 µs by
   two different mechanisms."""),
    ("""cause of the GPU-time rise. **Not proved.** Any shipped speedup (none); 60 FPS.""",
     """size of the mid-pass upload effect in CPU time. **Not proved.** Any shipped speedup (none); 60 FPS."""),
    ("AUDIT_PLACEHOLDER\n", """One agent, three lenses, sealed as `pred/05_audit109.md` (`{A_SHA}…`). **Recount CONFIRMED** (every number of
`ent109`, `vfy109`, `ent109b`, `frm109` reproduced by own parsers). **Protocol HOLDS, with defects** (records before
actions, seals before runs, hashes, pin in all 18 runs, no writes inside sealed windows). **Code NOT REFUTED** (no
first-contact hole, no wrong id; unlocked materialization touches only immutable-after-publish plan data and
thread-local state). Findings: (1) **MAJOR** — pred/04's M1–M4 were never scored (the scorer printed pred/03's G1–G6);
M4 MISS; pred/01 and pred/02 E2 MISS — corrected above and in ROADMAP; (2) **MAJOR** — `ent109b` FAIL weakly
significant, harm not shown, hypothesis supported (6/14 vs 1/17) — corrected above; (3) **MAJOR** — the `gpu_busy`
rise is ~2 extra mid-pass buffer uploads a flip (render-pass splits) — recorded; (4) MINOR — pred/04 and its ROADMAP
record share a commit; shipping `cspfree` needs a fresh sealed ABBA; 10 of 30 new mutants survive (no verdict
changes); code debts (skip after retirement, "moved" on null source, raw pointers in a thread-local memo). Report:
`C:/kyty/s109/audit109/AUDIT109.md`.
""".replace("{A_SHA}", a_sha)),
])

edit(RM, [
    ("""   [U]**; G1–G6 HIT. Вывод: снятие удержания тега 2 стоит ≈ −150 мкс кадра двумя разными способами — выигрыш реален.""",
     """   [U]**; предсказания печати 04 (оценены аудитом: скорер печатал G1–G6 печати 03): M1 M2 M3 HIT, **M4 MISS**
   (`da_walk_us` −36,1 против ≤ −100). Вывод: снятие удержания тега 2 стоит ≈ −150 мкс кадра двумя разными способами —
   выигрыш реален (перестановочный p 0,012, бутстреп [−270; −36], медиана пар −16 — выигрыш в доле одновблэнковых
   флипов 13,11 → 14,26 %). **Отгрузка `cspfree` требует нового запечатанного ABBA по времени кадра собранной со
   стражем сборки; `frm109` только измерил размер.**
9. **Итог сессии 109 и аудит** (одна агент-линза на три стороны, печать `C:/kyty/s109/pred/05_audit109.md`,
   `{A_SHA}…`): пересчёт CONFIRMED, протокол HOLDS с дефектами, код NOT REFUTED (дыры первой встречи нет, неверного id нет).
   MAJOR: предсказания печати 04 не оценивались (исправлено в п. 8), E2 печатей 01 и 02 — MISS; FAIL `ent109b` верен
   по правилу, но значим слабо (p 0,03–0,06), вред по длительности не показан, гипотеза «GuestGpu догоняет асинхронные
   компиляции» поддержана (ожидание во флипе с новым пайплайном после загрузки: B 6/14, A 1/17); **рост
   `gpu_busy_us` объяснён [I]: ~2 лишние загрузки буферов посреди прохода рендера на флип рвут проходы** (единственная
   сдвигающаяся причина закрытия прохода, `sync_up_kb` +250 КиБ, `nvidia-smi` +0,5 п.п. и +0,2 Вт при той же
   частоте). MINOR: печать 04 и её запись в одном коммите; 10 из 30 новых мутантов выживают (вердикты не меняются);
   долги кода `cspfree` — в §7.

**Дополнение сессии 109: ускорения нет.** Пропуск префетча по семейству закрыт окончательно (`ent109`, v2 — 34 против
12 событий). `cspfree` (память «запись источника + специализация», префетч без замка) проверен (`vfy109`: 0
расхождений на 2,06 млн) и сокращает средний кадр на 154 мкс при пине (`frm109`, измерение), но его страж по ЧИСЛУ
событий не пройден (`ent109b`: 17 против 7, в основном ожидания). Итоги — `docs/local-session-109.md`.

**РЕШЕНИЕ ИСПОЛНИТЕЛЯ ПОСЛЕ С. 109 (записано до действия; основание — `ent109b`, `frm109` и аудит `pred/05`).**
1. **Сессия 110: страж по ДЛИТЕЛЬНОСТИ рывков для `cspfree`.** Счётчики стены на потоке диспатча `cs_sync_new_us`,
   `cs_sync_wait_us` и шкала `cs_stall_max_us` (самый долгий рывок кадра); затем запечатанный ABBA входов (как
   `ent109b`) с правилом по длительности, записанным сюда ДО печати (предложение плана с. 110: Σ мкс плеча B ≤ 1,25 ×
   Σ плеча A + 20 000 мкс и самый долгий рывок B ≤ самого долгого A + 10 000 мкс, при Σ A > 0); при PASS — новый
   запечатанный ABBA по времени кадра и видео с пином, затем умолчание.
2. **Параллельно — код `daslot` (тег 1)** по `design109.md` §A, без времени прогонов до скоринга п. 1.
3. **Загрузки буферов посреди прохода** (причина роста `gpu_busy_us` при снятии удержания) — отдельный рычаг:
   сначала перепись причин (какие буферы, чьи записи CPU, почему синхронно), запись проекта до кода.
4. **Фикстуры производных скореров** добавляют убийц 10 выживших мутантов аудита с. 109 (`AUDIT109.md`).
""".replace("{A_SHA}", a_sha)),
    ("""первой встречи (6 против 3 синхронных компиляций при выключенном precache compute) — v2 в с. 109. 60 FPS —
направление без маршрута с живой оценкой.""",
     """первой встречи (6 против 3 синхронных компиляций при выключенном precache compute); v2 закрыт в с. 109. `cspfree`
(с. 109): −154,1 мкс при пине измерено, проверка чиста, страж по числу событий не пройден (17 против 7) — страж по
длительности в с. 110. 60 FPS — направление без маршрута с живой оценкой."""),
    ("""| **префетч compute под `PipelineCache::m_mutex` на потоке обхода** — в установившейся сцене `cspf_have` 266/266, `cspf_new` 0 (`obs107`): чистое удержание 342 мкс/кадр; память по user SGPR закрыта (`cspmemo`, VERIFY FAIL, 44 % попаданий). **С. 108: `cspfam=4` — Δ`dt` −141,8 мкс (`fam108`), но при выключенном precache compute 6 против 3 синхронных компиляций ⇒ откат к 0** | `cspfam` v2: сброс серий по счётчику созданий пайплайнов; ABBA по времени + ABBA входов со стражем в силе (решение после с. 108) | **106 → 109** |""",
     """| **префетч compute под `PipelineCache::m_mutex` на потоке обхода** — в установившейся сцене `cspf_have` 266/266, `cspf_new` 0 (`obs107`): чистое удержание 342 мкс/кадр; память по user SGPR закрыта (`cspmemo`, VERIFY FAIL, 44 % попаданий). С. 108: `cspfam=4` — Δ`dt` −141,8 мкс, откат стражем. **С. 109: семейство закрыто (v2 FAIL 34/12); `cspfree` — проверка чиста, Δ`dt` −154,1 мкс (`frm109`), страж по числу событий FAIL (17/7)** | страж по длительности рывков, затем ABBA отгрузки (решение после с. 109) | **106 → 110** |
| **загрузки буферов посреди прохода рендера** — при снятии удержания префетча +1,7…3,0 разрыва прохода на флип, `sync_up_kb` +250 КиБ, `gpu_busy_us` +70…90 мкс (`fam108`, `frm109`; аудит с. 109) | перепись причин (буферы, записи CPU, почему синхронно) | **109** |
| долги кода `cspfree`: пропуск префетча после вывода записи из обращения (только производительность); режим 2 пишет «moved», когда `FreeSourceFor` вернул null; память на поток хранит сырые указатели — корректно, пока в процессе один `PipelineCache` | при отгрузке | **109** |
| 10 выживших мутантов скореров с. 109 (`ent109`: режим пина, `fatal`, позиция токена гейта, удержание 80 %, двойные метки запуска, строка precache; `frm109`: окно ±1, `pstdev`, средние уровни, `GpuWaitSlow`) | фикстуры в следующих производных скорерах | **109** |"""),
])
print('ok', a_sha)
