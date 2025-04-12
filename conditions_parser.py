import json


def convert_to_mongo_query(condition):
    def clean_value(val):
        val = val.strip()
        if val.isdigit():
            return int(val)
        # Remove surrounding quotes if they exist
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            return val[1:-1]
        return val

    if isinstance(condition, str):
        if "==" in condition:
            field, value = condition.split("==")
            field = field.strip()
            value = clean_value(value)
            return {field: value}
        elif "!=" in condition:
            field, value = condition.split("!=")
            field = field.strip()
            value = clean_value(value)
            return {field: {"$ne": value}}
        elif ">" in condition:
            field, value = condition.split(">")
            field = field.strip()
            value = clean_value(value)
            return {field: {"$gt": value}}
        elif "<" in condition:
            field, value = condition.split("<")
            field = field.strip()
            value = clean_value(value)
            return {field: {"$lt": value}}
        else:
            return condition  # fallback

    elif isinstance(condition, dict):
        op = condition.get("op")
        values = condition.get("values", [])

        if op == "and":
            return {"$and": [convert_to_mongo_query(val) for val in values]}
        elif op == "or":
            return {"$or": [convert_to_mongo_query(val) for val in values]}
        elif op == "not":
            return {"$not": convert_to_mongo_query(values[0] if isinstance(values, list) else values)}

    return {}

    

# with open('results.json', 'r') as file:
#     conditions = json.load(file)
#     for method_call in conditions["method_calls"]:
#         if "conditions" in method_call:
#             formatted_condition = convert_to_mongo_query(method_call["conditions"])
#             print(formatted_condition)
        
#     for functions_call in conditions["loops"]:
#         if "conditions" in functions_call:
#             formatted_condition = convert_to_mongo_query(functions_call["conditions"])
#             print(formatted_condition)

