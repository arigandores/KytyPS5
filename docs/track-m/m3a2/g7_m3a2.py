"""Track M link M3a2 (HPP-861; ROADMAP s122 item 778 (d)(7); port of M3a g7_m3a.py, HPP-842): the G7 rows over the logs of every tag
of the series M3 of wave 2.  NO VERDICT (M3b2 reads).  Verbs (run them in order after the series, outside the lock):
  sweep <budget_s> [workers]   the F48a method: docs/track-f/f32a/sweep_f32a.py imported unchanged with F32A_ROOT = C:/kyty/m657/m3a2,
                               F32A_OUT = C:/kyty/m657/m3a2/g7, F32A_STOP = C:/kyty/m657/STOP and T0 = item 749 (2026-10-12 05:11:25
                               UTC); 'list' then 'run' (resumable by its segment files)
  agg                          per log the F0 signatures (KEY of sweep_f0.py).  The baseline: the F0 signatures, the signatures of the MS1
                               logs of the series M3a (their segment files C:/kyty/m657/m3a/g7/seg by its list loglist_f32a.tsv, the sweep
                               of M3a, item 765) and of the MS1 logs of this series (m3w2_g5_ap / a1 / a2).  A signature of an MS2 log
                               not in the baseline - a CANDIDATE (new K1-K4 or not - the class is read by M3b2); the signatures of the
                               MS1 logs of this series absent from the MS2 logs - a row
  grep                         docs/track-m/m1/m1a2/grep_sig_m1a2.py over the logs and stdout of the series (item 757 (v)), per binary
  wit                          the witnesses of docs/track-m/m1/m1a2/witness.tsv (item 756 (b)(4)): for each level, the keys present in
                               the MS1 support V log of M3a (sg m3_sg_v_r1, hb m3_hb_v, mg m3_mg_v) and absent from the MS2 V log
                               (m3w2_<L>_v) - LOST.  Note N1 (item 783 (d)): keys only, no port numbers
  rows                         per log the lines without a knob of item 767 (z) (T031 'GuestPrintf: negative precision', T309
                               'AmprRecordSpace: refused' / 'AmprWriteAddress: refused', T023 'AgcReserveDW: cursor state'; >= 1 - a
                               register row, not a failure) and the lines our scripts read (item 756 (b)(4): 'AudioStat:', 'AvTrace:',
                               'MTexOffset:'; 'AudioStat:' / 'AvTrace:' print only with KYTY_AV_TRACE=1 - absent in the V / W form by
                               design, a row)
The summary lines: 'G7 candidates <n>', 'G7 grep <bin>: fatal hits <n>', 'G7 witnesses lost <n>', 'G7 rows no-knob lines <n>'.  Refuses
under the lock (exit 3) and with the stop file (exit 4).  ASCII only.  usage: python g7_m3a2.py sweep <budget> [workers] | agg | grep |
wit | rows"""
import calendar
import collections
import csv
import hashlib
import os
import pickle
import re
import subprocess
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - exit 3')
    sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP - exit 4')
    sys.exit(4)
G = 'C:/kyty/m657/m3a2'
OUT = G + '/g7'
M3A = 'C:/kyty/m657/m3a'
os.environ['F32A_ROOT'] = G
os.environ['F32A_OUT'] = OUT
os.environ['F32A_STOP'] = 'C:/kyty/m657/STOP'
F32A = 'C:/kyty/KytyPS5/docs/track-f/f32a'
GREP = 'C:/kyty/KytyPS5/docs/track-m/m1/m1a2/grep_sig_m1a2.py'
WIT = 'C:/kyty/KytyPS5/docs/track-m/m1/m1a2/witness.tsv'
T0_749 = calendar.timegm((2026, 10, 12, 5, 11, 25))
SUPPORT = {'sg': 'm3_sg_v_r1', 'hb': 'm3_hb_v', 'mg': 'm3_mg_v'}
NOKNOB = (b'GuestPrintf: negative precision', b'AmprRecordSpace: refused', b'AmprWriteAddress: refused', b'AgcReserveDW: cursor state')
READ = (b'AudioStat:', b'AvTrace:', b'MTexOffset:')
sys.path.insert(0, G)
import m3a2_read  # noqa: E402


def sweep_mod():
    if F32A not in sys.path:
        sys.path.insert(0, F32A)
    import sweep_f32a as S  # noqa: E402
    S.T0 = T0_749
    return S


