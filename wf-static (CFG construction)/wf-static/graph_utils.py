'''
Graph utilities for CFGs generated through NetworkX
'''
import ast_operations

'''
#General Function to use when looking for any arbitrary function accessible from the "cfg" argument
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
            additional_nodes = find_all_nodes_for_func(curr_cfg, all_cfgs, all_func_names, desired_func)
            func_node.extend(additional_nodes)
            funcs_called.remove(func)

    return func_node

'''
Example function that finds all nodes that make a call to pthread_create()
'''
def find_pthread_create(main_cfg, all_cfgs, all_func_names):
    return find_all_nodes_for_func(main_cfg, all_cfgs, all_func_names, "pthread_create")

