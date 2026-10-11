# F47a3 (HPP-816): map of the report links <commit>:<path>:<line>, form of F47a2 refs_f47a2.py. check: every link's line
# contains its anchor and the next line, with leading whitespace removed, starts with its +1 control ('' = empty line)
# (git show); neg: every link with the anchor mutated and every link moved to line +1 must fail; text: every link
# written in the report is in the table and nothing else. --code-commit C: code links (ea6c6e9e) read at commit C
# instead (item 715(d): the worktree commit of the installed binary before the first tag of F47d).
# Usage: python refs_f47a3.py check [--code-commit C] | neg | text <report.md>
import re, subprocess, sys

ROOT = 'C:/kyty/KytyPS5'
RM = 'docs/ROADMAP.md'
E2 = 'docs/track-f/f47a2.md'
PL = 'src/graphics/host_gpu/renderer/pipeline/'
STC = PL + 'shaderTranslationCache.cpp'
PM4 = 'src/graphics/guest_gpu/command_processor/pm4Handlers.cpp'
CODE = 'ea6c6e9e'
# commit, path, line, anchor (substring of the line), +1 control (prefix of the next line after lstrip; '' = empty line)
REFS = [
    ('6a2fed23', RM, 24764, '718. **Звено F47b2 трека F (`HPP-808`, Red Team;', '(а) **Приёмка строкой. F47b2 ✓**'),
    ('6a2fed23', RM, 24766, '   (б) **RC1 — решение лида.**', '(в) **RC2 — принято (1)–(4).**'),
    ('6a2fed23', RM, 24767, '   (в) **RC2 — принято (1)–(4).**', '(г) **RC3 — принято (1)–(5).**'),
    ('6a2fed23', RM, 24768, '   (г) **RC3 — принято (1)–(5).**', '(д) **RC4 — принято.**'),
    ('6a2fed23', RM, 24769, '   (д) **RC4 — принято.**', '(е) **RC5 — принято.**'),
    ('6a2fed23', RM, 24770, '   (е) **RC5 — принято.**', '(ж) **Звенья.**'),
    ('6a2fed23', RM, 24771, '   (ж) **Звенья.** F47b2 `HPP-808`', '(з) **Не заявляется:**'),
    ('6a2fed23', RM, 24772, '   (з) **Не заявляется:** что блоки Б34', ''),
    ('e63d6339', E2, 71, '| 1 | цвет точки на выходе D_b — литерал программы D_b (вход выборки не участвует или умножен на 0)',
     '| 2 | цвет — из буфера констант / вершинного цвета'),
    ('e63d6339', E2, 87, 'Ч2 — событие заливки цели (clear)', 'гостя; читается по форме (б)(2) как C-buf'),
    ('e63d6339', E2, 93, '1. **Программа D_b:** модуль PS события D_b в снимке', '`ps_<H>_<ключ>.bin` каталога варианта'),
    ('e63d6339', E2, 100, '3. **Значение в снимке:** цвет, который D_b записал в точке', 'питающая выход, — V_c (справка).'),
    ('e63d6339', E2, 102, '4. **«Равно»:** V_g, приведённое к формату цели D_b', 'цвета зависит только от литералов'),
    ('e63d6339', E2, 129, '«Не равно» (⇒ `дефект` по (в)(4)) — **только**:', 'своим разбором; для C-imm'),
    (CODE, PL + 'shaderTranslationCache.h', 22, 'struct Permutation {', 'ShaderRecompiler::IR::ResourceSpecialization specialization;'),
    (CODE, PL + 'shaderTranslationCache.h', 30, 'std::vector<Permutation>           permutations;', '};'),
    (CODE, STC, 621, 'std::snprintf(name, sizeof(name), "%s_%016llx_%016llx.bin",', 'key.stage == static_cast<uint32_t>(ShaderType::Vertex)'),
    (CODE, STC, 772, 'w.U32(key.user_data_count);', 'w.U32(key.code_size);'),
    (CODE, STC, 779, 'w.U32(static_cast<uint32_t>(permutations.size()));', 'for (const auto& p: permutations) {'),
    (CODE, STC, 783, 'w.PodVec(p.spirv);', '}'),
    (CODE, STC, 802, 'file.Write(&payload_hash, sizeof(payload_hash), &w2);', 'file.Write(payload.data(),'),
    (CODE, PL + 'shaders.cpp', 337, 'static vk::ShaderModule CreateDualSourceVariant(', 'uint64_t ps_hash, uint32_t color_count) {'),
    (CODE, PL + 'shaders.cpp', 357, 'LOGF("DualSrcBlend: patched ps=%016" PRIx64 "\\n", ps_hash);', '}'),
    (CODE, PL + 'shaders.cpp', 583, 'dual_src_module = CreateDualSourceVariant(graphics, pixel_program,',
     'ps_input_info->stage.program->shader_hash,'),
    (CODE, PL + 'dualSrcBlend.h', 46, 'inline Outcome RewriteLocation1ToIndex1(', 'constexpr uint32_t kMagic             = 0x07230203u;'),
    (CODE, PM4, 98, 'static HW::BlendControl DecodeBlendControl(uint32_t value) {', 'HW::BlendControl r {};'),
    (CODE, PM4, 108, 'r.enable               = KYTY_PM4_GET(value, CB_BLEND0_CONTROL, ENABLE) != 0;', ''),
    (CODE, PM4, 138, 'r.op   = KYTY_PM4_GET(value, CB_COLOR_CONTROL, ROP3);', 'return r;'),
    (CODE, PM4, 539, 'cp.GetCtx().SetBlendControl(param, DecodeBlendControl(buffer[0]));', ''),
    (CODE, PM4, 557, 'cp.GetCtx().SetColorControl(DecodeColorControl(buffer[0]));', ''),
    (CODE, PM4, 860, 'cp.GetCtx().SetRenderTargetMask(*buffer);', ''),
    (CODE, PM4, 2899, 'clear_word0.word0 = value;', 'uint32_t slot     = (cmd_offset - Pm4::CB_COLOR0_CLEAR_WORD0) / 15;'),
    (CODE, PM4, 2909, 'clear_word1.word1 = value;', 'uint32_t slot     = (cmd_offset - Pm4::CB_COLOR0_CLEAR_WORD1) / 15;'),
    (CODE, PM4, 3279, 'cp.GetCtx().SetRenderTargetMask(value);', '};'),
    (CODE, PM4, 3362, 'cp.GetCtx().SetBlendControl(param, DecodeBlendControl(value));', '};'),
    (CODE, PM4, 3615, 'cp.GetCtx().SetColorControl(DecodeColorControl(value));', '};'),
    (CODE, 'src/graphics/guest_gpu/hardwareContext.h', 418, 'struct BlendControl {', 'uint8_t color_srcblend       = 1;'),
    (CODE, 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 114, 'DecodePackedColorClear(format, metadata.dcc_clear_word, clear);', '}'),
]
cache = {}


