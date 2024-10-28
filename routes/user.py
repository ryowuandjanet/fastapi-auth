from fastapi import APIRouter, Body, Request, HTTPException, status
from models.user import User
from typing import List

router = APIRouter()

@router.post("/", response_description="Create a new user")
async def create_user(request: Request, user: User = Body(...)):
    user = user.dict()
    new_user = await request.app.mongodb_client["fastapi_db"]["users"].insert_one(user)
    created_user = await request.app.mongodb_client["fastapi_db"]["users"].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user

@router.get("/", response_description="List all users")
async def list_users(request: Request):
    users = []
    for doc in await request.app.mongodb_client["fastapi_db"]["users"].find().to_list(length=100):
        users.append(doc)
    return users

@router.get("/{id}", response_description="Get a single user")
async def show_user(id: str, request: Request):
    if (user := await request.app.mongodb_client["fastapi_db"]["users"].find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=404, detail=f"User {id} not found")

