import unittest
from .Field import Field

class Field_unittests(unittest.TestCase):
    def test_size(self):
        self.validate_type_size('uint8', 1)
        self.validate_type_size('int8', 1)
        self.validate_type_size('uint16', 2)
        self.validate_type_size('int16', 2)
        self.validate_type_size('uint32', 4)
        self.validate_type_size('int32', 4)
        self.validate_type_size('float32', 4)
        self.validate_type_size('uint64', 8)
        self.validate_type_size('int64', 8)
        self.validate_type_size('float64', 8)

    def validate_type_size(self, type, expected_size):
        size = Field("", type, 0, None).size()
        self.assertEqual(size, expected_size, f'Size for type {type} is {size} not {expected_size}.')