def tag_of(path):
    m = re.match(r'^log_(m3w2_[a-z0-9_]+)\.txt$', os.path.basename(path))
    return m.group(1) if m and m3a2_read.plan_of(m.group(1)) else None


def sigs_of(S, rows, root, seg, accept):
    per, missing = {}, []
    for p, s, mt, kind, osz, st, note in rows:
        t = accept(p)
        if st != 'SWEEP' or t is None or os.path.dirname(p).replace('\\', '/') != root:
            continue
        md = hashlib.md5(p.encode('utf-8')).hexdigest()
        whole = kind == 'xz' or osz <= S.SEG_BYTES
        nseg = 1 if whole else (osz + S.SEG_BYTES - 1) // S.SEG_BYTES
        sg = {}
        ok = True
        for i in range(nseg):
            fn = '%s/%s_%d.pkl' % (seg, md, i)
            if not os.path.exists(fn):
                ok = False
                break
            r = pickle.load(open(fn, 'rb'))
            for k, v in r['sigs'].items():
                e = sg.setdefault(k, [0, v[2]])
                e[0] += v[0]
        if not ok:
            missing.append(t)
            continue
        per[t] = sg
    return per, missing


def m3a_rows():
    rows = []
    for l in open(M3A + '/g7/loglist_f32a.tsv', encoding='utf-8'):
        x = l.rstrip('\n').split('\t')
        rows.append((x[0], int(x[1]), int(x[2]), x[3], int(x[4]), x[5], x[6] if len(x) > 6 else ''))
    return rows


def m3a_ms1(p):
    m = re.match(r'^log_(m3_[a-z0-9_]+)\.txt$', os.path.basename(p))
    if not m or re.match(r'^m3_(sg|hb|mg|ac|f1|f2)_f$', m.group(1)) or m.group(1) in ('m3_g5_a1', 'm3_g5_a2'):
        return None
    return m.group(1)


def cmd_agg(S):
    base = set()
    if os.path.exists(S.F0_SIGS):
        for p, sg in pickle.load(open(S.F0_SIGS, 'rb')).items():
            base.update(sg.keys())
    nf0 = len(base)
    per_a, miss_a = sigs_of(S, m3a_rows(), M3A, M3A + '/g7/seg', m3a_ms1)
    for t in per_a:
        base.update(per_a[t].keys())
    per, missing = sigs_of(S, S.read_list(), G, S.SEG, tag_of)
    ms2 = [t for t in per if m3a2_read.plan_of(t)['bin'] == 'ms2']
    ms1 = [t for t in per if m3a2_read.plan_of(t)['bin'] == 'ms1']
    for t in ms1:
        base.update(per[t].keys())
    ms2_sigs = collections.defaultdict(list)
    for t in ms2:
        for k, v in per[t].items():
            ms2_sigs[k].append((t, v[0], v[1]))
    ms1_sigs = set()
    for t in ms1:
        ms1_sigs.update(per[t].keys())
    cand = sorted(k for k in ms2_sigs if k not in base)
    ms1only = sorted(k for k in ms1_sigs if k not in ms2_sigs)
    print('G7 agg: logs MS2 %d, MS1 %d (this series), M3a MS1 logs %d (missing segments %s); missing segments %s; F0 baseline %d; '
          'baseline with MS1 %d; signatures MS2 %d, MS1 %d' % (len(ms2), len(ms1), len(per_a), miss_a or 'none', missing or 'none', nf0,
                                                                len(base), len(ms2_sigs), len(ms1_sigs)))
    for k in cand:
        ex = ms2_sigs[k]
        print('  CANDIDATE %s | tags %s | lines %d | example %s' % (
            k.decode('latin1')[:160], ' '.join(t for t, n, e in ex)[:200], sum(n for t, n, e in ex),
            ex[0][2].decode('utf-8', 'replace').strip()[:200] if isinstance(ex[0][2], bytes) else str(ex[0][2])[:200]))
    for k in ms1only:
        print('  MS1-ONLY (this series; not in the MS2 logs; a row) %s' % k.decode('latin1')[:160])
    print('G7 candidates %d' % len(cand))
    return len(cand)