def lines(commit, path):
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
        cache[key] = out.decode('utf-8').split('\n')
    return cache[key]


def ok_link(commit, path, line, anchor, plus1):
    L = lines(commit, path)
    if line < 1 or line > len(L) - 1:
        return False
    nxt = L[line].lstrip()
    return anchor in L[line - 1] and (nxt.startswith(plus1) if plus1 else nxt.strip() == '')


def main():
    mode = sys.argv[1]
    sub = sys.argv[sys.argv.index('--code-commit') + 1] if '--code-commit' in sys.argv else None
    if mode == 'check':
        bad = 0
        for c, p, n, a, p1 in REFS:
            cc = sub if (sub and c == CODE) else c
            good = ok_link(cc, p, n, a, p1)
            bad += not good
            print('%s %s:%s:%d' % ('ok ' if good else 'BAD', cc, p, n))
        print('links %d bad %d' % (len(REFS), bad))
        print('ALL OK' if bad == 0 else 'FAIL')
        return 0 if bad == 0 else 1
    if mode == 'neg':
        caught = 0
        for c, p, n, a, p1 in REFS:
            caught += (not ok_link(c, p, n, a + ' MUTANT', p1)) and (not ok_link(c, p, n + 1, a, p1))
        print('neg %d of %d caught (anchor mutant and line +1)' % (caught, len(REFS)))
        print('ALL OK' if caught == len(REFS) else 'FAIL')
        return 0 if caught == len(REFS) else 1
    if mode == 'text':
        text = open(sys.argv[2], encoding='utf-8').read()
        found = set(re.findall(r'`([0-9a-f]{8}):([^`:]+):(\d+)`', text))
        table = {(c, p, str(n)) for c, p, n, _, _ in REFS}
        extra, missing = found - table, table - found
        print('text links %d table %d extra %s missing %s' % (len(found), len(table), sorted(extra), sorted(missing)))
        print('ALL OK' if not extra and not missing else 'FAIL')
        return 0 if not extra and not missing else 1
    return 2


sys.exit(main())
