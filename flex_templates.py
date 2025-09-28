# flex_templates.py
"""
集中管理 Flex Message 模板
"""

from typing import Dict, Any

# -------------------- Buyer (我的追蹤條件卡片) --------------------
def buyer_card(liff_url: str) -> Dict[str, Any]:
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "我們會依您「房型×預算×類型」\n在未來有符合您需求的物件時\n第一時間通知您",
                    "size": "sm",
                    "wrap": True,
                    "margin": "md",
                },
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#EB941E",
                    "height": "sm",
                    "action": {"type": "uri", "label": "設定追蹤條件", "uri": "https://liff.line.me/2007720984-AYJY7nWQ"},
                }
            ],
        },
    }


# -------------------- Seller (賣方回覆文字) --------------------
def seller_text() -> str:
    return "好的，請留下您的姓名及電話\n我將盡速與您聯繫"


# -------------------- Manage Condition (追蹤條件卡片) --------------------
def manage_condition_card(budget: str, room: str, genre: str, liff_url: str) -> Dict[str, Any]:
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "當前追蹤條件",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#333333",
                    "margin": "sm"
                },
                {"type": "separator", "margin": "xs"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "md",
                    "contents": [
                        {"type": "text", "text": f"預算：{budget or '-'}", "size": "md", "wrap": True},
                        {"type": "text", "text": f"格局：{room or '-'}", "size": "md", "wrap": True},
                        {"type": "text", "text": f"類型：{genre or '-'}", "size": "md", "wrap": True}
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": "#EB941E",
                    "action": {"type": "uri", "label": "更改追蹤條件", "uri": "https://liff.line.me/2007720984-AYJY7nWQ"}
                }
            ]
        }
    }


# -------------------- Search (搜尋入口卡片) --------------------
def search_card() -> dict:
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "搜尋你的理想好屋",
                                "uri": "https://liff.line.me/2007720984-Wdoapz3B"
                            },
                            "color": "#ffffff",
                            "height": "sm"
                        }
                    ],
                    "backgroundColor": "#EB941E",
                    "cornerRadius": "5px",
                    "spacing": "xs"
                }
            ],
            "spacing": "xs"
        }
    }


# -------------------- Intro (房仲介紹卡片) --------------------
def intro_card() -> dict:
    return {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "size": "mega",
                # Hero 區塊 (頭貼圖片)
                "hero": {
                    "type": "image",
                    "size": "80%",
                    "aspectMode": "cover",
                    "aspectRatio": "1:1",
                    "url": "https://res.cloudinary.com/daj9nkjd1/image/upload/v1757148957/%E9%A0%AD%E8%B2%BC_a1gz5t.png"
                },
                # Body 區塊 (文字與標籤)
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "金牌房仲", "weight": "bold", "align": "center", "size": "20px"},
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
                        # Footer (CTA 按鈕)
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
                                    "backgroundColor": "#EB941E",
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
                                    "action": {"type": "uri", "label": "action", "uri": "tel:0937339406"}
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


# -------------------- Utils (安全文字處理) --------------------
def safe_str(value, default="-"):
    """確保 Flex 的 text 一定是字串"""
    return str(value) if value not in [None, ""] else default


