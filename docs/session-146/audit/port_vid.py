# port_vid.py - builds vid146.py and glitch146.py from the auditor's own vid145.py / glitch145.py by anchored replacements.
D = 'C:/kyty/KytyPS5/docs/session-145/audit/'
src = open(D + 'vid145.py', 'rb').read().decode('utf-8')
def rep(a, b, n=1):
    global src
    assert src.count(a) == n, (a, src.count(a))
    src = src.replace(a, b)
rep("# vid145.py - Session Auditor, s145 step 3 (HPP-353)", "# vid146.py - Session Auditor, s146 step 3 (HPP-389)")
rep("No code of sc145.py / s51_vidglitch.py / sheet142.py (a port of the", "No code of sc146.py / s51_vidglitch.py / sheet142.py / tiles146.py (a port of the")
rep("# auditor's own vid144.py + vidcont144.py).", "# auditor's own vid145.py).")
rep("Usage: python vid145.py [--no-decode]", "Usage: python vid146.py [--no-decode]")
rep("A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s145/step3/aud145.json'))}",
    "A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s146/step3/aud146.json'))}")
rep("VID = [('s145', 'C:/kyty/s145', 'runs145', 'v145_%02d' % i) for i in range(2, 18)] + [('s144', 'C:/kyty/s144', 'runs144', 'v144_09')]",
    "VID = [('s146', 'C:/kyty/s146', 'runs146', t) for t in ['i146_v'] + ['r146_%02d' % i for i in range(1, 5)] + ['v146_%02d' % i for i in range(5, 20)]]")
rep("        new = R['ses'] == 's145'", "        new = R['tag'] != 'i146_v'")
rep("('FrameTrace rows (second own read) = rows of aud145', R['rows'], rows),", "('FrameTrace rows (second own read) = rows of aud146', R['rows'], rows),")
# the warm-up tag has no score.json: only the own counts are compared for it
rep("        checks = [('container samples = decoded frames', mine, dc['frames'] if dc else mine),",
    "        if 'error' in sc:\n"
    "            sc = {'video_frames': dc['frames'] if dc else mine, 'idx': ix['records'] if ix else None, 'rows_total': rows, 'cover': (dc['frames'] if dc else mine) >= rows - 100,\n"
    "                  'rec_sha': R['sha256'], 'times_rec_sha': R['sha256'], 'sheet_sha': R['sheet_sha'], 'sheet_times_sha': R['sheet_sha'], 'noscore': True}\n"
    "        checks = [('container samples = decoded frames', mine, dc['frames'] if dc else mine),")
rep("        nf += len(checks)", "        if sc.get('noscore'):\n            checks = checks[:2] + [checks[5]]\n        nf += len(checks)")
rep("json.dump(res, open('C:/kyty/s145/step3/vid145.json', 'w', encoding='ascii')", "json.dump(res, open('C:/kyty/s146/step3/vid146.json', 'w', encoding='ascii')")
assert '145' not in src.replace('vid145.py', ''), [l for l in src.split(chr(10)) if '145' in l]
open('C:/kyty/s146/step3/vid146.py', 'wb').write(src.encode('utf-8'))
src = open(D + 'glitch145.py', 'rb').read().decode('utf-8')
rep("# glitch145.py - Session Auditor, s145 step 3 (HPP-353), debt D-4 of s144: own detector of one-frame glitches.",
    "# glitch146.py - Session Auditor, s146 step 3 (HPP-389): own detector of one-frame glitches (= the auditor's glitch145.py, header only).")
rep("Usage: python glitch145.py <out.json>", "Usage: python glitch146.py <out.json>")
rep("R['tile_top'] = ttop[:8]" if False else "'tile_events_T4': tev4, 'tile_events_T12': tev12, 'tile_top': ttop[:8],",
    "'tile_events_T4': tev4, 'tile_events_T12': tev12, 'tile_top': ttop[:8], 'tile_frames': sorted(x[0] for x in ttop),")
assert '145' not in src.replace('glitch145.py', ''), 1
open('C:/kyty/s146/step3/glitch146.py', 'wb').write(src.encode('utf-8'))
print('written')
