class Field:
    def __init__(self, name, type, offset):
        self.name = str(name)
        self.type = str(type)
        self.offset = offset

    def size(self):
        # At this time only float|int|uint 8|16|32|64 are supported. So the size (in bits) is always at the end
        size_string = "".join([c for c in self.type if c.isnumeric()])
        size_in_bits = int(size_string)
        assert size_in_bits % 8 == 0, "Size should be multitude of 8. This should be enforced by the parser rules"
        return size_in_bits // 8