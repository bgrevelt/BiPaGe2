from .Node import Node
from .BuildMessage import BuildMessage

class Field(Node):
    def __init__(self, name, type, offset, token):
        super().__init__(token)
        self.name = str(name)
        self.type = str(type)
        self.offset = offset
        # At this time only float|int|uint 8|16|32|64 are supported. So the size (in bits) is always at the end
        self._bits = int("".join([c for c in self.type if c.isnumeric()]))

    def size(self):
        assert self._bits % 8 == 0, "Size should be multitude of 8. This should be enforced by the parser rules"
        return self._bits // 8

    def check_semantics(self):
        warnings = []
        errors = []

        if self.type.startswith('float') and self._bits not in (32,64):
            errors.append(BuildMessage(self._token.line, self._token.column,
                                          f"Width {self._bits} not supported for float type. Only 32 and 64 bit float types are supported"))

        return warnings, errors