"""Track F link FS5e (HPP-513; ROADMAP s122 item 410 (g)(5), items 424 (zh), 426): the reader of the warm-up tag fs5_i - V Sky Garden of
the form fs5_v on the INSTALLED FS5 631ff987, the caches NOT returned after the tag.
usage: python fs5e_read.py fs5_i [--json <out.json>]
       python fs5e_read.py --dir <fixture dir>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
           installed_before.txt, installed_sha.txt, cold.txt, warm.txt)
The scanning functions are imported from C:/kyty/f287/fs5/fs5c/fs5c_read.py (FS5c HPP-511, sealed sha256 in the seal of this link)
without a change: the members of fs5_v keep their definitions (seal docs/track-f/fs5c.md section 4).  Differences from the kind v of FS5c:
  binary          installed_before.txt (inside the lock before the tag) = installed_sha.txt (right before enter_scene) = 631ff987...: the tag
                  runs the installed FS5, nothing is copied in (member).
  caches          not copied and not returned (item 410 (g)(5)): no manifest equality rows; the manifests before / after are reference.
  warm form       warm.txt (written by go_fs5e.sh after the run) says 'pipelines.bin present size <n>' with n > 0 for
                  variant_fixb26_fixb1b_fixf10 (member: the purpose of the warm-up).
  cold form       reference only (cold.txt 'absent' and the first PipelinePrecache line 'no ..._fixf10...pipelines.bin yet').
Verdict (the go script acts on it inside the lock):
  WARMUP VERDICT fs5_i: PASS          every member YES -> the install stays.
  WARMUP VERDICT fs5_i: INTERFERENCE  the interference row NO (window minimized / Recovering Vulkan swapchain / GamePatch) -> not read as
                                      an outcome; the install stays (the binary passed FS5c), question to the lead (variant of the
                                      executor, seal section 2).
  WARMUP VERDICT fs5_i: FAIL          otherwise -> rollback by the copy 31cbfee8 inside the lock, question to the lead.
ASCII output only."""
import hashlib, json, os, re, sys

FS5C = 'C:/kyty/f287/fs5/fs5c'
sys.path.insert(0, FS5C)
import fs5c_read as C  # noqa: E402

G = 'C:/kyty/f287/fs5/fs5e'
TAG = 'fs5_i'
LEVEL = C.SKY
BIN_EXPECT = C.BIN_EXPECT
REV = C.REV
DIR_FIX = C.DIR_FIX
RX_WARM = re.compile(r'pipelines\.bin present size (\d+)')


def paths(base=None):
    names = ('installed_sha', 'installed_before', 'cold', 'warm', 'glitch', 'sheet')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'))
        return p
    d = os.path.join(G, 'runs', TAG)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % TAG), stdout=os.path.join(G, 'stdout_%s.txt' % TAG), run=os.path.join(G, '%s.json' % TAG),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % TAG))
    return p


def read(p):
    r = C.scan(p['log'], LEVEL)
    sd, sfail, srev, shashes, ssha = C.stdout_scan(p['stdout'])
    rj = C.text(p['run'])
    run = json.loads(rj) if rj else None
    ended, end_info = C.process_end(run)
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
    fixf10_ok = len(stc) >= 1 and all(s.replace('/', '\\').endswith('\\' + DIR_FIX) for s in stc)
    pf = r['precache_first']
    cold_ok = (bool(cold_t) and 'absent' in cold_t and pf is not None and pf.startswith('PipelinePrecache: no ')
               and pf.endswith(' yet') and DIR_FIX in pf)
    fs_ok = (len(r['fs']) >= 1 and all(m == 1 and u == 1 for _, m, u in r['fs'])
             and (r['guest_first'] is None or r['fs'][0][0] < r['guest_first']))
    rev = r['rev'] + srev
    rev_row = 'NOT_PRESENT' if not rev else ('YES' if all(REV in t for _, _, t in rev) else 'NO')
    hashes = list(r['fail_hashes'])
    for hx in shashes:
        if hx not in hashes:
            hashes.append(hx)
    death = r['death'] + (sd or [])
    return dict(tag=TAG, level=LEVEL, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha, rev=rev[:6],
                rev_row=rev_row, stc=stc, fixf10_ok=fixf10_ok, precache_first=pf, cold_txt=(cold_t or '').strip()[:200], cold_ok=cold_ok,
                warm_txt=(warm_t or '').strip()[:200], warm_size=warm_size, warm_ok=warm_size is not None and warm_size > 0,
                installed_sha=sha, installed_before=sha_b, sha_ok=sha == BIN_EXPECT and sha_b == BIN_EXPECT,
                fs=r['fs'][:3], fs_ok=fs_ok, fail_log=len(r['fail']), fail_stdout=sfail, fail_hashes=hashes[:20],
                ended=ended, end_info=end_info, guest_first=r['guest_first'], entry_line=r['entry_line'],
                scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'], hold_us=r['hold_us'],
                hold_s=round(r['hold_us'] / 1e6, 2), k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], ft_rows=r['ft_rows'],
                death=death, stdout_present=sd is not None, skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'],
                gamepatch=r['gamepatch'], idx_records=idx_n, glitches=gl, sheet=sheet)


