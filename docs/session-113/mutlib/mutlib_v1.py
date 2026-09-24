#!/usr/bin/env python3
"""mutlib.py - a fast, strict, shared mutation harness for the session log scorers (a scorer X.py certified by a
fixture suite test_X.py and a mutant list mut_X.py).  Design, guarantees and residual assumptions: README.md next to
this file.

    python mutlib.py --scorer S --test T --mutants M [--workers N] [--no-memo] [--no-hoist] [--no-fast]
                     [--only a,b] [--changed-from PARENT_SCORER --sample 0.2 --seed N] [--control]
                     [--timeout SEC] [--out FILE]

Nothing is edited: the mutant scorer is written into a per-worker scratch directory under mutlib/work, the fixture
suite is transformed in memory (AST) and executed in-process by a pool of spawned worker processes, the mutants are
read from the mutant script by evaluating only the statements that define them.
"""
import argparse
import ast
import builtins
import collections
import copy
import difflib
import functools
import gc
import hashlib
import inspect
import io
import json
import os
import pickle
import random
import re
import shutil
import signal
import stat as stat_mod
import sys
import time
import traceback
import types
import multiprocessing as mp
from multiprocessing.connection import wait as mp_wait
from pathlib import Path, PurePath

HERE = Path(__file__).resolve().parent
HARNESS = Path(__file__).resolve()
SEALED_LOCK = Path('C:/kyty/SEALED_RUN.lock')
PFX = '_mutlib_'
VERSION = 'mutlib 1'


class HarnessError(Exception):
    """A configuration the harness refuses (bad anchor, unsupported suite shape, failing baseline)."""


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def short(text, n=160):
    text = ' '.join(str(text).split())
    return text if len(text) <= n else text[:n - 3] + '...'


def exc_line(exc):
    """'Type: message [file:line]' of the innermost frame."""
    where = ''
    tb = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ is not None else []
    if tb:
        where = ' [%s:%d]' % (Path(tb[-1].filename).name, tb[-1].lineno)
    return short('%s: %s' % (type(exc).__name__, exc), 140) + where


# ======================================================================================================================
# AST helpers: scopes, bound / loaded / free names
# ======================================================================================================================
_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef, ast.ListComp, ast.SetComp,
                ast.DictComp, ast.GeneratorExp)
_FUNC_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


def _outer_parts(n):
    """The parts of a scope-creating node that are evaluated in the ENCLOSING scope."""
    if isinstance(n, _FUNC_NODES):
        a = n.args
        parts = list(n.decorator_list) + list(a.defaults) + [d for d in a.kw_defaults if d is not None]
        for x in a.posonlyargs + a.args + a.kwonlyargs + [a.vararg, a.kwarg]:
            if x is not None and x.annotation is not None:
                parts.append(x.annotation)
        if n.returns is not None:
            parts.append(n.returns)
        return parts
    if isinstance(n, ast.Lambda):
        return list(n.args.defaults) + [d for d in n.args.kw_defaults if d is not None]
    if isinstance(n, ast.ClassDef):
        return list(n.decorator_list) + list(n.bases) + [k.value for k in n.keywords]
    return [n.generators[0].iter]


def scope_walk(node):
    """Every node below `node` in the same scope: nested function / lambda / class / comprehension bodies are not
    entered (the parts of them evaluated in this scope are)."""
    stack = list(ast.iter_child_nodes(node))
    while stack:
        n = stack.pop()
        yield n
        if isinstance(n, _SCOPE_NODES):
            stack.extend(_outer_parts(n))
        else:
            stack.extend(ast.iter_child_nodes(n))


def stmt_nodes(st):
    """`st` and every node of it that lives in the scope `st` lives in."""
    if isinstance(st, _SCOPE_NODES):
        out = [st]
        for p in _outer_parts(st):
            out.append(p)
            out.extend(scope_walk(p))
        return out
    return [st] + list(scope_walk(st))


def import_names(st):
    return {(a.asname or a.name.split('.')[0]) for a in st.names if a.name != '*'}


def bound_names(st):
    """Names a statement binds in its own scope."""
    names = set()
    for n in stmt_nodes(st):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            names.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            names |= import_names(n)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            names.add(n.name)
        elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
            names.add(n.name)
        elif isinstance(n, ast.MatchMapping) and n.rest:
            names.add(n.rest)
    return names


def declared_globals(fn):
    out = set()
    for b in fn.body:
        for n in stmt_nodes(b):
            if isinstance(n, ast.Global):
                out |= set(n.names)
    return out


