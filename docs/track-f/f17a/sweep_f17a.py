# F17a (HPP-525, ROADMAP s122 item 421(e)): block sweep of the game logs of sessions 143-146 and of the tracks for F6 -
# the validation-layer warning "fragment shader writes to out_mrt_N, no colour attachment N" - and for the log lines of
# the colour-target binding paths.  Form of docs/track-f/f16a/sweep_f16a.py: files are read in 64 MiB blocks, only whole
# lines are processed, the unfinished tail is carried to the next block; '.xz' goes through 'xz -dc'.
# Per log one JSON line in <out.jsonl>:
#   val                 validation was enabled: the head has 'VK_LAYER_KHRONOS_validation available extension:'
#                       (vulkanWindow.cpp:865-874 prints it only when the layer is requested and found)
#   vw / ve             '[Vulkan][W]' / '[Vulkan][E]' lines
#   f6_broad            lines with 'it writes to [Output variable' (the F6 form, any wording)
#   f6{key:n}           parsed F6 lines; key = 'types|command|Location|name|attachment index|N' (N = 1: the text has
#                       '(imageView is VK_NULL_HANDLE)', i.e. the index is below colorAttachmentCount; 0: at or above it).
#                       identity of a log: sum(f6) == f6_broad
#   wo{text:n}          the other '[Vulkan][W]' lines, digit runs replaced by '#', 200 chars, at most 64 distinct texts
#                       (wo_over - lines beyond the cap)
#   sig{sig:n}          bursts: maximal runs of F6 lines with nothing but one 'Spec information' line between them;
#                       sig = 'command:loc[n],loc[n],...' in the order of the log ('n' marks VK_NULL_HANDLE); at most 256
#                       distinct (sig_over).  A burst is one draw only while no other thread printed inside it.
#   last_report         'last time reporting it' lines (the duplicate limit of the layer was reached)
#   cnt{name:n}         lines of the binding paths (see COUNT below)
#   txt{name:[texts]}   distinct line texts of TEXT patterns, at most 32 per name
#   nco{key:n}          'RenderColorTarget: no color output' lines (graphics debug dump only) by
#                       'base0|basenz' + '_' + 'mask0|masknz'
#   mrt{key:n}          'MrtState[i]: slot=' lines (graphics debug dump only) by
#                       'addr0|addrnz' _ 'tm0|tmnz' _ 'om0|omnz' _ 'fmt0|fmtnz'
#   rct_slots{slot:n}   'RenderColorTarget: slot=' decision lines (first 128 of a process)
#   lvl                 distinct 'Level has started: <name>' names, at most 16
#   ver, sha256, size, lines
# Fixture directories are excluded ('/fx/', '/fx_', '/work_', '/mut', '/test_', '/fixt').
# Resumable: paths already in <out.jsonl> are skipped; stops between files after <budget_s> seconds of wall time and
# when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.  Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep_f17a.py <out.jsonl> <budget_s>
import hashlib, json, os, re, subprocess, sys, time

out = sys.argv[1]
budget = float(sys.argv[2])
t0 = time.time()
roots = ['C:/kyty/s143', 'C:/kyty/s144', 'C:/kyty/s145', 'C:/kyty/s146', 'C:/kyty/f287', 'C:/kyty/p283', 'C:/kyty/s288']
if os.environ.get('F17A_ROOTS'):  # the self-check of selfcheck_f17a.py
    roots = os.environ['F17A_ROOTS'].split(';')
fx = re.compile(r'/(fx/|fx_|work_|mut|test_|fixt)')
files = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        dn[:] = [x for x in dn if x not in ('.git', 'build', 'wt', '_ShaderCache', '_Shaders', 'node_modules', '__pycache__')]
        d = dp.replace(os.sep, '/')
        for f in fn:
            ok = (f.startswith('log_') and (f.endswith('.txt') or f.endswith('.txt.xz'))) or (f.startswith('_kyty') and f.endswith('.txt'))
            if not ok:
                continue
            p = d + '/' + f
            if fx.search(p):
                continue
            files.append((p, os.path.getsize(p)))
files.sort()

