from .Node import Node
from .BuildMessage import BuildMessage
from collections import defaultdict
from Model.ImportedFile import ImportedFile
from typing import List

class Definition(Node):
    def __init__(self,name, endianness, namespace, imports, datatypes, enumerations, token):
        super().__init__(token)
        self.name = name
        self.imports = imports
        self.datatypes = datatypes
        self.endianness = endianness
        self.namespace = namespace
        self.enumerations = enumerations


    def check_semantics(self, warnings, errors):
        initial_error_count = len(errors)
        names = defaultdict(list)
        for datatype in self.datatypes:
            names[datatype.identifier].append(datatype.location())
        for enum in self.enumerations:
            names[enum.name()].append(enum.location())
        for import_ in self.imports:
            for name, enum in import_.enumerations_by_fully_qualified_name().items():
                names[name].append(enum.location())


        for name, locations in names.items():
            if len(locations) > 1:
                msg = f'Mutiple defintions found for {name}.\n' + \
                      '\n'.join(f'{{file}}:{line}:{column} Found other defintion of {name} here.' for line, column in locations[1:])
                line, column = locations[0]
                errors.append(BuildMessage(line, column, msg))

        for datatype in self.datatypes:
            datatype.check_semantics(warnings, errors)

        for enum in self.enumerations:
            enum.check_semantics(warnings, errors)

        return len(errors) > initial_error_count