# FS5b (HPP-510, Red Team, ROADMAP s122 item 410(g)(2)): make my FS5b scripts as copies of my FS4b scripts with paths
# fs4/fs4b -> fs5/fs5b and the worktree commit 3d0e46da -> 0e72bc19 (FS5a worktree commit = 3d0e46da + 8a56dc2a + 0e72bc19);
# build_fs5b.cmd also gets the "target <name>" argument (shader_recompiler_compute_tests for the F12d GPU gate). LF output.
import io
S = 'C:/kyty/KytyPS5/docs/track-f/fs4b/'
D = 'C:/kyty/f287/fs5/fs5b/'
BS = chr(92)


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read().replace('\r\n', '\n')


def wr(p, t):
    open(p, 'wb').write(t.encode('utf-8'))
    print('wrote', p, len(t))


t = rd(S + 'mk_wt_fs4b.sh')
hdr = '# FS5b (HPP-510, Red Team, ROADMAP s122 item 410(g)(2)): own clean worktree on the FS5a worktree commit 0e72bc19 (3d0e46da + 8a56dc2a + 0e72bc19); copy of my FS4b script with WT and C changed. Was:\n'
assert t.count('WT=C:/kyty/f287/fs4/fs4b/wt') == 1 and t.count('C=3d0e46da') == 1
t = t.replace('WT=C:/kyty/f287/fs4/fs4b/wt', 'WT=C:/kyty/f287/fs5/fs5b/wt').replace('C=3d0e46da', 'C=0e72bc19')
t = t.replace('#!/bin/bash\n', '#!/bin/bash\n' + hdr, 1)
wr(D + 'mk_wt_fs5b.sh', t)

t = rd(S + 'build_fs4b.cmd')
a = 'fs4' + BS + 'fs4b'
print('build_fs4b.cmd occurrences of fs4\\fs4b:', t.count(a))
assert t.count(a) == 3
t = t.replace(a, 'fs5' + BS + 'fs5b')
t = t.replace('@echo off\n', '@echo off\nrem FS5b (HPP-510, Red Team): copy of my build_fs4b.cmd with SRC/BUILD set to fs5' + BS + 'fs5b and the "target <name>" argument of build_fs5a.cmd. Was:\n', 1)
anc = 'cmake --build "%BUILD%" --target kyty_emulator --parallel || exit /b 1\n'
assert t.count(anc) == 1
t = t.replace(anc, 'if "%1"=="target" (\n  cmake --build "%BUILD%" --target %2 --parallel || exit /b 1\n  echo BUILD OK: %BUILD%' + BS + '%2.exe\n  exit /b 0\n)\n' + anc)
wr(D + 'build_fs5b.cmd', t)

t = rd(S + 'lockrun.sh')
a = 'fs4' + BS + BS + 'fs4b' + BS + BS + 'build_fs4b.cmd'
assert t.count(a) == 1, t.count(a)
t = t.replace(a, 'fs5' + BS + BS + 'fs5b' + BS + BS + 'build_fs5b.cmd')
t = t.replace('#!/bin/bash\n', '#!/bin/bash\n# FS5b (HPP-510, Red Team): copy of my FS4b lockrun.sh with the build script path changed; passes a third argument (target name). Was:\n', 1)
anc = 'cmd //c "C:' + BS + BS + 'kyty' + BS + BS + 'f287' + BS + BS + 'fs5' + BS + BS + 'fs5b' + BS + BS + 'build_fs5b.cmd" $ARG > "$LOG" 2>&1 &'
assert t.count(anc) == 1
t = t.replace(anc, anc.replace('$ARG', '$ARG $3'))
wr(D + 'lockrun.sh', t)
print('ALL OK')
