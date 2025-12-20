# 專案文件總覽

本文件列出專案中所有文件及其用途。

## 📁 專案結構

```
chatgpt-conversation-viewer/
├── 📄 核心檔案
│   ├── app.py                      # Flask 主應用程式
│   ├── etl_script.py               # JSON 解析和資料庫建立腳本
│   └── requirements.txt            # Python 依賴套件清單
│
├── 📂 templates/                   # Jinja2 模板目錄
│   ├── base.html                   # 基礎模板（含 Bootstrap 5）
│   ├── index.html                  # 對話列表頁面
│   ├── detail.html                 # 對話詳細頁面
│   ├── stats.html                  # 統計資訊頁面
│   ├── 404.html                    # 404 錯誤頁面
│   └── 500.html                    # 500 錯誤頁面
│
├── 📚 文件檔案
│   ├── README.md                   # 主要說明文件
│   ├── QUICKSTART.md               # 快速開始指南
│   ├── GITHUB_UPLOAD.md            # GitHub 上傳指南
│   ├── DEPLOYMENT.md               # 部署指南
│   ├── CONTRIBUTING.md             # 貢獻指南
│   ├── CHANGELOG.md                # 更新日誌
│   ├── SECURITY.md                 # 安全政策
│   ├── LICENSE                     # MIT 授權條款
│   └── DOCUMENTATION.md            # 本文件
│
├── ⚙️ 配置檔案
│   ├── .gitignore                  # Git 忽略清單
│   └── .github/
│       └── workflows/
│           └── tests.yml           # GitHub Actions 測試工作流程
│
└── 🚫 不應提交的檔案（已在 .gitignore）
    ├── chat_history.db             # SQLite 資料庫（本地生成）
    ├── conversations.json          # ChatGPT 對話資料（用戶提供）
    └── __pycache__/                # Python 快取目錄
```

## 📄 檔案說明

### 核心程式碼

#### `app.py`
Flask Web 應用程式主檔案。

**主要功能**：
- 路由定義（首頁、詳情頁、統計頁）
- 資料庫查詢邏輯
- 搜尋和分頁功能
- Markdown 渲染過濾器
- 錯誤處理（404、500）

**關鍵路由**：
- `/` - 對話列表（支援搜尋和分頁）
- `/chat/<id>` - 對話詳細內容
- `/stats` - 統計資訊

#### `etl_script.py`
ETL（Extract, Transform, Load）腳本。

**主要功能**：
- 使用 ijson 串流解析大型 JSON 檔案
- 建立 SQLite 資料庫結構
- 提取對話和訊息資料
- 生成智慧標籤
- 批次寫入資料庫（每 1000 筆）
- 建立全文搜尋索引

**使用方式**：
```bash
python etl_script.py conversations.json
```

#### `requirements.txt`
Python 依賴套件清單。

**包含的套件**：
- Flask 3.0.0 - Web 框架
- ijson 3.2.3 - JSON 串流解析器
- markdown 3.5.1 - Markdown 渲染器

### 模板檔案

#### `templates/base.html`
基礎模板，所有其他頁面都繼承此模板。

**包含**：
- Bootstrap 5 CSS/JS
- 導航列（搜尋框）
- 頁腳
- 自訂 CSS（主題色、程式碼高亮）
- Highlight.js（程式碼語法高亮）

#### `templates/index.html`
對話列表頁面。

**功能**：
- 顯示對話標題、時間、標籤
- 搜尋結果提示
- 分頁導航（每頁 20 筆）
- 空狀態提示
- 懸停效果

#### `templates/detail.html`
對話詳細頁面。

**功能**：
- 顯示對話標題和元資料
- 使用者和助手訊息區分
- Markdown 內容渲染
- 程式碼高亮
- 返回按鈕
- 捲動到頂部功能

#### `templates/stats.html`
統計資訊頁面。

**顯示內容**：
- 總對話數
- 總訊息數
- 平均訊息數
- 最活躍月份
- 標籤分布

#### `templates/404.html` & `templates/500.html`
錯誤頁面。

