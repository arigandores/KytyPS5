# ---------------- link 1b (HPP-282, item 224 (a)(1)-(10)): one case per new term and per edge
LV = 'bumper_enemy_snowy_canyon'
ok &= case('m8b the seal of link 1b is pred/02_sc142.md', S.PRED_PATH == 'C:/kyty/s142/pred/02_sc142.md')
ok &= case('b0 the check logs of item 224 (b)(2): s1s128, s2s128 of s128; s6s137 log and stdout of s137',
           S.CHECK_K2 == (('s1s128', 'C:/kyty/s128'), ('s2s128', 'C:/kyty/s128')) and S.CHECK_VAL ==
           ('s6s137', 'C:/kyty/s137/log_s6s137.txt', 'C:/kyty/s137/stdout_s6s137.txt'))
d = S.derive(mem([(1, 20000, 100), (2, 50, 3000), (3, 10, 3000), (4, 40, 3000), (5, 30, 3000), (6, 20, 3000)], [('lvl', 0)]), 'lvl')
ok &= case('f3 dt median and max after the first scene frame (10 20 30 40 50 -> 30, 50)', d['dt_median_us'] == 30
           and d['dt_max_us'] == 50)
# RC1: the outcome class by the FIRST death marker by position (item 224 (a)(1))
e = census('n1', None, lines=scene_lines(LV, LONG) + ['vkQueueSubmit failed: ErrorDeviceLost (-4)', '--- Fatal Error ---'],
           js=js_for('c142_01', attempt=dict(hold_exit=321)))
ok &= case('n1 ErrorDeviceLost -> --- Fatal Error --- + hold_exit -> K2 (the crash is the consequence), markers in order',
           e['outcome'] == 'K2' and [m['kind'] for m in e['marks']] == ['ErrorDeviceLost', '--- Fatal Error ---']
           and e['reason'].startswith('first death marker ErrorDeviceLost'))
e = census('n2', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1', '--- Error ---'],
           js=js_for('c142_01', attempt=dict(outcome='exited', hold_s=None, ft_tail=None)))
ok &= case('n2 GpuHangAbort: -> --- Error --- + exited -> K2', e['outcome'] == 'K2')
e = census('n3', None, lines=scene_lines(LV, LONG) + ['--- Error ---', 'GpuHangAbort: requested=1'])
ok &= case('n3 --- Error --- -> GpuHangAbort: -> K1', e['outcome'] == 'K1' and e['marks'][0]['kind'] == '--- Error ---')
e = census('n3b', None, lines=scene_lines(LV, LONG) + ['--- Fatal Error ---', 'vkWaitSemaphores failed: ErrorDeviceLost'])
ok &= case('n3b --- Fatal Error --- -> ErrorDeviceLost -> K1', e['outcome'] == 'K1')
e = census('n4', None, lines=scene_lines(LV, LONG) + ['--- Error ---'], stdout_lines=['GpuHangAbort: requested=1'])
ok &= case('n4 a crash in the log, a hang only in the stdout -> K1 (stdout markers after the log ones)',
           e['outcome'] == 'K1' and [m['src'] for m in e['marks']] == ['log', 'stdout'])
