from .Node import Node
from .BuildMessage import BuildMessage
from typing import List, Tuple
import math
from Model.Expressions.NumberLiteral import NumberLiteral

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
        #TODO: This code should be moved to some place where both field en enumerator can use it.
        bytes_required = math.ceil(self._base_type.size_in_bits() / 8)
        bytes_nearest_type = 2 ** (math.ceil(math.log(bytes_required, 2)))
        return bytes_nearest_type * 8

    def signed(self):
        return self._base_type.signed()

    def enumerators(self):
        return self._enumerators

    def check_semantics(self, warnings, errors):
        self._check_unique_enumerators(warnings, errors)
        self._check_enumerand_value(warnings, errors)

    def _check_unique_enumerators(self, warnings, errors):
        line, column = self.location()
        for name, value in self._enumerators:
            if sum(1 for n,v in self._enumerators if n==name) > 1:
                errors.append(BuildMessage(line, column, f'Duplicated enumerand {name} in {self._name}'))

    def _check_enumerand_value(self, warnings, errors):
        min, max = self._base_type.range()
        for name, value in self._enumerators:
            line, column = value.location()

            if type(value) is not NumberLiteral:
                errors.append(BuildMessage(line, column, f'Only number literals are allowed for enumerator values. Not {type(value).__name__}'))
                continue

            value = value.value()
            if value < min or value > max:
                errors.append(BuildMessage(line, column, f'Enumerand {name} in enumeration {self._name} has a value that is outside of the supported range of the underlying type ({min},{max})'))

            enumerators_with_value = [e for e in self._enumerators if type(e[1]) is NumberLiteral and e[1].value() == value]
            if len(enumerators_with_value) > 1:
                msg = f'Same value ({value}) used by mulitple enumerands in enumeration {self._name}:\n'
                msg += "\n".join(f'\t{n}' for n,v in enumerators_with_value)
                errors.append(BuildMessage(line, column, msg))
