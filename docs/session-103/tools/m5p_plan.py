"""Session 103, M5': the bench plan, from the capture's module listing and the offline recompile.

    python C:/kyty/s103/m5p_plan.py --find <rd_m5_find.json> --recompile <m5p/recompile.json> \
        --out <plan.json> [--cache-dir C:/kyty/cache_snap/PPSA21564_2db9065a] \
        [--signature-prefix KytySC3:2db9065a] [--regs m5p/regs.json] [--layout m5p/layout_check.json]

Derived from m5_plan.py (session 102) by copying and minimal editing.  Sealed protocol:
C:/kyty/s103/pred/02_m5p_bench.md (sha256 4035a9b0..., decisive) with its session-102 parents
prev102/pred/01_m5_bench.md (cf3c353f...) and prev102/pred/02_m5_addendum.md (ced6d410...); all three
are verified before planning (m5p_103.SEALS).  This tool implements 102 pred/01 s2 (the ten items,
by hash, with their weights), new s2 (arms B / A / V1 / V2p), the identity rule V-c of 102 pred/01 s6,
"present" of 102 pred/02 s5 and the V-f command of 102 pred/02 s1:

  * A captured module BELONGS to an item when md5(refl.rawBytes) equals the md5 of arm A of one
    permutation of that item (recompile.json).  That is the ONLY link that includes a module.
  * EXCLUSIONS are found through the translation cache: every permutation's SPIR-V is stored in
    <cache dir>/<stage>_<hash>_<state>.bin behind a word-count prefix, so md5(cached SPIR-V) names the
    GCN hash of a captured module.  The default cache dir is the SNAPSHOT
    C:/kyty/cache_snap/PPSA21564_2db9065a (new s2): the live _ShaderCache has since been overwritten by
    another translator.  A captured module whose md5 is a cached permutation of item i, but which no
    arm-A permutation reproduces, is EXCLUDED (its events listed, timed, put into the V-c share, never
    summed).  The cache link can only exclude, never include.  'recompiled' says whether the cache
    permutation was built by m5p_recompile.py at all.
  * PRESENT (V-a, V-b, the V-c denominator) = at least one captured module linked to the item's hash
    by either link; INCLUDED (replaced, summed, compared) = linked by arm A's md5.
  * FALLBACK REPORT (never deciding, never including): see fallback_report.

recompile.json is read in the format m5p_recompile.py writes (items[] -> caches[] -> modules[] with
arm A / V1 / V2p and perm).  regs.json (register count, local memory, binary size, SASS counts, LDG
variants) and layout_check.json are merged into the arm entries by module name - REPORTED ONLY.

The plan carries arms B / A / V1 / V2p with one replacement per included captured module, the events of
every included and every excluded module, the spirv-val result of every module of every arm ('ubsl' =
the deciding command, 'pred01' = 102 pred/01's original command, reported only), the three seal
hashes, and the recompile inputs (test recompiler sha256, cache dir, signature) that the scorer checks
against new s2.

Differences from m5_plan.py: arms A/V1/V2p instead of A/V1/V2/V2s; three seals; default --cache-dir =
the snapshot, default --recompile/--regs/--layout under m5p/; the plan records recompile_exe_sha256,
recompile_cache_dir, recompile_signature, recompile_pred_sha256 and parent seal hashes; regs field
'ldg_variants' merged.
--mechanics lets items outside the sealed table through (weight 0) for the mechanics test only.
The output is never overwritten.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m5p_103  # noqa: E402  (the seal constants and the V-f command live in the scorer)

PRED = m5p_103.PRED
PRED_SHA = m5p_103.PRED_SHA
PARENT01 = m5p_103.PARENT01
PARENT01_SHA = m5p_103.PARENT01_SHA
PARENT02 = m5p_103.PARENT02
PARENT02_SHA = m5p_103.PARENT02_SHA
# 102 pred/01_m5_bench.md section 2, verbatim: item, stage, hash, us/frame (gpt72a).  Unchanged by new s2.
ITEMS = (('S1', 'cs', '56a15431999c5a2d', 1009.1),
         ('S2', 'ps', '746c68bba46b2b49', 493.0),
         ('S3', 'ps', '3d705c1b57adec00', 473.2),
         ('S4', 'ps', '2e2ae33a4d374e8f', 428.9),
         ('S5', 'ps', 'b96c2898f05637df', 373.9),
         ('S6', 'cs', '173677e49330bd65', 373.5),
         ('S7', 'cs', '3276e23cce1be33c', 361.4),
         ('S8', 'ps', '7a46be05e11e081b', 359.1),
         ('S9', 'ps', 'ca11de665702d6d9', 349.9),
         ('S10', 'ps', 'c924afb0821b68c8', 286.0))
ARMS = ('A', 'V1', 'V2p')
ARMS_LOWER = tuple(a.lower() for a in ARMS)
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
VAL_DECIDING = list(m5p_103.VF_DECIDING)      # 102 pred/02 s1
VAL_PRED01 = list(m5p_103.VF_PRED01)          # 102 pred/01 s6 as written: reported, never deciding
DEFAULT_CACHE = m5p_103.SNAPSHOT_DIR
DEFAULT_SIGNATURE = m5p_103.SIGNATURE_PREFIX
DEFAULT_RECOMPILE = 'C:/kyty/s103/m5p/recompile.json'
DEFAULT_REGS = 'C:/kyty/s103/m5p/regs.json'
DEFAULT_LAYOUT = 'C:/kyty/s103/m5p/layout_check.json'
SPIRV_MAGIC = struct.pack('<I', 0x07230203)
# fields of an m5p_recompile.py module entry carried into the plan (reported only)
RECOMPILE_FIELDS = ('name', 'bytes', 'sha256', 'cache_id', 'identity', 'bda_rewrite', 'bda_rewrite_detail',
                    'words', 'buffer_align')
REGS_FIELDS = ('register_count', 'local_memory_bytes', 'binary_size', 'stack_size', 'full_instructions',
               'full_ops', 's16_instructions', 's16_ops', 'ldg_variants')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def md5_file(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def norm_stage(value):
    key = str(value or '').strip().lower()
    return {'ps': 'ps', 'pixel': 'ps', 'fs': 'ps', 'fragment': 'ps', 'cs': 'cs',
            'compute': 'cs', 'vs': 'vs', 'vertex': 'vs'}.get(key, key or None)


def norm_hash(value):
    text = str(value or '').strip().lower()
    if text.startswith('0x'):
        text = text[2:]
    return text.rjust(16, '0') if re.fullmatch(r'[0-9a-f]{1,16}', text) else text


# ---------------------------------------------------------------- recompile.json
def norm_arm(value, base_dir, notes, where):
    """An arm entry -> {path, md5, ...extra} or None.  Accepts a dict or a bare path."""
    if value is None:
        return None
    if isinstance(value, str):
        value = {'path': value}
    if not isinstance(value, dict):
        notes.append('%s: arm entry of type %s ignored' % (where, type(value).__name__))
        return None
    entry = dict(value)
    path = entry.get('path') or entry.get('spv') or entry.get('file') or entry.get('out')
    if path:
        path = str(path).replace('\\', '/')
        if not os.path.isabs(path) and base_dir:
            path = os.path.join(base_dir, path).replace('\\', '/')
        entry['path'] = path
    entry.pop('spv', None)
    md5 = entry.get('md5')
    if path and os.path.isfile(path):
        actual = md5_file(path)
        if md5 and md5.lower() != actual:
            notes.append('%s: md5 in recompile.json %s != file %s (file used)' % (where, md5, actual))
            entry['md5_recorded'] = md5
        entry['md5'] = actual
        entry['exists'] = True
    else:
        entry['exists'] = False
        if md5:
            entry['md5'] = str(md5).lower()
    return entry


def perms_from_caches(entry, notes, name):
    """m5p_recompile.py format: caches[] -> modules[] (one per arm and permutation)."""
    perms = {}
    for cache in entry.get('caches', []):
        cache_id = cache.get('cache_id') or 'cache'
        for module in cache.get('modules', []):
            arm = module.get('arm')
            if arm not in ARMS:
                notes.append('%s: module %s of unknown arm %r ignored' % (name, module.get('name'), arm))
                continue
            k = '%s:%s' % (cache_id, module.get('perm'))
            row = perms.setdefault(k, {'k': k, 'cache_id': cache_id, 'perm_index': module.get('perm')})
            if arm in row:
                notes.append('%s: two %s modules for permutation %s; the first is kept' % (name, arm, k))
                continue
            arm_entry = {'path': module.get('spv'), 'md5': module.get('md5')}
            for field in RECOMPILE_FIELDS:
                if field in module:
                    arm_entry[field] = module[field]
            if isinstance(module.get('spirv_val'), dict):
                arm_entry['recompile_spirv_val_pass'] = module['spirv_val'].get('pass')
            arm_entry['recompile_rc'] = module.get('rc')
            row[arm] = arm_entry
    return list(perms.values())


def load_side_table(path, notes, what):
    """regs.json / layout_check.json -> {module name: row}; missing or unreadable => {}."""
    if not path or path == '0' or not os.path.isfile(path):
        if path and path != '0':
            notes.append('%s %s missing: not merged' % (what, path))
        return {}
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    rows = data.get('rows', []) if isinstance(data, dict) else data
    return {row.get('module'): row for row in rows if isinstance(row, dict) and row.get('module')}


def load_recompile(path, notes, regs=None, layout=None):
    """recompile.json -> ({item: {stage, hash, perms: [{k, A, V1, V2p, ...}]}}, header).

    header: the recompile inputs new s2 fixes (exe sha256, cache dir, signature, seal)."""
    regs = regs or {}
    layout = layout or {}
    if path is None or not os.path.isfile(path):
        notes.append('recompile.json missing (%s): every item has no arm-A module' % path)
        return {}, {}
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    base_dir = os.path.dirname(os.path.abspath(path))
    raw_items = data.get('items', data) if isinstance(data, dict) else data
    if isinstance(raw_items, list):
        listed = {}
        for i, entry in enumerate(raw_items):
            key = entry.get('item') or entry.get('name') or entry.get('id') or entry.get('hash') or str(i)
            listed[key] = entry
        raw_items = listed
    by_hash = {h: name for name, _, h, _ in ITEMS}
    items = {}
    for key, entry in raw_items.items():
        if not isinstance(entry, dict):
            continue
        name = key if key in {n for n, _, _, _ in ITEMS} else None
        hash_ = norm_hash(entry.get('hash') or (key if name is None else ''))
        if name is None:
            name = by_hash.get(hash_, key)
        perms_raw = entry.get('perms', entry.get('permutations'))
        source = 'perms'
        if perms_raw is None and entry.get('caches'):
            perms_raw = perms_from_caches(entry, notes, name)
            source = 'caches'
        if isinstance(perms_raw, dict):
            perms_raw = [dict(v, k=k) if isinstance(v, dict) else v for k, v in perms_raw.items()]
        perms = []
        for i, perm in enumerate(perms_raw or []):
            if not isinstance(perm, dict):
                continue
            k = perm.get('k', perm.get('perm', perm.get('index', i)))
            try:
                k = int(k)
            except (TypeError, ValueError):
                pass
            row = {'k': k}
            for arm in ARMS:
                value = perm.get(arm, perm.get(arm.lower()))
                arm_entry = norm_arm(value, base_dir, notes, '%s perm %s %s' % (name, k, arm))
                if arm_entry is not None:
                    module_name = arm_entry.get('name')
                    if module_name in regs:
                        for field in REGS_FIELDS:
                            if field in regs[module_name]:
                                arm_entry[field] = regs[module_name][field]
                        if regs[module_name].get('md5') and arm_entry.get('md5') \
                                and regs[module_name]['md5'] != arm_entry['md5']:
                            notes.append('%s: regs.json md5 differs from the module file' % module_name)
                    if module_name in layout:
                        arm_entry['layout_ok'] = layout[module_name].get('ok')
                row[arm] = arm_entry
            for extra in perm:
                if extra not in ('k', 'perm', 'index') and extra not in ARMS and extra.lower() not in ARMS_LOWER:
                    row.setdefault('extra', {})[extra] = perm[extra]
            perms.append(row)
        keys = [p['k'] for p in perms]
        if len(set(map(str, keys))) != len(keys):
            notes.append('%s: permutation keys are not unique: %s' % (name, keys))
        items[name] = {'stage': norm_stage(entry.get('stage')), 'hash': hash_, 'perms': perms, 'source': source,
                       'extra': {k: v for k, v in entry.items()
                                 if k not in ('stage', 'hash', 'perms', 'permutations', 'caches', 'cache_candidates')}}
    header = {}
    if isinstance(data, dict):
        header = dict(exe_sha256=data.get('exe_sha256'), cache_dir=data.get('cache_dir'),
                      signature=data.get('signature'), pred_sha256=data.get('pred_sha256'),
                      arms=data.get('arms'))
    return items, header


# ---------------------------------------------------------------- translation cache link
def cache_modules(data):
    """Every SPIR-V module stored behind its u32 word-count prefix (PodVec) in a cache file."""
    found = []
    pos = data.find(SPIRV_MAGIC)
    while pos != -1:
        if pos >= 4:
            count = struct.unpack_from('<I', data, pos - 4)[0]
            end = pos + 4 * count
            if count >= 5 and end <= len(data):
                cursor = pos + 20
                ok = True
                while cursor < end:
                    word_count = struct.unpack_from('<I', data, cursor)[0] >> 16
                    if word_count == 0:
                        ok = False
                        break
                    cursor += 4 * word_count
                if ok and cursor == end:
                    found.append(hashlib.md5(data[pos:end]).hexdigest())
        pos = data.find(SPIRV_MAGIC, pos + 4)
    return found


def cache_link(cache_dir, signature_prefix, hashes):
    """hash -> {md5 -> [file#index]} for the cache files of the given hashes, current signature."""
    link = {h: {} for h in hashes}
    files = {h: [] for h in hashes}
    skipped = {h: [] for h in hashes}
    if not cache_dir or not os.path.isdir(cache_dir):
        return link, files, skipped, False
    for name in sorted(os.listdir(cache_dir)):
        match = re.fullmatch(r'(ps|cs|vs)_([0-9a-f]{16})_([0-9a-f]{16})\.bin', name)
        if not match or match.group(2) not in link:
            continue
        data = Path(cache_dir, name).read_bytes()
        signature = data[:data.find(b'\n')].decode('ascii', 'replace') if b'\n' in data[:256] else ''
        if signature_prefix and not signature.startswith(signature_prefix):
            skipped[match.group(2)].append(dict(file=name, signature=signature[:60]))
            continue
        mods = cache_modules(data)
        files[match.group(2)].append(dict(file=name, signature=signature, permutations=len(mods),
                                          sha256=hashlib.sha256(data).hexdigest()))
        for index, md5 in enumerate(mods):
            link[match.group(2)].setdefault(md5, []).append('%s#%d' % (name, index))
    return link, files, skipped, True


def recompiled_cache_perms(perms):
    """{(cache_id, perm index)} the recompile covered (m5p_recompile.py format only)."""
    out = set()
    for perm in perms.values():
        if perm.get('cache_id') is not None and perm.get('perm_index') is not None:
            out.add((str(perm['cache_id']), int(perm['perm_index'])))
    for perm in perms.values():      # m5p_recompile.py keeps cache_id / perm_index in 'extra'
        extra = perm.get('extra') or {}
        if extra.get('cache_id') is not None and extra.get('perm_index') is not None:
            out.add((str(extra['cache_id']), int(extra['perm_index'])))
    return out


def link_recompiled(ref, covered):
    """'<stage>_<hash>_<cache_id>.bin#<index>' -> was that permutation recompiled?"""
    match = re.fullmatch(r'(?:ps|cs|vs)_[0-9a-f]{16}_([0-9a-f]{16})\.bin#(\d+)', ref)
    if not match:
        return None
    return (match.group(1), int(match.group(2))) in covered


# ---------------------------------------------------------------- spirv-val (V-f)
def spirv_val(path, exe, args):
    try:
        done = subprocess.run([exe] + list(args) + [path], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as error:
        return dict(ok=False, rc=None, output=str(error)[:2000], cmd=' '.join(args))
    return dict(ok=done.returncode == 0, rc=done.returncode, cmd=' '.join(args),
                output=(done.stdout + done.stderr).strip()[:2000])


# ---------------------------------------------------------------- the plan
def build_plan(find, recompile, options, notes):
    modules = find.get('modules', {})
    events = find.get('events', [])
    events_of = {}
    for event in events:
        for stage in ('ps', 'cs'):
            rid = event.get(stage)
            if rid is None:
                continue
            if (stage == 'ps' and event.get('kind') != 'draw') or (stage == 'cs' and event.get('kind') != 'dispatch'):
                continue
            events_of.setdefault((rid, stage), []).append(event['eid'])

    table = [row for row in ITEMS]
    if options.mechanics:
        known = {row[0] for row in table}
        for name, entry in sorted(recompile.items()):
            if name not in known:
                table.append((name, entry.get('stage'), entry.get('hash'), 0.0))
    if options.items:
        wanted = set(options.items.split(','))
        table = [row for row in table if row[0] in wanted]

    # md5 -> [(item, perm k)] for arm A
    a_index = {}
    for name, stage, hash_, _ in table:
        for perm in recompile.get(name, {}).get('perms', []):
            a = perm.get('A')
            if a and a.get('md5'):
                a_index.setdefault(a['md5'], []).append((name, perm['k']))

    link, cache_files, cache_skipped, cache_ok = ({}, {}, {}, False)
    if not options.no_cache_link:
        link, cache_files, cache_skipped, cache_ok = cache_link(
            options.cache_dir, options.signature_prefix, [norm_hash(h) for _, _, h, _ in table])

    items = {}
    claimed = {}
    for name, stage, hash_, weight in table:
        rec = recompile.get(name, {})
        if rec and rec.get('stage') and rec['stage'] != stage:
            notes.append('%s: recompile.json stage %s != sealed %s' % (name, rec['stage'], stage))
        if rec and rec.get('hash') and norm_hash(rec['hash']) != norm_hash(hash_):
            notes.append('%s: recompile.json hash %s != sealed %s' % (name, rec['hash'], hash_))
        perms = {perm['k']: perm for perm in rec.get('perms', [])}
        covered = recompiled_cache_perms(perms)
        item = dict(stage=stage, hash=hash_, weight=weight, perms_available=sorted(perms, key=str),
                    modules=[], excluded_modules=[], stage_conflicts=[], arm_missing={},
                    events=[], excluded_events=[], last_event=None, present=False)
        for rid, entry in sorted(modules.items(), key=lambda kv: kv[0]):
            md5 = entry.get('md5')
            owners = [o for o in a_index.get(md5, []) if o[0] == name]
            cached = link.get(norm_hash(hash_), {}).get(md5)
            if owners:
                if entry.get('stage') != stage:
                    item['stage_conflicts'].append(dict(orig_shader_id=rid, md5=md5, stage=entry.get('stage')))
                    continue
                k = owners[0][1]
                if len(owners) > 1:
                    notes.append('%s: module %s matches several permutations %s; using %s'
                                 % (name, rid, [o[1] for o in owners], k))
                if rid in claimed:
                    notes.append('module %s matched by %s and %s; kept for %s' % (rid, claimed[rid], name, claimed[rid]))
                    continue
                claimed[rid] = name
                evs = sorted(events_of.get((rid, stage), []))
                perm = perms[k]
                row = dict(orig_shader_id=rid, md5=md5, size=entry.get('size'), perm=k, events=evs,
                           cache_link=cached or [])
                for arm in ARMS:
                    arm_entry = perm.get(arm)
                    if arm_entry and arm_entry.get('exists'):
                        row[arm] = dict(path=arm_entry['path'], md5=arm_entry['md5'])
                        for key in arm_entry:
                            if key not in ('path', 'md5', 'exists'):
                                row[arm][key] = arm_entry[key]
                    else:
                        row[arm] = None
                        item['arm_missing'].setdefault(arm, []).append(k)
                item['modules'].append(row)
            elif cached:
                evs = sorted(events_of.get((rid, stage), []))
                flags = [link_recompiled(ref, covered) for ref in cached]
                item['excluded_modules'].append(dict(orig_shader_id=rid, md5=md5, size=entry.get('size'),
                                                     stage=entry.get('stage'), events=evs,
                                                     link='cache', cache_link=cached,
                                                     recompiled=(True if any(f is True for f in flags)
                                                                 else False if flags and all(f is False for f in flags)
                                                                 else None)))
        # "present in the capture" (V-a, V-b, the V-c denominator; 102 pred/02 s5): a captured module is
        # linked to the item's hash, by arm A's md5 or by the translation cache.  "included" (summed,
        # replaced, compared): linked by arm A's md5 only.  A present item with no included module is
        # wholly excluded - its time goes into the V-c share and never into a sum.
        item['included'] = bool(item['modules'])
        item['present'] = bool(item['modules'] or item['excluded_modules'])
        item['events'] = sorted({e for m in item['modules'] for e in m['events']})
        item['excluded_events'] = sorted({e for m in item['excluded_modules'] for e in m['events']})
        item['last_event'] = item['events'][-1] if item['events'] else None
        item['modules_without_events'] = [m['orig_shader_id'] for m in item['modules'] if not m['events']]
        item['excluded_not_recompiled'] = [m['orig_shader_id'] for m in item['excluded_modules']
                                           if m.get('recompiled') is False]
        seen = {m['perm'] for m in item['modules']}
        item['perms_not_captured'] = [k for k in item['perms_available'] if k not in seen]
        # cache consistency, offline: does arm A reproduce what the game cached?
        cached_md5 = set(link.get(norm_hash(hash_), {}))
        a_md5 = {p['A']['md5'] for p in perms.values() if p.get('A') and p['A'].get('md5')}
        item['cache'] = dict(files=cache_files.get(norm_hash(hash_), []),
                             skipped_other_signature=cache_skipped.get(norm_hash(hash_), []),
                             cached_permutations=len(cached_md5),
                             arm_a_in_cache=sorted(str(k) for k, p in perms.items()
                                                   if p.get('A') and p['A'].get('md5') in cached_md5),
                             arm_a_not_in_cache=sorted(str(k) for k, p in perms.items()
                                                       if p.get('A') and p['A'].get('md5') and p['A']['md5'] not in cached_md5),
                             cached_not_reproduced=sorted(ref for md5, refs in link.get(norm_hash(hash_), {}).items()
                                                          if md5 not in a_md5 for ref in refs))
        if not item['included']:
            item['fallback'] = fallback_report(find, hash_, stage, perms, item)
        items[name] = item

    arms = [dict(name='B', replacements=[])]
    for arm in ARMS:
        reps = []
        for name, item in items.items():
            for module in item['modules']:
                if module.get(arm):
                    reps.append(dict(orig_shader_id=module['orig_shader_id'], spv_path=module[arm]['path'],
                                     md5=module[arm]['md5'], orig_md5=module['md5'], stage=item['stage'],
                                     item=name, perm=module['perm']))
        arms.append(dict(name=arm, replacements=reps))
    all_events = sorted({e for item in items.values() for e in item['events'] + item['excluded_events']})
    return items, arms, all_events, cache_ok


def fallback_report(find, hash_, stage, perms, item):
    """Report only.  Never includes a module."""
    report = {'hash_text_hits': [], 'nearest_by_size': [], 'note':
              'report only: a fallback never includes a module (102 pred/01_m5_bench.md V-c)'}
    needle = norm_hash(hash_).encode()
    needle_upper = needle.upper()
    for rid, entry in find.get('modules', {}).items():
        dump = entry.get('dump')
        if dump and os.path.isfile(dump):
            raw = Path(dump).read_bytes()
            if needle in raw or needle_upper in raw:
                report['hash_text_hits'].append(dict(orig_shader_id=rid, md5=entry.get('md5')))
    sizes = [os.path.getsize(p['A']['path']) for p in perms.values()
             if p.get('A') and p['A'].get('exists')]
    if sizes:
        cands = []
        for rid, entry in find.get('modules', {}).items():
            if entry.get('stage') != stage or not entry.get('size'):
                continue
            rel = min(abs(entry['size'] - s) / float(s) for s in sizes)
            cands.append((rel, rid, entry.get('size'), entry.get('md5'), entry.get('n_events')))
        cands.sort()
        report['nearest_by_size'] = [dict(orig_shader_id=rid, size=size, md5=md5, n_events=n,
                                          rel_size_diff=round(rel, 4))
                                     for rel, rid, size, md5, n in cands[:5]]
        report['arm_a_sizes'] = sizes
    report['hash_text_note'] = ('the translator embeds no hash (session 102 check), so no text hit '
                                'is expected')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--find', required=True)
    parser.add_argument('--recompile', default=DEFAULT_RECOMPILE)
    parser.add_argument('--out', required=True)
    parser.add_argument('--cache-dir', default=DEFAULT_CACHE)
    parser.add_argument('--signature-prefix', default=None,
                        help='default: recompile.json "signature", else %s' % DEFAULT_SIGNATURE)
    parser.add_argument('--no-cache-link', action='store_true')
    parser.add_argument('--regs', default=DEFAULT_REGS, help="regs.json to merge (reported only); '0' = none")
    parser.add_argument('--layout', default=DEFAULT_LAYOUT, help="layout_check.json to merge; '0' = none")
    parser.add_argument('--spirv-val', default=SPIRV_VAL)
    parser.add_argument('--no-spirv-val', action='store_true')
    parser.add_argument('--items', default=None, help='comma list restricting the item table')
    parser.add_argument('--mechanics', action='store_true',
                        help='accept items outside the sealed table (weight 0); mechanics only')
    parser.add_argument('--pred', default=PRED, help=argparse.SUPPRESS)
    parser.add_argument('--parent01', default=PARENT01, help=argparse.SUPPRESS)
    parser.add_argument('--parent02', default=PARENT02, help=argparse.SUPPRESS)
    options = parser.parse_args(argv)
    if os.path.exists(options.out):
        print('refusing to overwrite %s' % options.out)
        return 2
    for label, path, want in (("M5' SEAL", options.pred, PRED_SHA),
                              ('SESSION-102 PARENT pred/01', options.parent01, PARENT01_SHA),
                              ('SESSION-102 PARENT pred/02', options.parent02, PARENT02_SHA)):
        if not m5p_103.seal_ok(path, want):
            print('%s CHANGED OR MISSING (%s): refusing to plan' % (label, path))
            return 2
    notes = []
    find = json.loads(Path(options.find).read_text(encoding='utf-8'))
    if not find.get('complete'):
        print('find JSON %s is not complete' % options.find)
        return 2
    regs = load_side_table(options.regs, notes, 'regs.json')
    layout = load_side_table(options.layout, notes, 'layout_check.json')
    recompile, header = load_recompile(options.recompile, notes, regs, layout)
    signature = header.get('signature')
    if options.signature_prefix is None:
        options.signature_prefix = signature.strip() if signature else DEFAULT_SIGNATURE
    items, arms, all_events, cache_ok = build_plan(find, recompile, options, notes)

    validation = {}
    if not options.no_spirv_val:
        paths = sorted({rep['spv_path'] for arm in arms for rep in arm['replacements']})
        for path in paths:
            validation[path] = dict(ubsl=spirv_val(path, options.spirv_val, VAL_DECIDING),
                                    pred01=spirv_val(path, options.spirv_val, VAL_PRED01))
    plan = dict(tool='m5p_plan', created=time.strftime('%Y-%m-%dT%H:%M:%S'),
                pred=PRED, pred_sha256=PRED_SHA, parent01=PARENT01, parent01_sha256=PARENT01_SHA,
                parent02=PARENT02, parent02_sha256=PARENT02_SHA,
                mechanics=bool(options.mechanics),
                capture=find.get('capture'), capture_sha256=find.get('capture_sha256'),
                find_json=os.path.abspath(options.find).replace('\\', '/'), find_sha256=sha256(options.find),
                recompile_json=options.recompile,
                recompile_sha256=sha256(options.recompile) if options.recompile and os.path.isfile(options.recompile) else None,
                recompile_exe_sha256=header.get('exe_sha256'), recompile_cache_dir=header.get('cache_dir'),
                recompile_signature=header.get('signature'), recompile_pred_sha256=header.get('pred_sha256'),
                recompile_arms=header.get('arms'),
                regs_json=options.regs if regs else None,
                regs_sha256=sha256(options.regs) if regs else None,
                layout_json=options.layout if layout else None,
                layout_sha256=sha256(options.layout) if layout else None,
                cache_dir=options.cache_dir, cache_link_used=cache_ok, signature_prefix=options.signature_prefix,
                spirv_val=None if options.no_spirv_val else options.spirv_val,
                spirv_val_command_deciding='spirv-val %s <spv>' % ' '.join(VAL_DECIDING),
                spirv_val_command_pred01_reported='spirv-val %s <spv>' % ' '.join(VAL_PRED01),
                items=items, arms=arms, events=all_events, validation=validation, notes=notes)
    input_problems = m5p_103.input_problems(plan)
    plan['input_problems'] = input_problems
    Path(options.out).parent.mkdir(parents=True, exist_ok=True)
    Path(options.out).write_text(json.dumps(plan, indent=1), encoding='utf-8')

    print('plan -> %s' % options.out)
    print('capture %s  sha256 %s%s' % (plan['capture'], plan['capture_sha256'],
                                       '' if plan['capture_sha256'] == m5p_103.CAPTURE_SHA
                                       else '  (NOT the sealed capture %s)' % m5p_103.CAPTURE_SHA[:12]))
    print('%-4s %-3s %-16s %8s %7s %8s %5s %5s %6s %6s %6s %6s  %s' % (
        'item', 'stg', 'hash', 'weight', 'present', 'included', 'mods', 'excl', 'x-norc', 'events', 'x-evts',
        'last', 'arm missing'))
    for name, item in items.items():
        print('%-4s %-3s %-16s %8.1f %7s %8s %5d %5d %6d %6d %6d %6s  %s'
              % (name, item['stage'], item['hash'], item['weight'], item['present'], item['included'],
                 len(item['modules']), len(item['excluded_modules']), len(item['excluded_not_recompiled']),
                 len(item['events']), len(item['excluded_events']), item['last_event'], item['arm_missing'] or ''))
    for arm in arms:
        print('arm %-3s %d replacements' % (arm['name'], len(arm['replacements'])))
    if validation:
        bad = [p for p, v in validation.items() if not v['ubsl']['ok']]
        bad_pred01 = [p for p, v in validation.items() if not v['pred01']['ok']]
        print('spirv-val, deciding command (102 pred/02 s1, --uniform-buffer-standard-layout): %d of %d modules fail'
              % (len(bad), len(validation)))
        print('spirv-val, 102 pred/01 command (reported only): %d of %d fail' % (len(bad_pred01), len(validation)))
        for path in bad:
            print('  V-f FAIL %s: %s' % (path, validation[path]['ubsl']['output'][:300]))
    if input_problems:
        print('WARNING: recompile inputs are not the sealed ones (the scorer will fail IDENTITY): %s' % input_problems)
    not_recompiled = {n: i['excluded_not_recompiled'] for n, i in items.items() if i['excluded_not_recompiled']}
    if not_recompiled:
        print('WARNING: excluded modules whose cache permutation was never recompiled (see M5P_RUNBOOK): %s'
              % not_recompiled)
    for note in notes:
        print('note:', note)
    return 0


if __name__ == '__main__':
    sys.exit(main())
