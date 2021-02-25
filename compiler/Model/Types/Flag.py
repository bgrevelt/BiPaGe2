from ..Node import Node
from ..BuildMessage import BuildMessage


class Flag(Node):
    def __init__(self, token):
        super().__init__(token)

    def size_in_bits(self):
        return 1

    def signed(self):
        return False

    def range(self):
        return 0,1

    def check_semantics(self, warnings, errors):
        pass # Nothing to check. Just a bit