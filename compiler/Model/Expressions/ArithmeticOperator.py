from abc import ABC, abstractmethod
from Model.Expressions.BinaryOperator import BinaryOperator
from Model.Expressions.Expression import Expression
from Model.Expressions.NumberLiteral import NumberLiteral

class ArithmeticOperator(BinaryOperator, ABC):
    def __init__(self, left:Expression, right:Expression):
        super().__init__(left, right)

    def evaluate(self):
        if type(self._evaluated_left) is not NumberLiteral or type(self._evaluated_right) is not NumberLiteral:
            # If both operands are number literals, we can compute the number literal this operator will return
            # If not, one of the operands may (indirectly) contain a reference. In that case, we cannot evaluate
            # the value until run time.
            return self
        else:
            return NumberLiteral(self.compute(self._evaluated_left, self._evaluated_right))

    @abstractmethod
    def compute(self, left:NumberLiteral, right:NumberLiteral):
        pass