def free_vars(node):
    """Names a function / lambda / class body / comprehension reads but does not bind: they resolve in the module
    namespace when it RUNS.  Names declared `global` count as free."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        a = node.args
        bound = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
        bound |= {x.arg for x in (a.vararg, a.kwarg) if x is not None}
        roots = node.body if isinstance(node.body, list) else [node.body]
    elif isinstance(node, ast.ClassDef):
        bound, roots = set(), list(node.body)
    else:
        bound = set()
        roots = [node.elt] if hasattr(node, 'elt') else [node.key, node.value]
        for g in node.generators:
            roots.append(g.target)
            roots.extend(g.ifs)
        roots.extend(g.iter for g in node.generators[1:])
    loads, glob, inner = set(), set(), set()
    for r in roots:
        for n in stmt_nodes(r):
            if isinstance(n, ast.Name):
                (loads if isinstance(n.ctx, ast.Load) else bound).add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                bound.add(n.name)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                bound |= import_names(n)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                bound.add(n.name)
            elif isinstance(n, ast.Global):
                glob |= set(n.names)
            elif isinstance(n, ast.Nonlocal):
                bound |= set(n.names)
            if isinstance(n, _SCOPE_NODES) and n is not node:
                inner |= free_vars(n)
    if isinstance(node, ast.ClassDef):
        return (loads - bound) | inner
    return (loads - bound) | (loads & glob) | (inner - bound) | (inner & glob)


def loaded_names(st):
    """Names a statement reads in its scope plus the free names of every function / lambda / comprehension it
    creates (they read module names when called)."""
    names = set()
    for n in stmt_nodes(st):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            names.add(n.id)
        if isinstance(n, _SCOPE_NODES):
            names |= free_vars(n)
    return names


def calls_name(node, name):
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name for n in ast.walk(node))


def root_name(node):
    while isinstance(node, (ast.Attribute, ast.Subscript, ast.Call, ast.Starred)):
        node = node.func if isinstance(node, ast.Call) else node.value
    return node.id if isinstance(node, ast.Name) else None


def parent_map(tree):
    parents = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parents[c] = p
    return parents


def snippet(text):
    """Statements parsed from `text` (for inserted code: carries every field the running Python wants)."""
    return ast.parse(text).body


# ======================================================================================================================
# Mutant extraction (the mutant script is never run: only the statements that define the mutants are evaluated)
# ======================================================================================================================
def _mutant_helper_dict(fn):
    """The dict a mutant(name, old, new) helper fills; refuse any helper that does more than assert and store."""
    a = fn.args
    params = [x.arg for x in a.posonlyargs + a.args]
    if len(params) != 3 or a.vararg or a.kwarg or a.kwonlyargs or a.defaults:
        raise HarnessError('mutant() helper does not take exactly (name, old, new): refusing to guess its meaning')
    name, old, new = params
    target = None
    for st in fn.body:
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
            continue
        if isinstance(st, ast.Assert):
            continue
        if (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Subscript)
                and isinstance(st.targets[0].value, ast.Name) and isinstance(st.targets[0].slice, ast.Name)
                and st.targets[0].slice.id == name and isinstance(st.value, ast.Tuple)
                and [getattr(e, 'id', None) for e in st.value.elts] == [old, new] and target is None):
            target = st.targets[0].value.id
            continue
        raise HarnessError('mutant() helper line %d is more than assert/store: extend mutlib before trusting it'
                           % st.lineno)
    if target is None:
        raise HarnessError('mutant() helper stores nothing')
    return target


def _is_main_guard(st):
    return (isinstance(st, ast.If) and isinstance(st.test, ast.Compare) and isinstance(st.test.left, ast.Name)
            and st.test.left.id == '__name__')


def extract_mutants(mut_path):
    """-> (format, [(name, old, new), ...], executed statement lines).  Formats: 'list' (MUTANTS = [(name, old, new),
    ...]) and 'calls' (mutant(name, old, new) calls filling a dict, helper variables and loops allowed)."""
    mut_path = Path(mut_path)
    src = mut_path.read_bytes().decode('utf-8')
    tree = ast.parse(src, filename=str(mut_path))
    body = tree.body
    helper = None
    for st in body:
        if isinstance(st, ast.FunctionDef) and st.name == 'mutant':
            helper = st
    fmt = 'calls' if helper is not None else 'list'
    coll = _mutant_helper_dict(helper) if helper is not None else 'MUTANTS'
    stop = len(body)
    for i, st in enumerate(body):
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name in ('run', 'lane', 'main', 'worker'):
            stop = i
            break
        if isinstance(st, (ast.For, ast.AsyncFor)) and coll in loaded_names(st.iter):
            stop = i
            break
        if isinstance(st, (ast.While, ast.Try, ast.With, ast.AsyncWith)) or _is_main_guard(st):
            stop = i
            break
        if hasattr(ast, 'TryStar') and isinstance(st, ast.TryStar):
            stop = i
            break
    cand = body[:stop]
    roots = []
    for i, st in enumerate(cand):
        if st is helper or isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if fmt == 'calls':
            if calls_name(st, 'mutant'):
                roots.append(i)
        elif coll in bound_names(st) or (isinstance(st, ast.Expr) and root_name(st.value) == coll):
            roots.append(i)
    if not roots:
        raise HarnessError('no mutant definitions found in %s' % mut_path)
    needed = set()
    for i in roots:
        needed |= loaded_names(cand[i])
    selected = set(roots)
    changed = True
    while changed:
        changed = False
        for i, st in enumerate(cand):
            if i in selected or st is helper or isinstance(st, (ast.Import, ast.ImportFrom, ast.Expr)):
                continue
            if bound_names(st) & needed:
                selected.add(i)
                needed |= loaded_names(st)
                changed = True
    stmts = [st for i, st in enumerate(cand)
             if i in selected or isinstance(st, (ast.Import, ast.ImportFrom))]
    collected = collections.OrderedDict()

    def stub(name, old, new):
        if name in collected:
            raise HarnessError('mutant name %r defined twice' % (name,))
        collected[name] = (old, new)
    ns = {'__name__': '__mutlib_mutants__', '__file__': str(mut_path), '__builtins__': builtins, 'mutant': stub}
    saved = sys.argv, sys.stdout
    sys.argv, sys.stdout = [str(mut_path)], io.StringIO()
    try:
        exec(compile(ast.Module(body=stmts, type_ignores=[]), str(mut_path), 'exec'), ns)
    finally:
        sys.argv, sys.stdout = saved
    if fmt == 'list':
        lst = ns.get(coll)
        if not isinstance(lst, (list, tuple)):
            raise HarnessError('%s is not a list in %s' % (coll, mut_path))
        out, seen = [], set()
        for item in lst:
            if not (isinstance(item, (tuple, list)) and len(item) == 3):
                raise HarnessError('mutant entry %r is not (name, old, new)' % (item,))
            if item[0] in seen:
                raise HarnessError('mutant name %r defined twice' % (item[0],))
            seen.add(item[0])
            out.append(tuple(item))
    else:
        out = [(n, o, w) for n, (o, w) in collected.items()]
    for name, old, new in out:
        if not all(isinstance(x, str) for x in (name, old, new)) or not name.strip():
            raise HarnessError('mutant %r: name / old / new must be non-empty strings' % (name,))
    return fmt, out, sorted(st.lineno for st in stmts)


def validate_mutants(mutants, scorer_src):
    for name, old, new in mutants:
        n = scorer_src.count(old)
        if n != 1:
            raise HarnessError('mutant %s: anchor found %d times: %r' % (name, n, old[:80]))
        if old == new:
            raise HarnessError('mutant %s changes nothing' % name)


def control_mutants(scorer_src, memo_target):
    """Three equivalent mutants that MUST survive: a comment after the docstring (the text changes, no code does), a
    `pass` at the end of read_run (the memo's dependency hash changes, so the uncached path runs) or of evaluate(),
    and a `pass` at module level at the end of the file."""
    tree = ast.parse(scorer_src)
    eol = '\r\n' if '\r\n' in scorer_src else '\n'
    out = []
    first = tree.body[0] if tree.body else None
    if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)):
        seg = ast.get_source_segment(scorer_src, first)
        out.append(('CONTROL_comment_after_docstring', seg, seg + eol + '# mutlib control: an added comment line'))
    funcs = {st.name: st for st in tree.body if isinstance(st, ast.FunctionDef)}
    target = funcs.get(memo_target) or funcs.get('evaluate') or (list(funcs.values())[-1] if funcs else None)
    if target is not None:
        seg = ast.get_source_segment(scorer_src, target)
        out.append(('CONTROL_pass_end_of_%s' % target.name, seg,
                    seg + eol + ' ' * target.body[0].col_offset + 'pass'))
    last = tree.body[-1] if tree.body else None
    if last is not None:
        seg = ast.get_source_segment(scorer_src, last)
        out.append(('CONTROL_module_pass_at_end', seg, seg + eol + 'pass'))
    good = []
    for name, old, new in out:
        if scorer_src.count(old) == 1 and old != new:
            ast.parse(scorer_src.replace(old, new))
            good.append((name, old, new))
    return good


def changed_lines(parent_src, src):
    """0-based line numbers of `src` that differ from `parent_src` (a deletion marks the lines around it)."""
    a, b = parent_src.splitlines(), src.splitlines()
    out = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        if j2 > j1:
            out.update(range(j1, j2))
        else:
            out.update(x for x in (j1 - 1, j1) if 0 <= x < len(b))
    return out


def anchor_lines(src, old):
    start = src.index(old)
    first = src.count('\n', 0, start)
    return first, first + old.count('\n')


# ======================================================================================================================
# The fixture suite: analysis and transformation
# ======================================================================================================================
_MUTATORS = {'append', 'extend', 'insert', 'pop', 'remove', 'clear', 'update', 'setdefault', 'add', 'discard', 'sort',
             'reverse', 'popitem', '__setitem__', '__delitem__'}


class _GuardRewriter(ast.NodeTransformer):
    """`ok &= X` and `ok = ok and X` -> the same with X routed through _mutlib_guard(X, label, lineno), which returns X
    unchanged (so the suite's own bookkeeping is untouched) and raises MutantKilled on a falsy X in fast mode.  Only the
    module's `ok` is rewritten: module scope (loops, ifs, ...) and functions declaring it global; a function's own
    local `ok` is left alone.  drop_assign: emit the bare guard (the hoisted check, which runs before `ok` exists)."""

    def __init__(self, okname, final_lineno=None, label_var=None, drop_assign=False):
        self.okname, self.final_lineno, self.label_var, self.drop = okname, final_lineno, label_var, drop_assign
        self.count = 0

    def _guard(self, value, lineno):
        self.count += 1
        label = (ast.Call(func=ast.Name(PFX + 'label', ast.Load()), args=[ast.Name(self.label_var, ast.Load())],
                          keywords=[]) if self.label_var else ast.Constant(None))
        return ast.Call(func=ast.Name(PFX + 'guard', ast.Load()), args=[value, label, ast.Constant(lineno)],
                        keywords=[])

    def visit_FunctionDef(self, node):
        if self.okname in declared_globals(node):
            self.generic_visit(node)
        return node
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        return node

    def visit_ClassDef(self, node):
        return node

    def visit_For(self, node):
        if self.final_lineno is not None and node.lineno == self.final_lineno and isinstance(node.target, ast.Name):
            saved, self.label_var = self.label_var, node.target.id
            self.generic_visit(node)
            self.label_var = saved
        else:
            self.generic_visit(node)
        return node

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name) and node.target.id == self.okname and isinstance(node.op, ast.BitAnd):
            g = self._guard(node.value, node.lineno)
            if self.drop:
                return ast.copy_location(ast.Expr(g), node)
            node.value = g
        return node

    def visit_Assign(self, node):
        v = node.value
        if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == self.okname
                and isinstance(v, ast.BoolOp) and isinstance(v.op, ast.And) and isinstance(v.values[0], ast.Name)
                and v.values[0].id == self.okname):
            rest = v.values[1:]
            g = self._guard(rest[0] if len(rest) == 1 else ast.BoolOp(ast.And(), rest), node.lineno)
            if self.drop:
                return ast.copy_location(ast.Expr(g), node)
            node.value = ast.BoolOp(ast.And(), [ast.Name(self.okname, ast.Load()), g])
        return node


class _ContinueToReturn(ast.NodeTransformer):
    """The final loop body as a function: its own `continue` becomes `return` (inner loops keep theirs)."""

    def visit_For(self, node):
        node.orelse = [self.visit(s) for s in node.orelse]
        return node
    visit_AsyncFor = visit_While = visit_For

    def visit_FunctionDef(self, node):
        return node
    visit_AsyncFunctionDef = visit_Lambda = visit_ClassDef = visit_FunctionDef

    def visit_Continue(self, node):
        return ast.copy_location(ast.Return(value=None), node)


def _loop_breaks(body):
    """`break` statements that belong to the loop whose body this is."""
    out = []
    stack = list(body)
    while stack:
        n = stack.pop()
        if isinstance(n, ast.Break):
            out.append(n)
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.While)):
            stack.extend(n.orelse)
        elif not isinstance(n, _SCOPE_NODES):
            stack.extend(ast.iter_child_nodes(n))
    return out


def _is_path_expr(v):
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == 'Path':
        return True
    return isinstance(v, ast.IfExp) and _is_path_expr(v.body) and _is_path_expr(v.orelse)


class TestPlan:
    """What the harness knows about one fixture suite (computed identically in the parent and in every worker)."""

    def __init__(self, path, src, okname='ok'):
        self.path, self.src, self.okname = Path(path), src, okname
        self.tree = tree = ast.parse(src, filename=str(path))
        body = tree.body
        self.notes = []
        # ---- the fixture directory -----------------------------------------------------------------------------
        base = [i for i, st in enumerate(body) if 'BASE' in bound_names(st)]
        if len(base) != 1 or not (isinstance(body[base[0]], ast.Assign) and len(body[base[0]].targets) == 1
                                  and isinstance(body[base[0]].targets[0], ast.Name)
                                  and _is_path_expr(body[base[0]].value)):
            raise HarnessError('%s: need exactly one top-level `BASE = Path(...)` to give each worker its own fixture '
                               'directory' % self.path.name)
        self.base_idx = base[0]
        self.uses_argv2 = any(isinstance(n, ast.Subscript) and isinstance(n.value, ast.Attribute)
                              and n.value.attr == 'argv' and isinstance(n.slice, ast.Constant)
                              and n.slice.value == 2 for n in ast.walk(tree))
        # ---- the N family: def case(...) appending to a list, checked by a final `for c in cases:` loop -----------
        self.case_idx = self.final_idx = None
        self.cases_name = self.loopvar = None
        for i, st in enumerate(body):
            if isinstance(st, ast.FunctionDef) and st.name == 'case':
                self.case_idx = i
                for n in ast.walk(st):
                    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'append'
                            and isinstance(n.func.value, ast.Name)):
                        self.cases_name = n.func.value.id
        if self.case_idx is not None and self.cases_name:
            for i, st in enumerate(body):
                if (i > self.case_idx and isinstance(st, ast.For) and isinstance(st.iter, ast.Name)
                        and st.iter.id == self.cases_name and isinstance(st.target, ast.Name)):
                    self.final_idx, self.loopvar = i, st.target.id
        self.family = 'N' if self.final_idx is not None else 'V'
        # ---- fast mode: early exit is exact only if `ok` only ever falls and the exit code follows it -------------
        self.fast, self.fast_reason = self._fast_analysis()
        # ---- hoisting (N family): check each case the moment case() registers it ---------------------------------
        self.hoist, self.hoist_reason, self.helper_idxs = False, 'not an N-family suite', []
        if self.family == 'N':
            self.hoist, self.hoist_reason = self._hoist_analysis()
        # the transform must build (both variants) and compile
        build_test_code(self, Path('C:/mutlib_probe_fx'), hoist=False)
        if self.hoist:
            build_test_code(self, Path('C:/mutlib_probe_fx'), hoist=True)

    # ------------------------------------------------------------------------------------------------------------------
    def _ok_scopes(self):
        """(node, in_module_scope) for every node where the module's `ok` is visible for writing."""
        out = []
        for st in self.tree.body:
            for n in stmt_nodes(st):
                out.append(n)
        for n in ast.walk(self.tree):
            if isinstance(n, _FUNC_NODES) and self.okname in declared_globals(n):
                for b in n.body:
                    out.extend(stmt_nodes(b))
        return out

    def _fast_analysis(self):
        ok = self.okname
        inits = updates = 0
        problems = []
        for n in self._ok_scopes():
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == ok for t in n.targets):
                v = n.value
                if len(n.targets) != 1:
                    problems.append('line %d assigns %s in a chain' % (n.lineno, ok))
                elif isinstance(v, ast.Constant) and v.value is True and inits == 0 and updates == 0:
                    inits += 1
                elif (isinstance(v, ast.BoolOp) and isinstance(v.op, ast.And) and isinstance(v.values[0], ast.Name)
                      and v.values[0].id == ok):
                    updates += 1
                else:
                    problems.append('line %d: %s = %s' % (n.lineno, ok, short(ast.unparse(v), 40)))
            elif isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id == ok:
                if isinstance(n.op, ast.BitAnd):
                    updates += 1
                else:
                    problems.append('line %d: %s %s= ...' % (n.lineno, ok, type(n.op).__name__))
            elif isinstance(n, (ast.AnnAssign, ast.NamedExpr)) and isinstance(n.target, ast.Name) \
                    and n.target.id == ok:
                problems.append('line %d binds %s' % (n.lineno, ok))
            elif isinstance(n, (ast.For, ast.AsyncFor)) and ok in {m.id for m in ast.walk(n.target)
                                                                   if isinstance(m, ast.Name)}:
                problems.append('line %d binds %s as a loop variable' % (n.lineno, ok))
            elif isinstance(n, (ast.With, ast.AsyncWith)) and any(
                    ok in {m.id for m in ast.walk(i.optional_vars) if isinstance(m, ast.Name)}
                    for i in n.items if i.optional_vars is not None):
                problems.append('line %d binds %s in a with' % (n.lineno, ok))
            elif isinstance(n, ast.Name) and n.id == ok and isinstance(n.ctx, ast.Del):
                problems.append('line %d deletes %s' % (n.lineno, ok))
        if inits != 1:
            problems.append('%d initialisations `%s = True`' % (inits, ok))
        if updates == 0:
            problems.append('no `%s &= ...` update' % ok)
        exits = [n for n in ast.walk(self.tree)
                 if (isinstance(n, ast.Call) and ((isinstance(n.func, ast.Attribute) and n.func.attr in ('exit', '_exit'))
                                                  or (isinstance(n.func, ast.Name) and n.func.id in
                                                      ('exit', 'quit', 'SystemExit'))))
                 or (isinstance(n, ast.Raise) and n.exc is not None and root_name(n.exc) == 'SystemExit')]
        last = self.tree.body[-1]
        final_exit = (isinstance(last, ast.Expr) and isinstance(last.value, ast.Call) and last.value in exits
                      and ok in loaded_names(last))
        if not final_exit:
            problems.append('the suite does not end with sys.exit(<depends on %s>)' % ok)
        others = [n for n in exits if not (final_exit and n is last.value)]
        if others:
            problems.append('other exits at lines %s' % sorted({n.lineno for n in others}))
        if problems:
            return False, '; '.join(problems)
        return True, '%d guarded updates of %s' % (updates, ok)

    def _hoist_analysis(self):
        body = self.tree.body
        case_def, loop = body[self.case_idx], body[self.final_idx]
        if any(isinstance(n, (ast.Return, ast.Yield, ast.YieldFrom)) for b in case_def.body for n in stmt_nodes(b)):
            return False, 'case() has a return / yield'
        if loop.orelse:
            return False, 'the final loop has an else clause'
        if _loop_breaks(loop.body):
            return False, 'the final loop body breaks'
        lv = self.loopvar
        for b in loop.body:
            nodes = stmt_nodes(b)
            # `ok = ok and X` reads ok legitimately (the hoisted copy drops the assignment); any other read of ok
            # would see a name that does not exist yet when case() runs
            guard_reads = {id(m.value.values[0]) for m in nodes
                           if isinstance(m, ast.Assign) and isinstance(m.value, ast.BoolOp)
                           and isinstance(m.value.op, ast.And) and isinstance(m.value.values[0], ast.Name)
                           and m.value.values[0].id == self.okname}
            for n in nodes:
                if (isinstance(n, (ast.Subscript, ast.Attribute)) and isinstance(n.ctx, (ast.Store, ast.Del))
                        and root_name(n) == lv):
                    return False, 'the final loop body writes into its case (line %d)' % n.lineno
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in _MUTATORS
                        and root_name(n.func.value) == lv):
                    return False, 'the final loop body mutates its case (line %d)' % n.lineno
                if (isinstance(n, ast.Name) and n.id == self.okname and isinstance(n.ctx, ast.Load)
                        and id(n) not in guard_reads):
                    return False, 'the final loop body reads %s (line %d)' % (self.okname, n.lineno)
                if isinstance(n, _SCOPE_NODES) and self.okname in free_vars(n):
                    return False, 'a function in the final loop body reads %s (line %d)' % (self.okname, n.lineno)
        # the first case() call: everything after it may run AFTER a hoisted check that the original ran later
        first_case = None
        for i, st in enumerate(body):
            if i > self.case_idx and calls_name(st, 'case'):
                first_case = i
                break
        if first_case is None or first_case > self.final_idx:
            return False, 'no case() call before the final loop'
        # module names bound more than once can be read by a lazily run lambda / function with a value the original
        # (which ran every check after the last binding) never saw
        counts = collections.Counter()
        for st in body:
            names = bound_names(st)
            repeated = set()
            for n in stmt_nodes(st):
                if isinstance(n, (ast.For, ast.AsyncFor, ast.While)):
                    repeated |= bound_names(n)
            for x in names:
                counts[x] += 2 if x in repeated else 1
        for n in ast.walk(self.tree):
            if isinstance(n, _FUNC_NODES):
                g = declared_globals(n)
                if g:
                    stored = {m.id for b in n.body for m in stmt_nodes(b)
                              if isinstance(m, ast.Name) and isinstance(m.ctx, (ast.Store, ast.Del))}
                    for x in g & stored:
                        counts[x] += 2
        multi = {x for x, k in counts.items() if k >= 2}
        refs = set()
        for i, st in enumerate(body):
            if i == self.final_idx:
                continue
            for n in stmt_nodes(st):
                if isinstance(n, _SCOPE_NODES):
                    refs |= free_vars(n)
        check_fn = snippet('def _f(%s):\n    pass' % lv)[0]
        check_fn.body = copy.deepcopy(loop.body)
        loop_free = free_vars(check_fn)
        hazard = sorted((refs | loop_free) & multi - {self.okname})
        if hazard:
            return False, 'late-bound module names read lazily: %s' % hazard
        # module-level mutation of objects after the first case() call (files are covered by the read audit)
        module_names = set(counts)
        for i in range(first_case, self.final_idx):
            st = body[i]
            for n in stmt_nodes(st):
                if (isinstance(n, (ast.Subscript, ast.Attribute)) and isinstance(n.ctx, (ast.Store, ast.Del))
                        and root_name(n) in module_names):
                    return False, 'module-level store into %s after the first case (line %d)' % (root_name(n),
                                                                                                n.lineno)
                if (isinstance(n, ast.AugAssign) and isinstance(n.target, (ast.Subscript, ast.Attribute))
                        and root_name(n.target) in module_names):
                    return False, 'module-level store into %s after the first case (line %d)' % (
                        root_name(n.target), n.lineno)
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in _MUTATORS
                        and root_name(n.func.value) in module_names and root_name(n.func.value) != self.cases_name):
                    return False, 'module-level %s.%s() after the first case (line %d)' % (
                        root_name(n.func.value), n.func.attr, n.lineno)
        # helpers the check reads that are defined after case(): copied in front of the hoisted check
        later_defs = {st.name: i for i, st in enumerate(body)
                      if self.case_idx < i < self.final_idx and isinstance(st, _FUNC_NODES)}
        need, todo = set(), list(loop_free & set(later_defs))
        while todo:
            name = todo.pop()
            if name in need:
                continue
            need.add(name)
            todo.extend(free_vars(body[later_defs[name]]) & set(later_defs))
        self.helper_idxs = sorted(later_defs[x] for x in need)
        if self.helper_idxs:
            self.notes.append('helpers copied in front of the hoisted check: %s'
                              % [body[i].name for i in self.helper_idxs])
        return True, 'each case checked when case() registers it (the final loop re-checks survivors)'


