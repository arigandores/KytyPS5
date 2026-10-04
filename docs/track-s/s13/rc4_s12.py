#!/usr/bin/env python3
"""rc4_s12.py - S13a3 (HPP-537), item 436 (b)(4): before the code, check on the logs C:/kyty/s288/s12/log_s12_*.txt that both
lines of the end of the preparation screen ("ShaderPreparation: ready", "PipelinePrecache: all pipelines created") are printed
in the arms of the seal form (precache by default, KYTY_S_PCW=1) and that >= 1 guest frame row ("FrameTrace: n=", the form the
scorer counts) follows the later of them.  Streaming, binary.  ASCII output."""
import glob
import hashlib
import sys

M_READY = b'ShaderPreparation: ready'
M_CREATED = b'PipelinePrecache: all pipelines created'
M_FT = b'FrameTrace: n='
M_SPCW = b'S-pcw:'


def one(p):
    h = hashlib.sha256()
    n = 0
    ready = created = None
    nready = ncreated = 0
    ft_before = ft_after = 0
    first_ft = None
    first_ft_after = None
    spcw = set()
    with open(p, 'rb') as f:
        for line in f:
            h.update(line)
            n += 1
            if line.startswith(M_FT):
                if first_ft is None:
                    first_ft = n
                if ready is not None and created is not None:
                    ft_after += 1
                    if first_ft_after is None:
                        first_ft_after = n
                else:
                    ft_before += 1
            elif line.startswith(M_READY):
                nready += 1
                if ready is None:
                    ready = n
            elif line.startswith(M_CREATED):
                ncreated += 1
                if created is None:
                    created = n
            elif line.startswith(M_SPCW):
                spcw.add(line.strip().decode('latin1'))
    return dict(sha=h.hexdigest(), lines=n, ready=ready, nready=nready, created=created, ncreated=ncreated,
                ft_before=ft_before, ft_after=ft_after, first_ft=first_ft, first_ft_after=first_ft_after, spcw=sorted(spcw))


def main():
    ok_all = True
    paths = sorted(glob.glob('C:/kyty/s288/s12/log_s12_*.txt'))
    print('rc4_s12.py sha256 %s; logs %d' % (hashlib.sha256(open(__file__, 'rb').read()).hexdigest(), len(paths)))
    for p in paths:
        r = one(p)
        later = max(r['ready'] or 0, r['created'] or 0) if r['ready'] and r['created'] else None
        ok = r['ready'] is not None and r['created'] is not None and r['ft_after'] >= 1
        pcw1 = any('KYTY_S_PCW=1' in x for x in r['spcw'])
        print('%s sha256 %s lines %d; S-pcw %s; "ShaderPreparation: ready" first line %s (count %d); '
              '"PipelinePrecache: all pipelines created" first line %s (count %d); the later line %s; first FrameTrace row line '
              '%s; FrameTrace rows before the later line %d, after it %d (first after: line %s) -> %s' % (
                  p.replace(chr(92), '/'), r['sha'], r['lines'], ';'.join(r['spcw']) or 'none', r['ready'], r['nready'],
                  r['created'], r['ncreated'], later, r['first_ft'], r['ft_before'], r['ft_after'], r['first_ft_after'],
                  'BOTH LINES AND A GUEST FRAME AFTER' if ok else 'MISSING'))
        if pcw1:
            ok_all = ok_all and ok
    print('RC4 CHECK (arms with KYTY_S_PCW=1): %s' % ('ALL PRINT BOTH' if ok_all else 'A LINE IS MISSING - a question to the lead'))
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
