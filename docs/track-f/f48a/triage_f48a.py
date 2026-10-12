# F48a (HPP-830): triage of the F48a delta-sweep signatures that are new against F0 (new_f32a.tsv of the F48a sweep).
# Rules = docs/track-f/f32a/triage_f32a.py RULES (imported unchanged, first) + the F48a rules below (each with its source [c]).
# A signature that is also in the F32a sweep table (sig_f32a.tsv of F32a or F32d) is marked SEEN_F32 in the output (it was
# triaged by F32a / F32d); every signature still gets exactly one class; an unclassified one fails the run.
# Usage: python triage_f48a.py <new_f32a.tsv> <out.tsv> [<f32a sig.tsv> ...]   (prints counts, NEW_VS_F32 list, ALL OK)
import os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'f32a'))
import triage_f32a as T  # noqa: E402

TAB = chr(9)
NL = chr(10)
RULES48 = [
    # stand KYTY_TEST_HIDLOSS (Ph24, F40c; src/graphics/presentation/window/window.cpp test stand print)
    ('INSTR', 'stand KYTY_TEST_HIDLOSS result line (F40c tags f24_*)', r'^TestHidLoss: '),
    # stand KYTY_TEST_EXITFATAL (Ph21, F33): config line and the injected fatal (EXIT_IF(g_inject.load()), src/emulator.cpp)
    ('INSTR', 'stand KYTY_TEST_EXITFATAL config (F33a/F33c/F33d runs)', r'^ExitFatal: config '),
    ('INSTR', 'stand KYTY_TEST_EXITFATAL injected fatal (emulator.cpp EXIT_IF g_inject / g_arm; stand worktrees)',
     r'^Error: condition \((g_inject\.load\(\)|g_arm == Arm::CN)\) is true in '),
    # test-runner summaries of the FS13a / FS14a ship links (known socket failure 'guest PEEK and WAITALL', F15c / F15d / F38a)
    ('INSTR', 'test-runner summary line (shader_cfg_tests, kernel_file_system_tests)', r'^OK   (tX shader_cfg_tests|kernel_file_system_tests) '),
    ('INSTR', 'stand f29_fault_stand result line (F44, FS14a)', r'^\[X\] lines overflow = min'),
    # KYTY_STREAM_TRACE=1 (src/kernel/fileSystem.cpp StreamTraceEnd) - set by the F47i harness go_f47i.sh; asset names contain 'crash'
    ('INSTR', 'KYTY_STREAM_TRACE=1 print (F47i form); asset names contain the key word', r'^StreamRead: #X '),
    # KYTY_FIX_F24 open failure: in the delta only in the mutant m1 log (F40b2 review: 'only at m1')
    ('INSTR', 'KYTY_FIX_F24 open failure of the mutant m1 (log_f24_m1, binary 3bc5305)', r'^FixFX: open failed index=X '),
    # host tool output in a harness build log (not an emulator log)
    ('TOOL', 'host tool error in a harness build log (fs15a/runs/log_mk_wt.txt)', r'^<X>WSL \(X - Relay\) ERROR'),
]


def load_seen(paths):
    s = set()
    for p in paths:
        for i, l in enumerate(open(p, encoding='utf-8')):
            if i:
                s.add(l.rstrip(NL).split(TAB)[8])
    return s


def classify(sig, ex):
    for c, note, rx in T.RULES + RULES48:
        if re.search(rx, sig):
            if c == 'FIXTURE' and not T.FXPATH.search(ex.replace(chr(92), '/')):
                return ('BAD', 'FIXTURE OUTSIDE FIXTURE PATH')
            return (c, note)
    return None


def main():
    src, out = sys.argv[1], sys.argv[2]
    seen = load_seen(sys.argv[3:])
    rows = open(src, encoding='utf-8').read().splitlines()
    hdr = rows[0].split(TAB)
    iS, iEx, iL, iB = hdr.index('signature'), hdr.index('example_path:line'), hdr.index('logs'), hdr.index('builds')
    res, bad = [], []
    cnt = collections.Counter()
    cnt_new = collections.Counter()
    for l in rows[1:]:
        x = l.split(TAB)
        sig, ex = x[iS], x[iEx]
        hit = classify(sig, ex)
        if hit is None or hit[0] == 'BAD':
            bad.append(('UNCLASSIFIED ' if hit is None else hit[1] + ' ') + sig[:120])
            continue
        tag = 'SEEN_F32' if sig in seen else 'NEW_VS_F32'
        cnt[hit[0]] += 1
        if tag == 'NEW_VS_F32':
            cnt_new[hit[0]] += 1
        res.append([hit[0], hit[1], tag, x[iL], x[iB], ex, sig])
    with open(out, 'w', encoding='utf-8', newline=NL) as o:
        o.write(TAB.join(['class', 'row_or_note', 'vs_f32', 'logs', 'builds', 'example_path:line', 'signature']) + NL)
        for r in res:
            o.write(TAB.join(r) + NL)
    print('signatures new vs F0', len(rows) - 1, 'classified', len(res), dict(sorted(cnt.items())))
    print('of them not in F32a / F32d sweep tables', sum(cnt_new.values()), dict(sorted(cnt_new.items())))
    k14 = [r for r in res if r[0] not in ('ROW', 'ROW_K5', 'FIXTURE', 'INSTR', 'GUEST', 'FS', 'ARGS', 'TOOL')]
    print('new K1-K4 rows proposed by the triage:', len(k14))
    for b in bad:
        print(b)
    ok = not bad and len(res) == len(rows) - 1
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
