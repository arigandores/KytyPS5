"""cachesig_f6e.py - F6e (HPP-377): the manifest of the translation cache by signature (ROADMAP p.290(b)(1): "the state of the
translation cache of the signature 56189185 before f6e_a1 - a line of the seal").  For the root of _ShaderCache/PPSA21564 and
every variant directory one level under it: the number of files, the number of *.bin files by the signature of their header
"KytySC3:<sig>" (first 8 hex digits), files without that header.  Read only.  ASCII only.
  python cachesig_f6e.py [<cache dir>]       (default: the game cache)
Last line: 'cachesig ...' - one line for times.txt.
"""
import os
import sys

CACHE = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564'
MAGIC = b'KytySC3:'


def sig_of(path):
    try:
        with open(path, 'rb') as f:
            h = f.read(64)
    except OSError:
        return None
    if not h.startswith(MAGIC):
        return None
    return h[len(MAGIC):len(MAGIC) + 8].decode('latin1')


def survey(d):
    """{place: (files, {sig8: n}, other)} for the root ('.') and each variant directory."""
    out = {}
    if not os.path.isdir(d):
        return out
    places = ['.'] + sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)))
    for p in places:
        full = d if p == '.' else os.path.join(d, p)
        files = [x for x in os.listdir(full) if os.path.isfile(os.path.join(full, x))]
        sigs = {}
        other = 0
        for x in files:
            s = sig_of(os.path.join(full, x)) if x.endswith('.bin') else None
            if s is None:
                other += 1
            else:
                sigs[s] = sigs.get(s, 0) + 1
        out[p] = (len(files), sigs, other)
    return out


def line(res, want='56189185'):
    parts = []
    total_want = 0
    for p, (n, sigs, other) in res.items():
        total_want += sigs.get(want, 0)
        parts.append('%s: files %d sig %s other %d' % (p, n, ','.join('%s=%d' % kv for kv in sorted(sigs.items())) or '-', other))
    return 'cachesig %s; files of signature %s: %d' % ('; '.join(parts) or 'no cache dir', want, total_want)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    d = a[0] if a else CACHE
    print(line(survey(d)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
