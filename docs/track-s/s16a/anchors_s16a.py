# S16a (HPP-605): checks every `5fc57612:<path>:<line>` reference of docs/track-s/s16a-design.md - the backticked anchor must be
# in that line and the "+1" text in the next line of the file at commit 5fc57612 (fragments split on the ellipsis). Run from
# the KytyPS5 repository root: python docs/track-s/s16a/anchors_s16a.py docs/track-s/s16a-design.md
import re, subprocess, sys

txt = open(sys.argv[1], encoding='utf-8').read()
C = '5fc57612'
src = {}

def line(path, n):
    if path not in src:
        src[path] = subprocess.run(['git', 'show', C + ':' + path], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
    return src[path][n - 1]

bad = 0
n = 0
ok = set()
for m in re.finditer(r'5fc57612:([\w./]+):(\d+)`?\s*(?:\((?:якорь\s*)?)?`([^`]+)`;\s*\+1\s*`([^`]+)`', txt):
    ok.add(m.start())
    path, ln, a, b = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    n += 1
    for fs, text in ((a, line(path, ln)), (b, line(path, ln + 1))):
        frags = [x.strip() for x in fs.replace(chr(92) + '|', '|').split('…') if x.strip()]
        norm = ' '.join(text.split())
        if not all(' '.join(f.split()) in norm for f in frags):
            bad += 1
            print('MISMATCH', path, ln, fs)
refs = [m.start() for m in re.finditer(r'5fc57612:[\w./]+:\d+', txt)]
print('refs', len(refs), 'anchored', n, 'unanchored', len([x for x in refs if x not in ok]), 'bad', bad)
print('ANCHORS ALL OK' if bad == 0 and n == len(refs) else 'ANCHORS CHECK FAILED')
