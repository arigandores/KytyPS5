import hashlib,sys
V=b'VUID-VkSwapchainCreateInfoKHR-imageExtent-01689'
for p in ['C:/kyty/f287/f5c/log_f5c_b.txt','C:/kyty/s144/log_w144_09.txt']:
    d=open(p,'rb').read()
    print(p,'sha256',hashlib.sha256(d).hexdigest(),'bytes',len(d))
    mi=d.find(b'TestMinimize: minimize'); wm=d.find(b'Window 1 minimized')
    e=d.find(b'[Vulkan][E]'); v=d.find(V)
    print(' minimize',mi,'Window1min',wm,'first [Vulkan][E]',e,'count E',d.count(b'[Vulkan][E]'),'VUID',v,'count VUID',d.count(V))
    le=d[e:d.find(b'\n',e)]; ls=d.rfind(b'\n',0,v)+1; lv=d[ls:d.find(b'\n',v)]
    print(' E line has VUID:',V in le,'| E line:',le[:160])
    print(' VUID line:',lv[:200])
    print(' lines between E and VUID:',d[e:v].count(b'\n'))
    print(' last line:',d.rstrip().rsplit(b'\n',1)[-1][:160])
