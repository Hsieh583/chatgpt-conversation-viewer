# 上傳到 GitHub 指南

本指南將協助您將專案上傳到 GitHub。

## 📋 前置準備

1. **GitHub 帳號**：確保您有 GitHub 帳號
2. **Git 安裝**：確認已安裝 Git
   ```bash
   git --version
   ```
3. **清理敏感資料**：確保 `.gitignore` 已正確配置

## 🚀 步驟說明

### 步驟 1: 初始化 Git 儲存庫

在專案根目錄執行：

```bash
# 初始化 Git
git init

# 添加所有檔案（會自動排除 .gitignore 中的檔案）
git add .

# 查看將要提交的檔案
git status
```

**重要檢查**：確認以下檔案**不在**待提交列表中：
- ❌ `conversations.json`
- ❌ `chat_history.db`
- ❌ `__pycache__/`
- ❌ `.env`

### 步驟 2: 提交檔案

```bash
# 建立初始提交
git commit -m "Initial commit: ChatGPT Conversation Viewer v1.0.0"
```

### 步驟 3: 在 GitHub 上創建儲存庫

1. 前往 [GitHub](https://github.com)
2. 點擊右上角的 `+` → `New repository`
3. 填寫資訊：
   - **Repository name**: `chatgpt-conversation-viewer`
   - **Description**: `A local web application to view and search ChatGPT conversation history`
   - **Public/Private**: 選擇 `Public`（如果要分享）或 `Private`
   - **不要**勾選 `Add a README file`（我們已經有了）
   - **不要**勾選 `Add .gitignore`（我們已經有了）
   - **License**: 選擇 `MIT License`（或保持空白，我們已有 LICENSE 檔案）

4. 點擊 `Create repository`

### 步驟 4: 連接遠端儲存庫

GitHub 會顯示指令，但使用以下步驟：

```bash
# 設定遠端儲存庫（替換成您的 GitHub 用戶名）
git remote add origin https://github.com/YOUR-USERNAME/chatgpt-conversation-viewer.git

# 設定主分支名稱
git branch -M main

# 推送到 GitHub
git push -u origin main
```

### 步驟 5: 驗證上傳

1. 重新整理 GitHub 儲存庫頁面
2. 確認所有檔案都已上傳
3. 檢查 README.md 是否正確顯示

## ✅ 上傳檢查清單

上傳前請確認：

- [ ] `.gitignore` 已包含所有敏感檔案
- [ ] `data/` 目錄中的所有檔案都被 `.gitignore` 排除
- [ ] `data/conversations.json` **沒有**被提交
- [ ] `data/chat_history.db` **沒有**被提交
- [ ] ChatGPT 下載的所有檔案（file-*, dalle-generations/ 等）都被排除
- [ ] 專案結構已重組（src/, data/, docs/ 目錄分離）
- [ ] README.md 中的連結和路徑已更新
- [ ] 所有文件都已完成
- [ ] 沒有包含個人敏感資訊

### 🔒 安全性驗證

執行以下命令確認敏感檔案不會被提交：

```bash
# 查看將要提交的檔案
git status

# 確認 data/ 目錄中的檔案沒有出現在列表中
# 應該看到類似這樣的結構：
# - src/
# - docs/
# - .github/
# - README.md, LICENSE, CHANGELOG.md 等
# - 但 data/ 不應該出現

# 如果看到 data/ 或其中的檔案，請檢查 .gitignore
```

## 📝 後續更新

當您對專案進行更改後：

```bash
# 查看更改
git status

# 添加更改的檔案
git add <file-name>
# 或添加所有更改
git add .

# 提交更改
git commit -m "描述您的更改"

# 推送到 GitHub
git push
```

## 🏷️ 創建版本標籤（可選）

為重要版本創建標籤：

```bash
# 創建標籤
git tag -a v1.0.0 -m "Version 1.0.0 - Initial Release"

# 推送標籤到 GitHub
git push origin v1.0.0
```

## 🌟 優化 GitHub 儲存庫

### 添加主題（Topics）

在 GitHub 儲存庫頁面：
1. 點擊右側的 ⚙️ 設定圖示
2. 在 "Topics" 中添加：
   - `chatgpt`
   - `flask`
   - `python`
   - `sqlite`
   - `conversation-viewer`
   - `web-application`

### 設定儲存庫描述

在儲存庫頁面頂部添加：
```
🗨️ A local web app to view, search, and analyze ChatGPT conversation history with memory-efficient JSON streaming
```

### 設定儲存庫網站（可選）

如果您部署了 Demo 版本，可以添加網站連結。

### 啟用 Discussions（可選）

1. 前往儲存庫 `Settings`
2. 勾選 `Discussions`
3. 這樣用戶可以討論功能和使用心得

### 添加問題模板

GitHub 會自動偵測 `.github/ISSUE_TEMPLATE/` 目錄，您可以：
1. 前往 `Settings` → `Features` → `Issues` → `Set up templates`
2. 選擇 Bug report 和 Feature request 模板

## 🔄 同步 Fork（如果其他人 Fork 了您的專案）

如果您想要從主要儲存庫同步更新：

```bash
# 添加上游儲存庫
git remote add upstream https://github.com/original-owner/chatgpt-conversation-viewer.git

# 獲取上游更改
git fetch upstream

# 合併更改
git merge upstream/main

# 推送到您的 Fork
git push origin main
```

## 📊 GitHub Insights

上傳後，您可以在 GitHub 查看：
- **Insights** → **Traffic**: 查看訪問統計
- **Insights** → **Contributors**: 查看貢獻者
- **Insights** → **Community**: 查看專案健康度分數

## 🎯 常見問題

### Q: 不小心提交了敏感資料怎麼辦？

```bash
# 從 Git 歷史中移除檔案
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch conversations.json" \
  --prune-empty --tag-name-filter cat -- --all

# 強制推送（⚠️ 危險操作）
git push origin --force --all
```

**更好的方式**：刪除儲存庫並重新建立，如果是新專案的話。

### Q: 如何更新 README 中的連結？

使用文字編輯器全域搜尋並替換：
- `your-username` → 您的 GitHub 用戶名
- `your-email@example.com` → 您的 Email（如果要公開）

### Q: 可以使用 GitHub Desktop 嗎？

可以！GitHub Desktop 提供圖形化介面：
1. 下載 [GitHub Desktop](https://desktop.github.com/)
2. 使用 `File` → `Add Local Repository`
3. 選擇專案目錄
4. 使用介面進行提交和推送

## 🎉 完成！

您的專案現在已經在 GitHub 上了！

接下來：
- 分享您的儲存庫連結
- 添加截圖到 README
- 回應 Issues 和 Pull Requests
- 持續改進專案

---

**提醒**：請定期檢查沒有意外提交敏感資料！
