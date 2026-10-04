import subprocess, sys
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('7de178f9', 'docs/ROADMAP.md', 21798, '(4) **FS5d (лид):** приёмка; строка реестра; **установка FS5**', '`variant_fixb26_fixb1b` остаётся тёплым, `_fixf10` создаёт первый запуск); откат — копия `31cbfee8`'),
    ('7de178f9', 'docs/ROADMAP.md', 21804, '(6) **Порядок отгрузок FS5 и S12 и сбор S13', '`56189185` и варианте `variant_fixb26_fixb1b`'),
    ('5d37ef09', 'docs/ROADMAP.md', 22049, '(б) **З1 (`SDL_REVISION` в `631ff987` называет `8a56dc2a`', '(в) **З2 (рецепты `pipelines.bin` лежат в каталоге варианта'),
    ('5d37ef09', 'docs/ROADMAP.md', 22050, '(в) **З2 (рецепты `pipelines.bin` лежат в каталоге варианта', '(г) **Звенья:** FS5b (`HPP-510`) — приём этой строкой'),
    ('2443ddb0', 'docs/track-f/fs5c.md', 149, '| тег | замок (`lock.log`, UTC) | вход / удержание после 1-го кадра сцены |', '|---|---|---|---|---|---|---|---|'),
    ('2eec748a', 'docs/ROADMAP.md', 22054, '(а) **Пересчёт лида [c] на KytyPS5 `4cba9eed`:**', '(б) **Чтение члена «путь `=0` байт в байт FS4 `3d0e46da`»**'),
]
ok = True
for c, p, n, a, b in REFS:
    lines = subprocess.run(['git', '-C', REPO, 'show', f'{c}:{p}'], capture_output=True).stdout.decode('utf-8').split('\n')
    la, lb = lines[n - 1], lines[n]
    r = a in la and b in lb
    ok &= r
    print('OK' if r else 'NOT OK', f'{c}:{p}:{n}')
    if not r:
        print('  L:', la[:200]); print('  +1:', lb[:200])
print(f'{sum(1 for _ in REFS)} refs')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
