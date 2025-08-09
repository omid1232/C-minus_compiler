from symbol_table import SymbolTable
from code_gen_info import CodeGenInfo

class SemanticStack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def get_top(self):
        if self.stack:
            return self.stack[-1]
        return None

class CodeGen:
    def __init__(self):
        self.semantic_stack = SemanticStack()
        self.symbol_table = SymbolTable()
        self.info = CodeGenInfo()

    def declare(self):
        self.symbol_table.set_declaration(True)

    def push_type(self, type):
        self.symbol_table.add_empty_symbol_type(type)

    def declare_id(self, lexeme):
        self.symbol_table.add_symbol_lexeme(lexeme)
        if self.info.get_counting_func_arg(): # condition to count function arguments
            self.info.inc_func_arg_num()

    def pid(self, id):
        # id is lexeme of the identifier
        id_entry = self.symbol_table.lookup(id)
        if id_entry is not None:
            self.semantic_stack.push(id_entry.address)

    def pnum(self, token_string):
        self.semantic_stack.push(f'#{token_string}')

    def declare_arr(self, has_arg_num):
        arg_num = None
        if has_arg_num:
            arg_num = int(self.semantic_stack.pop()[1:])
        self.symbol_table.change_to_array(arg_num)

    def declare_func(self):
        self.symbol_table.change_to_func()

    def params_start(self):
        self.info.reset_func_arg_num()
        self.info.set_counting_func_arg(True)

    def params_end(self):
        self.info.set_counting_func_arg(False)
        arg_num = self.info.get_func_arg_num()
        self.info.reset_func_arg_num()
        self.symbol_table.update_function_arg_num(arg_num)

    def func_return(self): ##
        pass

    def save(self): ##
        pass

    def jpf_save(self): ##
        pass

    def jp(self): ##
        pass

    def label(self): ##
        pass

    def while_end(self): ##
        pass

    def pvalue(self): ##
        pass

    def assign(self): ##
        pass

    def parr(self): ##
        pass

    def math_exec(self): ##
        pass

    def push_op(self): ##
        pass

    def p0(self): ##
        pass

    def args_start(self): ##
        pass

    def args_end(self): ##
        pass

    def func_call(self): ##
        pass