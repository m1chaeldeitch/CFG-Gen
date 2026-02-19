__author__ = 'Michael'

'''
Goal of the file:
Given a list of source files, generate a list of CFGs
Each CFG in the list is a CFG generated from a singular function in the list of source files
'''

#Imports
import pycparser
from pycparser import c_generator
import ast_simplification_c
import cfgbuilder_c

import os
import sys
import networkx as nx
import webbrowser



def build_cfgs(file_list):
    #cfg_map[function_name_file_name] = graph_object
    cfg_map = {}

    for file in file_list:
        #Obtain AST for the file + transform switch -> if + transform for/dowhile -> while
        #https://eli.thegreenplace.net/2015/on-parsing-c-type-declarations-and-fake-headers/
        # TODO remove hard coded path, see how to add this to repo
        # for now: Must change line 33 to include a valid local path to pycparser source code available here: https://github.com/eliben/pycparser
        file_ast = pycparser.parse_file(file, use_cpp=True,
                                            cpp_path='gcc',
                                            cpp_args=['-E',  r'-I/local/path/to/pycparser/utils/fake_libc_include'])
        ast_simplification_c.run(file_ast)

        #Build the cfg for each function def in the current file
        func_cfg_mappings = {}
        if '/' in file:
            index = file.rfind('/')
            file_name = file[index + 1:]
            pass
        else:
            file_name = file

        for func_ast in file_ast.ext:

            if isinstance(func_ast, pycparser.c_ast.FuncDef):
                #Block generation
                block_list = cfgbuilder_c.make_basic_blocks(func_ast, 0)
                cfgbuilder_c.replace_exits(block_list, -2, len(block_list)) #Essentially converts the statements of the last working block to point to exit instead of -2

                #Graph generation
                func_name = func_ast.decl.name
                graph = __build_and_display_graph(block_list, 3, func_name, file_name)

                #Graph association
                # First bind each function name to its graph object as a dict
                # Then bind the file name to all of the {function_name->graph} dicts
                func_cfg_mappings[func_name] = graph
                #cfg_map[str(func_name + "_" + file)] = graph

        cfg_map[file_name] = func_cfg_mappings

    return cfg_map


def __build_and_display_graph(bblist, limit_lines, func_name, file_name):
    G = nx.DiGraph()
    generator = c_generator.CGenerator()

    for bb in bblist:
        text = "BB" + str(bb._id)

        if bb._type == 1 or bb._type == 3:
            look = "ellipse"

            lines_printed = 0

            for s in bb._statements:

                if lines_printed == limit_lines:
                    text += "\n..."
                    break
                line = generator.visit(s).strip()
                # line = visitors.to_source(s).strip()
                line = line.replace("\\r", "\\\\r")
                line = line.replace("\\n", "\\\\n")
                text += "\n" + line

                lines_printed += 1
        else:
            look = "diamond"

            if limit_lines > 0:
                line = generator.visit(bb._expression).strip()
                # line = visitors.to_source(bb._expression).strip()
                text += "\n" + line

        G.add_node(bb._id, label=text, shape=look)

    # add exit node
    G.add_node(len(bblist), label="exit")

    # add edges
    for bb in bblist:
        # normal edges
        if bb._exit_true != -1:
            if bb._type == 2:
                G.add_edge(bb._id, bb._exit_true, label="t")
            else:
                G.add_edge(bb._id, bb._exit_true)

        if bb._exit_false != -1:
            if bb._type == 2:
                G.add_edge(bb._id, bb._exit_false, label="f")
            else:
                G.add_edge(bb._id, bb._exit_false)

        # break control flow
        if bb._exit_break != -1:
            G.add_edge(bb._id, bb._exit_break, color="orange")

        # break control flow
        if bb._exit_expt != -1:
            G.add_edge(bb._id, bb._exit_expt, color="red")

    nx.drawing.nx_pydot.write_dot(G, func_name + "_" + file_name + ".dot")
    os.system("dot -Tpng " + func_name + "_" + file_name + ".dot > " + func_name + "_" + file_name + ".png")
    webbrowser.open(str(func_name + "_" + file_name) + '.png')
    return G


if __name__ == "__main__":
    ## Example usage -- commented out to avoid accidental use a live autograder ---

    file_list = ["ctestfiles/switch_testing.c", "ctestfiles/test_goto.c"]
    graph_mapping = build_cfgs(file_list)
    x = "stop"