from Model.Enumeration import Enumeration as ModelEnum
from .Fields.Integer import Integer

class Enumeration:
    def __init__(self, enumeration:ModelEnum):
        self._model = enumeration
        self._base_standard_type = Integer.to_cpp_type(self._model.standard_size(), self._model.signed())
        self._template = '''
        enum class {name} : {type}
        {{
        {enumerators}
        }};'''

    def defintion(self):
        name = self._model.name()
        enumerators = self._enumerators()
        return self._template.format(name=name, type=self._base_standard_type, enumerators=enumerators)

    def to_string(self):
        return f'''
        std::string enum_to_string({self._model.name()} value)
        {{
            switch(value)
            {{
                {self._enumerator_cases()}
                default: 
                    return "unknown enumerator (" + std::to_string(static_cast<{self._base_standard_type}>(value)) + ") for enumeration {self._model.name()}"; 
            }}
        }} 
        '''

    def includes(self):
        incs = ['<cstdint>','<string>']

        return [f'#include {include}' for include in incs]

    def _enumerator_cases(self):
        return "\n".join(f'case {self._model.name()}::{n}: return "{self._model.name()}::{n} ({v.value()})";' for n, v in self._model.enumerators())

    def _enumerators(self):
        r = "\n".join(f'{n} = {v.value()},' for n,v in self._model.enumerators())
        return r[:-1]
