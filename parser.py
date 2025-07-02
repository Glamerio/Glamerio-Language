from glam_ast import *

# TryCatchNode for error handling


# Try-catch statement parser
def parse_try_catch_statement(stream):
    stream.consume('KEYWORD')  # 'try'
    try_block = parse_block(stream)
    catch_var = None
    catch_block = None
    if stream.peek() and stream.peek()[0] == 'KEYWORD' and stream.peek()[1] == 'catch':
        stream.consume('KEYWORD')  # 'catch'
        # Optional: catch (err)
        if stream.peek() and stream.peek()[0] == 'LPAREN':
            stream.consume('LPAREN')
            if stream.peek()[0] == 'ID':
                catch_var = stream.consume('ID')[1]
            stream.consume('RPAREN')
        catch_block = parse_block(stream)
    else:
        raise Exception('try bloğundan sonra catch bloğu bekleniyor!')
    return TryCatchNode(try_block, catch_var, catch_block)
# ----------------------
# Class Instance Creation (new keyword)
# ----------------------


# ----------------------
# List and Class AST Nodes
# ----------------------



from lexer import lexer  # Import lexer function

# ----------------------
# Token Stream Class
# ----------------------
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


# ----------------------
# AST Node Definitions
# ----------------------


# For-each node
def parse_for_each_statement(stream):
    stream.consume('KEYWORD')  # 'for'
    stream.consume('LPAREN')
    if stream.peek()[0] == 'TYPE':
        var_type = stream.consume('TYPE')[1]
        var_name = stream.consume('ID')[1]
    else:
        var_type = None
        var_name = stream.consume('ID')[1]
    stream.consume('KEYWORD')  # 'in'
    iterable = parse_expression(stream)
    stream.consume('RPAREN')
    # Inline for-each desteği
    if stream.peek() and stream.peek()[0] == 'LBRACE':
        body = parse_block(stream)
    else:
        # Tek satırlık statement (ör: print(...); veya atama)
        stmt = None
        token = stream.peek()
        if token[0] == 'KEYWORD' and token[1] == 'print':
            stmt = parse_print_statement(stream)
        elif token[0] == 'KEYWORD' and token[1] == 'input':
            stmt = parse_input_expression(stream)
        elif token[0] == 'ID' or (token[0] == 'KEYWORD' and token[1] == 'this'):
            expr = parse_expression(stream)
            if stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] == '=':
                stream.consume('OP')
                value = parse_expression(stream)
                stream.consume('SEMI')
                stmt = BinaryOpNode(expr, '=', value)
            elif stream.peek() and stream.peek()[0] == 'SEMI':
                stream.consume('SEMI')
                stmt = expr
            else:
                raise Exception(f"Unexpected token after inline for-each: {stream.peek()}")
        else:
            raise Exception(f"Unsupported inline for-each statement: {token}")
        body = BlockNode([stmt])
    return ForEachNode(var_type, var_name, iterable, body)

# ----------------------
# Expression Parsers (with precedence)
# ----------------------



# Logical OR precedence: or, ||
def parse_logical_or(stream):
    left = parse_logical_and(stream)
    while stream.peek() and (
        (stream.peek()[0] == 'LOGIC' and stream.peek()[1] == 'or') or
        (stream.peek()[0] == 'OP' and stream.peek()[1] == '||')
    ):
        if stream.peek()[0] == 'LOGIC':
            op = stream.consume()[1]
        else:
            op = stream.consume()[1]
        right = parse_logical_and(stream)
        left = BinaryOpNode(left, op, right)
    return left

# Logical AND precedence: and, &&
def parse_logical_and(stream):
    left = parse_comparison(stream)
    while stream.peek() and (
        (stream.peek()[0] == 'LOGIC' and stream.peek()[1] == 'and') or
        (stream.peek()[0] == 'OP' and stream.peek()[1] == '&&')
    ):
        if stream.peek()[0] == 'LOGIC':
            op = stream.consume()[1]
        else:
            op = stream.consume()[1]
        right = parse_comparison(stream)
        left = BinaryOpNode(left, op, right)
    return left

