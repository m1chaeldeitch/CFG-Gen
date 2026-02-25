'''
Graph utilities for CFGs generated through NetworkX
'''
import ast

import pycparser
from networkx.algorithms.traversal import dfs_successors
import graph_generator_c
import ast_operations


#DFS (searching for function call with a specific name)

#We have all of the basic blocks for some function (todo return this with some function in graph_generator)
#Within each basic block are statements (there won't be if-nodes or for-nodes)
#   For each statement of each function, identify if there is a function call = the input function call
#   Obtain the basicblock ID that the funccall resides in


# In the graph object, each of the nodes (basic blocks) are represented by an ID which contains their block number
# By performing a DFS on that node within the graph, we can record the nodes that are visited after the funccall
# Having this list of visited blocks, we can then traverse through the blocks for the input function


## TODO There needs to be an association between basic blocks of different functions?
# Symbol table to associate basic block root with funciton identifiers
# For example, the first basic block for all functions has been a function signature
    # We would remove this node from the graph and instead opt for a symbol table to associate this basic block root with the function name found in the aformentioned signature
    # Then enytime we visit/see a BB that is a function call, check to see if there is an entry in our symbol table for it
    # if not exists then no further analysis
    # if it does exist (we have a set of basic blocks for that function call), then we would further analyze that function (its set of basic blocks)


#Maybe look into extending node class of network x to preserve statements as ast nodes


# Keep in mind that the input here is the entire graph for a single function, of a single source file
# In short -> Input graph = function graph
#          -> Input function_name = the function invocation we are searching for within the graph
#          -> Output = whether or not the function call was made within the input function's graph
# TODO NOTE: Probably not the right way to do this. Says nothing about whether or not the function call is
#  actually reached... that will require a DFS/BFS on the entry node.
def func_contains(function_name, graphe):
    returnlist = [] #TODO REMOVE
    for i in range(len(graphe.nodes)):
        #for basic_block in graphe.nodes[i]['meta']:
        basic_block = graphe.nodes[i]['meta']

        # handle the exit nodes which have no statements
        if basic_block is None:
            continue
        for statement in basic_block._statements:
            if isinstance(statement, pycparser.c_ast.FuncCall):
                if statement.name.name == function_name:
                    returnlist.append("true") #TODO CHANGE BACK

    return False

# This is going to take an input of the graph for one function call
# Goal: Find whether or not the input function has a connected route from the entry node to the function call
# Later extend this to explore the graphs of other functions that are called (?)
# Could also be done by returning the specific basic block as a "yes" with another graph returned as a

# Lets say main() makes a call to runner1() which makes another call to pthread_start()
# We should look in main()'s graph and find the runner1() function
# We should then explore runner1()
# We should then see the FuncCall object in runner1
# Then we should return (True, runner1)
# This tells us that 1) the desired function that we were looking for (pthread_start()) is accessible from main
#                    2) We can then look at runner1 for later when we want to see if there's a downstream pthread_join() from this point


# Another appraoch (maybe the same lol)
# We can identify the node within the graph that makes the call to pthread_create()
# Then we can (using networkx) see the edges to predecessors
# Then we can check all the way up the predecessor chain until we get back to a looping structure
# In this looping structure, we can then check the bounds.
# Relevant functions in networkx:
#   1. reconstruct_path()
#   2. digraph.predecessors() (page 68)p
def func_called_bfs(function_name, graph):
    pass


'''
Starts at the entry point of the program (main function's cfg)
and checks this function, as well as all other functions that it can
reach, for calls to pthread_create()
'''
def validate_thread_creation(main_cfg):
    #Store a dict so we have:
    #thread_create_nodes["func_name"] = [node1, node2] todo Maybe adapt to this, not necessary under current plan
    #thread_create_nodes = [] should be enough since we are always inputting only one cfg and not tracing the function calls
    thread_create_nodes = []

    for i in range(len(main_cfg.nodes)):
        #Create an object to look at the basic blocks of the cfg
        #Basic blocks might contain many statements -- todo Can there be multiple basic blocks for a node?
        basic_block = main_cfg.nodes[i]['meta']

        #Store a list of the nodes which make the call to pthread_create
        # thread_create_nodes = []

        #Handle the exit nodes which have no statements
        if basic_block is None:
            continue

        #In any other case, where there are statements in the current basic block
        #Look for the pthread_create function being called
        for statement in basic_block._statements:
            if isinstance(statement, pycparser.c_ast.FuncCall):
                if statement.name.name == "pthread_create":        #TODO Search the entire tree of the statement
                    thread_create_nodes.append(main_cfg.nodes[i])

        #Add to the mapping
        # if thread_create_nodes:
        #     thread_create_map[main_cfg.nodes[0]['label'].split(" ")[1].strip("()")] = thread_create_nodes

    pass
    return thread_create_nodes

'''
General Function to use when looking for any arbitrary function accessible from the "cfg" argument
'''
def find_all_nodes_for_func(cfg, all_cfgs, all_func_names, desired_func):
    func_node = []
    func_call_map = {}
    #thread_create_nodes["func_name"] = [node1, node2] todo Maybe adapt to this, not necessary under current plan
    funcs_called = []

    ## (1) Look for calls to pthread_create() within just the main cfg
    for i in range(len(cfg.nodes)):
        # Create an object to look at the basic blocks of the cfg
        basic_block = cfg.nodes[i]['meta']

        # Handle the exit nodes which have no statements
        if basic_block is None:
            continue

        # In any other case, where there are statements in the current basic block
        # Look for the pthread_create function being called
        for statement in basic_block._statements:
            if statement is not None:
                statement_search = ast_operations.find_func(statement, desired_func)

                #If the pthread_create() is found, mark this as true and then keep track of it
                #If false, add the name to the list of functions that are accessible by the current function
                if statement_search.found is True:
                    func_node.append(cfg.nodes[i])
                elif statement_search.found is False:
                    for name in statement_search.names:
                        funcs_called.append(name)

        #Associate all thread creation nodes to the current function name todo maybe implement the mapping later
        if func_node:
            func_call_map[cfg.nodes[0]['label'].split(" ")[1].strip("()")] = func_node


    ## (2) Look for calls to pthread_create() within the functions that the current function called
    for func in funcs_called:
        if func in all_func_names:
            curr_cfg = all_cfgs[func]
            additional_nodes = find_all_nodes_for_func(curr_cfg, all_cfgs, all_func_names)
            func_node.extend(additional_nodes)
            funcs_called.remove(func)

    return func_node

'''
Example function that finds all nodes that make a call to pthread_create()
'''
def find_pthread_create(main_cfg, all_cfgs, all_func_names):
    return find_all_nodes_for_func(main_cfg, all_cfgs, all_func_names, "pthread_create")

