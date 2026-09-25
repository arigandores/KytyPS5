#!/usr/bin/env python3
"""mutlib.py v3 - a fast, strict, shared mutation harness for the session log scorers (a scorer X.py certified by a
fixture suite test_X.py and a mutant list mut_X.py).  Design, guarantees, what changed from v1 / v2 and why, residual
assumptions: README.md next to this file (v1 is kept as mutlib_v1.py, v2 as mutlib_v2.py).

    python mutlib.py --scorer S --test T --mutants M [--workers N] [--no-memo] [--no-fast]
                     [--only a,b] [--changed-from PARENT_SCORER --sample 0.2 --seed N] [--control]
                     [--timeout SEC] [--out FILE]

Nothing is edited: the mutant scorer is written into a per-job scratch directory under mutlib/work, the fixture suite
is transformed in memory (AST: fixture directory, guarded `ok` updates, an end-of-suite marker, output hooks), compiled
once and executed in-process by a FRESH spawned process per job (its stdout / stderr are real files), the mutants are
read from the mutant script by evaluating only the statements that define them (any other statement that mentions the
mutant collection, a second collection of (name, old, new) tuples, or a substitution in the harness part whose text
does not come from the recognised collection makes the extraction refuse).
"""
import argparse
import ast
import builtins
import codecs
import collections
import copy
import difflib
import functools
import hashlib
import importlib
import inspect
import io
import json
import locale
import marshal
import os
import pickle
import queue
import random
import re
import shutil
import signal
import sys
import threading
import time
import tokenize
import traceback
import types
import multiprocessing as mp
from multiprocessing.connection import wait as mp_wait
from pathlib import Path, PurePath

HERE = Path(__file__).resolve().parent
HARNESS = Path(__file__).resolve()
SEALED_LOCK = Path('C:/kyty/SEALED_RUN.lock')
PFX = '_mutlib_'
VERSION = 'mutlib 3'
DRAFT_MARK_RE = re.compile(r'^#\s*mutlib:\s*draft-only\b')     # a comment that STARTS with the marker
# harness frames that can sit ABOVE a suite / scorer frame: the audit hook (about 6 frames) and, when the parse memo is
# on, the read_run wrapper and its key (up to about 50: _canon descends at most 41 levels).  The job's recursion limit
# is raised by the frames below the suite plus this margin (README: residual assumptions)
RECURSION_MARGIN = 16
RECURSION_MARGIN_MEMO = 64


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


def same_file(a, b):
    try:
        return os.path.normcase(os.path.abspath(str(a))) == os.path.normcase(os.path.abspath(str(b)))
    except (TypeError, ValueError):
        return False


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


def _enclosing_scope(n, parents):
    p = parents.get(n)
    while p is not None:
        if isinstance(p, _SCOPE_NODES):
            return p
        p = parents.get(p)
    return None


# ======================================================================================================================
# Mutant extraction (the mutant script is never run: only the statements that define the mutants are evaluated; any
# statement that mentions the mutant collection and is not a recognised definition or a read-only use -> refuse)
# ======================================================================================================================
_RO_CALLS = frozenset({'len', 'list', 'sorted', 'tuple', 'dict', 'set', 'frozenset', 'enumerate', 'iter', 'reversed',
                       'print', 'str', 'repr', 'any', 'all', 'sum', 'min', 'max', 'zip', 'map', 'filter', 'bool'})
_RO_METHODS = frozenset({'items', 'keys', 'values', 'get', 'copy', 'index', 'count'})
_RO_COMPARE = (ast.In, ast.NotIn, ast.Eq, ast.NotEq, ast.Is, ast.IsNot)


def _readonly_use(n, parents):
    """A Load of the mutant collection that cannot change it and does not hand it out for later changes."""
    p = parents.get(n)
    if isinstance(p, (ast.For, ast.AsyncFor)) and p.iter is n:
        return True
    if isinstance(p, ast.comprehension) and p.iter is n:
        return True
    if (isinstance(p, ast.Call) and any(a is n for a in p.args) and isinstance(p.func, ast.Name)
            and p.func.id in _RO_CALLS):
        return True
    if isinstance(p, ast.Attribute) and p.value is n and p.attr in _RO_METHODS:
        gp = parents.get(p)
        return isinstance(gp, ast.Call) and gp.func is p
    if isinstance(p, ast.Subscript) and p.value is n and isinstance(p.ctx, ast.Load):
        return True
    if isinstance(p, ast.Compare) and all(isinstance(o, _RO_COMPARE) for o in p.ops):
        return True
    if isinstance(p, ast.UnaryOp) and isinstance(p.op, ast.Not):
        return True
    if isinstance(p, (ast.If, ast.While, ast.IfExp, ast.Assert)) and p.test is n:
        return True
    if isinstance(p, ast.FormattedValue) and p.value is n:
        return True
    return False


def _mutant_helper_dict(fn):
    """The dict a mutant(name, old, new) helper fills; refuse any helper that does more than assert and store."""
    a = fn.args
    params = [x.arg for x in a.posonlyargs + a.args]
    if len(params) != 3 or a.vararg or a.kwarg or a.kwonlyargs or a.defaults or fn.decorator_list:
        raise HarnessError('mutant() helper does not take exactly (name, old, new): refusing to guess its meaning')
    name, old, new = params
    target = None
    for st in fn.body:
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
            continue
        if isinstance(st, ast.Assert) and not any(isinstance(n, (ast.Call, ast.NamedExpr)) for n in ast.walk(st)):
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


def _is_refilter(v, coll):
    """`[x for x in COLL if cond]`: a filter of the mutant list (the old harness ran the filtered list)."""
    return (isinstance(v, ast.ListComp) and len(v.generators) == 1 and isinstance(v.elt, ast.Name)
            and isinstance(v.generators[0].target, ast.Name) and v.generators[0].target.id == v.elt.id
            and isinstance(v.generators[0].iter, ast.Name) and v.generators[0].iter.id == coll
            and not v.generators[0].is_async)


def _calls_def_stmt(st):
    """A calls-format definition statement: mutant(...) calls, possibly in for / if blocks with name assignments."""
    if isinstance(st, ast.Expr):
        return (isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Name)
                and st.value.func.id == 'mutant')
    if isinstance(st, ast.Pass):
        return True
    if isinstance(st, ast.Assign):
        return all(isinstance(n, ast.Name) for t in st.targets for n in ast.walk(t)
                   if isinstance(n, (ast.Name, ast.Attribute, ast.Subscript, ast.Starred)))
    if isinstance(st, ast.For):
        return (not st.orelse and all(isinstance(n, (ast.Name, ast.Tuple, ast.List)) for n in ast.walk(st.target)
                                      if not isinstance(n, (ast.Store, ast.Load)))
                and all(_calls_def_stmt(s) for s in st.body))
    if isinstance(st, ast.If):
        return all(_calls_def_stmt(s) for s in st.body + st.orelse)
    return False


_IMMUTABLE_VALUES = (str, bytes, int, float, bool, complex, type(None), range, frozenset)


def _immutable_value(v, depth=0):
    if depth > 20:
        return False
    if isinstance(v, _IMMUTABLE_VALUES) or isinstance(v, re.Pattern):
        return True
    if type(v) is tuple:
        return all(_immutable_value(x, depth + 1) for x in v)
    return False


def extract_mutants(mut_path, scorer_src=None):
    """-> (format, [(name, old, new), ...], executed statement lines, collection name).  See extract_mutants_full."""
    info = extract_mutants_full(mut_path, scorer_src)
    return info['format'], info['mutants'], info['lines'], info['coll']


