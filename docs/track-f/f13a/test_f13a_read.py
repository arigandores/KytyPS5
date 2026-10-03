"""F13a (HPP-479): fixtures of f13a_read.py - one per member and edge of the seal (docs/track-f/f13a.md section 4); the regression
on the v146_08 log (card end k 1259, 20.98 s, hold 311.459 s) runs when the log is there.  ASCII only; ends with ALL OK.
usage: python test_f13a_read.py"""
import hashlib, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f13a_read as R

fails = []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f13a_read.py sha256 %s target f13a_read.py sha256 %s' % (sha(__file__), sha(os.path.join(HERE, 'f13a_read.py'))))


def check(name, cond):
    print('%s %s' % ('OK  ' if cond else 'FAIL', name))
    if not cond:
        fails.append(name)


def ft(n, draws, dt=16667):
    return 'FrameTrace: n=%d dt_us=%d lat_us=1 draws=%d draw_us=0\n' % (n, dt, draws)


def build(parts):
    d = tempfile.mkdtemp(prefix='f13a_')
    with open(os.path.join(d, 'log.txt'), 'w', newline='\n') as f:
        f.write(''.join(parts))
    return d


def scene(card=100, black=8000, pre=['GuestOut: Level has started: \n'], extra=None, card_draws=1018, dt=16667):
    """pre lines, entry, `card` rows of card_draws, `black` rows of 22; extra = {row index after entry: [lines]} (inserted after it)."""
    p = list(pre) + [ft(1, 29), 'GuestOut: Level has started: ending_boss_after_credit\n']
    n = 2
    total = card + black
    for i in range(1, total + 1):
        p.append(ft(n, card_draws if i <= card else 22, dt))
        n += 1
        for x in (extra or {}).get(i, []):
            p.append(x)
    return p


def press(key, s, present):
    return 'InputScript: press %s at %.2f s (present %u)\n' % (key, s, present)


# 1 card end: first row < 100 after >= 90 rows >= 300; k is the row number after entry
r = R.analyse('rd', os.path.join(build(scene(card=100, black=50)), 'log.txt'))
check('card_end_k = 101 after 100 card rows', r['card_end_k'] == 101)
check('card_end_s_from_entry = 100 rows x 16667 us', abs(r['card_end_s_from_entry'] - 1.6667) < 1e-3)
check('card_draws_median 1018', r['card_draws_median'] == 1018)
# 2 edge: a run of 89 rows >= 300 is not a card
r = R.analyse('rd', os.path.join(build(scene(card=89, black=50)), 'log.txt'))
check('card of 89 rows -> NOT_FOUND', r['card_end_k'] == 'NOT_FOUND')
r = R.analyse('rd', os.path.join(build(scene(card=90, black=50)), 'log.txt'))
check('card of 90 rows -> card_end_k 91', r['card_end_k'] == 91)
# 3 edge: a dip below 100 before the 90-row run is not the card end; rows between 100 and 300 do not end the card
p = scene(card=0, black=0) + [ft(9, 1018)] * 10 + [ft(9, 50)] + [ft(9, 1018)] * 95 + [ft(9, 150)] * 3 + [ft(9, 22)] * 5
r = R.analyse('rd', os.path.join(build(p), 'log.txt'))
check('early dip ignored; rows of 100..299 after the card run do not end it, the first row < 100 does (k 110)', r['card_end_k'] == 110)
p = scene(card=0, black=0) + [ft(9, 1018)] * 10 + [ft(9, 50)] + [ft(9, 1018)] * 95 + [ft(9, 22)] * 5
r = R.analyse('rd', os.path.join(build(p), 'log.txt'))
check('early dip ignored, card end = row 107', r['card_end_k'] == 107)
# 4 rd: capture line t(card) and the 10 s row (600 rows x 16667 us = 10.0002 s)
ex = {100 + 600: ['RenderDoc: auto capture at frame 900 (level+700)\n', 'RenderDoc: capture started\n'],
      100 + 602: ['RenderDoc: captured guest flip 1/2\n', 'RenderDoc: captured guest flip 2/2\n', 'RenderDoc: capture finished\n']}
