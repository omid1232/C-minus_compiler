# Omidreza Masoumi 401106522
# Kasra Azizadeh 401106222

SYMBOLS = [";", ":", ",", "[", "]", "{", "}", "(", ")", "+", "-", "*", "/", "=", "<", "=="]
KEYWORDS = ["if", "else", "void", "int", "while", "break", "return"]
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
              "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
              "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
INVALIDS = ['!', '"', '#', '$', '%', '&', "'", '.', '?', '@', '^', '_', '`', '|', '~',]

def get_next_token(start, line):
    def get_number(start, line):
        number = ""
        error_msg = None
        stay = True
        while start < len(line) and stay:
            stay = False
            if line[start] in NUMBERS:
                number += line[start]
                start += 1
                stay = True
            elif line[start] in LETTERS or line[start] in INVALIDS:
                number += line[start]
                start += 1
                error_msg = "Invalid number"
        return start, "NUMBER", number, error_msg
    
    def get_identifier(start, line):
        identifier = ""
        error_msg = None
        stay = True
        while start < len(line) and stay:
            stay = False
            if line[start] in LETTERS or line[start] in NUMBERS:
                identifier += line[start]
                start += 1
                stay = True
            elif line[start] in INVALIDS:
                identifier += line[start]
                start += 1
                error_msg = "Invalid input"
        if identifier in KEYWORDS:
            return start, "KEYWORD", identifier, None
        else:
            return start, "IDENTIFIER", identifier, error_msg
    
    def get_comment(start, line):
        comment = ""
        start += 2
        while start < len(line) and not (line[start] == "*" and start + 1 < len(line) and line[start + 1] == "/"):
            comment += line[start]
            start += 1
        if start < len(line):
            start += 2
        return start, "COMMENT", comment, None
    
    def get_symbol(start, line):
        symbol = line[start]
        start += 1
        if symbol == '=' and start < len(line) and line[start] == '=':
            return start + 1, "EQUAL", "==", None
        if symbol == '*' and start < len(line) and line[start] == '/':
            return start + 1, "ERROR", "*/", "Unclosed comment"
        elif symbol == '*' and start < len(line) and line[start] in INVALIDS:
            symbol += line[start]
            start += 1
            return start, "ERROR", symbol, "Invalid input"
        else:
            return start, "SYMBOL", symbol, None
    
    while start < len(line) and (line[start] == ' ' or line[start] == '\t'):
        start += 1
    if start >= len(line):
        return start, "EOF", None
    if line[start] in INVALIDS:
        return start + 1, "ERROR", line[start], "Invalid Input"
    if line[start] in NUMBERS:
        return get_number(start, line)
    elif line[start] in LETTERS:
        return get_identifier(start, line)
    elif line[start] == '/' and start + 1 < len(line) and line[start + 1] == '*':
        return get_comment(start, line)
    elif line[start] in SYMBOLS:
        return get_symbol(start, line)
    else:
        return start + 1, "ERROR", line[start], "Invalid input"


def scan(content):
    tokens = []
    errors = []
    for line in content:
        line = line.strip()
        line_tokens = []
        line_errors = []
        index = 0
        while index < len(line):
            index, type, token_string, error_msg = get_next_token(index, line)
            if type != "EOF":
                if error_msg is None:
                    line_tokens.append((type, token_string))
                else:
                    line_errors.append((token_string, error_msg))
        if len(line_tokens) != 0:
            tokens.append(line_tokens)
        if len(line_errors):
            errors.append(line_errors)
    return tokens, errors


if __name__ == '__main__':
    with open("D:/Books/University/6th Semester (Winter 03- Spring 04)/Compiler Design/Assignments/Project/Phase 1/Code/input.txt", "r") as file:
        content = file.read().split('\n')
    tokens, errors = scan(content)
    print("tokens:")
    for token in tokens:
        print(token)
    print("errors:")
    if len(errors) > 0:
        for error in errors:
            print(error)
    else:
        print("There is no lexical error")
