# Red Team s145 step 1: can the message-id filter hide another message? Hash every id-like string of the
# validation layer binary with XXH32 (seed 8 = vvl VuidHash [I, from memory of the layer source]; seed 0 also printed)
# and look for any string whose hash equals the filter's. Pure-python XXH32 with test vectors.
import re, sys, hashlib
P1, P2, P3, P4, P5 = 2654435761, 2246822519, 3266489917, 668265263, 374761393
M = 0xFFFFFFFF
def rotl(x, r):
    return ((x << r) | (x >> (32 - r))) & M
def xxh32(b, seed=0):
    n = len(b); i = 0
    if n >= 16:
        v1 = (seed + P1 + P2) & M; v2 = (seed + P2) & M; v3 = seed & M; v4 = (seed - P1) & M
        while i + 16 <= n:
            for k in range(4):
                lane = int.from_bytes(b[i:i + 4], 'little'); i += 4
                if k == 0: v1 = (rotl((v1 + lane * P2) & M, 13) * P1) & M
                elif k == 1: v2 = (rotl((v2 + lane * P2) & M, 13) * P1) & M
                elif k == 2: v3 = (rotl((v3 + lane * P2) & M, 13) * P1) & M
                else: v4 = (rotl((v4 + lane * P2) & M, 13) * P1) & M
        h = (rotl(v1, 1) + rotl(v2, 7) + rotl(v3, 12) + rotl(v4, 18)) & M
    else:
        h = (seed + P5) & M
    h = (h + n) & M
    while i + 4 <= n:
        h = (rotl((h + int.from_bytes(b[i:i + 4], 'little') * P3) & M, 17) * P4) & M; i += 4
    while i < n:
        h = (rotl((h + b[i] * P5) & M, 11) * P1) & M; i += 1
    h ^= h >> 15; h = (h * P2) & M; h ^= h >> 13; h = (h * P3) & M; h ^= h >> 16
    return h
tv = [(b'', 0, 0x02CC5D05), (b'Nobody inspects the spammish repetition', 0, 0xE2293B2F)]
for s, sd, want in tv:
    got = xxh32(s, sd)
    print('test vector %r seed %d: %08x want %08x %s' % (s[:20], sd, got, want, 'OK' if got == want else 'FAIL'))
DLL = 'C:/VulkanSDK/1.4.357.0/Bin/VkLayer_khronos_validation.dll'
data = open(DLL, 'rb').read()
print('dll sha256', hashlib.sha256(data).hexdigest())
FILT = b'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
ids = set(re.findall(rb'(?<![A-Za-z0-9_\-])((?:VUID|UNASSIGNED|Undefined|BestPractices|WARNING|SYNC|GPU|DEBUG|Shader|SPIRV|RuntimeSpirv|VVL|AVF|ERROR|Threading|ObjectTracker|INVALID|kVUID)[A-Za-z0-9_\-]*-[A-Za-z0-9_\-]+)(?=\x00)', data))
ids2 = set(re.findall(rb'(?<=\x00)([A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z0-9_]+)+)(?=\x00)', data))
allids = ids | ids2
print('id-like strings: prefixed %d, any dash-joined nul-terminated %d, union %d' % (len(ids), len(ids2), len(allids)))
print('filter string present:', FILT in allids, 'occurrences in dll:', data.count(FILT + b'\x00'))
for seed in (8, 0):
    fh = xxh32(FILT, seed)
    coll = sorted(s for s in allids if s != FILT and xxh32(s, seed) == fh)
    print('seed %d: filter hash %08x (%d); other strings with the same hash: %d %s' % (seed, fh, fh, len(coll), [c.decode() for c in coll][:5]))
    # also the decimal hash and 5-digit forms the layer accepts: does any id end with the same last 5 digits as the filter token? (token has no digits)
print('filter token digits:', re.findall(rb'[0-9]+', FILT))
pref = sorted(s for s in allids if s.startswith(b'Undefined-Value-ShaderOutputNotConsumed'))
print('strings with the filter prefix:', [p.decode() for p in pref])
