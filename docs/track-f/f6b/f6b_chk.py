"""F6b (HPP-373): lead recount of F6a (docs/track-f/f6a-b9a.md) claims, own code, does not import F6a scripts.
(1) NID = hash(name) for the 22 names of table 1; (2) HLE NIDs in libAudio.cpp at HEAD; (3) stub-call profile in c142_03 and the 5-log sweep."""
import base64, hashlib, re, struct, subprocess, sys
SUF = bytes.fromhex('518D64A635DED8C1E6B039B1C3E55230')
def nid(name):
    d = hashlib.sha1(name.encode() + SUF).digest()
    v = struct.unpack('<Q', d[:8])[0]
    return base64.b64encode(struct.pack('>Q', v)).decode().rstrip('=').replace('/', '-')
T = [('XKCN4gpeYsM', 'SystemUnregisterMaterial'), ('VlBT16890mA', 'SystemSetRays'), ('ZQXE-xS6MTE', 'PortalDestroy'),
     ('kIdb+iQUzCs', 'SystemSetAttributes'), ('5vzOS2pHMFc', 'SourceSetAudioPaths'), ('aNEqtSHdUSo', 'SystemCreate'),
     ('CPLV6G-eXmk', 'SystemRegisterMaterial'), ('WXMhENV2NcA', 'PortalSetAttributes'), ('b-dYXrjSNZU', 'PortalCreate'),
     ('S0JwP2AFTTE', 'RoomDestroy'), ('x5VPqg5iyAk', 'SystemDestroy'), ('d84otraxt2s', 'SourceCreate'),
     ('-wsUTr31yeg', 'SourceSetAttributes'), ('aKJZx7wCma8', 'SourceGetRays'), ('7xyAxrusLko', 'SystemQueryMemory'),
     ('G+QLTfyLMYk', 'SourceGetAudioPathCount'), ('ht-QXT3zGxo', 'SystemGetRays'), ('wkseM3LWPuc', 'SourceDestroy'),
     ('hhz9pITnC8k', 'SourceRender'), ('eEeKqFeNI3o', 'SourceGetAudioPath'), ('8bI5h8req30', 'RoomCreate'),
     ('PBcrVpEqUVY', 'SourceCalculateAudioPaths')]
ok = True
assert nid('sceKernelGetProcessTimeCounter') == 'fgxnMeTNUtY', nid('sceKernelGetProcessTimeCounter')
bad = [(n, f) for n, f in T if nid('sceAudioPropagation' + f) != n]
print('NID==hash(name):', len(T) - len(bad), 'of', len(T), bad)
ok &= not bad and len(T) == 22 and len({n for n, _ in T}) == 22
src = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', 'HEAD:src/libs/libAudio.cpp'],
                     capture_output=True, check=True).stdout.decode('utf-8')
hle = set(re.findall(r'LIB_FUNC\("([^"]+)",\s*LibAudioPropagation::', src))
lib = {n for n, _ in T}
print('HLE in libAudio.cpp (AudioPropagation):', len(hle), sorted(hle), 'subset of 22:', hle <= lib)
ok &= len(hle) == 6 and hle <= lib
called = ['b-dYXrjSNZU', 'WXMhENV2NcA', 'd84otraxt2s', 'G+QLTfyLMYk']
ok &= not (set(called) & hle)
rx = re.compile(rb'Unresolved import stub called \[\d+\]:.*?symbol=([^\[\s]+)')
def prof(p):
    c = {}
    with open(p, 'rb') as f:
        for ln in f:
            if b'Unresolved import stub called [' in ln:
                m = rx.search(ln)
                if m:
                    k = m.group(1).decode()
                    c[k] = c.get(k, 0) + 1
    return c
for tag, p in [('c142_03', 'C:/kyty/s142/log_c142_03.txt'), ('v144_13', 'C:/kyty/s144/log_v144_13.txt'),
               ('w144_13', 'C:/kyty/s144/log_w144_13.txt'), ('v143_03', 'C:/kyty/s143/log_v143_03.txt'),
               ('w144_03', 'C:/kyty/s144/log_w144_03.txt')]:
    try:
        c = prof(p)
    except FileNotFoundError:
        print(tag, 'MISSING'); ok = False; continue
    print(tag, [(k, c.get(k, 0)) for k in called], 'other:', {k: v for k, v in c.items() if k not in called})
    if tag == 'c142_03':
        ok &= [c.get(k, 0) for k in called] == [2, 295, 365, 362] and sum(c.values()) == 1024
print('F6B RECOUNT ALL OK' if ok else 'F6B RECOUNT FAIL')
sys.exit(0 if ok else 1)
