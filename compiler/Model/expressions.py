from abc import ABC, abstractmethod
from Model.types import SignedInteger, UnsignedInteger, Float
from Model.Node import Node

class Expression(Node, ABC):
    def __init__(self, token):
        super().__init__(token)

    @abstractmethod
    def check_semantics(self, warnings, errors):
       pass

    @abstractmethod
    def return_type(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass

    # Used for testing. Test if the expression matches other
    @abstractmethod
    def Equals(self, other):
        pass

class NumberLiteral(Expression):
    def __init__(self, number, token = None):
        super().__init__(token)
        self._number = number

    def evaluate(self):
        # nothing to evaluate, we're just a number literal
        return self

    def value(self):
        return self._number

    def Equals(self, other):
        return type(other) is NumberLiteral and other._number == self._number

    def check_semantics(self, warnings, errors):
        #Nothing to check for a number literal
        return False

    def return_type(self):
        if self._number < 0:
            return SignedInteger
        else:
            return UnsignedInteger

    def __str__(self):
        return str(self._number)

class Reference(Expression):
    def __init__(self, name, referenced_type, token):
        super().__init__(token)
        self._name = name
        self._referenced_type = referenced_type

    def size_in_bits(self):
        return self._referenced_type.size_in_bits()

    def signed(self):
        return self._referenced_type.signed()

    def referenced_type(self):
        return self._referenced_type

    def name(self):
        return self._name

    def check_semantics(self, warnings, errors):
        return False

    def evaluate(self):
        return self

class FieldReference(Reference):
    def __init__(self, name, referenced_type, token):
        super().__init__(name, referenced_type, token)

    def Equals(self, other):
        return type(other) == FieldReference and self._name == other.name() and self._referenced_type.Equals(other.referenced_type())

    def return_type(self):
        from Model.Field import Field
        if type(self.referenced_type()) is Field:
            if type(self.referenced_type().type()) in [FieldReference, EnumerationReference]:
                return self.referenced_type().type().return_type()
            else:
                return type(self.referenced_type().type())
        else:
            return self.referenced_type()

    def __str__(self):
        return self._name

class EnumerationReference(Reference):
    def __init__(self, name, referenced_type, token):
        super().__init__(name, referenced_type, token)

    def Equals(self, other):
        return type(other) is EnumerationReference and self.name() != other.name() and self._referenced_type.Equals(other.referenced_type())

    def return_type(self):
        return self.referenced_type()

class DataTypeReference(Reference):
    def __init__(self, name, referenced_type, token):
        super().__init__(name, referenced_type, token)

    def Equals(self, other):
        return type(other) is DataTypeReference and self.name() == other.name() and self._referenced_type.Equals(other.referenced_type())

    def return_type(self):
        return self.referenced_type()


class EnumeratorReference(Reference):
    def __init__(self, identifier:str, parent, token):
        super().__init__(identifier, parent, token)

    def identifier(self):
        return self._name

    def fully_qualified_name(self):
        return f'{self._referenced_type._name}.{self._name}'

    def parent(self):
        return self._referenced_type

    def Equals(self, other):
        return type(other) is EnumeratorReference and self._name() == other.identifier() and self._referenced_type == other.parent()

    def return_type(self):
        return self._referenced_type

# Fake reference we use to put a reference object in the model when we can't figure out what is referenced during parsing
# That means that the input is not semantically valid, but we still want to create a model
class NullReference(Reference):
    def __init__(self, identifier:str, token):
        super().__init__(identifier, None, token)

    def identifier(self):
        return self._name

    def check_semantics(self, warnings, errors):
        self.add_message(f'Reference "{self._name}" cannot be resolved', errors)
        return True

    def Equals(self, other):
        return type(other) == NullReference and self._name == other.identifier()

    def return_type(self):
        return None

    def size_in_bits(self):
        return 8

class BinaryOperator(Expression):
    def __init__(self, left:Expression, right:Expression, token):
        super().__init__(token)
        self._left = left
        self._right = right
        self._evaluated_left = self._left.evaluate()
        self._evaluated_right = self._right.evaluate()

    def Equals(self, other):
        if not isinstance(other, BinaryOperator):
            return False

        return self._left.Equals(other._left) and self._right.Equals(other._right)

    def check_semantics(self, warnings, errors):
        inital_error_count = len(errors)
        self._left.check_semantics(warnings, errors)
        self._right.check_semantics(warnings, errors)
        return len(errors) > inital_error_count

    def left(self):
        return self._left

    def right(self):
        return self._right

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
            return True

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

class EqualityOperator(BinaryOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def check_semantics(self, warnings, errors):
        if super().check_semantics(warnings, errors):
            return True

        # Comparing negative values to signed integer does not make sense
        if (self._left.return_type() == UnsignedInteger and type(
                self._right.evaluate()) == NumberLiteral and self._right.evaluate().value() < 0) or \
                (self._right.return_type() == UnsignedInteger and type(
                    self._left.evaluate()) == NumberLiteral and self._left.evaluate().value() < 0):
            self.add_message(f'Comparing unsigned value to a negative literal', errors)

        elif self._left.return_type() != self._right.return_type():
            self.add_message(f"Can't compare {self._left.return_type().__name__} to {self._right.return_type().__name__}", errors)

    def _operands_equal(self):
        if (type(self._evaluated_left) is NumberLiteral and type(self._evaluated_right) is NumberLiteral) or\
            (type(self._evaluated_left) is bool and type(self._evaluated_right) is bool):
            return self._evaluated_left.Equals(self._evaluated_right)

        # There are theoretically cases we could resolve as well. For example
        # some_field + 1 == 1 + some_field will always be true
        # but we'll just leave the tough stuff up to the compiler/interpreter for the output language

        return None

    def return_type(self):
        return bool

class ArithmeticOperator(BinaryOperator, ABC):
    def __init__(self, left: Expression, right: Expression, token):
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
        if super().check_semantics(warnings, errors):
            return True

        # Operands should be integer or floating point
        if self._left.return_type() not in [Float, SignedInteger, UnsignedInteger]:
            self.add_message(f'Left hand operand ({str(self._left)}) does not resolve to integer or float', errors)
        if self._right.return_type() not in [Float, SignedInteger, UnsignedInteger]:
            self.add_message(f'Right hand operand ({str(self._right)}) does not resolve to integer or float', errors)

    def return_type(self):
        # If either one of the operands is a float, the result will be considered a float
        if self._left.return_type() is Float or self._right.return_type() is Float:
            return Float
        # if the operand is semantically valid, the operands will both be integers
        elif self._left.return_type() is SignedInteger or self._right.return_type() is SignedInteger:
            # If one of the two operands is signed, the result will be signed
            return SignedInteger
        else:
            # If both operands are unsigned, the result will be unsigned
            return UnsignedInteger

    @abstractmethod
    def compute(self, left: NumberLiteral, right: NumberLiteral):
        pass

class AddOperator(ArithmeticOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is AddOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() + right.value()


    def __str__(self):
        return f'({str(self._left)} + {str(self._right)})'

class DivisionOperator(ArithmeticOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is DivisionOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() / right.value()

    def check_semantics(self, warnings, errors):
        error = super().check_semantics(warnings, errors)
        self.add_message(f'Division operator {self.__str__()} may have in non-integer result. It depends on the target language how those results are handled.', warnings)
        return error

    def __str__(self):
        return f'({str(self._left)} / {str(self._right)})'

class GreaterThanEqualOperator(RelationalOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is GreaterThanEqualOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() >= right.value()

    def __str__(self):
        return f'({str(self._left)} >= {str(self._right)})'

class GreaterThanOperator(RelationalOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is GreaterThanOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() > right.value()

    def __str__(self):
        return f'({str(self._left)} >= {str(self._right)})'

class LessThanEqualOperator(RelationalOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is LessThanEqualOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() <= right.value()

    def __str__(self):
        return f'({str(self._left)} <= {str(self._right)})'

class LessThanOperator(RelationalOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is LessThanOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() < right.value()

    def __str__(self):
        return f'({str(self._left)} < {str(self._right)})'

class MultiplyOperator(ArithmeticOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is MultiplyOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() * right.value()

    def __str__(self):
        return f'({str(self._left)} * {str(self._right)})'

class EqualsOperator(EqualityOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def evaluate(self):
        # method returns a troolean. None means we don't know if their equal. Yes, I know trooleans are bad. I'm sorry.
        operands_equal = self._operands_equal()
        return self if operands_equal is None else operands_equal

    def Equals(self, other):
        return type(other) is EqualsOperator and super().Equals(other)

    def __str__(self):
        return f'({str(self._left)} == {str(self._right)})'

class NotEqualsOperator(EqualityOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def evaluate(self):
        # method returns a troolean. None means we don't know if their equal. Yes, I know trooleans are bad. I'm sorry.
        operands_equal = self._operands_equal()
        return self if operands_equal is None else not operands_equal

    def Equals(self, other):
        return type(other) is NotEqualsOperator and super().Equals(other)

    def __str__(self):
        return f'({str(self._left)} != {str(self._right)})'


class SubtractOperator(ArithmeticOperator):
    def __init__(self, left, right, token=None):
        super().__init__(left, right, token)

    def Equals(self, other):
        return type(other) is SubtractOperator and super().Equals(other)

    def compute(self, left:NumberLiteral, right:NumberLiteral):
        return left.value() - right.value()

    def __str__(self):
        return f'({str(self._left)} - {str(self._right)})'

class TernaryOperator(Expression):
    def __init__(self, condition, true, false, token=None):
        super().__init__(token)
        self._condition = condition
        self._true = true
        self._false = false

    def condition(self):
        return self._condition

    def true_clause(self):
        return self._true

    def false_clause(self):
        return self._false

    def evaluate(self):
        evaluated_condition = self._condition.evaluate()
        evaluated_true = self._true.evaluate()
        evaluated_false = self._false.evaluate()

        if type(evaluated_condition) is bool:
            # if the condition can be 'compile time' evaluated to a boolean, we can evaluate the operator to just the
            # evaluated true or false clause
            return evaluated_true if evaluated_condition else evaluated_false
        else:
            # if not, we can't 'evaluate away' the ternary operator itself, but maybe we can simplify the clauses
            self._true = evaluated_true
            self._false = evaluated_false
            return self

    def Equals(self, other):
        return type(other) is TernaryOperator and \
            self._condition.Equals(other._condition) and \
            self._true.Equals(other._true) and \
            self._false.Equals(other._false)

    def check_semantics(self, warnings, errors):
        initial_error_count = len(errors)
        self._condition.check_semantics(warnings, errors)
        self._true.check_semantics(warnings, errors)
        self._false.check_semantics(warnings, errors)
        if len(errors) > initial_error_count:
            return True

        return_type_true = self._true.return_type()
        return_type_false = self._false.return_type()
        return_type_condition = self._condition.return_type()

        from Model.types import Flag
        if return_type_condition not in [bool, Flag]:
            self.add_message(
                f'{return_type_condition.__name__} not allowed as ternary condition',
                errors)

        # We can mix and match signed integers, unsigned integers, and number literals
        allowed_mix = return_type_true in [SignedInteger, UnsignedInteger, NumberLiteral] \
                      and return_type_false in [SignedInteger, UnsignedInteger, NumberLiteral]

        if not allowed_mix and return_type_true != return_type_false:
            self.add_message(
                f'Different types for true ({return_type_true.__name__}) and false ({return_type_false.__name__}) clause',
                errors
            )

        if len(errors) > initial_error_count:
            return True

    def return_type(self):
        return_type_true = self._true.return_type()
        return_type_false = self._false.return_type()
        if return_type_true == SignedInteger or return_type_false == SignedInteger:
            return SignedInteger
        else:
            assert return_type_true == return_type_false, f'True and false clause have different return types ({return_type_true} and {return_type_false})'
            return return_type_true

    def __str__(self):
        return f'{str(self._condition)} ? {str(self._true)} : {str(self._false)}'