def extract_mutants_full(mut_path, scorer_src=None):
    """The mutants of a mutant script, read strictly.  Formats: 'list' (MUTANTS = [(name, old, new), ...], optionally
    re-filtered by `MUTANTS = [m for m in MUTANTS if ...]`) and 'calls' (mutant(name, old, new) calls filling a dict,
    helper variables and for / if blocks allowed).  The harness part is checked too (_HarnessCheck): no second
    collection of (name, old, new) tuples, every text substitution draws its old / new text from the recognised
    collection, and every filter in front of a substitution is evaluated (a mutant it skips is reported SKIPPED).
    Returns a dict: format, mutants, lines, coll, draft_only (names marked draft-only), skips ({name: why} for the
    mutants the script's own harness part skips), harness (notes for the report header)."""
    mut_path = Path(mut_path)
    src = mut_path.read_bytes().decode('utf-8')
    tree = ast.parse(src, filename=str(mut_path))
    body = tree.body
    parents = parent_map(tree)
    helpers = [n for n in ast.walk(tree) if isinstance(n, _FUNC_NODES) and n.name == 'mutant']
    if len(helpers) > 1:
        raise HarnessError('mutant() is defined %d times' % len(helpers))
    helper = helpers[0] if helpers else None
    if helper is not None and helper not in body:
        raise HarnessError('mutant() is not a top-level def (line %d)' % helper.lineno)
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
    top = {}
    for i, st in enumerate(body):
        for n in ast.walk(st):
            top[id(n)] = i
    problems, inits, filters = [], [], []
    for n in ast.walk(tree):
        line = getattr(n, 'lineno', 0)
        if isinstance(n, (ast.Global, ast.Nonlocal)) and (coll in n.names or 'mutant' in n.names):
            problems.append('line %d declares %s global' % (line, coll))
        elif isinstance(n, (ast.Import, ast.ImportFrom)) and (import_names(n) & {coll, 'mutant'}
                                                             or any(a.name == '*' for a in n.names)):
            problems.append('line %d imports %s' % (line, sorted(import_names(n) & {coll, 'mutant'}) or '*'))
        elif isinstance(n, ast.arg) and n.arg in (coll, 'mutant'):
            problems.append('line %d: a parameter named %s' % (line, n.arg))
        elif isinstance(n, ast.Name) and n.id == coll:
            i = top.get(id(n), len(body))
            p = parents.get(n)
            scope = _enclosing_scope(n, parents)
            if isinstance(n.ctx, ast.Store):
                if (isinstance(p, ast.Assign) and len(p.targets) == 1 and p.targets[0] is n and p in body
                        and i < stop):
                    v = p.value
                    if fmt == 'list' and isinstance(v, (ast.List, ast.Tuple)):
                        bad = [e for e in v.elts if not (isinstance(e, ast.Tuple) and len(e.elts) == 3
                                                         and not any(isinstance(x, ast.Starred) for x in e.elts))]
                        if bad:
                            problems.append('line %d: an entry of the %s literal is not a (name, old, new) tuple'
                                            % (bad[0].lineno, coll))
                        inits.append(p)
                    elif fmt == 'list' and _is_refilter(v, coll):
                        filters.append(p)
                    elif fmt == 'calls' and isinstance(v, ast.Dict) and not v.keys:
                        inits.append(p)
                    else:
                        problems.append('line %d: %s = <%s> is not a recognised definition'
                                        % (line, coll, type(v).__name__))
                else:
                    problems.append('line %d binds %s outside a recognised definition' % (line, coll))
            elif isinstance(n.ctx, ast.Del):
                problems.append('line %d deletes %s' % (line, coll))
            else:
                if helper is not None and scope is helper:
                    if _readonly_use(n, parents):
                        continue
                    if (isinstance(p, ast.Subscript) and isinstance(p.ctx, ast.Store)
                            and isinstance(parents.get(p), ast.Assign) and parents[p] in helper.body):
                        continue
                    problems.append('line %d: the mutant() helper uses %s in an unrecognised way' % (line, coll))
                elif not _readonly_use(n, parents):
                    what = type(p).__name__
                    if isinstance(p, ast.Attribute):
                        what = '.%s' % p.attr
                    elif isinstance(p, ast.Subscript):
                        what = 'item store'
                    problems.append('line %d: %s is used in a way that may change it (%s)' % (line, coll, what))
        elif fmt == 'calls' and isinstance(n, ast.Name) and n.id == 'mutant':
            p = parents.get(n)
            i = top.get(id(n), len(body))
            if not (isinstance(n.ctx, ast.Load) and isinstance(p, ast.Call) and p.func is n):
                problems.append('line %d: mutant is used other than by a direct call' % line)
            elif _enclosing_scope(n, parents) is not None:
                problems.append('line %d: mutant() is called inside a function / lambda / comprehension' % line)
            elif i >= stop:
                problems.append('line %d: mutant() is called after the harness part starts (line %d)'
                                % (line, body[stop].lineno if stop < len(body) else 0))
            elif not isinstance(parents.get(p), ast.Expr):
                problems.append('line %d: the result of mutant() is used' % line)
    if len(inits) != 1:
        problems.append('%d definitions `%s = %s` (need exactly one)' % (len(inits), coll,
                                                                       '[...]' if fmt == 'list' else '{}'))
    elif any(f.lineno < inits[0].lineno for f in filters):
        problems.append('a re-filter of %s precedes its definition' % coll)
    roots = []
    if fmt == 'list':
        roots = sorted(body.index(s) for s in inits + filters)
    else:
        for i, st in enumerate(body[:stop]):
            if st is helper or isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if calls_name(st, 'mutant'):
                if not _calls_def_stmt(st):
                    problems.append('line %d: a statement that calls mutant() is not a plain call / for / if block'
                                    % st.lineno)
                roots.append(i)
    if problems:
        raise HarnessError('strict mutant extraction refused %s: %s%s'
                           % (mut_path.name, '; '.join(problems[:4]), ' (+%d more)' % (len(problems) - 4)
                              if len(problems) > 4 else ''))
    if not roots:
        raise HarnessError('no mutant definitions found in %s' % mut_path)
    cand = body[:stop]
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
    stmts = [st for i, st in enumerate(cand) if i in selected or isinstance(st, (ast.Import, ast.ImportFrom))]
    for st in stmts:
        if isinstance(st, (ast.Import, ast.ImportFrom)):
            continue
        for n in ast.walk(st):
            if ((isinstance(n, ast.Attribute) and n.attr in ('argv', 'environ', 'getenv'))
                    or (isinstance(n, ast.Name) and n.id in ('input', 'argv', 'environ', 'getenv'))):
                raise HarnessError('strict mutant extraction refused %s: line %d - the mutant definitions depend on '
                                   'the command line / environment' % (mut_path.name, st.lineno))
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
    # a statement that is not evaluated must not be able to change a mutable value the definitions read
    helper_names = needed - {coll, 'mutant'}
    mutable = {x for x in helper_names if x in ns and not _immutable_value(ns[x])
               and not isinstance(ns[x], (types.FunctionType, types.ModuleType, type, types.BuiltinFunctionType))}
    for i, st in enumerate(cand):
        if i in selected or st is helper or isinstance(st, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                                                             ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        hit = loaded_names(st) & mutable
        if hit:
            raise HarnessError('strict mutant extraction refused %s: line %d is not evaluated but uses %s, a mutable '
                               'value the mutant definitions read' % (mut_path.name, st.lineno, sorted(hit)))
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
    # ---- v3: the harness part (a second collection, substitutions, filters) and the draft-only markers ------------
    def_ids = set()
    for st in stmts + ([helper] if helper is not None else []):
        for n in ast.walk(st):
            def_ids.add(id(n))
    hc = _HarnessCheck(tree, parents, coll, fmt, def_ids, scorer_src, mut_path.name)
    hc.check_collections({m[0] for m in out})
    hc.check_substitutions()
    skips = hc.evaluate_filters(out)
    draft = _draft_only_marks(src, tree, body, coll, fmt, inits, stmts, def_ids, out, mut_path.name)
    return {'format': fmt, 'mutants': out, 'lines': sorted(st.lineno for st in stmts), 'coll': coll,
            'draft_only': draft, 'skips': skips, 'harness': hc.notes}


# ======================================================================================================================
# v3: the harness part of the mutant script (never run; read statically)
# ======================================================================================================================
def _strlike(e):
    return (isinstance(e, ast.Constant) and isinstance(e.value, str)) or isinstance(e, ast.JoinedStr)


def _triple_shaped(n):
    """(s, s, s) or (s, (s, s)) with s a string literal / f-string: the shape of a mutant entry."""
    if not isinstance(n, (ast.Tuple, ast.List)):
        return False
    e = n.elts
    if len(e) == 3 and all(_strlike(x) for x in e):
        return True
    return (len(e) == 2 and _strlike(e[0]) and isinstance(e[1], (ast.Tuple, ast.List)) and len(e[1].elts) == 2
            and all(_strlike(x) for x in e[1].elts))


def _assign_scopes(tree):
    """id(node) -> the scope node it is evaluated in (Module, function, lambda, class body, comprehension); the parts
    of a scope-creating node that are evaluated outside it (defaults, decorators, the first iterable of a
    comprehension) belong to the enclosing scope."""
    scope_of, override, stack = {}, {}, [(tree, tree)]
    while stack:
        node, scope = stack.pop()
        scope = override.get(id(node), scope)
        scope_of[id(node)] = scope
        inner = scope
        if isinstance(node, _SCOPE_NODES):
            for p in _outer_parts(node):
                override[id(p)] = scope
            inner = node
        for c in ast.iter_child_nodes(node):
            stack.append((c, inner))
    return scope_of


class _Unknown(Exception):
    pass


_NAME, _OLD, _NEW = ('s', 'name'), ('s', 'old'), ('s', 'new')
_OTHER = ('s', 'other')
_PAIR = ('t', (_OLD, _NEW))
_ELEM = ('t', (_NAME, _OLD, _NEW))
_MAP = ('map',)
_JUMPS = (ast.Continue, ast.Break, ast.Return, ast.Raise)


class _HarnessCheck:
    """Static reading of the mutant script's harness part (review3 MAJOR-2 and MINOR 6).
    * check_collections: a (name, old, new)-shaped tuple (or a dict name -> (old, new)) outside the recognised
      definitions is a second mutant collection -> refuse.
    * check_substitutions: every `.replace(A, B)` / `str.replace(S, A, B)` outside the definitions must take A and B
      from one element of the recognised collection (a loop over the whole collection or a view of it, `M[k]`,
      unpacking, a helper parameter all of whose call sites pass such values), or be a replacement of constants that
      do not occur in the scorer; `re.sub` & co. with non-constant arguments refuse.  So a second list, a loop over
      `list(M.items()) + LATE`, a slice of the collection or a hard-coded extra replacement cannot run mutants that
      mutlib does not see.
    * evaluate_filters: every condition in front of such a substitution (an enclosing if, an earlier
      `if ...: continue / break / return / raise`) is evaluated per mutant (name / old / new, literal collections of
      strings, `X.count(old)` on the scorer text); a mutant it skips is SKIPPED, a condition that cannot be evaluated
      refuses the run."""

    def __init__(self, tree, parents, coll, fmt, def_ids, scorer_src, script):
        self.tree, self.parents, self.coll, self.fmt = tree, parents, coll, fmt
        self.def_ids, self.scorer_src, self.script = def_ids, scorer_src, script
        self.scope_of = _assign_scopes(tree)
        self.binds = collections.defaultdict(list)
        self.globals_of = collections.defaultdict(set)
        self.loads = collections.defaultdict(list)
        for n in ast.walk(tree):
            if isinstance(n, (ast.Global, ast.Nonlocal)):
                self.globals_of[id(self.scope_of.get(id(n), tree))] |= set(n.names)

        def bscope(sc, name):
            return tree if sc is not tree and name in self.globals_of.get(id(sc), ()) else sc
        for n in ast.walk(tree):
            sc = self.scope_of.get(id(n), tree)
            if isinstance(n, ast.Name):
                if isinstance(n.ctx, ast.Load):
                    self.loads[n.id].append(n)
                else:
                    self.binds[(id(bscope(sc, n.id)), n.id)].append(('store', n))
            elif isinstance(n, ast.arg):
                self.binds[(id(sc), n.arg)].append(('param', n))
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.binds[(id(bscope(sc, n.name)), n.name)].append(('def', n))
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for nm in import_names(n):
                    self.binds[(id(bscope(sc, nm)), nm)].append(('import', n))
            elif isinstance(n, ast.ExceptHandler) and n.name:
                self.binds[(id(bscope(sc, n.name)), n.name)].append(('except', n))
        self.busy = set()
        self.sites = []
        self.notes = []

    def refuse(self, msg):
        raise HarnessError('strict mutant extraction refused %s: %s' % (self.script, msg))

    # ---- names -----------------------------------------------------------------------------------------------------
    def lookup(self, name, scope):
        s = scope
        while True:
            if s is not self.tree and name in self.globals_of.get(id(s), ()):
                s = self.tree
            b = self.binds.get((id(s), name))
            if b:
                return s, b
            if s is self.tree:
                return s, []
            s = self.scope_of.get(id(s), self.tree)
            while isinstance(s, ast.ClassDef):
                s = self.scope_of.get(id(s), self.tree)

    def is_coll(self, e, scope):
        if not (isinstance(e, ast.Name) and e.id == self.coll):
            return False
        s, _ = self.lookup(e.id, scope)
        return s is self.tree

    # ---- roles: where a value comes from, relative to the recognised collection ----------------------------------
    def role(self, e, scope):
        key = (id(e), id(scope))
        if key in self.busy:
            return None
        self.busy.add(key)
        try:
            return self._role(e, scope)
        finally:
            self.busy.discard(key)

    def _role(self, e, scope):
        if self.is_coll(e, scope):
            return ('seq', _ELEM) if self.fmt == 'list' else _MAP
        if isinstance(e, ast.Name):
            _, bs = self.lookup(e.id, scope)
            roles = [self.binding_role(kind, node) for kind, node in bs]
            if not roles or any(r is None for r in roles) or any(r != roles[0] for r in roles):
                return None
            if roles[0] == _MAP or roles[0][0] == 'seq':
                # a name holding a view of the collection counts only if nothing can change it afterwards
                # (`ALL = list(MUTANTS); ALL.extend(EXTRA)` must not pass as MUTANTS)
                for u in self.loads.get(e.id, []):
                    if self.lookup(e.id, self.scope_of.get(id(u), self.tree))[1] is bs \
                            and not _readonly_use(u, self.parents):
                        return None
            return roles[0]
        if isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Name) and len(e.args) == 1 and not isinstance(e.args[0], ast.Starred):
                r = self.role(e.args[0], scope)
                if r == _MAP:
                    r = ('seq', _NAME)
                if not (isinstance(r, tuple) and r[0] == 'seq'):
                    return None
                if f.id in ('list', 'tuple', 'reversed', 'iter') and not e.keywords:
                    return r
                if f.id == 'sorted' and all(k.arg in ('key', 'reverse') for k in e.keywords):
                    return r
                if f.id == 'enumerate' and not e.keywords:
                    return ('seq', ('t', (_OTHER, r[1])))
                return None
            if isinstance(f, ast.Attribute) and self.is_coll(f.value, scope) and self.fmt == 'calls' \
                    and not e.keywords:
                if f.attr == 'items' and not e.args:
                    return ('seq', ('t', (_NAME, _PAIR)))
                if f.attr == 'values' and not e.args:
                    return ('seq', _PAIR)
                if f.attr == 'keys' and not e.args:
                    return ('seq', _NAME)
                if f.attr == 'get' and len(e.args) == 1:
                    return _PAIR
            return None
        if isinstance(e, ast.Subscript):
            r = self.role(e.value, scope)
            idx = e.slice
            if r == _MAP:
                return _PAIR if not isinstance(idx, ast.Slice) else None
            if isinstance(r, tuple) and r[0] == 'seq':
                return r[1] if not isinstance(idx, ast.Slice) else None       # a slice runs only part of it
            if isinstance(r, tuple) and r[0] == 't':
                if isinstance(idx, ast.Constant) and isinstance(idx.value, int) and not isinstance(idx.value, bool):
                    try:
                        return r[1][idx.value]
                    except IndexError:
                        return None
                if isinstance(idx, ast.Slice) and idx.step is None and all(
                        x is None or (isinstance(x, ast.Constant) and type(x.value) is int)
                        for x in (idx.lower, idx.upper)):
                    return ('t', r[1][slice(idx.lower.value if idx.lower else None,
                                            idx.upper.value if idx.upper else None)])
            return None
        if isinstance(e, ast.IfExp):
            a, b = self.role(e.body, scope), self.role(e.orelse, scope)
            return a if a is not None and a == b else None
        return None

    def _target_path(self, name_node):
        """(the target root, the statement / comprehension binding it, [indices]) for a Name in a store context."""
        path, cur = [], name_node
        while True:
            p = self.parents.get(cur)
            if isinstance(p, (ast.Tuple, ast.List)) and isinstance(p.ctx, ast.Store):
                if any(isinstance(x, ast.Starred) for x in p.elts):
                    return None
                path.append(p.elts.index(cur))
                cur = p
                continue
            return cur, p, list(reversed(path))

    def binding_role(self, kind, node):
        if kind == 'param':
            return self.param_role(node)
        if kind != 'store':
            return None
        tp = self._target_path(node)
        if tp is None:
            return None
        root, stmt, path = tp
        scope = self.scope_of.get(id(root), self.tree)
        if isinstance(stmt, ast.Assign) and root in stmt.targets:
            r = self.role(stmt.value, scope)
        elif isinstance(stmt, (ast.AnnAssign, ast.NamedExpr)) and stmt.target is root and stmt.value is not None:
            r = self.role(stmt.value, scope)
        elif isinstance(stmt, (ast.For, ast.comprehension)) and stmt.target is root:
            it_scope = self.scope_of.get(id(stmt.iter), scope)
            r = self.role(stmt.iter, it_scope)
            if r == _MAP:
                r = ('seq', _NAME)
            r = r[1] if isinstance(r, tuple) and r[0] == 'seq' else None
        else:
            return None
        for i in path:
            if not (isinstance(r, tuple) and r[0] == 't' and i < len(r[1])):
                return None
            r = r[1][i]
        return r

    def param_role(self, arg):
        fn = self.parents.get(self.parents.get(arg))
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return None
        a = fn.args
        pos = [x.arg for x in a.posonlyargs + a.args]
        if arg.arg not in pos + [x.arg for x in a.kwonlyargs]:
            return None                                     # *args / **kwargs
        scope_def = self.scope_of.get(id(fn), self.tree)
        _, bs = self.lookup(fn.name, scope_def)
        if len(bs) != 1 or bs[0][1] is not fn:
            return None
        roles = []
        for use in self.loads.get(fn.name, []):
            if self.lookup(fn.name, self.scope_of.get(id(use), self.tree))[1] != bs:
                continue
            call = self.parents.get(use)
            if not (isinstance(call, ast.Call) and call.func is use):
                return None                                 # passed as a value: its arguments cannot be followed
            if any(isinstance(x, ast.Starred) for x in call.args) or any(k.arg is None for k in call.keywords):
                return None
            val = None
            if arg.arg in pos and pos.index(arg.arg) < len(call.args):
                val = call.args[pos.index(arg.arg)]
            for k in call.keywords:
                if k.arg == arg.arg:
                    val = k.value
            if val is None:
                return None
            roles.append(self.role(val, self.scope_of.get(id(call), self.tree)))
        if not roles or any(r is None or r != roles[0] for r in roles):
            return None
        return roles[0]

    def origin(self, e, scope, depth=0):
        """frozenset of tokens naming the element a derived value was taken from (equal sets: the same element), or
        None.  A statement that unpacks an element (a loop target, `old, new = M[k]`) is one token; `x = y` follows y;
        `m[1]` follows m; a helper parameter is a ('param', function, name) token."""
        if depth > 20:
            return None
        if isinstance(e, ast.Subscript):
            if self.is_coll(e.value, scope):
                return frozenset([('sub', e)])
            return self.origin(e.value, scope, depth + 1)
        if isinstance(e, ast.Call):
            return frozenset([('call', e)])
        if not isinstance(e, ast.Name):
            return None
        _, bs = self.lookup(e.id, scope)
        toks = set()
        for kind, node in bs:
            if kind == 'param':
                toks.add(('param', self.parents.get(self.parents.get(node)), node.arg))
                continue
            if kind != 'store':
                return None
            tp = self._target_path(node)
            if tp is None:
                return None
            root, stmt, _ = tp
            if isinstance(stmt, ast.Assign) and root is node and len(stmt.targets) == 1:
                o = self.origin(stmt.value, self.scope_of.get(id(stmt), self.tree), depth + 1)
                if o is None:
                    return None
                toks |= o
            else:
                toks.add(('stmt', stmt))
        return frozenset(toks) if toks else None

    def same_element(self, a, b, scope, depth=0):
        """Do a (old) and b (new) come from ONE element of the collection?"""
        oa, ob = self.origin(a, scope), self.origin(b, scope)
        if oa is None or ob is None:
            return False
        if oa == ob:
            return True
        if len(oa) == 1 and len(ob) == 1 and depth < 5:
            (ta,), (tb,) = tuple(oa), tuple(ob)
            if ta[0] == tb[0] == 'param' and ta[1] is tb[1] and isinstance(ta[1], (ast.FunctionDef,
                                                                                    ast.AsyncFunctionDef)):
                fn = ta[1]
                pos = [x.arg for x in fn.args.posonlyargs + fn.args.args]
                sites = 0
                for use in self.loads.get(fn.name, []):
                    call = self.parents.get(use)
                    if not (isinstance(call, ast.Call) and call.func is use):
                        return False
                    args = {}
                    for i, x in enumerate(call.args):
                        if isinstance(x, ast.Starred):
                            return False
                        if i < len(pos):
                            args[pos[i]] = x
                    for k in call.keywords:
                        if k.arg is None:
                            return False
                        args[k.arg] = k.value
                    if ta[2] not in args or tb[2] not in args:
                        return False
                    if not self.same_element(args[ta[2]], args[tb[2]], self.scope_of.get(id(call), self.tree),
                                             depth + 1):
                        return False
                    sites += 1
                return sites > 0
        return False

    # ---- 1. a second collection -----------------------------------------------------------------------------------
    def check_collections(self, names):
        for n in ast.walk(self.tree):
            if id(n) in self.def_ids:
                continue
            p = self.parents.get(n)
            bad = False
            if isinstance(n, (ast.Tuple, ast.List)) and all(isinstance(x, ast.Constant) and x.value in names
                                                            for x in n.elts):
                continue                                    # a collection of mutant NAMES (e.g. DRAFT_ONLY)
            if isinstance(n, ast.Tuple) and _triple_shaped(n):
                bad = True
            elif isinstance(n, ast.List) and _triple_shaped(n) and (
                    isinstance(p, (ast.List, ast.Tuple, ast.Set))
                    or (isinstance(p, ast.Call) and isinstance(p.func, ast.Attribute)
                        and p.func.attr in ('append', 'extend', 'insert'))):
                bad = True
            elif isinstance(n, ast.Dict) and any(
                    k is not None and _strlike(k) and isinstance(v, (ast.Tuple, ast.List)) and len(v.elts) == 2
                    and all(_strlike(x) for x in v.elts) for k, v in zip(n.keys, n.values)):
                bad = True
            if bad:
                self.refuse('line %d: a (name, old, new)-shaped value outside the recognised %s definition (a second '
                            'mutant collection?): %s' % (n.lineno, self.coll, short(ast.unparse(n), 80)))

    # ---- 2. every text substitution draws from the recognised collection -------------------------------------------
    def check_substitutions(self):
        for n in ast.walk(self.tree):
            if id(n) in self.def_ids or not isinstance(n, ast.Call):
                continue
            f = n.func
            scope = self.scope_of.get(id(n), self.tree)
            if isinstance(f, ast.Attribute) and f.attr in ('sub', 'subn'):
                if len(n.args) >= 2 and not all(isinstance(a, ast.Constant) for a in n.args):
                    self.refuse('line %d: the harness part substitutes text with .%s(...); mutlib reads only '
                                '.replace(old, new) drawn from %s' % (n.lineno, f.attr, self.coll))
                continue
            if not (isinstance(f, ast.Attribute) and f.attr == 'replace'):
                continue
            if isinstance(f.value, ast.Name) and f.value.id in ('os', 'shutil', 'pathlib') \
                    and self.lookup(f.value.id, scope)[1] and self.lookup(f.value.id, scope)[1][0][0] == 'import':
                continue                                    # os.replace(src, dst): a file move, not a text edit
            args = list(n.args)
            if isinstance(f.value, ast.Name) and f.value.id in ('str', 'bytes') and args:
                args = args[1:]
            if not args:
                continue
            if isinstance(args[0], ast.Starred):
                if self.role(args[0].value, scope) != _PAIR or len(args) != 1:
                    self.refuse('line %d: %s does not take (old, new) of one element of %s'
                                % (n.lineno, short(ast.unparse(n), 70), self.coll))
                self.sites.append((n, scope))
                continue
            if len(args) < 2:
                continue
            a, b = args[0], args[1]
            if not isinstance(b, ast.Starred) and self.role(a, scope) == _OLD and self.role(b, scope) == _NEW:
                if not self.same_element(a, b, scope):
                    self.refuse('line %d: %s takes old and new from different elements of %s'
                                % (n.lineno, short(ast.unparse(n), 70), self.coll))
                self.sites.append((n, scope))
                continue
            if isinstance(a, ast.Constant) and isinstance(a.value, (str, bytes)):
                text = a.value if isinstance(a.value, str) else a.value.decode('utf-8', 'replace')
                if self.scorer_src is not None and text and text in self.scorer_src:
                    self.refuse('line %d: the harness part replaces scorer text %r outside %s (an unlisted mutant?)'
                                % (n.lineno, short(text, 50), self.coll))
                continue
            self.refuse('line %d: %s does not take its old / new text from one element of %s (a loop over another '
                        'iterable, a second list, a slice or a filtered copy of %s?)'
                        % (n.lineno, short(ast.unparse(n), 70), self.coll, self.coll))
        if self.sites:
            self.notes.append('harness part: %d text substitution(s) at line(s) %s, each drawing (old, new) from one '
                              'element of %s' % (len(self.sites), sorted({s.lineno for s, _ in self.sites}),
                                                 self.coll))

    # ---- 3. filters in front of a substitution (MINOR 6) -------------------------------------------------------------
    def _env_vars(self, site, scope):
        """{variable name: 'name' | 'old' | 'new' | 'elem' | 'pair'} for the element the site applies."""
        args = list(site.args)
        if isinstance(site.func.value, ast.Name) and site.func.value.id in ('str', 'bytes'):
            args = args[1:]
        exprs = [args[0].value] if isinstance(args[0], ast.Starred) else args[:2]
        stmts = set()
        env = {}
        for e in exprs:
            base = e
            while isinstance(base, ast.Subscript):
                base = base.value
            if not isinstance(base, ast.Name) or self.is_coll(base, scope):
                if isinstance(e, ast.Subscript) and self.is_coll(e.value, scope) and isinstance(e.slice, ast.Name):
                    env[e.slice.id] = 'name'
                continue
            _, bs = self.lookup(base.id, scope)
            if len(bs) != 1 or bs[0][0] != 'store':
                return None
            tp = self._target_path(bs[0][1])
            if tp is None:
                return None
            root, stmt, _ = tp
            stmts.add(id(stmt))
            for leaf in ast.walk(root):
                if isinstance(leaf, ast.Name):
                    r = self.binding_role('store', leaf)
                    role = {_NAME: 'name', _OLD: 'old', _NEW: 'new', _ELEM: 'elem', _PAIR: 'pair'}.get(r)
                    if role:
                        env[leaf.id] = role
            if isinstance(stmt, ast.Assign):
                v = stmt.value
                if isinstance(v, ast.Subscript) and self.is_coll(v.value, scope) and isinstance(v.slice, ast.Name):
                    env[v.slice.id] = 'name'
                elif (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == 'get'
                      and self.is_coll(v.func.value, scope) and v.args and isinstance(v.args[0], ast.Name)):
                    env[v.args[0].id] = 'name'
        if len(stmts) > 1:
            return None                                     # old and new bound by different statements
        return env

    def _guards(self, site):
        """[(test, want, kind, lineno, local assignments)]: the site runs only if every 'cond' test == want; an
        'abort' test aborts the old harness when it == want.  Collected from the site up to the innermost loop /
        comprehension / function around it: enclosing ifs and earlier `if ...: continue / break / return / raise`
        statements; the simple assignments `x = ...` in front of a test are visible to it."""
        levels = []                                         # inner -> outer: ('block', lst, idx) / ('test', ...)
        node = site
        while True:
            p = self.parents.get(node)
            if p is None:
                break
            for field in ('body', 'orelse', 'finalbody'):
                lst = getattr(p, field, None)
                if isinstance(lst, list) and node in lst:
                    levels.append(('block', (lst, lst.index(node))))
            if isinstance(p, ast.If) and node is not p.test:
                levels.append(('test', (p.test, node in p.body, 'cond', p.lineno)))
            if isinstance(p, ast.IfExp) and node is not p.test:
                levels.append(('test', (p.test, node is p.body, 'cond', p.lineno)))
            if isinstance(p, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                for g in p.generators:
                    for c in g.ifs:
                        levels.append(('test', (c, True, 'cond', c.lineno)))
                break
            if isinstance(p, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                break
            if isinstance(p, (ast.For, ast.AsyncFor, ast.While)) and node in p.body:
                break                                       # the loop that applies the mutants
            node = p
        out, local = [], {}
        for kind, data in reversed(levels):                 # outer -> inner, in execution order
            if kind == 'test':
                out.append(data + (dict(local),))
                continue
            lst, idx = data
            for prev in lst[:idx]:
                for g in self._jump_guards(prev):
                    out.append(g + (dict(local),))
                if isinstance(prev, ast.Assign) and len(prev.targets) == 1 and isinstance(prev.targets[0], ast.Name):
                    local[prev.targets[0].id] = prev.value
                else:
                    for n in stmt_nodes(prev):              # any other binding hides an earlier simple one
                        if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
                            local[n.id] = None
        return out

    def _jump_guards(self, st):
        def jumps(stmts):
            return [s for s in stmts for m in stmt_nodes(s) if isinstance(m, _JUMPS)
                    and not any(isinstance(a, (ast.For, ast.AsyncFor, ast.While)) and isinstance(m, (ast.Continue,
                                                                                                     ast.Break))
                                for a in self._ancestors(m, st))]
        if isinstance(st, ast.If):
            jb, jo = jumps(st.body), jumps(st.orelse)
            if not jb and not jo:
                return []
            top_b = [s for s in st.body if isinstance(s, _JUMPS)]
            top_o = [s for s in st.orelse if isinstance(s, _JUMPS)]
            if jb and jo or (jb and not top_b) or (jo and not top_o):
                raise _Unknown('line %d: a conditional jump mutlib cannot evaluate' % st.lineno)
            j = (top_b or top_o)[0]
            if isinstance(j, (ast.Raise, ast.Break)):
                # a raise aborts the old harness, a break skips this mutant AND every later one: both are accepted
                # only if they are never taken
                return [(st.test, bool(top_b), 'abort', st.lineno)]      # taken when test == (jump in the body)
            return [(st.test, bool(top_o), 'cond', st.lineno)]           # the site runs when the jump is not taken
        for m in stmt_nodes(st):
            if isinstance(m, (ast.Return, ast.Raise)) or (
                    isinstance(m, (ast.Continue, ast.Break))
                    and not any(isinstance(a, (ast.For, ast.AsyncFor, ast.While)) for a in self._ancestors(m, st))):
                raise _Unknown('line %d: a jump inside a %s in front of the substitution'
                               % (m.lineno, type(st).__name__))
        return []

    def _ancestors(self, node, stop):
        out, p = [], self.parents.get(node)
        while p is not None and p is not stop:
            out.append(p)
            p = self.parents.get(p)
        return out

    def _eval(self, e, env, vals, scope, local, depth=0):
        if depth > 30:
            raise _Unknown('too deep')
        ev = lambda x: self._eval(x, env, vals, scope, local, depth + 1)  # noqa: E731
        if isinstance(e, ast.Constant):
            return e.value
        if isinstance(e, ast.Name):
            if e.id in env:
                return vals[env[e.id]]
            if e.id in local:
                if local[e.id] is None:
                    raise _Unknown('%s is bound in front of the filter in a way mutlib does not follow' % e.id)
                return self._eval(local[e.id], env, vals, scope, {k: v for k, v in local.items() if k != e.id},
                                  depth + 1)
            s, bs = self.lookup(e.id, scope)
            if len(bs) == 1 and bs[0][0] == 'store':
                tp = self._target_path(bs[0][1])
                if tp is not None and isinstance(tp[1], ast.Assign) and tp[0] is bs[0][1] \
                        and len(tp[1].targets) == 1:
                    val = tp[1].value
                    if s is self.tree:
                        try:
                            lit = ast.literal_eval(val)
                        except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                            lit = _MISSING
                        if lit is not _MISSING and all(_readonly_use(u, self.parents) for u in self.loads[e.id]):
                            return lit
                    return self._eval(val, env, vals, s, {}, depth + 1)
            raise _Unknown('%s' % e.id)
        if isinstance(e, ast.BoolOp):
            if isinstance(e.op, ast.And):
                r = True
                for x in e.values:
                    r = ev(x)
                    if not r:
                        return r
                return r
            r = False
            for x in e.values:
                r = ev(x)
                if r:
                    return r
            return r
        if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.Not):
            return not ev(e.operand)
        if isinstance(e, ast.Compare):
            left = ev(e.left)
            for op, c in zip(e.ops, e.comparators):
                right = ev(c)
                ok = {ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b, ast.Lt: lambda a, b: a < b,
                      ast.LtE: lambda a, b: a <= b, ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b,
                      ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
                      ast.Is: lambda a, b: a is b, ast.IsNot: lambda a, b: a is not b}[type(op)](left, right)
                if not ok:
                    return False
                left = right
            return True
        if isinstance(e, ast.IfExp):
            return ev(e.body) if ev(e.test) else ev(e.orelse)
        if isinstance(e, (ast.Tuple, ast.List, ast.Set)):
            items = [ev(x) for x in e.elts]
            return set(items) if isinstance(e, ast.Set) else tuple(items) if isinstance(e, ast.Tuple) else items
        if isinstance(e, ast.Subscript):
            v = ev(e.value)
            if isinstance(e.slice, ast.Slice):
                lo, hi, st = (None if x is None else ev(x) for x in (e.slice.lower, e.slice.upper, e.slice.step))
                return v[lo:hi:st]
            return v[ev(e.slice)]
        if isinstance(e, ast.Call) and not e.keywords and not any(isinstance(a, ast.Starred) for a in e.args):
            f = e.func
            if isinstance(f, ast.Name) and f.id == 'len' and len(e.args) == 1:
                s2, _ = self.lookup('len', scope)
                if self.binds.get((id(s2), 'len')):
                    raise _Unknown('len is rebound')
                return len(ev(e.args[0]))
            if isinstance(f, ast.Attribute) and f.attr == 'count' and len(e.args) == 1:
                arg = ev(e.args[0])
                try:
                    recv = ev(f.value)
                except _Unknown:
                    if not isinstance(f.value, ast.Name) or not isinstance(arg, str):
                        raise
                    if self.scorer_src is None:             # no scorer given: mutlib's own anchor check (exactly
                        return 1                            # once, or refuse) is what main() enforces
                    recv = self.scorer_src                  # `SRC.count(old)`: the anchor check on the scorer text
                return recv.count(arg)
            if isinstance(f, ast.Attribute) and f.attr in ('startswith', 'endswith', 'strip', 'lower', 'upper'):
                recv = ev(f.value)
                if isinstance(recv, str):
                    return getattr(recv, f.attr)(*[ev(a) for a in e.args])
        raise _Unknown(short(ast.unparse(e), 60))

    def evaluate_filters(self, mutants):
        skips = {}
        if not self.sites:
            return skips
        runs = {m[0]: False for m in mutants}
        filt = []
        for site, scope in self.sites:
            try:
                guards = self._guards(site)
                env = self._env_vars(site, scope) if guards else {}
                if env is None:
                    raise _Unknown('the substitution at line %d does not bind name / old / new in one statement'
                                   % site.lineno)
                for name, old, new in mutants:
                    vals = {'name': name, 'old': old, 'new': new, 'elem': (name, old, new), 'pair': (old, new)}
                    ok = True
                    for test, want, kind, line, local in guards:
                        v = bool(self._eval(test, env, vals, scope, local))
                        if kind == 'abort':
                            if v == want:
                                raise _Unknown('line %d raises / breaks out of the loop on mutant %s' % (line, name))
                            continue
                        if v != want:
                            ok = False
                            filt.append((name, line, test))
                            break
                    runs[name] = runs[name] or ok
            except _Unknown as u:
                self.refuse('the harness part filters the mutants in front of the substitution at line %d with a '
                            'condition mutlib cannot evaluate (%s); put the filter into a `%s = [m for m in %s if ...]` '
                            're-filter or a DRAFT_ONLY list' % (site.lineno, u, self.coll, self.coll))
        for name, line, test in filt:
            if not runs[name] and name not in skips:
                skips[name] = 'line %d: %s' % (line, short(ast.unparse(test), 60))
        guards_seen = sorted({line for _, line, _ in filt})
        if skips:
            self.notes.append('harness part: its own filter skips %d mutant(s) (%s): %s'
                              % (len(skips), ', '.join('line %d' % x for x in guards_seen), sorted(skips)))
        return skips


def _draft_only_marks(src, tree, body, coll, fmt, inits, stmts, def_ids, mutants, script):
    """Names marked draft-only: a trailing comment `# mutlib: draft-only` on a mutant's definition, or a top-level
    `DRAFT_ONLY = [names]` literal.  A marker that does not sit on exactly one mutant definition with a literal name
    refuses."""
    names = {m[0] for m in mutants}
    spans = []                                              # (first line, last line, name or None)
    if fmt == 'list':
        for st in inits:
            for e in st.value.elts:
                nm = e.elts[0].value if isinstance(e.elts[0], ast.Constant) and isinstance(e.elts[0].value, str) \
                    else None
                spans.append((e.lineno, e.end_lineno, nm))
    else:
        for st in stmts:
            for n in ast.walk(st):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'mutant':
                    a0 = n.args[0] if n.args else None
                    nm = a0.value if isinstance(a0, ast.Constant) and isinstance(a0.value, str) else None
                    spans.append((n.lineno, n.end_lineno, nm))
    out = set()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, SyntaxError) as e:
        raise HarnessError('cannot tokenize %s: %s' % (script, e))
    for tok in toks:
        if tok.type != tokenize.COMMENT or not DRAFT_MARK_RE.search(tok.string):
            continue
        line = tok.start[0]
        hit = [s for s in spans if s[0] <= line <= s[1]]
        if len(hit) != 1:
            raise HarnessError('strict mutant extraction refused %s: line %d: a `# mutlib: draft-only` marker that '
                               'is not on exactly one mutant definition (%d)' % (script, line, len(hit)))
        if hit[0][2] is None or hit[0][2] not in names:
            raise HarnessError('strict mutant extraction refused %s: line %d: a draft-only marker on a mutant whose '
                               'name is not a string literal of a defined mutant' % (script, line))
        out.add(hit[0][2])
    drafts = [st for st in body if 'DRAFT_ONLY' in bound_names(st)]
    uses = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == 'DRAFT_ONLY']
    if drafts or uses:
        parents = parent_map(tree)
        st = drafts[0] if len(drafts) == 1 else None
        if not (st is not None and isinstance(st, ast.Assign) and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name) and len([u for u in uses if isinstance(u.ctx, ast.Store)]) == 1
                and all(isinstance(u.ctx, ast.Store) or _readonly_use(u, parents) for u in uses)):
            raise HarnessError('strict mutant extraction refused %s: DRAFT_ONLY must be one top-level literal list of '
                               'mutant names, only read elsewhere' % script)
        try:
            lst = ast.literal_eval(st.value)
        except (ValueError, TypeError, SyntaxError) as e:
            raise HarnessError('strict mutant extraction refused %s: DRAFT_ONLY is not a literal (%s)' % (script, e))
        if not (isinstance(lst, (list, tuple, set, frozenset)) and all(isinstance(x, str) for x in lst)):
            raise HarnessError('strict mutant extraction refused %s: DRAFT_ONLY is not a collection of names' % script)
        unknown = sorted(set(lst) - names)
        if unknown:
            raise HarnessError('strict mutant extraction refused %s: DRAFT_ONLY names undefined mutants %s'
                               % (script, unknown[:5]))
        out |= set(lst)
    return out


