from abc import ABC, abstractmethod
from Model.Expressions.Expression import Expression
from Model.Expressions.BinaryOperator import BinaryOperator
from Model.Expressions.NumberLiteral import NumberLiteral

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
        # both operands should resolve to boolean values
        # we can only check that if both operands are semantically valid
        previous_error_count = len(errors)
        self._left.check_semantics(warnings, errors)
        self._right.check_semantics(warnings, errors)
        if len(errors) > previous_error_count:
            return
        else:
            if self._left.return_type() != 'integer':
                self.add_message(f'Left hand operand {str(self._left)} does not resolve to integer', errors)
            if self._right.return_type() != 'integer':
                self.add_message(f'Right hand operand {str(self._left)} does not resolve to integer', errors)


    def return_type(self):
        # Relational operators always return booleans
        return 'boolean'