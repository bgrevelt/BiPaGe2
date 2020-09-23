import os
from .ViewGenerator import ViewGenerator
from .BuilderGenerator import BuilderGenerator
from .HelperFunctions import *
class Generator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.view_generator = ViewGenerator()
        self.builder_generator = BuilderGenerator()
        self.header_template = '''{includes}

namespace BiPaGe
{{
{offsets}

{view_class}

{builder_class}

}}
'''

    def Generate(self, model):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        for DataType in model:
            headerpath = os.path.join(self.output_dir, f"{DataType.identifier}_generated.h")
            with open(headerpath, 'w+') as header:
                includes = "\n".join([f'#include {include}' for include in self._GetIncludes()])
                offsets = "\n".join([f'#define {name} {value}' for name, value in self._GetOffsets(DataType)])
                view = self.view_generator.GenerateDataTypeParser(DataType)
                builder = self.builder_generator.GenerateBuilder(DataType)
                header.write(self.header_template.format(includes=includes,
                                                         offsets=self._Tabify(offsets, 1),
                                                         view_class=self._Tabify(view, 1),
                                                         builder_class=self._Tabify(builder, 1)))

    def _GetIncludes(self):
        return list(set(self.view_generator.GetIncludes() + self.builder_generator.GetIncludes()))

    def _GetOffsets(self, DataType):
        return [(FieldOffsetName(field), field.offset) for field in DataType.fields]

    def _Tabify(self, text, depth):
        return "\n".join([('\t' * depth) + line for line in text.splitlines()])

