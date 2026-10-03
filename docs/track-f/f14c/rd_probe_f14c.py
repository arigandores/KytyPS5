# Track F link F14c (HPP-489; ROADMAP s122 item 400(v)(1)): qrenderdoc --python rd_probe_f14c.py
# RD_CAP=<capture> RD_OUT=<file>.  NO REPLAY: structured data only.  Prints the chunk-name histogram and the child tree of the
# first two chunks of each name the F14c reader needs (sampler, image view, pipelines, layouts, descriptor writes, binds, draws).
# DATA ONLY; ASCII only; exits the process (os._exit).
import os, traceback
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f14c/rd_probe.txt')
out = open(OUT, 'w')
NL = chr(10)
WANT = ('vkCreateSampler', 'vkCreateImageView', 'vkCreateGraphicsPipelines', 'vkCreateComputePipelines',
        'vkCreatePipelineLayout', 'vkCreateDescriptorSetLayout', 'vkCmdPushDescriptorSetKHR', 'vkCmdPushDescriptorSet', 'vkUpdateDescriptorSets',
        'vkCmdBindDescriptorSets', 'vkCmdBindPipeline', 'vkCmdDrawIndexed', 'vkCmdDraw', 'vkCmdDispatch',
        'vkCmdExecuteCommands', 'vkBeginCommandBuffer', 'vkCreateImage', 'vkUpdateDescriptorSetWithTemplate',
        'vkCmdPushDescriptorSetWithTemplateKHR', 'vkCmdDrawIndexedIndirect', 'vkCmdDrawIndirect', 'vkCmdDrawMeshTasksEXT',
        'vkCmdDrawIndirectCount', 'vkCmdDrawIndexedIndirectCount', 'vkCreateShaderModule')


def dump(o, depth, maxd, lines, budget):
    if len(lines) >= budget:
        return
    try:
        val = ''
        n = o.NumChildren()
        if n == 0:
            try:
                val = ' = ' + str(o.AsString())
            except Exception:
                try:
                    val = ' = ' + str(o.AsInt())
                except Exception:
                    val = ''
            try:
                r = o.AsResourceId()
                val = val + ' rid=' + str(r)
            except Exception:
                pass
        lines.append('  ' * depth + '%s : %s/%s n=%d%s' % (o.name, o.type.name, o.type.basetype, n, val[:120]))
        if depth < maxd:
            for i in range(min(n, 40)):
                dump(o.GetChild(i), depth + 1, maxd, lines, budget)
    except Exception as e:
        lines.append('  ' * depth + 'ERR %s' % e)


def main():
    import renderdoc as rd
    cap = rd.OpenCaptureFile()
    st = cap.OpenFile(os.environ['RD_CAP'], '', None)
    if st != rd.ResultCode.Succeeded:
        out.write('open failed %s' % st + NL); return 1
    sdf = cap.GetStructuredData()
    out.write('capture %s chunks %d buffers %d' % (os.environ['RD_CAP'], len(sdf.chunks), len(sdf.buffers)) + NL)
    hist = {}
    shown = {}
    for ci, ch in enumerate(sdf.chunks):
        nm = ch.name
        hist[nm] = hist.get(nm, 0) + 1
        if nm in WANT and shown.get(nm, 0) < 2:
            shown[nm] = shown.get(nm, 0) + 1
            lines = []
            dump(ch, 0, 7 if nm != 'vkCreateShaderModule' else 3, lines, 400)
            out.write('CHUNK %d %s' % (ci, nm) + NL + NL.join(lines) + NL)
    for nm in sorted(hist):
        out.write('HIST %s %d' % (nm, hist[nm]) + NL)
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
