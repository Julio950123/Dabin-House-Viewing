document.getElementById("searchForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    user_id: document.getElementById("user_id").value,
    budget: document.getElementById("budget").value,
    room: document.getElementById("room").value,
    genre: document.getElementById("genre").value
  };

  try {
    const res = await fetch("/submit_search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await res.json();
    if (result.status === "success") {
      await liff.sendMessages([
        { type: "text", text: "🔍 搜尋完成，請查看結果！" }
      ]);
      liff.closeWindow();
    } else {
      alert("送出失敗：" + result.message);
    }
  } catch (err) {
    alert("發生錯誤：" + err);
  }
});
