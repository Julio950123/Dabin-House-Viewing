import firebase_admin
from firebase_admin import credentials, firestore

# 1. 初始化 Firebase (用你下載的金鑰 JSON)
cred = credentials.Certificate("dabin-house-viewing-2c4f0-firebase-adminsdk-fbsvc-b6616d3d51.json")  # ⚠️ 改成你的金鑰檔案名稱
firebase_admin.initialize_app(cred)

# 2. 建立 Firestore 連線
db = firestore.client()

# 3. 寫入一筆測試資料
doc_ref = db.collection("forms").add({
    "budget": "1500-2000萬",
    "room": "3房",
    "genre": "電梯大樓",
    "user_id": "TEST_USER",
    "created_at": firestore.SERVER_TIMESTAMP
})

print("✅ 測試成功，已新增文件:", doc_ref)