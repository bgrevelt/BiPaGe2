from ..Node import Node
from ..BuildMessage import BuildMessage

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
           line, column = self.location()
           errors.append(BuildMessage(line, column,f"Width {self._size} not supported for float type. Only 32 and 64 bit float types are supported"))