# S14k: reference map of section 17 of the design - <commit>:<path>:<line>, anchor and the +1 control (general rule 24(1)).
# "gen": resolves every anchor (a prefix of the stripped line, unique or picked by index) in the pinned commit and writes
# refs_s14k.tsv; "check": verifies line, anchor prefix and +1 prefix of every row of refs_s14k.tsv against git.
import subprocess, sys, os
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
REPO = 'C:/kyty/KytyPS5'; GIT = 'C:/Program Files/Git/cmd/git.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
P = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
W = 90   # prefix width of an anchor
REFS = [
    ('fb45aea5', 'docs/ROADMAP.md', ['430. **Звено S14d трека S (`HPP-527`, Probe Designer; приёмка лида на стадии review): S14d ПРИНЯТО',
                                     '(в) **Классы (ответ на вопрос 1, первая часть) — принят новый состав:**',
                                     '(2) **S14k (Probe Designer):** скрипт `docs/track-s/s14k/c0p_s14k.py`',
                                     '(3) **Правило исхода (0′) — до данных.**',
                                     '(3) **Момент записи (вопрос 4) — принят как чтение п. 423(г):**',
                                     '(5) **Свой хэш цели (вопрос 6) — принят вариант исполнителя:**']),
    ('236cf189', 'docs/ROADMAP.md', ['439. **Звено S14j трека S (`HPP-533`, Emu Engineer; приёмка лида на стадии review): S14j ПРИНЯТО',
                                     '(в) **Ответ на вопрос — вариант исполнителя принят (чтение п. 430(г)(1)–(2), не новая константа',
                                     '(г) **Долги звена (правило п. 324(и)(5)):** (1) список 14 прежних падений']),
    ('2b1b8787', P, ['LOGF("AvTrace: shader-spec %s hash=0x%016" PRIx64 " perm=%zu%s',
                     'LOGF("ShaderRegister: hash=%016" PRIx64 " type=%u size=%u scratch=%u code=%016" PRIx64']),
    ('ff953d4f', 'tests/shaderCfgTests.cpp', ['std::fprintf(out, "SpecDump: file=%s stage=%s hash=0x%016llx perm=%zu spec=%s',
                                              'if (!ShaderTranslationCache::ReadFileUnchecked(path, key, entry)) {']),
    ('ff953d4f', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
     ['if (std::memcmp(data.data(), m_signature.data(), m_signature.size()) != 0) {|LINE652']),
    ('65bcebcc', 'docs/track-s/s14a-design.md', ['### 15.2. Серии и веса — сверка со скорером',
                                                 '### 15.3. Вариант исполнителя: более слабое необходимое условие вычислено',
                                                 'Справка (не граница): среди 22 различных compile-записей шести логов',
                                                 '3. *Предсказание* — запись r\\* с наибольшим m(r) < t_reg(T)']),
]


def show(c, p):
    return subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')


mode = sys.argv[1]
T = os.path.join(HERE, 'refs_s14k.tsv')
if mode == 'gen':
    rows = []; bad = 0
    for c, p, ls in REFS:
        L = [x.strip() for x in show(c, p)]
        for a in ls:
            want = None
            if '|LINE' in a:
                a, want = a.rsplit('|LINE', 1); want = int(want)
            hits = [i for i, x in enumerate(L) if x.startswith(a)]
            if want is not None: hits = [i for i in hits if i + 1 == want]
            if len(hits) != 1:
                print('NOT UNIQUE', p, a, hits); bad += 1; continue
            i = hits[0]
            rows.append('%s\t%s\t%d\t%s\t%s' % (c, p, i + 1, L[i][:W], L[i + 1][:W]))
    open(T, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    for r in rows:
        f = r.split('\t'); print(f[0], f[1].split('/')[-1], f[2], '|', f[3][:60], '|+1|', f[4][:50])
    print('rows', len(rows), 'bad', bad)
    sys.exit(1 if bad else 0)
else:
    ok = True; n = 0
    for r in open(T, encoding='utf-8').read().split('\n'):
        if not r: continue
        c, p, ln, a, b = r.split('\t'); L = show(c, p); ln = int(ln); n += 1
        good = L[ln - 1].strip().startswith(a) and L[ln].strip().startswith(b)
        ok &= good
        if not good: print('FAIL', c, p, ln)
    print('refs', n, 'ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
