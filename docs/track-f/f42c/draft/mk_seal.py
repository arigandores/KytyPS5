"""Make pred/f42c_seal.md from draft/f42c_seal.md: FS13-or-FS14 installed (item 710(g)(4)), section 8 numbers, section 9 header.
UTF-8, LF.  usage: python draft/mk_seal.py"""
import sys

G = 'C:/kyty/f287/f42c/'
NL = chr(10)
t = open(G + 'draft/f42c_seal.md', 'rb').read().decode('utf-8')


def rep(old, new):
    global t
    if t.count(old) != 1:
        print('ANCHOR FAIL', repr(old[:90]), t.count(old))
        sys.exit(1)
    t = t.replace(old, new)


rep("""- **Установленный — FS13** `abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73` (п. 703–704), закреплённая копия
  `C:/kyty/f287/bin/kyty_emulator_abab2196.exe`; до вызова (вне и внутри замка) = после возврата из закреплённой копии (член допуска).""",
    """- **Установленный — FS13 или FS14** (вариант исполнителя по п. 710(г)(4): FS14d ставит FS14 «при отсутствии идущей серии под замком» —
  между тегами этой серии тоже): FS13 `abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73` (п. 703–704, копия
  `C:/kyty/f287/bin/kyty_emulator_abab2196.exe`) или FS14 `013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd` (п. 717, 720,
  копия `C:/kyty/f287/bin/kyty_emulator_013e1974.exe`). `go_f42c.sh` до замка определяет установленный по полному sha256 (иной — отказ, не
  попытка, вопрос лиду), сверяет закреплённую копию того же и после тега возвращает его из неё; член допуска — установленный до = после
  (один из двух). На 16:52:10Z установлен FS14 `013e1974` [c sha] — FS14d `HPP-815` поставил его после конца серии FS14c.""")
rep("""установленный во время тега = `1994a0ce`; установленный до = после = FS13 `abab2196`;""",
    """установленный во время тега = `1994a0ce`; установленный до = после, FS13 `abab2196` или FS14 `013e1974` (§1);""")
rep("""установленный FS13 `abab2196` не меняется.""",
    """установленный бинарь (FS13 или FS14 — тот, что стоял до тега) серией не меняется.""")
rep("""- **Очередь замка:** п. 322(г) (P > F > S); внутри F — после F38c и F40c (оба `done`) и после конца серии F46c `HPP-800` (п. 719(д)) —""",
    """- **Очередь замка:** п. 322(г) (P > F > S); внутри F — после F38c и F40c (оба `done`), после конца серии F46c `HPP-800` (п. 719(д);
  `lock released` 16:00:50Z) и серии FS14c `HPP-814`, взявшей замок первой по п. 714(б)(2) (`lock released` `fs14_z` 16:43:11Z) —""")

S8 = """- **Наборы (зачётные прогоны на установленных файлах `C:/kyty/f287/f42c/`, 2026-10-11 16:50–16:52Z, после правки FS13/FS14):**
  - `test_f42c_read.out.txt` (sha256 `f0683d8c28585bcc2f362770b80276d95d781d61a19a6e96b79b037492db4ab4`) — первая строка
    `suite test_f42c_read.py sha256 0538dc533130ba5c9ab340164b8d1f3b80a50e90ab3b04eddb551c8057a47176 target f42c_read.py sha256
    cd05eb4776c2a5d85c99500a267337f105ddc8557065295c0d5729c2ca739560`, `checks 357 failed 0`, `ALL OK` (каждый член допуска у трёх тегов,
    включая установленный FS14 до = после — допуск, FS13 → FS14 и FS14 → FS13 — `NOT_ADMITTED`; каждый член буквы и группы формы; Н1; строки).
  - `test_tools_f42c.out.txt` (sha256 `90403a6674ec91fc1b33052745f02370499ee79b278be745f7467e560f3675d6`) — первая строка
    `suite test_tools_f42c.py sha256 81c01e43c72935e13c5d2b820efe21dc01ebd1fd2ab16e327245a422039bacf7 target go_f42c.sh sha256
    b9e3826b4f96644e1783bfdd123033b762425e93cb49f4a58546f8928fe1963c`, `checks 149 failed 0`, `ALL OK` (сухие планы, отказы, порядок
    серии, линтер первой строкой, литералы и sha копий F42a2, FS13, FS14 на диске, `case` установленного до замка, сторож после замка до
    манифеста, возврат до `installed_after`, ASCII, cp1250).
  - `regress_f42c.out.txt` (sha256 `8fba00d257de69923abfb00d748230829d9d48a922b909f08ed3e2e9601502fc`) — `fs13_v` → `f20_v` и `fs13_w` →
    `f20_w`: допуск падает ровно на 5 членов (бинарь json, установленный на теге, установленный до/после — FS12 `46892c20`, нет
    `KYTY_FIX_F20`, член серии), члены — все ДА, кроме `FixF20`/`FixF20Stat`/Н1 (строк до F42a нет — члены живы); `fs4_hb` → `f20_hb`: вход
    345794, первый кадр сцены n 211, удержание 335,9 с, кадров ≥ 1 с 0 = ридеру FS4c; `ALL OK`.
  - `refs_f42c.out.txt` (sha256 `b4be8a5f4e112e11f3a860a1b1a275e0c62b363302c1b01f30099990d90d90f0`) — 17 ссылок `OK`, 17 сдвигов `NOT OK`,
    `ALL OK`.
- **Манифест базы** (без замка, только чтение, 16:52:07–16:52:10Z): `base/base.txt` — `manifest base/base.tsv files 4830 bytes 1300774961
  listsha 0e42960642ae9a910bd92c83ed600fd2c17c359a73c0a176ef8ab00a7259ab17`; размеры: `_ShaderCache` 689 683 755, `_ShaderSeeds`
  133 960 046, `_PipelineCache` 192 243 915, GLCache 284 887 245 байт.
- **Бинари на диске** [c sha256 16:52Z]: копия F42a2 `1994a0ce…3f29`; закреплённые FS13 `abab2196…4b73`, FS14 `013e1974…d0cd`;
  установленный — FS14 `013e1974…d0cd`.
- **Правка до печати (16:49Z, строка `C:/kyty/f287/times.txt`):** `go_f42c.sh`, `f42c_read.py`, `test_f42c_read.py`, `test_tools_f42c.py` —
  установленный до вызова FS13 или FS14 (§1); прежние файлы — `old/pre_fs14/`; скрипты правки — `draft/patch_fs14.py`, `draft/patch_fs14b.py`.
- **Линтер формы п. 634 / 661** — `C:/kyty/KytyPS5/ps5 em/docs/form634_check.py` (sha256 — `SHA256SUMS_seal.txt`); он же — первая
  исполняемая строка `launch_f42c.sh` и `go_f42c.sh`:

```
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f42c
ALL OK
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --text C:/kyty/f287/f42c/pred/f42c_seal.md
ALL OK
```

- Полные sha256 файлов харнесса и печати — `C:/kyty/f287/f42c/SHA256SUMS_seal.txt` (пишется сразу после печати).

## 9. Отчёт тегов

(заполняется после тегов в `docs/track-f/f42c.md`; печать выше не меняется)
"""
rep('<FILL8>' + NL, S8)
open(G + 'pred/f42c_seal.md', 'wb').write(t.encode('utf-8'))
print('seal written', len(t))
