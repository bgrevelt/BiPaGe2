from Model.Expressions.BinaryOperator import BinaryOperator

class NotEqualsOperator(BinaryOperator):
    def __init__(self, left, right):
        super().__init__(left, right)

    def evaluate(self):
        self._binary_evaluate(lambda l, r: l != r)

    def Equals(self, other):
        return type(other) is NotEqualsOperator and super().Equals(other)

    def __str__(self):
        return f'({str(self._left)} != {str(self._right)})'