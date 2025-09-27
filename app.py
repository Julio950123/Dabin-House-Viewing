import os
import json
import logging
import warnings
import time
import threading
from collections import OrderedDict
from urllib.parse import parse_qs

from flask import Flask, request, abort, render_template, jsonify

# -------------------- LINE SDK --------------------
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
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

# LIFF Apps
LIFF_ID_SUBSCRIBE = os.getenv("LIFF_ID_SUBSCRIBE", "")
LIFF_ID_BOOKING   = os.getenv("LIFF_ID_BOOKING", "")

LIFF_URL_SUBSCRIBE = f"https://liff.line.me/{LIFF_ID_SUBSCRIBE}"
LIFF_URL_BOOKING   = f"https://liff.line.me/{LIFF_ID_BOOKING}"

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

# -------------------- 表單頁面 --------------------
@app.route("/setting", methods=["GET"])
def show_form():
    return render_template("setting_form.html")

@app.route("/search", methods=["GET"])
def show_search_form():
    return render_template("search_form.html")

@app.route("/share")
def share_page():
    """LIFF 分享頁面"""
    return render_template("share.html")

@app.route("/booking")
def booking():
    return render_template("booking_form.html")
       
# -------------------- Flex Templates --------------------
import flex_templates as ft

def get_top_flex():
    docs = db.collection("listings").where("top", "==", True).limit(5).stream()
    bubbles = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        try:
            bubble = ft.listing_card(doc.id, data)
            if bubble:
                bubbles.append(bubble)
        except Exception as e:
            log.error(f"[get_top_flex] 產生 Flex 失敗: {e}")
    if not bubbles:
        return None
    return {"type": "carousel", "contents": bubbles}

# -------------------- 非阻塞 Loading：session + 執行緒池 --------------------
_session = requests.Session()
_retries = Retry(total=2, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
_adapter = HTTPAdapter(pool_connections=10, pool_maxsize=50, max_retries=_retries)
_session.mount("https://", _adapter)
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

def _post_loading(chat_id: str, seconds: int):
    try:
        url = "https://api.line.me/v2/bot/chat/loading/start"
        headers = {
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        s = max(5, min(60, int(round((seconds or 5) / 5.0) * 5)))
        payload = {"chatId": chat_id, "loadingSeconds": s}
        r = _session.post(url, headers=headers, json=payload, timeout=(1, 1.5))
        log.info(f"[loading] {r.status_code} payload={payload}")
    except Exception as e:
        log.warning(f"[loading] fail: {e}")

def send_loading_animation_async(user_id: str, seconds: int = 5):
    if not user_id:
        return
    _executor.submit(_post_loading, user_id, seconds)

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

# -------------------- LINE Bot MessageEvent --------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()
    user_id = event.source.user_id
    log.info(f"[handle_message] 收到訊息: {repr(msg)} user_id={user_id}")

    if msg == "高鐵生活圈精選":
        flex = get_top_flex()
        if flex:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="精選物件", contents=flex)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="目前沒有精選物件 🙏")
            )

    elif msg == "委託賣房":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ft.seller_text()))

    elif msg == "立即找房":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="立即找房", contents=ft.search_card())
        )

    elif msg == "你是誰":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="你是誰", contents=ft.intro_card())
        )

    elif msg == "管理我的追蹤條件":
        doc = db.collection("forms").document(user_id).get()

        if doc.exists:
            data = doc.to_dict() or {}
            budget = data.get("budget", "-")
            room   = data.get("room", "-")
            genre  = data.get("genre", "-")

            log.info(
                f"[manage_condition] user_id={user_id}, "
                f"budget={budget}, room={room}, genre={genre}, "
                f"LIFF_URL_SUBSCRIBE={LIFF_URL_SUBSCRIBE}"
            )

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="管理我的追蹤條件",
                    contents=ft.manage_condition_card(budget, room, genre, LIFF_URL_SUBSCRIBE),
                ),
            )
        else:
            log.info(
                f"[manage_condition] user_id={user_id}, 尚未填過表單 → 顯示 buyer_card"
            )
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="我想買房",
                    contents=ft.buyer_card(LIFF_URL_SUBSCRIBE),
                ),
            )

# -------------------- FollowEvent --------------------
@handler.add(FollowEvent)
def handle_follow(event):
    welcome_text = (
        "我可以協助你：\n"
        "✔ 快速尋找適合的物件\n"
        "✔ 新上架 24hr 搶先通知\n\n"
        "請點下方【精選推薦】"
    )
    quick_reply = TextSendMessage(
        text=welcome_text,
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="立即找房", text="立即找房")),
                QuickReplyButton(action=MessageAction(label="委託賣房", text="委託賣房")),
            ]
        ),
    )
    line_bot_api.reply_message(event.reply_token, quick_reply)

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
        # 嘗試解析 JSON 或表單
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        
        # Debug log
        log.info(f"[submit_search] 測試收到資料: {data}")

        # 回傳 echo 給前端確認
        return jsonify({
            "status": "ok",
            "echo": data
        }), 200

    except Exception as e:
        log.exception("[submit_search] 測試錯誤")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/submit_search", methods=["POST"])
