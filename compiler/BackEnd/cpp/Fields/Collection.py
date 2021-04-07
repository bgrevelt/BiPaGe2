from BackEnd.cpp.Fields.Field import Field
from Model.Field import Field as ModelField
from Model.Types.Reference import Reference as ModelRef

class Collection(Field):
    def __init__(self, type_name:str, field:ModelField, cpp_type, endianness:str, settings):
        self._collection_type = cpp_type
        self._is_enum_collection = type(field.type().type()) is ModelRef
        super().__init__(type_name, field, endianness)

    def getter_body(self):
        return f'return {self.cpp_type()}(data_ + {self._offset_name()});'

    def cpp_type(self):
        collection = self._field.type()
        if self._endianness == 'big' and self._field.size_in_bits() != 8:
            return f'BiPaGe::CollectionBigEndian<{self._collection_type},{collection.collection_size()}>'
        else:
            return f'BiPaGe::CollectionLittleEndian<{self._collection_type},{collection.collection_size()}>'

    def default_value(self):
        return ""

    def includes(self):
        return ['<BiPaGe/Collection.h>']

    def builder_parameter_code(self):
        # std::uintt_t foo
        return f'std::vector<{self._collection_type}> {self._field.name}'

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

    def to_string_code(self, string_stream_var_name):
        return f'''auto {self._field.name}_iterator = {self._field.name}();
            {string_stream_var_name} << "[ ";
            for(auto current = {self._field.name}_iterator.begin() ; current < {self._field.name}_iterator.end() ; ++current)
                {string_stream_var_name} << {"enum_to_string(*current)" if self._is_enum_collection else "*current"} << (current < ({self._field.name}_iterator.end()-1) ? ", " : "");
            {string_stream_var_name} << " ]";'''

    def builder_serialize_body(self, ):
        collection_size = self._field.type().collection_size()
        if self._endianness == 'little' or self._field.size_in_bits() == 8:
            return f'''for(size_t i = 0 ; i < {collection_size} ; ++i)
                    *(reinterpret_cast<{self._collection_type}*>(sink + {self._offset_name()}) + i) = {self._field.name}_[i];
                '''
        else:
            return f'''for(size_t i = 0 ; i < {collection_size} ; ++i)
                            *(reinterpret_cast<{self._collection_type}*>(sink + {self._offset_name()}) + i) = BiPaGe::swap_bytes({self._field.name}_[i]);'''