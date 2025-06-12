import pymongo

client1=pymongo.MongoClient("mongodb://localhost:27017/")
db1=client1["studentdb"]
col1=db1["student_details"]

def add_update_detail():
    name=input("Enter name:")
    rollno=int(input("Enter roll no:"))
    email=input("Enter email:")
    if col1.find_one({"rollno":rollno}):
        print("Student with this rollno already exists")
        option=input("Do you want to update(y/n)")
        if option=="y":
            new_email=input("Enter new email(press enter if you dont want to):")
            new_name=input("Enter new name(press enter if you dont want to):")
            update_fields={}
            if new_email:
                update_fields["email"]=new_email
            if new_name:
                update_fields["name"]=new_name
            if update_fields:
                col1.update_one({"rollno":rollno}, {"$set":update_fields})
                print("Contact updated")
            else:
                print("No updates")
        else:
            return
    else:
        col1.insert_one({"name":name,"rollno":rollno,"email":email})
        print("Student added successfully")

def search_detail():
    name=input("Enter the name to search:")
    results=col1.find({"name": {"$regex": name, "$options": "i"}})
    flag=False
    for r in results:
        print(r)
        flag=True
    if not flag:
        print("No such student")

def display_detail():
    for s in col1.find():
        print(s)

def delete_detail():
    name=input("Enter the name of the student to be deleted:")
    if name:
        col1.delete_one({"name":name})
        print("Student detail deleted successfully:")
    else:
        print("Nothing deleted")

while True:
    print("Student Database")
    print("1.add_update_detail")
    print("2.search_detail")
    print("3.display_detail")
    print("4.delete_detail")
    print("5.exit")
    choice=input("Enter your choice:")
    if choice=="1":
        add_update_detail()
    elif choice=="2":
        search_detail()
    elif choice=="3":
        display_detail()
    elif choice=="4":
        delete_detail()
    elif choice=="5":
        print("Exited Successfully")
        break
    else:
        print("Invalid choice. Try again.")
