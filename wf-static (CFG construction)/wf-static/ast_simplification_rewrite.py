from pycparser import c_ast, parse_file
from pycparser.c_ast import For
from pycparser.c_ast import While
from pycparser.c_ast import DoWhile

class CompoundVisitor(c_ast.NodeVisitor):
    def visit_Compound(self, node):
        print("Found compound node")
        if hasattr(node, 'block_items'):
            for index, sub_node in enumerate(node.block_items): #https://stackoverflow.com/questions/19162285/get-index-in-the-list-of-objects-by-attribute-in-python
                if isinstance(sub_node, For):
                    print(f"[Coord] -> [File = {sub_node.coord.file}] [Line = {sub_node.coord.line}]\n")
                    coord = sub_node.coord
                    stmt = sub_node.stmt
                    cond = sub_node.cond

                    replacement_while = While(cond, stmt, coord)
                    replacement_while.stmt.block_items.append(sub_node.next)

                    decls = node.block_items[index].init.decls
                    for decl in decls:
                        node.block_items.insert(index, decl)
                        index = index + 1

                    node.block_items[index] = replacement_while
                elif isinstance(sub_node, DoWhile):
                    coord = sub_node.coord
                    stmt = sub_node.stmt
                    cond = sub_node.cond

                    replacement_while = While(cond, stmt, coord)
                    node.block_items[index] = replacement_while

                self.visit(sub_node)

    def visit_Case(self, node):
        print(f"Found a case node at line: {node.coord.line}")

        if hasattr(node, 'stmts') and node.stmts is not None:
            for index, sub_node in enumerate(
                    node.stmts):  # https://stackoverflow.com/questions/19162285/get-index-in-the-list-of-objects-by-attribute-in-python
                if isinstance(sub_node, For):
                    print(f"[Coord] -> [File = {sub_node.coord.file}] [Line = {sub_node.coord.line}]\n")
                    coord = sub_node.coord
                    stmt = sub_node.stmt
                    cond = sub_node.cond

                    replacement_while = While(cond, stmt, coord)
                    replacement_while.stmt.block_items.append(sub_node.next)

                    decls = node.stmts[index].init.decls
                    for decl in decls:
                        node.stmts.insert(index, decl)
                        index = index + 1

                    node.stmts[index] = replacement_while
                elif isinstance(sub_node, DoWhile):
                    coord = sub_node.coord
                    stmt = sub_node.stmt
                    cond = sub_node.cond

                    replacement_while = While(cond, stmt, coord)
                    node.stmts[index] = replacement_while

                self.visit(sub_node)


class IfVisitor(c_ast.NodeVisitor):

    def visit_If(self, node):
        node.coord = "EVIDENCE"
        if hasattr(node, 'iffalse') and node.iffalse is not None:
            self.visit(node.iffalse)
        if hasattr(node, 'ifftrue') and node.iffalse is not None:
            self.visit(node.ifftrue)


class ForVisitor(c_ast.NodeVisitor):
    def visit_For(self, node):
        print(f"Found a 'for' node on line: {node.coord.line}")
        self.visit(node.stmt)


## Testing purposes so that I can identify with certainty that even the most nested 'for' nodes
## have been converted -- saves time having to look through the debugger
def find_fors(ast):
    print("===================")
    print("Below are the lines on which a 'for' node was found:")
    v = ForVisitor()
    v.visit(ast)
    print("===================")


def run(ast):
    #Transform all for-loops and do-while-loops to while-loops
    v = CompoundVisitor()
    v.visit(ast)

    v = IfVisitor()
    v.visit(ast)