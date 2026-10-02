# port_aud.py - builds aud146.py from the auditor's own aud145.py by anchored replacements (no backslashes in this file).
import io, sys
src = open('C:/kyty/KytyPS5/docs/session-145/audit/aud145.py', 'rb').read().decode('utf-8')
def rep(a, b, n=1):
    global src
    assert src.count(a) == n, (a, src.count(a))
    src = src.replace(a, b)
rep("# aud145.py - Session Auditor, s145 step 3 (HPP-353). Own recount of the sc145 outputs from the logs.",
    "# aud146.py - Session Auditor, s146 step 3 (HPP-389). Own recount of the sc146 outputs from the logs.")
rep("# Independent of sc145.py / sc144.py / gate145.py: no import, no shared code (a port of the auditor's own aud144.py).",
    "# Independent of sc146.py / gate146.py: no import, no shared code (a port of the auditor's own aud145.py).")
rep("# Rules by the letter of pred/03_sc145.md s.2-4 (= pred/01_sc144.md s.2-4) and ROADMAP s122 items 221 (v)-(g), 224, 242,",
    "# Rules by the letter of pred/02_sc146.md s.1-2, 5 and ROADMAP s122 items 221 (v)-(g), 224, 242, 273 (k), 295 (b), (g),")
rep("# 254 (e), 266, 273 (k), 295 (b), (g). Reads the logs through mmap in binary mode, never whole text.",
    "# 300 (b)(4), 309 (l)(4), 316. New data rows: stubs (F13), asserts (F14), DualSrcBlend. Reads the logs through mmap, binary mode.")
rep("# Usage: python aud145.py <out.json> [--workers N]", "# Usage: python aud146.py <out.json> [--workers N]")
rep("S145 = 'C:/kyty/s145'", "S146 = 'C:/kyty/s146'")
rep("S144 = 'C:/kyty/s144'\n", "")
a = src.index("LV = [")
b = src.index("FT = b'FrameTrace: n='")
src = src[:a] + ("RL = ['hoover_beach', 'sponge_dirty_bath', 'timestop_casino', 'bonus_path_maker_mix']\n"
    "LV = ['robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit', 'collectible_viewer',\n"
    "      'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo', 'fragile_battle_1', 'voxel_challenge_1',\n"
    "      'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2', 'fragile_battle_3']\n") + src[b:]
rep("         b'Recovering Vulkan swapchain', b'eErrorOutOfDateKHR', b'eSuboptimalKHR']",
    "         b'Recovering Vulkan swapchain', b'eErrorOutOfDateKHR', b'eSuboptimalKHR', b'Unresolved import stub called', b'ASSERT:',\n"
    "         b'user_msg_param', b'DualSrcBlend:', b'VK_LAYER_KHRONOS_validation', b'VK_EXT_validation_features', b'VK_EXT_debug_utils']\n"
    "RDUAL = re.compile(rb'DualSrcBlend: supported=(" + chr(92) + "d+) enabled=(" + chr(92) + "d+)')")
rep("            R['recipes_arrow_lines'] = len(RREC.findall(mm))",
    "            R['recipes_arrow_lines'] = len(RREC.findall(mm))\n"
    "            R['dual'] = [(m.start(), int(m.group(1)), int(m.group(2))) for m in RDUAL.finditer(mm)]\n"
    "            gp = first_pos.get('GuestOut')\n"
    "            R['dual_pre'] = sum(1 for p, s, e in R['dual'] if (s, e) == (1, 1) and (gp is None or p < gp))")
rep("    out['recipes_arrow_lines'] = len(RREC.findall(data))",
    "    out['recipes_arrow_lines'] = len(RREC.findall(data))\n"
    "    out['dual'] = [(m.start(), int(m.group(1)), int(m.group(2))) for m in RDUAL.finditer(data)]")
a = src.index("    jobs = [('w145_00'")
b = src.index("    with Pool(workers) as pool:")
src = src[:a] + ("    jobs = [('i146_v', 'underwater_aerial_garden', S146), ('w146_00', 'underwater_aerial_garden', S146)]\n"
    "    for i, lv in enumerate(RL, 1):\n"
    "        jobs.append(('r146_%02d' % i, lv, S146))\n"
    "    for i, lv in enumerate(LV, 5):\n"
    "        jobs.append(('v146_%02d' % i, lv, S146))\n"
    "        jobs.append(('w146_%02d' % i, lv, S146))\n"
    "    jobs = [(t, lv, root, '%s/log_%s.txt' % (root, t)) for t, lv, root in jobs]\n"
    "    known = set(j[3] for j in jobs)\n"
    "    lvof = {j[0]: j[1] for j in jobs}\n"
    "    for f in sorted(os.listdir(S146)):\n"
    "        if re.match(r'log_.*[.]txt$', f) and ('%s/%s' % (S146, f)) not in known:\n"
    "            t = f[4:-4]\n"
    "            jobs.append((t, lvof.get(t[:7]), S146, '%s/%s' % (S146, f)))\n") + src[b:]
rep("    for r in res:\n        L = r['log']", "    for r in res:\n        L = r['log']\n        d = L.get('dual') or []")
rep("'marks', L.get('n_marks'), 'minimized', (L.get('win_kinds') or {}).get('minimized'), 'recover', c.get('Recovering Vulkan swapchain'))",
    "'marks', L.get('n_marks'), 'minimized', (L.get('win_kinds') or {}).get('minimized'), 'recover', c.get('Recovering Vulkan swapchain'),\n"
    "              'stubcall', c.get('Unresolved import stub called'), 'ASSERT', c.get('ASSERT:'), 'ump', c.get('user_msg_param'),\n"
    "              'dual', [x[1:] for x in d], 'dual_pre', L.get('dual_pre'), 'changes', [x[1] for x in (L.get('scene_changes') or [])])")
assert 's145' not in src.lower().replace('aud145.py', '').replace('sc145', ''), [l for l in src.split('\n') if '145' in l]
open('C:/kyty/s146/step3/aud146.py', 'wb').write(src.encode('utf-8'))
print('aud146.py written', len(src))
