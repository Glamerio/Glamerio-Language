class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, expected_type=None):
        token = self.peek()
        if token is None:
            raise Exception("Unexpected end of input")
        if expected_type and token[0] != expected_type:
            raise Exception(f"Expected token type {expected_type}, but got {token[0]}")
        self.position += 1
        return token


# AST Node
class VarDeclarationNode:
    def __init__(self, var_type, name, value):
        self.var_type = var_type
        self.name = name
        self.value = value

class PrintNode:
    def __init__(self, value):
        self.value = value

class LiteralNode:
    def __init__(self, value):
        self.value = value

class IdentifierNode:
    def __init__(self, name):
        self.name = name        

class BinaryOpNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class NumberNode:
    def __init__(self, value):
        self.value = float(value) if '.' in value else int(value)

class StringNode:
    def __init__(self, value):
        self.value = value

# Parser

def parse_expression(stream):
    token = stream.consume()
    if token[0] == 'NUMBER':
        left = LiteralNode(token[1])
    elif token[0] == 'STRING':
        left = StringNode(token[1])
    elif token[0] == 'ID':
        left = IdentifierNode(token[1])
    else:
        raise Exception(f"Invalid expression start: {token}")
    
    while stream.peek() and stream.peek()[0] in ('OP'):
        op = stream.consume()[1]  # Consume the operator token
        right_token = stream.consume()
        if right_token[0] == 'NUMBER':
            right = LiteralNode(right_token[1])
        elif right_token[0] == 'ID':
            right = IdentifierNode(right_token[1])
        else:
            raise Exception(f"Expected a literal or identifier after operator")
        
        left = BinaryOpNode(left, op, right)  # Create a binary operation node
        
    return left
        
def parse_variable_declaration(stream):
    var_type = stream.consume('TYPE')[1]
    var_name = stream.consume('ID')[1]
    stream.consume('OP')  # '='
    value = parse_expression(stream)
    stream.consume('SEMI')
    return VarDeclarationNode(var_type, var_name, value)

def parse_print_statement(stream):
    stream.consume('KEYWORD')  # 'print'
    stream.consume('LPAREN')
    value = parse_expression(stream)
    stream.consume('RPAREN')
    stream.consume('SEMI')
    return PrintNode(value)

# Test
tokens = [
    ('TYPE', 'int'), ('ID', 'x'), ('OP', '='), ('NUMBER', '5'), ('OP', '+'), ('NUMBER', '2'), ('SEMI', ';'),
    ('KEYWORD', 'print'), ('LPAREN', '('), ('ID', 'x'), ('OP', '*'), ('NUMBER', '3'), ('RPAREN', ')'), ('SEMI', ';')
]

stream = TokenStream(tokens)

ast1 = parse_variable_declaration(stream)
ast2 = parse_print_statement(stream)


def print_ast(node):
    if isinstance(node, LiteralNode):
        return node.value
    elif isinstance(node, IdentifierNode):
        return node.name
    elif isinstance(node, BinaryOpNode):
        return f"({print_ast(node.left)} {node.operator} {print_ast(node.right)})"
    elif isinstance(node, VarDeclarationNode):
        return f"{node.var_type} {node.name} = {print_ast(node.value)};"
    elif isinstance(node, PrintNode):
        return f"print({print_ast(node.value)});"
    elif isinstance(node, StringNode):
        return f'"{node.value}"'
    else:
        return str(node)

print(f"{ast1.var_type} {ast1.name} = {print_ast(ast1.value)};")
print(f"print({print_ast(ast2.value)});")