# S2a (HPP-312), Session Auditor. Own check of the references of ROADMAP p.235, p.238, p.241:
# <commit>:<path>:<line> must contain the anchor; the +1 control line must contain the control text
# and must NOT contain the anchor (unless stated "same anchor" by the item). No code shared with refs_s0/refs_s1/p239refs.
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
CP = 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h'
VO = 'src/graphics/presentation/videoOut.cpp'
_cache = {}


def lines(commit, path):
    k = (commit, path)
    if k not in _cache:
        r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
        if r.returncode != 0:
            _cache[k] = None
        else:
            _cache[k] = r.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')
    return _cache[k]


# (item, commit, path, line, anchor, control text on line+1 or None when the item gives none)
REFS = [
    ('235(a)', '4fc501f4', PC, 6092, 'if (recipes_match(cache.Directory() / "pipelines.bin")) return;', 'if (!recipes_match(seed / "pipelines.bin")) {'),
    ('235(a)', '4fc501f4', 'src/emulator.cpp', 209, 'SetCacheTestEnvironment("KYTY_PIPELINE_CACHE", "0");', 'if (selected == "cold") {'),
    ('235(b)', '4fc501f4', CP, 116, None, None),
    ('235(b)', '4fc501f4', CP, 130, None, None),
    ('238(a)', '4fc501f4', VO, 1191, 'if ((r.incomplete && hold_incomplete) || r.skip_ceil) {', 'if (r.skip_ceil) {'),
    ('238(a)', '4fc501f4', PC, 6008, 'known = m_program_cache->programs.contains(key);', 'm_mutex.Unlock();'),
    ('241(a)', '57729aed', 'docs/track-f/register.md', 148, '| Б1б |', '| Б2 | K3 |'),
    ('241(b)(5)', 'a2849aec', PC, 4764, 'getPipelineCacheData(m_driver_cache, &size, nullptr);', 'if (result != vk::Result::eSuccess || size == 0 ||'),
    ('241(b)(5)', 'a2849aec', PC, 4655, '// Called with m_mutex held right after a new pipeline was created.', '// without running destructors'),
    ('241(b)(5)', 'a2849aec', PC, 5362, 'MaybeWriteDriverCache();', 'm_ready_shader_pairs.insert(pair_key);'),
    ('241(b)(5)', 'a2849aec', PC, 5399, 'MaybeWriteDriverCache();', ''),
    # the lead's p.238(a) text about the SkcBad counters and S1 references used by p.241 without anchors in ROADMAP
    ('S1 RC5 (238(a) text)', '4fc501f4', VO, 1206, None, None),
    ('S1 RC5 (238(a) text)', '4fc501f4', VO, 1211, None, None),
    ('S1 RC3', '4fc501f4', PC, 4660, None, None),
    ('S1 RC3', '4fc501f4', PC, 4806, None, None),
    ('S1 RC3', '4fc501f4', PC, 5354, None, None),
    ('S1 RC6', '4fc501f4', PC, 5127, None, None),
    ('S1 RC1/RC2', '4fc501f4', 'src/emulator.cpp', 215, None, None),
    ('S1 RC12', '4fc501f4', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 639, None, None),
    ('S1 RC15', '4fc501f4', CP, 38, None, None),
]

ok = True
n_anch = 0
n_ok = 0
for item, c, p, ln, anchor, ctl in REFS:
    L = lines(c, p)
    if L is None or ln > len(L):
        print('FAIL %s %s:%s:%d - no such file/line' % (item, c, p, ln))
        ok = False
        continue
    a = L[ln - 1]
    b = L[ln] if ln < len(L) else ''
    if anchor is None:
        print('NOANCHOR %s %s:%s:%d' % (item, c, p, ln))
        print('      line: %r' % a.strip()[:150])
        print('      +1  : %r' % b.strip()[:150])
        continue
    n_anch += 1
    r_anchor = anchor in a
    if ctl == '':
        r_ctl = (b.strip() == '')
    else:
        r_ctl = (ctl in b)
    r_plus1 = (anchor not in b)          # control: the anchor does not sit on the next line
    hits = sum(1 for x in L if anchor in x)
    res = r_anchor and r_ctl and r_plus1
    n_ok += 1 if res else 0
    ok &= res
    print('%s %s %s:%s:%d anchor=%s control+1=%s anchor_not_on_+1=%s anchor_hits_in_file=%d' % (
        'OK  ' if res else 'FAIL', item, c, p, ln, r_anchor, r_ctl, r_plus1, hits))
    if not res:
        print('      line: %r' % a.strip()[:150])
        print('      +1  : %r' % b.strip()[:150])

print('anchored refs: %d of %d OK' % (n_ok, n_anch))

# "a2849aec - the last commit of src/ in main" as of the p.241 commit 20b39318
r = subprocess.run([GIT, '-C', REPO, 'log', '-1', '--format=%h %cI', '20b39318', '--', 'src/'], capture_output=True)
print('last src/ commit reachable from 20b39318:', r.stdout.decode().strip())
for a_, b_ in (('4fc501f4', 'a2849aec'),):
    r = subprocess.run([GIT, '-C', REPO, 'diff', '--stat', a_, b_, '--', PC, VO, CP, 'src/emulator.cpp'], capture_output=True)
    print('diff %s..%s on the referenced files: %r' % (a_, b_, r.stdout.decode().strip()))
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
