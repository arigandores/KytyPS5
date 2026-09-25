#!/usr/bin/env python3
"""mutlib.py v4.1 - a fast, strict, shared mutation harness for the session log scorers (a scorer X.py certified by
a fixture suite test_X.py and a mutant list mut_X.py).  Design, guarantees, what changed from v1 / v2 / v3 / v4 and
why, residual assumptions: README.md next to this file (v1 is kept as mutlib_v1.py, v2 as mutlib_v2.py, v3 as
mutlib_v3.py, v4 as mutlib_v4.py).

    python mutlib.py --scorer S --test T --mutants M [--workers N] [--no-memo] [--no-fast] [--no-replay]
                     [--only a,b] [--changed-from PARENT_SCORER --parent-report REPORT [--parent-test T0]
                     [--parent-mutants M0] [--sample 0.2] [--seed N]] [--control]
                     [--python INTERPRETER] [--profile-fixtures] [--timeout SEC] [--out FILE]

v4.1 (ROADMAP session 116 item 1, review5): --changed-from needs the parent's sealed report and also selects every
mutant whose kill case changed in the fixture suite, every mutant the report does not vouch for, and every mutant when
the suite's shared machinery changed; fixture replay turns itself off for copies that raise no audit event
(shutil.copy2 / copytree / move), and such copies are audited in the jobs; --changed-from numbers lines at newline
characters only; the fixture directory cache re-hashes a file written since it was hashed.

v4 adds speed without giving up a v3 guarantee: fixture replay (the fixture files a suite writes are generated once by
the baseline, validated by a second baseline, kept read-only and hard-linked into every job whose generator calls
provably see the same inputs), early exit inside functions, a job interpreter of choice (--python), a fixture profile,
and a robust --changed-from selection for derived scorers.

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
VERSION = 'mutlib 4.1'
DRAFT_MARK_RE = re.compile(r'^#\s*mutlib:\s*draft-only\b')     # a comment that STARTS with the marker
# harness frames that can sit ABOVE a suite / scorer frame: the audit hook (about 6 frames) and, when the parse memo is
# on, the read_run wrapper and its key (up to about 50: _canon descends at most 41 levels).  The job's recursion limit
# is raised by the frames below the suite plus this margin (README: residual assumptions)
RECURSION_MARGIN = 16
RECURSION_MARGIN_MEMO = 64
RECURSION_MARGIN_REPLAY = 8         # v4: the fixture-replay wrapper around a generator call (3 frames) plus slack


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


_SCRIPT_REFLECTION = frozenset({'globals', 'vars', 'locals', 'exec', 'eval', '__import__', 'execfile'})
_SCRIPT_RUNNERS = frozenset({'runpy', 'importlib'})


def _script_reflection(tree):
    """Uses of reflection in a mutant script (globals()['M'].extend(...)) or of a runner of other scripts (runpy,
    importlib): v4 refuses them (review4 T12 / T13)."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in _SCRIPT_REFLECTION:
            out.append('line %d uses %s()' % (n.lineno, n.id))
        elif isinstance(n, ast.Attribute) and n.attr in ('__dict__', 'modules') and not (
                n.attr == 'modules' and not (isinstance(n.value, ast.Name) and n.value.id == 'sys')):
            out.append('line %d uses .%s' % (n.lineno, n.attr))
        elif isinstance(n, ast.Import) and any(a.name.split('.')[0] in _SCRIPT_RUNNERS for a in n.names):
            out.append('line %d imports %s' % (n.lineno, [a.name for a in n.names]))
        elif isinstance(n, ast.ImportFrom) and (n.module or '').split('.')[0] in _SCRIPT_RUNNERS:
            out.append('line %d imports from %s' % (n.lineno, n.module))
    return out


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
    refl = _script_reflection(tree)
    if refl:
        # v4 (review4 T12 / T13): mutants defined through reflection or in another script the harness part runs are
        # invisible to the strict extraction
        raise HarnessError('strict mutant extraction refused %s: %s - mutants reached that way are invisible to mutlib'
                           % (mut_path.name, '; '.join(refl[:3])))
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
    hc.check_test_calls()
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
        self.cur_site = self.cur_site_scope = None

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

    # ---- 2b. how the harness part runs the suite (v4, review4 T11) -------------------------------------------------
    def check_test_calls(self):
        """A `subprocess.*([sys.executable, (flags,) TEST, mutant(, fx dir)], ...)` call in the harness part must not
        pass the suite more than mutlib does: an extra argument (`--quick`), a flag after the script or an `env=`
        would run a different suite than the one mutlib runs -> refuse."""
        for n in ast.walk(self.tree):
            if id(n) in self.def_ids or not isinstance(n, ast.Call):
                continue
            f = n.func
            fname = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
            if fname not in ('run', 'call', 'check_call', 'check_output', 'Popen'):
                continue
            if not n.args or not isinstance(n.args[0], (ast.List, ast.Tuple)) or not n.args[0].elts:
                continue
            elts = n.args[0].elts
            first = elts[0]
            if not (isinstance(first, ast.Attribute) and first.attr == 'executable'):
                continue                                    # not a Python process
            if any(k.arg == 'env' for k in n.keywords):
                self.refuse('line %d: the harness part runs the suite with its own environment (env=...); mutlib '
                            'runs it in its own' % n.lineno)
            rest = list(elts[1:])
            while rest and isinstance(rest[0], ast.Constant) and isinstance(rest[0].value, str) \
                    and rest[0].value.startswith('-'):
                rest.pop(0)                                 # interpreter flags (-B, -u, ...)
            after = rest[1:]                                # after the script: the mutant, maybe a fixture directory
            flags = [e for e in after if isinstance(e, ast.Constant) and isinstance(e.value, str)
                     and e.value.startswith('-')]
            if flags or len(after) > 2 or any(isinstance(e, ast.Starred) for e in after):
                self.refuse('line %d: the harness part passes the suite %s; mutlib passes only the mutant scorer '
                            '(and a fixture directory)' % (n.lineno, short(ast.unparse(n.args[0]), 80)))

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

    def _only_read(self, name, scope, bs):
        """Every load of `name` that resolves to the binding `bs` (in `scope`) is a read-only use: nothing can change
        its value after the definition (`.discard`, `.add`, `[:] = `, `del x[0]`, an alias, a helper that changes it,
        passing it to a call that could keep it)."""
        for u in self.loads.get(name, []):
            if self.lookup(name, self.scope_of.get(id(u), self.tree))[1] is bs and not _readonly_use(u, self.parents):
                return False
        return True

    def _site_receiver(self):
        site = self.cur_site
        f = site.func
        if isinstance(f.value, ast.Name) and f.value.id in ('str', 'bytes') and site.args:
            return site.args[0]
        return f.value

    def _is_site_receiver(self, node, scope):
        """`node` names the very text the substitution at the current site edits (the same binding)."""
        if self.cur_site is None or not isinstance(node, ast.Name):
            return False
        recv = self._site_receiver()
        if not isinstance(recv, ast.Name) or recv.id != node.id:
            return False
        return self.lookup(node.id, scope)[1] is self.lookup(recv.id, self.cur_site_scope)[1]

    def _eval(self, e, env, vals, scope, local, depth=0):
        if depth > 30:
            raise _Unknown('too deep')
        ev = lambda x: self._eval(x, env, vals, scope, local, depth + 1)  # noqa: E731
        if isinstance(e, ast.Constant):
            return e.value
        if isinstance(e, ast.Name):
            # v4 (review4 MAJOR-1): a name is evaluated only where its value needs no fallback; anything else refuses
            s, bs = self.lookup(e.id, scope)
            if e.id in env:
                if len(bs) != 1:                    # `name = name.upper()`: the old harness filters the new value
                    raise _Unknown('%s is rebound in its scope (%d bindings)' % (e.id, len(bs)))
                return vals[env[e.id]]
            if e.id in local:
                if local[e.id] is None or len(bs) != 1:
                    raise _Unknown('%s is bound in front of the filter in a way mutlib does not follow' % e.id)
                v = self._eval(local[e.id], env, vals, scope, {k: v for k, v in local.items() if k != e.id},
                               depth + 1)
                if not _immutable_value(v) and not self._only_read(e.id, s, bs):   # a container: nothing may
                    raise _Unknown('%s is changed or handed out after it is bound' % e.id)  # change it after
                return v
            if s is not self.tree:
                raise _Unknown('%s is a function-local name' % e.id)
            if len(bs) == 1 and bs[0][0] == 'store':
                tp = self._target_path(bs[0][1])
                if tp is not None and isinstance(tp[1], ast.Assign) and tp[0] is bs[0][1] \
                        and len(tp[1].targets) == 1 and tp[1] in self.tree.body \
                        and self.cur_site is not None and tp[1].lineno < self.cur_site.lineno:
                    try:
                        lit = ast.literal_eval(tp[1].value)
                    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                        raise _Unknown('%s is not a literal' % e.id)
                    if not _immutable_value(lit) and not self._only_read(e.id, s, bs):
                        raise _Unknown('%s is changed or handed out after its literal definition (line %d)'
                                       % (e.id, tp[1].lineno))
                    return lit
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
                    # v4 (review4 MAJOR-1): only the anchor check `SRC.count(old)` - the receiver the substitution
                    # itself edits, the argument the element's old text - falls back to the scorer text; any other
                    # receiver mutlib cannot evaluate (a file of equivalent names, ...) refuses
                    if not (self._is_site_receiver(f.value, scope) and isinstance(e.args[0], ast.Name)
                            and env.get(e.args[0].id) == 'old' and isinstance(arg, str)):
                        raise _Unknown('%s: .count on a receiver mutlib cannot evaluate' % short(ast.unparse(e), 50))
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
            self.cur_site, self.cur_site_scope = site, scope
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
    """0-based line numbers of `src` that differ from `parent_src` (a deletion marks the lines around it).  v4.1
    (review5 MINOR-4): lines are split at newline characters only, as anchor_lines counts them (str.splitlines also
    breaks at form feed, vertical tab, the file / group / record separators, NEL, the Unicode line and paragraph
    separators and a lone carriage return, which shifted every later line)."""
    a, b = parent_src.split('\n'), src.split('\n')
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
        # v4: early exit is allowed inside a function too (the kill is recorded before the raise and honoured even if
        # the suite swallows the exception, review4 MINOR-2)
        return ast.Call(func=ast.Name(PFX + 'guard', ast.Load()),
                        args=[ast.Name(self.okname, ast.Load()), value, label, ast.Constant(node.lineno),
                              ast.Constant(True), ast.Constant(self.orient.get(id(node), '?')),
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
        self.fx_names = fx_generator_names(tree, okname)       # v4: the fixture generators (replay candidates)
        self._codes = {}

    def code_for(self, fx=False, case_hook=False):
        """v4: the suite's code with the fixture generators wrapped (replay / recording) and / or the case hook."""
        key = (bool(fx), bool(case_hook))
        if key == (False, False):
            return self.code
        if key not in self._codes:
            self._codes[key] = build_test_code(self, fx_names=self.fx_names if fx else None, case_hook=case_hook)
        return self._codes[key]

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

    def _ok_bindings(self):
        """Every node that binds the MODULE's pass flag, in source order: in module scope and in every function (at
        any depth) that declares it global, including a walrus in a comprehension there (it binds in the enclosing
        scope); a nested function / lambda / class / comprehension scope of its own is not entered."""
        ok = self.okname
        roots = list(self.tree.body)
        for n in ast.walk(self.tree):
            if isinstance(n, _FUNC_NODES) and ok in declared_globals(n):
                roots.extend(n.body)
        out = []

        def visit(node):
            for m in stmt_nodes(node):
                if isinstance(m, ast.Name) and m.id == ok and isinstance(m.ctx, (ast.Store, ast.Del)):
                    out.append(m)
                elif isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and m.name == ok:
                    out.append(m)
                elif isinstance(m, (ast.Import, ast.ImportFrom)) and ok in import_names(m):
                    out.append(m)
                elif isinstance(m, ast.ExceptHandler) and m.name == ok:
                    out.append(m)
                elif isinstance(m, (ast.MatchAs, ast.MatchStar)) and m.name == ok:
                    out.append(m)
                elif isinstance(m, ast.MatchMapping) and m.rest == ok:
                    out.append(m)
                if isinstance(m, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                    for c in ast.walk(m):         # a walrus in a comprehension binds in THIS scope
                        if isinstance(c, ast.NamedExpr) and isinstance(c.target, ast.Name) and c.target.id == ok:
                            if not any(isinstance(a, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef,
                                                      ast.ClassDef)) for a in self._between(c, m)):
                                out.append(c.target)
        for r in roots:
            visit(r)
        uniq, seen = [], set()
        for m in out:
            if id(m) not in seen:
                seen.add(id(m))
                uniq.append(m)
        return sorted(uniq, key=lambda m: (getattr(m, 'lineno', 0), getattr(m, 'col_offset', 0)))

    def _between(self, node, top):
        if not hasattr(self, '_parents'):
            self._parents = parent_map(self.tree)
        out, p = [], self._parents.get(node)
        while p is not None and p is not top:
            out.append(p)
            p = self._parents.get(p)
        return out

    def _fast_analysis(self):
        ok = self.okname
        inits = updates = 0
        problems = []
        parents = parent_map(self.tree)
        # v4 (review4 MINOR-1): EVERY binding of the module's ok is classified; anything but the one `ok = True` and
        # `ok &= ...` / `ok = ok and ...` (a tuple / list / starred target, a walrus, a match capture, another
        # augmented operator, a loop / with / except target, an import, a def, del) turns fast mode off
        for m in self._ok_bindings():
            p = parents.get(m)
            if isinstance(m, ast.Name) and isinstance(p, ast.Assign) and m in p.targets:
                v = p.value
                if len(p.targets) != 1:
                    problems.append('line %d assigns %s in a chain' % (p.lineno, ok))
                elif isinstance(v, ast.Constant) and v.value is True and inits == 0 and updates == 0:
                    inits += 1
                elif _is_guard_stmt(p, ok):
                    updates += 1
                else:
                    problems.append('line %d: %s = %s' % (p.lineno, ok, short(ast.unparse(v), 40)))
            elif isinstance(m, ast.Name) and isinstance(p, ast.AugAssign) and p.target is m:
                if isinstance(p.op, ast.BitAnd):
                    updates += 1
                else:
                    problems.append('line %d: %s %s= ...' % (p.lineno, ok, type(p.op).__name__))
            elif isinstance(m, ast.Name) and isinstance(m.ctx, ast.Del):
                problems.append('line %d deletes %s' % (m.lineno, ok))
            else:
                try:
                    what = short(ast.unparse(p if isinstance(p, ast.stmt) else m), 40)
                except Exception:
                    what = type(m).__name__
                problems.append('line %d binds %s (%s)' % (getattr(m, 'lineno', 0), ok, what))
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


def build_test_code(plan, fx_dir=None, fx_names=None, case_hook=False):
    """The transformed suite as a code object: BASE -> the job's fixture directory (read from the job's globals, so
    one code object serves every job; `fx_dir` is ignored, kept for old callers), guards, the end-of-suite marker,
    the output hooks.  v4: `fx_names` - the fixture generators, each rebound right after its def to the replay
    wrapper (`F = _mutlib_fx(F, 'F')`); `case_hook` - `case` rebound to the fixture profile's registration hook."""
    tree = copy.deepcopy(plan.tree)
    body = tree.body
    if fx_names or case_hook:
        new_body = []
        for st in body:
            new_body.append(st)
            if isinstance(st, ast.FunctionDef) and (st.name in (fx_names or ()) or (case_hook and st.name == 'case')):
                fn = PFX + ('case' if st.name == 'case' and case_hook else 'fx')
                args = '%s, %r' % (st.name, st.name) if fn.endswith('fx') else st.name
                w = snippet('%s = %s(%s)' % (st.name, fn, args))[0]
                for n in ast.walk(w):
                    n.lineno, n.end_lineno = st.end_lineno, st.end_lineno
                    n.col_offset, n.end_col_offset = 0, 0
                new_body.append(w)
        old_final = plan.tree.body[plan.final_idx] if plan.final_idx is not None else None
        if fx_names and old_final is not None:
            # the N family: `_mutlib_phase()` right before the final loop (the recording baselines dump there)
            i = next(i for i, st in enumerate(new_body) if isinstance(st, ast.For) and st.lineno == old_final.lineno)
            ph = snippet('%sphase()' % PFX)[0]
            for n in ast.walk(ph):
                n.lineno, n.end_lineno = old_final.lineno, old_final.lineno
                n.col_offset, n.end_col_offset = 0, 0
            new_body.insert(i, ph)
        tree.body = body = new_body
        plan = copy.copy(plan)
        plan.base_idx = next(i for i, st in enumerate(body) if 'BASE' in bound_names(st))
        if plan.final_idx is not None:
            plan.final_idx = next(i for i, st in enumerate(body) if isinstance(st, ast.For)
                                  and st.lineno == old_final.lineno)
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


_SINGLETON_NAMES = frozenset({'None', 'True', 'False', 'Ellipsis', 'NotImplemented'})


_BUILTIN_TYPE_NAMES = frozenset({'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple', 'set', 'frozenset', 'bytes',
                                 'bytearray', 'complex', 'type', 'object', 'range', 'slice'})


def _is_singleton(n):
    """An operand whose identity a copy cannot change: None / True / False / Ellipsis / NotImplemented, a builtin
    type, `type(x)` (a class; classes are pickled by reference) or `x.__class__`."""
    return ((isinstance(n, ast.Constant) and (n.value is None or n.value is True or n.value is False
                                               or n.value is Ellipsis))
            or (isinstance(n, ast.Name) and (n.id in _SINGLETON_NAMES or n.id in _BUILTIN_TYPE_NAMES))
            or (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'type' and len(n.args) == 1
                and not n.keywords)
            or (isinstance(n, ast.Attribute) and n.attr == '__class__'))


def identity_uses(tree):
    """v4 (review4 MAJOR-2): the memo returns a fresh copy of read_run's value, so an object in it is never the
    object the uncached call returned: `x is MISSING` (a sentinel), `r['kind'] is 'empty'` (an interned literal) or
    id() can change their answer.  Every `is` / `is not` whose operands are not a None / True / False / Ellipsis /
    NotImplemented singleton, every call of id(), and operator.is_ / is_not."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare):
            left = n.left
            for op, right in zip(n.ops, n.comparators):
                if isinstance(op, (ast.Is, ast.IsNot)) and not (_is_singleton(left) or _is_singleton(right)):
                    out.append('line %d: %s' % (n.lineno, short(ast.unparse(n), 50)))
                left = right
        elif isinstance(n, ast.Name) and n.id == 'id' and isinstance(n.ctx, ast.Load):
            out.append('line %d: id()' % n.lineno)
        elif (isinstance(n, ast.Attribute) and n.attr in ('is_', 'is_not')) or (
                isinstance(n, ast.alias) and n.name in ('is_', 'is_not')):
            out.append('line %d: operator.%s' % (getattr(n, 'lineno', 0), getattr(n, 'attr', getattr(n, 'name', ''))))
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
    ident = identity_uses(tree)
    if ident:
        return MemoPlan(False, 'the module compares object identity (a fresh copy would change the answer): %s'
                        % '; '.join(ident[:3]))
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


class _Restart(Exception):
    """v4: the pipelined start is abandoned; the run starts again the v3 way."""


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
_LISTING = frozenset({'os.listdir', 'os.scandir', 'glob.glob', 'glob.glob/2'})     # v4: directory reads (replay)
_MMAP = frozenset({'mmap.__new__'})
_AUDITED = frozenset({'open'}) | _WRITE_1 | _WRITE_BOTH | _WRITE_DST | _SPAWN | _TEMP | _LISTING | _MMAP


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


_NAN_FLOAT = re.compile(rb'G[\x7f\xff][\xf0-\xff]')


def _blob_has_nan(blob):
    """Does a pickle hold a float NaN?  Every float (also inside a complex or a float subclass) is pickled as BINFLOAT:
    'G' and 8 big-endian bytes; a NaN's first two bytes are 7F / FF and F0..FF.  A match that is not a NaN (the same
    bytes inside a string, an infinity) is ruled out by decoding it.  read_run's allow-list cannot build a Decimal."""
    import struct
    for m in _NAN_FLOAT.finditer(blob):
        raw = blob[m.start() + 1:m.start() + 9]
        if len(raw) == 8:
            v = struct.unpack('>d', raw)[0]
            if v != v:
                return True
    return False


def _has_nan(root, limit=20000000):
    """Does a value hold a float / complex NaN (or a Decimal NaN) anywhere in its containers?  Too large -> True."""
    seen, stack = set(), [root]
    n = 0
    while stack:
        v = stack.pop()
        t = type(v)
        if t is float:
            if v != v:
                return True
            continue
        if t is complex:
            if v != v:
                return True
            continue
        if t in (str, bytes, int, bool) or v is None:
            continue
        if isinstance(v, (dict, list, tuple, set, frozenset, collections.deque)):
            i = id(v)
            if i in seen:
                continue
            seen.add(i)
            n += 1
            if n > limit:
                return True
            if isinstance(v, dict):
                stack.extend(v.keys())
                stack.extend(v.values())
            else:
                stack.extend(v)
            continue
        if isinstance(v, float):                    # float subclasses
            if v != v:
                return True
            continue
        try:
            if v != v:                              # Decimal('NaN') and anything else not equal to itself
                return True
        except Exception:
            return True
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
        if plan.dep_hash != self.shared_dep:
            # v4: this job's read_run closure is mutated: its values could only be reused inside this job, and a
            # guarded miss costs more than such a repeat saves (ttl114b: +0.39 s a miss on a 0.88 s parse, about 200
            # parses against 51 repeats); without the memo the job computes what the old harness computed
            return self._off('the read_run closure of this mutant differs from the scorer\'s: no memo')
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
        if _blob_has_nan(blob):
            # v4 (review4 MAJOR-2 backstop): a NaN is equal only to itself by identity (`v in rows`, `[v] == [v]`,
            # dict / set lookups), so a fresh copy could change an answer: never stored, the original returned
            self.stats['nan_in_result'] += 1
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


# ======================================================================================================================
# v4: fixture replay.  The files a suite's fixture generators write (the top-level test functions that can write a
# file: make() / variant() / video() in the N suites) are produced ONCE per run by the baseline R1, which records every
# generator call: its inputs (the arguments, the test globals its code can read, the scorer-module attributes it read,
# the random state, the environment, the fixture directory's state before the call, the files outside it that it
# read) and its effects (the fixture directory's changes and its return value).  A second baseline R2, run in a job
# directory of the same path length, records the same calls independently; a call is replayable only if both records
# agree once the job directory is written as a placeholder, so a generator that embeds anything but the job path, or
# depends on time, the process, the hash seed or global random state, is never replayed.  A job replays call #i only
# if every input R1 recorded is equal NOW; replaying = hard-linking the recorded files (kept read-only in the run's
# store) into the job's own fixture directory, writing the files that carry the job path with THIS job's path, and
# returning the recorded value.  A job that tries to change or delete a shared file (or its mode) is stopped and rerun
# in a fully isolated fresh process; the parent checks the store after every job and re-hashes it at the end.
# ======================================================================================================================
class FxTouched(BaseException):
    """The job tried to change, delete or re-mode a shared read-only fixture file: its result is discarded and it is
    rerun in a fully isolated fresh process (no replay)."""


class FxUnsupported(Exception):
    pass


FX_MAX_TEMPLATE = 8 * 1024 * 1024        # a file carrying the job path is replayed by writing it: up to this size
FX_MAX_CALLS_PER_FN = 5000               # depth-0 calls of one generator that are recorded
FX_MIN_SAVING_S = 1.0                    # replay is used only if the validated calls took at least this long in R1
FX_LINK_LIMIT = 900                      # NTFS allows 1023 names per file; above this a job gets a private copy
_FX_WRITE_NAMES = frozenset({'write_text', 'write_bytes', 'open', 'mkdir', 'makedirs', 'link', 'hardlink_to',
                             'symlink_to', 'copyfile', 'copy', 'copy2', 'copytree', 'copyfileobj', 'dump', 'rename',
                             'replace', 'unlink', 'remove', 'rmtree', 'rmdir', 'symlink', 'touch', 'write',
                             'writelines', 'move', 'truncate', 'savez', 'save', 'mkstemp', 'mkdtemp',
                             'NamedTemporaryFile', 'TemporaryDirectory', 'ZipFile', 'TarFile'})
_FX_DENY = frozenset({'st_mtime', 'st_mtime_ns', 'st_ctime', 'st_ctime_ns', 'st_atime', 'st_atime_ns', 'st_birthtime',
                      'st_birthtime_ns', 'getmtime', 'getctime', 'getatime', 'st_ino', 'st_dev', 'st_nlink',
                      'samefile', 'samestat', 'sameopenfile', 'st_mode', 'st_file_attributes', 'st_reparse_tag',
                      'st_flags', 'S_IMODE', 'S_IWRITE', 'S_IREAD', 'S_IWUSR', 'filemode', 'is_symlink', 'readlink',
                      'lstat', 'is_junction'})
_FX_DENY_ATTR_ONLY = frozenset({'access'})          # os.access(...): only as an attribute / an imported name
_FX_PH = ['\x00MUTLIBJ%d\x00' % k for k in range(6)]


def fx_deny_uses(tree):
    """What a scorer or a suite could see of a replayed fixture that a freshly written one would not show: its times
    (the store's), its inode and link count, its read-only mode.  Any of these names turns replay off for the run."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute):
            nm = n.attr
        elif isinstance(n, ast.Name):
            nm = n.id if n.id not in _FX_DENY_ATTR_ONLY else None
        elif isinstance(n, ast.alias):
            nm = n.asname or n.name
            nm = n.name if n.name in _FX_DENY | _FX_DENY_ATTR_ONLY else nm
        else:
            continue
        if nm in _FX_DENY or (nm in _FX_DENY_ATTR_ONLY and not isinstance(n, ast.Name)):
            out.append('line %d: %s' % (getattr(n, 'lineno', 0), nm))
    return out


_FX_COPY_BYPASS = frozenset({'copy2', 'copytree', 'CopyFile2', '_winapi', 'ctypes', 'windll', 'cdll', 'oledll',
                             'WinDLL', 'CDLL', 'OleDLL'})
FX_COPY_BYPASS_RE = re.compile(r'\b(%s)\b|\bshutil\s*\.\s*move\b' % '|'.join(sorted(_FX_COPY_BYPASS)))


def fx_copy_bypass_uses(tree):
    """v4.1 (review5 MAJOR-2): copies that raise no audit event.  CPython 3.12+ on Windows copies shutil.copy2 /
    copytree (and shutil.move across volumes) through _winapi.CopyFile2: a replayed read-only fixture is copied
    read-only (a later append fails: a false kill), and the copy is invisible to the write audit.  Any use of these
    names (a name, an attribute, an import, shutil.move, a getattr string) turns fixture replay off for the run."""
    out = []
    shutil_names = {'shutil'}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == 'shutil' and a.asname:
                    shutil_names.add(a.asname)
    for n in ast.walk(tree):
        nm = None
        if isinstance(n, ast.Attribute):
            if n.attr in _FX_COPY_BYPASS or (n.attr == 'move' and root_name(n.value) in shutil_names):
                nm = n.attr
        elif isinstance(n, ast.Name) and n.id in _FX_COPY_BYPASS:
            nm = n.id
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name in _FX_COPY_BYPASS or (n.module or '').split('.')[0] in _FX_COPY_BYPASS \
                        or (n.module == 'shutil' and a.name in ('move', '*')):
                    nm = a.name
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split('.')[0] in _FX_COPY_BYPASS:
                    nm = a.name
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in _FX_COPY_BYPASS:
            nm = repr(n.value)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'getattr' \
                and len(n.args) > 1 and isinstance(n.args[1], ast.Constant) and n.args[1].value == 'move':
            nm = "getattr(..., 'move')"
        if nm is not None:
            out.append('line %d: %s' % (getattr(n, 'lineno', 0), nm))
    return out


def fx_generator_names(tree, okname):
    """Top-level test functions whose code can write a file, directly or by calling another such function; not
    decorated, not a generator / coroutine, no global / nonlocal statement, no update of the pass flag."""
    defs = {}
    for st in tree.body:
        if isinstance(st, ast.FunctionDef):
            defs.setdefault(st.name, []).append(st)
    names = {n: fs[0] for n, fs in defs.items() if len(fs) == 1}
    rebound = set()
    for st in tree.body:
        if not isinstance(st, ast.FunctionDef):
            rebound |= bound_names(st) & set(names)
    writes = {n for n, fn in names.items() if any(
        (isinstance(m, ast.Attribute) and m.attr in _FX_WRITE_NAMES)
        or (isinstance(m, ast.Name) and m.id in _FX_WRITE_NAMES) for m in ast.walk(fn))}
    changed = True
    while changed:
        changed = False
        for n, fn in names.items():
            if n not in writes and any(isinstance(m, ast.Name) and m.id in writes for m in ast.walk(fn)):
                writes.add(n)
                changed = True

    def fine(fn):
        if fn.decorator_list:
            return False
        for m in ast.walk(fn):
            if isinstance(m, (ast.Global, ast.Nonlocal, ast.Yield, ast.YieldFrom, ast.Await, ast.AsyncFunctionDef)):
                return False
            if isinstance(m, ast.stmt) and _is_guard_stmt(m, okname):
                return False
        return True
    return sorted(n for n in writes if n != 'case' and n not in rebound and fine(names[n]))


def _fx_forms(J):
    """The spellings of a job directory that a fixture can carry: as given, with forward slashes, backslash-escaped
    (repr / JSON), and lower-cased (os.path.normcase); longest first, each with its placeholder index."""
    out = []
    for f in (J.replace('\\', '\\\\'), J.replace('\\', '\\\\').lower(), J, J.lower(), J.replace('\\', '/'),
              J.replace('\\', '/').lower()):
        if f not in [x for _, x in out]:
            out.append((len(out), f))
    return out


def _fx_immutable(v, depth=0):
    if depth > 30:
        return False
    if v is None or type(v) in (bool, int, float, complex, str, bytes, range) or isinstance(v, (PurePath, re.Pattern)):
        return True
    if type(v) in (tuple, frozenset):
        return all(_fx_immutable(x, depth + 1) for x in v)
    return False


def _unlink_ro(path):
    """Deletes one directory entry whose file is read-only WITHOUT clearing the attribute (it belongs to the file, so
    every hard link to it would lose it): FILE_DISPOSITION_FLAG_IGNORE_READONLY_ATTRIBUTE, Windows 10 1809+."""
    path = str(path)
    try:
        os.unlink(path)
        return
    except PermissionError:
        if os.name != 'nt':
            raise
    import ctypes
    from ctypes import wintypes as wt
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    create = k32.CreateFileW
    create.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, wt.LPVOID, wt.DWORD, wt.DWORD, wt.HANDLE]
    create.restype = wt.HANDLE
    setinfo = k32.SetFileInformationByHandle
    setinfo.argtypes = [wt.HANDLE, ctypes.c_int, wt.LPVOID, wt.DWORD]
    setinfo.restype = wt.BOOL
    close = k32.CloseHandle
    close.argtypes = [wt.HANDLE]

    class _Disp(ctypes.Structure):
        _fields_ = [('Flags', wt.DWORD)]
    h = create(os.path.abspath(path), 0x00010000, 7, None, 3, 0x02000000 | 0x00200000, None)
    if h is None or h == wt.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        info = _Disp(0x1 | 0x2 | 0x10)                 # DELETE | POSIX_SEMANTICS | IGNORE_READONLY_ATTRIBUTE
        if not setinfo(h, 21, ctypes.byref(info), ctypes.sizeof(info)):   # FileDispositionInfoEx
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        close(h)


def _rmtree_force(d):
    """shutil.rmtree that also removes directory entries of read-only (shared, hard-linked) files."""
    def onexc(func, p, exc):
        e = exc[1] if isinstance(exc, tuple) else exc
        if func in (os.unlink, os.remove) and isinstance(e, PermissionError):
            _unlink_ro(p)
            return
        raise e
    if sys.version_info >= (3, 12):
        shutil.rmtree(d, onexc=onexc)
    else:
        shutil.rmtree(d, onerror=onexc)


class _FxModule(types.ModuleType):
    """The scorer module's class while fixture replay is on: attribute reads (and writes) are seen during a recorded
    generator call."""

    def __getattribute__(self, name):
        rt = _RT
        fx = rt.fx if rt is not None else None
        if fx is not None and fx.track is not None:
            fx.track.add((fx.module_index(self), name))
        return types.ModuleType.__getattribute__(self, name)

    def __setattr__(self, name, value):
        rt = _RT
        fx = rt.fx if rt is not None else None
        if fx is not None and fx.track is not None:
            fx.track_write = True
        types.ModuleType.__setattr__(self, name, value)

    def __delattr__(self, name):
        rt = _RT
        fx = rt.fx if rt is not None else None
        if fx is not None and fx.track is not None:
            fx.track_write = True
        types.ModuleType.__delattr__(self, name)


class FxRuntime:
    """The job side of fixture replay.  mode 'record' (R1 with the store, R2 and the fixture profile without) or
    'replay' (every other job that is eligible)."""

    def __init__(self, rt, spec, job_dir, base_dir, mutant_path):
        self.rt, self.spec, self.mode = rt, spec, spec['mode']
        self.J = str(job_dir)
        self.base = str(base_dir)
        self.nbase = os.path.normcase(os.path.abspath(self.base))
        self.nJ = os.path.normcase(os.path.abspath(self.J))
        self.forms = _fx_forms(self.J)
        self.bforms = [(k, f.encode('utf-8', 'surrogatepass')) for k, f in self.forms]
        self.mutant_norm = os.path.normcase(os.path.abspath(str(mutant_path)))
        self.g = None
        self.mods = []
        self.mod_ids = {}
        self.depth = 0
        self.seq = 0
        self.per_fn = collections.Counter()
        self.track = None
        self.track_write = False
        self.cur = None
        self.records = []
        self.cache = {}
        self.wgen = 0                                       # v4.1: write events so far (review5 MINOR-5)
        self.dirty_np = {}                                  # path -> the write event that last touched it
        self.dirty_ino = {}                                 # (inode, device) -> the same, for its other names
        self.clean = False
        self.digest = None
        self.watch = set()
        self.watch_state = {}
        self.touched = None
        self.failed = None
        self.stats = collections.Counter()
        self.first_miss = None
        self.cases = []                                     # the fixture profile: (time, case name)
        self.code_names = {}
        self.produced = {}                                  # record: file a recorded call produced -> its rel
        self.read_cids = set()                              # replay: shared files the job read
        self.later_touched = set()                          # record: produced files the suite changed later
        self.store = spec.get('store')
        self.store_inodes = {}
        if self.mode == 'replay':
            with open(spec['plan'], 'rb') as fh:
                plan = pickle.load(fh)
            self.recs = plan['records']
            self.J1 = plan['J1']
            self.noop = plan['noop']
            # the store files' identities as THIS interpreter reports them (PyPy's st_dev differs from CPython's)
            for cid in plan['inodes'].values():
                st = os.stat(os.path.join(spec['store'], cid))
                self.store_inodes[(st.st_ino, st.st_dev)] = cid

    # ---- text: the job directory as a placeholder ----------------------------------------------------------------
    def norm_s(self, s, forms=None):
        for k, f in (forms or self.forms):
            if f in s:
                s = s.replace(f, _FX_PH[k])
        return s

    def norm_b(self, b, bforms=None):
        for k, f in (bforms or self.bforms):
            if f in b:
                b = b.replace(f, _FX_PH[k].encode())
        return b

    def denorm_s(self, s):
        if '\x00' not in s:
            return s
        for k, f in self.forms:
            s = s.replace(_FX_PH[k], f)
        return s

    def denorm_b(self, b):
        if b'\x00' not in b:
            return b
        for k, f in self.bforms:
            b = b.replace(_FX_PH[k].encode(), f)
        return b

    def npath(self, p):
        if p is None or isinstance(p, int):
            return None
        try:
            return os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(p))))
        except (TypeError, ValueError):
            return None

    def under_base(self, np):
        return np is not None and (np == self.nbase or np.startswith(self.nbase.rstrip('\\/') + os.sep))

    def under_J(self, np):
        return np is not None and (np == self.nJ or np.startswith(self.nJ.rstrip('\\/') + os.sep))

    # ---- the scorer module ---------------------------------------------------------------------------------------
    def register_module(self, module):
        if self.mode == 'record':
            # only the two recording baselines follow attribute reads; a replaying job only reads values
            try:
                module.__class__ = _FxModule
            except TypeError as e:
                self.failed = self.failed or 'cannot follow the scorer module: %s' % e
                return
        self.mod_ids[id(module)] = len(self.mods)
        self.mods.append(module)

    def module_index(self, module):
        return self.mod_ids.get(id(module), -1)

    def mod_value(self, mi, name):
        if mi < 0 or mi >= len(self.mods):
            raise FxUnsupported('an attribute of an unknown scorer module')
        saved, self.track = self.track, None
        try:
            return types.ModuleType.__getattribute__(self.mods[mi], name)
        except AttributeError:
            return _MISSING
        finally:
            self.track = saved

    # ---- fingerprints (process-independent, the job directory as a placeholder) ----------------------------------
    def fp(self, v, depth=0, active=None):
        if depth > 60:
            raise FxUnsupported('a value nested too deeply')
        if active is None:
            active = set()
        t = type(v)
        if v is None or t in (bool, int):
            return (t.__name__, v)
        if v is _MISSING:
            return ('MISSING',)
        if t is float or t is complex:
            return (t.__name__, repr(v))
        if t is str:
            return ('s', self.norm_s(v))
        if t in (bytes, bytearray):
            return (t.__name__, self.norm_b(bytes(v)))
        if v is Ellipsis or v is NotImplemented:
            return ('const', repr(v))
        if isinstance(v, PurePath):
            return ('path', t.__name__, self.norm_s(str(v)))
        if isinstance(v, re.Pattern):
            p = v.pattern
            return ('re', self.norm_s(p) if isinstance(p, str) else self.norm_b(p), v.flags)
        if t is range:
            return ('range', v.start, v.stop, v.step)
        if t is slice:
            return ('slice', self.fp(v.start, depth + 1, active), self.fp(v.stop, depth + 1, active),
                    self.fp(v.step, depth + 1, active))
        if t in (tuple, list, set, frozenset, dict, collections.OrderedDict, collections.defaultdict,
                 collections.Counter, collections.deque) or (isinstance(v, tuple) and hasattr(v, '_fields')):
            i = id(v)
            if i in active:
                raise FxUnsupported('a cyclic value')
            active.add(i)
            try:
                if isinstance(v, dict):
                    items = tuple((self.fp(a, depth + 1, active), self.fp(b, depth + 1, active)) for a, b in v.items())
                    extra = self.fp(v.default_factory, depth + 1, active) if t is collections.defaultdict else None
                    return ('dict', t.__name__, items, extra)
                if t in (set, frozenset):
                    return (t.__name__, tuple(sorted((self.fp(x, depth + 1, active) for x in v), key=repr)))
                return (t.__name__, tuple(self.fp(x, depth + 1, active) for x in v))
            finally:
                active.discard(i)
        wrapped = getattr(v, '_mutlib_fx_wrapped', None) if callable(v) else None
        if wrapped is not None:
            return ('fxwrap', self.fp(wrapped, depth + 1, active))
        if isinstance(v, types.ModuleType):
            mi = self.mod_ids.get(id(v))
            if mi is not None:
                return ('scorer_module', mi)
            f = getattr(v, '__file__', None)
            if f and self.npath(f) == self.mutant_norm:
                raise FxUnsupported('the scorer is loaded in a way mutlib does not follow')
            return ('module', v.__name__)
        if isinstance(v, types.FunctionType):
            if v.__globals__ is self.g:
                cells = tuple(self.fp(self._cell(c), depth + 1, active) for c in (v.__closure__ or ()))
                return ('fn', self._code_fp(v.__code__), self.fp(v.__defaults__, depth + 1, active),
                        self.fp(v.__kwdefaults__, depth + 1, active), cells)
            if any(v.__globals__ is m.__dict__ for m in self.mods) or \
                    self.npath(v.__globals__.get('__file__')) == self.mutant_norm:
                raise FxUnsupported('a scorer function (%s)' % getattr(v, '__qualname__', '?'))
            if v.__closure__:
                raise FxUnsupported('a closure outside the suite (%s)' % getattr(v, '__qualname__', '?'))
            return ('pyfn', getattr(v, '__module__', None), v.__qualname__)
        if isinstance(v, types.BuiltinFunctionType):
            s = getattr(v, '__self__', None)
            if s is None or isinstance(s, types.ModuleType):
                return ('bfn', getattr(v, '__module__', None) or getattr(s, '__name__', None), v.__qualname__)
            return ('bmeth', v.__qualname__, self.fp(s, depth + 1, active))
        if isinstance(v, types.MethodType):
            if v.__self__ is self.rt or v.__self__ is self:
                return ('mutlib_api', v.__func__.__name__)
            return ('meth', self.fp(v.__func__, depth + 1, active), self.fp(v.__self__, depth + 1, active))
        if isinstance(v, functools.partial):
            return ('partial', self.fp(v.func, depth + 1, active), self.fp(v.args, depth + 1, active),
                    self.fp(v.keywords, depth + 1, active))
        if isinstance(v, type):
            mod = getattr(v, '__module__', None)
            if mod == 'builtins':
                return ('type', v.__qualname__)
            if mod in ('__main__', '__mp_main__') or mod in {m.__name__ for m in self.mods}:
                raise FxUnsupported('a class of the suite or the scorer (%s)' % v.__qualname__)
            return ('cls', mod, v.__qualname__)
        raise FxUnsupported('a value of type %s' % t.__name__)

    @staticmethod
    def _cell(c):
        try:
            return c.cell_contents
        except ValueError:
            return _MISSING

    def _code_fp(self, co):
        consts = tuple(self._code_fp(c) if isinstance(c, types.CodeType) else repr(c) for c in co.co_consts)
        return ('code', co.co_filename, getattr(co, 'co_qualname', co.co_name), co.co_firstlineno,
                hashlib.sha256(co.co_code).hexdigest()[:24], consts, co.co_names)

    def global_names(self, fn, a, k):
        """Every name the generator's code (and the suite functions / lambdas it can reach through its arguments,
        closures and the suite's globals) can look up: a superset of the suite globals it reads."""
        names, seen_code, seen_obj = set(), set(), set()
        todo = [fn, a, k]

        def add_code(co):
            if id(co) in seen_code:
                return
            seen_code.add(id(co))
            names.update(self._code_globals(co))
            for c in co.co_consts:
                if isinstance(c, types.CodeType):
                    add_code(c)
        while todo:
            v = todo.pop()
            if id(v) in seen_obj or len(seen_obj) > 200000:
                continue
            seen_obj.add(id(v))
            if isinstance(v, types.FunctionType):
                if v.__globals__ is self.g:
                    add_code(v.__code__)
                    todo.extend(self._cell(c) for c in (v.__closure__ or ()))
                    todo.extend(v.__defaults__ or ())
                    todo.extend((v.__kwdefaults__ or {}).values())
                w = getattr(v, '_mutlib_fx_wrapped', None)
                if w is not None:
                    todo.append(w)
            elif isinstance(v, functools.partial):
                todo.extend([v.func, v.args, v.keywords])
            elif isinstance(v, types.MethodType):
                todo.extend([v.__func__, v.__self__])
            elif isinstance(v, (tuple, list, set, frozenset)):
                todo.extend(v)
            elif isinstance(v, dict):
                todo.extend(v.keys())
                todo.extend(v.values())
            if not todo:
                for n in sorted(names):
                    gv = self.g.get(n, _MISSING)
                    if isinstance(gv, (types.FunctionType, functools.partial)) and id(gv) not in seen_obj:
                        todo.append(gv)
        refl = names & self._REFLECTION_NAMES
        attrs = set()
        for cid in seen_code:
            c = self.code_names.get(cid)
            if c is not None:
                attrs.update(c[0].co_names)
        refl |= attrs & self._REFLECTION_ATTRS
        if refl:
            raise FxUnsupported('it can reach the suite globals by reflection (%s)' % sorted(refl))
        return tuple(sorted(names))

    _REFLECTION_NAMES = frozenset({'globals', 'vars', 'locals', 'eval', 'exec', '__import__', 'compile', 'breakpoint'})
    _REFLECTION_ATTRS = frozenset({'__globals__', 'f_globals', 'f_locals', 'f_back', '_getframe', 'currentframe',
                                   'stack', 'getframeinfo', '__dict__', 'modules', '__builtins__'})

    _GLOBAL_OPS = frozenset({'LOAD_GLOBAL', 'LOAD_NAME', 'STORE_GLOBAL', 'DELETE_GLOBAL', 'STORE_NAME', 'DELETE_NAME',
                             'LOAD_FROM_DICT_OR_GLOBALS'})

    def _code_globals(self, co):
        """The global names a code object's bytecode looks up (not its attribute names); co_names if dis fails."""
        c = self.code_names.get(id(co))
        if c is None or c[0] is not co:
            try:
                import dis
                names = frozenset(ins.argval for ins in dis.get_instructions(co)
                                  if ins.opname in self._GLOBAL_OPS and isinstance(ins.argval, str))
            except Exception:
                names = frozenset(co.co_names)
            c = self.code_names[id(co)] = (co, names)
        return c[1]

    def globals_fp(self, names):
        return tuple((n, self.fp(self.g[n]) if n in self.g else 'ABSENT') for n in names)

    def env_fp(self):
        """The process state a generator can depend on beyond its own inputs: the environment, cwd, argv, sys.path,
        where printing goes, the locale, the decimal context."""
        env = tuple(sorted((self.norm_s(a), self.norm_s(b)) for a, b in os.environ.items()))
        streams = (sys.stdout is self.rt.out.f if self.rt.out else None,
                   sys.stderr is self.rt.err.f if self.rt.err else None)
        try:
            import locale as _locale
            loc = _locale.setlocale(_locale.LC_ALL)
        except Exception:
            loc = '?'
        dec = repr(sys.modules['decimal'].getcontext()) if 'decimal' in sys.modules else None
        return hashlib.sha256(repr((env, self.norm_s(os.getcwd()), self.fp(list(sys.argv)),
                                    self.fp(list(sys.path)), streams, loc, dec)).encode(
            'utf-8', 'surrogatepass')).hexdigest()

    @staticmethod
    def rand_fp():
        return hashlib.sha256(repr(random.getstate()).encode()).hexdigest()

    # ---- the fixture directory -------------------------------------------------------------------------------------
    def _mark_dirty(self, p):
        """v4.1 (review5 MINOR-5): a file opened for writing or changed is hashed again at the next walk whatever its
        size, time and inode say (an in-place rewrite of the same size within one file-time tick keeps all of them);
        by its path and by its inode (its hard links)."""
        if p is None or isinstance(p, int):
            return
        try:
            np = os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(p))))
        except (TypeError, ValueError):
            return
        self.wgen += 1
        self.dirty_np[np] = self.wgen
        try:
            st = os.stat(p)
            self.dirty_ino[(st.st_ino, st.st_dev)] = self.wgen
        except (OSError, TypeError, ValueError):
            pass

    def _dirty_since(self, path, st, gen):
        if not self.dirty_np and not self.dirty_ino:
            return False
        if self.dirty_ino.get((st.st_ino, st.st_dev), 0) > gen:
            return True
        try:
            return self.dirty_np.get(os.path.normcase(os.path.abspath(path)), 0) > gen
        except (TypeError, ValueError):
            return True

    def content_id(self, rel, path, st):
        key = (st.st_size, st.st_mtime_ns, st.st_ino, st.st_dev)
        c = self.cache.get(rel)
        if c is not None and c[0] == key and not self._dirty_since(path, st, c[4]):
            return c[1], c[2], c[3]
        cid = self.store_inodes.get((st.st_ino, st.st_dev)) if self.mode == 'replay' else None
        if cid is not None:
            templ, nl = False, None
        else:
            with open(path, 'rb') as fh:
                data = fh.read()
            templ = any(f in data for _, f in self.bforms)
            cid = hashlib.sha256(self.norm_b(data) if templ else data).hexdigest()
            nl = data.count(b'\n')
        self.cache[rel] = (key, cid, templ, nl, self.wgen)
        return cid, templ, nl

    def walk(self):
        """{relative path: ('d',) | ('f', size, content id, carries the job path)} of the fixture directory."""
        out = {}
        if not os.path.isdir(self.base):
            return out
        stack = ['']
        while stack:
            rel = stack.pop()
            d = os.path.join(self.base, *rel.split('/')) if rel else self.base
            with os.scandir(d) as it:
                entries = list(it)
            for e in entries:
                r = (rel + '/' + e.name) if rel else e.name
                if e.is_symlink() or (hasattr(e, 'is_junction') and e.is_junction()):
                    raise FxUnsupported('a link / junction in the fixture directory: %s' % r)
                if e.is_dir():
                    out[r] = ('d',)
                    stack.append(r)
                else:
                    st = os.stat(e.path)
                    cid, templ, _ = self.content_id(r, e.path, st)
                    out[r] = ('f', st.st_size, cid, templ)
        return out

    @staticmethod
    def digest_of(snap):
        items = sorted((r, e[0], e[1] if e[0] == 'f' else 0, e[2] if e[0] == 'f' else '') for r, e in snap.items())
        return hashlib.sha256(repr(items).encode('utf-8', 'surrogatepass')).hexdigest()

    def _watch_now(self):
        out = {}
        for np in self.watch:
            try:
                st = os.stat(np)
                out[np] = (st.st_size, st.st_mtime_ns)
            except OSError:
                out[np] = None
        return out

    def current_digest(self):
        """The fixture directory's digest; walked again unless nothing can have changed it since the last walk or
        replay (no write event since, and every file ever opened for writing in the job is as it was then)."""
        if self.clean and self._watch_now() != self.watch_state:
            self.clean = False
        if not self.clean:
            snap = self.walk()
            self.digest = self.digest_of(snap)
            self.clean = True
            self.stats['walks'] += 1
            self.watch_state = self._watch_now()
        return self.digest

    def cap_sizes(self):
        out = []
        for s in (self.rt.out, self.rt.err):
            try:
                s.flush(sys.stdout if s is self.rt.out else sys.stderr)
                out.append(os.path.getsize(s.path))
            except OSError:
                out.append(None)
        return tuple(out)

    # ---- the generator wrapper -------------------------------------------------------------------------------------
    def wrap(self, fn, name):
        fx = self

        @functools.wraps(fn)
        def fixture_generator(*a, **k):
            return fx.call(fn, name, a, k)
        fixture_generator._mutlib_fx_wrapped = fn
        return fixture_generator

    def wrap_case(self, fn):
        fx = self

        @functools.wraps(fn)
        def case_registration(*a, **k):
            if fx.depth == 0:
                nm = a[0] if a and isinstance(a[0], str) else k.get('name')
                fx.cases.append((time.perf_counter() - fx.rt.t0, nm if isinstance(nm, str) else '?', fx.seq))
            return fn(*a, **k)
        case_registration._mutlib_fx_wrapped = fn
        return case_registration

    def call(self, fn, name, a, k):
        if self.depth or not self.rt.in_job:
            return self._real(fn, a, k)
        if self.touched is not None:
            raise FxTouched(self.touched)
        i = self.seq
        self.seq += 1
        if self.mode == 'record':
            return self._record(fn, name, i, a, k)
        return self._replay(fn, name, i, a, k)

    def _real(self, fn, a, k):
        self.depth += 1
        try:
            return fn(*a, **k)
        finally:
            self.depth -= 1

    # ---- recording (R1 / R2 / the profile) -----------------------------------------------------------------------
    def _record(self, fn, name, i, a, k):
        self.per_fn[name] += 1
        rec = {'i': i, 'fn': name, 'ok': False, 'why': None, 't': round(time.perf_counter() - self.rt.t0, 4)}
        if self.per_fn[name] > FX_MAX_CALLS_PER_FN:
            rec['why'] = 'more than %d calls of %s' % (FX_MAX_CALLS_PER_FN, name)
            self.records.append(rec)
            self.clean = False
            return self._real(fn, a, k)
        t_in = time.perf_counter()
        pre = None
        with _Suppress():
            try:
                if self.failed:
                    raise FxUnsupported(self.failed)
                pre_args = self.fp((a, k))
                gnames = self.global_names(fn, a, k)
                pre_glob = self.globals_fp(gnames)
                env, rand = self.env_fp(), self.rand_fp()
                pre_snap = self.walk()
                pre = (pre_args, gnames, pre_glob, env, rand, pre_snap, self.digest_of(pre_snap),
                       self.cap_sizes(), threading.active_count(), self._mods_snapshot())
            except FxUnsupported as e:
                rec['why'] = 'input: %s' % e
            except OSError as e:
                rec['why'] = 'input: %s' % exc_line(e)
        cur = self.cur = {'reads': [], 'bad': []}
        self.track, self.track_write = set(), False
        self.depth += 1
        t0 = time.perf_counter()
        raised = True
        try:
            ret = fn(*a, **k)
            raised = False
        finally:
            dur = time.perf_counter() - t0
            self.depth -= 1
            track, self.track = self.track, None
            self.cur = None
            self.clean = False
            rec['dur'] = round(dur, 4)
            if raised:
                rec['why'] = rec['why'] or 'it raised'
                self.records.append(rec)
        if rec['why'] is None:
            with _Suppress():
                try:
                    rec.update(self._finish(fn, a, k, pre, ret, track, cur))
                    rec['ok'] = True
                except FxUnsupported as e:
                    rec['why'] = str(e)
                except OSError as e:
                    rec['why'] = 'effects: %s' % exc_line(e)
        if self.spec.get('profile') and 'bytes' not in rec and pre is not None:
            with _Suppress():                               # the profile wants the sizes even of unreplayable calls
                try:
                    post = self.walk()
                    new = [r for r, e in post.items() if e[0] == 'f' and pre[5].get(r) != e]
                    rec['bytes'] = sum(post[r][1] for r in new)
                    rec['rows'] = sum(self.cache.get(r, (0, 0, 0, 0))[3] or 0 for r in new)
                    rec['files'] = len(new)
                except (OSError, FxUnsupported):
                    pass
        rec['overhead'] = round(time.perf_counter() - t_in - dur, 4)
        self.records.append(rec)
        return ret

    def _returns_given(self, ret, a, k, gnames):
        """Does the return value hold (by identity) a tuple / frozenset / path / pattern that is also reachable from the
        arguments or the suite globals the generator reads?  Then `ret is X` could tell a replay's copy apart."""
        mark = (tuple, frozenset, PurePath, re.Pattern)
        known, stack, n = set(), [a, k] + [self.g.get(x) for x in gnames], 0
        while stack and n < 200000:
            v = stack.pop()
            n += 1
            if isinstance(v, mark):
                if id(v) in known:
                    continue
                known.add(id(v))
            if isinstance(v, (tuple, list, set, frozenset)):
                stack.extend(v)
            elif isinstance(v, dict):
                stack.extend(v.values())
        stack = [ret]
        while stack:
            v = stack.pop()
            if isinstance(v, mark) and id(v) in known and not (isinstance(v, tuple) and not v):
                return True
            if isinstance(v, (tuple, frozenset)):
                stack.extend(v)
        return False

    def _mods_snapshot(self):
        """fingerprints of the scorer modules' data attributes before a recorded call (functions, classes and
        modules are not data; a value without a fingerprint is marked)."""
        out = {}
        for mi, m in enumerate(self.mods):
            saved, self.track = self.track, None
            try:
                items = list(types.ModuleType.__getattribute__(m, '__dict__').items())
            finally:
                self.track = saved
            for n, v in items:
                if isinstance(v, (types.FunctionType, types.ModuleType, type)) or n.startswith('__'):
                    continue
                try:
                    out[(mi, n)] = self.fp(v)
                except FxUnsupported as e:
                    out[(mi, n)] = ('UNSUPPORTED', str(e))
        return out

    def _finish(self, fn, a, k, pre, ret, track, cur):
        pre_args, gnames, pre_glob, env, rand, pre_snap, pre_d, caps, threads, pre_mods = pre
        if self.track_write:
            raise FxUnsupported('it set an attribute of the scorer module')
        if cur['bad']:
            raise FxUnsupported(cur['bad'][0])
        if self.fp((a, k)) != pre_args:
            raise FxUnsupported('it changed its arguments')
        if self.globals_fp(gnames) != pre_glob:
            raise FxUnsupported('it changed a suite global it can reach')
        if self.env_fp() != env:
            raise FxUnsupported('it changed the environment / cwd / argv / sys.path')
        if self.rand_fp() != rand:
            raise FxUnsupported('it used the global random state')
        if self.cap_sizes() != caps:
            raise FxUnsupported('it printed')
        if threading.active_count() != threads:
            raise FxUnsupported('it started or ended a thread')
        if not _fx_immutable(ret):
            raise FxUnsupported('it returns a %s (only immutable values are replayed)' % type(ret).__name__)
        if self._returns_given(ret, a, k, gnames):
            raise FxUnsupported('it returns an object it was given or a suite global (a replay would return a copy)')
        mods = tuple((mi, n, self.fp(self.mod_value(mi, n))) for mi, n in sorted(track))
        for mi, n, post in mods:
            if (mi, n) in pre_mods and pre_mods[(mi, n)] != post:
                raise FxUnsupported('it changed the scorer value %s' % n)
        reads = []
        for np in sorted(set(cur['reads'])):
            if self.under_base(np):
                continue                                    # covered by the directory state
            if np == self.mutant_norm:
                raise FxUnsupported('it read the scorer file')
            try:
                with open(np, 'rb') as fh:
                    data = fh.read()
                reads.append((self.norm_s(np), hashlib.sha256(self.norm_b(data)).hexdigest()))
            except OSError:
                reads.append((self.norm_s(np), None))
        post = self.walk()
        effects = []
        for rel in sorted(pre_snap, key=lambda r: (-r.count('/'), r)):
            e0, e1 = pre_snap[rel], post.get(rel)
            if e1 is None or e1[0] != e0[0] or (e0[0] == 'f' and e0[2] != e1[2]):
                effects.append(('rmfile' if e0[0] == 'f' else 'rmdir', rel))
        created = [r for r in post if r not in pre_snap or post[r][0] != pre_snap[r][0]
                   or (post[r][0] == 'f' and post[r][2] != pre_snap[r][2])]
        for rel in sorted((r for r in created if post[r][0] == 'd'), key=lambda r: (r.count('/'), r)):
            effects.append(('mkdir', rel))
        nbytes = nrows = 0
        for rel in sorted(r for r in created if post[r][0] == 'f'):
            _, size, cid, templ = post[rel]
            path = os.path.join(self.base, *rel.split('/'))
            nl = self.cache.get(rel, (None, None, None, None))[3]
            nbytes += size
            nrows += nl or 0
            if templ:
                if size > FX_MAX_TEMPLATE:
                    raise FxUnsupported('%s carries the job path and is larger than %d bytes' % (rel, FX_MAX_TEMPLATE))
                with open(path, 'rb') as fh:
                    effects.append(('write', rel, cid, self.norm_b(fh.read())))
            else:
                effects.append(('link', rel, cid, size))
                self.produced[self.npath(path)] = rel
                if self.store:
                    # a COPY, not a link: the baseline may change its own file later, and jobs may already link the
                    # store (the store is made read-only while the baselines still run their final loop)
                    dst = os.path.join(self.store, cid)
                    if not os.path.exists(dst):
                        tmp = dst + '.tmp%d' % os.getpid()
                        shutil.copyfile(path, tmp)
                        os.replace(tmp, dst)
        ret_norm = self.transform(ret, self.norm_s, self.norm_b)
        return {'args': pre_args, 'gnames': gnames, 'glob': pre_glob, 'env': env, 'rand': rand, 'mods': mods,
                'reads': tuple(reads), 'pre': pre_d, 'post': self.digest_of(post), 'effects': effects,
                'ret': pickle.dumps(ret_norm, protocol=4), 'ret_fp': self.fp(ret), 'bytes': nbytes, 'rows': nrows,
                'files': sum(1 for e in effects if e[0] in ('link', 'write'))}

    _PATH_MARK = '\x00MUTLIBPATH\x00'

    def transform(self, v, fs, fb, depth=0):
        """A copy of an immutable value with every string / bytes passed through fs / fb (a path is carried as a
        marked tuple, so no Path object ever holds a placeholder)."""
        if depth > 30:
            raise FxUnsupported('a return value nested too deeply')
        t = type(v)
        if t is str:
            return fs(v)
        if t is bytes:
            return fb(v)
        if isinstance(v, PurePath):
            if t.__module__ != 'pathlib' and not t.__module__.startswith('pathlib.'):
                raise FxUnsupported('a return value of type %s' % t.__name__)
            return (self._PATH_MARK, t.__name__, fs(str(v)))
        if isinstance(v, re.Pattern):
            p = v.pattern
            return re.compile(fs(p) if isinstance(p, str) else fb(p), v.flags)
        if t is tuple:
            if len(v) == 3 and v[0] == self._PATH_MARK and isinstance(v[2], str):
                import pathlib
                return getattr(pathlib, v[1])(fs(v[2]))
            return tuple(self.transform(x, fs, fb, depth + 1) for x in v)
        if t is frozenset:
            return frozenset(self.transform(x, fs, fb, depth + 1) for x in v)
        if v is None or t in (bool, int, float, complex, range):
            return v
        raise FxUnsupported('a return value of type %s' % t.__name__)

    # ---- replay (every other job) --------------------------------------------------------------------------------
    def _miss(self, i, why):
        self.stats['real'] += 1
        if self.first_miss is None:
            self.first_miss = (i, why)

    def _replay(self, fn, name, i, a, k):
        rec = self.recs.get(i)
        if rec is None or rec['fn'] != name:
            self._miss(i, 'no validated record for call %d (%s)' % (i, name))
            self.clean = False
            return self._real(fn, a, k)
        if i in self.noop:
            self.stats['noop'] += 1
            return self._real(fn, a, k)
        with _Suppress():
            why = self._check(rec, fn, a, k)
        if why:
            self._miss(i, why)
            self.clean = False
            return self._real(fn, a, k)
        with _Suppress():
            try:
                self._apply(rec)
            except (OSError, FxUnsupported) as e:
                self.touched = 'replay could not apply call %d (%s): %s' % (i, name, exc_line(e))
                raise FxTouched(self.touched)
        self.stats['replayed'] += 1
        self.stats['saved_s'] += rec.get('dur', 0.0)
        return self.transform(pickle.loads(rec['ret']), self.denorm_s, self.denorm_b)

    def _check(self, rec, fn, a, k):
        try:
            if self.failed:
                return self.failed
            if self.fp((a, k)) != rec['args']:
                return 'call %d: other arguments' % rec['i']
            if self.globals_fp(rec['gnames']) != rec['glob']:
                return 'call %d: a suite global differs' % rec['i']
            for mi, n, want in rec['mods']:
                if self.fp(self.mod_value(mi, n)) != want:
                    return 'call %d: the scorer attribute %s differs' % (rec['i'], n)
            if self.env_fp() != rec['env']:
                return 'call %d: the environment differs' % rec['i']
            for np, sha in rec['reads']:
                p = self.denorm_s(np)
                try:
                    with open(p, 'rb') as fh:
                        now = hashlib.sha256(self.norm_b(fh.read())).hexdigest()
                except OSError:
                    now = None
                if now != sha:
                    return 'call %d: the file %s it reads differs' % (rec['i'], p)
            if self.current_digest() != rec['pre']:
                return 'call %d: the fixture directory differs' % rec['i']
        except FxUnsupported as e:
            return 'call %d: %s' % (rec['i'], e)
        return None

    def _apply(self, rec):
        for eff in rec['effects']:
            kind, rel = eff[0], eff[1]
            p = os.path.join(self.base, *rel.split('/'))
            if kind == 'rmfile':
                _unlink_ro(p)
            elif kind == 'rmdir':
                os.rmdir(p)
            elif kind == 'mkdir':
                os.mkdir(p)
            elif kind == 'link':
                src = os.path.join(self.spec['store'], eff[2])
                try:
                    if os.stat(src).st_nlink >= FX_LINK_LIMIT:
                        raise OSError('the store file has %d links' % os.stat(src).st_nlink)
                    os.link(src, p)
                    self.stats['linked'] += 1
                except OSError:                             # NTFS allows 1023 names per file: a private copy
                    shutil.copyfile(src, p)
                    self.stats['copied'] += 1
            elif kind == 'copy':                            # the suite changes this file later: a private copy
                shutil.copyfile(os.path.join(self.spec['store'], eff[2]), p)
                self.stats['copied'] += 1
            elif kind == 'write':
                with open(p, 'wb') as fh:
                    fh.write(self.denorm_b(eff[3]))
                self.stats['written'] += 1
            else:
                raise FxUnsupported('unknown effect %r' % kind)
        self.digest = rec['post']
        self.clean = True
        self.watch_state = self._watch_now()

    # ---- the audit hook ------------------------------------------------------------------------------------------
    def _store_file(self, p, follow=True):
        if not self.store_inodes:
            return False
        try:
            st = os.stat(p) if follow else os.lstat(p)
        except (OSError, TypeError, ValueError):
            return False
        return (st.st_ino, st.st_dev) in self.store_inodes

    def _touch(self, event, p):
        self.touched = '%s %s' % (event, p)
        raise FxTouched(self.touched)

    def _note_later(self, event, args):
        """record mode: a change of a file an earlier recorded call produced (replayed as a writable copy)."""
        if event == 'open':
            path, mode, flags = (tuple(args) + (None, None, None))[:3]
            if mode is not None:
                writing = bool(set(str(mode)) & set('wax+'))
            else:
                writing = bool((flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))
            paths = [path] if writing else []
        elif event in _WRITE_1 or event in _WRITE_BOTH or event in _WRITE_DST or event in _MMAP:
            paths = list(args[:2]) if event in _WRITE_BOTH or event in _WRITE_DST else list(args[:1])
            if event == 'os.link':
                paths = []
        else:
            paths = []
        for p in paths:
            np = self.npath(p) if not isinstance(p, int) else None
            if np is not None and np in self.produced:
                self.later_touched.add(self.produced[np])

    def on_audit(self, event, args):
        rec = self.cur is not None and self.depth > 0 and self.mode == 'record'
        if self.mode == 'record' and self.produced:
            self._note_later(event, args)
        if event == 'open':
            path, mode, flags = (tuple(args) + (None, None, None))[:3]
            if path is None or isinstance(path, int):
                return
            if mode is not None:
                writing = bool(set(str(mode)) & set('wax+'))
            else:
                writing = bool((flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))
            np = self.npath(path)
            if not writing:
                if rec and np is not None:
                    self.cur['reads'].append(np)
                if self.mode == 'replay' and self.store_inodes and self.under_J(np):
                    try:                                    # a shared file the job reads: re-hashed at its end
                        st = os.stat(path)
                        cid = self.store_inodes.get((st.st_ino, st.st_dev))
                        if cid is not None:
                            self.read_cids.add(cid)
                    except (OSError, TypeError, ValueError):
                        pass
                return
            self.clean = False
            self._mark_dirty(path)
            if self.under_J(np):
                self.watch.add(np)
            if rec and not self.under_base(np):
                self.cur['bad'].append('it writes outside the fixture directory: %s' % np)
            if self.mode == 'replay' and self._store_file(path):
                self._touch(event, path)
            return
        if event in _LISTING:
            if rec:
                np = self.npath(args[0] if args else None)
                if np is None or not self.under_base(np):
                    self.cur['bad'].append('it lists a directory outside the fixture directory: %s' % np)
            return
        if event in _SPAWN:
            if rec:
                self.cur['bad'].append('it starts a process')
            return
        if event in _MMAP:
            if rec:
                self.cur['bad'].append('it maps a file')
            if self.mode == 'replay' and self.store_inodes:
                try:
                    fd, access = args[0], args[2]
                    st = os.fstat(fd) if isinstance(fd, int) and fd >= 0 else None
                except (OSError, IndexError, TypeError):
                    st = None
                if st is not None and (st.st_ino, st.st_dev) in self.store_inodes and access != 1:
                    self._touch(event, 'fd %s' % args[0])
            return
        if event in _WRITE_1 or event in _WRITE_BOTH or event in _WRITE_DST:
            self.clean = False
            paths = list(args[:2]) if event in _WRITE_BOTH or event in _WRITE_DST else list(args[:1])
            for p in (paths if event in _WRITE_1 or event in _WRITE_BOTH else paths[1:]):
                self._mark_dirty(p)
            if rec:
                for p in paths:
                    np = self.npath(p)
                    if np is not None and not self.under_base(np) and not (event in _WRITE_DST and p is paths[0]):
                        self.cur['bad'].append('it changes a path outside the fixture directory: %s %s' % (event, np))
            if self.mode != 'replay' or not self.store_inodes:
                return
            if event == 'os.link':                          # a new name for a shared file: fine, it stays read-only,
                src = paths[0] if paths else None           # unless the file is near NTFS's 1023 names (the link
                try:                                        # would fail where the original's private file would not)
                    if src is not None and not isinstance(src, int) and self._store_file(src) \
                            and os.stat(src).st_nlink >= FX_LINK_LIMIT:
                        self._touch('os.link (the shared file has %d names)' % os.stat(src).st_nlink, src)
                except OSError:
                    pass
                return
            if event in ('shutil.copyfile', 'shutil.copytree', 'os.rename', 'shutil.move'):
                check = paths[1:]                           # overwriting a shared file (renaming one is harmless)
            elif event in ('shutil.copymode', 'shutil.copystat', 'os.symlink'):
                check = paths                               # the read-only mode would spread / a writable alias
            else:
                check = paths
            for p in check:
                follow = event not in ('os.remove', 'os.rmdir', 'os.rename', 'shutil.move', 'os.lchmod', 'os.lchown',
                                       'os.lchflags')
                if p is not None and not isinstance(p, int) and self._store_file(p, follow):
                    self._touch(event, p)

    def dump(self, path, extra=None):
        """The recording so far, written atomically (the phase-G dump before the final loop, and the job's end).  A
        recorded file that the suite changed, removed or renamed LATER is replayed as a private writable copy
        ('copy'), not a read-only link (every job would do the same and touch the shared file)."""
        records = []
        for rec in self.records:
            if rec.get('ok') and any(e[0] == 'link' and e[1] in self.later_touched for e in rec['effects']):
                rec = dict(rec, effects=[('copy',) + tuple(e[1:]) if e[0] == 'link' and e[1] in self.later_touched
                                         else e for e in rec['effects']])
            records.append(rec)
        data = {'J': self.J, 'records': records, 'cases': list(self.cases), 'modules': len(self.mods)}
        data.update(extra or {})
        tmp = path + '.%d.tmp' % os.getpid()
        with open(tmp, 'wb') as fh:
            pickle.dump(data, fh, protocol=4)
        os.replace(tmp, path)

    def verify_reads(self):
        """After the job: every shared file it read still has the content its name says (its sha256); a mismatch
        cannot be traced to one job and makes the run NOT CERTIFIED."""
        bad = []
        for cid in sorted(self.read_cids):
            h = hashlib.sha256()
            try:
                with open(os.path.join(self.spec['store'], cid), 'rb') as fh:
                    for chunk in iter(lambda: fh.read(1 << 22), b''):
                        h.update(chunk)
            except OSError:
                bad.append(cid[:12] + ' (unreadable)')
                continue
            if h.hexdigest() != cid:
                bad.append(cid[:12])
        return bad

    def result(self):
        return {'mode': self.mode, 'calls': self.seq, 'replayed': self.stats['replayed'], 'real': self.stats['real'],
                'noop': self.stats['noop'], 'walks': self.stats['walks'], 'linked': self.stats['linked'],
                'written': self.stats['written'], 'copied': self.stats['copied'],
                'saved_s': round(self.stats['saved_s'], 2),
                'first_miss': self.first_miss, 'touched': self.touched, 'failed': self.failed,
                'modules': len(self.mods)}


