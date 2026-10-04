"""seedexp_s13.py - track S, link S13a (HPP-498; ROADMAP "SESSION 122" item 408 (l), (z), item 355 (e)): the export of the
catalogue collected by the arms k_01 .. k_19 of S13b - tools/shader_seed.py from the post copy of the last collection arm
(C:/kyty/s288/s13/cat/k_19/ShaderCache_PPSA21564/<variant>) into C:/kyty/s288/s13/seeds/PPSA21564.  The port of
C:/kyty/s288/s9/seedexp_s9.py (S9, accepted by item 364).  No game; file copies only, under no lock (the run refuses rc 5 when
C:/kyty/SEALED_RUN.lock exists, before any write and again before the tool).  ps5 em/_ShaderSeeds is not touched.

STEPS
  0. the seal in force (sc_s13.current_seal) names the installed binary, its signature and its variant ("installed: <sha256>
     <signature> <variant>"); "installed: PENDING" -> rc 6 (no export before the edition).
  1. the source: the post copy cat/k_19 - its MANIFEST.txt = app_post_copy of runs_s/k_19.cache.json (the harness noted it), and
     cachex_s.py verify app (the files = the MANIFEST.txt) - else rc 1; the variant directory of the seal inside it; its file
     manifest (name, size, sha256).
  2. the log of k_19 (log_k_19.txt): its json binary = the seal line, no KYTY_GAME_PATCH, its compatibility line carries the
     signature of the seal line - else rc 1.
  3. the staging copy C:/kyty/s288/s13/stage/PPSA21564 (the tool refuses a directory not named after the title; S9 V5): byte for
     byte, the source manifest read again after the copy is the same.
  4. the tool: python tools/shader_seed.py --cache <stage> --log <log_k_19.txt> --output s13/seeds/PPSA21564; a refusal - rc 6, a
     question to the lead, no code change.
  5. the print: shaders by stage, recipes (graphics / compute) parsed from the exported pipelines.bin (s7/recipes_s7.py parse()),
     duplicate keys R_DUP_GFX / R_DUP_CS, the line "removed duplicates (F17): N" (item 408 (z): the tool copies pipelines.bin byte
     for byte -> 0, else UNDETERMINED), the shaders not referenced by a recipe; "compatibility.txt: <line>" and its equality with
     the log line; the offline install check (signature + XXH3 of every shader file, the recipe header).
  6. the manifest C:/kyty/s288/s13/seeds_manifest.txt ("<name> <bytes> <sha256>" sorted) and the line "SEEDS manifest <path>
     files N sha256 <sha>"; the line "source arm k_19 app_post_copy <sha>"; "EXPORT: OK" when every check holds.
    python seedexp_s13.py
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

LOCK = 'C:/kyty/SEALED_RUN.lock'
LINK = 'C:/kyty/s288/s13'
LAST = 'k_19'
STAGE = LINK + '/stage/PPSA21564'
OUT_ROOT = LINK + '/seeds'
OUT = OUT_ROOT + '/PPSA21564'
MANI = LINK + '/seeds_manifest.txt'
TOOL = 'C:/kyty/KytyPS5/tools/shader_seed.py'
RECIPES_S7 = 'C:/kyty/s288/s7/recipes_s7.py'
SC13 = 'C:/kyty/s288/s13/sc_s13.py'
CACHEX = 'C:/kyty/s288/cachex_s.py'
CKEY = b'ShaderSeed: compatibility='
NL = chr(10)


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
    t = ''.join(x + NL for x in lines)
    return t, hashlib.sha256(t.encode('ascii')).hexdigest()


def log_compat(p):
    with open(p, 'rb') as f:
        for i, line in enumerate(f):
            if line.startswith(CKEY):
                return line[len(CKEY):].strip().decode('ascii')
            if i > 200000:
                break
    return None


def check_shader(p, sig):
    import xxhash
    d = open(p, 'rb').read()
    if not d.startswith(sig) or len(d) < len(sig) + 8:
        return 'bad signature'
    (cs,) = struct.unpack_from('<Q', d, len(sig))
    return 'ok' if cs == xxhash.xxh3_64_intdigest(d[len(sig) + 8:]) else 'bad checksum'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dups(recs):
    """(R_DUP_GFX, R_DUP_CS, the referenced shader file names) - the keys of seedexp_s9.py (F17 kinds)."""
    kg, kc, dg, dc, refs = {}, {}, 0, 0, set()
    for r in recs:
        if r['kind'] == 1:
            key = (r['ren'], r['vin'], r['sta'], (r['vk'], r['vi']), (r['pk'], r['pi']) if r['pk'] is not None else None)
            dg += key in kg
            kg.setdefault(key, r['i'])
        else:
            key = (r['ck'], r['ci'])
            dc += key in kc
            kc.setdefault(key, r['i'])
    return dg, dc


def main(link=LINK, tool=TOOL, sc13=SC13, recipes=RECIPES_S7, cachex=CACHEX, check_files=True, pr=print):
    if os.path.exists(LOCK):
        pr('LOCKED: %s exists - nothing done' % LOCK)
        return 5
    stage, out_root = link + '/stage/PPSA21564', link + '/seeds'
    out, mani = out_root + '/PPSA21564', link + '/seeds_manifest.txt'
    pr('seedexp_s13 start %s self sha256 %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), sha(os.path.abspath(__file__))))
    S = load(sc13, 'sc_s13_for_export')
    seal = S.current_seal()
    inst = S.seal_installed(seal)
    pr('seal in force %s sha256 %s; installed line %s' % (seal, sha(seal) if os.path.isfile(seal) else 'missing',
                                                         ' '.join(x for x in inst if x) if inst else 'MALFORMED'))
    if inst is None or inst[0] == 'PENDING':
        pr('STOP: the seal names no installed binary (rc 6) - an edition by a lead item first')
        return 6
    ish, isig, ivar = inst
    pr('tool %s sha256 %s' % (tool, sha(tool)))
    cj = json.load(open('%s/runs_s/%s.cache.json' % (link, LAST), encoding='utf-8'))
    pc = (cj.get('app_post_copy') or {}).get('sha')
    cat = '%s/cat/%s' % (link, LAST)
    ms = sha(cat + '/MANIFEST.txt') if os.path.isfile(cat + '/MANIFEST.txt') else None
    v = subprocess.run([sys.executable, cachex, '--tag', 'seedexp', 'verify', 'app', cat, pc or '-'], capture_output=True,
                       text=True) if check_files else None
    pr('source arm %s app_post_copy %s' % (LAST, pc))
    pr('post copy %s MANIFEST.txt sha256 %s; cachex verify rc %s %s' % (cat, ms, v.returncode if v else 'skipped',
                                                                       (v.stdout.strip() if v else '')[:200]))
    if pc is None or ms != pc or (v is not None and v.returncode != 0):
        pr('STOP: the post copy of %s is not the one the harness noted' % LAST)
        return 1
    src = '%s/ShaderCache_PPSA21564/%s' % (cat, ivar)
    if not os.path.isdir(src):
        pr('STOP: no variant directory %s in the post copy' % src)
        return 1
    log = '%s/log_%s.txt' % (link, LAST)
    lj = json.load(open('%s/%s.json' % (link, LAST), encoding='utf-8'))
    env = lj.get('env') or {}
    lc = log_compat(log)
    pr('log %s sha256 %s; json binary %s KYTY_GAME_PATCH %s; compatibility line %s' % (log, sha(log), lj.get('binary_sha256'),
                                                                                     env.get('KYTY_GAME_PATCH'), lc))
    if lj.get('binary_sha256') != ish or 'KYTY_GAME_PATCH' in env or lc is None or (':' + isig + ':') not in (':' + lc + ':'):
        pr('STOP: the log of %s is not a run of the installed binary of the seal without a patch on its signature' % LAST)
        return 1
    if os.path.exists(out) or os.path.exists(stage):
        pr('STOP: %s or %s exists - the export runs once (the tool refuses an existing output)' % (out, stage))
        return 1
    m0 = manifest(src)
    _, s0 = text_sha(m0)
    pr('source %s files %d sha %s' % (src, len(m0), s0))
    if os.path.exists(LOCK):
        pr('LOCKED before the copy')
        return 5
    os.makedirs(stage)
    for n in sorted(os.listdir(src)):
        if os.path.isfile(os.path.join(src, n)):
            shutil.copy2(os.path.join(src, n), os.path.join(stage, n))
    _, ss = text_sha(manifest(stage))
    _, s1 = text_sha(manifest(src))
    pr('stage %s sha %s; source again sha %s -> %s' % (stage, ss, s1, 'EQUAL' if ss == s0 == s1 else 'DIFFERENT'))
    if not (ss == s0 == s1):
        pr('STOP: the staging copy or the source changed')
        return 1
    if os.path.exists(LOCK):
        pr('LOCKED before the tool')
        return 5
    os.makedirs(out_root, exist_ok=True)
    p = subprocess.run([sys.executable, tool, '--cache', stage, '--log', log, '--output', out], capture_output=True, text=True)
    pr('tool rc %d stdout: %s stderr tail: %s' % (p.returncode, p.stdout.strip(), p.stderr.strip()[-400:]))
    if p.returncode != 0:
        pr('TOOL REFUSED - a question to the lead (item 408 (l)), no code change')
        return 6
    mf = json.load(open(out + '/manifest.json', encoding='utf-8'))
    comp = open(out + '/compatibility.txt', encoding='ascii').read().strip()
    pr('compatibility.txt: %s' % comp)
    pr('log line: %s' % lc)
    pr('compatibility of the export = the line of the log of %s: %s' % (LAST, 'EQUAL' if comp == lc else 'DIFFERENT'))
    names = [n for n in mf['files'] if n != 'pipelines.bin']
    st = {}
    for n in names:
        st[n.split('_', 1)[0]] = st.get(n.split('_', 1)[0], 0) + 1
    pr('shaders by stage: %s; total %d (manifest.json shaders %d); recipes (manifest.json) %d' % (
        ' '.join('%s %d' % kv for kv in sorted(st.items())), len(names), mf['shaders'], mf['recipes']))
    same = sha(out + '/pipelines.bin') == sha(stage + '/pipelines.bin')
    pr('removed duplicates (F17): %s (pipelines.bin of the export = the staged one byte for byte: %s)' % (
        '0' if same else 'UNDETERMINED', same))
    R = load(recipes, 'recipes_s7')
    head, recs = R.parse(out + '/pipelines.bin')
    dg, dc = dups(recs)
    refs = set()
    for r in recs:
        if r['kind'] == 1:
            refs.add(R.path_name(r['vk']))
            if r['pk'] is not None:
                refs.add(R.path_name(r['pk']))
        else:
            refs.add(R.path_name(r['ck']))
    pr('recipes_s7.py sha256 %s; recipes parsed %d (header %d, at_end %s): graphics %d, compute %d; duplicate keys in the export '
       '(F17 kinds): R_DUP_GFX %d, R_DUP_CS %d' % (sha(recipes), len(recs), head['count'], head['at_end'],
                                                   sum(1 for r in recs if r['kind'] == 1), sum(1 for r in recs if r['kind'] == 2),
                                                   dg, dc))
    pr('shader files referenced by recipes %d; exported shader files not referenced %d; referenced but absent %d' % (
        len(refs), sum(1 for n in names if n not in refs), sum(1 for n in refs if n not in names)))
    sigb = (isig + NL).encode('ascii')
    bad = [(n, check_shader(out + '/' + n, sigb)) for n in names] if check_files else []
    bad = [x for x in bad if x[1] != 'ok']
    rp = open(out + '/pipelines.bin', 'rb').read(16 + 512)
    (size,) = struct.unpack_from('<I', rp, 8)
    rsig = rp[12:12 + size]
    pr('offline install check (InstallShaderSeed): shader files with a bad signature or checksum %d %s; recipe header magic %s, '
       'signature+layout %s' % (len(bad), bad[:3], rp[:8] == b'KytyPR1' + NL.encode(),
                                rsig.decode('ascii', 'replace').replace(NL, '|')))
    lines = manifest(out)
    text, msha = text_sha(lines)
    with open(mani, 'w', encoding='ascii', newline=NL) as f:
        f.write(text)
    pr('SEEDS manifest %s files %d sha256 %s (= sha256 of the file %s)' % (mani, len(lines), msha, sha(mani)))
    pr('seedexp_s13 end %s' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    ok = comp == lc and same and not bad and head['at_end'] and len(recs) == mf['recipes'] and rsig.startswith(sigb)
    pr('EXPORT: %s' % ('OK' if ok else 'CHECK FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
