class ID_entry:
    def __init__(self, lexeme, type, role, arg_num, scope, address, jmp_add):
        """
        type: [int, void]
        role: [var, arr, func]
        arg_num for function param count, for array element count
        """
        self.lexeme = lexeme
        self.type = type
        self.role = role
        self.arg_num = arg_num
        self.scope = scope
        self.address = address
        self.jmp_add = jmp_add


class ScopeStack:
    def __init__(self, upperStack=None):
        self.scopeStack = []
        self.upperStack = upperStack
    
    def add(self, lexeme, type, address, is_declaration=False):
        if is_declaration:
            id_entry = ID_entry(lexeme, type, "var", None, self, address, None)
            self.scopeStack.append(id_entry)
            return id_entry
        id_entry = self.get_IDentry(lexeme)
        if id_entry:
            return id_entry
        else:
            id_entry = ID_entry(lexeme, type, "var", None, self, address, None)
            self.scopeStack.append(id_entry)
            return id_entry

    def get_IDentry(self, lexeme):
        for entry in self.scopeStack:
            if entry.lexeme == lexeme:
                return entry
        if self.upperStack:
            return self.upperStack.get_IDentry(lexeme)
        return None
    
    def change_to_func(self, jmp_add):
        symbol = self.scopeStack[-1] if self.scopeStack else None
        if symbol is not None:
            symbol.jmp_add = symbol.address
            symbol.address = jmp_add
            symbol.role = 'func'
            symbol.arg_num = 0

    def change_to_array(self, arg_num):
        symbol = self.scopeStack[-1] if self.scopeStack else None
        if symbol is not None:
            symbol.role = 'arr'
            symbol.arg_num = arg_num

    def update_func_arg_num(self, arg_num):
        symbol = self.scopeStack[-1] if self.scopeStack else None
        if symbol is not None and symbol.role == 'func':
            symbol.arg_num = arg_num

class SymbolTable:
    def __init__(self):
        self.is_declaration = False
        self.symbols = []
        self.scopes = []
        self.scopes.append(ScopeStack())

    def add_symbol(self, lexeme, type, address):
        self.get_current_scope().add(lexeme, type, address, self.is_declaration)
        self.set_declaration(False)

    def change_to_array(self, arg_num):
        #change last symbol to array
        self.get_current_scope().change_to_array(arg_num)

    def change_to_func(self, jmp_add):
        #change last symbol to function
        self.get_current_scope().change_to_func(jmp_add)

    def update_function_arg_num(self, arg_num):
        self.get_current_scope().update_func_arg_num(arg_num)

    def lookup(self, lexeme):
        return self.get_current_scope().get_IDentry(lexeme)

    def enter_scope(self):
        self.scopes.append(ScopeStack(self.scopes[-1]))

    def exit_scope(self):
        self.scopes.pop()

    def get_current_scope(self):
        return self.scopes[-1]

    def set_declaration(self, is_declaration):
        self.is_declaration = is_declaration
