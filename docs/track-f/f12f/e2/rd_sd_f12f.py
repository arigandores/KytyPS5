# Track F link F12f (HPP-480; ROADMAP s122 item 391 (g)(4)): qrenderdoc --python rd_sd_f12f.py
# RD_CAP=<capture> RD_OUT=<file> RD_MARK=<sha256,...>.  Edition 2 of the capture reader (seal section 8): NO REPLAY - only the
# structured data of the capture file (CaptureFile.GetStructuredData), CPU and disk.  The in-lock reader rd_cs_f12f.py moved the replay to
# every dispatch (SetFrameEvent) and needed > 900 s on a load-frame capture with thousands of dispatches.
# From the chunks: vkCreateShaderModule (module id -> sha256 of the SPIR-V bytes), vkCreateComputePipelines (pipeline id -> module id),
# vkCmdBindPipeline with the compute bind point (command buffer -> current pipeline), vkCmdDispatch / vkCmdDispatchIndirect /
# vkCmdDispatchBase (the module of the current compute pipeline of the command buffer).  Prints the modules with their sha, every dispatch
# chunk (chunk index, ordinal, call, size, module sha, mark), 'CS sha=... dispatches=...', 'MODULES total M marked_380b K', the line
# 'SUMMARY dispatches D distinct_cs C marked_380b N marked_eids chunk:<i>,...' (chunk indices, NOT event ids: event ids need the replay -
# F12g), 'done'; exits the process (os._exit).  DATA ONLY.  ASCII only.
import os, traceback, hashlib
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f12f/rd_sd.txt')
MARK = set(x.strip().lower() for x in os.environ.get('RD_MARK', '').split(',') if x.strip())
out = open(OUT, 'w')
NL = chr(10)
DISPATCH = ('vkCmdDispatch', 'vkCmdDispatchIndirect', 'vkCmdDispatchBase', 'vkCmdDispatchBaseKHR')


def child(o, *names):
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


def code_bytes(sdf, info):
    """the SPIR-V bytes of VkShaderModuleCreateInfo: pCode as a buffer, or as an array of integers."""
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


def main():
    import renderdoc as rd
    cap = rd.OpenCaptureFile()
    st = cap.OpenFile(os.environ['RD_CAP'], '', None)
    if st != rd.ResultCode.Succeeded:
        out.write('open failed %s' % st + NL); return 1
    sdf = cap.GetStructuredData()
    out.write('capture %s' % os.environ['RD_CAP'] + NL)
    out.write('mark %s' % ','.join(sorted(MARK)) + NL)
    out.write('chunks %d buffers %d' % (len(sdf.chunks), len(sdf.buffers)) + NL)
    modules, pipes, bound = {}, {}, {}
    disp = []
    seen_kinds = set()
    for ci, ch in enumerate(sdf.chunks):
        nm = ch.name
        if nm == 'vkCreateShaderModule':
            info = child(ch, 'CreateInfo', 'pCreateInfo')
            mid = child(ch, 'ShaderModule', 'pShaderModule')
            if 'mod' not in seen_kinds:
                seen_kinds.add('mod'); out.write('FIRST vkCreateShaderModule children %s' % names(ch) + NL)
            if info is None or mid is None:
                continue
            b, how = code_bytes(sdf, info)
            if b is None:
                out.write('MODULE %s unread: %s' % (rid(mid), how) + NL); continue
            sha = hashlib.sha256(b).hexdigest()
            modules[rid(mid)] = (sha, len(b))
            out.write('MODULE %s sha=%s bytes=%d via=%s mark=%s' % (rid(mid), sha, len(b), how, '380b' if sha in MARK else '-') + NL)
        elif nm == 'vkCreateComputePipelines':
            if 'pipe' not in seen_kinds:
                seen_kinds.add('pipe'); out.write('FIRST vkCreateComputePipelines children %s' % names(ch) + NL)
            info = child(ch, 'CreateInfo', 'pCreateInfos')
            pid = child(ch, 'Pipeline', 'pPipelines')
            if info is None or pid is None:
                continue
            if info.type.basetype == rd.SDBasic.Array:
                info = info.GetChild(0)
            if pid.type.basetype == rd.SDBasic.Array:
                pid = pid.GetChild(0)
            stg = child(info, 'stage')
            mod = child(stg, 'module') if stg is not None else None
            if mod is not None:
                pipes[rid(pid)] = rid(mod)
        elif nm == 'vkCmdBindPipeline':
            bp = child(ch, 'pipelineBindPoint')
            if bp is not None and bp.AsInt() == 1:
                bound[rid(child(ch, 'commandBuffer'))] = rid(child(ch, 'pipeline'))
        elif nm in DISPATCH:
            cb = rid(child(ch, 'commandBuffer'))
            p = bound.get(cb)
            m = pipes.get(p)
            sha, n = modules.get(m, ('unknown', 0))
            gx, gy, gz = (child(ch, 'groupCountX'), child(ch, 'groupCountY'), child(ch, 'groupCountZ'))
            dims = 'x'.join(str(g.AsInt()) for g in (gx, gy, gz)) if None not in (gx, gy, gz) else 'indirect'
            disp.append((ci, nm, dims, sha, n))
    seen = {}
    marked = []
    for k, (ci, nm, dims, sha, n) in enumerate(disp, 1):
        mk = '380b' if sha in MARK else '-'
        if mk == '380b':
            marked.append(ci)
        seen[sha] = seen.get(sha, 0) + 1
        out.write('DISPATCH chunk=%d ord=%d call=%s dims=%s cs_sha=%s bytes=%d mark=%s' % (ci, k, nm, dims, sha, n, mk) + NL)
    for sha in sorted(seen):
        out.write('CS sha=%s dispatches=%d mark=%s' % (sha, seen[sha], '380b' if sha in MARK else '-') + NL)
    nmod = sum(1 for s, _ in modules.values() if s in MARK)
    out.write('MODULES total %d marked_380b %d; compute pipelines %d' % (len(modules), nmod, len(pipes)) + NL)
    out.write('SUMMARY dispatches %d distinct_cs %d marked_380b %d marked_eids %s' % (
        len(disp), len(seen), len(marked), ('chunk:' + ','.join(str(c) for c in marked)) if marked else '-') + NL)
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
