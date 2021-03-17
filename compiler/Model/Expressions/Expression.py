from Model.Node import Node

#TODO make this an ABC

class Expression(Node):
    def __init__(self, token):
        super().__init__(token)