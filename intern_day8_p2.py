from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,EmailStr,Field
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
from fastapi.security import  HTTPBearer
from fastapi import Depends, Security
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import List,Optional
from bson import ObjectId

Client=MongoClient("mongodb://localhost:27017/")
Db=Client["Users_db"]
Col=Db["User_info"]
ItemsCol=Db["Items_info"]

app=FastAPI()

PwdContext=CryptContext(schemes=["bcrypt"], deprecated="auto")

SecretKey = "mysecretkey"
Algorithm = "HS256"

Oauth2Scheme = HTTPBearer()

class UserIn(BaseModel):
    UserName:str
    Password:str
    Email:EmailStr

class UserInDB(BaseModel):
    UserName:str
    HashedPassword:str
    Email:EmailStr


class User(BaseModel):
    UserName:str
    Password:str

class ItemIn(BaseModel):
    Name:str
    Price:int

class Item(BaseModel):
    Name:str
    id:str= Field(..., alias="_id")
    Price:int
    Owner:Optional[str]
    class Config:
        validate_by_name = True

class RegisterResponse(BaseModel):
    Message:str

class LoginResponse(BaseModel):
    AccessToken:str
    TokenType:str
    Message:str

class CreateResponse(BaseModel):
    Message:str
    item:Item

class UpdateResponse(BaseModel):
    Message:str
    item:Item

class DeleteResponse(BaseModel):
    Message:str
    item:Item
    
def HashPassword(Password: str):
    return PwdContext.hash(Password)

def VerifyPassword(PlainPassword: str, HashedPassword: str):
    return PwdContext.verify(PlainPassword, HashedPassword)

def CreateAccessToken(data: dict):
    InputData = data.copy()
    Expire = datetime.utcnow() + timedelta(minutes=30)
    InputData.update({"exp": Expire})
    EncodedJwt = jwt.encode(InputData, SecretKey, algorithm=Algorithm)
    return EncodedJwt

def VerifyToken(Credentials: HTTPAuthorizationCredentials = Security(Oauth2Scheme)):
    Token = Credentials.credentials
    CredentialsException = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        PayLoad = jwt.decode(Token, SecretKey, algorithms=[Algorithm])
        UserName = PayLoad.get("sub")
        if UserName is None:
            raise CredentialsException
        return UserName
    except JWTError:
        raise CredentialsException

@app.post("/register",response_model=RegisterResponse)
def Register(user: UserIn):
    if Col.find_one({"UserName":user.UserName}):
        raise HTTPException(status_code=400, detail="User already exists")
    if Col.find_one({"Email":user.Email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    HashedPw=HashPassword(user.Password)
    UserDb=UserInDB(UserName=user.UserName, HashedPassword=HashedPw, Email=user.Email)
    Col.insert_one(UserDb.dict())
    return RegisterResponse(Message="User registered successfully")

@app.post("/login",response_model=LoginResponse)
def login(user:User):
    User1=Col.find_one({"UserName":user.UserName})
    if not User1:
        raise HTTPException(status_code=404, detail="User not found")
    if not VerifyPassword(user.Password,User1["HashedPassword"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    accessToken=CreateAccessToken(data={"sub":user.UserName})
    return LoginResponse(AccessToken=accessToken,TokenType="bearer",Message="Login successful")

@app.post("/item/",response_model=CreateResponse)
def CreateItem(item: ItemIn, CurrentUser: str = Depends(VerifyToken)):
    ExistingItem = ItemsCol.find_one({"Name": item.Name, "Owner": CurrentUser})
    if ExistingItem:
        raise HTTPException(status_code=400, detail="Item with this name already exists for the current user")
    ItemData = item.dict()
    ItemData["Owner"] = CurrentUser
    ItemsCol.insert_one(ItemData)
    finditem=ItemsCol.find_one({"Name":ItemData["Name"],"Owner":ItemData["Owner"]})
    return CreateResponse(Message="Item created successfully",item=Item(Name=finditem["Name"],id=str(finditem["_id"]),Price=finditem["Price"],Owner=finditem["Owner"]))

@app.get("/items/",response_model=List[Item])
def ReadItems(CurrentUser: str = Depends(VerifyToken)):
    UserItem = list(ItemsCol.find({"Owner": CurrentUser}))
    UserItems=[]
    for doc in UserItem:
        item = Item(
            Name=doc["Name"],
            id=str(doc["_id"]),
            Price=doc["Price"],
            Owner=doc["Owner"]
        )
        UserItems.append(item)
    return UserItems

@app.get("/items/{id}/",response_model=Item)
def FindItem(id: str, CurrentUser:str=Depends(VerifyToken)):
    try:
        objId = ObjectId(id.strip())
    except:
        raise HTTPException(status_code=400, detail="Invalid Id format")
    Result=ItemsCol.find_one({"_id":objId,"Owner":CurrentUser})
    if not Result:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(Name=Result["Name"],id=str(Result["_id"]),Price=Result["Price"],Owner=Result["Owner"])

@app.put("/items/{id}",response_model=UpdateResponse)
def UpdateItem(id: str, item: ItemIn, CurrentUser: str = Depends(VerifyToken)):
    try:
        objId=ObjectId(id.strip())
    except:
        raise HTTPException(status_code=400, detail="Invalid Id format")
    Result = ItemsCol.update_one(
        {"_id": objId, "Owner": CurrentUser},
        {"$set": item.dict()}
    )
    if Result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated=ItemsCol.find_one({"_id": objId, "Owner": CurrentUser})
    return UpdateResponse(Message="Item updated successfully",item=Item(Name=updated["Name"],id=str(updated["_id"]),Price=updated["Price"],Owner=updated["Owner"]))

@app.delete("/items/{id}",response_model=DeleteResponse)
def DeleteItem(id: str, CurrentUser: str = Depends(VerifyToken)):
    try:
        objId=ObjectId(id.strip())
    except:
        raise HTTPException(status_code=400, detail="Invalid Id format")
    Result = ItemsCol.find_one({"_id": objId, "Owner": CurrentUser})
    if not Result:
        raise HTTPException(status_code=404, detail="Item not found")
    ItemsCol.delete_one({"_id":objId,"Owner":CurrentUser})
    return DeleteResponse(Message="Item deleted successfully",item=Item(Name=Result["Name"],id=str(Result["_id"]),Price=Result["Price"],Owner=Result["Owner"]))
