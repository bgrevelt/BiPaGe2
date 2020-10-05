from .Float import Float
from .Integer import Integer

def Build(field):
    if field.type == 'int' or field.type == 'uint':
        return Integer(field)
    else:
        assert field.type == 'float', "Unknown type {}".format(field.type)
        return Float(field)