def _fx_touch_shim():
    """Interpreters whose os functions raise no audit events (PyPy): raise them from Python, so the write audit and
    the shared-fixture guard see os.remove / rename / link / chmod / ... as CPython's C functions report them."""
    if sys.implementation.name == 'cpython' or getattr(os, '_mutlib_shimmed', False):
        return
    table = {'remove': ('os.remove', 1), 'unlink': ('os.remove', 1), 'rmdir': ('os.rmdir', 1),
             'mkdir': ('os.mkdir', 1), 'rename': ('os.rename', 2), 'replace': ('os.rename', 2),
             'link': ('os.link', 2), 'symlink': ('os.symlink', 2), 'chmod': ('os.chmod', 1),
             'utime': ('os.utime', 1), 'truncate': ('os.truncate', 1), 'listdir': ('os.listdir', 1),
             'scandir': ('os.scandir', 1)}
    for name, (event, n) in table.items():
        orig = getattr(os, name, None)
        if orig is None:
            continue

        def make(orig=orig, event=event, n=n):
            def shim(*a, **k):
                try:
                    sys.audit(event, *(list(a[:n]) + [None] * (n - len(a[:n]))))
                except AttributeError:
                    pass
                return orig(*a, **k)
            shim.__name__ = getattr(orig, '__name__', 'shim')
            return shim
        setattr(os, name, make())
    os._mutlib_shimmed = True


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
        # v4 (review4 MINOR-2): an early-exit kill is recorded BEFORE its exception is raised and re-raised at every
        # later hook; the job's verdict honours it even when the suite swallowed the exception
        self.early_kill = None
        self.t0 = time.perf_counter()
        self.guard_t = [] if self.want_probe else None       # the baseline's time at every guard (early-exit stats)
        self.guard_info = []                                    # (time, line, case label, orientation): the profile
        self.gi_pending = None
        self.t_end = None
        self.n_guards = 0
        self.fx = None                                          # v4 fixture replay (FxRuntime) or None

    def api(self):
        return {PFX + 'Path': Path, PFX + 'guard': self.guard, PFX + 'label': self.label, PFX + 'end': self.end,
                PFX + 'after': self.after, PFX + 'phase': self.phase}

    def phase(self):
        """v4: the N family's final loop starts here.  A recording baseline writes its generator calls so far, so the
        parent can validate them and start the mutants while the baselines run their checks."""
        fx = self.fx
        if fx is not None and fx.mode == 'record' and fx.spec.get('records_out') and fx.spec.get('phase_dump'):
            with _Suppress():
                try:
                    fx.dump(fx.spec['records_out'] + '.g', {'phase': 'G'})
                except OSError:
                    pass

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
        if self.gi_pending is not None:             # the profile: a guard whose case line follows it
            gi, self.gi_pending = self.gi_pending, None
            t, ln, _, orient = self.guard_info[gi]
            self.guard_info[gi] = (t, ln, line.split()[0] if line.split() else None, orient)
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
        """Ends the job at a failed guard whose case line has been printed since (fast mode); once a kill has been
        raised, every later hook raises it again (the suite may have swallowed it)."""
        if self.fx is not None and self.fx.touched:
            raise FxTouched(self.fx.touched)
        if self.kill is not None:
            k, self.kill = self.kill, None
            if self.early_kill is None:
                self.early_kill = k
            raise MutantKilled(*self.early_kill)
        if self.early_kill is not None:
            raise MutantKilled(*self.early_kill)

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
        if self.fx is not None and self.fx.touched:
            raise FxTouched(self.fx.touched)
        if self.early_kill is not None:
            raise MutantKilled(*self.early_kill)
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
        if self.guard_t is not None:
            self.guard_t.append(round(time.perf_counter() - self.t0, 4))
            tok = since[-1].split()[0] if since and since[-1].split() else None
            self.guard_info.append((self.guard_t[-1], lineno, label if isinstance(label, str) else tok, orient))
            if not isinstance(label, str) and orient == 'after':
                self.gi_pending = len(self.guard_info) - 1
        self.n_guards += 1
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
        self.failures.append([label, lineno, exact, self.n_guards - 1])
        stop = self.fast and raise_ok and exact
        if label is None:
            self.pending = (len(self.failures) - 1, stop)
            return value
        if stop:
            self.early_kill = (label, lineno)
            raise MutantKilled(label, lineno)
        return value

    def end(self, value, probe=None):
        self.drain()
        self._raise_kill()
        self.reached_end = True
        self.t_end = round(time.perf_counter() - self.t0, 4)
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
        if self.fx is not None:
            self.fx.on_audit(event, args)                 # v4: may raise FxTouched (aborts the operation)


