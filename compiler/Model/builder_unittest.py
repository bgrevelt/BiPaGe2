import unittest
from build_model import build_model_from_text
from Model.Types.Integer import Integer
from Model.Types.Float import Float

class BuilderUnittests(unittest.TestCase):
    def test_simple(self):
        _, _, model = build_model_from_text('''
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
        ''', "")

        self.assertEqual(len(model.datatypes), 1)
        datatype = model.datatypes[0]

        self.verify_datatype(datatype, "SomeDataType", [
            ("field1", Integer(8, True, None), 0),
            ("field2", Integer(16, True, None), 8),
            ("field3", Integer(32, True, None), 24),
            ("field4", Integer(64, True, None), 56),
            ("field5", Integer(8, False, None), 120),
            ("field6", Integer(16, False, None), 128),
            ("field7", Integer(32, False, None), 144),
            ("field8", Integer(64, False, None), 176),
            ("field9", Float(32, None), 240),
            ("field10", Float(64, None), 272)
        ])

    def test_alias(self):
            _, _, model = build_model_from_text('''
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
            ''', "")

            self.assertEqual(len(model.datatypes), 1)
            datatype = model.datatypes[0]

            # Aliases get turned into their counterpart types in the builder so the backend only needs to be worried
            # about those typessou
            self.verify_datatype(datatype, "SomeDataType", [
                ("field1", Integer(8, True, None), 0),
                ("field2", Integer(16, True, None), 8),
                ("field3", Integer(32, True, None), 24),
                ("field4", Integer(64, True, None), 56),
                ("field5", Integer(8, False, None), 120),
                ("field6", Integer(16, False, None), 128),
                ("field7", Integer(32, False, None), 144),
                ("field8", Integer(64, False, None), 176),
                ("field9", Float(32, None), 240),
                ("field10", Float(64, None), 272)
            ])

    def test_reserved_fields(self):
            _, _, model = build_model_from_text('''
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
            ''', "")

            self.assertEqual(len(model.datatypes), 1)
            datatype = model.datatypes[0]

            # Reserved fields are not part of the model since we don't need to do anything with them in the backend
            self.verify_datatype(datatype, "SomeDataType", [
                ("field1", Integer(8, True, None), 0),
                ("field3", Integer(32, True, None), 24),
                ("field5", Integer(8, False, None), 120),
                ("field7", Integer(32, False, None), 144),
                ("field9", Float(32, None), 240)
            ])

    def test_non_standard_width(self):
        _, _, model = build_model_from_text('''
    SomeDataType
    {
        field1 : int32;   
        {     
            field2 : int5;
            field3 : uint20;
            field4 : int7;
        }
        field5 : float64;
    }
            ''', "")

        self.verify_datatype(model.datatypes[0], 'SomeDataType', [
            ('field1', Integer(32, True, None),   0, 32, 0,  0xffffffff),
            ('field2', Integer(5, True, None),   32, 32, 32, 0x0000001f),
            ('field3', Integer(20, False, None), 37, 32, 32, 0x01ffffe0),
            ('field4', Integer(7, True, None),   57, 32, 32, 0xfe000000),
            ('field5', Float(64, None),          64, 64, 64, 0xffffffffffffffff)
        ])

    def test_non_standard_width_with_padding(self):
        _, _, model = build_model_from_text('''
    SomeDataType
    {
        field1 : int32;   
        {     
            field2 : int5;
            int3;
            field3 : uint10;
            field4 : int14;
        }
        field5 : float64;
    }
            ''', "")
        # name, type, offset, size, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask
        self.verify_datatype(model.datatypes[0], 'SomeDataType', [
            ('field1', Integer(32, True, None),    0, 32, 0,  0xffffffff),
            ('field2', Integer(5, True, None),    32, 32, 32, 0x0000001f),
            ('field3', Integer(10, False, None),  40, 32, 32, 0x0003ff00),
            ('field4', Integer(14, True, None),   50, 32, 32, 0xfffc0000),
            ('field5', Float(64, None),           64, 64, 64, 0xffffffffffffffff)
        ])

    def test_non_standard_width_alias(self):
        _, _, model = build_model_from_text('''
    SomeDataType
    {
        field1 : s32;   
        {     
            field2 : s5;
            s3;
            field3 : u10;
            field4 : s14;
        }
        field5 : f64;
    }
            ''', "")

        self.verify_datatype(model.datatypes[0], 'SomeDataType', [
            ('field1', Integer(32, True, None),  0, 32,  0, 0xffffffff),
            ('field2', Integer(5, True, None),  32, 32, 32, 0x0000001f),
            ('field3', Integer(10, False, None),40, 32, 32, 0x0003ff00),
            ('field4', Integer(14, True, None), 50, 32, 32, 0xfffc0000),
            ('field5', Float(64, None),         64, 64, 64, 0xffffffffffffffff)
        ])


    def verify_datatype(self, datatype, expected_name, expected_fields):
        self.assertEqual(datatype.identifier, expected_name)
        self.assertEqual(len(datatype.fields), len(expected_fields))
        for field, expected in zip(datatype.fields, expected_fields):
            expected = expected + tuple([None] * (6-len(expected)))
            name, type, offset, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask = expected
            self.verify_field(field, name, type, offset, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask)

    def verify_field(self, field, name, field_type, offset, encapsulating_type_size, encapsulating_type_offset, encapsulating_type_mask):
        self.assertEqual(field.name, name)
        #self.assertEqual(field.type, type)
        self.assertTrue(type(field_type) is type(field._type))

        self.assertEqual(field.offset, offset)
        self.assertEqual(field.size_in_bits(), field_type.size_in_bits())
        if encapsulating_type_size is not None:
            self.assertEqual(field.capture_size, encapsulating_type_size)
        if encapsulating_type_offset is not None:
            self.assertEqual(field.capture_type_offset(), encapsulating_type_offset)
        if encapsulating_type_mask is not None:
            self.assertEqual(field.capture_type_mask(), encapsulating_type_mask)
