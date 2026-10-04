# F21a (HPP-563; form of f20a/refs_f20a.py): references of f21a.md (general rule 24(1)): <commit>:<path>:<line> with an
# anchor and the +1 control.
#   python refs_f21a.py <refs.tsv> [<report.md>]
# writes <refs.tsv> (commit, path, line, anchor, +1 text) from SPEC after checking every row against
# 'git show <commit>:<path>' (the anchor must stand in the line, the +1 text must start the next line), then checks
# that every 'name.ext:<line>' written in the report (md, cpp, h) is a row of the table.  Prints 'refs N of N',
# 'report refs M of M', 'ALL OK'.
import re, subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
DOC = '16e0556f'
SRC = '3cc79cb2'
RL = 'src/loader/runtimeLinker.cpp'
CP = 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
SPEC = [
    (DOC, 'docs/ROADMAP.md', 22555, '462. **Звено F20b трека F (`HPP-552`, лид; приёмка F20a', '(а) **Приёмка строкой. F20a ✓**'),
    (DOC, 'docs/ROADMAP.md', 22562, '(ж) **Следующая итерация очереди F — F21 = Б9 (Q4)', '(з) **Звенья (стадия review лида у каждого звена исполнителя):**'),
    (DOC, 'docs/ROADMAP.md', 22561, '(е) **Долги F20a (п. 324(и)(5)).**', '(ж) **Следующая итерация очереди F — F21 = Б9 (Q4)'),
    (DOC, 'docs/track-f/register.md', 174, '| Б9 | K4 | наблюдение (проявления нет) |', '| Ф8 | K4 |'),
    (DOC, 'docs/track-f/register.md', 157, '| Ф3 | K4 | наблюдение по букве п. 228(б)', '| Ф7 | K4 |'),
    (DOC, 'docs/track-f/register.md', 322, '| Б26в (новая) | K4 (при запросе — K1) |', '| Б26г (новая) |'),
    (DOC, 'docs/track-f/register.md', 323, '| Б26г (новая) | K4 (при запросе — K1) |', '| Ф9 (новая) |'),
    (DOC, 'docs/track-f/register.md', 402, '| Б9а | K4 | дефект (путь исполняется [c]) | 16 неразрешённых импортов `AudioPropagation` из 22', '| Б9б (новая) |'),
    (DOC, 'docs/track-f/register.md', 691, '| Ф3 (поправка к §4, §37) | K4 |', '| Б4 (поправка к §4) |'),
    (DOC, 'docs/track-f/register.md', 830, '| Q4 | Б9 | K4 | наблюдение |', '| Q5 | Ф4 |'),
    (SRC, RL, 394, 'LOGF("Late-resolved import: %s -> %s', 'resolved.name.c_str(), resolved.vaddr);'),
    (SRC, RL, 405, 'const auto log_index = g_unresolved_stub_call_log_count.fetch_add(1);', 'if (log_index < 1024) {'),
    (SRC, RL, 410, 'LOGF("Unresolved import stub called [%u]: patch_vaddr=', '" jmprela_index='),
    (SRC, RL, 1158, 'LOGF("Relocate: unresolved PLT import patched to stub [%u]', '", %s, %s, %s, %s'),
    (SRC, CP, 116, 'LOGF("CsPretranslate: hit hash=', 'hash, job->translate_us, stats.hits);'),
    (SRC, CP, 130, 'LOGF("CsPretranslate: miss hash=', 'return std::nullopt;'),
    (SRC, PC, 4002, 'if (ComputePretranslation::Enabled() && !Config::GraphicsDebugDumpEnabled()) {', 'prepared = pretranslation.Take(params.code, params.hash, input_info,'),
]
tsv = sys.argv[1]
report = sys.argv[2] if len(sys.argv) > 2 else None
cache = {}


def lines(commit, path):
    if (commit, path) not in cache:
        o = subprocess.run([GIT, '-C', REPO, 'show', commit + ':' + path], capture_output=True)
        cache[(commit, path)] = o.stdout.decode('utf-8', 'replace').split(chr(10))
    return cache[(commit, path)]


ok = 0
names = set()
rows = []
for commit, path, line, anchor, plus1 in SPEC:
    L = lines(commit, path)
    a = L[line - 1] if line - 1 < len(L) else ''
    b = L[line] if line < len(L) else ''
    good = anchor in a and b.strip().startswith(plus1)
    ok += good
    if not good:
        print('FAIL %s:%s:%d' % (commit, path, line))
        for i, x in enumerate(L):
            if anchor in x:
                print('   anchor found at line %d; next line starts %r' % (i + 1, L[i + 1].strip()[:60] if i + 1 < len(L) else ''))
    names.add((path.rsplit('/', 1)[1], line))
    rows.append(chr(9).join([commit, path, str(line), anchor, plus1]))
with open(tsv, 'w', encoding='utf-8', newline=chr(10)) as f:
    f.write(chr(10).join(rows) + chr(10))
print('refs %d of %d' % (ok, len(SPEC)))
miss = []
cited = set()
if report:
    text = open(report, encoding='utf-8').read()
    cited = set((m.group(1), int(m.group(2))) for m in re.finditer(r'([A-Za-z0-9_]+[.](?:md|cpp|h)):(\d+)', text))
    miss = sorted(c for c in cited if c not in names)
    for c in miss:
        print('NOT IN TABLE %s:%d' % c)
    print('report refs %d of %d' % (len(cited) - len(miss), len(cited)))
good = ok == len(SPEC) and not miss
print('ALL OK' if good else 'FAILED')
sys.exit(0 if good else 1)
