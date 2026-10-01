"""F2c wake 2 (comment 53664de2, p.254(e)): append the addendum to FACTS, facts_f2c.md and the git mirror; times lines. LF."""
import sys

T0 = sys.argv[1]
ADD = """
### F2c, пробуждение 2 (`issue_commented` 53664de2, лид, 04:58:58Z) — форма W по п. 254(е); прогонов нет, `blocked` сохраняется

Время — UTC из `C:/kyty/f287/times.txt`: пробуждение прочитано 04:59Z, правка скорера и фикстур — до 05:01Z. Замка не было ни на одной команде,
`STOP` не было. Игры, установок бинаря, операций с кэшами нет.

**Комментарий лида** — `d3a8d951:docs/ROADMAP.md:13404` п. 254(е), якорь «(е) **Форма W до отгрузки исправления Б35 (решение):**» (контроль +1 —
13405 «с `KYTY_PIPELINE_PRECACHE=0`»): каждый прогон с `--vulkan-validation true` — с `KYTY_PIPELINE_PRECACHE=0`; печать называет форму; скорер
проверяет её положительным контролем — в логе W нет строки `PipelinePrecache: N recipes ->`, в логе V той же серии она есть; нарушение — тег FAIL;
для F2c — плечо (б) W (`d3a8d951:docs/ROADMAP.md:13411`, якорь «F2c `HPP-310` — плечо W», контроль +1 — 13412 «`HPP-318` — `pcw_val`»).

**Противоречит ли форма замыслу плеча (б) — нет [c по коду `4fc501f4`]:** `KYTY_PIPELINE_PRECACHE` читает только `PipelinePrecacheEnabled()`
(`pipelineCache.cpp:5845`), а её зовут лишь `RecordGraphicsRecipe` (:5858), `RecordComputeRecipe` (:5904) и `StartPrecache` (:6142). Предтрансляция
CS, дающая строки `CsPretranslate: ready|skipped` 5 хэшей Б26б, ставится из `TraceShaderRegistration` (:5968, очередь :6012) под
`ComputePretranslation::Enabled()` = `KYTY_CS_PRETRANSLATE` (`computePretranslation.h:37`) — от precache не зависит. Плечо W проверяет валидацией
пайплайны, которые создаёт уровень; CS Б26б создаются по dispatch уровня, а в `log_v142` их строки идут после строки входа (пробуждение 1) — не из
стартового precache. Плечо (б) запускается в форме (е), вопроса лиду нет.
Оговорка [c по коду, I по следствию]: без стартового precache проверка `known` (:6006–6010) реже находит программу — в W могут встать в очередь
CS, которые при precache уже готовы; число строк `CsPretranslate` и счёт профиля 96 / 0 / 0 в W поэтому печатаются как данные, критерий (б) —
0 `[Vulkan][E]` при активной валидации (п. 224), как в задании.

**Правка скорера `f2c_b26.py` до печати (печати F2c ещё нет, скорер не запечатан):** ключ `--arm V|W`; счёт строк по регулярному выражению
`PipelinePrecache: \\d+ recipes -> ` (`pipelineCache.cpp:6425`); `--arm W` — 0 строк, `--arm V` — ≥ 1, иначе вердикт обоих прочтений
`FAIL (form p.254(e): …)`; недействительная ручка важнее формы; без `--arm` форма печатается «not judged». Плечи (а) и (в) — `--arm V`
(без валидации, precache по умолчанию), (б) — `--arm W`. sha256 `f2c_b26.py` `{S_SC}`, копия до правки `f2c_b26.pre254.py`.
Фикстуры `test_f2c_b26.py` (sha256 `{S_T}`): {N} проверок (+11: W без строки — ok; W со строкой — FAIL у обоих прочтений; V со строкой; V без строки
и на контроле `=0`; две строки; иная строка `PipelinePrecache:` без «N recipes ->» — не сводка; ручка важнее формы; `main --arm W/X/` без значения),
`ALL OK`, вывод `test_f2c_b26.out.txt` sha256 `{S_O}` (первая строка — sha набора `{S_T8}` и цели `{S_SC8}`).
Регрессия `base142_f2c.py` (печатает число строк precache) → `base142_f2c.out.txt` sha256 `{S_B}`: 12 из 12 логов с. 142 — `CONTROL RETURNS`,
переоткрытий 0, смертей 0, строк `PipelinePrecache: N recipes ->` ровно 1 в каждом (и в `log_w142` — прежняя форма W с precache) —
регулярное выражение подтверждено на реальных логах.

**Остаётся открытым:** В1–В5 пробуждения 1 — в п. 254 ответов нет (п. 254(е) отвечает только на форму W). Блокер — `HPP-301` (закрытие с. 143,
`in_progress`); затем очередь замка п. 228(в) и п. 254(к)(4): цепочка с. 144 (33 тега `sc144`) > P > F; звено трека с замком, не `done` к старту
шага прогонов с. 144 (`HPP-332`), получает блокер `HPP-333` (п. 254(и)(1)).
**Следующее действие:** после `done` `HPP-301` и ответов В1–В5 — харнесс `go_f2c.sh` (порт `go142a.sh`, плечо W с
`KYTY_PIPELINE_PRECACHE=0` позиционно в `enter_scene.py`), печать `pred/01_f2c.md` с формой (е), три прогона под замком в очереди.
**Не заявляется:** ничего о правке в игре; прогонов нет.
"""


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