r = R.analyse('rd', os.path.join(build(scene(card=100, black=2000, pre=['RenderDoc: level started at frame 5, capture at frame 705 (+0 more)\n'], extra=ex)), 'log.txt'))
check('rd capture t_card = 600 rows = 10.0002 s', abs(r['rd_capture_t_card'] - 10.0002) < 1e-3)
check('rd_after_card_10s YES at 10.0002 s', r['rd_after_card_10s'] == 'YES')
check('rd capture draws next 3 = 22', r['rd_capture_draws_next3'] == [22, 22, 22])
check('rd_finished YES', r['rd_finished'] == 'YES')
check('rd level-started line before entry kept', any('level started at frame' in x for x in r['rd_lines']))
ex = {100 + 599: ['RenderDoc: auto capture at frame 900 (level+700)\n']}
r = R.analyse('rd', os.path.join(build(scene(card=100, black=2000, extra=ex)), 'log.txt'))
check('rd_after_card_10s NO at 599 rows (9.983 s)', r['rd_after_card_10s'] == 'NO')
check('rd_finished NO without the line', r['rd_finished'] == 'NO')
r = R.analyse('rd', os.path.join(build(scene(card=100, black=2000)), 'log.txt'))
check('rd_after_card_10s NOT_DETERMINED without a capture line', r['rd_after_card_10s'] == 'NOT_DETERMINED')
ex = {50: ['RenderDoc: auto capture at frame 900 (level+700)\n']}
r = R.analyse('rd', os.path.join(build(scene(card=100, black=2000, extra=ex)), 'log.txt'))
check('rd capture inside the card -> negative t_card, NO', r['rd_capture_t_card'] < 0 and r['rd_after_card_10s'] == 'NO')
# 5 keys: three J and three L, 15 s apart, all >= 10 s after the card end
keys = [('J', 75), ('J', 90), ('J', 105), ('L', 120), ('L', 135), ('L', 150)]
ex = {}
for key, s in keys:
    row = 100 + int((s - 30) * 60)
    ex.setdefault(row, []).append(press(key, s, row + 10))
idx_d = build(scene(card=100, black=9000, extra=ex))
with open(os.path.join(idx_d, 'rec.idx'), 'w') as f:
    for i in range(9200):
        f.write('%d %d %.3f\n' % (i, i + 1, i / 60.0))
with open(os.path.join(idx_d, 'glitch.txt'), 'w') as f:
    f.write('one-frame glitches: 0\n')
with open(os.path.join(idx_d, 'sheet.txt'), 'w') as f:
    f.write('sheet: x.png frames 9200 step 191 tiles 8x6\n')
with open(os.path.join(idx_d, 'installed_sha.txt'), 'w') as f:
    f.write(R.WANT + '\n')
with open(os.path.join(idx_d, 'manifest_cmp.txt'), 'w') as f:
    f.write('manifest cmp EQUAL files 3 listsha abc\n')
r = R.analyse('k', os.path.join(idx_d, 'log.txt'), os.path.join(idx_d, 'rec.idx'), os.path.join(idx_d, 'glitch.txt'),
              os.path.join(idx_d, 'sheet.txt'), os.path.join(idx_d, 'manifest_cmp.txt'), os.path.join(idx_d, 'installed_sha.txt'))
check('presses J 3 L 3 -> YES', r['presses_J'] == 3 and r['presses_L'] == 3 and r['presses_J_ge3_L_ge3'] == 'YES')
check('keys_after_card_10s YES (first at 45 s after the card)', r['keys_after_card_10s'] == 'YES')
check('first press t_card = 2700 rows', abs(r['presses'][0]['t_card'] - 2700 * 0.016667) < 1e-3)
check('keys_pause_10s YES at 15 s', r['keys_pause_10s'] == 'YES')
check('video frame of a press = first idx frame with present >= press present', r['presses'][0]['video_frame'] == r['presses'][0]['k'] + 9)
check('video rows read (records, glitches 0, sheet YES)', r['video_records'] == 9200 and r['video_glitches'] == 0 and r['video_sheet'] == 'YES')
check('installed_sha YES, manifest EQUAL line', r['installed_sha'] == 'YES' and r['manifest_cmp'].startswith('manifest cmp EQUAL'))
check('hold_after_card_120s YES (9000 rows = 150 s)', r['hold_after_card_120s'] == 'YES')
check('draws window card..first press = only 22', r['draws_card_to_first_press_top'] == [[22, 2700]] or r['draws_card_to_first_press_top'] == [(22, 2700)])
# 5b edges: a press 9.98 s after the card end, a pause of 9.9 s, two L only
ex = {100 + 599: [press('J', 40, 700)], 100 + 2000: [press('J', 49.9, 2100)], 100 + 3000: [press('L', 70, 3100)], 100 + 4000: [press('L', 90, 4100)]}
r = R.analyse('k', os.path.join(build(scene(card=100, black=9000, extra=ex)), 'log.txt'))
check('keys_after_card_10s NO for a press 599 rows after the card', r['keys_after_card_10s'] == 'NO')
check('keys_pause_10s NO for 9.9 s', r['keys_pause_10s'] == 'NO')
check('presses_J_ge3_L_ge3 NO for 2 + 2', r['presses_J_ge3_L_ge3'] == 'NO')
ex = {100 + 600: [press('J', 40, 700)], 100 + 2000: [press('J', 50.0, 2100)]}
r = R.analyse('k', os.path.join(build(scene(card=100, black=9000, extra=ex)), 'log.txt'))
check('keys_after_card_10s YES at exactly 600 rows (10.0002 s); pause 10.0 s YES', r['keys_after_card_10s'] == 'YES' and r['keys_pause_10s'] == 'YES')
r = R.analyse('k', os.path.join(build(scene(card=100, black=9000)), 'log.txt'))
check('no presses -> NOT_DETERMINED both', r['keys_after_card_10s'] == 'NOT_DETERMINED' and r['keys_pause_10s'] == 'NOT_DETERMINED')
# 6 reaction: a scene line and changed draws after a press are attributed to that press window
ex = {100 + 1000: [press('J', 75, 1100)], 100 + 1100: ['LevelDocument Loaded: worldmap [worldmap]\n', 'GuestOut: Level has started: worldmap\n'],
      100 + 2000: [press('J', 90, 2100)]}
