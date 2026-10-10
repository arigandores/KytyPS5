# F36a (HPP-758; ROADMAP s122 item 687(e)(1)-(2)): qrenderdoc --python rd_f36a.py - replay of the events of the PS
# be4c35a2031fd3f4 in one capture with the arms of the FS11 translation (method of section 0 of docs/track-f/f36a.md).
# Env: RD_CAP capture; RD_EV json list [{eid, exec_no, PSInvocations, SamplesPassed}]; RD_OUT jsonl (one line per event, appended;
#      events already in it are skipped - resumable).
# Per arm (order orig, def, mask, mem, sens, diag, orig2): replacement of the PS module (BuildTargetShader + ReplaceResource;
# none for orig / orig2), SetFrameEvent(pre_eid, force) -> read every output (state BEFORE the event under the same replacement;
# pre_eid = (first event of the action's event group) - 1: an indirect draw's group is [bind, 'Indirect sub-command', draw] and
# the sub-command = eid - 1 already executes the draw - runs/dbg_46220.txt; correction of section 0.8 of f36a.md),
# SetFrameEvent(eid, force) -> sha of the bound PS module (must be the arm's bytes) and read every output (state AFTER), then
# RemoveReplacement + FreeTargetResource.  Outputs: every bound colour target (its mip / slice), the depth-stencil target, every
# read-write descriptor of the PS (textures: all mips / slices; buffers: the bound range, > 64 MiB not read - named).
# Printed: Npre_<arm> = N(orig before, arm before) (G1); N_null = N(orig after, orig2 after); N_diff = N(def, mask) and N(def, mem);
# N_mask_mem; sens = N(def after, sens after) (G4); writes = N(orig before, orig after); N_orig_def (reference only: the captured
# module is the pre-F19 translation).  Counters (diag): the RC4 module of refs_f23f.rewrite on the FS11 def at the three sites, slots
# at the end of the largest read-write 'buffers' range bound at the event; n = (slot after) - (slot before), BOTH read under the
# diag replacement (atomics only add: the difference holds only this event's executions); n_entry vs PSInvocations of the event
# (G2); self-check = every output except the slot words = def after.  Bound samplers (compare enable / function) are printed.
# N(x, y) = units that differ: texels (size = bytes / texels of the subresource) or 4-byte words (buffer); 0 when sha256 equal.
# ASCII only; exits by os._exit.
import os, sys, json, time, hashlib, struct, traceback
sys.path.insert(0, 'C:/kyty/f287/f23f')
OUT = os.environ['RD_OUT']
LOGF = open(OUT + '.log', 'a')
NL = chr(10)
T0 = time.time()
BIG = 64 * 1024 * 1024
CH = 1 << 16
A = 'C:/kyty/f287/f36a/arms/ps_be4c35a2031fd3f4_%s.spv'
CAP_SHA = 'ebff0feeb90b9b35c7aecbd6fc542fb6ded352504b70442b9172f533a571cb96'
ARMS = os.environ.get('RD_ARMS', 'orig,def,mask,mem,sens,diag,orig2').split(',')


def P(*a):
    LOGF.write(('[%7.1f] ' % (time.time() - T0)) + ' '.join(str(x) for x in a) + NL)
    LOGF.flush()


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


def NS(x, y, skip=None):
    """per output N; skip = (key, lo, hi) byte range excluded (counter slots)"""
    out = {}
    for k in x:
        a, u = x[k]
        b = y[k][0]
        if skip is not None and k == skip[0]:
            lo, hi = skip[1], skip[2]
            out[k] = -1 if len(a) != len(b) else ndiff(a[:lo], b[:lo], 4) + ndiff(a[hi:], b[hi:], 4)
        else:
            out[k] = ndiff(a, b, u)
    return out


def tot(d):
    if any(v < 0 for v in d.values()):
        return -1
    return sum(d.values())


