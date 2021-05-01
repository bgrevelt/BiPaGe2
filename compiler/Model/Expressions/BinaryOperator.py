from Model.Expressions.Expression import Expression

class BinaryOperator(Expression):
    def __init__(self, left:Expression, right:Expression):
        self._left = left
        self._right = right

    def Equals(self, other):
        if not isinstance(other, BinaryOperator):
            return False

        return self._left.Equals(other._left) and self._right.Equals(other._right)

    def _binary_evaluate(self, binary_function):
        evaluated_left = self._left.evaluate()
        evaluated_right = self._right.evaluate()
        if evaluated_left is None or evaluated_right is None:
            # One of the operands cannot be evaluated (e.g. it's value is not known until run time)
            return None
        else:
            return binary_function(evaluated_left, evaluated_right)