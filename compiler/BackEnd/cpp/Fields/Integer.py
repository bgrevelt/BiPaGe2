from .Field import Field
from ..HelperFunctions import *

class Integer(Field):
    def __init__(self, field):
        super().__init__(field)
        self._complex = (not field.is_byte_aligned() or not field.is_standard_size())

    def builder_serialize_code(self):
        if not self._complex:
            return super().builder_serialize_code()

        offset_in_byte = self._field.offset % 8
        mask = (2 ** self._field.size_in_bits - 1) << offset_in_byte  # mask should not include sign bit

        r = f'{TypeToCppType(self._field.type, self._field.encapsulating_type_size())} {self._field.name} = {self._field.name}_;\n'
        if offset_in_byte != 0:
            r += f'{self._field.name} <<= {offset_in_byte};\n'
        r += f'{self._field.name} &= 0x{mask:x};\n'
        r += f'*reinterpret_cast<{TypeToCppType(self._field.type, self._field.encapsulating_type_size())}*>(sink + {FieldOffsetName(self._field)}) |= {self._field.name};\n\n'
        return r

    def view_getter_code(self):
        if not self._complex:
            return super().view_getter_code()

        fieldname = self._field.name
        return_type = TypeToCppType(self._field.type, self._field.return_type_size())
        body = self._body()

        return f'''{return_type} {fieldname}() const
        {{
            {body}
        }}'''

    def _body(self):
        capture_type = TypeToCppType(self._field.type, self._field.encapsulating_type_size())

        body = f'auto capture_type = *reinterpret_cast<const {capture_type}*>(&data_ + {FieldOffsetName(self._field)});\n'
        body += self._add_shift()
        body += self._add_mask()
        body += self._add_return()

        return body

    def _add_shift(self):
        offset_in_byte = self._field.offset % 8
        if offset_in_byte != 0:
            return f'capture_type >>= {offset_in_byte};\n'
        else:
            return ""

    def _add_mask(self):
        if not self._issigned():
            mask = 2 ** self._field.size_in_bits - 1
            return f'capture_type &= 0x{mask:x};\n'
        else:
            r = ""
            mask = 2 ** (self._field.size_in_bits - 1) - 1  # mask should not include sign bit
            sign_mask = 2 ** (self._field.size_in_bits - 1)
            sign_mask_return_type = (2 ** (self._field.return_type_size()) - 1) - mask;

            r += f'bool negative = ((capture_type & 0x{sign_mask:x}) == 0x{sign_mask:x});\n'
            r += f'capture_type &= 0x{mask:x};\n'
            r += f'''if(negative)
                    {{
                        // Set sign bit and all bits that are not part of the data (2's complement).
                        capture_type |= 0x{sign_mask_return_type:x}; 
                    }}
                    '''
            return r

    def _add_return(self):
        capture_type = TypeToCppType(self._field.type, self._field.encapsulating_type_size())
        return_type = TypeToCppType(self._field.type, self._field.return_type_size())

        if (return_type != capture_type):
            return f'return static_cast<{return_type}>(capture_type);\n';
        else:
            return 'return capture_type;\n'

    def _issigned(self):
        return self._field.type == 'int'