# Comparison precedence: <, >, <=, >=, ==, !=
def parse_comparison(stream):
    left = parse_additive(stream)
    while stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] in ('<', '>', '<=', '>=', '==', '!='):
        op = stream.consume()[1]
        right = parse_additive(stream)
        left = BinaryOpNode(left, op, right)
    return left

# Additive precedence: + -
def parse_additive(stream):
    left = parse_term(stream)
    while stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] in ('+', '-'):
        op = stream.consume()[1]
        right = parse_term(stream)
        left = BinaryOpNode(left, op, right)
    return left

# parse_expression now starts with logical or
def parse_expression(stream):
    return parse_logical_or(stream)

# Medium precedence: * /
def parse_term(stream):
    left = parse_power(stream)
    while stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] in ('*', '/'):
        op = stream.consume()[1]
        right = parse_power(stream)
        left = BinaryOpNode(left, op, right)
    return left

# High precedence: ^
# RIGHT-associative: a ^ b ^ c → a ^ (b ^ c)
def parse_power(stream):
    left = parse_factor(stream)
    while stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] == '^':
        op = stream.consume()[1]
        right = parse_power(stream)  # right-associative
        left = BinaryOpNode(left, op, right)
    return left

def parse_input_expression(stream):
    stream.consume('KEYWORD')  # 'input'
    stream.consume('LPAREN')
    prompt = parse_expression(stream)
    stream.consume('RPAREN')
    return InputNode(prompt)

