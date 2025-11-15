__author__ = 'Ruben'

#http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def enum(**enums):
    return type('Enum', (), enums)

BlockType = enum(NORMAL=1, CONDITIONAL=2, LOOP_JUMP=3)

ExitType = enum(UNSET=-1, HANGING_BLOCK_EXIT=-2, HANGING_BREAK=-3, HANGING_CONTINUE=-4)

#data structures
class BasicBlock(object):
    def __init__(self, block_id = -1):

        self._statements = []
        self._expression = None

        self._id = block_id
        self._leader = 0
        self._type = BlockType.NORMAL

        #a -2 represents that it should be connected to whatever is on the outside
        self._exit_true = ExitType.UNSET
        self._exit_false = ExitType.UNSET
        self._exit_break = ExitType.UNSET

        self._expt_name = ""
        self._exit_expt = ExitType.UNSET

        self._exception_handler = -1

    def add(self, statement):
        self._statements.append(statement)

    def statement_count(self):
        return len(self._statements)