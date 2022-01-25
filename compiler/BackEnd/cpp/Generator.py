import os
from .DataType import DataType
from .Beautifier import *
from .Enumeration import Enumeration

class Generator:
    def __init__(self, settings):
        self._settings = settings
        self.output_dir = settings.output
        self._beautifier = Beautifier()

    def generate(self, model):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        imports = self.get_import_includes(model)
        cpp_datatypes = [DataType(dt, model.endianness, self._settings) for dt in model.datatypes]
        cpp_enums = [Enumeration(e) for e in model.enumerations]

        header_path = os.path.join(self.output_dir, f"{model.name}_generated.h")

        includes = set(inc for datatype in cpp_datatypes for inc in datatype.includes())
        includes.update(set(inc for enum in cpp_enums for inc in enum.includes()))
        includes.update(imports)
        includes = "\n".join(list(includes))

        defines = "\n".join([define for datatype in cpp_datatypes for define in datatype.defines()])

        content = f'''{includes}

                {self.namespace_open(model.namespace)}
                
                {defines}
                
                '''
        for enum in cpp_enums:
            content += enum.defintion()
            if self._settings.cpp_to_string:
                content += enum.to_string()

        for datatype in cpp_datatypes:
            content += f'''
            {datatype.parser_code()}

            {datatype.builder_code()}
            '''

        content += self.namespace_close(model.namespace)

        with open(header_path, 'w+') as f:
            f.write(self._beautifier.beautify(content))

    @staticmethod
    def get_import_includes(model):
        imports = []
        for i in model.imports:
            path = i.path
            path = path.replace('"', '')
            path, _ = os.path.splitext(path)
            path += "_generated.h"
            imports.append(f'#include "{path}"')
        return imports

    @staticmethod
    def namespace_open(full_namespace):
        if len(full_namespace) == 0:
            return ""
        ns = ""
        for namespace in full_namespace:
            ns += f'namespace {namespace}\n{{\n'
        return ns

    @staticmethod
    def namespace_close(namespace):
        if len(namespace) == 0:
            return ""
        else:
            return '}\n' * len(namespace)