# Highest level: numbers, identifiers, parentheses
def parse_factor(stream):
    token = stream.peek()
    # ...
    if token[0] == 'KEYWORD' and token[1] == 'this':
        stream.consume('KEYWORD')  # 'this'
        base = IdentifierNode('this')
        # Property/method erişimi: this.x, this.x.y, this.method(...)
        while stream.peek() and stream.peek()[0] == 'DOT':
            stream.consume('DOT')
            prop = stream.consume('ID')[1]
            base = BinaryOpNode(base, '.', IdentifierNode(prop))
        # Fonksiyon çağrısı mı?
        if stream.peek() and stream.peek()[0] == 'LPAREN':
            stream.consume('LPAREN')
            args = []
            if stream.peek()[0] != 'RPAREN':
                while True:
                    arg = parse_expression(stream)
                    args.append(arg)
                    if stream.peek()[0] == 'COMMA':
                        stream.consume('COMMA')
                    else:
                        break
            stream.consume('RPAREN')
            return FunctionCallNode(base, args)
        else:
            return base
    token = stream.peek()
    if token[0] == 'KEYWORD' and token[1] == 'new':
        stream.consume('KEYWORD')  # 'new'
        class_name = stream.consume('ID')[1]
        args = []
        if stream.peek() and stream.peek()[0] == 'LPAREN':
            stream.consume('LPAREN')
            print(f"DEBUG: parse_factor: after consume '(', peek: {stream.peek()}")
            if stream.peek() and stream.peek()[0] != 'RPAREN':
                while True:
                    args.append(parse_expression(stream))
                    if stream.peek()[0] == 'COMMA':
                        stream.consume('COMMA')
                    else:
                        break
            stream.consume('RPAREN')
            print(f"DEBUG: parse_factor: after consume ')', peek: {stream.peek()}")
        base = NewInstanceNode(class_name, args) if args else NewInstanceNode(class_name)
        print(f"DEBUG: parse_factor: created NewInstanceNode({class_name}, args={args}), peek: {stream.peek()}")
        # Zincirli erişim: .prop, .method(), [index] gibi
        while True:
            token2 = stream.peek()
            if not token2 or token2[0] not in ('DOT', 'LPAREN', 'LBRACKET'):
                break
            if token2[0] == 'DOT':
                stream.consume('DOT')
                prop = stream.consume('ID')[1]
                base = BinaryOpNode(base, '.', IdentifierNode(prop))
            elif token2[0] == 'LPAREN':
                stream.consume('LPAREN')
                call_args = []
                if stream.peek()[0] != 'RPAREN':
                    while True:
                        call_args.append(parse_expression(stream))
                        if stream.peek()[0] == 'COMMA':
                            stream.consume('COMMA')
                        else:
                            break
                stream.consume('RPAREN')
                base = FunctionCallNode(base, call_args)
            elif token2[0] == 'LBRACKET':
                while stream.peek() and stream.peek()[0] == 'LBRACKET':
                    stream.consume('LBRACKET')
                    index_expr = parse_expression(stream)
                    stream.consume('RBRACKET')
                    base = IndexAccessNode(base, index_expr)
        return base
    token = stream.peek()
    if token[0] == 'LPAREN':
        stream.consume('LPAREN')
        expr = parse_expression(stream)
        stream.consume('RPAREN')
        return expr
    # Array literal: [expr, expr, ...]
    elif token[0] == 'LBRACKET':
        stream.consume('LBRACKET')
        elements = []
        if stream.peek()[0] != 'RBRACKET':
            while True:
                elements.append(parse_expression(stream))
                if stream.peek()[0] == 'COMMA':
                    stream.consume('COMMA')
                else:
                    break
        stream.consume('RBRACKET')
        return ArrayNode(elements)
    elif token[0] == 'BOOL':
        return LiteralNode(stream.consume()[1])  # 'True' or 'False'
    elif token[0] == 'NULL':
        stream.consume()
        return LiteralNode('null')
    elif token[0] == 'NUMBER':
        return LiteralNode(stream.consume()[1])
    elif token[0] == 'STRING':
        return StringNode(stream.consume()[1])
    elif token[0] == 'ID':
        # Property access: p.x
        base = IdentifierNode(stream.consume('ID')[1])
        while stream.peek() and stream.peek()[0] == 'DOT':
            stream.consume('DOT')
            prop = stream.consume('ID')[1]
            base = BinaryOpNode(base, '.', IdentifierNode(prop))
        # Fonksiyon çağrısı mı, index erişimi mi?
        if stream.peek() and stream.peek()[0] == 'LPAREN':
            stream.consume('LPAREN')
            args = []
            if stream.peek()[0] != 'RPAREN':
                while True:
                    arg = parse_expression(stream)
                    args.append(arg)
                    if stream.peek()[0] == 'COMMA':
                        stream.consume('COMMA')
                    else:
                        break
            stream.consume('RPAREN')
            return FunctionCallNode(base, args)
        elif stream.peek() and stream.peek()[0] == 'LBRACKET':
            while stream.peek() and stream.peek()[0] == 'LBRACKET':
                stream.consume('LBRACKET')
                index_expr = parse_expression(stream)
                stream.consume('RBRACKET')
                base = IndexAccessNode(base, index_expr)
            return base
        else:
            return base
    elif token[0] == 'KEYWORD' and token[1] == 'input':
        return parse_input_expression(stream)
    else:
        raise Exception(f"Invalid factor: {token}")
# ----------------------
# Class Definition Parser (Temel)
# ----------------------
def parse_class_definition(stream):
    stream.consume('KEYWORD')  # 'class'
    name = stream.consume('ID')[1]
    # Inheritance kaldırıldı, sadece class ismi ve gövdesi
    base = None
    body = parse_class_block(stream)
    return ClassDefNode(name, body, base)

