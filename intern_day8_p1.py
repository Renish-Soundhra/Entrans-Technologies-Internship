from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional

app=FastAPI()

client=MongoClient("mongodb://localhost:27017/")
db=client["bookdb"]
col=db["books"]

class Book(BaseModel):
    title:str
    author:str

class Book_update(BaseModel):
    title:Optional[str]=None
    author:Optional[str]=None

@app.get("/books/{title}")
def find(title:str):
    book=col.find_one({"title":title})
    if book:
        book["_id"]=str(book["_id"])
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books")
def add_book(book:Book):
    if col.find_one({"title":book.title}):
        raise HTTPException(status_code=400, detail="Book already exists")
    col.insert_one(book.dict())
    return {"message":"Book added successfully"}

@app.put("/books/{title}")
def update(title:str,updated_data:Book_update):
    book=col.find_one({"title":title})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_fields={k:v for k,v in updated_data.dict().items() if v is not None}
    if not update_fields:
        return {"message":"No fields provided for update"}

    col.update_one({"title":title},{"$set":update_fields})
    return {"message":"Book updated successfully"}

@app.delete("/books/{title}")
def delete_book(title:str):
    book=col.delete_one({"title":title})
    if book.deleted_count==0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message":"Book deleted successfully"}
    
    
