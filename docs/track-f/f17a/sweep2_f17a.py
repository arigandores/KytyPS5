# F17a (HPP-525): second pass over the logs of sweep.jsonl that have F6 lines - the F6 lines of one draw.
# The layer reports the unconsumed outputs of a draw in ascending Location order and prints nothing between two draws, so
# a burst of sweep_f17a.py glues several draws together.  Here a DRAW RUN is a maximal run of F6 lines of one command with
# strictly ascending Location and nothing but one 'Spec information' line between neighbours [I: a line of another thread
# inside a draw splits its run in two; two draws whose Locations happen to ascend across the border merge].
# Per log one JSON line in <out.jsonl>:
#   run{key:n}     key = 'command:loc[n],loc[n],...' ('n' - the text has '(imageView is VK_NULL_HANDLE)'); at most 512
#                  distinct keys (run_over - runs beyond the cap)
#   runs, f6       runs and F6 lines; identity with sweep.jsonl: f6 == f6_sum of the same path
#   first{key:line}  the 1-based line number of the first F6 line of the first run with this key
# Resumable, budgeted and stopped like sweep_f17a.py.  Usage: python sweep2_f17a.py <sweep.jsonl> <out.jsonl> <budget_s>
import json, os, re, subprocess, sys, time

src, out = sys.argv[1], sys.argv[2]
budget = float(sys.argv[3])
t0 = time.time()
todo = []
seen = set()
for l in sorted(open(src, encoding='utf-8')):
    if l.startswith('{'):
        r = json.loads(l)
        if r['f6_sum'] > 0 and r['sha256'] not in seen:  # one path per sha256: copies of a log are read once
            seen.add(r['sha256'])
            todo.append((r['path'], r['f6_sum']))
todo.sort()
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{'):
            done.add(json.loads(l)['path'])
left = [x for x in todo if x[0] not in done]
print('logs with F6', len(todo), 'done before', len(done), 'left', len(left))

NL = b'\n'
BLOCK = 64 << 20
VW = b'[Vulkan][W]'
SPEC = b'Spec information at'
F6 = re.compile(rb'\[Vulkan\]\[W\]\[\d+\]: (vk\w+)\(\): Inside \[VK_SHADER_STAGE_FRAGMENT_BIT\] it writes to \[Output variable, Location (\d+), "[^"]*"\] '
                rb'but there is no VkRenderingInfo::pColorAttachments\[\d+\]( \(imageView is VK_NULL_HANDLE\))? and this write is unused[^\r\n]*')
RUN_CAP = 512


def sweep(path):
    rec = {'path': path, 'run': {}, 'run_over': 0, 'runs': 0, 'f6': 0, 'first': {}}
    proc = None
    if path.endswith('.xz'):
        proc = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE)
        f = proc.stdout
    else:
        f = open(path, 'rb')
    carry = b''
    run = []            # (command, loc, null) of the open run
    run_line = [0]
    gap_prefix = None
    lines_before = 0

    def close_run():
        if not run:
            return
        k = run[0][0].decode() + ':' + ','.join(str(l) + ('n' if n else '') for _, l, n in run)
        rec['runs'] += 1
        if k in rec['run'] or len(rec['run']) < RUN_CAP:
            rec['run'][k] = rec['run'].get(k, 0) + 1
            if k not in rec['first']:
                rec['first'][k] = run_line[0]
        else:
            rec['run_over'] += 1
        del run[:]

    while True:
        b = f.read(BLOCK)
        if not b and not carry:
            break
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
        last_end = None
        pos_line = 0        # lines counted up to cnt_pos
        cnt_pos = 0
        if VW in buf:
            for m in F6.finditer(buf):
                rec['f6'] += 1
                cmd, loc, null = m.group(1), int(m.group(2)), 1 if m.group(3) else 0
                if run:
                    gap = (gap_prefix if last_end is None else b'') + buf[(0 if last_end is None else last_end):m.start()]
                    ls = [x for x in gap.split(NL) if x.strip()]
                    joined = len(ls) == 0 or (len(ls) == 1 and ls[0].startswith(SPEC))
                    if not (joined and cmd == run[-1][0] and loc > run[-1][1]):
                        close_run()
                if not run:
                    pos_line += buf.count(NL, cnt_pos, m.start())
                    cnt_pos = m.start()
                    run_line[0] = lines_before + pos_line + 1
                run.append((cmd, loc, null))
                last_end = m.end()
                gap_prefix = b''
        if run:
            if last_end is not None:
                gap_prefix = buf[last_end:]
            else:
                gap_prefix = (gap_prefix or b'') + buf
            if len(gap_prefix) > 4096:
                close_run()
                gap_prefix = None
        lines_before += buf.count(NL)
        if not b:
            break
    close_run()
    if proc is None:
        f.close()
    else:
        proc.wait()
    return rec


n = 0
for p, f6 in left:
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('STOPPED: lock or STOP present')
        sys.exit(3)
    if time.time() - t0 > budget:
        break
    rec = sweep(p)
    rec['f6_sweep1'] = f6
    with open(out, 'ab') as fo:
        fo.write((json.dumps(rec, ensure_ascii=True, sort_keys=True) + '\n').encode('ascii'))
    n += 1
print('swept now', n, 'wall %.1f s' % (time.time() - t0))
if n == len(left):
    print('SWEEP2 COMPLETE')