# Parse class block with static/private/public/constructor
def parse_class_block(stream):
    stmts = []
    stream.consume('LBRACE')
    while stream.peek() and stream.peek()[0] != 'RBRACE':
        # Modifiers
        is_static = False
        is_private = False
        is_constructor = False
        while stream.peek() and stream.peek()[0] == 'KEYWORD' and stream.peek()[1] in ('static', 'private', 'public', 'constructor'):
            mod = stream.consume('KEYWORD')[1]
            if mod == 'static':
                is_static = True
            elif mod == 'private':
                is_private = True
            elif mod == 'constructor':
                is_constructor = True

        # Tip(ler) ve isim ayrımı (C/Java/Python toleransı)
        type_token = None
        name_token = None
        # Modifierlardan sonra doğrudan LPAREN gelirse: constructor
        if stream.peek()[0] == 'LPAREN':
            func_name = 'constructor'
            stream.consume('LPAREN')
            params = []
            if stream.peek()[0] != 'RPAREN':
                while True:
                    if stream.peek()[0] == 'TYPE':
                        stream.consume('TYPE')
                    elif stream.peek()[0] == 'ID' and stream.tokens[stream.position+1][0] == 'ID':
                        stream.consume('ID')
                    param_name = stream.consume('ID')[1]
                    params.append(param_name)
                    if stream.peek()[0] == 'COMMA':
                        stream.consume('COMMA')
                    else:
                        break
            stream.consume('RPAREN')
            body = parse_block(stream)
            stmts.append(FunctionDefNode(func_name, params, body, is_static, is_private, True))
            continue
        # Tip veya isim gelirse: method/property
        elif stream.peek()[0] == 'TYPE':
            tokens = []
            # Tüm ardışık TYPE tokenlarını topla, sonuncusu isim, öncekiler tip
            while stream.peek()[0] == 'TYPE':
                tokens.append(stream.consume('TYPE')[1])
            if stream.peek()[0] == 'ID':
                name_token = stream.consume('ID')[1]
                type_token = ' '.join(tokens) if tokens else None
            else:
                raise Exception(f"Expected identifier after type in class body, got {stream.peek()}")
            # Eğer isimden sonra doğrudan parantez geliyorsa: method
            if stream.peek()[0] == 'LPAREN':
                func_is_constructor = False
                if (type_token is None and (name_token == 'constructor')):
                    func_is_constructor = True
                func_name = name_token if not func_is_constructor else 'constructor'
                stream.consume('LPAREN')
                params = []
                if stream.peek()[0] != 'RPAREN':
                    while True:
                        if stream.peek()[0] == 'TYPE':
                            stream.consume('TYPE')
                        elif stream.peek()[0] == 'ID' and stream.tokens[stream.position+1][0] == 'ID':
                            stream.consume('ID')
                        param_name = stream.consume('ID')[1]
                        params.append(param_name)
                        if stream.peek()[0] == 'COMMA':
                            stream.consume('COMMA')
                        else:
                            break
                stream.consume('RPAREN')
                body = parse_block(stream)
                stmts.append(FunctionDefNode(func_name, params, body, is_static, is_private, func_is_constructor or is_constructor))
                continue
        # Eğer ilk token ID ve ardından LPAREN geliyorsa (method): tip yok, isim var
        elif stream.peek()[0] == 'ID' and stream.position + 1 < len(stream.tokens) and stream.tokens[stream.position+1][0] == 'LPAREN':
            name_token = stream.consume('ID')[1]
            type_token = None
            # Method
            stream.consume('LPAREN')
            params = []
            if stream.peek()[0] != 'RPAREN':
                while True:
                    if stream.peek()[0] == 'TYPE':
                        stream.consume('TYPE')
                    elif stream.peek()[0] == 'ID' and stream.tokens[stream.position+1][0] == 'ID':
                        stream.consume('ID')
                    param_name = stream.consume('ID')[1]
                    params.append(param_name)
                    if stream.peek()[0] == 'COMMA':
                        stream.consume('COMMA')
                    else:
                        break
            stream.consume('RPAREN')
            body = parse_block(stream)
            stmts.append(FunctionDefNode(name_token, params, body, is_static, is_private, False))
            continue
            # Eğer isimden sonra doğrudan parantez geliyorsa: method
            if stream.peek()[0] == 'LPAREN':
                func_is_constructor = False
                if (type_token is None and (name_token == 'constructor')):
                    func_is_constructor = True
                func_name = name_token if not func_is_constructor else 'constructor'
                stream.consume('LPAREN')
                params = []
                if stream.peek()[0] != 'RPAREN':
                    while True:
                        if stream.peek()[0] == 'TYPE':
                            stream.consume('TYPE')
                        elif stream.peek()[0] == 'ID' and stream.tokens[stream.position+1][0] == 'ID':
                            stream.consume('ID')
                        param_name = stream.consume('ID')[1]
                        params.append(param_name)
                        if stream.peek()[0] == 'COMMA':
                            stream.consume('COMMA')
                        else:
                            break
                stream.consume('RPAREN')
                body = parse_block(stream)
                stmts.append(FunctionDefNode(func_name, params, body, is_static, is_private, func_is_constructor or is_constructor))
                continue
        else:
            raise Exception(f"Expected type or identifier in class body, got {stream.peek()[0]}")

        # Method mu property mi?
        if stream.peek()[0] == 'LPAREN':
            # Method/fonksiyon
            func_name = name_token
            stream.consume('LPAREN')
            params = []
            if stream.peek()[0] != 'RPAREN':
                while True:
                    # Parametre tipi (isteğe bağlı, atla)
                    if stream.peek()[0] == 'TYPE':
                        stream.consume('TYPE')
                    elif stream.peek()[0] == 'ID' and stream.tokens[stream.position+1][0] == 'ID':
                        stream.consume('ID')
                    param_name = stream.consume('ID')[1]
                    params.append(param_name)
                    if stream.peek()[0] == 'COMMA':
                        stream.consume('COMMA')
                    else:
                        break
            stream.consume('RPAREN')
            body = parse_block(stream)
            stmts.append(FunctionDefNode(func_name, params, body, is_static, is_private, False))
        elif stream.peek()[0] == 'OP' and stream.peek()[1] == '=':
            # Property
            stream.consume('OP')  # '='
            value = parse_expression(stream)
            stream.consume('SEMI')
            stmts.append(VarDeclarationNode(type_token, name_token, value, is_static, is_private))
        elif stream.peek()[0] == 'SEMI':
            # Property (başlangıç değeri yok)
            stream.consume('SEMI')
            stmts.append(VarDeclarationNode(type_token, name_token, None, is_static, is_private))
        else:
            # Hatalı veya beklenmeyen durum
            raise Exception(f"Unexpected token after class member name: {stream.peek()}")
    stream.consume('RBRACE')
    return BlockNode(stmts)


