# Omidreza Masoumi 401106522
# Kasra Azizadeh 401106222


# Scanner Functions
SYMBOLS = [";", ":", ",", "[", "]", "{", "}", "(", ")", "+", "-", "*", "/", "=", "<"]
KEYWORDS = ["if", "else", "void", "int", "while", "break", "return"]
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
              "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
              "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
WSPACE = [' ', '\n', '\r', '\t', '\v', '\f']
#INVALIDS = ['!', '"', '#', '$', '%', '&', "'", '.', '?', '@', '^', '_', '`', '|', '~']
symbol_table = ["if", "else", "void", "int", "while", "break", "return"]


def build_index_to_line_map(text):
    index_to_line = {}
    current_line = 1
    for i, char in enumerate(text):
        index_to_line[i] = current_line
        if char == '\n':
            current_line += 1
    index_to_line[len(text)] = current_line
    return index_to_line


def get_next_token(start, text):
    def get_number(start):
        number = ""
        error_msg = None
        stay = True
        while start < len(text) and stay:
            stay = False
            if text[start] in NUMBERS:
                number += text[start]
                start += 1
                stay = True
        
            elif text[start] in LETTERS or (text[start] not in LETTERS and text[start] not in NUMBERS and text[start] not in SYMBOLS and text[start] not in WSPACE):
                number += text[start]
                start += 1
                error_msg = "Invalid number"
        return start, "NUM", number, error_msg

    def get_identifier(start):
        identifier = ""
        error_msg = None
        stay = True
        while start < len(text) and stay:
            stay = False
            if text[start] in LETTERS or text[start] in NUMBERS:
                identifier += text[start]
                start += 1
                stay = True
            elif (text[start] not in LETTERS and text[start] not in NUMBERS and text[start] not in SYMBOLS and text[start] not in WSPACE):
                identifier += text[start]
                start += 1
                error_msg = "Invalid input"
        if identifier in KEYWORDS:
            return start, "KEYWORD", identifier, None
        else:
            if identifier not in symbol_table and error_msg is None:
                symbol_table.append(identifier)
            return start, "ID", identifier, error_msg

    def get_comment(start):
        comment = "/*"
        start += 2
        while start < len(text) and not (text[start] == '*' and start + 1 < len(text) and text[start + 1] == '/'):
            comment += text[start]
            start += 1
        if start + 1 >= len(text):
            return len(text), "ERROR", comment[0:7]+"...", "Unclosed comment"
        comment += "*/"
        return start + 2, "COMMENT", comment, None

    def get_symbol(start):
        symbol = text[start]
        start += 1
        if symbol == '=' and start < len(text) and text[start] == '=':
            return start + 1, "SYMBOL", "==", None
        if symbol == '=' and start < len(text) and (text[start] not in LETTERS and text[start] not in NUMBERS and text[start] not in SYMBOLS and text[start] not in WSPACE):
            symbol += text[start]
            start += 1
            return start, "ERROR", symbol, "Invalid input"
        if symbol == '/' and start < len(text) and (text[start] not in LETTERS and text[start] not in NUMBERS and text[start] not in SYMBOLS and text[start] not in WSPACE):
            symbol += text[start]
            start += 1
            return start, "ERROR", symbol, "Invalid input"
        if symbol == '*' and start < len(text) and text[start] == '/':
            return start + 1, "ERROR", "*/", "Unmatched comment"
        elif symbol == '*' and start < len(text) and (text[start] not in LETTERS and text[start] not in NUMBERS and text[start] not in SYMBOLS and text[start] not in WSPACE):
            symbol += text[start]
            start += 1
            return start, "ERROR", symbol, "Invalid input"
        else:
            return start, "SYMBOL", symbol, None

    # Skip whitespace
    while start < len(text) and text[start] in WSPACE:
        start += 1
    if start >= len(text):
        return start, "$", None, None

    #if text[start] in INVALIDS:
    #    return start + 1, "ERROR", text[start], "Invalid input"
    elif text[start] in NUMBERS:
        return get_number(start)
    elif text[start] in LETTERS:
        return get_identifier(start)
    elif text[start] == '/' and start + 1 < len(text) and text[start + 1] == '*':
        return get_comment(start)
    elif text[start] in SYMBOLS:
        return get_symbol(start)
    else:
        return start + 1, "ERROR", text[start], "Invalid input"


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
        self.index, self.token_type, self.token_string, _ = get_next_token(self.index, text)

        self.parser_errors = []
        self.root = None
        self.stack = []

    def update_token(self):
        while self.index < len(text) and text[self.index] in WSPACE:
            self.index += 1
        if self.index >= len(text):
            self.token_string = "$"
        else:
            self.token_string_start = self.index
            self.line_number = self.index_to_line[self.token_string_start]
            self.index, self.token_type, self.token_string, _ = get_next_token(self.index, text)
    
    def make_node(self, label):
        node = Node(label)
        self.stack[-1].children.append(node)
        return node

    def enter_node(self, label):
        node = self.make_node(label)
        self.stack.append(node)
        # print(node.label)

    def exit_node(self):
        out = self.stack.pop()
        print(out.label)

    def match(self, expected_string):
        if self.token_string == expected_string:
            self.make_node(f"({self.token_type}, {self.token_string}) ")
            self.update_token()
        else:
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing {expected_string}")
            print(f"#{self.line_number} : syntax error, missing {expected_string}")

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
        def _print_tree(node, prefix="", is_last=True, is_root=False):
            if is_root:
                line = node.label
            else:
                connector = "└── " if is_last else "├── "
                line = prefix + connector + node.label
            lines = [line]
            new_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(node.children):
                lines.extend(_print_tree(child, new_prefix, i == len(node.children) - 1))
            return lines

        # Print root label
        lines = [self.root.label]
        # Top-level children use '├── ' connector and no indent
        for child in self.root.children:
            lines.extend(_print_tree(child, "", False, is_root=False))
        # Append end-of-input marker
        lines.append("└── $\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    #------------------------------- Grammer DFAs
    
    def Program(self):
        self.root = Node("Program")
        self.stack.append(self.root)
        # print(self.token_string)
        while self.token_string not in {"int", "void", "$"}:
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.DeclarationList()
        elif self.token_string == {"$"}:            # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Program")
        self.stack.pop()
        
    def DeclarationList(self):
        self.enter_node("DeclarationList")
        while self.token_string not in {"int", "void", ";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.Declaration()
            self.DeclarationList()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  # follow
            self.make_node("epsilon")
        self.exit_node()

    def Declaration(self):
        self.enter_node("Declaration")
        while self.token_string not in {"int", "void", ";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.DeclarationInitial()
            self.DeclarationPrime()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Declaration")
        self.exit_node()

    def DeclarationInitial(self):
        self.enter_node("DeclarationInitial")
        while self.token_string not in {"int", "void", ";", "[", "(", ")", ","}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.TypeSpecifier()
            self.match_id()
        elif self.token_string in {";", "[", "(", ")", ","}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing DeclarationInitial")
        self.exit_node()

    def DeclarationPrime(self):
        self.enter_node("DeclarationPrime")
        while self.token_string not in {"[", ";", "(", "{", "}", "break", "if", "while", "int", "void", "return", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.FunDeclarationPrime()
        elif self.token_string in {"[", ";"}:
            self.VarDeclarationPrime()
        elif self.token_string in {"{", "}", "break", "if", "while", "return", "void", "int", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing DeclarationPrime")
        self.exit_node()

    def VarDeclarationPrime(self):
        self.enter_node("VarDeclarationPrime")
        while self.token_string not in {"[", ";", "(", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "[":    #first
            self.match("[")
            self.match_num()
            self.match("]")
            self.match(";")
        elif self.token_string == ";":
            self.match(";")
        elif self.token_string in {"(", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing VarDeclarationPrime")
        self.exit_node()

    def FunDeclarationPrime(self):
        self.enter_node("FunDeclarationPrime")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.match("(")
            self.Params()
            self.match(")")
            self.CompoundStmt()
        elif self.token_string in {";", "{", "}", "break", "if", "while", "return", "int", "void", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing FunDeclarationPrime")
        self.exit_node()

    def TypeSpecifier(self):
        self.enter_node("TypeSpecifier")
        while self.token_string not in {"int", "void"} and self.token_type not in {"ID"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "int":    # first
            self.match("int")
        elif self.token_string == "void":    # first
            self.match("void")
        elif self.token_type == "ID":   # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing TypeSpecifier")
        self.exit_node()

    def Params(self):
        self.enter_node("Params")
        while self.token_string not in {"int", "void", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "int":    # first
            self.match("int")
            self.match_id()
            self.ParamPrime()
            self.ParamList()
        elif self.token_string == "void":    # first
            self.match("void")
        elif self.token_type == ")":   # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Params")
        self.exit_node()

    def ParamList(self):
        self.enter_node("ParamList")
        while self.token_string not in {",", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {","}:    # first
            self.match(",")
            self.Param()
            self.ParamList()
        elif self.token_string in {")"}:  # follow
            self.make_node("epsilon")
        self.exit_node()

    def Param(self):
        self.enter_node("Param")
        while self.token_string not in {"int", "void", ",", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"int", "void"}:    # first
            self.DeclarationInitial()
            self.ParamPrime()
        elif self.token_type in {",", ")"}:   # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Param")
        self.exit_node()

    def ParamPrime(self):
        self.enter_node("ParamPrime")
        while self.token_string not in {"[", ",", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "[":    # first
            self.match("[")
            self.match("]")
        elif self.token_string in {",", ")"}:  # follow
            self.make_node("epsilon")
        self.exit_node()
    
    def CompoundStmt(self):
        self.enter_node("CompoundStmt")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "int", "void", "else", "+", "-", "$"} and self.token_type not in {"ID", "NUM"}:
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "{":    #first
            self.match("{")
            self.DeclarationList()
            self.StatementList()
            self.match("}")
        elif self.token_string in {";", "}", "break", "if", "while", "return", "int", "void", "else", "+", "-", "$"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing CompoundStmt")
        self.exit_node()

    def StatementList(self):
        self.enter_node("StatementList")
        while self.token_string not in {"{", "}", ";", "break", "if", "while", "return", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"{", ";", "break", "if", "while", "return", "+", "-", "("} or self.token_type in {"ID", "NUM"}:    # first
            self.Statement()
            self.StatementList()
        elif self.token_string in {"}"}:  # follow
            self.make_node("epsilon")
        self.exit_node()

    def Statement(self):
        self.enter_node("Statement")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {";", "(", "break", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.ExpressionStmt()
        elif self.token_string == "{":
            self.CompoundStmt()
        elif self.token_string == "if":
            self.SelectionStmt()
        elif self.token_string == "while":
            self.IterationStmt()
        elif self.token_string == "return":
            self.ReturnStmt()
        elif self.token_string in {"}", "else"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Statement")
        self.exit_node()

    def ExpressionStmt(self):
        self.enter_node("ExpressionStmt")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.Expression()
            self.match(";")
        elif self.token_string == "break":
            self.match("break")
            self.match(";")
        elif self.token_string == ";":
            self.match(";")
        elif self.token_string in {"{", "}", "if", "while", "return", "else"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ExpressionStmt")
        self.exit_node()
    
    def SelectionStmt(self):
        self.enter_node("SelectionStmt")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "if":
            self.match("if")
            self.match("(")
            self.Expression()
            self.match(")")
            self.Statement()
            self.match("else")
            self.Statement()
        elif self.token_string in {";", "(", "{", "}", "break", "while", "return", "else", "+", "-"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SelectionStmt")
        self.exit_node()

    def IterationStmt(self):
        self.enter_node("IterationStmt")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "while":
            self.match("while")
            self.match("(")
            self.Expression()
            self.match(")")
            self.Statement()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "return", "else", "+", "-"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing IterationStmt")
        self.exit_node()

    def ReturnStmt(self):
        self.enter_node("ReturnStmt")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "return":
            self.match("return")
            self.ReturnStmtPrime()
        elif self.token_string in {";", "(", "{", "}", "break", "if", "while", "else", "+", "-"} or self.token_type in {"ID", "NUM"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ReturnStmt")
        self.exit_node()


    def ReturnStmtPrime(self):
        self.enter_node("ReturnStmtPrime")
        while self.token_string not in {";", "(", "{", "}", "break", "if", "while", "return", "else", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.Expression()
            self.match(";")
        elif self.token_string == ";":
            self.match(";")
        elif self.token_string in {"{", "}", "if", "while", "return", "else", "break"}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ReturnStmtPrime")
        self.exit_node()
    
    def Expression(self):
        self.enter_node("Expression")
        while self.token_string not in {"(",")", ";", "]", ",", "+", "-"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"NUM"}:    #first
            self.SimpleExpressionZegond()
        elif self.token_type == "ID":
            self.match_id()
            self.B()
        elif self.token_string in {")", ";", "]", ","}:  #synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Expression")
        self.exit_node()

    def B(self):
        self.enter_node("B")
        while self.token_string not in {"(", "*", "+", "-", "<", "==", "[", "=", ";", ",", "]", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "*", "+", "-", "<", "=="}:    #first
            self.SimpleExpressionPrime()
        elif self.token_string == "[":
            self.match("[")
            self.Expression()
            self.match("]")
            self.H()
        elif self.token_string == "=":
            self.match("=")
            self.Expression()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.SimpleExpressionPrime()
        self.exit_node()
    
    def H(self):
        self.enter_node("H")
        while self.token_string not in {"*", "+", "-", "<", "==", "=", ";", ",", "]", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"*", "+", "-", "<", "=="}:    #first
            self.G()
            self.D()
            self.C()
        elif self.token_string == "=":
            self.match("=")
            self.Expression()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.G()
            self.D()
            self.C()
        self.exit_node()
    
    def SimpleExpressionZegond(self):
        self.enter_node("SimpleExpressionZegond")
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")"} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type == "NUM":    #first
            self.AdditiveExpressionZegond()
            self.C()
        elif self.token_string in {";", ",", "]", ")"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SimpleExpressionZegond")
        self.exit_node()

    def SimpleExpressionPrime(self):
        self.enter_node("SimpleExpressionPrime")
        while self.token_string not in {"(", "*", "+", "-", "<", "==", ";", ",", "]", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "*", "+", "-", "<", "=="}:    #first
            self.AdditiveExpressionPrime()
            self.C()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.AdditiveExpressionPrime()
            self.C()
        self.exit_node()

    def C(self):
        self.enter_node("C")
        while self.token_string not in {"<", "==", ";", ",", "]", ")"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"<", "=="}:    #first
            self.Relop()
            self.AdditiveExpression()
        elif self.token_string in {";", ",", "]", ")"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def Relop(self):
        self.enter_node("Relop")
        while self.token_string not in {"<", "==", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "<":    #first
            self.match("<")
        elif self.token_string == "==":
            self.match("==")
        elif self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Relop")
        self.exit_node()

    def AdditiveExpression(self):
        self.enter_node("AdditiveExpression")
        while self.token_string not in {";", ",", "]", ")", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:    #first
            self.Term()
            self.D()
        elif self.token_string in {";", ",", "]", ")"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing AdditiveExpression")
        self.exit_node()

    def AdditiveExpressionPrime(self):
        self.enter_node("AdditiveExpressionPrime")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"*", "+", "-", "("}:    #first
            self.TermPrime()
            self.D()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # follow
            self.TermPrime()
            self.D()
        self.exit_node()

    def AdditiveExpressionZegond(self):
        self.enter_node("AdditiveExpressionZegond")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-", "("} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type in {"NUM"}:    #first
            self.TermZegond()
            self.D()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing AdditiveExpressionZegond")
        self.exit_node()
    
    def D(self):
        self.enter_node("D")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-"}:    #first
            self.Addop()
            self.Term()
            self.D()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def Addop(self):
        self.enter_node("Addop")
        while self.token_string not in {"+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "+":    #first
            self.match("+")
        elif self.token_string == "-":
            self.match("-")
        elif self.token_string in {"("} or self.token_type in {"ID", "NUM"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Addop")
        self.exit_node()

    def Term(self):
        self.enter_node("Term")
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "=="} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"ID", "NUM"}:    #first
            self.SignedFactor()
            self.G()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Term")
        self.exit_node()

    def TermPrime(self):
        self.enter_node("TermPrime")
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "==", "*"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "*"}:    #first
            self.SignedFactorPrime()
            self.G()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "+", "-"}:     # follow
            self.SignedFactorPrime()
            self.G()
        self.exit_node()

    def TermZegond(self):
        self.enter_node("TermZegond")
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "=="} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"(", "+", "-"} or self.token_type in {"NUM"}:    #first
            self.SignedFactorZegond()
            self.G()
        elif self.token_string in {";", ",", "]", ")", "<", "=="}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing TermZegond")
        self.exit_node()
    
    def G(self):
        self.enter_node("G")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-", "*"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "*":    #first
            self.match("*")
            self.SignedFactor()
            self.G()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "+", "-"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def SignedFactor(self):
        self.enter_node("SignedFactor")
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "==", "*"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "+":    #first
            self.match("+")
            self.Factor()
        elif self.token_string == "-":
            self.match("-")
            self.Factor()
        elif self.token_string == "(" or self.token_type in {"ID", "NUM"}:
            self.Factor()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SignedFactor")
        self.exit_node()

    def SignedFactorPrime(self):
        self.enter_node("SignedFactorPrime")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "+", "-", "*", "("}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.FactorPrime()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "+", "-", "*"}:     # follow
            self.FactorPrime()
        self.exit_node()

    def SignedFactorZegond(self):
        self.enter_node("SignedFactorZegond")
        while self.token_string not in {"+", "-", "(", ";", ",", "]", ")", "<", "==", "*"} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "+":    #first
            self.match("+")
            self.Factor()
        elif self.token_string == "-":
            self.match("-")
            self.Factor()
        elif self.token_string == "(" or self.token_type in {"NUM"}:
            self.FactorZegond()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing SignedFactorZegond")
        self.exit_node()

    def Factor(self):
        self.enter_node("Factor")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.match("(")
            self.Expression()
            self.match(")")
        elif self.token_type == "ID":
            self.match_id()
            self.VarCallPrime()
        elif self.token_type == "NUM":
            self.match_num()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing Factor")
        self.exit_node()

    def VarCallPrime(self):
        self.enter_node("VarCallPrime")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "(", "["}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    #first
            self.match("(")
            self.Args()
            self.match(")")
        elif self.token_string == "[":
            self.VarPrime()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # follow
            self.VarPrime()
        self.exit_node()

    def VarPrime(self):
        self.enter_node("VarPrime")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "["}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "[":    # first
            self.match("[")
            self.Expression()
            self.match("]")
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def FactorPrime(self):
        self.enter_node("FactorPrime")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    # first
            self.match("(")
            self.Args()
            self.match(")")
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def FactorZegond(self):
        self.enter_node("FactorZegond")
        while self.token_string not in {";", ",", "]", ")", "<", "==", "*", "+", "-", "("} and self.token_type not in {"NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string == "(":    # first
            self.match("(")
            self.Expression()
            self.match(")")
        elif self.token_type == "NUM":
            self.match_num()
        elif self.token_string in {";", ",", "]", ")", "<", "==", "*", "+", "-"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing FactorZegond")
        self.exit_node()

    def Args(self):
        self.enter_node("Args")
        while self.token_string not in {"+", "-", "(", ")"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:    # first
            self.ArgList()
        elif self.token_string in {")"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    def ArgList(self):
        self.enter_node("ArgList")
        while self.token_string not in {"+", "-", "(", ")"} and self.token_type not in {"ID", "NUM"}:
            if self.token_string == "$":
                return
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {"+", "-", "("} or self.token_type in {"ID", "NUM"}:    # first
            self.Expression()
            self.ArgListPrime()
        elif self.token_string in {")"}:     # synch
            self.parser_errors.append(f"#{self.line_number} : syntax error, missing ArgList")
        self.exit_node()

    def ArgListPrime(self):
        self.enter_node("ArgListPrime")
        while self.token_string not in {",", ")"}:
            if self.token_string == "$":
                return
            print(self.token_string)
            self.parser_errors.append(f"#{self.line_number} : syntax error, illegal {self.token_string}")
            self.update_token()
        if self.token_string in {","}:    # first
            self.match(",")
            self.Expression()
            self.ArgListPrime()
        elif self.token_string in {")"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    #------------------------------------------------ Parsing
    def parse(self):
        self.Program()
        if self.token_string != "$":
            self.parser_errors.append(f"Syntax Error: Unexpected token '{self.token_string}' after program end at line {self.line_number}")
        self.make_tree("parse_tree.txt")
        with open("syntax_errors.txt", "w", encoding="utf-8") as f:
            if self.parser_errors:
                f.write("\n".join(self.parser_errors))
            else:
                f.write("There is no syntax error.")


if __name__ == '__main__':
    with open("input.txt", "r", encoding="utf-8") as file:
        text = file.read()
    parser = Parser(text)
    parser.parse()
