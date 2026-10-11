# FS13b (HPP-788): default commit ea6c6e9e, expected ON set of item 697(g)(1): the FS12b set + KYTY_FIX_F25.
# FS13b (HPP-788, Red Team, ROADMAP s122 item 697(g)(2)): copy of the FS12b file with fs12b->fs13b, FS12b->FS13b, fs12n->fs13n in ALL lines (older header lines that say FS13b mean earlier links).
# FS13b (HPP-751, Red Team, ROADMAP s122 item 683(g)(2)): copy of the FS11b file with fs11b->fs13b, fs11n->fs13n, FS11b->FS13b in ALL lines (older header lines below that say FS13b mean FS11b HPP-715); default commits 730ed40a (FS12) / 9aaea58c (FS12 without FS12a).
# FS13b (HPP-715, Red Team, ROADMAP s122 item 647(d)(2)): copy of the FS10b file; fs10b -> fs13b, fs10n -> fs13n (paths, names, times label), default commits ee9632be / eded064e.
# FS10b (HPP-685, Red Team, ROADMAP s122 item 624(e)(2)): copy of the FS9b file; fs9b -> fs10b in code lines only (paths, names, times label);
# default commit dc5d4712, expected ON set of item 624(e)(1): the FS9b set + KYTY_FIX_B36.
# FS13b: default commit ee9632be, expected ON set of item 647(d)(1): the FS10b set + KYTY_FIX_B12.
# FS9b (HPP-672, Red Team): copy of my FS8b knobs_fs8b.py (HPP-572) - default commit 11164d72, expected ON set of item 604(d)(1): base set + KYTY_FIX_B13.
# FS8b (HPP-572, Red Team): copy of my FS7b knobs_fs7b.py (HPP-566) - default commit 302347b4, expected ON set of item 471(g)(1) with 487(g)(6): + KYTY_FIX_F19.
# FS7b (HPP-566, Red Team): copy of my FS6b knobs_fs6b.py (HPP-556) - default commit d6ee2dc8, expected ON set of items 467(g)(1), 487(g)(1): + KYTY_FIX_F8, KYTY_FIX_B24.
# FS6b (HPP-556, Red Team): port of my FS5b knobs_fs5b.py (default commit 3904522d, expected ON set of item 454(g)(1): + KYTY_S_PCW, KYTY_FIX_B4). Was:
# FS5b (HPP-510, Red Team): port of my FS4b knobs_fs4b.py by mk_fx_scripts_fs5b.py (default commit 0e72bc19, expected ON set + KYTY_FIX_F10, item 410(g)(1)). Was:
# FS4b (HPP-471, Red Team): port of my FS3b scanner to the FS4 worktree commit 0e72bc19 (independent of knobs_fs4a.py) +
# the expected ON set of ROADMAP s122 item 378(g)(1). Was:
# FS3b (HPP-448, Red Team): port of my FS2b scanner to the FS3 worktree commit d515b901 (independent of knobs_fs3a.py) +
# the expected ON set of ROADMAP s122 item 367(g)(1). Was:
# FS2b (HPP-382, Red Team): own reading of env knobs in git diff 4fc501f4 <commit> -- src/ (independent of knobs_fs2a.py;
# a port of knobs_fsb.py of FSb with the tip reading listed per name).
# (1) every +/- diff line with an environment read call or a "KYTY_..." literal; (2) KNOB_DEFINITIONS rows added/removed;
# (3) for every KYTY_* name on a code (non-comment) + line: the reading lines in the tip (git grep) with the 3 following lines,
#     and a default class decided by hand-checkable text rules:
#       ON-IF-UNSET  - the reading statement contains "== nullptr ||" (unset counts as on) followed by EnvValueOn in the same
#                      statement (up to the ';');
#       OFF-IF-UNSET - EnvFlagOn(name), or getenv compared to a literal, or "== nullptr" leading to a return / no stand;
#       TABLE        - KNOB_DEFINITIONS row (fallback column);
#     every class is printed with the statement so the reader checks it by eye.
import re, subprocess, sys, collections

C = sys.argv[1] if len(sys.argv) > 1 else 'ea6c6e9e'
BASE = '4fc501f4'
G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'


