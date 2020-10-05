from .HelperFunctions import *
import math
class ViewGenerator:

    def GenerateDataTypeParser(self, DataType):
        template = \
'''class {typename}_view
{{
public:
    // You should not create or copy this class as it's just a view on raw data
    // Creating or copying this class will give you a class with one byte of data.
    {typename}_view() = delete;
    ~{typename}_view() = delete;
    {typename}_view(const {typename}_view&) = delete;
    {typename}_view& operator=(const {typename}_view&) = delete;

    {fields}

private:
    const std::uint8_t data_;
}};

const {typename}_view& Parse{typename}(const std::uint8_t* data) 
{{ 
    assert(data);
    return reinterpret_cast<const {typename}_view&>(*data);
}}
'''
        fields = "\n".join([self.GetFieldGetter(field) for field in DataType.fields])
        return template.format(typename=DataType.identifier, fields=fields)


    def GetFieldGetter(self, Field):
        template = \
'''{type} {fieldname}() const
{{
    {body}
}}'''
        non_standard_field = not Field.is_byte_aligned() or not Field.is_standard_size()
        body = self.GetSimpleFieldGetterBody(Field) if not non_standard_field else self.GetNonStandardIntFieldGetterBody(Field)
        return template.format(fieldname=Field.name, type=TypeToCppType(Field.type, Field.return_type_size()), body=body)

    def GetSimpleFieldGetterBody(self, Field):
        return 'return *reinterpret_cast<const {type}*>(&data_ + {offset});'.format(
            type=TypeToCppType(Field.type, Field.size_in_bits),
            offset=FieldOffsetName(Field)
        )

    def GetNonStandardIntFieldGetterBody(self, Field):
        encapsulating_type = TypeToCppType(Field.type, Field.encapsulating_type_size())
        return_type = TypeToCppType(Field.type, Field.return_type_size())
        offset_in_byte = Field.offset % 8


        r =f'auto encapsulating_type = *reinterpret_cast<const {encapsulating_type}*>(&data_ + {FieldOffsetName(Field)});\n'
        if offset_in_byte != 0:
            r += f'encapsulating_type >>= {offset_in_byte};\n'

        if Field.is_signed_type():
            mask = 2 ** (Field.size_in_bits - 1) -1 # mask should not include sign bit
            sign_mask = 2 ** (Field.size_in_bits -1)
            sign_mask_return_type = (2 ** (Field.return_type_size()) -1) - mask;

            r += f'bool negative = ((encapsulating_type & 0x{sign_mask:x}) == 0x{sign_mask:x});\n'
            r += f'encapsulating_type &= 0x{mask:x};\n'
            r += f'''if(negative)
            {{
                // Set sign bit and all bits that are not part of the data (2's complement).
                encapsulating_type |= 0x{sign_mask_return_type:x}; 
            }}
            '''
        else:
            mask = 2 ** Field.size_in_bits - 1
            r += f'encapsulating_type &= 0x{mask:x};\n'

        if(return_type != encapsulating_type):
            r += f'return static_cast<{return_type}>(encapsulating_type);\n';
        else:
            r += 'return encapsulating_type;\n'

        return r

    def GetIncludes(self):
        return ['<cstdint>', '<assert.h>']
