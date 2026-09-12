# Сессия 45, часть 2 — Json2: итераторы и числовые типы

Дата: 2026-09-12. Ветка `merge-upstream`, поверх `3fe9b23` (часть 1 — структуризатор CFG).

## Задача

После части 1 игра на карте галактики падала: 65 обращений к стабам `Json2_v1`, затем
обращение по нулевому адресу (`runtimeLinker.cpp:844`, `code=0xC0000005`) в потоке `RoomLoad_ATQT`.

## Что найдено

### 21 нереализованный импорт Json2

В логе видно 21 неразрешённый PLT-импорт `Json2_v1`. Имена восстановлены перебором по схеме NID
Sony: `nid = base64(reverse(sha1(name + salt))[:8])`, где `salt = 518D64A635DED8C1E6B039B1C3E55230`,
`/` → `-`; схема проверена на известных парах (`clock_gettime` → `lLMT9vJAck0`). Кандидаты —
Itanium-манглинг методов `sce::Json::*`.

| NID | Символ |
|---|---|
| `bcH5EnFE2xY` | `sce::Json::Array::begin() const` |
| `WXF2ihRF+B8` | `sce::Json::Array::end() const` |
| `w5+VCznos5E` | `Array::iterator::operator++()` |
| `wcgr5mte7T8` | `Array::iterator::operator*() const` |
| `5AZPp99ogrc` | `Array::iterator::operator!=(const iterator&) const` |
| `9yLjn46Ypfs` | `Array::iterator::~iterator()` |
| `9uP25i6ipno` | `Array::empty() const` |
| `xhAcaIwnrgk` | `Object::begin() const` |
| `ivMCitpSQNk` | `Object::end() const` |
| `DlWmn2ZQuWY` | `Object::iterator::operator++()` |
| `ZCd6IYoD3Bc` | `Object::iterator::operator*() const` |
| `+isUKw4zud4` | `Object::iterator::operator!=(const iterator&) const` |
| `hoINmSMlYjI` | `Object::iterator::~iterator()` |
| `0CAesfH963Q` | `String::String(const String&)` |
| `wM4LO2iK3s8` | `String::empty() const` |
| `VbFjEs--uiA` | `String::operator==(const char*) const` |
| `n6FC+l9DU70` | `Value::set(const char*)` |
| `195ad-jAsTU` | `Value::set(const Array&)` |
| `XL8+BUqjB1w` | `Value::set(const Value&)` |
| `sn4HNCtNRzY` | `Value::getUInteger() const` |
| `x4AUdbhpRB0` | `Value::Value(uint64_t)` |

ABI снят с кода игры (eboot: сегмент кода лежит со сдвигом `0x3b1f0`, строковый — `0x42df0`):
`begin`/`end` — sret (`rdi` = 8 байт под итератор на стеке гостя, `rsi` = `this`), `operator*`
массива возвращает `const Value*`, `operator*` объекта — указатель на пару, где имя-`String`
лежит по смещению 0, а значение-`Value` по 0x10. Наблюдавшаяся последовательность вызовов
(begin, end, `!=`, dtor, dtor без тела цикла) объясняется тем, что стабы возвращали 0.

### Реализация

`src/libs/libJson2.cpp`: добавлены типы `JsonObjectPair` (48 байт, значение по 0x10),
`JsonArrayIterator`/`JsonObjectIterator` (по 8 байт, со `static_assert`), итераторы массива —
указатель в `std::vector`, итераторы объекта — указатель в снимок членов объекта
(`std::map` не даёт указателей на пары). Снимок хранится отдельно на объект и перестраивается
только при изменении состава членов, поэтому `begin()` и `end()` одной итерации всегда
указывают в одно хранилище; снимок сбрасывается в `JsonObjectDestroy`, `JsonObjectClear` и при
создании нового члена в `JsonObjectLookup`. Плюс `Array::empty`, копирующий конструктор
`String`, `String::empty`, `String::operator==(const char*)`, `Value::set(const char*/Array/Value)`,
`Value::getUInteger`, `Value::Value(uint64_t)`.

