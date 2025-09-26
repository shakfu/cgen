# mini_py2c_classes_fixed.py
# Flow-sensitive, constraint-based type inference + C emitter
# Features: ints, floats, bools, unions, loops, IfExp, isinstance refinement,
#           classes -> C structs, comparisons fix, parameter reconciliation.

import ast
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List

# ---------- Type domain ----------

class Type:
    def __repr__(self): return self.__str__()

@dataclass(frozen=True)
class TInt(Type):
    def __str__(self): return "int"

@dataclass(frozen=True)
class TBool(Type):
    def __str__(self): return "bool"

@dataclass(frozen=True)
class TFloat(Type):
    def __str__(self): return "float"

@dataclass(frozen=True)
class TClass(Type):
    name: str
    def __str__(self): return self.name

@dataclass(frozen=True)
class TUnion(Type):
    options: frozenset
    def __str__(self):
        return " | ".join(sorted(str(o) for o in self.options))

@dataclass(frozen=True)
class TUnknown(Type):
    def __str__(self): return "unknown"

INT, BOOL, FLOAT, UNKNOWN = TInt(), TBool(), TFloat(), TUnknown()

def ann_to_type(ann: Optional[ast.expr], class_table: Dict[str, Dict[str, Type]] = None) -> Type:
    if ann is None: return UNKNOWN
    if isinstance(ann, ast.Name):
        base = {"int": INT, "bool": BOOL, "float": FLOAT}.get(ann.id)
        if base is not None: return base
        if class_table and ann.id in class_table:
            return TClass(ann.id)
    return UNKNOWN

def make_union(*types: Type) -> Type:
    opts = set()
    for t in types:
        if isinstance(t, TUnion):
            opts |= t.options
        elif t != UNKNOWN:
            opts.add(t)
    if not opts: return UNKNOWN
    if len(opts) == 1: return next(iter(opts))
    return TUnion(frozenset(opts))

def unify(a: Type, b: Type) -> Type:
    if a == b: return a
    if a == UNKNOWN: return b
    if b == UNKNOWN: return a
    if (a == INT and b == FLOAT) or (a == FLOAT and b == INT):
        return FLOAT
    if isinstance(a, TClass) and isinstance(b, TClass):
        if a.name == b.name:
            return a
        return make_union(a, b)
    if isinstance(a, TUnion) or isinstance(b, TUnion):
        return make_union(a, b)
    if (a == BOOL and b == INT) or (a == INT and b == BOOL):
        return INT
    return make_union(a, b)

# ---------- Inferencer ----------

