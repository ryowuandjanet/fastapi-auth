from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    name: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "secretpassword"
            }
        }

