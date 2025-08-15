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
        self.info.return_address = self.get_data_address()
        self.info.return_value = self.get_data_address()
        self.info.program_block.append(f"(ASSIGN, #{self.info.return_address}, {self.info.return_address}, )")
        self.info.pb_i += 1

        self.ops = {'+': 'ADD', '-': 'SUB', '*': 'MULT', '<': 'LT', '==': 'EQ'}

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
            if id_entry.role == 'func': # means we are calling another function
                # save return address of last call
                temp = self.get_temp_address()
                self.info.program_block.append(f"(ASSIGN, {self.info.return_address}, {temp}, )")
                self.info.pb_i += 1
                # save info in recursive stack
                self.info.recursive_stack.append(temp)
                self.info.recursive_stack.append(self.info.current_func)
                self.info.recursive_stack.append(self.info.arg_start_pointer)
                self.info.current_func = id_entry

            if id_entry.lexeme != "output":
                if id_entry.role == 'arr':
                    self.semantic_stack.push(f"#{id_entry.address}")
                else:
                    self.semantic_stack.push(id_entry.address)

    def pnum(self, token_string):
        self.semantic_stack.push(f'#{token_string}')

    def declare_arr(self, has_arg_num):
        arg_num = None
        role = 'arr_param'
        if has_arg_num:
            arg_num = int(self.semantic_stack.pop()[1:])
            self.info.increase_data_address(self.info.word_size * (arg_num - 1))
            role = 'arr'
        self.symbol_table.change_to_array(arg_num, role)

    def save(self): ## save address of program block for later jump
        if self.info.current_func is not None and self.info.current_func.lexeme == "output":
            return
        self.semantic_stack.push(self.info.pb_i)
        self.info.program_block.append("")
        self.info.pb_i += 1
    
    def declare_func(self): ##change type of id to func and set the address of program block cell for function call
        lexeme = self.symbol_table.change_to_func(self.info.pb_i)
        if lexeme == "main":
            self.info.declaring_main = True

    def params_start(self):
        self.info.reset_func_arg_num()
        self.info.set_arg_declaration(True)

    def params_end(self):
        self.info.set_arg_declaration(False)
        arg_num = self.info.func_arg_num
        self.symbol_table.update_function_arg_num(arg_num)

    def func_return(self): ## return to after function call stored in return_address
        if self.info.declaring_main:
            self.info.program_block.append(f"(JP, {self.info.pb_i + 2}, , )")
        else:
            self.info.program_block.append(f"(JP, @{self.info.return_address}, , )")
        self.info.pb_i += 1

    def func_save_resolve(self):
        pb_i = self.semantic_stack.pop()
        self.info.program_block[pb_i] = f"(JP, {self.info.pb_i}, , )"
        # jump to outside for ending program after main
        if self.info.declaring_main:
            self.info.program_block.append(f"(JP, {pb_i + 1}, , )")
            self.info.program_block.append(f"(ASSIGN, {self.info.return_address}, {self.info.return_address}, )")
            self.info.pb_i += 2

    def new_scope(self):
        self.symbol_table.enter_scope()

    def end_scope(self):
        self.symbol_table.exit_scope()

    def jpf_save(self): ## jump address and expression value should be at ss(top) and ss(top-1)
        pb_i = self.semantic_stack.pop()
        self.info.program_block[pb_i] = f"(JPF, {self.semantic_stack.pop()}, {self.info.pb_i + 1}, )"
        self.info.program_block.append("")
        self.semantic_stack.push(self.info.pb_i)
        self.info.pb_i += 1

    def jp(self): ## fill saved jump to out of if statement
        pb_i = self.semantic_stack.pop()
        self.info.program_block[pb_i] = f"(JP, {self.info.pb_i}, , )"

    def label(self): ## save address of before while condition
        self.info.enter_loop()
        self.semantic_stack.push(self.info.pb_i)

    def while_end(self): ## fill jumps for false and correct conditions based on 3 values in ss
        # get every break from inside while loop
        breaks = self.info.loop_stack[-1] if self.info.loop_stack else []
        a_while_add = self.semantic_stack.pop()
        expression_val = self.semantic_stack.pop()
        b_while_add = self.semantic_stack.pop()
        # set break jumps to outside
        for i in range(len(breaks)):
            self.info.program_block[breaks[i]] = f"(JP, {self.info.pb_i + 1}, , )"
        # jump to condition
        self.info.program_block[a_while_add] = f"(JPF, {expression_val}, {self.info.pb_i + 1}, )"
        self.info.program_block.append(f"(JP, {b_while_add}, , )")
        self.info.pb_i += 1
        self.info.exit_loop()

    def pret_value(self): ## push address of return value for assignment
        self.semantic_stack.push(self.info.return_value)

    def return_jmp(self):
        self.info.program_block.append(f"(JP, @{self.info.return_address}, , )")
        self.info.pb_i += 1 

    def inc_eq(self):
        self.info.eq_count += 1

    def dec_eq(self):
        self.info.eq_count -= 1

    def assign(self): ## assign ss(top) to ss(top-1)
        value_add = self.semantic_stack.pop()
        rv_add = self.semantic_stack.pop()
        self.info.program_block.append(f"(ASSIGN, {value_add}, {rv_add}, )")
        # if we jave multiple assignments, or assigning in arg function or arr index save address again
        if self.info.eq_count > 0:
            self.semantic_stack.push(rv_add)
        elif self.info.arr_ass:
            self.semantic_stack.push(rv_add)
        elif self.info.func_ass:
            self.semantic_stack.push(rv_add)
        self.info.pb_i += 1

    def parr(self): ## id of arr and expression value are in stack
        offset = self.semantic_stack.pop()
        id_add = self.semantic_stack.pop()
        temp = self.get_temp_address()
        # calc offset and add to base address
        self.info.program_block.append(f"(MULT, #{self.info.word_size}, {offset}, {temp})")
        self.info.program_block.append(f"(ADD, {id_add}, {temp}, {temp})")
        self.semantic_stack.push(f"@{temp}")    #TODO check later
        self.info.pb_i += 2

    def arr_ass_flag(self):
        self.info.arr_ass = True

    def arr_ass_reset(self):
        self.info.arr_ass = False

    def math_exec(self): ## based on op do one math expression and store in temp
        second = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        first = self.semantic_stack.pop()
        temp = self.get_temp_address()
        self.info.program_block.append(f"({op}, {first}, {second}, {temp})")
        self.info.pb_i += 1
        self.semantic_stack.push(temp)

    def push_op(self, op): ## store op for math
        self.semantic_stack.push(self.ops[op])

    def p0(self): ## store 0 for minus ops
        self.semantic_stack.push(f"#0")

    def args_start(self): ##
        self.info.arg_start_pointer = len(self.semantic_stack.stack)

    def func_ass_flag(self):
        self.info.func_ass = True

    def func_ass_reset(self):
        self.info.func_ass = False

    def args_set(self): ##
        func_add = self.info.current_func.jmp_add
        func_arg_num = len(self.semantic_stack.stack) - self.info.arg_start_pointer
        for arg in range(len(self.semantic_stack.stack), self.info.arg_start_pointer, -1):
            arg_add = self.semantic_stack.pop()
            self.info.program_block.append((f"(ASSIGN, {arg_add}, {func_add + (func_arg_num * self.info.word_size)}, )"))
            func_arg_num -= 1
            self.info.pb_i += 1

    def func_call(self): ##
        # if func is output we just print
        if self.info.current_func.lexeme == "output":
            self.info.program_block.append(f"(PRINT, {self.semantic_stack.pop()}, , )")
            self.info.pb_i += 1
            self.info.arg_start_pointer = self.info.recursive_stack.pop()
            self.info.current_func = self.info.recursive_stack.pop()
            temp = self.info.recursive_stack.pop()
            self.info.program_block.append(f"(ASSIGN, {temp}, {self.info.return_address}, )")
            self.info.pb_i += 1
            return
        self.args_set()

        self.info.program_block.append(f"(ASSIGN, #{self.info.pb_i + 2}, {self.info.return_address}, )")
        pb_func_add = self.semantic_stack.pop()
        self.info.program_block.append(f"(JP, {pb_func_add}, , )")
        self.info.pb_i += 2

        self.set_ret_Val()
        # get info from before last call
        self.info.arg_start_pointer = self.info.recursive_stack.pop()
        self.info.current_func = self.info.recursive_stack.pop()
        temp = self.info.recursive_stack.pop()
        self.info.program_block.append(f"(ASSIGN, {temp}, {self.info.return_address}, )")
        self.info.pb_i += 1

    def set_ret_Val(self):
        result = self.get_temp_address()
        if self.info.current_func.type == "int":
            self.info.program_block.append(f"(ASSIGN, {self.info.return_value}, {result}, )")
            self.info.pb_i += 1
        self.semantic_stack.push(result)
        if self.info.current_func.type == "void":
            self.semantic_stack.pop()

    def add_break(self):
        self.info.program_block.append("")
        self.info.add_break(self.info.pb_i)
        self.info.pb_i += 1

    #code genrator functions
    def get_data_address(self):
        addr = self.info.get_data_address()
        self.info.increase_data_address(self.info.word_size)
        return addr
    
    def get_temp_address(self):
        temp = self.info.get_temp_address()
        self.info.increase_temp_address(self.info.word_size)
        return temp
    
    def debug(self, step):
        print(step)
        print(self.semantic_stack.stack)
        print(self.info.program_block)
        print(self.info.pb_i)
        print("\n")
        pass
    
    def output(self, path):
        with open(path, "w") as f:
            for i, l in enumerate(self.info.program_block):
                f.write(f"{i}\t{l}\n")
