# F30a (HPP-706, ROADMAP s122 item 640(d)(1)(i)): the rtskip code of the session-127 build (98d98eee, commit defd2c91)
# against FS10 (worktree HEAD dc5d4712) and against main (HEAD of the run).  Checks:
#   C1  files of the resolution / capture / memo / hooks / register context with an EMPTY diff defd2c91..dc5d4712;
#   C2  renderDraw.cpp: every changed line of defd2c91..dc5d4712 is either the dead store t_rts_a (written, never read -
#       counted in defd2c91) or a line of the measurement knobs rbcen / rbslow / b2reuse (default 0);
#   C3  textureCache.cpp / textureCache.h / image.h / commandScheduler.cpp: every changed hunk is B42 (KYTY_FIX_B42) or
#       rbcen, and no changed line touches a field the latch reads (DANGER);
#   C5  guest_gpu (register setters, PM4 handlers, submission): every changed line is a measurement knob (rbcen, b2reuse,
#       bindlean) or the protceil re-arm call (knob 0: one empty-list test, graphicsRun.cpp comment); no hook / setter line;
#   C4  main (HEAD) against dc5d4712 on renderDraw.cpp / colorRenderTarget.cpp / depthRenderTarget.cpp: every added line is
#       KYTY_DIAG_F5 / KYTY_DIAG_F6 (counters, default 0) - no removed line, no rtskip site line;
#   NEG the classifiers reject planted rtskip lines (negative control).
# Exit 0 and ALL OK when every check holds.  usage: python code_f30a.py [<head commit>]
import re, subprocess, sys

REPO = 'C:/kyty/KytyPS5'
S127, FS10 = 'defd2c91', 'dc5d4712'
HEAD = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
R = 'src/graphics/host_gpu/renderer/'
NL = chr(10)


