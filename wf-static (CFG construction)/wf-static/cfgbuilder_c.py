__author__ = 'Ruben Acuna', 'Michael Deitch'

#imports
from cfg_structures import *

#settings
DEBUG_PRINT = False

#mapping for second pass
# label_dict[label_name] = block_num
label_dict = {}

#functions
def debug_print(s):
    if DEBUG_PRINT:
        print (s)

def search_for_block_number(BBlist, blockNum):
    for block in BBlist:
        if block._id == blockNum:
            return True

    return False

#extended_basic_block_list_t
#add_to_extended_basic_block_list
#new_basic_block_list
def add_to_basic_block_list(lst, block):    #renamed this add->merge
    if search_for_block_number(lst, block._id):
        raise Exception("	Block " + str(block._id) + " already exists in list, not added.")
    else:
        lst += [block]

def replace_exits(blocks, source, target):
    for bb in blocks:

        if bb._exit_true == source:
            bb._exit_true = target
        if bb._exit_false == source:
            bb._exit_false = target
        if bb._exit_break == source:
            bb._exit_break = target

def flush_normal_block(return_list, block_next_id, working_block):
    if working_block.statement_count() > 0:
        debug_print("  flushing working_block")

        #lock in previous block
        working_block._id = block_next_id
        working_block._type = BlockType.NORMAL
        working_block._exit_true = block_next_id + 1

        add_to_basic_block_list(return_list, working_block)

        #prepare new block
        block_next_id += 1
        working_block = BasicBlock(block_next_id)

    return block_next_id, working_block

