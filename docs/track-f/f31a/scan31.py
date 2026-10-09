# F31a: one pass over a log - sigs, counts of line kinds, FrameTrace tail, level lines, env lines
import sys, re, json, collections
path = sys.argv[1]
SIG = {'E': b'There are too many objects/batches', 'S1': b'command_buffer_writer.ppr.cpp', 'S3': b'pc=0x00000009004a020e'}
cnt = collections.Counter()
first = {}
lvl = []
ft = []  # last FrameTrace lines
ftx = []
heads = []
n = 0
with open(path, 'rb') as f:
    for line in f:
        n += 1
        for k, s in SIG.items():
            if s in line:
                cnt[k] += 1
                first.setdefault(k, n)
        if b'Level has started:' in line or b'LevelDocument Loaded' in line:
            lvl.append((n, line.strip()[:200].decode('utf-8', 'replace')))
        if line.startswith(b'FrameTrace-x') or b'FrameTrace-x' in line[:40]:
            ftx.append((n, line.strip()[:2000].decode('utf-8', 'replace')))
            if len(ftx) > 40:
                ftx.pop(0)
        elif b'FrameTrace' in line[:30]:
            ft.append((n, line.strip()[:600].decode('utf-8', 'replace')))
            if len(ft) > 40:
                ft.pop(0)
        if n <= 120:
            heads.append(line.strip()[:300].decode('utf-8', 'replace'))
        for key in (b'--- Error ---', b'Unhandled host exception', b'ASSERT', b'RtSkip', b'Fork build', b'MemStats', b'FaultTrace-gpu', b'skipped draw', b'GpuHangAbort'):
            if key in line:
                cnt[key.decode()] += 1
print(json.dumps({'lines': n, 'cnt': cnt, 'first': first, 'lvl': lvl[:20]}, ensure_ascii=False, indent=1))
print('--- heads')
for h in heads:
    print(h)
print('--- last FrameTrace')
for k, l in ft[-12:]:
    print(k, l)
print('--- last FrameTrace-x')
for k, l in ftx[-6:]:
    print(k, l)
