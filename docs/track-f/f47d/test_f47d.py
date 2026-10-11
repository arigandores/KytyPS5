"""Track F link F47d (HPP-809): fixtures of the reader f47d_read.py, the machine rules next_f47d.py, the detector thumb_f47d.py and the
queue queue_f47d.py - one fixture per member and per edge; the last line is ALL OK.  The first line names the suite and its targets with
sha256.  Outputs of the scripts are checked in strict cp1250 without PYTHONIOENCODING.  ASCII only.
usage: python test_f47d.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f47d_read as R  # noqa: E402
import next_f47d as N  # noqa: E402

TARGETS = ['f47d_read.py', 'next_f47d.py', 'thumb_f47d.py', 'queue_f47d.py']
FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
FS14 = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
SKY = 'underwater_aerial_garden'
OK = True


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond):
    global OK
    print('%-70s %s' % (name[:70], 'PASS' if cond else 'FAIL'))
    OK &= bool(cond)


def w(path, s, mode='w'):
    with open(path, mode, newline='\n') as f:
        f.write(s)


def mk_log(rd=True, grid=None, n0=300, flips=12, rdl=True, death=False, hang=False, win=None, rec=False, imp=0, stg=1000,
           draw_lines=True, other_flip=False, rdl_before=False, ge1_capture=True, variant='variant_fixb26_fixb1b_fixf10_fixf19'):
    grid = grid or N_GRID1
    L = ['Fork build arigandores/KytyPS5 x', 'Shader translation cache: _ShaderCache' + chr(92) + 'PPSA21564' + chr(92) + variant,
         'GuestOut: Level has started: ' + SKY]
    if rdl_before:
        L.insert(1, 'RenderDoc: level started at frame 5, capture at frame 734 (+11 more)')
    n = n0
    L.append('FrameTrace: n=%d dt_us=16000 draws=50' % n)
    if draw_lines:
        L.append('FrameTrace-draw: n=%d a=1 img_imp=%d img_imp_kb=%d x=1' % (n, imp, imp * 4))
    L.append('FrameTrace-x: n=%d a=1 stg_img_pool_b=%d stg_img_in_b=0 x=1' % (n, stg))
    if rd and rdl and not rdl_before:
        L.append('RenderDoc: level started at frame %d, capture at frame %d (+11 more)' % (n, n + grid[0]))
    for i in range(1, 20):
        n += 1
        L.append('FrameTrace: n=%d dt_us=16000 draws=400' % n)
        if draw_lines:
            L.append('FrameTrace-draw: n=%d a=1 img_imp=0 img_imp_kb=0 x=1' % n)
        L.append('FrameTrace-x: n=%d a=1 stg_img_pool_b=0 stg_img_in_b=0 x=1' % n)
    if rd:
        for k, g in enumerate(grid):
            L += ['RenderDoc: auto capture at frame %d (level+%d)' % (n0 + g, g), 'RenderDoc: capture requested', 'RenderDoc: capture started']
            if k < flips:
                L.append('RenderDoc: captured guest flip 1/1')
            L.append('RenderDoc: capture finished')
            n += 1
            L.append('FrameTrace: n=%d dt_us=%d draws=400' % (n, 9000000 if ge1_capture else 16000))
            if draw_lines:
                L.append('FrameTrace-draw: n=%d a=1 img_imp=0 img_imp_kb=0 x=1' % n)
            L.append('FrameTrace-x: n=%d a=1 stg_img_pool_b=0 stg_img_in_b=0 x=1' % n)
        if other_flip:
            L.append('RenderDoc: captured guest flip 1/2')
    n += 1
    L.append('FrameTrace: n=%d dt_us=1500000 draws=400' % n)
    if draw_lines:
        L.append('FrameTrace-draw: n=%d a=1 img_imp=0 img_imp_kb=0 x=1' % n)
    L.append('FrameTrace-x: n=%d a=1 stg_img_pool_b=0 stg_img_in_b=0 x=1' % n)
    if death:
        L.append('--- Fatal Error ---')
    if hang:
        L.append('GpuHangAbort: fence 3 timeout')
    if win:
        L.append('Window 1 %s' % win)
    L.append('Event: quit')
    return '\n'.join(L) + '\n'


N_GRID1 = [729 + 3 * k for k in range(12)]


def mk_tag(root, tag, inst=FS13, rd=True, grid=None, env_extra=None, env_drop=None, cmd_rd=None, log_kw=None, rdc=12, thumbs=12,
           mcmp='manifest cmp EQUAL 5 of 5', vcopy='manifest C:/x/variant_copy.tsv files 812 bytes 1 listsha ' + 'a' * 64, free='120', interf=None, hold=120, outcome='ok',
           seal='seal text v1\n', pre=None, ipre=None, ia=None):
    d = os.path.join(root, tag)
    os.makedirs(d)
    grid = grid or N_GRID1
    w(os.path.join(d, 'seal.md'), seal)
    env = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/x/g', KYTY_SAMPLE_GATE='C:/x/s', KYTY_QUEUE_TRACE='1',
               KYTY_GPU_HANG_ABORT_S='8', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
    if rd:
        env.update(KYTY_RD_LEVEL=SKY, KYTY_RD_LEVEL_FRAME=','.join(str(g) for g in grid), KYTY_RD_FLIPS='1')
    else:
        env.update(KYTY_HOST_IMPORT_MIN_KB='4194304', KYTY_REC='C:/x/rec.mp4')
    env.update(env_extra or {})
    for k in env_drop or []:
        env.pop(k, None)
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false'] + (['--rd'] if (rd if cmd_rd is None else cmd_rd) else [])
    js = dict(binary_sha256=inst, prereg=dict(sha256=pre or sha(os.path.join(d, 'seal.md'))), env=env, cmdline=cmd,
              attempts=[dict(outcome=outcome)], guest_args='-lvl ' + SKY, hold_s=hold)
    w(os.path.join(d, 'es.json'), json.dumps(js))
    w(os.path.join(d, 'log.txt'), mk_log(rd=rd, grid=grid, **(log_kw or {})))
    w(os.path.join(d, 'stdout.txt'), 'ok\n')
    w(os.path.join(d, 'installed_pre.txt'), '%s FS\n' % (ipre or inst))
    w(os.path.join(d, 'installed_before.txt'), inst + '\n')
    w(os.path.join(d, 'installed_after.txt'), (ia or inst) + '\n')
    w(os.path.join(d, 'manifest_cmp.txt'), mcmp + '\n')
    w(os.path.join(d, 'variant_copy.txt'), vcopy + '\n')
    w(os.path.join(d, 'level.txt'), SKY + '\n')
    w(os.path.join(d, 'free_gib_before.txt'), free + '\n')
    if not rd:
        w(os.path.join(d, 'rec.idx'), ''.join('%d %d 1.0\n' % (i, i + 10) for i in range(4000)))
    if rd:
        w(os.path.join(d, 'grid.txt'), ','.join(str(g) for g in grid) + '\n')
        w(os.path.join(d, 'rdc_sha.txt'), ''.join('%064x  %s_k%02d.rdc  100\n' % (i, tag, i) for i in range(1, rdc + 1)))
        th = ['thumb_f47d band']
        for i in range(1, thumbs + 1):
            th.append('k%02d level+%d K %d Wt 0 class %s' % (i, grid[i - 1] if i <= len(grid) else 0, 200 if i == 3 else 0,
                                                              'black' if i == 3 else '-'))
        th.append('G black %d white 0 of 12 thumbs %d' % (1 if thumbs >= 3 else 0, thumbs))
        w(os.path.join(d, 'thumbs.txt'), '\n'.join(th) + '\n')
    if interf:
        w(os.path.join(d, 'INTERFERENCE'), interf + '\n')
    return d


def rd_(root, tag, **kw):
    d = mk_tag(root, tag, **kw)
    t = os.path.basename(tag)
    return R.read_tag(t, R.paths(t, d))


def failed_has(res, sub):
    return any(sub in f for f in res['failed'])


def main():
    hdr = 'suite test_f47d.py sha256 %s target %s' % (sha(os.path.abspath(__file__)),
                                                         ' '.join('%s sha256 %s' % (t, sha(os.path.join(HERE, t))) for t in TARGETS))
    print(hdr)
    root = tempfile.mkdtemp(prefix='f47d_t_')
    try:
        # reader: rd
        r = rd_(root, 'f47_rd')
        check('rd: good tag ADMITTED', r['status'] == 'ADMITTED' and not r['failed'])
        check('rd: n0 300, P = 745.25, inside sample', r['rows']['n0'] == 300 and r['rows']['P'] == 745.25 and not r['rows']['P_outside_sample'])
        check('rd: G black 1 row', r['rows']['G_black'] == 1)
        check('rd: frames >= 1 s at capture 12, outside 1', len(r['rows']['frames_ge1s_at_capture']) == 12 and
              len(r['rows']['frames_ge1s_outside']) == 1)
        r = rd_(root, 'f47_rd_r1', log_kw=dict(n0=150))
        check('rd: n0 150 - prediction outside the sample', r['rows']['P_outside_sample'] is True and r['status'] == 'ADMITTED')
        r = rd_(root, 'f47_rd_r2', inst=FS14)
        check('rd: FS14 installed ADMITTED, binary FS14', r['status'] == 'ADMITTED' and r['binary'] == 'FS14')
        r = rd_(root, 'x1/f47_rd', inst='0' * 64)
        check('rd: unknown binary NOT_ADMITTED', r['status'] == 'NOT_ADMITTED' and failed_has(r, 'binary_sha256'))
        r = rd_(root, 'x2/f47_rd', ia=FS14)
        check('rd: binary changed after NOT_ADMITTED', r['status'] == 'NOT_ADMITTED' and failed_has(r, 'binary_sha256'))
        r = rd_(root, 'x3/f47_rd', ipre=FS14)
        check('rd: binary pre differs NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')
        r = rd_(root, 'x4/f47_rd', pre='1' * 64)
        check('rd: prereg != seal NOT_ADMITTED', failed_has(r, 'prereg'))
        r = rd_(root, 'x5/f47_rd', env_extra=dict(KYTY_FIX_F26='1'))
        check('rd: extra KYTY_FIX_* NOT_ADMITTED', failed_has(r, 'env ='))
        r = rd_(root, 'x6/f47_rd', env_extra=dict(KYTY_GAME_PATCH='C:/p.txt'))
        check('rd: KYTY_GAME_PATCH NOT_ADMITTED', failed_has(r, 'env ='))
        r = rd_(root, 'x7/f47_rd', env_extra=dict(KYTY_RD_FLIPS='2'))
        check('rd: KYTY_RD_FLIPS=2 NOT_ADMITTED', failed_has(r, 'env ='))
        r = rd_(root, 'x8/f47_rd', env_drop=['KYTY_GPU_CLOCK_PIN'])
        check('rd: missing KYTY_GPU_CLOCK_PIN NOT_ADMITTED', failed_has(r, 'env ='))
        r = rd_(root, 'x9/f47_rd', env_extra=dict(KYTY_GPU_CHECKPOINTS='1'))
        check('rd: KYTY_GPU_CHECKPOINTS NOT_ADMITTED', failed_has(r, 'env ='))
        r = rd_(root, 'x10/f47_rd', cmd_rd=False)
        check('rd: no --rd NOT_ADMITTED', failed_has(r, '--rd'))
        r = rd_(root, 'x11/f47_rd', hold=330)
        check('rd: hold 330 NOT_ADMITTED', failed_has(r, 'hold option'))
        r = rd_(root, 'x12/f47_rd', outcome='timeout')
        check('rd: outcome timeout NOT_ADMITTED', failed_has(r, 'outcome'))
        r = rd_(root, 'x13/f47_rd', log_kw=dict(death=True))
        check('rd: death marker NOT_ADMITTED', failed_has(r, 'death'))
        r = rd_(root, 'x14/f47_rd', log_kw=dict(hang=True))
        check('rd: GpuHangAbort NOT_ADMITTED (both members)', failed_has(r, 'GpuHangAbort') and failed_has(r, 'death'))
        r = rd_(root, 'x15/f47_rd', log_kw=dict(win='minimized'))
        check('rd: window minimized INTERFERENCE', r['status'] == 'INTERFERENCE')
        r = rd_(root, 'x16/f47_rd', log_kw=dict(win='lost keyboard focus'))
        check('rd: lost keyboard focus INTERFERENCE', r['status'] == 'INTERFERENCE')
        r = rd_(root, 'x17/f47_rd', interf='display not ON after the tag')
        check('rd: INTERFERENCE file', r['status'] == 'INTERFERENCE')
        r = rd_(root, 'x18/f47_rd', mcmp='manifest cmp DIFF 1')
        check('rd: manifest DIFF NOT_ADMITTED', failed_has(r, 'caches returned'))
        r = rd_(root, 'x19/f47_rd', vcopy='')
        check('rd: no variant copy NOT_ADMITTED', failed_has(r, 'variant catalog'))
        r = rd_(root, 'x19b/f47_rd', vcopy='manifest C:/x/v.tsv files 0 bytes 0 listsha ' + 'a' * 64)
        check('rd: variant copy with 0 files NOT_ADMITTED', failed_has(r, 'variant catalog'))
        r = rd_(root, 'x19c/f47_rd', log_kw=dict(variant='variant_fixb26_fixb1b_fixf10'))
        check('rd: translation cache of another variant NOT_ADMITTED', failed_has(r, 'Shader translation cache'))
        r = rd_(root, 'x20/f47_rd', free='79')
        check('rd: free 79 GiB NOT_ADMITTED', failed_has(r, 'free on C'))
        r = rd_(root, 'x21/f47_rd', free='80')
        check('rd: free 80 GiB edge ADMITTED', r['status'] == 'ADMITTED')
        r = rd_(root, 'x22/f47_rd', log_kw=dict(flips=11))
        check('rd: 11 flip lines NOT_ADMITTED', failed_has(r, 'captured guest flip'))
        r = rd_(root, 'x23/f47_rd', log_kw=dict(other_flip=True))
        check('rd: other flip line NOT_ADMITTED', failed_has(r, 'captured guest flip'))
        r = rd_(root, 'x24/f47_rd', log_kw=dict(rdl=False))
        check('rd: no level started line NOT_ADMITTED', failed_has(r, 'level started'))
        r = rd_(root, 'x25/f47_rd', log_kw=dict(rdl_before=True))
        check('rd: level started before the named start NOT_ADMITTED', failed_has(r, 'level started'))
        r = rd_(root, 'x26/f47_rd', rdc=11)
        check('rd: 11 captures NOT_ADMITTED', failed_has(r, 'new captures'))
        r = rd_(root, 'x27/f47_rd', thumbs=11)
        check('rd: 11 thumbs NOT_ADMITTED', failed_has(r, 'thumbnail rows'))
        g2 = [730 + 3 * k for k in range(12)]
        d = mk_tag(root, 'x28/f47_rd', grid=g2)
        w(os.path.join(d, 'grid.txt'), ','.join(str(g) for g in g2) + '\n')
        r = R.read_tag('f47_rd', R.paths('f47_rd', d))
        check('rd: f47_rd with a grid other than 729..762 NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')
        r = rd_(root, 'x29/f47_rd2', grid=g2)
        check('rd2: grid from grid.txt ADMITTED', r['status'] == 'ADMITTED' and r['rows']['grid'] == g2)
        d = mk_tag(root, 'x30/f47_rd2', grid=g2)
        w(os.path.join(d, 'grid.txt'), ','.join(str(g + 1) for g in g2) + '\n')
        r = R.read_tag('f47_rd2', R.paths('f47_rd2', d))
        check('rd2: log X list != grid.txt NOT_ADMITTED', failed_has(r, 'auto capture'))
        r = rd_(root, 'x31/f47_rd', log_kw=dict(ge1_capture=False))
        check('rd: no long frames at captures - rows 0 / 1', len(r['rows']['frames_ge1s_at_capture']) == 0 and r['status'] == 'ADMITTED')
        # reader: hi
        r = rd_(root, 'h1/f47_hi', rd=False, log_kw=dict(imp=0))
        check('hi: good tag ADMITTED', r['status'] == 'ADMITTED' and r['rows']['knob']['img_imp'] == 0)
        r = rd_(root, 'h2/f47_hi', rd=False, log_kw=dict(imp=3))
        check('hi: img_imp 3 - knob action (1) NOT_ADMITTED', failed_has(r, 'knob action (1)'))
        r = rd_(root, 'h3/f47_hi', rd=False, log_kw=dict(stg=0))
        check('hi: staging 0 - knob action (2) NOT_ADMITTED', failed_has(r, 'knob action (2)'))
        r = rd_(root, 'h4/f47_hi', rd=False, log_kw=dict(draw_lines=False))
        check('hi: no draw lines - knob action (4) NOT_ADMITTED', failed_has(r, 'knob action (4)'))
        r = rd_(root, 'h5/f47_hi', rd=False, cmd_rd=True)
        check('hi: --rd NOT_ADMITTED', failed_has(r, '--rd'))
        r = rd_(root, 'h6/f47_hi', rd=False, env_drop=['KYTY_HOST_IMPORT_MIN_KB'])
        check('hi: no KYTY_HOST_IMPORT_MIN_KB NOT_ADMITTED', failed_has(r, 'env ='))
        r = rd_(root, 'h7/f47_hi', rd=False, env_extra=dict(KYTY_HOST_IMPORT_MIN_KB='64'))
        check('hi: KYTY_HOST_IMPORT_MIN_KB=64 NOT_ADMITTED', failed_has(r, 'env ='))
        d = mk_tag(root, 'h8/f47_hi', rd=False)
        os.remove(os.path.join(d, 'rec.idx'))
        r = R.read_tag('f47_hi', R.paths('f47_hi', d))
        check('hi: no video index NOT_ADMITTED', failed_has(r, 'video index'))
        # rows output and table are ascii
        out = '\n'.join(R.rows_out(rd_(root, 'y1/f47_rd')))
        check('reader rows ascii', all(ord(c) < 128 for c in out))
        # machine rules
        runs = os.path.join(root, 'runs')
        os.makedirs(runs)

        def made(tag, status, gblack=None, n0=None):
            d = os.path.join(runs, tag)
            os.makedirs(d, exist_ok=True)
            rows = {}
            if gblack is not None:
                rows['G_black'] = gblack
            if n0 is not None:
                rows['n0'] = n0
            if status:
                w(os.path.join(d, 'read.json'), json.dumps(dict(status=status, rows=rows)))

        def lk(tag, a, b):
            with open(os.path.join(runs, 'lock.log'), 'a', newline='\n') as f:
                f.write('lock taken %s 2026-10-11T17:%02d:00Z\nlock released %s 2026-10-11T17:%02d:00Z\n' % (tag, a, tag, b))
        check('next: f47_rd first MAY', N.may(runs, 'f47_rd')[0] == 0)
        check('next: f47_hi before f47_rd - 7', N.may(runs, 'f47_hi')[0] == 7)
        check('next: f47_rd2 before f47_rd - 7', N.may(runs, 'f47_rd2')[0] == 7)
        check('next: f47_rd_r1 before f47_rd - 11', N.may(runs, 'f47_rd_r1')[0] == 11)
        made('f47_rd', None)
        check('next: unread attempt - 7', N.may(runs, 'f47_rd_r1')[0] == 7)
        check('next: existing tag - 2', N.may(runs, 'f47_rd')[0] == 2)
        made('f47_rd', 'NOT_ADMITTED')
        check('next: after NOT_ADMITTED f47_rd_r1 MAY', N.may(runs, 'f47_rd_r1')[0] == 0)
        check('next: after NOT_ADMITTED f47_rd_r2 - 11 (order)', N.may(runs, 'f47_rd_r2')[0] == 11)
        made('f47_rd_r1', 'INTERFERENCE')
        check('next: interference does not spend - f47_rd_r2 MAY', N.may(runs, 'f47_rd_r2')[0] == 0)
        made('f47_rd_r2', 'NOT_ADMITTED')
        check('next: two NOT_ADMITTED - f47_rd_r3 refused 11', N.may(runs, 'f47_rd_r3')[0] == 11)
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', 'ADMITTED', gblack=2, n0=326)
        check('next: rd ADMITTED - f47_rd_r1 refused 11', N.may(runs, 'f47_rd_r1')[0] == 11)
        check('next: G black 2 - f47_rd2 not due 7', N.may(runs, 'f47_rd2')[0] == 7)
        os.environ['F47D_RD2_OK'] = '1'
        check('next: F47D_RD2_OK=1 - f47_rd2 MAY', N.may(runs, 'f47_rd2')[0] == 0)
        del os.environ['F47D_RD2_OK']
        check('next: G black 2 - f47_hi MAY', N.may(runs, 'f47_hi')[0] == 0)
        rc, gr = N.grid(runs)
        check('next: grid n0 326 -> R 748 -> 732..765', rc == 0 and gr == ','.join(str(732 + 3 * k) for k in range(12)))
        # lead admission F47D_RD_ADMIT_LEAD=f47_rd (item 731 (v)): without it waits, with it goes, another name does nothing
        shutil.rmtree(runs)
        os.makedirs(runs)
        os.environ.pop('F47D_RD_ADMIT_LEAD', None)
        made('f47_rd', 'NOT_ADMITTED', gblack=2, n0=187)
        check('next: lead admit unset - f47_hi waits (7)', N.may(runs, 'f47_hi')[0] == 7)
        check('next: lead admit unset - f47_rd_r1 MAY', N.may(runs, 'f47_rd_r1')[0] == 0)
        check('next: lead admit unset - no grid (7)', N.grid(runs)[0] == 7)
        for other in ('f47_rd_r1', 'f47_rd2', 'F47_RD', 'f47_rd ', '1', ''):
            os.environ['F47D_RD_ADMIT_LEAD'] = other
            check('next: lead admit %r - f47_hi waits (7)' % other, N.may(runs, 'f47_hi')[0] == 7)
            check('next: lead admit %r - f47_rd_r1 MAY' % other, N.may(runs, 'f47_rd_r1')[0] == 0)
        os.environ['F47D_RD_ADMIT_LEAD'] = 'f47_rd'
        check('next: lead admit f47_rd - f47_hi MAY', N.may(runs, 'f47_hi')[0] == 0)
        check('next: lead admit f47_rd - f47_rd_r1 refused 11', N.may(runs, 'f47_rd_r1')[0] == 11)
        check('next: lead admit f47_rd - G black 2 - f47_rd2 not due 7', N.may(runs, 'f47_rd2')[0] == 7)
        rc, gr = N.grid(runs)
        check('next: lead admit f47_rd - grid n0 187 -> R 733 -> 717..750', rc == 0 and gr == ','.join(str(717 + 3 * k) for k in range(12)))
        os.environ['F47D_RD2_OK'] = '1'
        check('next: lead admit + F47D_RD2_OK=1 - f47_rd2 MAY', N.may(runs, 'f47_rd2')[0] == 0)
        del os.environ['F47D_RD2_OK']
        made('f47_rd_r1', 'NOT_ADMITTED')
        check('next: lead admit names f47_rd only - r1 made, f47_rd still NOT_ADMITTED -> f47_hi MAY', N.may(runs, 'f47_hi')[0] == 0)
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', 'INTERFERENCE')
        check('next: lead admit on INTERFERENCE f47_rd does nothing - f47_hi waits (7)', N.may(runs, 'f47_hi')[0] == 7)
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', None)
        check('next: lead admit on UNREAD f47_rd does nothing - f47_hi waits (7)', N.may(runs, 'f47_hi')[0] == 7)
        # lead admission F47D_HI_ADMIT_LEAD=f47_hi (item 734 (v)): without it f47_hi_r1 is due, with it the series ends, another
        # value / another status does nothing
        shutil.rmtree(runs)
        os.makedirs(runs)
        os.environ['F47D_RD_ADMIT_LEAD'] = 'f47_rd'
        os.environ.pop('F47D_HI_ADMIT_LEAD', None)
        made('f47_rd', 'NOT_ADMITTED', gblack=2, n0=187)
        made('f47_hi', 'INTERFERENCE')
        check('next: hi admit unset - f47_hi_r1 MAY', N.may(runs, 'f47_hi_r1')[0] == 0)
        check('next: hi admit unset - f47_hi not admitted', N.admitted(runs, 'f47_hi') is None)
        for other in ('f47_hi_r1', 'f47_rd', 'F47_HI', 'f47_hi ', '1', ''):
            os.environ['F47D_HI_ADMIT_LEAD'] = other
            check('next: hi admit %r - f47_hi_r1 MAY' % other, N.may(runs, 'f47_hi_r1')[0] == 0)
            check('next: hi admit %r - f47_hi not admitted' % other, N.admitted(runs, 'f47_hi') is None)
        os.environ.pop('F47D_HI_ADMIT_LEAD', None)
        os.environ['F47D_RD_ADMIT_LEAD'] = 'f47_hi'
        check('next: rd variable = f47_hi does not admit f47_hi - f47_hi_r1 refused 7 (rd not admitted)',
              N.may(runs, 'f47_hi_r1')[0] == 7 and N.admitted(runs, 'f47_hi') is None)
        os.environ['F47D_RD_ADMIT_LEAD'] = 'f47_rd'
        os.environ['F47D_HI_ADMIT_LEAD'] = 'f47_hi'
        rc, msg = N.may(runs, 'f47_hi_r1')
        check('next: hi admit f47_hi - f47_hi_r1 refused 11, series ends', rc == 11 and 'series F47d ends' in msg and 'item 734' in msg)
        check('next: hi admit f47_hi - f47_hi admitted', N.admitted(runs, 'f47_hi') == 'f47_hi')
        check('next: hi admit f47_hi - f47_hi exists 2', N.may(runs, 'f47_hi')[0] == 2)
        check('next: hi admit f47_hi - f47_rd2 keeps its rule (not due 7)', N.may(runs, 'f47_rd2')[0] == 7)
        check('next: hi admit f47_hi - rd still admitted by item 731', N.admitted(runs, 'f47_rd') == 'f47_rd')
        os.environ['F47D_RD_ADMIT_LEAD'] = 'f47_hi'
        check('next: hi variable does not admit f47_rd', N.admitted(runs, 'f47_rd') is None)
        os.environ['F47D_RD_ADMIT_LEAD'] = 'f47_rd'
        for st in ('NOT_ADMITTED', None):
            shutil.rmtree(runs)
            os.makedirs(runs)
            made('f47_rd', 'NOT_ADMITTED', gblack=2, n0=187)
            made('f47_hi', st)
            exp = 0 if st == 'NOT_ADMITTED' else 7
            check('next: hi admit on %s f47_hi does nothing - f47_hi_r1 rc %d' % (st or 'UNREAD', exp),
                  N.may(runs, 'f47_hi_r1')[0] == exp and N.admitted(runs, 'f47_hi') is None)
        del os.environ['F47D_HI_ADMIT_LEAD']
        del os.environ['F47D_RD_ADMIT_LEAD']
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', 'ADMITTED', gblack=0, n0=300)
        rc, gr = N.grid(runs)
        check('next: grid n0 300 -> 745.25 -> R 745 -> 729..762', rc == 0 and gr.split(',')[0] == '729' and gr.split(',')[-1] == '762')
        check('next: G black 0 - f47_rd2 MAY', N.may(runs, 'f47_rd2')[0] == 0)
        check('next: G black 0 - f47_hi waits for f47_rd2 (7)', N.may(runs, 'f47_hi')[0] == 7)
        made('f47_rd2', 'ADMITTED', gblack=0, n0=310)
        check('next: rd2 ADMITTED - f47_hi MAY', N.may(runs, 'f47_hi')[0] == 0)
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', 'ADMITTED', gblack=0, n0=None)
        check('next: grid without n0 - 7', N.grid(runs)[0] == 7)
        made('f47_rd2', 'NOT_ADMITTED')
        made('f47_rd2_r1', 'NOT_ADMITTED')
        check('next: rd2 exhausted - f47_hi MAY', N.may(runs, 'f47_hi')[0] == 0)
        # grid rounding edge: 713.0 + 0.1075 * n0 = x.5 exactly -> up (n0 = 200: 734.5 -> 735)
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', 'ADMITTED', gblack=0, n0=200)
        check('next: grid rounding 734.5 -> R 735 (half up)', N.grid(runs)[1].split(',')[0] == '719')
        # budget
        shutil.rmtree(runs)
        os.makedirs(runs)
        check('next: budget default estimate rd 1200 MAY', N.may(runs, 'f47_rd')[0] == 0)
        made('f47_rd', 'ADMITTED', gblack=0, n0=300)
        lk('f47_rd', 0, 20)
        check('next: spent 1200 + est 1200 = 2400 - f47_rd2 MAY', N.may(runs, 'f47_rd2')[0] == 0)
        made('f47_rd2', 'NOT_ADMITTED')
        lk('f47_rd2', 21, 41)
        check('next: spent 2400 + est 1200 > 2700 - f47_rd2_r1 refused 12', N.may(runs, 'f47_rd2_r1')[0] == 12)
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', 'ADMITTED', gblack=1, n0=300)
        lk('f47_rd', 0, 33)
        check('next: spent 1980 + est hi 720 = 2700 edge - f47_hi MAY', N.may(runs, 'f47_hi')[0] == 0)
        with open(os.path.join(runs, 'lock.log'), 'a', newline='\n') as f:
            f.write('lock taken f47_hi 2026-10-11T18:00:00Z\n')
        check('next: open lock span - refused 12', N.may(runs, 'f47_hi')[0] == 12)
        shutil.rmtree(runs)
        os.makedirs(runs)
        made('f47_rd', 'ADMITTED', gblack=1, n0=300)
        lk('f47_rd', 0, 34)
        check('next: spent 2040 + est hi 720 > 2700 - f47_hi refused 12', N.may(runs, 'f47_hi')[0] == 12)
        os.makedirs(os.path.join(runs, 'f47_hi.busy_120000'))
        check('next: moved-aside folder is not an attempt', N.chain(runs, 'f47_hi') == [])
        # queue
        qf = os.path.join(root, 'q.json')

        def q(items, ok=None):
            w(qf, json.dumps(items))
            env = dict(os.environ)
            env.pop('PYTHONIOENCODING', None)
            if ok:
                env['F47D_QUEUE_OK'] = ok
            p = subprocess.run([sys.executable, os.path.join(HERE, 'queue_f47d.py'), '--fake', qf], capture_output=True, env=env)
            return p.returncode, p.stdout.decode('cp1250')
        T = '\u0442\u0440\u0435\u043a '
        rc, o = q([dict(identifier='HPP-1', status='in_progress', title=T + 'F x', executionRunId='r')])
        check('queue: F link in_progress with a run - BUSY', rc == 1 and 'BUSY: HPP-1' in o)
        rc, o = q([dict(identifier='HPP-1', status='in_progress', title=T + 'F x', executionRunId='r')], ok='HPP-1')
        check('queue: F47D_QUEUE_OK lets that issue pass', rc == 0)
        rc, o = q([dict(identifier='HPP-1', status='in_progress', title=T + 'F x', executionRunId=None)])
        check('queue: F link in_progress without a run - FREE', rc == 0)
        rc, o = q([dict(identifier='HPP-2', status='todo', title=T + 'P x', executionRunId=None)])
        check('queue: P link todo - BUSY', rc == 1)
        rc, o = q([dict(identifier='HPP-2', status='todo', title=T + 'P x')], ok='HPP-2')
        check('queue: F47D_QUEUE_OK does not pass a P link', rc == 1)
        rc, o = q([dict(identifier='HPP-3', status='in_review', title=T + 'F x', executionRunId='r')])
        check('queue: in_review with a run - FREE', rc == 0)
        rc, o = q([dict(identifier='HPP-809', status='in_progress', title=T + 'F x', executionRunId='r')])
        check('queue: own link ignored - FREE', rc == 0)
        # thumbnails (ffmpeg pictures) and cp1250 of every script output
        import numpy as np
        td = os.path.join(root, 'th')
        os.makedirs(td)

        def pic(name, arr):
            p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '480x270', '-i', '-',
                                os.path.join(td, name)], input=arr.tobytes(), capture_output=True)
            return p.returncode == 0
        base = np.full((270, 480, 3), 128, dtype=np.uint8)
        a = base.copy()
        a[10:20, 10:25] = 0          # 150 black pixels in the band - edge K >= 150
        b = base.copy()
        b[10:20, 10:24] = 0          # 140
        c = base.copy()
        c[0:20, 0:50] = 255          # 1000 white - edge
        e = base.copy()
        e[100:200, 0:480] = 0        # black below the band only
        f = base.copy()
        f[0:81, :] = 0               # whole band black (darkening): K 38 880
        ok = all(pic(n, x) for n, x in (('k01.png', a), ('k02.png', b), ('k03.png', c), ('k04.png', e), ('k05.png', f)))
        check('thumb: pictures written', ok)
        w(os.path.join(td, 'grid.txt'), ','.join(str(g) for g in N_GRID1) + '\n')
        env = dict(os.environ)
        env.pop('PYTHONIOENCODING', None)
        p = subprocess.run([sys.executable, os.path.join(HERE, 'thumb_f47d.py'), td], capture_output=True, env=env)
        o = p.stdout.decode('cp1250')
        rows = dict((l.split()[0], l) for l in o.splitlines() if l[:1] == 'k')
        check('thumb: K 150 edge -> black', 'K 150 ' in rows.get('k01', '') and rows['k01'].endswith('class black'))
        check('thumb: K 140 -> -', 'K 140 ' in rows.get('k02', '') and rows['k02'].endswith('class -'))
        check('thumb: Wt 1000 edge -> white', 'Wt 1000 ' in rows.get('k03', '') and rows['k03'].endswith('class white'))
        check('thumb: black below the band -> K 0', 'K 0 ' in rows.get('k04', ''))
        check('thumb: whole band black K 38880 printed', 'K 38880 ' in rows.get('k05', ''))
        check('thumb: k01 matched to level+729, k05 to level+741', 'level+729 ' in rows.get('k01', '') and 'level+741 ' in rows.get('k05', ''))
        check('thumb: G line black 2 white 1 of 12 thumbs 5', 'G black 2 white 1 of 12 thumbs 5' in o)
        check('thumb: output strict cp1250 / ascii', p.returncode == 0 and all(ord(ch) < 128 for ch in o))
        d = mk_tag(root, 'z1/f47_rd')
        p = subprocess.run([sys.executable, os.path.join(HERE, 'f47d_read.py'), '--dir', d, '--tag', 'f47_rd'], capture_output=True, env=env)
        check('reader: subprocess output strict cp1250, STATUS ADMITTED', p.returncode == 0 and b'STATUS ADMITTED' in p.stdout and
              all(ch < 128 for ch in p.stdout))
        p = subprocess.run([sys.executable, os.path.join(HERE, 'next_f47d.py'), '--may', 'f47_rd', '--runs', os.path.join(root, 'empty')],
                           capture_output=True, env=env)
        check('next: subprocess output strict cp1250, MAY', p.returncode == 0 and p.stdout.startswith(b'MAY') and
              all(ch < 128 for ch in p.stdout))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print('ALL OK' if OK else 'FAILED')
    return 0 if OK else 1


if __name__ == '__main__':
    sys.exit(main())
