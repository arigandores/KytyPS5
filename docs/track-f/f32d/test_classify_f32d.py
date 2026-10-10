# F32d (HPP-742): fixtures of classify_f32d.py - one member per rule, per order edge and per form key; last line ALL OK.
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('c', os.path.join(HERE, 'classify_f32d.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
ok = True


def iv(**k):
    base = {'il': 50, 'ir': 0, 'gcn': 0, 'skip': 0, 'held': 0, 'skipceil': 0, 'cs_miss': 0, 'pcs': [], 'prio_n': 0, 'prio_max': 0,
            'mtl_n': 0, 'mtl_max': 0, 'win': 0, 'win_ex': [], 'pause_on': 0, 'pause_off': 0, 'logasync': [], 'diagb32': [],
            'top': []}
    base.update(k)
    return base


def row(level='mini_giants_garden', dt=150000, tr_win=0, tr_hold_before=0, **k):
    return {'level': level, 'dt_us': dt, 'tr_win': tr_win, 'tr_hold_before': tr_hold_before, 'iv': iv(**k)}


DEF = c.form_of('C:/kyty/x/log_v.txt', {'env': {'KYTY_FRAME_TRACE': 'lite', 'KYTY_QUEUE_TRACE': '1', 'KYTY_GPU_CLOCK_PIN': '1',
                                                 'KYTY_KEYS': '@1:j'}, 'cmdline': ['x', '--vulkan-validation', 'false']}, [])


def check(name, got, want):
    global ok
    g = [x[0] for x in got]
    if g[:len(want)] != want:
        print('FAIL', name, got, 'want', want)
        ok = False
    else:
        print('ok  ', name, g)


def eq(name, got, want):
    global ok
    if got != want:
        print('FAIL', name, got, 'want', want)
        ok = False
    else:
        print('ok  ', name)


# form keys
eq('default form: no instr, no b5f, no patch', (DEF['instr'], DEF['b5f'], DEF['patch']), ([], [], False))
f = c.form_of('p', {'env': {}, 'cmdline': []}, ['RenderDoc: API 1.6.0 bound'])
eq('RenderDoc head -> instr', f['instr'], ['--rd (RenderDoc bound)'])
f = c.form_of('p', {'env': ['KYTY_AV_TRACE=1', 'KYTY_FRAME_TRACE=lite'], 'cmdline': None}, [])
eq('env as list, AV_TRACE -> instr', f['instr'], ['KYTY_AV_TRACE=1'])
f = c.form_of('p', {'env': {'KYTY_POKE': '27e46c:90'}, 'cmdline': []}, [])
eq('POKE -> instr', f['instr'], ['KYTY_POKE=27e46c:90'])
f = c.form_of('p', {'env': {'KYTY_DIAG_B32': '0'}, 'cmdline': []}, [])
eq('DIAG at 0 -> not instr', f['instr'], [])
f = c.form_of('p', {'env': {}, 'cmdline': ['x', '--shader-validation', 'true']}, [])
eq('shader validation -> instr', f['instr'], ['--shader-validation true'])
f = c.form_of('p', {'env': {'KYTY_PIPELINE_PRECACHE': '0', 'KYTY_PIPELINE_SALT': 's'}, 'cmdline': []}, [])
eq('salted cold -> b5f', f['b5f'], ['KYTY_PIPELINE_PRECACHE=0', 'KYTY_PIPELINE_SALT'])
f = c.form_of('p', {'env': {'KYTY_S_REPLAY': '3'}, 'cmdline': []}, [])
eq('S_REPLAY=3 (shipped default) -> not b5f', f['b5f'], [])
f = c.form_of('C:/kyty/s288/s15/log_k_02.txt', {'env': {}}, [])
eq('catalog arm k_ -> b5f', f['b5f'], ['catalog collection arm k_'])
f = c.form_of('C:/kyty/s288/s15/log_u_02.txt', {'env': {}}, [])
eq('u_ arm without cold mode -> not b5f', f['b5f'], [])
f = c.form_of('p', {'env': {}, 'times': 'x patch sha256 a2'}, [])
eq('user recording patch from times.txt', f['patch'], True)
f = c.form_of('p', {'env': {'KYTY_GAME_PATCH': 'C:/x.txt'}}, [])
eq('GAME_PATCH env -> patch, not instr', (f['patch'], f['instr']), (True, []))
# rules and order
check('NONE on a clean warm frame', c.classify(row(), DEF), ['NONE'])
check('B32 by level', c.classify(row(level='underwater_aerial_garden'), DEF), ['B32'])
check('B32 intro_next', c.classify(row(level='intro_next'), DEF), ['B32'])
check('B5 ir', c.classify(row(ir=5), DEF), ['B5'])
check('B5 gcn', c.classify(row(gcn=1), DEF), ['B5'])
check('B5 skipped draw', c.classify(row(skip=1), DEF), ['B5'])
check('B5 held', c.classify(row(held=1), DEF), ['B5'])
eq('B5 cold sub-form', c.classify(row(ir=1, tr_win=3), DEF)[0][1].split(':')[0], 'cold')
eq('B5 hold sub-form', c.classify(row(ir=1, tr_win=0), DEF)[0][1].split(':')[0], 'hold')
check('B5 before B33', c.classify(row(ir=1, pcs=[(10, 140000, 1.0)]), DEF), ['B5', 'B33'])
check('B33 save >= half excess', c.classify(row(dt=150000, pcs=[(10, 66667, 1.0)]), DEF), ['B33'])
check('B33 save < half excess -> NONE', c.classify(row(dt=150000, pcs=[(10, 66665, 1.0)]), DEF), ['NONE'])
eq('B33 reopen flag on default form', 'reopen' in c.classify(row(pcs=[(10, 140000, 1.0)]), DEF)[0][1], True)
f = c.form_of('p', {'env': {'KYTY_AV_TRACE': '1'}}, [])
eq('B33 no reopen under instr', 'reopen' in c.classify(row(pcs=[(10, 140000, 1.0)]), f)[0][1], False)
check('B33 before PAUSE', c.classify(row(pcs=[(10, 140000, 1.0)], pause_on=1, win_ex=['1:Pause: true']), DEF), ['B33', 'PAUSE'])
check('PAUSE by Pause: true', c.classify(row(pause_on=1, win_ex=['1:Pause: true']), DEF), ['PAUSE'])
check('PAUSE by focus loss', c.classify(row(win_ex=['1:Window 1 lost keyboard focus']), DEF), ['PAUSE'])
check('Window exposed only -> NONE', c.classify(row(win=1, win_ex=['1:Window 1 exposed']), DEF), ['NONE'])
fi = c.form_of('p', {'env': {}}, ['RenderDoc: API 1.6.0 bound'])
check('INSTR before B32', c.classify(row(level='underwater_aerial_garden'), fi), ['INSTR', 'B32'])
check('PAUSE before INSTR', c.classify(row(pause_on=1, win_ex=['1:Pause: true']), fi), ['PAUSE', 'INSTR'])
fb = c.form_of('C:/kyty/s288/s13/log_k_05.txt', {'env': {}}, [])
check('B5F', c.classify(row(), fb), ['B5F'])
fib = c.form_of('C:/kyty/s288/s13/log_u_06.txt', {'env': {'KYTY_AV_TRACE': '1', 'KYTY_CACHE_MODE': 'prepare-cold'}}, [])
check('INSTR before B5F', c.classify(row(), fib), ['INSTR', 'B5F'])
check('HOST fires', c.classify(row(dt=100000, diagb32=['5:DiagB32: n=1 other_us=1460000 ncpu=32']), DEF), ['HOST'])
check('HOST below theta -> NONE', c.classify(row(dt=100000, diagb32=['5:DiagB32: n=1 other_us=1459000 ncpu=32']), DEF), ['NONE'])
check('B5F before HOST before B32', c.classify(row(level='intro_next', dt=100000, diagb32=['5:DiagB32: other_us=9999999 ncpu=1']), fb),
      ['B5F', 'HOST', 'B32'])
print('ALL OK' if ok else 'FAILED')
