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