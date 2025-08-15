class CodeGenInfo:
    def __init__(self):
        self.program_block = []
        self.pb_i = 0

        self.word_size = 4
        self.data_address = 1000  # Starting address for variables
        self.temp_address = 4000  # Starting address for temporary variables

        self.return_address = 0
        self.return_value = 0

        self.last_used_id = None
        self.current_func = None    # what function we are currently calling
        self.func_arg_num = 0       # how many parameters a function has
        self.eq_count = 0           # how many consecutive assignment are in one line
        self.arg_start_pointer = 0  #start of arg pushed in to stack for function call
        
        self.arg_declaration = False    # wether we are declaring function parameters
        self.declaring_main = False
        self.arr_ass = False            # wether we have an assignment in arr index
        self.func_ass = False           # wether we have an assignment in func arg
        
        self.loop_stack = []            # stack to hold all lines we break out of loop
        self.recursive_stack = []       # stack for holding information of last func call during new one

    def increase_data_address(self, size):
        self.data_address += size

    def get_data_address(self):
        return self.data_address
        
    def increase_temp_address(self, size):
        self.temp_address += size

    def get_temp_address(self):
        return self.temp_address

    def inc_func_arg_num(self):
        self.func_arg_num += 1

    def reset_func_arg_num(self):
        self.func_arg_num = 0
    
    def set_arg_declaration(self, arg_declaration):
        self.arg_declaration = arg_declaration

    def get_arg_declaration(self):
        return self.arg_declaration

    def enter_loop(self):
        self.loop_stack.append([])

    def add_break(self, address):
        self.loop_stack[-1].append(address)
    
    def exit_loop(self):
        self.loop_stack.pop()