def build_test_code(plan, fx_dir, hoist):
    """The transformed suite as a code object: BASE -> fx_dir, guards, phase markers, (hoist) the per-case check."""
    tree = copy.deepcopy(plan.tree)
    body = tree.body
    base = body[plan.base_idx]
    base.value = ast.copy_location(ast.Call(func=ast.Name(PFX + 'Path', ast.Load()),
                                            args=[ast.Constant(str(fx_dir))], keywords=[]), base.value)
    final_lineno = body[plan.final_idx].lineno if plan.final_idx is not None else None
    tree = _GuardRewriter(plan.okname, final_lineno).visit(tree)
    body = tree.body
    inserts = []                                   # (index, statements) applied from the end
    if plan.final_idx is not None:
        mark_final = snippet("%sphase('final')" % PFX)
        mark_post = snippet("%sphase('post')" % PFX)
        for s in mark_final + mark_post:
            ast.copy_location(s, body[plan.final_idx])
        inserts.append((plan.final_idx + 1, mark_post))
        inserts.append((plan.final_idx, mark_final))
    if hoist:
        case_def = body[plan.case_idx]
        head = snippet('%sn0 = len(%s)' % (PFX, plan.cases_name))
        tail = snippet('%safter_case(%s, %sn0, %scheck)' % (PFX, plan.cases_name, PFX, PFX))
        for s in head + tail:
            ast.copy_location(s, case_def.body[0])
        case_def.body = head + case_def.body + tail
        loop = copy.deepcopy(plan.tree.body[plan.final_idx])
        fn = snippet('def %scheck(%s):\n    pass' % (PFX, plan.loopvar))[0]
        rw = _GuardRewriter(plan.okname, label_var=plan.loopvar, drop_assign=True)
        fn.body = [_ContinueToReturn().visit(rw.visit(s)) for s in loop.body]
        ast.copy_location(fn, loop)
        helpers = [copy.deepcopy(plan.tree.body[i]) for i in plan.helper_idxs]
        inserts.append((plan.case_idx + 1, helpers + [fn]))
    for idx, stmts in sorted(inserts, key=lambda x: -x[0]):
        body[idx:idx] = stmts
    ast.fix_missing_locations(tree)
    return compile(tree, str(plan.path), 'exec')


