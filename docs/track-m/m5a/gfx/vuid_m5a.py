import os, sys, json, hashlib, re
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
P = 'C:/VulkanSDK/1.4.357.0/share/vulkan/registry/validusage.json'
X = 'C:/VulkanSDK/1.4.357.0/share/vulkan/registry/vk.xml'
for f in (P, X):
    print('sha256', hashlib.sha256(open(f, 'rb').read()).hexdigest(), f)
j = json.load(open(P, encoding='utf-8'))
print('version', j.get('version info'))
vu = j['validation']
want = re.compile(r'VkImageViewMinLodCreateInfoEXT|minLod-06|depthClamp|DepthClamp|depthClipEnable')
n = 0
seen = set()
for obj, d in vu.items():
    for k, lst in d.items():
        for e in lst:
            vid = e.get('vuid', '')
            t = e.get('text', '')
            if vid in seen:
                continue
            if (obj == 'VkImageViewMinLodCreateInfoEXT') or ('VkImageViewMinLodCreateInfoEXT' in vid) \
               or ('depthClampEnable' in t and 'Rasterization' in obj) or ('depthClipEnable' in vid):
                seen.add(vid)
                n += 1
                print(obj, '|', vid, '|', re.sub(r'<[^>]+>', '', t)[:400])
print('matched', n)
# vk.xml: member comment of VkImageViewMinLodCreateInfoEXT
x = open(X, encoding='utf-8').read()
i = x.find('name="VkImageViewMinLodCreateInfoEXT"')
print(x[i - 50:i + 600])
print('DONE')