def validate_mutants(mutants, scorer_src, draft_only=frozenset()):
    """Every anchor occurs exactly once in the scorer and differs from its replacement.  A mutant marked draft-only
    whose anchor is ABSENT is returned (skipped: its anchor lives only in an unfilled seal); any other count refuses,
    marked or not."""
    skipped = []
    for name, old, new in mutants:
        n = scorer_src.count(old)
        if n == 0 and name in draft_only:
            skipped.append(name)
            continue
        if n != 1:
            raise HarnessError('mutant %s: anchor found %d times: %r%s' % (
                name, n, old[:80], '' if n or name in draft_only else
                ' (if the anchor exists only in an unfilled seal, mark the mutant `# mutlib: draft-only`)'))
        if old == new:
            raise HarnessError('mutant %s changes nothing' % name)
    return skipped


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
# The fixture suite: analysis and transformation (no hoisting: every check runs where the original runs it)
# ======================================================================================================================
_EXIT_ATTRS = ('exit', '_exit')
_EXIT_NAMES = ('exit', 'quit', 'SystemExit')
_SIMPLE_EXPR = (ast.Name, ast.Constant, ast.BoolOp, ast.UnaryOp, ast.Compare, ast.IfExp, ast.BinOp, ast.Load,
                ast.And, ast.Or, ast.Not, ast.USub, ast.UAdd, ast.Invert, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt,
                ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn, ast.Add, ast.Sub, ast.Mult, ast.BitAnd, ast.BitOr,
                ast.BitXor, ast.Mod, ast.FloorDiv, ast.Div)


def _is_exit_call(n):
    return (isinstance(n, ast.Call) and ((isinstance(n.func, ast.Attribute) and n.func.attr in _EXIT_ATTRS)
                                         or (isinstance(n.func, ast.Name) and n.func.id in _EXIT_NAMES)))


def _end_site(stmts):
    """Where the suite ends: ('call', stmts, call) for a final sys.exit(...) / exit(...) statement, ('raise', stmts,
    call) for a final `raise SystemExit(...)`, ('append', stmts, None) otherwise (the marker goes after the last
    statement).  Descends into a final `if __name__ == '__main__':` block."""
    last = stmts[-1]
    if isinstance(last, ast.Expr) and _is_exit_call(last.value):
        return 'call', stmts, last.value
    if (isinstance(last, ast.Raise) and isinstance(last.exc, ast.Call) and isinstance(last.exc.func, ast.Name)
            and last.exc.func.id == 'SystemExit'):
        return 'raise', stmts, last.exc
    if _is_main_guard(last) and not last.orelse:
        return _end_site(last.body)
    return 'append', stmts, None


def _is_guard_stmt(s, ok):
    if isinstance(s, ast.AugAssign) and isinstance(s.target, ast.Name) and s.target.id == ok \
            and isinstance(s.op, ast.BitAnd):
        return True
    return (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name)
            and s.targets[0].id == ok and isinstance(s.value, ast.BoolOp) and isinstance(s.value.op, ast.And)
            and isinstance(s.value.values[0], ast.Name) and s.value.values[0].id == ok)


def _is_print_stmt(s):
    return isinstance(s, ast.Expr) and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                                           and c.func.id == 'print' for c in ast.walk(s.value))


def _guard_orientations(tree, ok):
    """id(guard statement) -> 'before' (its case line is printed before the update), 'after' (the next statement
    prints it) or '?' (both or neither).  Used only to name the failing case, never for a verdict."""
    out = {}
    for node in ast.walk(tree):
        for field in ('body', 'orelse', 'finalbody'):
            lst = getattr(node, field, None)
            if not isinstance(lst, list) or not lst or not isinstance(lst[0], ast.stmt):
                continue
            prev = -1
            for i, s in enumerate(lst):
                if not _is_guard_stmt(s, ok):
                    continue
                before = any(_is_print_stmt(lst[j]) for j in range(prev + 1, i))
                after = i + 1 < len(lst) and _is_print_stmt(lst[i + 1])
                out[id(s)] = 'before' if before and not after else 'after' if after and not before else '?'
                prev = i
    return out


class _GuardRewriter(ast.NodeTransformer):
    """`ok &= X` and `ok = ok and X` -> the same with X routed through _mutlib_guard(ok, X, label, lineno, raise_ok,
    orient, op), which returns X unchanged (so the suite's own bookkeeping is untouched).  The current `ok` is passed
    FIRST, so it is loaded before X exactly as the suite's own statement loads it; the guard computes `ok & X` (or
    X for `ok and X`) itself and treats the update as failing only when that computation does not raise (review3
    MINOR 2).  Only the module's `ok` is rewritten: module scope (loops, ifs, ...) and functions declaring it global;
    a function's own local `ok` is left alone.  Early exit (raise_ok) is allowed only at module level; a guard inside
    a function only records."""

    def __init__(self, okname, final_lineno, orient):
        self.okname, self.final_lineno, self.orient = okname, final_lineno, orient
        self.label_var = None
        self.in_func = 0
        self.count = 0

    def _guard(self, value, node, op):
        self.count += 1
        label = (ast.Call(func=ast.Name(PFX + 'label', ast.Load()), args=[ast.Name(self.label_var, ast.Load())],
                          keywords=[]) if self.label_var else ast.Constant(None))
        return ast.Call(func=ast.Name(PFX + 'guard', ast.Load()),
                        args=[ast.Name(self.okname, ast.Load()), value, label, ast.Constant(node.lineno),
                              ast.Constant(not self.in_func), ast.Constant(self.orient.get(id(node), '?')),
                              ast.Constant(op)], keywords=[])

    def visit_FunctionDef(self, node):
        if self.okname in declared_globals(node):
            self.in_func += 1
            saved, self.label_var = self.label_var, None
            self.generic_visit(node)
            self.label_var = saved
            self.in_func -= 1
        return node
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        return node

    def visit_ClassDef(self, node):
        return node

    def visit_For(self, node):
        if (self.final_lineno is not None and node.lineno == self.final_lineno and isinstance(node.target, ast.Name)
                and not self.in_func):
            saved, self.label_var = self.label_var, node.target.id
            self.generic_visit(node)
            self.label_var = saved
        else:
            self.generic_visit(node)
        return node

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name) and node.target.id == self.okname and isinstance(node.op, ast.BitAnd):
            node.value = self._guard(node.value, node, 'iand')
        return node

    def visit_Assign(self, node):
        if _is_guard_stmt(node, self.okname):
            rest = node.value.values[1:]
            g = self._guard(rest[0] if len(rest) == 1 else ast.BoolOp(ast.And(), rest), node, 'and')
            node.value = ast.BoolOp(ast.And(), [ast.Name(self.okname, ast.Load()), g])
        return node


def _is_output_stmt(s):
    """An expression statement that prints / writes (after it, a pending case label may be resolvable)."""
    if not isinstance(s, ast.Expr):
        return False
    for c in ast.walk(s.value):
        if isinstance(c, ast.Call) and ((isinstance(c.func, ast.Name) and c.func.id == 'print')
                                        or (isinstance(c.func, ast.Attribute)
                                            and c.func.attr in ('write', 'writelines', 'flush'))):
            return True
    return False


class _HookInserter(ast.NodeTransformer):
    """`_mutlib_after()` after every printing / writing expression statement of the suite: a failed guard whose case
    line is printed after it is named (and, in fast mode, ends the job) right after that line, as v2 did from its
    Python capture stream; v3's streams are real files, which call no Python code."""

    def generic_visit(self, node):
        super().generic_visit(node)
        for field in ('body', 'orelse', 'finalbody'):
            lst = getattr(node, field, None)
            if not (isinstance(lst, list) and lst and isinstance(lst[0], ast.stmt)):
                continue
            new = []
            for s in lst:
                new.append(s)
                if _is_output_stmt(s):
                    h = ast.Expr(ast.Call(func=ast.Name(PFX + 'after', ast.Load()), args=[], keywords=[]))
                    ast.copy_location(h, s)
                    ast.fix_missing_locations(h)
                    new.append(h)
            setattr(node, field, new)
        return node


