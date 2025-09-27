const LIFF_ID = "2007720984-Wdoapz3B";  

async function initLiff() {
    try {
        await liff.init({ liffId: LIFF_ID });

        if (!liff.isLoggedIn()) {
            liff.login();
            return;
        }

        const profile = await liff.getProfile();
        document.getElementById("user_id").value = profile.userId;
        console.log("✅ 抓到 user_id:", profile.userId);

    } catch (error) {
        console.error("❌ LIFF 初始化失敗:", error);
        alert("⚠️ LIFF 初始化失敗，請重新開啟連結");
    }
}

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

            const text = await res.text();   // ⚠️ 先讀純文字
            console.log("🔍 原始回傳:", text);

            let data = {};
            try {
                data = JSON.parse(text);
            } catch {
                data = { message: text };
            }

            if (res.ok && data.status === "ok") {
                alert("✅ 成功：" + JSON.stringify(data));
                liff.closeWindow();
            } else {
                alert("❌ 錯誤：" + (data.message || "未知錯誤") + "\n原始回傳: " + text);
            }
        } catch (err) {
            console.error("⚠️ 網路錯誤:", err);
            alert("⚠️ 網路錯誤：" + err.message);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initLiff();
    bindFormSubmit();
});