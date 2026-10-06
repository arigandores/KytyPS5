"""S18a (HPP-642, ROADMAP s122 item 571(b)): members of the patch-id check of the S18a cherry-picks.
Input: C:/kyty/s288/s18a/picked.tsv (order, source, picked, conflict resolution) written by w2.sh.
Per commit: git patch-id --stable of the source and of the pick, whole commit and code paths (src tests CMakeLists.txt).
Readings of item 571(b):
  283a6ef9, 9635cb0f - per file the multisets of + and - lines equal the source, and each context difference is checked:
      lines in the source context missing in the pick - each must be a line added by 381aa80a or 1d8d9aa6 (F16d, S16d,
      absent from FS8a); lines in the pick context missing in the source - printed with the check that each is a line of
      the source commit's post-image of the same file (the 3-line window moved over the removed foreign lines; reading
      of the executor, printed). Extra: git diff <source> <pick> on the files of the commit - only '-' lines, each a line
      added by 381aa80a or 1d8d9aa6.
  29542308 - patch-id of the code paths equal; README (docs) blob = the blob of the source commit.
  the others - patch-id of the whole commit equal.
(b)(4): git diff <default commit> <HEAD> on the src/tests paths of the 7 commits - each line a line added by 381aa80a,
1d8d9aa6 or 9bd96f44, count printed; K1(7) diff 302347b4..HEAD empty.
ASCII output. Usage: python chk571.py <default commit> <out tsv>
"""
import collections
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
CODE = ['src', 'tests', 'CMakeLists.txt']
FOREIGN = ['381aa80a', '1d8d9aa6']
FOREIGN3 = FOREIGN + ['9bd96f44']
K17 = ['src/graphics/shader', 'CMakeLists.txt', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
       'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h',
       'src/graphics/host_gpu/renderer/image/imageInfo.h']
NL = chr(10)
TAB = chr(9)


def git(*a, inp=None):
    p = subprocess.run([GIT, '-C', REPO] + list(a), input=inp, capture_output=True)
    if p.returncode != 0:
        raise SystemExit('git failed: %s %s' % (a, p.stderr.decode('utf-8', 'replace')))
    return p.stdout


def show(c, paths=None):
    args = ['show', '--format=', c]
    if paths:
        args += ['--'] + paths
    return git(*args)


def pid(c, paths=None):
    out = git('patch-id', '--stable', inp=git(*(['show', c] + (['--'] + paths if paths else []))))
    return out.decode('ascii').split(' ')[0] if out else '-'


def parse(raw):
    files = {}
    cur = None
    for line in raw.decode('utf-8').split(NL):
        if line.startswith('diff --git '):
            cur = line.split(' b/', 1)[1]
            files[cur] = {'plus': [], 'minus': [], 'ctx': []}
            continue
        if cur is None or line.startswith('+++ ') or line.startswith('--- '):
            continue
        if line.startswith('+'):
            files[cur]['plus'].append(line[1:])
        elif line.startswith('-'):
            files[cur]['minus'].append(line[1:])
        elif line.startswith(' '):
            files[cur]['ctx'].append(line[1:])
    return files


def added_lines(commits):
    s = set()
    for c in commits:
        for f in parse(show(c)).values():
            s.update(f['plus'])
    return s