def _audit_hook(event, args):
    rt = _RT
    if rt is None or not rt.in_job or rt.suppress or event not in _AUDITED:
        return
    try:
        rt.on_audit(event, args)
    except Exception:
        pass


def _copyfile2_shim():
    """v4.1 (review5 MAJOR-2): CPython 3.12+ on Windows copies shutil.copy2 / copytree / move through
    _winapi.CopyFile2, which raises no audit event.  In a job it raises the events shutil.copyfile + shutil.copystat
    raise, so the write audit (outside writers) and the shared-fixture guard (a copy of a shared file) see it."""
    try:
        import _winapi
    except ImportError:
        return
    orig = getattr(_winapi, 'CopyFile2', None)
    if orig is None or getattr(orig, '_mutlib_shim', False):
        return

    def CopyFile2(src, dst, *rest, **kw):
        sys.audit('shutil.copyfile', src, dst)
        sys.audit('shutil.copystat', src, dst)
        return orig(src, dst, *rest, **kw)
    CopyFile2._mutlib_shim = True
    try:
        _winapi.CopyFile2 = CopyFile2
    except (AttributeError, TypeError):
        pass


def _install_worker_hooks(rt, memo, src):
    _fx_touch_shim()                                    # v4: os audit events on interpreters that raise none (PyPy)
    _copyfile2_shim()                                   # v4.1: copies through _winapi.CopyFile2 (review5 MAJOR-2)
    sys.addaudithook(_audit_hook)
    if memo is None and rt.fx is None:
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
                    if memo is not None:
                        try:
                            memo.install(module, src)
                        except Exception as e:
                            memo._off('install failed: %s' % exc_line(e))
                    if rt.fx is not None:
                        rt.fx.register_module(module)
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
    fxspec = job.get('fx')
    want_fx = fxspec is not None
    want_case = bool(fxspec and fxspec.get('profile'))
    if cfg.get('foreign'):
        # v4 --python: another interpreter cannot load CPython's marshalled code; the same transformation runs here
        code = TestPlan(test_path, cfg['test_src'], cfg['okname']).code_for(want_fx, want_case)
    else:
        key = 'test_code' + ('_fx' if want_fx else '') + ('_case' if want_case else '')
        code = marshal.loads(cfg[key])              # the suite transformed and compiled ONCE by the parent
    memo = Memo(cfg['cache'], cfg['scorer_src'], cfg['memo_mem']) if job['memo'] else None
    rt = _RT = Runtime(job, cfg, job_dir, mutant_path)
    try:
        (job_dir / 'cap').mkdir()
        rt.out = _Stream(job_dir / 'cap' / 'stdout.txt', False)
        rt.err = _Stream(job_dir / 'cap' / 'stderr.txt', True)
    except OSError as e:
        return {'outcome': 'env_error', 'crash': 'cannot open the job output files: %s' % exc_line(e)}
    if want_fx:
        try:
            rt.fx = FxRuntime(rt, fxspec, job_dir, fx, mutant_path)
        except (OSError, pickle.UnpicklingError, KeyError) as e:
            return {'outcome': 'env_error', 'crash': 'cannot load the fixture replay plan: %s' % exc_line(e)}
    _install_worker_hooks(rt, memo, job['src'])
    g = {'__name__': '__main__', '__file__': str(test_path), '__builtins__': builtins, '__doc__': None,
         '__package__': None, '__spec__': None, '__loader__': None, PFX + 'FX': str(fx)}
    g.update(rt.api())
    if rt.fx is not None:
        rt.fx.g = g
        g[PFX + 'fx'] = rt.fx.wrap
        g[PFX + 'case'] = rt.fx.wrap_case
    argv = [str(test_path), str(mutant_path)] + ([str(fx)] if cfg['uses_argv2'] else [])
    # ---- the recursion limit (review3 MINOR 5): `python test.py` runs the suite's module frame at depth 1; here it
    # sits on top of this process's own frames.  Raise the limit by those frames plus a margin for harness frames
    # that can sit above a scorer frame (the audit hook, the memo wrapper), and keep sys.getrecursionlimit() /
    # sys.setrecursionlimit() as the suite would see them.
    below, f = 0, sys._getframe()
    while f is not None:
        below, f = below + 1, f.f_back
    offset = below + (RECURSION_MARGIN_MEMO if memo is not None else RECURSION_MARGIN) \
        + (RECURSION_MARGIN_REPLAY if rt.fx is not None else 0)
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
    elif rt.fx is not None and rt.fx.touched:
        # v4: the job tried to change a shared fixture file (the operation was refused): its result is not a verdict;
        # the parent reruns it in a fully isolated fresh process
        res.update(outcome='fx_touched', crash=rt.fx.touched)
    elif rt.memo_violation:
        res.update(outcome='memo_violation', crash=rt.memo_violation)
    elif rt.early_kill is not None:
        # v4 (review4 MINOR-2): the early exit was raised at an exact failing guard; whatever the suite did with the
        # exception afterwards (an `except BaseException` that swallowed it, a later exit 0), ok stayed falsy and the
        # original suite exits non-zero: the recorded kill is the verdict
        if res.get('outcome') != 'killed' or (res.get('label'), res.get('lineno')) != tuple(rt.early_kill):
            res['swallowed'] = '%s%s' % (res.get('outcome'), (' %s' % res.get('exit_code'))
                                         if res.get('outcome') == 'exit' else '')
        res.update(outcome='killed', label=rt.early_kill[0], lineno=rt.early_kill[1])
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
    res['n_guards'] = rt.n_guards
    res['guard_t'] = rt.guard_t
    res['t_end'] = rt.t_end
    res['kill_guard'] = exact[0][3] if exact and res.get('outcome') == 'killed' else None
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
    if rt.fx is not None:
        res['fx'] = rt.fx.result()
        if rt.fx.mode == 'replay':
            with _Suppress():
                res['fx']['read_shared'] = len(rt.fx.read_cids)
                res['fx']['store_mismatch'] = rt.fx.verify_reads()
        if rt.fx.mode == 'record' and fxspec.get('records_out'):
            try:
                rt.fx.dump(fxspec['records_out'], {'guards': rt.guard_info, 't_end': rt.t_end,
                                                   'names': list(cfg.get('fx_names') or ())})
            except OSError as e:
                res['fx']['failed'] = 'cannot write the records: %s' % exc_line(e)
    return res


