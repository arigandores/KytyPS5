"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)(ii)-(iii)): supplement to the T1 corpus for the themes whose instruction no
T1 program carries (T234 - 0 of 222 T1 programs, T306 - 0 of 222; corpus/predict.tsv). Rows: game programs found by
scan_game.py and confirmed by the translator's own decoder (KYTY_M_DECODE), with a translation cache file of the game
(copied with sha256 into x/cache/) and the GCN code extracted from the ELF .text (x/gcn/, truncated to the key code size
when the recompile reports a different size). Configs as corpus_m2a.py (base, u, z, t<T>, all). Writes x/corpus_x.tsv,
prints per row the configs whose SPIR-V differs from base, and per theme: changed rows must carry the theme's instruction.
Usage: python corpus_x.py <base exe> <dev exe>. Lock and STOP before every process."""
import hashlib
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_named import elf_programs, GAME  # noqa: E402
import xxhash  # noqa: E402

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
OUT = 'C:/kyty/m657/m2a/x'
BASE_DIR = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564'
VAR_DIR = BASE_DIR + '/variant_fixb26_fixb1b_fixf10_fixf19'
THEMES = ['T234', 'T233', 'T256', 'T306', 'T032', 'T203']
CONFIGS = ['base', 'u', 'z'] + ['t' + t for t in THEMES] + ['all']
# (theme, stage, hash16, cache dir)
ROWS = [
    ('T234', 'cs', '77076965e0344358', BASE_DIR),
    ('T234', 'ps', '1d611e7de1c75dbe', BASE_DIR),
    ('T306', 'ps', '5a34b303576ee324', VAR_DIR),
    ('T306', 'ps', 'f47c0c097c598a36', VAR_DIR),
    ('T306', 'cs', '7b4078750f32db50', VAR_DIR),
    ('T306', 'ps', 'c7143960900de8db', VAR_DIR),
    ('T306', 'ps', 'b96c2898f05637df', VAR_DIR),
    ('T306', 'cs', '8d2319190763817e', VAR_DIR),
    ('T306', 'ps', '2e2ae33a4d374e8f', VAR_DIR),
]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def env_for(name):
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    if name == 'z':
        for t in THEMES:
            env['KYTY_M_' + t] = '0'
    elif name == 'all':
        for t in THEMES:
            env['KYTY_M_' + t] = '1'
    elif name.startswith('t'):
        env['KYTY_M_' + name[1:]] = '1'
    return env


def main():
    base_exe, dev_exe = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    guard()
    for d in ('cache', 'gcn', 'run'):
        os.makedirs(OUT + '/' + d, exist_ok=True)
    want = {r[2] for r in ROWS}
    codes = {}
    for fp in [GAME + 'eboot.bin']:
        for src, elf, code in elf_programs(fp):
            h = '%016x' % xxhash.xxh3_64_intdigest(code)
            if h in want and h not in codes:
                codes[h] = code
    lines = []
    ok = True
    for theme, stage, h, cdir in ROWS:
        guard()
        files = [f for f in os.listdir(cdir) if f.startswith('%s_%s_' % (stage, h)) and f.endswith('.bin')]
        if not files or h not in codes:
            print('row', h, 'missing cache or code', files, h in codes)
            ok = False
            continue
        cache = '%s/cache/%s' % (OUT, files[0])
        shutil.copyfile(cdir + '/' + files[0], cache)
        gcn = '%s/gcn/%s_%s.bin' % (OUT, stage, h)
        open(gcn, 'wb').write(codes[h])
        dec = subprocess.run([dev_exe], env=dict(env_for('u'), KYTY_M_DECODE=gcn), capture_output=True,
                             timeout=120).stdout.decode('utf-8', 'replace')
        open('%s/gcn/%s_%s.dec.txt' % (OUT, stage, h), 'w', newline='\n').write(dec)
        if theme == 'T234':
            hits = len(re.findall(r': DS_M(?:IN|AX)_F32 ', dec))
        else:
            hits = len([l for l in dec.split('\n') if re.search(r': IMAGE_SAMPLE\w* ', l, re.I) and
                        re.search(r'sample_flags=\S*offset', l)])
        shas = {}
        rcs = {}
        for c in CONFIGS:
            guard()
            work = '%s/run/%s/%s_%s' % (OUT, c, stage, h)
            os.makedirs(work, exist_ok=True)
            spv = work + '/out.spv'
            env = env_for(c)
            env['KYTY_RECOMPILE'] = '%s;%s;%s;0' % (gcn, cache, spv)
            p = subprocess.run([base_exe if c == 'base' else dev_exe], cwd=work, env=env, capture_output=True,
                               timeout=300)
            open(work + '/log.txt', 'wb').write(p.stdout + p.stderr)
            rcs[c] = p.returncode
            shas[c] = sha(spv) if p.returncode == 0 and os.path.exists(spv) else None
        log_u = open('%s/run/u/%s_%s/log.txt' % (OUT, stage, h), 'rb').read().decode('utf-8', 'replace')
        warn = [l for l in log_u.split('\n') if 'code size' in l]
        diff = [c for c in CONFIGS[1:] if shas[c] != shas['base']]
        member = all(rcs[c] == 0 for c in CONFIGS) and shas['u'] == shas['base'] and shas['z'] == shas['base']
        theme_changed = shas['t' + theme] != shas['base']
        other = [c for c in diff if c not in ('t' + theme, 'all') and not c.startswith('tT233')]
        line = '%s\t%s\t%s\tinstr=%d\trc=%s\tcache=%s %s\tgcn_sha=%s\tdiffer_from_base=%s\ttheme_changed=%d\twarn=%s' % (
            theme, stage, h, hits, ','.join('%s:%s' % (c, rcs[c]) for c in CONFIGS if rcs[c] != 0) or 'all0',
            files[0], sha(cache)[:16], sha(gcn)[:16], ','.join(diff) or '-', theme_changed, warn[:1])
        print(line)
        lines.append(line)
        ok &= member and hits >= 1
    open(OUT + '/corpus_x.tsv', 'w', newline='\n').write('\n'.join(lines) + '\n')
    print('corpus_x.tsv sha256', sha(OUT + '/corpus_x.tsv'))
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
