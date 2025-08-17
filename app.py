from flask import Flask, request, abort
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
import os

app = Flask(__name__)

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Firebase 設定
FIREBASE_PROJECT_ID = "house-c82d9"
FIREBASE_DB_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running."

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook Error:", e)
        abort(400)
    return "OK"

from linebot.models import FollowEvent, QuickReply, QuickReplyButton, MessageAction

@handler.add(FollowEvent)
def handle_follow(event):
    quick_reply = TextSendMessage(
        text="歡迎加入張大彬的 LINE！\n"
        "我可以協助你：\n"
        "✔ 找適合的房子\n"
        "✔ 分析物件行情\n"
        "✔ 協助你賣房找買家！\n\n"
        "請選擇您的身分：",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(label="我是買家", text="我是買家")
                ),
                QuickReplyButton(
                    action=MessageAction(label="我是賣家", text="我是賣家")
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, quick_reply)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()

    
    if msg == "你是誰":
        flex_intro = {
            "type": "carousel",
            "contents": [
                {
                    "type": "bubble",
                    "size": "mega",
                    "hero": {
                        "type": "image",
                        "size": "80%",
                        "aspectMode": "cover",
                        "aspectRatio": "1:1",
                        "margin": "none",
                        "url": "https://res.cloudinary.com/daj9nkjd1/image/upload/v1753039495/%E5%A4%A7%E5%BD%AC%E7%9C%8B%E6%88%BF_%E9%A0%AD%E8%B2%BC_%E5%B7%A5%E4%BD%9C%E5%8D%80%E5%9F%9F_1_addzrg.jpg"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "張大彬 Leo", "weight": "bold", "align": "center", "size": "20px"},
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "text", "text": "新世代自媒體", "color": "#7B7B7B"}],
                                        "backgroundColor": "#D0D0D0",
                                        "cornerRadius": "5px",
                                        "height": "23px",
                                        "justifyContent": "center",
                                        "maxWidth": "49%",
                                        "alignItems": "center"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "text", "text": "優質資深房仲", "color": "#7B7B7B"}],
                                        "backgroundColor": "#D0D0D0",
                                        "alignItems": "center",
                                        "cornerRadius": "5px",
                                        "height": "23px",
                                        "justifyContent": "center",
                                        "maxWidth": "49%"
                                    }
                                ],
                                "justifyContent": "space-between"
                            },
                            {"type": "text", "text": "桃園市中壢區", "size": "20px", "weight": "bold", "color": "#FF8000", "margin": "10px"},
                            {"type": "text", "text": "擁有多年的房地產經驗\n平時也經營 TikTok、YouTube   用影片分析房市趨勢，也分享生活趣事\n\n想買房、換屋，或了解市場，都歡迎與我聊聊！", "size": "15px", "wrap": True, "margin": "10px"},
                            {"type": "separator", "color": "#101010", "margin": "15px"},
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "text", "text": "用影片更認識我", "color": "#ffffff"}],
                                        "height": "30px",
                                        "maxWidth": "69%",
                                        "backgroundColor": "#FF8000",
                                        "cornerRadius": "5px",
                                        "justifyContent": "center",
                                        "alignItems": "center"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "text", "text": "通話", "color": "#ffffff"}],
                                        "height": "30px",
                                        "maxWidth": "29%",
                                        "backgroundColor": "#7B7B7B",
                                        "cornerRadius": "5px",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "action": {
                                            "type": "uri",
                                            "label": "action",
                                            "uri": "tel:0918837739"
                                        }
                                    }
                                ],
                                "justifyContent": "space-between",
                                "margin": "15px"
                            }
                        ]
                    }
                }
            ]
        }

        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="我是誰", contents=flex_intro)
        )




if __name__ == "__main__":
    app.run(debug=True)
