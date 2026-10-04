# S11a (HPP-493): the reference map of AUDIT_S3.md - anchor on the line, control on line + 1 (general rule 24 (1)).
import subprocess, sys
REFS = [
 ('bf19abaf', 'docs/ROADMAP.md', 19367, 'единственное плечо, которое такой блоб грузит', '**Решение: `FIXED` Б33 не объявляется'),
 ('bf19abaf', 'docs/ROADMAP.md', 21479, 'Все члены чтения S10 считаются после первого кадра сцены или после строки входа', '(в) **Правило для плеч S10**'),
 ('bf19abaf', 'docs/ROADMAP.md', 21486, 'Страж при этом не слепнет [I]', '(в) **Повтор целостности**'),
 ('bf19abaf', 'docs/ROADMAP.md', 21492, 'у тегов T2 и U на установленном `540c035a` — 0', '(б) **Лист лида.**'),
 ('bf19abaf', 'docs/ROADMAP.md', 21552, '`540c035a`, ручки S = 0): засчитано 5 из 5', 'строк пропуска 31 / 1 / 1 / 6 / 9'),
 ('bf19abaf', 'docs/ROADMAP.md', 21559, 'в пяти сериях цена целиком — PREP (трансляция)', 'прототип открывается проектом'),
 ('bf19abaf', 'docs/ROADMAP.md', 21566, 'событий T2 — трансляция VS/PS (г), не CS.', '(е) **S-cat'),
 ('bf19abaf', 'docs/ROADMAP.md', 21592, '(ответ 422 на `blocked` с монитором — со слов исполнителя)', '(л) **Звенья четвёртой волны**'),
 ('7037b199', 'docs/ROADMAP.md', 19369, '**Чтение повтора — до данных:**', '(г)(1)) → `pi_r1`'),
 ('7037b199', 'docs/ROADMAP.md', 19401, '**Чтение по букве п. 229(д)(2):**', 'атрибутированный к шейдерам кадр ≥ 100 мс'),
 ('7037b199', 'docs/ROADMAP.md', 12199, '(е) **«ИСПРАВЛЕНО» трека (до кода; отгрузка):**', 'по (г)(2) каждого из 19 входимых уровней'),
 ('4fc501f4', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 5358, 'vs_id, ps_id, create_end - create_begin,', 'static_cast<uint64_t>(m_graphics_pipelines.size()), create_begin - queued_at,'),
]
ok = True
cache = {}
for c, p, n, a, b in REFS:
    if (c, p) not in cache:
        cache[(c, p)] = subprocess.run(['git', 'show', '%s:%s' % (c, p)], capture_output=True, cwd='C:/kyty/KytyPS5').stdout.decode('utf-8').split('\n')
    t = cache[(c, p)]
    r = a in t[n - 1] and b in t[n]
    ok &= r
    print('%s %s:%s:%d' % ('OK  ' if r else 'FAIL', c, p, n))
print('ALL OK' if ok else 'BROKEN')
sys.exit(0 if ok else 1)
