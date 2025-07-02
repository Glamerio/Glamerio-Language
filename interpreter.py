# ---------------------------------------------
# Glamerio Interpreter - interpreter.py
# Full runtime support for:
# - Variables, Print, Input
# - If / Else, While
# - Functions, Return
# ---------------------------------------------

from glam_ast import *

memory = {}         # global variables
functions = {}      # function definitions
classes = {}        # class definitions (name -> ClassDefNode)
call_stack = []     # for function calls

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


def evaluate(node, local_scope=None):
    # Try-catch error handling
    if isinstance(node, TryCatchNode):
        try:
            return evaluate(node.try_block, local_scope)
        except Exception as e:
            if node.catch_var:
                # Yeni bir scope ile hata değişkenini ata
                catch_scope = dict(local_scope) if local_scope else {}
                catch_scope[node.catch_var] = str(e)
                return evaluate(node.catch_block, catch_scope)
            else:
                return evaluate(node.catch_block, local_scope)
    # ClassInstanceNode desteği (ileride parser veya başka bir yerde kullanılabilir)
    # Method ve property'leri ayır: methodlar fonksiyon, property'ler değişken
    if isinstance(node, ClassInstanceNode):
        def collect_class_hierarchy(class_name):
            # Inheritance desteği: üst sınıfları sırayla topla
            hierarchy = []
            current = classes.get(class_name)
            while current:
                hierarchy.append(current)
                base = getattr(current, 'base', None)
                if base:
                    current = classes.get(base)
                else:
                    break
            return hierarchy

        class_def = classes.get(node.class_name)
        if not class_def:
            raise Exception(f"Class '{node.class_name}' not defined")
        instance = {'__class__': node.class_name}
        methods = {}
        # Inheritance: base class'lardan property ve methodları sırayla ekle (alt sınıf override eder)
        for cdef in reversed(collect_class_hierarchy(node.class_name)):
            for stmt in cdef.body.statements:
                # Access control: private property/method sadece this içinden erişilebilir
                is_private = hasattr(stmt, 'is_private') and stmt.is_private
                if isinstance(stmt, VarDeclarationNode):
                    if stmt.name not in instance:
                        instance[stmt.name] = evaluate(stmt.value, memory)
                    if is_private:
                        if '__private__' not in instance:
                            instance['__private__'] = set()
                        instance['__private__'].add(stmt.name)
                elif isinstance(stmt, FunctionDefNode):
                    methods[stmt.name] = stmt
                    if is_private:
                        if '__private_methods__' not in instance:
                            instance['__private_methods__'] = set()
                        instance['__private_methods__'].add(stmt.name)
        instance['__methods__'] = methods
        # Constructor çağrısı (init veya constructor methodu varsa)
        ctor = methods.get('constructor') or methods.get('init')
        if ctor:
            local = {'this': instance}
            # Parametre yoksa boş çağır
            try:
                evaluate(ctor.body, local)
            except ReturnException as r:
                pass
        return instance
    # Class definition
    if isinstance(node, ClassDefNode):
        # Static property/method desteği: class objesine ekle
        static_props = {}
        static_methods = {}
        for stmt in node.body.statements:
            # Static property: var static int x = 5; veya static int x = 5;
            if hasattr(stmt, 'is_static') and stmt.is_static:
                if isinstance(stmt, VarDeclarationNode):
                    static_props[stmt.name] = evaluate(stmt.value, memory)
                elif isinstance(stmt, FunctionDefNode):
                    static_methods[stmt.name] = stmt
        node.__static_props__ = static_props
        node.__static_methods__ = static_methods
        classes[node.name] = node
        return None

    # new ClassName() instance creation
    if isinstance(node, NewInstanceNode):
        def collect_class_hierarchy(class_name):
            hierarchy = []
            current = classes.get(class_name)
            while current:
                hierarchy.append(current)
                base = getattr(current, 'base', None)
                if base:
                    current = classes.get(base)
                else:
                    break
            return hierarchy

        class_def = classes.get(node.class_name)
        if not class_def:
            raise Exception(f"Class '{node.class_name}' not defined")
        instance = {'__class__': node.class_name}
        methods = {}
        for cdef in reversed(collect_class_hierarchy(node.class_name)):
            for stmt in cdef.body.statements:
                if isinstance(stmt, VarDeclarationNode):
                    if stmt.name not in instance:
                        instance[stmt.name] = evaluate(stmt.value, memory)
                elif isinstance(stmt, FunctionDefNode):
                    methods[stmt.name] = stmt
        instance['__methods__'] = methods
        # Constructor çağrısı (init veya constructor methodu varsa)
        ctor = methods.get('constructor') or methods.get('init')
        if ctor:
            local = {'this': instance}
            try:
                evaluate(ctor.body, local)
            except ReturnException as r:
                pass
        return instance
    scope = local_scope if local_scope is not None else memory

    # Array literal
    if isinstance(node, ArrayNode):
        return [evaluate(el, scope) for el in node.elements]

    # Array index access
    if isinstance(node, IndexAccessNode):
        lst = evaluate(node.list_expr, scope)
        idx = evaluate(node.index_expr, scope)
        return lst[idx]

    if isinstance(node, LiteralNode):
        value = node.value
        if value == 'null':
            return None
        elif value == 'True':
            return True
        elif value == 'False':
            return False
        return float(value) if '.' in value else int(value)

    elif isinstance(node, StringNode):
        return node.value
    
    elif isinstance(node, InputNode):
        prompt = evaluate(node.prompt, scope)
        return input(str(prompt))  # Ensure it's string prompt

    elif isinstance(node, IdentifierNode):
        name = node.name
        if name in scope:
            return scope[name]
        elif name in memory:
            return memory[name]
        elif name in classes:
            return classes[name]
        else:
            raise Exception(f"Undefined variable or class: {name}")

    # Property/method/static access: p.x, p.foo, ClassName.staticX, ClassName.staticFoo, string method/property
    elif isinstance(node, BinaryOpNode) and node.operator == '.':
        left_val = evaluate(node.left, scope)
        prop = node.right.name
        # String property support
        if isinstance(left_val, str):
            if prop == 'length':
                return len(left_val)
            raise Exception(f"Unknown string property: {prop}")
        # Instance property/method
        if isinstance(left_val, dict):
            # ...existing code...
            if '__private__' in left_val and prop in left_val['__private__']:
                # ...existing code...
                import inspect
                stack = inspect.stack()
                # ...existing code...
                allow = False
                for frame in stack:
                    if 'this' in frame.frame.f_locals and frame.frame.f_locals['this'] is left_val:
                        allow = True
                        break
                if not allow:
                    raise Exception(f"Property '{prop}' is private")
            if prop in left_val:
                return left_val[prop]
            elif '__methods__' in left_val and prop in left_val['__methods__']:
                # ...existing code...
                if '__private_methods__' in left_val and prop in left_val['__private_methods__']:
                    import inspect
                    stack = inspect.stack()
                    allow = False
                    for frame in stack:
                        if 'this' in frame.frame.f_locals and frame.frame.f_locals['this'] is left_val:
                            allow = True
                            break
                    if not allow:
                        raise Exception(f"Method '{prop}' is private")
                return ('__method__', left_val, left_val['__methods__'][prop])
        # Static property/method: ClassName.x
        elif isinstance(node.left, IdentifierNode) and node.left.name in classes:
            class_def = classes[node.left.name]
            # ...existing code...
            if hasattr(class_def, '__static_props__') and prop in class_def.__static_props__:
                return class_def.__static_props__[prop]
            # ...existing code...
            if hasattr(class_def, '__static_methods__') and prop in class_def.__static_methods__:
                return ('__staticmethod__', class_def, class_def.__static_methods__[prop])
        raise Exception(f"Property or method '{prop}' not found on object or class")

    # String method call support: "abc".substring(1, 2)
    elif isinstance(node, FunctionCallNode) and isinstance(node.name, BinaryOpNode) and node.name.operator == '.':
        left_val = evaluate(node.name.left, scope)
        method = node.name.right.name
        if isinstance(left_val, str):
            if method == 'substring':
                args = [evaluate(arg, scope) for arg in node.args]
                if len(args) == 1:
                    return left_val[args[0]:]
                elif len(args) == 2:
                    return left_val[args[0]:args[1]]
                else:
                    raise Exception('substring() expects 1 or 2 arguments')
            raise Exception(f"Unknown string method: {method}")
        # Instance property/method
        if isinstance(left_val, dict):
            # Access control: private property/method dışarıdan erişilemez
            if '__private__' in left_val and prop in left_val['__private__']:
                # Sadece this içinden erişime izin ver
                import inspect
                stack = inspect.stack()
                # this ile erişim: en az bir üstte local'de 'this' varsa izin ver
                allow = False
                for frame in stack:
                    if 'this' in frame.frame.f_locals and frame.frame.f_locals['this'] is left_val:
                        allow = True
                        break
                if not allow:
                    raise Exception(f"Property '{prop}' is private")
            if prop in left_val:
                return left_val[prop]
            elif '__methods__' in left_val and prop in left_val['__methods__']:
                # Private method kontrolü
                if '__private_methods__' in left_val and prop in left_val['__private_methods__']:
                    import inspect
                    stack = inspect.stack()
                    allow = False
                    for frame in stack:
                        if 'this' in frame.frame.f_locals and frame.frame.f_locals['this'] is left_val:
                            allow = True
                            break
                    if not allow:
                        raise Exception(f"Method '{prop}' is private")
                return ('__method__', left_val, left_val['__methods__'][prop])
        # Static property/method: ClassName.x
        elif isinstance(node.left, IdentifierNode) and node.left.name in classes:
            class_def = classes[node.left.name]
            # Static property
            if hasattr(class_def, '__static_props__') and prop in class_def.__static_props__:
                return class_def.__static_props__[prop]
            # Static method
            if hasattr(class_def, '__static_methods__') and prop in class_def.__static_methods__:
                return ('__staticmethod__', class_def, class_def.__static_methods__[prop])
        raise Exception(f"Property or method '{prop}' not found on object or class")

    elif isinstance(node, BinaryOpNode):
        op = node.operator
        # Assignment as expression: x = expr, or array index assignment
        if op == '=':
            # Array index assignment: l[1] = 99;
            if isinstance(node.left, IndexAccessNode):
                lst = evaluate(node.left.list_expr, scope)
                idx = evaluate(node.left.index_expr, scope)
                value = evaluate(node.right, scope)
                lst[idx] = value
                return value
            # Property assignment: p.x = ... veya ClassName.staticX = ...
            if isinstance(node.left, BinaryOpNode) and node.left.operator == '.':
                obj = evaluate(node.left.left, scope)
                prop = node.left.right.name
                value = evaluate(node.right, scope)
                # Instance property
                if isinstance(obj, dict):
                    obj[prop] = value
                    return value
                # Static property assignment: ClassName.x = ...
                elif hasattr(obj, '__static_props__'):
                    obj.__static_props__[prop] = value
                    return value
                else:
                    raise Exception('Left side of assignment must be a variable, array index, or object property')
            # Normal variable assignment
            if not isinstance(node.left, IdentifierNode):
                raise Exception('Left side of assignment must be a variable, array index, or object property')
            value = evaluate(node.right, scope)
            scope[node.left.name] = value
            return value
        left = evaluate(node.left, scope)
        right = evaluate(node.right, scope)
        if op == '+':
            # String birleştirme desteği
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '^':
            return left ** right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '<=':
            return left <= right
        elif op == '>':
            return left > right
        elif op == '>=':
            return left >= right
        elif op in ('and', '&&'):
            return bool(left) and bool(right)
        elif op in ('or', '||'):
            return bool(left) or bool(right)
        else:
            raise Exception(f"Unknown operator: {op}")

    elif isinstance(node, VarDeclarationNode):
        value = evaluate(node.value, scope)
        # Otomatik tip dönüşümü: int x = input(); gibi durumlar için
        if hasattr(node, 'var_type'):
            if node.var_type == 'int' and isinstance(value, str):
                try:
                    value = int(value)
                except Exception:
                    raise Exception(f"Cannot convert input to int: {value}")
            elif node.var_type == 'float' and isinstance(value, str):
                try:
                    value = float(value)
                except Exception:
                    raise Exception(f"Cannot convert input to float: {value}")
        scope[node.name] = value

    elif isinstance(node, PrintNode):
        value = evaluate(node.value, scope)
        if value is None:
            print('null')
        else:
            print(value)

    elif isinstance(node, InputNode):
        prompt = evaluate(node.prompt, scope)
        return input(prompt)

    elif isinstance(node, IfNode):
        condition = evaluate(node.condition, scope)
        if condition:
            evaluate(node.then_block, scope)
        elif node.else_block:
            evaluate(node.else_block, scope)
    
    elif isinstance(node, ForNode):
        # For döngüsünde ana scope'u kullan, böylece x gibi dış değişkenler güncellenir
        evaluate(node.init, scope)
        while evaluate(node.condition, scope):
            evaluate(node.body, scope)
            evaluate(node.increment, scope)
    
    # For-each döngüsü
    elif isinstance(node, ForEachNode):
        iterable = evaluate(node.iterable, local_scope if local_scope is not None else memory)
        scope = local_scope if local_scope is not None else memory
        for item in iterable:
            scope[node.var_name] = item
            result = evaluate(node.body, scope)
        return None

    elif isinstance(node, WhileNode):
        while evaluate(node.condition, scope):
            evaluate(node.body, scope)

    elif isinstance(node, BlockNode):
        result = None
        for stmt in node.statements:
            result = evaluate(stmt, scope)
        return result

    elif isinstance(node, FunctionDefNode):
        functions[node.name] = node  # store the function definition

    elif isinstance(node, FunctionCallNode):
        # Method veya static method çağrısı: p.foo(1,2) veya ClassName.staticFoo(1,2)
        if isinstance(node.name, BinaryOpNode) and node.name.operator == '.':
            method_ref = evaluate(node.name, scope)
            # Instance method
            if isinstance(method_ref, tuple) and method_ref[0] == '__method__':
                instance = method_ref[1]
                method_def = method_ref[2]
                local = {'this': instance}
                for i, param in enumerate(method_def.params):
                    local[param] = evaluate(node.args[i], scope)
                try:
                    evaluate(method_def.body, local)
                except ReturnException as r:
                    return r.value
                return None
            # Static method
            elif isinstance(method_ref, tuple) and method_ref[0] == '__staticmethod__':
                class_def = method_ref[1]
                method_def = method_ref[2]
                local = {}
                for i, param in enumerate(method_def.params):
                    local[param] = evaluate(node.args[i], scope)
                try:
                    evaluate(method_def.body, local)
                except ReturnException as r:
                    return r.value
                return None
            else:
                raise Exception('Invalid method call')
        # Normal fonksiyon çağrısı
        func = functions.get(node.name)
        if not func:
            raise Exception(f"Function '{node.name}' not defined")
        # Create local scope for function
        local = {}
        for i, param in enumerate(func.params):
            local[param] = evaluate(node.args[i], scope)
        try:
            evaluate(func.body, local)
        except ReturnException as r:
            return r.value
        return None

    elif isinstance(node, ReturnNode):
        value = evaluate(node.value, scope)
        raise ReturnException(value)

    else:
        raise Exception(f"Unknown node type: {type(node)} (name: {type(node).__name__}, content: {node})")


def run(ast):
    for node in ast:
        evaluate(node)