def submit_search():
    try:
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        budget = data.get("budget")
        room   = data.get("room")
        genre  = data.get("genre")
        user_id= data.get("user_id")

        log.info(f"[submit_search] data={data}")

        if not user_id:
            return jsonify({"status": "error", "message": "missing user_id"}), 400

        db.collection("search_form").document().set({
            "budget": budget,
            "room": room,
            "genre": genre,
            "user_id": user_id,
            "created_at": firestore.SERVER_TIMESTAMP
        })

        query = db.collection("listings")
        if budget and "-" in budget:
            min_budget, max_budget = budget.split("-")
            min_budget, max_budget = int(min_budget), int(max_budget)
            if min_budget > 0:
                query = query.where("price", ">=", min_budget)
            if max_budget < 99999:
                query = query.where("price", "<=", max_budget)
        if room and room.isdigit() and int(room) > 0:
            query = query.where("room", "==", int(room))
        if genre and genre != "不限":
            query = query.where("genre", "==", genre)

        docs = query.limit(5).stream()
        bubbles = []
        for doc in docs:
            house = doc.to_dict() or {}
            try:
                bubbles.append(ft.listing_card(doc.id, house))
            except Exception as e:
                log.error(f"[submit_search] listing_card error, id={doc.id}, e={e}")

        if bubbles:
            carousel = {"type": "carousel", "contents": bubbles}
            line_bot_api.push_message(user_id, FlexSendMessage(alt_text="找到物件", contents=carousel))
        else:
            line_bot_api.push_message(user_id, TextSendMessage(text="❌ 沒有符合的物件"))

        return jsonify({"status": "success"}), 200

    except Exception as e:
        log.exception("[submit_search] error")
        return jsonify({"status": "error", "message": str(e)}), 500
    
# -------------------- 預約賞屋表單 --------------------
@app.route("/api/booking", methods=["POST"])
def api_booking():
    try:
        data = request.get_json(force=True)
        log.info(f"[api_booking] 收到資料: {data}")

        user_id     = data.get("userId")
        displayName = data.get("displayName", "")
        name        = data.get("name", "")
        phone       = data.get("phone", "")
        timeslot    = data.get("timeslot", "")
        house_id    = data.get("houseId", "")
        house_title = data.get("houseTitle", "")

        if not user_id:
            log.error("[api_booking] 缺少 userId")
            return jsonify({"status": "error", "message": "missing userId"}), 400

        # ---------------- Firestore ----------------
        db.collection("bookings").document().set({
            "userId": user_id,
            "displayName": displayName,
            "name": name,
            "phone": phone,
            "timeslot": timeslot,
            "houseId": house_id,
            "houseTitle": house_title,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        log.info("[api_booking] ✅ Firestore 寫入成功")

        # ---------------- Flex 卡片 ----------------
        success_card = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": "✅ 預約成功！", "weight": "bold", "size": "lg", "color": "#EB941E"},
                    {"type": "text", "text": f"物件：{house_title}", "wrap": True},
                    {"type": "text", "text": f"姓名：{name}", "wrap": True},
                    {"type": "text", "text": f"電話：{phone}", "wrap": True},
                    {"type": "text", "text": f"時段：{timeslot}", "wrap": True},
                    {"type": "separator", "margin": "md"},
                    {"type": "text", "text": "我們將盡快與您聯繫 🙏", "align": "center", "color": "#555555", "size": "sm"}
                ]
            }
        }

        # ---------------- Push LINE ----------------
        try:
            line_bot_api.push_message(
                user_id,
                FlexSendMessage(alt_text="預約成功！", contents=success_card)
            )
            log.info(f"[api_booking] ✅ Push 成功 user_id={user_id}")
        except Exception as e:
            log.exception(f"[api_booking] ❌ Push 失敗 user_id={user_id}, error={e}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        log.exception("[api_booking] error")
        return jsonify({"status": "error", "message": str(e)}), 500
    
# -------------------- 測試 --------------------
@app.route("/debug/push/<user_id>")
def debug_push(user_id):
    try:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text="✅ 測試 Push 成功！")
        )
        return "ok"
    except Exception as e:
        return f"❌ Push 失敗: {e}", 500


# -------------------- PostbackEvent (物件詳情) --------------------
from flex_templates import property_flex

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    log.info(f"[PostbackEvent] data={data}")

    params = parse_qs(data or "")
    action = (params.get("action") or [None])[0]
    house_id = (params.get("id") or [None])[0]

    log.info(f"[PostbackEvent] action={action}, house_id={house_id}")

    if action == "detail" and house_id:
        user_id = getattr(event.source, "user_id", None)
        source_type = getattr(event.source, "type", "unknown")
        if source_type == "user" and user_id:
            send_loading_animation_async(user_id, 5)

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
            flex_json = property_flex(house_id, house)
        except Exception as e:
            log.error(f"[PostbackEvent] property_flex error: {e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 物件詳情載入失敗"))
            return

        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text=f"物件詳情：{house.get('title', house_id)}",
                contents=flex_json
            )
        )

# -------------------- 基礎路由 --------------------
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running."

@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    log.info(f"[callback] body={body}")  # ✅ debug log
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        log.error("[callback] Invalid signature")
        abort(400)
    return "OK"

# -------------------- 啟動 --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
