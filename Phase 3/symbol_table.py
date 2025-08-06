class Symbol:
    def __init__(self, lexeme, type, scope):
        self.lexeme = lexeme
        self.type = type
        self.scope = scope


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
        self.symbols = []
        self.scopeStack = ScopeStack()

    def add_symbol(self, lexeme, type):
        current_scope = self.scopeStack.get_scope()
        if current_scope is not None:
            symbol = Symbol(lexeme, type, current_scope)
            self.symbols.append(symbol)

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