from Model.Expressions.ArithmeticOperator import ArithmeticOperator
from Model.Expressions.NumberLiteral import NumberLiteral

class DivisionOperator(ArithmeticOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is DivisionOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() / right.value()

    def check_semantics(self, warnings, errors):
        super().check_semantics(warnings, errors)
        self.add_message(f'Division operator {self.__str__()} may have in non-integer result. It depends on the target language how those results are handled.', warnings)

    def __str__(self):
        return f'({str(self._left)} / {str(self._right)})'