D = 'C:/kyty/f287/f2c/'
out_lines = open(D + 'test_f2c_b26.out.txt', 'rb').read().decode('ascii').splitlines()
assert out_lines[-1] == 'ALL OK'
n = [l for l in out_lines if l.startswith('checks ')][0].split()[1]
s_sc, s_t, s_o, s_b = sha(D + 'f2c_b26.py'), sha(D + 'test_f2c_b26.py'), sha(D + 'test_f2c_b26.out.txt'), sha(D + 'base142_f2c.out.txt')
assert out_lines[0] == 'suite test_f2c_b26.py sha256 %s target f2c_b26.py sha256 %s' % (s_t, s_sc)
txt = (ADD.replace('{S_SC}', s_sc[:8] + '…').replace('{S_T}', s_t[:8] + '…').replace('{S_O}', s_o[:8] + '…')
       .replace('{S_B}', s_b[:8] + '…').replace('{N}', n).replace('{S_T8}', s_t[:8]).replace('{S_SC8}', s_sc[:8]))
for p in ('C:/kyty/f287/FACTS.md', D + 'facts_f2c.md', 'C:/kyty/KytyPS5/docs/track-f/f2c.md'):
    b = open(p, 'rb').read()
    assert b'\r\n' not in b and b'\xd0\xbf\xd1\x80\xd0\xbe\xd0\xb1\xd1\x83\xd0\xb6\xd0\xb4\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 2' not in b, p
    if not b.endswith(b'\n'):
        b += b'\n'
    open(p, 'wb').write(b + txt.encode('utf-8'))
with open('C:/kyty/f287/times.txt', 'ab') as f:
    f.write(('2026-10-01T04:59:16Z F2c wake 2 issue_commented 53664de2 (lead, event 04:58:58Z from comment createdAt): p.254(e) W form '
             'KYTY_PIPELINE_PRECACHE=0; no lock, no STOP\n').encode('ascii'))
    f.write(('%s F2c f2c_b26.py --arm V|W form control (sha %s), test_f2c_b26.out.txt %s checks %s ALL OK, base142_f2c.out.txt %s '
             '12/12 CONTROL RETURNS precache 1 each; FACTS + facts_f2c.md + docs/track-f/f2c.md appended\n'
             % (T0, s_sc[:8], s_o[:8], n, s_b[:8])).encode('ascii'))
print('done', n, s_sc[:8], s_t[:8], s_o[:8], s_b[:8])
