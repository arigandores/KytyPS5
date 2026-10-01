p = 'C:/kyty/s144/step0/partD.py.txt'
t = open(p, 'rb').read().decode('ascii')
R = [
("ok &= case('D18h a W without its log has no key (and is not admitted by the form line)', e['wkey'] is None and not adm_ok(e))\n",
 "ok &= case('D18h a W without its log has no key and fails the form line row itself (no log is no proof of the form)',\n"
 "           e['wkey'] is None and [a[1] for a in e['admit'] if a[0].startswith('W form: no')] == [False])\n"),
("           'STOP RULE CONTROL before w144_01: not made' in r27b[1])\n",
 "           'STOP RULE CONTROL before w144_01: not made' in r27b[1])\n"
 "o27 = S.summary(str(R27), SH4, None)[0]\n"
 "ok &= case('D26d the summary of a series whose control W attempt has no json: the control line says STOP by the gate',\n"
 "           any(x.startswith('CONTROL W w144_00 (underwater_aerial_garden, item 254 (k)(4)): STOP; letter (death marker or '\n"
 "                            '[Vulkan][E]) pass (none); executor reading (any W row or admission row failing; the gate) stop '\n"
 "                            '(attempt made without json (instrument))') for x in o27))\n"),
("      dict(js143('v143_02'), prereg=dict(path=S.PRED_PATH, sha256=SH3)))\n",
 "      dict(js143('v143_02'), prereg=dict(path=S.PRED_PATH, sha256=SH3)))\n"
 "mk143(RG3, 'v143_03', scene_lines(LV3, [16667] * 700 + [150000] + [16667] * 7300),\n"
 "      dict(js143('v143_03'), prereg=dict(path=S.PRED_PATH, sha256=SH3), binary_sha256=OTHER))\n"),
]
for a, b in R:
    assert t.count(a) == 1, a[:70]
    t = t.replace(a, b)
open(p, 'wb').write(t.encode('ascii'))
print('ok')