def _job_main(spec_path, res_path):
    """v4 --python: a job run by another interpreter (`INTERPRETER mutlib.py --_job SPEC RESULT`); the spec and the
    result are pickle files (protocol 4), the result is written atomically; the process exits with os._exit."""
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except (ValueError, OSError):
        pass
    t0 = time.perf_counter()
    job = {'name': '?', 'kind': '?', 'memo': False}
    try:
        with open(spec_path, 'rb') as fh:
            cfg, job = pickle.load(fh)
        res = _run_job(cfg, job)
    except BaseException as e:
        res = {'outcome': 'harness_error', 'crash': exc_line(e), 'trace': traceback.format_exc()[-3000:]}
    res.update(name=job['name'], kind=job['kind'], seconds=time.perf_counter() - t0, memo_on=bool(job['memo']))
    try:
        tmp = res_path + '.tmp'
        with open(tmp, 'wb') as fh:
            pickle.dump(res, fh, protocol=4)
        os.replace(tmp, res_path)
    except BaseException:
        pass
    os._exit(0)


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
    if o == 'fx_touched':
        return 'UNRESOLVED', 'UNRESOLVED (it touched the shared fixtures: %s)' % res.get('crash')
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


class _PopenProc:
    """v4 --python: a job process started with subprocess, seen through the multiprocessing.Process calls the
    scheduler makes."""

    def __init__(self, popen):
        self.p = popen

    @property
    def sentinel(self):
        h = getattr(self.p, '_handle', None)
        return int(h) if h is not None else None

    def is_alive(self):
        return self.p.poll() is None

    def join(self, timeout=None):
        try:
            self.p.wait(timeout)
        except Exception:
            pass

    def terminate(self):
        self.p.terminate()

    def kill(self):
        self.p.kill()

    @property
    def exitcode(self):
        return self.p.poll()


class _FileConn:
    """v4 --python: the job's result arrives as a pickle file (written atomically by _job_main)."""

    def __init__(self, res_path, spec_path):
        self.res, self.spec = res_path, spec_path

    def poll(self):
        return os.path.exists(self.res)

    def recv(self):
        with open(self.res, 'rb') as fh:
            return pickle.load(fh)

    def send(self, msg):
        pass

    def close(self):
        for p in (self.res, self.spec):
            try:
                os.unlink(p)
            except OSError:
                pass


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
                    _rmtree_force(d)                    # v4: shared fixtures are read-only hard links
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
        if self.cfg.get('python'):
            import subprocess
            sd = Path(self.cfg['work']) / '_spec'
            sd.mkdir(parents=True, exist_ok=True)
            sp, rp = str(sd / ('j%05d.pkl' % self.seq)), str(sd / ('j%05d.res.pkl' % self.seq))
            with open(sp, 'wb') as fh:
                pickle.dump((self.cfg, job), fh, protocol=4)
            p = subprocess.Popen([self.cfg['python'], str(HARNESS), '--_job', sp, rp], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return _Running(_PopenProc(p), _FileConn(rp, sp), job, time.time(), d)
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

    def run(self, jobs, on_result, timeout_of, workers, tick=None):
        """Runs `jobs` (a deque; callbacks may add to it) with at most `workers` processes.  v4: `tick()` is called
        at every turn of the loop (it may add jobs, or raise to stop the run: running jobs are then killed)."""
        finishing = []
        try:
            while True:
                if tick is not None:
                    tick()
                if not (jobs or self.running):
                    break
                while jobs and len(self.running) < workers:
                    job = jobs.popleft()
                    try:
                        self.running.append(self._start(job))
                    except Exception as e:
                        on_result(job, {'name': job['name'], 'kind': job['kind'], 'outcome': 'env_error',
                                        'crash': 'cannot start a job process: %s' % exc_line(e), 'seconds': 0.0})
                waitables = [r.conn for r in self.running if not isinstance(r.conn, _FileConn)] + \
                    [r.proc.sentinel for r in self.running if r.proc.sentinel is not None]
                if waitables:
                    mp_wait(waitables, timeout=0.5 if not self.cfg.get('python') else 0.2)
                elif self.running:
                    time.sleep(0.1)
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


# ======================================================================================================================
# v4: fixture replay, the parent's side (validation of R1 against R2, the read-only store, per-job eligibility)
# ======================================================================================================================
_FX_SAFE_CALLS = frozenset({'frozenset', 'set', 'tuple', 'list', 'dict', 'str', 'int', 'float', 'bool', 'bytes',
                            'range', 'len', 'sorted', 'min', 'max', 'sum', 'abs', 'round', 'Path', 'PurePath',
                            'zip', 'enumerate', 'reversed', 'repr', 'chr', 'ord', 'any', 'all', 'isinstance', 'map',
                            'filter', 'divmod', 'pow', 'hex', 'oct', 'bin', 'complex', 'slice', 'Fraction',
                            'OrderedDict', 'namedtuple', 'defaultdict', 'Counter', 'deque'})
_FX_SAFE_ATTR_CALLS = frozenset({('re', 'compile'), ('re', 'escape'), ('math', 'sqrt'), ('math', 'log'),
                                 ('math', 'log10'), ('math', 'exp'), ('math', 'floor'), ('math', 'ceil'),
                                 ('math', 'isclose'), ('math', 'inf'), ('os', 'path'), ('collections', 'namedtuple'),
                                 ('collections', 'OrderedDict')})
_FX_STR_METHODS = frozenset({'join', 'format', 'split', 'strip', 'lower', 'upper', 'replace', 'encode', 'decode',
                             'splitlines', 'rstrip', 'lstrip', 'startswith', 'endswith', 'zfill', 'ljust', 'rjust'})


def _inert_expr(e):
    """An expression whose evaluation at import can only build a value (no call that could change shared state)."""
    for n in ast.walk(e):
        if isinstance(n, (ast.NamedExpr, ast.Await, ast.Yield, ast.YieldFrom)):
            return False
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in _FX_SAFE_CALLS:
                continue
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                    and (f.value.id, f.attr) in _FX_SAFE_ATTR_CALLS:
                continue
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Constant) and f.attr in _FX_STR_METHODS:
                continue
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Attribute) and isinstance(f.value.value,
                                                                                               ast.Name) \
                    and f.value.value.id == 'os' and f.value.attr == 'path':
                continue
            return False
    return True


def mutant_import_inert(scorer_src, old, new):
    """(True, '') when the mutated region of the scorer can have no effect at import time beyond binding its own
    names: it lies in a comment / blank space, inside the BODY of a top-level def, or in a top-level assignment
    whose value only builds data.  Anything else (a class body, a decorator, a default, an import, a call at module
    level) -> (False, why): that job runs without fixture replay."""
    msrc = scorer_src.replace(old, new, 1)
    pre = 0
    while pre < min(len(old), len(new)) and old[pre] == new[pre]:
        pre += 1
    suf = 0
    while suf < min(len(old), len(new)) - pre and old[len(old) - 1 - suf] == new[len(new) - 1 - suf]:
        suf += 1
    start = scorer_src.index(old) + pre                 # the text that really changes
    end = start + len(new) - pre - suf
    try:
        tree = ast.parse(msrc)
    except SyntaxError as e:
        return False, 'the mutant does not parse (%s)' % e.msg
    starts = [0]
    for line in msrc.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))

    def off(lineno, col):
        # ast columns are utf-8 byte offsets: convert through the line's text
        line_start = starts[lineno - 1]
        text = msrc[line_start:starts[lineno] if lineno < len(starts) else len(msrc)]
        return line_start + len(text.encode('utf-8')[:col].decode('utf-8', 'ignore'))
    for st in tree.body:
        s0 = off(st.lineno, st.col_offset)
        s1 = off(st.end_lineno, st.end_col_offset)
        first = min([s0] + [off(d.lineno, d.col_offset) for d in getattr(st, 'decorator_list', [])])
        if s1 <= start or first >= end:
            continue                                    # no overlap
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and not st.decorator_list:
            b0 = off(st.body[0].lineno, st.body[0].col_offset)
            if start >= b0:
                continue                                # inside the body: runs only when called
            return False, 'the mutation touches the header of def %s (line %d)' % (st.name, st.lineno)
        if isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)) and st.value is not None \
                and all(isinstance(t, (ast.Name, ast.Tuple, ast.List)) for t in
                        (st.targets if isinstance(st, ast.Assign) else [st.target])) \
                and _inert_expr(st.value):
            continue
        if isinstance(st, ast.Pass) or (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant)):
            continue
        return False, 'the mutation touches a %s at line %d that runs at import' % (type(st).__name__, st.lineno)
    return True, ''


def _fx_effects_equal(a, b):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x[0] != y[0] or x[1] != y[1]:
            return False
        if x[0] in ('link', 'copy') and x[2] != y[2]:
            return False
        if x[0] == 'write' and (x[2] != y[2] or x[3] != y[3]):
            return False
    return True


_FX_KEYS = ('args', 'gnames', 'glob', 'mods', 'env', 'reads', 'pre', 'post', 'ret_fp')   # not 'rand': a
# process's own seed; a call that consumes the global random state is never replayable (_finish)


