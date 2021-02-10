from .Node import Node
from .BuildMessage import BuildMessage
from collections import defaultdict

class Definition(Node):
    def __init__(self,name, endianness, namespace, datatypes, enumerations, token):
        super().__init__(token)
        self.name = name
        self.datatypes = datatypes
        self.endianness = endianness
        self.namespace = namespace
        self.enumerations = enumerations


    def check_semantics(self, warnings, errors):
        names = defaultdict(list)
        for datatype in self.datatypes:
            names[datatype.identifier].append(datatype.location())
        for enum in self.enumerations:
            names[enum.name()].append(enum.location())

        for name, locations in names.items():
            if len(locations) > 1:
                msg = f'Name {name} used for multiple type definitions'
                for line,column in locations:
                    errors.append(BuildMessage(line, column, msg))

        for datatype in self.datatypes:
            datatype.check_semantics(warnings, errors)

        for enum in self.enumerations:
            enum.check_semantics(warnings, errors)