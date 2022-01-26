from .Node import Node
from abc import ABC, abstractmethod

class Type(Node, ABC):
    @abstractmethod
    def size_in_bits(self):
        pass

    @abstractmethod
    def check_semantics(self, messages):
        pass

    @abstractmethod
    def signed(self):
        pass

class Flag(Type):
    def __init__(self, token):
        super().__init__(token)

    def size_in_bits(self):
        return 1

    def signed(self):
        return False

    def check_semantics(self, messages):
        pass # Nothing to check. Just a bit

class Float(Type):
    def __init__(self, size, token):
        super().__init__(token)
        self._size = size

    def size_in_bits(self):
        return self._size

    def signed(self):
        return True

    def check_semantics(self, messages):
        if self._size not in (32, 64):
            self.add_error(f"Width {self._size} not supported for float type. Only 32 and 64 bit float types are supported", messages)
            return True
        return False




class Integer(Type):
    def __init__(self, size, token):
        super().__init__(token)
        self._size = size

    def size_in_bits(self):
        return self._size

    def check_semantics(self, messages):
        if self._size < 2 or self._size > 64:
            self.add_error(f'Size ({self.size_in_bits()}) for integer outside supported range [2-64]', messages)
            return True
        return False

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

