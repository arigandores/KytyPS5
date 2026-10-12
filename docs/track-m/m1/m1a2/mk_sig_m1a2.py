"""M1a2 (HPP-837, ROADMAP p.756(b)(1)): build docs/track-m/m1/m1a2/signatures.tsv - our failure signature per site for the
30 FATAL and 18 RT themes of m1b/rc1_themes.tsv.
Input: agents/sig_a.tsv, sig_b.tsv, sig_c.tsv (site rows found by three read-only helper agents of this link; every row
re-checked here). Added columns:
  поток    - where the text goes: лог (EXIT*/Fail -> Log::WriteFatal, read by sweep_f48a: log_*.txt/_kyty*.txt), stderr /
             stdout (_run_stdout.txt of a run - NOT read by sweep_f48a), нет (no print on our side);
  в_логе   - for stderr/stdout rows: the companion line that does reach the log, with its place, or '-';
  ключ_свипа - does the printed log line that carries the signature match KEY of docs/track-f/f0/sweep_f0.py (the scanner
             sweep_f48a imports unchanged): да / нет; for stderr/stdout rows - the same for the companion line.
Checks (exit 1 on failure): every place b3dc9c67:<path>:<N> - line N == якорь and N+1 == якорь_плюс1 (whitespace-stripped);
every theme of the 48 FATAL/RT has >= 1 row; every non-'-' signature (without the print prefix 'Not implemented (' /
'condition (') is a substring of lines N-2..N+3 of our source. Prints ALL OK.
Usage: python mk_sig_m1a2.py   (writes signatures.tsv next to this file; read-only for git; exit 3 lock / 4 STOP)."""
import csv, os, re, subprocess, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP present - exit 4'); sys.exit(4)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
GIT = 'C:/Program Files/Git/cmd/git.exe' if os.path.exists('C:/Program Files/Git/cmd/git.exe') else 'git'
OURS = 'b3dc9c67'


def show(path):
    return subprocess.run([GIT, '-C', REPO, 'show', OURS + ':' + path], capture_output=True).stdout.decode(
        'utf-8', 'replace').split('\n')


src = open(os.path.join(REPO, 'docs/track-f/f0/sweep_f0.py'), encoding='utf-8').read()
m = re.search(r"^KEY = re\.compile\(\n(.*?)\)\n", src, re.S | re.M)
KEY = eval('re.compile(' + m.group(1) + ')', {'re': re})
rc1 = {r['тема']: r['вид'] for r in csv.DictReader(open(os.path.join(HERE, '..', 'm1b', 'rc1_themes.tsv'), encoding='utf-8'),
                                                   delimiter='\t', quoting=csv.QUOTE_NONE)}
need = sorted(t for t, v in rc1.items() if v in ('FATAL', 'RT'))
MAT = 'b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4064 «shader resource materialization failed hash=»'
DEP = 'b3dc9c67:src/graphics/host_gpu/renderer/depthRenderTarget.cpp:46 «unsupported render state; details were printed above»'
# Narrowed by the lead-free real negative control (grep_sig_m1a2.py on stdout_fs15_v: 16 lines 'Exception: code=0xe06d7363'
# - C++ exceptions of a clean run). 0xC00000FD = STATUS_STACK_OVERFLOW, the only failure of a deep PM4 chain on our tree.
OVERRIDE = {('T001', 'b3dc9c67:src/common/hostException.cpp:119'): (
    'Exception: code=0xc00000fd',
    'сигнатура сужена до кода переполнения стека: «Exception: code=» есть в чистом прогоне (C++-исключения 0xe06d7363)')}
