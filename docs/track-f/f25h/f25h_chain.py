#!/usr/bin/env python3
# F25h (HPP-675; ROADMAP s122 item 611(d)(2)(v)): the chain "Gpu W:emu_mutex -> waker Present, Present Sw" counted by
# OWN code from the recorded KYTY_DIAG_B32 lines (no reader). MEASUREMENT READING ONLY.
#
# Own definition (CH): a DiagB32 window (header "DiagB32: n=<n> dt_us=<dt>", dt >= 100 ms) that has
#  (1) a DiagB32-w record kind=emu_mutex whose waiter slot is the role Gpu and whose waker is the slot of the role
#      Present, with wait_us >= dt / 2, and
#  (2) the Present -t line with Sw >= half of the window samples (the header field samples).
# For each CH window it prints: the level (the first "Level has started:" line), the line position relative to it,
# dt, the obj of the record and its offset from the W:vo_pace obj of the run (VideoOutDriver::Impl this), wait_us,
# Present Sw / SwR, the FrameTrace-draw log_us / log_gpu_us of the same n and the FlipHold other_us of flip n-1.
# Windows with (1) but not (2) are counted as CH1.
#
# usage: f25h_chain.py <out file> <log> [<log> ...]
import hashlib
import os
import re
import sys

KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(\S*)')
LOGS = re.compile(rb'FrameTrace-draw: n=(\d+) logs=(\d+) log_us=(\d+) log_gpu_us=(\d+)')


def kv(line):
    return {k.decode(): v.decode('latin-1') for k, v in KV.findall(line)}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def scan(path):
    level, level_line = None, None
    hdr = {}          # n -> (dt, samples, line)
    tpres = {}        # n -> -t dict of Present
    roles = {}        # slot -> role (last seen)
    wem = {}          # n -> [w dicts]
    logx, fh = {}, {}
    vo = {}
    with open(path, 'rb') as f:
        for i, line in enumerate(f, 1):
            if line.startswith(b'DiagB32'):
                if line.startswith(b'DiagB32: n='):
                    d = kv(line)
                    hdr[int(d['n'])] = (int(d['dt_us']), int(d['samples']), i)
                elif line.startswith(b'DiagB32-t: n='):
                    d = kv(line)
                    roles[d['slot']] = d.get('role', '')
                    if d.get('role') == 'Present':
                        tpres[int(d['n'])] = d
                    if d.get('last') == 'W:vo_pace':
                        vo[d['obj']] = vo.get(d['obj'], 0) + 1
                elif line.startswith(b'DiagB32-w: n=') and b'kind=emu_mutex' in line:
                    d = kv(line)
                    wem.setdefault(int(d['n']), []).append(d)
                elif line.startswith(b'DiagB32-w: n=') and b'kind=vo_pace' in line:
                    d = kv(line)
                    vo[d['obj']] = vo.get(d['obj'], 0) + 1
            elif line.startswith(b'FrameTrace-draw: n='):
                m = LOGS.match(line)
                if m:
                    logx[int(m.group(1))] = (int(m.group(3)), int(m.group(4)))
            elif line.startswith(b'FlipHold:'):
                d = kv(line)
                fh[int(d['flip'])] = int(d['other_us'])
            elif level is None and b'Level has started:' in line:
                name = line.split(b'Level has started:', 1)[1].strip().decode('latin-1')
                if name:  # the first non-blank name (a blank one precedes it, diagB32.h TestArm)
                    level = name
                    level_line = i
    return level, level_line, hdr, tpres, roles, wem, logx, fh, vo


def main():
    out = open(sys.argv[1], 'w', encoding='utf-8')
    total = {'logs': 0, 'win100': 0, 'ch': 0, 'ch1': 0}
    for path in sys.argv[2:]:
        level, level_line, hdr, tpres, roles, wem, logx, fh, vo = scan(path)
        base = int(max(vo, key=vo.get), 16) if vo else None
        pslot = {n: d['slot'] for n, d in tpres.items()}
        ch, ch1 = [], []
        win100 = 0
        for n, (dt, samples, ln) in sorted(hdr.items()):
            if dt < 100000:
                continue
            win100 += 1
            p = tpres.get(n)
            if p is None:
                continue
            hit = None
            for w in wem.get(n, []):
                if roles.get(w['slot']) == 'Gpu' and w['waker'] == p['slot'] and int(w['wait_us']) * 2 >= dt:
                    if hit is None or int(w['wait_us']) > int(hit['wait_us']):
                        hit = w
            if hit is None:
                continue
            if int(p['Sw']) * 2 >= samples:
                ch.append((n, dt, samples, ln, hit, p))
            else:
                ch1.append((n, dt, samples, ln, hit, p))
        tag = os.path.basename(path)
        out.write('LOG %s sha256 %s level %s windows>=100ms %d CH %d CH1 %d vo_pace_base %s\n' % (
            tag, sha256(path), level, win100, len(ch), len(ch1), hex(base) if base is not None else '-'))
        for kind, rows in (('CH', ch), ('CH1', ch1)):
            for n, dt, samples, ln, w, p in rows:
                off = int(w['obj'], 16) - base if base is not None else None
                lx = logx.get(n)
                out.write('  %s %s n %d dt_us %d after_level %s obj %s off %s wait_us %s Present Sw %s/%d SwR %s H %s W %s'
                          ' log_us %s log_gpu_us %s fliphold_other_us(n-1) %s\n' % (
                              kind, tag, n, dt, 'yes' if level_line is not None and ln > level_line else 'no', w['obj'],
                              hex(off) if off is not None else '-', w['wait_us'], p['Sw'], samples, p['SwR'], p['H'],
                              p['W'], lx[0] if lx else '-', lx[1] if lx else '-', fh.get(n - 1, '-')))
        out.flush()
        total['logs'] += 1
        total['win100'] += win100
        total['ch'] += len(ch)
        total['ch1'] += len(ch1)
    out.write('TOTAL logs %d windows>=100ms %d CH %d CH1 %d\n' % (total['logs'], total['win100'], total['ch'], total['ch1']))
    out.close()


if __name__ == '__main__':
    main()
