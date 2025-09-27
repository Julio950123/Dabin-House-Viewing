// =====================
// search.js
// =====================

const LIFF_ID = "2007720984-Wdoapz3B"; // ⚠️ 換成你的 LIFF ID

async function initLiff() {
  try {
    await liff.init({ liffId: LIFF_ID });

    if (!liff.isLoggedIn()) {
      liff.login();
      return;
    }

    const profile = await liff.getProfile();
    document.getElementById("user_id").value = profile.userId;
    console.log("✅ 取得 user_id:", profile.userId);

  } catch (error) {
    console.error("❌ LIFF 初始化失敗:", error);
    alert("⚠️ LIFF 初始化失敗，請重新開啟連結");
  }
}

document.getElementById("searchForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const payload = {
    user_id: document.getElementById("user_id").value,
    budget: document.getElementById("budget").value,
    room: document.getElementById("room").value,
    genre: document.getElementById("genre").value,
  };

  console.log("📤 送出搜尋條件:", payload);

  try {
    let res = await fetch("/submit_search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await res.json();
    console.log("📥 後端回傳結果:", result);

    if (res.ok && result.status === "success") {
      // 🔹 在 LINE APP 內：關閉 LIFF 視窗
      if (liff.isInClient()) {
        console.log("🔒 LIFF 視窗即將關閉");
        liff.closeWindow();
      } else {
        // 🔹 在瀏覽器測試：導向感謝頁
        console.log("🌐 Browser 模式 → 導向 /thank-you");
        window.location.href = "/thank-you";
      }
    } else {
      alert("送出失敗，請稍後再試");
    }
  } catch (err) {
    console.error("❌ 表單送出錯誤:", err);
    alert("送出失敗，請稍後再試");
  }
});

// 🚀 初始化 LIFF
initLiff();
