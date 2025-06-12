from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app=FastAPI()

class User(BaseModel):
    name:str
    age:int
    email:str

class User1(BaseModel):
    age:int

class User2(BaseModel):
    name:str
    age:int

class Product(BaseModel):
    name:str
    price:int
    tax:float

class Check(BaseModel):
    name:str
    instock:bool

class Login(BaseModel):
    username:str
    password:str

class Calculate(BaseModel):
    num1:int
    num2:int
    operation:str

class Grade(BaseModel):
    name:str
    marks:List[int]

class Product2(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

products_db=[]

class Product_update(BaseModel):
    id:int=None
    name:str=None
    price:float=None
    quantity:int=None
    
@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}

@app.get("/add/{num1}/{num2}")
def add(num1:int,num2:int):
    return {"sum":num1+num2}

@app.post("/user")
def add_user(user:User):
    return {"message":f"User {user.name} added successfully"}

@app.put("/user/{username}")
def update(username:str,ageup:User1):
    return {"message":f"User {username}'s age updated to {ageup.age}"}

@app.post("/product")
def tax(product:Product):
    return {f"name":{product.name},
            "price":{product.price},
            "tax":{product.tax},
            "total_price" : product.price*product.tax+product.price}

@app.post("/check")
def available(check:Check):
    if check.instock:
        return {"message":f"Product {check.name} is available"}
    else:
        return {"message":f"Product {check.name} is not available"}

@app.post("/register_users")
def register(user2:List[User2]):
    return {
        "message":f"{len(user2)} users registered successfully",
        "users":[{"name":user.name,"age":user.age} for user in user2]}

@app.post("/login")
def validate(login:Login):
    if login.username=="admin" and login.password=="1234":
        return {"message":"Login Successful"}
    else:
        return {"message":"Invalid credentials"}
    
@app.post("/calculate")
def calculator(calculate:Calculate):
    if calculate.operation=="add":
        return {"message":f"The addition of {calculate.num1} and {calculate.num2} gives {calculate.num1+calculate.num2}"}
    elif calculate.operation=="sub":
        return {"message":f"The subtraction of {calculate.num1} and {calculate.num2} gives {calculate.num1-calculate.num2}"}
    elif calculate.operation=="mul":
        return {"message":f"The multiplication of {calculate.num1} and {calculate.num2} gives {calculate.num1*calculate.num2}"}
    elif calculate.operation=="div":
        if calculate.num2==0:
            return {"message":"Division by zero is not allowed"}
        else:
            return {"message":f"The divition of {calculate.num1} and {calculate.num2} gives {calculate.num1/calculate.num2}"}
    else:
        return {"message":"Invalid operation"}

@app.post("/grade")
def calculate_grade(grade:Grade):
    avg=sum(grade.marks)/len(grade.marks)
    if avg>=90:
        gr="A"
    elif avg>=80:
        gr="B"
    elif avg>=70:
        gr="C"
    elif avg>=60:
        gr="D"
    else:
        gr="F"
    return {"Student name":grade.name,
            "Total marks":sum(grade.marks),
            "Average marks":avg,
            "Grade":gr}

@app.post("/product2")
def add(product2:Product2):
    products_db.append(product2.dict())
    return {"message":"Product added successfully"}

@app.get("/product2/{id}")
def get_product(id:int):
    for product in products_db:
        if product["id"]==id:
            return product
    return {"message":"Product not found"}

@app.put("/product2/{id}")
def update_product(id:int,update_data:Product_update):
    for product in products_db:
        if product["id"]==id:
            if update_data.id is not None:
                product["id"]=update_data.id
            if update_data.name is not None:
                product["name"]=update_data.name
            if update_data.price is not None:
                product["price"]=update_data.price
            if update_data.quantity is not None:
                product["quantity"]=update_data.quantity
            return {"message":"Product updated successfully"}
    return {"message":"Product not found"}

@app.delete("/product2/{id}")
def delete_product(id:int):
    for product in products_db:
        if product["id"]==id:
            products_db.remove(product)
            return {"message":"Product removed successfully"}
    return {"message":"Product not found"}

@app.get("/products2")
def get_all():
    return products_db
