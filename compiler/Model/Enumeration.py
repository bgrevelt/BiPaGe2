from .Node import Node
from .BuildMessage import BuildMessage
from typing import List, Tuple

class Enumeration(Node):
    def __init__(self, name:str, base_type, enumerands:List[Tuple[str,int]], token):
        super().__init__(token)
        self._name = name
        self._enumerands = enumerands
        self._base_type = base_type

    def name(self):
        return self._name

    def size_in_bits(self):
        return self._base_type.size_in_bits()

    def signed(self):
        return self._base_type.signed()

    def check_semantics(self, warnings, errors):
        self._check_unique_enumerands(warnings, errors)
        self._check_enumerand_value(warnings, errors)

    def _check_unique_enumerands(self, warnings, errors):
        line, column = self.location()
        for name, value in self._enumerands:
            if sum(1 for n,v in self._enumerands if n==name) > 1:
                errors.append(BuildMessage(line, column, f'Duplicated enumerand {name} in {self._name}'))

    def _check_enumerand_value(self, warnings, errors):
        line, column = self.location()
        min, max = self._base_type.range()
        for name, value in self._enumerands:
            if value < min or value > max:
                errors.append(BuildMessage(line, column, f'Enumerand {name} in enumeration {self._name} has a value that is outside of the supported range of the underlying type ({min},{max})'))

            enumerands_with_value = [e for e in self._enumerands if e[1] == value]
            if len(enumerands_with_value) > 1:
                msg = f'Same value ({value}) used by mulitple enumerands in enumeration {self._name}:\n'
                msg += "\n".join(f'\t{n}' for n,v in enumerands_with_value)
                errors.append(BuildMessage(line, column, msg))
