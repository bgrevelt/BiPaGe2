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
            ("field1", "int8", 0, 1),
            ("field2", "int16", 1, 2),
            ("field3", "int32", 3, 4),
            ("field4", "int64", 7, 8),
            ("field5", "uint8", 15, 1),
            ("field6", "uint16", 16, 2),
            ("field7", "uint32", 18, 4),
            ("field8", "uint64", 22, 8),
            ("field9", "float32", 30, 4),
            ("field10", "float64", 34, 8)
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
                ("field1", "int8", 0, 1),
                ("field2", "int16", 1, 2),
                ("field3", "int32", 3, 4),
                ("field4", "int64", 7, 8),
                ("field5", "uint8", 15, 1),
                ("field6", "uint16", 16, 2),
                ("field7", "uint32", 18, 4),
                ("field8", "uint64", 22, 8),
                ("field9", "float32", 30, 4),
                ("field10", "float64", 34, 8)
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
                ("field1", "int8", 0, 1),
                ("field3", "int32", 3, 4),
                ("field5", "uint8", 15, 1),
                ("field7", "uint32", 18, 4),
                ("field9", "float32", 30, 4)
            ])


    def verify_datatype(self, datatype, expected_name, expected_fields):
        self.assertEqual(datatype.identifier, expected_name)
        self.assertEqual(len(datatype.fields), len(expected_fields))
        for field, (name, type, offset, size) in zip(datatype.fields, expected_fields):
            self.verify_field(field, name, type, offset, size)

    def verify_field(self, field, name, type, offset, size):
        self.assertEqual(field.name, name)
        self.assertEqual(field.type, type)
        self.assertEqual(field.offset, offset)
        self.assertEqual(field.size(), size)