done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{'):
            done.add(json.loads(l)['path'])
left = [(p, s) for p, s in files if p not in done]
print('files', len(files), 'done before', len(done), 'left', len(left), 'left GiB %.1f' % (sum(s for _, s in left) / 2.0 ** 30))

NL = b'\n'
BLOCK = 64 << 20
VAL = b'VK_LAYER_KHRONOS_validation available extension:'


def head_val(p):
    # validation marker in the first 256 KiB (plain logs only; '.xz' is swept in the second group)
    if p.endswith('.xz'):
        return False
    with open(p, 'rb') as fh:
        return VAL in fh.read(256 << 10)


# logs with validation first: the reading of item 421(e) needs them; the others give only debug-dump witness lines
left.sort(key=lambda x: (not head_val(x[0]), x[0]))
print('left with validation (head)', sum(1 for p, _ in left if head_val(p)))
VW = b'[Vulkan][W]'
VE = b'[Vulkan][E]'
BROAD = b'it writes to [Output variable'
SPEC = b'Spec information at'
VWLINE = re.compile(rb'\[Vulkan\]\[W\]\[(\d+)\]: ([^\r\n]*)')
F6 = re.compile(rb'(vk\w+)\(\): Inside \[VK_SHADER_STAGE_FRAGMENT_BIT\] it writes to \[Output variable, Location (\d+), "([^"]*)"\] '
                rb'but there is no VkRenderingInfo::pColorAttachments\[(\d+)\]( \(imageView is VK_NULL_HANDLE\))? and this write is unused')
NCO = re.compile(rb'RenderColorTarget: no color output slot=(\d+) base=0x([0-9a-f]+) slot_mask=0x([0-9a-f]+)')
MRT = re.compile(rb'MrtState\[\d+\]: slot=(\d+) addr=0x([0-9a-f]+) target_mask=0x([0-9a-f]+) shader_mask=0x([0-9a-f]+) out_mode=(\d+) fmt=0x([0-9a-f]+)')
RCT = re.compile(rb'RenderColorTarget: slot=(\d+) addr=')
LVL = re.compile(rb'Level has started: ([^\r\n]+)')
VER = re.compile(rb'(?m)^\s*version:\s*([^\r\n]+)')
DIG = re.compile(rb'\d+')
COUNT = {
    'last_report': b'last time reporting it',
    'fb_skip': b'DrawFramebufferSkip[',
    'mrt_state': b'MrtState[',
    'nco': b'RenderColorTarget: no color output',
    'rct_decision': b'RenderColorTarget: slot=',
    'rts_mismatch': b'RtSkipVerify: MISMATCH',
    'guest_out': b'GuestOut',
}
TEXT = {
    'exit_rt_hyphen': b'render-target',          # every EXIT text of colorRenderTarget.cpp:201-402 and textureCommon.cpp:137
    'exit_rt_space': b'render target',           # '1D render target has ...', 'non-3D render target has ...', 'multisampled ...'
    'exit_tile': b'unknown tile mode',
    'exit_mixed': b'mixed color attachment sample counts',
    'exit_changed': b'target changed after render-state discovery',
    'rts_mode': b'RtSkip: mode',
    'rts_refused': b'RtSkip: refused',
    'cb_shader_mask': b'CB_SHADER_MASK',
    'dualsrc': b'DualSrcBlend:',
}
TXT_CAP = 32
WO_CAP = 64
SIG_CAP = 256


def line_at(buf, i):
    a = buf.rfind(NL, 0, i) + 1
    b = buf.find(NL, i)
    if b == -1:
        b = len(buf)
    return buf[a:b].rstrip(b'\r')


def dec(b):
    return b.decode('utf-8', 'replace')


def sweep(path, size):
    rec = {'path': path, 'size': size, 'val': False, 'vw': 0, 've': 0, 'f6_broad': 0, 'f6': {}, 'wo': {}, 'wo_over': 0,
           'sig': {}, 'sig_over': 0, 'cnt': {k: 0 for k in COUNT}, 'txt': {k: [] for k in TEXT}, 'nco': {}, 'mrt': {},
           'rct_slots': {}, 'lvl': [], 'ver': None, 'lines': 0}
    h = hashlib.sha256()
    proc = None
    if path.endswith('.xz'):
        with open(path, 'rb') as fh:
            while True:
                b = fh.read(BLOCK)
                if not b:
                    break
                h.update(b)
        proc = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE)
        f = proc.stdout
    else:
        f = open(path, 'rb')
    carry = b''
    first = True
    burst = []          # the F6 lines of the open burst: (command, loc, null)
    gap_prefix = None   # bytes after the last F6 line of the previous block (None: no open burst)

    def close_burst():
        if not burst:
            return
        s = dec(burst[0][0]) + ':' + ','.join(str(l) + ('n' if n else '') for _, l, n in burst)
        if s in rec['sig'] or len(rec['sig']) < SIG_CAP:
            rec['sig'][s] = rec['sig'].get(s, 0) + 1
        else:
            rec['sig_over'] += 1
        del burst[:]

    while True:
        b = f.read(BLOCK)
        if not b and not carry:
            break
        if proc is None:
            h.update(b)
        buf = carry + b
        if b:
            cut = buf.rfind(NL)
            if cut == -1:
                carry = buf
                continue
            carry = buf[cut + 1:]
            buf = buf[:cut + 1]
        else:
            carry = b''
        rec['lines'] += buf.count(NL)
        if first:
            first = False
            rec['val'] = VAL in buf[:4 << 20]
            m = VER.search(buf[:1 << 20])
            if m:
                rec['ver'] = dec(m.group(1))[:80]
        rec['vw'] += buf.count(VW)
        rec['ve'] += buf.count(VE)
        rec['f6_broad'] += buf.count(BROAD)
        for k, pat in COUNT.items():
            rec['cnt'][k] += buf.count(pat)
        for k, pat in TEXT.items():
            i = buf.find(pat)
            n = 0
            while i != -1 and n < 4096:
                t = dec(DIG.sub(b'#', line_at(buf, i)))[:240]
                if t not in rec['txt'][k] and len(rec['txt'][k]) < TXT_CAP:
                    rec['txt'][k].append(t)
                n += 1
                i = buf.find(pat, buf.find(NL, i) if buf.find(NL, i) != -1 else len(buf))
        if rec['cnt']['nco']:
            for m in NCO.finditer(buf):
                k = ('base0' if int(m.group(2), 16) == 0 else 'basenz') + '_' + ('mask0' if int(m.group(3), 16) == 0 else 'masknz')
                rec['nco'][k] = rec['nco'].get(k, 0) + 1
        if rec['cnt']['mrt_state']:
            for m in MRT.finditer(buf):
                k = '_'.join((('addr0' if int(m.group(2), 16) == 0 else 'addrnz'), ('tm0' if int(m.group(3), 16) == 0 else 'tmnz'),
                              ('om0' if int(m.group(5)) == 0 else 'omnz'), ('fmt0' if int(m.group(6), 16) == 0 else 'fmtnz')))
                rec['mrt'][k] = rec['mrt'].get(k, 0) + 1
        if RCT.search(buf):
            for m in RCT.finditer(buf):
                k = dec(m.group(1))
                rec['rct_slots'][k] = rec['rct_slots'].get(k, 0) + 1
        if len(rec['lvl']) < 16:
            for m in LVL.finditer(buf):
                t = dec(m.group(1)).strip()[:60]
                if t not in rec['lvl'] and len(rec['lvl']) < 16:
                    rec['lvl'].append(t)
        last_end = None
        if VW in buf:
            for m in VWLINE.finditer(buf):
                body = m.group(2)
                g = F6.match(body)
                if g is None:
                    if gap_prefix is not None or burst:
                        close_burst()
                        gap_prefix = None
                    last_end = None
                    t = dec(DIG.sub(b'#', body))[:200]
                    if t in rec['wo'] or len(rec['wo']) < WO_CAP:
                        rec['wo'][t] = rec['wo'].get(t, 0) + 1
                    else:
                        rec['wo_over'] += 1
                    continue
                null = 1 if g.group(5) else 0
                key = '|'.join((dec(m.group(1)), dec(g.group(1)), dec(g.group(2)), dec(g.group(3)), dec(g.group(4)), str(null)))
                rec['f6'][key] = rec['f6'].get(key, 0) + 1
                if burst:
                    gap = (gap_prefix if last_end is None else b'') + buf[(0 if last_end is None else last_end):m.start()]
                    lines = [x for x in gap.split(NL) if x.strip()]
                    if not (len(lines) == 0 or (len(lines) == 1 and lines[0].startswith(SPEC))):
                        close_burst()
                burst.append((g.group(1), int(g.group(2)), null))
                last_end = m.end()
                gap_prefix = b''
        if burst:
            if last_end is not None:
                gap_prefix = buf[last_end:]
            else:
                gap_prefix = (gap_prefix or b'') + buf
            if len(gap_prefix) > 4096:
                close_burst()
                gap_prefix = None
        if not b:
            break
    close_burst()
    if proc is None:
        f.close()
    else:
        proc.wait()
    rec['sha256'] = h.hexdigest()
    rec['f6_sum'] = sum(rec['f6'].values())
    return rec


n = 0
for p, s in left:
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('STOPPED: lock or STOP present')
        sys.exit(3)
    if time.time() - t0 > budget:
        break
    rec = sweep(p, s)
    with open(out, 'ab') as fo:
        fo.write((json.dumps(rec, ensure_ascii=True, sort_keys=True) + '\n').encode('ascii'))
    n += 1
print('swept now', n, 'wall %.1f s' % (time.time() - t0))
if n == len(left):
    print('SWEEP COMPLETE')