class _OkToFalse(ast.NodeTransformer):
    def __init__(self, ok):
        self.ok = ok

    def visit_Name(self, node):
        if node.id == self.ok and isinstance(node.ctx, ast.Load):
            return ast.copy_location(ast.Constant(False), node)
        return node


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
            raise HarnessError('%s: need exactly one top-level `BASE = Path(...)` to give each job its own fixture '
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
        # ---- the end of the suite ---------------------------------------------------------------------------------
        kind, _, node = _end_site(body)
        self.end_kind = kind
        self.end_lineno = node.lineno if node is not None else body[-1].end_lineno
        # ---- fast mode: early exit is exact only if `ok` only ever falls and the exit code follows it -------------
        self.fast, self.fast_reason = self._fast_analysis()
        self.code = build_test_code(self)       # compiled ONCE; every job runs this code object (marshal)

    def _ok_scopes(self):
        out = []
        for st in self.tree.body:
            for n in stmt_nodes(st):
                out.append(n)
        for n in ast.walk(self.tree):
            if isinstance(n, _FUNC_NODES) and self.okname in declared_globals(n):
                for b in n.body:
                    out.extend(stmt_nodes(b))
        return out

    def exit_expr(self):
        """The expression the final exit passes (None if there is none)."""
        kind, _, node = _end_site(self.tree.body)
        if kind in ('call', 'raise') and node.args and not node.keywords and len(node.args) == 1:
            return node.args[0]
        return None

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
                elif _is_guard_stmt(n, ok):
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
            elif isinstance(n, (ast.Import, ast.ImportFrom)) and ok in import_names(n):
                problems.append('line %d imports %s' % (n.lineno, ok))
        if inits != 1:
            problems.append('%d initialisations `%s = True`' % (inits, ok))
        if updates == 0:
            problems.append('no `%s &= ...` update' % ok)
        refl = sorted({n.id for n in ast.walk(self.tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
                       and n.id in ('globals', 'vars', 'locals', 'exec', 'eval')})
        if refl:
            problems.append('the suite uses %s' % refl)
        exits = [n for n in ast.walk(self.tree)
                 if _is_exit_call(n) or (isinstance(n, ast.Raise) and n.exc is not None
                                         and root_name(n.exc) == 'SystemExit')]
        last = self.tree.body[-1]
        final_exit = (isinstance(last, ast.Expr) and isinstance(last.value, ast.Call) and last.value in exits
                      and ok in loaded_names(last))
        if not final_exit:
            problems.append('the suite does not end with sys.exit(<depends on %s>)' % ok)
        else:
            e = self.exit_expr()
            if e is None or not all(isinstance(m, _SIMPLE_EXPR) for m in ast.walk(e)):
                problems.append('the final exit expression is not a plain expression of %s' % ok)
            else:
                other = sorted({m.id for m in ast.walk(e) if isinstance(m, ast.Name)} - {ok})
                if other:                                   # review3 MINOR 1: a mutant can move those names
                    problems.append('the final exit expression reads %s besides %s' % (other, ok))
        others = [n for n in exits if not (final_exit and n is last.value)]
        if others:
            problems.append('other exits at lines %s' % sorted({n.lineno for n in others}))
        if problems:
            return False, '; '.join(problems)
        return True, '%d guarded updates of %s' % (updates, ok)


def build_test_code(plan, fx_dir=None):
    """The transformed suite as a code object: BASE -> the job's fixture directory (read from the job's globals, so
    one code object serves every job; `fx_dir` is ignored, kept for old callers), guards, the end-of-suite marker,
    the output hooks."""
    tree = copy.deepcopy(plan.tree)
    body = tree.body
    base = body[plan.base_idx]
    base.value = ast.copy_location(ast.Call(func=ast.Name(PFX + 'Path', ast.Load()),
                                            args=[ast.Name(PFX + 'FX', ast.Load())], keywords=[]), base.value)
    final_lineno = body[plan.final_idx].lineno if plan.final_idx is not None else None
    orient = _guard_orientations(tree, plan.okname)
    tree = _GuardRewriter(plan.okname, final_lineno, orient).visit(tree)
    kind, stmts, node = _end_site(tree.body)
    if kind in ('call', 'raise'):
        arg = node.args[0] if node.args else ast.Constant(None)
        extra = []
        if plan.fast and node.args:
            probe = _OkToFalse(plan.okname).visit(copy.deepcopy(arg))
            extra = [ast.Lambda(args=ast.arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                                                   kw_defaults=[], kwarg=None, defaults=[]), body=probe)]
        node.args = [ast.Call(func=ast.Name(PFX + 'end', ast.Load()), args=[arg] + extra, keywords=[])] \
            + list(node.args[1:])
    else:
        mark = snippet('%send(None)' % PFX)[0]
        ast.copy_location(mark, stmts[-1])
        stmts.append(mark)
    tree = _HookInserter().visit(tree)
    ast.fix_missing_locations(tree)
    return compile(tree, str(plan.path), 'exec')


# ======================================================================================================================
# The parse memo (read_run): static plan, ALLOW-LIST purity
# ======================================================================================================================
PURE_MODULES = frozenset({'re', 'math', 'statistics', 'struct', 'json', 'collections', 'itertools', 'functools',
                          'operator', 'bisect', 'heapq', 'string', 'hashlib', 'binascii', 'zlib', 'base64',
                          'unicodedata', 'copy', 'fractions'})
_DENY_MODULE_ATTRS = frozenset({('operator', 'methodcaller'), ('operator', 'attrgetter'), ('functools', 'lru_cache'),
                                ('functools', 'cache'), ('functools', 'cached_property'),
                                ('functools', 'singledispatch'), ('re', 'purge'), ('json', 'dump')})
_MUTATING_MODULE_FUNCS = frozenset({
    ('heapq', 'heappush'), ('heapq', 'heappop'), ('heapq', 'heapify'), ('heapq', 'heapreplace'),
    ('heapq', 'heappushpop'), ('bisect', 'insort'), ('bisect', 'insort_left'), ('bisect', 'insort_right'),
    ('operator', 'setitem'), ('operator', 'delitem'), ('operator', 'iadd'), ('operator', 'iand'),
    ('operator', 'iconcat'), ('operator', 'ifloordiv'), ('operator', 'ilshift'), ('operator', 'imod'),
    ('operator', 'imul'), ('operator', 'imatmul'), ('operator', 'ior'), ('operator', 'ipow'), ('operator', 'irshift'),
    ('operator', 'isub'), ('operator', 'itruediv'), ('operator', 'ixor')})
_EXCEPTIONS = frozenset(n for n, v in vars(builtins).items() if isinstance(v, type) and issubclass(v, BaseException))
ALLOWED_BUILTINS = frozenset({
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable', 'chr', 'complex', 'dict', 'divmod',
    'enumerate', 'filter', 'float', 'format', 'frozenset', 'hex', 'int', 'isinstance', 'issubclass', 'iter', 'len',
    'list', 'map', 'max', 'min', 'next', 'oct', 'ord', 'pow', 'range', 'repr', 'reversed', 'round', 'set', 'slice',
    'sorted', 'str', 'sum', 'tuple', 'type', 'zip', 'Ellipsis', 'NotImplemented'}) | _EXCEPTIONS
_CONTAINER_BUILTINS = frozenset({'list', 'tuple', 'dict', 'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
                                 'iter', 'min', 'max', 'next', 'sum', 'bytearray'})
PURE_METHODS = frozenset({
    # str / bytes
    'strip', 'lstrip', 'rstrip', 'split', 'rsplit', 'splitlines', 'startswith', 'endswith', 'find', 'rfind', 'index',
    'rindex', 'count', 'decode', 'encode', 'lower', 'upper', 'casefold', 'title', 'capitalize', 'swapcase', 'replace',
    'join', 'partition', 'rpartition', 'isdigit', 'isalpha', 'isalnum', 'isspace', 'isdecimal', 'isnumeric', 'isupper',
    'islower', 'isascii', 'isidentifier', 'isprintable', 'istitle', 'format', 'zfill', 'ljust', 'rjust', 'center',
    'expandtabs', 'translate', 'removeprefix', 'removesuffix', 'hex', 'fromhex', 'maketrans', 'fromkeys',
    'from_bytes',
    # numbers
    'bit_length', 'bit_count', 'to_bytes', 'is_integer', 'as_integer_ratio', 'conjugate', 'real', 'imag', 'numerator',
    'denominator',
    # dict / list / tuple / set (reading)
    'get', 'keys', 'values', 'items', 'copy', 'union', 'intersection', 'difference', 'symmetric_difference',
    'issubset', 'issuperset', 'isdisjoint', 'most_common', 'elements', 'total',
    # re.Pattern / re.Match
    'match', 'search', 'fullmatch', 'finditer', 'findall', 'sub', 'subn', 'pattern', 'flags', 'groups', 'groupindex',
    'group', 'groupdict', 'start', 'end', 'span', 'expand', 'string', 'pos', 'endpos', 'lastindex', 'lastgroup',
    # exceptions
    'args'})
_ALIAS_METHODS = frozenset({'get', 'keys', 'values', 'items'})       # results that share the receiver's objects
FRESH_METHODS = PURE_METHODS - _ALIAS_METHODS
MUTATING_METHODS = frozenset({
    'append', 'extend', 'insert', 'pop', 'remove', 'clear', 'update', 'setdefault', 'add', 'discard', 'sort',
    'reverse', 'popitem', 'appendleft', 'extendleft', 'popleft', 'rotate', 'subtract', 'move_to_end',
    'difference_update', 'intersection_update', 'symmetric_difference_update', 'write', 'writelines', 'truncate',
    'close', 'seek'})
_REFLECTION = frozenset({'globals', 'vars', 'locals', 'exec', 'eval', '__import__'})
FOREIGN = None                      # purity lattice: FOREIGN, or a frozenset of the helper parameters a value comes from
_OWNED = frozenset()


def _meet(a, b):
    if a is FOREIGN or b is FOREIGN:
        return FOREIGN
    return a | b


def _immutable_literal(n):
    if isinstance(n, ast.Constant):
        return True
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)) and isinstance(n.operand, ast.Constant):
        return True
    return isinstance(n, ast.Tuple) and all(_immutable_literal(e) for e in n.elts)


class MemoPlan:
    def __init__(self, ok, reason='', dep_hash='', dep_names=(), file_params=frozenset(), params=(),
                 static_names=frozenset(), builtins_used=frozenset(), n_touch=0, path_reasons=()):
        self.ok, self.reason, self.dep_hash = ok, reason, dep_hash
        self.dep_names, self.file_params, self.params = tuple(dep_names), frozenset(file_params), tuple(params)
        self.static_names, self.builtins_used, self.n_touch = frozenset(static_names), frozenset(builtins_used), n_touch
        # v3 (review3 MAJOR-1): read_run's result can depend on the TEXT of a file argument, not only on the file's
        # type and bytes -> file arguments are keyed by their path too, and nothing goes to the shared disk cache
        self.path_reasons = tuple(path_reasons)
        self.path_sensitive = bool(self.path_reasons)


_FH_METHODS = frozenset({'read', 'readline', 'readlines', 'close'})
_FH_CALLS = frozenset({'iter', 'next', 'list', 'tuple', 'enumerate'})
_EXC_ATTRS = frozenset({'errno', 'strerror', 'winerror'})


def _fh_read_use(n, parents):
    """A use of a file object that only reads it."""
    p = parents.get(n)
    if isinstance(p, ast.Attribute) and p.value is n and p.attr in _FH_METHODS:
        g = parents.get(p)
        return isinstance(g, ast.Call) and g.func is p
    if isinstance(p, (ast.For, ast.comprehension)) and p.iter is n:
        return True
    if (isinstance(p, ast.Call) and isinstance(p.func, ast.Name) and p.func.id in _FH_CALLS and len(p.args) == 1
            and p.args[0] is n and not p.keywords):
        return True
    return isinstance(p, ast.withitem) and p.context_expr is n and p.optional_vars is None


def _path_sensitivity(fn):
    """Why read_run's result could depend on the text of a file argument rather than only on the file's type and
    bytes: an exception object used other than .errno / .strerror / .winerror (str(exc), exc.filename, exc.args name
    the file), a file object used other than to read it (fh.name, repr(fh), passing it on).  [] = insensitive (the
    file parameter itself may only be opened for reading, compared with None or probed by Path(p).is_file() /
    .exists(): _file_params)."""
    parents = parent_map(fn)
    out, handles = [], set()
    for c in ast.walk(fn):
        if not (isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == 'open'):
            continue
        p = parents.get(c)
        if isinstance(p, ast.withitem) and p.context_expr is c:
            if isinstance(p.optional_vars, ast.Name):
                handles.add(p.optional_vars.id)
            elif p.optional_vars is not None:
                out.append('open() bound to %s (line %d)' % (short(ast.unparse(p.optional_vars), 30), c.lineno))
        elif isinstance(p, ast.Assign) and p.value is c and len(p.targets) == 1 and isinstance(p.targets[0], ast.Name):
            handles.add(p.targets[0].id)
        elif not _fh_read_use(c, parents):
            out.append('a file object used other than to read it (line %d)' % c.lineno)
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and n.id in handles and isinstance(n.ctx, ast.Load) \
                and not _fh_read_use(n, parents):
            out.append('the file object %s is used other than to read it (line %d)' % (n.id, n.lineno))
    excs = {h.name for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler) and h.name}
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and n.id in excs and isinstance(n.ctx, ast.Load):
            p = parents.get(n)
            if not (isinstance(p, ast.Attribute) and p.value is n and p.attr in _EXC_ATTRS):
                out.append('the exception object %s is used (line %d); its text can name the file' % (n.id, n.lineno))
    return out


def _file_params(fn, parents):
    """Parameters of read_run used ONLY as `open(p[, read mode])`, `p is (not) None` or `Path(p).is_file()` /
    `.exists()`: the result can depend on them only through the file's type and bytes."""
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
    if any(k.arg not in ('mode', 'encoding', 'errors', 'newline') for k in call.keywords):
        return False
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


def _module_attr_problem(modname, attr):
    if attr.startswith('_'):
        return 'private attribute %s.%s' % (modname, attr)
    if (modname, attr) in _DENY_MODULE_ATTRS:
        return '%s.%s is not allowed' % (modname, attr)
    try:
        val = getattr(importlib.import_module(modname), attr)
    except Exception:
        return '%s.%s does not exist' % (modname, attr)
    if isinstance(val, types.ModuleType):
        return '%s.%s is a module' % (modname, attr)
    return None