# ----------------------
# Other Statements
# ----------------------
def parse_variable_declaration(stream):
    var_type = stream.consume('TYPE')[1]
    var_name = stream.consume('ID')[1]
    stream.consume('OP')  # Expect '='
    value = parse_expression(stream)
    stream.consume('SEMI')  # Expect ';'
    return VarDeclarationNode(var_type, var_name, value)

def parse_print_statement(stream):
    stream.consume('KEYWORD')  # 'print'
    stream.consume('LPAREN')
    value = parse_expression(stream)
    stream.consume('RPAREN')
    stream.consume('SEMI')
    return PrintNode(value)

def parse_variable_declaration_inline(stream):
    var_type = stream.consume('TYPE')[1]
    var_name = stream.consume('ID')[1]
    op = stream.consume('OP')
    if op[1] != '=':
        raise Exception(f"Expected '=' in inline variable declaration, got {op[1]}")
    value = parse_expression(stream)
    return VarDeclarationNode(var_type, var_name, value)

def parse_assignment_expression(stream):
    # Assignment expression: ID = expr, right-associative
    if stream.peek()[0] == 'ID':
        # Lookahead for '='
        if stream.position + 1 < len(stream.tokens) and stream.tokens[stream.position+1][0] == 'OP' and stream.tokens[stream.position+1][1] == '=':
            name = stream.consume('ID')[1]
            stream.consume('OP')  # '='
            value = parse_assignment_expression(stream)
            return BinaryOpNode(IdentifierNode(name), '=', value)
    # Otherwise, fallback to normal expression
    return parse_expression(stream)

