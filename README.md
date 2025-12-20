# ChatGPT 對話檢視器

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask Version](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)

一個本地的 ChatGPT 對話歷史記錄查看器，使用 Python Flask 和 SQLite 建構。專門設計用於處理大型 JSON 檔案（約 250MB），在低記憶體環境下運行。

## 📸 預覽

![對話列表](https://via.placeholder.com/800x400.png?text=Conversation+List+Preview)
*對話列表頁面 - 顯示所有對話，支援搜尋和分頁*

![對話詳情](https://via.placeholder.com/800x400.png?text=Conversation+Detail+Preview)
*對話詳情頁面 - 完整的對話內容，支援 Markdown 渲染*

## 特色功能

✨ **串流 JSON 解析** - 使用 ijson 進行串流解析，避免記憶體溢出  
🔍 **全文搜尋** - 在標題和訊息內容中搜尋關鍵字  
📄 **分頁顯示** - 每頁顯示 20 筆對話，支援分頁導航  
🏷️ **智慧標籤** - 根據對話內容自動產生標籤  
💬 **Markdown 支援** - 正確渲染程式碼區塊和格式化文字  
📊 **統計資訊** - 查看對話總數、訊息數量等統計資料  
🎨 **Bootstrap 5 介面** - 現代化、響應式的使用者介面

## 🚀 快速開始

```bash
# 1. 克隆專案（或下載 ZIP）
git clone https://github.com/YOUR-USERNAME/chatgpt-conversation-viewer.git
cd chatgpt-conversation-viewer

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 準備資料：將 ChatGPT 匯出的檔案放到 data/ 目錄
mkdir data
# 將 conversations.json 複製到 data/ 目錄

# 4. 執行 ETL 腳本
cd src
python etl_script.py

# 5. 啟動應用程式
python app.py

# 6. 在瀏覽器開啟 http://127.0.0.1:5000
```

詳細安裝步驟請參考下方說明。

## 系統需求

- Python 3.7+
- 約 2GB 可用記憶體
- 瀏覽器（Chrome, Firefox, Edge, Safari）

## 📖 詳細安裝步驟

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

或手動安裝：

```bash
pip install Flask==3.0.0
pip install ijson==3.2.3
pip install markdown==3.5.1
```

### 2. 準備 JSON 檔案

將您從 ChatGPT 下載的所有檔案放到 `data/` 目錄中：

```bash
mkdir data
# 將 conversations.json 和其他檔案移動到 data/ 目錄
```

### 3. 執行 ETL 腳本

使用 ETL 腳本解析 JSON 並建立資料庫：

```bash
python src/etl_script.py data/conversations.json
```

或使用預設路徑：

```bash
cd src
python etl_script.py
```

**重要提示**：此步驟可能需要數分鐘，取決於 JSON 檔案大小。腳本會顯示處理進度。

### 4. 啟動 Flask 應用程式

```bash
cd src
python app.py
```

### 5. 開啟瀏覽器

在瀏覽器中訪問：`http://127.0.0.1:5000`

## 📂 專案結構

```
chatgpt-conversation-viewer/
├── src/                    # 應用程式碼
│   ├── app.py              # Flask 主應用程式
│   ├── etl_script.py       # JSON 解析和資料庫建立腳本
│   └── templates/          # HTML 模板檔案
│       ├── base.html       # 基礎模板
│       ├── index.html      # 對話列表頁面
│       ├── detail.html     # 對話詳細頁面
│       ├── stats.html      # 統計資訊頁面
│       ├── 404.html        # 404 錯誤頁面
│       └── 500.html        # 500 錯誤頁面
├── data/                   # 用戶資料（被 .gitignore 排除）
│   ├── conversations.json  # ChatGPT 對話記錄
│   ├── chat_history.db     # SQLite 資料庫（執行後生成）
│   └── ...                 # 其他 ChatGPT 下載檔案
├── docs/                   # 文件
│   ├── CONTRIBUTING.md     # 貢獻指南
│   ├── DEPLOYMENT.md       # 部署說明
│   ├── QUICKSTART.md       # 快速開始
│   ├── SECURITY.md         # 安全政策
│   └── DOCUMENTATION.md    # 完整文件
├── .github/                # GitHub Actions 工作流程
│   └── workflows/
│       └── tests.yml       # CI/CD 測試
├── .gitignore              # Git 忽略檔案
├── README.md               # 專案介紹（本檔案）
├── LICENSE                 # MIT 授權
├── CHANGELOG.md            # 版本紀錄
├── GITHUB_UPLOAD.md        # GitHub 上傳指南
└── requirements.txt        # Python 依賴套件
```

## 資料庫結構

### conversations 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | TEXT | 對話 ID（主鍵）|
| title | TEXT | 對話標題 |
| create_time | DATETIME | 建立時間 |
| tags | TEXT | 標籤（逗號分隔）|
| total_char_count | INTEGER | 總字元數 |

### messages 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | TEXT | 訊息 ID（主鍵）|
| conversation_id | TEXT | 所屬對話 ID（外鍵）|
| role | TEXT | 角色（user/assistant）|
| content | TEXT | 訊息內容 |
| create_time | DATETIME | 建立時間 |

## 使用說明

### 搜尋對話

1. 在導航列的搜尋框中輸入關鍵字
2. 點擊搜尋按鈕
3. 系統會在對話標題和訊息內容中搜尋

### 查看對話詳情

1. 在對話列表中點擊任一對話
2. 查看完整的對話內容
3. 訊息會以對話框形式顯示，區分使用者和助手

### 查看統計資訊

點擊導航列的「統計」按鈕，查看：
- 總對話數
- 總訊息數
- 平均訊息數/對話
- 最活躍月份
- 標籤分布

## 技術細節

### 記憶體優化

- **串流解析**：使用 `ijson.items()` 逐項解析 JSON，不將整個檔案載入記憶體
- **批次提交**：每 1000 筆記錄提交一次到資料庫，平衡 I/O 和記憶體使用
- **索引優化**：在常用查詢欄位上建立索引，提升查詢效能

### 自動標籤規則

etl_script.py 會根據對話標題自動添加標籤：

- 包含 "python", "code", "programming" → `Coding`
- 包含 "data", "database", "sql" → `Data`
- 包含 "web", "html", "flask" → `Web Development`
- 包含 "ai", "ml", "machine learning" → `AI/ML`

您可以在 `etl_script.py` 的 `generate_tags()` 函數中自訂標籤規則。

## 故障排除

### 問題：執行 ETL 腳本時出現 MemoryError

**解決方案**：
- 確認已使用 ijson（而非 json.load()）
- 減小 batch_size 參數（預設為 1000）
- 關閉其他佔用記憶體的程式

### 問題：找不到資料庫檔案

**解決方案**：
- 確保已執行 `python etl_script.py`
- 檢查當前目錄是否有 `chat_history.db`

### 問題：搜尋速度慢

**解決方案**：
- 資料庫已包含索引，首次搜尋可能較慢
- 考慮在 messages 表上建立全文索引（FTS）

### 問題：程式碼區塊顯示不正確

**解決方案**：
- 確保已安裝 markdown 套件
- 檢查瀏覽器是否載入了 highlight.js

## 自訂與擴充

### 修改每頁顯示數量

在 `app.py` 中修改：

```python
ITEMS_PER_PAGE = 20  # 改為您想要的數字
```

### 添加更多標籤規則

在 `etl_script.py` 的 `generate_tags()` 函數中添加：

```python
if 'your_keyword' in title_lower:
    tags.append('Your Tag')
```

### 自訂樣式

修改 `templates/base.html` 中的 CSS 變數：

```css
:root {
    --primary-color: #10a37f;    /* 主要顏色 */
    --secondary-color: #19c37d;   /* 次要顏色 */
}
```

## 效能考量

- **資料庫大小**：預期約為 JSON 檔案大小的 60-80%
- **載入時間**：首次 ETL 處理 250MB JSON 約需 5-10 分鐘
- **查詢效能**：有索引的情況下，查詢通常在 100ms 內完成

## 🤝 貢獻

歡迎貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何參與專案。

### 貢獻者

感謝所有為這個專案做出貢獻的人！

<!-- 這裡會自動顯示貢獻者頭像 -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

## 📝 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件。

## 🔒 隱私聲明

- **本地運行**：所有資料僅存儲在您的本地電腦，不會上傳到任何伺服器
- **資料安全**：請勿將包含對話內容的 `conversations.json` 和 `chat_history.db` 上傳到公開的版本控制系統
- **建議**：在 GitHub 上使用時，`.gitignore` 已配置為排除這些敏感檔案

## ⭐ Star 歷史

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/chatgpt-conversation-viewer&type=Date)](https://star-history.com/#your-username/chatgpt-conversation-viewer&Date)

## 📮 聯絡方式

如有問題或建議，歡迎：
- 開啟 [Issue](https://github.com/your-username/chatgpt-conversation-viewer/issues)
- 提交 [Pull Request](https://github.com/your-username/chatgpt-conversation-viewer/pulls)

## 🙏 致謝

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [ijson](https://github.com/ICRAR/ijson) - JSON 串流解析
- [Bootstrap](https://getbootstrap.com/) - UI 框架
- [Highlight.js](https://highlightjs.org/) - 程式碼語法高亮

---

**⚠️ 重要提醒**：
- 此工具設計用於本地使用，請勿在生產環境或公開網路上部署
- 您的對話資料包含個人隱私資訊，請妥善保管
- 定期備份您的 `chat_history.db` 資料庫檔案

如果這個專案對您有幫助，請給個 ⭐ Star 支持一下！
