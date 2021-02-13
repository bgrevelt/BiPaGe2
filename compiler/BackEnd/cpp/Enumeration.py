from Model.Enumeration import Enumeration as ModelEnum
from .Fields.Integer import _to_cpp_type

class Enumeration:
    def __init__(self, enumeration:ModelEnum):
        self._model = enumeration
        self._template = '''
        enum class {name} : {type}
        {{
        {enumerators}
        }};'''

    def defintion(self):
        name = self._model.name()
        type = _to_cpp_type(self._model.size_in_bits(), self._model.signed())
        enumerators = self._enumerators()
        return self._template.format(name=name, type=type, enumerators=enumerators)

    def _enumerators(self):
        r = "\n".join(f'{n} = {v},' for n,v in self._model.enumerators())
        return r[:-1]
