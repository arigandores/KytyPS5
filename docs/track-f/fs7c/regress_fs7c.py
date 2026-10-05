"""FS7c (HPP-567): regression of fs7c_read.py on real logs - F19e b24_h1 (form of fs7_h, binary 9b00ad40) and F18e f8_n1 (form of fs7_n,
binary 35c4a754).  The rows of the forms must give the numbers of the lead's recount (ROADMAP s122 item 487 (b), item 467 (b)); the rows
those binaries cannot pass (FS7 identity, FixF8/FixB4 or FixB24 lines, FS6 installed) must be NO.  Read-only.
usage: python regress_fs7c.py   (ASCII only; ends with ALL OK)"""
import hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs7c_read.py')
sys.path.insert(0, HERE)
import fs7c_read as R

print('suite regress_fs7c.py sha256 %s target fs7c_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(open(TARGET, 'rb').read()).hexdigest()))
N = [0]
FAIL = []


def check(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    if not cond:
        FAIL.append(name)


def src(root, tag):
    d = os.path.join(root, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in ('installed_sha', 'installed_before', 'installed_after', 'warm', 'manifest_cmp',
                                                        'glitch', 'sheet'))
    p.update(log=os.path.join(root, 'log_%s.txt' % tag), stdout=os.path.join(root, 'stdout_%s.txt' % tag),
             run=os.path.join(root, '%s.json' % tag), idx=os.path.join(root, 'rec_%s.mp4.idx' % tag),
             seal=os.path.join(root, 'pred', os.path.basename(root) + '_seal.md'), bin=R.BIN_PATH)
    return p


def row(res, prefix, sub):
    for name, val in res[prefix]:
        if sub in name:
            return val
    raise KeyError(sub)


h = R.read('fs7_h', src('C:/kyty/f287/f19e', 'b24_h1'))
check('h log sha256 = F19e artefact f95af1e8 (b24_h1)', h['log_sha256'].startswith('f95af1e8'))
s = h['stat'] or {}
check('h main_late_max_us 3000289', s.get('main_late_max_us') == 3000289)
check('h po_wait_max_us 2973393', s.get('po_wait_max_us') == 2973393)
check('h pad_wait_max_us 10', s.get('pad_wait_max_us') == 10)
check('h guest_sdl 0, po_applied 186', s.get('guest_sdl') == 0 and s.get('po_applied') == 186)
check('h frames >= 1 s in the wide window 0', h['k2_wide'] == [])
for sub in ('main_late_max_us', 'po_wait_max_us', 'pad_wait_max_us', 'guest_sdl', 'stand window', 'FixB24'):
    check('h member %s YES' % sub, row(h, 'mem', sub) is True)
check('h member FixF8 NO (F19c binary has no F8 default)', row(h, 'mem', 'FixF8') is False)
check('h member FixB4 NO (base S12a)', row(h, 'mem', 'FixB4') is False)
check('h all harm rows YES (video 10121)', all(v is True for _, v in h['harm']) and '10121' in [n for n, _ in h['harm'] if 'video' in n][0])
check('h all identity rows YES', all(v is True for _, v in h['ident']))
check('h stand admission rows YES', all(v is True for n, v in h['adm'] if not n.startswith(('binary', 'version', 'revision', 'pre-reg', 'env'))))
check('h binary/revision/env admission NO', all(v is False for n, v in h['adm'] if n.startswith(('binary', 'revision', 'env'))))
check('h version row reads the FS7 file itself - YES', row(h, 'adm', 'version string') is True)
check('h form: installed before/after NO (adb0c82f), manifest YES', [v for _, v in h['form']] == [False, False, True])
check('h reading NOT_ADMITTED', h['word'] == 'NOT_ADMITTED')
check('h exit row close_rc 0', 'close_rc 0' in h['exit'])

n = R.read('fs7_n', src('C:/kyty/f287/f18e', 'f8_n1'))
check('n log sha256 = F18e artefact 402b6f6e (f8_n1)', n['log_sha256'].startswith('402b6f6e'))
check('n F8 lines 0', n['f8'] == 0)
check('n max init_calls 1', n['max_init'] == 1)
check('n last acq 285', (n['last_astat'] or {}).get('acq') == 285)
check('n AudioStat rows 856', n['astat_rows'] == 856)
check('n FixF8 line 11488 before the first GuestOut 12803 (N4 row)', n['n4_row'] == (11488, 12803))
for sub in ('F8 lines', 'init_calls <= 1', 'acq >= 250', 'status in', 'FixF8', 'TestHidLoss'):
    check('n member %s YES' % sub, row(n, 'mem', sub) is True)
check('n member FixB4 NO (base S12a)', row(n, 'mem', 'FixB4') is False)
check('n member FixB24 NO (F18c binary)', row(n, 'mem', 'FixB24') is False)
check('n harm frame max 182589 and video 25725, all harm YES', all(v is True for _, v in n['harm']) and
      '182589' in [x for x, _ in n['harm'] if 'frames' in x][0] and '25725' in [x for x, _ in n['harm'] if 'video' in x][0])
check('n vibration admission rows YES', all(v is True for x, v in n['adm'] if x.startswith(('line AudioOut', 'lines Haptics', 'A >= 1',
                                                                                         'lines TestAudioLoss', 'no interference'))))
check('n reading NOT_ADMITTED', n['word'] == 'NOT_ADMITTED')
print('checks %d failed %d' % (N[0], len(FAIL)))
if FAIL:
    sys.exit(1)
print('ALL OK')
