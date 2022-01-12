from Model.Expressions.BinaryOperator import BinaryOperator
from Model.Expressions.NumberLiteral import NumberLiteral
from Model.types import UnsignedInteger

class EqualityOperator(BinaryOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def check_semantics(self, warnings, errors):
        if super().check_semantics(warnings, errors):
            return

        # Comparing negative values to signed integer does not make sense
        if (self._left.return_type() == UnsignedInteger and type(
                self._right.evaluate()) == NumberLiteral and self._right.evaluate().value() < 0) or \
                (self._right.return_type() == UnsignedInteger and type(
                    self._left.evaluate()) == NumberLiteral and self._left.evaluate().value() < 0):
            self.add_message(f'Comparing unsigned value to a negative literal', errors)

        elif self._left.return_type() != self._right.return_type():
            self.add_message(f"Can't compare {self._left.return_type().__name__} to {self._right.return_type().__name__}", errors)

    def return_type(self):
        return bool