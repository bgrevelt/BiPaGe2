import unittest
from compiler.build_model import build_model_from_text
from compiler.Model.types import SignedInteger, UnsignedInteger, Float

class BuilderUnittests(unittest.TestCase):
    def test_simple(self):
        _, _, models = build_model_from_text('''
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
        model = models[0]
        self.assertEqual(len(model.datatypes), 1)
        datatype = model.datatypes[0]

        self.verify_datatype(datatype, "SomeDataType", [
            ("field1", SignedInteger(8, None), 0),
            ("field2", SignedInteger(16, None), 8),
            ("field3", SignedInteger(32, None), 24),
            ("field4", SignedInteger(64, None), 56),
            ("field5", UnsignedInteger(8, None), 120),
            ("field6", UnsignedInteger(16, None), 128),
            ("field7", UnsignedInteger(32, None), 144),
            ("field8", UnsignedInteger(64, None), 176),
            ("field9", Float(32, None), 240),
            ("field10", Float(64, None), 272)
        ])

    def test_alias(self):
            _, _, models = build_model_from_text('''
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
            model = models[0]

            self.assertEqual(len(model.datatypes), 1)
            datatype = model.datatypes[0]

            # Aliases get turned into their counterpart types in the builder so the backend only needs to be worried
            # about those typessou
            self.verify_datatype(datatype, "SomeDataType", [
                ("field1", SignedInteger(8, None), 0),
                ("field2", SignedInteger(16, None), 8),
                ("field3", SignedInteger(32, None), 24),
                ("field4", SignedInteger(64, None), 56),
                ("field5", UnsignedInteger(8, None), 120),
                ("field6", UnsignedInteger(16, None), 128),
                ("field7", UnsignedInteger(32, None), 144),
                ("field8", UnsignedInteger(64, None), 176),
                ("field9", Float(32, None), 240),
                ("field10", Float(64, None), 272)
            ])

    def test_reserved_fields(self):
            _, _, models = build_model_from_text('''
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
            model = models[0]

            self.assertEqual(len(model.datatypes), 1)
            datatype = model.datatypes[0]

            # Reserved fields are not part of the model since we don't need to do anything with them in the backend
            self.verify_datatype(datatype, "SomeDataType", [
                ("field1", SignedInteger(8, None), 0),
                ("field3", SignedInteger(32, None), 24),
                ("field5", UnsignedInteger(8, None), 120),
                ("field7", UnsignedInteger(32, None), 144),
                ("field9", Float(32, None), 240)
            ])

    def test_non_standard_width(self):
        _, _, models = build_model_from_text('''
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
        model = models[0]

        self.verify_datatype(model.datatypes[0], 'SomeDataType', [
            ('field1', SignedInteger(32, None),   0, 32, 0,  0xffffffff),
            ('field2', SignedInteger(5, None),   32, 32, 32, 0x0000001f),
            ('field3', UnsignedInteger(20, None), 37, 32, 32, 0x01ffffe0),
            ('field4', SignedInteger(7, None),   57, 32, 32, 0xfe000000),
            ('field5', Float(64, None),          64, 64, 64, 0xffffffffffffffff)
        ])

    def test_non_standard_width_with_padding(self):
        _, _, models = build_model_from_text('''
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
        model = models[0]
        # name, type, offset, size, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask
        self.verify_datatype(model.datatypes[0], 'SomeDataType', [
            ('field1', SignedInteger(32, None),    0, 32, 0,  0xffffffff),
            ('field2', SignedInteger(5, None),    32, 32, 32, 0x0000001f),
            ('field3', UnsignedInteger(10, None),  40, 32, 32, 0x0003ff00),
            ('field4', SignedInteger(14, None),   50, 32, 32, 0xfffc0000),
            ('field5', Float(64, None),           64, 64, 64, 0xffffffffffffffff)
        ])

    def test_non_standard_width_alias(self):
        _, _, models = build_model_from_text('''
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
        model = models[0]

        self.verify_datatype(model.datatypes[0], 'SomeDataType', [
            ('field1', SignedInteger(32, None),  0, 32,  0, 0xffffffff),
            ('field2', SignedInteger(5, None),  32, 32, 32, 0x0000001f),
            ('field3', UnsignedInteger(10, None),40, 32, 32, 0x0003ff00),
            ('field4', SignedInteger(14, None), 50, 32, 32, 0xfffc0000),
            ('field5', Float(64, None),         64, 64, 64, 0xffffffffffffffff)
        ])


    def verify_datatype(self, datatype, expected_name, expected_fields):
        self.assertEqual(datatype.identifier, expected_name)
        self.assertEqual(len(datatype.fields()), len(expected_fields))
        for field, expected in zip(datatype.fields(), expected_fields):
            expected = expected + tuple([None] * (6-len(expected)))
            name, type, offset, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask = expected
            self.verify_field(field, name, type, offset, encapsulating_type_size, encalsulating_type_offset, encapsulating_type_mask)

    def verify_field(self, field, name, field_type, offset, encapsulating_type_size, encapsulating_type_offset, encapsulating_type_mask):
        self.assertEqual(field.name, name)
        #self.assertEqual(field.type, type)
        self.assertTrue(type(field_type) is type(field._type))

        offset_in_capture = 0 if encapsulating_type_offset is None else offset-encapsulating_type_offset
        self.assertEqual(field.offset_in_capture, offset_in_capture)
        self.assertEqual(field.size_in_bits(), field_type.size_in_bits())
        if encapsulating_type_size is not None:
            self.assertEqual(field.capture_size(), encapsulating_type_size)
        if encapsulating_type_offset is not None:
            self.assertEqual(field.static_capture_offset(), encapsulating_type_offset)
        if encapsulating_type_mask is not None:
            self.assertEqual(field.capture_type_mask(), encapsulating_type_mask)
