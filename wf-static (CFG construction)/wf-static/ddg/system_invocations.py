__author__ = 'Ruben Acuna'

import ast
from astmonkey import visitors, transformers
from itertools import chain

#argument list
# list of
#    {key AS basestring, value AS ast.Expr}


class ToolInvocation(object):
    def __init__(self, cmd, file_arg, gen_arg):

        self._cmd = cmd
        self._file_args = file_arg
        self._gen_args = gen_arg

    def to_string(self):

        if isinstance(self._cmd, ast.Str):
            return self._cmd.s
        else:
            return "Expr: " + visitors.to_source(self._cmd)

    def display(self):
        print "==TOOL INVOCATION=="

        print visitors.to_source(self._cmd).strip()
        print

        print "Key(Source)".ljust(20),
        print "Expr(Source)".ljust(26),
        print "Key".ljust(35),
        print "Expression",
        print

        for argument in self._file_args:
            print visitors.to_source(argument["key"]).strip().ljust(20),
            print argument["file"].to_string().strip().ljust(26),
            print str(argument["key"]).ljust(35),
            print str(argument["file"]._expr).strip(),
            print

def build_add(left, right):
    t = ast.BinOp()
    t.op = ast.Add()
    t.left = left
    t.right = right

    return t


#locate tool invocations
class VisitorOSSystem(ast.NodeVisitor):
    def __init__(self, symtable, invocations, fileman):
        self._table = symtable
        self._tool_invoke = invocations
        self._fileman = fileman

    def process_str(self, expr, workplace):
        tokens = list(chain.from_iterable((e, " -") for e in expr.s.split(" -")))[:-1]
        sep_parameters = []

        for token in tokens:
            if len(sep_parameters) > 0 and sep_parameters[len(sep_parameters)-1] == " -":
                sep_parameters[len(sep_parameters)-1] += token

            elif token != "":
                sep_parameters += [token]

        for parameter in sep_parameters:
            if parameter[:2] == " -":

                #flush accumulator
                if workplace["accum"]["key"]:
                    workplace["arguments"] += [{"key": workplace["accum"]["key"], "value": workplace["accum"]["value"]}]
                    workplace["accum"]["key"] = None
                    workplace["accum"]["delim"] = False
                    workplace["accum"]["value"] = None

                if " " in parameter.strip():
                    key = parameter.strip().split(" ", 1)[0][1:]
                    value = parameter.strip().split(" ", 1)[1]
                    workplace["arguments"] += [{"key": ast.Str(key), "value": ast.Str(value)}]
                elif " " in parameter.lstrip():
                    key = parameter.strip().split(" ", 1)[0][1:]
                    workplace["accum"]["key"] = ast.Str(key)
                    workplace["accum"]["delim"] = True
                    workplace["accum"]["value"] = None
                else:
                    print "DDG.py: TODO0"
            else:
                #HACK: obv
                workplace["cmd"] = ast.Str(parameter)


        #print "tokens", tokens
        #print "sep_parameters", sep_parameters
        #print "parseStr result:", workplace

        return workplace

    def process_expr(self, expr):

        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            #os.system("tool1 -i " + input + " -o " + output)

            workplace = self.process_expr(expr.left)

            #now need to integrate the results from parsing the right operand
            #if accu is non-empty, then it stores the beginning of a key

            if workplace["accum"]["delim"]:

                if isinstance(expr.right, ast.Name):
                    if workplace["accum"]["value"]:
                        print "DDG.py: UNTESTED2a"
                        workplace["accum"]["value"] = build_add(workplace["accum"]["value"], expr.right)
                    else:
                        workplace["accum"]["value"] = expr.right

                elif isinstance(expr.right, ast.Str):
                    workplace = self.process_str(expr.right, workplace)

                else:
                    print "DDG.py: TODO3"
            else:
                if isinstance(expr.right, ast.Name):
                    print "DDG.py: TODO4"

                elif isinstance(expr.right, ast.Str):
                    workplace = self.process_str(expr.right, workplace)

                else:
                    print "DDG.py: TODO6"

            return workplace

        #base case
        elif isinstance(expr, ast.Str):
            return self.process_str(expr, {"arguments": [], "accum": {"key": None, "delim" : False, "value": None}})

        else:
            raise BaseException("VisitorOSSystem::doBinOp found unknown expression")

    def visit_Expr(self, node):

        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if node.value.func.attr == "system" and node.value.func.value.id == "os":
                    if len(node.value.args) != 1:
                        raise BaseException("VisitorOSSystem Tool invocation has wrong number of arguments.")

                    expr = node.value.args[0]

                    #analyze arguments list
                    os_invoke = self.process_expr(expr)

                    #finish the arguments list
                    system_arguments = os_invoke["arguments"]
                    #flush arguments accumulator
                    if os_invoke["accum"]["key"]:
                        system_arguments += [{"key": os_invoke["accum"]["key"], "value": os_invoke["accum"]["value"]}]

                    #todo: separate arguments into file or generic
                    #file arguments
                    file_args = system_arguments
                    #generic arguments
                    gen_args = []

                    #analyze invocation and populate the filemanager
                    file_args = [{"key": x["key"], "file": self._fileman.touch_file(x["value"])} for x in file_args]

                    #create tool invoke based on os invoke
                    tool_invoke = ToolInvocation(os_invoke["cmd"], file_args, gen_args)
                    self._tool_invoke += [tool_invoke]

                    #print "final arguments:", result["arguments"]
                    #print "final accum
                    #print "Found system call:", visitors.to_source(expr).strip()
                    #display_arguments_list(result["arguments"])

                    #prepped_expr = transformers.ParentNodeTransformer().visit(expr)
                    #visitor = visitors.GraphNodeVisitor()
                    #visitor.visit(prepped_expr)
                    #visitor.graph.write_png('graph.png')