from BackEnd.cpp.Fields.Field import Field
from Model.Field import Field as ModelField
import Model.expressions
from Model.Collection import Collection as ModelCollection

class Collection(Field):
    def __init__(self, type_name:str, field:ModelField, cpp_type, endianness:str):
        self._collection_type = cpp_type
        self._is_enum_collection = type(field.type().type()) is Model.expressions.EnumerationReference
        super().__init__(type_name, field, endianness)

        self._collection_size = f'static_cast<size_t>({self._convert_expression(self._field.type().collection_size())})'

    def getter_body(self):
        return f'return {self.cpp_type()}(data_ + {self._dynamic_offset}{self.offset_name()}, {self._collection_size});'

    def cpp_type(self):
        if self._is_big_endian():
            return f'BiPaGe::CollectionBigEndian<{self._collection_type}>'
        else:
            return f'BiPaGe::CollectionLittleEndian<{self._collection_type}>'

    def default_value(self):
        return ""

    def includes(self):
        return ['<BiPaGe/Collection.h>']

    def builder_parameter_code(self):
        return f'std::vector<{self._collection_type}> {self._field.name}'

    def builder_field_code(self):
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
        if type(self._field.type().type()) is Model.expressions.DataTypeReference:
            #TODO
            return ''

        return f'''auto {self._field.name}_iterator = {self._field.name}();
            {string_stream_var_name} << "[ ";
            for(auto current = {self._field.name}_iterator.begin() ; current < {self._field.name}_iterator.end() ; ++current)
            {{
                {string_stream_var_name} << {"enum_to_string(*current)" if self._is_enum_collection else "*current"} << (current < ({self._field.name}_iterator.end()-1) ? ", " : "");
            }}
            {string_stream_var_name} << " ]";'''

    def builder_serialize_body(self):
        if not self._is_big_endian():
            return f'''for(size_t i = 0 ; i < {self._collection_size} ; ++i)
            {{
                    *(reinterpret_cast<{self._collection_type}*>(sink + {self._dynamic_offset}{self.offset_name()}) + i) = {self._field.name}_[i];
            }}
            '''
        else:
            return f'''for(size_t i = 0 ; i < {self._collection_size} ; ++i)
            {{
                *(reinterpret_cast<{self._collection_type}*>(sink + {self._dynamic_offset}{self.offset_name()}) + i) = BiPaGe::swap_bytes({self._field.name}_[i]);
            }}'''

    def _is_big_endian(self):
        collection = self._field.type()
        assert type(collection) is ModelCollection, f"We're building a collection object but the model type passed in is not an object, but {collection}"
        return self._endianness == 'big' and collection.element_size_in_bits() != 8

    def _convert_binary_expression(self, expression, operation):
        return f'({self._convert_expression(expression.left())} {operation} {self._convert_expression(expression.right())})'


    def _convert_expression(self, expression):
        expression_type = type(expression)
        if expression_type is Model.expressions.NumberLiteral:
            return expression.evaluate()
        elif expression_type is Model.expressions.FieldReference:
            return f'{expression.name()}()'
        elif expression_type is Model.expressions.EnumerationReference:
            assert False, "This should have been caught in semantic analysis"
        elif expression_type is Model.expressions.EnumeratorReference:
            return expression.fully_qualified_name().replace('.', '::')
        elif expression_type is Model.expressions.EqualsOperator:
            return self._convert_binary_expression(expression, '==')
        elif expression_type is Model.expressions.NotEqualsOperator:
            return self._convert_binary_expression(expression, '!=')
        elif expression_type is Model.expressions.MultiplyOperator:
            return self._convert_binary_expression(expression, '*')
        elif expression_type is Model.expressions.DivisionOperator:
            return self._convert_binary_expression(expression, '/')
        elif expression_type is Model.expressions.AddOperator:
            return self._convert_binary_expression(expression, '+')
        elif expression_type is Model.expressions.SubtractOperator:
            return self._convert_binary_expression(expression, '-')
        elif expression_type is Model.expressions.LessThanOperator:
            return self._convert_binary_expression(expression, '<')
        elif expression_type is Model.expressions.LessThanEqualOperator:
            return self._convert_binary_expression(expression, '<=')
        elif expression_type is Model.expressions.GreaterThanOperator:
            return self._convert_binary_expression(expression, '>')
        elif expression_type is Model.expressions.GreaterThanEqualOperator:
            return self._convert_binary_expression(expression, '>=')
        elif expression_type is Model.expressions.TernaryOperator:
            return f'({self._convert_expression(expression.condition())} ? {self._convert_expression(expression.true_clause())} : {self._convert_expression(expression.false_clause())})'
        else:
            assert False, f'Unhandled expression type {expression_type}: {expression}'

    def size_builder(self, field_name):
        return f'{field_name}_.size() * sizeof(decltype ({field_name}_)::value_type)'

    def size_view(self, field_name):
        return f'{field_name}().size_in_bytes()'


class DataTypeCollection(Collection):
    def __init__(self, type_name:str, field:ModelField, cpp_type, endianness:str):
        self._view_type = f'{field.type().type().name()}_view'
        self._builder_type = f'{field.type().type().name()}_builder'
        super().__init__(type_name, field, cpp_type, endianness)

    def cpp_type(self):
            return f'BiPaGe::DataTypeCollection<{self._view_type}>'

    def includes(self):
        return super().includes() + ['<numeric>']

    def builder_parameter_code(self):
        return f'std::vector<{self._builder_type}> {self._field.name}'

    def builder_field_code(self):
            return f'std::vector<{self._builder_type}> {self._field.name}_;'

    def builder_setter_code(self):
        return \
        f'''void {self._field.name}(const std::vector<{self._builder_type}>& val) 
        {{ 
            {self._field.name}_ = val; 
        }}'''

    def builder_getter_code(self):
        return f'''const std::vector<{self._builder_type}>& {self._field.name}() const
        {{
            return {self._field.name}_;
        }}'''

    def to_string_code(self, string_stream_var_name):
        return f'''auto {self._field.name}_iterator = {self._field.name}();
        {string_stream_var_name} << "[ ";
        for(auto current = {self._field.name}_iterator.begin() ; current < {self._field.name}_iterator.end() ; ++current)
        {{
            {string_stream_var_name} << std::endl << "{{" << std::endl << current->to_string() << "}}" << (current < ({self._field.name}_iterator.end()-1) ? ", " : "");
        }}
        {string_stream_var_name} << " ]";'''

    def builder_serialize_body(self):
        return f'''auto collection_start = sink + {self._dynamic_offset}{self.offset_name()};
        for(auto& elem : {self._field.name}_)
        {{
                elem.build(collection_start);
                collection_start += elem.size();
        }}
        '''
    def size_builder(self, field_name):
        return f'std::accumulate({field_name}_.begin(), {field_name}_.end(), 0, [](auto& l, auto& r){{return l + r.size();}});'

    def size_view(self, field_name):
        return f'{field_name}().size_in_bytes()'