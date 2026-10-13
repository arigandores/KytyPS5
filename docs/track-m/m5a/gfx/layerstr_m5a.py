import os, sys, re, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
F = 'C:/VulkanSDK/1.4.357.0/Bin/VkLayer_khronos_validation.dll'
b = open(F, 'rb').read()
print('sha256', hashlib.sha256(b).hexdigest(), F)
# printable ASCII strings mentioning minLod near image view / mipmap level, and depthClamp
strs = re.findall(rb'[\x20-\x7e]{12,}', b)
pat = re.compile(rb'minLod|06456|depthClamp|depthClip')
n = 0
for s in strs:
    if pat.search(s):
        n += 1
        if n <= 80:
            print(s.decode('ascii')[:300])
print('strings matched', n)
print('DONE')
# second pass: strings mentioning the last mip level / baseMipLevel + levelCount
pat2 = re.compile(rb'(?i)(accessible|baseMipLevel \+|last mip|levelCount - 1|levelCount-1)')
n2 = 0
for s in strs:
    if pat2.search(s) and (b'%' in s or b'min' in s.lower()):
        n2 += 1
        if n2 <= 40:
            print('P2', s.decode('ascii')[:300])
print('P2 matched', n2)
print('DONE2')
