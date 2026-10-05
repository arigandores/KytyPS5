"""Track F link FS8e (HPP-575; ROADMAP s122 item 471 (g)(5), items 544 (g), 545 (v)-(g)): the reader of the warm-up tag fs8_i - V Sky Garden
of the form fs8_v on the INSTALLED FS8 2c9b69b9 (installed by FS8d at 2026-10-05 11:39:58Z), the caches NOT returned after the tag.
usage: python fs8e_read.py fs8_i [--json <out.json>]
       python fs8e_read.py --dir <fixture dir>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt,
           installed_sha.txt, cold.txt, warm.txt, seal.md, bin.exe)
The scanning functions are imported from C:/kyty/f287/fs8c/fs8c_read.py (FS8c HPP-573, sealed sha256 in the seal of this link) without a
change: the members of fs8_v keep their definitions (seal docs/track-f/fs8c.md section 4).  Port of C:/kyty/f287/fs5/fs5e/fs5e_read.py
(FS5e HPP-513).  Differences from the kind v of FS8c:
  binary          installed_before.txt (inside the lock before the tag) = installed_sha.txt (right before enter_scene) = json binary_sha256 =
                  2c9b69b9...: the tag runs the installed FS8, nothing is copied in (member); identification by N1 of item 530 (g) / 545 (v):
                  the version string ...-1889-g302347b4 in the installed binary file and every revision text of the log / stdout = 302347b
                  (SDL_REVISION never read) - members.
  caches          not copied and not returned (item 471 (g)(5)): no manifest rows; the manifests before / after are reference in the go script.
  warm form       warm.txt (written by go_fs8e.sh after the run) says 'pipelines.bin present size <n>' with n > 0 for
                  variant_fixb26_fixb1b_fixf10_fixf19 (member: the purpose of the warm-up).
  cold form       reference only (cold.txt 'absent').
Verdict (the go script acts on it inside the lock):
  WARMUP VERDICT fs8_i: PASS          every member YES -> the install stays.
  WARMUP VERDICT fs8_i: INTERFERENCE  an interference row NO (window minimized / Recovering Vulkan swapchain / GamePatch line; the
                                      environment or command line not of the form fs8_v; json prereg != sha256 of the seal) -> not read as
                                      an outcome; the install stays (the binary passed FS8c), question to the lead (variant of the
                                      executor, seal section 2).
  WARMUP VERDICT fs8_i: FAIL          otherwise (a member NO or NOT_DETERMINED) -> rollback by the copy 8df61c00 inside the lock (item 544 (g)),
                                      question to the lead.
ASCII output only."""
import json, os, re, sys

FS8C = 'C:/kyty/f287/fs8c'
sys.path.insert(0, FS8C)
import fs8c_read as C  # noqa: E402

G = 'C:/kyty/f287/fs8e'
TAG = 'fs8_i'
FORM = 'fs8_v'
LEVEL = C.SKY
HOLD = C.SPEC[FORM]['hold']
BIN_EXPECT = C.BIN_EXPECT
VERSION = C.VERSION
REV = C.REV
DIR_FIX = C.DIR_FIX
INSTALLED = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'
SEAL_PATH = 'C:/kyty/f287/fs8e/pred/fs8e_seal.md'
RX_WARM = re.compile(r'pipelines\.bin present size (\d+)')


def paths(base=None):
    names = ('installed_sha', 'installed_before', 'cold', 'warm', 'glitch', 'sheet')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=os.path.join(base, 'bin.exe'))
        return p
    d = os.path.join(G, 'runs', TAG)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % TAG), stdout=os.path.join(G, 'stdout_%s.txt' % TAG), run=os.path.join(G, '%s.json' % TAG),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % TAG), seal=SEAL_PATH, bin=INSTALLED)
    return p


