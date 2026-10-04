# F15a: copies of the F14a worktree and build scripts with the paths set to f15a (LF, write_bytes).
F = 'C:/kyty/KytyPS5/docs/track-f/f14a/'
D = 'C:/kyty/f287/f15a/'
bs = chr(92)

sh = open(F + 'mk_wt_f14a.sh', 'rb').read().decode('utf-8').replace('\r\n', '\n')
lines = sh.split('\n')
assert lines[1].startswith('# F14a (HPP-487, ROADMAP s122 item 395(g)): clean detached worktree'), lines[1]
lines[1:4] = ['# F15a (HPP-491, ROADMAP s122 item 400(d)(2)): clean detached worktree on the current main for the B4 stand -',
              '# copy of docs/track-f/f14a/mk_wt_f14a.sh with the path changed (f14a -> f15a); the rest as F14a/F11d.']
sh = '\n'.join(lines)
assert sh.count('WT=C:/kyty/f287/f14a/wt') == 1 and sh.count('mk_wt_f14a.sh <commit>') == 1
sh = sh.replace('WT=C:/kyty/f287/f14a/wt', 'WT=C:/kyty/f287/f15a/wt').replace('mk_wt_f14a.sh <commit>', 'mk_wt_f15a.sh <commit>')
assert 'f14a' not in sh.split('\n', 3)[3].replace('docs/track-f/f14a/mk_wt_f14a.sh', ''), 'f14a left'
open(D + 'mk_wt_f15a.sh', 'wb').write(sh.encode('utf-8'))

raw = open(F + 'build_f14a.cmd', 'rb').read()
crlf = b'\r\n' in raw
cmd = raw.decode('utf-8').replace('\r\n', '\n')
lines = cmd.split('\n')
assert lines[1].startswith('rem F14a (HPP-487'), lines[1]
lines[1] = 'rem F15a (HPP-491, ROADMAP s122 item 400(d)(2)): copy of docs/track-f/f14a/build_f14a.cmd with SRC/BUILD set to f15a'
cmd = '\n'.join(lines)
old_src = 'C:' + bs + 'kyty' + bs + 'f287' + bs + 'f14a' + bs
new_src = 'C:' + bs + 'kyty' + bs + 'f287' + bs + 'f15a' + bs
assert cmd.count(old_src) == 2
cmd = cmd.replace(old_src, new_src).replace('F14a builds only test targets', 'F15a builds only test targets')
cmd = cmd.replace('build_f14a.cmd [configure]', 'build_f15a.cmd [configure]')
assert 'f14a' not in cmd.replace('docs/track-f/f14a/build_f14a.cmd', '')
open(D + 'build_f15a.cmd', 'wb').write((cmd.replace('\n', '\r\n') if crlf else cmd).encode('utf-8'))
print('COPIES OK crlf', crlf)