rows, ok, cache = [], True, {}
for fn in ('sig_a.tsv', 'sig_b.tsv', 'sig_c.tsv'):
    for r in csv.DictReader(open(os.path.join(HERE, 'agents', fn), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
        mm = re.fullmatch(r'b3dc9c67:([^:]+):(\d+)', r['место'])
        p, n = mm.group(1), int(mm.group(2))
        if p not in cache:
            cache[p] = show(p)
        L = cache[p]
        if L[n - 1].strip() != r['якорь'].strip() or L[n].strip() != r['якорь_плюс1'].strip():
            ok = False
            print('FAIL anchor', r['тема'], r['место'])
        sig, kind = r['сигнатура'], r['вид_печати']
        note = r['примечание']
        if (r['тема'], r['место']) in OVERRIDE:
            sig, why = OVERRIDE[(r['тема'], r['место'])]
            note = note + ' [M1a2: ' + why + ']'
        bare = sig
        for pre in ('Not implemented (', 'condition ('):
            if bare.startswith(pre):
                bare = bare[len(pre):]
        if bare.endswith(') is true'):
            bare = bare[:-len(') is true')]
        if sig != '-' and (r['тема'], r['место']) not in OVERRIDE and bare not in '\n'.join(L[max(0, n - 3):n + 3]) and bare.strip() not in ' '.join(
                x.strip() for x in L[max(0, n - 3):n + 3]):
            ok = False
            print('FAIL signature not in source', r['тема'], r['место'], repr(sig))
        # stream
        if sig == '-':
            stream, comp = 'нет', '-'
        elif 'hostException.cpp' in p:
            stream, comp = 'stderr', '-'
        elif 'renderDraw.cpp' in p and kind == 'printf':
            stream, comp = 'stdout', '-'
        elif 'ResourceMaterialization.cpp' in p or 'SrtWalker.cpp' in p:
            stream, comp = 'stderr', MAT
        elif 'depthRenderTarget.cpp' in p and 'DepthFatal' in L[n - 1]:
            stream, comp = 'stderr', DEP
        else:
            stream, comp = 'лог', '-'
        if stream == 'лог':
            printed = {'EXIT_IF': 'Error: ' + ('' if sig.startswith('condition (') else 'condition (... '),
                       'EXIT_NOT_IMPLEMENTED': '' if sig.startswith('Not implemented (') else 'Not implemented (',
                       'Fail': 'shader resource tracking: hash=0x0 stage=X pc=0x0 '}.get(kind, '') + sig
            key = 'да' if KEY.search(printed.encode('utf-8')) else 'нет'
        elif comp != '-':
            key = 'да' if KEY.search(comp.split('«')[1].encode('utf-8')) else 'нет'
        else:
            key = '-'
        rows.append([r['тема'], rc1.get(r['тема'], '?'), r['sha'], r['место'], r['якорь'], r['якорь_плюс1'], sig, kind, stream,
                     comp, key, note])
have = {r[0] for r in rows}
miss = [t for t in need if t not in have]
extra = sorted(have - set(need))
if miss or extra:
    ok = False
    print('FAIL themes missing', miss, 'extra', extra)
rows.sort(key=lambda r: (r[0], r[3]))
with open(os.path.join(HERE, 'signatures.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\t'.join(['тема', 'вид', 'sha', 'место', 'якорь', 'якорь_плюс1', 'сигнатура', 'печать', 'поток', 'в_логе',
                       'ключ_свипа', 'примечание']) + '\n')
    for r in rows:
        assert not any('\t' in x or '\n' in x for x in r)
        f.write('\t'.join(r) + '\n')
from collections import Counter
print('rows', len(rows), 'themes', len(have), 'of', len(need))
print('stream', dict(Counter(r[8] for r in rows)), 'sweep key', dict(Counter(r[10] for r in rows)))
printed_themes = {r[0] for r in rows if r[6] != '-'}
print('themes with a printed signature', len(printed_themes), 'without:', sorted(set(need) - printed_themes))
log_themes = {r[0] for r in rows if (r[8] == 'лог' and r[10] == 'да') or (r[8] == 'stderr' and r[9] != '-' and r[10] == 'да')}
print('themes whose failure puts a KEY-matching line into the swept log', len(log_themes), 'not:',
      sorted(set(need) - log_themes))
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
