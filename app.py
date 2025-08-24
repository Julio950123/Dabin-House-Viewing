# app.py
import os
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FollowEvent, QuickReply, QuickReplyButton, MessageAction
)

def must_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing environment variable: {name}")
    return v

app = Flask(__name__)

# 從環境變數讀取（Render → Environment 中設定）
CHANNEL_ACCESS_TOKEN = must_env("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = must_env("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.get("/")
def health():
    return "OK", 200

@app.post("/callback")
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400, "Invalid signature")
    return "OK"

@handler.add(FollowEvent)
def handle_follow(event):
    text = (
        "歡迎加入張大彬的 LINE！\n"
        "我可以協助你：\n"
        "✔ 找適合的房子\n"
        "✔ 分析物件行情\n"
        "✔ 協助你賣房找買家！\n\n"
        "請選擇您的身分："
    )
    qr = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="我是買家", text="我是買家")),
        QuickReplyButton(action=MessageAction(label="我是賣家", text="我是賣家")),
    ])
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text, quick_reply=qr)
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    msg = (event.message.text or "").strip()
    if msg == "我是買家":
        reply = "收到～買家服務啟動 ✅\n請告訴我：預算／房型／區域。"
    elif msg == "我是賣家":
        reply = "收到～賣家服務啟動 ✅\n請提供：地點／建物型態／期望售價。"
    else:
        reply = "輸入「我是買家」或「我是賣家」開始；或直接敘述你的需求。"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)