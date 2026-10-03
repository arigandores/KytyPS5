"""Track F, link F10d (HPP-452, Red Team): run_f10d.py (= run_f10c.py of 1a588fc2 with OUT/TOOL from argv) with the SDK
spirv-val calls memoized on disk, so that the set survives a halt on the lock (the script checks the lock before every SDK
call and exits 3) and resumes in the next free window without repeating the finished SDK calls.

Only calls whose argv[0] is the SDK spirv-val are memoized; the key is the argument list plus the sha256 of the module file
named by the last argument (a synthetic NEG module rewritten with other bytes gets a new key). The tool calls (sval.exe) are
never memoized. Nothing else of run_f10d.py changes: it is executed as __main__ with sys.argv = [run_f10d.py, OUT, TOOL].
Usage: python run_f10d_cached.py <out dir> <tool exe>
"""
import hashlib
import json
import os
import subprocess
import sys

D = 'C:/kyty/f287/f10d'
CACHE = D + '/sdk_cache.json'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'

cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
real_run = subprocess.run
stats = {'hit': 0, 'miss': 0}


def cached_run(args, **kw):
    if isinstance(args, list) and args and args[0] == SPIRV_VAL and args[-1] != '--version':
        key = json.dumps(args) + ' ' + hashlib.sha256(open(args[-1], 'rb').read()).hexdigest()
        if key in cache:
            stats['hit'] += 1
            c = cache[key]
            return subprocess.CompletedProcess(args, c['rc'], bytes.fromhex(c['out']), bytes.fromhex(c['err']))
        r = real_run(args, **kw)
        stats['miss'] += 1
        cache[key] = {'rc': r.returncode, 'out': (r.stdout or b'').hex(), 'err': (r.stderr or b'').hex()}
        tmp = CACHE + '.tmp'
        json.dump(cache, open(tmp, 'w'))
        os.replace(tmp, CACHE)
        return r
    return real_run(args, **kw)


subprocess.run = cached_run
sys.argv = [D + '/run_f10d.py', sys.argv[1], sys.argv[2]]
code = open(D + '/run_f10d.py', encoding='ascii').read()
try:
    exec(compile(code, D + '/run_f10d.py', 'exec'), {'__name__': '__main__'})
finally:
    sys.stderr.write('sdk cache: hit %d miss %d\n' % (stats['hit'], stats['miss']))