### 文件檔案

#### `README.md`
主要說明文件，包含：
- 專案簡介
- 功能特色
- 安裝步驟
- 使用說明
- 故障排除
- 技術細節

#### `QUICKSTART.md`
5 分鐘快速開始指南，適合新用戶。

#### `GITHUB_UPLOAD.md`
詳細的 GitHub 上傳指南，包含：
- Git 初始化
- 儲存庫創建
- 推送步驟
- 常見問題

#### `DEPLOYMENT.md`
部署指南，涵蓋：
- 本地部署
- Docker 部署
- 區域網路部署
- 安全建議
- 效能優化

#### `CONTRIBUTING.md`
貢獻指南，說明：
- 如何貢獻程式碼
- 開發環境設置
- 程式碼風格
- Pull Request 流程

#### `CHANGELOG.md`
更新日誌，記錄：
- 版本歷史
- 新增功能
- 錯誤修復
- 未來計劃

#### `SECURITY.md`
安全政策，包含：
- 漏洞回報流程
- 安全最佳實踐
- 已知限制
- 聯絡資訊

#### `LICENSE`
MIT 授權條款。

### 配置檔案

#### `.gitignore`
Git 忽略清單，排除：
- 資料庫檔案（chat_history.db）
- JSON 資料檔案（conversations.json）
- Python 快取（__pycache__/）
- 虛擬環境（venv/）
- IDE 設定檔
- 環境變數檔（.env）

#### `.github/workflows/tests.yml`
GitHub Actions 自動測試工作流程。

**測試內容**：
- 多平台測試（Windows、macOS、Linux）
- 多 Python 版本測試（3.7-3.11）
- 語法檢查
- 資料庫結構驗證

## 📊 檔案統計

| 類別 | 檔案數 | 說明 |
|------|--------|------|
| 核心程式碼 | 3 | Python 應用程式 |
| HTML 模板 | 6 | Jinja2 模板 |
| 文件 | 9 | Markdown 文件 |
| 配置 | 2 | Git 和 CI/CD 配置 |
| **總計** | **20** | - |

## 🔄 檔案關係圖

```
app.py
  ├─→ templates/base.html
  │     ├─→ templates/index.html
  │     ├─→ templates/detail.html
  │     ├─→ templates/stats.html
  │     ├─→ templates/404.html
  │     └─→ templates/500.html
  │
  └─→ chat_history.db (由 etl_script.py 生成)

etl_script.py
  ├─→ conversations.json (輸入)
  └─→ chat_history.db (輸出)

requirements.txt
  ├─→ Flask
  ├─→ ijson
  └─→ markdown
```

## 📝 文件更新指南

### 當添加新功能時

需要更新：
1. ✅ `CHANGELOG.md` - 記錄新功能
2. ✅ `README.md` - 更新功能清單
3. ✅ `QUICKSTART.md` - 如果影響使用流程
4. ✅ 相關程式碼註釋

### 當修復 Bug 時

需要更新：
1. ✅ `CHANGELOG.md` - 記錄修復
2. ✅ 相關文件（如果 Bug 影響使用方式）

### 當發布新版本時

需要更新：
1. ✅ `CHANGELOG.md` - 版本資訊
2. ✅ `README.md` - 版本號
3. ✅ Git 標籤
4. ✅ GitHub Release

## 🎯 文件完整性檢查清單

- [x] README.md 包含所有基本資訊
- [x] 有快速開始指南
- [x] 有詳細的安裝說明
- [x] 有故障排除章節
- [x] 有貢獻指南
- [x] 有安全政策
- [x] 有授權條款
- [x] 有更新日誌
- [x] 有 .gitignore 檔案
- [x] 有 GitHub Actions 配置

## 💡 提示

1. **定期更新文件**：當程式碼變更時，確保文件同步更新
2. **保持簡潔**：文件應該清晰易懂
3. **添加範例**：盡可能提供程式碼範例和截圖
4. **檢查連結**：確保所有連結都有效
5. **審查拼寫**：使用拼寫檢查工具

---

最後更新：2025-12-20
