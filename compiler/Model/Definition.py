from .Node import Node
from .BuildMessage import BuildMessage
from collections import defaultdict

class Definition(Node):
    def __init__(self,name, endianness, namespace, imports, datatypes, enumerations, token):
        super().__init__(token)
        self.name = name
        self.imports = imports
        self.datatypes = datatypes
        self.endianness = endianness
        self.namespace = namespace
        self.enumerations = enumerations

    def namespace_as_string(self):
        return '.'.join(self.namespace)


    def check_semantics(self, messages):
        initial_error_count = messages.error_count()
        names = defaultdict(list)
        for datatype in self.datatypes:
            names[datatype.identifier].append(datatype)
        for enum in self.enumerations:
            names[enum.name()].append(enum)
        for import_ in self.imports:
            for enum in import_.enumerations:
                ns = import_.namespace_as_string()
                name = (ns + "." if ns else "") + enum.name()
                names[name].append(enum)


        for name, types in names.items():
            if len(types) > 1:
                msg = f'Mutiple defintions found for {name}.\n' + \
                      '\n'.join(f'{{file}}:{t.location()[0]}:{t.location()[1]} Found other defintion of {name} here.' for t in types[1:])
                types[0].add_error(msg, messages)

        for datatype in self.datatypes:
            datatype.check_semantics(messages)

        for enum in self.enumerations:
            enum.check_semantics(messages)

        return messages.error_count() > initial_error_count