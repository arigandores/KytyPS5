"""m5_recompile.py -- session 102, route E, M5 (C:/kyty/s102/pred/01_m5_bench.md): the offline
modules of arms A, V1, V2 and V2s for EVERY permutation of EVERY sealed item (§2), their spirv-val,
their driver statistics and SASS. No game run: shader_cfg_tests.exe (KYTY_RECOMPILE), spirv-val,
pipestat (a real driver compile, no capture), nvdisasm.

  A  : KYTY_RECOMPILE, no switch
  V1 : KYTY_RECOMPILE_CBANK=0
  V2 : KYTY_RECOMPILE_BDA=1 (tests/shaderCfgTests.cpp, RewriteBuffersToBda)
  V2s: KYTY_RECOMPILE_BDA=2 (the same rewrite through the loads' own descriptors: V2's per-dword
       granularity, run-time stride and bounds selects without the page table; layout = A's)

Outputs (all under C:/kyty/s102/m5):
  spv/<item>_<hash>[_<cache8>]_p<k>_<arm>.spv   (<cache8> only when an item has several current cache files)
  logs/<module>.stderr.txt                     stderr of every recompile run
  dump/<module>.spv(.ir/.rdna2)                KYTY_RECOMPILE_DUMP runs of A, V2 and V2s (V2/V2s with the trace)
  sass/<module>.s16.txt + <module>.sass        python C:/kyty/scripts/s16_sass.py <spv> <sass> [--ps] --stats
  sass/<module>.full.sass                      the whole FS/CS code (m5_sass_full.py: every zstd frame,
                                               start..last EXIT inside Binary Size)
  recompile.json                               every command, env, stdout line, md5/sha256, bda-rewrite counts,
                                               spirv-val, dump cross-checks
  regs.json                                    Register Count, Local Memory Size, Binary Size, SASS counts
Usage: python C:/kyty/s102/m5_recompile.py [--no-sass] [--baseline <old recompile.json>]
  --baseline: every module of the old file is compared by md5 with the module of the same name built
  now (recompile.json 'baseline'); used to show that adding V2s left A, V1 and V2 byte-identical.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m5_sass_full  # noqa: E402  (the whole-code disassembly shared with the refresh pass)
import m5_spv_loads  # noqa: E402  (SPIR-V load census: grouped alias views, load widths)

ROOT = 'C:/kyty/s102'
M5 = ROOT + '/m5'
PRED = ROOT + '/pred/01_m5_bench.md'
EMU = 'C:/Users/<user>/OneDrive/Desktop/ps5 em'
GCN_DIR = EMU + '/_Shaders/gcn'
CACHE_DIR = EMU + '/_ShaderCache/PPSA21564'
SIGNATURE = b'KytySC3:2db9065a'
EXE = 'C:/kyty/build/shader_cfg_tests.exe'
BUILD = 'C:/kyty/build'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
# The stand recipe (scripts/s18_recompile.sh, s20_recompile.sh) validates with this flag:
# const-bank modules declare stride-4/8 arrays in uniform blocks.
VAL_ARGS = ['--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout']
S16 = 'C:/kyty/scripts/s16_sass.py'
PIPESTAT = r'C:\kyty\tools\pipestat\pipestat.exe'
NVDISASM = r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin\nvdisasm.exe'
SM = 'SM120'
ARMS = [('A', {}), ('V1', {'KYTY_RECOMPILE_CBANK': '0'}), ('V2', {'KYTY_RECOMPILE_BDA': '1'}),
        ('V2s', {'KYTY_RECOMPILE_BDA': '2'})]
DUMP_ARMS = ('A', 'V2', 'V2s')
# Items whose A/V2 IR is dumped for the side-by-side of item 5 (all items are dumped for the
# count cross-check; these are only the ones the report quotes).
LOAD_OPS = ('ReadConstBuffer', 'LoadBufferU8', 'LoadBufferU16', 'LoadBufferU32', 'LoadBufferU32x2',
            'LoadBufferU32x3', 'LoadBufferU32x4')


def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


def parse_items():
    text = open(PRED, encoding='utf-8').read()
    items = []
    for m in re.finditer(r'^\| (S\d+) \| (CS|PS) \| `([0-9a-f]{16})` \| ([^|]+)\|', text, re.M):
        items.append({'item': m.group(1), 'stage': m.group(2).lower(), 'hash': m.group(3),
                      'us_per_frame': m.group(4).strip()})
    assert len(items) == 10, items
    return items


def cache_files(stage, h):
    found = []
    for path in sorted(glob.glob(f'{CACHE_DIR}/{stage}_{h}_*.bin')):
        head = open(path, 'rb').read(512)
        pos = head.find(b'KytySC')
        sig = head[pos:pos + 64].split(b'\0')[0] if pos >= 0 else b''
        found.append((path, sig.decode('ascii', 'replace'), sig.startswith(SIGNATURE)))
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


def main():
    do_sass = '--no-sass' not in sys.argv
    for sub in ('spv', 'logs', 'dump', 'sass'):
        os.makedirs(f'{M5}/{sub}', exist_ok=True)
    items = parse_items()
    report = {'script': os.path.abspath(__file__), 'script_sha256': sha256(__file__), 'started': time.strftime('%Y-%m-%d %H:%M:%S'),
              'pred': PRED, 'pred_sha256': sha256(PRED), 'exe': EXE, 'exe_sha256': sha256(EXE),
              'spirv_val': SPIRV_VAL, 'val_args': VAL_ARGS, 'arms': {a: e for a, e in ARMS}, 'items': []}
    modules = []
    for item in items:
        gcn = f"{GCN_DIR}/{item['stage']}_{item['hash']}.bin"
        entry = dict(item)
        entry['gcn'] = gcn
        entry['gcn_md5'] = md5(gcn) if os.path.exists(gcn) else None
        caches = cache_files(item['stage'], item['hash'])
        entry['cache_candidates'] = [{'path': p, 'signature': s, 'current': ok} for p, s, ok in caches]
        current = [p for p, s, ok in caches if ok]
        entry['caches'] = []
        for cache in current:
            cache_id = os.path.basename(cache)[len(item['stage']) + 1 + 16 + 1:-4]
            tag = f"{item['item']}_{item['hash']}" + (f'_{cache_id[:8]}' if len(current) > 1 else '')
            probe = recompile(gcn, cache, f'{M5}/spv/{tag}_p0_A.spv', 0, {}, f'{M5}/logs/{tag}_p0_A.stderr.txt')
            count = probe.get('permutations', 0)
            centry = {'cache': cache, 'cache_id': cache_id, 'cache_sha256': sha256(cache), 'tag': tag,
                      'permutations': count, 'modules': []}
            for perm in range(count):
                for arm, arm_env in ARMS:
                    name = f'{tag}_p{perm}_{arm}'
                    rec = probe if (perm == 0 and arm == 'A') else recompile(
                        gcn, cache, f'{M5}/spv/{name}.spv', perm, arm_env, f'{M5}/logs/{name}.stderr.txt')
                    rec.update({'name': name, 'item': item['item'], 'stage': item['stage'], 'hash': item['hash'],
                                'cache_id': cache_id, 'perm': perm, 'arm': arm})
                    if 'spv' in rec:
                        rec['spirv_val'] = spirv_val(rec['spv'])
                        rec['spv_loads'] = m5_spv_loads.spv_loads(rec['spv'])
                    if arm in DUMP_ARMS:
                        # Dump runs: must emit the same bytes as the canonical module.
                        dump_spv = f'{M5}/dump/{name}.spv'
                        drec = recompile(gcn, cache, dump_spv, perm, arm_env, f'{M5}/logs/{name}.dump.stderr.txt',
                                         dump=True, trace=(arm in ('V2', 'V2s')))
                        rec['dump'] = {'spv': dump_spv, 'rc': drec['rc'], 'md5': drec.get('md5'),
                                       'same_bytes': drec.get('md5') == rec.get('md5'),
                                       'ir': dump_spv + '.ir', 'trace': f'{M5}/logs/{name}.dump.stderr.txt'}
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

    # Item 5 cross-check: A-to-V2 load counts from the IR dumps against the rewrite counters.
    checks = []
    by_name = {m['name']: m for m in modules}
    for m in modules:
        if m['arm'] != 'V2':
            continue
        a = by_name.get(m['name'][:-2] + 'A')
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
            'module': m['name'], 'loads_A': loads_a, 'loads_V2': loads_v, 'converted': converted,
            'kept': kept, 'planning_only': det.get('planning_only', 0), 'dead': det.get('dead', 0),
            'new_LoadAddressU32': cv['LoadAddressU32'] - ca['LoadAddressU32'], 'dwords': det.get('dwords', 0),
            'converted_equals_removed': loads_a - loads_v == converted,
            'remaining_equals_kept_plus_planning': loads_v == kept + det.get('planning_only', 0),
            'dwords_equal_new_loads': cv['LoadAddressU32'] - ca['LoadAddressU32'] == det.get('dwords', 0),
            'remaining_eligible_zero': det.get('remaining_eligible', -1) == 0,
            'ir_counts_A': ca, 'ir_counts_V2': cv})
    # V2s: every converted load is replaced by its dwords on the SAME descriptor path, so the descriptor
    # loads grow by (dwords - converted), and no LoadAddressU32 / GetAddressResource appears.
    for m in modules:
        if m['arm'] != 'V2s':
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
        checks.append({
            'module': m['name'], 'mode': bda.get('mode'), 'loads_A': loads_a, 'loads_V2s': loads_v,
            'converted': converted, 'dwords': det.get('dwords', 0),
            'converted_equals_removed': loads_v - loads_a == det.get('dwords', 0) - converted,
            'remaining_equals_kept_plus_planning': ca['ReadConstBuffer'] == cv['ReadConstBuffer'],
            'dwords_equal_new_loads': (cv['LoadAddressU32'] == ca['LoadAddressU32'] and
                                       cv['GetAddressResource'] == ca['GetAddressResource']),
            'remaining_eligible_zero': det.get('remaining_eligible', -1) == 0,
            'uses_dma_unchanged': det.get('uses_dma_before') == det.get('uses_dma_after'),
            'mode_is_2': bda.get('mode') == 2,
            'reference_u32_added': cv['ReferenceU32'] - ca['ReferenceU32'],
            'reference_u32_expected': 4 * det.get('address_handles', 0),
            'note': 'V2s semantics of the keys: converted_equals_removed = descriptor loads grew by '
                    'dwords - converted; remaining_equals_kept_plus_planning = ReadConstBuffer count unchanged '
                    '(1:1); dwords_equal_new_loads = no new LoadAddressU32/GetAddressResource',
            'ir_counts_A': ca, 'ir_counts_V2s': cv})
    report['dump_crosscheck'] = checks

    regs = []
    if do_sass:
        for m in modules:
            if 'spv' not in m:
                continue
            base = f"{M5}/sass/{m['name']}"
            pixel = m['stage'] == 'ps'
            s = s16(m['spv'], pixel, base)
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
                   'full_mem': f.get('mem')}
            regs.append(row)
            print(f"{m['name']}: R={row['register_count']} bin={row['binary_size']} lmem={row['local_memory_bytes']} "
                  f"sass(s16)={row['s16_instructions']} sass(full)={row['full_instructions']} "
                  f"LDG={(row['full_ops'] or {}).get('LDG')} LDC={(row['full_ops'] or {}).get('LDC')} "
                  f"LDCU={(row['full_ops'] or {}).get('LDCU')} STL={(row['full_ops'] or {}).get('STL')} "
                  f"LDL={(row['full_ops'] or {}).get('LDL')}", flush=True)
        json.dump({'note': 'REPORTED numbers, not decisions (pred/01 §6). local_memory_bytes = low dword of '
                           'pipestat Local Memory Size. full_* = m5_sass_full.py: the whole CS/FS code (all zstd '
                           'frames, the longest clean prefix of Binary Size; full_instructions excludes the '
                           'trailing NOP/BRA padding, full_instructions_raw includes it); s16_* = '
                           'scripts/s16_sass.py (first zstd frame only; its PS window ends at the first '
                           'unconditional EXIT). full_mem = memory opcodes with their width suffix; '
                           'const_bank_split: cx[] = indexed constant bank (uniform-buffer descriptor load), '
                           'c[] = fixed bank.',
                   'rows': regs}, open(f'{M5}/regs.json', 'w', encoding='utf-8'), indent=1)
    if '--baseline' in sys.argv:
        path = sys.argv[sys.argv.index('--baseline') + 1]
        old = json.load(open(path, encoding='utf-8'))
        compared = []
        for item in old['items']:
            for cache in item['caches']:
                for om in cache['modules']:
                    nm = by_name.get(om['name'])
                    compared.append({'module': om['name'], 'arm': om['arm'], 'md5_before': om.get('md5'),
                                     'md5_now': nm.get('md5') if nm else None,
                                     'same': nm is not None and nm.get('md5') == om.get('md5')})
        report['baseline'] = {'file': path, 'file_sha256': sha256(path), 'exe_before': old.get('exe_sha256'),
                              'modules': compared,
                              'changed': [c['module'] for c in compared if not c['same']]}
    report['finished'] = time.strftime('%Y-%m-%d %H:%M:%S')
    report['summary'] = {
        'modules': len(modules),
        'rc_nonzero': [m['name'] for m in modules if m['rc'] != 0],
        'spirv_val_fail': [m['name'] for m in modules if not m.get('spirv_val', {}).get('pass')],
        'A_not_identical_to_stored': [m['name'] for m in modules if m['arm'] == 'A' and m.get('identity', {}).get('identical') != 1],
        'dump_bytes_differ': [m['name'] for m in modules if 'dump' in m and not m['dump']['same_bytes']],
        'crosscheck_fail': [c['module'] for c in checks if not (c['converted_equals_removed'] and c['remaining_equals_kept_plus_planning'] and c['dwords_equal_new_loads'] and c['remaining_eligible_zero'] and c.get('uses_dma_unchanged', True) and c.get('mode_is_2', True) and c.get('reference_u32_added', 0) == c.get('reference_u32_expected', 0))],
        'V2s_grouped_alias_chains': {m['name']: m.get('spv_loads', {}).get('grouped_alias_chains')
                                     for m in modules if m['arm'] == 'V2s'},
        'baseline_changed': report.get('baseline', {}).get('changed'),
    }
    json.dump(report, open(f'{M5}/recompile.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps(report['summary'], indent=1))


if __name__ == '__main__':
    main()
