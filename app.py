import os
import json
import logging
import warnings
import time
import threading
from collections import OrderedDict
from urllib.parse import parse_qs, quote_plus

from flask import Flask, request, abort, render_template, jsonify

# -------------------- LINE SDK --------------------
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FlexSendMessage, FollowEvent, QuickReply, QuickReplyButton, MessageAction,
    PostbackEvent
)

# -------------------- requests / async for ShowLoadingAnimation --------------------
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures

# -------------------- dotenv --------------------
from dotenv import load_dotenv
if os.path.exists(".env.local"):
    load_dotenv(".env.local", override=True)

APP_ENV = os.getenv("APP_ENV", "local")
if APP_ENV == "prod":
    print("🚀 使用 .env.prod 設定")
    if os.path.exists(".env.prod"):
        load_dotenv(".env.prod", override=True)
else:
    print("🛠 使用 .env.local 設定")

# -------------------- 讀取 LINE 設定 --------------------
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

# ✅ 分成兩組 LIFF（追蹤物件 / 預約賞屋）
LIFF_ID_SUBSCRIBE = os.getenv("LIFF_ID_SUBSCRIBE", "")
LIFF_ID_BOOKING   = os.getenv("LIFF_ID_BOOKING", "")

LIFF_URL_SUBSCRIBE = f"https://liff.line.me/{LIFF_ID_SUBSCRIBE}" if LIFF_ID_SUBSCRIBE else ""
LIFF_URL_BOOKING   = f"https://liff.line.me/{LIFF_ID_BOOKING}"   if LIFF_ID_BOOKING   else ""

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("❌ 請先設定 LINE_CHANNEL_ACCESS_TOKEN 與 LINE_CHANNEL_SECRET 環境變數")

# -------------------- 基本設定 --------------------
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# -------------------- Firebase 初始化 --------------------
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    raw_json = os.getenv("FIREBASE_CREDENTIALS")
    raw_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
    try:
        if raw_json:
            cred = credentials.Certificate(json.loads(raw_json))
            log.info("✅ 使用 FIREBASE_CREDENTIALS JSON 初始化成功")
        elif raw_file and os.path.exists(raw_file):
            cred = credentials.Certificate(raw_file)
            log.info(f"✅ 使用 FIREBASE_CREDENTIALS_FILE ({raw_file}) 初始化成功")
        else:
            raise RuntimeError("❌ 缺少 FIREBASE_CREDENTIALS 或 FIREBASE_CREDENTIALS_FILE")
        firebase_admin.initialize_app(cred)
    except Exception:
        log.exception("❌ Firebase 初始化失敗")
        raise

db = firestore.client()

# -------------------- Flex Templates --------------------
import flex_templates as ft
from flex_templates import property_flex, listing_card

# -------------------- Tiny Cache --------------------
class TinyTTLCache:
    def __init__(self, maxsize=256, ttl=30):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache = OrderedDict()
        self.lock = threading.RLock()
    def get(self, key):
        now = time.time()
        with self.lock:
            if key in self.cache:
                val, ts = self.cache[key]
                if now - ts < self.ttl:
                    self.cache.move_to_end(key)
                    return val
                else:
                    self.cache.pop(key, None)
        return None
    def set(self, key, val):
        with self.lock:
            self.cache[key] = (val, time.time())
            self.cache.move_to_end(key)
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

_detail_cache = TinyTTLCache(maxsize=256, ttl=30)

# -------------------- 表單頁面 --------------------
@app.route("/setting", methods=["GET"])
def show_form():
    return render_template("setting_form.html")

@app.route("/search", methods=["GET"])
def show_search_form():
    return render_template("search_form.html")

@app.route("/share")
def share_page():
    return render_template("share.html")

@app.route("/booking")
def booking():
    return render_template("booking_form.html")

# -------------------- 追蹤物件表單提交 --------------------
@app.route("/submit_form", methods=["POST"])
def submit_form():
    try:
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        budget = data.get("budget")
        room   = data.get("room")
        genre  = data.get("genre")
        user_id= data.get("user_id")

        if not user_id:
            return jsonify({"status": "error", "message": "missing user_id"}), 400

        doc_ref = db.collection("forms").document(user_id)
        existed = doc_ref.get().exists

        payload = {"budget": budget, "room": room, "genre": genre, "user_id": user_id,
                   "updated_at": firestore.SERVER_TIMESTAMP}
        if not existed:
            payload["created_at"] = firestore.SERVER_TIMESTAMP
        doc_ref.set(payload, merge=True)

        title = "🎉 追蹤成功！" if not existed else "條件已更新"
        card = ft.manage_condition_card(budget, room, genre, LIFF_URL_SUBSCRIBE)
        line_bot_api.push_message(user_id, FlexSendMessage(alt_text=title, contents=card))
        return jsonify({"status": "success"}), 200
    except Exception as e:
        log.exception("[submit_form] error")
        return jsonify({"status": "error", "message": str(e)}), 500

