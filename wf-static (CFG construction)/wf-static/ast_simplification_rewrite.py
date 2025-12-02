from pycparser import c_ast, parse_file
from pycparser.ast_transforms import fix_switch_cases
from pycparser.c_ast import For, Switch, Case, Default, If, BinaryOp, Compound, Return, Break
from pycparser.c_ast import While
from pycparser.c_ast import DoWhile
from pycparser import ast_transforms

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
        if hasattr(node, 'iffalse') and node.iffalse is not None:
            self.visit(node.iffalse)
        if hasattr(node, 'ifftrue') and node.iffalse is not None:
            self.visit(node.ifftrue)


class ForVisitor(c_ast.NodeVisitor):
    def visit_For(self, node):
        print(f"Found a 'for' node on line: {node.coord.line}")
        self.visit(node.stmt)



class SwitchVisitor(c_ast.NodeVisitor):
    def generic_visit(self, node):
        for _, child in node.children():
            if isinstance(child, c_ast.Switch):
                print("Found a switch node")
                #Fix nesting issues of switch statements using built in method, then translate to If
                child = fix_switch_cases(child)
                child = self._translate_to_if(child)

            if child is not None:
                self.visit(child)

    def _create_false(self, case, parent_switch, index):
        #TODO should defaults be handled here too? -- yes REVISIT LATER

        if isinstance(case, Case):
            if index + 1 > len(parent_switch.stmt.block_items):
                return None

            cond = BinaryOp('==',parent_switch.cond, case.expr)            #previously index + 1
            iftrue_next_case = Compound(case.stmts)
            iffalse_next_case = self._create_false(parent_switch.stmt.block_items[index + 1], parent_switch, index + 1)

            return If(cond, iftrue_next_case, iffalse_next_case)
        elif isinstance(case, Default):
            x = "stop"

    def _translate_to_if(self, switch_node):
        handled_next = 0
        for index, child in enumerate(switch_node.stmt.block_items):
            #Handled next means that the last iteration handled this child already
            if handled_next > 0 :
                handled_next = handled_next - 1
                continue

            #Treat cases right before default different
            # All cases with a default right after will look like a branch new if-else, with the else having the default
            # statements
            if (isinstance(child, Case)
                and index + 1 < len(switch_node.stmt.block_items)
                and isinstance(switch_node.stmt.block_items[index + 1], Default)):
                    cond = BinaryOp('==', switch_node.cond, child.expr)
                    iftrue = Compound(child.stmts)
                    iffalse = Compound(switch_node.stmt.block_items[index + 1].stmts)
                    replacement = If(cond, iftrue, iffalse)
                    child = replacement
                    switch_node.stmt.block_items[index] = child #todo check if this is necessary
                    handled_next = handled_next + 1

            #For when the child case is not a direct predecessor of a default node
            # A return inside  the statements implies an if-else-if structure
            # No return inside  the statements implies an if structure only
            elif isinstance(child, Case):
                return_present = False

                for stmt in child.stmts:
                    if isinstance(stmt, Return) or isinstance(stmt, Break):
                        return_present = True

                if return_present and switch_node.stmt.block_items[index + 1].stmts is not None:
                    cond = BinaryOp('==', switch_node.cond, child.expr)
                    iftrue = Compound(child.stmts)
                    iffalse = self._create_false(switch_node.stmt.block_items[index + 1], switch_node, index)
                    replacement = If(cond, iftrue, iffalse)
                    child = replacement
                    switch_node.stmt.block_items[index] = child  # todo check if this is necessary
                    handled_next = handled_next + 1

                elif return_present and switch_node.stmt.block_items[index + 1].stmts is None:   #Todo better way to check if the index exists probably
                    cond = BinaryOp('==', switch_node.cond, child.expr)
                    iftrue = Compound(child.stmts)
                    iffalse = None
                    replacement = If(cond, iftrue, iffalse)
                    child = replacement
                    switch_node.stmt.block_items[index] = child  # todo check if this is necessary
            elif isinstance(child, Default):

        return switch_node

## Testing purposes so that I can identify with certainty that even the most nested 'for' nodes
## have been converted -- saves time having to look through the debugger
def find_fors(ast):
    print("===================")
    print("Below are the lines on which a 'for' node was found:")
    v = ForVisitor()
    v.visit(ast)
    print("===================")
def run(ast):
    #Fix all of the switch cases before any sort of block gen
    v = SwitchVisitor()
    v.visit(ast)

    #Transform all for-loops and do-while-loops to while-loops
    v = CompoundVisitor()
    v.visit(ast)

    v = IfVisitor()
    v.visit(ast)