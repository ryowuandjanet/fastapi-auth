from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError
from models.user import UserCreate, UserLogin, Token, PasswordReset, NewPassword
from config.auth import create_access_token, verify_password, get_password_hash
from config.email import send_reset_password_email
import secrets

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=Token)
async def register(request: Request, user: UserCreate):
    # 檢查郵箱是否已存在
    if await request.app.database["users"].find_one({"email": user.email}):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # 創建新用戶
    user_dict = user.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict["password"])
    del user_dict["password"]
    
    await request.app.database["users"].insert_one(user_dict)
    
    # 創建訪問令牌
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# 保留原有的表單登入端點
@router.post("/token", response_model=Token)
async def login_form(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await request.app.database["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# 新增 JSON 格式的登入端點
@router.post("/login", response_model=Token)
async def login_json(request: Request, user_data: UserLogin):
    user = await request.app.database["users"].find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(request: Request, password_reset: PasswordReset):
    user = await request.app.database["users"].find_one({"email": password_reset.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 生成重置令牌
    reset_token = secrets.token_urlsafe(32)
    reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    
    # 更新用戶的重置令牌
    await request.app.database["users"].update_one(
        {"email": password_reset.email},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expires": reset_token_expires
        }}
    )
    
    # 發送重置郵件
    await send_reset_password_email(password_reset.email, reset_token)
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(request: Request, new_password: NewPassword):
    # 查找具有有效重置令牌的用戶
    user = await request.app.database["users"].find_one({
        "reset_token": new_password.token,
        "reset_token_expires": {"$gt": datetime.utcnow()}
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # 更新密碼並清除重置令牌
    hashed_password = get_password_hash(new_password.new_password)
    await request.app.database["users"].update_one(
        {"_id": user["_id"]},
        {
            "$set": {"hashed_password": hashed_password},
            "$unset": {"reset_token": "", "reset_token_expires": ""}
        }
    )
    
    return {"message": "Password updated successfully"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # 這裡可以實現令牌黑名單機制
    return {"message": "Successfully logged out"}