def fx_validate(r1, r2):
    """R1's and R2's recordings -> ({call index: R1 record} replayable, {indices of validated effect-free calls},
    Counter of the reasons the others are not, a refusal reason or None)."""
    a, b = r1['records'], r2['records']
    if len(a) != len(b):
        return {}, set(), collections.Counter(), ('the two baselines made %d and %d generator calls (a nondeterministic '
                                                  'suite?)' % (len(a), len(b)))
    if r1.get('modules', 0) > 1 or r2.get('modules', 0) > 1:
        return {}, set(), collections.Counter(), 'the suite loads the scorer more than once'
    good, noop, why = {}, set(), collections.Counter()
    for x, y in zip(a, b):
        if x['fn'] != y['fn']:
            return {}, set(), collections.Counter(), 'call %d is %s in one baseline and %s in the other' % (
                x['i'], x['fn'], y['fn'])
        if not x['ok'] or not y['ok']:
            why[short(x.get('why') or y.get('why') or '?', 70)] += 1
            continue
        diff = [k for k in _FX_KEYS if x.get(k) != y.get(k)]
        if diff or not _fx_effects_equal(x['effects'], y['effects']):
            why['the two baselines differ (%s)' % (', '.join(diff) or 'effects')] += 1
            continue
        if not x['effects']:
            noop.add(x['i'])
            continue
        good[x['i']] = x
    return good, noop, why, None


def fx_finalize_store(store_dir, good):
    """Checks every store file against its name (the sha256 of its content), drops the records that need a file
    that is missing or wrong, sets the files read-only.  -> (inodes {(ino, dev): sha}, meta {sha: (size, mtime_ns)},
    number of dropped records)."""
    need = collections.defaultdict(list)
    for i, rec in good.items():
        for eff in rec['effects']:
            if eff[0] in ('link', 'copy'):
                need[eff[2]].append(i)
    bad = set()
    inodes, meta = {}, {}
    for sha in sorted(need):
        p = os.path.join(store_dir, sha)
        try:
            h = hashlib.sha256()
            with open(p, 'rb') as fh:
                for chunk in iter(lambda: fh.read(1 << 22), b''):
                    h.update(chunk)
            if h.hexdigest() != sha:
                raise OSError('content does not match its name')
            os.chmod(p, 0o444)
            st = os.stat(p)
            inodes[(st.st_ino, st.st_dev)] = sha
            meta[sha] = (st.st_size, st.st_mtime_ns)
        except OSError:
            bad.update(need[sha])
    for i in bad:
        good.pop(i, None)
    for name in os.listdir(store_dir):                  # files no validated record uses
        if name not in meta:
            try:
                os.unlink(os.path.join(store_dir, name))
            except OSError:
                pass
    return inodes, meta, len(bad)


def fx_check_store(store_dir, meta):
    """After a job: every store file keeps its size, time and read-only mode.  -> (restored modes, changed files)."""
    restored, changed = [], []
    for sha, (size, mt) in meta.items():
        p = os.path.join(store_dir, sha)
        try:
            st = os.stat(p)
        except OSError:
            changed.append(sha[:12] + ' (missing)')
            continue
        if st.st_size != size or st.st_mtime_ns != mt:
            changed.append(sha[:12])
        if st.st_mode & 0o222:
            try:
                os.chmod(p, 0o444)
            except OSError:
                pass
            restored.append(sha[:12])
    return restored, changed


def fx_verify_store(store_dir, meta):
    bad = []
    for sha in meta:
        h = hashlib.sha256()
        try:
            with open(os.path.join(store_dir, sha), 'rb') as fh:
                for chunk in iter(lambda: fh.read(1 << 22), b''):
                    h.update(chunk)
            if h.hexdigest() != sha:
                bad.append(sha[:12])
        except OSError:
            bad.append(sha[:12] + ' (unreadable)')
    return bad


def fx_remove_store(store_dir):
    if not os.path.isdir(store_dir):
        return
    for name in os.listdir(store_dir):
        p = os.path.join(store_dir, name)
        try:
            os.chmod(p, 0o666)
        except OSError:
            pass
    shutil.rmtree(store_dir, ignore_errors=True)


def _fmt_memo(m):
    if not m:
        return 'memo off'
    keys = ('hit_mem', 'hit_disk', 'miss', 'bypass', 'off', 'violation', 'path_in_result', 'nan_in_result')
    return 'memo ' + ' '.join('%s=%d' % (k, m.get(k, 0)) for k in keys if m.get(k))


def old_console_encoding():
    """The encoding a child `python test.py` printed with when the old harnesses captured it through a pipe."""
    pie = os.environ.get('PYTHONIOENCODING')
    if pie and pie.split(':')[0]:
        return pie.split(':')[0]
    if os.environ.get('PYTHONUTF8') == '1' or sys.flags.utf8_mode:
        return 'utf-8'
    return locale.getpreferredencoding(False)


# ======================================================================================================================
# v4.1: --changed-from PARENT --parent-report REPORT - the selection follows the fixture suite as well as the scorer
# (ROADMAP session 116 item 1; review5 MAJOR-1)
# ======================================================================================================================
_REPORT_HEAD_RE = re.compile(r'^(scorer|test|mutants) +(.+) sha256 ([0-9a-f]{64})\s*$')
_REPORT_ROW_RE = re.compile(r'^(\S+)  (.+?)  \((\d+(?:\.\d+)?) s\)(?:  \[.*\])?\s*$')
_REPORT_VERDICTS = (('ALL KILLED (', 'ALL KILLED'), ('SURVIVORS: ', 'SURVIVORS'), ('NOT CERTIFIED', 'NOT CERTIFIED'),
                    ('REFUSED', 'REFUSED'), ('INTERRUPTED', 'INTERRUPTED'))
SEL_REASONS = ('scorer-line', 'kill-case-changed', 'not-in-parent', 'machinery-changed')


def parse_report(text):
    """A mutlib report (v1 to v4.1 write the same rows) -> {'version', 'scorer' / 'test' / 'mutants': (path, sha256),
    'rows': {mutant: detail}, 'dups': names with two rows, 'verdict': 'ALL KILLED' | 'SURVIVORS' | 'NOT CERTIFIED' |
    'REFUSED' | 'INTERRUPTED' | None}.  Rows are the lines between the BASELINE line and the `N mutants:` summary."""
    rep = {'version': None, 'rows': {}, 'dups': set(), 'verdict': None}
    lines = [ln.rstrip('\r') for ln in text.split('\n')]
    if lines and lines[0].startswith('mutlib '):
        rep['version'] = lines[0].split('  ')[0].strip()
    stage = 'head'
    for ln in lines:
        for prefix, v in _REPORT_VERDICTS:
            if ln.startswith(prefix):
                rep['verdict'] = v
        if stage == 'head':
            m = _REPORT_HEAD_RE.match(ln)
            if m:
                rep.setdefault(m.group(1), (m.group(2), m.group(3)))
            elif ln.startswith('BASELINE  '):
                stage = 'rows'
            continue
        if stage != 'rows':
            continue
        if re.match(r'^\d+ mutants: ', ln):
            stage = 'tail'
            continue
        if ln.startswith(('CONTROL ', 'BASELINE')):
            continue
        m = _REPORT_ROW_RE.match(ln)
        if m:
            if m.group(1) in rep['rows']:
                rep['dups'].add(m.group(1))
            rep['rows'][m.group(1)] = m.group(2)
    return rep


# what makes a suite impossible to compare case by case (then every mutant runs)
_SUITE_REFLECT_NAMES = frozenset({'globals', 'vars', 'locals', 'exec', 'eval', '__import__', 'compile', 'breakpoint'})
_SUITE_REFLECT_ATTRS = frozenset({'__dict__', '__globals__', 'f_globals', 'f_locals', 'f_back', '_getframe',
                                  'currentframe', '__code__', '__defaults__', '__kwdefaults__', '__closure__',
                                  'import_module', 'reload', '__builtins__', 'modules'})
_SUITE_REFLECT_MODULES = frozenset({'inspect', 'runpy', 'gc', 'ctypes', 'code', 'pdb', 'builtins', '__main__'})
# a data assignment is position-free (a helper, not machinery) only if its value calls nothing but these
_PURE_CALL_NAMES = frozenset({'dict', 'list', 'tuple', 'set', 'frozenset', 'range', 'len', 'sorted', 'sum', 'min',
                              'max', 'abs', 'round', 'int', 'float', 'str', 'bool', 'repr', 'enumerate', 'zip',
                              'reversed', 'any', 'all', 'chr', 'ord', 'bytes', 'hex', 'oct', 'bin', 'divmod', 'pow',
                              'format', 'isinstance', 'map', 'filter', 'complex', 'slice'})
_PURE_IMPORT_MODULES = frozenset({'math', 'statistics', 're', 'string', 'json', 'hashlib', 'itertools', 'functools',
                                  'operator', 'fractions', 'textwrap', 'collections', 'pathlib'})
# what makes a suite function a WRITER (fixture machinery): it writes / creates / removes files or starts processes
_W_ATTRS = frozenset({'write_text', 'write_bytes', 'mkdir', 'makedirs', 'link', 'hardlink_to', 'symlink_to',
                      'copyfile', 'copy2', 'copytree', 'copyfileobj', 'rename', 'renames', 'unlink', 'remove',
                      'removedirs', 'rmtree', 'rmdir', 'symlink', 'touch', 'truncate', 'mkstemp', 'mkdtemp', 'dump',
                      'write', 'writelines', 'chmod', 'lchmod', 'utime', 'savez', 'save', 'NamedTemporaryFile',
                      'TemporaryDirectory', 'TemporaryFile', 'SpooledTemporaryFile', 'ZipFile', 'TarFile', 'mkfifo',
                      'mknod', 'CopyFile2'})
_W_MOD_ATTRS = frozenset({'replace', 'copy', 'move', 'open', 'system', 'popen', 'startfile', 'run', 'Popen', 'call',
                          'check_call', 'check_output', 'spawnl', 'spawnv', 'execv', 'execl'})
_W_ROOTS = frozenset({'os', 'shutil', 'io', 'codecs', 'tempfile', 'zipfile', 'tarfile', 'subprocess', 'gzip', 'bz2',
                      'lzma', 'pathlib', '_winapi'})


class _Unknown2(Exception):
    """A case name that cannot be evaluated statically."""


def _dump(node):
    return ast.dump(node, annotate_fields=True, include_attributes=False)


def _open_writes(call, pos):
    """Whether an open(...) call (its mode at position `pos`) may open for writing (an unknown mode: yes)."""
    if any(isinstance(a, ast.Starred) for a in call.args):
        return True
    mode = call.args[pos] if len(call.args) > pos else None
    for k in call.keywords:
        if k.arg is None:
            return True
        if k.arg == 'mode':
            mode = k.value
    if mode is None:
        return False
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        return bool(set(mode.value) & set('wax+'))
    return True


