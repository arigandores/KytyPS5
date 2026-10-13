import sys
p = sys.argv[1]
t = open(p, encoding='utf-8').read()
old = '\tstd::fflush(stdout);\n\tstd::_Exit(0);\n'
new = '\tstd::fflush(stdout);\n\tLog::Flush();\n\tLog::DrainForExit();\n\tstd::_Exit(0);\n'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new)
open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('ok')