### Ассерт LevelPath (следующая причина падения)

После правки итераторов прежнего обращения по нулю нет, но прогон дошёл до собственного
ассерта игры: `int 0x41` по `rva 0x121fce0`, в логе —

```
ASSERT: D:\asobi\6.0\source\app\PlayRoomB\Game\Level\LevelPath.cpp:111
Assertion failed: m_points.size() == n
```

Разбор функции (`rva 0x121f920`): игра парсит JSON вида `{"n": 1682, "pts": [x,y,z, …]}`
(лежит строкой внутри `level.lvx`, ключи `"n"` и `"pts"` — литералы в коде), читает `n`
геттером числа (перед этим сама проверяет тип 2/3 — Integer/UInteger), резервирует `n`
элементов по 64 байта, затем итерирует массив `pts` через реализованные итераторы и сверяет
число набранных точек с `n`. `n` парсится nlohmann как unsigned, а наши геттеры отдавали
указатель на ноль для «не своего» числового типа → `n = 0` при 1682 набранных точках.

Правка: `JsonValueGetInteger`/`GetUInteger`/`GetReal` конвертируют между Integer/UInteger/Real
(результат конвертации — в thread-local, так как геттеры возвращают указатель).

## Проверки

- Короткий прогон до меню: неразрешённых импортов `Json2` — **0**, вызовов стабов — 0, падений нет.
- Прогон 1 (проходил пользователь, 7 мин): стабов 0, прежнего обращения по нулю нет,
  дошло до ассерта `LevelPath.cpp:111`. Артефакты: `stdout_assert_levelpath.txt`,
  `log_assert_levelpath_tail.txt`, видео `rec_galaxy_check.mp4` (16319 кадров, индекс совпал).
- Прогон 2 после правки геттеров (проходил пользователь): **ассерта нет, guest fault нет**,
  стартовали уровни `hub_crashsite`, `underwater_aerial_garden`. Артефакты: `stdout_run2_gs.txt`,
  `log_run2_gs_tail.txt`, видео `rec_galaxy_check2.mp4`.
- Обзор видео прогона 2 (`rec_galaxy_check2.mp4`): **16626 кадров, 0 одно-кадровых кандидатов,
  декодирование без ошибок**. Штатный `s20_vidglitch.py` на такой длине падает по памяти (держит все
  кадры, ~25 ГБ), поэтому использован потоковый вариант с тем же правилом (три кадра в памяти).
  Это проверка только на одно-кадровые дефекты, не полная оценка картинки.
- `shader_cfg_tests` в этой части не перезапускались: код шейдерного тракта не менялся.

## Открыто дальше

Прогон 2 остановил эмулятор на **своей** непроверяемой конфигурации GS:

```
unsupported GS assembly: input=5 output=2 vertices=8 GE=32/32 max_output=256
 in src/graphics/shader/shader.cpp:1006
```

`input=5` — `PrimitiveType::kTriFan`, а `PrepareProgram` принимает только PointList/LineList/
TriStrip/TriList (остальные поля условия проходят). Для tri-fan неверна и модель «шага» в
`ShaderMeshInputInfo::InputPrimitiveStep`/`Translate.cpp` (примитив i — это вершины 0, i+1, i+2),
поэтому нужна отдельная ветка сборки индексов. Временный обход без правок: `KYTY_GE_DRAWS=0` —
`ShouldSkipGeShader` срабатывает до подготовки шейдера (`renderDraw.cpp:1640/1773`), то есть
EXIT не наступает, но GS-draw'ы не рисуются. В прежних логах сессий этого сообщения нет.

## Файлы

- `src/libs/libJson2.cpp` — все правки этой части.
- `C:/kyty/s45/` — артефакты: логи и stdout обоих прогонов, видео, лог упавшего прогона до правок
  (`log_crash_roomload_tail.txt`).

Бинарь установлен, SHA256 `D5FD1DF9295785C7AC2137EC3605DF9B8BD0D38D578D0B6CCC78D85C63A9CD32`.
