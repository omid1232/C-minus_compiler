from code_gen_info import CodeGenInfo

class ID_entry:
    def __init__(self, lexeme, type, role, arg_num, scope, address):
        """
        type: [int, void]
        role: [variable, array, function]
        arg_num is int
        """
        self.lexeme = lexeme
        self.type = type
        self.role = role
        self.arg_num = arg_num
        self.scope = scope
        self.address = address


class ScopeStack:
    def __init__(self):
        self.scopeStack = []

    def push(self, scope):
        self.scopeStack.append(scope)
    
    def pop(self):
        if self.scopeStack:
            return self.scopeStack.pop()
        return None
    
    def get_scope(self):
        if self.scopeStack:
            return self.scopeStack[-1]
        return None
        

class SymbolTable:
    def __init__(self):
        self.is_declaration = False
        self.symbols = []
        self.scopeStack = ScopeStack()
        self.info = CodeGenInfo()

    def add_symbol(self, lexeme):
        current_scope = self.scopeStack.get_scope()
        if current_scope is not None:
            if self.is_declaration == True:
                symbol = ID_entry(lexeme, None, "variable", None, current_scope, self.info.get_address())
                self.symbols.append(symbol)
            else:
                if self.lookup(lexeme) is None:
                    symbol = ID_entry(lexeme, None, "variable", None, current_scope, self.info.get_address())
            self.info.increase_address(lexeme)

    def add_empty_symbol_type(self, type):
        current_scope = self.scopeStack.get_scope()
        if current_scope is not None:
            symbol = ID_entry(None, type, None, None, current_scope, self.info.get_address())
            # update address on add_symbol_lexeme
            self.symbols.append(symbol)

    def add_symbol_lexeme(self, lexeme):
        # add lexeme to the last symbol in the symbols list (for declaration)
        symbol = self.symbols[-1] if self.symbols else None
        if symbol is not None:
            symbol.lexeme = lexeme
            self.info.increase_address(lexeme)

    def change_to_array(self, arg_num):
        #change last symbol to array
        symbol = self.symbols[-1] if self.symbols else None
        if symbol is not None:
            symbol.role = 'array'
            symbol.arg_num = arg_num

    def change_to_func(self):
        #change last symbol to function
        symbol = self.symbols[-1] if self.symbols else None
        if symbol is not None:
            symbol.role = 'function'
            symbol.arg_num = 0

    def update_function_arg_num(self, arg_num):
        symbol = self.symbols[-1] if self.symbols else None
        if symbol is not None and symbol.role == 'function':
            symbol.arg_num = arg_num

    def lookup(self, lexeme):
        for symbol in reversed(self.symbols):
            if symbol.lexeme == lexeme:
                return symbol
        return None

    def enter_scope(self):
        self.scopeStack.push()

    def exit_scope(self):
        current_scope = self.scopeStack.get_scope()
        index = len(self.symbols) - 1
        while index >= 0 and self.symbols[index].scope == current_scope:
            self.symbols.pop()
            index -= 1
        self.scopeStack.pop()

    def set_declaration(self, is_declaration):
        self.is_declaration = is_declaration