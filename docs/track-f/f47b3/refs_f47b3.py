# F47b3 (HPP-817, Red Team): map of the review links <commit>:<path>:<line>, form of refs_f47a3.py. check: every link's
# line contains its anchor and the next line, with leading whitespace removed, starts with its +1 control ('' = empty
# line) (git show); neg: every link with the anchor mutated and every link moved to line +1 must fail; text: every link
# written in the review is in the table and nothing else.
# Usage: python refs_f47b3.py check | neg | text <review.md>
import re, subprocess, sys

ROOT = 'C:/kyty/KytyPS5'
RM = 'docs/ROADMAP.md'
E3 = 'docs/track-f/f47a3.md'
CL = 'docs/track-f/f47a3/cls_f47a3.py'
SA = 'src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
CODE = 'ea6c6e9e'
REFS = [
    ('45dd78a2', RM, 24789, '721. **Звено F47a3 трека F (`HPP-816`, Probe Designer;', '(а) **Приёмка строкой. F47a3 ✓**'),
    ('45dd78a2', RM, 24794, '   (д) **В4 — решение лида: принята рекомендация издания.**', '(е) **Замечания'),
    ('94c221ed', 'docs/track-f/f47b2-review.md', 106, '**RC3 (таблица класса не полна: user-SGPR, зависимость по управлению',
     'если «вход выборки не участвует или умножен на 0»;'),
    ('04d5ac8a', CL, 197, 'if op in (0x30, 0x31):  # s_cselect reads SCC', "I.srcs.append(('reg', 'scc'))"),
    ('04d5ac8a', CL, 364, "elif 'OTHER' in leaves and 'IMG' not in leaves:", "cls = 'undetermined'"),
    ('04d5ac8a', E3, 93, '(а) V_g, приведённое к формату цели (UNORM8 — к ближайшему, float16 — точно), = `Shader Out`',
     '(б) своё смешение B(V_g, `Pre-Mod`, S)'),
    ('04d5ac8a', E3, 174, '3. **«Ровно одна»:** совпадения (точные или переписанные)', 'одного H) или 0 ⇒'),
    ('04d5ac8a', E3, 187, '| маска записи | сырое слово `CB_TARGET_MASK`, биты [4t + 3 : 4t] |', '| режим цвета |'),
    ('04d5ac8a', E3, 189, '| позиции квада | экспорт POS0 VS D_b:', ''),
    ('04d5ac8a', E3, 251, '| **Н-СО+** — своё декодирование и сравнение СО |', '| **Н-СО−**'),
    (CODE, SA, 13, '{0x04u, Opcode::S_ADDC_U32},        {0x05u, Opcode::S_SUBB_U32},', '{0x06u, Opcode::S_MIN_I32},'),
    (CODE, SA, 16, '{0x0au, Opcode::S_CSELECT_B32},     {0x0bu, Opcode::S_CSELECT_B64},', '{0x0eu, Opcode::S_AND_B32},'),
    (CODE, SA, 32, '{0x2fu, Opcode::S_LSHL2_ADD_U32},   {0x30u, Opcode::S_LSHL3_ADD_U32},', '{0x31u, Opcode::S_LSHL4_ADD_U32},'),
    (CODE, PC, 428, 'if (const char* salt = std::getenv("KYTY_PIPELINE_SALT"); salt != nullptr && salt[0] != 0) {',
     'uint32_t void_id = 0;'),
    (CODE, PC, 5500, 'static_params.color_mask[slot] = colors[i].export_mapping.ApplyMask(',
     'render_target_mask_slot(ctx.GetRenderTargetMask(), slot));'),
    (CODE, 'src/graphics/guest_gpu/gpu_defs.h', 122, '[[nodiscard]] constexpr uint32_t ApplyMask(uint32_t logical_mask) const {',
     'uint32_t mapped = 0;'),
    (CODE, 'src/graphics/host_gpu/renderer/pipeline/shaders.cpp', 550, 'color_blend_attachment[i].colorWriteMask =',
     'vk::ColorComponentFlags {static_params.color_mask[i]};'),
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
    if mode == 'check':
        bad = 0
        for c, p, n, a, p1 in REFS:
            good = ok_link(c, p, n, a, p1)
            bad += not good
            print('%s %s:%s:%d' % ('ok ' if good else 'BAD', c, p, n))
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
