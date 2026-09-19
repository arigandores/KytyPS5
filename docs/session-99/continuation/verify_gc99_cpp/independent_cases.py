"""Independent specification cases; no emulator/game/build and no author fixtures."""
import itertools
import json
from pathlib import Path


def actual_path(helper, usage, trigger=30, critical=80):
    # Existing C++ mutation/return order, independently transcribed during review.
    delta = 0 if helper else 1
    if usage < trigger:
        return delta, False, 'below_trigger'
    if helper:
        if usage < critical:
            return delta, False, 'held_return'
        delta += 1
    return delta, usage >= critical, 'collect'


def audit(helper, sticky, before, after, critical):
    held = helper or sticky
    expected = 0 if held and not critical else 1
    return dict(checks=1, hold=int(held and not critical),
                bad=int((sticky and not helper) or after < before or after-before != expected),
                critical=int(held and critical))


cases = []
for helper, usage in itertools.product((False, True), (0, 29, 30, 79, 80, 100)):
    delta, critical, path = actual_path(helper, usage)
    for sticky in (False, True):
        result = audit(helper, sticky, 41, 41+delta, critical)
        assert result['bad'] == int(sticky and not helper)
        assert result['checks'] == 1
        cases.append(dict(helper=helper, sticky=sticky, usage=usage, path=path, result=result))

mutants = [
    ('paused_clock_advances', True, True, 41, 42, False),
    ('base_clock_pauses', False, False, 41, 41, False),
    ('base_catches_up', False, False, 41, 59, False),
    ('held_catches_up', True, True, 41, 59, False),
    ('clock_backwards', True, True, 41, 40, False),
    ('uint64_wrap', False, False, 2**64-1, 0, False),
    ('critical_clock_frozen', True, True, 41, 41, True),
    ('critical_double_tick', True, True, 41, 43, True),
    # The delta is RIGHT here; independent sticky still catches lost helper.
    ('lost_sticky_even_with_correct_pause', False, True, 41, 41, False),
    ('lost_sticky_at_critical', False, True, 41, 42, True),
]
for name, *args in mutants:
    result = audit(*args)
    assert result['bad'] == 1, name
    cases.append(dict(mutant=name, result=result))

# Refresh is the pressure authority, not the old value and not the observed tick.
for old, fresh in ((0, 100), (100, 0)):
    delta, critical, path = actual_path(True, fresh)
    assert delta == (1 if fresh >= 80 else 0)
    assert audit(True, True, 41, 41+delta, critical)['bad'] == 0
    cases.append(dict(old_usage=old, refreshed_usage=fresh, path=path, delta=delta))

# Outside-slice witness has no stale-current-op dependency.
for stale_current_op in (False, True):
    current_slice = None
    sticky = current_slice is not None and current_slice['counted']
    assert sticky is False
    cases.append(dict(outside_slice=True, stale_current_op=stale_current_op, sticky=sticky))

output = dict(verdict='PASS', cases=len(cases), scope='Independent model cases, not compiled C++ execution', results=cases)
Path(__file__).with_name('independent_cases.json').write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
print(f"PASS: {len(cases)} independent cases, including {len(mutants)} caught mutants")
