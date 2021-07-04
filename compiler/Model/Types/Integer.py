from ..Node import Node
from ..BuildMessage import BuildMessage
from abc import ABC, abstractmethod

class Integer(Node, ABC):
    def __init__(self, size, token):
        super().__init__(token)
        self._size = size

    def size_in_bits(self):
        return self._size

    def check_semantics(self, warnings, errors):
        line, column = self.location()
        if self._size < 2 or self._size > 64:
            errors.append(BuildMessage(line, column,
                                       f'Size ({self.size_in_bits()}) for integer outside supported range [2-64]'))

    @abstractmethod
    def signed(self):
        pass

    @abstractmethod
    def range(self):
        pass