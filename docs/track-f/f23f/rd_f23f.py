# F23f (HPP-592; ROADMAP s122 item 498(g)(3)-(4)): qrenderdoc --python rd_f23f.py - replay of the form-A programs in a capture
# (form of F12g rd_f12g.py: the module of the program is replaced in the capture, outputs read on the event where it is bound).
# Env: RD_CAP capture; RD_PLAN json {events: [{eid, prog, stage, cap_sha}], arms: {prog: {def, mask, mem, blend: path; sites: [[sid,
#      cid, nid, oid]]; diag_var: 'fault_buffer'|'buffers'; diag_var_id}}}; RD_OUT jsonl (one line per event, appended; events already in
#      it are skipped - resumable); RD_DIR raw dumps (only outputs with N_diff > 0 of a gate arm).
# Per event (all states by SetFrameEvent(eid-1, force) then SetFrameEvent(eid, force), as F12g):
#   pre   - state of every output at eid-1 (data: does the event write?);
#   orig  - the captured module, no replacement (data: replacement neutrality orig vs def);
#   def   - the S12 module (BuildTargetShader + ReplaceResource); def2 - the same bytes, a second build (N_null of RC2);
#   mask  - reference (a); mem - reference (b); blend - F23c bit blend (reference only); sens - values of the form-A selects
#           swapped (control: the outputs observe the sites when N(def, sens) > 0);
#   diag  - the RC4 module built here (refs_f23f.rewrite 'diag') with the counter slots at the end of the chosen storage range;
#           n_t / n_f = slot after - slot before; n_entry = invocations entering the program (positive control of the counters);
#           self-check: every output except the counter words = def.
# Outputs: PS - every bound colour target (its mip / slice), the depth target, every read-write descriptor of the stage; CS - every
#   read-write descriptor (textures: all mips and slices; buffers: the bound range; a range > 64 MiB is not read - named in the line).
# N(x, y) = units that differ: texels (texture; size = bytes / texels of the subresource) or 4-byte words (buffer); 0 when sha256 equal.
# ASCII only; exits by os._exit.
import os, sys, json, time, hashlib, traceback
sys.path.insert(0, 'C:/kyty/f287/f23f')
OUT = os.environ['RD_OUT']
DUMP = os.environ.get('RD_DIR', 'C:/kyty/f287/f23f/dump')
LOG = open(OUT + '.log', 'a')
NL = chr(10)
T0 = time.time()
BIG = 64 * 1024 * 1024
CH = 1 << 16


def P(*a):
    LOG.write(('[%7.1f] ' % (time.time() - T0)) + ' '.join(str(x) for x in a) + NL)
    LOG.flush()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rid_num(r):
    try:
        return int(str(r).split('::')[-1])
    except Exception:
        return -1


def ndiff(a, b, unit):
    if a is None or b is None or len(a) != len(b) or unit <= 0:
        return -1
    if a == b:
        return 0
    n = 0
    for i in range(0, len(a), CH):
        x, y = a[i:i + CH], b[i:i + CH]
        if x == y:
            continue
        for j in range(0, len(x), unit):
            if x[j:j + unit] != y[j:j + unit]:
                n += 1
    return n


def ndiff_except(a, b, unit, lo, hi):
    """4-byte words that differ outside the byte range [lo, hi) (the counter slots of the diag module)"""
    if a is None or b is None or len(a) != len(b):
        return -1
    return ndiff(a[:lo], b[:lo], unit) + ndiff(a[hi:], b[hi:], unit)


