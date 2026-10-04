# F20a (HPP-551, ROADMAP s122 item 451(e)): block sweep of the game logs for B2 / B32 - the scenes, the frames with
# dt_us >= 100 ms after the first scene frame and what is logged inside the interval of each such frame.
# Form of docs/track-f/f19a/sweep_f19a.py: 64 MiB blocks, only whole lines, the unfinished tail is carried; '.xz' goes
# through 'xz -dc'.  One JSON line per log in <out.jsonl>.
#   mode 'hash'  : sha256 (stored file), sha256_text ('.xz': unpacked text), size - nothing else.
#   mode 'sweep' : also
#     lines, ft_n / ft_us (count and sum of dt_us of the 'FrameTrace: n=' lines), n_first / n_last
#     head[]   text[:200] of the config lines of the header (before the first 'FrameTrace: n=' line of the first block,
#              at most the first 8 MiB): line starts HEADRE, at most 80
#     cnt{}    whole-log counts of line starts: vk ('[Vulkan]['), trip ('BvhLoopCapTrip:'), prio ('PriorityStall:'),
#              mtl ('MainTaskLate:'), gatearm ('GateArm:'), quit ('Event: quit'), and of the substrings pcs
#              ('Vulkan pipeline cache: saved'), fatal ('--- Fatal Error ---'), lvl_empty (level start with no name)
#     scenes[] one per non-empty 'Level has started: <name>' (at most 64, scenes_over): level, line, ft_before (frames
#              before the line), first_n / first_line (the first scene frame: the first 'FrameTrace: n=' with draws >= 100
#              after the level line, items 218(g) / 221(v); its own dt is not counted), frames / sum_us / last_n (frames
#              AFTER the first scene frame up to the next level line or 'Event: quit'), hold_first_n (the first frame that
#              STARTS at or after WIN_US = 10 s of scene time), frames_h / sum_h (hold part), k100_w / k100_h (frames with
#              dt >= 100 ms that start inside / after the window; frames >= 1 s included), k1s_w / k1s_h, max_w / max_h,
#              after_quit (frames after 'Event: quit', not counted anywhere else)
#     slow[]   every frame with dt >= 100 ms after the first scene frame of a scene (also after quit, flagged), at most
#              CAP (slow_over): line, n, dt_us, draws, scene (index), idx (1-based frame index after the first scene
#              frame), t_before_us (scene time before the frame), q (1 = after 'Event: quit'), and the interval - the
#              lines between the previous 'FrameTrace: n=' line and this one:
#                il (lines), io (blank / file-io lines), fta (other 'FrameTrace' lines), pcs / pcs_us (lines with
#                'Vulkan pipeline cache: saved' and the largest '(<n> us'), trip ('BvhLoopCapTrip:' line starts), prio /
#                prio_us ('PriorityStall:' line starts, largest ' us='), ir (lines that start with '%' - the IR dump of
#                a translation), gcn (lines '<n>: X_...' - the GCN listing of a translation), skip ('AsyncPipelines:
#                skipped draw'), cs ('CsStall:'), mtl / mtl_us ('MainTaskLate:'), win (line starts 'Window ', 'Event: ',
#                'Recovering Vulkan swapchain', 'Pause'), cut (1 = the interval start was lost: more than TAILCAP bytes
#                without a frame line), top (the 10 most frequent normalised signatures of the other lines, [text, n])
# Identities (selfcheck_f20a.py): per scene frames == frames_w + frames_h and k100 == number of its slow rows with q == 0
# when slow_over == 0; sum over scenes of frames + first-scene frames + frames outside <= ft_n; slow dt_us >= 100 000.
# Resumable: paths already in <out.jsonl> are skipped; stops between files after <budget_s> seconds of wall time and
# when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.  Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep_f20a.py <list.tsv> <out.jsonl> <budget_s>      (list.tsv: path <TAB> size <TAB> mode)
import collections, hashlib, json, os, re, subprocess, sys, time

