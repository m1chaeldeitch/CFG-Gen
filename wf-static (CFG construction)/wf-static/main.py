__author__ = 'Ruben'

import pycparser

#import ddg.core

#import ast
#import ast_simplification
#import cfgbuilder
#import symboltable
#import ddg
#import os
#import networkx as nx
#from astmonkey import visitors
#import webbrowser

#http://networkx.github.com/documentation/latest/examples/drawing/labels_and_colors.html
# def display_cfg(bblist, limit_lines):
#
#     # extract nodes from graph
#     G = nx.DiGraph()
#
#     for bb in bblist:
#         text = "BB" + str(bb._id)
#
#         if bb._type == 1 or bb._type == 3:
#             look = "ellipse"
#
#             lines_printed = 0
#
#             for s in bb._statements:
#
#                 if lines_printed == limit_lines:
#                     text += "\n..."
#                     break
#
#                 line = visitors.to_source(s).strip()
#                 line = line.replace("\\r", "\\\\r")
#                 line = line.replace("\\n", "\\\\n")
#                 text += "\n" + line
#
#                 lines_printed += 1
#         else:
#             look = "diamond"
#
#             if limit_lines > 0:
#                 line = visitors.to_source(bb._expression).strip()
#                 text += "\n" + line
#
#         G.add_node(bb._id, label=text, shape=look)
#
#     #add exit node
#     G.add_node(len(bblist), label="exit")
#
#     #add edges
#     for bb in bblist:
#         #normal edges
#         if bb._exit_true != -1:
#             if bb._type == 2:
#                 G.add_edge(bb._id, bb._exit_true, label="t")
#             else:
#                 G.add_edge(bb._id, bb._exit_true)
#
#         if bb._exit_false != -1:
#             if bb._type == 2:
#                 G.add_edge(bb._id, bb._exit_false, label="f")
#             else:
#                 G.add_edge(bb._id, bb._exit_false)
#
#         #break control flow
#         if bb._exit_break != -1:
#             G.add_edge(bb._id, bb._exit_break, color="orange")
#
#         #break control flow
#         if bb._exit_expt != -1:
#             G.add_edge(bb._id, bb._exit_expt, color="red")
#
#     nx.write_dot(G, "output.dot")
#     os.system("dot -Tpng output.dot > output.png")
#    webbrowser.open('output.png')

#settings
filename = "test5.py"

#entry point
#procedure = ast.parse(open(filename).read())
procedure = pycparser.parse_file(filename)

#simplify the ASTs
ast_simplification.run(procedure)

#display ASTs as source
#print visitors.to_source(program).strip()

#build cfg
block_list = cfgbuilder.make_basic_blocks(procedure.body, 0)
cfgbuilder.replace_exits(block_list, -2, len(block_list))

#build symbol table
table = symboltable.generate(block_list)
table.display()

#build disk dependency graph
ddg.core.build_ddg(block_list, table)

#display cfg
#cfgbuilder.print_basic_blocks(block_list)
#display_cfg(block_list, 3)
