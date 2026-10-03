# Track F link F14c (HPP-489; ROADMAP s122 item 400(v)(1), member (0) of F14a section 4): qrenderdoc --python rd_cmp_f14c.py
# RD_CAP=<capture> RD_OUT=<file>.  NO REPLAY: only the structured data of the capture file (CaptureFile.GetStructuredData), CPU and
# disk (form of rd_sd_f12f.py, F12f edition 2).
# From the chunks: vkCreateShaderModule (module -> sha256 and the compare sites of spv_sites_f14c.py: manual = ManualDepthCompare
# pattern, native = OpImageSampleDref*/OpImageDrefGather, each with (set, binding, index) of its image and its sampler);
# vkCreateSampler (magFilter, minFilter, mipmapMode, compareEnable, compareOp, anisotropy, pNext); vkCreateImageView (format,
# aspect, image); vkCreateImage (format); vkCreateGraphicsPipelines / vkCreateComputePipelines (pipeline -> modules);
# vkCmdBindPipeline; vkCmdPushDescriptorSet[KHR] (per command buffer, bind point, set: binding/element -> descriptor, accumulated
# within the command buffer; 'fresh' = written by the last push call before the draw, 'carry' = by an earlier one);
# vkUpdateDescriptorSets + vkCmdBindDescriptorSets (set contents: every write of the capture to that element is kept; 'set1' = all
# writes agree, 'setN' = they differ - the last write before the draw chunk is used and the row is flagged);
# a push to set index s drops the set bound at s and a bind of s drops the push state of s; vkBeginCommandBuffer resets the state of its command buffer; every vkCmdDraw* / vkCmdDispatch* chunk with a bound pipeline whose
# modules carry compare sites gives one record per site: sampler state of the sampler binding and view format of the image binding.
# Output lines: MODULE (modules with sites), PIPE, AGG, TYPES (descriptor types of the image and sampler bindings per record) (aggregate per module/site/sampler/view), DRAWX (first 3 records per AGG key),
# UNRES (records whose descriptor is not in the structured data, with the reason), SUMMARY, done.  DATA ONLY.  ASCII only.
import os, sys, traceback, hashlib
sys.path.insert(0, 'C:/kyty/f287/f14c')
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f14c/rd_cmp.txt')
out = open(OUT, 'w')
NL = chr(10)


def child(o, *names):
    for n in names:
        c = o.FindChild(n)
        if c is not None:
            return c
    return None


def rid(o):
    try:
        return str(o.AsResourceId()) if o is not None else None
    except Exception:
        return None


def s_(o):
    if o is None:
        return '-'
    try:
        v = o.AsString()
        if v:
            return v
    except Exception:
        pass
    try:
        return str(o.AsInt())
    except Exception:
        pass
    try:
        return '%g' % o.AsFloat()
    except Exception:
        return '?'


def i_(o):
    try:
        return o.AsInt()
    except Exception:
        return None


def arr(o):
    if o is None:
        return []
    return [o.GetChild(i) for i in range(o.NumChildren())]


def code_bytes(sdf, info):
    import renderdoc as rd
    pc = child(info, 'pCode')
    if pc is None:
        return None
    if pc.type.basetype == rd.SDBasic.Buffer:
        return bytes(sdf.buffers[pc.data.basic.u])
    if pc.type.basetype == rd.SDBasic.Array:
        vals = [pc.GetChild(i).AsInt() for i in range(pc.NumChildren())]
        bw = pc.GetChild(0).type.byteSize if pc.NumChildren() else 4
        return b''.join(int(v & ((1 << (8 * bw)) - 1)).to_bytes(bw, 'little') for v in vals)
    return None


def writes_of(lst):
    """VkWriteDescriptorSet array -> list of (dstSet, binding, element, type, sampler, view)"""
    res = []
    for w in arr(lst):
        ds = rid(child(w, 'dstSet'))
        b = i_(child(w, 'dstBinding'))
        e0 = i_(child(w, 'dstArrayElement')) or 0
        t = s_(child(w, 'descriptorType'))
        ii = arr(child(w, 'pImageInfo'))
        for k, inf in enumerate(ii):
            res.append((ds, b, e0 + k, t, rid(child(inf, 'sampler')), rid(child(inf, 'imageView'))))
    return res


