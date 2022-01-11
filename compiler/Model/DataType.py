from .Node import Node
from .BuildMessage import BuildMessage

class DataType(Node):
    def __init__(self, identifier, capture_scopes, fields, token):
        super().__init__(token)
        self._fields = fields
        self.identifier = identifier
        self.capture_scopes = capture_scopes

    def __str__(self):
        s = self.identifier + "\n"
        for field in self._fields:
            s += f"\t{field.name} : {field.type} at {field.offset()}\n"
        return s

    def size_in_bits(self):
        # If any of the fields has a dynamic size, we don't have an 'a-priori' size for this data type
        if any(field.size_in_bits() is None for field in self._fields):
            return None

        return sum(field.size_in_bits() for field in self._fields)

    def static_size_in_bits(self):
        return sum(field.size_in_bits() for field in self._fields if field.size_in_bits() is not None)

    def check_semantics(self, warnings, errors):
        self._check_empty(warnings, errors)
        self._check_unique_field_names(warnings, errors)
        self._check_capture_scopes(warnings, errors)
        self._check_fields(warnings, errors)
        self._check_size(warnings, errors)

    def _check_empty(self, warnings, errors):
        if len(self.fields(include_padding_fields=False)) == 0:
            line, column = self.location()
            warnings.append(BuildMessage(line, column, f'Datatype {self.identifier} has no non-padding fields'))

    def _check_unique_field_names(self, warnings, errors):
        # check if we don't have muliple fields with the same name
        unique_field_names = {field.name for field in self._fields if field.name is not None}
        for field_name in unique_field_names:
            fields = [field for field in self._fields if field.name == field_name]
            if len(fields) > 1:
                for field in fields:
                    msg = f"Semantic error: Duplicate field name {field.name} found in data type {self.identifier}."
                    line, column = field.location()
                    errors.append(BuildMessage(line, column, msg))

    def _check_capture_scopes(self, warnings, errors):
        for capture_scope in self.capture_scopes:
            capture_scope.check_semantics(warnings, errors)

    def _check_fields(self, warnings, errors):
        for field in self._fields:
            field.check_semantics(warnings, errors)

    def _check_size(self, warnings, errors):
        if self.size_in_bits() is not None and self.size_in_bits() % 8 != 0:
            line, column = self.location()
            errors.append(BuildMessage(line, column,
                            f'''DataType {self.identifier} is ({self.size_in_bits()}) bits in size. Datatypes should be a multiple of eight in size (e.g a number of bytes).'''))

    def fields(self, include_padding_fields = False):
        return [field for field in self._fields if include_padding_fields or (not field.is_padding_field())]
