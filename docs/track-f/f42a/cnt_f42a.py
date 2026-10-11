"""F42a (HPP-779, ROADMAP s122 item 694(g)(0), RC1(a) of F41b): how many translated modules carry the fault buffer, read-only.

Inputs (all read-only):
  C:/kyty/f287/f42a/cat_fixf19     - copy of _ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19 (FS12 signature
                                     9177b426..., manifest cat_fixf19.sha256), its pipelines.bin;
  C:/kyty/s288/s7/t1_base.tsv      - the T1 corpus rows (A rows: stage, hash16, key16, perm);
  C:/kyty/f287/f42a/build/shader_cfg_tests.exe (worktree 730ed40a, no F42a commit) - permutation count of a cache
                                     file by the KYTY_RECOMPILE probe 999 (ReadFileUnchecked), the method of recipes_s7.py.
Per module: named = the OpName instruction (the named modules are then walked by spvscan_f42a.scan:
bound_dec, triples, loads) <0x00060005, id, "fault_buffer" + 4 NUL bytes> occurs in the module bytes (fast byte
search; the triple counts come from the C++ corpus run (g)(4)); the module list is checked by a full instruction walk. A module of a program whose
translator layout has the FaultBuffer binding carries the variable "fault_buffer" with a Binding decoration
(spirvEmitterModule.cpp, DescriptorBindingKind::FaultBuffer -> Define(..., "fault_buffer")) - read from the code, the
count below is by the SPIR-V (name + Binding decoration); the count by CompiledShaderInfo is FixF20Stat modules_bound of
the corpus run (g)(4).
Recipes: pipelines.bin of the copy parsed by recipes_s7.parse (format checked against FS12 RecordGraphicsRecipe /
RecordComputeRecipe: kind, StoredKey, index, ...); a recipe counts when any of its stage modules (vs / ps / cs by
file + permutation index) is named.
Output: cnt_f42a.txt (ASCII), cnt_f42a_files.tsv.
"""
import collections
import os
import re
import struct
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/s288/s7')
sys.path.insert(0, 'C:/kyty/f287/f42a')
import recipes_s7  # noqa: E402
import spvscan_f42a as sv  # noqa: E402

CAT = 'C:/kyty/f287/f42a/cat_fixf19'
T1 = 'C:/kyty/s288/s7/t1_base.tsv'
EXE = 'C:/kyty/f287/f42a/build/shader_cfg_tests.exe'
PROBE_DIR = 'C:/kyty/f287/f42a/probe'
SIG = 'KytySC3:9177b426'


def perm_count(path):
    os.makedirs(PROBE_DIR, exist_ok=True)
    dummy = PROBE_DIR + '/empty.bin'
    open(dummy, 'wb').close()
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_RECOMPILE'] = '%s;%s;%s;999' % (dummy, path, PROBE_DIR + '/rcp.spv')
    p = subprocess.run([EXE], env=env, capture_output=True)
    m = re.search(rb'permutation 999 of (\d+)', p.stderr)
    return int(m.group(1)) if m else None


PROBE = os.environ.get('CNT_PROBE') == '1'
NAME_RE = re.compile(rb'\x05\x00\x06\x00....fault_buffer\x00\x00\x00\x00', re.S)


def fast_scan(words):
    raw = struct.pack('<%dI' % len(words), *words)
    named = len(NAME_RE.findall(raw))
    return {'named': named, 'bound_dec': 0, 'triples': 0, 'loads_fb': 0, 'atomics_or': 0, 'returns': 0,
            'words': len(words)}


