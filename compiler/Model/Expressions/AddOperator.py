from Model.Expressions.ArithmeticOperator import ArithmeticOperator
from Model.Expressions.NumberLiteral import NumberLiteral

class AddOperator(ArithmeticOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is AddOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() + right.value()


    def __str__(self):
        return f'({str(self._left)} + {str(self._right)})'