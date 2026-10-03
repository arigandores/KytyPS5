import re, sys, hashlib, os
R = 'C:/kyty/f287/fs3/fs3c/'
TAGS = [('fs3_u', R+'runs/fs3_u/log.txt', R+'runs/fs3_u/stdout.txt', '1'),
        ('fs3_u0', R+'runs/fs3_u0/log.txt', R+'runs/fs3_u0/stdout.txt', '0'),
        ('fs3_w', R+'log_fs3_w.txt', R+'stdout_fs3_w.txt', '1'),
        ('fs3_v', R+'log_fs3_v.txt', R+'stdout_fs3_v.txt', '1'),
        ('fs3_hb', R+'log_fs3_hb.txt', R+'stdout_fs3_hb.txt', '1'),
        ('fs3_pu', R+'runs/fs3_pu/log.txt', R+'runs/fs3_pu/stdout.txt', '1')]
RE_B = re.compile(rb'FixB42: mode=([01]) .*extent=(\d+x\d+)')
RE_E = re.compile(rb'FixB42Ext: mode=([01]) extent=(\d+x\d+) hit=(\d+) applied=(\d+) drawn=(\d+) rearm=(\d+) frame=(\d+)')
DEATH = [b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost']
for tag, log, so, mode in TAGS:
    nb = ne = rb_ = re_ = 0; modes = set(); vE = vW = 0; dsb = None; gout = None; gp = 0; death = 0; n = 0
    ext960 = []; maxdt = 0; lvl = []
    h = hashlib.sha256()
    with open(log, 'rb') as f:
        for line in f:
            n += 1; h.update(line)
            if b'FixB42Ext:' in line:
                ne += 1; m = RE_E.search(line)
                if not m: re_ += 1
                else:
                    modes.add(m.group(1))
                    if m.group(2) == b'960x540': ext960.append((n, int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(7))))
            elif b'FixB42:' in line:
                nb += 1; m = RE_B.search(line)
                if not m: rb_ += 1
                else: modes.add(m.group(1))
            if b'[Vulkan][E]' in line: vE += 1
            elif b'[Vulkan][W][2]' in line: vW += 1
            if dsb is None and b'DualSrcBlend: supported=1 enabled=1' in line: dsb = n
            if gout is None and b'GuestOut' in line: gout = n
            if b'GamePatch:' in line: gp += 1
            if b'Level has started:' in line and len(lvl) < 3: lvl.append(line.strip()[-60:].decode('utf-8', 'replace'))
            for d in DEATH:
                if d in line: death += 1
    sd = 0
    with open(so, 'rb') as f:
        for line in f:
            for d in DEATH:
                if d in line: sd += 1
    print(f'{tag}: lines {n} sha {h.hexdigest()[:16]} FixB42 {nb} (ragged {rb_}) FixB42Ext {ne} (ragged {re_}) modes {sorted(x.decode() for x in modes)} expect {mode}'
          f' | VulkanE {vE} VulkanW2 {vW} | DualSrcBlend line {dsb} firstGuestOut {gout} | GamePatch {gp} | death log {death} stdout {sd}')
    print(f'  levels {lvl}')
    print(f'  ext960 rows {len(ext960)} last {ext960[-1] if ext960 else None}')
    print(f'  ext960 all (line,hit,applied,drawn,frame): {ext960}')
