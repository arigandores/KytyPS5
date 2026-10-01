# F3e (HPP-343): create shipment links FSa..FSd and F6 links F6a, F6b per ROADMAP p.282(g), (zh) (cc9880e6); specialist links with the
# lead's review stage (executionPolicy checked in the API answer, script fails on empty stages); then HPP-287 blocked on FSd, F6b, HPP-358.
import json, os, subprocess, urllib.request
B = os.environ['PAPERCLIP_API_URL'].rstrip('/')
if B.endswith('/api'):
    B = B[:-4]
H = {'Authorization': 'Bearer ' + os.environ['PAPERCLIP_API_KEY'], 'Content-Type': 'application/json',
     'X-Paperclip-Run-Id': os.environ['PAPERCLIP_RUN_ID']}
CO = os.environ['PAPERCLIP_COMPANY_ID']
OUT = 'C:/kyty/f287/lead/chain_fs.json'
assert not os.path.exists(OUT), 'chain already created'
C = 'cc9880e6'
RM = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', C + ':docs/ROADMAP.md'],
                    capture_output=True, check=True).stdout.decode('utf-8').split('\n')
def ref(n, a, a1):
    assert RM[n - 1].strip().startswith(a), (n, RM[n - 1][:80])
    assert RM[n].strip().startswith(a1), (n + 1, RM[n][:80])
    return '`%s:docs/ROADMAP.md:%d` «%s» (контроль +1 — %d «%s»)' % (C, n, a, n + 1, a1)
def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(B + path, data=data, method=method, headers=H)
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode('utf-8'))
AG = {'emu': 'eb15eb75-9046-4c8a-b92c-be4254b9ee85', 'red': 'dc34de0a-4911-443b-a2d4-7c99d2c9cd9e',
      'harn': '2f5a0935-2e1a-4a76-8d98-67897fca3b8b', 'lead': 'f1276629-91fd-414a-b13f-52d1445432c9',
      'lever': 'aabc0a15-c42c-44df-bd7a-3984d1f51ea7'}
cur = req('GET', '/api/issues/HPP-343')
PARENT, PROJ, PWS = cur['parentId'], cur['projectId'], cur.get('projectWorkspaceId')
REVIEW = {'mode': 'normal', 'commentRequired': True,
          'stages': [{'type': 'review', 'approvalsNeeded': 1, 'participants': [{'type': 'agent', 'agentId': AG['lead']}]}]}
H358 = req('GET', '/api/issues/HPP-358')['id']
R282 = ref(14712, '282. **Звено F3e трека F', 'регрессионный вход п. 228(г)(5)')
RG = ref(14745, '(г) **Ответ на п. 259(е)(8)', '`KYTY_FIX_B1B` (`FIXED`, (а))')
RZH = ref(14780, '(ж) **Следующая итерация — F6 = Б9а**', 'очереди F0 §6')
COMMON = ('\n\n**Общие правила трека F (п. 228, п. 237, п. 259, п. 282):** решение — ' + R282 + '; форма трека — `beb36ab0:docs/ROADMAP.md:12074` «Трек F» (п. 228); '
  'правило печати п. 258(д) (член сверх пункта — «член исполнителя [I]», вердикта не задаёт). Читать п. 228, п. 259(б), п. 281(в)–(г), п. 282 целиком до первого действия; '
  'реестр — `' + C + ':docs/track-f/register.md` (§4, §15, §16). Файлы — `C:/kyty/f287/<звено>/`, в git — `docs/track-f/<звено>/`. '
  'Раздел звена в `C:/kyty/f287/FACTS.md` ДО `done`, время — UTC по `date -u`, строки событий — `C:/kyty/f287/times.txt`. '
  '**Общее правило 27:** первая строка каждой команды — `[ -e C:/kyty/SEALED_RUN.lock ] && exit 3` (кроме команд Harness Engineer внутри своего замка); при замке не запускать процессов (сборка — тоже процесс) и не писать файлов; '
  'запись файла и комментарий — одной командой с проверкой замка; пока идёт серия сессии (`HPP-352` `in_progress`) — у звеньев без замка нет сборок, мутантов и пересчётов дольше 30 с; '
  'процесс с устройством Vulkan у звена без замка — только если ни одна задача с проверкой GLCache или загрузки ГП между тегами не `in_progress` (п. 277(г), ответ API — строкой `times.txt`). '
  'Стоп: перед каждой командой дольше 60 с — `[ -e C:/kyty/f287/STOP ] && exit 4` в той же команде и проверка комментариев звена `GET …/comments?after=<последний>`; найденный стоп — строка `times.txt` с обоими временами (общее правило 26). '
  '`find /` запрещён; процессов после хартбита не оставлять (общее правило 28). '
  'Ссылки на изменяемые документы — `<коммит>:<путь>:<строка>` с якорем и контролем +1 (общее правило 24(1)). Коммит — `C:/Program Files/Git/cmd/git.exe` с `GIT_AUTHOR_*`/`GIT_COMMITTER_*` в том же вызове и `--only` (ловушка 11); push — нет. '
  'Кириллица в API — только JSON из Python через stdin. PATH в Bash — `export PATH=/usr/bin:/mingw64/bin:$PATH`; `PYTHONIOENCODING=utf-8`. '
  'Игру запускает только Harness Engineer под замком `C:/kyty/SEALED_RUN.lock` (очередь: цепочка сессии > трек P > трек F > трек S). Никаких `tail -F`, фоновых процессов вместо ожидания, `run_in_background`. Сдача — `done` (платформа отдаёт на review лиду).')
