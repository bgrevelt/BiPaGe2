class DataType:
    def __init__(self, identifier):
        self.fields = []
        self.identifier = identifier

    def add_field(self,field):
        self.fields.append(field)

    def __str__(self):
        s = self.identifier + "\n"
        for field in self.fields:
            s += f"\t{field.name} : {field.type} at {field.offset}\n"
        return s