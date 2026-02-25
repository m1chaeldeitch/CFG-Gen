import pycparser.c_ast
from pycparser import c_ast
from pycparser.c_ast import NodeVisitor
from pycparser.c_ast import FuncCall

class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.found = False
        self.names = []

    def visit_FuncCall(self, node):
        if node.name.name == 'pthread_create': #Todo account for not just .name.name but expressions too?
            self.found = True
        else:
            self.names.append(node.name.name)

def find_pthread(ast):
    v = FuncCallVisitor()
    v.visit(ast)
    return v