class _Purity:
    """Allow-list purity of read_run's closure.  Every closure function (read_run, the module functions and lambdas
    it reaches) may only: read locals, module names bound statically and allowed builtins; call allowed builtins,
    closure functions, local nested functions and functions of PURE_MODULES; change objects it owns (built during the
    call).  A value's state is FOREIGN (module data, read_run's own parameters, anything reached from them) or OWNED
    by the call (optionally derived from a helper's parameters, which then counts as a changed parameter: every call
    site must pass an owned value there).  Reading a function's attributes, dunders / private names, reflection,
    classes, generators, global / nonlocal, imports, IO other than reading a file parameter: refused."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.mutated = collections.defaultdict(set)      # helper name -> its parameters it may change
        self.ret = {}                                   # helper name -> state of its return value

    # ---- entry ----------------------------------------------------------------------------------------------------
    def run(self):
        problems = []
        for _ in range(12):
            before = ({k: frozenset(v) for k, v in self.mutated.items()}, dict(self.ret))
            problems = []
            for name, info in self.ctx['funcs'].items():
                problems += ['%s: %s' % (name, p) for p in self.analyse(name, info)]
            if before == ({k: frozenset(v) for k, v in self.mutated.items()}, dict(self.ret)):
                return problems
        return problems + ['the purity analysis did not converge']

    # ---- one function -----------------------------------------------------------------------------------------------
    def analyse(self, name, info):
        node, kind = info['node'], info['kind']
        self.cur, self.kind, self.problems = name, kind, []
        self.params = [x.arg for x in node.args.posonlyargs + node.args.args + node.args.kwonlyargs]
        self.params += [x.arg for x in (node.args.vararg, node.args.kwarg) if x is not None]
        st, assigns, nested_callables = {}, [], set()
        for p in self.params:
            st[p] = frozenset([p]) if kind == 'helper' else FOREIGN
        for n in ast.walk(node):
            if n is not node and isinstance(n, (ast.FunctionDef, ast.Lambda)):
                if isinstance(n, ast.FunctionDef):
                    nested_callables.add(n.name)
                    st.setdefault(n.name, _OWNED)
                    if n.decorator_list:
                        self.problems.append('decorated nested function %s' % n.name)
                a = n.args
                for x in a.posonlyargs + a.args + a.kwonlyargs + [a.vararg, a.kwarg]:
                    if x is not None:
                        st[x.arg] = FOREIGN
                for d in list(a.defaults) + [d for d in a.kw_defaults if d is not None]:
                    if not _immutable_literal(d):
                        self.problems.append('a non-constant default argument (line %d)' % d.lineno)
            elif isinstance(n, (ast.AsyncFunctionDef, ast.ClassDef, ast.AsyncFor, ast.AsyncWith, ast.Await,
                                ast.Yield, ast.YieldFrom, ast.Global, ast.Nonlocal, ast.Import, ast.ImportFrom,
                                ast.Match)):
                self.problems.append('%s (line %d)' % (type(n).__name__, getattr(n, 'lineno', 0)))
            elif isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
                st.setdefault(n.id, _OWNED)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                st.setdefault(n.name, _OWNED)
            if isinstance(n, ast.Assign):
                assigns.extend((t, n.value) for t in n.targets)
            elif isinstance(n, ast.AnnAssign) and n.value is not None:
                assigns.append((n.target, n.value))
            elif isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name):
                assigns.append((n.target, n.value))
            elif isinstance(n, (ast.For, ast.comprehension)):
                assigns.append((n.target, n.iter))
            elif isinstance(n, ast.withitem) and n.optional_vars is not None:
                assigns.append((n.optional_vars, n.context_expr))
            elif isinstance(n, ast.NamedExpr):
                assigns.append((n.target, n.value))
        if node is not None and isinstance(node, ast.FunctionDef):
            if node.decorator_list and kind != 'nested':
                self.problems.append('decorated')
            a = node.args
            for d in list(a.defaults) + [d for d in a.kw_defaults if d is not None]:
                if not _immutable_literal(d):
                    self.problems.append('a non-constant default argument (line %d)' % d.lineno)
        self.st, self.nested_callables = st, nested_callables
        for _ in range(len(st) + 5):
            changed = False
            for t, v in assigns:
                changed |= self.assign(t, self.eval(v), v)
            if not changed:
                break
        # ---- checks with the final states ---------------------------------------------------------------------------
        parents = parent_map(node)
        self.parents = parents
        mutated = set()
        self.mut = mutated
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                self.check_name(n)
            elif isinstance(n, ast.Attribute):
                self.check_attribute(n)
            elif isinstance(n, ast.Call):
                self.check_call(n)
            if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
                targets = n.targets if isinstance(n, (ast.Assign, ast.Delete)) else [n.target]
                for t in targets:
                    for m in ast.walk(t):
                        if isinstance(m, ast.Subscript) and isinstance(m.ctx, (ast.Store, ast.Del)):
                            self.mutation(self.eval(m.value), 'stores into %s (line %d)'
                                          % (short(ast.unparse(m.value), 40), m.lineno))
                        elif isinstance(m, ast.Attribute) and isinstance(m.ctx, (ast.Store, ast.Del)):
                            self.problems.append('attribute store %s (line %d)' % (short(ast.unparse(m), 40),
                                                                                    m.lineno))
                    if isinstance(n, ast.AugAssign) and isinstance(t, ast.Subscript):
                        self.mutation(self.eval(t.value), 'updates %s (line %d)' % (short(ast.unparse(t), 40),
                                                                                  t.lineno))
        # ---- the return value ---------------------------------------------------------------------------------------
        if isinstance(node, ast.Lambda):
            ret = self.eval(node.body)
        else:
            ret = _OWNED
            for n in scope_walk(node):
                if isinstance(n, ast.Return) and n.value is not None:
                    ret = _meet(ret, self.eval(n.value))
        if kind == 'helper':
            self.ret[name] = ret
            self.mutated[name] |= mutated & set(self.params)
        return self.problems

    def assign(self, t, s, v):
        changed = False
        if isinstance(t, ast.Name):
            old = self.st.get(t.id, _OWNED)
            new = _meet(old, s)
            if new != old:
                self.st[t.id] = new
                changed = True
        elif isinstance(t, (ast.Tuple, ast.List)):
            if isinstance(v, (ast.Tuple, ast.List)) and len(v.elts) == len(t.elts) \
                    and not any(isinstance(e, ast.Starred) for e in t.elts + v.elts):
                for te, ve in zip(t.elts, v.elts):
                    changed |= self.assign(te, self.eval(ve), ve)
            else:
                for te in t.elts:
                    changed |= self.assign(te, s, None)
        elif isinstance(t, ast.Starred):
            changed |= self.assign(t.value, s, None)
        return changed

    def mutation(self, s, what):
        if s is FOREIGN:
            self.problems.append('changes a value it does not own: %s' % what)
        else:
            self.mut |= s

    # ---- value states -------------------------------------------------------------------------------------------------
    def eval(self, e):
        if e is None or isinstance(e, (ast.Constant, ast.JoinedStr, ast.FormattedValue, ast.Compare, ast.UnaryOp,
                                       ast.Lambda, ast.SetComp, ast.Set)):
            return _OWNED
        if isinstance(e, ast.Name):
            if e.id in self.st:
                return self.st[e.id]
            return FOREIGN
        if isinstance(e, (ast.List, ast.Tuple)):
            s = _OWNED
            for x in e.elts:
                s = _meet(s, self.eval(x))
            return s
        if isinstance(e, ast.Dict):
            s = _OWNED
            for x in e.values:
                s = _meet(s, self.eval(x))
            return s
        if isinstance(e, (ast.ListComp, ast.GeneratorExp)):
            return self.eval(e.elt)
        if isinstance(e, ast.DictComp):
            return self.eval(e.value)
        if isinstance(e, ast.BinOp):
            if isinstance(e.op, (ast.Add, ast.Mult)):
                return _meet(self.eval(e.left), self.eval(e.right))
            return _OWNED
        if isinstance(e, ast.BoolOp):
            s = _OWNED
            for x in e.values:
                s = _meet(s, self.eval(x))
            return s
        if isinstance(e, ast.IfExp):
            return _meet(self.eval(e.body), self.eval(e.orelse))
        if isinstance(e, (ast.Subscript, ast.Starred)):
            return self.eval(e.value)
        if isinstance(e, ast.NamedExpr):
            return self.eval(e.value)
        if isinstance(e, ast.Attribute):
            if isinstance(e.value, ast.Name) and e.value.id not in self.st:
                return FOREIGN
            return self.eval(e.value)
        if isinstance(e, ast.Call):
            return self.eval_call(e)
        return FOREIGN

    def _data_args(self, call):
        """The states of a call's arguments that are data (names of callables do not count)."""
        s = _OWNED
        for a in list(call.args) + [k.value for k in call.keywords]:
            if isinstance(a, ast.Name) and a.id not in self.st and (a.id in ALLOWED_BUILTINS
                                                                     or a.id in self.ctx['funcs']):
                continue
            s = _meet(s, self.eval(a))
        return s

    def eval_call(self, c):
        f = self.ctx
        if isinstance(c.func, ast.Name):
            fn = c.func.id
            if fn in self.st:
                return FOREIGN
            if fn in f['funcs']:
                r = self.ret.get(fn, _OWNED)
                if r is FOREIGN:
                    return FOREIGN
                out = _OWNED
                for p, a in self.bind(fn, c).items():
                    if p in r and a is not None:
                        out = _meet(out, self.eval(a))
                return out
            if fn in ('open', 'Path'):
                return _OWNED
            if fn in f['import_from']:
                mod, attr = f['import_from'][fn]
                return self._module_call_state(mod, attr, c)
            if fn in _CONTAINER_BUILTINS:
                return self._data_args(c)
            if fn in ALLOWED_BUILTINS:
                return _OWNED
            return FOREIGN
        if isinstance(c.func, ast.Attribute):
            v = c.func.value
            if isinstance(v, ast.Name) and v.id not in self.st and v.id in f['import_mod']:
                return self._module_call_state(f['import_mod'][v.id], c.func.attr, c)
            recv = self.eval(v)
            if c.func.attr in FRESH_METHODS:
                return _OWNED
            return recv
        return FOREIGN

    def _module_call_state(self, mod, attr, c):
        if mod == 'copy' or mod == 'itertools' or (mod, attr) in (
                ('heapq', 'heappop'), ('heapq', 'heapreplace'), ('heapq', 'heappushpop'), ('heapq', 'nlargest'),
                ('heapq', 'nsmallest'), ('operator', 'getitem'), ('functools', 'reduce'), ('heapq', 'merge'),
                ('collections', 'deque'), ('collections', 'OrderedDict'), ('collections', 'ChainMap'),
                ('collections', 'Counter'), ('collections', 'defaultdict'), ('functools', 'partial')):
            return self._data_args(c)
        return _OWNED

    def bind(self, fname, c):
        """helper parameter -> argument expression at this call site (None when it cannot be mapped)."""
        info = self.ctx['funcs'][fname]
        node = info['node']
        a = node.args
        pos = [x.arg for x in a.posonlyargs + a.args]
        out = {}
        if any(isinstance(x, ast.Starred) for x in c.args) or any(k.arg is None for k in c.keywords):
            return {p: None for p in pos + [x.arg for x in a.kwonlyargs]}
        for p, x in zip(pos, c.args):
            out[p] = x
        for k in c.keywords:
            out[k.arg] = k.value
        return out

    # ---- checks -----------------------------------------------------------------------------------------------------
    def check_name(self, n):
        f = self.ctx
        i = n.id
        if i in self.st:
            return
        if i in _REFLECTION:
            self.problems.append('uses %s (line %d)' % (i, n.lineno))
        elif i in f['static']:
            k = f['kinds'].get(i)
            if k == 'class':
                self.problems.append('uses the class %s (line %d)' % (i, n.lineno))
            elif k == 'import_other':
                if i == 'Path' and self._path_probe(n):
                    return
                self.problems.append('uses %s, imported from a module outside the allow-list (line %d)'
                                     % (i, n.lineno))
            elif k == 'import_from':
                mod, attr = f['import_from'][i]
                why = _module_attr_problem(mod, attr)
                if why:
                    self.problems.append('%s (line %d)' % (why, n.lineno))
                elif (mod, attr) in _MUTATING_MODULE_FUNCS:
                    p = self.parents.get(n)
                    if not (isinstance(p, ast.Call) and p.func is n and p.args):
                        self.problems.append('%s.%s used as a value (line %d)' % (mod, attr, n.lineno))
                    else:
                        self.mutation(self.eval(p.args[0]), '%s.%s(...) (line %d)' % (mod, attr, n.lineno))
        elif i == 'open':
            p = self.parents.get(n)
            if not (self.kind == 'target' and isinstance(p, ast.Call) and p.func is n and p.args
                    and isinstance(p.args[0], ast.Name) and p.args[0].id in f['fparams'] and _open_of(p, p.args[0])):
                self.problems.append('open() other than reading a file parameter (line %d)' % n.lineno)
        elif i == 'Path':
            if not self._path_probe(n):
                self.problems.append('Path other than Path(<file parameter>).is_file() / .exists() (line %d)'
                                     % n.lineno)
        elif i not in ALLOWED_BUILTINS:
            self.problems.append('reads %s, which is neither bound in the module nor an allowed builtin (line %d)'
                                 % (i, n.lineno))

    def _path_probe(self, n):
        p = self.parents.get(n)
        return (self.kind == 'target' and isinstance(p, ast.Call) and p.func is n and p.args
                and isinstance(p.args[0], ast.Name) and p.args[0].id in self.ctx['fparams']
                and _path_probe_of(p, p.args[0], self.parents))

    def check_attribute(self, n):
        f = self.ctx
        if n.attr.startswith('_'):
            self.problems.append('private / dunder attribute .%s (line %d)' % (n.attr, n.lineno))
            return
        if not isinstance(n.ctx, ast.Load):
            return                                      # reported with the store
        v = n.value
        p = self.parents.get(n)
        called = isinstance(p, ast.Call) and p.func is n
        if isinstance(v, ast.Name) and v.id not in self.st:
            k = f['kinds'].get(v.id)
            if k == 'import_mod':
                mod = f['import_mod'][v.id]
                why = _module_attr_problem(mod, n.attr)
                if why:
                    self.problems.append('%s (line %d)' % (why, n.lineno))
                elif (mod, n.attr) in _MUTATING_MODULE_FUNCS:
                    if not (called and p.args):
                        self.problems.append('%s.%s used as a value (line %d)' % (mod, n.attr, n.lineno))
                    else:
                        self.mutation(self.eval(p.args[0]), '%s.%s(...) (line %d)' % (mod, n.attr, n.lineno))
                return
            if k in ('func', 'lambda', 'class'):
                self.problems.append('reads the attribute %s.%s of a function / class (line %d)'
                                     % (v.id, n.attr, n.lineno))
                return
            if k == 'import_other':
                self.problems.append('attribute of %s, imported from a module outside the allow-list (line %d)'
                                     % (v.id, n.lineno))
                return
            recv = FOREIGN
        elif isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == 'Path' \
                and v.func.id not in self.st and self._path_probe(v.func):
            return
        else:
            recv = self.eval(v)
        if n.attr in MUTATING_METHODS:
            self.mutation(recv, '.%s on %s (line %d)' % (n.attr, short(ast.unparse(v), 40), n.lineno))
        elif n.attr in PURE_METHODS:
            return
        elif recv is FOREIGN:
            self.problems.append('.%s on a value it does not own: %s (line %d)'
                                 % (n.attr, short(ast.unparse(v), 40), n.lineno))
        else:
            self.mut |= recv

    def check_call(self, c):
        f = self.ctx
        fn = c.func
        if isinstance(fn, ast.Name):
            if fn.id in self.st:
                if fn.id not in self.nested_callables:
                    self.problems.append('calls the local value %s (line %d)' % (fn.id, c.lineno))
                return
            if f['kinds'].get(fn.id) in ('data', 'mixed'):
                self.problems.append('calls the module value %s, which is not a function definition (line %d)'
                                     % (fn.id, c.lineno))
                return
            if fn.id in f['funcs']:
                muts = self.mutated.get(fn.id, set())
                if muts:
                    bound = self.bind(fn.id, c)
                    for p in muts:
                        if p not in bound:
                            continue
                        a = bound[p]
                        if a is None:
                            self.problems.append('passes *args / **kwargs to %s, which changes its parameter %s '
                                                 '(line %d)' % (fn.id, p, c.lineno))
                        else:
                            self.mutation(self.eval(a), 'passes %s to %s(), which changes its parameter %s (line %d)'
                                          % (short(ast.unparse(a), 30), fn.id, p, c.lineno))
            return
        if isinstance(fn, ast.Attribute):
            return
        self.problems.append('call through an expression %s (line %d)' % (short(ast.unparse(fn), 40), c.lineno))


def _module_reflection(tree):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and any(a.name == '*' for a in n.names):
            out.append('import * (line %d)' % n.lineno)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in _REFLECTION:
            out.append('%s() (line %d)' % (n.id, n.lineno))
        elif isinstance(n, ast.Attribute) and n.attr == '__dict__':
            out.append('.__dict__ (line %d)' % n.lineno)
        elif isinstance(n, ast.Attribute) and n.attr == 'modules' and isinstance(n.value, ast.Name) \
                and n.value.id == 'sys':
            out.append('sys.modules (line %d)' % n.lineno)
    return out


def _touches(st, deps, ctx):
    """A top-level statement that may change a dependency's value at import time (stores into it, calls a method
    of it that is not a pure one, passes it to a call)."""
    for n in stmt_nodes(st):
        if isinstance(n, (ast.Subscript, ast.Attribute)) and isinstance(n.ctx, (ast.Store, ast.Del)) \
                and root_name(n) in deps:
            return True
        if isinstance(n, ast.Call):
            fn = n.func
            if isinstance(fn, ast.Attribute) and root_name(fn.value) in deps:
                r = root_name(fn.value)
                if not (ctx['kinds'].get(r) == 'import_mod' or fn.attr in PURE_METHODS):
                    return True
            if isinstance(fn, ast.Name) and (fn.id in ALLOWED_BUILTINS or fn.id in ('print', 'Path')):
                continue
            if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) \
                    and ctx['kinds'].get(fn.value.id) == 'import_mod':
                continue
            for a in list(n.args) + [k.value for k in n.keywords]:
                if any(isinstance(m, ast.Name) and m.id in deps for m in ast.walk(a)):
                    return True
    return False


def plan_memo(src, fname='read_run'):
    """Static plan of the read_run memo for one scorer source: the dependency closure, its hash, the file parameters,
    the statically bound names and the builtins the closure reads, or the reason the memo is off for this source."""
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return MemoPlan(False, 'syntax error: %s' % exc)
    refl = _module_reflection(tree)
    if refl:
        return MemoPlan(False, 'the module uses %s' % '; '.join(refl[:3]))
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
    static = frozenset(bindings)
    defs = bindings.get(fname, [])
    if len(defs) != 1 or not isinstance(defs[0], ast.FunctionDef) or defs[0].name != fname:
        return MemoPlan(False, '%s is not one top-level def' % fname)
    fn = defs[0]
    # ---- what every module name is --------------------------------------------------------------------------------
    kinds, import_mod, import_from = {}, {}, {}
    funcs_by_name, lambdas_by_name = {}, {}
    for name, sts in bindings.items():
        ks = set()
        for st in sts:
            if isinstance(st, ast.FunctionDef) and st.name == name:
                ks.add('func')
                funcs_by_name[name] = st
            elif isinstance(st, (ast.ClassDef, ast.AsyncFunctionDef)):
                ks.add('class')
            elif isinstance(st, ast.Import):
                for a in st.names:
                    if (a.asname or a.name.split('.')[0]) == name:
                        mod = a.name if a.asname else a.name.split('.')[0]
                        if mod in PURE_MODULES:
                            ks.add('import_mod')
                            import_mod[name] = mod
                        else:
                            ks.add('import_other')
            elif isinstance(st, ast.ImportFrom):
                for a in st.names:
                    if (a.asname or a.name) == name:
                        if st.level == 0 and st.module in PURE_MODULES:
                            ks.add('import_from')
                            import_from[name] = (st.module, a.name)
                        else:
                            ks.add('import_other')
            elif (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                  and st.targets[0].id == name and isinstance(st.value, ast.Lambda)):
                ks.add('lambda')
                lambdas_by_name[name] = st.value
            else:
                ks.add('data')
        kinds[name] = ks.pop() if len(ks) == 1 else 'mixed'
    # ---- the dependency closure, plus top-level statements that touch a dependency --------------------------------
    order, seen_ids, names_seen, todo = [], set(), set(), [fname]
    ctx = {'kinds': kinds}
    while True:
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
        deps = {n for n in names_seen if n in bindings}
        more = [st for st in tree.body if id(st) not in seen_ids and not isinstance(st, (ast.Import, ast.ImportFrom))
                and _touches(st, deps, ctx)]
        if not more:
            break
        for st in more:
            seen_ids.add(id(st))
            order.append(st)
            todo.extend(r for r in loaded_names(st) if r in bindings and r not in names_seen)
    n_touch = sum(1 for st in order if not (bound_names(st) & names_seen))
    dep_names = sorted(n for n in names_seen if n in bindings)
    fparams = _file_params(fn, parent_map(fn))
    # ---- closure functions ------------------------------------------------------------------------------------------
    funcs = {fname: {'node': fn, 'kind': 'target'}}
    problems = []
    for name in dep_names:
        if name == fname:
            continue
        k = kinds[name]
        if k == 'func':
            funcs[name] = {'node': funcs_by_name[name], 'kind': 'helper'}
        elif k == 'lambda':
            funcs[name] = {'node': lambdas_by_name[name], 'kind': 'helper'}
        elif k in ('class', 'mixed'):
            problems.append('%s in the dependencies is a %s' % (name, 'class' if k == 'class' else
                                                                 'name bound more than one way'))
    k_extra = 0
    for st in order:
        if isinstance(st, (ast.ClassDef, ast.AsyncFunctionDef)):
            problems.append('%s %s in the dependencies' % (type(st).__name__, st.name))
        for n in stmt_nodes(st):
            if isinstance(n, ast.Lambda) and not any(i['node'] is n for i in funcs.values()):
                k_extra += 1
                funcs['<lambda line %d #%d>' % (n.lineno, k_extra)] = {'node': n, 'kind': 'helper'}
    ctx.update(static=static, import_mod=import_mod, import_from=import_from, funcs=funcs, fparams=fparams)
    builtins_used = set()
    for name, info in funcs.items():
        for x in free_vars(info['node']):
            if x not in static:
                builtins_used.add(x)
    if not problems:
        problems = _Purity(ctx).run()
    if problems:
        return MemoPlan(False, 'not provably pure: %s' % '; '.join(sorted(set(problems))[:4]))
    segs = []
    for st in sorted(order, key=lambda s: (s.lineno, s.col_offset)):
        segs.append(ast.get_source_segment(src, st) or '')
        segs.append(ast.dump(st))
    text = '%s|%s|%s|' % (VERSION, fname, sys.version) + '\n\0\n'.join(segs)
    a = fn.args
    return MemoPlan(True, '', sha256_bytes(text.encode('utf-8')), dep_names, fparams,
                    [x.arg for x in a.posonlyargs + a.args], static, builtins_used, n_touch,
                    _path_sensitivity(fn) if fparams else ())


# ======================================================================================================================
# Worker runtime (one fresh process per job)
# ======================================================================================================================
class MutantKilled(BaseException):
    def __init__(self, label, lineno):
        super().__init__(label)
        self.label, self.lineno = label, lineno


class MemoViolation(BaseException):
    pass


class HarnessFault(BaseException):
    pass


class _Bypass(Exception):
    pass


