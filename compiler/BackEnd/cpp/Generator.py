import os
from .DataType import DataType

class Generator:
    def __init__(self, settings):
        self._settings = settings
        self.output_dir = settings.output

    def generate(self, model):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        for datatype in model.datatypes:
            generator = DataType(datatype, self._settings)
            header_path = os.path.join(self.output_dir, f"{datatype.identifier}_generated.h")
            generator.generate(header_path)