# F2d (HPP-311): create links F3b, F3c, F3d, F3e per ROADMAP p.259(zh) (f8396bed); specialist links with the lead's review stage
# (executionPolicy checked in the API answer); then HPP-287 blocked on HPP-338 and F3e.
import json, os, urllib.request
B = os.environ['PAPERCLIP_API_URL'].rstrip('/')
if B.endswith('/api'):
    B = B[:-4]
H = {'Authorization': 'Bearer ' + os.environ['PAPERCLIP_API_KEY'], 'Content-Type': 'application/json',
     'X-Paperclip-Run-Id': os.environ['PAPERCLIP_RUN_ID']}
CO = os.environ['PAPERCLIP_COMPANY_ID']
OUT = 'C:/kyty/f287/lead/chain_f3.json'
assert not os.path.exists(OUT), 'chain already created'
def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(B + path, data=data, method=method, headers=H)
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode('utf-8'))
AG = {'emu': 'eb15eb75-9046-4c8a-b92c-be4254b9ee85', 'red': 'dc34de0a-4911-443b-a2d4-7c99d2c9cd9e',
      'harn': '2f5a0935-2e1a-4a76-8d98-67897fca3b8b', 'lead': 'f1276629-91fd-414a-b13f-52d1445432c9'}
cur = req('GET', '/api/issues/HPP-311')
PARENT, PROJ, PWS = cur['parentId'], cur['projectId'], cur.get('projectWorkspaceId')
REVIEW = {'mode': 'normal', 'commentRequired': True,
          'stages': [{'type': 'review', 'approvalsNeeded': 1, 'participants': [{'type': 'agent', 'agentId': AG['lead']}]}]}
H333 = req('GET', '/api/issues/HPP-333')['id']
H338 = req('GET', '/api/issues/HPP-338')['id']
REF = ('`f8396bed:docs/ROADMAP.md:13592` «259. **Приёмка F2 (Б26б) и F3a (Б1б), критерий F3 до» (п. 259; контроль +1 — 13593 «по `date -u`, записано ДО создания звеньев F3»); '
       'критерий F3 — `f8396bed:docs/ROADMAP.md:13641` «(е) **Критерий F3 (Б1б + Ф9), до ко» (контроль +1 — 13642 «(1) **Семантика**»)')
COMMON = ('\n\n**Общие правила трека F (п. 228, п. 237, п. 259):** решение и критерий итерации — ' + REF + '; форма трека — `beb36ab0:docs/ROADMAP.md:12074` «Трек F» (п. 228); '
  'правило печати п. 258(д) (член сверх пункта — «член исполнителя [I]», вердикта не задаёт). Читать п. 228, п. 237(д), п. 256, п. 258, п. 259 целиком до первого действия; '
  'проект — `f8396bed:docs/track-f/f3a-b1b.md`; реестр — `f8396bed:docs/track-f/register.md` (§11). Файлы — `C:/kyty/f287/<звено>/`, в git — `docs/track-f/<звено>/`. '
  'Раздел звена в `C:/kyty/f287/FACTS.md` ДО `done`, время — UTC по `date -u`, строки событий — `C:/kyty/f287/times.txt`. '
  '**Общее правило 27:** первая строка каждой команды — `[ -e C:/kyty/SEALED_RUN.lock ] && exit 3` (кроме команд Harness Engineer внутри своего замка); при замке не запускать процессов (сборка — тоже процесс) и не писать файлов. '
  'Стоп: перед каждой командой дольше 60 с — `[ -e C:/kyty/f287/STOP ] && exit 4` в той же команде и проверка комментариев звена `GET …/comments?after=<последний>`; найденный стоп — строка `times.txt` с обоими временами (общее правило 26). '
  '`find /` запрещён; процессов после хартбита не оставлять (общее правило 28). '
  'Ссылки на изменяемые документы — `<коммит>:<путь>:<строка>` с якорем и контролем +1 (общее правило 24(1)). Коммит — `C:/Program Files/Git/cmd/git.exe` с `GIT_AUTHOR_*`/`GIT_COMMITTER_*` в том же вызове и `--only` (ловушка 11); push — нет. '
  'Кириллица в API — только JSON из Python через stdin. PATH в Bash — `export PATH=/usr/bin:/mingw64/bin:$PATH`; `PYTHONIOENCODING=utf-8`. '
  'Игру запускает только Harness Engineer под замком `C:/kyty/SEALED_RUN.lock` (очередь: цепочка сессии > трек P > трек F > трек S). Никаких `tail -F`, фоновых процессов вместо ожидания, `run_in_background`. Сдача — `done` (платформа отдаёт на review лиду).')
