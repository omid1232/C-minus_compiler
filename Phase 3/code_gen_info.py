class CodeGenInfo:
    def __init__(self):
        self.word_size = 4
        self.data_address = 500  # Starting address for variables
        self.temp_address = 900  # Starting address for temporary variables
        self.last_used_id = None
        self.func_arg_num = 0    # how many parameters a function has
        self.arg_declaration = False    # wether we are declaring function parameters
        self.arg_start_pointer = 0 #start of arg pushed in to stack for function call
        self.program_block = []
        self.pb_i = 0
        self.current_func = None
        self.return_address = 0
        self.return_value = 0
        self.declaring_main = False

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
