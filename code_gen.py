import json
import ast


class CodeGenerator:
    def __init__(self):
        with open('results.json', 'r') as file:
            self.parsed_text = json.load(file)
        self.code = ""

    def generate_assignment_code(self):

        for  assignment in self.parsed_text["assignments"]:
            for function_call in self.parsed_text["function_calls"]:
                if assignment["function"] == function_call["name"] == "create_db":
                    self.code+= f"use {function_call['args'][0]}\n"
                elif assignment["function"] == function_call["name"] == "create_table":
                    self.code+= f"db.createCollection('{assignment["target"]}');\n"
        
    def generate_drop_code(self):
        for method in self.parsed_text["method_calls"]:
            if method["method"]=="delete_table":
                self.code+= f"db.{method["object"]}.drop();\n"
            elif method["method"]=="delete":
                self.code+= "db.dropDatabase();\n"
        

    def generate_insert_code(self):
        for method in self.parsed_text["method_calls"]:
            if method["method"] == "insert_one":
                self.code += f"db.{method['object']}.insertOne({method['args'][0]});\n"
            elif method["method"] == "insert_many":
                elements = ", ".join([str(item) for item in method["args"]])
                self.code += f"db.{method['object']}.insertMany({elements});\n"
    
    def generate_update_code(self):
        for method in self.parsed_text["method_calls"]:
            if method["method"] == "update_one":
                self.code+=f"db.{method["object"]}.updateOne({method["conditions"]}, {method["set_statement"]});\n"
            elif method["method"] == "update_all":
                self.code+=f"db.{method["object"]}.updateMany({method["conditions"]}, {method["set_statement"]});\n"
            
    def generate_delete_code(self):
        for method in self.parsed_text["method_calls"]:
            if method["method"] == "delete_one":
                self.code+=f"db.{method["object"]}.deleteOne({method["conditions"]});\n"
            elif method["method"] == "delete_all":
                self.code+=f"db.{method["object"]}.deleteMany({method["conditions"]});\n"



    def generate_query_code(self):
        for loop in self.parsed_text["loops"]:
            if loop["type"] == "for_loop":
                self.code+=f"printjson(db.{loop["iterable"]}.find({loop["conditions"]}).toArray());\n"
        
    def show_code(self):
        with open("output.txt", "w") as file:
            file.write(self.code)
        # print(self.code)



class MainGenerator(CodeGenerator):
    def __init__(self):
        super().__init__()
        self.code = ""

    def generate_code(self):
        self.generate_assignment_code()
        self.generate_insert_code()
        self.generate_update_code()
        self.generate_delete_code()
        self.generate_query_code()
        self.generate_drop_code()
        return self.code

# obj= MainGenerator()
# obj.generate_code()
# obj.show_code()