# ======================================================================================================================
# The parse memo (read_run): static plan
# ======================================================================================================================
_IO_NAMES = {'os', 'sys', 'time', 'random', 'datetime', 'glob', 'subprocess', 'io', 'shutil', 'tempfile', 'socket',
             'threading', 'multiprocessing', 'input', 'eval', 'exec', 'compile', 'globals', 'locals', 'vars',
             'setattr', 'delattr', '__import__', 'print', 'breakpoint', 'exit', 'quit', 'open', 'Path', 'PurePath',
             'pathlib', 'codecs', 'builtins', 'importlib', 'mmap', 'fileinput', 'linecache', 'uuid', 'secrets'}
_IMPURE_METHODS = _MUTATORS | {'write', 'writelines', 'close', 'flush', 'seek', 'truncate', 'read', 'readline',
                               'readlines', 'send', 'recv', 'put', 'acquire', 'release', 'wait', 'start', 'join',
                               'cache_clear', 'unlink', 'mkdir', 'rmdir', 'touch', 'write_text', 'write_bytes',
                               'read_text', 'read_bytes', 'iterdir', 'glob', 'rglob', 'stat', 'open'}


class MemoPlan:
    def __init__(self, ok, reason='', dep_hash='', dep_names=(), file_params=frozenset(), params=()):
        self.ok, self.reason, self.dep_hash = ok, reason, dep_hash
        self.dep_names, self.file_params, self.params = tuple(dep_names), frozenset(file_params), tuple(params)


def _file_params(fn, parents):
    """Parameters of read_run used ONLY as `open(p[, read mode])`, `p is (not) None` or `Path(p).is_file()` /
    `.exists()`: the result can depend on them only through the file's existence and bytes."""
    a = fn.args
    params = [x.arg for x in a.posonlyargs + a.args]
    out = set()
    for p in params:
        good = True
        uses = [n for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id == p]
        if not uses:
            continue
        for n in uses:
            par = parents.get(n)
            if isinstance(n.ctx, ast.Store) or isinstance(n.ctx, ast.Del):
                good = False
            elif _open_of(par, n):
                pass
            elif (isinstance(par, ast.Compare) and par.left is n and len(par.ops) == 1
                  and isinstance(par.ops[0], (ast.Is, ast.IsNot)) and isinstance(par.comparators[0], ast.Constant)
                  and par.comparators[0].value is None):
                pass
            elif _path_probe_of(par, n, parents):
                pass
            else:
                good = False
        if good:
            out.add(p)
    return out


def _open_of(call, arg):
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'open'
            and call.args and call.args[0] is arg):
        return False
    modes = list(call.args[1:2]) + [k.value for k in call.keywords if k.arg == 'mode']
    for m in modes:
        if not (isinstance(m, ast.Constant) and isinstance(m.value, str) and not set(m.value) & set('wax+')):
            return False
    return len(call.args) <= 2 or all(isinstance(x, ast.Constant) for x in call.args[2:])


def _path_probe_of(call, arg, parents):
    """`Path(arg).is_file()` / `.exists()` with `call` the inner Path(arg) call."""
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'Path'
            and len(call.args) == 1 and call.args[0] is arg and not call.keywords):
        return False
    attr = parents.get(call)
    outer = parents.get(attr)
    return (isinstance(attr, ast.Attribute) and attr.attr in ('is_file', 'exists') and isinstance(outer, ast.Call)
            and outer.func is attr and not outer.args and not outer.keywords)


