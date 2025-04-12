import ast
import json
from conditions_parser import convert_to_mongo_query, parse_set_statement


code = '''
mydb = create_db("myDB")
users = create_table(mydb)
users.insert_one({"key": "value","age":324})
users.insert_many([{"key1": "value1"}, {"key2": "value2"}])


for obj in users:
    if obj["Rating"]> 4.5 or obj["Rating"]==5:
        print(obj)
   
users.delete_one(["age>18 and age<30 or age!=25"])

users.delete_all(["age>18 and age<30 or age!=25 and something=='nihar'"])

users.update_one(["age > 30 and key2==5"],["something = 100 , something_else='nihar' "])
users.update_all(["age > 30 and key2==5"],["something = 100"])


users.delete_table()
mydb.delete()
'''



# with open("test.py", "r") as file:
#     code = file.read()

tree = ast.parse(code)


# Base visitor class
class BaseVisitor(ast.NodeVisitor):
    def __init__(self):
        self.results = []
    
    def get_results(self):
        return self.results

# Assignment visitor
class AssignmentVisitor(BaseVisitor):
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                assignment_info = {"target": target.id}
                
                # Handle assignment value
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        assignment_info["type"] = "function_call"
                        assignment_info["function"] = node.value.func.id
                    elif isinstance(node.value.func, ast.Attribute):
                        assignment_info["type"] = "method_call"
                        assignment_info["method"] = node.value.func.attr
                elif isinstance(node.value, ast.Name):
                    assignment_info["type"] = "variable"
                    assignment_info["source"] = node.value.id
                elif isinstance(node.value, ast.Constant):
                    assignment_info["type"] = "constant"
                    assignment_info["value"] = node.value.value
                
                self.results.append(assignment_info)
        
        self.generic_visit(node)




# Function/Method call visitor
class CallVisitor(BaseVisitor):
    def __init__(self):
        super().__init__()
        self.function_calls = []
        self.method_calls = []

    def extract_condition_structure(self,expr):
        if isinstance(expr, ast.BoolOp):
            op_type = type(expr.op)
            if op_type == ast.And:
                op_str = "and"
            elif op_type == ast.Or:
                op_str = "or"
            else:
                op_str = "unknown"

            return {
                "op": op_str,
                "values": [self.extract_condition_structure(value) for value in expr.values]
            }

        elif isinstance(expr, ast.UnaryOp):
            # Handle `not <expr>`
            if isinstance(expr.op, ast.Not):
                return {
                    "op": "not",
                    "value": self.extract_condition_structure(expr.operand)
                }

        elif isinstance(expr, ast.Compare):
            return ast.unparse(expr)

        else:
            return ast.unparse(expr)  # Fallback for any unknown cases

    def visit_Call(self, node):
        call_info = {
            "args": [],
            "kwargs": {}
        }

        for arg in node.args:
            if isinstance(arg, ast.Constant):
                call_info["args"].append(arg.value)
            elif isinstance(arg, ast.Dict):
                call_info["args"].append(ast.literal_eval(arg))
            elif isinstance(arg, ast.Name):
                call_info["args"].append(arg.id)
            else:
                call_info["args"].append(ast.unparse(arg))

        for keyword in node.keywords:
            key = keyword.arg
            val = keyword.value
            if isinstance(val, ast.Constant):
                call_info["kwargs"][key] = val.value
            elif isinstance(val, ast.Name):
                call_info["kwargs"][key] = val.id
            else:
                call_info["kwargs"][key] = ast.unparse(val)

        # Separate logic for functions vs methods
        if isinstance(node.func, ast.Name):
            call_info["type"] = "function_call"
            call_info["name"] = node.func.id
            self.function_calls.append(call_info)

        elif isinstance(node.func, ast.Attribute):
            expr_str = None
            set_statement= None
            if len(node.args) > 0:
                first_arg = node.args[0]
                second_arg=node.args[1] if len(node.args) > 1 else None

                if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                    expr_str = first_arg.value

                elif isinstance(first_arg, ast.List) and len(first_arg.elts) > 0:
                    first_elt = first_arg.elts[0]
                    if isinstance(first_elt, ast.Constant) and isinstance(first_elt.value, str):
                        expr_str = first_elt.value
                
                if isinstance(second_arg,ast.List) and len(second_arg.elts) > 0:
                    second_elt = second_arg.elts[0]
                    if isinstance(second_elt, ast.Constant) and isinstance(second_elt.value, str):
                        set_statement = second_elt.value
                

            if expr_str:
                try:
                    parsed_expr = ast.parse(expr_str, mode='eval').body
                    call_info["conditions"] = convert_to_mongo_query(self.extract_condition_structure(parsed_expr))
                except Exception as e:
                    call_info["condition_parse_error"] = str(e)
            
            # print(set_statement)
            if set_statement:
                try:
                    parsed_set_statement = parse_set_statement(set_statement)
                    call_info["set_statement"] = parsed_set_statement
                except Exception as e:
                    call_info["set_statement_parse_error"] = str(e)

            call_info["type"] = "method_call"
            call_info["method"] = node.func.attr
            call_info["object"] = ast.unparse(node.func.value)
            self.method_calls.append(call_info)


        self.generic_visit(node)

    def get_results(self):
        return {
            "function_calls": self.function_calls,
            "method_calls": self.method_calls
        }


