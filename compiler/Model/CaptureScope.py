from .Node import Node
from .BuildMessage import BuildMessage

class CaptureScope(Node):
    def __init__(self, offset, fields, token):
        super().__init__(token)

        self._offset = offset # offset of the capture scope in the data type in bits
        self._fields = fields # fields in the capture scope

    def check_semantics(self, warnings, errors):
        size = sum(f.size_in_bits for f in self._fields)
        line, column = self.location()
        standard_widths = [8,16,32,64]

        if size > 64:
            errors.append(BuildMessage(line, column,
                                       f"Accumulated size of fields in capture scope ({size} bits) is Larger than the maximum supported capture type: 64 bits."))
        elif not size in standard_widths:
            errors.append(BuildMessage(line, column, f"Accumulated size of fields in capture scope ({size} bits) is not a standard size."))

        if all(f.size_in_bits in standard_widths for f in self._fields):
            warnings.append(BuildMessage(line, column,
                                       f"Capture scope contains only standard types. Capture scope is likely to be superfluous."))

