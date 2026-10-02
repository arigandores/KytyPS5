#!/usr/bin/env python3
# F6f (HPP-378): track F iteration F7 = diagnosis of B39 (ROADMAP p.{N}(e)). F7a blocked on HPP-378, F7b on F7a, F7c on F7b; HPP-287 blocked on
# F7c and HPP-384. Executor links carry the lead review stage; the script fails if executionPolicy.stages is empty. LOCAL ONLY.
import json, os, sys, urllib.request

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
N = sys.argv[1]
CMT = sys.argv[2]
B = os.environ["PAPERCLIP_API_URL"].rstrip("/")
if B.endswith("/api"):
    B = B[:-4]
KEY = os.environ["PAPERCLIP_API_KEY"]
RUN = os.environ.get("PAPERCLIP_RUN_ID", "")
CO = os.environ["PAPERCLIP_COMPANY_ID"]
LEAD = "f1276629-91fd-414a-b13f-52d1445432c9"
HE = "2f5a0935-2e1a-4a76-8d98-67897fca3b8b"
EMU = "eb15eb75-9046-4c8a-b92c-be4254b9ee85"
OUT = "C:/kyty/f287/lead/chain_f7.json"
assert not os.path.exists(OUT), "chain already created"


def req(method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    r = urllib.request.Request(B + path, data=data, method=method)
    r.add_header("Authorization", "Bearer " + KEY)
    r.add_header("Content-Type", "application/json")
    if RUN:
        r.add_header("X-Paperclip-Run-Id", RUN)
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode("utf-8"))


cur = req("GET", "/api/issues/HPP-378")
F6F = cur["id"]
ROOT, PROJECT, PWS = cur["parentId"], cur["projectId"], cur.get("projectWorkspaceId")
REF = "`%s:docs/ROADMAP.md` п. %s(е) (якорь «(е) **Итерация F7 трека F = диагностика Б39»; +1 — «Звенья (у звеньев исполнителей — стадия review лида»)" % (CMT, N)

COMMON = """

---
**Общие правила трека F (п. 228, п. 259, п. 282, п. 287, п. 309(е)(1), п. 322, п. %s):** форма трека — `beb36ab0:docs/ROADMAP.md:12074` «Трек F» (п. 228); решение — %s. Читать п. 228, п. 309(е)(1), п. 322, п. 324(е), п. %s целиком до первого действия; реестр — `docs/track-f/register.md` §21 (строка Б39), §22–§23. Источник Б39: лист `C:/kyty/s145/sheet_v145_17.png`, кадры `C:/kyty/s145/step4/hud/v17_frames.png`, лог `C:/kyty/s145/log_v145_17.txt`, W `w145_17` — 0 `[Vulkan][E]`. Файлы — `C:/kyty/f287/<звено>/`, в git — `docs/track-f/<звено>/`. Раздел звена в `C:/kyty/f287/FACTS.md` ДО `done`, время — UTC по `date -u`, строки событий — `C:/kyty/f287/times.txt`. **Общее правило 27:** первая строка каждой команды — `[ -e C:/kyty/SEALED_RUN.lock ] && exit 3` (кроме команд Harness Engineer внутри своего замка); при чужом замке не запускать процессов (сборка, реплей RenderDoc — тоже процессы) и не писать файлов; запись файла и комментарий — одной командой с проверкой замка; процесс с устройством Vulkan у звена без замка — только если ни одна задача с проверкой GLCache или загрузки ГП между тегами не `in_progress` (п. 277(г), ответ API — строкой `times.txt`). Стоп: перед каждой командой дольше 60 с — `[ -e C:/kyty/f287/STOP ] && exit 4` в той же команде и проверка комментариев звена `GET …/comments?after=<последний>`; найденный стоп — строка `times.txt` с обоими временами (общее правило 26). `find /` запрещён; процессов после хартбита не оставлять; имя постороннего приложения — `<app>`, перед `git commit --only` — `git grep -P -f C:/kyty/scrub/checks.txt -- <добавляемые пути>` (общее правило 28). Ссылки на изменяемые документы — `<коммит>:<путь>:<строка>` с якорем и контролем +1 (общее правило 24(1)). Коммит — `C:/Program Files/Git/cmd/git.exe` с `GIT_AUTHOR_*`/`GIT_COMMITTER_*` в том же вызове и `--only` (ловушка 11); push — нет. Кириллица в API — только JSON из Python через stdin. PATH в Bash — `export PATH=/usr/bin:/mingw64/bin:$PATH`; `PYTHONIOENCODING=utf-8`. Игру запускает только Harness Engineer под замком `C:/kyty/SEALED_RUN.lock` через `procload.py` (очередь после с. 146: P > F > S, п. 322(г)). Никаких `tail -F`, `run_in_background`, внешнего `timeout` вокруг прогона; прогон и разбор — синхронно в хартбите. Вопрос лиду — комментарием с упоминанием и строкой в `HPP-3`; монитор — только с текущими `stages` (ловушка 12). Сдача — `done` (платформа отдаёт на review лиду). Не заявлять: что пол `enemy_final` неверен или верен до вывода звена с основаниями [c]; что сцена корректна; ни одно число — не выигрыш; 60 FPS не обещать.""" % (N, REF, N)

