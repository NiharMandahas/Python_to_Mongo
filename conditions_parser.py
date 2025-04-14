import json


def convert_to_mongo_query(condition):
    # Handle None case
    if condition is None:
        return {}
    
    # Strip surrounding brackets and quotes if present
    if isinstance(condition, str):
        # Remove ["'....'"] format
        if condition.startswith("['") and condition.endswith("']"):
            condition = condition[2:-2]
        # Remove regular quotes
        elif (condition.startswith('"') and condition.endswith('"')) or (condition.startswith("'") and condition.endswith("'")):
            condition = condition[1:-1]
    
    def clean_value(val):
        val = val.strip()
        if val.isdigit():
            return int(val)
        # Try to convert to float
        try:
            return float(val)
        except ValueError:
            pass
        # Remove surrounding quotes if they exist
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            return val[1:-1]
        return val
    
    # Handle dictionary case (as before)
    if isinstance(condition, dict):
        op = condition.get("op")
        values = condition.get("values", [])
        value = condition.get("value")
        
        if op == "and":
            return {"$and": [convert_to_mongo_query(val) for val in values]}
        elif op == "or":
            return {"$or": [convert_to_mongo_query(val) for val in values]}
        elif op == "not":
            return {"$not": convert_to_mongo_query(value if value is not None else (values[0] if values else {}))}
        return condition  # fallback for other dict cases
    
    # Handle string case with compound conditions
    elif isinstance(condition, str):
        # Check for AND/OR operators in the string
        if " and " in condition.lower():
            parts = condition.lower().split(" and ")
            return {"$and": [convert_to_mongo_query(part) for part in parts]}
        elif " or " in condition.lower():
            parts = condition.lower().split(" or ")
            return {"$or": [convert_to_mongo_query(part) for part in parts]}
        
        # Handle individual conditions
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
        elif ">=" in condition:  # Add this case for >= operator
            field, value = condition.split(">=")
            field = field.strip()
            value = clean_value(value)
            return {field: {"$gte": value}}
        elif "<=" in condition:  # Add this case for <= operator
            field, value = condition.split("<=")
            field = field.strip()
            value = clean_value(value)
            return {field: {"$lte": value}}
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
    
    return {}    




def parse_set_statement(set_str):
    set_dict = {}
    try:
        # Split by comma to get each assignment
        assignments = set_str.split(',')
        for assign in assignments:
            if '=' in assign:
                key, value = assign.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Try to parse int, float, or strip quotes for strings
                if value.isdigit():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                            value = value[1:-1]
                        else:
                            pass  # Keep it as-is if it's something unknown

                set_dict[key] = value
    except Exception as e:
        print("Error parsing set statement:", e)
    
    return {"$set": set_dict}