def read(p):
    r = C.scan(p['log'], LEVEL)
    sd, srev, ssha = C.stdout_scan(p['stdout'])
    rj = C.text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0]
    sha = C.first_line(C.text(p['installed_sha'])) or None
    sha_b = C.first_line(C.text(p['installed_before'])) or None
    cold_t = C.text(p['cold'])
    warm_t = C.text(p['warm'])
    mw = RX_WARM.search(warm_t or '')
    warm_size = int(mw.group(1)) if mw else None
    idx_n = None
    if p.get('idx') and os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as f:
            idx_n = sum(1 for _ in f)
    gl = None
    gt = C.text(p['glitch'])
    if gt:
        m = C.RX_GL.search(gt)
        gl = int(m.group(1)) if m else None
    st = C.text(p['sheet'])
    sheet = next((x.strip() for x in st.split('\n') if x.startswith('sheet: ')), None) if st else None
    stc = r['stc']
    rev = r['rev'] + srev
    death = r['death'] + (sd or [])
    env_ok, env_info = C.env_admit(FORM, run)
    seal_sha = C.sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    ended_ok = None
    if run is not None:
        ended_ok = (att.get('outcome') == 'ok' and att.get('hold_exit') is None and att.get('hold_s') is not None
                    and att.get('hold_s') >= HOLD)
    return dict(tag=TAG, level=LEVEL, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha,
                stdout_present=sd is not None, rev=rev[:6], rev_ok=bool(rev) and all(t in (REV, VERSION.decode()) for _, _, t in rev),
                json_binary=(run or {}).get('binary_sha256'), installed_sha=sha, installed_before=sha_b,
                sha_ok=sha == BIN_EXPECT and sha_b == BIN_EXPECT and (run or {}).get('binary_sha256') == BIN_EXPECT,
                version_in_bin=C.has_bytes(p['bin'], VERSION), prereg=pre, seal_sha=seal_sha, prereg_ok=bool(pre) and pre == seal_sha,
                env_ok=env_ok, env_info=env_info, stc=stc,
                fixf19_ok=len(stc) >= 1 and all(s.replace('/', '\\').endswith('\\' + DIR_FIX) for s in stc),
                cold_txt=(cold_t or '').strip()[:200], cold_ok=bool(cold_t) and 'absent' in cold_t and 'present' not in cold_t,
                warm_txt=(warm_t or '').strip()[:200], warm_size=warm_size, warm_ok=warm_size is not None and warm_size > 0,
                fixl=r['fixl'], first_guest=r['first_guest'], fb4=C.fix_member(r['fixl']['B4'], r['first_guest']),
                ff8=C.fix_member(r['fixl']['F8'], r['first_guest']), ff8v=C.fix_member(r['fixl']['F8'], r['first_guest'], order=False),
                fb24=C.fix_member(r['fixl']['B24'], r['first_guest']),
                attempt=dict((k, att.get(k)) for k in ('outcome', 'detail', 'hold_exit', 'hold_s', 'stable_s', 'close_rc', 'close_killed')),
                ended_ok=ended_ok, entry_line=r['entry_line'], scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'],
                hold_us=r['hold_us'], hold_s=round(r['hold_us'] / 1e6, 2), k2_after=r['k2_after'], dt_max_after=r['dt_max_after'],
                ft_rows=r['ft_rows'], death=death, skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'],
                gamepatch=r['gamepatch'], quit_line=r['quit_line'], idx_records=idx_n, glitches=gl, sheet=sheet)


