from Model.Expressions.EqualityOperator import EqualityOperator
from Model.Expressions.NumberLiteral import NumberLiteral

class NotEqualsOperator(EqualityOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

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

    # def check_semantics(self, warnings, errors):
    #     #TODO: same as equalsoperator and relationaloperator. We need a common base class
    #     # Comparing negative values to signed integer does not make sense
    #     if (self._left.return_type() == UnsignedInteger and type(
    #             self._right.evaluate()) == NumberLiteral and self._right.evaluate().value() < 0) or \
    #             (self._right.return_type() == UnsignedInteger and type(
    #                 self._left.evaluate()) == NumberLiteral and self._left.evaluate().value() < 0):
    #         self.add_message(f'Comparing unsigned value to a negative literal', errors)
    #
    # def return_type(self):
    #     return bool

    def __str__(self):
        return f'({str(self._left)} != {str(self._right)})'