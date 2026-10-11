"""F40a (HPP-770): identity of the tag binary of the F40a worktree (ROADMAP s122 item 692(g)(2)); copy of binary_f38a.py.
Prints sha256 of both, the counts of fixed byte strings in the tag binary and in the installed FS12 copy (the knob, the
FixF25 lines, the translation signature 9177b426..., the version string), and the worktree facts: HEAD, src/ diff vs
730ed40a (files), git cherry of the worktree commits against main. Usage: binary_f38a.py"""
import hashlib
import re
import subprocess

G = 'C:/Program Files/Git/cmd/git.exe'
WT = 'C:/kyty/f287/f40a/wt'
TAG = 'C:/kyty/f287/f40a/build/install/kyty_emulator.exe'
FS12 = 'C:/kyty/f287/bin/kyty_emulator_46892c20.exe'
STRINGS = [b'KYTY_FIX_F24', b'FixF24: mode=', b'FixF24: init tid=', b'FixF24: pump_stop_expired', b'FixF24: pump_update_long',
           b'FixF24: open failed', b'FixF24: add event', b'FixF24: wait error', b'TestHidLoss: f24 mode=', b'KYTY_TEST_HIDLOSS',
           b'KYTY_FIX_F21', b'FixF21: mode=', b'FixB24: mode=', b'9177b4267de1fb8bac7d1113afd8733210addfac']


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def git(*a):
    return subprocess.run([G, '-C', WT] + list(a), capture_output=True).stdout.decode('utf-8').strip()


def main():
    tag = open(TAG, 'rb').read()
    fs12 = open(FS12, 'rb').read()
    print('tag   %s sha256 %s size %d' % (TAG, sha(TAG), len(tag)))
    print('fs12  %s sha256 %s' % (FS12, sha(FS12)))
    for s in STRINGS:
        print('count %-45s tag %d fs12 %d' % (s.decode(), tag.count(s), fs12.count(s)))
    for name, data in (('tag', tag), ('fs12', fs12)):
        vers = sorted(set(m.group(0).decode() for m in re.finditer(rb'KytyPS5-\d{4}-\d\d-\d\d-[0-9a-f]+-\d+-g[0-9a-f]+', data)))
        print('version %s %s' % (name, vers))
    print('worktree HEAD %s' % git('rev-parse', 'HEAD'))
    print('worktree src/ diff vs 730ed40a: %s' % git('diff', '--name-only', '730ed40a', '--', 'src').replace('\n', ', '))
    print('worktree status lines %d' % len([x for x in git('status', '--short', '--ignore-submodules=all').split('\n') if x]))
    print('git cherry main HEAD (worktree commits after 730ed40a):')
    for line in git('cherry', '-v', 'main', 'HEAD').split('\n'):
        if line and git('merge-base', '--is-ancestor', '730ed40a', line.split()[1]) == '' and \
                subprocess.run([G, '-C', WT, 'merge-base', '--is-ancestor', line.split()[1], '730ed40a']).returncode != 0:
            print('  ' + line[:110])


if __name__ == '__main__':
    main()
