import os
from .DataType import DataType

class Generator:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate(self, model):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        for datatype in model.datatypes:
            generator = DataType(datatype)
            header_path = os.path.join(self.output_dir, f"{datatype.identifier}_generated.h")
            generator.generate(header_path)