import unittest
from .Builder import Builder

class Builder_unittests(unittest.TestCase):
    def test_simple(self):
        _, _, model = Builder().build('''
SomeDataType
{
    field1 : int8;
    field2 : int16;
    field3 : int32;
    field4 : int64;
    field5 : uint8;
    field6 : uint16;
    field7 : uint32;
    field8 : uint64;
    field9 : float32;
    field10 : float64;
}
        ''')

        self.assertEqual(len(model._datatypes), 1)
        datatype = model._datatypes[0]

        self.verify_datatype(datatype, "SomeDataType", [
            ("field1", "int8", 0, 8),
            ("field2", "int16", 8, 16),
            ("field3", "int32", 24, 32),
            ("field4", "int64", 56, 64),
            ("field5", "uint8", 120, 8),
            ("field6", "uint16", 128, 16),
            ("field7", "uint32", 144, 32),
            ("field8", "uint64", 176, 64),
            ("field9", "float32", 240, 32),
            ("field10", "float64", 272, 64)
        ])

    def test_alias(self):
            _, _, model = Builder().build('''
    SomeDataType
    {
        field1 : s8;
        field2 : s16;
        field3 : s32;
        field4 : s64;
        field5 : u8;
        field6 : u16;
        field7 : u32;
        field8 : u64;
        field9 : f32;
        field10 : f64;
    }
            ''')

            self.assertEqual(len(model._datatypes), 1)
            datatype = model._datatypes[0]

            # Aliases get turned into their counterpart types in the builder so the backend only needs to be worried
            # about those typessou
            self.verify_datatype(datatype, "SomeDataType", [
                ("field1", "int8", 0, 8),
                ("field2", "int16", 8, 16),
                ("field3", "int32", 24, 32),
                ("field4", "int64", 56, 64),
                ("field5", "uint8", 120, 8),
                ("field6", "uint16", 128, 16),
                ("field7", "uint32", 144, 32),
                ("field8", "uint64", 176, 64),
                ("field9", "float32", 240, 32),
                ("field10", "float64", 272, 64)
            ])

    def test_reserved_fields(self):
            _, _, model = Builder().build('''
    SomeDataType
    {
        field1 : s8;
        s16;
        field3 : s32;
        s64;
        field5 : u8;
        u16;
        field7 : u32;
        u64;
        field9 : f32;
        f64;
    }
            ''')

            self.assertEqual(len(model._datatypes), 1)
            datatype = model._datatypes[0]

            # Reserved fields are not part of the model since we don't need to do anything with them in the backend
            self.verify_datatype(datatype, "SomeDataType", [
                ("field1", "int8", 0, 8),
                ("field3", "int32", 24, 32),
                ("field5", "uint8", 120, 8),
                ("field7", "uint32", 144, 32),
                ("field9", "float32", 240, 32)
            ])

    def test_non_standard_width(self):
        _, _, model = Builder().build('''
    SomeDataType
    {
        field1 : int5;
        field2 : uint20;
        field3 : int7;
    }
            ''')

        self.verify_datatype(model._datatypes[0], 'SomeDataType', [
            ('field1', 'int5',   0,  5,  8,  0,  0x1f),
            ('field2', 'uint20', 5,  20, 32, 0,  0x1ffffe0),
            ('field3', 'int7',   25, 7,  8,  24, 0xfe)
        ])

    def test_non_standard_width_alias(self):
        _, _, model = Builder().build('''
    SomeDataType
    {
        field1 : s5;
        field2 : u20;
        field3 : s7;
    }
            ''')

        self.verify_datatype(model._datatypes[0], 'SomeDataType', [
            ('field1', 'int5',   0,  5,  8,  0,  0x1f),
            ('field2', 'uint20', 5,  20, 32, 0,  0x1ffffe0),
            ('field3', 'int7',   25, 7,  8,  24, 0xfe)
        ])


    def verify_datatype(self, datatype, expected_name, expected_fields):
        self.assertEqual(datatype.identifier, expected_name)
        self.assertEqual(len(datatype.fields), len(expected_fields))
        for field, expected in zip(datatype.fields, expected_fields):
            expected = expected + tuple([None] * (7-len(expected)))
            name, type, offset, size, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask = expected
            self.verify_field(field, name, type, offset, size, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask)

    def verify_field(self, field, name, type, offset, size, encapsulating_type_size, encapsulating_type_offset, encapsulating_type_mask):
        self.assertEqual(field.name, name)
        self.assertEqual(field.type, type)
        self.assertEqual(field.offset, offset)
        self.assertEqual(field.size(), size)
        if encapsulating_type_size is not None:
            self.assertEqual(field.encapsulating_type_size(), encapsulating_type_size)
        if encapsulating_type_offset is not None:
            self.assertEqual(field.encapsulating_type_offset(), encapsulating_type_offset)
        if encapsulating_type_mask is not None:
            self.assertEqual(field.encapsulated_type_mask(), encapsulating_type_mask)
