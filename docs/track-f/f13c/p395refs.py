import hashlib, os, re, subprocess, sys
# F13c: verify refs (anchor and +1), sha of F13b files, fill draft placeholders
S = os.path.dirname(os.path.abspath(__file__))
G = 'C:/Program Files/Git/cmd/git.exe'
R = 'C:/kyty/KytyPS5'
C13A, C13B, CH = '84c1f78c', '0ba742fb', '2f1dafec'
B11NEXT = '| Б14 | K4 | наблюдение (проявления нет) |'
REFS = [
    ('22519cde', 'docs/ROADMAP.md', 21089, '   (з) **F13 = Б41** (очередь п. 366(д); реестр', '«| Ф15 (новая) | K5 (инструмент доказательства) | дефект | запись видео `KYTY_REC`»): чёрный экран `ending_boss_after_credit` после ≈ 20 с карточки'),
    ('22519cde', 'docs/ROADMAP.md', 19872, '(в) **Звено F7d (Red Team, `todo`, стадия review лида) — враждебный отзыв вывода (2) F7b.**', '(только чтение уже снятых выходов; новый реплей RenderDoc звено F7d не запускает'),
    (C13A, 'docs/track-f/f13a.md', 98, '**Итог: оба тега сделаны с первой попытки, помех нет.**', '`766880cf54d2d80f'),
    (C13B, 'docs/track-f/f13b.md', 14, '1. Чёрный кадр даёт **сама игра константой полноэкранного затемнения**', 'сцену с цветом (0, 0, 0) с весом `1,0`'),
    (C13B, 'docs/track-f/f13b.md', 27, 'Не определено и не заявляется (§5): что на PS5 игра при входе `-lvl ending_boss_after_credit` тоже держит чёрный экран', 'почему игра держит затемнение и никуда не переходит (логика игры, [U])'),
    (C13B, 'docs/track-f/f13b.md', 143, '- Если лид сочтёт материальным остаток §4.4', 'установленном бинаре с `KYTY_DUMP_FRAME=<k чёрного кадра>`'),
    (CH, 'docs/track-f/register.md', 648, '| Б41 (поправка к §22) | K4 | наблюдение (эталона нет [U])', None),
    (CH, 'docs/track-f/register.md', 165, '| Б11 | K4 | наблюдение (проявления нет) |', B11NEXT),
    (CH, 'docs/track-f/register.md', 157, '| Ф3 | K4 | наблюдение по букве п. 228(б)', '| Ф7 | K4 | наблюдение |'),
]
ok = True; cache = {}; out = []
for c, p, n, a, b in REFS:
    if (c, p) not in cache:
        cache[(c, p)] = subprocess.run([G, '-C', R, 'show', c + ':' + p], capture_output=True).stdout.decode('utf-8').split('\n')
    L = cache[(c, p)]
    if b is None:
        good = a in L[n - 1] and L[n] == '' and L[n + 1].startswith('Дельта к строке курса: нет')
    else:
        good = a in L[n - 1] and b in L[n]
    ok &= good
    out.append(('OK  ' if good else 'FAIL') + ' %s:%s:%d' % (c, p, n))
out.append('%d refs' % len(REFS)); out.append('ALL OK' if ok else 'FAILED')
open(os.path.join(S, 'refs.out.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
# sha check of F13b files
D = 'C:/kyty/f287/f13b'
sh = open(R + '/docs/track-f/f13b/sha_f13b.txt', encoding='utf-8').read().split('\n')
tot = good = 0; bad = []
for line in sh:
    m = re.match(r'^([0-9a-f]{64})\s+\*?(.+)$', line.strip())
    if not m: continue
    tot += 1
    f = m.group(2).strip()
    cand = [f, os.path.join(D, f), os.path.join(D, 'rd', os.path.basename(f)), os.path.join(R, 'docs/track-f/f13b', os.path.basename(f))]
    hit = None
    for x in cand:
        if os.path.isfile(x):
            hit = hashlib.sha256(open(x, 'rb').read()).hexdigest(); break
    if hit == m.group(1): good += 1
    else: bad.append((f, hit is not None))
shachk = '%d из %d совпали' % (good, tot)
print('sha', shachk, bad[:5])
if not ok: sys.exit(1)
if '--fill' in sys.argv:
    N = sys.argv[sys.argv.index('--fill') + 1]
    for fn in ('p395.md', 'reg395.md'):
        t = open(os.path.join(S, fn), encoding='utf-8').read()
        t = (t.replace('{C13A}', C13A).replace('{C13B}', C13B).replace('{CHEAD}', CH).replace('{B11NEXT}', B11NEXT)
              .replace('{SHACHK}', shachk + ' [c]').replace('{REFSN}', '%d из %d' % (len(REFS), len(REFS)))
              .replace('p{N}refs.py', 'p%srefs.py' % N).replace('поправка к §2)', 'поправка к §4)').replace('| §2 |', '| §4 |'))
        if fn.startswith('reg'): t = t.replace('{N}', N)
        open(os.path.join(S, 'f_' + fn), 'w', encoding='utf-8', newline='\n').write(t)
    print('filled')