_MISSING = object()
_RT = None                        # the job's Runtime
_WRITE_1 = frozenset({'os.remove', 'os.rmdir', 'os.mkdir', 'shutil.rmtree', 'os.truncate', 'os.chmod', 'os.utime',
                      'os.chown', 'os.chflags', 'os.lchmod', 'os.lchown', 'os.lchflags', 'os.removexattr',
                      'os.setxattr'})
_WRITE_BOTH = frozenset({'os.rename', 'shutil.move'})
_WRITE_DST = frozenset({'shutil.copyfile', 'shutil.copytree', 'shutil.copymode', 'shutil.copystat', 'os.link',
                        'os.symlink'})
_SPAWN = frozenset({'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.spawn', 'os.exec', 'os.startfile',
                    'os.fork', 'os.forkpty', '_winapi.CreateProcess', 'pty.spawn'})
_TEMP = frozenset({'tempfile.mkstemp', 'tempfile.mkdtemp'})
_AUDITED = frozenset({'open'}) | _WRITE_1 | _WRITE_BOTH | _WRITE_DST | _SPAWN | _TEMP


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


def _mutable_ids(roots, limit=5000000):
    """ids of the mutable containers reachable from `roots` through containers."""
    seen, out, stack = set(), set(), list(roots)
    while stack:
        v = stack.pop()
        if isinstance(v, (dict, list, set, frozenset, tuple, bytearray)):
            i = id(v)
            if i in seen:
                continue
            seen.add(i)
            if len(seen) > limit:
                raise _Bypass('value too large to check for sharing')
            if isinstance(v, (dict, list, set, bytearray)):
                out.add(i)
            if isinstance(v, dict):
                stack.extend(v.keys())
                stack.extend(v.values())
            elif not isinstance(v, bytearray):
                stack.extend(v)
    return out


def _shares(root, ids, limit=20000000):
    """Does `root` reach (through dicts' values, lists and tuples) a mutable container whose id is in `ids`?  Keys,
    set and frozenset members are hashable, so they cannot hold a mutable container."""
    seen, stack = set(), [root]
    while stack:
        v = stack.pop()
        if isinstance(v, (dict, list, tuple, set, frozenset, bytearray)):
            i = id(v)
            if i in ids:
                return True
            if i in seen or isinstance(v, (set, frozenset, bytearray)):
                continue
            seen.add(i)
            if len(seen) > limit:
                raise _Bypass('value too large to check for sharing')
            stack.extend(v.values() if isinstance(v, dict) else v)
    return False


class _Suppress:
    def __enter__(self):
        if _RT is not None:
            _RT.suppress += 1

    def __exit__(self, *a):
        if _RT is not None:
            _RT.suppress -= 1


def _dep_kind(obj, md):
    if obj is _MISSING:
        return 'missing'
    if isinstance(obj, types.FunctionType):
        if obj.__globals__ is md:
            return 'func'
        return 'callable' if (getattr(obj, '__module__', '') or '').split('.')[0] in PURE_MODULES else None
    if isinstance(obj, types.ModuleType):
        return 'module' if obj.__name__ in PURE_MODULES else None
    if isinstance(obj, type):
        if obj is Path:
            return 'callable'
        return 'callable' if (getattr(obj, '__module__', '') or '').split('.')[0] in PURE_MODULES else None
    if isinstance(obj, types.BuiltinFunctionType):
        return 'callable' if (getattr(obj, '__module__', '') or '').split('.')[0].lstrip('_') in PURE_MODULES \
            else None
    if callable(obj) and not isinstance(obj, re.Pattern):
        return None
    return 'data'


class Memo:
    """read_run memo: key = (dependency hash of read_run's closure in THIS mutant's source, the current values of
    its data dependencies, the type and bytes of its file arguments, its other arguments); values stored pickled,
    returned as a fresh unpickled copy on hits AND misses.  Every miss is guarded: the canonical form of the arguments
    and the data dependencies before and after the call must be equal and the result must not share a mutable object
    with them, otherwise MemoViolation (the job is rerun without the memo).  Disk entries (shared by all jobs) only
    for the unmutated closure."""
    MAGIC = b'MUTLIBM2'

    def __init__(self, cache_dir, shared_src, mem_budget):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.plans = {}
        self.shared_dep = self.plan_for(shared_src).dep_hash
        self.mem, self.mem_bytes, self.budget = collections.OrderedDict(), 0, mem_budget
        self.stats = collections.Counter()
        self.miss_s = 0.0
        self.hit_s = 0.0
        self.off_reason = None
        self.last_paths = []

    def plan_for(self, src):
        key = sha256_bytes(src.encode('utf-8'))
        if key not in self.plans:
            self.plans[key] = plan_memo(src)
        return self.plans[key]

    def _off(self, reason):
        self.stats['off'] += 1
        self.off_reason = reason

    def install(self, module, src):
        plan = self.plan_for(src)
        md = module.__dict__
        fn = md.get('read_run')
        if not plan.ok or not isinstance(fn, types.FunctionType):
            return self._off(plan.reason or 'no read_run function')
        if fn.__globals__ is not md:
            return self._off('read_run is not defined in the scorer module')
        extra = sorted(k for k in md if not (k.startswith('__') and k.endswith('__')) and k not in plan.static_names)
        if extra:
            return self._off('the module defines names that are not bound statically: %s' % extra[:5])
        shadow = sorted(n for n in plan.builtins_used if n in md)
        if shadow:
            return self._off('builtins the closure reads are shadowed in the module: %s' % shadow)
        bns = md.get('__builtins__')
        bdict = bns if isinstance(bns, dict) else getattr(bns, '__dict__', None)
        if not isinstance(bdict, dict):
            return self._off('no builtins namespace')
        bsnap = {n: bdict.get(n, _MISSING) for n in plan.builtins_used}
        deps = {}
        for name in plan.dep_names:
            if name == 'read_run':
                continue
            obj = md.get(name, _MISSING)
            kind = _dep_kind(obj, md)
            if kind is None:
                return self._off('dependency %s is a %s outside the allow-list' % (name, type(obj).__name__))
            meta = (obj.__code__, obj.__defaults__, obj.__kwdefaults__) if kind == 'func' else None
            deps[name] = (obj, kind, meta)
        sig = inspect.signature(fn)
        env = {'module': module, 'md': md, 'plan': plan, 'fn': fn, 'sig': sig, 'deps': deps, 'bns': bns,
               'bdict': bdict, 'bsnap': bsnap}
        memo = self

        @functools.wraps(fn)
        def read_run(*args, **kwargs):
            return memo.call(env, args, kwargs)
        module.read_run = read_run
        self.stats['installed'] += 1

    def state(self, env, args, kwargs, with_key):
        """(key, canonical deps and arguments, the objects to check for sharing); raises _Bypass."""
        md, plan = env['md'], env['plan']
        if md.get('__builtins__') is not env['bns']:
            raise _Bypass('__builtins__ was replaced')
        for n in plan.builtins_used:
            if n in md:
                raise _Bypass('builtin %s is shadowed in the module' % n)
            if env['bdict'].get(n, _MISSING) is not env['bsnap'][n]:
                raise _Bypass('builtin %s was replaced' % n)
        h = hashlib.sha256()
        h.update(plan.dep_hash.encode())
        canon, objs = [], []
        for name, (orig, kind, meta) in env['deps'].items():
            cur = md.get(name, _MISSING)
            if kind == 'missing':
                if cur is not _MISSING:
                    raise _Bypass('%s appeared' % name)
                h.update(b'|missing:' + name.encode())
            elif kind != 'data':
                if cur is not orig:
                    raise _Bypass('%s was rebound' % name)
                if meta is not None and (cur.__code__ is not meta[0] or cur.__defaults__ is not meta[1]
                                         or cur.__kwdefaults__ is not meta[2]):
                    raise _Bypass('%s was modified' % name)
                h.update(b'|obj:' + name.encode())
            else:
                if cur is _MISSING:
                    raise _Bypass('%s vanished' % name)
                r = repr(_canon(cur))
                canon.append((name, r))
                objs.append(cur)
                h.update(b'|data:' + name.encode() + b'=' + r.encode())
        try:
            bound = env['sig'].bind(*args, **kwargs)
        except TypeError:
            raise _Bypass('arguments do not bind')
        bound.apply_defaults()
        paths = []
        for pname, val in bound.arguments.items():
            h.update(b'|arg:' + pname.encode() + b'=')
            if pname in plan.file_params:
                if val is None:
                    tag = 'none'
                    h.update(b'none')
                elif isinstance(val, (str, os.PathLike)):
                    p = os.fspath(val)
                    if not isinstance(p, str):
                        raise _Bypass('bytes path')
                    tag = 'path:%r' % p
                    paths.append(p)
                    if with_key:
                        if plan.path_sensitive:         # the result may carry the path: the path is in the key
                            h.update(('path:%s:%s|' % (type(val).__name__, p)).encode('utf-8', 'surrogatepass'))
                        with _Suppress():
                            err = None
                            try:
                                st = os.stat(p)
                            except OSError as e:
                                st, err = None, e
                            if st is None:              # absent / unreadable: keyed by the kind of failure
                                h.update(('staterr:%s:%s:%s' % (type(err).__name__, err.errno,
                                                                getattr(err, 'winerror', None))).encode())
                            elif os.path.isdir(p):
                                h.update(b'dir')
                            elif os.path.isfile(p):
                                with open(p, 'rb') as fh:
                                    h.update(b'file:' + hashlib.sha256(fh.read()).digest())
                            else:
                                h.update(b'other:%d' % st.st_mode)
                else:
                    raise _Bypass('file argument of type %s' % type(val).__name__)
                canon.append((pname, tag))
            else:
                r = repr(_canon(val))
                canon.append((pname, r))
                objs.append(val)
                h.update(r.encode())
        if with_key:
            self.last_paths = paths
        return h.hexdigest(), canon, objs

    @staticmethod
    def _needles(paths):
        """The forms in which a file argument's path or name could appear in a pickled result."""
        exact, low = set(), set()
        for p in paths:
            forms = {p, os.path.abspath(p), repr(p)[1:-1]}
            forms |= {f.replace('\\', '/') for f in forms} | {f.replace('/', '\\') for f in forms}
            forms |= {f.replace('\\', '\\\\') for f in forms}
            base = os.path.basename(p.rstrip('/\\'))
            if len(base) >= 3:
                forms.add(base)
            for f in forms:
                if f:
                    exact.add(f.encode('utf-8', 'surrogatepass'))
                    low.add(f.lower().encode('utf-8', 'surrogatepass'))
        return exact, low

    def _violate(self, reason):
        self.stats['violation'] += 1
        if _RT is not None:
            _RT.memo_violation = _RT.memo_violation or reason
        raise MemoViolation(reason)

    def _fault(self, reason):
        if _RT is not None:
            _RT.harness_fault = _RT.harness_fault or reason
        raise HarnessFault(reason)

    def call(self, env, args, kwargs):
        fn = env['fn']
        self.last_paths = []
        try:
            key, before, objs = self.state(env, args, kwargs, True)
        except _Bypass as b:
            self.stats['bypass'] += 1
            self.off_reason = 'bypass: %s' % b
            return fn(*args, **kwargs)
        except Exception as e:
            self.stats['bypass'] += 1
            self.off_reason = 'bypass: key failed: %s' % exc_line(e)
            return fn(*args, **kwargs)
        paths = self.last_paths
        shared = env['plan'].dep_hash == self.shared_dep and not env['plan'].path_sensitive
        t0 = time.perf_counter()
        blob = self.mem.get(key)
        if blob is not None:
            self.mem.move_to_end(key)
            self.stats['hit_mem'] += 1
        elif shared:
            blob = self.disk_get(key)
            if blob is not None:
                self.stats['hit_disk'] += 1
                self.mem_put(key, blob)
        if blob is not None:
            try:
                out = pickle.loads(blob)
            except Exception as e:
                self._fault('cannot unpickle a cached read_run value: %s' % exc_line(e))
            self.hit_s += time.perf_counter() - t0
            return out
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        self.miss_s += time.perf_counter() - t0
        self.stats['miss'] += 1
        try:
            _, after, _ = self.state(env, args, kwargs, False)
        except _Bypass as b:
            self._violate('after a miss the arguments / dependencies of read_run have no canonical form (%s)' % b)
        if after != before:
            diff = [a[0] for a, b in zip(before, after) if a != b] or ['(shape)']
            self._violate('read_run changed %s during a call' % diff[:3])
        try:
            ids = _mutable_ids(objs)
            shared_obj = bool(ids) and _shares(result, ids)
        except _Bypass as b:
            self._violate('cannot check the result for sharing (%s)' % b)
        if shared_obj:
            self._violate('read_run returned an object shared with its arguments / module data')
        try:
            blob = pickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            self.stats['unpicklable'] += 1
            return result
        if paths and not env['plan'].path_sensitive:
            # backstop of the static path analysis: a value that carries its file argument's path or name is never
            # stored, so no cached value can carry one path into a call on another
            exact, low = self._needles(paths)
            lowblob = blob.lower()
            if any(x in blob for x in exact) or any(x in lowblob for x in low):
                self.stats['path_in_result'] += 1
                try:
                    return pickle.loads(blob)
                except Exception as e:
                    self._fault('cannot unpickle a read_run value: %s' % exc_line(e))
        self.mem_put(key, blob)
        if shared:
            self.disk_put(key, blob)
        try:
            return pickle.loads(blob)
        except Exception as e:
            self._fault('cannot unpickle a read_run value: %s' % exc_line(e))

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


class _Stream:
    """One output stream of the suite (review3 MINOR 4 / 5).  sys.stdout / sys.stderr of a job are REAL text files in
    the job directory, like the pipes behind the old harness's `python test.py`: fileno(), writelines, closed, name,
    buffer, reconfigure and every other attribute exist, faulthandler and os.write reach them, and printing calls no
    Python code (no harness frames above a printing scorer).  The runtime reads what was written back as lines at
    its hooks (guards, after printing statements, the end marker, the end of the job)."""

    def __init__(self, path, line_buffering):
        self.path = path
        self.f = open(path, 'w', encoding='utf-8', errors='surrogatepass', newline='\n',
                      buffering=1 if line_buffering else -1)
        self.r = open(path, 'rb')
        self.dec = codecs.getincrementaldecoder('utf-8')('surrogatepass')
        self.partial = ''
        self.fd_wrapper = None          # sys.__stdout__ / sys.__stderr__ once fd 1 / 2 point at this file

    def flush(self, current=None):
        """Flushes the job's file and, first, a TextIOWrapper the suite put around its buffer (as sys.stdout) and
        the interpreter's own wrapper around fd 1 / 2."""
        targets = [self.f]
        if current is not None and current is not self.f and isinstance(current, io.TextIOWrapper):
            try:
                if current.buffer is self.f.buffer:
                    targets.insert(0, current)
            except Exception:
                pass
        if self.fd_wrapper is not None and self.fd_wrapper is not self.f:
            targets.insert(0, self.fd_wrapper)
        for f in targets:
            try:
                if not f.closed:
                    f.flush()
            except Exception:
                pass

    def read_lines(self, current=None, final=False):
        self.flush(current)
        data = self.r.read()
        try:
            text = self.dec.decode(data, final)
        except UnicodeDecodeError:
            self.dec = codecs.getincrementaldecoder('utf-8')('replace')
            text = self.dec.decode(data, final)
        buf = self.partial + text
        parts = buf.split('\n')
        self.partial = parts[-1]
        lines = parts[:-1]
        if final and self.partial:
            lines.append(self.partial)
            self.partial = ''
        return lines

    def close(self):
        for f in (self.f, self.r):
            try:
                f.close()
            except Exception:
                pass


def _fail_label(line):
    toks = line.split() if line is not None else []
    return toks[0] if toks and 'FAIL' in toks[1:] else None


class Runtime:
    def __init__(self, job, cfg, job_root, mutant_path):
        self.fast = bool(job['fast'])
        self.want_probe = bool(job.get('probe'))
        self.job_root = os.path.normcase(os.path.abspath(str(job_root)))
        self.mutant_path = mutant_path
        self.private = []
        self.old_enc = cfg.get('old_encoding')
        self.suppress = 0
        self.in_job = False
        self.lines = []
        self.err_lines = []
        self.since_guard = []
        self.pending = None
        self.kill = None
        self.failures = []
        self.guards_passed = 0
        self.reached_end = False
        self.probe = None
        self.enc_note = None
        self.outside = []
        self.spawned = []
        self.memo_violation = None
        self.harness_fault = None
        self.out = self.err = None

    def api(self):
        return {PFX + 'Path': Path, PFX + 'guard': self.guard, PFX + 'label': self.label, PFX + 'end': self.end,
                PFX + 'after': self.after}

    # ---- output ------------------------------------------------------------------------------------------------------
    def drain(self):
        """Reads the stdout lines written since the last drain (complete lines only)."""
        if self.out is None:
            return
        with _Suppress():
            for line in self.out.read_lines(sys.stdout):
                self.on_line('out', line)

    def drain_final(self, cur_out, cur_err):
        """At the end of the job: everything left in both streams (a last line without a newline included)."""
        with _Suppress():
            for line in self.out.read_lines(cur_out, True):
                self.on_line('out', line)
            for line in self.err.read_lines(cur_err, True):
                self.on_line('err', line)

    def on_line(self, stream, line):
        if stream != 'out':
            self.err_lines.append(line)                 # a case line is printed to stdout; stderr never names it
            return
        self.lines.append(line)
        self.since_guard.append(line)
        if self.enc_note is None and self.old_enc:
            try:
                line.encode(self.old_enc)
            except UnicodeEncodeError as e:
                ch = line[e.start]
                self.enc_note = 'printed %s (U+%04X), which %s cannot encode' % (ascii(ch), ord(ch), self.old_enc)
            except LookupError:
                self.old_enc = None
        if self.pending is not None:
            idx, raise_it = self.pending
            self.pending = None
            lab = _fail_label(line) or 'test line %d' % self.failures[idx][1]
            self.failures[idx][0] = lab
            if raise_it and self.kill is None:
                self.kill = (lab, self.failures[idx][1])

    def _raise_kill(self):
        """Ends the job at a failed guard whose case line has been printed since (fast mode, module level)."""
        if self.kill is not None:
            k, self.kill = self.kill, None
            raise MutantKilled(*k)

    # ---- the suite's hooks -------------------------------------------------------------------------------------------
    @staticmethod
    def label(item):
        if isinstance(item, dict) and isinstance(item.get('name'), str):
            return item['name']
        if isinstance(item, (tuple, list)) and item and isinstance(item[0], str):
            return item[0]
        return short(repr(item), 60)

    def after(self):
        """After a printing statement: resolves a pending case label (and, in fast mode, ends the job there)."""
        if self.pending is None:
            return
        self.drain()
        self._raise_kill()

    def guard(self, okv, value, label, lineno, raise_ok=True, orient='?', op='iand'):
        """`ok &= value` (op 'iand') or `ok = ok and value` (op 'and', reached only while ok is truthy).  A failure
        is recorded only when `ok & value` (resp. value) and value itself are falsy AND computing that did not raise
        (the suite's own statement raises in exactly those cases, or later, as without mutlib).  It is EXACT (may end
        the job early in fast mode, and names a kill) only when ok and value are plain bool / int, so the new ok is
        0 / False."""
        self.drain()
        self._raise_kill()
        since, self.since_guard = self.since_guard, []
        try:
            r = (okv & value) if op == 'iand' else value
            failed = (not value) and (not r)
        except Exception:
            failed = False
        if not failed:
            self.guards_passed += 1
            return value
        exact = type(okv) in (bool, int) and type(value) in (bool, int)
        if label is None:
            recent = since[-1] if since else None
            if orient in ('before', '?'):
                label = _fail_label(recent)
            if label is None and orient == 'before':
                label = 'test line %d' % lineno
        self.failures.append([label, lineno, exact])
        stop = self.fast and raise_ok and exact
        if label is None:
            self.pending = (len(self.failures) - 1, stop)
            return value
        if stop:
            raise MutantKilled(label, lineno)
        return value

    def end(self, value, probe=None):
        self.drain()
        self._raise_kill()
        self.reached_end = True
        if probe is not None and self.want_probe:
            try:
                self.probe = ('ok', probe())
            except Exception as e:
                self.probe = ('error', exc_line(e))
        return value

    # ---- the file-system audit (writes outside the job directory) ---------------------------------------------------
    def _norm(self, p):
        if p is None or isinstance(p, int):
            return None
        try:
            return os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(p))))
        except (TypeError, ValueError):
            return None

    def _inside(self, p):
        for root in [self.job_root] + self.private:
            if p == root or p.startswith(root.rstrip('\\/') + os.sep):
                return True
        return p in (os.path.normcase(os.path.abspath(os.devnull)), 'nul')

    def _write(self, p):
        p = self._norm(p)
        if p is None or self._inside(p):
            return
        if p not in self.outside and len(self.outside) < 20:
            self.outside.append(p)

    def on_audit(self, event, args):
        if event == 'open':
            path, mode, flags = (tuple(args) + (None, None, None))[:3]
            if path is None or isinstance(path, int):
                return
            if mode is not None:
                writing = bool(set(str(mode)) & set('wax+'))
            else:
                writing = bool((flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))
            if writing:
                self._write(path)
        elif event in _WRITE_1:
            self._write(args[0] if args else None)
        elif event in _WRITE_BOTH:
            self._write(args[0] if args else None)
            self._write(args[1] if len(args) > 1 else None)
        elif event in _WRITE_DST:
            self._write(args[1] if len(args) > 1 else None)
        elif event in _TEMP:
            p = self._norm(args[0] if args else None)
            if p is not None:
                self.private.append(p)
        elif event in _SPAWN:
            if len(self.spawned) < 5:
                self.spawned.append('%s %s' % (event, short(repr(tuple(args)[:2]), 100)))


