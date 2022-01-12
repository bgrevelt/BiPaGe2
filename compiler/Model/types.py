from .Node import Node
from abc import ABC, abstractmethod
from compiler.Model.Expressions.Expression import Expression


class Integer(Node, ABC):
    def __init__(self, size, token):
        super().__init__(token)
        self._size = size

    def size_in_bits(self):
        return self._size

    def check_semantics(self, warnings, errors):
        line, column = self.location()
        if self._size < 2 or self._size > 64:
            self.add_message(f'Size ({self.size_in_bits()}) for integer outside supported range [2-64]', errors)

    @abstractmethod
    def signed(self):
        pass

    @abstractmethod
    def range(self):
        pass

class SignedInteger(Integer):
    def __init__(self, size, token):
        super().__init__(size, token)

    def signed(self):
        return True

    def range(self):
        return -1 * (2**self._size // 2), 2**self._size // 2 -1

class UnsignedInteger(Integer):
    def __init__(self, size, token):
        super().__init__(size, token)

    def signed(self):
        return False

    def range(self):
        return 0, 2**self._size -1

class Flag(Node):
    def __init__(self, token):
        super().__init__(token)

    def size_in_bits(self):
        return 1

    def signed(self):
        return False

    def range(self):
        return 0,1

    def check_semantics(self, warnings, errors):
        pass # Nothing to check. Just a bit

class Float(Node):
    def __init__(self, size, token):
        super().__init__(token)
        self._size = size

    def size_in_bits(self):
        return self._size

    def signed(self):
        return True

    def check_semantics(self, warnings, errors):
       if self._size not in (32, 64):
           self.add_message(f"Width {self._size} not supported for float type. Only 32 and 64 bit float types are supported", errors)




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
        if self._referenced_type is None:
            self.add_message(f'Reference "{self._name}" cannot be resolved', errors)

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
                return self.referenced_type().type().return_type()
            else:
                return type(self.referenced_type().type())
        else:
            return self.referenced_type()

    def __str__(self):
        return self._name



class EnumeratorReference(Expression):
    def __init__(self, identifier:str, parent, token):
        super().__init__(token)
        self._identifier = identifier
        self._parent = parent

    def identifier(self):
        return self._identifier

    def parent(self):
        return self._parent

    def check_semantics(self, warnings, errors):
        #TODO I'm not sure what to check here
        return

    def Equals(self, other):
        if type(other) is not EnumeratorReference:
            return False

        if self._identifier() != other.identifier():
            return False

        return self._parent == other.parent()

    def return_type(self):
        return self._parent

    def evaluate(self):
        return self