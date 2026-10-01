"""Session 145 link 1b (HPP-379, ROADMAP s122 item 295 (z)): the difference of the new --regress144 output against the output
of step 0 / 0b (sha256 15e26fa5...): every old line must stay byte for byte and in order; every new line must be inserted and
named (a NEW295 line of a W tag, of a V tag, or a NEW295 ROWS line).  ASCII.  usage: diff145.py <old> <new> <out.txt>"""
import difflib
import hashlib
import sys

OLD_SHA = '15e26fa5b87d1de6c15ca98c2895e78b3334df897ccdb63152ce827a36e549f7'


def main():
    old_b, new_b = open(sys.argv[1], 'rb').read(), open(sys.argv[2], 'rb').read()
    a, b = old_b.decode('ascii').split('\n'), new_b.decode('ascii').split('\n')
    out = ['diff145 old %s sha256 %s (expected %s: %s) lines %d; new %s sha256 %s lines %d' % (
        sys.argv[1], hashlib.sha256(old_b).hexdigest(), OLD_SHA[:16], 'yes' if hashlib.sha256(old_b).hexdigest() == OLD_SHA
        else 'NO', len(a), sys.argv[2], hashlib.sha256(new_b).hexdigest(), len(b))]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ins, other = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        if tag == 'insert':
            ins += [(j + 1, b[j]) for j in range(j1, j2)]
        else:
            other.append((tag, i1 + 1, i2, j1 + 1, j2))
    kinds = {'W': 0, 'V': 0, 'ROWS': 0, 'unnamed': 0}
    for n, line in ins:
        if line.startswith('NEW295 ROWS '):
            k = 'ROWS'
            name = line[len('NEW295 ROWS '):].split(':')[0]
        elif line.startswith('NEW295 ') and line.split(' ')[2] in ('W:', 'V:'):
            k = line.split(' ')[2][0]
            name = '%s %s' % (line.split(' ')[1], k)
        else:
            k = 'unnamed'
            name = line[:60]
        kinds[k] += 1
        out.append('INSERTED new line %d: %s - %s' % (n, k, name))
    for o in other:
        out.append('NOT AN INSERTION: %s old lines %d..%d new lines %d..%d' % o)
    kept = sum(i2 - i1 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag == 'equal')
    ok = not other and kinds['unnamed'] == 0 and kept == len(a) and hashlib.sha256(old_b).hexdigest() == OLD_SHA
    out.append('DIFF145 SUMMARY: old lines %d all kept byte for byte and in order (%d); inserted %d = NEW295 lines of W tags %d, of V '
               'tags %d, NEW295 ROWS %d, unnamed %d; replaced or deleted blocks %d -> %s' % (
                   len(a), kept, len(ins), kinds['W'], kinds['V'], kinds['ROWS'], kinds['unnamed'], len(other),
                   'PASS' if ok else 'FAIL'))
    open(sys.argv[3], 'w', encoding='ascii', newline='\n').write('\n'.join(out) + '\n')
    print(out[0])
    print(out[-1])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
