from Model.Expressions.RelationalOperator import RelationalOperator
from Model.Expressions.NumberLiteral import NumberLiteral

class LessThanOperator(RelationalOperator):
    def __init__(self, left, right):
        super().__init__(left, right)

    def Equals(self, other):
        return type(other) is LessThanOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() < right.value()

    def __str__(self):
        return f'({str(self._left)} < {str(self._right)})'