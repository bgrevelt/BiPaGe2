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
EndiannessDecorator: '@'('bigendian'|'littleendian');
Namespace: 'namespace ' Identifier ('.'Identifier)* ';';

// Parser rules
definition: Namespace? EndiannessDecorator? datatype+;
datatype: Identifier '{' field+ '}';
field: simple_field | capture_scope;
simple_field: (Identifier ':')? Type ';';
capture_scope: '{' simple_field+ '}';