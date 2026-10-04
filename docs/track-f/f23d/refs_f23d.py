"""F23d (HPP-588): every <commit>:<path>:<line> reference of f23d-review.md - anchor in the line, +1 in the next line
(general rule 24(1)); plus sha256 of the local SPIR-V disassembly read in section 1.1. Output: refs_f23d.txt, last line ALL OK."""
import hashlib
import subprocess

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('700208ce', 'docs/ROADMAP.md', 22782, '(ж) **Звенья (стадия review лида у каждого звена исполнителя):**', '(з) **Априор лида [I]:**'),
    ('700208ce', 'docs/ROADMAP.md', 22779, '**Правило исхода ступени 1 (решено сейчас, читает F23e):**', '(д) **Долги F23a (п. 324(и)(5)).**'),
    ('700208ce', 'docs/ROADMAP.md', 22781, '(е) **Строки реестра** — `docs/track-f/register.md` новым разделом этим коммитом',
     '(ж) **Звенья (стадия review лида у каждого звена исполнителя):**'),
    ('700208ce', 'docs/ROADMAP.md', 22781, 'остаются в 246 из 247 PS и 102 из 119 CS корпуса T1, форма драйвера A — 38 программ', None),
    ('1ab783ef', 'docs/track-f/f23c.md', 178, '| **битовая смесь** `old ^ ((new ^ old) & select(c, ~0, 0))`', '| программный Vulkan (SwiftShader / lavapipe)'),
    ('1ab783ef', 'docs/track-f/f23c.md', 177, 'у 37 из 38 программ select формы A вложены', None),
    ('1ab783ef', 'docs/track-f/f23c.md', 183, 'харнесс 3–5 ч, реплей и сверка 1–2 ч', 'исполняется в снятом кадре (присутствие ≠ исполнение)'),
    ('1ab783ef', 'docs/track-f/f23c.md', 138, 'магическому слову, длина — u64 перед выровненным на 64 Б модулем',
     'существовал на момент снимка, **не** «исполнялся в снятом кадре»'),
    ('1ab783ef', 'docs/track-f/f23c.md', 164, 'Не опознаны индексом 3–34 модуля на снимок', 'бинарь F14g с новой подписью): «не покрыта» = нет совпадения sha'),
    ('1ab783ef', 'docs/track-f/f23c.md', 46, '`normal` побайтно равен SPIR-V F23a', '(бинарь F14g; §3) — трансляция `main` = то, что исполняет эмулятор [c]'),
    ('1ab783ef', 'docs/track-f/f23c.md', 121, 'нечётных столбцах (адрес U = x − 1/W)', ''),
    ('1ab783ef', 'docs/track-f/f23c/f23c_hrun.cpp', 443, 'vkUpdateDescriptorSets(dev, 4, w, 0, nullptr);', ''),
    ('1ab783ef', 'docs/track-f/f23c/f23c_hrun.cpp', 518, 'att.loadOp      = VK_ATTACHMENT_LOAD_OP_CLEAR;', 'att.storeOp     = VK_ATTACHMENT_STORE_OP_STORE;'),
]
out = []
ok = True
cache = {}
for c, p, n, a, nxt in REFS:
    key = (c, p)
    if key not in cache:
        cache[key] = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    L = cache[key]
    line = L[n - 1] if n - 1 < len(L) else ''
    nl = L[n] if n < len(L) else ''
    g1 = a in line
    g2 = True if nxt is None else ((nl.strip() == '') if nxt == '' else (nxt in nl))
    out.append('%s %s:%s:%d anchor %s +1 %s' % ('OK ' if g1 and g2 else 'BAD', c, p, n, 'yes' if g1 else 'NO', 'n/a' if nxt is None else ('yes' if g2 else 'NO')))
    ok &= g1 and g2
spv = 'C:/kyty/f287/f23c/work/ref_predoff.spvasm'
L = open(spv, encoding='utf-8').read().split('\n')
chk = [(253, '%127 = OpLoad %bool %gl_HelperInvocation'), (256, '%130 = OpGroupNonUniformBallot %v4uint %uint_3 %129'),
       (287, '%167 = OpINotEqual %bool %166 %uint_0'), (396, '%286 = OpSelect %uint %167 %285 %196'), (416, '%306 = OpSelect %uint %167 %305 %224')]
for n, a in chk:
    g = a in L[n - 1]
    out.append('%s %s:%d %s' % ('OK ' if g else 'BAD', spv, n, a))
    ok &= g
out.append('sha256 %s %s' % (spv, hashlib.sha256(open(spv, 'rb').read()).hexdigest()))
out.append('ALL OK' if ok else 'NOT OK')
open('C:/kyty/f287/f23d/refs_f23d.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
