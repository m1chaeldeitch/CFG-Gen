__author__ = 'Ruben Acuna, Michael Deitch'

'''
Goal of the file:
Given a list of source files, generate a dict of dicts representing each files' CFG's

Input: list of source ".c" files
Output: Dict of dicts, following the general form:
        {"submission_file.c" -> {"func_1" -> CFG_OBJECT}, {"func_2" -> CFG_OBJECT2}},
         "submission_fileb.c -> {...}}
         
Each file has a collection of dicts associated with it, where each of those dicts contain
a mapping of the function name in the file, and the corresponding CFG for that function.
'''

#Imports
import pycparser
from pycparser import c_generator
import ast_simplification_c
import cfgbuilder_c
import os
import networkx as nx
import webbrowser
import graph_utils


def build_cfgs(file_list):
    #cfg_map[function_name_file_name] = graph_object
    cfg_map = {}

    for file in file_list:
        #Obtain AST for the file + transform switch -> if + transform for/dowhile -> while
        #https://eli.thegreenplace.net/2015/on-parsing-c-type-declarations-and-fake-headers/
        # Line 30-32 deal with headers that students will use. Including the fake_libc_include
        # is the way to handle headers. Read more here: https://deepwiki.com/eliben/pycparser/4-usage-and-examples
        # There might be a way to handle installing this via the install script (?). Read more here: https://pypi.org/project/pycparser-fake-libc/
        file_ast = pycparser.parse_file(file, use_cpp=True,
                                            cpp_path='gcc',
                                            cpp_args=['-E',  r'-Ifake_libc_include'])

        #This is where the actual simplification described above happens (transforming switch -> if
        # & transform for/dowhile -> while)
        ast_simplification_c.run(file_ast)

        #Helps create a cleaner mapping/return object in the end
        func_cfg_mappings = {}
        if '/' in file:
            index = file.rfind('/')
            file_name = file[index + 1:]
            pass
        else:
            file_name = file

        #Build the cfg for each function def in the current file
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


    # Creating nodes in a way that is easy to view is done through the line/text variables
    # Creating nodes with extra information will be done by extending the node class of nx
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

        #G.add_node(bb._id,  label=text, shape=look)
        bundle = (bb._id, bblist)
        bundle = dict(id=bb._id, statements=bblist)
        G.add_node(bb._id, label=text, shape=look, meta=bb)

    # add exit node
    G.add_node(len(bblist), label="exit", meta=None)

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

    file_list = ["ctestfiles/test_finding_func.c"]
    graph_mapping = build_cfgs(file_list)
    # single_graph = graph_mapping['test_finding_func.c']['runner1']
    # response = graph_utils.func_contains('printf', single_graph)
    # response2 = graph_utils.validate_thread_creation(single_graph)


    #Store a list of all thread creation nodes amongst all of the functions which were analyzed
    all_tc_nodes = {}

    #For each function of each file, call graph_utils.func_contains() method on them and store the results
    # for i, file_name in enumerate(graph_mapping):
    #     cfgs_curr_file = graph_mapping[file_name]
    #     for func_name in cfgs_curr_file:
    #         curr_func_cfg = cfgs_curr_file[func_name]
    #         tc_nodes = graph_utils.validate_thread_creation(curr_func_cfg)
    #         all_tc_nodes[func_name] = tc_nodes

    tc_nodes = graph_utils.validate_thread_creation2(graph_mapping["test_finding_func.c"]['main'], graph_mapping['test_finding_func.c'], list(graph_mapping["test_finding_func.c"].keys()))


    #Then create linkages between the two for exploration later.
    pass