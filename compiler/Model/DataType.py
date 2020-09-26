from .Node import Node
from .BuildMessage import BuildMessage

class DataType(Node):
    def __init__(self, identifier, fields, token):
        super().__init__(token)
        self.fields = fields
        self.identifier = identifier

    def __str__(self):
        s = self.identifier + "\n"
        for field in self.fields:
            s += f"\t{field.name} : {field.type} at {field.offset}\n"
        return s

    def check_semantics(self):
        warnings = []
        errors = []

        # check if we don't have muliple fields with the same name
        unique_field_names = {field.name for field in self.fields}
        for field_name in unique_field_names:
            fields = [field for field in self.fields if field.name == field_name]
            if len(fields) > 1:
                for field in fields:
                    msg = f"Semantic error: Duplicate field name {field.name} found in data type {self.identifier}."
                    line, column = field.location()
                    errors.append(BuildMessage(line, column, msg))

        for field in self.fields:
            ws, es = field.check_semantics()
            warnings.extend(ws)
            errors.extend(es)

        return (warnings, errors)