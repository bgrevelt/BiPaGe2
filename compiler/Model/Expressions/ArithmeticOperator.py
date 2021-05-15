from abc import ABC, abstractmethod
from Model.Expressions.BinaryOperator import BinaryOperator
from Model.Expressions.Expression import Expression
from Model.Expressions.NumberLiteral import NumberLiteral
from Model.Types.Integer import Integer

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

    def check_semantics(self, warnings, errors):
       #TODO
        pass

    def return_type(self):
        # Arithmatic operations only support integer type operands, so the return type is always integer
        return Integer

    @abstractmethod
    def compute(self, left:NumberLiteral, right:NumberLiteral):
        pass