LINKS = [
 ('FSa', 'emu', 'todo', [], 'трек F, звено FSa: коммит и сборка бинаря отгрузки трека F (умолчание KYTY_FIX_DUALSRC 0 -> 1)',
  'Роль: Emu Engineer. Звено отгрузки трека F по п. 282(г)(1) — ' + RG + '; основание — п. 259(б), п. 281(в)(1).\n'
  '1. Коммит в `main`: умолчание `KYTY_FIX_DUALSRC` 0 → 1 — разность только в константе умолчания и комментарии (строка проверки лида). Рабочее дерево `C:/kyty/KytyPS5` занято правкой F5a2 (`HPP-366`) — чужие изменения не захватывать (`--only`).\n'
  '2. Сборка — из чистого worktree с LF на этом коммите (подпись транслятора зависит от окончаний строк, п. 277(б)(4)); копия `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, sha256, подпись трансляции.\n'
  '3. **Таблица умолчаний:** каждая переменная `KYTY_*`, чтение которой добавлено или изменено в `git diff 4fc501f4 <коммит> -- src/` — ручка, умолчание, строка `FIXED` реестра или «0 — прежний путь» с местом в коде. '
  'Ожидание: умолчание 1 — только `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC`; любая иная ручка, чьё умолчание меняет прежнее поведение `9235a7ac`, — **стоп и вопрос лиду**.\n'
  '4. `shader_cfg_tests` при умолчаниях — 127 / 1 (Б11) или список падений.\n'
  'Установленную `9235a7ac` в папке эмулятора не трогать; игру не запускать. Окно: сборка и тесты — только без замка в той же команде и при `HPP-352` не `in_progress` (ответ API — строкой `times.txt`).\n'
  'Отчёт `docs/track-f/fsa.md`: коммит, sha бинаря, подпись, таблица умолчаний, тесты.'),
 ('FSb', 'red', 'blocked', ['FSa'], 'трек F, звено FSb: ревью бинаря отгрузки трека F (FSa)',
  'Роль: Red Team. Ревью FSa по п. 282(г)(2) — ' + RG + ': (1) разность коммита FSa против родителя — только константа умолчания `KYTY_FIX_DUALSRC`; '
  '(2) таблица умолчаний — своим чтением `git diff 4fc501f4 <коммит> -- src/` (каждая `KYTY_*`: умолчание и прежний путь при нём); (3) своя сборка из чистого worktree с LF — sha и подпись трансляции совпадают с FSa; '
  '(4) `=0` у `KYTY_FIX_DUALSRC` — путь F4c (`c9a5e198`), при `=1` — перепись выхода PS п. 262(б); (5) `shader_cfg_tests` своим прогоном. Вердикт PASS / PASS_WITH_FIXES / FAIL, RC с владельцем. Игру не запускать. '
  'Окно сборки — как FSa.'),
 ('FSc', 'harn', 'blocked', ['FSb'], 'трек F, звено FSc: регрессия бинаря отгрузки трека F под замком (Sky Garden W/V, mini_giants_garden W/V)',
  'Роль: Harness Engineer. Прогоны п. 282(г)(3) — ' + RG + ' — на копии бинаря FSa (sha — из FSa/FSb; сверка перед каждым тегом, пересборка запрещена). Если вердикт FSb FAIL — `NOT EVALUABLE` без замка и вопрос лиду.\n'
  '**Харнесс** — порт `C:/kyty/f287/f3d/go_f3d.sh` и `C:/kyty/f287/f4c/go_f4c2.sh`: установка копии, возврат `9235a7ac` с проверкой sha; копия и возврат `_ShaderCache/PPSA21564` (корень, каталоги вариантов, файл рецептов `pipelines.bin`) и `GLCache` (`GLRESTORE=1`); каталог, которого до серии не было, после серии отсутствует; ожидание `idle142` и один повтор отказа BUSY (п. 279(в)).\n'
  '**Теги по порядку, при умолчаниях (ни одна `KYTY_FIX_*` не задаётся):** (а) W Sky Garden — контрольный: `--vulkan-validation true`, precache по умолчанию (п. 281(г)), `VK_LAYER_MESSAGE_ID_FILTER` (Ф6) и `VK_LAYER_DUPLICATE_MESSAGE_LIMIT` как `sc145`; '
  'положительный контроль — строка `DualSrcBlend: supported=1 enabled=1` до первой `GuestOut`; вход, Σ`dt` после первого кадра сцены ≥ 300 с (стена 310 с), 0 `[Vulkan][E]`, активность валидации п. 224, строк лимита слоя 0; остановка (а) — стоп серии; '
  '(б) V Sky Garden — Σ`dt` ≥ 300 с (стена 330 с), видео ≥ 3 000 кадров, `s51_vidglitch.py 4 6` 0 глитчей, 0 маркеров смерти, 0 кадров ≥ 1 с, 0 строк `BvhLoopCapTrip:`, лист-пара «`v142` / FSc» по тем же номерам кадров, среднее `dt` — число; '
  '(в) W `mini_giants_garden` — форма (а), ≥ 310 с, 0 `[Vulkan][E]`, ≥ 1 строка `DualSrcBlend: patched ps=5514e10f1a60df83`; (г) V `mini_giants_garden` — стена ≥ 330 с, видео ≥ 3 000, 0 глитчей, 0 маркеров, лист против `f4c_g`; '
  '(д) V Sky Garden `KYTY_FIX_B1B=0` — информация, Σ`dt` ≥ 300 с, среднее `dt` — число, вердикта не задаёт. Удержание меньше названного — `NOT EVALUABLE`, повтор — строкой лида; событие окна — помеха прогона.\n'
  '**Скорер** — фикстуры на каждый член; **печать** `pred/01_fs.md` — п. 282(г)(3) дословно и п. 281(в)–(г); член сверх — по п. 258(д). Очередь замка — сессия > P > F > S; внутри F — по готовности, F5c (`HPP-357`) первым при одновременном ожидании. '
  'Исход — таблица в `FACTS.md`, зеркало `docs/track-f/fsc.md`.'),
 ('FSd', 'lead', 'blocked', ['FSc'], 'трек F, звено FSd: приёмка бинаря отгрузки трека F, строка установки (лид)',
  'Роль: Roadmap Lead. Приёмка п. 282(г)(4) — ' + RG + ': листы FSc, строка установки «да / нет», пара `mini_giants_garden` как кандидат `SCENE_OK` по п. 221(г)(3) с поправками, '
  'строка «`SCENE_OK` Sky Garden на новом бинаре — подтверждается контрольным W следующей серии»; установка — не раньше `done` закрытия с. 145 (`HPP-354`): принятая до закрытия — шаг 0 цепочки с. 146, после — звено установки Harness Engineer вне серии сессии; пункт `ROADMAP.md` ДО `done`.'),
 ('F6a', 'lever', 'todo', [], 'трек F, звено F6a: проект Б9а (AudioPropagation, 4 неразрешённых импорта) без игры и без кода',
  'Роль: Lever Researcher. Итерация F6 строки **Б9а** по п. 282(ж) — ' + RZH + '; строка реестра — §4 «Б9а», §16. Без игры, без кода эмулятора, без сборок.\n'
  '1. **Имена 4 NID** (`b-dYXrjSNZU`, `WXMhENV2NcA`, `d84otraxt2s`, `G+QLTfyLMYk`): сначала по коду загрузчика эмулятора — как считается NID (ожидание [I]: base64 первых 8 байт SHA-1 имени с суффиксом); затем счёт против списков имён, которые есть на машине (таблицы NID эмулятора, символы модулей `games/PPSA21564-app/sce_module`, строки `eboot.bin`), или иной первоисточник со ссылкой. Веб недоступен; имя без источника — [I].\n'
  '2. **Сигнатуры и места вызова:** разбор мест вызова в `eboot.bin` (какие аргументы, что игра делает с возвратом, ветвится ли по нему); логи `C:/kyty/s142/log_c142_03.txt` (`timestop_casino`) — частота и порядок вызовов.\n'
  '3. **Вариант правки:** реализация, заглушка с верным возвратом/выходными параметрами или «НЕ ДЕФЕКТ» (возврат 0 = успех и игра не читает выходов) — с основаниями [c]/[I]; если имён и семантики нет — `ТУПИК` по п. 228(д) назвать явно.\n'
  '4. **Предложение критерия** в форме п. 228(г)(1) с N (как строка реестра: вход `timestop_casino` 120 с, 0 строк `Unresolved import stub called` с `AudioPropagation`, 0 маркеров смерти, видео 0 глитчей, тест на каждый NID, контроль `=0`).\n'
  'Документ `docs/track-f/f6a-b9a.md` (правило 24: карта ссылок с якорем и контролем +1, инвентарь условий, фазы со статусом), скрипты — `docs/track-f/f6a/`. Вопросы лиду — разделом документа.'),
 ('F6b', 'lead', 'blocked', ['F6a'], 'трек F, звено F6b: приёмка проекта Б9а, критерий F6 до кода (лид)',
  'Роль: Roadmap Lead. Приёмка F6a (правило 24 строкой), ответы на вопросы, критерий F6 (Б9а) до кода в форме п. 228(г)(1) или `ТУПИК`/`НЕ ДЕФЕКТ` по п. 228(д); звенья кода, ревью, прогонов и приёмки; пункт `ROADMAP.md` ДО `done`; корень `HPP-287` — `blocked` на новых звеньях.'),
]
ids = {}
out = []
for k, ag, st, bl, title, desc in LINKS:
    body = {'title': title, 'description': desc + COMMON, 'status': st, 'priority': 'medium',
            'parentId': PARENT, 'projectId': PROJ, 'assigneeAgentId': AG[ag]}
    if PWS:
        body['projectWorkspaceId'] = PWS
    if bl:
        body['blockedByIssueIds'] = [ids[b][0] for b in bl]
    if ag != 'lead':
        body['executionPolicy'] = REVIEW
    d = req('POST', '/api/companies/' + CO + '/issues', body)
    ids[k] = (d['id'], d['identifier'])
    stg = (d.get('executionPolicy') or {}).get('stages') or []
    if ag != 'lead':
        assert len(stg) == 1 and stg[0].get('type') == 'review', ('executionPolicy not set', k, d.get('executionPolicy'))
    out.append((k, d['identifier'], d['id'], d['status'], d.get('createdAt'), 'stages=%d' % len(stg) if ag != 'lead' else 'lead'))
    print(*out[-1], flush=True)
    json.dump({'chain': out}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
r = req('PATCH', '/api/issues/HPP-287', {'blockedByIssueIds': [ids['FSd'][0], ids['F6b'][0], H358], 'status': 'blocked'})
print('HPP-287', r.get('status'), [b.get('identifier') for b in r.get('blockedBy', [])])
