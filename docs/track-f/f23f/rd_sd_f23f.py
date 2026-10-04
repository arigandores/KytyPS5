# F23f (HPP-592; ROADMAP s122 item 498(g)(2)(a)): qrenderdoc --python rd_sd_f23f.py
# RD_CAP=<capture> RD_OUT=<file> RD_MARK=<sha256=name,...>.  Copy of F12f rd_sd_f12f.py (no replay: CaptureFile.GetStructuredData,
# CPU and disk only) extended to graphics pipelines: vkCreateShaderModule (module -> sha256), vkCreateComputePipelines and
# vkCreateGraphicsPipelines (pipeline -> module per stage; graphics: colour blend attachments blendEnable / colorWriteMask, dynamic
# states, depth test / write), vkCmdBindPipeline (command buffer x bind point -> pipeline), vkCmdDispatch* / vkCmdDraw* (the module of
# the bound pipeline; for draws the fragment-stage module).  Prints MODULE, PIPE (only pipelines whose module is marked), every
# marked action 'ACT chunk=<i> call=<name> cb=<cmdbuf> stage=<cs|ps> sha=<sha> name=<mark name> pipe=<id>', per marked sha the count,
# 'SUMMARY ...', 'done'.  Event ids need the replay (next step).  DATA ONLY.  ASCII only.  Exits by os._exit.
import os, traceback, hashlib
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f23f/rd_sd.txt')
MARK = {}
for x in os.environ.get('RD_MARK', '').split(','):
    if '=' in x:
        s, n = x.split('=', 1)
        MARK[s.strip().lower()] = n.strip()
out = open(OUT, 'w')
NL = chr(10)
DISPATCH = ('vkCmdDispatch', 'vkCmdDispatchIndirect', 'vkCmdDispatchBase', 'vkCmdDispatchBaseKHR')
DRAW = ('vkCmdDraw', 'vkCmdDrawIndexed', 'vkCmdDrawIndirect', 'vkCmdDrawIndexedIndirect', 'vkCmdDrawIndirectCount',
        'vkCmdDrawIndexedIndirectCount', 'vkCmdDrawIndirectCountKHR', 'vkCmdDrawIndexedIndirectCountKHR',
        'vkCmdDrawMeshTasksEXT', 'vkCmdDrawMeshTasksIndirectEXT', 'vkCmdDrawMeshTasksIndirectCountEXT')
FRAG = 0x10
COMP = 0x20


def child(o, *names):
    if o is None:
        return None
    for n in names:
        c = o.FindChild(n)
        if c is not None:
            return c
    return None


def rid(o):
    try:
        return str(o.AsResourceId())
    except Exception:
        return None


def names(o):
    return [o.GetChild(i).name for i in range(o.NumChildren())]


def ival(o, default=-1):
    try:
        return int(o.AsInt())
    except Exception:
        try:
            return int(o.AsUInt())
        except Exception:
            return default


def arr(o):
    import renderdoc as rd
    if o is None:
        return []
    if o.type.basetype == rd.SDBasic.Array:
        return [o.GetChild(i) for i in range(o.NumChildren())]
    return [o]


def code_bytes(sdf, info):
    import renderdoc as rd
    pc = child(info, 'pCode')
    if pc is None:
        return None, 'no pCode in %s' % names(info)
    if pc.type.basetype == rd.SDBasic.Buffer:
        return bytes(sdf.buffers[pc.data.basic.u]), 'buffer'
    if pc.type.basetype == rd.SDBasic.Array:
        vals = [pc.GetChild(i).AsInt() for i in range(pc.NumChildren())]
        bw = pc.GetChild(0).type.byteSize if pc.NumChildren() else 4
        return b''.join(int(v & ((1 << (8 * bw)) - 1)).to_bytes(bw, 'little') for v in vals), 'array%d' % bw
    return None, 'pCode basetype %s' % pc.type.basetype


def gfx_state(info):
    """blend attachments, dynamic states, depth test/write of VkGraphicsPipelineCreateInfo (as text)."""
    parts = []
    cb = child(info, 'pColorBlendState')
    att = arr(child(cb, 'pAttachments')) if cb is not None else []
    parts.append('blend=[%s]' % ';'.join('%d/%x' % (ival(child(a, 'blendEnable')), ival(child(a, 'colorWriteMask')))
                                         for a in att))
    ds = child(info, 'pDynamicState')
    dyn = [ival(d) for d in arr(child(ds, 'pDynamicStates'))] if ds is not None else []
    parts.append('dyn=[%s]' % ','.join(str(d) for d in dyn))
    dss = child(info, 'pDepthStencilState')
    if dss is not None:
        parts.append('depth=%d/%d' % (ival(child(dss, 'depthTestEnable')), ival(child(dss, 'depthWriteEnable'))))
    return ' '.join(parts)


