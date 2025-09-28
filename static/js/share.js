// 🔹 Firebase Config
const firebaseConfig = {
  apiKey: "你的-APIKEY", // ⚠️ 必填，換成 Firebase Console 裡的
  authDomain: "dabin-house-viewing-2c4f0.firebaseapp.com",
  projectId: "dabin-house-viewing-2c4f0"
};
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// 取得網址參數
function getQueryParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

async function main() {
  try {
    // 初始化 LIFF
    await liff.init({ liffId: LIFF_ID });
    console.log("✅ LIFF 初始化成功");

    if (!liff.isLoggedIn()) {
      liff.login();
      return;
    }

    // 取得 doc_id
    const docId = getQueryParam("doc_id");
    if (!docId) {
      document.getElementById("status").innerText = "❌ 缺少 doc_id 參數";
      return;
    }

    // 從 Firestore 抓資料
    const snap = await db.collection("listings").doc(docId).get();
    if (!snap.exists) {
      document.getElementById("status").innerText = "❌ 找不到物件資料";
      return;
    }

    const data = snap.data();

    // Flex Message
    const flexMessage = {
      type: "flex",
      altText: `分享物件：${data.title || "好宅"}`,
      contents: {
        type: "bubble",
        size: "mega",
        hero: {
          type: "image",
          url: data.image_url || "https://picsum.photos/800/520",
          size: "full",
          aspectRatio: "20:13",
          aspectMode: "cover"
        },
        body: {
          type: "box",
          layout: "vertical",
          contents: [
            { type: "text", text: data.title || "未命名物件", weight: "bold", size: "lg" },
            { type: "text", text: data.address || "-", size: "sm", color: "#7B7B7B" },
            { type: "text", text: `${data.square_meters || "?"}坪｜${data.genre || "-"}`, size: "sm", color: "#555555" },
            { type: "text", text: `${data.price || "?"} 萬 (含車位)`, size: "xxl", weight: "bold", color: "#FF5809" }
          ]
        },
        footer: {
          type: "box",
          layout: "vertical",
          spacing: "md",
          contents: [
            {
              type: "button",
              style: "primary",
              color: "#F5A627",
              action: {
                type: "uri",
                label: "物件詳情請至LINE@搜尋",
                uri: "https://line.me/R/ti/p/999mxdib" // ⚠️ 改成你的 LINE 官方帳號 ID
              }
            }
          ]
        }
      }
    };

    // 分享
    document.getElementById("status").innerText = "載入完成，正在開啟分享...";
    await liff.shareTargetPicker([flexMessage]);
    setTimeout(() => liff.closeWindow(), 1200);

  } catch (err) {
    console.error("❌ LIFF 初始化失敗:", err);
    document.getElementById("status").innerText =
      "⚠️ LIFF 初始化失敗：" + JSON.stringify(err);
  }
}

main();
