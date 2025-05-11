import re
import ast





code = '''
mydb = create_db("myDB")
users = create_table(mydb)
users.insert_one({"key": "value","age":324})
users.insert_many([{"key1": "value1"}, {"key2": "value2"}])


for obj in users:
    if obj["Rating"]> 4.5 or obj["Rating"]==5:
        print(obj)
   
users.delete_one([{'name':'Alice','age':20, 'city':'New York'}])
users.delete_one(['age>18 and age<30 or age!=25 and condition2=="value2"'])
users.delete_all(["age>18 and age<30 or age!=25 and condition3=='value3'"])

users.update_one(["age > 30 and key2==5"],["condition1 = 100 , condition2='value2' "])
users.update_all(["age > 30 and key2==5"],["condition = 100"])


users.delete_table()
mydb.delete()
'''



class CustomLanguageSyntaxChecker:
    def __init__(self):
        # Define valid function/method patterns
        self.valid_functions = {
            "create_db": 1,  # Expects 1 argument
            "create_table": 1,  # Expects 1 argument
        }
        
        self.valid_methods = {
            "insert_one": 1,
            "insert_many": 1,
            "delete_one": 1,
            "delete_all": 1,
            "update_one": 2,  # Expects 2 arguments: condition and update
            "update_all": 2,
            "delete_table": 0,
            "delete": 0
        }
        
    def check_syntax(self, code):
        """Check the syntax of the custom language code."""
        errors = []
        
        try:
            # First, check if it's valid Python syntax
            tree = ast.parse(code)
            
            # Now check our custom language rules
            for i, line in enumerate(code.split('\n'), 1):
                line = line.strip()
                if not line:
                    continue
                    
                # Check db creation
                if re.match(r'^\w+\s*=\s*create_db\(.*\)\s*$', line):
                    if not re.match(r'^\w+\s*=\s*create_db\(["\'][^"\']*["\'](?:\s*,\s*\w+=\w+)?\)\s*$', line):
                        errors.append(f"Line {i}: Invalid create_db syntax. Expected: var = create_db(\"dbname\")")
                
                # Check table creation
                elif re.match(r'^\w+\s*=\s*create_table\(.*\)\s*$', line):
                    if not re.match(r'^\w+\s*=\s*create_table\(\w+(?:\s*,\s*["\'][^"\']*["\'])?\)\s*$', line):
                        errors.append(f"Line {i}: Invalid create_table syntax. Expected: var = create_table(db_var)")
                
                # Check insert_one
                elif re.search(r'\.insert_one\(.*\)\s*$', line):
                    if not re.search(r'\.insert_one\(\s*\{.*\}\s*\)\s*$', line):
                        errors.append(f"Line {i}: Invalid insert_one syntax. Expected: obj.insert_one({{...}})")
                
                # Check insert_many
                elif re.search(r'\.insert_many\(.*\)\s*$', line):
                    if not re.search(r'\.insert_many\(\s*\[.*\]\s*\)\s*$', line):
                        errors.append(f"Line {i}: Invalid insert_many syntax. Expected: obj.insert_many([...])")
                
                # Check delete operations
                elif re.search(r'\.delete_one\(.*\)\s*$', line) or re.search(r'\.delete_all\(.*\)\s*$', line):
                    if not re.search(r'\.(delete_one|delete_all)\(\s*\[.*\]\s*\)\s*$', line):
                        errors.append(f"Line {i}: Invalid delete syntax. Expected: obj.delete_X([condition])")
                
                # Check update operations
                elif re.search(r'\.update_one\(.*\)\s*$', line) or re.search(r'\.update_all\(.*\)\s*$', line):
                    if not re.search(r'\.(update_one|update_all)\(\s*\[.*\]\s*,\s*\[.*\]\s*\)\s*$', line):
                        errors.append(f"Line {i}: Invalid update syntax. Expected: obj.update_X([condition],[updates])")
                
                # Check for loop structure
                elif line.startswith("for "):
                    if not re.match(r'^for\s+\w+\s+in\s+\w+\s*:\s*$', line):
                        errors.append(f"Line {i}: Invalid for loop syntax. Expected: for item in collection:")
                
                # Check if statement structure
                elif line.startswith("if "):
                    # This is simplified - a real checker would be more complex for nested expressions
                    if not re.search(r'if\s+.*:\s*$', line):
                        errors.append(f"Line {i}: Invalid if statement syntax. Expected: if condition:")
            
            # Check for valid method calls with correct args (would require deeper AST analysis)
            method_calls = self._extract_method_calls(tree)
            for node, method_name in method_calls:
                if method_name in self.valid_methods:
                    expected_args = self.valid_methods[method_name]
                    if len(node.args) != expected_args:
                        errors.append(f"Line {node.lineno}: {method_name} expects {expected_args} arguments, got {len(node.args)}")
            
        except SyntaxError as e:
            errors.append(f"Python syntax error: {str(e)}")
        
        return errors
    
    def _extract_method_calls(self, tree):
        """Extract method calls from the AST."""
        method_calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                method_calls.append((node, node.func.attr))
        
        return method_calls

# Example usage
# checker = CustomLanguageSyntaxChecker()
# errors = checker.check_syntax(code)
# if errors:
#     for error in errors:
#         print(error)
# else:
#     print("Syntax is valid!")