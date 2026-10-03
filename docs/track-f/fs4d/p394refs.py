import subprocess, sys
# FS4d (HPP-473): references of ROADMAP item 394 - anchor and +1 control (general rule 24(1))
G = 'C:/Program Files/Git/cmd/git.exe'
R = 'C:/kyty/KytyPS5'
REFS = [
    ('2ab14596', 'docs/ROADMAP.md', 20620, '(4) **FS4d (лид):** приёмка; строка реестра; **установка FS4**', '`KYTY_FIX_SVAL=0`); ответ пользователю в `HPP-287`.'),
    ('2ab14596', 'docs/ROADMAP.md', 20622, '(5) **Порядок установки с треком P.** Бинарь FS4 обязан содержать', 'до FS4d установлен другой бинарь (итерация Д1-3 трека P, P44 `HPP-465`)'),
    ('2ab14596', 'docs/ROADMAP.md', 20650, '(в) **Смена установленного бинаря до S10.**', 'другой бинарь (FS4d `HPP-473` или любой другой), S10 не начинается'),
    ('2ab14596', 'docs/ROADMAP.md', 20653, 'FS4d ждёт строки «серия окончена» S10, если она уже начата', 'безопасен, но серия на двух установленных бинарях сравнивала бы разные пути'),
    ('2ab14596', 'docs/ROADMAP.md', 20746, '(б) **З1 (строка `SDL_REVISION` `31cbfee8` называет `92d11340`)**', '`KYTY_GIT_REVISION`, строка SDL не читается как происхождение'),
    ('2ab14596', 'docs/ROADMAP.md', 20749, '(в) **З2 (откат возвращает отказ Ф16 только на новой трансляции)**', 'холодном каталоге варианта; если `fs4_r0` идёт после'),
    ('2ab14596', 'docs/ROADMAP.md', 20907, '(2) Ручка удержания (`KYTY_PVAR_HOLD`, код P40 `c9b4268e` — предок `main`)', 'не описывается; без `KYTY_GAME_PATCH` она не действует (п. 342)'),
    ('2ab14596', 'docs/ROADMAP.md', 21056, '`-lvl` на **установленном** `540c035a` без правки (кэш не меняется)', '(F12g, офлайн): найти диспатчи `380bb9d636390bae` в снимке'),
    ('2ab14596', 'docs/ROADMAP.md', 21092, 'Engineer, `blocked` на FS4c `HPP-472` — один исполнитель и замок) — под замком на', 'до первого тега; `f13_rd` — снимок RenderDoc `ending_boss_after_credit`'),
    ('2ab14596', 'docs/track-f/fs4c.md', 126, '| тег (замок, UTC) | член | значение | строка ридера |', '|---|---|---|---|'),
]
ok = True
cache = {}
for c, p, n, a, b in REFS:
    k = (c, p)
    if k not in cache:
        cache[k] = subprocess.run([G, '-C', R, 'show', c + ':' + p], capture_output=True).stdout.decode('utf-8').split('\n')
    L = cache[k]
    good = a in L[n - 1] and b in L[n]
    ok &= good
    print(('OK  ' if good else 'FAIL') + ' %s:%s:%d' % (c, p, n))
print('%d refs' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
