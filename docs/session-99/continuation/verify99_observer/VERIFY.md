# Независимая VERIFY observer separation05 — PRESEAL

2026-09-19. Только исходники, синтетические данные и короткие Python тесты; игру, сборку, декодирование видео и production raw replay не запускал. Автор отчёта не менял scorer/protocol/tests.

**ТЕКУЩИЙ ВЕРДИКТ: FINAL PASS для алгоритма05 и отдельного визуального запуска900s**, после исправления F1 и проверки печати. Реальные игровые исходы этим не доказаны.

Исторический вердикт первой ревизии: **FAIL, исправить до печати/запуска CPU.** Обнаружен воспроизводимый пропуск целого внутреннего блока в A/A. Остальные перечисленные механизмы PASS по исходникам и синтетическим проверкам. Финальная печать и исходы игры НЕ ДОКАЗАНЫ.

## F1 — полностью отсутствующий внутренний блок A/A не отклонён

**FAIL.** pred/02_settled_bindings.md:61 требует отказ при missing INTERNAL blocks/rows; draft05:64 сохраняет full row completeness. Но settled99_norec.py:225 select перебирает только существующие blocks; :254 internal_incomplete получает только существующие incomplete. :294 принимает пустой список, :295 проверяет identity только оставшихся строк. В AA ветке :309/:376 нет старого EDGE, который в bf99.py:197 проверяет отсутствующие номера блоков.

Независимый контрпример: aa_fixture(blocks=80), удалить ровно90 строк blk8. Все12 technical=True и все5 strict=True; 36 полных пар, internal_incomplete=[]. Полный evaluate(..., mechanics=True) с temp raw/metadata/stdout дал все12 technical=True и все6 strict=True, errors только `mechanics-only; no admitted result or endpoint`. Значит protocol/fresh_area дыру тоже не закрывают. Нужна явная полнота внутренних номеров строк/блоков перед AA return, с отрицательным тестом; исходные02/04 не менять.

## Проверенные утверждения

* **PASS — неизменённая геометрия и численные полосы.** select и population в :225/:260 побайтово по inspect.getsource совпали с settled99.py и settled99_gc.py. idx60..88 =29 строк, пример blk4 n2221..2249; целые квартеты дают disjoint AB/BA. Численные проверки :354..358 и :400..406: area abs<1%, pair band<=0.5% с>=90% совпадений, work abs<0.5%, C5<=0.02, C9<=0.03. F1 касается обнаружения неполного raw, а не изменения selector.
* **PASS — A/A физически baseline.** :139..153 требует bindfloor=0/drawahead=1 в обоих текстах расписания, runtime GateArm проверяется :187..200. :376..406 считает сравнение по pseudo arm0/1, :382 требует нули floor/live/CPU-burn, отдельные whole-log GC invariants :299..305. B/endpoints в AA не формируются; не обещаются falling-edge/R2 доказательства (:612..619). :41 не принимает vis99base как CPU tag.
* **PASS — recorder запрещён и в metadata, и runtime.** :56..65 отклоняет любое наличие KYTY_REC, включая пустую строку/0; читает Recording: в raw и stdout, whitespace/case tolerated. Источник screenshot.cpp:494 печатает именно Recording:; commandRecorder.cpp:1069 RecordThread означает backend. Тест :107 проверил три env значения, два runtime канала и разрешение RecordThread. ImageLife запрещён :111..112/:164/:209. Entry конфигурация :89 сохраняет все KYTY_ поля без прежнего исключения recorder.
* **PASS по алгоритму — carried eng99a4 только exact artifact и оригинальный04 replay.** :512..546 закрепляет artifact SHA, scorer SHA, прежний pred04/binary/LOCK17800, все3 raw hashes, no-record source, затем вызывает CARRY04.evaluate под собственным04 и сравнивает metrics/technical/strict/decision/selection. Старый eng99a4 не становится новой identity05. Новый source chain :459..506 требует prelaunch source tag/hash, immediate predecessor для pilots, TUNE/LOCK и независимый replay. Реальный replay eng99a4 в этой VERIFY не запускался; тест :155 использует mock replay, что не равно независимому принятию production pilot.
* **PASS по алгоритму — AA provenance.** :549..570 требует exact AA artifact hash/tag в launch env, AA_PASS+seal+binary, три raw hash, evaluate AA заново и equality metrics/technical/strict/selection. :596..600 применяет gate ко всем measurement. Тест :176 отвергает отсутствие prelaunch hash и изменение selector. Реальные AA пока не доказаны.
* **PASS по плану — отдельное нормальное видео не даёт CPU число.** draft05 §3 задаёт идентичные bindfloor0 плечи, диагностический статус и запрет B/freeze; §6 отдельную последовательность процессов и отсутствие анализа в hold. Root сообщил продление600→900 для покрытия поздних артефактов~825s; это разумное изменение ДО печати. Визуальная корректность/отсутствие глитчей НЕ ДОКАЗАНЫ, live/video не проверялись.
* **PASS — нет глобальной лицензии.** :654..665 combine требует два admitted и разные a/c, addend=0, только HIGH/LOW/GAP diagnostic, global M3/G/R1 остаются неизменными.

