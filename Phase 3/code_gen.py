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

    #semantic actions
    def declare(self):
        self.symbol_table.set_declaration(True)

    def push_type(self, type):
        self.semantic_stack.push(type)

    def declare_id(self, lexeme):
        type = self.semantic_stack.pop()
        address = self.get_data_address()
        self.symbol_table.add_symbol(lexeme, type, address)
        self.info.last_used_id = lexeme
        if self.info.arg_declaration == True: # condition to count function arguments
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
            self.info.increase_data_address(self.info.word_size * (arg_num - 1))
        self.symbol_table.change_to_array(arg_num)

    def save(self): ## save address of program block for later jump
        self.semantic_stack.push(self.info.pb_i)
        self.info.program_block.append("")
        self.info.pb_i += 1
    
    def declare_func(self): ##change type of id to func and set the address of program block cell for function call
        self.symbol_table.change_to_func(self.info.pb_i)
        #TODO enter new scorp       

    def params_start(self):
        self.info.reset_func_arg_num()
        self.info.set_arg_declaration(True)

    def params_end(self):
        self.info.set_arg_declaration(False)
        arg_num = self.info.func_arg_num
        self.symbol_table.update_function_arg_num(arg_num)  #TODO doesnt work because we defined new ids

    def func_return(self): ##
        pass

    def func_save_resolve(self):
        pb_i = self.semantic_stack.pop()
        self.info.program_block[pb_i] = f"(JP, {self.info.pb_i}, , )"

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

    #code genrator functions
    def get_data_address(self):
        addr = self.info.get_data_address()
        self.info.increase_data_address(self.info.word_size)
        return addr
    
    def get_temp_address(self):
        temp = self.info.get_temp_address()
        self.info.increase_temp_address(self.info.word_size)
        return temp
