import unittest
from .Field import Field

class Field_unittests(unittest.TestCase):
    def test_size(self):
        self.validate_type_size('uint8', 8)
        self.validate_type_size('int8', 8)
        self.validate_type_size('uint16', 16)
        self.validate_type_size('int16', 16)
        self.validate_type_size('uint32', 32)
        self.validate_type_size('int32', 32)
        self.validate_type_size('float32', 32)
        self.validate_type_size('uint64', 64)
        self.validate_type_size('int64', 64)
        self.validate_type_size('float64', 64)

    def validate_type_size(self, type, expected_size):
        size = Field("", type, 0, None).size()
        self.assertEqual(size, expected_size, f'Size for type {type} is {size} not {expected_size}.')