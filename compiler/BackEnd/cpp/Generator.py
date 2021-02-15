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

        cpp_datatypes = [DataType(dt, model.endianness, self._settings) for dt in model.datatypes]

        header_path = os.path.join(self.output_dir, f"{model.name}_generated.h")
        includes = "\n".join(list(set(inc for datatype in cpp_datatypes for inc in datatype.includes())))
        defines = "\n".join([define for datatype in cpp_datatypes for define in datatype.defines()])

        content = f'''{includes}

                {self.namespace_open(model.namespace)}
                
                {defines}
                
                '''
        for enum in (Enumeration(e) for e in model.enumerations):
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