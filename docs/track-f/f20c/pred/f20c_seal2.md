# F20c (`HPP-561`, Harness Engineer): печать 2 — сторож игры пользователя (п. 534, общее правило 33)

Печать 2 после инцидента `f20_v11` и до первого тега после паузы. Решение — `ROADMAP.md` п. 534 (KytyPS5 `83b5da6e`, якорь «534.»),
комментарий лида `e7dc1438` (2026-10-05 07:44:10Z); общее правило 33 — `docs/agent-team.md` (ps5-em `8374372`). Метки: [c] — код
прочитан / проверен фикстурой, [I] — вывод.

## 0. Что не меняется

- Ридер `f20c_read.py`, его набор, чувствительность, регрессия и правила чтения п. 462(г)–(д) — без изменений (строки `seal:` ниже
  совпадают с печатью 1).
- `pred/f20c_seal.md` (sha256 `c34f5f2f…`) — без изменений; цепочка по-прежнему передаёт её в `enter_scene.py --pred`, поэтому поле
  `prereg` json тегов после паузы равно полю тегов `f20_v01`…`f20_v10`, и член допуска «`prereg` = sha256 печати» ридера не меняется.
- Форма тега, бинарь, кэши, очередь замка, предел 6 тегов подряд, окно FS6b — прежние.

## 1. Места правки (дифф — `docs/track-f/f20c/seal1_files/*.diff`)

1. **Убийство только по своему PID (п. 534(1)).** `go_f20c.sh` строки 70–71 (выход `finish()`) и 123 (после прогона): вместо
   `taskkill //F //IM kyty_emulator.exe` — `guard_f20c.py kill-own --pidfile runs/<тег>/game_pid.txt` (`taskkill /F /T /PID <свой pid>`;
   свой = pid файла, записанного `enter_scene.py` сразу после `Popen`, с временем создания процесса в пределах 15 с от записанного).
   `enter_scene.py:395` (`kill_game`): запасной `taskkill /F /IM` убран — после `taskkill /F /T /PID` и ожидания 20 с — `kill()` своего
   дескриптора. Запись pid-файла — по переменной `F20C_PIDFILE` (не `KYTY_*`, в json `env` не попадает).
2. **Проверка до замка и сразу после взятия (п. 534(2)).** `go_f20c.sh:52`: вместо `tasklist` по имени — `guard_f20c.py scan` (эмулятор
   пользователя = любой `kyty_emulator.exe`, кроме своего; лаунчер = любой другой процесс, чей файл лежит в папке с `kyty_emulator.exe`;
   имена и пути не печатаются — `<app> pid <n> kind <вид>`). Найден до замка ⇒ отказ 3, блок закрыт. Сразу после строки `lock taken` и до
   манифеста — та же проверка; найден ⇒ замок снят (строка `lock released`), кэши не тронуты, `runs/<тег>` → `<тег>.user_*`, блок закрыт,
   тег — помеха (повтор тем же именем).
3. **Блок тегов (п. 534(3)).** `launch_f20c.sh` после окна FS6b: `guard_f20c.py check` (находка ⇒ блок закрыт, строка `times.txt`,
   выход 7, помеха) и `status` (блок открыт и в нём < 6 тегов, иначе выход 8, строка `times.txt`); затем строка `TAG` блока. Блок
   открывает только `guard_f20c.py open-block`: чистая проверка при более ранней чистой проверке ≥ 600 с назад и без находки, `OPEN` или
   `CLOSE` между ними; файл блока `C:/kyty/f287/f20c/guard_block.txt`. Шестой тег блока закрывает его (`CLOSE limit6`); очередь `BUSY`
   закрывает блок вручную (`guard_f20c.py close queue`).
4. **Появление во время тега (п. 534(4)).** `go_f20c.sh` перед `enter_scene.py` запускает `guard_f20c.py watch` (опрос 2 с): процесс
   пользователя в двух опросах подряд ⇒ файл `runs/<тег>/USER_FOUND`, свой эмулятор убит по PID, чужой не тронут. В `finish()` до
   манифеста состояния прогона и возврата кэшей и GLCache — `guard_f20c.py wait-gone` (опрос 10 с; замок держится, пока процесс
   пользователя жив). После снятия замка `runs/<тег>` → `<тег>.user_*` (помеха, повтор тем же именем), блок закрыт. Тег, не дошедший до
   `enter_scene.py` (отказ манифеста, копии), — `runs/<тег>` → `<тег>.nostart_*` (помеха; так `f20_v11` → `f20_v11.nostart_073752`).

Вне мест 1–4 код не менялся; комментарии в шапках трёх файлов описывают места 1–4.

## 2. Проверки