def main():
    import renderdoc as rd
    cap = rd.OpenCaptureFile()
    st = cap.OpenFile(os.environ['RD_CAP'], '', None)
    if st != rd.ResultCode.Succeeded:
        out.write('open failed %s' % st + NL); return 1
    sdf = cap.GetStructuredData()
    out.write('capture %s' % os.environ['RD_CAP'] + NL)
    out.write('mark %s' % ','.join('%s=%s' % (k, v) for k, v in sorted(MARK.items())) + NL)
    out.write('chunks %d buffers %d' % (len(sdf.chunks), len(sdf.buffers)) + NL)
    modules, pipes, bound = {}, {}, {}
    acts = []
    first = set()
    other_dyn = {}
    for ci, ch in enumerate(sdf.chunks):
        nm = ch.name
        if nm == 'vkCreateShaderModule':
            info = child(ch, 'CreateInfo', 'pCreateInfo')
            mid = child(ch, 'ShaderModule', 'pShaderModule')
            if info is None or mid is None:
                continue
            b, how = code_bytes(sdf, info)
            if b is None:
                out.write('MODULE %s unread: %s' % (rid(mid), how) + NL); continue
            sha = hashlib.sha256(b).hexdigest()
            modules[rid(mid)] = (sha, len(b))
            if sha in MARK:
                out.write('MODULE %s sha=%s bytes=%d name=%s' % (rid(mid), sha, len(b), MARK[sha]) + NL)
        elif nm in ('vkCreateComputePipelines', 'vkCreateGraphicsPipelines'):
            if nm not in first:
                first.add(nm); out.write('FIRST %s children %s' % (nm, names(ch)) + NL)
            infos = arr(child(ch, 'CreateInfo', 'pCreateInfos'))
            pids = arr(child(ch, 'Pipeline', 'pPipelines'))
            for info, pid in zip(infos, pids):
                if nm == 'vkCreateComputePipelines':
                    mod = child(child(info, 'stage'), 'module')
                    pipes[rid(pid)] = ('cs', rid(mod), '')
                else:
                    fm = None
                    for sg in arr(child(info, 'pStages')):
                        if ival(child(sg, 'stage')) & FRAG:
                            fm = rid(child(sg, 'module'))
                    pipes[rid(pid)] = ('ps', fm, gfx_state(info))
                    if 'gfxinfo' not in first:
                        first.add('gfxinfo'); out.write('FIRST graphics CreateInfo children %s' % names(info) + NL)
                p = pipes[rid(pid)]
                sha = modules.get(p[1], ('unknown', 0))[0]
                if sha in MARK:
                    out.write('PIPE %s stage=%s module=%s name=%s %s' % (rid(pid), p[0], p[1], MARK[sha], p[2]) + NL)
        elif nm == 'vkCmdBindPipeline':
            bp = ival(child(ch, 'pipelineBindPoint'))
            bound[(rid(child(ch, 'commandBuffer')), bp)] = rid(child(ch, 'pipeline'))
        elif nm in DISPATCH or nm in DRAW:
            cb = rid(child(ch, 'commandBuffer'))
            p = bound.get((cb, 1 if nm in DISPATCH else 0))
            pi = pipes.get(p)
            sha = modules.get(pi[1], ('unknown', 0))[0] if pi else 'unknown'
            if sha in MARK:
                acts.append((ci, nm, cb, pi[0], sha, p))
        elif nm.startswith('vkCmdSet') and ('Blend' in nm or 'ColorWrite' in nm or 'Depth' in nm):
            other_dyn[nm] = other_dyn.get(nm, 0) + 1
    cnt = {}
    for ci, nm, cb, stg, sha, p in acts:
        cnt[sha] = cnt.get(sha, 0) + 1
        out.write('ACT chunk=%d call=%s cb=%s stage=%s sha=%s name=%s pipe=%s' % (ci, nm, cb, stg, sha, MARK[sha], p) + NL)
    for sha in sorted(MARK):
        out.write('COUNT name=%s sha=%s actions=%d module_present=%d' % (
            MARK[sha], sha, cnt.get(sha, 0), sum(1 for s, _ in modules.values() if s == sha)) + NL)
    out.write('DYNSET %s' % ','.join('%s:%d' % kv for kv in sorted(other_dyn.items())) + NL)
    out.write('SUMMARY modules %d pipelines %d marked_actions %d' % (len(modules), len(pipes), len(acts)) + NL)
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
