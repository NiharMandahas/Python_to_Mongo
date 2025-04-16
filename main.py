import ast
import re
import json
from code_gen import CodeGenerator,MainGenerator
from Parser import MainVisitor,BaseVisitor,AssignmentVisitor,CallVisitor,LoopVisitor
from syntax_analyzer import CustomLanguageSyntaxChecker
from conditions_parser import convert_to_mongo_query,parse_set_statement
import time
import tracemalloc
import os

# code=''' 
# '''


start=time.time()

tracemalloc.start()


with open("test.py", "r") as file:
    code = file.read()

syntax_checker= CustomLanguageSyntaxChecker()
errors = syntax_checker.check_syntax(code)

if errors:
    for error in errors:
        print(error,color="red")



tree = ast.parse(code)


visitor = MainVisitor()
results = visitor.visit(tree)

with open("results.json", "w") as f:
    json.dump(results, f, indent=4)


obj= MainGenerator()
obj.generate_code()
obj.show_code()

os.remove("results.json")

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6:.2f} MB")
print(f"Peak memory usage: {peak / 10**6:.2f} MB")
tracemalloc.stop()


end=time.time()
print("Execution time:", end - start)