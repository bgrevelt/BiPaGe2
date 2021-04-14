from Model.Node import Node
from abc import ABC, abstractmethod

class Expression(Node, ABC):
    def __init__(self, token):
        super().__init__(token)

    @abstractmethod
    def evaluate(self):
        pass