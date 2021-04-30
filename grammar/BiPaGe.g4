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
datatype: Identifier '{' (field | capture_scope)+ '}';
enumeration: Identifier ':' IntegerType '{' (enumerand ',')* enumerand '}';
enumerand: Identifier '=' NumberLiteral;
field: (Identifier ':')? field_type multiplier? ';';
multiplier: ('[' expression ']');
field_type:
    IntegerType |
    FloatingPointType |
    FlagType |
    reference |
    inline_enumeration;
inline_enumeration: IntegerType '{' (enumerand ',')* enumerand '}';
capture_scope: '{' field+ '}';
reference: (Identifier'.')* Identifier;
expression: '(' expression ')'                          # Parens
          | '!' expression                              # Not
          | <assoc=right> expression '^' expression      # Power
          | expression op=('*'|'/') expression            # MultDiv
          | expression op=('+'|'-') expression            # AddSub
          | expression op=('<'|'<='|'>'|'>=') expression  # Relational
          | expression op=('=='|'!=') expression          # Equality
          | expression '?' expression                   # Ternary
          | NumberLiteral                               # Number
          | reference                                   # Ref
          ;