"""Track F link F20l2 (HPP-648; ROADMAP s122 item 574 (d), (e); item 581 (v)(2), (v)(5), (zh); item 584 (v); the rule of item 550 (g) with
the amendments of items 551 (v), 552 (v)(3), (g), 553 (v), 554 (g)): the reader of the repeated KYTY_DIAG_B32 controls b32_z0b, b32_ppb,
b32_pcb on the F20j4 test binary 2d0c8815, and the reference reread of the F20l log b32_pd (F20j2 test binary b9e0ee00) with theta_load.
NO VERDICT - F20m2 (lead).  theta_load is read from the seal (line 'theta_load: <x>', item 574 (b)(6): 0.4562).  ASCII only.

    python b32_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f20l2; b32_pd - files of
                                                                    C:/kyty/f287/f20l, the reference reread of item 574 (e))
    python b32_read.py --dir <fixture dir> --tag <tag> [--json <out>]
                                                                    fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt,
                                                                    installed_before.txt, installed_after.txt, manifest_cmp.txt,
                                                                    seal.md, load.json
    python b32_read.py --table [--runs <dir>]                       the table of item 550 (z)(5) over every runs/<tag>/read.json
    python b32_read.py --check-seal [--seal <md>]                   every 'seal: <sha256> <path>' line against the file

ATTRIBUTION of a hold frame (B5 / B33 / B1b / 'prio only' / 'nothing') - the F20c reader as is: f20e_read.py (copy of
C:/kyty/f287/f20e/f20e_read.py, sha256 F20E_SHA below, checked at import) - functions scan, attr, evaluate.  The RC13 member: the F20c
attribution of the log = the attribution of the same log without the lines that start with 'DiagB32' (checked on every tag).

THE RULE (item 550 (g); letters of item 551 (v), 552 (v)(3), (g), 553 (v), 554 (g)):
  base (RC15)     for a frame: the 10 nearest scene frames before and the 10 nearest after with dt_us < 100 000 (F20g s1.1); median of
                  their FrameTrace dt_us, lat_us, gpu_busy_us; E = dt_us - median dt_us.
  P_I             hold frames (dt_us >= 100 000, start >= 10 s of the scene, F20e definitions) the F20c reader did not attribute to B5,
                  B33 or B1b (those go to PK-A / reference).  K_I = 1 for a hold with >= 1 frame in P_I (item 552 (g)).
  INSTR_MADE      a frame of P_I with a DiagB32: line and FrameTrace dt_us - instr_us < 100 000: not in the count.
  in the count    P_I minus INSTR_MADE.
  class (first match):
   (i)   HOST_FREEZE  sgap_max_us >= 0.5 x E (needs the DiagB32: line)
   (ii)  NO_SAMPLES   no DiagB32: line with this n, or i2 = 0, or samples = 0, or no DiagB32-x line of this n, or a zero invariant of the
                      window != 0: slot_full_w, torn_w, ring_drop_w, sgap_bad_w, lines_cut_w, req_miss_w, sub_miss_w (item 552 (v)(3),
                      lead comment 4c26ed76 of HPP-648)
   (iii) HOST_LOAD    other_us >= theta_load x ncpu x window (window = dt_us of the DiagB32: line); theta_load from the seal (0.4562,
                      item 574 (b)(6)); the ratio other_us / (ncpu x window) is printed
   (iv)  chain from the holder: the output thread (vo_slot) if FrameTrace lat_us - median lat_us >= 0.5 x E, else flip_slot.  At a
         thread, by shares of the window samples (count >= 0.5 x samples; ties - the order H > W > R > Sr > Sw > S, inside H and W the
         larger count, then the enum order):
           H:<call>  protect / fault / drain / qlock -> EMU_CALL:<call>; present / acquire / qsubmit / semwait -> RC7 split:
                     EMU_LOCK (another thread with H:qlock >= 0.5 x samples of the window), else DRV_GPU (FrameTrace gpu_busy_us >= median
                     gpu_busy_us + 0.5 x E), else DRV_HOST; printed 'EMU_CALL:<call>><split>'
           W:<kind>  sleep -> GUEST_SLEEP:sleep; else the -w record of this thread and kind with the largest overlap_us (item 574 (d)):
                     to = 1 with a guest deadline -> GUEST_SLEEP:<kind> (RC5 (v), item 581 (v)(5): a GUEST kind, or an EMU kind with
                     req_us > 0); else a step to the record waker (>= 0); else a step to the record peer (>= 0); else (as before) for
                     mutex a step to the -t peer; else EMU_WAIT:<kind> for an EMU kind (item 574 (d), 581 (v)(5): EmuMutex .. Av,
                     vblank, audio, aio, net, emu_join; no RC6) and GUEST_SLEEP:<kind> for a GUEST kind (RC6)
           R         EMU_RUN:<role> (role != guest) / GUEST_RUN:<name> (role guest)
           Sr        HOST_PREEMPT
           Sw or S   UNMARKED:<name> (kstate = 0: 'preempted or waiting outside the marks, not distinguishable')
           none      UNDETERMINED
         RC6: GUEST_RUN / GUEST_SLEEP stays only when GuestGpu (gpu_slot) has R + sum H < 0.5 x samples and W:gpu_regmem < 0.5 x
         samples; else GUEST_POLL (terminal; the GuestGpu state is printed); no GuestGpu row -> UNDETERMINED.
         Steps: the holder + at most 3 steps (4 threads); a 4th step, a cycle or a thread without a -t row -> UNDETERMINED.
  family          the class without its ':<detail>'; for a driver call the split (EMU_LOCK / DRV_GPU / DRV_HOST).
PK-A (item 550 (d)(7))  the B5 hold frames classified by (i)-(iv) (no count gate); armed member: EMU_RUN:Gpu or a path EMU_CALL:<...> that
                  ends on GuestGpu.
STAND (pp / pc)   the frames of the 3 FrameTrace lines after the line 'TestB32: fire'; the stand frame - the longest of them.
LOAD (pd / pd2)   load.json of the harness loader: n_start = last FrameTrace n of the live log at the burst start, n_end - at its end;
                  load frames = n in [n_start, n_end + 3]; for each one with a DiagB32: line other_us / (ncpu x window).
U5 (item 550 (zh), first and fourth members on the controls): median FrameTrace dt_us of the scene frames idx 723..828 against the F20e
                  base; sum of the _w invariants over every DiagB32-x line of the tag.  Second and third members are printed (reference).
INTERFERENCE (admission fails, the tag is repeated, item 550 (z)(4)): see ADMISSION in read_tag; rep_drop != 0 (item 551 (v)).
"""
import hashlib
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f20e_read as F  # noqa: E402  (the F20c reader of F20e, unchanged)