lst, out, budget = sys.argv[1], sys.argv[2], float(sys.argv[3])
LOCK = os.environ.get('F20A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F20A_STOP', 'C:/kyty/f287/STOP')
t0 = time.time()
files = []
for l in open(lst, encoding='utf-8'):
    l = l.rstrip('\n')
    if l:
        p, s, mode = l.split('\t')[:3]
        files.append((p, int(s), mode))
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{') and l.rstrip().endswith('}'):
            done.add(json.loads(l)['path'])
left = [x for x in files if x[0] not in done]
print('files', len(files), 'done before', len(done), 'left', len(left), 'left GiB %.2f' % (sum(x[1] for x in left) / 2.0 ** 30))

NL = b'\n'
BLOCK = 64 << 20
TAILCAP = 96 << 20
HEADCAP = 8 << 20
WIN_US = 10000000
SLOW_US = 100000
CAP = 400
FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
DRAWS = re.compile(rb' draws=(\d+)')
FTLIT = b'FrameTrace: n='
LVL = b'Level has started:'
HEADRE = re.compile(rb'^(?:Gate|Knob|GamePatch|S-pcw|Shader translation cache|DualSrcBlend|BvhLoopCap:|Test[A-Za-z]+:|'
                    rb'MainStallTest|PrepareHold|Fix[A-Za-z0-9]+:|PVar|Pvar|Poke|RenderDoc|AsyncPipelines: mode|'
                    rb'ShaderSeed: compat|Diag[A-Za-z0-9]+:|AudioSync|FrameTrace: mode|RtSkip|ShaderPreparation: startup)[^\n]*',
                    re.M)
NUM = re.compile(rb'0x[0-9a-fA-F]+|\b[0-9a-f]{16}\b|\d+')
USER = re.compile(rb'([Uu]sers[\\/]+)[^\\/ \t]+')
US_PAR = re.compile(rb'\((\d+) us')
US_EQ = re.compile(rb' us=(\d+)')
GCN = re.compile(rb'[0-9a-fA-F]+: [A-Z]_')
IO = (b'Read ', b'Open:', b'Close:', b'KernelFstat', b'KernelStat', b'path = ')
WINP = (b'Window ', b'Event: ', b'Recovering Vulkan swapchain', b'Pause')
COUNTS = (('vk', b'\n[Vulkan]['), ('trip', b'\nBvhLoopCapTrip:'), ('prio', b'\nPriorityStall:'), ('mtl', b'\nMainTaskLate:'),
          ('gatearm', b'\nGateArm:'), ('quit', b'\nEvent: quit'), ('pcs', b'Vulkan pipeline cache: saved'),
          ('fatal', b'--- Fatal Error ---'))


def dec(b):
    return USER.sub(rb'\1<user>', b).decode('utf-8', 'replace')


def interval(data, cut):
    r = {'il': 0, 'io': 0, 'fta': 0, 'pcs': 0, 'pcs_us': 0, 'trip': 0, 'prio': 0, 'prio_us': 0, 'ir': 0, 'gcn': 0, 'skip': 0,
         'cs': 0, 'mtl': 0, 'mtl_us': 0, 'win': 0, 'cut': 1 if cut else 0}
    c = collections.Counter()
    for l in data.split(NL):
        t = l.strip()
        r['il'] += 1
        if not t or l[:1] == b'\t' or t.startswith(IO):
            r['io'] += 1
            continue
        if t.startswith(b'FrameTrace'):
            r['fta'] += 1
            continue
        if t[:1] == b'%':
            r['ir'] += 1
            continue
        if GCN.match(t):
            r['gcn'] += 1
            continue
        if b'Vulkan pipeline cache: saved' in t:
            r['pcs'] += 1
            m = US_PAR.search(t)
            if m:
                r['pcs_us'] = max(r['pcs_us'], int(m.group(1)))
        elif t.startswith(b'BvhLoopCapTrip:'):
            r['trip'] += 1
        elif t.startswith(b'PriorityStall:'):
            r['prio'] += 1
            m = US_EQ.search(t)
            if m:
                r['prio_us'] = max(r['prio_us'], int(m.group(1)))
        elif t.startswith(b'AsyncPipelines: skipped draw'):
            r['skip'] += 1
        elif t.startswith(b'CsStall:'):
            r['cs'] += 1
        elif t.startswith(b'MainTaskLate:'):
            r['mtl'] += 1
            m = US_EQ.search(t)
            if m:
                r['mtl_us'] = max(r['mtl_us'], int(m.group(1)))
        elif t.startswith(WINP):
            r['win'] += 1
        c[NUM.sub(b'X', t)[:70]] += 1
    if data.endswith(NL) or not data:
        r['il'] -= 1
        r['io'] -= 1
    r['top'] = [[dec(k), v] for k, v in c.most_common(10)]
    return r


