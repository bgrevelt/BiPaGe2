class Beautifier:
    def __init__(self, tabsize=4):
        self._tab = tabsize * ' '
        self.indent = 0
        self.unindent_tokens = [
            '}',
            'private:',
            'public:'
        ]

    def beautify(self, code):
        lines = []
        for line in code.splitlines():
            line = line.lstrip()
            line = self.indent_line(line)
            lines.append(line)
            self.update_indent_level(line)
        return "\n".join(lines)

    def indent_line(self, line):
        line_indent = self.indent
        if any(line.startswith(token) for token in self.unindent_tokens):
            line_indent = 0 if line_indent <= 0 else line_indent -1
        return (line_indent * self._tab) + line

    def update_indent_level(self, line):
        inc_chars = '{('
        dec_chars = '})'
        for char in line:
            if any(char == inc_char for inc_char in inc_chars):
                self.indent += 1
            if any(char == dec_char for dec_char in dec_chars):
                self.indent -= 1