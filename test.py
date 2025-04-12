mydb = create_db("myDB")
users = create_table("myTable", mydb)
users.insert_one({"key": "value","age":324})
users.insert_many({"key1": "value1"}, {"key2": "value2"})


for obj in users:
    if age >18 and age<30 or age!=25:
        print(obj)
   
users.delete_entry(["age>18 and age<30 or age==25"])
users.update_entry({"key": "age > 30","key2":5}, {"key2": "new_value"})
users.delete_table()
mydb.delete()