"""Link 1b (HPP-321): clean part C (step1b/partC.py.txt) and insert it into test_sc143.py before the final count lines.
LF kept; each replacement must hit exactly once."""
p = 'C:/kyty/s143/test_sc143.py'
c = open('C:/kyty/s143/step1b/partC.py.txt', 'rb').read().decode('utf-8')
fix = [
    ("cut_lines = scene_lines(LV1, LATE[:3500] + ['MARK'] + LATE[3500:])\n"
     "cut_lines = [BOOM if x == ft(3515, 'MARK') else x for x in cut_lines] if False else None\n", ""),
    ("ok &= case('C4c the W SCENE_OK reads the dt-free W: a W with a frame dt 1.2 s is still YES', S.scene_ok(\n"
     "    ev and S.entry_of('v143_01', mk143(RW / 'c', 'v143_01'), PRED_SHA), S.entry_of('w143_01', mk143(RW / 'c', 'w143_01', WK2),\n"
     "                                                                                    PRED_SHA), 'viewed')[0] == 'YES')\n",
     "vc = S.entry_of('v143_01', mk143(RW / 'c', 'v143_01'), PRED_SHA)\n"
     "wc = S.entry_of('w143_01', mk143(RW / 'c', 'w143_01', WK2), PRED_SHA)\n"
     "ok &= case('C4c the W SCENE_OK has no dt row: a W with a frame dt 1.2 s and a good V -> YES',\n"
     "           S.scene_ok(vc, wc, 'viewed')[0] == 'YES')\n"),
    ("def wstop(name, rep, tag='w143_01', std=False):\n"
     "    lines = [VF] + scene_lines(LV1, [150000] * 300) + [VW]\n"
     "    if not std:\n"
     "        lines = lines + rep\n"
     "    root = mk143(BASE / name, tag, lines if tag in S.W_TAGS else scene_lines(LV1, LATE) + ([] if std else rep))\n",
     "def wstop(name, rep, tag='w143_01', std=False):\n"
     "    base = ([VF] + scene_lines(LV1, [150000] * 300) + [VW]) if tag in S.W_TAGS else scene_lines(LV1, LATE)\n"
     "    root = mk143(BASE / name, tag, base if std else base + rep)\n"),
    ("           w5 == 'NO' and sorted(r[0][:22] for r in rows5 if not r[1]) == ['W 0 . death markers'[:0] + 'W 0 [Vulkan][E] lines',\n"
     "                                                                          'W 0 death markers (inc'])\n",
     "           w5 == 'NO' and sorted(r[0] for r in rows5 if not r[1]) == ['W 0 [Vulkan][E] lines',\n"
     "                                                                     'W 0 death markers (incl. hold_exit, exited)'])\n"),
    ("old = S.profile(S.P142)\n"
     "r142 = S.build('w142', SKY, js_for('w142'), S.scan(Path(wstop('C5j', REP)['tag'] and BASE / 'C5j' / 'log_w143_01.txt')),\n"
     "               None, None, str(BASE / 'C5j'), PRED_SHA)\n"
     "S.profile(old)\n"
     "ok &= case('C5j profile 142 keeps the reading of s142: the same report -> K1', r142['outcome'] == 'K1'\n"
     "           and r142['marks'][0]['cls'] == 'K1')\n",
     "wstop('C5j', REP)\n"
     "lg = S.scan(str(BASE / 'C5j' / 'log_w143_01.txt'))\n"
     "old = S.profile(S.P142)\n"
     "r142 = S.build('w142', SKY, js_for('w142'), lg, None, None, str(BASE / 'C5j'), PRED_SHA)\n"
     "S.profile(old)\n"
     "ok &= case('C5j profile 142 keeps the reading of s142: the same report -> K1 (the scan still finds it)',\n"
     "           [m['cls'] for m in r142['marks']] == ['K1'] and len(lg['err_vk']) == 1)\n"),
    ("e = S.entry_of('v143_01', mk143(BASE / 'C3r', 'v143_01', scene_lines(LV1, [FILL] * 100, first_draws=50)), PRED_SHA)\n",
     "e = S.entry_of('v143_01', mk143(BASE / 'C3r', 'v143_01', scene_lines(LV1, [], first_draws=50) +\n"
     "                                [ft(15 + i, FILL, 50) for i in range(4000)]), PRED_SHA)\n"),
    ("           d119['k2_120'] == [(2853, 1200000, 'hold')] and d119['k2'] == [(2853, 1200000, 'hold')]\n"
     "           and d121['k2_120'] == [] and d121['k2'] == [(2903, 1200000, 'hold')])\n",
     "           d119['k2_120'] == [(2872, 1200000, 'hold')] and d119['k2'] == [(2872, 1200000, 'hold')]\n"
     "           and d121['k2_120'] == [] and d121['k2'] == [(2922, 1200000, 'hold')])\n"),
    ("'row past 120 s', d120['k2_120'] == [(2878, 1200000, 'hold')] and d120b['k2_120'] == [] and\n",
     "'row past 120 s', d120['k2_120'] == [(2897, 1200000, 'hold')] and d120b['k2_120'] == [] and\n"),
    ("           any(x.startswith('  K2 frames within 120 s of presented time after the entry line (item 242 (c)): [(2853, '\n",
     "           any(x.startswith('  K2 frames within 120 s of presented time after the entry line (item 242 (c)): [(2872, '\n"),
]
for a, b in fix:
    n = c.count(a)
    if n != 1:
        raise SystemExit('part C anchor count %d: %r' % (n, a[:90]))
    c = c.replace(a, b)
t = open(p, 'rb').read().decode('utf-8')
anchor = "print('checks: %d' % N_CASES[0])\n"
if t.count(anchor) != 1 or t.count('# ================= PART C') != 0:
    raise SystemExit('test anchor')
t = t.replace(anchor, c + anchor)
open(p, 'wb').write(t.encode('utf-8'))
print('part C inserted: %d lines' % c.count('\n'))
