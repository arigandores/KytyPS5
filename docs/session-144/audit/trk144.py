# trk144.py - Session Auditor s144 step 3 (HPP-333), ROADMAP item 270 (g)(2), supplement: the window / swapchain lines in the
# emulator logs of the track roots (p283, f287, s288) - every log_*.txt under them. READ ONLY, mmap, no sha (count and size only
# unless a hit is found - then sha256 of that log). Usage: python trk144.py
import os, sys, mmap, hashlib, datetime
from multiprocessing import Pool

ROOTS = ['C:/kyty/p283', 'C:/kyty/f287', 'C:/kyty/s288']
KEYS = [b'minimized', b'Recovering Vulkan swapchain', b'eErrorOutOfDateKHR', b'eSuboptimalKHR', b'restored',
        b'keyboard focus', b'vkCreateSwapchainKHR(): pCreateInfo->imageExtent']
UTC = datetime.timezone.utc


def scan(p):
    out = {'path': p, 'size': os.path.getsize(p), 'mtime': os.stat(p).st_mtime}
    if out['size'] == 0:
        out['n'] = {}
        return out
    with open(p, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        n = {}
        for k in KEYS:
            c = 0
            q = mm.find(k)
            first = q
            while q != -1:
                c += 1
                q = mm.find(k, q + 1)
            n[k.decode()] = (c, first if c else None)
        mm.close()
    out['n'] = n
    if any(v[0] for v in n.values()):
        h = hashlib.sha256()
        with open(p, 'rb') as f:
            for c in iter(lambda: f.read(1 << 22), b''):
                h.update(c)
        out['sha256'] = h.hexdigest()
    return out


def main():
    files = []
    for root in ROOTS:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if f.startswith('log_') and f.endswith('.txt'):
                    files.append(os.path.join(dp, f).replace(chr(92), '/'))
    files.sort()
    with Pool(8) as pool:
        res = pool.map(scan, files, chunksize=1)
    tot = sum(r['size'] for r in res)
    print('TRACK LOGS %d files, %.2f GB' % (len(res), tot / 1e9))
    for root in ROOTS:
        rr = [r for r in res if r['path'].startswith(root + '/')]
        print('ROOT %s: logs %d, %.2f GB; with a "minimized" line %d; with "Recovering Vulkan swapchain" %d; with eErrorOutOfDateKHR %d; '
              'with eSuboptimalKHR %d; with the swapchain extent error %d' % (
                  root, len(rr), sum(r['size'] for r in rr) / 1e9,
                  sum(1 for r in rr if r['n'].get('minimized', (0,))[0]),
                  sum(1 for r in rr if r['n'].get('Recovering Vulkan swapchain', (0,))[0]),
                  sum(1 for r in rr if r['n'].get('eErrorOutOfDateKHR', (0,))[0]),
                  sum(1 for r in rr if r['n'].get('eSuboptimalKHR', (0,))[0]),
                  sum(1 for r in rr if r['n'].get('vkCreateSwapchainKHR(): pCreateInfo->imageExtent', (0,))[0])))
    for r in res:
        hit = {k: v for k, v in r['n'].items() if v[0]}
        if hit:
            print('HIT %s size %d mtime %s sha256 %s %s' % (
                r['path'], r['size'], datetime.datetime.fromtimestamp(r['mtime'], UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
                r.get('sha256'), hit))
    print('ALL DONE')


if __name__ == '__main__':
    main()