- `test_guard_f20c.py` (новый набор) — **57 проверок, `ALL OK`**: члены и края `user_procs` (свой pid и время ± 15 с / 16 с, без
  pid-файла, имя в любом регистре, лаунчер рядом с эмулятором, процесс в другой папке и без пути, pid 0 / 4 / свой), маска вывода
  (ни одно входное имя и путь не в выводе), вывод в строгий cp1250 без `PYTHONIOENCODING`, `kill-own` только `/PID` своего и ничего при
  чужом времени создания или без файла, `watch` (одиночный опрос — ничего; два подряд — флаг и убийство своего по PID), `wait-gone`,
  блоки (599 / 600 с, 6 тегов, старая чистая проверка после закрытия не считается, находка между проверками), `launch_f20c.sh` в сухом
  прогоне 2 (блок закрыт — 8; открыт — 0; эмулятор пользователя — 7 и блок закрыт; сухой прогон 1 — до сторожа), `kill_game` в
  `enter_scene.py` (только `/PID`, затем `kill()`), отсутствие `/IM` во всех скриптах харнесса, порядок сторожа в `go_f20c.sh`, ASCII.
- `test_tools_f20c.py` (без изменений) на правленых файлах — **36 проверок, `ALL OK`** (37 в печати 1: проверка «`f20_v02` до
  `f20_v01`» выполняется только без каталога `runs/f20_v01`, он есть с 02:23Z).
- `f20c_read.py --check-seal` по строкам ниже — `SEAL PASS`.

## 3. Строки `seal:` всех файлов

```
seal: c34f5f2f8cf8c842bc08529a7d2fce2524507a0d974b498099f967a9701d6345 C:/kyty/f287/f20c/pred/f20c_seal.md
seal: 73e4a8fb62f7acfd812997d168cc1ee99dcdada43a1ee66e85007e171b536a2e C:/kyty/f287/f20c/f20c_read.py
seal: af1bf36fa18f98416253e75b351da6b005b004f42e41ec5f840d07ba5b0272b0 C:/kyty/f287/f20c/test_f20c_read.py
seal: b35f9854ef6dec71110509b4123d12198d44730fba85d60bf9f159b5611471d3 C:/kyty/f287/f20c/sens_f20c.py
seal: f176714b9ad99501b1aecc7b152dec6dac0fb80b0755bf5753ce89c8d9ae8d9a C:/kyty/f287/f20c/test_tools_f20c.py
seal: d920214909ddb6f70fe39e40e4e9cd599ce68f6934dbaaa9a077403817252f8f C:/kyty/f287/f20c/go_f20c.sh
seal: fb7551ee1ba7519676f431d0aad364377daf85c56cb869cb179e3da01e95448a C:/kyty/f287/f20c/launch_f20c.sh
seal: 14648c30d8d74c1f3ebaf9ef120162b556f3d8a31d83ffb5605e6cd4bf2afd75 C:/kyty/f287/f20c/wait_f20c.sh
seal: b77c93685b6796a5e79bb8323dc382efb5e78cad762985499071e20bc85c56ca C:/kyty/f287/f20c/post_f20c.sh
seal: 186e5e47b7bb69ca6d7b0ac445a9cae6bd6f2d02378b2c0517d64624c8ade026 C:/kyty/f287/f20c/queue_f20c.py
seal: 58f25518638540e8b407326acca790140f340fdd703cd934c0f751a7a2620755 C:/kyty/f287/f20c/watch_f20c.py
seal: b463c50cdb1aa901ff2a8b201e0232cceebd8f806ba64ab1ac03d5464927a4e5 C:/kyty/f287/f20c/enter_scene.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 C:/kyty/f287/f20c/procload.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 C:/kyty/f287/f20c/idle142.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 C:/kyty/f287/f20c/launch_run.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb C:/kyty/f287/f20c/manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d C:/kyty/f287/f20c/sheet142.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 C:/kyty/f287/f20c/run_safety99.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 C:/kyty/f287/f20c/gates_default.txt
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
seal: 54c7d8fcddde9a1c31b2c824f8e1d431fb9ecf63189083af0f801dfcb39ccd67 C:/kyty/f287/f20c/test_f20c_read.out.txt
seal: 303de819ace18b1b3d3ca90ca9f37a4beba98adc6aadbfc015ca909fe8350687 C:/kyty/f287/f20c/sens_f20c.out.txt
seal: 897e8fc9f875719cbf038bdb9d3e08eb2e965fc55f16b89eeb36b155c8aadaa7 C:/kyty/f287/f20c/test_tools_f20c.out.txt
seal: fc46f1a460b365a3ea745092bbc8b8391411f2170e51f9f01704c8eb71834c3a C:/kyty/f287/f20c/regress_f20c.txt
seal: 4608a12d972f776e6b9611668264c2c5bea7bf4dbd323c14c49e30d12f457bdc C:/kyty/f287/f20c/guard_f20c.py
seal: 78d93540881d27b70cc6ab92355a303c444c68e90b870c51ece3384f2e890ba2 C:/kyty/f287/f20c/test_guard_f20c.py
seal: efc19749cf128458200609c9c77e7794c62342d81881917dc8975dcd1ddb64ff C:/kyty/f287/f20c/test_guard_f20c.out.txt
```

Изменились против печати 1 (было → стало): `go_f20c.sh` 050b80ad → d9202149; `launch_f20c.sh` e1b0a652 → fb7551ee; `enter_scene.py` 9df6327b → b463c50c; `test_tools_f20c.out.txt` 5d2205d4 → 897e8fc9; `guard_f20c.py` нет → 4608a12d; `test_guard_f20c.py` нет → 78d93540; `test_guard_f20c.out.txt` нет → efc19749.
