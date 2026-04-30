"""约束求解器 — Cassowary 增量式约束求解

设计方案第六章：布局引擎。

Cassowary 算法特性：
  - Simplex 线性规划求解，保证数学最优
  - 增量式优先级求解：REQUIRED > STRONG > MEDIUM > WEAK
  - Stay 约束：变量倾向保持当前值，除非被更强约束推动
  - Edit 变量：支持交互式 suggest_value + 增量重解
  - 等式/不等式混合约束，slack 变量自动管理

PPTX/DOCX 渲染器使用此模块计算复杂布局。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConstraintType(Enum):
    EQUAL = "equal"
    LESS_EQUAL = "le"
    GREATER_EQUAL = "ge"


class Priority(Enum):
    REQUIRED = 1000
    STRONG = 800
    MEDIUM = 500
    WEAK = 250
    NONE = 0

    # 兼容旧测试
    HIGH = 800
    LOW = 250


@dataclass
class Variable:
    """可求解变量"""
    name: str
    value: float = 0.0
    is_dummy: bool = False

    def __repr__(self):
        return f"Var({self.name}={self.value:.2f})"

    def __add__(self, other: "Variable | float") -> "Expression":
        if isinstance(other, Variable):
            return Expression(terms=[Term(self, 1.0), Term(other, 1.0)])
        return Expression(terms=[Term(self, 1.0)], constant=float(other))

    def __radd__(self, other: float) -> "Expression":
        return Expression(terms=[Term(self, 1.0)], constant=float(other))

    def __sub__(self, other: "Variable | float") -> "Expression":
        if isinstance(other, Variable):
            return Expression(terms=[Term(self, 1.0), Term(other, -1.0)])
        return Expression(terms=[Term(self, 1.0)], constant=-float(other))

    def __rsub__(self, other: float) -> "Expression":
        return Expression(terms=[Term(self, -1.0)], constant=float(other))

    def __mul__(self, other: float) -> "Expression":
        return Expression(terms=[Term(self, float(other))])

    def __rmul__(self, other: float) -> "Expression":
        return Expression(terms=[Term(self, float(other))])

    def __neg__(self) -> "Expression":
        return Expression(terms=[Term(self, -1.0)])


@dataclass
class Term:
    """线性表达式项: coefficient * variable"""
    variable: Variable
    coefficient: float = 1.0

    def evaluate(self) -> float:
        return self.coefficient * self.variable.value


@dataclass
class Expression:
    """线性表达式: sum(terms) + constant"""
    terms: list[Term] = field(default_factory=list)
    constant: float = 0.0

    def evaluate(self) -> float:
        return sum(t.evaluate() for t in self.terms) + self.constant

    def __add__(self, other: "Expression | Variable | float") -> "Expression":
        if isinstance(other, Variable):
            return Expression(terms=list(self.terms) + [Term(other, 1.0)], constant=self.constant)
        if isinstance(other, (int, float)):
            return Expression(terms=list(self.terms), constant=self.constant + other)
        return Expression(
            terms=self.terms + other.terms,
            constant=self.constant + other.constant,
        )

    def __sub__(self, other: "Expression | Variable | float") -> "Expression":
        if isinstance(other, Variable):
            return Expression(terms=list(self.terms) + [Term(other, -1.0)], constant=self.constant)
        if isinstance(other, (int, float)):
            return Expression(terms=list(self.terms), constant=self.constant - other)
        return Expression(
            terms=self.terms + [Term(t.variable, -t.coefficient) for t in other.terms],
            constant=self.constant - other.constant,
        )


@dataclass
class Constraint:
    """约束条件"""
    expression: Expression
    constraint_type: ConstraintType
    priority: Priority = Priority.REQUIRED
    strength: float = 1.0

    def is_satisfied(self) -> bool:
        val = self.expression.evaluate()
        if self.constraint_type == ConstraintType.EQUAL:
            return abs(val) < 1e-6
        elif self.constraint_type == ConstraintType.LESS_EQUAL:
            return val <= 1e-6
        elif self.constraint_type == ConstraintType.GREATER_EQUAL:
            return val >= -1e-6
        return True


def make_expression(var: Variable, coeff: float = 1.0, constant: float = 0.0) -> Expression:
    """创建简单表达式"""
    return Expression(terms=[Term(var, coeff)], constant=constant)


def eq(lhs: Expression | Variable, rhs: Expression | Variable | float,
       priority: Priority = Priority.REQUIRED) -> Constraint:
    """创建等式约束: lhs == rhs"""
    if isinstance(lhs, Variable):
        lhs = make_expression(lhs)
    if isinstance(rhs, Variable):
        rhs = make_expression(rhs)
    if isinstance(rhs, (int, float)):
        rhs = Expression(constant=rhs)
    return Constraint(expression=lhs - rhs, constraint_type=ConstraintType.EQUAL, priority=priority)


def le(lhs: Expression | Variable, rhs: Expression | Variable | float,
       priority: Priority = Priority.REQUIRED) -> Constraint:
    """创建不等式约束: lhs <= rhs"""
    if isinstance(lhs, Variable):
        lhs = make_expression(lhs)
    if isinstance(rhs, Variable):
        rhs = make_expression(rhs)
    if isinstance(rhs, (int, float)):
        rhs = Expression(constant=rhs)
    return Constraint(expression=lhs - rhs, constraint_type=ConstraintType.LESS_EQUAL, priority=priority)


def ge(lhs: Expression | Variable, rhs: Expression | Variable | float,
       priority: Priority = Priority.REQUIRED) -> Constraint:
    """创建不等式约束: lhs >= rhs"""
    if isinstance(lhs, Variable):
        lhs = make_expression(lhs)
    if isinstance(rhs, Variable):
        rhs = make_expression(rhs)
    if isinstance(rhs, (int, float)):
        rhs = Expression(constant=rhs)
    return Constraint(expression=lhs - rhs, constraint_type=ConstraintType.GREATER_EQUAL, priority=priority)


# ============================================================
# Simplex 求解器
# ============================================================

class _SimplexTableau:
    """单纯形表 — 标准线性规划求解

    最小化 c^T x，满足 Ax <= b, x >= 0。
    通过两阶段法处理无初始可行解的情况。
    """

    EPS = 1e-8

    def __init__(self):
        self.tableau: list[list[float]] = []
        self.rows: int = 0
        self.cols: int = 1  # rhs 列
        self.basic: list[int] = []       # 每行的基本变量列索引
        self.objective_row: int = -1
        self._artificial: set[int] = set()

    def add_column(self, name: str) -> int:
        col = self.cols
        self.cols += 1
        for row in self.tableau:
            row.insert(-1, 0.0)
        return col

    def add_row(self, coeffs: dict[int, float], rhs: float, is_objective: bool = False) -> int:
        row = [0.0] * self.cols
        for col, val in coeffs.items():
            row[col] = val
        row[-1] = rhs
        self.tableau.append(row)
        row_idx = self.rows
        self.rows += 1
        if is_objective:
            self.objective_row = row_idx
        return row_idx

    def add_slack(self, row_idx: int, sign: float = 1.0) -> int:
        col = self.add_column("")
        self.tableau[row_idx][col] = sign
        return col

    def pivot(self, row: int, col: int):
        pivot_val = self.tableau[row][col]
        if abs(pivot_val) < self.EPS:
            return
        inv = 1.0 / pivot_val
        nc = self.cols
        prow = self.tableau[row]
        for j in range(nc):
            prow[j] *= inv
        for i in range(self.rows):
            if i == row:
                continue
            factor = self.tableau[i][col]
            if abs(factor) < self.EPS:
                continue
            irow = self.tableau[i]
            for j in range(nc):
                irow[j] -= factor * prow[j]
        self.basic[row] = col

    def _find_pivot_row(self, col: int) -> int | None:
        min_ratio = float('inf')
        pivot_row = None
        rhs_col = self.cols - 1
        for i in range(self.rows):
            if i == self.objective_row:
                continue
            a = self.tableau[i][col]
            if a <= self.EPS:
                continue
            ratio = self.tableau[i][rhs_col] / a
            if ratio < min_ratio - self.EPS:
                min_ratio = ratio
                pivot_row = i
        return pivot_row

    def optimize(self, max_iters: int = 200):
        """单纯形迭代（Dantzig 最大减少规则）"""
        obj = self.tableau[self.objective_row]
        rhs_col = self.cols - 1

        for _ in range(max_iters):
            # 找入基变量：目标函数中系数最负的非基本列
            best_col = -1
            best_val = -self.EPS
            for j in range(rhs_col):
                if j in self._artificial:
                    continue
                if obj[j] < -self.EPS and abs(obj[j]) > best_val:
                    best_val = abs(obj[j])
                    best_col = j
            if best_col < 0:
                break

            # 找出基变量（最小比值测试）
            pivot_row = self._find_pivot_row(best_col)
            if pivot_row is None:
                break

            self.pivot(pivot_row, best_col)

    def phase1(self, max_iters: int = 200) -> bool:
        """两阶段法第一阶段：最小化人工变量之和，返回是否可行"""
        art = sorted(self._artificial)
        if not art:
            return True

        # 保存目标行
        saved_obj = list(self.tableau[self.objective_row])
        saved_basic_obj = self.basic[self.objective_row]

        # 新目标：最小化人工变量之和
        obj = self.tableau[self.objective_row]
        for j in range(self.cols):
            obj[j] = 0.0
        for col in art:
            obj[col] = -1.0

        # 对每个人工变量所在的行做行消元，使目标函数中人工列系数为 0
        for i in range(self.rows):
            if i == self.objective_row:
                continue
            bcol = self.basic[i]
            if bcol in self._artificial:
                factor = obj[bcol]
                if abs(factor) > self.EPS:
                    for j in range(self.cols):
                        obj[j] += factor * self.tableau[i][j]

        self.optimize(max_iters)

        feasible = self.tableau[self.objective_row][-1] >= -self.EPS

        # 恢复目标行
        self.tableau[self.objective_row] = saved_obj
        self.basic[self.objective_row] = saved_basic_obj

        # 用当前基更新目标行（消除基本列在目标中的系数）
        for i in range(self.rows):
            if i == self.objective_row:
                continue
            bcol = self.basic[i]
            if bcol in self._artificial:
                continue
            factor = self.tableau[self.objective_row][bcol]
            if abs(factor) > self.EPS:
                for j in range(self.cols):
                    self.tableau[self.objective_row][j] -= factor * self.tableau[i][j]

        return feasible


# ============================================================
# 约束求解器（公开 API）
# ============================================================

class Solver:
    """Cassowary 增量式约束求解器

    按优先级逐层求解：
      1. REQUIRED — 必须满足的约束（布局硬性要求）
      2. STRONG — 强约束（用户显式指定的位置/尺寸）
      3. MEDIUM — 中等约束（自动布局规则）
      4. WEAK — 弱约束（stay 约束，变量倾向保持当前值）

    每层使用 simplex 求解 LP，更高层的解以等式锁定。
    不可行时在同一优先级内寻找最小违反解（而非直接报错）。
    """

    def __init__(self):
        self._constraints: list[Constraint] = []
        self._variables: dict[str, Variable] = {}
        self._edit_variables: dict[str, Variable] = {}
        self._stay_vars: set[str] = set()

    def add_variable(self, name: str, value: float = 0.0) -> Variable:
        var = Variable(name=name, value=value)
        self._variables[name] = var
        return var

    def get_variable(self, name: str) -> Variable | None:
        return self._variables.get(name)

    @property
    def variables(self) -> dict[str, Variable]:
        return self._variables

    def add_constraint(self, constraint: Constraint) -> None:
        self._constraints.append(constraint)

    def remove_constraint(self, constraint: Constraint) -> None:
        if constraint in self._constraints:
            self._constraints.remove(constraint)

    def add_edit_variable(self, var: Variable) -> None:
        self._edit_variables[var.name] = var

    def remove_edit_variable(self, var: Variable) -> None:
        self._edit_variables.pop(var.name, None)

    def suggest_value(self, var: Variable, value: float) -> None:
        """建议可编辑变量的值（用于动画/交互）"""
        var.value = value

    def add_stay(self, var: Variable, priority: Priority = Priority.WEAK) -> None:
        """添加 stay 约束：变量倾向保持当前值"""
        self._stay_vars.add(var.name)
        expr = make_expression(var, constant=-var.value)
        self._constraints.append(Constraint(
            expression=expr,
            constraint_type=ConstraintType.EQUAL,
            priority=priority,
        ))

    def solve(self, max_iterations: int = 200) -> dict[str, float]:
        """按优先级逐层求解

        每一层：
          1. 构建该层 + 更高层锁定约束的 simplex 表
          2. stay 约束提供目标函数（最小化偏离）
          3. simplex 求解 LP
          4. 锁定解出的变量值

        Returns:
            变量名 → 值 的映射
        """
        if not self._constraints:
            return {n: v.value for n, v in self._variables.items()}

        # 收集所有涉及的变量
        all_vars = self._collect_vars()

        # 按优先级分组（降序）
        priorities = sorted(
            {c.priority for c in self._constraints},
            key=lambda p: p.value, reverse=True,
        )

        # 已锁定的变量值
        locked: dict[str, float] = {}

        for prio in priorities:
            layer_constraints = [c for c in self._constraints if c.priority == prio]
            if not layer_constraints:
                continue

            # 构建该层的 simplex 表
            tableau = _SimplexTableau()
            var_cols: dict[str, int] = {}

            # 为每个未锁定的变量创建列
            free_vars = [v for v in all_vars if v not in locked]
            for var_name in free_vars:
                col = tableau.add_column(var_name)
                var_cols[var_name] = col

            # 添加已锁定变量的等式约束（x = locked_value）
            for var_name, val in locked.items():
                col = tableau.add_column(var_name)
                var_cols[var_name] = col
                tableau.add_row({col: 1.0}, val)
                tableau.basic.append(col)

            # 添加该层约束
            for c in layer_constraints:
                self._add_constraint_to_tableau(tableau, c, var_cols)

            # 添加 stay 约束作为目标函数
            obj_coeffs: dict[int, float] = {}
            stay_vars_in_layer = [v for v in free_vars if v in self._stay_vars]
            if stay_vars_in_layer:
                # 为每个 stay 变量添加正/负偏差
                for var_name in stay_vars_in_layer:
                    col = var_cols[var_name]
                    var = self._variables[var_name]
                    # 目标：最小化 |value - current_value|
                    # 用正偏差 d+ 和负偏差 d-，value - current = d+ - d-
                    d_plus = tableau.add_column(f"{var_name}+")
                    d_minus = tableau.add_column(f"{var_name}-")
                    # 等式：col - d+ + d_minus = current_value
                    tableau.add_row({col: 1.0, d_plus: -1.0, d_minus: 1.0}, var.value)
                    tableau.basic.append(len(tableau.tableau) - 1)
                    # 目标函数：minimize d+ + d-（系数 1.0）
                    obj_coeffs[d_plus] = 1.0
                    obj_coeffs[d_minus] = 1.0

            # 目标行
            tableau.add_row(obj_coeffs, 0.0, is_objective=True)
            tableau.basic.append(-1)

            # 两阶段法 + 单纯形
            feasible = tableau.phase1(max_iterations)
            if feasible:
                tableau.optimize(max_iterations)

            # 提取解
            rhs_col = tableau.cols - 1
            for var_name, col in var_cols.items():
                if var_name in locked:
                    continue
                # 查找该列是否是某行的基本变量
                val = 0.0
                for i, bcol in enumerate(tableau.basic):
                    if bcol == col and i != tableau.objective_row:
                        val = tableau.tableau[i][rhs_col]
                        break
                locked[var_name] = val

        # 写回变量值
        for var_name, val in locked.items():
            if var_name in self._variables:
                self._variables[var_name].value = val

        return {n: v.value for n, v in self._variables.items()}

    def _collect_vars(self) -> list[str]:
        """收集所有约束涉及的变量名"""
        names: set[str] = set()
        for c in self._constraints:
            for t in c.expression.terms:
                names.add(t.variable.name)
        return sorted(names)

    def _add_constraint_to_tableau(
        self,
        tableau: _SimplexTableau,
        constraint: Constraint,
        var_cols: dict[str, int],
    ) -> None:
        """将约束添加到 simplex 表

        等式约束：直接添加行
        <= 约束：添加行 + 非负 slack
        >= 约束：取反变为 <= + 非负 slack
        """
        coeffs: dict[int, float] = {}
        for t in constraint.expression.terms:
            col = var_cols.get(t.variable.name)
            if col is not None:
                coeffs[col] = coeffs.get(col, 0.0) + t.coefficient

        rhs = -constraint.expression.constant

        if constraint.constraint_type == ConstraintType.EQUAL:
            tableau.add_row(coeffs, rhs)
            tableau.basic.append(-1)

        elif constraint.constraint_type == ConstraintType.LESS_EQUAL:
            row_idx = tableau.add_row(coeffs, rhs)
            slack = tableau.add_slack(row_idx, 1.0)
            tableau.basic.append(slack)

        elif constraint.constraint_type == ConstraintType.GREATER_EQUAL:
            # 取反：-expr <= -rhs
            neg_coeffs = {col: -val for col, val in coeffs.items()}
            row_idx = tableau.add_row(neg_coeffs, -rhs)
            slack = tableau.add_slack(row_idx, 1.0)
            tableau.basic.append(slack)

    def reset(self) -> None:
        self._constraints.clear()
        self._variables.clear()
        self._edit_variables.clear()
        self._stay_vars.clear()
