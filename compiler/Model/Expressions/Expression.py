from Model.Node import Node
from abc import ABC, abstractmethod

class Expression(Node, ABC):
    def __init__(self, token):
        super().__init__(token)

    @abstractmethod
    def evaluate(self):
        pass

    # Used for testing. Test if the expression matches other
    @abstractmethod
    def Equals(self, other):
        pass