from .Integer import Integer

class SignedInteger(Integer):
    def __init__(self, size, token):
        super().__init__(size, token)

    def signed(self):
        return True

    def range(self):
        return -1 * (2**self._size // 2), 2**self._size // 2 -1