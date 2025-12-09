from pycparser import c_ast, parse_file, c_generator
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
    '''
    Generic_visit was overrridden instead of following the regular visitor pattern.
    This was an intentional workaround due to some things that come up when using pycparser's visitor pattern.
    If we used the visitor pattern for switches for example, we'd:
    1. Come across each switch statment (good)
    2. Be unable to modify that switch statement in place (bad)

    So instead if we override the generic_visit, which will touch every node, and then look at each node's children,
    we can see if the child node of the current node is a switch. Then we can modify that child node directly.

    Basically we have to look one layer above where we are wanting to edit. So if we're looking to modify switch
    nodes, we have to stop at the parent to modify its child switch node.
    '''
    def generic_visit(self, node):
        for index, child in node.children():
            if isinstance(child, c_ast.Switch):
                print("Found a switch node")
                #Fix nesting issues of switch statements using built in method, then translate to If
                child = fix_switch_cases(child)
                child = self._translate_to_if(child)
                actual_index = int(index.split('[')[1].split(']')[0])
                node.block_items[actual_index] = child
                x = "stop"

            if child is not None:
                self.visit(child)



    def _translate_to_if(self, switch_node):
        prev_case = None
        prev_if = None
        switch_children = switch_node.stmt.block_items
        cases = {}
        working_if = None
        all_if_blocks = []

        for index, child in enumerate(switch_children):
            if isinstance(child, c_ast.Case):
                cases[index] = child

        #switch_children includes cases and defaults
        #cases maps the index from switch_children to the case
        for case_index, case in cases.items():
            termination, t_type = _has_break_or_return(case)

            if termination is False: #If case !!!!has break/return
                #need condition, iftrue, iffalse
                cond = BinaryOp('==', switch_node.cond, case.expr)
                iftrue = None
                iffalse = None

                #Add all the statements from the current case
                all_true_stmts = case.stmts.copy()

                #For every following statement in each block until a break is found:
                break_found = False
                for child_index, child in enumerate(switch_children):
                    if break_found:
                        break
                    if child_index > case_index:               #For every case AFTER the current case
                        for child_stmt in child.stmts:
                            if isinstance(child_stmt, Return):  #Returns considered a break, but still add them to stmts
                                break_found = True
                                all_true_stmts.append(child_stmt)
                                break
                            elif isinstance(child_stmt, Break):
                                break_found = True
                                break
                            else:
                                all_true_stmts.append(child_stmt)

                iftrue = Compound(all_true_stmts)
                translated_if = If(cond, iftrue, None)

            elif termination is True:
                cond = BinaryOp('==', switch_node.cond, case.expr)
                iftrue = None
                iffalse = None

                # Add all the statements from the current case
                all_true_stmts = case.stmts.copy()
                iftrue = Compound(all_true_stmts)
                translated_if = If(cond, iftrue, None)

            if prev_case is not None and _has_break_or_return(prev_case):
                prev_if.iffalse = translated_if
                prev_if = translated_if
                prev_case = case

            else:
                prev_if = translated_if
                prev_case = case
                all_if_blocks.append(translated_if)

        #Handling default case -- if there is a default,  add it to the if-tree as an iffalse always, where iffalse is just a compound of statements
        for default_index, default in enumerate(switch_children):
            if isinstance(default, c_ast.Default):
                termination, t_type = _has_break_or_return(default)

                if termination is False:  # If default !!!!has break/return
                    # Add all the statements from the current case
                    all_true_stmts = default.stmts.copy()

                    # For every following statement in each block until a break is found:
                    break_found = False
                    for child_index, child in enumerate(switch_children):
                        if break_found:
                            break
                        if child_index > default_index:  # For every case AFTER the current case
                            for child_stmt in child.stmts:
                                if isinstance(child_stmt,
                                              Return):  # Returns considered a break, but still add them to stmts
                                    break_found = True
                                    all_true_stmts.append(child_stmt)
                                    break
                                elif isinstance(child_stmt, Break):
                                    break_found = True
                                    break
                                else:
                                    all_true_stmts.append(child_stmt)

                    iftrue = Compound(all_true_stmts)

                elif termination is True:
                    # Add all the statements from the current case
                    all_true_stmts = default.stmts.copy()
                    iftrue = Compound(all_true_stmts)

                if prev_case is not None:
                    prev_if.iffalse = iftrue

        #new_code = generator.visit(all_if_blocks[0])
        #print(f"\n\n\n{new_code}\n\n\n")
        #x = 'stop again'
        return all_if_blocks[0]


def _has_break_or_return(case):
    for stmt in case.stmts:
        if isinstance(stmt, c_ast.Break):
            return True,"break"
        if isinstance(stmt, c_ast.Return):
            return True,"return"

    return False, None


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