p = scene(card=100, black=2100, extra=ex) + [ft(9, 500)] * 2000
r = R.analyse('k', os.path.join(build(p), 'log.txt'))
check('scene lines after a press belong to its window (2)', len(r['presses'][0]['scene_lines_until_next']) == 2 and r['presses'][1]['scene_lines_until_next'] == [])
check('scene_lines_after_card counts them (2)', r['scene_lines_after_card'] == 2)
check('draws median after the second press = 500', r['presses'][1]['draws_med_after'] == 500)
# 7 hold edge: 7199 rows after the card = 119.98 s -> NO; 7200 rows = 120.0024 -> YES
r = R.analyse('rd', os.path.join(build(scene(card=100, black=7199)), 'log.txt'))
check('hold 7199 rows -> NO', r['hold_after_card_120s'] == 'NO')
r = R.analyse('rd', os.path.join(build(scene(card=100, black=7200)), 'log.txt'))
check('hold 7200 rows -> YES', r['hold_after_card_120s'] == 'YES')
# 8 death, frames >= 1 s, skipped draw, window events, swapchain recovery; entry missing
ex = {200: ['GpuHangAbort: x\n', 'AsyncPipelines: skipped draw 0x1\n', 'Window 1 minimized\n', 'Recovering Vulkan swapchain\n']}
p = scene(card=100, black=300, extra=ex)
p.insert(150, ft(9, 22, 1000000))
r = R.analyse('rd', os.path.join(build(p), 'log.txt'))
check('death line counted', r['death_lines'] == 1)
check('frame dt 1 000 000 counted (edge >=)', len(r['frames_ge_1s']) == 1)
p = scene(card=100, black=300)
p.insert(150, ft(9, 22, 999999))
r = R.analyse('rd', os.path.join(build(p), 'log.txt'))
check('frame dt 999 999 not counted', len(r['frames_ge_1s']) == 0)
r = R.analyse('rd', os.path.join(build(scene(card=100, black=300, extra=ex)), 'log.txt'))
check('skipped draw 1, window minimized 1, recovering 1', r['skipped_draw_lines'] == 1 and r['window_events'] == {'minimized': 1} and r['recovering_swapchain'] == 1)
p = ['GuestOut: Level has started: hub_crashsite\n'] + [ft(1, 1018)] * 200
r = R.analyse('rd', os.path.join(build(p), 'log.txt'))
check('no entry line of the level -> entry NO, no rows', r['entry'] == 'NO' and r['rows_after_entry'] == 0)
# 9 output in strict cp1250 without PYTHONIOENCODING (item 175 (v)), and the json
d = build(scene(card=100, black=300, extra={150: [press('J', 75, 300)]}))
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
pr = subprocess.run([sys.executable, os.path.join(HERE, 'f13a_read.py'), '--dir', d, '--kind', 'k', '--json', os.path.join(d, 'o.json')],
                    capture_output=True, env=env)
check('reader rc 0 under cp1250 strict', pr.returncode == 0)
check('reader stdout is ASCII and ends with the ROWS line', all(b < 128 for b in pr.stdout) and pr.stdout.strip().splitlines()[-1].startswith(b'ROWS '))
check('json written and parses', json.load(open(os.path.join(d, 'o.json')))['presses_J'] == 1)
# 10 regression on the v146_08 log (reference of the seal)
V = 'C:/kyty/s146/log_v146_08.txt'
if os.path.isfile(V):
    r = R.analyse('k', V)
    check('regression v146_08: card_end_k 1259, 20.98 s, hold 311.459 s, 0 presses, 0 scene lines after the card',
          r['card_end_k'] == 1259 and r['card_end_s_from_entry'] == 20.98 and r['hold_after_card_s'] == 311.459
          and r['presses_J'] == 0 and r['scene_lines_after_card'] == 0)
else:
    check('regression log v146_08 present', False)
print('FAILED: %s' % fails)
if not fails:
    print('ALL OK')
sys.exit(1 if fails else 0)
