from .Field import Field
import math


def _to_cpp_type(size, signed):
    # assert disabled to give semantic analysis a chance to catch this
    #assert math.log(size, 2).is_integer(), "integer types should be a power of two in size. Not {}".format(size)
    if signed:
        return f'std::int{size}_t'
    else:
        return f'std::uint{size}_t'


class Integer(Field):
    def __init__(self, type_name, field, endianness, settings):
        super().__init__(type_name, field, _to_cpp_type(field.standard_size, field.is_signed_type()), '0', endianness, settings)
        self._scoped = field.scoped
        self.capture_type = _to_cpp_type(field.capture_size, field.is_signed_type())

    def builder_serialize_code(self):
        if not self._scoped:
            return super().builder_serialize_code()

        offset_in_byte = (self._field.offset - self._field.capture_offset)
        mask = (2 ** self._field.size_in_bits() - 1) << offset_in_byte  # mask should not include sign bit

        r = f'{self.capture_type} {self._field.name} = {self._field.name}_;\n'
        if offset_in_byte != 0:
            r += f'{self._field.name} <<= {offset_in_byte};\n'

        r += f'{self._field.name} &= 0x{mask:x};\n'

        # Note: byte swapping for big endian types happens at the datatype level so we can swap the
        # entire capture scope at once

        r += f'*reinterpret_cast<{self.capture_type}*>(sink + {self._offset_name()}) |= {self._field.name};\n\n'
        return r

    def builder_setter_code(self):
        # only add validation code for non-standard width types and when validation generation is enabled
        if self._field.is_standard_size() or not self._settings.cpp_validate_input:
            return super().builder_setter_code()

        return \
        f'''void {self._field.name}({self._cpp_type} val) 
        {{ 
            {self.validation_code("val")}
            {self._field.name}_ = val; 
        }}'''

    def view_getter_code(self):
        if not self._scoped:
            return super().view_getter_code()

        fieldname = self._field.name
        return_type = _to_cpp_type(self._field.standard_size, self._issigned())
        body = self._body()

        return f'''{return_type} {fieldname}() const
        {{
            {body}
        }}'''

    def _body(self):
        capture_type = _to_cpp_type(self._field.capture_size, self._issigned())

        body = f'auto capture_type = *reinterpret_cast<const {capture_type}*>(data_ + {self._offset_name()});\n'
        if self._endianness == 'big' and self._field.size_in_bits() != 8:
            body += 'capture_type = BiPaGe::swap_bytes(capture_type);'
        body += self._add_shift()
        body += self._add_mask()
        body += self._add_return()

        return body

    def _add_shift(self):
        offset_in_byte = self._field.offset - self._field.capture_offset
        if offset_in_byte != 0:
            return f'capture_type >>= {offset_in_byte};\n'
        else:
            return ""

    def _add_mask(self):
        if not self._issigned():
            mask = 2 ** self._field.size_in_bits() - 1
            return f'capture_type &= 0x{mask:x};\n'
        else:
            r = ""
            mask = 2 ** (self._field.size_in_bits() - 1) - 1  # mask should not include sign bit
            sign_mask = 2 ** (self._field.size_in_bits() - 1)
            sign_mask_return_type = (2 ** (self._field.standard_size) - 1) - mask

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
        return_type = _to_cpp_type(self._field.standard_size, self._issigned())

        if self._field.capture_size != self._field.standard_size:
            return f'return static_cast<{return_type}>(capture_type);'
        else:
            return 'return capture_type;'

    def _issigned(self):
        return self._field.is_signed_type()

    def validation_code(self, variable_name):
        if self._field.is_standard_size():
            return ""

        type = "signed integer" if self._issigned() else "unsigned integer"
        error_msg = f'"Value " + std::to_string({variable_name}) + " cannot be assigned to {type} of {self._field.size_in_bits()} bits"'

        if self._issigned():
            min = int(-1 * math.pow(2, self._field.size_in_bits() -1))
            max = int(math.pow(2, self._field.size_in_bits() -1) -1)

            return \
            f'''if(({variable_name} < {min}) || ({variable_name} > {max}))
            {{
                throw std::runtime_error({error_msg});
            }}'''
        else:
            max = int(math.pow(2, self._field.size_in_bits()) -1)
            return \
            f'''if({variable_name} > {max})
            {{
                throw std::runtime_error({error_msg});
            }}'''



