# Omidreza Masoumi 401106522
# Kasra Azizadeh 401106222

SYMBOLS = [";", ":", ",", "[", "]", "{", "}", "(", ")", "+", "-", "*", "/", "=", "<"]
KEYWORDS = ["if", "else", "void", "int", "while", "break", "return"]
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
              "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
              "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
WSPACE = [' ', '\n', '\r', '\t', '\v', '\f']
INVALIDS = ['!', '"', '#', '$', '%', '&', "'", '.', '?', '@', '^', '_', '`', '|', '~']


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
        
            elif text[start] in LETTERS or text[start] in INVALIDS:
                number += text[start]
                start += 1
                error_msg = "Invalid number"
        return start, "NUMBER", number, error_msg

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
            elif text[start] in INVALIDS:
                identifier += text[start]
                start += 1
                error_msg = "Invalid input"
        if identifier in KEYWORDS:
            return start, "KEYWORD", identifier, None
        else:
            return start, "IDENTIFIER", identifier, error_msg

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
        if symbol == '*' and start < len(text) and text[start] == '/':
            return start + 1, "ERROR", "*/", "Unmatched comment"
        elif symbol == '*' and start < len(text) and text[start] in INVALIDS:
            symbol += text[start]
            start += 1
            return start, "ERROR", symbol, "Invalid input"
        else:
            return start, "SYMBOL", symbol, None

    # Skip whitespace
    while start < len(text) and text[start] in WSPACE:
        start += 1
    if start >= len(text):
        return start, "EOF", None, None

    if text[start] in INVALIDS:
        return start + 1, "ERROR", text[start], "Invalid input"
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


def scan(text):
    tokens = []
    errors = []
    index_to_line = build_index_to_line_map(text)

    index = 0
    while index < len(text):
        while index < len(text) and text[index] in WSPACE:
            index += 1
        if index >= len(text):
            break
        token_start = index
        index, token_type, token_string, error_msg = get_next_token(index, text)
        line_no = index_to_line[token_start]

        if error_msg is None:
            tokens.append((line_no, token_type, token_string))
        else:
            errors.append((line_no, token_string, error_msg))
    return tokens, errors


if __name__ == '__main__':
    with open("D:/Books/University/6th Semester (Winter 03- Spring 04)/Compiler Design/Assignments/Project/Phase 1/Code/input.txt", "r") as file:
        text = file.read()
    tokens, errors = scan(text)
    
    tokens_by_line = {}
    errors_by_line = {}
    for line_no, token_type, token_string in tokens:
        tokens_by_line.setdefault(line_no, []).append((token_type, token_string))

    for line_no, token_string, error_msg in errors:
        errors_by_line.setdefault(line_no, []).append((token_string, error_msg))

    print("tokens:")
    for line_no in sorted(tokens_by_line.keys()):
        line_tokens = tokens_by_line[line_no]
        token_str = " ".join(f"({typ}, {val})" for typ, val in line_tokens)
        print(f"{line_no}.\t{token_str}")

    print("\nerrors:")
    if errors_by_line:
        for line_no in sorted(errors_by_line.keys()):
            line_errors = errors_by_line[line_no]
            error_str = " ".join(f"({val}, {msg})" for val, msg in line_errors)
            print(f"{line_no}.\t{error_str}")
    else:
        print("There is no lexical error")
