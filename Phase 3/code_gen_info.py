class CodeGenInfo:
    def __init__(self):
        self.address = 100  # Starting address for variables
        self.temp = 500  # Starting address for temporary variables
        self.func_arg_num = 0
        self.counting_func_arg = False

    def increase_address(self, lexeme):
        # Increase address by 4 for each new variable
        self.address += 4

    def get_address(self):
        return self.address
        
    def increase_temp(self):
        # Increase temp address by 4 for each new temporary variable
        self.temp += 4

    def get_temp(self):
        return self.temp

    def inc_func_arg_num(self):
        self.func_arg_num += 1

    def reset_func_arg_num(self):
        self.func_arg_num = 0

    def get_func_arg_num(self):
        return self.func_arg_num
    
    def set_counting_func_arg(self, value):
        self.counting_func_arg = value

    def get_counting_func_arg(self):
        return self.counting_func_arg