REVIEW = {"mode": "normal", "commentRequired": True,
          "stages": [{"type": "review", "approvalsNeeded": 1,
                      "participants": [{"type": "agent", "agentId": LEAD}]}]}

STEPS = [
    ("f7a", HE, ["f6f"], "трек F, звено F7a: снимок RenderDoc кадра арены enemy_final под замком (диагностика Б39)",
     "Роль: Harness Engineer. Снимок по " + REF + ". Стартует после `done` F6f (`HPP-378`). **Окно:** очередь замка P > F > S (п. 322(г)) — ни одно звено трека P с замком не `in_progress` (порт `win_f6e.py`), замка нет; ожидание `idle142` и один повтор отказа BUSY (п. 279(в)). **Форма:** установленный бинарь `dac02fb9` (sha256 сверяется до замка и строкой внутри; закреплённая копия `C:/kyty/s146/kyty_emulator_dac02fb9.exe`), умолчания (ни одной `KYTY_FIX_*` в окружении), без валидации, precache по умолчанию, `-lvl enemy_final`, `--rd` (RenderDoc 1.46), `KYTY_RD_FLIPS=2`, `FrameTrace`. **Кадр:** после первого кадра сцены, когда пол арены в кадре (ориентир — лист `C:/kyty/s145/sheet_v145_17.png`: пол во всех клетках удержания); механизм захвата и номер кадра (от первого кадра сцены по `FrameTrace` лога `C:/kyty/s145/log_v145_17.txt`; под RenderDoc игра идёт медленнее) выбираешь ты и пишешь строкой `times.txt` до замка. **≤ 2 попыток:** вторая — только если миниатюра (`renderdoccmd thumb`) не показывает пол арены или `rd_list.py` даёт ≤ 1 draw; номер кадра второй попытки — строкой до неё. Копия и возврат `_ShaderCache/PPSA21564` (корень, каталоги вариантов, `pipelines.bin`) и `GLCache` — форма F6e (`C:/kyty/f287/f6e/go_f6e.sh`); после захвата `qrenderdoc.exe` может зависнуть — `taskkill //F //IM qrenderdoc.exe`. **Выход:** `C:/kyty/f287/f7a/enemy_final_<n>.rdc` с sha256 (сам `.rdc` в git не кладётся), миниатюра `.png`, список draw (`rd_list.py`: число draw, проходы, цели), лог прогона с sha256, отчёт `docs/track-f/f7a.md` (форма, кадр, попытки, возврат кэшей, sha). Код эмулятора не трогать." ),
    ("f7b", EMU, ["f7a"], "трек F, звено F7b: разбор draw пола арены enemy_final по снимку RenderDoc (диагностика Б39), вывод дефект / НЕ ДЕФЕКТ / не определено",
     "Роль: Emu Engineer. Разбор по " + REF + ". Вход — снимок F7a (`C:/kyty/f287/f7a/`, отчёт `docs/track-f/f7a.md`). Игру не запускать; код `src/` не менять (только скрипты разбора в `C:/kyty/f287/f7b/`). Реплей RenderDoc (`qrenderdoc.exe --python`, скрипты `C:/kyty/scripts/rd_*.py`, обязателен `os._exit`) — процесс с устройством Vulkan: только без замка и по п. 277(г). **Разбор:** (1) draw пола — историей пикселей не менее чем в 3 точках пола (координаты — строкой); (2) у каждого такого draw — хэш PS и VS, привязанные образы (формат, размер, тайлинг, мипы, статистика содержимого: однородна ли текстура, совпадает ли с данными гостя по адресу, если доступно), сэмплеры, константы, участвующие в цвете, цель и смешивание; (3) SPIR-V PS (`spirv-dis`; дамп — из снимка или `--graphics-debug-dump` не назначается) — какие чтения дают цвет пола; (4) сравнение с соседними draw той же сцены, у которых материал есть (стены арены, Астро). **Вывод одним из трёх:** (а) **дефект** — место (трансляция, загрузка или детайлинг образа, дескриптор, формат, состояние) с [c] и предложение критерия до кода (что изменится в снимке и на видео, ручка `KYTY_FIX_B39`, умолчание 0); (б) **`НЕ ДЕФЕКТ`** — основание [c] (материал плоский в данных игры: образ однороден в памяти гостя или цвет задан константой); (в) **не определено** — чего не хватает и чем добыть. Каждое число — [c] с путём и sha256, оценка — [I]. Отчёт `docs/track-f/f7b-b39.md`; коммит — своим вызовом `git.exe --only`."),
    ("f7c", LEAD, ["f7b"], "трек F, звено F7c: приёмка диагностики Б39 (лид) — критерий до кода и звенья F8, или отзыв Red Team на НЕ ДЕФЕКТ, или следующий шаг",
     "Роль: Roadmap Lead. Приёмка F7b по " + REF + ": пункт `ROADMAP.md` ДО `done`; вывод (а) — критерий до кода пунктом и звенья F8 (Emu Engineer код → Red Team ревью → Harness Engineer прогоны → лид приёмка); вывод (б) — до строки `НЕ ДЕФЕКТ` враждебный отзыв Red Team звеном, которое создаёт F7c (строка переоткрывает `SCENE_OK` `enemy_final` строкой закрытия, п. 309(е)(1)); вывод (в) — следующий шаг диагностики пунктом; строка реестра §24; следующая итерация очереди F (Ф10, затем Б41 — п. 324(е)) — создаётся ДО `done`; корень `HPP-287` — на новом терминальном звене и FS2d."),
]

