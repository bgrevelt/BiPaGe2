from abc import ABC, abstractmethod
from Model.Expressions.Expression import Expression
from Model.Expressions.BinaryOperator import BinaryOperator
from Model.Expressions.NumberLiteral import NumberLiteral
from Model.types import SignedInteger, UnsignedInteger

class RelationalOperator(BinaryOperator, ABC):
    def __init__(self, left:Expression, right:Expression, token=None):
        super().__init__(left, right, token)

    def evaluate(self):
        evaluated_left = self._left.evaluate()
        evaluated_right = self._right.evaluate()
        if type(evaluated_left) is not NumberLiteral or type(evaluated_right) is not NumberLiteral:
            # If both operands are number literals, we can compute the result of the relational operation
            # If not, one of the operands may (indirectly) contain a reference. In that case, we cannot evaluate
            # the value until run time.
            return self
        else:
            return self.compute(evaluated_left, evaluated_right)

    @abstractmethod
    def compute(self, left:NumberLiteral, right:NumberLiteral) -> bool:
        pass

    def check_semantics(self, warnings, errors):
        if super().check_semantics(warnings, errors):
            return

        # Comparing negative values to signed integer does not make sense
        if (self._left.return_type() == UnsignedInteger and type(self._right.evaluate()) == NumberLiteral and self._right.evaluate().value() < 0) or \
                (self._right.return_type() == UnsignedInteger and type(
                    self._left.evaluate()) == NumberLiteral and self._left.evaluate().value() < 0):
            self.add_message(f'Comparing unsigned value to a negative literal', errors)

        if self._left.return_type() not in [SignedInteger, UnsignedInteger]:
            self.add_message(f'Left hand operand {str(self._left)} does not resolve to integer', errors)
        if self._right.return_type() not in [SignedInteger, UnsignedInteger]:
            self.add_message(f'Right hand operand {str(self._left)} does not resolve to integer', errors)


    def return_type(self):
        # Relational operators always return booleans
        return bool