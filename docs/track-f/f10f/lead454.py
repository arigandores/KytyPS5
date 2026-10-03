import re, hashlib, json, sys, os
D = 'C:/kyty/f287/f10e/'
FILES = {
    'r0_log': D + 'runs/f10e_r0/log.txt', 'r0_out': D + 'runs/f10e_r0/stdout.txt', 'r0_run': D + 'runs/f10e_r0/run.json',
    'r1_log': D + 'log_f10e_r1.txt', 'r1_out': D + 'stdout_f10e_r1.txt', 'r1_json': D + 'f10e_r1.json',
    'r1_mp4': D + 'rec_f10e_r1.mp4', 'r1_idx': D + 'rec_f10e_r1.mp4.idx',
    'w_log': D + 'log_f10e_w.txt', 'w_out': D + 'stdout_f10e_w.txt', 'w_json': D + 'f10e_w.json',
}
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()
DEATH = [b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost']
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DR = re.compile(rb' draws=(\d+)')
RX_ST = re.compile(rb'FixSvalStat: validated=(\d+) rejected=(\d+)')
RX_FS = re.compile(rb'FixSval: mode=(\d+) ubo_std_layout=(\d+)')
def scan(p, level=b'underwater_aerial_garden'):
    r = dict(svf=0, svf_hash=set(), fs=[], st=[], death={}, ve=0, vw=0, last=0, dual=None, first_guest=None,
             entry=None, first_scene=None, hold_us=0, max_dt=0, k1s=0, change=None, win=0, recov=0, lines=0)
    with open(p, 'rb') as f:
        for i, ln in enumerate(f, 1):
            r['lines'] = i
            if b'SPIR-V validation failed' in ln:
                r['svf'] += 1
                for m in re.finditer(rb'hash=0x([0-9a-fA-F]+)', ln): r['svf_hash'].add(m.group(1).decode())
            if b'FixSval' in ln:
                m = RX_FS.search(ln)
                if m: r['fs'].append((i, int(m.group(1)), int(m.group(2))))
                m = RX_ST.search(ln)
                if m: r['st'].append((i, int(m.group(1)), int(m.group(2))))
            for d in DEATH:
                if d in ln: r['death'][d.decode()] = r['death'].get(d.decode(), 0) + 1
            if b'[Vulkan][E]' in ln: r['ve'] += 1
            if b'[Vulkan][W]' in ln: r['vw'] += 1
            if b'last time reporting it' in ln: r['last'] += 1
            if r['dual'] is None and b'DualSrcBlend: supported=' in ln: r['dual'] = (i, ln.strip()[-60:].decode('latin1'))
            if r['first_guest'] is None and b'GuestOut' in ln: r['first_guest'] = i
            if re.search(rb'Window \d+ minimized', ln): r['win'] += 1
            if b'Recovering Vulkan swapchain' in ln: r['recov'] += 1
            if b'Level has started:' in ln:
                if r['entry'] is None and level in ln: r['entry'] = i
                elif r['entry'] is not None and r['change'] is None and level not in ln: r['change'] = i
            if b'FrameTrace: n=' in ln and r['entry'] is not None and r['change'] is None:
                m = RX_FT.search(ln)
                if not m: continue
                dt = int(m.group(2))
                if r['first_scene'] is None:
                    d = RX_DR.search(m.group(3))
                    if d and int(d.group(1)) >= 100: r['first_scene'] = i
                    continue
                r['hold_us'] += dt; r['max_dt'] = max(r['max_dt'], dt)
                if dt >= 1000000: r['k1s'] += 1
    r['svf_hash'] = sorted(r['svf_hash']); return r
out = {}
for k, p in FILES.items(): out['sha_' + k] = sha(p)
for k in ('r0_log', 'r0_out', 'r1_log', 'r1_out', 'w_log', 'w_out'):
    out[k] = scan(FILES[k])
out['r0_run'] = json.load(open(FILES['r0_run']))
out['r1_idx_lines'] = sum(1 for _ in open(FILES['r1_idx'], 'rb'))
json.dump(out, open(sys.argv[1], 'w'), indent=1, default=str)
print('done')
