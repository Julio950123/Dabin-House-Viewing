// ⚠️ 換成你的 LIFF ID
const LIFF_ID = "2007720984-Wdoapz3B";  

// 初始化 LIFF
async function initLiff() {
    try {
        await liff.init({ liffId: LIFF_ID });

        if (!liff.isLoggedIn()) {
            liff.login();
            return;
        }

        // 取得使用者 profile
        const profile = await liff.getProfile();
        document.getElementById("user_id").value = profile.userId;
        console.log("✅ 抓到 user_id:", profile.userId);

    } catch (error) {
        console.error("❌ LIFF 初始化失敗:", error);
        alert("⚠️ LIFF 初始化失敗，請重新開啟連結");
    }
}

// 綁定表單送出
function bindFormSubmit() {
    const form = document.getElementById("searchForm");
    if (!form) return;

    form.addEventListener("submit", async function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const payload = Object.fromEntries(formData.entries());

        try {
            const res = await fetch("/submit_search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json().catch(() => ({}));

            if (res.ok && data.status === "ok") {
                console.log("✅ 搜尋成功:", data);
                liff.closeWindow();  // 成功就關閉 LIFF 視窗
            } else {
                console.error("❌ 搜尋失敗:", data);
                alert("❌ " + (data.message || "送出失敗，請稍後再試"));
            }
        } catch (err) {
            console.error("⚠️ 網路錯誤:", err);
            alert("⚠️ 網路錯誤：" + err.message);
        }
    });
}

// 啟動
document.addEventListener("DOMContentLoaded", () => {
    initLiff();
    bindFormSubmit();
});
