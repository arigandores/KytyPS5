# FSb (HPP-369): own reading of env knobs in git diff 4fc501f4 <commit> -- src/ (independent of knobs_fsa.py).
# Lists every +/- diff line with an environment read (getenv, EnvFlagOn, EnvValueOn, _wgetenv, GetEnvironmentVariable),
# a "KYTY_..." literal, a KNOB_DEFINITIONS row, or a gate/knob table row; for each name prints the default expression
# found at the reading line in the tip. Also lists removed reading lines (changed old readings).
import re, subprocess, sys, collections

C = sys.argv[1] if len(sys.argv) > 1 else '95eec776'
BASE = '4fc501f4'
G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
diff = subprocess.run([G, '-C', REPO, 'diff', '-U0', BASE, C, '--', 'src/'], capture_output=True).stdout.decode('utf-8', 'replace')
read_re = re.compile(r'getenv\s*\(|EnvFlagOn\s*\(|EnvValueOn\s*\(|GetEnvironmentVariable|_wgetenv|_dupenv_s')
name_re = re.compile(r'KYTY_[A-Z0-9_]+')
knobrow_re = re.compile(r'\{\s*"(KYTY_[A-Z0-9_]+)"\s*,\s*"([a-z0-9_]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*\}')
cur = None
newln = 0
added_reads, removed_reads = [], []
names = collections.defaultdict(lambda: {'+': [], '-': []})
for line in diff.split('\n'):
    if line.startswith('+++ b/'):
        cur = line[6:]
        continue
    if line.startswith('--- '):
        continue
    m = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
    if m:
        newln = int(m.group(1))
        continue
    if line.startswith('+'):
        body = line[1:]
        code = body.split('//')[0]
        if read_re.search(code):
            added_reads.append((cur, newln, body.strip()))
        for n in name_re.findall(body):
            names[n]['+'].append((cur, newln, '//' in body and body.find('//') < body.find(n)))
        newln += 1
    elif line.startswith('-'):
        body = line[1:]
        code = body.split('//')[0]
        if read_re.search(code):
            removed_reads.append((cur, body.strip()))
        for n in name_re.findall(body):
            names[n]['-'].append((cur, None, False))

print('added lines with an env read call (code part, comments stripped):', len(added_reads))
for f, n, b in added_reads:
    print('  +', f + ':' + str(n), b[:170])
print('removed lines with an env read call:', len(removed_reads))
for f, b in removed_reads:
    print('  -', f, b[:170])
print('KYTY_* names on +/- lines:', len(names))
for n in sorted(names):
    plus = names[n]['+']
    code_plus = [x for x in plus if not x[2]]
    print('  %-26s +%d (in code part %d) -%d' % (n, len(plus), len(code_plus), len(names[n]['-'])))
print('KNOB_DEFINITIONS rows added:')
for line in diff.split('\n'):
    if line.startswith('+'):
        for m in knobrow_re.finditer(line):
            print('  ', m.group(1), m.group(2), 'fallback', m.group(3), 'max', m.group(4))
print('KNOB_DEFINITIONS rows removed (changed old rows):')
for line in diff.split('\n'):
    if line.startswith('-'):
        for m in knobrow_re.finditer(line):
            print('  ', m.group(1), m.group(2), 'fallback', m.group(3), 'max', m.group(4))
