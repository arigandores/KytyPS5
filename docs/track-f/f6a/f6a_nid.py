# F6a (HPP-372): NID formula check on known pairs and the two names that are not in the eboot strings (object x verb search).
import hashlib, base64, struct, re
SUF = bytes.fromhex('518D64A635DED8C1E6B039B1C3E55230')
def nid(name):
    d = hashlib.sha1(name.encode() + SUF).digest()[:8]
    return base64.b64encode(struct.pack('>Q', struct.unpack('<Q', d)[0]), b'+-').decode().rstrip('=')
if __name__ == '__main__':
    src = open('C:/kyty/KytyPS5/src/libs/libAudio.cpp', encoding='utf-8', errors='replace').read()
    known = re.findall(r'LIB_FUNC\("([^"]+)",\s*LibAudioPropagation::(\w+)\)', src)
    ok = 0
    for n, f in known:
        r = nid('sce' + f) == n; ok += r
        print('%s sce%s %s' % (n, f, 'OK' if r else 'MISMATCH'))
    r = nid('sceKernelGetProcessTimeCounter') == 'fgxnMeTNUtY'; ok += r
    print('fgxnMeTNUtY sceKernelGetProcessTimeCounter %s' % ('OK' if r else 'MISMATCH'))
    print('formula check: %d of %d' % (ok, len(known) + 1))
    assert ok == len(known) + 1 == 7
    want = {'ZQXE-xS6MTE', 'x5VPqg5iyAk'}
    objs = ['System', 'Room', 'Portal', 'Source', 'Material', 'Listener', 'Context', 'MaterialSet', '']
    verbs = ['Destroy', 'Create', 'SetAttributes', 'GetAttributes', 'Update', 'Render', 'Release', 'Delete', 'Terminate', 'Finalize', 'Initialize', 'Init', 'Term', 'Reset', 'Lock', 'Unlock', 'SetRays', 'GetRays', 'Flush', 'Commit', 'Step', 'Process', 'QueryMemory', 'SetGeometry', 'SetListener', 'SetRoom', 'SetPortal', 'AddPortal', 'RemovePortal', 'AddRoom', 'RemoveRoom', 'Free', 'Close', 'Open', 'Start', 'Stop', 'GetInfo', 'GetStatus', 'GetMemoryInfo', 'UnregisterMaterial', 'RegisterMaterial', 'ReportApi', 'GetVersion']
    found = {}
    for o in objs:
        for v in verbs:
            n = 'sceAudioPropagation' + o + v
            if nid(n) in want: found[nid(n)] = n
    print('candidates tried: %d' % (len(objs) * len(verbs)))
    for k in sorted(found): print('MATCH %s %s' % (k, found[k]))
    assert set(found) == want
    print('ALL OK')
