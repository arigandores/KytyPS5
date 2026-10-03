# F13d (HPP-485, Red Team): offline scans for the review of the F13b outcome on B41 (no game, no Vulkan device).
#   python f13d_scan.py <outdir>
# Writes:
#   markers.txt   - per log: counts of HLE marker lines before / after the level entry (unresolved-import stub calls are
#                   logged for the first 1024 calls, runtimeLinker.cpp:405-406; SaveData, UDS, NpTrophy2 functions log
#                   their parameters unconditionally with LOGF; SystemServiceReceiveEvent logs nothing).
#   trans.txt     - per log: GuestOut / LevelDocument lines after the entry with frame k, opens per 300 frames, last k.
#   ramp_f13_k.txt- mean luma (YAVG) of rec_f13_k.mp4 frames 1280..1480 (card end k 1253 = video frame ~1387).
#   level_local.txt (game data excerpt - local only, not for git): parent_level.txt of the scene, flow lines of the
#                   child and of the parent level.lvx.
import collections, os, pathlib, re, subprocess, sys

OUT = pathlib.Path(sys.argv[1])
LOGS = [('f13_k', 'C:/kyty/f287/f13a/log_f13_k.txt', 'ending_boss_after_credit'),
        ('f13_rd', 'C:/kyty/f287/f13a/log_f13_rd.txt', 'ending_boss_after_credit'),
        ('v146_08', 'C:/kyty/s146/log_v146_08.txt', 'ending_boss_after_credit'),
        ('w146_08', 'C:/kyty/s146/log_w146_08.txt', 'ending_boss_after_credit'),
        ('v146_07', 'C:/kyty/s146/log_v146_07.txt', 'non_interactive_credit')]
MARKS = [b'Unresolved import stub called', b'Late-resolved import', b'Relocate: unresolved', b'event_name =',
         b'\t context =', b'mount_point', b'sync_param', b'event_param', b'SavePersist:', b'GuestOut:',
         b'LevelDocument Loaded:', b'\tOpen: ', b'slot_id', b'data_num =', b'icon_memory_size']


def scan(tag, path, lvl):
    ent = b'GuestOut: Level has started: ' + lvl.encode()
    side = 0; k = 0
    cnt = {m: [0, 0] for m in MARKS}
    ev = []; opens = collections.Counter()
    with open(path, 'rb') as f:
        for l in f:
            if side == 0 and ent in l:
                side = 1; ev.append((0, l.strip()[:150])); continue
            if side and l.startswith(b'FrameTrace: n='):
                k += 1; continue
            for m in MARKS:
                if m in l: cnt[m][side] += 1
            if side:
                if l.startswith(b'\tOpen: '): opens[k // 300] += 1
                if (b'GuestOut:' in l or b'LevelDocument' in l) and len(ev) < 40: ev.append((k, l.strip()[:150]))
    return cnt, ev, opens, k


mk = []; tr = []
for tag, path, lvl in LOGS:
    cnt, ev, opens, k = scan(tag, path, lvl)
    mk.append('== %s %s (entry marker: Level has started: %s)' % (tag, path, lvl))
    for m in MARKS:
        mk.append('  %-32s before_entry %8d  after_entry %8d' % (m.decode().strip(), cnt[m][0], cnt[m][1]))
    tr.append('== %s last_k_after_entry %d' % (tag, k))
    for kk, s in ev: tr.append('  %6d %s' % (kk, s.decode('utf-8', 'replace')))
    tr.append('  opens per 300 frames after entry: %s' % sorted(opens.items()))
(OUT / 'markers.txt').write_bytes(('\n'.join(mk) + '\n').encode())
(OUT / 'trans.txt').write_bytes(('\n'.join(tr) + '\n').encode())

yfile = OUT / 'yavg_raw.txt'
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', 'C:/kyty/f287/f13a/rec_f13_k.mp4', '-vf',
                r"select='between(n\,1280\,1480)',signalstats,"
                "metadata=print:key=lavfi.signalstats.YAVG:file=yavg_raw.txt",
                '-vsync', '0', '-f', 'null', '-'], cwd=str(OUT), check=True)
ys = [float(m.group(1)) for m in re.finditer(r'YAVG=([\d.]+)', yfile.read_text())]
yfile.unlink()
first_drop = next(i for i, v in enumerate(ys) if v < ys[0] - 0.5)
first_black = next(i for i, v in enumerate(ys) if v <= 16.0)
ramp = ['rec_f13_k.mp4 frames 1280..%d: %d values' % (1280 + len(ys) - 1, len(ys)),
        'first frame below the card level %.1f: %d; first frame at black 16.0: %d; ramp %d frames' %
        (ys[0], 1280 + first_drop, 1280 + first_black, first_black - first_drop),
        'monotone non-increasing over the ramp: %s' % all(ys[i + 1] <= ys[i] + 0.01 for i in range(first_drop, first_black)),
        'values: ' + ' '.join('%d:%.1f' % (1280 + i, v) for i, v in enumerate(ys))]
(OUT / 'ramp_f13_k.txt').write_bytes(('\n'.join(ramp) + '\n').encode())

D = pathlib.Path('C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/data/prein/levels')
lv = ['parent_level.txt of ending_boss_after_credit: %r' % (D / 'ending_boss_after_credit/parent_level.txt').read_text().strip(),
      'files of ending_boss_after_credit: %s' % sorted(p.name for p in (D / 'ending_boss_after_credit').iterdir())]
key = re.compile(r'Fade|Finish|finish|Next|Level type|room_finisher|Name>|Video|Skip|play_trigger')
for name in ('ending_boss_after_credit', 'non_interactive_credit'):
    lv.append('== %s/level.lvx' % name)
    for i, line in enumerate((D / name / 'level.lvx').read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if key.search(line): lv.append('  %4d %s' % (i, line.strip()[:150]))
(OUT / 'level_local.txt').write_bytes(('\n'.join(lv) + '\n').encode())
print('ALL OK')