## Проверки и фиксированные hashes первой ревизии

12/12 штатных тестов test_settled99_norec.py PASS за4.805s. Дополнительно два независимых F1 контрпримера (analyze и полный mechanics pipeline) показали ложный PASS. Фактические SHA:

- pred02 `1d1ebf286869ab59944fe135fc5c69d1315d4c61667b6c3dd2ab3ca14839724c`, совпал sealed constant.
- pred04 `a93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b`, совпал sealed constant.
- settled99_gc.py `be2a9a317fded5ee3ee6b421312d60e3fb6e9cd22c643eb3b7ec89a1258adef6`, совпал CARRY_SCORER_SHA.
- eng99a4_score.json `9f021e8bcc080f03a3309c851629f01c49b7f54868dd75b2a62b6ee28e175e8e`, совпал CARRY_ARTIFACT_SHA.
- проверенный settled99_norec.py `ea5c16960e69b94a8f72796231e15cfbfdc500c3a169deb6b50fd0ad4c5dbe35`.
- проверенный test_settled99_norec.py `7ec18560542c1c44c21bb04299c8e348e060ac203d39d43dbc0d13788a78f5a7`.

PRED_SHA=UNSEALED (:25) правильно блокирует production evaluate (:579). Протокол05 ещё draft; эта проверка не заменяет итоговую seal-pin проверку.

## Обновлённый визуальный draft — независимо проверено

**PASS для отдельного технического запуска.** В актуальном draft05:23..26 и :58..60 прямо ограничено заключение воспроизведением без floor в recorded path. Разделить renderer vs recorder или приписать regression этому binary невозможно; текст теперь этого не обещает. :45..51 hold900 вместо600 охватывает поздний период bf99e (~825s по сообщению root), оба плеча bindfloor0, B/freeze запрещены. Изменение до печати не меняет ни CPU selector, ни численные bands. Требование >=9000 recorded frames и раннее/среднее/позднее сопоставление — диагностика; outcome/survival ещё НЕ ДОКАЗАНЫ.

## Независимая повторная проверка после F1 — PRESEAL PASS

Проверенные финальные до печати bytes: settled99_norec.py SHA256 `d5604ee14a7d64f2549681c889643829ad6952158359bd7cfd74dd304df9980e`; test_settled99_norec.py `08e3f487036070a8f793a3d0a49742f6bcab1630c392e42de670335a4734f474`; draft05 `7e5f1372b3340e0af11aa2a80384bbfe1e4442c803b25192bab3c500687756c4`. Pred04 и старый scorer сохранили прежние SHA выше.

**PASS F1 закрыт.** :174..175 raw protocol теперь отклоняет разрыв или неверный порядок main frame. :230..231 select фиксирует frame_gaps; :250..252 добавляет отсутствующие внутренние блоки в rejected; :303..306 technical требует INTERNAL_ROWS_COMPLETE/FULL_RAW_CONTIGUITY/FULL_RAW_ORDER перед AA return. Это восстановление исходной полноты; данные не подбираются по endpoint, bands не изменены.

Повторил собственный прежний mutant: удаление90строк blk8 теперь даёт FULL_RAW_CONTIGUITY=False, INTERNAL_ROWS_COMPLETE=False, frame_gaps=[[2521,2610]], internal_incomplete=[8]. Полный mechanics pipeline возвращает явную ошибку `raw main-frame sequence has a gap or is out of order`. Независимо добавил дубликат main n2801: три ошибки (duplicate stream, duplicate duration, sequence); переставил main n2801/2802: sequence error. Чистая fixture: protocol errors=[].

