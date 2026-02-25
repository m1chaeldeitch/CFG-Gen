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

'''
Input: graph_mapping in the form of "graph_mapping[file_name] = list_of_functions"
Output: tuple in the form of main_cfg, all_cfgs, all_func_names
This gives you all of the arguments you need for find_all_nodes_for_func, except for the desire function name, which
is up to you :)
'''
def find_searching_params(graph_mapping):
    pass
    all_cfgs = {}
    main_cfg = None
    all_func_names = []

    for i, file_name in enumerate(graph_mapping):
        cfgs_curr_file = graph_mapping[file_name]
        for func_name in cfgs_curr_file:
            curr_cfg = cfgs_curr_file[func_name]
            #Collect all cfgs
            #all_cfgs.append(curr_cfg)
            all_cfgs[func_name] = curr_cfg

            #Store the main cfg
            if func_name == "main":
                main_cfg = curr_cfg

            #Collect all function names
            all_func_names.append(func_name)

    if main_cfg is None:
        raise Exception("Program doesn't contain a main function, cannot do further analysis.")
    return main_cfg, all_cfgs, all_func_names