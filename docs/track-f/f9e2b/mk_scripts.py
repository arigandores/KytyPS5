# F9e2b: build_f9e2b.cmd and lockrun.sh as copies of the F9e2 scripts with the paths changed (backslashes: file, not heredoc).
BS = chr(92)
D = 'C:/kyty/f287/f9/'
b = open(D + 'f9e2/build_f9e2.cmd', encoding='utf-8').read().replace('\r\n', '\n')
old_wt = 'set "SRC=C:' + BS + 'kyty' + BS + 'f287' + BS + 'f9' + BS + 'f9e2' + BS + 'wt"'
old_bd = 'set "BUILD=C:' + BS + 'kyty' + BS + 'f287' + BS + 'f9' + BS + 'f9e2' + BS + 'build"'
assert b.count(old_wt) == 1 and b.count(old_bd) == 1
b = b.replace(old_wt, old_wt.replace('f9e2' + BS, 'f9e2b' + BS)).replace(old_bd, old_bd.replace('f9e2' + BS, 'f9e2b' + BS))
first = b.split('\n')[1]
assert first.startswith('rem F9e2 (HPP-426')
b = b.replace(first, 'rem F9e2b (HPP-429, ROADMAP s122 item 353(g)(4)): copy of the F9e2 build_f9e2.cmd with SRC/BUILD set to f9e2b. Was:' + '\n' + first, 1)
open(D + 'f9e2b/build_f9e2b.cmd', 'wb').write(b.replace('\n', '\r\n').encode('utf-8'))
l = open(D + 'f9e2/lockrun.sh', encoding='utf-8').read()
old_cmd = 'C:' + BS * 2 + 'kyty' + BS * 2 + 'f287' + BS * 2 + 'f9' + BS * 2 + 'f9e2' + BS * 2 + 'build_f9e2.cmd'
assert l.count(old_cmd) == 1, l.count(old_cmd)
l = l.replace(old_cmd, old_cmd.replace('f9e2' + BS * 2 + 'build_f9e2.cmd', 'f9e2b' + BS * 2 + 'build_f9e2b.cmd'))
l = l.replace('# F9e2 (copy of the P30b script)', '# F9e2b (copy of the F9e2 script, build script path changed)', 1)
open(D + 'f9e2b/lockrun.sh', 'wb').write(l.encode('utf-8'))
print('ok')
