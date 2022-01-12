from BackEnd.cpp.Fields.Integral import Integral
import math

class Integer(Integral):
    def __init__(self, type_name, field, endianness, settings):
        super().__init__(type_name, field, endianness)
        self._settings = settings

    def cpp_type(self):
        return self.to_cpp_type(self._field.standard_size(), self._field.is_signed_type())

    def default_value(self):
        return '0'

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

    def to_string_code(self, string_stream_var_name:str):
        if self._field.return_type_size() == 8:
            # cast to int to prevent this from being interpreted as an ASCII charactor
            if self._field.is_signed_type():
                return f'{string_stream_var_name} << static_cast<int>({self._field.name}());'
            else:
                return f'{string_stream_var_name} << static_cast<unsigned int>({self._field.name}());'
        else:
            return f'{string_stream_var_name} << {self._field.name}();'

    @staticmethod
    def to_cpp_type(size, signed):
        # assert disabled to give semantic analysis a chance to catch this
        # assert math.log(size, 2).is_integer(), "integer types should be a power of two in size. Not {}".format(size)
        if signed:
            return f'std::int{size}_t'
        else:
            return f'std::uint{size}_t'



