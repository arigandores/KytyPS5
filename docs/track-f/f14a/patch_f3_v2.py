"""F14a: edit 2 of f14a_f3.py (written by Write, not a heredoc): positive control - count every
'CsPretranslate: miss|hit hash=' line of each log (any hash), the number of distinct levels per group, and a check of
translation-cache file names (cs_<hash16>_*.bin) for the target hashes in the cache trees named in CACHE_TREES."""
p = 'C:/kyty/f287/f14a/f14a_f3.py'
s = open(p, 'rb').read().decode('utf-8').replace('\r\n', '\n')
NL = chr(92) + 'n'


def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)


rep("f.write(b'shader CFG build failed" + NL + "CsPretranslate: summary" + NL + "Level has started: " + NL + "')",
    "f.write(b'shader CFG build failed" + NL + "CsPretranslate: summary" + NL + "Level has started: " + NL +
    "CsPretranslate: miss hash=" + NL + "CsPretranslate: hit hash=" + NL + "')")
rep("    n = 0\n    for line in grep_lines", "    n = 0\n    all_normal = 0\n    for line in grep_lines")
rep("        if b'CsPretranslate: summary' in body:\n",
    "        if b'CsPretranslate: miss hash=' in body or b'CsPretranslate: hit hash=' in body:\n"
    "            all_normal += 1\n"
    "        if b'CsPretranslate: summary' in body:\n")
rep("'normal_hashes': len(normal),", "'normal_hashes': len(normal), 'all_normal': all_normal,")
rep("cols = ['log', 'level', 'skipped_total', 'restrack', 'budget', 'normal_lines',",
    "cols = ['log', 'level', 'skipped_total', 'restrack', 'budget', 'all_normal', 'normal_lines',")
rep("    cf = sum(per_log[p]['cfg_fail_outside'] for p in ps)\n",
    "    cf = sum(per_log[p]['cfg_fail_outside'] for p in ps)\n"
    "    an = sum(per_log[p]['all_normal'] for p in ps)\n"
    "    lv = len({per_log[p]['level'] for p in ps if per_log[p]['level']})\n")
rep("normal-path miss/hit lines with these hashes %d; '",
    "levels %d; control: miss/hit lines of any hash %d (logs with >= 1: %d); normal-path miss/hit lines with these hashes %d; '")
rep("% (g, len(ps), dict(prof), nl, cf))",
    "% (g, len(ps), dict(prof), lv, an, sum(1 for p in ps if per_log[p]['all_normal']), nl, cf))")
# cache trees: file names only (os.walk, nothing is read)
rep("text = '\\n'.join(out) + '\\n'\nopen(OUT + '/f14a_f3_summary",
    "CACHE_TREES = ['C:/kyty/KytyPS5/ps5 em/_ShaderCache', 'C:/kyty/s288/s7/cache_root', 'C:/kyty/s288/snap0']\n"
    "for tree in CACHE_TREES:\n"
    "    names = 0\n"
    "    found = []\n"
    "    for d, _, fs in os.walk(tree):\n"
    "        for fn in fs:\n"
    "            names += 1\n"
    "            parts = fn.split('_')\n"
    "            if len(parts) >= 2 and parts[1].encode() in target:\n"
    "                found.append(os.path.join(d, fn).replace(chr(92), '/'))\n"
    "    out.append('cache tree %s: file names %d; files of target hashes %d %s' % (tree, names, len(found), ' '.join(found[:10])))\n"
    "text = '\\n'.join(out) + '\\n'\nopen(OUT + '/f14a_f3_summary")
open(p, 'wb').write(s.encode('utf-8'))
print('patched')
