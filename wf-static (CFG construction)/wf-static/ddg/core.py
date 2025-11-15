__author__ = 'Ruben'
#Disk Dependency Graph

import ast
import os
import networkx
#import webbrowser
from astmonkey import visitors, transformers

import file_manager
import system_invocations

def enum(**enums):
    return type('Enum', (), enums)

IOMode = enum(READ=1, WRITE=2, APPEND=3)




class NodeIOVariable(object):
    def __init__(self, symbol):
        self._symbol = symbol

        self._dependencies = []

    def AddDependency(self, nf, mode):

        if isinstance(mode, ast.Str) and mode.s == "r":
            self._dependencies.append({"target": nf, "mode": IOMode.READ})
        elif isinstance(mode, ast.Str) and mode.s == "w":
            self._dependencies.append({"target": nf, "mode": IOMode.WRITE})
        elif isinstance(mode, ast.Str) and mode.s == "a":
            self._dependencies.append({"target": nf, "mode": IOMode.APPEND})
        else:
            raise BaseException("NodeVariable::AddDependency Unknown mode: " + mode)

class NodeFile(object):
    def __init__(self, expr, symtable):
        self._expr = expr
        self._symtable = symtable

    def to_string(self):

        if isinstance(self._expr, ast.Name):
            entry = self._symtable[self._expr.id]

            if entry.assignment_count() == 1:

                return "Expr: " + visitors.to_source(entry.last_value())

        return "Expr: " + visitors.to_source(self._expr)

class VisitorFileOpen(ast.NodeVisitor):
    def __init__(self, symtable, nodes_variable, nodes_file):
        self._symtable = symtable
        self._nodes_variable = nodes_variable
        self._nodes_file = nodes_file

    def visit_Assign(self, node):
        #check for a file being opened
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id == "open":   #assuming std library
                    nf = NodeFile(node.value.args[0], self._symtable)
                    self._nodes_file.append(nf)

                    for target in node.targets:
                        for var_node in self._nodes_variable:
                            if target.id == var_node._symbol:
                                var_node.AddDependency(nf, node.value.args[1])

def build_ddg(block_list, symtable):
    nodes_handler = []
    nodes_file = []
    nodes_tools = []

    file_man = file_manager.FileManager(symtable)

    #find all calls to os.system.
    tool_invocations = []
    for block in block_list:
        block_module = ast.Module(block._statements)
        system_invocations.VisitorOSSystem(symtable, tool_invocations, file_man).visit(block_module)

    #create nodes that represent tool invocations
    for tool_invoke in tool_invocations:

        #nodes_tools += [NodeTool(symtable, tool_invoke._cmd)]

        tool_invoke.display()
        print

    #create nodes that represent variables used as file handlers
    for entry in symtable:
        if entry._opened or entry._closed:
            nodes_handler += [NodeIOVariable(entry._name)]

    #from IO access
    for block in block_list:
        block_module = ast.Module(block._statements)
        VisitorFileOpen(symtable, nodes_handler, nodes_file).visit(block_module)

    display_graph(tool_invocations, nodes_handler, nodes_file, symtable, file_man)

def display_graph(tool_invocations, nodes_handler, nodes_file, symtable, file_man):
    #display
    G = networkx.DiGraph()

    #add nodes

    #create nodes that represent 'touched' files on disk
    for file in file_man._files:
        text = file.to_string()
        look = "folder"
        G.add_node(file, label=text, shape=look)

    for node in tool_invocations:
        text = node.to_string()
        look = "doublecircle"
        G.add_node(node, label=text, shape=look, color = "blue")

        #create file argument edges
        for file_arg in node._file_args:
            G.add_edge(node, file_arg["file"], label=" ", color="blue")

    for node in nodes_handler:
        text = "Handler: " + node._symbol
        look = "circle"
        G.add_node(node, label=text, shape=look, color = "blue")

    for node in nodes_file:
        text = node.to_string()
        look = "folder"
        G.add_node(node, label=text, shape=look, color = "blue")

    #add edges
    for node in nodes_handler:

        for dependency in node._dependencies:

            text = "Unknown"

            if dependency["mode"] == IOMode.READ:
                text = "Read"
            elif dependency["mode"] == IOMode.WRITE:
                text = "Write"
            elif dependency["mode"] == IOMode.APPEND:
                text = "Append"

            G.add_edge(node, dependency["target"], label=text, color="blue")

    networkx.write_dot(G, "ddg.dot")
    os.system("dot -Tpng ddg.dot > ddg.png")
    #webbrowser.open('ddg.png')

#attempt to resolve symbolic names to actual names