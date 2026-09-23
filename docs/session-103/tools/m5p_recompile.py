"""m5p_recompile.py -- session 103, M5' (C:/kyty/s103/pred/02_m5p_bench.md): the offline modules of
arms A, V1 and V2p (the seal's "V2'") for EVERY permutation of EVERY sealed item (102 pred/01 s2,
unchanged), their spirv-val, their driver statistics and SASS.  No game run: shader_cfg_tests.exe
(KYTY_RECOMPILE), spirv-val, pipestat (a real driver compile, no capture), nvdisasm.  Everything runs
sequentially, one process at a time.

  A  : KYTY_RECOMPILE, no switch
  V1 : KYTY_RECOMPILE_CBANK=0
  V2p: KYTY_RECOMPILE_BDA=1 KYTY_BDA_LEAN=1 (the session-102 V2 IR rewrite, emitted by the lean
       session-103 BDA emitter: no fault store in PS, one page-table read per lookup, read-only PSB
       views, run-time 16-byte alignment test selecting uvec4 loads)

Derived from m5_recompile.py by copying and minimal editing.  Differences:
  * arms A / V1 / V2p (V2 and V2s are not built); dumps (KYTY_RECOMPILE_DUMP) of A and V2p;
  * CACHE_DIR = the snapshot C:/kyty/cache_snap/PPSA21564_2db9065a (new s2: the live _ShaderCache has
    been overwritten by another translator); every cache file used is checked against the snapshot's
    manifest_2db9065a.json;
  * refuses to run unless the three seals match and shader_cfg_tests.exe has the sealed sha256
    e7a15418...; the item table is parsed from the parent 102 pred/01 s2 (the M5' seal inherits it);
  * every regs.json row carries 'ldg_variants' (every LDG opcode with its full suffix, from the whole
    SASS: LDG.E.CONSTANT, LDG.E.128.CONSTANT, LDG.E.STRONG.SM, LDG.E.64, ...), 'stl'/'ldl' counts;
  * a V2p layout check (the V2 rule of m5_layout_check.py: V2p declares A's bindings plus the page table
    and the fault buffer, the same user-data registers and SRT slots) -> m5p/layout_check.json;
  * --baseline compares only the modules present in both files (e.g. A and V1 against session 102's
    m5/recompile.json) and lists the others separately;
  * a per-item summary table is printed at the end.

Outputs (all under C:/kyty/s103/m5p):
  spv/<item>_<hash>[_<cache8>]_p<k>_<arm>.spv   (<cache8> only when an item has several current cache files)
  logs/<module>.stderr.txt                     stderr of every recompile run
  dump/<module>.spv(.ir/.rdna2)                KYTY_RECOMPILE_DUMP runs of A and V2p (V2p with the trace)
  sass/<module>.s16.txt + <module>.sass        python C:/kyty/scripts/s16_sass.py <spv> <sass> [--ps] --stats
  sass/<module>.full.sass                      the whole FS/CS code (m5_sass_full.full_disasm)
  recompile.json                               every command, env, stdout line, md5/sha256, bda-rewrite counts,
                                               spirv-val, dump cross-checks, cache manifest check
  regs.json                                    Register Count, Local Memory Size, Binary Size, SASS counts, LDG variants
  layout_check.json                            the V2p layout check
Usage: python C:/kyty/s103/m5p_recompile.py [--no-sass] [--no-s16] [--baseline <old recompile.json>] [--overwrite]
  (refuses to rebuild over an existing m5p/recompile.json without --overwrite: a plan pins it by sha256)
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m5_sass_full  # noqa: E402  (the whole-code disassembly, unchanged from session 102)
import m5_spv_loads  # noqa: E402  (SPIR-V load census: grouped alias views, load widths)
import m5_layout_check  # noqa: E402  (bindings / user-data / SRT-slot readers, unchanged from session 102)
import m5p_103  # noqa: E402  (the seals and the sealed inputs)

ROOT = 'C:/kyty/s103'
OUT = ROOT + '/m5p'
PRED = m5p_103.PRED                      # the M5' seal: recorded and checked
ITEMS_SOURCE = m5p_103.PARENT01          # the sealed item table (102 pred/01 s2), inherited unchanged
EMU = 'C:/Users/<user>/OneDrive/Desktop/ps5 em'
GCN_DIR = EMU + '/_Shaders/gcn'
CACHE_DIR = m5p_103.SNAPSHOT_DIR
MANIFEST = m5p_103.SNAPSHOT_MANIFEST
SIGNATURE = m5p_103.SIGNATURE_PREFIX.encode('ascii')
EXE = m5p_103.EXE
EXE_SHA = m5p_103.EXE_SHA
BUILD = 'C:/kyty/build'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
VAL_ARGS = list(m5p_103.VF_DECIDING)     # the deciding V-f command (102 pred/02 s1)
S16 = 'C:/kyty/scripts/s16_sass.py'
ARMS = [('A', {}), ('V1', {'KYTY_RECOMPILE_CBANK': '0'}),
        ('V2p', {'KYTY_RECOMPILE_BDA': '1', 'KYTY_BDA_LEAN': '1'})]
DUMP_ARMS = ('A', 'V2p')
LOAD_OPS = ('ReadConstBuffer', 'LoadBufferU8', 'LoadBufferU16', 'LoadBufferU32', 'LoadBufferU32x2',
            'LoadBufferU32x3', 'LoadBufferU32x4')


def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


def parse_items():
    text = open(ITEMS_SOURCE, encoding='utf-8').read()
    items = []
    for m in re.finditer(r'^\| (S\d+) \| (CS|PS) \| `([0-9a-f]{16})` \| ([^|]+)\|', text, re.M):
        items.append({'item': m.group(1), 'stage': m.group(2).lower(), 'hash': m.group(3),
                      'us_per_frame': m.group(4).strip()})
    assert len(items) == 10, items
    assert [i['item'] for i in items] == list(m5p_103.WEIGHTS), items
    return items


def cache_files(stage, h):
    found = []
    for path in sorted(glob.glob(f'{CACHE_DIR}/{stage}_{h}_*.bin')):
        head = open(path, 'rb').read(512)
        pos = head.find(b'KytySC')
        sig = head[pos:pos + 64].split(b'\0')[0].split(b'\n')[0] if pos >= 0 else b''
        found.append((path.replace('\\', '/'), sig.decode('ascii', 'replace'), sig.startswith(SIGNATURE)))
    return found


def clean_env(extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update(extra)
    return env


def recompile(gcn, cache, out, perm, arm_env, stderr_path, dump=False, trace=False):
    extra = dict(arm_env)
    extra['KYTY_RECOMPILE'] = f'{gcn};{cache};{out};{perm}'
    if dump:
        extra['KYTY_RECOMPILE_DUMP'] = '1'
    if trace:
        extra['KYTY_RECOMPILE_BDA_TRACE'] = '1'
    t0 = time.time()
    r = subprocess.run([EXE], cwd=BUILD, env=clean_env(extra), capture_output=True, text=True,
                       errors='replace')
    open(stderr_path, 'w', encoding='utf-8').write(r.stderr)
    lines = r.stdout.splitlines()
    rec = {'cmd': [EXE], 'cwd': BUILD, 'env': extra, 'rc': r.returncode, 'seconds': round(time.time() - t0, 3),
           'stdout': lines, 'stderr_file': stderr_path, 'stderr_bytes': len(r.stderr)}
    for line in lines:
        m = re.search(r'permutations=(\d+)', line)
        if line.startswith('recompile ') and m:
            rec['permutations'] = int(m.group(1))
            w = re.search(r'spirv=(\d+) words \(cached (\d+)\)', line)
            if w:
                rec['words'], rec['cached_words'] = int(w.group(1)), int(w.group(2))
            b = re.search(r'buffer_align=\[([^\]]*)\]', line)
            if b:
                rec['buffer_align'] = b.group(1)
        if line.startswith('recompile-identity:'):
            rec['identity'] = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', line)}
        if line.startswith('bda-rewrite:'):
            rec['bda_rewrite'] = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', line)}
        if line.startswith('bda-rewrite-detail:'):
            d = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)\b(?!->)', line)}
            u = re.search(r'uses_dma=(\d)->(\d)', line)
            if u:
                d['uses_dma_before'], d['uses_dma_after'] = int(u.group(1)), int(u.group(2))
            d.pop('uses_dma', None)
            rec['bda_rewrite_detail'] = d
    if os.path.exists(out):
        rec['spv'] = out
        rec['md5'] = md5(out)
        rec['sha256'] = sha256(out)
        rec['bytes'] = os.path.getsize(out)
    return rec


def spirv_val(spv):
    r = subprocess.run([SPIRV_VAL] + VAL_ARGS + [spv], capture_output=True, text=True, errors='replace')
    return {'cmd': [SPIRV_VAL] + VAL_ARGS + [spv], 'rc': r.returncode,
            'output': (r.stdout + r.stderr).strip()[:4000], 'pass': r.returncode == 0}


def ir_counts(ir_path):
    text = open(ir_path, encoding='utf-8', errors='replace').read()
    ir = text.split('\nIR:\n', 1)[-1]
    counts = {}
    for op in LOAD_OPS + ('LoadAddressU32', 'GetAddressResource', 'GetBufferResource', 'ReferenceU32'):
        counts[op] = len(re.findall(r'(?:= |\s{10})' + op + r'\b', ir))
    return counts


def opcode_counts(sass_text):
    ops = {}
    n = 0
    for line in sass_text.splitlines():
        m = re.match(r'\s*/\*[0-9a-f]+\*/\s+(.*?)\s*;', line)
        if not m:
            continue
        n += 1
        t = re.sub(r'^@!?U?P\w+\s+', '', m.group(1))
        op = t.split()[0].split('.')[0] if t.split() else ''
        ops[op] = ops.get(op, 0) + 1
    keys = ['LDG', 'LDC', 'LDCU', 'ULDC', 'LDS', 'LD', 'STL', 'LDL', 'ISETP', 'BRA', 'TEX', 'EXIT']
    return n, {k: ops.get(k, 0) for k in keys}, ops


def s16(spv, pixel, base):
    out = base + '.sass'
    cmd = [sys.executable, S16, spv, out] + (['--ps'] if pixel else []) + ['--stats']
    r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    text = r.stdout + r.stderr
    open(base + '.s16.txt', 'w', encoding='utf-8').write(text)
    res = {'cmd': cmd, 'rc': r.returncode, 'log': base + '.s16.txt'}
    wanted = 'FS' if pixel else 'CS'
    for m in re.finditer(r'exec \d+ "(\w+)"[^:]*:(.*)', text):
        if m.group(1) == wanted:
            res['stats'] = {k.strip(): int(v) for k, v in re.findall(r'([A-Za-z ]+?)=(\d+)', m.group(2))}
    m = re.search(r'sass: start=0x([0-9a-f]+) size=(\d+) -> .* \((\d+) instructions\)', text)
    if m:
        res.update({'start': int(m.group(1), 16), 'size': int(m.group(2)), 'instructions': int(m.group(3))})
    if os.path.exists(out):
        n, keys, _ = opcode_counts(open(out, encoding='utf-8', errors='replace').read())
        res['ops'] = keys
    return res


def ldg_variants(mem):
    """Every LDG opcode with its full suffix (from m5_sass_full.memory_op_widths 'ops_full')."""
    full = (mem or {}).get('ops_full') or {}
    return dict(sorted((k, v) for k, v in full.items() if k.split('.')[0] == 'LDG'))


def layout_row(a, v):
    """The V2 rule of m5_layout_check.py applied to an A/V2p pair (reported only)."""
    group = 1 if v['stage'] == 'ps' else 0
    expected_new = {46 + 51 * group, 47 + 51 * group}
    ta, tv = m5_layout_check.disassemble(a['spv']), m5_layout_check.disassemble(v['spv'])
    ba, pa = m5_layout_check.bindings(a['spv'], ta)
    bv, pv = m5_layout_check.bindings(v['spv'], tv)
    ua, sa = m5_layout_check.ir_sets(a['dump']['ir'])
    uv, sv = m5_layout_check.ir_sets(v['dump']['ir'])
    added = sorted(set(bv) - set(ba))
    removed = sorted(set(ba) - set(bv))
    row = {'module': v['name'], 'arm': v['arm'], 'bindings_A': {str(k): n for k, n in sorted(ba.items())},
           'added': {str(k): bv[k] for k in added}, 'removed': removed,
           'added_is_pagetable_and_fault': not removed and (
               set(added) == expected_new or (not added and expected_new <= set(ba))),
           'pagetable_and_fault_in_A': expected_new <= set(ba),
           'push_constant_blocks': [pa, pv], 'user_data_A': ua, 'user_data_V2p': uv,
           'user_data_equal': ua == uv, 'srt_slots_equal': sa == sv,
           'srt_slots_A': len(sa), 'srt_slots_V2p': len(sv)}
    row['ok'] = row['added_is_pagetable_and_fault'] and row['user_data_equal'] and row['srt_slots_equal']
    return row


def main():
    do_sass = '--no-sass' not in sys.argv
    do_s16 = '--no-s16' not in sys.argv
    if not m5p_103.seals_ok():
        raise SystemExit('a sealed text changed (m5p_103.SEALS): refusing to build')
    exe_sha = sha256(EXE)
    if exe_sha != EXE_SHA:
        raise SystemExit('%s sha256 %s != sealed %s: refusing to build' % (EXE, exe_sha, EXE_SHA))
    for sub in ('spv', 'logs', 'dump', 'sass'):
        os.makedirs(f'{OUT}/{sub}', exist_ok=True)
    if os.path.exists(f'{OUT}/recompile.json') and '--overwrite' not in sys.argv:
        raise SystemExit('%s/recompile.json exists: a plan may pin it by sha256; keep it (e.g. as --baseline) '
                         'and pass --overwrite to rebuild in place' % OUT)
    manifest = json.load(open(MANIFEST, encoding='utf-8'))
    items = parse_items()
    report = {'script': os.path.abspath(__file__), 'script_sha256': sha256(__file__),
              'started': time.strftime('%Y-%m-%d %H:%M:%S'),
              'pred': PRED, 'pred_sha256': sha256(PRED), 'items_source': ITEMS_SOURCE,
              'items_source_sha256': sha256(ITEMS_SOURCE),
              'seals': m5p_103.seal_hashes(),
              'exe': EXE, 'exe_sha256': exe_sha, 'cache_dir': CACHE_DIR, 'signature': SIGNATURE.decode('ascii'),
              'manifest': MANIFEST, 'manifest_sha256': sha256(MANIFEST),
              'spirv_val': SPIRV_VAL, 'val_args': VAL_ARGS, 'arms': {a: e for a, e in ARMS}, 'items': []}
    modules = []
    manifest_bad = []
    for item in items:
        gcn = f"{GCN_DIR}/{item['stage']}_{item['hash']}.bin"
        entry = dict(item)
        entry['gcn'] = gcn
        entry['gcn_md5'] = md5(gcn) if os.path.exists(gcn) else None
        entry['gcn_sha256'] = sha256(gcn) if os.path.exists(gcn) else None
        caches = cache_files(item['stage'], item['hash'])
        entry['cache_candidates'] = [{'path': p, 'signature': s, 'current': ok} for p, s, ok in caches]
        current = [p for p, s, ok in caches if ok]
        entry['caches'] = []
        for cache in current:
            cache_id = os.path.basename(cache)[len(item['stage']) + 1 + 16 + 1:-4]
            tag = f"{item['item']}_{item['hash']}" + (f'_{cache_id[:8]}' if len(current) > 1 else '')
            cache_sha = sha256(cache)
            in_manifest = manifest.get(os.path.basename(cache)) == cache_sha
            if not in_manifest:
                manifest_bad.append(os.path.basename(cache))
            probe = recompile(gcn, cache, f'{OUT}/spv/{tag}_p0_A.spv', 0, {}, f'{OUT}/logs/{tag}_p0_A.stderr.txt')
            count = probe.get('permutations', 0)
            centry = {'cache': cache, 'cache_id': cache_id, 'cache_sha256': cache_sha,
                      'cache_in_manifest': in_manifest, 'tag': tag, 'permutations': count, 'modules': []}
            for perm in range(count):
                for arm, arm_env in ARMS:
                    name = f'{tag}_p{perm}_{arm}'
                    rec = probe if (perm == 0 and arm == 'A') else recompile(
                        gcn, cache, f'{OUT}/spv/{name}.spv', perm, arm_env, f'{OUT}/logs/{name}.stderr.txt')
                    rec.update({'name': name, 'item': item['item'], 'stage': item['stage'], 'hash': item['hash'],
                                'cache_id': cache_id, 'perm': perm, 'arm': arm})
                    if 'spv' in rec:
                        rec['spirv_val'] = spirv_val(rec['spv'])
                        rec['spv_loads'] = m5_spv_loads.spv_loads(rec['spv'])
                    if arm in DUMP_ARMS:
                        # Dump runs: must emit the same bytes as the canonical module.
                        dump_spv = f'{OUT}/dump/{name}.spv'
                        drec = recompile(gcn, cache, dump_spv, perm, arm_env, f'{OUT}/logs/{name}.dump.stderr.txt',
                                         dump=True, trace=(arm == 'V2p'))
                        rec['dump'] = {'spv': dump_spv, 'rc': drec['rc'], 'md5': drec.get('md5'),
                                       'same_bytes': drec.get('md5') == rec.get('md5'),
                                       'ir': dump_spv + '.ir', 'trace': f'{OUT}/logs/{name}.dump.stderr.txt'}
                        if os.path.exists(dump_spv + '.ir'):
                            rec['dump']['ir_counts'] = ir_counts(dump_spv + '.ir')
                    centry['modules'].append(rec)
                    modules.append(rec)
                    print(f"{name}: rc={rec['rc']} words={rec.get('words')} md5={rec.get('md5')} "
                          f"identical_to_stored={rec.get('identity', {}).get('identical')} "
                          f"val={'ok' if rec.get('spirv_val', {}).get('pass') else 'FAIL'} "
                          f"{rec.get('bda_rewrite', '')}", flush=True)
            entry['caches'].append(centry)
        report['items'].append(entry)
    report['manifest_mismatch'] = manifest_bad

    # Cross-check (the V2 rule of session 102; the IR rewrite of V2p is V2's, only the emitter differs):
    # A-to-V2p load counts from the IR dumps against the rewrite counters.
    checks = []
    by_name = {m['name']: m for m in modules}
    for m in modules:
        if m['arm'] != 'V2p':
            continue
        a = by_name.get(m['name'][:-3] + 'A')
        if a is None or 'dump' not in a or 'dump' not in m or 'ir_counts' not in a['dump'] or 'ir_counts' not in m['dump']:
            continue
        ca, cv = a['dump']['ir_counts'], m['dump']['ir_counts']
        bda = m.get('bda_rewrite', {})
        det = m.get('bda_rewrite_detail', {})
        loads_a = sum(ca[op] for op in LOAD_OPS)
        loads_v = sum(cv[op] for op in LOAD_OPS)
        converted = bda.get('converted_const', 0) + bda.get('converted_buffer', 0)
        kept = sum(bda.get(k, 0) for k in ('kept_written', 'kept_atomic', 'kept_formatted', 'kept_other'))
        checks.append({
            'module': m['name'], 'loads_A': loads_a, 'loads_V2p': loads_v, 'converted': converted,
            'kept': kept, 'planning_only': det.get('planning_only', 0), 'dead': det.get('dead', 0),
            'new_LoadAddressU32': cv['LoadAddressU32'] - ca['LoadAddressU32'], 'dwords': det.get('dwords', 0),
            'converted_equals_removed': loads_a - loads_v == converted,
            'remaining_equals_kept_plus_planning': loads_v == kept + det.get('planning_only', 0),
            'dwords_equal_new_loads': cv['LoadAddressU32'] - ca['LoadAddressU32'] == det.get('dwords', 0),
            'remaining_eligible_zero': det.get('remaining_eligible', -1) == 0,
            'uses_dma_after': det.get('uses_dma_after'),
            'ir_counts_A': ca, 'ir_counts_V2p': cv})
    report['dump_crosscheck'] = checks

    layout = []
    for m in modules:
        if m['arm'] != 'V2p' or 'spv' not in m:
            continue
        a = by_name.get(m['name'][:-3] + 'A')
        if a is None or 'spv' not in a or 'dump' not in a or 'dump' not in m:
            continue
        try:
            row = layout_row(a, m)
        except (OSError, KeyError) as error:
            row = {'module': m['name'], 'arm': 'V2p', 'ok': False, 'error': str(error)}
        layout.append(row)
        print(f"layout {m['name']}: added={row.get('added')} removed={row.get('removed')} ok={row['ok']}", flush=True)
    json.dump(layout, open(f'{OUT}/layout_check.json', 'w', encoding='utf-8'), indent=1)

    regs = []
    if do_sass:
        for m in modules:
            if 'spv' not in m:
                continue
            base = f"{OUT}/sass/{m['name']}"
            pixel = m['stage'] == 'ps'
            s = s16(m['spv'], pixel, base) if do_s16 else {}
            f = m5_sass_full.full_disasm(m['spv'], pixel, base)
            st = f.get('stats') or s.get('stats') or {}
            lms = st.get('Local Memory Size')
            row = {'module': m['name'], 'item': m['item'], 'stage': m['stage'], 'hash': m['hash'],
                   'cache_id': m['cache_id'], 'perm': m['perm'], 'arm': m['arm'], 'md5': m.get('md5'),
                   'register_count': st.get('Register Count'), 'binary_size': st.get('Binary Size'),
                   'stack_size': st.get('Stack Size'),
                   'local_memory_size_raw': lms,
                   'local_memory_bytes': (lms & 0xffffffff) if isinstance(lms, int) else None,
                   's16_rc': s.get('rc'), 's16_window': [s.get('start'), s.get('size')],
                   's16_instructions': s.get('instructions'), 's16_ops': s.get('ops'),
                   'full_window': [f.get('start'), f.get('size')], 'full_method': f.get('method'),
                   'full_instructions': f.get('instructions'),
                   'full_ops': f.get('ops'), 'full_error': f.get('error'),
                   's16_log': s.get('log'), 'full_sass': f.get('sass'),
                   'full_frame': f.get('frame'), 'full_instructions_raw': f.get('instructions_raw'),
                   'full_binary_size': (f.get('stats') or {}).get('Binary Size'),
                   'full_register_count': (f.get('stats') or {}).get('Register Count'),
                   'full_mem': f.get('mem'),
                   'ldg_variants': ldg_variants(f.get('mem')),
                   'stl': (f.get('ops') or {}).get('STL'), 'ldl': (f.get('ops') or {}).get('LDL')}
            regs.append(row)
            print(f"{m['name']}: R={row['register_count']} bin={row['binary_size']} lmem={row['local_memory_bytes']} "
                  f"sass(full)={row['full_instructions']} STL={row['stl']} LDG={row['ldg_variants']}", flush=True)
        json.dump({'note': "REPORTED numbers, never deciding (new s4). local_memory_bytes = low dword of pipestat "
                           "Local Memory Size. full_* = m5_sass_full.py: the whole CS/FS code (all zstd frames, the "
                           "longest clean prefix of Binary Size; full_instructions excludes the trailing NOP/BRA "
                           "padding). ldg_variants = every LDG opcode with its full suffix from the whole code. "
                           "s16_* = scripts/s16_sass.py (first zstd frame only).",
                   'rows': regs}, open(f'{OUT}/regs.json', 'w', encoding='utf-8'), indent=1)
    if '--baseline' in sys.argv:
        path = sys.argv[sys.argv.index('--baseline') + 1]
        old = json.load(open(path, encoding='utf-8'))
        compared = []
        not_built_now = []
        for item in old['items']:
            for cache in item['caches']:
                for om in cache['modules']:
                    nm = by_name.get(om['name'])
                    if nm is None:
                        not_built_now.append(om['name'])
                        continue
                    compared.append({'module': om['name'], 'arm': om['arm'], 'md5_before': om.get('md5'),
                                     'md5_now': nm.get('md5'), 'same': nm.get('md5') == om.get('md5')})
        report['baseline'] = {'file': path, 'file_sha256': sha256(path), 'exe_before': old.get('exe_sha256'),
                              'modules': compared, 'not_built_now': not_built_now,
                              'changed': [c['module'] for c in compared if not c['same']]}
    report['finished'] = time.strftime('%Y-%m-%d %H:%M:%S')
    report['summary'] = {
        'modules': len(modules),
        'rc_nonzero': [m['name'] for m in modules if m['rc'] != 0],
        'spirv_val_fail': [m['name'] for m in modules if not m.get('spirv_val', {}).get('pass')],
        'A_not_identical_to_stored': [m['name'] for m in modules if m['arm'] == 'A' and m.get('identity', {}).get('identical') != 1],
        'A_identical_to_stored': len([m for m in modules if m['arm'] == 'A' and m.get('identity', {}).get('identical') == 1]),
        'A_modules': len([m for m in modules if m['arm'] == 'A']),
        'dump_bytes_differ': [m['name'] for m in modules if 'dump' in m and not m['dump']['same_bytes']],
        'crosscheck_fail': [c['module'] for c in checks if not (c['converted_equals_removed'] and c['remaining_equals_kept_plus_planning'] and c['dwords_equal_new_loads'] and c['remaining_eligible_zero'])],
        'V2p_not_uses_dma': [m['name'] for m in modules if m['arm'] == 'V2p' and m.get('bda_rewrite_detail', {}).get('uses_dma_after') != 1],
        'layout_bad': [r['module'] for r in layout if not r['ok']],
        'manifest_mismatch': manifest_bad,
        'baseline_changed': report.get('baseline', {}).get('changed'),
    }
    json.dump(report, open(f'{OUT}/recompile.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps(report['summary'], indent=1))
    print_table(items, modules, regs)


def print_table(items, modules, regs):
    """Per item: A identical count, deciding spirv-val failures, registers A/V1/V2p, LDG variants."""
    by_mod = {r['module']: r for r in regs}
    print()
    print('item  perms  A identical  V-f fail (A/V1/V2p)  regs A/V1/V2p [lmem A/V1/V2p]')
    for item in items:
        mods = [m for m in modules if m['item'] == item['item']]
        perms = sorted({(m['cache_id'], m['perm']) for m in mods})
        a_ident = len([m for m in mods if m['arm'] == 'A' and m.get('identity', {}).get('identical') == 1])
        fails = '/'.join(str(len([m for m in mods if m['arm'] == arm and not m.get('spirv_val', {}).get('pass')]))
                         for arm, _ in ARMS)
        cells = []
        for cache_id, perm in perms:
            regs_ = []
            lmem = []
            for arm, _ in ARMS:
                m = [x for x in mods if x['cache_id'] == cache_id and x['perm'] == perm and x['arm'] == arm]
                row = by_mod.get(m[0]['name']) if m else None
                regs_.append(str(row.get('register_count')) if row else '-')
                lmem.append(str(row.get('local_memory_bytes')) if row else '-')
            cells.append('%s [%s]' % ('/'.join(regs_), '/'.join(lmem)))
        print('%-4s  %5d  %4d of %-4d  %-19s  %s' % (item['item'], len(perms), a_ident,
                                                     len([m for m in mods if m['arm'] == 'A']), fails, '; '.join(cells)))
    print()
    print('LDG variants per module (full SASS), A vs V2p:')
    for m in modules:
        if m['arm'] != 'V2p':
            continue
        row_v = by_mod.get(m['name'])
        row_a = by_mod.get(m['name'][:-3] + 'A')
        print('  %-40s A: %s' % (m['name'][:-4], (row_a or {}).get('ldg_variants')))
        print('  %-40s V2p: %s  STL %s -> %s' % ('', (row_v or {}).get('ldg_variants'),
                                              (row_a or {}).get('stl'), (row_v or {}).get('stl')))


if __name__ == '__main__':
    main()
