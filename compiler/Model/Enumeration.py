from .Node import Node
from .BuildMessage import BuildMessage
from typing import List, Tuple
from compiler.Model.expressions import NumberLiteral
from compiler.Model.helpers import to_standard_size

class Enumeration(Node):
    def __init__(self, name:str, base_type, enumerators:List[Tuple[str,int]], token):
        super().__init__(token)
        self._name = name
        self._enumerators = enumerators
        self._base_type = base_type
        self.__name__ = name

    def name(self):
        return self._name

    def setname(self, name):
        self._name = name

    def size_in_bits(self):
        return self._base_type.size_in_bits()

    def standard_size(self):
        return to_standard_size(self._base_type.size_in_bits())

    def signed(self):
        return self._base_type.signed()

    def enumerators(self):
        return self._enumerators

    def check_semantics(self, messages):
        initial_error_count = messages.error_count()
        self._check_unique_enumerators(messages)
        self._check_enumerand_value(messages)
        return messages.error_count() > initial_error_count

    def Equals(self, other):
        return type(other) == Enumeration and \
    self._name == other.name() and \
    self._base_type == other._base_type and \
    len(self.enumerators()) == len(other.enumerators()) and \
    all(l == r for l,r in zip(self.enumerators(), other.enumerators()))

    def _check_unique_enumerators(self, messages):
        for name, value in self._enumerators:
            if sum(1 for n,v in self._enumerators if n==name) > 1:
                self.add_error(f'Duplicated enumerand {name} in {self._name}', messages)

    def _check_enumerand_value(self, messages):
        min, max = self._base_type.range()
        for name, value in self._enumerators:
            if type(value) is not NumberLiteral:
                value.add_error(f'Only number literals are allowed for enumerator values. Not {type(value).__name__}', messages)
                continue

            if value.value() < min or value.value() > max:
                value.add_error(f'Enumerand {name} in enumeration {self._name} has a value that is outside of the supported range of the underlying type ({min},{max})',messages)

            enumerators_with_value = [e for e in self._enumerators if type(e[1]) is NumberLiteral and e[1].value() == value.value()]
            if len(enumerators_with_value) > 1:
                msg = f'Same value ({value.value()}) used by mulitple enumerands in enumeration {self._name}:\n'
                msg += "\n".join(f'\t{n}' for n,v in enumerators_with_value)
                value.add_error(msg, messages)
