from ..HelperFunctions import *

class Field():
    def __init__(self, field):
        self._field = field
        self._getter_template =\
'''{type} {fieldname}() const
{{
    {body}
}}'''

    def view_getter_code(self):
        return '''{type} {fieldname}() const
                {{
                    return *reinterpret_cast<const {type}*>(&data_ + {offset});
                }}'''.format(
            type=TypeToCppType(self._field.type, self._field.size_in_bits),
            offset=FieldOffsetName(self._field),
            fieldname=self._field.name)

    def builder_setter_code(self):
        return f'''void {self._field.name}({TypeToCppType(self._field.type, self._field.encapsulating_type_size())} val) 
{{ 
    {self._field.name}_ = val; 
}}'''

    def builder_getter_code(self):
        return f'''{TypeToCppType(self._field.type, self._field.encapsulating_type_size())} {self._field.name}() const
        {{
            return {self._field.name}_;
        }}'''

    def builder_serialize_code(self):
        return f'*reinterpret_cast<{TypeToCppType(self._field.type, self._field.encapsulating_type_size())}*>(sink + {FieldOffsetName(self._field)}) = {self._field.name}_;\n'