def main():
    default, out_tsv = sys.argv[1], sys.argv[2]
    rows = [l.split(TAB) for l in open('C:/kyty/s288/s18a/picked.tsv', encoding='ascii').read().split(NL) if l.strip()]
    foreign = added_lines(FOREIGN)
    foreign3 = added_lines(FOREIGN3)
    ok = True
    table = [['order', 'source', 'picked', 'resolution', 'pid_src_all', 'pid_pick_all', 'eq_all', 'pid_src_code',
              'pid_pick_code', 'eq_code', 'member_571b', 'verdict']]
    for n, src, pick, res in rows:
        n = int(n)
        a_all, b_all = pid(src), pid(pick)
        a_code, b_code = pid(src, CODE), pid(pick, CODE)
        s8 = src[:8]
        print('== %d %s -> %s (%s)' % (n, s8, pick[:8], res or 'none'))
        if s8 in ('283a6ef9', '9635cb0f'):
            member = 'plus_minus_multiset+context'
            fa, fb = parse(show(src)), parse(show(pick))
            v = set(fa) == set(fb)
            if not v:
                print('  file sets differ', sorted(set(fa) ^ set(fb)))
            for f in sorted(set(fa) & set(fb)):
                eq_pm = (collections.Counter(fa[f]['plus']) == collections.Counter(fb[f]['plus']) and
                         collections.Counter(fa[f]['minus']) == collections.Counter(fb[f]['minus']))
                ordered = fa[f]['plus'] == fb[f]['plus'] and fa[f]['minus'] == fb[f]['minus']
                v &= eq_pm
                ca, cb = collections.Counter(fa[f]['ctx']), collections.Counter(fb[f]['ctx'])
                only_src = ca - cb
                only_pick = cb - ca
                if not only_src and not only_pick:
                    print('  %s: +%d -%d multiset equal %s ordered equal %s; context identical' % (
                        f, len(fa[f]['plus']), len(fa[f]['minus']), eq_pm, ordered))
                    continue
                post = set(git('show', '%s:%s' % (src, f)).decode('utf-8').split(NL))
                bad_src = [l for l in only_src.elements() if l not in foreign]
                bad_pick = [l for l in only_pick.elements() if l not in post]
                v &= not bad_src and not bad_pick
                print('  %s: +%d -%d multiset equal %s ordered equal %s; context only in source %d (lines of 381aa80a/1d8d9aa6: %d), only in pick %d (lines of the source post-image: %d)' % (
                    f, len(fa[f]['plus']), len(fa[f]['minus']), eq_pm, ordered, sum(only_src.values()),
                    sum(only_src.values()) - len(bad_src), sum(only_pick.values()), sum(only_pick.values()) - len(bad_pick)))
                for l in only_src.elements():
                    print('    ctx source-only %s |%s' % ('F' if l in foreign else '?', l))
                for l in only_pick.elements():
                    print('    ctx pick-only   %s |%s' % ('P' if l in post else '?', l))
                d = parse(git('diff', src, pick, '--', f)).get(f, {'plus': [], 'minus': []})
                bad_d = [l for l in d['minus'] if l not in foreign] + d['plus']
                v &= not bad_d
                print('    git diff %s %s -- %s: - %d (lines of 381aa80a/1d8d9aa6: %d), + %d' % (
                    s8, pick[:8], f, len(d['minus']), len(d['minus']) - len([l for l in d['minus'] if l not in foreign]), len(d['plus'])))
                for l in d['minus']:
                    print('      - %s |%s' % ('F' if l in foreign else '?', l))
                for l in d['plus']:
                    print('      + ? |%s' % l)
        elif s8 == '29542308':
            member = 'pid_code+docs_blob'
            v = a_code == b_code
            for f in parse(show(src)):
                if f.startswith('docs/'):
                    ba = git('rev-parse', '%s:%s' % (src, f)).strip()
                    bb = git('rev-parse', '%s:%s' % (pick, f)).strip()
                    print('  %s blob source %s pick %s equal %s' % (f, ba.decode()[:12], bb.decode()[:12], ba == bb))
                    v &= ba == bb
        else:
            member = 'pid_all'
            v = a_all == b_all
        print('  patch-id all %s / %s  code %s / %s  member %s -> %s' % (a_all[:12], b_all[:12], a_code[:12], b_code[:12], member, 'OK' if v else 'FAIL'))
        ok &= v
        table.append([str(n), src, pick, res or 'none', a_all, b_all, 'yes' if a_all == b_all else 'no', a_code, b_code,
                      'yes' if a_code == b_code else 'no', member, 'OK' if v else 'FAIL'])
    head = rows[-1][2]
    paths = sorted({p for r in rows for p in git('show', '--format=', '--name-only', r[1], '--', 'src', 'tests').decode().split(NL) if p})
    d = parse(git('diff', default, head, '--', *paths))
    n24 = 0
    bad = 0
    print('== (b)(4) git diff %s %s on the src/tests paths of the 7 commits (%d paths)' % (default[:8], head[:8], len(paths)))
    for f in sorted(d):
        for sign, key in (('-', 'minus'), ('+', 'plus')):
            for l in d[f][key]:
                n24 += 1
                tag = 'F' if l in foreign3 else '?'
                bad += tag == '?'
                print('  %s %s %s |%s' % (f, sign, tag, l))
    print('  lines %d, not lines of 381aa80a/1d8d9aa6/9bd96f44: %d' % (n24, bad))
    ok &= n24 == 24 and bad == 0
    k = git('diff', '--stat', '302347b4', head, '--', *K17).decode()
    print('== K1(7) diff --stat 302347b4..%s: %s' % (head[:8], 'EMPTY' if not k.strip() else k))
    ok &= not k.strip()
    with open(out_tsv, 'w', encoding='ascii', newline=NL) as fo:
        for r in table:
            fo.write(TAB.join(r) + NL)
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
