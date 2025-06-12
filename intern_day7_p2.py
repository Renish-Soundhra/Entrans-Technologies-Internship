from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,EmailStr
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from typing import List

app=FastAPI()

class Greet(BaseModel):
    name:str

class Bmi(BaseModel):
    height:float
    weight:int

class Reverse(BaseModel):
    text:str

class Validate_email(BaseModel):
    email:EmailStr

class Student(BaseModel):
    name:str
    marks:List[int]

@app.get("/divide")
def div(num1:int,num2:int):
    if num2==0:
        raise HTTPException(status_code=400,detail="Cannot divide by zero")
    else:
        return {"message":num1/num2}

@app.get("/square/{num}")
def square_num(num:int):
    return {"result":num*num}

@app.post("/greet")
def greeting(greet:Greet):
    return {"message":f"Hello {greet.name}, welcome!"}

@app.get("/isprime/{num}")
def prime(num:int):
    if num<=1:
        return {"prime":False}
    for i in range (2,num//2+1,1):
        if num%i==0:
            return {"prime":False}
    return {"prime":True}

@app.post("/bmi")
def bmi_calculator(bmi:Bmi):
    if bmi.height<=0:
        raise HTTPException(status_code=400,detail="Height must be greater than 0")
    if bmi.weight<=0:
        raise HTTPException(status_code=400,detail="Weight must be greater than 0")
    res=round(bmi.weight/(bmi.height*bmi.height))
    if res>25:
        return {"BMI":res,"message":"Overweight"}
    elif res<18:
        return {"BMI":res,"message":"Underweight"}
    else:
        return {"BMI":res,"message":"Normal"}

@app.post("/reverse")
def rev_string(reverse:Reverse):
    return {"reversed":reverse.text[::-1]}

@app.get("/factorial/{num}")
def fact(num:int):
    def factorial(n):
        if n<=1:
            return 1
        else:
            return factorial(n-1)*n
    res=factorial(num)
    return {"factorial":res}

@app.post("/validate_email")
def email_validation(validate_email:Validate_email):
    return validate_email.email

@app.post("/report")
def generate_report(student:Student):
    avg=sum(student.marks)/len(student.marks)
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
    return {"Student name":student.name,
            "Total marks":sum(student.marks),
            "Average marks":avg,
            "Grade":gr}
    
