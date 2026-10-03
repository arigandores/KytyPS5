# FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): mk_wt_fs4a.sh, build_fs4a.cmd and lockrun.sh as copies of the FS3a
# scripts with the paths changed (backslashes: file, not heredoc). mk_wt_fs4a.sh: a clean detached worktree on the FS3
# worktree commit d515b901 (= 722c5e7f + cherry-pick 4e72289e, the code of the installed FS3 540c035a) + cherry-pick of
# the F10c commit 68602c4f; the FS4a commit is cherry-picked later, after the main commit. lockrun.sh - the FS3a one
# (540 s step limit, exit 6, the step is rerun).
BS = chr(92)
NL = chr(10)
S = 'C:/kyty/f287/fs3/fs3a/'
D = 'C:/kyty/f287/fs4/fs4a/'

b = open(S + 'build_fs3a.cmd', encoding='utf-8').read().replace('\r\n', '\n')
old_wt = 'set "SRC=C:' + BS + 'kyty' + BS + 'f287' + BS + 'fs3' + BS + 'fs3a' + BS + 'wt"'
old_bd = 'set "BUILD=C:' + BS + 'kyty' + BS + 'f287' + BS + 'fs3' + BS + 'fs3a' + BS + 'build"'
assert b.count(old_wt) == 1 and b.count(old_bd) == 1
new_wt = 'set "SRC=C:' + BS + 'kyty' + BS + 'f287' + BS + 'fs4' + BS + 'fs4a' + BS + 'wt"'
new_bd = 'set "BUILD=C:' + BS + 'kyty' + BS + 'f287' + BS + 'fs4' + BS + 'fs4a' + BS + 'build"'
b = b.replace(old_wt, new_wt).replace(old_bd, new_bd)
first = b.split(NL)[1]
assert first.startswith('rem FS3a (HPP-447')
b = b.replace(first, 'rem FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): copy of build_fs3a.cmd with SRC/BUILD set to fs4' + BS + 'fs4a. Was:' + NL + first, 1)
open(D + 'build_fs4a.cmd', 'wb').write(b.replace(NL, '\r\n').encode('utf-8'))

l = open(S + 'lockrun.sh', encoding='utf-8').read().replace('\r\n', '\n')
old_cmd = 'C:' + BS * 2 + 'kyty' + BS * 2 + 'f287' + BS * 2 + 'fs3' + BS * 2 + 'fs3a' + BS * 2 + 'build_fs3a.cmd'
assert l.count(old_cmd) == 1, l.count(old_cmd)
new_cmd = 'C:' + BS * 2 + 'kyty' + BS * 2 + 'f287' + BS * 2 + 'fs4' + BS * 2 + 'fs4a' + BS * 2 + 'build_fs4a.cmd'
l = l.replace(old_cmd, new_cmd)
old_h = '# FS3a (copy of the F9e2c script, build script path changed, 540 s step limit - exit 6, rerun the step). Was:'
assert l.count(old_h) == 1
l = l.replace(old_h, '# FS4a (copy of the FS3a script, build script path changed). Was:' + NL + old_h, 1)
open(D + 'lockrun.sh', 'wb').write(l.encode('utf-8'))

m = open(S + 'mk_wt_fs3a.sh', encoding='utf-8').read().replace('\r\n', '\n')
old_wtp = 'WT=C:/kyty/f287/fs3/fs3a/wt'
assert m.count(old_wtp) == 1
m = m.replace(old_wtp, 'WT=C:/kyty/f287/fs4/fs4a/wt')
old_c = 'C=722c5e7f' + NL
assert m.count(old_c) == 1
m = m.replace(old_c, 'C=d515b901' + NL)
old_log = '"$G" -C $WT log -4 '
assert m.count(old_log) == 1
cp = NL.join([
    'echo "--- cherry-pick F10c 68602c4f"',
    '"$G" -C $WT -c user.name="Emu Engineer" -c user.email=emu-engineer@agents.invalid cherry-pick 68602c4f',
    '']) + NL
m = m.replace(old_log, cp + '"$G" -C $WT log -6 ', 1)
old_hdr = '# FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): copy of mk_wt_f9e2c.sh on the F9e2c worktree commit 722c5e7f, no cherry-pick'
assert m.count(old_hdr) == 1
m = m.replace(old_hdr,
              '# FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): copy of mk_wt_fs3a.sh on the FS3 worktree commit d515b901 + cherry-pick of' + NL +
              '# the F10c commit 68602c4f (the FS4a commit is cherry-picked after the main commit). Was:' + NL + old_hdr, 1)
assert 'C=d515b901' in m and 'cherry-pick 68602c4f' in m
open(D + 'mk_wt_fs4a.sh', 'wb').write(m.encode('utf-8'))
print('ok')
