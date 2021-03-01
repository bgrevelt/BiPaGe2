from BackEnd.cpp.Fields.Field import Field
from Model.Field import Field as ModelField

class Collection(Field):
    def __init__(self, type_name:str, field:ModelField, cpp_type, endianness:str, settings):
        self._collection_type = cpp_type
        super().__init__(type_name, field, endianness)

    def cpp_type(self):
        collection = self._field.type()
        return f'BiPaGe::Collection<{self._collection_type},{collection.collection_size()}>'

    #todo
    def default_value(self):
        return ""

    def view_getter_code(self):
        return f'''{self.cpp_type()} {self._field.name}() const
        {{
            return {self.cpp_type()}(data_ + {self._offset_name()});
        }}'''

    def includes(self):
        return ['<BiPaGe/Collection.h>', '<vector>']

    def builder_parameter_code(self):
        # std::uintt_t foo
        return f'std::vector<{self._collection_type}> {self._field.name}'

    # def builder_initializer_code(self):
    #     # foo_(foo)
    #     return f'{self._field.name}_({self._field.name})'


    def builder_field_code(self):
        # std::uint8_t foo_ = 0;
        return f'std::vector<{self._collection_type}> {self._field.name}_;'

    def builder_setter_code(self):
        return \
        f'''void {self._field.name}(const std::vector<{self._collection_type}>& val) 
        {{ 
            {self._field.name}_ = val; 
        }}'''

    def builder_getter_code(self):
        return f'''const std::vector<{self._collection_type}>& {self._field.name}() const
        {{
            return {self._field.name}_;
        }}'''

    def to_string_code(self):
        return f'{self._field.name}().to_string()'

    def builder_serialize_code(self):
        collection_size = self._field.type().collection_size()
        # TODO: endianness
        # if self._endianness == 'little' or self._field.size_in_bits() == 8:
        #
        #     return f'*reinterpret_cast<{self._cpp_type}*>(sink + {self._offset_name()}) = {self._field.name}_;\n'
        # else:
        #     return f'*reinterpret_cast<{self._cpp_type}*>(sink + {self._offset_name()}) = BiPaGe::swap_bytes({self._field.name}_);\n'
        return f'''for(size_t i = 0 ; i < {collection_size} ; ++i)
                *(reinterpret_cast<{self._collection_type}*>(sink + {self._offset_name()}) + i) = {self._field.name}_[i];'''