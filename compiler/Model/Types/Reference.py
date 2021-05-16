from compiler.Model.Expressions.Expression import Expression
from ..BuildMessage import BuildMessage

#TODO: I think we should split this up into a TypeReference and FieldReference class
# That will safe us a lot of hacks all over the place where we figure out if the referenced type is a field or
# a type (e.g. Enumeration)

class Reference(Expression):
    def __init__(self, name, referenced_type, token):
        super().__init__(token)
        self._name = name
        self._referenced_type = referenced_type

    def size_in_bits(self):
        if self._referenced_type is not None:
            return self._referenced_type.size_in_bits()
        else:
            return 8

    def signed(self):
        if self._referenced_type is not None:
            return self._referenced_type.signed()
        else:
            return False

    def referenced_type(self):
        return self._referenced_type

    def name(self):
        return self._name

    def check_semantics(self, warnings, errors):
        line, column = self.location()
        if self._referenced_type is None:
            errors.append(BuildMessage(line, column,
                                       f'Reference "{self._name}" cannot be resolved'))

    def evaluate(self):
        return self

    def Equals(self, other):
        if type(other) is not Reference:
            return False

        if self.name() != other.name():
            return False

        if self._referenced_type == None:
            return other.referenced_type() == None
        else:
            #TODO: this will lead to a runtime error as Enumeration does not have an Equals method
            return self._referenced_type.Equals(other.referenced_type())

    def return_type(self):
        from Model.Field import Field
        if type(self.referenced_type()) is Field:
            return type(self.referenced_type().type())
        else:
            return type(self.referenced_type())

    def __str__(self):
        return self._name