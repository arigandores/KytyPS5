"""Track M link M3a (HPP-842; ROADMAP s122 item 756 (g)(7), 757 (v)): the G7 rows over the logs of every tag of the series M3.
NO VERDICT (M3b reads).  Three parts, each a verb (run them in order after the series, outside the lock):
  sweep <budget_s> [workers]   the F48a method: docs/track-f/f32a/sweep_f32a.py imported unchanged (it imports the F0 scanner) with
                               F32A_ROOT = C:/kyty/m657/m3a, F32A_OUT = C:/kyty/m657/m3a/g7, F32A_STOP = C:/kyty/m657/STOP and the time
                               origin T0 = item 749 (2026-10-12 05:11:25 UTC); 'list' then 'run' (resumable by its segment files)
  agg                          per log (the segment files of the sweep): the F0 signatures (KEY of sweep_f0.py); a signature of an MS1
                               log that is in neither the F0 baseline nor any FS15 log of this series - a CANDIDATE (new K1-K4 or not -
                               the class is read by M3b); also the signatures of FS15 logs absent from the MS1 logs (a row)
  grep                         docs/track-m/m1/m1a2/grep_sig_m1a2.py over the logs and stdout of the series (item 757 (v): the
                               signatures the sweep keys do not catch)
  wit                          the witnesses of docs/track-m/m1/m1a2/witness.tsv (log lines our scripts read, item 756 (b)(4)): for each
                               level, the keys present in its FS15 log (m3_<L>_f) and absent from its MS1 V log (m3_<L>_v) - LOST
The summary line: 'G7 ROWS candidates <n>; grep fatal hits MS1 <n> / FS15 <n>; witnesses lost <n>'.  Refuses under the lock (exit 3)
and with the stop file (exit 4).  ASCII only.  usage: python g7_m3a.py sweep <budget> [workers] | agg | grep | wit"""
import calendar
import collections
import csv
import hashlib
import json
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
G = 'C:/kyty/m657/m3a'
OUT = G + '/g7'
os.environ['F32A_ROOT'] = G
os.environ['F32A_OUT'] = OUT
os.environ['F32A_STOP'] = 'C:/kyty/m657/STOP'
F32A = 'C:/kyty/KytyPS5/docs/track-f/f32a'
GREP = 'C:/kyty/KytyPS5/docs/track-m/m1/m1a2/grep_sig_m1a2.py'
WIT = 'C:/kyty/KytyPS5/docs/track-m/m1/m1a2/witness.tsv'
T0_749 = calendar.timegm((2026, 10, 12, 5, 11, 25))
sys.path.insert(0, G)
import m3a_read  # noqa: E402


def sweep_mod():
    if F32A not in sys.path:
        sys.path.insert(0, F32A)
    import sweep_f32a as S  # noqa: E402
    S.T0 = T0_749
    return S


def tag_of(path):
    m = re.match(r'^log_(m3_[a-z0-9_]+)\.txt$', os.path.basename(path))
    return m.group(1) if m and m3a_read.plan_of(m.group(1)) else None


