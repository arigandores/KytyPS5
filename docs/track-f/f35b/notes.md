# F35b (HPP-756) — рабочие заметки Red Team (не отчёт; отчёт — docs/track-f/f35b-review.md)

Вход: п. 685 (`a2350134`), F35a `0d8bab3f` (§0 `1a4c9b24`, тест `13e120f2` / worktree `399d3271`).
Перечень мутантов до данных — комментарий `b27a70ba` в HPP-756 (19:39:30Z). Скрипты: `mut_f35b.py`, `run_all.sh`,
`guard.sh`, `build_f35b.cmd`; worktree `wt` на `399d3271`, сборка `build`. Запуск: `bash run_all.sh > run_all.log 2>&1`
(guard перед каждой сборкой: замок, STOP, серия HPP-752).

Пауза 19:40Z: HPP-752 FS12c `in_progress` (run 95e7b0fb) — по общему правилу 30 сборки (> 60 с) не запускаются.

## Статическая сверка (сделана, ee9632be)
- Путь теста: `RecompileForTest` (T.cpp:142) = TranslateProgram → ExtractResourcePlan → MaterializeResources(user_data,
  ReadHostTestMemory) → CompileProgram — специализация по T#, не готовая ✓ (RC11).
- Зеркало = код по ветвям: DS:2824 storage=written; DS:2835 IsNull (Base40, = NullImageDescriptor RM:127); NullTextureDesc
  DS:1320–1340 (Float→k32Float→R32; native_compare=Texture&&depth_compare&&!manual → D32); непустой DS:3033 format =
  descriptor.Format() = (f1>>20)&0x1FF (= F22TsharpFormat и = RM формат); DS:3072–3074 depth_compare && policy → depth.
  Входы зеркала = DS:4489 (program.info.images[i], snapshot.images[i]); тест берёт result.program (после
  ApplyResourceSpecialization) и result.resources (specialized_snapshot после ImageRemap) ✓. Неучтено зеркалом: класс
  Uint/Sint пустого (всё равно цвет), storage-вид (не Texture) — на меру не влияет.
- Кандидаты — копии корня: RM:492–497 (BuildResourceSpecialization), RM:1157–1159 (Apply) ⇒ depth_compare корня.
  Невалидный T# кандидата обнуляется (RM:314) = «пустой». Корень = первый найденный ключ (порядок обхода), дедуп RM:316.
- Опкод — по корню: EM:605 (images.at(mem.resource)), EM:683–685, EM:766–768, ветви OpSwitch тем же EmitSample (EM:800, 907).
- При =1: О1 RM:729–733 сводит manual по таблице; проход общего сэмплера RM:1206–1222 — только sampled_pairs (корень/прямые)
  и только ставит manual=true ⇒ Dref ⇒ все члены не ручные ⇒ пустой член D32 (DS:1337), непустой — формат политики ⇒ вид
  глубины (DS:3072). Т.е. при =1 «Dref по цветовому виду члена» невозможна в ЛЮБОЙ форме таблицы [c кода], не только §0.
- Следствие: правило пустого T# (m1a) не может менять меру — эквивалентный мутант для вопроса п. 685(б); m1b убивается.
- Тест при =1 не имеет строки с dref ≥ 1 (все формы с цветовым кандидатом ⇒ ручные). Строка {пустой, k32Float} дала бы
  Dref при =1 и ловила бы m1a печатью (dref 2→0, root_manual 0→1). Кандидат в замечание (не RC): ложного НЕ ДЕФЕКТ
  без неё нет по доводу [c] выше.