def main():
    import renderdoc as rd
    import spv_sites_f14c as S
    cap = rd.OpenCaptureFile()
    st = cap.OpenFile(os.environ['RD_CAP'], '', None)
    if st != rd.ResultCode.Succeeded:
        out.write('open failed %s' % st + NL); return 1
    sdf = cap.GetStructuredData()
    out.write('capture %s' % os.environ['RD_CAP'] + NL)
    out.write('chunks %d buffers %d' % (len(sdf.chunks), len(sdf.buffers)) + NL)
    modules = {}      # module rid -> (sha, sites)
    samplers = {}     # sampler rid -> tuple
    views = {}        # view rid -> (format, aspect, image)
    images = {}       # image rid -> format
    pipes = {}        # pipeline rid -> [(stage, module rid)]
    bound = {}        # (cb, bp) -> pipeline
    push = {}         # (cb, bp, set) -> {(binding, elem): (type, sampler, view, push_no)}
    push_no = {}      # (cb, bp, set) -> number of the last push call
    setw = {}         # set rid -> {(binding, elem): [(chunk, type, sampler, view)]}
    bsets = {}        # (cb, bp, set index) -> set rid
    agg = {}
    types = {}
    drawx = {}
    unres = {}
    n_draw_cmp = 0
    n_draw = 0
    n_copies = 0
    first_modules = []
    for ci, ch in enumerate(sdf.chunks):
        nm = ch.name
        if nm == 'vkCreateShaderModule':
            info = child(ch, 'CreateInfo', 'pCreateInfo')
            mid = rid(child(ch, 'ShaderModule', 'pShaderModule'))
            if info is None or mid is None:
                continue
            b = code_bytes(sdf, info)
            if b is None:
                out.write('MODULE_UNREAD %s' % mid + NL); continue
            sites, err = S.sites(b)
            sha = hashlib.sha256(b).hexdigest()
            modules[mid] = (sha, sites)
            if sites:
                nm_ = sum(1 for s in sites if s['kind'] == 'manual')
                nn_ = sum(1 for s in sites if s['kind'] == 'native')
                keys = {}
                for s in sites:
                    keys[S.key(s)] = keys.get(S.key(s), 0) + 1
                out.write('MODULE %s sha=%s bytes=%d manual=%d native=%d sites=%s' % (
                    mid, sha, len(b), nm_, nn_, ';'.join('%s x%d' % kv for kv in sorted(keys.items()))) + NL)
        elif nm == 'vkCreateSampler':
            info = child(ch, 'CreateInfo', 'pCreateInfo')
            sid = rid(child(ch, 'Sampler', 'pSampler'))
            if info is None or sid is None:
                continue
            samplers[sid] = (s_(child(info, 'magFilter')), s_(child(info, 'minFilter')), s_(child(info, 'mipmapMode')),
                             s_(child(info, 'compareEnable')), s_(child(info, 'compareOp')), s_(child(info, 'anisotropyEnable')),
                             s_(child(info, 'maxAnisotropy')), s_(child(info, 'pNextType')))
        elif nm == 'vkCreateImageView':
            info = child(ch, 'CreateInfo', 'pCreateInfo')
            vid = rid(child(ch, 'View', 'pView'))
            if info is None or vid is None:
                continue
            sr = child(info, 'subresourceRange')
            views[vid] = (s_(child(info, 'format')), s_(child(sr, 'aspectMask')) if sr is not None else '-',
                          rid(child(info, 'image')))
        elif nm == 'vkCreateImage':
            info = child(ch, 'CreateInfo', 'pCreateInfo')
            iid = rid(child(ch, 'Image', 'pImage'))
            if info is None or iid is None:
                continue
            images[iid] = s_(child(info, 'format'))
        elif nm in ('vkCreateGraphicsPipelines', 'vkCreateComputePipelines'):
            infos = child(ch, 'CreateInfo', 'pCreateInfos')
            pids = child(ch, 'Pipeline', 'pPipelines')
            if infos is None or pids is None:
                continue
            il = arr(infos) if infos.type.basetype == rd.SDBasic.Array else [infos]
            pl = arr(pids) if pids.type.basetype == rd.SDBasic.Array else [pids]
            for info, pid in zip(il, pl):
                mods = []
                if nm == 'vkCreateComputePipelines':
                    stg = child(info, 'stage')
                    if stg is not None:
                        mods.append(('CS', rid(child(stg, 'module'))))
                else:
                    for stg in arr(child(info, 'pStages')):
                        mods.append((s_(child(stg, 'stage')).replace('VK_SHADER_STAGE_', '').replace('_BIT', '').replace('_EXT', ''),
                                     rid(child(stg, 'module'))))
                pipes[rid(pid)] = mods
        elif nm == 'vkBeginCommandBuffer':
            cb = rid(child(ch, 'commandBuffer'))
            for d in (bound, bsets):
                for k in [k for k in d if k[0] == cb]:
                    del d[k]
            for k in [k for k in push if k[0] == cb]:
                del push[k]
        elif nm == 'vkCmdBindPipeline':
            bound[(rid(child(ch, 'commandBuffer')), i_(child(ch, 'pipelineBindPoint')))] = rid(child(ch, 'pipeline'))
        elif nm in ('vkCmdPushDescriptorSet', 'vkCmdPushDescriptorSetKHR'):
            k = (rid(child(ch, 'commandBuffer')), i_(child(ch, 'pipelineBindPoint')), i_(child(ch, 'set')))
            push_no[k] = push_no.get(k, 0) + 1
            bsets.pop(k, None)  # a push to a set index disturbs the set bound there (and the reverse below)
            d = push.setdefault(k, {})
            for (_, b, e, t, smp, vw) in writes_of(child(ch, 'pDescriptorWrites')):
                d[(b, e)] = (t, smp, vw, push_no[k])
        elif nm == 'vkUpdateDescriptorSets':
            for (ds, b, e, t, smp, vw) in writes_of(child(ch, 'pDescriptorWrites')):
                setw.setdefault(ds, {}).setdefault((b, e), []).append((ci, t, smp, vw))
            n_copies += len(arr(child(ch, 'pDescriptorCopies')))
        elif nm == 'vkCmdBindDescriptorSets':
            cb = rid(child(ch, 'commandBuffer'))
            bp = i_(child(ch, 'pipelineBindPoint'))
            fs = i_(child(ch, 'firstSet')) or 0
            for k, ds in enumerate(arr(child(ch, 'pDescriptorSets'))):
                bsets[(cb, bp, fs + k)] = rid(ds)
                push.pop((cb, bp, fs + k), None)
        elif nm.startswith('vkCmdDraw') or nm.startswith('vkCmdDispatch'):
            n_draw += 1
            cb = rid(child(ch, 'commandBuffer'))
            bp = 1 if nm.startswith('vkCmdDispatch') else 0
            p = bound.get((cb, bp))
            mods = pipes.get(p, [])
            hit = False
            for stage, m in mods:
                sha, sites = modules.get(m, (None, []))
                for s in sites:
                    hit = True

                    def look(t):
                        if t is None or t[0] is None or t[1] is None or t[2] == 'dyn':
                            return None, 'site-unresolved'
                        kk = (cb, bp, t[0])
                        if kk in push and (t[1], t[2]) in push[kk]:
                            v = push[kk][(t[1], t[2])]
                            return (v[0], v[1], v[2]), 'fresh' if v[3] == push_no.get(kk) else 'carry'
                        ds = bsets.get((cb, bp, t[0]))
                        if ds is None:
                            return None, 'no-push-no-set'
                        wl = setw.get(ds, {}).get((t[1], t[2]))
                        if not wl:
                            return None, 'set-not-written-in-capture'
                        before = [w for w in wl if w[0] < ci]
                        w = before[-1] if before else wl[-1]
                        same = len(set((x[2], x[3]) for x in wl)) == 1
                        return (w[1], w[2], w[3]), 'set1' if same else 'setN'
                    di, wi = look(s['img'])
                    ds_, ws = look(s['smp'])
                    if di is None or ds_ is None:
                        rk = (stage, sha[:16] if sha else '-', S.key(s), wi if di is None else 'img-ok', ws if ds_ is None else 'smp-ok')
                        unres[rk] = unres.get(rk, 0) + 1
                        continue
                    smp = samplers.get(ds_[1], ('?',) * 8) if ds_[1] not in (None, 'ResourceId::0') else ('null',) * 8
                    vw = views.get(di[2], ('?', '?', None)) if di[2] not in (None, 'ResourceId::0') else ('null', 'null', None)
                    ifmt = images.get(vw[2], '?') if vw[2] else '-'
                    ak = (stage, sha[:16], S.key(s), s['img_depth'], smp[0], smp[1], smp[2], smp[3], smp[4], smp[5], smp[7],
                          vw[0], vw[1], ifmt, wi + '/' + ws)
                    agg[ak] = agg.get(ak, 0) + 1
                    tk = (s['kind'], di[0], ds_[0])
                    types[tk] = types.get(tk, 0) + 1
                    if drawx.get(ak, 0) < 3:
                        drawx[ak] = drawx.get(ak, 0) + 1
                        out.write('DRAWX chunk=%d call=%s cb=%s pipe=%s stage=%s mod=%s site=%s sampler=%s view=%s' % (
                            ci, nm, cb, p, stage, sha[:16], S.key(s), ds_[1], di[2]) + NL)
            if hit:
                n_draw_cmp += 1
    for p, mods in sorted(pipes.items()):
        ms = [(st_, m) for st_, m in mods if modules.get(m, (None, []))[1]]
        if ms:
            out.write('PIPE %s %s' % (p, ' '.join('%s:%s:%s' % (st_, m, modules[m][0][:16]) for st_, m in ms)) + NL)
    for ak in sorted(agg):
        out.write('AGG stage=%s mod=%s site=%s depthflag=%s mag=%s min=%s mip=%s cmpEnable=%s cmpOp=%s aniso=%s smp_pnext=%s '
                  'view_format=%s aspect=%s image_format=%s src=%s n=%d' % (ak + (agg[ak],)) + NL)
    for tk in sorted(types):
        out.write('TYPES kind=%s img_descriptor=%s smp_descriptor=%s n=%d' % (tk + (types[tk],)) + NL)
    for rk in sorted(unres):
        out.write('UNRES stage=%s mod=%s site=%s img=%s smp=%s n=%d' % (rk + (unres[rk],)) + NL)
    nmods = sum(1 for v in modules.values() if v[1])
    out.write('SUMMARY draws_dispatches %d with_compare_sites %d modules %d modules_with_sites %d samplers %d views %d '
              'pipelines %d agg_rows %d records %d unresolved %d descriptor_copies %d' % (
                  n_draw, n_draw_cmp, len(modules), nmods, len(samplers), len(views), len(pipes), len(agg),
                  sum(agg.values()), sum(unres.values()), n_copies) + NL)
    out.write('done' + NL)
    cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    out.write(traceback.format_exc())
out.close()
os._exit(code)
