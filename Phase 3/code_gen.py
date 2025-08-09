from symbol_table import SymbolTable

class SemanticStack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return None

    def get_top(self):
        if not self.is_empty():
            return self.stack[-1]
        return None

class CodeGen:
    def __init__(self):
        self.semantic_stack = SemanticStack()
        self.symbol_table = SymbolTable()

    def declare():
        pass

    def push_type(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.semantic_stack.push(item)

    def declare_id(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.add(item)
            self.semantic_stack.push(item)

    def pid(self, id):
        id_entry = self.symbol_table.lookup(id)
        if id_entry is not None:
            self.semantic_stack.push(id_entry.address)

    def pnum(self, token_string):
        self.semantic_stack.push(f'#{token_string}')

    def declare_arr(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.add_array(item)
            self.semantic_stack.push(item)

    def declare_func(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.add_function(item)
            self.semantic_stack.push(item)

    def params_start(self): ##
        self.semantic_stack.push([])

    def params_end(self): ##
        params = self.semantic_stack.pop()
        if isinstance(params, list):
            func = self.semantic_stack.get_top()
            if func is not None:
                func['params'] = params
                self.symbol_table.update_function(func)
                self.semantic_stack.push(func)

    def func_return(self): ##
        func = self.semantic_stack.get_top()
        if func is not None:
            self.symbol_table.mark_function_as_returned(func)
            self.semantic_stack.push(func)

    def save(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.save(item)
            self.semantic_stack.push(item)

    def jpf_save(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.save_jpf(item)
            self.semantic_stack.push(item)

    def jp(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.jump(item)
            self.semantic_stack.push(item)

    def label(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.add_label(item)
            self.semantic_stack.push(item)

    def while_end(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.end_while(item)
            self.semantic_stack.push(item)

    def pvalue(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.push_value(item)
            self.semantic_stack.push(item)

    def assign(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.assign_value(item)
            self.semantic_stack.push(item)

    def parr(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.push_array(item)
            self.semantic_stack.push(item)

    def math_exec(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.symbol_table.execute_math(item)
            self.semantic_stack.push(item)

    def push_op(self): ##
        item = self.semantic_stack.get_top()
        if item is not None:
            self.semantic_stack.push(item)

    def p0(self): ##
        pass

    def args_start(self):
        pass

    def args_end(self):
        pass

    def func_call(self):
        pass

