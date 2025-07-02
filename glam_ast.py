# AST (Abstract Syntax Tree) Node Definitions

class VarDeclarationNode:
    def __init__(self, var_type, name, value, is_static=False, is_private=False):
        self.var_type = var_type
        self.name = name
        self.value = value
        self.is_static = is_static
        self.is_private = is_private

class PrintNode:
    def __init__(self, value):
        self.value = value

class LiteralNode:
    def __init__(self, value):
        self.value = value

class StringNode:
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

class InputNode:
    def __init__(self, prompt):
        self.prompt = prompt

class IfNode:
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class BlockNode:
    def __init__(self, statements):
        self.statements = statements

class FunctionDefNode:
    def __init__(self, name, params, body, is_static=False, is_private=False, is_constructor=False):
        self.name = name
        self.params = params
        self.body = body
        self.is_static = is_static
        self.is_private = is_private
        self.is_constructor = is_constructor

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ReturnNode:
    def __init__(self, value):
        self.value = value

class ForNode:
    def __init__(self, init, condition, increment, body):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body

class ForEachNode:
    def __init__(self, var_type, var_name, iterable, body):
        self.var_type = var_type
        self.var_name = var_name
        self.iterable = iterable
        self.body = body

class TryCatchNode:
    def __init__(self, try_block, catch_var, catch_block):
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block

class ArrayNode:
    def __init__(self, elements):
        self.elements = elements

class IndexAccessNode:
    def __init__(self, list_expr, index_expr):
        self.list_expr = list_expr
        self.index_expr = index_expr

class ClassDefNode:
    def __init__(self, name, body, base=None):
        self.name = name
        self.body = body
        self.base = base

class ClassInstanceNode:
    def __init__(self, class_name):
        self.class_name = class_name

class NewInstanceNode:
    def __init__(self, class_name, args=None):
        self.class_name = class_name
        self.args = args or []
