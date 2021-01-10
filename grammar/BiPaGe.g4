grammar BiPaGe;

// Lexer rules
Whitespace: [ \t\r\n\u000C]+ -> skip;
MultiLineComment: '/*' .*? '*/' -> skip;
SingleLineComment: '//' ~('\r' | '\n')* -> skip;

Type: IntegerType | FloatingPointType;
IntegerType: ('int' | 'uint' | 's' | 'u' ) NumberLiteral;
FloatingPointType: ('float' | 'f' ) ('32' | '64' );
NumberLiteral: [0-9]+;

Identifier: ('a'..'z'|'A'..'Z'|'_')('a'..'z'|'A'..'Z'|'_'|'0'..'9')*;

// Parser rules
definition: datatype+;
datatype: Identifier '{' field+ '}';
field: simple_field | scoped_field;
simple_field: (Identifier ':')? Type ';';
scoped_field: '{' simple_field+ '}';