def members(res):
    nfail = res['fail_log'] + res['fail_stdout']
    mem = [('binary: installed before the tag = binary of the tag = 631ff987 (installed FS5)', res['sha_ok']),
           ('translation cache directory %s in every line' % DIR_FIX, res['fixf10_ok']),
           ('entered (entry line of %s)' % res['level'], res['entry_line'] is not None),
           ('hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= C.HOLD_MIN_US),
           ('no process end before the timeout', None if res['ended'] is None else res['ended'] is False),
           ('0 death markers', not res['death']),
           ('video index records >= 3000', (res['idx_records'] or 0) >= C.VIDEO_MIN),
           ('0 one-frame glitches', None if res['glitches'] is None else res['glitches'] == 0),
           ('sheet for the lead made', res['sheet'] is not None),
           ('warm form after the tag: %s/pipelines.bin present, size > 0' % DIR_FIX, res['warm_ok'])]
    ref = [('revision text names 0e72bc1', res['rev_row']),
           ('cold form before the tag: %s absent, PipelinePrecache: no ... yet' % DIR_FIX, res['cold_ok']),
           ('frames >= 1 s after the first scene frame = %d (cold entry)' % res['k2_after'],
            res['entry_line'] is not None and res['k2_after'] == 0),
           ('FixSval mode=1 ubo_std_layout=1 before the first GuestOut', res['fs_ok']),
           ('0 lines SPIR-V validation failed', nfail == 0)]
    inter = not res['win'].get('minimized') and not res['recovering'] and not res['gamepatch']
    return mem, ref, inter


def verdict(res):
    mem, _, inter = members(res)
    if not inter:
        return 'INTERFERENCE'
    return 'PASS' if all(v is True for _, v in mem) else 'FAIL'


def rows(res):
    out = ['FS5E %s level %s log sha256 %s lines %d stdout sha256 %s' % (res['tag'], res['level'], res['log_sha256'], res['log_lines'],
                                                                       res['stdout_sha256'])]
    add = out.append
    add('  binary: installed before %s, of the tag %s (expected %s); revision texts %s' % (res['installed_before'], res['installed_sha'],
                                                                                         BIN_EXPECT, res['rev']))
    add('  Shader translation cache lines %s; first PipelinePrecache line %r; before: %s; after: %s'
        % (res['stc'][:3], res['precache_first'], res['cold_txt'], res['warm_txt']))
    add('  FixSval lines %s (first GuestOut line %s); SPIR-V validation failed: log %d, stdout %d, hashes %s'
        % (res['fs'], res['guest_first'], res['fail_log'], res['fail_stdout'], res['fail_hashes']))
    add('  process end before the timeout: %s (%s)' % (C.yn(res['ended']), C.asc(res['end_info'])))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold %.2f s; frames >= 1 s after it %d (max dt_us %d)'
        % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'], res['k2_after'], res['dt_max_after']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; AsyncPipelines: skipped draw %d (reference)'
        % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw']))
    add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    mem, ref, inter = members(res)
    for name, val in mem:
        add('  MEMBER %s: %s' % (name, C.yn(val)))
    for name, val in ref:
        add('  REFERENCE %s: %s' % (name, C.yn(val)))
    add('  INTERFERENCE none (window minimized / Recovering Vulkan swapchain / GamePatch): %s' % C.yn(inter))
    add('WARMUP VERDICT %s: %s' % (res['tag'], verdict(res)))
    return out


def main(argv):
    if '--dir' in argv:
        p = paths(argv[argv.index('--dir') + 1])
    else:
        if not argv or argv[0] != TAG:
            raise SystemExit('usage: fs5e_read.py fs5_i [--json <out>] | --dir <fixture dir>')
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