F20E_SHA = '5a986c03d161b9a5c52d589ad1da87e4676ceb9bac61acaeaa8f2131525400fa'
G = 'C:/kyty/f287/f20l2'
SEAL_PATH = G + '/pred/f20l2_seal.md'
G_F20L = 'C:/kyty/f287/f20l'          # the F20l files: reference reread of b32_pd (item 574 (e))
SEAL_F20L = G_F20L + '/pred/f20l_seal.md'
BIN_F20J2 = 'b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91'    # F20j2 test binary of the F20l log b32_pd
THETA_RX = re.compile(r'^theta_load: ([0-9]+\.[0-9]+)[ \t]*$', re.M)
SLOW_US = 100000
SHORT_US = 70000
WIN_US = 10000000
B2_LO, B2_HI = 723, 828
NEIGH = 10
HOLD_S = 330
BIN_TEST = '2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7'     # F20j4 test binary, items 583, 584 (g)
BIN_FS8 = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'      # installed FS8 (before = after)
SIG_FS8 = '9177b4267de1fb8bac7d1113afd8733210addfac'
HARN = {'KYTY_FRAME_TRACE', 'KYTY_GPU_HANG_ABORT_S', 'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_QUEUE_TRACE', 'KYTY_GPU_CLOCK_PIN',
        'KYTY_GPU_MARKERS', 'KYTY_GUEST_ARGS', 'KYTY_REC'}
FORM = {'b32_z0b': dict(KYTY_DIAG_B32='0', KYTY_GPU_WALL='1'),
        'b32_ppb': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1', KYTY_TEST_B32='60:present:200'),
        'b32_pcb': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1', KYTY_TEST_B32='60:gpusleep:200'),
        'b32_pd': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1')}
LOADER = {'b32_pd': 'all'}
TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd)(_r[1-6])?$')
# U5 base (item 550 (zh); b32_base.py over 41 holds F20a 8 + F20c 22 + F20e 11 and the 11 tags of F20e - filled before the seal)
U5_BASE = dict(slow70_per_hold=0.561, med_dt_b2win=36171.5, mean_dt_b5=134767.7)    # base/base_f20l2.txt (2026-10-05 18:42Z)
ZERO_W = ('slot_full_w', 'torn_w', 'ring_drop_w', 'sgap_bad_w', 'lines_cut_w', 'req_miss_w', 'sub_miss_w')
DRIVER = ('present', 'acquire', 'qsubmit', 'semwait')
CALLS = ('present', 'acquire', 'qsubmit', 'qlock', 'drain', 'semwait', 'protect', 'fault')
# enum Wait of 4371ff4b / f2307b02 src/common/diagB32.h in order (WaitName), item 574 (g)(1), 581 (v)(5)
WAITS = ('cond', 'mutex', 'sem', 'psem', 'evf', 'eq', 'sleep', 'gpu_idle', 'gpu_regmem',
         'emu_mutex', 'gpu_wait', 'gpu_cmd', 'flip_slot', 'flip_done', 'flip_cancel', 'flip_req', 'vo_pace', 'relay', 'frame_pool',
         'rec_wait', 'rec_idle', 'asub_idle', 'asub_drain', 'ops_wait', 'ops_idle', 'pipe_wait', 'pcopy', 'pm_drain', 'vma_flush',
         'rec_queue', 'main_task', 'main_idle', 'spin', 'av',
         'vblank', 'once', 'join', 'addr', 'aio', 'fiber', 'audio', 'ult', 'net', 'rwlock', 'emu_join')