def parse_for_statement(stream):
    stream.consume('KEYWORD')  # 'for'
    stream.consume('LPAREN')

    # INIT
    if stream.peek()[0] == 'TYPE':
        init = parse_variable_declaration_inline(stream)
        stream.consume('SEMI')
    else:
        init = parse_assignment_expression(stream)
        stream.consume('SEMI')

    # CONDITION
    condition = parse_expression(stream)
    stream.consume('SEMI')

    # INCREMENT
    increment = parse_assignment_expression(stream)
    stream.consume('RPAREN')

    # BODY
    body = parse_block(stream)

    return ForNode(init, condition, increment, body)


def parse_if_statement(stream):
    stream.consume('KEYWORD')  # 'if'
    stream.consume('LPAREN')
    condition = parse_expression(stream)
    stream.consume('RPAREN')
    # Inline if: blok yerine tek statement veya expression kabul et
    if stream.peek() and stream.peek()[0] == 'LBRACE':
        then_block = parse_block(stream)
    else:
        # Tek satırlık statement (ör: print(...); veya atama)
        # Sadece bir statement parse et, blok gibi davran
        stmt = None
        token = stream.peek()
        if token[0] == 'KEYWORD' and token[1] == 'print':
            stmt = parse_print_statement(stream)
        elif token[0] == 'KEYWORD' and token[1] == 'input':
            stmt = parse_input_expression(stream)
        elif token[0] == 'ID' or (token[0] == 'KEYWORD' and token[1] == 'this'):
            expr = parse_expression(stream)
            if stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] == '=':
                stream.consume('OP')
                value = parse_expression(stream)
                stream.consume('SEMI')
                stmt = BinaryOpNode(expr, '=', value)
            elif stream.peek() and stream.peek()[0] == 'SEMI':
                stream.consume('SEMI')
                stmt = expr
            else:
                raise Exception(f"Unexpected token after inline if: {stream.peek()}")
        else:
            raise Exception(f"Unsupported inline if statement: {token}")
        then_block = BlockNode([stmt])

    else_block = None
    # elseif zinciri
    if stream.peek() and stream.peek()[0] == 'KEYWORD' and stream.peek()[1] == 'elseif':
        stream.consume('KEYWORD')  # 'elseif'
        stream.consume('LPAREN')
        elseif_condition = parse_expression(stream)
        stream.consume('RPAREN')
        elseif_then = parse_block(stream)
        else_block = parse_if_statement_from_parts(stream, elseif_condition, elseif_then)
    elif stream.peek() and stream.peek()[0] == 'KEYWORD' and stream.peek()[1] == 'else':
        stream.consume('KEYWORD')  # 'else'
        if stream.peek() and stream.peek()[0] == 'LBRACE':
            else_block = parse_block(stream)
        else:
            # Tek satırlık else
            stmt = None
            token = stream.peek()
            if token[0] == 'KEYWORD' and token[1] == 'print':
                stmt = parse_print_statement(stream)
            elif token[0] == 'KEYWORD' and token[1] == 'input':
                stmt = parse_input_expression(stream)
            elif token[0] == 'ID' or (token[0] == 'KEYWORD' and token[1] == 'this'):
                expr = parse_expression(stream)
                if stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] == '=':
                    stream.consume('OP')
                    value = parse_expression(stream)
                    stream.consume('SEMI')
                    stmt = BinaryOpNode(expr, '=', value)
                elif stream.peek() and stream.peek()[0] == 'SEMI':
                    stream.consume('SEMI')
                    stmt = expr
                else:
                    raise Exception(f"Unexpected token after inline else: {stream.peek()}")
            else:
                raise Exception(f"Unsupported inline else statement: {token}")
            else_block = BlockNode([stmt])
    return IfNode(condition, then_block, else_block)

