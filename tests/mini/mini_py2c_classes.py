# mini_py2c_classes_fixed.py
# Flow-sensitive, constraint-based type inference + C emitter
# Features: ints, floats, bools, unions, loops, IfExp, isinstance refinement,
#           classes -> C structs, comparison propagation, parameter reconciliation.

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
    # numeric promotion
    if (a == INT and b == FLOAT) or (a == FLOAT and b == INT):
        return FLOAT
    # class types unify only by same name; otherwise form a union (toy)
    if isinstance(a, TClass) and isinstance(b, TClass):
        return a if a.name == b.name else make_union(a, b)
    # unions
    if isinstance(a, TUnion) or isinstance(b, TUnion):
        return make_union(a, b)
    # bool vs int → int (for C)
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

        # 1) Collect class definitions (typed fields only)
        for node in m.body:
            if isinstance(node, ast.ClassDef):
                fields: Dict[str, Type] = {}
                for stmt in node.body:
                    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                        fields[stmt.target.id] = ann_to_type(stmt.annotation, self.class_defs)
                self.class_defs[node.name] = fields

        # 2) First function only
        fns = [n for n in m.body if isinstance(n, ast.FunctionDef)]
        if not fns:
            raise ValueError("No function found in source.")
        fn = fns[0]
        self._current_func = fn

        # Reset per-function
        self.env, self.returns, self.var_order, self.errors = {}, [], [], []

        # Seed parameters (annotations may be UNKNOWN)
        for a in fn.args.args:
            t = ann_to_type(a.annotation, self.class_defs)
            self.env[a.arg] = t
            self._remember_var(a.arg)

        # 3) Flow-sensitive inference on a copy of env
        end_env = self._infer_block(fn.body, dict(self.env))

        # 4) Return type = unify(all returns) ∧ annotation if present
        ret_t = UNKNOWN
        if self.returns:
            ret_t = self.returns[0]
            for t in self.returns[1:]:
                ret_t = unify(ret_t, t)
        if fn.returns is not None:
            ret_t = unify(ret_t, ann_to_type(fn.returns, self.class_defs))

        # 5) PARAMETER RECONCILIATION (the important fix)
        for name in list(self.env.keys()):
            t_start = self.env[name]
            t_end = end_env.get(name, UNKNOWN)
            if t_start == UNKNOWN and t_end != UNKNOWN:
                self.env[name] = t_end
            elif t_start != UNKNOWN and t_end != UNKNOWN:
                self.env[name] = unify(t_start, t_end)
            elif t_start == UNKNOWN and t_end == UNKNOWN:
                self.errors.append(f"Type of parameter '{name}' is still unknown.")

        # 6) Merge locals
        for k, v in end_env.items():
            if k not in self.env:
                self.env[k] = v

        if self.errors:
            raise TypeError("Inference errors:\n  " + "\n  ".join(self.errors))

        # 7) Emit C with typedef structs
        c_src = self.emit_c(fn.name, self.env, ret_t, fn.body)
        return c_src, self.env, ret_t

    # ---------- Flow-sensitive blocks & statements ----------

    def _infer_block(self, stmts: List[ast.stmt], in_env: Dict[str, Type]) -> Dict[str, Type]:
        env = dict(in_env)
        for s in stmts:
            env = self._infer_stmt(s, env)
        return env

    def _infer_stmt(self, s: ast.stmt, env: Dict[str, Type]) -> Dict[str, Type]:
        # Assign / attribute assign
        if isinstance(s, ast.Assign):
            if len(s.targets) != 1:
                self.errors.append("Only single-target assignments supported.")
                return env
            target = s.targets[0]
            t_rhs = self._infer_expr(s.value, env)
            if isinstance(target, ast.Name):
                env[target.id] = unify(env.get(target.id, UNKNOWN), t_rhs)
                self._remember_var(target.id)
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                obj = target.value.id
                field = target.attr
                base_t = env.get(obj, UNKNOWN)
                if isinstance(base_t, TClass):
                    fields = self.class_defs.get(base_t.name, {})
                    fields[field] = unify(fields.get(field, UNKNOWN), t_rhs)
                else:
                    self.errors.append(f"Attribute assignment on non-class value '{obj}'.")
            else:
                self.errors.append("Unsupported assignment target.")
            return env

        # Annotated assignment (name or obj.field)
        if isinstance(s, ast.AnnAssign):
            t_ann = ann_to_type(s.annotation, self.class_defs)
            if isinstance(s.target, ast.Name):
                name = s.target.id
                t_rhs = self._infer_expr(s.value, env) if s.value else UNKNOWN
                env[name] = unify(unify(env.get(name, UNKNOWN), t_ann), t_rhs)
                self._remember_var(name)
                return env
            if isinstance(s.target, ast.Attribute) and isinstance(s.target.value, ast.Name):
                obj = s.target.value.id
                field = s.target.attr
                base_t = env.get(obj, UNKNOWN)
                if isinstance(base_t, TClass):
                    t_rhs = self._infer_expr(s.value, env) if s.value else UNKNOWN
                    self.class_defs[base_t.name][field] = unify(self.class_defs[base_t.name].get(field, UNKNOWN),
                                                                unify(t_ann, t_rhs))
                    return env
            self.errors.append("Unsupported annotated assignment.")
            return env

        # Return
        if isinstance(s, ast.Return):
            t = self._infer_expr(s.value, env) if s.value else UNKNOWN
            self.returns.append(t)
            return env

        # If (with tiny const-prop and isinstance refinement)
        if isinstance(s, ast.If):
            # const = self._eval_const_bool(s.test)
            # then_env_seed, else_env_seed = self._env_with_isinstance_refinements(env, s.test)
            # _ = self._infer_expr(s.test, env)  # type the condition (may refine via compare)
            const = self._eval_const_bool(s.test)
            _ = self._infer_expr(s.test, env)  # propagate types from the test (e.g., y:int from y > 0)
            then_env_seed, else_env_seed = self._env_with_isinstance_refinements(env, s.test)
            if const is True:
                return self._infer_block(s.body, then_env_seed)
            if const is False:
                return self._infer_block(s.orelse, else_env_seed)
            then_env = self._infer_block(s.body, then_env_seed)
            else_env = self._infer_block(s.orelse, else_env_seed) if s.orelse else dict(env)
            keys = set(then_env) | set(else_env)
            return {k: unify(then_env.get(k, UNKNOWN), else_env.get(k, UNKNOWN)) for k in keys}

        # While: one body analysis + join
        if isinstance(s, ast.While):
            _ = self._infer_expr(s.test, env)
            body_env = self._infer_block(s.body, dict(env))
            keys = set(env) | set(body_env)
            return {k: unify(env.get(k, UNKNOWN), body_env.get(k, UNKNOWN)) for k in keys}

        # For i in range(...)
        if isinstance(s, ast.For):
            if isinstance(s.target, ast.Name) and isinstance(s.iter, ast.Call) and isinstance(s.iter.func, ast.Name) and s.iter.func.id == "range":
                ivar = s.target.id
                env[ivar] = INT
                self._remember_var(ivar)
                body_env = self._infer_block(s.body, dict(env))
                keys = set(env) | set(body_env)
                return {k: unify(env.get(k, UNKNOWN), body_env.get(k, UNKNOWN)) for k in keys}
            else:
                self.errors.append("Only 'for i in range(...)' is supported.")
                return env

        if isinstance(s, ast.Pass):
            return env

        self.errors.append(f"Unsupported statement: {type(s).__name__}")
        return env

    # ---------- Expression inference ----------

    def _infer_expr(self, e: ast.expr, env: Dict[str, Type]) -> Type:
        # Name
        if isinstance(e, ast.Name):
            return env.get(e.id, UNKNOWN)

        # Constants
        if isinstance(e, ast.Constant):
            if isinstance(e.value, bool): return BOOL
            if isinstance(e.value, int): return INT
            if isinstance(e.value, float): return FLOAT
            return UNKNOWN

        # Attribute read
        if isinstance(e, ast.Attribute) and isinstance(e.value, ast.Name):
            base = env.get(e.value.id, UNKNOWN)
            if isinstance(base, TClass):
                fields = self.class_defs.get(base.name, {})
                return fields.get(e.attr, UNKNOWN)
            return UNKNOWN

        # Unary +/- numeric
        if isinstance(e, ast.UnaryOp) and isinstance(e.op, (ast.UAdd, ast.USub)):
            t = self._infer_expr(e.operand, env)
            return unify(t, INT)

        # Binary ops (+, -, *, /, //)
        if isinstance(e, ast.BinOp):
            lt = self._infer_expr(e.left, env)
            rt = self._infer_expr(e.right, env)
            if isinstance(e.op, (ast.Add, ast.Sub, ast.Mult)):
                return unify(lt, rt)
            if isinstance(e.op, ast.Div):
                return FLOAT
            if isinstance(e.op, ast.FloorDiv):
                return INT
            return UNKNOWN

        # Comparisons: propagate types back into names
        if isinstance(e, ast.Compare):
            if len(e.ops) != 1 or len(e.comparators) != 1:
                return BOOL
            left, right = e.left, e.comparators[0]
            lt = self._infer_expr(left, env)
            rt = self._infer_expr(right, env)
            t_res = unify(lt, rt)
            if isinstance(left, ast.Name):
                env[left.id] = unify(env.get(left.id, UNKNOWN), t_res)
            if isinstance(right, ast.Name):
                env[right.id] = unify(env.get(right.id, UNKNOWN), t_res)
            return BOOL

        # Ternary (IfExp)
        if isinstance(e, ast.IfExp):
            _ = self._infer_expr(e.test, env)
            t_then = self._infer_expr(e.body, env)
            t_else = self._infer_expr(e.orelse, env)
            return unify(t_then, t_else)

        # Calls: isinstance / class ctor
        if isinstance(e, ast.Call) and isinstance(e.func, ast.Name):
            fname = e.func.id
            if fname == "isinstance":
                return BOOL
            if fname in self.class_defs and len(e.args) == 0 and len(e.keywords) == 0:
                return TClass(fname)

        return UNKNOWN

    # ---------- Refinements & helpers ----------

    def _eval_const_bool(self, e: ast.expr) -> Optional[bool]:
        if isinstance(e, ast.Constant) and isinstance(e.value, bool):
            return e.value
        return None

    def _env_with_isinstance_refinements(self, env: Dict[str, Type], test: ast.expr):
        """Return (then_env, else_env) applying isinstance refinements if test matches."""
        if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == "isinstance":
            if len(test.args) == 2 and isinstance(test.args[0], ast.Name):
                var = test.args[0].id
                typ = ann_to_type(test.args[1], self.class_defs)
                if typ != UNKNOWN:
                    then_env = dict(env)
                    then_env[var] = unify(env.get(var, UNKNOWN), typ)
                    else_env = dict(env)
                    old = env.get(var, UNKNOWN)
                    if isinstance(old, TUnion):
                        else_env[var] = make_union(*(t for t in old.options if t != typ))
                    elif old == typ:
                        else_env[var] = UNKNOWN
                    else:
                        else_env[var] = old
                    return then_env, else_env
        return dict(env), dict(env)

    def _remember_var(self, name: str):
        if name not in self.var_order:
            self.var_order.append(name)

    # ---------- C emission ----------

    def emit_c(self, fn_name: str, env: Dict[str, Type], ret_t: Type, body: List[ast.stmt]) -> str:
        def t2c(t: Type) -> str:
            if t == INT: return "int"
            if t == BOOL: return "int"
            if t == FLOAT: return "double"
            if isinstance(t, TClass): return t.name
            if isinstance(t, TUnion):
                if FLOAT in t.options: return "double"
                if INT in t.options: return "int"
                for o in t.options:
                    if isinstance(o, TClass): return o.name
                return "int"
            if t == UNKNOWN: return "int"
            return "int"

        # 1) Struct typedefs
        structs = []
        for cname, fields in self.class_defs.items():
            lines = [f"typedef struct {cname} {{"]
            for fname, ftype in fields.items():
                lines.append(f"    {t2c(ftype)} {fname};")
            lines.append(f"}} {cname};")
            structs.append("\n".join(lines))

        # 2) Signature
        params = [a.arg for a in self._current_func.args.args] if self._current_func else []
        c_params = [f"{t2c(env[p])} {p}" for p in params]
        c_ret = t2c(ret_t if ret_t != UNKNOWN else INT)

        # 3) Locals
        locals_ = [v for v in self.var_order if v not in params]
        decls = [f"    {t2c(env[v])} {v};" for v in locals_]

        # 4) Body
        c_body_lines: List[str] = []
        self._emit_block(body, c_body_lines, indent=1, env=env, t2c=t2c)

        out = []
        if structs:
            out.extend(structs)
            out.append("")
        out.append(f"{c_ret} {fn_name}({', '.join(c_params)}) "+"{")
        if decls: out.extend(decls)
        out.extend(c_body_lines)
        out.append("}")
        return "\n".join(out)

    def _emit_block(self, stmts: List[ast.stmt], out: List[str], indent: int, env: Dict[str, Type], t2c):
        ind = "    " * indent
        for s in stmts:
            if isinstance(s, ast.Assign):
                tgt = s.targets[0]
                if isinstance(tgt, ast.Name):
                    out.append(f"{ind}{tgt.id} = {self._emit_expr(s.value, env, t2c)};")
                elif isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name):
                    out.append(f"{ind}{tgt.value.id}.{tgt.attr} = {self._emit_expr(s.value, env, t2c)};")
                else:
                    out.append(f"{ind}/* unsupported assignment target */")
            elif isinstance(s, ast.AnnAssign):
                if isinstance(s.target, ast.Name) and s.value is not None:
                    out.append(f"{ind}{s.target.id} = {self._emit_expr(s.value, env, t2c)};")
                elif isinstance(s.target, ast.Attribute) and isinstance(s.target.value, ast.Name) and s.value is not None:
                    out.append(f"{ind}{s.target.value.id}.{s.target.attr} = {self._emit_expr(s.value, env, t2c)};")
            elif isinstance(s, ast.Return):
                if s.value:
                    out.append(f"{ind}return {self._emit_expr(s.value, env, t2c)};")
                else:
                    out.append(f"{ind}return;")
            elif isinstance(s, ast.If):
                cond = self._emit_expr(s.test, env, t2c)
                out.append(f"{ind}if ({cond}) "+"{")
                self._emit_block(s.body, out, indent+1, env, t2c)
                out.append(f"{ind}"+"}")
                if s.orelse:
                    out.append(f"{ind}else "+"{")
                    self._emit_block(s.orelse, out, indent+1, env, t2c)
                    out.append(f"{ind}"+"}")
            elif isinstance(s, ast.While):
                cond = self._emit_expr(s.test, env, t2c)
                out.append(f"{ind}while ({cond}) "+"{")
                self._emit_block(s.body, out, indent+1, env, t2c)
                out.append(f"{ind}"+"}")
            elif isinstance(s, ast.For):
                if isinstance(s.iter, ast.Call) and len(s.iter.args) >= 1:
                    ivar = s.target.id if isinstance(s.target, ast.Name) else "i"
                    start, stop, step = self._range_parts(s.iter, env, t2c)
                    out.append(f"{ind}for ({ivar} = {start}; (({step}) > 0 ? {ivar} < {stop} : {ivar} > {stop}); {ivar} += ({step})) "+"{")
                    self._emit_block(s.body, out, indent+1, env, t2c)
                    out.append(f"{ind}"+"}")
                else:
                    out.append(f"{ind}/* unsupported for-iter */")
            elif isinstance(s, ast.Pass):
                out.append(f"{ind}/* pass */")
            else:
                out.append(f"{ind}/* unsupported stmt: {type(s).__name__} */")

    def _range_parts(self, it: ast.expr, env: Dict[str, Type], t2c) -> Tuple[str, str, str]:
        if isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == "range":
            args = it.args
            if len(args) == 1:
                return "0", self._emit_expr(args[0], env, t2c), "1"
            if len(args) == 2:
                return self._emit_expr(args[0], env, t2c), self._emit_expr(args[1], env, t2c), "1"
            if len(args) == 3:
                return (self._emit_expr(args[0], env, t2c),
                        self._emit_expr(args[1], env, t2c),
                        self._emit_expr(args[2], env, t2c))
        return "0", "0", "1"

    def _emit_expr(self, e: ast.expr, env: Dict[str, Type], t2c) -> str:
        if isinstance(e, ast.Name): return e.id
        if isinstance(e, ast.Constant):
            if isinstance(e.value, bool): return "1" if e.value else "0"
            if isinstance(e.value, int): return str(e.value)
            if isinstance(e.value, float): return repr(float(e.value))
        if isinstance(e, ast.Attribute) and isinstance(e.value, ast.Name):
            return f"{e.value.id}.{e.attr}"
        if isinstance(e, ast.UnaryOp) and isinstance(e.op, (ast.UAdd, ast.USub)):
            return ("+" if isinstance(e.op, ast.UAdd) else "-") + self._emit_expr(e.operand, env, t2c)
        if isinstance(e, ast.BinOp):
            op_map = {ast.Add:"+", ast.Sub:"-", ast.Mult:"*", ast.Div:"/", ast.FloorDiv:"/"}
            sym = op_map.get(type(e.op), "?")
            return f"({self._emit_expr(e.left, env, t2c)} {sym} {self._emit_expr(e.right, env, t2c)})"
        if isinstance(e, ast.Compare) and len(e.ops)==1:
            cmp_map = {ast.Lt:"<", ast.LtE:"<=", ast.Gt:">", ast.GtE:">=", ast.Eq:"==", ast.NotEq:"!="}
            sym = cmp_map.get(type(e.ops[0]), "?")
            return f"({self._emit_expr(e.left, env, t2c)} {sym} {self._emit_expr(e.comparators[0], env, t2c)})"
        if isinstance(e, ast.IfExp):
            return f"({self._emit_expr(e.test, env, t2c)} ? {self._emit_expr(e.body, env, t2c)} : {self._emit_expr(e.orelse, env, t2c)})"
        if isinstance(e, ast.Call) and isinstance(e.func, ast.Name):
            fname = e.func.id
            if fname == "isinstance":
                return "/* isinstance */ 1"
            if fname in self.class_defs and len(e.args) == 0 and len(e.keywords) == 0:
                return f"({fname}){{0}}"  # zero-init
        return "0"

# ---------- Demo ----------

if __name__ == "__main__":
    tests = [
        # 1) Flow-sensitive inference on unannotated y
        """
def f(x: int, y):
    if y > 0:
        z = x + y
    else:
        z = x * y
    return z
""",
        # 2) For loop
        """
def sum_range(n: int):
    total = 0
    for i in range(n):
        total = total + i
    return total
""",
        # 3) isinstance refinement + IfExp ternary
        """
def area_or_abs(x, r: float):
    pi = 3.14159
    if isinstance(x, int):
        return x if x >= 0 else -x
    else:
        return pi * r * r
""",
        # 4) Classes → C structs
        """
class Point:
    x: int
    y: int

def make_point(px: int, py: int) -> Point:
    p = Point()
    p.x = px
    p.y = py
    return p
"""
    ]

    for idx, src in enumerate(tests, 1):
        print("="*72)
        print(f"Test {idx} Python source:\n{src.strip()}\n")
        inf = Inferencer()
        c_code, env, ret_t = inf.infer_function(src)
        print("Inferred env:", env)
        print("Return type:", ret_t)
        print("\nC output:\n")
        print(c_code)
        print()

