"""Session 103: default-off identity of the translator change.

Every translation-cache file of the session-102 signature (snapshot C:/kyty/cache_snap/
PPSA21564_2db9065a, taken before any run of the new build) is recompiled by the NEW
shader_cfg_tests.exe (KYTY_RECOMPILE, every permutation, no switch) and compared word for word with
the SPIR-V the game stored (the test prints `recompile-identity: ... identical=`).
Expected: identical everywhere except the capped BVH program 380bb9d636390bae.

    python identity_sweep.py <out.json> [KYTY_X=v ...]   (extra env for an arm, e.g. KYTY_BDA_LEAN=1)
"""
import concurrent.futures
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

SNAP = 'C:/kyty/cache_snap/PPSA21564_2db9065a'
GCN_DIR = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/_Shaders/gcn'
EXE = 'C:/kyty/build/shader_cfg_tests.exe'
SIG = b'KytySC3:2db9065a'
TMP = tempfile.mkdtemp(prefix='idsweep_')


def env_for(extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update(extra)
    return env


def run(gcn, cache, perm, extra):
    out = os.path.join(TMP, '%s_%d.spv' % (os.path.basename(cache), perm))
    e = dict(extra)
    e['KYTY_RECOMPILE'] = '%s;%s;%s;%d' % (gcn, cache, out, perm)
    r = subprocess.run([EXE], cwd='C:/kyty/build', env=env_for(e), capture_output=True, text=True,
                       errors='replace', timeout=600)
    ident = re.search(r'recompile-identity: permutation=(\d+) words=(\d+) stored_words=(\d+) identical=(\d)',
                      r.stdout)
    perms = re.search(r'permutations=(\d+)', r.stdout)
    try:
        os.remove(out)
    except OSError:
        pass
    return {'rc': r.returncode, 'identical': int(ident.group(4)) if ident else None,
            'words': int(ident.group(2)) if ident else None,
            'stored_words': int(ident.group(3)) if ident else None,
            'perms': int(perms.group(1)) if perms else None,
            'err': (r.stderr[-300:] if r.returncode != 0 else '')}


def one(cache, extra):
    name = os.path.basename(cache)
    stage, h = name.split('_')[0], name.split('_')[1]
    gcn = '%s/%s_%s.bin' % (GCN_DIR, stage, h)
    if not os.path.exists(gcn):
        return {'file': name, 'status': 'no_gcn'}
    first = run(gcn, cache, 0, extra)
    res = {'file': name, 'hash': h, 'stage': stage, 'perm': [first]}
    n = first['perms'] or 1
    for p in range(1, n):
        res['perm'].append(run(gcn, cache, p, extra))
    ids = [x['identical'] for x in res['perm']]
    res['status'] = ('identical' if all(i == 1 for i in ids) else
                     'differs' if all(i is not None for i in ids) else 'failed')
    return res


def main():
    out_path = sys.argv[1]
    extra = dict(a.split('=', 1) for a in sys.argv[2:])
    files = []
    for path in sorted(glob.glob(SNAP + '/*.bin')):
        if not re.match(r'^(cs|ps|vs)_[0-9a-f]{16}_[0-9a-f]{16}[.]bin$', os.path.basename(path)):
            continue
        head = open(path, 'rb').read(512)
        if head.find(SIG) >= 0:
            files.append(path)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for r in pool.map(lambda c: one(c, extra), files):
            results.append(r)
    summary = {}
    for r in results:
        key = (r.get('stage', '?'), r['status'])
        summary['%s:%s' % key] = summary.get('%s:%s' % key, 0) + 1
    differs = [r['file'] for r in results if r['status'] == 'differs']
    failed = [(r['file'], [p['err'][-160:] for p in r['perm'] if p['identical'] is None])
              for r in results if r['status'] == 'failed']
    json.dump({'extra': extra, 'files': len(files), 'summary': summary, 'differs': differs,
               'failed': failed, 'results': results}, open(out_path, 'w'), indent=1)
    print('files', len(files), 'summary', json.dumps(summary, sort_keys=True))
    print('differs', differs)
    print('failed', len(failed), [f[0] for f in failed][:20])


if __name__ == '__main__':
    main()
