"""Track S, link S12c (HPP-496): the regression of s12/sc_s12.py on real logs (read only, streams in binary mode, ASCII output).
  FS5c (HPP-511) fs5_w  - the W rows on a real W log of the same FS5 tree: [Vulkan][E] 0, [Vulkan][W] > 0, limit lines 0, DualSrcBlend
                          supported=1 enabled=1 before the first GuestOut, hold >= 300 s, 0 frames >= 1 s (the reader of FS5c printed
                          [E] 0, [W] 930 253, DualSrcBlend (76, 1, 1), hold 324.2 s);
  FS5c fs5_v            - the V rows: hold 334.3 s, 0 frames >= 1 s, 0 death markers;
  S10 pi_w1 / pi_r1     - the cache classes: pi_w1 24 saved lines, the last 94 435 637, forced 23 (KYTY_S_PCW_FORCE_MS=15000; the last save, at the exit, is not forced); pi_r1
                          one loading, one loaded 94 435 637, 0 bad classes; the knob line of pi_r1 'S-pcw: KYTY_S_PCW=1
                          KYTY_S_PCW_FORCE_MS=15000' (ROADMAP item 408 (b): 24 saves, loaded 94 435 637 = the last save);
  S10 t2_1              - the data line of item 414 (g)(2): one held frame of 280 351 us of class PCW (AUDIT_S3 MINOR-2: t2_1 280 351 us,
                          class PCW by item 241 (v)(3)); no "AvTrace: pcw recipes" line (KYTY_S_PCW=0 arm) -> NOT_EVALUABLE.
usage: python regress_s12.py [<sc_s12 under test>]   (prints the sha256 of every log; ends with ALL OK)"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc_s12.py')
spec = importlib.util.spec_from_file_location('sc_s12_regress', SRC)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
print('regress_s12.py sha256 %s target sc_s12.py sha256 %s' % (hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
                                                               S.sha_file(SRC)))
F = 'C:/kyty/f287/fs5/fs5c'
T = 'C:/kyty/s288/s10'
ok = True


def chk(name, cond, detail):
    global ok
    ok &= bool(cond)
    print('%s %s (%s)' % ('PASS' if cond else 'FAIL', name, detail))


w = S.scan(F + '/log_fs5_w.txt', S.SKY)
wo = S.scan_stdout(F + '/stdout_fs5_w.txt')
print('log %s sha256 %s lines %d' % (F + '/log_fs5_w.txt', w['sha256'], w['lines']))
dual = any(s == 1 and e == 1 and ln < w['guest_first'] for ln, s, e in w['dual'])
chk('fs5_w W rows', w['vke'] == 0 and wo['vke'] == 0 and w['vkw'] == 930253 and w['vk_limit'] == 0 and dual,
    'E %d/%d W %d limit %d dual %s guest_first %s' % (w['vke'], wo['vke'], w['vkw'], w['vk_limit'], w['dual'][:1], w['guest_first']))
chk('fs5_w hold and frames >= 1 s', round(w['hold_us'] / 1e6, 1) == 324.2 and w['k2_after'] == 0 and not w['death'] + wo['death'],
    'hold %.1f k2 %d death %d' % (w['hold_us'] / 1e6, w['k2_after'], len(w['death'] + wo['death'])))
v = S.scan(F + '/log_fs5_v.txt', S.SKY)
vo = S.scan_stdout(F + '/stdout_fs5_v.txt')
print('log %s sha256 %s lines %d' % (F + '/log_fs5_v.txt', v['sha256'], v['lines']))
chk('fs5_v V rows', round(v['hold_us'] / 1e6, 1) == 334.3 and v['k2_after'] == 0 and not v['death'] + vo['death'] and v['first_scene_n'] == 360,
    'hold %.1f k2 %d first %s' % (v['hold_us'] / 1e6, v['k2_after'], v['first_scene_n']))
chk('fs5_v the knob line of FS5 (S-pcw default 0 there)', v['spcw'] == ['S-pcw: KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=0'], v['spcw'][:2])
pw = S.scan(T + '/log_pi_w1.txt', S.SKY)
print('log %s sha256 %s lines %d' % (T + '/log_pi_w1.txt', pw['sha256'], pw['lines']))
chk('pi_w1 saves', len(pw['saved']) == 24 and pw['saved'][-1] == 94435637 and pw['forced'] == 23 and pw['vc']['save failed'] == 0,
    'saved %d last %s forced %d' % (len(pw['saved']), pw['saved'][-1] if pw['saved'] else None, pw['forced']))
pr = S.scan(T + '/log_pi_r1.txt', S.SKY)
print('log %s sha256 %s lines %d' % (T + '/log_pi_r1.txt', pr['sha256'], pr['lines']))
chk('pi_r1 load classes', pr['vc']['loading'] == 1 and pr['loaded'] == [94435637] and all(pr['vc'][c] == 0 for c in S.LOAD_BAD)
    and pr['vc_unknown'] == 0, 'loading %d loaded %s bad %s unknown %d' % (pr['vc']['loading'], pr['loaded'],
                                                                            [pr['vc'][c] for c in S.LOAD_BAD], pr['vc_unknown']))
chk('pi_r1 knob line', pr['spcw'] == ['S-pcw: KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=15000'], pr['spcw'][:2])
chk('pi_r1 loaded = the last saved of pi_w1 = snap0 size - 76', pr['loaded'][0] == pw['saved'][-1] == S.SNAP_BIN_SIZE - S.BLOB_PREFIX,
    '%s %s %s' % (pr['loaded'][0], pw['saved'][-1], S.SNAP_BIN_SIZE - S.BLOB_PREFIX))
t = S.scan(T + '/log_t2_1.txt', 'hero_kratos')
print('log %s sha256 %s lines %d' % (T + '/log_t2_1.txt', t['sha256'], t['lines']))
h = S.held_data(T + '/log_t2_1.txt', T + '/stdout_t2_1.txt', 'hero_kratos')
print('t2_1 held: %s' % S.fmt_held(h))
print('t2_1 recipes: %s' % S.fmt_rec(t['rec']))
chk('t2_1 one held frame of 280 351 us of class PCW (AUDIT_S3 MINOR-2)', h is not None and
    [(x['dt_ms'], x['cls']) for x in h['rows']] == [(280.4, 'PCW')] and h['rows'][0]['rsave'], h and h['rows'][:2])
chk('t2_1 no pcw recipes line (KYTY_S_PCW=0) -> NOT_EVALUABLE', S.fmt_rec(t['rec']).startswith('NOT_EVALUABLE'), len(t['rec']))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
