class CaptureScope:
    def __init__(self, capture_scope, number, fields):
        self._capture_scope = capture_scope
        self._fields = fields
        self._number = number

    def byteswap_code(self):
        r = f'auto {self._name()} = reinterpret_cast<std::uint{self._size()}_t*>(sink + {self._offset_name()});\n'
        r += f'*{self._name()} = BiPaGe::swap_bytes(*{self._name()});\n'
        return r

    def _name(self):
        return f'capture_scope_{self._number+1}'

    def _offset_name(self):
        # Use the offset name of the first field in the capture scope
        # all fields in the capture scope have the same capture scope offset
        # so it doesn't really matter which one we take
        return self._fields[0].offset_name()

    def _size(self):
        return self._capture_scope.size()