# Loop visitor
class LoopVisitor(BaseVisitor):
    def extract_condition_structure(self,expr):
        if isinstance(expr, ast.BoolOp):
            op_type = type(expr.op)
            if op_type == ast.And:
                op_str = "and"
            elif op_type == ast.Or:
                op_str = "or"
            else:
                op_str = "unknown"

            return {
                "op": op_str,
                "values": [self.extract_condition_structure(value) for value in expr.values]
            }

        elif isinstance(expr, ast.UnaryOp):
            # Handle `not <expr>`
            if isinstance(expr.op, ast.Not):
                return {
                    "op": "not",
                    "value": self.extract_condition_structure(expr.operand)
                }

        elif isinstance(expr, ast.Compare):
            return ast.unparse(expr)

        else:
            return ast.unparse(expr)  # Fallback for any unknown cases
        
    def visit_For(self, node):

        if_is_present = (
            isinstance(node.body[0], ast.If)
        )

        # condition_expr = node.body[0].test if if_is_present else None

        condition_expr = (
            node.body[0].test
            if node.body and isinstance(node.body[0], ast.If)
            else None
        )

        loop_info = {
            "type": "for_loop",
            "target": ast.unparse(node.target),
            "iterable": ast.unparse(node.iter),
            "if_is_present": if_is_present,
            "condition_raw": ast.unparse(condition_expr) if condition_expr else None,
            "conditions": convert_to_mongo_query(self.extract_condition_structure(condition_expr) if condition_expr else None),
            "body_size": len(node.body)
        }


        self.results.append(loop_info)
        self.generic_visit(node)

    
    def visit_While(self, node):
        loop_info = {
            "type": "while_loop",
            "body_size": len(node.body)
        }
        self.results.append(loop_info)
        self.generic_visit(node)



# Main visitor that uses the specialized visitors
class MainVisitor:
    def __init__(self):
        self.assignment_visitor = AssignmentVisitor()
        self.call_visitor = CallVisitor()
        self.loop_visitor = LoopVisitor()
    
    def visit(self, tree):
        self.assignment_visitor.visit(tree)
        self.call_visitor.visit(tree)
        self.loop_visitor.visit(tree)
        
        assignment = self.assignment_visitor.get_results()
        calls = self.call_visitor.get_results()  # Now a dict
        loops = self.loop_visitor.get_results()
        
        return {
            "assignments": assignment,
            "function_calls": calls["function_calls"],
            "method_calls": calls["method_calls"],
            "loops": loops
        }


# Print the AST for reference
print(ast.dump(tree, indent=6))

# Use the visitors
visitor = MainVisitor()
results = visitor.visit(tree)

with open("results.json", "w") as f:
    json.dump(results, f, indent=4)