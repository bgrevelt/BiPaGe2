from abc import ABC, abstractmethod
from Model.Expressions.BinaryOperator import BinaryOperator
from Model.Expressions.Expression import Expression
from Model.Expressions.NumberLiteral import NumberLiteral
from Model.Types.Integer import Integer
from Model.Types.Float import Float

class ArithmeticOperator(BinaryOperator, ABC):
    def __init__(self, left:Expression, right:Expression, token):
        super().__init__(left, right, token)

    def evaluate(self):
        if type(self._evaluated_left) is not NumberLiteral or type(self._evaluated_right) is not NumberLiteral:
            # If both operands are number literals, we can compute the number literal this operator will return
            # If not, one of the operands may (indirectly) contain a reference. In that case, we cannot evaluate
            # the value until run time.
            self._left = self._evaluated_left
            self._right = self._evaluated_right
            return self
        else:
            return NumberLiteral(self.compute(self._evaluated_left, self._evaluated_right), self._token)

    # Arithmetic expressions can only be applied to integer and/or floating point operands. Note that we support
    # floats in the operand because it is mathematically valid, but since we can only use expressions to size collections
    # and we can only size collections with an integer value, there really is no valid use case for using floating points
    # in an expression
    def check_semantics(self, warnings, errors):
        initial_error_count = len(errors)
        self._left.check_semantics(warnings, errors)
        self._right.check_semantics(warnings, errors)
        if initial_error_count < len(errors):
            return

        # Operands should be integer or floating point
        if self._left.return_type() not in [Float, Integer]:
            self.add_message(f'Left hand operand ({str(self._left)}) does not resolve to integer or float', errors)
        if self._right.return_type() not in [Float, Integer]:
            self.add_message(f'Right hand operand ({str(self._right)}) does not resolve to integer or float', errors)

    def return_type(self):
        # If either one of the operands is a float, the result will be considered a float
        if self._left.return_type() is Float or self._right.return_type() is Float:
            return Float
        else:
            # if the operand is semantically valid, the operands will both be integers, so the result type will be an
            # integer as well
            return Integer

    @abstractmethod
    def compute(self, left:NumberLiteral, right:NumberLiteral):
        pass