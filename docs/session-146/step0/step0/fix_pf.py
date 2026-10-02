p='C:/kyty/s146/step0/partf146.py.txt'; t=open(p,'rb').read().decode('ascii')
old="b40 = [x for x in o17v if x.startswith('B40 SECOND HOLD bonus_path_maker_mix (r146_04;')]\n"
new=("R17b = BASE / 'F17b'\n"
     "mk146(R17b, 'r146_01', sheet=False)\n"
     "o17b = S.summary(str(R17b), SH6, 'viewed')[0]\n"
     "R17c = BASE / 'F17c'\n"
     "mk146(R17c, 'r146_01')\n"
     "with open(R17c / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:\n"
     "    f.write('2026-10-02T00:00:01Z go146a r146_01 enter_scene end rc 0 log_r146_01.txt sha256 %s\n' % ('ef' * 32))\n"
     "o17c = S.summary(str(R17c), SH6, 'viewed')[0]\n"
     "ok &= case('F17b RECHECK with the sheet viewed but no sheet file -> REMOVES SCENE_OK; with the log sha != the last enter_scene '\n"
     "           'end line of times.txt -> REMOVES SCENE_OK (the guest-args / json level / log sha row)',\n"
     "           rl(o17b, 'hoover_beach')[0].endswith(': REMOVES SCENE_OK') and rl(o17c, 'hoover_beach')[0].endswith(': REMOVES SCENE_OK')\n"
     "           and any(x.startswith('  FAIL V guest args -lvl hoover_beach') for x in o17c))\n"
     + old)
assert t.count(old)==1; t=t.replace(old,new)
old2="o19b = S.summary(str(R16), SH6, None)[0]\n"
new2=("R19c = BASE / 'F19c'\n"
      "mk146(R19c, 'w146_00', lines=wl6(SKY, dual=False))\n"
      "(R19c / 'score_i146_v.txt').write_text('FS VERDICT i146_v: PASS\nWARMUP VERDICT i146_v: FAIL (x)\n')\n"
      "o19c = S.summary(str(R19c), SH6, None)[0]\n"
      "ok &= case('F19c the Sky Garden line: a control W without the DualSrcBlend line -> STOP; the WARMUP VERDICT line (not another '\n"
      "           'verdict line) is quoted',\n"
      "           any(x.startswith('SKY GARDEN ON dac02fb9') and x.endswith('control W w146_00 STOP') and\n"
      "               'warm-up V i146_v WARMUP VERDICT i146_v: FAIL (x)' in x for x in o19c))\n"
      + old2)
assert t.count(old2)==1; t=t.replace(old2,new2)
open(p,'wb').write(t.encode('ascii'))
print('ok')
