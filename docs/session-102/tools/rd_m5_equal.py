"""Session 102, M5: output equality V-e (pred/01_m5_bench.md s6 AS AMENDED by pred/02_m5_addendum.md
s2), in one qrenderdoc.

    RD_CAP=<rdc> RD_PLAN=<plan.json> RD_OUT=<equal.json> \
        "C:/Program Files/RenderDoc/qrenderdoc.exe" --python C:/kyty/s102/rd_m5_equal.py

For every item with an included module, with ONLY that item's modules replaced, the replay is moved
to the item's LAST event (SetFrameEvent: the state right after it) and its outputs are read back:
  PS item: every colour target (PipeState.GetOutputTargets) and the depth target
           (GetDepthTarget) bound at that event - every mip and slice of the view actually bound,
           every sample of a multisampled target;
  CS item: every read-write image and buffer bound to the compute stage at that event
           (GetReadWriteResources(Compute), onlyUsed=False): images over the view's mips and
           slices, buffers over the bound range [byteOffset, byteOffset + byteSize).

pred/02 s2, as implemented:
  * arm A (the reference) is replayed THREE times - A1, A2, A3 - each a separate replace / move /
    read / un-replace; the differing bytes of every pair (A1-A2, A1-A3, A2-A3) are summed over the
    deciding outputs and recorded.  A1 = A2 = A3 => the item is REPEATABLE.
  * every variant (V1, V2, V2s) is read once and compared with A1 byte for byte.  A resource bound
    under the variant only (for example the BDA fault buffer, which only a uses_dma module declares)
    is read under A three more times, so E is always taken over exactly the outputs the variant is
    compared on; the per-variant pair counts are recorded as variants[arm].reference_pair_diff_bytes.
  * repeatable => the variant passes only bit-equal to A1; otherwise E = the largest pair count and
    the variant passes iff its differing bytes against A1 are <= 2*E ("within replay noise", never
    "equal").  The 'pass' written here is INFORMATIONAL (m5_102.ve_judge); the scorer re-judges from
    the raw counts.
  * every A replay and every variant read checks that the replacement is in effect at the last
    event (the pipeline reflection shows the replacement's bytes; RenderDoc 1.46 keeps the original
    id in GetShader()).

Env: RD_CAP, RD_PLAN, RD_OUT (required); RD_VARIANTS (default V1,V2,V2s), RD_REF (default A; 'B' =
     the capture's own modules, DIAGNOSTIC ONLY - the scorer refuses it), RD_ITEMS (comma list,
     default every present item), RD_PS_RW=1 (a PS item's read-write resources, reported only),
     RD_SHA=0 (mechanics only), RD_REPLAY_OPT (none|conservative|balanced|fastest, default
     RenderDoc's balanced).  The number of A replays is fixed at 3 by the addendum.
Refuses to run unless both sealed texts match.  Written after every item.  Log: <RD_OUT>.log.
"""
import os
import sys
import time
import json
import hashlib

sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s102')
import m5_rdlib as lib  # noqa: E402
import m5_102  # noqa: E402

OUT = lib.env_required('RD_OUT')
log = lib.Log(OUT + '.log')
compare_bytes = lib.compare_bytes


