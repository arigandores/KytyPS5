"""F14a: edit 2 of f14a_corpus.py (Write, not heredoc): (a) the compare opcode of each manual site is counted
(OpFOrd*/OpFUnordNotEqual name), (b) for every manual row the summary says whether the same (stage, hash) has a native row
(another permutation = another runtime specialization of the same program)."""
p = 'C:/kyty/f287/f14a/f14a_corpus.py'
s = open(p, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)


rep("OP_FCMP = {180, 183, 184, 186, 188, 190, 181, 182, 185, 187, 189, 191}",
    "OP_FCMP = {180, 183, 184, 186, 188, 190, 181, 182, 185, 187, 189, 191}\n"
    "FCMP_NAME = {180: 'FOrdEqual', 181: 'FUnordEqual', 182: 'FOrdNotEqual', 183: 'FUnordNotEqual', 184: 'FOrdLessThan',\n"
    "             185: 'FUnordLessThan', 186: 'FOrdGreaterThan', 187: 'FUnordGreaterThan', 188: 'FOrdLessThanEqual',\n"
    "             189: 'FUnordLessThanEqual', 190: 'FOrdGreaterThanEqual', 191: 'FUnordGreaterThanEqual'}")
rep("            fcmp[w[1]] = (w[2], w[3])", "            fcmp[w[1]] = (w[2], w[3], op)")
rep("    manual = 0\n    sel = []", "    manual = 0\n    kinds = {}\n    sel = []")
rep("        if x in extract and extract[x] in sample_res:\n            manual += 1\n    return native, manual",
    "        if x in extract and extract[x] in sample_res:\n            manual += 1\n"
    "            k = FCMP_NAME[fcmp[w[2]][2]]\n            kinds[k] = kinds.get(k, 0) + 1\n    return native, manual, kinds")
rep("    native, manual = analyse(p)", "    native, manual, kinds = analyse(p)")
rep("                     'manual': manual})", "                     'manual': manual, 'kinds': ','.join('%s:%d' % kv for kv in sorted(kinds.items()))})")
rep("    cols = ['stage', 'id', 'hash16', 'native', 'native_ops', 'manual']",
    "    cols = ['stage', 'id', 'hash16', 'native', 'native_ops', 'manual', 'kinds']")
rep("for s in man_rows:\n    g = gcn_by_hash",
    "nat_keys = {(s['stage'], s['hash16']) for s in nat_rows}\n"
    "man_keys = {(s['stage'], s['hash16']) for s in man_rows}\n"
    "allk = {}\n"
    "for s in man_rows:\n"
    "    for kv in s['kinds'].split(','):\n"
    "        if kv:\n"
    "            k, v = kv.split(':')\n"
    "            allk[k] = allk.get(k, 0) + int(v)\n"
    "out.append('  manual programs (stage, hash): %d (CS %d, PS %d); of them with a native permutation too: %d; native programs: %d; '\n"
    "           'compare ops of manual sites: %s' % (len(man_keys), sum(1 for k in man_keys if k[0] == 'cs'),\n"
    "           sum(1 for k in man_keys if k[0] == 'ps'), len(man_keys & nat_keys), len(nat_keys),\n"
    "           ', '.join('%s %d' % kv for kv in sorted(allk.items()))))\n"
    "for s in man_rows:\n    g = gcn_by_hash")
rep("    out.append('    manual row: %s %s manual %d native %d gcn %s scenes %s' % (s['stage'], s['id'], s['manual'], s['native'],\n"
    "               g.get('compare_ops', '?'), g.get('scenes', '?')))",
    "    out.append('    manual row: %s %s manual %d (%s) native-sibling %s gcn %s scenes %s' % (s['stage'], s['id'], s['manual'],\n"
    "               s['kinds'], 'yes' if (s['stage'], s['hash16']) in nat_keys else 'no',\n"
    "               g.get('compare_ops', '?'), g.get('scenes', '?')))")
open(p, 'wb').write(s.encode('utf-8'))
print('patched')