# EMU_WAIT kinds (item 574 (d); item 581 (v)(5): who clears the wait condition - the device emulation, the host I/O or an emulator thread)
EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net', 'emu_join')
# GUEST_SLEEP kinds: the older ones and the guest HLE kinds of item 581 (v)(5)
GUEST_WAITS = WAITS[:9] + ('once', 'join', 'addr', 'fiber', 'ult', 'rwlock')
NAME_OK = re.compile(r'^[A-Za-z0-9_.-]{1,31}$')
FTX = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) lat_us=(\d+)')
GBUSY = re.compile(rb' gpu_busy_us=(\d+)')
CPUG = re.compile(rb' cpu_gpu_us=(\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'


def sha_file(path):
    return F.sha_file(path)


def kv(line):
    """'DiagB32-t: n=1 a=2 ...' -> dict of str; the first token (prefix) is skipped."""
    d = {}
    for tok in line.split(' ')[1:]:
        k, s, v = tok.partition('=')
        if s:
            d[k] = v
    return d


def num(v, default=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def klist(v):
    """'cond:12,mutex:3' / '-' -> dict name -> count ('?' kept)."""
    out = {}
    if not v or v == '-':
        return out
    for part in v.split(','):
        k, _, c = part.rpartition(':')
        out[k] = out.get(k, 0) + (num(c, 0) or 0)
    return out


def parse_diag(raw):
    """raw: list of (kind, text) of one n -> dict hdr / t / w / c / x."""
    d = dict(hdr=None, t=[], w=[], c=[], x=None, dup=0)
    for kind, text in raw:
        f = kv(text)
        if kind == 'hdr':
            if d['hdr'] is not None:
                d['dup'] += 1
                continue
            h = dict((k, num(v, v)) for k, v in f.items())
            d['hdr'] = h
        elif kind == 't':
            r = dict((k, num(v, v)) for k, v in f.items())
            r['W'] = klist(f.get('W'))
            r['H'] = klist(f.get('H'))
            r['SwR'] = klist(f.get('SwR'))
            d['t'].append(r)
        elif kind == 'w':
            d['w'].append(dict((k, num(v, v)) for k, v in f.items()))
        elif kind == 'c':
            d['c'].append(dict((k, num(v, v)) for k, v in f.items()))
        elif kind == 'x':
            if d['x'] is not None:
                d['dup'] += 1
                continue
            d['x'] = dict((k, num(v, v)) for k, v in f.items())
    return d


def scan_b32(path):
    """One pass: FrameTrace fields of every line, DiagB32* lines keyed by n, stand lines, window events."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    ft = {}
    diag = {}
    r = dict(ft=ft, diag=diag, mode=[], invalid=[], test=[], recovering=0, minimized=0, diag_lines=0, diag_bad_prefix=0, ft_order=[],
             sig=[], variant_dir=[])
    last_n = None
    for line in fh:
        if line.startswith(b'FrameTrace: n='):
            m = FTX.match(line)
            if m:
                n = int(m.group(1))
                g = GBUSY.search(line)
                c = CPUG.search(line)
                ft[n] = (int(m.group(2)), int(m.group(3)), int(g.group(1)) if g else None, int(c.group(1)) if c else None)
                r['ft_order'].append(n)
                last_n = n
            continue
        if line.startswith(b'DiagB32'):
            r['diag_lines'] += 1
            t = line.decode('ascii', 'replace').rstrip('\r\n')
            if t.startswith('DiagB32: mode='):
                r['mode'].append(t[:300])
                continue
            if t.startswith('DiagB32: config'):
                r['invalid'].append(t[:200])
                continue
            kind = {'DiagB32: ': 'hdr', 'DiagB32-t: ': 't', 'DiagB32-w: ': 'w', 'DiagB32-c: ': 'c', 'DiagB32-x: ': 'x'}
            k = None
            for p, kk in kind.items():
                if t.startswith(p):
                    k = kk
                    break
            n = num(kv(t).get('n')) if k else None
            if k is None or n is None:
                r['diag_bad_prefix'] += 1
                continue
            diag.setdefault(n, []).append((k, t))
            continue
        if b'DiagB32' in line:
            r['diag_bad_prefix'] += 1      # RC13: a DiagB32 text not from the first column
        if line.startswith(b'ShaderSeed: compatibility=') and len(r['sig']) < 4:
            m = SEED.search(line)
            r['sig'].append(m.group(1).decode('ascii') if m else '?')
            continue
        if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
            r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
            continue
        if line.startswith(b'TestB32:'):
            r['test'].append(dict(text=line.decode('ascii', 'replace').strip()[:160], after_n=last_n))
            continue
        if b'Recovering Vulkan swapchain' in line:
            r['recovering'] += 1
        if b'Window ' in line and F.MINI.search(line):
            r['minimized'] += 1
    fh.close()
    r['diag'] = dict((n, parse_diag(v)) for n, v in diag.items())
    return r


def neighbours(frames, i):
    """frames: scene frames (F.scan tuples) in order; the 10 nearest before and after with dt < 100 ms (F20g s1.1)."""
    out = []
    j = i - 1
    while j >= 0 and len(out) < NEIGH:
        if frames[j][2] < SLOW_US:
            out.append(frames[j][1])
        j -= 1
    k = 0
    j = i + 1
    while j < len(frames) and k < NEIGH:
        if frames[j][2] < SLOW_US:
            out.append(frames[j][1])
            k += 1
        j += 1
    return out


def base_of(ft, ns):
    vals = [ft[n] for n in ns if n in ft]
    if not vals:
        return None
    gb = [v[2] for v in vals if v[2] is not None]
    return dict(dt=statistics.median(v[0] for v in vals), lat=statistics.median(v[1] for v in vals),
                gbusy=statistics.median(gb) if gb else None, k=len(vals))


def dominant(row, samples):
    half = 0.5 * samples
    hs = [(row['H'].get(c, 0), -i, c) for i, c in enumerate(CALLS) if row['H'].get(c, 0) >= half]
    if hs:
        return 'H', max(hs)[2]
    ws = [(row['W'].get(k, 0), -i, k) for i, k in enumerate(WAITS) if row['W'].get(k, 0) >= half]
    if ws:
        return 'W', max(ws)[2]
    for st in ('R', 'Sr', 'Sw', 'S'):
        if (num(row.get(st), 0) or 0) >= half:
            return st, None
    return None, None


def is_zero_bad(x):
    if x is None:
        return ['no -x line']
    return [k for k in ZERO_W if num(x.get(k), 0) != 0]


def chain(d, holder, fr, b, e_us, steps=None):
    """Item 550 (g)(2)(iv) with RC6, RC7 and the amendment of item 574 (d) / 581 (v)(5).  Returns (class, family, path list, terminal
    role, note); steps (a list) gets one dict per visited thread (slot, name, role, R, Sw, S, samples, how it was reached)."""
    steps = [] if steps is None else steps
    how = 'holder'
    h = d['hdr']
    samples = h['samples']
    rows = dict((t['slot'], t) for t in d['t'])
    gpu = rows.get(h.get('gpu_slot'))
    path = []

    def guest_check(cls):
        if gpu is None:
            return 'UNDETERMINED', 'UNDETERMINED', 'no GuestGpu -t row for RC6'
        busy = (num(gpu.get('R'), 0) or 0) + sum(gpu['H'].values())
        reg = gpu['W'].get('gpu_regmem', 0)
        if busy < 0.5 * samples and reg < 0.5 * samples:
            return cls, cls.split(':')[0], ''
        return 'GUEST_POLL', 'GUEST_POLL', 'RC6: GuestGpu R+H %d, W:gpu_regmem %d of %d' % (busy, reg, samples)

    cur = holder
    visited = []
    for step in range(4):
        row = rows.get(cur)
        if row is None:
            return 'UNDETERMINED', 'UNDETERMINED', path, None, 'no -t row for slot %s' % cur
        visited.append(cur)
        steps.append(dict(slot=cur, name=row.get('name'), role=row.get('role'), R=num(row.get('R'), 0), Sw=num(row.get('Sw'), 0),
                          S=num(row.get('S'), 0), samples=samples, how=how))
        st, x = dominant(row, samples)
        path.append('%s(%s)%s' % (row.get('name'), row.get('role'), ('=' + st + (':' + x if x else '')) if st else '=none'))
        role = row.get('role')
        if st == 'H':
            if x in DRIVER:
                others = [t for t in d['t'] if t['slot'] != cur and t['H'].get('qlock', 0) >= 0.5 * samples]
                if others:
                    sp = 'EMU_LOCK'
                elif fr['gbusy'] is not None and b['gbusy'] is not None and fr['gbusy'] >= b['gbusy'] + 0.5 * e_us:
                    sp = 'DRV_GPU'
                else:
                    sp = 'DRV_HOST'
                return 'EMU_CALL:%s>%s' % (x, sp), sp, path, role, ''
            return 'EMU_CALL:%s' % x, 'EMU_CALL', path, role, ''
        if st == 'W':
            if x == 'sleep':
                c, fam, note = guest_check('GUEST_SLEEP:sleep')
                return c, fam, path, role, note
            emu = x in EMU_WAITS
            recs = [w for w in d['w'] if w.get('slot') == cur and w.get('kind') == x]
            best = max(recs, key=lambda w: (num(w.get('overlap_us'), 0) or 0)) if recs else None
            target = None
            to = best is not None and best.get('to') == 1
            if to and (not emu or (num(best.get('req_us'), 0) or 0) > 0):
                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)
                return c, fam, path, role, (note + ' timeout record').strip()
            wk = num(best.get('waker'), -1) if best is not None else -1
            rp = num(best.get('peer'), -1) if best is not None else -1
            pr = num(row.get('peer'), -1)
            if wk is not None and wk >= 0:
                target, how = wk, 'waker'
            elif rp is not None and rp >= 0:
                target, how = rp, 'peer'
            elif x == 'mutex' and pr is not None and pr >= 0:
                target, how = pr, 'tpeer'
            if target is None:
                var = ('; executor variant (the -t peer for any kind): step to slot %d' % pr) if pr is not None and pr >= 0 else ''
                if to:
                    var += '; executor variant (RC5 (v) to = 1 for every kind): GUEST_SLEEP:%s' % x
                if emu:
                    return 'EMU_WAIT:%s' % x, 'EMU_WAIT', path, role, ('no waker, no peer' + (' (timeout record, req_us 0)' if to else '')
                                                                        + var)
                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)
                return c, fam, path, role, (note + ' no waker, no peer' + var).strip()
            path[-1] += '->' + how
            if step == 3:
                return 'UNDETERMINED', 'UNDETERMINED', path, role, '> 3 steps'
            if target in visited:
                return 'UNDETERMINED', 'UNDETERMINED', path, role, 'cycle at slot %s' % target
            cur = target
            continue
        if st == 'R':
            if role != 'guest':
                return 'EMU_RUN:%s' % role, 'EMU_RUN', path, role, ''
            c, fam, note = guest_check('GUEST_RUN:%s' % row.get('name'))
            return c, fam, path, role, note
        if st == 'Sr':
            return 'HOST_PREEMPT', 'HOST_PREEMPT', path, role, ''
        if st in ('Sw', 'S'):
            note = 'kstate=0: preempted or waiting outside the marks (not distinguishable)' if h.get('kstate') == 0 else ''
            return 'UNMARKED:%s' % row.get('name'), 'UNMARKED', path, role, note
        sws = (num(row.get('Sw'), 0) or 0) + (num(row.get('S'), 0) or 0)
        var = ('; executor variant (Sw + S >= 50 %%): UNMARKED:%s' % row.get('name')) if sws >= 0.5 * samples else ''
        return 'UNDETERMINED', 'UNDETERMINED', path, role, 'no state >= 50 %' + var
    return 'UNDETERMINED', 'UNDETERMINED', path, None, '> 3 steps'


def classify(fr, d, b, theta):
    """fr: dict n, dt, lat, gbusy; d: parsed diag of n or None; b: base.  Item 550 (g)(2) first match."""
    e_us = fr['dt'] - b['dt'] if b else None
    out = dict(E=e_us, holder=None, path=[], role=None, note='')
    h = d['hdr'] if d else None
    if h is not None and e_us is not None and (num(h.get('sgap_max_us'), 0) or 0) >= 0.5 * e_us:
        out.update(cls='HOST_FREEZE', family='HOST_FREEZE')
        return out
    bad = []
    if h is None:
        bad.append('no DiagB32: line')
    else:
        if h.get('i2') != 1:
            bad.append('i2=%s' % h.get('i2'))
        if not h.get('samples'):
            bad.append('samples=0')
        bad += is_zero_bad(d['x'])
    if bad:
        out.update(cls='NO_SAMPLES', family='NO_SAMPLES', note=', '.join(bad))
        return out
    win = num(h.get('dt_us'), 0) or 0
    ncpu = num(h.get('ncpu'), 0) or 0
    other = num(h.get('other_us'), 0) or 0
    out['load_ratio'] = round(other / (ncpu * win), 4) if ncpu and win else None
    if theta is not None and ncpu and win and other >= theta * ncpu * win:
        out.update(cls='HOST_LOAD', family='HOST_LOAD')
        return out
    if b is None:
        out.update(cls='UNDETERMINED', family='UNDETERMINED', note='no base')
        return out
    vo, fl = num(h.get('vo_slot'), -1), num(h.get('flip_slot'), -1)
    holder = vo if fr['lat'] - b['lat'] >= 0.5 * e_us else fl
    out['holder'] = 'output' if holder == vo and fr['lat'] - b['lat'] >= 0.5 * e_us else 'flip'
    if holder is None or holder < 0:
        out.update(cls='UNDETERMINED', family='UNDETERMINED', note='no holder slot')
        return out
    steps = []
    cls, fam, path, role, note = chain(d, holder, fr, b, e_us, steps)
    gs = num(h.get('gpu_slot'), -1)
    gpu_steps = [s for s in steps if s['slot'] == gs]
    out.update(cls=cls, family=fam, path=path, role=role, note=note, steps=steps,
               gpu_in_chain=bool(gpu_steps),
               gpu_sw_or_s50=any(s['Sw'] >= 0.5 * s['samples'] or s['S'] >= 0.5 * s['samples'] for s in gpu_steps),
               gpu_sw_plus_s50=any(s['Sw'] + s['S'] >= 0.5 * s['samples'] for s in gpu_steps))
    return out


def rc13_equal(log_path, tmp_dir):
    """The F20c attribution of the log = of the same log without the lines starting with 'DiagB32' (RC13)."""
    tmp = os.path.join(tmp_dir, '_rc13_stripped.txt')
    n_out = 0
    with open(log_path, 'rb') as fi, open(tmp, 'wb') as fo:
        for line in fi:
            if line.startswith(b'DiagB32'):
                n_out += 1
                continue
            fo.write(line)
    try:
        a = F.scan(log_path)
        s = F.scan(tmp)
    finally:
        os.remove(tmp)
    ea, es = F.evaluate(a, BIN_TEST), F.evaluate(s, BIN_TEST)
    same = a['frames'] == s['frames'] and ea['hold_frames'] == es['hold_frames']
    return same, n_out, a


def read_log(path, theta, load, tmp_dir):
    """All members of one log (no admission): returns dict."""
    same, stripped, r = rc13_equal(path, tmp_dir)
    e = F.evaluate(r, BIN_TEST)
    s = scan_b32(path)
    ft, diag = s['ft'], s['diag']
    frames = r['frames']                      # (idx, n, dt, t_before, ir, gcn, pcs, trip, prio, prio_us)
    pos = dict((x[1], i) for i, x in enumerate(frames))
    hold = e['hold']
    res = dict(rc13_equal=same, rc13_stripped=stripped, hold=hold, scene_s=e['scene_s'], first_n=e['first_n'], frames_n=len(frames),
               sig=s['sig'], variant_dir=s['variant_dir'], mode=s['mode'][:2], invalid=s['invalid'][:2], diag_lines=s['diag_lines'], diag_bad_prefix=s['diag_bad_prefix'],
               diag_n=len(diag), recovering=s['recovering'], minimized=s['minimized'], test=s['test'][:6],
               dup=sum(d['dup'] for d in diag.values()))
    rows = []
    for x in frames:
        if not (x[2] >= SLOW_US and x[3] >= WIN_US):
            continue
        n = x[1]
        att = F.attr(x, BIN_TEST, 'letter')
        f = ft.get(n)
        b = base_of(ft, neighbours(frames, pos[n]))
        fr = dict(n=n, dt=x[2], lat=f[1] if f else None, gbusy=f[2] if f else None, cpu_gpu=f[3] if f else None)
        d = diag.get(n)
        h = d['hdr'] if d else None
        row = dict(idx=x[0], n=n, dt_us=x[2], t_s=round(x[3] / 1e6, 3), attr=att, lat_us=fr['lat'], gbusy_us=fr['gbusy'],
                   base=b, diag=h is not None, instr_us=num(h.get('instr_us')) if h else None,
                   kq_n=num(h.get('kq_n')) if h else None, kq_us=num(h.get('kq_us')) if h else None,
                   m5r_us=num(h.get('m5r_us')) if h else None, kstate=num(h.get('kstate')) if h else None,
                   diag_dt_us=num(h.get('dt_us')) if h else None, samples=num(h.get('samples')) if h else None,
                   prev_slow=(pos[n] > 0 and frames[pos[n] - 1][2] >= SLOW_US))
        row['p_i'] = att not in ('B5', 'B33', 'B1b')
        row['instr_made'] = bool(row['p_i'] and h is not None and x[2] - (row['instr_us'] or 0) < SLOW_US)
        row['in_count'] = row['p_i'] and not row['instr_made']
        if d is not None and d['x'] is not None:
            row['zero_w'] = dict((k, num(d['x'].get(k), 0)) for k in ZERO_W)
            row['slot_full_w'] = num(d['x'].get('slot_full_w'), 0)
            row['ring_hold_w'] = num(d['x'].get('ring_hold_w'))
        c = classify(fr, d, b, theta) if b else dict(cls='UNDETERMINED', family='UNDETERMINED', note='no base', path=[])
        row.update(cls=c['cls'], family=c['family'], path=c.get('path'), holder=c.get('holder'), term_role=c.get('role'),
                   note=c.get('note'), E=c.get('E'), load_ratio=c.get('load_ratio'), steps=c.get('steps'),
                   gpu_sw_or_s50=c.get('gpu_sw_or_s50'))
        if d is not None:
            row['bad_names'] = [t.get('name') for t in d['t'] if not NAME_OK.match(str(t.get('name')))]
        rows.append(row)
    res['frames'] = rows
    pi = [x for x in rows if x['p_i']]
    cnt = [x for x in rows if x['in_count']]
    res['K_I'] = 1 if hold and pi else 0
    res['K'] = 1 if hold and cnt else 0
    res['P_I'] = len(pi)
    res['in_count'] = len(cnt)
    res['instr_made'] = sum(1 for x in pi if x['instr_made'])
    res['instr_share'] = round(res['instr_made'] / len(pi), 4) if pi else 'NOT EVALUABLE'
    res['kq0'] = sum(1 for x in pi if x['diag'] and x['kq_n'] == 0)
    res['kq0_share'] = round(res['kq0'] / len(pi), 4) if pi else 'NOT EVALUABLE'
    res['m5r'] = sum(1 for x in pi if (x['m5r_us'] or 0) > 0)
    res['prev_slow_in_count'] = sum(1 for x in cnt if x['prev_slow'])
    # reference over every frame >= 100 ms of the scene with a DiagB32: line (beside the P_I numbers)
    alld = [x for x in rows if x['diag']]
    alls = [(n, diag[n]['hdr']) for n in diag if diag[n]['hdr'] is not None and ft.get(n) and ft[n][0] >= SLOW_US]
    res['all_diag_frames'] = len(alls)
    res['all_instr_made'] = sum(1 for n, h in alls if ft[n][0] - (num(h.get('instr_us'), 0) or 0) < SLOW_US)
    res['all_kq0'] = sum(1 for n, h in alls if num(h.get('kq_n')) == 0)
    res['all_m5r'] = sum(1 for n, h in alls if (num(h.get('m5r_us'), 0) or 0) > 0)
    res['hold_class'] = max(cnt, key=lambda x: x['dt_us'])['cls'] if cnt and hold else None
    res['pk_a'] = [dict(n=x['n'], dt_us=x['dt_us'], cls=x['cls'], term_role=x['term_role']) for x in rows if x['attr'] == 'B5']
    res['pk_a_armed'] = sum(1 for x in rows if x['attr'] == 'B5' and armed_b5(x))
    res['zero_w_sum'] = dict((k, sum(num((d['x'] or {}).get(k), 0) or 0 for d in diag.values())) for k in ZERO_W)
    lastx = None
    for n in sorted(diag):
        if diag[n]['x'] is not None:
            lastx = diag[n]['x']
    res['x_last'] = lastx
    res['rep_drop'] = num((lastx or {}).get('rep_drop'), 0) or 0
    # item 554 (v)(1), 574 (g)(5): Z1 counter ring_hold_w over every -x line of the tag and on the hold frames (reference, not a member)
    res['ring_hold_w_sum'] = sum(num((d['x'] or {}).get('ring_hold_w'), 0) or 0 for d in diag.values())
    res['ring_hold_w_frames'] = sum(1 for x in rows if (x.get('ring_hold_w') or 0) > 0)
    res['ring_hold_w_field'] = sum(1 for d in diag.values() if d['x'] is not None and 'ring_hold_w' in d['x'])
    res['bad_names'] = sorted(set(nm for x in rows for nm in x.get('bad_names', [])))
    res['slot_full_on_nosamples'] = sum(1 for x in rows if x['cls'] == 'NO_SAMPLES' and (x.get('slot_full_w') or 0) != 0)
    # i5 / i4 checks (reference)
    res['i5_bad'] = sum(1 for x in rows if x['diag'] and abs((x['diag_dt_us'] or 0) - x['dt_us']) > 1000)
    # U5
    win = [x for x in frames if B2_LO <= x[0] <= B2_HI]
    res['u5_med_dt'] = statistics.median(x[2] for x in win) if len(frames) >= B2_HI else None
    res['u5_slow70'] = sum(1 for x in frames if x[2] >= SHORT_US and x[3] >= WIN_US and F.attr(x, BIN_TEST, 'letter') != 'B5' and
                          not (x[2] >= SLOW_US and n_instr(x[1], ft, diag)))
    b5 = [x[2] for x in frames if x[2] >= SLOW_US and x[3] >= WIN_US and F.attr(x, BIN_TEST, 'letter') == 'B5']
    res['u5_b5_mean'] = round(sum(b5) / len(b5), 1) if b5 else None
    res['u5_b5_n'] = len(b5)
    # stand
    fires = [t for t in s['test'] if t['text'].startswith('TestB32: fire')]
    if fires and fires[0]['after_n'] is not None:
        order = s['ft_order']
        k = order.index(fires[0]['after_n']) if fires[0]['after_n'] in order else None
        nxt = order[k + 1:k + 4] if k is not None else []
        res['stand'] = [stand_row(n, ft, diag, frames, pos, theta) for n in nxt]
    else:
        res['stand'] = None
    # load window
    res['load'] = None
    if load:
        ns, ne = load.get('n_start'), load.get('n_end')
        if ns is not None and ne is not None:
            lw = []
            for n in range(ns, ne + 4):
                if n in ft:
                    h = diag[n]['hdr'] if n in diag and diag[n]['hdr'] is not None else None
                    ratio = None
                    if h is not None and num(h.get('ncpu')) and num(h.get('dt_us')):
                        ratio = round((num(h.get('other_us'), 0) or 0) / (num(h['ncpu']) * num(h['dt_us'])), 4)
                    cls = None
                    if n in pos and ft[n][0] >= SLOW_US:
                        cls = next((x['cls'] for x in rows if x['n'] == n), None)
                    lw.append(dict(n=n, dt_us=ft[n][0], diag=h is not None, other_us=num(h.get('other_us')) if h else None,
                                   ncpu=num(h.get('ncpu')) if h else None, ratio=ratio, cls=cls))
            res['load'] = dict(n_start=ns, n_end=ne, frames=lw, stretched=[x for x in lw if x['dt_us'] >= SLOW_US],
                               called=any(x['dt_us'] >= SLOW_US for x in lw))
    return res


def n_instr(n, ft, diag):
    d = diag.get(n)
    if d is None or d['hdr'] is None:
        return False
    return ft[n][0] - (num(d['hdr'].get('instr_us'), 0) or 0) < SLOW_US


def stand_row(n, ft, diag, frames, pos, theta):
    f = ft[n]
    b = base_of(ft, neighbours(frames, pos[n])) if n in pos else None
    fr = dict(n=n, dt=f[0], lat=f[1], gbusy=f[2])
    d = diag.get(n)
    c = classify(fr, d, b, theta) if b else dict(cls='UNDETERMINED', note='no base (not a scene frame)')
    ws = [dict(slot=w.get('slot'), kind=w.get('kind'), overlap_us=w.get('overlap_us'), waker=w.get('waker'), peer=w.get('peer'),
               to=w.get('to'), req_us=w.get('req_us'), open=w.get('open')) for w in (d['w'] if d else [])]
    return dict(n=n, dt_us=f[0], lat_us=f[1], base_lat=b['lat'] if b else None, cls=c.get('cls'), holder=c.get('holder'),
                path=c.get('path'), note=c.get('note'), steps=c.get('steps'), gpu_in_chain=c.get('gpu_in_chain'),
                gpu_sw_or_s50=c.get('gpu_sw_or_s50'), gpu_sw_plus_s50=c.get('gpu_sw_plus_s50'), w=ws,
                ring_hold_w=num((d['x'] or {}).get('ring_hold_w')) if d else None)


def armed_b5(x):
    if x['cls'] == 'EMU_RUN:Gpu':
        return True
    return x['cls'].startswith('EMU_CALL:') and x.get('term_role') == 'Gpu'


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), load=os.path.join(base, 'load.json'), tmp=base,
                 theta_src=os.path.join(base, 'seal.md'))
        return p
    gg, seal = (G_F20L, SEAL_F20L) if TAG_RX.match(tag) and TAG_RX.match(tag).group(1) == 'b32_pd' else (G, SEAL_PATH)
    d = os.path.join(gg, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(gg, 'log_%s.txt' % tag), stdout=os.path.join(gg, 'stdout_%s.txt' % tag), run=os.path.join(gg, '%s.json' % tag),
             idx=os.path.join(gg, 'rec_%s.mp4.idx' % tag), seal=seal, load=os.path.join(d, 'load.json'), tmp=os.path.join(G, 'runs'),
             theta_src=SEAL_PATH)
    return p


def read_theta(path):
    """theta_load from the line 'theta_load: <x>' of the seal (item 574 (b)(6), (e)); None if absent or not exactly one."""
    if not os.path.exists(path):
        return None
    m = THETA_RX.findall(open(path, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n'))
    return float(m[0]) if len(m) == 1 else None


def read_tag(tag, p):
    base_tag = TAG_RX.match(tag).group(1)
    form = FORM[base_tag]
    theta = read_theta(p['theta_src'])
    want_bin = BIN_F20J2 if base_tag == 'b32_pd' else BIN_TEST
    res = dict(tag=tag, form=base_tag, reader_sha256=sha_file(os.path.abspath(__file__)), f20e_read_sha256=sha_file(F.__file__),
               theta=theta)
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    res['binary_sha256'] = jbin
    inst_b = (F.text(p['installed_before']) or '').strip() or None
    inst_a = (F.text(p['installed_after']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (F.text(p['manifest_cmp']) or '').strip().splitlines()
    load = json.load(open(p['load'], encoding='utf-8')) if os.path.exists(p['load']) else None
    r = read_log(p['log'], theta, load, p['tmp']) if os.path.exists(p['log']) and theta is not None else None
    extra = dict((k, v) for k, v in env.items() if k not in HARN)
    diag_on = form['KYTY_DIAG_B32'] == '1'
    want_test = form.get('KYTY_TEST_B32')
    tests = (r or {}).get('test') or []
    adm = [
        ('tag json present', run is not None),
        ('theta_load from the seal %s (%s)' % (p['theta_src'], theta), theta is not None),
        ('json binary_sha256 = %s (%s)' % ('F20j2 test b9e0ee00 (reference reread)' if base_tag == 'b32_pd' else 'F20j4 test 2d0c8815',
                                           (jbin or '-')[:16]), jbin == want_bin),
        ('installed before = after = FS8 2c9b69b9 (%s / %s)' % ((inst_b or '-')[:8], (inst_a or '-')[:8]),
         inst_b == BIN_FS8 and inst_a == BIN_FS8),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env: harness constants + form %s (extra %s)' % (sorted(form.items()), sorted(extra.items())),
         run is not None and extra == form),
        ('last --vulkan-validation false (%s)' % F.last_flag(cmd, '--vulkan-validation'), F.last_flag(cmd, '--vulkan-validation') == 'false'),
        ('last --shader-validation false (%s)' % F.last_flag(cmd, '--shader-validation'), F.last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl underwater_aerial_garden (%s)' % (run or {}).get('guest_args'),
         (run or {}).get('guest_args') == '-lvl underwater_aerial_garden'),
        ('hold %d s (%s)' % (HOLD_S, (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_S),
        ('log present', r is not None),
        ('scene entered (first scene frame %s)' % (r or {}).get('first_n'), r is not None and r['first_n'] is not None),
        ('window events: minimized %s, Recovering Vulkan swapchain %s' % ((r or {}).get('minimized'), (r or {}).get('recovering')),
         r is not None and r['minimized'] == 0 and r['recovering'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
        ('DiagB32 mode line %s (%d)' % ('present' if diag_on else 'absent', len((r or {}).get('mode') or [])),
         r is not None and (len(r['mode']) == 1 if diag_on else (len(r['mode']) == 0 and r['diag_lines'] == 0))),
        ('no DiagB32 config invalid line', r is not None and not r['invalid']),
        ('translation signature = FS8 9177b426 and cache dir %s (%s / %s)' % (VARIANT_DIR, [x[:8] for x in (r or {}).get('sig') or []],
                                                                            (r or {}).get('variant_dir')),
         r is not None and r['sig'] == [SIG_FS8] and r['variant_dir'] == [VARIANT_DIR]),
        ('TestB32 lines %s (%s)' % ('armed, fire, done' if want_test else 'none', [t['text'][:40] for t in tests][:4]),
         r is not None and (stand_ok(tests, want_test) if want_test else not tests)),
        ('rep_drop 0 (%s)' % (r or {}).get('rep_drop'), r is not None and r['rep_drop'] == 0),
        ('loader ran (%s)' % (None if load is None else load.get('status')),
         (load is not None and load.get('status') == 'done' and load.get('mode') == LOADER[base_tag]) if base_tag in LOADER
         else load is None),
    ]
    res['admission'] = [[a, bool(b)] for a, b in adm]
    res['admitted'] = all(b for _, b in adm)
    res['log'] = r
    idx_n = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as fi:
            idx_n = sum(1 for _ in fi)
    gl = None
    gt = F.text(p['glitch'])
    if gt:
        mg = F.RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    res['ref'] = dict(glitches=gl, video_index=idx_n, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'),
                      installed_sha=(F.text(p['installed_sha']) or '').strip()[:64] or None,
                      signature=','.join((r or {}).get('sig') or []) or None)
    res['reading'] = 'INTERFERENCE (repeat, not counted)' if not res['admitted'] else 'ADMITTED (no verdict; reading - F20m)'
    return res


def stand_ok(tests, want):
    mode = want.split(':')[1]
    t = [x['text'] for x in tests]
    return (any(x.startswith('TestB32: armed') for x in t) and any(x.startswith('TestB32: fire mode=' + mode) for x in t)
            and any(x.startswith('TestB32: done mode=' + mode) for x in t))


def u5_line(r):
    b = U5_BASE
    out = []
    if r.get('u5_med_dt') is not None and b['med_dt_b2win']:
        dev = (r['u5_med_dt'] - b['med_dt_b2win']) / b['med_dt_b2win']
        out.append('U5(1) median dt_us idx 723..828 %s vs F20e %s: %+.4f (member > 0.02: %s)' % (
            r['u5_med_dt'], b['med_dt_b2win'], dev, 'yes' if abs(dev) > 0.02 else 'no'))
    else:
        out.append('U5(1) median dt_us idx 723..828 %s (base %s)' % (r.get('u5_med_dt'), b['med_dt_b2win']))
    hs = 1 if r.get('hold') else 0
    out.append('U5(2) frames >= 70 ms (>= 10 s, no B5, no INSTR_MADE) %s per hold %s (base %s, member > 1.5 x base: %s) [reference]' % (
        r.get('u5_slow70'), hs, b['slow70_per_hold'],
        'yes' if hs and b['slow70_per_hold'] and r['u5_slow70'] > 1.5 * b['slow70_per_hold'] else 'no'))
    out.append('U5(3) mean dt_us of B5 frames %s (n %s; base %s, member > 1.25 x base: %s) [reference]' % (
        r.get('u5_b5_mean'), r.get('u5_b5_n'), b['mean_dt_b5'],
        'yes' if r.get('u5_b5_mean') and b['mean_dt_b5'] and r['u5_b5_mean'] > 1.25 * b['mean_dt_b5'] else 'no'))
    z = r.get('zero_w_sum') or {}
    out.append('U5(4) zero invariants, sum of _w over the tag %s: %s' % (z, 'NONZERO' if any(z.values()) else 'all 0'))
    return out


def rows_out(res):
    out = ['tag %s (form %s)  reader sha256 %s  f20e_read sha256 %s  theta %s' % (
        res['tag'], res['form'], res['reader_sha256'], res['f20e_read_sha256'], res['theta'])]
    out.append('  ADMISSION %s' % ('PASS' if res['admitted'] else 'FAIL'))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    rf = res['ref']
    out.append('  binary %s; installed during the tag %s; translation signature (ShaderSeed line of the log) %s' % (
        res['binary_sha256'], rf['installed_sha'], rf['signature']))
    r = res['log']
    if r:
        out.append('  scene: first_n %s, frames %d, scene %.1f s, hold %s; DiagB32 lines %d (windows %d, bad prefix %d, dup %d); mode %s' % (
            r['first_n'], r['frames_n'], r['scene_s'], r['hold'], r['diag_lines'], r['diag_n'], r['diag_bad_prefix'], r['dup'],
            r['mode'][:1]))
        out.append('  RC13: F20c attribution with = without DiagB32 lines (%d stripped): %s' % (r['rc13_stripped'], 'EQUAL' if r['rc13_equal']
                                                                                                else 'DIFFERENT'))
        out.append('  K_I %d; K %d; P_I %d; in count %d; INSTR_MADE %d share %s (all frames >= 100 ms with a DiagB32 line: %d, INSTR_MADE %d)'
                   % (r['K_I'], r['K'], r['P_I'], r['in_count'], r['instr_made'], r['instr_share'], r['all_diag_frames'], r['all_instr_made']))
        out.append('  kq_n = 0: %d share %s (all: %d); m5r_us > 0: %d (all: %d); in count with the previous frame >= 100 ms: %d; '
                   'Recovering Vulkan swapchain %d' % (r['kq0'], r['kq0_share'], r['all_kq0'], r['m5r'], r['all_m5r'],
                                                       r['prev_slow_in_count'], r['recovering']))
        out.append('  hold class (longest frame in count): %s' % r['hold_class'])
        for x in r['frames'][:60]:
            out.append('    FRAME n %d dt_us %d t %.1f s attr %s | diag %s instr_us %s kq_n %s m5r_us %s kstate %s | E %s holder %s | %s%s | '
                       '%s | %s%s' % (
                           x['n'], x['dt_us'], x['t_s'], x['attr'], x['diag'], x['instr_us'], x['kq_n'], x['m5r_us'], x['kstate'],
                           x['E'], x['holder'], x['cls'], ' INSTR_MADE' if x['instr_made'] else (' IN COUNT' if x['in_count'] else ''),
                           ' > '.join(x['path'] or []), x['note'], (' load %s' % x['load_ratio']) if x.get('load_ratio') is not None else ''))
        out.append('  PK-A B5 frames %d, armed member (EMU_RUN:Gpu / EMU_CALL on GuestGpu) %d: %s' % (
            len(r['pk_a']), r['pk_a_armed'], [(x['n'], x['cls']) for x in r['pk_a']][:10]))
        if r['stand'] is not None:
            out.append('  STAND frames after TestB32 fire: %s' % [(x['n'], x['dt_us'], x['cls'], x['holder']) for x in r['stand']])
            sf = max(r['stand'], key=lambda x: x['dt_us']) if r['stand'] else None
            if sf is not None:
                out.append('  STAND FRAME n %s dt_us %s class %s holder %s | path %s | note %s' % (
                    sf['n'], sf['dt_us'], sf['cls'], sf['holder'], ' > '.join(sf['path'] or []), sf['note']))
                out.append('    GuestGpu in the chain %s; a GuestGpu step with Sw or S >= 50 %% %s (executor variant Sw + S: %s); ring_hold_w %s'
                           % (sf.get('gpu_in_chain'), sf.get('gpu_sw_or_s50'), sf.get('gpu_sw_plus_s50'), sf.get('ring_hold_w')))
                for s in sf.get('steps') or []:
                    out.append('    step %s slot %s %s(%s) R %s Sw %s S %s of %s' % (s['how'], s['slot'], s['name'], s['role'], s['R'], s['Sw'],
                                                                      s['S'], s['samples']))
                for w in sf.get('w') or []:
                    out.append('    -w %s' % w)
        if r['load'] is not None:
            L = r['load']
            out.append('  LOAD n %s..%s+3: called %s; stretched %s' % (
                L['n_start'], L['n_end'], L['called'], [(x['n'], x['dt_us'], x['ratio'], x['cls']) for x in L['stretched']]))
            out.append('    load frames %s' % [(x['n'], x['dt_us'], x['ratio']) for x in L['frames']][:40])
        for l in u5_line(r):
            out.append('  ' + l)
        out.append('  debts item 552 (e): slot_full_w != 0 on a NO_SAMPLES frame %d; unprintable thread names %s; rep_drop %d; I5 dt > 1 ms %d'
                   % (r['slot_full_on_nosamples'], r['bad_names'], r['rep_drop'], r['i5_bad']))
        out.append('  ring_hold_w (Z1, reference): sum over the -x lines %s, hold frames with ring_hold_w > 0 %s, -x lines with the field %s'
                   % (r['ring_hold_w_sum'], r['ring_hold_w_frames'], r['ring_hold_w_field']))
        out.append('  -x last %s' % r['x_last'])
    out.append('  REFERENCE: glitches %s, video index %s, outcome %s, hold_exit %s, hold_s %s' % (
        rf['glitches'], rf['video_index'], rf['outcome'], rf['hold_exit'], rf['hold_s']))
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    tags = sorted(t for t in os.listdir(rd) if (TAG_RX.match(t) or t == 'b32_pd_ref') and os.path.exists(os.path.join(rd, t, 'read.json'))) \
        if os.path.isdir(rd) else []
    out = ['| tag | adm | bin / sig | K_I / K | in count | classes (n: class) | INSTR_MADE | kq_n=0 | m5r | prev>=100 | PK-A B5 armed | U5(1) | U5(4) '
           '| load ratio | recov |', '|' + '---|' * 15]
    for t in tags:
        res = json.load(open(os.path.join(rd, t, 'read.json'), encoding='utf-8'))
        r = res['log'] or {}
        cl = ['%d:%s' % (x['n'], x['cls']) for x in r.get('frames', []) if x['in_count']]
        sf = max(r.get('stand') or [], key=lambda x: x['dt_us'], default=None)
        if sf is not None:
            cl.append('STAND %d:%s gpuSwS50=%s' % (sf['n'], sf['cls'], sf.get('gpu_sw_or_s50')))
        lr = [x['ratio'] for x in ((r.get('load') or {}).get('stretched') or [])]
        out.append('| %s | %s | %s / %s | %s / %s | %s | %s | %s/%s | %s/%s | %s | %s | %s/%s | %s | %s | %s | %s |' % (
            t, 'Y' if res['admitted'] else 'N', (res['binary_sha256'] or '-')[:8], (res['ref'].get('signature') or '-')[:8], r.get('K_I'),
            r.get('K'), r.get('in_count'),
            ' '.join(cl) or '-', r.get('instr_made'), r.get('P_I'), r.get('kq0'), r.get('P_I'), r.get('m5r'), r.get('prev_slow_in_count'),
            r.get('pk_a_armed'), len(r.get('pk_a') or []), r.get('u5_med_dt'), 'NZ' if any((r.get('zero_w_sum') or {}).values()) else '0',
            lr or '-', r.get('recovering')))
    return out


def main(argv):
    if '--check-seal' in argv:
        seal = argv[argv.index('--seal') + 1] if '--seal' in argv else SEAL_PATH
        return F.main(['--check-seal', '--seal', seal])
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        p = paths(tag)
    if not TAG_RX.match(tag):
        print('usage: b32_read.py b32_z0b|b32_ppb|b32_pcb|b32_pd[_r1..6] | --dir D --tag T | --table | --check-seal')
        return 2
    if sha_file(F.__file__) != F20E_SHA:
        print('f20e_read.py sha256 %s != %s - refused' % (sha_file(F.__file__), F20E_SHA))
        return 1
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
