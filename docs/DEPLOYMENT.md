# 部署指南

本指南說明如何在不同環境下部署 ChatGPT 對話檢視器。

## ⚠️ 重要提醒

**此應用程式設計用於本地使用**，包含您的私人對話資料。**強烈建議不要**將其部署到公開的網路伺服器上。

## 🖥️ 本地部署（推薦）

### Windows

```powershell
# 安裝依賴
pip install -r requirements.txt

# 處理資料
python etl_script.py conversations.json

# 啟動應用
python app.py
```

### macOS / Linux

```bash
# 安裝依賴
pip3 install -r requirements.txt

# 處理資料
python3 etl_script.py conversations.json

# 啟動應用
python3 app.py
```

## 🐳 Docker 部署（進階）

### 創建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY app.py etl_script.py ./
COPY templates ./templates/

# 設定環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 啟動命令
CMD ["python", "app.py"]
```

### 使用 Docker Compose

創建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  chatgpt-viewer:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./chat_history.db:/app/chat_history.db
      - ./conversations.json:/app/conversations.json
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

執行：

```bash
# 首先處理資料（在主機上）
python etl_script.py conversations.json

# 啟動容器
docker-compose up -d
```

## 🌐 區域網路部署（僅限信任網路）

如果您想在家庭或辦公室網路內分享：

### 修改 app.py

```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### 設定防火牆

**Windows**:
```powershell
# 允許 5000 端口
New-NetFirewallRule -DisplayName "ChatGPT Viewer" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

**Linux**:
```bash
# 使用 ufw
sudo ufw allow 5000/tcp
```

### 訪問應用程式

在同一網路的其他裝置上，使用主機 IP 訪問：
```
http://192.168.1.100:5000
```

## 🔐 安全建議

如果您必須在網路上部署：

### 1. 添加身份驗證

安裝 Flask-HTTPAuth：
```bash
pip install Flask-HTTPAuth
```

在 `app.py` 中添加：
```python
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("your-secure-password")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# 在路由中添加 @auth.login_required
@app.route('/')
@auth.login_required
def index():
    # ...
```

### 2. 使用 HTTPS

使用自簽憑證（僅用於測試）：
```bash
# 生成憑證
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

修改 app.py：
```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, 
            ssl_context=('cert.pem', 'key.pem'))
```

### 3. 使用反向代理

使用 Nginx 作為反向代理：

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 效能優化

### 使用 Gunicorn（生產環境）

```bash
# 安裝 Gunicorn
pip install gunicorn

# 啟動
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 資料庫優化

對於大量對話，考慮定期優化資料庫：
```python
import sqlite3
conn = sqlite3.connect('chat_history.db')
conn.execute('VACUUM')
conn.execute('ANALYZE')
conn.close()
```

## 🔧 環境變數配置

創建 `.env` 檔案：
```
FLASK_APP=app.py
FLASK_ENV=production
DATABASE_PATH=chat_history.db
ITEMS_PER_PAGE=20
SECRET_KEY=your-secret-key-here
```

修改 app.py 載入環境變數：
```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
DATABASE = os.getenv('DATABASE_PATH', 'chat_history.db')
ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
```

## 📝 部署檢查清單

在部署前確認：

- [ ] 已更改預設密鑰和密碼
- [ ] 已設定適當的防火牆規則
- [ ] 資料庫檔案有適當的備份
- [ ] 已測試所有功能正常運作
- [ ] 已設定 HTTPS（如果在網路上部署）
- [ ] 已添加身份驗證（如果在網路上部署）
- [ ] 了解隱私風險並採取適當措施

## ⚡ 故障排除

### 端口被佔用
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### 權限問題
```bash
# Linux/Mac - 給予執行權限
chmod +x app.py etl_script.py
```

---

**再次提醒**：此應用程式包含您的私人對話，請謹慎部署並確保資料安全！
