from generated.BiPaGeListener import BiPaGeListener
import os
from generated.BiPaGeLexer import BiPaGeLexer
from antlr4 import *
from ErrorListener import BiPaGeErrorListener
from generated.BiPaGeParser import BiPaGeParser
from Model.imports.ImportTree import ImportTree

def _set_error_listener(target, listener):
    target.removeErrorListeners()
    target.addErrorListener(listener)

def _make_abs(path):
    if os.path.isabs(path):
        return path
    else:
        cwd = os.path.split(os.path.abspath(path))[0]
        return os.path.abspath(os.path.join(cwd, path))

class ImportAnalyzer(BiPaGeListener):
    def __init__(self, path):
        self.imports = []
        self.path = _make_abs(path)

    def _make_abs(self, path):
        if os.path.isabs(path):
            return path
        else:
            cwd = os.path.split(os.path.abspath(self.path))[0]
            return os.path.abspath(os.path.join(cwd, path))

    def exitImport_rule(self, ctx:BiPaGeParser.Import_ruleContext):
        path = str(ctx.FilePath()).replace('"', '')
        path = self._make_abs(path)
        self.imports.append(path)


def get_imports_from_text(input, path):
    lexer = BiPaGeLexer(InputStream(input))
    parser = BiPaGeParser(CommonTokenStream(lexer))
    errorlistener = BiPaGeErrorListener(path)
    _set_error_listener(lexer, errorlistener)
    _set_error_listener(parser, errorlistener)
    tree = parser.definition()
    analyzer = ImportAnalyzer(path)
    if len(errorlistener.errors()) == 0:
        ParseTreeWalker().walk(analyzer, tree)
    return analyzer.imports, errorlistener.errors()


def get_imports_from_file(path):
    return get_imports_from_text(open(path).read(), path)

def get_import_tree(path):
    path = _make_abs(path)
    import_tree = ImportTree()
    to_analyze = {path}

    while len(to_analyze) > 0:
        path = to_analyze.pop()
        imports, errors = get_imports_from_file(path)
        if len(errors) > 0:
            return import_tree, errors
        import_tree.addnode(path, imports)
        to_analyze = to_analyze.union({i for i in imports if i not in import_tree})

    return import_tree, []




if __name__ == '__main__':
    files = {
        'a.bp': '''
        import "b.bp";
        import "d.bp";
        import "f.bp";
        Foo { f1:u8;}
        ''',
        'b.bp': '''
        import "c.bp";
        import "d.bp";
        import "e.bp";
        Foo { f1:u8;}
        ''',
        'c.bp': '''
        import "e.bp";
        import "f.bp";
        Foo { f1:u8;}
        ''',
        'd.bp': '''
        import "g.bp";
        import "f.bp";
        Foo { f1:u8;}
        ''',
        'e.bp': '''
        Foo { f1:u8;}
        ''',
        'f.bp': '''
        import "g.bp";
        Foo { f1:u8;}
        ''',
        'g.bp': '''
        Foo { f1:u8;}
        '''
    }

    for path, content in files.items():
        with open(path, 'w') as f:
            f.write(content)

    import_tree, errors = get_import_tree('a.bp')

    for imp in import_tree.imports_in_order():
        print(imp)

    for path in files.keys():
        os.remove(path)


    # t = '''import "a.bp";
    # import "B.bp";
    # Foo
    # {
    # f1: u8;
    # }'''
    #
    # imports, errors = get_imports_from_text(t, '/foo/bar/bla.bp')
    # print(errors)
    # print(imports)