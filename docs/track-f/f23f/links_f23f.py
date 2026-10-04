"""F23f (HPP-592): check of the report's references to changing documents (general rule 24(1)): every <commit>:<path>:<line>
must hold the anchor on that line and the +1 control on the next line (copy of F23c refs_f23c.py; the name refs_f23f.py is the
SPIR-V rewriter of this link). Output: links_f23f.txt, last line ALL OK / FAIL."""
import subprocess

GIT = 'C:/Program Files/Git/cmd/git.exe'
REFS = [
    ('7030111b', 'docs/ROADMAP.md', 22809, '498. **Звено F23e трека F (`HPP-589`, лид; приёмка F23c `HPP-587` с отзывом F23d `HPP-588`)',
     '(а) **Приёмка строкой. F23c ✓**'),
    ('7030111b', 'docs/ROADMAP.md', 22812, '(в) **RC1–RC5 F23d приняты как члены ступени 2', '(г) **Ступень 2 — F23f**'),
    ('7030111b', 'docs/ROADMAP.md', 22814, '(д) **Правило исхода ступени 2 (решено сейчас, читает F23h).**',
     '(е) **Парковка и условие переоткрытия (RC5).**'),
    ('07c46693', 'docs/track-f/f23d-review.md', 74, '**RC1. Опора «битовая смесь» с одним контролем', 'Что не так: F23c предлагает у каждой программы'),
    ('07c46693', 'docs/track-f/f23d-review.md', 89, '**RC2. Нет нулевого контроля на событии ступени 2', '(`1ab783ef:docs/track-f/f23c.md:183`'),
    ('07c46693', 'docs/track-f/f23d-review.md', 98, '**RC3. «Покрыта» в описи ≠ годна для сверки', 'по совпадению sha модуля с любым файлом кэша'),
    ('07c46693', 'docs/track-f/f23d-review.md', 115, '**RC4. Место select формы A может быть не задействовано', 'формы A на вложенном уровне (F23c §4'),
    ('4d9e8ab7', 'src/graphics/shader/recompiler/frontend/translate/Translate.cpp', 314, 'value = ir.Select(ir.GetExec(), value, old);', '}'),
    ('4d9e8ab7', 'src/graphics/shader/recompiler/ShaderRecompiler.cpp', 752, 'auto spirv = Spirv::EmitProgram(ir, options.input_info);',
     'LOGF("%s phase end: stage=%s hash=0x%016" PRIx64 " SPIR-V EmitProgram words=%" PRIu64'),
    ('4d9e8ab7', 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp', 767, 'uint32_t ValueEmitContext::Result(const IR::Inst& inst) {',
     'if (const auto found = definitions.find(&inst); found != definitions.end()) {'),
    ('4d9e8ab7', 'tests/shaderCfgTests.cpp', 14208, 'if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {',
     '// Offline recompilation: KYTY_RECOMPILE="<gcn.bin>;<cache.bin>;<out.spv>[;<permutation>]"'),
    ('1ab783ef', 'docs/track-f/f23c.md', 178, '| **битовая смесь** `old ^ ((new ^ old) & select(c, ~0, 0))`', '| программный Vulkan (SwiftShader / lavapipe)'),
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
open('C:/kyty/f287/f23f/links_f23f.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
