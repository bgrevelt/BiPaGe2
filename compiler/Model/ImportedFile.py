class ImportedFile:
    def __init__(self, path, imports, namespace, enumerations):
        self.path = path
        self.namespace = namespace
        self.enumerations = enumerations
        self.imports = imports

    def enumerations_by_fully_qualified_name(self):
        r = {}
        for enum in self.enumerations:
            name = (self.namespace + "." if self.namespace else "") + enum.name()
            r[name] = enum
        return r

    def __str__(self):
        r = '=' * 150 + '\n'
        h = f'== Imported file {self.path}'
        r += h + ' ' * (150 - len(h) - 2) + '==\n'
        r += '=' * 150 + '\n'
        r += f'Namespace: {self.namespace}\n'
        r += 'Enumerations:\n'
        for enum in self.enumerations:
            r += f'\t{enum.name()} ({enum.size_in_bits()} bits)\n'
        r += f'Imports\n'
        for i in self.imports:
            r += f'\t{i}\n'
        return r