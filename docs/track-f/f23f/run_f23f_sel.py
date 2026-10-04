"""F23f (HPP-592, ROADMAP s122 item 498(g)(2)(b)-(v)): offline translation of the 17 covered form-A programs with the
worktree diagnostic binary (4d9e8ab7 = source of the installed S12 + F23a census + F23f id hook) - KYTY_RECOMPILE of
(guest code = eboot .shader_text of F23a, cache file = the INSTALLED S12 file of the same (stage, hash, state), perm 0):
  plain - without KYTY_F23A_SELDIAG: out.spv must equal the SPIR-V stored in the S12 file byte for byte (RC3(b));
  diag  - with KYTY_F23A_SELDIAG: out.spv must equal plain (no interference) and gives the census line (form A, ids).
Resumable (a job with both results is skipped); meant to run under watch_f23f.py. Output: sel_f23f.jsonl (census lines),
sel_f23f.status.jsonl (per job: rc, sha of both, equal to S12)."""
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import sys
import threading

D = 'C:/kyty/f287/f23f/'
BIN = D + 'build/shader_cfg_tests.exe'
S12DIR = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10'
GCN = 'C:/kyty/f287/f23a/eboot_text/'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
NL = chr(10)


def halt():
    if os.path.exists(LOCK):
        print('LOCK - exit 3', flush=True); os._exit(3)
    if os.path.exists(STOP):
        print('STOP - exit 4', flush=True); os._exit(4)


def env_with(extra):
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('KYTY_'):
            del env[k]
    env.update(extra)
    return env


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def main():
    halt()
    m = json.load(open(D + 'map_f23f.json'))
    jobs = []
    for h, v in sorted(m.items()):
        for k, s in v['s12'].items():
            state, perm = k.split('|')
            jobs.append(dict(hash=h, stage=v['stage'], state=state, perm=int(perm), s12sha=s['sha'],
                             cache='%s/%s_%s_%s.bin' % (S12DIR, v['stage'], h, state), gcn=GCN + h + '.bin'))
    status = D + 'sel_f23f.status.jsonl'
    done = set()
    if os.path.exists(status):
        for line in open(status, encoding='utf-8'):
            done.add(json.loads(line)['id'])
    lock = threading.Lock()
    todo = [j for j in jobs if '%s|%s|%d' % (j['hash'], j['state'], j['perm']) not in done]
    print('jobs', len(jobs), 'todo', len(todo), flush=True)

    def work(j):
        halt()
        jid = '%s|%s|%d' % (j['hash'], j['state'], j['perm'])
        wd = D + 'work/sel/%s_%s_%d' % (j['hash'], j['state'], j['perm'])
        os.makedirs(wd, exist_ok=True)
        res = dict(id=jid, stage=j['stage'], s12sha=j['s12sha'])
        for arm in ('plain', 'diag'):
            spv = wd + '/%s.spv' % arm
            if os.path.exists(spv):
                os.remove(spv)
            e = {'KYTY_RECOMPILE': '%s;%s;%s;%d' % (j['gcn'], j['cache'], spv, j['perm'])}
            selp = wd + '/sel.json'
            if arm == 'diag':
                for q in (selp, selp + '.post'):
                    if os.path.exists(q):
                        os.remove(q)
                e['KYTY_F23A_SELDIAG'] = selp
            try:
                r = subprocess.run([BIN], cwd=wd, env=env_with(e), capture_output=True, timeout=900)
                rc = r.returncode
                err = (r.stderr + r.stdout).replace(b'\r', b'').decode('latin1')
            except subprocess.TimeoutExpired:
                rc, err = 'timeout', ''
            res[arm + '_rc'] = rc
            res[arm + '_sha'] = sha(spv)
            res[arm + '_err1'] = [x for x in err.split(NL) if x.strip()][:3]
        res['plain_eq_s12'] = res['plain_sha'] == j['s12sha']
        res['diag_eq_plain'] = res['diag_sha'] is not None and res['diag_sha'] == res['plain_sha']
        line = open(wd + '/sel.json', encoding='utf-8').read() if os.path.exists(wd + '/sel.json') else ''
        post = open(wd + '/sel.json.post', encoding='utf-8').read() if os.path.exists(wd + '/sel.json.post') else ''
        with lock:
            if line:
                with open(D + 'sel_f23f.jsonl', 'a', encoding='utf-8', newline=NL) as f:
                    f.write(line if line.endswith(NL) else line + NL)
            if post:
                with open(D + 'sel_f23f_post.jsonl', 'a', encoding='utf-8', newline=NL) as f:
                    f.write(post if post.endswith(NL) else post + NL)
            with open(status, 'a', encoding='utf-8', newline=NL) as f:
                f.write(json.dumps(res, sort_keys=True) + NL)
        print(jid, res['plain_rc'], res['diag_rc'], 'eqS12', res['plain_eq_s12'], 'diag=plain', res['diag_eq_plain'], flush=True)
        return res

    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(work, todo))
    return 0


if __name__ == '__main__':
    sys.exit(main())
