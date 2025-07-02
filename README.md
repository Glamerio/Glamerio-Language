# Glamerio-Language

Glamerio-Language is a modern, user-friendly interpreted programming language designed for both beginners and advanced users. It combines the essential and advanced features of popular languages (such as Python, JavaScript, and Java) with a simple, readable syntax. Glamerio is ideal for learning programming concepts, rapid prototyping, and building small to medium-scale applications.

## Key Features
- **Object-Oriented Programming (OOP):** Classes, objects, methods, and the `new` keyword.
- **Map/Dictionary Data Type:** Native support for key-value pairs, dynamic access, and assignment.
- **String Functions:** Built-in methods like `toUpperCase`, `toLowerCase`, `substring`, `contains`, and `replace`.
- **Logical and Comparison Operators:** `&&`, `||`, `!`, `==`, `!=`, `<`, `>`, `<=`, `>=`.
- **Error Handling:** `try-catch` blocks for robust error management.
- **Inline If (Ternary Operator):** Short conditional expressions.
- **Flexible Loops:** Classic `for`, `for-each`, and `while` loops.
- **Automatic Type Conversion:** Use `var` for dynamic typing and easy variable declarations.
- **User-Friendly Error Messages:** All errors include line and column information for easy debugging.
- **Multiple/Empty Variable Declaration:** Declare multiple or empty variables with ease.
- **Optional Map Functions:** `keys()`, `values()`, `hasKey()`, `remove()` for advanced map operations.

## Getting Started

### 1. Requirements
- Python 3.8 or higher

### 2. Running a Glamerio Program
1. Write your code in a `.gl` file (see `test_cases.gl` for examples).
2. Run the interpreter from the command line:

```sh
python main.py your_program.gl
```

Example:

```sh
python main.py test_cases.gl
```

### 3. File Structure
- `main.py`         : Entry point for the interpreter
- `lexer.py`        : Lexical analyzer
- `parser.py`       : Parser and AST builder
- `interpreter.py`  : Main interpreter logic
- `glam_ast.py`     : AST node definitions
- `test_cases.gl`   : Example and test scripts
- `syntax.txt`      : Full language syntax reference

## Language Overview

### Variables & Types
```glam
int x = 5;
float y = 3.14;
str z = "Hello";
bool b = true;
var autoType = 42;
var emptyVar;
```

### Map/Dictionary
```glam
map student = {"name": "Ali", "id": 123, "grade": 95};
print(student["name"]);
student["grade"] = 100;
```

### String Functions
```glam
str s = "Glamerio Test";
print(s.toUpperCase());
print(s.substring(0, 7));
print(s.contains("Test"));
print(s.replace("Test", "Language"));
```

### Conditionals
```glam
if (x > 3) {
    print("Greater");
} else {
    print("Smaller");
}
result = x > 3 ? "Greater" : "Smaller";
```

### Loops
```glam
for (int i = 0; i < 5; i = i + 1) {
    print(i);
}
tuple numbers = [1, 2, 3];
for (var n in numbers) {
    print(n);
}
```

### Functions
```glam
def sum(int a, int b) {
    return a + b;
}
print(sum(3, 5));


    print("Hello, " + name);
}
greet();
greet("Ali");
```

### Classes & OOP
```glam
class Car {
    str brand;
    int year;
    def start() {
        print(brand + " is running");
    }
}
Car c = new Car();
c.brand = "BMW";
c.year = 2020;
c.start();
```

### Error Handling
```glam
try {
    int x = 5 / 0;
} catch (e) {
    print("Error: " + e);
}
```

## Map/Dictionary Functions (optional)
- `keys()`, `values()`, `hasKey()`, `remove()`

## Error Messages
All errors are shown in `[Line X, Column Y]` format with clear explanations.

## More
- For all examples and tests, see `test_cases.gl`.
- For full syntax, see `syntax.txt`.

---

Author: [Your Name]
Date: July 2025
