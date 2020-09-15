grammar BiPaGe;

// Lexer rules
Whitespace: [ \t\r\n\u000C]+ -> skip;
MultiLineComment: '/*' .*? '*/' -> skip;
SingleLineComment: '//' ~('\r' | '\n')* -> skip;

Type: (('int' | 'uint' | 'float' | 'i' | 'u' | 'f') ('8' | '16' | '32' | '64')) | 'bool';
Identifier: ('a'..'z'|'A'..'Z'|'_')('a'..'z'|'A'..'Z'|'_'|'0'..'9')*;

// Parser rules
elements: element+;
element: Identifier '{' field+ '}';
field: Identifier ':' Type ';';