from ..Node import Node
from ..BuildMessage import BuildMessage


class Integer(Node):
    def __init__(self, size, signed, token):
        super().__init__(token)
        self._size = size
        self._signed = signed

    def size_in_bits(self):
        return self._size

    def signed(self):
        return self._signed

    def check_semantics(self, warnings, errors):
        line, column = self.location()
        if self._size < 2 or self._size > 64:
            errors.append(BuildMessage(line, column,
                                       f'Size ({self.size_in_bits()}) for integer outside supported range [2-64]'))