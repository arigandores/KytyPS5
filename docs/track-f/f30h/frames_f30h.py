# F30h (HPP-718, Probe Designer): per-frame link of rts_bad_rx with rts_xb_ser / rts_xb_meta in the F30f logs (read only).
# Usage: python frames_f30h.py <log dir> <out tsv> [tags...]
import re
import sys

LOGDIR = sys.argv[1]
OUT = sys.argv[2]
TAGS = sys.argv[3:] or ['f30_s%d_%s' % (s, m) for s in range(1, 10) for m in ('c3', 'c4', 'v')]
KV = re.compile(rb'(rts_[a-z0-9_]+)=(\d+)')
NRE = re.compile(rb'FrameTrace-x: n=(\d+)')
ENTRY = b'Level has started'


def scan(tag):
    path = '%s/log_%s.txt' % (LOGDIR, tag)
    frames = []
    entry_seen = False
    entry_idx = None
    modes = []
    verify = []
    with open(path, 'rb') as f:
        for line in f:
            if ENTRY in line and not entry_seen:
                entry_seen = True
                entry_idx = len(frames)
            if line.startswith(b'RtSkip: mode'):
                modes.append(line.strip().decode('ascii', 'replace'))
            if line.startswith(b'RtSkipVerify:'):
                verify.append(line.strip().decode('ascii', 'replace'))
            if line.startswith(b'FrameTrace-x:') and b'rts_' in line:
                m = NRE.match(line)
                d = {k.decode(): int(v) for k, v in KV.findall(line)}
                d['_n'] = int(m.group(1)) if m else -1
                frames.append(d)
    return frames, entry_idx, modes, verify


def main():
    rows = []
    keys_all = set()
    out = open(OUT, 'w', encoding='utf-8', newline='\n')
    for tag in TAGS:
        frames, entry_idx, modes, verify = scan(tag)
        for d in frames:
            keys_all.update(k for k in d if k.startswith('rts_'))
        S = {}
        for d in frames:
            for k, v in d.items():
                if k.startswith('rts_'):
                    S[k] = S.get(k, 0) + v
        g = lambda d, k: d.get(k, 0)
        nf = len(frames)
        f_rx = sum(1 for d in frames if g(d, 'rts_bad_rx') > 0)
        f_ser = sum(1 for d in frames if g(d, 'rts_xb_ser') > 0)
        f_both = sum(1 for d in frames if g(d, 'rts_bad_rx') > 0 and g(d, 'rts_xb_ser') > 0)
        f_eq = sum(1 for d in frames if g(d, 'rts_bad_rx') == g(d, 'rts_xb_ser') and g(d, 'rts_bad_rx') > 0)
        f_eq_any = sum(1 for d in frames if g(d, 'rts_bad_rx') == g(d, 'rts_xb_ser'))
        f_eq_sm = sum(1 for d in frames if g(d, 'rts_bad_rx') == g(d, 'rts_xb_ser') + g(d, 'rts_xb_meta'))
        diffs = [g(d, 'rts_bad_rx') - g(d, 'rts_xb_ser') for d in frames]
        pos = sum(x for x in diffs if x > 0)
        neg = -sum(x for x in diffs if x < 0)
        f_bx = sum(1 for d in frames if g(d, 'rts_bad_b') != g(d, 'rts_bad_rx'))
        # place-A-only reports = rts_bad - rts_bad_b
        out.write('## %s frames=%d entry_frame_idx=%s\n' % (tag, nf, entry_idx))
        for m in modes:
            out.write('  mode_line: %s\n' % m)
        bits = {}
        for v in verify:
            mm = re.search(r'bits=(0x[0-9a-f]+)', v)
            if mm:
                bits[mm.group(1)] = bits.get(mm.group(1), 0) + 1
        out.write('  verify_lines=%d bits=%s\n' % (len(verify), bits))
        for k in sorted(S):
            out.write('  sum %s=%d\n' % (k, S[k]))
        out.write('  frames_rx>0=%d frames_ser>0=%d frames_both=%d frames_rx==ser>0=%d frames_rx==ser(all)=%d '
                  'frames_rx==ser+meta=%d frames_b!=rx=%d sum(rx-ser)+=%d sum(ser-rx)+=%d\n'
                  % (f_rx, f_ser, f_both, f_eq, f_eq_any, f_eq_sm, f_bx, pos, neg))
        rows.append((tag, nf, S, f_rx, f_ser, f_both, f_eq, f_eq_any, f_eq_sm, f_bx, pos, neg))
        # first 5 frames with rx != ser
        k = 0
        for d in frames:
            if g(d, 'rts_bad_rx') != g(d, 'rts_xb_ser') and k < 8:
                k += 1
                out.write('  diff_frame n=%d rx=%d ser=%d meta=%d b=%d bad=%d pb=%d chk_b=%d ids=%d live=%d bound=%d pass=%d\n'
                          % (d['_n'], g(d, 'rts_bad_rx'), g(d, 'rts_xb_ser'), g(d, 'rts_xb_meta'), g(d, 'rts_bad_b'),
                             g(d, 'rts_bad'), g(d, 'rts_pb'), g(d, 'rts_chk_b'), g(d, 'rts_xb_ids'),
                             g(d, 'rts_xb_live'), g(d, 'rts_xb_bound'), g(d, 'rts_xb_pass')))
        out.flush()
        print(tag, nf, 'rx', S.get('rts_bad_rx'), 'ser', S.get('rts_xb_ser'), 'meta', S.get('rts_xb_meta'),
              'b', S.get('rts_bad_b'), 'bad', S.get('rts_bad'), 'pb', S.get('rts_pb'), 'f_rx', f_rx, 'f_ser', f_ser,
              'f_eq_all', f_eq_any, 'f_eq_sm', f_eq_sm, '+', pos, '-', neg, flush=True)
    out.write('\nkeys: %s\n' % ' '.join(sorted(keys_all)))
    out.write('ALL OK\n')
    out.close()


main()