class SuiteModel:
    """v4.1: a fixture suite seen as CASES and SHARED MACHINERY, to compare a derived suite with its parent's.

    Cases.  N family: a top-level `case('NAME', ...)` statement (a static case), and a top-level statement that
    registers cases some other way - a loop of case() calls, a call of a function that registers - (a group: its case
    names are evaluated statically where every name is a constant expression of literal loop values, else unknown).
    V family: an entry ('NAME', ...) of a literal table iterated by a top-level `for NAME, ... in TABLE:` whose one
    guard is followed by a print whose output starts with the entry's name (so a failing line's first word IS the
    name).  A case's fingerprint is its own AST plus the definitions of every suite helper it reaches (the functions
    it calls, the constants it reads, transitively) that is not machinery.  A case whose reach reads BASE (the whole
    fixture directory) also depends on every case that writes fixtures.

    Machinery: every other top-level statement, in order (a run of cases is one marker, so moving a statement across
    cases counts), every helper the machinery reaches, every function that writes files / starts processes / changes
    module state / declares globals / registers cases, and every data assignment whose value is not a pure function
    of constants and helpers (it depends on WHEN it runs).  Not compared: the module docstring and the value of the
    BASE assignment (mutlib replaces it).

    `problems` lists why the suite cannot be compared case by case (reflection, a non-stdlib import, a `case`
    function that does not record its first argument as the name, no identifiable case): then every mutant runs."""

    def __init__(self, path, src, okname='ok'):
        self.path = Path(path)
        self.okname = okname
        self.problems = []
        self.units = []                 # dicts: kind 'case' | 'group' | 'entry', name, names, node, line, fp
        self.machinery = []             # normalised dumps in order ('UNITS' marks a run of cases)
        self.mach_desc = []             # what each machinery item is (for the header)
        self.family = None
        self.single_guard = False
        self.case_param = None
        try:
            plan = TestPlan(path, src, okname)
        except (HarnessError, SyntaxError, ValueError) as e:
            self.problems.append('%s cannot be analysed: %s' % (self.path.name, e if isinstance(e, HarnessError)
                                                                else exc_line(e)))
            return
        self.plan = plan
        self.family = plan.family
        tree = self.tree = plan.tree
        body = tree.body
        self._reflection(tree)
        self.binds = collections.defaultdict(list)
        for i, st in enumerate(body):
            for nm in bound_names(st):
                self.binds[nm].append(i)
        self.imported = set()
        self.pure_mods, self.pure_names, self.w_names = set(), set(), set()
        self.rand_mods, self.rand_names = set(), set()     # the random module / its functions (global state)
        for st in body:
            if isinstance(st, ast.Import):
                for a in st.names:
                    nm = a.asname or a.name.split('.')[0]
                    self.imported.add(nm)
                    if a.name == 'random':
                        self.rand_mods.add(nm)
                    if a.name.split('.')[0] in _PURE_IMPORT_MODULES and a.name.split('.')[0] != 'pathlib':
                        self.pure_mods.add(nm)
            elif isinstance(st, ast.ImportFrom):
                root = (st.module or '').split('.')[0]
                for a in st.names:
                    nm = a.asname or a.name
                    self.imported.add(nm)
                    if root in _PURE_IMPORT_MODULES and a.name not in _W_ATTRS:
                        self.pure_names.add(nm)
                    if root in _W_ROOTS:
                        self.w_names.add(nm)
                    if root == 'random' and a.name not in ('Random', 'SystemRandom'):
                        self.rand_names.add(nm)
        guards = [n for n in ast.walk(tree) if isinstance(n, ast.stmt) and _is_guard_stmt(n, okname)]
        kinds = ['other'] * len(body)            # doc | case | group | table | def | assign | other
        norm = list(body)                        # the statement as compared (BASE, tables normalised)
        units = []
        self.case_def = None
        reg = set()
        if self.family == 'N':
            self._n_family(plan, body, kinds, units, guards, reg)
        else:
            self._v_family(tree, body, kinds, norm, units, guards)
        bi = plan.base_idx
        nb = copy.deepcopy(body[bi])
        nb.value = ast.Constant('<mutlib: BASE>')
        norm[bi] = nb
        kinds[bi] = 'other'
        loads_doc = any(isinstance(n, ast.Name) and n.id == '__doc__' for n in ast.walk(tree))
        for i, st in enumerate(body):
            if kinds[i] == 'other' and isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) \
                    and not (i == 0 and loads_doc):
                kinds[i] = 'doc'
        # ---- helpers: single-bound top-level defs and position-free data assignments ------------------------------
        helpers = {}
        for i, st in enumerate(body):
            if kinds[i] != 'other' or i == bi:
                continue
            if isinstance(st, ast.FunctionDef) and self.binds[st.name] == [i] and not st.decorator_list \
                    and st.name != 'case':
                helpers[st.name] = ('def', i)
                kinds[i] = 'def'
            elif isinstance(st, (ast.Assign, ast.AnnAssign)) and st.value is not None:
                tg = st.targets if isinstance(st, ast.Assign) else [st.target]
                if len(tg) == 1 and isinstance(tg[0], ast.Name) and self.binds[tg[0].id] == [i] \
                        and self._pure(st.value):
                    helpers[tg[0].id] = ('assign', i)
                    kinds[i] = 'assign'
        # position-free: an assignment / a def's defaults read only builtins, imports and position-free helpers
        changed = True
        while changed:
            changed = False
            for nm, (k, i) in list(helpers.items()):
                st = body[i]
                if k == 'def':
                    parts = _outer_parts(st)
                    if not all(self._pure(p) for p in parts):
                        del helpers[nm]
                        kinds[i] = 'other'
                        changed = True
                        continue
                    reads = set().union(*[loaded_names(p) for p in parts]) if parts else set()
                else:
                    reads = loaded_names(st)
                bad = [r for r in reads if r in self.binds and r not in helpers and r not in self.imported]
                if bad:
                    del helpers[nm]
                    kinds[i] = 'other'
                    changed = True
        self.helpers = helpers
        # ---- machinery: writers, state changers, registrars, and the closure of what the machinery reads ------------
        self.defs = collections.defaultdict(list)          # every top-level def, helper or not
        for st in body:
            if isinstance(st, _FUNC_NODES):
                self.defs[st.name].append(st)
        writers = set(plan.fx_names) | {nm for nm, ds in self.defs.items() if any(self._def_writes(d) for d in ds)}
        # module state (registering a case - case() and its list - is not: its order only moves a label)
        reglist = {plan.cases_name} if self.family == 'N' and plan.cases_name else set()
        self.reglist = reglist
        self.stateful = {nm for nm, ds in self.defs.items() if nm != 'case'
                         and any(self._changes_state(d, free_vars(d) - reglist) for d in ds)}
        changed = True
        while changed:
            changed = False
            for nm, ds in self.defs.items():
                fv = set().union(*[free_vars(d) for d in ds])
                if nm not in writers and fv & writers:
                    writers.add(nm)
                    changed = True
                if nm not in self.stateful and nm != 'case' and fv & self.stateful:
                    self.stateful.add(nm)
                    changed = True
        self.writers = writers
        # names some function rebinds through `global` (a counter, a cache): whoever reads them sees module state
        self.global_names = {g for n in ast.walk(tree) if isinstance(n, ast.Global) for g in n.names} \
            - {okname} - reglist
        mach = set()
        for nm, (k, i) in helpers.items():
            if k == 'def' and (nm in writers or nm in reg or nm in self.stateful):
                mach.add(nm)
        todo = []
        for i, st in enumerate(body):
            if kinds[i] in ('other', 'table'):
                todo.extend(loaded_names(norm[i]))
        for nm in mach:
            todo.extend(self._helper_reads(nm))
        while todo:
            nm = todo.pop()
            if nm in helpers and nm not in mach:
                mach.add(nm)
                todo.extend(self._helper_reads(nm))
        self.mach_helpers = mach
        # ---- the machinery sequence -------------------------------------------------------------------------------
        seq, desc = [('family', self.family, self.single_guard, self.case_param)], ['the suite family']
        for i, st in enumerate(body):
            k = kinds[i]
            if k == 'doc':
                continue
            if k in ('case', 'group'):
                if seq[-1] != 'UNITS':
                    seq.append('UNITS')
                    desc.append('a run of cases')
                continue
            if k in ('def', 'assign') and self._helper_name(st) not in mach:
                continue
            seq.append(_dump(norm[i]))
            try:
                what = ast.unparse(norm[i]).split('\n')[0]
            except Exception:
                what = type(st).__name__
            desc.append('line %d: %s' % (st.lineno, short(what, 70)))
        self.machinery, self.mach_desc = seq, desc
        # ---- the cases' fingerprints ------------------------------------------------------------------------------
        # shared fixture objects: machinery names bound to what a writer returned (`good = make('good')`); a case that
        # uses one depends on every case that uses it AND writes (it may write into that directory)
        shared = set()
        for i, st in enumerate(body):
            if kinds[i] == 'other' and isinstance(st, (ast.Assign, ast.AnnAssign)) and st.value is not None and any(
                    isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in writers
                    for n in ast.walk(st.value)):
                shared |= bound_names(st)
        self.shared = shared
        own = []
        for u in units:
            u['idx'] = len(own)
            reach, reads_base, calls_writer, reads = self._reach(u['node'])
            parts = [('case', _dump(u['node']))] + sorted((nm, _dump(body[helpers[nm][1]])) for nm in reach)
            u['own'] = hashlib.sha256(repr(parts).encode('utf-8', 'surrogatepass')).hexdigest()
            u['base'] = reads_base
            u['writes'] = calls_writer
            u['shares'] = reads & shared
            # module state: a case that changes it (or calls a helper that does, or draws from the global random
            # state) depends on every other such case - one of them changed moves what the others see
            u['stateful'] = bool(reads & (self.stateful | self.global_names)) or \
                self._changes_state(u['node'], set(self.binds) - self.reglist)
            own.append(u)
        direct = {u['idx']: [w['idx'] for w in own if w is not u and (
            (w['writes'] and (u['base'] or u['shares'] & w['shares'])) or (u['stateful'] and w['stateful']))]
            for u in own}
        for u in own:                               # transitively: what a case depends on may depend on more
            seen, todo = set(), list(direct[u['idx']])
            while todo:
                k = todo.pop()
                if k not in seen:
                    seen.add(k)
                    todo.extend(direct[k])
            seen.discard(u['idx'])
            deps = sorted(own[k]['own'] for k in seen)
            u['deps'] = len(deps)
            u['fp'] = (u['own'] if not deps else
                       hashlib.sha256(('%s|%s' % (u['own'], ','.join(deps))).encode()).hexdigest())
        self.units = own
        self.fp_count = collections.Counter(u['fp'] for u in own)
        if not own and not self.problems:
            self.problems.append('%s: no case can be identified (%s)' % (
                self.path.name, 'no top-level case(...) statement' if self.family == 'N'
                else 'no literal table iterated by a loop whose guard is followed by a print of the entry name'))

    # ---- helpers of the analysis ----------------------------------------------------------------------------------
    def _reflection(self, tree):
        seen = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and n.id in _SUITE_REFLECT_NAMES:
                seen.append('line %d: %s' % (n.lineno, n.id))
            elif isinstance(n, ast.Attribute) and n.attr in _SUITE_REFLECT_ATTRS:
                seen.append('line %d: .%s' % (n.lineno, n.attr))
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                if isinstance(n, ast.ImportFrom) and (n.level or any(a.name == '*' for a in n.names)):
                    seen.append('line %d: a relative or star import' % n.lineno)
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or '']
                for m in mods:
                    root = m.split('.')[0]
                    if root in _SUITE_REFLECT_MODULES:
                        seen.append('line %d: import %s' % (n.lineno, m))
                    elif root not in sys.stdlib_module_names:
                        seen.append('line %d: import %s (not the standard library: its code is not compared)'
                                    % (n.lineno, m))
        if seen:
            self.problems.append('%s uses what a case-by-case comparison cannot follow: %s'
                                 % (self.path.name, '; '.join(seen[:4])))

    def _helper_name(self, st):
        if isinstance(st, ast.FunctionDef):
            return st.name
        tg = st.targets if isinstance(st, ast.Assign) else [st.target]
        return tg[0].id

    def _helper_reads(self, nm):
        k, i = self.helpers[nm]
        return loaded_names(self.tree.body[i])

    def _pure(self, e):
        """No call but pure builtins, pure stdlib modules and non-mutating methods; no await / yield / walrus."""
        for n in ast.walk(e):
            if isinstance(n, (ast.Await, ast.Yield, ast.YieldFrom, ast.NamedExpr)):
                return False
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if isinstance(f, ast.Name):
                if (f.id in _PURE_CALL_NAMES and f.id not in self.binds) or f.id in self.pure_names:
                    continue
                return False
            if isinstance(f, ast.Attribute):
                if isinstance(f.value, ast.Name) and f.value.id in self.pure_mods and f.attr not in _W_ATTRS \
                        and f.attr not in _W_MOD_ATTRS:
                    continue
                if f.attr in PURE_METHODS and f.attr not in MUTATING_METHODS:
                    continue
            return False
        return True

    def _def_writes(self, fn):
        for n in ast.walk(fn):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if isinstance(f, ast.Attribute):
                if f.attr in _W_ATTRS or (f.attr in _W_MOD_ATTRS and root_name(f.value) in (_W_ROOTS | self.w_names)):
                    return True
                if f.attr == 'open' and _open_writes(n, 0):
                    return True
            elif isinstance(f, ast.Name):
                if f.id == 'open' and _open_writes(n, 1):
                    return True
                if f.id in self.w_names:
                    return True
        return False

    def _changes_state(self, fn, free):
        """global / nonlocal, a store into an attribute or item of a module-level name (`free`), setattr / delattr of
        one, a mutating method called on one, a draw from the global random state."""
        for n in ast.walk(fn):
            if isinstance(n, (ast.Global, ast.Nonlocal)):
                return True
            if isinstance(n, (ast.Attribute, ast.Subscript)) and isinstance(n.ctx, (ast.Store, ast.Del)) \
                    and root_name(n) in free:
                return True
            if isinstance(n, ast.AugAssign) and isinstance(n.target, (ast.Attribute, ast.Subscript)) \
                    and root_name(n.target) in free:
                return True
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name) and f.id in ('setattr', 'delattr') and n.args \
                        and root_name(n.args[0]) in free:
                    return True
                if isinstance(f, ast.Attribute) and f.attr in MUTATING_METHODS and root_name(f.value) in free:
                    return True
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in self.rand_mods \
                        and f.attr not in ('Random', 'SystemRandom'):
                    return True
                if isinstance(f, ast.Name) and f.id in self.rand_names:
                    return True
        return False

    def _reach(self, node):
        """-> (the non-machinery helpers a case reaches: its fingerprint; whether it reads BASE other than inside a
        writer; whether it calls a writer; every name it reads, following every function and helper it reaches,
        machinery included: its dependencies)."""
        fp, seen, todo = set(), set(), [(nm, False) for nm in loaded_names(node)]
        reads, reads_nw = set(), set()
        while todo:
            nm, in_writer = todo.pop()
            reads.add(nm)
            if not in_writer:
                reads_nw.add(nm)
            if (nm, in_writer) in seen:
                continue
            seen.add((nm, in_writer))
            if nm in self.helpers:
                rd = self._helper_reads(nm)
                if nm not in self.mach_helpers:
                    fp.add(nm)
            elif nm in self.defs:
                rd = set().union(*[loaded_names(d) for d in self.defs[nm]])
            else:
                continue
            w = in_writer or nm in self.writers
            todo.extend((r, w) for r in rd)
        return fp, 'BASE' in reads_nw, bool(reads & self.writers), reads

    # ---- N family --------------------------------------------------------------------------------------------------
    def _n_family(self, plan, body, kinds, units, guards, reg):
        cn = plan.cases_name
        ci, fi = plan.case_idx, plan.final_idx
        fn = body[ci]
        self.case_def = fn
        param = self._case_shape(fn, cn)
        if param is None:
            self.problems.append("%s: its case() does not simply append a dict / tuple whose name is its first "
                                 "argument, so a kill label cannot be tied to a case(...) statement" % self.path.name)
            return
        if self.binds['case'] != [ci] or len(self.binds[cn]) != 1:
            self.problems.append('%s: `case` or `%s` is bound more than once' % (self.path.name, cn))
            return
        self.case_param = param
        final = body[fi]
        in_final = {id(n) for n in ast.walk(final)}
        self.single_guard = len(guards) == 1 and id(guards[0]) in in_final
        # functions that register cases (call case, touch the case list, or call such a function)
        defs = {st.name: st for st in body if isinstance(st, ast.FunctionDef) and st.name != 'case'}
        marks = {'case', cn}
        changed = True
        while changed:
            changed = False
            for nm, d in defs.items():
                if nm not in reg and free_vars(d) & (marks | reg):
                    reg.add(nm)
                    changed = True
        self.registrars = reg
        consts = self._literal_consts(body)
        for i, st in enumerate(body):
            if i in (ci, fi) or i > fi or cn in bound_names(st):
                continue
            if isinstance(st, _FUNC_NODES) and not any(loaded_names(p) & (marks | reg) for p in _outer_parts(st)):
                continue                    # a definition registers nothing until it is called (a registrar: machinery)
            c = st.value if isinstance(st, ast.Expr) else None
            if (isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == 'case' and c.args
                    and isinstance(c.args[0], ast.Constant) and isinstance(c.args[0].value, str)
                    and not any(isinstance(a, ast.Starred) for a in c.args)
                    and not any(k.arg == param for k in c.keywords)
                    and not (loaded_names(st) & ({cn} | reg))
                    and sum(1 for n in ast.walk(st) if isinstance(n, ast.Name) and n.id == 'case') == 1):
                kinds[i] = 'case'
                units.append({'kind': 'case', 'name': c.args[0].value, 'names': frozenset([c.args[0].value]),
                              'node': st, 'line': st.lineno})
            elif loaded_names(st) & (marks | reg):
                kinds[i] = 'group'
                try:
                    out = set()
                    self._group_names([st], {}, consts, cn, reg, param, out)
                    names = frozenset(out)
                except _Unknown2:
                    names = None
                units.append({'kind': 'group', 'name': None, 'names': names, 'node': st, 'line': st.lineno})

    @staticmethod
    def _case_shape(fn, cn):
        """The name of case()'s first parameter if case() appends to the case list exactly once a dict(name=P, ...)
        / {'name': P, ...} / (P, ...) and never rebinds P; else None."""
        a = fn.args
        params = a.posonlyargs + a.args
        if not params:
            return None
        p = params[0].arg
        uses = [n for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id == cn]
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and isinstance(n.func.value, ast.Name) and n.func.value.id == cn]
        if len(uses) != 1 or len(calls) != 1 or calls[0].func.attr != 'append' or len(calls[0].args) != 1 \
                or calls[0].keywords:
            return None
        if any(isinstance(n, ast.Name) and n.id == p and not isinstance(n.ctx, ast.Load) for n in ast.walk(fn)):
            return None
        if any(isinstance(n, (ast.Global, ast.Nonlocal)) for n in ast.walk(fn)):
            return None
        x = calls[0].args[0]
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == 'dict' and not x.args:
            kw = {k.arg: k.value for k in x.keywords}
            if None not in kw and isinstance(kw.get('name'), ast.Name) and kw['name'].id == p:
                return p
        if isinstance(x, ast.Dict) and None not in x.keys:
            for k, v in zip(x.keys, x.values):
                if isinstance(k, ast.Constant) and k.value == 'name':
                    return p if isinstance(v, ast.Name) and v.id == p and \
                        [kk.value for kk in x.keys if isinstance(kk, ast.Constant)].count('name') == 1 else None
        if isinstance(x, (ast.Tuple, ast.List)) and x.elts and isinstance(x.elts[0], ast.Name) and x.elts[0].id == p:
            return p
        return None

    def _literal_consts(self, body):
        """Module-level names bound once to a literal (tuple / str / number, or a list / dict / set nobody changes)."""
        out = {}
        for i, st in enumerate(body):
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                nm = st.targets[0].id
                if self.binds[nm] != [i]:
                    continue
                try:
                    v = ast.literal_eval(st.value)
                except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                    continue
                if isinstance(v, (list, dict, set)) and self._mutated(nm):
                    continue
                out[nm] = v
        return out

    def _mutated(self, nm):
        for n in ast.walk(self.tree):
            if isinstance(n, (ast.Attribute, ast.Subscript)) and isinstance(n.ctx, (ast.Store, ast.Del)) \
                    and root_name(n) == nm:
                return True
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and root_name(n.func.value) == nm \
                    and n.func.attr in MUTATING_METHODS:
                return True
            if isinstance(n, ast.AugAssign) and root_name(n.target) == nm:
                return True
            if isinstance(n, ast.Call) and any(isinstance(a, ast.Name) and a.id == nm for a in n.args) \
                    and not (isinstance(n.func, ast.Name) and n.func.id in _PURE_CALL_NAMES):
                return True                             # handed to a function that might change it
        return False

    def _group_names(self, stmts, env, consts, cn, reg, param, out):
        """The case names a group registers, by evaluating its loops over literal values (a superset: conditions are
        ignored).  _Unknown2 when a name, a loop or a registration cannot be followed."""
        marks = {'case', cn} | reg
        for s in stmts:
            if isinstance(s, ast.For) and not s.orelse:
                vals = self._iter_values(s.iter, env, consts)
                tnames = {n.id for n in ast.walk(s.target) if isinstance(n, ast.Name)}
                for b in s.body:
                    for n in ast.walk(b):
                        if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load) and \
                                (n.id in tnames or n.id in env):
                            raise _Unknown2('a loop variable is rebound')
                for v in vals:
                    e2 = dict(env)
                    self._bind(s.target, v, e2)
                    self._group_names(s.body, e2, consts, cn, reg, param, out)
            elif isinstance(s, ast.If):
                self._group_names(s.body, env, consts, cn, reg, param, out)
                self._group_names(s.orelse, env, consts, cn, reg, param, out)
            elif isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and isinstance(s.value.func, ast.Name) \
                    and s.value.func.id == 'case':
                c = s.value
                if any(isinstance(a, ast.Starred) for a in c.args) or any(k.arg is None for k in c.keywords):
                    raise _Unknown2('case(*args)')
                if any(loaded_names(a) & marks for a in list(c.args) + [k.value for k in c.keywords]):
                    raise _Unknown2('a registration inside a registration')
                arg = c.args[0] if c.args else next((k.value for k in c.keywords if k.arg == param), None)
                if arg is None:
                    raise _Unknown2('no name')
                v = self._eval(arg, env, consts)
                if not isinstance(v, str):
                    raise _Unknown2('the name is not a string')
                out.add(v)
            elif isinstance(s, (ast.Pass, ast.Continue, ast.Break)):
                continue
            elif loaded_names(s) & marks:
                raise _Unknown2('a registration this analysis does not follow')

    def _bind(self, target, v, env):
        if isinstance(target, ast.Name):
            env[target.id] = v
            return
        if isinstance(target, (ast.Tuple, ast.List)) and not any(isinstance(e, ast.Starred) for e in target.elts):
            try:
                vs = list(v)
            except TypeError:
                raise _Unknown2('unpacking')
            if len(vs) != len(target.elts):
                raise _Unknown2('unpacking')
            for t, x in zip(target.elts, vs):
                self._bind(t, x, env)
            return
        raise _Unknown2('a loop target')

    def _iter_values(self, e, env, consts):
        if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id in ('range', 'enumerate', 'zip',
                                                                                      'sorted', 'reversed') \
                and e.func.id not in self.binds and not e.keywords:
            args = [self._eval(a, env, consts) for a in e.args]
            try:
                return list({'range': range, 'enumerate': enumerate, 'zip': zip, 'sorted': sorted,
                             'reversed': reversed}[e.func.id](*args))
            except Exception:
                raise _Unknown2('iteration')
        v = self._eval(e, env, consts)
        if isinstance(v, (tuple, list, str, range, frozenset, set, dict)):
            return list(v)
        raise _Unknown2('iteration')

    def _eval(self, e, env, consts):
        if isinstance(e, ast.Constant):
            return e.value
        if isinstance(e, ast.Name):
            if e.id in env:
                return env[e.id]
            if e.id in consts:
                return consts[e.id]
            raise _Unknown2(e.id)
        if isinstance(e, (ast.Tuple, ast.List)) and not any(isinstance(x, ast.Starred) for x in e.elts):
            vals = [self._eval(x, env, consts) for x in e.elts]
            return tuple(vals) if isinstance(e, ast.Tuple) else vals
        if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.Mod, ast.Add, ast.Mult)):
            a, b = self._eval(e.left, env, consts), self._eval(e.right, env, consts)
            try:
                if isinstance(e.op, ast.Mod) and isinstance(a, str):
                    return a % b
                if isinstance(e.op, ast.Add) and type(a) is type(b) and isinstance(a, (str, int, tuple)):
                    return a + b
                if isinstance(e.op, ast.Mult) and isinstance(a, (str, int)) and isinstance(b, int):
                    return a * b
            except Exception:
                pass
            raise _Unknown2('operator')
        if isinstance(e, ast.JoinedStr):
            s = []
            for v in e.values:
                if isinstance(v, ast.Constant):
                    s.append(str(v.value))
                elif isinstance(v, ast.FormattedValue):
                    x = self._eval(v.value, env, consts)
                    x = {-1: x, 115: str(x), 114: repr(x), 97: ascii(x)}[v.conversion]
                    spec = '' if v.format_spec is None else self._eval(v.format_spec, env, consts)
                    try:
                        s.append(format(x, spec))
                    except Exception:
                        raise _Unknown2('format')
                else:
                    raise _Unknown2('f-string')
            return ''.join(s)
        if isinstance(e, ast.Slice):
            return slice(*[None if x is None else self._eval(x, env, consts) for x in (e.lower, e.upper, e.step)])
        if isinstance(e, ast.Subscript):
            v, k = self._eval(e.value, env, consts), self._eval(e.slice, env, consts)
            try:
                return v[k]
            except Exception:
                raise _Unknown2('subscript')
        if isinstance(e, ast.Call) and not e.keywords and not any(isinstance(a, ast.Starred) for a in e.args):
            f = e.func
            if isinstance(f, ast.Attribute) and f.attr in ('format', 'upper', 'lower', 'strip', 'replace', 'join'):
                recv = self._eval(f.value, env, consts)
                if isinstance(recv, str):
                    try:
                        return getattr(recv, f.attr)(*[self._eval(a, env, consts) for a in e.args])
                    except Exception:
                        raise _Unknown2('method')
            if isinstance(f, ast.Name) and f.id in ('str', 'repr', 'int') and f.id not in self.binds and \
                    len(e.args) == 1:
                return {'str': str, 'repr': repr, 'int': int}[f.id](self._eval(e.args[0], env, consts))
        raise _Unknown2(type(e).__name__)

    # ---- V family --------------------------------------------------------------------------------------------------
    def _v_family(self, tree, body, kinds, norm, units, guards):
        orient = _guard_orientations(tree, self.okname)
        loads = collections.defaultdict(list)
        parents = parent_map(tree)
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                loads[n.id].append(n)
        for i, st in enumerate(body):
            if not isinstance(st, ast.For) or st.orelse:
                continue
            nm = self._table_loop(st, orient)
            if nm is None:
                continue
            it = st.iter
            if isinstance(it, (ast.List, ast.Tuple)):
                table, host = it, i
            elif isinstance(it, ast.Name) and len(self.binds[it.id]) == 1:
                host = self.binds[it.id][0]
                hs = body[host]
                if not (host < i and isinstance(hs, ast.Assign) and len(hs.targets) == 1
                        and isinstance(hs.targets[0], ast.Name) and isinstance(hs.value, (ast.List, ast.Tuple))):
                    continue
                # the table is only iterated (or measured): nobody else reads, changes or hands out its entries
                if any(not (parents.get(ld) is st and st.iter is ld)
                       and not (isinstance(parents.get(ld), ast.Call) and isinstance(parents[ld].func, ast.Name)
                                and parents[ld].func.id == 'len' and len(parents[ld].args) == 1)
                       for ld in loads[it.id]):
                    continue
                table = hs.value
            else:
                continue
            entries = []
            for e in table.elts:
                if not (isinstance(e, (ast.Tuple, ast.List)) and e.elts and isinstance(e.elts[0], ast.Constant)
                        and isinstance(e.elts[0].value, str) and not any(isinstance(x, ast.Starred)
                                                                           for x in e.elts)):
                    entries = None
                    break
                name = e.elts[0].value
                if not name.split() or name[0].isspace():
                    entries = None
                    break
                entries.append((name, e))
            if not entries:
                continue
            for name, e in entries:
                units.append({'kind': 'entry', 'name': name, 'names': frozenset([name]), 'node': e,
                              'line': e.lineno})
            ns = copy.deepcopy(body[host])
            tbl = ns.iter if host == i else ns.value
            tbl.elts = [ast.Constant('<mutlib: the table entries>')]
            norm[host] = ns
            kinds[host] = 'table'

    def _table_loop(self, st, orient):
        """`for NAME, ... in TABLE:` with exactly one guard, at the top of its body, followed by a print whose output
        starts with NAME and a blank, NAME never rebound in the body -> NAME, else None."""
        t = st.target
        if not (isinstance(t, (ast.Tuple, ast.List)) and t.elts and isinstance(t.elts[0], ast.Name)
                and not any(isinstance(x, ast.Starred) for x in t.elts)):
            return None
        nm = t.elts[0].id
        if sum(1 for x in t.elts if isinstance(x, ast.Name) and x.id == nm) != 1:
            return None
        gs = [n for b in st.body for n in ast.walk(b) if isinstance(n, ast.stmt) and _is_guard_stmt(n, self.okname)]
        top = [k for k, b in enumerate(st.body) if _is_guard_stmt(b, self.okname)]
        if len(gs) != 1 or len(top) != 1 or orient.get(id(st.body[top[0]])) != 'after' \
                or top[0] + 1 >= len(st.body):
            return None
        if any(isinstance(n, ast.Name) and n.id == nm and not isinstance(n.ctx, ast.Load)
               for b in st.body for n in ast.walk(b)):
            return None
        return nm if self._print_leads_with(st.body[top[0] + 1], nm) else None

    def _print_leads_with(self, s, nm):
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and isinstance(s.value.func, ast.Name)
                and s.value.func.id == 'print' and 'print' not in self.binds):
            return False
        c = s.value
        if not c.args or any(isinstance(a, ast.Starred) for a in c.args) or \
                any(k.arg not in ('end', 'flush') for k in c.keywords):
            return False
        for n in ast.walk(c):                   # nothing in the print's arguments may print first
            if isinstance(n, ast.Call) and n is not c:
                f = n.func
                if isinstance(f, ast.Name) and f.id in _PURE_CALL_NAMES and f.id not in self.binds:
                    continue
                if isinstance(f, ast.Attribute) and f.attr in PURE_METHODS and f.attr not in MUTATING_METHODS:
                    continue
                return False
            if isinstance(n, (ast.Lambda, ast.NamedExpr, ast.Await, ast.Yield, ast.YieldFrom)):
                return False
        a0 = c.args[0]
        if isinstance(a0, ast.Name):
            return a0.id == nm
        if isinstance(a0, ast.BinOp) and isinstance(a0.op, ast.Mod) and isinstance(a0.left, ast.Constant) \
                and isinstance(a0.left.value, str) and re.match(r'%-?\d*s\s', a0.left.value):
            r = a0.right
            first = r.elts[0] if isinstance(r, ast.Tuple) and r.elts else r
            return isinstance(first, ast.Name) and first.id == nm
        if isinstance(a0, ast.JoinedStr) and len(a0.values) >= 2:
            v0, v1 = a0.values[0], a0.values[1]
            spec_ok = v0.format_spec is None if isinstance(v0, ast.FormattedValue) else False
            if isinstance(v0, ast.FormattedValue) and isinstance(v0.format_spec, ast.JoinedStr) and \
                    all(isinstance(x, ast.Constant) for x in v0.format_spec.values):
                spec_ok = re.fullmatch(r'[<>^]?\d*', ''.join(x.value for x in v0.format_spec.values)) is not None
            return (isinstance(v0, ast.FormattedValue) and isinstance(v0.value, ast.Name) and v0.value.id == nm
                    and v0.conversion in (-1, 115) and spec_ok and isinstance(v1, ast.Constant)
                    and isinstance(v1.value, str) and v1.value[:1].isspace())
        return False

    # ---- the comparison -----------------------------------------------------------------------------------------------
    def candidates(self, label):
        """The cases of THIS (the parent's) suite that a kill labelled `label` can come from (N family: the static
        cases of that name and every group that registers it or whose names are unknown; V family: the entries whose
        name or first word it is), or None when no case can carry it (the kill cannot be tied to a case)."""
        if self.family == 'N':
            out = [u for u in self.units if (u['names'] is None or label in u['names'])]
        else:
            out = [u for u in self.units if u['name'] == label or u['name'].split()[0] == label]
        return out or None


def suite_model(path, src, okname):
    """SuiteModel, with any failure of the analysis itself turned into a problem (then every mutant runs)."""
    try:
        return SuiteModel(path, src, okname)
    except Exception as e:                              # noqa: BLE001 - never a crash, never a silent pass
        m = SuiteModel.__new__(SuiteModel)
        m.path, m.okname, m.units, m.machinery, m.mach_desc = Path(path), okname, [], [], []
        m.family, m.single_guard, m.case_param, m.fp_count = None, False, None, collections.Counter()
        m.problems = ['the comparison of %s failed: %s' % (Path(path).name, exc_line(e))]
        return m


def suite_diff(parent, derived):
    """-> (None or why the machinery differs, {parent case index: 'changed' | 'removed'}, added names)."""
    if parent.problems or derived.problems:
        probs = list(parent.problems) + [x for x in derived.problems if x not in parent.problems]
        return '; '.join(probs), {}, []
    if parent.machinery != derived.machinery:
        a, b = parent.machinery, derived.machinery
        k = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        pd = parent.mach_desc[k] if k < len(a) else 'nothing (the derived suite has more)'
        dd = derived.mach_desc[k] if k < len(b) else 'nothing (the parent suite has more)'
        where = ('%s (it differs below its first line)' % dd.split(': ', 1)[-1] if pd == dd
                 else 'parent %s / derived %s' % (pd, dd))
        return 'the shared machinery differs at item %d: %s' % (k, where), {}, []
    status = {}
    dnames = collections.Counter()
    for u in derived.units:
        for n in (u['names'] or ()):
            dnames[n] += 1
    for u in parent.units:
        if derived.fp_count[u['fp']]:
            continue
        gone = u['names'] is not None and not any(dnames[n] for n in u['names'])
        status[u['idx']] = 'removed' if gone else 'changed'
    pn = set().union(*[u['names'] for u in parent.units if u['names'] is not None]) if parent.units else set()
    added = sorted(n for n in dnames if n not in pn)
    return None, status, added


def _case_label(u):
    if u['kind'] == 'group':
        return 'the group at line %d%s' % (u['line'], '' if u['names'] is None else ' (%d names)' % len(u['names']))
    return '%s (line %d)' % (u['name'], u['line'])


