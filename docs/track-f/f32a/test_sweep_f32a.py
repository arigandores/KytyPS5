# Fixtures for sweep_f32a.py (F32a, HPP-733). Builds a synthetic tree in a temp folder, runs list/run/agg as subprocesses
# with environment overrides, checks every member; last line ALL OK.
import os, sys, json, lzma, pickle, hashlib, tempfile, subprocess, calendar, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, 'sweep_f32a.py')
NL = chr(10)
TAB = chr(9)
ok = True


def check(name, cond):
    global ok
    print(('OK   ' if cond else 'FAIL ') + name)
    ok &= bool(cond)


tmp = tempfile.mkdtemp(prefix='f32a_fx_').replace(chr(92), '/')
root = tmp + '/kyty'
out = tmp + '/out'
os.makedirs(root + '/sA', exist_ok=True)
os.makedirs(root + '/fx_z', exist_ok=True)
NEW = calendar.timegm((2026, 10, 5, 0, 0, 0))
OLD = calendar.timegm((2026, 9, 20, 0, 0, 0))


def wr(p, text, mt):
    with open(p, 'wb') as o:
        o.write(text.encode())
    os.utime(p, (mt, mt))


a = ('Build' + NL + '  version: Fork build someone/KytyPS5 ee9632be' + NL + 'GuestOut: Level has started: hoover_beach' + NL +
     'FrameTrace: n=1 dt_us=16000 draws=10' + NL + 'Foo: failed to open 0x1234 at 77' + NL + 'Foo: failed to open 0x9999 at 12' + NL +
     'BrandNewThing: mismatch count=5' + NL + 'plain line without keys' + NL)
wr(root + '/sA/log_a.txt', a, NEW)
wr(root + '/sA/log_b.txt', 'Foo: failed to open 0x1 at 1' + NL, OLD)          # old mtime -> not listed
wr(root + '/fx_z/log_c.txt', 'BrandNewThing: mismatch count=1' + NL, NEW)   # fixture
wr(root + '/sA/log_dup.txt', a, NEW)                                          # same sha as log_a
# segmented file: many lines, segment 64 bytes
seg_text = ''.join('line %d Zap: overflow v=%d%s' % (i, i, NL) for i in range(50))
wr(root + '/sA/log_seg.txt', seg_text, NEW)
# xz with original in F0 (manifest sha in F0 agg) and xz not in F0
orig_d = ('Old: unknown thing 5' + NL).encode()
orig_e = ('Build' + NL + '  version: Fork build x/y abcdef12' + NL + 'XzOnly: invalid state 7' + NL).encode()
for nm, data in (('log_d.txt', orig_d), ('log_e.txt', orig_e)):
    with lzma.open(root + '/sA/' + nm + '.xz', 'wb') as o:
        o.write(data)
    os.utime(root + '/sA/' + nm + '.xz', (NEW, NEW))
sha_d = hashlib.sha256(orig_d).hexdigest()
sha_e = hashlib.sha256(orig_e).hexdigest()
man = tmp + '/manifest.tsv'
with open(man, 'w', encoding='utf-8', newline=NL) as o:
    o.write(TAB.join([root + '/sA/log_d.txt', str(len(orig_d)), sha_d, '10']) + NL)
    o.write(TAB.join([root + '/sA/log_e.txt', str(len(orig_e)), sha_e, '10']) + NL)
f0agg = tmp + '/agg_f0.json'
json.dump([{'path': 'C:/old/log_d.txt', 'sha256': sha_d}], open(f0agg, 'w', encoding='utf-8'))
f0sigs = tmp + '/logsigs_f0.pkl'
pickle.dump({'C:/old/log_x.txt': {b'Foo: failed to open X at X': [1, 1, b'x']}}, open(f0sigs, 'wb'))

