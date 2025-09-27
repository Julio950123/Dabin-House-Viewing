// booking.js
document.addEventListener("DOMContentLoaded", async () => {
  try {
    // 1. 初始化 LIFF
    await liff.init({ liffId: "2007720984-0vG5xWAw" }); // ✅ 固定 ID

    // 2. 解析 URL 參數
    const urlParams = new URLSearchParams(window.location.search);
    const houseId = urlParams.get("id") || "";
    const houseTitle = urlParams.get("title") || "";

    // 3. 預填表單
    if (houseId) document.getElementById("houseId").value = houseId;
    if (houseTitle) document.getElementById("houseTitle").value = decodeURIComponent(houseTitle);

    // 4. 綁定送出事件
    document.getElementById("bookingForm").addEventListener("submit", async (e) => {
      e.preventDefault();

      try {
        const profile = await liff.getProfile();

        const payload = {
          userId: profile.userId,
          displayName: profile.displayName,
          name: document.getElementById("name").value.trim(),
          phone: document.getElementById("phone").value.trim(),
          timeslot: document.getElementById("timeslot").value,
          houseId: houseId,
          houseTitle: decodeURIComponent(houseTitle),
          createdAt: new Date().toISOString()
        };

        const res = await fetch("/api/booking", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          liff.closeWindow();
        } else {
          throw new Error("提交失敗");
        }
      } catch (err) {
        console.error("[bookingForm] error:", err);
        alert("❌ 發生錯誤，請稍後再試");
      }
    });
  } catch (err) {
    console.error("[LIFF init] error:", err);
    alert("❌ LIFF 初始化失敗");
  }
});