def new_scene(name, line, ft_before):
    return {'level': name, 'line': line, 'ft_before': ft_before, 'first_n': None, 'first_line': None, 'frames': 0, 'sum_us': 0,
            'last_n': None, 'hold_first_n': None, 'frames_h': 0, 'sum_h': 0, 'k100_w': 0, 'k100_h': 0, 'k1s_w': 0, 'k1s_h': 0,
            'max_w': 0, 'max_h': 0, 'after_quit': 0}


def sweep(path, size, mode):
    rec = {'path': path, 'size': size, 'xz': path.endswith('.xz'), 'mode': mode}
    full = mode == 'sweep'
    if full:
        rec.update({'lines': 0, 'ft_n': 0, 'ft_us': 0, 'n_first': None, 'n_last': None, 'head': [], 'cnt': {k: 0 for k, _ in COUNTS},
                    'scenes': [], 'scenes_over': 0, 'slow': [], 'slow_over': 0, 'slow_n': 0})
        rec['cnt']['lvl_empty'] = 0
    h = hashlib.sha256()
    h2 = hashlib.sha256()
    proc = None
    if rec['xz']:
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
    tail = b''
    tail_cut = False
    cur = None
    quit_seen = False
    first_block = True
    while True:
        b = f.read(BLOCK)
        if not b and not carry:
            break
        if proc is None:
            h.update(b)
        else:
            h2.update(b)
        if not full:
            if not b:
                break
            continue
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
            if not buf.endswith(NL):
                buf += NL
        base_line = rec['lines']
        ev = []
        i = buf.find(FTLIT)
        first_ft = i
        while i != -1:
            if i == 0 or buf[i - 1:i] == NL:
                m = FT.match(buf, i)
                if m:
                    le = buf.find(NL, i)
                    d = DRAWS.search(buf, m.end(), le)
                    ev.append((i, 0, le + 1, int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else -1))
            i = buf.find(FTLIT, i + 1)
        i = buf.find(LVL)
        while i != -1:
            ls = buf.rfind(NL, 0, i) + 1
            le = buf.find(NL, i)
            ev.append((ls, 1, buf[i + len(LVL):le].strip()))
            i = buf.find(LVL, le)
        i = buf.find(b'\nEvent: quit')
        while i != -1:
            ev.append((i + 1, 2))
            i = buf.find(b'\nEvent: quit', i + 1)
        if buf.startswith(b'Event: quit'):
            ev.append((0, 2))
        ev.sort()
        if first_block:
            first_block = False
            hend = len(buf) if first_ft == -1 else first_ft
            for m in HEADRE.finditer(buf, 0, min(hend, HEADCAP)):
                if len(rec['head']) < 80:
                    rec['head'].append(dec(m.group(0).strip())[:200])
        for k, lit in COUNTS:
            rec['cnt'][k] += buf.count(lit)
            if lit[:1] == NL and buf.startswith(lit[1:]):
                rec['cnt'][k] += 1
        lc_pos, lc_n = 0, 0
        prev_end = -1
        for e in ev:
            pos = e[0]
            if e[1] == 2:
                quit_seen = True
                continue
            if e[1] == 1:
                lc_n += buf.count(NL, lc_pos, pos)
                lc_pos = pos
                name = dec(e[2])[:80]
                if not name:
                    rec['cnt']['lvl_empty'] += 1
                    continue
                cur = new_scene(name, base_line + lc_n + 1, rec['ft_n'])
                quit_seen = False
                if len(rec['scenes']) < 64:
                    rec['scenes'].append(cur)
                else:
                    rec['scenes_over'] += 1
                continue
            _, _, end, n, dt, draws = e
            rec['ft_n'] += 1
            rec['ft_us'] += dt
            if rec['n_first'] is None:
                rec['n_first'] = n
            rec['n_last'] = n
            sc = cur
            if sc is not None:
                if sc['first_n'] is None:
                    if draws >= 100:
                        lc_n += buf.count(NL, lc_pos, pos)
                        lc_pos = pos
                        sc['first_n'] = n
                        sc['first_line'] = base_line + lc_n + 1
                else:
                    tb = sc['sum_us']
                    slow = dt >= SLOW_US
                    if quit_seen:
                        sc['after_quit'] += 1
                    else:
                        hold = tb >= WIN_US
                        sc['frames'] += 1
                        sc['sum_us'] += dt
                        sc['last_n'] = n
                        if hold:
                            if sc['hold_first_n'] is None:
                                sc['hold_first_n'] = n
                            sc['frames_h'] += 1
                            sc['sum_h'] += dt
                        key = 'h' if hold else 'w'
                        if dt > sc['max_' + key]:
                            sc['max_' + key] = dt
                        if slow:
                            sc['k100_' + key] += 1
                            if dt >= 1000000:
                                sc['k1s_' + key] += 1
                    if slow:
                        rec['slow_n'] += 1
                        if len(rec['slow']) < CAP:
                            lc_n += buf.count(NL, lc_pos, pos)
                            lc_pos = pos
                            if prev_end == -1:
                                data = tail + buf[:pos]
                                cutf = tail_cut
                            else:
                                data = buf[prev_end:pos]
                                cutf = False
                            row = {'line': base_line + lc_n + 1, 'n': n, 'dt_us': dt, 'draws': draws,
                                   'scene': len(rec['scenes']) - 1 if rec['scenes'] and rec['scenes'][-1] is sc else -1,
                                   'idx': sc['frames'] + sc['after_quit'], 't_before_us': tb, 'q': 1 if quit_seen else 0}
                            row.update(interval(data, cutf))
                            rec['slow'].append(row)
                        else:
                            rec['slow_over'] += 1
            prev_end = end
        if prev_end == -1:
            tail = tail + buf
            if len(tail) > TAILCAP:
                tail = tail[-TAILCAP:]
                tail_cut = True
        else:
            tail = buf[prev_end:]
            tail_cut = False
        rec['lines'] += buf.count(NL)
        if not b:
            break
    if proc is None:
        f.close()
    else:
        proc.wait()
        rec['xz_rc'] = proc.returncode
        rec['sha256_text'] = h2.hexdigest()
    rec['sha256'] = h.hexdigest()
    return rec


n = 0
for p, s, mode in left:
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('STOPPED: lock or STOP present')
        sys.exit(3)
    if time.time() - t0 > budget:
        break
    if not os.path.exists(p):
        rec = {'path': p, 'size': s, 'mode': mode, 'missing': True}
    else:
        rec = sweep(p, s, mode)
    with open(out, 'ab') as fo:
        fo.write((json.dumps(rec, ensure_ascii=True, sort_keys=True) + '\n').encode('ascii'))
    n += 1
print('swept now', n, 'wall %.1f s' % (time.time() - t0))
if n == len(left):
    print('SWEEP COMPLETE')
