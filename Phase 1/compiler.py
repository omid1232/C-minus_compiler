# Omidreza Masoumi 401106522
# Kasra Azizadeh 401106222

SYMBOLS = [";", ":", ",", "[", "]", "{", "}", "(", ")", "+", "-", "*", "/", "=", "<", "=="]
KEYWORDS = ["if", "else", "void", "int", "while", "break", "return"]
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
              "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
              "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

def get_next_token(start, line):
    def get_number(start, line):
        number = ""
        while start < len(line) and line[start] in NUMBERS:
            number += line[start]
            start += 1
        return start, "NUMBER", number
    
    def get_identifier(start, line):
        identifier = ""
        while start < len(line) and (line[start] in LETTERS or line[start] in NUMBERS):
            identifier += line[start]
            start += 1
        if identifier in KEYWORDS:
            return start, "KEYWORD", identifier
        else:
            return start, "IDENTIFIER", identifier
    
    def get_comment(start, line):
        comment = ""
        start += 2
        while start < len(line) and not (line[start] == "*" and start + 1 < len(line) and line[start + 1] == "/"):
            comment += line[start]
            start += 1
        if start < len(line):
            start += 2
        return start, "COMMENT", comment
    
    def get_symbol(start, line):
        symbol = line[start]
        start += 1
        if symbol == '=' and start < len(line) and line[start] == '=':
            return start + 1, "EQUAL", "=="
        else:
            return start, "SYMBOL", symbol
    
    while start < len(line) and line[start] == ' ':
        start += 1
    if start >= len(line):
        return start, "EOF", None
    if line[start] in NUMBERS:
        return get_number(start, line)
    elif line[start] in LETTERS:
        return get_identifier(start, line)
    elif line[start] == '/' and start + 1 < len(line) and line[start + 1] == '*':
        return get_comment(start, line)
    elif line[start] in SYMBOLS:
        return get_symbol(start, line)


def scan(content):
    tokens = []
    for line in content:
        line = line.strip()
        line_tokens = []
        index = 0
        while index < len(line):
            index, type, token_string = get_next_token(index, line)
            if type != "EOF":
                line_tokens.append((type, token_string))
        if len(line_tokens) != 0:
            tokens.append(line_tokens)
    return tokens


if __name__ == '__main__':
    with open("input.txt", "r") as file:
        content = file.read().split('\n')
    tokens = scan(content)
    for token in tokens:
        print(token)