# -------------------- Listing Card (單筆物件卡片) --------------------
# -------------------- PostbackEvent (物件詳情) --------------------
def listing_card(doc_id: str, data: dict) -> dict:
    image_url = safe_str(
        data.get("image_url"),
        "https://picsum.photos/800/520?random=1"
    )
    return {
        "type": "bubble",
        "size": "mega",

        # Hero 區塊 (物件圖片)
        "hero": {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },

        # Body 區塊
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "offsetTop": "0px",
            "contents": [

                # 地址列
                {
                    "type": "box",
                    "layout": "horizontal",
                    "offsetEnd": "5px",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
                            "size": "15px",
                            "flex": 8,
                            "offsetTop": "3px"
                        },
                        {
                            "type": "text",
                            "text": safe_str(data.get("address")),
                            "flex": 90,
                            "color": "#7B7B7B"
                        }
                    ]
                },

                # 標題
                {
                    "type": "text",
                    "text": safe_str(data.get("title")),
                    "weight": "bold",
                    "size": "25px",
                    "offsetBottom": "2px"
                },

                # 坪數 + 類型
                {
                    "type": "text",
                    "text": f"{safe_str(data.get('square_meters'))}坪｜{safe_str(data.get('genre'))}",
                    "size": "18px",
                    "color": "#555555",
                    "margin": "5px",
                    "offsetBottom": "2px"
                },

                # Detail1 + Detail2 標籤
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "margin": "5px",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "cornerRadius": "5px",
                            "backgroundColor": "#e7e8e7",
                            "height": "30px",
                            "alignItems": "center",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": safe_str(data.get("detail1")),
                                    "align": "center",
                                    "color": "#7B7B7B"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "cornerRadius": "5px",
                            "backgroundColor": "#e7e8e7",
                            "height": "30px",
                            "alignItems": "center",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": safe_str(data.get("detail2")),
                                    "align": "center",
                                    "color": "#7B7B7B"
                                }
                            ]
                        }
                    ]
                },

                # 價格列
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "5px",
                    "offsetTop": "5px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "（含車位價格）",
                            "size": "15px",
                            "weight": "bold",
                            "color": "#7B7B7B",
                            "align": "end",
                            "gravity": "bottom",
                            "offsetBottom": "5px"
                        },
                        {
                            "type": "text",
                            "text": f"{safe_str(data.get('price'), '0')}萬",
                            "size": "30px",
                            "weight": "bold",
                            "color": "#FF5809",
                            "margin": "5px",
                            "align": "end",
                            "flex": 0
                        }
                    ]
                },

                {
                    "type": "separator",
                    "margin": "5px"
                },

                # Footer 按鈕 (詳情 / 分享)
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "button",
                            "height": "sm",
                            "flex": 50,
                            "color": "#EE9226",
                            "style": "primary",
                            "action": {
                                "type": "postback",
                                "label": "物件詳情",
                                "data": f"action=detail&id={doc_id}"
                            }
                        },
                        {
                            "type": "button",
                            "height": "sm",
                            "flex": 25,
                            "color": "#9D9D9D",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "分享",
                                "uri": f"https://liff.line.me/2007720984-L3DXgr6m?doc_id={doc_id}"
                            }
                        }
                    ]
                },

                # 備註文字
                {
                    "type": "text",
                    "text": "物件以現場與權狀為主",
                    "align": "center",
                    "size": "13px",
                    "color": "#7B7B7B",
                    "offsetTop": "3px"
                }
            ]
        }
    }



# -------------------- Listings Carousel (多頁物件卡片) --------------------
import urllib.parse

# ----------------- 共用工具函式 -----------------
def normalize_text(raw: str) -> str:
    if not raw:
        return ""
    return raw.replace("\\n\\n", "\n\n").replace("\\n", "\n").strip()

def safe_str(val, default=""):
    if val is None:
        return default
    return str(val)

