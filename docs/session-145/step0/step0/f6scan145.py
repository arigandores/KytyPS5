#!/usr/bin/env python3
"""f6scan145.py - session 145 step 0 (HPP-350; ROADMAP "SESSION 122" item 273 (k)(2)): the data for naming the one message id
of the W filter.  Over the W logs (and emulator stdouts) of session 144, streaming in binary: the "[Vulkan][<sev>][<type>]: "
lines by severity, the lines of the F6 text ("... there is no VkRenderingInfo::pColorAttachments[N] and this write is
unused."), the layer limit lines ("this will be the last time reporting it") with the message that follows each, the
"[Vulkan][" lines that are NOT the F6 text (the validation-active term of the W admission must survive the filter), and
the window-event lines.  ASCII output.  usage: f6scan145.py <out.txt> [tag ...]"""
import hashlib
import os
import re
import sys
from multiprocessing import Pool

ROOT = 'C:/kyty/s144'
CHUNK = 1 << 26
RX_VK = re.compile(rb'\[Vulkan\]\[(\w)\]\[(\d+)\]: ([^\n]*)')
F6 = b'and this write is unused.'
F6_DR = b'there is no VkRenderingInfo::pColorAttach'
LIMIT = b'this will be the last time reporting it'
WIN = (b' minimized\n', b' restored\n', b' resized to ', b' size changed to ', b' lost keyboard focus\n')
RX_WIN = re.compile(rb'Window \d+( minimized\n| restored\n| resized to | size changed to | lost keyboard focus\n)')
REC = b'Recovering Vulkan swapchain'


def one(path):
    res = dict(path=path, sev={}, f6=0, f6_dr=0, limit=[], other={}, other_n=0, win={}, rec=0, bytes=0)
    h = hashlib.sha256()
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            h.update(b)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf
                    continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if not whole:
                break
            res['bytes'] += len(whole)
            for m in RX_VK.finditer(whole):
                s = m.group(1).decode()
                res['sev'][s] = res['sev'].get(s, 0) + 1
                msg = m.group(3)
                if LIMIT in msg:
                    e = whole.find(b'\n', m.end() + 1)
                    nxt = whole[m.end() + 1:e if e >= 0 else len(whole)]
                    res['limit'].append((s, nxt[:400].decode('latin1')))
                    continue
                if F6 in msg:
                    res['f6'] += 1
                    if F6_DR in msg:
                        res['f6_dr'] += 1
                    continue
                res['other_n'] += 1
                k = s + ' ' + re.sub(r'0x[0-9a-fA-F]+', '0x?', msg[:110].decode('latin1'))
                k = re.sub(r'\d+', 'N', k)
                res['other'][k] = res['other'].get(k, 0) + 1
            for m in RX_WIN.finditer(whole):
                k = m.group(1).strip().decode()
                res['win'][k] = res['win'].get(k, 0) + 1
            res['rec'] += whole.count(REC)
            if not b:
                break
    res['sha256'] = h.hexdigest()
    return res


def main():
    out = sys.argv[1]
    tags = sys.argv[2:] or ['w144_%02d' % i for i in range(21)]
    paths = []
    for t in tags:
        for p in ('log_%s.txt' % t, 'stdout_%s.txt' % t):
            fp = os.path.join(ROOT, p)
            if os.path.isfile(fp):
                paths.append(fp)
    with Pool(8) as pool:
        rs = pool.map(one, paths)
    lines = ['f6scan145 over %d files of %s' % (len(rs), ROOT)]
    tot_lim = {}
    for r in rs:
        lines.append('FILE %s sha256 %s bytes %d' % (r['path'], r['sha256'], r['bytes']))
        lines.append('  [Vulkan] by severity %s; F6 text lines %d (VkRenderingInfo form %d); limit lines %d; '
                     'other [Vulkan][ lines %d; window %s; Recovering Vulkan swapchain %d' % (
                         sorted(r['sev'].items()), r['f6'], r['f6_dr'], len(r['limit']), r['other_n'],
                         sorted(r['win'].items()) or 'none', r['rec']))
        for s, nxt in r['limit']:
            lines.append('  LIMIT [%s] next line: %s' % (s, nxt))
            tot_lim[F6_DR.decode() in nxt] = tot_lim.get(F6_DR.decode() in nxt, 0) + 1
        for k, n in sorted(r['other'].items(), key=lambda kv: -kv[1])[:12]:
            lines.append('  OTHER %6d %s' % (n, k))
    logs = [r for r in rs if os.path.basename(r['path']).startswith('log_')]
    lines.append('SUMMARY logs %d; logs with a limit line %d; limit lines followed by the F6 VkRenderingInfo text %d, by another '
                 'text %d; logs with other [Vulkan][ lines >= 1: %d of %d' % (
                     len(logs), sum(1 for r in logs if r['limit']), tot_lim.get(True, 0), tot_lim.get(False, 0),
                     sum(1 for r in logs if r['other_n'] >= 1), len(logs)))
    open(out, 'w', encoding='ascii', errors='replace', newline='\n').write('\n'.join(lines) + '\n')
    print(lines[-1])


if __name__ == '__main__':
    main()
