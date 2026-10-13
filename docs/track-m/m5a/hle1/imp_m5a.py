# M5a HLE1: imports of eboot.bin / sce_module/*.prx for the NIDs of themes T125, T055/T298/T059, T023, T031.
# Method: dynamic entries DT_OS_IMPORT_LIB(_1) / DT_OS_NEEDED_MODULE(_1) found by tag scan, string table base
# found as the most common (name position - name offset); NID strings "<nid>#<lib id>#<mod id>\0".
# Import != call. Prints per-file table of target NIDs with library/module names. Read-only.
import os, re, sys, struct, collections, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('SEALED_RUN.lock present - exit'); sys.exit(3)

GAME = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/'
FILES = [GAME + 'eboot.bin', GAME + 'sce_module/libc.prx', GAME + 'sce_module/libSceNpCppWebApi.prx']
ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"

def enc(i):
    if i < 0x40: return ALPH[i]
    if i < 0x1000: return ALPH[(i >> 6) & 0x3f] + ALPH[i & 0x3f]
    return ALPH[(i >> 12) & 0x3f] + ALPH[(i >> 6) & 0x3f] + ALPH[i & 0x3f]

# our HLE NIDs (src/libs/libAudio.cpp, libC.cpp) - copied from LIB_FUNC lines of dd73d04d
T = {
 'AudioOut2': {'g2tViFIohHE':'Initialize','pDmme7Bgm6E':'ContextQueryMemory','t5YrizufpQc':'ContextResetParam',
  '0x6o1VVAYSY':'ContextCreate','on6ZH7Abo10':'ContextDestroy','4dq2rblWlg0':'ContextSetAttributes',
  'PE2zHMqLSHs':'ContextAdvance','aII9h5nli9U':'ContextPush','R7d0F1g2qsU':'ContextGetQueueLevel',
  'JK2wamZPzwM':'PortCreate','cd+Rtw+D1x8':'PortDestroy','8XTArSPyWHk':'PortSetAttributes',
  'gatEUKG+Ea4':'PortGetState','bkBN+CMLwRc':'GetSystemState','xywYcRB7nbQ':'UserCreate',
  'IaZXJ9M79uo':'UserDestroy','G1YOKDJYX2Y':'GetSpeakerArrayMemorySize','+k91hoTuoA8':'SpeakerArrayCreate',
  'erCWQR5eKiQ':'SpeakerArrayDestroy','4BlZurolOAo':'GetSpeakerArrayCoefficients',
  '28QqMnuuJ9Y':'GetSpeakerArrayAmbisonicsCoefficients','DImz2Ft9E2g':'GetSpeakerInfo',
  'b1HWDUC8zaE':'SetSystemDebugState','TViD1EZXkNI':'Set3DLatency','XHl38ZNknbs':'MasteringInit',
  'v8iOE+j8a5o':'MasteringSetParam','VZidxi2cYh0':'MasteringGetState','2bbBBOkH4CY':'MasteringTerm'},
 'AvPlayer': {'aS66RI0gGgo':'Init','o9eWRkSL+M4':'InitEx','HD1YKVU26-M':'PostInit','KMcEa+rHsIo':'AddSource',
  'x8uvuFOPZhU':'AddSourceEx','hdTyRzCXQeQ':'StreamCount','d8FcbzfAdQw':'GetStreamInfo','ctTAcF5DiKQ':'GetStreamInfoEx',
  'BOVKAzRmuTQ':'DisableStream','ODJK2sn9w4A':'EnableStream','buMCiJftcfw':'ChangeStream','ET4Gr-Uu07s':'Start',
  'NxSdL9t-KXk':'StartEx','ZC17w3vB5Lo':'Stop','9y5v+fGN4Wk':'Pause','w5moABNwnRY':'Resume',
  'k-q+xOxdc3E':'SetAvSyncMode','N6Oy-EjduiY':'SetAvailableBandwidth','OVths0xGfho':'SetLooping',
  'av8Z++94rs0':'SetTrickSpeed','o3+RWnHViSg':'GetVideoData','JdksQu8pNdQ':'GetVideoDataEx',
  'Wnp1OVcrZgk':'GetAudioData','UbQoYawOsfY':'IsActive','wwM99gjFf1Y':'CurrentTime','XC9wM+xULz8':'JumpToTime',
  'NkJwDzKmIlw':'Close','eBTreZ84JFY':'SetLogCallback'},
 'printf': {'GMpvxPFW924':'LibcInternal::vprintf','eLdDw6l0-bU':'LibcInternal::snprintf',
  'hcuQgD53UxM':'libc::printf','YQ0navp+YIc':'libc::puts','Q2V+iqvjgC0':'libc::vsnprintf(HLE LibcInternal::vsnprintf)'},
}

def scan(path):
    d = open(path, 'rb').read()
    sha = hashlib.sha256(d).hexdigest()
    libs, mods = {}, {}
    ents = []
    for tag in (0x61000015, 0x61000049, 0x6100000f, 0x61000045):
        tb = struct.pack('<Q', tag)
        for m in re.finditer(re.escape(tb), d):
            o = m.start()
            if o % 8: continue
            val = struct.unpack_from('<Q', d, o + 8)[0]
            ents.append((tag, o, val))
    # string table base: most common (pos of '\0name\0' - off)
    cnt = collections.Counter()
    namepos = [m.start() + 1 for m in re.finditer(rb'\x00(lib[A-Za-z0-9_]+)\x00', d)]
    nameposset = set(namepos)
    offs = [v & 0xffffffff for (_, _, v) in ents]
    for p in namepos:
        for off in set(offs):
            cnt[p - off] += 1
    base, hits = cnt.most_common(1)[0]
    def nm(off):
        e = d.index(b'\x00', base + off)
        return d[base + off:e].decode('ascii', 'replace')
    for tag, o, v in ents:
        idv = (v >> 48) & 0xffff
        name = nm(v & 0xffffffff)
        if tag in (0x61000015, 0x61000049):
            libs[enc(idv)] = '%s_v%d' % (name, (v >> 32) & 0xffff)
        else:
            mods[enc(idv)] = '%s_v%d.%d' % (name, (v >> 40) & 0xff, (v >> 32) & 0xff)
    imps = collections.defaultdict(set)
    for m in re.finditer(rb'([A-Za-z0-9+\-]{11})#([A-Za-z0-9+\-]{1,3})#([A-Za-z0-9+\-]{1,3})\x00', d):
        nid = m.group(1).decode(); li = m.group(2).decode(); mo = m.group(3).decode()
        imps[nid].add((libs.get(li, '?' + li), mods.get(mo, '?' + mo)))
    return sha, base, hits, libs, mods, imps

out = []
for p in FILES:
    sha, base, hits, libs, mods, imps = scan(p)
    out.append('== %s sha256=%s strtab_base=0x%x (hits %d) libs=%d mods=%d nid_strings=%d' % (
        os.path.basename(p), sha, base, hits, len(libs), len(mods), len(imps)))
    for grp, tbl in T.items():
        n_imp = 0
        for nid, fn in tbl.items():
            if nid in imps:
                n_imp += 1
                out.append('  [%s] %-12s %-45s %s' % (grp, nid, fn, sorted(imps[nid])))
        out.append('  [%s] imported %d of %d HLE NIDs' % (grp, n_imp, len(tbl)))
    # libc printf-family exported/imported by libc.prx names - show library list per file
    out.append('  libs: ' + ', '.join(sorted(set(libs.values()))))
print('\n'.join(out))
