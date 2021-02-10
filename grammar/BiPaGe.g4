grammar BiPaGe;

// Lexer rules
Whitespace: [ \t\r\n\u000C]+ -> skip;
MultiLineComment: '/*' .*? '*/' -> skip;
SingleLineComment: '//' ~('\r' | '\n')* -> skip;

IntegerType: ('int' | 'uint' | 's' | 'u' ) NumberLiteral;
FloatingPointType: ('float' | 'f' ) ('32' | '64' );
NumberLiteral: '-'?[0-9]+;

NameSpace: 'namespace';
Identifier: ('a'..'z'|'A'..'Z'|'_')('a'..'z'|'A'..'Z'|'_'|'0'..'9')*;
EndiannessDecorator: '@'('bigendian'|'littleendian');
SemiColon: ';';

// Parser rules
definition: namespace? endianness? (datatype|enumeration)+;
namespace: NameSpace Identifier ('.'Identifier)* SemiColon;
endianness: EndiannessDecorator SemiColon;
datatype: Identifier '{' field+ '}';
enumeration: Identifier ':' IntegerType '{' (enumerand ',')* enumerand '}';
enumerand: Identifier '=' NumberLiteral;
field: simple_field | capture_scope;
simple_field: (Identifier ':')? field_type ';';
capture_scope: '{' simple_field+ '}';
field_type: IntegerType | FloatingPointType | Identifier;