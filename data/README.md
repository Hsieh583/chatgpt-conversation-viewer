# 資料目錄

此目錄用於存放您從 ChatGPT 下載的所有個人資料。

## 📁 預期檔案

- `conversations.json` - 您的 ChatGPT 對話記錄（從 ChatGPT 匯出）
- `chat_history.db` - 由 ETL 腳本生成的 SQLite 資料庫
- `file-*` - ChatGPT 下載的圖片、檔案等
- `dalle-generations/` - DALL-E 生成的圖片
- 其他從 ChatGPT 匯出的資料

## 🔒 隱私保護

⚠️ **重要提醒**：此目錄中的所有檔案都包含您的個人對話資料，已被 `.gitignore` 排除，**不會**被上傳到 GitHub。

請確保：
1. 不要修改根目錄的 `.gitignore` 檔案中關於 `data/` 的設定
2. 不要強制提交此目錄中的檔案（使用 `git add -f`）
3. 不要與他人分享此目錄中的內容

## 📥 如何準備資料

1. 從 ChatGPT 網站匯出您的資料
2. 解壓縮下載的檔案
3. 將所有檔案複製到這個 `data/` 目錄
4. 執行 `python src/etl_script.py` 來處理資料

## 📊 資料庫說明

`chat_history.db` 是由 ETL 腳本自動生成的 SQLite 資料庫，包含：
- `conversations` 表：對話元資料
- `messages` 表：對話訊息內容
- `messages_fts` 表：全文搜尋索引

您可以使用任何 SQLite 瀏覽器查看資料庫內容，例如：
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- VS Code 的 SQLite 擴充套件