env = dict(os.environ, F32A_OUT=out, F32A_ROOT=root, F32A_F0_SIGS=f0sigs, F32A_F0_AGG=f0agg, F32A_MANIFEST=man,
           F32A_LOCK=tmp + '/LOCK', F32A_STOP=tmp + '/STOP', F32A_SEG_BYTES='64', PYTHONIOENCODING='utf-8')


def run(*a):
    r = subprocess.run([sys.executable, S] + list(a), env=env, capture_output=True, text=True, encoding='utf-8')
    return r.returncode, r.stdout + r.stderr


rc, o1 = run('list')
check('list rc 0', rc == 0)
rows = [l.split(TAB) for l in open(out + '/loglist_f32a.tsv', encoding='utf-8').read().splitlines()]
st = {r[0].rsplit('/', 1)[-1]: r[5] for r in rows}
check('old mtime not listed', 'log_b.txt' not in st)
check('fixture marked FIXTURE', st.get('log_c.txt') == 'FIXTURE')
check('xz with F0 sha -> F0_SAME', st.get('log_d.txt.xz') == 'F0_SAME')
check('xz not in F0 -> SWEEP', st.get('log_e.txt.xz') == 'SWEEP')
check('txt -> SWEEP', st.get('log_a.txt') == 'SWEEP' and st.get('log_seg.txt') == 'SWEEP')
rc, o2 = run('run', '60', '2')
check('run complete', rc == 0 and 'SWEEP COMPLETE' in o2)
# lock gate: run exits 3 when the lock exists
open(tmp + '/LOCK', 'w').close()
rc3, _ = run('run', '60', '2')
check('lock -> exit 3', rc3 == 3)
os.remove(tmp + '/LOCK')
rc, o3 = run('agg')
check('agg rc 0', rc == 0)
recs = {r['path'].rsplit('/', 1)[-1]: r for r in json.load(open(out + '/agg_f32a.json', encoding='utf-8'))}
check('dup detected', recs['log_dup.txt']['dup_of'] is not None or recs['log_a.txt']['dup_of'] is not None)
check('build hash parsed', recs['log_a.txt']['build'] == 'ee9632be' and recs['log_e.txt.xz']['build'] == 'abcdef12')
check('levels parsed', recs['log_a.txt']['levels'] == ['hoover_beach'])
check('segmented lines = 50', recs['log_seg.txt']['lines'] == 50)
check('xz lines = 3', recs['log_e.txt.xz']['lines'] == 3)
check('xz sha = original sha', recs['log_e.txt.xz']['sha256'] == sha_e)
sig = {l.split(TAB)[8]: l.split(TAB) for l in open(out + '/sig_f32a.tsv', encoding='utf-8').read().splitlines()[1:]}
check('baseline sig marked F0', sig.get('Foo: failed to open X at X', [0, 0, ''])[2] == 'F0')
check('baseline sig lines counted once per unique log (2)', sig.get('Foo: failed to open X at X', ['0', '0'])[1] == '2')
check('new sig marked NEW', sig.get('BrandNewThing: mismatch count=X', [0, 0, ''])[2] == 'NEW')
check('fixture sig not counted (logs 1)', sig.get('BrandNewThing: mismatch count=X', ['0'])[0] == '1')
check('segmented sig counted 50 lines', sig.get('line X Zap: overflow v=X', ['0', '0'])[1] == '50')
ex = sig.get('line X Zap: overflow v=X', [''] * 10)[6]
check('segmented example line 1', ex.endswith('log_seg.txt:1'))
check('xz-only sig present', 'XzOnly: invalid state X' in sig)
check('F0_SAME xz not swept', 'Old: unknown thing X' not in sig)
new = open(out + '/new_f32a.tsv', encoding='utf-8').read().splitlines()[1:]
check('new table excludes F0 sigs', all(l.split(TAB)[2] == 'NEW' for l in new) and len(new) == 3)
ex2 = sig['BrandNewThing: mismatch count=X'][6]
check('example line number 7', ex2.endswith('log_a.txt:7'))
shutil.rmtree(tmp, ignore_errors=True)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
