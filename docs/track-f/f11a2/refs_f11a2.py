# F11a2 (HPP-460): check of <commit>:<path>:<line> refs of docs/track-f/f11a2.md - anchor at the line and +1 at the next line.
import subprocess
import sys

REFS = [
    ('571bb3a7', 'docs/ROADMAP.md', 20233, '(б) **Звено F11a2** (Emu Engineer, `blocked` на `HPP-449` и `HPP-441`; стадия review лида)',
     'EID 3399–3455 снимка `C:/kyty/f287/f7a/enemy_final_600.rdc` (`181cb236…`) и есть ли в их коде `IMAGE_BVH_INTERSECT_RAY` [c]'),
    ('571bb3a7', 'docs/ROADMAP.md', 20147, '**Поправка состава F11a (член (4), добавляется этим пунктом; F11a ещё `blocked`, не начат):**',
     '`C:/kyty/f287/f7a/enemy_final_600.rdc` (`181cb236…`) — хэши CS и есть ли в их коде `IMAGE_BVH_INTERSECT_RAY` ['),
    ('571bb3a7', 'docs/ROADMAP.md', 14522, '(г) **RC3 — правило, действует с этой записи',
     '`docs/agent-team.md`:** процесс, создающий устройство Vulkan'),
    ('571bb3a7', 'src/graphics/host_gpu/renderer/indirectArgsSanitizer.cpp', 7, '#include "gpu_tiler_shaders/dispatch_indirect_sanitize_spv.h"',
     '#include "graphics/host_gpu/graphicContext.h"'),
]
ok = True
for c, p, n, a, b in REFS:
    t = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', c + ':' + p], capture_output=True).stdout.decode('utf-8').split(chr(10))
    r = a in t[n - 1] and b in t[n]
    ok &= r
    print('%s:%s:%d %s' % (c, p, n, 'OK' if r else 'FAIL'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
