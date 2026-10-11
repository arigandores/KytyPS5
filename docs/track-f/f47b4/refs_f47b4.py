# F47b4 (HPP-819, Red Team): map of the review links <commit>:<path>:<line>, form of refs_f47b3.py. check: every link's
# line contains its anchor and the next line, with leading whitespace removed, starts with its +1 control ('' = empty
# line) (git show); neg: every link with the anchor mutated and every link moved to line +1 must fail; text: every link
# written in the review is in the table and nothing else.
# Usage: python refs_f47b4.py check | neg | text <review.md>
import re, subprocess, sys

ROOT = 'C:/kyty/KytyPS5'
RM = 'docs/ROADMAP.md'
E4 = 'docs/track-f/f47a4.md'
CL = 'docs/track-f/f47a4/cls_f47a4.py'
RV = 'docs/track-f/f47b3-review.md'
CODE = 'ea6c6e9e'
REFS = [
    ('9ab3e10f', RM, 24807, '723. **Звено F47a4 трека F (`HPP-818`, Probe Designer;', '(а) **Приёмка строкой. F47a4 ✓**'),
    ('9ab3e10f', RM, 24809, '(б) **В5(а) — решение лида: лист `OTHER_BRS` читается как `OTHER_BR`**', '(в) **В5(б) — решение лида: форма издания 3.**'),
    ('4c9b928e', RM, 24802, '(г) **RC3 — решение лида: правка в издании 4.**', '(д) **RC4 — решение лида'),
    ('1073a385', RV, 84, '**RC1 (классификатор не моделирует чтение `SCC`', '`04d5ac8a:docs/track-f/f47a3/cls_f47a3.py:197`'),
    ('1073a385', RV, 95, '**RC2 (правило В4 нельзя применить по выводу классификатора', '`04d5ac8a:docs/track-f/f47a3/cls_f47a3.py:364`'),
    ('1073a385', RV, 105, '**RC3 (компаратор §3.2(а) не называет формат `Shader Out`', '`04d5ac8a:docs/track-f/f47a3.md:93`'),
    ('1073a385', RV, 120, '**RC4 (три правила чтения СО дают ложный исход', '(а) Н-СО+'),
    ('631f57ec', E4, 168, '**К-вид** (член положительного контроля F47e', ''),
    ('631f57ec', E4, 175, '**До ответа К-вид (и при «не определено»)** (а) читается при обоих прочтениях',
     'разряда формата цели: UNORM8 — 1/255, float16'),
    ('631f57ec', E4, 186, '- **До величины (i)** (а) даёт только «не равно» или «не определено»', 'каждой** из четырёх перестановок'),
    ('631f57ec', E4, 232, 'Перестановка `COMP_SWAP` (F; позиция — компонента экспорта R, G, B, A', '2 канала — STD `XY__`'),
    ('631f57ec', CL, 252, 'opnd((w & 0xff) + 1 if (w & 0xff) < 105 else 125),', 'opnd(((w >> 8) & 0xff) + 1 if ((w >> 8) & 0xff) < 105 else 125)]'),
    ('631f57ec', CL, 274, 'I.srcs = [opnd(s0), opnd(s0 + 1 if s0 < 105 else 125)]', 'if op in (0x05, 0x06):'),
    ('631f57ec', CL, 442, "v4 = int(cls in ('C-buf', 'T') and 'OTHER_BR' in leaves)", "b5 = classify(leaves, len(exps), brs_as_br=True)"),
    (CODE, 'src/graphics/guest_gpu/gpu_defs.h', 91, 'kSrgb  = 6,', 'kFloat = 7,'),
    (CODE, 'src/graphics/guest_gpu/gpu_format.cpp', 138, '{ChannelLayout::k8_8_8_8, BufferFormat::k8_8_8_8UNorm, kNormalizedIntegerTypes, 4,',
     'BufferFormat::k8_8_8_8Srgb, ChannelType::kSrgb},'),
    (CODE, 'src/graphics/host_gpu/renderer/image/imageInfo.h', 340, '{0x8000000022000000ull,',
     '{vk::Format::eR8G8B8A8Srgb, Prospero::BufferFormat::k8_8_8_8Srgb, 4, false}},'),
    (CODE, 'src/graphics/host_gpu/renderer/colorRenderTarget.cpp', 35, 'case vk::Format::eR8G8B8A8Srgb:', 'case vk::Format::eB8G8R8A8Unorm:'),
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
