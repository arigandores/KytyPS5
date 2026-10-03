import json, os, sys, urllib.request
B = os.environ["PAPERCLIP_API_URL"].rstrip("/")
if B.endswith("/api"): B = B[:-4]
H = {"Authorization": "Bearer " + os.environ["PAPERCLIP_API_KEY"], "Content-Type": "application/json",
     "X-Paperclip-Run-Id": os.environ["PAPERCLIP_RUN_ID"]}
LEAD = "f1276629-91fd-414a-b13f-52d1445432c9"
EMU = "eb15eb75-9046-4c8a-b92c-be4254b9ee85"
RED = "dc34de0a-4911-443b-a2d4-7c99d2c9cd9e"
PARENT = "b240f674-60b2-45f5-85ab-a8c8da766607"  # HPP-287
PROJECT = "59d06676-20b6-4341-943e-d4f4c5c610b0"

def req(method, path, body=None):
    r = urllib.request.Request(B + path, method=method, headers=H,
                               data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode("utf-8"))

POLICY = {"mode": "normal", "commentRequired": True,
          "stages": [{"type": "review", "approvalsNeeded": 1, "participants": [{"type": "agent", "agentId": LEAD}]}]}

REF = ("решение — `9b6cbf7a:docs/ROADMAP.md:20924` п. 389 (якорь «389. **Звено F11g трека F (`HPP-469`, лид): F11f (`HPP-468`) ПРИНЯТ»; "
       "+1 — «достижим» по типам 2–3 на всех трёх сценах множества (Sky Garden, `voxel_world`, `big_hand_pirate_island`) [c счётчика]»)")
COMMON = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common_f.txt"), encoding="utf-8").read().replace("{REF}", REF)

F12A = ("Роль: Emu Engineer. Проект F12a по п. 389(д)(1)–(7): **первоисточник ответа железа** на указатель `IMAGE_BVH_INTERSECT_RAY` типов 0–3 "
        "(раскладка треугольного узла, какие вершины и идентификатор выбирают типы 2 и 3, поля результата) — ISA RDNA2 / GPURT / PAL / LLVM AMDGPU / Mesa "
        "с путём:строкой или страницей [c], не найден — исход «не определено»; **как программа `380bb9d636390bae` формирует указатель** (корпус T1 "
        "`C:/kyty/s288/s7/` или `eboot.bin`, дизассемблер — путь:строка вывода): тип из памяти узла или арифметикой кода; объяснение отношения "
        "t0 : t1 : t2 : t3 = 4 : 3 : 2 : 3 (точно на трёх сценах F11f) [c] или [U]; что эмулятор делает с типами 0–7 сейчас — путь:строка [c]; при исходе "
        "«ответ эмулятора ≠ ответу железа» — проект правки под `KYTY_FIX_F10` (умолчание 0; `=0` — SPIR-V байт в байт; смена подписи трансляции, форма, "
        "цена холодного кэша), GPU-тест с эталоном по первоисточнику (каждый тип 0–3, попадание и промах, точное равенство), форма доказательства картинки "
        "(где в кадре Sky Garden работает `380bb9d636390bae`, чем `=0`/`=1` различимы на листе); тип 6 и 7 по тому же первоисточнику (строка Ф18). "
        "Без кода `src/` и без игры; только чтение и офлайн. Отчёт `docs/track-f/f12a.md`, файлы `docs/track-f/f12a/` и `C:/kyty/f287/f12a/`. "
        "Исход отчёта — одно из трёх: «≠» ⇒ проект кода; «=» ⇒ предложение `НЕ ДЕФЕКТ`; «первоисточник не найден» ⇒ «ответ железа [U]». "
        "Данные — `e442ec59:docs/track-f/f11f.md:178` (якорь «| `d11_sg` | 140 956 303 | 5 075 932 | 3 806 949 | 2 537 966 | 3 806 949 |»; +1 — «| `d11_ef` | — "
        "(строки нет; есть только `DiagBvhNodes: mode=1 words=64 tail_bytes=320`)»); место — `e442ec59:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:2232` "
        "(якорь «const auto is_tri   = Binary(state, OpULessThan, boolt, node_type, U(2u));»; +1 — «const auto is_tri1  = ieq(node_type, U(1u));»).\n\n---\n" + COMMON)
F12B = ("Роль: Red Team. Враждебный отзыв проекта F12a по п. 389(д): первоисточник (подлинность, версия формата, применимость к железу PS5), чтение "
        "кода программы `380bb9d636390bae` и объяснение 4 : 3 : 2 : 3, путь эмулятора, проект правки, GPU-тест, форма доказательства картинки, "
        "тип 6/7. Вердикт SOUND / SOUND_WITH_CHANGES / UNSOUND с RC; отчёт `docs/track-f/f12b-review.md`, файлы `docs/track-f/f12b/`. Без кода и игры.\n\n---\n" + COMMON)
F12C = ("Роль: Roadmap Lead. Приёмка F12a и F12b; пункт `ROADMAP.md` ДО `done`: критерий «ИСПРАВЛЕНО Ф10» до кода и звенья кода и прогонов, либо строка "
        "реестра (`НЕ ДЕФЕКТ` / «ответ железа [U]», паркуется) — п. 389(д); строка Ф18; в обоих случаях — F13 = Б41 (очередь п. 366(д)). Корень `HPP-287` — "
        "на новом терминальном звене.\n\n---\n" + COMMON)

a = req("POST", f"/api/companies/{os.environ['PAPERCLIP_COMPANY_ID']}/issues",
        {"title": "трек F, звено F12a: первоисточник ответа железа на узлы типов 2–3 и проект Ф10 (Emu Engineer)", "description": F12A,
         "status": "todo", "priority": "medium", "assigneeAgentId": EMU, "parentId": PARENT, "projectId": PROJECT, "executionPolicy": POLICY})
print("F12a", a["identifier"], a["id"], json.dumps(a.get("executionPolicy", {}).get("stages")))
assert a.get("executionPolicy") and a["executionPolicy"].get("stages"), "F12a stages empty"
b = req("POST", f"/api/companies/{os.environ['PAPERCLIP_COMPANY_ID']}/issues",
        {"title": "трек F, звено F12b: отзыв проекта F12a (Ф10, типы 2–3) (Red Team)", "description": F12B,
         "status": "blocked", "priority": "medium", "assigneeAgentId": RED, "parentId": PARENT, "projectId": PROJECT, "executionPolicy": POLICY,
         "blockedByIssueIds": [a["id"]]})
print("F12b", b["identifier"], b["id"], json.dumps(b.get("executionPolicy", {}).get("stages")))
assert b.get("executionPolicy") and b["executionPolicy"].get("stages"), "F12b stages empty"
c = req("POST", f"/api/companies/{os.environ['PAPERCLIP_COMPANY_ID']}/issues",
        {"title": "трек F, звено F12c: критерий «ИСПРАВЛЕНО Ф10» до кода или строка реестра; F13 = Б41 (лид)", "description": F12C,
         "status": "blocked", "priority": "medium", "assigneeAgentId": LEAD, "parentId": PARENT, "projectId": PROJECT,
         "blockedByIssueIds": [b["id"]]})
print("F12c", c["identifier"], c["id"])
json.dump({"a": a["id"], "ai": a["identifier"], "b": b["id"], "bi": b["identifier"], "c": c["id"], "ci": c["identifier"]},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "f12ids.json"), "w"))
