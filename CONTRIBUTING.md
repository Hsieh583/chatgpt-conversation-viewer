# 貢獻指南

感謝您對 ChatGPT 對話檢視器專案的關注！

## 如何貢獻

1. Fork 這個專案
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 開發環境設置

```bash
# 克隆專案
git clone https://github.com/your-username/chatgpt-conversation-viewer.git
cd chatgpt-conversation-viewer

# 安裝依賴
pip install -r requirements.txt

# 準備測試資料（您需要自己的 conversations.json）
python etl_script.py conversations.json

# 執行應用程式
python app.py
```

## 程式碼風格

- 遵循 PEP 8 Python 程式碼風格指南
- 使用有意義的變數和函數名稱
- 添加適當的註釋和文件字串
- 保持函數簡潔，單一職責

## 報告問題

如果您發現任何問題，請：

1. 檢查是否已經有相同的 Issue
2. 提供詳細的問題描述
3. 包含重現步驟
4. 提供系統資訊（OS、Python 版本等）

## 功能建議

歡迎提出新功能建議！請在 Issue 中詳細描述：

- 功能描述
- 使用場景
- 預期效果
- 可能的實現方式

## 測試

在提交 PR 之前，請確保：

- [ ] 程式碼可以正常運行
- [ ] 沒有引入新的錯誤
- [ ] 新功能有適當的錯誤處理
- [ ] 更新了相關文件

## 行為準則

- 尊重所有貢獻者
- 接受建設性的批評
- 專注於對專案最有利的事情
- 展現同理心

謝謝您的貢獻！🎉
