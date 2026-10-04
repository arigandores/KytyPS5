# F17a (HPP-525): self-check of sweep_f17a.py and sweep2_f17a.py on a synthetic log (every member and edge of the
# readers: the validation marker, the F6 keys with and without VK_NULL_HANDLE, a burst broken by a foreign line, runs
# split by the ascending rule, the dump witness lines, an EXIT text).  Ends with 'ALL OK'.
# Usage: python selfcheck_f17a.py <empty work dir>   (run from the directory of the two sweep scripts)
import json, os, subprocess, sys

work = sys.argv[1].replace(os.sep, '/').rstrip('/')
here = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
d = work + '/selfcheck'
os.makedirs(d, exist_ok=True)
W = ('[Vulkan][W][2]: vkCmdDrawIndexed(): Inside [VK_SHADER_STAGE_FRAGMENT_BIT] it writes to [Output variable, Location %d, '
     '"out_mrt_%d"] but there is no VkRenderingInfo::pColorAttachments[%d]%s and this write is unused.')
SP = 'Spec information at https://docs.vulkan.org/spec/latest/chapters/interfaces.html#interfaces-fragmentoutput'
N = ' (imageView is VK_NULL_HANDLE)'


def w(loc, null):
    return [W % (loc, loc, loc, N if null else ''), SP]


L = ['TITLE', 'VK_LAYER_KHRONOS_validation available extension: VK_EXT_debug_utils, version = 1',
     '[Vulkan][W][1]: Removing layer X 32 because duplicate', 'DualSrcBlend: supported=1 enabled=1']
L += w(0, 1) + w(1, 1) + w(2, 1) + w(4, 0)   # draw 1: 0n,1n,2n,4
L += ['\t Open: something']                  # a foreign line breaks the burst
L += w(0, 1) + w(1, 1)                       # draw 2: 0n,1n
L += w(0, 1) + w(1, 1)                       # draw 3: 0n,1n - glued to draw 2 in a burst, split by the ascending rule
L += ['RtSkip: mode 1 ctx_slots=8 groups=11 rec_bytes=7192', 'Level has started: abc',
      'RenderColorTarget: slot=3 addr=0x0517bb0000 size=0x1 extent=1x1x1',
      'RenderColorTarget: no color output slot=1 base=0x0000000000 slot_mask=0xf target_mask=0x000000ff rt_slice_offset=0',
      'RenderColorTarget: no color output slot=2 base=0x0000001000 slot_mask=0x0 target_mask=0x000000ff rt_slice_offset=0',
      'MrtState[0]: slot=1 addr=0x0000000000 target_mask=0xf shader_mask=0xf out_mode=4 fmt=0x0000000a nfmt=0x0 order=0x0 width=1 height=1 tile=0 blend=false',
      '[Vulkan][W][2]: vkCreateGraphicsPipelines(): something else 12',
      'unsupported render-target mip range: current=3 levels=2']
L += w(5, 0)                                 # draw 4 at the end of the file: 5
open(d + '/log_sc.txt', 'wb').write((chr(10).join(L) + chr(10)).encode())
for f in ('sc.jsonl', 'sc2.jsonl'):
    if os.path.exists(work + '/' + f):
        os.remove(work + '/' + f)
env = dict(os.environ, F17A_ROOTS=d)
o = subprocess.run([sys.executable, here + '/sweep_f17a.py', work + '/sc.jsonl', '30'], capture_output=True, text=True, env=env)
print(o.stdout.strip(), o.stderr.strip()[:300])
o = subprocess.run([sys.executable, here + '/sweep2_f17a.py', work + '/sc.jsonl', work + '/sc2.jsonl', '30'], capture_output=True, text=True)
print(o.stdout.strip(), o.stderr.strip()[:300])
r = json.loads(open(work + '/sc.jsonl').read())
q = json.loads(open(work + '/sc2.jsonl').read())
ok = True


def chk(name, cond):
    global ok
    print(('ok   ' if cond else 'FAIL ') + name)
    ok &= bool(cond)


chk('validation marker', r['val'] is True)
chk('[Vulkan][W] lines 11', r['vw'] == 11)
chk('f6_broad 9 == f6_sum', r['f6_broad'] == 9 and r['f6_sum'] == 9)
chk('F6 keys', r['f6'].get('2|vkCmdDrawIndexed|0|out_mrt_0|0|1') == 3 and r['f6'].get('2|vkCmdDrawIndexed|4|out_mrt_4|4|0') == 1
    and r['f6'].get('2|vkCmdDrawIndexed|5|out_mrt_5|5|0') == 1)
chk('bursts', r['sig'] == {'vkCmdDrawIndexed:0n,1n,2n,4': 1, 'vkCmdDrawIndexed:0n,1n,0n,1n': 1, 'vkCmdDrawIndexed:5': 1})
chk('other [Vulkan][W] texts 2', len(r['wo']) == 2 and sum(r['wo'].values()) == 2)
chk('identity vw == f6_sum + wo', r['vw'] == r['f6_sum'] + sum(r['wo'].values()))
chk('no color output classes', r['nco'] == {'base0_masknz': 1, 'basenz_mask0': 1})
chk('MrtState classes', r['mrt'] == {'addr0_tmnz_omnz_fmtnz': 1})
chk('decision lines', r['rct_slots'] == {'3': 1} and r['cnt']['rct_decision'] == 1)
chk('EXIT text', r['txt']['exit_rt_hyphen'] == ['unsupported render-target mip range: current=# levels=#'])
chk('RtSkip mode line', r['txt']['rts_mode'] == ['RtSkip: mode # ctx_slots=# groups=# rec_bytes=#'])
chk('scene', r['lvl'] == ['abc'])
chk('lines', r['lines'] == 31)
chk('sweep2 identity f6', q['f6'] == r['f6_sum'])
chk('sweep2 runs', q['run'] == {'vkCmdDrawIndexed:0n,1n,2n,4': 1, 'vkCmdDrawIndexed:0n,1n': 2, 'vkCmdDrawIndexed:5': 1} and q['runs'] == 4)
chk('sweep2 first lines', q['first'] == {'vkCmdDrawIndexed:0n,1n,2n,4': 5, 'vkCmdDrawIndexed:0n,1n': 14, 'vkCmdDrawIndexed:5': 30})
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