def main():
    import renderdoc as rd
    import refs_f23f as R
    evs = json.loads(os.environ['RD_EV'])
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                done.add(json.loads(line)['eid'])
            except Exception:
                pass
    todo = [e for e in evs if e['eid'] not in done]
    P('events', len(evs), 'done', len(done), 'todo', len(todo), 'arms', ARMS)
    if not todo:
        P('done'); return 0
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    P('opened', os.environ['RD_CAP'])
    grp = {}

    def walk(al):
        for a in al:
            evl = [e.eventId for e in a.events]
            for e in evl + [a.eventId]:
                grp[e] = (min(evl + [a.eventId]), evl)
            walk(a.children)
    walk(ctrl.GetRootActions())
    tex = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}
    buf = {rid_num(b.resourceId): b for b in ctrl.GetBuffers()}
    blobs = {a: open(A % a, 'rb').read() for a in ('def', 'mask', 'mem', 'sens')}
    sites = [tuple(s) for s in json.load(open('C:/kyty/f287/f36a/arms_f36a.json'))['sites']]
    sst = rd.ShaderStage.Pixel
    for ev in sorted(todo, key=lambda e: e['eid']):
        eid = ev['eid']
        r = {'eid': eid, 'exec_no': ev['exec_no'], 'PSInvocations': ev['PSInvocations'], 'SamplesPassed': ev['SamplesPassed'],
             't_start': round(time.time() - T0, 1), 'cap': os.path.basename(os.environ['RD_CAP'])}
        first, evl = grp[eid]
        pre_eid = first - 1
        r['pre_eid'], r['group_events'] = pre_eid, evl
        ctrl.SetFrameEvent(eid, True)
        ps = ctrl.GetPipelineState()
        refl = ps.GetShaderReflection(sst)
        r['bound_sha'] = sha(bytes(refl.rawBytes))
        r['bound_is_cap'] = r['bound_sha'] == CAP_SHA
        if not r['bound_is_cap']:
            r['skip'] = 'bound module is not the captured module'
            open(OUT, 'a').write(json.dumps(r, sort_keys=True) + NL)
            continue
        shid = ps.GetShader(sst)
        entry = refl.entryPoint
        rw_names = [x.name for x in refl.readWriteResources]
        outs, cands, large = [], [], []
        for k, d in enumerate(ps.GetOutputTargets()):
            n = rid_num(d.resource)
            if n > 0:
                outs.append(('rt%d' % k, 'tex', n, int(getattr(d, 'firstMip', 0)), int(getattr(d, 'firstSlice', 0))))
        dt = ps.GetDepthTarget()
        if rid_num(dt.resource) > 0:
            outs.append(('depth', 'tex', rid_num(dt.resource), int(getattr(dt, 'firstMip', 0)), int(getattr(dt, 'firstSlice', 0))))
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
            if n in tex:
                t = tex[n]
                for m in range(max(1, t.mips)):
                    for s in range(max(1, t.arraysize)):
                        outs.append(('rw_%s_%d_t%d_m%d_s%d' % (name, ae, n, m, s), 'tex', n, m, s))
            elif n in buf:
                off, size = int(getattr(d, 'byteOffset', 0)), int(getattr(d, 'byteSize', 0))
                if size == 0 or size > buf[n].length - off:
                    size = buf[n].length - off
                if size > BIG:
                    large.append('%s[%d] buf %d off %d size %d' % (name, ae, n, off, size))
                    continue
                outs.append(('rw_%s_%d_b%d_o%d' % (name, ae, n, off), 'buf', n, off, size))
                cands.append((name, ae, n, off, size))
        seen, uo = set(), []
        for o in outs:
            if o[1:] not in seen:
                seen.add(o[1:]); uo.append(o)
        outs = uo
        r['outputs'] = [o[0] for o in outs]
        r['outputs_not_read_large'] = large
        try:
            sm = []
            for u in ps.GetSamplers(sst):
                d = getattr(u, 'descriptor', None)
                if d is None:
                    continue
                sm.append({'cmp': str(getattr(d, 'compareFunction', '?')).split('.')[-1],
                           'use_cmp': bool(d.UseComparison()) if hasattr(d, 'UseComparison') else None})
            r['samplers'] = sm
        except Exception as e:
            r['samplers'] = 'error %s' % e

        def read():
            s = {}
            for key, kind, n, a, b in outs:
                if kind == 'tex':
                    data = bytes(ctrl.GetTextureData(tex[n].resourceId, rd.Subresource(a, b, 0)))
                    t = tex[n]
                    px = max(1, t.width >> a) * max(1, t.height >> a) * (max(1, t.depth >> a) if t.depth > 1 else 1)
                    s[key] = (data, len(data) // px if px else 0)
                else:
                    s[key] = (bytes(ctrl.GetBufferData(buf[n].resourceId, a, b)), 4)
            return s

        # counter module for this event
        dvid = R.named_var(blobs['def'], 'buffers')
        bc = [c for c in cands if c[0] == 'buffers']
        diag = None
        if 'diag' in ARMS:
            if dvid is None or not bc:
                r['diag'] = 'no read-write buffers descriptor / variable'
            else:
                name, ae, n, off, size = max(bc, key=lambda x: x[4])
                base_w = size // 4 - 2 * len(sites) - 1
                dblob, nd = R.rewrite(blobs['def'], sites, 'diag', diag_var=dvid, diag_base=base_w, diag_prefix=(ae, 0))
                ckey = 'rw_%s_%d_b%d_o%d' % (name, ae, n, off)
                lo, hi = base_w * 4, base_w * 4 + 8 * len(sites) + 4
                diag = (dblob, ckey, lo, hi)
                r['diag'] = {'buffer': n, 'elem': ae, 'off': off, 'size': size, 'base_word': base_w, 'diag_sha': sha(dblob)[:16],
                             'rewritten': nd}
        keep = {}
        for arm in ARMS:
            nid = None
            if arm in ('orig', 'orig2'):
                blob = None
            elif arm == 'diag':
                if diag is None:
                    continue
                blob = diag[0]
            else:
                blob = blobs[arm]
            if blob is not None:
                nid, err = ctrl.BuildTargetShader(entry, rd.ShaderEncoding.SPIRV, blob, rd.ShaderCompileFlags(), sst)
                if nid == rd.ResourceId.Null():
                    r['build_failed_' + arm] = (err or '')[:300]
                    continue
                ctrl.ReplaceResource(shid, nid)
            ctrl.SetFrameEvent(pre_eid, True)
            pre = read()
            ctrl.SetFrameEvent(eid, True)
            bsha = sha(bytes(ctrl.GetPipelineState().GetShaderReflection(sst).rawBytes))
            post = read()
            if nid is not None:
                ctrl.RemoveReplacement(shid)
                ctrl.FreeTargetResource(nid)
            r['bound_ok_' + arm] = bsha == (CAP_SHA if blob is None else sha(blob))
            r['units'] = {k: v[1] for k, v in post.items()}
            r['sha_post_' + arm] = {k: sha(v[0])[:16] for k, v in post.items()}
            if arm == 'orig':
                keep['orig_pre'], keep['orig_post'] = pre, post
                r['writes'] = NS(pre, post)
            else:
                if arm == 'diag':
                    skip = (diag[1], diag[2], diag[3])
                    r['Npre_diag'] = NS(keep['orig_pre'], pre, skip)
                    b4 = struct.unpack('<%dI' % (2 * len(sites) + 1), pre[diag[1]][0][diag[2]:diag[3]])
                    a4 = struct.unpack('<%dI' % (2 * len(sites) + 1), post[diag[1]][0][diag[2]:diag[3]])
                    cnt = [(a4[i] - b4[i]) & 0xffffffff for i in range(len(b4))]
                    r['n_t'] = [cnt[2 * i] for i in range(len(sites))]
                    r['n_f'] = [cnt[2 * i + 1] for i in range(len(sites))]
                    r['n_entry'] = cnt[2 * len(sites)]
                    r['selfcheck'] = NS(keep['def'], post, skip)
                    r['slots_before_nonzero_vs_orig'] = pre[diag[1]][0][diag[2]:diag[3]] != keep['orig_pre'][diag[1]][0][diag[2]:diag[3]]
                else:
                    r['Npre_' + arm] = NS(keep['orig_pre'], pre)
                if arm == 'orig2':
                    r['N_null'] = NS(keep['orig_post'], post)
                elif arm == 'def':
                    keep['def'] = post
                    r['N_orig_def'] = NS(keep['orig_post'], post)
                    r['writes_def'] = NS(pre, post)
                elif arm == 'mask':
                    keep['mask'] = post
                    r['N_diff_mask'] = NS(keep['def'], post)
                elif arm == 'mem':
                    r['N_diff_mem'] = NS(keep['def'], post)
                    if 'mask' in keep:
                        r['N_mask_mem'] = NS(keep.pop('mask'), post)
                elif arm == 'sens':
                    r['sens'] = NS(keep['def'], post)
            pre = post = None
            P('event', eid, 'arm', arm, 'done')
        keep = None
        r['t_end'] = round(time.time() - T0, 1)
        open(OUT, 'a').write(json.dumps(r, sort_keys=True) + NL)
        P('event', eid, 'written in', round(r['t_end'] - r['t_start'], 1), 's')
    P('done')
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    LOGF.write(traceback.format_exc())
    LOGF.flush()
LOGF.close()
os._exit(code)