def _audit_hook(event, args):
    rt = _RT
    if rt is None or not rt.in_job or rt.suppress or event not in _AUDITED:
        return
    try:
        rt.on_audit(event, args)
    except Exception:
        pass


def _install_worker_hooks(rt, memo, src):
    sys.addaudithook(_audit_hook)
    if memo is None:
        return
    import importlib.util as ilu
    orig_sffl = ilu.spec_from_file_location

    def spec_from_file_location(*a, **k):
        spec = orig_sffl(*a, **k)
        try:
            same = spec is not None and spec.origin and same_file(spec.origin, rt.mutant_path)
        except Exception:
            same = False
        if same:
            loader = spec.loader
            orig_exec = loader.exec_module

            def exec_module(module):
                orig_exec(module)
                with _Suppress():
                    try:
                        memo.install(module, src)
                    except Exception as e:
                        memo._off('install failed: %s' % exc_line(e))
            loader.exec_module = exec_module
        return spec
    ilu.spec_from_file_location = spec_from_file_location


def _run_job(cfg, job):
    """Runs ONE job in this (fresh) process and returns its result dict."""
    global _RT
    sys.dont_write_bytecode = True
    job_dir = Path(job['dir'])
    mdir, fx = job_dir / 'm', job_dir / 'fx'
    mutant_path = mdir / cfg['scorer_name']
    try:
        if job_dir.exists():
            shutil.rmtree(job_dir)
        mdir.mkdir(parents=True)
        mutant_path.write_bytes(job['src'].encode('utf-8'))
    except OSError as e:
        return {'outcome': 'env_error', 'crash': 'cannot prepare the job directory: %s' % exc_line(e)}
    test_path = Path(cfg['test_path'])
    code = marshal.loads(cfg['test_code'])          # the suite transformed and compiled ONCE by the parent
    memo = Memo(cfg['cache'], cfg['scorer_src'], cfg['memo_mem']) if job['memo'] else None
    rt = _RT = Runtime(job, cfg, job_dir, mutant_path)
    try:
        (job_dir / 'cap').mkdir()
        rt.out = _Stream(job_dir / 'cap' / 'stdout.txt', False)
        rt.err = _Stream(job_dir / 'cap' / 'stderr.txt', True)
    except OSError as e:
        return {'outcome': 'env_error', 'crash': 'cannot open the job output files: %s' % exc_line(e)}
    _install_worker_hooks(rt, memo, job['src'])
    g = {'__name__': '__main__', '__file__': str(test_path), '__builtins__': builtins, '__doc__': None,
         '__package__': None, '__spec__': None, '__loader__': None, PFX + 'FX': str(fx)}
    g.update(rt.api())
    argv = [str(test_path), str(mutant_path)] + ([str(fx)] if cfg['uses_argv2'] else [])
    # ---- the recursion limit (review3 MINOR 5): `python test.py` runs the suite's module frame at depth 1; here it
    # sits on top of this process's own frames.  Raise the limit by those frames plus a margin for harness frames
    # that can sit above a scorer frame (the audit hook, the memo wrapper), and keep sys.getrecursionlimit() /
    # sys.setrecursionlimit() as the suite would see them.
    below, f = 0, sys._getframe()
    while f is not None:
        below, f = below + 1, f.f_back
    offset = below + (RECURSION_MARGIN_MEMO if memo is not None else RECURSION_MARGIN)
    orig_set, orig_get = sys.setrecursionlimit, sys.getrecursionlimit

    def setrecursionlimit(limit):
        return orig_set(limit + offset)

    def getrecursionlimit():
        return orig_get() - offset
    orig_set(orig_get() + offset)
    sys.setrecursionlimit, sys.getrecursionlimit = setrecursionlimit, getrecursionlimit
    saved = sys.argv, sys.stdout, sys.stderr
    res = {'label': None, 'lineno': None, 'exit_code': None, 'crash': None}
    # fds 1 / 2 point at the job's files too (the old harness's pipes WERE the child's fds 1 / 2): os.write(1, ...),
    # faulthandler without a file, sys.__stdout__ and child processes land in the captured output
    saved_fds = []
    for fd, stream, wrapper in ((1, rt.out, sys.__stdout__), (2, rt.err, sys.__stderr__)):
        try:
            if wrapper is not None:
                wrapper.flush()
            keep = os.dup(fd)
            os.dup2(stream.f.fileno(), fd)
            saved_fds.append((fd, keep))
            stream.fd_wrapper = wrapper
        except (OSError, ValueError, AttributeError):
            pass
    sys.argv, sys.stdout, sys.stderr = argv, rt.out.f, rt.err.f
    sys.path.insert(0, str(test_path.parent))
    rt.in_job = True
    try:
        exec(code, g)
        res['outcome'], res['exit_code'] = 'exit', 0
    except SystemExit as e:
        c = e.code
        res['outcome'] = 'exit'
        if c is None:
            res['exit_code'] = 0
        elif isinstance(c, int):
            res['exit_code'] = c
        else:
            res['exit_code'] = 1
            res['exit_msg'] = short(c, 100)
    except MutantKilled as k:
        res.update(outcome='killed', label=k.label, lineno=k.lineno)
    except MemoViolation as m:
        res.update(outcome='memo_violation', crash=str(m))
    except HarnessFault as h:
        res.update(outcome='harness_error', crash=str(h))
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        tb = traceback.extract_tb(e.__traceback__) if e.__traceback__ is not None else []
        inner = tb[-1].filename if tb else ''
        res.update(outcome='crash', crash=exc_line(e), crash_in_scorer=same_file(inner, mutant_path),
                   crash_file=Path(inner).name if inner else '?')
        if same_file(inner, HARNESS) and not getattr(e, '_mutlib_emulated', False):
            res.update(outcome='harness_error', crash='in the harness: %s' % exc_line(e),
                       trace=''.join(traceback.format_exception(e))[-3000:])
    finally:
        rt.in_job = False
        cur_out, cur_err = sys.stdout, sys.stderr
        sys.argv, sys.stdout, sys.stderr = saved
        sys.setrecursionlimit, sys.getrecursionlimit = orig_set, orig_get
        for s in (rt.out, rt.err):
            s.flush()                                   # the fd wrappers' text into the files, before fds go back
            s.fd_wrapper = None
        for fd, keep in saved_fds:
            try:
                os.dup2(keep, fd)
                os.close(keep)
            except OSError:
                pass
        try:
            rt.drain_final(cur_out, cur_err)
        except Exception as e:
            rt.harness_fault = rt.harness_fault or 'cannot read the job output: %s' % exc_line(e)
    if rt.harness_fault:
        res.update(outcome='harness_error', crash=rt.harness_fault)
    elif rt.memo_violation:
        res.update(outcome='memo_violation', crash=rt.memo_violation)
    elif rt.kill is not None and res.get('outcome') != 'killed':
        # a failed guard's case line was printed after it but no hook ran before the job ended: v2's capture stream
        # would have ended the job at that line, before whatever ended it here
        res.update(outcome='killed', label=rt.kill[0], lineno=rt.kill[1])
    if rt.pending is not None:
        idx = rt.pending[0]
        rt.failures[idx][0] = 'test line %d' % rt.failures[idx][1]
    texts = rt.lines + rt.err_lines
    res['saw_all_ok'] = any('ALL OK' in t for t in texts)      # the old rule: anywhere in stdout + stderr
    res['saw_all_ok_line'] = res['saw_all_ok_sub'] = res['saw_all_ok']
    res['saw_fixture_failures'] = any(t.strip() == 'FIXTURE FAILURES' for t in texts)
    res['failures'] = [tuple(f) for f in rt.failures[:5]]
    exact = [f for f in rt.failures if f[2]]
    res['first_exact'] = tuple(exact[0]) if exact else None
    res['n_failures'] = len(rt.failures)
    res['guards_passed'] = rt.guards_passed
    res['reached_end'] = rt.reached_end
    res['probe'] = rt.probe
    res['n_lines'] = len(texts)
    res['tail'] = [short(t, 200) for t in rt.lines[-4:]] + ['stderr: ' + short(t, 200) for t in rt.err_lines[-2:]]
    res['enc_note'] = rt.enc_note
    res['outside'] = list(rt.outside)
    res['spawned'] = list(rt.spawned)
    res['memo'] = dict(memo.stats, miss_s=round(memo.miss_s, 3), hit_s=round(memo.hit_s, 3)) if memo else None
    res['memo_note'] = memo.off_reason if memo is not None else None
    res['fast'] = bool(job['fast'])
    return res


def _job_entry(conn, cfg, job):
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except (ValueError, OSError):
        pass
    t0 = time.perf_counter()
    try:
        res = _run_job(cfg, job)
    except BaseException as e:
        res = {'outcome': 'harness_error', 'crash': exc_line(e), 'trace': traceback.format_exc()[-3000:]}
    res.update(name=job['name'], kind=job['kind'], seconds=time.perf_counter() - t0, memo_on=bool(job['memo']))
    try:
        conn.send(res)
        conn.poll(30)
    except BaseException:
        pass
    os._exit(0)


# ======================================================================================================================
# The parent: fresh process per job, scheduling, verdicts, report
# ======================================================================================================================
def exit_nonzero(code):
    return not (code is None or (isinstance(code, int) and code == 0))


def classify(res, family):
    """-> (verdict, detail).  verdict: KILLED | SURVIVED | TIMEOUT | ERROR | UNRESOLVED."""
    o = res.get('outcome')
    if o == 'timeout':
        return 'TIMEOUT', 'TIMEOUT after %.0f s (unresolved, not counted as killed; raise --timeout)' % res['seconds']
    if o == 'env_error':
        return 'UNRESOLVED', 'UNRESOLVED (environment: %s)' % res.get('crash')
    if o in ('harness_error', 'memo_violation'):
        return 'ERROR', 'HARNESS ERROR (%s)' % res.get('crash')
    if o == 'died':
        return 'KILLED', 'KILLED (crash: the job process died, exit code %s)' % res.get('exit_code')
    if o == 'killed':
        return 'KILLED', 'KILLED by %s' % res['label']
    if o == 'crash':
        return 'KILLED', 'KILLED (crash: %s)' % res['crash']
    fails = res.get('failures') or []
    if exit_nonzero(res.get('exit_code')):
        fx = res.get('first_exact')
        if res.get('fast_sound') and fx:
            # the exit follows ok alone and ok fell at this guard: it names the kill (the verdict is the exit code)
            return 'KILLED', 'KILLED by %s' % (fx[0] or 'test line %s' % fx[1])
        first = (' (first failing guard: %s)' % (fails[0][0] or 'test line %s' % fails[0][1])) if fails else ''
        return 'KILLED', 'KILLED by exit %s%s%s' % (res.get('exit_code'), first,
                                                    (' (%s)' % res['exit_msg']) if res.get('exit_msg') else '')
    if not res.get('reached_end'):
        return 'KILLED', 'KILLED (exit 0 before the end of the suite)'
    if res.get('saw_fixture_failures'):
        return 'KILLED', 'KILLED by FIXTURE FAILURES'
    if not res.get('saw_all_ok', res.get('saw_all_ok_line')):
        return 'KILLED', 'KILLED (the suite exited 0 without ALL OK in its output)'
    return 'SURVIVED', 'SURVIVED'


def needs_confirmation(res):
    o = res.get('outcome')
    return o == 'died' or (o == 'crash' and not res.get('crash_in_scorer'))


class _Running:
    __slots__ = ('proc', 'conn', 'job', 't0', 'dir')

    def __init__(self, proc, conn, job, t0, d):
        self.proc, self.conn, self.job, self.t0, self.dir = proc, conn, job, t0, d


class Scheduler:
    """Starts one fresh spawned process per job (never reused), at most `workers` at a time."""

    def __init__(self, cfg, log, keep_work):
        self.ctx = mp.get_context('spawn')
        self.cfg, self.log, self.keep = cfg, log, keep_work
        self.seq = 0
        self.leftover = []
        self.cleanq = queue.Queue()
        self.cleaners = [threading.Thread(target=self._cleaner, daemon=True) for _ in range(2)]
        for t in self.cleaners:
            t.start()
        self.running = []

    def _cleaner(self):
        while True:
            d = self.cleanq.get()
            if d is None:
                self.cleanq.task_done()
                return
            ok = False
            for k in range(8):
                try:
                    shutil.rmtree(d)
                    ok = True
                    break
                except FileNotFoundError:
                    ok = True
                    break
                except OSError:
                    time.sleep(0.25 * (k + 1))
            if not ok and os.path.exists(d):
                self.leftover.append(str(d))
            self.cleanq.task_done()

    def _start(self, job):
        self.seq += 1
        d = Path(self.cfg['work']) / ('j%05d' % self.seq)
        job = dict(job, dir=str(d), seq=self.seq)
        parent, child = self.ctx.Pipe()
        p = self.ctx.Process(target=_job_entry, args=(child, self.cfg, job), daemon=True,
                             name='mutlib-j%d' % self.seq)
        p.start()
        child.close()
        return _Running(p, parent, job, time.time(), d)

    @staticmethod
    def _kill(proc):
        try:
            proc.terminate()
        except Exception:
            pass
        proc.join(5)
        if proc.is_alive():
            try:
                proc.kill()
            except Exception:
                pass
            proc.join(5)

    def _retire(self, r):
        try:
            r.conn.close()
        except Exception:
            pass
        if not self.keep:
            self.cleanq.put(r.dir)

    def run(self, jobs, on_result, timeout_of, workers):
        finishing = []
        try:
            while jobs or self.running:
                while jobs and len(self.running) < workers:
                    job = jobs.popleft()
                    try:
                        self.running.append(self._start(job))
                    except Exception as e:
                        on_result(job, {'name': job['name'], 'kind': job['kind'], 'outcome': 'env_error',
                                        'crash': 'cannot start a job process: %s' % exc_line(e), 'seconds': 0.0})
                waitables = [r.conn for r in self.running] + [r.proc.sentinel for r in self.running]
                if waitables:
                    mp_wait(waitables, timeout=0.5)
                done = []
                now = time.time()
                for r in list(self.running):
                    msg, got = None, False
                    try:
                        if r.conn.poll():
                            msg = r.conn.recv()
                            got = True
                    except (EOFError, OSError):
                        got = False
                    if got and isinstance(msg, dict):
                        try:
                            r.conn.send('bye')
                        except Exception:
                            pass
                        done.append((r, msg))
                    elif not r.proc.is_alive():
                        r.proc.join(1)
                        done.append((r, {'name': r.job['name'], 'kind': r.job['kind'], 'outcome': 'died',
                                         'exit_code': r.proc.exitcode, 'seconds': now - r.t0,
                                         'memo_on': bool(r.job['memo'])}))
                    elif now - r.t0 > timeout_of(r.job):
                        self.log('timeout: %s after %.0f s, killing its process' % (r.job['name'], now - r.t0))
                        self._kill(r.proc)
                        done.append((r, {'name': r.job['name'], 'kind': r.job['kind'], 'outcome': 'timeout',
                                         'seconds': now - r.t0, 'memo_on': bool(r.job['memo'])}))
                for r, res in done:
                    self.running.remove(r)
                    res['t0'], res['t1'] = r.t0, time.time()
                    finishing.append((r, time.time()))
                    on_result(r.job, res)
                for item in list(finishing):
                    r, t = item
                    if not r.proc.is_alive():
                        r.proc.join(0)
                        finishing.remove(item)
                        self._retire(r)
                    elif time.time() - t > 15:
                        self._kill(r.proc)
                        finishing.remove(item)
                        self._retire(r)
        finally:
            for r in self.running:
                self._kill(r.proc)
                self._retire(r)
            self.running = []
            deadline = time.time() + 15
            for r, _ in finishing:
                r.proc.join(max(0.1, deadline - time.time()))
                if r.proc.is_alive():
                    self._kill(r.proc)
                self._retire(r)

    def close(self):
        for _ in self.cleaners:
            self.cleanq.put(None)
        for t in self.cleaners:
            t.join(600)


def _fmt_memo(m):
    if not m:
        return 'memo off'
    keys = ('hit_mem', 'hit_disk', 'miss', 'bypass', 'off', 'violation', 'path_in_result')
    return 'memo ' + ' '.join('%s=%d' % (k, m.get(k, 0)) for k in keys if m.get(k))


