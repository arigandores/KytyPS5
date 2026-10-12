# M1b: independent member p.752(g)(3) check. For each shipped knob: files of OUR commits that mention the knob in the
# message (6a2987a7..b3dc9c67, src/ only) vs files listed in M1a evidence/knobs.md; then upstream themes touching the
# extra files (incl. rename sources) and whether M1a section 6.2 has a line for that theme.
import subprocess, re, collections, csv
BASE, OUR = '6a2987a7', 'b3dc9c67'
UP = 'dad900c61d6c7ff8aefc9e666ca7c3de4bbf4176'
D = 'docs/track-m/m1/'
def git(*a):
    return subprocess.run(['git', *a], capture_output=True, check=True).stdout.decode('utf-8', 'replace')
knobs_md = open(D + 'evidence/knobs.md', encoding='utf-8').read()
knob_files = {}
for line in knobs_md.split('\n'):
    m = re.match(r'\| `(KYTY_[A-Z0-9_]+)` \|', line)
    if m:
        knob_files[m.group(1)] = set(re.findall(r'`(src/[^`]+)`', line.split('|')[-2]))
up_files = collections.defaultdict(set)  # upstream theme -> files (with rename sources)
tsv = {r['sha']: r['тема'] for r in csv.DictReader(open(D + 'upstream.tsv', encoding='utf-8', newline=''), delimiter='\t', quoting=csv.QUOTE_NONE)}
for full in git('rev-list', '--no-merges', f'6a2987a7..{UP}').split():
    t = next((v for k, v in tsv.items() if full.startswith(k)), None)
    for l in git('diff-tree', '--no-commit-id', '-r', '-M', '--name-status', full).split('\n'):
        parts = l.split('\t')
        if len(parts) >= 2:
            for p in parts[1:]:
                up_files[t].add(p)
md = open(D + 'upstream.md', encoding='utf-8').read()
s62 = md[md.find('### 6.2'):md.find('## 7.')]
total_extra = 0
for k, kf in sorted(knob_files.items()):
    shas = git('log', '--format=%H', f'--grep={k}', f'{BASE}..{OUR}').split()
    mine = set()
    for s in shas:
        for f in git('diff-tree', '--no-commit-id', '--name-only', '-r', s).split('\n'):
            if f.startswith('src/'):
                mine.add(f)
    extra = sorted(mine - kf)
    hits = []
    for f in extra:
        for t, fs in up_files.items():
            if f in fs:
                hits.append((t, f))
    themes = sorted(set(t for t, _ in hits))
    unc = [t for t in themes if not re.search(r'\b' + t + r'\b[^\n]*' + k, s62)]
    total_extra += len(themes)
    print(f'{k}: our-commits {len(shas)}, src files by commits {len(mine)}, in knobs.md {len(kf)}, extra {len(extra)}; '
          f'upstream themes on extra files {len(themes)}; of them without a 6.2 line naming {k}: {len(unc)}')
    for t in unc[:40]:
        fs = sorted(f for tt, f in hits if tt == t)
        print(f'   {t}: {", ".join(fs[:4])}')
