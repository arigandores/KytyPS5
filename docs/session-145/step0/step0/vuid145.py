#!/usr/bin/env python3
"""vuid145.py - session 145 step 0 (HPP-350; ROADMAP "SESSION 122" item 273 (k)(2)): the evidence for the VUID string of the
F6 warning, the one message on which 13 W of s144 reached the duplicate limit (step0/f6scan145.out.txt).  The emulator logs
print the layer message text only ("[Vulkan][W][<type>]: <pMessage>", 4fc501f4 vulkanWindow.cpp VulkanDebugMessengerCallback),
not pMessageIdName; the name is read from the layer binary the W load (VK_LAYER_PATH = C:/VulkanSDK/1.4.357.0/Bin): the
format strings of the message and the string that follows them in .rdata, and the definition of the setting in the layer
manifest.  Read only, ASCII output.  usage: vuid145.py <out.txt>"""
import hashlib
import json
import sys

DLL = 'C:/VulkanSDK/1.4.357.0/Bin/VkLayer_khronos_validation.dll'
MAN = 'C:/VulkanSDK/1.4.357.0/Bin/VkLayer_khronos_validation.json'
F6_TAIL = b' and this write is unused.\nSpec information at https://docs.vulkan.org/spec/latest/chapters/interfaces.html#interfaces-fragmentoutput'
F6_HEAD = b'there is no VkRenderingInfo::pColorAttachments['


def strings_around(b, pos, before=6, after=3):
    """The NUL-separated strings (length > 3) around pos: `before` strings before it, the one holding it, `after` after."""
    s = b.rfind(b'\x00', 0, pos) + 1
    out_b, i = [], s - 1
    while len(out_b) < before and i > 0:
        j = b.rfind(b'\x00', 0, i)
        t = b[j + 1:i]
        if len(t) > 3:
            out_b.insert(0, (j + 1, t))
        i = j
    e = b.find(b'\x00', pos)
    cur = (s, b[s:e])
    out_a, i = [], e
    while len(out_a) < after:
        j = b.find(b'\x00', i + 1)
        t = b[i + 1:j]
        if len(t) > 3:
            out_a.append((i + 1, t))
        i = j
    return out_b, cur, out_a


def main():
    out = sys.argv[1]
    b = open(DLL, 'rb').read()
    lines = ['vuid145: layer %s sha256 %s bytes %d' % (DLL, hashlib.sha256(b).hexdigest(), len(b))]
    hits = []
    i = b.find(F6_TAIL)
    while i >= 0:
        hits.append(i)
        i = b.find(F6_TAIL, i + 1)
    lines.append('format strings ending " and this write is unused. Spec information ...fragmentoutput" (the VkRenderingInfo '
                 'form of the F6 text): %d' % len(hits))
    for h in hits:
        bf, cur, af = strings_around(b, h)
        for p, t in bf:
            lines.append('  before @%d: %s' % (p, t[:140].decode('latin1').replace('\n', ' ')))
        lines.append('  THIS   @%d: %s' % (cur[0], cur[1][:140].decode('latin1').replace('\n', ' ')))
        for p, t in af:
            lines.append('  after  @%d: %s' % (p, t[:140].decode('latin1').replace('\n', ' ')))
    head = b.count(F6_HEAD)
    lines.append('format strings "there is no VkRenderingInfo::pColorAttachments[": %d' % head)
    names = [b'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering', b'Undefined-Value-ShaderOutputNotConsumed\x00']
    for n in names:
        lines.append('string %s: %d occurrence(s)' % (n.rstrip(b'\x00').decode(), b.count(n)))
    m = json.load(open(MAN, encoding='utf-8'))
    found = []

    def walk(o):
        if isinstance(o, dict):
            if o.get('key') == 'message_id_filter':
                found.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(m)
    lines.append('manifest %s sha256 %s: setting message_id_filter %s' % (
        MAN, hashlib.sha256(open(MAN, 'rb').read()).hexdigest(),
        json.dumps(dict((k, found[0].get(k)) for k in ('env', 'type', 'description'))) if found else 'NOT FOUND'))
    lines.append('READING [I]: the string after the VkRenderingInfo form of the F6 format in .rdata is the VUID name passed '
                 'with it - Undefined-Value-ShaderOutputNotConsumed-DynamicRendering (the subpass form is followed by '
                 'Undefined-Value-ShaderOutputNotConsumed); the s144 W logs carry the VkRenderingInfo form only (f6scan145)')
    open(out, 'w', encoding='ascii', errors='replace', newline='\n').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[-6:]))


if __name__ == '__main__':
    main()
