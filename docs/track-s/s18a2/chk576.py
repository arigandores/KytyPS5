"""S18a2 (HPP-650, ROADMAP s122 item 576(g)(4)): members of the S18a2 cherry-pick.
  (1) git patch-id --stable of the commit in main = of the cherry-pick (whole commit and code paths);
  (2) git diff <main commit> <S18a2 HEAD> on the src/tests paths of the 7 S18a commits and of the S18a2 commit - each line
      a line added by 381aa80a, 1d8d9aa6 or 9bd96f44 (the 24 foreign lines of item 571(b)(4)), count printed, 24 expected;
      main has no other code commit between fe4b227a and the S18a2 commit (printed);
  (3) K1(7) diff 302347b4..<S18a2 HEAD> on the paths of the signature list (K17 of chk571.py) empty;
  (4) the S18a2 HEAD parent is 62ff7b5b, its tree differs from 62ff7b5b only by the paths of the S18a2 commit.
ASCII output. Usage: python chk576.py <main commit> <S18a2 HEAD>
"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
CODE = ['src', 'tests', 'CMakeLists.txt']
FOREIGN3 = ['381aa80a', '1d8d9aa6', '9bd96f44']
S18A = ['283a6ef9', '29542308', 'a2fee0d9', '9635cb0f', '9238a182', '5bd93ea1', 'fe4b227a']
K17 = ['src/graphics/shader', 'CMakeLists.txt', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
       'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h',
       'src/graphics/host_gpu/renderer/image/imageInfo.h']
NL = chr(10)


def git(*a, inp=None):
    p = subprocess.run([GIT, '-C', REPO] + list(a), input=inp, capture_output=True)
    if p.returncode != 0:
        raise SystemExit('git failed: %s %s' % (a, p.stderr.decode('utf-8', 'replace')))
    return p.stdout


def pid(c, paths=None):
    out = git('patch-id', '--stable', inp=git(*(['show', c] + (['--'] + paths if paths else []))))
    return out.decode('ascii').split(' ')[0] if out else '-'


def parse(raw):
    files, cur = {}, None
    for line in raw.decode('utf-8').split(NL):
        if line.startswith('diff --git '):
            cur = line.split(' b/', 1)[1]
            files[cur] = {'plus': [], 'minus': []}
            continue
        if cur is None or line.startswith('+++ ') or line.startswith('--- '):
            continue
        if line.startswith('+'):
            files[cur]['plus'].append(line[1:])
        elif line.startswith('-'):
            files[cur]['minus'].append(line[1:])
    return files


def main():
    main_c, head = sys.argv[1], sys.argv[2]
    main_c = git('rev-parse', main_c).decode().strip()
    head = git('rev-parse', head).decode().strip()
    ok = True
    a_all, b_all = pid(main_c), pid(head)
    a_code, b_code = pid(main_c, CODE), pid(head, CODE)
    v = a_all == b_all and a_code == b_code
    print('== (1) patch-id --stable main %s / S18a2 %s: all %s / %s, code %s / %s -> %s' % (
        main_c[:8], head[:8], a_all, b_all, a_code, b_code, 'OK' if v else 'FAIL'))
    ok &= v
    other = git('log', '--format=%h %s', 'fe4b227a..%s^' % main_c, '--', *CODE).decode().strip()
    print('== main code commits between fe4b227a and %s: %s' % (main_c[:8], other if other else 'NONE'))
    ok &= not other
    paths = sorted({p for c in S18A + [main_c] for p in
                    git('show', '--format=', '--name-only', c, '--', 'src', 'tests').decode().split(NL) if p})
    foreign = set()
    for c in FOREIGN3:
        for f in parse(git('show', '--format=', c)).values():
            foreign.update(f['plus'])
    d = parse(git('diff', main_c, head, '--', *paths))
    n, bad = 0, 0
    print('== (2) git diff %s %s on %d paths: %s' % (main_c[:8], head[:8], len(paths), ' '.join(paths)))
    for f in sorted(d):
        for sign, key in (('-', 'minus'), ('+', 'plus')):
            for l in d[f][key]:
                n += 1
                tag = 'F' if l in foreign else '?'
                bad += tag == '?'
                print('  %s %s %s |%s' % (f, sign, tag, l))
    print('  lines %d, not lines of 381aa80a/1d8d9aa6/9bd96f44: %d -> %s' % (n, bad, 'OK' if n == 24 and bad == 0 else 'FAIL'))
    ok &= n == 24 and bad == 0
    k = git('diff', '--stat', '302347b4', head, '--', *K17).decode()
    print('== (3) K1(7) diff --stat 302347b4..%s: %s' % (head[:8], 'EMPTY' if not k.strip() else k))
    ok &= not k.strip()
    parent = git('rev-parse', head + '^').decode().strip()
    changed = sorted(p for p in git('diff', '--name-only', parent, head).decode().split(NL) if p)
    mine = sorted(p for p in git('show', '--format=', '--name-only', main_c).decode().split(NL) if p)
    v = parent.startswith('62ff7b5b') and changed == mine
    print('== (4) parent %s, paths changed %s = paths of %s -> %s' % (parent[:8], changed, main_c[:8], 'OK' if v else 'FAIL'))
    ok &= v
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