e = census('n4b', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1'], stdout_lines=['--- Fatal Error ---'])
ok &= case('n4b a hang in the log, a crash only in the stdout -> K2', e['outcome'] == 'K2')
e = census('n4c', LONG, stdout_lines=['GpuHangAbort: requested=1', '--- Fatal Error ---'])
ok &= case('n4c stdout only: hang then crash -> K2', e['outcome'] == 'K2')
e = census('n4d', LONG, stdout_lines=['--- Fatal Error ---', 'GpuHangAbort: requested=1'])
ok &= case('n4d stdout only: crash then hang -> K1', e['outcome'] == 'K1')
e = census('n5', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1'],
           es_lines=['WARNING: the game ENDED inside the hold after 9.0 s, returncode 1 (0x00000001)'])
ok &= case('n5 a hang in the log + the ENDED line (attempt markers after the log) -> K2', e['outcome'] == 'K2')
e = census('n6', None, lines=[ft(i, 16667) for i in range(1, 900)] + ['GpuHangAbort: requested=1', '--- Error ---'])
ok &= case('n6 not entered: the stop key is the first marker by position (GpuHangAbort:)', e['outcome'] == 'NOT_ENTERED'
           and e['key'] == 'GpuHangAbort:')
e = census('n6b', None, lines=[ft(i, 16667) for i in range(1, 900)] + ['--- Error ---'], stdout_lines=['GpuHangAbort: x'])
ok &= case('n6b not entered: a log crash before a stdout hang -> key --- Error ---', e['key'] == '--- Error ---')
out_n = '\n'.join(S.fmt_entry(census('n7', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1',
                                                                               '--- Error ---'])))
ok &= case('n7 the markers are printed in order with class, source and position',
           out_n.find('K2 GpuHangAbort: log@') < out_n.find('K1 --- Error --- log@') and out_n.find('K2 GpuHangAbort: log@') > 0)
e = census('n8', None, lines=scene_lines(LV, LONG) + ['Event: quit', 'GpuHangAbort: requested=1', '--- Error ---'])
ok &= case('n8 markers after Event: quit: letter K2 by the first, variant vx HOLDS_120', e['outcome'] == 'K2'
           and e['outcome_vx'] == 'HOLDS_120')
# RC2: the admission row of W "validation active" by three terms (item 224 (a)(2))


def w_lines(pre=(VF,), post=(VW,) * 3):
    return list(pre) + W_BASE + list(post)


ok &= case('v0 the W of k1 carries the admission row validation active and it passes; V has no such row',
           any(a[0].startswith('validation active') and a[1] for a in ent(BASE / 'k1', 'w142')['admit'])
           and not any(a[0].startswith('validation active') for a in ent(BASE / 'k1', 'v142')['admit']))
ok &= case('v1a a "no validation layer:" line -> W not admitted', fails('v1a', 'W admitted',
           w_lines=w_lines(pre=(VF, 'no validation layer: VK_LAYER_KHRONOS_validation'))))
ok &= case('v1b no VK_EXT_validation_features line -> W not admitted', fails('v1b', 'W admitted', w_lines=w_lines(pre=())))
ok &= case('v1c no [Vulkan][ line -> W not admitted', fails('v1c', 'W admitted', w_lines=w_lines(post=())))
ok &= case('v1d another extension of the layer only -> W not admitted', fails('v1d', 'W admitted', w_lines=w_lines(
           pre=('VK_LAYER_KHRONOS_validation available extension: VK_EXT_debug_utils, version = 1',))))
ok &= case('v1e "no validation layer:" in the W stdout -> W not admitted', fails('v1e', 'W admitted', w_std=[
           'no validation layer: VK_LAYER_KHRONOS_validation']))
v, w = pair('v1f', w_lines=W_BASE, w_std=[VF, VW])
ok &= case('v1f the layer lines in the W stdout count -> admitted, YES', S.scene_ok(v, w, 'viewed')[0] == 'YES'
           and w['val']['ok'])
ok &= case('v1g exactly one layer line and one [Vulkan][ line (the edges >= 1) -> YES',
           S.scene_ok(*pair('v1g', w_lines=w_lines(post=(VW,))), sheet='viewed')[0] == 'YES')
root = BASE / 'v1h'
mkrun(root, 'v142', scene_lines(SKY, v_post()))
mkrun(root, 'w142', w_lines(), log=False, glitch=None, sheet=False, stdout_lines=[VF, VW])
ok &= case('v1h W without its log -> validation not active even with the stdout lines',
           not ent(root, 'w142')['val']['ok'])
# RC3: the video length and the coverage (item 224 (a)(3))
ok &= case('r1 V video 2 999 frames -> the video row fails (coverage still holds)', fails('r1', 'V video >= 3000 frames',
           v_lines=scene_lines(SKY, [100000] * 3000), v_glitch=(2999, 0)))
