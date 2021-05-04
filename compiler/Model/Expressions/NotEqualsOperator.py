from Model.Expressions.BinaryOperator import BinaryOperator
from Model.Expressions.NumberLiteral import NumberLiteral

class NotEqualsOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__(left, right)

    #todo: This is more or less a duplicate of the EqualsOperator
    def evaluate(self):
        if type(self._evaluated_left) is NumberLiteral and type(self._evaluated_right) is NumberLiteral:
            # both operands are number literals. We can resolve this
            return not self._evaluated_left.Equals(self._evaluated_right)

        if type(self._evaluated_left) is bool and type(self._evaluated_right) is bool:
            # both operands are booleans. We can resolve this
            return not self._evaluated_left.Equals(self._evaluated_right)

        # There are theoretically cases we could resolve as well. For example
        # some_field + 1 == 1 + some_field will always be true
        # but we'll just leave the tough stuff up to the compiler/interpreter for the output language
        return self

    def Equals(self, other):
        return type(other) is NotEqualsOperator and super().Equals(other)

    def __str__(self):
        return f'({str(self._left)} != {str(self._right)})'