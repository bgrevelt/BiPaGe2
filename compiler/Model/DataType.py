class DataType:
    def __init__(self, identifier, fields = []):
        self.fields = fields
        self.identifier = identifier

    def __str__(self):
        s = self.identifier + "\n"
        for field in self.fields:
            s += f"\t{field.name} : {field.type} at {field.offset}\n"
        return s