ok &= case('r1b V video 3 000 frames -> YES', S.scene_ok(*pair('r1b', v_lines=scene_lines(SKY, [100000] * 3000),
                                                              v_glitch=(3000, 0)), sheet='viewed')[0] == 'YES')
v, w = pair('r2')
ok &= case('r2 the V log carries 3 114 FrameTrace rows', v['rows_total'] == 3114)
ok &= case('r2b V video 3 013 frames against 3 114 rows -> the coverage row fails', fails('r2b', 'V video frames >= FrameTrace',
           v_glitch=(3013, 0)))
ok &= case('r2c V video 3 014 frames against 3 114 rows -> YES', S.scene_ok(*pair('r2c', v_glitch=(3014, 0)),
                                                                          sheet='viewed')[0] == 'YES')
v, w = pair('r3')
Path(BASE / 'r3' / 'glitch_v142.txt').write_text('Traceback (most recent call last):\nValueError: invalid literal\n')
v = ent(BASE / 'r3', 'v142')
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('r3 an unreadable video (s51_vidglitch.py traceback) -> the video, coverage and glitch rows fail, NO',
           word == 'NO' and row_ok(rows, 'V video >= 3000') is False and row_ok(rows, 'V video frames >=') is False
           and row_ok(rows, 'V 0 one-frame') is False)
e = census('r4', LONG, glitch=(100, 0))
out_r = '\n'.join(S.fmt_entry(e))
ok &= case('r4 census: a failed coverage prints "glitches not conclusive" and does not change the outcome',
           e['outcome'] == 'HOLDS_120' and 'NO - glitches not conclusive' in out_r and not e['cover'])
root = BASE / 'r5'
mkrun(root, 'c142_01', scene_lines(LV, LONG))
(root / 'rec_c142_01.mp4.idx').write_bytes(b'0 1 0.10\n1 2 0.12\nbad line\n2 3 0.15\n')
e = ent(root, 'c142_01')
out_r = '\n'.join(S.fmt_entry(e))
ok &= case('r5 .idx records are counted (lines of >= 3 fields) and printed with the video and FrameTrace counts',
           e['idx'] == 3 and 'video: frames 3200, .idx records 3, FrameTrace rows in all %d, after the first scene frame %d'
           % (e['rows_total'], e['derive']['frames_after_first']) in out_r)
ok &= case('r5b without the .idx file the record count is None', ent(BASE / 'r4', 'c142_01')['idx'] is None)
# RC4: HOLDS_120 only with a stable attempt; the attempt row of V (item 224 (a)(4))
e = census('h1', LONG, js=js_for('c142_01', attempt=dict(ft_tail=None, hold_s=None, outcome='timeout')))
ok &= case('h1 (replaces o7b) a timeout of enter_scene with 120 s shown -> NOT_EVALUABLE, no stable (timeout)',
           e['outcome'] == 'NOT_EVALUABLE' and e['reason'] == 'no stable (timeout)' and not e['tail_stall'])
