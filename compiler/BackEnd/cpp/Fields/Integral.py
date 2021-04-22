from BackEnd.cpp.Fields.Field import Field

class Integral(Field):
    def __init__(self, type_name, field, endianness):
        super().__init__(type_name, field, endianness)
        self._scoped = field.scoped()
        self.capture_type = self._to_cpp_type(field.capture_size, field.is_signed_type())

    def getter_body(self):
        if not self._scoped:
            body = f'*reinterpret_cast<const {self._cpp_type}*>(data_ + {self._dynamic_offset} {self.offset_name()})'
            body = self.add_swap_if_required(body);
            return f'return {body};'
        else:
            return self._body()

    def builder_serialize_body(self):
        if not self._scoped:
            return f'*reinterpret_cast<{self._cpp_type}*>(sink + {self._dynamic_offset} {self.offset_name()}) = {self.add_swap_if_required(self._field.name+"_")};\n'

        offset_in_byte = self._field.offset_in_capture
        mask = (2 ** self._field.size_in_bits() - 1) << offset_in_byte  # mask should not include sign bit

        if self.base_type() is not None:
            r = f'{self.capture_type} {self._field.name} = static_cast<{self.base_type()}>({self._field.name}_);\n'
        else:
            r = f'{self.capture_type} {self._field.name} = {self._field.name}_;\n'
        if offset_in_byte != 0:
            r += f'{self._field.name} <<= {offset_in_byte};\n'

        r += f'{self._field.name} &= 0x{mask:x};\n'

        # Note: byte swapping for big endian types happens at the datatype level so we can swap the
        # entire capture scope at once

        r += f'*reinterpret_cast<{self.capture_type}*>(sink + {self._dynamic_offset} {self.offset_name()}) |= {self._field.name};\n\n'
        return r

    # override for types that have a 'base' integral type (like enumerations)
    def base_type(self):
        return None

    def _body(self):
        capture_type = self._to_cpp_type()

        body = f'*reinterpret_cast<const {capture_type}*>(data_ + {self.offset_name()} {self._dynamic_offset})'
        body = f'auto capture_type = {self.add_swap_if_required(body)};\n'
        body += self._add_shift()
        body += self._add_mask()
        body += self._add_return()

        return body

    def _add_shift(self):
        if self._field.offset_in_capture is not None and self._field.offset_in_capture != 0:
            return f'capture_type >>= {self._field.offset_in_capture};\n'
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
            sign_mask_return_type = (2 ** self._field.standard_size - 1) - mask

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
        if self._field.capture_size != self._field.standard_size or self.base_type() is not None:
            return f'return static_cast<{self.cpp_type()}>(capture_type);'
        else:
            return 'return capture_type;'

    def _to_cpp_type(self, size=None, signed=None):
        if size is None:
            size = self._field.capture_size
        if signed is None:
            signed = self._issigned()
        # assert disabled to give semantic analysis a chance to catch this
        # assert math.log(size, 2).is_integer(), "integer types should be a power of two in size. Not {}".format(size)
        if signed:
            return f'std::int{size}_t'
        else:
            return f'std::uint{size}_t'

    def _issigned(self):
        return self._field.is_signed_type()