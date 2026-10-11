# F47a4 (HPP-818): map of the report links <commit>:<path>:<line>, form of F47a3 refs_f47a3.py. check: every link's line
# contains its anchor and the next line, with leading whitespace removed, starts with its +1 control ('' = empty line)
# (git show); neg: every link with the anchor mutated and every link moved to line +1 must fail; text: every link
# written in the report is in the table and nothing else. --code-commit C: code links (ea6c6e9e) read at commit C
# instead (item 715(d): the worktree commit of the installed binary before the first tag of F47d).
# Usage: python refs_f47a4.py check [--code-commit C] | neg | text <report.md>
import os, re, subprocess, sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3')
    sys.exit(3)

ROOT = 'C:/kyty/KytyPS5'
RM = 'docs/ROADMAP.md'
RV = 'docs/track-f/f47b3-review.md'
E3 = 'docs/track-f/f47a3.md'
C3 = 'docs/track-f/f47a3/cls_f47a3.py'
DEC = 'src/graphics/shader/recompiler/frontend/decode/'
TR = 'src/graphics/shader/recompiler/frontend/translate/'
PM4 = 'src/graphics/guest_gpu/command_processor/pm4Handlers.cpp'
PL = 'src/graphics/host_gpu/renderer/pipeline/'
CODE = 'ea6c6e9e'
# commit, path, line, anchor (substring of the line), +1 control (prefix of the next line after lstrip; '' = empty line)
REFS = [
    ('4c9b928e', RM, 24798, '722. **Звено F47b3 трека F (`HPP-817`, Red Team;', '(а) **Приёмка строкой. F47b3 ✓**'),
    ('4c9b928e', RM, 24800, '(б) **RC1 — решение лида: правка в издании 4.**', '(в) **RC2 — решение лида: правка в издании 4.**'),
    ('4c9b928e', RM, 24801, '(в) **RC2 — решение лида: правка в издании 4.**', '(г) **RC3 — решение лида: правка в издании 4.**'),
    ('4c9b928e', RM, 24802, '(г) **RC3 — решение лида: правка в издании 4.**', '(д) **RC4 — решение лида: правка в издании 4,'),
    ('4c9b928e', RM, 24803, '(д) **RC4 — решение лида: правка в издании 4,', '(е) **Строки отзыва Н1–Н4'),
    ('4c9b928e', RM, 24805, '(ж) **Звенья.** (1) F47b3 `HPP-817`', '(з) **Не заявляется:** п. 718(з) и п. 721(з)'),
    ('4c9b928e', RM, 24806, '(з) **Не заявляется:** п. 718(з) и п. 721(з)', ''),
    ('1073a385', RV, 84, '**RC1 (классификатор не моделирует чтение `SCC`', '`04d5ac8a:docs/track-f/f47a3/cls_f47a3.py:197`'),
    ('1073a385', RV, 95, '**RC2 (правило В4 нельзя применить', '`04d5ac8a:docs/track-f/f47a3/cls_f47a3.py:364`'),
    ('1073a385', RV, 105, '**RC3 (компаратор §3.2(а) не называет', '`04d5ac8a:docs/track-f/f47a3.md:93`'),
    ('1073a385', RV, 120, '**RC4 (три правила чтения СО', '(а) Н-СО+'),
    ('04d5ac8a', E3, 68, '| 6 | **иначе** — живой вход VGPR PS', ''),
    ('04d5ac8a', E3, 93, '(а) V_g, приведённое к формату цели', '(б) своё смешение B(V_g'),
    ('04d5ac8a', E3, 102, '### 3.3 Классификатор `cls_f47a3.py`', ''),
    ('04d5ac8a', E3, 174, '3. **«Ровно одна»:**', 'одного H) или 0'),
    ('04d5ac8a', E3, 187, '| маска записи | сырое слово `CB_TARGET_MASK`', '| режим цвета |'),
    ('04d5ac8a', E3, 189, '| позиции квада | экспорт POS0 VS D_b', ''),
    ('04d5ac8a', E3, 196, '`CB_BLEND<t>_CONTROL`: `COLOR_SRCBLEND` [4:0]', '`ALPHA_DESTBLEND` [28:24]'),
    ('04d5ac8a', E3, 251, '| **Н-СО+** — своё декодирование', '| **Н-СО−**'),
    ('04d5ac8a', E3, 297, '- **В4 — «не определено» от живого входа VGPR', 'листьями `SMEM` / `BUF`'),
    ('04d5ac8a', C3, 197, 'if op in (0x30, 0x31):  # s_cselect reads SCC', "I.srcs.append(('reg', 'scc'))"),
    ('04d5ac8a', C3, 364, "elif 'OTHER' in leaves and 'IMG' not in leaves:", "cls = 'undetermined'"),
    (CODE, DEC + 'ScalarAluOps.cpp', 13, '{0x04u, Opcode::S_ADDC_U32},        {0x05u, Opcode::S_SUBB_U32},', '{0x06u, Opcode::S_MIN_I32},'),
    (CODE, DEC + 'ScalarAluOps.cpp', 16, '{0x0au, Opcode::S_CSELECT_B32},     {0x0bu, Opcode::S_CSELECT_B64},', '{0x0eu, Opcode::S_AND_B32},'),
    (CODE, DEC + 'ScalarAluOps.cpp', 32, '{0x30u, Opcode::S_LSHL3_ADD_U32},', '{0x31u, Opcode::S_LSHL4_ADD_U32},'),
    (CODE, DEC + 'ScalarAluOps.cpp', 42, '{0x06u, Opcode::S_CMOV_B64},', '{0x07u, Opcode::S_NOT_B32},'),
    (CODE, DEC + 'ScalarAluOps.cpp', 100, '{0x04u, Opcode::S_CBRANCH_SCC0},', '{0x05u, Opcode::S_CBRANCH_SCC1},'),
    (CODE, DEC + 'ShaderDecoder.cpp', 268, 'case 253u: operand.kind = OperandKind::Scc; return;', 'case 255u:'),
    (CODE, TR + 'Scalar.cpp', 17, 'case O::S_CSELECT_B32: S_CSELECT_B32(inst); return true;', 'case O::S_CSELECT_B64:'),
    (CODE, TR + 'Scalar.cpp', 19, 'case O::S_CMOV_B64: ScalarSelect64(inst, inst.dst); return true;', 'case O::S_SETREG_B32:'),
    (CODE, TR + 'Scalar.cpp', 56, 'case O::S_ADDC_U32: ADD_U32(inst, false, true); return true;', 'case O::S_SUB_U32:'),
    (CODE, TR + 'Scalar.cpp', 58, 'case O::S_SUBB_U32: SUBB_U32(inst, false, false); return true;', 'case O::S_ABSDIFF_I32:'),
    (CODE, TR + 'Control.cpp', 90, ': ConditionBit(ConditionOperand(Decoder::OperandKind::Scc));', 'const auto add0'),
    (CODE, TR + 'Control.cpp', 123, ': ConditionBit(ConditionOperand(Decoder::OperandKind::Scc));', 'const auto partial'),
    (CODE, TR + 'Control.cpp', 247, 'const auto result = ir.Select(ir.GetScc(), ReadU32(inst.src0), ReadU32(inst.src1));',
     'WriteOperand(DestinationOperand(inst), result);'),
    (CODE, TR + 'Control.cpp', 253, 'const auto condition     = ir.GetScc();', 'const auto lhs'),
    (CODE, TR + 'Translate.cpp', 756, 'case CFG::BranchCondition::SccNonZero: condition = ir.GetScc(); break;',
     'case CFG::BranchCondition::VccZero:'),
    (CODE, PM4, 573, 'static_cast<Prospero::ChannelOrder>(KYTY_PM4_GET(buffer[0], CB_COLOR0_INFO, COMP_SWAP));',
     'r.cmask_fast_clear_enable'),
    (CODE, PM4, 584, 'cp.GetCtx().SetColorInfo(param, r);', ''),
    (CODE, PL + 'pipelineCache.cpp', 5500, 'static_params.color_mask[slot] = colors[i].export_mapping.ApplyMask(',
     'render_target_mask_slot(ctx.GetRenderTargetMask(), slot));'),
    (CODE, 'src/graphics/guest_gpu/gpu_defs.h', 122, '[[nodiscard]] constexpr uint32_t ApplyMask(uint32_t logical_mask) const {',
     'uint32_t mapped = 0;'),
    (CODE, PL + 'shaders.cpp', 550, 'color_blend_attachment[i].colorWriteMask =', 'vk::ColorComponentFlags {static_params.color_mask[i]};'),
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
