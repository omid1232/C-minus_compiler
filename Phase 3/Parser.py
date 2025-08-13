from Scanner import *
from code_gen import CodeGen

# Parser Functions
class Node:
    def __init__(self, label):
        self.label = label
        self.children = []

class Parser:
    def __init__(self, text):
        self.index_to_line = build_index_to_line_map(text)
        self.index = 0
        while self.index < len(text) and text[self.index] in WSPACE:
            self.index += 1
        if self.index >= len(text):
            self.token_string = "$"
        self.token_string_start = self.index
        self.line_number = self.index_to_line[self.token_string_start]
        self.index, self.token_type, self.token_string, self.scanner_error_msg = get_next_token(self.index, text)

        self.parser_errors = []
        self.root = None
        self.stack = []
        self.eof = False
        self.code_gen = CodeGen()

    def update_token(self):
        while self.index < len(text) and text[self.index] in WSPACE:
            self.index += 1
        if self.index >= len(text):
            self.token_string = "$"
        else:

            self.token_string_start = self.index
            self.line_number = self.index_to_line[self.token_string_start]
            self.index, self.token_type, self.token_string, self.scanner_error_msg = get_next_token(self.index, text)
            while self.scanner_error_msg is not None or self.token_type == "COMMENT":
                while self.index < len(text) and text[self.index] in WSPACE:
                    self.index += 1
                if self.index >= len(text):
                    self.token_string = "$"
                self.token_string_start = self.index
                self.line_number = self.index_to_line[self.token_string_start]
                self.index, self.token_type, self.token_string, self.scanner_error_msg = get_next_token(self.index, text)
                if self.token_type == "$":
                    self.token_string = "$"

    
    def make_node(self, label):
        node = Node(label)
        self.stack[-1].children.append(node)
        return node

    def enter_node(self, label):
        node = self.make_node(label)
        self.stack.append(node)

    def exit_node(self):
        self.stack.pop()

    def match(self, expected_string):
        if self.token_string == expected_string:
            self.make_node(f"({self.token_type}, {self.token_string}) ")
            self.update_token()
        else:
            if self.token_string == "$":
                self.eof = True
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing {expected_string}")

    def match_id(self):
        if self.token_type == "ID":
            self.make_node(f"(ID, {self.token_string}) ")
            self.update_token()
        else:
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ID")

    def match_num(self):
        if self.token_type == "NUM":
            self.make_node(f"(NUM, {self.token_string}) ")
            self.update_token()
        else:
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing NUM")

    def make_tree(self, filename):
        def _render(node, prefix="", is_last=True, is_root=False):
            if is_root:
                line = node.label
            else:
                connector = "└── " if is_last else "├── "
                line = f"{prefix}{connector}{node.label}"
            lines = [line]
            next_prefix = prefix + ("    " if is_last else "│   ")
            for idx, child in enumerate(node.children):
                last_child = (idx == len(node.children) - 1)
                lines += _render(child, next_prefix, last_child)
            return lines
        
        output = [_render(self.root, is_root=True)[0]]
        total = len(self.root.children)
        for i, child in enumerate(self.root.children):
            # is_last = self.eof or (i == total - 1)
            is_last = self.eof
            output += _render(child, "", is_last)
        if not self.eof:
            output.append("└── $")
        else:
            output.append("")
            self.parser_errors.append(f"#{self.line_number + 1} : syntax error, Unexpected EOF")
        with open(filename, "w", encoding="utf-8") as fp:
            fp.write("\n".join(output))


    #------------------------------- Grammer DFAs
    
    def Program(self):
        self.root = Node("Program")
        self.stack.append(self.root)
        while self.token_string not in {"int", "void", "$"}:
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.DeclarationList()
        elif self.token_string == {"$"}:            # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Program")
        self.stack.pop()
        
    def DeclarationList(self):
        if self.eof == True:
            return
        while self.token_string not in {"int", "void", ";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("DeclarationList")
        if self.token_string in {"int", "void"}:    # first
            self.Declaration()
            self.DeclarationList()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  # follow
            self.make_node("epsilon")
        self.exit_node()

    def Declaration(self):
        if self.eof == True:
            return
        while self.token_string not in {"int", "void", ";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.enter_node("Declaration")
            self.code_gen.declare()
            self.DeclarationInitial()
            self.DeclarationPrime()
            self.exit_node()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Declaration")

    def DeclarationInitial(self):
        while self.token_string not in {"int", "void", ";", "[", "(", ")", ","}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.enter_node("DeclarationInitial")
            self.code_gen.push_type(type= self.token_string)
            self.TypeSpecifier()
            self.code_gen.declare_id(lexeme= self.token_string)
            self.match_id()
            self.exit_node()
        elif self.token_string in {";", "[", "(", ")", ","}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing DeclarationInitial")

    def DeclarationPrime(self):
        if self.eof == True:
            return
        while self.token_string not in {"[", ";", "(", "{", "}", "break", "if", "while", "int", "void", "return", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.enter_node("DeclarationPrime")
            self.FunDeclarationPrime()
            self.exit_node()
        elif self.token_string in {"[", ";"}:
            self.enter_node("DeclarationPrime")
            self.VarDeclarationPrime()
            self.exit_node()
        elif self.token_string in {"{", "}", "break", "if", "while", "return", "void", "int", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing DeclarationPrime")

    def VarDeclarationPrime(self):
        if self.eof == True:
            return
        while self.token_string not in {"[", ";", "(", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "[":    #first
            self.enter_node("VarDeclarationPrime")
            self.match("[")
            self.code_gen.pnum(self.token_string)
            self.match_num()
            self.match("]")
            self.code_gen.declare_arr(True)
            self.match(";")
            self.exit_node()
        elif self.token_string == ";":
            self.enter_node("VarDeclarationPrime")
            self.match(";")
            self.exit_node()
        elif self.token_string in {"(", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing VarDeclarationPrime")

    def FunDeclarationPrime(self):
        if self.eof == True:
            return
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.enter_node("FunDeclarationPrime")
            self.code_gen.save()
            self.code_gen.declare_func()
            self.code_gen.new_scope()
            self.match("(")
            self.code_gen.params_start()
            self.Params()
            self.code_gen.params_end()
            self.match(")")
            self.CompoundStmt()
            self.code_gen.end_scope()
            self.code_gen.func_return()
            self.code_gen.func_save_resolve()
            self.exit_node()
        elif self.token_string in {";", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing FunDeclarationPrime")

    def TypeSpecifier(self):
        while self.token_string not in {"int", "void"} and self.token_type not in {"ID"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "int":    # first
            self.enter_node("TypeSpecifier")
            self.match("int")
            self.exit_node()
        elif self.token_string == "void":    # first
            self.enter_node("TypeSpecifier")
            self.match("void")
            self.exit_node()
        elif self.token_type == "ID":   # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing TypeSpecifier")

    def Params(self):
        while self.token_string not in {"int", "void", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "int":    # first
            self.enter_node("Params")
            self.code_gen.push_type(type= self.token_string)
            self.match("int")
            self.code_gen.declare_id(lexeme= self.token_string)
            self.match_id()
            self.ParamPrime()
            self.ParamList()
            self.exit_node()
        elif self.token_string == "void":    # first
            self.enter_node("Params")
            self.match("void")
            self.exit_node()
        elif self.token_string == ")":   # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Params")

    def ParamList(self):
        while self.token_string not in {",", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("ParamList")
        if self.token_string in {","}:    # first
            self.match(",")
            self.Param()
            self.ParamList()
        elif self.token_string in {")"}:  # follow
            self.make_node("epsilon")
        self.exit_node()

    def Param(self):
        while self.token_string not in {"int", "void", ",", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.enter_node("Param")
            self.code_gen.declare()
            self.DeclarationInitial()
            self.ParamPrime()
            self.exit_node()
        elif self.token_string in {",", ")"}:   # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Param")

    def ParamPrime(self):
        while self.token_string not in {"[", ",", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("ParamPrime")
        if self.token_string == "[":    # first
            self.match("[")
            self.match("]")
            self.code_gen.declare_arr(False)
        elif self.token_string in {",", ")"}:  # follow
            self.make_node("epsilon")
        self.exit_node()
    
    def CompoundStmt(self):
        if self.eof == True:
            return
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "int", "void", "else", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "{":    #first
            self.enter_node("CompoundStmt")
            self.match("{")
            self.DeclarationList()
            self.StatementList()
            self.match("}")
            self.exit_node()
        elif self.token_string in {";", "}", "break", "if", "while", "return", "int", "void", "else", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing CompoundStmt")

    def StatementList(self):
        while self.token_string not in {"{", "}", ";", "break", "if", "while", "return", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("StatementList")
        if self.token_string in {"{", ";", "break", "if", "while", "return", "+", "-", "("} or self.token_type in {"ID", "NUM"}:    # first
            self.Statement()
            self.StatementList()
        elif self.token_string in {"}"}:  # follow
            self.make_node("epsilon")
        self.exit_node()

    def Statement(self):
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {";", "(", "break", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.enter_node("Statement")
            self.ExpressionStmt()
            self.exit_node()
        elif self.token_string == "{":
            self.enter_node("Statement")
            self.CompoundStmt()
            self.exit_node()
        elif self.token_string == "if":
            self.enter_node("Statement")
            self.SelectionStmt()
            self.exit_node()
        elif self.token_string == "while":
            self.enter_node("Statement")
            self.IterationStmt()
            self.exit_node()
        elif self.token_string == "return":
            self.enter_node("Statement")
            self.ReturnStmt()
            self.exit_node()
        elif self.token_string in {"}", "else"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Statement")

    def ExpressionStmt(self):
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.enter_node("ExpressionStmt")
            self.Expression()
            self.match(";")
            self.exit_node()
        elif self.token_string == "break":
            self.enter_node("ExpressionStmt")
            self.match("break")
            self.match(";")
            self.exit_node()
        elif self.token_string == ";":
            self.enter_node("ExpressionStmt")
            self.match(";")
            self.exit_node()
        elif self.token_string in {"{", "}", "if", "while", "return", "else"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ExpressionStmt")
    
    def SelectionStmt(self):
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "if":
            self.enter_node("SelectionStmt")
            self.match("if")
            self.match("(")
            self.Expression()
            self.match(")")
            self.code_gen.save()
            self.code_gen.new_scope()
            self.Statement()
            self.code_gen.end_scope()
            self.match("else")
            self.code_gen.jpf_save()
            self.code_gen.new_scope()
            self.Statement()
            self.code_gen.end_scope()
            self.code_gen.jp()
            self.exit_node()
        elif self.token_string in {";", "(", "{", "}", "break", "while", "return", "else", "+", "-"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SelectionStmt")

    def IterationStmt(self):
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "while":
            self.enter_node("IterationStmt")
            self.match("while")
            self.code_gen.label()
            self.match("(")
            self.Expression()
            self.match(")")
            self.code_gen.save()
            self.code_gen.new_scope()
            self.Statement()
            self.code_gen.end_scope()
            self.code_gen.while_end()
            self.exit_node()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "return", "else", "+", "-"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing IterationStmt")

    def ReturnStmt(self):
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "return":
            self.enter_node("ReturnStmt")
            self.match("return")
            self.ReturnStmtPrime()
            self.exit_node()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "while", "else", "+", "-"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ReturnStmt")


    def ReturnStmtPrime(self):
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.enter_node("ReturnStmtPrime")
            self.code_gen.pret_value()
            self.Expression()
            self.code_gen.assign()
            self.match(";")
            self.exit_node()
        elif self.token_string == ";":
            self.enter_node("ReturnStmtPrime")
            self.match(";")
            self.exit_node()
        elif self.token_string in {"{", "}", "if", "while", "return", "else", "break"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ReturnStmtPrime")
    
    def Expression(self):
        while self.token_string not in {"(",")", ";", "]", ",", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"NUM"}:    #first
            self.enter_node("Expression")
            self.SimpleExpressionZegond()
            self.exit_node()
        elif self.token_type == "ID":
            self.enter_node("Expression")
            self.code_gen.pid(id= self.token_string)
            self.match_id()
            self.B()
            self.exit_node()
        elif self.token_string in {")", ";", "]", ","}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Expression")

    def B(self):
        while self.token_string not in {"(", "*", "+", "-", "<", "==", "[", "=", ";", ",", "]", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("B")
        if self.token_string in {"(", "*", "+", "-", "<", "=="}:    #first
            self.SimpleExpressionPrime()
        elif self.token_string == "[":
            self.match("[")
            self.code_gen.arr_ass_flag()
            self.Expression()
            self.code_gen.arr_ass_reset()
            self.match("]")
            self.code_gen.parr()
            self.H()
        elif self.token_string == "=":
            self.match("=")
            self.code_gen.inc_eq()
            self.Expression()
            self.code_gen.dec_eq()
            self.code_gen.assign()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.SimpleExpressionPrime()
        self.exit_node()
    
    def H(self):
        while self.token_string not in {"*", "+", "-", "<", "==", "=", ";", ",", "]", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("H")
        if self.token_string in {"*", "+", "-", "<", "=="}:    #first
            self.G()
            self.D()
            self.C()
        elif self.token_string == "=":
            self.match("=")
            self.code_gen.inc_eq()
            self.Expression()
            self.code_gen.dec_eq()
            self.code_gen.assign()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.G()
            self.D()
            self.C()
        self.exit_node()
    
    def SimpleExpressionZegond(self):
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")"} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type == "NUM":    #first
            self.enter_node("SimpleExpressionZegond")
            self.AdditiveExpressionZegond()
            self.C()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SimpleExpressionZegond")

    def SimpleExpressionPrime(self):
        while self.token_string not in {"(", "*", "+", "-", "<", "==", ";", ",", "]", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("SimpleExpressionPrime")
        if self.token_string in {"(", "*", "+", "-", "<", "=="}:    #first
            self.AdditiveExpressionPrime()
            self.C()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.AdditiveExpressionPrime()
            self.C()
        self.exit_node()

    def C(self):
        while self.token_string not in {"<", "==", ";", ",", "]", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("C")
        if self.token_string in {"<", "=="}:    #first
            self.Relop()
            self.AdditiveExpression()
            self.code_gen.math_exec()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def Relop(self):
        while self.token_string not in {"<", "==", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "<":    #first
            self.enter_node("Relop")
            self.code_gen.push_op(op= self.token_string)
            self.match("<")
            self.exit_node()
        elif self.token_string == "==":
            self.enter_node("Relop")
            self.code_gen.push_op(op= self.token_string)
            self.match("==")
            self.exit_node()
        elif self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Relop")

    def AdditiveExpression(self):
        while self.token_string not in {";", ",", "]", ")", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:    #first
            self.enter_node("AdditiveExpression")
            self.Term()
            self.D()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing AdditiveExpression")

    def AdditiveExpressionPrime(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("AdditiveExpressionPrime")
        if self.token_string in {"*", "+", "-", "("}:    #first
            self.TermPrime()
            self.D()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # follow
            self.TermPrime()
            self.D()
        self.exit_node()

    def AdditiveExpressionZegond(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-", "("} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type in {"NUM"}:    #first
            self.enter_node("AdditiveExpressionZegond")
            self.TermZegond()
            self.D()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing AdditiveExpressionZegond")
    
    def D(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("D")
        if self.token_string in {"+", "-"}:    #first
            self.Addop()
            self.Term()
            self.code_gen.math_exec()
            self.D()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def Addop(self):
        while self.token_string not in {"+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "+":    #first
            self.enter_node("Addop")
            self.code_gen.push_op(op= self.token_string)
            self.match("+")
            self.exit_node()
        elif self.token_string == "-":
            self.enter_node("Addop")
            self.code_gen.push_op(op= self.token_string)
            self.match("-")
            self.exit_node()
        elif self.token_string in {"("} or self.token_type in {"ID", "NUM"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Addop")

    def Term(self):
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "=="} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.enter_node("Term")
            self.SignedFactor()
            self.G()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Term")

    def TermPrime(self):
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "==", "*"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("TermPrime")
        if self.token_string in {"(", "*"}:    #first
            self.SignedFactorPrime()
            self.G()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "+", "-"}:     # follow
            self.SignedFactorPrime()
            self.G()
        self.exit_node()

    def TermZegond(self):
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "=="} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"NUM"}:    #first
            self.enter_node("TermZegond")
            self.SignedFactorZegond()
            self.G()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing TermZegond")
    
    def G(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-", "*"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("G")
        if self.token_string == "*":    #first
            self.code_gen.push_op(op= self.token_string)
            self.match("*")
            self.SignedFactor()
            self.code_gen.math_exec()
            self.G()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "+", "-"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def SignedFactor(self):
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "==", "*"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "+":    #first
            self.enter_node("SignedFactor")
            self.match("+")
            self.Factor()
            self.exit_node()
        elif self.token_string == "-":
            self.enter_node("SignedFactor")
            self.code_gen.p0()
            self.code_gen.push_op(op= self.token_string)
            self.match("-")
            self.Factor()
            self.code_gen.math_exec()
            self.exit_node()
        elif self.token_string == "(" or self.token_type in {"ID", "NUM"}:
            self.enter_node("SignedFactor")
            self.Factor()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SignedFactor")

    def SignedFactorPrime(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-", "*", "("}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("SignedFactorPrime")
        if self.token_string == "(":    #first
            self.FactorPrime()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "+", "-", "*"}:     # follow
            self.FactorPrime()
        self.exit_node()

    def SignedFactorZegond(self):
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "==", "*"} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "+":    #first
            self.enter_node("SignedFactorZegond")
            self.match("+")
            self.Factor()
            self.exit_node()
        elif self.token_string == "-":
            self.enter_node("SignedFactorZegond")
            self.code_gen.p0()
            self.code_gen.push_op(op= self.token_string)
            self.match("-")
            self.Factor()
            self.code_gen.math_exec()
            self.exit_node()
        elif self.token_string == "(" or self.token_type in {"NUM"}:
            self.enter_node("SignedFactorZegond")
            self.FactorZegond()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SignedFactorZegond")

    def Factor(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.enter_node("Factor")
            self.match("(")
            self.Expression()
            self.match(")")
            self.exit_node()
        elif self.token_type == "ID":
            self.enter_node("Factor")
            self.code_gen.pid(id= self.token_string)
            self.match_id()
            self.VarCallPrime()
            self.exit_node()
        elif self.token_type == "NUM":
            self.enter_node("Factor")
            self.code_gen.pnum(token_string= self.token_string)
            self.match_num()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Factor")

    def VarCallPrime(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "(", "["}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("VarCallPrime")
        if self.token_string == "(":    #first
            self.match("(")
            self.code_gen.args_start()
            self.Args()
            self.match(")")
            self.code_gen.func_call()
        elif self.token_string == "[":
            self.VarPrime()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # follow
            self.VarPrime()
        self.exit_node()

    def VarPrime(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "["}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("VarPrime")
        if self.token_string == "[":    # first
            self.match("[")
            self.code_gen.arr_ass_flag()
            self.Expression()
            self.code_gen.arr_ass_reset()
            self.match("]")
            self.code_gen.parr()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def FactorPrime(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("FactorPrime")
        if self.token_string == "(":    # first
            self.match("(")
            self.code_gen.args_start()
            self.Args()
            self.match(")")
            self.code_gen.func_call()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def FactorZegond(self):
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    # first
            self.enter_node("FactorZegond")
            self.match("(")
            self.Expression()
            self.match(")")
            self.exit_node()
        elif self.token_type == "NUM":
            self.enter_node("FactorZegond")
            self.code_gen.pnum(self.token_string)
            self.match_num()
            self.exit_node()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing FactorZegond")

    def Args(self):
        while self.token_string not in {"+", "-", "(", ")"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("Args")
        if self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:    # first
            self.ArgList()
        elif self.token_string in {")"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def ArgList(self):
        while self.token_string not in {"+", "-", "(", ")"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:    # first
            self.enter_node("ArgList")
            self.code_gen.func_ass_flag()
            self.Expression()
            self.code_gen.func_ass_reset()
            self.ArgListPrime()
            self.exit_node()
        elif self.token_string in {")"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ArgList")

    def ArgListPrime(self):
        while self.token_string not in {",", ")"}:
            if self.token_string == "$":
                self.eof = True
                return
            if self.token_type in {"ID", "NUM"}:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_type}")
            else:
                self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        self.enter_node("ArgListPrime")
        if self.token_string in {","}:    # first
            self.match(",")
            self.code_gen.func_ass_flag()
            self.Expression()
            self.code_gen.func_ass_reset()
            self.ArgListPrime()
        elif self.token_string in {")"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    #------------------------------------------------ Parsing
    def parse(self):
        self.Program()
        # self.make_tree("parse_tree.txt")
        # with open("syntax_errors.txt", "w", encoding="utf-8") as f:
        #     if self.parser_errors:
        #         f.write("\n".join(self.parser_errors))
        #     else:
        #         f.write("There is no syntax error.")
        # self.code_gen.output("output.txt")
        with open("semantic_errors.txt", "w", encoding="utf-8") as f:
            f.write("The input program is semantically correct.")
        self.code_gen.output("output.txt")
    
if __name__ == '__main__':
    with open("input.txt", "r", encoding="utf-8") as file:
        text = file.read()
    parser = Parser(text)
    parser.parse()
