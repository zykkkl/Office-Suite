"""约束求解器 — Cassowary 算法的简化实现

设计方案第六章：布局引擎。

Cassowary 是一种增量式约束求解算法，用于解决线性等式和不等式约束系统。
同 iOS AutoLayout 使用的算法。

本模块实现简化版本：
  - 变量（Variable）：可求解的数值
  - 约束（Constraint）：等式 / 不等式
  - 求解器（Solver）：维护约束集合并求解

PPTX/DOCX 渲染器使用此模块计算复杂布局。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConstraintType(Enum):
    EQUAL = "equal"          # ==
    LESS_EQUAL = "le"        # <=
    GREATER_EQUAL = "ge"     # >=


class Priority(Enum):
    REQUIRED = 1000
    HIGH = 750
    MEDIUM = 500
    LOW = 250
    NONE = 0


@dataclass
class Variable:
    """可求解变量"""
    name: str
    value: float = 0.0
    is_dummy: bool = False

    def __repr__(self):
        return f"Var({self.name}={self.value:.2f})"


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

    def __add__(self, other: "Expression | float") -> "Expression":
        if isinstance(other, (int, float)):
            return Expression(terms=list(self.terms), constant=self.constant + other)
        return Expression(
            terms=self.terms + other.terms,
            constant=self.constant + other.constant,
        )

    def __sub__(self, other: "Expression | float") -> "Expression":
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
    return Constraint(
        expression=lhs - rhs,
        constraint_type=ConstraintType.EQUAL,
        priority=priority,
    )


def le(lhs: Expression | Variable, rhs: Expression | Variable | float,
       priority: Priority = Priority.REQUIRED) -> Constraint:
    """创建不等式约束: lhs <= rhs"""
    if isinstance(lhs, Variable):
        lhs = make_expression(lhs)
    if isinstance(rhs, Variable):
        rhs = make_expression(rhs)
    if isinstance(rhs, (int, float)):
        rhs = Expression(constant=rhs)
    return Constraint(
        expression=lhs - rhs,
        constraint_type=ConstraintType.LESS_EQUAL,
        priority=priority,
    )


def ge(lhs: Expression | Variable, rhs: Expression | Variable | float,
       priority: Priority = Priority.REQUIRED) -> Constraint:
    """创建不等式约束: lhs >= rhs"""
    if isinstance(lhs, Variable):
        lhs = make_expression(lhs)
    if isinstance(rhs, Variable):
        rhs = make_expression(rhs)
    if isinstance(rhs, (int, float)):
        rhs = Expression(constant=rhs)
    return Constraint(
        expression=lhs - rhs,
        constraint_type=ConstraintType.GREATER_EQUAL,
        priority=priority,
    )


class Solver:
    """约束求解器

    使用简化的增量求解策略：
    1. 按优先级排序约束
    2. 对等式约束直接求解
    3. 对不等式约束通过迭代调整满足

    注意：这是 Cassowary 的简化实现，适合文档布局场景。
    完整 Cassowary 实现需要 simplex 求解器。
    """

    def __init__(self):
        self._constraints: list[Constraint] = []
        self._variables: dict[str, Variable] = {}
        self._edit_variables: dict[str, Variable] = {}

    def add_variable(self, name: str, value: float = 0.0) -> Variable:
        """添加变量"""
        var = Variable(name=name, value=value)
        self._variables[name] = var
        return var

    def get_variable(self, name: str) -> Variable | None:
        """获取变量"""
        return self._variables.get(name)

    def add_constraint(self, constraint: Constraint) -> None:
        """添加约束"""
        self._constraints.append(constraint)

    def remove_constraint(self, constraint: Constraint) -> None:
        """移除约束"""
        if constraint in self._constraints:
            self._constraints.remove(constraint)

    def add_edit_variable(self, var: Variable) -> None:
        """添加可编辑变量（用于动画/交互）"""
        self._edit_variables[var.name] = var

    def suggest_value(self, var: Variable, value: float) -> None:
        """建议可编辑变量的值"""
        var.value = value

    def solve(self, max_iterations: int = 100) -> dict[str, float]:
        """求解所有约束

        策略：
        1. 按优先级降序排列约束
        2. 对等式约束：直接设置变量值
        3. 对不等式约束：迭代调整直到满足

        Returns:
            变量名 → 值 的映射
        """
        # 按优先级排序
        sorted_constraints = sorted(
            self._constraints,
            key=lambda c: c.priority.value,
            reverse=True,
        )

        # 第一轮：处理等式约束
        for c in sorted_constraints:
            if c.constraint_type == ConstraintType.EQUAL:
                self._solve_equality(c)

        # 第二轮：迭代处理不等式约束
        for _ in range(max_iterations):
            all_satisfied = True
            for c in sorted_constraints:
                if c.constraint_type != ConstraintType.EQUAL:
                    if not c.is_satisfied():
                        all_satisfied = False
                        self._adjust_inequality(c)
            if all_satisfied:
                break

        return {name: var.value for name, var in self._variables.items()}

    def _solve_equality(self, constraint: Constraint) -> None:
        """求解等式约束"""
        expr = constraint.expression
        if not expr.terms:
            return

        # 单变量等式：直接求解
        if len(expr.terms) == 1:
            term = expr.terms[0]
            term.variable.value = -expr.constant / term.coefficient
            return

        # 多变量等式：设第一个变量为求解目标
        target = expr.terms[0]
        other_sum = sum(t.evaluate() for t in expr.terms[1:])
        target.variable.value = -(expr.constant + other_sum) / target.coefficient

    def _adjust_inequality(self, constraint: Constraint) -> None:
        """调整变量以满足不等式约束"""
        expr = constraint.expression
        if not expr.terms:
            return

        violation = expr.evaluate()
        if constraint.constraint_type == ConstraintType.LESS_EQUAL and violation > 0:
            # 需要减小表达式的值
            adjustment = -violation / len(expr.terms)
            for term in expr.terms:
                term.variable.value += adjustment / term.coefficient
        elif constraint.constraint_type == ConstraintType.GREATER_EQUAL and violation < 0:
            # 需要增大表达式的值
            adjustment = -violation / len(expr.terms)
            for term in expr.terms:
                term.variable.value += adjustment / term.coefficient

    def reset(self) -> None:
        """重置求解器"""
        self._constraints.clear()
        self._variables.clear()
        self._edit_variables.clear()