def main():
    import renderdoc as rd
    import refs_f23f as R
    plan = json.load(open(os.environ['RD_PLAN']))
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                done.add(json.loads(line)['eid'])
            except Exception:
                pass
    todo = sorted([e for e in plan['events'] if e['eid'] not in done], key=lambda e: e['eid'])
    P('plan events', len(plan['events']), 'done', len(done), 'todo', len(todo))
    if not todo:
        P('done'); return 0
    os.makedirs(DUMP, exist_ok=True)
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    P('capture', os.environ['RD_CAP'], 'opened')
    textures = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}
    buffers = {rid_num(b.resourceId): b for b in ctrl.GetBuffers()}
    built = {}
    arms_bytes = {}

    def arm_bytes(prog, arm):
        key = (prog, arm)
        if key not in arms_bytes:
            arms_bytes[key] = open(plan['arms'][prog][arm], 'rb').read()
        return arms_bytes[key]

    def build(prog, arm, blob, stage, entry):
        key = (prog, arm)
        if key not in built:
            nid, err = ctrl.BuildTargetShader(entry, rd.ShaderEncoding.SPIRV, blob, rd.ShaderCompileFlags(), stage)
            if nid == rd.ResourceId.Null():
                P('BUILD_FAILED', prog, arm, (err or '')[:800].replace(NL, ' | '))
                return None
            built[key] = nid
        return built[key]

    for ev in todo:
        eid, prog, stg = ev['eid'], ev['prog'], ev['stage']
        sst = rd.ShaderStage.Compute if stg == 'cs' else rd.ShaderStage.Pixel
        rec = {'eid': eid, 'prog': prog, 'stage': stg, 't_start': round(time.time() - T0, 1)}
        ctrl.SetFrameEvent(eid, True)
        ps = ctrl.GetPipelineState()
        refl = ps.GetShaderReflection(sst)
        raw = bytes(refl.rawBytes) if refl is not None else b''
        rec['bound_sha'] = sha(raw)
        rec['bound_is_capture_module'] = rec['bound_sha'] == ev['cap_sha']
        if not rec['bound_is_capture_module']:
            rec['skip'] = 'bound module is not the captured module of the program'
            open(OUT, 'a').write(json.dumps(rec, sort_keys=True) + NL)
            continue
        shid = ps.GetShader(sst)
        entry = refl.entryPoint
        rw_names = [r.name for r in refl.readWriteResources]
        outs = []   # (key, kind, res, a, b, extra)
        if stg == 'ps':
            for k, d in enumerate(ps.GetOutputTargets()):
                n = rid_num(d.resource)
                if n > 0:
                    outs.append(('rt%d' % k, 'tex', n, int(getattr(d, 'firstMip', 0)), int(getattr(d, 'firstSlice', 0)), ''))
            dt = ps.GetDepthTarget()
            n = rid_num(dt.resource)
            if n > 0:
                outs.append(('depth', 'tex', n, int(getattr(dt, 'firstMip', 0)), int(getattr(dt, 'firstSlice', 0)), ''))
        large = []
        counter_cands = []
        for u in ps.GetReadWriteResources(sst):
            d = getattr(u, 'descriptor', None)
            if d is None:
                continue
            n = rid_num(d.resource)
            if n <= 0:
                continue
            idx = int(getattr(u.access, 'index', -1))
            ae = int(getattr(u.access, 'arrayElement', 0))
            name = rw_names[idx] if 0 <= idx < len(rw_names) else '?'
            if n in textures:
                t = textures[n]
                for m in range(max(1, t.mips)):
                    for s in range(max(1, t.arraysize)):
                        outs.append(('rw_%s_%d_t%d_m%d_s%d' % (name, ae, n, m, s), 'tex', n, m, s, name))
            elif n in buffers:
                off, size = int(getattr(d, 'byteOffset', 0)), int(getattr(d, 'byteSize', 0))
                if size == 0 or size > buffers[n].length - off:
                    size = buffers[n].length - off
                if size > BIG:
                    large.append('%s[%d] buf %d off %d size %d' % (name, ae, n, off, size))
                    continue
                outs.append(('rw_%s_%d_b%d_o%d' % (name, ae, n, off), 'buf', n, off, size, name))
                counter_cands.append((name, ae, n, off, size))
        # de-duplicate (aliased views of one range)
        seen, uouts = set(), []
        for o in outs:
            k2 = (o[1], o[2], o[3], o[4])
            if k2 in seen:
                continue
            seen.add(k2)
            uouts.append(o)
        outs = uouts
        rec['outputs'] = [o[0] for o in outs]
        rec['outputs_not_read_large'] = large

        def read_all():
            stt = {}
            for key, kind, n, a, b, nm in outs:
                if kind == 'tex':
                    data = bytes(ctrl.GetTextureData(textures[n].resourceId, rd.Subresource(a, b, 0)))
                    t = textures[n]
                    mw, mh, md = max(1, t.width >> a), max(1, t.height >> a), max(1, t.depth >> a) if t.depth > 1 else 1
                    unit = len(data) // (mw * mh * md) if mw * mh * md else 0
                else:
                    data = bytes(ctrl.GetBufferData(buffers[n].resourceId, a, b))
                    unit = 4
                stt[key] = (data, unit)
            return stt

        def run_state(nid):
            if nid is not None:
                ctrl.ReplaceResource(shid, nid)
            ctrl.SetFrameEvent(eid - 1, True)
            ctrl.SetFrameEvent(eid, True)
            r2 = ctrl.GetPipelineState().GetShaderReflection(sst)
            bsha = sha(bytes(r2.rawBytes)) if r2 is not None else ''
            stt = read_all()
            if nid is not None:
                ctrl.RemoveReplacement(shid)
            return stt, bsha

        def shas(stt):
            return {k: sha(v[0])[:16] for k, v in stt.items()}

        # pre
        ctrl.SetFrameEvent(eid - 1, True)
        pre = read_all()
        rec['sha_pre'] = shas(pre)
        orig, bsha = run_state(None)
        rec['sha_orig'] = shas(orig)
        res_n = {}
        states = {}
        for arm in ('def', 'def2', 'mask', 'mem', 'blend', 'sens'):
            src = 'def' if arm == 'def2' else arm
            blob = arm_bytes(prog, src)
            nid = build(prog, arm, blob, sst, entry)
            if nid is None:
                rec['build_failed_' + arm] = True
                continue
            stt, bsha = run_state(nid)
            rec['bound_sha_' + arm] = bsha[:16]
            rec['bound_ok_' + arm] = bsha == sha(blob)
            rec['sha_' + arm] = shas(stt)
            states[arm] = stt
            if arm == 'def':
                rec['N_pre_def'] = {k: ndiff(pre[k][0], stt[k][0], stt[k][1]) for k in stt}
                rec['N_orig_def'] = {k: ndiff(orig[k][0], stt[k][0], stt[k][1]) for k in stt}
                pre = None
                orig = None
            else:
                base = states['def']
                res_n[arm] = {k: ndiff(base[k][0], stt[k][0], stt[k][1]) for k in stt}
                if arm == 'mem' and 'mask' in states:
                    res_n['mask_vs_mem'] = {k: ndiff(states['mask'][k][0], stt[k][0], stt[k][1]) for k in stt}
                if arm in ('def2', 'mask', 'mem') and any(v != 0 for v in res_n[arm].values()):
                    for k, v in res_n[arm].items():
                        if v != 0:
                            for a2 in ('def', arm):
                                open(os.path.join(DUMP, '%d_%s_%s.bin' % (eid, k, a2)), 'wb').write(states[a2][k][0])
                if arm in ('def2', 'blend', 'sens'):
                    states.pop(arm, None)
        for arm, v in res_n.items():
            rec['N_' + arm] = v
        states.pop('mem', None)
        states.pop('mask', None)
        # diag
        a = plan['arms'][prog]
        sites = [tuple(s) for s in a['sites']]
        if ev.get('no_diag'):
            rec['diag'] = 'not run: ' + ev['no_diag']
            states = None
            rec['t_end'] = round(time.time() - T0, 1)
            open(OUT, 'a').write(json.dumps(rec, sort_keys=True) + NL)
            P('event', eid, prog, 'done (no diag) in', rec['t_end'] - rec['t_start'], 's')
            continue
        # counter storage: the first of fault_buffer, buffers, shader_data, flattened_srt bound read-write at the event (the
        # largest range of that name); its variable id from the def module by OpName
        dv, cands = a['diag_var'], []
        for nm_ in ('fault_buffer', 'buffers', 'shader_data', 'flattened_srt'):
            cands = [c for c in counter_cands if c[0] == nm_]
            if cands:
                dv = nm_
                break
        dvid = R.named_var(arm_bytes(prog, 'def'), dv) if cands else None
        if cands and dvid is not None:
            c = max(cands, key=lambda x: x[4])
            name, ae, n, off, size = c
            nwords = size // 4
            if dv == 'fault_buffer':
                base_w = (8388608 // 4) - 64 - 2 * len(sites) - 1
                prefix = (0,)
            elif dv == 'buffers':
                base_w = nwords - 2 * len(sites) - 1
                prefix = (ae, 0)
            else:
                base_w = nwords - 2 * len(sites) - 1
                prefix = (0,)
            if base_w < 0:
                rec['diag'] = 'range too small: %d words for %d slots' % (nwords, 2 * len(sites) + 1)
            else:
                dblob, nd = R.rewrite(arm_bytes(prog, 'def'), sites, 'diag', diag_var=dvid, diag_base=base_w,
                                      diag_prefix=prefix)
                nid, err = ctrl.BuildTargetShader(entry, rd.ShaderEncoding.SPIRV, dblob, rd.ShaderCompileFlags(), sst)
                if nid == rd.ResourceId.Null():
                    rec['diag'] = 'build failed: ' + (err or '')[:300]
                else:
                    ckey = 'rw_%s_%d_b%d_o%d' % (name, ae, n, off)
                    lo, hi = base_w * 4, base_w * 4 + 8 * len(sites) + 4
                    ctrl.SetFrameEvent(eid - 1, True)
                    before = bytes(ctrl.GetBufferData(buffers[n].resourceId, off + lo, hi - lo))
                    stt, bsha = run_state(nid)
                    ctrl.FreeTargetResource(nid)
                    after = stt[ckey][0][lo:hi]
                    import struct as _s
                    if len(after) != hi - lo or len(before) != hi - lo:
                        rec['diag'] = 'counter range read %d / %d bytes of %d (output %s %d bytes, range size %d, base word %d)' % (
                            len(before), len(after), hi - lo, ckey, len(stt[ckey][0]), size, base_w)
                        states = None
                        rec['t_end'] = round(time.time() - T0, 1)
                        open(OUT, 'a').write(json.dumps(rec, sort_keys=True) + NL)
                        continue
                    b4 = _s.unpack('<%dI' % (2 * len(sites) + 1), before)
                    a4 = _s.unpack('<%dI' % (2 * len(sites) + 1), after)
                    cnt = [(a4[i] - b4[i]) & 0xffffffff for i in range(2 * len(sites) + 1)]
                    base = states['def']
                    selfc = {}
                    for k in stt:
                        if k == ckey:
                            selfc[k] = ndiff_except(base[k][0], stt[k][0], 4, lo, hi)
                        else:
                            selfc[k] = ndiff(base[k][0], stt[k][0], stt[k][1])
                    dc = base[ckey][0][lo:hi] if ckey in base else b''
                    rec['diag'] = {'var': dv, 'buffer': n, 'elem': ae, 'off': off, 'size': size, 'base_word': base_w, 'prefix': list(prefix),
                                   'bound_ok': bsha == sha(dblob), 'diag_sha': sha(dblob)[:16],
                                   'n_t': [cnt[2 * i] for i in range(len(sites))], 'n_f': [cnt[2 * i + 1] for i in range(len(sites))],
                                   'n_entry': cnt[2 * len(sites)],
                                   'selfcheck_N': selfc, 'def_changes_counter_words': dc != before}
        else:
            rec['diag'] = 'no read-write fault_buffer / buffers / shader_data / flattened_srt descriptor bound'
        states = None
        rec['t_end'] = round(time.time() - T0, 1)
        open(OUT, 'a').write(json.dumps(rec, sort_keys=True) + NL)
        P('event', eid, prog, 'done in', rec['t_end'] - rec['t_start'], 's')
    for nid in built.values():
        ctrl.FreeTargetResource(nid)
    P('done')
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    LOG.write(traceback.format_exc())
    LOG.flush()
LOG.close()
os._exit(code)