def members(res):
    mem = [('binary: installed before the tag = binary of the tag = json binary_sha256 = 2c9b69b9 (installed FS8)', res['sha_ok']),
           ('version string ...-1889-g302347b4 in the installed binary file (N1)', None if res['version_in_bin'] is None
            else bool(res['version_in_bin'])),
           ('every revision text of the log and stdout = %s (N1; SDL_REVISION never read)' % REV, res['rev_ok']),
           ('translation cache directory %s in every line (>= 1 line)' % DIR_FIX, res['fixf19_ok']),
           ('FixB4: mode=1 before the first GuestOut', res['fb4'][0]),
           ('FixF8: mode=1 before the first GuestOut', res['ff8'][0]),
           ('entered (entry line of %s)' % res['level'], res['entry_line'] is not None),
           ('hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= C.HOLD_MIN_US),
           ('the process lived to the end of the hold (outcome ok, hold_exit null, hold_s >= %d)' % HOLD, res['ended_ok']),
           ('0 death markers (log and stdout)', None if not res['stdout_present'] else not res['death']),
           ('video index records >= 3000', (res['idx_records'] or 0) >= C.VIDEO_MIN),
           ('0 one-frame glitches', None if res['glitches'] is None else res['glitches'] == 0),
           ('sheet for the lead made', res['sheet'] is not None),
           ('warm form after the tag: %s/pipelines.bin present, size > 0' % DIR_FIX, res['warm_ok'])]
    ref = [('cold form before the tag: %s absent' % DIR_FIX, res['cold_ok']),
           ('frames >= 1 s after the first scene frame = %d, max dt_us %d (cold entry)' % (res['k2_after'], res['dt_max_after']),
            res['entry_line'] is not None and res['k2_after'] == 0),
           ('FixB24: mode=1 before the first GuestOut', res['fb24'][0]),
           ('FixF8 exactly 1 line mode=1, order not a gate (item 518 (v)(4))', res['ff8v'][0]),
           ('AsyncPipelines: skipped draw lines = %d' % res['skipped_draw'], res['skipped_draw'] == 0)]
    inter = [('window minimized / Recovering Vulkan swapchain / GamePatch line',
              not res['win'].get('minimized') and not res['recovering'] and not res['gamepatch']),
             ('environment and command line of the form fs8_v (no KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS, VK_LAYER_*; KYTY_REC; '
              'validation false; -lvl %s)' % LEVEL, res['env_ok']),
             ('json prereg sha256 = sha256 of the seal file', res['prereg_ok'])]
    return mem, ref, inter


def verdict(res):
    mem, _, inter = members(res)
    if not all(v for _, v in inter):
        return 'INTERFERENCE'
    return 'PASS' if all(v is True for _, v in mem) else 'FAIL'


def rows(res):
    out = ['FS8E %s level %s log sha256 %s lines %d stdout sha256 %s' % (res['tag'], res['level'], res['log_sha256'], res['log_lines'],
                                                                       res['stdout_sha256'])]
    add = out.append
    add('  binary: installed before %s, of the tag %s, json %s (expected %s); version string in the binary %s; revision texts %s'
        % (res['installed_before'], res['installed_sha'], res['json_binary'], BIN_EXPECT, res['version_in_bin'], res['rev']))
    add('  prereg %s seal %s; %s' % (res['prereg'], res['seal_sha'], res['env_info']))
    add('  Shader translation cache lines %d %s; before: %s; after: %s' % (len(res['stc']), res['stc'][:2], res['cold_txt'], res['warm_txt']))
    add('  Fix lines (line, mode): B4 %s F8 %s B24 %s; first GuestOut line %s'
        % (res['fixl']['B4'][:3], res['fixl']['F8'][:3], res['fixl']['B24'][:3], res['first_guest']))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold %.2f s; frames >= 1 s after it %d (max dt_us %d); FrameTrace rows %d'
        % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'], res['k2_after'], res['dt_max_after'],
           res['ft_rows']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; AsyncPipelines: skipped draw %d (reference)'
        % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw']))
    add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    add('  EXIT (report): %s; Event: quit line %s' % (res['attempt'], res['quit_line']))
    mem, ref, inter = members(res)
    for name, val in mem:
        add('  MEMBER %s: %s' % (name, C.yn(val)))
    for name, val in ref:
        add('  REFERENCE %s: %s' % (name, C.yn(val)))
    for name, val in inter:
        add('  INTERFERENCE none: %s: %s' % (name, C.yn(val)))
    add('WARMUP VERDICT %s: %s' % (res['tag'], verdict(res)))
    return out


def main(argv):
    if '--dir' in argv:
        p = paths(argv[argv.index('--dir') + 1])
    else:
        if not argv or argv[0] != TAG:
            raise SystemExit('usage: fs8e_read.py fs8_i [--json <out>] | --dir <fixture dir>')
        p = paths()
    res = read(p)
    res['verdict'] = verdict(res)
    print('\n'.join(C.asc(x) for x in rows(res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
