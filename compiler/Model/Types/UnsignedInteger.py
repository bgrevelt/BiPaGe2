from .Integer import Integer

class UnsignedInteger(Integer):
    def __init__(self, size, token):
        super().__init__(size, token)

    def signed(self):
        return False

    def range(self):
        return 0, 2**self._size -1