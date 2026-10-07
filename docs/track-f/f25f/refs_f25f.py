"""F25f (HPP-669): every '<commit>:<path>:<line>' reference of the seal body with its anchor and +1 control (general rule 24(1)): the
anchor must be a substring of the line, the +1 text a substring of the next line.  The table is written below (ROWS) and printed into
refs_f25f.tsv.  --neg corrupts every anchor (its last character) - every reference must then fail.  ASCII output; ends with ALL OK /
FAILED (NEG CONTROL OK with --neg).
usage: python refs_f25f.py [--neg]"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GIT = 'C:/Program Files/Git/cmd/git.exe'
ROWS = [
    ('47d618fe', 'docs/ROADMAP.md', 23586, '596. **\u0417\u0432\u0435\u043d\u043e F25b \u0442\u0440\u0435\u043a\u0430 F (`HPP-661`',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F25a'),
    ('47d618fe', 'docs/ROADMAP.md', 23600, '599. **\u0417\u0432\u0435\u043d\u043e F25c \u0442\u0440\u0435\u043a\u0430 F (`HPP-666`',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F25c'),
    ('47d618fe', 'docs/ROADMAP.md', 23617, '600. **\u0417\u0432\u0435\u043d\u043e F25d \u0442\u0440\u0435\u043a\u0430 F (`HPP-667`',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F25d'),
    ('47d618fe', 'docs/ROADMAP.md', 23634, '602. **\u0417\u0432\u0435\u043d\u043e F25e \u0442\u0440\u0435\u043a\u0430 F (`HPP-668`, Red Team',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F25e'),
    ('24ce64ea', 'docs/track-f/f20l3/go_f20l3.sh', 55,
     'MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData" "GLCache=$GLDIR")',
     '[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }'),
    ('35b454c6', 'src/common/diagB32.cpp', 643,
     '" cover_us=%llu flip_ns=%llu\\n", // F25d (items 596(v) C4, 599(b)(11) C6): flip_ns - the FrameStats::NowNs scale, last',
     'n, static_cast<unsigned long long>(r.dt_us), static_cast<unsigned long long>(r.instr_us), r.gaps.samples,'),
    ('35b454c6', 'src/common/diagB32.cpp', 723,
     '" ring_hold=%llu ring_hold_w=%llu hist_exh=%llu hist_exh_w=%llu w_cut_w=%llu others_cut_w=%llu\\n",',
     'n, static_cast<unsigned long long>(counters->slots), static_cast<unsigned long long>(counters->slot_full),'),
    ('35b454c6', 'src/graphics/presentation/videoOut.cpp', 1293, 'Common::DiagB32::OnFlip(r.cfg->flip_status.count, r.id, r.reserve_host_ns);', '}'),
    ('35b454c6', 'src/graphics/presentation/videoOut.cpp', 1442, 'LOGF("FrameTrace: n=%" PRIu64 " dt_us=%llu lat_us=%llu gpu_proc=%llu gpu_idle=%llu"',
     '" gpu_blocked=%llu submits=%llu submit_us=%llu semwaits=%llu semwait_us=%llu"'),
    ('0005e11f', 'src/graphics/host_gpu/renderer/masterSemaphore.cpp', 128, 'EXIT("GPU stopped completing submissions\\n");', '}'),
    ('0005e11f', 'src/common/assert.cpp', 40, 'Log::WriteFatal(BuildFatalReport("--- Error ---", text, file, line));', 'return 1;'),
]


def main(argv):
    neg = '--neg' in argv
    tsv = os.path.join(HERE, 'refs_f25f.tsv')
    with open(tsv, 'w', encoding='utf-8', newline='\n') as f:
        for c, p, ln, a, n in ROWS:
            f.write('%s\t%s\t%d\t%s\t%s\n' % (c, p, ln, a, n))
    print('suite refs_f25f.py sha256 %s%s' % (hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
                                             ' (negative control)' if neg else ''))
    bad = 0
    cache = {}
    for c, p, ln, anc, nxt in ROWS:
        if (c, p) not in cache:
            cache[(c, p)] = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (c, p)],
                                           capture_output=True).stdout.decode('utf-8').split('\n')
        L = cache[(c, p)]
        a = anc[:-1] + ('#' if anc[-1] != '#' else '@') if neg else anc
        line = L[ln - 1] if ln - 1 < len(L) else ''
        nl = L[ln] if ln < len(L) else ''
        good = a in line and nxt in nl
        bad += 0 if good else 1
        print('%s %s:%s:%d' % ('ok' if good else 'MISMATCH', c, p, ln))
    print('refs %d mismatches %d' % (len(ROWS), bad))
    if neg:
        print('NEG CONTROL OK' if bad == len(ROWS) else 'NEG CONTROL FAILED')
        return 0 if bad == len(ROWS) else 1
    print('ALL OK' if bad == 0 else 'FAILED')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
