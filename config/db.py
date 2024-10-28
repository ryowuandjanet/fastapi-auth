from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pymongo.errors import ConnectionFailure
import asyncio

# 載入 .env 檔案
load_dotenv()

# 從環境變數獲取設定
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

async def check_connection():
    try:
        # 建立 MongoDB 連接
        client = AsyncIOMotorClient(MONGO_URL)
        
        # 驗證連接
        await client.admin.command('ping')
        server_info = await client.server_info()
        
        print("=== MongoDB Connection Info ===")
        print(f"✅ Successfully connected to MongoDB")
        print(f"📡 Server URL: {MONGO_URL}")
        print(f"📊 Database: {DATABASE_NAME}")
        print(f"🔧 MongoDB version: {server_info.get('version')}")
        print("============================")
        
        return client
        
    except ConnectionFailure as e:
        print("=== MongoDB Connection Error ===")
        print(f"❌ Failed to connect to MongoDB")
        print(f"📡 Server URL: {MONGO_URL}")
        print(f"❗ Error: {str(e)}")
        print("==============================")
        raise
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")
        raise

# 建立連接
client = AsyncIOMotorClient(MONGO_URL)
database = client[DATABASE_NAME]
user_collection = database.get_collection("users")

# 在應用啟動時執行連接檢查
if __name__ == "__main__":
    asyncio.run(check_connection())
