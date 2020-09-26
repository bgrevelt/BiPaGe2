from .Node import Node
from .BuildMessage import BuildMessage

class Definition(Node):
    def __init__(self, datatypes, token):
        super().__init__(token)
        self._datatypes = datatypes

    def check_semantics(self):
        warnings = []
        errors = []

        unique_datatype_names = {datatype.identifier for datatype in self._datatypes}
        for datatype_name in unique_datatype_names:
            datatypes = [datatype for datatype in self._datatypes if datatype.identifier == datatype_name]
            if len(datatypes) > 1:
                for datatype in datatypes:
                    msg = f"Semantic error: Duplicate datatype name {datatype.identifier} found."
                    line, column = datatype.location()
                    errors.append(BuildMessage(line, column, msg))

        for datatype in self._datatypes:
            ws, es = datatype.check_semantics()
            warnings.extend(ws)
            errors.extend(es)

        return warnings, errors