import os
from .ViewGenerator import ViewGenerator

class Generator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.view_generator = ViewGenerator()

    def Generate(self, model):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        for DataType in model:
            headerpath = os.path.join(self.output_dir, f"{DataType.identifier}_generated.h")
            with open(headerpath, 'w+') as header:
                header.write(self.view_generator.GenerateDataTypeParser(DataType))