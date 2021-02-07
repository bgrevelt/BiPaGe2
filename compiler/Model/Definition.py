from .Node import Node
from .BuildMessage import BuildMessage

class Definition(Node):
    def __init__(self, endianness, namespace, datatypes, enumerations, token):
        super().__init__(token)
        self.datatypes = datatypes
        self.endianness = endianness
        self.namespace = namespace
        self.enumerations = enumerations

    def check_semantics(self, warnings, errors):
        unique_datatype_names = {datatype.identifier for datatype in self.datatypes}
        for datatype_name in unique_datatype_names:
            datatypes = [datatype for datatype in self.datatypes if datatype.identifier == datatype_name]
            if len(datatypes) > 1:
                for datatype in datatypes:
                    msg = f"Semantic error: Duplicate datatype name {datatype.identifier} found."
                    line, column = datatype.location()
                    errors.append(BuildMessage(line, column, msg))

        for datatype in self.datatypes:
            datatype.check_semantics(warnings, errors)