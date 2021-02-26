grammar BiPaGe;

// Lexer rules
Whitespace: [ \t\r\n\u000C]+ -> skip;
MultiLineComment: '/*' .*? '*/' -> skip;
SingleLineComment: '//' ~('\r' | '\n')* -> skip;

IntegerType: ('int' | 'uint' | 's' | 'u' ) NumberLiteral;
FloatingPointType: ('float' | 'f' ) ('32' | '64' );
FlagType: 'flag';
NumberLiteral: '-'?[0-9]+;

NameSpace: 'namespace';
Identifier: ('a'..'z'|'A'..'Z'|'_')('a'..'z'|'A'..'Z'|'_'|'0'..'9')*;
EndiannessDecorator: '@'('bigendian'|'littleendian');
SemiColon: ';';
FilePath: '"'((Identifier | '.' | '..') '/')* Identifier('.'Identifier)?'"';

// Parser rules
definition: import_rule* namespace? endianness? (datatype|enumeration)+;
namespace: NameSpace Identifier ('.'Identifier)* SemiColon;
endianness: EndiannessDecorator SemiColon;
import_rule: 'import' FilePath SemiColon;
datatype: Identifier '{' field+ '}';
enumeration: Identifier ':' IntegerType '{' (enumerand ',')* enumerand '}';
enumerand: Identifier '=' NumberLiteral;
field: simple_field | capture_scope | inline_enumeration | collection_field;
simple_field: (Identifier ':')? field_type ';';
collection_field: (Identifier ':')? field_type '[' NumberLiteral ']' ';';
inline_enumeration: Identifier ':' IntegerType '{' (enumerand ',')* enumerand '}' ';';
capture_scope: '{' (simple_field|inline_enumeration)+ '}';
field_type: IntegerType | FloatingPointType | FlagType | reference;
reference: (Identifier'.')* Identifier;