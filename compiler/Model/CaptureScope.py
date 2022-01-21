from .Node import Node
from .BuildMessage import BuildMessage
from Model.Collection import Collection

class CaptureScope(Node):
    def __init__(self, offset, fields, token):
        super().__init__(token)

        self._offset = offset # offset of the capture scope in the data type in bits
        self._fields = fields # fields in the capture scope
        self._size = sum(f.size_in_bits() for f in self._fields)

    def size(self):
        return self._size

    def offset(self):
        return self._offset

    def fields(self, include_padding_fields = False):
        return [field for field in self._fields if include_padding_fields or (not field.is_padding_field())]

    def check_semantics(self, warnings, errors):
        initial_error_count = len(errors)

        line, column = self.location()
        standard_widths = [8,16,32,64]

        if self._size > 64:
            errors.append(BuildMessage(line, column,
                                       f"Accumulated size of fields in capture scope ({self._size} bits) is Larger than the maximum supported capture type: 64 bits."))
        elif not self._size in standard_widths:
            errors.append(BuildMessage(line, column, f"Accumulated size of fields in capture scope ({self._size} bits) is not a standard size."))

        if all(f.size_in_bits() in standard_widths for f in self._fields):
            warnings.append(BuildMessage(line, column,
                                       f"Capture scope contains only standard types. Capture scope is likely to be superfluous."))

        for field in self._fields:
            if type(field.type()) is Collection:
                line, column = field.location()
                errors.append(BuildMessage(line, column,
                                           "Collections inside a capture scope are not supported"))

        return len(errors) > initial_error_count