Независимый повтор всех новых штатных тестов: **14/14 PASS за6.270s**. На полной fixture80блоков новый selector сохранил все прежние поля равными исходному04 selector (добавились только integrity diagnostics):38пар, blk4 n2221..2249, прежние disjoint balanced quartets.

Алгоритм05 и обновлённый отдельный visual900 протокол готовы к печати. Предыдущий FAIL не скрыт; финальный PRED_SHA/bytes требуется сверить после seal. Реальные AA/confirmation/source replay, визуальная корректность и причинная атрибуция по-прежнему НЕ ДОКАЗАНЫ этой проверкой.

## Финальная печать — PASS

pred/05_observer_separation.md:8583 bytes, SHA256 `fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0`; settled99_norec.py:25 PRED_SHA совпал точно. Финальный scorer SHA256 `8216acd9797f7b2eeb61f2654a7827daed3f103ac0a07ec3b80a570ae6626399`. Независимо восстановил только PRED_SHA=UNSEALED в памяти: hash стал ровно ранее проверенным d5604ee1..., то есть после14тестов поменялась ТОЛЬКО печать.

Финальный §7 честно сохраняет обнаруженный дефект,14 synthetic тестов, и требование реального исходного04 source replay до принятия CPU. **FINAL PASS для готовности алгоритма05 и отдельного визуального контроля900s.** Все host задачи этого проверяющего остановлены до окончания hold/нового задания root. Ни одна игра/сборка/видеоанализ не запущены этим проверяющим.

## Фактический eng99a4 replay под оригинальным04 — PASS

После окончания игрового hold root отдельно разрешил реальные raw. Запущен ровно read-only CLI `python C:/kyty/s99/settled99_gc.py eng99a4`, без --out, без правки старого artifact. Процесс scorer завершился exit0 за20.659s, stdout15118 bytes, stderr0 bytes. Новый stdout сохранён отдельно: `verify99_observer/eng99a4_replay_stdout.json`.

**PASS: весь JSON И все bytes свежего stdout совпали со старым eng99a4_score.json**, SHA256 `9f021e8bcc080f03a3309c851629f01c49b7f54868dd75b2a62b6ee28e175e8e`. ENGINEERING_COMPLETE, errors=[], decision LOCK/fixed_burn17800. Все40/40 technical и6/6 strict PASS. Pred04 SHA `a93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b`, scorer SHA `be2a9a317fded5ee3ee6b421312d60e3fb6e9cd22c643eb3b7ec89a1258adef6` совпали до и после. Replay использовал собственную неизменённую печать04, не05.

**Числа воспроизвелись:** work5036.843260188088→5035.652037617555 draws/flip,−0.023650181453%; area−0.015102132731%; match22/22=100%;22 независимые пары, AB/BA11/11,638 retained rows/arm. dt_U49631.72727272727us, dt_A49629.63009404389us, delta+2.09717868338339us, относительное расхождение0.00422547994725%. Survival300.1s;12 completed falls (pilot минимум8). GC checks50242, hold17490, bad/critical/evict0/0/0.

**Raw provenance3/3 PASS**, фактические SHA совпали со старым и свежим JSON:
- eng99a4.json `5f052e4fe07138be0d8d7d1d43e724c8fb95b4c5d1e8becda05ae5227899388b`;
- log_eng99a4.txt `5fe17e7c57ce124bc80f1b4043ab361537bc2429b859ff230220ce0e8646c5c5`;
- stdout_eng99a4.txt `865d1ce06697862235798ee0348b7f760b08738fe07ff2263da0670a4183d3b0`.

Отдельно вызван no_recording по настоящей metadata и обоим raw/stdout: errors=[], KYTY_REC отсутствует и runtime Recording: не найден. **Ранее не доказанный реальный source replay теперь закрыт PASS** для единственного exact eng99a4 source.

Ограничения сохранены: это инженерный LOCK, не B/confirmation и не доказательство корректности изображений. В исходном reported тексте по-прежнему R6′ FAIL60>50 и старый R3 FAIL; они не скрыты и не переопределены. Действуют неизменённые deciding controls04 (прямой GC audit, repaired R3′). AA/новые05 confirmations этим не приняты, globalM3/G/R1 не изменены.
