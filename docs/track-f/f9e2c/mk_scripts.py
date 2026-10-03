# F9e2c: mk_wt_f9e2c.sh, build_f9e2c.cmd and lockrun.sh as copies of the F9e2b scripts with the paths changed
# (backslashes: file, not heredoc); mk_wt additionally cherry-picks the F9e2b worktree commit 0cbaa644.
BS = chr(92)
NL = chr(10)
D = 'C:/kyty/f287/f9/'

b = open(D + 'f9e2b/build_f9e2b.cmd', encoding='utf-8').read().replace('\r\n', '\n')
old_wt = 'set "SRC=C:' + BS + 'kyty' + BS + 'f287' + BS + 'f9' + BS + 'f9e2b' + BS + 'wt"'
old_bd = 'set "BUILD=C:' + BS + 'kyty' + BS + 'f287' + BS + 'f9' + BS + 'f9e2b' + BS + 'build"'
assert b.count(old_wt) == 1 and b.count(old_bd) == 1
b = b.replace(old_wt, old_wt.replace('f9e2b' + BS, 'f9e2c' + BS)).replace(old_bd, old_bd.replace('f9e2b' + BS, 'f9e2c' + BS))
first = b.split(NL)[1]
assert first.startswith('rem F9e2b (HPP-429')
b = b.replace(first, 'rem F9e2c (HPP-436, ROADMAP s122 item 357(g)(4)): copy of build_f9e2b.cmd with SRC/BUILD set to f9e2c. Was:' + NL + first, 1)
open(D + 'f9e2c/build_f9e2c.cmd', 'wb').write(b.replace(NL, '\r\n').encode('utf-8'))

l = open(D + 'f9e2b/lockrun.sh', encoding='utf-8').read()
old_cmd = 'C:' + BS * 2 + 'kyty' + BS * 2 + 'f287' + BS * 2 + 'f9' + BS * 2 + 'f9e2b' + BS * 2 + 'build_f9e2b.cmd'
assert l.count(old_cmd) == 1, l.count(old_cmd)
l = l.replace(old_cmd, old_cmd.replace('f9e2b' + BS * 2 + 'build_f9e2b.cmd', 'f9e2c' + BS * 2 + 'build_f9e2c.cmd'))
old_h = '# F9e2b (copy of the F9e2 script, build script path changed)'
assert l.count(old_h) == 1
l = l.replace(old_h, '# F9e2c (copy of the F9e2b script, build script path changed)', 1)
open(D + 'f9e2c/lockrun.sh', 'wb').write(l.encode('utf-8'))

m = open(D + 'f9e2b/mk_wt_f9e2b.sh', encoding='utf-8').read()
old_wtp = 'WT=C:/kyty/f287/f9/f9e2b/wt'
assert m.count(old_wtp) == 1
m = m.replace(old_wtp, 'WT=C:/kyty/f287/f9/f9e2c/wt')
old_cp = '"$G" -C $WT -c core.autocrlf=false cherry-pick 23a0b3f2' + NL
assert m.count(old_cp) == 1
m = m.replace(old_cp, old_cp + 'echo "--- cherry-pick F9e2b worktree commit 0cbaa644"' + NL +
              '"$G" -C $WT -c core.autocrlf=false cherry-pick 0cbaa644' + NL, 1)
old_log = '"$G" -C $WT log -2 '
assert m.count(old_log) == 1
m = m.replace(old_log, '"$G" -C $WT log -3 ')
m = m.replace('# F9e2b (HPP-429, ROADMAP s122 item 353(g)(4)): clean detached worktree on 4414e235 (P23 code) + the F9e2 commit 23a0b3f2',
              '# F9e2c (HPP-436, ROADMAP s122 item 357(g)(4)): copy of mk_wt_f9e2b.sh + cherry-pick of the F9e2b worktree commit 0cbaa644.' + NL +
              '# Was: F9e2b (HPP-429, ROADMAP s122 item 353(g)(4)): clean detached worktree on 4414e235 (P23 code) + the F9e2 commit 23a0b3f2', 1)
assert 'F9e2c (HPP-436' in m
open(D + 'f9e2c/mk_wt_f9e2c.sh', 'wb').write(m.encode('utf-8'))
print('ok')
