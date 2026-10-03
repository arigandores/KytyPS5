"""seedexp_s9.py - track S, link S9 (HPP-431; ROADMAP "SESSION 122" item 355 (e)): the export of the S-cat catalogue by
tools/shader_seed.py from the local catalogue of the installed binary (translator signature 56189185...:fixb26:fixb1b, the
directory variant_fixb26_fixb1b) into C:/kyty/s288/s9/seeds/PPSA21564.  No game; file copies only, under no lock (the run refuses
rc 5 when C:/kyty/SEALED_RUN.lock exists, before any write and again before the tool).  ps5 em/_ShaderSeeds is not touched.

STEPS
  1. the source: <emulator>/_ShaderCache/PPSA21564/variant_fixb26_fixb1b - its file manifest (name, size, sha256).
  2. the staging copy C:/kyty/s288/s9/stage/PPSA21564: tools/shader_seed.py refuses a cache directory not named after the title
     ("Cache and output directories must be named PPSA21564"); the variant directory postdates the tool.  The copy keeps every
     file byte for byte (manifest equal), and the source manifest read again after the copy must be the same (no writer ran).
     Executor's variant (a question to the lead in the S9 report): the copy is not a code change of the tool.
  3. the tool: python tools/shader_seed.py --cache <stage> --log <log of the installed binary> --output s9/seeds/PPSA21564
     (the log: C:/kyty/p283/p24/log_ia_A3.txt - its json binary 4aa62e95, no KYTY_GAME_PATCH; its line "ShaderSeed:
     compatibility=" is the line of the installed binary).  A refusal of the tool - rc 6, a question to the lead, no code change.
  4. the print: shaders by stage (vs / ps / cs by the file name prefix), recipes (graphics / compute) parsed from the exported
     pipelines.bin (C:/kyty/s288/s7/recipes_s7.py parse(), pinned by sha), duplicate keys (R_DUP_GFX / R_DUP_CS by the stored
     keys and the raw state bytes - Ф17), the removed duplicates (the tool copies pipelines.bin byte for byte: 0 - checked by
     sha), the shaders the recipes do not reference; the compatibility line of the export = the log line (EQUAL / DIFFERENT);
     the offline install check of the emulator (4414e235 pipelineCache.cpp InstallShaderSeed): every shader file begins with the
     translation signature and its 8-byte checksum = XXH3_64 of the rest; pipelines.bin begins with "KytyPR1\\n" + size +
     signature + layout.
  5. the manifest C:/kyty/s288/s9/seeds_manifest.txt: "<name> <bytes> <sha256>" sorted, of every exported file; its sha256 goes
     into the seal 05 (go_s9.sh verifies the catalogue by it before every U arm).
    python seedexp_s9.py
"""
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import time

import xxhash

LOCK = 'C:/kyty/SEALED_RUN.lock'
EMU = 'C:/kyty/KytyPS5/ps5 em'
SRC = EMU + '/_ShaderCache/PPSA21564/variant_fixb26_fixb1b'
STAGE = 'C:/kyty/s288/s9/stage/PPSA21564'
OUT_ROOT = 'C:/kyty/s288/s9/seeds'
OUT = OUT_ROOT + '/PPSA21564'
MANI = 'C:/kyty/s288/s9/seeds_manifest.txt'
TOOL = 'C:/kyty/KytyPS5/tools/shader_seed.py'
LOG = 'C:/kyty/p283/p24/log_ia_A3.txt'
LOG_JSON = 'C:/kyty/p283/p24/ia_A3.json'
INSTALLED = '4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac'
RECIPES_S7 = 'C:/kyty/s288/s7/recipes_s7.py'
SIG = b'KytySC3:56189185f9e9f9a0ea5174f3f85206e6d099db3d:robust:ftz:cbank:fixb26:fixb1b\n'
CKEY = b'ShaderSeed: compatibility='


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def manifest(root):
    return sorted('%s %d %s' % (n, os.path.getsize(os.path.join(root, n)), sha(os.path.join(root, n)))
                  for n in os.listdir(root) if os.path.isfile(os.path.join(root, n)))