def select_derived(args, scorer_src, scorer_sha, mutants, selected, header, test_path, test_src):
    """v4.1 --changed-from PARENT --parent-report REPORT [--sample F] [--seed N] -> (selected, summary, detail).
    Selected always: (i) scorer-line: the anchor overlaps a scorer line that differs from PARENT; (ii) kill-case-
    changed: the case that killed it in the parent's report is changed or removed in this suite (its own AST and every
    helper it reaches, parent suite against this one), or cannot be tied to a case; (iii) not-in-parent: no row in the
    report, not KILLED there, or its (old, new) differs from the parent's mutant script; (iv) machinery-changed: the
    suite's shared machinery differs (or cannot be compared): ALL mutants.  Plus the reproducible sample of the rest.
    Raises HarnessError (a refusal, exit 3) when the report does not belong to PARENT or is not certified."""
    parent = Path(args.changed_from).resolve()
    parent_bytes = parent.read_bytes()
    parent_src = parent_bytes.decode('utf-8')
    parent_sha = sha256_bytes(parent_bytes)
    rpath = Path(args.parent_report).resolve()
    rbytes = rpath.read_bytes()
    rep = parse_report(rbytes.decode('utf-8', errors='replace'))
    for key in ('scorer', 'test', 'mutants'):
        if key not in rep:
            raise HarnessError('--parent-report %s has no `%s ... sha256 ...` header line: not a mutlib report'
                               % (rpath, key))
    if rep['scorer'][1] != parent_sha:
        raise HarnessError('--parent-report %s is a report of a scorer with sha256 %s, not of --changed-from %s '
                           '(sha256 %s)' % (rpath, rep['scorer'][1][:16], parent, parent_sha[:16]))
    if rep['verdict'] not in ('ALL KILLED', 'SURVIVORS'):
        raise HarnessError('--parent-report %s is not a certified report (its verdict: %s); only an ALL KILLED or '
                           'SURVIVORS report can vouch for a kill' % (rpath, rep['verdict'] or 'none - incomplete?'))
    files = {}
    for key, opt in (('test', args.parent_test), ('mutants', args.parent_mutants)):
        p = Path(opt or rep[key][0])
        try:
            b = p.read_bytes()
        except OSError as e:
            raise HarnessError('the parent %s named by the report (%s) cannot be read (%s); pass --parent-%s PATH '
                               '(a copy with sha256 %s)' % (key, p, exc_line(e), key, rep[key][1][:16]))
        if sha256_bytes(b) != rep[key][1]:
            raise HarnessError('the parent %s %s has sha256 %s, the report was made with %s'
                               % (key, p, sha256_bytes(b)[:16], rep[key][1][:16]))
        files[key] = (p.resolve(), b.decode('utf-8'))
    try:
        pinfo = extract_mutants_full(files['mutants'][0], parent_src)
    except HarnessError as e:
        raise HarnessError("the parent's mutant script %s cannot be read strictly, so no mutant's text can be "
                           "compared with the parent's (%s); run without --changed-from for a full run"
                           % (files['mutants'][0], e))
    pmut = {n: (o, w) for n, o, w in pinfo['mutants']}
    by = {n: (o, w) for n, o, w in mutants}
    # ---- (i) scorer lines -----------------------------------------------------------------------------------------
    changed = changed_lines(parent_src, scorer_src)
    touch, covered = set(), set()
    for n in selected:
        a, b = anchor_lines(scorer_src, by[n][0])
        span = set(range(a, b + 1))
        if span & changed:
            touch.add(n)
            covered |= span & changed
    # ---- (iv) the suites ------------------------------------------------------------------------------------------
    pm = suite_model(files['test'][0], files['test'][1], args.ok_name)
    dm = suite_model(test_path, test_src, args.ok_name)
    mach_why, status, added = suite_diff(pm, dm)
    reasons = collections.OrderedDict((n, []) for n in selected)
    by_case = collections.defaultdict(list)
    for n in selected:
        rs = reasons[n]
        if n in touch:
            rs.append(('scorer-line', None))
        if mach_why:
            rs.append(('machinery-changed', None))
        if n not in pmut:
            rs.append(('not-in-parent', "absent from the parent's mutant script"))
            continue
        if pmut[n] != by[n]:
            rs.append(('not-in-parent', "its text differs from the parent's"))
            continue
        row = rep['rows'].get(n)
        if row is None or n in rep['dups']:
            rs.append(('not-in-parent', 'no row in the parent report' if row is None else 'two rows there'))
            continue
        if not row.startswith('KILLED'):
            rs.append(('not-in-parent', '%s there' % short(row, 40)))
            continue
        if not row.startswith('KILLED by '):
            rs.append(('not-in-parent', 'killed there by no named case (%s)' % short(row, 40)))
            continue
        if mach_why:
            continue
        label = row[len('KILLED by '):]
        cands = pm.candidates(label)
        if cands is None:
            rs.append(('kill-case-changed', 'its kill case %r cannot be tied to a case of the parent suite' % label))
            by_case['%s (not identifiable)' % label].append(n)
            continue
        bad = [u for u in cands if u['idx'] in status]
        if bad:
            what = ', '.join('%s %s' % (_case_label(u), status[u['idx']]) for u in bad[:3])
            rs.append(('kill-case-changed', 'killed by %s there; %s' % (label, what)))
            by_case[label].append(n)
    rest = [n for n in selected if not reasons[n]]
    frac = 0.2 if args.sample is None else args.sample
    seed = args.seed if args.seed is not None else int(scorer_sha[:16], 16)
    k = min(len(rest), int(round(frac * len(rest))))
    sample = random.Random(seed).sample(rest, k) if k else []
    sset = set(sample)
    out = [n for n in selected if reasons[n] or n in sset]
    primary = collections.OrderedDict((r, []) for r in SEL_REASONS)
    for n in selected:
        if reasons[n]:
            primary[reasons[n][0][0]].append(n)
    counts = ' + '.join('%d %s' % (len(v), r) for r, v in primary.items())
    header.append('selection: --changed-from %s (sha256 %s, %d changed line(s) of the scorer) with --parent-report %s '
                  '(sha256 %s, %s, %s, %d rows; parent suite %s sha256 %s, parent mutants %s sha256 %s): %s + a '
                  'sample of %d of the other %d (fraction %.3f, seed %d) = %d selected'
                  % (parent, parent_sha[:16], len(changed), rpath, sha256_bytes(rbytes)[:16], rep['version'] or '?',
                     rep['verdict'], len(rep['rows']), files['test'][0], rep['test'][1][:16], files['mutants'][0],
                     rep['mutants'][1][:16], counts, len(sample), len(rest), frac, seed, len(out)))
    if mach_why:
        header.append('  suite: %s -> every mutant runs (machinery-changed)' % mach_why)
    else:
        ch = sorted(status.items())
        names = {u['idx']: _case_label(u) for u in pm.units}
        header.append('  suite: family %s, the shared machinery is equal (%d items); parent cases %d (%d groups), '
                      'derived %d (%d groups); changed or removed in the derived suite: %s; added: %s'
                      % (pm.family, len(pm.machinery), len(pm.units), sum(u['kind'] == 'group' for u in pm.units),
                         len(dm.units), sum(u['kind'] == 'group' for u in dm.units),
                         ('%d: %s' % (len(ch), '; '.join('%s %s' % (names[ln], st) for ln, st in ch[:40])
                                      + (' ...' if len(ch) > 40 else ''))) if ch else 'none',
                         (short(repr(added), 400) if added else 'none')))
    for r, v in primary.items():
        if r == 'machinery-changed' and v:
            header.append('  machinery-changed: all %d selected mutant(s) not already listed' % len(v))
            continue
        header.append('  %s: %s' % (r, v or 'none'))
        if r == 'kill-case-changed' and by_case:
            header.append('    by kill case: %s' % '; '.join('%s: %s' % (c, ms) for c, ms in by_case.items()))
        if r == 'not-in-parent' and v:
            why = collections.defaultdict(list)
            for n in v:
                why[reasons[n][0][1]].append(n)
            header.append('    why: %s' % '; '.join('%s: %s' % (w, ms) for w, ms in why.items()))
    multi = ['%s=%s' % (n, '+'.join(r for r, _ in reasons[n])) for n in selected if len(reasons[n]) > 1
             and not (len(reasons[n]) == 2 and reasons[n][1][0] == 'machinery-changed')]
    if multi:
        header.append('  more than one reason: %s' % short(' '.join(multi), 600))
    header.append('  sampled: %s' % (sorted(sample, key=selected.index) or 'none'))
    uncovered = sorted(changed - covered)
    if uncovered:
        header.append('  changed lines no mutant anchor overlaps (not mutated by this run): %s'
                      % _ranges([x + 1 for x in uncovered]))
    if not changed:
        header.append('  NOTE: the scorer does not differ from the parent')
    summary = 'selected by --changed-from %s with --parent-report %s: %s + %d of %d sampled' % (
        parent.name, rpath.name, counts, len(sample), len(rest))
    return out, summary, reasons


