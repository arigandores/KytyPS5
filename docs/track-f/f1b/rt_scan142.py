# F1b (Red Team): own recount on the 12 s142 logs, no code shared with F1a scripts.
# Per log: 'shader CFG build failed' total vs CsPretranslate-prefixed; B26 opcode profile; hashes;
# dispatch-path translations ('ShaderRecompiler CS phase begin') of B26 hashes; '--- Error ---'; skip reasons.
import re, glob, hashlib, os, json, collections
logs = sorted(glob.glob('C:/kyty/s142/log_*.txt'))
pat_skip = re.compile(rb'CsPretranslate: skipped hash=([0-9a-f]{16}) reason=([^\r\n]*)')
pat_cfg = re.compile(rb'unsupported decoded instruction in CFG at pc 0x([0-9a-f]{8}): .*?family=(\w+) opcode=(0x[0-9a-f]+)')
pat_disp = re.compile(rb'ShaderRecompiler CS phase begin: stage=CS hash=0x([0-9a-f]{16})')
B26 = {'SOP1 0x21', 'SOP1 0x0c', 'VOPC 0xe3'}
sets = []
for p in logs:
    data = open(p, 'rb').read()
    n_cfg = data.count(b'shader CFG build failed')
    skips = pat_skip.findall(data)
    n_cfg_pre = sum(1 for h, r in skips if b'shader CFG build failed' in r)
    prof = collections.Counter(); b26 = set(); other = collections.Counter()
    for h, r in skips:
        m = pat_cfg.search(r)
        if m:
            k = (m.group(2) + b' ' + m.group(3)).decode()
            prof[k] += 1
            if k in B26:
                b26.add((h, m.group(1), k))
        else:
            other[re.sub(rb'[0-9]+', b'X', r[r.rfind(b' ', 0, 120) + 1:][:90]).decode('latin1')] += 1
    disp = set(pat_disp.findall(data))
    b26h = set(h for h, pc, k in b26)
    sset = hashlib.sha256(b'\n'.join(sorted(h + b' ' + pc + b' ' + k.encode() for h, pc, k in b26))).hexdigest()[:16]
    sets.append(sset)
    row = dict(cfg_failed=n_cfg, cfg_failed_pre=n_cfg_pre, cfg_failed_nonpre=n_cfg - n_cfg_pre,
               b26={k: prof[k] for k in sorted(B26)}, other_cfg={k: v for k, v in prof.items() if k not in B26},
               skips=len(skips), skip_other=dict(other.most_common(5)), disp_cs=len(disp), disp_b26=len(disp & b26h),
               err=data.count(b'--- Error ---'), fatal=data.count(b'--- Fatal Error ---'), set_sha=sset)
    print(os.path.basename(p), json.dumps(row, ensure_ascii=True), flush=True)
    del data
print('distinct B26 set sha:', sorted(set(sets)))
print('ALL OK')
