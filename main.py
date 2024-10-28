from fastapi import FastAPI
from routes.user import router as user_router
from config.db import client, check_connection
import uvicorn

app = FastAPI()

# 啟動事件
@app.on_event("startup")
async def startup_db_client():
    await check_connection()

# 關閉事件
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    print("📤 Closed MongoDB connection")

# 註冊路由
app.include_router(user_router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with MongoDB"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
