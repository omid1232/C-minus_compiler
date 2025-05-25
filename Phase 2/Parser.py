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
        self.index, self.token_type, self.token_string, self.scanner_error_msg = get_next_token(self.index, text)

        self.parser_errors = []
        self.root = None
        self.stack = []
        self.eof = False

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
            self.TypeSpecifier()
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
            self.match_num()
            self.match("]")
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
            self.match("(")
            self.Params()
            self.match(")")
            self.CompoundStmt()
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
            self.match("int")
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
            self.Statement()
            self.match("else")
            self.Statement()
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
            self.match("(")
            self.Expression()
            self.match(")")
            self.Statement()
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
            self.Expression()
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
            self.Expression()
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
            self.match("<")
            self.exit_node()
        elif self.token_string == "==":
            self.enter_node("Relop")
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
            self.match("+")
            self.exit_node()
        elif self.token_string == "-":
            self.enter_node("Addop")
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
            self.match("*")
            self.SignedFactor()
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
            self.match("-")
            self.Factor()
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
            self.match("-")
            self.Factor()
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
            self.match_id()
            self.VarCallPrime()
            self.exit_node()
        elif self.token_type == "NUM":
            self.enter_node("Factor")
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
            self.Args()
            self.match(")")
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
            self.Expression()
            self.match("]")
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
            self.Args()
            self.match(")")
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
            self.Expression()
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
            self.Expression()
            self.ArgListPrime()
        elif self.token_string in {")"}:     # follow
            self.make_node("epsilon")
        self.exit_node()

    #------------------------------------------------ Parsing
    def parse(self):
        self.Program()
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
