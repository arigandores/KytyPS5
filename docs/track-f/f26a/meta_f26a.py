# F20a (HPP-551, item 451(e)): the tag json of every log of list_f20a.tsv -> meta_f20a.jsonl (one JSON line per log):
#   path, size, json (path or '-'), json_form, binary_sha256, validation (cmdline '--vulkan-validation' value), rd ('--rd' in
#   the cmdline), shader_validation, guest_args, env (dict of the env of the json, values kept), cmd_extra (cmdline items
#   that are not in the base set of the shipped launcher line), attempts-form note.
# A log 'log_<tag>_a<k>.txt' (the per-attempt copy of enter_scene.py) takes the json of <tag>.
# Prints the census of env keys and of binaries.  Usage: python meta_f20a.py <list.tsv> <out.jsonl>
import collections, json, lzma, os, re, sys

lst, out = sys.argv[1], sys.argv[2]
TAB = chr(9)
rows = [l.rstrip(chr(10)).split(TAB) for l in open(lst, encoding='utf-8') if l.strip()]
BASE = {'--screen-width', '--screen-height', '--user-name', '--user-id', '--present-mode', '--vblank-frequency',
        '--console-language', '--vulkan-validation', '--shader-validation', '--shader-optimization-type',
        '--shader-log-direction', '--shader-log-folder', '--command-buffer-dump', '--command-buffer-dump-folder',
        '--printf-direction', '--printf-output-file', '--spirv-debug-printf', '--game'}


def load(p):
    if p.endswith('.xz'):
        return json.loads(lzma.open(p, 'rt', encoding='utf-8').read())
    return json.load(open(p, encoding='utf-8'))


def find_json(path, js):
    if js != '-':
        return js
    d, f = path.rsplit('/', 1)
    if f.startswith('log_'):
        tag = f[4:].split('.txt')[0]
        m = re.fullmatch(r'(.*)_a\d+', tag)
        if m:
            for c in (d + '/' + m.group(1) + '.json', d + '/' + m.group(1) + '.json.xz'):
                if os.path.isfile(c):
                    return c
    return '-'


envc = collections.Counter()
binc = collections.Counter()
forms = collections.Counter()
recs = []
for path, size, mt, root, js in rows:
    rec = {'path': path, 'size': int(size), 'mtime': int(mt), 'root': root, 'json': '-', 'json_form': 'none',
           'binary_sha256': None, 'validation': None, 'rd': None, 'shader_validation': None, 'guest_args': None,
           'env': None, 'cmd_extra': None, 'attempt_copy': False}
    j = find_json(path, js.split(';')[0] if js != '-' else '-')
    if j != js.split(';')[0]:
        rec['attempt_copy'] = True
    if j != '-':
        rec['json'] = j
        try:
            d = load(j)
        except Exception as e:
            rec['json_form'] = 'unreadable: %s' % type(e).__name__
            d = None
        if isinstance(d, dict):
            keys = sorted(k for k in ('binary_sha256', 'cmdline', 'env') if k in d)
            rec['json_form'] = '+'.join(keys) or 'other:' + ','.join(sorted(d)[:6])
            rec['binary_sha256'] = d.get('binary_sha256')
            cl = d.get('cmdline')
            if isinstance(cl, list):
                cl = [str(x) for x in cl]
                def val(k):
                    # the LAST occurrence wins (enter_scene.py appends '--emu-arg' pairs after the base line)
                    if k not in cl:
                        return None
                    i = len(cl) - 1 - cl[::-1].index(k)
                    return cl[i + 1] if i + 1 < len(cl) else None
                rec['validation'] = val('--vulkan-validation')
                rec['shader_validation'] = val('--shader-validation')
                rec['rd'] = '--rd' in cl
                extra = []
                i = 1
                while i < len(cl):
                    if cl[i] in BASE:
                        i += 2
                        continue
                    extra.append(cl[i])
                    i += 1
                rec['cmd_extra'] = extra
            env = d.get('env')
            if isinstance(env, dict):
                rec['env'] = {str(k): str(v) for k, v in env.items()}
                rec['guest_args'] = env.get('KYTY_GUEST_ARGS')
                for k in env:
                    envc[k] += 1
    binc[(rec['binary_sha256'] or 'none')[:8]] += 1
    forms[rec['json_form']] += 1
    recs.append(rec)
with open(out, 'w', encoding='utf-8', newline=chr(10)) as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=True, sort_keys=True) + chr(10))
print('logs', len(recs), 'json forms', dict(forms))
print('binaries', binc.most_common())
print('validation', collections.Counter(str(r['validation']) for r in recs).most_common())
print('rd', collections.Counter(str(r['rd']) for r in recs).most_common())
print('cmd_extra', collections.Counter(' '.join(r['cmd_extra'] or []) for r in recs).most_common(20))
print('env keys', len(envc))
for k, v in sorted(envc.items()):
    vals = collections.Counter(r['env'][k] for r in recs if r['env'] and k in r['env'])
    print('  %s %d: %s' % (k, v, '; '.join('%s x%d' % (a[:60], b) for a, b in vals.most_common(6))))
