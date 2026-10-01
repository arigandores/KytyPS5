"""Link 1b (HPP-321): Part B helpers of test_sc143.py for item 242 (e) (json level, the enter_scene end line of times.txt),
the seal path 02, nested sealed names.  Each replacement must hit exactly once.  LF kept."""
p = 'C:/kyty/s143/test_sc143.py'
t = open(p, 'rb').read().decode('utf-8')
reps = [
    ("    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=310.0 if is_w else 330.0, hold_exit=None, ft_tail=300,\n"
     "             pipeline_cache_off=False)",
     "    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=310.0 if is_w else 330.0, hold_exit=None, ft_tail=300,\n"
     "             pipeline_cache_off=False, level=S.level_of(tag))"),
    ("    if log:\n        (root / ('log_%s.txt' % tag)).write_bytes(('\\n'.join(lines) + '\\n').encode('utf-8'))\n"
     "    (root / ('stdout_%s.txt' % tag)).write_bytes(b'\\n')",
     "    if log:\n        (root / ('log_%s.txt' % tag)).write_bytes(('\\n'.join(lines) + '\\n').encode('utf-8'))\n"
     "        (root / 'step2').mkdir(exist_ok=True)\n"
     "        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:\n"
     "            f.write('2026-10-01T00:00:00Z %s %s enter_scene end rc 0 log_%s.txt sha256 %s\\n' % (\n"
     "                chain, tag, tag, _h.sha256((root / ('log_%s.txt' % tag)).read_bytes()).hexdigest()))\n"
     "    (root / ('stdout_%s.txt' % tag)).write_bytes(b'\\n')"),
    ("           S.PRED_PATH == 'C:/kyty/s143/pred/01_sc143.md' and S.CHAIN == 'go143a'",
     "           S.PRED_PATH == 'C:/kyty/s143/pred/02_sc143.md' and S.CHAIN == 'go143a'"),
    ("    elif name != 'sc143.py':\n        (rs / name).write_bytes(('fixture ' + name).encode())",
     "    elif name != 'sc143.py':\n        (rs / name).parent.mkdir(parents=True, exist_ok=True)\n"
     "        (rs / name).write_bytes(('fixture ' + name).encode())"),
    ("[x for x in b2 if x.startswith('  FAIL')] == ['  FAIL W made ()', '  FAIL V v143_02 and W w143_02 are the pair of '\n"
     "                                                         'one level (guest args -lvl booster_construction in both) '\n"
     "                                                         '(-lvl booster_construction / None)']",
     "[x.split(' (')[0] for x in b2 if x.startswith('  FAIL')] == ['  FAIL W made', '  FAIL V v143_02 and W w143_02 are "
     "the pair of one level']"),
]
for a, b in reps:
    n = t.count(a)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, a[:80]))
    t = t.replace(a, b)
open(p, 'wb').write(t.encode('utf-8'))
print('patched %d' % len(reps))
