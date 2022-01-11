from compiler.Model.Expressions.Expression import Expression
from ..BuildMessage import BuildMessage

#TODO: I think we should split this up into a TypeReference and FieldReference class
# That will safe us a lot of hacks all over the place where we figure out if the referenced type is a field or
# a type (e.g. Enumeration)
#TODO: I don't think there is any valid situation in which referenced type is None other than malformed input. I'm not sure if we
# need to cater to that situation in all of these methods. Maybe we can say that if check_semantics returns false any other
# method is allowed to throw. But that will only work if other types do not call any of the methods of a reference in
# their check_semantics method. Note: Field calls size_in_bits in the ctor. Maybe we can evaluate if we can set things
# up so no methods are called before calling check semantics?! But I'm not really comfortable with those types of
# prerequisites...

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
            if type(self.referenced_type().type()) == Reference:
                return type(self.referenced_type().type().referenced_type())
            else:
                return type(self.referenced_type().type())
        else:
            return type(self.referenced_type())

    def __str__(self):
        return self._name