# -------------------- 查詢物件 --------------------
@app.route("/submit_search", methods=["POST"])
def submit_search():
    try:
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        user_id = data.get("user_id")
        budget  = data.get("budget")
        room    = data.get("room")
        genre   = data.get("genre")

        log.info(f"[submit_search] 收到 user_id={user_id}, budget={budget}, room={room}, genre={genre}")

        if not user_id:
            return jsonify({"status": "error", "message": "❌ 缺少 user_id"}), 400

        # Firestore 查 listings 集合
        query = db.collection("listings")
        if room and room != "0":  
            query = query.where("room", "==", int(room))
        if genre:
            query = query.where("genre", "==", genre)

        docs = list(query.stream())
        log.info(f"[submit_search] 找到 {len(docs)} 筆 listings (未過濾價格)")

        # 預算範圍解析
        min_budget, max_budget = None, None
        if budget:
            try:
                if "-" in budget:
                    parts = budget.replace("萬", "").split("-")
                    min_budget, max_budget = int(parts[0]), int(parts[1])
                elif "以下" in budget:
                    max_budget = int(budget.replace("萬以下", ""))
                elif "以上" in budget:
                    min_budget = int(budget.replace("萬以上", ""))
            except Exception as e:
                log.warning(f"[submit_search] 預算解析失敗: {e}")

        # Python 過濾價格
        bubbles = []
        for d in docs:
            data = d.to_dict()
            price = data.get("price")
            if price is not None:
                if min_budget and price < min_budget:
                    continue
                if max_budget and price > max_budget:
                    continue
            try:
                bubbles.append(ft.listing_card(d.id, data))
            except Exception as e:
                log.error(f"[submit_search] listing_card 失敗 doc_id={d.id}, error={e}")

        if not bubbles:
            line_bot_api.push_message(user_id, TextSendMessage(text="❌ 沒有符合條件的物件"))
        else:
            flex_message = {"type": "carousel", "contents": bubbles[:10]}
            line_bot_api.push_message(user_id, FlexSendMessage(alt_text="搜尋結果", contents=flex_message))

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        log.exception("[submit_search] error")
        return jsonify({"status": "error", "message": str(e)}), 400

# -------------------- 預約賞屋表單 --------------------
@app.route("/submit_booking", methods=["POST"])
def submit_booking():
    try:
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        house_id   = data.get("house_id")
        house_title= data.get("house_title")
        name       = data.get("name")
        phone      = data.get("phone")
        timeslot   = data.get("timeslot")
        user_id    = data.get("user_id")

        if not (house_id and name and phone and timeslot and user_id):
            return jsonify({"status": "error", "message": "缺少必要欄位"}), 400

        db.collection("appointments").document().set({
            "house_id": house_id, "house_title": house_title,
            "name": name, "phone": phone, "timeslot": timeslot, "user_id": user_id,
            "status": "pending", "created_at": firestore.SERVER_TIMESTAMP
        })

        line_bot_api.push_message(user_id, TextSendMessage(text=f"✅ 已收到您的預約\n物件：{house_title}\n時段：{timeslot}\n我們將盡快與您聯繫 📞"))
        return jsonify({"status": "success"}), 200
    except Exception as e:
        log.exception("[submit_booking] error")
        return jsonify({"status": "error", "message": str(e)}), 500

# -------------------- PostbackEvent (物件詳情) --------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    params = parse_qs(data or "")
    action = (params.get("action") or [None])[0]
    house_id = (params.get("id") or [None])[0]

    if action == "detail" and house_id:
        user_id = getattr(event.source, "user_id", None)
        source_type = getattr(event.source, "type", "unknown")

        if source_type == "user" and user_id:
            pass  # 可選擇是否要顯示 loading 動畫

        cache_key = f"listing:{house_id}"
        house = _detail_cache.get(cache_key)
        if house is None:
            doc = db.collection("listings").document(house_id).get()
            if not doc.exists:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 找不到物件資訊"))
                return
            house = doc.to_dict() or {}
            _detail_cache.set(cache_key, house)

        try:
            try:
                flex_json = property_flex(house_id, house, LIFF_URL_BOOKING)
            except TypeError:
                flex_json = property_flex(house_id, house)
        except Exception as e:
            log.error(f"[Postback] 產生 Flex 失敗, house_id={house_id}, error={e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 物件詳情載入失敗"))
            return

        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text=f"物件詳情：{house.get('title', house_id)}", contents=flex_json))

# -------------------- Debug push --------------------
@app.route("/debug/push/<user_id>")
def debug_push(user_id):
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text="✅ 測試 Push 成功！"))
        return "ok"
    except Exception as e:
        return f"❌ Push 失敗: {e}", 500

# -------------------- Callback --------------------
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        log.error("[callback] Invalid signature")
        abort(400)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running."

@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok"

# -------------------- 啟動 --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