def old_console_encoding():
    """The encoding a child `python test.py` printed with when the old harnesses captured it through a pipe."""
    pie = os.environ.get('PYTHONIOENCODING')
    if pie and pie.split(':')[0]:
        return pie.split(':')[0]
    if os.environ.get('PYTHONUTF8') == '1' or sys.flags.utf8_mode:
        return 'utf-8'
    return locale.getpreferredencoding(False)


def main(argv=None):
    ap = argparse.ArgumentParser(description='fast, strict, shared mutation harness (see README.md)')
    ap.add_argument('--scorer', required=True, help='the scorer under test (the sealed copy when there is one)')
    ap.add_argument('--test', required=True, help='its fixture suite test_*.py')
    ap.add_argument('--mutants', required=True, help='its mutant script mut_*.py (read, never run)')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 1) - 4))
    ap.add_argument('--no-memo', action='store_true', help='no read_run parse memo')
    ap.add_argument('--no-fast', action='store_true', help='no early exit: every suite runs to its end')
    ap.add_argument('--only', help='comma-separated mutant names')
    ap.add_argument('--changed-from', help='parent scorer: run mutants whose anchor touches a changed line ...')
    ap.add_argument('--sample', type=float, default=None, help='... plus this fraction of the rest (default 0.2)')
    ap.add_argument('--seed', type=int, default=None, help='sample seed (default: from the scorer sha256)')
    ap.add_argument('--control', action='store_true', help='add three equivalent mutants that must survive')
    ap.add_argument('--timeout', type=float, default=0.0, help='seconds per mutant (default: from the baseline)')
    ap.add_argument('--out', help='also write the report here')
    ap.add_argument('--ok-name', default='ok', help="the suite's pass flag (default ok)")
    ap.add_argument('--cache-dir', default=None, help='read_run memo cache root (default mutlib/cache)')
    ap.add_argument('--work-dir', default=str(HERE / 'work'))
    ap.add_argument('--memo-mem-mb', type=int, default=256, help='in-memory memo budget per job')
    ap.add_argument('--keep-work', action='store_true')
    ap.add_argument('--dry-run', action='store_true', help='print the header and the selection, run nothing')
    args = ap.parse_args(argv)

    t_start = time.time()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='backslashreplace')     # a label printed by a suite must never crash the report
        except (AttributeError, ValueError, OSError):
            pass
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
        info = extract_mutants_full(mutf, scorer_src)
        fmt, mutants, lines_run, coll = info['format'], info['mutants'], info['lines'], info['coll']
        draft_skipped = validate_mutants(mutants, scorer_src, info['draft_only'])
        plan = TestPlan(test, test_src, args.ok_name)
    except HarnessError as e:
        for h in header:
            print(h)
        print('REFUSED: %s' % e)
        if args.out:
            Path(args.out).write_text('\n'.join(header + ['REFUSED: %s' % e]) + '\n', encoding='utf-8')
        return 3
    n_defined = len(mutants)
    header.append('mutants: format %s, %d defined (strict: every use of %s checked; statements evaluated at lines %s)'
                  % (fmt, n_defined, coll, _ranges(lines_run)))
    header.extend(info['harness'])
    names = [m[0] for m in mutants]
    skip_reason = {}
    if info['draft_only']:
        header.append('draft-only: %d mutant(s) marked %s; %d skipped because the anchor is absent from this scorer '
                      '(an unfilled seal): %s' % (len(info['draft_only']), sorted(info['draft_only']),
                                                  len(draft_skipped), draft_skipped))
        skip_reason.update((n, 'SKIPPED (draft-only: its anchor is absent from this scorer)') for n in draft_skipped)
    filter_skipped = [n for n in names if n in info['skips'] and n not in skip_reason]
    skip_reason.update((n, "SKIPPED (the mutant script's own filter skips it: %s)" % info['skips'][n])
                       for n in filter_skipped)
    selected = [n for n in names if n not in skip_reason]
    want = None
    if args.only:
        want = [x.strip() for x in args.only.split(',') if x.strip()]
        unknown = [x for x in want if x not in names]
        if unknown:
            print('REFUSED: unknown mutant names %s' % unknown)
            return 3
        selected = [n for n in selected if n in want]
        header.append('selection: --only, %d mutants' % len(selected))
    skipped_shown = [n for n in names if n in skip_reason and (want is None or n in want)]
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
    header.append('suite: family %s; fast %s (%s); end of suite: %s at line %d'
                  % (plan.family, 'on' if fast else 'OFF', 'disabled by --no-fast' if args.no_fast and plan.fast
                     else plan.fast_reason, {'call': 'the final exit call', 'raise': 'the final raise SystemExit',
                                             'append': 'after the last statement'}[plan.end_kind], plan.end_lineno))
    cache_root = Path(args.cache_dir) if args.cache_dir else HERE / 'cache'
    cache_dir = cache_root / scorer.stem
    if memo_on:
        header.append('memo: read_run, %d dependencies %s, %d touching statements, file params %s, dep hash %s, '
                      'cache %s' % (len(memo_plan.dep_names), list(memo_plan.dep_names), memo_plan.n_touch,
                                    sorted(memo_plan.file_params), memo_plan.dep_hash[:16], cache_dir))
        if memo_plan.file_params:
            header.append('memo: file arguments keyed by %s' % (
                'their path as well as their type and bytes, memory only, no disk cache (read_run can carry the '
                'path: %s)' % '; '.join(memo_plan.path_reasons[:3]) if memo_plan.path_sensitive else
                'their type (a stat failure by its kind) and bytes; a value that carries the path or name of its file '
                'argument is never stored'))
    controls = control_mutants(scorer_src, 'read_run' if memo_on else 'evaluate') if args.control else []
    run_dir = Path(args.work_dir) / ('%s_%d_%d' % (scorer.stem, os.getpid(), int(time.time())))
    workers = max(1, min(args.workers, len(selected) + len(controls)))
    old_enc = old_console_encoding()
    header.append('isolation: one fresh spawned process per job; a crash outside the scorer or a dead job process is '
                  'confirmed by a rerun; old console encoding %s (noted, not emulated)' % old_enc)
    header.append('workers %d (spawn, one process per job), work dir %s' % (workers, run_dir))
    for h in header:
        print(h, flush=True)
    printed_header = len(header)
    if args.dry_run:
        print('dry run: %d selected mutants: %s' % (len(selected), selected))
        if skipped_shown:
            print('skipped: %s' % skipped_shown)
        print('controls: %s' % ([c[0] for c in controls] or 'none'))
        return 0
    durations_file = cache_root / scorer.stem / 'durations.json'
    try:
        prev = json.loads(durations_file.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        prev = {}
    dispatch = sorted(selected, key=lambda n: -float(prev.get(n, 1e9)))
    by_name = {n: (o, w) for n, o, w in mutants}
    cfg = {'work': str(run_dir), 'scorer_name': scorer.name, 'test_path': str(test), 'test_src': test_src,
           'okname': args.ok_name, 'scorer_src': scorer_src, 'cache': str(cache_dir),
           'memo_mem': args.memo_mem_mb * 1024 * 1024, 'old_encoding': old_enc,
           'test_code': marshal.dumps(plan.code), 'uses_argv2': plan.uses_argv2, 'family': plan.family}
    state = {'memo': memo_on, 'fast': fast, 'timeout': args.timeout or 1800.0, 'done': 0, 'phase': 'baseline'}
    results, history = {}, collections.defaultdict(list)
    sched = Scheduler(cfg, log, args.keep_work)
    total = len(selected) + len(controls)
    fast_sound = fast

    def mk(kind, name, src, **flags):
        job = {'kind': kind, 'name': name, 'src': src, 'fast': state['fast'] and kind != 'baseline',
               'memo': state['memo'], 'probe': kind == 'baseline', 'confirm': False, 'nomemo': False, 'alone': False}
        job.update(flags)
        return job

    def timeout_of(job):
        if job['kind'] == 'baseline':
            return 10.0 * args.timeout if args.timeout else 4 * 3600.0
        return state['timeout']

    rc = 3
    try:
        # ---- phase 1: the baseline, alone ------------------------------------------------------------------------------
        base_res = {}

        def on_base(job, res):
            base_res['res'] = res
            base_res['job'] = job
        tries = []
        for attempt in range(3):
            jobs = collections.deque([mk('baseline', 'BASELINE', scorer_src)])
            sched.run(jobs, on_base, timeout_of, 1)
            res = base_res['res']
            res['fast_sound'] = False
            tries.append(res)
            if res.get('outcome') == 'memo_violation':
                state['memo'] = False
                header.append('memo: DISABLED at run time (the baseline: %s); every job runs without it'
                              % res.get('crash'))
                log(header[-1])
                continue
            verdict, detail = classify(res, plan.family)
            if verdict == 'SURVIVED':
                break
            if needs_confirmation(res) and attempt == 0:
                header.append('baseline: the first run gave %s; rerun once in a fresh process' % detail)
                log(header[-1])
                continue
            raise HarnessError('the unmutated scorer does not pass its own suite in this harness: %s; last lines %s%s'
                               % (detail, res.get('tail'), ('\n' + res['trace']) if res.get('trace') else ''))
        else:
            raise HarnessError('the baseline could not be completed: %s' % [classify(r, plan.family)[1]
                                                                           for r in tries])
        b = res
        if res.get('memo_note') and state['memo']:
            header.append('memo: the baseline reports: %s' % res['memo_note'])
        if fast:
            pr = res.get('probe')
            if not pr or pr[0] != 'ok' or not exit_nonzero(pr[1]):
                state['fast'] = fast_sound = False
                header.append('fast: DISABLED after the baseline (the final exit with %s=False gives %r, not a '
                              'non-zero code)' % (args.ok_name, pr))
            else:
                header.append('fast: confirmed by the baseline (the final exit with %s=False gives %r)'
                              % (args.ok_name, pr[1]))
        if res.get('outside') or res.get('spawned'):
            why = []
            if res.get('outside'):
                why.append('wrote outside its job directory: %s' % res['outside'][:5])
            if res.get('spawned'):
                why.append('started processes whose writes cannot be audited: %s' % res['spawned'][:2])
            workers = 1
            header.append('workers: FORCED TO 1 - the baseline %s' % '; '.join(why))
            log(header[-1])
        if not args.timeout:
            est = res['seconds']
            m = res.get('memo') or {}
            if state['memo'] and m:
                hits = m.get('hit_mem', 0) + m.get('hit_disk', 0)
                per_miss = (m.get('miss_s', 0.0) / m['miss']) if m.get('miss', 0) >= 3 else \
                    20.0 * (m.get('hit_s', 0.0) / hits if hits else 0.0)
                est = res['seconds'] - m.get('hit_s', 0.0) + hits * per_miss
            state['timeout'] = max(120.0, 3.0 * res['seconds'], 3.0 * est)
        log('BASELINE passed in %.1f s (%s); mutant timeout %.0f s; workers %d'
            % (res['seconds'], _fmt_memo(res.get('memo')), state['timeout'], workers))
        state['phase'] = 'main'

        # ---- phase 2: controls and mutants -----------------------------------------------------------------------------
        jobs = collections.deque()
        for name, old, new in controls:
            jobs.append(mk('control', name, scorer_src.replace(old, new)))
        for n in dispatch:
            old, new = by_name[n]
            jobs.append(mk('mutant', n, scorer_src.replace(old, new)))

        def on_result(job, res):
            res['fast_sound'] = fast_sound and job['fast']
            if res.get('outcome') == 'memo_violation':
                history[job['name']].append(('memo violation', res))
                if state['memo']:
                    state['memo'] = False
                    header.append('memo: DISABLED at run time after %s (%s); later jobs run without it'
                                  % (job['name'], res.get('crash')))
                    log(header[-1])
                    for q in jobs:
                        q['memo'] = False
                jobs.appendleft(dict(job, memo=False, nomemo=True))
                return
            if needs_confirmation(res) and not job['confirm']:
                history[job['name']].append(('needs confirmation', res))
                jobs.appendleft(dict(job, memo=state['memo'] and job['memo'], confirm=True))
                log('%s: %s - confirming in a fresh process' % (job['name'], classify(res, plan.family)[1]))
                return
            res['flags'] = {k: job[k] for k in ('confirm', 'nomemo', 'alone')}
            res['history'] = [(why, classify(r, plan.family)[1]) for why, r in history[job['name']]]
            results[job['name']] = res
            state['done'] += 1
            log('[%d/%d] %s' % (state['done'], total, _line(job['kind'], job['name'], res,
                                                            final_detail(res, plan.family)[1])))
        sched.run(jobs, on_result, timeout_of, workers)

        # ---- phase 3: jobs that ran next to a job writing outside its directory are rerun alone ----------------------
        writers = [n for n, r in results.items() if r.get('outside') or r.get('spawned')]
        if writers and workers > 1:
            suspects = set()
            for w in writers:
                rw = results[w]
                for n, r in results.items():
                    if n != w and r.get('t0', 0) < rw.get('t1', 0) and rw.get('t0', 0) < r.get('t1', 0):
                        suspects.add(n)
            header.append('rerun alone: %d jobs ran next to a job that wrote outside its directory (%s)'
                          % (len(suspects), writers[:5]))
            log(header[-1])
            kinds = {c[0]: 'control' for c in controls}
            srcs = {c[0]: scorer_src.replace(c[1], c[2]) for c in controls}
            for n in selected:
                srcs[n] = scorer_src.replace(*by_name[n])
            jobs = collections.deque()
            for n in [x for x in [c[0] for c in controls] + selected if x in suspects]:
                history[n].append(('ran next to an outside writer', results.pop(n)))
                state['done'] -= 1
                jobs.append(mk(kinds.get(n, 'mutant'), n, srcs[n], alone=True))
            sched.run(jobs, on_result, timeout_of, 1)
        rc = 0
    except HarnessError as e:
        print('REFUSED: %s' % e)
        if args.out:
            Path(args.out).write_text('\n'.join(header + ['REFUSED: %s' % e]) + '\n', encoding='utf-8')
        return 3
    except KeyboardInterrupt:
        print('INTERRUPTED')
        return 3
    finally:
        sched.close()
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
    out = list(header)
    out.append(_line('baseline', 'BASELINE', b, 'SURVIVED'))
    rows = collections.Counter()
    survivors, bad_controls, unresolved, enc_notes = [], [], [], []
    for name, _, _ in controls:
        res = results[name]
        verdict, detail = final_detail(res, plan.family)
        out.append(_line('control', name, res, detail))
        if verdict != 'SURVIVED':
            bad_controls.append(name)
    for n in skipped_shown:
        out.append('%s  %s  (0.0 s)' % (n, skip_reason[n]))
    for n in selected:
        res = results[n]
        verdict, detail = final_detail(res, plan.family)
        rows[verdict] += 1
        if verdict == 'KILLED' and 'crash' in detail:
            rows['crash'] += 1
        fl = res.get('flags') or {}
        rows['confirmed'] += bool(fl.get('confirm')) and verdict == 'KILLED'
        rows['memo_rerun'] += bool(fl.get('nomemo'))
        rows['alone'] += bool(fl.get('alone'))
        if res.get('enc_note'):
            enc_notes.append(n)
        out.append(_line('mutant', n, res, detail))
        if verdict == 'SURVIVED':
            survivors.append(n)
        elif verdict in ('TIMEOUT', 'ERROR', 'UNRESOLVED'):
            unresolved.append(n)
    wall = time.time() - t_start
    cpu = sum(r.get('seconds', 0.0) for r in results.values()) + (b.get('seconds', 0.0) if b else 0.0)
    out.append('%d mutants: %d killed (%d by a crash of the suite), %d survived, %d unresolved (timeout / harness '
               'error / environment / not reproduced); %d confirmed by a rerun in a fresh process, %d rerun without '
               'the memo, %d rerun alone' % (len(selected), rows['KILLED'], rows['crash'], rows['SURVIVED'],
                                             len(unresolved), rows['confirmed'], rows['memo_rerun'], rows['alone']))
    if controls:
        out.append('controls: %d of %d survived%s' % (len(controls) - len(bad_controls), len(controls),
                                                      (' - NOT SURVIVED: %s' % bad_controls) if bad_controls else ''))
    if unresolved:
        out.append('UNRESOLVED: %s' % unresolved)
    if enc_notes:
        out.append('NOTE: %d mutant(s) printed text the old harness console (%s) cannot encode, where the old harness '
                   'would have crashed (killed); noted, not emulated: %s' % (len(enc_notes), old_enc, enc_notes[:10]))
    if sched.leftover:
        out.append('WARNING could not remove %d job directories: %s' % (len(sched.leftover), sched.leftover[:3]))
    out.append('wall %.1f s, worker time %.1f s, %d workers' % (wall, cpu, workers))
    extra = ''
    if draft_skipped:
        extra += ', %d skipped as draft-only' % len(draft_skipped)
    if filter_skipped:
        extra += ", %d skipped by the mutant script's own filter" % len(filter_skipped)
    counts = '(%d of %d selected mutants killed; %d defined in the mutant script%s)' % (rows['KILLED'], len(selected),
                                                                                      n_defined, extra)
    if survivors:
        out.append('SURVIVORS: %s %s' % (survivors, counts))
    elif unresolved or bad_controls:
        out.append('NOT CERTIFIED (see UNRESOLVED / controls above) %s' % counts)
    else:
        out.append('ALL KILLED %s' % counts)
    text = '\n'.join(out)
    print('\n'.join(out[printed_header:]))
    if args.out:
        Path(args.out).write_text(text + '\n', encoding='utf-8')
    if survivors:
        return 1
    return 2 if (unresolved or bad_controls) else rc


def final_detail(res, family):
    """The verdict of a finished job, taking its confirmation history into account."""
    verdict, detail = classify(res, family)
    if (res.get('flags') or {}).get('confirm'):
        first = [d for why, d in res.get('history', []) if why == 'needs confirmation']
        if verdict == 'KILLED':
            return 'KILLED', detail
        if verdict == 'SURVIVED':
            return 'UNRESOLVED', 'UNRESOLVED (not reproduced: first run %s, the rerun in a fresh process SURVIVED)' % (
                first[0] if first else '?')
    return verdict, detail


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
    fl = res.get('flags') or {}
    if fl.get('confirm'):
        first = [d for why, d in res.get('history', []) if why == 'needs confirmation']
        extra.append('rerun in a fresh process to confirm; first run: %s' % short(first[0] if first else '?', 90))
    if fl.get('nomemo'):
        extra.append('rerun without the memo')
    if fl.get('alone'):
        extra.append('rerun alone (it ran next to a job that wrote outside its directory)')
    if res.get('enc_note'):
        extra.append('note: %s - the old harness would have crashed here' % res['enc_note'])
    if res.get('outside') and kind != 'baseline':
        extra.append('wrote outside its directory: %s' % short(res['outside'][:2], 100))
    s = '%s%s  %s  (%.1f s)' % (prefix, name, detail, res.get('seconds', 0.0))
    if extra:
        s += '  [%s]' % '; '.join(extra)
    return s


if __name__ == '__main__':
    sys.exit(main())
