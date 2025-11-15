__author__ = 'Ruben Acuna'

import ast
from astmonkey import visitors

next_iter_id = 0

class TransformForLoopToWhileLoop(ast.NodeTransformer):
    def visit_For(self, node):

        global next_iter_id

        if node.orelse != []:
            raise "unexpected: saw use of orelse while transforming for loops to while loops"

        #example:
        #for i in range(1, 10):
        #    print "cat"

        #should generate something like:
        #iter = range(1, 10).__iter__()
        #while True:
        #    try:
        #        i = iter.next()
        #    except StopIteration:
        #        break
        #    print "cat"

        target_src = visitors.to_source(node.target).strip()
        iter_src = visitors.to_source(node.iter).strip()

        new_body = []
        for statement in node.body:
            result = self.visit(statement)
            if isinstance(result, list):
                new_body.extend(result)
            else:
                new_body.append(result)

        loopNode = ast.parse("while True:\n"
                             "    try:\n"
                             "        " + target_src + " = RA_iter"+str(next_iter_id)+".next()\n"
                                                       "    except StopIteration:\n"
                                                       "        break\n"
                                                       "    pass\n").body

        #attach body to new loop node
        loopNode[0].body = loopNode[0].body[:-1] + new_body

        #combine iterator initialization and new loop nodes
        combo = [ast.parse("RA_iter"+str(next_iter_id)+" = " + iter_src + ".__iter__()").body[0]] + [loopNode][0]

        next_iter_id += 1

        return combo

class ApplyConcatenation(ast.NodeTransformer):
    def __init__(self, changing):
        self._changing = changing
        self._changing[0] = False

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            if isinstance(node.left, ast.Str) and isinstance(node.right, ast.Str):
                self._changing[0] = True
                return ast.Str(node.left.s + node.right.s)

        return node

#flatten modulus
#see http://www.informit.com/articles/article.aspx?p=28790&seqNum=2
class ApplyConcatenation(ast.NodeTransformer):
    def __init__(self, changing):
        self._changing = changing
        self._changing[0] = False

    def buildStrAdd(self, left, right):
        t = ast.BinOp()
        t.op = ast.Add()
        t.left = left
        t.right = right

        return t

    def visit_BinOp(self, node):

        if isinstance(node.op, ast.Mod):

            #StringOperand % TupleOperand
            if isinstance(node.left, ast.Str) and isinstance(node.right, ast.Tuple):

                chunks = node.left.s.split("%s")
                items = node.right.elts

                combined = []
                for piece in chunks:
                    if piece:
                        combined += [ast.Str(piece)]
                    else:
                        combined += [items[0]]
                        items.pop(0)

                tree = combined.pop(0)
                while combined:
                    tree = self.buildStrAdd(tree, combined[0])
                    combined.pop(0)

                return tree

        return node

def run(module):
    TransformForLoopToWhileLoop().visit(module)

    #try to simplify strings in program.
    changing = [True]
    while changing[0]:
        ApplyConcatenation(changing).visit(module)

    #print(visitors.to_source(module).strip())
    #print
