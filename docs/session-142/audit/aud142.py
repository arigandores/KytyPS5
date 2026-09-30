# aud142.py - Session Auditor, s142 step 3 (HPP-280). Own recount of the sc142 outputs.
# Independent of sc142.py: no import, no shared code. Rules by the letter of pred/02_sc142.md s.2-3 and ROADMAP p.221(v)-(g), 223(a), 224(a).
# Usage: python aud142.py <out.json> <label> <level> <log> [<emu stdout>] [<enter_scene stdout>]
import sys, re, json, hashlib, statistics

FT = b'FrameTrace: n='
LVL = b'GuestOut: Level has started: '
K2M = (b'GpuHangAbort:', b'ErrorDeviceLost')
K1M = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---')
TS = re.compile(rb'\]\[(\d\d:\d\d:\d\d\.\d{3})\]')
RN = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
RD = re.compile(rb' draws=(\d+)')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


def scan(log, level):
    lv = level.encode()
    rows = []          # (lineno, n, dt, draws, last_ts)
    entry = None       # lineno of the entry line
    starts = []        # (lineno, name, rows_before)
    marks = []         # (lineno, marker)
    vk = {'E': 0, 'any': 0, 'nolayer': 0, 'valfeat': 0}
    skipped_lines = 0; skipped_frames = set(); skipped_ids = set(); torn = 0; opc = 0; stub = 0; bvh = 0
    last_ts = None
    with open(log, 'rb') as f:
        for i, l in enumerate(f):
            m = TS.search(l)
            if m:
                last_ts = m.group(1).decode()
            if FT in l:
                if not l.startswith(FT):
                    torn += 1
                r = RN.search(l)
                if r:
                    d = RD.search(l)
                    rows.append((i, int(r.group(1)), int(r.group(2)), int(d.group(1)) if d else None, last_ts))
                continue
            if LVL in l:
                name = l.split(LVL, 1)[1].strip().decode('ascii', 'replace')
                if entry is None and name == level:
                    entry = i
                starts.append((i, name, len(rows)))
            for k in K2M + K1M:
                if k in l:
                    marks.append((i, k.decode()))
            if b'[Vulkan][' in l:
                vk['any'] += 1
                if b'[Vulkan][E]' in l:
                    vk['E'] += 1
            if b'no validation layer:' in l:
                vk['nolayer'] += 1
            if b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features' in l:
                vk['valfeat'] += 1
            if b'AsyncPipelines: skipped draw' in l:
                skipped_lines += 1; skipped_frames.add(len(rows))
                q = re.search(rb' frame=(\d+)', l)
                if q:
                    skipped_ids.add(int(q.group(1)))
            if b'opcode is not implemented' in l:
                opc += 1
            if b'=== Stubbed function' in l:
                stub += 1
            if b'BvhLoopCapTrip:' in l:
                bvh += 1
    return dict(rows=rows, entry=entry, starts=starts, marks=marks, vk=vk, skipped_lines=skipped_lines,
                skipped_frames=len(skipped_frames), skipped_ids=len(skipped_ids), torn=torn, opc=opc, stub=stub, bvh=bvh)


def scan_text(p):
    out = {'marks': [], 'vkE': 0, 'vkany': 0, 'nolayer': 0, 'valfeat': 0, 'ended': 0}
    if not p:
        return None
    try:
        data = open(p, 'rb').read()
    except OSError:
        return None
    for i, l in enumerate(data.split(b'\n')):
        for k in K2M + K1M:
            if k in l:
                out['marks'].append((i, k.decode()))
        if b'[Vulkan][' in l:
            out['vkany'] += 1
            if b'[Vulkan][E]' in l:
                out['vkE'] += 1
        if b'no validation layer:' in l:
            out['nolayer'] += 1
        if b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features' in l:
            out['valfeat'] += 1
        if b'the game ENDED inside the hold' in l:
            out['ended'] += 1
    return out


def main():
    outp, label, level, log = sys.argv[1:5]
    emu = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '-' else None
    ens = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '-' else None
    s = scan(log, level)
    rows = s['rows']
    R = {'label': label, 'level': level, 'log': log, 'log_sha256': sha(log), 'rows_all': len(rows), 'torn': s['torn']}
    R['entry_line'] = s['entry']
    # scene change: any Level-has-started line after the entry line
    ch = [x for x in s['starts'] if s['entry'] is not None and x[0] > s['entry']]
    R['scene_changes'] = [(x[1], x[2]) for x in ch]
    cut = ch[0][0] if ch else None
    R['marks_log'] = s['marks'][:20]
    R['n_marks_log'] = len(s['marks'])
    R['vk_log'] = s['vk']
    R['skipped_lines'] = s['skipped_lines']; R['skipped_frames'] = s['skipped_frames']; R['skipped_ids'] = s['skipped_ids']
    R['opc'] = s['opc']; R['stub'] = s['stub']; R['bvh'] = s['bvh']
    R['emu_stdout'] = scan_text(emu)
    R['es_stdout'] = scan_text(ens)
    if s['entry'] is not None:
        after = [r for r in rows if r[0] > s['entry'] and (cut is None or r[0] < cut)]
        R['sum_dt_after_entry_us'] = sum(r[2] for r in after)
        fi = next((k for k, r in enumerate(after) if r[3] is not None and r[3] >= 100), None)
        if fi is not None:
            f0 = after[fi]
            R['first_scene'] = {'n': f0[1], 'dt_us': f0[2], 'draws': f0[3], 'ts': f0[4]}
            post = after[fi + 1:]
            win, hold = post[:599], post[599:]
            R['win_len'] = len(win); R['hold_len'] = len(hold)
            R['frames_after_first'] = len(post)
            R['sum_dt_after_first_us'] = sum(r[2] for r in post)
            dts = [r[2] for r in post]
            R['median_dt'] = statistics.median(dts) if dts else None
            R['max_dt'] = max(dts) if dts else None
            R['K2'] = [(r[1], r[2], 'window' if k < 599 else 'hold') for k, r in enumerate(post) if r[2] >= 1000000]
            R['K3_win'] = [(r[1], r[2], r[4]) for r in win if 100000 <= r[2] < 1000000]
            R['K3_hold'] = [(r[1], r[2], r[4]) for r in hold if 100000 <= r[2] < 1000000]
            ns = [r[1] for r in post]
            R['n_gaps'] = sum(1 for a, b in zip([f0[1]] + ns, ns) if b != a + 1)
            R['win_last_ts'] = win[-1][4] if win else None
        else:
            R['first_scene'] = None
    print(json.dumps(R, ensure_ascii=True))
    json.dump(R, open(outp, 'w'), ensure_ascii=True, indent=1)


if __name__ == '__main__':
    main()