# elseif zinciri için yardımcı fonksiyon
def parse_if_statement_from_parts(stream, condition, then_block):
    else_block = None
    if stream.peek() and stream.peek()[0] == 'KEYWORD' and stream.peek()[1] == 'elseif':
        stream.consume('KEYWORD')
        stream.consume('LPAREN')
        elseif_condition = parse_expression(stream)
        stream.consume('RPAREN')
        elseif_then = parse_block(stream)
        else_block = parse_if_statement_from_parts(stream, elseif_condition, elseif_then)
    elif stream.peek() and stream.peek()[0] == 'KEYWORD' and stream.peek()[1] == 'else':
        stream.consume('KEYWORD')
        else_block = parse_block(stream)
    return IfNode(condition, then_block, else_block)

def parse_while_statement(stream):
    stream.consume('KEYWORD')  # 'while'
    stream.consume('LPAREN')
    condition = parse_expression(stream)
    stream.consume('RPAREN')
    body = parse_block(stream)
    return WhileNode(condition, body)

def parse_function_definition(stream):
    stream.consume('KEYWORD')  # 'fn'
    name = stream.consume('ID')[1]
    stream.consume('LPAREN')

    params = []
    if stream.peek()[0] != 'RPAREN':
        while True:
            param = stream.consume('ID')[1]
            params.append(param)
            if stream.peek()[0] == 'COMMA':
                stream.consume('COMMA')
            else:
                break

    stream.consume('RPAREN')
    body = parse_block(stream)
    return FunctionDefNode(name, params, body)

def parse_return_statement(stream):
    stream.consume('KEYWORD')  # 'return'
    value = parse_expression(stream)
    stream.consume('SEMI')
    return ReturnNode(value)

def parse_function_call(stream):
    name = stream.consume('ID')[1]
    stream.consume('LPAREN')

    args = []
    if stream.peek()[0] != 'RPAREN':
        while True:
            arg = parse_expression(stream)
            args.append(arg)
            if stream.peek()[0] == 'COMMA':
                stream.consume('COMMA')
            else:
                break

    stream.consume('RPAREN')
    stream.consume('SEMI')
    return FunctionCallNode(name, args)

# for-each ile klasik for ayrımını yapan yardımcı fonksiyon
def is_for_each_syntax(stream):
    pos = stream.position
    try:
        if stream.peek()[0] == 'KEYWORD' and stream.peek()[1] == 'for':
            if stream.tokens[pos+1][0] == 'LPAREN':
                idx = pos+2
                if stream.tokens[idx][0] == 'TYPE':
                    idx += 1
                if stream.tokens[idx][0] == 'ID' and stream.tokens[idx+1][0] == 'KEYWORD' and stream.tokens[idx+1][1] == 'in':
                    return True
                if stream.tokens[idx][0] == 'ID' and stream.tokens[idx+1][0] == 'KEYWORD' and stream.tokens[idx+1][1] == 'in':
                    return True
    except Exception:
        pass
    return False

