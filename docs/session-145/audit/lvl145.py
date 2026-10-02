# lvl145.py - Session Auditor, s145 step 3 (HPP-353): "cold first entry" of the 16 levels of sc145 - is there an earlier
# entry of any of them in the emulator logs written since the inventory of s141 (2026-09-30) outside the sc145 tags?
# Every *.txt file larger than 5 MB under the track roots (p283, f287, s288) and the session roots s141..s145 with the
# line "GuestOut: Level has started: <level>" or "StartLevel <level>" for one of the 16 levels (and their sub-level names).
# READ ONLY, mmap. Usage: python lvl145.py [--list]
import os, sys, mmap, datetime
from multiprocessing import Pool

ROOTS = ['C:/kyty/p283', 'C:/kyty/f287', 'C:/kyty/s288', 'C:/kyty/s141', 'C:/kyty/s142', 'C:/kyty/s143', 'C:/kyty/s144', 'C:/kyty/s145']
LV = ['small_pot_lava', 'spin_drill_natural_cave', 'enemy_taco', 'jack_in_the_box', 'final_shooting', 'picup_light', 'enemy_snake',
      'light_gadget_graveyard', 'shuriken_ninja_castle', 'final_stage', 'mini_rocket_chain', 'enemy_chameleon', 'bonus_path_maker_mix',
      'enemy_bird', 'cymbal_party_land', 'enemy_final']
UTC = datetime.timezone.utc
KEY = b'Level has started: '
SKIP = ('mutwork', 'mutcache', '__pycache__', 'vidframes', 'fx_')


def scan(p):
    out = {'path': p, 'size': os.path.getsize(p), 'mtime': os.stat(p).st_mtime, 'starts': []}
    with open(p, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        q = mm.find(KEY)
        k = 0
        while q != -1 and k < 200:
            e = mm.find(b'\n', q)
            out['starts'].append(mm[q + len(KEY):e if e != -1 else q + 80].strip().decode('ascii', 'replace')[:60])
            k += 1
            q = mm.find(KEY, q + 1)
        mm.close()
    return out


def main():
    files = []
    for root in ROOTS:
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if not d.startswith(SKIP)]
            for f in fn:
                if f.endswith('.txt'):
                    p = os.path.join(dp, f).replace(chr(92), '/')
                    try:
                        if os.path.getsize(p) > 5000000:
                            files.append(p)
                    except OSError:
                        pass
    files.sort()
    tot = sum(os.path.getsize(p) for p in files)
    print('FILES %d, %.1f GB' % (len(files), tot / 1e9))
    if '--list' in sys.argv:
        for root in ROOTS:
            rr = [p for p in files if p.startswith(root + '/')]
            print('ROOT %s: %d files, %.1f GB' % (root, len(rr), sum(os.path.getsize(p) for p in rr) / 1e9))
        return
    with Pool(8) as pool:
        res = pool.map(scan, files, chunksize=1)
    hits = 0
    names = {}
    for r in res:
        for s in r['starts']:
            names[s] = names.get(s, 0) + 1
        hl = sorted(set(s for s in r['starts'] if s in LV))
        if hl:
            base = os.path.basename(r['path'])
            own = r['path'].startswith('C:/kyty/s145/') and (base.startswith(('log_v145_', 'log_w145_')) or base == 'abort_w145_06_kyty.txt')
            hits += 0 if own else 1
            print('%s %s size %d mtime %s levels %s' % ('SC145' if own else 'OTHER', r['path'], r['size'],
                                                      datetime.datetime.fromtimestamp(r['mtime'], UTC).strftime('%Y-%m-%dT%H:%M:%SZ'), hl))
    print('LEVEL NAMES in "Level has started:" lines over all files: %s' % sorted(names.items(), key=lambda x: -x[1]))
    print('LOGS OUTSIDE THE sc145 TAGS WITH AN ENTRY LINE OF ONE OF THE 16 LEVELS: %d' % hits)
    print('ALL DONE')


if __name__ == '__main__':
    main()
