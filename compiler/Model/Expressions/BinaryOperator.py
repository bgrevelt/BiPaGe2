from Model.Expressions.Expression import Expression

class BinaryOperator(Expression):
    def __init__(self, left:Expression, right:Expression):
        self._left = left
        self._right = right
        self._evaluated_left = self._left.evaluate()
        self._evaluated_right = self._right.evaluate()

    def Equals(self, other):
        if not isinstance(other, BinaryOperator):
            return False

        return self._left.Equals(other._left) and self._right.Equals(other._right)