def git(*a):
    return subprocess.run(['git', '-C', REPO] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')


def is_change(ln):
    return (ln.startswith('+') or ln.startswith('-')) and not ln.startswith('+++') and not ln.startswith('---')


def changed(a, b, path):
    return [ln for ln in git('diff', '-U0', a, b, '--', path).split(NL) if is_change(ln)]


def hunks_of(a, b, path):
    out, cur = [], None
    for ln in git('diff', '-U0', a, b, '--', path).split(NL):
        if ln.startswith('@@'):
            cur = []
            out.append(cur)
        elif cur is not None and is_change(ln):
            cur.append(ln)
    return [h for h in out if h]


MEAS = re.compile(r'RbCen|B2Reuse|rbcen|rbslow|b2reuse|RebindSlowCensus|is booked here, outside mh_bind|'
                  r'that opens mh_bind - its price lands in mh_prog_us')
DEAD = re.compile(r'\bt_rts_a\b')
B42 = re.compile(r'[Bb]42|fce_materialize|QueryMetaFill|MetaFillQuery|FCE|fast-clear-eliminate|uint32_t guest_clear_regs')
# Fields the latch / place A / place B read (renderDraw.cpp RtsPlaceA, RtsPlaceB): a changed line writing one of them in
# the texture cache would be a new source the latch must see.
DANGER = re.compile(r'bind_stamp|MetaEpoch|m_meta_epoch|state_serial|needs_rebind|pending_levels|\bregistered\b|'
                    r'backing\.image|source_size|source_first_level|view_fast|\bmemo\b|is_bound|htile_clear_mask|'
                    r'attachment_layout|attachment_access|depth_id')
DIAG = re.compile(r'DiagF5|DiagF6|diagF5\.h|DIAG_F5|DIAG_F6|host_slots|mrt_count|mrt\[|mrt\s+=|ps_on|DrawKind|NoteDraw|'
                  r'^\+\s*[{}]?\s*$|^\+\s*\}\s*$|^\+\s*//|host_count|const auto&\s+ps\s+=|for \(const auto& output|'
                  r'output\.kind|\? DiagF6|: indirect|: indexed|PrepareDrawRenderState / RtsPlaceA fork|program by guest index|'
                  r'static void DiagF6NoteDraw|bool indexed\) \{|if \(DiagF6::On\(\)\)|has_dcc|depth_clear_enable \|\| rc\.stencil')
SITE = re.compile(r'\bt_rts\b|Rts[A-Z]\w*\(|RtSkip|PrepareDrawRenderState\(|AcquireRenderTargets\(|AcquireTargetView\(')
GPUOK = re.compile(r'BindLean|bindlean|protceil|ProtCeilRearm|on the GuestGpu thread before the submission|'
                   r'callback, with no region|^\+\s*//')
HOOK = re.compile(r'Rk3::|NoteWrite|NoteSlot|NoteObject')

ok = True
print('C1 empty diffs %s..%s' % (S127, FS10))
for p in [R + 'colorRenderTarget.cpp', R + 'depthRenderTarget.cpp', R + 'render.h', R + 'renderMemo.h',
          'src/common/rk3Census.h', 'src/graphics/guest_gpu/hardwareContext.h']:
    exists = git('cat-file', '-t', '%s:%s' % (FS10, p)).strip() == 'blob'
    n = len(changed(S127, FS10, p))
    good = exists and n == 0
    ok &= good
    print('  %-4s %s exists=%s changed_lines=%d' % ('OK' if good else 'BAD', p, exists, n))

print('C2 renderDraw.cpp %s..%s' % (S127, FS10))
c2 = changed(S127, FS10, R + 'renderDraw.cpp')
bad = [l for l in c2 if not (MEAS.search(l) or DEAD.search(l))]
dead_lines = [l for l in git('show', '%s:%s' % (S127, R + 'renderDraw.cpp')).split(NL) if DEAD.search(l)]
reads = [l for l in dead_lines if re.search(r'\bt_rts_a\b(?!\s*=)', l) and 'constinit' not in l]
good = not bad and len(dead_lines) == 3 and not reads
ok &= good
print('  %-4s changed %d lines (rbcen/b2reuse/rbslow %d, t_rts_a %d), unexplained %d; t_rts_a in %s: %d lines, reads %d'
      % ('OK' if good else 'BAD', len(c2), sum(1 for l in c2 if MEAS.search(l)), sum(1 for l in c2 if DEAD.search(l)),
         len(bad), S127, len(dead_lines), len(reads)))
for l in bad[:10]:
    print('     ', l[:160])

print('C3 texture cache / image / scheduler %s..%s' % (S127, FS10))
for p in [R + 'cache/textureCache.cpp', R + 'cache/textureCache.h', R + 'image/image.h', R + 'commandScheduler.cpp']:
    hunks = hunks_of(S127, FS10, p)
    c3 = [l for h in hunks for l in h]
    bad = [h[0] for h in hunks if not any(B42.search(l) or MEAS.search(l) for l in h)]
    danger = [l for l in c3 if DANGER.search(l)]
    good = not bad and not danger
    ok &= good
    print('  %-4s %s hunks %d changed %d, hunks without B42/rbcen %d, lines touching a latch field %d' % (
          'OK' if good else 'BAD', p, len(hunks), len(c3), len(bad), len(danger)))
    for l in (bad + danger)[:12]:
        print('     ', l[:160])

print('C5 guest_gpu %s..%s' % (S127, FS10))
c5 = changed(S127, FS10, 'src/graphics/guest_gpu')
bad = [l for l in c5 if not (MEAS.search(l) or GPUOK.search(l))]
hooks = [l for l in c5 if HOOK.search(l)]
good = not bad and not hooks
ok &= good
print('  %-4s changed %d lines, unexplained %d, hook lines %d' % ('OK' if good else 'BAD', len(c5), len(bad), len(hooks)))
for l in (bad + hooks)[:10]:
    print('     ', l[:160])

print('C4 main (%s) against %s' % (HEAD, FS10))
for p in [R + 'renderDraw.cpp', R + 'colorRenderTarget.cpp', R + 'depthRenderTarget.cpp']:
    c4 = changed(FS10, HEAD, p)
    removed = [l for l in c4 if l.startswith('-')]
    site = [l for l in c4 if SITE.search(l) and 'RtsPlaceA fork' not in l]
    bad = [l for l in c4 if not DIAG.search(l)]
    good = not removed and not site and not bad
    ok &= good
    print('  %-4s %s added %d removed %d rtskip-site lines %d unexplained %d' % ('OK' if good else 'BAD', p,
          len(c4) - len(removed), len(removed), len(site), len(bad)))
    for l in (bad + site)[:12]:
        print('     ', l[:160])

print('NEG planted lines')
neg1 = ['+\tt_rts = 1;']
neg2 = ['-\t\t\tRtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd);']
neg3 = ['+\timage.bind_stamp.fetch_add(1); // B42']
neg4 = ['+\tCommon::Rk3::NoteWrite(this, 0);']
r1 = [l for l in neg1 if not (MEAS.search(l) or DEAD.search(l))]
r2 = [l for l in neg2 if SITE.search(l)]
r3 = [l for l in neg1 if not (B42.search(l) or MEAS.search(l))]
r4 = [l for l in neg3 if DANGER.search(l)]
r5 = [l for l in neg4 if HOOK.search(l)]
good = (len(r1), len(r2), len(r3), len(r4), len(r5)) == (1, 1, 1, 1, 1)
ok &= good
print('  %-4s C2 rejects %d/1, C4 site catches %d/1, C3 rejects %d/1, C3 danger catches %d/1, C5 hook catches %d/1' % (
      'OK' if good else 'BAD', len(r1), len(r2), len(r3), len(r4), len(r5)))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
