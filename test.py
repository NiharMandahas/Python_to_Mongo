mydb = create_db("myDB")
users = create_table("myTable", mydb)
users.insert_one({"key": "value","age":324})
users.insert_many({"key1": "value1"}, {"key2": "value2"})


for obj in users:
    if obj.age >18 and obj.age<30 or obj.age==25:
        print(obj)

users.delete()
mydb.delete()