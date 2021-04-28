class Beautifier:
    def __init__(self, tabsize=4):
        self._tab = tabsize * ' '
        self.indent = 0
        self.unindent_tokens = [
            '}',
            'private:',
            'public:'
        ]
        self.switch_indent_level = None

    def beautify(self, code):
        lines = []
        input_lines = code.splitlines()
        for i, line in enumerate(input_lines):
            line = line.lstrip()
            if len(line) == 0 and (i == 0 or len(input_lines[i - 1].lstrip()) == 0):
            #if len(line) == 0 and (i == 0 or not any(c in input_lines[i-1] for c in ";}")):
            #if len(line) == 0:
                continue  # skip over empty lines unless the previous line contains a statement or closing brace
            line = self.indent_line(line)
            lines.append(line)
            self.update_indent_level(line)
            self.check_switch(line)
        return "\n".join(lines)

    def indent_line(self, line):
        line_indent = self.indent
        if any(line.startswith(token) for token in self.unindent_tokens):
            line_indent = max(0, line_indent-1)
        return (line_indent * self._tab) + line

    def update_indent_level(self, line):
        line = line.lstrip()

        inc_chars = '{('
        dec_chars = '})'
        for char in line:
            if any(char == inc_char for inc_char in inc_chars):
                self.indent += 1
            if any(char == dec_char for dec_char in dec_chars):
                self.indent -= 1

        if self.switch_indent_level is not None:
            if line.startswith('case') or line.startswith('default'):
                self.indent += 1
            elif line.startswith('break'):
                self.indent -= 1


    def check_switch(self, line):
        if self.switch_indent_level is None: # Not currently in a switch
            if line.startswith('switch'):
                self.switch_indent_level = self.indent
                print(f'IN SIWTCH {line}')
        else: # currently in a switch
            if self.indent == self.switch_indent_level: # closing brace for switch found
                self.switch_indent_level = None
                print(f'OUT SWITCH {line}')


