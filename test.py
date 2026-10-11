from fastapi import FastAPI
import random
from pydantic import BaseModel, EmailStr


app = FastAPI()

users_db = {}


class Users(BaseModel):
    name:str
    age:int
    surname:str
    email:EmailStr


#get all users information
@app.get("/users")
def get_users():
    return users_db

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return users_db.get(user_id, {"error": "user not found"})

#add users
@app.post("/users")
def create_User(user: Users):
    return {"user ",user.name, user.surname, user.age,user.email,  " Created!" }

