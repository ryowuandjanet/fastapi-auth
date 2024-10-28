from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# 基本用戶模型
class UserBase(BaseModel):
    email: EmailStr = Field(...)
    name: str = Field(...)

# 用於創建用戶
class UserCreate(UserBase):
    password: str = Field(...)

# 用於登入
class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

# 用於資料庫中的用戶
class User(UserBase):
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "is_active": True
            }
        }

# 用於響應的用戶模型
class UserResponse(UserBase):
    id: str = Field(...)
    created_at: datetime
    is_active: bool

# Token 相關模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# 密碼重置相關模型
class PasswordReset(BaseModel):
    email: EmailStr

class NewPassword(BaseModel):
    token: str
    new_password: str