out = []
ids = {"f6f": F6F}
for key, agent, blockers, title, body in STEPS:
    payload = {"title": title, "description": body + COMMON, "status": "blocked", "priority": "medium",
               "assigneeAgentId": agent, "parentId": ROOT, "projectId": PROJECT,
               "blockedByIssueIds": [ids[b] for b in blockers]}
    if PWS:
        payload["projectWorkspaceId"] = PWS
    if agent != LEAD:
        payload["executionPolicy"] = REVIEW
    d = req("POST", "/api/companies/%s/issues" % CO, payload)
    ids[key] = d["id"]
    st = (d.get("executionPolicy") or {}).get("stages") or []
    if agent != LEAD:
        assert len(st) == 1 and st[0].get("type") == "review", ("executionPolicy not set", key, d.get("executionPolicy"))
    out.append((key, d.get("identifier"), d["id"], d.get("status"), d.get("createdAt"), "stages=%d" % len(st),
                [b.get("identifier") for b in d.get("blockedBy", [])]))
    print(*out[-1], flush=True)
    json.dump({"chain": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

h384 = req("GET", "/api/issues/HPP-384")["id"]
d = req("PATCH", "/api/issues/%s" % ROOT, {"status": "blocked", "blockedByIssueIds": [ids["f7c"], h384]})
print("root", d.get("identifier"), d.get("status"), [b.get("identifier") for b in d.get("blockedBy", [])])
