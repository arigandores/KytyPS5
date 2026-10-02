p='C:/kyty/s146/step0/port_tools146.py'; t=open(p,'rb').read().decode('ascii')
t=t.replace("d.rep('''    powershell -NoProfile","d.rep('''  powershell -NoProfile",1).replace("      '''    powershell -NoProfile","      '''  powershell -NoProfile",1)
old="d = Doc(S6 + '/fgcpu146.py')\n"
new=("d = Doc(S5 + '/fgcpu145.py')\n"
     "d.rep('''to s145 by HPP-350, names 143 -> 144 -> 145)''', '''to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146)''')\n"
     "d.t = d.t.replace('fgcpu145', 'fgcpu146').replace('go145a.sh', 'go146a.sh')\n")
assert t.count(old)==1; t=t.replace(old,new)
open(p,'wb').write(t.encode('ascii'))
