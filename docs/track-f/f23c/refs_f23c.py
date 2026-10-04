"""F23c (HPP-587): check of the report's references to changing documents (general rule 24(1)): every <commit>:<path>:<line>
must hold the anchor on that line and the +1 control on the next line. Output: refs_f23c.txt, last line ALL OK / FAIL."""
import subprocess

GIT = 'C:/Program Files/Git/cmd/git.exe'
REFS = [
    ('700208ce', 'docs/ROADMAP.md', 22771, '493. **Звено F23b трека F (`HPP-579`, лид; приёмка F23a `HPP-578`)', '(а) **Приёмка строкой. F23a ✓**'),
    ('700208ce', 'docs/ROADMAP.md', 22779, '**Правило исхода ступени 1 (решено сейчас, читает F23e):**', '(д) **Долги F23a (п. 324(и)(5)).**'),
    ('0c806367', 'docs/track-f/f23a/b8_forms_normal.tsv', 1, 'stage\thash16\tformB\titems(perm,level,depth,new,old,B)', 'cs\t001028ba8efc6ae1\t0\t'),
    ('b6858d6d', 'src/graphics/shader/recompiler/frontend/translate/Translate.cpp', 314, 'value = ir.Select(ir.GetExec(), value, old);', '}'),
    ('b6858d6d', 'src/graphics/shader/recompiler/ir/passes/PredicationElimination.cpp', 336, 'const char* value = std::getenv("KYTY_PRED_ELIM");',
     "return value == nullptr || value[0] != '0';"),
    ('b6858d6d', 'tests/shaderCfgTests.cpp', 15148, 'if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {',
     '// Offline recompilation: KYTY_RECOMPILE="<gcn.bin>;<cache.bin>;<out.spv>[;<permutation>]"'),
    ('b6858d6d', 'docs/agent/HANDOFF.md', 5249, 'RenderDoc подтвердил: в PS `0xe197e307a5f2cb39` GCN-код `image_sample v2, v3(+v1)`',
     'следующий `image_sample v1, v6` пишет результат U в v1'),
    ('b6858d6d', 'docs/track-f/f12f.md', 210, 'Модуль `380bb9d6…` в снимках k02–k04 — один, 462 744 Б, sha256 `3e034e543b3c8d5c…`', 'sha — вход контроля А;'),
]
out = []
ok = True
for c, p, n, a, b in REFS:
    text = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8')
    lines = text.split('\n')
    l0 = lines[n - 1] if n - 1 < len(lines) else ''
    l1 = lines[n] if n < len(lines) else ''
    good = a in l0 and b in l1
    ok &= good
    out.append('%s %s:%s:%d anchor %s +1 %s' % ('OK  ' if good else 'FAIL', c, p, n, 'yes' if a in l0 else 'NO', 'yes' if b in l1 else 'NO'))
out.append('refs %d, ok %d' % (len(REFS), sum(1 for x in out if x.startswith('OK'))))
out.append('ALL OK' if ok else 'FAIL')
open('C:/kyty/f287/f23c/refs_f23c.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
