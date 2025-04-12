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