def _impurities(fdef, fparams, is_target, module_names):
    parents = parent_map(fdef)
    local = set()
    a = fdef.args
    local |= {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
    local |= {x.arg for x in (a.vararg, a.kwarg) if x is not None}
    for n in ast.walk(fdef):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            local.add(n.id)
        elif isinstance(n, ast.arg):
            local.add(n.arg)
    out = []
    for n in ast.walk(fdef):
        if isinstance(n, (ast.Global, ast.Nonlocal)):
            out.append('global/nonlocal at line %d' % n.lineno)
        elif isinstance(n, (ast.Yield, ast.YieldFrom, ast.Await)):
            out.append('generator at line %d' % n.lineno)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in _IO_NAMES and n.id not in local:
            par = parents.get(n)
            if is_target and n.id == 'open' and isinstance(par, ast.Call) and par.func is n and par.args \
                    and isinstance(par.args[0], ast.Name) and par.args[0].id in fparams and _open_of(par, par.args[0]):
                continue
            if is_target and n.id == 'Path' and isinstance(par, ast.Call) and par.func is n and par.args \
                    and isinstance(par.args[0], ast.Name) and par.args[0].id in fparams \
                    and _path_probe_of(par, par.args[0], parents):
                continue
            out.append('uses %s at line %d' % (n.id, n.lineno))
        elif isinstance(n, (ast.Subscript, ast.Attribute)) and isinstance(n.ctx, (ast.Store, ast.Del)):
            r = root_name(n)
            if r is None or (r not in local):
                out.append('stores into %s at line %d' % (r, n.lineno))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in _IMPURE_METHODS:
            r = root_name(n.func.value)
            if r is None or (r not in local and r in module_names):
                out.append('%s.%s() at line %d' % (r, n.func.attr, n.lineno))
    return out


def plan_memo(src, fname='read_run'):
    """Static plan of the read_run memo for one scorer source: the dependency closure, its hash, the file parameters,
    or the reason the memo is off for this source."""
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return MemoPlan(False, 'syntax error: %s' % exc)
    bindings = collections.defaultdict(list)
    for st in tree.body:
        for n in bound_names(st):
            bindings[n].append(st)
    for st in tree.body:
        for n in ast.walk(st):
            if isinstance(n, _FUNC_NODES):
                g = declared_globals(n)
                stored = {m.id for b in n.body for m in stmt_nodes(b)
                          if isinstance(m, ast.Name) and isinstance(m.ctx, (ast.Store, ast.Del))}
                for x in g & stored:
                    if st not in bindings[x]:
                        bindings[x].append(st)
    defs = bindings.get(fname, [])
    if len(defs) != 1 or not isinstance(defs[0], ast.FunctionDef) or defs[0].name != fname:
        return MemoPlan(False, '%s is not one top-level def' % fname)
    fn = defs[0]
    order, seen_ids, names_seen, todo = [], set(), set(), [fname]
    while todo:
        name = todo.pop()
        if name in names_seen:
            continue
        names_seen.add(name)
        for st in bindings.get(name, ()):
            if id(st) in seen_ids:
                continue
            seen_ids.add(id(st))
            order.append(st)
            todo.extend(r for r in loaded_names(st) if r in bindings and r not in names_seen)
    dep_names = sorted(n for n in names_seen if n in bindings)
    fparams = _file_params(fn, parent_map(fn))
    module_names = set(bindings)
    problems = []
    for st in order:
        for n in ast.walk(st):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and n is not fn:
                if isinstance(n, ast.Lambda):
                    continue
                problems += _impurities(n, set(), False, module_names)
        if st is fn:
            problems += _impurities(fn, fparams, True, module_names)
        elif isinstance(st, ast.ClassDef):
            problems.append('class %s in the dependencies' % st.name)
    if problems:
        return MemoPlan(False, 'not provably pure: %s' % '; '.join(sorted(set(problems))[:4]))
    segs = []
    for st in sorted(order, key=lambda s: (s.lineno, s.col_offset)):
        segs.append(ast.get_source_segment(src, st) or '')
        segs.append(ast.dump(st))
    text = '%s|%s|%s|' % (VERSION, fname, sys.version) + '\n\0\n'.join(segs)
    a = fn.args
    return MemoPlan(True, '', sha256_bytes(text.encode('utf-8')), dep_names, fparams,
                    [x.arg for x in a.posonlyargs + a.args])


# ======================================================================================================================
# Worker runtime
# ======================================================================================================================
class MutantKilled(BaseException):
    def __init__(self, label, lineno, phase):
        super().__init__(label)
        self.label, self.lineno, self.phase = label, lineno, phase


class HoistUnsafe(BaseException):
    pass


class _Bypass(Exception):
    pass


_MISSING = object()
_RT = None                        # the worker's Runtime
_ORIG = {}                        # original os / importlib functions the worker wraps
_WRITE_EVENTS = {'os.remove', 'os.rename', 'os.mkdir', 'os.rmdir', 'shutil.rmtree', 'shutil.copyfile',
                 'shutil.copytree', 'shutil.move', 'os.link', 'os.symlink', 'os.truncate', 'os.chmod', 'os.utime',
                 'os.chown', 'os.chflags', 'os.putenv', 'os.unsetenv', 'os.chdir'}


def _canon(v, depth=0):
    """A process-independent structural image of a data value (sets sorted), or _Bypass."""
    if depth > 40:
        raise _Bypass('value too deep')
    t = type(v)
    if v is None or t in (bool, int, float, complex, str, bytes):
        return (t.__name__, v)
    if t in (tuple, list):
        return (t.__name__, tuple(_canon(x, depth + 1) for x in v))
    if t is dict:
        return ('dict', tuple((_canon(k, depth + 1), _canon(x, depth + 1)) for k, x in v.items()))
    if t in (set, frozenset):
        return (t.__name__, tuple(sorted((_canon(x, depth + 1) for x in v), key=repr)))
    if isinstance(v, re.Pattern):
        return ('re', v.pattern, v.flags)
    if isinstance(v, PurePath):
        return ('path', t.__name__, str(v))
    if t is range:
        return ('range', v.start, v.stop, v.step)
    raise _Bypass('no canonical form for %s' % t.__name__)


class _Suppress:
    def __enter__(self):
        if _RT is not None:
            _RT.suppress += 1

    def __exit__(self, *a):
        if _RT is not None:
            _RT.suppress -= 1


class Memo:
    """read_run memo: key = (dependency hash of read_run's closure in THIS mutant's source, the current values of
    its data dependencies, the bytes of its file arguments, its other arguments); values stored pickled, returned as a
    fresh unpickled copy on hits AND misses.  Disk entries (shared by all workers) only for the unmutated closure."""
    MAGIC = b'MUTLIBM1'

    def __init__(self, cache_dir, shared_src, mem_budget):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.plans = {}
        self.shared_dep = self.plan_for(shared_src).dep_hash
        self.mem, self.mem_bytes, self.budget = collections.OrderedDict(), 0, mem_budget
        self.stats = collections.Counter()
        self.off_reason = None

    def plan_for(self, src):
        key = sha256_bytes(src.encode('utf-8'))
        if key not in self.plans:
            self.plans[key] = plan_memo(src)
        return self.plans[key]

    def install(self, module, src):
        plan = self.plan_for(src)
        fn = module.__dict__.get('read_run')
        if not plan.ok or not isinstance(fn, types.FunctionType):
            self.stats['off'] += 1
            self.off_reason = plan.reason or 'no read_run function'
            return
        deps = {}
        for name in plan.dep_names:
            if name == 'read_run':
                continue
            obj = module.__dict__.get(name, _MISSING)
            meta = (obj.__code__, obj.__defaults__, obj.__kwdefaults__) if isinstance(obj, types.FunctionType) else None
            deps[name] = (obj, meta)
        sig = inspect.signature(fn)
        memo = self

        @functools.wraps(fn)
        def read_run(*args, **kwargs):
            return memo.call(module, plan, fn, sig, deps, args, kwargs)
        module.read_run = read_run
        self.stats['installed'] += 1

    def key(self, module, plan, sig, deps, args, kwargs):
        h = hashlib.sha256()
        h.update(plan.dep_hash.encode())
        for name, (orig, meta) in deps.items():
            cur = module.__dict__.get(name, _MISSING)
            if orig is _MISSING or cur is _MISSING:
                if cur is not orig:
                    raise _Bypass('%s appeared / vanished' % name)
                h.update(b'|missing:' + name.encode())
            elif isinstance(orig, (types.FunctionType, type, types.ModuleType, types.BuiltinFunctionType,
                                   types.MethodType)) or callable(orig) and not isinstance(orig, re.Pattern):
                if cur is not orig:
                    raise _Bypass('%s was rebound' % name)
                if meta is not None and (cur.__code__ is not meta[0] or cur.__defaults__ is not meta[1]
                                         or cur.__kwdefaults__ is not meta[2]):
                    raise _Bypass('%s was modified' % name)
                h.update(b'|obj:' + name.encode())
            else:
                h.update(b'|data:' + name.encode() + b'=' + repr(_canon(cur)).encode())
        try:
            bound = sig.bind(*args, **kwargs)
        except TypeError:
            raise _Bypass('arguments do not bind')
        bound.apply_defaults()
        for pname, val in bound.arguments.items():
            h.update(b'|arg:' + pname.encode() + b'=')
            if pname in plan.file_params:
                if val is None:
                    h.update(b'none')
                elif isinstance(val, (str, os.PathLike)):
                    p = os.fspath(val)
                    if not isinstance(p, str):
                        raise _Bypass('bytes path')
                    if os.path.isfile(p):
                        with open(p, 'rb') as fh:
                            h.update(b'file:' + hashlib.sha256(fh.read()).digest())
                    else:
                        h.update(b'absent')
                else:
                    raise _Bypass('file argument of type %s' % type(val).__name__)
            else:
                h.update(repr(_canon(val)).encode())
        return h.hexdigest()

    def call(self, module, plan, fn, sig, deps, args, kwargs):
        try:
            key = self.key(module, plan, sig, deps, args, kwargs)
        except _Bypass as b:
            self.stats['bypass'] += 1
            self.off_reason = 'bypass: %s' % b
            return fn(*args, **kwargs)
        shared = plan.dep_hash == self.shared_dep
        blob = self.mem.get(key)
        if blob is not None:
            self.mem.move_to_end(key)
            self.stats['hit_mem'] += 1
        elif shared:
            blob = self.disk_get(key)
            if blob is not None:
                self.stats['hit_disk'] += 1
                self.mem_put(key, blob)
        if blob is None:
            result = fn(*args, **kwargs)
            try:
                blob = pickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception:
                self.stats['unpicklable'] += 1
                return result
            self.stats['miss'] += 1
            self.mem_put(key, blob)
            if shared:
                self.disk_put(key, blob)
        return pickle.loads(blob)

    def mem_put(self, key, blob):
        if len(blob) > self.budget:
            return
        self.mem[key] = blob
        self.mem_bytes += len(blob)
        while self.mem_bytes > self.budget:
            _, old = self.mem.popitem(last=False)
            self.mem_bytes -= len(old)

    def disk_get(self, key):
        path = self.dir / (key + '.pkl')
        with _Suppress():
            try:
                data = path.read_bytes()
            except OSError:
                return None
        if len(data) < 40 or data[:8] != self.MAGIC or hashlib.sha256(data[40:]).digest() != data[8:40]:
            self.stats['disk_bad'] += 1
            return None
        return data[40:]

    def disk_put(self, key, blob):
        path = self.dir / (key + '.pkl')
        with _Suppress():
            if path.exists():
                return
            tmp = self.dir / ('%s.%d.tmp' % (key, os.getpid()))
            try:
                tmp.write_bytes(self.MAGIC + hashlib.sha256(blob).digest() + blob)
                os.replace(tmp, path)
                self.stats['disk_put'] += 1
            except OSError:
                try:
                    tmp.unlink()
                except OSError:
                    pass


class Capture:
    """sys.stdout / sys.stderr of the suite: keeps every line with the phase it was printed in, and raises a pending
    MutantKilled on the first line printed after an unlabelled failed guard (that line names the case)."""
    encoding = 'utf-8'
    errors = 'replace'

    def __init__(self, rt):
        self.rt, self.buf = rt, ''

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError('write() argument must be str, not %s' % type(s).__name__)
        if '\n' not in s:
            self.buf += s
            return len(s)
        parts = (self.buf + s).split('\n')
        self.buf = parts[-1]
        for line in parts[:-1]:
            self.rt.on_line(line)
        return len(s)

    def finish(self):
        if self.buf:
            line, self.buf = self.buf, ''
            try:
                self.rt.on_line(line)
            except MutantKilled:
                pass

    def flush(self):
        pass

    def reconfigure(self, *a, **k):
        pass

    def isatty(self):
        return False

    def writable(self):
        return True

    def fileno(self):
        raise io.UnsupportedOperation('fileno')


def _fail_label(line):
    toks = line.split()
    return toks[0] if toks and 'FAIL' in toks[1:] else None


def _module_fp(m):
    items = []
    for k, v in list(m.__dict__.items()):
        if k == '__builtins__':
            continue
        if isinstance(v, types.FunctionType):
            items.append((k, 'f', id(v), id(v.__code__), id(v.__defaults__), id(v.__kwdefaults__)))
        elif isinstance(v, (types.ModuleType, type, types.BuiltinFunctionType, types.MethodType)):
            items.append((k, 'o', id(v)))
        else:
            try:
                r = repr(v)
            except Exception:
                r = '<unrepr %s>' % type(v).__name__
            items.append((k, 'd', id(v), hashlib.sha1(r.encode('utf-8', 'replace')).digest()))
    return tuple(items)


def _stat_sig(path):
    try:
        st = _ORIG['stat'](path)
    except (OSError, ValueError, TypeError):
        return (False,)
    return (True, stat_mod.S_IFMT(st.st_mode), st.st_size, st.st_mtime_ns)


class Runtime:
    def __init__(self):
        self.suppress = 0
        self.in_hoist = False
        self.reset(False, False, None)

    def reset(self, fast, hoist, mutant_path):
        self.fast, self.hoist, self.mutant_path = fast, hoist, mutant_path
        self.phase = 'main'
        self.lines = []
        self.since_guard = []
        self.pending = None
        self.failures = []
        self.hoisted_n = 0
        self.in_hoist = False
        self.hoist_case = None
        self.hoist_writes = []
        self.exit_case = None
        self.reads, self.dirs, self.probes = {}, {}, {}
        self.read_drift = None
        self.scorer_modules = []
        self.test_globals = {}
        self.guards_passed = 0

    def api(self):
        return {PFX + 'Path': Path, PFX + 'guard': self.guard, PFX + 'label': self.label,
                PFX + 'after_case': self.after_case, PFX + 'phase': self.set_phase}

    # ---- output ------------------------------------------------------------------------------------------------------
    def on_line(self, line):
        self.lines.append(('hoist' if self.in_hoist else self.phase, line))
        self.since_guard.append(line)
        if self.pending is not None:
            lineno, self.pending = self.pending, None
            label = _fail_label(line) or 'test line %d' % lineno
            if self.failures and self.failures[-1][0] is None:
                self.failures[-1] = (label,) + self.failures[-1][1:]
            raise MutantKilled(label, lineno, self.phase)

    # ---- the suite's hooks -------------------------------------------------------------------------------------------
    @staticmethod
    def label(item):
        if isinstance(item, dict) and isinstance(item.get('name'), str):
            return item['name']
        if isinstance(item, (tuple, list)) and item and isinstance(item[0], str):
            return item[0]
        return short(repr(item), 60)

    def guard(self, value, label, lineno):
        since, self.since_guard = self.since_guard, []
        if value:
            self.guards_passed += 1
            return value
        if label is None:
            for line in reversed(since):
                label = _fail_label(line)
                if label:
                    break
        phase = 'hoist' if self.in_hoist else self.phase
        self.failures.append((label, lineno, phase))
        if self.fast:
            if label is not None:
                raise MutantKilled(label, lineno, phase)
            self.pending = lineno
        return value

    def set_phase(self, name):
        if name == 'final' and self.hoist:
            self.read_drift = self._drift()
        self.phase = name

    def after_case(self, cases, n0, check):
        if not self.hoist:
            return
        if len(cases) != n0 + 1:
            raise HoistUnsafe('case() appended %d items' % (len(cases) - n0))
        if not self.scorer_modules:
            raise HoistUnsafe('the scorer was not loaded through importlib.util.spec_from_file_location')
        item = cases[-1]
        lab = self.label(item)
        before = self.state_fp()
        self.in_hoist, self.hoist_case, self.hoist_writes = True, lab, []
        try:
            check(item)
        except (MutantKilled, HoistUnsafe):
            raise
        except SystemExit:
            self.exit_case = lab
            raise
        except Exception as exc:
            raise HoistUnsafe('hoisted check of %s raised %s' % (lab, exc_line(exc)))
        finally:
            self.in_hoist = False
        if self.hoist_writes:
            raise HoistUnsafe('hoisted check of %s wrote %s' % (lab, short(self.hoist_writes[:3], 120)))
        if self.state_fp() != before:
            raise HoistUnsafe('hoisted check of %s left interpreter state changed' % lab)
        self.hoisted_n += 1

    def state_fp(self):
        out = [_module_fp(m) for m in self.scorer_modules]
        out.append(tuple(sorted((k, id(v)) for k, v in self.test_globals.items() if not k.startswith(PFX))))
        out.append(tuple(sorted(os.environ.items())))
        out.append(os.getcwd())
        return out

    # ---- the file-system audit of hoisted checks ---------------------------------------------------------------------
    def on_audit(self, event, args):
        if event == 'open':
            path, mode, flags = (tuple(args) + (None, None, None))[:3]
            if path is None or isinstance(path, int):
                return
            path = os.fsdecode(os.fspath(path))
            if mode is not None:
                writing = bool(set(str(mode)) & set('wax+'))
            else:
                writing = bool((flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))
            if writing:
                self.hoist_writes.append('open(%s, %r)' % (path, mode if mode is not None else flags))
            else:
                self.note(path)
        elif event in _WRITE_EVENTS:
            self.hoist_writes.append('%s%r' % (event, tuple(args)[:2]))
        elif event in ('os.listdir', 'os.scandir'):
            p = args[0] if args and args[0] is not None else '.'
            if isinstance(p, int):
                return
            p = os.path.abspath(os.fsdecode(os.fspath(p)))
            if p not in self.dirs:
                self.suppress += 1
                try:
                    self.dirs[p] = sorted(_ORIG['listdir'](p))
                except OSError:
                    self.dirs[p] = None
                finally:
                    self.suppress -= 1

    def note(self, path):
        try:
            p = os.path.abspath(os.fsdecode(os.fspath(path)))
        except (TypeError, ValueError):
            return
        if p not in self.reads:
            self.suppress += 1
            try:
                self.reads[p] = _stat_sig(p)
            finally:
                self.suppress -= 1

    def _drift(self):
        self.suppress += 1
        try:
            out = [p for p, sig in self.reads.items() if _stat_sig(p) != sig]
            for p, listing in self.dirs.items():
                try:
                    now = sorted(_ORIG['listdir'](p))
                except OSError:
                    now = None
                if now != listing:
                    out.append(p + os.sep)
            return out
        finally:
            self.suppress -= 1


def _audit_hook(event, args):
    rt = _RT
    if rt is None or not rt.in_hoist or rt.suppress:
        return
    try:
        rt.on_audit(event, args)
    except Exception:
        pass


def _probe_wrapper(orig):
    def probe(path, *a, **k):
        rt = _RT
        if rt is not None and rt.in_hoist and not rt.suppress and not isinstance(path, int):
            rt.note(path)
        return orig(path, *a, **k)
    functools.update_wrapper(probe, orig)
    return probe


def _install_worker_hooks():
    _ORIG['stat'] = os.stat
    _ORIG['listdir'] = os.listdir
    os.stat = _probe_wrapper(os.stat)
    os.lstat = _probe_wrapper(os.lstat)
    for name in ('exists', 'isfile', 'isdir', 'lexists', 'getsize', 'getmtime'):
        setattr(os.path, name, _probe_wrapper(getattr(os.path, name)))
    sys.addaudithook(_audit_hook)
    import importlib.util as ilu
    orig_sffl = ilu.spec_from_file_location

    def spec_from_file_location(*a, **k):
        spec = orig_sffl(*a, **k)
        rt = _RT
        try:
            same = (rt is not None and rt.mutant_path is not None and spec is not None and spec.origin
                    and os.path.normcase(os.path.abspath(spec.origin))
                    == os.path.normcase(os.path.abspath(str(rt.mutant_path))))
        except Exception:
            same = False
        if same:
            loader = spec.loader
            orig_exec = loader.exec_module

            def exec_module(module):
                orig_exec(module)
                _WORKER.on_scorer_loaded(module)
            loader.exec_module = exec_module
        return spec
    ilu.spec_from_file_location = spec_from_file_location


_WORKER = None


class Worker:
    def __init__(self, wid, cfg):
        global _RT, _WORKER
        self.wid, self.cfg = wid, cfg
        sys.dont_write_bytecode = True
        self.dir = Path(cfg['work']) / ('w%d' % wid)
        shutil.rmtree(self.dir, ignore_errors=True)
        self.dir.mkdir(parents=True)
        self.fx = self.dir / 'fx'
        self.mdir = self.dir / 'm'
        self.mutant_path = self.mdir / cfg['scorer_name']
        self.test_path = Path(cfg['test_path'])
        self.plan = TestPlan(self.test_path, cfg['test_src'], cfg['okname'])
        self.code = {False: build_test_code(self.plan, self.fx, hoist=False)}
        if self.plan.hoist:
            self.code[True] = build_test_code(self.plan, self.fx, hoist=True)
        self.memo = Memo(cfg['cache'], cfg['scorer_src'], cfg['memo_mem']) if cfg['memo'] else None
        self.rt = _RT = Runtime()
        _WORKER = self
        _install_worker_hooks()
        self.src = None

    def on_scorer_loaded(self, module):
        self.rt.scorer_modules.append(module)
        if self.memo is not None:
            self.memo.install(module, self.src)

    def run(self, job):
        t0 = time.perf_counter()
        hoist = bool(job['hoist'] and self.plan.hoist)
        res = self.run_once(job, hoist)
        if res['outcome'] == 'unsafe':
            reason = res['label']
            first_seconds = time.perf_counter() - t0
            res = self.run_once(job, False)
            res['fallback'] = reason
            res['fallback_seconds'] = first_seconds
        res['seconds'] = time.perf_counter() - t0
        return res

    def run_once(self, job, hoist):
        rt, cfg = self.rt, self.cfg
        with _Suppress():
            shutil.rmtree(self.fx, ignore_errors=True)
            shutil.rmtree(self.mdir, ignore_errors=True)
            self.mdir.mkdir(parents=True)
            self.mutant_path.write_bytes(job['src'].encode('utf-8'))
        self.src = job['src']
        rt.reset(job['fast'], hoist, self.mutant_path)
        if self.memo is not None:
            self.memo.stats = collections.Counter()
            self.memo.off_reason = None
        g = {'__name__': '__main__', '__file__': str(self.test_path), '__builtins__': builtins, '__doc__': None,
             '__package__': None, '__spec__': None, '__loader__': None}
        g.update(rt.api())
        rt.test_globals = g
        argv = [str(self.test_path), str(self.mutant_path)] + ([str(self.fx)] if self.plan.uses_argv2 else [])
        saved = (sys.argv, sys.stdout, sys.stderr, dict(os.environ), os.getcwd(), list(sys.path), set(sys.modules))
        cap = Capture(rt)
        res = {'name': job['name'], 'kind': job['kind'], 'hoist': hoist, 'fast': job['fast'], 'fallback': None,
               'label': None, 'lineno': None, 'phase': None, 'exit_code': None, 'crash': None}
        sys.argv, sys.stdout, sys.stderr = argv, cap, cap
        sys.path.insert(0, str(self.test_path.parent))
        try:
            exec(self.code[hoist], g)
            res['outcome'], res['exit_code'] = 'exit', 0
        except SystemExit as e:
            code = e.code
            res['outcome'] = 'exit'
            if code is None:
                res['exit_code'] = 0
            elif isinstance(code, int):
                res['exit_code'] = code
            else:
                res['exit_code'] = 1
                res['exit_msg'] = short(code, 100)
            res['exit_case'] = rt.exit_case
        except MutantKilled as k:
            res.update(outcome='killed', label=k.label, lineno=k.lineno, phase=k.phase)
        except HoistUnsafe as h:
            res.update(outcome='unsafe', label=str(h))
        except KeyboardInterrupt:
            raise
        except BaseException as e:
            res.update(outcome='crash', crash=exc_line(e), phase='hoist' if rt.in_hoist else rt.phase)
        finally:
            cap.finish()
            sys.argv, sys.stdout, sys.stderr = saved[0], saved[1], saved[2]
            if dict(os.environ) != saved[3]:
                os.environ.clear()
                os.environ.update(saved[3])
            if os.getcwd() != saved[4]:
                os.chdir(saved[4])
            sys.path[:] = saved[5]
            for name in set(sys.modules) - saved[6]:
                f = getattr(sys.modules.get(name), '__file__', None) or ''
                if f and str(self.dir).lower() in os.path.abspath(f).lower():
                    del sys.modules[name]
        lines = rt.lines
        texts = [t for _, t in lines]
        res['saw_all_ok'] = any(t.strip() == 'ALL OK' for t in texts)
        res['saw_fixture_failures'] = any(t.strip() == 'FIXTURE FAILURES' for t in texts)
        res['failures'] = rt.failures[:5]
        res['n_failures'] = len(rt.failures)
        res['pending'] = rt.pending
        res['guards_passed'] = rt.guards_passed
        res['hoisted_n'] = rt.hoisted_n
        res['reached_post'] = rt.phase == 'post'
        if hoist and rt.phase == 'post':
            hl = [t for p, t in lines if p == 'hoist']
            fl = [t for p, t in lines if p == 'final']
            res['hoist_equal'] = hl == fl
            if hl != fl:
                diff = [(a, b) for a, b in zip(hl, fl) if a != b]
                res['hoist_diff'] = short(diff[:2] if diff else 'hoist %d lines, final %d lines' % (len(hl), len(fl)),
                                          300)
            res['read_drift'] = (rt.read_drift or [])[:5]
            res['n_reads'] = len(rt.reads) + len(rt.dirs)
        res['n_lines'] = len(texts)
        res['tail'] = [short(t, 200) for t in texts[-4:]]
        res['memo'] = dict(self.memo.stats) if self.memo is not None else None
        res['memo_note'] = self.memo.off_reason if self.memo is not None else None
        g.clear()
        rt.test_globals = {}
        rt.scorer_modules = []
        gc.collect()
        return res


def _worker_entry(wid, conn, cfg):
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except (ValueError, OSError):
        pass
    try:
        w = Worker(wid, cfg)
    except BaseException as e:
        conn.send({'init_error': exc_line(e) + '\n' + traceback.format_exc()})
        return
    conn.send({'ready': wid})
    while True:
        try:
            job = conn.recv()
        except (EOFError, OSError):
            break
        if job is None:
            break
        try:
            res = w.run(job)
        except BaseException as e:
            res = {'name': job['name'], 'kind': job['kind'], 'outcome': 'harness_error', 'crash': exc_line(e),
                   'trace': traceback.format_exc(), 'seconds': 0.0, 'hoist': job['hoist'], 'fast': job['fast']}
        try:
            conn.send(res)
        except (EOFError, OSError, BrokenPipeError):
            break
    try:
        shutil.rmtree(w.dir, ignore_errors=True)
    except Exception:
        pass


# ======================================================================================================================
# The parent: pool, scheduling, verdicts, report
# ======================================================================================================================
def classify(res, require_all_ok):
    """-> (verdict, detail).  verdict: KILLED | SURVIVED | TIMEOUT | ERROR."""
    o = res.get('outcome')
    if o == 'timeout':
        # never counted as killed: a slow mutant whose suite would still pass must not hide behind the clock
        return 'TIMEOUT', 'TIMEOUT after %.0f s (unresolved, not counted as killed; raise --timeout)' % res['seconds']
    if o == 'died':
        return 'KILLED', 'KILLED (crash: worker process died, exit code %s)' % res.get('exit_code')
    if o == 'harness_error':
        return 'ERROR', 'HARNESS ERROR (%s)' % res.get('crash')
    if o == 'killed':
        return 'KILLED', 'KILLED by %s' % res['label']
    if o == 'crash':
        return 'KILLED', 'KILLED (crash: %s)' % res['crash']
    if res.get('failures'):
        lab = res['failures'][0][0] or 'test line %s' % res['failures'][0][1]
        return 'KILLED', 'KILLED by %s' % lab
    if res.get('pending') is not None:
        return 'KILLED', 'KILLED by test line %s' % res['pending']
    if res.get('exit_code') != 0:
        where = ' in %s' % res['exit_case'] if res.get('exit_case') else ''
        return 'KILLED', 'KILLED by exit %s%s%s' % (res.get('exit_code'), where,
                                                    (' (%s)' % res['exit_msg']) if res.get('exit_msg') else '')
    if res.get('saw_fixture_failures'):
        return 'KILLED', 'KILLED by FIXTURE FAILURES'
    if require_all_ok and not res.get('saw_all_ok'):
        return 'KILLED', 'KILLED (the suite exited 0 without printing ALL OK)'
    return 'SURVIVED', 'SURVIVED'


class _Slot:
    def __init__(self, wid, proc, conn):
        self.wid, self.proc, self.conn = wid, proc, conn
        self.job = None
        self.t0 = None
        self.ready = False


class Pool:
    def __init__(self, n, cfg):
        self.ctx = mp.get_context('spawn')
        self.cfg = cfg
        self.slots = [self._start(k) for k in range(n)]

    def _start(self, wid):
        parent, child = self.ctx.Pipe()
        p = self.ctx.Process(target=_worker_entry, args=(wid, child, self.cfg), daemon=True,
                             name='mutlib-w%d' % wid)
        p.start()
        child.close()
        return _Slot(wid, p, parent)

    def restart(self, slot):
        self.kill(slot)
        new = self._start(slot.wid)
        self.slots[self.slots.index(slot)] = new
        return new

    @staticmethod
    def kill(slot):
        try:
            slot.proc.terminate()
        except Exception:
            pass
        slot.proc.join(10)
        if slot.proc.is_alive():
            try:
                slot.proc.kill()
            except Exception:
                pass
            slot.proc.join(5)
        try:
            slot.conn.close()
        except Exception:
            pass

    def close(self, force=False):
        if force:
            for s in self.slots:
                self.kill(s)
            return
        for s in self.slots:
            try:
                if s.proc.is_alive() and s.job is None and s.ready:
                    s.conn.send(None)
            except Exception:
                pass
        deadline = time.time() + 20
        for s in self.slots:
            s.proc.join(max(0.1, deadline - time.time()))
        for s in self.slots:
            if s.proc.is_alive():
                self.kill(s)


def run_jobs(pool, jobs, on_result, timeout_of, log):
    """Feed jobs (a deque, may grow from on_result) to the pool; on_result(job, res) -> None."""
    busy = {}
    while jobs or busy:
        for s in list(pool.slots):
            if s.job is None and s.ready and jobs:
                job = jobs.popleft()
                s.job, s.t0 = job, time.time()
                try:
                    s.conn.send(job)
                except (OSError, BrokenPipeError):
                    jobs.appendleft(job)
                    s.job = None
                    pool.restart(s)
                    continue
                busy[s.wid] = s
        conns = {s.conn: s for s in pool.slots if s.proc.is_alive() or s.job is not None}
        ready = mp_wait(list(conns), timeout=1.0) if conns else []
        for c in ready:
            s = conns[c]
            try:
                msg = c.recv()
            except (EOFError, OSError):
                msg = None
            if msg is None:
                job = s.job
                code = s.proc.exitcode
                new = pool.restart(s)
                busy.pop(s.wid, None)
                if job is not None:
                    on_result(job, {'name': job['name'], 'kind': job['kind'], 'outcome': 'died', 'exit_code': code,
                                    'seconds': time.time() - s.t0, 'hoist': job['hoist'], 'fast': job['fast']})
                del new
                continue
            if 'init_error' in msg:
                raise HarnessError('worker %d failed to start: %s' % (s.wid, msg['init_error']))
            if 'ready' in msg:
                s.ready = True
                continue
            job = s.job
            s.job = None
            busy.pop(s.wid, None)
            on_result(job, msg)
        now = time.time()
        for s in list(pool.slots):
            if s.job is not None and now - s.t0 > timeout_of(s.job):
                job = s.job
                log('timeout: %s after %.0f s, restarting worker %d' % (job['name'], now - s.t0, s.wid))
                pool.restart(s)
                busy.pop(s.wid, None)
                on_result(job, {'name': job['name'], 'kind': job['kind'], 'outcome': 'timeout',
                                'seconds': now - s.t0, 'hoist': job['hoist'], 'fast': job['fast']})


def _fmt_memo(m):
    if not m:
        return 'memo off'
    keys = ('hit_mem', 'hit_disk', 'miss', 'bypass', 'off')
    return 'memo ' + ' '.join('%s=%d' % (k, m.get(k, 0)) for k in keys if m.get(k))


def main(argv=None):
    ap = argparse.ArgumentParser(description='fast, strict, shared mutation harness (see README.md)')
    ap.add_argument('--scorer', required=True, help='the scorer under test (the sealed copy when there is one)')
    ap.add_argument('--test', required=True, help='its fixture suite test_*.py')
    ap.add_argument('--mutants', required=True, help='its mutant script mut_*.py (read, never run)')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 1) - 4))
    ap.add_argument('--no-memo', action='store_true', help='no read_run parse memo')
    ap.add_argument('--no-hoist', action='store_true', help='N family: check cases only in the final loop')
    ap.add_argument('--no-fast', action='store_true', help='no early exit: every suite runs to its end')
    ap.add_argument('--only', help='comma-separated mutant names')
    ap.add_argument('--changed-from', help='parent scorer: run mutants whose anchor touches a changed line ...')
    ap.add_argument('--sample', type=float, default=None, help='... plus this fraction of the rest (default 0.2)')
    ap.add_argument('--seed', type=int, default=None, help='sample seed (default: from the scorer sha256)')
    ap.add_argument('--control', action='store_true', help='add three equivalent mutants that must survive')
    ap.add_argument('--timeout', type=float, default=0.0, help='seconds per mutant (default max(120, 3 x baseline))')
    ap.add_argument('--out', help='also write the report here')
    ap.add_argument('--ok-name', default='ok', help="the suite's pass flag (default ok)")
    ap.add_argument('--cache-dir', default=None, help='read_run memo cache root (default mutlib/cache)')
    ap.add_argument('--work-dir', default=str(HERE / 'work'))
    ap.add_argument('--memo-mem-mb', type=int, default=256, help='in-memory memo budget per worker')
    ap.add_argument('--keep-work', action='store_true')
    ap.add_argument('--dry-run', action='store_true', help='print the header and the selection, run nothing')
    args = ap.parse_args(argv)

    t_start = time.time()
    log = lambda msg: print(msg, file=sys.stderr, flush=True)  # noqa: E731
    if SEALED_LOCK.exists():
        log('refusing: %s exists (a sealed run is in progress; no parallel CPU work)' % SEALED_LOCK)
        return 3
    scorer = Path(args.scorer).resolve()
    test = Path(args.test).resolve()
    mutf = Path(args.mutants).resolve()
    scorer_bytes = scorer.read_bytes()
    scorer_src = scorer_bytes.decode('utf-8')
    scorer_sha = sha256_bytes(scorer_bytes)
    test_bytes = test.read_bytes()
    test_src = test_bytes.decode('utf-8')
    header = ['%s  harness %s sha256 %s' % (VERSION, HARNESS, sha256_file(HARNESS)),
              'scorer  %s sha256 %s' % (scorer, scorer_sha),
              'test    %s sha256 %s' % (test, sha256_bytes(test_bytes)),
              'mutants %s sha256 %s' % (mutf, sha256_file(mutf))]
    try:
        fmt, mutants, lines_run = extract_mutants(mutf)
        validate_mutants(mutants, scorer_src)
        plan = TestPlan(test, test_src, args.ok_name)
    except HarnessError as e:
        for h in header:
            print(h)
        print('REFUSED: %s' % e)
        return 3
    header.append('mutants: format %s, %d defined (statements evaluated at lines %s)'
                  % (fmt, len(mutants), _ranges(lines_run)))
    names = [m[0] for m in mutants]
    selected = names
    if args.only:
        want = [x.strip() for x in args.only.split(',') if x.strip()]
        unknown = [x for x in want if x not in names]
        if unknown:
            print('REFUSED: unknown mutant names %s' % unknown)
            return 3
        selected = [n for n in names if n in want]
        header.append('selection: --only, %d mutants' % len(selected))
    if args.changed_from:
        parent_src = Path(args.changed_from).read_bytes().decode('utf-8')
        changed = changed_lines(parent_src, scorer_src)
        by = {n: (o, w) for n, o, w in mutants}
        touch = []
        for n in selected:
            a, b = anchor_lines(scorer_src, by[n][0])
            if any(x in changed for x in range(a, b + 1)):
                touch.append(n)
        rest = [n for n in selected if n not in touch]
        frac = 0.2 if args.sample is None else args.sample
        seed = args.seed if args.seed is not None else int(scorer_sha[:16], 16)
        k = min(len(rest), int(round(frac * len(rest))))
        sample = set(random.Random(seed).sample(rest, k)) if k else set()
        selected = [n for n in selected if n in touch or n in sample]
        header.append('selection: --changed-from %s (%d changed lines): %d touching + sample %d of %d (fraction %.3f, '
                      'seed %d)' % (Path(args.changed_from).resolve(), len(changed), len(touch), len(sample),
                                    len(rest), frac, seed))
        header.append('  touching: %s' % (touch or 'none'))
    memo_on = not args.no_memo
    memo_plan = plan_memo(scorer_src)
    if memo_on and not memo_plan.ok:
        header.append('memo: off for this scorer (%s)' % memo_plan.reason)
        memo_on = False
    fast = plan.fast and not args.no_fast
    hoist = plan.hoist and not args.no_hoist
    header.append('suite: family %s; fast %s (%s); hoist %s (%s)%s'
                  % (plan.family, 'on' if fast else 'OFF', 'disabled by --no-fast' if args.no_fast and plan.fast
                     else plan.fast_reason, 'on' if hoist else 'off',
                     'disabled by --no-hoist' if args.no_hoist and plan.hoist else plan.hoist_reason,
                     ('; ' + '; '.join(plan.notes)) if plan.notes else ''))
    cache_root = Path(args.cache_dir) if args.cache_dir else HERE / 'cache'
    cache_dir = cache_root / scorer.stem
    if memo_on:
        header.append('memo: read_run, %d dependencies %s, file params %s, dep hash %s, cache %s'
                      % (len(memo_plan.dep_names), list(memo_plan.dep_names), sorted(memo_plan.file_params),
                         memo_plan.dep_hash[:16], cache_dir))
    controls = control_mutants(scorer_src, 'read_run' if memo_on else 'evaluate') if args.control else []
    run_dir = Path(args.work_dir) / ('%s_%d_%d' % (scorer.stem, os.getpid(), int(time.time())))
    workers = max(1, min(args.workers, len(selected) + len(controls) + 1))
    header.append('workers %d (spawn), work dir %s' % (workers, run_dir))
    for h in header:
        print(h, flush=True)
    printed_header = len(header)
    if args.dry_run:
        print('dry run: %d selected mutants: %s' % (len(selected), selected))
        print('controls: %s' % ([c[0] for c in controls] or 'none'))
        return 0
    # dispatch order only (the report keeps definition order): the slowest mutants of the last run first, new ones
    # before known ones, so the run does not end on a long tail
    durations_file = cache_root / scorer.stem / 'durations.json'
    try:
        prev = json.loads(durations_file.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        prev = {}
    dispatch = sorted(selected, key=lambda n: -float(prev.get(n, 1e9)))
    by_name = {n: (o, w) for n, o, w in mutants}
    cfg = {'work': str(run_dir), 'scorer_name': scorer.name, 'test_path': str(test), 'test_src': test_src,
           'okname': args.ok_name, 'scorer_src': scorer_src, 'memo': memo_on, 'cache': str(cache_dir),
           'memo_mem': args.memo_mem_mb * 1024 * 1024}

    def mk(kind, name, src, h):
        return {'kind': kind, 'name': name, 'src': src, 'fast': fast and kind != 'baseline', 'hoist': h}

    state = {'hoist': hoist, 'baseline': None, 'timeout': args.timeout or 1800.0, 'require_all_ok': True,
             'done': 0}
    results = {}
    jobs = collections.deque()
    total = len(selected) + len(controls)

    def queue_all(h):
        jobs.append(mk('baseline', 'BASELINE', scorer_src, h))
        for name, old, new in controls:
            jobs.append(mk('control', name, scorer_src.replace(old, new), h))
        for n in dispatch:
            old, new = by_name[n]
            jobs.append(mk('mutant', n, scorer_src.replace(old, new), h))

    def timeout_of(job):
        if job['kind'] == 'baseline':
            return 10.0 * args.timeout if args.timeout else 4 * 3600.0
        return state['timeout']

    def on_result(job, res):
        if job['kind'] == 'baseline':
            state['baseline'] = res
            verdict, detail = classify(res, False)
            if res.get('outcome') == 'harness_error':
                raise HarnessError('baseline: harness error %s\n%s' % (res.get('crash'), res.get('trace', '')))
            if job['hoist']:
                why = None
                if verdict != 'SURVIVED':
                    why = 'the baseline failed with hoisting (%s); retrying it faithfully' % detail
                elif res.get('fallback'):
                    why = 'the baseline needed a faithful rerun: %s' % res['fallback']
                elif not res.get('hoist_equal'):
                    why = 'hoisted and final-loop results differ on the baseline: %s' % res.get('hoist_diff')
                elif res.get('read_drift'):
                    why = 'files read by hoisted checks changed before the final loop: %s' % res['read_drift']
                if why:
                    raise _Rehoist(why)
            if verdict != 'SURVIVED':
                raise HarnessError('the unmutated scorer does not pass its own suite in this harness: %s; last lines '
                                   '%s' % (detail, res.get('tail')))
            state['require_all_ok'] = bool(res.get('saw_all_ok'))
            if not args.timeout:
                state['timeout'] = max(120.0, 3.0 * res['seconds'])
            log('BASELINE passed in %.1f s (%s; hoisted checks %s; %s); mutant timeout %.0f s'
                % (res['seconds'], 'hoist' if job['hoist'] else 'faithful', res.get('hoisted_n'),
                   _fmt_memo(res.get('memo')), state['timeout']))
            return
        if job['hoist'] and not state['hoist']:
            jobs.append(dict(job, hoist=False))
            return
        results[job['name']] = res
        state['done'] += 1
        verdict, detail = classify(res, state['require_all_ok'])
        log('[%d/%d] %s' % (state['done'], total, _line(job['kind'], job['name'], res, detail)))

    pool = None
    finished = False
    try:
        for attempt in (0, 1):
            queue_all(state['hoist'])
            pool = Pool(workers, cfg)
            try:
                run_jobs(pool, jobs, on_result, timeout_of, log)
                finished = True
                break
            except _Rehoist as r:
                log('hoisting disabled: %s -> restarting every job in faithful mode' % r)
                header.append('hoist: DISABLED at run time (%s)' % r)
                state['hoist'] = False
                results.clear()
                state['done'] = 0
                jobs.clear()
                pool.close(force=True)
                pool = None
    except HarnessError as e:
        print('REFUSED: %s' % e)
        return 3
    finally:
        if pool is not None:
            pool.close(force=not finished)
        if not args.keep_work:
            shutil.rmtree(run_dir, ignore_errors=True)
    try:
        prev.update({n: round(r.get('seconds', 0.0), 1) for n, r in results.items()})
        durations_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = durations_file.with_name('durations.json.%d.tmp' % os.getpid())
        tmp.write_text(json.dumps(prev, indent=0, sort_keys=True), encoding='utf-8')
        os.replace(tmp, durations_file)
    except OSError:
        pass
    # ---- report ----------------------------------------------------------------------------------------------------
    b = state['baseline']
    out = list(header)
    out.append(_line('baseline', 'BASELINE', b, 'SURVIVED'))
    rows = collections.Counter()
    survivors, bad_controls, notes = [], [], []
    for name, _, _ in controls:
        res = results[name]
        verdict, detail = classify(res, state['require_all_ok'])
        out.append(_line('control', name, res, detail))
        if verdict != 'SURVIVED':
            bad_controls.append(name)
        elif res.get('hoist') and res.get('reached_post') and not res.get('hoist_equal', True):
            notes.append('%s: hoisted and final results differ (%s)' % (name, res.get('hoist_diff')))
    for n in selected:
        res = results[n]
        verdict, detail = classify(res, state['require_all_ok'])
        rows[verdict] += 1
        if detail.startswith('KILLED (crash'):
            rows['crash'] += 1
        if res.get('fallback'):
            rows['fallback'] += 1
        out.append(_line('mutant', n, res, detail))
        if verdict == 'SURVIVED':
            survivors.append(n)
            if res.get('hoist') and not res.get('hoist_equal', True):
                notes.append('%s: hoisted and final results differ (%s)' % (n, res.get('hoist_diff')))
    wall = time.time() - t_start
    cpu = sum(r.get('seconds', 0.0) for r in results.values()) + (b.get('seconds', 0.0) if b else 0.0)
    unresolved = [n for n in selected if classify(results[n], True)[0] in ('TIMEOUT', 'ERROR')]
    out.append('%d mutants: %d killed (%d by a crash of the suite), %d survived, %d unresolved (timeout / harness '
               'error); %d needed a faithful rerun' % (len(selected), rows['KILLED'], rows['crash'],
                                                       rows['SURVIVED'], len(unresolved), rows['fallback']))
    if controls:
        out.append('controls: %d of %d survived%s' % (len(controls) - len(bad_controls), len(controls),
                                                      (' - KILLED: %s' % bad_controls) if bad_controls else ''))
    if unresolved:
        out.append('UNRESOLVED: %s' % unresolved)
    for note in notes:
        out.append('WARNING %s' % note)
    out.append('wall %.1f s, worker time %.1f s, %d workers' % (wall, cpu, workers))
    if survivors:
        out.append('SURVIVORS: %s' % survivors)
    elif unresolved or bad_controls or notes:
        out.append('NOT CERTIFIED (see UNRESOLVED / controls / WARNING above)')
    else:
        out.append('ALL KILLED')
    text = '\n'.join(out)
    print('\n'.join(out[printed_header:]))
    if args.out:
        Path(args.out).write_text(text + '\n', encoding='utf-8')
    if survivors:
        return 1
    return 2 if (unresolved or bad_controls or notes) else 0


class _Rehoist(Exception):
    pass


def _ranges(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else '%d-%d' % (nums[i], nums[j]))
        i = j + 1
    return ','.join(out)


def _line(kind, name, res, detail):
    prefix = {'control': 'CONTROL ', 'baseline': ''}.get(kind, '')
    extra = []
    if res.get('fallback'):
        extra.append('faithful rerun: %s' % short(res['fallback'], 120))
    if res.get('phase') == 'final' and res.get('hoist') and res.get('outcome') == 'killed':
        extra.append('found in the final loop')
    s = '%s%s  %s  (%.1f s)' % (prefix, name, detail, res.get('seconds', 0.0))
    if extra:
        s += '  [%s]' % '; '.join(extra)
    return s


if __name__ == '__main__':
    sys.exit(main())
