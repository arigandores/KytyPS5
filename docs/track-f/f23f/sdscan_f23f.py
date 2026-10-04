# F23f (HPP-592): structured-data scan shared by the replay scripts (the logic of rd_sd_f23f.py as a function, applied to the
# REPLAY controller's structured file - its chunk indices are those of the replay's action events; the CaptureFile structured
# data numbers chunks differently on f12_rd_k05, see runs/dbg_k05.txt).  scan(sdf, marks) -> list of (chunk, call, stage, sha, name).
import hashlib
DISPATCH = ('vkCmdDispatch', 'vkCmdDispatchIndirect', 'vkCmdDispatchBase', 'vkCmdDispatchBaseKHR')
DRAW = ('vkCmdDraw', 'vkCmdDrawIndexed', 'vkCmdDrawIndirect', 'vkCmdDrawIndexedIndirect', 'vkCmdDrawIndirectCount',
        'vkCmdDrawIndexedIndirectCount', 'vkCmdDrawIndirectCountKHR', 'vkCmdDrawIndexedIndirectCountKHR',
        'vkCmdDrawMeshTasksEXT', 'vkCmdDrawMeshTasksIndirectEXT', 'vkCmdDrawMeshTasksIndirectCountEXT')
FRAG = 0x10


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
        return None
    if pc.type.basetype == rd.SDBasic.Buffer:
        return bytes(sdf.buffers[pc.data.basic.u])
    if pc.type.basetype == rd.SDBasic.Array:
        vals = [pc.GetChild(i).AsInt() for i in range(pc.NumChildren())]
        bw = pc.GetChild(0).type.byteSize if pc.NumChildren() else 4
        return b''.join(int(v & ((1 << (8 * bw)) - 1)).to_bytes(bw, 'little') for v in vals)
    return None


def code_bytes_safe(sdf, info):
    try:
        return code_bytes(sdf, info)
    except Exception:
        return None


def scan(sdf, marks):
    modules, pipes, bound = {}, {}, {}
    acts = []
    for ci, ch in enumerate(sdf.chunks):
        nm = ch.name
        if nm == 'vkCreateShaderModule':
            info = child(ch, 'CreateInfo', 'pCreateInfo')
            mid = child(ch, 'ShaderModule', 'pShaderModule')
            if info is None or mid is None:
                continue
            # the replay structured file carries no buffer contents: the module is marked by its resource id (the
            # MODULE lines of rd_sd_f23f.py on the capture file give id -> sha); marks may hold ids or shas
            r = rid(mid)
            modules[r] = r if r in marks else 'unknown'
            b = None if r in marks else code_bytes_safe(sdf, info)
            if b is not None:
                modules[r] = hashlib.sha256(b).hexdigest()
        elif nm in ('vkCreateComputePipelines', 'vkCreateGraphicsPipelines'):
            infos = arr(child(ch, 'CreateInfo', 'pCreateInfos'))
            pids = arr(child(ch, 'Pipeline', 'pPipelines'))
            for info, pid in zip(infos, pids):
                if nm == 'vkCreateComputePipelines':
                    pipes[rid(pid)] = ('cs', rid(child(child(info, 'stage'), 'module')))
                else:
                    fm = None
                    for sg in arr(child(info, 'pStages')):
                        if ival(child(sg, 'stage')) & FRAG:
                            fm = rid(child(sg, 'module'))
                    pipes[rid(pid)] = ('ps', fm)
        elif nm == 'vkCmdBindPipeline':
            bound[(rid(child(ch, 'commandBuffer')), ival(child(ch, 'pipelineBindPoint')))] = rid(child(ch, 'pipeline'))
        elif nm in DISPATCH or nm in DRAW:
            cb = rid(child(ch, 'commandBuffer'))
            p = bound.get((cb, 1 if nm in DISPATCH else 0))
            pi = pipes.get(p)
            sha = modules.get(pi[1], 'unknown') if pi else 'unknown'
            if sha in marks:
                acts.append((ci, nm, pi[0], sha, marks[sha]))
    return acts, len(modules), len(pipes)