WIN = ('**Окно для сборок и тестов (п. 259(ж)):** команда сборки или тестов идёт, только если в той же команде нет `C:/kyty/SEALED_RUN.lock` и `HPP-332` (прогоны с. 144) не `in_progress` '
       '(ответ API — строкой `times.txt`); иначе — ждать `done` `HPP-333` (аудит с. 144). ')
LINKS = [
 ('F3b', 'emu', 'todo', [], 'трек F, звено F3b: правка Ф9/Б1б — база дескриптора BVH со сдвигом 8 под KYTY_FIX_B1B',
  'Роль: Emu Engineer. Итерация F3 строк **Б1б + Ф9** (п. 259(е)(2)–(3)), первая итерация кода. Вход — проект F3a `docs/track-f/f3a-b1b.md` §3, §7 (вариант V1).\n'
  '1. **До кода (п. 259(е)(2)):** сопоставить 40 инструкций `S_BFE_U64 …, 0x00280008` (20 мест) `eboot.bin` с BVH-программами игры (все, где есть `IMAGE_BVH_INTERSECT_RAY`; число — по коду) и назвать форму дескриптора у каждой; '
  'перечень всех мест `src/`, где декодируется база дескриптора BVH (ожидание 2: `20b39318:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:2216`, `20b39318:src/graphics/shader/recompiler/frontend/translate/Memory.cpp:872`); '
  'предсказание числом (пар «X / X>>8» при `=1` — 0). Иная форма у какой-либо программы — **стоп и вопрос лиду до кода**.\n'
  '2. **Правка V1 (п. 259(е)(3)):** ручка `KYTY_FIX_B1B`, умолчание 1; `0` — прежний адрес байт в байт. База = поле 40 бит (`desc0 | (desc1 & 0xff) << 32`) `<< 8` в обоих путях (`KYTY_BVH_NATIVE` 1 и 0). '
  'Токен ручки — в подписи и каталоге кэша трансляции; `=0`/`=1` кэш не делят, и с любым значением `KYTY_FIX_B26`. V2–V5 (граница `size`, типы 2–3, предел 4 096, `KYTY_BVH_STUB`) — не делать.\n'
  '3. **Тесты:** адрес узла в обоих путях — база 40 бит, сдвиг 8, биты слова 1 выше поля (`box_grow_value`, `box_sort_en`) в адрес не попадают, путь 64-битного указателя узла не меняется — `ALL OK` при `=1` и прежнее поведение при `=0`; '
  '`shader_cfg_tests` — падений не больше, чем у той же сборки при `=0` (оба списка в отчёт).\n'
  '4. **Сборка** (`cmd //c "C:\\kyty\\build_local.cmd"`), копия `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, sha256, подпись транслятора при `=1` и `=0`; коммит в `main` (src, tests, `docs/track-f/f3b/`). '
  '`git diff ba3be480 <коммит сборки> -- src/` — перечень каждой иной правки (ожидание: F4a `1713a8be` под `KYTY_FIX_DUALSRC` с умолчанием 0, S5a/S5c под `KYTY_S_PCW`; если в `main` к этому моменту есть доработка F4 по RC F4b — назвать). '
  'Установленную `9235a7ac` в папке эмулятора не трогать; игру не запускать.\n' + WIN +
  'Отчёт `docs/track-f/f3b.md`: сопоставление программ, места декодирования, правка, тесты, sha бинаря и подписи, коммит, diff, предсказание.'),
 ('F3c', 'red', 'blocked', ['F3b'], 'трек F, звено F3c: код-ревью правки Ф9/Б1б (F3b)',
  'Роль: Red Team. Код-ревью F3b по п. 228(г)(3) и п. 259(е)(2)–(3): (1) формат дескриптора — своим чтением первоисточника (PAL `gfx9Device.cpp:5334`, `gfx10_sq_ko_reg.h:99–111`; копии `C:/kyty/f287/f3a/src_ext/`) и кода игры (`S_BFE_U64 …, 0x00280008`); '
  '(2) правка чинит механизм (адрес узла), а не прячет маркер (`BvhLoopCapTrip:`, промахи); (3) `=0` — прежний адрес байт в байт, тестом или кодом; (4) токен ручки в подписи и каталоге кэша, сочетание с `KYTY_FIX_B26`; '
  '(5) тесты — свой прогон, `ALL OK`, падения `shader_cfg_tests` `=1` против `=0`; (6) оба пути (`KYTY_BVH_NATIVE` 1/0), путь 64-битного указателя; (7) сопоставление BVH-программ F3b — перепроверить выборочно; (8) `git diff ba3be480 <коммит> -- src/` — перечень иных правок. '
  'Вердикт SOUND / SOUND_WITH_CHANGES / UNSOUND, RC с владельцем. Игру не запускать. ' + WIN),
 ('F3d', 'harn', 'blocked', ['F3c', 'H333'], 'трек F, звено F3d: доказательные прогоны Ф9/Б1б под замком (бинарь F3b)',
  'Роль: Harness Engineer. Прогоны п. 259(е)(4)–(6) на бинаре F3b (`C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, sha — из отчёта F3b/F3c). Если вердикт F3c UNSOUND — `NOT EVALUABLE` без замка и вопрос лиду. '
  'Старт — после `done` аудита с. 144 `HPP-333` (общее правило 27); очередь замка — сессия > P > F > S; если F4c (`HPP-337`) ждёт замка одновременно — F4c первым.\n'
  '**Харнесс** — порт `C:/kyty/f287/f2c/go_f2c.sh` (установка бинаря правки, возврат `9235a7ac` с проверкой sha, копия и возврат `_ShaderCache/PPSA21564` (корень и все каталоги вариантов) и `GLCache` (`GLRESTORE=1`, п. 256(в)), манифесты, стоп-файл при провале возврата). '
  '**Скорер** — фикстуры на каждый член п. 259(е)(4)–(6): пары «промах X ≥ 4 ГиБ и промах страницы `(X >> 8) & ~0x3fff`» (0 при `=1`, ≥ 1 при `=0`), промахи ниже 4 ГиБ при `=1` (каждый — строкой с адресом), строки `BvhLoopCapTrip:`, маркеры смерти, K2, Σ`dt_us` удержания после первого кадра сцены (п. 221(в)), форма W п. 254(е), среднее `dt` V (число, не гейт). Без мутантов. '
  '**Печать** `pred/01_f3d.md` — п. 259(е) дословно; член сверх пункта — по п. 258(д).\n'
  '**Теги:** (а) `big_hand_pirate_island`, `voxel_world` — по два входа `KYTY_FIX_B1B=1` подряд (первый холодный: только (4) и маркеры смерти; второй — удержание 120 с, видео, `s51_vidglitch.py 4 6`, лист); '
  '(б) Sky Garden `=1`: V ≥ 300 с (стена 330 с), видео ≥ 3 000 кадров, лист «`v142` / F3d» по тем же позициям кадров; W — `--vulkan-validation true` + `KYTY_PIPELINE_PRECACHE=0`, ≥ 300 с (стена 310 с), 0 `[Vulkan][E]`, активность валидации по трём признакам п. 224; '
  '(в) контроль `KYTY_FIX_B1B=0` — оба уровня по одному входу 120 с. Удержание меньше названного — `NOT EVALUABLE`, повтор — только строкой лида.\n'
  'Исход — таблица в `FACTS.md` в форме F2c, зеркало `docs/track-f/f3d.md`.'),
 ('F3e', 'lead', 'blocked', ['F3d'], 'трек F, звено F3e: приёмка F3 (Ф9 + Б1б), звено отгрузки трека F (лид)',
  'Роль: Roadmap Lead. Приёмка итерации F3 по критерию п. 259(е): листы видео (уровни и Sky Garden «`v142` / F3d»), `FIXED` / следующая итерация / `ТУПИК`; '
  'регрессионный вход п. 228(г)(5) — по п. 259(е)(8); звено отгрузки трека F (бинарь `main` со всеми принятыми `KYTY_FIX_*`, регрессия Sky Garden ≥ 300 с, строка установки) — по п. 259(б), если F3e — последняя терминальная из F3e и F4d `HPP-338` и аудит с. 144 `HPP-333` — `done`; '
  'следующая итерация очереди F (F0 §6: Б9а, Б11 (+Ф3), Б4, Ф5/Ф7); пункт `ROADMAP.md` ДО `done`; следующая приёмка создаётся ДО `done`; корень `HPP-287` — `blocked` на новых звеньях.'),
]
ids = {'H333': (H333, 'HPP-333')}
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
r = req('PATCH', '/api/issues/HPP-287', {'blockedByIssueIds': [H338, ids['F3e'][0]], 'status': 'blocked'})
print('HPP-287', r.get('status'), [b.get('identifier') for b in r.get('blockedBy', [])])
