# F4b (Red Team): VUIDs about dual-source blend in the SDK validation layer used by W runs
import re, hashlib, sys
p='C:/VulkanSDK/1.4.357.0/Bin/VkLayer_khronos_validation.dll'
b=open(p,'rb').read()
print(p,len(b),hashlib.sha256(b).hexdigest()[:16])
s=set(re.findall(rb'VUID-[A-Za-z0-9_\-]*(?:[Dd]ualSrc|DualSource|dual)[A-Za-z0-9_\-]*',b))
for x in sorted(s): print(x.decode())
for m in re.finditer(rb'[ -~]{0,200}maxFragmentDualSrcAttachments[ -~]{0,300}',b):
    t=m.group(0).decode()
    if 'VUID' in t or 'Location' in t or 'dual' in t.lower(): print('TXT:',t[:500])
for m in re.finditer(rb'[ -~]{0,120}dualSrcBlend feature[ -~]{0,200}',b): print('TXT2:',m.group(0).decode()[:400])
