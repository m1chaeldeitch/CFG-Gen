import pycparser.c_ast
from pycparser import c_ast
from pycparser.c_ast import NodeVisitor
from pycparser.c_ast import FuncCall

class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self, desired_func_name):
        self.found = False
        self.names = []
        self.desired_func = desired_func_name

    def visit_FuncCall(self, node):
        if node.name.name == self.desired_func: #Todo account for not just .name.name but expressions too?
            self.found = True
        else:
            self.names.append(node.name.name)

def find_func(ast, desired_func_name):
    v = FuncCallVisitor(desired_func_name)
    v.visit(ast)
    return v