def git(*a):
    return subprocess.run([G, '-C', REPO] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')


diff = git('diff', '--ignore-cr-at-eol', '-U0', BASE, C, '--', 'src/')
read_re = re.compile(r'getenv\s*\(|EnvFlagOn\s*\(|EnvValueOn\s*\(|GetEnvironmentVariable|_wgetenv|_dupenv_s')
name_re = re.compile(r'KYTY_[A-Z0-9_]+')
knobrow_re = re.compile(r'\{\s*"(KYTY_[A-Z0-9_]+)"\s*,\s*"([a-z0-9_]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*\}')
cur = None
newln = 0
files = set()
added_reads, removed_reads = [], []
names = collections.defaultdict(lambda: {'+': [], '+code': [], '-': []})
plus = minus = 0
for line in diff.split('\n'):
    if line.startswith('+++ b/'):
        cur = line[6:]
        files.add(cur)
        continue
    if line.startswith('--- '):
        continue
    m = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
    if m:
        newln = int(m.group(1))
        continue
    if line.startswith('+'):
        plus += 1
        body = line[1:]
        code = body.split('//')[0]
        if read_re.search(code):
            added_reads.append((cur, newln, body.strip()))
        for n in name_re.findall(body):
            names[n]['+'].append((cur, newln))
        for n in name_re.findall(code):
            names[n]['+code'].append((cur, newln))
        newln += 1
    elif line.startswith('-'):
        minus += 1
        body = line[1:]
        code = body.split('//')[0]
        if read_re.search(code):
            removed_reads.append((cur, body.strip()))
        for n in name_re.findall(body):
            names[n]['-'].append((cur, None))

print('diff', BASE, C, '-- src/: files', len(files), '+%d -%d' % (plus, minus))
print('added lines with an env read call (code part):', len(added_reads))
for f, n, b in added_reads:
    print('  +', f + ':' + str(n), b[:170])
print('removed lines with an env read call:', len(removed_reads))
for f, b in removed_reads:
    print('  -', f, b[:170])
print('KYTY_* names on +/- lines:', len(names))
for n in sorted(names):
    print('  %-26s +%d (code %d) -%d' % (n, len(names[n]['+']), len(names[n]['+code']), len(names[n]['-'])))
rows_add, rows_rm = [], []
for line in diff.split('\n'):
    if line.startswith('+'):
        rows_add += knobrow_re.findall(line)
    elif line.startswith('-'):
        rows_rm += knobrow_re.findall(line)
print('KNOB_DEFINITIONS rows added:', len(rows_add))
for r in rows_add:
    print('   ', r[0], r[1], 'fallback', r[2], 'max', r[3])
print('KNOB_DEFINITIONS rows removed:', len(rows_rm))
for r in rows_rm:
    print('   ', r[0], r[1], 'fallback', r[2], 'max', r[3])

table = {r[0]: r for r in rows_add}
print()
print('per name: tip readings (code part, git grep -n at', C + ')')
classes = {}
for n in sorted(names):
    if not names[n]['+code']:
        print('==', n, ': only in comments on + lines')
        continue
    if n in table:
        classes[n] = 'TABLE fallback ' + table[n][2]
        print('==', n, ': KNOB_DEFINITIONS fallback', table[n][2])
        continue
    hits = git('grep', '-n', '-F', '"' + n + '"', C, '--', 'src/')
    cls = []
    for h in hits.strip().split('\n'):
        if not h:
            continue
        _, path, ln, text = h.split(':', 3)
        if '//' in text and text.find('//') < text.find(n):
            continue
        src = git('show', C + ':' + path).split('\n')
        i = int(ln) - 1
        stmt = ' '.join(s.strip() for s in src[i:i + 4])
        print('==', n, path + ':' + ln)
        for k in range(i, min(i + 4, len(src))):
            print('     ', k + 1, src[k].strip()[:160])
        if 'EnvFlagOn("' + n + '")' in text:
            cls.append('OFF-IF-UNSET (EnvFlagOn)')
        elif 'getenv("' + n + '")' in text:
            m = re.search(r'(?:const\s+)?char\s*\*\s*(\w+)\s*=\s*std::getenv', text)
            var = m.group(1) if m else None
            rest = ' '.join(s.strip() for s in src[i + 1:i + 4])
            st = rest.split(';')[0]
            if var and re.search(re.escape(var) + r'\s*==\s*nullptr\s*\|\|', st) and 'EnvValueOn(' + var in st.replace(' ', ''):
                cls.append('ON-IF-UNSET')
            elif var and re.search(re.escape(var) + r'\s*==\s*nullptr', rest):
                cls.append('OFF-IF-UNSET (nullptr -> exit)')
            elif var and re.search(re.escape(var) + r'\s*!=\s*nullptr\s*&&', rest):
                cls.append('OFF-IF-UNSET (!= nullptr &&)')
            else:
                cls.append('UNDECIDED')
        else:
            cls.append('NOT A READ (name use)')
    classes[n] = ', '.join(cls)
    print('   class:', classes[n])
print()
print('DEFAULT CLASS SUMMARY')
on = []
for n in sorted(classes):
    print('  %-26s %s' % (n, classes[n]))
    if 'ON-IF-UNSET' in classes[n] and 'OFF' not in classes[n]:
        on.append(n)
print('ON-IF-UNSET:', ' '.join(on))
und = [n for n in classes if 'UNDECIDED' in classes[n]]
print('UNDECIDED:', ' '.join(und) if und else 'none')
EXPECTED = {'KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE', 'KYTY_FIX_B9A', 'KYTY_FIX_B42', 'KYTY_FIX_SVAL', 'KYTY_FIX_F10', 'KYTY_S_PCW', 'KYTY_FIX_B4', 'KYTY_FIX_F8', 'KYTY_FIX_B24', 'KYTY_FIX_F19', 'KYTY_FIX_B13', 'KYTY_FIX_B36', 'KYTY_FIX_B12', 'KYTY_FIX_F21', 'KYTY_FIX_F25'}
ok = set(on) == EXPECTED and not und
print('ON-IF-UNSET == items 467(g)(1)+487(g)(1)+471(g)(1)+604(d)(1)+624(e)(1)+647(d)(1)+683(g)(1)+697(g)(1) set:', set(on) == EXPECTED, 'missing', sorted(EXPECTED - set(on)), 'extra', sorted(set(on) - EXPECTED))
print('KNOBS', 'ALL OK' if ok else 'CHECK BY HAND (UNDECIDED or set differs)')