e = census('h2', LONG, js=js_for('c142_01', attempt=dict(hold_s=119.9)))
ok &= case('h2 hold_s 119.9 -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE' and e['reason'].startswith('hold_s'))
e = census('h2b', LONG, js=js_for('c142_01', attempt=dict(hold_s=120.0)))
ok &= case('h2b hold_s 120.0 -> HOLDS_120', e['outcome'] == 'HOLDS_120')
e = census('h2c', LONG, js=js_for('c142_01', attempt=dict(hold_s=None)))
ok &= case('h2c attempt ok without hold_s -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
ok &= case('h3 V timeout (no hold) -> the V attempt row fails', fails('h3', 'V attempt ok',
           v_js=js_for('v142', attempt=dict(outcome='timeout', hold_s=None))))
ok &= case('h4 V hold_s 329.9 -> the V attempt row fails', fails('h4', 'V attempt ok',
           v_js=js_for('v142', attempt=dict(hold_s=329.9))))
v, w = pair('h5', v_es=['WARNING: the game ENDED inside the hold after 9.0 s, returncode 1 (0x00000001)'])
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('h5 V ENDED line -> the attempt and death rows fail, NO', word == 'NO' and row_ok(rows, 'V attempt ok') is False
           and row_ok(rows, 'V 0 death markers') is False)
# RC5: the sheet file and its sha (item 224 (a)(5))


def sheet_case(name, act):
    v, w = pair(name)
    act(BASE / name)
    v = ent(BASE / name, 'v142')
    word, rows = S.scene_ok(v, w, 'viewed')
    return word, row_ok(rows, 'V sheet file'), S.scene_ok(v, w, None)[0]


TP = 'step2/times.txt'
res = sheet_case('s1', lambda r: (r / 'sheet_v142.png').unlink())
ok &= case('s1 viewed without sheet_v142.png -> NO; unset -> PENDING_SHEET (by the letter)', res == ('NO', False, 'PENDING_SHEET'))
res = sheet_case('s2', lambda r: (r / 'sheet_v142.png').write_bytes(b''))
ok &= case('s2 an empty sheet -> NO', res[:2] == ('NO', False))
res = sheet_case('s3', lambda r: (r / 'sheet_v142.png').write_bytes(b'another png'))
ok &= case('s3 a sheet whose sha is not the times.txt line -> NO', res[:2] == ('NO', False))
res = sheet_case('s4', lambda r: (r / 'rec_v142.mp4').write_bytes(b'another video'))
ok &= case('s4 a video whose sha is not the times.txt line -> NO', res[:2] == ('NO', False))
res = sheet_case('s5', lambda r: (r / TP).unlink())
ok &= case('s5 no step2/times.txt -> NO', res[:2] == ('NO', False))


def s6(r):
    (r / 'rec_v142.mp4').unlink()
    keep = [l for l in (r / TP).read_text().splitlines(True) if 's51_vidglitch' not in l]
    (r / TP).write_text(''.join(keep))


res = sheet_case('s6', s6)
ok &= case('s6 no video and no video line -> NO', res[:2] == ('NO', False))


def s7(r):
    (r / 'sheet_v142.png').write_bytes(b'')
    keep = [l for l in (r / TP).read_text().splitlines(True) if ' sheet rc ' not in l]
    (r / TP).write_text(''.join(keep))


res = sheet_case('s7', s7)
ok &= case('s7 an empty sheet and no sheet line -> NO', res[:2] == ('NO', False))


def s8(r):
    lines = (r / TP).read_text().splitlines(True)
    (r / TP).write_text(''.join(l.replace('sha256 ', 'sha256 0') for l in lines) + ''.join(lines))


res = sheet_case('s8', s8)
ok &= case('s8 the last matching times.txt lines count (a stale line before them) -> YES', res[:2] == ('YES', True))


def s9(r):
    lines = (r / TP).read_text().splitlines(True)
    (r / TP).write_text(''.join(lines) + ''.join(l.replace('sha256 ', 'sha256 f', 1) if ' sheet rc ' in l else l
                                                 for l in lines if ' sheet rc ' in l))


res = sheet_case('s9', s9)
ok &= case('s9 a later sheet line with another sha -> NO', res[:2] == ('NO', False))
# RC6: W ft_tail > 0 (item 224 (a)(6))
ok &= case('w1 W ft_tail 0 -> the W ft_tail row fails', fails('w1', 'W ft_tail > 0', w_js=js_for('w142', attempt=dict(ft_tail=0))))
ok &= case('w2 W ft_tail None -> the W ft_tail row fails', fails('w2', 'W ft_tail > 0',
           w_js=js_for('w142', attempt=dict(ft_tail=None))))
ok &= case('w3 W ft_tail 1 -> YES', S.scene_ok(*pair('w3', w_js=js_for('w142', attempt=dict(ft_tail=1))), sheet='viewed')[0] == 'YES')
# RC7: a scene change after the entry line (item 224 (a)(7))


def changed(name, change, before=100, after=(2000000, 16667), **kw):
    lines = scene_lines(LV, [16667] * before) + [change] + [ft(15 + before + i, dt) for i, dt in enumerate(after)]
    return census(name, None, lines=kw.pop('lines_extra', lambda l: l)(lines), **kw)


e = changed('q1', start('volcano_mountain'))
ok &= case('q1 another level started after the entry -> NOT_EVALUABLE scene change; the 2 s row after it is not K2, printed apart',
           e['outcome'] == 'NOT_EVALUABLE' and e['reason'] == 'scene change' and e['derive']['k2'] == []
           and e['derive']['other_starts'] == [('volcano_mountain', 114)] and e['derive']['after_change'] ==
           dict(rows=2, dt_us=2016667, k2=1) and e['derive']['frames_after_first'] == 100)
ok &= case('q2 the same level started again -> NOT_EVALUABLE', changed('q2', start(LV))['outcome'] == 'NOT_EVALUABLE')
ok &= case('q3 an empty name started -> NOT_EVALUABLE', changed('q3', 'GuestOut: Level has started: ')['outcome'] == 'NOT_EVALUABLE')
e = changed('q4', start('volcano_mountain'), lines_extra=lambda l: l[:40] + [ft(99, 1000000)] + l[40:])
ok &= case('q4 a K2 frame before the change -> K2', e['outcome'] == 'K2' and e['reason'] == 'frame dt >= 1 s before the scene change')
e = changed('q5', start('volcano_mountain'), lines_extra=lambda l: l[:40] + ['--- Error ---'] + l[40:] + ['GpuHangAbort: x'])
ok &= case('q5 a log crash before the change -> K1 (the hang after it does not decide)', e['outcome'] == 'K1')
e = changed('q5c', start('volcano_mountain'), lines_extra=lambda l: l[:40] + ['GpuHangAbort: x', '--- Error ---'] + l[40:])
ok &= case('q5c two log markers before the change: the first (hang) decides -> K2', e['outcome'] == 'K2')
e = changed('q10', start('volcano_mountain'), after=(16667, 1000000, 16667), lines_extra=lambda l: l + [start('voxel_world')])
ok &= case('q10 two changes: the first one cuts (a 1 s row between them is not classified) -> NOT_EVALUABLE',
           e['outcome'] == 'NOT_EVALUABLE' and [x[0] for x in e['derive']['other_starts']] == ['volcano_mountain', 'voxel_world'])
e = changed('q5b', start('volcano_mountain'), lines_extra=lambda l: l + ['GpuHangAbort: requested=1'])
ok &= case('q5b a log marker only after the change -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
e = changed('q6', start('volcano_mountain'), stdout_lines=['--- Fatal Error ---'])
ok &= case('q6 a stdout marker with a change -> NOT_EVALUABLE (stdout is after the log)', e['outcome'] == 'NOT_EVALUABLE')
e = changed('q6b', start('volcano_mountain'), js=js_for('c142_01', attempt=dict(hold_exit=1, ft_tail=0)))
ok &= case('q6b hold_exit and tail stall with a change -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
e = changed('q6c', start('volcano_mountain'), js=js_for('c142_01', attempt=dict(outcome='exited', hold_s=None)))
ok &= case('q6c exited with a change -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
out_q = '\n'.join(S.fmt_entry(changed('q7', start('volcano_mountain'))))
ok &= case('q7 the change is printed with the name and the last n before it', "[('volcano_mountain', 114)]" in out_q
           and 'rows after it 2' in out_q)
ok &= case('q8 V with a later start -> the V change row fails', fails('q8', 'V no scene change',
           v_lines=scene_lines(SKY, v_post()) + [start(SKY)]))
ok &= case('q8b W with a later start -> the W change row fails', fails('q8b', 'W no scene change',
           w_lines=W_LINES + ['GuestOut: Level has started: ']))
e = changed('q9', start('volcano_mountain'))
ok &= case('q9 the sum after the entry line stops at the change', e['derive']['dt_after_entry_us'] == 1500000 + 20000 +
           2000000 + 16667 * 100)
# RC8: an attempt without json; the emulator stdout missing (item 224 (a)(8))
root = BASE / 'j1'
mkrun(root, 'c142_01', [ft(i, 16667) for i in range(1, 50)], js=js_for('c142_01', attempt=dict(outcome='timeout')))
(root / 'attempt_c142_02.txt').write_text('made\n')
mkrun(root, 'c142_03', [ft(i, 16667) for i in range(1, 50)], js=js_for('c142_03', attempt=dict(outcome='timeout')))
mkrun(root, 'c142_04', [ft(i, 16667) for i in range(1, 50)], js=js_for('c142_04', attempt=dict(outcome='timeout')))
PRJ = root / 'pred.md'
PRJ.write_text('fixture\n', encoding='utf-8')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rj = S.main(['--tag', 'c142_02'], root=str(root), pred=str(PRJ))
    rj2 = S.main(['--tag', 'c142_05'], root=str(root), pred=str(PRJ))
    rj3 = S.main(['--stop-check', 'c142_05'], root=str(root), pred=str(PRJ))
    S.main(['--summary'], root=str(root), pred=str(PRJ))
out_j = buf.getvalue()
ok &= case('j1 --tag of an attempt without json -> ATTEMPT MADE, NO JSON (instrument), rc 1; without the marker NO_RUN',
           rj == 1 and 'TAG c142_02: ATTEMPT MADE, NO JSON (instrument)' in out_j and rj2 == 1 and 'TAG c142_05: NO_RUN' in out_j)
ok &= case('j2 summary: the attempt without json in the tag list and the census map, made 4 (1 without json), not admitted',
           'TAG c142_02: ATTEMPT MADE, NO JSON (instrument)' in out_j and
           'c142_02 big_hand_pirate_island ATTEMPT MADE, NO JSON (instrument) - not admitted' in ' '.join(out_j.split()) and
           'CENSUS made 4 of 10 (of them attempt made without json 1)' in out_j)
ok &= case('j3 the stop rule: not entered, no json, not entered, not entered -> no stop (--stop-check rc 0, summary not met)',
           rj3 == 0 and 'STOP RULE before c142_05: not met' in out_j and 'STOP RULE (item 221 (g)(4)): not met' in out_j)
root = BASE / 'j4'
mkrun(root, 'c142_01', scene_lines(LV, LONG))
(root / 'stdout_c142_01.txt').unlink()
e = ent(root, 'c142_01')
ok &= case('j4 census without the emulator stdout -> printed MISSING', not e['stdout_present'] and
           'emulator stdout: MISSING' in '\n'.join(S.fmt_entry(e)))
v, w = pair('j5')
(BASE / 'j5' / 'stdout_v142.txt').unlink()
ok &= case('j5 V without the emulator stdout -> the V stdout row fails', row_ok(S.scene_ok(ent(BASE / 'j5', 'v142'), w,
           'viewed')[1], 'V emulator stdout present') is False)
v, w = pair('j6')
(BASE / 'j6' / 'stdout_w142.txt').unlink()
ok &= case('j6 W without the emulator stdout -> the W stdout row fails', row_ok(S.scene_ok(v, ent(BASE / 'j6', 'w142'),
           'viewed')[1], 'W emulator stdout present') is False)
# RC9: n gaps after the first scene frame; torn lines (item 224 (a)(9))


def shifted(k):
    """V lines with every post row from index k on renumbered +1 (one gap, the dt sum unchanged)."""
    lines = scene_lines(SKY, v_post())
    i0 = lines.index(ft(14, 2000000, 894)) + 1
    for j in range(i0 + k, len(lines)):
        p = lines[j].split(' ', 2)
        lines[j] = 'FrameTrace: n=%d %s' % (int(p[1][2:]) + 1, p[2])
    return lines


ok &= case('g1 V one n gap after the first scene frame -> the gap row fails', fails('g1', 'V n gaps', v_lines=shifted(1500)))
ok &= case('g2 a gap before the first scene frame is not counted -> YES', S.scene_ok(*pair('g2', v_lines=scene_lines(
           SKY, v_post(), pre=[ft(12, 1500000, 20), ft(40, 20000, 99)])), sheet='viewed')[0] == 'YES')
e = census('g3', None, lines=scene_lines(LV, LONG) + ['FrameTrace: n=77 dt_', 'FrameTrace: n=78 dt_us=16667 lat_us=1'])
ok &= case('g3 a torn FrameTrace line is counted and printed', e['torn'] == 1 and 'torn FrameTrace lines 1' in
           '\n'.join(S.fmt_entry(e)))
# RC10: the second reading by the order; the info line of W beside V (item 224 (a)(2), (10))
ok &= case('f1 the forms by the order: first five B5a 1/5 B5 2/5, last five B5a 1/5 B5 0/5',
           'first five B5a 1/5 B5 2/5; last five B5a 1/5 B5 0/5' in out3)
ok &= case('f2 the summary prints the dt median and max of V and W', 'info dt_us after the first scene frame: V median 96774 '
           'max 97374; W median 150000 max 150000; W presented 300.0 s over 2000 frames' in out2)
# item 224 (b)(2): the check lines on synthetic device-lost and validation logs
cb = BASE / 'cb'


def cb_run(tag, lines, std=()):
    mkrun(cb, tag, lines, stdout_lines=std, glitch=None, sheet=False, js=js_for('c142_01', attempt=dict(hold_exit=321)))


cb_run('q1', scene_lines(LV, LONG) + ['vkQueueSubmit failed: ErrorDeviceLost (-4)', '--- Fatal Error ---'])
cb_run('q2', scene_lines(LV, LONG) + ['GpuHangAbort: requested=1', '--- Error ---'])
cb_run('q3', scene_lines(LV, LONG) + ['--- Fatal Error ---', 'vkQueueSubmit failed: ErrorDeviceLost (-4)'])
(cb / 'qv.txt').write_bytes(('\n'.join([VF, VW, VW]) + '\n').encode())
(cb / 'qn.txt').write_bytes(('\n'.join([VF, 'no validation layer: x', VW]) + '\n').encode())
S.CHECK_K2 = (('q1', str(cb)), ('q2', str(cb)))
S.CHECK_VAL = ('qv', str(cb / 'qv.txt'), str(cb / 'none.txt'))
n1b, t1b, l1b = S.checks1b()
ok &= case('b1 check lines: device lost and hang before the crash -> K2, validation active -> 3 of 3',
           (n1b, t1b) == (3, 3) and l1b[-1] == 'CHECK1B 3 of 3')
S.CHECK_K2 = (('q1', str(cb)), ('q3', str(cb)))
S.CHECK_VAL = ('qn', str(cb / 'qn.txt'), str(cb / 'none.txt'))
n1b, t1b, l1b = S.checks1b()
ok &= case('b2 a crash before the device lost and a "no validation layer" line -> 1 of 3', (n1b, t1b) == (1, 3))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rb2 = S.main(['--check1b'])
    S.CHECK_K2 = (('q1', str(cb)), ('q2', str(cb)))
    S.CHECK_VAL = ('qv', str(cb / 'qv.txt'), str(cb / 'none.txt'))
    rb1 = S.main(['--check1b'])
ok &= case('b3 main --check1b: rc 1 on a failed check, rc 0 on 3 of 3', rb2 == 1 and rb1 == 0)
try:
    (out_n + out_r + out_q + out_j + buf.getvalue()).encode('cp1250', errors='strict')
    enc = True
except UnicodeError:
    enc = False
ok &= case('m6b the new printed lines are ASCII (strict cp1250)', enc)
