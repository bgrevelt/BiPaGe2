grammar BiPaGe;

// Lexer rules
Whitespace: [ \t\r\n\u000C]+ -> skip;
MultiLineComment: '/*' .*? '*/' -> skip;
SingleLineComment: '//' ~('\r' | '\n')* -> skip;

Type: ('int' | 'uint' | 'float' | 's' | 'u' | 'f') ('8' | '16' | '32' | '64');
Identifier: ('a'..'z'|'A'..'Z'|'_')('a'..'z'|'A'..'Z'|'_'|'0'..'9')*;

// Parser rules
definition: datatype+;
datatype: Identifier '{' field+ '}';
field: (Identifier ':')? Type ';';