"""F47i (HPP-826): the generator of the copied files of the harness C:/kyty/f287/f47i - the F47d (HPP-809) files of the same role with
the names moved (f47d -> f47i, F47D -> F47I, F47d -> F47i, HPP-809 -> HPP-826) and one header line; no change of meaning.  Files without a
name of the link are copied byte for byte.  ASCII only.  usage: python mk_f47i.py"""
import pathlib
import shutil

SRC = pathlib.Path('C:/kyty/f287/f47d')
DST = pathlib.Path('C:/kyty/f287/f47i')
MOVED = ['guard_f47d.py', 'hold_f47d.py', 'hostload_f47d.py', 'mfsub_f47d.py', 'runchk_f47d.py', 'snap_f47d.py', 'queue_f47d.py',
         'wait_f47d.sh', 'chk_f47d.sh', 'enter_scene.py']
PLAIN = ['dispstate.py', 'idle142.py', 'launch_run.py', 'manifest_fs4c.py', 'procload.py', 'run_safety99.py', 'sheet142.py',
         'gates_default.txt']


def move(text):
    for a, b in (('f47d', 'f47i'), ('F47D', 'F47I'), ('F47d', 'F47i'), ('HPP-809', 'HPP-826')):
        text = text.replace(a, b)
    return text


def main():
    DST.mkdir(exist_ok=True)
    for name in MOVED:
        src = SRC / name
        raw = src.read_bytes().decode('ascii')
        assert '\r' not in raw, name
        out_name = move(name)
        lead = '#' if name.endswith(('.py', '.sh')) else None
        head = ('%s Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), 742 (e), 744 (g)-(d)): copy of the F47d (HPP-809) file %s with '
                'the names moved (f47d -> f47i, F47D -> F47I, F47d -> F47i, HPP-809 -> HPP-826); no change of meaning.\n' % (lead, name))
        body = move(raw)
        if raw.startswith('#!'):
            first, rest = body.split('\n', 1)
            text = first + '\n' + head + rest
        elif raw.startswith('"""'):
            text = head + body
        else:
            text = head + body
        (DST / out_name).write_bytes(text.encode('ascii'))
        print('moved %s -> %s' % (name, out_name))
    for name in PLAIN:
        shutil.copyfile(SRC / name, DST / name)
        print('copied %s' % name)


if __name__ == '__main__':
    main()
