# FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): mk_wt_fs3a.sh, build_fs3a.cmd and lockrun.sh as copies of the F9e2c
# scripts with the paths changed (backslashes: file, not heredoc). mk_wt_fs3a.sh: a clean detached worktree on the F9e2c
# worktree commit 722c5e7f (= 4414e235 + F9e2 + F9e2b + F9e2c), submodules as P23; the FS3a commit is cherry-picked
# later. lockrun.sh additionally stops its step after 540 s (exit 6, the step is rerun - ninja is incremental), so no
# process outlives a tool call.
BS = chr(92)
NL = chr(10)
S = 'C:/kyty/f287/f9/f9e2c/'
D = 'C:/kyty/f287/fs3/fs3a/'

b = open(S + 'build_f9e2c.cmd', encoding='utf-8').read().replace('\r\n', '\n')
old_wt = 'set "SRC=C:' + BS + 'kyty' + BS + 'f287' + BS + 'f9' + BS + 'f9e2c' + BS + 'wt"'
old_bd = 'set "BUILD=C:' + BS + 'kyty' + BS + 'f287' + BS + 'f9' + BS + 'f9e2c' + BS + 'build"'
assert b.count(old_wt) == 1 and b.count(old_bd) == 1
new_wt = 'set "SRC=C:' + BS + 'kyty' + BS + 'f287' + BS + 'fs3' + BS + 'fs3a' + BS + 'wt"'
new_bd = 'set "BUILD=C:' + BS + 'kyty' + BS + 'f287' + BS + 'fs3' + BS + 'fs3a' + BS + 'build"'
b = b.replace(old_wt, new_wt).replace(old_bd, new_bd)
first = b.split(NL)[1]
assert first.startswith('rem F9e2c (HPP-436')
b = b.replace(first, 'rem FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): copy of build_f9e2c.cmd with SRC/BUILD set to fs3\\fs3a. Was:'.replace('\\\\', BS) + NL + first, 1)
open(D + 'build_fs3a.cmd', 'wb').write(b.replace(NL, '\r\n').encode('utf-8'))

l = open(S + 'lockrun.sh', encoding='utf-8').read().replace('\r\n', '\n')
old_cmd = 'C:' + BS * 2 + 'kyty' + BS * 2 + 'f287' + BS * 2 + 'f9' + BS * 2 + 'f9e2c' + BS * 2 + 'build_f9e2c.cmd'
assert l.count(old_cmd) == 1, l.count(old_cmd)
new_cmd = 'C:' + BS * 2 + 'kyty' + BS * 2 + 'f287' + BS * 2 + 'fs3' + BS * 2 + 'fs3a' + BS * 2 + 'build_fs3a.cmd'
l = l.replace(old_cmd, new_cmd)
old_h = '# F9e2c (copy of the F9e2b script, build script path changed)'
assert l.count(old_h) == 1
l = l.replace(old_h, '# FS3a (copy of the F9e2c script, build script path changed, 540 s step limit - exit 6, rerun the step). Was:' + NL + old_h, 1)
old_loop = 'while kill -0 $PID 2>/dev/null; do' + NL
assert l.count(old_loop) == 1
l = l.replace(old_loop, 'T0=$(date +%s)' + NL + old_loop + NL.join([
    '\tif [ $(( $(date +%s) - T0 )) -ge 540 ]; then',
    '\t\ttaskkill //T //F //PID $WINPID > /dev/null 2>&1',
    '\t\twait $PID',
    '\t\techo "STOPPED: 540 s step limit $(date -u +%Y-%m-%dT%H:%M:%SZ)"',
    '\t\texit 6',
    '\tfi']) + NL, 1)
open(D + 'lockrun.sh', 'wb').write(l.encode('utf-8'))

m = open(S + 'mk_wt_f9e2c.sh', encoding='utf-8').read().replace('\r\n', '\n')
old_wtp = 'WT=C:/kyty/f287/f9/f9e2c/wt'
assert m.count(old_wtp) == 1
m = m.replace(old_wtp, 'WT=C:/kyty/f287/fs3/fs3a/wt')
old_c = 'C=4414e235' + NL
assert m.count(old_c) == 1
m = m.replace(old_c, 'C=722c5e7f' + NL)
# no cherry-picks here: 722c5e7f already carries F9e2 / F9e2b / F9e2c
i = m.index('echo "--- cherry-pick F9e2 23a0b3f2"')
j = m.index('"$G" -C $WT log -3 ')
m = m[:i] + m[j:]
m = m.replace('"$G" -C $WT log -3 ', '"$G" -C $WT log -4 ')
m = m.replace('# F9e2c (HPP-436, ROADMAP s122 item 357(g)(4)): copy of mk_wt_f9e2b.sh + cherry-pick of the F9e2b worktree commit 0cbaa644.',
              '# FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): copy of mk_wt_f9e2c.sh on the F9e2c worktree commit 722c5e7f, no cherry-pick' + NL +
              '# (the FS3a commit is cherry-picked after the main commit). Was:' + NL +
              '# F9e2c (HPP-436, ROADMAP s122 item 357(g)(4)): copy of mk_wt_f9e2b.sh + cherry-pick of the F9e2b worktree commit 0cbaa644.', 1)
assert 'FS3a (HPP-447' in m and 'cherry-pick 0cbaa644' not in m and 'cherry-pick 23a0b3f2' not in m
open(D + 'mk_wt_fs3a.sh', 'wb').write(m.encode('utf-8'))
print('ok')