def property_flex(doc_id: str, data: dict) -> dict:
    """回傳物件詳情的 Flex Message (三個 bubble)"""

    # 固定 booking LIFF URL
    LIFF_URL_BOOKING = "https://liff.line.me/2007720984-0vG5xWAw"

    # 格式化文字
    text = normalize_text(data.get("text", ""))

    # 組合 booking_url（帶 id & title）
    title = data.get("title", "")
    title_encoded = urllib.parse.quote(title)
    booking_url = f"{LIFF_URL_BOOKING}?id={doc_id}&title={title_encoded}"


    return {
        "type": "carousel",
        "contents": [

            # ----------------- Bubble 1：封面卡 -----------------
            {
                "type": "bubble",
                "size": "mega",
                "hero": {
                    "type": "image",
                    "url": data.get("image_url", "https://picsum.photos/800/520"),
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "offsetTop": "0px",
                    "contents": [

                        # 地址
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "offsetEnd": "5px",
                            "contents": [
                                {
                                    "type": "image",
                                    "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
                                    "size": "15px",
                                    "flex": 8,
                                    "offsetTop": "3px"
                                },
                                {
                                    "type": "text",
                                    "text": data.get("address", "-"),
                                    "flex": 90,
                                    "color": "#7B7B7B"
                                }
                            ]
                        },

                        # 標題
                        {
                            "type": "text",
                            "text": data.get("title", "未命名物件"),
                            "weight": "bold",
                            "size": "25px",
                            "offsetBottom": "2px"
                        },

                        # 坪數 + 類型
                        {
                            "type": "text",
                            "text": f'{data.get("square_meters", "?")}坪｜{data.get("genre", "-")}',
                            "size": "18px",
                            "margin": "5px",
                            "offsetBottom": "2px"
                        },

                        # 標籤 (detail1, detail2)
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "md",
                            "margin": "5px",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "cornerRadius": "5px",
                                    "backgroundColor": "#e7e8e7",
                                    "height": "30px",
                                    "alignItems": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": data.get("detail1", ""),
                                            "align": "center",
                                            "color": "#7B7B7B"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "cornerRadius": "5px",
                                    "backgroundColor": "#e7e8e7",
                                    "height": "30px",
                                    "alignItems": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": data.get("detail2", ""),
                                            "align": "center",
                                            "color": "#7B7B7B"
                                        }
                                    ]
                                }
                            ]
                        },

                        # 價格
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "5px",
                            "offsetTop": "5px",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "（含車位價格）",
                                    "size": "15px",
                                    "weight": "bold",
                                    "color": "#7B7B7B",
                                    "align": "end",
                                    "gravity": "bottom",
                                    "offsetBottom": "5px"
                                },
                                {
                                    "type": "text",
                                    "text": f"{safe_str(data.get('price'), '0')}萬",
                                    "size": "30px",
                                    "weight": "bold",
                                    "color": "#FF5809",
                                    "margin": "5px",
                                    "align": "end",
                                    "flex": 0
                                }
                            ]
                        },

                        {
                            "type": "separator",
                            "margin": "5px"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "預約賞屋",
                                "uri": booking_url
                            },
                            "color": "#EE9226",
                            "style": "primary",
                            "margin": "md",
                            "height": "sm"
                        },
                        {
                            "type": "text",
                            "text": "物件以現場與權狀為主",
                            "align": "center",
                            "size": "13px",
                            "color": "#7B7B7B",
                            "margin": "sm",
                            "offsetTop": "3px"
                        }
                    ]
                }
            },

            # ----------------- Bubble 2：格局卡 -----------------
            {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [

                        # 標題 + 獨家專任
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "lg",
                            "alignItems": "center",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": data.get("project_name", ""),
                                    "size": "30px",
                                    "flex": 0
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "cornerRadius": "5px",
                                    "borderColor": "#307B91",
                                    "borderWidth": "1px",
                                    "alignItems": "center",
                                    "flex": 0,
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": data.get("exclusive", ""),
                                            "color": "#307B91"
                                        }
                                    ]
                                }
                            ]
                        },

                        {
                            "type": "separator",
                            "color": "#165161",
                            "margin": "md"
                        },

                        # 格局
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "md",
                            "spacing": "xl",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "格局",
                                    "color": "#8A8F91",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": data.get("pattern", "")
                                }
                            ]
                        },

                        # 屋齡 + 樓高
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "md",
                            "spacing": "xl",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "屋齡",
                                    "color": "#8A8F91",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": data.get("old", ""),
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": "樓高",
                                    "color": "#8A8F91",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": data.get("height", "")
                                }
                            ]
                        },

                        # 坪數
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "md",
                            "spacing": "xl",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "權狀坪數",
                                    "color": "#8A8F91",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": f'{data.get("square_meters2", "")} (不含車位)'
                                }
                            ]
                        },

                        # 格局圖
                        {
                            "type": "image",
                            "url": data.get("pattern_url", "https://picsum.photos/800/520"),
                            "size": "full"
                        },

                        # 影片 + 導航
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "md",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "uri",
                                        "label": "用影片看更多",
                                        "uri": data.get("video_uri", "http://linecorp.com/")
                                    },
                                    "color": "#EE9226",
                                    "style": "primary",
                                    "flex": 50,
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "uri",
                                        "label": "導航",
                                        "uri": data.get("map_uri", "http://maps.google.com/")
                                    },
                                    "color": "#9D9D9D",
                                    "style": "primary",
                                    "flex": 25,
                                    "height": "sm"
                                }
                            ]
                        }
                    ]
                }
            },

            # ----------------- Bubble 3：完整文案 -----------------
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": text,   # ✅ 使用處理過的文字
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }




# -------------------- Export --------------------
__all__ = [
    "buyer_card",
    "seller_text",
    "manage_condition_card",
    "intro_card",
    "listing_card",
    "search_card",
    "listings_to_carousel",
]

