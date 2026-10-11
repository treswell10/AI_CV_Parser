from fastapi import FastAPI
from pydantic import BaseModel

class UserClass(BaseModel):
    name: str
    age: int


app = FastAPI()


@app.post("/users")
def create_user(user: UserClass):
    return {"message": f"User {user.name} of age {user.age} created successfully!"}