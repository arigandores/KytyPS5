"""S17c (HPP-613): the description of the S-replay state of the emulator folder before a tag (state_in.txt) and after the emulator
exit, before the return of the caches (state_out.txt).  Three directories of _ShaderCache/PPSA21564: the variant folder of KYTY_FIX_F19=0
(variant_fixb26_fixb1b_fixf10, 'f10'), of KYTY_FIX_F19=1 (variant_fixb26_fixb1b_fixf10_fixf19, 'f19') and the catalogue folder 'replay'.
Per directory one line 'dir <name> absent' or 'dir <name> present files <n> cache_files <n> pipelines_bin <absent|size sha256>';
for replay also 'replay.cur <text>' and one line per file 'file <name> <size> <sha256>'.  ASCII only.
usage: python state_s17c.py [<_ShaderCache/PPSA21564 path>]"""
import hashlib
import os
import sys

TC = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564'
DIRS = (('f10', 'variant_fixb26_fixb1b_fixf10'), ('f19', 'variant_fixb26_fixb1b_fixf10_fixf19'), ('replay', 'replay'))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def is_cache_file(name):
    return name[:3] in ('vs_', 'ps_', 'cs_') and name.endswith('.bin') and len(name) == 40


def describe(tc):
    out = []
    for label, name in DIRS:
        d = os.path.join(tc, name)
        if not os.path.isdir(d):
            out.append('dir %s absent' % label)
            continue
        names = sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n)))
        pb = os.path.join(d, 'pipelines.bin')
        pbs = '%d %s' % (os.path.getsize(pb), sha(pb)) if os.path.isfile(pb) else 'absent'
        out.append('dir %s present files %d cache_files %d pipelines_bin %s' % (label, len(names), sum(1 for n in names if is_cache_file(n)), pbs))
        if label == 'replay':
            cur = os.path.join(d, 'replay.cur')
            text = open(cur, 'rb').read().decode('ascii', 'replace').strip() if os.path.isfile(cur) else '<none>'
            out.append('replay.cur %s' % text)
            for n in names:
                p = os.path.join(d, n)
                out.append('file %s %d %s' % (n.encode('ascii', 'replace').decode('ascii'), os.path.getsize(p), sha(p)))
    return out


def parse(text):
    """state text -> {label: dict(present, files, cache_files, pipelines_bin, cur, replay_files {name: (size, sha)})}."""
    res = {}
    for line in text.splitlines():
        a = line.split()
        if len(a) >= 3 and a[0] == 'dir':
            if a[2] == 'absent':
                res[a[1]] = dict(present=False)
            else:
                res[a[1]] = dict(present=True, files=int(a[4]), cache_files=int(a[6]), pipelines_bin=(a[8] != 'absent'),
                                 replay_files={}, cur=None)
        elif len(a) >= 2 and a[0] == 'replay.cur' and 'replay' in res:
            res['replay']['cur'] = a[1]
        elif len(a) == 4 and a[0] == 'file' and 'replay' in res:
            res['replay']['replay_files'][a[1]] = (int(a[2]), a[3])
    return res


if __name__ == '__main__':
    print('\n'.join(describe(sys.argv[1] if len(sys.argv) > 1 else TC)))