def fx_profile_report(data, family, res):
    """The --profile-fixtures table: per case, the fixture files written for it (bytes, rows = newlines), the time
    spent generating them and the time its check took (the baseline's guards)."""
    recs = data.get('records') or []
    guards = data.get('guards') or []
    cases = data.get('cases') or []
    out = []
    rows = []
    if family == 'N' and cases:
        # registration segment k = the generator calls between case k-1 and case k; the check of case k = the k-th
        # guard of the final loop (its time since the guard before it)
        bounds = [c[2] for c in cases]                      # generator calls made before each registration
        seg = [[] for _ in cases]
        tail = []
        for r in recs:
            j = next((idx for idx, s in enumerate(bounds) if r['i'] < s), None)
            (seg[j] if j is not None else tail).append(r)
        bounds = [c[0] for c in cases]
        loop = guards[-len(cases):] if len(guards) >= len(cases) else guards
        for idx, (t, name, _) in enumerate(cases):
            rs = seg[idx]
            ev = None
            if idx < len(loop):
                prev = loop[idx - 1][0] if idx else (bounds[-1] if bounds else 0.0)
                ev = loop[idx][0] - prev
            rows.append((name, sum(r.get('dur', 0.0) for r in rs), sum(r.get('bytes', 0) or 0 for r in rs),
                         sum(r.get('rows', 0) or 0 for r in rs), sum(r.get('files', 0) or 0 for r in rs), ev,
                         ', '.join(sorted({r['fn'] for r in rs}))))
        if tail:
            rows.append(('(after the last case)', sum(r.get('dur', 0.0) for r in tail),
                         sum(r.get('bytes', 0) or 0 for r in tail), sum(r.get('rows', 0) or 0 for r in tail),
                         sum(r.get('files', 0) or 0 for r in tail), None, ''))
    else:
        prev = 0.0
        gi = 0
        for g in guards:
            t, line, label, _ = g
            rs = [r for r in recs if prev <= r.get('t', 0) < t]
            gen = sum(r.get('dur', 0.0) for r in rs)
            rows.append(('%s (line %d)' % (label or '?', line), gen, sum(r.get('bytes', 0) or 0 for r in rs),
                         sum(r.get('rows', 0) or 0 for r in rs), sum(r.get('files', 0) or 0 for r in rs),
                         max(0.0, t - prev - gen), ', '.join(sorted({r['fn'] for r in rs}))))
            prev = t
            gi += 1
    tot = [sum(r[i] or 0 for r in rows) for i in (1, 2, 3, 4)]
    tev = sum(r[5] or 0 for r in rows)
    out.append('fixture profile (%s family, %d case(s)): generation %.1f s, %.1f MB in %d file(s), %d rows; checks '
               '%.1f s; suite total %.1f s' % (family, len(rows), tot[0], tot[1] / 1e6, tot[3], tot[2], tev,
                                              res.get('seconds', 0.0)))
    out.append('%-34s %9s %11s %9s %6s %8s  %s' % ('case', 'gen s', 'bytes', 'rows', 'files', 'check s',
                                                   'generators'))
    for name, gen, b, r, f, ev, fns in rows:
        out.append('%-34s %9.3f %11d %9d %6d %8s  %s' % (short(name, 34), gen, b, r, f,
                                                         '-' if ev is None else '%.3f' % ev, fns))
    big = sorted(rows, key=lambda x: -x[2])[:10]
    out.append('largest by bytes: %s' % ', '.join('%s %.1f MB' % (short(x[0], 30), x[2] / 1e6) for x in big if x[2]))
    slow = sorted(rows, key=lambda x: -(x[1] + (x[5] or 0)))[:10]
    out.append('slowest (generation + check): %s' % ', '.join('%s %.2f s' % (short(x[0], 30), x[1] + (x[5] or 0))
                                                             for x in slow))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='fast, strict, shared mutation harness (see README.md)')
    ap.add_argument('--scorer', required=True, help='the scorer under test (the sealed copy when there is one)')
    ap.add_argument('--test', required=True, help='its fixture suite test_*.py')
    ap.add_argument('--mutants', required=True, help='its mutant script mut_*.py (read, never run)')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 1) - 4))
    ap.add_argument('--no-memo', action='store_true', help='no read_run parse memo')
    ap.add_argument('--no-fast', action='store_true', help='no early exit: every suite runs to its end')
    ap.add_argument('--no-replay', action='store_true', help='no fixture replay: every job writes its own fixtures')
    ap.add_argument('--only', help='comma-separated mutant names')
    ap.add_argument('--changed-from', help='parent scorer (derived scorers): run the mutants whose anchor touches a '
                                           'changed line, whose kill case changed, ... (needs --parent-report)')
    ap.add_argument('--parent-report', help="the parent's sealed mutlib report (v4.1: required by --changed-from)")
    ap.add_argument('--parent-test', help="the parent's fixture suite (default: the path in the report's header; its "
                                          "sha256 must match the report)")
    ap.add_argument('--parent-mutants', help="the parent's mutant script (default: the path in the report's header; "
                                             "its sha256 must match the report)")
    ap.add_argument('--sample', type=float, default=None, help='... plus this fraction of the rest (default 0.2)')
    ap.add_argument('--seed', type=int, default=None, help='sample seed (default: from the scorer sha256)')
    ap.add_argument('--control', action='store_true', help='add three equivalent mutants that must survive')
    ap.add_argument('--python', default=None, help='run every job (the baselines too) under this interpreter')
    ap.add_argument('--profile-fixtures', action='store_true', help='run the baseline only and report, per case, '
                                                                    'the fixture bytes, rows and time')
    ap.add_argument('--timeout', type=float, default=0.0, help='seconds per mutant (default: from the baseline)')
    ap.add_argument('--out', help='also write the report here')
    ap.add_argument('--ok-name', default='ok', help="the suite's pass flag (default ok)")
    ap.add_argument('--cache-dir', default=None, help='read_run memo cache root (default mutlib/cache)')
    ap.add_argument('--work-dir', default=str(HERE / 'work'))
    ap.add_argument('--memo-mem-mb', type=int, default=256, help='in-memory memo budget per job')
    ap.add_argument('--keep-work', action='store_true')
    ap.add_argument('--dry-run', action='store_true', help='print the header and the selection, run nothing')
    ap.add_argument('--replay-min-s', type=float, default=FX_MIN_SAVING_S, help=argparse.SUPPRESS)
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

    def refuse(msg):
        for h in header:
            print(h)
        print('REFUSED: %s' % msg)
        if args.out:
            Path(args.out).write_text('\n'.join(header + ['REFUSED: %s' % msg]) + '\n', encoding='utf-8')
        return 3
    if (args.sample is not None or args.seed is not None) and not args.changed_from:
        return refuse('--sample / --seed select a sample of the mutants that do NOT touch the lines changed from a '
                      'parent: they need --changed-from PARENT')
    if args.sample is not None and not (0.0 <= args.sample <= 1.0):
        return refuse('--sample must be a fraction between 0 and 1, not %r' % args.sample)
    if args.changed_from and not Path(args.changed_from).is_file():
        return refuse('--changed-from %s is not a file' % args.changed_from)
    if (args.parent_report or args.parent_test or args.parent_mutants) and not args.changed_from:
        return refuse('--parent-report / --parent-test / --parent-mutants belong to a --changed-from selection')
    if args.changed_from and not args.parent_report:
        return refuse('--changed-from needs --parent-report REPORT (v4.1, ROADMAP session 116 item 1): a mutant on an '
                      'unchanged scorer line whose killing fixture changed must run, and only the parent\'s sealed '
                      'report says which case killed it; run without --changed-from for a full run')
    if args.parent_report and not Path(args.parent_report).is_file():
        return refuse('--parent-report %s is not a file' % args.parent_report)
    try:
        info = extract_mutants_full(mutf, scorer_src)
        fmt, mutants, lines_run, coll = info['format'], info['mutants'], info['lines'], info['coll']
        draft_skipped = validate_mutants(mutants, scorer_src, info['draft_only'])
        plan = TestPlan(test, test_src, args.ok_name)
    except HarnessError as e:
        return refuse(e)
    n_defined = len(mutants)
    header.append('mutants: format %s, %d defined (strict: every use of %s checked; statements evaluated at lines %s)'
                  % (fmt, n_defined, coll, _ranges(lines_run)))
    header.extend(info['harness'])
    names = [m[0] for m in mutants]
    by_name = {n: (o, w) for n, o, w in mutants}
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
    selection_note = ''
    if args.changed_from:
        try:
            selected, selection_note, _ = select_derived(args, scorer_src, scorer_sha, mutants, selected, header,
                                                         test, test_src)
        except HarnessError as e:
            return refuse('--changed-from: %s' % e)
        except (OSError, UnicodeDecodeError) as e:
            return refuse('--changed-from: %s' % exc_line(e))
    # ---- the memo (v4 review4 MAJOR-2: identity comparisons turn it off) ------------------------------------------
    memo_on = not args.no_memo
    memo_plan = plan_memo(scorer_src)
    suite_ident = identity_uses(plan.tree)
    if memo_on and not memo_plan.ok:
        header.append('memo: off for this scorer (%s)' % memo_plan.reason)
        memo_on = False
    elif memo_on and suite_ident:
        header.append('memo: off for this run (the suite compares object identity; a fresh copy of a parse value '
                      'would change the answer: %s)' % '; '.join(suite_ident[:3]))
        memo_on = False
    ident_mutants = []
    if memo_on:
        for n in selected:
            new = by_name[n][1]
            if re.search(r'\bis\b|\bid\b|\bis_(not)?\b', new):
                try:
                    if identity_uses(ast.parse(scorer_src.replace(*by_name[n], 1))):
                        ident_mutants.append(n)
                except SyntaxError:
                    pass
    fast = plan.fast and not args.no_fast
    header.append('suite: family %s; fast %s (%s); end of suite: %s at line %d'
                  % (plan.family, 'on' if fast else 'OFF', 'disabled by --no-fast' if args.no_fast and plan.fast
                     else plan.fast_reason, {'call': 'the final exit call', 'raise': 'the final raise SystemExit',
                                             'append': 'after the last statement'}[plan.end_kind], plan.end_lineno))
    cache_root = Path(args.cache_dir) if args.cache_dir else HERE / 'cache'
    cache_dir = cache_root / '_shared_v4'           # v4: shared by every scorer (the key holds the closure's hash)
    if memo_on:
        header.append('memo: read_run, %d dependencies %s, %d touching statements, file params %s, dep hash %s, '
                      'cache %s' % (len(memo_plan.dep_names), list(memo_plan.dep_names), memo_plan.n_touch,
                                    sorted(memo_plan.file_params), memo_plan.dep_hash[:16], cache_dir))
        if memo_plan.file_params:
            header.append('memo: file arguments keyed by %s' % (
                'their path as well as their type and bytes, memory only, no disk cache (read_run can carry the '
                'path: %s)' % '; '.join(memo_plan.path_reasons[:3]) if memo_plan.path_sensitive else
                'their type (a stat failure by its kind) and bytes; a value that carries the path or name of its file '
                'argument, or a NaN, is never stored'))
        if ident_mutants:
            header.append('memo: off for %d mutant(s) whose source compares object identity: %s'
                          % (len(ident_mutants), ident_mutants[:10]))
    # ---- the job interpreter (v4 --python) -----------------------------------------------------------------------
    python = None
    if args.python:
        import subprocess
        python = str(Path(args.python).resolve())
        try:
            who = subprocess.run([python, '-c', 'import sys; print(sys.implementation.name, sys.version.split()[0])'],
                                 capture_output=True, text=True, timeout=60).stdout.strip()
        except (OSError, subprocess.SubprocessError) as e:
            return refuse('--python %s does not run: %s' % (python, exc_line(e)))
        if not who:
            return refuse('--python %s does not run' % python)
        header.append('interpreter: every job runs under %s (%s); the suite is transformed again in each job '
                      '(no shared bytecode); verdicts under another interpreter are trusted only for the suites '
                      'where the acceptance compared them with CPython' % (python, who))
    # ---- fixture replay (v4), the static part --------------------------------------------------------------------
    fx_reason = None
    if args.no_replay:
        fx_reason = 'disabled by --no-replay'
    elif not plan.fx_names:
        fx_reason = 'the suite has no fixture generator (a top-level function that writes a file)'
    else:
        deny = fx_deny_uses(ast.parse(scorer_src)) + fx_deny_uses(plan.tree)
        bypass = fx_copy_bypass_uses(ast.parse(scorer_src)) + fx_copy_bypass_uses(plan.tree)
        if deny:
            fx_reason = ('the scorer or the suite reads file times / inodes / modes, which a shared fixture would '
                         'change: %s' % '; '.join(deny[:3]))
        elif bypass:
            fx_reason = ('the scorer or the suite copies files in a way that raises no audit event (shutil.copy2 / '
                         'copytree / move go through _winapi.CopyFile2): a shared read-only fixture would be copied '
                         'read-only, unseen - review5 MAJOR-2; automatic --no-replay: %s' % '; '.join(bypass[:3]))
    replay_on = fx_reason is None
    controls = control_mutants(scorer_src, 'read_run' if memo_on else 'evaluate') if args.control else []
    run_dir = (Path(args.work_dir) / ('%s_%d_%d' % (scorer.stem, os.getpid(), int(time.time())))).resolve()
    workers = max(1, min(args.workers, len(selected) + len(controls)))
    old_enc = old_console_encoding()
    header.append('isolation: one fresh spawned process per job; a crash outside the scorer or a dead job process is '
                  'confirmed by a rerun; old console encoding %s (noted, not emulated)' % old_enc)
    if replay_on:
        # every job of a replaying run hashes strings the same way: a generator whose output follows set / dict order
        # of strings writes what every job would write (two baselines of different seeds could agree by chance)
        os.environ['PYTHONHASHSEED'] = '0'
        header.append('fixtures: replay candidates %s (validated by two baselines before any job uses them); every '
                      'job runs with PYTHONHASHSEED=0' % plan.fx_names)
    else:
        header.append('fixtures: every job writes its own (replay off: %s)' % fx_reason)
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
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg = {'work': str(run_dir), 'scorer_name': scorer.name, 'test_path': str(test), 'test_src': test_src,
           'okname': args.ok_name, 'scorer_src': scorer_src, 'cache': str(cache_dir),
           'memo_mem': args.memo_mem_mb * 1024 * 1024, 'old_encoding': old_enc,
           'test_code': marshal.dumps(plan.code), 'uses_argv2': plan.uses_argv2, 'family': plan.family,
           'python': python, 'foreign': bool(python), 'fx_names': list(plan.fx_names)}
    if (replay_on or args.profile_fixtures) and not python:
        cfg['test_code_fx'] = marshal.dumps(plan.code_for(True, False))
        cfg['test_code_fx_case'] = marshal.dumps(plan.code_for(True, True))
    state = {'memo': memo_on, 'fast': fast, 'timeout': args.timeout or 1800.0, 'done': 0, 'phase': 'baseline'}
    results, history = {}, collections.defaultdict(list)
    sched = Scheduler(cfg, log, args.keep_work)
    total = len(selected) + len(controls)
    fast_sound = fast
    store_dir = str(run_dir / 'fxstore')
    fx_of = {}
    fx_meta = {}
    fx_notes = {'restored': [], 'changed': []}

    def mk(kind, name, src, **flags):
        job = {'kind': kind, 'name': name, 'src': src, 'fast': state['fast'] and kind != 'baseline',
               'memo': state['memo'] and name not in ident_mutants, 'probe': kind == 'baseline', 'confirm': False,
               'nomemo': False, 'alone': False, 'isolated': False, 'fx': fx_of.get(name)}
        job.update(flags)
        return job

    def timeout_of(job):
        if job['kind'] == 'baseline':
            return 10.0 * args.timeout if args.timeout else 4 * 3600.0
        return state['timeout']

    # v4: the final exit with ok=False, evaluated here (fast mode allows only a plain expression of ok): the pipelined
    # baseline confirms it later, as v3's baseline did
    static_probe, static_probe_ok = None, not fast
    if fast:
        e = plan.exit_expr()
        if e is not None:
            try:
                ex = ast.Expression(body=_OkToFalse(args.ok_name).visit(copy.deepcopy(e)))
                ast.fix_missing_locations(ex)
                static_probe = eval(compile(ex, '<exit probe>', 'eval'), {'__builtins__': {}})   # noqa: S307
                static_probe_ok = exit_nonzero(static_probe)
            except Exception:
                static_probe_ok = False
    rc = 3
    b = b2 = None
    try:
        # ---- --profile-fixtures: the baseline alone, recording every generator call -------------------------------
        if args.profile_fixtures:
            recs_path = str(run_dir / 'fxprofile.pkl')
            got = {}
            sched.run(collections.deque([mk('baseline', 'BASELINE', scorer_src,
                                            fx={'mode': 'record', 'profile': True, 'store': None,
                                                'records_out': recs_path})]),
                      lambda job, res: got.update(res=res), timeout_of, 1)
            res = got['res']
            verdict, detail = classify(res, plan.family)
            print(_line('baseline', 'BASELINE', res, detail))
            if verdict != 'SURVIVED':
                print('REFUSED: the unmutated scorer does not pass its own suite in this harness: %s' % detail)
                return 3
            try:
                with open(recs_path, 'rb') as fh:
                    data = pickle.load(fh)
            except (OSError, pickle.UnpicklingError) as e:
                print('REFUSED: no fixture profile was written (%s)' % exc_line(e))
                return 3
            lines = fx_profile_report(data, plan.family, res)
            print('\n'.join(lines))
            if args.out:
                Path(args.out).write_text('\n'.join(header + lines) + '\n', encoding='utf-8')
            return 0
        # ---- fixture replay: the plan from the two recordings (R1 = BASELINE, R2 = BASELINE#2) -----------------------
        def fx_build(r1, r2, when):
            """Validates R1 against R2, finalises the read-only store and decides which jobs replay.  -> None, or
            why replay stays off."""
            good, noop, whys, refusal = fx_validate(r1, r2)
            if refusal:
                return refusal
            inodes, meta, dropped = fx_finalize_store(store_dir, good)
            fx_meta.clear()
            fx_meta.update(meta)
            saving = sum(rec.get('dur', 0.0) for rec in good.values())
            n_calls = len(r1['records'])
            size = sum(m[0] for m in fx_meta.values())
            if not good or saving < args.replay_min_s:
                return ('the validated generator calls took only %.2f s in the baseline (%d of %d calls validated%s)'
                        % (saving, len(good), n_calls, ('; not validated: %s' % '; '.join(
                            '%d x %s' % (c, w) for w, c in whys.most_common(3))) if whys else ''))
            plan_path = str(run_dir / 'fxplan.pkl')
            with open(plan_path, 'wb') as fh:
                pickle.dump({'J1': r1['J'], 'records': good, 'inodes': inodes, 'noop': noop}, fh, protocol=4)
            header.append('fixtures: REPLAY ON (%s) - %d of %d generator calls validated by the two baselines (%d more '
                          'validated effect-free); they took %.1f s in the baseline; store %d read-only file(s), %.1f '
                          'MB, %s' % (when, len(good), n_calls, len(noop), saving, len(fx_meta), size / 1e6, store_dir))
            if whys:
                header.append('fixtures: not replayed: %s' % '; '.join('%d x %s' % (c, w)
                                                                       for w, c in whys.most_common(4)))
            if dropped:
                header.append('fixtures: %d record(s) dropped: their store file did not verify' % dropped)
            spec = {'mode': 'replay', 'plan': plan_path, 'store': store_dir}
            off_jobs = collections.Counter()
            for name, old, new in controls + [(n,) + by_name[n] for n in selected]:
                inert, why = mutant_import_inert(scorer_src, old, new)
                if inert and re.search(r'\b(%s)\b' % '|'.join(sorted(_FX_DENY)), new):
                    inert, why = False, 'the mutant text names a file time / inode / mode'
                if inert and FX_COPY_BYPASS_RE.search(new):
                    inert, why = False, 'the mutant text copies files unaudited (copy2 / copytree / move)'
                if inert:
                    fx_of[name] = spec
                else:
                    off_jobs[short(why, 60)] += 1
            if off_jobs:
                header.append('fixtures: %d job(s) without replay: %s' % (
                    sum(off_jobs.values()), '; '.join('%d x %s' % (c, w) for w, c in off_jobs.most_common(4))))
            return None

        def load_recs(suffix=''):
            with open(str(run_dir / 'fxrec_r1.pkl') + suffix, 'rb') as fh:
                r1 = pickle.load(fh)
            with open(str(run_dir / 'fxrec_r2.pkl') + suffix, 'rb') as fh:
                r2 = pickle.load(fh)
            return r1, r2

        def accept_baseline(res, b2):
            """v3's decisions after the baseline: the memo note, the fast-mode confirmation, the write audit (workers
            forced to 1), the mutant timeout."""
            nonlocal workers, fast_sound
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
            writers = [r for r in (res, b2) if r and (r.get('outside') or r.get('spawned'))]
            if writers:
                why = []
                for r in writers:
                    if r.get('outside'):
                        why.append('wrote outside its job directory: %s' % r['outside'][:5])
                    if r.get('spawned'):
                        why.append('started processes whose writes cannot be audited: %s' % r['spawned'][:2])
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

        def on_result(job, res):
            res['fast_sound'] = fast_sound and job['fast']
            if (res.get('fx') or {}).get('store_mismatch'):
                fx_notes['changed'].append((job['name'], res['fx']['store_mismatch'][:3]))
            if fx_meta:
                restored, changed = fx_check_store(store_dir, fx_meta)
                if restored:
                    fx_notes['restored'].append((job['name'], restored[:3]))
                if changed:
                    fx_notes['changed'].append((job['name'], changed[:3]))
            if res.get('outcome') == 'fx_touched':
                history[job['name']].append(('touched the shared fixtures', res))
                log('%s: it touched the shared fixtures (%s) - rerun isolated in a fresh process without replay'
                    % (job['name'], res.get('crash')))
                jobs_now[0].appendleft(dict(job, fx=None, isolated=True, isolated_why=res.get('crash')))
                return
            if res.get('outcome') == 'memo_violation':
                history[job['name']].append(('memo violation', res))
                if state['memo']:
                    state['memo'] = False
                    header.append('memo: DISABLED at run time after %s (%s); later jobs run without it'
                                  % (job['name'], res.get('crash')))
                    log(header[-1])
                    for q in jobs_now[0]:
                        q['memo'] = False
                jobs_now[0].appendleft(dict(job, memo=False, nomemo=True))
                return
            if needs_confirmation(res) and not job['confirm']:
                history[job['name']].append(('needs confirmation', res))
                jobs_now[0].appendleft(dict(job, memo=state['memo'] and job['memo'], confirm=True))
                log('%s: %s - confirming in a fresh process' % (job['name'], classify(res, plan.family)[1]))
                return
            res['flags'] = {k: job.get(k) for k in ('confirm', 'nomemo', 'alone', 'isolated', 'isolated_why')}
            res['history'] = [(why, classify(r, plan.family)[1]) for why, r in history[job['name']]]
            results[job['name']] = res
            state['done'] += 1
            log('[%d/%d] %s' % (state['done'], total, _line(job['kind'], job['name'], res,
                                                            final_detail(res, plan.family)[1])))

        early = set()                                   # jobs the pipelined start dispatched with the baselines

        def mutant_jobs():
            q = collections.deque()
            for name, old, new in controls:
                if name not in early:
                    q.append(mk('control', name, scorer_src.replace(old, new)))
            for n in dispatch:
                q.append(mk('mutant', n, scorer_src.replace(*by_name[n])))
            return q

        def new_store():
            if os.path.isdir(store_dir):
                fx_remove_store(store_dir)
            os.makedirs(store_dir)
            for suffix in ('', '.g'):
                for r in ('r1', 'r2'):
                    try:
                        os.unlink(str(run_dir / ('fxrec_%s.pkl' % r)) + suffix)
                    except OSError:
                        pass

        def r_specs(phase_dump):
            return ({'mode': 'record', 'store': store_dir, 'records_out': str(run_dir / 'fxrec_r1.pkl'),
                     'phase_dump': phase_dump},
                    {'mode': 'record', 'store': None, 'records_out': str(run_dir / 'fxrec_r2.pkl'),
                     'phase_dump': phase_dump})
        jobs_now = [collections.deque()]
        base_res = {}

        # ---- phase 1+2 PIPELINED (the N family with replay): the mutants start when both baselines reach their
        # final loop (their generator calls are then complete and validated); the baselines' verdicts arrive later -
        pipelined_done = False
        if replay_on and plan.family == 'N' and plan.final_idx is not None and static_probe_ok:
            new_store()
            r1spec, r2spec = r_specs(True)
            jobs_now[0] = jobs = collections.deque([mk('baseline', 'BASELINE', scorer_src, fx=r1spec),
                                                    mk('baseline', 'BASELINE#2', scorer_src, fx=r2spec)])
            for name, old, new in controls:
                # the control that mutates read_run misses the memo on every parse and runs the whole suite: the
                # longest job of a run; it needs no replay plan, so it starts with the baselines
                if name == 'CONTROL_pass_end_of_read_run':
                    early.add(name)
                    jobs.append(mk('control', name, scorer_src.replace(old, new), fx=None))
            pl = {'plan': None, 'checked': False}
            state['timeout'] = args.timeout or 4 * 3600.0         # provisional, until the baseline has passed
            g1, g2 = str(run_dir / 'fxrec_r1.pkl') + '.g', str(run_dir / 'fxrec_r2.pkl') + '.g'

            def on_any(job, res):
                if job['kind'] == 'baseline':
                    base_res[job['name']] = res
                else:
                    on_result(job, res)

            def tick():
                if pl['plan'] is None and os.path.exists(g1) and os.path.exists(g2):
                    try:
                        r1, r2 = load_recs('.g')
                        why = fx_build(r1, r2, 'from the generator calls before the final loop')
                    except (OSError, pickle.UnpicklingError, AttributeError, EOFError) as e:
                        why = 'the baselines left no readable recording (%s)' % exc_line(e)
                    pl['plan'] = why or 'ok'
                    if why:                                 # the mutants start anyway, each writing its own fixtures
                        fx_of.clear()
                        fx_meta.clear()
                        header.append('fixtures: replay OFF after the baselines\' generator calls: %s' % why)
                    log(header[-1][:300])
                    state['phase'] = 'main'
                    jobs.extend(mutant_jobs())
                if not pl['checked'] and 'BASELINE' in base_res and 'BASELINE#2' in base_res:
                    pl['checked'] = True
                    res, r2 = base_res['BASELINE'], base_res['BASELINE#2']
                    res['fast_sound'] = False
                    for name, r in (('the baseline', res), ('the second baseline', r2)):
                        if classify(r, plan.family)[0] != 'SURVIVED':
                            raise _Restart('%s gave %s' % (name, classify(r, plan.family)[1]))
                        if r.get('outside') or r.get('spawned'):
                            raise _Restart('%s wrote outside its job directory or started a process' % name)
                    pr = res.get('probe')
                    if fast and (not pr or pr[0] != 'ok' or pr[1] != static_probe):
                        raise _Restart('the baseline evaluated the final exit with ok=False to %r, not %r'
                                       % (pr, static_probe))
                    if pl['plan'] is None:                  # no dump before a final loop: build from the ends
                        try:
                            r1d, r2d = load_recs()
                            why = fx_build(r1d, r2d, 'from the whole baselines')
                        except (OSError, pickle.UnpicklingError, AttributeError, EOFError) as e:
                            why = 'the baselines left no readable recording (%s)' % exc_line(e)
                        pl['plan'] = why or 'ok'
                        if why:
                            fx_of.clear()
                            fx_meta.clear()
                            header.append('fixtures: replay OFF after the baselines: %s' % why)
                        jobs.extend(mutant_jobs())
                    accept_baseline(res, r2)
                    state['phase'] = 'main'
            try:
                sched.run(jobs, on_any, timeout_of, max(workers, min(2, args.workers)), tick)
                b, b2 = base_res['BASELINE'], base_res['BASELINE#2']
                pipelined_done = True
            except _Restart as e:
                # anything unusual: every result so far is dropped and the run starts again as v3 did it (the
                # baseline alone, no fixture replay)
                header.append('fixtures: pipelined replay abandoned (%s); every job runs again the v3 way: the '
                              'baseline alone, then the mutants, no fixture replay' % e)
                log(header[-1])
                results.clear()
                history.clear()
                base_res.clear()
                early.clear()
                fx_of.clear()
                fx_meta.clear()
                fx_remove_store(store_dir)
                state.update(done=0, fast=fast, memo=memo_on, phase='baseline')
                fast_sound = fast
                replay_on = False

        if not pipelined_done:
            # ---- phase 1: the baseline (with fixture replay: R1 records and keeps the store, R2 validates) ---------
            def on_base(job, res):
                base_res[job['name']] = res
            tries = []
            for attempt in range(3):
                base_res.clear()
                jobs = collections.deque()
                if replay_on:
                    new_store()
                    r1spec, r2spec = r_specs(False)
                    jobs.append(mk('baseline', 'BASELINE', scorer_src, fx=r1spec))
                    jobs.append(mk('baseline', 'BASELINE#2', scorer_src, fx=r2spec))
                else:
                    jobs.append(mk('baseline', 'BASELINE', scorer_src))
                sched.run(jobs, on_base, timeout_of, 2 if replay_on else 1)
                res = base_res['BASELINE']
                res['fast_sound'] = False
                if replay_on and any(r.get('outside') or r.get('spawned') for r in base_res.values()):
                    # the two baselines ran side by side and one of them wrote outside its directory: neither
                    # result is v3's "baseline alone"; fixture replay goes off and the baseline runs again, alone
                    replay_on = False
                    header.append('fixtures: replay OFF - a baseline wrote outside its job directory (%s); the '
                                  'baseline runs again, alone' % ([r.get('outside', [])[:2] + r.get('spawned', [])[:1]
                                                                   for r in base_res.values()]))
                    log(header[-1])
                    fx_remove_store(store_dir)
                    continue
                tries.append(res)
                if res.get('outcome') == 'memo_violation' or base_res.get('BASELINE#2', {}).get('outcome') == \
                        'memo_violation':
                    state['memo'] = False
                    header.append('memo: DISABLED at run time (the baseline: %s); every job runs without it'
                                  % (res.get('crash') or base_res.get('BASELINE#2', {}).get('crash')))
                    log(header[-1])
                    continue
                verdict, detail = classify(res, plan.family)
                if verdict == 'SURVIVED':
                    break
                if needs_confirmation(res) and attempt == 0:
                    header.append('baseline: the first run gave %s; rerun once in a fresh process' % detail)
                    log(header[-1])
                    continue
                raise HarnessError('the unmutated scorer does not pass its own suite in this harness: %s; last lines '
                                   '%s%s' % (detail, res.get('tail'), ('\n' + res['trace']) if res.get('trace') else ''))
            else:
                raise HarnessError('the baseline could not be completed: %s' % [classify(r, plan.family)[1]
                                                                               for r in tries])
            b = res
            b2 = base_res.get('BASELINE#2')
            if replay_on:
                why_off = None
                if b2 is None or classify(b2, plan.family)[0] != 'SURVIVED':
                    why_off = 'the second baseline did not pass (%s): a nondeterministic suite?' % (
                        classify(b2, plan.family)[1] if b2 else 'missing')
                else:
                    try:
                        r1, r2 = load_recs()
                        why_off = fx_build(r1, r2, 'from the whole baselines')
                    except (OSError, pickle.UnpicklingError, AttributeError, EOFError) as e:
                        why_off = 'the baselines left no readable recording (%s)' % exc_line(e)
                if why_off:
                    replay_on = False
                    fx_of.clear()
                    fx_meta.clear()
                    header.append('fixtures: replay OFF after the baselines: %s' % why_off)
                    fx_remove_store(store_dir)
                log(header[-1])
            accept_baseline(res, b2)
            state['phase'] = 'main'

            # ---- phase 2: controls and mutants ---------------------------------------------------------------------
            jobs_now[0] = jobs = mutant_jobs()
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
            jobs_now[0] = jobs = collections.deque()
            for n in [x for x in [c[0] for c in controls] + selected if x in suspects]:
                was = results.pop(n)
                history[n].append(('ran next to an outside writer', was))
                state['done'] -= 1
                fl = was.get('flags') or {}
                if fl.get('isolated'):                  # it touched the shared fixtures before: stays isolated
                    jobs.append(mk(kinds.get(n, 'mutant'), n, srcs[n], alone=True, fx=None, isolated=True,
                                   isolated_why=fl.get('isolated_why')))
                else:
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
        store_bad = fx_verify_store(store_dir, fx_meta) if fx_meta and os.path.isdir(store_dir) else []
        if not args.keep_work:
            fx_remove_store(store_dir)
            try:
                _rmtree_force(run_dir)
            except OSError:
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
    if b2 is not None:
        out.append(_line('baseline', 'BASELINE#2', b2, classify(b2, plan.family)[1]) + '  [fixture replay validation]')
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
    skipped_frac, skipped_s, fx_rep, fx_real, fx_jobs, n_iso = [], [], 0, 0, 0, 0
    G = (b or {}).get('n_guards') or 0
    T = (b or {}).get('guard_t') or []
    t_end = (b or {}).get('t_end')
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
        n_iso += bool(fl.get('isolated'))
        if res.get('enc_note'):
            enc_notes.append(n)
        out.append(_line('mutant', n, res, detail))
        if verdict == 'SURVIVED':
            survivors.append(n)
        elif verdict in ('TIMEOUT', 'ERROR', 'UNRESOLVED'):
            unresolved.append(n)
        k = res.get('kill_guard')
        if verdict == 'KILLED' and res.get('outcome') == 'killed' and k is not None and G:
            skipped_frac.append(max(0.0, (G - k - 1) / G))
            if t_end is not None and k < len(T):
                skipped_s.append(max(0.0, t_end - T[k]))
        fxr = res.get('fx')
        if fxr and fxr.get('mode') == 'replay':
            fx_jobs += 1
            fx_rep += fxr.get('replayed', 0)
            fx_real += fxr.get('real', 0)
    wall = time.time() - t_start
    cpu = sum(r.get('seconds', 0.0) for r in results.values()) + sum(x.get('seconds', 0.0) for x in (b, b2) if x)
    out.append('%d mutants: %d killed (%d by a crash of the suite), %d survived, %d unresolved (timeout / harness '
               'error / environment / not reproduced); %d confirmed by a rerun in a fresh process, %d rerun without '
               'the memo, %d rerun alone, %d rerun isolated (they touched the shared fixtures)'
               % (len(selected), rows['KILLED'], rows['crash'], rows['SURVIVED'], len(unresolved), rows['confirmed'],
                  rows['memo_rerun'], rows['alone'], n_iso))
    if controls:
        out.append('controls: %d of %d survived%s' % (len(controls) - len(bad_controls), len(controls),
                                                      (' - NOT SURVIVED: %s' % bad_controls) if bad_controls else ''))
    if skipped_frac:
        sf = sorted(skipped_frac)
        out.append('early exit: %d kill(s) ended at their first failing case; they skipped a median %.0f %% / mean '
                   '%.0f %% of the suite\'s %d checks%s' % (
                       len(sf), 100 * sf[len(sf) // 2], 100 * sum(sf) / len(sf), G,
                       (', about %.1f s of the baseline\'s suite time per job (%.0f s in all)'
                        % (sum(skipped_s) / len(skipped_s), sum(skipped_s))) if skipped_s else ''))
    if fx_jobs:
        out.append('fixture replay: %d job(s) replayed %d generator call(s) (%.1f per job), %d call(s) ran for real'
                   % (fx_jobs, fx_rep, fx_rep / fx_jobs, fx_real))
    store_problem = None
    if fx_notes['restored']:
        out.append('WARNING fixture store: the read-only mode was restored after %s' % fx_notes['restored'][:3])
    if fx_notes['changed'] or store_bad:
        store_problem = 'the shared fixture store changed during the run (%s%s)' % (
            fx_notes['changed'][:3], ('; final hashes: %s' % store_bad[:3]) if store_bad else '')
        out.append('STORE CHANGED: %s' % store_problem)
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
    if selection_note:
        extra += '; %s' % selection_note
    counts = '(%d of %d selected mutants killed; %d defined in the mutant script%s)' % (rows['KILLED'], len(selected),
                                                                                      n_defined, extra)
    if store_problem:
        out.append('NOT CERTIFIED (%s) %s' % (store_problem, counts))
    elif survivors:
        out.append('SURVIVORS: %s %s' % (survivors, counts))
    elif unresolved or bad_controls:
        out.append('NOT CERTIFIED (see UNRESOLVED / controls above) %s' % counts)
    else:
        out.append('ALL KILLED %s' % counts)
    text = '\n'.join(out)
    print('\n'.join(out[printed_header:]))
    if args.out:
        Path(args.out).write_text(text + '\n', encoding='utf-8')
    if store_problem:
        return 2
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
    if fl.get('isolated'):
        extra.append('rerun isolated in a fresh process without fixture replay: it touched the shared fixtures (%s)'
                     % short(fl.get('isolated_why') or '?', 90))
    if res.get('swallowed'):
        extra.append('the suite swallowed the early exit (it then ended: %s); the recorded kill stands'
                     % res['swallowed'])
    if res.get('enc_note'):
        extra.append('note: %s - the old harness would have crashed here' % res['enc_note'])
    if res.get('outside') and kind != 'baseline':
        extra.append('wrote outside its directory: %s' % short(res['outside'][:2], 100))
    s = '%s%s  %s  (%.1f s)' % (prefix, name, detail, res.get('seconds', 0.0))
    if extra:
        s += '  [%s]' % '; '.join(extra)
    return s


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--_job':
        _job_main(sys.argv[2], sys.argv[3])
    sys.exit(main())