def text_sha(lines):
    t = ''.join(x + '\n' for x in lines)
    return t, hashlib.sha256(t.encode('ascii')).hexdigest()


def log_compat(p):
    with open(p, 'rb') as f:
        for i, line in enumerate(f):
            if line.startswith(CKEY):
                return line[len(CKEY):].strip().decode('ascii')
            if i > 200000:
                break
    return None


def check_shader(p, sig=SIG):
    d = open(p, 'rb').read()
    if not d.startswith(sig) or len(d) < len(sig) + 8:
        return 'bad signature'
    (cs,) = struct.unpack_from('<Q', d, len(sig))
    return 'ok' if cs == xxhash.xxh3_64_intdigest(d[len(sig) + 8:]) else 'bad checksum'


def main():
    if os.path.exists(LOCK):
        print('LOCKED: %s exists - nothing done' % LOCK)
        return 5
    print('seedexp_s9 start %s self sha256 %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                                                 sha(os.path.abspath(__file__))))
    print('tool %s sha256 %s' % (TOOL, sha(TOOL)))
    lj = json.load(open(LOG_JSON, encoding='utf-8'))
    env = lj.get('env') or {}
    print('log %s sha256 %s; json binary %s KYTY_GAME_PATCH %s' % (LOG, sha(LOG), lj.get('binary_sha256'),
                                                                 env.get('KYTY_GAME_PATCH')))
    if lj.get('binary_sha256') != INSTALLED or 'KYTY_GAME_PATCH' in env:
        print('STOP: the log is not a run of the installed binary without a patch')
        return 1
    emu_sha = sha(EMU + '/kyty_emulator.exe')
    print('installed binary now %s (%s)' % (emu_sha, 'the seal value' if emu_sha == INSTALLED else 'DIFFERENT'))
    if os.path.exists(OUT) or os.path.exists(STAGE):
        print('STOP: %s or %s exists - the export runs once (the tool refuses an existing output)' % (OUT, STAGE))
        return 1
    m0 = manifest(SRC)
    t0, s0 = text_sha(m0)
    print('source %s files %d sha %s' % (SRC, len(m0), s0))
    if os.path.exists(LOCK):
        print('LOCKED before the copy')
        return 5
    os.makedirs(STAGE)
    for n in sorted(os.listdir(SRC)):
        if os.path.isfile(os.path.join(SRC, n)):
            shutil.copy2(os.path.join(SRC, n), os.path.join(STAGE, n))
    ms = manifest(STAGE)
    m1 = manifest(SRC)
    _, ss = text_sha(ms)
    _, s1 = text_sha(m1)
    print('stage %s files %d sha %s; source again sha %s -> %s' % (STAGE, len(ms), ss, s1,
                                                                  'EQUAL' if ss == s0 == s1 else 'DIFFERENT'))
    if not (ss == s0 == s1):
        print('STOP: the staging copy or the source changed')
        return 1
    if os.path.exists(LOCK):
        print('LOCKED before the tool')
        return 5
    os.makedirs(OUT_ROOT, exist_ok=True)
    p = subprocess.run([sys.executable, TOOL, '--cache', STAGE, '--log', LOG, '--output', OUT], capture_output=True,
                       text=True)
    print('tool rc %d stdout: %s stderr tail: %s' % (p.returncode, p.stdout.strip(), p.stderr.strip()[-400:]))
    if p.returncode != 0:
        print('TOOL REFUSED - a question to the lead (item 355 (e)), no code change')
        return 6
    mf = json.load(open(OUT + '/manifest.json', encoding='utf-8'))
    comp = open(OUT + '/compatibility.txt', encoding='ascii').read().strip()
    lc = log_compat(LOG)
    print('compatibility.txt: %s' % comp)
    print('log line         : %s' % lc)
    print('compatibility of the export = the line of the installed binary log: %s' % ('EQUAL' if comp == lc else 'DIFFERENT'))
    names = [n for n in mf['files'] if n != 'pipelines.bin']
    st = {}
    for n in names:
        st[n.split('_', 1)[0]] = st.get(n.split('_', 1)[0], 0) + 1
    print('shaders by stage: %s; total %d (manifest.json shaders %d); recipes (manifest.json) %d' % (
        ' '.join('%s %d' % kv for kv in sorted(st.items())), len(names), mf['shaders'], mf['recipes']))
    same = sha(OUT + '/pipelines.bin') == sha(STAGE + '/pipelines.bin')
    print('pipelines.bin of the export = the staged one (byte for byte): %s -> removed duplicates (F17): %s' % (
        same, '0 (the tool copies the recipe file unchanged)' if same else 'UNDETERMINED'))
    spec = importlib.util.spec_from_file_location('recipes_s7', RECIPES_S7)
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    head, recs = R.parse(OUT + '/pipelines.bin')
    gfx = [r for r in recs if r['kind'] == 1]
    cs = [r for r in recs if r['kind'] == 2]
    kg = {}
    kc = {}
    dg = dc = 0
    refs = set()
    for r in recs:
        if r['kind'] == 1:
            key = (r['ren'], r['vin'], r['sta'], (r['vk'], r['vi']), (r['pk'], r['pi']) if r['pk'] is not None else None)
            dg += key in kg
            kg.setdefault(key, r['i'])
            refs.add(R.path_name(r['vk']))
            if r['pk'] is not None:
                refs.add(R.path_name(r['pk']))
        else:
            key = (r['ck'], r['ci'])
            dc += key in kc
            kc.setdefault(key, r['i'])
            refs.add(R.path_name(r['ck']))
    print('recipes_s7.py sha256 %s; recipes parsed %d (header %d, at_end %s): graphics %d, compute %d; duplicate keys in the '
          'export (F17 kinds): R_DUP_GFX %d, R_DUP_CS %d' % (sha(RECIPES_S7), len(recs), head['count'], head['at_end'], len(gfx),
                                                           len(cs), dg, dc))
    print('shader files referenced by recipes %d; exported shader files not referenced %d; referenced but absent %d' % (
        len(refs), sum(1 for n in names if n not in refs), sum(1 for n in refs if n not in names)))
    bad = [(n, check_shader(OUT + '/' + n)) for n in names]
    bad = [x for x in bad if x[1] != 'ok']
    rp = open(OUT + '/pipelines.bin', 'rb').read(16 + 512)
    (size,) = struct.unpack_from('<I', rp, 8)
    rsig = rp[12:12 + size]
    print('offline install check (InstallShaderSeed): shader files with a bad signature or checksum %d %s; recipe header '
          'magic %s, signature+layout %s' % (len(bad), bad[:3], rp[:8] == b'KytyPR1\n', rsig.decode('ascii', 'replace')
                                             .replace('\n', '|')))
    lines = manifest(OUT)
    text, msha = text_sha(lines)
    with open(MANI, 'w', encoding='ascii', newline='\n') as f:
        f.write(text)
    print('SEEDS manifest %s files %d sha256 %s (= sha256 of the file %s)' % (MANI, len(lines), msha, sha(MANI)))
    print('compatibility.txt sha256 %s manifest.json sha256 %s pipelines.bin sha256 %s' % (
        sha(OUT + '/compatibility.txt'), sha(OUT + '/manifest.json'), sha(OUT + '/pipelines.bin')))
    print('seedexp_s9 end %s' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    ok = comp == lc and same and not bad and head['at_end'] and len(recs) == mf['recipes']
    print('EXPORT: %s' % ('OK' if ok else 'CHECK FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
