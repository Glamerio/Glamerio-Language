import re

# A simple lexer for a hypothetical programming language
# This lexer tokenizes a small set of keywords, identifiers, numbers, strings, and operators.

TOKENS = [
    # Keywords
    ('KEYWORD', r'\b(fn|if|else|elseif|for|while|class|return|input|print|this|static|private|public|constructor|new|try|catch|in)\b'),

    # Logical operators as keywords (and/or)
    ('LOGIC', r'\b(and|or)\b'),

    # Data types
    ('TYPE', r'\b(int|float|str|bool|array|void)\b'),

    # Boolean & null values
    ('BOOL', r'\b(True|False)\b'),
    ('NULL', r'\bnull\b'),

    # Identifiers (variables, function names, etc.)
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),

    # Numbers (integers and floats)
    ('NUMBER', r'\d+(\.\d+)?'),

    # Strings
    ('STRING', r'"[^"\n]*"'),

    # Symbols
    ('SEMI', r';'),
    ('COMMA', r','),
    ('DOT', r'\.'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    
    # Operators (add && and ||)
    ('OP', r'\^|==|!=|<=|>=|=|<|>|\+|\-|\*|\/|&&|\|\|'),


    # Whitespace and comments (ignored)
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    # Single-line comment: // ...
    ('COMMENT_SLASH', r'//.*'),
    # Hash comment: # ...
    ('COMMENT_HASH', r'\#.*'),
    # Multi-line comment: /* ... */
    ('COMMENT_BLOCK', r'/\*[\s\S]*?\*/')
]


# Yorumları (// ve #) satırın herhangi bir yerinde algılamak için kodu ön işle
def remove_comments(code):
    import re
    # Remove /* ... */
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    # Remove // ... (from // to end of line)
    code = re.sub(r'//.*', '', code)
    # Remove # ... (from # to end of line)
    code = re.sub(r'#.*', '', code)
    return code

TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKENS))

# Lexer function
def lexer(code):
    tokens = []
    code = remove_comments(code)
    line_starts = [0]
    for i, c in enumerate(code):
        if c == '\n':
            line_starts.append(i + 1)
    for match in TOKEN_RE.finditer(code):
        kind = match.lastgroup
        value = match.group()
        start = match.start()
        # Satır numarasını bul
        line = 1
        for i, ls in enumerate(line_starts):
            if start < ls:
                break
            line = i + 1

        # Skip whitespace, newlines, and comments
        if kind in ('NEWLINE', 'SKIP', 'COMMENT_SLASH', 'COMMENT_HASH', 'COMMENT_BLOCK'):
            continue

        # Remove quotes from strings
        if kind == 'STRING':
            value = value[1:-1]

        tokens.append((kind, value, line))

    return tokens

# Example usage: run with test file
if __name__ == "__main__":
    try:
        with open('program.gl', 'r', encoding='utf-8') as f:
            code = f.read()
        token_list = lexer(code)
        for token in token_list:
            print(token)
    except FileNotFoundError:
        print("Error: 'program.gl' file not found.")