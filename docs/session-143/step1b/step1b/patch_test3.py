"""Link 1b (HPP-321): the edge fixtures the mutants of item 242 need - C1e (K2 of exactly 1 s within 120 s at window
frames 598/599), C3s (hold_s exactly 120), C3t (exactly 120 s presented, no cut), C6g in the order that tells the last
go143a line from a later go142a line, C7h (two breaks: the first decides), C7i (only the sha256 of a file changes), C10
(profile 142 prints no line of link 1b).  Each anchor must hit exactly once."""
p = 'C:/kyty/s143/test_sc143.py'
t = open(p, 'rb').read().decode('utf-8')
reps = [
    ("RC = BASE / 'C2'\n",
     "d1e = S.derive(S.scan(mk143(BASE / 'C1f', 'v143_01', scene_lines(LV1, [FILL] * 598 + [1000000, 1000000] + [FILL] * 100))\n"
     "                      + '/log_v143_01.txt'), LV1)\n"
     "ok &= case('C1e K2 of exactly 1 000 000 us within 120 s is in the 120 s list; frame 598 after the first frame is entry, '\n"
     "           '599 is hold', d1e['k2_120'] == [(613, 1000000, 'entry'), (614, 1000000, 'hold')])\n"
     "RC = BASE / 'C2'\n"),
    ("RW = BASE / 'C4'\n",
     "e = S.entry_of('v143_01', mk143(BASE / 'C3s', 'v143_01', scene_lines(LV1, LATE),\n"
     "                                js143('v143_01', attempt=dict(hold_s=120.0))), PRED_SHA)\n"
     "ok &= case('C3s hold_s exactly 120 is enough on 120 s: HOLDS_120', e['outcome120'] == ('HOLDS_120', 'held'))\n"
     "e = S.entry_of('v143_01', mk143(BASE / 'C3t', 'v143_01', scene_lines(LV1, [FILL] * 2912)), PRED_SHA)\n"
     "ok &= case('C3t exactly 120 000 000 us presented after the entry line: no cut, HOLDS_120 on 120 s',\n"
     "           e['derive']['cut120_pos'] is None and e['derive']['dt_after_entry_us'] == 120000000 and\n"
     "           e['outcome120'] == ('HOLDS_120', 'held'))\n"
     "RW = BASE / 'C4'\n"),
    ("    f.write('2026-10-01T00:00:01Z go142a v143_01 enter_scene end rc 0 log_v143_01.txt sha256 %s\\n' % ('cd' * 32))\n"
     "    f.write('2026-10-01T00:00:01Z go143a v143_01 enter_scene end rc 0 log_v143_01.txt sha256 %s\\n' % ('ef' * 32))\n",
     "    f.write('2026-10-01T00:00:01Z go143a v143_01 enter_scene end rc 0 log_v143_01.txt sha256 %s\\n' % ('ef' * 32))\n"
     "    f.write('2026-10-01T00:00:02Z go142a v143_01 enter_scene end rc 0 log_v143_01.txt sha256 %s\\n' % ('cd' * 32))\n"),
    ("ok &= case('C7f a pair with a tag not made has no line (v143_03 -> w143_03)',\n"
     "           not any(x.startswith('  v143_03 -> w143_03') for x in o7d))\n",
     "ok &= case('C7f a pair with a tag not made has no line (v143_03 -> w143_03)',\n"
     "           not any(x.startswith('  v143_03 -> w143_03') for x in o7d))\n"
     "RH = BASE / 'C7h'\n"
     "for t in ('v143_01', 'w143_01', 'v143_02', 'w143_02'):\n"
     "    mk143(RH, t)\n"
     "manifest(RH, 'v143_01', 'after', F0)\n"
     "manifest(RH, 'w143_01', 'before', F0)\n"
     "manifest(RH, 'w143_01', 'after', F0)\n"
     "manifest(RH, 'v143_02', 'before', F1)\n"
     "manifest(RH, 'v143_02', 'after', F1)\n"
     "manifest(RH, 'w143_02', 'before', F0)\n"
     "o7h = S.summary(str(RH), PRED_SHA, None)[0]\n"
     "ok &= case('C7h two breaks (before v143_02 and before w143_02): the FIRST decides the forms',\n"
     "           any(x.startswith('FORMS without the tags after the first cache break (before v143_02;') for x in o7h)\n"
     "           and sum(1 for x in o7h if 'cache changed between tags' in x) == 2)\n"
     "manifest(RH, 'w143_02', 'before', [F1[0][:4] + ('ee' * 32,)] + F1[1:])\n"
     "ok &= case('C7i only the sha256 of a file differs -> changed (~1)', S.cache_diff(\n"
     "    S.cache_manifest(str(RH), 'v143_02', 'after'), S.cache_manifest(str(RH), 'w143_02', 'before'))['shader'] ==\n"
     "    (0, 0, 1, False))\n"),
    ("ok &= case('C9 every line new in link 1b is ASCII', encc)\n",
     "ok &= case('C9 every line new in link 1b is ASCII', encc)\n"
     "ok &= case('C10 profile 142 prints no line of link 1b (no 120 s outcome, no map (A) row, no B5a variant, no cache '\n"
     "           'continuity, no W info line)', not any(s in x for x in outr for s in (\n"
     "               'outcome on 120 s', 'map (A) row', 'FORM B5a variant', 'K2 ON THE HOLD', 'CACHE CONTINUITY', 'FORMS without',\n"
     "               'under validation, not classified', 'json level')) and any('K2 frames (dt >= 1 s' in x for x in outr))\n"),
]
for a, b in reps:
    n = t.count(a)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, a[:90]))
    t = t.replace(a, b)
open(p, 'wb').write(t.encode('utf-8'))
print('patched %d' % len(reps))
