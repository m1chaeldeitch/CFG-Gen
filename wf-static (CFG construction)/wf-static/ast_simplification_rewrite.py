from pycparser import c_ast, parse_file
from pycparser.c_ast import For
from pycparser.c_ast import While
from pycparser.c_ast import DoWhile

class CompoundVisitor(c_ast.NodeVisitor):
    def visit_Compound(self, node):
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
                        node.block_items.insert(index, decl)  #todo might need to change for when the init has multiple decls?
                        index = index + 1

                    node.block_items[index] = replacement_while
                elif isinstance(sub_node, DoWhile):
                    coord = sub_node.coord
                    stmt = sub_node.stmt
                    cond = sub_node.cond

                    replacement_while = While(cond, stmt, coord)
                    node.block_items[index] = replacement_while


def run(ast):
    #Transform all for-loops and do-while-loops to while-loops
    v = CompoundVisitor()
    v.visit(ast)