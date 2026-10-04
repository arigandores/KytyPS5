# S14d: reference map of the design revision - <commit>:<path>:<line>, anchor and the +1 control (general rule 24(1)).
# "gen": resolves every anchor (a prefix of the stripped line, unique or picked by index) in the pinned commit and writes
# refs_s14d.tsv; "check": verifies line, anchor prefix and +1 prefix of every row of refs_s14d.tsv against git.
import subprocess, sys, os
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
REPO = 'C:/kyty/KytyPS5'; GIT = 'C:/Program Files/Git/cmd/git.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
P = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
C = '2b1b8787'
W = 90   # prefix width of an anchor
REFS = [
    (C, P, ['[[gnu::noinline]] bool LoadFromTranslationCache(const ProgramKey& key,',
            'LOGF("ShaderFirstUse: hash=%016" PRIx64 " stage=%u words=%zu ud=%zu host_us=%" PRIu64',
            'LOGF("AvTrace: shader-cache load hash=0x%016" PRIx64 " permutations=%zu us=%" PRIu64',
            'LOGF("AvTrace: shader-spec %s hash=0x%016" PRIx64 " perm=%zu%s',
            'bool Resolve(const ShaderTranslationCache::StoredKey& key, uint32_t index,',
            'LOGF("S-pcw: KYTY_S_PCW=%d KYTY_S_PCW_FORCE_MS=%u',
            'PipelineCache::~PipelineCache() {',
            'LOGF("AsyncPipelines: mode=%d workers=%u',
            '// Workers drain the queue before they exit, so every queued pipeline is created even when the',
            'm_pending_pipelines.fetch_add(1, std::memory_order_relaxed);|0',
            'm_pending_pipelines.fetch_add(1, std::memory_order_relaxed);|2',
            'LOGF("ShaderRegister: hash=%016" PRIx64 " type=%u size=%u scratch=%u code=%016" PRIx64',
            'if (!m_program_cache->Resolve(vs_key, vs_index, vs_loaded ? &vs_entry : nullptr,',
            '// m_mutex, which is what serialises it - NOT the draw thread, since Get also runs on']),
    (C, 'src/libs/agc.cpp', ['int KYTY_SYSV_ABI AgcDriverSubmitAcb(uint32_t queue, const Packet* packet) {',
                             'LOGF("\\t acb   = 0x%016" PRIx64']),
    (C, 'src/graphics/guest_gpu/graphicsRun.cpp', ['void GuestGpu::Enqueue(Submission submission) {',
                                                   'static const bool trace_lag = Common::EnvFlagOn("KYTY_LAG_TRACE");',
                                                   'LOGF("LagTrace: queue=%u type=%u dwords=%zu lag=%llu us"']),
    (C, 'src/graphics/shader/shader.h', ['struct ShaderUserData {', 'struct ShaderSemantic {', 'struct Shader {']),
    (C, 'src/graphics/presentation/videoOut.cpp', ['r.reserve_host_ns = Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;',
                                                   'const auto lat_us = r.reserve_host_ns != 0 && cur.host_ns > r.reserve_host_ns']),
    (C, 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
     ['bool ShaderTranslationCache::ReadFileUnchecked(const std::filesystem::path& path, StoredKey& key,']),
    ('4aeb7ff6', 'docs/ROADMAP.md', ['423. **Звено S14c трека S (`HPP-504`, лид): S14a и S14b приняты',
                                     '(в) **Ответы на вопросы.** Проект §12: **(1)** принят с поправками RC3 и RC4',
                                     '(г) **Правило исхода — до данных** (дополняет условие убийства п. 229(д)(4)',
                                     '(1) **Член (0), без кода (S14d):** если логи S10',
                                     '(д) **Критерий кода фазы A — до кода** (ручка ТОЛЬКО ИЗМЕРЕНИЯ `KYTY_S_EARLY_DIAG`',
                                     '(8) Сборка — из чистого worktree от дерева последнего принятого лидом бинаря отгрузки',
                                     '(е) **Члены правки проекта S14d** (Probe Designer, без игры и кода;']),
    ('b0c8566d', 'docs/track-s/s14b-review.md', ['### RC3 — чтение A3 меряет', '### RC4 — порог фазы A меряет только модули',
                                                 '### RC5 — источник `snap1` (а)', '### RC8 — фаза A не только измеряет',
                                                 '### RC9 — положительный контроль фазы A', '### RC11 — прогрев W']),
    ('887825c7', 'docs/track-s/s14a-design.md', ['### 6.1. Фаза A — `KYTY_S_EARLY_DIAG=1` (умолчание 0): только измерение',
                                                 '## 8. Сборка плеч и снимок холода (п. 414(б))']),
]


def show(c, p):
    return subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')


mode = sys.argv[1]
T = os.path.join(HERE, 'refs_s14d.tsv')
if mode == 'gen':
    rows = []; bad = 0
    for c, p, ls in REFS:
        L = [x.strip() for x in show(c, p)]
        for a in ls:
            pick = None
            if '|' in a[-3:]:
                a, pick = a.rsplit('|', 1); pick = int(pick)
            hits = [i for i, x in enumerate(L) if x.startswith(a)]
            if not hits or (len(hits) > 1 and pick is None):
                print('NOT UNIQUE', p, a, hits); bad += 1; continue
            i = hits[pick or 0]
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
