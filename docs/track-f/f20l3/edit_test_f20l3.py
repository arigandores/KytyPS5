"""F20l3 (HPP-655): edits of the ported test_b32_read.py - the admission section of F20l2 (controls b32_z0b / ppb / pcb, the b32_pd
reference reread) is replaced by test_new_section.py (PK-A of the cold form, cold / warm admission, the installed S18, tag names, the exact
Mann-Whitney test against a brute force, the U5 rule of item 555 (b)(2) and 591 (d)(2), the series stop rule, --pka); build() gets the
pre_scene frames; the cp1250 check reads b32_s01.  LF.  usage: python edit_test_f20l3.py <test_b32_read.py> <test_new_section.py>"""
import sys


def main(argv):
    path, new = argv
    s = open(path, 'rb').read().decode('utf-8')
    sec = open(new, 'rb').read().decode('utf-8').replace('\r\n', '\n')
    E = [
        ('''"""F20l3 (HPP-655): fixtures of b32_read.py - the rule of item 574 (d)''',
         '''"""F20l3 (HPP-655): fixtures of b32_read.py - item 591: the PK-A domain of the cold form (v)(2), the member and 'not called' (v)(3)-(4),
U5(3) not computable (v)(6), the U5(1) rule of item 555 (b)(2) with the base of (d)(2) (exact Mann-Whitney against a brute force), the
series stop rule of item 550 (e)(2)-(3), cold / warm admission and the installed S18 (g)(3); and as in F20l2: the rule of item 574 (d)'''),
        ('import shutil\nimport subprocess\n', 'import shutil\nimport statistics\nimport subprocess\n'),
        ('''          dt_by_idx=None, seed=None, stand_mode='present'):''',
         '''          dt_by_idx=None, seed=None, stand_mode='present', pre_scene=None):'''),
        ('''        ['GuestOut: Level has started: underwater_aerial_garden\\n']
    lines.append('FrameTrace: n=%d''',
         '''        ['GuestOut: Level has started: underwater_aerial_garden\\n'] + [x + '\\n' for x in (pre_scene or [])]
    lines.append('FrameTrace: n=%d'''),
        ('''                    'sys.argv=["b32_read.py","--dir",%r,"--tag","b32_ppb"]; runpy.run_path(%r, run_name="__main__")' % (
                        os.path.join(TMP, 'adm_pp'), os.path.join(HERE, 'b32_read.py'))], env=env, capture_output=True, cwd=HERE)''',
         '''                    'sys.argv=["b32_read.py","--dir",%r,"--tag","b32_s01"]; runpy.run_path(%r, run_name="__main__")' % (
                        os.path.join(TMP, 'adm_s01'), os.path.join(HERE, 'b32_read.py'))], env=env, capture_output=True, cwd=HERE)'''),
    ]
    for i, (a, b) in enumerate(E):
        c = s.count(a)
        if c != 1:
            print('edit %d matches %d times - refused: %r' % (i, c, a[:70]))
            return 1
        s = s.replace(a, b)
    i0 = s.index('# ---- admission (--dir form)\n')
    i1 = s.index('# ---- strict cp1250 output')
    s = s[:i0] + sec + s[i1:]
    open(path, 'wb').write(s.encode('ascii'))
    print('test edits %d + section %d lines -> %s' % (len(E), sec.count('\n'), path))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
