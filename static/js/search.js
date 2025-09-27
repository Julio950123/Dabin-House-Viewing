// ⚠️ 換成你的搜尋專用 LIFF ID
const LIFF_ID = "你的_LIFF_ID";  

// 初始化 LIFF
async function initLiff() {
    try {
        await liff.init({ liffId: LIFF_ID });

        if (!liff.isLoggedIn()) {
            liff.login();
            return;
        }

        // 取得 LINE 使用者 ID
        const profile = await liff.getProfile();
        const userIdInput = document.getElementById("user_id");
        if (userIdInput) {
            userIdInput.value = profile.userId;
        }
        console.log("✅ 取得 user_id:", profile.userId);

    } catch (error) {
        console.error("❌ LIFF 初始化失敗:", error);
        alert("⚠️ LIFF 初始化失敗，請重新開啟連結");
    }
}

// 綁定表單送出事件
function bindFormSubmit() {
    const form = document.getElementById("searchForm");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        // 取表單值
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        try {
            let res = await fetch("/submit_search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const resultDiv = document.getElementById("results");
            resultDiv.innerHTML = "";

            if (res.ok) {
                const data = await res.json();

                if (data.status === "ok" && data.results.length > 0) {
                    data.results.forEach(h => {
                        resultDiv.innerHTML += `
                            <div class="result-card">
                                <h5>${h.title || "未命名物件"}</h5>
                                <p>💰 ${h.budget} 萬 ｜ 🛏 ${h.room} ｜ 🏢 ${h.genre}</p>
                            </div>
                        `;
                    });
                } else {
                    resultDiv.innerHTML = "<p class='text-danger'>沒有符合條件的物件</p>";
                }
            } else {
                alert("搜尋失敗，請稍後再試");
            }
        } catch (err) {
            console.error("❌ 搜尋錯誤:", err);
            alert("搜尋失敗，請稍後再試");
        }
    });
}

// 啟動
document.addEventListener("DOMContentLoaded", () => {
    initLiff();
    bindFormSubmit();
});