# ----------------------
# Block Parser
# ----------------------
def parse_block(stream):
    stream.consume('LBRACE')
    statements = []
    while stream.peek() and stream.peek()[0] != 'RBRACE':
        token = stream.peek()
        if token[0] == 'TYPE':
            node = parse_variable_declaration(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'print':
            node = parse_print_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'input':
            node = parse_input_expression(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'if':
            node = parse_if_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'while':
            node = parse_while_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'return':
            node = parse_return_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'fn':
            node = parse_function_definition(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'class':
            node = parse_class_definition(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'try':
            node = parse_try_catch_statement(stream)
            statements.append(node)
        elif token[0] == 'ID' or (token[0] == 'KEYWORD' and token[1] == 'this'):
            # Fonksiyon çağrısı mı yoksa atama mı? (this.x = ... veya this.method(...))
            start_pos = stream.position
            # this veya id ile başlayan bir ifade
            expr = parse_expression(stream)
            # Atama mı?
            if stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] == '=':
                stream.consume('OP')  # '='
                value = parse_expression(stream)
                stream.consume('SEMI')
                node = BinaryOpNode(expr, '=', value)
                statements.append(node)
            # Fonksiyon çağrısı mı? (ör: this.method(...); veya foo(...);)
            elif stream.peek() and stream.peek()[0] == 'SEMI':
                stream.consume('SEMI')
                statements.append(expr)
            else:
                raise Exception(f"Unexpected token in block after expression: {stream.peek()}")
        elif token[0] == 'KEYWORD' and token[1] == 'for' and is_for_each_syntax(stream):
            node = parse_for_each_statement(stream)
            statements.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'for':
            node = parse_for_statement(stream)
            statements.append(node)
        else:
            raise Exception(f"Unexpected token in block: {token}")
    stream.consume('RBRACE')
    return BlockNode(statements)

# ----------------------
# Top-Level Program Parser
# ----------------------
def parse_program(tokens):
    stream = TokenStream(tokens)
    ast_nodes = []

    while stream.peek():
        token = stream.peek()
        if token[0] == 'TYPE':
            node = parse_variable_declaration(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'print':
            node = parse_print_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'input':
            node = parse_input_expression(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'if':
            node = parse_if_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'for' and is_for_each_syntax(stream):
            node = parse_for_each_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'for':
            node = parse_for_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'while':
            node = parse_while_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'return':
            node = parse_return_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'fn':
            node = parse_function_definition(stream)
            ast_nodes.append(node)
        elif token[0] == 'KEYWORD' and token[1] == 'class':
            node = parse_class_definition(stream)
            ast_nodes.append(node)
            # Class tanımı sonrası, bir sonraki statement'a kadar ilerle
            while stream.peek() and stream.peek()[0] not in ('TYPE', 'KEYWORD', 'ID'):
                stream.position += 1
            continue
        elif token[0] == 'KEYWORD' and token[1] == 'try':
            node = parse_try_catch_statement(stream)
            ast_nodes.append(node)
        elif token[0] == 'ID' or (token[0] == 'KEYWORD' and token[1] == 'this'):
            # Zincirli property/method erişimi ve atama/fonksiyon çağrısı desteği
            expr = parse_expression(stream)
            if stream.peek() and stream.peek()[0] == 'OP' and stream.peek()[1] == '=':
                stream.consume('OP')
                value = parse_expression(stream)
                stream.consume('SEMI')
                node = BinaryOpNode(expr, '=', value)
                ast_nodes.append(node)
            elif stream.peek() and stream.peek()[0] == 'SEMI':
                stream.consume('SEMI')
                ast_nodes.append(expr)
            else:
                raise Exception(f"Unexpected token in top-level after expression: {stream.peek()}")
        else:
            raise Exception(f"Unexpected token: {token}")

    return ast_nodes


# ----------------------
# AST Printer (for debugging)
# ----------------------
def print_ast(node):
    if isinstance(node, LiteralNode):
        return node.value
    elif isinstance(node, IdentifierNode):
        return node.name
    elif isinstance(node, StringNode):
        return f'"{node.value}"'
    elif isinstance(node, BinaryOpNode):
        return f"({print_ast(node.left)} {node.operator} {print_ast(node.right)})"
    elif isinstance(node, VarDeclarationNode):
        return f"{node.var_type} {node.name} = {print_ast(node.value)};"
    elif isinstance(node, PrintNode):
        return f"print({print_ast(node.value)});"
    else:
        return str(node)