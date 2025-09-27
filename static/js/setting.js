document.getElementById("settingForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    user_id: document.getElementById("user_id").value,
    budget: document.getElementById("budget").value,
    room: document.getElementById("room").value,
    genre: document.getElementById("genre").value
  };

  try {
    const res = await fetch("/submit_form", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await res.json();
    if (result.status === "success") {
      await liff.sendMessages([
        { type: "text", text: "✅ 追蹤條件已更新！" }
      ]);
      liff.closeWindow();
    } else {
      alert("送出失敗：" + result.message);
    }
  } catch (err) {
    alert("發生錯誤：" + err);
  }
});