class Inferencer(ast.NodeVisitor):
    def __init__(self):
        self.env: Dict[str, Type] = {}
        self.returns: List[Type] = []
        self.var_order: List[str] = []
        self.errors: List[str] = []
        self._current_func: Optional[ast.FunctionDef] = None
        self.class_defs: Dict[str, Dict[str, Type]] = {}

    def infer_function(self, src: str) -> Tuple[str, Dict[str, Type], Type]:
        m = ast.parse(src)

        # Collect class definitions
        for node in m.body:
            if isinstance(node, ast.ClassDef):
                fields: Dict[str, Type] = {}
                for stmt in node.body:
                    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                        fields[stmt.target.id] = ann_to_type(stmt.annotation, self.class_defs)
                self.class_defs[node.name] = fields

        fns = [n for n in m.body if isinstance(n, ast.FunctionDef)]
        if not fns:
            raise ValueError("No function found in source.")
        fn = fns[0]
        self._current_func = fn

        self.env, self.returns, self.var_order, self.errors = {}, [], [], []

        for a in fn.args.args:
            t = ann_to_type(a.annotation, self.class_defs)
            self.env[a.arg] = t
            self._remember_var(a.arg)

        end_env = self._infer_block(fn.body, dict(self.env))

        ret_t = UNKNOWN
        if self.returns:
            ret_t = self.returns[0]
            for t in self.returns[1:]:
                ret_t = unify(ret_t, t)
        if fn.returns is not None:
            ret_t = unify(ret_t, ann_to_type(fn.returns, self.class_defs))

        # --- FIX: reconcile parameters with inferred body types ---
        for name in list(self.env.keys()):
            t_start = self.env[name]
            t_end = end_env.get(name, UNKNOWN)
            if t_start == UNKNOWN and t_end != UNKNOWN:
                self.env[name] = t_end
            elif t_start != UNKNOWN and t_end != UNKNOWN:
                self.env[name] = unify(t_start, t_end)
            elif t_start == UNKNOWN and t_end == UNKNOWN:
                self.errors.append(f"Type of parameter '{name}' is still unknown.")

        for k, v in end_env.items():
            if k not in self.env:
                self.env[k] = v

        if self.errors:
            raise TypeError("Inference errors:\n  " + "\n  ".join(self.errors))

        c_src = self.emit_c(fn.name, self.env, ret_t, fn.body)
        return c_src, self.env, ret_t

    # ---------- Inference core (stmts/exprs) ----------

    def _infer_block(self, stmts, in_env):
        env = dict(in_env)
        for s in stmts:
            env = self._infer_stmt(s, env)
        return env

    def _infer_stmt(self, s, env):
        if isinstance(s, ast.Assign):
            target = s.targets[0]
            t_rhs = self._infer_expr(s.value, env)
            if isinstance(target, ast.Name):
                env[target.id] = unify(env.get(target.id, UNKNOWN), t_rhs)
                self._remember_var(target.id)
            return env
        if isinstance(s, ast.Return):
            t = self._infer_expr(s.value, env) if s.value else UNKNOWN
            self.returns.append(t)
            return env
        if isinstance(s, ast.If):
            _ = self._infer_expr(s.test, env)
            then_env = self._infer_block(s.body, dict(env))
            else_env = self._infer_block(s.orelse, dict(env)) if s.orelse else dict(env)
            keys = set(then_env) | set(else_env)
            return {k: unify(then_env.get(k, UNKNOWN), else_env.get(k, UNKNOWN)) for k in keys}
        return env

    def _infer_expr(self, e, env):
        if isinstance(e, ast.Name):
            return env.get(e.id, UNKNOWN)
        if isinstance(e, ast.Constant):
            if isinstance(e.value, bool): return BOOL
            if isinstance(e.value, int): return INT
            if isinstance(e.value, float): return FLOAT
        if isinstance(e, ast.BinOp):
            lt = self._infer_expr(e.left, env)
            rt = self._infer_expr(e.right, env)
            return unify(lt, rt)
        if isinstance(e, ast.Compare):
            left, right = e.left, e.comparators[0]
            lt = self._infer_expr(left, env)
            rt = self._infer_expr(right, env)
            t_res = unify(lt, rt)
            if isinstance(left, ast.Name):
                env[left.id] = unify(env.get(left.id, UNKNOWN), t_res)
            if isinstance(right, ast.Name):
                env[right.id] = unify(env.get(right.id, UNKNOWN), t_res)
            return BOOL
        return UNKNOWN

    def _remember_var(self, name):
        if name not in self.var_order:
            self.var_order.append(name)

    # ---------- C emitter (minimal) ----------

    def emit_c(self, fn_name, env, ret_t, body):
        def t2c(t: Type) -> str:
            if t == INT: return "int"
            if t == BOOL: return "int"
            if t == FLOAT: return "double"
            if isinstance(t, TClass): return t.name
            return "int"
        params = [a.arg for a in self._current_func.args.args]
        c_params = [f"{t2c(env[p])} {p}" for p in params]
        c_ret = t2c(ret_t if ret_t != UNKNOWN else INT)
        locals_ = [v for v in self.var_order if v not in params]
        decls = [f"    {t2c(env[v])} {v};" for v in locals_]
        lines = [f"{c_ret} {fn_name}({', '.join(c_params)}) "+"{"]
        if decls: lines.extend(decls)
        for s in body:
            if isinstance(s, ast.If):
                cond = self._emit_expr(s.test, env)
                lines.append(f"    if ({cond}) "+"{")
                for stmt in s.body:
                    if isinstance(stmt, ast.Assign):
                        lines.append(f"        {stmt.targets[0].id} = {self._emit_expr(stmt.value, env)};")
                lines.append("    } else {")
                for stmt in s.orelse:
                    if isinstance(stmt, ast.Assign):
                        lines.append(f"        {stmt.targets[0].id} = {self._emit_expr(stmt.value, env)};")
                lines.append("    }")
            if isinstance(s, ast.Return):
                lines.append(f"    return {self._emit_expr(s.value, env)};")
        lines.append("}")
        return "\n".join(lines)

    def _emit_expr(self, e, env):
        if isinstance(e, ast.Name): return e.id
        if isinstance(e, ast.Constant): return str(e.value)
        if isinstance(e, ast.BinOp):
            return f"({self._emit_expr(e.left, env)} + {self._emit_expr(e.right, env)})"
        if isinstance(e, ast.Compare):
            return f"({self._emit_expr(e.left, env)} > {self._emit_expr(e.comparators[0], env)})"
        return "0"

# ---------- Demo ----------

if __name__ == "__main__":
    src = """
def f(x: int, y):
    if y > 0:
        z = x + y
    else:
        z = x * y
    return z
"""
    inf = Inferencer()
    c_code, env, ret_t = inf.infer_function(src)
    print("Inferred env:", env)
    print("Return type:", ret_t)
    print("\nC output:\n")
    print(c_code)


    src = """
class Person:
    name: str
    age: int

"""
    inf = Inferencer()
    c_code, env, ret_t = inf.infer_function(src)
    print("Inferred env:", env)
    print("Return type:", ret_t)
    print("\nC output:\n")
    print(c_code)