def cmd_agg(S):
    base = set()
    if os.path.exists(S.F0_SIGS):
        for p, sg in pickle.load(open(S.F0_SIGS, 'rb')).items():
            base.update(sg.keys())
    per = {}
    missing = []
    for p, s, mt, kind, osz, st, note in S.read_list():
        t = tag_of(p)
        if st != 'SWEEP' or t is None or os.path.dirname(p).replace('\\', '/') != G:
            continue
        md = hashlib.md5(p.encode('utf-8')).hexdigest()
        whole = kind == 'xz' or osz <= S.SEG_BYTES
        nseg = 1 if whole else (osz + S.SEG_BYTES - 1) // S.SEG_BYTES
        sigs = {}
        ok = True
        for i in range(nseg):
            fn = '%s/%s_%d.pkl' % (S.SEG, md, i)
            if not os.path.exists(fn):
                ok = False
                break
            r = pickle.load(open(fn, 'rb'))
            for k, v in r['sigs'].items():
                e = sigs.setdefault(k, [0, v[2]])
                e[0] += v[0]
        if not ok:
            missing.append(t)
            continue
        per[t] = sigs
    ms1 = [t for t in per if m3a_read.plan_of(t)['bin'] == 'ms1']
    fs = [t for t in per if m3a_read.plan_of(t)['bin'] == 'fs15']
    fs_sigs = set()
    for t in fs:
        fs_sigs.update(per[t].keys())
    ms_sigs = collections.defaultdict(list)
    for t in ms1:
        for k, v in per[t].items():
            ms_sigs[k].append((t, v[0], v[1]))
    cand = sorted(k for k in ms_sigs if k not in base and k not in fs_sigs)
    lost = sorted(k for k in fs_sigs if k not in ms_sigs and k not in base)
    print('G7 agg: logs MS1 %d, FS15 %d, missing segments %s; F0 baseline %d; signatures MS1 %d, FS15 %d' % (
        len(ms1), len(fs), missing or 'none', len(base), len(ms_sigs), len(fs_sigs)))
    for k in cand:
        ex = ms_sigs[k]
        print('  CANDIDATE %s | tags %s | lines %d | example %s' % (
            k.decode('latin1')[:160], ' '.join(t for t, n, e in ex)[:200], sum(n for t, n, e in ex),
            ex[0][2].decode('utf-8', 'replace').strip()[:200] if isinstance(ex[0][2], bytes) else str(ex[0][2])[:200]))
    for k in lost:
        print('  FS15-ONLY (not in F0, not in MS1 logs; a row) %s' % k.decode('latin1')[:160])
    print('G7 candidates %d' % len(cand))
    return len(cand)


def cmd_grep():
    files = sorted(os.path.join(G, f) for f in os.listdir(G) if re.match(r'^(log|stdout)_m3_[a-z0-9_]+\.txt$', f))
    res = {}
    for side in ('ms1', 'fs15'):
        fl = [f for f in files if m3a_read.plan_of(re.sub(r'^(log|stdout)_', '', os.path.basename(f))[:-4])['bin'] == side]
        if not fl:
            print('G7 grep %s: no files' % side)
            res[side] = None
            continue
        r = subprocess.run([sys.executable, GREP] + fl, capture_output=True)
        txt = r.stdout.decode('utf-8', 'replace')
        open(os.path.join(OUT, 'grep_%s.out.txt' % side), 'w', encoding='utf-8', newline='\n').write(txt)
        hits = sum(int(v) for v in re.findall(r'	fatal=(\d+)', txt))
        res[side] = hits
        print('G7 grep %s: %d files, rc %d, output grep_%s.out.txt sha256 %s; last line: %s' % (
            side, len(fl), r.returncode, side, hashlib.sha256(r.stdout).hexdigest()[:16], (txt.strip().splitlines() or ['-'])[-1][:200]))
        print('G7 grep %s: fatal hits (sum of the theme rows) %d' % (side, hits))
    return res


def cmd_wit():
    rows = list(csv.DictReader(open(WIT, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    keys = sorted(set(r[list(r.keys())[2]].encode('utf-8') for r in rows))
    alt = re.compile(b'|'.join(re.escape(k) for k in sorted(keys, key=len, reverse=True)))
    lost_total = 0
    for L in ('sg', 'hb', 'mg', 'ac', 'f1', 'f2'):
        cnt = {}
        for t in ('m3_%s_v' % L, 'm3_%s_f' % L):
            p = os.path.join(G, 'log_%s.txt' % t)
            if not os.path.exists(p):
                cnt[t] = None
                continue
            c = collections.Counter()
            with open(p, 'rb') as f:
                for line in f:
                    if line.startswith(b'FrameTrace'):
                        continue
                    for m in alt.finditer(line):
                        c[m.group(0)] += 1
            cnt[t] = c
        a, b = cnt['m3_%s_v' % L], cnt['m3_%s_f' % L]
        if a is None or b is None:
            print('G7 wit %s: logs missing (MS1 %s, FS15 %s)' % (L, a is not None, b is not None))
            continue
        lost = sorted(k for k in b if k not in a)
        lost_total += len(lost)
        print('G7 wit %s: keys in FS15 %d, in MS1 %d, LOST %d %s' % (L, len(b), len(a), len(lost),
                                                                      [k.decode('utf-8', 'replace')[:60] for k in lost[:8]]))
    print('G7 witnesses lost %d' % lost_total)
    return lost_total


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
    print(__doc__.split('usage: ')[1])
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