#returns a list of basic blocks
def make_basic_blocks(block_items, blockNum):
    #statements will be adapted to be the AST rooted at at 'blockItems' for the function
    #Todo: Add some error handling for AST
    # if len(statements) > 0 and not isinstance(statements[0], ast.stmt):
    #     raise Exception("called make_basic_blocks on something that is not a statement!")

    return_list = []
    working_block = BasicBlock(blockNum)
    skip_num = 0
    for index, statement in enumerate(block_items):
        if (skip_num > 0):
            skip_num -= 1
            continue
        debug_print("Processing " + statement.__class__.__name__ + ":")

        if statement.__class__.__name__ == "Assignment" or statement.__class__.__name__ == "Decl":
            #Todo confirm that this is unnecesssary for C
            # Thoughts are:
            #   1. This looks to be related to the translation of loops that RA did to use next
            #   2. Not sure the utility of open

            # debug_print("  assign|augassign statement on line " + str(statement.coord.line) + ", adding to block " + str(blockNum))
            #HACK: hooking internal exception in call to X.next() or open().
            # if isinstance(statement.value, ast.Call):
            #     if isinstance(statement.value.func, ast.Attribute):
            #         if statement.value.func.attr == "next" and "RA_iter" in statement.value.func.value.id:
            #             blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)
            #
            #             working_block._expt_name = "StopIteration"
            #             working_block.add(statement)
            #
            #             blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)
            #
            #             continue
            #     elif isinstance(statement.value.func, ast.Name):
            #         if statement.value.func.id == "open":
            #             blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)
            #
            #             working_block._expt_name = "IOError"
            #             working_block.add(statement)
            #
            #             blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)
            #
            #             continue

            working_block.add(statement)

        #for - see ast_simplification
        elif statement.__class__.__name__ == "If":
            #example:
            #If(test=Compare(left=Name(id='num', ctx=Load()),
            #                ops=[Eq()], comparators=[Num(n=2)]),
            #                body=[Print(dest=None, values=[Str(s='num is 2')], nl=True)],
            #                orelse=[])

            #debug_print("  if statement on line " + str(statement.coord.line))

            blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)

            #captures the if statement evaluating expression in a block
            debug_print("  Capturing if statement expression in block")
            working_block._type = BlockType.CONDITIONAL
            working_block._exit_true = blockNum + 1
            #Todo -- Q: what does expression mean and what is the test value
            # A: statement.test is looking at the if condition
            working_block._expression = statement.cond

            add_to_basic_block_list(return_list, working_block)

            blockNum += 1

            debug_print("  Calling make_basic_blocks for if statements")
            if_list = make_basic_blocks(statement.iftrue, blockNum)          #todo, ensure that this is handled correctly by compound
                                                                             # slightly odd that an iftrue node is a compound...

            debug_print("  Calling make_basic_blocks for else statements")
            if statement.iffalse is not None:
                else_list = make_basic_blocks(statement.iffalse, blockNum + len(if_list))
            else:
                else_list = []

            for bb in if_list:
                add_to_basic_block_list(return_list, bb)

            for bb in else_list:
                add_to_basic_block_list(return_list, bb)

            if len(else_list) == 0:
                working_block._exit_false = ExitType.HANGING_BLOCK_EXIT
            else:
                working_block._exit_false = blockNum + len(if_list)

            debug_print("  " + str(len(else_list)) + " elements added to return_list from else_list")
            blockNum += len(if_list) + len(else_list)

            #prepare everything to link to the block we are just about to create
            replace_exits(return_list, ExitType.HANGING_BLOCK_EXIT, blockNum)

            #recreate the working_block with new parameters
            working_block = BasicBlock(blockNum)
            working_block._exit_true = blockNum + 1

        elif statement.__class__.__name__ == "While":
            #print ast.dump(statement)
            #While(test=Compare(left=Name(id='i', ctx=Load()), ops=[Lt()], comparators=[Num(n=101)]),
            #      body=[Print(dest=None, values=[Str(s='cat')], nl=True), AugAssign(target=Name(id='i', ctx=Store()), op=Add(), value=Num(n=1))],
            #      orelse=[])

            while_ss = statement.stmt.block_items  #While block statements
            while_e = statement.cond               #Condition check for the while statement

            blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)

            debug_print("Capturing while expression in block\n")

            working_block._type = BlockType.CONDITIONAL
            working_block._exit_true = blockNum + 1
            working_block._exit_false = 999
            working_block._expression = while_e

            while_head_block = working_block

            add_to_basic_block_list(return_list, working_block)
            blockNum += 1

            #// Make sure working_block cannot be used until it is recreated
            working_block = None

            while_blockNum = blockNum

            debug_print("Calling make_basic_blocks blockNum = " + str(while_blockNum))
            while_list = make_basic_blocks(while_ss, while_blockNum)

            #traverses the returned while_list, adding elements to the return_list and counting
            while_count = len(while_list)
            for bb in while_list:
                add_to_basic_block_list(return_list, bb)

            #update links out of the while
            block_after_while = while_blockNum + while_count

            for bb in while_list:
                if bb._type == BlockType.LOOP_JUMP and bb._exit_break == ExitType.HANGING_BREAK:
                    bb._exit_break = block_after_while
                elif bb._type == BlockType.LOOP_JUMP and bb._exit_break == ExitType.HANGING_CONTINUE:
                    bb._exit_break = while_head_block._id

            while_head_block._exit_false = block_after_while

            debug_print("   Blocks in while_list = " + str(while_count))

            #prepare everything to like the block we are just about to create
            replace_exits(return_list, ExitType.HANGING_BLOCK_EXIT, while_head_block._id)

            #// Recreate working_block with new parameters
            working_block = BasicBlock()
            working_block._id = while_blockNum + while_count
            working_block._exit_true = while_blockNum + while_count

            #// And change the global parameter
            blockNum = while_blockNum + while_count

        elif statement.__class__.__name__ == "Import":
            #debug_print("  import statement on line " + str(statement.coord.line) + ", adding to block " + str(blockNum))
            working_block.add(statement)

        #Raise(expr? type, expr? inst, expr? tback)
        elif statement.__class__.__name__ == "Raise":
            #example:
            #Raise(type=Call(func=Name(id='StopIteration', ctx=Load()),
            #                args=[Str(s='help!')],
            #                keywords=[],
            #                starargs=None,
            #               kwargs=None),
            #      inst=None,
            #      tback=None)

            debug_print("  raise statement on line " + str(statement.coord.line))

            if statement.inst or statement.tback:
                raise Exception("Raise: unexpected input.")

            blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)

            #captures the raise in a single block
            working_block._expt_name = statement.type.func.id
            working_block.add(statement)
            add_to_basic_block_list(return_list, working_block)

            #create a new working block
            blockNum += 1
            working_block = BasicBlock(blockNum)

        #TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
        elif statement.__class__.__name__ == "TryExcept":
            #example:
            #TryExcept(body=[Print(dest=None, values=[Str(s='something')], nl=True), Assign(targets=[Name(id='i', ctx=Store())], value=Num(n=4))],
            #          handlers=[ExceptHandler(type=Name(id='StopIteration', ctx=Load()), name=None, body=[Print(dest=None, values=[Str(s='muffin')], nl=True)])],
            #          orelse=[])

            blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)

            #BB generation for body
            debug_print("  Calling make_basic_blocks for body of TryExcept")
            blocks_body = make_basic_blocks(statement.body, blockNum)

            for bb in blocks_body:
                add_to_basic_block_list(return_list, bb)

            blockNum += len(blocks_body)

            block_body_last = blocks_body[-1]

            debug_print("    added blocks to body = " + str(len(blocks_body)))

            #BB generation for exception handler
            #http://greentreesnakes.readthedocs.org/en/latest/nodes.html

            blocks_expt_end = []

            for handler in statement.handlers:

                debug_print("  Calling make_basic_blocks for an exception handler in TryExcept\n")

                #seek out and attach raises
                for bb in blocks_body:
                    if bb._type == BlockType.NORMAL:
                        if bb._expt_name and bb._exit_expt == ExitType.UNSET:
                            if handler.type:
                                if bb._expt_name == handler.type.id:
                                    bb._exit_expt = blockNum
                            else:
                                bb._exit_expt = blockNum

                blocks_handler = make_basic_blocks(handler.body, blockNum)

                blocks_expt_end += [blocks_handler[-1]]

                for bb in blocks_handler:
                    add_to_basic_block_list(return_list, bb)

                debug_print("    added blocks to handler = " + str(len(blocks_handler)))

                blockNum += len(blocks_handler)

            replace_exits(return_list, ExitType.HANGING_BLOCK_EXIT, blockNum)

            #update the blank working_block with new parameters
            working_block._id = blockNum

        #Expr
        elif statement.__class__.__name__ == "Expr":
            working_block.add(statement)
            #TODO: finish

        elif statement.__class__.__name__ == "BinaryOp":
            working_block.add(statement)

        elif statement.__class__.__name__ == "UnaryOp":
            #Example: "variable_name--;"
            working_block.add(statement)

        elif statement.__class__.__name__ == "EmptyStatement":
            working_block.add(statement)

        elif statement.__class__.__name__ == "FuncCall":
            #TODO: ? Not sure if this is how it should be handled, but I remember something about ignoring function
            # calls for now and dealing with associating the different CFGs through function calls?
            # Maybe a tag -- find out where it leads
            # Some way to know that the block contains a function call
            # 2 passes for identifying edges between goto & labels
            # **Jumping to label or variable -- maybe handle labels first then deal with variables later (or raise exception)
            # need a data structure to associated statements with a label
            working_block.add(statement)
        #Pass
        elif statement.__class__.__name__ == "Pass":
            working_block.add(statement)

        #Break
        elif statement.__class__.__name__ == "Break":
            #debug_print("  break statement on line " + str(statement.coord.line))

            #// Captures the break in a block
            working_block._id = blockNum
            working_block._type = BlockType.LOOP_JUMP
            working_block._exit_break = ExitType.HANGING_BREAK
            working_block.add(statement)

            #// Commit the current working_block
            add_to_basic_block_list(return_list, working_block)
            blockNum += 1

            #Create a new the working_block with new parameters
            working_block = BasicBlock(blockNum)

        elif statement.__class__.__name__ == "Compound":
            x = "stop here"
            print("Further processing required...");

            ### EXCERPTED FROM "IF" CASE START
            #debug_print("  if statement on line " + str(statement.coord.line))

            blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)

            # captures the if statement evaluating expression in a block
            # debug_print("  Capturing if statement expression in block")
            # working_block._type = BlockType.CONDITIONAL
            # working_block._exit_true = blockNum + 1
            # Todo -- Q: what does expression mean and what is the test value
            # A: statement.test is looking at the if condition
            # working_block._expression = statement.cond
            #
            # add_to_basic_block_list(return_list, working_block)
            #
            # blockNum += 1
            #Todo evaluate that above commented out portion is ok to do this.
            # Reasoning: For if statements, the "if" portion is separated from the "iftrue" and "iffalse"
            # all of which are in different blocks. Compounds though aren't really a the same in my opinion and
            # don't really need that extra layer? The only time they are found inside of a traversal is when looking
            # at certain edge cases, otherwise they're typically encompassed in a single statement. But compounds
            # in the edge cases act more as a collection of nodes? There's also no conditional checks which makes it
            # even less of a fit for this specific mold...

            debug_print("  Calling make_basic_blocks for if statements")
            stmt_list = make_basic_blocks(statement.block_items,
                                        blockNum)
            for bb in stmt_list:
                add_to_basic_block_list(return_list, bb)

            working_block._exit_false = ExitType.HANGING_BLOCK_EXIT #because no else list, always will default to this
            blockNum += len(stmt_list)

            # prepare everything to link to the block we are just about to create
            replace_exits(return_list, ExitType.HANGING_BLOCK_EXIT, blockNum)

            # recreate the working_block with new parameters
            working_block = BasicBlock(blockNum)
            working_block._exit_true = blockNum + 1
            ### EXCERPTED FROM "IF" CASE END



        #Continue
        elif statement.__class__.__name__ == "Continue":
            #debug_print("  break statement on line " + str(statement.coord.line))

            #// Captures the break in a block
            working_block._id = blockNum
            working_block._type = BlockType.LOOP_JUMP
            working_block._exit_break = ExitType.HANGING_CONTINUE
            working_block.add(statement)

            #// Commit the current working_block
            add_to_basic_block_list(return_list, working_block)
            blockNum += 1

            #Create a new the working_block with new parameters
            working_block = BasicBlock(blockNum)

        elif statement.__class__.__name__ == "Label":
            #TODO Maybe do something here to make the output graph png show the label more clearly
            # to avoid confunsion. Currently just shows the statements of the bb, but not the label itself


            #debug_print("Label statement on line " + str(statement.coord.line))

            blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)
            debug_print("  Calling make_basic_blocks for all label statements")
            label_dict[statement.name] = blockNum
            allowable_label_stmts = []

            #obtain all statements within the label
            #list will end upon seeing
            #   - labels (do not include)
            #   - goto   (do not include)
            #   - if     (do not include)
            #   - return (include)
            # also make sure to increment skip_num for each statement added

            for i in range (index, len(block_items)):
                after_label_stmt = block_items[i]


                disallowed_types = ["Label", "Goto", "If"]
                if after_label_stmt.__class__.__name__ == "Return":
                    allowable_label_stmts.append(after_label_stmt)
                    skip_num += 1
                    break
                elif after_label_stmt.__class__.__name__ in disallowed_types:
                    break
                else:
                    allowable_label_stmts.append(after_label_stmt)
                    skip_num += 1

            stmt_list = make_basic_blocks(allowable_label_stmts, blockNum)

            for bb in stmt_list:
                add_to_basic_block_list(return_list, bb)

            working_block._exit_false = ExitType.HANGING_BLOCK_EXIT  # because no else list, always will default to this
            blockNum += len(stmt_list)

            # prepare everything to link to the block we are just about to create
            replace_exits(return_list, ExitType.HANGING_BLOCK_EXIT, blockNum)

            # recreate the working_block with new parameters
            working_block = BasicBlock(blockNum)
            working_block._exit_true = blockNum + 1

        elif statement.__class__.__name__ == "Goto":
            #debug_print("  Goto statement on line " + str(statement.coord.line))
            blockNum, working_block = flush_normal_block(return_list, blockNum, working_block)

            # captures the goto in a single block
            working_block.add(statement)
            add_to_basic_block_list(return_list, working_block)

            # create a new working block
            blockNum += 1
            working_block = BasicBlock(blockNum)
        else:
            pass
            #raise Exception("encountered unknown block type: " + statement.__class__.__name__ + " " + ast.dump(statement))

    if working_block.statement_count() > 0:
        working_block._id = blockNum
        working_block._exit_true = ExitType.HANGING_BLOCK_EXIT
        add_to_basic_block_list(return_list, working_block)
        debug_print("Exiting, added working_block to list for block " + str(working_block._id))
    else:
        #replace_exits(return_list, blockNum, ExitType.HANGING_BLOCK_EXIT)
        print("Doing nothing as a fix to see") #We want to avoid creating more pointers to -2, and want to preserve an exit node instead.

    #??? otherwise we need to put -2s back?
    #Looping back around to adjust the exit_true according to the known labels
    #Essentially in the "first pass" we are looking at labels (see above if-else tree) and associating a block to a label
    #Then for every Goto statement, we are checking that the name it's jumping to is a label and not a variable name.
    #We do this by collecting the name to which the goto is "going to" and checking if there is a block associated with that name
    #A block associated with the name would imply that the Goto is "going to" a label, if not found -- implies that goto is "going to" a variable name.
    for block in return_list:
        for stmt in block._statements:
            if stmt.__class__.__name__ == "Goto":
                label_name = stmt.name

                if not label_dict.keys().__contains__(label_name):
                    raise Exception(f"Label {label_name} has no associated block number. This is likely from a \"goto\" "
                                    f"statement in which the destination is a variable name. This is unsupported.")
                block_num = label_dict[label_name]
                block._exit_true = block_num
                block._exit_false = block_num

    return return_list


def print_basic_blocks(input):
    print
    print("DISPLAYING BASIC BLOCKS:")

    if len(input) == 0:
        debug_print("  ERROR: Block list is empty.")
    else:
        for bb in input:
            debug_print("Block " + str(bb._id) + ": type = " + str(bb._type) + ", leader = " + str(bb._leader))
            debug_print("  exits: true = " + str(bb._exit_true) + ", false = " + str(bb._exit_false) + ", break = " + str(bb._exit_break) + ", expt = " + str(bb._exit_expt))
            debug_print("  CONTAINS (" + str(bb.statement_count()) + "):")

            if bb._type == 1:
                local_ss = bb._statements

                if local_ss == []:
                    debug_print("    ERROR: Block has no statements.")
                else:
                    for s in local_ss:
                        if hasattr(s, "coord"):
                            debug_print("    type " + s.__class__.__name__+" from line " + str(s.coord.line))
            elif bb._type == ExitType.UNSET:
                debug_print("    type not set.")
            else:
                debug_print("    Expression data")