def main():
    out = []
    files = {}
    tot = collections.Counter()
    by_stage = collections.defaultdict(collections.Counter)
    rows = []
    for name in sorted(os.listdir(CAT)):
        if name == 'pipelines.bin':
            continue
        path = CAT + '/' + name
        data = open(path, 'rb').read()
        sig_ok = data.startswith(SIG.encode())
        mods = sv.modules_in_cache_file(data)
        n_perm = perm_count(path) if PROBE else len(mods)
        scans = [sv.scan(m) if fast_scan(m)['named'] else fast_scan(m) for m in mods]  # full scan of the named modules
        files[name] = scans
        st = name[:2]
        tot['files'] += 1
        tot['sig_ok'] += sig_ok
        tot['perm_count_equal'] += n_perm == len(mods)
        for k, s in enumerate(scans):
            tot['modules'] += 1
            by_stage[st]['modules'] += 1
            named = s['named'] > 0
            tot['named'] += named
            by_stage[st]['named'] += named
            tot['named_and_bound_dec'] += named and s['bound_dec'] > 0
            tot['triples'] += s['triples']
            by_stage[st]['triples'] += s['triples']
            tot['loads_fb'] += s['loads_fb']
            tot['loads_outside_triple'] += s['loads_fb'] - s['triples']
            tot['atomics_or'] += s['atomics_or']
            if named and s['triples'] == 0:
                tot['named_without_triple'] += 1
            rows.append('%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d' % (name, k, s['words'], s['named'], s['bound_dec'],
                                                           s['triples'], s['loads_fb'], s['returns']))
        if n_perm != len(mods):
            out.append('PERM MISMATCH %s probe %s found %d' % (name, n_perm, len(mods)))
    # recipes
    head, recs = recipes_s7.parse(CAT + '/pipelines.bin')
    rc = collections.Counter()
    for r in recs:
        if r['kind'] == 1:
            keys = [(r['vk'], r['vi'])] + ([(r['pk'], r['pi'])] if r['pk'] is not None else [])
        else:
            keys = [(r['ck'], r['ci'])]
        rc['recipes'] += 1
        rc['gfx' if r['kind'] == 1 else 'cs'] += 1
        named = False
        missing = False
        for key, idx in keys:
            fname = recipes_s7.path_name(key)
            sc = files.get(fname)
            if sc is None or idx >= len(sc):
                missing = True
                continue
            named |= sc[idx]['named'] > 0
        rc['with_fault_buffer'] += named
        rc['with_fault_buffer_' + ('gfx' if r['kind'] == 1 else 'cs')] += named
        rc['unresolved'] += missing
    # T1 corpus
    t1 = collections.Counter()
    for line in open(T1, encoding='ascii'):
        f = line.rstrip('\n').split('\t')
        if f[0] != 'A':
            continue
        t1['rows'] += 1
        fname = '%s_%s_%s.bin' % (f[1], f[2], f[3])
        sc = files.get(fname)
        perm = int(f[4])
        if sc is None or perm >= len(sc):
            t1['not_in_catalog'] += 1
            continue
        t1['in_catalog'] += 1
        t1['named'] += sc[perm]['named'] > 0
        t1['triples'] += sc[perm]['triples']
    with open('C:/kyty/f287/f42a/cnt_f42a_files.tsv', 'w', encoding='ascii', newline='\n') as f:
        f.write('file\tperm\twords\tnamed\tbound_dec\ttriples\tloads_fb\treturns\n')
        f.write('\n'.join(rows) + '\n')
    lines = ['catalog copy: files %d signature %s.. %d, perm count probe == modules found %d (probe only with CNT_PROBE=1; the cross-check of this run is SpecDump, specdump_cat.txt)' % (
        tot['files'], SIG, tot['sig_ok'], tot['perm_count_equal'])]
    lines.append('modules %d named(fault_buffer) %d named+Binding %d triples %d loads_fb %d loads_outside_triple %d '
                 'atomic_or_on_fb %d named_without_triple %d' % (
                     tot['modules'], tot['named'], tot['named_and_bound_dec'], tot['triples'], tot['loads_fb'],
                     tot['loads_outside_triple'], tot['atomics_or'], tot['named_without_triple']))
    for st in sorted(by_stage):
        lines.append('  stage %s modules %d named %d triples %d' % (st, by_stage[st]['modules'], by_stage[st]['named'],
                                                                   by_stage[st]['triples']))
    lines.append('recipes %d (gfx %d cs %d) at_end %s signature %s' % (rc['recipes'], rc['gfx'], rc['cs'],
                                                                         head['at_end'], head['signature'][:60]))
    lines.append('recipes with a fault_buffer module %d (gfx %d cs %d) unresolved %d' % (
        rc['with_fault_buffer'], rc['with_fault_buffer_gfx'], rc['with_fault_buffer_cs'], rc['unresolved']))
    lines.append('T1 rows %d in_catalog %d not_in_catalog %d named %d triples %d' % (
        t1['rows'], t1['in_catalog'], t1['not_in_catalog'], t1['named'], t1['triples']))
    lines += out
    text = '\n'.join(lines) + '\n'
    open('C:/kyty/f287/f42a/cnt_f42a.txt', 'w', encoding='ascii', newline='\n').write(text)
    sys.stdout.write(text)


if __name__ == '__main__':
    main()