def main():
    import renderdoc as rd
    lib.hide_ui(log)
    seals = lib.require_seals(log)
    cap_path = lib.env_required('RD_CAP')
    plan_path = lib.env_required('RD_PLAN')
    plan = json.load(open(plan_path, encoding='utf-8'))
    variants = [v.strip() for v in os.environ.get('RD_VARIANTS', ','.join(m5_102.VARIANTS)).split(',') if v.strip()]
    ref = os.environ.get('RD_REF', 'A').strip()
    only = [v.strip() for v in os.environ.get('RD_ITEMS', '').split(',') if v.strip()]
    ps_rw = os.environ.get('RD_PS_RW', '0') == '1'
    replays = m5_102.A_REPLAYS
    if os.path.exists(OUT):
        raise SystemExit('RD_OUT %s exists: never overwritten' % OUT)
    out = dict(tool='rd_m5_equal', capture=cap_path, plan=os.path.abspath(plan_path).replace('\\', '/'),
               plan_sha256=hashlib.sha256(open(plan_path, 'rb').read()).hexdigest(),
               pred_sha256=plan.get('pred_sha256'), addendum_sha256=plan.get('addendum_sha256'),
               seals=seals, mechanics=bool(plan.get('mechanics')),
               reference=ref, a_replays=replays, variants=variants, ps_rw=ps_rw,
               rule='pred/02 s2: repeatable => bit-equal to A1; else differing bytes vs A1 <= 2*E',
               replay_optimisation=lib.replay_opt_name(),
               started=time.strftime('%Y-%m-%dT%H:%M:%S'),
               items={}, build_errors=[], complete=False)
    if os.environ.get('RD_SHA', '1') != '0':
        out['capture_sha256'] = lib.sha256_file(cap_path)
        if plan.get('capture_sha256') and plan['capture_sha256'] != out['capture_sha256']:
            out['capture_sha256_mismatch_plan'] = plan['capture_sha256']
    else:
        out['capture_sha256'] = None
    cap, ctrl = lib.open_capture(rd, cap_path, log)
    resources = lib.resource_map(ctrl)
    textures = {str(t.resourceId): t for t in ctrl.GetTextures()}
    buffers = {str(b.resourceId): b for b in ctrl.GetBuffers()}
    built = {}

    def build(path, stage, item, arm):
        spv = open(path, 'rb').read()
        key = (hashlib.md5(spv).hexdigest(), stage)
        if key not in built:
            new_id, errors = ctrl.BuildTargetShader('main', rd.ShaderEncoding.SPIRV, spv, rd.ShaderCompileFlags(),
                                                    lib.stage_enum(rd, stage))
            if new_id == rd.ResourceId.Null():
                out['build_errors'].append(dict(item=item, arm=arm, path=path, messages=errors))
                log('BUILD FAILED %s %s %s:\n%s' % (item, arm, path, errors))
                return None
            built[key] = new_id
        return built[key]

    def texture_keys(desc):
        """Every subresource of the view bound by a texture descriptor."""
        rid = str(desc.resource)
        tex = textures.get(rid)
        if tex is None:
            return []
        first_mip = desc.firstMip
        num_mips = desc.numMips if desc.numMips > 0 else tex.mips - first_mip
        first_slice = desc.firstSlice
        num_slices = desc.numSlices if desc.numSlices > 0 else tex.arraysize - first_slice
        if tex.depth > 1:          # 3D: GetTextureData returns the whole mip whatever the slice
            first_slice, num_slices = 0, 1
        keys = []
        for mip in range(first_mip, min(tex.mips, first_mip + num_mips)):
            for sl in range(first_slice, min(max(tex.arraysize, 1), first_slice + num_slices)):
                for sample in range(max(tex.msSamp, 1)):
                    keys.append(('tex', rid, mip, sl, sample))
        return keys

    def buffer_key(desc):
        rid = str(desc.resource)
        buf = buffers.get(rid)
        if buf is None:
            return None
        offset = desc.byteOffset
        size = desc.byteSize
        if size == 0 or size > buf.length - offset:     # VK_WHOLE_SIZE or over-long range
            size = max(0, buf.length - offset)
        return ('buf', rid, offset, size)

    def discover(stage):
        """Keys of every output resource bound at the current event."""
        pipe = ctrl.GetPipelineState()
        keys = []
        if stage == 'ps':
            for desc in pipe.GetOutputTargets():
                if not lib.is_null(rd, desc.resource):
                    keys += texture_keys(desc)
            depth = pipe.GetDepthTarget()
            if depth is not None and not lib.is_null(rd, depth.resource):
                keys += texture_keys(depth)
        if stage == 'cs' or (stage == 'ps' and ps_rw):
            rw = pipe.GetReadWriteResources(rd.ShaderStage.Compute if stage == 'cs' else rd.ShaderStage.Pixel)
            for used in rw:
                desc = used.descriptor
                if lib.is_null(rd, desc.resource):
                    continue
                rid = str(desc.resource)
                if rid in textures:
                    keys += [k + ('rw',) if stage == 'ps' else k for k in texture_keys(desc)]
                elif rid in buffers:
                    key = buffer_key(desc)
                    if key and key[3] > 0:
                        keys.append(key + ('rw',) if stage == 'ps' else key)
        seen = []
        for k in keys:
            if k not in seen:
                seen.append(k)
        return seen

    def read(key):
        if key[0] == 'tex':
            return bytes(ctrl.GetTextureData(resources[key[1]], rd.Subresource(key[2], key[3], key[4])))
        return bytes(ctrl.GetBufferData(resources[key[1]], key[2], key[3]))

    def state(pairs, eid, stage, read_keys=None, also=()):
        """Replace, move to eid, list the bound outputs, read read_keys (default: the listed
        ones) plus `also`, un-replace.  Returns (listed keys, {key: bytes}, md5 of the module the
        pipeline reflection shows at eid)."""
        for orig, new_id in pairs:
            ctrl.ReplaceResource(orig, new_id)
        try:
            ctrl.SetFrameEvent(eid, True)
            refl = ctrl.GetPipelineState().GetShaderReflection(lib.stage_enum(rd, stage))
            shown = hashlib.md5(bytes(refl.rawBytes)).hexdigest() if refl is not None else None
            keys = discover(stage)
            wanted = list(keys if read_keys is None else read_keys)
            wanted += [k for k in also if k not in wanted]
            data = {key: read(key) for key in wanted}
        finally:
            for orig, _ in pairs:
                ctrl.RemoveReplacement(orig)
        return keys, data, shown

    def deciding(key):
        return not (key[-1] == 'rw')      # a PS item's read-write resources are reported only

    def pair_counts(d1, d2, d3, keys):
        """Differing bytes of every pair of the three A replays, summed over the deciding keys, and
        per key (non-zero only)."""
        total = {p: 0 for p in m5_102.REPLAY_PAIRS}
        by_key = []
        for key in keys:
            n12 = compare_bytes(d1.get(key, b''), d2.get(key, b''))[2]
            n13 = compare_bytes(d1.get(key, b''), d3.get(key, b''))[2]
            n23 = compare_bytes(d2.get(key, b''), d3.get(key, b''))[2]
            if deciding(key):
                total['A1-A2'] += n12
                total['A1-A3'] += n13
                total['A2-A3'] += n23
            if n12 or n13 or n23:
                by_key.append(dict(key=list(key), deciding=deciding(key), pairs=[n12, n13, n23]))
        return total, by_key

    names = [n for n, item in plan['items'].items() if item.get('modules') and (not only or n in only)]
    for name in names:
        item = plan['items'][name]
        t_item = time.time()
        stage = item['stage']
        eid = item['last_event']
        record = dict(stage=stage, last_event=eid, modules=[m['orig_shader_id'] for m in item['modules']],
                      variants={})
        out['items'][name] = record
        arm_pairs = {}
        for arm in [ref] + variants:
            pairs = []
            missing = False
            for module in (item['modules'] if arm != 'B' else []):     # 'B' = the capture's own modules
                entry = module.get(arm)
                if not entry:
                    missing = True
                    break
                new_id = build(entry['path'], stage, name, arm)
                if new_id is None:
                    missing = True
                    break
                pairs.append((resources[module['orig_shader_id']], new_id))
            arm_pairs[arm] = None if missing else pairs
        if arm_pairs[ref] is None:
            record['error'] = 'reference arm %s unavailable' % ref
            lib.write_json_atomic(OUT, out)
            continue
        # the module bound at the last event and what each arm must show there
        at_last = [m for m in item['modules'] if eid in m.get('events', [])]
        expect = {}
        for arm in [ref] + variants:
            if at_last and arm == 'B':
                expect[arm] = at_last[0].get('md5')
            elif at_last and at_last[0].get(arm):
                expect[arm] = hashlib.md5(open(at_last[0][arm]['path'], 'rb').read()).hexdigest()
        record['in_effect'] = {}

        def effect(label, arm, shown):
            ok = expect.get(arm) is not None and expect.get(arm) == shown
            record['in_effect'][label] = dict(expected=expect.get(arm), got=shown, ok=ok)
            return ok

        # ---- the three A replays (pred/02 s2) ----
        keys_ref, data1, shown = state(arm_pairs[ref], eid, stage)
        ok = effect('%s1' % ref, ref, shown)
        _, data2, shown = state(arm_pairs[ref], eid, stage, read_keys=keys_ref)
        ok = effect('%s2' % ref, ref, shown) and ok
        _, data3, shown = state(arm_pairs[ref], eid, stage, read_keys=keys_ref)
        ok = effect('%s3' % ref, ref, shown) and ok
        if not ok:
            record['error'] = 'reference replacement not in effect at the last event'
            log('%s: %s' % (name, record['error']))
            lib.write_json_atomic(OUT, out)
            continue
        ref_pairs, ref_by_key = pair_counts(data1, data2, data3, keys_ref)
        del data2, data3
        record['reference_resources'] = [list(k) + [len(data1[k])] for k in keys_ref]
        record['reference_replays'] = replays
        record['reference_pair_diff_bytes'] = ref_pairs
        record['reference_pair_diff_by_resource'] = ref_by_key[:64]
        record['E'] = max(ref_pairs.values())
        record['repeatable'] = record['E'] == 0
        log('%s: last event %d, %d output subresources under %s; A replay pairs %s -> %s'
            % (name, eid, len(keys_ref), ref, ref_pairs,
               'REPEATABLE' if record['repeatable'] else 'replay-nondeterministic, E = %d' % record['E']))
        if not any(deciding(k) for k in keys_ref):
            record['error'] = 'no output resource bound at the last event'
            lib.write_json_atomic(OUT, out)
            continue

        # ---- every variant against A1 ----
        for arm in variants:
            if arm_pairs.get(arm) is None:
                record['variants'][arm] = dict(equal=False, error='variant module unavailable')
                continue
            keys_var, data_var, shown = state(arm_pairs[arm], eid, stage, also=keys_ref)
            if not effect(arm, arm, shown):
                record['variants'][arm] = dict(equal=False, error='variant replacement not in effect at the last event')
                log('%s %s: replacement NOT in effect' % (name, arm))
                continue
            extra = [k for k in keys_var if k not in keys_ref]
            pairs_v = dict(ref_pairs)
            extra_ref = {}
            if extra:                                  # bound only under the variant: A three times too
                _, x1, s1 = state(arm_pairs[ref], eid, stage, read_keys=extra)
                _, x2, s2 = state(arm_pairs[ref], eid, stage, read_keys=extra)
                _, x3, s3 = state(arm_pairs[ref], eid, stage, read_keys=extra)
                if not (effect('%s1+%s' % (ref, arm), ref, s1) and effect('%s2+%s' % (ref, arm), ref, s2)
                        and effect('%s3+%s' % (ref, arm), ref, s3)):
                    record['variants'][arm] = dict(equal=False, error='reference replacement not in effect (extra reads)')
                    continue
                more, _ = pair_counts(x1, x2, x3, extra)
                for p in pairs_v:
                    pairs_v[p] += more[p]
                extra_ref = x1
                del x2, x3
            union = keys_ref + extra
            rows = []
            first = None
            ndiff = 0
            equal = True
            info_equal = True
            for key in union:
                a = data1.get(key, extra_ref.get(key))
                b = data_var.get(key)
                same, off, n = compare_bytes(a if a is not None else b'', b if b is not None else b'')
                rows.append(dict(key=list(key), deciding=deciding(key),
                                 size_ref=len(a) if a is not None else None,
                                 size_var=len(b) if b is not None else None, equal=same, first_diff=off,
                                 n_diff_bytes=n,
                                 bound_in=('both' if key in keys_ref and key in keys_var
                                           else 'reference' if key in keys_ref else 'variant')))
                if same:
                    continue
                if not deciding(key):
                    info_equal = False
                    continue
                equal = False
                ndiff += n
                if first is None:
                    first = dict(key=list(key), offset=off)
            judged = m5_102.ve_judge(pairs_v, ndiff, equal)
            record['variants'][arm] = {
                'equal': bool(equal), 'first_diff': first, 'n_diff_bytes': ndiff,
                'reference_pair_diff_bytes': pairs_v, 'E': judged['E'], 'limit': judged['limit'],
                'repeatable': judged['repeatable'], 'pass': judged['pass'], 'pass_kind': judged['kind'],
                'same_resource_set': keys_var == keys_ref, 'error': None,
                'info_rw_equal': info_equal if ps_rw and stage == 'ps' else None,
                'resources': rows}
            del data_var
            log('%s %s: bit-equal=%s, differing bytes vs A1 %d over %d subresources; E=%s -> %s%s'
                % (name, arm, equal, ndiff, len(rows), judged['E'], 'pass' if judged['pass'] else 'FAIL',
                   (' (%s)' % judged['kind']) if judged['kind'] else ''))
        del data1
        record['seconds'] = round(time.time() - t_item, 1)
        lib.write_json_atomic(OUT, out)
    out['finished'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    out['complete'] = True
    lib.write_json_atomic(OUT, out)
    for new_id in built.values():
        ctrl.FreeTargetResource(new_id)
    return 0


lib.run_main(main, log)