def cmd_grep():
    files = sorted(os.path.join(G, f) for f in os.listdir(G) if re.match(r'^(log|stdout)_m3w2_[a-z0-9_]+\.txt$', f))
    files = [f for f in files if m3a2_read.plan_of(re.sub(r'^(log|stdout)_', '', os.path.basename(f))[:-4])]
    res = {}
    for side in ('ms2', 'ms1'):
        fl = [f for f in files if m3a2_read.plan_of(re.sub(r'^(log|stdout)_', '', os.path.basename(f))[:-4])['bin'] == side]
        if not fl:
            print('G7 grep %s: no files' % side)
            res[side] = None
            continue
        r = subprocess.run([sys.executable, GREP] + fl, capture_output=True)
        txt = r.stdout.decode('utf-8', 'replace')
        open(os.path.join(OUT, 'grep_%s.out.txt' % side), 'w', encoding='utf-8', newline='\n').write(txt)
        hits = sum(int(v) for v in re.findall(r'\tfatal=(\d+)', txt))
        res[side] = hits
        print('G7 grep %s: %d files, rc %d, output grep_%s.out.txt sha256 %s; last line: %s' % (
            side, len(fl), r.returncode, side, hashlib.sha256(r.stdout).hexdigest()[:16], (txt.strip().splitlines() or ['-'])[-1][:200]))
        print('G7 grep %s: fatal hits (sum of the theme rows) %d' % (side, hits))
    return res


def count_keys(p, alt):
    c = collections.Counter()
    with open(p, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace'):
                continue
            for m in alt.finditer(line):
                c[m.group(0)] += 1
    return c


def cmd_wit():
    rows = list(csv.DictReader(open(WIT, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    keys = sorted(set(r[list(r.keys())[2]].encode('utf-8') for r in rows))
    alt = re.compile(b'|'.join(re.escape(k) for k in sorted(keys, key=len, reverse=True)))
    lost_total = 0
    for L in ('sg', 'hb', 'mg'):
        pa = os.path.join(G, 'log_m3w2_%s_v.txt' % L)
        pb = os.path.join(M3A, 'log_%s.txt' % SUPPORT[L])
        if not os.path.exists(pa) or not os.path.exists(pb):
            print('G7 wit %s: logs missing (MS2 %s, MS1 support %s)' % (L, os.path.exists(pa), os.path.exists(pb)))
            continue
        a, b = count_keys(pa, alt), count_keys(pb, alt)
        lost = sorted(k for k in b if k not in a)
        lost_total += len(lost)
        print('G7 wit %s: keys in MS1 %s %d, in MS2 m3w2_%s_v %d, LOST %d %s' % (
            L, SUPPORT[L], len(b), L, len(a), len(lost), [k.decode('utf-8', 'replace')[:60] for k in lost[:8]]))
    print('G7 witnesses lost %d' % lost_total)
    return lost_total


def cmd_rows():
    pat = re.compile(b'|'.join(re.escape(k) for k in NOKNOB + READ))
    total = 0
    for f in sorted(os.listdir(G)):
        t = re.match(r'^log_(m3w2_[a-z0-9_]+)\.txt$', f)
        if not t or not m3a2_read.plan_of(t.group(1)):
            continue
        c = collections.Counter()
        with open(os.path.join(G, f), 'rb') as fh:
            for line in fh:
                if line.startswith(b'FrameTrace'):
                    continue
                for m in pat.finditer(line):
                    c[m.group(0)] += 1
        nk = sum(c[k] for k in NOKNOB)
        total += nk
        print('G7 rows %s: no-knob %s; read %s' % (t.group(1), dict((k.decode(), c[k]) for k in NOKNOB if c[k]) or 0,
                                                   dict((k.decode(), c[k]) for k in READ)))
    print('G7 rows no-knob lines %d (>= 1 - a register row, item 778 (d)(7))' % total)
    return total


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    c = argv[0] if argv else ''
    if c == 'sweep':
        S = sweep_mod()
        S.cmd_list()
        S.cmd_run(float(argv[1]) if len(argv) > 1 else 480, int(argv[2]) if len(argv) > 2 else 4)
        return 0
    if c == 'agg':
        cmd_agg(sweep_mod())
        return 0
    if c == 'grep':
        cmd_grep()
        return 0
    if c == 'wit':
        cmd_wit()
        return 0
    if c == 'rows':
        cmd_rows()
        return 0
    print(__doc__.split('usage: ')[1])
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
