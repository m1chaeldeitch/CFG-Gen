#http://greentreesnakes.readthedocs.org/en/latest/
import ast
from astmonkey import visitors

def enum(**enums):
    return type('Enum', (), enums)

DisplayOrder = enum(DISCOVERED=1, LINE=2)

SemanticFlags = enum(OSSEP=1, OPENED=2, CLOSED=3, FILEEXT=4)
def get_flag_name(flag):
    if flag == SemanticFlags.OSSEP:
        return "OS.SEP"
    elif flag == SemanticFlags.OPENED:
        return "OPENED"
    elif flag == SemanticFlags.CLOSED:
        return "CLOSED"
    elif flag == SemanticFlags.FILEEXT:
        return "FILE EXT"
    else:
        return "Unknown"

class SymbolEntry(object):
    def __init__(self, name, value):
        self._name = name
        self._values = [value]

        self._opened = False
        self._closed = False

        self._flags = []

        self.analyze_value()

    def value_has_ossep(self, op):
        if isinstance(op, ast.BinOp):
            if isinstance(op.op, ast.Add):
                return self.value_has_ossep(op.left) or self.value_has_ossep(op.right)
            elif isinstance(op.op, ast.Sub): #not defined for strings.
                return False
            else:
                raise BaseException("ERROR: ExprHasOSSep::Unknown Operator")

        elif isinstance(op, ast.Num) or isinstance(op, ast.Str):
            return False

        elif isinstance(op, ast.Call):
            return False

        elif isinstance(op, ast.Attribute):
            if op.attr == "sep" and op.value.id == "os":
                return True
            return False

        elif isinstance(op, ast.Subscript):
            return False

        elif isinstance(op, ast.Name):         #HACK: ???
            return False

        else:
            raise BaseException("ERROR: ExprHasOSSep::dfdfdfkljklq")

    def analyze_value(self):

        self._flags = []

        #hack: for now just analyze the first value
        value = self._values[0]

        if self._opened:
            self._flags += [SemanticFlags.OPENED]

        if self._closed:
            self._flags += [SemanticFlags.CLOSED]

        if(self.value_has_ossep(value)):
            self._flags += [SemanticFlags.OSSEP]

        if isinstance(value, ast.Str):
            if len(value.s) > 3 and value.s[-4] == ".":
                self._flags += [SemanticFlags.FILEEXT]

    def is_filename(self):

        return SemanticFlags.FILEEXT in self._flags

    def is_file_related(self):

        flags = self._flags[:]

        if SemanticFlags.OSSEP in flags:
            flags.remove(SemanticFlags.OSSEP)

        if flags:
            return True

        return False

    def assignment_count(self):
        return len(self._values)

    def last_value(self):
        return self._values[-1]

    def add_assignment(self, value):
        self._values += [value]


#visits every assignment and inserts it into the symbol table.
class VisitorCollectAssignments(ast.NodeVisitor):
    def __init__(self, symtable):
        self._symtable = symtable

    def visit_Assign(self, node):

        for target in node.targets:
            self._symtable.insert_assignment(target.id, node.value)

class VisitorFindIOAccess(ast.NodeVisitor):
    def __init__(self, table):
        self._table = table

    def visit_Assign(self, node):
        #check for a file being opened
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if(node.value.func.id == "open"):   #assuming std library
                    for target in node.targets:
                        self._table[target.id]._opened = True

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if(node.func.attr == "close"):          #assuming std library
                self._table[node.func.value.id]._closed = True

class SymbolTable(object):
    def __init__(self):

        self._entries = []

    def insert_assignment(self, name, value):

        #check if we have already seen it
        for entry in self._entries:
            if name == entry._name:
                entry.add_assignment(value)
                return

        new_entry = SymbolEntry(name, value)

        self._entries += [new_entry]

    def analyze_entries(self):
        for entry in self._entries:
            entry.analyze_value()

    def display(self, filter_ra=True, order=DisplayOrder.DISCOVERED):

        ordered_entries = self._entries

        if order == DisplayOrder.LINE:
            ordered_entries = sorted(self._entries, key=lambda x: x._line_number)

        print "Name".ljust(20),
        print "filename".ljust(10),
        print "flags".ljust(20),
        print "constant".ljust(8),
        print

        checked = dict({True: "Y", False: ""})

        for entry in ordered_entries:

            if filter_ra and "RA_" in entry._name:
                continue

            print entry._name.ljust(20),
            print str(entry.is_filename()).ljust(10),
            print ", ".join([get_flag_name(x) for x in entry._flags]).ljust(20),

            if entry.assignment_count() == 1:
                print visitors.to_source(entry.last_value()).strip().ljust(8),
            else:
                print "".ljust(8),
            print

    def __iter__(self):
        for item in self._entries:
            yield item

    def __getitem__(self, key):

        found = None

        for entry in self._entries:
            if key == entry._name:
                found = entry
                break

        return found


def generate(block_list):
    symtable = SymbolTable()

    for block in block_list:
        block_module = ast.Module(block._statements)

        #collect all assignments in this block
        VisitorCollectAssignments(symtable).visit(block_module)

        VisitorFindIOAccess(symtable).visit(block_module)

    symtable.analyze_entries()

    return symtable