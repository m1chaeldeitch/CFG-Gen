import ast
from astmonkey import visitors, transformers

class File(object):
    def __init__(self, expr, symtable):
        self._expr = expr
        self._symtable = symtable

    def to_string(self):

        if isinstance(self._expr, ast.Name):
            entry = self._symtable[self._expr.id]

            if entry.assignment_count() == 1:

                return "Expr: " + visitors.to_source(entry.last_value())

        return "Expr: " + visitors.to_source(self._expr)

class FileManager(object):
    def __init__(self, symtable):

        self._files = []
        self._symtable = symtable

    def expressions_match(self, expr1, expr2):

        if isinstance(expr1, ast.Name) and isinstance(expr2, ast.Name):

            #TODO: also check if constant assignment
            return expr1.id == expr2.id

        return False

    def touch_file(self, expr):

        #check if the file has already been touched by something
        for file in self._files:
            if self.expressions_match(expr, file._expr):
                return file


        file = File(expr, self._symtable)

        self._files += [file]

        return file